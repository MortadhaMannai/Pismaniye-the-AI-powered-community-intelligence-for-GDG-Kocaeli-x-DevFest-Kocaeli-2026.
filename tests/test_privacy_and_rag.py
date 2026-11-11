"""Unit tests for PISMANIYE privacy guardrails, PII redaction, RAG knowledge engine, and repository."""

from __future__ import annotations

from pismaniye.data.repository import PismaniyeRepository, reset_repository
from pismaniye.privacy.guardrails import PrivacyGuard
from pismaniye.schemas.domain import KnowledgeDocument, VerificationStatus


def test_opt_in_filtering_excludes_private_attendees() -> None:
    repo = reset_repository()
    discoverable = repo.list_discoverable_people()
    ids = {p.id for p in discoverable}
    assert "att-private-opted-out-sample" not in ids
    assert "spk-selin-kaya-sample" in ids
    assert "att-deniz-aksoy-sample" in ids


def test_public_serialization_never_exposes_email_or_phone() -> None:
    repo = reset_repository()
    for person in repo.people.values():
        sanitized = PrivacyGuard.sanitize_profile(person)
        assert "private_email" not in sanitized
        assert "private_phone" not in sanitized
        serialized_str = str(sanitized)
        assert "example.invalid" not in serialized_str
        assert "+90-555" not in serialized_str


def test_pii_regex_redaction() -> None:
    raw = "Reach me at secret.user@domain.org or call +90 555 123 4567 right away."
    cleaned = PrivacyGuard.redact_pii_text(raw)
    assert "secret.user@domain.org" not in cleaned
    assert "555 123 4567" not in cleaned
    assert "[REDACTED-EMAIL-CONSENT-REQUIRED]" in cleaned
    assert "[REDACTED-PHONE-CONSENT-REQUIRED]" in cleaned


def test_hybrid_rag_ingestion_chunking_and_update() -> None:
    repo = PismaniyeRepository()
    initial_doc_count = len(repo.rag.documents)
    assert initial_doc_count >= 15

    custom_doc = KnowledgeDocument(
        id="doc-custom-test",
        title="Custom Organizer Guide to LangGraph Checkpoints",
        doc_type="learning",
        content=(
            "LangGraph StateGraph checkpoints allow GDG Kocaeli developers to inspect multi-agent "
            "execution state and resume workflows deterministically on Cloud Run."
        ),
        source_uri="pismaniye://test/langgraph-checkpoints",
        tags=["LangGraph", "Cloud Run", "Checkpoints"],
        verification_status=VerificationStatus.VERIFIED_ORGANIZER_DATA,
    )
    chunks_added = repo.rag.ingest_document(custom_doc)
    assert chunks_added >= 1

    citations = repo.rag.search("LangGraph checkpoints Cloud Run", top_k=3)
    assert len(citations) >= 1
    assert any("doc-custom-test" in c.source_id for c in citations)

    updated = repo.rag.update_document(
        "doc-custom-test",
        content="Updated content discussing Vertex AI text-embedding-004 vector search.",
        tags=["Vertex AI", "text-embedding-004"],
    )
    assert updated is not None
    assert repo.rag.delete_document("doc-custom-test") is True


def test_right_to_erasure_deletes_profile_and_rag_chunks() -> None:
    repo = PismaniyeRepository()
    target_id = "att-deniz-aksoy-sample"
    assert target_id in repo.people
    assert repo.delete_person_data(target_id) is True
    assert target_id not in repo.people
    assert f"doc-{target_id}" not in repo.rag.documents
