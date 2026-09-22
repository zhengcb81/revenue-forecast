# M11 · infrastructure — accounting / disclosure decisions (PROPOSED, UNPROPOSED REVIEW)

Status of every item below: **proposed by the implementer session, unsigned, not reviewed**.
None of them may be read as an accepted accounting decision, and none of them changes the product.

Scope note: the model is `infrastructure` - utilities, pipelines and toll/chargeable transport after start of operation. Unit rule: actual billable activity volume x U per same activity unit.

- **DEC-M11-1** - Is the tariff a regulated all-in price, or does it exclude capacity charges and subsidies?
  - PROPOSED: one regulatory regime per segment; each of capacity fee and subsidy is either inside `tariff` or inside `other_revenue`, never both.
  - Risk if unanswered: Double counting raises revenue with no runtime error.
- **DEC-M11-2** - How is a tiered tariff with a mid-year effective date collapsed?
  - PROPOSED: a volume-weighted effective tariff for the year, with the conversion formula and the effective date recorded per driver row; the model has no tier structure.
  - Risk if unanswered: Using the year-end tariff for the whole year misstates a regulated step change.
- **DEC-M11-3** - Is the disclosed throughput the billable volume?
  - PROPOSED: no automatic pass-through. Only the billable volume enters `billable_volume`; unbilled throughput must be excluded and the exclusion recorded.
  - Risk if unanswered: Passing throughput straight into the driver inflates revenue.

## Disclosure items that must be collected before D can be claimed

card L37: billable volume, tiered tariffs, regulatory effective dates, taxes, capacity charges, subsidies, recognition timing

## Business-level negatives that must be adjudicated (not runtime gates)

- throughput is not automatically fully billable
- subsidies and capacity charges must not be added twice

## What is deliberately NOT decided here

- No gross-versus-net, tax, ownership or consolidation-scope ruling is made; the mapping skeleton lists
  those as required fields with no value.
- No fiscal-period or restatement mapping is asserted.
- No scenario or accuracy statement is made from this model.
