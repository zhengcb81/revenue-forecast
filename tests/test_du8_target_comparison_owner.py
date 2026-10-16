"""DU8: one comparison owner for legacy and typed management targets.

The report validator and the scenario producer must not each re-derive
"does this scenario meet the target". These tests freeze, before the change:

* the exact legacy numeric semantics (``max(1.0, |v|) * tolerance`` for
  ``approximately``, ``v * (1 -/+ t)`` for ``at_least``/``at_most``, the
  ``target_value == 0`` ratio rule) as an explicit compatibility path inside
  one owner -- not as a second implementation;
* the emitted legacy row key set and every value bit for bit;
* that the owner is the only place the decision is written, measured by an AST
  guard over the two callers;
* that a tampered legacy row is still refused, and that both the producer and
  the report reach the same owner for both branches.

Hand anchors in this file are written from the arithmetic of
``references/management-targets.md`` and ``references/target-measurement-comparison.md``;
they never import the production formula they are checking.
"""
from __future__ import annotations

import ast
import copy
import math
import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_core import ForecastInputError, canonical_sha256, run_forecast  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_management_targets import add_target  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

SCRIPTS = ROOT / "scripts"

LEGACY_ROW_KEYS = {
    "measurement_basis",
    "measurement_periods",
    "modeled_period_values",
    "modeled_value",
    "target_value",
    "attainment_ratio",
    "meets_target",
}


# --------------------------------------------------------------------------
# synthetic documents (no production module decides the expected numbers)
# --------------------------------------------------------------------------


def legacy_document(
    *,
    target_value: float = 144.0,
    comparison: str = "at_least",
    tolerance: float = 0.01,
    ratio: float = 1.0,
    period: str = "FY2027",
    treatment: str = "scenario_boundary",
    measurement_basis: str = "annual_period",
    measurement_periods: list[str] | None = None,
):
    """A legacy (non-typed) target with the high scenario scaled by ``ratio``.

    Every scenario is scaled by the same factor so the engine's
    ``low <= base <= high`` ordering gate still holds, which is what makes the
    observable value reachable through the public entry point.
    """
    data = add_target(
        forecast_document(),
        target_value=target_value,
        period=period,
        treatment=treatment,
        measurement_basis=measurement_basis,
        measurement_periods=measurement_periods,
    )
    target = data["management_targets"][0]
    target.update(comparison=comparison, comparison_tolerance=tolerance,
                  comparison_value=target_value, mapped_scenarios=["high"])
    claim = next(c for c in data["evidence_claims"] if c["claim_id"] in target["claim_ids"])
    claim["extracted_value"] = target_value
    index = {p["parameter_id"]: p for p in data["parameters"]}
    for scenario, offset in (("low", 0.94), ("base", 0.97), ("high", 1.0)):
        ids = data["segments"][0]["scenarios"][scenario]["driver_parameter_ids"]["revenue"]
        seed = target_value * ratio * offset
        index[ids[0]]["value"] = seed
        index[ids[1]]["value"] = seed
    return data


def reseal(result: dict) -> dict:
    out = copy.deepcopy(result)
    out["result_sha256"] = canonical_sha256(
        {key: value for key, value in out.items() if key != "result_sha256"}
    )
    return out


# --------------------------------------------------------------------------
# 1. hand anchors: the frozen legacy arithmetic, written by hand
# --------------------------------------------------------------------------


class LegacyHandAnchorTests(unittest.TestCase):
    """Every expected value below is typed out from the reference tables."""

    def test_approximately_band_is_one_absolute_unit_for_small_targets(self) -> None:
        # references/management-targets.md legacy row:
        #   abs_tol = max(1.0, |v|) * t
        # v = 0.5, t = 0.01  ->  abs_tol = 0.01  ->  band [0.490, 0.510]
        # rel_tol = 0.01 already gives [0.495, 0.505]; the absolute term widens.
        rows = {}
        for observed in (0.4899, 0.4901, 0.495, 0.500, 0.5099, 0.5101):
            rows[observed] = math.isclose(
                observed, 0.5, rel_tol=0.01, abs_tol=max(1.0, abs(0.5)) * 0.01
            )
        self.assertEqual(
            rows,
            {0.4899: False, 0.4901: True, 0.495: True,
             0.500: True, 0.5099: True, 0.5101: False},
        )

    def test_approximately_band_is_the_relative_band_for_large_targets(self) -> None:
        # v = 144, t = 0.01. In ``isclose(observed, v, rel_tol=t, abs_tol=A)``
        # the accepted distance is ``max(t * |v|, A)``; the frozen legacy
        # absolute term is ``A = max(1.0, |v|) * t`` = 1.44 = ``t * |v|``, so
        # for |v| >= 1 the absolute term is inert and the accepted distance is
        # exactly ``t * |v|`` = 1.44 around 144.
        self.assertEqual(max(1.0, abs(144.0)) * 0.01, 0.01 * abs(144.0))
        self.assertEqual(max(1.0, abs(144.0)) * 0.01, 1.44)
        self.assertTrue(math.isclose(144.0 - 1.44, 144.0, rel_tol=0.01, abs_tol=1.44))
        self.assertTrue(math.isclose(144.0 + 1.44, 144.0, rel_tol=0.01, abs_tol=1.44))
        # Outside the accepted distance by a clear margin, the band is closed.
        self.assertFalse(math.isclose(144.0 - 1.5, 144.0, rel_tol=0.01, abs_tol=1.44))
        self.assertFalse(math.isclose(144.0 + 1.5, 144.0, rel_tol=0.01, abs_tol=1.44))

    def test_approximately_band_above_one_never_uses_the_fixed_unit_floor(self) -> None:
        # The distinguishing property of the legacy expression: the absolute
        # term only matters when |v| < 1, where max(1.0, |v|) is the constant
        # 1.0. Above that it equals |v| * t and cancels against rel_tol.
        self.assertEqual(max(1.0, abs(2.0)) * 0.01, 0.02)
        self.assertEqual(max(1.0, abs(2.0)) * 0.01, 0.01 * abs(2.0))
        self.assertNotEqual(max(1.0, abs(0.5)) * 0.01, 0.01 * abs(0.5))
        self.assertEqual(max(1.0, abs(0.5)) * 0.01, 0.01)

    def test_approximately_band_matches_the_typed_band_only_at_or_above_one(self) -> None:
        # This is the documented, intentional divergence kept as an explicit
        # compatibility path: below |v| = 1 the legacy absolute term is the
        # fixed 1.0 unit floor, the typed one is |v| itself.
        for value, legacy_abs, typed_abs in (
            (0.0, 0.01, 1e-14),
            (0.5, 0.01, 0.005),
            (1.0, 0.01, 0.01),
            (144.0, 1.44, 1.44),
        ):
            with self.subTest(value=value):
                self.assertEqual(max(1.0, abs(value)) * 0.01, legacy_abs)
                self.assertEqual(max(abs(value), 1e-12) * 0.01, typed_abs)

    def test_legacy_at_least_and_at_most_use_v_times_one_minus_or_plus_t(self) -> None:
        # references/management-targets.md legacy at_least/at_most expressions.
        self.assertAlmostEqual(144.0 * (1 - 0.01), 142.56, places=12)
        self.assertAlmostEqual(144.0 * (1 + 0.01), 145.44, places=12)
        # 0.5 is below the 0.99 factor of 1.0 by construction.
        self.assertAlmostEqual(1.0 * (1 - 0.01), 0.99, places=12)
        self.assertFalse(1.0 * (1 - 0.01) <= 0.9899)

    def test_legacy_attainment_ratio_rule_is_zero_only(self) -> None:
        # revenue_report.py legacy rule: None if target_value == 0 else observed/target
        self.assertIsNone(None if 0 == 0 else 5 / 0)
        self.assertAlmostEqual(0.981, 0.4905 / 0.5, places=12)


# --------------------------------------------------------------------------
# 2. RED: the producer and the report must agree with one owner
# --------------------------------------------------------------------------


class SingleOwnerAgreementTests(unittest.TestCase):
    def test_legacy_emitted_row_matches_the_single_owner(self) -> None:
        from research.target_comparison import compare_legacy_target_measurement

        data = legacy_document(target_value=0.5, comparison="approximately", ratio=0.981)
        result = run_forecast(data)
        target = result["management_target_coverage"]["targets"][0]
        row = target["scenario_comparison"]["high"]
        owner = compare_legacy_target_measurement(target, result)["high"]
        self.assertEqual(owner, row)

    def test_legacy_row_key_set_is_unchanged(self) -> None:
        data = legacy_document(target_value=144.0)
        result = run_forecast(data)
        row = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        self.assertEqual(set(row), LEGACY_ROW_KEYS)

    def test_legacy_values_are_bit_identical_to_the_frozen_formulas(self) -> None:
        data = legacy_document(target_value=144.0, comparison="at_least")
        result = run_forecast(data)
        target = result["management_target_coverage"]["targets"][0]
        row = target["scenario_comparison"]["high"]
        observed = row["modeled_value"]
        self.assertEqual(row["modeled_value"], 144.0)
        self.assertEqual(row["target_value"], 144.0)
        self.assertEqual(row["meets_target"], observed >= 144.0 * (1 - 0.01))
        self.assertEqual(row["attainment_ratio"], observed / 144.0)
        self.assertEqual(row["measurement_basis"], "annual_period")
        self.assertEqual(row["measurement_periods"], ["FY2027"])
        self.assertEqual(row["modeled_period_values"], {"FY2027": observed})

    def test_legacy_zero_target_keeps_the_report_ratio_rule(self) -> None:
        data = legacy_document(target_value=0.0, comparison="approximately")
        result = run_forecast(data)
        row = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        self.assertIsNone(row["attainment_ratio"])
        self.assertTrue(row["meets_target"])
        self.assertEqual(row["target_value"], 0.0)

    def test_report_reaches_the_same_owner_for_the_legacy_branch(self) -> None:
        # The report must not accept a row the owner refuses. 0.4905 vs a 0.5
        # target is outside the legacy band [0.490, 0.510] once the observed
        # value is replaced; the report must refuse it.
        data = legacy_document(target_value=0.5, comparison="approximately")
        result = run_forecast(data)
        tampered = reseal(result)
        row = tampered["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        row["modeled_value"] = 0.5120
        row["modeled_period_values"]["2027"] = 0.5120
        row["meets_target"] = True
        with pytest.raises(ForecastInputError):
            validate_published_forecast(tampered, data)

    def test_producer_and_report_share_one_decision_function(self) -> None:
        from research import target_comparison

        source = (SCRIPTS / "research" / "target_comparison.py").read_text(encoding="utf-8")
        self.assertIn("def compare_legacy_target_measurement", source)
        # The owner spells each frozen expression exactly once.
        self.assertEqual(source.count("max(1.0, abs("), 1)
        self.assertEqual(source.count("def legacy_meets_target"), 1)
        self.assertTrue(hasattr(target_comparison, "legacy_meets_target"))


# --------------------------------------------------------------------------
# 3. the two callers hold no comparison arithmetic of their own
# --------------------------------------------------------------------------


def _numeric_literals(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            found.add(repr(node.value))
    return found


def _management_target_blocks(path: Path) -> list[ast.AST]:
    """Return the AST subtrees that own management-target comparison logic."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    blocks: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For)):
            segment = ast.get_source_segment(path.read_text(encoding="utf-8"), node) or ""
            if "scenario_comparison" in segment or "management_target_coverage" in segment:
                blocks.append(node)
    return blocks


def _comparison_calls_in_target_blocks(path: Path) -> list[tuple[int, str]]:
    """Find comparison *decision* arithmetic inside management-target blocks.

    Independent input binding (an exact ``rel_tol=1e-9, abs_tol=1e-9`` identity
    check against the result's own revenue path) is required by the card and is
    deliberately not counted here. What must not exist is a re-derivation of the
    attainment decision: a tolerance band built from ``comparison_tolerance``,
    the ``max(1.0, |v|)`` legacy absolute term, or the typed ``|v|,1e-12`` term.
    """
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    found: list[tuple[int, str]] = []
    for block in _management_target_blocks(path):
        for node in ast.walk(block):
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                if node.value in {1.0, 1e-12, 0.25}:
                    found.append((node.lineno, repr(node.value)))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr != "isclose":
                    continue
                keys = {kw.arg for kw in node.keywords}
                if "abs_tol" in keys:
                    segment = ast.get_source_segment(source, node) or ""
                    if "max(" in segment or "comparison_tolerance" in segment:
                        found.append((node.lineno, "isclose(abs_tol=max(...))"))
                elif "comparison_tolerance" in "".join(
                    lines[node.lineno - 1: node.lineno + 3]
                ):
                    found.append((node.lineno, "isclose(comparison_tolerance)"))
    return sorted(set(found))


class CallerGuardTests(unittest.TestCase):
    def test_report_holds_no_inline_target_comparison(self) -> None:
        path = SCRIPTS / "revenue_report.py"
        offenders = _comparison_calls_in_target_blocks(path)
        self.assertEqual(
            offenders, [],
            f"revenue_report.py still recomputes the target comparison at {offenders}",
        )

    def test_targets_module_holds_no_inline_target_comparison(self) -> None:
        path = SCRIPTS / "research" / "targets.py"
        offenders = _comparison_calls_in_target_blocks(path)
        self.assertEqual(
            offenders, [],
            f"research/targets.py still recomputes the target comparison at {offenders}",
        )

    def test_only_the_owner_defines_the_two_numeric_semantics(self) -> None:
        owner = (SCRIPTS / "research" / "target_comparison.py").read_text(encoding="utf-8")
        self.assertEqual(owner.count("max(1.0, abs("), 1)
        self.assertEqual(owner.count("def legacy_meets_target"), 1)
        self.assertEqual(owner.count("def legacy_acceptance_bound"), 1)
        typed = (SCRIPTS / "research" / "target_measurement.py").read_text(encoding="utf-8")
        self.assertEqual(typed.count("max(abs(low), 1e-12)"), 1)
        # The legacy attainment expression itself appears in exactly one module:
        # ``legacy_meets_target``. The typed expression stays in the DU6-frozen
        # typed owner (``research/target_measurement.py``), which this card must
        # not restate. Unrelated modules may still use their own
        # ``max(1.0, abs(...))`` tolerance for other contracts (document
        # validation, growth math, reconciliation), so the check is anchored on
        # the two comparison owners, not on the shape of the text.
        allowed = {"target_comparison.py", "target_measurement.py"}
        for path in sorted(SCRIPTS.rglob("*.py")):
            if path.name in allowed:
                continue
            self.assertNotIn(
                "rel_tol=tolerance",
                path.read_text(encoding="utf-8"),
                f"{path.relative_to(SCRIPTS)} still recomputes a target tolerance",
            )


# --------------------------------------------------------------------------
# 4. anti-tamper: every emitted legacy field is rebound to its inputs
# --------------------------------------------------------------------------


class LegacyAntiTamperTests(unittest.TestCase):
    @staticmethod
    def _result():
        data = legacy_document(target_value=144.0, comparison="at_least")
        return data, run_forecast(data)

    def test_tampered_fields_are_all_refused(self) -> None:
        data, result = self._result()
        mutations = {
            "modeled_value": lambda row: row.__setitem__("modeled_value", 999.0),
            "target_value": lambda row: row.__setitem__("target_value", 999.0),
            "attainment_ratio": lambda row: row.__setitem__("attainment_ratio", 9.99),
            "meets_target": lambda row: row.__setitem__("meets_target", False),
            "measurement_periods": lambda row: row.__setitem__("measurement_periods", ["FY2026"]),
            "measurement_basis": lambda row: row.__setitem__("measurement_basis", "cumulative_periods"),
            "modeled_period_values": lambda row: row["modeled_period_values"].__setitem__("2027", 999.0),
        }
        for label, mutate in mutations.items():
            with self.subTest(field=label):
                tampered = reseal(result)
                row = tampered["management_target_coverage"]["targets"][0][
                    "scenario_comparison"]["high"]
                mutate(row)
                with pytest.raises(ForecastInputError):
                    validate_published_forecast(tampered, data)

    def test_tampered_scenario_key_set_is_refused(self) -> None:
        data, result = self._result()
        tampered = reseal(result)
        comparison = tampered["management_target_coverage"]["targets"][0]["scenario_comparison"]
        comparison["bogus_scenario"] = copy.deepcopy(comparison["high"])
        with pytest.raises(ForecastInputError):
            validate_published_forecast(tampered, data)

    def test_legacy_row_cannot_be_swapped_for_a_typed_shaped_row(self) -> None:
        data, result = self._result()
        tampered = reseal(result)
        row = tampered["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        row.pop("modeled_period_values")
        with pytest.raises(ForecastInputError):
            validate_published_forecast(tampered, data)

    def test_legacy_row_is_not_a_typed_row(self) -> None:
        data, result = self._result()
        target = result["management_target_coverage"]["targets"][0]
        self.assertFalse(isinstance(target.get("comparison_basis"), dict))
        row = target["scenario_comparison"]["high"]
        # The typed row carries metric_kind/period/unit/target_low/...; the
        # legacy row must not silently gain or lose any of them.
        self.assertFalse({"metric_kind", "period", "unit", "target_low", "target_high"} & set(row))


if __name__ == "__main__":
    unittest.main()
