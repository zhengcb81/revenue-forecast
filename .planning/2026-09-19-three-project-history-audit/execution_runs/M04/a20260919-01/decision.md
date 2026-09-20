# M04 · decision record — not NA

Card step D is `[professional_decision_required]`, so this file is **required** and is not marked NA.
It is intentionally **not duplicated** here:

- The full record is `evidence/M04/accounting_decision.md`, containing six decisions
  (DEC-M04-1 **ACTIVE STOP**: the capacity denominator, DEC-M04-2 why `yield = 1` is a scope statement and
  not a filled disclosure, DEC-M04-3 commissioning time must not be counted twice, DEC-M04-4 production is
  not sales, DEC-M04-5 unidentifiable parameters, DEC-M04-6 special review) and four special-review flags
  (SR-M04-A/B/C/D).
- Steps E/F are **not implemented**: E belongs to I-10-A (only a labelled historical mapping probe is
  delivered, and it FAILED its frozen volume tolerance), and F requires the I-12 frozen design.

Key judgement calls the reviewer must attack first:

1. **The card is at `STOP_DISCLOSURE_ADAPTATION`.** SMIC discloses only a period-end monthly capacity
   (`94.8万片/月`), never a year-average available capacity. Annualising the period-end figure and applying
   the disclosed utilisation `85.6%` yields `9,737,856` good wafers against a disclosed shipment volume of
   `8,021,000` — a **21.4045% gap versus a 0.5% tolerance frozen before the run**. The model's documented
   input ("full-year gross capacity") therefore has no disclosed source for this issuer.
2. **`yield = 1` is the riskiest assumption in this card.** It is justified only because the disclosed
   utilisation ratio appears to be effective-output over available capacity. If the denominator is
   nameplate capacity, yield is *not* inside the ratio and the choice overstates output (SR-M04-A).
3. The gap mixes the wrong capacity basis with output-versus-sales; **no apportionment was attempted**
   because no inventory/wafer-stock bridge is disclosed.
4. The source PDF's sidecar is a 5-line stub with **no provider receipt and no URL**, so the document
   identity cannot be cross-checked against a publisher hash (SR-M04-B).

**Status of every decision in the record: PROPOSED, NOT APPROVED.**
