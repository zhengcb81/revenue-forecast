# M12 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a
professional decision (cross-process locking, publication transaction boundaries, fiscal-period /
restatement / gross-vs-net and payability attribution, unidentifiable model parameters, sample and
statistical thresholds, deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net or deployment decision arises in this card:
the scope is a pure in-process calculator plus read-only evidence. The decisions that DO arise are
accounting/disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in
`evidence/M12/accounting_decision.md`:

- **DEC-M12-1** - Average balances versus period-end balances.
  - PROPOSED: average balances only (card L8). A period-end balance substituted for an average is a restatement of the driver, not a rounding choice.
  - Risk if unanswered: Period-end balances import a rate shock into the average and misstate the year.
- **DEC-M12-2** - NIM is not the asset yield.
  - PROPOSED: derive `asset_yield` from disclosed interest income divided by average earning assets; NIM must never be used as a substitute, and the derivation is recorded in `conversion_formula`.
  - Risk if unanswered: NIM already nets funding cost, so using it as the yield double-counts the funding side.
- **DEC-M12-3** - A year with negative total revenue cannot be expressed.
  - PROPOSED: escalate rather than adapt. `card_M12.md` L48 states the contract does not support a negative total, and `common_model_cards.md` L11 forbids clipping to zero or changing the accounting definition to force a pass. A contract extension is an owner decision.
  - Risk if unanswered: Clipping to zero would silently replace a real loss year with break-even.

## Escalated to the owner (not decided here)

- OQ-1 (batch): `scripts/model_registry.py:335` silently zero-fills an omitted optional driver that has no
  declared default. All 5 optional drivers of M09-M12 are in that
  class (5 of
  5), and 31
  registry-wide. No position asserted, no product change.
- OQ-3 (M09/M11): `revenue_per_unit` / `revenue_per_activity` default to `[0, inf)`, so a negative realised
  price or a negative (rebate) tariff cannot be expressed; only
  2 of
  23 such drivers admit negative values.
  Registered, not fixed.
- OQ-5 (provenance): production files under `scripts/` carry an external LastWriteTime inside this
  attempt's window with byte-identical content; `integrity.json` records the affected files and hashes.

## Owner hand-off

The owner-facing steps and open questions of this card are listed in `handoff.json`
(`open_questions`, `next_action`, `blocked_by`); `handoff.json` is the authoritative continuation record.
Nothing in this card needs a **fiscal-period / restatement / gross-vs-net** ruling to stay within A-C,
because no disclosure value was bound to a driver in this attempt.
