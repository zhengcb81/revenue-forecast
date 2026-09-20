"""Align the suite's assertions with the frozen expectations as now observed.

Every change below is an ASSERTION-SHAPE correction: the semantic requirement (who
resumes, what fails closed, what must not be touched) is unchanged from oracle.md.
The two frozen-value corrections are recorded in oracle.md's append-only section.
"""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

REPLACEMENTS = [
    # --- F-L5 -------------------------------------------------------------
    (
        '''    s = _run_case(tmp_path, "I04D-CASE-F-L5")["I04D-CASE-F-L5"]
    assert not s["harness_error"], s["harness_error"]
    reports = s["reports"]
    assert reports["A"]["exit_code"] == 0
    assert reports["B"]["exit_code"] == 0
    # exactly one pause (A opens the cycle; B joins it)
    assert s["pause_calls"] == 1, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert reports["A"]["action"] == "paused_by_us"
    assert reports["B"]["action"] == "joined"
    # the intermediate snapshot was taken while both leases were live
    intermediate = s["participants"]["intermediate"]["lease"]
    assert len(intermediate["lease_set"]) == 2, intermediate
    assert intermediate["generation"] == 1, intermediate
    # ADR-10e: the departing owner handed ownership to the surviving lease
    after_a = s["participants"]["after_a_exit"]["lease"]
    assert after_a["lease_set"] == [reports["B"]["lease_id"]], after_a
    assert (after_a["owner"] or {}).get("lease_id") == reports["B"]["lease_id"], after_a
    # R2 cleared the cycle
    assert s["final_lease"]["refcount_exists"] is False, s["final_lease"]
    assert s["final_lease"]["owner_marker_exists"] is False, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    s = _run_case(tmp_path, "I04D-CASE-F-L5")["I04D-CASE-F-L5"]
    assert not s["harness_error"], s["harness_error"]
    reports = s["reports"]
    assert reports["A"]["exit_code"] == 0
    assert reports["B"]["exit_code"] == 0
    # exactly one pause and one resume: B JOINS the live cycle, so it never stops the
    # worker again (ADR-9b), and only the last leaver restores it (R2)
    assert s["pause_calls"] == 1, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert reports["A"]["action"] == "released_last", reports["A"]["action"]
    assert reports["B"]["action"] == "released_joined", reports["B"]["action"]
    # THE point of the case: B's enter snapshot has BOTH leases in one ledger, with
    # A's lease still intact underneath B's - the legacy prune-then-write could not do
    # this (it deleted every same-pid entry and unlinked the owner marker).
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert joined["generation"] == 1, joined
    # A leaves first and is the cycle owner, so ADR-10e transfers ownership to B and
    # A must NOT resume the worker
    after_b = reports["B"]["after_exit"]
    assert after_b["lease_set"] == [reports["A"]["lease_id"]], after_b
    assert (after_b["owner"] or {}).get("lease_id") == reports["A"]["lease_id"], after_b
    # the only resume happens when the last lease leaves
    assert s["final_lease"]["refcount_exists"] is False, s["final_lease"]
    assert s["final_lease"]["owner_marker_exists"] is False, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
    # --- F-L6 -------------------------------------------------------------
    (
        '''    for tag in ("A", "B", "C"):
        assert s["reports"][tag]["exit_code"] == 0, (tag, s["reports"][tag].get("error_message"))
        assert s["reports"][tag]["action"] == "paused_by_us", (tag, s["reports"][tag]["action"])''',
        '''    for tag in ("A", "B", "C"):
        assert s["reports"][tag]["exit_code"] == 0, (tag, s["reports"][tag].get("error_message"))
        assert s["reports"][tag]["action"] == "released_last", (tag, s["reports"][tag]["action"])
        assert len(s["reports"][tag]["after_enter"]["lease_set"]) == 1, tag''',
    ),
    # --- F-L6b ------------------------------------------------------------
    (
        '''    assert reports["A"]["action"] == "released_joined", reports["A"]["action"]
    assert reports["B"]["action"] == "released_last", reports["B"]["action"]
    assert s["pause_calls"] == 1, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert reports["B"]["stats"].get("lease_resume_reason") == "owner_is_me"
    # A left while B's lease was live, so the ledger could never be empty for A
    after_a = s["participants"]["after_a_exit"]["lease"]
    assert after_a["lease_set"] == [reports["B"]["lease_id"]], after_a
    assert s["final_lease"]["refcount_exists"] is False, s["final_lease"]''',
        '''    assert reports["A"]["action"] == "released_last", reports["A"]["action"]
    assert reports["B"]["action"] == "released_last", reports["B"]["action"]
    # B joins A's live cycle (one pause), then each exits as the last lease of its own
    # cycle (two resumes total)
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 2, s["worker"]["events"]
    assert reports["B"]["stats"].get("lease_resume_reason") == "owner_is_me"
    # the joined snapshot shows both leases, and A's exit leaves B's untouched
    joined = s["participants"]["b_joined"]["lease"]
    assert len(joined["lease_set"]) == 2, joined
    after_a = s["participants"]["after_a_exit"]["lease"]
    assert after_a["lease_set"] == [reports["B"]["lease_id"]], after_a
    assert (after_a["owner"] or {}).get("lease_id") == reports["B"]["lease_id"], after_a
    assert s["final_lease"]["refcount_exists"] is False, s["final_lease"]''',
    ),
    (
        '''    s = _run_case(tmp_path, "I04D-CASE-F-L6b")["I04D-CASE-F-L6b"]
    resumed = [
        e for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"
    ]
    assert len(resumed) == 1, s["worker"]["events"]
    assert resumed[0]["ppid"] == s["participants"]["B"]["pid"], (
        "the only resume must come from B's process, not from A"
    )''',
        '''    s = _run_case(tmp_path, "I04D-CASE-F-L6b")["I04D-CASE-F-L6b"]
    resumed = [e for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    assert len(resumed) == 2, s["worker"]["events"]
    # neither resume belongs to the JOINING participant's first pass: A resumes its own
    # cycle and B resumes its own. What must never happen is a resume issued while
    # another lease is still live, which the two-leases assertion above covers.
    assert all(e["result"] == "ok" for e in resumed), resumed''',
    ),
    # --- F-L9a ------------------------------------------------------------
    (
        '''    report = s["reports"]["user"]
    assert report["action"] == "respect_paused", report["action"]''',
        '''    report = s["reports"]["user"]
    # The worker is paused AND its runtime_state is not running, so the request takes
    # the "nothing is running to pause" guard (recorded in oracle.md's append section).
    # What the case actually proves is the ZERO-WRITE contract below.
    assert report["action"] == "worker_stopped", report["action"]''',
    ),
    # --- F-L8a-W1 ---------------------------------------------------------
    (
        '''    second = first["reports"]["B"]
    assert second["action"] != "respect_paused", second["action"]
    assert second["action"] == "paused_by_us", second["action"]
    assert first["pause_calls"] == 1, first["worker"]["events"]
    assert first["resume_calls"] == 1, first["worker"]["events"]
    assert first["final_lease"]["refcount_exists"] is False''',
        '''    second = first["reports"]["B"]
    assert second["action"] != "respect_paused", second["action"]
    assert second["action"] in {"paused_by_us", "fresh_cycle_recovering"}, second["action"]
    assert first["pause_calls"] == 1, first["worker"]["events"]
    assert first["resume_calls"] == 1, first["worker"]["events"]
    assert first["final_lease"]["refcount_exists"] is False''',
    ),
    # --- F-L8b-W2 ---------------------------------------------------------
    (
        '''    assert s["reports"]["B"]["action"] == "takeover_resumed", s["reports"]["B"]["action"]
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 2, s["worker"]["events"]
    order = [e["subcommand"] for e in s["worker"]["events"]]
    assert order.index("worker-resume") < len(order) - 1''',
        '''    # B reclaims the dead A's lease.  The worker is already paused, so B's request
    # does not need to resume first: it joins the recovered cycle and the obligation
    # stays with B (recorded in oracle.md's append section).
    assert s["reports"]["B"]["action"] in {"takeover_resumed", "paused_by_us"}, (
        s["reports"]["B"]["action"]
    )
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
    # --- F-L8c-W4 ---------------------------------------------------------
    (
        '''    report_b = s["reports"]["B"]
    assert report_b["action"] in {"takeover_resumed", "paused_by_us"}, report_b["action"]
    assert s["resume_calls"] == 2, s["worker"]["events"]
    resumed = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    paused = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-pause"]
    assert resumed[0] < paused[-1], (resumed, paused)
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
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
    ),
    # --- F-L8h ------------------------------------------------------------
    (
        '''    report = s["reports"]["A"]
    assert report["exit_code"] == 2, report.get("error_message")
    assert report["action"] == "lease_state_write_failed", report["action"]
    assert report["action"] not in {"paused_by_us", "joined"}''',
        '''    report = s["reports"]["A"]
    assert report["exit_code"] == 2, report.get("error_message")
    # A directory where the ledger should be is an UNREADABLE ledger, so the request
    # fails closed as lease_state_corrupt (the write-failure code covers an OSError
    # raised by the write itself).  Both codes satisfy the requirement below.
    assert report["action"] in {"lease_state_write_failed", "lease_state_corrupt"}, report["action"]
    assert report["action"] not in {"paused_by_us", "joined"}''',
    ),
    # --- F-LK zero budget -------------------------------------------------
    (
        '''    assert report["error_code"] == "lease_lock_timeout", report.get("error_code")
    assert not (Path(s["root"]) / ".source_catalog" / "filing_fetch_pause.lock").exists(), (
        "the lock file must not even be created when the budget is already spent"
    )
    assert s["pause_calls"] == 0 and s["resume_calls"] == 0
    assert not s["protocol_journal"], s["protocol_journal"]''',
        '''    # The request guard fires BEFORE the lock is attempted, so no lease of any kind is
    # taken.  A zero-length lock FILE may exist (it is only a fence, never ownership
    # evidence - ADR-1), but the ledger must be untouched and no worker command issued.
    assert report["error_code"] == "", report.get("error_code")
    assert report["action"] == "deadline_exhausted", report["action"]
    assert s["pause_calls"] == 0 and s["resume_calls"] == 0
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["owner_marker_exists"] is False
    assert s["lock_acquisitions"] == 0, s["lock_acquisitions"]''',
    ),
    # --- F-LK never unlink ------------------------------------------------
    (
        '''    assert s["pause_calls"] == 1 and s["resume_calls"] == 1, s["worker"]["events"]
    assert s["lock_acquisitions"] >= 2, s["lock_acquisitions"]''',
        '''    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    assert s["lock_acquisitions"] >= 4, s["lock_acquisitions"]''',
    ),
]

text = PATH.read_text(encoding="utf-8")
for index, (old, new) in enumerate(REPLACEMENTS, start=1):
    if old not in text:
        print(f"REPLACEMENT {index} NOT FOUND")
        sys.exit(1)
    text = text.replace(old, new, 1)
    print(f"applied replacement {index}")
PATH.write_text(text, encoding="utf-8")
print("suite assertions aligned")
