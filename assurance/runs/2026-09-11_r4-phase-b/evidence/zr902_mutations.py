"""ZR-902 mutation check: is the daily outcome split load-bearing?

Companion to the owner decision of 2026-09-13 (the daily T2 loop gets the same
blocked/not-ok split as the weekly T3 loop).  Each mutant reverts ONE property; the
named case must fail.  The tool file is restored from captured bytes, never from git.

    python zr902_mutations.py [path-to-revenue-forecast]

Exit 0 = every mutant killed, the file byte-identical, and the new file green.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
TOOL = "tools/daily_t2_schedule.py"
TEST_FILE = "tests/test_zr902b_run_outcome.py"

MUTANTS: list[tuple[str, str, str, str]] = [
    (
        "M1: environment markers are never consulted (every failure blames the product)",
        "    markers = [marker for marker in ENVIRONMENT_MARKERS if marker in lowered]",
        "    markers = []  # mutant",
        "test_zr902b_no_report_with_environment_evidence_is_blocked",
    ),
    (
        "M1b: the daily vocabulary drifts from the weekly one",
        'ENVIRONMENT_MARKERS = (\n    "not found",',
        'ENVIRONMENT_MARKERS = (\n    "zzz-drifted",',
        "test_zr902b_the_daily_and_weekly_vocabularies_are_identical",
    ),
    (
        "M2: a report with problems is ignored (bad health reads as blocked)",
        '    if report is not None:\n'
        '        problems = report.get("problems") or []',
        '    if False:\n'
        '        problems = report.get("problems") or []',
        "test_zr902b_a_verdict_of_bad_health_is_not_ok",
    ),
    (
        "M3: an observer failure is blamed on the environment",
        '        return False, "not-ok", (\n'
        '            f"observation period failed (exit {obs.returncode}) while the T2 run itself "',
        '        return False, "blocked", (\n'
        '            f"observation period failed (exit {obs.returncode}) while the T2 run itself "',
        "test_zr902b_an_observer_failure_is_never_blamed_on_the_environment",
    ),
    (
        "M4: the sentinel is not authoritative",
        "    if ENVIRONMENT_SENTINEL.lower() in lowered:",
        "    if False:",
        "test_zr902b_the_sentinel_is_authoritative",
    ),
    (
        "M5: an unexplained crash is called blocked (the unconservative direction)",
        '    return False, "not-ok", (\n'
        '        f"T2 runner failed without a report (exit {proc.returncode}) and the output "\n'
        '        f"carries no environment marker"\n'
        '    )',
        '    return False, "blocked", (\n'
        '        f"T2 runner failed without a report (exit {proc.returncode}) and the output "\n'
        '        f"carries no environment marker"\n'
        '    )',
        "test_zr902b_no_report_and_no_marker_stays_not_ok",
    ),
]


def main(argv: list[str]) -> int:
    repo = Path(argv[1]) if len(argv) > 1 else DEFAULT_REPO
    tool_path = repo / TOOL
    original_bytes = tool_path.read_bytes()
    original = original_bytes.decode("utf-8")
    failures = 0
    try:
        for label, old, new, case in MUTANTS:
            if old not in original:
                print(f"STALE  {label}: pattern not found - harness is out of date")
                return 2
            tool_path.write_bytes(original.replace(old, new, 1).encode("utf-8"))
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-k", case, TEST_FILE],
                cwd=str(repo), capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=600,
            )
            killed = proc.returncode != 0
            failures += 0 if killed else 1
            print(f"{'KILLED' if killed else 'SURVIVED'}  {label} (exit={proc.returncode})")
            tool_path.write_bytes(original_bytes)
    finally:
        tool_path.write_bytes(original_bytes)

    restored = tool_path.read_bytes() == original_bytes
    baseline = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", TEST_FILE],
        cwd=str(repo), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600,
    )
    summary = {
        "repo": str(repo), "mutants": len(MUTANTS), "survived": failures,
        "all_killed": failures == 0, "tree_restored": restored,
        "baseline_exit": baseline.returncode,
        "baseline_tail": baseline.stdout.strip().splitlines()[-1] if baseline.stdout else "",
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["all_killed"] and restored and baseline.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
