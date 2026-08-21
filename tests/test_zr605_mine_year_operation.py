"""ZR-605 acceptance tests: MineYearOperation input contract.

  C1  Seven required fields: volume (>0), grade (>0), recovery ∈ (0,1],
      payable ∈ (0,1], product (non-empty str), period (non-empty str),
      scenario ∈ {low,base,high} — missing any creates a gap
      (ForecastInputError, never default 0). Invalid values rejected.
  C2  ADR compliance: derive_saleable_volume = volume × grade × recovery
      × payable — decomposition matches ADR §2 resource model upstream.
  C3  Consumability: to_resource_model_drivers maps to {saleable_volume,
      realized_price} ready for calculate_model_path with model="resource".
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from contracts.evidence import ForecastInputError  # noqa: E402
from mine_year_operation import (  # noqa: E402
    MineYearOperation,
    derive_saleable_volume,
    to_resource_model_drivers,
    validate_mine_year_operation,
)
from revenue_core import calculate_model_path  # noqa: E402

VALID_OP = {
    "volume": 1000.0,
    "grade": 0.5,
    "recovery": 0.90,
    "payable": 0.95,
    "product": "copper concentrate",
    "period": "FY2026",
    "scenario": "base",
}


# ---------------------------------------------------------------------------
# C1 — seven required fields
# ---------------------------------------------------------------------------


def test_c1_valid_operation_passes():
    op = validate_mine_year_operation(VALID_OP)
    assert isinstance(op, MineYearOperation)
    assert op.volume == 1000.0
    assert op.scenario == "base"


@pytest.mark.parametrize("field", [
    "volume", "grade", "recovery", "payable", "product", "period", "scenario",
])
def test_c1_missing_field_creates_gap(field):
    bad = dict(VALID_OP)
    bad.pop(field)
    with pytest.raises(ForecastInputError, match=f"{field} is required"):
        validate_mine_year_operation(bad)


@pytest.mark.parametrize("field,bad_value", [
    ("volume", 0), ("volume", -100), ("volume", "abc"), ("volume", True),
    ("grade", 0), ("grade", -0.5), ("grade", "abc"),
    ("recovery", 0), ("recovery", -0.1), ("recovery", 1.5), ("recovery", True),
    ("payable", 0), ("payable", -0.1), ("payable", 2.0),
])
def test_c1_invalid_values_rejected(field, bad_value):
    bad = dict(VALID_OP)
    bad[field] = bad_value
    with pytest.raises(ForecastInputError):
        validate_mine_year_operation(bad)


def test_c1_empty_product_rejected():
    bad = dict(VALID_OP, product="  ")
    with pytest.raises(ForecastInputError, match="product"):
        validate_mine_year_operation(bad)


def test_c1_invalid_scenario_rejected():
    bad = dict(VALID_OP, scenario="extreme")
    with pytest.raises(ForecastInputError, match="scenario"):
        validate_mine_year_operation(bad)


def test_c1_frozen_dataclass():
    op = validate_mine_year_operation(VALID_OP)
    with pytest.raises(AttributeError):
        op.volume = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# C2 — ADR compliance: derive_saleable_volume
# ---------------------------------------------------------------------------


def test_c2_derive_saleable_volume_hand_check():
    op = validate_mine_year_operation(VALID_OP)
    # 1000 × 0.5 × 0.90 × 0.95 = 427.5
    assert derive_saleable_volume(op) == pytest.approx(427.5)


def test_c2_derive_preserves_unit_semantics():
    # volume=2000 kt, grade=0.8%, recovery=0.85, payable=0.90
    op = validate_mine_year_operation({
        **VALID_OP, "volume": 2000.0, "grade": 0.8,
        "recovery": 0.85, "payable": 0.90,
    })
    # 2000 × 0.8 × 0.85 × 0.90 = 1224.0
    assert derive_saleable_volume(op) == pytest.approx(1224.0)


# ---------------------------------------------------------------------------
# C3 — consumability: to_resource_model_drivers
# ---------------------------------------------------------------------------


def test_c3_to_resource_model_drivers():
    op = validate_mine_year_operation(VALID_OP)
    drivers = to_resource_model_drivers(op, realized_price=5.5)
    assert drivers["saleable_volume"] == pytest.approx(427.5)
    assert drivers["realized_price"] == 5.5


def test_c3_drivers_feed_resource_model():
    op = validate_mine_year_operation(VALID_OP)
    drivers = to_resource_model_drivers(op, realized_price=5.0)
    # Feed into resource model via calculate_model_path
    from test_models import YEARS, make_parameters
    params, ids = make_parameters("resource", {
        "saleable_volume": [drivers["saleable_volume"]] * len(YEARS),
        "realized_price": [drivers["realized_price"]] * len(YEARS),
    })
    result = calculate_model_path("resource", 0, ids, params, YEARS, "base")
    assert len(result["annual_revenue"]) == len(YEARS)
    # revenue = saleable_volume × realized_price = 427.5 × 5.0 = 2137.5
    for year_revenue in result["annual_revenue"].values():
        assert year_revenue == pytest.approx(2137.5)


def test_c3_invalid_realized_price_rejected():
    op = validate_mine_year_operation(VALID_OP)
    for bad in (0, -1.0, "abc", None, True):
        with pytest.raises(ForecastInputError, match="realized_price"):
            to_resource_model_drivers(op, realized_price=bad)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
