"""FC-1003: coverage-gate self-tests.

The gate (compatibility/scenario_coverage.py) must itself be tested: composite
IDs split, deferred owners exempted, and marker or receipt evidence resolves
only its own scenarios.
The historical full matrix is cross-owner evidence, separate from owner CI.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "compatibility"))

import scenario_coverage as sc  # noqa: E402


class TestSplitId(unittest.TestCase):
    def test_composite_ids_split(self):
        self.assertEqual(sc._split_id("LT-09/DL-04"), {"LT-09", "DL-04"})

    def test_space_separated(self):
        self.assertEqual(sc._split_id("EX-01 EX-02"), {"EX-01", "EX-02"})

    def test_garbage_ignored(self):
        self.assertEqual(sc._split_id("EX-01 not-an-id SCENARIO: nope"), {"EX-01"})


class TestCoverageReport(unittest.TestCase):
    def test_all_95_scenarios_accounted(self):
        report = sc.coverage_report()
        self.assertEqual(report["total_mandatory"], 95)

    def test_required_gaps_reconcile_markers_and_receipts_without_claiming_peer_coverage(self):
        registry = {"total_mandatory": 3, "scenarios": [
            {"id": "EX-01", "tier_entries": {"unit": {"owner_fc": "FC-1003"}}},
            {"id": "EX-02", "tier_entries": {"unit": {"owner_fc": "FC-1003"}}},
            {"id": "AUD-07", "tier_entries": {"unit": {"owner_fc": "FC-1105"}}},
        ]}
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            tests = root / "tests"
            tests.mkdir()
            receipt = root / "assurance" / "fc" / "FC-1003" / "11_report.json"
            receipt.parent.mkdir(parents=True)
            with patch.object(sc, "SIBLINGS", (root,)), patch.object(sc, "load_registry", return_value=registry):
                before = sc.coverage_report()
                self.assertEqual(before["required_gaps"], ["EX-01", "EX-02"])
                self.assertEqual(before["deferred_future_phase"], ["AUD-07"])
                (tests / "test_example.py").write_text(
                    '"""\nSCENARIO: EX-01\n"""\ndef test_actual():\n    assert 1 + 1 == 2\n', encoding="utf-8",
                )
                receipt.write_text(json.dumps({"scenario_results": [{"id": "EX-02"}]}), encoding="utf-8")
                after = sc.coverage_report()
        self.assertEqual(after["required_gaps"], [])
        self.assertEqual(after["matrix"]["EX-01"]["covered_by"], ["markers"])
        self.assertEqual(after["matrix"]["EX-02"]["covered_by"], ["receipts"])

    def test_deferred_are_future_phase_only(self):
        report = sc.coverage_report()
        for sid in report["deferred_future_phase"]:
            owners = report["matrix"][sid]["owners"]
            self.assertTrue(
                any(o.startswith(("FC-110", "FC-120", "FC-130", "FC-150", "FC-1004"))
                    for o in owners),
                f"{sid} deferred but owners {owners} are not future-phase",
            )

    def test_broken_marked_file_fails_the_gate(self):
        """F2 regression: a SCENARIO marker in a file that does not parse must
        FAIL the gate (SystemExit), never prop it with un-runnable coverage."""
        import tempfile

        from unittest import mock

        with tempfile.TemporaryDirectory() as td:
            tests = Path(td) / "tests"
            tests.mkdir()
            broken = '"""SCENARIO: EX-01"""\n' + "def test_x():\n    pass\n" + "01bad\n"
            (tests / "test_broken.py").write_text(broken, encoding="utf-8")
            with mock.patch.object(sc, "SIBLINGS", (Path(td),)):
                with self.assertRaises(SystemExit) as ctx:
                    sc.collect_test_markers()
                self.assertIn("does not parse", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
