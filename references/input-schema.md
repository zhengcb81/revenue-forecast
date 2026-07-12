# Revenue forecast v3 input schema

## 1. Identity

Require `schema_version="3.2"`, company, `as_of_date`, currency, scale in `unit`, fiscal-year end, base year, consecutive forecast years, sources, evidence claims, parameters, history, segments, reported-total parameter ID, nine-dimension research coverage, management-communication coverage, and a management-target ledger.

Use `pre_revenue=true` only when reported and segment base revenue are zero. A genuinely pre-revenue company may use an empty history.

## 2. Evidence claims

Every claim requires:

```json
{
  "claim_id": "claim_units_2026_base",
  "source_id": "capacity_release",
  "target_type": "parameter",
  "target_id": "units_2026_base",
  "support_type": "rationale_support",
  "locator": "Commissioning table, row 4",
  "excerpt": "Short passage opened and checked by the research agent.",
  "excerpt_sha256": "<sha256 of trimmed excerpt>",
  "content_sha256": "<sha256 of retrieved source artifact>",
  "verification_status": "opened_and_checked",
  "verified_by": "research-agent-id",
  "verified_date": "2026-07-12"
}
```

`reported_fact` and `management_guidance` require an `exact_value` claim whose extracted value, unit, and period match the parameter. Source-linked assumptions require a linked rationale-support claim. Historical revenue, recognition policies, scenario probabilities, and actual revenue use their dedicated target types.

The deterministic validator proves mapping, identity, hash, date, and extracted-value consistency. It cannot understand a live webpage; the research agent must open the page before creating the claim.

## 3. Parameters

```json
{
  "parameter_id": "units_2026_base",
  "kind": "analyst_assumption",
  "value": 120.0,
  "unit": "thousand units",
  "period": "FY2026",
  "dimension": "quantity",
  "time_basis": "annual",
  "definition": "base-case deliverable units",
  "scenario": "base",
  "rationale": "Commissioned capacity and customer schedules support the assumption",
  "source_ids": ["capacity_release"],
  "claim_ids": ["claim_units_2026_base"]
}
```

Periods must match `FYyyyy` exactly. Accepted dimensions are `revenue`, `quantity`, `ratio`, `revenue_per_unit`, `activity`, `revenue_per_activity`, `monetary_balance`, `area`, `revenue_per_area`, `backlog`, and `coverage_units`. Monetary dimensions also require company-matching `currency` and `scale`. `time_basis` is `annual` or `point_in_time`.

For `derived_fact`, use `x0...xn` in a restricted arithmetic formula and list inputs in that order. The engine recomputes the formula and rejects a conflicting stored value.

## 4. History and base

Historical records require value, year, source IDs, and exact-value claim IDs. Years cannot exceed the base year and must be consecutive. Reported total, segment bases, signed base adjustments, and historical base revenue must reconcile.

## 5. Segments, scenarios, and recognition

Each segment contains the same model in low/base/high and one parameter-ID series per driver. Recognition requires timing, trigger, gross/net presentation, matching `modeled_presentation`, and recognition-policy claim IDs.

- Point-in-time `modeled_as_recognized`: modeled revenue is recognized directly.
- Point-in-time `lagged_activity`: supply `lag_years` and scenario carry-in parameter IDs.
- Over-time: supply `progress_measure` and low/base/high annual `progress_parameter_ids`; recognized revenue equals modeled revenue times progress.

`project_backlog` also requires `base_backlog_parameter_id`; `delivery_pipeline` requires `base_orders_parameter_id`. First forecast-year opening balances must match these base facts.

## 6. Adjustments

Forecast adjustments contain name, accepted category, and low/base/high annual revenue-parameter IDs. Eliminations and disposals are non-positive; acquisitions are non-negative.

## 7. Scenario probabilities

Probabilities are optional. When supplied, require low/base/high values summing to one, a rationale, and `probability_claim_ids` targeting `scenario_probability`.

## 8. Sensitivities

Each base-referenced assumption can appear once. Supported shocks:

- `percent`, `percentage_point`, `basis_point`, or `absolute` with positive `shock_value`;
- `range` or `discrete` with `down_value` and `up_value`.

The output records requested values, effective bounded values, and clamp flags. Use absolute/range shocks for zero-base parameters.

## 9. Theme and historical accuracy

Theme counterfactual IDs must be non-negative terminal-year revenue assumptions for low/base/high. Historical accuracy accepts only `historical_accuracy_records` emitted by backtesting; the engine verifies each record hash and imports WAPE automatically.

## 10. Management communication and targets

`management_communication_coverage` contains exactly the six categories defined in `management-targets.md`. Every record contains status, checked date, conclusion, source IDs and `material_revenue_target_ids`; unavailable/inapplicable records require a rationale.

`management_targets` contains the exact statement, raw target value/unit/currency/scale, source period label, materiality, commitment strength, scope, metric definition, perimeter status/notes, comparison direction, treatment, mapped parameter/scenario IDs, exact-value target claims, and rationale. Comparable targets also require a model-currency comparison value and normalization rationale.

Every target also requires `measurement_basis`, `measurement_periods`, and `measurement_rationale`:

- `annual_period` or `run_rate_at_period_end`: exactly one `FYyyyy` model period;
- `cumulative_periods`: at least two ordered, contiguous `FYyyyy` periods;
- `ambiguous`: no model periods, no comparison value or scenario mapping, and treatment `unmodeled_data_gap`.
