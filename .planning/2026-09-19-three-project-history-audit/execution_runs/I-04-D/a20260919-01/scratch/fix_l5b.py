"""F-L5: release A's ENTER gate, then wait for A's release park, then wake B.

B cannot reach its own ``enter-complete`` while A still holds the lock, so the
scheduler must let A out of its enter critical section before waiting on B.
"""

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

    A parks at ``enter-complete`` (its lease is durable but its enter critical section
    is still open, so it still holds the OS lock) only long enough for B to be spawned.
    A is then let out of its enter critical section and parks inside its RELEASE
    critical section; B - which has been blocked on the lock all along - acquires it and
    parks at its own ``enter-complete``, reached with B's lease already persisted.  The
    scheduler releases B's park first (B only joins), then A's, so the ledger it reads
    in between holds BOTH leases: the state the legacy prune-then-write could not
    represent.
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
    # A leaves its enter critical section (releasing the lock) and parks in release.
    run.release("enter-complete", "A")
    assert run.wait_reached("release-read", "A"), "A never reached its release critical section"
    # B now owns the lock and is parked with its lease persisted.
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

text = SCHED.read_text(encoding="utf-8")
pattern = re.compile(r"^def case_f_l5\(run: CaseRun\) -> None:\n(?:.*?\n)*?\n\n", re.MULTILINE)
match = pattern.search(text)
if not match:
    print("PATTERN NOT FOUND")
    sys.exit(1)
text = text[: match.start()] + NEW_L5 + "\n\n" + text[match.end() :]
SCHED.write_text(text, encoding="utf-8")
print("case_f_l5 rewritten")
