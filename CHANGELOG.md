# Changelog

This project follows Semantic Versioning. The runtime release source of truth is `SKILL_VERSION` in `scripts/revenue_core.py`; forecast schema versions are managed separately.

## Unreleased

## v3.10.0 — 2026-07-26

- Moved filing identity, reuse-first lookup, explicit download routing, exact-hash deduplication, canonical write, and immutable provenance into the revenue-forecast skill.
- Removed the runtime dependency on the external filing-fetch skill and on the company-wiki Python package/CLI. Company-wiki remains only a configurable data root.
- Added a versioned JSON configuration for the storage root, local security-master snapshots, skill-owned staging, and the CN StockInfoDLSimple plus HK/US dayu-agent CLI commands.
- Added isolated-copy, movable-root, authorization, identity, three-market routing, tamper, exact-dedup, and immutable-sidecar tests.
- Preserved forecast schema 3.4 and all deterministic revenue formulas.

## v3.9.0 — 2026-07-25

- Added `reserve_depletion` model to `model_registry.py` with stock-flow bridge validation (opening + additions - depletion = closing) and year-to-year continuity enforcement. Suitable for mining (ore reserves), pharma (drug pipeline), real estate (land bank), and manufacturing (capacity plan).
- Added `reserve_volume` parameter dimension to `revenue_core.py` for physical reserve quantities (tonnes, koz, MMboe, sqm).
- Added `sensitivities` as an alias for `sensitivity_tests` in the input schema, with auto-generation of `name` from `parameter_id` when omitted.
- Made research coverage validation flexible: nine core dimensions are still required, but additional custom dimensions (e.g., `reserves`, `processing`, `regulatory_permits`) are now accepted.
- Added `references/resource-business-guidance.md` with domain guidance for reserve-to-revenue businesses.
- Updated `references/model-library.md`, `references/input-schema.md`, `references/research-coverage.md`, and `SKILL.md` with new model documentation and routing.
- All 135 tests pass with backward compatibility preserved.

## v3.8.0 — 2026-07-22

- Extracted the on-demand filing fetch (identify → resolve/ensure, market routing, canonical write, reuse-first) into a standalone **filing-fetch** skill. `scripts/company_wiki_source.py` now keeps only the revenue-specific `build_revenue_source_record` that converts a filing-fetch handle into a schema-3.4 source/capture record.
- SKILL.md step 3 now instructs using the `filing-fetch` skill to obtain filings, then `build_revenue_source_record` to formalize them.
- Fixed `run_forecasts.py` hardcoded absolute skill path to `Path(__file__).resolve().parents[1]`.
- Preserved forecast formulas, schema 3.4, the read-only default, and explicit download authorization.

## v3.7.0 — 2026-07-19

- Added fail-closed `company_query` handling to the company-wiki host adapter: fuzzy names, brands, abbreviations, or tickers are identified first, and only one verified active security can construct the canonical source request.
- Preserved the configurable company-wiki root, read-only resolve default, explicit ensure authorization, existing downloader routing, forecast formulas, and schema 3.4.

## v3.6.0 — 2026-07-18

- Added a host-side company-wiki source adapter that resolves existing indexed filings before any download, delegates explicit missing-source acquisition to company-wiki, verifies canonical whole-file hashes, and builds the existing schema-3.4 capture contract without changing forecast formulas or output schemas.
- Added strict `config/company_wiki.json` root discovery so moving company-wiki requires a configuration edit rather than Python or caller changes; retained explicit root injection as a compatibility override.

## v3.5.0 — 2026-07-14

- Added forecast schema 3.4 source-capture receipts that bind claims to opened-source snapshot hashes, capture traces, explicit untrusted-data treatment, and prompt-injection disposition.
- Added a machine-recomputed workflow compliance receipt covering the input, evidence, research, target, driver, model, and output gates; formal output authority is renderer-only and free-form override is forbidden.
- Made the independent output validator revalidate capture receipts, claim-to-snapshot binding, and the workflow receipt even after a result is rehashed.
- Added an atomic, exact-manifest installation synchronizer for the Agents and Claude skill directories.
- Preserved immutable schema 3.0-3.3 validation and expanded the suite to 129 tests plus 85 model subtests.

## v3.4.0 — 2026-07-14

- Added schema 3.3 causal growth-driver trees with concise top-driver summaries, full evidence branches, persistence, leading indicators, falsifiers, and explicit counterevidence search status.
- Ranked drivers deterministically by Base terminal segment-revenue increment using analyst-declared segment weights that reconcile to one, while disclosing company-level forecast adjustments separately.
- Reused the existing parameter, evidence-claim, source, recognition, and segment-contribution contracts instead of introducing a parallel research or calculation system.
- Added independent output recomputation for driver evidence identities, Base-parameter mappings, attribution, impact, shares, ranking, and reconciliation.
- Preserved validation for immutable schema 3.0-3.2 outputs and expanded the suite to 123 tests across all 22 registered revenue models.

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
