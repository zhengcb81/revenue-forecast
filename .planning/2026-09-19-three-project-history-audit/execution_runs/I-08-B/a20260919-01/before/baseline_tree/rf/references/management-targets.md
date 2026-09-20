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
- treatment: `modeled_scenario`, `scenario_boundary`, `independent_benchmark`, `sensitivity_only`, `unmodeled_data_gap`, or `out_of_horizon`;
- mapped scenario and parameter IDs when modeled.

Do not equate external revenue with segment total revenue, ARR/run-rate with annual recognized revenue, bookings with revenue, or gross transaction value with net commission revenue. Do not infer that “over the next five years” means cumulative: it can describe the time allowed to reach a fifth-year annualized target.

Resolve measurement basis using, in order: explicit management definition or Q&A; official transcript/presentation; official cross-language wording; management's disclosed current-to-target bridge or CAGR; then corroborating direct reporting. An isolated translated phrase is insufficient when the surrounding arithmetic implies another basis. Record conflicting evidence; use `ambiguous` if it cannot be reconciled.

For `cumulative_periods`, provide at least two ordered, contiguous fiscal years; attainment is the sum of those modeled annual revenues. `annual_period` and `run_rate_at_period_end` each use exactly one period but remain separately labeled. If primary wording and context do not resolve the basis, use `ambiguous`, leave periods empty, and set treatment to `unmodeled_data_gap`.

A period-end run-rate is not annual recognized revenue. A comparable run-rate target requires `comparison_basis="annual_recognized_revenue"`, `normalization_formula`, `normalization_parameter_ids`, and the existing `normalization_rationale`. Explain the intra-year trajectory, effective contract dates, service periods, variable fees and recognition where relevant. Preserve the original run-rate value, wording and `measurement_basis`; only the comparison amount is converted.

The restricted arithmetic formula uses `x0` for `raw_target_value` and `x1`, `x2`, etc. for the verified registered parameters in `normalization_parameter_ids` order. Include at least one evidence-backed conversion or timing input. The runtime requires the expression to syntactically reference `x0` and every listed input and recompute to `comparison_value`; a literal constant or an expression omitting an input fails. This is not a proof of algebraic dependence: cancellation such as `x0-x0+x1` must be rejected in economic review even though all names occur. Review that each input genuinely performs the claimed conversion. For example, `x0*x1*x2` can express a supported annual exposure factor and currency/scale conversion, but the identity and evidence for those factors must fit the actual contract. The syntax example does not supply default numerical assumptions.

If a supported conversion is unavailable, use `unmodeled_data_gap`, `comparison_value=null`, and no mapped parameters or scenarios; a genuine perimeter mismatch remains explicitly recorded as such. Do not fabricate a normalization to satisfy the material-target gate. Recomputable arithmetic is stronger than a narrative assertion of comparability, but does not itself prove the economic validity of the conversion.

## Independent judgment before target attainment

First build an independent operating forecast and an external reference-class check. Then compare it with management's target. A goal, aspiration or capacity plan does not acquire a probability merely by being disclosed. Record management's historical delivery, changed scope, execution prerequisites and contrary evidence where available; distinguish these from the target's exact-value claim.

Use `independent_benchmark` for a material, comparable in-horizon target that should be evaluated without forcing any scenario to achieve it. This treatment requires:

- non-empty `mapped_parameter_ids` used by the forecast;
- `mapped_scenarios` containing exactly `low`, `base`, and `high`;
- a non-empty `benchmark_rationale` explaining the independent assumptions, their difference from the target and why forced attainment is inappropriate;
- `benchmark_claim_ids` with checked `rationale_support` claims bound to the same `management_target` / `target_id`; the original exact-value target claim remains mandatory.

The engine reports each scenario's comparison and `meets_target`, including `false`, without requiring attainment for this treatment. This is a documented disagreement or benchmark, not permission to omit a target or its evidence. Use `modeled_scenario` or `scenario_boundary` when deliberately testing the operating conditions that meet the target; those treatments retain the numerical attainment gate.

When independent comparisons exist, the output includes the optional count `targets_independent_benchmarks`; they are not counted as `targets_unmodeled`. The extra count is absent when there are no independent benchmarks, preserving the existing count shape for those forecasts.

## Hard behavior

- Communication target IDs and ledger target IDs must match exactly.
- A material, comparable target inside the forecast horizon must receive scenario treatment or a fully evidenced `independent_benchmark` comparison; `sensitivity_only` cannot silently bypass this gate.
- A target using `modeled_scenario` or `scenario_boundary` must numerically meet `at_least`, `at_most`, or `approximately` within the disclosed tolerance. An `independent_benchmark` compares all three scenarios and may remain unmet.
- The comparison must be recomputed using the declared measurement basis and every declared model period; output records the per-period values as well as the aggregate.
- A metric-perimeter mismatch cannot be modeled directly.
- An out-of-horizon or otherwise unmodeled target is copied into `data_gaps` and confidence limitations.
- Consider extending the horizon when evidence supports an explicit path. A target within ten years does not by itself justify a longer forecast. Use `out_of_horizon` with a reason when extrapolation would add unsupported precision.

## Downstream boundary

Revenue-forecast owns target discovery, reconciliation and scenario mapping. Financials, valuation and SOTP consume the frozen revenue lineage. They may disclose whether the selected scenario covers a target, but must never reconstruct a second target-driven revenue path.
