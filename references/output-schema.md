# Revenue forecast outputs

The CLI emits validated JSON and can render a Markdown report from the same result.

## Core JSON sections

- identity: company, information date, currency, unit, fiscal-year end, base year, forecast years, version;
- history: source-linked historical company revenue;
- research coverage: all nine dimensions, status, revenue mechanism, used parameter IDs, sources, and exclusions or gaps;
- management target coverage: six official-communication checks, complete target ledger, measurement basis and model periods, perimeter treatment, mapped scenarios, per-period modeled values and numerical attainment;
- segments: model, formula, driver values, modeled activity, accounting `recognized_revenue`, constraint-adjusted `effective_revenue`, recognition metadata, carry-in, and unrecognized tail;
- revenue constraints: frozen definitions plus one audit row per constraint/scenario/year with parameter IDs, affected segments, before value, signed adjustment, after value, and before/after totals;
- consolidated forecast: low/base/high segment bridge, adjustment bridge, annual revenue, annual growth, terminal revenue, CAGR, and incremental contribution;
- optional probability-weighted forecast: annual expected revenue and expected-terminal-implied CAGR;
- sensitivities: parameter shocks and terminal revenue impact;
- optional theme analysis: explicit counterfactual, increment, elasticity, and terminal mix;
- confidence: score, rating, components, evidence coverage, concentration, and limitations;
- traceability: complete parameter trace, evidence-claim registry, source registry, input hash, result hash, schema, and engine version;
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

It rejects fields for stock prices, valuation, profitability, cash generation, investment ratings, shareholder returns, and position sizing.

## Markdown sections

The standard renderer includes:

1. information boundary and base revenue;
2. low/base/high terminal revenue, CAGR, and increment;
3. historical revenue;
4. nine-dimension research coverage and model mapping;
5. management communication and revenue-target coverage;
6. annual scenario paths;
7. segment models and recognition;
8. base-case incremental contribution;
9. sensitivities;
10. confidence components;
11. disconfirming indicators and data gaps;
12. parameter-to-claim-to-source table;
13. linked source registry.

Generate both outputs with:

```powershell
python scripts/revenue_forecast.py input.json --output forecast.json --markdown forecast.md
```
