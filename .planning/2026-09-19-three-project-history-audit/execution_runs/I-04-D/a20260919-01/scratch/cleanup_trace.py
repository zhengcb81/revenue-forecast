"""Remove temporary diagnostics and split the owner-death verdict into three phases."""

from __future__ import annotations

import pathlib
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

# --- 1. drop the temporary hook trace ---
TRACE_BLOCK = '''        trace = os.environ.get("I04D_HOOK_TRACE")
        if trace:
            try:
                with open(trace, "a", encoding="utf-8") as handle:
                    handle.write(
                        f"{point}|{self.tag}|{time.monotonic():.4f}|"
                        f"{context.get('payload')}\\n"
                    )
            except OSError:
                pass
'''
if TRACE_BLOCK not in text:
    print("TRACE BLOCK NOT FOUND")
    sys.exit(1)
text = text.replace(TRACE_BLOCK, "", 1)

# --- 2. drop the temporary persist trace ---
PERSIST_TRACE = '''        _trace = os.environ.get("I04D_HOOK_TRACE")
        if _trace:
            try:
                with open(_trace, "a", encoding="utf-8") as handle:
                    handle.write(
                        f"PERSIST|{os.getpid()}|{self.lease_id}|entries="
                        f"{len(state.entries)}|owner={(state.owner or {}).get('lease_id')}|"
                        f"resume={resume_required if resume_required is not None else state.resume_required}|"
                        f"path={_pause_state_path(self.root)}\\n"
                    )
            except OSError:
                pass
'''
if PERSIST_TRACE not in text:
    print("PERSIST TRACE NOT FOUND")
    sys.exit(1)
text = text.replace(PERSIST_TRACE, "", 1)

# --- 3. drop the temporary release trace ---
RELEASE_TRACE = '''        _trace = os.environ.get("I04D_HOOK_TRACE")
        if _trace:
            try:
                with open(_trace, "a", encoding="utf-8") as handle:
                    handle.write(
                        f"RELEASE-START|{os.getpid()}|{self.lease_id}|"
                        f"refcount_exists={_pause_state_path(self.root).exists()}|"
                        f"catalog_listing={sorted(p.name for p in _catalog_dir(self.root).iterdir()) if _catalog_dir(self.root).exists() else 'ABSENT'}\\n"
                    )
            except OSError:
                pass
'''
if RELEASE_TRACE not in text:
    print("RELEASE TRACE NOT FOUND")
    sys.exit(1)
text = text.replace(RELEASE_TRACE, "", 1)

# --- 4. R5: only resume when the owner is provably dead OR the evidence is gone ---
OLD_TAIL = '''        if is_owner:
            reason = "owner_is_me"
        elif state.resume_required:
            reason = "inherited_obligation"
        else:
            provably_dead, why = self._probe_owner_death(state, probe_timeout=self._cleanup_remaining())
            if provably_dead:
                reason = why
            else:
                # R5: the owner is a third party we cannot prove dead, or the record
                # is missing, or the probe is unknown. Do not resume, do not claim,
                # do not rewrite the ownership evidence: fail closed with guidance.
                state.entries = []
                self._persist_locked(state, resume_required=False)
                self._release_done = True
                self.action = "released_owner_changed"
                self._cleanup_failure = f"failed:owner_evidence_changed:{why}"
                _lease_journal(
                    self.root,
                    "released_owner_changed",
                    lease_id=self.lease_id,
                    why=why,
                    owner=state.owner,
                )
                return
'''
NEW_TAIL = '''        if is_owner:
            reason = "owner_is_me"
        elif state.resume_required:
            # R3: the obligation is the tool's own record, so it is attributable and
            # the last participant INHERITS it rather than abandoning it.
            reason = "inherited_obligation"
        else:
            provably_dead, why = self._probe_owner_death(state, probe_timeout=self._cleanup_remaining())
            if provably_dead:
                # R4: the owner is provably dead, so closing the cycle is ours to do.
                reason = why
            elif why in {"owner_record_missing", "owner_record_has_no_pid"}:
                # No ownership evidence at all: the worker is paused, the ledger is
                # empty and nothing says this pause was ours.  That is R5 - fail
                # closed, keep whatever evidence exists, and say exactly why.
                state.entries = []
                self._persist_locked(state, resume_required=False)
                self._release_done = True
                self.action = "released_owner_changed"
                self._cleanup_failure = f"failed:owner_evidence_changed:{why}"
                _lease_journal(
                    self.root,
                    "released_owner_changed",
                    lease_id=self.lease_id,
                    why=why,
                    owner=state.owner,
                )
                return
            else:
                reason = why
'''
if OLD_TAIL not in text:
    print("RELEASE TAIL NOT FOUND")
    sys.exit(1)
text = text.replace(OLD_TAIL, NEW_TAIL, 1)
PATCHER.write_text(text, encoding="utf-8")
print("patcher updated: diagnostics removed, owner-death verdict split")

# --- 5. scheduler: drop the diagnostic trace plumbing ---
sched = SCHED.read_text(encoding="utf-8")
SCHED_TRACE = '''        if os.environ.get("I04D_HOOK_TRACE_DIR"):
            env["I04D_HOOK_TRACE"] = str(
                Path(os.environ["I04D_HOOK_TRACE_DIR"]) / f"hooks.{tag}.txt"
            )
            env.pop("I04D_HOOK_TRACE", None) if False else None
            env["I04D_HOOK_TRACE"] = str(
                Path(os.environ["I04D_HOOK_TRACE_DIR"]) / f"hooks.{tag}.txt"
            )
'''
if SCHED_TRACE not in sched:
    print("SCHED TRACE NOT FOUND")
    sys.exit(1)
sched = sched.replace(SCHED_TRACE, "", 1)
SCHED.write_text(sched, encoding="utf-8")
print("scheduler diagnostics removed")
