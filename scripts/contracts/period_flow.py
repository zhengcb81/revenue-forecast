"""M3-FLOW (root cause R20): typed dated period flows, schema 3.9 opt-in.

A ``time_basis=period_flow`` parameter states that its ``value`` is the amount
recognized over the explicit ``[period_start, period_end]`` window — nothing
else. The pure rules below keep the amount attached to the covered period:

* both dates are required, strict ISO days, and ``period_start < period_end``;
* the window must lie inside the fiscal year named by the ``period`` label as
  resolved from the document's ``fiscal_year_end`` — this is what makes
  cross-calendar-year flows and non-calendar fiscal years expressible without
  any new period vocabulary;
* the covered length must be 3, 6 or 12 calendar months (an exact fiscal-year
  span is twelve month-differences by construction);
* amounts are never annualized implicitly: an H1 flow plus an H2 flow composes
  into the annual flow only through an explicit derived formula (x0+x1), and a
  point-in-time stock keeps the legacy ``point_in_time`` basis untouched.

Unknown start dates stay unknown: the contract requires both endpoints, so an
author who cannot evidence a real start date must not fabricate one — the flow
simply cannot be typed as ``period_flow`` yet.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta

from contracts.constants import (
    PERIOD_FLOW_MONTH_LENGTHS,
    PERIOD_FLOW_TIME_BASIS,
)
from contracts.evidence import (
    ForecastInputError,
    parse_iso_date,
    period_year,
    require,
)

def _fiscal_year_end_date(fiscal_year_end: str, year: int) -> date:
    month, day = int(fiscal_year_end[:2]), int(fiscal_year_end[3:])
    try:
        return date(year, month, day)
    except ValueError as exc:
        if (month, day) == (2, 29):
            # A Feb-29 FYE anchors to Feb-28 in non-leap years so windows
            # stay contiguous; the MM-DD shape itself is validated upstream.
            return date(year, 2, 28)
        raise ForecastInputError(
            f"fiscal_year_end {fiscal_year_end} is not a valid month-day"
        ) from exc


def fiscal_year_window(fiscal_year_end: str, year: int) -> tuple[date, date]:
    """Return the (start, end) dates of fiscal year ``year`` (inclusive)."""
    require(
        isinstance(fiscal_year_end, str) and len(fiscal_year_end) == 5,
        "fiscal_year_end must use MM-DD",
    )
    end = _fiscal_year_end_date(fiscal_year_end, int(year))
    start = _fiscal_year_end_date(fiscal_year_end, int(year) - 1) + timedelta(days=1)
    return start, end


def period_flow_months(start: date, end: date) -> int:
    """Exact 3/6/12 calendar-month span, using inclusive end dates.

    The next period starts at the calendar-month anniversary of ``start``.
    A duration merely close to a quarter or half year has no typed-month
    meaning. The caller handles an exact fiscal-year window separately to
    preserve leap-day year-end conventions.
    """
    require(
        isinstance(start, date) and isinstance(end, date),
        "period_flow months requires date endpoints",
    )
    require(start < end, "period_start must be strictly before period_end")
    # Compare the exclusive boundary as a tuple so a valid window ending
    # on 9999-12-31 does not overflow datetime by adding one day.
    if end.day == monthrange(end.year, end.month)[1]:
        exclusive_year, exclusive_month_index = divmod(end.year * 12 + end.month, 12)
        exclusive_end = (exclusive_year, exclusive_month_index + 1, 1)
    else:
        exclusive_end = (end.year, end.month, end.day + 1)
    for months in sorted(PERIOD_FLOW_MONTH_LENGTHS):
        month_index = start.year * 12 + start.month - 1 + months
        year, zero_based_month = divmod(month_index, 12)
        month = zero_based_month + 1
        boundary = (year, month, min(start.day, monthrange(year, month)[1]))
        if exclusive_end == boundary:
            return months
    raise ForecastInputError(
        "period_flow must cover 3, 6 or 12 whole calendar months; "
        f"got {start.isoformat()}..{end.isoformat()}"
    )


def validate_period_flow_fields(
    parameter_id: str,
    parameter: dict,
    fiscal_year_end: str,
) -> dict[str, date]:
    """Fail closed unless the parameter carries a legal dated flow.

    Returns the parsed endpoints ``{"period_start": date, "period_end": date}``
    for callers that need typed dates (rendering, downstream checks).
    """
    require(
        "period_start" in parameter and "period_end" in parameter,
        f"{parameter_id}: time_basis {PERIOD_FLOW_TIME_BASIS} requires "
        "period_start and period_end",
    )
    start = parse_iso_date(parameter["period_start"], f"{parameter_id}.period_start")
    end = parse_iso_date(parameter["period_end"], f"{parameter_id}.period_end")
    require(
        start < end,
        f"{parameter_id}: period_start must be strictly before period_end",
    )
    year = period_year(parameter.get("period"), f"{parameter_id}.period")
    window_start, window_end = fiscal_year_window(fiscal_year_end, year)
    require(
        window_start <= start and end <= window_end,
        f"{parameter_id}: period_flow dates must lie within the FY{year} window "
        f"({window_start.isoformat()}..{window_end.isoformat()}) implied by "
        f"fiscal_year_end {fiscal_year_end}",
    )
    # A fiscal year is explicitly a twelve-month reporting window even
    # when its leap-day boundary does not match a naive date anniversary.
    # All shorter flows must match exact calendar-month boundaries.
    if (start, end) != (window_start, window_end):
        try:
            period_flow_months(start, end)
        except ForecastInputError as exc:
            raise ForecastInputError(f"{parameter_id}: {exc}") from exc
    return {"period_start": start, "period_end": end}
