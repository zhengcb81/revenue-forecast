# COMMANDS — exact command plan (no git mutations; read-only git only for pins/apply-check in scratch)

Notation: `$A` = attempt dir, `$ISO` = `%TEMP%\cwgu1\repo`, `$CW` = company-wiki,
`$E` = `$A\evidence`. Every run's raw output tee'd into `$E`.

## 0. Iso build + identity verification
```powershell
robocopy $CW\src     $ISO\src     /E /XD __pycache__ .pytest_cache .mypy_cache .ruff_cache
robocopy $CW\tests    $ISO\tests    /E /XD __pycache__ .pytest_cache .mypy_cache .ruff_cache
robocopy $CW\scripts  $ISO\scripts  /E /XD __pycache__ .pytest_cache .mypy_cache .ruff_cache
robocopy $CW\config   $ISO\config   /E
robocopy $CW\tools    $ISO\tools    /E
robocopy $CW\.source_catalog\security_master $ISO\.source_catalog\security_master /E
copy root files: conftest.py, pytest.ini, pyproject.toml
Get-FileHash iso gate+archive files  == compare with binding pins (byte identity before RED)
```

## 1. RED — RC-1 gate encoding crash (CURRENT, pinned-identical gate file)
```powershell
# repro_write E01_gate_crash_repro.py: import gate module from $ISO\tools,
# then sys.stdout.reconfigure(encoding='gbk', errors='strict')   # simulate Windows GBK console
# then pre_push_gate._run([py, "-c", "import sys; sys.stderr.write('payload \\u05a3 ok\\n'); sys.stderr.flush(); sys.exit(3)"], "repro-step")
# then print REPRO-RC and sys.exit(rc)
python $E\E01_gate_crash_repro.py        # EXPECT: UnicodeEncodeError 'gbk' codec can't encode '\u05a3'; abnormal exit (≠3) → RED log
```

## 2. RED — RC-2 complexity ratchet (CURRENT archive file) + baseline of its test family
```powershell
cd $ISO; $env:PYTHONPATH="$ISO\src"
python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q   # EXPECT fail: "max complexity 19 exceeds frozen 7"
python -m pytest tests/contract/test_source_catalog_archive_retired.py tests/contract/test_fc1204_coverage_ratchet.py -q  # EXPECT pass (baseline; coverage test skips)
```

## 3. Fixes (ISO copies only — CW untouched)
- Edit `$ISO\tools\pre_push_gate.py` (RC-1: encoding-safe output printing).
- Edit `$ISO\src\company_wiki\source_catalog\archive_retired_evidence.py` (RC-2: split
  monolith into ≤7-complexity helpers, pure code motion, zero behavior change).

## 4. GREEN — RC-1 + RC-2
```powershell
python $E\E01_gate_crash_repro.py        # EXPECT: prints payload, exit code == 3 (rc propagation preserved)
cd $ISO; python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q   # EXPECT 2 passed
python -m pytest tests/contract/test_source_catalog_archive_retired.py tests/contract/test_fc1204_coverage_ratchet.py -q  # EXPECT pass, no regression
python $E\measure_cc.py <fixed file>     # EXPECT every function ≤7, file max ≤7
python -m ruff check <fixed archive file> tools/pre_push_gate.py  # style-safe (step-1 scope includes src)
python -m compileall -q src scripts tests                        # step-2 scope sanity
```

## 5. MUTATION — non-vacuous proof (scratch edit of the fixed file, then restore)
```powershell
# M2 (single split reverted): inline _write_rows hot loop back into archive_retired_evidence()
python $E\measure_cc.py <mutated file>   # EXPECT archive_retired_evidence() CC ≥8
cd $ISO; python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q  # EXPECT RED "max complexity N exceeds frozen 7"
# M1 (full revert control): copy pinned ORIGINAL archive file over fixed → ratchet EXPECT RED 19>7
# RESTORE fixed file; re-run ratchet → EXPECT 2 passed (green restored)
```

## 6. FULL gate step discovery (fixed iso) — per-step then whole-gate
```powershell
cd $ISO; $env:PYTHONPATH="$ISO\src"
step1: ruff check src tests/unit tests/contract scripts
step2: python -m compileall -q src scripts tests
step3: python scripts/config_doctor.py
step4: python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q
step5: python scripts/host_assumption_guard.py
step6: python -m pytest -q --timeout=180 <the six files from binding>
record rc of each → FULL STATUS TABLE (any new failure = in-scope fix or BLOCKED-with-evidence)
whole: python tools/pre_push_gate.py      # EXPECT "pre-push gate GREEN", rc 0
```

## 7. changes.diff build + verification
```powershell
# OLD tree = pinned originals, NEW tree = fixed iso files, identical relative paths
git diff --no-index -- OLD NEW  → post-process headers → a/ b/ paths → $A\changes.diff
# apply-check in scratch repo (git operations ONLY inside %TEMP% scratch):
cd $VERIFY; git init; copy the two ORIGINAL files at their paths;
git apply --check changes.diff; git apply changes.diff;
byte-compare applied files vs $ISO fixed files (must be identical)  → evidence
```

## 8. Docs + handoff: decision.md, evidence index, handoff.md, recovery.md, report, send_message to parent.

## Prohibited (checked at the end)
- NO write anywhere under $CW / revenue-forecast sources / filing-fetch (RF/FF untouched).
- NO `git add/commit/stash/checkout/reset/push/...` in any real repo (read-only `git rev-parse/log/status/diff --no-index` + scratch-repo apply-check only).
- NO network. No frozen-bound increase, no baseline addition, no step bypass.
