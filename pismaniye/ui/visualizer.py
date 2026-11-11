"""Live terminal execution graph, RAG visualization, trace tree, and XAI audit renderer."""

from __future__ import annotations

from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from pismaniye.schemas.agent import DecisionExplanation, LiveOrchestrationEvent, TraceRecord
from pismaniye.ui.theme import (
    AGENT_VISUAL_META,
    CYAN_ACCENT,
    GOOGLE_BLUE,
    GOOGLE_GREEN,
    GOOGLE_RED,
    GOOGLE_YELLOW,
    MUTED_SLATE,
    PISMANIYE_GOLD,
    PISMANIYE_SILK,
    PURPLE_ACCENT,
    format_verification_badge,
    render_thread_divider,
)


def build_live_orchestration_panel(
    query: str,
    events: list[LiveOrchestrationEvent],
    active_agent: str | None = None,
) -> Panel:
    """Build a live Rich Panel visualizing real backend orchestration events as they happen."""
    tree = Tree(
        f"[bold {PISMANIYE_GOLD}]◈ LangGraph + ADK Stateful Execution Graph[/bold {PISMANIYE_GOLD}] "
        f"[{MUTED_SLATE}](Query: {query!r})[/{MUTED_SLATE}]"
    )

    agent_nodes: dict[str, Tree] = {}
    for ev in events:
        ag_key = ev.agent_id.value if ev.agent_id else "supervisor"
        meta = AGENT_VISUAL_META.get(ag_key, AGENT_VISUAL_META["supervisor"])
        color = meta["color"]
        icon = meta["icon"]
        label = meta["name"]

        if ev.event_type == "route_start":
            node = tree.add(
                f"[{color} bold]{icon} {label}[/{color} bold] → [italic]{ev.message}[/italic]"
            )
            agent_nodes[ag_key] = node
        elif ev.event_type == "agent_start":
            node = tree.add(
                f"[{color} bold]{icon} {label}[/{color} bold] [{GOOGLE_YELLOW}]⚡ ACTIVE[/{GOOGLE_YELLOW}] — {ev.message}"
            )
            agent_nodes[ag_key] = node
        elif ev.event_type == "tool_call":
            parent = agent_nodes.get(ag_key, tree)
            tool_name = ev.detail.get("tool_name", "tool")
            items = ev.detail.get("items_returned", 0)
            parent.add(
                f"[{CYAN_ACCENT}]⚙ Tool:[/{CYAN_ACCENT}] [bold]{tool_name}[/bold] "
                f"→ {ev.message} [{MUTED_SLATE}]({items} records, {ev.duration_ms:.1f} ms)[/{MUTED_SLATE}]"
            )
        elif ev.event_type == "rag_retrieval":
            parent = agent_nodes.get(ag_key, tree)
            top_score = ev.detail.get("top_score", 0.0)
            chunks = ev.detail.get("chunk_count", 0)
            parent.add(
                f"[{GOOGLE_YELLOW}]📚 Hybrid RAG:[/{GOOGLE_YELLOW}] Retrieved [bold]{chunks}[/bold] grounded chunks "
                f"(top relevance={top_score:.2f}, {ev.duration_ms:.1f} ms)"
            )
        elif ev.event_type == "agent_complete":
            parent = agent_nodes.get(ag_key, tree)
            parent.add(
                f"[{GOOGLE_GREEN}]✔ Completed[/{GOOGLE_GREEN}] in [bold]{ev.duration_ms:.1f} ms[/bold] — {ev.message}"
            )
        elif ev.event_type == "xai_audit":
            node = tree.add(
                f"[bold bright_white]⚖ XAI Auditor[/bold bright_white] — {ev.message} "
                f"[{GOOGLE_GREEN}]({ev.duration_ms:.1f} ms)[/{GOOGLE_GREEN}]"
            )
            agent_nodes["xai_auditor"] = node

    status_line = (
        f"[bold {GOOGLE_YELLOW}]⟳ Executing: {active_agent}[/bold {GOOGLE_YELLOW}]"
        if active_agent
        else f"[bold {GOOGLE_GREEN}]✔ Execution Graph Complete[/bold {GOOGLE_GREEN}]"
    )
    return Panel(
        Group(tree, Text(""), Text.from_markup(status_line)),
        title=f"[bold {GOOGLE_BLUE}]Live Agent Orchestration Telemetry[/bold {GOOGLE_BLUE}]",
        border_style=GOOGLE_BLUE,
    )


def render_trace_summary(console: Console, trace: TraceRecord) -> None:
    """Render full execution trace, RAG evidence table, and response markdown."""
    # 1. Execution Steps & Tool Calls
    step_table = Table(
        title=f"[bold {PISMANIYE_SILK}]Execution Trace • ID: [bold {GOOGLE_YELLOW}]{trace.trace_id}[/bold {GOOGLE_YELLOW}] • Decision ID: [bold {CYAN_ACCENT}]{trace.decision_id}[/bold {CYAN_ACCENT}][/bold {PISMANIYE_SILK}]",
        border_style=GOOGLE_BLUE,
        expand=True,
    )
    step_table.add_column("#", width=3, justify="right")
    step_table.add_column("Agent", width=22)
    step_table.add_column("Status", width=12)
    step_table.add_column("Tools & RAG Invocations", style=f"{PISMANIYE_SILK}")
    step_table.add_column("Confidence", width=10, justify="right")
    step_table.add_column("Duration", width=10, justify="right", style=f"bold {GOOGLE_GREEN}")

    all_citations = []
    for idx, step in enumerate(trace.steps, start=1):
        meta = AGENT_VISUAL_META.get(step.agent_id.value, AGENT_VISUAL_META["supervisor"])
        color = meta["color"]
        tools_desc = []
        for tc in step.tool_calls:
            tools_desc.append(f"[{CYAN_ACCENT}]⚙ {tc.tool_name}[/{CYAN_ACCENT}] ({tc.items_returned} items)")
        if step.rag_citations:
            tools_desc.append(f"[{GOOGLE_YELLOW}]📚 RAG: {len(step.rag_citations)} chunks[/{GOOGLE_YELLOW}]")
            all_citations.extend(step.rag_citations)
        if not tools_desc:
            tools_desc.append(step.output_summary or step.thought)

        step_table.add_row(
            str(idx),
            f"[{color} bold]{meta['icon']} {step.agent_label}[/{color} bold]",
            f"[{GOOGLE_GREEN}]{step.status.value}[/{GOOGLE_GREEN}]",
            " • ".join(tools_desc),
            f"{step.confidence * 100:.0f}%",
            f"{step.duration_ms:.1f} ms",
        )

    console.print(step_table)

    # 2. RAG Retrieval Visualization if citations exist
    if all_citations:
        rag_table = Table(
            title=f"[bold {GOOGLE_YELLOW}]📚 Grounded RAG Retrieval & Source Verification[/bold {GOOGLE_YELLOW}]",
            border_style=GOOGLE_YELLOW,
            expand=True,
        )
        rag_table.add_column("Source ID", width=18, style=f"bold {CYAN_ACCENT}")
        rag_table.add_column("Document Title", width=28, style=f"bold {PISMANIYE_SILK}")
        rag_table.add_column("Relevance Bar", width=18)
        rag_table.add_column("Verification Badge", width=26)

        seen_ids: set[str] = set()
        for cit in all_citations:
            if cit.source_id in seen_ids:
                continue
            seen_ids.add(cit.source_id)
            filled = int(round(cit.relevance_score * 10))
            bar = f"[{GOOGLE_GREEN}]{'█' * filled}[/{GOOGLE_GREEN}][{MUTED_SLATE}]{'░' * (10 - filled)}[/{MUTED_SLATE}] {cit.relevance_score:.2f}"
            rag_table.add_row(
                cit.source_id,
                cit.source_title,
                bar,
                format_verification_badge(cit.verification_status.value),
            )
        console.print(rag_table)

    # 3. Final Response Panel
    console.print(
        Panel(
            Markdown(trace.final_response_markdown),
            title=(
                f"[bold {GOOGLE_GREEN}]✦ Pismaniye Synthesized Response[/bold {GOOGLE_GREEN}] "
                f"[{MUTED_SLATE}](Workflow: {trace.workflow_name} | Total: {trace.total_duration_ms:.1f} ms)[/{MUTED_SLATE}]"
            ),
            subtitle=(
                f"[{MUTED_SLATE}]Inspect trace: [bold]pismaniye trace {trace.trace_id}[/bold] • "
                f"XAI explain: [bold]pismaniye explain {trace.decision_id}[/bold][/{MUTED_SLATE}]"
            ),
            border_style=GOOGLE_GREEN,
            padding=(1, 2),
        )
    )


def render_decision_explanation(console: Console, explanation: DecisionExplanation) -> None:
    """Render deep XAI audit view for `pismaniye explain <decision_id>`."""
    header = Table.grid(padding=(0, 3))
    header.add_column()
    header.add_column()
    header.add_row(
        f"[bold {PISMANIYE_GOLD}]Decision ID:[/bold {PISMANIYE_GOLD}] {explanation.decision_id}",
        f"[bold {CYAN_ACCENT}]Linked Trace ID:[/bold {CYAN_ACCENT}] {explanation.trace_id}",
    )
    header.add_row(
        f"[bold {GOOGLE_BLUE}]Workflow:[/bold {GOOGLE_BLUE}] {explanation.workflow_type}",
        f"[bold {GOOGLE_YELLOW}]Epistemic Uncertainty:[/bold {GOOGLE_YELLOW}] {explanation.uncertainty_score * 100:.1f}%",
    )

    console.print(
        Panel(
            header,
            title="[bold bright_white]⚖ XAI DECISION AUDIT & PROVENANCE INSPECTOR[/bold bright_white]",
            border_style=PURPLE_ACCENT,
        )
    )

    if explanation.scoring_breakdowns:
        score_tbl = Table(
            title=f"[bold {PURPLE_ACCENT}]Transparent Multi-Factor Scoring Breakdown[/bold {PURPLE_ACCENT}]",
            border_style=PURPLE_ACCENT,
            expand=True,
        )
        score_tbl.add_column("Candidate / Item", width=26, style=f"bold {PISMANIYE_SILK}")
        score_tbl.add_column("Composite Score", width=14, justify="right", style=f"bold {GOOGLE_GREEN}")
        score_tbl.add_column("Factor Breakdown", width=34)
        score_tbl.add_column("Explainable Rationale", style=f"{PISMANIYE_SILK}")

        for sb in explanation.scoring_breakdowns:
            factors_str = ", ".join(f"{k}={v:.2f}" for k, v in sb.factors.items())
            score_tbl.add_row(
                sb.item_name,
                f"{sb.total_score * 100:.1f}%",
                factors_str,
                sb.rationale,
            )
        console.print(score_tbl)

    # Provenance & Privacy Checks
    prov_tree = Tree(f"[bold {GOOGLE_BLUE}]◈ Decision Provenance Chain[/bold {GOOGLE_BLUE}]")
    for item in explanation.provenance_chain:
        prov_tree.add(f"[{PISMANIYE_SILK}]{item}[/{PISMANIYE_SILK}]")

    priv_tree = Tree(f"[bold {GOOGLE_GREEN}]🛡 Privacy, Safety & Verification Guardrails[/bold {GOOGLE_GREEN}]")
    for check in explanation.privacy_checks_passed:
        priv_tree.add(f"[{GOOGLE_GREEN}]✔[/{GOOGLE_GREEN}] {check}")
    for note in explanation.uncertainty_notes:
        priv_tree.add(f"[{GOOGLE_YELLOW}]ℹ Uncertainty Note:[/{GOOGLE_YELLOW}] {note}")
    priv_tree.add(f"[{CYAN_ACCENT}]ℹ {explanation.verified_vs_generated_note}[/{CYAN_ACCENT}]")

    console.print(Panel(Group(prov_tree, Text(""), priv_tree), border_style=GOOGLE_GREEN))
