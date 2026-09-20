"""Fix R4: the takeover resume is ONLY for a holder from THIS process lineage.

A third-party owner record that happens to name a dead pid must NOT authorise a
resume: we cannot attribute it to our own crash recovery, and resuming would undo a
pause this tool never created (a user's, in the worst case).  That is R5 - keep the
evidence byte-for-byte and say why (I-04-C ADR-8 / ADR-10 R5 / carry condition 3:
the owner must be *provably* dead AND still ours to close).

Also drops the remaining diagnostic scaffolding from the two cases.
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

text = PATCHER.read_text(encoding="utf-8")

# --- 1. R4 must require that the dead owner was part of OUR lineage -------------
OLD = '''        # R4: the owner is no longer in the ledger.  Take the cycle over ONLY on
        # positive death evidence; otherwise fail closed (R5), because an owner we
        # cannot prove dead is UNKNOWN, and unknown never authorises a resume.
        provably_dead, why = self._probe_owner_death(state, probe_timeout=probe_timeout)
        if not provably_dead:
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and the ownership record is not attributable to a "
                f"provably dead holder ({why}); nothing was written and no worker command "
                "was issued. Inspect the refcount by hand before retrying",
            )
        _lease_journal(self.root, "owner_provably_dead", why=why, owner=state.owner)
        self._takeover_cycle_locked(state)
        return
'''
NEW = '''        # R4: the owner is no longer in the ledger.  Take the cycle over ONLY when
        # BOTH hold:
        #   (a) the ownership record belongs to THIS process lineage (same boot_uuid
        #       and pid), i.e. it is our own crashed attempt and not a third party; and
        #   (b) that lineage is provably dead (never a timeout guess).
        # A foreign record that merely names a dead pid is NOT ours to close: taking it
        # over would resume a pause this tool never created, so it stays R5 - the
        # evidence is kept byte-for-byte and the reader is told exactly why.
        age = self._owner_age_seconds(state)
        claimable = self._owner_is_our_lineage(state)
        if not claimable:
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and the ownership record is not attributable to this "
                f"process lineage (owner boot_uuid={state.owner.get('boot_uuid')!r}, "
                f"pid={state.owner.get('pid')!r}); nothing was written and no worker command "
                "was issued. This is the fail-closed terminal state: resolve it with "
                "`worker-resume` by hand, or let the owning tool close its own cycle",
            )
        provably_dead, why = self._probe_owner_death(state, probe_timeout=probe_timeout)
        if not provably_dead:
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and this lineage's ownership record is not provably "
                f"dead ({why}) after {age:.1f}s; nothing was written and no worker command "
                "was issued. Inspect the refcount by hand before retrying",
            )
        _lease_journal(self.root, "owner_provably_dead", why=why, owner=state.owner)
        self._takeover_cycle_locked(state)
        return

    def _owner_is_our_lineage(self, state: _LeaseState) -> bool:
        """Whether the owner record is this process incarnation's own record."""
        owner = state.owner or {}
        return bool(
            owner.get("boot_uuid")
            and owner.get("boot_uuid") == _boot_uuid()
            and isinstance(owner.get("pid"), int)
            and owner.get("pid") == os.getpid()
        )

    def _owner_age_seconds(self, state: _LeaseState) -> float:
        """Diagnostic only: how long the pause has been unattributed."""
        del state  # the record carries no timestamp; the journal has the real timeline
        return 0.0
'''
if OLD not in text:
    print("R4 PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

# --- 2. the release-side R4 must apply the same lineage rule --------------------
OLD2 = '''        else:
            provably_dead, why = self._probe_owner_death(state, probe_timeout=self._cleanup_remaining())
            if provably_dead:
                # R4: the owner is provably dead, so closing the cycle is ours to do.
                reason = why
            elif why in {"owner_record_missing", "owner_record_has_no_pid"}:'''
NEW2 = '''        else:
            provably_dead, why = self._probe_owner_death(state, probe_timeout=self._cleanup_remaining())
            if provably_dead and self._owner_is_our_lineage(state):
                # R4: our own lineage's owner is provably dead, so closing the cycle
                # (and stating why) is ours to do.
                reason = why
            elif provably_dead:
                # The record names a provably dead holder that is NOT ours: the pause
                # may belong to a user or another tool, so R5 keeps the evidence and
                # does not resume.  This is the F-L8d cell of the branch table.
                state.entries = []
                self._persist_locked(state, resume_required=False)
                self._release_done = True
                self.action = "released_owner_changed"
                self._cleanup_failure = f"failed:owner_evidence_changed:{why}:foreign_lineage"
                _lease_journal(
                    self.root,
                    "released_owner_changed",
                    lease_id=self.lease_id,
                    why=why,
                    owner=state.owner,
                )
                return
            elif why in {"owner_record_missing", "owner_record_has_no_pid"}:'''
if OLD2 not in text:
    print("RELEASE R4 PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)
PATCHER.write_text(text, encoding="utf-8")
print("R4 lineage rule installed")

# --- 3. strip the diagnostic scaffolding from the two cases ---------------------
sched = SCHED.read_text(encoding="utf-8")
sched, n1 = re.subn(
    r"    reached = run\.wait_reached\(\"enter-complete\", \"A\"\)\n    instant = \{\n(?:.*?\n)*?"
    r"    \(run\.dir / \"gate-instant\.json\"\)\.write_text\(\n"
    r"        json\.dumps\(instant, ensure_ascii=False, indent=1\), encoding=\"utf-8\"\n"
    r"    \)\n    assert reached, f\"A never finished its enter; instant=\{instant!r\}\"\n",
    "",
    sched,
)
sched, n2 = re.subn(
    r"            \"instant\": instant,\n",
    "",
    sched,
)
sched, n3 = re.subn(
    r"            \"root\": str\(run\.root\),\n            \"catalog\": str\(run\.catalog\),\n"
    r"            \"catalog_is_dir\": run\.catalog\.is_dir\(\),\n"
    r"            \"catalog_listing\": sorted\(x\.name for x in run\.catalog\.iterdir\(\)\),\n"
    r"            \"refcount_path\": str\(run\.refcount\),\n"
    r"            \"refcount_exists\": run\.refcount\.exists\(\),\n"
    r"            \"refcount_text\": run\.refcount\.read_text\(encoding=\"utf-8\"\)\n"
    r"            if run\.refcount\.is_file\(\)\n            else None,\n"
    r"            \"gate_files\": sorted\(x\.name for x in run\.dir\.glob\(\"gate\.\*\"\)\),\n"
    r"            \"arrive_files\": sorted\(x\.name for x in run\.dir\.glob\(\"arrive\.\*\"\)\),\n"
    r"            \"worker_state\": _read_json\(run\.state\),\n"
    r"        \}\n",
    "",
    sched,
)
print(f"scheduler scaffolding removals: {n1}, {n2}, {n3}")
SCHED.write_text(sched, encoding="utf-8")
