"""DU5-RF-UNITS: one money-unit description (Currency x Scale) and real
parameter-unit consistency for sensitivity inputs.

The R6 layer described money units with three parallel hand tables and
re-enumerated currency spellings in the shock semantics, so HKD was missing
and a self-consistent record could carry a currency/scale that contradicts the
parameter it shocks. This file freezes the old USD/RMB/share/count behaviour
byte-for-byte and adds the HKD/wan/yi vocabulary plus the consumer-side
parameter-unit check.

Hand-computed oracle values are used throughout (7.25 yi = 725 million,
5 shiyi = 5000 million and the reverses); no expected number is read back
from the implementation.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from research.input_quantities import (  # noqa: E402
    build_sensitivity_test,
    convert_input_quantity,
    validate_input_quantity_record,
)
from test_golden_behavior_lock import model_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def re_denominate(data: dict, currency: str, scale: str) -> dict:
    """Re-denominate a synthetic fixture into ``currency scale`` (factor 1)."""
    data = copy.deepcopy(data)
    data["currency"] = currency
    data["unit"] = scale
    for entry in data["parameters"]:
        if "currency" in entry:
            entry["currency"] = currency
            entry["scale"] = scale
            entry["unit"] = f"{currency} {scale}"
    for claim in data["evidence_claims"]:
        unit = claim.get("unit")
        if isinstance(unit, str) and unit.startswith("USD "):
            claim["unit"] = f"{currency} {scale}"
    return data


def hkd_document() -> dict:
    return re_denominate(forecast_document(), "HKD", "million")


class HkdScaleConversionTests(unittest.TestCase):
    """HKD is a supported currency; same-currency scale conversion only."""

    def test_hkd_billion_to_million_and_million_to_thousand(self) -> None:
        # 5 HKD billion = 5000 HKD million (x1000); 5 HKD million = 5000
        # HKD thousand (x1000).
        record = convert_input_quantity(5, input_unit="hkd_billion", engine_unit="hkd_million")
        self.assertEqual(record["engine_value"], 5000.0)
        record = convert_input_quantity(5, input_unit="hkd_million", engine_unit="hkd_thousand")
        self.assertEqual(record["engine_value"], 5000.0)

    def test_hkd_yi_to_million_is_hand_checked(self) -> None:
        # 7.25 HKD yi (1e8) = 725 HKD million.
        record = convert_input_quantity(7.25, input_unit="hkd_100m", engine_unit="hkd_million")
        self.assertEqual(record["engine_value"], 725.0)

    def test_hkd_reverse_scaling_and_zero_negative_decimal(self) -> None:
        self.assertAlmostEqual(
            convert_input_quantity(725, input_unit="hkd_million", engine_unit="hkd_100m")["engine_value"],
            7.25,
            places=12,
        )
        self.assertEqual(
            convert_input_quantity(0, input_unit="hkd_billion", engine_unit="hkd_million")["engine_value"],
            0.0,
        )
        self.assertEqual(
            convert_input_quantity(-5, input_unit="hkd_billion", engine_unit="hkd_million")["engine_value"],
            -5000.0,
        )
        self.assertAlmostEqual(
            convert_input_quantity(2.5, input_unit="hkd_billion", engine_unit="hkd_million")["engine_value"],
            2500.0,
            places=9,
        )


class RmbWanYiScaleConversionTests(unittest.TestCase):
    """RMB/CNY yi -> million/wan with hand oracles, both directions."""

    def test_rmb_yi_to_million_and_wan(self) -> None:
        # 7.25 RMB yi = 725 RMB million = 72500 RMB wan.
        self.assertEqual(
            convert_input_quantity(7.25, input_unit="rmb_100m", engine_unit="rmb_million")["engine_value"],
            725.0,
        )
        self.assertEqual(
            convert_input_quantity(7.25, input_unit="rmb_100m", engine_unit="rmb_10k")["engine_value"],
            72500.0,
        )

    def test_rmb_shiyi_to_million_and_reverse(self) -> None:
        # 5 RMB shiyi (1e9) = 5000 RMB million; the reverse divides by 1000.
        self.assertEqual(
            convert_input_quantity(5, input_unit="rmb_billion", engine_unit="rmb_million")["engine_value"],
            5000.0,
        )
        self.assertAlmostEqual(
            convert_input_quantity(5000, input_unit="rmb_million", engine_unit="rmb_billion")["engine_value"],
            5.0,
            places=12,
        )
        self.assertAlmostEqual(
            convert_input_quantity(725, input_unit="rmb_million", engine_unit="rmb_100m")["engine_value"],
            7.25,
            places=12,
        )
        self.assertAlmostEqual(
            convert_input_quantity(72500, input_unit="rmb_10k", engine_unit="rmb_100m")["engine_value"],
            7.25,
            places=12,
        )

    def test_zero_negative_and_decimal_rmb_values_convert_by_the_same_algebra(self) -> None:
        self.assertEqual(
            convert_input_quantity(0, input_unit="rmb_100m", engine_unit="rmb_10k")["engine_value"],
            0.0,
        )
        self.assertEqual(
            convert_input_quantity(-7.25, input_unit="rmb_100m", engine_unit="rmb_million")["engine_value"],
            -725.0,
        )
        self.assertAlmostEqual(
            convert_input_quantity(2.5, input_unit="rmb_100m", engine_unit="rmb_million")["engine_value"],
            250.0,
            places=12,
        )

    def test_cny_is_the_same_currency_as_rmb(self) -> None:
        """CNY spellings normalize to the existing RMB units, never to USD."""
        record = convert_input_quantity(7.25, input_unit="cny_100m", engine_unit="cny_million")
        self.assertEqual(record["engine_value"], 725.0)
        # Cross-alias spellings convert: CNY and RMB are one currency family.
        self.assertEqual(
            convert_input_quantity(7.25, input_unit="cny_100m", engine_unit="rmb_million")["engine_value"],
            725.0,
        )
        self.assertEqual(
            convert_input_quantity(5, input_unit="cny_billion", engine_unit="rmb_million")["engine_value"],
            5000.0,
        )
        self.assertAlmostEqual(
            convert_input_quantity(5, input_unit="cny_million", engine_unit="rmb_10k")["engine_value"],
            500.0,
            places=12,
        )


class CrossCurrencyAndFamilyRejectTests(unittest.TestCase):
    def test_usd_hkd_rmb_pairs_never_convert(self) -> None:
        incompatible = [
            ("usd_million", "hkd_million"),
            ("hkd_million", "usd_million"),
            ("hkd_million", "rmb_million"),
            ("rmb_million", "hkd_million"),
            ("usd_billion", "cny_million"),
            ("cny_100m", "usd_million"),
        ]
        for input_unit, engine_unit in incompatible:
            with self.subTest(input_unit=input_unit, engine_unit=engine_unit):
                with self.assertRaisesRegex(ForecastInputError, "incompatible unit conversion"):
                    convert_input_quantity(5, input_unit=input_unit, engine_unit=engine_unit)

    def test_money_count_and_share_families_never_mix(self) -> None:
        incompatible = [
            ("hkd_million", "million_units"),
            ("million_units", "hkd_million"),
            ("rmb_10k", "units"),
            ("pp", "hkd_million"),
            ("hkd_million", "pp"),
            ("usd_million", "basis_point"),
            ("basis_point", "rmb_100m"),
        ]
        for input_unit, engine_unit in incompatible:
            with self.subTest(input_unit=input_unit, engine_unit=engine_unit):
                with self.assertRaisesRegex(ForecastInputError, "incompatible unit conversion"):
                    convert_input_quantity(5, input_unit=input_unit, engine_unit=engine_unit)

    def test_identity_short_circuit_only_applies_to_the_same_unit(self) -> None:
        """cny_million and rmb_million name one unit (identity record), while a
        genuinely different same-currency unit is a real scale conversion."""
        record = convert_input_quantity(5, input_unit="cny_million", engine_unit="rmb_million")
        self.assertEqual(record["engine_value"], 5.0)
        self.assertIn("identity", record["conversion"].lower())
        record = convert_input_quantity(5, input_unit="hkd_billion", engine_unit="hkd_million")
        self.assertEqual(record["engine_value"], 5000.0)
        self.assertNotIn("identity", record["conversion"].lower())


class UnknownSpellingTests(unittest.TestCase):
    def test_unknown_and_multi_currency_spellings_are_rejected_not_guessed(self) -> None:
        for bad_unit in (
            "hkd_mega",
            "usd_hkd_million",
            "usd hkd million",
            "money_million",
            "million",
            "hkd",
            "yuan",
            "wan",
            "wan_yuan",
            "wan_yuan_million",
            "万元",
            "",
            "  ",
        ):
            with self.subTest(bad_unit=bad_unit):
                with self.assertRaises(ForecastInputError):
                    convert_input_quantity(5, input_unit=bad_unit, engine_unit="rmb_million")
                with self.assertRaises(ForecastInputError):
                    convert_input_quantity(5, input_unit="rmb_million", engine_unit=bad_unit)

    def test_currency_less_wan_yuan_never_defaults_to_rmb(self) -> None:
        """A bare 万元 has no calling context: unknown/error, never guessed RMB.

        The target being RMB does not license guessing the source currency.
        """
        for spelling in ("wan_yuan", "万元", "wan", "yi", "亿", "百万", "百万美元"):
            with self.subTest(spelling=spelling):
                with self.assertRaisesRegex(ForecastInputError, "unknown"):
                    convert_input_quantity(7.25, input_unit=spelling, engine_unit="rmb_10k")


class FiniteNumberBoundaryTests(unittest.TestCase):
    def test_nan_inf_bool_and_non_numeric_are_rejected_for_hkd_too(self) -> None:
        for bad in (True, False, float("nan"), float("inf"), float("-inf"), "5", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ForecastInputError):
                    convert_input_quantity(bad, input_unit="hkd_billion", engine_unit="hkd_million")

    def test_overflowing_conversion_is_rejected_not_wrapped(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "finite"):
            convert_input_quantity(1e308, input_unit="usd_billion", engine_unit="usd_thousand")


class LegacyFreezeTests(unittest.TestCase):
    """Pre-DU5 records and builder outputs re-derive byte-identically."""

    FROZEN_RECORDS = [
        (
            {"value": 5, "input_unit": "pp", "engine_unit": "ratio"},
            {
                "schema_version": "rf-input-quantity/1",
                "value": 5.0,
                "input_unit": "pp",
                "engine_unit": "ratio",
                "engine_value": 0.05,
                "conversion": "5 pp = 0.05 (1 pp = 0.01 ratio fraction)",
            },
        ),
        (
            {"value": 5, "input_unit": "usd_thousand", "engine_unit": "usd_million"},
            {
                "schema_version": "rf-input-quantity/1",
                "value": 5.0,
                "input_unit": "usd_thousand",
                "engine_unit": "usd_million",
                "engine_value": 0.005,
                "conversion": "5 usd_thousand x 0.001 = 0.005 usd_million",
            },
        ),
        (
            {"value": 2.5, "input_unit": "rmb_billion", "engine_unit": "rmb_million"},
            {
                "schema_version": "rf-input-quantity/1",
                "value": 2.5,
                "input_unit": "rmb_billion",
                "engine_unit": "rmb_million",
                "engine_value": 2500.0,
                "conversion": "2.5 rmb_billion x 1000 = 2500 rmb_million",
            },
        ),
        (
            {"value": 7.25, "input_unit": "rmb_100m", "engine_unit": "rmb_million"},
            {
                "schema_version": "rf-input-quantity/1",
                "value": 7.25,
                "input_unit": "rmb_100m",
                "engine_unit": "rmb_million",
                "engine_value": 725.0,
                "conversion": "7.25 rmb_100m x 100 = 725 rmb_million",
            },
        ),
        (
            {"value": 3, "input_unit": "thousand_units", "engine_unit": "units"},
            {
                "schema_version": "rf-input-quantity/1",
                "value": 3.0,
                "input_unit": "thousand_units",
                "engine_unit": "units",
                "engine_value": 3000.0,
                "conversion": "3 thousand_units x 1000 = 3000 units",
            },
        ),
        (
            {"value": 5.0, "input_unit": "ratio", "engine_unit": "ratio"},
            {
                "schema_version": "rf-input-quantity/1",
                "value": 5.0,
                "input_unit": "ratio",
                "engine_unit": "ratio",
                "engine_value": 5.0,
                "conversion": "5 ratio is already the engine unit ratio (identity)",
            },
        ),
        (
            {"value": 50, "input_unit": "bp", "engine_unit": "basis_point"},
            {
                "schema_version": "rf-input-quantity/1",
                "value": 50.0,
                "input_unit": "bp",
                "engine_unit": "basis_point",
                "engine_value": 50.0,
                "conversion": "50 basis_point is already the engine unit basis_point (identity)",
            },
        ),
    ]

    def test_frozen_records_re_derive_exactly(self) -> None:
        for kwargs, frozen in self.FROZEN_RECORDS:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(convert_input_quantity(**kwargs), frozen)

    def test_frozen_stored_records_still_recompute(self) -> None:
        for _kwargs, frozen in self.FROZEN_RECORDS:
            with self.subTest(frozen=frozen):
                expected = validate_input_quantity_record(copy.deepcopy(frozen), field="r")
                self.assertEqual(expected["engine_value"], frozen["engine_value"])

    def test_frozen_builder_outputs_are_unchanged(self) -> None:
        additive = build_sensitivity_test(
            parameter_id="growth", value=5, input_unit="pp", shock_semantics="additive"
        )
        self.assertEqual(
            additive,
            {
                "name": "growth",
                "parameter_id": "growth",
                "shock_type": "percentage_point",
                "shock_value": 0.05,
                "input_quantity": {
                    "schema_version": "rf-input-quantity/1",
                    "value": 5.0,
                    "input_unit": "pp",
                    "engine_unit": "ratio",
                    "engine_value": 0.05,
                    "conversion": "5 pp = 0.05 (1 pp = 0.01 ratio fraction)",
                },
            },
        )
        absolute = build_sensitivity_test(
            parameter_id="price", value=2, input_unit="usd_million", shock_semantics="absolute"
        )
        self.assertEqual(
            absolute,
            {
                "name": "price",
                "parameter_id": "price",
                "shock_type": "absolute",
                "shock_value": 2.0,
                "input_quantity": {
                    "schema_version": "rf-input-quantity/1",
                    "value": 2.0,
                    "input_unit": "usd_million",
                    "engine_unit": "usd_million",
                    "engine_value": 2.0,
                    "conversion": "2 usd_million is already the engine unit usd_million (identity)",
                },
            },
        )


class BuilderEngineUnitTests(unittest.TestCase):
    """The optional engine_unit converts for real; it never relabels."""

    def test_explicit_engine_unit_converts_hkd_shiyi_to_million(self) -> None:
        # 5 HKD shiyi = 5000 HKD million, hand-computed, and the converted
        # shock_value is what the engine applies.
        test = build_sensitivity_test(
            parameter_id="revenue", value=5, input_unit="hkd_billion",
            shock_semantics="absolute", engine_unit="hkd_million",
        )
        self.assertEqual(test["shock_type"], "absolute")
        self.assertEqual(test["shock_value"], 5000.0)
        self.assertEqual(test["input_quantity"]["engine_value"], 5000.0)
        self.assertEqual(test["input_quantity"]["engine_unit"], "hkd_million")
        self.assertIn("x 1000", test["input_quantity"]["conversion"])

    def test_explicit_engine_unit_converts_hkd_yi_to_million(self) -> None:
        # 7.25 HKD yi = 725 HKD million.
        test = build_sensitivity_test(
            parameter_id="revenue", value=7.25, input_unit="hkd_100m",
            shock_semantics="absolute", engine_unit="hkd_million",
        )
        self.assertEqual(test["shock_value"], 725.0)

    def test_explicit_engine_unit_reverses_to_yi(self) -> None:
        # 725 HKD million = 7.25 HKD yi (reverse scaling).
        test = build_sensitivity_test(
            parameter_id="revenue", value=725, input_unit="hkd_million",
            shock_semantics="absolute", engine_unit="hkd_100m",
        )
        self.assertAlmostEqual(test["shock_value"], 7.25, places=12)

    def test_explicit_engine_unit_rejects_cross_currency(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "incompatible unit conversion"):
            build_sensitivity_test(
                parameter_id="revenue", value=5, input_unit="hkd_billion",
                shock_semantics="absolute", engine_unit="usd_million",
            )

    def test_explicit_engine_unit_share_shock_targets_the_engine_contract_unit(self) -> None:
        # 50 bp additive as a ratio-fraction shock is 0.005 (real conversion),
        # and as bp stays 50; both keep the additive semantics.
        as_ratio = build_sensitivity_test(
            parameter_id="growth", value=50, input_unit="bp",
            shock_semantics="additive", engine_unit="ratio",
        )
        self.assertEqual(as_ratio["shock_type"], "percentage_point")
        self.assertAlmostEqual(as_ratio["shock_value"], 0.005, places=12)
        as_bp = build_sensitivity_test(
            parameter_id="growth", value=5, input_unit="pp",
            shock_semantics="additive", engine_unit="basis_point",
        )
        self.assertEqual(as_bp["shock_type"], "basis_point")
        self.assertAlmostEqual(as_bp["shock_value"], 500.0, places=9)

    def test_explicit_engine_unit_rejects_human_spelling_as_engine_target(self) -> None:
        """pp/percent are human spellings; an additive engine shock is
        ratio or basis_point, and a multiplicative one is the ratio factor.
        Relabeling 5 pp as shock_value 5 would read as 500 pp."""
        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=5, input_unit="pp",
                shock_semantics="additive", engine_unit="pp",
            )
        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=5, input_unit="percent",
                shock_semantics="multiplicative", engine_unit="percent",
            )
        with self.assertRaises(ForecastInputError):
            build_sensitivity_test(
                parameter_id="growth", value=5, input_unit="percent",
                shock_semantics="multiplicative", engine_unit="basis_point",
            )

    def test_explicit_engine_unit_enters_the_real_revenue_delta(self) -> None:
        """The converted shock must move terminal revenue, not sit as metadata.

        Hand oracle: base terminal is 181.5 (121 + 60.5); the shocked parameter
        is the 2027 driver at 121. Up: 121 + 725 = 846 -> terminal 906.5.
        Down: 121 - 725 clamps to 0 -> terminal 60.5 (clamp stays transparent).
        """
        data = hkd_document()
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=7.25, input_unit="hkd_100m",
            shock_semantics="absolute", engine_unit="hkd_million",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        self.assertEqual(sensitivity["shock_value"], 725.0)
        self.assertEqual(sensitivity["input_quantity"]["engine_unit"], "hkd_million")
        self.assertAlmostEqual(
            result["consolidated_forecast"]["base"]["terminal_revenue"], 181.5, places=9
        )
        self.assertAlmostEqual(sensitivity["requested_values"]["up"], 846.0, places=9)
        self.assertAlmostEqual(sensitivity["up_terminal_revenue"], 906.5, places=9)
        self.assertTrue(sensitivity["clamped"]["down"])
        self.assertAlmostEqual(sensitivity["down_terminal_revenue"], 60.5, places=9)


class RecordTamperTests(unittest.TestCase):
    """Reloaded records re-derive; any tampering fails closed."""

    def _record(self) -> dict:
        return build_sensitivity_test(
            parameter_id="revenue", value=7.25, input_unit="hkd_100m",
            shock_semantics="absolute", engine_unit="hkd_million",
        )["input_quantity"]

    def test_tampered_engine_value_value_unit_and_conversion_are_rejected(self) -> None:
        mutations = {
            "engine_value": lambda r: r.update(engine_value=700.0),
            "value": lambda r: r.update(value=7.0),
            "input_unit": lambda r: r.update(input_unit="hkd_million"),
            "engine_unit": lambda r: r.update(engine_unit="hkd_100m"),
            "conversion": lambda r: r.update(conversion=r["conversion"] + " x 1"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                record = self._record()
                mutate(record)
                with self.assertRaisesRegex(ForecastInputError, "input_quantity"):
                    validate_input_quantity_record(record, field="r.input_quantity")

    def test_tampered_record_is_rejected_by_the_real_sensitivity_path(self) -> None:
        data = hkd_document()
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=7.25, input_unit="hkd_100m",
            shock_semantics="absolute", engine_unit="hkd_million",
        )
        test["input_quantity"]["value"] = 7.0  # source_value tampered
        data["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "input_quantity"):
            run_forecast(data)


class ParameterUnitCompatibilityTests(unittest.TestCase):
    """The consumer checks the record against the parameter's real unit.

    All of these run through the public ``run_forecast`` sensitivity path,
    not only the helper.
    """

    def test_self_consistent_usd_record_on_hkd_parameter_is_rejected(self) -> None:
        data = hkd_document()
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=5, input_unit="usd_million",
            shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "currency"):
            run_forecast(data)

    def test_same_number_in_record_currency_and_parameter_currency_passes(self) -> None:
        data = hkd_document()
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=5, input_unit="hkd_million",
            shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        self.assertEqual(sensitivity["shock_value"], 5.0)
        self.assertEqual(sensitivity["input_quantity"]["input_unit"], "hkd_million")

    def test_self_consistent_record_with_wrong_scale_is_rejected(self) -> None:
        data = forecast_document()  # USD million parameters
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=5, input_unit="usd_thousand",
            shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "scale"):
            run_forecast(data)

    def test_money_record_on_quantity_parameter_is_rejected(self) -> None:
        data = model_document("volume")
        test = build_sensitivity_test(
            parameter_id="volume_saleable_volume_base_2026", value=5,
            input_unit="usd_million", shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "cannot shock"):
            run_forecast(data)

    def test_per_unit_dimension_gives_a_clear_diagnostic(self) -> None:
        """revenue_per_unit is monetary-per-unit: an absolute money shock
        would silently drop the denominator and must be diagnosed."""
        data = model_document("volume")
        test = build_sensitivity_test(
            parameter_id="volume_realized_price_base_2026", value=5,
            input_unit="usd_million", shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "monetary-per-unit"):
            run_forecast(data)

    def test_count_record_on_money_parameter_is_rejected(self) -> None:
        data = forecast_document()
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=5, input_unit="million_units",
            shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "cannot shock"):
            run_forecast(data)

    def test_absolute_shock_never_pairs_with_a_share_record(self) -> None:
        data = forecast_document()
        record = convert_input_quantity(5, input_unit="pp", engine_unit="ratio")
        data["sensitivity_tests"] = [{
            "name": "mixed_semantics", "parameter_id": "0_base_2027",
            "shock_type": "absolute", "shock_value": 0.05,
            "input_quantity": record,
        }]
        with self.assertRaisesRegex(ForecastInputError, "absolute shock"):
            run_forecast(data)

    def test_relative_shock_never_pairs_with_a_money_record(self) -> None:
        data = forecast_document()
        record = convert_input_quantity(0.05, input_unit="usd_million", engine_unit="usd_million")
        data["sensitivity_tests"] = [{
            "name": "mixed_relative", "parameter_id": "0_base_2027",
            "shock_type": "percent", "shock_value": 0.05,
            "input_quantity": record,
        }]
        with self.assertRaisesRegex(ForecastInputError, "share-of-total"):
            run_forecast(data)

    def test_relative_share_shock_on_revenue_parameter_still_passes(self) -> None:
        """Frozen positive control from the R6 input-semantics E2E: a relative
        5 percent shock on a revenue-dimension parameter is dimension-free."""
        data = forecast_document()
        test = build_sensitivity_test(
            parameter_id="0_base_2026", value=5, input_unit="percent",
            shock_semantics="multiplicative",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        self.assertEqual(sensitivity["shock_type"], "percent")
        self.assertAlmostEqual(sensitivity["shock_value"], 0.05, places=12)
        self.assertAlmostEqual(sensitivity["requested_values"]["down"], 104.5, places=9)
        self.assertAlmostEqual(sensitivity["requested_values"]["up"], 115.5, places=9)

    def test_wan_scale_parameter_context_resolves_currency_less_scale(self) -> None:
        """A parameter scale like 万 is resolved with its explicit currency
        context (HKD here), while the bare currency-less 万元 spelling stays
        unknown for input records."""
        data = re_denominate(forecast_document(), "HKD", "万")
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=5, input_unit="hkd_wan",
            shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        self.assertEqual(result["sensitivities"][0]["shock_value"], 5.0)
        # Same record against a million-scale parameter is a scale mismatch.
        data_million = hkd_document()
        data_million["sensitivity_tests"] = [test]
        with self.assertRaisesRegex(ForecastInputError, "scale"):
            run_forecast(data_million)

    def test_usd_rmb_samples_do_not_regress(self) -> None:
        """Old USD/RMB public-path behaviour is frozen."""
        data = forecast_document()  # USD million
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=2.5, input_unit="usd_million",
            shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        self.assertEqual(sensitivity["shock_value"], 2.5)
        self.assertAlmostEqual(sensitivity["requested_values"]["up"], 123.5, places=9)
        data = re_denominate(forecast_document(), "CNY", "million")
        test = build_sensitivity_test(
            parameter_id="0_base_2027", value=2.5, input_unit="cny_million",
            shock_semantics="absolute",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        self.assertEqual(result["sensitivities"][0]["shock_value"], 2.5)

    def test_ratio_parameter_pp_shock_is_unchanged(self) -> None:
        data = model_document("capacity")
        test = build_sensitivity_test(
            parameter_id="capacity_utilization_base_2026", value=5,
            input_unit="pp", shock_semantics="additive",
        )
        data["sensitivity_tests"] = [test]
        result = run_forecast(data)
        sensitivity = result["sensitivities"][0]
        self.assertAlmostEqual(sensitivity["requested_values"]["down"], 0.75, places=12)
        self.assertAlmostEqual(sensitivity["requested_values"]["up"], 0.85, places=12)


class HelperContractTests(unittest.TestCase):
    """The shared helper itself, for paths the engine reaches only rarely."""

    @staticmethod
    def _helper():
        from research.input_quantities import validate_input_quantity_for_parameter

        return validate_input_quantity_for_parameter

    def test_unknown_parameter_currency_is_diagnosed_not_guessed(self) -> None:
        parameter = {
            "parameter_id": "p", "dimension": "revenue",
            "currency": "EUR", "scale": "million",
        }
        record = convert_input_quantity(5, input_unit="usd_million", engine_unit="usd_million")
        with self.assertRaisesRegex(ForecastInputError, "cannot be safely interpreted"):
            self._helper()(
                record, parameter=parameter, shock_type="absolute", field="t"
            )

    def test_unknown_parameter_scale_is_diagnosed_not_guessed(self) -> None:
        parameter = {
            "parameter_id": "p", "dimension": "revenue",
            "currency": "USD", "scale": "model-specific",
        }
        record = convert_input_quantity(5, input_unit="usd_million", engine_unit="usd_million")
        with self.assertRaisesRegex(ForecastInputError, "cannot be safely interpreted"):
            self._helper()(
                record, parameter=parameter, shock_type="absolute", field="t"
            )

    def test_matching_parameter_unit_passes_the_helper(self) -> None:
        parameter = {
            "parameter_id": "p", "dimension": "revenue",
            "currency": "HKD", "scale": "million",
        }
        record = convert_input_quantity(725, input_unit="hkd_million", engine_unit="hkd_million")
        expected = self._helper()(
            record, parameter=parameter, shock_type="absolute", field="t"
        )
        self.assertEqual(expected["engine_value"], 725.0)


if __name__ == "__main__":
    unittest.main()
