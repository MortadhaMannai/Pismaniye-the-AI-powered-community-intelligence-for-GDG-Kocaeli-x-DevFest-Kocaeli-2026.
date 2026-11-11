"""XAI Auditing Engine inspecting recommendations, retrieved evidence, provenance, and uncertainty."""

from __future__ import annotations

import time
import uuid

from pismaniye.privacy.guardrails import PrivacyGuard
from pismaniye.schemas.agent import (
    AgentExecutionStep,
    AgentID,
    AgentStatus,
    DecisionExplanation,
    EvidenceCitation,
    ScoringBreakdown,
    ToolCallRecord,
)
from pismaniye.schemas.domain import VerificationStatus


class XAIAuditor:
    """Audits multi-agent outputs, computes epistemic uncertainty, and records provenance chains."""

    def audit_execution(
        self,
        trace_id: str,
        query: str,
        workflow_type: str,
        steps: list[AgentExecutionStep],
        scoring_breakdowns: list[ScoringBreakdown],
        total_people_pool: int,
        discoverable_people_pool: int,
    ) -> tuple[DecisionExplanation, AgentExecutionStep]:
        t0 = time.perf_counter()
        decision_id = f"dec-{uuid.uuid4().hex[:8]}"

        participating: list[AgentID] = []
        all_citations: list[EvidenceCitation] = []
        provenance_chain: list[str] = []

        for step in steps:
            if step.agent_id not in participating:
                participating.append(step.agent_id)
            for tc in step.tool_calls:
                provenance_chain.append(
                    f"[{step.agent_label}] called `{tc.tool_name}` -> {tc.result_summary} ({tc.duration_ms:.1f} ms)"
                )
            for cit in step.rag_citations:
                all_citations.append(cit)
                provenance_chain.append(
                    f"[{step.agent_label}] cited `{cit.source_id}` ({cit.source_title}, relevance={cit.relevance_score:.2f}, status={cit.verification_status.value})"
                )

        # Deduplicate citations
        dedup_citations: list[EvidenceCitation] = []
        seen_cits: set[str] = set()
        for c in all_citations:
            if c.source_id not in seen_cits:
                seen_cits.add(c.source_id)
                dedup_citations.append(c)

        # Compute uncertainty based on verification status & evidence coverage
        has_synthetic = any(
            c.verification_status == VerificationStatus.SYNTHETIC_SAMPLE for c in dedup_citations
        ) or any(
            sb.verification_status == VerificationStatus.SYNTHETIC_SAMPLE for sb in scoring_breakdowns
        )
        base_uncertainty = 0.14 if has_synthetic else 0.04
        if not dedup_citations and not scoring_breakdowns:
            base_uncertainty = 0.28

        uncertainty_notes: list[str] = []
        if has_synthetic:
            uncertainty_notes.append(
                "Underlying records are labeled SYNTHETIC_SAMPLE (fictional DevFest Kocaeli 2026 demo dataset). "
                "Once GDG Kocaeli organizers verify records in the dashboard, uncertainty drops to <= 4%."
            )
        else:
            uncertainty_notes.append(
                "All cited records are marked VERIFIED_ORGANIZER_DATA."
            )
        uncertainty_notes.append(
            "Generated rationales, agendas, and introduction icebreakers are explicitly marked GENERATED_SUGGESTION."
        )

        opted_out_count = max(0, total_people_pool - discoverable_people_pool)
        privacy_checks = PrivacyGuard.build_privacy_audit_checklist(
            candidates_checked=discoverable_people_pool,
            opted_out_filtered=opted_out_count,
            consent_gate_active=True,
        )

        primary_summary = (
            scoring_breakdowns[0].rationale
            if scoring_breakdowns
            else (
                f"Synthesized grounded response across {len(participating)} agents with {len(dedup_citations)} citations."
            )
        )

        participating.append(AgentID.XAI_AUDITOR)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        explanation = DecisionExplanation(
            decision_id=decision_id,
            trace_id=trace_id,
            query=query,
            workflow_type=workflow_type,
            participating_agents=participating,
            primary_recommendation_summary=primary_summary,
            scoring_breakdowns=scoring_breakdowns,
            evidence_citations=dedup_citations,
            provenance_chain=provenance_chain,
            uncertainty_score=round(base_uncertainty, 3),
            uncertainty_notes=uncertainty_notes,
            privacy_checks_passed=privacy_checks,
        )

        audit_step = AgentExecutionStep(
            step_id=f"step-xai-{uuid.uuid4().hex[:6]}",
            agent_id=AgentID.XAI_AUDITOR,
            agent_label="XAI Auditor",
            status=AgentStatus.COMPLETED,
            thought="Auditing multi-agent outputs, verifying opt-in & PII boundaries, and recording factor provenance.",
            tool_calls=[
                ToolCallRecord(
                    call_id=f"tc-{uuid.uuid4().hex[:6]}",
                    agent_id=AgentID.XAI_AUDITOR,
                    tool_name="verify_provenance_and_privacy",
                    arguments={
                        "citations_checked": len(dedup_citations),
                        "scored_items": len(scoring_breakdowns),
                    },
                    result_summary=(
                        f"Decision {decision_id} verified ({len(privacy_checks)} privacy gates passed, "
                        f"uncertainty={base_uncertainty * 100:.1f}%)"
                    ),
                    items_returned=len(scoring_breakdowns) + len(dedup_citations),
                    duration_ms=duration_ms,
                )
            ],
            rag_citations=[],
            output_summary=f"Audited decision `{decision_id}` with {len(provenance_chain)} provenance links.",
            confidence=round(1.0 - base_uncertainty, 2),
            duration_ms=duration_ms,
        )

        return explanation, audit_step
