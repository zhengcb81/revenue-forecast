# M09 · resource — accounting / disclosure decisions (PROPOSED, UNPROPOSED REVIEW)

Status of every item below: **proposed by the implementer session, unsigned, not reviewed**.
None of them may be read as an accepted accounting decision, and none of them changes the product.

Scope note: the model is `resource` - mining / energy / agricultural commodities from start of production to decline. Unit rule: sold settleable quantity x U per same quantity unit; never mix ore tonnes, concentrate tonnes and metal tonnes.

- **DEC-M09-1** - Which quantity enters `saleable_volume` when the disclosure gives both produced and sold volumes, and whether the payable/recovery factor belongs inside the volume driver or on the price.
  - PROPOSED: the driver is the already-payable settleable quantity (card L8 wording `sold settleable quantity`); recovery/payability/TC-RC are applied exactly once, before the driver, and the conversion is recorded in `conversion_formula`.
  - Risk if unanswered: If the factor is applied twice the revenue is understated without any runtime error.
- **DEC-M09-2** - Unit homogeneity across ore / concentrate / metal tonnes.
  - PROPOSED: one unit family per segment; a segment that changes unit family must be split. The runtime contract cannot detect this, so it is a professional gate, not a test.
  - Risk if unanswered: The model has no unit field, so this is not run-time testable (oracle.md R7).
- **DEC-M09-3** - Whether by-product revenue may sit in `other_revenue`.
  - PROPOSED: only when it is not already inside `realized_price` x volume; the mapping must state which by-products are inside the price.
  - Risk if unanswered: Double counting by-products inflates revenue without any error.

## Disclosure items that must be collected before D can be claimed

card L37: production / sales / inventory, grade, recovery and payability factors, TC/RC units, settlement price, FX, by-products

## Business-level negatives that must be adjudicated (not runtime gates)

- recovery / payability / treatment-charge may be deducted exactly once
- production volume is not sales volume
- ore tonnes, concentrate tonnes and metal tonnes must not be mixed

## What is deliberately NOT decided here

- No gross-versus-net, tax, ownership or consolidation-scope ruling is made; the mapping skeleton lists
  those as required fields with no value.
- No fiscal-period or restatement mapping is asserted.
- No scenario or accuracy statement is made from this model.
