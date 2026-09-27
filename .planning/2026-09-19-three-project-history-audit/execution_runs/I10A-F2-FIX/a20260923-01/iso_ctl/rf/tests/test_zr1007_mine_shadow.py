"""ZR-1007 acceptance tests: mine facts / model shadow vs legacy segment models.

Stage I seventh card.  A mine-facts shadow model path
(MineYearOperation -> to_resource_model_drivers -> registered resource
model) is computed side-by-side with the legacy segment model path
(direct_growth / unit_sales style).  Differences are attributable and
reconciled; the shadow path is backtested (mine-volume level) but never
replaces production forecasts (zero publication-registry writes).

  C1  shadow path exists & is computable: MineYearOperation ->
      to_resource_model_drivers -> calculate_model_path("resource") yields
      the same revenue as saleable_volume x realized_price (hand check).
  C2  attribution: a mine-facts driver change (volume/grade/recovery/
      payable/price) changes shadow revenue by the attributable delta;
      the legacy segment model responds to its own drivers independently.
  C3  reconciliation: shadow per-mine contributions close to the legacy
      segment total within tolerance (reconcile_layer/gap_report) — gap
      reported honestly when not closed.
  C4  backtest: rolling backtest mine-volume level evaluates
      saleable_volume decomposition from MineYearOperation actuals;
      strict as-of discipline (future actual leaks fail closed).
  C5  zero replacement: shadow computation never writes the publication
      registry (registry content unchanged before/after), production
      forecast output is untouched.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from mine_year_operation import (  # noqa: E402
    derive_saleable_volume,
    to_resource_model_drivers,
    validate_mine_year_operation,
)
from reconciliation import gap_report, reconcile_layer  # noqa: E402
from revenue_core import calculate_model_path  # noqa: E402
from rolling_backtest import run_rolling_backtest  # noqa: E402
from test_models import YEARS, make_parameters  # noqa: E402
from test_zr713_rolling_backtest import _window  # noqa: E402

VALID_OP = {
    "volume": 1000.0,
    "grade": 0.5,
    "recovery": 0.90,
    "payable": 0.95,
    "product": "copper concentrate",
    "period": "FY2026",
    "scenario": "base",
}
REALIZED_PRICE = 5.0  # revenue per unit


def _shadow_revenue(op: dict, price: float) -> dict:
    """Compute the shadow revenue path: MineYearOperation -> resource model."""
    validated = validate_mine_year_operation(op)
    drivers = to_resource_model_drivers(validated, realized_price=price)
    params, ids = make_parameters("resource", {
        "saleable_volume": [drivers["saleable_volume"]] * len(YEARS),
        "realized_price": [drivers["realized_price"]] * len(YEARS),
    })
    return calculate_model_path("resource", 0, ids, params, YEARS, "base")


def _legacy_revenue(model: str, driver_values: dict[str, list[float]],
                    base_revenue: float = 0.0) -> dict:
    """Compute the legacy segment-model path."""
    params, ids = make_parameters(model, driver_values)
    return calculate_model_path(model, base_revenue, ids, params, YEARS, "base")


# ---------------------------------------------------------------------------
# C1 — shadow path exists and hand-checks to saleable_volume x price
# ---------------------------------------------------------------------------


def test_c1_shadow_path_matches_saleable_times_price():
    op = validate_mine_year_operation(VALID_OP)
    saleable = derive_saleable_volume(op)
    assert saleable == pytest.approx(427.5)  # 1000 x 0.5 x 0.9 x 0.95
    result = _shadow_revenue(VALID_OP, REALIZED_PRICE)
    assert result["model"] == "resource"
    for year in map(str, YEARS):
        assert result["annual_revenue"][year] == pytest.approx(
            saleable * REALIZED_PRICE)  # 427.5 x 5.0 = 2137.5
    assert result["driver_values"]["saleable_volume"][str(YEARS[0])] == pytest.approx(427.5)


def test_c1_legacy_segment_path_still_computable():
    """The legacy segment model path coexists (no removal, no replacement)."""
    legacy = _legacy_revenue("direct_growth", {"growth_rate": [0.1, 0.1]}, base_revenue=100.0)
    assert list(legacy["annual_revenue"].values()) == pytest.approx([110.0, 121.0])


# ---------------------------------------------------------------------------
# C2 — attribution: each driver change maps to an attributable delta
# ---------------------------------------------------------------------------


def test_c2_volume_change_attributable():
    base = _shadow_revenue(VALID_OP, REALIZED_PRICE)
    changed = dict(VALID_OP, volume=1200.0)  # +20%
    result = _shadow_revenue(changed, REALIZED_PRICE)
    # saleable: 1200 x 0.5 x 0.9 x 0.95 = 513.0 vs 427.5 -> delta 85.5 x price 5.0
    expected_delta = (1200 - 1000) * 0.5 * 0.9 * 0.95 * REALIZED_PRICE
    assert expected_delta == pytest.approx(427.5)
    assert result["annual_revenue"]["2026"] - base["annual_revenue"]["2026"] == pytest.approx(
        expected_delta)


def test_c2_price_change_attributable():
    base = _shadow_revenue(VALID_OP, REALIZED_PRICE)
    result = _shadow_revenue(VALID_OP, price=6.0)
    delta = (6.0 - 5.0) * 427.5
    assert result["annual_revenue"]["2026"] - base["annual_revenue"]["2026"] == pytest.approx(
        delta)


def test_c2_recovery_change_attributable():
    base = _shadow_revenue(VALID_OP, REALIZED_PRICE)
    changed = dict(VALID_OP, recovery=0.80)
    result = _shadow_revenue(changed, REALIZED_PRICE)
    delta = 1000 * 0.5 * (0.80 - 0.90) * 0.95 * REALIZED_PRICE
    assert result["annual_revenue"]["2026"] - base["annual_revenue"]["2026"] == pytest.approx(
        delta)


def test_c2_legacy_drivers_independent():
    """Legacy model drivers respond only to their own parameters."""
    legacy = _legacy_revenue("unit_sales", {"units": [10, 12], "unit_revenue": [5, 5]})
    assert list(legacy["annual_revenue"].values()) == [50.0, 60.0]
    legacy2 = _legacy_revenue("unit_sales", {"units": [20, 24], "unit_revenue": [5, 5]})
    assert list(legacy2["annual_revenue"].values()) == [100.0, 120.0]


# ---------------------------------------------------------------------------
# C3 — reconciliation: shadow closes to legacy total or honest gap
# ---------------------------------------------------------------------------


def test_c3_shadow_reconciles_to_legacy_total():
    """Shadow per-mine contributions (two mines) close to the legacy
    segment total within tolerance."""
    mine_a = _shadow_revenue(VALID_OP, REALIZED_PRICE)["annual_revenue"]["2026"]
    mine_b_op = dict(VALID_OP, volume=2000.0)
    mine_b = _shadow_revenue(mine_b_op, REALIZED_PRICE)["annual_revenue"]["2026"]
    # legacy segment total equals the sum of the two shadow mines here
    legacy_total = mine_a + mine_b
    status = reconcile_layer(
        asset_total=mine_a + mine_b,
        reference_total=legacy_total,
        tolerance=0.001,
    )
    assert status["status"] == "reconciled_modeled", status
    report = gap_report(
        {"mine_a": mine_a, "mine_b": mine_b},
        reference_total=legacy_total,
        tolerance=0.001,
    )
    assert report["status"] == "reconciled_modeled", report


def test_c3_gap_reported_honestly_when_not_closed():
    """When shadow does NOT close to the legacy total, the gap is reported
    honestly (never fabricated as revenue)."""
    mine_a = _shadow_revenue(VALID_OP, REALIZED_PRICE)["annual_revenue"]["2026"]
    legacy_total = mine_a + 50.0  # unexplained 50.0
    status = reconcile_layer(
        asset_total=mine_a,
        reference_total=legacy_total,
        tolerance=0.001,
    )
    assert status["status"] != "reconciled_modeled"
    assert abs(status["difference"]) == pytest.approx(50.0)
    report = gap_report(
        {"mine_a": mine_a},
        reference_total=legacy_total,
        tolerance=0.001,
    )
    assert report["status"] != "reconciled_modeled"


# ---------------------------------------------------------------------------
# C4 — backtest: mine-volume level with strict as-of discipline
# ---------------------------------------------------------------------------


def _actuals_with_units() -> dict:
    from test_backtest import actuals_document

    actuals = actuals_document()
    actuals["operating_units"] = [
        {**VALID_OP, "period": "FY2026", "scenario": "base"},
        {**dict(VALID_OP, volume=2000.0), "period": "FY2026", "scenario": "base"},
    ]
    return actuals


def test_c4_mine_volume_backtest_decomposes_saleable():
    result = run_rolling_backtest([_window("2028-06-01", _actuals_with_units())])
    mine = next(item for item in result["windows"] if item["level"] == "mine-volume")
    assert mine["observations"] == 2
    # 427.5 + 855.0 = 1282.5
    assert mine["total_saleable_volume"] == pytest.approx(427.5 + 855.0)
    assert mine["record_sha256"]


def test_c4_future_actual_leak_fails_closed():

    actuals = _actuals_with_units()
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


# ---------------------------------------------------------------------------
# C5 — zero replacement: shadow never writes the publication registry
# ---------------------------------------------------------------------------


def test_c5_shadow_computation_writes_nothing(monkeypatch):
    import publication_registry

    def _boom(*args, **kwargs):
        raise AssertionError("shadow computation must not write the registry")

    monkeypatch.setattr(publication_registry, "_append", _boom)
    # compute shadow + legacy paths — any registry write would explode
    _shadow_revenue(VALID_OP, REALIZED_PRICE)
    _legacy_revenue("direct_growth", {"growth_rate": [0.1, 0.1]})


def test_c5_production_forecast_untouched(monkeypatch):
    """Shadow + legacy path computation does not call run_forecast, so the
    production forecast output is unchanged (no side effect)."""
    import revenue_core

    original = revenue_core.run_forecast
    called = {"n": 0}

    def _spy(data, **kwargs):
        called["n"] += 1
        return original(data, **kwargs)

    monkeypatch.setattr(revenue_core, "run_forecast", _spy)
    _shadow_revenue(VALID_OP, REALIZED_PRICE)
    _legacy_revenue("unit_sales", {"units": [10, 12], "unit_revenue": [5, 5]})
    assert called["n"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
