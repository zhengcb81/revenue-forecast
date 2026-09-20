# M10 · reserve_depletion — implementer review record

Card M10 (`reserve_depletion`), Parent I-10, title `储量消耗桥`. Attempt `execution_runs/M10/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded
> as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; both files hash-equal to the task anchors | `binding.json`, `evidence/M10/source_manifest.json` |
| B positive | actual `[490.0]` vs independent oracle `[490.0]`, tolerance `[4.9e-07]` | `evidence/M10/formula_result.json` |
| continuity positive | actual `[490.0, 0.0]` vs oracle `[490.0, 0.0]` (run before the break patch) | `evidence/M10/negative_results.json` |
| defaults case | actual `[600.0]` vs oracle `[600.0]` | `evidence/M10/negative_results.json` |
| C negatives | 11/11 rejected with the frozen expected exception type | `evidence/M10/negative_results.json` |
| D mapping | source survey + all-missing mapping skeleton only; professional decisions PROPOSED, unsigned | `evidence/M10/disclosure_source_survey.json`, `disclosure_mapping.json`, `accounting_decision.md` |
| E wiring | **NOT done** - owned by I-10-A after D | `evidence/M10/deferred_work.json` |
| F accuracy | **NOT done** - needs the I-12 frozen design | `evidence/M10/qualification.json` |
| exit code | runner rc = **0** (pass); the runner carries the verdict | `evidence/M10/run_result.json`, `after/rc_ledger.txt` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_cards_M09_M12.py`, whose imports are only
  `argparse`, `hashlib`, `json`, `os` and `decimal` (see `import_lines` in
  `evidence/M10/oracle_selfcheck.json`; `product_import_present` is `false`).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads every expectation only
  from `evidence/M10/oracle.json`.
- `evidence/M10/regeneration_check.json` and `after/console_A4-M10-oracle-regenerate-compare_M10.txt`
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

- Registry formula observed from the isolated copy: `revenue = depletion * recovery_rate * realized_price + other_revenue`
- required `['opening_reserves', 'additions', 'depletion', 'closing_reserves', 'recovery_rate', 'realized_price']`; optional `['other_revenue', 'reserve_revisions']`
- declared defaults `{}`; ratio drivers
  `['recovery_rate']`; explicit driver bounds
  `{'reserve_revisions': [None, None]}`
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
| NEG-CARD | `set_driver` | ModelRegistryError | `reserve stock-flow balance failed: FY2027` | PASS_rejected |
| N01a | `set_driver_element` | ModelRegistryError | `reserve_depletion.opening_reserves.FY2027 must be numeric` | PASS_rejected |
| N01b | `set_driver_element` | ModelRegistryError | `reserve_depletion.opening_reserves.FY2027 must be finite` | PASS_rejected |
| N01c | `set_driver_element` | ModelRegistryError | `reserve_depletion.opening_reserves.FY2027 must be finite` | PASS_rejected |
| N01d | `set_driver_element` | ModelRegistryError | `reserve_depletion.opening_reserves.FY2027 must be finite` | PASS_rejected |
| N02 | `set_driver` | ModelRegistryError | `driver reserve_depletion.opening_reserves must contain one value per forecast year` | PASS_rejected |
| N03 | `delete_driver` | ModelRegistryError | `missing drivers for reserve_depletion: opening_reserves` | PASS_rejected |
| N04 | `add_driver` | ModelRegistryError | `unsupported drivers for reserve_depletion: unknown_driver` | PASS_rejected |
| N05a | `set_years` | ModelRegistryError | `reserve_depletion.years must contain fiscal years` | PASS_rejected |
| N05b | `set_years` | ModelRegistryError | `reserve_depletion.years must contain fiscal years` | PASS_rejected |
| CONT-BREAK | `set_driver_multi` | ModelRegistryError | `reserve continuity failed: FY2028` | PASS_rejected |

Observations (measured, **not** part of the exit code):

| id | raised / actual | expectation matched | compared-to match | message |
|---|---|---|---|---|
| OBS-BASE-IGNORED | [490.0] | yes | True |  |
| OBS-DEFAULT-EQUIV | [600.0] | yes | True |  |
| OBS-REVISION-POS | [490.0] | yes | None |  |
| OBS-RECOVERY-GT1 | ModelRegistryError | yes | None | driver reserve_depletion.recovery_rate must be between 0.0 and 1.0: FY2027 |

## 4. Exit-code mutation self-check (red then green)

| case | mutation (applied to a scratch copy only) | raw rc | expected rc | result |
|---|---|---|---|---|
| A | positive.expected_float [490.0] -> [999.0] | **2** | 2 | as expected |
| B | cases.json NEG-CARD expected -> TypeError | **3** | 3 | as expected |
| C | cases.json NEG-CARD neutralised to a no-op (base_revenue = 0) | **3** | 3 | as expected |
| D | oracle.json positive.expected_float deleted (expectation missing) | **2** | 2 | as expected |
| E | none (uncorrupted control copy) | **0** | 0 | as expected |

- `frozen_evidence_not_modified`: `True`;
  `product_sha256_unchanged`: `True`.
- Case E is the uncorrupted control: the same frozen evidence returns rc 0 again.
- Details: `recovery/selfcheck_result.json` (each scratch tree keeps its own `stdout.txt`).

## 5. Judgement calls the reviewer should attack first

1. **The two card gates are different code paths and both are exercised.** NEG-CARD trips the self-balance guard (`reserve stock-flow balance failed: FY2027`); CONT-BREAK trips the cross-year guard (`reserve continuity failed: FY2028`) while each year still balances on its own - exactly the case the card describes.
2. **The continuity negative is the card's own patch, applied only after the two-year positive passed.** `cases.json` records the ordering (`continuity_then_break_order`) and the runner's `continuity_positive.ran_before_negative_patch` flag is true.
3. **The defaults case had to be designed, not copied.** Omitting `reserve_revisions` forces 0, so the card's positive input would fail the balance test; the frozen defaults case changes `depletion` to 250 so the identity still holds. A reviewer should check that this is a legitimate defaults probe and not a smuggled input change.
4. **Silent zero-fill is dangerous for `reserve_revisions`.** With `model_registry.py:335`, `no revision` and `we did not find the revision` become indistinguishable and the missing revision silently becomes balance. Registered as OQ-1, no product change.
5. **OBS-REVISION-POS shows revisions do not enter revenue** (490 before and after a +50 revision that keeps the balance). A reviewer should confirm this is the intended contract: the model prices depletion, not the reserve movement.
6. **Disclosure adaptation is 0/8 drivers.** The survey found a real local mining annual report; no reserve-class page/span extraction and no closed-period reconciliation was performed.

## 6. What this card does NOT claim

- It does not claim the model is accurate, nor that one company's mapping generalises.
- It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review.
- It does not rewrite the formula or move any gate; the existing implementation is retained.

## 7. Disclosure adaptation status (D)

The card's own business negatives are still open and no industry/accounting reviewer has signed anything:

- reserves that already embed the recovery factor must not be multiplied by it again
- depletion does not automatically equal current-period sales

Therefore `disclosure_adaptation` stays `unmapped`; `evidence/M10/disclosure_mapping.json` lists every
driver as `missing` with the fields that would have to be filled, and no value was invented.

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_cards_M09_M12.py --card M10 --out-root <scratch>` and diff `oracle.json`
   against the frozen one (or read `regeneration_check.json` and then reproduce it independently).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm rc 0, the positive
   `[490.0]`, continuity `[490.0, 0.0]` and `11/11`
   rejections.
3. Confirm the isolated copies still hash-equal the task anchors (`source_manifest.json`, `integrity.json`)
   and read the mtime finding in `integrity.json` about production files touched by an external writer.
4. Pick a case the implementer did not use - for example a three-year path, a unit-scale change, or a
   driver value at a bound - freeze its expectation BEFORE running, and check it.
5. Adjudicate the DEC items in `evidence/M10/accounting_decision.md` and the OQ items in
   `evidence/M10/oq_rulings.json`.

## 9. Final batch verification

- `after/final_audit.txt`, produced by `scripts/final_audit.py`, reports **`failures: none`** across
  M09-M12. For this card it records rc `0`, positive `[490.0]`, continuity
  `[490.0, 0.0]`, defaults `[600.0]`, `11/11` negatives
  rejected, `4/4` observations matching their frozen expectations and
  `25` printed-value-vs-evidence-file consistency checks (all passing).
- The audit re-checks the freeze ordering (`oracle.md` < `oracle.json` < `stdout.txt`), the three
  qualification states, the empty revision-r2 slot (`revision_r2.json`) and that `iso/checkout_scripts`
  still hashes equal to the production files.
- `evidence/M10/evidence_hashes.json` (119 files) excludes the three **self-referential**
  hash files by name (`evidence_hashes.json`, `artifact_hashes.txt`, `after/rerun_sha256.json`) and names
  the artefacts written after the snapshot (`after/rc_ledger.txt`, the finalize-pass console,
  `after/final_audit.txt`). Everything else in the attempt is inside the snapshot.
- Closing attempts that failed on the way here were not erased: their raw consoles are preserved with a
  `_FAILED_first_attempt` suffix under `after/`.
- `decision.md` section "Owner hand-off" points at `handoff.json` (`open_questions`, `next_action`,
  `blocked_by`) as the authoritative continuation record.
