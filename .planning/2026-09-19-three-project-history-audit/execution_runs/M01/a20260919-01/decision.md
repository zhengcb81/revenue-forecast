# M01 · decision record — not NA

Card step D is `[professional_decision_required]`, so this file is **required** and is not marked NA.
It is intentionally **not duplicated** here:

- The full record is `evidence/M01/accounting_decision.md`, containing four decisions
  (DEC-M01-1 which revenue line anchors `base_revenue`, DEC-M01-2 whether one disclosed rate may be reused
  as a constant CAGR, DEC-M01-3 unidentifiable parameters, DEC-M01-4 special review) and three
  special-review flags (SR-M01-A/B/C).
- Steps E/F are **not implemented**: E belongs to I-10-A (only a labelled historical mapping probe is
  delivered, see `evidence/M01/historical_mapping_probe.json`), and F requires the I-12 frozen design,
  which does not exist.

Key judgement calls the reviewer must attack first:

1. **The single-rate path is already falsified for this issuer over one closed year.** Handing the model the
   issuer's own printed rate (14.96%) predicts CNY 349,064,494,744.53 for FY2025 versus the disclosed
   CNY 349,079,082,852 — a residual of +CNY 14,588,108.91 (0.0042%). The model cannot decompose that
   residual, and the *exact* ratio of the two disclosed figures is 14.9648%, so the issuer's 2-decimal
   rounding alone explains most of it. Either way the model expresses no economics.
2. **A constant CAGR is contradicted by two consecutive disclosed periods**: FY2024 = +3.49%, FY2025 = +14.96%.
3. **Base anchor choice**: the FY2024 comparative in the FY2025 report is identical to the FY2024 report's own
   FY2024 figure, so no restatement bridge is needed — the reviewer should confirm this themselves.
4. The `growth_rate` driver is unidentifiable with respect to volume, price, equity production, intercompany
   elimination, M&A, FX and inventory; no mapping may imply otherwise.

**Status of every decision in the record: PROPOSED, NOT APPROVED.**
