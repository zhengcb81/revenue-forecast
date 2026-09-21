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


def _operating_unit() -> dict:
    return {"volume": 1000.0, "grade": 0.5, "recovery": 0.9, "payable": 0.95,
            "product": "copper", "period": "FY2026", "scenario": "base"}


def test_c2_mine_volume_level_included_with_operating_units():
    actuals = actuals_document()
    actuals["operating_units"] = [_operating_unit()]
    result = run_rolling_backtest([_window("2028-06-01", actuals)])
    levels = {item["level"] for item in result["windows"]}
    assert "mine-volume" in levels


def test_c2_levels_emit_distinct_evaluations():
    # REV-001 regression: each level must emit its own evaluation view and
    # hash chain — never byte-identical relabeled copies.
    actuals = actuals_document()
    actuals["operating_units"] = [_operating_unit()]
    result = run_rolling_backtest([_window("2028-06-01", actuals)])
    windows = {item["level"]: item for item in result["windows"]}
    assert set(windows) == {"company", "segment", "mine-volume"}
    signatures = {
        item["level"]: (item["evaluation_sha256"], item["record_sha256"])
        for item in result["windows"]
    }
    assert len(set(signatures.values())) == 3
    # company vs segment wape are computed from different actuals series
    assert windows["company"]["wape"] != windows["segment"]["wape"]
    # mine-volume has no revenue projection to compare — wape stays None
    assert windows["mine-volume"]["wape"] is None


def test_c2_segment_level_uses_segment_metrics():
    result = run_rolling_backtest([_window("2028-06-01")])
    segment = next(item for item in result["windows"] if item["level"] == "segment")
    # segment window carries segment-level data, not the company summary
    assert "backtest_id" in segment
    assert segment["observations"] == 2
    assert isinstance(segment["wape"], float)


def test_c2_mine_volume_contract_fails_closed_on_gap():
    # ZR-605 contract: missing MineYearOperation field is a gap, not a default
    actuals = actuals_document()
    actuals["operating_units"] = [{"volume": 1000.0, "grade": 0.5}]
    with pytest.raises(ForecastInputError, match="required"):
        run_rolling_backtest([_window("2028-06-01", actuals)])


def test_c2_mine_volume_saleable_volume_decomposition():
    actuals = actuals_document()
    actuals["operating_units"] = [_operating_unit()]
    result = run_rolling_backtest([_window("2028-06-01", actuals)])
    mine = next(item for item in result["windows"] if item["level"] == "mine-volume")
    # saleable_volume = volume * grade * recovery * payable (ZR-605)
    assert mine["total_saleable_volume"] == pytest.approx(1000 * 0.5 * 0.9 * 0.95)
    assert mine["observations"] == 1


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
        assert len(window[key]) == 64
    # snapshot_id is the frozen snapshot's own identity — same across levels
    assert result["windows"][0]["snapshot_id"] == result["windows"][1]["snapshot_id"]


def test_c3_record_hash_binds_level_and_as_of():
    # REV-002 regression: relabeling or re-dating a window breaks its hash
    windows = [_window("2028-06-01"), _window("2029-06-01")]
    result = run_rolling_backtest(windows)
    company = [w for w in result["windows"] if w["level"] == "company"]
    segment = [w for w in result["windows"] if w["level"] == "segment"]
    assert company[0]["record_sha256"] != segment[0]["record_sha256"]
    # same level, different as_of → bound hash must differ
    assert company[0]["record_sha256"] != company[1]["record_sha256"]


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
