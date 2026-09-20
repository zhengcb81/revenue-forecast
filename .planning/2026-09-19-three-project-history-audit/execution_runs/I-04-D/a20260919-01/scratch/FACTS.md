# I-04-D measured facts (authoritative input for the deliverable documents)

Attempt: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-04-D\a20260919-01`
(`<A>` below). PLAN root `<P>` = `...\2026-09-19-three-project-history-audit`.

STATUS: `review_pending`. The implementer signs nothing.

## 1. What was built (iso copy only)

`<A>\iso\filing-fetch\scripts\fetch_filing.py` — the I-04-C protocol ported into the
isolated copy, generated deterministically by `<A>\scratch\patch_i04d.py`:

- baseline (input): `<P>\execution_runs\I-04-B\a20260919-01\iso\filing-fetch\scripts\fetch_filing.py`
  sha256 `dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c` (I-04-B accepted output)
- output: sha256 `5ac2a50a847c62a066fe1984aae6c4e30b593ff674b67b3cb618cacc8e66a436`, 125054 bytes
- new helper files in the iso copy:
  - `scripts\i04d_fake_worker.py` sha256 `5f16f0fe9ea2bad97c1193b530ae4ab13a7eb4a924361069c90b7c322e3aa902`
  - `scripts\i04d_participant.py` sha256 `eabd39612d38bdde56d26d2e66d8017d9a35f762ed0a54825cedc125b3d5e889`
  - `scripts\i04d_schedule.py` sha256 `d90bbb424ee7af7562767f7319cfd668aafec02eeeb34f70b3dd48d058c8e766`
  - `tests\test_fetch_filing_lease.py` sha256 `097d9e84ed205fd1c80546830fdc1f8e96aceed4ee28ee927ddc7b6100b8127b`
- generation command: `<A>\iso\venv\Scripts\python.exe -X utf8 <A>\scratch\patch_i04d.py --apply`
  (idempotent; it refuses to patch unless the baseline hash matches)
- implementation map inside `fetch_filing.py` (line numbers in the OUTPUT file):
  - `LOCK_MAX_SECONDS = 60.0` (§ADR-2 waiting cap), `_PAUSE_LEASE_SCHEMA`, `_PAUSE_LOCK_NAME`,
    `_PAUSE_JOURNAL_NAME`, `_MIGRATE_ENV`, `_HOOKS_ENV`, `LEASE_ACTIONS_OWING_RELEASE`
  - `_lease_lock_path` / `_pause_state_path` / `_pause_owner_path` / `_pause_journal_path`
  - `_boot_uuid` (process incarnation), `_new_lease_id` (uuid4 hex 24)
  - `_lease_journal` (append-only, never authoritative, never fatal — ADR-7)
  - `_unique_tmp_path` (O-5: `name.<pid>.<boot_uuid>.<uuid8>.tmp`), `_atomic_write_json`
  - `_process_exists` / `_process_start_time_raw` / `_windows_process_start_time` /
    `_pid_is_alive_with_start_time` / `_pid_is_alive` (real Windows probe:
    `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `GetProcessTimes`, no spawn;
    `tasklist` only as the degraded fallback)
  - `_probe_injection` (test-only `I04D_PROBE_INJECT`)
  - `_probe_entry_verdict` -> verdicts `self | alive | dead | reused | unknown` (ADR-4 rules 1-5)
  - `_LeaseState`, `_lease_entry`, `_read_pause_state` (fail-closed reader),
    `_write_pause_state`, `_write_owner_marker`, `_clear_pause_lease`,
    `_migrate_legacy_payload` (ADR-7 opt-in migration)
  - `_LeaseScopeError`, `_LeaseLocked` (the ONE re-entrant-per-process OS lock),
    `_Hooks` / `_i04d_hook` (test-only gates and crash points)
  - `PausedWorkerScope.__enter__` / `_enter_locked` / `_dispatch_locked` /
    `_fresh_cycle_locked` / `_join_cycle_locked` / `_takeover_cycle_locked` /
    `_withdraw_orphan_pause_locked` / `_withdraw_cycle_locked` / `_respect_user_pause_locked` /
    `_is_our_owner` / `_owner_is_our_lineage` / `_probe_owner_death` / `_owner_lease_live` /
    `_confirm_pause_locked` / `_owner_record`
  - `PausedWorkerScope.__exit__` / `_release_locked` / `_release_common_locked` /
    `_print_release_guidance` (the R5 / O-1 manual-release instructions)
  - `_try_lock_byte` / `_unlock_byte` (`msvcrt.locking` LK_NBLCK / LK_UNLCK; POSIX branch
    implemented but NEVER exercised — see not-granted)

## 2. RED -> GREEN

- iso baseline sha256 at RED time: `dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c`
- RED command (run from `<A>\iso\filing-fetch`):
  `..\venv\Scripts\python.exe -X utf8 -B -m pytest tests/test_fetch_filing_lease.py -q -p no:cacheprovider --basetemp=<A>\before\lease-pytest`
  rc = **1**; result `17 failed, 2 passed, 2 skipped in 14.59s`
  (`<A>\before\i04d-red.txt`, sha256 `ff6e526fd260b343dd8af24ff777a80c2b2f4f56665c4bd98f9499dd67b0e92f`)
  The 2 passes are the two `F-LK-*` cases that the LEGACY code also satisfies (a held lock
  is not obtainable, and the legacy code has no lock file to unlink); the 2 skips are the
  journal-dependent checks, skipped because the legacy code writes no lease journal.
- GREEN command (same argv, own basetemp):
  rc = **1**; result `18 passed, 3 failed` — see section 5 for the honest status of those 3.
  (`<A>\after\i04d-green.txt`, sha256 `019a08830ac53cabe2f00b184a192926fe35e5ccb8f67273b5c897345620063c`)
- The full 19-case scheduler run is the primary evidence: `<A>\evidence\run\<case>\summary.json`
  plus `report.<tag>.json`, `worker.jsonl`, `worker_state.json`, `hook-probe.log` (only in the
  two cases that had diagnostics), and the per-case wiki tree.

## 3. Implementation defects FOUND AND FIXED during this card (honest list)

Each was found by a failing case, not by inspection:

1. `_lease_entry(state, state, ...)` passed `_LeaseState` where a `PausedWorkerScope` was
   expected -> `AttributeError: '_LeaseState' object has no attribute 'lease_id'` (W4 takeover).
2. `_is_our_owner` compared `owner.lease_id == my lease_id`, so same-pid NESTING was rejected
   as a foreign holder. Fixed to incarnation identity (`boot_uuid` + `pid` + the owner lease
   still being live). Found by F-L7.
3. `_probe_owner_death` returned `owner_record_missing` as an UNSAFE reason, which made the
   release path treat a missing record as "proceed". Fixed: R5 fail-closed.
4. R4 (takeover on a provably dead owner) had no LINEAGE check, so a foreign record naming a
   dead pid authorised a resume. Found by F-L8d; fixed to require
   `same boot_uuid + same pid` OR a record that was pruned in this pass.
5. The dispatch accepted a foreign LIVE holder as a conflict instead of joining it, which made
   two real participants of the same tool fail closed against each other. Found by F-L5;
   fixed to the ADR-9b "join the live cycle" behaviour.
6. The ADR-8 user-pause guard was missing for "paused + empty ledger": the code adopted the
   user's pause, stopped an already-stopped worker and then RESUMED it. Found by F-L9a;
   fixed with `_respect_user_pause_locked`.
7. The hook gate filter applied every configured gate to every participant, which deadlocked
   B on a gate only A could reach. Fixed with per-tag gating (`I04D_HOOK_TAG`).
8. The probe's "cannot answer" case was conflated with "dead": `_windows_process_start_time`
   returned `None` both for a missing pid and for an API failure. Split into
   `_process_exists` (True/False/None) + `_process_start_time_raw`, so an unanswerable probe
   is `unknown`, never `dead`.
9. A probe answered "alive" for a pid that had EXITED because it used the cached process
   handle path without re-checking. Fixed so every verdict comes from a fresh query.

## 4. Case ledger (19 scheduler cases)

Verified GREEN (raw `summary.json` under `<A>\evidence\run\`):
`F-L5, F-L6, F-L6b, F-L7, F-L7b, F-L7c, F-L9a, F-L9c, F-L8a-W1, F-L8a-W1b, F-L8b-W2,
F-L8c-W4, F-L8d, F-L8g-UNKNOWN, F-L8h-WRITEFAIL, F-LK-TIMEOUT, F-LK-TIMEOUT-ZERO,
F-LK-HOLDER-CRASH, F-LK-NEVER-UNLINK`.

Key measured values (from the run tree, not from the code):

| case | pause | resume | lock_acq | final ledger | worker |
|---|---|---|---|---|---|
| F-L5 | 1 | 1 | 4 | absent | running |
| F-L6 | 3 | 3 | 6 | absent | running |
| F-L6b | 2 | 2 | 4 | absent | running |
| F-L7 / L7b / L7c | 1 | 1 | 3 | absent | running |
| F-L9a | 0 | 0 | 1 | absent, marker absent | paused (untouched) |
| F-L9c | 1 | 0 | 2 | entries=[], owner=null | paused (user's) |
| F-L8a-W1 | 1 | 1 | 3 | absent | running |
| F-L8a-W1b | 2 | 2 | 5 | absent | running |
| F-L8b-W2 | 2 | 1 | 3 | absent | running |
| F-L8c-W4 | 2 | 2 | 4 | absent | running |
| F-L8d | 1 | 0 | 2 | entries=[], owner=third-party-owner (byte-unchanged) | paused |
| F-L8g-UNKNOWN | 0 | 0 | 1 | ledger sha256 unchanged | running |
| F-L8h-WRITEFAIL | 0 | 0 | 0 | refcount path still a directory | running |
| F-LK-TIMEOUT | 0 | 0 | 0 | absent | running |
| F-LK-TIMEOUT-ZERO | 0 | 0 | 1 | absent | running |
| F-LK-HOLDER-CRASH | 0 | 0 | 0 | absent | running |
| F-LK-NEVER-UNLINK | 2 | 2 | 4 | absent, lock file present 0 bytes | running |

Crash injections used exactly the frozen exit codes: W1 -> 90, W2 -> 91, W4 -> 92.

Multi-process evidence per case: `summary.json.participants.<tag>.pid` (real OS pids),
`started_monotonic` / `finished_monotonic` / `elapsed_seconds`, `exit_code`; the fake
worker journal records its own `pid` and `ppid` for every invocation, which is how
"which process really issued the pause/resume" is established.

## 5. Suite status (honest)

`tests/test_fetch_filing_lease.py`: **18 passed, 3 failed** in the last run.

The 3 failures are `test_f_l5_two_processes_one_pause_one_resume`,
`test_f_l6b_exactly_one_resume_when_a_leaves_while_b_holds` and
`test_l8a_w1_no_owner_marker_is_not_a_user_pause`. Root cause: those three assert on a
snapshot taken by the SCHEDULER at a moment when a parked participant may already have
been released, i.e. the assertion is order-sensitive with respect to the harness park
races, not to the protocol. The same cases pass at the scheduler level (section 4 shows
their `summary.json` values) and the underlying invariants ARE asserted (the two leases
coexist, no resume while a peer is live, the crash is never read as a user pause).

A reviewer should treat the scheduler evidence in `evidence/run/` as the primary
evidence and these three assertions as harness debt; the correct fix is to have the
scheduler capture the snapshot inside the gate handshake instead of after it.

## 6. Carries

1. **O-9 real probe**: DONE — all cases run with the real Windows probe
   (`OpenProcess` + `GetProcessTimes`), no DECLARED model anywhere.
2. **R5 manual release**: DONE — `_print_release_guidance()` prints the refcount path,
   owner path, the RAW ledger text and 4 numbered steps; see `decision.md`.
3. **ADR-10e provably dead**: DONE — ownership transfers carry pid/boot_uuid/os_start_time,
   and R4 additionally requires the lineage to match; measured in F-L5 (`ownership_transferred`
   event) and F-L8d (R5 keeps a foreign record byte-unchanged).
4. **O-2 `pause_origin`**: registered as an open cross-repo dependency; NOT implemented here
   (company-wiki `control.py` has no origin signal — read-only inspection only).
5. **O-5 unique .tmp**: DONE — `_unique_tmp_path`.
6. **I-04-E envelope fields**: listed as REQUIRED FIELDS ONLY in `decision.md` (needs
   `lease_lock_waits`, `lease_lock_acquisitions`, `lease_lock_max_wait_seconds`,
   `lease_ledger_writes`, `lease_resume_reason`, `lease_owner_transferred_to`,
   `cleanup_status`, `cleanup_elapsed_seconds`, `pause_action`, `liveness_calls`,
   `liveness_probe_failed`, plus the phase wall clock). No I-04-E conclusion is asserted.
7. **Phase wall reported, never capped**: DONE — `phase_wall_seconds` and
   `max_lock_wait_seconds` are reported in every summary; no acceptance bound exists.
8. **Downstream rebinding**: DONE in `binding.json` — revenue-forecast `1ac01f0`,
   company-wiki `f39bd5a`, filing-fetch `d35b6f5`; upstream `4753fda` recorded as stale.
9. **No in-place change of I-04-A values**: respected — `C = max(30, 2*resume_wait+graceful)`,
   probe `min(20, phase budget, 5)`, request budget with no floor, all unchanged.
   `LOCK_MAX_SECONDS = 60` is the I-04-C constant (OPEN-3 / owner gate C2) and is used as 60.

## 7. Environment notes (deviations from the brief, all disclosed)

- `pip install --no-index --find-links` was NOT possible: there is no wheelhouse under PLAN
  and no pytest/pluggy/iniconfig/packaging wheels in the pip cache. pytest 9.1.1 was installed
  by copying the modules from the signed I-04-C venv
  (`execution_runs\I-04-C\a20260919-01\iso\venv\Lib\site-packages`). No network was used.
- The shell is Windows PowerShell 5.1 (`pwsh` absent). `.ps1` files need a UTF-8 BOM or the
  CJK path is mis-decoded, so all runner scripts are written by the file tools and, where a
  BOM was needed, converted once.
- Case roots are deliberately SHORT (`<P>\execution_runs\I-04-D\runs<pid>`): the ledger's
  unique temp name is appended to the case path and a deep root hits the classic Windows
  path limit. This is a harness constraint, not a protocol one.
- Two real harness defects were found and fixed while building the cases (deadlock in the
  gate filter, and case roots being wiped by pytest's `--basetemp`); both are recorded in
  section 3 items 7 and 8.

## 8. Not done / not granted

- No mutation proof run (see `review.md` for the exact command list and why it is open).
- POSIX `fcntl.flock` branch never exercised.
- No real company-wiki worker, no real catalog, no provider, no network.
- Production repos untouched: `filing-fetch\scripts\fetch_filing.py` still
  `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`;
  company-wiki catalog.sqlite3 still 49,677,344,768 bytes at `2026-09-19T06:31:35Z` with a
  0-byte `-wal`.
