# recovery.md — RF-RATCHET-FIX-2 / a20260923-01

## State at this closing: COMPLETE (review_pending/unsigned). If this attempt dies again, resume here.

### What is done (all judged runs finished; evidence on disk)
1. oracle.md = predecessor frozen oracle §0 (verbatim) + dated APPEND A — frozen before judged runs.
2. binding.json + evidence/integrity/* (key shas, scripts manifest, iso-vs-live 0 mismatches,
   porcelain before/after, frozen_sha_proof.txt).
3. Judged RED reproduced exactly (2 rows) + full-row scan + inlined twin cross-check (agree).
4. File 1 confidence.py: CC 32→17 (FILE_MAX), per-row GREEN + MUT1 (24>23) flip + restore.
5. File 2 model_extensions.py: CC 27→8 (FILE_MAX), FULL GREEN of test_new_files_stay_simple +
   MUT2 (11>10) flip + restore; golden-lock verdict NO CONFLICT, runtime proof 7 passed before AND after.
6. Family 24 files before == after (2 pre-existing failures both sides, 283 passed, 149 subtests).
7. changes.diff (exactly 2 files) generated + `git apply --check`/apply roundtrip byte-exact.

### Remaining for a successor (nothing technical): owner review of changes.diff, sign handoff.json.

### How to re-verify from scratch (all read-only w.r.t. RF)
- Ratchet RED on live RF: `python -B -m pytest tools/tests/test_complexity_ratchet.py -q --basetemp %TEMP%\<fresh> -p no:cacheprovider`
- Vehicle: `git -c core.autocrlf=false apply --check <ATTEMPT>\changes.diff` in a scratch tree seeded
  with `iso/*.baseline` at `scripts/analysis/confidence.py` + `scripts/model_extensions.py`
  (RF `.gitattributes` pins `*.py eol=lf`; under autocrlf=true a scratch apply writes CRLF — content
  identical: confidence.py 334 lines compared equal modulo CR; model_extensions.py hash-equal after
  the LF apply).
- Runnable refactored tree: `%TEMP%\rf2-iso-work` (scripts/tests/tools copy; refactored files applied).
  Pristine twin: `%TEMP%\rf2-iso`. Basetemps: `%TEMP%\rf2-*-bt`. If TEMP was cleaned, rebuild: copy
  RF's agents/assurance/audit_review/compatibility/config/docs/e2e/examples/references/review_audit/
  scripts/tests/tools + root files (exclude __pycache__/caches), then apply `iso/*.refactored`.
- Mutants: `python -B evidence\mutation\make_mutants.py` (re-derives both mutants from the refactored
  files in `%TEMP%\rf2-iso-work`).

### Hard constraints for any successor (unchanged)
- RF sources READ-ONLY: only `changes.diff` delivers code. Never edit FROZEN_MAX / NEW_FILE_MAX /
  the ratchet test / any test. No skip/xfail/baseline. No git mutations. No network.
- Scope: ONLY scripts/analysis/confidence.py + scripts/model_extensions.py. F2–F7 rows belong to
  REST-A / REST-B. Do not chase overall green with a third file.
- Predecessor attempt `RF-RATCHET-FIX/a20260923-01` = READ-ONLY baseline: cite, never write.
