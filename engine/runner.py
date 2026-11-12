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

LEAK_CHECK_CASES = 5            # cases run under valgrind when leak_check is set

# Calls the compiler emits on its own (gcc turns printf("x\n") into puts("x")).
ALIASES = {"printf": {"puts", "putchar"}, "fprintf": {"fputs", "fputc", "fwrite"}}

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
    valgrind: Optional[str] = None

    @classmethod
    def detect(cls) -> "Toolchain":
        return cls(cc=_first_available("CC", ["cc", "gcc", "clang"]),
                   nm=_first_available("NM", ["nm", "llvm-nm"]),
                   python=sys.executable,
                   valgrind=_first_available("VALGRIND", ["valgrind"]))


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


def _stage(ex: Exercise, source_dir: Path, names: List[str], dest: Path) -> None:
    """Copy only the expected files, like the real exam does."""
    dest.mkdir(parents=True)
    for name in names:
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_dir / name, target)
    for path in ex.provided:  # ours always wins, as in the real exam
        shutil.copy2(path, dest / path.name)


def _sources(names: List[str], lang: dict, workdir: Path) -> List[str]:
    ext = lang.get("source_ext", "")
    return [str(workdir / f) for f in names if f.endswith(ext)]


def _prepare(ex: Exercise, lang: dict, tc: Toolchain, workdir: Path, names: List[str],
             variant: dict, index: int) -> Callable[[Case], List[str]]:
    """Build in `workdir` if needed; return a function giving the run command."""
    values = {
        "cc": tc.cc or "",
        "python": tc.python,
        "bin": str(workdir / f"a.out{index or ''}{EXE_SUFFIX}"),
        "main": str(workdir / names[0]),
        "sources": _sources(names, lang, workdir) + [str(h) for h in ex.harness],
        "cflags": ex.cflags + variant.get("cflags", []),
        "ldflags": ex.ldflags,
    }
    if lang.get("build"):
        cmd = expand(lang["build"], **values)
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(workdir), timeout=120)
        if proc.returncode != 0:
            output = (proc.stdout + proc.stderr).replace(str(workdir) + os.sep, "")
            raise BuildError(output.strip() or f"compiler exited with {proc.returncode}")
    return lambda case: expand(lang["run"], **values, args=case.args)


def _forbidden_calls(ex: Exercise, lang: dict, tc: Toolchain, workdir: Path,
                     names: List[str]) -> List[str]:
    undefined, defined = set(), set()
    for src in _sources(names, lang, workdir):
        obj = workdir / (Path(src).stem + ".o")
        subprocess.run(expand(lang["object"], cc=tc.cc, source=src, obj=str(obj),
                              cflags=ex.cflags + ex.variants[0].get("cflags", [])),
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


def _numbers_match(a: bytes, b: bytes, tolerance: float) -> bool:
    ta, tb = a.split(), b.split()
    if len(ta) != len(tb):
        return False
    for x, y in zip(ta, tb):
        if x == y:
            continue
        try:
            if abs(float(x) - float(y)) > tolerance + 1e-9:
                return False
        except ValueError:
            return False
    return True


def outputs_match(ex: Exercise, expected: Outcome, got: Outcome) -> bool:
    if expected.error or got.error or expected.timed_out != got.timed_out \
            or expected.code != got.code:
        return False
    if ex.compare == "sorted_lines":
        return sorted(expected.stdout.split(b"\n")) == sorted(got.stdout.split(b"\n"))
    if ex.compare == "numeric":
        return _numbers_match(expected.stdout, got.stdout, ex.tolerance)
    return expected.stdout == got.stdout


def _leak_report(cmd: List[str], case: Case, ex: Exercise, tc: Toolchain,
                 workdir: Path) -> Optional[str]:
    """Run under valgrind; return its report if memory was leaked, else None."""
    log = workdir / "valgrind.log"
    vg = [tc.valgrind, "--leak-check=full", "--errors-for-leak-kinds=definite,indirect",
          "--show-leak-kinds=definite,indirect", "--error-exitcode=42", f"--log-file={log}"]
    outcome = run_program(vg + cmd, case, ex.timeout * 20, workdir)
    if outcome.code == 42:
        return log.read_text(errors="replace") if log.exists() else "valgrind reported errors"
    return None


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


COMPARE_NOTES = {
    "sorted_lines": "(the order of the lines does not matter)",
    "numeric": "(numbers are compared with a tolerance of {tol})",
}


def _case_trace(ex: Exercise, index: int, total: int, case: Case, variant: dict,
                expected: Outcome, got: Outcome) -> str:
    lines = [f"Test {index}/{total}: {case.display(ex.name)}"]
    if variant.get("name"):
        lines.append(f"Build: {variant['name']}")
    if case.stdin is not None:
        lines += ["stdin:", cat_e(case.stdin.encode())]
    note = COMPARE_NOTES.get(ex.compare, "").format(tol=ex.tolerance)
    lines += [
        "",
        f"--- expected ({expected.describe()}) --- {note}".rstrip(),
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

    user_names, missing = ex.collect_files(submission)
    if not missing and not _sources(user_names, lang, submission):
        missing = [f"a {lang.get('source_ext', 'source')} file"]
    if missing:
        return Result(False, "Missing file(s): " + ", ".join(missing),
                      trace=f"Expected in {submission}: {', '.join(ex.files)}")
    ref_names, ref_missing = ex.collect_files(ex.reference_dir)
    if ref_missing:
        return Result(False, "Reference solution incomplete: " + ", ".join(ref_missing),
                      internal=True)

    notes: List[str] = []
    try:
        cases = ex.cases(random.Random(seed))
    except ExerciseError as exc:
        return Result(False, str(exc), internal=True)

    with tempfile.TemporaryDirectory(prefix="mockexam-") as tmp_name:
        tmp = Path(tmp_name)
        user_dir, ref_dir = tmp / "user", tmp / "ref"
        _stage(ex, submission, user_names, user_dir)
        _stage(ex, ex.reference_dir, ref_names, ref_dir)

        for v_index, variant in enumerate(ex.variants):
            label = f" ({variant['name']})" if variant.get("name") else ""
            try:
                user_cmd = _prepare(ex, lang, tc, user_dir, user_names, variant, v_index)
            except BuildError as exc:
                return Result(False, "Compilation error" + label, trace=str(exc))
            try:
                ref_cmd = _prepare(ex, lang, tc, ref_dir, ref_names, variant, v_index)
            except BuildError as exc:
                return Result(False, "Reference solution does not build" + label,
                              trace=str(exc), internal=True)

            if v_index == 0 and lang.get("symbol_check") and ex.allowed is not None:
                if tc.nm:
                    bad = _forbidden_calls(ex, lang, tc, user_dir, user_names)
                    if bad:
                        return Result(False, "Forbidden function(s): " + ", ".join(bad),
                                      trace="Allowed functions: "
                                            + (", ".join(ex.allowed) or "none")
                                            + "\nFound: " + ", ".join(bad))
                else:
                    notes.append("nm not found: allowed-functions check skipped")

            for i, case in enumerate(cases, 1):
                expected = run_program(ref_cmd(case), case, ex.timeout, ref_dir)
                if expected.error or expected.timed_out or expected.crash():
                    return Result(False, f"Reference solution failed on test {i}{label}: "
                                         f"{expected.describe()}",
                                  trace=case.display(ex.name), internal=True)
                got = run_program(user_cmd(case), case, ex.timeout, user_dir)
                if not outputs_match(ex, expected, got):
                    return Result(False, f"Failed test {i}/{len(cases)}{label}",
                                  trace=_case_trace(ex, i, len(cases), case, variant,
                                                    expected, got),
                                  notes=notes)

        if ex.leak_check:
            if tc.valgrind:
                for i, case in enumerate(cases[:LEAK_CHECK_CASES], 1):
                    report = _leak_report(user_cmd(case), case, ex, tc, user_dir)
                    if report:
                        return Result(False, f"Memory leak (test {i}: {case.display(ex.name)})",
                                      trace=report, notes=notes)
            else:
                notes.append("valgrind not found: leak check skipped")

    builds = f" x {len(ex.variants)} builds" if len(ex.variants) > 1 else ""
    return Result(True, f"Passed {len(cases)} tests{builds}", notes=notes)
