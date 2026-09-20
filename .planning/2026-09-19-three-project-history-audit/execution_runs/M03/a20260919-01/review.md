# M03 · implementer review record

Card M03 (`unit_sales`), Parent I-10. Attempt `execution_runs/M03/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict.

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local isolated snapshot; hashes equal | `binding.json`, `evidence/M03/source_manifest.json` |
| B positive | `[305.0]` vs independent oracle `[305]` within tolerance | `evidence/M03/formula_result.json` |
| C negatives | **13/13** rejected with `ModelRegistryError`; continuity positive `[200, 220]` passes; defaults case `[30]` and zero-volume case `[5]` match the pre-frozen oracle | `evidence/M03/negative_results.json` |
| D mapping | real BYD FY2024 disclosure mapping (volume + revenue + segment line + mix), with the derived-price caveat stated openly | `evidence/M03/disclosure_mapping.json`, `evidence/M03/accounting_decision.md` |
| E probe | labelled `historical_mapping_probe` | `evidence/M03/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M03/qualification.json` |

## 2. Independence of the oracle

- `scripts/oracle_M03.py` imports only `json`, `os`, `decimal`; it never imports `model_registry`.
- The BYD figures in the oracle were **hand-transcribed** from the read-only extracted page text
  (`before/probe01_byd.json`, `before/probe02_byd.json`), not read from any product parser.
- Negatives are in-memory `deepcopy` cases; JSON-parser rejections cannot masquerade as model rejections.
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`.

## 3. Results in detail

- Registry formula string observed:
  `revenue = units * unit_revenue * timing_factor + other_revenue` — matches the frozen expectation.
- Positive `[305.0]`: `120 x 2.5 x 1 + 5`.
- Defaults case `[30.0]`: only the two required drivers supplied, so `timing_factor` defaulted to `1.0` and
  `other_revenue` to `0.0` — the documented defaults behave as documented (this is **not** an authorisation to
  fill 1/0 when a disclosure is missing).
- Zero-volume case `[5.0]`: `units = 0` is data, and `other_revenue` still applies.
- Continuity positive `[200.0, 220.0]`; break patch rejected.
- Rejections: `NEG-CARD` → `driver unit_sales.units must be between 0.0 and inf: FY2027`;
  `R7-TIMING` → `driver unit_sales.timing_factor must be between 0.0 and 1.0: FY2027`;
  `R8-NET-NEG` → `calculated revenue cannot be negative: unit_sales`;
  `N01a` numeric; `N01b/c/d` finite; `N02` length; `N03` missing driver; `N04` unknown driver;
  `N05a/b` fiscal years; `CONT-BREAK` consecutive years.
- Observation `OBS-NEG-OTHER`: `other_revenue = [-10]` (a signed driver inside its domain) yields `290.0`,
  i.e. accepted; only a **negative net result** is refused. Recorded as a design observation, not scored.

## 4. Unit / dimension and rejection checks

- Dimension chain: `quantity x CNY/unit x ratio + CNY = CNY`. Checked with real numbers:
  `4,250,370 vehicles x 123,751.503987229 CNY/vehicle = 525,989,680,000.00 CNY`.
- Per-share vs total: not applicable; every mapped field is a total amount or a physical count.
- Gross vs net: **OPEN** — the mapped column is labelled 销售收入 with no printed gross/net statement
  (SR-M03-B). The model has no returns/rebate term, so the net basis must be established at the mapping layer.
- Period alignment: volume and revenue are read from the **same table row** for FY2024, so numerator and
  denominator share one period and one boundary.
- `timing_factor = 1` because the volume is a full-year realised figure; applying a fraction would be the
  repeated-time-scaling failure the card names.
- Rejection conditions R1-R11 in `oracle.md` §6; R1-R8 executed, R9-R11 are business refusals.

## 5. Judgement calls the reviewer should attack first

1. **`unit_revenue` is derived, not disclosed.** `525,989,680,000 / 4,250,370 = 123,751.503987229`, so the
   zero residual is a constructive identity. DEC-M03-2 asks whether `unit_sales` can earn a disclosure
   adaptation at all when the per-unit net price is not disclosed; the implementer's position is **not yet**.
2. **Confirmed sales volume, not production.** The same table prints production `4,281,084` and sales
   `4,250,370` — a 30,714-unit (0.72%) difference that would have silently inflated revenue.
3. **The 14.37% scope gap.** Rebuilding the automobile segment revenue from **total** vehicle unit sales at
   the passenger-vehicle unit price gives `528,681,308,161.71` against a disclosed
   `617,381,935,000.00`, i.e. a gap of `88,700,626,838.29` (14.3667%), far outside the 2% tolerance frozen
   before the run. Interpretation: the segment line also contains batteries, parts and other products that
   this model cannot identify. It must be bridged with evidence and must **never** be booked into
   `other_revenue` to make the reconciliation pass.
4. **Derived price across boundaries.** Using the passenger-vehicle unit price against the *total* vehicle
   volume is already a boundary mismatch; it was used only to quantify the scope gap, and that is stated in
   the mapping.
5. **I-00-B interpretation** — same deviation note as M01/M02 (attempt-local byte-identical snapshot).
6. **`calculate_model_path` not exercised** (I-10-A obligation); only read-only call-site observations.

## 6. What this card does NOT claim

- No accuracy claim (FY2024 is a closed period; two of the three reconciliations are constructive).
- No `disclosure_adaptation` (derived price, unresolved gross/net, unexplained 14.37% scope gap, no reviewer
  signature).
- No formula rewrite; no change to any product file.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M03.py` and `scripts/run_card.py`; diff against the recorded results.
2. Re-read BYD FY2024 page 23 yourself and confirm the row/column selection (乘用车 快报销量 4,250,370;
   销售收入 525,989,680,000.00) and that production is a different column.
3. Confirm the frozen tolerances in `oracle.md` §7 predate the run (they are consistent with
   `historical_reconciliation.json`).
4. Pick an unused case (e.g. `units=[10]`, `unit_revenue=[3]`, `timing_factor=[0.25]`) and freeze the
   expectation before running.
5. Adjudicate DEC-M03-1..6 and SR-M03-A/B/C/D.

---

## revision r2 - response to the independent review (status stays `review_pending`)

The reviewer returned **accepted_scoped (formula only)** for M01-M04 with five required fixes and one
item reserved for adjudication. r2 changes **attempt-local files only**; no production repository was
touched and no oracle expectation, tolerance or disclosure figure was altered to make anything pass.

### Verdict-carrying exit code (F-M01-02)

| item | change | evidence |
|---|---|---|
| F-M01-02 | `scripts/run_card.py` no longer returns 0 unconditionally. It now returns **0** only when the positive path matches the independent oracle within tolerance, the continuity positive passes and **all** negative cases were rejected with `ModelRegistryError`; **2** if the harness could not produce a verdict; **3** if the verdict is negative. The JSON artefacts are still written before returning, so a non-zero exit never destroys evidence. `scripts/run_M01.py` was patched the same way (M01 only). | `scripts/run_card.py`, `evidence/M03/revision_r2.json`, `after/rerun_sha256.json` |
| re-run | the same `calculate_registered_model` call was re-executed unchanged | **raw rc = 0** (expected 0), `evidence/run_result.json/exit_code_semantics` = `verdict` / `exit_code` |

### Delivery completeness (F-M01-03)

- `after/rerun_sha256.json` + `after/rerun_stdout.txt` + `after/rerun_stderr.txt`: post-r2 re-run hashes.
- `recovery/README.md`: `not_applicable_with_reason` - this card is a pure in-process function with no durable state, lock, lease or partial publication to recover.
- `changes.diff`: explicit **no product change** statement; there is no diff to show by design.
- `before/git_status_revenue-forecast.txt` re-written as **UTF-8** (was UTF-16LE).
- `evidence/M03/first_run_forensics.json`: F-M01-01 record.

### Frozen expectations were NOT rewritten

`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body, and `evidence/M03/source_manifest.json.oracle_versions` now indexes the oracle document and script versions with hashes and timestamps.

### F-M03-01 - arithmetic typo corrected

- The rebuild/gap figures in `oracle.md`, `evidence/M03/historical_reconciliation.json`, `evidence/M03/disclosure_mapping.json` and `evidence/M03/accounting_decision.md` used a **truncated unit price**; they now match `evidence/M03/oracle.json`, which was always correct (full-precision unit price 123,751.503986712 -> rebuild 528,684,368,999.31, gap 88,697,566,000.69).
- Cause: intermediate rounding of the unit price. **Conclusion unchanged**: the gap is still 14.3667%% of the segment line, still far outside the pre-frozen 2%% tolerance, and filling it into `other_revenue` remains forbidden.
- The corrected values are now **read from `oracle.json`** before being written, so the files cannot diverge again.

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
