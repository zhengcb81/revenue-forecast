"""F-L9a: a user pause with NO tool leases must be respected, not adopted.

The dispatch lacked the ADR-8 user-intent guard for the case "paused + empty ledger":
it took the "fresh cycle" path and STOPPED an already-stopped worker, then resumed it
on exit - exactly the "our pause vs the user's pause" confusion the design forbids.
Priority is now user intent > cycle hygiene > join/takeover.
"""

from __future__ import annotations

import pathlib
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''        if self._withdraw_orphan_pause_locked(status):
            self._fresh_cycle_locked(state, live, resume_required=False)
            return
        if not live:
            if state.resume_required:
                self._takeover_cycle_locked(state)
                return
            self._fresh_cycle_locked(state, live, resume_required=False)
            return
'''
NEW = '''        if not live and not state.resume_required and self._respect_user_pause_locked(state):
            # ADR-8: the worker is paused, the ledger is EMPTY and nobody owes a
            # resume, so this pause is not ours.  It is a user/external pause: leave
            # it completely alone - no lease, no pause, no resume - and let the caller
            # continue with the explicit opt-in the CLI already carries.
            self.action = "respect_paused"
            _lease_journal(self.root, "respect_paused", lease_id=self.lease_id)
            return
        if self._withdraw_orphan_pause_locked(status):
            self._fresh_cycle_locked(state, live, resume_required=False)
            return
        if not live:
            if state.resume_required:
                self._takeover_cycle_locked(state)
                return
            self._fresh_cycle_locked(state, live, resume_required=False)
            return
'''
text = PATCHER.read_text(encoding="utf-8")
if OLD not in text:
    print("DISPATCH PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = '''    def _owner_lease_live(self, state: _LeaseState, live: list[dict[str, Any]]) -> bool:'''
NEW2 = '''    def _respect_user_pause_locked(self, state: _LeaseState) -> bool:
        """ADR-8: paused with no tool-held lease, no obligation and no owner record.

        The owner RECORD (not the marker file) is the authority (ADR-5 W1): if a record
        exists we treat the cycle as a crashed one of ours and recover it instead of
        silently adopting a human's pause.
        """
        return not state.entries and not state.owner

    def _owner_lease_live(self, state: _LeaseState, live: list[dict[str, Any]]) -> bool:'''
if OLD2 not in text:
    print("HELPER PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)
PATCHER.write_text(text, encoding="utf-8")
print("ADR-8 user-pause guard installed")
