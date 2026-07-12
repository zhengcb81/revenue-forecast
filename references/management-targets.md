# Management communication and target coverage

Use this gate to reduce omission risk. It cannot prove that the internet contains no undiscovered statement; it forces a reproducible official-source search and makes every found target visible.

## Required communication categories

Provide exactly one record for each:

- `latest_annual_filing`;
- `latest_results_release`;
- `latest_earnings_call`;
- `latest_investor_presentation`;
- `latest_strategy_communication`;
- `material_announcements_since_last_filing`.

Use `checked`, `not_available`, or `not_applicable`. A checked record requires opened source IDs and lists every material revenue target found. `not_available` requires the search performed and why no primary artifact could be opened. Search snippets are never evidence.

## Target ledger

For every material or contextually relevant revenue statement record:

- exact statement, source-linked claim, target period and commitment strength (`guidance`, `goal`, `aspiration`, or `capacity_plan`);
- raw value, currency, scale and unit exactly as communicated;
- metric definition and company/segment/custom scope;
- whether its perimeter is `matched`, `reconciled`, or `mismatch` versus recognized revenue;
- normalized comparison value in the model currency/unit and the normalization rationale when comparable;
- treatment: `modeled_scenario`, `scenario_boundary`, `sensitivity_only`, `unmodeled_data_gap`, or `out_of_horizon`;
- mapped scenario and parameter IDs when modeled.

Do not equate external revenue with segment total revenue, ARR/run-rate with annual recognized revenue, bookings with revenue, gross transaction value with net commission revenue, or a five-year goal with next-year guidance.

## Hard behavior

- Communication target IDs and ledger target IDs must match exactly.
- A material, comparable target inside the forecast horizon must enter a scenario.
- A mapped scenario must numerically meet `at_least`, `at_most`, or `approximately` within the disclosed tolerance.
- A metric-perimeter mismatch cannot be modeled directly.
- An out-of-horizon or otherwise unmodeled target is copied into `data_gaps` and confidence limitations.
- Prefer extending the horizon for material targets within ten years. Use `out_of_horizon` only when a longer explicit path would create more false precision than insight.

## Downstream boundary

Revenue-forecast owns target discovery, reconciliation and scenario mapping. Financials, valuation and SOTP consume the frozen revenue lineage. They may disclose whether the selected scenario covers a target, but must never reconstruct a second target-driven revenue path.
