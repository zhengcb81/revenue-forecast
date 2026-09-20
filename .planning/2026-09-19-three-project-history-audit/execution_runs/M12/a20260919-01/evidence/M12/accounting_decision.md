# M12 · bank_revenue — accounting / disclosure decisions (PROPOSED, UNPROPOSED REVIEW)

Status of every item below: **proposed by the implementer session, unsigned, not reviewed**.
None of them may be read as an accepted accounting decision, and none of them changes the product.

Scope note: the model is `bank_revenue` - bank growth, maturity and balance-sheet repricing. Unit rule: average earning / interest-bearing balances in U; rates are annual decimals and may be negative; fees are recognised net amounts.

- **DEC-M12-1** - Average balances versus period-end balances.
  - PROPOSED: average balances only (card L8). A period-end balance substituted for an average is a restatement of the driver, not a rounding choice.
  - Risk if unanswered: Period-end balances import a rate shock into the average and misstate the year.
- **DEC-M12-2** - NIM is not the asset yield.
  - PROPOSED: derive `asset_yield` from disclosed interest income divided by average earning assets; NIM must never be used as a substitute, and the derivation is recorded in `conversion_formula`.
  - Risk if unanswered: NIM already nets funding cost, so using it as the yield double-counts the funding side.
- **DEC-M12-3** - A year with negative total revenue cannot be expressed.
  - PROPOSED: escalate rather than adapt. `card_M12.md` L48 states the contract does not support a negative total, and `common_model_cards.md` L11 forbids clipping to zero or changing the accounting definition to force a pass. A contract extension is an owner decision.
  - Risk if unanswered: Clipping to zero would silently replace a real loss year with break-even.

## Disclosure items that must be collected before D can be claimed

card L46: average earning assets / interest-bearing liabilities, annualised rates, net interest, fees and other operating income

## Business-level negatives that must be adjudicated (not runtime gates)

- negative interest rates are allowed and must not be re-bounded to 0-1
- net interest margin (NIM) is not the asset yield
- a negative total revenue is not supported by the current contract

## What is deliberately NOT decided here

- No gross-versus-net, tax, ownership or consolidation-scope ruling is made; the mapping skeleton lists
  those as required fields with no value.
- No fiscal-period or restatement mapping is asserted.
- No scenario or accuracy statement is made from this model.
