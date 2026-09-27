from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from revenue_report import validate_forecast_output  # noqa: E402
from test_recognition_bridge import add_parameter, forecast_document  # noqa: E402


SCENARIOS = ("low", "base", "high")


def _series(data: dict, prefix: str, values: dict[str, list[float]], dimension: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for scenario in SCENARIOS:
        result[scenario] = [
            add_parameter(data, f"{prefix}_{scenario}_{year}", value, year, scenario, dimension=dimension)
            for year, value in zip(data["forecast_years"], values[scenario])
        ]
    return result


class RevenueConstraintTests(unittest.TestCase):
    def test_sum_cap_is_applied_proportionally_and_is_auditable(self) -> None:
        data = forecast_document()
        cap_ids = _series(
            data,
            "shared_cap",
            {"low": [140, 145], "base": [150, 170], "high": [160, 190]},
            "revenue",
        )
        data["revenue_constraints"] = [{
            "constraint_id": "shared_capacity_cap",
            "type": "sum_cap",
            "segments": ["Segment A", "Segment B"],
            "allocation": "proportional",
            "scenario_parameter_ids": cap_ids,
            "rationale": "Both segments consume the same constrained external capacity.",
        }]
        frozen_input = copy.deepcopy(data)

        result = run_forecast(data)

        self.assertEqual(data, frozen_input)
        self.assertEqual(result["consolidated_forecast"]["base"]["annual_revenue"], {"2026": 150.0, "2027": 170.0})
        self.assertEqual(result["revenue_constraints"], frozen_input["revenue_constraints"])
        self.assertEqual(len(result["constraint_audit"]), 6)
        for segment in result["segments"]:
            self.assertIn("effective_revenue", segment["scenarios"]["base"])
        validate_forecast_output(result)

    def test_linked_ratio_can_cap_a_dependent_segment(self) -> None:
        data = forecast_document()
        ratio_ids = _series(
            data,
            "installed_base_ratio",
            {scenario: [0.4, 0.4] for scenario in SCENARIOS},
            "ratio",
        )
        data["revenue_constraints"] = [{
            "constraint_id": "service_attach_cap",
            "type": "linked_ratio",
            "source_segment": "Segment A",
            "target_segment": "Segment B",
            "relation": "maximum",
            "scenario_parameter_ids": ratio_ids,
            "rationale": "Service revenue cannot exceed the explicit installed-base attach ratio.",
        }]

        result = run_forecast(data)

        effective = result["segments"][1]["scenarios"]["base"]["effective_revenue"]
        self.assertAlmostEqual(effective["2026"], 44.0)
        self.assertAlmostEqual(effective["2027"], 48.4)
        validate_forecast_output(result)

    def test_elimination_is_applied_to_explicit_segments(self) -> None:
        data = forecast_document()
        elimination_ids = _series(
            data,
            "segment_b_elimination",
            {scenario: [-5, -5] for scenario in SCENARIOS},
            "revenue",
        )
        data["revenue_constraints"] = [{
            "constraint_id": "internal_service_elimination",
            "type": "elimination",
            "segment_adjustment_parameter_ids": {"Segment B": elimination_ids},
            "rationale": "Remove explicitly measured internal service revenue before consolidation.",
        }]

        result = run_forecast(data)

        self.assertEqual(result["segments"][1]["scenarios"]["base"]["effective_revenue"]["2026"], 50.00000000000001)
        self.assertAlmostEqual(result["consolidated_forecast"]["base"]["annual_revenue"]["2026"], 160.0)
        validate_forecast_output(result)

    def test_unknown_constraint_segment_is_rejected(self) -> None:
        data = forecast_document()
        cap_ids = _series(
            data,
            "bad_cap",
            {scenario: [100, 100] for scenario in SCENARIOS},
            "revenue",
        )
        data["revenue_constraints"] = [{
            "constraint_id": "bad_segment",
            "type": "sum_cap",
            "segments": ["Segment A", "Missing Segment"],
            "allocation": "proportional",
            "scenario_parameter_ids": cap_ids,
            "rationale": "Negative test.",
        }]
        with self.assertRaisesRegex(ForecastInputError, "unknown constraint segment"):
            run_forecast(data)

    def test_fixed_weights_must_sum_to_one_for_every_scenario_year(self) -> None:
        data = forecast_document()
        cap_ids = _series(data, "weighted_cap", {scenario: [100, 100] for scenario in SCENARIOS}, "revenue")
        weight_a = _series(data, "weight_a", {scenario: [0.7, 0.7] for scenario in SCENARIOS}, "ratio")
        weight_b = _series(data, "weight_b", {scenario: [0.4, 0.4] for scenario in SCENARIOS}, "ratio")
        data["revenue_constraints"] = [{
            "constraint_id": "bad_fixed_weights",
            "type": "sum_cap",
            "segments": ["Segment A", "Segment B"],
            "allocation": "fixed_weights",
            "scenario_parameter_ids": cap_ids,
            "weight_parameter_ids": {"Segment A": weight_a, "Segment B": weight_b},
            "rationale": "Negative test.",
        }]
        with self.assertRaisesRegex(ForecastInputError, "fixed weights must sum to one"):
            run_forecast(data)

    def test_positive_elimination_is_rejected(self) -> None:
        data = forecast_document()
        ids = _series(data, "positive_elimination", {scenario: [1, 1] for scenario in SCENARIOS}, "revenue")
        data["revenue_constraints"] = [{
            "constraint_id": "bad_elimination_sign",
            "type": "elimination",
            "segment_adjustment_parameter_ids": {"Segment B": ids},
            "rationale": "Negative test.",
        }]
        with self.assertRaisesRegex(ForecastInputError, "elimination must be non-positive"):
            run_forecast(data)

    def test_constraint_audit_tampering_is_rejected(self) -> None:
        data = forecast_document()
        ids = _series(data, "tamper_elimination", {scenario: [-1, -1] for scenario in SCENARIOS}, "revenue")
        data["revenue_constraints"] = [{
            "constraint_id": "audited_elimination",
            "type": "elimination",
            "segment_adjustment_parameter_ids": {"Segment B": ids},
            "rationale": "Audit mutation test.",
        }]
        result = run_forecast(data)
        result["constraint_audit"][0]["changes"][0]["adjustment"] = -999
        with self.assertRaisesRegex(ForecastInputError, "constraint audit recomputation mismatch"):
            validate_forecast_output(result)

    def test_constraint_schema_rejects_unknown_fields(self) -> None:
        data = forecast_document()
        cap_ids = _series(data, "strict_cap", {scenario: [100, 100] for scenario in SCENARIOS}, "revenue")
        data["revenue_constraints"] = [{
            "constraint_id": "strict_schema",
            "type": "sum_cap",
            "segments": ["Segment A", "Segment B"],
            "allocation": "proportional",
            "scenario_parameter_ids": cap_ids,
            "rationale": "Negative test.",
            "silent_default": True,
        }]
        with self.assertRaisesRegex(ForecastInputError, "unsupported constraint fields"):
            run_forecast(data)


if __name__ == "__main__":
    unittest.main()
