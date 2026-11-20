"""Native two-business timing stress with dated inputs and no double counting."""

import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from forecast.dependencies import expand_derived_inputs  # noqa: E402
from research import timing_bridge  # noqa: E402
from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_data_contract import apply_parameter_contract, finalize_contract  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402
from test_revenue_constraints import _series  # noqa: E402
from test_w05_dated_contribution_contract import add_window_parameter, parameter  # noqa: E402


SCENARIOS = {"low": 0.05, "base": 0.10, "high": 0.20}


def _ratio(data, pid, value, year, scenario, *, kind="analyst_assumption", **extra):
    entry = {"parameter_id": pid, "kind": kind, "value": value, "unit": "ratio",
             "period": f"FY{year}", "definition": pid, "scenario": scenario,
             "rationale": "Explicit conditional scenario input.", "source_ids": [], **extra}
    apply_parameter_contract(data, entry, "ratio")
    data["parameters"].append(entry)
    return pid


def _model_and_request():
    data = forecast_document()
    data["forecast_years"] = [2026, 2027, 2028]
    data["as_of_date"] = "2026-08-01"
    exposures = {}
    base_drivers = []
    for serial, (segment, h1_value) in enumerate(zip(data["segments"], [45.0, 23.0], strict=True)):
        base_id = segment["base_revenue_parameter_id"]
        opening = parameter(data, base_id)["value"]
        h1 = add_window_parameter(data, f"h1_{serial}", h1_value, "2026-01-01", "2026-06-30", 2026)
        scopes = {}
        exposures[segment["name"]] = scopes
        for scenario, growth in SCENARIOS.items():
            amount = opening * (1 + growth)
            h2 = add_window_parameter(data, f"h2_{serial}_{scenario}", amount - h1_value,
                                      "2026-07-01", "2026-12-31", 2026, kind="analyst_assumption")
            parameter(data, h2)["scenario"] = scenario
            scopes[scenario] = h2
            annual = add_window_parameter(data, f"annual_{serial}_{scenario}", amount, None, None, 2026,
                                          kind="derived_fact", time_basis="annual", formula="x0+x1",
                                          input_parameter_ids=[h1, h2])
            parameter(data, annual)["scenario"] = scenario
            ratios = [_ratio(data, f"growth_{serial}_{scenario}_2026", growth, 2026, scenario,
                             kind="derived_fact", formula="x0/x1-1", input_parameter_ids=[annual, base_id])]
            ratios.extend(_ratio(data, f"growth_{serial}_{scenario}_{year}", growth, year, scenario)
                          for year in (2027, 2028))
            segment["scenarios"][scenario].update(
                model="direct_growth", driver_parameter_ids={"growth_rate": ratios})
            if scenario == "base":
                base_drivers.extend(ratios)

    coverage = next(item for item in data["research_coverage"] if item["dimension"] == "growth_curve")
    coverage["parameter_ids"] = base_drivers
    data["sensitivity_tests"] = [{"name": "Existing native growth sensitivity",
                                  "parameter_id": "growth_0_base_2027", "shock_type": "percentage_point",
                                  "shock_value": 0.02}]
    delay = _ratio(data, "shared_delay_rate", 0.10, 2026, "all", kind="scenario_stress")
    cancel = _ratio(data, "shared_cancel_rate", 0.05, 2026, "all", kind="scenario_stress")
    finalize_contract(data)
    data["schema_version"] = "3.10"
    return data, {"exposure_parameter_ids": exposures, "from_year": 2026,
                  "delay_rate_parameter_id": delay, "cancellation_rate_parameter_id": cancel,
                  "prefix": "common_event", "rationale": "Illustrative shared acceptance event with no impact on H1."}


def test_joint_stress_fixture_emits_original_unshocked_forecast():
    data, _ = _model_and_request()
    result = run_forecast(data)
    assert result["consolidated_forecast"]["base"]["annual_revenue"]["2026"] == pytest.approx(165.0)
    assert len(result["sensitivities"]) == 1


def test_shared_event_changes_only_pending_recognition_and_recovers_once():
    data, request = _model_and_request()
    checkpoint = deepcopy(data)
    before = run_forecast(deepcopy(data))
    stressed, receipt = timing_bridge.build_shared_recognition_stress(data, **request)
    assert data == checkpoint
    assert receipt["status"] == "illustrative_stress"
    after = run_forecast(stressed)
    validate_published_forecast(after, stressed)
    assert len(after["sensitivities"]) == 1
    for ordinal, (old, changed) in enumerate(zip(before["segments"], after["segments"], strict=True)):
        assert parameter(stressed, f"h1_{ordinal}") == parameter(checkpoint, f"h1_{ordinal}")
        for scenario in SCENARIOS:
            exposure_id = request["exposure_parameter_ids"][data["segments"][ordinal]["name"]][scenario]
            exposure = parameter(data, exposure_id)["value"]
            original = old["scenarios"][scenario]["recognized_revenue"]
            actual = changed["scenarios"][scenario]["recognized_revenue"]
            assert actual["2026"] == pytest.approx(original["2026"] - exposure * 0.145)
            assert actual["2027"] == pytest.approx(original["2027"] + exposure * 0.10)
            assert actual["2028"] == pytest.approx(original["2028"])
            assert sum(actual.values()) == pytest.approx(sum(original.values()) - exposure * 0.045)
    restored_driver = stressed["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["growth_rate"][2]
    index = {p["parameter_id"]: p for p in stressed["parameters"]}
    assert "shared_cancel_rate" not in expand_derived_inputs((restored_driver,), index)


def test_existing_portfolio_capacity_is_applied_once_after_the_shared_event():
    data, request = _model_and_request()
    cap_ids = _series(data, "observed_fixture_capacity", {
        "low": [140, 200, 250], "base": [145, 205, 255], "high": [155, 270, 300],
    }, "revenue")
    data["schema_version"] = "3.10"
    cap = {"constraint_id": "portfolio_capacity", "type": "sum_cap", "allocation": "proportional",
           "segments": list(request["exposure_parameter_ids"]), "scenario_parameter_ids": cap_ids,
           "rationale": "The synthetic businesses use the same external acceptance capacity."}
    data["revenue_constraints"] = [cap]
    stressed, _ = timing_bridge.build_shared_recognition_stress(data, **request)
    after = run_forecast(stressed)
    assert after["revenue_constraints"] == [cap]
    base = after["consolidated_forecast"]["base"]["annual_revenue"]
    assert base["2026"] == pytest.approx(145)
    assert base["2027"] == pytest.approx(181.5 + 9.7)


def test_stress_does_not_move_an_already_reported_flow():
    data, request = _model_and_request()
    scopes = next(iter(request["exposure_parameter_ids"].values()))
    scopes["base"] = "h1_0"
    with pytest.raises(ForecastInputError, match="already reported"):
        timing_bridge.build_shared_recognition_stress(data, **request)


def test_stress_cannot_borrow_another_businesss_dated_projection():
    data, request = _model_and_request()
    left, right = request["exposure_parameter_ids"].values()
    left["base"] = right["base"]
    with pytest.raises(ForecastInputError, match="forecast path"):
        timing_bridge.build_shared_recognition_stress(data, **request)
