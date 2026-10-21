"""R1 W05: selected native revenue scope and ratio dimensions, not guidance fitting."""
from copy import deepcopy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from revenue_report import render_markdown, validate_published_forecast  # noqa: E402
from research.native_dependencies import scope_components  # noqa: E402
from research.target_measurement import compare_target_measurement, normalize_target_bounds  # noqa: E402
from test_data_contract import finalize_contract  # noqa: E402
from test_independent_targets import benchmark_document  # noqa: E402
from test_target_measurement_comparison import yoy_document, quarter_document  # noqa: E402


SCENARIOS = ("low", "base", "high")


def group_scope(*names):
    return {"type": "segment_group", "name": "Continuing services", "segment_names": list(names)}


def group_document():
    """Third native segment is excluded; selected A+B retain 100+50 base."""
    data = benchmark_document()
    target = deepcopy(data["management_targets"][0])
    target_claims = deepcopy([c for c in data["evidence_claims"] if c["target_type"] == "management_target"])
    third = deepcopy(data["segments"][1])
    third["name"] = "Exited segment"
    parameter_ids = {third["base_revenue_parameter_id"]}
    for scenario in SCENARIOS:
        parameter_ids.update(third["scenarios"][scenario]["driver_parameter_ids"]["revenue"])
    replacements = {pid: "excluded_" + pid for pid in parameter_ids}
    for parameter in list(data["parameters"]):
        if parameter["parameter_id"] in replacements:
            clone = deepcopy(parameter)
            clone["parameter_id"] = replacements[parameter["parameter_id"]]
            clone["definition"] = "Excluded business " + clone["definition"]
            # Excluded segment shrinks while selected businesses grow.
            clone["value"] = 25.0 if parameter["period"] == "FY2025" else 10.0
            data["parameters"].append(clone)
    third["base_revenue_parameter_id"] = replacements[third["base_revenue_parameter_id"]]
    for scenario in SCENARIOS:
        third["scenarios"][scenario]["driver_parameter_ids"]["revenue"] = [
            replacements[pid] for pid in third["scenarios"][scenario]["driver_parameter_ids"]["revenue"]
        ]
    data["segments"].append(third)
    next(p for p in data["parameters"] if p["parameter_id"] == data["reported_total_revenue_parameter_id"])["value"] = 175.0
    data["historical_revenue"][-1]["value"] = 175.0
    finalize_contract(data)
    data["management_targets"] = [target]
    data["evidence_claims"].extend(target_claims)
    target.update(scope=group_scope("Segment A", "Segment B"),
                  comparison_basis={"schema_version": "management-target-comparison/1", "metric_kind": "annual_revenue_level", "period": "FY2027"},
                  mapped_parameter_ids=[s["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1] for s in data["segments"][:2]])
    return data


@pytest.mark.parametrize("currency", ["CNY", "USD", "HKD"])
@pytest.mark.parametrize("treatment", ["independent_benchmark", "unmodeled_data_gap"])
def test_typed_growth_cannot_carry_raw_money_currency(currency, treatment):
    data = yoy_document()
    target = data["management_targets"][0]
    target.update(raw_currency=currency, treatment=treatment)
    if treatment == "unmodeled_data_gap":
        target.update(mapped_parameter_ids=[], mapped_scenarios=[], comparison_value=None)
    with pytest.raises(ForecastInputError, match="typed_growth_currency_must_be_dimensionless"):
        run_forecast(data)


def test_growth_ratio_endpoints_are_dimensionless_without_a_midpoint():
    data = yoy_document()
    target = data["management_targets"][0]
    target.update(raw_target_value=None, raw_value_kind="numeric_range", raw_target_value_low=18,
                  raw_target_value_high=22, comparison_value=None)
    for claim in data["evidence_claims"]:
        if claim["claim_id"] in target["claim_ids"]:
            claim.pop("extracted_value", None)
    result = run_forecast(data)
    rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
    assert normalize_target_bounds(target, data) == (0.18, 0.22)
    for row in rows.values():
        assert row["target_low"] == 0.18 and row["target_high"] == 0.22
        assert row["unit"] == "ratio" and row.get("currency") is None
        assert row["target_value"] is None and row["attainment_ratio"] is None
        assert row["derived_revenue_benchmark"] is None


def test_group_native_forecast_report_and_dependencies_exclude_exited_segment():
    data = group_document()
    result = run_forecast(data)
    validate_published_forecast(result, data)
    target = result["management_target_coverage"]["targets"][0]
    assert target["scope"] == group_scope("Segment A", "Segment B")
    assert [target["scenario_comparison"][s]["modeled_value"] for s in SCENARIOS] == pytest.approx([150, 181.5, 216])
    assert result["consolidated_forecast"]["base"]["annual_revenue"]["2027"] == pytest.approx(191.5)
    parameters = {p["parameter_id"]: p for p in data["parameters"]}
    components = scope_components(data, parameters, target["scope"], "base", 2027)
    assert set(components) == {"Segment A", "Segment B"}
    assert all(not pid.startswith("excluded_") for refs in components.values() for pid in refs)
    assert "Continuing services" in render_markdown(result)


@pytest.mark.parametrize("members,reason", [
    ([], "segment_group_members_required"),
    (["Segment A", "Segment A"], "segment_group_duplicate_member"),
    (["Segment A", "Unknown"], "segment_group_unknown_member"),
    (["Segment A", {"type": "segment_group", "name": "Nested"}], "segment_group_member_must_be_name"),
])
def test_group_scope_rejects_unknown_duplicate_or_nested_members(members, reason):
    data = group_document()
    data["management_targets"][0]["scope"]["segment_names"] = members
    with pytest.raises(ForecastInputError, match=reason):
        run_forecast(data)


def test_group_does_not_allow_implicit_company_adjustments():
    data = group_document()
    data["management_targets"][0]["scope"]["adjustment_names"] = ["company-only"]
    with pytest.raises(ForecastInputError, match="segment_group_fields_are_not_exact"):
        run_forecast(data)


def test_group_mapping_cannot_point_only_to_exited_or_one_selected_member():
    for member_index in (1, 2):
        data = group_document()
        data["management_targets"][0]["mapped_parameter_ids"] = [
            data["segments"][member_index]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
        ]
        with pytest.raises(ForecastInputError, match="segment_group_parameter_ancestry_mismatch"):
            run_forecast(data)


def test_quarter_group_uses_same_native_scope_ancestry():
    data = quarter_document()
    data["management_targets"][0]["scope"] = group_scope("Segment A")
    result = run_forecast(data)
    assert result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]["modeled_value"] == 108000
    data["management_targets"][0]["scope"] = group_scope("Segment A", "Segment B")
    with pytest.raises(ForecastInputError, match="native component ancestry"):
        run_forecast(data)


def result_fixture():
    """An unrelated three-business company: actual effective, not raw recognized, income."""
    segments = []
    for name, base, values in (("Cloud", 60, [66, 72, 78]), ("Support", 40, [44, 48, 52]), ("Legacy", 100, [50, 50, 50])):
        segments.append({"name": name, "base_revenue": base, "scenarios": {
            s: {"recognized_revenue": {"2026": value + 20}, "effective_revenue": {"2026": value}}
            for s, value in zip(SCENARIOS, values)
        }})
    return {"company_name": "Other company", "currency": "USD", "unit": "million", "base_year": 2025,
            "base_revenue": 200, "segments": segments, "parameter_trace": [],
            "consolidated_forecast": {s: {"annual_revenue": {"2026": value}}
                                      for s, value in zip(SCENARIOS, [160, 170, 180])}}


def measured_target():
    return {"scope": group_scope("Cloud", "Support"), "treatment": "independent_benchmark", "mapped_scenarios": list(SCENARIOS),
            "raw_target_value": None, "raw_target_value_low": 18, "raw_target_value_high": 22,
            "raw_currency": "dimensionless", "raw_unit": "percent", "raw_scale": "percent", "comparison": "approximately",
            "comparison_basis": {"schema_version": "management-target-comparison/1", "metric_kind": "year_over_year_growth",
                                 "period": "FY2026", "base_period": "FY2025", "raw_ratio_basis": "percent"}}


def test_group_yoy_uses_same_members_in_base_and_effective_future():
    result = result_fixture()
    rows = compare_target_measurement(measured_target(), result)
    assert [rows[s]["modeled_value"] for s in SCENARIOS] == pytest.approx([0.1, 0.2, 0.3])
    assert all(row["base_value"] == 100 for row in rows.values())
    assert [rows[s]["numerator_value"] for s in SCENARIOS] == [110, 120, 130]
    assert all(row["target_value"] is None for row in rows.values())


@pytest.mark.parametrize("fault,reason", [("missing", "missing_base_period"), ("zero", "nonpositive_base_revenue"), ("negative", "nonpositive_base_revenue")])
def test_group_missing_and_nonpositive_base_are_named_gaps(fault, reason):
    result = result_fixture()
    if fault == "missing":
        del result["segments"][0]["base_revenue"]
    else:
        result["segments"][0]["base_revenue"] = 0 if fault == "zero" else -100
        result["segments"][1]["base_revenue"] = 0
    rows = compare_target_measurement(measured_target(), result)
    assert all(row["reason"] == reason and row["modeled_value"] is None for row in rows.values())


def test_group_missing_member_period_is_not_summed_as_zero():
    result = result_fixture()
    del result["segments"][1]["scenarios"]["base"]["effective_revenue"]["2026"]
    rows = compare_target_measurement(measured_target(), result)
    assert rows["base"]["reason"] == "missing_numerator_period"
    assert rows["base"]["modeled_value"] is None
    assert rows["low"]["modeled_value"] == pytest.approx(0.1)


@pytest.mark.parametrize("field,value,reason", [("currency", "CNY", "currency mismatch"), ("scale", "billion", "scale mismatch")])
def test_group_does_not_bypass_existing_money_or_fx_validation(field, value, reason):
    data = group_document()
    pid = data["segments"][1]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
    next(p for p in data["parameters"] if p["parameter_id"] == pid)[field] = value
    with pytest.raises(ForecastInputError, match=reason):
        run_forecast(data)


def test_group_cannot_count_one_native_base_again_under_another_member_name():
    from research.target_scope import resolve_scope_segments
    data = {"segments": [{"name": "Parent", "base_revenue_parameter_id": "same_flow"},
                         {"name": "Child alias", "base_revenue_parameter_id": "same_flow"}]}
    with pytest.raises(ForecastInputError, match="segment_group_overlapping_base"):
        resolve_scope_segments(data, group_scope("Parent", "Child alias"))


def test_custom_scope_stays_unresolved_and_old_non_typed_shape_is_not_guessed():
    from research.target_scope import resolve_scope_segments
    data = group_document()
    target = data["management_targets"][0]
    target.update(scope={"type": "custom", "name": "Segment A"}, treatment="unmodeled_data_gap",
                  comparison_value=None, mapped_parameter_ids=[], mapped_scenarios=[])
    result = run_forecast(data)
    assert result["management_target_coverage"]["targets"][0]["scenario_comparison"] == {}
    assert resolve_scope_segments(data, target["scope"]) == ()
    target.pop("comparison_basis")
    target["scope"] = group_scope("Segment A")
    with pytest.raises(ForecastInputError, match="segment_group_requires_typed_comparison"):
        run_forecast(data)


def test_group_old_recognized_path_fallback_and_signed_company_adjustment_exclusion():
    result = result_fixture()
    for segment in result["segments"]:
        for output in segment["scenarios"].values():
            output.pop("effective_revenue")
    rows = compare_target_measurement(measured_target(), result)
    # Original fallback: 92+68=160; unrelated company aggregate stays 170.
    assert rows["base"]["numerator_value"] == 160
    assert rows["base"]["modeled_value"] == pytest.approx(0.6)
    assert result["consolidated_forecast"]["base"]["annual_revenue"]["2026"] == 170


def test_typed_ratio_declared_fraction_is_identity_and_pp_is_not_a_yoy_level():
    data = yoy_document()
    target = data["management_targets"][0]
    target.update(raw_target_value=0.18, raw_unit="ratio", raw_scale="units", comparison_value=0.18)
    target["comparison_basis"]["raw_ratio_basis"] = "fraction"
    for claim in data["evidence_claims"]:
        if claim["claim_id"] in target["claim_ids"]:
            claim.update(unit="ratio", extracted_value=0.18)
    result = run_forecast(data)
    assert result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]["target_value"] == 0.18
    target["comparison_basis"]["raw_ratio_basis"] = "percentage_points"
    with pytest.raises(ForecastInputError, match="raw_ratio_basis"):
        run_forecast(data)


def test_group_comparison_tamper_is_rejected_against_frozen_model():
    data = group_document()
    result = run_forecast(data)
    target = result["management_target_coverage"]["targets"][0]
    target["scenario_comparison"]["base"]["modeled_value"] = 191.5
    with pytest.raises(ForecastInputError, match="typed management target comparison recomputation mismatch"):
        validate_published_forecast(result, data)


def test_continuing_business_frozen_external_review_arithmetic_anchor():
    # Values copied from initial frozen model and an independent reviewer,
    # not generated by the implementation. Amounts are CNY million. The small
    # group-base rounding difference is explicit: sum rounded segment bases.
    bases = [36465.8469, 4041.701, 2677.175, 236.1008]
    future = {"low": [40841.748528, 3839.61595, 2596.85975, 177.0756],
              "base": [43759.01628, 4203.36904, 2837.8055, 212.49072],
              "high": [46676.284032, 4445.8711, 2998.436, 236.1008]}
    result = result_fixture()
    result.update(currency="CNY", base_revenue=45456.16577418)
    result["segments"] = [{"name": "Continuing " + str(i), "base_revenue": base,
        "scenarios": {s: {"recognized_revenue": {"2026": future[s][i]}} for s in SCENARIOS}}
        for i, base in enumerate(bases)]
    result["segments"].append({"name": "Discontinued", "base_revenue": 2035.342,
        "scenarios": {s: {"recognized_revenue": {"2026": 0}} for s in SCENARIOS}})
    target = measured_target()
    target["scope"] = group_scope(*(segment["name"] for segment in result["segments"][:4]))
    rows = compare_target_measurement(target, result)
    expected = {"low": 0.0929156967043463, "base": 0.17484370740716337, "high": 0.25185768604823533}
    for scenario in SCENARIOS:
        assert rows[scenario]["base_value"] == pytest.approx(43420.8237)
        assert rows[scenario]["modeled_value"] == pytest.approx(expected[scenario], abs=2e-9)
    assert rows["base"]["modeled_value"] != pytest.approx(0.122238990881)


@pytest.mark.parametrize("growth", [False, True])
def test_native_cli_group_validate_publish_render_snapshot(growth, tmp_path):
    import json
    import subprocess
    data = group_document()
    target = data["management_targets"][0]
    if growth:
        target.update(target_period="FY2026", measurement_periods=["FY2026"], raw_unit="percent",
                      raw_currency="dimensionless", raw_scale="percent", raw_target_value=18,
                      comparison_value=0.18, comparison_currency=None, comparison_scale=None,
                      comparison_basis={"schema_version": "management-target-comparison/1",
                          "metric_kind": "year_over_year_growth", "period": "FY2026",
                          "base_period": "FY2025", "raw_ratio_basis": "percent"},
                      mapped_parameter_ids=[s["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
                                            for s in data["segments"][:2]])
        for claim in data["evidence_claims"]:
            if claim["claim_id"] in target["claim_ids"]:
                claim.update(extracted_value=18, unit="percent", period="FY2026")
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "published"
    completed = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tools/run_target_measurement_e2e.py"),
        "--input", str(input_path), "--output-root", str(output), "--version", "r1-group-fixture-v1"],
        capture_output=True, encoding="utf-8", timeout=30, check=False)
    assert completed.returncode == 0, completed.stderr
    receipt = json.loads((output / "commands.json").read_text(encoding="utf-8"))
    assert [event["exit_code"] for event in receipt["events"]] == [0, 0, 0]
    assert receipt["supplier_calls"] == receipt["model_calls"] == 0
    result = json.loads((output / "forecast.json").read_text(encoding="utf-8"))
    snapshot = json.loads((output / "snapshot.json").read_text(encoding="utf-8"))
    assert snapshot and "Continuing services" in (output / "forecast.md").read_text(encoding="utf-8")
    rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
    if growth:
        assert [rows[s]["modeled_value"] for s in SCENARIOS] == pytest.approx([0, 0.1, 0.2])
    else:
        assert [rows[s]["modeled_value"] for s in SCENARIOS] == pytest.approx([150, 181.5, 216])



def test_typed_growth_canonical_comparison_has_no_contextual_money_currency():
    data = yoy_document()
    raw_target = data["management_targets"][0]
    raw_target.update(comparison_currency="CNY", comparison_scale="million")
    result = run_forecast(data)
    validate_published_forecast(result, data)
    canonical = result["management_target_coverage"]["targets"][0]
    assert canonical["raw_currency"] == "dimensionless"
    assert canonical["comparison_currency"] is None and canonical["comparison_scale"] is None
    assert raw_target["comparison_currency"] == "CNY"  # Input is not rewritten.
    assert canonical["scenario_comparison"]["base"]["derived_revenue_benchmark"]["unit"] == "USD million"
