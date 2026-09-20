# M28 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a professional decision (cross-process locking, publication transaction boundaries, fiscal-period / restatement / gross-vs-net and payability attribution, unidentifiable model parameters, sample and statistical thresholds, deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net, sampling or deployment decision arises in this card: the scope is a pure in-process calculator plus read-only evidence. The decisions that DO arise are accounting / disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in `evidence/M28/accounting_decision.md`:

- DEC-M28-1 (unsigned): a year-end AUM must not be charged a full year of fees (card_M28.md L60)
- DEC-M28-2 (unsigned): the timing of market moves and performance-fee crystallisation needs evidence (card_M28.md L60)

## Escalated to the owner (not decided here)

- OQ-M25M28-01 for this card: the registry declares `defaults = {}` while `recognized_performance_fees` is optional, so `scripts/model_registry.py:335` silently zero-fills it on omission. The card text (card_M28.md L9) declares a default of 0. The omission is therefore indistinguishable from a genuine zero. Recorded, NOT fixed; no position asserted, no product change. Enumeration evidence: `evidence/M28/oq_rulings.json`.
- OQ-01 (binding scope, all four cards): the cards say the run cwd must come from I-00-B, but I-00-B binds only the isolation plan and the two-stage command rule, not a materialised checkout tree. This attempt materialised its own read-only snapshot (iso/checkout_scripts, hashes equal to production). The code under test is byte-identical either way; the provenance chain differs. Needs a binding ruling.

## No owner gate is hidden here

Nothing in this card silently resolved a professional question by writing code: the calculator was not modified, the registry was not modified, and every unresolved item above is left open for the owner / reviewer.
