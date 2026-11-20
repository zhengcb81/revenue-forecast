"""Native two-business timing stress with dated inputs and no double counting."""

import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from forecast.calc import evaluate_derived_formula  # noqa: E402
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



def test_stress_rejects_a_full_period_flow_mixing_reported_and_pending_amounts():
    data, request = _model_and_request()
    segment = data["segments"][0]["name"]
    request["exposure_parameter_ids"] = {segment: {}}
    parameter(data, "shared_delay_rate")["value"] = 0.9
    parameter(data, "shared_cancel_rate")["value"] = 0.5
    for scenario in SCENARIOS:
        annual = parameter(data, f"annual_0_{scenario}")["value"]
        mixed = add_window_parameter(
            data, f"mixed_reported_and_pending_{scenario}", annual,
            "2026-01-01", "2026-12-31", 2026, kind="derived_fact",
            input_parameter_ids=["h1_0", f"h2_0_{scenario}"],
        )
        parameter(data, mixed)["scenario"] = scenario
        parameter(data, f"growth_0_{scenario}_2026")["input_parameter_ids"][0] = mixed
        request["exposure_parameter_ids"][segment][scenario] = mixed
    before = run_forecast(deepcopy(data))
    assert before["segments"][0]["scenarios"]["base"]["recognized_revenue"]["2026"] == pytest.approx(110)
    assert parameter(data, "h1_0")["value"] == 45
    with pytest.raises(ForecastInputError, match="already reported"):
        timing_bridge.build_shared_recognition_stress(data, **request)


def test_stress_rejects_dollars_used_only_as_another_businesss_ratio_covariate():
    data, request = _model_and_request()
    own, peer = data["segments"]
    scopes = request["exposure_parameter_ids"]
    request["exposure_parameter_ids"] = {own["name"]: scopes[peer["name"]]}
    for scenario in SCENARIOS:
        growth = parameter(data, f"growth_0_{scenario}_2026")
        inputs = growth["input_parameter_ids"]
        inputs.extend([f"h2_1_{scenario}", peer["base_revenue_parameter_id"]])
        growth["formula"] = "x0/x1*(1+(x2/x3-0.5)*0.01)-1"
        growth["value"] = evaluate_derived_formula(
            growth["formula"], [parameter(data, dep)["value"] for dep in inputs],
        )
    before = run_forecast(deepcopy(data))
    assert before["segments"][0]["scenarios"]["base"]["recognized_revenue"]["2026"] == pytest.approx(110.154)
    with pytest.raises(ForecastInputError, match="forecast path"):
        timing_bridge.build_shared_recognition_stress(data, **request)



@pytest.mark.parametrize("unavailable", ["ended_on_cutoff", "missing_endpoint", "cross_fiscal_year"])
def test_stress_requires_a_known_unfinished_fiscal_window(unavailable):
    data, request = _model_and_request()
    row = parameter(data, "h2_0_base")
    if unavailable == "ended_on_cutoff":
        row["period_end"] = data["as_of_date"]
    elif unavailable == "missing_endpoint":
        del row["period_end"]
    else:
        row["period_end"] = "2027-01-01"
    with pytest.raises(ForecastInputError, match="period_end|unfinished|FY2026 window"):
        timing_bridge.build_shared_recognition_stress(data, **request)


def test_stress_cannot_bind_to_an_unrelated_opening_amount_with_the_same_value():
    data, request = _model_and_request()
    base_id = data["segments"][0]["base_revenue_parameter_id"]
    matching_value = parameter(data, base_id)["value"]
    borrowed = add_window_parameter(
        data, "unrelated_equal_opening", matching_value, None, None, 2025,
        kind="analyst_assumption", time_basis="annual",
    )
    growth = parameter(data, "growth_0_base_2026")
    growth["input_parameter_ids"][1] = borrowed
    with pytest.raises(ForecastInputError, match="forecast path"):
        timing_bridge.build_shared_recognition_stress(data, **request)


def test_net_pending_amount_remains_traceable_and_the_gross_cannot_be_selected():
    data, request = _model_and_request()
    segment = data["segments"][0]["name"]
    for scenario in SCENARIOS:
        gross = f"h2_0_{scenario}"
        value = parameter(data, gross)["value"]
        parameter(data, gross)["value"] = value * 2
        net = add_window_parameter(
            data, f"net_pending_{scenario}", value, "2026-07-01", "2026-12-31", 2026,
            kind="derived_fact", formula="x0*0.5", input_parameter_ids=[gross],
        )
        parameter(data, net)["scenario"] = scenario
        parameter(data, f"annual_0_{scenario}")["input_parameter_ids"][1] = net
        request["exposure_parameter_ids"][segment][scenario] = net
    # Subtraction before division and an inlined annual sum are valid native
    # arithmetic; the bookable amount is determined by the bound operands.
    for scenario in SCENARIOS:
        growth = parameter(data, f"growth_0_{scenario}_2026")
        base = growth["input_parameter_ids"][1]
        growth.update(formula="(x2 + x0 - x1)/x1",
                      input_parameter_ids=[f"net_pending_{scenario}", base, "h1_0"])
    stressed, receipt = timing_bridge.build_shared_recognition_stress(data, **request)
    after = run_forecast(stressed)
    assert after["segments"][0]["scenarios"]["base"]["recognized_revenue"]["2026"] == pytest.approx(110 - 65 * .145)
    assert receipt["exposures"][segment]["base"]["recognized_addend"]["pending_origin_ids"] == ["h2_0_base"]
    request["exposure_parameter_ids"][segment]["base"] = "h2_0_base"
    with pytest.raises(ForecastInputError, match="forecast path"):
        timing_bridge.build_shared_recognition_stress(data, **request)


def test_same_origin_cannot_be_retimed_twice_under_distinct_business_aliases():
    data, request = _model_and_request()
    name = data["segments"][1]["name"]
    for scenario in SCENARIOS:
        original_id = f"h2_0_{scenario}"
        original = parameter(data, original_id)
        alias = add_window_parameter(data, f"shared_alias_{scenario}", original["value"],
                                     "2026-07-01", "2026-12-31", 2026, kind="derived_fact",
                                     formula="x0", input_parameter_ids=[original_id])
        parameter(data, alias)["scenario"] = scenario
        annual = parameter(data, f"annual_1_{scenario}")
        annual["input_parameter_ids"][1] = alias
        annual["value"] = parameter(data, "h1_1")["value"] + original["value"]
        growth = parameter(data, f"growth_1_{scenario}_2026")
        growth["value"] = annual["value"] / parameter(data, growth["input_parameter_ids"][1])["value"] - 1
        request["exposure_parameter_ids"][name][scenario] = alias
    with pytest.raises(ForecastInputError, match="same pending flow cannot be shocked twice"):
        timing_bridge.build_shared_recognition_stress(data, **request)


@pytest.mark.parametrize("opening_bridge", ["previous_revenue_plan", "previous_native_product"])
def test_stress_with_a_proven_second_year_opening_amount(opening_bridge):
    data, request = _model_and_request()
    name = data["segments"][0]["name"]
    request["exposure_parameter_ids"] = {name: {}}
    request["from_year"] = 2027
    request["delay_rate_parameter_id"] = _ratio(data, "delay_2027", .1, 2027, "all", kind="scenario_stress")
    request["cancellation_rate_parameter_id"] = _ratio(data, "cancel_2027", .05, 2027, "all", kind="scenario_stress")
    data["sensitivity_tests"] = []
    for scenario in SCENARIOS:
        prior = f"annual_0_{scenario}"
        opening = parameter(data, prior)["value"]
        year2 = opening * (1 + SCENARIOS[scenario])
        first_year_growth = parameter(data, f"growth_0_{scenario}_2026")
        if opening_bridge == "previous_native_product":
            base_id = data["segments"][0]["base_revenue_parameter_id"]
            first_year_growth.update(kind="analyst_assumption")
            first_year_growth.pop("formula")
            first_year_growth.pop("input_parameter_ids")
            prior = add_window_parameter(data, f"previous_product_{scenario}", opening,
                                         None, None, 2026, kind="derived_fact", time_basis="annual",
                                         formula="(x1+1)*x0", input_parameter_ids=[base_id, first_year_growth["parameter_id"]])
            parameter(data, prior)["scenario"] = scenario
        first = add_window_parameter(data, f"prior_quarters_{scenario}", year2 * .7,
                                     "2027-01-01", "2027-09-30", 2027, kind="analyst_assumption")
        final = add_window_parameter(data, f"pending_quarter_{scenario}", year2 * .3,
                                     "2027-10-01", "2027-12-31", 2027, kind="analyst_assumption")
        growth = parameter(data, f"growth_0_{scenario}_2027")
        growth.update(kind="derived_fact", formula="(x0+x1-x2)/x2",
                      input_parameter_ids=[first, final, prior])
        request["exposure_parameter_ids"][name][scenario] = final
    before = run_forecast(deepcopy(data))
    stressed, _ = timing_bridge.build_shared_recognition_stress(data, **request)
    after = run_forecast(stressed)
    validate_published_forecast(after, stressed)
    for scenario in SCENARIOS:
        original = before["segments"][0]["scenarios"][scenario]["recognized_revenue"]
        actual = after["segments"][0]["scenarios"][scenario]["recognized_revenue"]
        exposure = parameter(data, f"pending_quarter_{scenario}")["value"]
        assert actual["2026"] == pytest.approx(original["2026"])
        assert actual["2027"] == pytest.approx(original["2027"] - exposure * .145)
        assert actual["2028"] == pytest.approx(original["2028"] + exposure * .1)


def test_zero_stress_rates_preserve_the_path_and_native_sensitivities():
    data, request = _model_and_request()
    parameter(data, "shared_delay_rate")["value"] = 0
    parameter(data, "shared_cancel_rate")["value"] = 0
    before = run_forecast(deepcopy(data))
    stressed, receipt = timing_bridge.build_shared_recognition_stress(data, **request)
    after = run_forecast(stressed)
    assert before["consolidated_forecast"] == after["consolidated_forecast"]
    assert before["sensitivities"] == after["sensitivities"]
    assert all(not item["growth_parameter_ids"] for business in receipt["exposures"].values()
               for item in business.values())


@pytest.mark.parametrize("location, formula", [
    ("amount", "x0 + 1 * x1"),
    ("amount", "x0 + x1 * 1.0"),
    ("growth", "(x0 / x1 - 1) * 1"),
    ("growth", "1.0 * (x0 / (1 * x1) - 1)"),
])
def test_unit_multiplier_preserves_the_same_proven_booked_flow(location, formula):
    data, request = _model_and_request()
    for scenario in SCENARIOS:
        pid = f"annual_0_{scenario}" if location == "amount" else f"growth_0_{scenario}_2026"
        parameter(data, pid)["formula"] = formula
    original = deepcopy(data)
    native_result = run_forecast(deepcopy(data))
    stressed, receipt = timing_bridge.build_shared_recognition_stress(data, **request)
    assert data == original
    forecast = run_forecast(stressed)
    validate_published_forecast(forecast, stressed)
    scope = receipt["exposures"][data["segments"][0]["name"]]["base"]["recognized_addend"]
    assert scope["pending_origin_ids"] == ["h2_0_base"]
    assert scope["recognized_coefficient"] == 1
    before = native_result["consolidated_forecast"]["base"]["annual_revenue"]
    after = forecast["consolidated_forecast"]["base"]["annual_revenue"]
    assert before["2026"] == pytest.approx(165)
    assert after["2026"] == pytest.approx(150.935)
    assert after["2027"] == pytest.approx(before["2027"] + 9.7)
    assert after["2028"] == pytest.approx(before["2028"])


def test_model_input_equal_to_one_is_not_a_literal_identity():
    data, request = _model_and_request()
    scale = _ratio(data, "conditional_exposure_scale", 1.0, 2026, "all")
    for scenario in SCENARIOS:
        growth = parameter(data, f"growth_0_{scenario}_2026")
        growth["input_parameter_ids"].append(scale)
        growth["formula"] = "(x0 / x1 - 1) * x2"
    original = run_forecast(deepcopy(data))
    assert original["consolidated_forecast"]["base"]["annual_revenue"]["2026"] == pytest.approx(165)
    with pytest.raises(ForecastInputError, match="forecast path"):
        timing_bridge.build_shared_recognition_stress(data, **request)
