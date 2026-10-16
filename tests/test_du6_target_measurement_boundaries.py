"""DU6-RF-TARGET-MEASURES: signed management targets, one money description,
and an explicit comparison contract.

Covered boundaries (all hand-computed in
``tests/fixtures/du6_targets/hand_computed_expectations.json``):

* same-currency money scaling reuses the DU5 Currency x Scale description, so
  CNY and RMB are one currency while HKD/USD/RMB never mix without FX evidence;
* signed growth (negative single value, cross-zero range, ``level_multiple``
  below one) enters the normal typed flow at its own percent — a decline is
  never rewritten as a positive growth number, and a negative revenue amount
  is still refused;
* ``at_least`` / ``at_most`` / ``approximately`` / ``greater_than`` /
  ``less_than`` get a sign-safe tolerance band; strict comparisons stay strict;
* a two-ended range keeps both ends and never becomes a midpoint; operator x
  range combinations with no unambiguous meaning get a named diagnostic instead
  of a guess;
* ``attainment_ratio`` is withheld for non-positive point targets instead of
  flipping better/worse, without erasing any comparable observed value.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from research.target_measurement import (  # noqa: E402
    compare_target_measurement,
    normalize_target_bounds,
)
from test_management_targets import add_target  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


FIXTURE = json.loads(
    (ROOT / "tests" / "fixtures" / "du6_targets" / "hand_computed_expectations.json")
    .read_text(encoding="utf-8")
)


def expectation(identifier: str) -> dict:
    for key in ("money_scaling", "growth_normalization", "signed_comparison",
                "attainment_ratio", "yoy_derived"):
        for row in FIXTURE[key]:
            if row["id"] == identifier:
                return row
    raise AssertionError(f"unknown hand-computed expectation: {identifier}")


# --------------------------------------------------------------------------
# synthetic input construction on top of the existing native fixtures
# --------------------------------------------------------------------------


def _parameters(data: dict) -> dict:
    return {p["parameter_id"]: p for p in data["parameters"]}


SCENARIO_ORDER = ("low", "base", "high")


def set_scenario_growth(
    data: dict,
    growth_by_scenario: dict,
    company_levels: tuple[float, float, float] = (100.0, 200.0, 400.0),
) -> dict:
    """Reshape both segments so each scenario's company YoY growth is exact.

    ``company_levels`` fixes each scenario's FY2026 company revenue and keeps
    low <= base <= high for every year no matter which growth rates are asked
    for, so the truth table can order its observed values freely.
    """
    index = _parameters(data)
    for segment in data["segments"]:
        for scenario, growth in growth_by_scenario.items():
            ids = segment["scenarios"][scenario]["driver_parameter_ids"]["revenue"]
            start = company_levels[SCENARIO_ORDER.index(scenario)] / len(data["segments"])
            index[ids[0]]["value"] = start
            index[ids[1]]["value"] = start * (1 + growth)
    return data


def growth_document(
    *,
    raw_value=None,
    raw_value_low=None,
    raw_value_high=None,
    comparison_value=None,
    raw_ratio_basis: str = "percent",
    comparison: str = "at_least",
    tolerance: float = 0.01,
    base_period: str | None = "FY2026",
    treatment: str = "independent_benchmark",
    growth_by_scenario: dict | None = None,
    company_levels: tuple[float, float, float] = (100.0, 200.0, 400.0),
    target_id: str = "signed_growth_target",
):
    """A synthetic company whose typed management target is a YoY growth rate.

    ``comparison_value`` is the hand-normalized target (percent /100, fraction
    identity, level_multiple -1); it is supplied by the test, never derived from
    the code under test.
    """
    data = add_target(forecast_document(), target_value=1000, treatment=treatment)
    if growth_by_scenario:
        set_scenario_growth(data, growth_by_scenario, company_levels)
    target = data["management_targets"][0]
    is_range = raw_value_low is not None or raw_value_high is not None
    if raw_value is None and not is_range:
        raw_value = 0.0
        comparison_value = 0.0
    mapped = treatment in {"modeled_scenario", "scenario_boundary", "independent_benchmark"}
    target.update({
        "target_id": target_id,
        "statement": "Management guides FY2027 year over year revenue growth at the stated rate.",
        "metric_name": "revenue growth",
        "metric_definition": "year over year growth of consolidated recognized revenue",
        "target_period": "FY2027",
        "measurement_basis": "annual_period",
        "measurement_periods": ["FY2027"],
        "raw_unit": "percent",
        "raw_currency": "dimensionless",
        "raw_scale": "percent",
        "raw_value_kind": "numeric_range" if is_range else "numeric",
        "raw_target_value": None if is_range else raw_value,
        "raw_target_value_low": raw_value_low,
        "raw_target_value_high": raw_value_high,
        "comparison": comparison,
        "comparison_tolerance": tolerance,
        "comparison_value": None if is_range else comparison_value,
        "comparison_currency": None,
        "comparison_scale": None,
        "mapped_scenarios": ["low", "base", "high"] if mapped else [],
        "mapped_parameter_ids": [
            data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
        ] if mapped else [],
        "comparison_basis": {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": base_period,
            "raw_ratio_basis": raw_ratio_basis,
        },
    })
    if mapped:
        target["benchmark_rationale"] = "The stated growth rate is a benchmark, not an attained path."
        target["benchmark_claim_ids"] = ["benchmark_evidence"]
    claim = next(c for c in data["evidence_claims"] if c["claim_id"] in target["claim_ids"])
    claim.update(target_id=target_id, unit="percent", period="FY2027")
    if is_range:
        claim.pop("extracted_value", None)
    else:
        claim.update(extracted_value=raw_value)
    other = copy.deepcopy(claim)
    other.update(claim_id="benchmark_evidence", support_type="rationale_support")
    data["evidence_claims"].append(other)
    for record in data["management_communication_coverage"]:
        record["material_revenue_target_ids"] = [
            target_id if item == "five_year_revenue_goal" else item
            for item in record["material_revenue_target_ids"]
        ]
    return data


def money_target_document(
    *,
    raw_value,
    raw_currency: str,
    raw_scale: str,
    comparison_value,
    model_currency: str = "USD",
    model_unit: str = "million",
    comparison: str = "at_least",
    treatment: str = "independent_benchmark",
    target_id: str = "money_target",
):
    """A synthetic company with one typed annual revenue level target.

    ``comparison_value`` is the hand-converted target expressed in
    ``model_currency model_unit`` and is always written by the test itself.
    """
    data = add_target(forecast_document(), target_value=1000, treatment=treatment)
    data["currency"] = model_currency
    data["unit"] = model_unit
    index = _parameters(data)
    for parameter in data["parameters"]:
        if "currency" in parameter:
            parameter["currency"] = model_currency
            parameter["scale"] = model_unit
        if isinstance(parameter.get("unit"), str) and " " in parameter["unit"]:
            parameter["unit"] = f"{model_currency} {model_unit}"
        claim_id = f"claim_parameter_{parameter['parameter_id']}"
        for claim in data["evidence_claims"]:
            if claim["claim_id"] == claim_id and "unit" in claim:
                claim["unit"] = parameter["unit"]
    for record in data.get("historical_revenue", []):
        for claim in data["evidence_claims"]:
            if claim["claim_id"] == f"claim_history_{record['year']}":
                claim["unit"] = f"{model_currency} {model_unit}"
    target = data["management_targets"][0]
    target.update({
        "target_id": target_id,
        "raw_unit": f"{raw_currency} {raw_scale}",
        "raw_currency": raw_currency,
        "raw_scale": raw_scale,
        "raw_target_value": raw_value,
        "raw_value_kind": "numeric",
        "comparison": comparison,
        "comparison_value": comparison_value,
        "comparison_basis": {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "annual_revenue_level",
            "period": "FY2027",
        },
        "mapped_scenarios": ["low", "base", "high"],
        "mapped_parameter_ids": [index[
            data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
        ]["parameter_id"]],
        "benchmark_rationale": "A level benchmark kept independent of the scenario paths.",
        "benchmark_claim_ids": ["benchmark_evidence"],
    })
    claim = next(c for c in data["evidence_claims"] if c["claim_id"] in target["claim_ids"])
    claim.update(target_id=target_id, extracted_value=raw_value,
                 unit=f"{raw_currency} {raw_scale}")
    other = copy.deepcopy(claim)
    other.update(claim_id="benchmark_evidence", support_type="rationale_support")
    data["evidence_claims"].append(other)
    for record in data["management_communication_coverage"]:
        record["material_revenue_target_ids"] = [
            target_id if item == "five_year_revenue_goal" else item
            for item in record["material_revenue_target_ids"]
        ]
    return data


# --------------------------------------------------------------------------
# 1. shared money description (one Currency x Scale table)
# --------------------------------------------------------------------------


class SharedMoneyDescriptionTests(unittest.TestCase):
    """API RED until B implements the shared lookups on the DU5 description."""

    @staticmethod
    def _shared():
        from research.input_quantities import (
            money_currency,
            money_scale_factor,
            same_money_currency,
        )

        return money_currency, money_scale_factor, same_money_currency

    def test_scale_aliases_cover_both_vocabularies(self) -> None:
        _, money_scale_factor, _ = self._shared()
        for spelling, factor in (
            ("unit", 1.0), ("units", 1.0), ("元", 1.0),
            ("thousand", 1e3), ("千", 1e3),
            ("10k", 1e4), ("wan", 1e4), ("万", 1e4), ("万元", 1e4),
            ("million", 1e6), ("百万", 1e6),
            ("100m", 1e8), ("yi", 1e8), ("亿", 1e8), ("亿元", 1e8),
            ("billion", 1e9), ("十亿", 1e9),
            ("trillion", 1e12), ("万亿", 1e12),
        ):
            with self.subTest(scale=spelling):
                self.assertEqual(money_scale_factor(spelling), factor)
        self.assertIsNone(money_scale_factor("mega"))
        self.assertIsNone(money_scale_factor(None))

    def test_cny_and_rmb_are_one_currency(self) -> None:
        money_currency, _, same_money_currency = self._shared()
        self.assertEqual(money_currency("CNY"), "rmb")
        self.assertEqual(money_currency("cny"), "rmb")
        self.assertEqual(money_currency("RMB"), "rmb")
        self.assertEqual(money_currency("USD"), "usd")
        self.assertEqual(money_currency("HKD"), "hkd")
        self.assertIsNone(money_currency("EUR"))
        self.assertIsNone(money_currency(None))
        self.assertTrue(same_money_currency("CNY", "RMB"))
        self.assertTrue(same_money_currency("rmb", "cny"))
        self.assertFalse(same_money_currency("HKD", "USD"))
        self.assertFalse(same_money_currency("CNY", "HKD"))
        self.assertFalse(same_money_currency("EUR", "EUR"))

    def test_du5_unknown_spelling_rule_is_unchanged(self) -> None:
        """Adding target scale aliases must not make a bare 万元 guessable."""
        from research.input_quantities import convert_input_quantity

        for spelling in ("万元", "wan", "wan_yuan", "亿", "yi", "百万", "trillion"):
            with self.subTest(spelling=spelling):
                with self.assertRaises(ForecastInputError):
                    convert_input_quantity(5, input_unit=spelling, engine_unit="rmb_10k")


# --------------------------------------------------------------------------
# 2. normalize_target_bounds: one money description, signed growth
# --------------------------------------------------------------------------


def level_target(*, raw_value, raw_currency, raw_scale, low=None, high=None) -> dict:
    target = {
        "comparison_basis": {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "annual_revenue_level",
            "period": "FY2027",
        },
        "raw_unit": f"{raw_currency} {raw_scale}",
        "raw_currency": raw_currency,
        "raw_scale": raw_scale,
    }
    if raw_value is None:
        target["raw_target_value_low"] = low
        target["raw_target_value_high"] = high
    else:
        target["raw_target_value"] = raw_value
    return target


class NormalizeTargetBoundsTests(unittest.TestCase):
    def test_hkd_wan_yi_baiwan_scales_convert_by_hand(self) -> None:
        for identifier, scale in (
            ("hk_wan_to_million", "万"),
            ("hk_yi_to_million", "亿"),
            ("hk_baiwan_identity", "百万"),
        ):
            case = expectation(identifier)
            with self.subTest(scale=scale):
                low, high = normalize_target_bounds(
                    level_target(
                        raw_value=case["input_value"],
                        raw_currency=case["input_currency"],
                        raw_scale=case["input_scale"],
                    ),
                    {"currency": case["target_unit_currency"], "unit": case["target_unit_scale"]},
                )
                self.assertEqual(low, case["expected"])
                self.assertEqual(high, case["expected"])

    def test_cny_target_is_the_same_currency_as_an_rmb_model(self) -> None:
        for identifier in ("cny_yiyuan_same_currency_rmb_model", "cny_wanyuan_to_rmb_100m"):
            case = expectation(identifier)
            with self.subTest(case=identifier):
                low, _ = normalize_target_bounds(
                    level_target(
                        raw_value=case["input_value"],
                        raw_currency=case["input_currency"],
                        raw_scale=case["input_scale"],
                    ),
                    {"currency": case["target_unit_currency"], "unit": case["target_unit_scale"]},
                )
                self.assertEqual(low, case["expected"])

    def test_same_currency_scale_conversion_runs_in_both_directions(self) -> None:
        for identifier in ("cny_wanyuan_to_rmb_100m", "cny_100m_to_rmb_wanyuan_reverse"):
            case = expectation(identifier)
            with self.subTest(case=identifier):
                low, high = normalize_target_bounds(
                    level_target(
                        raw_value=case["input_value"],
                        raw_currency=case["input_currency"],
                        raw_scale=case["input_scale"],
                    ),
                    {"currency": case["target_unit_currency"], "unit": case["target_unit_scale"]},
                )
                self.assertEqual(low, pytest.approx(case["expected"]))
                self.assertEqual(high, pytest.approx(case["expected"]))

    def test_inverted_range_bounds_are_refused(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "inverted"):
            normalize_target_bounds(
                level_target(raw_value=None, raw_currency="USD", raw_scale="million",
                             low=10.0, high=5.0),
                {"currency": "USD", "unit": "million"},
            )
        with self.assertRaisesRegex(ForecastInputError, "inverted"):
            normalize_target_bounds(
                {
                    "comparison_basis": {
                        "schema_version": "management-target-comparison/1",
                        "metric_kind": "year_over_year_growth",
                        "period": "FY2027",
                        "base_period": "FY2026",
                        "raw_ratio_basis": "percent",
                    },
                    "raw_target_value_low": 5.0,
                    "raw_target_value_high": -10.0,
                },
                {"currency": "USD", "unit": "million"},
            )

    def test_trillion_scale_is_still_accepted(self) -> None:
        case = expectation("trillion_to_billion")
        low, _ = normalize_target_bounds(
            level_target(raw_value=3.0, raw_currency="USD", raw_scale="trillion"),
            {"currency": "USD", "unit": "billion"},
        )
        self.assertEqual(low, case["expected"])

    def test_cross_currency_without_fx_evidence_is_still_refused(self) -> None:
        for raw_currency, model_currency in (
            ("HKD", "USD"), ("USD", "HKD"), ("CNY", "HKD"), ("HKD", "RMB"), ("USD", "RMB"),
        ):
            with self.subTest(target=raw_currency, model=model_currency):
                with self.assertRaisesRegex(ForecastInputError, "currency"):
                    normalize_target_bounds(
                        level_target(raw_value=100, raw_currency=raw_currency, raw_scale="million"),
                        {"currency": model_currency, "unit": "million"},
                    )

    def test_unknown_currency_and_wrong_unit_family_are_refused(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "currency"):
            normalize_target_bounds(
                level_target(raw_value=100, raw_currency="EUR", raw_scale="million"),
                {"currency": "USD", "unit": "million"},
            )
        for bad_scale in ("ratio", "percent", "million_units", "mega"):
            with self.subTest(scale=bad_scale):
                with self.assertRaisesRegex(ForecastInputError, "scale"):
                    normalize_target_bounds(
                        level_target(raw_value=100, raw_currency="USD", raw_scale=bad_scale),
                        {"currency": "USD", "unit": "million"},
                    )

    def test_growth_normalization_is_sign_preserving(self) -> None:
        for identifier in (
            "level_multiple_point_0_9",
            "level_multiple_range_cross_zero",
            "percent_negative_point",
            "percent_cross_zero_range",
            "fraction_negative_point",
        ):
            case = expectation(identifier)
            target = {
                "comparison_basis": {
                    "schema_version": "management-target-comparison/1",
                    "metric_kind": "year_over_year_growth",
                    "period": "FY2027",
                    "base_period": "FY2026",
                    "raw_ratio_basis": case["raw_ratio_basis"],
                },
            }
            if "raw_value" in case:
                target["raw_target_value"] = case["raw_value"]
            else:
                target["raw_target_value_low"] = case["raw_value_low"]
                target["raw_target_value_high"] = case["raw_value_high"]
            with self.subTest(case=identifier):
                low, high = normalize_target_bounds(target, {"currency": "USD", "unit": "million"})
                self.assertEqual(low, pytest.approx(case["expected_low"]))
                self.assertEqual(high, pytest.approx(case["expected_high"]))


# --------------------------------------------------------------------------
# 3. signed comparison truth table
# --------------------------------------------------------------------------


class SignedComparisonTruthTableTests(unittest.TestCase):
    """compare_target_measurement over a real native forecast result."""

    @staticmethod
    def _rows(target, result):
        return compare_target_measurement(target, result)

    def _growth_result(self, growth_by_scenario, company_levels=(100.0, 200.0, 400.0)):
        data = growth_document(growth_by_scenario=growth_by_scenario,
                               company_levels=company_levels)
        return run_forecast(data)

    def _target(self, *, comparison, low, high, tolerance=0.01):
        target = {
            "target_id": "signed_growth_target",
            "treatment": "independent_benchmark",
            "comparison": comparison,
            "comparison_tolerance": tolerance,
            "scope": {"type": "company", "name": "company"},
            "mapped_scenarios": ["low", "base", "high"],
            "comparison_basis": {
                "schema_version": "management-target-comparison/1",
                "metric_kind": "year_over_year_growth",
                "period": "FY2027",
                "base_period": "FY2026",
                "raw_ratio_basis": "fraction",
            },
        }
        if low == high:
            target["raw_target_value"] = low
        else:
            target["raw_target_value_low"] = low
            target["raw_target_value_high"] = high
        return target

    def test_point_tolerance_widens_away_from_zero_for_negative_targets(self) -> None:
        result = self._growth_result({"low": -0.0995, "base": -0.102, "high": -0.20})
        target = self._target(comparison="at_least", low=-0.10, high=-0.10, tolerance=0.01)
        rows = self._rows(target, result)
        self.assertTrue(rows["low"]["meets_target"], expectation(
            "at_least_negative_point_tolerance_widens_downward"))
        self.assertFalse(rows["base"]["meets_target"])
        self.assertFalse(rows["high"]["meets_target"])
        self.assertEqual(rows["low"]["attainment_ratio"], None)

    def test_at_most_negative_point_widens_upward(self) -> None:
        result = self._growth_result({"low": -0.0995, "base": -0.095, "high": -0.20})
        target = self._target(comparison="at_most", low=-0.10, high=-0.10, tolerance=0.01)
        rows = self._rows(target, result)
        self.assertTrue(rows["low"]["meets_target"])
        self.assertFalse(rows["base"]["meets_target"])
        self.assertTrue(rows["high"]["meets_target"])

    def test_positive_point_tolerance_is_byte_identical_to_the_legacy_band(self) -> None:
        case = expectation("at_least_positive_point_unchanged")
        result = self._growth_result({"low": 0.0995, "base": 0.0985, "high": 0.20})
        target = self._target(comparison="at_least", low=0.10, high=0.10, tolerance=0.01)
        rows = self._rows(target, result)
        self.assertEqual(rows["low"]["meets_target"], case["cases"][0]["expected_meets"])
        self.assertEqual(rows["base"]["meets_target"], case["cases"][1]["expected_meets"])

    def test_approximately_cross_zero_range_keeps_both_ends(self) -> None:
        expectation("approximately_cross_zero_range")
        result = self._growth_result({"low": 0.0, "base": -0.11, "high": 0.06})
        target = self._target(comparison="approximately", low=-0.10, high=0.05)
        rows = self._rows(target, result)
        self.assertTrue(rows["low"]["meets_target"])
        self.assertFalse(rows["base"]["meets_target"])
        self.assertFalse(rows["high"]["meets_target"])
        for row in rows.values():
            self.assertEqual(row["target_low"], -0.10)
            self.assertEqual(row["target_high"], 0.05)
            self.assertEqual(row["target_value"], None)
            self.assertEqual(row["attainment_ratio"], None)

    def test_strict_comparisons_stay_strict_for_negative_points(self) -> None:
        # -1/8, -1/16 and -1/4 are exact binary fractions, so the observed
        # growth lands exactly on the target and the strict bound is testable.
        result = self._growth_result({"low": -0.125, "base": -0.0625, "high": -0.25})
        greater = self._rows(self._target(comparison="greater_than", low=-0.125, high=-0.125), result)
        self.assertFalse(greater["low"]["meets_target"])
        self.assertTrue(greater["base"]["meets_target"])
        self.assertFalse(greater["high"]["meets_target"])
        less = self._rows(self._target(comparison="less_than", low=-0.125, high=-0.125), result)
        self.assertFalse(less["low"]["meets_target"])
        self.assertFalse(less["base"]["meets_target"])
        self.assertTrue(less["high"]["meets_target"])

    def test_zero_target_band_does_not_widen(self) -> None:
        result = self._growth_result({"low": 0.0, "base": -0.5, "high": 0.2})
        rows = self._rows(self._target(comparison="at_least", low=0.0, high=0.0), result)
        self.assertTrue(rows["low"]["meets_target"])
        self.assertFalse(rows["base"]["meets_target"])

    def test_operator_on_a_two_ended_range_is_a_named_diagnostic(self) -> None:
        result = self._growth_result({"low": 0.0, "base": 0.1, "high": 0.2})
        for comparison in ("at_least", "at_most", "greater_than", "less_than"):
            with self.subTest(comparison=comparison):
                with self.assertRaisesRegex(
                    ForecastInputError, "typed_comparison_operator_range_incompatible"
                ):
                    self._rows(self._target(comparison=comparison, low=-0.10, high=0.05), result)

    def test_attainment_ratio_is_withheld_only_where_it_would_mislead(self) -> None:
        for identifier in (
            "negative_point_is_withheld",
            "zero_point_is_withheld",
            "positive_point_unchanged",
        ):
            case = expectation(identifier)
            with self.subTest(case=identifier):
                result = self._growth_result({
                    "low": case["observed"], "base": case["observed"], "high": case["observed"],
                })
                rows = self._rows(
                    self._target(comparison="approximately", low=case["target"], high=case["target"]),
                    result,
                )
                if case["expected_ratio"] is None:
                    self.assertEqual(rows["low"]["attainment_ratio"], None)
                else:
                    self.assertEqual(rows["low"]["attainment_ratio"],
                                     pytest.approx(case["expected_ratio"]))
                self.assertIsNotNone(rows["low"]["modeled_value"])
                self.assertIsNotNone(rows["low"]["meets_target"])

    def test_yoy_difference_pp_and_derived_benchmark_stay_comparable(self) -> None:
        case = expectation("negative_growth_difference_pp_and_benchmark")
        result = self._growth_result({
            "low": case["expected_observed"], "base": case["expected_observed"],
            "high": case["expected_observed"],
        }, company_levels=(200.0, 300.0, 400.0))
        rows = self._rows(self._target(comparison="approximately", low=case["target_growth"],
                                       high=case["target_growth"]), result)
        row = rows["low"]
        self.assertEqual(row["modeled_value"], pytest.approx(case["expected_observed"]))
        self.assertEqual(row["difference_percentage_points"],
                         pytest.approx(case["expected_difference_percentage_points"]))
        self.assertEqual(row["derived_revenue_benchmark"]["value"],
                         pytest.approx(case["expected_derived_revenue_benchmark"]))
        self.assertEqual(row["derived_revenue_benchmark"]["difference"],
                         pytest.approx(case["expected_benchmark_difference"]))
        self.assertEqual(row["attainment_ratio"], None)


# --------------------------------------------------------------------------
# 4. engine entry points
# --------------------------------------------------------------------------


class EngineEntryTests(unittest.TestCase):
    def test_negative_growth_target_enters_the_engine_at_its_own_percent(self) -> None:
        data = growth_document(raw_value=-10.0, comparison_value=-0.10, comparison="approximately",
                               growth_by_scenario={"low": -0.20, "base": -0.10, "high": 0.20})
        result = run_forecast(data)
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        self.assertEqual(rows["base"]["modeled_value"], pytest.approx(-0.10))
        self.assertTrue(rows["base"]["meets_target"])
        self.assertEqual(rows["low"]["modeled_value"], pytest.approx(-0.20))
        self.assertFalse(rows["low"]["meets_target"])
        self.assertEqual(rows["low"]["attainment_ratio"], None)
        self.assertEqual(rows["low"]["difference_percentage_points"], pytest.approx(-10.0))

    def test_level_multiple_below_one_is_a_decline_not_a_positive_growth(self) -> None:
        data = growth_document(raw_value=0.9, comparison_value=-0.10, raw_ratio_basis="level_multiple",
                               comparison="approximately",
                               growth_by_scenario={"low": -0.20, "base": -0.10, "high": 0.20})
        result = run_forecast(data)
        target = result["management_target_coverage"]["targets"][0]
        rows = target["scenario_comparison"]
        self.assertEqual(rows["base"]["target_value"], pytest.approx(-0.10))
        self.assertTrue(rows["base"]["meets_target"])
        self.assertEqual(target["raw_target_value"], 0.9)

    def test_cross_zero_range_enters_and_compares_without_a_midpoint(self) -> None:
        data = growth_document(raw_value_low=-10.0, raw_value_high=5.0,
                               comparison="approximately",
                               growth_by_scenario={"low": -0.20, "base": -0.02, "high": 0.20})
        result = run_forecast(data)
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        self.assertEqual(rows["base"]["target_low"], pytest.approx(-0.10))
        self.assertEqual(rows["base"]["target_high"], pytest.approx(0.05))
        self.assertEqual(rows["base"]["target_value"], None)
        self.assertTrue(rows["base"]["meets_target"])
        self.assertFalse(rows["low"]["meets_target"])
        self.assertEqual(rows["base"]["attainment_ratio"], None)

    def test_negative_revenue_amount_is_still_refused(self) -> None:
        data = money_target_document(raw_value=-100, comparison_value=-100,
                                     raw_currency="USD", raw_scale="million")
        with self.assertRaisesRegex(ForecastInputError, "cannot be negative"):
            run_forecast(data)

    def test_negative_growth_range_lower_bound_is_not_an_amount(self) -> None:
        data = growth_document(raw_value_low=-10.0, raw_value_high=5.0,
                               comparison="approximately", treatment="unmodeled_data_gap")
        run_forecast(data)

    def test_unknown_base_period_stays_a_named_reason(self) -> None:
        data = growth_document(raw_value=-10.0, comparison_value=-0.10, comparison="approximately",
                               base_period=None,
                               growth_by_scenario={"low": -0.20, "base": -0.10, "high": 0.20})
        result = run_forecast(data)
        target = result["management_target_coverage"]["targets"][0]
        self.assertEqual(target["comparison_status"], "not_comparable")
        self.assertEqual(target["comparison_reason"], "base_period_unknown")
        for row in target["scenario_comparison"].values():
            self.assertEqual(row["reason"], "missing_base_period")
            self.assertEqual(row["meets_target"], None)

    def test_operator_on_a_two_ended_range_is_refused_before_any_comparison(self) -> None:
        for comparison in ("at_least", "at_most", "greater_than", "less_than"):
            data = growth_document(raw_value_low=-10.0, raw_value_high=5.0, comparison=comparison)
            with self.subTest(comparison=comparison):
                with self.assertRaisesRegex(
                    ForecastInputError, "typed_comparison_operator_range_incompatible"
                ):
                    run_forecast(data)

    def test_unmodeled_operator_range_is_preserved_with_the_named_reason(self) -> None:
        data = growth_document(raw_value_low=-10.0, raw_value_high=5.0, comparison="at_least",
                               treatment="unmodeled_data_gap")
        result = run_forecast(data)
        target = result["management_target_coverage"]["targets"][0]
        self.assertEqual(target["comparison_reason"], "operator_range_incompatible")
        self.assertEqual(target["comparison_status"], "not_comparable")
        self.assertEqual(target["scenario_comparison"], {})

    def test_zero_base_revenue_stays_a_nonpositive_base_reason(self) -> None:
        data = growth_document(raw_value=-10.0, comparison_value=-0.10, comparison="approximately",
                               growth_by_scenario={"low": -0.10, "base": -0.10, "high": -0.10})
        for parameter in data["parameters"]:
            if parameter["period"] == "FY2026" and parameter["dimension"] == "revenue":
                parameter["value"] = 0.0
        result = run_forecast(data)
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        for row in rows.values():
            self.assertEqual(row["base_value"], 0)
            self.assertEqual(row["reason"], "nonpositive_base_revenue")
            self.assertEqual(row["modeled_value"], None)
            self.assertEqual(row["meets_target"], None)

    def test_original_scope_quarter_and_schema_rejections_are_preserved(self) -> None:
        data = growth_document(raw_value=-10.0, comparison_value=-0.10, comparison="approximately")
        data["management_targets"][0]["scope"] = {"type": "segment", "name": "Segment Z"}
        with self.assertRaisesRegex(ForecastInputError, "unknown management target segment"):
            run_forecast(data)

        data = growth_document(raw_value=-10.0, comparison_value=-0.10, comparison="approximately")
        data["management_targets"][0]["comparison_basis"]["schema_version"] = "management-target-comparison/2"
        with self.assertRaisesRegex(ForecastInputError, "unsupported typed management comparison"):
            run_forecast(data)

        data = growth_document(raw_value=-10.0, comparison_value=-0.10, comparison="approximately")
        spec = data["management_targets"][0]["comparison_basis"]
        spec["metric_kind"] = "quarterly_revenue_level"
        spec["period"] = "FY2027Q3"
        data["management_targets"][0]["measurement_basis"] = "quarterly_period"
        with self.assertRaises(ForecastInputError):
            run_forecast(data)

    def test_cny_target_on_an_rmb_model_runs_end_to_end(self) -> None:
        data = money_target_document(raw_value=500, comparison_value=500, raw_currency="CNY",
                                     raw_scale="亿元", model_currency="RMB", model_unit="亿元")
        result = run_forecast(data)
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        for row in rows.values():
            self.assertEqual(row["unit"], "RMB 亿元")

    def test_hkd_target_scale_aliases_normalize_against_the_model_unit(self) -> None:
        data = money_target_document(raw_value=72500, comparison_value=725, raw_currency="HKD",
                                     raw_scale="万", model_currency="HKD", model_unit="million")
        result = run_forecast(data)
        rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
        for row in rows.values():
            self.assertEqual(row["target_value"], pytest.approx(725.0))

    def test_cross_currency_target_is_refused_by_the_engine(self) -> None:
        data = money_target_document(raw_value=100, comparison_value=100, raw_currency="HKD",
                                     raw_scale="million", model_currency="USD", model_unit="million")
        with self.assertRaisesRegex(ForecastInputError, "currency"):
            run_forecast(data)

    def test_wrong_unit_family_on_a_money_target_is_refused(self) -> None:
        data = money_target_document(raw_value=100, comparison_value=100, raw_currency="USD",
                                     raw_scale="ratio", model_currency="USD", model_unit="million")
        with self.assertRaisesRegex(ForecastInputError, "scale"):
            run_forecast(data)


# --------------------------------------------------------------------------
# 5. typed builder: no hand-patching of the target dictionary
# --------------------------------------------------------------------------


class TypedBuilderTests(unittest.TestCase):
    def _kwargs(self, **overrides) -> dict:
        kwargs = dict(
            statement="Management guides FY2027 revenue growth of about negative ten percent.",
            target_id="t_signed_growth",
            metric_name="revenue growth",
            metric_definition="year over year growth of consolidated recognized revenue",
            source_id="filing",
            locator="Guidance section",
            excerpt="Management guides FY2027 revenue growth of about negative ten percent.",
            verified_by="du6-test",
            verified_date="2026-10-16",
            raw_unit="percent",
            raw_currency="dimensionless",
            raw_scale="percent",
            period_label="FY2027",
            measurement_basis="annual_period",
            measurement_periods=["FY2027"],
            target_period="FY2027",
            rationale="Signed growth guidance recorded at its own percent.",
            measurement_rationale="The statement is an annual growth rate.",
            normalization_rationale="The stated rate is already an annual YoY growth ratio; only its sign and ratio basis are normalized.",
            perimeter_notes="Company recognized revenue.",
            comparison="approximately",
        )
        kwargs.update(overrides)
        return kwargs

    def _build(self, **overrides):
        from research.input_targets import build_management_target

        kwargs = self._kwargs(**overrides)
        statement = kwargs.pop("statement")
        return build_management_target(statement, **kwargs)

    def test_default_call_shape_is_unchanged_for_a_positive_amount(self) -> None:
        built = self._build(raw_value=144.0, raw_unit="USD million", raw_currency="USD",
                            raw_scale="million", statement="Reach USD 144 million.")
        self.assertEqual(built["target"]["raw_target_value"], 144.0)
        self.assertNotIn("comparison_basis", built["target"])
        self.assertNotIn("comparison_value", built["target"])

    def test_signed_growth_is_accepted_only_with_a_growth_comparison_spec(self) -> None:
        spec = {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": "FY2026",
            "raw_ratio_basis": "percent",
        }
        built = self._build(raw_value=-10.0, comparison_spec=spec, treatment="independent_benchmark")
        self.assertEqual(built["target"]["comparison_basis"], spec)
        self.assertEqual(built["target"]["comparison_value"], pytest.approx(-0.10))
        self.assertEqual(built["target"]["raw_target_value"], -10.0)

    def test_negative_revenue_amount_is_still_refused_by_the_builder(self) -> None:
        spec = {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "annual_revenue_level",
            "period": "FY2027",
        }
        with self.assertRaisesRegex(ForecastInputError, "cannot be negative"):
            self._build(raw_value=-10.0, raw_unit="USD million", raw_currency="USD",
                        raw_scale="million", comparison_currency="USD",
                        comparison_scale="million", comparison_spec=spec,
                        statement="Reach negative USD 10 million.")
        with self.assertRaisesRegex(ForecastInputError, "cannot be negative"):
            self._build(raw_value=-10.0)

    def test_level_multiple_spec_normalizes_to_a_signed_growth(self) -> None:
        spec = {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": "FY2026",
            "raw_ratio_basis": "level_multiple",
        }
        built = self._build(raw_value=0.9, comparison_spec=spec, treatment="independent_benchmark")
        self.assertEqual(built["target"]["comparison_value"], pytest.approx(-0.10))

    def test_range_spec_carries_both_ends_and_no_point_value(self) -> None:
        spec = {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": "FY2026",
            "raw_ratio_basis": "percent",
        }
        built = self._build(raw_value=None, raw_value_low=-10.0, raw_value_high=5.0,
                            comparison_spec=spec)
        self.assertEqual(built["target"]["comparison_value"], None)
        self.assertEqual(built["target"]["raw_target_value_low"], -10.0)
        self.assertEqual(built["target"]["raw_target_value_high"], 5.0)

    def test_comparison_spec_conflicts_with_a_conversion_are_named(self) -> None:
        spec = {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": "FY2026",
            "raw_ratio_basis": "percent",
        }
        conversion = {
            "comparison_basis": "annual_recognized_revenue",
            "parameter_ids": ["p1"],
            "formula": "x0 * x1",
            "parameter_values": [1.0],
        }
        with self.assertRaisesRegex(ForecastInputError, "typed_comparison_spec_conflicts_with_conversion"):
            self._build(raw_value=-10.0, comparison_spec=spec, conversion=conversion)

    def test_builder_output_needs_no_hand_patch_to_validate(self) -> None:
        spec = {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": "FY2026",
            "raw_ratio_basis": "percent",
        }
        built = self._build(raw_value=-10.0, comparison_spec=spec, treatment="independent_benchmark")
        data = growth_document(raw_value=-10.0, comparison_value=-0.10, comparison="approximately",
                               growth_by_scenario={"low": -0.20, "base": -0.10, "high": 0.20})
        data["evidence_claims"].extend(built["claims"])
        target = built["target"]
        target.update(treatment="independent_benchmark",
                      mapped_scenarios=["low", "base", "high"],
                      mapped_parameter_ids=[data["segments"][0]["scenarios"]["base"]
                                            ["driver_parameter_ids"]["revenue"][-1]],
                      benchmark_rationale="Independent benchmark rationale.",
                      benchmark_claim_ids=["benchmark_evidence"])
        claim = next(c for c in data["evidence_claims"] if c["claim_id"] == "claim_t_signed_growth")
        claim.update(source_id="filing", content_sha256="a" * 64,
                     capture_receipt_sha256=data["sources"][0]["capture"]["receipt_sha256"])
        for extra in data["evidence_claims"]:
            if extra["claim_id"] == "benchmark_evidence":
                extra.update(target_id="t_signed_growth")
        data["management_targets"] = [target]
        for record in data["management_communication_coverage"]:
            if record["material_revenue_target_ids"]:
                record["material_revenue_target_ids"] = ["t_signed_growth"]
        result = run_forecast(data)
        self.assertEqual(
            result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]
            ["target_value"],
            pytest.approx(-0.10),
        )


if __name__ == "__main__":
    unittest.main()
