# WC-6 recovery / continuation

Attempt `a20260923-01` (card **WC-6-ADAPTER-DISPATCH**, REM-95). Read this together with
`binding.json` (pins), `oracle.md` (frozen expectations) and `handoff.json` (next action).

## 1. What is where

| Path | Role | Writable? |
|---|---|---|
| live `C:\Users\郑曾波\Projects\company-wiki` (CW) | product sources — **READ-ONLY for this card** | no (delivery is `changes.diff` only) |
| `<attempt>/iso/cw/` | byte-identical copy of CW `src/ tests/ config/` (503-file pin, `evidence/source_pins_before.json`) — the ONLY place the fix is applied | yes (iso only) |
| `<attempt>/iso/venv/` | interpreter cloned from I-07-C's venv (lineage I-06-A → I-00-A); `PYTHONPATH=<attempt>/iso/cw/src` | yes |
| `<attempt>/iso/fixed/` | byte snapshot of the two FIXED product files | yes |
| `%TEMP%\wc6\cells\probes\cwroot` | isolated probe cell (one root, 4 probe files), rebuilt fresh by `harness/prepare.py <label>` | yes (temp) |
| `<attempt>/evidence/` | all raw outputs, normalized comparisons, family runs | yes |
| `<attempt>/harness/` | the scripts that produce the evidence | yes |

## 2. Exact state of the code under test (how to verify in one command)

```powershell
$att='<attempt>'
$py=Join-Path $att 'iso\venv\Scripts\python.exe'
(Get-FileHash -Algorithm SHA256 (Join-Path $att 'iso\cw\src\company_wiki\source_catalog\adapter_dispatch.py')).Hash.ToLower()
(Get-FileHash -Algorithm SHA256 (Join-Path $att 'iso\cw\src\company_wiki\source_catalog\scanner.py')).Hash.ToLower()
```

Expected at handoff (**fix present**):
`adapter_dispatch.py = 0c5ac1a2c2a4bd53dc10f954bd4d429b2d5511dcc8610b3b901ea11c10754769`,
`scanner.py = 85d96757b627a45e3487197d164eb611a19aa54bcfbfc4eb62ad223bd02a47a9`.

If you need the pre-image (RED) instead: copy the two files back from live CW
(`iso == live` held at step 2; `pin_sources.py after` re-proves live never moved) —
that is exactly how the `red_prefix` arm was produced.

## 3. Re-running every claim (all commands run from `<attempt>`, no git)

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; $env:PYTHONPATH=(Join-Path $att 'iso\cw\src')
& $py -X utf8 -B harness\pin_sources.py before     # pins + iso==live proof
& $py -X utf8 -B harness\prepare.py green          # fresh probe cell (tree_sha256 must equal 37be0c5a…)
& $py -X utf8 -B harness\run_stage.py green scan   # then rescan / resolve / cfg01
& $py -X utf8 -B harness\compare_runs.py red_prefix green   # rc 0 = outcome bytes identical
& $py -X utf8 -B harness\reason_chain.py chain     # rc 0 = 4 hops x 4 probes match oracle
& $py -X utf8 -B harness\select_family.py
& $py -X utf8 -B harness\run_family.py fam_rerun --cwd iso   # ~25 min; compare with compare_family.py
& $py -X utf8 -B harness\make_changes_diff.py      # regenerates changes.diff (must be sha ad88feed…)
& $py -X utf8 -B harness\pin_sources.py after      # live CW must not have moved
```

## 4. How to reproduce the MUTATION arm (non-vacuity) safely

1. `Copy-Item iso\fixed\adapter_dispatch.py <iso adapter_dispatch.py>` (fix present).
2. Byte-replace, in the iso file only:
   `error=item.evidence.get("remediation"),` → `error=None,  # MUTATION …`
   (the attempt used a **byte-level** replace: the file is CRLF; a text-mode write would
   rewrite every line ending — see decision.md "harness corrections").
3. `prepare.py mutation` + `run_stage.py mutation scan` ⇒ `locations.error` must be `NULL` ×4.
4. Restore with `Copy-Item iso\fixed\adapter_dispatch.py <iso path>` and re-check the hash.

Never run the mutation against live CW.

## 5. Failure / abort rules (frozen in oracle §8)

- live CW pin drift ⇒ STOP, report `blocked` (isolation broken) — do not "fix" CW to match.
- family outcome differs before/after ⇒ STOP, keep the failing run's raw output; do not re-run
  until green and do not edit tests.
- fixture `tree_sha256` differs between arms ⇒ the input was not held constant; discard the arm
  and rebuild with `prepare.py`.
- If an interrupted run leaves the cell half-built: just re-run `prepare.py <label>` — the cell
  is disposable and rebuilt from scratch every time (evidence dirs are never overwritten by
  `prepare`; only `run_stage.py` writes into `evidence/<label>/<stage>`).

## 6. Cleanup (authorized only AFTER the reviewer accepts this attempt)

- `%TEMP%\wc6\cells\**` (isolated cell) — disposable, rebuildable from `harness/prepare.py`.
- `<attempt>/iso/venv` (~28 MB) — rebuildable by cloning any card venv in the lineage.
- Do NOT delete `evidence/`, `oracle.md`, `binding.json`, `commands.json`, `changes.diff`,
  `decision.md`, `handoff.json` before the review is landed (they are the review surface).

## 7. Known non-blocking conditions to disclose on continuation

- The regression family has **23 pre-existing failures and 8 pre-existing skips in the
  baseline (pre-fix)** — see `evidence/fam_before_family.txt`. 18 of them are iso-scope
  artifacts (the iso copies `src/ tests/ config/`, not `scripts/`, so
  `snapshot_catalog.py` / `source_catalog_control.ps1` / `source_catalog_worker_at_logon.vbs`
  are absent); the other 5 are pre-existing/environmental, including the complexity-ratchet
  failure `archive_retired_evidence.py 19 > frozen 7` which is a **live-CW pre-existing
  condition unrelated to this card**. The card's contract is *before == after on this same
  tree*, not "family is green".
- `test_fc1204_coverage_ratchet` skips by design unless `FC1204_COVERAGE_GATE=1` with a fresh
  `coverage.json` (existing conditional skip; this card adds none).
