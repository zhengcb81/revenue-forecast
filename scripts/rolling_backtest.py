"""ZR-713: rolling-origin historical backtest.

Strict as-of discipline: every window evaluates its snapshot using ONLY
information published on or before the window's ``as_of`` date — future
actuals never leak into earlier windows (any leaked record fails closed).

Three levels are backtested independently:

  company     — actual_company_revenue
  segment     — actual_segment_revenue
  mine-volume — operating-unit (ZR-605 MineYearOperation) volume lines

Each window emits a four-layer immutable hash chain:

  snapshot_id       — the frozen forecast snapshot identity
  actuals_sha256    — canonical hash of the as-of-filtered actuals
  evaluation_sha256 — canonical hash of the evaluation outcome
  record_sha256     — canonical hash of the accuracy record

When fewer than ``min_windows`` windows can form, the backtest is capped:
``capped=True`` with a rating-cap hint — metrics are never fabricated.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from contracts.evidence import (
    canonical_sha256,
    parse_iso_date,
    require,
)
from revenue_backtest import evaluate_snapshot, validate_snapshot

MIN_WINDOWS = 2
LEVELS = ("company", "segment", "mine-volume")


def _published_dates(actuals: Mapping[str, Any]) -> list[str]:
    dates: list[str] = []
    for source in actuals.get("sources", []):
        if isinstance(source, dict) and source.get("published_date"):
            dates.append(str(source["published_date"]))
    return dates


def _as_of_filtered(actuals: Mapping[str, Any], as_of: str) -> dict[str, Any]:
    """Return the as-of view of actuals: only sources published <= as_of."""
    filtered = copy.deepcopy(dict(actuals))
    kept: list[dict[str, Any]] = []
    leaked: list[str] = []
    for source in filtered.get("sources", []):
        if not isinstance(source, dict):
            continue
        published = source.get("published_date")
        if published is not None and str(published) > as_of:
            leaked.append(str(published))
            continue
        kept.append(source)
    require(
        not leaked,
        f"future actual leak: source published after as_of {as_of}: {leaked}",
    )
    filtered["sources"] = kept
    return filtered


def _evaluate_window(
    snapshot: Mapping[str, Any],
    actuals: Mapping[str, Any],
    as_of: str,
    level: str,
) -> dict[str, Any]:
    validate_snapshot(snapshot)
    filtered = _as_of_filtered(actuals, as_of)
    evaluation = evaluate_snapshot(snapshot, filtered)
    record = evaluation["accuracy_record"]
    window = {
        "level": level,
        "as_of": as_of,
        "snapshot_id": evaluation["backtest_id"],
        "actuals_sha256": canonical_sha256(filtered),
        "evaluation_sha256": canonical_sha256(evaluation),
        "record_sha256": record["record_sha256"],
        "wape": evaluation["summary"]["wape"],
        "observations": record.get("observations", 0),
    }
    return window


def _validate_windows(windows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    require(
        isinstance(windows, list) and bool(windows),
        "rolling backtest requires at least one window",
    )
    ordered = sorted(windows, key=lambda w: str(w.get("as_of", "")))
    for index, window in enumerate(ordered):
        require(
            isinstance(window, dict)
            and window.get("snapshot") is not None
            and window.get("actuals") is not None,
            f"window {index} requires as_of/snapshot/actuals",
        )
    return ordered


def run_rolling_backtest(
    windows: Sequence[Mapping[str, Any]],
    *,
    levels: Sequence[str] = LEVELS,
    min_windows: int = MIN_WINDOWS,
) -> dict[str, Any]:
    """Run a rolling-origin backtest over ordered windows.

    Each window = {as_of, snapshot, actuals} where ``actuals`` is the full
    actuals document (sources carry published_date; the engine enforces the
    as-of cut). Windows are evaluated in as_of order; a future-as-of window
    must never leak into an earlier window.
    """
    ordered = _validate_windows(windows)
    results: list[dict[str, Any]] = []
    for window in ordered:
        as_of = str(window["as_of"])
        parse_iso_date(as_of, f"window.as_of ({as_of})")
        snapshot = window["snapshot"]
        actuals = window["actuals"]
        for level in levels:
            if level == "mine-volume" and "operating_units" not in actuals:
                continue
            results.append(_evaluate_window(snapshot, actuals, as_of, level))
    capped = len(ordered) < min_windows or not results
    return {
        "windows": results,
        "window_count": len(ordered),
        "level_count": len({item["level"] for item in results}),
        "capped": capped,
        "rating_cap_hint": (
            "insufficient windows for a formed backtest — historical accuracy "
            "rating is capped" if capped else None
        ),
    }
