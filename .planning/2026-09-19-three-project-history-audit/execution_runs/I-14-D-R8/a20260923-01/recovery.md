# WC-1 / I-14-D-R8 recovery — how to resume, reproduce, or undo

## What exists where

- Deliverables: this directory (`oracle.md`+`oracle.sha256`, `binding.json`, `commands.md`,
  `decision.md`, `changes.diff`, `handoff.md`, `recovery.md`, `evidence\`, `harness\`).
- Isolated trees (inside attempt, regenerable): `iso/r8_base` (pin `2f644994…`),
  `iso/r8_fixed` (pin `90b3fdc3…`). Both are COPIES; delete and rebuild freely with
  `harness/build_r8.py` — it re-copies from the sealed predecessor and re-applies the three
  literal edits with count assertions.
- r8 instruments (new carriers): `harness/run_i14d_oracle_r8.py` (`ad7861ee…`),
  `harness/run_rule_table_i14d_r8.py` (`ffe3372b…`). Their bases are the r7-frozen r6
  harnesses in the sealed I-14-D attempt (pins re-verified by this card).
- Scratch (safe to delete, `%TEMP%`): `i14dr8_mutants\MUT-A-revert-REM06`,
  `i14dr8_mutants\MUT-B-revert-R305` (regenerate: `harness/build_mutants.py`),
  `i14dr8_prodapply\src` (regenerate: `harness/make_changes_diff.py`).

## Reproduce the whole matrix (from this directory, PowerShell)

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $py='C:\Miniconda\python.exe'
& $py -B .\harness\build_r8.py                     # rc 0: rebuilds iso/r8_base + iso/r8_fixed + r8 harnesses
& $py -B .\harness\run_i14d_oracle_r8.py  --src .\iso\r8_base  --label r8_base  --out .\evidence\red_oracle_r8_base.json     # rc 3
& $py -B .\harness\run_rule_table_i14d_r8.py --src .\iso\r8_base --label r8_base --out .\evidence\red_rule_r8_base.json     # rc 3
& $py -B .\harness\run_i14d_oracle_r8.py  --src .\iso\r8_fixed --label r8_fixed --out .\evidence\green_oracle_r8_fixed.json  # rc 0
& $py -B .\harness\run_rule_table_i14d_r8.py --src .\iso\r8_fixed --label r8_fixed --out .\evidence\green_rule_r8_fixed.json # rc 3 (by design)
& $py -B .\harness\build_mutants.py                # rc 0
& $py -B .\harness\run_i14d_oracle_r8.py  --src "$env:TEMP\i14dr8_mutants\MUT-A-revert-REM06" --label mutA_oracle --out .\evidence\mutA_oracle_r8_fixed_minus_rem06.json   # rc 3
& $py -B .\harness\run_rule_table_i14d_r8.py --src "$env:TEMP\i14dr8_mutants\MUT-A-revert-REM06" --label mutA_rule   --out .\evidence\mutA_rule_r8_fixed_minus_rem06.json     # rc 3
& $py -B .\harness\run_i14d_oracle_r8.py  --src "$env:TEMP\i14dr8_mutants\MUT-B-revert-R305" --label mutB_oracle --out .\evidence\mutB_oracle_r8_fixed_minus_r305.json   # rc 3
& $py -B .\harness\run_rule_table_i14d_r8.py --src "$env:TEMP\i14dr8_mutants\MUT-B-revert-R305" --label mutB_rule   --out .\evidence\mutB_rule_r8_fixed_minus_r305.json     # rc 3
& $py -B .\harness\sweep_key_domain.py            # rc 0 (pass)
& $py -B .\harness\sweep_value_start.py           # rc 0 (pass)
& $py -B .\harness\diag_key_sweep.py              # rc 0
& $py -B .\harness\make_changes_diff.py           # rc 0 (rewrites changes.diff byte-identically)
& $py -B .\harness\final_integrity.py             # rc 0: pin recompute + zero-write scan
```

product_base direction runs (read-only, `-B` mandatory so the sealed tree stays clean):

```powershell
$B='..\I-14-D\a20260919-01\iso\product_base\src'
& $py -B .\harness\run_i14d_oracle_r8.py    --src $B --label base_oracle --out .\evidence\base_oracle_product_base.json   # rc 3 (direction only)
& $py -B .\harness\run_rule_table_i14d_r8.py --src $B --label base_rule   --out .\evidence\base_rule_product_base.json   # rc 3 (direction only)
```

## Undo / scope facts

- NOTHING outside this attempt directory was written by this card (verified:
  `evidence/final_integrity.json` — production `edcbeccb…`, register `5348278f…`,
  WC-1 decision `a68ed77f…`, r6 tree `2f644994…`, r6 harnesses `85a1b064…`/`8f5feffd…` all
  unchanged; zero files modified today under the sealed I-14-D attempt / REGISTRY-CLOSURE /
  company-wiki src).
- The product fixes exist ONLY inside `iso/r8_fixed` (scratch copy) and `changes.diff`.
  Landing them anywhere real = the owner's next promotion/repair batch (apply `changes.diff`;
  both hunks-sets are independently apply-checked — `evidence/production_apply.json`).
- If a reviewer disagrees with a fix: revert = rebuild from `iso/r8_base` (the pinned r6
  tree); no inverse patch is needed because production/sealed trees were never touched.
- Mid-flight resume point: if this attempt is found incomplete, the state machine is
  `oracle frozen → build → red → green → base → mutants → sweeps → changes.diff → carriers`;
  every step's rc is archived in `evidence/*.rc.txt`, so re-running any single step is safe
  and idempotent (all scripts overwrite their own outputs).
