"""FC-1103: weekly T3 runner contracts.

SCENARIO: AUD-06 (weekly T3; blocked is an alert, never a silent green)

The runner must (a) exit BLOCKED (2) without --force — T3 real-provider
download is never silently green, (b) with --force run the FC-805 suite
(skipped -> blocked; passed -> 0; failed -> 1), (c) write an isolated
report, (d) never touch the production catalog.

The forced child is mocked here: ordinary CI verifies dispatch and status
mapping without making live provider requests. Real T3 remains an explicit run.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "tools" / "weekly_t3_runner.py"
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
import weekly_t3_runner  # noqa: E402


def _run(report_root: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--report-root", str(report_root),
         *extra],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )


class TestWeeklyT3Runner(unittest.TestCase):
    def test_without_force_is_blocked(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            proc = _run(Path(td))
            self.assertEqual(proc.returncode, 2, "un-authorized T3 must be BLOCKED")
            self.assertIn("BLOCKED", proc.stderr)
            report = json.loads(
                next(Path(td).glob("*/t3_report.json")).read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "blocked")

    def test_with_force_invokes_fc805_suite(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            cases = (
                (0, "3 passed", "passed", 0),
                (0, "2 passed, 1 skipped", "blocked", 2),
                (0, "3 skipped", "blocked", 2),
                (1, "1 failed", "failed", 1),
            )
            for index, (child_rc, child_stdout, status, expected_rc) in enumerate(cases):
                report_root = Path(td) / str(index)
                completed = subprocess.CompletedProcess(
                    args=["pytest"], returncode=child_rc,
                    stdout=child_stdout, stderr="",
                )
                with patch.object(
                    weekly_t3_runner.subprocess,
                    "run",
                    return_value=completed,
                ) as run_child:
                    result = weekly_t3_runner.main([
                        "--report-root", str(report_root),
                        "--run-id", "mocked-run", "--force",
                    ])

                self.assertEqual(result, expected_rc)
                command = run_child.call_args.args[0]
                self.assertIn(str(weekly_t3_runner.T3_TEST), command)
                child_env = run_child.call_args.kwargs["env"]
                self.assertEqual(child_env["FC805_REAL_DOWNLOAD"], "1")
                self.assertEqual(run_child.call_args.kwargs["timeout"], 1800)
                report = json.loads(
                    (report_root / "mocked-run" / "t3_report.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(report["status"], status)
                self.assertEqual(report["returncode"], child_rc)

    def test_report_isolated(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            _run(Path(td))
            reports = list(Path(td).glob("*/t3_report.json"))
            self.assertEqual(len(reports), 1)
            # runner must not write anywhere outside the report root
            self.assertEqual(
                len([p for p in Path(td).rglob("*") if p.is_file()]), 1)


if __name__ == "__main__":
    unittest.main()
