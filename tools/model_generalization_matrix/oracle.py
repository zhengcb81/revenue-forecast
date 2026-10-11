"""Independent hand-computed oracle for the model generalization matrix.

This module is deliberately standalone.  Every function computes an expected
value from the *input drivers alone* using the documented model formula or a
hand-computed conservation law.  It never imports or calls the engine under
test (``revenue_core``), so an expected value can never be derived from the
result being tested.  A wrong engine result is therefore always caught here.

Only pure arithmetic is used.  Where a boundary is a *reject* or an *unknown*
(null) rather than a number, the oracle returns an explicit sentinel so the
comparison layer can assert it without inventing a number.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

# Sentinels that stand for "there is no finite number here" without pretending
# the value is zero.  A reject and an unknown are different things.
REJECT = object()  # the entry must refuse the input with a contract reason
UNKNOWN = object()  # the honest value is null/undefined, never 0


@dataclass(frozen=True)
class Expected:
    """Frozen expectation for one case.

    ``values`` holds hand-computed numbers keyed by a stable label.  ``reject``
    marks the whole vector as a rejection expectation.  ``conservation`` holds
    named conservation assertions that must hold between the values (or between
    input drivers and observed values), expressed as small predicates over the
    observed mapping in the runner.
    """

    values: Mapping[str, Any] = field(default_factory=dict)
    reject: bool = False
    reject_reason: str | None = None
    unknown_fields: Sequence[str] = ()
    conservation: Mapping[str, str] = field(default_factory=dict)


# --- M01: quantity x price x currency/unit ---------------------------------

def unit_sales_revenue(
    units: Sequence[float],
    unit_revenue: Sequence[float],
    timing_factor: Sequence[float] | None = None,
    other_revenue: Sequence[float] | None = None,
) -> list[float]:
    """revenue = units * unit_revenue * timing_factor + other_revenue (hand formula)."""
    n = len(units)
    timing = list(timing_factor) if timing_factor is not None else [1.0] * n
    other = list(other_revenue) if other_revenue is not None else [0.0] * n
    return [
        units[i] * unit_revenue[i] * timing[i] + other[i] for i in range(n)
    ]


def economic_amount(engine_value: float, unit_scale: float) -> float:
    """Economic amount in a common base unit; invariant under same-dimension scaling."""
    return engine_value * unit_scale


def scaled_amount_preserved(
    value_a: float, scale_a: float, value_b: float, scale_b: float
) -> bool:
    """True when the same economic amount is expressed at two same-family scales."""
    return abs(value_a * scale_a - value_b * scale_b) <= 1e-9 * max(
        1.0, abs(value_a * scale_a)
    )


# --- M02: ARR stock -> recognition + late contract/churn -------------------

def arr_bridge_revenue(
    opening_arr: Sequence[float],
    gross_retention_rate: Sequence[float],
    expansion_arr: Sequence[float],
    new_arr: Sequence[float],
    lost_arr_revenue_fraction: Sequence[float],
    expansion_revenue_fraction: Sequence[float],
    new_arr_revenue_fraction: Sequence[float],
    usage_revenue: Sequence[float] | None = None,
) -> list[float]:
    """revenue = opening - opening*(1-grr)*lost + expansion*exp + new*new + usage."""
    n = len(opening_arr)
    usage = list(usage_revenue) if usage_revenue is not None else [0.0] * n
    out = []
    for i in range(n):
        churned_revenue = (
            opening_arr[i] * (1.0 - gross_retention_rate[i]) * lost_arr_revenue_fraction[i]
        )
        out.append(
            opening_arr[i]
            - churned_revenue
            + expansion_arr[i] * expansion_revenue_fraction[i]
            + new_arr[i] * new_arr_revenue_fraction[i]
            + usage[i]
        )
    return out


def closing_arr_is_not_revenue(
    closing_arr: Sequence[float], revenue: Sequence[float]
) -> bool:
    """Conservation boundary: the ARR stock is not the recognized revenue line."""
    return any(abs(c - r) > 1e-9 for c, r in zip(closing_arr, revenue))


# --- M03: capacity/demand/launch fraction ---------------------------------

def commercial_launch_revenue(
    eligible_units: Sequence[float],
    adoption_rate: Sequence[float],
    annual_supply_capacity: Sequence[float],
    commercial_year_fraction: Sequence[float],
    net_revenue_per_unit: Sequence[float],
) -> list[float]:
    """conditional = min(eligible*adoption, capacity) * fraction * net_rev (fraction once)."""
    out = []
    for i in range(len(eligible_units)):
        demand = eligible_units[i] * adoption_rate[i]
        capped = min(demand, annual_supply_capacity[i])
        out.append(capped * commercial_year_fraction[i] * net_revenue_per_unit[i])
    return out


# --- M05: zero-base commercial launch + CAGR ------------------------------

def cagr(base: float, terminal: float, periods: int) -> float | None:
    """CAGR is undefined (None) when the base is zero; never 0, never an error."""
    if base <= 0 or terminal < 0 or periods <= 0:
        return None
    return (terminal / base) ** (1.0 / periods) - 1.0


# --- M06: shared shock + joint scenarios ----------------------------------

def quarter_delay_shock(
    before: Mapping[str, float], deferred: float, catch_up_fraction: float
) -> dict[str, float]:
    """One shared shock applied exactly once.

    Conservation: the first year drops by the deferred amount; the second year
    recovers ``deferred * catch_up_fraction``; the net across both years is the
    ``-deferred * (1 - catch_up_fraction)`` cancellation.  The shock is never
    applied twice.
    """
    years = sorted(before)
    y0, y1 = years[0], years[1]
    after = dict(before)
    after[y0] = before[y0] - deferred
    after[y1] = before[y1] + deferred * catch_up_fraction
    return after


def shock_applied_once(
    before: Mapping[str, float], after: Mapping[str, float], deferred: float
) -> bool:
    """The first-year drop equals the deferred amount exactly once (not double)."""
    years = sorted(before)
    drop = before[years[0]] - after[years[0]]
    return abs(drop - deferred) <= 1e-9 * max(1.0, abs(deferred))


# --- M07: management target + gross/net/cannibalization -------------------

def annual_target_comparison(raw_value: float, measurement_basis: str) -> float | None:
    """A comparable annual target keeps its value; a run-rate/cumulative does not
    masquerade as the current-year figure (no invented annualization)."""
    if measurement_basis == "annual_period":
        return raw_value
    return None  # leave a gap; never re-label a run-rate/cumulative as current year


# --- M08: optional operating support + segment/year/scenario + future -----

def support_cell_status(
    covered: bool, has_uncovered_params: bool
) -> str:
    """Per-cell support: one calibrated cell never presumes another cell is covered."""
    if covered and not has_uncovered_params:
        return "supported"
    if covered and has_uncovered_params:
        return "conditional"
    return "unsupported"


def unknown_stays_null(value: Any) -> bool:
    """An unknown observed range/actual is null, never coerced to 0."""
    return value is None
