# W05-RF-FLOW: Dated Consolidated Contributions (schema 3.10)

Engineering contract for the 3.10 opt-in schema: any real, evidenced window may
carry a dated revenue contribution — most importantly an acquisition
post-control flow whose control date falls mid-period. The sealed counterexample
(PROCESS-006) is a purchase date of 2026-05-31 with purchase-to-end revenue
1,291,902.08 CNY = 1.29190208 CNY million over 2026-05-31..2026-06-30: under 3.9
the author had to write it as 2026-01-01..2026-06-30 (H1-shaped), and the flow
still could not claim H1 or full-year coverage. 3.10 removes that coercion
without weakening any date, scope, amount or unit rule.

## Version matrix (from the registry, not assumed)

| schema | emitted by | window rule |
|---|---|---|
| 3.7 / 3.8 | 4.1.0, 4.1.1, 4.2.0, 4.2.1 | no dated fields (fail closed) |
| 3.9 | 4.2.0, 4.2.1 | `period_start < period_end`, 3/6/12 whole months |
| 3.10 | 4.3.0 | `period_start <= period_end`, any real finite window |

Engine 4.2.x never emitted 3.10 and fails closed on it in every read mode. The
4.2.1 emit history is pinned as literal versions in
`scripts/schema_compatibility.py`, so the 4.3.0 bump cannot erase it. Default
schema stays 3.7; the data version is not a permission flag and requires no
human sign-off.

## Window contract (`scripts/contracts/period_flow.py`)

`validate_period_flow_fields(parameter_id, parameter, fiscal_year_end,
schema_version="3.9")` — the old three-argument call keeps 3.9 semantics; new
callers pass the schema explicitly:

1. Both `period_start` and `period_end` are required, strict ISO days.
2. The window must lie inside the fiscal year of the `FYyyyy` `period` label
   resolved from `fiscal_year_end` (Feb-29 FYE anchors to Feb-28 in non-leap
   years). A cross-FY amount must be **split by its real source or an explicit
   estimate** into per-FY parameters — dates are never clipped to a fiscal
   window while the whole amount is kept.
3. 3.9 keeps `period_start < period_end` and the exact 3/6/12-calendar-month
   rule (or the exact fiscal-year span). 3.10 admits `period_start <=
   period_end` (same-day flows included) of any length.
4. Amounts belong only to the written window. Nothing multiplies by 2 or 12 or
   pro-rates by day count anywhere in the chain. `H1 + H2 = FY` holds only
   through an explicit derived formula.
5. `period_start`/`period_end` remain rejected on every non-`period_flow`
   parameter in every schema; `point_in_time` stocks stay stocks.

## Composition honesty (`validate_windowed_composition`, 3.10 only)

The same temporal rule checks derived `period_flow` and derived `annual`
wrappers with dated ancestors. Changing the outer time-basis or definition
cannot hide the period of the underlying amount:

* Actual nonzero formula operands must lie inside the composed window. An
  annual operand uses its actual FY window. `rationale` never exempts dates.
* Scalar/rate/price factors change amount, not time coverage. Unused or
  zero-weight operands never fill gaps. Date coverage follows the real formula.
* Positive overlapping additions of the same original flow or same source
  semantic definition are rejected even with explanation. Dated derived aliases
  preserve original leaf identity/definition, so renaming the output or an
  intermediate node does not make H1 plus its Q2 a valid sum.
* Different disclosed business scopes and a negative residual work split can
  overlap in dates; both still need an explicit existing `rationale`. A scope
  explanation is data, not authorization. Different labels do not erase a
  shared original leaf.
* A full-year claim needs exact coverage, or an explicit perimeter explanation
  (e.g. the pre-control interval is outside consolidation). Valid annual bridges
  carry their validated period/scope forward; no repeated review receipt exists.

Source identity/definition remains authored and evidenced by the source/input
layer. This validator cannot infer real subsidiary membership or the truth of
two independently rewritten reported facts from hashes or free text alone.
The company audit still reads those sources. Arbitrary nonlinear products of
two flow amounts are not a temporal sum; express the intended estimate/model
through the existing assumption/forecast fields. No new identity contracts,
permission flags, data lake copies or per-material approvals are introduced.


## Actual type ancestry, including annual-only aliases (ROOT P1 follow-up)

Schema 3.10 checks the actual formula, not just an output's `annual` label.
`validate_derived_flow_ancestry` is shared by derived revenue composition and
actual annual-flow consumer roots. It recursively preserves original units and
period meaning through aliases, ratios, multiplication and division:

* A money balance, point quantity, scalar or ratio cannot be renamed annual
  recognized revenue. An unused or zero-multiplied income input cannot justify
  adding an untyped literal amount. Stock and period money cannot simply be
  added, even when one amount is zero.
* `flow * (stock / flow)` is still stock; an intermediate `ratio` label does not
  erase the inverse period meaning. Conversely an actual annual turnover
  `flow / stock` may multiply a stock to form a period amount. A derived price
  `annual income / point customers` preserves annual ARPU; `money stock / point
  customers` remains a stock-per-unit value and cannot become annual ARPU.
* Point operating quantity times a raw annual per-unit price/ARPU is allowed when
  units match. Raw annual per-unit/activity/area prices can be transaction prices
  or annual operating rates; the formula's matched quantity and real source/native
  model establish the business interpretation. Derived prices keep their actual
  origin and cannot acquire a period simply by changing metadata.
* Price-role interpretation is consistent within the actual formula DAG.
  Multiplying/dividing by the same price, its alias/equivalent expression, or a
  like operating-period price ratio cannot change a stock into income. Like
  raw period prices of one existing dimension share a role; year/source ID or
  amount changes do not make a growth-price ratio into annual turnover. The
  equations are checked together, not by independently choosing spot/annual
  meaning at each occurrence. Real flow times transaction price, point quantity
  times annual ARPU, and income-derived turnover remain supported.
* If one generic expression genuinely needs both annual ARPU and transaction
  price of the same dimension, derive the ARPU from actual income/point quantity
  or use existing native model roles. Free-text labels cannot prove those two
  distinct roles. No new schema field or authorization is required.
* Existing native subscription, bank, asset-management and stock-flow models
  retain their explicit driver roles. Generic stock/flow additions should use
  those native bridges. Arbitrary dated stock-pricing expressions are not a dated
  sum of evidenced contribution amounts; model the contribution and its real
  interval explicitly. The date containment/coverage owner is unchanged.

This is mathematical precondition validation, with no new fields, flags, identity
registry, authorization or repeated human review. Schema 3.9 and earlier keep
their established behavior. It cannot establish economic truth of independently
authored source facts, or choose a real business scope from free text alone.

## Annual consumers, kinds, units

* Annual roles (company/segment annual base, base adjustments, forecast
  adjustments, recognition carry-in, constraints) reuse the single
  `annual_consumption` rule across the 3.9/3.10 family: only full-fiscal-year
  coverage qualifies; partial flows compose through explicit derived bridges
  (e.g. `cmp_fy2026 = cmp_post_2026 + cmp_h2_2026`).
* Estimates and stresses keep `analyst_assumption`/`scenario_stress` kinds;
  a dated `reported_fact` needs its exact-value claim with `source_id`/locator
  (the control date's evidence lives in that claim's locator). Unknown source
  dates stay unknown — `available_by` never becomes a publication date.
* Every monetary parameter matches the document `currency` and `unit` scale
  (CNY 亿 / USD million / USD billion are separate documents); conversions are
  recomputed, never assumed.
* Group scope changes enter the forecast DAG explicitly through
  `forecast_adjustments` category `acquisition_contribution` (non-negative) or
  `disposal_contribution` (non-positive), keeping the perimeter change named.

## Hand-checkable fixture formulas (synthetic except the sealed figure)

```
C1 acquisition contribution (FYE 12-31):
   cmp_post_2026  reported_fact       1.29190208  2026-05-31..2026-06-30   (sealed)
   cmp_h2_2026    analyst_assumption 40.0        2026-07-01..2026-12-31   (synthetic)
   cmp_fy2026     derived x0+x1      41.29190208 2026-01-01..2026-12-31
                  rationale: 2026-01-01..2026-05-30 out of perimeter (control 2026-05-31)

C2 non-12-31 fiscal year (FYE 06-30, FY2026 = 2025-07-01..2026-06-30):
   fy26_a 7.0  2025-07-01..2025-12-31
   fy26_b 10.0 2026-01-01..2026-05-31
   fy26_c 3.0  2026-06-01..2026-06-30
   fy2026 derived x0+x1+x2 = 20.0  2025-07-01..2026-06-30 (exact partition, no rationale)
```

## Output/report/snapshot boundaries

* Rendered parameter rows show `period_flow` with the real window dates,
  amount and sources; a partial contribution is never displayed as annual.
* Against a frozen bound input, output identity fields (company, as-of date,
  currency, unit, fiscal calendar, base year, forecast years, schema) must
  match exactly; a rehashed artifact with rewritten dates/currency/scope is
  rejected. This is integrity of the chain, not truth of the content: a
  self-consistent rewrite of the whole input and its evidence references is
  **not** detectable by hashing alone, and this layer never claims to replace
  reading the sources.

## Authoring

`generate_input_template.py --schema 3.10` emits the skeleton comment carrying
these rules; `references/input-construction.md` holds the author-facing
guidance. Tests: `tests/test_w05_dated_contribution_*.py`.
