"""Bring the acquire dispatch to the ADR-9b shape: a LIVE peer's cycle is joined.

ADR-9b (I-04-C, frozen): "live leases route to the same branch even when the status
still says enabled; one pause per cycle", and a participant joining a cycle that
another live process owns must NOT stop the worker again.  The R5 fail-closed path is
for an ownership record we cannot attribute to a live holder - not for a peer that is
simply a different process.
"""

from __future__ import annotations

import pathlib
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''        if self._owner_lease_live(state, live):
            # The ownership record names a holder that is NOT this incarnation while
            # another live lease keeps the cycle alive.  We cannot attribute it, and
            # the ADR-9b evidence ("a request of ours left a pause behind") does not
            # apply: fail closed rather than guess.  This is the R5 terminal state,
            # resolved by a human or by wiki-side evidence (ADR-8 / section 8 O-2).
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and held by another participant "
                f"(owner lease {(state.owner or {}).get('lease_id')}, generation "
                f"{state.generation}); the ownership record does not name a holder we can "
                "attribute, so nothing was written and no worker command was issued",
            )
'''
NEW = '''        if self._owner_lease_live(state, live):
            # ADR-9b: a LIVE holder keeps the cycle alive, so this request JOINS it
            # instead of stopping the worker a second time.  The cycle is already
            # paused, so a peer's request needs no pause of its own.  (This is also what
            # makes the mixed-fleet/foreign-live holder case safe: we add a lease and
            # touch nothing else, and the ownership record is left exactly as found.)
            _lease_journal(
                self.root,
                "joined_live_holder",
                lease_id=self.lease_id,
                owner=(state.owner or {}).get("lease_id"),
                generation=state.generation,
            )
            self._join_cycle_locked(state, live)
            return
'''
text = PATCHER.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATCHER.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("ADR-9b live-holder join installed")
