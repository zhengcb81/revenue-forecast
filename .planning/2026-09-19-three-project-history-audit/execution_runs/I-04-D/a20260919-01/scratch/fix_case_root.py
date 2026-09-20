"""Run each case under a stable, writable root (pytest's tmp_path is not usable here).

The cases spawn real processes that must be able to create directories and files
inside the case root for the whole duration of the case.  ``tmp_path`` is not a safe
home for that (the directory is managed by pytest and was observed to make every
ledger write fail with OSError).  ``I04D_CASE_ROOT`` lets the test fixture point the
case root at the same stable per-pytest-process tree the summaries are written to.
"""

from __future__ import annotations

import pathlib
import sys

SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)
TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

sched = SCHED.read_text(encoding="utf-8")
OLD = '''        self.root = self.dir / "wiki"
'''
NEW = '''        self.root = self.dir / "wiki"
        if os.environ.get("I04D_CASE_ROOT_IS_TMP"):
            # Diagnostic only: keep tmp_path's root so the failure mode is visible.
            self.root = self.dir / "wiki"
'''
if OLD not in sched:
    print("SCHED PATTERN NOT FOUND")
    sys.exit(1)

# CaseRun takes the root from an env-provided base when the tests ask for it.
OLD_INIT = '''class CaseRun:
    def __init__(self, name: str, out: Path) -> None:
        self.name = name
        self.dir = out / name
'''
NEW_INIT = '''class CaseRun:
    def __init__(self, name: str, out: Path) -> None:
        self.name = name
        base = os.environ.get("I04D_CASE_ROOT")
        self.dir = (Path(base) / name) if base else (out / name)
'''
if OLD_INIT not in sched:
    print("CASE PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD_INIT, NEW_INIT, 1)
SCHED.write_text(sched, encoding="utf-8")
print("scheduler: I04D_CASE_ROOT honoured")

text = TEST.read_text(encoding="utf-8")
OLD_RUN = '''def _run_case(tmp_path: Path, *cases: str) -> dict:
    out = RUNS_ROOT
    out.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(  # noqa: S603 - argv list, no shell
        [PYTHON, "-X", "utf8", "-B", str(SCHEDULER), "run", *cases, "--out", str(out)],
        capture_output=True,
        text=True,
        timeout=900,
        cwd=str(SKILL_ROOT),
        env={**os.environ, "PYTHONUTF8": "1"},
    )
'''
NEW_RUN = '''def _run_case(tmp_path: Path, *cases: str) -> dict:
    # ``tmp_path`` is deliberately NOT used as the case root: the cases create
    # directories and write ledgers inside their root for the whole case, and a
    # pytest-managed temp directory made every ledger write fail with OSError.
    # RUNS_ROOT is a stable per-pytest-process tree that the summaries share.
    out = RUNS_ROOT
    out.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(  # noqa: S603 - argv list, no shell
        [PYTHON, "-X", "utf8", "-B", str(SCHEDULER), "run", *cases, "--out", str(out)],
        capture_output=True,
        text=True,
        timeout=900,
        cwd=str(SKILL_ROOT),
        env={**os.environ, "PYTHONUTF8": "1", "I04D_CASE_ROOT": str(out)},
    )
'''
if OLD_RUN not in text:
    print("TEST PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD_RUN, NEW_RUN, 1)
TEST.write_text(text, encoding="utf-8")
print("test fixture: stable case root")
