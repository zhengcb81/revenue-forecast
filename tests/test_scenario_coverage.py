"""FC-1003: coverage-gate self-tests.

The gate (compatibility/scenario_coverage.py) must itself be tested: composite
IDs split, deferred owners exempted, required gaps detected, and the whole
95-scenario matrix currently has ZERO required gaps.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

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

    def test_no_required_gaps(self):
        """FC-1003 exit gate: every required scenario is covered by a marker
        or a receipt; anything else must be explicitly deferred."""
        report = sc.coverage_report()
        self.assertEqual(report["required_gaps"], [],
                         f"required gaps: {report['required_gaps']}")

    def test_deferred_are_future_phase_only(self):
        report = sc.coverage_report()
        for sid in report["deferred_future_phase"]:
            owners = report["matrix"][sid]["owners"]
            self.assertTrue(
                any(o.startswith(("FC-110", "FC-120", "FC-130", "FC-150", "FC-1004"))
                    for o in owners),
                f"{sid} deferred but owners {owners} are not future-phase",
            )

    def test_marker_scan_finds_fixture_tests(self):
        markers = sc.collect_test_markers()
        self.assertIn("UJ-01", markers)
        self.assertIn("EX-02", markers)


if __name__ == "__main__":
    unittest.main()
