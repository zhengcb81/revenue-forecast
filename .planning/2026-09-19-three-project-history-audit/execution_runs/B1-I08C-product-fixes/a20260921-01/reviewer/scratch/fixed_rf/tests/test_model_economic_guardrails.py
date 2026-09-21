"""Economic counterexamples for the buy-side model audit.

These test failures that can yield plausible-looking but economically invalid
revenue, rather than duplicating only each calculator's happy-path formula.
"""
from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_registry import (  # noqa: E402
    MODEL_REGISTRY,
    ModelRegistryError,
    calculate_registered_model,
    driver_value_bounds,
)
from test_models import CASES, YEARS  # noqa: E402


class EconomicGuardrailTests(unittest.TestCase):
    def test_public_calculator_preserves_every_existing_case_without_mutation(self) -> None:
        for model, (drivers, expected) in CASES.items():
            with self.subTest(model=model):
                before = copy.deepcopy(drivers)
                actual = calculate_registered_model(model, 100.0, drivers, YEARS)
                self.assertEqual(drivers, before)
                for observed, target in zip(actual, expected):
                    self.assertAlmostEqual(observed, target)

    def test_nonfinite_input_is_rejected_for_every_model(self) -> None:
        for model, (drivers, _) in CASES.items():
            for invalid in (float("nan"), float("inf"), -float("inf")):
                with self.subTest(model=model, invalid=invalid):
                    changed = copy.deepcopy(drivers)
                    changed[MODEL_REGISTRY[model].required[0]][0] = invalid
                    with self.assertRaisesRegex(ModelRegistryError, "finite"):
                        calculate_registered_model(model, 100.0, changed, YEARS)

    def test_boolean_and_text_are_not_numeric_observations(self) -> None:
        for value in (True, False, "120"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ModelRegistryError, "numeric"):
                    calculate_registered_model("direct_revenue", 100, {"revenue": [value, 1]}, YEARS)

    def test_year_gaps_and_duplicates_do_not_silently_skip_compounding(self) -> None:
        for years in ([2026, 2028], [2027, 2026], [2026, 2026]):
            with self.subTest(years=years):
                with self.assertRaisesRegex(ModelRegistryError, "consecutive"):
                    calculate_registered_model("direct_growth", 100, {"growth_rate": [0.1, 0.1]}, years)

    def test_driver_path_length_and_unknown_driver_fail(self) -> None:
        for drivers, message in (({"revenue": [1]}, "one value"), ({"revenue": [1, 2], "typo": [1, 2]}, "unsupported drivers")):
            with self.subTest(drivers=drivers):
                with self.assertRaisesRegex(ModelRegistryError, message):
                    calculate_registered_model("direct_revenue", 100, drivers, YEARS)

    def test_overflow_and_negative_net_revenue_fail_closed(self) -> None:
        for drivers, message in (
            ({"units": [1e308], "unit_revenue": [1e308]}, "finite"),
            ({"units": [1], "unit_revenue": [1], "other_revenue": [-2]}, "negative"),
        ):
            with self.subTest(drivers=drivers):
                with self.assertRaisesRegex(ModelRegistryError, message):
                    calculate_registered_model("unit_sales", 100, drivers, [2026])

    def test_shutdown_can_reach_zero_and_growth_cannot_resurrect_zero_base(self) -> None:
        self.assertEqual(calculate_registered_model("direct_growth", 100, {"growth_rate": [-1, 3]}, YEARS), [0, 0])
        self.assertEqual(calculate_registered_model("direct_growth", 0, {"growth_rate": [3, 3]}, YEARS), [0, 0])
        with self.assertRaises(ModelRegistryError):
            calculate_registered_model("direct_growth", 100, {"growth_rate": [-1.01]}, [2026])

    def test_bank_negative_rates_preserve_sign_without_probability_clamp(self) -> None:
        drivers = {
            "average_earning_assets": [1000], "asset_yield": [-0.005],
            "average_interest_bearing_liabilities": [800], "funding_cost": [-0.01],
            "fee_revenue": [2],
        }
        self.assertEqual(calculate_registered_model("bank_revenue", 0, drivers, [2026]), [5])
        self.assertEqual(driver_value_bounds("bank_revenue", "funding_cost"), (-math.inf, math.inf))
        self.assertEqual(driver_value_bounds("capacity_utilization", "utilization"), (0, 1))

    def test_late_customer_additions_do_not_earn_half_year_automatically(self) -> None:
        drivers = {
            "opening_customers": [100], "new_customers": [100], "churned_customers": [0],
            "ending_customers": [200], "revenue_per_customer": [12],
            "new_customer_revenue_fraction": [1 / 12],
        }
        self.assertAlmostEqual(calculate_registered_model("cohort_subscription", 0, drivers, [2026])[0], 1300)
        drivers["new_customer_revenue_fraction"] = [0]
        self.assertEqual(calculate_registered_model("cohort_subscription", 0, drivers, [2026]), [1200])

    def test_churn_timing_is_revenue_lost_after_exit(self) -> None:
        drivers = {
            "opening_customers": [100], "new_customers": [0], "churned_customers": [20],
            "ending_customers": [80], "revenue_per_customer": [12],
            "churned_customer_lost_fraction": [1],
        }
        self.assertEqual(calculate_registered_model("cohort_subscription", 0, drivers, [2026]), [960])
        drivers["churned_customer_lost_fraction"] = [0]
        self.assertEqual(calculate_registered_model("cohort_subscription", 0, drivers, [2026]), [1200])

    def test_inconsistent_customer_timing_cannot_create_negative_exposure(self) -> None:
        drivers = {
            "opening_customers": [0], "new_customers": [10], "churned_customers": [10],
            "ending_customers": [0], "revenue_per_customer": [1],
            "new_customer_revenue_fraction": [0], "churned_customer_lost_fraction": [1],
        }
        with self.assertRaisesRegex(ModelRegistryError, "time exposure"):
            calculate_registered_model("cohort_subscription", 0, drivers, [2026])

    def test_fx_backlog_remeasurement_is_not_fictitious_revenue(self) -> None:
        drivers = {
            "opening_backlog": [100], "bookings": [0], "cancellations": [0],
            "contract_changes": [0], "closing_backlog": [70], "backlog_remeasurements": [-10],
        }
        self.assertEqual(calculate_registered_model("project_backlog", 0, drivers, [2026]), [20])

    def test_large_backlog_preserves_small_revenue_increment(self) -> None:
        drivers = {
            "opening_backlog": [1e16], "bookings": [1], "cancellations": [0],
            "contract_changes": [0], "closing_backlog": [1e16],
        }
        self.assertEqual(calculate_registered_model("project_backlog", 0, drivers, [2026]), [1])

    def test_reserve_downgrade_is_not_saleable_depletion(self) -> None:
        drivers = {
            "opening_reserves": [100], "additions": [0], "reserve_revisions": [-20],
            "depletion": [10], "closing_reserves": [70], "recovery_rate": [0.8], "realized_price": [5],
        }
        self.assertEqual(calculate_registered_model("reserve_depletion", 0, drivers, [2026]), [40])

    def test_resources_cannot_deplete_beyond_available_stock(self) -> None:
        drivers = {
            "opening_reserves": [10], "additions": [0], "depletion": [11],
            "closing_reserves": [-1], "recovery_rate": [1], "realized_price": [1],
        }
        with self.assertRaisesRegex(ModelRegistryError, "closing_reserves"):
            calculate_registered_model("reserve_depletion", 0, drivers, [2026])

    def test_scenario_customer_capacity_bounds_do_not_admit_above_one(self) -> None:
        drivers = {"capacity": [100], "utilization": [1.01], "yield": [1], "unit_revenue": [1]}
        with self.assertRaisesRegex(ModelRegistryError, "utilization"):
            calculate_registered_model("capacity_utilization", 0, drivers, [2026])


if __name__ == "__main__":
    unittest.main()
