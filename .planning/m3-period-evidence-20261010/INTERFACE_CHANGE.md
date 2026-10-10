# INTERFACE_CHANGE — M3-FLOW / W07 (period flow + mechanism evidence roles)

Lane: M3-FLOW. Repo: revenue-forecast. Base: `0c248d9a07a2dd7a2c756946d88507479d5e9d15`.
Scope: frozen root causes R19/R20 (W07). All changes stay inside the M3-FLOW write
set declared in `phase6/m3_parallel_handoff_2026-10-10/INTERFACES.md`.

## 1. New/changed contract surface

### Schema 3.9 (opt-in) — `PERIOD_EVIDENCE_SCHEMA_VERSION`

| surface | change |
|---|---|
| `scripts/contracts/constants.py` | `SKILL_VERSION` 4.1.1 → **4.2.0**; added `PERIOD_EVIDENCE_SCHEMA_VERSION="3.9"`, `PERIOD_FLOW_TIME_BASIS="period_flow"`, `PERIOD_FLOW_MONTH_LENGTHS={3,6,12}`, `MECHANISM_EVIDENCE_ROLES={"mechanism_direction"}`; `SUPPORTED_FORECAST_SCHEMA_VERSIONS` now includes 3.9. `TIME_BASES` **unchanged** `{annual, point_in_time}` (legacy meaning preserved; guard test `test_input_construction_consistency` keeps passing). |
| `scripts/contracts/period_flow.py` (new) | pure validators: `fiscal_year_window(fye, year)`, `period_flow_months(start, end)`, `validate_period_flow_fields(pid, parameter, fye)` — strict ISO dates, start<end, containment in the FY window resolved from `fiscal_year_end` (cross-calendar + non-calendar FYE supported, Feb-29 FYE anchors Feb-28), 3/6/12 whole months (±0.2-month tolerance), unknown stays unknown (both endpoints required). |
| `scripts/contracts/document.py` | `validate_top_level` accepts 3.9 (same message shape plus the new option); claim capture-eligibility tuple includes 3.9; `validate_parameters` gates: `period_flow` accepted only on 3.9 (3.7/3.8 fail closed), `period_start`/`period_end` rejected on any non-`period_flow` parameter **in every schema**; flow params validated via `validate_period_flow_fields`. |
| `scripts/research/drivers.py` | `_validate_growth_driver_evidence(..., role_aware=)` — on 3.9 only, triangulation counts nodes with ≥1 `mechanism_direction` claim (still ≥2 types + ≥2 sources); history/financing/value/conversion/recognition/peer/unroled rows stay disclosed with an explicit limitation note; mixed nodes keep valid mechanism supports + all contrary rows. 3.7/3.8 keep the legacy peer-only exclusion. Confidence untouched (never reads role category). |
| `scripts/schema_compatibility.py` | emit matrix: 3.7/3.8 → `{4.1.0, 4.1.1, ENGINE_VERSION}` (4.1.1 history frozen across the engine bump); **new row** 3.9 → `{ENGINE_VERSION}` = `{4.2.0}` (4.1.x fails closed in every read mode). Provenance comment updated. |
| `scripts/generate_input_template.py` | `build_template(..., schema_version=None)` + CLI `--schema {3.7,3.8,3.9}`; 3.8 skeleton carries `operating_units: []`; 3.9 skeleton carries a `_comment` recipe for period flows/roles. Default output unchanged (3.7, `time_basis=annual`). |
| `references/input-construction.md` | new sections “Dated period flows (schema 3.9 opt-in)” and “Mechanism evidence roles (schema 3.9 opt-in)”; the guarded quick-reference bullet list untouched. |
| `references/m3-period-evidence.md` (new) | full contract note: version matrix, pure rules, role rule, authoring, real-18-flow mapping table. |
| tests | new `tests/test_m3_period_flow_contract.py`, `tests/test_m3_evidence_roles.py`, `tests/test_m3_schema_compatibility.py`; extended `tests/test_growth_driver_tree.py` with the 3.9 role-aware negative case (legacy tests untouched). |

### New DTO shapes (input side, schema 3.9 only)

```json
{
  "schema_version": "3.9",
  "parameters": [{
    "parameter_id": "games_h1_2025",
    "time_basis": "period_flow",
    "period_start": "2025-01-01",
    "period_end": "2025-06-30",
    "...": "all existing parameter fields unchanged"
  }]
}
```

Unknown semantics: a flow whose start/end cannot be evidenced must NOT be
typed `period_flow` (no fabrication path exists); missing endpoints fail
closed. Output DTOs are unchanged in shape — 3.9 results carry
`schema_version="3.9"`, `engine_version="4.2.0"` through the existing result
fields and the existing registry read/strong paths
(`revenue_report.require_validating_engine` needs no code change).

## 2. MAIN integration patch (version-release wiring only)

`MAIN_INTEGRATION_PATCH.patch` (same directory) — 4 files, applies clean on
base + this branch, trial-verified: with it applied, all 9 baseline-diff
regressions pass (59 tests green in `test_schema_compatibility.py`,
`test_data_contract.py`, `test_rf_release_checklist.py::c3`,
`test_rf_coverage_report.py`):

1. `tests/test_schema_compatibility.py` — pins `ENGINE_VERSION=="4.2.0"`,
   formal-mode matrix updated, `3.9` unknown-schema negative becomes `3.10`
   plus a new `3.9`-on-4.1.1 fail-closed negative, supported-set includes 3.9.
2. `tests/test_data_contract.py` — release pin `SKILL_VERSION=="4.2.0"`.
3. `CHANGELOG.md` — new versioned section `## 4.2.0 (2026-10-10)` (required by
   `tools/release_checklist._changelog_problem`, which demands a versioned
   heading, not an Unreleased entry).
4. `SKILL.md` — “Period evidence (4.2.0 / schema 3.9 opt-in)” paragraph.

Expected CI after MAIN applies the patch: exact CI green. Exact CI **on this
branch without the patch** is red solely on the 4 above (the rf_coverage
errors are downstream: its subprocess runs `test_schema_compatibility.py`);
that is the documented, card-sanctioned version-release wiring state.

## 3. Commands for MAIN at the big integration node

```bash
# after applying MAIN_INTEGRATION_PATCH.patch:
python -m pytest -q -p no:cacheprovider tests/test_m3_period_flow_contract.py \
  tests/test_m3_evidence_roles.py tests/test_m3_schema_compatibility.py \
  tests/test_growth_driver_tree.py tests/test_research_evidence_roles.py \
  tests/test_schema_compatibility.py tests/test_data_contract.py \
  tests/test_rf_release_checklist.py tests/test_rf_coverage_report.py
python tools/pre_push_gate.py        # full daily gate
python tools/release_checklist.py    # release readiness incl. CHANGELOG 4.2.0
```

## 4. Not changed (explicit)

`revenue_report.py`, `revenue_backtest.py`, `revenue_forecast.py`,
`revenue_core.py`, `revenue_publication.py`, `publication_registry.py`,
`lint_input.py`, `fix_hashes.py`, `filing_fetch_client.py`,
`filing_upstream_cause.py`, `source_preparation.py`, `SKILL.md`, `CHANGELOG.md`,
`tools/*`, `assurance/*`, `output/*`, installed skill directory, other repos.
Formula compute, sensitivity DAG, signed base adjustment, input tolerance,
opening residual and confidence math are behavior-locked by the 122-pass
compatibility batch plus the 3.7/3.8 economic-equivalence SHA control
(`restore_receipt.json`).
