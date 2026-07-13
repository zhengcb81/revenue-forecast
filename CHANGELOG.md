# Changelog

This project follows Semantic Versioning. The runtime release source of truth is `SKILL_VERSION` in `scripts/revenue_core.py`; forecast schema versions are managed separately.

## v3.3.0 — 2026-07-13

- Replaced the central formula dispatcher with an immutable, validated model registry while preserving all 22 model IDs and compatibility exports.
- Added deterministic `sum_cap`, `linked_ratio`, and `elimination` cross-segment constraints owned by revenue-forecast.
- Preserved accounting `recognized_revenue` and added audited `effective_revenue` for company aggregation and downstream segment adapters.
- Added independent output recomputation for constraint definitions, audit rows, effective paths, and ordering.
- Expanded the revenue suite from 101 to 112 tests, including registry immutability, strict constraint schema, invalid weights/signs/segments, audit mutation, and heterogeneous downstream integration fixtures.

## v3.2.1 — 2026-07-12

- Corrected target-semantic research guidance: “over the next five years” must not be classified as cumulative without checking management Q&A, official cross-language wording, and current-to-target arithmetic.
- Preserved validation for immutable schema-3.2/engine-3.2.0 outputs while emitting engine 3.2.1 for new forecasts.

## v3.2.0 — 2026-07-12

- Added forecast schema 3.2 with explicit management-target measurement semantics: annual period, period-end run-rate, cumulative periods, or ambiguous.
- Cumulative targets now sum every declared contiguous fiscal period and disclose the per-period modeled values; annual and run-rate targets remain visibly distinct.
- Ambiguous target language cannot be scenario-mapped and must propagate as an unmodeled data gap.
- Preserved immutable output validation for schema 3.0/engine 3.0.0 and schema 3.1/engine 3.1.0 artifacts.

## v3.1.0 — 2026-07-12

- Added forecast schema 3.1 with six-category official management-communication coverage and a source-linked forward revenue-target ledger.
- Added hard gates for target completeness, metric-perimeter reconciliation, in-horizon scenario mapping, and numerical target attainment.
- Added target coverage to JSON, Markdown, data gaps, confidence quality gates, immutable output validation, and adversarial tests.
- Preserved validation of immutable schema-3.0/engine-3.0.0 forecast outputs and snapshots while requiring schema 3.1 for new inputs.

## v3.0.0 — 2026-07-12

- Rebuilt the skill as a revenue-only, segment-driver forecasting system.
- Added parameter-level evidence claims, strict periods and dimensions, deterministic derived formulas, revenue-recognition bridges, low/base/high paths, sensitivity, confidence, immutable snapshots, and backtesting.
- Expanded the model library to 22 revenue archetypes and the deterministic suite to 89 tests.
- Replaced the legacy package layout and introduced forecast schema 3.0 and snapshot schema 2.0.
- Breaking change: legacy v2.x inputs and reports require migration to the new contracts.

## v2.6.1 — 2026-06-13

- Last release of the legacy framework before the v3 rebuild.
