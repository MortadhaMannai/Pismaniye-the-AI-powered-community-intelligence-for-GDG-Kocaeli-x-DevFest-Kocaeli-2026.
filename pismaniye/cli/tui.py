"""Interactive Textual TUI cockpit for PISMANIYE (`pismaniye launch --tui`)."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, RichLog, Static

from pismaniye.orchestration.graph import get_orchestrator
from pismaniye.schemas.agent import LiveOrchestrationEvent


class PismaniyeCockpitApp(App[None]):
    """Textual Interactive Multi-Agent Mission Control for DevFest Kocaeli 2026."""

    TITLE = "PISMANIYE — GDG Kocaeli Multi-Agent Intelligence Platform"
    SUB_TITLE = "Unraveling People. Connecting Possibilities."

    CSS = """
    Screen {
        background: #0b1020;
        color: #f8f4ec;
    }
    #top-bar {
        height: 4;
        padding: 1 2;
        background: #131c36;
        border-bottom: solid #4285F4;
    }
    #main-split {
        height: 1fr;
    }
    #left-pane {
        width: 42%;
        border-right: solid #4285F4;
        padding: 1;
    }
    #right-pane {
        width: 58%;
        padding: 1;
    }
    #quick-workflows {
        height: auto;
        padding-bottom: 1;
    }
    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "workflow_a", "Workflow A: Meet Expert"),
        ("2", "workflow_b", "Workflow B: DevFest Day"),
        ("3", "workflow_c", "Workflow C: Kocaeli 3h"),
        ("4", "workflow_d", "Workflow D: Learning Path"),
    ]

    def __init__(self, event_id: str = "devfest-kocaeli-2026") -> None:
        super().__init__()
        self.event_id = event_id
        self.orchestrator = get_orchestrator()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            f"[bold #4285F4]◈ Event:[/bold #4285F4] {self.event_id}   "
            f"[bold #34A853]● Agents:[/bold #34A853] 6 Specialized + XAI Auditor   "
            f"[bold #FBBC04]✦ Keys:[/bold #FBBC04] Press [1-4] for Signature Workflows or type below",
            id="top-bar",
        )
        with Horizontal(id="quick-workflows"):
            yield Button("1: Meet Expert", id="btn-wfa", variant="primary")
            yield Button("2: My DevFest Day", id="btn-wfb", variant="success")
            yield Button("3: Discover Kocaeli (3h)", id="btn-wfc", variant="warning")
            yield Button("4: Learning Path", id="btn-wfd", variant="default")
        with Horizontal(id="main-split"):
            with Vertical(id="left-pane"):
                yield Static("[bold #FBBC04]⚡ Live Agent Execution Graph & Telemetry[/bold #FBBC04]")
                yield RichLog(id="trace-log", markup=True, wrap=True)
            with Vertical(id="right-pane"):
                yield Static("[bold #34A853]✦ Grounded Multi-Agent Output & XAI Provenance[/bold #34A853]")
                yield RichLog(id="response-log", markup=True, wrap=True)
        yield Input(
            placeholder="Ask Pismaniye anything (e.g. 'Who should I meet for Agentic AI and Gemini?')...",
            id="query-input",
        )
        yield Footer()

    def on_mount(self) -> None:
        trace_log = self.query_one("#trace-log", RichLog)
        trace_log.write("[bold #4285F4]✔ Pismaniye LangGraph + Google ADK Orchestrator Ready.[/bold #4285F4]")
        trace_log.write("Select a signature workflow button or enter a query below.")

    def _execute_query(self, query: str, workflow: str | None = None) -> None:
        trace_log = self.query_one("#trace-log", RichLog)
        resp_log = self.query_one("#response-log", RichLog)
        trace_log.write(f"\n[bold #FFD57E]▶ Query:[/bold #FFD57E] {query}")

        def _on_event(ev: LiveOrchestrationEvent) -> None:
            ag = ev.agent_label or "Supervisor"
            trace_log.write(f"[#4ECDC4]{ag}[/#4ECDC4]: {ev.message} ({ev.duration_ms:.1f} ms)")

        trace = self.orchestrator.run_query(
            query=query,
            explicit_workflow=workflow,
            event_callback=_on_event,
        )
        resp_log.clear()
        resp_log.write(f"[bold #4285F4]Trace ID:[/bold #4285F4] {trace.trace_id} | [bold #A78BFA]Decision ID:[/bold #A78BFA] {trace.decision_id}\n")
        resp_log.write(trace.final_response_markdown)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        if val:
            event.input.value = ""
            self._execute_query(val)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-wfa":
            self.action_workflow_a()
        elif btn_id == "btn-wfb":
            self.action_workflow_b()
        elif btn_id == "btn-wfc":
            self.action_workflow_c()
        elif btn_id == "btn-wfd":
            self.action_workflow_d()

    def action_workflow_a(self) -> None:
        self._execute_query(
            "I'm interested in Agentic AI, Gemini, and production AI systems. Who should I meet?",
            workflow="workflow_a",
        )

    def action_workflow_b(self) -> None:
        self._execute_query(
            "Create my ideal DevFest agenda. I'm interested in Google Cloud and AI.",
            workflow="workflow_b",
        )

    def action_workflow_c(self) -> None:
        self._execute_query(
            "I'm a visiting GDE. I have three free hours. Help me discover Kocaeli.",
            workflow="workflow_c",
        )

    def action_workflow_d(self) -> None:
        self._execute_query(
            "I want to start learning Agentic AI after DevFest.",
            workflow="workflow_d",
        )
