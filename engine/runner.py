"""Grading: build the submission and the reference, run both, compare.

Every test case is run against the reference solution first, so tests never
need hand-written expected outputs: the reference *is* the expected output.
"""
from __future__ import annotations

import json
import os
import random
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .exercise import Case, Exercise, ExerciseError

ENGINE_DIR = Path(__file__).resolve().parent
EXE_SUFFIX = ".exe" if os.name == "nt" else ""
OUTPUT_LIMIT = 1 << 20          # stdout bytes kept per run
FILE_SIZE_LIMIT = 16 << 20      # POSIX: a runaway writer gets SIGXFSZ
TRACE_OUTPUT_MAX = 4000         # characters of output shown in a trace

# Calls the compiler emits on its own (gcc turns printf("x\n") into puts("x")).
ALIASES = {"printf": {"puts", "putchar"}}

WINDOWS_CRASHES = {
    0xC0000005: "ACCESS_VIOLATION",
    0xC00000FD: "STACK_OVERFLOW",
    0xC0000094: "INTEGER_DIVIDE_BY_ZERO",
    0xC0000409: "STACK_BUFFER_OVERRUN",
}


def load_languages() -> dict:
    return json.loads((ENGINE_DIR / "languages.json").read_text(encoding="utf-8"))


def _first_available(env: str, candidates: List[str]) -> Optional[str]:
    if os.environ.get(env):
        return os.environ[env]
    return next((c for c in candidates if shutil.which(c)), None)


@dataclass
class Toolchain:
    cc: Optional[str]
    nm: Optional[str]
    python: str

    @classmethod
    def detect(cls) -> "Toolchain":
        return cls(cc=_first_available("CC", ["cc", "gcc", "clang"]),
                   nm=_first_available("NM", ["nm", "llvm-nm"]),
                   python=sys.executable)


def expand(template: List[str], **values) -> List[str]:
    """Fill a command template. A token that is exactly "{key}" whose value is
    a list expands to several arguments; other tokens are str.format()ed."""
    scalars = {k: v for k, v in values.items() if not isinstance(v, list)}
    cmd: List[str] = []
    for token in template:
        key = token[1:-1] if token.startswith("{") and token.endswith("}") else None
        if key is not None and isinstance(values.get(key), list):
            cmd.extend(str(v) for v in values[key])
        else:
            cmd.append(token.format(**scalars))
    return cmd


# --------------------------------------------------------------------------- #
# Running a program
# --------------------------------------------------------------------------- #

@dataclass
class Outcome:
    stdout: bytes = b""
    code: Optional[int] = None
    timed_out: bool = False
    error: Optional[str] = None

    def crash(self) -> Optional[str]:
        if self.code is None:
            return None
        if self.code < 0:
            try:
                return signal.Signals(-self.code).name
            except ValueError:
                return f"signal {-self.code}"
        if os.name == "nt" and self.code >= 0xC0000000:
            return WINDOWS_CRASHES.get(self.code, hex(self.code))
        return None

    def describe(self) -> str:
        if self.error:
            return f"could not run: {self.error}"
        if self.timed_out:
            return "TIMEOUT"
        crash = self.crash()
        return f"CRASH: {crash}" if crash else f"exit code {self.code}"

    def matches(self, other: "Outcome") -> bool:
        return (not self.error and not other.error
                and self.timed_out == other.timed_out
                and self.stdout == other.stdout
                and self.code == other.code)


def _limit_resources() -> None:  # runs in the child, POSIX only
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_SIZE_LIMIT, FILE_SIZE_LIMIT))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run_program(cmd: List[str], case: Case, timeout: float, cwd: Path) -> Outcome:
    with tempfile.TemporaryFile() as out:
        kwargs: Dict = {"stdout": out, "stderr": subprocess.DEVNULL, "cwd": str(cwd)}
        if os.name == "posix":
            kwargs["preexec_fn"] = _limit_resources
        stdin = subprocess.PIPE if case.stdin is not None else subprocess.DEVNULL
        try:
            proc = subprocess.Popen(cmd, stdin=stdin, **kwargs)
        except OSError as exc:
            return Outcome(error=str(exc))
        data = case.stdin.encode() if case.stdin is not None else None
        try:
            proc.communicate(data, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            return Outcome(timed_out=True)
        out.seek(0)
        return Outcome(stdout=out.read(OUTPUT_LIMIT), code=proc.returncode)


# --------------------------------------------------------------------------- #
# Building
# --------------------------------------------------------------------------- #

class BuildError(Exception):
    pass


def _stage(ex: Exercise, source_dir: Path, dest: Path) -> None:
    """Copy only the expected files, like the real exam does."""
    dest.mkdir(parents=True)
    for name in ex.files:
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_dir / name, target)


def _sources(ex: Exercise, lang: dict, workdir: Path) -> List[str]:
    ext = lang.get("source_ext", "")
    return [str(workdir / f) for f in ex.files if f.endswith(ext)]


def _prepare(ex: Exercise, lang: dict, tc: Toolchain, workdir: Path) -> Callable[[Case], List[str]]:
    """Build in `workdir` if needed; return a function giving the run command."""
    values = {
        "cc": tc.cc or "",
        "python": tc.python,
        "bin": str(workdir / ("a.out" + EXE_SUFFIX)),
        "main": str(workdir / ex.files[0]),
        "sources": _sources(ex, lang, workdir) + [str(h) for h in ex.harness],
    }
    if lang.get("build"):
        cmd = expand(lang["build"], **values)
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(workdir), timeout=120)
        if proc.returncode != 0:
            output = (proc.stdout + proc.stderr).replace(str(workdir) + os.sep, "")
            raise BuildError(output.strip() or f"compiler exited with {proc.returncode}")
    return lambda case: expand(lang["run"], **values, args=case.args)


def _forbidden_calls(ex: Exercise, lang: dict, tc: Toolchain, workdir: Path) -> List[str]:
    undefined, defined = set(), set()
    for src in _sources(ex, lang, workdir):
        obj = workdir / (Path(src).stem + ".o")
        subprocess.run(expand(lang["object"], cc=tc.cc, source=src, obj=str(obj)),
                       capture_output=True, cwd=str(workdir))
        listing = subprocess.run([tc.nm, str(obj)], capture_output=True, text=True).stdout
        for line in listing.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            kind, name = parts[-2], parts[-1]
            if sys.platform == "darwin" and name.startswith("_"):
                name = name[1:]
            if kind == "U":
                undefined.add(name)
            elif kind.isupper():
                defined.add(name)
    allowed = set(ex.allowed or [])
    for fn in list(allowed):
        allowed |= ALIASES.get(fn, set())
    return sorted(n for n in undefined - defined - allowed if not n.startswith(("_", ".")))


# --------------------------------------------------------------------------- #
# Grading
# --------------------------------------------------------------------------- #

@dataclass
class Result:
    passed: bool
    summary: str
    trace: str = ""
    internal: bool = False          # broken exercise/toolchain, not the student's fault
    notes: List[str] = field(default_factory=list)


def cat_e(data: bytes) -> str:
    """Render bytes like `cat -e`: '$' at line ends, ^X / M- for non-printables."""
    out = []
    for b in data:
        prefix = ""
        if b >= 128:
            prefix, b = "M-", b - 128
        if not prefix and b == 10:
            out.append("$\n")
        elif not prefix and b == 9:
            out.append("\t")
        elif b < 32 or b == 127:
            out.append(prefix + "^" + chr(b ^ 64))
        else:
            out.append(prefix + chr(b))
    text = "".join(out)
    if len(text) > TRACE_OUTPUT_MAX:
        text = text[:TRACE_OUTPUT_MAX] + "\n[... output truncated ...]"
    return text if text else "(no output)"


def _case_trace(ex: Exercise, index: int, total: int, case: Case,
                expected: Outcome, got: Outcome) -> str:
    lines = [f"Test {index}/{total}: {case.display(ex.name)}"]
    if case.stdin is not None:
        lines += ["stdin:", cat_e(case.stdin.encode())]
    lines += [
        "",
        f"--- expected ({expected.describe()}) ---",
        cat_e(expected.stdout),
        f"--- yours ({got.describe()}) ---",
        cat_e(got.stdout),
    ]
    return "\n".join(lines)


def grade(ex: Exercise, submission: Path, tc: Toolchain, languages: dict,
          seed: Optional[int] = None) -> Result:
    lang = languages.get(ex.language)
    if lang is None:
        return Result(False, f"Unknown language '{ex.language}'", internal=True)
    missing_tools = [t for t in lang.get("requires", []) if not getattr(tc, t, None)]
    if missing_tools:
        return Result(False, f"Missing tool(s): {', '.join(missing_tools)} "
                             "(install a C compiler or set CC=...)", internal=True)

    missing = [f for f in ex.files if not (submission / f).is_file()]
    if missing:
        return Result(False, "Missing file(s): " + ", ".join(missing),
                      trace=f"Expected in {submission}: {', '.join(ex.files)}")

    notes: List[str] = []
    with tempfile.TemporaryDirectory(prefix="mockexam-") as tmp_name:
        tmp = Path(tmp_name)
        user_dir, ref_dir = tmp / "user", tmp / "ref"
        _stage(ex, submission, user_dir)
        _stage(ex, ex.reference_dir, ref_dir)

        try:
            user_cmd = _prepare(ex, lang, tc, user_dir)
        except BuildError as exc:
            return Result(False, "Compilation error", trace=str(exc))
        try:
            ref_cmd = _prepare(ex, lang, tc, ref_dir)
        except BuildError as exc:
            return Result(False, "Reference solution does not build", trace=str(exc), internal=True)

        if lang.get("symbol_check") and ex.allowed is not None:
            if tc.nm:
                bad = _forbidden_calls(ex, lang, tc, user_dir)
                if bad:
                    return Result(False, "Forbidden function(s): " + ", ".join(bad),
                                  trace="Allowed functions: " + (", ".join(ex.allowed) or "none")
                                        + "\nFound: " + ", ".join(bad))
            else:
                notes.append("nm not found: allowed-functions check skipped")

        try:
            cases = ex.cases(random.Random(seed))
        except ExerciseError as exc:
            return Result(False, str(exc), internal=True)

        for i, case in enumerate(cases, 1):
            expected = run_program(ref_cmd(case), case, ex.timeout, ref_dir)
            if expected.error or expected.timed_out or expected.crash():
                return Result(False, f"Reference solution failed on test {i}: {expected.describe()}",
                              trace=case.display(ex.name), internal=True)
            got = run_program(user_cmd(case), case, ex.timeout, user_dir)
            if not got.matches(expected):
                return Result(False, f"Failed test {i}/{len(cases)}",
                              trace=_case_trace(ex, i, len(cases), case, expected, got),
                              notes=notes)

    return Result(True, f"Passed {len(cases)} tests", notes=notes)
