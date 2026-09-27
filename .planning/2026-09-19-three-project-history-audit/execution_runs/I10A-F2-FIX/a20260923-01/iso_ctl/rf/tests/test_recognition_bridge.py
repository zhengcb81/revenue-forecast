from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from test_data_contract import apply_parameter_contract, finalize_contract, valid_document  # noqa: E402


def add_parameter(data: dict, parameter_id: str, value: float, year: int, scenario: str, definition: str | None = None, dimension: str = "revenue") -> str:
    parameter = {
            "parameter_id": parameter_id,
            "kind": "analyst_assumption",
            "value": value,
            "unit": "USD million",
            "period": f"FY{year}",
            "definition": definition or parameter_id,
            "scenario": scenario,
            "rationale": "bridge test",
            "source_ids": ["filing"],
        }
    apply_parameter_contract(data, parameter, dimension)
    data["parameters"].append(parameter)
    finalize_contract(data)
    return parameter_id


def forecast_document() -> dict:
    data = valid_document()
    for segment_index, segment in enumerate(data["segments"]):
        segment["recognition"] = {
            "mode": "modeled_as_recognized",
            "timing": "point_in_time",
            "trigger": "customer acceptance",
            "presentation": "gross",
        }
        segment["scenarios"] = {}
        base = 100 if segment_index == 0 else 50
        for scenario, multiplier in (("low", 1.0), ("base", 1.1), ("high", 1.2)):
            ids = [
                add_parameter(data, f"{segment_index}_{scenario}_{year}", base * multiplier ** (year - 2025), year, scenario)
                for year in data["forecast_years"]
            ]
            segment["scenarios"][scenario] = {
                "model": "direct_revenue",
                "driver_parameter_ids": {"revenue": ids},
                "rationale": f"{scenario} direct revenue test",
            }
    data["forecast_adjustments"] = []
    base_driver_ids = [
        parameter_id
        for segment in data["segments"]
        for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
        for parameter_id in ids
    ]
    growth_record = next(item for item in data["research_coverage"] if item["dimension"] == "growth_curve")
    growth_record.update({
        "status": "modeled_driver",
        "conclusion": "Direct scenario revenue paths generate the synthetic forecast",
        "revenue_mechanism": "registered scenario revenue parameters aggregate by segment",
        "parameter_ids": base_driver_ids,
        "source_ids": ["filing"],
    })
    growth_record.pop("rationale", None)
    return finalize_contract(data)


class RecognitionBridgeTests(unittest.TestCase):
    def test_company_aggregates_recognized_segments(self) -> None:
        result = run_forecast(forecast_document())
        base = result["consolidated_forecast"]["base"]
        self.assertAlmostEqual(base["annual_revenue"]["2026"], 165)
        self.assertAlmostEqual(base["annual_revenue"]["2027"], 181.5)
        self.assertAlmostEqual(base["cagr"], 0.1)

    def test_lagged_recognition_preserves_tail(self) -> None:
        data = forecast_document()
        segment = data["segments"][0]
        carry = {}
        for scenario, value in (("low", 90), ("base", 95), ("high", 100)):
            carry[scenario] = [add_parameter(data, f"carry_{scenario}", value, 2026, scenario)]
        segment["recognition"] = {
            "mode": "lagged_activity",
            "timing": "point_in_time",
            "trigger": "customer acceptance after installation",
            "presentation": "gross",
            "lag_years": 1,
            "carry_in_parameter_ids": carry,
        }
        finalize_contract(data)
        result = run_forecast(data)
        segment_result = result["segments"][0]["scenarios"]["base"]
        self.assertEqual(segment_result["recognized_revenue"], {"2026": 95.0, "2027": 110.00000000000001})
        self.assertEqual(segment_result["unrecognized_tail_activity"], [121.00000000000001])

    def test_over_time_requires_progress_measure(self) -> None:
        data = forecast_document()
        data["segments"][0]["recognition"]["timing"] = "over_time"
        with self.assertRaisesRegex(ForecastInputError, "progress_measure"):
            run_forecast(data)

    def test_over_time_progress_changes_recognized_revenue(self) -> None:
        data = forecast_document()
        segment = data["segments"][0]
        progress = {}
        for scenario in ("low", "base", "high"):
            progress[scenario] = [add_parameter(data, f"progress_{scenario}_{year}", 0.5, year, scenario, dimension="ratio") for year in data["forecast_years"]]
        segment["recognition"].update({
            "timing": "over_time",
            "progress_measure": "verified output progress",
            "progress_parameter_ids": progress,
        })
        finalize_contract(data)
        result = run_forecast(data)
        modeled = result["segments"][0]["scenarios"]["base"]["modeled_activity"]["2026"]
        recognized = result["segments"][0]["scenarios"]["base"]["recognized_revenue"]["2026"]
        self.assertAlmostEqual(recognized, modeled * 0.5)

    def test_signed_adjustment_bridge(self) -> None:
        data = forecast_document()
        adjustment = {
            "name": "Intersegment elimination",
            "category": "intersegment_elimination",
            "scenario_parameter_ids": {},
        }
        for scenario in ("low", "base", "high"):
            adjustment["scenario_parameter_ids"][scenario] = [
                add_parameter(data, f"elim_{scenario}_{year}", -5, year, scenario)
                for year in data["forecast_years"]
            ]
        data["forecast_adjustments"] = [adjustment]
        result = run_forecast(data)
        self.assertAlmostEqual(result["consolidated_forecast"]["base"]["annual_revenue"]["2026"], 160)

    def test_positive_elimination_is_rejected(self) -> None:
        data = forecast_document()
        ids = {}
        for scenario in ("low", "base", "high"):
            ids[scenario] = [add_parameter(data, f"bad_elim_{scenario}_{year}", 1, year, scenario) for year in data["forecast_years"]]
        data["forecast_adjustments"] = [{"name": "Bad elimination", "category": "intersegment_elimination", "scenario_parameter_ids": ids}]
        with self.assertRaisesRegex(ForecastInputError, "non-positive"):
            run_forecast(data)

    def test_unmodeled_tam_driver_is_rejected(self) -> None:
        data = forecast_document()
        segment = data["segments"][0]
        tam_ids = [add_parameter(data, f"tam_base_{year}", 1000, year, "base") for year in data["forecast_years"]]
        segment["scenarios"]["base"]["driver_parameter_ids"]["tam"] = tam_ids
        with self.assertRaisesRegex(ForecastInputError, "unsupported drivers"):
            run_forecast(data)


if __name__ == "__main__":
    unittest.main()
