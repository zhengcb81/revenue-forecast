# FC-1005 critical-mutation evidence

Live-verified mutations per class (the rest of the classes draw evidence from
implementer receipts scanned by the gate).  Each record: mutation -> test
that dies -> reverted.

## root_special_case
FC-301 M: drop-external-writable-check -> config load rejects external writable root test dies; reverted (receipt FC-301).

## epoch_condition
FC-202 M: drop-epoch-condition / drop-cohort-condition from resolver SQL -> CTRL-01/02 tests die; reverted (receipt FC-202).

## hash_check
FC-101/102/902/903 receipts: hash/version tamper oracles all kill; FC-1001 M-hash (corrupt tamper removed -> artifact still REUSABLE -> test dies).

## download_authorization
FC-802 M: bare allow_download without authorization -> authorized test dies; reverted (receipt FC-802).

## latest_reresolve
FC-1005 M-latest: close_gap._finalize re-resolve removed (resolution=None) -> test_close_gap_fc801 cg05 (idempotent rerun) + cg07 (downloaded_new envelope) DIE; reverted -> 7 passed. Verified live 2026-08-12.

## artifact_invalidation
FC-904 M1: DAG ancestor gate disabled -> test_ar03 dies (DAG-invalidated roles read); FC-901 M1/M2 (bucket mapping removed -> classification test dies).

## zero_call_event
FC-905-a M1/M2: review-receipt read removed / journal count removed -> pi01/pi05 die; FC-704 M: pseudo download_calls inference -> dies.

## path_containment
FC-502 M: borrow-legacy-containers (adapter returns acquisition/dayu_meta) -> normalized-assertion test dies; FC-504 M1 path-safety dropped -> sample test dies.

## chaos_fault_injection (supplementary)
FC-405 (receipt): disaster drills — interrupted migration resume, disk-full,
stale schema, duplicate assertion, wrong epoch, rollback re-run, restore
points + catalog hashes verified. FC-804 (receipt): single-flight lock,
crash recovery, idempotent retry, staging orphan, provider timeout — all
outcomes rebuildable from the journal. FC-1005 M-latest verified live above.
