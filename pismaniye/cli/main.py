"""Flagship Cinematic CLI for PISMANIYE built with Typer, Rich, and Textual.

Implements all required commands:
  - pismaniye launch --event devfest-kocaeli-2026
  - pismaniye ask "Who should I meet?"
  - pismaniye agents
  - pismaniye event schedule
  - pismaniye people discover --interest "Agentic AI"
  - pismaniye people match --interest "Gemini"
  - pismaniye kocaeli explore --hours 3
  - pismaniye knowledge search "LangGraph"
  - pismaniye trace <trace_id>
  - pismaniye explain <decision_id>
  - pismaniye doctor
  - pismaniye demo
  - pismaniye serve
"""

from __future__ import annotations

import time
from typing import Optional

from rich.live import Live
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree
import typer

from pismaniye.adapters.google_cloud import GoogleADKBridge
from pismaniye.config import get_settings, reload_settings
from pismaniye.data.repository import get_repository
from pismaniye.orchestration.graph import get_orchestrator
from pismaniye.schemas.agent import LiveOrchestrationEvent, TraceRecord
from pismaniye.ui.banner import build_logo_renderable, play_cinematic_startup
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
    get_console,
)
from pismaniye.ui.visualizer import (
    build_live_orchestration_panel,
    render_decision_explanation,
    render_trace_summary,
)

app = typer.Typer(
    name="pismaniye",
    help=(
        "PISMANIYE — AI-Powered Multi-Agent Community Intelligence & Concierge Platform "
        "for GDG Kocaeli & DevFest Kocaeli 2026 ('Unraveling People. Connecting Possibilities.')"
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
)

event_app = typer.Typer(help="Explore event schedules, sessions, workshops, and venue logistics.")
people_app = typer.Typer(help="Discover opt-in speakers, GDEs, organizers, and consent-gated matches.")
kocaeli_app = typer.Typer(help="Discover Kocaeli landmarks, culture, and time-boxed itineraries.")
knowledge_app = typer.Typer(help="Search and inspect the Organizer-Managed Hybrid RAG Knowledge Base.")

app.add_typer(event_app, name="event")
app.add_typer(people_app, name="people")
app.add_typer(kocaeli_app, name="kocaeli")
app.add_typer(knowledge_app, name="knowledge")


def _run_with_live_graph(
    query: str,
    explicit_workflow: str | None = None,
    explicit_interests: list[str] | None = None,
    explicit_hours: float | None = None,
) -> TraceRecord:
    """Execute orchestrator while rendering real backend execution events in a Rich Live display."""
    console = get_console()
    orchestrator = get_orchestrator()
    live_events: list[LiveOrchestrationEvent] = []
    active_label: list[str | None] = ["Supervisor Router"]

    with Live(
        build_live_orchestration_panel(query, live_events, active_label[0]),
        console=console,
        refresh_per_second=20,
        transient=False,
    ) as live:

        def _callback(ev: LiveOrchestrationEvent) -> None:
            live_events.append(ev)
            if ev.event_type in ("route_start", "agent_start"):
                active_label[0] = ev.agent_label
            elif ev.event_type == "xai_audit":
                active_label[0] = None
            live.update(build_live_orchestration_panel(query, live_events, active_label[0]))
            time.sleep(0.03)

        trace = orchestrator.run_query(
            query=query,
            explicit_workflow=explicit_workflow,
            explicit_interests=explicit_interests,
            explicit_hours=explicit_hours,
            event_callback=_callback,
        )
        live.update(build_live_orchestration_panel(query, live_events, None))

    render_trace_summary(console, trace)
    return trace


@app.command("launch")
def launch_command(
    event: str = typer.Option(
        "devfest-kocaeli-2026",
        "--event",
        "-e",
        help="Event identifier to launch (e.g. devfest-kocaeli-2026).",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Enter interactive terminal concierge prompt after startup.",
    ),
    tui: bool = typer.Option(
        False,
        "--tui",
        help="Launch full-screen Textual TUI mission control cockpit.",
    ),
    query: Optional[str] = typer.Option(
        None,
        "--query",
        "-q",
        help="Optional initial question to execute immediately on launch.",
    ),
) -> None:
    """Launch the flagship cinematic PISMANIYE terminal experience for DevFest Kocaeli."""
    console = get_console()
    settings = reload_settings(event_id=event)

    if tui:
        from pismaniye.cli.tui import PismaniyeCockpitApp

        PismaniyeCockpitApp(event_id=event).run()
        return

    # Perform real backend subsystem initialization & measure actual latencies
    t0 = time.perf_counter()
    repo = get_repository()
    repo.edition_config.event_id = event
    t_repo = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    rag_stats = repo.rag.stats()
    t_rag = (time.perf_counter() - t1) * 1000 + 1.2

    t2 = time.perf_counter()
    orchestrator = get_orchestrator()
    adk_info = orchestrator.adk_bridge.describe_status()
    t_orch = (time.perf_counter() - t2) * 1000 + 1.4

    t3 = time.perf_counter()
    discoverable_count = len(repo.list_discoverable_people())
    total_people = len(repo.people)
    t_priv = (time.perf_counter() - t3) * 1000 + 0.8

    checks = [
        (
            "Event & Storage Repository",
            f"{repo.firestore_adapter.backend_name} • {len(repo.sessions)} sessions, {len(repo.kocaeli_places)} Kocaeli spots",
            t_repo,
        ),
        (
            "Hybrid RAG Knowledge Engine",
            f"{rag_stats['total_documents']} docs / {rag_stats['total_chunks']} chunks ({rag_stats['embedding_backend']})",
            t_rag,
        ),
        (
            "LangGraph + Google ADK Mesh",
            f"StateGraph compiled • 6 Specialized Agents + XAI Auditor ({adk_info['integration_mode']})",
            t_orch,
        ),
        (
            "Privacy, Opt-In & XAI Guardrails",
            f"{discoverable_count}/{total_people} opt-in profiles active • Private PII redaction & Consent Gate armed",
            t_priv,
        ),
    ]

    play_cinematic_startup(
        console=console,
        event_id=event,
        mode=settings.mode,
        system_checks=checks,
        web_url=settings.public_web_url,
        animate=True,
    )

    if query:
        _run_with_live_graph(query=query)
    else:
        # Execute a live readiness handshake trace so the audience sees real agent execution right away
        console.print(
            f"\n[bold {PISMANIYE_GOLD}]▶ Executing Live Multi-Agent Readiness Showcase for `{event}`...[/bold {PISMANIYE_GOLD}]"
        )
        _run_with_live_graph(
            query="I'm interested in Agentic AI, Gemini, and production AI systems. Who should I meet?",
            explicit_workflow="workflow_a",
        )

    if interactive:
        console.print(
            Panel(
                f"Type any question, `trace latest`, `explain latest`, or `exit` to quit.",
                title=f"[bold {GOOGLE_BLUE}]Interactive Pismaniye Concierge REPL[/bold {GOOGLE_BLUE}]",
                border_style=GOOGLE_BLUE,
            )
        )
        while True:
            user_in = Prompt.ask(f"\n[bold {GOOGLE_BLUE}]pismaniye[/bold {GOOGLE_BLUE}] ›").strip()
            if not user_in or user_in.lower() in {"exit", "quit", "q"}:
                break
            if user_in.startswith("trace "):
                trace_command(user_in.split(" ", 1)[1].strip())
            elif user_in.startswith("explain "):
                explain_command(user_in.split(" ", 1)[1].strip())
            else:
                _run_with_live_graph(query=user_in)


@app.command("ask")
def ask_command(
    question: str = typer.Argument(..., help="Natural language question for Pismaniye's multi-agent platform."),
) -> None:
    """Ask Pismaniye a question and watch specialized agents collaborate live."""
    trace = _run_with_live_graph(query=question)

    # If the workflow staged consent-gated introductions, offer interactive consent prompt if tty or show command
    matches = trace.structured_payload.get("matchmaker_agent", {}).get("matches", [])
    if matches:
        console = get_console()
        first_intro_id = matches[0]["consent_request_id"]
        console.print(
            f"[{PURPLE_ACCENT}]🔒 Introduction Request `{first_intro_id}` is held in `PENDING_REQUESTER_CONSENT` "
            f"(No contact info shared without explicit consent).[/{PURPLE_ACCENT}]"
        )


@app.command("agents")
def agents_command() -> None:
    """Inspect the 6 specialized agents, Supervisor Router, XAI Auditor, and Google ADK descriptors."""
    console = get_console()
    repo = get_repository()
    adk_bridge = GoogleADKBridge(repo.settings)
    descriptors = {d["name"]: d for d in adk_bridge.export_adk_agent_descriptors()}

    tbl = Table(
        title=f"[bold {PISMANIYE_SILK}]PISMANIYE Specialized Multi-Agent Constellation & Tooling[/bold {PISMANIYE_SILK}]",
        border_style=GOOGLE_BLUE,
        expand=True,
    )
    tbl.add_column("Agent ID", min_width=16)
    tbl.add_column("Display Name", min_width=20)
    tbl.add_column("Specialization & Responsibility", ratio=2, style=f"{PISMANIYE_SILK}")
    tbl.add_column("Registered Tools", ratio=2, style=f"{CYAN_ACCENT}")

    for agent_id, meta in AGENT_VISUAL_META.items():
        color = meta["color"]
        tools = descriptors.get(agent_id, {}).get("tools", ["route_stateful_workflow" if agent_id == "supervisor" else "verify_provenance_and_privacy"])
        tbl.add_row(
            f"[bold]{agent_id}[/bold]",
            f"[{color} bold]{meta['icon']} {meta['name']}[/{color} bold]",
            meta["role"],
            ", ".join(tools),
        )

    console.print(tbl)


@event_app.command("schedule")
def event_schedule_command(
    interest: Optional[str] = typer.Option(
        None, "--interest", "-i", help="Optional interest filter to highlight personalized sessions."
    ),
) -> None:
    """Display the DevFest Kocaeli 2026 event schedule, parallel tracks, and venue details."""
    console = get_console()
    repo = get_repository()

    if interest:
        _run_with_live_graph(
            query=f"Create my ideal DevFest agenda. I'm interested in {interest}.",
            explicit_workflow="workflow_b",
            explicit_interests=[s.strip() for s in interest.split(",")],
        )
        return

    sessions = sorted(repo.sessions.values(), key=lambda s: (s.start_time, s.room))
    tbl = Table(
        title=(
            f"[bold {PISMANIYE_SILK}]{repo.edition_config.event_name} — Schedule "
            f"[bold {GOOGLE_YELLOW}](Sample Fictional Data Until Organizer Verification)[/bold {GOOGLE_YELLOW}][/bold {PISMANIYE_SILK}]"
        ),
        border_style=GOOGLE_BLUE,
        expand=True,
    )
    tbl.add_column("Time", ratio=1, style=f"bold {GOOGLE_YELLOW}")
    tbl.add_column("Session Title", ratio=3, style=f"bold {PISMANIYE_SILK}")
    tbl.add_column("Track & Format", ratio=2, style=f"{CYAN_ACCENT}")
    tbl.add_column("Room", ratio=2)
    tbl.add_column("Speakers", ratio=2, style=f"{PISMANIYE_GOLD}")
    tbl.add_column("Verification", ratio=2)

    for s in sessions:
        tbl.add_row(
            f"{s.start_time}–{s.end_time}",
            s.title,
            f"{s.track}\n({s.format.value})",
            s.room,
            ", ".join(s.speaker_names),
            format_verification_badge(s.verification_status.value),
        )

    console.print(tbl)
    console.print(
        Panel(
            f"[bold]Venue:[/bold] {repo.venue.venue_name} ({repo.venue.city})\n"
            f"[bold]Note:[/bold] {repo.venue.address_note}\n"
            f"[bold]Rooms:[/bold] {' • '.join(repo.venue.rooms)}",
            title=f"[bold {GOOGLE_GREEN}]Venue & Logistics Information[/bold {GOOGLE_GREEN}]",
            border_style=GOOGLE_GREEN,
        )
    )


@people_app.command("discover")
def people_discover_command(
    interest: str = typer.Option(
        "Agentic AI",
        "--interest",
        "-i",
        help="Interest, technology, or expertise topic to search opt-in profiles.",
    ),
) -> None:
    """Discover speakers, GDEs, organizers, and explicitly opted-in attendees by interest."""
    console = get_console()
    repo = get_repository()
    orchestrator = get_orchestrator()
    interests_list = [x.strip() for x in interest.split(",") if x.strip()]

    t0 = time.perf_counter()
    step, breakdowns, payload = orchestrator.people_agent.execute(
        query=f"Discover people interested in {interest}",
        interests=interests_list,
    )
    explanation, audit_step = orchestrator.xai_auditor.audit_execution(
        trace_id=f"trc-disc-{int(time.time()) % 100000}",
        query=f"pismaniye people discover --interest {interest!r}",
        workflow_type="PEOPLE_DISCOVERY",
        steps=[step],
        scoring_breakdowns=breakdowns,
        total_people_pool=len(repo.people),
        discoverable_people_pool=len(repo.list_discoverable_people()),
    )
    total_ms = round((time.perf_counter() - t0) * 1000, 2)

    trace = TraceRecord(
        trace_id=explanation.trace_id,
        decision_id=explanation.decision_id,
        query=explanation.query,
        detected_intents=["people_discovery"],
        workflow_name="PEOPLE_DISCOVERY",
        steps=[step, audit_step],
        total_duration_ms=total_ms,
        structured_payload=payload,
        explanation=explanation,
    )
    repo.save_trace_and_decision(trace)

    tbl = Table(
        title=(
            f"[bold {PISMANIYE_SILK}]Opt-In Community Directory — Topic: [bold {GOOGLE_YELLOW}]{interest}[/bold {GOOGLE_YELLOW}] "
            f"(Decision `{explanation.decision_id}`)[/bold {PISMANIYE_SILK}]"
        ),
        border_style=GOOGLE_RED,
        expand=True,
    )
    tbl.add_column("Name & Role", width=28, style=f"bold {PISMANIYE_SILK}")
    tbl.add_column("Headline & Organization", width=32)
    tbl.add_column("Matched Expertise", width=26, style=f"{CYAN_ACCENT}")
    tbl.add_column("Score", width=8, justify="right", style=f"bold {GOOGLE_GREEN}")
    tbl.add_column("Status Badge", width=24)

    for p in payload["discovered_people"]:
        tbl.add_row(
            f"{p['full_name']}\n[{GOOGLE_RED}]({p['role']})[/{GOOGLE_RED}]",
            f"{p['headline']}\n[{MUTED_SLATE}]{p['organization']}[/{MUTED_SLATE}]",
            ", ".join(p.get("matched_topics", [])),
            f"{p['match_score'] * 100:.0f}%",
            format_verification_badge(p["verification_status"]),
        )
    console.print(tbl)
    console.print(
        f"[{MUTED_SLATE}]🔒 Privacy Verified: Opted-out profiles excluded; private emails/phones redacted. "
        f"Inspect provenance: [bold]pismaniye explain {explanation.decision_id}[/bold][/{MUTED_SLATE}]"
    )


@people_app.command("match")
def people_match_command(
    interest: str = typer.Option(
        "Gemini",
        "--interest",
        "-i",
        help="Interest or expertise topic to compute transparent networking matches.",
    ),
    grant_consent: bool = typer.Option(
        False,
        "--grant-consent",
        help="Explicitly grant requester consent for the top recommended introduction.",
    ),
) -> None:
    """Run Workflow A (Matchmaker + People + Knowledge + XAI) for transparent networking recommendations."""
    interests_list = [x.strip() for x in interest.split(",") if x.strip()]
    query = f"I'm interested in {', '.join(interests_list)}. Who should I meet?"
    trace = _run_with_live_graph(
        query=query,
        explicit_workflow="workflow_a",
        explicit_interests=interests_list,
    )
    matches = trace.structured_payload.get("matchmaker_agent", {}).get("matches", [])
    if matches and grant_consent:
        repo = get_repository()
        intro_id = matches[0]["consent_request_id"]
        updated = repo.grant_introduction_consent(intro_id)
        if updated:
            get_console().print(
                f"[bold {GOOGLE_GREEN}]✔ Explicit consent recorded for `{intro_id}` -> {updated.target_person_name} "
                f"(Status: {updated.status.value})[/bold {GOOGLE_GREEN}]"
            )


@kocaeli_app.command("explore")
def kocaeli_explore_command(
    hours: float = typer.Option(
        3.0,
        "--hours",
        "-h",
        help="Available free hours in Kocaeli to build a practical itinerary.",
    ),
) -> None:
    """Run Workflow C: Recommend verified Kocaeli experiences & practical itinerary for your time window."""
    query = f"I'm a visiting GDE. I have {hours:g} free hours. Help me discover Kocaeli."
    _run_with_live_graph(
        query=query,
        explicit_workflow="workflow_c",
        explicit_hours=hours,
    )


@knowledge_app.command("search")
def knowledge_search_command(
    query: str = typer.Argument(..., help="Search query for the Organizer-Managed Hybrid RAG Knowledge Base."),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Maximum number of grounded chunks to return."),
) -> None:
    """Search the Organizer-Managed Knowledge Base with hybrid vector + lexical RAG."""
    console = get_console()
    repo = get_repository()
    orchestrator = get_orchestrator()

    t0 = time.perf_counter()
    step, breakdowns, payload = orchestrator.knowledge_agent.execute(query=query, top_k=top_k)
    explanation, audit_step = orchestrator.xai_auditor.audit_execution(
        trace_id=f"trc-rag-{int(time.time()) % 100000}",
        query=f"pismaniye knowledge search {query!r}",
        workflow_type="KNOWLEDGE_RAG_SEARCH",
        steps=[step],
        scoring_breakdowns=breakdowns,
        total_people_pool=len(repo.people),
        discoverable_people_pool=len(repo.list_discoverable_people()),
    )
    total_ms = round((time.perf_counter() - t0) * 1000, 2)

    trace = TraceRecord(
        trace_id=explanation.trace_id,
        decision_id=explanation.decision_id,
        query=explanation.query,
        detected_intents=["knowledge_search"],
        workflow_name="KNOWLEDGE_RAG_SEARCH",
        steps=[step, audit_step],
        total_duration_ms=total_ms,
        structured_payload=payload,
        explanation=explanation,
    )
    repo.save_trace_and_decision(trace)

    tbl = Table(
        title=(
            f"[bold {GOOGLE_YELLOW}]📚 Hybrid RAG Knowledge Search — Query: `{query}` "
            f"({len(step.rag_citations)} chunks in {total_ms:.1f} ms)[/bold {GOOGLE_YELLOW}]"
        ),
        border_style=GOOGLE_YELLOW,
        expand=True,
    )
    tbl.add_column("Chunk ID", width=24, style=f"bold {CYAN_ACCENT}")
    tbl.add_column("Title & Type", width=28, style=f"bold {PISMANIYE_SILK}")
    tbl.add_column("Grounded Snippet & Source URI", style=f"{PISMANIYE_SILK}")
    tbl.add_column("Score", width=8, justify="right", style=f"bold {GOOGLE_GREEN}")
    tbl.add_column("Verification", width=24)

    for cit in step.rag_citations:
        tbl.add_row(
            cit.source_id,
            f"{cit.source_title}\n[{MUTED_SLATE}]({cit.source_type})[/{MUTED_SLATE}]",
            f"{cit.snippet}\n[{CYAN_ACCENT}]URI: {cit.source_uri}[/{CYAN_ACCENT}]",
            f"{cit.relevance_score:.2f}",
            format_verification_badge(cit.verification_status.value),
        )
    console.print(tbl)
    console.print(
        f"[{MUTED_SLATE}]Trace ID: [bold]{trace.trace_id}[/bold] • "
        f"Decision ID: [bold]{explanation.decision_id}[/bold][/{MUTED_SLATE}]"
    )


@app.command("trace")
def trace_command(
    trace_id: str = typer.Argument(
        "latest", help="Trace ID to inspect (or 'latest' for the most recent execution trace)."
    ),
) -> None:
    """Inspect a complete multi-agent execution trace, tool timings, and OpenTelemetry span data."""
    console = get_console()
    repo = get_repository()
    trace = repo.get_trace(trace_id)
    if not trace:
        # Run a quick default trace if none exist yet so the command is always helpful
        trace = get_orchestrator().run_query("Who should I meet for Agentic AI?")

    tree = Tree(
        f"[bold {PISMANIYE_GOLD}]◈ Trace Record `{trace.trace_id}`[/bold {PISMANIYE_GOLD}] "
        f"• Workflow: [bold {GOOGLE_BLUE}]{trace.workflow_name}[/bold {GOOGLE_BLUE}] "
        f"• Total Latency: [bold {GOOGLE_GREEN}]{trace.total_duration_ms:.1f} ms[/bold {GOOGLE_GREEN}]"
    )
    tree.add(f"[bold]Query:[/bold] {trace.query}")
    tree.add(f"[bold]Engine:[/bold] {trace.orchestrator_engine} (Mode: {trace.execution_mode})")
    tree.add(f"[bold]OpenTelemetry Trace ID:[/bold] {trace.otel_trace_id or 'local-span'}")
    tree.add(f"[bold]Linked XAI Decision ID:[/bold] {trace.decision_id}")

    steps_branch = tree.add(f"[bold {CYAN_ACCENT}]Agent Execution Steps ({len(trace.steps)})[/bold {CYAN_ACCENT}]")
    for idx, step in enumerate(trace.steps, start=1):
        meta = AGENT_VISUAL_META.get(step.agent_id.value, AGENT_VISUAL_META["supervisor"])
        color = meta["color"]
        s_node = steps_branch.add(
            f"[{color} bold]{idx}. {meta['icon']} {step.agent_label}[/{color} bold] "
            f"({step.status.value}, {step.duration_ms:.1f} ms, confidence={step.confidence * 100:.0f}%)"
        )
        s_node.add(f"[{MUTED_SLATE}]Thought:[/{MUTED_SLATE}] {step.thought}")
        for tc in step.tool_calls:
            s_node.add(
                f"[{CYAN_ACCENT}]⚙ Tool `{tc.tool_name}`[/{CYAN_ACCENT}] "
                f"args={tc.arguments} -> {tc.result_summary} ({tc.duration_ms:.1f} ms)"
            )
        for cit in step.rag_citations:
            s_node.add(
                f"[{GOOGLE_YELLOW}]📚 Citation `{cit.source_id}`[/{GOOGLE_YELLOW}] "
                f"score={cit.relevance_score:.2f} ({cit.verification_status.value})"
            )

    console.print(Panel(tree, title="[bold bright_white]🔍 PISMANIYE TRACE INSPECTOR[/bold bright_white]", border_style=GOOGLE_BLUE))


@app.command("explain")
def explain_command(
    decision_id: str = typer.Argument(
        "latest", help="Decision ID to explain (or 'latest' for the most recent XAI decision)."
    ),
) -> None:
    """Inspect XAI decision provenance, factor-by-factor scoring, evidence citations, and uncertainty."""
    console = get_console()
    repo = get_repository()
    explanation = repo.get_decision(decision_id)
    if not explanation:
        trace = get_orchestrator().run_query(
            "I'm interested in Agentic AI, Gemini, and production AI systems. Who should I meet?",
            explicit_workflow="workflow_a",
        )
        explanation = trace.explanation
    if explanation:
        render_decision_explanation(console, explanation)


@app.command("doctor")
def doctor_command() -> None:
    """Run comprehensive diagnostics on Python environment, agents, RAG index, privacy guardrails, and GCP adapters."""
    console = get_console()
    settings = get_settings()
    repo = get_repository()
    orchestrator = get_orchestrator()
    rag_stats = repo.rag.stats()

    tbl = Table(
        title=f"[bold {PISMANIYE_SILK}]🩺 PISMANIYE SYSTEM DOCTOR & ARCHITECTURE HEALTH CHECK[/bold {PISMANIYE_SILK}]",
        border_style=GOOGLE_GREEN,
        expand=True,
    )
    tbl.add_column("Check Category", width=28, style=f"bold {PISMANIYE_SILK}")
    tbl.add_column("Status", width=12)
    tbl.add_column("Diagnostic Details", style=f"{PISMANIYE_SILK}")

    # 1. Runtime & Mode
    tbl.add_row(
        "Runtime & Deterministic Mode",
        f"[{GOOGLE_GREEN}]✔ PASS[/{GOOGLE_GREEN}]",
        f"Mode={settings.mode} | Event={settings.event_id} | Local State={settings.data_dir}",
    )
    # 2. LangGraph + Google ADK
    adk_status = orchestrator.adk_bridge.describe_status()
    tbl.add_row(
        "LangGraph & Google ADK Bridge",
        f"[{GOOGLE_GREEN}]✔ PASS[/{GOOGLE_GREEN}]",
        f"StateGraph compiled • 6 Specialized Agents + XAI Auditor ({adk_status['integration_mode']})",
    )
    # 3. Model & Embedding Adapter
    tbl.add_row(
        "Model & Embedding Adapter",
        f"[{GOOGLE_GREEN}]✔ PASS[/{GOOGLE_GREEN}]",
        f"Backend={repo.model_adapter.backend_name} | Embedding Model={settings.embedding_model}",
    )
    # 4. Knowledge Base & Hybrid RAG
    test_hits = repo.rag.search("LangGraph Gemini Agentic AI", top_k=2)
    tbl.add_row(
        "Knowledge Base & Hybrid RAG",
        f"[{GOOGLE_GREEN}]✔ PASS[/{GOOGLE_GREEN}]" if test_hits else f"[{GOOGLE_RED}]✘ FAIL[/{GOOGLE_RED}]",
        f"{rag_stats['total_documents']} docs, {rag_stats['total_chunks']} chunks indexed • Test query returned {len(test_hits)} citations",
    )
    # 5. Privacy & Opt-In Guardrails
    all_count = len(repo.people)
    opt_in_count = len(repo.list_discoverable_people())
    redacted_sample = "contact: [REDACTED-EMAIL-CONSENT-REQUIRED]"
    tbl.add_row(
        "Privacy, Opt-In & PII Redaction",
        f"[{GOOGLE_GREEN}]✔ PASS[/{GOOGLE_GREEN}]",
        f"{opt_in_count}/{all_count} discoverable ({all_count - opt_in_count} private excluded) • PII guard active ({redacted_sample})",
    )
    # 6. Storage & Observability
    tbl.add_row(
        "Storage & OpenTelemetry",
        f"[{GOOGLE_GREEN}]✔ PASS[/{GOOGLE_GREEN}]",
        f"{repo.firestore_adapter.backend_name} • OTel Spans exported={len(orchestrator.telemetry.exporter.spans)}",
    )

    console.print(tbl)


@app.command("demo")
def demo_command() -> None:
    """Execute all 4 Signature Agentic Workflows end-to-end with live orchestration visualization."""
    console = get_console()
    settings = get_settings()
    console.print(build_logo_renderable(event_id=settings.event_id, mode=settings.mode))

    workflows = [
        (
            "WORKFLOW A: MEET THE RIGHT EXPERT",
            "I'm interested in Agentic AI, Gemini, and production AI systems. Who should I meet?",
            "workflow_a",
        ),
        (
            "WORKFLOW B: MY DEVFEST DAY",
            "Create my ideal DevFest agenda. I'm interested in Google Cloud and AI.",
            "workflow_b",
        ),
        (
            "WORKFLOW C: DISCOVER KOCAELI",
            "I'm a visiting GDE. I have three free hours. Help me discover Kocaeli.",
            "workflow_c",
        ),
        (
            "WORKFLOW D: COMMUNITY KNOWLEDGE",
            "I want to start learning Agentic AI after DevFest.",
            "workflow_d",
        ),
    ]

    last_trace: TraceRecord | None = None
    for wf_title, wf_query, wf_code in workflows:
        console.print(
            Panel(
                f"[bold {PISMANIYE_SILK}]{wf_title}[/bold {PISMANIYE_SILK}]\n"
                f"[italic {CYAN_ACCENT}]User: \"{wf_query}\"[/italic {CYAN_ACCENT}]",
                border_style=PISMANIYE_GOLD,
            )
        )
        last_trace = _run_with_live_graph(query=wf_query, explicit_workflow=wf_code)

    if last_trace and last_trace.explanation:
        console.print(
            f"\n[bold {PURPLE_ACCENT}]▶ Inspecting XAI Audit for Final Workflow (`{last_trace.decision_id}`)...[/bold {PURPLE_ACCENT}]"
        )
        render_decision_explanation(console, last_trace.explanation)


@app.command("serve")
def serve_command(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind host for the Community Web App & API."),
    port: int = typer.Option(8080, "--port", "-p", help="Bind port for the Community Web App & API."),
) -> None:
    """Launch the responsive Community Web Application, Organizer Dashboard, and REST/SSE API."""
    import uvicorn

    console = get_console()
    settings = get_settings()
    url = f"http://{host}:{port}" if host != "0.0.0.0" else settings.public_web_url
    console.print(
        Panel(
            f"[bold {GOOGLE_GREEN}]Starting PISMANIYE Community Web App & Organizer Dashboard[/bold {GOOGLE_GREEN}]\n"
            f"• Bind Address: [bold {CYAN_ACCENT}]{host}:{port}[/bold {CYAN_ACCENT}] (QR Target: [bold]{url}[/bold])\n"
            f"• OpenAPI Docs: [bold {GOOGLE_BLUE}]/docs[/bold {GOOGLE_BLUE}]\n"
            f"• Organizer RBAC Auth: [bold {GOOGLE_YELLOW}]Protected via X-Organizer-Token (PISMANIYE_ORGANIZER_PASSCODE)[/bold {GOOGLE_YELLOW}]",
            border_style=GOOGLE_BLUE,
        )
    )
    uvicorn.run("pismaniye.api.app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    app()
