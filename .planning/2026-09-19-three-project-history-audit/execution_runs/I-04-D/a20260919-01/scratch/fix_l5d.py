"""F-L5: keep the first participant alive past its enter, using a harness-side hold.

``--hold-for <file>`` makes a participant, right after its enter returns, publish
``signal.<tag>.ready`` and wait for a released marker before leaving the scope.  That
is harness code (like ``--wait-for``), not instrumentation of the protocol, and the
legacy baseline supports it too because it only uses the context manager.
"""

from __future__ import annotations

import pathlib
import re
import sys

PART = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_participant.py"
)
SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

part = PART.read_text(encoding="utf-8")
OLD = '''    parser.add_argument("--wait-for", default="")
'''
NEW = '''    parser.add_argument("--wait-for", default="")
    parser.add_argument("--hold-for", default="")
    parser.add_argument("--hold-timeout", type=float, default=60.0)
'''
if OLD not in part:
    print("ARG PATTERN NOT FOUND")
    sys.exit(1)
part = part.replace(OLD, NEW, 1)

OLD2 = '''            if args.wait_for:'''
NEW2 = '''            if args.hold_for:
                # Harness-side hold: publish "we are inside the scope" and wait for the
                # scheduler's released marker before leaving.  It only uses the context
                # manager, so the legacy baseline can be driven this way too.
                released = Path(args.hold_for)
                (released.parent / f"signal.{args.tag}.ready").write_text(
                    "ready", encoding="utf-8"
                )
                report["hold_released_marker"] = str(released)
                limit = time.monotonic() + args.hold_timeout
                while not released.exists():
                    if time.monotonic() > limit:
                        report["hold_timed_out"] = True
                        break
                    time.sleep(0.005)
                report["hold_released"] = released.exists()
                report["held_snapshot"] = _snapshot(root)
            if args.wait_for:'''
if OLD2 not in part:
    print("HOLD PATTERN NOT FOUND")
    sys.exit(1)
part = part.replace(OLD2, NEW2, 1)
PART.write_text(part, encoding="utf-8")
print("participant: --hold-for installed")

sched = SCHED.read_text(encoding="utf-8")
OLD3 = '''        wait_for: str = "",
        wait_timeout: float = 60.0,
'''
NEW3 = '''        wait_for: str = "",
        wait_timeout: float = 60.0,
        hold_for: str = "",
        hold_timeout: float = 60.0,
'''
if OLD3 not in sched:
    print("SPAWN PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD3, NEW3, 1)

OLD4 = '''        if wait_for:
            argv.extend(["--wait-for", str(wait_for), "--wait-timeout", str(wait_timeout)])
'''
NEW4 = '''        if wait_for:
            argv.extend(["--wait-for", str(wait_for), "--wait-timeout", str(wait_timeout)])
        if hold_for:
            argv.extend(["--hold-for", str(hold_for), "--hold-timeout", str(hold_timeout)])
'''
if OLD4 not in sched:
    print("ARGV PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD4, NEW4, 1)

NEW_L5 = '''def case_f_l5(run: CaseRun) -> None:
    """Two real processes, two live leases in ONE ledger (card F-L5 + ADR-11).

    A is HELD ALIVE inside its scope (the harness keeps it there), so B's whole
    register-then-pause sequence happens while A's lease is still in the ledger: at the
    moment the scheduler reads it, both leases are live.  A then leaves first; because
    A is the cycle's owner and B is still live, ADR-10e transfers ownership to B and A
    must NOT resume the worker.  B resumes when it leaves.  That is exactly the
    sequence the legacy prune-then-write could not produce - it deleted every same-pid
    entry and unlinked the owner marker, so the worker was woken under a live lease.
    """
    a_release = run.dir / "hold.A.release"
    run.spawn("A", resume_wait=0.2, graceful=0.2, hold_for=str(a_release))
    assert run.wait_snapshot("A"), "A never reached the scope body"
    run.meta["a_holding"] = {"lease": run.summarise()["final_lease"]}
    run.spawn("B", resume_wait=0.2, graceful=0.2)
    run.reap("B")
    run.meta["after_b_exit"] = {"lease": run.summarise()["final_lease"]}
    a_release.write_text("go", encoding="utf-8")
    run.reap("A")
'''

text = sched
pattern = re.compile(r"^def case_f_l5\(run: CaseRun\) -> None:\n(?:.*?\n)*?\n\n", re.MULTILINE)
match = pattern.search(text)
if not match:
    print("L5 PATTERN NOT FOUND")
    sys.exit(1)
text = text[: match.start()] + NEW_L5 + "\n\n" + text[match.end() :]
SCHED.write_text(text, encoding="utf-8")
print("case_f_l5 rewritten with a harness-side hold")
