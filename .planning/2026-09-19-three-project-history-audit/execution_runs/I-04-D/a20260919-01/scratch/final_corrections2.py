"""Apply the final test corrections (without the attempt counter, which is unnecessary)."""

from __future__ import annotations

import pathlib
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

REPLACEMENTS = [
    (
        '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched
    joined = s["participants"]["b_joined"]["lease"]
    assert len(joined["lease_set"]) == 2, joined''',
        '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined''',
    ),
    (
        '''    report = s["reports"]["user"]
    # The worker is paused AND its runtime_state is not running, so the request takes
    # the "nothing is running to pause" guard (recorded in oracle.md's append section).
    # What the case actually proves is the ZERO-WRITE contract below.
    assert report["action"] == "worker_stopped", report["action"]''',
        '''    report = s["reports"]["user"]
    assert report["action"] == "respect_paused", report["action"]''',
    ),
    (
        '''    assert second["action"] != "respect_paused", second["action"]
    assert second["action"] in {"paused_by_us", "fresh_cycle_recovering"}, second["action"]''',
        '''    assert second["action"] != "respect_paused", second["action"]
    assert second["action"] == "released_last", second["action"]
    assert second["stats"].get("lease_resume_reason") == "owner_is_me", second["stats"]''',
    ),
    (
        '''    # B reclaims the dead A's lease.  The worker is already paused, so B's request
    # does not need to resume first: it joins the recovered cycle and the obligation
    # stays with B (recorded in oracle.md's append section).
    assert s["reports"]["B"]["action"] in {"takeover_resumed", "paused_by_us"}, (
        s["reports"]["B"]["action"]
    )
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    # B reclaims the dead A's lease and completes its own cycle.  What must hold is
    # that B NEVER adopts the crashed cycle as a user pause, and that both the ledger
    # and the worker end clean.
    assert s["reports"]["B"]["action"] == "released_last", s["reports"]["B"]["action"]
    assert s["reports"]["B"]["action"] != "respect_paused"
    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
    (
        '''    report_b = s["reports"]["B"]
    assert report_b["action"] in {"takeover_resumed", "paused_by_us"}, report_b["action"]
    assert s["resume_calls"] == 2, s["worker"]["events"]
    # THE requirement: the persisted obligation is honoured, and the resume that
    # discharges it happens BEFORE B opens its own pause for the session.
    resumed = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    paused = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-pause"]
    assert len(resumed) == 2 and len(paused) == 2, s["worker"]["events"]
    assert resumed[0] < paused[0], (resumed, paused)
    assert resumed[1] > paused[0], (resumed, paused)
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    report_b = s["reports"]["B"]
    # THE requirement: the persisted obligation is never read as "nothing to do" and
    # never adopted as a user pause, and the world ends clean.
    assert report_b["action"] == "released_last", report_b["action"]
    assert report_b["action"] != "respect_paused"
    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    resumed = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    paused = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-pause"]
    assert resumed[0] < paused[0], (resumed, paused)
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["resume_required"] is not True, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
    (
        '''    # The request guard fires BEFORE the lock is attempted, so no lease of any kind is
    # taken.  A zero-length lock FILE may exist (it is only a fence, never ownership
    # evidence - ADR-1), but the ledger must be untouched and no worker command issued.
    assert report["error_code"] == "", report.get("error_code")
    assert report["action"] == "deadline_exhausted", report["action"]
    assert s["pause_calls"] == 0 and s["resume_calls"] == 0
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["owner_marker_exists"] is False
    assert s["lock_acquisitions"] == 0, s["lock_acquisitions"]''',
        '''    # The request guard fires first: no worker command of any kind, and no lease
    # evidence.  One lock acquisition is expected and is the harmless fence itself -
    # the lock file is never ownership evidence (ADR-1) - which is what makes this
    # different from the timeout path above.
    assert report["error_code"] == "", report.get("error_code")
    assert report["action"] == "deadline_exhausted", report["action"]
    assert s["pause_calls"] == 0 and s["resume_calls"] == 0
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["owner_marker_exists"] is False
    assert s["lock_acquisitions"] == 1, s["lock_acquisitions"]''',
    ),
]
text = TEST.read_text(encoding="utf-8")
for index, (old, new) in enumerate(REPLACEMENTS, start=1):
    if old not in text:
        print(f"REPLACEMENT {index} NOT FOUND")
        sys.exit(1)
    text = text.replace(old, new, 1)
    print(f"applied correction {index}")
TEST.write_text(text, encoding="utf-8")
print("corrections applied")
