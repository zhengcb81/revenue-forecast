"""Annual consumers must retain the covered period of typed 3.9 flows."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "scripts"),
               str(Path(__file__).resolve().parents[1])]

from contracts.evidence import Collector, ForecastInputError, MultiValidationError  # noqa: E402
from revenue_core import canonical_sha256, run_forecast, validate_document  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_m3_period_flow_contract import add_flow_parameter, schema_3_9_document  # noqa: E402


def parameter(data: dict, parameter_id: str) -> dict:
    return next(p for p in data["parameters"] if p["parameter_id"] == parameter_id)


def mark_half(data: dict, parameter_id: str) -> None:
    p = parameter(data, parameter_id)
    year = int(p["period"][2:])
    p.update(time_basis="period_flow", period_start=f"{year}-01-01",
             period_end=f"{year}-06-30")


@pytest.mark.parametrize("parameter_id", ["0_base_2026", "segment_a_base", "reported_total"])
def test_public_annual_consumers_reject_half_year_as_full_year(parameter_id: str) -> None:
    data = schema_3_9_document()
    mark_half(data, parameter_id)
    with pytest.raises(ForecastInputError, match="annual"):
        run_forecast(data)


@pytest.mark.parametrize("parameter_id", ["0_base_2026", "segment_a_base", "reported_total"])
def test_validate_only_rejects_half_year_at_actual_annual_role(parameter_id: str) -> None:
    data = schema_3_9_document()
    mark_half(data, parameter_id)
    with pytest.raises(ForecastInputError, match="annual"):
        validate_document(data)


@pytest.mark.parametrize("parameter_id", ["0_base_2026", "segment_a_base", "reported_total"])
def test_full_fiscal_year_period_flow_is_accepted_without_scaling(parameter_id: str) -> None:
    data = schema_3_9_document()
    p = parameter(data, parameter_id)
    year = int(p["period"][2:])
    p.update(time_basis="period_flow", period_start=f"{year}-01-01",
             period_end=f"{year}-12-31")
    reference = run_forecast(schema_3_9_document())
    result = run_forecast(data)
    assert result["consolidated_forecast"] == reference["consolidated_forecast"]
    validate_published_forecast(result, data)


def test_explicit_half_year_sum_is_valid_annual_input_and_keeps_partial_evidence() -> None:
    data = schema_3_9_document()
    add_flow_parameter(data, "source_h1", 60.0, "2026-01-01", "2026-06-30", 2026)
    add_flow_parameter(data, "source_h2", 50.0, "2026-07-01", "2026-12-31", 2026)
    original_value = parameter(data, "0_base_2026")["value"]
    p = parameter(data, "0_base_2026")
    p.update(kind="derived_fact", formula="x0+x1",
             input_parameter_ids=["source_h1", "source_h2"],
             time_basis="period_flow", period_start="2026-01-01", period_end="2026-12-31")
    reference = run_forecast(schema_3_9_document())
    result = run_forecast(data)
    validate_published_forecast(result, data)
    assert p["value"] == original_value
    assert result["consolidated_forecast"] == reference["consolidated_forecast"]
    assert parameter(data, "source_h1")["value"] == 60.0
    assert parameter(data, "source_h2")["value"] == 50.0


def test_unused_half_year_fact_remains_legal_supporting_information() -> None:
    data = schema_3_9_document()
    add_flow_parameter(data, "supporting_h1", 55.0, "2026-01-01", "2026-06-30", 2026)
    result = run_forecast(data)
    validate_published_forecast(result, data)
    assert parameter(data, "supporting_h1")["value"] == 55.0


@pytest.mark.parametrize("role", ["base_adjustment", "forecast_adjustment", "carry_in", "constraint"])
def test_single_annual_contract_covers_adjustments_recognition_and_constraints(role: str) -> None:
    from contracts.annual_consumption import validate_annual_consumption
    flow = {"parameter_id": "partial", "time_basis": "period_flow", "period": "FY2026",
            "period_start": "2026-01-01", "period_end": "2026-06-30", "dimension": "revenue"}
    data = {"schema_version": "3.9", "fiscal_year_end": "12-31", "segments": []}
    if role == "base_adjustment":
        data["base_adjustment_parameter_ids"] = ["partial"]
    elif role == "forecast_adjustment":
        data["forecast_adjustments"] = [{"scenario_parameter_ids": {"base": ["partial"]}}]
    elif role == "carry_in":
        data["segments"] = [{"recognition": {"carry_in_parameter_ids": {"base": ["partial"]}}}]
    else:
        data["revenue_constraints"] = [{"type": "sum_cap", "scenario_parameter_ids": {"base": ["partial"]}}]
    with pytest.raises(ForecastInputError, match="annual"):
        validate_annual_consumption(data, {"partial": flow})


def test_single_annual_contract_preserves_declared_point_in_time_stock_drivers() -> None:
    from contracts.annual_consumption import validate_annual_consumption
    stocks = {name: {"parameter_id": name, "period": "FY2026", "time_basis": "point_in_time",
                     "dimension": "backlog", "value": 100.0}
              for name in ("opening", "closing")}
    data = {"schema_version": "3.9", "fiscal_year_end": "12-31", "segments": [{
        "scenarios": {"base": {"model": "project_backlog", "driver_parameter_ids": {
            "opening_backlog": ["opening"], "closing_backlog": ["closing"]}}}}]}
    before = copy.deepcopy(stocks)
    validate_annual_consumption(data, stocks)
    assert stocks == before


def test_non_calendar_full_year_does_not_mean_calendar_january_to_december() -> None:
    from contracts.annual_consumption import validate_annual_consumption
    full_year = {"parameter_id": "revenue", "time_basis": "period_flow", "period": "FY2026",
                 "period_start": "2025-07-01", "period_end": "2026-06-30", "dimension": "revenue"}
    data = {"schema_version": "3.9", "fiscal_year_end": "06-30",
            "reported_total_revenue_parameter_id": "revenue", "segments": []}
    validate_annual_consumption(data, {"revenue": full_year})
    full_year.update(period_start="2026-01-01", period_end="2026-12-31")
    with pytest.raises(ForecastInputError, match="annual"):
        validate_annual_consumption(data, {"revenue": full_year})


def test_collect_all_keeps_annual_consumption_violation_in_its_own_gate() -> None:
    data = schema_3_9_document()
    mark_half(data, "0_base_2026")
    collector = Collector()
    with pytest.raises(MultiValidationError, match="annual"):
        validate_document(data, collector=collector)
    assert any("annual" in message for _, message in collector.errors)


def test_strong_output_boundary_rejects_bound_partial_annual_driver() -> None:
    data = schema_3_9_document()
    result = run_forecast(data)
    mark_half(data, "0_base_2026")
    result["parameter_trace"] = data["parameters"]
    result["input_document"] = copy.deepcopy(data)
    result["input_sha256"] = canonical_sha256(data)
    result["result_sha256"] = canonical_sha256({k: v for k, v in result.items() if k != "result_sha256"})
    with pytest.raises(ForecastInputError, match="annual"):
        validate_published_forecast(result, data)


@pytest.mark.parametrize("model, stock_drivers", [
    ("project_backlog", {"opening_backlog", "closing_backlog"}),
    ("subscription_arr_bridge", {"opening_arr", "closing_arr"}),
    ("inventory_sellthrough", {"opening_inventory", "closing_inventory"}),
])
def test_public_stock_bridges_preserve_point_in_time_values(model: str, stock_drivers: set[str]) -> None:
    from test_industry_end_to_end import model_document
    data = model_document(model)
    reference = run_forecast(copy.deepcopy(data))
    data["schema_version"] = "3.9"
    stock_ids = set()
    for scenario in data["segments"][0]["scenarios"].values():
        for driver in stock_drivers:
            stock_ids.update(scenario["driver_parameter_ids"][driver])
    before = {pid: parameter(data, pid)["value"] for pid in stock_ids}
    for pid in stock_ids:
        parameter(data, pid)["time_basis"] = "point_in_time"
    result = run_forecast(data)
    validate_published_forecast(result, data)
    assert result["consolidated_forecast"] == reference["consolidated_forecast"]
    assert {pid: parameter(data, pid)["value"] for pid in stock_ids} == before


@pytest.mark.parametrize("model, driver, dimension", [
    ("aum_fee_bridge", "inflows", "monetary_balance"),
    ("unit_sales", "units", "quantity"),
])
def test_flow_roles_do_not_become_stocks_only_because_dimensions_match(model: str, driver: str, dimension: str) -> None:
    from contracts.annual_consumption import validate_annual_consumption
    data = {"schema_version": "3.9", "fiscal_year_end": "12-31", "segments": [{
        "scenarios": {"base": {"model": model, "driver_parameter_ids": {driver: ["flow"]}}}}]}
    parameters = {"flow": {"parameter_id": "flow", "time_basis": "point_in_time",
                           "period": "FY2026", "dimension": dimension}}
    with pytest.raises(ForecastInputError, match="annual"):
        validate_annual_consumption(data, parameters)


def test_average_operating_power_is_a_stock_even_when_dimension_is_quantity() -> None:
    from contracts.annual_consumption import validate_annual_consumption
    data = {"schema_version": "3.9", "fiscal_year_end": "12-31", "segments": [{
        "scenarios": {"base": {"model": "renewable_generation", "driver_parameter_ids": {
            "average_commissioned_mw": ["power"]}}}}]}
    parameters = {"power": {"parameter_id": "power", "time_basis": "point_in_time",
                            "period": "FY2026", "dimension": "quantity", "value": 10.0}}
    before = copy.deepcopy(parameters)
    validate_annual_consumption(data, parameters)
    assert parameters == before
