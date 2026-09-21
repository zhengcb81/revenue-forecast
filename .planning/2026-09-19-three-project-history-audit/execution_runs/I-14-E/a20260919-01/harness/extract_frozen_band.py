"""I-14-E glue: re-extract the RAW record of the frozen band (I-14-C r5 frequency run).

The 24-run x 2-round x 2-tree band that card I-14-E quotes was recorded by
``I-14-C/a20260919-01/harness/run_flake_frequency.py``.  That script kept only
stdout per run inside the attempt; the *scratch* basetemp root
(``%TEMP%/i14c-flake-freq``) still holds every run's
``worker_launcher_events.jsonl``, i.e. the per-attempt timelines.

This script reads that surviving scratch (READ-ONLY) and emits, per run:
  tree, pass, run, rc/verdict (from the frozen JSON, cross-checked against the
  surviving stdout capture), child_started count, per-attempt uptime_seconds,
  launcher-session wall time, and the assertion line.

Nothing is executed; nothing is written outside this attempt.
"""

from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
from datetime import datetime
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
FROZEN_JSON = (ATTEMPT.parent.parent / "I-14-C" / "a20260919-01" / "r5" / "flake-evidence"
               / "frequency-child_without_runtime.json")
SCRATCH = Path(os.environ.get("TEMP", "")) / "i14c-flake-freq"
OUT_JSON = ATTEMPT / "evidence" / "frozen_band_raw_record.json"


def parse_ts(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def main() -> int:
    frozen = json.loads(FROZEN_JSON.read_text(encoding="utf-8"))
    by_key = {(r["pass"], r["tree"], r["run"]): r for r in frozen["results"]}
    # the 48 rows were recorded before run_flake_frequency.py started hashing its own
    # captures; the per-capture sha256 lives in the later `captures.files` backfill block.
    cap_sha = {(c["pass"], c["tree"], c["run"]): c["sha256"]
               for c in frozen.get("captures", {}).get("files", [])}
    rows = []
    for (pass_index, tree, run), rec in sorted(by_key.items()):
        tag = f"p{pass_index}-{tree}-child_without_runtime-{run}"
        run_dir = SCRATCH / tag
        events_path = None
        for candidate in run_dir.rglob("worker_launcher_events.jsonl"):
            events_path = candidate
            break
        events = []
        if events_path is not None and events_path.exists():
            txt = events_path.read_text(encoding="utf-8-sig")
            events = [json.loads(line) for line in txt.splitlines() if line.strip()]
        statuses = [e["status"] for e in events]
        starts = [e for e in events if e["status"] == "child_started"]
        unresp = [e for e in events if e["status"] == "child_unresponsive"]
        attempts = []
        for e in events:
            if e["status"] == "child_started":
                attempts.append({"attempt": e.get("attempt"), "child_pid": e.get("child_pid"),
                                 "recorded_at": e["recorded_at"]})
            elif e["status"] == "child_unresponsive" and attempts:
                attempts[-1]["unresponsive_uptime_seconds"] = e.get("uptime_seconds")
                attempts[-1]["unresponsive_reason"] = e.get("reason")
            elif e["status"] == "exited" and attempts:
                attempts[-1]["exited_uptime_seconds"] = e.get("uptime_seconds")
                attempts[-1]["exited_reason"] = e.get("reason")
                attempts[-1]["exit_code"] = e.get("exit_code")
        session_start = events[0]["recorded_at"] if events else None
        session_end = events[-1]["recorded_at"] if events else None
        wall = None
        if session_start and session_end:
            wall = (parse_ts(session_end) - parse_ts(session_start)).total_seconds()
        stdout_path = run_dir / "stdout.txt"
        stdout_sha = stdout_path.exists() and hashlib.sha256(stdout_path.read_bytes()).hexdigest()
        # run_flake_frequency.py hashed the *decoded text*, then wrote it with
        # Path.write_text (which translates \n -> \r\n on Windows).  Hash the
        # newline-normalised bytes too, so "is this the same run's output?" can
        # be answered honestly instead of by sha equality of different byte forms.
        stdout_sha_lf = None
        if stdout_path.exists():
            stdout_sha_lf = hashlib.sha256(
                stdout_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        rows.append({
            "pass": pass_index,
            "tree": tree,
            "run": run,
            "verdict_frozen_json": rec["verdict"],
            "returncode_frozen_json": rec["returncode"],
            "assertion_frozen_json": rec.get("assertion", ""),
            "stdout_sha256_surviving": stdout_sha or None,
            "stdout_sha256_surviving_lf_normalised": stdout_sha_lf,
            "stdout_sha256_frozen_capture": cap_sha.get((pass_index, tree, run)),
            "stdout_matches_frozen_capture": bool(stdout_sha) and
                stdout_sha == cap_sha.get((pass_index, tree, run)),
            "final_attempt_exit_uptime_seconds": (
                attempts[-1].get("exited_uptime_seconds") if attempts else None),
            "final_attempt_exit_code": (attempts[-1].get("exit_code") if attempts else None),
            "child_started_count": len(starts),
            "child_unresponsive_count": len(unresp),
            "statuses": statuses,
            "attempts": attempts,
            "launcher_session_wall_seconds": wall,
            "events_path": str(events_path) if events_path else None,
            "events_present": bool(events),
        })
    payload = {
        "source_frozen_json": str(FROZEN_JSON),
        "source_frozen_json_sha256": hashlib.sha256(FROZEN_JSON.read_bytes()).hexdigest(),
        "source_scratch_root": str(SCRATCH),
        "note": ("surviving scratch = the same 48 run dirs; events jsonl is the untouched "
                 "output of the frozen run (not a re-run)"),
        "rows": rows,
    }
    # tallies, computed from the surviving raw record only
    tally = {}
    for row in rows:
        key = f"pass{row['pass']}/{row['tree']}"
        bucket = tally.setdefault(key, {"runs": 0, "failed_by_verdict": 0,
                                        "failed_by_child_started_gt2": 0,
                                        "child_started_hist": {}})
        bucket["runs"] += 1
        if row["verdict_frozen_json"] == "failed":
            bucket["failed_by_verdict"] += 1
        if row["child_started_count"] > 2:
            bucket["failed_by_child_started_gt2"] += 1
        hist = bucket["child_started_hist"]
        hist[str(row["child_started_count"])] = hist.get(str(row["child_started_count"]), 0) + 1
    payload["tally"] = tally
    extra_started = [r["attempts"][1].get("unresponsive_uptime_seconds")
                     for r in rows if len(r["attempts"]) > 1
                     and "unresponsive_uptime_seconds" in r["attempts"][1]]
    payload["second_attempt_uptime_seconds"] = {
        "n": len(extra_started),
        "min": min(extra_started) if extra_started else None,
        "median": statistics.median(extra_started) if extra_started else None,
        "max": max(extra_started) if extra_started else None,
        "values": extra_started,
    }
    # the no-op (immediate-exit) child's own lifetime, from the clean-exit event
    clean = [r["final_attempt_exit_uptime_seconds"] for r in rows
             if r["final_attempt_exit_uptime_seconds"] is not None]
    failed_clean = [r["final_attempt_exit_uptime_seconds"] for r in rows
                    if r["final_attempt_exit_uptime_seconds"] is not None
                    and r["verdict_frozen_json"] == "failed"]
    passed_clean = [r["final_attempt_exit_uptime_seconds"] for r in rows
                    if r["final_attempt_exit_uptime_seconds"] is not None
                    and r["verdict_frozen_json"] == "passed"]
    payload["noop_child_lifetime_seconds"] = {
        "note": ("uptime_seconds of the attempt that exited cleanly (behaviour 2 = immediate "
                 "exit); this is the quantity the test's 0.5 s hang timeout must exceed"),
        "all": {"n": len(clean), "min": min(clean), "median": statistics.median(clean),
                "max": max(clean)},
        "passed_runs": {"n": len(passed_clean),
                        "min": min(passed_clean) if passed_clean else None,
                        "median": statistics.median(passed_clean) if passed_clean else None,
                        "max": max(passed_clean) if passed_clean else None},
        "failed_runs": {"n": len(failed_clean),
                        "min": min(failed_clean) if failed_clean else None,
                        "median": statistics.median(failed_clean) if failed_clean else None,
                        "max": max(failed_clean) if failed_clean else None},
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"tally": tally,
                      "second_attempt_uptime": payload["second_attempt_uptime_seconds"],
                      "noop_child_lifetime": payload["noop_child_lifetime_seconds"],
                      "rows": len(rows),
                      "events_present": sum(1 for r in rows if r["events_present"]),
                      "stdout_matches_frozen_capture":
                          sum(1 for r in rows if r["stdout_matches_frozen_capture"])},
                     indent=2))
    print("out:", OUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
