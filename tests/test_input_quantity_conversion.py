"""R6-RF-INPUT I1: explicit human-unit conversion for research input quantities.

The US cross-market failure built a 5-percentage-point shock as
``shock_value=5.0`` on a ratio parameter; the engine arithmetic on that wrong
input is self-consistently green, so no clamp or float tolerance can catch it.
The responsibility layer is the input construction half: an explicit,
auditable conversion from the unit a human source uses (pp, percent, bp,
million USD, thousand units) to the engine's contract unit (fraction ratio,
basis points, declared absolute unit).

Hand-computed oracle values are used throughout; none of the expected numbers
are read back from the implementation.
"""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from test_golden_behavior_lock import model_document  # noqa: E402


class ConvertInputQuantityTests(unittest.TestCase):
    """Unit-algebra oracle: convert_input_quantity(value, *, input_unit, engine_unit)."""

    def test_percentage_point_to_ratio_fraction(self) -> None:
        from research.input_quantities import convert_input_quantity

        record = convert_input_quantity(5, input_unit="pp", engine_unit="ratio")
        self.assertEqual(record["value"], 5)
        self.assertEqual(record["input_unit"], "pp")
        self.assertEqual(record["engine_unit"], "ratio")
        self.assertAlmostEqual(record["engine_value"], 0.05, places=12)
        # The conversion expression must be preserved for audit, not just the number.
        self.assertIn("0.05", record["conversion"])
        self.assertIn("pp", record["conversion"])

    def test_percent_to_ratio_fraction(self) -> None:
        from research.input_quantities import convert_input_quantity

        record = convert_input_quantity(5, input_unit="percent", engine_unit="ratio")
        self.assertAlmostEqual(record["engine_value"], 0.05, places=12)

    def test_basis_point_to_ratio_fraction(self) -> None:
        from research.input_quantities import convert_input_quantity

        record = convert_input_quantity(50, input_unit="bp", engine_unit="ratio")
        self.assertAlmostEqual(record["engine_value"], 0.005, places=12)

    def test_zero_and_negative_shares_convert_by_the_same_algebra(self) -> None:
        from research.input_quantities import convert_input_quantity

        self.assertEqual(convert_input_quantity(0, input_unit="pp", engine_unit="ratio")["engine_value"], 0.0)
        self.assertAlmostEqual(
            convert_input_quantity(-5, input_unit="pp", engine_unit="ratio")["engine_value"],
            -0.05,
            places=12,
        )

    def test_ratio_five_keeps_its_real_semantics(self) -> None:
        """ratio=5.0 is a 500% factor; it must not be silently read as 5 percent."""
        from research.input_quantities import convert_input_quantity

        record = convert_input_quantity(5.0, input_unit="ratio", engine_unit="ratio")
        self.assertEqual(record["engine_value"], 5.0)
        self.assertIn("identity", record["conversion"].lower())

    def test_unit_aliases_and_whitespace_are_normalized(self) -> None:
        from research.input_quantities import convert_input_quantity

        for alias in ("percentage_point", "percentage_points", " PP ", "Pct", "%"):
            record = convert_input_quantity(5, input_unit=alias, engine_unit="ratio")
            self.assertAlmostEqual(record["engine_value"], 0.05, places=12)

    def test_cross_share_units(self) -> None:
        from research.input_quantities import convert_input_quantity

        self.assertAlmostEqual(
            convert_input_quantity(5, input_unit="pp", engine_unit="basis_point")["engine_value"],
            500.0,
            places=9,
        )
        self.assertAlmostEqual(
            convert_input_quantity(0.05, input_unit="ratio", engine_unit="percent")["engine_value"],
            5.0,
            places=9,
        )

    def test_money_scale_conversion_is_explicit_not_currency_conversion(self) -> None:
        from research.input_quantities import convert_input_quantity

        record = convert_input_quantity(5000, input_unit="usd_thousand", engine_unit="usd_million")
        self.assertAlmostEqual(record["engine_value"], 5.0, places=12)
        self.assertEqual(
            convert_input_quantity(5, input_unit="usd_million", engine_unit="usd_million")["engine_value"],
            5.0,
        )
        self.assertAlmostEqual(
            convert_input_quantity(2.5, input_unit="rmb_billion", engine_unit="rmb_million")["engine_value"],
            2500.0,
            places=9,
        )

    def test_count_scale_conversion(self) -> None:
        from research.input_quantities import convert_input_quantity

        record = convert_input_quantity(3, input_unit="thousand_units", engine_unit="units")
        self.assertAlmostEqual(record["engine_value"], 3000.0, places=9)

    def test_rejects_bool_nan_inf_and_non_numeric(self) -> None:
        from research.input_quantities import convert_input_quantity

        for bad in (True, False, float("nan"), float("inf"), float("-inf"), "5", None):
            with self.assertRaises(ForecastInputError):
                convert_input_quantity(bad, input_unit="pp", engine_unit="ratio")

    def test_rejects_unknown_units(self) -> None:
        from research.input_quantities import convert_input_quantity

        for bad_unit in ("magic", "points", "", "percent-ish"):
            with self.assertRaises(ForecastInputError):
                convert_input_quantity(5, input_unit=bad_unit, engine_unit="ratio")
            with self.assertRaises(ForecastInputError):
                convert_input_quantity(5, input_unit="pp", engine_unit=bad_unit)

    def test_rejects_incompatible_unit_families(self) -> None:
        """Absolute money/count quantities must never be silently mixed with percent."""
        from research.input_quantities import convert_input_quantity

        incompatible = [
            ("pp", "usd_million"),
            ("percent", "thousand_units"),
            ("usd_million", "ratio"),
            ("usd_million", "percent"),
            ("thousand_units", "ratio"),
            ("usd_million", "thousand_units"),
        ]
        for input_unit, engine_unit in incompatible:
            with self.assertRaises(ForecastInputError):
                convert_input_quantity(5, input_unit=input_unit, engine_unit=engine_unit)

    def test_rejects_cross_currency_conversions_without_a_rate(self) -> None:
        from research.input_quantities import convert_input_quantity

        with self.assertRaises(ForecastInputError):
            convert_input_quantity(5, input_unit="usd_million", engine_unit="rmb_million")


class BuildSensitivityTestTests(unittest.TestCase):
    """build_sensitivity_test chooses the engine shock_type from unit + semantics."""

    def test_percentage_point_is_additive_fraction(self) -> None:
        from research.input_quantities import build_sensitivity_test

        test = build_sensitivity_test(
            parameter_id="growth", value=5, input_unit="pp", shock_semantics="additive"
        )
        self.assertEqual(test["shock_type"], "percentage_point")
        self.assertAlmostEqual(test["shock_value"], 0.05, places=12)
        self.assertEqual(test["name"], "growth")
        self.assertEqual(test["parameter_id"], "growth")
        self.assertEqual(test["input_quantity"]["input_unit"], "pp")
        self.assertAlmostEqual(test["input_quantity"]["engine_value"], 0.05, places=12)

    def test_percent_is_multiplicative(self) -> None:
        from research.input_quantities import build_sensitivity_test

        test = build_sensitivity_test(
            parameter_id="growth", value=5, input_unit="percent", shock_semantics="multiplicative"
        )
        self.assertEqual(test["shock_type"], "percent")
        self.assertAlmostEqual(test["shock_value"], 0.05, places=12)

    def test_basis_point_stays_in_engine_bp_units(self) -> None:
        from research.input_quantities import build_sensitivity_test

        test = build_sensitivity_test(
            parameter_id="margin", value=50, input_unit="bp", shock_semantics="additive"
        )
        self.assertEqual(test["shock_type"], "basis_point")
        self.assertAlmostEqual(test["shock_value"], 50.0, places=9)

    def test_absolute_units_map_to_absolute_shock(self) -> None:
        from research.input_quantities import build_sensitivity_test

        test = build_sensitivity_test(
            parameter_id="price", value=2, input_unit="usd_million", shock_semantics="absolute"
        )
        self.assertEqual(test["shock_type"], "absolute")
        self.assertAlmostEqual(test["shock_value"], 2.0, places=12)

    def test_semantic_mismatch_between_unit_and_shock_is_rejected(self) -> None:
        """5 percent is NOT 5 percentage points; the wrong pairing must fail loudly."""
        from research.input_quantities import build_sensitivity_test

        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=5, input_unit="percent", shock_semantics="additive"
            )
        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=5, input_unit="pp", shock_semantics="multiplicative"
            )
        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=5, input_unit="bp", shock_semantics="multiplicative"
            )
        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=5, input_unit="usd_million", shock_semantics="additive"
            )

    def test_nonpositive_and_malformed_shocks_are_rejected(self) -> None:
        from research.input_quantities import build_sensitivity_test

        for bad_value in (0, -5):
            with self.assertRaises(ForecastInputError):
                build_sensitivity_test(
                    parameter_id="growth", value=bad_value, input_unit="pp",
                    shock_semantics="additive",
                )
        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=True, input_unit="pp", shock_semantics="additive"
            )


class FormalSensitivityPathTests(unittest.TestCase):
    """The converted shock must flow through the real engine sensitivity path."""

    def test_pp_shock_on_ratio_driver_requests_fraction_values(self) -> None:
        from research.input_quantities import build_sensitivity_test

        data = model_document("capacity")
        # capacity_utilization driver: base utilization = 0.8 (golden fixture).
        parameter_id = "capacity_utilization_base_2026"
        test = build_sensitivity_test(
            parameter_id=parameter_id, value=5, input_unit="pp", shock_semantics="additive"
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        # Hand-computed oracle: 0.8 -/+ 0.05 -> 0.75 / 0.85 requested, unclamped.
        self.assertAlmostEqual(sensitivity["requested_values"]["down"], 0.75, places=12)
        self.assertAlmostEqual(sensitivity["requested_values"]["up"], 0.85, places=12)
        self.assertFalse(sensitivity["clamped"]["down"])
        self.assertFalse(sensitivity["clamped"]["up"])
        self.assertEqual(sensitivity["shock_type"], "percentage_point")

    def test_legacy_malformed_pp_input_still_shows_what_it_does(self) -> None:
        """The recorded US failure (shock_value=5.0 on ratio, no conversion record)
        must stay visible as a 500pp request with clamping, not be silently
        relabeled as 5pp. The clamp is transparent; the fix is at construction."""
        data = model_document("capacity")
        parameter_id = "capacity_utilization_base_2026"
        data["sensitivity_tests"] = [
            {"name": "utilization_5pp", "parameter_id": parameter_id,
             "shock_type": "percentage_point", "shock_value": 5.0},
        ]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        # 0.8 -/+ 5.0 clamps to [0, 1]; the requested values expose the unit error.
        self.assertAlmostEqual(sensitivity["requested_values"]["down"], -4.2, places=12)
        self.assertAlmostEqual(sensitivity["requested_values"]["up"], 5.8, places=12)
        self.assertTrue(sensitivity["clamped"]["down"] or sensitivity["clamped"]["up"])

    def test_stored_input_quantity_record_is_recomputed_by_the_engine(self) -> None:
        from research.input_quantities import build_sensitivity_test

        data = model_document("capacity")
        test = build_sensitivity_test(
            parameter_id="capacity_utilization_base_2026", value=5,
            input_unit="pp", shock_semantics="additive",
        )
        # A forged conversion record (claiming 5pp == 5.0) must be rejected.
        test["input_quantity"]["engine_value"] = 5.0
        data["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "input_quantity"):
            run_forecast(data)

    def test_sensitivity_output_carries_the_conversion_lineage(self) -> None:
        from research.input_quantities import build_sensitivity_test

        data = model_document("capacity")
        test = build_sensitivity_test(
            parameter_id="capacity_utilization_base_2026", value=5,
            input_unit="pp", shock_semantics="additive",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        record = result["sensitivities"][0].get("input_quantity")
        self.assertIsNotNone(record)
        self.assertEqual(record["input_unit"], "pp")
        self.assertAlmostEqual(record["engine_value"], 0.05, places=12)


if __name__ == "__main__":
    unittest.main()
