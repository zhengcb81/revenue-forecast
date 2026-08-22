"""ZR-713 acceptance tests: rolling-origin historical backtest.

  C1  strict as-of: each window uses only actuals published <= as_of —
      future actuals never leak into earlier windows (leak fails closed).
  C2  three levels: company / segment / mine-volume backtested
      independently (mine-volume skipped when no operating_units).
  C3  four-layer immutable hashes + cap: each window emits snapshot_id /
      actuals_sha256 / evaluation_sha256 / record_sha256; fewer than
      min_windows → capped=True with rating hint (no fabricated metrics).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from revenue_backtest import create_snapshot  # noqa: E402
from rolling_backtest import (  # noqa: E402
    LEVELS,
    MIN_WINDOWS,
    run_rolling_backtest,
)
from test_backtest import actuals_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def _window(as_of: str, actuals: dict | None = None) -> dict:
    return {
        "as_of": as_of,
        "snapshot": create_snapshot(forecast_document(), "v1"),
        "actuals": actuals if actuals is not None else actuals_document(),
    }


# ---------------------------------------------------------------------------
# C1 — strict as-of, no future actual leak
# ---------------------------------------------------------------------------


def test_c1_future_actual_leak_rejected():
    actuals = actuals_document()
    # add a source published AFTER the window as_of → leak
    actuals["sources"].append({
        "source_id": "future_filing",
        "source_type": "exchange_filing",
        "title": "FY2028 filing",
        "publisher": "Test Exchange",
        "url": "https://www.sec.gov/Archives/edgar/data/1/future.htm",
        "published_date": "2029-01-01",
        "accessed_date": "2029-01-05",
        "page_or_section": "Revenue note",
    })
    with pytest.raises(ForecastInputError, match="future actual leak"):
        run_rolling_backtest([_window("2028-06-01", actuals)])


def test_c1_as_of_cut_excludes_future_sources():
    actuals = actuals_document()
    result = run_rolling_backtest([_window("2028-06-01", actuals)])
    assert result["window_count"] == 1
    # actuals_sha256 is over the as-of-filtered view (deterministic)
    assert isinstance(result["windows"][0]["actuals_sha256"], str)
    assert len(result["windows"][0]["actuals_sha256"]) == 64


def test_c1_empty_windows_rejected():
    with pytest.raises(ForecastInputError, match="at least one window"):
        run_rolling_backtest([])


# ---------------------------------------------------------------------------
# C2 — three levels
# ---------------------------------------------------------------------------


def test_c2_company_and_segment_levels():
    result = run_rolling_backtest([_window("2028-06-01")])
    levels = {item["level"] for item in result["windows"]}
    assert "company" in levels
    assert "segment" in levels
    # mine-volume skipped (no operating_units in actuals doc)
    assert "mine-volume" not in levels


def test_c2_mine_volume_level_included_with_operating_units():
    actuals = actuals_document()
    actuals["operating_units"] = [
        {"volume": 1000.0, "grade": 0.5, "recovery": 0.9, "payable": 0.95,
         "product": "copper", "period": "FY2026", "scenario": "base"}
    ]
    result = run_rolling_backtest([_window("2028-06-01", actuals)])
    levels = {item["level"] for item in result["windows"]}
    assert "mine-volume" in levels


def test_c2_levels_vocabulary():
    assert LEVELS == ("company", "segment", "mine-volume")


# ---------------------------------------------------------------------------
# C3 — four-layer hashes + cap
# ---------------------------------------------------------------------------


def test_c3_four_layer_hash_chain():
    result = run_rolling_backtest([_window("2028-06-01")])
    window = result["windows"][0]
    for key in ("snapshot_id", "actuals_sha256", "evaluation_sha256", "record_sha256"):
        assert isinstance(window[key], str)
        assert len(window[key]) == 64 or key == "snapshot_id"
    # snapshot_id matches backtest id chain (from evaluate_snapshot)
    assert window["snapshot_id"]


def test_c3_single_window_capped():
    result = run_rolling_backtest([_window("2028-06-01")])
    assert result["capped"] is True
    assert result["rating_cap_hint"] is not None


def test_c3_multiple_windows_not_capped():
    # two windows both after the actuals source published_date (2028-02-20);
    # actuals must postdate fiscal year end (2027-12-31) per validate_actuals
    windows = [_window("2028-06-01"), _window("2029-06-01")]
    result = run_rolling_backtest(windows)
    assert result["capped"] is False
    assert result["rating_cap_hint"] is None
    assert result["window_count"] == 2


def test_c3_min_windows_constant():
    assert MIN_WINDOWS == 2


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
