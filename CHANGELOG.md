# Changelog

This project follows Semantic Versioning. The runtime release source of truth is `SKILL_VERSION` in `scripts/revenue_core.py`; forecast schema versions are managed separately.

## v3.0.0 — 2026-07-12

- Rebuilt the skill as a revenue-only, segment-driver forecasting system.
- Added parameter-level evidence claims, strict periods and dimensions, deterministic derived formulas, revenue-recognition bridges, low/base/high paths, sensitivity, confidence, immutable snapshots, and backtesting.
- Expanded the model library to 22 revenue archetypes and the deterministic suite to 89 tests.
- Replaced the legacy package layout and introduced forecast schema 3.0 and snapshot schema 2.0.
- Breaking change: legacy v2.x inputs and reports require migration to the new contracts.

## v2.6.1 — 2026-06-13

- Last release of the legacy framework before the v3 rebuild.
