"""Central data repository for PISMANIYE with local JSON persistence and Firestore adapter support."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from pismaniye.adapters.google_cloud import (
    CloudStorageDocumentAdapter,
    FirestoreStateAdapter,
    ModelAndEmbeddingAdapter,
)
from pismaniye.config import PismaniyeSettings, get_settings
from pismaniye.data.seed_devfest_kocaeli_2026 import (
    get_seed_community_resources,
    get_seed_edition_config,
    get_seed_knowledge_documents,
    get_seed_kocaeli_places,
    get_seed_people,
    get_seed_sessions,
    get_seed_venue,
)
from pismaniye.knowledge.rag_engine import HybridRAGEngine
from pismaniye.privacy.guardrails import PrivacyGuard
from pismaniye.schemas.agent import DecisionExplanation, TraceRecord
from pismaniye.schemas.domain import (
    AuditLogEntry,
    CommunityResource,
    EventEditionConfig,
    EventSession,
    IntroductionConsentStatus,
    IntroductionRequest,
    KnowledgeDocument,
    KocaeliPlace,
    ModerationSubmission,
    PersonProfile,
    VenueInfo,
    VerificationStatus,
    utc_now_iso,
)


class PismaniyeRepository:
    """Unified repository managing event data, knowledge base, traces, decisions, and audit trails."""

    def __init__(self, settings: PismaniyeSettings | None = None) -> None:
        self.settings = settings or get_settings()
        self.state_dir: Path = self.settings.ensure_dirs()
        self.model_adapter = ModelAndEmbeddingAdapter(self.settings)
        self.firestore_adapter = FirestoreStateAdapter(self.settings)
        self.gcs_adapter = CloudStorageDocumentAdapter(self.settings)
        self.rag = HybridRAGEngine(
            model_adapter=self.model_adapter,
            storage_adapter=self.gcs_adapter,
        )

        # In-memory collections hydrated from seed or persisted state
        self.edition_config: EventEditionConfig = get_seed_edition_config(self.settings.event_id)
        self.venue: VenueInfo = get_seed_venue(self.settings.event_id)
        self.people: dict[str, PersonProfile] = {}
        self.sessions: dict[str, EventSession] = {}
        self.kocaeli_places: dict[str, KocaeliPlace] = {}
        self.community_resources: dict[str, CommunityResource] = {}
        self.introductions: dict[str, IntroductionRequest] = {}
        self.moderation_queue: dict[str, ModerationSubmission] = {}
        self.audit_logs: list[AuditLogEntry] = []
        self.traces: dict[str, TraceRecord] = {}
        self.decisions: dict[str, DecisionExplanation] = {}

        self._initialize_seed_data()
        self._load_persisted_traces_and_decisions()

    def _initialize_seed_data(self) -> None:
        for person in get_seed_people():
            self.people[person.id] = person
        for sess in get_seed_sessions(self.settings.event_id):
            self.sessions[sess.id] = sess
        for place in get_seed_kocaeli_places():
            self.kocaeli_places[place.id] = place
        for res in get_seed_community_resources():
            self.community_resources[res.id] = res

        seed_docs = get_seed_knowledge_documents(self.settings.event_id)
        self.rag.ingest_documents(seed_docs)

        # Seed one pending community submission for organizer moderation demo
        sub = ModerationSubmission(
            submission_id="mod-sub-001",
            submitter_name="Merve Arslan (Community Member — Sample)",
            submission_type="community_resource",
            title="Kocaeli University Agentic AI Study Group Notes",
            content="Open-source colab notebooks from our student study group on LangGraph & Gemini.",
            tags=["Agentic AI", "LangGraph", "Student Community"],
            status="PENDING",
        )
        self.moderation_queue[sub.submission_id] = sub

        self.record_audit(
            actor_role="SYSTEM",
            action="SEED_INITIALIZED",
            resource_type="event_edition",
            resource_id=self.settings.event_id,
            summary=f"Initialized labeled sample dataset & indexed {len(self.rag.chunks)} RAG chunks.",
        )

    def _load_persisted_traces_and_decisions(self) -> None:
        traces_dir = self.state_dir / "traces"
        for p in sorted(traces_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                tr = TraceRecord.model_validate(data)
                self.traces[tr.trace_id] = tr
                if tr.explanation:
                    self.decisions[tr.explanation.decision_id] = tr.explanation
            except Exception:
                continue

        decisions_dir = self.state_dir / "decisions"
        for p in sorted(decisions_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                dec = DecisionExplanation.model_validate(data)
                self.decisions[dec.decision_id] = dec
            except Exception:
                continue

    def save_trace_and_decision(self, trace: TraceRecord) -> None:
        """Persist trace and its XAI decision explanation to disk for CLI/Web inspection."""
        self.traces[trace.trace_id] = trace
        trace_path = self.state_dir / "traces" / f"{trace.trace_id}.json"
        trace_path.write_text(trace.model_dump_json(indent=2), encoding="utf-8")

        if trace.explanation:
            dec = trace.explanation
            self.decisions[dec.decision_id] = dec
            dec_path = self.state_dir / "decisions" / f"{dec.decision_id}.json"
            dec_path.write_text(dec.model_dump_json(indent=2), encoding="utf-8")

    def get_trace(self, trace_id: str) -> TraceRecord | None:
        if trace_id == "latest" and self.traces:
            return list(self.traces.values())[-1]
        if trace_id in self.traces:
            return self.traces[trace_id]
        # Prefix match support for convenience
        for tid, tr in self.traces.items():
            if tid.startswith(trace_id):
                return tr
        return None

    def get_decision(self, decision_id: str) -> DecisionExplanation | None:
        if decision_id == "latest" and self.decisions:
            return list(self.decisions.values())[-1]
        if decision_id in self.decisions:
            return self.decisions[decision_id]
        for did, dec in self.decisions.items():
            if did.startswith(decision_id):
                return dec
        return None

    def record_audit(
        self,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            audit_id=f"aud-{uuid.uuid4().hex[:8]}",
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            summary=PrivacyGuard.redact_pii_text(summary),
            metadata=metadata or {},
        )
        self.audit_logs.append(entry)
        return entry

    # --- People & Privacy Operations ---

    def list_discoverable_people(self, for_matchmaking: bool = False) -> list[PersonProfile]:
        all_people = list(self.people.values())
        return PrivacyGuard.filter_discoverable_people(all_people, for_matchmaking=for_matchmaking)

    def upsert_person(self, profile: PersonProfile, actor_role: str = "ORGANIZER") -> PersonProfile:
        self.people[profile.id] = profile
        if profile.opt_in_networking and profile.visibility.value != "PRIVATE":
            doc = KnowledgeDocument(
                id=f"doc-{profile.id}",
                event_id=self.edition_config.event_id,
                title=f"{profile.full_name} — {profile.headline}",
                doc_type="gde_profile" if profile.role.value == "GDE" else "speaker_bio",
                content=(
                    f"Name: {profile.full_name}\nRole: {profile.role.value} | Org: {profile.organization}\n"
                    f"Bio: {profile.bio}\nExpertise: {', '.join(profile.expertise_tags + profile.technologies)}\n"
                    f"Interests: {', '.join(profile.interests)}"
                ),
                source_uri=f"pismaniye://directory/{profile.id}",
                tags=list(set(profile.interests + profile.expertise_tags + profile.technologies)),
                verification_status=profile.verification_status,
            )
            self.rag.ingest_document(doc, persist_blob=True)
        else:
            self.rag.delete_document(f"doc-{profile.id}")

        self.record_audit(
            actor_role=actor_role,
            action="UPSERT_PERSON_PROFILE",
            resource_type="person_profile",
            resource_id=profile.id,
            summary=f"Updated profile {profile.full_name} (opt_in={profile.opt_in_networking}, status={profile.verification_status.value}).",
        )
        return profile

    def delete_person_data(self, person_id: str, actor_role: str = "ATTENDEE_OR_ORGANIZER") -> bool:
        """Right-to-erasure: Delete profile, RAG chunks, and pending introductions."""
        if person_id not in self.people:
            return False
        removed = self.people.pop(person_id)
        self.rag.delete_document(f"doc-{person_id}")
        to_delete_intros = [
            iid for iid, req in self.introductions.items() if req.target_person_id == person_id
        ]
        for iid in to_delete_intros:
            del self.introductions[iid]

        self.record_audit(
            actor_role=actor_role,
            action="DATA_ERASURE_EXECUTED",
            resource_type="person_profile",
            resource_id=person_id,
            summary=f"Deleted profile {removed.id}, associated RAG chunks, and {len(to_delete_intros)} intro records.",
        )
        return True

    # --- Introduction Consent Operations ---

    def create_introduction_request(
        self,
        requester_name: str,
        requester_interests: list[str],
        target_person_id: str,
        match_score: float,
        shared_topics: list[str],
        complementary_reason: str,
        suggested_icebreaker: str,
        requester_consent_granted: bool = False,
    ) -> IntroductionRequest:
        target = self.people.get(target_person_id)
        target_name = target.full_name if target else target_person_id
        status = (
            IntroductionConsentStatus.APPROVED_AND_LOGGED
            if requester_consent_granted and (target and target.opt_in_matchmaker)
            else IntroductionConsentStatus.PENDING_REQUESTER_CONSENT
        )
        intro = IntroductionRequest(
            intro_id=f"intro-{uuid.uuid4().hex[:8]}",
            requester_name=requester_name,
            requester_interests=requester_interests,
            target_person_id=target_person_id,
            target_person_name=target_name,
            match_score=match_score,
            shared_topics=shared_topics,
            complementary_reason=complementary_reason,
            suggested_icebreaker=suggested_icebreaker,
            requester_consent_granted=requester_consent_granted,
            status=status,
        )
        self.introductions[intro.intro_id] = intro
        self.record_audit(
            actor_role="MATCHMAKER_CONSENT_GATE",
            action="INTRO_REQUEST_CREATED",
            resource_type="introduction",
            resource_id=intro.intro_id,
            summary=f"Intro request created for {target_name} (consent={requester_consent_granted}, status={status.value}).",
        )
        return intro

    def grant_introduction_consent(self, intro_id: str) -> IntroductionRequest | None:
        intro = self.introductions.get(intro_id)
        if not intro:
            return None
        intro.requester_consent_granted = True
        intro.status = IntroductionConsentStatus.APPROVED_AND_LOGGED
        intro.updated_at = utc_now_iso()
        self.record_audit(
            actor_role="ATTENDEE_CONSENT",
            action="INTRO_CONSENT_GRANTED",
            resource_type="introduction",
            resource_id=intro_id,
            summary=f"Explicit consent granted for introduction {intro_id} -> {intro.target_person_name}.",
        )
        return intro

    # --- Organizer Schedule, Venue, Resource & Edition Reset Operations ---

    def upsert_session(self, session: EventSession) -> EventSession:
        self.sessions[session.id] = session
        doc = KnowledgeDocument(
            id=f"doc-{session.id}",
            event_id=session.event_id,
            title=f"{session.title} ({session.start_time}–{session.end_time}, {session.room})",
            doc_type="workshop" if session.format.value == "WORKSHOP" else "session",
            content=(
                f"Title: {session.title}\nTrack: {session.track} | Format: {session.format.value}\n"
                f"Time: {session.start_time}–{session.end_time} | Room: {session.room}\n"
                f"Speakers: {', '.join(session.speaker_names)}\nAbstract: {session.abstract}"
            ),
            source_uri=f"pismaniye://schedule/{session.id}",
            tags=session.tags + [session.track],
            verification_status=session.verification_status,
        )
        self.rag.ingest_document(doc, persist_blob=True)
        self.record_audit(
            actor_role="ORGANIZER",
            action="UPSERT_SESSION",
            resource_type="event_session",
            resource_id=session.id,
            summary=f"Updated session '{session.title}' ({session.start_time}-{session.end_time}).",
        )
        return session

    def update_venue(self, venue: VenueInfo) -> VenueInfo:
        self.venue = venue
        doc = KnowledgeDocument(
            id="doc-venue-logistics",
            event_id=venue.event_id,
            title=f"Venue & Logistics Guide — {venue.venue_name}",
            doc_type="venue",
            content=(
                f"Venue: {venue.venue_name} ({venue.city})\nAddress: {venue.address_note}\n"
                f"Rooms: {'; '.join(venue.rooms)}\nTransport: {'; '.join(venue.transport_notes)}"
            ),
            source_uri=f"pismaniye://venue/{venue.event_id}",
            tags=["venue", "logistics", "Kocaeli"],
            verification_status=venue.verification_status,
        )
        self.rag.ingest_document(doc, persist_blob=True)
        self.record_audit(
            actor_role="ORGANIZER",
            action="UPDATE_VENUE",
            resource_type="venue",
            resource_id=venue.event_id,
            summary=f"Updated venue information: {venue.venue_name} ({venue.verification_status.value}).",
        )
        return venue

    def add_community_resource(self, resource: CommunityResource) -> CommunityResource:
        self.community_resources[resource.id] = resource
        doc = KnowledgeDocument(
            id=f"doc-{resource.id}",
            event_id=self.edition_config.event_id,
            title=f"{resource.title} ({resource.category})",
            doc_type="learning" if "Learning" in resource.category else "community",
            content=(
                f"Resource: {resource.title}\nCategory: {resource.category}\n"
                f"Summary: {resource.summary}\nURL: {resource.url}\n"
                f"Contribute: {resource.how_to_contribute or ''}"
            ),
            source_uri=resource.url,
            tags=resource.topic_tags + [resource.category],
            verification_status=resource.verification_status,
        )
        self.rag.ingest_document(doc, persist_blob=True)
        self.record_audit(
            actor_role="ORGANIZER",
            action="ADD_COMMUNITY_RESOURCE",
            resource_type="community_resource",
            resource_id=resource.id,
            summary=f"Added community resource '{resource.title}'.",
        )
        return resource

    def moderate_submission(
        self,
        submission_id: str,
        decision: str,
        moderator_note: str = "",
    ) -> ModerationSubmission | None:
        sub = self.moderation_queue.get(submission_id)
        if not sub:
            return None
        sub.status = decision.upper()
        sub.moderator_note = moderator_note
        if sub.status == "APPROVED":
            res = CommunityResource(
                id=f"res-{sub.submission_id}",
                title=sub.title,
                category="Community Contributed",
                topic_tags=sub.tags,
                summary=sub.content,
                url=f"pismaniye://community/{sub.submission_id}",
                verification_status=VerificationStatus.VERIFIED_ORGANIZER_DATA,
            )
            self.add_community_resource(res)

        self.record_audit(
            actor_role="ORGANIZER_MODERATOR",
            action=f"MODERATION_{sub.status}",
            resource_type="moderation_submission",
            resource_id=submission_id,
            summary=f"Moderated submission '{sub.title}' -> {sub.status}.",
        )
        return sub

    def reset_for_new_edition(
        self,
        new_event_id: str = "devfest-kocaeli-2027",
        new_event_name: str = "DevFest Kocaeli 2027",
        new_year: int = 2027,
        keep_community_knowledge: bool = True,
    ) -> dict[str, Any]:
        """Reset event-specific schedule/attendees for a future edition while retaining reusable GDG Kocaeli assets."""
        self.edition_config = EventEditionConfig(
            event_id=new_event_id,
            event_name=new_event_name,
            edition_year=new_year,
            community_name="GDG Kocaeli",
            tagline="Unraveling People. Connecting Possibilities.",
            date_display=f"Autumn {new_year} • Ready for Organizer Schedule Import",
            is_sample_data=False,
        )
        self.sessions.clear()
        self.introductions.clear()
        # Keep organizers, clear event-specific attendees
        self.people = {
            pid: p for pid, p in self.people.items() if p.role.value == "ORGANIZER"
        }
        if keep_community_knowledge:
            # Remove only session-specific docs, keep Kocaeli & Community & Learning docs
            to_remove = [
                did for did, doc in self.rag.documents.items() if doc.doc_type in ("session", "workshop")
            ]
            for did in to_remove:
                self.rag.delete_document(did)
        else:
            self.rag.documents.clear()
            self.rag.chunks.clear()

        self.record_audit(
            actor_role="ORGANIZER",
            action="EDITION_RESET",
            resource_type="event_edition",
            resource_id=new_event_id,
            summary=(
                f"Reset event-specific schedule for {new_event_name} ({new_event_id}); "
                f"preserved {len(self.kocaeli_places)} Kocaeli guides and {len(self.community_resources)} community resources."
            ),
        )
        return {
            "new_event_id": new_event_id,
            "new_event_name": new_event_name,
            "edition_year": new_year,
            "preserved_kocaeli_places": len(self.kocaeli_places),
            "preserved_community_resources": len(self.community_resources),
            "remaining_knowledge_documents": len(self.rag.documents),
        }

    def generate_event_report(self) -> dict[str, Any]:
        """Export comprehensive community & operational analytics report for organizers."""
        discoverable = self.list_discoverable_people()
        workflow_counts: dict[str, int] = {}
        for tr in self.traces.values():
            workflow_counts[tr.workflow_name] = workflow_counts.get(tr.workflow_name, 0) + 1

        report = {
            "generated_at": utc_now_iso(),
            "event_edition": self.edition_config.model_dump(),
            "metrics": {
                "total_profiles": len(self.people),
                "opt_in_discoverable_profiles": len(discoverable),
                "private_opted_out_profiles": len(self.people) - len(discoverable),
                "scheduled_sessions": len(self.sessions),
                "kocaeli_verified_places": len(self.kocaeli_places),
                "community_resources": len(self.community_resources),
                "knowledge_documents": len(self.rag.documents),
                "knowledge_chunks": len(self.rag.chunks),
                "orchestration_traces_executed": len(self.traces),
                "xai_decisions_audited": len(self.decisions),
                "introductions_requested": len(self.introductions),
                "introductions_consented": sum(
                    1 for i in self.introductions.values() if i.requester_consent_granted
                ),
                "workflows_by_type": workflow_counts,
            },
            "recent_audit_trail": [a.model_dump() for a in self.audit_logs[-15:]],
        }
        report_path = self.state_dir / "reports" / f"report-{self.edition_config.event_id}.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report


_repo: PismaniyeRepository | None = None


def get_repository() -> PismaniyeRepository:
    global _repo
    if _repo is None:
        _repo = PismaniyeRepository()
    return _repo


def reset_repository() -> PismaniyeRepository:
    global _repo
    _repo = PismaniyeRepository()
    return _repo
