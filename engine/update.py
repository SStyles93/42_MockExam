"""Self-update: `git pull --ff-only` on the MockExam checkout before starting.

Never blocks or breaks a launch: offline, no git, local edits, a diverged
branch... all leave the current version running with a one-line note.
Runtime folders (rendu/, traces/, .vogsphere/, ...) are git-ignored, so a pull
never touches the student's work.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

TIMEOUT = 15  # seconds for the whole pull
SKIP_ENV = "MOCKEXAM_NO_UPDATE"


def _env() -> dict:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"                    # never ask for a password
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=5")
    env["LC_ALL"] = "C"
    return env


def _head(root: Path) -> Optional[str]:
    proc = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True, env=_env())
    return proc.stdout.strip() if proc.returncode == 0 else None


def self_update(root: Path) -> Tuple[bool, str]:
    """Returns (code changed, message to show or "")."""
    if os.environ.get(SKIP_ENV):
        return False, ""
    if not (root / ".git").exists() or shutil.which("git") is None:
        return False, ""  # not a git checkout (e.g. a downloaded zip): nothing to do
    before = _head(root)
    if before is None:
        return False, ""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "pull", "--ff-only", "--quiet"],
            capture_output=True, text=True, timeout=TIMEOUT, env=_env(),
            stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return False, "update check timed out; running the current version"
    except OSError as exc:
        return False, f"update skipped ({exc})"
    if proc.returncode != 0:
        first = next((line for line in proc.stderr.splitlines() if line.strip()), "")
        return False, f"update skipped: {first.strip() or 'git pull failed'}"
    after = _head(root)
    if after and after != before:
        return True, f"MockExam updated ({before[:7]} -> {after[:7]})"
    return False, ""
