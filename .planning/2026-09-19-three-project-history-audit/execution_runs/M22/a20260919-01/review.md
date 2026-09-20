# M22 · milestone_royalty · 里程碑与销售分成 - implementer review record

Card M22 (`milestone_royalty`), Parent I-10. Attempt `execution_runs/M22/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M22/source_manifest.json` |
| B positive | actual `[55.0]` vs independent oracle `[55.0]`, within `1e-9*max(1,|e|)` | `evidence/M22/formula_result.json` |
| continuity positive | actual `[55.0, 4.0]` vs oracle `[55.0, 4.0]` | `evidence/M22/negative_results.json` |
| defaults case | actual `[40.0]` vs oracle `[40.0]` (not gating) | `evidence/M22/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M22/negative_results.json` |
| D mapping | **NOT DONE** - needs a signed industry/accounting review | `evidence/M22/qualification.json` |
| E probe | **NOT DONE** - belongs to I-10-A | `evidence/M22/qualification.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M22/qualification.json` |

Raw exit code of the product run: **0** (0=pass / 2=no-verdict / 3=negative not rejected as
expected / 1=harness error). stderr is 0 bytes.

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M22.py`, which imports only `argparse`,
  `hashlib`, `json`, `os`, `sys` and `decimal` - see the `import_lines` list inside
  `evidence/M22/oracle_selfcheck.json`; `product_import_present` is `false`.
- The oracle document `oracle.md` (sections 0-11) was written **before** any product run. Its
  frozen body is 9693 bytes, sha256
  `d83ce2961186c324a445985bc3b569a87183642b5a68e9abce6332d0f5f83d76`; the exact reconstruction identity
  `oracle.md == frozen_body + b"\n---\n\n" + run_section` is verified by
  `scripts/verify_prefix_chain.py` in all four attempts of this batch.
- `evidence/M22/oracle.json` is **byte-identical when regenerated** (re-run performed).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations
  only from `evidence/M22/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`) was used for
  M05-M08 and for all four attempts of this batch; there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = eligible_sales * royalty_rate + milestone_revenue + service_revenue`
- Registry required: `['eligible_sales', 'royalty_rate']`; optional: `['milestone_revenue', 'service_revenue']`; defaults: `{}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - `driver milestone_royalty.royalty_rate must contain one value per forecast year`
- `N01a`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be numeric`
- `N01b`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be finite`
- `N01c`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be finite`
- `N01d`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be finite`
- `N02`: ModelRegistryError - `driver milestone_royalty.eligible_sales must contain one value per forecast year`
- `N03`: ModelRegistryError - `missing drivers for milestone_royalty: eligible_sales`
- `N04`: ModelRegistryError - `unsupported drivers for milestone_royalty: unknown_driver`
- `N05a`: ModelRegistryError - `milestone_royalty.years must contain fiscal years`
- `N05b`: ModelRegistryError - `milestone_royalty.years must contain fiscal years`
- `CONT-BREAK`: ModelRegistryError - `milestone_royalty.years must be consecutive and increasing`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[55.0]
- `OBS-DEFAULT-EQUIV`: raised=None actual=[40.0]

## 5. Judgement calls the reviewer should attack first

1. NEG-CARD is the card's literal negative, but it is also the case that most obviously tests a CONTRACT question rather than an economic one: a tiered royalty agreement can have an effective rate above 1.0 of a narrow base. The registry's [0,1] ratio domain answers it, and the card's own text does not state that 1.01 is impossible; a reviewer should decide whether that is the intended contract.
2. `milestone_revenue` and `service_revenue` are optional with a DECLARED default of 0, so the defaults case is a genuine default test; `millestone`/`service` amounts are signed (any real number), so a negative milestone adjustment is accepted by the contract - this card does not test that.
3. the second year of the continuity positive has eligible_sales = 0 and a milestone only; this is the deliberate 'no sales, milestone only' shape and asserts nothing about probability-weighted contingent payments (which the card refuses).

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review
  plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated
  specification, the existing implementation is retained.
- It does **not** claim that a formula pass on this card implies anything about the other 30
  models: the parent card explicitly forbids extrapolating accuracy from formula passes.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M22.py --card M22 --out-root <scratch>` and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` against
   `iso/checkout_scripts` and diff `run_result.json`.
2. Re-run `scripts/verify_prefix_chain.py <plan>` to confirm the oracle.md frozen-body chain.
3. Confirm the isolated copy hashes still equal production
   (`evidence/M22/source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running it.
5. Re-run `scripts/enumerate_oq_rulings.py` and compare the counts with
   `evidence/M22/oq_rulings_enumeration.json`.
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
