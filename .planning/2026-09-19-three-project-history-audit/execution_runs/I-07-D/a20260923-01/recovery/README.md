# I-07-D a20260923-01 — recovery / cleanup README

Card: 故障矩阵与断点恢复 (fault matrix & breakpoint recovery). This attempt only ever
touched **scratch state**: its own attempt directory plus `%TEMP%\i07d\cases\**`.
Production writes = 0 (proof: `evidence/snapshot_verdict.json` — 26/26 anchors and
3/3 samples byte-identical before/after; `changes.diff` — `anchors_changed=[]`,
production catalog main `bytes`/`mtime_ns` identical).

## 1. What exists after this attempt (retention rules)

KEEP (evidence — required for the independent review, do not clean before sign-off):

- `execution_runs/I-07-D/a20260923-01/**` — oracle/binding/commands/decision/
  changes.diff/handoff/evidence/** including superseded material:
  - `evidence/cases/F06C/*.pre_gate_fix/**` (first-attempt evidence, preserved)
  - decision.md §7 carries the **transcribed** F04 attempt-1 values (those original
    bytes were overwritten during the corrective rebuild — disclosed, unrecoverable)
- `%TEMP%\i07d\cases\{F01,F02,F03,F04,F05}` — isolated cells (rebuilt/validated
  product-isomorphic catalogs, rebound configs, F01 fixture config, F05 relocated
  production_observation_copy). Reviewer re-runs may reuse them; a fresh rebuild is
  also safe: `python harness/run_d_matrix.py build`.

SAFE TO CLEAN after the independent review signs off (scratch only):

1. `%TEMP%\i07d\**` — all cell trees, catalogs, raw copies
   (e.g. `Remove-Item -Recurse "$env:TEMP\i07d"`).
2. `evidence/wprobe_tmp/**` (throwaway wiring-probe catalog).
3. `iso/venv`, `iso/base`, `iso/rf`, `fixtures/` if the attempt dir itself is ever
   archived away (they are rebuildable: venv = I-00-A template recipe, iso/rf =
   read-only copy of RF scripts/config/references/tests, fixtures = I-07-B copies).

## 2. Processes / locks — verified clean at handoff

- No holder/locker/writer processes of this attempt remain: final scans found zero
  `hold_file.py` / `writer.py` / `lock_catalog.py` processes; every share-none handle
  was released via release-marker (F02 hold `released_by: release marker`, F05 same)
  and the F03 DB lock `hold.json` shows `released 2026-09-23T17:30:46Z, ok: true`.
- Both killed PIDs were this attempt's own manifest-registered processes (F04 wiki
  child pid 42124, F06C writer child); `evidence/census_diff.json` proves
  `real_source_catalog_gone=0` — **no real worker was ever killed or left dead**.
- Re-verify any time:
  `Get-CimInstance Win32_Process | Where CommandLine -match 'i07d|I-07-D|hold_file|writer\.py'`
  → must return nothing.

## 3. Real roots re-hash — unchanged (re-run to confirm)

```powershell
# anchors + samples (the same tool the card ran before/after):
<attempt>\iso\venv\Scripts\python.exe <attempt>\harness\snapshot.py after
# expect: anchor_count=26, raw_all_match=true, sidecar_all_match=true
# compare against evidence/snapshot_before.json → evidence/snapshot_verdict.json
```

Known disclosed stat-only delta: production catalog `-shm` **mtime** changed (bytes
unchanged 32768) from read-only WAL reader attachment (`mode=ro` +
`PRAGMA query_only=ON` on every open) — main `catalog.sqlite3` and `-wal` bytes+mtime
are identical before/after (`changes.diff` header). No data was written to production.

## 4. If something must be redone

- Re-run any cell: `<PY> harness/run_d_matrix.py f0X` (runs) or `f0Xv` (verdict
  recompute from existing evidence only — no product re-runs).
- F04 requires a truly fresh cell if re-run: `build_iso.py case F04 HK-XIAOMI-2025
  state3` + `scaffold_adapters.py` + clear `evidence/cases/F04/{counters,state,run*,
  verdict.json}` (this is exactly what the corrective rebuild did; disclose it again
  if repeated).
- Never point any fault tool at a production path: `hold_file.py` refuses targets
  outside the `i07d` tree by construction; `lock_catalog.py` resolves the catalog only
  under `%TEMP%\i07d\cases`; kill gates refuse PIDs without a matching manifest.
