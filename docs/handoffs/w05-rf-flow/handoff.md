# W05-RF-FLOW handoff — schema 3.10 dated consolidated contributions (engine 4.3.0)

Status: **COMPLETE** (lane-local). Branch `codex/w05-rf-flow`, base
`1b616622`, verified-work commit `7b22bca8d6aa87f643780100832daec2836ed558`.
This is an unmerged lane: ROOT integration into main is not claimed done.

## Root cause (sealed evidence)

The 3.9 `period_flow` contract only admits 3/6/12 whole calendar months, so a
real acquisition post-control contribution — purchase date 2026-05-31,
purchase-to-end revenue 1,291,902.08 CNY (= 1.29190208 CNY million) over
2026-05-31..2026-06-30 (PROCESS-006, PDF p176) — had to be written as
2026-01-01..2026-06-30 and still could not honestly claim H1 or full-year
coverage. The G4 probe showed the native entry accepts 01-01..06-30 yet rejects
the true 05-31..06-30 window.

## What was actually implemented

Additive **schema 3.10 / engine 4.3.0** (default schema stays 3.7):

- `contracts/period_flow.py`: `validate_period_flow_fields(..., schema_version=`
  (default `"3.9"`, so old pure-helper calls keep their meaning) — 3.10 admits
  `period_start <= period_end` (same-day flows included), any real length, still
  inside the fiscal-year window; cross-FY amounts must be split, never
  date-clipped. New `validate_windowed_composition` keeps derived dated amounts
  honest: inputs inside the composed window, overlapping components disclosed
  via `rationale` (口径解释), full-year claims complete or explicitly explained —
  an out-of-scope pre-control gap is never silently zero-filled.
- `contracts/document.py` / `annual_consumption.py`: 3.10 accepted; the dated
  basis, window-semantic conflict key and the single annual-consumption rule now
  follow the 3.9/3.10 family. Partial flows still cannot be annual bases; they
  compose through explicit derived bridges (`x0+x1`).
- `schema_compatibility.py`: 3.10 emitted only by 4.3.0; **4.2.1 pinned as
  literal versions** so the bump cannot erase the emit history; 3.10 added to
  the bound-input set (output/snapshot recomputation reused, not duplicated).
- `revenue_report.py`: bound-input identity guard (company, as-of, currency,
  unit, fiscal calendar, base year, forecast years, schema) — a rehashed output
  with rewritten dates/currency/scope now fails; reports already render real
  window dates/amounts/sources and never relabel a partial window as annual.
- `research/drivers.py`: role-aware mechanism triangulation keyed on the
  3.9/3.10 family (history/financing/peer rows cannot fake a mechanism on 3.10;
  3.7/3.8 legacy semantics untouched).
- `generate_input_template.py`: `--schema 3.10` skeleton comment; old templates
  unchanged. Docs: CHANGELOG 4.3.0 entry, SKILL.md capability paragraph,
  references/input-schema|input-construction|output-schema.md updates and new
  references/dated-contribution.md.

Per-file necessity is recorded in `handoff.json.changed_files`; no unrelated
refactoring was done.

## Old vs new behavior

| shape | before | after |
|---|---|---|
| window 2026-05-31..2026-06-30 on 3.9 | rejected ("month") | still rejected on 3.9; valid on 3.10 |
| same-day / 10-day windows | impossible | valid on 3.10 inside the FY |
| partial flow as annual base | rejected | still rejected; compose explicitly |
| FY sum with gap / overlap | silently accepted | needs explicit rationale (口径解释) |
| output currency/date tamper + rehash | could pass | rejected vs frozen bound input |
| 4.2.1 validating 3.7/3.8/3.9 | valid | still valid (history pinned) |
| 4.2.x emitting 3.10 | n/a | fail-closed |

## TDD

- RED first (`logs/phaseA_red.txt`, 41 failed / 12 passed): the native entry
  rejects every 3.10 document including the sealed window
  ("schema_version must be 3.7, 3.8 (opt-in) or 3.9 …"). One failing case is the
  not-yet-existing `schema_version` kwarg (API-shape TypeError) and is not
  claimed as business RED.
- GREEN (`logs/phaseB_final_consolidated.txt`, 120 passed + 33 subtests, 7.2s):
  centralized suites `test_m3_period_flow_*`, `test_m3_schema_compatibility`,
  `test_schema_compatibility` plus the three new `tests/test_w05_dated_contribution_*`
  files. Version-string pins 4.2.1 -> 4.3.0 (4 files) and schema-vocabulary pins
  (unknown-schema probe 3.10 -> 3.11, supported-set + "3.10") were updated with
  the reason listed; no math/semantic assertion was relaxed.
- INTEGRATION (`logs/phaseB_regression_all.txt`, 448 passed / 4 skipped / 102
  subtests, 75.7s): 40 consumer/report/pipeline/model suites. Skips are
  pre-existing gates (golden lock requires the 4.1.0 runtime).
- E2E (`logs/phaseC_*`): native CLI confirmed via real `--help`; scratch run of
  prepare/validate/forecast/report + published output reader + snapshot reader
  for both required cases (acquisition contribution; FYE 06-30 short flows with
  10-day window and exact partition sum 7+10+3=20). Rehashed window/currency
  tampers rejected in both cases and in the snapshot.

## Interfaces

10 public seams recorded in `handoff.json.interfaces` (period-flow validator
signature + schema family, composition helper, schema vocabulary, document /
annual-consumption gating, emit registry, identity guard, role-aware gating,
revenue_core exports/ENGINE_VERSION, template wiring).

## Installation list (ROOT-owned sync, not applied here)

Files an installation must pick up via `tools/sync_installations.py`:
`CHANGELOG.md`, `SKILL.md`, `references/` (dated-contribution.md new;
input-schema/input-construction/output-schema updated), `scripts/contracts/
{constants,period_flow,document,annual_consumption}.py`,
`scripts/{schema_compatibility,revenue_core,revenue_report,generate_input_template}.py`,
`scripts/research/drivers.py`. Tests and `docs/handoffs/`, `.planning/` are repo
records, not installable package content.

## Temporary-space handling

Scratch root `C:/Users/郑曾波/AppData/Local/Temp/w05-rf-flow-e2e-20261011` was
freshly created (initial manifest: ABSENT) and fully deleted afterwards (final
manifest: RESTORED). Peak ~500 KiB; retained lane evidence ~720 KiB (small
inputs/outputs/logs under `docs/handoffs/w05-rf-flow/`, hashes in `manifest.json`).
The 87 source keys / 12 sealed reviews / old real runs / canonical assurance and
output were not touched; registry writes went to the scratch registry via
`REVENUE_PUBLICATION_REGISTRY`.

## Honest limits

- Fixture amounts are clearly synthetic except the sealed 1,291,902.08 CNY
  figure and its dates; this lane does not claim a buyer-grade economic PASS —
  the real-company economic end-to-end remains with ROOT at G4/G5.
- A self-consistent rewrite of an entire input plus its evidence references is
  not verifiable by hashing alone; the guards prove chain integrity, not source
  truth (see references/dated-contribution.md).

## Remaining (ROOT)

- Merge `codex/w05-rf-flow` into main; run the fast gate + installation sync.
- Pre-existing diagnostics outside this lane's writable set (see
  `findings.md` F-04 / handoff findings DIAG-01..03):
  `test_mixed_rejects_lagged_activity` KeyError (reproduces at base),
  `test_contract_registry`/`test_compatibility_manifest` collection failure
  (missing `compatibility/` at baseline), 15 pre-existing mypy errors in
  `revenue_report.py`.
