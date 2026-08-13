"""FC-1303: SLO probe contract tests — frozen budgets + percentile math.

The probe itself runs against the production catalog (read-only); these
tests lock the frozen budgets and the percentile computation so a budget
weakening or a percentile bug fails fast.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from slo_probe import BUDGETS, _percentiles  # noqa: E402


class SloProbeContractTests(unittest.TestCase):
    def test_budgets_are_frozen_at_measured_levels(self) -> None:
        # Measured on production 2026-08-13 (findings 62): p95 ~0.6s, RSS 21MB.
        # Weakening any budget must fail this test (deliberate-review path).
        self.assertEqual(BUDGETS["exact_p95"], 5.0)
        self.assertEqual(BUDGETS["latest_p95"], 5.0)
        self.assertEqual(BUDGETS["bundle_p95"], 5.0)
        self.assertEqual(BUDGETS["peak_rss_gb"], 2.0)

    def test_percentiles_are_order_statistics(self) -> None:
        values = [0.1, 0.2, 0.3, 0.4, 0.5]
        p = _percentiles(values)
        self.assertEqual(p["p50"], 0.3)
        self.assertGreaterEqual(p["p95"], p["p50"])
        self.assertGreaterEqual(p["p99"], p["p95"])
        self.assertEqual(_percentiles([1.0])["p50"], 1.0)

    def test_probe_cli_is_read_only_by_contract(self) -> None:
        # The probe never writes to the catalog — it only spawns resolve
        # (read-only) and writes an isolated report.  Guard the docstring
        # contract with a source scan: no INSERT/UPDATE/DELETE in the tool.
        source = (ROOT / "tools" / "slo_probe.py").read_text(encoding="utf-8")
        for forbidden in ("INSERT", "UPDATE ", "DELETE FROM", "CREATE TABLE"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
