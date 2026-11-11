"""FastAPI Backend serving the Community Web Application, Organizer Dashboard, and Multi-Agent API."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field
import qrcode
import qrcode.image.svg

from pismaniye.config import get_settings
from pismaniye.data.repository import get_repository
from pismaniye.orchestration.graph import get_orchestrator
from pismaniye.privacy.guardrails import PrivacyGuard
from pismaniye.schemas.domain import (
    CommunityResource,
    EventSession,
    KnowledgeDocument,
    ModerationSubmission,
    PersonProfile,
    ProfileVisibility,
    RoleType,
    SessionFormat,
    VenueInfo,
    VerificationStatus,
)

app = FastAPI(
    title="PISMANIYE — Multi-Agent Community Intelligence & Concierge API",
    description="Built for GDG Kocaeli & DevFest Kocaeli 2026 ('Unraveling People. Connecting Possibilities.')",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-Organizer-Token"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Any) -> Response:
    """Attach strict HTTP security headers to all API and Web responses."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; frame-ancestors 'none';"
    )
    return response

WEB_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "web" / "index.html"


# --- Request Payload Models ---


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    workflow: str | None = Field(default=None, max_length=64)
    interests: list[str] | None = Field(default=None, max_length=20)
    hours: float | None = Field(default=None, ge=0.5, le=24.0)


class SpeakerUpsertRequest(BaseModel):
    id: str | None = None
    full_name: str
    role: RoleType = RoleType.SPEAKER
    headline: str
    organization: str
    gde_category: str | None = None
    country: str = "Türkiye"
    bio: str
    interests: list[str] = Field(default_factory=list)
    expertise_tags: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    can_mentor_on: list[str] = Field(default_factory=list)
    opt_in_networking: bool = True
    opt_in_matchmaker: bool = True
    verification_status: VerificationStatus = VerificationStatus.VERIFIED_ORGANIZER_DATA


class SessionUpsertRequest(BaseModel):
    id: str | None = None
    title: str
    track: str = "AI & Agents"
    format: SessionFormat = SessionFormat.TECHNICAL_TALK
    level: str = "Intermediate"
    start_time: str = "15:00"
    end_time: str = "15:45"
    room: str = "Main Hall — Pişmaniye Stage"
    speaker_names: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    abstract: str
    verification_status: VerificationStatus = VerificationStatus.VERIFIED_ORGANIZER_DATA


class VenueUpdateRequest(BaseModel):
    venue_name: str
    city: str = "Kocaeli (İzmit)"
    address_note: str
    rooms: list[str]
    wifi_ssid: str = "GDG-Kocaeli-Verified"
    transport_notes: list[str] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED_ORGANIZER_DATA


class ResourceCreateRequest(BaseModel):
    id: str | None = None
    title: str
    category: str = "Learning Path"
    topic_tags: list[str] = Field(default_factory=list)
    difficulty: str = "Intermediate"
    summary: str
    url: str
    estimated_hours: float = 2.0
    how_to_contribute: str | None = None
    verification_status: VerificationStatus = VerificationStatus.VERIFIED_ORGANIZER_DATA


class KnowledgeDocUpsertRequest(BaseModel):
    id: str | None = None
    title: str
    doc_type: str = "community"
    content: str
    source_uri: str = "pismaniye://organizer/custom"
    tags: list[str] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED_ORGANIZER_DATA


class CommunitySubmissionRequest(BaseModel):
    submitter_name: str = Field(..., min_length=1, max_length=120)
    submission_type: str = Field(default="community_resource", max_length=64)
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=4000)
    tags: list[str] = Field(default_factory=list, max_length=15)


class ModerationDecisionRequest(BaseModel):
    decision: str  # APPROVED or REJECTED
    moderator_note: str = ""


class AgentConfigUpdateRequest(BaseModel):
    enabled_agents: list[str] | None = None
    agent_weights: dict[str, float] | None = None


class EditionResetRequest(BaseModel):
    new_event_id: str = "devfest-kocaeli-2027"
    new_event_name: str = "DevFest Kocaeli 2027"
    new_year: int = 2027
    keep_community_knowledge: bool = True


def require_organizer_auth(
    x_organizer_token: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    if not PrivacyGuard.verify_organizer_role(x_organizer_token, settings.organizer_passcode):
        raise HTTPException(
            status_code=403,
            detail="Organizer RBAC authorization required. Provide valid X-Organizer-Token header.",
        )
    return "ORGANIZER"


# --- Web Frontend & QR Endpoints ---


@app.get("/", response_class=HTMLResponse)
def serve_web_app() -> HTMLResponse:
    if WEB_TEMPLATE_PATH.exists():
        return HTMLResponse(WEB_TEMPLATE_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Pismaniye Web UI not found</h1>", status_code=404)


@app.get("/api/qr.svg")
def generate_qr_svg(request: Request, url: str | None = Query(default=None, max_length=256)) -> Response:
    base_fallback = str(request.base_url).rstrip("/") if request.base_url else get_settings().public_web_url
    target_url = (url or base_fallback).strip()
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        raise HTTPException(status_code=400, detail="QR URL must use http:// or https:// scheme.")
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(target_url, image_factory=factory, border=1)
    buf = io.BytesIO()
    img.save(buf)
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


@app.get("/api/health")
def health_check() -> dict[str, Any]:
    repo = get_repository()
    orchestrator = get_orchestrator()
    return {
        "status": "healthy",
        "event": repo.edition_config.model_dump(),
        "mode": repo.settings.mode,
        "rag": repo.rag.stats(),
        "agents": orchestrator.adk_bridge.export_adk_agent_descriptors(),
        "discoverable_people_count": len(repo.list_discoverable_people()),
        "sessions_count": len(repo.sessions),
        "kocaeli_places_count": len(repo.kocaeli_places),
    }


# --- Community Concierge & Multi-Agent Endpoints ---


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest) -> dict[str, Any]:
    orchestrator = get_orchestrator()
    live_events = []
    trace = orchestrator.run_query(
        query=req.query,
        explicit_workflow=req.workflow,
        explicit_interests=req.interests,
        explicit_hours=req.hours,
        event_callback=lambda ev: live_events.append(ev.model_dump()),
    )
    return {
        "trace": trace.model_dump(),
        "live_events": live_events,
    }


@app.get("/api/schedule")
def list_schedule(interest: str | None = Query(default=None)) -> dict[str, Any]:
    repo = get_repository()
    orchestrator = get_orchestrator()
    sessions = sorted(repo.sessions.values(), key=lambda s: (s.start_time, s.room))
    agenda_payload = None
    if interest:
        interests_list = [i.strip() for i in interest.split(",") if i.strip()]
        _, _, agenda_payload = orchestrator.event_agent.execute(
            query=f"Build agenda for {interest}",
            interests=interests_list,
        )
    return {
        "event": repo.edition_config.model_dump(),
        "venue": repo.venue.model_dump(),
        "sessions": [s.model_dump() for s in sessions],
        "personalized_agenda": agenda_payload,
    }


@app.get("/api/people")
def discover_people(interest: str | None = Query(default=None)) -> dict[str, Any]:
    repo = get_repository()
    orchestrator = get_orchestrator()
    if interest:
        interests_list = [i.strip() for i in interest.split(",") if i.strip()]
        _, _, payload = orchestrator.people_agent.execute(
            query=f"Discover people for {interest}",
            interests=interests_list,
        )
        return {
            "people": payload["discovered_people"],
            "privacy_notice": "Only explicitly opted-in profiles are returned. Private email/phone fields are never exposed.",
        }
    people = [PrivacyGuard.sanitize_profile(p) for p in repo.list_discoverable_people()]
    return {
        "people": people,
        "privacy_notice": "Only explicitly opted-in profiles are returned. Private email/phone fields are never exposed.",
    }


@app.post("/api/matchmaker")
def matchmaker_endpoint(req: ChatRequest) -> dict[str, Any]:
    orchestrator = get_orchestrator()
    trace = orchestrator.run_query(
        query=req.query or "Who should I meet?",
        explicit_workflow="workflow_a",
        explicit_interests=req.interests,
    )
    return {
        "trace_id": trace.trace_id,
        "decision_id": trace.decision_id,
        "matches": trace.structured_payload.get("matchmaker_agent", {}).get("matches", []),
        "explanation": trace.explanation.model_dump() if trace.explanation else None,
    }


@app.post("/api/introductions/{intro_id}/consent")
def grant_intro_consent_endpoint(intro_id: str) -> dict[str, Any]:
    repo = get_repository()
    updated = repo.grant_introduction_consent(intro_id)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Introduction request {intro_id} not found.")
    return {
        "status": "consent_recorded",
        "introduction": updated.model_dump(),
        "privacy_note": "Consent recorded in audit trail. Organizers/concierge can now broker the double opt-in handoff without exposing raw phone/email.",
    }


@app.get("/api/kocaeli")
def explore_kocaeli_endpoint(hours: float = Query(default=3.0, ge=0.5, le=24.0)) -> dict[str, Any]:
    orchestrator = get_orchestrator()
    _, _, payload = orchestrator.kocaeli_agent.execute(
        query=f"Explore Kocaeli in {hours:g} hours",
        hours=hours,
    )
    return payload


@app.get("/api/community")
def list_community_resources(topic: str | None = Query(default=None)) -> dict[str, Any]:
    orchestrator = get_orchestrator()
    interests = [t.strip() for t in topic.split(",")] if topic else None
    _, _, payload = orchestrator.community_agent.execute(
        query=f"Learning path for {topic or 'Agentic AI'}",
        interests=interests,
    )
    return payload


def _strip_html_tags(value: str) -> str:
    """Neutralize angle brackets to prevent stored HTML/script injection in community submissions."""
    return value.replace("<", "&lt;").replace(">", "&gt;").strip()


@app.post("/api/community/submit")
def submit_community_item(req: CommunitySubmissionRequest) -> dict[str, Any]:
    repo = get_repository()
    safe_title = _strip_html_tags(PrivacyGuard.redact_pii_text(req.title))
    safe_submitter = _strip_html_tags(PrivacyGuard.redact_pii_text(req.submitter_name))
    safe_content = _strip_html_tags(PrivacyGuard.redact_pii_text(req.content))
    safe_tags = [_strip_html_tags(t)[:40] for t in req.tags if t.strip()]
    sub = ModerationSubmission(
        submission_id=f"mod-{uuid.uuid4().hex[:8]}",
        submitter_name=safe_submitter,
        submission_type=_strip_html_tags(req.submission_type),
        title=safe_title,
        content=safe_content,
        tags=safe_tags,
        status="PENDING",
    )
    repo.moderation_queue[sub.submission_id] = sub
    repo.record_audit(
        actor_role="COMMUNITY_MEMBER",
        action="SUBMISSION_CREATED",
        resource_type="moderation_submission",
        resource_id=sub.submission_id,
        summary=f"Community submission '{sub.title}' queued for organizer moderation.",
    )
    return {"submission": sub.model_dump()}


@app.get("/api/knowledge/search")
def search_knowledge_endpoint(
    q: str = Query(..., min_length=1, max_length=300),
    top_k: int = Query(default=5, ge=1, le=25),
) -> dict[str, Any]:
    repo = get_repository()
    citations = repo.rag.search(query=q, top_k=top_k)
    return {
        "query": q,
        "citations": [c.model_dump() for c in citations],
        "stats": repo.rag.stats(),
    }


@app.get("/api/traces/{trace_id}")
def get_trace_endpoint(trace_id: str) -> dict[str, Any]:
    repo = get_repository()
    tr = repo.get_trace(trace_id)
    if not tr:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found.")
    return tr.model_dump()


@app.get("/api/decisions/{decision_id}")
def get_decision_endpoint(decision_id: str) -> dict[str, Any]:
    repo = get_repository()
    dec = repo.get_decision(decision_id)
    if not dec:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found.")
    return dec.model_dump()


# --- Privacy & Data Deletion Controls (RBAC Protected) ---


@app.delete("/api/privacy/profile/{person_id}")
def delete_profile_privacy_endpoint(
    person_id: str,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    deleted = repo.delete_person_data(person_id, actor_role="PRIVACY_ERASURE_API")
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Profile {person_id} not found.")
    return {
        "deleted": True,
        "person_id": person_id,
        "retention_days_policy": repo.settings.data_retention_days,
        "message": "Profile, RAG knowledge chunks, and pending introduction records permanently erased.",
    }


# --- Organizer Dashboard Endpoints (RBAC Protected) ---


@app.post("/api/organizer/speakers")
def organizer_upsert_speaker(
    req: SpeakerUpsertRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    pid = req.id or f"spk-{uuid.uuid4().hex[:8]}"
    profile = PersonProfile(
        id=pid,
        full_name=req.full_name,
        role=req.role,
        headline=req.headline,
        organization=req.organization,
        gde_category=req.gde_category,
        country=req.country,
        bio=req.bio,
        interests=req.interests,
        expertise_tags=req.expertise_tags,
        technologies=req.technologies,
        can_mentor_on=req.can_mentor_on,
        visibility=ProfileVisibility.PUBLIC if req.opt_in_networking else ProfileVisibility.PRIVATE,
        opt_in_networking=req.opt_in_networking,
        opt_in_matchmaker=req.opt_in_matchmaker,
        verification_status=req.verification_status,
        synthetic_disclaimer="Verified by GDG Kocaeli Organizer."
        if req.verification_status == VerificationStatus.VERIFIED_ORGANIZER_DATA
        else "Sample profile.",
    )
    saved = repo.upsert_person(profile, actor_role="ORGANIZER")
    return {"speaker": PrivacyGuard.sanitize_profile(saved)}


@app.post("/api/organizer/sessions")
def organizer_upsert_session(
    req: SessionUpsertRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    sid = req.id or f"sess-{uuid.uuid4().hex[:8]}"
    session = EventSession(
        id=sid,
        event_id=repo.edition_config.event_id,
        title=req.title,
        track=req.track,
        format=req.format,
        level=req.level,
        start_time=req.start_time,
        end_time=req.end_time,
        room=req.room,
        speaker_names=req.speaker_names,
        tags=req.tags,
        abstract=req.abstract,
        verification_status=req.verification_status,
    )
    saved = repo.upsert_session(session)
    return {"session": saved.model_dump()}


@app.put("/api/organizer/venue")
def organizer_update_venue(
    req: VenueUpdateRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    venue = VenueInfo(
        event_id=repo.edition_config.event_id,
        venue_name=req.venue_name,
        city=req.city,
        address_note=req.address_note,
        rooms=req.rooms,
        wifi_ssid=req.wifi_ssid,
        transport_notes=req.transport_notes,
        emergency_and_code_of_conduct=repo.venue.emergency_and_code_of_conduct,
        verification_status=req.verification_status,
    )
    saved = repo.update_venue(venue)
    return {"venue": saved.model_dump()}


@app.post("/api/organizer/resources")
def organizer_add_resource(
    req: ResourceCreateRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    rid = req.id or f"res-{uuid.uuid4().hex[:8]}"
    resource = CommunityResource(
        id=rid,
        title=req.title,
        category=req.category,
        topic_tags=req.topic_tags,
        difficulty=req.difficulty,
        summary=req.summary,
        url=req.url,
        estimated_hours=req.estimated_hours,
        how_to_contribute=req.how_to_contribute,
        verification_status=req.verification_status,
    )
    saved = repo.add_community_resource(resource)
    return {"resource": saved.model_dump()}


@app.post("/api/organizer/knowledge")
def organizer_upsert_knowledge(
    req: KnowledgeDocUpsertRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    did = req.id or f"doc-{uuid.uuid4().hex[:8]}"
    doc = KnowledgeDocument(
        id=did,
        event_id=repo.edition_config.event_id,
        title=req.title,
        doc_type=req.doc_type,
        content=req.content,
        source_uri=req.source_uri,
        tags=req.tags,
        verification_status=req.verification_status,
    )
    chunks_indexed = repo.rag.ingest_document(doc, persist_blob=True)
    repo.record_audit(
        actor_role="ORGANIZER",
        action="UPSERT_KNOWLEDGE_DOC",
        resource_type="knowledge_document",
        resource_id=did,
        summary=f"Ingested knowledge document '{doc.title}' ({chunks_indexed} chunks indexed).",
    )
    return {"document": doc.model_dump(), "chunks_indexed": chunks_indexed}


@app.get("/api/organizer/moderation")
def organizer_list_moderation(
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    return {
        "submissions": [s.model_dump() for s in repo.moderation_queue.values()],
        "introductions": [i.model_dump() for i in repo.introductions.values()],
    }


@app.post("/api/organizer/moderation/{submission_id}")
def organizer_moderate_submission(
    submission_id: str,
    req: ModerationDecisionRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    sub = repo.moderate_submission(submission_id, req.decision, req.moderator_note)
    if not sub:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found.")
    return {"submission": sub.model_dump()}


@app.put("/api/organizer/agents/config")
def organizer_update_agent_config(
    req: AgentConfigUpdateRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    if req.enabled_agents is not None:
        repo.edition_config.enabled_agents = req.enabled_agents
    if req.agent_weights is not None:
        repo.edition_config.agent_weights.update(req.agent_weights)
    repo.record_audit(
        actor_role="ORGANIZER",
        action="UPDATE_AGENT_CONFIG",
        resource_type="agent_config",
        resource_id=repo.edition_config.event_id,
        summary=f"Updated agent configuration (weights={repo.edition_config.agent_weights}).",
    )
    return {"edition_config": repo.edition_config.model_dump()}


@app.get("/api/organizer/analytics")
def organizer_analytics(
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    return repo.generate_event_report()


@app.get("/api/organizer/report")
def organizer_export_report(
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    return repo.generate_event_report()


@app.post("/api/organizer/reset-edition")
def organizer_reset_edition(
    req: EditionResetRequest,
    _role: str = Depends(require_organizer_auth),
) -> dict[str, Any]:
    repo = get_repository()
    return repo.reset_for_new_edition(
        new_event_id=req.new_event_id,
        new_event_name=req.new_event_name,
        new_year=req.new_year,
        keep_community_knowledge=req.keep_community_knowledge,
    )
