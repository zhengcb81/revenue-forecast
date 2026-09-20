# M05 · implementer review record

Card M05 (`subscription`), Parent I-10. Attempt `execution_runs/M05/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M05/source_manifest.json` |
| B positive | `[620.0]` vs independent oracle `[620]`, within `1e-9*max(1,|e|)` | `evidence/M05/formula_result.json` |
| continuity positive | actual `[550.0, 880.0]` vs oracle `[550, 880]` | `evidence/M05/negative_results.json` |
| defaults case | actual `[600.0]` vs oracle `[600]` (not gating) | `evidence/M05/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M05/negative_results.json` |
| D mapping | one real disclosed mapping with page, span, unit, period and PDF sha256; professional decisions written as PROPOSED only | `evidence/M05/disclosure_mapping.json`, `evidence/M05/accounting_decision.md` |
| E probe | recorded as `blocked` with the concrete reason; NOT a scenario set and NOT accuracy evidence | `evidence/M05/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M05/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M05.py`, which imports only `argparse`, `hashlib`, `json`, `os`
  and `decimal` (see the `import_lines` list inside `evidence/M05/oracle_selfcheck.json`).
  It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from
  `evidence/M05/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON
  parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`,
  N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and
  `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`) was used for M05-M08;
  there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = average_customers * revenue_per_customer * timing_factor + usage_revenue`
- Registry required: `['average_customers', 'revenue_per_customer']`; optional: `['timing_factor', 'usage_revenue']`; defaults: `{'timing_factor': 1.0}`; driver_bounds: `{}`
- Rejections and their messages:
  - `NEG-CARD`: ModelRegistryError - `driver subscription.timing_factor must contain one value per forecast year`
  - `N01a`: ModelRegistryError - `subscription.average_customers.FY2027 must be numeric`
  - `N01b`: ModelRegistryError - `subscription.average_customers.FY2027 must be finite`
  - `N01c`: ModelRegistryError - `subscription.average_customers.FY2027 must be finite`
  - `N01d`: ModelRegistryError - `subscription.average_customers.FY2027 must be finite`
  - `N02`: ModelRegistryError - `driver subscription.average_customers must contain one value per forecast year`
  - `N03`: ModelRegistryError - `missing drivers for subscription: average_customers`
  - `N04`: ModelRegistryError - `unsupported drivers for subscription: unknown_driver`
  - `N05a`: ModelRegistryError - `subscription.years must contain fiscal years`
  - `N05b`: ModelRegistryError - `subscription.years must contain fiscal years`
  - `CONT-BREAK`: ModelRegistryError - `subscription.years must be consecutive and increasing`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[620.0] matches_compared=True expect_equal=None matches_expected=None
  - why: rowwise calculator discards base_revenue; design observation only, not a pass condition
- `OBS-ALT-CONV`: raised=None actual=[620.0] matches_compared=True expect_equal=None matches_expected=None
  - why: replays the frozen card input so the runner's own reading is reproducible

## 5. Judgement calls the reviewer should attack first

1. **The period-end member trap.** The issuer prints 7331 万 members *at year end* and 51.48 亿元 of
   *full-year* membership revenue. Dividing them gives ≈70.22 元/member, which looks like an ARPU and is
   recorded in the mapping only as a labelled reference value - it is **not** the driver, because the card
   refuses the period-end-for-average substitution (R7). A reviewer who accepts that ratio silently would
   convert an arithmetic artefact into an input.
2. **NEG-CARD is rejected for a different reason than the card's wording suggests.** `timing_factor=[1.5]`
   is refused by the *length* guard first (`driver subscription.timing_factor must contain one value per
   forecast year`) because the positive input has a 1-year `years` list and index 0 does not exist on an
   empty array. The value-domain rejection (ratio [0,1]) is therefore **not** exercised by this case. If the
   reviewer wants the value-domain path covered, a new case with `years=[2027,2027+1]` and
   `timing_factor=[1,1.5]` is the right one - it is a case the implementer did not run.
3. **Silent zero-fill of `usage_revenue`.** `scripts/model_registry.py:335` turns an omitted optional driver
   without an explicit default into `0.0`. For this model that asserts *no usage revenue* without any
   disclosure saying so. Recorded as OQ-04, no product change made.
4. **Disclosure adaptation is 0/2.** Both required drivers are unmapped, so no historical reconciliation is
   possible; a mapping probe would have to invent the average-customer series.

5. **Isolated-checkout provenance.** I-00-B binds the isolation *plan* and the two-stage command rule but
   does not materialise a checkout tree; this attempt therefore materialises its own read-only snapshot
   (`iso/checkout_scripts`, hashes equal to production). If the intended binding is a checkout materialised by
   I-00-B, that is a scope deviation to record - the code under test is byte-identical either way.
6. **Disclosure receipt strength.** Unlike the cninfo sidecars used by M01, the company-wiki sidecars for
   these documents carry no publisher content hash, so `local_hash_matches_publisher_receipt` is
   `NOT_VERIFIABLE` for all four cards. Stated as a gap.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a production
  forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated specification,
  the existing implementation is retained.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M05.py --card M05 --out-root <attempt>` in a scratch tree and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` and diff `run_result.json`.
2. Confirm the isolated copy hashes still equal production (`evidence/M05/source_manifest.json`).
3. Confirm `oracle.md` was not edited after the run (hash in `commands.json` / `source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running.
5. Adjudicate the DEC items in `evidence/M05/accounting_decision.md`.

---

## Exit-code self-check (shared runner; self-check performed on M05)

| case | mutation | raw rc | expected | proves |
|---|---|---|---|---|
| A | `oracle.json positive.expected_float -> [999]` in a scratch copy | **3** | 3 | a corrupted expectation cannot hide behind rc=0 |
| B | `input.json` positive driver deleted in a scratch copy | **2** | 2 | rc=2 is reachable: no verdict exists |
| C | uncorrupted scratch copy | **0** | 0 | the repaired exit code stays 0 for a genuinely passing card |

Details: `execution_runs/M05/a20260919-01/recovery/selfcheck_result.json`.

---

## revision r2 - response to the independent review

Independent review of r1: **accepted_scoped (formula qualification only)**.

The nine r1 findings were handled as follows (nothing frozen was rewritten, no product file was touched):

- F-M05-01 (source_manifest pre-run-hash wording)
- F-M05-02 (self-check argv path + scope)

Details per finding (file:line) are in `evidence/M05/revision_r2.json`; the OQ-02 / OQ-04 rulings are in
`evidence/M05/oq_rulings.json`; the owner's three-step index remediation for M08 is in `handoff.json`.

New hashes after r2: `oracle.md`, `commands.json`, `after/rerun_sha256.json` and `evidence/M05/*` were all
re-hashed; see `evidence/M05/evidence_hashes.json` and `after/rerun_sha256.json`.

Status after r2: `formula` = review_pending (point review of r2), `disclosure_adaptation` = unmapped, `accuracy` = unproven.

---