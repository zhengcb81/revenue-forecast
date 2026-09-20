# M26 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a professional decision (cross-process locking, publication transaction boundaries, fiscal-period / restatement / gross-vs-net and payability attribution, unidentifiable model parameters, sample and statistical thresholds, deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net, sampling or deployment decision arises in this card: the scope is a pure in-process calculator plus read-only evidence. The decisions that DO arise are accounting / disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in `evidence/M26/accounting_decision.md`:

- DEC-M26-1 (unsigned): treating a next-year new store as an opening mature store is a simplification (card_M26.md L54)
- DEC-M26-2 (unsigned): a multi-year ramp is not covered by the single-year fraction (card_M26.md L54)

## Escalated to the owner (not decided here)

- OQ-M25M28-01 is NOT triggered by this card: `optional = ()` and `defaults = {}`, so there is no optional driver to zero-fill. The card's `optional default {}` text and the registry agree. Enumeration evidence: `evidence/M26/oq_rulings.json`.
- OQ-01 (binding scope, all four cards): the cards say the run cwd must come from I-00-B, but I-00-B binds only the isolation plan and the two-stage command rule, not a materialised checkout tree. This attempt materialised its own read-only snapshot (iso/checkout_scripts, hashes equal to production). The code under test is byte-identical either way; the provenance chain differs. Needs a binding ruling.

## No owner gate is hidden here

Nothing in this card silently resolved a professional question by writing code: the calculator was not modified, the registry was not modified, and every unresolved item above is left open for the owner / reviewer.
