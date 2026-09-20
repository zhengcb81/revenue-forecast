# M24 · subscription_arr_bridge · ARR 存量与收入时点 - implementer review record

Card M24 (`subscription_arr_bridge`), Parent I-10. Attempt `execution_runs/M24/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M24/source_manifest.json` |
| B positive | actual `[215.0]` vs independent oracle `[215.0]`, within `1e-9*max(1,|e|)` | `evidence/M24/formula_result.json` |
| continuity positive | actual `[215.0, 250.0]` vs oracle `[215.0, 250.0]` | `evidence/M24/negative_results.json` |
| defaults case | actual `[210.0]` vs oracle `[210.0]` (not gating) | `evidence/M24/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M24/negative_results.json` |
| D mapping | **NOT DONE** - needs a signed industry/accounting review | `evidence/M24/qualification.json` |
| E probe | **NOT DONE** - belongs to I-10-A | `evidence/M24/qualification.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M24/qualification.json` |

Raw exit code of the product run: **0** (0=pass / 2=no-verdict / 3=negative not rejected as
expected / 1=harness error). stderr is 0 bytes.

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M24.py`, which imports only `argparse`,
  `hashlib`, `json`, `os`, `sys` and `decimal` - see the `import_lines` list inside
  `evidence/M24/oracle_selfcheck.json`; `product_import_present` is `false`.
- The oracle document `oracle.md` (sections 0-11) was written **before** any product run. Its
  frozen body is 11525 bytes, sha256
  `fbef9d5493d56e96e9a14808f1570ffcec4871ab6296c9ca9ff000038f88693c`; the exact reconstruction identity
  `oracle.md == frozen_body + b"\n---\n\n" + run_section` is verified by
  `scripts/verify_prefix_chain.py` in all four attempts of this batch.
- `evidence/M24/oracle.json` is **byte-identical when regenerated** (re-run performed).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations
  only from `evidence/M24/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`) was used for
  M05-M08 and for all four attempts of this batch; there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = opening_arr - opening_arr*(1-gross_retention_rate)*lost_arr_revenue_fraction + expansion_arr*expansion_revenue_fraction + new_arr*new_arr_revenue_fraction + usage_revenue`
- Registry required: `['opening_arr', 'expansion_arr', 'new_arr', 'closing_arr', 'gross_retention_rate', 'lost_arr_revenue_fraction', 'expansion_revenue_fraction', 'new_arr_revenue_fraction']`; optional: `['usage_revenue']`; defaults: `{}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - `opening_arr stock-flow balance failed: FY2027`
- `N01a`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be numeric`
- `N01b`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be finite`
- `N01c`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be finite`
- `N01d`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be finite`
- `N02`: ModelRegistryError - `driver subscription_arr_bridge.opening_arr must contain one value per forecast year`
- `N03`: ModelRegistryError - `missing drivers for subscription_arr_bridge: opening_arr`
- `N04`: ModelRegistryError - `unsupported drivers for subscription_arr_bridge: unknown_driver`
- `N05a`: ModelRegistryError - `subscription_arr_bridge.years must contain fiscal years`
- `N05b`: ModelRegistryError - `subscription_arr_bridge.years must contain fiscal years`
- `CONT-BREAK`: ModelRegistryError - `opening_arr continuity failed: FY2028`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[215.0]
- `OBS-DEFAULT-EQUIV`: raised=None actual=[210.0]
- `OBS-GRR-ONE-SECOND-YEAR`: raised=None actual=[215.0, 250.0]

## 5. Judgement calls the reviewer should attack first

1. The card's CONT-BREAK patch is documented in the card as 'each year balances individually, but year-2 opening is 1 above year-1 closing'. With the frozen numbers (`opening_arr=[200,251]`, `closing_arr=[250,251]`) that description is not what happens: FY2027's closing was also moved to 251, so FY2027's BALANCE check fires first. The observed message is `opening_arr stock-flow balance failed: FY2027`, not a continuity message. The frozen requirement is the exception TYPE, and it was met; a reviewer should confirm that satisfying the type is enough, or ask for a case whose numbers make the card's prose literally true.
2. Because of that, the product's cross-year CONTINUITY guard (`opening_arr continuity failed`) is NOT exercised by this case set. The guard exists in the code but is a change the implementer did not run; the parent agent was told.
3. the continuity positive relies on `gross_retention_rate = 1` in FY2028; the retained-ARR guard (`opening_arr * gross_retention_rate == 0 and expansion_arr > 0`) is therefore not triggered, but a zero opening ARR with positive expansion would be. The non-gating observation OBS-GRR-ONE-SECOND-YEAR only records that the input replays.
4. `usage_revenue` is optional with no explicit default and is silently zero-filled.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review
  plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated
  specification, the existing implementation is retained.
- It does **not** claim that a formula pass on this card implies anything about the other 30
  models: the parent card explicitly forbids extrapolating accuracy from formula passes.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M24.py --card M24 --out-root <scratch>` and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` against
   `iso/checkout_scripts` and diff `run_result.json`.
2. Re-run `scripts/verify_prefix_chain.py <plan>` to confirm the oracle.md frozen-body chain.
3. Confirm the isolated copy hashes still equal production
   (`evidence/M24/source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running it.
5. Re-run `scripts/enumerate_oq_rulings.py` and compare the counts with
   `evidence/M24/oq_rulings_enumeration.json`.
6. Adjudicate the OQ items in `decision.md` and `handoff.json`.

## 8. Exit-code mutation self-check (red then green)

Scratch tree: `recovery/selfcheck/` (the frozen evidence is never mutated).

| probe | raw rc | expected rc |
|---|---|---|
| D_pristine_uncorrupted | 0 | 0 |
| A_corrupted_positive_expectation | 3 | 3 |
| B_corrupted_negative_assertion | 3 | 3 |
| C_corrupted_positive_input | 2 | 2 |
| D_restored_uncorrupted | 0 | 0 |

`frozen_hashes_unchanged` = `True`. Full record:
`recovery/selfcheck/selfcheck_result.json`.
