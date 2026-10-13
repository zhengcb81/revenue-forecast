"""Regression over actual recognition and consolidation parameter consumption."""
from copy import deepcopy
from unittest.mock import patch

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from forecast.calc import base_segment_parameter_ids, collect_parameter_roles
from research.native_dependencies import direct_parameter_cells, segment_roots
from revenue_core import run_forecast
from source_narrative_context import _formula_refs, consume_narrative_input
from test_data_contract import finalize_contract
from test_recognition_bridge import add_parameter, forecast_document
from test_revenue_constraints import _series
from test_source_preparation_complete_result import golden_context


def recognized_document(kind):
    data = forecast_document()
    segment = data["segments"][0]
    if kind == "carry":
        mapping = {scenario: [add_parameter(data, "carry_" + scenario, value, 2026, scenario)]
                   for scenario, value in (("low", 90), ("base", 95), ("high", 100))}
        segment["recognition"].update(mode="lagged_activity", lag_years=1,
                                       carry_in_parameter_ids=mapping)
    else:
        mapping = {scenario: [add_parameter(data, f"progress_{scenario}_{year}", 0.5,
                    year, scenario, dimension="ratio") for year in data["forecast_years"]]
                   for scenario in ("low", "base", "high")}
        segment["recognition"].update(timing="over_time", progress_measure="measured output",
                                       progress_parameter_ids=mapping)
    finalize_contract(data)
    return data, mapping["base"][0]


def test_short_carry_in_is_an_actual_first_year_root():
    data, pid = recognized_document("carry")
    segment = data["segments"][0]
    assert pid in segment_roots(data, segment, "base", 2026)
    assert pid not in segment_roots(data, segment, "base", 2027)
    assert direct_parameter_cells(data, pid, scope=segment["name"], scenario="base") == [
        (segment["name"], "base", "FY2026")]
    result = run_forecast(data, mode="draft")
    assert result["segments"][0]["scenarios"]["base"]["recognized_revenue"]["2026"] == 95


@pytest.mark.parametrize("kind", ["carry", "progress"])
def test_actual_recognition_input_can_consume_a_verified_narrative(kind, tmp_path):
    data, pid = recognized_document(kind)
    request, context = golden_context()
    source = data["sources"][0]
    source["capture"]["snapshot_sha256"] = request["narrative_ref"]["source_ref"]["content_sha256"]
    data["as_of_date"] = request["as_of_date"]
    from fix_hashes import apply_hash_fixes
    apply_hash_fixes(data)
    before = run_forecast(deepcopy(data), mode="draft")
    binding = {"span_id": context.to_dict()["evidence_spans"][0]["span_id"],
               "claim_id": "recognition_context", "parameter_id": pid,
               "support_type": "rationale_support"}
    with patch("source_narrative_context.read_narrative_context", return_value=context) as read:
        updated, receipt = consume_narrative_input(data, request=request, bindings=[binding],
                           source_id=source["source_id"], catalog_config=tmp_path / "catalog.json")
    assert read.call_count == 1
    assert receipt["status"] == "consumed"
    refs = receipt["dependencies"][0]["formula_refs"]
    assert any(r["scenario"] == "base" and r["output"] == "recognized_revenue" for r in refs)
    after = run_forecast(updated, mode="draft")
    assert after["consolidated_forecast"] == before["consolidated_forecast"]
    assert any(c["claim_id"] == binding["claim_id"] for c in after["input_document"]["evidence_claims"])


def test_adjustment_and_constraint_uses_bind_their_actual_output():
    data = forecast_document()
    adjustments = _series(data, "elim", {s: [-5, -5] for s in ("low", "base", "high")}, "revenue")
    data["forecast_adjustments"] = [{"name": "Intersegment elimination",
        "category": "intersegment_elimination", "scenario_parameter_ids": adjustments}]
    caps = _series(data, "cap", {s: [140, 145] for s in ("low", "base", "high")}, "revenue")
    data["revenue_constraints"] = [{"constraint_id": "capacity", "type": "sum_cap",
        "segments": ["Segment A", "Segment B"], "allocation": "proportional",
        "scenario_parameter_ids": caps, "rationale": "Explicit combined capacity"}]
    index = {p["parameter_id"]: p for p in data["parameters"]}
    assert any(ref["output"] == "consolidated_revenue"
               for ref in _formula_refs(data, adjustments["base"][0], index))
    assert any(ref["output"] == "effective_revenue"
               for ref in _formula_refs(data, caps["base"][0], index))
    base_ids = base_segment_parameter_ids(data, index)
    assert caps["base"][0] in base_ids["Segment A"]
    assert caps["low"][0] not in base_ids["Segment A"]
    assert caps["high"][0] not in base_ids["Segment A"]
    output = run_forecast(data, mode="draft")
    assert output["consolidated_forecast"]["base"]["annual_revenue"] == {"2026": 135.0, "2027": 140.0}


def test_context_mentions_never_become_calculation_dependencies():
    data = forecast_document()
    pid = add_parameter(data, "unused_context", 3, 2026, "base")
    index = {p["parameter_id"]: p for p in data["parameters"]}
    assert _formula_refs(data, pid, index) == []
    assert pid not in collect_parameter_roles(data, index)["used"]


def test_deep_derived_ancestry_is_bounded_and_preserves_true_driver_use():
    data = forecast_document()
    pid = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
    index = {p["parameter_id"]: p for p in data["parameters"]}
    previous = "leaf"
    index[previous] = {"parameter_id": previous, "kind": "reported_fact", "value": 1}
    for step in range(1200):
        current = f"derived_{step}"
        index[current] = {"parameter_id": current, "kind": "derived_fact",
                          "input_parameter_ids": [previous], "value": 1}
        previous = current
    index[pid] = {"parameter_id": pid, "kind": "derived_fact", "input_parameter_ids": [previous], "value": 1}
    refs = _formula_refs(data, "leaf", index)
    assert refs == [{"segment": "Segment A", "scenario": "base", "model": "direct_revenue",
                     "driver": "revenue", "output": "recognized_revenue"}]


def test_staged_graph_preserves_dependencies_without_inventing_fiscal_cells():
    from forecast.dependencies import parameter_uses
    data = {"segments": [{"name": "DraftSegment", "scenarios": {"base": {
        "model": "direct_revenue", "driver_parameter_ids": {"revenue": ["bound"]}}}}]}
    index = {"bound": {"kind": "derived_fact", "input_parameter_ids": ["evidence_input"]},
             "evidence_input": {"kind": "analyst_assumption"}}
    uses = list(parameter_uses(data))
    assert len(uses) == 1 and uses[0].year is None
    assert _formula_refs(data, "evidence_input", index)
    assert segment_roots(data, data["segments"][0], "base", 2026) == []


def cross_segment_document(kind):
    data = forecast_document()
    if kind == "linked":
        ratios = _series(data, "attach", {s: [0.4, 0.4] for s in ("low", "base", "high")}, "ratio")
        data["revenue_constraints"] = [{"constraint_id": "attach", "type": "linked_ratio",
            "source_segment": "Segment A", "target_segment": "Segment B", "relation": "exact",
            "scenario_parameter_ids": ratios, "rationale": "Service sales follow explicit host revenue."}]
    else:
        caps = _series(data, "cap", {s: [150, 170] for s in ("low", "base", "high")}, "revenue")
        data["revenue_constraints"] = [{"constraint_id": "cap", "type": "sum_cap",
            "segments": ["Segment A", "Segment B"], "allocation": "proportional",
            "scenario_parameter_ids": caps, "rationale": "Both businesses share constrained capacity."}]
    source_ids = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"]
    data["growth_driver_tree"]["drivers"][1]["parameter_ids"] = list(source_ids)
    return data, source_ids[0]


@pytest.mark.parametrize(("kind", "before_value", "after_value"), [
    ("linked", 44, 48.4), ("proportional", 50, 46.875),
])
def test_true_cross_segment_dependency_is_accepted_and_matches_real_shock(kind, before_value, after_value):
    data, pid = cross_segment_document(kind)
    index = {p["parameter_id"]: p for p in data["parameters"]}
    assert pid in base_segment_parameter_ids(data, index)["Segment B"]
    before = run_forecast(deepcopy(data), mode="draft")
    changed = deepcopy(data)
    # One business shock applies to A's three scenario vectors; changing only
    # Base from 110 to 121 would overtake the original High=120 and correctly
    # violate the scenario-order contract.
    shock_ids = {config["driver_parameter_ids"]["revenue"][0]
                 for config in changed["segments"][0]["scenarios"].values()}
    for parameter in changed["parameters"]:
        if parameter["parameter_id"] in shock_ids:
            parameter["value"] *= 1.1
    after = run_forecast(changed, mode="draft")
    assert before["segments"][1]["scenarios"]["base"]["effective_revenue"]["2026"] == pytest.approx(before_value)
    assert after["segments"][1]["scenarios"]["base"]["effective_revenue"]["2026"] == pytest.approx(after_value)
    assert any(r["segment"] == "Segment B" and r["output"] == "effective_revenue"
               for r in _formula_refs(data, pid, index))


def test_fixed_weight_amount_and_branch_control_dependencies_are_distinct():
    from forecast.dependencies import effective_segment_dependencies
    data, pid = cross_segment_document("proportional")
    weights = {name: _series(data, name, {s: [0.5, 0.5] for s in ("low", "base", "high")}, "ratio")
               for name in ("Segment A", "Segment B")}
    data["revenue_constraints"][0].update(allocation="fixed_weights", weight_parameter_ids=weights)
    effect = effective_segment_dependencies(data, "base")["Segment B"][2026]
    assert pid not in effect.value_parameter_ids
    assert pid in effect.control_parameter_ids
    assert weights["Segment B"]["base"][0] in effect.value_parameter_ids
    assert weights["Segment A"]["base"][0] not in effect.value_parameter_ids


def test_lagged_input_and_recognized_output_clocks_are_explicit():
    from forecast.dependencies import effective_segment_dependencies, segment_parameter_uses
    data, carry = recognized_document("carry")
    segment = data["segments"][0]
    driver = segment["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
    tail = segment["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
    use = next(u for u in segment_parameter_uses(data, segment, "base") if u.parameter_id == driver)
    assert use.input_year == 2026 and use.recognized_year == 2027
    effect = effective_segment_dependencies(data, "base")[segment["name"]]
    assert carry in effect[2026].value_parameter_ids
    assert driver not in effect[2026].value_parameter_ids
    assert driver in effect[2027].value_parameter_ids
    assert tail not in set().union(*(e.value_parameter_ids for e in effect.values()))


def test_activity_tail_cannot_be_assigned_to_in_horizon_revenue_growth():
    from contracts.evidence import ForecastInputError
    data, _ = recognized_document("carry")
    tail = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
    data["growth_driver_tree"]["drivers"][0]["parameter_ids"] = [tail]
    with pytest.raises(ForecastInputError, match="does not affect an attributed segment"):
        run_forecast(data, mode="draft")


def test_elimination_does_not_import_an_unrelated_segments_value_roots():
    from forecast.dependencies import effective_segment_dependencies
    data = forecast_document()
    adjustments = _series(data, "signed", {s: [-5, -5] for s in ("low", "base", "high")}, "revenue")
    data["revenue_constraints"] = [{"constraint_id": "signed", "type": "elimination",
        "segment_adjustment_parameter_ids": {"Segment B": adjustments}, "rationale": "Measured internal sales"}]
    a = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
    effect = effective_segment_dependencies(data, "base")["Segment B"][2026]
    assert a not in effect.value_parameter_ids | effect.control_parameter_ids
    assert adjustments["base"][0] in effect.value_parameter_ids
    assert run_forecast(data, mode="draft")["segments"][1]["scenarios"]["base"]["effective_revenue"]["2026"] == pytest.approx(50)
