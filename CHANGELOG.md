# Changelog

This project follows Semantic Versioning. The runtime release source of truth is `SKILL_VERSION` in `scripts/revenue_core.py`; forecast schema versions are managed separately.

## Unreleased

- Bumped forecast schema to 3.6. Growth-driver attribution weights now accept
  `[-1, 1]` excluding zero: a negative root is a quantified revenue headwind and
  is reported in `growth_driver_analysis.headwinds[]` (with a negative Base
  terminal increment and zero positive-driver share) instead of being ranked
  among positive drivers. Segment weight sums still reconcile to 1.0 and driver
  increments still reconcile to the segment increment. Schema 3.5 becomes legacy
  read-only; existing positive-weight inputs remain valid unchanged.
  Implemented per `docs/proposals/headwind-driver-schema.md` (approved 方案 A,
  rule-10 full change flow); see `references/schema-migration-3.5-to-3.6.md`.
- Added input-construction helper tools to cut schema 3.5 build round-trips:
  `scripts/generate_input_template.py` emits a field-correct skeleton,
  `scripts/lint_input.py` is a collect-all static pre-flight (field shape,
  reference integrity, hash staleness, aggregate weights), and
  `scripts/fix_hashes.py` recomputes and syncs every input-side hash. All reuse
  the engine's `canonical_sha256` / `text_sha256` for byte-for-byte parity.
- Added `--validate-only --verbose` to `revenue_forecast.py`: `validate_document`
  gains an optional `Collector` (threaded through `require`) that reports every
  input violation in one pass instead of failing fast. The default path is
  unchanged; a `MultiValidationError` groups violations by gate.
- Bumped forecast schema to 3.5; schema 3.4 is now legacy read-only.
- Added a `publication_receipt` that certifies a forecast result has passed the
  self-contained output validator. The receipt binds the validated payload to the
  input, schema, engine and validator version; it is signed only after validation
  succeeds and never permits freeform override.
- Extracted `_build_forecast_draft` as the private computation layer; `run_forecast`
  now drafts, publishes (signs publication receipt, computes result hash), runs the
  output validator, and only returns if all gates pass. A failure in output
  validation raises before a caller ever sees a receipt.
- The execution receipt (`workflow_compliance_receipt`) no longer claims the
  `output_recomputation` gate, which belongs to the publication validator.
- Added `scripts/revenue_publication.py` with `build_publication_receipt` and
  `validate_publication_receipt`; both are deterministic and never re-run the
  revenue model.
- Hardened the output validator against rehash attacks: it now independently
  re-derives the scenario probability contract (sum to 1, non-negative, three
  keys), recomputes management-target `meets_target` from the comparison
  operator and tolerance, re-runs each sensitivity shock against the model, and
  scans the full output tree for structured investment fields (prohibited keys
  with non-string values) while still allowing investment vocabulary inside
  source excerpts.
- Relaxed the research-coverage output contract to accept custom dimensions
  appended after the nine core dimensions, with non-empty-string and uniqueness
  validation.
- Wired `validate_source_coverage` into `validate_document` so a source whose
  coverage horizon precedes a forecast year that references it is rejected.
  Source-linked assumptions/stresses now require a `rationale_support` claim;
  base-adjustment parameter IDs are checked for existence and uniqueness.
- Hardened snapshots and actuals: snapshots accept legacy engine versions for
  legacy schemas; actuals now require capture receipts and bind claim content
  hashes to source snapshots; segment backtesting uses `effective_revenue`.
- Unifying parameter coverage: recognition-progress parameters are now
  sensitivity-eligible, constraint parameters feed confidence weights, and an
  opt-in sensitivity-completeness gate enforces that every eligible base
  parameter is either tested or carries a structured exclusion.
- Moved the non-formal `run_forecasts.py` example to `examples/` so `scripts/`
  contains only formal entry points; the whole tree is now ruff-clean.

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

## Unreleased (Phase 17)

- Added opt-in heuristics to `scripts/lint_input.py`, both off by default so
  existing behavior is unchanged:
  - `--check-conclusion-facts`: warns when a `research_coverage` /
    `management_communication_coverage` conclusion contains a digit token with
    no claim-backed value (numeric-value matching against bound claim excerpts;
    years, ISO dates, FY-prefixed and date-context numbers, and identifier
    suffixes such as `Qwen3.6` / `SEC 6-K` are excluded).
  - `--check-sensitivity-propagation`: warns when a sensitivity shocks an
    absolute-level driver (usage_platform `eligible_activity` /
    `monetization_rate`, forecast adjustments, recognition progress) in a year
    before the terminal year — such a shock cannot propagate to the terminal
    year (A11 lesson).
- `references/backtesting.md`: added the "Snapshot version discipline" section —
  any input change requires a new version label; published snapshots must never
  be deleted or overwritten (already enforced by `write_new_json`, pinned by
  `test_backtest.py`).
- Added `docs/session-checklist.md` (pre-flight checklist for all forecast
  sessions), `docs/templates/trust-boundary.md` (5-section delivery template),
  `docs/proposals/headwind-driver-schema.md` (schema 3.6 proposal, **not
  implemented**), and `docs/proposals/segment-refinement-backlog.md` (A7/A8/A9
  backlog, no implementation commitment).
- `references/compliance-contract.md`: added the "Delivery narrative" section —
  every formal artifact must carry a trust-boundary statement; chat summaries
  must state the guarantee scope (structure/hash/recomputation provable;
  tool invocation/search exhaustiveness/source truthfulness host-trusted).
- No schema change in this phase; schema 3.6 remains a proposal only.
