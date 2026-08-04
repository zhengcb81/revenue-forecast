"""Run the revenue test suite with per-module coverage gates.

Phase 6 C1 (F-07): the historical quality gate only asserted a single total
``fail-under`` (84%), which let newly added modules (e.g. the filing-fetch
client CLI) ship with near-zero direct coverage because subprocess invocations
were invisible to the coverage run.  This driver:

* enables subprocess coverage (``COVERAGE_PROCESS_START``) so ``python
  scripts/*.py`` calls made inside tests are measured;
* combines the per-process data files;
* asserts a minimum per-module statement coverage for the core modules.

Exit code is non-zero when any gate fails, so it can be used as a CI check.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RC = ROOT / ".coveragerc"

# Module -> minimum statement coverage % (Phase 6 C1).
PER_MODULE_MINIMUM = {
    "scripts/revenue_core.py": 70,
    "scripts/revenue_report.py": 70,
    "scripts/revenue_publication.py": 70,
    "scripts/revenue_backtest.py": 70,
    "scripts/filing_fetch_client.py": 40,
    "scripts/company_wiki_source.py": 60,
    "scripts/model_registry.py": 80,
    "scripts/revenue_forecast.py": 60,
}


def main() -> int:
    env = dict(os.environ)
    env["COVERAGE_PROCESS_START"] = str(RC)
    subprocess.run(
        [sys.executable, "-m", "coverage", "erase"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--rcfile",
            str(RC),
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "coverage", "combine", "--rcfile", str(RC)],
        cwd=ROOT,
        check=True,
    )
    report = subprocess.run(
        [sys.executable, "-m", "coverage", "report", "--rcfile", str(RC)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    print(report.stdout)
    failed: list[str] = []
    report_rows = [row.replace("\\", "/") for row in report.stdout.splitlines()]
    for path, minimum in PER_MODULE_MINIMUM.items():
        line = next(
            (row for row in report_rows if row.lstrip().startswith(path)),
            None,
        )
        if line is None:
            failed.append(f"{path}: not measured")
            continue
        # Coverage report columns (--branch): Name, Stmts, Miss, Branch,
        # BrPart, Cover(%).  The cover percentage is the sixth token.
        parts = [p for p in line.split() if p]
        try:
            percent = float(parts[5].rstrip("%"))
        except (IndexError, ValueError):
            failed.append(f"{path}: cannot parse {line!r}")
            continue
        if percent < minimum:
            failed.append(f"{path}: {percent:.0f}% < {minimum}%")
    if report.returncode != 0:
        failed.append("total coverage below fail_under")
    if failed:
        print("PER-MODULE COVERAGE FAILURES:")
        for item in failed:
            print(f"  {item}")
        return 1
    print("PER-MODULE COVERAGE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
