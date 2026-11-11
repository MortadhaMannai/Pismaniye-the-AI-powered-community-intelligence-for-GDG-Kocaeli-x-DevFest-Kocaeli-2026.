"""Visual identity, Google-Developer-inspired palette, and thread motifs for PISMANIYE."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

# Google Developer community-inspired accent colors on deep navy/obsidian canvas
GOOGLE_BLUE = "#4285F4"
GOOGLE_RED = "#EA4335"
GOOGLE_YELLOW = "#FBBC04"
GOOGLE_GREEN = "#34A853"
PISMANIYE_SILK = "#F8F4EC"
PISMANIYE_GOLD = "#FFD57E"
NAVY_SURFACE = "#0B1020"
MUTED_SLATE = "#8B95A5"
CYAN_ACCENT = "#4ECDC4"
PURPLE_ACCENT = "#A78BFA"

PISMANIYE_THEME = Theme(
    {
        "brand.blue": f"bold {GOOGLE_BLUE}",
        "brand.red": f"bold {GOOGLE_RED}",
        "brand.yellow": f"bold {GOOGLE_YELLOW}",
        "brand.green": f"bold {GOOGLE_GREEN}",
        "brand.silk": f"bold {PISMANIYE_SILK}",
        "brand.gold": f"{PISMANIYE_GOLD}",
        "muted": f"{MUTED_SLATE}",
        "agent.supervisor": f"bold {PISMANIYE_GOLD}",
        "agent.event": f"bold {GOOGLE_BLUE}",
        "agent.people": f"bold {GOOGLE_RED}",
        "agent.knowledge": f"bold {GOOGLE_YELLOW}",
        "agent.kocaeli": f"bold {GOOGLE_GREEN}",
        "agent.matchmaker": f"bold {PURPLE_ACCENT}",
        "agent.community": f"bold {CYAN_ACCENT}",
        "agent.xai": "bold bright_white",
        "badge.verified": f"bold black on {GOOGLE_GREEN}",
        "badge.synthetic": f"bold black on {GOOGLE_YELLOW}",
        "badge.generated": f"bold white on {GOOGLE_BLUE}",
    }
)


def get_console() -> Console:
    """Return a Rich Console configured with the PISMANIYE visual identity."""
    return Console(theme=PISMANIYE_THEME, highlight=False)


AGENT_VISUAL_META: dict[str, dict[str, str]] = {
    "supervisor": {
        "name": "Supervisor Router",
        "icon": "◈",
        "color": PISMANIYE_GOLD,
        "role": "Intent Decomposition & Stateful Thread Routing",
    },
    "event_agent": {
        "name": "Event Agent",
        "icon": "◆",
        "color": GOOGLE_BLUE,
        "role": "Schedules, Sessions, Workshops, Conflict Resolution & Venue Logistics",
    },
    "people_agent": {
        "name": "People Agent",
        "icon": "●",
        "color": GOOGLE_RED,
        "role": "Opt-in Speaker, GDE, Organizer & Attendee Discovery",
    },
    "knowledge_agent": {
        "name": "Knowledge Agent",
        "icon": "▲",
        "color": GOOGLE_YELLOW,
        "role": "Hybrid RAG over Talk Abstracts, Bios, Docs & Technical Archives",
    },
    "kocaeli_agent": {
        "name": "Kocaeli Agent",
        "icon": "✦",
        "color": GOOGLE_GREEN,
        "role": "Verified Local Landmarks, Gastronomy & Time-Boxed Itineraries",
    },
    "matchmaker_agent": {
        "name": "Matchmaker Agent",
        "icon": "♾",
        "color": PURPLE_ACCENT,
        "role": "Transparent Compatibility Scoring, Mutual Benefit & Consent-Gated Intros",
    },
    "community_agent": {
        "name": "Community Agent",
        "icon": "⬢",
        "color": CYAN_ACCENT,
        "role": "Post-DevFest Learning Paths, Study Jams & GDG Kocaeli Contributions",
    },
    "xai_auditor": {
        "name": "XAI Auditor",
        "icon": "⚖",
        "color": "#FFFFFF",
        "role": "Evidence Provenance, Factor Breakdown, Uncertainty & Privacy Verification",
    },
}


def render_thread_divider(width: int = 78) -> str:
    """Render an intertwined Pişmaniye thread divider with Google Developer four-color accents."""
    segment = max(4, width // 4)
    return (
        f"[{GOOGLE_BLUE}]{'═' * segment}[/{GOOGLE_BLUE}]"
        f"[{GOOGLE_RED}]{'═' * segment}[/{GOOGLE_RED}]"
        f"[{GOOGLE_YELLOW}]{'═' * segment}[/{GOOGLE_YELLOW}]"
        f"[{GOOGLE_GREEN}]{'═' * segment}[/{GOOGLE_GREEN}]"
    )


def format_verification_badge(status: str) -> str:
    """Return a Rich-formatted badge distinguishing verified, synthetic, and generated items."""
    if status == "VERIFIED_ORGANIZER_DATA":
        return f"[{GOOGLE_GREEN} bold]✔ VERIFIED ORGANIZER DATA[/{GOOGLE_GREEN} bold]"
    if status == "GENERATED_SUGGESTION":
        return f"[{GOOGLE_BLUE} bold]✦ AI SYNTHESIZED SUGGESTION[/{GOOGLE_BLUE} bold]"
    return f"[{GOOGLE_YELLOW} bold]⚠ SAMPLE / FICTIONAL DATA[/{GOOGLE_YELLOW} bold]"
