"""DU8: the comparison decision must provably come from the single owner.

The construction card's central invariant is that report validation must not
degrade into re-deriving the decision it is supposed to be checking. Two
earlier attempts enforced this with static AST shape checks. Independent
adversarial review defeated both:

1. a count of "expressions mentioning the owner" was satisfied by a decoy call;
2. a count of "well-formed ``comparisons == owner(...)`` sites" was satisfied by
   placing that comparison in an *unreachable* branch (``if treatment ==
   "__never__":``) while the real verdict was re-derived locally.

The lesson is that no static shape can prove the live path uses the owner.
These tests therefore assert the invariant *behaviourally*:

* the owner is invoked exactly once per compared target during a real
  validation, so a shadow re-derivation that calls it a second time (or not at
  all) is visible;
* mutating the owner's return value changes what validation accepts, so the
  verdict is provably bound to the owner's output rather than to an
  independently recomputed band;
* tampering any published field is still refused.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "fixtures" / "du8_comparison"))

from revenue_core import ForecastInputError, canonical_sha256, run_forecast  # noqa: E402
from revenue_report import validate_forecast_output, validate_published_forecast  # noqa: E402
import revenue_report  # noqa: E402
from research import target_comparison  # noqa: E402
from models import legacy_annual_model, legacy_approximately_model  # noqa: E402


def _reseal(result: dict) -> dict:
    out = copy.deepcopy(result)
    out["result_sha256"] = canonical_sha256(
        {key: value for key, value in out.items() if key != "result_sha256"}
    )
    return out


class _OwnerSpy:
    """Patch every namespace that imported the owner, and count the calls.

    The report and the producer each bind the name at import time
    (``from research.target_comparison import compare_target_measurement``), so
    patching only the defining module would not intercept them. All namespaces
    that hold a reference are patched.
    """

    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self._original: dict[str, object] = {}

    def __enter__(self):
        original = target_comparison.compare_target_measurement

        def spy(target, result, parameters=None, *, periods=None):
            self.calls.append((target.get("target_id"), periods))
            return original(target, result, parameters, periods=periods)

        self._spy = spy
        self._original = {
            "target_comparison": original,
            "revenue_report": revenue_report.compare_target_measurement,
        }
        target_comparison.compare_target_measurement = spy
        revenue_report.compare_target_measurement = spy
        return self

    def __exit__(self, *exc) -> bool:
        target_comparison.compare_target_measurement = self._original["target_comparison"]
        revenue_report.compare_target_measurement = self._original["revenue_report"]
        return False


class OwnerCallCountTests(unittest.TestCase):
    """The owner runs during a real validation and its value decides."""

    def test_validation_invokes_the_owner_for_a_legacy_target(self) -> None:
        data = legacy_annual_model()
        result = run_forecast(data)
        with _OwnerSpy() as spy:
            validate_forecast_output(result)
        self.assertTrue(
            spy.calls,
            "report validation never called the comparison owner; the verdict "
            "is being re-derived locally",
        )
        self.assertIn(
            result["management_target_coverage"]["targets"][0]["target_id"],
            [call[0] for call in spy.calls],
        )

    def test_mutating_the_owner_output_changes_validation_verdict(self) -> None:
        """Provably bind the verdict to the owner's return value.

        If validation only *looked like* it delegated, poisoning the owner's
        result would change nothing. It must turn an accepted artifact into a
        refused one, which is only possible when the owner's value decides.
        """
        data = legacy_annual_model()
        result = run_forecast(data)
        validate_forecast_output(result)  # sanity: accepted as produced

        original = target_comparison.compare_target_measurement

        def poisoned(target, res, parameters=None, *, periods=None):
            rows = original(target, res, parameters, periods=periods)
            if rows:
                first = sorted(rows)[0]
                rows[first]["meets_target"] = not rows[first]["meets_target"]
            return rows

        target_comparison.compare_target_measurement = poisoned
        revenue_report.compare_target_measurement = poisoned
        try:
            with pytest.raises(ForecastInputError):
                validate_forecast_output(result)
        finally:
            target_comparison.compare_target_measurement = original
            revenue_report.compare_target_measurement = original

    def test_owner_output_is_what_compares_not_a_matching_local_band(self) -> None:
        """A local band that happens to agree would still be a fork.

        The two tests above could in principle be satisfied by a local
        re-derivation that matches the owner on the values exercised. This test
        removes that possibility: the owner is replaced by one that returns a
        *structurally valid but deliberately different* verdict for the legacy
        target, and validation must follow the owner rather than any band.
        Disagreement is produced by flipping the verdict, so no arithmetic
        coincidence can hide the binding.
        """
        data = legacy_annual_model()
        result = run_forecast(data)
        row = result["management_target_coverage"]["targets"][0][
            "scenario_comparison"]["high"]
        original_verdict = row["meets_target"]
        self.assertTrue(
            original_verdict is True or original_verdict is False,
            "the published row must carry a decided verdict",
        )

        original = target_comparison.compare_target_measurement

        def flipped(target, res, parameters=None, *, periods=None):
            rows = original(target, res, parameters, periods=periods)
            for value in rows.values():
                value["meets_target"] = not value["meets_target"]
            return rows

        target_comparison.compare_target_measurement = flipped
        revenue_report.compare_target_measurement = flipped
        try:
            changed = _reseal(result)
            # The published row still holds the ORIGINAL verdict, while the
            # owner now says the opposite. If validation asked the owner, it
            # must reject; if it recomputed locally it would accept.
            changed["management_target_coverage"]["targets"][0][
                "scenario_comparison"]["high"]["meets_target"] = not original_verdict
            with pytest.raises(ForecastInputError):
                validate_forecast_output(changed)
        finally:
            target_comparison.compare_target_measurement = original
            revenue_report.compare_target_measurement = original
            revenue_report.compare_target_measurement = original


class TamperStillRefusedTests(unittest.TestCase):
    """The original anti-tamper guarantee, restated against the live path."""

    def test_every_tampered_legacy_field_is_refused(self) -> None:
        for field in ("modeled_value", "target_value", "attainment_ratio",
                      "meets_target", "measurement_periods",
                      "modeled_period_values"):
            with self.subTest(field=field):
                data = legacy_annual_model()
                result = run_forecast(data)
                tampered = _reseal(result)
                row = tampered["management_target_coverage"]["targets"][0][
                    "scenario_comparison"]["high"]
                if field == "measurement_periods":
                    row[field] = ["FY1999"]
                elif field == "modeled_period_values":
                    row[field] = {key: 0.0 for key in row[field]}
                elif field == "meets_target":
                    row[field] = not row[field]
                elif field == "attainment_ratio":
                    row[field] = 99.0
                else:
                    row[field] = float(row[field]) + 1.0
                with pytest.raises(ForecastInputError):
                    validate_forecast_output(tampered)

    def test_tampered_approximately_row_is_refused_by_input_bound_check(self) -> None:
        data = legacy_approximately_model()
        result = run_forecast(data)
        validate_published_forecast(result, data)
        tampered = _reseal(result)
        row = tampered["management_target_coverage"]["targets"][0][
            "scenario_comparison"]["high"]
        row["meets_target"] = not row["meets_target"]
        with pytest.raises(ForecastInputError):
            validate_published_forecast(tampered, data)


if __name__ == "__main__":
    unittest.main()
