"""ZR-903 mutation check: are the weekly-T3 harness tests load-bearing?

Companion to the ZR-903 change set (F-B01-10 + the B.VR-zr903 review dispositions).
Each mutant reverts ONE property the tests claim to protect; the named case must fail.
Run with the repo clean or dirty - the file is restored from captured bytes, never from
git, so an uncommitted change under test survives.

    python zr903_mutations.py [path-to-revenue-forecast]

Prints one line per mutant and a JSON summary on the last line.  Exit 0 = all killed
and the tool file is byte-identical to what it was.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
TOOL = "tools/weekly_t3_schedule.py"
TEST_FILE = "tests/test_zr903_weekly_t3.py"

MUTANTS: list[tuple[str, str, str, str]] = [
    (
        "P1: the persisted report is never written (call replaced by the bare label)",
        "    report = _write_suite_report(ledger_path, run_id, proc, ok, status, detail)",
        '    report = f"weekly-run-{run_id}"',
        "test_c1_suite_output_is_persisted_and_the_ledger_names_a_real_file",
    ),
    (
        "P2: the ledger records the old label instead of the report file name",
        "    write_ledger(ledger_path, run_id, started, triplet, ok, report)",
        '    write_ledger(ledger_path, run_id, started, triplet, ok, f"weekly-run-{run_id}")',
        "test_c1_suite_output_is_persisted_and_the_ledger_names_a_real_file",
    ),
    (
        "P3: an unwritable report propagates instead of being recorded",
        "    except OSError as exc:  # a diagnostic file must never break the assurance run",
        "    except ZeroDivisionError as exc:  # mutant: OSError no longer caught",
        "test_c1_report_write_failure_never_breaks_the_assurance_run",
    ),
    (
        "P4: the environment marker is no longer required (any no-verdict failure is blocked)",
        "        markers = [m for m in ENVIRONMENT_MARKERS if m in lowered]",
        "        markers = ['forced']",
        "test_c3_an_ambiguous_collection_error_stays_not_ok",
    ),
    (
        "P5: verdicts are never detected (a real failure looks like nothing evaluated)",
        "    return any(int(count) > 0 for count in VERDICT_COUNTS.findall(out))",
        "    return False",
        "test_c3_a_failing_test_is_never_laundered_into_blocked",
    ),
    (
        "P6: exit 0 with no verdict count is treated as a pass (rule 1 deleted)",
        "        if not _tests_reached_a_verdict(out):\n"
        "            return False, \"blocked\", (\n"
        "                \"T3 suite exited 0 but reported no test result (nothing was evaluated)\"\n"
        "            )\n",
        "",
        "test_c5_exit_zero_without_a_verdict_is_blocked",
    ),
    (
        "P7: the explicit sentinel is ignored",
        "    if ENVIRONMENT_SENTINEL.lower() in lowered:",
        "    if False:",
        "test_c5_the_sentinel_beats_every_heuristic",
    ),
    (
        "P8: language-neutral markers are removed (the localized WinError cases)",
        '    "filenotfounderror",\n    "winerror 2",\n    "errno 2",\n',
        "",
        "test_c5_a_localized_missing_tool_is_blocked_not_not_ok"
        " or test_c5_a_bare_localized_os_error_code_is_enough",
    ),
    (
        "P9: a crash/timeout is no longer recorded as a run",
        "    except (subprocess.TimeoutExpired, OSError) as exc:",
        "    except ZeroDivisionError as exc:",
        "test_c5_a_crash_is_recorded_as_a_run",
    ),
    (
        "P10: a blocked run returns the suite's exit code (0 for all-skipped)",
        "    if status != \"ok\":\n"
        "        # Task Scheduler must not record a success for a run that could not\n"
        "        # establish the gate (an all-skipped suite exits 0 on its own).\n"
        "        return proc.returncode or 1\n",
        "",
        "test_c5_a_blocked_run_exits_non_zero_even_when_pytest_exited_zero",
    ),
    (
        "P11: the report records the real argv (machine profile in a tracked file)",
        '    argv = [Path(sys.argv[0]).name, *sys.argv[1:]]',
        "    argv = sys.argv",
        "test_c5_the_persisted_report_does_not_leak_the_machine_profile",
    ),
    (
        "P12: run ids may collide (no suffix when the ledger already has that id)",
        "    previous = (read_ledger(ledger_path) or {}).get(\"latest_run_id\")\n"
        "    if previous != base:\n        return base\n",
        "    return base\n",
        "test_c5_a_second_run_in_the_same_second_gets_a_distinct_id",
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
                errors="replace", timeout=900,
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
        errors="replace", timeout=900,
    )
    summary = {
        "repo": str(repo),
        "mutants": len(MUTANTS),
        "survived": failures,
        "all_killed": failures == 0,
        "tree_restored": restored,
        "baseline_exit": baseline.returncode,
        "baseline_tail": baseline.stdout.strip().splitlines()[-1] if baseline.stdout else "",
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["all_killed"] and restored and baseline.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
