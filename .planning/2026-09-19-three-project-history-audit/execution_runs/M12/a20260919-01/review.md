# M12 · bank_revenue — implementer review record

Card M12 (`bank_revenue`), Parent I-10, title `银行净利息与手续费`. Attempt `execution_runs/M12/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded
> as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; both files hash-equal to the task anchors | `binding.json`, `evidence/M12/source_manifest.json` |
| B positive | actual `[34.0]` vs independent oracle `[34.0]`, tolerance `[3.4e-08]` | `evidence/M12/formula_result.json` |
| continuity positive | actual `[34.0, 38.0]` vs oracle `[34.0, 38.0]` (run before the break patch) | `evidence/M12/negative_results.json` |
| defaults case | actual `[32.0]` vs oracle `[32.0]` | `evidence/M12/negative_results.json` |
| C negatives | 11/11 rejected with the frozen expected exception type | `evidence/M12/negative_results.json` |
| D mapping | source survey + all-missing mapping skeleton only; professional decisions PROPOSED, unsigned | `evidence/M12/disclosure_source_survey.json`, `disclosure_mapping.json`, `accounting_decision.md` |
| E wiring | **NOT done** - owned by I-10-A after D | `evidence/M12/deferred_work.json` |
| F accuracy | **NOT done** - needs the I-12 frozen design | `evidence/M12/qualification.json` |
| exit code | runner rc = **0** (pass); the runner carries the verdict | `evidence/M12/run_result.json`, `after/rc_ledger.txt` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_cards_M09_M12.py`, whose imports are only
  `argparse`, `hashlib`, `json`, `os` and `decimal` (see `import_lines` in
  `evidence/M12/oracle_selfcheck.json`; `product_import_present` is `false`).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads every expectation only
  from `evidence/M12/oracle.json`.
- `evidence/M12/regeneration_check.json` and `after/console_A4-M12-oracle-regenerate-compare_M12.txt`
  show that re-running the generator into a different root reproduces `input.json`, `oracle.json`,
  `cases.json`, `observation_expected.json` and `oracle_selfcheck.json` **byte for byte**.
- Negative cases and observations are built in memory from a fresh `deepcopy` of the frozen input - never
  round-tripped through a JSON parser - so a parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires the raised exception to be an instance of `ModelRegistryError` **and** to match
  the exception name frozen in `cases.json`. `ImportError`, `ModuleNotFoundError`, `FileNotFoundError` and
  every other type are recorded as FAIL, never as pass.
- The same `scripts/run_card.py` (sha256 `997c553b0b9e6452e9edfeb8bfec3a40ff55d10f2646e562456913feb9332fce`)
  is used by all four attempts of this batch, and the same generator
  (sha256 `54f3cdb1cfbd3d0cd7bb4b4fce0891288555cf6ae30dfdab32a87fdc8088e635`) generates all four
  oracles, so there is no per-card runner or generator to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = average_earning_assets * asset_yield - average_interest_bearing_liabilities * funding_cost + fee_revenue + other_revenue`
- required `['average_earning_assets', 'asset_yield', 'average_interest_bearing_liabilities', 'funding_cost', 'fee_revenue']`; optional `['other_revenue']`
- declared defaults `{}`; ratio drivers
  `['asset_yield', 'funding_cost']`; explicit driver bounds
  `{'asset_yield': [None, None], 'funding_cost': [None, None]}`
- contract fidelity (formula string, required/optional sets, dimensions) `True`
- positive structure: container `list`, length
  `1` = len(years) `True`, element types
  `['float']`, all finite `True`
- The contract returns a bare `list[float]` positionally aligned with `years`, so there is no named output
  field set; the "field set" requirement is realised as container type + element type set + length/order,
  and the oracle `years` equal the input `years` (`fidelity_checks.years_match`).

Rejections exactly as recorded (message text is read back from `negative_results.json`):

| case | mutation kind | expected | actual message | verdict |
|---|---|---|---|---|
| NEG-CARD | `set_driver_multi` | ModelRegistryError | `calculated revenue cannot be negative: bank_revenue` | PASS_rejected |
| N01a | `set_driver_element` | ModelRegistryError | `bank_revenue.average_earning_assets.FY2027 must be numeric` | PASS_rejected |
| N01b | `set_driver_element` | ModelRegistryError | `bank_revenue.average_earning_assets.FY2027 must be finite` | PASS_rejected |
| N01c | `set_driver_element` | ModelRegistryError | `bank_revenue.average_earning_assets.FY2027 must be finite` | PASS_rejected |
| N01d | `set_driver_element` | ModelRegistryError | `bank_revenue.average_earning_assets.FY2027 must be finite` | PASS_rejected |
| N02 | `set_driver` | ModelRegistryError | `driver bank_revenue.average_earning_assets must contain one value per forecast year` | PASS_rejected |
| N03 | `delete_driver` | ModelRegistryError | `missing drivers for bank_revenue: average_earning_assets` | PASS_rejected |
| N04 | `add_driver` | ModelRegistryError | `unsupported drivers for bank_revenue: unknown_driver` | PASS_rejected |
| N05a | `set_years` | ModelRegistryError | `bank_revenue.years must contain fiscal years` | PASS_rejected |
| N05b | `set_years` | ModelRegistryError | `bank_revenue.years must contain fiscal years` | PASS_rejected |
| CONT-BREAK | `set_years` | ModelRegistryError | `bank_revenue.years must be consecutive and increasing` | PASS_rejected |

Observations (measured, **not** part of the exit code):

| id | raised / actual | expectation matched | compared-to match | message |
|---|---|---|---|---|
| OBS-BASE-IGNORED | [34.0] | yes | True |  |
| OBS-NEG-RATE-ACCEPTED | [0.0] | yes | None |  |
| OBS-NEG-RATE-TOTAL-NEG | ModelRegistryError | yes | None | calculated revenue cannot be negative: bank_revenue |
| OBS-FEE-SIGNED | [21.0] | yes | None |  |
| OBS-RATE-GT1 | [494.0] | yes | None |  |

## 4. Exit-code mutation self-check (red then green)

| case | mutation (applied to a scratch copy only) | raw rc | expected rc | result |
|---|---|---|---|---|
| A | positive.expected_float [34.0] -> [999.0] | **2** | 2 | as expected |
| B | cases.json NEG-CARD expected -> TypeError | **3** | 3 | as expected |
| C | cases.json NEG-CARD neutralised to a no-op (base_revenue = 0) | **3** | 3 | as expected |
| D | oracle.json positive.expected_float deleted (expectation missing) | **2** | 2 | as expected |
| E | none (uncorrupted control copy) | **0** | 0 | as expected |

- `frozen_evidence_not_modified`: `True`;
  `product_sha256_unchanged`: `True`.
- Case E is the uncorrupted control: the same frozen evidence returns rc 0 again.
- Details: `recovery/selfcheck_result.json` (each scratch tree keeps its own `stdout.txt`).

## 5. Judgement calls the reviewer should attack first

1. **The card's negative is a totals refusal, not a rate refusal.** NEG-CARD yields 0 - 80 + 0 + 0 = -80 and is rejected by `calculated revenue cannot be negative`. A reviewer must not read it as `rates must be positive`.
2. **The negative-rate pair is the sharpest evidence in this card.** OBS-NEG-RATE-ACCEPTED (`asset_yield = -0.01` with a total of exactly 0) is ACCEPTED, while OBS-NEG-RATE-TOTAL-NEG (same rate, total -16) is refused. Together they isolate the binding guard to the revenue total.
3. **OBS-RATE-GT1 (yield 0.5 -> 494) shows the ratio dimension's default [0, 1] does not apply to `asset_yield`.** The enumeration confirms both rate drivers carry explicit `(None, None)` bounds.
4. **`fee_revenue` is signed** (OBS-FEE-SIGNED, -5 -> 21), so a negative net fee is representable; a reviewer should confirm that is the intended contract for fee reversals.
5. **The totals guard is a real adapter limit, not a theoretical one.** A bank year with a net interest loss cannot be represented; DEC-M12-3 asks the owner for a ruling instead of a workaround.
6. **No local source document supports this card's industry.** The survey lists the two securities firms and two insurers available locally and why their revenue contracts differ.
7. **Silent zero-fill of `other_revenue`** (OQ-1).

## 6. What this card does NOT claim

- It does not claim the model is accurate, nor that one company's mapping generalises.
- It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review.
- It does not rewrite the formula or relax the totals guard; the existing implementation is retained.

## 7. Disclosure adaptation status (D)

The card's own business negatives are still open and no industry/accounting reviewer has signed anything:

- negative interest rates are allowed and must not be re-bounded to 0-1
- net interest margin (NIM) is not the asset yield
- a negative total revenue is not supported by the current contract

Therefore `disclosure_adaptation` stays `unmapped`; `evidence/M12/disclosure_mapping.json` lists every
driver as `missing` with the fields that would have to be filled, and no value was invented.

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_cards_M09_M12.py --card M12 --out-root <scratch>` and diff `oracle.json`
   against the frozen one (or read `regeneration_check.json` and then reproduce it independently).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm rc 0, the positive
   `[34.0]`, continuity `[34.0, 38.0]` and `11/11`
   rejections.
3. Confirm the isolated copies still hash-equal the task anchors (`source_manifest.json`, `integrity.json`)
   and read the mtime finding in `integrity.json` about production files touched by an external writer.
4. Pick a case the implementer did not use - for example a three-year path, a unit-scale change, or a
   driver value at a bound - freeze its expectation BEFORE running, and check it.
5. Adjudicate the DEC items in `evidence/M12/accounting_decision.md` and the OQ items in
   `evidence/M12/oq_rulings.json`.

## 9. Final batch verification

- `after/final_audit.txt`, produced by `scripts/final_audit.py`, reports **`failures: none`** across
  M09-M12. For this card it records rc `0`, positive `[34.0]`, continuity
  `[34.0, 38.0]`, defaults `[32.0]`, `11/11` negatives
  rejected, `5/5` observations matching their frozen expectations and
  `25` printed-value-vs-evidence-file consistency checks (all passing).
- The audit re-checks the freeze ordering (`oracle.md` < `oracle.json` < `stdout.txt`), the three
  qualification states, the empty revision-r2 slot (`revision_r2.json`) and that `iso/checkout_scripts`
  still hashes equal to the production files.
- `evidence/M12/evidence_hashes.json` (119 files) excludes the three **self-referential**
  hash files by name (`evidence_hashes.json`, `artifact_hashes.txt`, `after/rerun_sha256.json`) and names
  the artefacts written after the snapshot (`after/rc_ledger.txt`, the finalize-pass console,
  `after/final_audit.txt`). Everything else in the attempt is inside the snapshot.
- Closing attempts that failed on the way here were not erased: their raw consoles are preserved with a
  `_FAILED_first_attempt` suffix under `after/`.
- `decision.md` section "Owner hand-off" points at `handoff.json` (`open_questions`, `next_action`,
  `blocked_by`) as the authoritative continuation record.
