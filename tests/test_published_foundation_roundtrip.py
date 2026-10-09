"""Publication preserves consumed foundation semantics and opening bridges."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from forecast.calc import collect_parameter_roles  # noqa: E402
from revenue_core import ForecastInputError, run_forecast, validate_document  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_data_contract import finalize_contract  # noqa: E402
from test_industry_end_to_end import model_document  # noqa: E402
from test_recognition_bridge import add_parameter, forecast_document  # noqa: E402
from test_revenue_constraints import _series  # noqa: E402


def inventory(data, pids):
    params = {p["parameter_id"]: p for p in data["parameters"]}
    data["operating_research"] = {"schema_version": "operating-research/1", "observations": [], "calibrations": [],
        "inventory": [{"item_id": "foundation", "topic": "other", "disposition": "modeled",
        "rationale": "Audited opening foundation retained in the consumed input.",
        "claim_ids": [cid for pid in pids for cid in params[pid]["claim_ids"]],
        "parameter_ids": pids, "driver_ids": [], "recognition_note": "Opening anchor, not additional revenue", "included_in": None}]}


def test_foundation_inventory_roundtrips_actual_base_total_and_stock_ids():
    data = model_document("delivery_pipeline")
    pids = [data["reported_total_revenue_parameter_id"], data["segments"][0]["base_revenue_parameter_id"], "base_orders"]
    inventory(data, pids)
    expected = collect_parameter_roles(data, validate_document(data)["parameter_index"])
    assert set(pids) <= expected["foundation"]
    result = run_forecast(data)
    validate_published_forecast(result, data)
    assert result["confidence"]["research_adequacy"]["inventory"][0]["parameter_ids"] == pids


def test_active_constraint_inventory_is_consumed_during_strong_roundtrip():
    data = forecast_document()
    caps = _series(data, "capacity", {"low": [140,145], "base": [150,170], "high": [160,190]}, "revenue")
    data["revenue_constraints"] = [{"constraint_id": "shared", "type": "sum_cap", "segments": ["Segment A", "Segment B"],
                                  "allocation": "proportional", "scenario_parameter_ids": caps, "rationale": "One shared external resource"}]
    inventory(data, [caps["base"][1]])
    result = run_forecast(data)
    assert result["consolidated_forecast"]["base"]["terminal_revenue"] == 170
    validate_published_forecast(result, data)


def opening_document(adjustment, difference=0):
    data = forecast_document()
    if adjustment:
        pid = add_parameter(data, "opening_elimination", adjustment, 2025, "all")
        data["base_adjustment_parameter_ids"] = [pid]
    value = 150 + adjustment + difference
    next(p for p in data["parameters"] if p["parameter_id"] == "reported_total")["value"] = value
    data["historical_revenue"][-1]["value"] = value
    data["reconciliation_tolerance"] = 0.001
    return finalize_contract(data)


@pytest.mark.parametrize("adjustment", [-5, 5])
def test_lawful_signed_opening_adjustment_publishes_and_stays_auditable(adjustment):
    data = opening_document(adjustment)
    inventory(data, ["opening_elimination"])
    result = run_forecast(data)
    assert result["base_revenue"] == 150 + adjustment
    assert result["opening_base_bridge"]["base_adjustment_total"] == adjustment
    validate_published_forecast(result, data)


def test_custom_input_tolerance_preserves_explicit_opening_residual():
    data = opening_document(0, 0.01)
    result = run_forecast(data)
    assert result["base_revenue"] == 150.01
    assert result["opening_base_bridge"]["reconciliation_tolerance"] == 0.001
    assert result["opening_base_bridge"]["reconciliation_difference"] == pytest.approx(-0.01)
    for path in result["consolidated_forecast"].values():
        assert path["incremental_contribution"]["total"] == pytest.approx(path["incremental_revenue"])
    validate_published_forecast(result, data)


def test_forged_opening_base_or_adjustment_is_rejected():
    data = opening_document(-5)
    result = run_forecast(data)
    for field in ("base_revenue", "base_revenue_parameter_id"):
        forged = copy.deepcopy(result)
        forged["segments"][0][field] = 999 if field == "base_revenue" else "reported_total"
        forged.pop("result_sha256", None)
        with pytest.raises(ForecastInputError, match="segment base"):
            validate_published_forecast(forged, data)
    forged = copy.deepcopy(result)
    forged["opening_base_bridge"]["base_adjustment_total"] = 0
    forged.pop("result_sha256", None)
    with pytest.raises(ForecastInputError, match="opening base bridge"):
        validate_published_forecast(forged, data)


def test_outside_input_tolerance_and_forged_increment_residual_are_rejected():
    with pytest.raises(ForecastInputError, match="does not reconcile"):
        run_forecast(opening_document(0, 1))
    data = opening_document(0, 0.01)
    result = run_forecast(data)
    forged = copy.deepcopy(result)
    forged["consolidated_forecast"]["base"]["incremental_contribution"]["adjustments"] = 0
    forged.pop("result_sha256", None)
    with pytest.raises(ForecastInputError, match="opening base bridge incremental"):
        validate_published_forecast(forged, data)
