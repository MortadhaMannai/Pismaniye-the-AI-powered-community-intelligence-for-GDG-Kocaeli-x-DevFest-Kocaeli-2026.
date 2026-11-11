"""UI and terminal rendering utilities for PISMANIYE."""

from pismaniye.ui.banner import build_logo_renderable, generate_terminal_qr, play_cinematic_startup
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
    render_thread_divider,
)

__all__ = [
    "AGENT_VISUAL_META",
    "CYAN_ACCENT",
    "GOOGLE_BLUE",
    "GOOGLE_GREEN",
    "GOOGLE_RED",
    "GOOGLE_YELLOW",
    "MUTED_SLATE",
    "PISMANIYE_GOLD",
    "PISMANIYE_SILK",
    "PURPLE_ACCENT",
    "build_logo_renderable",
    "format_verification_badge",
    "generate_terminal_qr",
    "get_console",
    "play_cinematic_startup",
    "render_thread_divider",
]
