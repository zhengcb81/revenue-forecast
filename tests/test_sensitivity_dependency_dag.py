"""Generic retained-DAG shocks; fixture numbers are not company forecasts."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from revenue_core import ForecastInputError, canonical_sha256, run_forecast, validate_document  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_data_contract import finalize_contract  # noqa: E402
from test_recognition_bridge import add_parameter, forecast_document  # noqa: E402


def index(data):
    return {p["parameter_id"]: p for p in data["parameters"]}


def h2_document():
    data = forecast_document()
    data["company_name"] = "SYNTHETIC unrelated H2 issuer"
    h1 = add_parameter(data, "realized_h1", 50, 2026, "all")
    h2 = add_parameter(data, "prior_h2", 50, 2025, "all")
    growth = add_parameter(data, "h2_growth", 0.2, 2026, "base", dimension="ratio")
    params = index(data)
    for pid in (h1, h2):
        params[pid]["kind"] = "reported_fact"
    params[h1]["measurement_period"] = "FY2026H1"
    params[growth].update(unit="ratio", sensitivity_domain={"lower": -1.0, "upper": None,
                         "basis": "signed revenue growth, not a share"})
    ids = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"]
    params[ids[0]].update(kind="derived_fact", formula="x0+x1*(1+x2)", input_parameter_ids=[h1, h2, growth])
    params[ids[1]].update(kind="derived_fact", formula="x0*1.1", input_parameter_ids=[ids[0]])
    data["sensitivity_tests"] = [{"name": "H2 only", "parameter_id": growth,
                                 "shock_type": "percentage_point", "shock_value": 0.03}]
    return finalize_contract(data), growth, ids


def signed_delta_document():
    data = forecast_document()
    data["company_name"] = "SYNTHETIC unrelated signed-delta issuer"
    historical = add_parameter(data, "historical_growth", 0.2, 2025, "all", dimension="ratio")
    delta = add_parameter(data, "growth_change", -0.1, 2026, "base", dimension="ratio")
    params = index(data)
    params[historical].update(kind="reported_fact", unit="ratio")
    params[delta].update(unit="ratio", sensitivity_domain={"lower": None, "upper": None,
                         "basis": "signed change to historical growth"})
    for scenario, rate in (("low", 0.0), ("base", 0.1), ("high", 0.2)):
        path = data["segments"][0]["scenarios"][scenario]
        ids = path["driver_parameter_ids"]["revenue"]
        path.update(model="direct_growth", driver_parameter_ids={"growth_rate": ids})
        for pid in ids:
            params[pid].update(value=rate, unit="ratio", dimension="ratio")
            params[pid].pop("currency", None)
            params[pid].pop("scale", None)
        if scenario == "base":
            params[ids[0]].update(kind="derived_fact", formula="x0+x1", input_parameter_ids=[historical, delta])
    data["sensitivity_tests"] = [{"name": "Signed delta", "parameter_id": delta,
                                 "shock_type": "percentage_point", "shock_value": 0.05}]
    return finalize_contract(data), delta


def test_h2_ancestor_refreshes_later_year_without_changing_realized_h1():
    data, pid, descendants = h2_document()
    frozen = copy.deepcopy(data)
    result = run_forecast(data)
    shock = result["sensitivities"][0]
    assert shock["down_terminal_revenue"] == pytest.approx(179.85)
    assert shock["up_terminal_revenue"] == pytest.approx(183.15)
    audit = shock["dependency_recalculation"]
    assert audit["affected_derived_parameter_ids"] == sorted(descendants)
    assert index(result["input_document"])["realized_h1"]["value"] == 50
    assert data == frozen and canonical_sha256(data) == canonical_sha256(frozen)
    validate_published_forecast(result, data)


def test_signed_delta_keeps_negative_requested_and_effective_values():
    data, pid = signed_delta_document()
    result = run_forecast(data)
    shock = result["sensitivities"][0]
    assert shock["requested_values"] == pytest.approx({"down": -0.15, "up": -0.05})
    assert shock["effective_values"] == pytest.approx(shock["requested_values"])
    assert shock["down_terminal_revenue"] == pytest.approx(176)
    assert shock["up_terminal_revenue"] == pytest.approx(187)
    assert index(result["input_document"])["historical_growth"]["value"] == 0.2
    validate_published_forecast(result, data)


def test_reversed_parameter_order_preserves_multi_level_shock_results():
    data, _, _ = h2_document()
    other = copy.deepcopy(data)
    other["parameters"].reverse()
    assert run_forecast(data)["sensitivities"] == run_forecast(other)["sensitivities"]


def test_direct_consumed_shared_assumption_also_refreshes_derived_fanout():
    data = forecast_document()
    params = index(data)
    root = data["segments"][1]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
    leaf = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
    params[leaf].update(kind="derived_fact", formula="x0*2", input_parameter_ids=[root])
    data["sensitivity_tests"] = [{"name": "Shared", "parameter_id": root, "shock_type": "percent", "shock_value": 0.01}]
    finalize_contract(data)
    result = run_forecast(data)
    shock = result["sensitivities"][0]
    assert shock["max_absolute_terminal_impact"] == pytest.approx(1.815)
    assert shock["dependency_recalculation"]["affected_derived_parameter_ids"] == [leaf]


def test_ancestor_ratio_needs_explicit_domain_instead_of_guessing_share():
    data, pid, _ = h2_document()
    del index(data)[pid]["sensitivity_domain"]
    with pytest.raises(ForecastInputError, match="explicit sensitivity_domain"):
        run_forecast(data)


@pytest.mark.parametrize("domain", [{"lower": 1, "upper": 0, "basis": "bad"},
                                    {"lower": False, "upper": 1, "basis": "bad"},
                                    {"lower": 0, "upper": 0.1, "basis": "excludes original"}, None])
def test_parameter_domain_is_validated_before_shocks(domain):
    data, pid, _ = h2_document()
    index(data)[pid]["sensitivity_domain"] = domain
    with pytest.raises(ForecastInputError, match="sensitivity_domain"):
        validate_document(data)


def test_fact_unused_node_duplicate_and_cycle_still_fail():
    data, pid, descendants = h2_document()
    for target in ("realized_h1", data["segments"][0]["scenarios"]["low"]["driver_parameter_ids"]["revenue"][0]):
        changed = copy.deepcopy(data)
        changed["sensitivity_tests"][0]["parameter_id"] = target
        with pytest.raises(ForecastInputError):
            run_forecast(changed)
    repeated = copy.deepcopy(data)
    repeated["sensitivity_tests"].append({**repeated["sensitivity_tests"][0], "name": "Again"})
    with pytest.raises(ForecastInputError, match="duplicate sensitivity parameter_id"):
        run_forecast(repeated)
    cyclic = copy.deepcopy(data)
    index(cyclic)[descendants[0]]["input_parameter_ids"][0] = descendants[1]
    with pytest.raises(ForecastInputError, match="cycle"):
        run_forecast(cyclic)


def test_infeasible_descendant_driver_bounds_are_not_relaxed():
    data, pid = signed_delta_document()
    data["sensitivity_tests"][0].update(shock_type="discrete", down_value=-2, up_value=-0.1)
    with pytest.raises(ForecastInputError, match="bounds"):
        run_forecast(data)


def test_shocked_descendant_obeys_stock_flow_and_formal_base_obeys_ordering():
    from test_industry_end_to_end import model_document

    data = model_document("inventory_sellthrough")
    sold = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["sold_units"][0]
    root = add_parameter(data, "sold_condition", index(data)[sold]["value"], 2026, "base", dimension="quantity")
    index(data)[sold].update(kind="derived_fact", formula="x0", input_parameter_ids=[root])
    data["sensitivity_tests"] = [{"name": "Stock violation", "parameter_id": root,
                                  "shock_type": "absolute", "shock_value": 1}]
    finalize_contract(data)
    with pytest.raises(ForecastInputError, match="stock-flow balance"):
        run_forecast(data)
    from forecast.calc import refresh_derived_descendants

    # One-variable sensitivity is a conditional diagnostic and may exceed the
    # original scenario bracket. Formal authored Base still must be ordered.
    crossing, root, _ = h2_document()
    index(crossing)[root]["value"] = 0.7
    refresh_derived_descendants(index(crossing), root)
    crossing["sensitivity_tests"] = []
    with pytest.raises(ForecastInputError, match="ordering"):
        run_forecast(crossing)


def test_dependency_audit_and_shock_values_cannot_be_forged():
    data, _, _ = h2_document()
    result = run_forecast(data)
    for field in ("dependency_recalculation", "effective_values"):
        forged = copy.deepcopy(result)
        forged["sensitivities"][0][field] = {}
        forged.pop("result_sha256", None)
        with pytest.raises(ForecastInputError, match=field):
            validate_published_forecast(forged, data)


def test_constraint_ancestor_refreshes_cap_and_low_only_constraint_is_ineligible():
    from test_revenue_constraints import _series

    data = forecast_document()
    caps = _series(data, "cap", {"low": [140,145], "base": [150,170], "high": [160,190]}, "revenue")
    root = add_parameter(data, "capacity_condition", 170, 2027, "base")
    low_only = add_parameter(data, "low_only_shared", 145, 2027, "all")
    caps["low"][1] = low_only
    index(data)[caps["base"][1]].update(kind="derived_fact", formula="x0", input_parameter_ids=[root])
    data["revenue_constraints"] = [{"constraint_id": "resource", "type": "sum_cap",
        "segments": ["Segment A", "Segment B"], "allocation": "proportional",
        "scenario_parameter_ids": caps, "rationale": "One shared capacity constraint"}]
    data["sensitivity_tests"] = [{"name": "Cap condition", "parameter_id": root,
                                  "shock_type": "absolute", "shock_value": 2}]
    finalize_contract(data)
    result = run_forecast(data)
    shock = result["sensitivities"][0]
    assert (shock["down_terminal_revenue"], shock["up_terminal_revenue"]) == pytest.approx((168,172))
    data["sensitivity_tests"][0]["parameter_id"] = low_only
    with pytest.raises(ForecastInputError, match="not referenced by the base scenario"):
        run_forecast(data)


def test_completeness_gate_includes_consumed_assumption_ancestors():
    from forecast.calc import scenario_forecast_parameter_ids

    data, root, _ = h2_document()
    params = index(data)
    eligible = {pid for pid in scenario_forecast_parameter_ids(data, "base", params)
                if params[pid]["kind"] in {"analyst_assumption", "scenario_stress"}}
    data["require_sensitivity_completeness"] = True
    data["sensitivity_tests"] = []
    data["sensitivity_exclusions"] = [{"parameter_id": pid, "reason": "fixture exclusion",
        "rationale": "Synthetic gate test only"} for pid in sorted(eligible - {root})]
    with pytest.raises(ForecastInputError, match=root):
        run_forecast(data)
    data["sensitivity_exclusions"].append({"parameter_id": root, "reason": "fixture exclusion",
        "rationale": "Explicit ancestor exclusion for this synthetic contract test"})
    run_forecast(data)


def test_explicit_multiplier_can_exceed_one_but_cannot_expand_driver_bounds():
    from test_industry_end_to_end import model_document

    data, root, descendants = h2_document()
    params = index(data)
    params[root].update(value=1.2, sensitivity_domain={"lower": 0, "upper": None,
                        "basis": "Nonnegative revenue multiplier, not a share"})
    params[descendants[0]]["formula"] = "x0+x1*x2"
    data["sensitivity_tests"][0].update(shock_type="percent", shock_value=0.1)
    finalize_contract(data)
    shock = run_forecast(data)["sensitivities"][0]
    assert shock["effective_values"] == pytest.approx({"down": 1.08, "up": 1.32})
    assert shock["up_terminal_revenue"] == pytest.approx(188.1)
    bounded = model_document("capacity_utilization")
    pid = bounded["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["utilization"][0]
    index(bounded)[pid]["sensitivity_domain"] = {"lower": None, "upper": None, "basis": "Broad stress request"}
    bounded["sensitivity_tests"] = [{"name": "Utilization", "parameter_id": pid,
                                    "shock_type": "percentage_point", "shock_value": 0.5}]
    result = run_forecast(bounded)
    assert result["sensitivities"][0]["effective_values"]["up"] == 1
    assert result["sensitivities"][0]["clamped"]["up"]
