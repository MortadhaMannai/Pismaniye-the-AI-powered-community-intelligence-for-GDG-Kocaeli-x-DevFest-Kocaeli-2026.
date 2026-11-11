"""Organizer-Managed Knowledge Base with chunking, metadata, embeddings, and hybrid retrieval."""

from __future__ import annotations

import math
import re
from typing import Any

from pismaniye.adapters.google_cloud import CloudStorageDocumentAdapter, ModelAndEmbeddingAdapter
from pismaniye.schemas.agent import EvidenceCitation
from pismaniye.schemas.domain import KnowledgeChunk, KnowledgeDocument, utc_now_iso


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a)) or 1.0
    norm_b = math.sqrt(sum(b * b for b in vec_b)) or 1.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


class HybridRAGEngine:
    """Ingests, chunks, embeds, updates, and retrieves organizer-managed community knowledge."""

    def __init__(
        self,
        model_adapter: ModelAndEmbeddingAdapter | None = None,
        storage_adapter: CloudStorageDocumentAdapter | None = None,
        chunk_size_chars: int = 420,
        chunk_overlap_chars: int = 80,
    ) -> None:
        self.model_adapter = model_adapter or ModelAndEmbeddingAdapter()
        self.storage_adapter = storage_adapter or CloudStorageDocumentAdapter()
        self.chunk_size_chars = chunk_size_chars
        self.chunk_overlap_chars = chunk_overlap_chars
        self.documents: dict[str, KnowledgeDocument] = {}
        self.chunks: list[KnowledgeChunk] = []

    def chunk_document(self, doc: KnowledgeDocument) -> list[KnowledgeChunk]:
        """Split a KnowledgeDocument into overlapping semantic chunks with embeddings and metadata."""
        text = doc.content.strip()
        if not text:
            return []

        raw_segments: list[str] = []
        if len(text) <= self.chunk_size_chars:
            raw_segments = [text]
        else:
            start = 0
            step = max(100, self.chunk_size_chars - self.chunk_overlap_chars)
            while start < len(text):
                segment = text[start : start + self.chunk_size_chars].strip()
                if segment:
                    raw_segments.append(segment)
                start += step

        doc_chunks: list[KnowledgeChunk] = []
        for idx, seg in enumerate(raw_segments):
            embed_input = f"{doc.title} | Tags: {', '.join(doc.tags)} | {seg}"
            vector = self.model_adapter.embed_text(embed_input)
            doc_chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{doc.id}#c{idx}",
                    doc_id=doc.id,
                    event_id=doc.event_id,
                    doc_title=doc.title,
                    doc_type=doc.doc_type,
                    text=seg,
                    chunk_index=idx,
                    tags=list(doc.tags),
                    source_uri=doc.source_uri,
                    verification_status=doc.verification_status,
                    embedding=vector,
                )
            )
        return doc_chunks

    def ingest_document(self, doc: KnowledgeDocument, persist_blob: bool = False) -> int:
        """Ingest or update a single KnowledgeDocument and re-index its chunks."""
        self.documents[doc.id] = doc
        if persist_blob:
            self.storage_adapter.store_document_blob(doc.id, doc.content)
        self.chunks = [c for c in self.chunks if c.doc_id != doc.id]
        new_chunks = self.chunk_document(doc)
        self.chunks.extend(new_chunks)
        return len(new_chunks)

    def ingest_documents(self, docs: list[KnowledgeDocument]) -> int:
        """Batch ingest documents and return total chunk count."""
        total = 0
        for doc in docs:
            total += self.ingest_document(doc, persist_blob=False)
        return total

    def update_document(
        self,
        doc_id: str,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> KnowledgeDocument | None:
        """Update an existing knowledge document and re-compute its chunks and embeddings."""
        existing = self.documents.get(doc_id)
        if not existing:
            return None
        if title is not None:
            existing.title = title
        if content is not None:
            existing.content = content
        if tags is not None:
            existing.tags = tags
        existing.updated_at = utc_now_iso()
        self.ingest_document(existing, persist_blob=True)
        return existing

    def delete_document(self, doc_id: str) -> bool:
        """Remove a document and all of its indexed chunks."""
        if doc_id not in self.documents:
            return False
        del self.documents[doc_id]
        self.chunks = [c for c in self.chunks if c.doc_id != doc_id]
        return True

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_types: list[str] | None = None,
    ) -> list[EvidenceCitation]:
        """Execute hybrid dense vector + lexical/tag retrieval and return grounded EvidenceCitations."""
        if not self.chunks:
            return []

        query_vec = self.model_adapter.embed_text(query)
        query_tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        stop_words = {"the", "and", "for", "with", "who", "what", "how", "want", "after", "have", "can", "you"}
        meaningful_tokens = {t for t in query_tokens if len(t) > 2 and t not in stop_words} or query_tokens

        scored: list[tuple[float, KnowledgeChunk]] = []
        for chunk in self.chunks:
            if doc_types and chunk.doc_type not in doc_types:
                continue

            dense_sim = _cosine_similarity(query_vec, chunk.embedding)
            haystack = f"{chunk.doc_title} {' '.join(chunk.tags)} {chunk.text}".lower()
            haystack_tokens = set(re.findall(r"[a-z0-9]+", haystack))

            # Lexical & tag overlap boost
            matched_tokens = meaningful_tokens.intersection(haystack_tokens)
            lexical_score = len(matched_tokens) / max(1, len(meaningful_tokens))

            tag_bonus = 0.0
            for tag in chunk.tags:
                tag_low = tag.lower()
                if tag_low in query.lower() or any(t == tag_low for t in meaningful_tokens):
                    tag_bonus += 0.18

            hybrid_score = min(0.99, round(0.45 * dense_sim + 0.40 * lexical_score + min(0.30, tag_bonus), 3))
            if hybrid_score > 0.08:
                scored.append((hybrid_score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)

        citations: list[EvidenceCitation] = []
        seen_docs: set[str] = set()
        for score, chunk in scored:
            if chunk.doc_id in seen_docs and len(citations) >= 2:
                continue
            seen_docs.add(chunk.doc_id)
            citations.append(
                EvidenceCitation(
                    source_id=chunk.chunk_id,
                    source_title=chunk.doc_title,
                    source_type=chunk.doc_type,
                    source_uri=chunk.source_uri,
                    snippet=chunk.text[:280] + ("..." if len(chunk.text) > 280 else ""),
                    relevance_score=score,
                    verification_status=chunk.verification_status,
                )
            )
            if len(citations) >= top_k:
                break

        return citations

    def stats(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        for doc in self.documents.values():
            by_type[doc.doc_type] = by_type.get(doc.doc_type, 0) + 1
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "documents_by_type": by_type,
            "embedding_backend": self.model_adapter.backend_name,
            "storage_backend": self.storage_adapter.backend_name,
        }
