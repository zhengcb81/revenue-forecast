"""Public output consumer tests for additive forecast schemas."""
from __future__ import annotations
import copy
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from revenue_core import ForecastInputError, canonical_sha256, run_forecast
from revenue_report import render_markdown, validate_published_forecast, validate_legacy_output
from test_recognition_bridge import forecast_document
from test_m3_period_flow_contract import add_flow_parameter

@pytest.mark.parametrize("schema", ["3.7", "3.8", "3.9"])
@pytest.mark.parametrize("mutation", ["missing_growth", "invalid_growth", "missing_workflow", "forged_workflow", "missing_management", "forged_management"])
def test_modern_output_consumers_reject_rehashed_semantic_mutations(schema, mutation):
    data = forecast_document()
    data["schema_version"] = schema
    result = run_forecast(data)
    if mutation == "missing_growth":
        del result["growth_driver_analysis"]
    elif mutation == "invalid_growth":
        result["growth_driver_analysis"]["status"] = "fabricated"
    elif mutation == "missing_workflow":
        del result["workflow_compliance_receipt"]
    elif mutation == "forged_workflow":
        result["workflow_compliance_receipt"]["freeform_formal_output_allowed"] = True
    elif mutation == "missing_management":
        del result["management_target_coverage"]
    elif mutation == "forged_management":
        result["management_target_coverage"]["counts"]["targets_total"] += 1
    result["result_sha256"] = canonical_sha256({k:v for k,v in result.items() if k != "result_sha256"})
    with pytest.raises(ForecastInputError):
        validate_published_forecast(result, data)

@pytest.mark.parametrize("schema", ["3.7", "3.8", "3.9"])
def test_modern_output_needs_bound_input_in_all_consumer_paths(schema):
    data = forecast_document()
    data["schema_version"] = schema
    result = run_forecast(data)
    result.pop("input_document", None)
    result["result_sha256"] = canonical_sha256({k:v for k,v in result.items() if k != "result_sha256"})
    with pytest.raises(ForecastInputError, match="bound input"):
        validate_legacy_output(result)

def test_report_discloses_partial_year_window_without_annualizing():
    data = forecast_document()
    data["schema_version"] = "3.9"
    add_flow_parameter(data, "half_year_observation", 55, "2026-01-01", "2026-06-30", 2026)
    result = run_forecast(copy.deepcopy(data))
    before = copy.deepcopy(result["consolidated_forecast"])
    text = render_markdown(result)
    row = next(line for line in text.splitlines() if "half_year_observation" in line)
    assert "period_flow" in row
    assert "2026-01-01" in row and "2026-06-30" in row
    assert "55.00" in row
    assert result["consolidated_forecast"] == before


@pytest.mark.parametrize("second_window,second_value,allowed", [
    (("2025-07-01", "2025-12-31"), 65, True),
    (("2025-01-01", "2025-03-31"), 25, True),
    (("2025-01-01", "2025-06-30"), 65, False),
])
def test_parameter_fact_conflict_identity_includes_the_actual_time_window(second_window, second_value, allowed):
    from revenue_core import validate_document
    data = forecast_document()
    data["schema_version"] = "3.9"
    definition = "Segment A recognized revenue"
    add_flow_parameter(data, "window_first", 55, "2025-01-01", "2025-06-30", 2025, definition=definition)
    add_flow_parameter(data, "window_second", second_value, *second_window, 2025, definition=definition)
    if allowed:
        validated = validate_document(data)
        assert validated["parameter_index"]["window_first"]["value"] == 55
        assert validated["parameter_index"]["window_second"]["value"] == second_value
        result = run_forecast(copy.deepcopy(data))
        validate_published_forecast(result, data)
    else:
        with pytest.raises(ForecastInputError, match="conflict|resolution"):
            validate_document(data)
