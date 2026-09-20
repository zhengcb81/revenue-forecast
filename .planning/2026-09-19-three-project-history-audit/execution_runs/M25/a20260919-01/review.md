# M25 · implementer review record

Card M25 (`installed_base_aftermarket`), Parent I-10. Attempt `execution_runs/M25/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M25/source_manifest.json` |
| B positive | `[300.0]` vs independent oracle `[300.0]`, within `1e-9*max(1,|e|)` | `evidence/M25/formula_result.json` |
| continuity positive | actual `[300.0, 330.0]` vs oracle `[300.0, 330.0]` | `evidence/M25/negative_results.json` |
| defaults case | actual `[0.0]` vs oracle `[0.0]` (not gating) | `evidence/M25/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M25/negative_results.json` |
| mutation proof | A/B/D red (rc=3), C green (rc=0), E byte-identical | `recovery/selfcheck/selfcheck_result.json` |
| D mapping | **NOT delivered**: no real disclosure was adapted; the per-driver mapping is explicitly `missing` and the professional decisions are PROPOSED only | `evidence/M25/disclosure_mapping.json`, `evidence/M25/accounting_decision.md` |
| E probe | `not_applicable_with_reason`; NOT a scenario set and NOT accuracy evidence | `evidence/M25/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M25/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M25_M28.py`, which imports only `argparse`, `hashlib`, `json`, `os` and `decimal` (see the `import_lines` list inside `evidence/M25/oracle_selfcheck.json`). It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- The runner `scripts/run_card.py` calls exactly one product function, `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from `evidence/M25/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The frozen oracle is reproducible: case E regenerated `input.json`, `cases.json` and `oracle.json` byte-for-byte from the generator alone.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = (opening_installed_units + new_installed_units*new_unit_revenue_fraction - retired_units*retirement_lost_fraction) * attach_rate * annual_revenue_per_attached_unit`
- Registry required: `['opening_installed_units', 'new_installed_units', 'retired_units', 'closing_installed_units', 'new_unit_revenue_fraction', 'retirement_lost_fraction', 'attach_rate', 'annual_revenue_per_attached_unit']`; optional: `[]`; defaults: `{}`; driver_bounds: `{}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - retired_units exceeds opening installed cohort: FY2027
- `N01a`: ModelRegistryError - installed_base_aftermarket.opening_installed_units.FY2027 must be numeric
- `N01b`: ModelRegistryError - installed_base_aftermarket.opening_installed_units.FY2027 must be finite
- `N01c`: ModelRegistryError - installed_base_aftermarket.opening_installed_units.FY2027 must be finite
- `N01d`: ModelRegistryError - installed_base_aftermarket.opening_installed_units.FY2027 must be finite
- `N02`: ModelRegistryError - driver installed_base_aftermarket.opening_installed_units must contain one value per forecast year
- `N03`: ModelRegistryError - missing drivers for installed_base_aftermarket: opening_installed_units
- `N04`: ModelRegistryError - unsupported drivers for installed_base_aftermarket: unknown_driver
- `N05a`: ModelRegistryError - installed_base_aftermarket.years must contain fiscal years
- `N05b`: ModelRegistryError - installed_base_aftermarket.years must contain fiscal years
- `CONT-BREAK`: ModelRegistryError - opening_installed_units continuity failed: FY2028

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[300.0] matches_compared=True expect_equal=None - rowwise calculator discards base_revenue; design observation only, not a pass condition
- `OBS-DEFAULT-ZERO`: raised=None actual=[0.0] matches_compared=None expect_equal=None - all eight required drivers explicitly zero, no optional driver exists; the mechanism is the rowwise calculator, which starts from zero for every year

## 5. Judgement calls the reviewer should attack first

1. **The oracle history, and where the earlier narrative was wrong.** The v1 generation had a defect, the first product run exposed it, and the generator was re-run before the definitive run. THREE corrections to the earlier write-up are recorded rather than glossed over: (a) the claim 'the correction was applied BEFORE `oracle.md` was written' is **not supported by mtime** and is withdrawn - the final generator's mtime is later than all four `oracle.md` files and later than the first product run; what IS supported is that no GATING expectation was ever rewritten and that only M25's non-gating defaults block changed; (b) the claim that the M27 crash meant 'no `oracle.json` was produced at all' is **wrong** - a complete valid v1 `oracle.json` exists and is byte-identical to the frozen one; (c) the v1 generator SOURCE and the M27 traceback were **never persisted**, so that accident is not reproducible and is recorded as a provenance gap. Also note the r2 re-freeze: the M26/M27/M28 NEG-CARD patch was corrected (review finding P2-1) and `cases.json` re-frozen before the definitive run. If the owner insists on the stricter rule '`oracle.json` must predate ANY product run', this attempt does not satisfy it and the honest answer is `oracle_json_precedes_the_first_ever_run = false`.
2. **NEG-CARD's rejection mechanism is now declared AND enforced.** For M26/M27/M28 the r1 patch used `kind=set_driver` with a `{"__float__": X}` envelope, so the driver was assigned a dict and the generic per-year length guard refused the case before the card-specific guard ran - the r1 coverage claim was unsupported. The patch is now a one-element list, and `run_card.py` verifies the declared mechanism message as a GATING condition (`neg_card_mechanism_check`). M25 never had the defect.
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

- R8: no negative case exercises a ratio driver outside [0,1] (NEG-CARD is refused by the retired-cohort guard, not by a value-domain check)
- R2: the stock-flow bridge mismatch branch is not exercised directly by NEG-CARD (its closing value 39 is consistent with the bridge); only the cross-year branch is exercised, by CONT-BREAK

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M25_M28.py --card M25 --out-root <scratch>` in a scratch tree and diff the generated artefacts against the frozen ones (case E already did this; repeating it independently is the point).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm `[300.0]` / `[300.0, 330.0]` / `[0.0]` with 11/11 negatives rejected.
3. Confirm the isolated copy hashes still equal production (`evidence/M25/source_manifest.json`).
4. Confirm `oracle.md` was not edited after the definitive run (compare `sha256` with `source_manifest.oracle_document.sha256_before_the_definitive_product_run`); the r2 revision section at the end of `oracle.md` is an APPEND made after that run and is declared as such.
5. Confirm the r2 re-freeze only changed `cases.json` for M26/M27/M28 (the NEG-CARD patch), compare `evidence/%s/revision_r2.json` `p2_1_cases_json_refreeze.cases_json_sha256`, and confirm no gating expectation moved.
6. Pick a case the implementer did not use (section 7) and freeze its expectation BEFORE running.
7. Adjudicate the DEC items in `evidence/M25/accounting_decision.md` and the OQ items in `evidence/M25/oq_rulings.json`.
