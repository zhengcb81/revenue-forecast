# M10 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a
professional decision (cross-process locking, publication transaction boundaries, fiscal-period /
restatement / gross-vs-net and payability attribution, unidentifiable model parameters, sample and
statistical thresholds, deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net or deployment decision arises in this card:
the scope is a pure in-process calculator plus read-only evidence. The decisions that DO arise are
accounting/disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in
`evidence/M10/accounting_decision.md`:

- **DEC-M10-1** - Does the disclosed reserve quantity already embed the recovery factor?
  - PROPOSED: `depletion` is the in-situ reserve quantity consumed and `recovery_rate` is the factor applied to it; when the disclosure only publishes recoverable reserves, the adapter must set `recovery_rate = 1` and record `reported_derived_assumed = assumed`.
  - Risk if unanswered: Multiplying twice understates revenue with no runtime error (oracle.md R9).
- **DEC-M10-2** - Is `depletion` equal to current-period sales?
  - PROPOSED: no. The model treats depletion x recovery as the sellable production proxy; the production/sales/inventory bridge must be reconciled in the mapping and any difference recorded as an assumption.
  - Risk if unanswered: Treating depletion as sales mixes inventory movement into revenue.
- **DEC-M10-3** - Non-negative `additions` versus signed `reserve_revisions`.
  - PROPOSED: keep. Downward reserve movements must be routed through `reserve_revisions`; a negative addition is refused (`[0, inf)`), which the enumeration in oq_rulings.json confirms as contract, not as an accident.
  - Risk if unanswered: The sign routing is a mapping decision that the runtime cannot check.

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
