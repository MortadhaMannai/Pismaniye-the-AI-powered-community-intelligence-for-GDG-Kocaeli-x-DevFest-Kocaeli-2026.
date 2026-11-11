"""Schemas for Multi-Agent Orchestration, Telemetry Traces, RAG Evidence, and XAI Auditing."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from pismaniye.schemas.domain import VerificationStatus, utc_now_iso


class AgentID(str, Enum):
    SUPERVISOR = "supervisor"
    EVENT_AGENT = "event_agent"
    PEOPLE_AGENT = "people_agent"
    KNOWLEDGE_AGENT = "knowledge_agent"
    KOCAELI_AGENT = "kocaeli_agent"
    MATCHMAKER_AGENT = "matchmaker_agent"
    COMMUNITY_AGENT = "community_agent"
    XAI_AUDITOR = "xai_auditor"


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    ROUTING = "ROUTING"
    THINKING = "THINKING"
    CALLING_TOOL = "CALLING_TOOL"
    RETRIEVING_RAG = "RETRIEVING_RAG"
    AUDITING_XAI = "AUDITING_XAI"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class EvidenceCitation(BaseModel):
    """A single grounded piece of evidence retrieved via RAG or structured tool call."""

    source_id: str
    source_title: str
    source_type: str
    source_uri: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE


class ScoringBreakdown(BaseModel):
    """Transparent factor-by-factor scoring for recommendations (sessions, matches, places)."""

    item_id: str
    item_name: str
    total_score: float = Field(ge=0.0, le=1.0)
    factors: dict[str, float] = Field(default_factory=dict)
    rationale: str
    verification_status: VerificationStatus = VerificationStatus.SYNTHETIC_SAMPLE


class ToolCallRecord(BaseModel):
    """Record of an actual backend tool invocation by an agent."""

    call_id: str
    agent_id: AgentID
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result_summary: str
    items_returned: int = 0
    duration_ms: float = 0.0
    timestamp: str = Field(default_factory=utc_now_iso)


class AgentExecutionStep(BaseModel):
    """A discrete execution step in the multi-agent orchestration graph."""

    step_id: str
    agent_id: AgentID
    agent_label: str
    status: AgentStatus
    thought: str
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    rag_citations: list[EvidenceCitation] = Field(default_factory=list)
    output_summary: str = ""
    confidence: float = 0.92
    duration_ms: float = 0.0
    started_at: str = Field(default_factory=utc_now_iso)
    completed_at: str | None = None


class DecisionExplanation(BaseModel):
    """XAI Audit & Decision Provenance object inspectable via `pismaniye explain <decision_id>`."""

    decision_id: str
    trace_id: str
    query: str
    workflow_type: str
    participating_agents: list[AgentID]
    primary_recommendation_summary: str
    scoring_breakdowns: list[ScoringBreakdown] = Field(default_factory=list)
    evidence_citations: list[EvidenceCitation] = Field(default_factory=list)
    provenance_chain: list[str] = Field(default_factory=list)
    uncertainty_score: float = Field(
        default=0.08,
        ge=0.0,
        le=1.0,
        description="Epistemic/data uncertainty (0 = fully verified, higher = sample/inferred).",
    )
    uncertainty_notes: list[str] = Field(default_factory=list)
    privacy_checks_passed: list[str] = Field(default_factory=list)
    verified_vs_generated_note: str = (
        "All source records are tagged with VerificationStatus; generated introductions/rationales "
        "are labeled GENERATED_SUGGESTION and grounded on cited records."
    )
    created_at: str = Field(default_factory=utc_now_iso)


class TraceRecord(BaseModel):
    """End-to-end execution trace inspectable via `pismaniye trace <trace_id>`."""

    trace_id: str
    decision_id: str
    event_id: str = "devfest-kocaeli-2026"
    query: str
    detected_intents: list[str] = Field(default_factory=list)
    workflow_name: str
    execution_mode: str = "local_deterministic"
    orchestrator_engine: str = "LangGraph + Google ADK Bridge"
    steps: list[AgentExecutionStep] = Field(default_factory=list)
    total_duration_ms: float = 0.0
    final_response_markdown: str = ""
    structured_payload: dict[str, Any] = Field(default_factory=dict)
    explanation: DecisionExplanation | None = None
    otel_trace_id: str | None = None
    created_at: str = Field(default_factory=utc_now_iso)


class LiveOrchestrationEvent(BaseModel):
    """Real-time event emitted during orchestration for CLI and Web SSE visualization."""

    event_type: str  # route_start, agent_start, tool_call, rag_retrieval, agent_complete, xai_audit, workflow_complete
    trace_id: str
    agent_id: AgentID | None = None
    agent_label: str | None = None
    status: AgentStatus | None = None
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: str = Field(default_factory=utc_now_iso)
