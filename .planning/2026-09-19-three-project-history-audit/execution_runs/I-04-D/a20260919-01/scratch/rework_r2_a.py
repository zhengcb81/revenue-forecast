"""Rework r2 — fix the reviewer's P1 findings.

Root cause of F1/F2/F3: the gate matcher in _Hooks.__call__ never compares the gate's
NAME with the hook point, so `gate:enter-complete@A` fired at A's FIRST hook
(`enter-acquired`) and every case that armed an enter gate was actually parked at the
wrong place.  That is why F-L6b/W1b could never see the interleaving the oracle froze.

This script also removes the temporary stderr breadcrumb/traceback the diagnostics left
behind, and re-orders the scheduler's fence releases so a participant is never woken
before the participant it must overlap with has been parked.
"""

from __future__ import annotations

import pathlib
import re
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)
SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)
TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

# ---------------------------------------------------------------- 1. gate fix + cleanup
text = PATCHER.read_text(encoding="utf-8")

OLD_GATE = """        for (name, gate_tag), timeout in self.gates.items():
            if not self._applies(gate_tag):
                continue
            base = self._fence_name(name, gate_tag)
            reached = self.dir / f"{base}.reached"
            if not reached.exists():
                reached.write_text("reached", encoding="utf-8")
                try:
                    import traceback as _tb

                    sys.stderr.write(
                        f"[i04d] gate {base} published by pid {os.getpid()} at {point}\\n"
                        + "".join(_tb.format_stack()[-6:])
                    )
                    sys.stderr.flush()
                except Exception:  # noqa: BLE001
                    pass
            fence = self.dir / f"{base}.fence"
"""
NEW_GATE = """        for (name, gate_tag), timeout in self.gates.items():
            if name != point:
                # A gate is armed at ONE named point.  Without this comparison the gate
                # fires at the participant's FIRST hook instead (enter-acquired), which
                # parks the participant at the wrong place and silently destroys the
                # interleaving the schedule was written to pin.
                continue
            if not self._applies(gate_tag):
                continue
            base = self._fence_name(name, gate_tag)
            reached = self.dir / f"{base}.reached"
            if not reached.exists():
                reached.write_text("reached", encoding="utf-8")
            fence = self.dir / f"{base}.fence"
"""
if OLD_GATE not in text:
    print("GATE PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD_GATE, NEW_GATE, 1)

OLD_ARRIVE = """        for name, arrive_tag in self.arrivals:
            if not self._applies(arrive_tag):
                continue
"""
NEW_ARRIVE = """        for name, arrive_tag in self.arrivals:
            if name != point:
                continue  # same rule as the gates: an arrival marker names one point
            if not self._applies(arrive_tag):
                continue
"""
if OLD_ARRIVE not in text:
    print("ARRIVE PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD_ARRIVE, NEW_ARRIVE, 1)

# the docstring must describe the corrected contract
OLD_DOC = """      ``gate:<name>[@<tag>][@<timeout>]``  publish ``gate.<name>[@<tag>].reached``
                                           and wait for ``gate.<name>.fence``"""
NEW_DOC = """      ``gate:<point>[@<tag>][@<timeout>]``  at the hook POINT called ``<point>``,
                                           publish ``gate.<point>[@<tag>].reached`` and
                                           wait for ``gate.<point>.fence``
      ``arrive:<point>[@<tag>]``            at that point, publish
                                           ``arrive.<point>.<tag>`` and continue"""
if OLD_DOC in text:
    text = text.replace(OLD_DOC, NEW_DOC, 1)
PATCHER.write_text(text, encoding="utf-8")
print("gate/arrival matching fixed; breadcrumb removed")

# ---------------------------------------------------------------- 2. scheduler release order
sched = SCHED.read_text(encoding="utf-8")

# F-L5: B must be parked for real before A is let out, otherwise A wins by construction.
OLD_L5 = """    # A leaves its enter critical section (releasing the lock) and parks in release.
    run.release("enter-complete", "A")
    assert run.wait_reached("release-read", "A"), "A never reached its release critical section"
    # B now owns the lock and is parked with its lease persisted.
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter critical section"
"""
NEW_L5 = """    # A leaves its enter critical section (releasing the lock) and parks in release.
    run.release("enter-complete", "A")
    assert run.wait_reached("release-read", "A"), "A never reached its release critical section"
    # B now owns the lock and is parked with its lease persisted.  B is released only
    # AFTER A is parked, so the ledger holds both leases when the scheduler reads it.
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter critical section"
"""
if OLD_L5 in sched:
    sched = sched.replace(OLD_L5, NEW_L5, 1)
    print("F-L5 release order confirmed")

# F-L6b: same rule - park B, read the overlap, then release B, then let A go.
OLD_L6B = """    run.spawn("B", hooks="gate:enter-complete@B,gate:release-read@B", resume_wait=0.2, graceful=0.2)
    run.release("enter-complete", "A")
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter critical section"
    run.meta["b_joined"] = {"lease": run.summarise()["final_lease"]}
    run.release("enter-complete", "B")
    run.reap("A")
    run.meta["after_a_exit"] = {"lease": run.summarise()["final_lease"]}
    assert run.wait_reached("release-read", "B"), "B never reached its release critical section"
    run.release("release-read", "B")
    run.reap("B")"""
NEW_L6B = """    run.spawn("B", hooks="gate:enter-complete@B,gate:release-read@B", resume_wait=0.2, graceful=0.2)
    run.release("enter-complete", "A")
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter critical section"
    # B is parked with its lease durable while A is ALSO still inside its own scope, so
    # this snapshot is the overlap the case is about.
    run.meta["b_joined"] = {"lease": run.summarise()["final_lease"]}
    run.release("enter-complete", "B")
    run.reap("A")
    run.meta["after_a_exit"] = {"lease": run.summarise()["final_lease"]}
    assert run.wait_reached("release-read", "B"), "B never reached its release critical section"
    run.release("release-read", "B")
    run.reap("B")"""
if OLD_L6B in sched:
    sched = sched.replace(OLD_L6B, NEW_L6B, 1)
    print("F-L6b release order confirmed")

# F-L8a-W1b: B must still hold the cycle when C joins.  Park B INSIDE its enter, spawn
# C, and only release B after C has come and gone.
OLD_W1B = """    run.spawn("B", hooks="gate:enter-complete@B", resume_wait=0.2, graceful=0.2)
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter"
    run.meta["b_state"] = {
        "lease": run.summarise()["final_lease"],
        "worker_state": _read_json(run.state),
    }
    run.release("enter-complete", "B")
    run.spawn("C", resume_wait=0.2, graceful=0.2)
    run.reap("C")
    run.meta["after_c_exit"] = {"lease": run.summarise()["final_lease"]}
    run.reap("B")"""
NEW_W1B = """    run.spawn("B", hooks="gate:enter-complete@B", resume_wait=0.2, graceful=0.2)
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter"
    run.meta["b_state"] = {
        "lease": run.summarise()["final_lease"],
        "worker_state": _read_json(run.state),
    }
    # B stays parked (its lease is in the ledger) while C comes and goes, so C really
    # rejoins a live cycle instead of opening its own.
    run.spawn("C", resume_wait=0.2, graceful=0.2)
    run.reap("C")
    run.meta["after_c_exit"] = {"lease": run.summarise()["final_lease"]}
    run.release("enter-complete", "B")
    run.reap("B")"""
if OLD_W1B not in sched:
    print("W1B PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD_W1B, NEW_W1B, 1)
print("F-L8a-W1b release order fixed")
SCHED.write_text(sched, encoding="utf-8")

# ---------------------------------------------------------------- 3. the three broken assertions
test = TEST.read_text(encoding="utf-8")

# F1: line 110 reads a key F-L5 never writes.
test, n1 = re.subn(
    r'    joined = s\["participants"\]\["b_joined"\]\["lease"\]\n'
    r'    assert reports\["B"\]\["lease_id"\] in joined\["lease_set"\], joined\n'
    r'    assert reports\["A"\]\["lease_id"\] in joined\["lease_set"\], joined\n'
    r'    assert len\(joined\["lease_set"\]\) == 2, joined\n',
    '    joined = reports["B"]["after_enter"]\n'
    '    assert reports["B"]["lease_id"] in joined["lease_set"], joined\n'
    '    assert reports["A"]["lease_id"] in joined["lease_set"], joined\n'
    '    assert len(joined["lease_set"]) == 2, joined\n',
    test,
)
test, n2 = re.subn(
    r'    snapshots = \[reports\["A"\]\["after_enter"\], reports\["B"\]\["after_enter"\]\]\n'
    r'    a_id, b_id = reports\["A"\]\["lease_id"\], reports\["B"\]\["lease_id"\]\n'
    r'    assert any\(\n'
    r'        a_id in snap\["lease_set"\] and b_id in snap\["lease_set"\] for snap in snapshots\n'
    r'    \), snapshots\n',
    '    joined = reports["B"]["after_enter"]\n'
    '    assert reports["B"]["lease_id"] in joined["lease_set"], joined\n'
    '    assert reports["A"]["lease_id"] in joined["lease_set"], joined\n'
    '    assert len(joined["lease_set"]) == 2, joined\n',
    test,
)
print(f"F1 replacements: {n1} + {n2}")

# F3: the W1b block referenced an undefined name and asserted an impossible pair.
OLD_W1B_TEST = re.compile(
    r"    third = s\[\"I04D-CASE-F-L8a-W1b\"\]\n(?:.*?\n)*?    assert \(before_b\[\"owner\"\] or \{\}\)\.get\(\"lease_id\"\) == third\[\"reports\"\]\[\"B\"\]\[\"lease_id\"\]\n"
)
NEW_W1B_TEST = '''    third = s["I04D-CASE-F-L8a-W1b"]
    assert not third["harness_error"], third["harness_error"]
    # C rejoins a cycle B is still holding, so C leaves the ledger populated.
    for tag in ("B", "C"):
        assert third["reports"][tag]["action"] != "respect_paused", (
            tag,
            third["reports"][tag]["action"],
        )
    assert third["reports"]["C"]["action"] == "released_joined", third["reports"]["C"]
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]
    assert third["pause_calls"] == 1, third["worker"]["events"]
    assert third["resume_calls"] == 1, third["worker"]["events"]
    before_b = third["participants"]["after_c_exit"]["lease"]
    assert third["reports"]["B"]["lease_id"] in before_b["lease_set"], before_b
    assert third["reports"]["A"]["lease_id"] not in before_b["lease_set"], before_b
    assert (before_b["owner"] or {}).get("lease_id") == third["reports"]["B"]["lease_id"]
    assert third["final_lease"]["refcount_exists"] is False, third["final_lease"]
'''
test, n3 = OLD_W1B_TEST.subn(NEW_W1B_TEST, test)
print(f"F3 replacement: {n3}")
TEST.write_text(test, encoding="utf-8")
