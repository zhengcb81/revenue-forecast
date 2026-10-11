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

A derived `period_flow` parameter asserts `value = composition(inputs)` over
its own window. Without an explicit `rationale` (the existing disclosure field —
no new identity or approval contracts):

* windowed inputs must lie inside the composed window;
* windowed inputs must not overlap — overlapping summation components double
  count. The group total plus the acquired standalone over the same window is a
  cross-perimeter merge, not a sum; a residual work split (`core = group -
  acquired`, PROCESS-007) overlaps by construction and must say so;
* a full-year window must be covered exactly (an `annual` input already covers
  the whole year; `point_in_time` stocks never fill a flow gap). A partial
  contribution can never pose as a complete FY base, and the pre-control gap is
  **out of consolidation scope, not missing data** — never silently zero.

A non-empty `rationale` (口径解释) keeps every honest shape expressible and puts
the scope explanation into the artifact. Same entity/definition/window
contradictions keep the fact-conflict check (window identity is part of the
semantic key on 3.9/3.10).

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
