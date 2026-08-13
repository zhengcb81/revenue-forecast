# Phase 13 — Independent Review Report (r1)

> Reviewer identities: `reviewer-fc1301-independent` … `reviewer-fc1304-independent` (one per FC).
> Reviewed 2026-08-13T03:15:36Z. All reproduction in clean worktrees under
> `C:/Users/郑曾波/Projects/.fcap-review/fc-130x/` (F-6 rule: zero `git checkout <rev> -- <paths>`
> in main checkouts; all mutations via reverse edits; main checkouts untouched).
> Triplets (git rev-parse in worktrees): base `4a4c108` / `83c638e` / `b93994a`,
> result `a9f1ff1` / `83c638e` (unchanged) / `304966d`.

## Verdicts

| FC | Verdict | Reviewer receipt sha256 |
|----|---------|-------------------------|
| FC-1301 (reason taxonomy 1.1) | **ACCEPTED** | `2064d37a302578579be85bc18dd9f3db37800084dc613ac21fe9dd8dbbf80812` |
| FC-1302 (increment scan-health) | **ACCEPTED** | `a42e91429b116e750eae5a1f03675ec58e0c85705f136e56e80f2b5ae177e7f3` |
| FC-1303 (production SLO probe) | **ACCEPTED** | `43b472fc1b70c8a318c6f67f1905b03211e88072978b77aefbe8fae61ab85b70` |
| FC-1304 (capacity/concurrency verification) | **ACCEPTED** | `78b3e5ff85af70e26134a3aaa0924f733a587af569d65dd08323b827c8b39aa1` |

All four implementer receipts pass the strict `receipt_validator --accept` gate after the
reviewer corrected their stale `result_triplet` (finding F1 per FC, below).

## Key numbers (reviewer-measured)

- **FC-1301**: registry `1.0/28` at base → `1.1/78` at result (+50 additive, grouped).
  RED at base: 2 failed (version + 50 unregistered codes, exactly the 28-vs-50 drift claimed).
  GREEN at result: 3 passed (0.91s). M1 kill: injected `reason="unregistered_drift_code"`
  emission → gate died naming exactly `['unregistered_drift_code']`; reverted, re-green.
- **FC-1302**: RED at base: 3 failed (base runner exits 0 in all three scenarios). GREEN at
  result: 3 passed; regression `test_fc1102_t2_runner.py` + `test_fc1105_fault_injection.py`
  = 9 passed → 12 total, matching the implementer's combined claim. M2 kill: removing the
  `new_errors` problems.append block → `test_new_errors_in_24h_fail` fails; reverted, re-green.
  Production T2 run (mode=ro, query_only, temp report root, run-id `reviewer-fc1302`): **exit 0**,
  `new_errors_24h=0`, `recurring_unchanged_runs_24h=34` (implementer: 33 — the ambient worker
  advanced one recurring run between the two measurements, which is the exact recurring-error
  scenario the increment semantics exist for), `interrupted=16`, `completed_with_errors=243`
  (informational), policy freshness matches, manifest triplet commits all present.
- **FC-1303**: RED at base: `ModuleNotFoundError: slo_probe` (tool missing). GREEN: 3 passed.
  M3 kill: `exact_p95` 5.0→50.0 → frozen-budget test fails (`50.0 != 5.0`); reverted, re-green.
  Production run (`--samples 3`, production config + catalog): **exit 0**, exact p95 0.453s,
  latest p95 0.438s, bundle p95 0.453s (budget 5s), peak RSS 0.021GB = 21MB (budget 2GB),
  `breaches=[]`. No INSERT/UPDATE/DELETE/CREATE TABLE in the tool (grep + contract test).
- **FC-1304**: drills re-run at the current wiki tip — `test_capacity_concurrency.py` +
  `test_disaster_drill_fc405.py` **11 passed**; `test_close_gap_concurrency_fc804.py` +
  `test_source_catalog_operation_lock.py` **14 passed** → 25 total, matching the receipt.
  Capacity snapshot re-measured: production `catalog.sqlite3` = 49,623,977,984 bytes ≈ 46.2 GiB
  (receipt's `du -sh` 47G is block-usage; consistent), unchanged by the review (read-only).

## Findings

Common to all four FCs — **F1 (info, fixed)**: the implementer receipts' `result_triplet` was
generated pre-commit (`Phase-13/_write_receipts.py` captures `heads()` before the sealing
commit) and therefore equaled the base triplet. The reviewer updated it to the actual tips
`a9f1ff1` / `304966d`; the discrepancy is recorded for the audit trail.

- **FC-1302-F2 (info)**: the T2 24h window filter compares `started_at >= <T-format ISO>`
  lexicographically. Production writes T-format timestamps (`scanner._utc_now` isoformat), so
  the boundary is correct live; a space-format timestamp from the boundary day would compare
  out of the window (`' ' < 'T'`). No action needed while scanner remains the only writer.
- **FC-1302-F3 (info)**: commit `a9f1ff1` also carries `assurance/fc/Phase-13/_write_receipts.py`
  (receipt-generation helper) which no receipt lists in allowed/changed files. Docs-area
  tooling, no production impact.
- **FC-1303-F2 (warn)**: `slo_probe._resolve()` ignores its `request` parameter —
  `EXACT_PROBE`/`LATEST_PROBE` are decorative and every sample runs the identical exact-mode
  CLI call (no `--mode latest_as_of`, which the wiki resolve CLI supports at `cli.py:415`).
  The report's `latest` row measures the exact path a second time and is mislabeled: the
  latest-as-of SLO is not actually measured. Nothing is fabricated and the frozen budgets
  still guard real resolve latency. Disposition: wire `--mode latest_as_of` for the latest
  samples (or relabel) in a follow-up before the baseline is treated as covering latest-as-of.
- **FC-1303-F3 (info)**: peak RSS measures the probe process's own peak working set (21MB),
  not the resolver subprocess that opens the 47G catalog — the 2GB RSS budget is nearly
  vacuous. Honest (None fallback) but the RSS SLO is effectively unmonitored. Disposition:
  measure the spawned resolve subprocess in a follow-up.

## Methodology / hygiene

- Worktrees: `revenue-base` @ 4a4c108, `revenue-forecast` @ a9f1ff1 (canonical name for the
  sibling-layout contract), `wiki-base` @ b93994a, `wiki-result` @ 304966d, `filing-fetch`
  @ 83c638e, plus a transient junction `company-wiki -> wiki-result` removed at cleanup.
- RED-at-base performed by copying the new test files onto base worktrees and deleting them
  afterwards (base worktrees clean); mutations performed as reverse edits on result worktrees
  and reverted (all worktrees clean at close).
- Production verification was strictly read-only: T2 runner opens the catalog `mode=ro` with
  `PRAGMA query_only=ON`; the SLO probe only spawns the read-only resolve CLI and writes its
  isolated report; the catalog file mtime was unchanged by the review runs.
- Diff audit exact: wiki `b93994a..304966d` = one commit, two files (observability.py + audit
  test). revenue `4a4c108..a9f1ff1` = one commit; production code is only `daily_t2_runner.py`
  (+54/-6) plus the two new test files; the remainder is docs (4 receipts, WU card, helper).
  No extra production changes anywhere.
