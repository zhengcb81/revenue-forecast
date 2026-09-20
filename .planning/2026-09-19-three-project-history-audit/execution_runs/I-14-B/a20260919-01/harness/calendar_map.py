"""I-14-B requirement-id -> I-17 calendar mapping (READ-ONLY evidence).

Every row is anchored by SEARCHING the source file for a distinctive literal, so
line numbers and quoted text are produced by the script, never hand-copied.  The
script also re-reads the real assurance manifests that already exist in the
product tree so that the calendar distinguishes "a real artifact exists" from
"the window is complete".

Nothing here may set started_at / due_at: I-17-A starts the clock from the real
run, and an unfrozen document date must never be used as the observation start.

Usage:
  <iso-python> -X utf8 -B harness/calendar_map.py --out evidence/calendar_mapping.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
PLAN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit")
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")

AUG09 = RF / "audit_review" / "2026-08-09_full_completion_assurance_plan" / "task_plan.md"
CA206 = RF / "tests" / "test_ca206_soak_window.py"
WIKI_LEGACY = PLAN / "reviews" / "wiki_legacy" / "review.md"
REVENUE_REVIEW = PLAN / "reviews" / "revenue" / "review.md"
AUG09_CASES = PLAN / "reviews" / "aug09_plans" / "manual_cases.json"

# (row_id, requirement_id_short, cadence, minimum, file, search literal, why)
ROWS = [
    ("CAL-01", "CA-206 daily (T2)", "daily", "7 consecutive days",
     CA206, "DAILY_TARGET = 7",
     "original non-waivable soak window; the acceptance function is a pure function today"),
    ("CAL-02", "CA-206 weekly (T3)", "weekly", "2 runs, >= 7 d apart",
     CA206, "WEEKLY_TARGET = 2",
     "original non-waivable soak window"),
    ("CAL-03", "CA-206 monthly", "monthly", "1 run within 35 d",
     CA206, "MONTHLY_TARGET = 1",
     "original non-waivable soak window"),
    ("CAL-04", "CA-206 alert drill", "event", "1 acknowledged alert",
     CA206, "DRILL_TARGET = 1",
     "alert drill must fire and be acknowledged"),
    ("CAL-05", "FC-1102 daily read-only runner", "daily", ">= 1 per day",
     AUG09, "FC-1102",
     "daily production read-only T2 runner writes only an audit report"),
    ("CAL-06", "Phase 11 exit gate (2 daily windows)", "daily", "2 consecutive daily T2 periods",
     AUG09, "连续至少",
     "exit gate that the original plan itself left unaccumulated"),
    ("CAL-07", "FC-1103 weekly real-provider runner", "weekly", "1 per week",
     AUG09, "FC-1103",
     "weekly isolated CN/HK/US provider run"),
    ("CAL-08", "FC-1104 release gate freshness", "rolling", "T2 within 24 h AND T3 within 7 d",
     AUG09, "FC-1104",
     "release gate consumes the natural windows"),
    ("CAL-09", "FC-1504 observation period + rollback drill", "daily+weekly",
     "2 x >=24 h T2 plus 7 d T3 plus one rollback drill",
     AUG09, "FC-1504：",
     "the original observation-period obligation"),
    ("CAL-10", "Phase 14 R2 two-cycle shadow diff", "2 cycles", "2 cycles fully explained",
     AUG09, "| R2 |",
     "wave entry/exit condition"),
    ("CAL-11", "Phase 14 R8 legacy bridge off", "daily", "two >= 24 h zero-hit periods",
     AUG09, "| R8 |",
     "wave entry condition"),
    ("CAL-12", "Phase 14 R9 delete v1/legacy code", "1 cycle", "one further observation cycle",
     AUG09, "| R9 |",
     "wave entry condition"),
    ("CAL-13", "WR login 30/60/120 immediacy (company-wiki)", "event-anchored",
     "3 labels on ONE login anchor within tolerance",
     WIKI_LEGACY, "30/60/120",
     "immediate-UI evidence; BLOCKED here (no capture capability, no frozen tolerance)"),
    ("CAL-14", "slow canary > 900 s must stay a real-time gate", "long-run",
     ">= 900 s real duration (縮時 must not be renamed)",
     WIKI_LEGACY, ">900 秒",
     "compressed-time substitutes must not be presented as the real long gate"),
    ("CAL-15", "A09-055 two daily windows still outstanding", "daily", "2 daily windows",
     AUG09_CASES, '"case_id": "A09-055"',
     "the audit recorded that the double-daily window was still unaccumulated"),
    ("CAL-16", "A09-056 Phase 12/13 quality+capacity", "n/a (perf)", "not a natural window",
     AUG09_CASES, '"case_id": "A09-056"',
     "recorded so it is not silently merged into the natural-time calendar"),
    ("CAL-17", "CA-206 review conclusion (pure-function substitute)", "n/a (finding)", "n/a",
     REVENUE_REVIEW, "CA-206",
     "the finding that a pure function replaced the real observation"),
]

MANIFESTS = {
    "daily_manifest.json": RF / "assurance" / "runs" / "daily_manifest.json",
    "weekly_manifest.json": RF / "assurance" / "runs" / "weekly_manifest.json",
    "monthly_manifest.json": RF / "assurance" / "runs" / "monthly_manifest.json",
    "legacy_periods.json": RF / "assurance" / "runs" / "legacy_periods.json",
    "daily_alert.jsonl": RF / "assurance" / "runs" / "daily_alert.jsonl",
}


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_anchor(path: Path, literal: str) -> dict:
    if not path.is_file():
        return {"found": False, "reason": "file missing"}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for number, line in enumerate(lines, start=1):
        if literal in line:
            return {"found": True, "line_number": number, "line_text": line.strip()[:400]}
    return {"found": False, "reason": f"literal not present: {literal}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ATTEMPT / "evidence" / "calendar_mapping.json"))
    args = ap.parse_args()

    calendar = []
    for row_id, requirement, cadence, minimum, path, literal, why in ROWS:
        anchor = find_anchor(path, literal)
        calendar.append({
            "row_id": row_id,
            "requirement_id": requirement,
            "cadence": cadence,
            "minimum": minimum,
            "source_path": str(path),
            "source_sha256": sha256_file(path),
            "anchor": anchor,
            "why": why,
            "started_at": None,
            "due_at": None,
            "status": "pending",
            "status_reason": ("no real start recorded; I-17-A starts the clock from the actual run. "
                              "A due date must never be computed from this document's date, and a "
                              "simulated clock may not advance a window."),
            "measured_here": False,
        })

    observed = {}
    for name, path in MANIFESTS.items():
        record = {"path": str(path), "sha256": sha256_file(path), "exists": path.is_file()}
        if path.is_file() and path.suffix == ".json":
            record["content"] = json.loads(path.read_text(encoding="utf-8"))
        elif path.is_file():
            record["line_count"] = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        observed[name] = record

    daily = observed["daily_manifest.json"].get("content", {})
    doc = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "calendar_state": "ALL ROWS PENDING -- no real natural window is started, measured or complete",
        "rows": calendar,
        "existing_real_artifacts_read_only_census": observed,
        "adjudication_boundary": (
            "This card maps requirement ids to the I-17 calendar and records which real artifacts "
            "already exist.  It does NOT decide eligibility: I-17-A's reviewer signs the retained "
            "requirement list, and the latest daily manifest itself reports ok=false, so no existing "
            "artifact may be counted as a green period here."),
        "latest_daily_manifest_ok": daily.get("ok"),
        "latest_daily_manifest_run_id": daily.get("latest_run_id"),
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    missing = [row["row_id"] for row in calendar if not row["anchor"].get("found")]
    print(json.dumps({
        "rows": len(calendar),
        "anchors_not_found": missing,
        "all_pending": all(row["status"] == "pending" for row in calendar),
        "latest_daily_manifest_ok": daily.get("ok"),
    }, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
