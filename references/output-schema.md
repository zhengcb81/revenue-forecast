# Revenue forecast outputs

The CLI emits validated JSON and can render a Markdown report from the same result.

## Core JSON sections

- identity: company, information date, currency, unit, fiscal-year end, base year, forecast years, version;
- history: source-linked historical company revenue;
- research coverage: all nine dimensions, status, revenue mechanism, used parameter IDs, sources, and exclusions or gaps;
- segments: model, formula, driver values, modeled activity, recognized revenue, recognition metadata, carry-in, and unrecognized tail;
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
- terminal revenue, annual growth, and CAGR;
- segment plus adjustment bridge for every scenario/year;
- incremental contribution;
- low/base/high ordering;
- probability-weighted annual revenue, terminal, implied CAGR, and increment;
- theme counterfactual arithmetic, sensitivity impacts, and confidence components;
- presence of source and parameter traces.
- nine-dimension completeness, counts, parameter/source identities, and propagation of research data gaps.

It rejects fields for stock prices, valuation, profitability, cash generation, investment ratings, shareholder returns, and position sizing.

## Markdown sections

The standard renderer includes:

1. information boundary and base revenue;
2. low/base/high terminal revenue, CAGR, and increment;
3. historical revenue;
4. nine-dimension research coverage and model mapping;
5. annual scenario paths;
6. segment models and recognition;
7. base-case incremental contribution;
8. sensitivities;
9. confidence components;
10. disconfirming indicators and data gaps;
11. parameter-to-claim-to-source table;
12. linked source registry.

Generate both outputs with:

```powershell
python scripts/revenue_forecast.py input.json --output forecast.json --markdown forecast.md
```
