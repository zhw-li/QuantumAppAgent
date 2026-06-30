"""Shared constants and utilities for CLI and TUI modules."""

from datetime import UTC, datetime


def _agent_name() -> str:
    # Deferred import: ``sessions`` pulls in langgraph/aiosqlite (~300 ms)
    # and is only needed when ``build_metadata`` is actually called.
    from ..sessions import AGENT_NAME

    return AGENT_NAME


# Dangerous-mode warning banner — shared by Rich CLI, Textual TUI, and serve so
# the wording never drifts. Label is rendered white-on-red, message in red.
DANGEROUS_BANNER_LABEL = "DANGEROUS MODE"
DANGEROUS_BANNER_MESSAGE = (
    "Real-filesystem access • the agent can read/write/delete anywhere."
)

WELCOME_SLOGANS = [
    "天衍量智已就绪。请输入你的量子应用目标。",
    "From idea to validated quantum application.",
    "TianYan Quantum Agent is ready for the next workflow.",
    "Define the problem. TYQA will structure the delivery path.",
    "Build, validate, and package quantum applications.",
]

# ASCII art logo — shared by both Rich CLI and Textual TUI banners.
LOGO_LINES = (
    r" ████████╗ ██╗  █████╗  ███╗   ██╗ ██╗   ██╗  █████╗  ███╗   ██╗       ██████╗   █████╗   ██████╗ ███████╗ ███╗   ██╗ ████████╗",
    r" ╚══██╔══╝ ██║ ██╔══██╗ ████╗  ██║ ╚██╗ ██╔╝ ██╔══██╗ ████╗  ██║      ██╔═══██╗ ██╔══██╗ ██╔════╝ ██╔════╝ ████╗  ██║ ╚══██╔══╝",
    r"    ██║    ██║ ███████║ ██╔██╗ ██║  ╚████╔╝  ███████║ ██╔██╗ ██║█████╗██║   ██║ ███████║ ██║  ███╗█████╗   ██╔██╗ ██║    ██║   ",
    r"    ██║    ██║ ██╔══██║ ██║╚██╗██║   ╚██╔╝   ██╔══██║ ██║╚██╗██║╚════╝██║▄▄ ██║ ██╔══██║ ██║   ██║██╔══╝   ██║╚██╗██║    ██║   ",
    r"    ██║    ██║ ██║  ██║ ██║ ╚████║    ██║    ██║  ██║ ██║ ╚████║      ╚██████╔╝ ██║  ██║ ╚██████╔╝███████╗ ██║ ╚████║    ██║   ",
    r"    ╚═╝    ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═══╝    ╚═╝    ╚═╝  ╚═╝ ╚═╝  ╚═══╝       ╚══▀▀═╝  ╚═╝  ╚═╝  ╚═════╝ ╚══════╝ ╚═╝  ╚═══╝    ╚═╝   ",
)

# Blue gradient: deep navy -> royal blue -> sky blue -> cyan
LOGO_GRADIENT = ["#1a237e", "#1565c0", "#1e88e5", "#42a5f5", "#64b5f6", "#90caf9"]


def build_metadata(workspace_dir: str | None, model: str | None) -> dict:
    """Build metadata dict for LangGraph checkpoint persistence."""
    return {
        "agent_name": _agent_name(),
        "updated_at": datetime.now(UTC).isoformat(),
        "workspace_dir": workspace_dir or "",
        "model": model or "",
    }
