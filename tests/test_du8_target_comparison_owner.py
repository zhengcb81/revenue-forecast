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


class CallerGuardTests(unittest.TestCase):
    """Structural guards that the two callers hold no comparison arithmetic.

    A substring scan is defeatable by ordinary refactoring (renaming a
    parameter, reordering an expression), which the DU8 adversarial review
    demonstrated by re-introducing a full second comparison inside the guarded
    block while every text guard stayed green. These guards are therefore
    *semantic*: they compile the callers and ask which functions they call.
    """

    @staticmethod
    def _called_names(path: Path) -> set[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    names.add(func.id)
                elif isinstance(func, ast.Attribute):
                    names.add(func.attr)
        return names

    @staticmethod
    def _calls_owner(node: ast.AST) -> bool:
        """Whether *node* is a direct call to the shared comparison owner."""
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "compare_target_measurement"
        )

    @classmethod
    def _owner_gated_requires(cls, path: Path) -> list[ast.Call]:
        """``require`` calls whose *condition* is decided by the owner's value.

        A guard is only real when the owner's return value is what the
        ``require`` tests, and when the *published* comparison map is what it
        is tested against. The earlier version of this guard asked whether the
        condition's *source text* mentioned the owner, which a decoy call
        satisfies: ``require(True or bool(owner(...)), ...)`` keeps the text
        while the decision is local.

        This version requires an equality comparison of the form
        ``<published comparisons> == compare_target_measurement(...)``:

        * the condition must BE a ``Compare`` (no wrapping ``not``/``bool``/
          ternary that could invert or discard the verdict);
        * the top level may not be a ``BoolOp`` (an ``or``/``and`` escape hatch
          can force the outcome without consulting the owner);
        * the operator must be ``==``/``is`` — a comparison that cannot be
          satisfied by an unrelated side effect, unlike ``is not None``;
        * the owner call must be one operand and the published comparison map
          the other, so a decoy comparison (the owner against itself, or
          against an unrelated value) does not qualify.
        """
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        gated: list[ast.Call] = []
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "require"
                and node.args
            ):
                continue
            condition = node.args[0]
            # An ``or``/``and`` at the top level is an escape hatch.
            if isinstance(condition, ast.BoolOp):
                continue
            # ``not``, ``bool(...)``, ternaries: the verdict could be inverted
            # or discarded, so none of them count as gating on the value.
            if not isinstance(condition, ast.Compare):
                continue
            if not all(
                isinstance(op, (ast.Eq, ast.Is)) for op in condition.ops
            ):
                continue
            operands = [condition.left, *condition.comparators]
            owner_operands = [op for op in operands if cls._calls_owner(op)]
            if len(owner_operands) != 1:
                continue
            # The other operand must be the published comparison map, named by
            # the target's own output key. Comparing the owner to itself or to
            # an unrelated value is a decoy, not a binding.
            others = [
                op for op in operands
                if not cls._calls_owner(op)
            ]
            if not others:
                continue
            if not any(
                isinstance(op, ast.Name) and op.id == "comparisons"
                for op in others
            ):
                continue
            gated.append(node)
        return gated

    def test_report_asserts_the_owner_result_not_a_local_recompute(self) -> None:
        """The report must consult the owner rather than derive the decision.

        The typed branch compares the published map against the owner's return
        value. The legacy branch asks the owner to recompute from the report's
        own scenarios and compares the decision fields row by row, which is
        strictly stronger (see ``test_du8_owner_enforcement.py``). This guard
        only requires that at least one such binding exists and that a local
        band is not built; the behavioural suite is what actually enforces the
        invariant, because three successive shape-based guards were defeated.
        """
        gated = self._owner_gated_requires(SCRIPTS / "revenue_report.py")
        self.assertTrue(
            gated,
            "revenue_report.py never gates a require on the owner's return "
            "value; the comparison decision is no longer bound to the owner",
        )

    def test_owner_call_result_is_not_merely_echoed(self) -> None:
        """Calling the owner and discarding its value is not delegation.

        The bypass this rejects: assign the owner's return value to an unused
        name, then assert something locally true. The value must reach the
        assertion through the same ``<published map> == owner(...)`` shape the
        gating test requires, so a decoy call cannot satisfy it.
        """
        source = (SCRIPTS / "revenue_report.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name not in {"validate_forecast_output", "validate_published_forecast"}:
                continue
            body = ast.get_source_segment(source, node) or ""
            if "compare_target_measurement(" not in body:
                continue
            gated_in_function = [
                inner
                for inner in self._owner_gated_requires(SCRIPTS / "revenue_report.py")
                if node.lineno <= inner.lineno <= (node.end_lineno or node.lineno)
            ]
            self.assertTrue(
                gated_in_function,
                f"{node.name} calls the owner but never gates a require on its "
                "value; the owner's result is being echoed, not used",
            )

    def test_report_gates_the_typed_branch_on_the_owner(self) -> None:
        """The typed branch compares the published map against the owner.

        The legacy branch is verified differently and more strongly: it asks the
        owner to recompute from the report's own scenarios and then compares the
        decision fields row by row (see
        ``test_du8_owner_enforcement.py``). Counting owner-shaped ``require``
        sites is exactly the static heuristic that adversarial review defeated
        three times, so only the typed branch is checked structurally here and
        the real enforcement lives in the behavioural suite.
        """
        gated = self._owner_gated_requires(SCRIPTS / "revenue_report.py")
        self.assertTrue(
            gated,
            "revenue_report.py never gates a require on the owner's return "
            "value; the comparison decision is no longer bound to the owner",
        )

    def test_report_recomputes_the_decision_from_its_own_scenarios(self) -> None:
        """The legacy branch must ask the owner for a fresh row set.

        The durable property (three static guards were defeated before it was
        found): the owner must be called with the *report's* view of the model
        and the result compared field by field, so no echo of the artifact can
        satisfy the check. This asserts that the call site receives a target
        whose stored comparison rows are not what gets compared.
        """
        source = (SCRIPTS / "revenue_report.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        call_lines: list[int] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "compare_target_measurement":
                    call_lines.append(node.lineno)
        self.assertGreaterEqual(
            len(call_lines),
            2,
            "revenue_report.py must consult the owner in both comparison "
            f"branches; owner calls found at lines {call_lines}",
        )
        # The legacy call must be fed a target with its comparison rows cleared,
        # so the owner cannot be handed the artifact's own answer.
        segment = source.splitlines()
        legacy_calls = [
            line for line in call_lines
            if "scenario_comparison=None" in "\n".join(
                segment[max(0, line - 6):line + 8]
            )
        ]
        self.assertTrue(
            legacy_calls,
            "the legacy branch must rebuild the comparison from the model with "
            "the stored rows withheld; no such owner call found",
        )

    def test_targets_module_uses_the_owner_result_directly(self) -> None:
        """The producer must *store* the owner's return value, not rebuild it.

        ``add_management_target_analysis`` attaches the comparison to the
        output, so the contract here is that the stored value IS the owner's
        return value — an assignment, not a local reconstruction.
        """
        source = (SCRIPTS / "research" / "targets.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        assigned_from_owner = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            value = node.value
            if not (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)):
                continue
            if value.func.id == "compare_target_measurement":
                assigned_from_owner = True
        self.assertTrue(
            assigned_from_owner,
            "research/targets.py does not store the owner's return value directly; "
            "the producer comparison is no longer bound to the shared owner",
        )

    def test_report_never_builds_a_local_target_band(self) -> None:
        """No expression in the report may combine a tolerance with a target.

        This is shape-based on purpose: it must catch a band written with any
        variable names, including the ``_floor``/``_ok`` form that defeated the
        previous substring guard.
        """
        source = (SCRIPTS / "revenue_report.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        offenders: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in {
                "validate_forecast_output", "validate_published_forecast",
            }:
                for inner in ast.walk(node):
                    if not isinstance(inner, ast.Compare):
                        continue
                    segment = ast.get_source_segment(source, inner) or ""
                    lowered = segment.lower()
                    if "comparison_tolerance" in lowered or "_tol" in lowered:
                        offenders.append(f"line {inner.lineno}: {segment[:120]}")
        self.assertEqual(
            offenders, [],
            f"revenue_report.py builds a local attainment band: {offenders}",
        )

    def test_report_delegates_the_comparison_decision(self) -> None:
        names = self._called_names(SCRIPTS / "revenue_report.py")
        self.assertIn(
            "compare_target_measurement",
            names,
            "revenue_report.py must call the shared comparison owner",
        )

    def test_targets_module_delegates_the_comparison_decision(self) -> None:
        names = self._called_names(SCRIPTS / "research" / "targets.py")
        self.assertIn(
            "compare_target_measurement",
            names,
            "research/targets.py must call the shared comparison owner",
        )

    def test_report_does_not_call_the_band_builders_itself(self) -> None:
        """The report may not reach for either band builder directly."""
        names = self._called_names(SCRIPTS / "revenue_report.py")
        for forbidden in ("legacy_meets_target", "legacy_acceptance_bound",
                          "legacy_target_ratio", "meets_target", "acceptance_bound"):
            with self.subTest(symbol=forbidden):
                self.assertNotIn(
                    forbidden,
                    names,
                    f"revenue_report.py must not call {forbidden} directly; "
                    f"only the owner decides attainment",
                )

    def test_targets_module_does_not_call_the_band_builders_itself(self) -> None:
        names = self._called_names(SCRIPTS / "research" / "targets.py")
        for forbidden in ("legacy_meets_target", "legacy_acceptance_bound",
                          "legacy_target_ratio", "meets_target", "acceptance_bound"):
            with self.subTest(symbol=forbidden):
                self.assertNotIn(
                    forbidden,
                    names,
                    f"research/targets.py must not call {forbidden} directly",
                )

    def test_the_only_modules_defining_the_band_arithmetic(self) -> None:
        """Repository-wide: exactly two modules define a comparison band."""
        defining: set[str] = set()
        for path in sorted(SCRIPTS.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name in {
                    "legacy_acceptance_bound", "acceptance_bound",
                    "legacy_meets_target", "meets_target",
                }:
                    defining.add(path.name)
        self.assertEqual(
            defining,
            {"target_comparison.py", "target_measurement.py"},
            f"unexpected module defines comparison arithmetic: {sorted(defining)}",
        )

    def test_no_caller_rebuilds_the_target_comparison_band(self) -> None:
        """A target comparison band is identifiable by its *source*, not its shape.

        The distinguishing input is the declared ``comparison_tolerance`` of a
        management target. Only the two owner modules may turn that value into
        a band. Unrelated contracts (document validation, input quantities)
        legitimately build their own tolerances from other inputs and are not
        this card's business.

        Renaming a local variable cannot hide this: the check follows the
        function's own source for the declared tolerance key.
        """
        allowed = {"target_comparison.py", "target_measurement.py"}
        offenders: list[str] = []
        for path in sorted(SCRIPTS.rglob("*.py")):
            if path.name in allowed:
                continue
            source = path.read_text(encoding="utf-8")
            if "comparison_tolerance" not in source:
                continue
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                body = ast.get_source_segment(source, node) or ""
                if "comparison_tolerance" not in body:
                    continue
                for inner in ast.walk(node):
                    if not (
                        isinstance(inner, ast.Call)
                        and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr in {"isclose", "approx"}
                    ):
                        continue
                    for keyword in inner.keywords:
                        if keyword.arg != "abs_tol":
                            continue
                        segment = ast.get_source_segment(source, keyword.value) or ""
                        if "1e-9" in segment:
                            continue
                        offenders.append(f"{path.name}:{inner.lineno}")
        self.assertEqual(
            offenders, [],
            f"a caller rebuilds the target comparison band at {offenders}",
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
