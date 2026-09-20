"""Economic invariants and limiting cases for the added archetypes."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_extensions import EXTENSION_OPENING_BALANCES, build_extension_specs  # noqa: E402
from model_registry import ModelRegistryError, ModelSpec, build_registry  # noqa: E402


YEARS = [2026, 2027]
EXTENSION_CASES = {
    "subscription_arr_bridge": ({
        "opening_arr": [100, 125], "gross_retention_rate": [0.9, 0.9],
        "expansion_arr": [15, 20], "new_arr": [20, 30], "closing_arr": [125, 162.5],
        "lost_arr_revenue_fraction": [0.75, 0.5], "expansion_revenue_fraction": [0.5, 0.5],
        "new_arr_revenue_fraction": [0.25, 0.25],
    }, [105, 136.25]),
    "installed_base_aftermarket": ({
        "opening_installed_units": [100, 110], "new_installed_units": [20, 25],
        "retired_units": [10, 15], "closing_installed_units": [110, 120],
        "new_unit_revenue_fraction": [0.25, 0.5], "retirement_lost_fraction": [0.75, 0.5],
        "attach_rate": [0.8, 0.8], "annual_revenue_per_attached_unit": [2, 2],
    }, [156, 184]),
    "store_cohorts": ({
        "opening_stores": [10, 12], "new_stores": [3, 4], "closed_stores": [1, 2],
        "closing_stores": [12, 14], "new_store_revenue_fraction": [0.5, 0.5],
        "closure_lost_fraction": [0.5, 0.5], "new_store_productivity": [0.8, 0.8],
        "annual_revenue_per_mature_store": [5, 5],
    }, [53.5, 63]),
    "renewable_generation": ({
        "average_commissioned_mw": [10, 12], "period_hours": [8760, 8760],
        "pre_curtailment_capacity_factor": [0.25, 0.25], "curtailment_rate": [0.1, 0.1],
        "contracted_share": [0.6, 0.6], "contract_price_per_mwh": [0.05, 0.05],
        "merchant_price_per_mwh": [0.04, 0.04],
    }, [906.66, 1087.992]),
    "aum_fee_bridge": ({
        "opening_aum": [1000, 1050], "inflows": [100, 120], "outflows": [50, 70],
        "market_change": [0, -100], "closing_aum": [1050, 1000],
        "inflow_revenue_fraction": [0.5, 0.5], "outflow_lost_fraction": [0.5, 0.5],
        "market_change_revenue_fraction": [0.5, 0.5], "management_fee_rate": [0.01, 0.01],
    }, [10.25, 10.25]),
    "commercial_launch": ({
        "eligible_units": [1000, 1200], "adoption_rate": [0.1, 0.2],
        "annual_supply_capacity": [80, 300], "commercial_year_fraction": [0.5, 1],
        "net_revenue_per_unit": [2, 2],
    }, [80, 480]),
    "finite_adoption": ({
        "opening_unserved_market": [100, 85], "new_eligible_units": [10, 10],
        "removed_eligible_units": [5, 5], "adopted_units": [20, 30],
        "closing_unserved_market": [85, 60], "net_revenue_per_unit": [2, 2],
    }, [40, 60]),
    "inventory_sellthrough": ({
        "opening_inventory": [100, 95], "saleable_production": [50, 60],
        "purchased_units": [10, 10], "scrapped_units": [5, 5], "sold_units": [60, 70],
        "closing_inventory": [95, 90], "net_revenue_per_unit": [2, 2],
    }, [120, 140]),
}

# Scale only a free price/fee or recognition weight so scenario fixtures keep
# stock-flow bridges valid. All chosen baseline fractions remain below 1 at 1.1x.
EXTENSION_SCALABLE_DRIVER = {
    "subscription_arr_bridge": "new_arr_revenue_fraction",
    "installed_base_aftermarket": "annual_revenue_per_attached_unit",
    "store_cohorts": "annual_revenue_per_mature_store",
    "renewable_generation": "contract_price_per_mwh",
    "aum_fee_bridge": "management_fee_rate",
    "commercial_launch": "net_revenue_per_unit",
    "finite_adoption": "net_revenue_per_unit",
    "inventory_sellthrough": "net_revenue_per_unit",
}


class ExtensionModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_registry(build_extension_specs(ModelSpec, ModelRegistryError))

    def run_model(self, model: str, drivers: dict | None = None, years: list[int] | None = None) -> list[float]:
        inputs = copy.deepcopy(EXTENSION_CASES[model][0] if drivers is None else drivers)
        return self.registry[model].calculator(0, inputs, YEARS if years is None else years)

    def one_year(self, model: str) -> dict:
        return {name: values[:1] for name, values in EXTENSION_CASES[model][0].items()}

    def test_all_extension_formulas_and_no_input_mutation(self) -> None:
        self.assertEqual(set(self.registry), set(EXTENSION_CASES))
        self.assertEqual(set(self.registry), set(EXTENSION_SCALABLE_DRIVER))
        for model, (drivers, expected) in EXTENSION_CASES.items():
            with self.subTest(model=model):
                original = copy.deepcopy(drivers)
                observed = self.registry[model].calculator(0, drivers, YEARS)
                self.assertEqual(drivers, original)
                for actual, target in zip(observed, expected):
                    self.assertAlmostEqual(actual, target)

    def test_stock_flow_corruption_is_rejected_for_each_bridge(self) -> None:
        closings = {
            "subscription_arr_bridge": "closing_arr", "installed_base_aftermarket": "closing_installed_units",
            "store_cohorts": "closing_stores", "aum_fee_bridge": "closing_aum",
            "finite_adoption": "closing_unserved_market", "inventory_sellthrough": "closing_inventory",
        }
        self.assertEqual(set(closings), set(EXTENSION_OPENING_BALANCES))
        for model, closing in closings.items():
            with self.subTest(model=model):
                drivers = self.one_year(model)
                drivers[closing][0] += 1
                with self.assertRaisesRegex(ModelRegistryError, "stock-flow balance"):
                    self.run_model(model, drivers, [2026])

    def test_balanced_but_discontinuous_arr_is_rejected(self) -> None:
        drivers = copy.deepcopy(EXTENSION_CASES["subscription_arr_bridge"][0])
        drivers["opening_arr"][1] += 10
        drivers["closing_arr"][1] += 9
        with self.assertRaisesRegex(ModelRegistryError, "continuity"):
            self.run_model("subscription_arr_bridge", drivers)

    def test_arr_new_contract_at_year_end_is_not_full_year_revenue(self) -> None:
        drivers = self.one_year("subscription_arr_bridge")
        drivers.update(opening_arr=[0], expansion_arr=[0], new_arr=[100], closing_arr=[100], new_arr_revenue_fraction=[0])
        self.assertEqual(self.run_model("subscription_arr_bridge", drivers, [2026]), [0])
        drivers["new_arr_revenue_fraction"] = [1]
        self.assertEqual(self.run_model("subscription_arr_bridge", drivers, [2026]), [100])

    def test_arr_churn_loss_timing_limits(self) -> None:
        drivers = self.one_year("subscription_arr_bridge")
        drivers.update(gross_retention_rate=[0], expansion_arr=[0], new_arr=[0], closing_arr=[0])
        drivers["lost_arr_revenue_fraction"] = [0]
        self.assertEqual(self.run_model("subscription_arr_bridge", drivers, [2026]), [100])
        drivers["lost_arr_revenue_fraction"] = [1]
        self.assertEqual(self.run_model("subscription_arr_bridge", drivers, [2026]), [0])

    def test_arr_rejects_expansion_without_retained_opening_cohort(self) -> None:
        drivers = self.one_year("subscription_arr_bridge")
        drivers.update(opening_arr=[0], expansion_arr=[10], new_arr=[20], closing_arr=[30])
        with self.assertRaisesRegex(ModelRegistryError, "retained opening ARR"):
            self.run_model("subscription_arr_bridge", drivers, [2026])

    def test_arr_rejects_nrr_as_additional_multiplier(self) -> None:
        drivers = self.one_year("subscription_arr_bridge")
        drivers["net_retention_rate"] = [1.1]
        with self.assertRaisesRegex(ModelRegistryError, "unknown"):
            self.run_model("subscription_arr_bridge", drivers, [2026])

    def test_installed_base_retirements_cannot_consume_new_cohort(self) -> None:
        drivers = self.one_year("installed_base_aftermarket")
        drivers.update(retired_units=[110], closing_installed_units=[10])
        with self.assertRaisesRegex(ModelRegistryError, "opening installed cohort"):
            self.run_model("installed_base_aftermarket", drivers, [2026])

    def test_zero_attach_rate_eliminates_aftermarket_revenue(self) -> None:
        drivers = self.one_year("installed_base_aftermarket")
        drivers["attach_rate"] = [0]
        self.assertEqual(self.run_model("installed_base_aftermarket", drivers, [2026]), [0])

    def test_store_productivity_can_exceed_mature_average(self) -> None:
        drivers = self.one_year("store_cohorts")
        drivers["new_store_productivity"] = [1.2]
        self.assertAlmostEqual(self.run_model("store_cohorts", drivers, [2026])[0], 56.5)

    def test_store_year_end_openings_generate_no_current_revenue(self) -> None:
        drivers = self.one_year("store_cohorts")
        drivers.update(opening_stores=[0], closed_stores=[0], closing_stores=[3], new_store_revenue_fraction=[0])
        self.assertEqual(self.run_model("store_cohorts", drivers, [2026]), [0])

    def test_full_curtailment_removes_energy_revenue(self) -> None:
        drivers = self.one_year("renewable_generation")
        drivers["curtailment_rate"] = [1]
        self.assertEqual(self.run_model("renewable_generation", drivers, [2026]), [0])

    def test_ppa_share_partitions_not_duplicates_generation(self) -> None:
        drivers = self.one_year("renewable_generation")
        drivers["merchant_price_per_mwh"] = drivers["contract_price_per_mwh"].copy()
        observations = []
        for share in [0, 0.5, 1]:
            drivers["contracted_share"] = [share]
            observations.append(self.run_model("renewable_generation", drivers, [2026])[0])
        self.assertEqual(observations, [985.5] * 3)

    def test_negative_merchant_price_allowed_when_total_revenue_nonnegative(self) -> None:
        drivers = self.one_year("renewable_generation")
        drivers["merchant_price_per_mwh"] = [-0.01]
        self.assertAlmostEqual(self.run_model("renewable_generation", drivers, [2026])[0], 512.46)
        drivers["contracted_share"] = [0]
        with self.assertRaisesRegex(ModelRegistryError, "finite and non-negative"):
            self.run_model("renewable_generation", drivers, [2026])

    def test_generation_scales_with_explicit_calendar_hours(self) -> None:
        drivers = self.one_year("renewable_generation")
        original = self.run_model("renewable_generation", drivers, [2026])[0]
        drivers["period_hours"] = [8784]
        self.assertAlmostEqual(self.run_model("renewable_generation", drivers, [2026])[0] / original, 8784 / 8760)
        drivers["period_hours"] = [0]
        with self.assertRaisesRegex(ModelRegistryError, "positive"):
            self.run_model("renewable_generation", drivers, [2026])

    def test_aum_flow_timing_limits(self) -> None:
        drivers = self.one_year("aum_fee_bridge")
        drivers.update(inflows=[100], outflows=[0], closing_aum=[1100], inflow_revenue_fraction=[0])
        self.assertEqual(self.run_model("aum_fee_bridge", drivers, [2026]), [10])
        drivers["inflow_revenue_fraction"] = [1]
        self.assertEqual(self.run_model("aum_fee_bridge", drivers, [2026]), [11])

    def test_aum_market_losses_reduce_fee_base(self) -> None:
        drivers = self.one_year("aum_fee_bridge")
        drivers.update(inflows=[0], outflows=[0], market_change=[-200], closing_aum=[800])
        self.assertEqual(self.run_model("aum_fee_bridge", drivers, [2026]), [9])

    def test_recognized_fee_and_other_revenue_reversals_are_signed(self) -> None:
        for model, name in (("aum_fee_bridge", "recognized_performance_fees"),
                            ("renewable_generation", "other_revenue")):
            with self.subTest(model=model):
                drivers = self.one_year(model)
                before = self.run_model(model, drivers, [2026])[0]
                drivers[name] = [-1]
                self.assertAlmostEqual(self.run_model(model, drivers, [2026])[0], before - 1)
                drivers[name] = [-before - 1]
                with self.assertRaisesRegex(ModelRegistryError, "finite and non-negative"):
                    self.run_model(model, drivers, [2026])

    def test_nonnegative_closing_aum_does_not_mask_invalid_average(self) -> None:
        drivers = self.one_year("aum_fee_bridge")
        drivers.update(inflows=[2000], outflows=[2500], closing_aum=[500],
                       inflow_revenue_fraction=[0], outflow_lost_fraction=[1])
        with self.assertRaisesRegex(ModelRegistryError, "time-weighted AUM"):
            self.run_model("aum_fee_bridge", drivers, [2026])

    def test_launch_is_supply_capped_and_zero_before_commercial_start(self) -> None:
        drivers = self.one_year("commercial_launch")
        drivers["adoption_rate"] = [1]
        self.assertEqual(self.run_model("commercial_launch", drivers, [2026]), [80])
        drivers["commercial_year_fraction"] = [0]
        self.assertEqual(self.run_model("commercial_launch", drivers, [2026]), [0])

    def test_launch_rejects_second_probability_discount(self) -> None:
        drivers = self.one_year("commercial_launch")
        drivers["success_probability"] = [0.5]
        with self.assertRaisesRegex(ModelRegistryError, "unknown"):
            self.run_model("commercial_launch", drivers, [2026])

    def test_finite_adoption_cannot_sell_more_than_remaining_market(self) -> None:
        drivers = self.one_year("finite_adoption")
        drivers.update(adopted_units=[106], closing_unserved_market=[0])
        with self.assertRaisesRegex(ModelRegistryError, "stock-flow balance"):
            self.run_model("finite_adoption", drivers, [2026])

    def test_fully_penetrated_market_without_additions_has_zero_sales(self) -> None:
        drivers = self.one_year("finite_adoption")
        for name in drivers:
            if name != "net_revenue_per_unit":
                drivers[name] = [0]
        self.assertEqual(self.run_model("finite_adoption", drivers, [2026]), [0])

    def test_production_is_not_revenue_without_sellthrough(self) -> None:
        drivers = self.one_year("inventory_sellthrough")
        drivers.update(sold_units=[0], closing_inventory=[155])
        self.assertEqual(self.run_model("inventory_sellthrough", drivers, [2026]), [0])

    def test_inventory_cannot_sell_scrapped_or_unproduced_units(self) -> None:
        drivers = self.one_year("inventory_sellthrough")
        drivers.update(sold_units=[156], closing_inventory=[0])
        with self.assertRaisesRegex(ModelRegistryError, "stock-flow balance"):
            self.run_model("inventory_sellthrough", drivers, [2026])

    def test_pure_calculators_reject_nonfinite_negative_and_wrong_length(self) -> None:
        for value in [-1, float("inf"), float("nan"), True]:
            drivers = self.one_year("commercial_launch")
            drivers["eligible_units"] = [value]
            with self.subTest(value=value), self.assertRaises(ModelRegistryError):
                self.run_model("commercial_launch", drivers, [2026])
        drivers = self.one_year("commercial_launch")
        drivers["eligible_units"] = [1, 2]
        with self.assertRaisesRegex(ModelRegistryError, "path length"):
            self.run_model("commercial_launch", drivers, [2026])


if __name__ == "__main__":
    unittest.main()
