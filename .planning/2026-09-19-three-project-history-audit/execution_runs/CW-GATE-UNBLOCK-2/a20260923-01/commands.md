# COMMANDS — CW-GATE-UNBLOCK-2 / a20260923-01 (EXECUTED record; no git mutations; %TEMP% scratch)

Notation: `$A` = attempt dir, `$ISO` = `%TEMP%\cwgu2\repo`, `$CW` = company-wiki,
`$E` = `$A\evidence`, `$P` = predecessor attempt dir. Every judged run's raw output
written into `$E` at run time (long runs tee'd progressively).

## 0. Inherit + freeze (FIRST writes) ✅
- read `$P\oracle.md` (sha `017C41BD…`), evidence `20/21/22/23/24/25/26-*`, iso `%TEMP%\cwgu1\repo`
- robocopy `%TEMP%\cwgu1\repo` → `%TEMP%\cwgu2\repo` /E (caches excluded) + sha identity of 7 pinned files (`10-iso-identity-check.log`, ALL IDENTICAL)
- wrote `$A\oracle.md` (§0 verbatim + APPEND A) BEFORE any judged run; living docs same turn

## 1. RC-1 re-verify (predecessor GREEN reused) ✅
```powershell
python $E\E01_gate_crash_repro.py        # predecessor iso gate: payload printed, exit==3
python $E\E02_gate_crash_repro_myiso.py  # my iso gate: payload printed, exit==3  (00/00b)
```

## 2. RC-2d PR4 (main work) — in $ISO only ✅
```powershell
ruff check $ISO\...\prune_retired_evidence.py          # RED: F821 absent/deleted (11)
# edit: replace duplicated inline batch loop with _delete_batches(...) call
python $E\measure_cc.py <file>                          # FILE-MAX 12, main 9 (12)
ruff check <file> ; python -m compileall -q <file>      # clean (12b/12c)
```

## 3. RC-2 RED(all-rows)/GREEN/mutation per row ✅
```powershell
python $E\enumerate_ratchet.py                                   # 0 violations (13)
python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q   # 2 passed (14)
# mutation rows a–d: merge one split → measure_cc → ratchet RED → restore → GREEN
#   a: inline _write_snapshot → 10>7 (16/16b) → restore (16c)
#   b: inline _find_closing_quote → 8>6 (23/23b) → restore (23c)
#   c: inline _parse_metadata → 19>15 (24/24b) → restore (24c)
#   d: inline _delete_batches → 17>12 (15/15b) → restore (15c)
```

## 4. Test-face lanes ✅ (each red/green/mutation; test files only)
```powershell
python -m pytest tests/contract/test_source_catalog_prune_retired.py -q   # RED now= (20)
# adapt: NOW= + plant real verified archives via archive_retired_evidence (D1)
python -m pytest tests/contract/test_source_catalog_prune_retired.py -q   # GREEN 3 passed (22)
# batch mutation (25–25e): backup shas → copy CW originals over 9 faces →
python -m pytest <9 files> -q    # 22 failed/75 passed = per-lane RED
# restore from backup (sha-verified) → python -m pytest <9 files> -q  # 96 passed +1 iso-fidelity rerun (26b) = 97/97
```

## 5. Coverage lane ✅ (CI-equivalent measurement)
```powershell
# BEFORE-A family-scoped (reproduce frozen 85.4): pytest <archive family> --cov=... --cov-branch --cov-report=json:scratch  (30) → 85.38%
# new file: tests/contract/test_archive_retired_evidence_fail_closed.py (12 fail-closed tests, 31)
# AFTER-A family-union (32) → 100.0% (141/141, 30/30)
# BEFORE-B / AFTER-B: pytest tests/ -q --tb=short --cov=src/company_wiki/source_catalog --cov-branch --cov-report=json:<path>
#   (CI step-identical; AFTER-B isolates the data file via COVERAGE_FILE env because
#    --cov-data-file is unsupported in this pytest-cov — same measurement semantics)
# judged: copy AFTER-B json → $ISO\coverage.json; FC1204_COVERAGE_GATE=1 pytest tests/contract/test_fc1204_coverage_ratchet.py (36)
```

## 6. Gate full-run (final tree) ✅
```powershell
# per-step then whole (50-gate-fullrun.log): steps 1–6 ALL rc=0; whole gate rc=0; unique-symbols rc=0
python tools/pre_push_gate.py
```

## 7. changes.diff build + verification ✅
```powershell
# OLD tree = CW originals, NEW tree = iso finals + staged new file (15 files)
Push-Location $V; git diff --no-index --binary --output=raw2.diff OLD NEW   # rc=1 expected
# post-process a/OLD/ b/NEW/ a/NEW/ → a/ b/ (byte-exact, no EOL normalization) → $A\changes.diff
# apply-check scratch repo: git init; git apply --check (rc=0); git apply (rc=0)
# content-identity after LF normalization: 15/15 IDENTICAL (42/43/44)
# note: git apply under host core.autocrlf=true smudges EOL only; repo-stored bytes identical
```

## 8. Docs close + report + send_message ✅ (this file last, then re-opened by §9)

## 9. Close-out batch (last-gate card: attribution + final three + handoff) ✅
```powershell
# 0. read register §一一七 + oracle/decision/handoff/binding; baseline: git diff HEAD non-.planning = 0
# 1. dual judgment (same cmd/pytest/criteria; writable byte-identical copy — iso writes are sandbox-denied)
Copy-Item scratch\cov_afterB.json <copy>\coverage.json ; FC1204_COVERAGE_GATE=1 python -m pytest -q tests/contract/test_fc1204_coverage_ratchet.py   # 39a = reproduces 36
Copy-Item scratch\cov_beforeB.json <copy>\coverage.json ; FC1204_COVERAGE_GATE=1 python -m pytest -q tests/contract/test_fc1204_coverage_ratchet.py   # 39b = same 3 rows red
# 2. raw + bound: python evidence\attr_3modules.py                                        # 40
# 3. CI-equivalent dual runs verified COMPLETE on disk (33b/34 footers)                    # 51  (33 stays VOID)
# 4. failure classification + iso-artifact check: evidence\classify_afterB_failures.py      # 52, 53 ; zr409 isolated re-run # 46
# 5. 15-file sha table (read-only hashes of CW + iso)                                      # 47
# 6. deliverables: final_report.md (D.1/D.2/D.3) + decision.md §8 (append-only) + handoff.json
# attempted-but-denied: copy into iso (→ VOID 38); full-suite diagnostic 37 redo (→ blocked, 49)
```
