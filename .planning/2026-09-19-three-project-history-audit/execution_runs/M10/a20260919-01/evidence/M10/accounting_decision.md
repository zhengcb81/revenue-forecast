# M10 · reserve_depletion — accounting / disclosure decisions (PROPOSED, UNPROPOSED REVIEW)

Status of every item below: **proposed by the implementer session, unsigned, not reviewed**.
None of them may be read as an accepted accounting decision, and none of them changes the product.

Scope note: the model is `reserve_depletion` - extraction and decline businesses whose reserves, depletion and sales link is verifiable. Unit rule: reserve stock and flow in one unit; depletion x recovery rate converts to sellable quantity, then multiplied by a net price in the same unit.

- **DEC-M10-1** - Does the disclosed reserve quantity already embed the recovery factor?
  - PROPOSED: `depletion` is the in-situ reserve quantity consumed and `recovery_rate` is the factor applied to it; when the disclosure only publishes recoverable reserves, the adapter must set `recovery_rate = 1` and record `reported_derived_assumed = assumed`.
  - Risk if unanswered: Multiplying twice understates revenue with no runtime error (oracle.md R9).
- **DEC-M10-2** - Is `depletion` equal to current-period sales?
  - PROPOSED: no. The model treats depletion x recovery as the sellable production proxy; the production/sales/inventory bridge must be reconciled in the mapping and any difference recorded as an assumption.
  - Risk if unanswered: Treating depletion as sales mixes inventory movement into revenue.
- **DEC-M10-3** - Non-negative `additions` versus signed `reserve_revisions`.
  - PROPOSED: keep. Downward reserve movements must be routed through `reserve_revisions`; a negative addition is refused (`[0, inf)`), which the enumeration in oq_rulings.json confirms as contract, not as an accident.
  - Risk if unanswered: The sign routing is a mapping decision that the runtime cannot check.

## Disclosure items that must be collected before D can be claimed

card L52: reserve classification, additions and revisions, depletion, the recovery definition, the production/sales/inventory bridge and the realised price

## Business-level negatives that must be adjudicated (not runtime gates)

- reserves that already embed the recovery factor must not be multiplied by it again
- depletion does not automatically equal current-period sales

## What is deliberately NOT decided here

- No gross-versus-net, tax, ownership or consolidation-scope ruling is made; the mapping skeleton lists
  those as required fields with no value.
- No fiscal-period or restatement mapping is asserted.
- No scenario or accuracy statement is made from this model.
