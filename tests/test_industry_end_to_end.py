from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from revenue_core import ForecastInputError, MODEL_DRIVER_DIMENSIONS, MODEL_SPECS, run_forecast  # noqa: E402
from revenue_report import validate_forecast_output  # noqa: E402
from test_data_contract import apply_parameter_contract, finalize_contract, research_coverage  # noqa: E402
from test_models import CASES  # noqa: E402


SCALABLE_DRIVER = {
    "direct_revenue": "revenue",
    "unit_sales": "units",
    "capacity_utilization": "capacity",
    "subscription": "average_customers",
    "usage_platform": "eligible_activity",
    "services": "billable_capacity",
    "project_backlog": "bookings",
    "resource": "saleable_volume",
    "infrastructure": "billable_volume",
    "bank_revenue": "average_earning_assets",
    "asset_management": "average_aum",
    "retail_franchise": "average_owned_stores",
    "transport": "capacity",
    "real_estate_rental": "average_occupied_area",
    "licensing_commercial": "treated_units",
    "advertising": "eligible_impressions",
    "gaming": "active_users",
    "cohort_subscription": "revenue_per_customer",
    "delivery_pipeline": "unit_revenue",
    "milestone_royalty": "royalty_rate",
    "insurance_service": "revenue_per_coverage_unit",
}


def model_document(model: str) -> dict:
    years = [2026, 2027]
    source = {
        "source_id": "filing",
        "source_type": "exchange_filing",
        "title": "Industry test filing",
        "publisher": "Test Exchange",
        "url": "https://www.sec.gov/Archives/edgar/data/1/industry-test.htm",
        "published_date": "2026-03-01",
        "accessed_date": "2026-07-01",
        "page_or_section": "Revenue note",
    }
    parameters = [
        {
            "parameter_id": "reported_total",
            "kind": "reported_fact",
            "value": 100,
            "unit": "USD million",
            "period": "FY2025",
            "definition": "reported total revenue",
            "source_ids": ["filing"],
        },
        {
            "parameter_id": "segment_base",
            "kind": "reported_fact",
            "value": 100,
            "unit": "USD million",
            "period": "FY2025",
            "definition": "segment external revenue",
            "source_ids": ["filing"],
        },
    ]
    for parameter in parameters:
        apply_parameter_contract({"currency": "USD", "unit": "million"}, parameter, "revenue")
    if model == "project_backlog":
        parameter = {"parameter_id": "base_backlog", "kind": "reported_fact", "value": 100, "unit": "USD million", "period": "FY2025", "definition": "base disclosed backlog", "source_ids": ["filing"]}
        apply_parameter_contract({"currency": "USD", "unit": "million"}, parameter, "backlog")
        parameters.append(parameter)
    if model == "delivery_pipeline":
        parameter = {"parameter_id": "base_orders", "kind": "reported_fact", "value": 100, "unit": "orders", "period": "FY2025", "definition": "base opening orders", "source_ids": ["filing"]}
        apply_parameter_contract({"currency": "USD", "unit": "million"}, parameter, "quantity")
        parameters.append(parameter)
    scenario_inputs = {}
    base_drivers = CASES[model][0]
    for scenario, multiplier in (("low", 0.9), ("base", 1.0), ("high", 1.1)):
        drivers = copy.deepcopy(base_drivers)
        if model == "direct_growth":
            drivers["growth_rate"] = {"low": [0.0, 0.0], "base": [0.1, 0.1], "high": [0.2, 0.2]}[scenario]
        else:
            target = SCALABLE_DRIVER[model]
            drivers[target] = [value * multiplier for value in drivers[target]]
        driver_ids = {}
        for driver, values in drivers.items():
            driver_ids[driver] = []
            for year, value in zip(years, values):
                parameter_id = f"{model}_{driver}_{year}_{scenario}"
                parameters.append(
                    parameter := {
                        "parameter_id": parameter_id,
                        "kind": "analyst_assumption",
                        "value": value,
                        "unit": "model-specific",
                        "period": f"FY{year}",
                        "definition": f"{model} {driver} {scenario}",
                        "scenario": scenario,
                        "rationale": "end-to-end industry model test",
                        "source_ids": ["filing"],
                    }
                )
                apply_parameter_contract({"currency": "USD", "unit": "million"}, parameter, MODEL_DRIVER_DIMENSIONS[model][driver])
                driver_ids[driver].append(parameter_id)
        scenario_inputs[scenario] = {
            "model": model,
            "driver_parameter_ids": driver_ids,
            "rationale": f"{scenario} {model} test",
        }
    base_driver_ids = [
        parameter_id
        for ids in scenario_inputs["base"]["driver_parameter_ids"].values()
        for parameter_id in ids
    ]
    segment = {
        "name": "Core segment",
        "base_revenue_parameter_id": "segment_base",
        "recognition": {
            "mode": "modeled_as_recognized",
            "timing": "point_in_time",
            "trigger": "reported recognition event",
            "presentation": "net" if model == "usage_platform" else "gross",
        },
        "scenarios": scenario_inputs,
    }
    if model == "project_backlog":
        segment["base_backlog_parameter_id"] = "base_backlog"
    if model == "delivery_pipeline":
        segment["base_orders_parameter_id"] = "base_orders"
    data = {
        "company_name": f"{model} Test Co",
        "as_of_date": "2026-07-12",
        "currency": "USD",
        "unit": "million",
        "fiscal_year_end": "12-31",
        "base_year": 2025,
        "forecast_years": years,
        "forecast_version": "test-v1",
        "historical_revenue": [
            {"year": 2024, "value": 90, "source_ids": ["filing"]},
            {"year": 2025, "value": 100, "source_ids": ["filing"]},
        ],
        "sources": [source],
        "parameters": parameters,
        "segments": [segment],
        "reported_total_revenue_parameter_id": "reported_total",
        "base_adjustment_parameter_ids": [],
        "forecast_adjustments": [],
        "data_gaps": [],
        "disconfirming_indicators": ["Observed driver falls below the low case"],
        "research_coverage": research_coverage(["reported_total", "segment_base"], base_driver_ids),
    }
    return finalize_contract(data)


class IndustryEndToEndTests(unittest.TestCase):
    def test_all_models_run_end_to_end(self) -> None:
        self.assertEqual(set(MODEL_SPECS), set(CASES))
        for model in MODEL_SPECS:
            with self.subTest(model=model):
                result = run_forecast(model_document(model))
                validate_forecast_output(result)
                self.assertEqual(result["segments"][0]["scenarios"]["base"]["model"], model)

    def test_representative_industry_groups_are_covered(self) -> None:
        groups = {
            "manufacturing": "capacity_utilization",
            "saas": "subscription",
            "platform": "usage_platform",
            "project": "project_backlog",
            "resource": "resource",
            "bank": "bank_revenue",
            "asset_management": "asset_management",
            "retail": "retail_franchise",
            "transport": "transport",
            "real_estate": "real_estate_rental",
            "biopharma": "licensing_commercial",
            "media": "advertising",
            "gaming": "gaming",
            "cohort_subscription": "cohort_subscription",
            "delivery_pipeline": "delivery_pipeline",
            "milestone_royalty": "milestone_royalty",
            "insurance": "insurance_service",
        }
        for industry, model in groups.items():
            with self.subTest(industry=industry):
                self.assertIn(model, MODEL_SPECS)
                validate_forecast_output(run_forecast(model_document(model)))

    def test_cli_generates_json_and_markdown(self) -> None:
        data = model_document("subscription")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            json_path = root / "forecast.json"
            markdown_path = root / "forecast.md"
            input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SKILL_ROOT / "scripts" / "revenue_forecast.py"), str(input_path), "--output", str(json_path), "--markdown", str(markdown_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(json_path.exists())
            self.assertIn("## 核心营收结论", markdown_path.read_text(encoding="utf-8"))

    def test_invalid_fiscal_year_end_is_rejected(self) -> None:
        data = model_document("unit_sales")
        data["fiscal_year_end"] = "13-40"
        with self.assertRaisesRegex(ForecastInputError, "valid month-day"):
            run_forecast(data)

    def test_empty_currency_is_rejected(self) -> None:
        data = model_document("unit_sales")
        data["currency"] = ""
        with self.assertRaisesRegex(ForecastInputError, "currency is required"):
            run_forecast(data)

    def test_driver_period_mismatch_is_rejected(self) -> None:
        data = model_document("unit_sales")
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["units"][0]
        for parameter in data["parameters"]:
            if parameter["parameter_id"] == parameter_id:
                parameter["period"] = "FY2030"
        with self.assertRaisesRegex(ForecastInputError, "period mismatch"):
            run_forecast(data)

    def test_ratio_sensitivity_clamps_without_crashing(self) -> None:
        data = model_document("capacity_utilization")
        for scenario, utilization in (("low", 0.8), ("base", 0.95), ("high", 0.99)):
            for parameter_id in data["segments"][0]["scenarios"][scenario]["driver_parameter_ids"]["utilization"]:
                next(item for item in data["parameters"] if item["parameter_id"] == parameter_id)["value"] = utilization
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["utilization"][-1]
        data["sensitivity_tests"] = [{"name": "Utilization boundary", "parameter_id": parameter_id, "shock_type": "percentage_point", "shock_value": 0.1}]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        self.assertTrue(sensitivity["clamped"]["up"])
        self.assertEqual(sensitivity["effective_values"]["up"], 1.0)

    def test_project_backlog_first_opening_reconciles_to_base(self) -> None:
        data = model_document("project_backlog")
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["opening_backlog"][0]
        next(item for item in data["parameters"] if item["parameter_id"] == parameter_id)["value"] = 99
        with self.assertRaisesRegex(ForecastInputError, "first opening"):
            run_forecast(data)

    def test_driver_dimension_mismatch_is_rejected(self) -> None:
        data = model_document("unit_sales")
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["unit_revenue"][0]
        parameter = next(item for item in data["parameters"] if item["parameter_id"] == parameter_id)
        parameter["dimension"] = "quantity"
        parameter.pop("currency", None)
        parameter.pop("scale", None)
        with self.assertRaisesRegex(ForecastInputError, "dimension mismatch"):
            run_forecast(data)

    def test_retail_franchise_optional_pair_is_enforced(self) -> None:
        data = model_document("retail_franchise")
        ids = []
        for year in data["forecast_years"]:
            parameter = {"parameter_id": f"system_sales_{year}_low", "kind": "analyst_assumption", "value": 100, "unit": "USD million", "period": f"FY{year}", "definition": "franchise system sales", "scenario": "low", "rationale": "test", "source_ids": ["filing"]}
            apply_parameter_contract(data, parameter, "revenue")
            data["parameters"].append(parameter)
            ids.append(parameter["parameter_id"])
        data["segments"][0]["scenarios"]["low"]["driver_parameter_ids"]["franchise_system_sales"] = ids
        finalize_contract(data)
        with self.assertRaisesRegex(ForecastInputError, "requires franchise_system_sales and recognized_fee_rate together"):
            run_forecast(data)

    def test_basis_point_sensitivity_for_rate_driver(self) -> None:
        data = model_document("bank_revenue")
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["asset_yield"][-1]
        data["sensitivity_tests"] = [{"name": "Yield 100bp", "parameter_id": parameter_id, "shock_type": "basis_point", "shock_value": 100}]
        sensitivity = run_forecast(data)["sensitivities"][0]
        self.assertAlmostEqual(sensitivity["requested_values"]["up"] - sensitivity["requested_values"]["down"], 0.02)


if __name__ == "__main__":
    unittest.main()
