"""I-14-B natural-time / observation-evidence classifier -- BASELINE (pre-fix) revision.

This file is the attempt-local subject under test, not production code.  The
revision you are reading is the BEFORE revision: it implements the accounting
that the audit found in the history (see oracle.md section 2 for the exact
counterexamples it must eventually satisfy).

Deliberate properties of this BEFORE revision (each one is a documented defect,
not an accident):

  B1  a single "elapsed" number is reported; scheduled_at / started_at /
      sampled_at / observation_finished_at / quick_check / command total are
      collapsed into it, so no reader can tell them apart.
  B2  the collapsed number is the COMMAND TOTAL, i.e. the continuous
      observation window silently contains quick_check.
  B3  overlapping windows are ADDED (sum), never merged (union).
  B4  the claim is accepted whenever the claimed number equals the collapsed
      number; the claim's own "basis" is not inspected at all.
  B5  a single sample yields 0 seconds instead of "unmeasured".
  B6  the calendar rules accept future timestamps, empty evidence hashes and
      several entries sharing one instant; a simulated clock is not looked at.
  B7  the login labels are reported but never checked against the anchor, and a
      post-hoc log is accepted as if it were an immediate capture.
  B8  no refusal code is ever produced, so the report cannot distinguish
      "verified" from "not looked at".

CLI:  natural_window.py --cases <in.json> --report <out.json>
      [--tolerance-seconds N] [--capture-tolerance-seconds N] [--frozen-now ISO]
Exit: 0 report written, 2 malformed input (fail closed), 4 internal error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SUT_VERSION = "i14b-before-1"


def _parse(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _secs(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds()


# ---------------------------------------------------------------------------
# window accounting (B1/B2/B3/B5)
# ---------------------------------------------------------------------------

def derive_window(fields: dict) -> dict:
    started = _parse(fields["started_at"])
    finished = fields.get("command_finished_at") or fields.get("observation_finished_at")
    observed = {}

    if finished is not None:
        observed["elapsed_seconds"] = _secs(started, _parse(finished))
    elif fields.get("windows"):
        observed["elapsed_seconds"] = 0.0
    else:
        observed["elapsed_seconds"] = 0.0

    if fields.get("windows"):
        total = 0.0
        for w in fields["windows"]:
            total += _secs(_parse(w["started_at"]), _parse(w["finished_at"]))
        observed["elapsed_seconds"] = total

    samples = fields.get("sampled_at") or []
    observed["sample_count"] = len(samples)
    if len(samples) == 1:
        observed["elapsed_seconds"] = 0.0
    return observed


# ---------------------------------------------------------------------------
# calendar (B6): the rules the historical acceptance function used
# ---------------------------------------------------------------------------

def _daily_chain(daily: list[dict]) -> int:
    entries = sorted(
        [e for e in daily if e.get("ok") is True],
        key=lambda e: _parse(e["started_at"]),
    )
    chain = 0
    prev = None
    seen: set[str] = set()
    for e in entries:
        if e["run_id"] in seen:
            continue
        when = _parse(e["started_at"])
        if prev is not None and _secs(prev, when) > 25 * 3600:
            chain = 0
        chain += 1
        seen.add(e["run_id"])
        prev = when
    return chain


def derive_calendar(fields: dict, frozen_now: datetime) -> dict:
    ledger = fields.get("ledger") or {}
    daily_count = _daily_chain(ledger.get("daily") or [])

    weekly = sorted(
        [e for e in (ledger.get("weekly") or []) if e.get("ok") is True],
        key=lambda e: _parse(e["started_at"]),
    )
    distinct = []
    for e in weekly:
        when = _parse(e["started_at"])
        if not distinct or _secs(_parse(distinct[-1]["started_at"]), when) >= 7 * 86400:
            distinct.append(e)
    weekly_ok = len(distinct) >= 2

    monthly = [e for e in (ledger.get("monthly") or []) if e.get("ok") is True]
    monthly_ok = len(monthly) >= 1

    alerts = [a for a in (ledger.get("alerts") or []) if a.get("acked") is True]
    drill_ok = len(alerts) >= 1

    complete = daily_count >= 7 and weekly_ok and monthly_ok and drill_ok
    return {
        "daily_count": daily_count,
        "window_status": "complete" if complete else "pending",
    }


# ---------------------------------------------------------------------------
# login anchors (B7)
# ---------------------------------------------------------------------------

def derive_login(fields: dict, tol: float, cap_tol: float, frozen_now: datetime) -> dict:
    check = fields.get("login_check") or {}
    anchor = check.get("anchor_event") or {}
    anchor_at = _parse(anchor["anchor_at"]) if anchor.get("anchor_at") else None
    offsets = []
    for label in check.get("labels") or []:
        if anchor_at is None:
            offsets.append(None)
            continue
        offsets.append(int(round(_secs(anchor_at, _parse(label["sampled_at"])))))
    return {"label_offsets_seconds": offsets}


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------

def classify(case: dict, frozen_now: datetime, tol: float, cap_tol: float) -> dict:
    klass = case.get("class")
    fields = case.get("fields") or {}
    claim = case.get("claim") or {}
    refusals: list[str] = []
    computed: dict = {}

    if klass == "window_accounting":
        computed = derive_window(fields)
        wanted = claim.get("natural_observation_seconds")
        verdict = "accept_claim" if wanted == computed.get("elapsed_seconds") else "reject_claim"
    elif klass == "calendar":
        computed = derive_calendar(fields, frozen_now)
        verdict = (
            "accept_claim"
            if claim.get("status") == computed.get("window_status")
            else "reject_claim"
        )
    elif klass == "login_anchor":
        computed = derive_login(fields, tol, cap_tol, frozen_now)
        verdict = "accept_claim"
    else:
        computed = {}
        verdict = "reject_claim"

    return {
        "case_id": case.get("case_id"),
        "class": klass,
        "requirement_id": case.get("requirement_id"),
        "verdict": verdict,
        "refusals": sorted(refusals),
        "computed": computed,
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
    except Exception as exc:  # malformed input -> fail closed
        print(json.dumps({"ok": False, "error": "malformed_input", "detail": str(exc)}))
        return 2

    try:
        verdicts = [classify(c, frozen_now, args.tolerance_seconds,
                             args.capture_tolerance_seconds) for c in cases]
    except Exception as exc:  # internal error
        print(json.dumps({"ok": False, "error": "internal_error", "detail": str(exc)}))
        return 4

    report = {
        "ok": True,
        "sut_version": SUT_VERSION,
        "case_count": len(verdicts),
        "tolerance_seconds_input": args.tolerance_seconds,
        "capture_tolerance_seconds_input": args.capture_tolerance_seconds,
        "frozen_now_utc": frozen_now.isoformat().replace("+00:00", "Z"),
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
