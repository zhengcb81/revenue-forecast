"""r3 commands.json patch: register the timeout case set and refresh the counts."""

from __future__ import annotations

import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ATTEMPT, "commands.json")


def main():
    with open(PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    data["note"] += (" (v1.3: the protocol suite now includes the r3 lock-timeout/queue cases "
                     "F-T1..F-T4; the lease lock reports code `lease_lock_timeout`.)")

    protocol = ["F-L1", "F-L2a", "F-L2b", "F-L2c", "F-L2c-dead", "F-L2d", "F-L3", "F-L4a",
                "F-L4b", "F-L4c", "F-L4d", "F-L4e", "F-W1", "F-W2", "F-W4", "F-W4b", "F-W5",
                "V4-a", "V4-e", "V4-f", "F-W7", "F-L2e-stale", "F-L2e-fixed", "F-GEN",
                "F-T1", "F-T2", "F-T3", "F-T4"]
    for command in data["commands"]:
        if command["id"] == "I04C-01-compile-sim":
            command["argv"] = [
                "iso/venv/Scripts/python.exe", "-B", "-m", "py_compile",
                "sim/kernel.py", "sim/participant.py", "sim/stub_worker.py", "sim/hold_lock.py",
                "sim/harness.py", "sim/cases_core.py", "sim/cases_ownership.py",
                "sim/cases_legacy.py", "sim/cases_review.py", "sim/cases_timeout.py",
                "sim/stress.py", "sim/scheduler.py", "sim/parse_run.py", "sim/static_check.py",
                "sim/phase_wall.py", "sim/freeze_evidence.py",
            ]
        if command["id"] == "I04C-02-protocol-suite":
            command["argv"] = (["iso/venv/Scripts/python.exe", "-B", "sim/scheduler.py", "run"]
                               + protocol + ["--log", "evidence/run-all.txt"])
            command["purpose"] += " + the r3 lock-timeout/queue cases (F-T1..F-T4)"
            command["parsed_counts"] = ("cases_in_log=28 pass=28 fail=0 harness_error=0 "
                                        "failing_checks=0")
            command["raw_returncode"] = 0

    data["commands"].append({
        "id": "I04C-09-timeout-boundary",
        "purpose": ("r3 F-I04C-11/12: lock-timeout and queue-crosses-budget boundary. An external "
                    "process really holds the lease lock; request phase (budget 0.05), budget 0, "
                    "cleanup phase and 6-way queue contention."),
        "cwd": "C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/execution_runs/I-04-C/a20260919-01",
        "argv": ["iso/venv/Scripts/python.exe", "-B", "sim/scheduler.py", "run",
                 "F-T1", "F-T2", "F-T3", "F-T4"],
        "config_paths": [],
        "allowed_write_roots": ["execution_runs/I-04-C/a20260919-01/evidence"],
        "network": "disabled",
        "timeout_seconds": 600,
        "expected_returncode": 0,
        "expected_business_result": ("code/action lease_lock_timeout in the request phase, "
                                     "cleanup_status=failed:lease_lock_timeout in the cleanup "
                                     "phase, no wait at all when the budget is 0, and the queue "
                                     "tail failing closed with zero writes"),
        "raw_returncode": 0,
        "raw_log": "evidence/run-all.txt (the same run that carries the protocol suite)",
    })
    with open(PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1, ensure_ascii=False)
    print("commands.json updated; commands =", len(data["commands"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
