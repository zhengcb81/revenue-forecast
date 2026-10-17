"""One owner for management-target scenario comparison (DU8).

Before DU8 the "does this scenario meet the target" decision existed three
times: ``research.target_measurement`` (typed), ``research.targets`` (legacy
production) and ``revenue_report`` (legacy verification). The report's copy
made report validation a comparison of two results produced by the same
formula, so a future edit to the producer would have moved the verifier with
it instead of being caught by it.

This module is the single owner. It keeps the two historical numeric
semantics side by side as **explicit compatibility paths** rather than
collapsing them:

``typed``
    ``management-target-comparison/1`` targets. Delegates to
    ``research.target_measurement``, which DU6 froze (sign-safe acceptance
    bands, strict comparisons, two-ended ranges, no invented midpoint).

``legacy``
    Targets with no ``comparison_basis`` dict. Preserves the published
    arithmetic bit for bit:

    * ``approximately`` -> ``isclose(observed, v, rel_tol=t,
      abs_tol=max(1.0, |v|) * t)``;
    * ``at_least`` -> ``observed >= v * (1 - t)``;
    * ``at_most`` -> ``observed <= v * (1 + t)``;
    * ``attainment_ratio`` -> ``None if v == 0 else observed / v``.

The two are deliberately different below ``|v| = 1`` and for negative point
targets: the legacy absolute term is a fixed one-unit floor, the typed one is
``|v|`` itself, and only the typed path accepts a negative point target at
all. Unifying them would silently restate published results, so the split is
named here instead of being inferred from the magnitude of the inputs.

Callers do not choose a branch by guessing from the data: :func:`is_typed_target`
is the single predicate, and both the producer and the report call
:func:`compare_target_measurement` with the already-resolved target.
"""
from __future__ import annotations

import math
from typing import Any

from contracts.evidence import finite_number, require
from research.target_measurement import (
    compare_target_measurement as _compare_typed_target_measurement,
    is_typed_target,
)

__all__ = [
    "LEGACY_COMPARISON_ROW_KEYS",
    "LEGACY_COMPARISON_ROW_KEYS_31",
    "compare_legacy_target_measurement",
    "compare_target_measurement",
    "is_typed_target",
    "legacy_acceptance_bound",
    "legacy_meets_target",
    "legacy_target_ratio",
]

# Exact published key set of a legacy comparison row. Frozen: the report
# verifies set equality, not a superset.
LEGACY_COMPARISON_ROW_KEYS = frozenset(
    {
        "measurement_basis",
        "measurement_periods",
        "modeled_period_values",
        "modeled_value",
        "target_value",
        "attainment_ratio",
        "meets_target",
    }
)

# Schema 3.1 published the same row without the measurement basis/periods and
# the per-period values. That shape is immutable and must not gain keys.
LEGACY_COMPARISON_ROW_KEYS_31 = frozenset(
    {"modeled_value", "target_value", "attainment_ratio", "meets_target"}
)

_MODELED_TREATMENTS = frozenset(
    {"modeled_scenario", "scenario_boundary", "independent_benchmark"}
)


def legacy_acceptance_bound(value: float, tolerance: float, *, lower: bool) -> float:
    """The frozen pre-DU6 acceptance edge ``value * (1 -/+ tolerance)``.

    Kept verbatim, including its behaviour for a negative point target: the
    band narrows toward zero instead of widening away from it. That is the
    published legacy arithmetic; the typed path's sign-safe
    ``acceptance_bound`` lives in :mod:`research.target_measurement` and is not
    substituted here.
    """
    return value * (1 - tolerance) if lower else value * (1 + tolerance)


def legacy_target_ratio(observed: float | None, target_value: float) -> float | None:
    """The frozen legacy ratio rule: withheld only for an exact zero target."""
    if observed is None or target_value == 0:
        return None
    return observed / target_value


def legacy_meets_target(
    observed: float, target_value: float, comparison: str, tolerance: float
) -> bool:
    """The frozen legacy attainment test for one point target."""
    if comparison == "at_least":
        return observed >= legacy_acceptance_bound(target_value, tolerance, lower=True)
    if comparison == "at_most":
        return observed <= legacy_acceptance_bound(target_value, tolerance, lower=False)
    return math.isclose(
        observed,
        target_value,
        rel_tol=tolerance,
        abs_tol=max(1.0, abs(target_value)) * tolerance,
    )


def legacy_comparison_row(
    *,
    observed: float,
    target_value: float,
    measurement_basis: str,
    measurement_periods: list[str],
    period_values: dict[str, float],
    comparison: str,
    tolerance: float,
    schema_version: str = "3.2",
) -> dict[str, Any]:
    """Build one legacy comparison row with its exact key set and order.

    Schema 3.1 published only the four aggregate fields; 3.2 and later added
    the measurement basis, the declared periods and the per-period values.
    The schema is the *declared output version*, not a guess from the values.
    """
    row = {
        "measurement_basis": measurement_basis,
        "measurement_periods": measurement_periods,
        "modeled_period_values": period_values,
        "modeled_value": observed,
        "target_value": target_value,
        "attainment_ratio": legacy_target_ratio(observed, target_value),
        "meets_target": legacy_meets_target(
            observed, target_value, comparison, tolerance
        ),
    }
    if schema_version == "3.1":
        for key in ("measurement_basis", "measurement_periods", "modeled_period_values"):
            row.pop(key)
    return row


def legacy_comparison_tolerance(target: dict) -> float:
    """Read and bound the declared legacy tolerance exactly as published."""
    tolerance = finite_number(
        target.get("comparison_tolerance", 0.01),
        f"{target['target_id']}.comparison_tolerance",
    )
    require(
        0 <= tolerance <= 0.25,
        f"management target comparison_tolerance outside 0..0.25: {target['target_id']}",
    )
    return tolerance


def _legacy_revenue_path(result: dict, target: dict, scenario: str) -> dict:
    if target["scope"]["type"] == "company":
        return result["consolidated_forecast"][scenario]["annual_revenue"]
    segment = next(
        item for item in result["segments"] if item["name"] == target["scope"]["name"]
    )
    scenario_output = segment["scenarios"][scenario]
    return scenario_output.get("effective_revenue", scenario_output["recognized_revenue"])


def compare_legacy_target_measurement(
    target: dict, result: dict, *, periods: list[str] | None = None
) -> dict[str, Any]:
    """Compare one legacy (non-typed) target across its mapped scenarios.

    ``periods`` lets a caller that already resolved the schema-dependent
    measurement periods reuse them. The schema-3.1 output shape carries no
    ``measurement_periods`` at all, so a 3.1 caller passes
    ``[target_period]`` explicitly; every other caller passes the target's own
    declared periods or omits the argument. The schema version comes from the
    result being compared, never from the magnitude of the numbers.
    """
    if not is_modeled_comparison(target):
        return {}
    if periods is None:
        periods = target.get("measurement_periods")
        if periods is None:
            periods = [target["target_period"]]
    measurement_periods = list(periods)
    schema_version = result.get("schema_version", "3.2")
    # Schema 3.1 predates the declared measurement basis and always compared a
    # single annual period, so its rows carry no basis field at all.
    measurement_basis = target.get("measurement_basis", "annual_period")
    target_value = float(target["comparison_value"])
    tolerance = legacy_comparison_tolerance(target)
    comparisons: dict[str, Any] = {}
    for scenario in target["mapped_scenarios"]:
        revenue_path = _legacy_revenue_path(result, target, scenario)
        period_values = {
            period: float(revenue_path[period[2:]]) for period in measurement_periods
        }
        if measurement_basis == "cumulative_periods":
            observed = sum(period_values.values())
        else:
            observed = period_values[measurement_periods[0]]
        row = legacy_comparison_row(
            observed=observed,
            target_value=target_value,
            measurement_basis=measurement_basis,
            measurement_periods=measurement_periods,
            period_values=period_values,
            comparison=target["comparison"],
            schema_version=schema_version,
            tolerance=tolerance,
        )
        require(
            row["meets_target"] or target["treatment"] == "independent_benchmark",
            f"mapped scenario does not satisfy management target: "
            f"{target['target_id']}/{scenario}",
        )
        comparisons[scenario] = row
    return comparisons


def is_modeled_comparison(target: dict) -> bool:
    """Whether a target's treatment participates in numerical comparison."""
    return target["treatment"] in _MODELED_TREATMENTS


def compare_target_measurement(
    target: dict,
    result: dict,
    parameters: dict | None = None,
    *,
    periods: list[str] | None = None,
) -> dict[str, Any]:
    """Route one target to its one comparison owner.

    The branch is selected by :func:`is_typed_target` — a declared input shape,
    never the magnitude or sign of the numbers involved.

    ``periods`` is a legacy-path override for the schema-dependent measurement
    periods (schema 3.1 carries none). A typed target owns its periods inside
    ``comparison_basis``, so passing the override for one is a caller error and
    is refused rather than silently dropped.
    """
    if is_typed_target(target):
        require(
            periods is None,
            "typed management target owns its measurement periods; "
            "no caller override is accepted",
        )
        return _compare_typed_target_measurement(target, result, parameters)
    return compare_legacy_target_measurement(target, result, periods=periods)
