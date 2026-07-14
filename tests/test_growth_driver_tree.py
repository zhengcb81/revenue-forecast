from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from test_data_contract import _claim  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


class GrowthDriverTreeTests(unittest.TestCase):
    def test_drivers_are_ranked_by_reconciled_terminal_increment(self) -> None:
        result = run_forecast(forecast_document())
        analysis = result["growth_driver_analysis"]
        self.assertEqual(analysis["status"], "modeled")
        self.assertEqual(analysis["top_drivers"][0]["segment_names"], ["Segment A"])
        self.assertAlmostEqual(analysis["top_drivers"][0]["estimated_base_terminal_increment"], 21.0)
        self.assertAlmostEqual(analysis["reconciliation"]["difference"], 0.0)

    def test_explicit_data_gap_is_reported_without_fabricating_drivers(self) -> None:
        data = forecast_document()
        data["growth_driver_tree"] = {
            "status": "data_gap",
            "drivers": [],
            "rationale": "Independent evidence is not yet sufficient to form a causal tree.",
        }
        result = run_forecast(data)
        analysis = result["growth_driver_analysis"]
        self.assertEqual(analysis["status"], "data_gap")
        self.assertEqual(analysis["top_drivers"], [])
        self.assertTrue(any(item.startswith("growth_driver_tree:") for item in result["data_gaps"]))
        self.assertAlmostEqual(analysis["reconciliation"]["difference"], -31.5)

    def test_one_segment_can_be_split_across_multiple_causal_drivers(self) -> None:
        data = forecast_document()
        original = data["growth_driver_tree"]["drivers"][0]
        original["segment_attribution"][0]["weight"] = 0.7
        second = copy.deepcopy(original)
        second["driver_id"] = "second_generic_cause"
        second["title"] = "Second generic causal mechanism"
        second["segment_attribution"][0]["weight"] = 0.3
        second["evidence_nodes"][0]["evidence_id"] = "second_generic_evidence"
        second["evidence_nodes"][0]["claim_ids"] = ["claim_second_generic_evidence"]
        data["evidence_claims"].append(_claim(
            "claim_second_generic_evidence", "filing", "growth_driver", "second_generic_evidence",
            "rationale_support", "A second checked source claim supports this generic causal mechanism.",
            data["as_of_date"],
        ))
        data["growth_driver_tree"]["drivers"].insert(1, second)
        result = run_forecast(data)
        impacts = {
            driver["driver_id"]: driver["estimated_base_terminal_increment"]
            for driver in result["growth_driver_analysis"]["drivers"]
        }
        self.assertAlmostEqual(impacts[original["driver_id"]], 14.7)
        self.assertAlmostEqual(impacts[second["driver_id"]], 6.3)

    def test_attribution_weights_must_reconcile_for_every_segment(self) -> None:
        data = forecast_document()
        data["growth_driver_tree"]["drivers"][0]["segment_attribution"][0]["weight"] = 0.8
        with self.assertRaisesRegex(ForecastInputError, "weights must sum to 1"):
            run_forecast(data)

    def test_driver_must_map_to_a_parameter_used_by_the_base_case(self) -> None:
        data = forecast_document()
        high_ids = data["segments"][0]["scenarios"]["high"]["driver_parameter_ids"]["revenue"]
        data["growth_driver_tree"]["drivers"][0]["parameter_ids"] = high_ids
        with self.assertRaisesRegex(ForecastInputError, "not used by the base forecast"):
            run_forecast(data)

    def test_driver_parameter_must_affect_its_attributed_segment(self) -> None:
        data = forecast_document()
        segment_b_base_ids = data["segments"][1]["scenarios"]["base"]["driver_parameter_ids"]["revenue"]
        data["growth_driver_tree"]["drivers"][0]["parameter_ids"] = segment_b_base_ids
        with self.assertRaisesRegex(ForecastInputError, "does not affect an attributed segment"):
            run_forecast(data)

    def test_found_counterevidence_requires_a_contrary_evidence_node(self) -> None:
        data = forecast_document()
        driver = data["growth_driver_tree"]["drivers"][0]
        driver["counterevidence_status"] = "found"
        driver["counterevidence_rationale"] = "Contrary evidence was found during the search."
        with self.assertRaisesRegex(ForecastInputError, "requires a contrary evidence node"):
            run_forecast(data)

    def test_two_evidence_types_and_sources_are_marked_triangulated(self) -> None:
        data = forecast_document()
        data["sources"].append({
            "source_id": "industry_source",
            "source_type": "industry_association",
            "title": "Independent operating indicator",
            "publisher": "Industry Association",
            "url": "https://www.semiconductors.org/independent-operating-indicator",
            "published_date": "2026-06-01",
            "accessed_date": data["as_of_date"],
            "page_or_section": "Operating indicator",
        })
        driver = data["growth_driver_tree"]["drivers"][0]
        driver["evidence_nodes"].append({
            "evidence_id": "independent_demand_signal",
            "evidence_type": "independent_demand_signal",
            "inference_distance": "one_step",
            "conclusion": "An independent checked indicator supports the direction of the modeled demand path.",
            "claim_ids": ["claim_independent_demand_signal"],
        })
        data["evidence_claims"].append(_claim(
            "claim_independent_demand_signal", "industry_source", "growth_driver",
            "independent_demand_signal", "rationale_support",
            "Independent operating data supports the direction of the modeled demand path.",
            data["as_of_date"],
        ))
        result = run_forecast(data)
        first = next(item for item in result["growth_driver_analysis"]["drivers"] if item["driver_id"] == driver["driver_id"])
        self.assertEqual(first["evidence_status"], "triangulated")


if __name__ == "__main__":
    unittest.main()
