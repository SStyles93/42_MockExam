#!/usr/bin/env python3
"""MockExam - a 42-style exam simulator.

    python3 exam.py                 resume the current session, or start an exam
    -e, --exam NAME                 start a new timed exam
    -p, --practice [EXERCISE]       untimed practice (full traces), optionally on one exercise
    -r, --restart                   fresh exam; old rendu/ and traces/ moved to archive/
    -c, --clear                     delete all exam data and archives, then fresh exam
    -l, --list                      list exams and exercises
    -t, --selftest                  check every reference solution passes its own tests
    -g, --git                       practice: grade only what was pushed (always on in exams)
    -y, --yes                       skip confirmation questions
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 8):
    sys.exit("MockExam needs Python 3.8 or newer")

import argparse
import os
import random
import shutil
import stat
import tempfile
import time
from pathlib import Path
from typing import Optional

from engine import ui, vcs
from engine.exercise import Exam, Exercise, ExerciseError, list_exams, load_exam
from engine.runner import Toolchain, grade, load_languages
from engine.session import Session

ROOT = Path(__file__).resolve().parent
EXAMS_DIR = ROOT / "exams"
RENDU_DIR = ROOT / "rendu"
SUBJECTS_DIR = ROOT / "subjects"
TRACES_DIR = ROOT / "traces"
ARCHIVE_DIR = ROOT / "archive"
SESSION_FILE = ROOT / ".session.json"
VOGSPHERE_DIR = ROOT / ".vogsphere"          # fake git server
REMOTE_REPO = VOGSPHERE_DIR / "rendu.git"

HELP = """\
  grademe        grade the current exercise (with git: only what was pushed)
  status         show level, exercise and remaining time
  subject        print the current subject
  help           show this help
  exit           leave (the session is saved; run exam.py again to resume)
practice mode only:
  next           switch to another random exercise
  pick NAME      switch to a given exercise
  list           list all exercises"""


class Shell:
    def __init__(self, exam: Exam, session: Session):
        self.exam = exam
        self.session = session
        self.toolchain = Toolchain.detect()
        self.languages = load_languages()

    # ------------------------------------------------------------- state --
    @property
    def practice(self) -> bool:
        return self.session["mode"] == "practice"

    @property
    def git(self) -> bool:
        return bool(self.session.get("git"))

    def current(self) -> Optional[Exercise]:
        key = self.session.get("exercise")
        return self.exam.find(key) if key else None

    def remaining(self) -> Optional[float]:
        deadline = self.session.get("deadline")
        return None if deadline is None else deadline - time.time()

    def points(self) -> int:
        return round(100 * self.session["level"] / len(self.exam.levels))

    def pick_random(self, pool, exclude: Optional[Exercise] = None) -> Exercise:
        choices = [ex for ex in pool if exclude is None or ex.id != exclude.id] or list(pool)
        return random.choice(choices)

    def assign(self, ex: Exercise) -> None:
        self.session["exercise"] = ex.id
        self.session["failures"] = 0
        self.session.save()
        if SUBJECTS_DIR.exists():
            shutil.rmtree(SUBJECTS_DIR)
        (SUBJECTS_DIR / ex.name).mkdir(parents=True)
        (SUBJECTS_DIR / ex.name / "subject.txt").write_text(ex.subject(), encoding="utf-8")
        for path in ex.provided + ex.starter:
            shutil.copy2(path, SUBJECTS_DIR / ex.name / path.name)
        (RENDU_DIR / ex.name).mkdir(parents=True, exist_ok=True)
        print()
        print(ui.bold(f"New assignment: {ex.name}") + ui.dim(f"  ({ex.level})"))
        print(f"  subject : {self.rel(SUBJECTS_DIR / ex.name / 'subject.txt')}")
        print(f"  rendu   : {self.rel(RENDU_DIR / ex.name)}/  ->  {', '.join(ex.files)}")

    @staticmethod
    def rel(path: Path) -> str:
        try:
            return str(path.relative_to(Path.cwd()))
        except ValueError:
            return str(path)

    # ---------------------------------------------------------- commands --
    def cmd_status(self, _arg: str = "") -> None:
        ex = self.current()
        print(ui.rule())
        print(f"  {ui.bold(self.exam.title)}  [{'practice' if self.practice else 'exam'}]"
              + ("  [git: push before grademe]" if self.git else ""))
        if not self.practice:
            level = min(self.session["level"] + 1, len(self.exam.levels))
            print(f"  level    : {level}/{len(self.exam.levels)}"
                  f"   points: {self.points()}/100")
            remaining = self.remaining()
            if remaining is not None:
                color = ui.red if remaining < 600 else ui.cyan
                print(f"  time left: {color(ui.duration(remaining))}")
        if self.session.get("finished"):
            print(f"  {ui.green('Exam finished.')}")
        elif ex:
            print(f"  exercise : {ui.bold(ex.name)} ({ex.level}),"
                  f" failed attempts: {self.session.get('failures', 0)}")
        print(ui.rule())

    def cmd_subject(self, _arg: str = "") -> None:
        ex = self.current()
        if ex:
            print(ex.subject())

    def cmd_help(self, _arg: str = "") -> None:
        print(HELP)

    def cmd_list(self, _arg: str = "") -> None:
        for i, level in enumerate(self.exam.levels, 1):
            print(f"  level {i}: " + ", ".join(ex.name for ex in level))

    def cmd_next(self, _arg: str = "") -> None:
        if not self.practice:
            print("Only available in practice mode.")
            return
        self.assign(self.pick_random(self.exam.all_exercises(), exclude=self.current()))

    def cmd_pick(self, arg: str) -> None:
        if not self.practice:
            print("Only available in practice mode.")
            return
        ex = self.exam.find(arg.strip())
        if ex is None:
            print(f"Unknown exercise '{arg.strip()}'. Type 'list'.")
            return
        self.assign(ex)

    def cmd_grademe(self, _arg: str = "") -> None:
        if self.session.get("finished"):
            print("The exam is over. Run exam.py -r to start again.")
            return
        remaining = self.remaining()
        if remaining is not None and remaining <= 0:
            print(ui.red("Time is up!"))
            self.finish()
            return
        ex = self.current()
        if ex is None:
            return
        try:
            answer = input(f"Submit {ex.name} for grading? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            return

        print(ui.dim("Grading..."))
        result = self.grade_submission(ex)
        self.session["grademes"] = self.session.get("grademes", 0) + 1
        for note in result.notes:
            print(ui.yellow(f"note: {note}"))

        if result.internal:
            print(ui.yellow(f"Exercise/toolchain problem (not counted): {result.summary}"))
            if result.trace:
                print(result.trace)
            self.session.save()
            return

        trace_file = self.write_trace(ex, result)
        if result.passed:
            print(ui.green(f">>>>>>>>>> SUCCESS <<<<<<<<<<  {result.summary}"))
            self.on_success(ex)
        else:
            print(ui.red(f">>>>>>>>>> FAILURE <<<<<<<<<<  {result.summary}"))
            if self.practice:
                print(result.trace)
            else:
                print(f"Trace: {self.rel(trace_file)}")
            self.on_failure(ex)
        self.session.save()

    def grade_submission(self, ex: Exercise):
        seed = random.randrange(1 << 30)
        where = f"rendu/{ex.name}"
        if not self.git:
            return grade(ex, RENDU_DIR / ex.name, self.toolchain, self.languages,
                         seed=seed, where=where)
        # like the real exam: only what was pushed counts, silently
        with tempfile.TemporaryDirectory(prefix="mockexam-pushed-") as tmp:
            pushed = Path(tmp) / ex.name
            vcs.export_pushed(REMOTE_REPO, ex.name, pushed)
            return grade(ex, pushed, self.toolchain, self.languages,
                         seed=seed, where=where)

    def setup_git(self) -> None:
        if not self.git:
            return
        if not vcs.git_available():
            print(ui.yellow("warning: git not found; grading the files in rendu/ directly."))
            self.session["git"] = False
            self.session.save()
            return
        vcs.init(RENDU_DIR, REMOTE_REPO)

    def write_trace(self, ex: Exercise, result) -> Path:
        TRACES_DIR.mkdir(exist_ok=True)
        path = TRACES_DIR / f"{self.session['grademes']:03d}-{ex.name}.trace"
        header = (f"{ex.name} | {'PASSED' if result.passed else 'FAILED'} | {result.summary}\n"
                  f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        path.write_text(header + result.trace + "\n", encoding="utf-8")
        return path

    def on_success(self, ex: Exercise) -> None:
        if self.practice:
            print("Type 'next' for another exercise, or 'pick NAME'.")
            return
        self.session["level"] += 1
        self.session["passed"] = self.session.get("passed", []) + [ex.id]
        if self.session["level"] >= len(self.exam.levels):
            self.finish()
        else:
            print(f"Level up! points: {self.points()}/100")
            self.assign(self.pick_random(self.exam.levels[self.session["level"]]))

    def on_failure(self, ex: Exercise) -> None:
        self.session["failures"] = self.session.get("failures", 0) + 1
        if not self.practice and self.exam.reroll_on_fail:
            self.assign(self.pick_random(self.exam.levels[self.session["level"]], exclude=ex))

    def finish(self) -> None:
        self.session["finished"] = True
        self.session.save()
        print(ui.bold(f"Exam finished. Final grade: {self.points()}/100"))

    # -------------------------------------------------------------- loop --
    def run(self) -> None:
        if self.toolchain.cc is None:
            print(ui.yellow("warning: no C compiler found (cc/gcc/clang). Set CC=... or use WSL."))
        elif sys.platform == "win32":
            print(ui.yellow("warning: native Windows lacks POSIX headers (unistd.h); "
                            "run MockExam from WSL for C exams."))
        self.setup_git()
        if self.git:
            print(ui.bold("rendu/ is a git repository: git add, git commit and git push "
                          "your work. Only what is pushed is graded."))
        if self.current() is None and not self.session.get("finished"):
            pool = (self.exam.all_exercises() if self.practice
                    else self.exam.levels[self.session["level"]])
            self.assign(self.pick_random(pool))
        self.cmd_status()
        print("Type 'help' for commands.")
        commands = {
            "grademe": self.cmd_grademe, "status": self.cmd_status,
            "subject": self.cmd_subject, "help": self.cmd_help,
            "next": self.cmd_next, "pick": self.cmd_pick, "list": self.cmd_list,
        }
        while True:
            try:
                line = input(ui.cyan("examshell> ")).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            name, _, arg = line.partition(" ")
            if name in ("exit", "quit", "finish"):
                break
            handler = commands.get(name)
            if handler is None:
                print(f"Unknown command '{name}'. Type 'help'.")
                continue
            try:
                handler(arg)
            except KeyboardInterrupt:
                print(ui.yellow("\ninterrupted"))
        self.session.save()
        print("Session saved. Run exam.py again to resume.")


# ------------------------------------------------------------------ CLI --
def choose_exam(requested: Optional[str]) -> str:
    exams = list_exams(EXAMS_DIR)
    if not exams:
        sys.exit("No exam found in exams/.")
    if requested:
        if requested not in exams:
            sys.exit(f"Unknown exam '{requested}'. Available: {', '.join(exams)}")
        return requested
    if len(exams) == 1:
        return exams[0]
    for i, name in enumerate(exams, 1):
        print(f"  {i}) {name}")
    while True:
        try:
            answer = input("Choose an exam: ").strip()
        except EOFError:
            sys.exit(1)
        if answer.isdigit() and 1 <= int(answer) <= len(exams):
            return exams[int(answer) - 1]
        if answer in exams:
            return answer


def ask(question: str) -> bool:
    try:
        return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def confirm_overwrite(existing: Optional[Session], yes: bool) -> None:
    if existing and not existing.get("finished") and not yes:
        if not ask(f"A session is in progress ({existing['exam']}, {existing['mode']} mode). "
                   "Abandon it?"):
            sys.exit(0)


def archive_workspace() -> Optional[Path]:
    """Move rendu/ and traces/ aside so a restart begins with an empty rendu/,
    without ever deleting the student's code."""
    for d in (SUBJECTS_DIR, VOGSPHERE_DIR):  # rendu/.git keeps everything that was pushed
        if d.exists():
            _rmtree(d)
    to_move = [d for d in (RENDU_DIR, TRACES_DIR)
               if d.exists() and any(p.is_file() and ".git" not in p.relative_to(d).parts
                                     for p in d.rglob("*"))]
    for d in (RENDU_DIR, TRACES_DIR):
        if d.exists() and d not in to_move:
            _rmtree(d)  # only empty dirs (and .git) left
    if not to_move:
        return None
    dest = ARCHIVE_DIR / time.strftime("%Y%m%d-%H%M%S")
    dest.mkdir(parents=True, exist_ok=True)
    for d in to_move:
        shutil.move(str(d), str(dest / d.name))
    return dest


def _rmtree(path: Path) -> None:
    """rmtree that also removes read-only files (git objects block deletion on Windows)."""
    def force(func, target, _exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=force)
    else:
        shutil.rmtree(path, onerror=force)


WORKSPACE_DIRS = (RENDU_DIR, SUBJECTS_DIR, TRACES_DIR, ARCHIVE_DIR, VOGSPHERE_DIR)


def confirm_clear(yes: bool) -> bool:
    present = [d.name + "/" for d in WORKSPACE_DIRS if d.exists()]
    if yes or (not present and not SESSION_FILE.exists()):
        return True
    print(ui.yellow("This permanently deletes: " + (", ".join(present) or "the saved session")))
    print(ui.yellow("including all your code in rendu/ and archive/."))
    return ask("Continue?")


def clear_workspace() -> None:
    """Delete every runtime file MockExam created (never touches exams/)."""
    for d in WORKSPACE_DIRS:
        if d.exists():
            _rmtree(d)
    SESSION_FILE.unlink(missing_ok=True)


def selftest() -> int:
    toolchain, languages = Toolchain.detect(), load_languages()
    failures = 0
    for exam_name in list_exams(EXAMS_DIR):
        exam = load_exam(EXAMS_DIR, exam_name)
        for ex in exam.all_exercises():
            result = grade(ex, ex.reference_dir, toolchain, languages, seed=42)
            status = ui.green("OK  ") if result.passed else ui.red("FAIL")
            print(f"{status} {exam_name}/{ex.id}: {result.summary}")
            for note in result.notes:
                print(ui.yellow(f"     note: {note}"))
            if not result.passed:
                failures += 1
                if result.trace:
                    print(result.trace)
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="42-style exam simulator. Without options: resume the current "
                    "session, or start a new exam.")
    command = parser.add_mutually_exclusive_group()
    command.add_argument("-r", "--restart", action="store_true",
                         help="start a fresh exam; old rendu/ and traces/ go to archive/")
    command.add_argument("-c", "--clear", action="store_true",
                         help="delete all exam data and archives, then start a fresh exam")
    command.add_argument("-l", "--list", action="store_true",
                         help="list exams and exercises")
    command.add_argument("-t", "--selftest", action="store_true",
                         help="check every reference solution passes its own tests")
    parser.add_argument("-e", "--exam", metavar="NAME",
                        help="exam to use (e.g. rank02); alone, starts a new timed exam")
    parser.add_argument("-p", "--practice", nargs="?", const="", metavar="EXERCISE",
                        help="untimed practice mode, optionally on a given exercise")
    parser.add_argument("-g", "--git", action="store_true",
                        help="practice mode: grade only what was pushed (always on in exams)")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="skip confirmation questions")
    args = parser.parse_args()
    if (args.list or args.selftest) and (args.exam or args.practice is not None
                                         or args.yes or args.git):
        parser.error("-l/--list and -t/--selftest take no other option")
    if args.git and args.practice is None:
        parser.error("-g/--git is for practice mode (-p); exams always use git")

    try:
        if args.selftest:
            return selftest()
        if args.list:
            for name in list_exams(EXAMS_DIR):
                exam = load_exam(EXAMS_DIR, name)
                print(ui.bold(f"{name}: {exam.title} ({exam.duration_minutes} min)"))
                for i, level in enumerate(exam.levels, 1):
                    print(f"  level {i}: " + ", ".join(ex.name for ex in level))
            return 0

        existing = Session.load(SESSION_FILE)
        previous_exam = existing["exam"] if existing else None
        if args.clear:
            if not confirm_clear(args.yes):
                return 0
            clear_workspace()
            existing = None
            print("All exam data and archives deleted.")
        elif args.restart:
            if existing:
                existing.clear()
                existing = None
            archived = archive_workspace()
            if archived:
                print(ui.dim(f"Previous rendu/ and traces/ moved to {Shell.rel(archived)}/"))

        if args.practice is not None:
            confirm_overwrite(existing, args.yes)
            exam = load_exam(EXAMS_DIR, choose_exam(args.exam or previous_exam))
            first = exam.find(args.practice) if args.practice else None
            if args.practice and first is None:
                sys.exit(f"Unknown exercise '{args.practice}'. Try -l.")
            session = Session.new(SESSION_FILE, exam=exam.name, mode="practice",
                                  level=0, deadline=None, exercise=None, git=args.git)
            shell = Shell(exam, session)
            if first:
                shell.assign(first)
            shell.run()
            return 0
        elif args.exam or existing is None or existing.get("finished"):
            if args.exam:
                confirm_overwrite(existing, args.yes)
            exam = load_exam(EXAMS_DIR, choose_exam(args.exam or previous_exam))
            session = Session.new(SESSION_FILE, exam=exam.name, mode="exam", level=0,
                                  deadline=time.time() + exam.duration_minutes * 60,
                                  exercise=None, git=True)
            print(ui.bold(f"Starting {exam.title}: {exam.duration_minutes} minutes, "
                          f"{len(exam.levels)} level(s). Good luck!"))
        else:
            session = existing
            exam = load_exam(EXAMS_DIR, session["exam"])
            print(ui.dim("Resuming saved session."))

        Shell(exam, session).run()
        return 0
    except ExerciseError as exc:
        print(ui.red(f"Broken exercise definition: {exc}"))
        return 2


if __name__ == "__main__":
    sys.exit(main())
