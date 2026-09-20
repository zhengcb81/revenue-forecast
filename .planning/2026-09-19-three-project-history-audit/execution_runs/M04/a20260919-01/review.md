# M04 · implementer review record

Card M04 (`capacity_utilization`), Parent I-10. Attempt `execution_runs/M04/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped` **and this card records an ACTIVE
> `STOP_DISCLOSURE_ADAPTATION` finding**; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict.

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local isolated snapshot; hashes equal | `binding.json`, `evidence/M04/source_manifest.json` |
| B positive | `[730.0]` vs independent oracle `[730]` within tolerance | `evidence/M04/formula_result.json` |
| C negatives | **15/15** rejected with `ModelRegistryError`; continuity positive `[144, 172.8]` passes; defaults case `[1440]` matches the pre-frozen oracle | `evidence/M04/negative_results.json` |
| D mapping | real SMIC FY2024 disclosure mapping (utilisation, capacity, shipments) **including a failed reconciliation reported as a stop** | `evidence/M04/disclosure_mapping.json`, `evidence/M04/accounting_decision.md` |
| E probe | labelled `historical_mapping_probe`; its volume check FAILED the frozen tolerance | `evidence/M04/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M04/qualification.json` |

## 2. Independence of the oracle

- `scripts/oracle_M04.py` imports only `json`, `os`, `decimal`; it never imports `model_registry`.
- SMIC's figures were hand-transcribed from read-only extracted page text (`before/probe01_smic.json`,
  `before/probe02_smic.json`), not from any product parser.
- Negatives are in-memory `deepcopy` cases; JSON-parser rejections cannot masquerade as model rejections.
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`.

## 3. Results in detail

- Registry formula string observed:
  `revenue = capacity * utilization * yield * unit_revenue * timing_factor + other_revenue` — matches the
  frozen expectation.
- Positive `[730.0]`: `1000 x 0.8 x 0.9 x 2 x 0.5 + 10`.
- Defaults case `[1440.0]`: only the four required drivers supplied, so `timing_factor` defaulted to `1.0`
  and `other_revenue` to `0.0`.
- Continuity positive `[144.0, 172.8]`; break patch rejected.
- Rejections: `NEG-CARD` (`utilization = [1.1]`) → `driver capacity_utilization.utilization must be between
  0.0 and 1.0: FY2027`; `R2-YIELD` (`yield = [1.2]`) → same bound for `yield`;
  `R3-CAPACITY-NEG` → `... capacity must be between 0.0 and inf`; `R3-UNIT-REV-NEG` → same for
  `unit_revenue`; `R8-NET-NEG` → `calculated revenue cannot be negative: capacity_utilization`;
  `N01a` numeric; `N01b/c/d` finite; `N02` length; `N03` missing driver; `N04` unknown driver;
  `N05a/b` fiscal years; `CONT-BREAK` consecutive years.

## 4. Unit / dimension and rejection checks

- Dimension chain: `quantity x ratio x ratio x CNY/quantity x ratio + CNY = CNY`.
- Per-share vs total: not applicable.
- Gross vs net: consolidated operating revenue; the report's main accounting-data table header states
  `单位：千元 币种：人民币`, so the raw `57,795,570` multiplies by 1000 — this scale conversion is explicit in
  the mapping.
- Period alignment: utilisation, capacity and revenue are all FY2024.
- Rejection conditions R1-R11 in `oracle.md` §6; R1-R8 executed, R9-R11 are business refusals (double-counting
  yield, double-counting commissioning time, production-as-sales).

## 5. Judgement calls the reviewer should attack first

1. **ACTIVE STOP — the capacity denominator.** The model documents `capacity` as a **full-year gross** figure.
   SMIC discloses only a **period-end** monthly capacity (`94.8万片/月` at 2024-12-31). Annualising it
   (`948,000 x 12 = 11,376,000`) and applying the disclosed utilisation `85.6%` gives `9,737,856` good
   wafers, versus a disclosed shipment volume of `8,021,000` — a gap of `+1,716,856` wafers = **21.4045%**
   against a **0.5% tolerance frozen before the run**. The reconciliation FAILS; SMIC was expanding all year
   (implied average ≈ `780,860.59` wafers/month = 82.37% of the period-end annualised figure). DEC-M04-1 asks
   the reviewer to choose between (a) obtaining a disclosed average/available capacity, (b) building an
   audited capacity-ramp bridge, or (c) restricting the model to issuers that disclose an average.
2. **`yield = 1` is the riskiest assumption.** No numeric yield exists anywhere in the 222-page report
   (full-text probe: 2 hits, both qualitative). `yield = 1` is justified only if the disclosed utilisation
   denominator is *available* rather than *nameplate* capacity. If it is nameplate, yield is not inside the
   ratio and this choice overstates output (SR-M04-A). The field is recorded as **missing**, not as reported.
3. **No apportionment of the gap.** It mixes the wrong capacity basis with output-versus-sales (the disclosed
   `8,021,000` is *sold* wafers); no inventory/wafer-stock bridge is disclosed, so this attempt refuses to
   split it. The back-solved `9,370,327.10` capacity is marked diagnostic-only and must never be presented as
   a disclosed parameter (I-10-A item 3).
4. **Partial provenance.** This PDF's sidecar is a 5-line stub (`market`/`security_id`/`source_title`) with
   no provider receipt, no `source_url` and no content hash, so the local sha256
   (`d0d08d76…`, computed by this attempt) cannot be cross-checked against a publisher receipt — unlike the
   cninfo documents used in M01/M02/M03. SR-M04-B asks whether the company-wiki copy is acceptable as
   disclosure evidence.
5. **I-00-B interpretation** — same deviation note as M01/M02/M03.
6. **`calculate_model_path` not exercised** (I-10-A obligation); only read-only call-site observations.

## 6. What this card does NOT claim

- No accuracy claim.
- No `disclosure_adaptation` — the card is at a recorded stop, not at a pass. The existence of a mapping must
  not be read as an adaptation result.
- No formula rewrite; no change to any product file.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M04.py` and `scripts/run_card.py`; diff against the recorded results.
2. Re-read SMIC FY2024 pages 6, 8 and 84 yourself and confirm: `产能利用率 85.6%`, `月产能 94.8 万片`,
   `销售晶圆 802.1 万片`, `营业收入 57,795,570 千元 (2024) / 45,250,425 千元 (2023)`.
3. Reproduce `11,376,000 x 0.856 = 9,737,856` and the 21.4045% gap independently.
4. Confirm the frozen tolerances in `oracle.md` §7 predate the run and were not relaxed afterwards.
5. Pick an unused case (e.g. `utilization=[0.0]`, or `yield=[0.0]` with a non-zero capacity) and freeze the
   expectation before running.
6. Adjudicate DEC-M04-1..6 and SR-M04-A/B/C/D — DEC-M04-1 is the blocking one.

---

## revision r2 - response to the independent review (status stays `review_pending`)

The reviewer returned **accepted_scoped (formula only)** for M01-M04 with five required fixes and one
item reserved for adjudication. r2 changes **attempt-local files only**; no production repository was
touched and no oracle expectation, tolerance or disclosure figure was altered to make anything pass.

### Verdict-carrying exit code (F-M01-02)

| item | change | evidence |
|---|---|---|
| F-M01-02 | `scripts/run_card.py` no longer returns 0 unconditionally. It now returns **0** only when the positive path matches the independent oracle within tolerance, the continuity positive passes and **all** negative cases were rejected with `ModelRegistryError`; **2** if the harness could not produce a verdict; **3** if the verdict is negative. The JSON artefacts are still written before returning, so a non-zero exit never destroys evidence. `scripts/run_M01.py` was patched the same way (M01 only). | `scripts/run_card.py`, `evidence/M04/revision_r2.json`, `after/rerun_sha256.json` |
| re-run | the same `calculate_registered_model` call was re-executed unchanged | **raw rc = 0** (expected 0), `evidence/run_result.json/exit_code_semantics` = `verdict` / `exit_code` |

### Delivery completeness (F-M01-03)

- `after/rerun_sha256.json` + `after/rerun_stdout.txt` + `after/rerun_stderr.txt`: post-r2 re-run hashes.
- `recovery/README.md`: `not_applicable_with_reason` - this card is a pure in-process function with no durable state, lock, lease or partial publication to recover.
- `changes.diff`: explicit **no product change** statement; there is no diff to show by design.
- `before/git_status_revenue-forecast.txt` re-written as **UTF-8** (was UTF-16LE).
- `evidence/M04/first_run_forensics.json`: F-M01-01 record.

### Frozen expectations were NOT rewritten

`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body, and `evidence/M04/source_manifest.json.oracle_versions` now indexes the oracle document and script versions with hashes and timestamps.

### F-M04-01 - typo corrected

- "781,861 wafers/month" -> **"780,860.59 wafers/month"**, matching `evidence/M04/oracle.json.wafer_count_reconciliation.implied_monthly_capacity_diagnostic_only`. The other M04 files already carried the correct value; this was a prose typo only, and the ACTIVE `STOP_DISCLOSURE_ADAPTATION` conclusion is unchanged.

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

Typo fixed in the same revision (F-M04-01): the monthly-capacity figure in this file was 781,861 and is now 780,860.59 wafers/month (the other M04 files already carried the correct value).

Exit-code map (corrected in revision r3): **rc=2 IS reachable** - it is produced when the corrupted
artefact is the POSITIVE INPUT, so the product raises and no verdict exists (case D below, raw rc=2).
Case B is a defect **outside** the guarded block, so it still raises and exits **1** rather than 2;
that remains fail-loud but is a different code path. The earlier r2 wording ("rc=2 is not yet
reachable in practice") was wrong and is corrected here.
