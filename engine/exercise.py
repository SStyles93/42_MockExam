"""Loading exams and exercises from the `exams/` directory.

Layout:
    exams/<exam>/exam.json
    exams/<exam>/<level>/<exercise>/meta.json
                                   /subject.txt
                                   /tests.py
                                   /reference/<expected files>
                                   /<harness files>        (function exercises)
"""
from __future__ import annotations

import importlib.util
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

LABEL_MAX = 72


class ExerciseError(Exception):
    """An exercise definition is broken (not the student's fault)."""


@dataclass
class Case:
    args: List[str]
    stdin: Optional[str] = None
    label: Optional[str] = None

    def display(self, program: str) -> str:
        if self.label:
            text = self.label
        else:
            text = " ".join([f"./{program}"] + [_quote(a) for a in self.args])
        return text if len(text) <= LABEL_MAX else text[: LABEL_MAX - 3] + "..."


@dataclass
class Exercise:
    exam: str
    level: str
    name: str
    path: Path
    meta: dict

    @property
    def id(self) -> str:
        return f"{self.level}/{self.name}"

    @property
    def type(self) -> str:
        return self.meta.get("type", "program")

    @property
    def language(self) -> str:
        return self.meta.get("language", "c")

    @property
    def files(self) -> List[str]:
        return self.meta["files"]

    @property
    def allowed(self) -> Optional[List[str]]:
        """Allowed external functions; None disables the check."""
        return self.meta.get("allowed_functions")

    @property
    def timeout(self) -> float:
        return float(self.meta.get("timeout", 2))

    @property
    def harness(self) -> List[Path]:
        return [self.path / h for h in self.meta.get("harness", [])]

    @property
    def cflags(self) -> List[str]:
        return list(self.meta.get("cflags", []))

    @property
    def ldflags(self) -> List[str]:
        return list(self.meta.get("ldflags", []))

    @property
    def variants(self) -> List[dict]:
        """Builds to test, e.g. several -D BUFFER_SIZE values. Each runs every case."""
        return self.meta.get("variants") or [{"name": "", "cflags": []}]

    @property
    def compare(self) -> str:
        """"exact" (default), "sorted_lines" or "numeric"."""
        return self.meta.get("compare", "exact")

    @property
    def tolerance(self) -> float:
        return float(self.meta.get("tolerance", 0.01))

    @property
    def leak_check(self) -> bool:
        return bool(self.meta.get("leak_check", False))

    @property
    def starter(self) -> List[Path]:
        """Files given to the student in subjects/ only (never used to build)."""
        return [self.path / p for p in self.meta.get("starter", [])]

    def collect_files(self, directory: Path):
        """Resolve `files` (which may contain *.c style patterns) in a directory.
        Returns (names found, required names missing)."""
        names: List[str] = []
        missing: List[str] = []
        for pattern in self.files:
            if any(ch in pattern for ch in "*?["):
                names += sorted(p.name for p in directory.glob(pattern) if p.is_file())
            elif (directory / pattern).is_file():
                names.append(pattern)
            else:
                missing.append(pattern)
        return list(dict.fromkeys(names)), missing

    @property
    def provided(self) -> List[Path]:
        """Files handed to the student (e.g. a header) and used for every build."""
        return [self.path / p for p in self.meta.get("provided", [])]

    @property
    def reference_dir(self) -> Path:
        return self.path / "reference"

    def subject(self) -> str:
        return (self.path / "subject.txt").read_text(encoding="utf-8")

    def cases(self, rng: random.Random) -> List[Case]:
        tests_file = self.path / "tests.py"
        spec = importlib.util.spec_from_file_location(
            f"mockexam_tests_{self.exam}_{self.level}_{self.name}", tests_file)
        if spec is None or spec.loader is None:
            raise ExerciseError(f"cannot load {tests_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "cases"):
            raise ExerciseError(f"{tests_file} must define cases(rng)")
        return [_to_case(raw, tests_file) for raw in module.cases(rng)]


def _quote(arg: str) -> str:
    """Shell-like double quoting with visible escapes (\\t, \\n, ...)."""
    escaped = arg.encode("unicode_escape").decode("ascii").replace('"', '\\"')
    return f'"{escaped}"'


def _to_case(raw, origin: Path) -> Case:
    if isinstance(raw, (list, tuple)):
        return Case(args=[str(a) for a in raw])
    if isinstance(raw, dict):
        return Case(args=[str(a) for a in raw.get("args", [])],
                    stdin=raw.get("stdin"), label=raw.get("label"))
    raise ExerciseError(f"{origin}: a case must be a list of args or a dict, got {raw!r}")


@dataclass
class Exam:
    name: str
    title: str
    duration_minutes: int
    reroll_on_fail: bool
    levels: List[List[Exercise]] = field(default_factory=list)

    def all_exercises(self) -> List[Exercise]:
        return [ex for level in self.levels for ex in level]

    def find(self, key: str) -> Optional[Exercise]:
        """Find by id ("level1/first_word") or by bare name ("first_word")."""
        for ex in self.all_exercises():
            if key in (ex.id, ex.name):
                return ex
        return None


def list_exams(exams_dir: Path) -> List[str]:
    return sorted(p.name for p in exams_dir.iterdir() if (p / "exam.json").is_file())


def load_exam(exams_dir: Path, name: str) -> Exam:
    exam_dir = exams_dir / name
    config = json.loads((exam_dir / "exam.json").read_text(encoding="utf-8"))
    exam = Exam(
        name=name,
        title=config.get("title", name),
        duration_minutes=int(config.get("duration_minutes", 180)),
        reroll_on_fail=bool(config.get("reroll_on_fail", False)),
    )
    for level in config["levels"]:
        level_dir = exam_dir / level
        exercises = [
            Exercise(name, level, d.name, d,
                     json.loads((d / "meta.json").read_text(encoding="utf-8")))
            for d in sorted(level_dir.iterdir())
            if (d / "meta.json").is_file()
        ]
        if not exercises:
            raise ExerciseError(f"{level_dir} contains no exercise")
        exam.levels.append(exercises)
    return exam
