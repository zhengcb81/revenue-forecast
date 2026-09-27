from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analysis.sensitivity import _sensitivity_bounds, _requested_sensitivity_values  # noqa: E402
from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from model_extensions import EXTENSION_OPENING_BALANCES  # noqa: E402
from test_industry_end_to_end import model_document  # noqa: E402


def test_bounds_intersect_all_model_roles_and_allow_complete_shutdown():
    assert _sensitivity_bounds({"dimension": "ratio"}, {("direct_growth", "growth_rate")})[0] == -1
    assert _sensitivity_bounds({"dimension": "ratio"}, {
        ("bank_revenue", "asset_yield"), ("capacity_utilization", "utilization")}) == (0, 1)
    assert _sensitivity_bounds({"dimension": "ratio"}, {("bank_revenue", "funding_cost")})[0] < 0


def test_negative_parameter_percent_shocks_remain_numerically_ordered():
    down, up, _ = _requested_sensitivity_values({"shock_type": "percent", "shock_value": 0.1}, -10, "signed", "revenue")
    assert (down, up) == (-11, -9)


@pytest.mark.parametrize("model", EXTENSION_OPENING_BALANCES)
def test_extension_opening_balance_must_match_source_linked_base(model):
    data = model_document(model)
    _, opening_driver, _ = EXTENSION_OPENING_BALANCES[model]
    pid = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"][opening_driver][0]
    next(parameter for parameter in data["parameters"] if parameter["parameter_id"] == pid)["value"] += 1
    with pytest.raises(ForecastInputError, match="first opening"):
        run_forecast(data)
