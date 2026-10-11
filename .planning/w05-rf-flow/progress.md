# Progress

- 2026-10-11: read construction card + input manifest/evidence; mapped period_flow
  3.9 seams (contracts/document.py, annual_consumption.py, schema_compatibility.py,
  research/drivers.py, revenue_report.py, generate_input_template.py, revenue_backtest.py).
  Planning files created.
- Phase A (TDD/RED): design.md written; tests/test_w05_dated_contribution_{contract,
  composition,output}.py fail with real business RED (native entry rejects schema
  3.10 windows: "schema_version must be 3.7, 3.8 (opt-in) or 3.9 …"); log
  docs/handoffs/w05-rf-flow/logs/phaseA_red.txt (41 failed, 12 passed).
- Phase B (implement + tests): schema 3.10 / engine 4.3.0 landed —
  constants (DATED_CONTRIBUTION_SCHEMA_VERSION, schema families), period_flow
  (schema-aware validate + validate_windowed_composition), document (gating,
  semantic key, composition call), annual_consumption (family gate),
  schema_compatibility (3.10 row, literal 4.2.1 history pins), drivers (role-aware
  family), revenue_report (bound-input identity guard), revenue_core re-exports,
  generate_input_template 3.10 wiring; CHANGELOG/SKILL/references updated incl.
  new references/dated-contribution.md. Version-string/schema-vocabulary pins in
  old tests updated (reasons listed in handoff). Centralized suites + 39 new tests:
  120 passed; 40-file regression batch: 448 passed, 4 skipped. mypy clean on the
  new/changed contract files (15 pre-existing revenue_report errors unchanged).
- Phase C (CLI E2E + handoff): native CLI confirmed (`revenue_forecast.py --help`);
  scratch E2E (Temp/w05-rf-flow-e2e-20261011, restored after) — case1 acquisition
  contribution (sealed window 2026-05-31..2026-06-30 = 1.29190208 CNY million +
  synthetic H2, explicit derived FY bridge with scope rationale, acquisition_
  contribution DAG adjustment) and case2 FYE 06-30 short flows (10-day window +
  exact partition sum) through prepare/validate/forecast/report + published output
  reader + snapshot reader; rehashed window/currency tampers rejected; artifacts
  and logs retained under docs/handoffs/w05-rf-flow/. Handoff package delivered;
  two normal commits (work, then handoff record).
