# M28 accounting / disclosure decisions (PROPOSED, unsigned)

These are `professional_decision_required` items (card step D). They are recorded as PROPOSED so the industry/accounting reviewer can rule on them; the implementer asserts no position and made no product change.

- DEC-M28-1: a year-end AUM must not be charged a full year of fees (card_M28.md L60) - PROPOSED, unsigned
- DEC-M28-2: the timing of market moves and performance-fee crystallisation needs evidence (card_M28.md L60) - PROPOSED, unsigned

## Disclosure items still missing

- AUM bridge
- gross inflows/outflows
- market/FX effect
- time weighting
- fee rate
- recognised performance fees
- anchor

## Entry-point / accounting boundary

- gross vs net, tax, ownership and consolidation scope: **unmapped** (no real disclosure was adapted in this attempt).
- base-period anchor for the forecast integration: `base_aum_parameter_id` -> `opening_aum` (dimension `monetary_balance`).
