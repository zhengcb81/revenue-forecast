"""Freeze the r2 oracle material AFTER the r1 review (changes_required) and
BEFORE any r2 run.

Append-only provenance rules honoured here:
  * the r1 files stay byte-identical in harness/archive/ (pre-image sha256s);
  * the new files are NEW paths (cases.r2.json / frozen_expectations.r2.json) --
    nothing the reviewer verified is overwritten;
  * the one corrected r1 value (W1 union_seconds 2220 -> 1740) is kept in the
    file as `expected_superseded` with old value, new value, reason, timestamp,
    pre-image sha256 and a mechanical unified diff -- never erased, and never
    described as "there was never a 2220".

Usage:
  <iso-python> -X utf8 -B harness/freeze_r2.py
"""

from __future__ import annotations

import copy
import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
ARCHIVE = HERE / "archive"

CASES_R1 = ARCHIVE / "cases.r1.json"
EXP_R1 = ARCHIVE / "frozen_expectations.r1.json"
CASES_R2 = HERE / "cases.r2.json"
EXP_R2 = HERE / "frozen_expectations.r2.json"

W1_FIELDS = {
    "scheduled_at": "2026-09-19T00:00:00Z",
    "started_at": "2026-09-19T00:00:00Z",
    "sampled_at": [f"2026-09-19T00:{m:02d}:00Z" for m in range(30)],
    "observation_finished_at": "2026-09-19T00:29:00Z",
    "quick_check_started_at": "2026-09-19T00:29:00Z",
    "quick_check_finished_at": "2026-09-19T00:37:00Z",
    "command_finished_at": "2026-09-19T00:37:00Z",
}


def _daily(dates, prefix="T2"):
    return [{"run_id": f"{prefix}-{d}", "started_at": f"{d}T03:30:00Z", "ok": True,
             "report_sha256": f"h{d.replace('-', '')}"} for d in dates]


NEW_CASES = [
    {
        "case_id": "X1", "class": "window_accounting",
        "requirement_id": "P1-BASIS-CLOSED-ENUM(review finding)",
        "note": "reviewer probe B1: W1 facts, claim 2220 s but basis renamed to an unregistered name",
        "claim": {"status": "eligible", "natural_observation_seconds": 2220, "basis": "wall_clock"},
        "fields": copy.deepcopy(W1_FIELDS),
    },
    {
        "case_id": "X2", "class": "window_accounting",
        "requirement_id": "P1-BASIS-CLOSED-ENUM(review finding)",
        "note": "reviewer probe B2: empty-string basis with an arbitrary 99999 s claim",
        "claim": {"status": "eligible", "natural_observation_seconds": 99999, "basis": ""},
        "fields": copy.deepcopy(W1_FIELDS),
    },
    {
        "case_id": "X3", "class": "window_accounting",
        "requirement_id": "P1-BASIS-CLOSED-ENUM(review finding)",
        "note": "reviewer probe B3: basis key absent entirely",
        "claim": {"status": "eligible", "natural_observation_seconds": 99999},
        "fields": copy.deepcopy(W1_FIELDS),
    },
    {
        "case_id": "X4", "class": "window_accounting",
        "requirement_id": "P1-BASIS-CLOSED-ENUM(review finding)",
        "note": "reviewer probe B4: basis explicitly null",
        "claim": {"status": "eligible", "natural_observation_seconds": 2220, "basis": None},
        "fields": copy.deepcopy(W1_FIELDS),
    },
    {
        "case_id": "X5", "class": "window_accounting",
        "requirement_id": "P2-QC-NOT-IN-UNION(review finding)",
        "note": "P2 fixed direction: the honest 1740 s claim under union_of_windows is now supported",
        "claim": {"status": "eligible", "natural_observation_seconds": 1740, "basis": "union_of_windows"},
        "fields": copy.deepcopy(W1_FIELDS),
    },
    {
        "case_id": "X6", "class": "window_accounting",
        "requirement_id": "P2-QC-NOT-IN-UNION(review finding)",
        "note": "reviewer case X6: 37 minutes claimed as the natural observation under union_of_windows",
        "claim": {"status": "eligible", "natural_observation_seconds": 2220, "basis": "union_of_windows"},
        "fields": copy.deepcopy(W1_FIELDS),
    },
    {
        "case_id": "X7", "class": "window_accounting",
        "requirement_id": "P2-QC-NOT-IN-UNION(review finding)",
        "note": "same attack under sum_of_windows",
        "claim": {"status": "eligible", "natural_observation_seconds": 2220, "basis": "sum_of_windows"},
        "fields": copy.deepcopy(W1_FIELDS),
    },
    {
        "case_id": "X8", "class": "window_accounting",
        "requirement_id": "P2-QC-RENAMED-AS-WINDOW(review finding)",
        "note": "reviewer probe P4/P5: the quick_check span renamed as a second observation window",
        "claim": {"status": "eligible", "natural_observation_seconds": 2220, "basis": "union_of_windows"},
        "fields": {
            "scheduled_at": "2026-09-19T00:00:00Z",
            "started_at": "2026-09-19T00:00:00Z",
            "windows": [
                {"window_id": "A", "started_at": "2026-09-19T00:00:00Z", "finished_at": "2026-09-19T00:29:00Z"},
                {"window_id": "B-copy-of-quick-check", "started_at": "2026-09-19T00:29:00Z",
                 "finished_at": "2026-09-19T00:37:00Z"},
            ],
            "observation_finished_at": "2026-09-19T00:37:00Z",
            "quick_check_started_at": "2026-09-19T00:29:00Z",
            "quick_check_finished_at": "2026-09-19T00:37:00Z",
            "command_finished_at": "2026-09-19T00:37:00Z",
        },
    },
    {
        "case_id": "X9", "class": "window_accounting",
        "requirement_id": "P2-QC-RENAMED-AS-WINDOW(review finding)",
        "note": "same renamed window with an honest 1740 s claim: the record itself is still not observation evidence",
        "claim": {"status": "eligible", "natural_observation_seconds": 1740, "basis": "union_of_windows"},
        "fields": {
            "scheduled_at": "2026-09-19T00:00:00Z",
            "started_at": "2026-09-19T00:00:00Z",
            "windows": [
                {"window_id": "A", "started_at": "2026-09-19T00:00:00Z", "finished_at": "2026-09-19T00:29:00Z"},
                {"window_id": "B-copy-of-quick-check", "started_at": "2026-09-19T00:29:00Z",
                 "finished_at": "2026-09-19T00:37:00Z"},
            ],
            "observation_finished_at": "2026-09-19T00:37:00Z",
            "quick_check_started_at": "2026-09-19T00:29:00Z",
            "quick_check_finished_at": "2026-09-19T00:37:00Z",
            "command_finished_at": "2026-09-19T00:37:00Z",
        },
    },
    {
        "case_id": "X10", "class": "window_accounting",
        "requirement_id": "SIBLING-OF-P1-P2-NO-INTERVAL",
        "note": "sibling hole found while extending the review's attack class: no declared interval at all, claim 0",
        "claim": {"status": "eligible", "natural_observation_seconds": 0, "basis": "union_of_windows"},
        "fields": {
            "scheduled_at": "2026-09-19T00:00:00Z",
            "started_at": "2026-09-19T00:00:00Z",
            "quick_check_started_at": "2026-09-19T00:29:00Z",
            "quick_check_finished_at": "2026-09-19T00:37:00Z",
            "command_finished_at": "2026-09-19T00:37:00Z",
        },
    },
    {
        "case_id": "X11", "class": "window_accounting",
        "requirement_id": "SIBLING-OF-P1-P2-NO-INTERVAL",
        "note": "same absent-interval record claiming 0 seconds under sample_span",
        "claim": {"status": "eligible", "natural_observation_seconds": 0, "basis": "sample_span"},
        "fields": {
            "scheduled_at": "2026-09-19T00:00:00Z",
            "started_at": "2026-09-19T00:00:00Z",
            "quick_check_started_at": "2026-09-19T00:29:00Z",
            "quick_check_finished_at": "2026-09-19T00:37:00Z",
            "command_finished_at": "2026-09-19T00:37:00Z",
        },
    },
    {
        "case_id": "X12", "class": "calendar",
        "requirement_id": "P3-b-WEEKLY-STALE",
        "note": "reviewer suggestion: weekly window entirely stale while the claim says complete",
        "claim": {"status": "complete", "natural_observation_seconds": None, "basis": None},
        "fields": {
            "clock_source": "system_utc",
            "ledger": {
                "daily": _daily(["2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11",
                                 "2026-09-12", "2026-09-13", "2026-09-14"]),
                "weekly": [
                    {"run_id": "T3-2026-08-30", "started_at": "2026-08-30T04:30:00Z", "ok": True,
                     "report_sha256": "wstale0"},
                    {"run_id": "T3-2026-09-06", "started_at": "2026-09-06T04:30:00Z", "ok": True,
                     "report_sha256": "wstale1"},
                ],
                "monthly": [
                    {"run_id": "M-2026-09-08", "started_at": "2026-09-08T05:00:00Z", "ok": True,
                     "report_sha256": "mok0"},
                ],
                "alerts": [{"run_id": "drill-1", "acked": True}],
            },
        },
    },
    {
        "case_id": "X13", "class": "calendar",
        "requirement_id": "P3-b-MONTHLY-STALE",
        "note": "reviewer suggestion: monthly window stale while the claim says complete",
        "claim": {"status": "complete", "natural_observation_seconds": None, "basis": None},
        "fields": {
            "clock_source": "system_utc",
            "ledger": {
                "daily": _daily(["2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11",
                                 "2026-09-12", "2026-09-13", "2026-09-14"]),
                "weekly": [
                    {"run_id": "T3-2026-09-06", "started_at": "2026-09-06T04:30:00Z", "ok": True,
                     "report_sha256": "w0b0"},
                    {"run_id": "T3-2026-09-13", "started_at": "2026-09-13T04:30:00Z", "ok": True,
                     "report_sha256": "w0b1"},
                ],
                "monthly": [
                    {"run_id": "M-2026-07-01", "started_at": "2026-07-01T05:00:00Z", "ok": True,
                     "report_sha256": "mstale0"},
                ],
                "alerts": [{"run_id": "drill-1", "acked": True}],
            },
        },
    },
    {
        "case_id": "X14", "class": "calendar",
        "requirement_id": "P3-a-SAME-DAY-SECOND-RUN",
        "note": "reviewer probe Q1 class: a second run on the same UTC day is ignored (and reported) instead of silently breaking the chain",
        "claim": {"status": "complete", "natural_observation_seconds": None, "basis": None},
        "fields": {
            "clock_source": "system_utc",
            "ledger": {
                "daily": _daily(["2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11",
                                 "2026-09-12", "2026-09-13"]) + [
                    {"run_id": "T2-2026-09-10-extra", "started_at": "2026-09-10T12:00:00Z",
                     "ok": True, "report_sha256": "hextra"},
                ],
                "weekly": [
                    {"run_id": "T3-2026-09-06", "started_at": "2026-09-06T04:30:00Z", "ok": True,
                     "report_sha256": "w0b0"},
                    {"run_id": "T3-2026-09-13", "started_at": "2026-09-13T04:30:00Z", "ok": True,
                     "report_sha256": "w0b1"},
                ],
                "monthly": [
                    {"run_id": "M-2026-09-08", "started_at": "2026-09-08T05:00:00Z", "ok": True,
                     "report_sha256": "m0b0"},
                ],
                "alerts": [{"run_id": "drill-1", "acked": True}],
            },
        },
    },
]

# the single corrected r1 value, plus the new assertions that pin the P2 fix
EXPECTATION_UPDATES = {
    "W1": {
        "computed": {
            "union_seconds": 1740,
            "sum_seconds": 1740,
            "observation_interval_count": 1,
            "quick_check_overlap_seconds": 0,
            "quick_check_in_observation_intervals": False,
        }
    }
}

EXPECTED_NEW = {
    "X1": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"],
           "computed": {"observation_span_seconds": 1740, "union_seconds": 1740,
                        "basis_registered": False, "basis": "wall_clock"}},
    "X2": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"],
           "computed": {"basis_registered": False, "basis": ""}},
    "X3": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"],
           "computed": {"basis_registered": False, "basis": None}},
    "X4": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"],
           "computed": {"basis_registered": False, "basis": None}},
    "X5": {"verdict": "accept_claim", "refusals": [],
           "computed": {"union_seconds": 1740, "sum_seconds": 1740, "overlap_seconds": 0,
                        "quick_check_seconds": 480, "command_total_seconds": 2220,
                        "quick_check_overlap_seconds": 0}},
    "X6": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS"],
           "computed": {"union_seconds": 1740, "quick_check_seconds": 480}},
    "X7": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS"],
           "computed": {"sum_seconds": 1740, "union_seconds": 1740, "overlap_seconds": 0}},
    "X8": {"verdict": "reject_claim", "refusals": ["R-QC-IN-OBS"],
           "computed": {"union_seconds": 2220, "sum_seconds": 2220,
                        "quick_check_overlap_seconds": 480, "observation_interval_count": 2}},
    "X9": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS", "R-QC-IN-OBS"],
           "computed": {"union_seconds": 2220, "quick_check_overlap_seconds": 480}},
    "X10": {"verdict": "reject_claim", "refusals": ["R-NO-INTERVAL"],
            "computed": {"observation_interval_count": 0, "union_seconds": 0, "sum_seconds": 0,
                         "observation_span_seconds": None}},
    "X11": {"verdict": "reject_claim", "refusals": ["R-NO-INTERVAL"],
            "computed": {"observation_interval_count": 0, "observation_span_seconds": None}},
    "X12": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS"],
            "computed": {"daily_count": 7, "weekly_count": 0, "monthly_count": 1,
                         "alert_count": 1, "window_status": "pending"}},
    "X13": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS"],
            "computed": {"daily_count": 7, "weekly_count": 2, "monthly_count": 0,
                         "alert_count": 1, "window_status": "pending"}},
    "X14": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS"],
            "computed": {"daily_count": 6, "daily_same_day_runs_dropped": 1,
                         "weekly_count": 2, "monthly_count": 1, "alert_count": 1,
                         "window_status": "pending"}},
}

ERRATUM_REASON = (
    "Independent review (report sha256 21ac638dd052f443948647eb824fc15326b8e2c974c4e781ab09616f2702cc1e, "
    "section 3 P2, verdict changes_required) found that the natural observation intervals included the "
    "quick_check interval, so union_of_windows/sum_of_windows accepted 37 minutes as the observation and "
    "rejected the honest 1740 s claim. Fix option 甲 was chosen: the natural duration is taken over the "
    "observation phase only, quick_check is separated (J15 refuses a declared window that covers the "
    "quick_check interval), and W1's union_seconds expectation is corrected from 2220 to 1740. The old "
    "value is preserved here; it was never absent and is not being erased."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cases_r1 = json.loads(CASES_R1.read_text(encoding="utf-8"))
    exp_r1 = json.loads(EXP_R1.read_text(encoding="utf-8"))
    pre_image_exp_sha = sha256(EXP_R1)
    pre_image_cases_sha = sha256(CASES_R1)

    cases_r2 = copy.deepcopy(cases_r1)
    cases_r2["revision"] = "r2"
    cases_r2["r1_pre_image_sha256"] = pre_image_cases_sha
    cases_r2["r2_note"] = ("r1's 20 cases are byte-identical copies; X1-X14 were added after the "
                           "independent review returned changes_required. No r1 case was edited.")
    cases_r2["cases"] = cases_r1["cases"] + NEW_CASES

    exp_r2 = copy.deepcopy(exp_r1)
    exp_r2["revision"] = "r2"
    exp_r2["r1_pre_image_sha256"] = pre_image_exp_sha
    exp_r2["authored"] = ("r2, written AFTER the independent review and BEFORE any r2 run; values hand-derived "
                          "from oracle.md sections 3-4 plus the r2 additions recorded in oracle.md section 11")

    superseded = {}
    for case_id, update in EXPECTATION_UPDATES.items():
        old = copy.deepcopy(exp_r2["expected"][case_id])
        for key, value in update["computed"].items():
            old_value = exp_r2["expected"][case_id]["computed"].get(key, "<absent>")
            superseded.setdefault(case_id, {})[f"computed.{key}"] = {
                "old": old_value,
                "new": value,
                "pre_image_sha256": pre_image_exp_sha,
                "changed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "reason": ERRATUM_REASON,
            }
            exp_r2["expected"][case_id]["computed"][key] = value

    for case_id, expected in EXPECTED_NEW.items():
        exp_r2["expected"][case_id] = expected

    # mechanical diff of the expected map: the reviewer can re-derive it
    before = json.dumps(exp_r1["expected"], ensure_ascii=False, indent=2, sort_keys=True)
    after = json.dumps(exp_r2["expected"], ensure_ascii=False, indent=2, sort_keys=True)
    diff_lines = list(difflib.unified_diff(before.splitlines(), after.splitlines(),
                                           fromfile="frozen_expectations.r1.json:expected",
                                           tofile="frozen_expectations.r2.json:expected", n=2,
                                           lineterm=""))
    exp_r2["expected_superseded"] = superseded
    exp_r2["errata"] = [{
        "id": "ERR-I14B-R2-01",
        "what": "W1.computed.union_seconds 2220 -> 1740 (plus new pinning assertions)",
        "why": ERRATUM_REASON,
        "pre_image": {
            "frozen_expectations.json": pre_image_exp_sha,
            "cases.json": pre_image_cases_sha,
            "archived_at": "harness/archive/frozen_expectations.r1.json, harness/archive/cases.r1.json",
        },
        "new_files": {
            "harness/frozen_expectations.r2.json": "self",
            "harness/cases.r2.json": "self",
        },
        "r1_value_retained_in": "expected_superseded",
        "diff_from_r1_expected_map": diff_lines,
        "added_expectations": sorted(EXPECTED_NEW),
        "unchanged_r1_cases": [c["case_id"] for c in cases_r1["cases"]],
    }]

    CASES_R2.write_text(json.dumps(cases_r2, ensure_ascii=False, indent=2), encoding="utf-8")
    EXP_R2.write_text(json.dumps(exp_r2, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "cases_r2": str(CASES_R2), "cases_r2_sha256": sha256(CASES_R2),
        "case_count": len(cases_r2["cases"]),
        "expectations_r2": str(EXP_R2), "expectations_r2_sha256": sha256(EXP_R2),
        "expected_count": len(exp_r2["expected"]),
        "r1_cases_pre_image_sha256": pre_image_cases_sha,
        "r1_expectations_pre_image_sha256": pre_image_exp_sha,
        "superseded_keys": {k: list(v) for k, v in superseded.items()},
        "diff_hunk_lines": len(diff_lines),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
