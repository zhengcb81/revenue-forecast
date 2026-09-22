# I-14-E after/analysis.md (rendered from analysis.json)

## 1. Frozen observation band (hand-computed from the raw record)

- source: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-C\a20260919-01\r5\flake-evidence\frequency-child_without_runtime.json` (sha256 `68d4e63e64744f09...`)
- completeness: 48 rows / events files 48 / stdout byte-identical to the frozen captures 48

| round/tree | runs | failed | child_started histogram |
|---|---|---|---|
| pass1/T0 | 12 | **3** | 2x9, 3x3 |
| pass1/T4 | 12 | **2** | 2x10, 3x2 |
| pass2/T0 | 12 | **3** | 2x9, 3x3 |
| pass2/T4 | 12 | **4** | 2x8, 3x2, 4x2 |

- per-tree totals: {"T0": {"runs": 24, "failed": 6}, "T4": {"runs": 24, "failed": 6}}
- flip: pass1 more-failing tree `T0`, pass2 `T4`

## 2. Independent window measurement (M-A / M-C)

- **popen-quiet** (popen/quiet, n=30): Q1 median 0.5805 s / max 2.05 s / >=0.5 s 18; Q2 median 0.6905 s / max 1.721 s / >=0.5 s 24
- **popen-cpu8** (popen/cpu, n=25): Q1 median 1.287 s / max 2.486 s / >=0.5 s 25; Q2 median 1.351 s / max 2.303 s / >=0.5 s 25
- **popen-cpu12** (popen/cpu, n=20): Q1 median 0.8225 s / max 1.696 s / >=0.5 s 20; Q2 median 0.9075 s / max 2.083 s / >=0.5 s 20
- **startproc-quiet** (startproc/quiet, n=8): Q1 median 0.541 s / max 1.415 s / >=0.5 s 8; Q2 median 0.954 s / max 1.164 s / >=0.5 s 8
- **startproc-cpu8** (startproc/cpu, n=8): Q1 median 0.8495 s / max 2.109 s / >=0.5 s 8; Q2 median 1.13 s / max 1.762 s / >=0.5 s 8
- **wrapper/quiet**: wrapper median 4.721 s (budget 15 s, over 0); wait-for-child_started median 8.48 s (budget 15 s, over 0); wait-for-exit median 19.379 s (budget 20 s, over 4, upper-bound timing)
- **wrapper/cpu8**: wrapper median 9.687000000000001 s (budget 15 s, over 0); wait-for-child_started median 15.0245 s (budget 15 s, over 6); wait-for-exit median 21.3935 s (budget 20 s, over 2, upper-bound timing)

## 3. Node-level outcome bands (M-B)

| band | node | condition | runs | failed | rate | Wilson95 | rungs |
|---|---|---|---|---|---|---|---|
| child-quiet | child_without_runtime | quiet | 18 | 17 | 0.9444 | [0.7424, 0.9901] | passedx1, rung1x2, rung2x15 |
| child-cpu8 | child_without_runtime | cpu | 18 | 18 | 1.0 | [0.8241, 1.0] | rung2x12, rung3x2, rung4x4 |
| child-spawn | child_without_runtime | spawn | 9 | 9 | 1.0 | [0.7008, 1.0] | rung2x7, rung3x2 |
| logon-quiet | logon_wrapper_quoted | quiet | 8 | 0 | 0.0 | [0.0, 0.3244] | passedx8 |
| logon-cpu8 | logon_wrapper_quoted | cpu | 8 | 0 | 0.0 | [0.0, 0.3244] | passedx8 |

Per tree (byte-identical T0/T0b is the identity control):

- **child-quiet**: T0 6/6, T0b 6/6, T4 5/6
- **child-cpu8**: T0 6/6, T0b 6/6, T4 6/6
- **child-spawn**: T0 3/3, T0b 3/3, T4 3/3
- **logon-quiet**: T0 0/4, T4 0/4
- **logon-cpu8**: T0 0/4, T4 0/4

## 4. Per-run load probe x outcome (drift-robust)

| quartile | runs | cpu_loop median (ms) | failed | rate |
|---|---|---|---|---|
| q1 | 12 | 59.9 | 11 | 0.9167 |
| q2 | 11 | 81.4 | 11 | 1.0 |
| q3 | 11 | 142.6 | 11 | 1.0 |
| q4 | 11 | 192.1 | 11 | 1.0 |

## 5. Concurrent activity (addendum B2)

- 70 samples, window ['2026-09-21T21:44:58', '2026-09-21T22:24:37']
- other sessions' **pytest campaigns** (samples present):
  - x54 `C:\Miniconda\python.exe -X utf8 -B -m pytest -p no:cacheprovider --basetemp C:\Users\郑曾波\Projects\revenue-fore`
  - x51 `C:\Miniconda\python.exe -m pytest -q --tb=short tests/test_zr803_chaos_recovery.py tests/test_zr1103_journey_r`
  - x34 `C:\Miniconda\python.exe -X utf8 -B -m pytest -p no:cacheprovider -q --no-header -rA C:\Users\郑曾波\Projects\reve`
  - x6 `C:\Miniconda\python.exe -m pytest -q --timeout=180 tests/test_zr901_pr_fanout.py tests/test_compatibility_mani`
  - x4 `C:\Miniconda\python.exe -m company_wiki.source_catalog.cli --config C:\Users\郑曾波\AppData\Local\Temp\pytest-of-`
- top CPU-delta process names (times in the top 3): chrome-headless-shellx142, chromex38, nodex14, Taskmgrx6, pythonx4

## 6. Hypothesis verdicts (criteria frozen in oracle.md before the runs)

- **H1**: ceiling: both arms are saturated (>=90% failures), so this contrast cannot separate the arms; load-dependence is carried by the measured window (M-A) and by the frozen-band cross-era comparison instead
- **H2**: supported (byte-identical T0/T0b behave the same; see also the structural argument in binding.json)
- **H3**: dominant mechanism supported: 17/18 failed runs show the session_start_timeout watchdog kill; the rest are launcher-level startup-latency timeouts (no child cycle completed) - same resource, different rung, and no run shows the artifact-absence path signature
- **H4**: supported: the measured lifetime distribution straddles 0.5 s
- **H5**: no jitter band observed end-to-end under the measured conditions

## 7. Not achieved / not self-signed

- The card's exit criterion (tests no longer randomly red/green under load) is **not achieved**: it needs a test-side change, and this attempt's boundary is production-read-only (proposal in `after/proposed-test-side-change.md`).
- The 'quiet' arm means 'this attempt added no load', not an idle machine: other sessions' pytest campaigns and a persistent chrome-headless-shell load were present (see section 5 and oracle-addendum-A/B).
- Node 2 passed 16/16 end-to-end, while the direct window probe missed the 15 s events budget in 6/8 loaded samples; both are reported side by side, not merged.

