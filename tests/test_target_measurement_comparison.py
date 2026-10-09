"""W05 native quarterly/YoY benchmarks and truthful communication intervals."""
from copy import deepcopy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from revenue_report import render_markdown, validate_published_forecast  # noqa: E402
from test_independent_targets import benchmark_document  # noqa: E402
from test_recognition_bridge import forecast_document, add_parameter  # noqa: E402
from test_data_contract import finalize_contract  # noqa: E402
from test_management_targets import add_target  # noqa: E402


def yoy_document():
    data = benchmark_document()
    target = data["management_targets"][0]
    target.update(raw_target_value=70, raw_unit="percent", raw_currency="dimensionless", raw_scale="percent",
                  comparison_value=0.70, comparison_currency=None, comparison_scale=None,
                  statement="Revenue is expected to grow approximately 70 percent year over year.",
                  comparison="approximately",
                  comparison_basis={"schema_version": "management-target-comparison/1", "metric_kind": "year_over_year_growth",
                                    "period": "FY2027", "base_period": "FY2026", "raw_ratio_basis": "percent"})
    for claim in data["evidence_claims"]:
        if claim["claim_id"] in target["claim_ids"]:
            claim.update(extracted_value=70, unit="percent")
    return data


def quarter_document():
    data = forecast_document()
    segment = data["segments"][0]
    quarter_ids = {}
    for scenario, value in (("low", 105840), ("base", 108000), ("high", 110160)):
        pid = add_parameter(data, "quarter_" + scenario, value, 2026, scenario)
        next(p for p in data["parameters"] if p["parameter_id"] == pid)["measurement_period"] = "FY2026Q3"
        quarter_ids[scenario] = [pid]
        annual_id = segment["scenarios"][scenario]["driver_parameter_ids"]["revenue"][0]
        annual = next(p for p in data["parameters"] if p["parameter_id"] == annual_id)
        annual.update(kind="derived_fact", value=value + 300000, formula="x0 + 300000", input_parameter_ids=[pid])
    finalize_contract(data)
    add_target(data, period="FY2026", target_value=108, treatment="independent_benchmark",
               measurement_basis="quarterly_period", measurement_periods=[])
    target = data["management_targets"][0]
    target.update(target_quarter="Q3", raw_target_value=None, raw_value_kind="numeric_range",
                  raw_target_value_low=105.84, raw_target_value_high=110.16, raw_unit="USD billion",
                  raw_currency="USD", raw_scale="billion", comparison_value=None, comparison="approximately",
                  mapped_scenarios=["low", "base", "high"], mapped_parameter_ids=quarter_ids["base"],
                  benchmark_rationale="Quarter inputs enter the explicit annual bridge.", benchmark_claim_ids=["quarter_benchmark"],
                  comparison_basis={"schema_version": "management-target-comparison/1", "metric_kind": "quarterly_revenue_level",
                                    "period": "FY2026Q3", "scenario_parameter_ids": quarter_ids})
    claim = next(c for c in data["evidence_claims"] if c["claim_id"] in target["claim_ids"])
    claim.pop("extracted_value", None)
    claim["unit"] = "USD billion"
    other = deepcopy(claim)
    other.update(claim_id="quarter_benchmark", support_type="rationale_support")
    data["evidence_claims"].append(other)
    return data


def test_quarter_band_uses_actual_quarter_bridge_without_times_four():
    data = quarter_document()
    result = run_forecast(data)
    validate_published_forecast(result, data)
    target = result["management_target_coverage"]["targets"][0]
    for scenario, amount in (("low", 105840), ("base", 108000), ("high", 110160)):
        comparison = target["scenario_comparison"][scenario]
        assert comparison["modeled_value"] == amount
        assert comparison["target_low"] == pytest.approx(105840)
        assert comparison["target_high"] == pytest.approx(110160)
        assert comparison["period"] == "FY2026Q3"
        assert comparison["unit"] == "USD million"
        assert comparison["meets_target"] is True
    assert target["comparison"] == "approximately"


def test_yoy_uses_each_scenario_denominator_and_separate_derived_dollars():
    data = yoy_document()
    result = run_forecast(data)
    validate_published_forecast(result, data)
    target = result["management_target_coverage"]["targets"][0]
    for scenario, growth in (("low", 0), ("base", 0.1), ("high", 0.2)):
        row = target["scenario_comparison"][scenario]
        assert row["modeled_value"] == pytest.approx(growth)
        assert row["target_value"] == pytest.approx(0.70)
        assert row["difference_percentage_points"] == pytest.approx((growth - 0.70) * 100)
        assert row["derived_revenue_benchmark"]["origin"] == "analyst_derived"
        assert row["derived_revenue_benchmark"]["value"] == pytest.approx(row["base_value"] * 1.70)
    markdown = render_markdown(result)
    assert "FY2026" in markdown and "FY2027" in markdown
    assert "percentage_points" in markdown
    assert "70 percent" in markdown


def test_zero_or_missing_yoy_denominator_is_not_comparable():
    data = yoy_document()
    result = run_forecast(data)
    from research.target_measurement import compare_target_measurement
    target = result["management_target_coverage"]["targets"][0]
    for scenario in ("low", "base", "high"):
        result["segments"][0]["scenarios"][scenario]["recognized_revenue"].pop("2026")
        result["segments"][0]["scenarios"][scenario]["effective_revenue"].pop("2026")
    comparisons = compare_target_measurement(target, result)
    for row in comparisons.values():
        assert row["modeled_value"] is None and row["meets_target"] is None
        assert row["comparison_status"] == "not_comparable"
        assert row["reason"] == "missing_base_period"


def test_strict_relative_bound_is_growth_above_one_and_unknown_period_stays_unknown():
    from research.target_measurement import normalize_target_bounds
    data = yoy_document()
    target = data["management_targets"][0]
    target.update(raw_target_value=2, comparison="greater_than")
    target["comparison_basis"]["raw_ratio_basis"] = "level_multiple"
    assert normalize_target_bounds(target, data)[0] == 1


def test_typed_comparison_refuses_unused_quarter_parameter_and_output_tamper():
    data = quarter_document()
    data["management_targets"][0]["comparison_basis"]["scenario_parameter_ids"]["base"] = ["a_growth_2026_base"]
    with pytest.raises(ForecastInputError, match="used"):
        run_forecast(data)
    data = yoy_document()
    result = run_forecast(data)
    result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]["base_value"] = 1
    with pytest.raises(ForecastInputError):
        validate_published_forecast(result, data)


def test_existing_annual_target_keeps_the_original_output_shape():
    result = run_forecast(benchmark_document())
    row = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]
    assert set(row) == {"measurement_basis", "measurement_periods", "modeled_period_values",
                        "modeled_value", "target_value", "attainment_ratio", "meets_target"}


def test_source_presence_is_not_post_filing_interval_coverage():
    from research.communication_scope import analyze_communication_scope
    data = forecast_document()
    sources = {s["source_id"]: s for s in data["sources"]}
    record = data["management_communication_coverage"][-1]
    diagnostic = analyze_communication_scope(record, sources, data["as_of_date"])
    assert diagnostic["coverage_complete"] is False
    assert diagnostic["status"] == "semantically_unverified"
    record["checked_scope"] = {"schema_version": "management-communication-scope/1", "category": record["category"],
                                "start_date": sources["filing"]["published_date"], "end_date": data["as_of_date"],
                                "coverage_complete": False, "items": [{"item_ref": "notice", "source_id": "filing",
                                "content_role": "index_notice", "selected": True, "read": True, "skip_reason": None}]}
    with pytest.raises(ForecastInputError, match="business original"):
        analyze_communication_scope(record, sources, data["as_of_date"])


def test_zero_denominator_stays_null_in_native_output():
    data = yoy_document()
    for scenario in ("low", "base", "high"):
        pid = data["segments"][0]["scenarios"][scenario]["driver_parameter_ids"]["revenue"][0]
        next(p for p in data["parameters"] if p["parameter_id"] == pid)["value"] = 0
    result = run_forecast(data)
    for row in result["management_target_coverage"]["targets"][0]["scenario_comparison"].values():
        assert row["base_value"] == 0
        assert row["modeled_value"] is None
        assert row["difference_percentage_points"] is None
        assert row["reason"] == "nonpositive_base_revenue"


def test_native_partial_coverage_and_legacy_diagnostics_are_explicit():
    data = forecast_document()
    data["audit_communication_coverage"] = True
    result = run_forecast(data)
    assert result["management_target_coverage"]["communications"][-1]["coverage_diagnostic"]["status"] == "semantically_unverified"
    assert any(gap.startswith("management_communication:") for gap in result["data_gaps"])
    record = data["management_communication_coverage"][-1]
    record["checked_scope"] = {"schema_version": "management-communication-scope/1", "category": record["category"],
                                "start_date": data["sources"][0]["published_date"], "end_date": data["as_of_date"],
                                "coverage_complete": False, "items": [{"item_ref": "original", "source_id": "filing",
                                "content_role": "business_original", "selected": True, "read": True, "skip_reason": None}]}
    result = run_forecast(data)
    assert result["management_target_coverage"]["communications"][-1]["status"] == "incomplete"
    record["checked_scope"]["end_date"] = "2026-01-01"
    with pytest.raises(ForecastInputError, match="interval|as_of_date"):
        run_forecast(data)


def test_unavailable_quarter_comparison_does_not_create_conversion_or_require_duplicate_reason():
    data = quarter_document()
    target = data["management_targets"][0]
    target.update(treatment="unmodeled_data_gap", mapped_scenarios=[], mapped_parameter_ids=[], raw_currency="EUR")
    target["comparison_basis"]["scenario_parameter_ids"] = None
    result = run_forecast(data)
    assert not result["management_target_coverage"]["targets"][0]["scenario_comparison"]
    assert any("management_target:" in gap for gap in result["data_gaps"])
    assert "unmodeled_data_gap" in render_markdown(result)


def test_recipe_runs_actual_native_validation_compute_and_snapshot(tmp_path):
    import json
    import subprocess
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(quarter_document()), encoding="utf-8")
    output = tmp_path / "published"
    completed = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tools/run_target_measurement_e2e.py"),
                                "--input", str(input_path), "--output-root", str(output), "--version", "typed-quarter-fixture-v1"],
                               capture_output=True, encoding="utf-8", timeout=30, check=False)
    assert completed.returncode == 0, completed.stderr
    receipt = json.loads((output / "commands.json").read_text(encoding="utf-8"))
    assert [event["exit_code"] for event in receipt["events"]] == [0, 0, 0]
    assert (output / "forecast.md").is_file() and (output / "snapshot.json").is_file()
    assert receipt["supplier_calls"] == 0


def test_boundary_filing_alone_does_not_complete_post_filing_content_scope():
    from research.communication_scope import analyze_communication_scope
    sources={"annual":{"source_type":"regulatory_filing","published_date":"2026-02-20"}}
    record={"category":"material_announcements_since_last_filing","source_ids":["annual"],
        "checked_scope":{"schema_version":"management-communication-scope/1","category":"material_announcements_since_last_filing",
            "start_date":"2026-02-20","end_date":"2026-10-09","coverage_complete":True,
            "items":[{"item_ref":"annual","source_id":"annual","published_date":"2026-02-20","content_role":"business_original","selected":True,"read":True}]}}
    diagnostic=analyze_communication_scope(record,sources,"2026-10-09")
    assert diagnostic["coverage_complete"] is False
    assert diagnostic["reason"]=="boundary_filing_does_not_cover_later_interval"


def test_annual_filing_does_not_prove_a_checked_earnings_call():
    from research.communication_scope import analyze_communication_scope
    category="latest_earnings_call"
    scope={"schema_version":"management-communication-scope/1","category":category,"start_date":"2026-02-20","end_date":"2026-10-09","coverage_complete":True,
        "items":[{"item_ref":"annual","source_id":"annual","content_role":"business_original","selected":True,"read":True}]}
    record={"category":category,"source_ids":["annual"],"checked_scope":scope}
    diagnostic=analyze_communication_scope(record,{"annual":{"source_type":"regulatory_filing","published_date":"2026-02-20"}},"2026-10-09")
    assert not diagnostic["coverage_complete"] and diagnostic["reason"]=="source_category_not_supported"
