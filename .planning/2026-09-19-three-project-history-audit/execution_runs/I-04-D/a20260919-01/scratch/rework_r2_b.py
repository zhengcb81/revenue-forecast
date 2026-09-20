"""F-L8a-W1b: park B in its RELEASE critical section so C can rejoin reliably."""

from __future__ import annotations

import pathlib
import sys

SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

NEW = '''def case_f_l8a_w1b(run: CaseRun) -> None:
    """W1 crash, then a THIRD participant rejoins the recovered cycle.

    A is gone (its pid is dead), B reclaimed A's orphan lease and owns the cycle.  B is
    parked inside its RELEASE critical section, so the worker is paused and B's lease is
    in the ledger for the whole of C's visit: C therefore joins a live cycle (R1) rather
    than opening its own, and B - the last leaver - is the one that restores the worker.
    """
    run.spawn("A", hooks="crash:after-refcount-before-owner:90")
    run.reap("A")
    run.spawn("B", hooks="gate:release-read@B", resume_wait=0.2, graceful=0.2)
    assert run.wait_reached("release-read", "B"), "B never reached its release critical section"
    run.meta["b_state"] = {
        "lease": run.summarise()["final_lease"],
        "worker_state": _read_json(run.state),
    }
    # B holds the lock here, so C cannot misread the cycle as ended.
    run.spawn("C", hooks="gate:enter-complete@C", resume_wait=0.2, graceful=0.2)
    run.release("release-read", "B")
    assert run.wait_reached("enter-complete", "C"), "C never finished its enter"
    run.release("enter-complete", "C")
    run.meta["c_joined"] = {"lease": run.summarise()["final_lease"]}
    run.reap("C")
    run.meta["after_c_exit"] = {"lease": run.summarise()["final_lease"]}
    run.reap("B")
'''

text = SCHED.read_text(encoding="utf-8")
import re

pattern = re.compile(r"^def case_f_l8a_w1b\(run: CaseRun\) -> None:\n(?:.*?\n)*?\n\n", re.MULTILINE)
match = pattern.search(text)
if not match:
    print("PATTERN NOT FOUND")
    sys.exit(1)
text = text[: match.start()] + NEW + "\n\n" + text[match.end() :]
SCHED.write_text(text, encoding="utf-8")
print("case_f_l8a_w1b rewritten")

# the matching test assertions
TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
test = TEST.read_text(encoding="utf-8")
OLD = '''    assert third["reports"]["C"]["action"] == "released_joined", third["reports"]["C"]
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]
    assert third["pause_calls"] == 1, third["worker"]["events"]
    assert third["resume_calls"] == 1, third["worker"]["events"]
    before_b = third["participants"]["after_c_exit"]["lease"]
    assert third["reports"]["B"]["lease_id"] in before_b["lease_set"], before_b
    assert third["reports"]["A"]["lease_id"] not in before_b["lease_set"], before_b
    assert (before_b["owner"] or {}).get("lease_id") == third["reports"]["B"]["lease_id"]
    assert third["final_lease"]["refcount_exists"] is False, third["final_lease"]'''
NEW = '''    assert third["reports"]["C"]["action"] == "released_joined", third["reports"]["C"]
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]
    # exactly one pause (B's reclaimed cycle) and one resume (B, its last leaver)
    assert third["pause_calls"] == 1, third["worker"]["events"]
    assert third["resume_calls"] == 1, third["worker"]["events"]
    # C really rejoined: at C's enter BOTH leases were in the ledger
    joined = third["reports"]["C"]["after_enter"]
    assert third["reports"]["B"]["lease_id"] in joined["lease_set"], joined
    assert third["reports"]["C"]["lease_id"] in joined["lease_set"], joined
    # and after C left, only B remained, with the ownership record still on B
    after_c = third["participants"]["after_c_exit"]["lease"]
    assert after_c["lease_set"] == [third["reports"]["B"]["lease_id"]], after_c
    assert (after_c["owner"] or {}).get("lease_id") == third["reports"]["B"]["lease_id"]
    assert third["final_lease"]["refcount_exists"] is False, third["final_lease"]'''
if OLD not in test:
    print("TEST PATTERN NOT FOUND")
    sys.exit(1)
TEST.write_text(test.replace(OLD, NEW, 1), encoding="utf-8")
print("W1b assertions aligned")
