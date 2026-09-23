# recovery.md — RF-E2E-ADAPT (before-pins revert)

No git was used; full pre-edit content of every touched file is frozen in
this attempt, so any revert is a file copy.

## Files frozen (before-pins)

| frozen copy | sha256 (= BEFORE pin in binding.md) |
|---|---|
| `diffs/before/tests/e2e_support/isolated_lake.py` | `210FB643A123371B3C250ABAC68473BE1FF71E417579F18033957C350B5F1A37` |
| `diffs/before/tests/test_zr803_chaos_recovery.py` | `B426F77459038D94C0DB3893E3532631BDAE01F4A2D2CF658C84175389655A0B` |
| `diffs/before/tests/test_preparation_e2e_success.py` | `1CECA7AB69357BFEE7AF0AECA15FD75DAD270B90F1FC29546540349D7D95A22C` |
| `diffs/before/tests/test_zr709_zijin_journey.py` | `1A4E0B2616A5C996FA7B899A69E28169909F56BF5B2D0B7F91ED908CD180FA3D` |

## Full revert to pre-attempt state (all four files)

From RF root:

```powershell
$attp = ".planning\2026-09-19-three-project-history-audit\execution_runs\RF-E2E-ADAPT\a20260923-01"
Copy-Item "$attp\diffs\before\tests\e2e_support\isolated_lake.py" "tests\e2e_support\isolated_lake.py" -Force
Copy-Item "$attp\diffs\before\tests\test_zr803_chaos_recovery.py"  "tests\test_zr803_chaos_recovery.py"  -Force
Copy-Item "$attp\diffs\before\tests\test_preparation_e2e_success.py" "tests\test_preparation_e2e_success.py" -Force
Copy-Item "$attp\diffs\before\tests\test_zr709_zijin_journey.py"   "tests\test_zr709_zijin_journey.py"   -Force
```

Then re-pin against `binding.md` BEFORE column — any mismatch means the
revert did not land.

**Expected state after full revert:** the real-roots E2E step is RED again
with the `prompt_injection_status=not_reviewed` upstream error (this is the
pre-attempt state; reverting is for rollback of THIS attempt only — do not
push it: it re-opens gate failure RF-E2E-ADAPT).

## Partial rollback

- To undo only the mutation-demonstration artifact: none is possible to leave
  behind — the mutation step restores `diffs/after/.../isolated_lake.py`
  (`867AC82B…`) as its final action and re-verifies the hash in the same
  command.
- CW repo: nothing to roll back (zero writes, oracle clause (e)).

## Fix-only re-apply (if a later revert wiped the fix)

`diffs/after/tests/e2e_support/isolated_lake.py`
(`867AC82BCB48E9FD81592C2304AC390453B5B1F85BEE0B8D9EFA476D57AA2883`) holds the
fixed root fixture; `changes.diff` holds the exact deltas for all four files.
