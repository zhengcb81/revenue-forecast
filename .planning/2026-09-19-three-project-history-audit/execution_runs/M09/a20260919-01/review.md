# M09 · resource — implementer review record

Card M09 (`resource`), Parent I-10, title `资源销售量与实售价`. Attempt `execution_runs/M09/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded
> as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; both files hash-equal to the task anchors | `binding.json`, `evidence/M09/source_manifest.json` |
| B positive | actual `[122.0]` vs independent oracle `[122.0]`, tolerance `[1.22e-07]` | `evidence/M09/formula_result.json` |
| continuity positive | actual `[122.0, 225.0]` vs oracle `[122.0, 225.0]` (run before the break patch) | `evidence/M09/negative_results.json` |
| defaults case | actual `[120.0]` vs oracle `[120.0]` | `evidence/M09/negative_results.json` |
| C negatives | 11/11 rejected with the frozen expected exception type | `evidence/M09/negative_results.json` |
| D mapping | source survey + all-missing mapping skeleton only; professional decisions PROPOSED, unsigned | `evidence/M09/disclosure_source_survey.json`, `disclosure_mapping.json`, `accounting_decision.md` |
| E wiring | **NOT done** - owned by I-10-A after D | `evidence/M09/deferred_work.json` |
| F accuracy | **NOT done** - needs the I-12 frozen design | `evidence/M09/qualification.json` |
| exit code | runner rc = **0** (pass); the runner carries the verdict | `evidence/M09/run_result.json`, `after/rc_ledger.txt` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_cards_M09_M12.py`, whose imports are only
  `argparse`, `hashlib`, `json`, `os` and `decimal` (see `import_lines` in
  `evidence/M09/oracle_selfcheck.json`; `product_import_present` is `false`).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads every expectation only
  from `evidence/M09/oracle.json`.
- `evidence/M09/regeneration_check.json` and `after/console_A4-M09-oracle-regenerate-compare_M09.txt`
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

- Registry formula observed from the isolated copy: `revenue = saleable_volume * realized_price + other_revenue`
- required `['saleable_volume', 'realized_price']`; optional `['other_revenue']`
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
| NEG-CARD | `set_driver_element` | ModelRegistryError | `driver resource.saleable_volume must be between 0.0 and inf: FY2027` | PASS_rejected |
| N01a | `set_driver_element` | ModelRegistryError | `resource.saleable_volume.FY2027 must be numeric` | PASS_rejected |
| N01b | `set_driver_element` | ModelRegistryError | `resource.saleable_volume.FY2027 must be finite` | PASS_rejected |
| N01c | `set_driver_element` | ModelRegistryError | `resource.saleable_volume.FY2027 must be finite` | PASS_rejected |
| N01d | `set_driver_element` | ModelRegistryError | `resource.saleable_volume.FY2027 must be finite` | PASS_rejected |
| N02 | `set_driver` | ModelRegistryError | `driver resource.saleable_volume must contain one value per forecast year` | PASS_rejected |
| N03 | `delete_driver` | ModelRegistryError | `missing drivers for resource: saleable_volume` | PASS_rejected |
| N04 | `add_driver` | ModelRegistryError | `unsupported drivers for resource: unknown_driver` | PASS_rejected |
| N05a | `set_years` | ModelRegistryError | `resource.years must contain fiscal years` | PASS_rejected |
| N05b | `set_years` | ModelRegistryError | `resource.years must contain fiscal years` | PASS_rejected |
| CONT-BREAK | `set_years` | ModelRegistryError | `resource.years must be consecutive and increasing` | PASS_rejected |

Observations (measured, **not** part of the exit code):

| id | raised / actual | expectation matched | compared-to match | message |
|---|---|---|---|---|
| OBS-BASE-IGNORED | [122.0] | yes | True |  |
| OBS-PRICE-NEG | ModelRegistryError | yes | None | driver resource.realized_price must be between 0.0 and inf: FY2027 |

## 4. Exit-code mutation self-check (red then green)

| case | mutation (applied to a scratch copy only) | raw rc | expected rc | result |
|---|---|---|---|---|
| A | positive.expected_float [122.0] -> [999.0] | **2** | 2 | as expected |
| B | cases.json NEG-CARD expected -> TypeError | **3** | 3 | as expected |
| C | cases.json NEG-CARD neutralised to a no-op (base_revenue = 0) | **3** | 3 | as expected |
| D | oracle.json positive.expected_float deleted (expectation missing) | **2** | 2 | as expected |
| E | none (uncorrupted control copy) | **0** | 0 | as expected |

- `frozen_evidence_not_modified`: `True`;
  `product_sha256_unchanged`: `True`.
- Case E is the uncorrupted control: the same frozen evidence returns rc 0 again.
- Details: `recovery/selfcheck_result.json` (each scratch tree keeps its own `stdout.txt`).

## 5. Judgement calls the reviewer should attack first

1. **The card-specific negative is a value-domain refusal, not a length refusal.** `saleable_volume = [-1]` is rejected by `driver resource.saleable_volume must be between 0.0 and inf: FY2027`. The same batch's r1 was rejected for a negative case that actually tripped the length guard; this one does not.
2. **A negative realized price cannot be expressed.** OBS-PRICE-NEG shows the driver-domain guard fires first (`resource.realized_price must be between 0.0 and inf`); the totals guard would also refuse the resulting -28. For a commodity that can trade negative (for example the April-2020 crude episode) the current entry point cannot express it. Registered as OQ-3, no product change.
3. **Silent zero-fill of `other_revenue`.** `scripts/model_registry.py:335` turns an omitted optional driver with no declared default into 0.0. For this model that asserts `no other revenue` without any disclosure saying so. Registered as OQ-1.
4. **The 'no mixed tonnes' rule cannot be tested at runtime.** The model has no unit field, so oracle.md R7/R8/R9 are professional gates; a reviewer should not read their absence from the negative list as coverage.
5. **Disclosure adaptation is 0/1 drivers (nothing mapped).** Both required drivers are still `missing`; the survey found a real local mining annual report, but no page/span extraction and no closed-period reconciliation was performed.

## 6. What this card does NOT claim

- It does not claim the model is accurate, nor that one company's mapping generalises.
- It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a production forecast-entry-point mapping reviewed independently.
- It does not rewrite the formula. With no independent counter-example and no adjudicated specification, the existing implementation is retained.

## 7. Disclosure adaptation status (D)

The card's own business negatives are still open and no industry/accounting reviewer has signed anything:

- recovery / payability / treatment-charge may be deducted exactly once
- production volume is not sales volume
- ore tonnes, concentrate tonnes and metal tonnes must not be mixed

Therefore `disclosure_adaptation` stays `unmapped`; `evidence/M09/disclosure_mapping.json` lists every
driver as `missing` with the fields that would have to be filled, and no value was invented.

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_cards_M09_M12.py --card M09 --out-root <scratch>` and diff `oracle.json`
   against the frozen one (or read `regeneration_check.json` and then reproduce it independently).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm rc 0, the positive
   `[122.0]`, continuity `[122.0, 225.0]` and `11/11`
   rejections.
3. Confirm the isolated copies still hash-equal the task anchors (`source_manifest.json`, `integrity.json`)
   and read the mtime finding in `integrity.json` about production files touched by an external writer.
4. Pick a case the implementer did not use - for example a three-year path, a unit-scale change, or a
   driver value at a bound - freeze its expectation BEFORE running, and check it.
5. Adjudicate the DEC items in `evidence/M09/accounting_decision.md` and the OQ items in
   `evidence/M09/oq_rulings.json`.

## 9. Final batch verification

- `after/final_audit.txt`, produced by `scripts/final_audit.py`, reports **`failures: none`** across
  M09-M12. For this card it records rc `0`, positive `[122.0]`, continuity
  `[122.0, 225.0]`, defaults `[120.0]`, `11/11` negatives
  rejected, `2/2` observations matching their frozen expectations and
  `25` printed-value-vs-evidence-file consistency checks (all passing).
- The audit re-checks the freeze ordering (`oracle.md` < `oracle.json` < `stdout.txt`), the three
  qualification states, the empty revision-r2 slot (`revision_r2.json`) and that `iso/checkout_scripts`
  still hashes equal to the production files.
- `evidence/M09/evidence_hashes.json` (122 files) excludes the three **self-referential**
  hash files by name (`evidence_hashes.json`, `artifact_hashes.txt`, `after/rerun_sha256.json`) and names
  the artefacts written after the snapshot (`after/rc_ledger.txt`, the finalize-pass console,
  `after/final_audit.txt`). Everything else in the attempt is inside the snapshot.
- Closing attempts that failed on the way here were not erased: their raw consoles are preserved with a
  `_FAILED_first_attempt` suffix under `after/`.
- `decision.md` section "Owner hand-off" points at `handoff.json` (`open_questions`, `next_action`,
  `blocked_by`) as the authoritative continuation record.

## 独立验收裁定（M-T-REVIEW 点复审 · 2026-09-23）
- 结论：accepted_with_conditions —— 仅 formula、仅本 attempt、仅锚 9ec65295…。
- 既有终裁载体（采信）：独立 reviewer 报告 sha256 5a44fd4e1e4dca5f…（40679 B）「## 1. 结论汇总」M09 行
  「| M09 | resource | accepted_scoped | 仅 formula |」+ 卡内逐字副本 evidence/M09/reviewer_report_m09m12.md。
- 本块即 owed 的卡内裁决区补录（追加式，附前缀哈希证明）；in_card_transcription_owed 由此清账。
- carried：F-MT-02/03/04（由本块闭合）。本次抽验：[122] 三方一致；负例 11/11；九件齐；pin 3/3（LF 直配）；无产品重写。
- status_authority: { status: "accepted_scoped", reviewer_status: "independent verdict transcribed in-card by M-T-REVIEW append (N=1) 2026-09-23: accepted_scoped (formula only); original carrier report 5a44fd4e…", carrier: "…/reviews/M09.md + acceptance_rulings.md#M09", implementer_signed: false, supersedes: "RESOLVED … in-card verdict region owed" }
— 独立审查员 M-T-REVIEW / N=1
- install_record (carrier landing batch 2026-09-23 | M-T-REVIEW/a20260923-01): append-only flip per landing_package/README.md; prefix proof: pre-append sha256 e01551c6f5c7dcf9a33261477e9dbe29faf4be3def6ee971f7cfe574f332225d over 11608 bytes, verified post-install as sha256 of the first 11608 bytes of this file (PASS/FAIL + post sha in install_log.jsonl); F-RV-02 block_sha256 = 84a766b5b8586e41518da11e7920d4318a0b98a961898f16f7471f27e6b434c0 = sha256 of the appended block body above (header ## 独立验收裁定 line through the signature line — 独立审查员 M-T-REVIEW / N=1, LF-terminated, 1086 bytes); F-RV-03 verdict_is_transcribed_not_authored: true; block transcribes the signed ruling carried by M-T-REVIEW/a20260923-01/reviews/M09.md (sha256 423766517b0e64a5197e0ac4b3a8452880db3d0b56f1cf8f05cff245865a67b8) + acceptance_rulings.md (sha256 257e47da5f2924c2f6079f093c6884aa8ecc37a6eab2ce044c7fc26130e5495b); installer authors no verdict and signs nothing (never self-sign)
