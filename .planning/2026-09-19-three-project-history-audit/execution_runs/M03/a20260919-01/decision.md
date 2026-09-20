# M03 · decision record — not NA

Card step D is `[professional_decision_required]`, so this file is **required** and is not marked NA.
It is intentionally **not duplicated** here:

- The full record is `evidence/M03/accounting_decision.md`, containing six decisions
  (DEC-M03-1 confirmed sales volume vs production/shipment, DEC-M03-2 whether a derived unit price is
  admissible, DEC-M03-3 the three double-counting traps named by the card, DEC-M03-4 the 14.37% scope gap as
  a stop signal rather than a residual, DEC-M03-5 unidentifiable parameters, DEC-M03-6 special review) and
  four special-review flags (SR-M03-A/B/C/D).
- Steps E/F are **not implemented**: E belongs to I-10-A (only a labelled historical mapping probe is
  delivered, see `evidence/M03/historical_mapping_probe.json`), and F requires the I-12 frozen design.

Key judgement calls the reviewer must attack first:

1. `unit_revenue` is **derived** by dividing the mapped table's own revenue cell by its own volume cell;
   the resulting zero residual is therefore a constructive identity, not verification.
2. `units` must be the **confirmed sales volume** (`4,250,370`), not the production figure
   (`4,281,084`) that is printed in the same table.
3. The 14.37% gap against the automobile segment revenue line must be bridged with evidence and must
   **never** be booked into `other_revenue` to make the reconciliation pass.

**Status of every decision in the record: PROPOSED, NOT APPROVED.**
