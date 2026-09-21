"""I-14-B natural-time / observation-evidence classifier -- AFTER revision r2.

Attempt-local subject under test; production trees are NOT touched.

r2 fixes the two blocking findings of the independent review (changes_required):
  P1 -> J16 below;  P2 -> the natural observation intervals plus J15 below.
r1 is preserved byte-identically at harness/archive/natural_window.after-r1.py
(sha256 495a44111a854bd5b76d39aeae91d11ab789fe48bb8bcbc9ae3af4b87d8c5b95).

Frozen judgements implemented here (oracle.md section 2 plus the r2 addition in
oracle.md section 11); each is a single-line `if` tagged with its judgement id so
that a mutation harness can revert exactly one judgement in a scratch copy:

  J1  overlapping windows -> union, never the sum              (# J1)
  J2  the command total is not the observation duration        (# J2)
  J3  quick_check is outside the observation window            (# J3)
  J4  fewer than two samples -> unmeasured (null), not zero    (# J4)
  J4b no declared observation interval -> unmeasured            (# J4b)
  J5  every sample must lie inside the window                  (# J5)
  J6  no timestamp may be after the frozen evaluation instant  (# J6)
  J7  only a trusted clock source may complete a window        (# J7)
  J8  empty evidence hash does not count                       (# J8)
  J9  a duplicated run id does not count twice                 (# J9)
  J10 one instant is not a chain (calendar # J10a, login # J10b)
  J10c a second run on the same UTC day is ignored, not chained (# J10c)
  J11 a "complete" claim may not exceed the computed facts      (# J11)
  J12 a login label must sit at its own offset from the anchor (# J12)
  J13 all three labels must share one anchor event             (# J13)
  J14 a post-hoc log is not an immediate capture               (# J14)
  J15 a declared window may not cover the quick_check interval  (# J15)
  J16 the claim's basis must belong to a closed enumeration     (# J16)

Deliberately separated outputs: scheduled_at / started_at / first-last sampled_at
/ observation_finished_at / quick_check_seconds / command_total_seconds.  The
natural duration is taken over OBSERVATION intervals only; quick_check is never
one of them and is reported separately (`quick_check_in_observation_intervals`
=false).  The forbidden sum is reported only as `sum_seconds` +
`sum_used_for_natural_duration` = false, so no reader can mistake it for the
natural duration.

CLI:  natural_window.py --cases <in.json> --report <out.json>
      [--tolerance-seconds N] [--capture-tolerance-seconds N] [--frozen-now ISO]
Exit: 0 report written and every case decided, 2 malformed input (fail closed),
      4 internal error.  The anti-cheat gate lives in the oracle-side runner.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SUT_VERSION = "i14b-after-2"
TRUSTED_CLOCKS = {"system_utc", "scheduler_trusted"}
# J16 / P1: the claim's basis is a CLOSED enumeration.  A basis outside this set
# (unknown name, empty string, null or a missing key) refuses the claim instead of
# silently falling through and leaving every timing judgement unchecked.
BASIS_REGISTRY = {
    "sample_span",
    "command_total",
    "observation_plus_quick_check",
    "sum_of_windows",
    "union_of_windows",
}
LIVE_KIND = "live_ui_capture"
DAILY_GAP_SECONDS = 25 * 3600
WEEKLY_GAP_SECONDS = 7 * 86400
WEEKLY_MAX_AGE_SECONDS = 7 * 86400
MONTHLY_MAX_AGE_SECONDS = 35 * 86400


def _parse(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _secs(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds()


def _opt(fields: dict, key: str):
    value = fields.get(key)
    return _parse(value) if value else None


def _measure_union(intervals: list[tuple[datetime, datetime]]) -> float:
    if not intervals:
        return 0.0
    ordered = sorted(intervals)
    union = 0.0
    cur_start, cur_end = ordered[0]
    for start, end in ordered[1:]:
        if start <= cur_end:
            cur_end = max(cur_end, end)
        else:
            union += _secs(cur_start, cur_end)
            cur_start, cur_end = start, end
    union += _secs(cur_start, cur_end)
    return union


def _all_timestamps(fields: dict) -> list[datetime]:
    stamps: list[datetime] = []
    for key in ("scheduled_at", "started_at", "observation_finished_at",
                "quick_check_started_at", "quick_check_finished_at",
                "command_finished_at"):
        value = fields.get(key)
        if value:
            stamps.append(_parse(value))
    for value in fields.get("sampled_at") or []:
        stamps.append(_parse(value))
    for window in fields.get("windows") or []:
        stamps.append(_parse(window["started_at"]))
        stamps.append(_parse(window["finished_at"]))
    return stamps


# ---------------------------------------------------------------------------
# window accounting
# ---------------------------------------------------------------------------

def derive_window(fields: dict, frozen_now: datetime) -> tuple[dict, list[str]]:
    refusals: list[str] = []
    started = _parse(fields["started_at"])
    scheduled = _opt(fields, "scheduled_at")
    obs_finished = _opt(fields, "observation_finished_at")
    qc_started = _opt(fields, "quick_check_started_at")
    qc_finished = _opt(fields, "quick_check_finished_at")
    cmd_finished = _opt(fields, "command_finished_at")

    sample_stamps = [_parse(x) for x in (fields.get("sampled_at") or [])]
    outside = []
    if obs_finished is not None:
        outside = [s for s in sample_stamps if s < started or s > obs_finished]
    in_window = [s for s in sample_stamps if s not in outside]

    span = None
    if len(in_window) >= 2:
        span = _secs(min(in_window), max(in_window))

    quick_check = None
    if qc_started is not None and qc_finished is not None:
        quick_check = _secs(qc_started, qc_finished)

    command_total = None
    if cmd_finished is not None:
        command_total = _secs(started, cmd_finished)

    explicit = [
        (_parse(w["started_at"]), _parse(w["finished_at"]))
        for w in (fields.get("windows") or [])
    ]
    quick_check_interval = None
    if qc_started is not None and qc_finished is not None:
        quick_check_interval = (qc_started, qc_finished)

    # J15: no declared observation window may cover any part of the quick_check
    # interval.  A window that copies/splits the quick_check span is the same
    # defect as adding quick_check, only renamed.
    qc_overlap_seconds = 0.0
    if quick_check_interval is not None:
        for start, end in explicit or ([(started, obs_finished)] if obs_finished else []):
            low = max(start, quick_check_interval[0])
            high = min(end, quick_check_interval[1])
            if high > low:
                qc_overlap_seconds += _secs(low, high)

    # J1/J3/P2: the natural observation intervals contain the OBSERVATION phase
    # only.  quick_check is never an observation interval, whatever the claim's
    # basis is called.
    if explicit:
        intervals = explicit
    elif obs_finished is not None:
        intervals = [(started, obs_finished)]
    else:
        intervals = []

    sum_seconds = sum(_secs(a, b) for a, b in intervals)
    union = _measure_union(intervals)  # J1
    overlap = sum_seconds - union

    if outside:  # J5
        refusals.append("R-SAMPLE-OUTSIDE")
    if "sampled_at" in fields and len(in_window) < 2:  # J4
        refusals.append("R-NO-SAMPLES")
    if not intervals and span is None:  # J4b
        refusals.append("R-NO-INTERVAL")
    if qc_overlap_seconds > 0:  # J15
        refusals.append("R-QC-IN-OBS")
    if any(stamp > frozen_now for stamp in _all_timestamps(fields)):  # J6
        refusals.append("R-FUTURE-CLOCK")

    basis = (fields.get("_claim") or {}).get("basis")
    wanted = (fields.get("_claim") or {}).get("natural_observation_seconds")
    allowed = None
    if basis not in BASIS_REGISTRY:  # J16 / P1
        refusals.append("R-BASIS-UNKNOWN")
    elif basis == "sample_span":
        allowed = span
    elif basis == "union_of_windows":
        allowed = union
    elif basis == "sum_of_windows":
        allowed = sum_seconds
        if overlap > 0:  # J1 refusal
            refusals.append("R-SUM-OVERLAP")
    elif basis == "command_total":
        allowed = command_total
        if command_total is not None and span is not None and command_total > span:  # J2
            refusals.append("R-TOTAL-AS-OBS")
    elif basis == "observation_plus_quick_check":
        if span is not None and quick_check is not None:
            allowed = span + quick_check
        if quick_check is not None:  # J3
            refusals.append("R-QC-IN-OBS")
    if allowed is not None and wanted != allowed:  # J11
        refusals.append("R-CLAIM-EXCEEDS")

    computed = {
        "scheduled_at": fields.get("scheduled_at"),
        "started_at": fields.get("started_at"),
        "first_sampled_at": min(in_window).isoformat().replace("+00:00", "Z") if in_window else None,
        "last_sampled_at": max(in_window).isoformat().replace("+00:00", "Z") if in_window else None,
        "observation_finished_at": fields.get("observation_finished_at"),
        "observation_span_seconds": span,
        "sample_count": len(sample_stamps),
        "samples_outside_window": len(outside),
        "quick_check_seconds": quick_check,
        "command_total_seconds": command_total,
        "schedule_lag_seconds": _secs(scheduled, started) if scheduled else None,
        "observation_interval_count": len(intervals),
        "observation_intervals": [
            [a.isoformat().replace("+00:00", "Z"), b.isoformat().replace("+00:00", "Z")]
            for a, b in intervals
        ],
        "quick_check_in_observation_intervals": False,
        "quick_check_overlap_seconds": qc_overlap_seconds,
        "union_seconds": union,
        "sum_seconds": sum_seconds,
        "overlap_seconds": overlap,
        "basis": basis,
        "basis_registered": basis in BASIS_REGISTRY,
        "sum_used_for_natural_duration": False,
    }
    return computed, refusals


# ---------------------------------------------------------------------------
# natural calendar
# ---------------------------------------------------------------------------

def _eligible(entries: list[dict], frozen_now: datetime) -> tuple[list[dict], list[str]]:
    """Count-eligible entries plus EVERY raw-record violation found.

    Detection is per-entry and independent of the counting outcome: a record can
    violate several judgements at once (C1 violates J6, J8 and J10a together) and
    the report must name all of them, not just the first one encountered.
    """
    ordered = sorted(entries, key=lambda e: _parse(e["started_at"]))
    ok_entries = [e for e in ordered if e.get("ok") is True]
    instant_counts: dict[datetime, int] = {}
    for entry in ok_entries:
        key = _parse(entry["started_at"])
        instant_counts[key] = instant_counts.get(key, 0) + 1
    first_index: dict[str, int] = {}
    for index, entry in enumerate(ordered):
        first_index.setdefault(str(entry.get("run_id")), index)

    kept: list[dict] = []
    codes: list[str] = []
    for index, entry in enumerate(ordered):
        if entry.get("ok") is not True:
            continue
        entry_codes: list[str] = []
        if not entry.get("report_sha256"):                      # J8
            entry_codes.append("R-EMPTY-EVIDENCE")
        if _parse(entry["started_at"]) > frozen_now:            # J6
            entry_codes.append("R-FUTURE-CLOCK")
        if first_index.get(str(entry.get("run_id"))) != index:  # J9
            entry_codes.append("R-DUP-RUN-ID")
        if instant_counts.get(_parse(entry["started_at"]), 0) > 1:  # J10a
            entry_codes.append("R-SAME-INSTANT")
        codes.extend(entry_codes)
        if not entry_codes:
            kept.append(entry)
    return kept, sorted(set(codes))


def derive_calendar(fields: dict, frozen_now: datetime) -> tuple[dict, list[str]]:
    refusals: list[str] = []
    ledger = fields.get("ledger") or {}

    daily, daily_ref = _eligible(ledger.get("daily") or [], frozen_now)
    best = 0
    chain = 0
    prev_date = None
    prev_dt = None
    same_day_dropped = 0
    for entry in daily:
        when = _parse(entry["started_at"])
        day = when.date()
        if prev_date is not None and day == prev_date:  # J10c
            same_day_dropped += 1
            continue
        if prev_date is not None and _secs(prev_dt, when) > DAILY_GAP_SECONDS:
            chain = 0
        chain += 1
        best = max(best, chain)
        prev_date, prev_dt = day, when

    weekly, weekly_ref = _eligible(ledger.get("weekly") or [], frozen_now)
    weekly_count = 0
    if weekly:
        latest = _parse(weekly[-1]["started_at"])
        if _secs(latest, frozen_now) <= WEEKLY_MAX_AGE_SECONDS:
            distinct: list[datetime] = []
            for entry in weekly:
                when = _parse(entry["started_at"])
                if not distinct or _secs(distinct[-1], when) >= WEEKLY_GAP_SECONDS:
                    distinct.append(when)
            weekly_count = len(distinct)

    monthly, monthly_ref = _eligible(ledger.get("monthly") or [], frozen_now)
    monthly_count = sum(
        1 for entry in monthly
        if _secs(_parse(entry["started_at"]), frozen_now) <= MONTHLY_MAX_AGE_SECONDS
    )

    alert_count = sum(1 for a in (ledger.get("alerts") or []) if a.get("acked") is True)

    refusals += daily_ref + weekly_ref + monthly_ref
    clock_source = fields.get("clock_source")
    if clock_source not in TRUSTED_CLOCKS:  # J7
        refusals.append("R-SIMULATED-CLOCK")

    complete = (best >= 7 and weekly_count >= 2 and monthly_count >= 1 and alert_count >= 1)
    computed_status = "complete" if complete else "pending"
    claim_status = (fields.get("_claim") or {}).get("status")
    if claim_status == "complete" and computed_status != "complete":  # J11
        refusals.append("R-CLAIM-EXCEEDS")

    computed = {
        "daily_count": best,
        "daily_same_day_runs_dropped": same_day_dropped,
        "weekly_count": weekly_count,
        "monthly_count": monthly_count,
        "alert_count": alert_count,
        "window_status": computed_status,
        "clock_source": clock_source,
    }
    return computed, refusals


# ---------------------------------------------------------------------------
# login anchors
# ---------------------------------------------------------------------------

def derive_login(fields: dict, tol: float, cap_tol: float,
                 frozen_now: datetime) -> tuple[dict, list[str]]:
    refusals: list[str] = []
    check = fields.get("login_check") or {}
    anchor = check.get("anchor_event") or {}
    anchor_at = _parse(anchor["anchor_at"]) if anchor.get("anchor_at") else None
    labels = check.get("labels") or []

    offsets: list[int] = []
    errors: list[float] = []
    latencies: list[float] = []
    anchor_ids: set[str] = set()
    posthoc = False
    sampled_stamps: list[datetime] = []
    captured_stamps: list[datetime] = []
    for label in labels:
        sampled = _parse(label["sampled_at"])
        captured = _parse(label["captured_at"]) if label.get("captured_at") else sampled
        sampled_stamps.append(sampled)
        captured_stamps.append(captured)
        if anchor_at is not None:
            offset = _secs(anchor_at, sampled)
            offsets.append(int(round(offset)))
            errors.append(abs(offset - float(label["name"])))
        anchor_ids.add(str(label.get("anchor_event_id", anchor.get("event_id"))))
        latencies.append(_secs(sampled, captured))
        if label.get("evidence_kind") != LIVE_KIND:
            posthoc = True

    max_error = max(errors) if errors else None
    max_latency = max(latencies) if latencies else None
    shared = len(anchor_ids) == 1

    if anchor_at is not None and max_error is not None and max_error > tol:  # J12
        refusals.append("R-LABEL-ANCHOR")
    if not shared:  # J13
        refusals.append("R-ANCHOR-NOT-SHARED")
    if len(sampled_stamps) != len(set(sampled_stamps)):  # J10b
        refusals.append("R-SAME-INSTANT")
    if posthoc or (max_latency is not None and max_latency > cap_tol):  # J14
        refusals.append("R-POSTHOC-CAPTURE")
    if any(stamp > frozen_now for stamp in sampled_stamps + captured_stamps):  # J6
        refusals.append("R-FUTURE-CLOCK")

    computed = {
        "anchor_event_id": anchor.get("event_id"),
        "shared_anchor_event_id": sorted(anchor_ids)[0] if shared and anchor_ids else None,
        "label_offsets_seconds": offsets,
        "label_offset_max_error_seconds": max_error,
        "capture_latency_max_seconds": max_latency,
        "label_count": len(labels),
    }
    return computed, refusals


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------

def classify(case: dict, frozen_now: datetime, tol: float, cap_tol: float) -> dict:
    klass = case.get("class")
    fields = dict(case.get("fields") or {})
    fields["_claim"] = case.get("claim") or {}
    refusals: list[str] = []
    computed: dict = {}

    if klass == "window_accounting":
        computed, refusals = derive_window(fields, frozen_now)
    elif klass == "calendar":
        computed, refusals = derive_calendar(fields, frozen_now)
    elif klass == "login_anchor":
        computed, refusals = derive_login(fields, tol, cap_tol, frozen_now)
    else:
        refusals = ["R-UNKNOWN_CLASS"]

    verdict = "accept_claim" if not refusals else "reject_claim"
    return {
        "case_id": case.get("case_id"),
        "class": klass,
        "requirement_id": case.get("requirement_id"),
        "verdict": verdict,
        "refusals": sorted(set(refusals)),
        "computed": computed,
        "claim": case.get("claim"),
        "note": case.get("note"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--tolerance-seconds", type=float, default=5.0)
    ap.add_argument("--capture-tolerance-seconds", type=float, default=5.0)
    ap.add_argument("--frozen-now", default=None)
    args = ap.parse_args(argv)

    try:
        doc = json.loads(Path(args.cases).read_text(encoding="utf-8"))
        cases = doc["cases"]
        frozen_now = _parse(args.frozen_now or doc["frozen_now_utc"])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": "malformed_input", "detail": str(exc)}))
        return 2

    try:
        verdicts = [classify(c, frozen_now, args.tolerance_seconds,
                             args.capture_tolerance_seconds) for c in cases]
    except Exception as exc:
        print(json.dumps({"ok": False, "error": "internal_error", "detail": str(exc)}))
        return 4

    report = {
        "ok": True,
        "sut_version": SUT_VERSION,
        "case_count": len(verdicts),
        "tolerance_seconds_input": args.tolerance_seconds,
        "capture_tolerance_seconds_input": args.capture_tolerance_seconds,
        "frozen_now_utc": frozen_now.isoformat().replace("+00:00", "Z"),
        "trusted_clock_sources": sorted(TRUSTED_CLOCKS),
        "verdicts": verdicts,
        "accepted_claim_count": sum(1 for v in verdicts if v["verdict"] == "accept_claim"),
        "refusal_code_count": sum(len(v["refusals"]) for v in verdicts),
    }
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(out), "case_count": len(verdicts),
                      "accepted_claim_count": report["accepted_claim_count"],
                      "sut_version": SUT_VERSION}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
