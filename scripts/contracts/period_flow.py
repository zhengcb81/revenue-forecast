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

# Average calendar month length used to classify covered lengths. Calendar
# halves are 181-184 days, quarters 89-92 days, fiscal years 365/366 days;
# tolerance below keeps those inside {3, 6, 12} and everything else out.
_AVG_MONTH_DAYS = 30.4375
_MONTH_TOLERANCE = 0.2


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
    """Calendar months covered by the inclusive window (nearest whole count)."""
    require(
        isinstance(start, date) and isinstance(end, date),
        "period_flow months requires date endpoints",
    )
    require(start < end, "period_start must be strictly before period_end")
    inclusive_days = (end - start).days + 1
    return round(inclusive_days / _AVG_MONTH_DAYS)


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
    inclusive_days = (end - start).days + 1
    exact_months = inclusive_days / _AVG_MONTH_DAYS
    months = round(exact_months)
    require(
        months in PERIOD_FLOW_MONTH_LENGTHS and abs(exact_months - months) <= _MONTH_TOLERANCE,
        f"{parameter_id}: period_flow must cover 3, 6 or 12 whole months; "
        f"got {inclusive_days} days",
    )
    return {"period_start": start, "period_end": end}
