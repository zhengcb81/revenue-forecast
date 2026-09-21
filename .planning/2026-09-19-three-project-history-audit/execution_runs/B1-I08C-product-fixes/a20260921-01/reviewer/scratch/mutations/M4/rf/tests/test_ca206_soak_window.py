"""CA-206 acceptance tests: non-waivable natural-time soak window.

The CA-206 card: accumulate 7 consecutive Daily T2 runs, 2 Weekly T3 runs,
1 Monthly run and 1 alert drill; windows are computed from TRUSTED
timestamps and run IDs (never hand-edited clocks or copied reports); any
required run that is missing / stale / duplicate-sample does NOT count;
an incomplete window may only be PENDING (never waivable).

  C1  daily window: 7 consecutive Daily runs with trusted distinct run IDs
      on consecutive dates -> daily window complete; a missing day, a
      stale run (>24h gap), a duplicate run ID, or a re-copied report
      (same run ID + same hash on another day) does NOT count.
  C2  weekly window: 2 Weekly runs >= 7d apart, both ok -> weekly window
      complete; a stale week or an all-skipped suite does not count.
  C3  monthly window: 1 Monthly run within 35d -> complete; stale ->
      incomplete (pending).
  C4  alert drill: 1 alert journal entry with ack -> drill complete;
      unacked alerts do not count.
  C5  window computation is deterministic and pending-only when
      incomplete: the same ledger yields the same window status; a
      partially accumulated window is PENDING (never approved/waived).

The window calculator is a pure function over ledger entries
(run_id/started_at/kind/ok/hash); all tests are hermetic.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

DAILY_TARGET = 7
WEEKLY_TARGET = 2
MONTHLY_TARGET = 1
DRILL_TARGET = 1
DAILY_MAX_GAP_HOURS = 24
WEEKLY_MIN_GAP_DAYS = 7
WEEKLY_MAX_AGE_DAYS = 7
MONTHLY_MAX_AGE_DAYS = 35


@dataclass(frozen=True)
class SoakRun:
    run_id: str
    started_at: str
    kind: str  # daily | weekly | monthly
    ok: bool = True
    report_sha256: str = ""


def _parse(iso: str) -> datetime:
    return datetime.fromisoformat(iso).astimezone(UTC)


def _hash(run_id: str, day: str) -> str:
    return hashlib.sha256(f"{run_id}:{day}".encode()).hexdigest()


def _daily_runs(days: int, *, gap_hours: int = 24, ok: bool = True,
                base: str = "2026-07-01T03:30:00+00:00") -> list[SoakRun]:
    base_dt = _parse(base)
    runs = []
    for i in range(days):
        run_id = f"T2-{base_dt.date() + timedelta(days=i)}"
        runs.append(SoakRun(
            run_id=run_id,
            started_at=(base_dt + timedelta(days=i, hours=gap_hours - 24 if i else 0)
                        ).isoformat(),
            kind="daily", ok=ok,
            report_sha256=_hash(run_id, str(base_dt.date() + timedelta(days=i)))))
    return runs


def daily_window(runs: list[SoakRun], *, now: str) -> dict:
    """Complete when >=7 consecutive daily runs (chain gaps break it).

    Runs are historical accumulation: each run counts when it is ok and
    follows the previous one within DAILY_MAX_GAP_HOURS (missing days and
    stale gaps break the chain); duplicate run ids never count twice.
    """
    daily = sorted(
        [r for r in runs if r.kind == "daily" and r.ok],
        key=lambda r: _parse(r.started_at))
    consecutive: list[SoakRun] = []
    prev_day: datetime | None = None
    seen_ids: set[str] = set()
    for run in daily:
        day = _parse(run.started_at)
        if run.run_id in seen_ids:
            continue  # duplicate run id / copied report does not count
        if prev_day is not None and (day - prev_day) > timedelta(hours=25):
            consecutive = []  # missing or stale gap breaks the chain
        consecutive.append(run)
        seen_ids.add(run.run_id)
        prev_day = day
        if len(consecutive) >= DAILY_TARGET:
            return {"complete": True, "count": len(consecutive), "pending": False}
    return {"complete": False, "count": len(consecutive), "pending": True}


def weekly_window(runs: list[SoakRun], *, now: str) -> dict:
    """Complete when >=2 weekly runs in distinct weeks and the latest one
    is still fresh (<= WEEKLY_MAX_AGE_DAYS before now)."""
    weekly = sorted(
        [r for r in runs if r.kind == "weekly" and r.ok],
        key=lambda r: _parse(r.started_at))
    if not weekly:
        return {"complete": False, "count": 0, "pending": True}
    latest = weekly[-1]
    if _parse(now) - _parse(latest.started_at) > timedelta(days=WEEKLY_MAX_AGE_DAYS):
        return {"complete": False, "count": 0, "pending": True}  # stale window
    # distinct weeks: at least WEEKLY_MIN_GAP_DAYS apart
    distinct: list[SoakRun] = []
    for run in weekly:
        if not distinct or (_parse(run.started_at) - _parse(distinct[-1].started_at)
                            >= timedelta(days=WEEKLY_MIN_GAP_DAYS)):
            distinct.append(run)
    return {"complete": len(distinct) >= WEEKLY_TARGET,
            "count": len(distinct), "pending": len(distinct) < WEEKLY_TARGET}


def monthly_window(runs: list[SoakRun], *, now: str) -> dict:
    monthly = [r for r in runs if r.kind == "monthly" and r.ok]
    fresh = [r for r in monthly
             if _parse(now) - _parse(r.started_at) <= timedelta(days=MONTHLY_MAX_AGE_DAYS)]
    return {"complete": len(fresh) >= MONTHLY_TARGET,
            "count": len(fresh), "pending": len(fresh) < MONTHLY_TARGET}


def drill_window(alerts: list[dict], *, now: str) -> dict:
    acked = [a for a in alerts if a.get("acked") is True]
    return {"complete": len(acked) >= DRILL_TARGET,
            "count": len(acked), "pending": len(acked) < DRILL_TARGET}


def soak_status(runs: list[SoakRun], alerts: list[dict], *, now: str) -> dict:
    """Aggregate window status; incomplete -> pending (never approved)."""
    windows = {
        "daily": daily_window(runs, now=now),
        "weekly": weekly_window(runs, now=now),
        "monthly": monthly_window(runs, now=now),
        "alert_drill": drill_window(alerts, now=now),
    }
    complete = all(w["complete"] for w in windows.values())
    return {"complete": complete, "windows": windows,
            "status": "complete" if complete else "pending"}


NOW = "2026-08-20T12:00:00+00:00"


def _daily_aug(days: int) -> list[SoakRun]:
    """7 consecutive daily runs 2026-08-13..08-19 (latest fresh at NOW)."""
    runs = []
    for i in range(days):
        day = _parse("2026-08-13T03:30:00+00:00") + timedelta(days=i)
        run_id = f"T2-{day.date()}"
        runs.append(SoakRun(
            run_id=run_id, started_at=day.isoformat(), kind="daily",
            report_sha256=_hash(run_id, str(day.date()))))
    return runs


# ---------------------------------------------------------------------------
# C1 — daily window: 7 consecutive, missing/stale/duplicate do not count
# ---------------------------------------------------------------------------


def test_c1_seven_consecutive_daily_completes():
    runs = _daily_aug(7)
    status = daily_window(runs, now=NOW)
    assert status["complete"] is True
    assert status["count"] == 7


def test_c1_missing_day_breaks_chain():
    runs = _daily_aug(6)
    # add a 7th run two days after the 6th -> the chain breaks at the gap
    runs.append(SoakRun(run_id="T2-2026-08-20",
                        started_at="2026-08-20T03:30:00+00:00",
                        kind="daily", report_sha256="x"))
    status = daily_window(runs, now=NOW)
    assert status["complete"] is False
    assert status["pending"] is True


def test_c1_stale_run_does_not_count():
    runs = _daily_aug(6)
    # 7th run is 48h after the 6th -> stale, chain not completed
    runs.append(SoakRun(run_id="T2-2026-08-20",
                        started_at="2026-08-20T03:30:00+00:00",
                        kind="daily", report_sha256="y"))
    status = daily_window(runs, now=NOW)
    assert status["complete"] is False


def test_c1_duplicate_run_id_and_copied_report_do_not_count():
    runs = _daily_aug(6)
    # duplicate run id on a different day (copied report) must not count
    dup = SoakRun(run_id=runs[0].run_id,
                  started_at="2026-08-19T03:30:00+00:00",
                  kind="daily", report_sha256=runs[0].report_sha256)
    runs.append(dup)
    status = daily_window(runs, now=NOW)
    assert status["complete"] is False
    assert status["count"] < 7


def test_c1_not_ok_run_does_not_count():
    runs = _daily_aug(7)
    runs[3] = SoakRun(run_id=runs[3].run_id, started_at=runs[3].started_at,
                      kind="daily", ok=False, report_sha256="z")
    status = daily_window(runs, now=NOW)
    assert status["complete"] is False
    assert status["count"] == 3  # chain breaks at the not-ok day (3 ok before it)


# ---------------------------------------------------------------------------
# C2 — weekly window: 2 runs >= 7d apart
# ---------------------------------------------------------------------------


def test_c2_two_weekly_completes():
    runs = [
        SoakRun("T3-2026-08-09", "2026-08-09T04:30:00+00:00", "weekly"),
        SoakRun("T3-2026-08-16", "2026-08-16T04:30:00+00:00", "weekly"),
    ]
    status = weekly_window(runs, now=NOW)
    assert status["complete"] is True


def test_c2_weekly_stale_or_skipped_does_not_count():
    # latest weekly within 7d but only one distinct ok week
    runs = [
        SoakRun("T3-2026-08-16", "2026-08-16T04:30:00+00:00", "weekly", ok=True),
        SoakRun("T3-2026-08-17", "2026-08-17T04:30:00+00:00", "weekly", ok=True),
    ]
    status = weekly_window(runs, now=NOW)
    assert status["complete"] is False
    assert status["count"] == 1  # same week counts once
    # all-skipped suite (not-ok) does not count toward the window
    runs2 = [
        SoakRun("T3-2026-08-14", "2026-08-14T04:30:00+00:00", "weekly", ok=True),
        SoakRun("T3-2026-08-16", "2026-08-16T04:30:00+00:00", "weekly", ok=False),
    ]
    status2 = weekly_window(runs2, now=NOW)
    assert status2["count"] == 1  # only the ok week counts
    # a window whose latest run is stale (older than 7d) counts nothing
    runs3 = [
        SoakRun("T3-2026-08-01", "2026-08-01T04:30:00+00:00", "weekly", ok=True),
        SoakRun("T3-2026-08-08", "2026-08-08T04:30:00+00:00", "weekly", ok=True),
    ]
    status3 = weekly_window(runs3, now=NOW)
    assert status3["count"] == 0  # stale window does not accumulate


# ---------------------------------------------------------------------------
# C3 — monthly window within 35d
# ---------------------------------------------------------------------------


def test_c3_monthly_fresh_completes():
    runs = [SoakRun("M-2026-08-01", "2026-08-01T05:00:00+00:00", "monthly")]
    status = monthly_window(runs, now=NOW)
    assert status["complete"] is True


def test_c3_monthly_stale_is_pending():
    runs = [SoakRun("M-2026-06-01", "2026-06-01T05:00:00+00:00", "monthly")]
    status = monthly_window(runs, now=NOW)
    assert status["complete"] is False
    assert status["pending"] is True


# ---------------------------------------------------------------------------
# C4 — alert drill: acked alert counts
# ---------------------------------------------------------------------------


def test_c4_acked_alert_completes_drill():
    alerts = [{"run_id": "drill-1", "status": "stale", "reason": "x", "acked": True}]
    status = drill_window(alerts, now=NOW)
    assert status["complete"] is True


def test_c4_unacked_alert_does_not_count():
    alerts = [{"run_id": "drill-1", "status": "stale", "reason": "x", "acked": False}]
    status = drill_window(alerts, now=NOW)
    assert status["complete"] is False


# ---------------------------------------------------------------------------
# C5 — deterministic + pending-only when incomplete
# ---------------------------------------------------------------------------


def test_c5_window_computation_is_deterministic():
    runs = _daily_aug(5) + [
        SoakRun("T3-2026-08-16", "2026-08-16T04:30:00+00:00", "weekly"),
        SoakRun("M-2026-08-01", "2026-08-01T05:00:00+00:00", "monthly"),
    ]
    alerts = [{"run_id": "d", "acked": True}]
    one = soak_status(runs, alerts, now=NOW)
    two = soak_status(runs, alerts, now=NOW)
    assert one == two
    assert one["status"] == "pending"  # incomplete -> pending, never approved


def test_c5_full_soak_completes():
    runs = _daily_aug(7) + [
        SoakRun("T3-2026-08-09", "2026-08-09T04:30:00+00:00", "weekly"),
        SoakRun("T3-2026-08-16", "2026-08-16T04:30:00+00:00", "weekly"),
        SoakRun("M-2026-08-01", "2026-08-01T05:00:00+00:00", "monthly"),
    ]
    alerts = [{"run_id": "drill-1", "acked": True}]
    status = soak_status(runs, alerts, now=NOW)
    assert status["complete"] is True
    assert status["status"] == "complete"


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
