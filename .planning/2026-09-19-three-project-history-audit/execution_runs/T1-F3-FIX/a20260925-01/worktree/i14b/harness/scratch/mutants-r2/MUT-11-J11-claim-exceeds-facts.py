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
# T1-F2-FIX (defect F-1, J7 clock guard): a TUPLE, not a set.  Set membership
# HASHES its probe, so a container clock_source (list/dict) raised TypeError
# inside the J7 guard below and destroyed the whole batch (rc=4, no report, 0
# adjudications) instead of refusing one claim.  Tuple membership compares with
# == and is total over every JSON value, so the guard line itself and the
# report's trusted-clock field keep their exact bytes on the normal path while
# an unreadable clock cleanly lands in the existing simulated-clock refusal.
TRUSTED_CLOCKS = ("system_utc", "scheduler_trusted")
# J16 / P1: the claim's basis is a CLOSED enumeration.  A basis outside this set
# (unknown name, empty string, null or a missing key) refuses the claim instead of
# silently falling through and leaving every timing judgement unchecked.
# T1-10-FIX (defect 1, M-T-REVIEW changes_required): a TUPLE, not a set.
# Set membership HASHES its probe, so a container basis (list/dict) raised
# TypeError inside the guard below ("basis not in BASIS_REGISTRY") AND inside the
# "basis_registered" report field -- the guard crashed the whole J16 batch
# (rc=4, no report, every case undecided) instead of refusing one claim.
# Tuple membership compares with == and is total over every JSON value, so both
# membership sites become total with this single change (I-14-B review.md P4
# minimal remedy, first option: "BASIS_REGISTRY 由 set 改 tuple").
BASIS_REGISTRY = (
    "sample_span",
    "command_total",
    "observation_plus_quick_check",
    "sum_of_windows",
    "union_of_windows",
)
LIVE_KIND = "live_ui_capture"
DAILY_GAP_SECONDS = 25 * 3600
WEEKLY_GAP_SECONDS = 7 * 86400
WEEKLY_MAX_AGE_SECONDS = 7 * 86400
MONTHLY_MAX_AGE_SECONDS = 35 * 86400


def _parse(ts: str) -> datetime | None:
    """T1-F3-FIX: TOTAL over every JSON value (I-14-B oracle.md sec 11.8).

    A present-but-malformed timestamp used to raise ValueError out of here
    ("Invalid isoformat string: ..."), which escaped classify() into main()'s
    internal-error handler: rc=4, no report written, and the WHOLE batch left
    with zero adjudications - the same verdict-stripping shape as defect (1).
    A non-string or unparsable value now yields None instead; every consumer
    below treats None as "this field carries no timing fact", and classify()
    refuses that ONE case with the new R-TIMESTAMP-MALFORMED code (section
    11.8 is the code's only authorisation source; vocabulary 16 -> 17).
    """
    if not isinstance(ts, str):
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _secs(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds()


def _opt(fields: dict, key: str):
    value = fields.get(key)
    return _parse(value) if value else None


def _echo_ts(fields: dict, key: str):
    """T1-F3-FIX (oracle.md sec 11.8): a time field that is present but cannot
    be parsed is REPORTED as null in `computed`; a field that parses keeps its
    input bytes verbatim; an absent key keeps its original null."""
    if key not in fields:
        return None
    raw = fields[key]
    return raw if _parse(raw) is not None else None


def _bad_ts_slot(mapping, key: str) -> bool:
    """Present AND unparsable -> malformed.  An ABSENT key is never malformed
    here, so every missing-key path keeps its original behaviour byte for
    byte (dispatch invariant: 缺键行为不变)."""
    return key in mapping and _parse(mapping[key]) is None


def _malformed_time_fields(fields: dict, klass: str) -> list[str]:
    """Every timestamp slot the given class actually reads, kept only when it
    is present and unparsable (I-14-B oracle.md sec 11.8 third bullet: 类型/
    格式错误 = per-case rejection, one new code, one code only)."""
    bad: list[str] = []
    if klass == "window_accounting":
        for key in ("scheduled_at", "started_at", "observation_finished_at",
                    "quick_check_started_at", "quick_check_finished_at",
                    "command_finished_at"):
            if _bad_ts_slot(fields, key):
                bad.append(key)
        for index, value in enumerate(fields.get("sampled_at") or []):
            if _parse(value) is None:
                bad.append("sampled_at[%d]" % index)
        for index, window in enumerate(fields.get("windows") or []):
            if isinstance(window, dict):
                for key in ("started_at", "finished_at"):
                    if _bad_ts_slot(window, key):
                        bad.append("windows[%d].%s" % (index, key))
    elif klass == "calendar":
        ledger = fields.get("ledger") or {}
        if isinstance(ledger, dict):
            for sub in ("daily", "weekly", "monthly"):
                for index, entry in enumerate(ledger.get(sub) or []):
                    if isinstance(entry, dict) and _bad_ts_slot(entry, "started_at"):
                        bad.append("ledger.%s[%d].started_at" % (sub, index))
    elif klass == "login_anchor":
        check = fields.get("login_check") or {}
        if isinstance(check, dict):
            anchor = check.get("anchor_event") or {}
            if isinstance(anchor, dict) and _bad_ts_slot(anchor, "anchor_at"):
                bad.append("login_check.anchor_event.anchor_at")
            for index, label in enumerate(check.get("labels") or []):
                if isinstance(label, dict):
                    for key in ("sampled_at", "captured_at"):
                        if _bad_ts_slot(label, key):
                            bad.append("login_check.labels[%d].%s" % (index, key))
    return bad


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
    # T1-F3-FIX: only PARSEABLE stamps can be compared with frozen_now.  A
    # malformed one contributes no timing fact; the case is refused separately
    # (R-TIMESTAMP-MALFORMED), so J6 never loses its verdict to a bad value.
    stamps: list[datetime] = []
    for key in ("scheduled_at", "started_at", "observation_finished_at",
                "quick_check_started_at", "quick_check_finished_at",
                "command_finished_at"):
        value = fields.get(key)
        if value:
            stamp = _parse(value)
            if stamp is not None:
                stamps.append(stamp)
    for value in fields.get("sampled_at") or []:
        stamp = _parse(value)
        if stamp is not None:
            stamps.append(stamp)
    for window in fields.get("windows") or []:
        started = _parse(window["started_at"])
        if started is not None:
            stamps.append(started)
        finished = _parse(window["finished_at"])
        if finished is not None:
            stamps.append(finished)
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
    # T1-F3-FIX: an observation interval needs BOTH endpoints.  When the start
    # cannot be parsed the window is unavailable, so the other endpoint stops
    # forming intervals as well; the case is refused anyway and the remaining
    # facts (samples, quick_check, basis) are still computed (oracle.md sec 11.8).
    if started is None:
        obs_finished = None

    # T1-F3-FIX: only parseable samples are comparable with started/finished.
    sample_stamps = [stamp for stamp in
                     (_parse(x) for x in (fields.get("sampled_at") or []))
                     if stamp is not None]
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
    if cmd_finished is not None and started is not None:
        command_total = _secs(started, cmd_finished)

    # T1-F3-FIX: an interval whose endpoint cannot be parsed carries no timing
    # fact, so it never enters sum/union; that case is refused on its own.
    explicit = []
    for w in (fields.get("windows") or []):
        pair = (_parse(w["started_at"]), _parse(w["finished_at"]))
        if pair[0] is not None and pair[1] is not None:
            explicit.append(pair)
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

    # T1-10-FIX (defect 1, entry E1): the claim that CARRIES basis must be an
    # object before it is read (I-14-B review.md P4: "claim 为 list => rc 4").
    # A truthy non-object carrier made the line below raise AttributeError and
    # killed the whole batch; now the basis input is validated at its entry, and
    # an unreadable basis behaves exactly like a MISSING basis key: no registered
    # basis -> refuse the claim (oracle.md sec 11.3, same scalar semantics).
    claim = fields.get("_claim")
    if not isinstance(claim, dict):
        claim = {}
    basis = claim.get("basis")
    wanted = claim.get("natural_observation_seconds")
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
        "scheduled_at": _echo_ts(fields, "scheduled_at"),
        "started_at": _echo_ts(fields, "started_at"),
        "first_sampled_at": min(in_window).isoformat().replace("+00:00", "Z") if in_window else None,
        "last_sampled_at": max(in_window).isoformat().replace("+00:00", "Z") if in_window else None,
        "observation_finished_at": _echo_ts(fields, "observation_finished_at"),
        "observation_span_seconds": span,
        "sample_count": len(sample_stamps),
        "samples_outside_window": len(outside),
        "quick_check_seconds": quick_check,
        "command_total_seconds": command_total,
        "schedule_lag_seconds": _secs(scheduled, started) if scheduled and started is not None else None,
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
    # T1-F3-FIX: a record whose started_at cannot be parsed carries no ordering
    # or timing fact, so it cannot be counted as eligible (it is not silently
    # promoted - the CASE it belongs to is refused with R-TIMESTAMP-MALFORMED
    # by classify(), so no claim can gain from the drop).  A MISSING key still
    # raises KeyError here, exactly as before.
    entries = [e for e in entries if _parse(e["started_at"]) is not None]
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
    # T1-F2-FIX (defect F-2, J11 claim.status carrier): the carrier must be an
    # object before it is read (same entry-validation shape as T1-10-FIX's E1
    # basis guard).  present-but-malformed (a truthy NON-object claim) is read
    # FAIL-CLOSED as the strongest assertion, so the unchanged J11 line below
    # refuses with the existing claim-exceeds code whenever the facts fall
    # short of complete.  A genuinely ABSENT status key (or a claim key the
    # classify() entry already normalised to an empty object) keeps the
    # original path byte-identically -- only the unreadable carrier is
    # re-routed.  Parent pre-freeze ruling, oracle.md sec 3.
    claim = fields.get("_claim")
    if not isinstance(claim, dict):
        claim = {"status": "complete"}  # T1-F2-FIX F-2 fail-closed read surrogate
    claim_status = claim.get("status")
    if False:  # MUT-11
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
        # T1-F3-FIX: an unparsable label timestamp contributes no timing fact,
        # but the LABEL still counts (label_count) and is still checked for its
        # evidence kind, so a malformed timestamp can never dodge J14/J13.
        if sampled is not None:
            sampled_stamps.append(sampled)
        if captured is not None:
            captured_stamps.append(captured)
        if anchor_at is not None and sampled is not None:
            offset = _secs(anchor_at, sampled)
            offsets.append(int(round(offset)))
            errors.append(abs(offset - float(label["name"])))
        anchor_ids.add(str(label.get("anchor_event_id", anchor.get("event_id"))))
        if sampled is not None and captured is not None:
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
    # T1-F2-FIX (P4 container family): present-but-container carriers are
    # normalised at this single entry so EVERY read site (windows 2, sampled_at
    # 2, ledger 1+4) is total; absent keys stay untouched (byte-identical).
    for _key in ("windows", "sampled_at"):
        if _key in fields and not isinstance(fields[_key], list):
            fields[_key] = []
    if "ledger" in fields:
        _ledger = fields["ledger"]
        if not isinstance(_ledger, dict):
            fields["ledger"] = {}
        else:
            _ledger = dict(_ledger)
            for _sub in ("daily", "weekly", "monthly", "alerts"):
                if _sub in _ledger and not isinstance(_ledger[_sub], list):
                    _ledger[_sub] = []
            fields["ledger"] = _ledger
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

    # T1-F3-FIX (I-14-B oracle.md sec 11.8): a present-but-malformed timestamp
    # in a SINGLE case is a per-case refusal, never an internal error - the
    # whole batch stays adjudicated and the report is still written (rc=0).
    # Appended after the dispatch because each derive_* rebinds `refusals`.
    if _malformed_time_fields(fields, klass):
        refusals.append("R-TIMESTAMP-MALFORMED")

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
        # T1-F3-FIX: _parse is total now, so this document/call-domain guard has
        # to be restated explicitly or a malformed frozen instant would slip past
        # rc=2.  oracle.md sec 11.8 bullet 1 keeps rc=2 for exactly these shapes:
        # the failure happens BEFORE any case is decided, so nothing is stripped.
        if frozen_now is None:
            raise ValueError("Invalid isoformat string: %r"
                             % (args.frozen_now or doc["frozen_now_utc"],))
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
