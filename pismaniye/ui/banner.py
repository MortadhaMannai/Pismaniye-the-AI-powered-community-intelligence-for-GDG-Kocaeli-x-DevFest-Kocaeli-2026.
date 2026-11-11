"""Cinematic terminal banner, thread animation, and QR code renderer for PISMANIYE."""

from __future__ import annotations

import io
import time
from typing import Any

import qrcode
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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
    render_thread_divider,
)

ASCII_LOGO_LINES = [
    "██████╗ ██╗███████╗███╗   ███╗ █████╗ ███╗   ██╗██╗██╗   ██╗███████╗",
    "██╔══██╗██║██╔════╝████╗ ████║██╔══██╗████╗  ██║██║╚██╗ ██╔╝██╔════╝",
    "██████╔╝██║███████╗██╔████╔██║███████║██╔██╗ ██║██║ ╚████╔╝ █████╗  ",
    "██╔═══╝ ██║╚════██║██║╚██╔╝██║██╔══██║██║╚██╗██║██║  ╚██╔╝  ██╔══╝  ",
    "██║     ██║███████║██║ ╚═╝ ██║██║  ██║██║ ╚████║██║   ██║   ███████╗",
    "╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝",
]

THREAD_FRAMES = [
    f"[{GOOGLE_BLUE}]╭───╮[/{GOOGLE_BLUE}][{GOOGLE_RED}]╭───╮[/{GOOGLE_RED}][{GOOGLE_YELLOW}]╭───╮[/{GOOGLE_YELLOW}][{GOOGLE_GREEN}]╭───╮[/{GOOGLE_GREEN}]  [italic {PISMANIYE_SILK}]Spinning community knowledge threads...[/italic {PISMANIYE_SILK}]",
    f"[{GOOGLE_RED}]╰───╯[/{GOOGLE_RED}][{GOOGLE_YELLOW}]╭───╮[/{GOOGLE_YELLOW}][{GOOGLE_GREEN}]╰───╯[/{GOOGLE_GREEN}][{GOOGLE_BLUE}]╭───╮[/{GOOGLE_BLUE}]  [italic {PISMANIYE_SILK}]Weaving LangGraph + Google ADK orchestrator...[/italic {PISMANIYE_SILK}]",
    f"[{GOOGLE_YELLOW}]╭───╮[/{GOOGLE_YELLOW}][{GOOGLE_GREEN}]╰───╯[/{GOOGLE_GREEN}][{GOOGLE_BLUE}]╭───╮[/{GOOGLE_BLUE}][{GOOGLE_RED}]╰───╯[/{GOOGLE_RED}]  [italic {PISMANIYE_SILK}]Verifying privacy guardrails & XAI audit engine...[/italic {PISMANIYE_SILK}]",
    f"[{GOOGLE_GREEN}]═════[/{GOOGLE_GREEN}][{GOOGLE_BLUE}]═════[/{GOOGLE_BLUE}][{GOOGLE_RED}]═════[/{GOOGLE_RED}][{GOOGLE_YELLOW}]═════[/{GOOGLE_YELLOW}]  [bold {GOOGLE_GREEN}]✔ All 6 Specialized Agents + XAI Auditor Online[/bold {GOOGLE_GREEN}]",
]


def build_logo_renderable(event_id: str = "devfest-kocaeli-2026", mode: str = "local_deterministic") -> Panel:
    """Create the flagship PISMANIYE hero banner panel."""
    colors = [GOOGLE_BLUE, GOOGLE_BLUE, GOOGLE_RED, GOOGLE_YELLOW, GOOGLE_GREEN, PISMANIYE_GOLD]
    logo_text = Text()
    for idx, line in enumerate(ASCII_LOGO_LINES):
        color = colors[idx % len(colors)]
        logo_text.append(line + "\n", style=f"bold {color}")

    tagline = Text()
    tagline.append("‹/› ", style=f"bold {GOOGLE_BLUE}")
    tagline.append("GDG Kocaeli ", style=f"bold {PISMANIYE_SILK}")
    tagline.append("• ", style=f"{MUTED_SLATE}")
    tagline.append("DevFest Kocaeli 2026 ", style=f"bold {GOOGLE_YELLOW}")
    tagline.append("• ", style=f"{MUTED_SLATE}")
    tagline.append("Multi-Agent Community Intelligence Platform\n", style=f"{CYAN_ACCENT}")
    tagline.append('"Unraveling People. Connecting Possibilities."', style=f"italic bold {PISMANIYE_GOLD}")

    meta_bar = Table.grid(padding=(0, 2))
    meta_bar.add_column(justify="center")
    meta_bar.add_column(justify="center")
    meta_bar.add_column(justify="center")
    meta_bar.add_column(justify="center")
    meta_bar.add_row(
        f"[{GOOGLE_BLUE}]● Event:[/{GOOGLE_BLUE}] [bold]{event_id}[/bold]",
        f"[{GOOGLE_GREEN}]● Mode:[/{GOOGLE_GREEN}] [bold]{mode}[/bold]",
        f"[{GOOGLE_YELLOW}]● Agents:[/{GOOGLE_YELLOW}] [bold]6 + XAI Auditor[/bold]",
        f"[{PURPLE_ACCENT}]● Privacy:[/{PURPLE_ACCENT}] [bold]Opt-In + Consent Enforced[/bold]",
    )

    group = Group(
        Align.center(logo_text),
        Align.center(tagline),
        Text(""),
        Align.center(Text.from_markup(render_thread_divider(72))),
        Align.center(meta_bar),
    )

    return Panel(
        group,
        border_style=GOOGLE_BLUE,
        title=f"[bold {PISMANIYE_SILK}] ✦ PISMANIYE v1.0.0 — COMMUNITY CONCIERGE & INTELLIGENCE ✦ [/bold {PISMANIYE_SILK}]",
        subtitle=f"[{MUTED_SLATE}]One community. Many threads. Infinite possibilities.[/{MUTED_SLATE}]",
        padding=(1, 2),
    )


def generate_terminal_qr(url: str) -> str:
    """Render a compact Unicode QR code for terminal presentation."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    buf = io.StringIO()
    qr.print_ascii(out=buf, invert=True)
    return buf.getvalue().rstrip("\n")


def play_cinematic_startup(
    console: Console,
    event_id: str,
    mode: str,
    system_checks: list[tuple[str, str, float]],
    web_url: str = "https://pismaniye-concierge.gdgkocaeli.dev",
    animate: bool = True,
) -> None:
    """Render the live cinematic startup sequence grounded on real subsystem initialization checks."""
    console.print(build_logo_renderable(event_id=event_id, mode=mode))

    if animate:
        with Live(console=console, refresh_per_second=16, transient=False) as live:
            for step_idx, (subsys, detail, duration_ms) in enumerate(system_checks):
                frame_str = THREAD_FRAMES[min(step_idx, len(THREAD_FRAMES) - 1)]
                tbl = Table(
                    title=f"[bold {PISMANIYE_SILK}]Live Subsystem & Agent Mesh Initialization[/bold {PISMANIYE_SILK}]",
                    border_style=GOOGLE_BLUE,
                    expand=True,
                )
                tbl.add_column("Subsystem", style=f"bold {PISMANIYE_SILK}", width=28)
                tbl.add_column("Status", width=14)
                tbl.add_column("Telemetry Detail", style=f"{MUTED_SLATE}")
                tbl.add_column("Latency", justify="right", style=f"bold {GOOGLE_GREEN}", width=10)

                for completed_sub, completed_det, completed_ms in system_checks[: step_idx + 1]:
                    tbl.add_row(
                        completed_sub,
                        f"[{GOOGLE_GREEN}]● READY[/{GOOGLE_GREEN}]",
                        completed_det,
                        f"{completed_ms:.1f} ms",
                    )

                live.update(Group(Panel(frame_str, border_style=PISMANIYE_GOLD), tbl))
                time.sleep(0.08)

    # Render Agent Mesh Topology & QR Code side-by-side
    agent_table = Table(
        title=f"[bold {PISMANIYE_SILK}]Active Multi-Agent Constellation[/bold {PISMANIYE_SILK}]",
        border_style=GOOGLE_GREEN,
        expand=True,
    )
    agent_table.add_column("Agent", width=22)
    agent_table.add_column("Specialization & Grounding", style=f"{PISMANIYE_SILK}")
    for key, meta in AGENT_VISUAL_META.items():
        if key == "supervisor":
            continue
        color = meta["color"]
        agent_table.add_row(
            f"[{color} bold]{meta['icon']} {meta['name']}[/{color} bold]",
            meta["role"],
        )

    qr_ascii = generate_terminal_qr(web_url)
    qr_panel = Panel(
        Align.center(
            Text.from_markup(
                f"[bold {GOOGLE_YELLOW}]Scan for Mobile Concierge[/bold {GOOGLE_YELLOW}]\n"
                f"[{PISMANIYE_SILK}]{qr_ascii}[/{PISMANIYE_SILK}]\n"
                f"[bold {CYAN_ACCENT}]{web_url}[/bold {CYAN_ACCENT}]"
            )
        ),
        title=f"[bold {GOOGLE_BLUE}]Community Web App[/bold {GOOGLE_BLUE}]",
        border_style=GOOGLE_YELLOW,
    )

    console.print(Columns([agent_table, qr_panel], expand=True))
