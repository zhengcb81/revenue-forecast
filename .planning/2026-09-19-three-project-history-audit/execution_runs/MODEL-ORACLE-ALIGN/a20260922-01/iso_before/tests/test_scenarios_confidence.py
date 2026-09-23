from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from test_data_contract import finalize_contract, update_parameter_value_and_claim  # noqa: E402
from test_recognition_bridge import add_parameter, forecast_document  # noqa: E402


class ScenarioConfidenceTests(unittest.TestCase):
    def test_probability_weighted_path(self) -> None:
        data = forecast_document()
        data["scenario_probabilities"] = {"low": 0.25, "base": 0.5, "high": 0.25}
        data["probability_rationale"] = "Calibrated scenario test"
        result = run_forecast(data)
        expected_2026 = 0.25 * 150 + 0.5 * 165 + 0.25 * 180
        self.assertAlmostEqual(result["probability_weighted_forecast"]["annual_revenue"]["2026"], expected_2026)

    def test_probabilities_require_rationale(self) -> None:
        data = forecast_document()
        data["scenario_probabilities"] = {"low": 0.25, "base": 0.5, "high": 0.25}
        with self.assertRaisesRegex(ForecastInputError, "probability_rationale"):
            run_forecast(data)

    def test_probabilities_must_sum_to_one(self) -> None:
        data = forecast_document()
        data["scenario_probabilities"] = {"low": 0.2, "base": 0.5, "high": 0.2}
        data["probability_rationale"] = "Invalid test"
        with self.assertRaisesRegex(ForecastInputError, "sum to 1"):
            run_forecast(data)

    def test_scenario_crossing_is_rejected(self) -> None:
        data = forecast_document()
        high_id = data["segments"][0]["scenarios"]["high"]["driver_parameter_ids"]["revenue"][0]
        for parameter in data["parameters"]:
            if parameter["parameter_id"] == high_id:
                parameter["value"] = 1
        with self.assertRaisesRegex(ForecastInputError, "scenario ordering"):
            run_forecast(data)

    def test_sensitivity_reruns_the_model(self) -> None:
        data = forecast_document()
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
        data["sensitivity_tests"] = [{"name": "Core terminal revenue", "parameter_id": parameter_id, "shock_type": "percent", "shock_value": 0.1}]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        self.assertGreater(sensitivity["up_terminal_revenue"], sensitivity["baseline_terminal_revenue"])
        self.assertLess(sensitivity["down_terminal_revenue"], sensitivity["baseline_terminal_revenue"])

    def test_sensitivity_requires_base_reference(self) -> None:
        data = forecast_document()
        low_id = data["segments"][0]["scenarios"]["low"]["driver_parameter_ids"]["revenue"][0]
        data["sensitivity_tests"] = [{"name": "Wrong scenario", "parameter_id": low_id, "shock_type": "percent", "shock_value": 0.1}]
        with self.assertRaisesRegex(ForecastInputError, "not referenced by the base"):
            run_forecast(data)

    def test_confidence_is_independent_of_growth_rate(self) -> None:
        low_growth = forecast_document()
        high_growth = copy.deepcopy(low_growth)
        for parameter in high_growth["parameters"]:
            if parameter.get("scenario") in {"low", "base", "high"} and parameter["parameter_id"].startswith(("0_", "1_")):
                parameter["value"] *= 1.5
        low_score = run_forecast(low_growth)["confidence"]["score"]
        high_score = run_forecast(high_growth)["confidence"]["score"]
        self.assertEqual(low_score, high_score)

    def test_confidence_hard_gates_are_not_constant_score_components(self) -> None:
        confidence = run_forecast(forecast_document())["confidence"]
        self.assertNotIn("base_reconciliation", confidence["components"])
        self.assertNotIn("recognition_basis", confidence["components"])
        self.assertNotIn("scenario_consistency", confidence["components"])
        self.assertTrue(all(confidence["quality_gates"].values()))

    def test_incremental_contribution_reconciles(self) -> None:
        result = run_forecast(forecast_document())
        base = result["consolidated_forecast"]["base"]
        self.assertAlmostEqual(base["incremental_contribution"]["total"], base["incremental_revenue"])

    def test_theme_elasticity_uses_explicit_counterfactual(self) -> None:
        data = forecast_document()
        counterfactual = {}
        for scenario, value in (("low", 90), ("base", 100), ("high", 110)):
            counterfactual[scenario] = add_parameter(data, f"counterfactual_{scenario}", value, 2027, scenario)
        data["theme_analysis"] = {
            "name": "Core theme",
            "segment_names": ["Segment A"],
            "counterfactual_terminal_parameter_ids": counterfactual,
        }
        result = run_forecast(data)
        theme = result["theme_analysis"]["scenarios"]["base"]
        self.assertAlmostEqual(theme["theme_incremental_revenue"], 21)
        self.assertAlmostEqual(theme["theme_elasticity_to_company_base"], 0.14)

    def test_research_gap_flows_to_output_without_changing_score(self) -> None:
        baseline_score = run_forecast(forecast_document())["confidence"]["score"]
        data = forecast_document()
        record = next(item for item in data["research_coverage"] if item["dimension"] == "policy")
        record.update({
            "status": "data_gap",
            "conclusion": "Policy award timing is not disclosed",
            "revenue_mechanism": "award timing could shift bookings and recognition",
            "rationale": "No source provides a reliable award calendar",
        })
        result = run_forecast(data)
        self.assertIn("policy: Policy award timing is not disclosed", result["data_gaps"])
        self.assertEqual(result["confidence"]["score"], baseline_score)
        self.assertTrue(any("Research coverage contains 1" in item for item in result["confidence"]["limitations"]))

    def test_duplicate_sensitivity_parameter_is_rejected(self) -> None:
        data = forecast_document()
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
        data["sensitivity_tests"] = [
            {"name": "One", "parameter_id": parameter_id, "shock_type": "percent", "shock_value": 0.1},
            {"name": "Two", "parameter_id": parameter_id, "shock_type": "absolute", "shock_value": 5},
        ]
        with self.assertRaisesRegex(ForecastInputError, "duplicate sensitivity parameter_id"):
            run_forecast(data)

    def test_zero_parameter_supports_absolute_sensitivity(self) -> None:
        data = forecast_document()
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
        parameter = next(item for item in data["parameters"] if item["parameter_id"] == parameter_id)
        parameter["value"] = 0
        low_id = data["segments"][0]["scenarios"]["low"]["driver_parameter_ids"]["revenue"][1]
        next(item for item in data["parameters"] if item["parameter_id"] == low_id)["value"] = 0
        data["sensitivity_tests"] = [{"name": "Zero base", "parameter_id": parameter_id, "shock_type": "absolute", "shock_value": 5}]
        result = run_forecast(data)
        self.assertEqual(result["sensitivities"][0]["effective_values"]["down"], 0)
        self.assertTrue(result["sensitivities"][0]["clamped"]["down"])

    def test_user_declared_source_rank_cannot_raise_confidence(self) -> None:
        high_rank = forecast_document()
        low_rank = forecast_document()
        high_rank["sources"][0]["source_type"] = "audited_filing"
        low_rank["sources"][0]["source_type"] = "reputable_news"
        self.assertEqual(run_forecast(high_rank)["confidence"]["score"], run_forecast(low_rank)["confidence"]["score"])

    def test_segment_crossing_cannot_be_hidden_by_other_segment(self) -> None:
        data = forecast_document()
        for segment_index, values in ((0, [120, 130]), (1, [20, 20])):
            ids = data["segments"][segment_index]["scenarios"]["low"]["driver_parameter_ids"]["revenue"]
            for parameter_id, value in zip(ids, values):
                next(item for item in data["parameters"] if item["parameter_id"] == parameter_id)["value"] = value
        with self.assertRaisesRegex(ForecastInputError, "segment scenario ordering"):
            run_forecast(data)

    def test_range_and_discrete_sensitivities_use_explicit_values(self) -> None:
        for shock_type in ("range", "discrete"):
            with self.subTest(shock_type=shock_type):
                data = forecast_document()
                parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
                data["sensitivity_tests"] = [{"name": shock_type, "parameter_id": parameter_id, "shock_type": shock_type, "down_value": 100, "up_value": 140}]
                sensitivity = run_forecast(data)["sensitivities"][0]
                self.assertEqual(sensitivity["effective_values"], {"down": 100.0, "up": 140.0})

    def test_pre_revenue_company_runs_with_zero_base(self) -> None:
        data = forecast_document()
        data["pre_revenue"] = True
        data["historical_revenue"] = []
        for parameter_id in ("reported_total", "segment_a_base", "segment_b_base"):
            update_parameter_value_and_claim(data, parameter_id, 0)
        finalize_contract(data)
        result = run_forecast(data)
        self.assertEqual(result["base_revenue"], 0)
        self.assertIsNone(result["consolidated_forecast"]["base"]["cagr"])


if __name__ == "__main__":
    unittest.main()
