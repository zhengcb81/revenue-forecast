# M02 · implementer review record

Card M02 (`direct_revenue`), Parent I-10. Attempt `execution_runs/M02/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict.

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local isolated snapshot; hashes equal | `binding.json`, `evidence/M02/source_manifest.json` |
| B positive | `[80.0, 0.0, 120.0]` vs independent oracle `[80, 0, 120]`, all within tolerance | `evidence/M02/formula_result.json` |
| C negatives | 11/11 rejected with `ModelRegistryError`; continuity positive `[50, 60]` passes | `evidence/M02/negative_results.json` |
| D mapping | one real disclosed mapping (ZJ FY2025 consolidated revenue) with page/table/span/hash/unit/period; four decisions written as PROPOSED only | `evidence/M02/disclosure_mapping.json`, `evidence/M02/accounting_decision.md` |
| E probe | labelled `historical_mapping_probe` (identity wiring only) | `evidence/M02/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M02/qualification.json` |

## 2. Independence of the oracle

- `scripts/oracle_M02.py` imports only `json`, `os`, `decimal`. It never imports `model_registry`.
- `scripts/run_card.py` calls exactly one product function and reads expectations only from `oracle.json`.
- Negatives are in-memory `deepcopy` cases; JSON-parser rejections cannot masquerade as model rejections.
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`; import/file errors are recorded as FAIL.

## 3. Results in detail

- Registry formula string observed: `revenue[t] = direct_revenue[t]` — matches the frozen expectation.
- Positive: `[80.0, 0.0, 120.0]`. The middle value stayed exactly `0.0`, i.e. a zero is treated as data and
  not as a missing field that would attract a default.
- Continuity positive `[50, 60]`; break patch `years = [2027, 2029]` rejected with
  `direct_revenue.years must be consecutive and increasing`.
- Rejections: `NEG-CARD` → `driver direct_revenue.revenue must be between 0.0 and inf: FY2028`;
  `N01a` numeric; `N01b/c/d` finite; `N02` one value per forecast year;
  `N03` `missing drivers for direct_revenue: revenue`;
  `N04` `unsupported drivers for direct_revenue: unknown_driver`;
  `N05a/b` fiscal years.
- **Two design observations (recorded, not scored)**:
  - `BASE-INDEPENDENCE`: with `base_revenue = 999` the output is **identical** to the positive case, proving
    `base_revenue` is not a term of this model.
  - `OBS-NEG-BASE`: with `base_revenue = -5` the product still raises
    `ModelRegistryError: direct_revenue.base_revenue cannot be negative`, even though the value is unused.
    Raised as DEC-M02-3 for the reviewer; **no product change was made**.

## 4. Unit / dimension and rejection checks

- `revenue` is an amount; the model copies it, so input and output dimensions are identical by construction.
- Float exactness: `349,079,082,852 < 2**53`, so the IEEE754 input is exact — no rounding is introduced.
- Per-share vs total: not applicable (the field must be a total).
- Gross vs net: the mapping fixes the basis as consolidated gross operating revenue.
- Period alignment: one value per fiscal year, positionally aligned with `years`; the model performs no
  continuity check itself, which is why the `years` contract carries the whole burden.
- Rejection conditions R1-R8 in `oracle.md` §6; R1-R6 executed, R7-R8 are disclosure/business refusals.

## 5. Judgement calls the reviewer should attack first

1. **The reconciliation is a constructive identity.** The driver *is* the disclosed figure, so the residual is
   identically zero and carries no information. This attempt refuses to call that "reconciliation passed"
   (DEC-M02-2) because I-10-A item 3 forbids back-solving a parameter from revenue and then treating the
   same-formula result as verification.
2. **No driver means no causal content.** The card says the simple formula must not raise confidence; the
   mapping therefore records `not_decomposed_reason` and refuses to claim any explanation of the revenue path.
3. **`base_revenue` guard vs unused field.** Keep fail-closed validation (current behaviour) or ignore unused
   fields? Implementer position: keep the guard; the observation is recorded so the reviewer can overrule.
4. **I-00-B interpretation** — same deviation note as M01: I-00-B binds the isolation plan, so this attempt
   materialised its own byte-identical read-only snapshot rather than running from a tree that I-00-B created.
5. **The production forecast entry point was not exercised** (`calculate_model_path` is an I-10-A obligation);
   `evidence/M02/forecast_integration.json` records only read-only observations of the call site.

## 6. What this card does NOT claim

- No accuracy claim: the model has no growth driver, so forecast skill cannot be evaluated from its own output.
- No `disclosure_adaptation`: the mapping is a minimum, unsigned, and its reconciliation is an identity.
- No formula rewrite (card line 65).

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M02.py` and `scripts/run_card.py`; diff against the recorded results.
2. Confirm the isolated copy hash still equals the production hash.
3. Re-derive `349,079,082,852` from the FY2025 report page 15 yourself, and confirm the FY2024 comparative is
   the same figure as in the FY2024 report page 15 (no restatement bridge needed).
4. Pick an unused case (e.g. a two-year path with a very large value, or `revenue = [0]` with `years=[2030]`)
   and freeze the expectation before running.
5. Adjudicate DEC-M02-1..4 and SR-M02-A/B.

---

## revision r2 - response to the independent review (status stays `review_pending`)

The reviewer returned **accepted_scoped (formula only)** for M01-M04 with five required fixes and one
item reserved for adjudication. r2 changes **attempt-local files only**; no production repository was
touched and no oracle expectation, tolerance or disclosure figure was altered to make anything pass.

### Verdict-carrying exit code (F-M01-02)

| item | change | evidence |
|---|---|---|
| F-M01-02 | `scripts/run_card.py` no longer returns 0 unconditionally. It now returns **0** only when the positive path matches the independent oracle within tolerance, the continuity positive passes and **all** negative cases were rejected with `ModelRegistryError`; **2** if the harness could not produce a verdict; **3** if the verdict is negative. The JSON artefacts are still written before returning, so a non-zero exit never destroys evidence. `scripts/run_M01.py` was patched the same way (M01 only). | `scripts/run_card.py`, `evidence/M02/revision_r2.json`, `after/rerun_sha256.json` |
| re-run | the same `calculate_registered_model` call was re-executed unchanged | **raw rc = 0** (expected 0), `evidence/run_result.json/exit_code_semantics` = `verdict` / `exit_code` |

### Delivery completeness (F-M01-03)

- `after/rerun_sha256.json` + `after/rerun_stdout.txt` + `after/rerun_stderr.txt`: post-r2 re-run hashes.
- `recovery/README.md`: `not_applicable_with_reason` - this card is a pure in-process function with no durable state, lock, lease or partial publication to recover.
- `changes.diff`: explicit **no product change** statement; there is no diff to show by design.
- `before/git_status_revenue-forecast.txt` re-written as **UTF-8** (was UTF-16LE).
- `evidence/M02/first_run_forensics.json`: F-M01-01 record.

### Frozen expectations were NOT rewritten

`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body, and `evidence/M02/source_manifest.json.oracle_versions` now indexes the oracle document and script versions with hashes and timestamps.

### F-M02-01 - reserved for owner/specialist adjudication (not self-decided)

- The reviewer asked for the two behaviours to be written up rather than resolved. Both are recorded in `decision.md` DEC-M02-3 and in the appended r2 section of `evidence/M02/accounting_decision.md`: the validator rejects `base_revenue < 0` uniformly before dispatch, while `_direct_revenue` deletes the field and `_direct_growth` consumes it. Measured: `base_revenue = 999` leaves the output identical; `base_revenue = -5` still raises `ModelRegistryError`.
- No product change was made and no position is asserted; the item is carried in `handoff.json.open_questions` marked `requires_owner_or_specialist_ruling`.

### Status

- `formula`: still **`review_pending`** - the implementer does not sign acceptance.
- `disclosure_adaptation`: still **`unmapped`**.
- `accuracy`: still **`unproven`**.

#### Self-check: is the new exit code actually meaningful? (do not take it on trust)

`recovery/r2_exit_code_selfcheck/selfcheck_result.json` runs the **patched** harness against deliberately
corrupted copies of `oracle.json` / `cases.json` in a scratch tree, so the frozen evidence is untouched:

| case | mutation | raw rc | expected | what it proves |
|---|---|---|---|---|
| A | `oracle.json positive.expected_float -> [999,999,999]` | **3** | 3 | a corrupted expectation is no longer hidden behind a bookkeeping-only rc=0; the product itself still returned the correct path |
| B | `cases.json first case base_input -> 'no_such_block'` | **1** | non-zero | a harness defect cannot masquerade as a pass; it raises |
| C | none (the real card) | **0** | 0 | the repaired exit code stays 0 for a genuinely passing card |
| D (added in r3) | `input.json positive.drivers.growth_rate` deleted | **2** | 2 | **rc=2 is reachable**: a corrupted positive input makes the product raise, so no verdict exists and the harness says so instead of exiting 0 |

Exit-code map (corrected in revision r3): **rc=2 IS reachable** - it is produced when the corrupted
artefact is the POSITIVE INPUT, so the product raises and no verdict exists (case D below, raw rc=2).
Case B is a defect **outside** the guarded block, so it still raises and exits **1** rather than 2;
that remains fail-loud but is a different code path. The earlier r2 wording ("rc=2 is not yet
reachable in practice") was wrong and is corrected here.
