---
name: revenue-forecast
description: Build auditable company revenue forecasts by segment from source-linked operating drivers, management targets, revenue-recognition timing, low/base/high scenarios, annual paths, CAGR, incremental revenue, sensitivity, confidence, immutable snapshots, and historical forecast errors. Use for revenue, sales growth, guidance or long-term revenue goals, segment growth, order or backlog conversion, capacity, subscribers, users, transaction activity, volume-price, market-share, or theme-driven revenue elasticity. Keep the scope strictly on revenue and hand non-revenue investment analysis to the relevant invest skill.
---

# Revenue Forecast

Forecast recognized revenue from explicit, source-traceable operating drivers. Treat a company as a portfolio of segment revenue curves rather than assigning one company-wide business-model label.

## Scope boundary

Produce historical revenue, segment revenue, recognized company revenue, annual growth, CAGR, incremental revenue, revenue mix, theme elasticity, scenario ranges, sensitivities, confidence, sources, and forecast errors.

Do not produce stock-price, valuation, profitability, cash-generation, investment-rating, expected-return, or position-sizing conclusions. Use the relevant `invest-*` skill if the user separately requests them.

## Versioning

Continue the legacy release line with Semantic Versioning. `SKILL_VERSION` in `scripts/revenue_core.py` is the runtime source of truth; `ENGINE_VERSION` remains a compatibility alias in serialized outputs. Keep the forecast input/output schema on its own version because schema compatibility can change independently from skill behavior. See [CHANGELOG.md](CHANGELOG.md) for release history.

Revenue model metadata and pure calculators are registered in `scripts/model_registry.py`. Add or change a model there; do not add formula dispatch branches to `revenue_core.py`.

## Resource routing

Read only what the task needs:

- Read [references/data-governance.md](references/data-governance.md) before collecting or accepting data.
- Read [references/research-coverage.md](references/research-coverage.md) before deciding which research conclusions enter the model.
- Read [references/management-targets.md](references/management-targets.md) before accepting that official communications and forward revenue targets are complete.
- Read [references/accounting-boundaries.md](references/accounting-boundaries.md) when contracts, projects, platforms, banks, or insurers require accounting judgment.
- Read [references/model-library.md](references/model-library.md) before assigning segment driver models.
- Read [references/input-schema.md](references/input-schema.md) when building a calculation input.
- Read [references/output-schema.md](references/output-schema.md) before delivering JSON or Markdown.
- Read [references/backtesting.md](references/backtesting.md) when freezing or evaluating forecasts.

Use these deterministic tools:

- `scripts/revenue_forecast.py`: validate input, calculate all segment scenarios, aggregate company revenue, validate output, and optionally render Markdown.
- `scripts/revenue_backtest.py`: create an immutable forecast snapshot or compare a snapshot with source-linked actual revenue.

## Required workflow

### 0. Complete the nine-dimension coverage gate

Review company foundation, growth curve, industry market, competition, capacity, technology, policy, customers, and demand. For each dimension, either map the conclusion to parameters actually used by the revenue model, register a material data gap, or explain why it is immaterial to the forecast horizon.

Use this gate to prevent omissions. Never add a research dimension directly to CAGR or confidence and never require nine separate narrative reports.

### 1. Freeze the information set

Record company identity, `as_of_date`, currency, unit, fiscal-year end, base year, forecast years, forecast version, and reported-revenue definition. Exclude every source published after `as_of_date`.

### 1A. Complete the management-communication and target gate

Open and record the latest annual filing, results release, earnings call, investor presentation, strategy communication, and material announcements since the last filing. Mark an unavailable or inapplicable category explicitly; never infer that silence means no target.

Register every material dated revenue target with its exact source wording, commitment strength, raw currency/unit, source period, measurement basis, explicit model periods, metric perimeter, normalized comparison value, and treatment. Distinguish a single-year amount, period-end run-rate, multi-period cumulative amount, and ambiguous wording. A comparable in-horizon target must enter at least one low/base/high scenario or the forecast fails. A perimeter mismatch, ambiguous measurement basis, or out-of-horizon target must remain a prominent data gap. Do not silently treat an aspiration as base-case guidance.

Determine measurement semantics from the complete evidence hierarchy: original management remarks and Q&A, official presentation or transcript, official cross-language wording, and explicit current-to-target arithmetic. Do not infer cumulative versus annual/run-rate from an isolated English preposition such as “over the next five years.” If sources conflict, preserve the conflict and use `ambiguous` until reconciled.

### 2. Verify history and the base

Collect at least two historical company-revenue observations unless the company is explicitly pre-revenue. Link every observation to primary evidence. Reconcile:

```text
reported company revenue
= segment external revenue
+ signed base adjustments
```

Stop numerical forecasting if the base year, unit, fiscal period, or reconciliation cannot be verified.

### 3. Register sources and parameters

Register sources once. For every cited fact or rationale, create a parameter-level evidence claim with exact target, locator, checked excerpt, hashes, verifier/date, and extracted value/unit/period when applicable. Register every input by `parameter_id` and classify it as:

- `reported_fact`;
- `derived_fact`;
- `management_guidance`;
- `analyst_assumption`;
- `scenario_stress`.

Use strict `FYyyyy` periods and machine-readable dimension, time basis, currency, and scale. Open every cited page before creating its claim. URL-format validation and claim structure do not independently understand a live webpage.

### 4. Split the company into revenue curves

Create one segment for each economically distinct revenue stream. A company may combine product, subscription, platform, service, project, licensing, or other models. Use exact model and driver names from `model-library.md`.

Use `direct_growth` or `direct_revenue` only as transparent fallbacks. Their use lowers forecast confidence because they do not explain operating causality.

### 5. Define recognized revenue

For every segment, document:

- point-in-time or over-time recognition;
- shipment, acceptance, milestone, usage, delivery, or progress trigger;
- gross or net presentation;
- accounting-policy claim;
- progress measure and progress parameters for over-time recognition;
- lag and carry-in revenue where modeled activity precedes recognition.

Do not equate orders, bookings, backlog, TAM, reserves, pipeline value, shipments, billings, or receipts with recognized revenue.

### 6. Build driver scenarios

Construct low, base, and high cases from parameter-level drivers. Require the same model for a segment across scenarios. Give every assumption a rationale and do not insert unsupported precision.

Do not create scenario probabilities by default. If probabilities are used, document their calibration rationale and source IDs.

### 7. Aggregate and bridge

Calculate recognized segment revenue before company revenue. When segments share a hard ceiling, depend on another segment, or contain measured internal revenue, apply explicit `revenue_constraints` after recognition and before aggregation. Preserve both `recognized_revenue` and constrained `effective_revenue`, plus a deterministic before/adjustment/after audit. Never use a constraint as an unexplained growth plug.

Add signed company-level adjustments for acquisitions, disposals, foreign exchange, reclassifications, and items that genuinely belong only at company scope. Do not duplicate an elimination already applied to segment effective revenue. Reconcile every forecast year.

Calculate company CAGR only from aggregated base and terminal company revenue. Never average segment or scenario CAGRs.

### 8. Test sensitivities and theme increments

Shock each base parameter at most once and rerun the model. Choose percent, percentage-point/bp, absolute, range, or discrete shocks according to driver semantics; disclose requested/effective values and clamping. For theme analysis, use explicit terminal-year revenue counterfactual assumptions.

### 9. Assess confidence

Use revenue-weighted verified-claim quality/coverage, freshness, explicit-model coverage, immutable historical backtests, and sensitivity coverage. Keep base reconciliation, recognition, scenarios, and research completeness as pass/fail gates rather than constant score components. Never use growth magnitude.

### 10. Validate and deliver

Run:

```powershell
python scripts/revenue_forecast.py input.json --output forecast.json --markdown forecast.md
```

The command must fail if any critical source, parameter, period, scenario, bridge, CAGR, or output-boundary check fails.

Deliver:

1. base revenue and information date;
2. low/base/high annual revenue and CAGR;
3. segment contribution to incremental revenue;
4. operating-driver trace;
5. recognition assumptions;
6. sensitivities and confidence limitations;
7. official-communication coverage and management-target attainment;
8. parameter-level source table.

### 11. Freeze and backtest

Create an immutable snapshot before actual results are known:

```powershell
python scripts/revenue_backtest.py create input.json --version 2026-07-12-v1 --output snapshot.json
```

Evaluate later without modifying the snapshot:

```powershell
python scripts/revenue_backtest.py evaluate snapshot.json actuals.json --output backtest.json
```

Track absolute error, MAE, signed error, APE, sMAPE, base-scaled error, WAPE, direction accuracy, interval coverage, and CAGR error by company, segment, and horizon. Reuse only hash-linked accuracy records generated by backtesting.

## Hard failure gates

Block output when any of these is true:

- a fact or management guidance lacks a source;
- a source is a placeholder, search-results page, malformed URL, or published after `as_of_date`;
- a citation was not opened and checked against the parameter;
- an evidence claim target, excerpt hash, extracted value, unit, period, or information date does not match;
- any of the nine research dimensions is missing, maps to an unused parameter, or lacks the required gap/immaterial rationale;
- any required official communication category is neither checked nor explicitly unavailable/inapplicable;
- a material revenue target found in official communications is absent from the target ledger;
- an in-horizon comparable material target does not enter a scenario, or its mapped scenario does not numerically satisfy the target;
- a target's external/internal, segment, currency, unit, period, gross/net, recurring/run-rate, or recognized-revenue perimeter is unresolved but modeled as if matched;
- cumulative, annual, and run-rate target language is not explicitly classified, or an ambiguous measurement basis is modeled directly;
- historical base revenue does not equal reported base revenue;
- segment base revenue plus adjustments does not reconcile to reported revenue;
- a driver has the wrong period, scenario, unit, range, or parameter identity;
- a derived formula cannot be safely recomputed to its stored value;
- project backlog or delivery orders fail base opening, stock-flow, or annual continuity;
- revenue-recognition metadata is incomplete;
- low/base/high paths cross;
- a revenue constraint has an unknown type, segment, parameter, period, scenario, dimension, allocation, sign, or extra field;
- fixed constraint weights do not cover every segment and sum to one in every scenario/year;
- a constraint makes segment effective revenue negative, its audit cannot be recomputed, or effective low/base/high paths cross;
- probabilities do not sum to one or lack an evidence rationale;
- company CAGR, bridge, or incremental contribution cannot be recomputed;
- output contains a non-revenue investment field;
- a historical snapshot fingerprint does not match its frozen input.
