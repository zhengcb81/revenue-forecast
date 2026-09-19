"""I-04-A design measurement 2/2: the model-clock math oracle, recomputed independently.

This does NOT import fetch_filing (an expectation derived from the function under test is not
independent).  It re-implements the FROZEN retry rules from oracle.md as pure arithmetic on a
virtual monotonic clock and prints the raw timestamp table for F-D1/F-D2/F-D3, so the
independent reviewer can recompute every number by hand.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent / "design_measurements" / "math_oracle.json"

BACKOFF = 5.0          # frozen CATALOG_LOCKED_BACKOFF_SECONDS (jitter 0 in F-D1)
CLEANUP_BUDGET = 30.0  # proposed C (signed in decision.md)


def simulate_fd1() -> dict:
    """clock 0 -> subcall consumes 9 and raises catalog_busy -> deadline 10, jitter 0."""
    t = 0.0
    deadline = 10.0
    calls: list[dict] = []
    sleeps: list[dict] = []
    calls.append({"action": "identify", "start": t, "end": 9.0,
                  "timeout_granted": round(10.0 - t, 6), "result": "catalog_busy"})
    t = 9.0
    remaining = deadline - t
    wait = min(BACKOFF, remaining)          # clamp to remaining
    sleeps.append({"start": t, "end": round(t + wait, 6), "requested": BACKOFF, "wait": wait})
    t = round(t + wait, 6)
    end = t
    remaining_after = round(deadline - t, 6)
    raised = remaining_after <= 0
    return {
        "case": "F-D1",
        "deadline": deadline,
        "events": {"calls": calls, "sleeps": sleeps},
        "request_end": end,
        "finished_within_deadline": end <= deadline,
        "retry_subcalls_after_backoff": 0,
        "raised_upstream_error": raised,
        "terminal_reason": ("remaining<=0 before any further call" if raised else "loop continued"),
    }


def simulate_fd2() -> dict:
    """now=100, deadline=90 (already exceeded), worker-status wanted by a REQUEST stage."""
    now = 100.0
    deadline = 90.0
    remaining = deadline - now
    buggy_floor_would_grant = max(10.0, min(remaining, 60.0))
    return {
        "case": "F-D2",
        "remaining_at_decision": remaining,
        "request_stage_worker_status_calls": 0,
        "budget_a_regranted_floor_would_give": buggy_floor_would_grant,
        "expected_budget_for_requests": 0.0,
        "violation_if_floor_kept": buggy_floor_would_grant > 0,
        "expected_outcome": ("request stage is skipped/raises deadline-exceeded; no new 10 s "
                             "request budget may be minted after the deadline"),
    }


def simulate_fd3() -> dict:
    """This scope paused the worker; the deadline is exhausted; ownership must still be restored
    under the INDEPENDENT cleanup budget, reported separately from the request."""
    request_deadline = 10.0
    now = 25.0  # request long over (it failed at/after the deadline)
    cleanup_start = now
    resume_wait = 5.0
    cleanup_elapsed = min(CLEANUP_BUDGET, resume_wait + 0.5)  # subprocess overhead inside C
    return {
        "case": "F-D3",
        "request_status": "failed (deadline exhausted before completion)",
        "cleanup_allowed_after_deadline": True,
        "cleanup_budget": CLEANUP_BUDGET,
        "cleanup_start": cleanup_start,
        "cleanup_end": round(cleanup_start + cleanup_elapsed, 6),
        "cleanup_elapsed": cleanup_elapsed,
        "cleanup_counted_into_request_deadline": False,
        "resume_wait_arg": resume_wait,
        "on_cleanup_failure": ("record cleanup_status=failed + stderr warning; the request's own "
                               "exit code/outcome must not be rewritten by the cleanup failure"),
        "ownership_restored_attempted": True,
    }


def main() -> int:
    record = {
        "artifact": "I-04-A model-clock math oracle (independent recomputation)",
        "rules_source": "oracle.md (frozen before this run; no import of fetch_filing)",
        "constants": {"backoff": BACKOFF, "jitter_fd1": 0.0, "cleanup_budget": CLEANUP_BUDGET},
        "cases": [simulate_fd1(), simulate_fd2(), simulate_fd3()],
        "ran_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=True, indent=2))
    if len(sys.argv) > 1 and sys.argv[1] == "--assert":
        fd1, fd2, fd3 = record["cases"]
        assert fd1["finished_within_deadline"] and fd1["retry_subcalls_after_backoff"] == 0
        assert fd1["raised_upstream_error"]
        assert fd2["request_stage_worker_status_calls"] == 0 and fd2["violation_if_floor_kept"]
        assert fd3["cleanup_allowed_after_deadline"] and not fd3["cleanup_counted_into_request_deadline"]
        print("math oracle assertions: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
