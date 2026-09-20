# M26 · implementer review record

Card M26 (`store_cohorts`), Parent I-10. Attempt `execution_runs/M26/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M26/source_manifest.json` |
| B positive | `[205.0]` vs independent oracle `[205.0]`, within `1e-9*max(1,|e|)` | `evidence/M26/formula_result.json` |
| continuity positive | actual `[205.0, 230.0]` vs oracle `[205.0, 230.0]` | `evidence/M26/negative_results.json` |
| defaults case | actual `[0.0]` vs oracle `[0.0]` (not gating) | `evidence/M26/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M26/negative_results.json` |
| mutation proof | A/B/D red (rc=3), C green (rc=0), E byte-identical | `recovery/selfcheck/selfcheck_result.json` |
| D mapping | **NOT delivered**: no real disclosure was adapted; the per-driver mapping is explicitly `missing` and the professional decisions are PROPOSED only | `evidence/M26/disclosure_mapping.json`, `evidence/M26/accounting_decision.md` |
| E probe | `not_applicable_with_reason`; NOT a scenario set and NOT accuracy evidence | `evidence/M26/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M26/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M25_M28.py`, which imports only `argparse`, `hashlib`, `json`, `os` and `decimal` (see the `import_lines` list inside `evidence/M26/oracle_selfcheck.json`). It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- The runner `scripts/run_card.py` calls exactly one product function, `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from `evidence/M26/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The frozen oracle is reproducible: case E regenerated `input.json`, `cases.json` and `oracle.json` byte-for-byte from the generator alone.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = (opening_stores - closed_stores*closure_lost_fraction + new_stores*new_store_revenue_fraction*new_store_productivity) * annual_revenue_per_mature_store`
- Registry required: `['opening_stores', 'new_stores', 'closed_stores', 'closing_stores', 'new_store_revenue_fraction', 'closure_lost_fraction', 'new_store_productivity', 'annual_revenue_per_mature_store']`; optional: `[]`; defaults: `{}`; driver_bounds: `{'new_store_productivity': [0.0, None]}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - driver store_cohorts.closing_stores must contain one value per forecast year
- `N01a`: ModelRegistryError - store_cohorts.opening_stores.FY2027 must be numeric
- `N01b`: ModelRegistryError - store_cohorts.opening_stores.FY2027 must be finite
- `N01c`: ModelRegistryError - store_cohorts.opening_stores.FY2027 must be finite
- `N01d`: ModelRegistryError - store_cohorts.opening_stores.FY2027 must be finite
- `N02`: ModelRegistryError - driver store_cohorts.opening_stores must contain one value per forecast year
- `N03`: ModelRegistryError - missing drivers for store_cohorts: opening_stores
- `N04`: ModelRegistryError - unsupported drivers for store_cohorts: unknown_driver
- `N05a`: ModelRegistryError - store_cohorts.years must contain fiscal years
- `N05b`: ModelRegistryError - store_cohorts.years must contain fiscal years
- `CONT-BREAK`: ModelRegistryError - opening_stores continuity failed: FY2028

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[205.0] matches_compared=True expect_equal=None - rowwise calculator discards base_revenue; design observation only, not a pass condition
- `OBS-PRODUCTIVITY-BOUND`: raised=None actual=[220.0] matches_compared=None expect_equal=None - card_M26.md L8 says new-store productivity may exceed one; the registry declares store_cohorts.new_store_productivity = (0.0, inf) while this driver's dimension is ratio. The probe records black-box behaviour with NO expectation and NO verdict asserted.

## 5. Judgement calls the reviewer should attack first

1. **The oracle was corrected mid-attempt, and that is disclosed rather than hidden.** The first generation planted a wrong defaults expectation for M25 (positive 300 instead of the all-zero hand value 0) and crashed on M27 (`TypeError: Object of type Decimal is not JSON serializable`, no `oracle.json` at all). The generator was fixed BEFORE `oracle.md` was written and BEFORE the definitive product run; the pre-correction artefacts are preserved under `recovery/precorrection/`. Consequence to attack: `oracle.json`'s mtime is LATER than the first ever product run, so the headline mtime claim only holds against the DEFINITIVE run. If the reviewer requires the stricter claim (oracle.json older than any product run whatsoever), this attempt does not satisfy it and the honest answer is `oracle_json_precedes_the_first_ever_product_run = false`.
2. **NEG-CARD is refused for a different reason than the card's wording suggests.** NEG-CARD: closing_stores=[24] (card_M26.md L50) - 20+5-2 = 23 != 24, so the store-count bridge does not balance. The dedicated guard is therefore exercised, but any *other* branch of the same guard family is not - see the uncovered list in section 7.
3. **Silent zero-fill.** not triggered: this model declares `optional = ()` and `defaults = {}`, so there is no optional driver to zero-fill.
4. **Disclosure adaptation is 0/N.** No real company disclosure was adapted in this attempt, so no historical reconciliation exists; a mapping probe would have to invent the series.
5. **Isolated-checkout provenance.** I-00-B binds the isolation *plan* and the two-stage command rule but does not materialise a checkout tree; this attempt materialises its own read-only snapshot (`iso/checkout_scripts`, hashes equal to production). If the intended binding is a checkout materialised by I-00-B, that is a scope deviation to record - the code under test is byte-identical either way.
6. **`defaults` case for M25/M26 is an all-zero identity input, not an omission case.** With `optional = ()` there is nothing to omit; the case only shows that the rowwise calculator starts from zero. It is marked not gating.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated specification, the existing implementation is retained.
- It does **not** treat the two-year continuity example as a scenario set or as accuracy evidence.

## 7. Known uncovered surfaces (offered to the reviewer as reserve cases)

- R3: no negative case exercises closed_stores exceeding opening_stores (NEG-CARD is refused by the bridge, not by that dedicated guard)
- R8: no negative case exercises a negative new_store_productivity

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M25_M28.py --card M26 --out-root <scratch>` in a scratch tree and diff the generated artefacts against the frozen ones (case E already did this; repeating it independently is the point).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm `[205.0]` / `[205.0, 230.0]` / `[0.0]` with 11/11 negatives rejected.
3. Confirm the isolated copy hashes still equal production (`evidence/M26/source_manifest.json`).
4. Confirm `oracle.md` was not edited after the definitive run (compare `sha256` with `revision_r2.hash_ledger.oracle_md_sha256_before_the_definitive_product_run`).
5. Pick a case the implementer did not use (section 7) and freeze its expectation BEFORE running.
6. Adjudicate the DEC items in `evidence/M26/accounting_decision.md` and the OQ items in `evidence/M26/oq_rulings.json`.
