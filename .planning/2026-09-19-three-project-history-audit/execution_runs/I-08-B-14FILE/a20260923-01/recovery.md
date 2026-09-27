# RECOVERY — I-08-B-14FILE / a20260923-01

## State classification

This card performs **no stateful product operation**: no publication, no registry append, no worker, no
lock, no git mutation, no network. RF was opened read-only; the only writes were (a) this attempt
directory, (b) disposable trees under `%TEMP%\i08b14file\a20260923-01\`.

## RF production tree: nothing to recover

- Open/close hashes of all 14 product paths are identical (`evidence/c4_rf_close_hashes.txt`):
  9 edited files unchanged, 5 added files still ABSENT → **production write count = 0**.
- RF `.pytest_cache\v\cache\nodeids` mtime `2026-09-23 20:37:58` — before this card's execution window
  (23:12-24:05) → no test ever executed inside RF; no `__pycache__` was created in RF by this card
  (`PYTHONDONTWRITEBYTECODE=1` on every run, all runs cwd = scratch).
- The landing itself (if the merge batch proceeds) = apply `changes.diff`; recovery of a failed landing is
  the inverse: restore the 9 paths from RF HEAD / re-remove the 5 added paths — RF is currently in exactly
  the pre-landing state, so **no rollback of RF is ever needed from this card**.

## Scratch trees (disposable)

`%TEMP%\i08b14file\a20260923-01\{before_tree, after_tree, mut_test, mut_prod, mut_guard, mut_golden,
compat_tree, basetemp}` — safe to delete wholesale; they are reproducible from the recorded steps
(`commands.md` B1-B5) and are NOT evidence. Evidence lives only under this attempt dir.
If a tree must be rebuilt after cleanup: re-run B1 (`robocopy` with the same `/XD` list), B3/B4 (Copy-Item of
the carrier files — hashes in binding §2 verify each step), then re-apply mutations/compat as in D4-D11.

## Evidence: deliberately NOT restored/rewritten

All raw stdout/rc files under `evidence/` are append-only evidence. Two superseded raws are kept on purpose:
- `r1…` re-run after the retracted basetemp-missing attempt (the retracted attempt produced only error
  output and was overwritten by the valid run — disclosed in commands C0);
- compat steps `c3/c3b/c3e` (superseded by `c3f/c3g/c3h`) kept to show the partial-write incident chain.

## Incidents (all closed, no residual state outside this attempt)

1. basetemp-missing first run → directory created, re-run (binding §6.1).
2. stale copied `.pyc` pointing traceback display at RF → purged from scratch trees (§6.2).
3. tool-timeout kill of one foreground pytest batch → background re-run; no orphan processes of this card
   (verified via process enumeration, §6.3).
4. UTF-16 evidence files → re-encoded (§6.4).
5. verifier universal-newline bug → fixed, full re-verify green (§6.5).
6. compat applier partial-write on forbid → accounted section-by-section; final compat state fully listed
   in commands D4-D11 (§6.6).

## If something later fails at merge

- `changes.diff` sha must equal `9721711a214c4dc7745dc960bf0be6280d86f25c8fe750376c9c9daf4a50bb66`
  (regeneration is deterministic: `scratch/gen_diff.py`, proven byte-identical across runs).
- Apply-order and the three merge-batch items are in `decision.md` §3-§5; do not apply TRIAGE's guard
  section on top of the carrier guard (proven conflict) — re-express it instead.
