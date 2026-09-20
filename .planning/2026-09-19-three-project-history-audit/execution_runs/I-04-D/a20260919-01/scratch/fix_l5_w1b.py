"""Final case fixes: F-L5 without the arrival marker; F-L8a-W1b without a deadlock."""

from __future__ import annotations

import pathlib
import re
import sys

SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

NEW_L5 = '''def case_f_l5(run: CaseRun) -> None:
    """Two real processes; B registers BEFORE A releases (card F-L5).

    A parks at ``enter-complete`` (its lease is durable, but its enter critical section
    is still open, so it still holds the OS lock) only long enough for B to be spawned;
    A then leaves the critical section and parks inside its RELEASE critical section.
    B acquires the lock that A just released and parks at its own ``enter-complete``,
    which is reached with B's lease already persisted.  At the moment the scheduler
    reads the ledger BOTH leases are therefore live - the state the legacy
    prune-then-write could not represent.

    The two leases overlap because A's park and B's park are both inside the lock, not
    because of timing luck: nothing downstream of A's park can run until A is released.
    """
    run.spawn(
        "A",
        hooks="gate:enter-complete@A,gate:release-read@A",
        resume_wait=0.2,
        graceful=0.2,
    )
    assert run.wait_reached("enter-complete", "A"), "A never finished its enter critical section"
    run.meta["a_entered"] = {"lease": run.summarise()["final_lease"]}
    run.spawn(
        "B",
        hooks="gate:enter-complete@B",
        resume_wait=0.2,
        graceful=0.2,
    )
    run.release("enter-complete", "A")
    assert run.wait_reached("release-read", "A"), "A never reached its release critical section"
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter critical section"
    run.meta["intermediate"] = {
        "lease": run.summarise()["final_lease"],
        "worker_state": _read_json(run.state),
    }
    run.release("enter-complete", "B")
    run.release("release-read", "A")
    run.reap("A")
    run.meta["after_a_exit"] = {"lease": run.summarise()["final_lease"]}
    run.reap("B")
'''

NEW_W1B = '''def case_f_l8a_w1b(run: CaseRun) -> None:
    """W1 crash, then a THIRD participant joins and leaves first.

    A is gone (its pid is dead), B reclaimed A's orphan lease and owns the cycle.
    B parks inside its enter critical section, which keeps its lease in the ledger for
    as long as the scheduler needs; C then joins and leaves.  B must still be the one
    that resumes - a peer's exit must never steal the resume from the owner.
    """
    run.spawn("A", hooks="crash:after-refcount-before-owner:90")
    run.reap("A")
    run.spawn("B", hooks="gate:enter-complete@B", resume_wait=0.2, graceful=0.2)
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter"
    run.meta["b_state"] = {
        "lease": run.summarise()["final_lease"],
        "worker_state": _read_json(run.state),
    }
    run.release("enter-complete", "B")
    run.spawn("C", resume_wait=0.2, graceful=0.2)
    run.reap("C")
    run.meta["after_c_exit"] = {"lease": run.summarise()["final_lease"]}
    run.reap("B")
'''

text = SCHED.read_text(encoding="utf-8")
for name, new in (("case_f_l5", NEW_L5), ("case_f_l8a_w1b", NEW_W1B)):
    pattern = re.compile(rf"^def {name}\(run: CaseRun\) -> None:\n(?:.*?\n)*?\n\n", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        print(f"PATTERN NOT FOUND: {name}")
        sys.exit(1)
    text = text[: match.start()] + new + "\n\n" + text[match.end() :]
    print(f"replaced {name}")
SCHED.write_text(text, encoding="utf-8")
