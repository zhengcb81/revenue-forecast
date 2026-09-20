# M22 · milestone_royalty · 里程碑与销售分成 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls
under a professional decision (cross-process locking, publication transaction boundaries,
fiscal-period / restatement / gross-vs-net and payability attribution, unidentifiable model
parameters, sample and statistical thresholds, deployment migration and natural-observation
qualification).

## Professional decisions

**None of those categories arises in this card's A-C scope**, and no product file was
modified. The scope is a pure in-process calculator plus a frozen formula oracle:

- no cross-process locking, no lease, no publication and no deployment decision (the model is
  a pure function: `calculate_registered_model` has no durable state and no side effect);
- no restatement / gross-vs-net / payability attribution decision: this attempt uses only the
  card's frozen **synthetic** numbers, never a real company disclosure;
- no unidentifiable parameter and no statistical threshold: the tolerance is the shared
  contract `1e-9 * max(1, |expected|)`.

## Escalated to the owner (not decided here)

- **OQ-01 (binding provenance).** The cards say the run cwd must come from I-00-B, but I-00-B
  binds the isolation *plan* and the two-stage command rule, not a materialised checkout tree.
  This attempt therefore materialises its own read-only snapshot (`iso/checkout_scripts`,
  hashes equal to production). If the intended binding is an I-00-B-materialised checkout, the
  provenance chain differs; the code under test is byte-identical either way. Needs a ruling.
- **OQ-02 (gating negative vs the card's literal negative).** For M22 the card's literal
  negative is also a length-domain case, so the GATING negative was moved to a case that
  reaches the value-domain guard and the literal case was kept as a non-gating observation.
  Owner/reviewer must confirm that is acceptable (see `review.md` section 5).
- **OQ-03 (silent zero-fill).** `scripts/model_registry.py:335` silently turns an omitted
  optional driver with no explicit default into 0.0. Named instances for these four cards:
  `delivery_pipeline.other_revenue`, `milestone_royalty.milestone_revenue` and
  `.service_revenue`, `insurance_service.other_revenue`, `subscription_arr_bridge.usage_revenue`.
  Registered, NOT fixed; no product change. Enumeration in `evidence/M22/oq_rulings.json`.
- **OQ-04 (business rejections stay open).** The cards' "professional decision / business
  negative" items (delivery != recognition; probability-weighted milestones are not recognised
  revenue; this is not an IFRS17 engine; NRR != GRR, ARR != revenue) are NOT runtime contract
  and are NOT adjudicated here. Unresolved -> `STOP_DISCLOSURE_ADAPTATION`.
