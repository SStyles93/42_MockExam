"""A fake "vogsphere": rendu/ is a git repository whose remote is a local bare
repository. Like the real exam, only what was pushed gets graded.

Standard library only; needs the `git` executable.
"""
from __future__ import annotations

import io
import os
import shutil
import subprocess
import tarfile
from pathlib import Path, PurePosixPath
from typing import List, Optional

BRANCH = "master"


def git_available() -> bool:
    return shutil.which("git") is not None


def _git(args: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, check=check)


def init(rendu: Path, remote: Path) -> None:
    """Make sure the bare remote and the rendu/ clone exist and are wired together.
    Safe to call on every launch."""
    if not (remote / "HEAD").is_file():
        remote.mkdir(parents=True, exist_ok=True)
        _git(["init", "--bare", "-q", str(remote)])
        _git(["symbolic-ref", "HEAD", f"refs/heads/{BRANCH}"], cwd=remote)

    rendu.mkdir(parents=True, exist_ok=True)
    if not (rendu / ".git").exists():
        _git(["init", "-q"], cwd=rendu)
        _git(["symbolic-ref", "HEAD", f"refs/heads/{BRANCH}"], cwd=rendu)

    # Relative, so the same repo works from WSL, Git Bash, macOS... (an absolute
    # /mnt/c/... path written under WSL is meaningless to Git for Windows).
    # git runs remote operations from the worktree root, so this resolves from rendu/.
    url = Path(os.path.relpath(remote.resolve(), rendu.resolve())).as_posix()
    if _git(["remote", "get-url", "origin"], cwd=rendu, check=False).returncode == 0:
        _git(["remote", "set-url", "origin", url], cwd=rendu)
    else:
        _git(["remote", "add", "origin", url], cwd=rendu)
    # a plain `git push` works from the first push on, as in the real exam
    _git(["config", f"branch.{BRANCH}.remote", "origin"], cwd=rendu)
    _git(["config", f"branch.{BRANCH}.merge", f"refs/heads/{BRANCH}"], cwd=rendu)
    # commits must not fail on a machine without a configured identity
    for key, value in (("user.name", "student"), ("user.email", "student@mockexam.local")):
        if not _git(["config", key], cwd=rendu, check=False).stdout.strip():
            _git(["config", key, value], cwd=rendu)


def export_pushed(remote: Path, subdir: str, dest: Path) -> None:
    """Extract `subdir` of the pushed branch into dest (created, possibly empty).
    Nothing pushed simply yields an empty directory."""
    dest.mkdir(parents=True, exist_ok=True)
    if not (remote / "HEAD").is_file():
        return
    proc = _git(["--git-dir", str(remote), "archive", "--format=tar",
                 f"refs/heads/{BRANCH}", "--", subdir], check=False)
    if proc.returncode != 0:  # branch missing, or subdir not in the tree
        return
    prefix = PurePosixPath(subdir)
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tar:
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or ".." in path.parts:
                continue
            try:
                rel = path.relative_to(prefix)
            except ValueError:
                continue
            target = dest.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is not None:
                target.write_bytes(source.read())
