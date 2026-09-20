# M01 · implementer review record

Card M01 (`direct_growth`), Parent I-10. Attempt `execution_runs/M01/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local isolated snapshot; hashes recorded and equal | `binding.json`, `evidence/M01/source_manifest.json` |
| B positive | `[220.00000000000003, 110.00000000000001, 0.0]` vs independent oracle `[220, 110, 0]`, all within `1e-9*max(1,|e|)` | `evidence/M01/formula_result.json`, `evidence/M01/stdout.txt` |
| C negatives | 11/11 rejected with `ModelRegistryError`; continuity positive `[110, 115.5]` passes before the break patch | `evidence/M01/negative_results.json` |
| D mapping | one real disclosed mapping (ZJ FY2024/FY2025) with page, table, span, hash, unit and period; professional decisions written as PROPOSED only | `evidence/M01/disclosure_mapping.json`, `evidence/M01/accounting_decision.md` |
| E probe | labelled `historical_mapping_probe`; explicitly not a scenario set and not accuracy evidence | `evidence/M01/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M01/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M01.py`, which imports **only** `json`, `os`, `sys` and
  `decimal`. It never imports `model_registry`.
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from
  `evidence/M01/oracle.json`.
- Negative cases are built **in memory** from a fresh `deepcopy` each time — never round-tripped through a
  JSON parser — so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses real `bool`,
  N01b-d use real `float('nan'/'inf'/'-inf')`).
- A verdict of `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- Cross-check: the earlier card-specific runner `scripts/run_M01.py` and the later generic
  `scripts/run_card.py` produced **identical** results for M01 (`run_result.json` vs
  `run_result_generic.json`), which guards against a harness-specific artefact.

## 3. Results in detail

- Positive per-year: 2027 `abs_diff = 2.84e-14` (tol 2.2e-07); 2028 `1.42e-14` (tol 1.1e-07);
  2029 `0.0` (tol 1e-09). `growth_rate = -1` produced exactly `0.0`, not a negative or NaN.
- Registry formula string observed via the isolated copy:
  `revenue[t] = revenue[t-1] * (1 + growth_rate[t])` — matches the frozen expectation in `oracle.md` §1.
- Rejections and their messages:
  - `NEG-CARD`: `direct_growth.growth_rate must be between -1.0 and inf: FY2027`
  - `N01a`: `... must be numeric`; `N01b/c/d`: `... must be finite`
  - `N02`: `... must contain one value per forecast year`
  - `N03`: `missing drivers for direct_growth: growth_rate`
  - `N04`: `unsupported drivers for direct_growth: unknown_driver`
  - `N05a/b`: `direct_growth.years must contain fiscal years`
  - `CONT-BREAK`: `direct_growth.years must be consecutive and increasing`
- Design observation recorded by the generic runner: none for M01 (no `extra_observations` were defined).

## 4. Unit / dimension and rejection checks (card requirement)

- Currency: base and output are both CNY, scale 1; the model multiplies by a dimensionless decimal only,
  so no dimension can drift.
- Per-share vs total: not applicable — `direct_growth` produces a total, and `base_revenue` must be a total.
- Gross vs net: the framework's mapping fixes the basis (consolidated gross operating revenue); the model
  itself adds no tax or elimination term.
- Period alignment: one `growth_rate` per fiscal year, positionally aligned with `years`.
- Rejection conditions R1-R9 are listed in `oracle.md` §8; R1-R7 were executed, R8/R9 are business refusals
  recorded in `decision.md` and `disclosure_mapping.json` rather than runtime cases.

## 5. Judgement calls the reviewer should attack first

1. **The residual is small, and that is the trap.** Handing the model the issuer's own printed 14.96% rate
   yields a prediction that misses the disclosed FY2025 revenue by only CNY 14.59m (0.0042%) — which looks
   like success but is really "the model reproduces the number it was handed". Most of that residual is the
   issuer's 2-decimal rounding (the exact ratio is 14.9648%). Do **not** read it as evidence of forecast
   skill. See `evidence/M01/historical_reconciliation.json`.
2. **Constant-CAGR falsifier**: FY2024 was +3.49% and FY2025 was +14.96% for the same issuer and line. A
   single constant rate cannot be reconciled with two consecutive disclosed periods.
3. **I-00-B interpretation.** I-00-B binds the isolation *plan* and the two-stage command rule but does not
   materialise a checkout tree. This attempt therefore materialised its own read-only snapshot
   (`iso/checkout_scripts/model_registry.py` + `model_extensions.py`, hashes equal to production) and ran
   from it. If the intended binding is a checkout materialised by I-00-B, this is a scope deviation and must
   be recorded as such — the code under test is byte-identical either way, but the provenance chain differs.
4. **Runner bug found and fixed, not hidden.** The first B run exited 1 (`KeyError: 'continuity'`) because the
   case file referenced the wrong input key. That was a harness bug; the product was never changed. The
   failing stderr is superseded by the final run's logs, and `commands.json` records it.
5. **`base_revenue` domain**: `calculate_registered_model` rejects a negative `base_revenue` before dispatch
   even though `_direct_growth` uses it and `_direct_revenue` does not. For M01 the field is genuinely used,
   so the guard is unambiguously correct here; the semantics question is raised in M02's `decision.md`
   (DEC-M02-3).
6. **Disclosure scope.** The mapped line is the *consolidated group* total. It is not a segment, so it cannot
   be used to justify a segment-level `direct_growth` path.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review and a
  reconciliation against the production forecast entry point, which this attempt only inspected read-only
  (`evidence/M01/forecast_integration.json`).
- It does **not** rewrite the formula. Card line 65: with no independent counter-example and no adjudicated
  specification, the existing implementation is retained.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M01.py`, then `scripts/run_card.py`, and diff against the recorded
   `run_result.json` / `formula_result.json`.
2. Confirm the isolated copy hash equals the production hash *now* (drift means this card must be re-run).
3. Confirm `oracle.md` was not edited after the run (the file is under version-free disk; compare mtimes and
   the recorded `input.json`/`oracle.json` hashes in `source_manifest.json`).
4. Pick a case the implementer did not use (e.g. `growth_rate = [0.0, 0.0]` with a non-200 base, or
   `years = [1999, 2000]`) and freeze the expectation before running.
5. Adjudicate DEC-M01-1/2/3 and SR-M01-A/B/C in `evidence/M01/accounting_decision.md`.

---

## revision r2 - response to the independent review (status stays `review_pending`)

The reviewer returned **accepted_scoped (formula only)** for M01-M04 with five required fixes and one
item reserved for adjudication. r2 changes **attempt-local files only**; no production repository was
touched and no oracle expectation, tolerance or disclosure figure was altered to make anything pass.

### Verdict-carrying exit code (F-M01-02)

| item | change | evidence |
|---|---|---|
| F-M01-02 | `scripts/run_card.py` no longer returns 0 unconditionally. It now returns **0** only when the positive path matches the independent oracle within tolerance, the continuity positive passes and **all** negative cases were rejected with `ModelRegistryError`; **2** if the harness could not produce a verdict; **3** if the verdict is negative. The JSON artefacts are still written before returning, so a non-zero exit never destroys evidence. `scripts/run_M01.py` was patched the same way (M01 only). | `scripts/run_card.py`, `evidence/M01/revision_r2.json`, `after/rerun_sha256.json` |
| re-run | the same `calculate_registered_model` call was re-executed unchanged | **raw rc = 0** (expected 0), `evidence/run_result.json/exit_code_semantics` = `verdict` / `exit_code` |

### Delivery completeness (F-M01-03)

- `after/rerun_sha256.json` + `after/rerun_stdout.txt` + `after/rerun_stderr.txt`: post-r2 re-run hashes.
- `recovery/README.md`: `not_applicable_with_reason` - this card is a pure in-process function with no durable state, lock, lease or partial publication to recover.
- `changes.diff`: explicit **no product change** statement; there is no diff to show by design.
- `before/git_status_revenue-forecast.txt` re-written as **UTF-8** (was UTF-16LE).
- `evidence/M01/first_run_forensics.json`: F-M01-01 record.

### Frozen expectations were NOT rewritten

`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body, and `evidence/M01/source_manifest.json.oracle_versions` now indexes the oracle document and script versions with hashes and timestamps.

### F-M01-01 - first-run evidence and version provenance (honest gap)

- The first product run's stderr **cannot be recovered**: the corrected re-run redirected stderr to the same path and overwrote it, and `-B` suppressed `__pycache__`, so no bytecode record of the pre-fix oracle exists (a directory search confirmed this).
- What is recorded instead: the exact first-run argv, `raw_rc = 1`, and the transcribed `KeyError: 'continuity'` traceback, explicitly labelled as a **session-transcript capture, not an original artefact** (`evidence/M01/first_run_forensics.json`).
- oracle script v1 is stored as `scripts/oracle_M01.v1.reconstructed.py`, derived by reversing the one documented token change and explicitly marked **RECONSTRUCTED**.
- **Remaining gap the reviewer should note:** the pre-run frozen hash of `oracle.md` was never captured (the manifest was generated after the re-run), so "the frozen version was not edited to fit the result" is supported only by the mtime sequence and by the fact that the frozen body is unmodified; it is not supported by a pre-run hash. This is stated rather than papered over.

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
| B | `cases.json first case base_input -> 'no_such_block'` | **1** | non-zero | a harness defect outside the guard cannot masquerade as a pass; it raises |
| C | none (the real card) | **0** | 0 | the repaired exit code stays 0 for a genuinely passing card |
| D (added in r3) | `input.json positive.drivers.growth_rate` deleted | **2** | 2 | **rc=2 is reachable**: a corrupted positive input makes the product raise, so no verdict exists and the harness says so instead of exiting 0 |

Exit-code map (corrected in revision r3): **rc=2 IS reachable** - it is produced when the corrupted
artefact is the POSITIVE INPUT, so the product raises and no verdict exists (case D below, raw rc=2).
Case B is a defect **outside** the guarded block, so it still raises and exits **1** rather than 2;
that remains fail-loud but is a different code path. The earlier r2 wording ("rc=2 is not yet
reachable in practice") was wrong and is corrected here.
