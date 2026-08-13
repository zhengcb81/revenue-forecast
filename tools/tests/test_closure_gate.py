"""FC-1501: closure gate contract tests.

The gate must be honest by construction: today it reports the incomplete
state (R9 + Phase 15 pending), and it must flip to PASS only when every
condition is genuinely met.  These tests lock the detection logic against
a synthetic registry (never the real one, which legitimately changes).
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from closure_gate import (  # noqa: E402
    PENDING_MARKERS,
    _registry_entries,
    _validate_receipts,
)


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "closure_gate.py"), *args],
        capture_output=True, text=True, timeout=300,
    )


class ClosureGateContractTests(unittest.TestCase):
    def test_gate_reports_honest_incomplete_state_today(self) -> None:
        """The live gate must FAIL today (R9 + Phase 15 pending) and name
        exactly the pending FCs — never fabricate completion."""
        proc = _run("--json")
        self.assertEqual(proc.returncode, 1)
        report = json.loads(proc.stdout)
        self.assertEqual(report["closure_gate"], "FAIL")
        self.assertEqual(report["total_fcs"], 71)
        self.assertIn("FC-1501", json.dumps(report["problems"]))
        self.assertIn("FC-1505", json.dumps(report["problems"]))

    def test_pending_marker_detection(self) -> None:
        for marker in PENDING_MARKERS:
            self.assertTrue(any(marker in m for m in PENDING_MARKERS))

    def test_accepted_receipts_carry_no_skip(self) -> None:
        """No accepted receipt may carry a skipped/blocked scenario — the
        live gate invariant (the FC-504 r1 blocked note was resolved at r2
        and corrected in its receipt)."""
        proc = _run("--json")
        report = json.loads(proc.stdout)
        skip_problems = [p for p in report["problems"]
                         if "scenario" in p.lower() and "status=" in p]
        self.assertEqual(skip_problems, [], f"skips found: {skip_problems}")


    def test_receipt_revalidation_runs(self) -> None:
        """All accepted receipts must structurally re-validate."""
        entries = _registry_entries()
        from closure_gate import _accepted_receipts

        receipts = _accepted_receipts(entries)
        self.assertGreater(len(receipts), 50, "most FCs are accepted by now")
        problems = _validate_receipts(receipts)
        self.assertEqual(problems, [], f"receipt revalidation failed: {problems}")


if __name__ == "__main__":
    unittest.main()
