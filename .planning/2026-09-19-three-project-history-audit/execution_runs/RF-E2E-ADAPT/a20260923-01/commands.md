# commands.md — RF-E2E-ADAPT (every command executed, in order)

No git, no bypass, no gate-step edits. All from RF root
(`C:\Users\郑曾波\Projects\revenue-forecast`) unless noted.

## Phase 0 — investigation (pre-freeze, no edits)

```powershell
# which company_wiki package the interpreter resolves (live CW src, not vendored)
python -c "import company_wiki; print(company_wiki.__file__)"
# → C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\__init__.py

# live receipt-read probe (fixture receipt vs live CW reader; + state_domain)
python <ATTEMPT>\evidence\probe_receipt_read.py
# → evidence/probe_receipt_read.out
```

## Phase 1 — RED reproduction (oracle clause b), raw captured

```powershell
python -m pytest -q tests/test_fc1002_three_process_e2e.py `
  "tests/test_zr803_chaos_recovery.py::test_lock_held_write_transaction_does_not_block_read_journey" `
  --basetemp="$env:TEMP\rf-e2e-adapt-red" --tb=short
# → evidence/red_raw.txt  — 4 failed in 30.64s
```

zr803-alone + attribution probes (oracle step 3):

```powershell
python -m pytest -q "tests/test_zr803_chaos_recovery.py::test_lock_held_write_transaction_does_not_block_read_journey" `
  --basetemp="$env:TEMP\rf-adapt-zr803-lock" --tb=long
# → evidence/red_zr803_lock_raw.txt

python <ATTEMPT>\evidence\probe_zr803_chain.py
# → evidence/probe_zr803_chain.out  (LOCK-HELD rc=3 + AFTER-RELEASE rc=3, both not_reviewed)
```

Same-family attribution (real-data receipt twins, standalone):

```powershell
python -m pytest -q tests/test_preparation_e2e_success.py --basetemp="$env:TEMP\rf-adapt-prep-e2e" --tb=line
# → evidence/red_prep_e2e_raw.txt  — 1 failed (same not_reviewed block)
python -m pytest -q tests/test_zr709_zijin_journey.py --basetemp="$env:TEMP\rf-adapt-zr709" --tb=line
# → evidence/red_zr709_raw.txt  — 1 failed, 8 passed (same not_reviewed block)
```

## Phase 2 — oracle frozen (edits start only after this)

`<ATTEMPT>/oracle.md` written; before-copies of all four candidate files
frozen under `<ATTEMPT>/diffs/before/` (sha-pinned in binding.md).

## Phase 3 — the fix (4 RF test/fixture files, see changes.diff)

Edits applied via the file-edit tool to:

1. `tests/e2e_support/isolated_lake.py`
2. `tests/test_preparation_e2e_success.py`
3. `tests/test_zr709_zijin_journey.py`
4. `tests/test_zr803_chaos_recovery.py` (message expression only)

## Phase 4 — GREEN (oracle clause c): gate's EXACT real-roots selection

The selection is quoted from `tools/pre_push_gate.py:141-149` + `:178-181`
(`_real_roots()` runs `python -m pytest -q --tb=short <REAL_ROOTS_TESTS>`):

```powershell
python -m pytest -q --tb=short `
  tests/test_zr803_chaos_recovery.py tests/test_zr1103_journey_reverify.py `
  tests/test_ca203_weekly_t3.py tests/test_fc1101_ci_manifest.py `
  tests/test_compatibility_manifest.py tests/test_fc1002_three_process_e2e.py `
  tests/test_ca302_three_journeys.py `
  --basetemp="$env:TEMP\rf-e2e-adapt-green"
# → evidence/green_raw.txt
```

Immediate-4 re-check (first signal after the edit):

```powershell
python -m pytest -q tests/test_fc1002_three_process_e2e.py `
  "tests/test_zr803_chaos_recovery.py::test_lock_held_write_transaction_does_not_block_read_journey" `
  --basetemp="$env:TEMP\rf-e2e-adapt-post" --tb=short
# → 4 passed in 30.27s
```

Same-family real-data twins:

```powershell
python -m pytest -q tests/test_preparation_e2e_success.py tests/test_zr709_zijin_journey.py `
  --basetemp="$env:TEMP\rf-e2e-adapt-family" --tb=short
# → evidence/green_family_raw.txt — 10 passed in 28.86s
```

## Phase 5 — other fast gate steps (all untouched-step verification)

```powershell
ruff check scripts tests tools e2e                     # → All checks passed (RUFF=0)
python -m compileall -q scripts tests tools e2e        # → COMPILEALL=0
python tools/check_unique_test_symbols.py              # → OK: 123 files, no duplicates
python tools/host_assumption_guard.py --roots tests tools scripts e2e
# → violations=24; new(not baselined/registered)=0; baseline=16   (NO baseline additions)
```

## Phase 6 — MUTATION (oracle clause d): revert the fixture change ⇒ red returns

```powershell
# save fixed copy first, then restore the pre-edit fixture
Copy-Item tests\e2e_support\isolated_lake.py <ATTEMPT>\diffs\after\tests\e2e_support\isolated_lake.py -Force
Copy-Item <ATTEMPT>\diffs\before\tests\e2e_support\isolated_lake.py tests\e2e_support\isolated_lake.py -Force

python -m pytest -q tests/test_fc1002_three_process_e2e.py `
  "tests/test_zr803_chaos_recovery.py::test_lock_held_write_transaction_does_not_block_read_journey" `
  --basetemp="$env:TEMP\rf-e2e-adapt-mutation" --tb=short
# → evidence/mutation_raw.txt (expect the not_reviewed reds again)

# restore the fix and pin it
Copy-Item <ATTEMPT>\diffs\after\tests\e2e_support\isolated_lake.py tests\e2e_support\isolated_lake.py -Force
Get-FileHash -Algorithm SHA256 tests\e2e_support\isolated_lake.py   # must equal the after-pin
```

## Phase 7 — deliverable generation (no git)

```powershell
python <ATTEMPT>\make_diff.py    # difflib before/after → changes.diff
Get-FileHash -Algorithm SHA256 <touched files>          # binding pins
Get-FileHash -Algorithm SHA256 <evidence logs>          # gate-log hash quotes
```
