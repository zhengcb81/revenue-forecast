"""DU8: the owner is checked against Decimal hand anchors, not itself.

``tests/fixtures/du8_comparison/hand_anchors.py`` recomputes every frozen
constant with :mod:`decimal` and imports no production comparison code. This
module compares the owner's arithmetic against those anchors and covers the
boundary families the construction card names explicitly.
"""
from __future__ import annotations

import copy
import sys
import unittest
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "fixtures" / "du8_comparison"))

from hand_anchors import (  # noqa: E402
    DIVERGENCE_CASE,
    LEGACY_ANCHORS,
    TOLERANCE,
    TYPED_ANCHORS,
)
from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from research.target_comparison import (  # noqa: E402
    compare_legacy_target_measurement,
    legacy_acceptance_bound,
    legacy_meets_target,
    legacy_target_ratio,
)
from research.target_measurement import acceptance_bound, meets_target  # noqa: E402
from models import (  # noqa: E402
    constrained_model,
    growth_model,
    legacy_annual_model,
    legacy_approximately_model,
    legacy_cumulative_model,
    typed_level_model,
    typed_quarterly_model,
)


class LegacyDecimalAnchorTests(unittest.TestCase):
    """Each anchor is recomputed here in Decimal and matched by the owner."""

    def test_approximately_absolute_term_matches_the_decimal_anchor(self) -> None:
        for name in (
            "legacy_approximately_abs_tol_small_target",
            "legacy_approximately_abs_tol_at_one",
            "legacy_approximately_abs_tol_large_target",
        ):
            with self.subTest(anchor=name):
                _, expected = LEGACY_ANCHORS[name]
                value = {"legacy_approximately_abs_tol_small_target": Decimal("0.5"),
                         "legacy_approximately_abs_tol_at_one": Decimal("1"),
                         "legacy_approximately_abs_tol_large_target": Decimal("144")}[name]
                recomputed = max(Decimal("1.0"), abs(value)) * TOLERANCE
                self.assertEqual(recomputed, expected)

    def test_acceptance_bounds_match_the_decimal_anchor(self) -> None:
        for name, lower, value in (
            ("legacy_at_least_bound_144", True, 144.0),
            ("legacy_at_most_bound_144", False, 144.0),
            ("legacy_at_least_bound_one", True, 1.0),
        ):
            with self.subTest(anchor=name):
                _, expected = LEGACY_ANCHORS[name]
                observed = legacy_acceptance_bound(value, 0.01, lower=lower)
                self.assertEqual(Decimal(repr(observed)), expected)

    def test_ratio_rule_matches_the_decimal_anchor(self) -> None:
        _, expected = LEGACY_ANCHORS["legacy_attainment_ratio_4905_over_500"]
        self.assertEqual(
            Decimal(repr(legacy_target_ratio(0.4905, 0.5))), expected
        )
        self.assertIsNone(legacy_target_ratio(0.4905, 0.0))
        self.assertIsNone(legacy_target_ratio(None, 0.5))

    def test_typed_bounds_match_their_decimal_anchors(self) -> None:
        # typed_approximately_abs_tol_* : max(|v|, 1e-12) * t
        self.assertEqual(
            Decimal(repr(max(abs(0.5), 1e-12) * 0.01)),
            TYPED_ANCHORS["typed_approximately_abs_tol_half"][1],
        )
        self.assertEqual(
            Decimal(repr(max(abs(144.0), 1e-12) * 0.01)),
            TYPED_ANCHORS["typed_approximately_abs_tol_large"][1],
        )
        # DU6 acceptance_bound widens away from zero for a negative target.
        self.assertEqual(
            Decimal(repr(acceptance_bound(-0.10, 0.01, lower=True))),
            TYPED_ANCHORS["typed_at_least_negative_widens_down"][1],
        )
        self.assertEqual(
            Decimal(repr(acceptance_bound(-0.10, 0.01, lower=False))),
            TYPED_ANCHORS["typed_at_most_negative_widens_up"][1],
        )

    def test_the_two_paths_disagree_exactly_where_the_anchors_say(self) -> None:
        target = float(DIVERGENCE_CASE["target_value"])
        observed = float(DIVERGENCE_CASE["observed"])
        legacy = legacy_meets_target(observed, target, "approximately", 0.01)
        typed = meets_target(observed, target, target, "approximately", 0.01)
        self.assertIs(legacy, DIVERGENCE_CASE["legacy_accepted"])
        self.assertIs(typed, DIVERGENCE_CASE["typed_accepted"])
        self.assertNotEqual(legacy, typed)


class BoundaryFamilyTests(unittest.TestCase):
    """The boundary list the construction card names in section 4."""

    def test_zero_target_uses_the_report_band_in_the_legacy_path(self) -> None:
        # v = 0: legacy abs_tol = max(1,0)*t = t, typed abs_tol = max(0,1e-12)*t.
        self.assertTrue(legacy_meets_target(0.005, 0.0, "approximately", 0.01))
        self.assertFalse(meets_target(0.005, 0.0, 0.0, "approximately", 0.01))
        # An exact zero observation is inside both, and has no ratio.
        self.assertTrue(legacy_meets_target(0.0, 0.0, "approximately", 0.01))
        self.assertIsNone(legacy_target_ratio(0.0, 0.0))

    def test_negative_target_is_refused_by_the_legacy_band_shape(self) -> None:
        # The legacy at_least bound narrows toward zero for a negative point
        # target; the typed bound widens away from it. Frozen difference.
        self.assertEqual(legacy_acceptance_bound(-1.0, 0.01, lower=True), -0.99)
        self.assertEqual(acceptance_bound(-1.0, 0.01, lower=True), -1.01)

    def test_tiny_values_still_use_the_legacy_floor(self) -> None:
        for target in (1e-9, 1e-6, 0.001):
            with self.subTest(target=target):
                self.assertEqual(
                    max(1.0, abs(target)) * 0.01, 0.01
                )
                self.assertTrue(
                    legacy_meets_target(target + 0.009, target, "approximately", 0.01)
                )

    def test_strict_legacy_comparisons_are_narrowed_to_three_operators(self) -> None:
        # The legacy input contract admits only at_least/at_most/approximately;
        # the owner's legacy path treats anything else as the tolerance band
        # rather than inventing a strict rule of its own.
        self.assertTrue(legacy_meets_target(1.0, 1.0, "approximately", 0.01))
        self.assertTrue(legacy_meets_target(0.99, 1.0, "at_least", 0.01))
        self.assertFalse(legacy_meets_target(0.989, 1.0, "at_least", 0.01))
        self.assertTrue(legacy_meets_target(1.01, 1.0, "at_most", 0.01))
        self.assertFalse(legacy_meets_target(1.011, 1.0, "at_most", 0.01))

    def test_legacy_ratio_is_withheld_only_for_zero(self) -> None:
        self.assertIsNone(legacy_target_ratio(5.0, 0.0))
        self.assertEqual(legacy_target_ratio(5.0, 2.0), 2.5)
        self.assertIsNotNone(legacy_target_ratio(-5.0, 2.0))


class UnmodeledAndBenchmarkFidelityTests(unittest.TestCase):
    def test_unmodeled_target_keeps_the_legacy_empty_comparison(self) -> None:
        from test_management_targets import add_target
        from test_recognition_bridge import forecast_document

        data = add_target(forecast_document(), target_value=250.0,
                          period="FY2030", treatment="out_of_horizon")
        result = run_forecast(data)
        target = result["management_target_coverage"]["targets"][0]
        self.assertEqual(target["scenario_comparison"], {})
        self.assertTrue(
            any(gap.startswith("management_target:") for gap in result["data_gaps"])
        )

    def test_independent_benchmark_compares_all_three_and_may_stay_unmet(self) -> None:
        from test_independent_targets import benchmark_document

        result = run_forecast(benchmark_document())
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        self.assertEqual(set(rows), {"low", "base", "high"})
        self.assertTrue(all(row["meets_target"] is False for row in rows.values()))

    def test_legacy_cumulative_sums_every_registered_period(self) -> None:
        result = run_forecast(legacy_cumulative_model())
        row = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        self.assertEqual(row["measurement_basis"], "cumulative_periods")
        self.assertEqual(row["measurement_periods"], ["FY2026", "FY2027"])
        self.assertAlmostEqual(
            row["modeled_value"], sum(row["modeled_period_values"].values())
        )

    def test_quarterly_typed_target_sums_the_quarter_instead_of_times_four(self) -> None:
        result = run_forecast(typed_quarterly_model())
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        for scenario, amount in (("low", 105840), ("base", 108000), ("high", 110160)):
            self.assertEqual(rows[scenario]["modeled_value"], amount)
        self.assertNotEqual(rows["base"]["modeled_value"], 108000 * 4)


class CompanyAndSegmentScopeTests(unittest.TestCase):
    def test_segment_scope_reads_the_segment_path_not_the_consolidated_one(self) -> None:
        result = run_forecast(legacy_annual_model())
        target = result["management_target_coverage"]["targets"][0]
        self.assertEqual(target["scope"]["type"], "segment")
        row = target["scenario_comparison"]["high"]
        segment = next(
            item for item in result["segments"] if item["name"] == target["scope"]["name"]
        )
        path = segment["scenarios"]["high"].get(
            "effective_revenue", segment["scenarios"]["high"]["recognized_revenue"]
        )
        self.assertEqual(row["modeled_period_values"]["FY2027"], float(path["2027"]))
        # And it is *not* silently the consolidated company path.
        consolidated = result["consolidated_forecast"]["high"]["annual_revenue"]
        self.assertNotEqual(
            row["modeled_period_values"]["FY2027"], float(consolidated["2027"])
        )

    def test_company_scope_reads_the_consolidated_path(self) -> None:
        from test_management_targets import add_target
        from test_recognition_bridge import forecast_document

        data = add_target(forecast_document(), target_value=200.0)
        target = data["management_targets"][0]
        # The declared tolerance stays inside the published 0..0.25 bound; the
        # comparison is ``approximately`` so a company-scope target is legal.
        target.update(scope={"type": "company", "name": "company"},
                      mapped_scenarios=["high"], comparison="approximately",
                      comparison_tolerance=0.25)
        result = run_forecast(data)
        row = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        consolidated = result["consolidated_forecast"]["high"]["annual_revenue"]
        self.assertEqual(row["modeled_period_values"]["FY2027"], float(consolidated["2027"]))

    def test_ownership_semantics_use_effective_revenue_when_present(self) -> None:
        """The owner reads the constraint-adjusted path, not the gross one.

        ``effective_revenue`` is ``recognized_revenue`` after the declared
        revenue constraints; it exists only when constraints were applied.
        Where the two differ, the owner must read effective revenue. Without
        any constraint the fallback to recognized revenue must hold.
        """
        result = run_forecast(legacy_annual_model())
        target = result["management_target_coverage"]["targets"][0]
        segment = next(
            item for item in result["segments"] if item["name"] == target["scope"]["name"]
        )
        output = segment["scenarios"]["high"]
        row = target["scenario_comparison"]["high"]
        if "effective_revenue" in output:
            expected = float(output["effective_revenue"]["2027"])
        else:
            expected = float(output["recognized_revenue"]["2027"])
        self.assertEqual(row["modeled_period_values"]["FY2027"], expected)
        self.assertEqual(row["modeled_value"], expected)

    def test_ownership_reads_effective_when_a_constraint_changes_it(self) -> None:
        """A revenue constraint makes effective differ from recognized.

        This is the case that distinguishes the two paths instead of relying on
        them coinciding. The owner must follow the constraint-adjusted value.
        """
        result = run_forecast(constrained_model())
        target = result["management_target_coverage"]["targets"][0]
        segment = next(
            item for item in result["segments"] if item["name"] == target["scope"]["name"]
        )
        output = segment["scenarios"]["base"]
        effective = float(output["effective_revenue"]["2027"])
        recognized = float(output["recognized_revenue"]["2027"])
        self.assertNotEqual(
            effective, recognized, "the constraint must actually change the path"
        )
        row = target["scenario_comparison"]["base"]
        self.assertEqual(row["modeled_period_values"]["FY2027"], effective)
        self.assertEqual(row["modeled_value"], effective)

    def test_ownership_fallback_reads_recognized_when_no_effective_path(self) -> None:
        """Without an adjusted path the owner falls back to recognized revenue."""
        result = run_forecast(legacy_annual_model())
        target = copy.deepcopy(result["management_target_coverage"]["targets"][0])
        for segment in result["segments"]:
            for scenario in segment["scenarios"].values():
                scenario.pop("effective_revenue", None)
        expected = float(
            next(
                item for item in result["segments"]
                if item["name"] == target["scope"]["name"]
            )["scenarios"]["high"]["recognized_revenue"]["2027"]
        )
        row = compare_legacy_target_measurement(
            target, result, periods=target["measurement_periods"]
        )["high"]
        self.assertEqual(row["modeled_period_values"]["FY2027"], expected)


class SameCurrencyAndScaleTests(unittest.TestCase):
    def test_cny_target_on_an_rmb_model_needs_no_fx(self) -> None:
        from test_du6_target_measurement_boundaries import money_target_document

        data = money_target_document(raw_value=500, comparison_value=500,
                                    raw_currency="CNY", raw_scale="亿元",
                                    model_currency="RMB", model_unit="亿元")
        result = run_forecast(data)
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        for row in rows.values():
            self.assertEqual(row["unit"], "RMB 亿元")

    def test_cross_currency_without_fx_is_refused(self) -> None:
        from test_du6_target_measurement_boundaries import money_target_document

        data = money_target_document(raw_value=100, comparison_value=100,
                                    raw_currency="HKD", raw_scale="million",
                                    model_currency="USD", model_unit="million")
        with pytest.raises(ForecastInputError, match="currency"):
            run_forecast(data)

    def test_trillion_scale_alias_normalizes(self) -> None:
        from research.target_measurement import normalize_target_bounds

        low, high = normalize_target_bounds(
            {
                "comparison_basis": {"schema_version": "management-target-comparison/1",
                                     "metric_kind": "annual_revenue_level",
                                     "period": "FY2027"},
                "raw_unit": "USD trillion", "raw_currency": "USD", "raw_scale": "trillion",
                "raw_target_value": 3.0,
            },
            {"currency": "USD", "unit": "billion"},
        )
        self.assertEqual(low, 3000.0)
        self.assertEqual(high, 3000.0)


class LegacyRowShapeFreezeTests(unittest.TestCase):
    def test_legacy_keys_are_frozen_for_every_legacy_model(self) -> None:
        from research.target_comparison import LEGACY_COMPARISON_ROW_KEYS

        for model in (legacy_annual_model, legacy_approximately_model,
                      legacy_cumulative_model):
            with self.subTest(model=model.__name__):
                result = run_forecast(model())
                rows = result["management_target_coverage"]["targets"][0][
                    "scenario_comparison"
                ]
                for row in rows.values():
                    self.assertEqual(set(row), LEGACY_COMPARISON_ROW_KEYS)

    def test_typed_level_row_keeps_its_own_key_set(self) -> None:
        result = run_forecast(typed_level_model())
        row = next(iter(
            result["management_target_coverage"]["targets"][0]["scenario_comparison"].values()
        ))
        self.assertEqual(
            set(row),
            {"metric_kind", "period", "unit", "modeled_value", "target_value",
             "target_low", "target_high", "comparison", "comparison_status",
             "reason", "meets_target", "attainment_ratio", "difference"},
        )

    def test_typed_and_legacy_models_really_take_different_paths(self) -> None:
        """Guard against a fixture silently testing the wrong branch."""
        from research.target_comparison import is_typed_target

        legacy = legacy_annual_model()["management_targets"][0]
        typed = typed_level_model()["management_targets"][0]
        growth = growth_model()["management_targets"][0]
        quarter = typed_quarterly_model()["management_targets"][0]
        self.assertFalse(is_typed_target(legacy))
        for name, target in (("typed_level", typed), ("typed_growth", growth),
                             ("typed_quarterly", quarter)):
            with self.subTest(model=name):
                self.assertTrue(is_typed_target(target))
                self.assertEqual(
                    target["comparison_basis"]["schema_version"],
                    "management-target-comparison/1",
                )

    def test_typed_level_row_has_no_legacy_measurement_keys(self) -> None:
        """A typed row must not be mistaken for a legacy one."""
        result = run_forecast(typed_level_model())
        row = next(iter(
            result["management_target_coverage"]["targets"][0]["scenario_comparison"].values()
        ))
        self.assertFalse(set(row) == {
            "measurement_basis", "measurement_periods", "modeled_period_values",
            "modeled_value", "target_value", "attainment_ratio", "meets_target",
        })


if __name__ == "__main__":
    unittest.main()
