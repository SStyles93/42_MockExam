# 42_MockExam

A 42-style exam simulator for training before the real exam: random exercise per level, a countdown timer, `grademe`, and traces when you fail.

Pure Python 3.8+ with the **standard library only**. Nothing to install: clone and run.

## Usage

```
python3 exam.py [options]
```

Without options it resumes the current session, or starts a new exam.

| Short | Long | |
|---|---|---|
| `-e NAME` | `--exam NAME` | start a new timed exam (e.g. `-e rank02`) |
| `-p [EX]` | `--practice [EX]` | untimed practice, full traces printed on failure |
| `-r` | `--restart` | fresh exam; old `rendu/` and `traces/` moved to `archive/` |
| `-c` | `--clear` | delete all exam data and archives, then a fresh exam (asks first) |
| `-l` | `--list` | list exams and exercises |
| `-t` | `--selftest` | check every reference solution passes its own tests |
| `-g` | `--git` | practice mode: grade only what was pushed (always on in exams) |
| `-y` | `--yes` | skip confirmation questions |
| | `--no-update` | do not update MockExam before starting |
| `-h` | `--help` | show help |

`-r`, `-c`, `-l` and `-t` are commands and cannot be combined with each other. `-e`, `-p`, `-g` and `-y` modify them:

```
python3 exam.py -r -p               # restart into practice mode
python3 exam.py -p ft_strlen        # practice a given exercise
python3 exam.py -p -g               # practice, with the git push workflow
python3 exam.py -c -y -e rank02     # clear without asking, start rank02
```

**Automatic update:** when MockExam was installed with `git clone`, every launch first runs `git pull --ff-only` (15 s max, never asks for a password) and restarts on the new version if anything changed. Being offline, having local edits or a diverged branch only prints a one-line note and the current version runs. Your work (`rendu/`, `traces/`, `archive/`, ...) is git-ignored and never touched. Disable with `--no-update` or `MOCKEXAM_NO_UPDATE=1`.

Inside the shell:

| Command | |
|---|---|
| `grademe` | submit the current exercise |
| `status` | level, exercise, time left, points |
| `subject` | print the subject |
| `next` / `pick NAME` / `list` | practice mode only: change exercise |
| `exit` | leave; the session is saved and resumes on the next launch |

While the exam runs:

```
subjects/<exercise>/subject.txt   # read this
rendu/<exercise>/<files>          # write your code here
traces/NNN-<exercise>.trace       # written after each grademe
```

### Git, like the real exam

In exam mode (and practice with `-g`), `rendu/` is a git repository whose remote is a local "fake vogsphere" (`.vogsphere/rendu.git`). As at 42, **only what was pushed is graded**:

```
cd rendu
git add ft_strlen/ft_strlen.c
git commit -m "ft_strlen"
git push
```

Forgotten files, uncommitted edits and unpushed commits fail silently, exactly like the real exam: the trace just says the file was not found. If `git` is not installed, the files in `rendu/` are graded directly.

Restarting (`-r`) moves your previous `rendu/` and `traces/` to `archive/<date>/`, so the new exam starts with an empty `rendu/` and no code is ever deleted. Clearing (`-c`) asks for confirmation (unless `-y`), then permanently deletes all of it, archives included.

In **exam mode** a failure only tells you where the trace is (like the real exam). In **practice mode** the trace is printed directly.

## Requirements

| Tool | Notes |
|---|---|
| Python 3.8+ | standard library only |
| `cc` / `gcc` / `clang` | for C exams (override with `CC=...`) |
| `git` | for the push-to-submit workflow; skipped with a note if missing |
| `nm` | for the allowed-functions check (override with `NM=...`); skipped with a note if missing |
| `valgrind` | optional, for leak checks (rank03 `broken_gnl`); skipped with a note if missing |
| Linux / macOS / WSL | native Windows lacks POSIX headers such as `unistd.h`; `filter`'s short-read test is Linux-only |

## Exams

| Exam | Levels | Exercises |
|---|---|---|
| `rank02` | 4 | 55 (12 / 18 / 15 / 10) |
| `rank03` | 2 | 8: `broken_gnl`, `filter`, `ft_scanf` / `n_queens`, `permutations`, `powerset`, `rip`, `tsp` |

## How grading works

1. Only the expected files are copied from `rendu/<exercise>/` (with git: from the pushed commit) to a temp directory.
2. Your code is compiled with `-Wall -Wextra -Werror`, together with the harness for function exercises.
3. The object files are checked with `nm`: any external symbol not in `allowed_functions` fails the exercise. Compiler substitutions are tolerated (`printf` allows `puts`/`putchar`).
4. The **reference solution** is built and both programs run on the same test cases: fixed edge cases plus random ones. stdout and exit code must match (exactly, or per the exercise's `compare` mode), and crashes and timeouts are reported.
5. Exercises that require it are rebuilt with several flags (e.g. each `BUFFER_SIZE`) and checked for leaks with valgrind.

Expected outputs are never written by hand: the reference solution *is* the expectation.

## Adding an exercise

```
exams/rank02/
├── exam.json                  # title, duration, levels, reroll_on_fail
└── level1/
    └── first_word/
        ├── meta.json          # type, language, files, allowed_functions, harness, timeout
        ├── subject.txt        # shown to the student
        ├── tests.py           # def cases(rng): -> list of cases
        ├── reference/         # a correct solution, same file names as "files"
        │   └── first_word.c
        └── main.c             # harness (function exercises only)
```

`meta.json`:

```json
{
  "type": "function",
  "language": "c",
  "files": ["ft_strlen.c"],
  "harness": ["main.c"],
  "allowed_functions": [],
  "timeout": 2
}
```

| Key | Meaning |
|---|---|
| `type` | `function` or `program` |
| `language` | an entry of `engine/languages.json` (default `c`) |
| `files` | expected files; patterns allowed (`["*.c", "*.h"]`) |
| `allowed_functions` | `[]` means none allowed; omit the key to disable the check |
| `harness` | extra sources compiled with both the submission and the reference: a `main.c` calling the function, or e.g. a `read()` wrapper for a program |
| `provided` | files given to the student **and** always used to build (e.g. a header they must not turn in) |
| `starter` | files only given to the student in `subjects/` (code to complete or repair, example inputs) |
| `cflags` / `ldflags` | extra compiler / linker flags (e.g. `["-lm"]`) |
| `variants` | several builds, each running every test: `[{"name": "BUFFER_SIZE=1", "cflags": ["-DBUFFER_SIZE=1"]}, ...]` |
| `compare` | `exact` (default), `sorted_lines` (line order does not matter) or `numeric` (with `tolerance`, default 0.01) |
| `leak_check` | run the first test cases under valgrind and fail on definite/indirect leaks |
| `timeout` | seconds per run (default 2) |

`tests.py` files can import random-input helpers from `engine/testgen.py` (`sentence`, `word`, `text`, ...).

`tests.py` returns a list of cases. Each case is a list of arguments, or a dict:

```python
def cases(rng):                       # rng is a seeded random.Random
    return [
        [],                                        # ./a.out
        ["hello world"],                           # ./a.out "hello world"
        {"args": ["x"], "stdin": "input\n"},       # with stdin
        {"args": ["abc"], "label": 'ft_strlen("abc")'},  # custom trace label
    ] + [[random_word(rng)] for _ in range(40)]
```

Add the level directory to `levels` in `exam.json`, then run `python3 exam.py -t`.

## Other languages

Languages are defined in `engine/languages.json` as build/run command templates. Python is already supported: set `"language": "python"` in `meta.json`, with `files` naming the script. Adding a language means adding an entry; the engine code stays the same.
