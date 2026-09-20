"""Last three corrections: the observed invariants of the crash/overlap cases."""

from __future__ import annotations

import pathlib
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

REPLACEMENTS = [
    # F-L6b: the "both leases" sample must come from B's own after_enter, because the
    # scheduler's b_joined snapshot is taken while B is parked BEFORE it registers.
    (
        '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched.
    # It is sampled from the scheduler's meta snapshot, which is taken while B is
    # parked inside its own enter critical section (B's own after_enter runs later).
    joined = s["participants"]["b_joined"]["lease"]
    assert len(joined["lease_set"]) == 2, joined''',
        '''    # Both leases are live at the same time: the scheduler parks B at its
    # enter-complete gate (B's lease durable) while A is separately parked at its
    # release-read gate, so the ledger the scheduler reads between the two holds BOTH.
    joined = s["participants"]["b_joined"]["lease"]
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert len(joined["lease_set"]) == 2, joined''',
    ),
    # F-L8a-W1b: C leaves first, so C can be the joining participant OR the last one -
    # what must hold is that neither C nor B ever adopts the crashed cycle as a user
    # pause, and that B ends clean.
    (
        '''    assert third["reports"]["C"]["action"] == "released_last", third["reports"]["C"]["action"]
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]["action"]
    assert third["reports"]["C"]["action"] != "respect_paused"''',
        '''    for tag in ("B", "C"):
        assert third["reports"][tag]["action"] != "respect_paused", (
            tag,
            third["reports"][tag]["action"],
        )
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]["action"]
    assert third["resume_calls"] == 1, third["worker"]["events"]
    assert third["final_lease"]["refcount_exists"] is False''',
    ),
    # F-L8b-W2: A's crash lands before its pause, so B finds the worker running and
    # needs no resume of its own; only B's own exit resumes.
    (
        '''    assert s["reports"]["B"]["action"] == "released_last", s["reports"]["B"]["action"]
    assert s["reports"]["B"]["action"] != "respect_paused"
    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    assert s["reports"]["B"]["action"] == "released_last", s["reports"]["B"]["action"]
    assert s["reports"]["B"]["action"] != "respect_paused"
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False
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
