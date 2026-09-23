# F-EE1-FIX recovery (exact revert) — a20260923-01

Nothing in a live worktree was modified by this attempt (proof: `binding_after.json`
`live_pins_changed_vs_before=0`; `evidence/porcelain_at_close.txt` — no tracked
modification outside pre-existing entries). Revert paths, worst case first:

## 1. Revert the ISO fix (restore pristine iso, one line)

```powershell
Copy-Item "C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\canonical_writer.py" `
  "C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\F-EE1-FIX\a20260923-01\iso\cw\src\company_wiki\source_catalog\canonical_writer.py" -Force
# expected sha after revert: c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258
```

## 2. If the fix was landed into live company-wiki (it was NOT by this attempt)

```powershell
Set-Location "C:\Users\郑曾波\Projects\company-wiki"
git apply -R "<ATT>\changes.diff"        # exact inverse of the delivered diff
# or, if the change is the only uncommitted edit to that file:
#   git checkout -- src/company_wiki/source_catalog/canonical_writer.py
```
Verify: `Get-FileHash src\company_wiki\source_catalog\canonical_writer.py` ==
`c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258`.

## 3. Re-apply the fix after a revert (forward direction)

```powershell
Copy-Item "<ATT>\iso\canonical_writer.py.fixed" `
  "<ATT>\iso\cw\src\company_wiki\source_catalog\canonical_writer.py" -Force
# sha must become 4bc653725febcc755e3a01ac48227a6b0799c4c262968356b356f8cb42d3c6bc
# (or apply changes.diff forward with: git apply <ATT>\changes.diff)
```

## 4. Scratch cleanup (all disposable, %TEMP% only)

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue @(
  "$env:TEMP\f_ee1_harness_*", "$env:TEMP\f_ee1_b2_*",
  "$env:TEMP\f_ee1_e2e_work", "$env:TEMP\f_ee1_bt_cw",
  "$env:TEMP\f_ee1_bt_rf", "$env:TEMP\f_ee1_bt_ff", "$env:TEMP\f_ee1_bt_e2etests",
  "$env:TEMP\f_ee1_cc_check.pyc")
```

## 5. Full attempt-artifact removal (only if the attempt itself must vanish)

Delete `<ATT>` entirely (`...\execution_runs\F-EE1-FIX\a20260923-01`). It is the only path
this attempt ever wrote inside the RF worktree; RF's pre-existing untracked leftovers
(`.tmp-r41-mutation/`, `assurance/.../plan_inputs.json.bak`) are NOT part of it — leave them.
