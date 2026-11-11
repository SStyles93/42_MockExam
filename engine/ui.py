"""Terminal output helpers (ANSI colours, durations)."""
from __future__ import annotations

import os
import sys

if os.name == "nt":
    os.system("")  # enables ANSI escape sequences in the Windows console

_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _style(code: str):
    def apply(text: object) -> str:
        return f"\033[{code}m{text}\033[0m" if _COLOR else str(text)
    return apply


red = _style("31")
green = _style("32")
yellow = _style("33")
cyan = _style("36")
bold = _style("1")
dim = _style("2")


def duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rest = divmod(seconds, 3600)
    m, s = divmod(rest, 60)
    return f"{h}h{m:02d}m{s:02d}s"


def rule(width: int = 64) -> str:
    return dim("-" * width)
