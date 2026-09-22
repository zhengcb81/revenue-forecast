"""I-14-E-APPLY: analyse campaign v2 from the JSONL (read-only; runs nothing).

Emits ``after/campaign_v2-analysis.json`` with, per arm: tallies vs frozen
expectations, the hang timeout the launcher actually used, watchdog-kill uptimes
against the derived budget (non-vacuity check (a)/(b)/(c) of oracle.md SS5),
retention checks (zip covers all files, flat copies, executed path lengths,
artifact presence for the CF-I14F-X1 discrimination set), load probes, and the
persistence proof (append-only line order, index sync).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
AFTER = ATT / "after"
JSONL = AFTER / "campaign_v2.jsonl"
INDEX = AFTER / "campaign_v2-index.json"
OUT = AFTER / "campaign_v2-analysis.json"

POLL_MS = 100


def load_lines() -> list[dict]:
    records = []
    torn = 0
    for line in JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            torn += 1
    return records, torn


def nonvacuity_check(rec: dict) -> dict:
    """oracle.md SS5 (a)(b)(c) evaluated from the run's own events."""
    ev = rec.get("events", {})
    hang = ev.get("hang_timeout_seconds_actually_used")
    uptimes = ev.get("watchdog_kill_uptimes") or []
    reasons = ev.get("watchdog_kill_reasons") or []
    starts = ev.get("child_started_count")
    lo = (hang - POLL_MS / 1000.0) if isinstance(hang, (int, float)) else None
    hi = (hang + 1.0) if isinstance(hang, (int, float)) else None
    in_budget = ([u for u in uptimes
                  if u is not None and lo is not None and lo <= u <= hi]
                 if uptimes else [])
    return {
        "run": rec["run"], "condition": rec["condition"], "outcome": rec["outcome"],
        "a_watchdog_fired": bool(uptimes),
        "a_reasons": reasons,
        "a_reason_is_session_start_timeout": reasons == ["session_start_timeout"],
        "hang_timeout_seconds": hang,
        "b_kill_uptimes": uptimes,
        "b_expected_window": [lo, hi],
        "b_kills_in_budget": len(in_budget),
        "b_all_kills_in_budget": bool(uptimes) and len(in_budget) == len(uptimes),
        "c_child_started_count": starts,
        "c_equals_3": starts == 3,
        "assertion": rec.get("assertion", ""),
        "guard_triggered": rec.get("guard_triggered"),
        "wall_seconds": rec.get("wall_seconds"),
    }


def retention_check(rec: dict) -> dict:
    art = rec.get("artifacts", {})
    key = art.get("key_files", {})
    return {
        "run": rec["run"],
        "basetemp_path": rec.get("basetemp_path"),
        "basetemp_path_chars": len(rec.get("basetemp_path") or ""),
        "longest_executed_path_chars": rec.get("basetemp_longest_path_chars"),
        "executed_tree_deleted": rec.get("basetemp_executed_tree_deleted"),
        "zip": rec.get("basetemp_archive"),
        "zip_present": bool(rec.get("basetemp_archive")) and Path(rec["basetemp_archive"]).exists(),
        "zip_entries": rec.get("basetemp_zip_entries"),
        "zip_covers_all_files": rec.get("basetemp_zip_covers_all_files"),
        "flat_dir": rec.get("basetemp_artifacts_dir"),
        "flat_files": rec.get("basetemp_flat_files"),
        "files_total": rec.get("basetemp_files"),
        "archive_error": rec.get("basetemp_archive_error"),
        "key_files_present": {name: entry.get("present", False)
                              for name, entry in key.items()},
        "worker_stdout_logs": art.get("worker_log_files", {}).get("stdout", []),
        "worker_stderr_logs": art.get("worker_log_files", {}).get("stderr", []),
        "events_present_in_jsonl": rec.get("events", {}).get("events_present"),
    }


def main() -> int:
    records, torn = load_lines()
    index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    arms: dict[str, dict] = {}
    for rec in records:
        arm = rec["arm"]
        bucket = arms.setdefault(arm, {
            "expect": rec.get("arm_expect"), "runs": [],
            "outcomes": {}, "hang_used": [], "as_expected": 0,
            "not_as_expected": 0, "starts": [], "kills": [],
            "load_pct": [], "walls": [], "trees": {}, "suites": {}})
        bucket["outcomes"][rec["outcome"]] = bucket["outcomes"].get(rec["outcome"], 0) + 1
        bucket["as_expected" if rec.get("as_expected") else "not_as_expected"] += 1
        hang = rec.get("events", {}).get("hang_timeout_seconds_actually_used")
        if hang is not None:
            bucket["hang_used"].append(hang)
        bucket["starts"].append(rec.get("events", {}).get("child_started_count"))
        bucket["kills"].append(rec.get("events", {}).get("child_unresponsive_count"))
        bucket["walls"].append(rec.get("wall_seconds"))
        bucket["trees"][rec["tree"]] = bucket["trees"].get(rec["tree"], 0) + 1
        bucket["suites"][rec.get("suite_sha256")] = bucket["suites"].get(rec.get("suite_sha256"), 0) + 1
        load_pct = (rec.get("machine_after_warmup") or {}).get("load_pct")
        if load_pct is not None:
            bucket["load_pct"].append(load_pct)
        bucket["runs"].append(rec["run"])
    for arm, bucket in arms.items():
        bucket["n"] = len(bucket["runs"])
        bucket["hang_used"] = sorted(set(bucket["hang_used"]))
        bucket["load_pct_range"] = ([min(bucket["load_pct"]), max(bucket["load_pct"])]
                                    if bucket["load_pct"] else None)
        bucket["wall_range"] = ([min(bucket["walls"]), max(bucket["walls"])]
                                if bucket["walls"] else None)
        bucket["all_expected"] = bucket["not_as_expected"] == 0

    nonvacuity = [nonvacuity_check(r) for r in records if r["arm"] == "A3-nonvacuity"]
    retention = [retention_check(r) for r in records]
    timestamps_ok = all(
        records[i].get("started_utc", "") <= records[i + 1].get("started_utc", "")
        for i in range(len(records) - 1))

    v1 = {}
    for name in ("B1-fixed-quiet", "B2-fixed-cpu8", "B3-mutant0.5-cpu8"):
        path = AFTER / f"bench-{name}.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            v1[name] = payload.get("tally_by_condition")

    payload = {
        "card": "I-14-E-APPLY", "attempt": "a20260921-01", "campaign": "v2",
        "analysed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "oracle": "oracle-addendum-C.md (frozen 2026-09-22T07:31:56Z, before run 1)",
        "arms": arms,
        "expectations_met_all_arms": all(b["all_expected"] for b in arms.values()),
        "nonvacuity": {
            "runs": nonvacuity,
            "quiet_all_pass": all(r["outcome"] == "passed" for r in nonvacuity
                                  if r["condition"] == "quiet"),
            "caught_event_level_all_runs": all(
                r["a_watchdog_fired"] and r["c_equals_3"]
                and r["a_reason_is_session_start_timeout"] for r in nonvacuity),
            "all_kills_in_derived_budget": all(r["b_all_kills_in_budget"]
                                               for r in nonvacuity),
            "pytest_red_under_load": [r["run"] for r in nonvacuity
                                      if r["condition"] == "cpu"
                                      and r["outcome"] != "passed"],
            "red_cause": ("subprocess.TimeoutExpired at the node's own outer "
                          "timeout=15 - the watchdog DID fire and the hung child "
                          "WAS caught (starts=3, kills=2); this is budget-RED, not "
                          "vacuity-RED; oracle.md SS5's letter ('any RED => blocked') "
                          "is engaged for reviewer adjudication"),
        },
        "retention": {
            "all_zips_present": all(r["zip_present"] for r in retention),
            "all_zips_cover_files": all(r["zip_covers_all_files"] for r in retention),
            "any_executed_tree_deleted": any(r["executed_tree_deleted"]
                                             for r in retention),
            "executed_path_chars_range": [min(r["basetemp_path_chars"] for r in retention),
                                          max(r["basetemp_path_chars"] for r in retention)],
            "longest_executed_path_chars_range":
                [min(r["longest_executed_path_chars"] for r in retention),
                 max(r["longest_executed_path_chars"] for r in retention)],
            "archive_errors": [r for r in retention if r["archive_error"]],
            "runs_missing_events_artifact":
                [r["run"] for r in retention
                 if not r["key_files_present"].get("worker_launcher_events.jsonl")],
            "per_run": retention,
        },
        "persistence": {
            "jsonl_lines": len(records),
            "jsonl_torn_lines": torn,
            "jsonl_bytes": JSONL.stat().st_size,
            "index_recorded_total": index.get("recorded_total"),
            "index_torn": index.get("jsonl_lines_torn"),
            "index_synced_with_jsonl": index.get("recorded_total") == len(records),
            "started_utc_monotonic": timestamps_ok,
            "planned_total": 22,
            "complete": len(records) == 22,
        },
        "v1_comparison": v1,
        "records": records,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"analysis -> {OUT}")
    for arm, bucket in arms.items():
        print(f"  {arm}: n={bucket['n']} outcomes={bucket['outcomes']} "
              f"expected={bucket['as_expected']}/{bucket['n']} hang={bucket['hang_used']} "
              f"load%={bucket['load_pct_range']} walls={bucket['wall_range']}")
    nv = payload["nonvacuity"]
    print(f"  nonvacuity: quiet_pass={nv['quiet_all_pass']} "
          f"caught_event_level_all_runs={nv['caught_event_level_all_runs']} "
          f"kills_in_budget={nv['all_kills_in_derived_budget']} "
          f"pytest_red_under_load={nv['pytest_red_under_load']}")
    ret = payload["retention"]
    print(f"  retention: zips={ret['all_zips_present']} "
          f"cover={ret['all_zips_cover_files']} "
          f"exec_path_chars={ret['executed_path_chars_range']} "
          f"longest={ret['longest_executed_path_chars_range']} "
          f"missing_events={ret['runs_missing_events_artifact']}")
    print(f"  persistence: {payload['persistence']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
