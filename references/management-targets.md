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
- measurement basis: `annual_period`, `run_rate_at_period_end`, `cumulative_periods`, or `ambiguous`;
- explicit `measurement_periods` used by the model and a rationale for translating the source wording into those periods;
- metric definition and company/segment/custom scope;
- whether its perimeter is `matched`, `reconciled`, or `mismatch` versus recognized revenue;
- normalized comparison value in the model currency/unit and the normalization rationale when comparable;
- treatment: `modeled_scenario`, `scenario_boundary`, `sensitivity_only`, `unmodeled_data_gap`, or `out_of_horizon`;
- mapped scenario and parameter IDs when modeled.

Do not equate external revenue with segment total revenue, ARR/run-rate with annual recognized revenue, bookings with revenue, gross transaction value with net commission revenue, or “over five years” cumulative revenue with fifth-year annual revenue.

For `cumulative_periods`, provide at least two ordered, contiguous fiscal years; attainment is the sum of those modeled annual revenues. `annual_period` and `run_rate_at_period_end` each use exactly one period but remain separately labeled. If primary wording and context do not resolve the basis, use `ambiguous`, leave periods empty, and set treatment to `unmodeled_data_gap`.

## Hard behavior

- Communication target IDs and ledger target IDs must match exactly.
- A material, comparable target inside the forecast horizon must enter a scenario.
- A mapped scenario must numerically meet `at_least`, `at_most`, or `approximately` within the disclosed tolerance.
- The comparison must be recomputed using the declared measurement basis and every declared model period; output records the per-period values as well as the aggregate.
- A metric-perimeter mismatch cannot be modeled directly.
- An out-of-horizon or otherwise unmodeled target is copied into `data_gaps` and confidence limitations.
- Prefer extending the horizon for material targets within ten years. Use `out_of_horizon` only when a longer explicit path would create more false precision than insight.

## Downstream boundary

Revenue-forecast owns target discovery, reconciliation and scenario mapping. Financials, valuation and SOTP consume the frozen revenue lineage. They may disclose whether the selected scenario covers a target, but must never reconstruct a second target-driven revenue path.
