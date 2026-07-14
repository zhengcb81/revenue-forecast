# Revenue forecast outputs

The CLI emits validated JSON and can render a Markdown report from the same result.

## Core JSON sections

- identity: company, information date, currency, unit, fiscal-year end, base year, forecast years, version;
- history: source-linked historical company revenue;
- research coverage: all nine dimensions, status, revenue mechanism, used parameter IDs, sources, and exclusions or gaps;
- management target coverage: six official-communication checks, complete target ledger, measurement basis and model periods, perimeter treatment, mapped scenarios, per-period modeled values and numerical attainment;
- growth-driver analysis: up to five positive drivers ranked by reconciled Base terminal segment-revenue increment, negative headwinds, complete causal/evidence nodes, parameter mapping, persistence, leading indicators, falsifiers, and attribution reconciliation;
- segments: model, formula, driver values, modeled activity, accounting `recognized_revenue`, constraint-adjusted `effective_revenue`, recognition metadata, carry-in, and unrecognized tail;
- revenue constraints: frozen definitions plus one audit row per constraint/scenario/year with parameter IDs, affected segments, before value, signed adjustment, after value, and before/after totals;
- consolidated forecast: low/base/high segment bridge, adjustment bridge, annual revenue, annual growth, terminal revenue, CAGR, and incremental contribution;
- optional probability-weighted forecast: annual expected revenue and expected-terminal-implied CAGR;
- sensitivities: parameter shocks and terminal revenue impact;
- optional theme analysis: explicit counterfactual, increment, elasticity, and terminal mix;
- confidence: score, rating, components, evidence coverage, concentration, and limitations;
- traceability: complete parameter trace, evidence-claim registry, source registry, input hash, result hash, schema, and engine version;
- workflow compliance: captured-source receipt hashes, checked-claim and assumption inventory, data-gap hash, prompt-injection flags, mandatory gate IDs, and formal-output authority;
- data gaps and disconfirming indicators.

## Output validation

`revenue_report.validate_forecast_output` independently recomputes:

- every segment formula from driver IDs and values;
- modeled-to-recognized revenue, including progress and lag;
- every cross-segment constraint and its complete audit, independently recomputed from recognized revenue and registered parameters;
- terminal revenue, annual growth, and CAGR;
- segment plus adjustment bridge for every scenario/year;
- incremental contribution;
- low/base/high ordering;
- effective segment low/base/high ordering after all constraints;
- probability-weighted annual revenue, terminal, implied CAGR, and increment;
- theme counterfactual arithmetic, sensitivity impacts, and confidence components;
- presence of source and parameter traces.
- nine-dimension completeness, counts, parameter/source identities, and propagation of research data gaps.
- official-communication completeness, target-ledger identity, cumulative/annual/run-rate measurement arithmetic, mapped-scenario attainment, and propagation of ambiguous or otherwise unmodeled targets.
- every growth-driver claim/source identity, Base-parameter mapping, segment attribution weight, evidence status, terminal increment, ranking, share, and reconciliation to segment contribution.
- every current-schema source capture and claim-to-capture snapshot binding, plus exact recomputation of the workflow compliance receipt.

It rejects fields for stock prices, valuation, profitability, cash generation, investment ratings, shareholder returns, and position sizing.

## Markdown sections

The standard renderer includes:

1. information boundary and base revenue;
2. low/base/high terminal revenue, CAGR, and increment;
3. a concise list of the main future revenue drivers and revenue headwinds;
4. historical revenue;
5. nine-dimension research coverage and model mapping;
6. management communication and revenue-target coverage;
7. annual scenario paths;
8. segment models and recognition;
9. base-case incremental contribution and the full causal growth-driver tree;
10. sensitivities;
11. confidence components;
12. disconfirming indicators and data gaps;
13. parameter-to-claim-to-source table;
14. linked source registry.

Generate both outputs with:

```powershell
python scripts/revenue_forecast.py input.json --output forecast.json --markdown forecast.md
```
