# M11 · infrastructure — implementer review record

Card M11 (`infrastructure`), Parent I-10, title `计费量与费率`. Attempt `execution_runs/M11/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded
> as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; both files hash-equal to the task anchors | `binding.json`, `evidence/M11/source_manifest.json` |
| B positive | actual `[210.0]` vs independent oracle `[210.0]`, tolerance `[2.1e-07]` | `evidence/M11/formula_result.json` |
| continuity positive | actual `[210.0, 300.0]` vs oracle `[210.0, 300.0]` (run before the break patch) | `evidence/M11/negative_results.json` |
| defaults case | actual `[200.0]` vs oracle `[200.0]` | `evidence/M11/negative_results.json` |
| C negatives | 11/11 rejected with the frozen expected exception type | `evidence/M11/negative_results.json` |
| D mapping | source survey + all-missing mapping skeleton only; professional decisions PROPOSED, unsigned | `evidence/M11/disclosure_source_survey.json`, `disclosure_mapping.json`, `accounting_decision.md` |
| E wiring | **NOT done** - owned by I-10-A after D | `evidence/M11/deferred_work.json` |
| F accuracy | **NOT done** - needs the I-12 frozen design | `evidence/M11/qualification.json` |
| exit code | runner rc = **0** (pass); the runner carries the verdict | `evidence/M11/run_result.json`, `after/rc_ledger.txt` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_cards_M09_M12.py`, whose imports are only
  `argparse`, `hashlib`, `json`, `os` and `decimal` (see `import_lines` in
  `evidence/M11/oracle_selfcheck.json`; `product_import_present` is `false`).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads every expectation only
  from `evidence/M11/oracle.json`.
- `evidence/M11/regeneration_check.json` and `after/console_A4-M11-oracle-regenerate-compare_M11.txt`
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

- Registry formula observed from the isolated copy: `revenue = billable_volume * tariff + other_revenue`
- required `['billable_volume', 'tariff']`; optional `['other_revenue']`
- declared defaults `{}`; ratio drivers
  `[]`; explicit driver bounds
  `{}`
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
| NEG-CARD | `set_driver_element` | ModelRegistryError | `driver infrastructure.billable_volume must be between 0.0 and inf: FY2027` | PASS_rejected |
| N01a | `set_driver_element` | ModelRegistryError | `infrastructure.billable_volume.FY2027 must be numeric` | PASS_rejected |
| N01b | `set_driver_element` | ModelRegistryError | `infrastructure.billable_volume.FY2027 must be finite` | PASS_rejected |
| N01c | `set_driver_element` | ModelRegistryError | `infrastructure.billable_volume.FY2027 must be finite` | PASS_rejected |
| N01d | `set_driver_element` | ModelRegistryError | `infrastructure.billable_volume.FY2027 must be finite` | PASS_rejected |
| N02 | `set_driver` | ModelRegistryError | `driver infrastructure.billable_volume must contain one value per forecast year` | PASS_rejected |
| N03 | `delete_driver` | ModelRegistryError | `missing drivers for infrastructure: billable_volume` | PASS_rejected |
| N04 | `add_driver` | ModelRegistryError | `unsupported drivers for infrastructure: unknown_driver` | PASS_rejected |
| N05a | `set_years` | ModelRegistryError | `infrastructure.years must contain fiscal years` | PASS_rejected |
| N05b | `set_years` | ModelRegistryError | `infrastructure.years must contain fiscal years` | PASS_rejected |
| CONT-BREAK | `set_years` | ModelRegistryError | `infrastructure.years must be consecutive and increasing` | PASS_rejected |

Observations (measured, **not** part of the exit code):

| id | raised / actual | expectation matched | compared-to match | message |
|---|---|---|---|---|
| OBS-BASE-IGNORED | [210.0] | yes | True |  |
| OBS-TARIFF-NEG | ModelRegistryError | yes | None | driver infrastructure.tariff must be between 0.0 and inf: FY2027 |

## 4. Exit-code mutation self-check (red then green)

| case | mutation (applied to a scratch copy only) | raw rc | expected rc | result |
|---|---|---|---|---|
| A | positive.expected_float [210.0] -> [999.0] | **2** | 2 | as expected |
| B | cases.json NEG-CARD expected -> TypeError | **3** | 3 | as expected |
| C | cases.json NEG-CARD neutralised to a no-op (base_revenue = 0) | **3** | 3 | as expected |
| D | oracle.json positive.expected_float deleted (expectation missing) | **2** | 2 | as expected |
| E | none (uncorrupted control copy) | **0** | 0 | as expected |

- `frozen_evidence_not_modified`: `True`;
  `product_sha256_unchanged`: `True`.
- Case E is the uncorrupted control: the same frozen evidence returns rc 0 again.
- Details: `recovery/selfcheck_result.json` (each scratch tree keeps its own `stdout.txt`).

## 5. Judgement calls the reviewer should attack first

1. **The card-specific negative is a value-domain refusal.** `billable_volume = [-1]` is rejected by `driver infrastructure.billable_volume must be between 0.0 and inf: FY2027`.
2. **A negative tariff cannot be expressed.** OBS-TARIFF-NEG records the driver-domain guard (`infrastructure.tariff must be between 0.0 and inf`); a rebate-style negative tariff has no representation at this entry point. Registered as OQ-3.
3. **No local source document supports this card's industry.** The survey lists the nearest available names (equipment, design institute, property, landscaping, equipment rental) and why each is the wrong contract. D therefore cannot even reach a mapping decision here.
4. **The tier / effective-date question is not testable in this model.** DEC-M11-2 has to be adjudicated in the mapping; the formula is linear in one tariff per year.
5. **Silent zero-fill of `other_revenue`.** Omitted means 0.0 with no disclosure backing (OQ-1).

## 6. What this card does NOT claim

- It does not claim the model is accurate, nor that one company's mapping generalises.
- It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review.
- It does not rewrite the formula; the existing implementation is retained.

## 7. Disclosure adaptation status (D)

The card's own business negatives are still open and no industry/accounting reviewer has signed anything:

- throughput is not automatically fully billable
- subsidies and capacity charges must not be added twice

Therefore `disclosure_adaptation` stays `unmapped`; `evidence/M11/disclosure_mapping.json` lists every
driver as `missing` with the fields that would have to be filled, and no value was invented.

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_cards_M09_M12.py --card M11 --out-root <scratch>` and diff `oracle.json`
   against the frozen one (or read `regeneration_check.json` and then reproduce it independently).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm rc 0, the positive
   `[210.0]`, continuity `[210.0, 300.0]` and `11/11`
   rejections.
3. Confirm the isolated copies still hash-equal the task anchors (`source_manifest.json`, `integrity.json`)
   and read the mtime finding in `integrity.json` about production files touched by an external writer.
4. Pick a case the implementer did not use - for example a three-year path, a unit-scale change, or a
   driver value at a bound - freeze its expectation BEFORE running, and check it.
5. Adjudicate the DEC items in `evidence/M11/accounting_decision.md` and the OQ items in
   `evidence/M11/oq_rulings.json`.

## 9. Final batch verification

- `after/final_audit.txt`, produced by `scripts/final_audit.py`, reports **`failures: none`** across
  M09-M12. For this card it records rc `0`, positive `[210.0]`, continuity
  `[210.0, 300.0]`, defaults `[200.0]`, `11/11` negatives
  rejected, `2/2` observations matching their frozen expectations and
  `25` printed-value-vs-evidence-file consistency checks (all passing).
- The audit re-checks the freeze ordering (`oracle.md` < `oracle.json` < `stdout.txt`), the three
  qualification states, the empty revision-r2 slot (`revision_r2.json`) and that `iso/checkout_scripts`
  still hashes equal to the production files.
- `evidence/M11/evidence_hashes.json` (119 files) excludes the three **self-referential**
  hash files by name (`evidence_hashes.json`, `artifact_hashes.txt`, `after/rerun_sha256.json`) and names
  the artefacts written after the snapshot (`after/rc_ledger.txt`, the finalize-pass console,
  `after/final_audit.txt`). Everything else in the attempt is inside the snapshot.
- Closing attempts that failed on the way here were not erased: their raw consoles are preserved with a
  `_FAILED_first_attempt` suffix under `after/`.
- `decision.md` section "Owner hand-off" points at `handoff.json` (`open_questions`, `next_action`,
  `blocked_by`) as the authoritative continuation record.
