"""Stateful Multi-Agent Orchestrator built on LangGraph StateGraph + Google ADK Bridge."""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph

from pismaniye.adapters.google_cloud import GoogleADKBridge
from pismaniye.adapters.telemetry import get_telemetry
from pismaniye.agents.specialists import (
    CommunityAgent,
    EventAgent,
    KnowledgeAgent,
    KocaeliAgent,
    MatchmakerAgent,
    PeopleAgent,
)
from pismaniye.data.repository import PismaniyeRepository, get_repository
from pismaniye.privacy.guardrails import PrivacyGuard
from pismaniye.schemas.agent import (
    AgentExecutionStep,
    AgentID,
    AgentStatus,
    DecisionExplanation,
    LiveOrchestrationEvent,
    ScoringBreakdown,
    ToolCallRecord,
    TraceRecord,
)
from pismaniye.xai.auditor import XAIAuditor

EventCallback = Callable[[LiveOrchestrationEvent], None]


class OrchestrationGraphState(TypedDict, total=False):
    trace_id: str
    query: str
    explicit_workflow: str | None
    explicit_interests: list[str] | None
    explicit_hours: float | None
    detected_intents: list[str]
    workflow_name: str
    agent_plan: list[str]
    current_agent_idx: int
    steps: list[AgentExecutionStep]
    scoring_breakdowns: list[ScoringBreakdown]
    structured_payload: dict[str, Any]
    explanation: DecisionExplanation | None
    final_response_markdown: str


class PismaniyeOrchestrator:
    """Explicit stateful multi-agent orchestrator powered by LangGraph and Google ADK descriptors."""

    def __init__(self, repo: PismaniyeRepository | None = None) -> None:
        self.repo = repo or get_repository()
        self.telemetry = get_telemetry()
        self.adk_bridge = GoogleADKBridge(self.repo.settings)

        self.event_agent = EventAgent(self.repo)
        self.people_agent = PeopleAgent(self.repo)
        self.knowledge_agent = KnowledgeAgent(self.repo)
        self.kocaeli_agent = KocaeliAgent(self.repo)
        self.matchmaker_agent = MatchmakerAgent(self.repo)
        self.community_agent = CommunityAgent(self.repo)
        self.xai_auditor = XAIAuditor()

        self._active_callback: EventCallback | None = None
        self.compiled_graph = self._build_langgraph()

    def _emit(
        self,
        event_type: str,
        trace_id: str,
        message: str,
        agent_id: AgentID | None = None,
        agent_label: str | None = None,
        status: AgentStatus | None = None,
        detail: dict[str, Any] | None = None,
        duration_ms: float = 0.0,
    ) -> None:
        if self._active_callback is not None:
            ev = LiveOrchestrationEvent(
                event_type=event_type,
                trace_id=trace_id,
                agent_id=agent_id,
                agent_label=agent_label,
                status=status,
                message=message,
                detail=detail or {},
                duration_ms=duration_ms,
            )
            self._active_callback(ev)

    def _classify_workflow_and_plan(
        self,
        query: str,
        explicit_workflow: str | None = None,
    ) -> tuple[str, list[str], list[str]]:
        q = query.lower()
        if explicit_workflow == "workflow_a" or any(
            kw in q for kw in ["who should i meet", "match", "introduce", "connect with", "expert", "networking"]
        ):
            return (
                "WORKFLOW_A_MEET_THE_RIGHT_EXPERT",
                ["networking_discovery", "compatibility_scoring", "consent_gated_intro"],
                ["people_agent", "matchmaker_agent", "knowledge_agent"],
            )

        if explicit_workflow == "workflow_b" or any(
            kw in q for kw in ["agenda", "schedule", "devfest day", "which session", "talk", "workshop", "venue"]
        ):
            return (
                "WORKFLOW_B_MY_DEVFEST_DAY",
                ["schedule_retrieval", "conflict_resolution", "personalized_agenda"],
                ["event_agent", "knowledge_agent"],
            )

        if explicit_workflow == "workflow_c" or any(
            kw in q for kw in ["kocaeli", "free hour", "three free hours", "visit", "explore", "itinerary", "sekapark", "local"]
        ):
            return (
                "WORKFLOW_C_DISCOVER_KOCAELI",
                ["time_budget_extraction", "local_kocaeli_discovery", "itinerary_planning"],
                ["kocaeli_agent", "knowledge_agent"],
            )

        if explicit_workflow == "workflow_d" or any(
            kw in q for kw in ["start learning", "after devfest", "learning path", "study jam", "contribute", "community"]
        ):
            return (
                "WORKFLOW_D_COMMUNITY_KNOWLEDGE",
                ["learning_goal_analysis", "pathway_construction", "community_contribution"],
                ["community_agent", "event_agent", "knowledge_agent"],
            )

        # General multi-agent inquiry
        plan = ["knowledge_agent", "people_agent", "event_agent"]
        return ("MULTI_AGENT_CONCIERGE_INQUIRY", ["hybrid_rag", "community_concierge"], plan)

    def _build_langgraph(self) -> Any:
        graph = StateGraph(OrchestrationGraphState)

        graph.add_node("supervisor_node", self._supervisor_node)
        graph.add_node("event_agent_node", self._event_agent_node)
        graph.add_node("people_agent_node", self._people_agent_node)
        graph.add_node("matchmaker_agent_node", self._matchmaker_agent_node)
        graph.add_node("kocaeli_agent_node", self._kocaeli_agent_node)
        graph.add_node("community_agent_node", self._community_agent_node)
        graph.add_node("knowledge_agent_node", self._knowledge_agent_node)
        graph.add_node("xai_auditor_node", self._xai_auditor_node)
        graph.add_node("synthesize_node", self._synthesize_node)

        graph.add_edge(START, "supervisor_node")

        for node_name in [
            "supervisor_node",
            "event_agent_node",
            "people_agent_node",
            "matchmaker_agent_node",
            "kocaeli_agent_node",
            "community_agent_node",
            "knowledge_agent_node",
        ]:
            graph.add_conditional_edges(
                node_name,
                self._route_next_specialist,
                {
                    "event_agent": "event_agent_node",
                    "people_agent": "people_agent_node",
                    "matchmaker_agent": "matchmaker_agent_node",
                    "kocaeli_agent": "kocaeli_agent_node",
                    "community_agent": "community_agent_node",
                    "knowledge_agent": "knowledge_agent_node",
                    "xai_auditor": "xai_auditor_node",
                },
            )

        graph.add_edge("xai_auditor_node", "synthesize_node")
        graph.add_edge("synthesize_node", END)
        return graph.compile()

    def _route_next_specialist(self, state: OrchestrationGraphState) -> str:
        plan = state.get("agent_plan", [])
        idx = state.get("current_agent_idx", 0)
        if idx < len(plan):
            return plan[idx]
        return "xai_auditor"

    def _supervisor_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        t0 = time.perf_counter()
        trace_id = state["trace_id"]
        query = state["query"]
        wf_name, intents, plan = self._classify_workflow_and_plan(
            query=query,
            explicit_workflow=state.get("explicit_workflow"),
        )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        sup_step = AgentExecutionStep(
            step_id=f"step-sup-{uuid.uuid4().hex[:6]}",
            agent_id=AgentID.SUPERVISOR,
            agent_label="Supervisor Router",
            status=AgentStatus.COMPLETED,
            thought=f"Classified intent {intents} -> Workflow `{wf_name}` with specialist chain {plan}.",
            tool_calls=[
                ToolCallRecord(
                    call_id=f"tc-sup-{uuid.uuid4().hex[:6]}",
                    agent_id=AgentID.SUPERVISOR,
                    tool_name="route_stateful_workflow",
                    arguments={"workflow": wf_name, "agent_chain": plan},
                    result_summary=f"Dispatched {len(plan)} specialized agents + XAI Auditor.",
                    items_returned=len(plan),
                    duration_ms=duration_ms,
                )
            ],
            output_summary=f"Workflow: {wf_name} ({' -> '.join(plan)} -> xai_auditor)",
            confidence=0.98,
            duration_ms=duration_ms,
        )

        self._emit(
            "route_start",
            trace_id,
            f"Activated {wf_name} → Routing to {', '.join(plan)}",
            agent_id=AgentID.SUPERVISOR,
            agent_label="Supervisor Router",
            status=AgentStatus.ROUTING,
            detail={"workflow": wf_name, "plan": plan},
            duration_ms=duration_ms,
        )

        return {
            "workflow_name": wf_name,
            "detected_intents": intents,
            "agent_plan": plan,
            "current_agent_idx": 0,
            "steps": [sup_step],
            "scoring_breakdowns": [],
            "structured_payload": {},
        }

    def _emit_step_telemetry(self, trace_id: str, step: AgentExecutionStep) -> None:
        for tc in step.tool_calls:
            self._emit(
                "tool_call",
                trace_id,
                tc.result_summary,
                agent_id=step.agent_id,
                agent_label=step.agent_label,
                status=AgentStatus.CALLING_TOOL,
                detail={"tool_name": tc.tool_name, "items_returned": tc.items_returned},
                duration_ms=tc.duration_ms,
            )
        if step.rag_citations:
            top_score = max(c.relevance_score for c in step.rag_citations)
            self._emit(
                "rag_retrieval",
                trace_id,
                f"Retrieved {len(step.rag_citations)} grounded chunks",
                agent_id=step.agent_id,
                agent_label=step.agent_label,
                status=AgentStatus.RETRIEVING_RAG,
                detail={"chunk_count": len(step.rag_citations), "top_score": top_score},
                duration_ms=step.duration_ms,
            )
        self._emit(
            "agent_complete",
            trace_id,
            step.output_summary,
            agent_id=step.agent_id,
            agent_label=step.agent_label,
            status=AgentStatus.COMPLETED,
            duration_ms=step.duration_ms,
        )

    def _event_agent_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        trace_id = state["trace_id"]
        self._emit(
            "agent_start",
            trace_id,
            "Analyzing event schedule, rooms & parallel track conflicts...",
            agent_id=AgentID.EVENT_AGENT,
            agent_label="Event Agent",
            status=AgentStatus.THINKING,
        )
        with self.telemetry.span("agent.event_agent", trace_id=trace_id):
            step, bds, payload = self.event_agent.execute(
                query=state["query"],
                interests=state.get("explicit_interests"),
            )
        self._emit_step_telemetry(trace_id, step)
        merged_payload = dict(state.get("structured_payload", {}))
        merged_payload["event_agent"] = payload
        return {
            "current_agent_idx": state.get("current_agent_idx", 0) + 1,
            "steps": list(state.get("steps", [])) + [step],
            "scoring_breakdowns": list(state.get("scoring_breakdowns", [])) + bds,
            "structured_payload": merged_payload,
        }

    def _people_agent_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        trace_id = state["trace_id"]
        self._emit(
            "agent_start",
            trace_id,
            "Querying opt-in speaker, GDE, organizer & attendee directory...",
            agent_id=AgentID.PEOPLE_AGENT,
            agent_label="People Agent",
            status=AgentStatus.THINKING,
        )
        with self.telemetry.span("agent.people_agent", trace_id=trace_id):
            step, bds, payload = self.people_agent.execute(
                query=state["query"],
                interests=state.get("explicit_interests"),
            )
        self._emit_step_telemetry(trace_id, step)
        merged_payload = dict(state.get("structured_payload", {}))
        merged_payload["people_agent"] = payload
        return {
            "current_agent_idx": state.get("current_agent_idx", 0) + 1,
            "steps": list(state.get("steps", [])) + [step],
            "scoring_breakdowns": list(state.get("scoring_breakdowns", [])) + bds,
            "structured_payload": merged_payload,
        }

    def _matchmaker_agent_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        trace_id = state["trace_id"]
        self._emit(
            "agent_start",
            trace_id,
            "Scoring compatibility factors & staging consent-gated introductions...",
            agent_id=AgentID.MATCHMAKER_AGENT,
            agent_label="Matchmaker Agent",
            status=AgentStatus.THINKING,
        )
        with self.telemetry.span("agent.matchmaker_agent", trace_id=trace_id):
            step, bds, payload = self.matchmaker_agent.execute(
                query=state["query"],
                interests=state.get("explicit_interests"),
            )
        self._emit_step_telemetry(trace_id, step)
        merged_payload = dict(state.get("structured_payload", {}))
        merged_payload["matchmaker_agent"] = payload
        # Prioritize matchmaker scoring breakdowns in Workflow A
        return {
            "current_agent_idx": state.get("current_agent_idx", 0) + 1,
            "steps": list(state.get("steps", [])) + [step],
            "scoring_breakdowns": bds + list(state.get("scoring_breakdowns", [])),
            "structured_payload": merged_payload,
        }

    def _kocaeli_agent_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        trace_id = state["trace_id"]
        self._emit(
            "agent_start",
            trace_id,
            "Calculating time-constrained Kocaeli itinerary & transit buffers...",
            agent_id=AgentID.KOCAELI_AGENT,
            agent_label="Kocaeli Agent",
            status=AgentStatus.THINKING,
        )
        with self.telemetry.span("agent.kocaeli_agent", trace_id=trace_id):
            step, bds, payload = self.kocaeli_agent.execute(
                query=state["query"],
                hours=state.get("explicit_hours"),
            )
        self._emit_step_telemetry(trace_id, step)
        merged_payload = dict(state.get("structured_payload", {}))
        merged_payload["kocaeli_agent"] = payload
        return {
            "current_agent_idx": state.get("current_agent_idx", 0) + 1,
            "steps": list(state.get("steps", [])) + [step],
            "scoring_breakdowns": list(state.get("scoring_breakdowns", [])) + bds,
            "structured_payload": merged_payload,
        }

    def _community_agent_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        trace_id = state["trace_id"]
        self._emit(
            "agent_start",
            trace_id,
            "Building post-DevFest learning path & GDG Kocaeli contribution guide...",
            agent_id=AgentID.COMMUNITY_AGENT,
            agent_label="Community Agent",
            status=AgentStatus.THINKING,
        )
        with self.telemetry.span("agent.community_agent", trace_id=trace_id):
            step, bds, payload = self.community_agent.execute(
                query=state["query"],
                interests=state.get("explicit_interests"),
            )
        self._emit_step_telemetry(trace_id, step)
        merged_payload = dict(state.get("structured_payload", {}))
        merged_payload["community_agent"] = payload
        return {
            "current_agent_idx": state.get("current_agent_idx", 0) + 1,
            "steps": list(state.get("steps", [])) + [step],
            "scoring_breakdowns": list(state.get("scoring_breakdowns", [])) + bds,
            "structured_payload": merged_payload,
        }

    def _knowledge_agent_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        trace_id = state["trace_id"]
        self._emit(
            "agent_start",
            trace_id,
            "Retrieving grounded evidence chunks & source citations from Knowledge Base...",
            agent_id=AgentID.KNOWLEDGE_AGENT,
            agent_label="Knowledge Agent",
            status=AgentStatus.RETRIEVING_RAG,
        )
        with self.telemetry.span("agent.knowledge_agent", trace_id=trace_id):
            step, bds, payload = self.knowledge_agent.execute(query=state["query"], top_k=4)
        self._emit_step_telemetry(trace_id, step)
        merged_payload = dict(state.get("structured_payload", {}))
        merged_payload["knowledge_agent"] = payload
        existing_bds = list(state.get("scoring_breakdowns", []))
        return {
            "current_agent_idx": state.get("current_agent_idx", 0) + 1,
            "steps": list(state.get("steps", [])) + [step],
            "scoring_breakdowns": existing_bds if existing_bds else bds,
            "structured_payload": merged_payload,
        }

    def _xai_auditor_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        trace_id = state["trace_id"]
        steps = list(state.get("steps", []))
        bds = list(state.get("scoring_breakdowns", []))
        total_people = len(self.repo.people)
        disc_people = len(self.repo.list_discoverable_people())

        with self.telemetry.span("agent.xai_auditor", trace_id=trace_id):
            explanation, audit_step = self.xai_auditor.audit_execution(
                trace_id=trace_id,
                query=state["query"],
                workflow_type=state.get("workflow_name", "MULTI_AGENT_CONCIERGE"),
                steps=steps,
                scoring_breakdowns=bds,
                total_people_pool=total_people,
                discoverable_people_pool=disc_people,
            )

        self._emit(
            "xai_audit",
            trace_id,
            f"Decision `{explanation.decision_id}` audited (Uncertainty={explanation.uncertainty_score * 100:.1f}%, Privacy gates=PASS)",
            agent_id=AgentID.XAI_AUDITOR,
            agent_label="XAI Auditor",
            status=AgentStatus.COMPLETED,
            detail={"decision_id": explanation.decision_id},
            duration_ms=audit_step.duration_ms,
        )

        return {
            "steps": steps + [audit_step],
            "explanation": explanation,
        }

    def _synthesize_node(self, state: OrchestrationGraphState) -> dict[str, Any]:
        wf = state.get("workflow_name", "")
        payload = state.get("structured_payload", {})
        explanation = state.get("explanation")
        dec_id = explanation.decision_id if explanation else "dec-unknown"

        lines: list[str] = [
            f"> **Verification & Trust Notice:** Underlying DevFest Kocaeli 2026 records are labeled `SYNTHETIC_SAMPLE` until organizer confirmation. Recommendations below are `GENERATED_SUGGESTION` audited under Decision ID **`{dec_id}`**.\n"
        ]

        if wf == "WORKFLOW_A_MEET_THE_RIGHT_EXPERT" or "matchmaker_agent" in payload:
            matches = payload.get("matchmaker_agent", {}).get("matches", [])
            lines.append("### 🤝 Recommended Community & Expert Connections (Opt-In Only)\n")
            for idx, m in enumerate(matches, start=1):
                person = m["person"]
                factors = m["scoring_factors"]
                lines.append(
                    f"#### {idx}. {person['full_name']} — *{person['headline']}*\n"
                    f"- **Compatibility Score:** **{m['match_score'] * 100:.0f}%** "
                    f"(`interest_overlap={factors['interest_overlap']}`, `complementarity={factors['expertise_complementarity']}`, `mentorship={factors['mentorship_alignment']}`)\n"
                    f"- **Why You Should Meet:** {m['why_meet']}\n"
                    f"- **Suggested Personalized Introduction:**\n"
                    f'  > *"{m["suggested_introduction"]}"*\n'
                    f"- **🔒 Consent Gate (`{m['consent_request_id']}`):** Status is `{m['consent_status']}`. "
                    f"**Would you like to grant explicit consent to send this introduction request?** (Private contact info is never exposed.)\n"
                )

        if wf == "WORKFLOW_B_MY_DEVFEST_DAY" or (
            "event_agent" in payload and wf != "WORKFLOW_D_COMMUNITY_KNOWLEDGE"
        ):
            evt = payload.get("event_agent", {})
            agenda = evt.get("agenda", [])
            conflicts = evt.get("conflicts_resolved", [])
            lines.append("### 📅 Your Personalized Conflict-Free DevFest Kocaeli 2026 Agenda\n")
            for slot in agenda:
                lines.append(
                    f"- **`{slot['time_slot']}` — {slot['title']}** *(Relevance: {slot['score'] * 100:.0f}%)*\n"
                    f"  - **Room:** {slot['room']} | **Track:** {slot['track']} | **Speakers:** {', '.join(slot['speakers'])}\n"
                    f"  - **Why Selected:** {slot['why_selected']}"
                )
            if conflicts:
                lines.append("\n#### ⚖️ Scheduling Conflicts Automatically Resolved")
                for c in conflicts:
                    lines.append(f"- **{c['time_slot']}:** {c['resolution_reason']}")

        if wf == "WORKFLOW_C_DISCOVER_KOCAELI" or "kocaeli_agent" in payload:
            koc = payload.get("kocaeli_agent", {})
            hours = koc.get("available_hours", 3.0)
            total_min = koc.get("total_planned_minutes_with_return", 0)
            lines.append(
                f"### 🌊 Practical {hours:g}-Hour Kocaeli Discovery Itinerary (Total: {total_min} min incl. return buffer)\n"
            )
            for idx, stop in enumerate(koc.get("itinerary", []), start=1):
                lines.append(
                    f"#### Stop {idx}: {stop['name']} *({stop['category']})*\n"
                    f"- **Time Budget:** ~{stop['transit_minutes']} min transit + {stop['visit_duration_minutes']} min visit "
                    f"(Cumulative: {stop['cumulative_minutes']} min)\n"
                    f"- **Opening Hours:** {stop['opening_hours']}\n"
                    f"- **Why Visit:** {stop['summary']} {stop['cultural_context']}\n"
                    f"- **Local Tip:** *{stop['visitor_tip']}*"
                )
            skipped = koc.get("alternatives_requiring_more_time", [])
            if skipped:
                lines.append("\n#### ⏱️ Deferred for Longer Visits (Exceeds Current Time Window)")
                for s in skipped:
                    lines.append(f"- **{s['name']}:** {s['reason']}")

        if wf == "WORKFLOW_D_COMMUNITY_KNOWLEDGE" or "community_agent" in payload:
            comm = payload.get("community_agent", {})
            lines.append("### 🚀 Post-DevFest Agentic AI Learning Path & GDG Kocaeli Roadmap\n")
            for step in comm.get("pathway", []):
                talks = ", ".join(step["related_devfest_talks"]) if step["related_devfest_talks"] else "Core Track"
                lines.append(
                    f"#### Stage {step['step_number']}: {step['title']} *({step['category']} • ~{step['estimated_hours']}h)*\n"
                    f"- **What You'll Learn:** {step['summary']}\n"
                    f"- **Connected DevFest Sessions:** {talks}\n"
                    f"- **How to Contribute to GDG Kocaeli:** {step['how_to_contribute']}\n"
                    f"- **Verified Resource Link:** `{step['url']}`"
                )

        # Fallback if general knowledge query
        if len(lines) == 1 and "knowledge_agent" in payload:
            cits = payload["knowledge_agent"].get("citations", [])
            lines.append("### 📚 Grounded Knowledge Base Results\n")
            for cit in cits:
                lines.append(
                    f"- **{cit['source_title']}** (`{cit['source_id']}`, Relevance: `{cit['relevance_score']:.2f}`)\n"
                    f"  - {cit['snippet']}\n"
                    f"  - *Source:* `{cit['source_uri']}` (`{cit['verification_status']}`)"
                )

        fallback_md = PrivacyGuard.redact_pii_text("\n".join(lines))
        final_md = self.repo.model_adapter.generate_grounded_synthesis(
            prompt=f"User query: {state['query']}\nGrounded context:\n{fallback_md}",
            fallback_markdown=fallback_md,
        )
        final_md = PrivacyGuard.redact_pii_text(final_md)
        return {"final_response_markdown": final_md}

    def run_query(
        self,
        query: str,
        explicit_workflow: str | None = None,
        explicit_interests: list[str] | None = None,
        explicit_hours: float | None = None,
        event_callback: EventCallback | None = None,
    ) -> TraceRecord:
        """Execute the full stateful LangGraph multi-agent workflow and persist trace + XAI audit."""
        t0 = time.perf_counter()
        trace_id = f"trc-{uuid.uuid4().hex[:8]}"
        query = PrivacyGuard.sanitize_user_query(query)
        self._active_callback = event_callback

        try:
            with self.telemetry.span("orchestrator.run_query", trace_id=trace_id, query=query):
                initial_state: OrchestrationGraphState = {
                    "trace_id": trace_id,
                    "query": query,
                    "explicit_workflow": explicit_workflow,
                    "explicit_interests": explicit_interests,
                    "explicit_hours": explicit_hours,
                }
                final_state: OrchestrationGraphState = self.compiled_graph.invoke(initial_state)
        finally:
            self._active_callback = None

        total_ms = round((time.perf_counter() - t0) * 1000, 2)
        explanation = final_state.get("explanation")
        decision_id = explanation.decision_id if explanation else f"dec-{uuid.uuid4().hex[:8]}"

        trace_record = TraceRecord(
            trace_id=trace_id,
            decision_id=decision_id,
            event_id=self.repo.edition_config.event_id,
            query=query,
            detected_intents=final_state.get("detected_intents", []),
            workflow_name=final_state.get("workflow_name", "MULTI_AGENT_CONCIERGE"),
            execution_mode=self.repo.settings.mode,
            orchestrator_engine=f"LangGraph StateGraph + {self.repo.model_adapter.backend_name}",
            steps=final_state.get("steps", []),
            total_duration_ms=total_ms,
            final_response_markdown=final_state.get("final_response_markdown", ""),
            structured_payload=final_state.get("structured_payload", {}),
            explanation=explanation,
            otel_trace_id=self.telemetry.latest_otel_trace_id(),
        )
        self.repo.save_trace_and_decision(trace_record)
        return trace_record


_orchestrator: PismaniyeOrchestrator | None = None


def get_orchestrator() -> PismaniyeOrchestrator:
    global _orchestrator
    current_repo = get_repository()
    if _orchestrator is None or _orchestrator.repo is not current_repo:
        _orchestrator = PismaniyeOrchestrator(current_repo)
    return _orchestrator
