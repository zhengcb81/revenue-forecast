# Findings

## F-01 baseline architecture map (2026-10-11)
- `contracts/period_flow.py` pure rules: `fiscal_year_window`, `period_flow_months`
  (3/6/12 only), `validate_period_flow_fields(pid, param, fye)` — no schema arg yet.
- `contracts/document.py:validate_parameters` gates `period_flow` to
  `schema_version == PERIOD_EVIDENCE_SCHEMA_VERSION ("3.9")`; semantic conflict key
  extends with (time_basis, start, end) only on 3.9.
- `contracts/annual_consumption.py:validate_annual_consumption` runs only on 3.9;
  annual roles need the flow to exactly equal the FY window.
- `schema_compatibility.py` SCHEMA_EMIT_ENGINES lists ENGINE_VERSION (=4.2.1) in
  emit sets — after bump, 4.2.1 must be pinned explicitly or history is lost.
- Output side is mostly version-agnostic via `BOUND_INPUT_SCHEMA_VERSIONS` +
  `requires_bound_input_schema`; adding "3.10" there reuses bound-input/output
  recomputation (`revenue_report._validate_forecast_output`,
  `validate_published_forecast`, `revenue_backtest.validate_snapshot`).
- `research/drivers.py` role-aware triangulation gated on `== "3.9"` (needs family).
- `revenue_report.render_markdown` already prints `period_flow` window generically.
- Test fixtures: `test_data_contract.apply_parameter_contract/finalize_contract`,
  `test_recognition_bridge.forecast_document`; flow fixture helper lives in
  `tests/test_m3_period_flow_contract.py::add_flow_parameter`.
- Version pins that must change with the engine bump (strings only, listed per
  card): SKILL_VERSION/ENGINE_VERSION 4.2.1 -> 4.3.0 assertions in
  test_m3_period_flow_contract.py (2 places) and test_m3_schema_compatibility.py
  (1 place); no math/semantic assertions relaxed.

## F-02 real counterexample (sealed input)
- control-window-findings.json PROCESS-006: purchase date 2026-05-31, purchase-to-end
  revenue 1,291,902.08 CNY = 1.29190208 CNY million, window 2026-05-31..2026-06-30,
  wrongly filed as period_start=2026-01-01. G4 probe: 01-01..06-30 accepted,
  2026-05-31..2026-06-30 rejected by 3/6/12 rule -> real RED for 3.10.
- inputs.json: reported control equity 64.69% (must NOT multiply revenue by it),
  must-not-assume list recorded. Fixture amounts besides 1.29190208 synthetic.

## F-03 TDD outcome (2026-10-11)
- RED (business-level): native entry rejected every 3.10 document incl. the sealed
  window — "schema_version must be 3.7, 3.8 (opt-in) or 3.9 (period evidence opt-in)".
  One RED test hit the not-yet-existing `schema_version` kwarg (API-shape TypeError,
  not counted as business RED). Log: docs/handoffs/w05-rf-flow/logs/phaseA_red.txt.
- GREEN: centralized suites + new tests 120 passed (7.2s); 40-file regression batch
  448 passed / 4 skipped (75.7s). Version-string pins updated 4.2.1 -> 4.3.0 in
  test_data_contract/test_m3_period_flow_contract/test_m3_schema_compatibility/
  test_schema_compatibility; test_schema_compatibility's unknown-schema probe moved
  "3.10" -> "3.11" and its supported-set pin added "3.10" (schema vocabulary, not
  math/semantic relaxations).

## F-04 pre-existing diagnostics (not caused by this lane; ROOT triage)
- tests/test_mixed_aggregate_recognition.py::test_mixed_rejects_lagged_activity:
  KeyError 'carry_in_parameter_ids' at scripts/forecast/calc.py — reproduces
  unchanged at base 1b616622 (verified in the canonical repo).
- tests/test_contract_registry.py + tests/test_compatibility_manifest.py fail at
  collection: repo-root `compatibility/` directory absent at baseline (missing
  module imports) — pre-existing.
- mypy: 15 pre-existing errors in scripts/revenue_report.py, identical count at
  base; new/changed contract files clean.

## F-05 honest limit
- A self-consistent rewrite of an entire input plus its evidence references is not
  detectable by hashing alone; the identity/tamper guards prove chain integrity
  only. Documented in references/dated-contribution.md and the CHANGELOG entry.
