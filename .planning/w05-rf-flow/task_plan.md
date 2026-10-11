# W05-RF-FLOW task plan (schema 3.10 dated contribution)

Worktree: `C:/Users/郑曾波/Projects/_harness_worktrees/w05/rf-flow` (branch `codex/w05-rf-flow`, base `1b616622`).

Goal: additive **schema 3.10 / engine 4.3.0** letting any real inclusive finite
window (start <= end) carry a dated consolidated-revenue contribution
(acquisition post-control flow, short non-12-31-FY flows), end-to-end:
input -> validate -> formula DAG -> forecast -> report -> output/snapshot readers.

## Nodes
- [x] Read construction card, handoff inputs, contracts, tests.
- [x] A: TDD design + real RED tests (new `tests/test_w05_dated_contribution*.py`).
- [x] B: implement 3.10 (constants, period_flow schema family, document,
      annual_consumption, schema_compatibility registry, engine 4.3.0,
      drivers role-aware family, template wiring, report identity guard, docs).
- [x] B: unit/integration coverage list from card section B items 1-7.
- [x] C: isolated CLI E2E (prepare/validate/forecast/report + reader + tamper
      rejection; acquisition-contribution and non-12-31-FY short-flow cases).
- [x] C: scratch cleanup, handoff JSON/MD/manifest, normal commit.

## Fixed interface decisions (ROOT)
- Reuse `time_basis="period_flow"`, `period_start`, `period_end`; no new short-term params.
- 3.10: any finite inclusive ISO window, start<=end, inside the FY window of the
  `period` label from `fiscal_year_end`. Cross-FY amounts must be split by real
  source / explicit estimate — never date-clipped while keeping the whole amount.
- 3.9 keeps start<end + 3/6/12 whole months. 3.7/3.8 reject new fields. Old pure
  helpers default to 3.9 semantics; new callers pass schema explicitly.
- Amounts belong only to the written window: no implicit x2/x12/day-annualization.
  Control date != contribution window != publication date; source dates need the
  original source_id/locator; unknown stays unknown.
- point_in_time stays a stock. Estimates use analyst_assumption/scenario_stress.
- Annual consumers reuse period_flow/annual_consumption rules; partial contribution
  may compose a full year only through explicit full-window derived composition;
  pre-acquisition out-of-scope != missing data (never default 0).
- Overlapping observations (H1 + Q2) may coexist, but same-basis annual summation
  components must not double count; same entity/basis/window conflicts keep the
  fact-conflict check. Rehashing must not let forged results pass.
- Registry keeps the 4.2.1 emit history after the engine bump (explicit "4.2.1"
  strings, not just ENGINE_VERSION alias).
