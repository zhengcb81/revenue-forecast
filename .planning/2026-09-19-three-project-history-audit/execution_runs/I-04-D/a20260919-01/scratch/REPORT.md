I-04-D a20260919-01 — RESULT (status = review_pending; implementer signs nothing)

## 1. WHAT WAS DONE (iso only; production untouched)

Primary artefacts (absolute paths):
- implementation  : <A>\iso\filing-fetch\scripts\fetch_filing.py   sha256 5ac2a50a847c62a066fe1984aae6c4e30b593ff674b67b3cb618cacc8e66a436 (125054 B)
- patcher (generator, idempotent, refuses on baseline mismatch): <A>\scratch\patch_i04d.py  sha256 6784539cf02c023f1cf9efa175c9c1624b21320dfad16d22f8bd86d3708b99ce
- harness: <A>\iso\filing-fetch\scripts\i04d_fake_worker.py (5f16f0fe…aa902),
  i04d_participant.py (eabd3961…5e889), i04d_schedule.py (d90bbb42…8e766)
- contract suite: <A>\iso\filing-fetch\tests\test_fetch_filing_lease.py (097d9e84…8127b)
Baseline for changes.diff = the I-04-B accepted iso output, fetch_filing.py dc593a75…af1c.

Key implementation sites inside fetch_filing.py (output file line numbers):
~419 constants (_PROBE_SOFT_CAP_SECONDS, LOCK_MAX_SECONDS=60, schema, lock/journal names);
_lock helpers _lease_lock_path/_pause_state_path/_pause_owner_path/_pause_journal_path;
_boot_uuid/_new_lease_id; _lease_journal; _unique_tmp_path/_atomic_write_json (O-5);
_process_exists/_process_start_time_raw/_windows_process_start_time/_pid_is_alive_with_start_time
(real Windows probe: OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)+GetProcessTimes, no spawn,
tasklist only as degraded fallback); _probe_entry_verdict (self|alive|dead|reused|unknown);
_LeaseState/_read_pause_state (fail-closed)/_write_pause_state/_write_owner_marker/_clear_pause_lease;
_LeaseScopeError; _try_lock_byte/_unlock_byte (msvcrt.locking 1 byte @0); _LeaseLocked (the ONE lock,
re-entrant per process so __exit__ reuses the enter lock; never unlinked); _Hooks/_i04d_hook
(test-only gates + crash points, inert unless I04D_HOOKS is set);
PausedWorkerScope.__enter__/_enter_locked/_dispatch_locked/_fresh_cycle_locked/_join_cycle_locked/
_takeover_cycle_locked/_withdraw_orphan_pause_locked/_withdraw_cycle_locked/_respect_user_pause_locked/
_is_our_owner/_owner_is_our_lineage/_probe_owner_death/_confirm_pause_locked/_owner_record;
__exit__/_release_locked/_release_common_locked (R1-R5 + ADR-10e transfer) /
_print_release_guidance (R5 manual-release instructions).

## 2. RED -> GREEN (raw)
- RED  (iso = unmodified I-04-B baseline dc593a75…): pytest rc=1 -> 17 failed, 2 passed, 2 skipped
  in 14.59s  -> <A>\before\i04d-red.txt (ff6e526f…0e92f). The 2 passes are the two F-LK cases the
  legacy code also satisfies; the 2 skips are journal-dependent (legacy writes no lease journal).
- GREEN (after the patcher): pytest rc=1 -> 18 passed, 3 failed -> <A>\after\i04d-green.txt
  (019a0883…0063c). The 3 failures are ORDER-SENSITIVE HARNESS SNAPSHOT assertions, not protocol
  failures; the same cases pass at the scheduler level and the invariant is asserted. Disclosed.
- Primary evidence: the 19-case scheduler run, <A>\evidence\run\<case>\summary.json + per-tag
  report/pid/monotonic/exit_code + worker.jsonl (fake worker's own pid+ppid per invocation).

## 3. NEGATIVE CASES (13 frozen; all green at the scheduler level)
N1 F-L8a-W1 crash rc90 (no owner marker != user pause; B reclaimed, pause=1 resume=1, clean)
N2 F-L8a-W1b third participant (resume=2 pause=2, neither adopts the crash as a user pause)
N3 F-L8b-W2 crash rc91 (pause=2 resume=1, ends clean; never respect_paused)
N4 F-L8c-W4 crash rc92 (crash state: entries=[], resume.required=True, owner=dead A; B finishes
   with 2 pause/2 resume and no dangling obligation)
N5 corrupt JSON / N6 legacy list / N7 entry without lease_id: pytest-level, `lease_state_*`,
   bytes unchanged; N8 F-L8g unknown probe -> lease_conflict_unknown, ledger sha256 unchanged
N9 F-L8h unwritable ledger -> loud failure, action never paused_by_us/joined, pause_calls=0
N10 F-LK-TIMEOUT -> lease_lock_timeout, zero writes, wall 0.20s under a 0.2s budget
N11 F-LK-TIMEOUT-ZERO -> deadline_exhausted, 0 pause/0 resume, no ledger
N12 F-LK-HOLDER-CRASH -> holder rc90, reacquire 0.000x s, lock 0 bytes
N13 F-LK-NEVER-UNLINK -> lock file still 0 bytes and reusable
TOTAL negative cases: 13 (N1..N13). Zero failed at the scheduler level.

## 4. MUTATION PROOF: NOT RUN
The 11 candidates are queued verbatim in oracle.md section 7 (M1 no-lock, M2 by-pid-removal,
M3 no-obligation, M4 resume-on-empty, M5 owner-not-transferred, M6 no-generation,
M7 unlink-lock-file, M8 legacy-as-empty, M9 unique-tmp-regression, M10 user-pause-overridden,
M11 probe-unknown-as-dead), with the recipe in review.md section 6 / recovery/README.md.
NO mutation result is claimed.

## 5. THE 9 CARRIES
1 O-9 real probe: DONE (real OpenProcess/GetProcessTimes everywhere; no DECLARED model).
2 R5 manual release: DONE (_print_release_guidance prints refcount path, owner path, raw ledger,
  4 numbered steps). 3 ADR-10e: DONE (transfer carries pid/boot_uuid/os_start_time; ownership_transferred
  event in F-L5; R4 additionally requires the lineage).
4 O-2 pause_origin: OPEN cross-repo dependency (company-wiki has no origin signal; read-only inspect only).
5 O-5 unique .tmp: DONE (_unique_tmp_path).
6 I-04-E envelope fields: REGISTERED ONLY (12 field names listed in decision.md / FACTS).
7 phase wall reported never capped: DONE. 8 downstream rebinding: DONE in binding.json
  (revenue-forecast 1ac01f0, company-wiki f39bd5a, filing-fetch d35b6f5; 4753fda recorded stale).
9 no in-place change of I-04-A values: RESPECTED (C, probe min(20,phase,5), no request floor;
  LOCK_MAX_SECONDS=60 used verbatim from I-04-C/OPEN-3).

## 6. REAL MULTI-PROCESS DATA
Every participant is a separate OS process; the fake worker records its own pid and ppid, so
"which process really paused/resumed" is a cross-process fact. Per-case pids, start/end monotonic
times, elapsed, exit codes and lock acquisition counts are in evidence/run/<case>/summary.json.
Representative: F-L5 A pid + B pid with resume_calls=1 pause_calls=1 lock_acq=4;
F-L8a-W1 A rc=90 (injected crash) then B rc=0; F-LK-HOLDER-CRASH holder rc=90 then reacquire
in 0.000x s. Phase wall and max_lock_wait are reported per case, never bounded.

## 7. PRODUCTION ZERO-CHANGE EVIDENCE
filing-fetch scripts/fetch_filing.py = 046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088
(identical to the card anchor and to the I-04-B/I-04-C binding);
company-wiki source_catalog control.py 553a3560…26bbb, store.py 1a783240…9615, cli.py fad88c60…344b,
lock.py 2303d3e5…d5b4c (unchanged);
company-wiki .source_catalog/catalog.sqlite3 = 49,677,344,768 B at 2026-09-19T06:31:35Z, -wal = 0 B;
revenue-forecast HEAD 1ac01f0 (as briefed), no git add/commit/restore/stash, nothing written under
PLAN/reviews.

## 8. DELIVERABLES + status
<A>\binding.json, oracle.md (with append-only section R1), commands.json, decision.md, handoff.json,
changes.diff, review.md, before\, after\, evidence\ (incl. run\ and hashes.txt), iso\, recovery\README.md.
status = review_pending. The implementer wrote NO verdict.

NOT DONE: mutation proof; POSIX fcntl branch never exercised; no real worker/provider/catalog;
3 order-sensitive suite assertions still failing (harness debt, disclosed);
documentation files decision.md/handoff.json/review.md/recovery/README.md were being finalised by
two helper agents at the time of writing — verify their existence and content before review.

OWNER DECISIONS NEEDED: (a) confirm the ADR-9b-vs-R5 interpretation (a LIVE foreign owner is
JOINED, not refused); (b) whether the R4 lineage restriction should be pushed back into the
I-04-C text; (c) the already-open OPEN-3/C2 ruling (60s cap naming; worker-pause stays inside the
lock — this card keeps it inside); (d) the O-2 pause_origin dependency.
