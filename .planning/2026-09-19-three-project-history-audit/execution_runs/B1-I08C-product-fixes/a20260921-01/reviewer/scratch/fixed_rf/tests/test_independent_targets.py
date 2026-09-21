"""Management targets are testable benchmarks, not mandatory analyst beliefs."""
from __future__ import annotations
import copy
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_management_targets import add_target  # noqa: E402
from test_recognition_bridge import forecast_document, add_parameter  # noqa: E402


def benchmark_document():
    data = add_target(forecast_document(), target_value=1000, treatment="independent_benchmark")
    target = data["management_targets"][0]
    target.update({
        "mapped_scenarios": ["low", "base", "high"],
        "mapped_parameter_ids": [data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]],
        "benchmark_rationale": "Contracted capacity and customer demand do not support the aspiration.",
        "benchmark_claim_ids": ["benchmark_evidence"],
    })
    claim = copy.deepcopy(data["evidence_claims"][-1])
    claim.update({"claim_id": "benchmark_evidence", "support_type": "rationale_support"})
    data["evidence_claims"].append(claim)
    return data


def test_independent_view_can_miss_target_in_every_scenario_and_validate():
    data = benchmark_document()
    result = run_forecast(data)
    validate_published_forecast(result, data)
    comparisons = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
    assert set(comparisons) == {"low", "base", "high"}
    assert all(not row["meets_target"] for row in comparisons.values())
    assert result["consolidated_forecast"]["base"]["annual_revenue"]["2027"] == pytest.approx(181.5)
    assert result["management_target_coverage"]["counts"]["targets_unmodeled"] == 0
    assert result["management_target_coverage"]["counts"]["targets_independent_benchmarks"] == 1


@pytest.mark.parametrize("field", ["benchmark_rationale", "benchmark_claim_ids", "mapped_parameter_ids"])
def test_independent_benchmark_cannot_be_an_unsupported_escape_hatch(field):
    data = benchmark_document()
    del data["management_targets"][0][field]
    with pytest.raises(ForecastInputError):
        run_forecast(data)


def test_period_end_run_rate_cannot_silently_equal_annual_revenue():
    data = forecast_document()
    pid = add_parameter(data, "recognition_fraction", 1.0, 2027, "all", dimension="ratio")
    data = add_target(data, measurement_basis="run_rate_at_period_end")
    with pytest.raises(ForecastInputError, match="explicit annual recognized revenue conversion"):
        run_forecast(data)
    data["management_targets"][0]["comparison_basis"] = "annual_recognized_revenue"
    data["management_targets"][0]["normalization_rationale"] = "Constant monthly recognized revenue makes the ending annualized rate equal to the full fiscal year."
    data["management_targets"][0]["normalization_parameter_ids"] = [pid]
    data["management_targets"][0]["normalization_formula"] = "x0 * x1"
    run_forecast(data)
    data["management_targets"][0]["comparison_value"] = 150
    with pytest.raises(ForecastInputError, match="normalization recomputation mismatch"):
        run_forecast(data)


def test_unconverted_run_rate_can_remain_explicit_data_gap():
    data = add_target(forecast_document(), measurement_basis="run_rate_at_period_end", treatment="unmodeled_data_gap")
    data["management_targets"][0]["comparison_value"] = None
    result = run_forecast(data)
    assert result["management_target_coverage"]["counts"]["targets_unmodeled"] == 1


def test_approximately_uses_revenue_units_consistently_in_output_validator():
    data = add_target(forecast_document(), target_value=144)
    data["management_targets"][0]["comparison"] = "approximately"
    run_forecast(data)


def test_zero_revenue_target_does_not_require_an_attainment_ratio():
    data = add_target(forecast_document(), target_value=0)
    result = run_forecast(data)
    comparison = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
    assert comparison["meets_target"] is True
    assert comparison["attainment_ratio"] is None
