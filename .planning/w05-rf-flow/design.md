# W05-RF-FLOW TDD design — schema 3.10 dated consolidated contribution

All fixture amounts below are **synthetic** except the sealed control-window fact
(P1); nothing here is a real reported company revenue beyond that sealed item.

## P1 sealed real counterexample (from input/inputs.json + control-window-findings.json)

- control date: 2026-05-31 (purchase date, PDF p176, source locator kept)
- contribution window: 2026-05-31..2026-06-30 (inclusive)
- amount: 1,291,902.08 CNY = **1.29190208 CNY million** (purchase-to-end revenue)
- reported control equity 64.69% must NOT multiply the revenue; window must not
  be widened to 2026-01-01..2026-06-30 and must not be called H1/full year.
- 3.9 rejects this window ("period_flow must cover 3, 6 or 12 whole calendar
  months"); 3.10 must accept it.

## Hand-checkable contribution formulas

### C1 acquisition contribution (control date 2026-05-31, FYE 12-31)

```
cmp_post_2026   reported_fact     1.29190208 CNY million  2026-05-31..2026-06-30  (P1 real dates+value)
cmp_h2_2026     analyst_assumption  40.0   CNY million   2026-07-01..2026-12-31  (synthetic estimate)
cmp_fy2026      derived_fact x0+x1 = 41.29190208          2026-01-01..2026-12-31
                rationale: pre-control window 2026-01-01..2026-05-30 is outside
                the group consolidation perimeter (control 2026-05-31) — an
                out-of-scope gap, never zero-filled missing data.
hand check: 1.29190208 + 40.0 = 41.29190208  (no x2/x12/day annualization anywhere)
```

Rules exercised: window honesty, scope explanation for the non-partitioned
full-year composition (口径解释), estimate kind, annual-role eligibility only
through the explicit derived bridge.

### C2 non-12-31 fiscal year short flows (FYE 06-30, FY2026 = 2025-07-01..2026-06-30)

```
fy26_a  reported_fact      7.0  2025-07-01..2025-12-31
fy26_b  reported_fact     10.0  2026-01-01..2026-05-31
fy26_c  reported_fact      3.0  2026-06-01..2026-06-30
fy2026  derived_fact x0+x1+x2 = 20.0  2025-07-01..2026-06-30  (exact partition, no rationale needed)
hand check: 7 + 10 + 3 = 20
```

10-day window (2026-06-01..2026-06-10) and same-day window
(2026-06-30..2026-06-30) validate as facts; they compose only through explicit
derived sums that are honest about coverage.

## Composition honesty rule (3.10 only; 3.9 unchanged)

For a `derived_fact` with `time_basis=period_flow` on schema 3.10:

1. every windowed (`period_flow`) input window must lie inside the derived
   result window (amounts belong to their windows);
2. windowed inputs must be pairwise non-overlapping — overlapping summation
   components double count — unless the derived parameter carries an explicit
   `rationale` (口径解释: e.g. cross-perimeter core + contribution overlap, or a
   disclosed residual work-split);
3. when the derived window is the full fiscal-year window, the windowed inputs
   (plus any annual-basis input, which already covers the full year) must cover
   it exactly; otherwise the full-year claim needs the same explicit rationale
   (missing full-year basis / unexplained gap never pass silently).

point_in_time stocks never fill a flow gap and never ride a period window.
Same entity/definition/window contradictions keep the fact-conflict check.

## Reject-set counterexamples (must stay rejected)

- reversed / non-ISO / missing endpoint / window outside the labeled FY
  (cross-FY amounts must be split by source or explicit estimate);
- 3.9 short windows (3/6/12 preserved), 3.7/3.8 period fields fail closed;
- partial flow consumed directly as annual base/adjustment (annual_consumption);
- stock/net-asset/customer-count as revenue;
- currency/scale mismatch (RMB亿 vs USD million/billion), output-side currency,
  date and scope tampering against a frozen bound input even after rehashing;
- overlapping same-window components merged without explanation (cross-entity
  mis-merge shape), unexplained full-year gaps.

## Version matrix

- schema 3.10 emitted only by engine 4.3.0; 4.2.x fail closed on 3.10.
- 4.2.1 stays a documented emitter for 3.7/3.8/3.9 (pinned explicitly in the
  registry so the ENGINE_VERSION bump cannot erase history).
- Default schema stays 3.7; data version is not a permission flag.

## Limit (honest)

A self-consistent rewrite of the whole input and its evidence references cannot
be detected by hashing alone; this layer never claims to replace source reading.
