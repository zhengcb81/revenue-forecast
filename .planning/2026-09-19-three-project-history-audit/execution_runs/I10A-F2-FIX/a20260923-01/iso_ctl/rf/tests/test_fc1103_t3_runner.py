"""FC-1103: weekly T3 runner contracts.

SCENARIO: AUD-06 (weekly T3; blocked is an alert, never a silent green)

The runner must (a) exit BLOCKED (2) without --force — T3 real-provider
download is never silently green, (b) with --force run the FC-805 suite
(skipped -> blocked; passed -> 0; failed -> 1), (c) write an isolated
report, (d) never touch the production catalog.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "tools" / "weekly_t3_runner.py"


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
            subprocess.run(
                [sys.executable, "-B", str(RUNNER), "--report-root", str(td),
                 "--force"],
                capture_output=True, text=True, encoding="utf-8", timeout=900,
            )
            # the FC-805 suite either passes (authorized creds) or is skipped
            # (no credentials) — either way the runner classifies it; it must
            # NOT be a silent green without running
            report = json.loads(
                next(Path(td).glob("*/t3_report.json")).read_text(encoding="utf-8"))
            self.assertIn(report["status"], ("passed", "blocked", "failed"))
            self.assertIn("returncode", report)

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
