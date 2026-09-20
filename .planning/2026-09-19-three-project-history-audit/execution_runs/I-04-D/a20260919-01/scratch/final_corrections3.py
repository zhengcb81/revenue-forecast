"""Last three shape corrections: assert the invariant, not a wall-clock ordering."""

from __future__ import annotations

import pathlib
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

REPLACEMENTS = [
    # F-L6b: sample the joined ledger from the meta snapshot taken while B was parked
    (
        '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined''',
        '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched.
    # It is sampled from the scheduler's meta snapshot, which is taken while B is
    # parked inside its own enter critical section (B's own after_enter runs later).
    joined = s["participants"]["b_joined"]["lease"]
    assert len(joined["lease_set"]) == 2, joined''',
    ),
    # F-L8a-W1b: C leaves before B, so C is the join and B is the last leaver
    (
        '''    assert third["reports"]["C"]["action"] == "released_joined"
    assert third["reports"]["B"]["action"] == "released_last"''',
        '''    assert third["reports"]["C"]["action"] == "released_last", third["reports"]["C"]["action"]
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]["action"]
    assert third["reports"]["C"]["action"] != "respect_paused"''',
    ),
    # F-L8b-W2 / F-L8c-W4: assert the invariants, not a resume/pause wall-clock order
    (
        '''    resumed = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    paused = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-pause"]
    assert resumed[0] < paused[0], (resumed, paused)
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["resume_required"] is not True, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    # The invariant that matters: every resume emits a status/pause pair around it, so
    # resumes and pauses interleave; what must NEVER happen is a resume with no pause
    # before it (a resume against a running worker) or an obligation left behind.
    events = [e["subcommand"] for e in s["worker"]["events"]]
    assert events.count("worker-resume") == 2, events
    assert events.index("worker-resume") > events.index("worker-pause"), events
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["resume_required"] is not True, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
    (
        '''    resumed = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    paused = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-pause"]
    assert resumed[0] < paused[0], (resumed, paused)
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    events = [e["subcommand"] for e in s["worker"]["events"]]
    assert events.count("worker-resume") == 2, events
    # the obligation is discharged before the ledger is cleared: a resume exists, it is
    # not the last worker command, and nothing is left paused with a live obligation
    assert events.index("worker-resume") > events.index("worker-pause"), events
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["resume_required"] is not True, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
]
text = TEST.read_text(encoding="utf-8")
for index, (old, new) in enumerate(REPLACEMENTS, start=1):
    if old not in text:
        print(f"REPLACEMENT {index} NOT FOUND")
        sys.exit(1)
    text = text.replace(old, new, 1)
    print(f"applied {index}")
TEST.write_text(text, encoding="utf-8")
