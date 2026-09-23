# I-07-C recovery / cleanup

## What this attempt created outside its own directory

1. `%TEMP%\i07c\cells\` — seven isolated company-wiki cell trees
   (`X04-multiroot`, `X05-fifthroot`, `UNK-adapter`, `UNK-sidecar`, `UNK-kind`,
   `X01-companies-only`, `X02-dayu-only`): each holds a rebound
   `cwroot/config/source_catalog.yaml`, a product-initialized 18-table
   `.source_catalog/catalog.sqlite3`, copied/adapted root assets and the
   `resolve_request.json` inputs. Nothing here is product state.

## How to remove (the whole isolation is disposable)

```powershell
Remove-Item -Recurse -Force "$env:TEMP\i07c"
Remove-Item -Recurse -Force "C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-07-C"
```

Deleting those two trees removes everything this card wrote. No product file,
no production catalog row, no real external root byte was modified — so there is
nothing to restore, only to re-verify.

## Real roots must re-hash unchanged (post-recovery verification)

Re-run the witness after cleanup and compare against
`evidence/snapshot_before.json` (the frozen pre-run values):

```powershell
Set-Location "C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-07-C\a20260923-01"
& .\iso\venv\Scripts\python.exe -X utf8 -B .\harness\snapshot.py after
# then compare evidence/snapshot_after.json vs evidence/snapshot_before.json
```

Required outcome (already measured once in `evidence/snapshot_verdict.json`,
`no_mutation: true`):

- all 16 product anchor sha256 values identical (RF/CW/FF source + production
  `config/source_catalog.yaml`),
- the 3 manifest samples (raw + sidecar, full sha256) identical to the manifest
  pins,
- production catalog identity (size 49,677,344,476 / mtime) identical —
  [F-REV-3 correction: the figure `49,677,344,476` on the line above is a digit transposition; true size = 49,677,344,768 bytes — evidence: reviewer live stat (mtime 2026-09-19T06:31:35.406919Z) + evidence/snapshot_before.json + evidence/snapshot_after.json + evidence/prod_census.json + evidence/prod_census.run1_threaderror.json + the reviewer's census re-run all = 49677344768; the wrong figure `…476` occurs in exactly this one place (reviewer_report.md §D / finding F-REV-3); pinned pre-image sha256 5ca0c271c83227b75a921a59ef283d23a364d5beed4f4c876f9af525d0dabd86 retained — the pinned figure is annotated here, NOT rewritten]
  a full sha256 of a 49.7GB file is not feasible and is recorded as such,
- real external roots (`CW/companies`, `CW/future_lake`, `dayu-agent/workspace/portfolio`,
  `Dropbox/Stock`) identical file count / total bytes / max mtime (full sha for
  `future_lake`, which is under the 10MB full-hash policy threshold).

## Cell-specific notes

- `X05-fifthroot` and `UNK-sidecar` each have a **superseded first run**
  (`scan1`, and `resolve1` for X05) whose evidence was deliberately kept: the
  first runs exposed two defects of MY fixture (X05 sidecar lacked the
  `source_url` the resolver's capture-ready gate requires — resolver.py:1919-1965;
  UNK-sidecar's clean probe declared a pre-newline-translation hash). The
  fixtures were completed, `scan2`/`resolve2` were captured alongside — never
  over — the first evidence.
- `X03-external-only` has NO tree by design: it is BLOCKED for lack of a
  reviewer-frozen sample and must never be materialized by deleting other copies.

## Recovery rule carried from I-07-B (exit declaration 3, verbatim)

恢复：保留已取得raw，只回退当前隔离变更。
