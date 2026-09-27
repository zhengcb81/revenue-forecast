# commands.md — RF-RATCHET-FIX-2 / a20260923-01 (command log, chronological; all runs Windows / Python 3.13.9)

Working dirs: RF = `C:\Users\郑曾波\Projects\revenue-forecast` (sources READ-ONLY).
ATTEMPT = `<RF>\.planning\2026-09-19-three-project-history-audit\execution_runs\RF-RATCHET-FIX-2\a20260923-01`.
ISO = `%TEMP%\rf2-iso` (pristine baseline copy, scripts+tests verified byte-equal to live,
`evidence/integrity/iso_vs_live_hashes.txt`: 0 mismatches). WORK = `%TEMP%\rf2-iso-work`
(same copy + refactors applied progressively). All pytest runs: `-B` (no .pyc) +
`-p no:cacheprovider` (repo cache-clean); basetemps under `%TEMP%`.

## 1. Verbatim RED command exactly as written in the card (kept raw)
```
python -m pytest tools/tests/test_complexity_ratchet.py -q --basetemp %TEMP%\rf2-red-bt -B
```
→ exit 4, `unrecognized arguments: -B` (pytest rejects trailing interpreter flag). Raw:
`evidence/red/red_verbatim_command.txt`. Disclosed interpretation (identical to predecessor §7):
`-B` is a CPython interpreter flag → judged equivalent below.

## 2. Judged RED (live RF repo) — must match oracle §2
```
cd /d C:\Users\郑曾波\Projects\revenue-forecast
python -B -m pytest tools/tests/test_complexity_ratchet.py -q --basetemp %TEMP%\rf2-red-bt -p no:cacheprovider
```
→ 2 failed: `analysis/confidence.py max 32 > 23`, `model_extensions.py max 27 > 10`. Raw:
`evidence/red/ratchet_red_judged.txt`.

## 3. Full-row scan (import-based, test module's own `_mccabe`/`_max_complexity`)
```
python -B evidence\measure\scan_all_violations.py   > evidence\measure\full_row_scan_before.txt
```
## 4. Independent inlined twin (no import of test module) — MUST agree with #3
```
python -B evidence\measure\independent_crosscheck.py > evidence\measure\independent_crosscheck_before.txt
```
→ both agree: 7 frozen + 1 new violation = 8 rows on HEAD b7a6a116.

## 5. Per-function CC (same measurement code as the test)
```
python -B evidence\measure\measure_cc.py <file...>   > evidence\measure\per_function_cc_{before,after}.txt
```

## 6. Family runs (24 test files union: 17 confidence-touching + 7 model_extensions importers)
```
python -B -m pytest <24 files listed in decision.md §3> -q -p no:cacheprovider --basetemp %TEMP%\rf2-fam-{before,after}-bt
```
before = ISO (pristine), after = WORK (refactored).

## 7. Per-file judged runs (WORK tree, per row)
```
python -B -m pytest tools/tests/test_complexity_ratchet.py -q --basetemp %TEMP%\rf2-green-bt -p no:cacheprovider
```
(+ mutation variants per decision.md §5).

## 8. Golden-lock gate (before AND after)
```
python -B -m pytest tests/test_golden_behavior_lock.py tests/test_model_extensions_anchor.py -q -p no:cacheprovider --basetemp %TEMP%\rf2-gold-bt
```

## 9. changes.diff (vehicle; exactly 2 files)
```
git -C <RF> diff --no-index <baseline copies vs refactored copies>  (paths normalized to a/scripts/... b/scripts/...)
```

No network. No git mutations (read-only verbs: log/-1, status --porcelain, diff --no-index). Scratch,
basetemps and iso trees under `%TEMP%`.
