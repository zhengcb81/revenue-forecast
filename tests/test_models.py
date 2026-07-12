from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, MODEL_DRIVER_DIMENSIONS, MODEL_SPECS, calculate_model_path  # noqa: E402


YEARS = [2026, 2027]


def make_parameters(model: str, driver_values: dict[str, list[float]], scenario: str = "base") -> tuple[dict, dict]:
    parameters = {}
    ids = {}
    for driver, values in driver_values.items():
        ids[driver] = []
        for year, value in zip(YEARS, values):
            parameter_id = f"{driver}_{year}_{scenario}"
            parameters[parameter_id] = {
                "parameter_id": parameter_id,
                "kind": "analyst_assumption",
                "value": float(value),
                "unit": "test",
                "period": f"FY{year}",
                "definition": f"{driver} {scenario}",
                "scenario": scenario,
                "rationale": "unit test",
                "source_ids": [],
                "claim_ids": [],
                "dimension": MODEL_DRIVER_DIMENSIONS[model][driver],
                "time_basis": "annual",
            }
            ids[driver].append(parameter_id)
    return parameters, ids


CASES = {
    "direct_growth": ({"growth_rate": [0.1, 0.1]}, [110.0, 121.0]),
    "direct_revenue": ({"revenue": [90, 95]}, [90, 95]),
    "unit_sales": ({"units": [10, 12], "unit_revenue": [5, 5]}, [50, 60]),
    "capacity_utilization": ({"capacity": [100, 120], "utilization": [0.8, 0.75], "yield": [0.9, 0.9], "unit_revenue": [2, 2]}, [144, 162]),
    "subscription": ({"average_customers": [100, 110], "revenue_per_customer": [2, 2]}, [200, 220]),
    "usage_platform": ({"eligible_activity": [1000, 1200], "monetization_rate": [0.02, 0.02]}, [20, 24]),
    "services": ({"billable_capacity": [100, 120], "utilization": [0.8, 0.75], "billing_rate": [2, 2]}, [160, 180]),
    "project_backlog": ({"opening_backlog": [100, 120], "bookings": [80, 90], "cancellations": [5, 5], "contract_changes": [0, 0], "closing_backlog": [120, 130]}, [55, 75]),
    "resource": ({"saleable_volume": [10, 11], "realized_price": [5, 5]}, [50, 55]),
    "infrastructure": ({"billable_volume": [100, 105], "tariff": [2, 2]}, [200, 210]),
    "bank_revenue": ({"average_earning_assets": [1000, 1100], "asset_yield": [0.05, 0.05], "average_interest_bearing_liabilities": [800, 850], "funding_cost": [0.02, 0.02], "fee_revenue": [10, 11]}, [44, 49]),
    "asset_management": ({"average_aum": [1000, 1100], "management_fee_rate": [0.01, 0.01]}, [10, 11]),
    "retail_franchise": ({"average_owned_stores": [10, 12], "revenue_per_owned_store": [5, 5]}, [50, 60]),
    "transport": ({"capacity": [100, 120], "utilization": [0.8, 0.75], "yield": [2, 2]}, [160, 180]),
    "real_estate_rental": ({"average_occupied_area": [100, 110], "rent_per_area": [2, 2]}, [200, 220]),
    "licensing_commercial": ({"treated_units": [10, 12], "net_revenue_per_unit": [5, 5]}, [50, 60]),
    "advertising": ({"eligible_impressions": [100000, 120000], "fill_rate": [0.8, 0.75], "revenue_per_thousand_impressions": [2, 2]}, [160, 180]),
    "gaming": ({"active_users": [1000, 1200], "payer_conversion": [0.1, 0.1], "revenue_per_payer": [2, 2]}, [200, 240]),
    "cohort_subscription": ({"opening_customers": [100, 110], "new_customers": [20, 20], "churned_customers": [10, 15], "ending_customers": [110, 115], "revenue_per_customer": [2, 2]}, [210, 225]),
    "delivery_pipeline": ({"opening_orders": [100, 120], "new_orders": [50, 60], "cancellations": [5, 5], "deliveries": [25, 35], "ending_orders": [120, 140], "unit_revenue": [2, 2]}, [50, 70]),
    "milestone_royalty": ({"eligible_sales": [100, 120], "royalty_rate": [0.1, 0.1]}, [10, 12]),
    "insurance_service": ({"coverage_units": [100, 110], "revenue_per_coverage_unit": [2, 2]}, [200, 220]),
}


class ModelTests(unittest.TestCase):
    def test_every_registered_model_has_a_case(self) -> None:
        self.assertEqual(set(MODEL_SPECS), set(CASES))

    def test_model_formulas(self) -> None:
        for model, (drivers, expected) in CASES.items():
            with self.subTest(model=model):
                parameters, ids = make_parameters(model, drivers)
                result = calculate_model_path(model, 100, ids, parameters, YEARS, "base")
                actual = list(result["annual_revenue"].values())
                self.assertEqual(len(actual), len(expected))
                for observed, target in zip(actual, expected):
                    self.assertAlmostEqual(observed, target)

    def test_rejects_ratio_above_one(self) -> None:
        parameters, ids = make_parameters("capacity_utilization", {"capacity": [100, 100], "utilization": [1.1, 1], "yield": [1, 1], "unit_revenue": [1, 1]})
        with self.assertRaisesRegex(ForecastInputError, "between 0 and 1"):
            calculate_model_path("capacity_utilization", 100, ids, parameters, YEARS, "base")

    def test_rejects_scenario_mismatch(self) -> None:
        parameters, ids = make_parameters("direct_growth", {"growth_rate": [0.1, 0.1]}, scenario="high")
        with self.assertRaisesRegex(ForecastInputError, "scenario mismatch"):
            calculate_model_path("direct_growth", 100, ids, parameters, YEARS, "base")

    def test_rejects_project_backlog_discontinuity(self) -> None:
        drivers = {"opening_backlog": [100, 119], "bookings": [80, 90], "cancellations": [5, 5], "contract_changes": [0, 0], "closing_backlog": [120, 130]}
        parameters, ids = make_parameters("project_backlog", drivers)
        with self.assertRaisesRegex(ForecastInputError, "continuity"):
            calculate_model_path("project_backlog", 100, ids, parameters, YEARS, "base")

    def test_timing_factor_models_partial_year_commissioning(self) -> None:
        parameters, ids = make_parameters("unit_sales", {"units": [10, 10], "unit_revenue": [5, 5], "timing_factor": [0.5, 1.0]})
        result = calculate_model_path("unit_sales", 0, ids, parameters, YEARS, "base")
        self.assertEqual(list(result["annual_revenue"].values()), [25, 50])


if __name__ == "__main__":
    unittest.main()
