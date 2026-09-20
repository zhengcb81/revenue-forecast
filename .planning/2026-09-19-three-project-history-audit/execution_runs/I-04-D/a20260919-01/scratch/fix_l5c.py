"""F-L5 final form: two live leases in one ledger, A's release does not disturb B.

The enter critical section holds the OS lock end to end (ADR-11), so a second
participant physically cannot register while the first is inside it: B necessarily
opens its own cycle after A's exit.  What F-L5 must therefore assert is the property
the legacy prune-then-write could NOT provide - two leases coexisting in the ledger,
and A's release removing exactly its own lease and resuming only its own cycle.
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
    """Two real processes, two live leases in ONE ledger (card F-L5 + ADR-11).

    A holds the enter critical section end to end, so B cannot register while A is
    inside it; B is therefore blocked on the OS lock while A parks, and opens its own
    cycle the moment A leaves.  The scheduler then holds B at its ``enter-complete``
    (its lease durable) and lets A run its whole release: A must remove ONLY its own
    lease and resume ONLY its own cycle, leaving B's lease byte-intact.  Two leases
    coexisting in one ledger is exactly what the legacy prune-then-write could not do.
    """
    run.spawn("A", hooks="gate:enter-complete@A", resume_wait=0.2, graceful=0.2)
    assert run.wait_reached("enter-complete", "A"), "A never finished its enter critical section"
    run.meta["a_entered_only"] = {"lease": run.summarise()["final_lease"]}
    run.spawn("B", hooks="gate:enter-complete@B", resume_wait=0.2, graceful=0.2)
    run.release("enter-complete", "A")
    run.reap("A")
    run.meta["after_a_exit"] = {
        "lease": run.summarise()["final_lease"],
        "worker_state": _read_json(run.state),
    }
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter critical section"
    run.meta["b_entered"] = {"lease": run.summarise()["final_lease"]}
    run.release("enter-complete", "B")
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
print("case_f_l5 finalised")
