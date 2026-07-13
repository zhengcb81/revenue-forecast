from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, canonical_sha256, run_forecast, text_sha256  # noqa: E402
from revenue_report import render_markdown, validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def add_target(
    data: dict,
    *,
    target_value: float = 144.0,
    period: str = "FY2027",
    treatment: str = "scenario_boundary",
    perimeter_status: str = "matched",
    measurement_basis: str = "annual_period",
    measurement_periods: list[str] | None = None,
) -> dict:
    target_id = "five_year_revenue_goal"
    comparable = perimeter_status != "mismatch" and measurement_basis != "ambiguous"
    mapped_ids = []
    mapped_scenarios = []
    if treatment in {"modeled_scenario", "scenario_boundary"}:
        mapped_ids = [data["segments"][0]["scenarios"]["high"]["driver_parameter_ids"]["revenue"][-1]]
        mapped_scenarios = ["high"]
    claim_id = "claim_five_year_revenue_goal"
    excerpt = "Management targets at least USD 144 million of segment revenue by fiscal year 2027."
    data["evidence_claims"].append({
        "claim_id": claim_id,
        "source_id": "filing",
        "target_type": "management_target",
        "target_id": target_id,
        "support_type": "exact_value",
        "locator": "Strategy section",
        "excerpt": excerpt,
        "excerpt_sha256": text_sha256(excerpt),
        "content_sha256": "a" * 64,
        "verification_status": "opened_and_checked",
        "verified_by": "target-test",
        "verified_date": data["as_of_date"],
        "extracted_value": target_value,
        "unit": "USD million",
        "period": period,
    })
    data["management_targets"] = [{
        "target_id": target_id,
        "statement": "Reach at least USD 144 million of annual segment revenue.",
        "metric_name": "segment revenue",
        "metric_definition": "recognized annual revenue of Segment A",
        "target_period": period,
        "raw_target_value": target_value,
        "raw_unit": "USD million",
        "raw_currency": "USD",
        "raw_scale": "million",
        "measurement_basis": measurement_basis,
        "measurement_periods": measurement_periods if measurement_periods is not None else ([] if measurement_basis == "ambiguous" else [period]),
        "measurement_rationale": "The source target is interpreted using the explicitly registered model periods.",
        "materiality": "material",
        "commitment_strength": "goal",
        "scope": {"type": "segment", "name": "Segment A"},
        "perimeter_status": perimeter_status,
        "perimeter_notes": "The target metric matches the modeled segment perimeter.",
        "comparison": "at_least",
        "comparison_value": target_value if comparable else None,
        "comparison_currency": "USD" if comparable else None,
        "comparison_scale": "million" if comparable else None,
        "normalization_rationale": "Source and model use the same currency, unit and revenue definition.",
        "treatment": treatment,
        "mapped_parameter_ids": mapped_ids,
        "mapped_scenarios": mapped_scenarios,
        "claim_ids": [claim_id],
        "rationale": "Material management target must be visible in the scenario set or as an explicit gap.",
    }]
    call_record = next(record for record in data["management_communication_coverage"] if record["category"] == "latest_earnings_call")
    call_record["material_revenue_target_ids"] = [target_id]
    call_record["conclusion"] = "The earnings call contains one material forward revenue target."
    return data


class ManagementTargetCoverageTests(unittest.TestCase):
    def test_missing_communication_category_is_rejected(self) -> None:
        data = forecast_document()
        data["management_communication_coverage"].pop()
        with self.assertRaisesRegex(ForecastInputError, "every required category"):
            run_forecast(data)

    def test_unregistered_target_id_is_rejected(self) -> None:
        data = forecast_document()
        data["management_communication_coverage"][0]["material_revenue_target_ids"] = ["missing_target"]
        with self.assertRaisesRegex(ForecastInputError, "must match management_targets"):
            run_forecast(data)

    def test_material_in_horizon_target_must_enter_scenario(self) -> None:
        data = add_target(forecast_document(), treatment="sensitivity_only")
        with self.assertRaisesRegex(ForecastInputError, "must enter a scenario"):
            run_forecast(data)

    def test_mapped_high_scenario_must_numerically_meet_target(self) -> None:
        data = add_target(forecast_document(), target_value=147.0)
        with self.assertRaisesRegex(ForecastInputError, "does not satisfy management target"):
            run_forecast(data)

    def test_mapped_target_is_disclosed_and_rendered(self) -> None:
        result = run_forecast(add_target(forecast_document()))
        validate_forecast_output(result)
        target = result["management_target_coverage"]["targets"][0]
        self.assertAlmostEqual(target["scenario_comparison"]["high"]["attainment_ratio"], 1.0)
        self.assertIn("## 管理层沟通与营收目标覆盖", render_markdown(result))

    def test_cumulative_target_sums_every_registered_period(self) -> None:
        result = run_forecast(add_target(
            forecast_document(),
            target_value=260.0,
            period="FY2026-FY2027",
            measurement_basis="cumulative_periods",
            measurement_periods=["FY2026", "FY2027"],
        ))
        comparison = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        self.assertEqual(comparison["measurement_basis"], "cumulative_periods")
        self.assertEqual(comparison["measurement_periods"], ["FY2026", "FY2027"])
        self.assertAlmostEqual(comparison["modeled_value"], sum(comparison["modeled_period_values"].values()))

    def test_ambiguous_measurement_cannot_be_mapped(self) -> None:
        data = add_target(forecast_document(), measurement_basis="ambiguous")
        with self.assertRaisesRegex(ForecastInputError, "must remain an unmodeled data gap"):
            run_forecast(data)

    def test_measurement_basis_is_required(self) -> None:
        data = add_target(forecast_document())
        data["management_targets"][0].pop("measurement_basis")
        with self.assertRaisesRegex(ForecastInputError, "measurement basis"):
            run_forecast(data)

    def test_immutable_schema_31_target_output_still_validates(self) -> None:
        legacy = run_forecast(add_target(forecast_document()))
        legacy["schema_version"] = "3.1"
        legacy["engine_version"] = "3.1.0"
        target = legacy["management_target_coverage"]["targets"][0]
        for field in ("measurement_basis", "measurement_periods", "measurement_rationale"):
            target.pop(field)
        for comparison in target["scenario_comparison"].values():
            for field in ("measurement_basis", "measurement_periods", "modeled_period_values"):
                comparison.pop(field)
        legacy["result_sha256"] = canonical_sha256({key: value for key, value in legacy.items() if key != "result_sha256"})
        validate_forecast_output(legacy)

    def test_immutable_engine_320_output_still_validates(self) -> None:
        legacy = run_forecast(add_target(forecast_document()))
        legacy["engine_version"] = "3.2.0"
        legacy["result_sha256"] = canonical_sha256({key: value for key, value in legacy.items() if key != "result_sha256"})
        validate_forecast_output(legacy)

    def test_immutable_engine_321_output_still_validates(self) -> None:
        legacy = run_forecast(add_target(forecast_document()))
        legacy["engine_version"] = "3.2.1"
        legacy["result_sha256"] = canonical_sha256({key: value for key, value in legacy.items() if key != "result_sha256"})
        validate_forecast_output(legacy)

    def test_out_of_horizon_target_is_propagated_as_gap(self) -> None:
        result = run_forecast(add_target(forecast_document(), target_value=250.0, period="FY2030", treatment="out_of_horizon"))
        self.assertTrue(any(gap.startswith("management_target:five_year_revenue_goal:") for gap in result["data_gaps"]))
        self.assertEqual(result["management_target_coverage"]["counts"]["targets_unmodeled"], 1)

    def test_tampered_target_attainment_is_rejected(self) -> None:
        result = run_forecast(add_target(forecast_document()))
        tampered = copy.deepcopy(result)
        tampered["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]["modeled_value"] += 1
        tampered["result_sha256"] = canonical_sha256({key: value for key, value in tampered.items() if key != "result_sha256"})
        with self.assertRaisesRegex(ForecastInputError, "management target modeled value mismatch"):
            validate_forecast_output(tampered)


if __name__ == "__main__":
    unittest.main()
