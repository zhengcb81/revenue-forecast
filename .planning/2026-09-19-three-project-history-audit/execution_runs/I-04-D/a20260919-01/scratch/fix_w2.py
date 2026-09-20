"""W2 crash recovery: the owner record is gone because the owner was PRUNED.

When the crashed owner's lease has just been reclaimed, the record legitimately
disappears - that is our own lineage, not a foreign party.  The R4 gate must accept
"provably dead AND (same lineage OR the record was pruned in this pass)"; anything
else stays R5.
"""

from __future__ import annotations

import pathlib
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''        age = self._owner_age_seconds(state)
        claimable = self._owner_is_our_lineage(state)
        if not claimable:'''
NEW = '''        age = self._owner_age_seconds(state)
        claimable = (
            self._owner_is_our_lineage(state)
            or not state.owner
            or not state.owner.get("lease_id")
        )
        if not claimable:'''
text = PATCHER.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = '''        if not claimable:
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and the ownership record is not attributable to this "
                f"process lineage (owner boot_uuid={state.owner.get('boot_uuid')!r}, "
                f"pid={state.owner.get('pid')!r}); nothing was written and no worker command "
                "was issued. This is the fail-closed terminal state: resolve it with "
                "`worker-resume` by hand, or let the owning tool close its own cycle",
            )'''
NEW2 = '''        if not claimable:
            owner = state.owner or {}
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and the ownership record is not attributable to this "
                f"process lineage (owner boot_uuid={owner.get('boot_uuid')!r}, "
                f"pid={owner.get('pid')!r}); nothing was written and no worker command "
                "was issued. This is the fail-closed terminal state: resolve it with "
                "`worker-resume` by hand, or let the owning tool close its own cycle",
            )'''
if OLD2 not in text:
    print("MESSAGE PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)
PATCHER.write_text(text, encoding="utf-8")
print("W2 recovery rule installed")
