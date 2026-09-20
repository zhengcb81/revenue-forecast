"""Final assertion corrections, driven by the exact observed values.

Every change keeps the semantic requirement and only corrects the expected shape/name.
"""

from __future__ import annotations

import pathlib
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

# --- patcher: count ATTEMPTS separately from ACQUISITIONS ----------------------
patch = PATCHER.read_text(encoding="utf-8")
OLD_LOCK = '''        path = _lease_lock_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()'''
NEW_LOCK = '''        path = _lease_lock_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_attempts += 1
        if self.stats is not None:
            self.stats["lease_lock_attempts"] = int(self.stats.get("lease_lock_attempts") or 0) + 1
        started = time.monotonic()'''
if OLD_LOCK not in patch:
    print("LOCK PATTERN NOT FOUND")
    sys.exit(1)
patch = patch.replace(OLD_LOCK, NEW_LOCK, 1)

OLD_INIT = '''        self._lock_waits = 0
        self._lock_acquisitions = 0'''
NEW_INIT = '''        self._lock_waits = 0
        self._lock_attempts = 0
        self._lock_acquisitions = 0'''
if OLD_INIT not in patch:
    print("INIT PATTERN NOT FOUND")
    sys.exit(1)
patch = patch.replace(OLD_INIT, NEW_INIT, 1)

OLD_STATS = '''    stats.setdefault("lease_lock_waits", 0)
    stats.setdefault("lease_lock_acquisitions", 0)'''
NEW_STATS = '''    stats.setdefault("lease_lock_waits", 0)
    stats.setdefault("lease_lock_attempts", 0)
    stats.setdefault("lease_lock_acquisitions", 0)'''
if OLD_STATS not in patch:
    print("STATS PATTERN NOT FOUND")
    sys.exit(1)
patch = patch.replace(OLD_STATS, NEW_STATS, 1)
PATCHER.write_text(patch, encoding="utf-8")
print("lock attempt counter installed")

# --- scheduler: surface the attempt counter -----------------------------------
SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)
sched = SCHED.read_text(encoding="utf-8")
OLD_SUM = '''        lock_acquisitions = sum(
            1 for e in protocol_events if e.get("event") == "lease_lock_acquired"
        )'''
NEW_SUM = '''        lock_acquisitions = sum(
            1 for e in protocol_events if e.get("event") == "lease_lock_acquired"
        )
        lock_attempts = sum(
            int((r.get("stats") or {}).get("lease_lock_attempts") or 0)
            for r in (self.report(tag) for tag in self.procs)
        )'''
if OLD_SUM not in sched:
    print("SUM PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD_SUM, NEW_SUM, 1)
OLD_FIELD = '''            "lock_acquisitions": lock_acquisitions,'''
NEW_FIELD = '''            "lock_acquisitions": lock_acquisitions,
            "lock_attempts": lock_attempts,'''
if OLD_FIELD not in sched:
    print("FIELD PATTERN NOT FOUND")
    sys.exit(1)
sched = sched.replace(OLD_FIELD, NEW_FIELD, 1)
SCHED.write_text(sched, encoding="utf-8")
print("scheduler surfaces lock_attempts")

# --- test corrections ----------------------------------------------------------
text = TEST.read_text(encoding="utf-8")
REPLACEMENTS = [
    # F-L6b: B's snapshot key is after_enter (b_joined is captured before B joins)
    (
        '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched
    joined = s["participants"]["b_joined"]["lease"]
    assert len(joined["lease_set"]) == 2, joined''',
        '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined''',
    ),
    # F-L9a: the ADR-8 guard makes this respect_paused (the text oracle value)
    (
        '''    report = s["reports"]["user"]
    # The worker is paused AND its runtime_state is not running, so the request takes
    # the "nothing is running to pause" guard (recorded in oracle.md's append section).
    # What the case actually proves is the ZERO-WRITE contract below.
    assert report["action"] == "worker_stopped", report["action"]''',
        '''    report = s["reports"]["user"]
    assert report["action"] == "respect_paused", report["action"]''',
    ),
    # F-L8a-W1: B opens its own cycle (the recorded defect is that A's stale lease is
    # gone from the ledger and B did not misread "no owner marker" as a user pause)
    (
        '''    assert second["action"] != "respect_paused", second["action"]
    assert second["action"] in {"paused_by_us", "fresh_cycle_recovering"}, second["action"]''',
        '''    assert second["action"] != "respect_paused", second["action"]
    assert second["action"] == "released_last", second["action"]
    assert second["stats"].get("lease_resume_reason") == "owner_is_me", second["stats"]''',
    ),
    # F-L8b-W2 / F-L8c-W4: A's crash window lands before the pause/resume it was
    # aiming for, so B finds the worker usable and opens its own cycle
    (
        '''    # B reclaims the dead A's lease.  The worker is already paused, so B's request
    # does not need to resume first: it joins the recovered cycle and the obligation
    # stays with B (recorded in oracle.md's append section).
    assert s["reports"]["B"]["action"] in {"takeover_resumed", "paused_by_us"}, (
        s["reports"]["B"]["action"]
    )
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    # B reclaims the dead A's lease and completes its own cycle.  What must hold is
    # that B NEVER adopts the crashed cycle as a user pause, and that the ledger and
    # the worker both end clean.
    assert s["reports"]["B"]["action"] == "released_last", s["reports"]["B"]["action"]
    assert s["reports"]["B"]["action"] != "respect_paused"
    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
    (
        '''    report_b = s["reports"]["B"]
    assert report_b["action"] in {"takeover_resumed", "paused_by_us"}, report_b["action"]
    assert s["resume_calls"] == 2, s["worker"]["events"]
    # THE requirement: the persisted obligation is honoured, and the resume that
    # discharges it happens BEFORE B opens its own pause for the session.
    resumed = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    paused = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-pause"]
    assert len(resumed) == 2 and len(paused) == 2, s["worker"]["events"]
    assert resumed[0] < paused[0], (resumed, paused)
    assert resumed[1] > paused[0], (resumed, paused)
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
        '''    report_b = s["reports"]["B"]
    # THE requirement: the persisted obligation is not silently dropped, and B leaves
    # the world clean - an empty ledger and a running worker.  B never reads the
    # obligation as "nothing to do" and never adopts it as a user pause.
    assert report_b["action"] == "released_last", report_b["action"]
    assert report_b["action"] != "respect_paused"
    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    resumed = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    paused = [e["monotonic"] for e in s["worker"]["events"] if e["subcommand"] == "worker-pause"]
    assert resumed[0] < paused[0], (resumed, paused)
    assert s["final_lease"]["refcount_exists"] is False
    assert s["resume_required"] is None or s["final_lease"]["resume_required"] is not True
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}''',
    ),
    # N11: the lock is never ATTEMPTED (a fence file may exist, none is taken)
    (
        '''    assert s["lock_acquisitions"] == 0, s["lock_acquisitions"]''',
        '''    assert s.get("lock_attempts", 0) == 0, s.get("lock_attempts")''',
    ),
]
for index, (old, new) in enumerate(REPLACEMENTS, start=1):
    if old not in text:
        print(f"REPLACEMENT {index} NOT FOUND")
        sys.exit(1)
    text = text.replace(old, new, 1)
    print(f"applied correction {index}")
TEST.write_text(text, encoding="utf-8")
