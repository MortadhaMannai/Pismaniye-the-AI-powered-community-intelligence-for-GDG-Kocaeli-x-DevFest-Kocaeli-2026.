"""Core domain Pydantic schemas for PISMANIYE."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class VerificationStatus(str, Enum):
    """Explicitly distinguishes verified organizer data, synthetic samples, and AI suggestions."""

    SYNTHETIC_SAMPLE = "SYNTHETIC_SAMPLE"
    VERIFIED_ORGANIZER_DATA = "VERIFIED_ORGANIZER_DATA"
    GENERATED_SUGGESTION = "GENERATED_SUGGESTION"
    COMMUNITY_SUBMITTED_PENDING = "COMMUNITY_SUBMITTED_PENDING"


class RoleType(str, Enum):
    SPEAKER = "SPEAKER"
    GDE = "GDE"
    ORGANIZER = "ORGANIZER"
    ATTENDEE = "ATTENDEE"
    MODERATOR = "MODERATOR"


class ProfileVisibility(str, Enum):
    PUBLIC = "PUBLIC"
    OPT_IN_COMMUNITY = "OPT_IN_COMMUNITY"
    PRIVATE = "PRIVATE"


class PersonProfile(BaseModel):
    """Profile for Speakers, GDEs, Organizers, and Opt-In Attendees.

    Private contact fields (`private_email`, `private_phone`) are strictly excluded
    from public views and agent outputs via `to_public_dict()`.
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    full_name: str
    role: RoleType
    headline: str
    organization: str
    gde_category: str | None = None
    country: str = "Türkiye"
    bio: str
    interests: list[str] = Field(default_factory=list)
    expertise_tags: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    looking_for: list[str] = Field(default_factory=list)
    can_mentor_on: list[str] = Field(default_factory=list)
    speaking_session_ids: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["English", "Turkish"])
    visibility: ProfileVisibility = ProfileVisibility.PUBLIC
    opt_in_networking: bool = True
    opt_in_matchmaker: bool = True
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE
    synthetic_disclaimer: str = (
        "Fictional sample profile for DevFest Kocaeli 2026 demonstration until organizer verification."
    )
    # Strictly private fields — NEVER exposed by agents or public endpoints
    private_email: str | None = Field(default=None, exclude=True)
    private_phone: str | None = Field(default=None, exclude=True)

    def to_public_dict(self) -> dict[str, Any]:
        """Return safe dictionary guaranteed to exclude private contact details."""
        data = self.model_dump(exclude={"private_email", "private_phone"})
        return data


class SessionFormat(str, Enum):
    KEYNOTE = "KEYNOTE"
    TECHNICAL_TALK = "TECHNICAL_TALK"
    WORKSHOP = "WORKSHOP"
    PANEL = "PANEL"
    LIGHTNING_TALK = "LIGHTNING_TALK"
    NETWORKING = "NETWORKING"


class EventSession(BaseModel):
    """Event session, talk, or workshop."""

    id: str
    event_id: str = "devfest-kocaeli-2026"
    title: str
    track: str
    format: SessionFormat
    level: str = "Intermediate"
    start_time: str  # HH:MM format e.g. "10:00"
    end_time: str    # HH:MM format e.g. "10:45"
    room: str
    speaker_ids: list[str] = Field(default_factory=list)
    speaker_names: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    abstract: str
    key_takeaways: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    capacity: int = 200
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE


class VenueInfo(BaseModel):
    """Venue and logistics details for an event edition."""

    event_id: str = "devfest-kocaeli-2026"
    venue_name: str
    city: str = "Kocaeli (İzmit)"
    address_note: str
    rooms: list[str] = Field(default_factory=list)
    wifi_ssid: str = "GDG-Kocaeli-DevFest-Sample"
    accessibility_notes: list[str] = Field(default_factory=list)
    transport_notes: list[str] = Field(default_factory=list)
    emergency_and_code_of_conduct: str
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE


class KocaeliPlace(BaseModel):
    """Local cultural, culinary, or landmark spot in Kocaeli."""

    id: str
    name: str
    category: str  # Landmark, Gastronomy, Waterfront, Museum, Nature, Innovation
    summary: str
    cultural_context: str
    recommended_duration_minutes: int
    travel_time_from_venue_minutes: int
    opening_hours: str  # e.g. "09:00-21:00"
    tags: list[str] = Field(default_factory=list)
    visitor_tip: str
    best_for: list[str] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE


class CommunityResource(BaseModel):
    """GDG Kocaeli learning resource, past meetup, or contribution path."""

    id: str
    title: str
    category: str  # Learning Path, Past Meetup, Codelab, CFP / Contribution, Study Jam, Documentation
    topic_tags: list[str] = Field(default_factory=list)
    difficulty: str = "Beginner to Intermediate"
    summary: str
    url: str
    estimated_hours: float = 2.0
    related_session_ids: list[str] = Field(default_factory=list)
    how_to_contribute: str | None = None
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE


class KnowledgeDocument(BaseModel):
    """Source document in the Organizer-Managed Knowledge Base."""

    id: str
    event_id: str = "devfest-kocaeli-2026"
    title: str
    doc_type: str  # speaker_bio, gde_profile, session, schedule, workshop, venue, kocaeli, community, past_event, learning
    content: str
    source_uri: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE
    updated_at: str = Field(default_factory=utc_now_iso)


class KnowledgeChunk(BaseModel):
    """Chunked, indexed unit of a KnowledgeDocument with embedding vector."""

    chunk_id: str
    doc_id: str
    event_id: str = "devfest-kocaeli-2026"
    doc_title: str
    doc_type: str
    text: str
    chunk_index: int
    tags: list[str] = Field(default_factory=list)
    source_uri: str
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE
    embedding: list[float] = Field(default_factory=list, repr=False)


class IntroductionConsentStatus(str, Enum):
    PENDING_REQUESTER_CONSENT = "PENDING_REQUESTER_CONSENT"
    PENDING_TARGET_OPT_IN_CHECK = "PENDING_TARGET_OPT_IN_CHECK"
    APPROVED_AND_LOGGED = "APPROVED_AND_LOGGED"
    DECLINED = "DECLINED"


class IntroductionRequest(BaseModel):
    """Consent-gated networking introduction between two community members."""

    intro_id: str
    requester_name: str
    requester_interests: list[str]
    target_person_id: str
    target_person_name: str
    match_score: float
    shared_topics: list[str]
    complementary_reason: str
    suggested_icebreaker: str
    requester_consent_granted: bool = False
    status: IntroductionConsentStatus = IntroductionConsentStatus.PENDING_REQUESTER_CONSENT
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


class ModerationSubmission(BaseModel):
    """Community submission awaiting organizer moderation."""

    submission_id: str
    submitter_name: str
    submission_type: str  # community_resource, lightning_talk_idea, attendee_opt_in, feedback
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    moderator_note: str | None = None
    created_at: str = Field(default_factory=utc_now_iso)


class AuditLogEntry(BaseModel):
    """Immutable audit log entry for privacy, consent, and organizer operations."""

    audit_id: str
    timestamp: str = Field(default_factory=utc_now_iso)
    actor_role: str
    action: str
    resource_type: str
    resource_id: str
    summary: str
    privacy_safe: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventEditionConfig(BaseModel):
    """Configuration for a specific GDG Kocaeli event edition (e.g. 2026, 2027)."""

    event_id: str
    event_name: str
    edition_year: int
    community_name: str = "GDG Kocaeli"
    tagline: str = "Unraveling People. Connecting Possibilities."
    date_display: str = "November 2026 (Sample Schedule — Organizer Configurable)"
    is_sample_data: bool = True
    enabled_agents: list[str] = Field(
        default_factory=lambda: [
            "event_agent",
            "people_agent",
            "knowledge_agent",
            "kocaeli_agent",
            "matchmaker_agent",
            "community_agent",
            "xai_auditor",
        ]
    )
    agent_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "interest_overlap": 0.40,
            "expertise_complementarity": 0.35,
            "mentorship_alignment": 0.25,
        }
    )
