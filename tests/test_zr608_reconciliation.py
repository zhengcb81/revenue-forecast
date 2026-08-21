"""ZR-608 acceptance tests: asset→segment→group reconciliation.

  C1  tolerance gate: within |diff| ≤ max(1.0,|ref|)×tol → reconciled_
      modeled; outside → gap (honest fallback).
  C2  fallback listing: side-by-side segments + explicit gap when unclosed
      (never fabricated); closed listing marks closed=True.
  C3  anti-fake-revenue: NaN/inf contributions rejected (finite_number);
      missing/fabricated asset contribution → gap never revenue.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from contracts.evidence import ForecastInputError  # noqa: E402
from reconciliation import (  # noqa: E402
    fallback_segment_listing,
    gap_report,
    reconcile_layer,
)


# ---------------------------------------------------------------------------
# C1 — tolerance gate
# ---------------------------------------------------------------------------


def test_c1_within_tolerance_reconciled_modeled():
    result = reconcile_layer(100.0, 100.0, tolerance=1e-6)
    assert result["status"] == "reconciled_modeled"
    assert result["difference"] == pytest.approx(0.0)


def test_c1_small_difference_within_tolerance():
    # |100.5 − 100| = 0.5 ≤ max(1,100)×0.01 = 1.0
    result = reconcile_layer(100.5, 100.0, tolerance=0.01)
    assert result["status"] == "reconciled_modeled"


def test_c1_outside_tolerance_gap():
    result = reconcile_layer(105.0, 100.0, tolerance=0.01)
    assert result["status"] == "gap"
    assert result["difference"] == pytest.approx(5.0)


def test_c1_negative_tolerance_rejected():
    with pytest.raises(ForecastInputError, match="tolerance cannot be negative"):
        reconcile_layer(100.0, 100.0, tolerance=-0.1)


# ---------------------------------------------------------------------------
# C2 — honest fallback
# ---------------------------------------------------------------------------


def test_c2_closed_listing():
    result = fallback_segment_listing({"copper": 60.0, "gold": 40.0}, 100.0)
    assert result["closed"] is True
    assert result["segment_total"] == pytest.approx(100.0)
    assert result["gap"] == pytest.approx(0.0)


def test_c2_unclosed_listing_reports_gap_not_fake_revenue():
    result = fallback_segment_listing({"copper": 60.0, "gold": 30.0}, 100.0)
    assert result["closed"] is False
    assert result["gap"] == pytest.approx(10.0)
    # the unclosed 10.0 is a GAP — never added to segment_total
    assert result["segment_total"] == pytest.approx(90.0)


def test_c2_non_finite_segment_revenue_rejected():
    for bad in (float("nan"), float("inf"), "abc", None):
        with pytest.raises(ForecastInputError):
            fallback_segment_listing({"copper": bad}, 100.0)


# ---------------------------------------------------------------------------
# C3 — anti-fake-revenue
# ---------------------------------------------------------------------------


def test_c3_gap_report_reconciled():
    result = gap_report({"mine_a": 60.0, "mine_b": 40.0}, 100.0)
    assert result["status"] == "reconciled_modeled"
    assert result["total"] == pytest.approx(100.0)


def test_c3_gap_report_unreconciled_is_gap():
    result = gap_report({"mine_a": 60.0}, 100.0)
    assert result["status"] == "gap"
    assert result["difference"] == pytest.approx(-40.0)


def test_c3_nan_inf_contribution_rejected():
    # NaN/inf can never silently close a layer (anti-fake-revenue)
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ForecastInputError, match="finite"):
            gap_report({"mine_a": bad}, 100.0)


def test_c3_missing_asset_is_gap_not_revenue():
    # asset with no derivable contribution is a gap — never 0 revenue
    result = gap_report({}, 100.0)
    assert result["status"] == "gap"
    assert result["total"] == pytest.approx(0.0)
    assert result["contributions"] == {}


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
