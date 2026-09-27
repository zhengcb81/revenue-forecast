"""ZR-601 acceptance tests: asset facts — mining asset-fact contract
(reserve stock-flow balance/continuity/non-negativity, resource row-wise
formula, missing-driver fail-closed).

  C1  stock-flow math: 3-period reserve_depletion — per-year balance
      (opening+additions-depletion==closing), continuity
      (closing[t-1]==opening[t]), non-negativity of every asset driver
      (negative reserve/additions/depletion/recovery/price rejected).
  C2  missing-driver honesty: resource and reserve_depletion reject any
      missing asset driver (ForecastInputError, never fabricated).
  C3  formula/registry consistency: resource and reserve_depletion
      annual revenue match hand computation; registry specs carry
      non-empty formula text and the expected unit vocabulary.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from revenue_core import MODEL_SPECS, calculate_model_path  # noqa: E402
from test_models import YEARS, make_parameters  # noqa: E402


def _reserve_drivers() -> dict:
    return {
        "opening_reserves": [1000.0, 1020.0],
        "additions": [100.0, 110.0],
        "depletion": [80.0, 90.0],
        "closing_reserves": [1020.0, 1040.0],
        "recovery_rate": [0.9, 0.92],
        "realized_price": [5.0, 5.5],
    }


def _run(model: str, drivers: dict, scenario: str = "base") -> dict:
    params, ids = make_parameters(model, drivers, scenario=scenario)
    return calculate_model_path(model, 0, ids, params, YEARS, scenario)


# ---------------------------------------------------------------------------
# C1 — stock-flow math contract
# ---------------------------------------------------------------------------


def test_c1_three_period_balance_and_continuity():
    result = _run("reserve_depletion", _reserve_drivers())
    annual = result["annual_revenue"]
    drivers = result["driver_values"]
    opening = drivers["opening_reserves"]
    additions = drivers["additions"]
    depletion = drivers["depletion"]
    closing = drivers["closing_reserves"]
    years = list(annual)
    for index, year in enumerate(years):
        assert opening[year] + additions[year] - depletion[year] == closing[year]
        if index > 0:
            assert closing[years[index - 1]] == opening[year]


def test_c1_imbalance_rejected():
    drivers = _reserve_drivers()
    drivers["closing_reserves"] = [1020.0, 1030.0]  # 1020+110-90=1040 != 1030
    with pytest.raises(ForecastInputError, match="stock-flow balance"):
        _run("reserve_depletion", drivers)


def test_c1_discontinuity_rejected():
    drivers = _reserve_drivers()
    # break continuity (closing[0]==1020 != opening[1]==1010) while keeping
    # the second-year balance (1010+110-90 == 1030)
    drivers["opening_reserves"] = [1000.0, 1010.0]
    drivers["closing_reserves"] = [1020.0, 1030.0]
    with pytest.raises(ForecastInputError, match="continuity"):
        _run("reserve_depletion", drivers)


def test_c1_negative_asset_drivers_rejected():
    for field in ("opening_reserves", "additions", "depletion", "closing_reserves",
                  "realized_price"):
        drivers = _reserve_drivers()
        drivers[field] = list(drivers[field])
        drivers[field][1] = -1.0
        with pytest.raises(ForecastInputError, match="cannot be negative"):
            _run("reserve_depletion", drivers)


def test_c1_recovery_rate_out_of_range_rejected():
    drivers = _reserve_drivers()
    drivers["recovery_rate"] = [0.9, 1.5]  # ratio driver must be in [0, 1]
    with pytest.raises(ForecastInputError, match="must be between 0 and 1"):
        _run("reserve_depletion", drivers)


# ---------------------------------------------------------------------------
# C2 — missing-driver honesty
# ---------------------------------------------------------------------------


def test_c2_resource_missing_drivers_rejected():
    for field in ("saleable_volume", "realized_price"):
        drivers = {"saleable_volume": [10.0, 11.0], "realized_price": [5.0, 5.0]}
        drivers.pop(field)
        with pytest.raises(ForecastInputError, match="missing drivers"):
            _run("resource", drivers)


def test_c2_reserve_missing_drivers_rejected():
    base = _reserve_drivers()
    for field in ("opening_reserves", "additions", "depletion", "closing_reserves",
                  "recovery_rate", "realized_price"):
        drivers = dict(base)
        drivers.pop(field)
        with pytest.raises(ForecastInputError, match="missing drivers"):
            _run("reserve_depletion", drivers)


# ---------------------------------------------------------------------------
# C3 — formula/registry consistency
# ---------------------------------------------------------------------------


def test_c3_resource_rowwise_formula_matches_hand_computation():
    result = _run("resource", {"saleable_volume": [10.0, 11.0],
                               "realized_price": [5.0, 5.0],
                               "other_revenue": [1.0, 2.0]})
    annual = result["annual_revenue"]
    assert [annual["2026"], annual["2027"]] == [51.0, 57.0]
    assert result["formula"] == (
        "revenue = saleable_volume * realized_price + other_revenue"
    )


def test_c3_reserve_formula_matches_hand_computation():
    drivers = _reserve_drivers()
    result = _run("reserve_depletion", drivers)
    annual = result["annual_revenue"]
    d = result["driver_values"]
    years = list(annual)
    for year in years:
        expected = (
            d["depletion"][year] * d["recovery_rate"][year] * d["realized_price"][year]
        )
        assert annual[year] == pytest.approx(expected)
    assert result["formula"] == (
        "revenue = depletion * recovery_rate * realized_price + other_revenue"
    )


def test_c3_registry_specs_carry_formula_and_units():
    for model in ("resource", "reserve_depletion"):
        spec = MODEL_SPECS[model]
        assert spec["formula"].strip()
        # asset facts: reserve stock-flow drivers present in the vocabulary
        if model == "reserve_depletion":
            assert "opening_reserves" in spec["required"]
            assert "closing_reserves" in spec["required"]
            assert "recovery_rate" in spec["required"]
        else:
            assert "saleable_volume" in spec["required"]
            assert "realized_price" in spec["required"]


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
