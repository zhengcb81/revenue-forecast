# M13 · asset_management — implementer review record

Card M13 (`asset_management`), Parent I-10, card title `M13 · asset_management · 平均资管规模收费`.
Attempt `execution_runs/M13/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M13/source_manifest.json`, `before/setup_receipt.json` |
| B positive | `[25.0]` vs independent oracle `[25]`, within `2.5e-08`; structure/length/type/finiteness faithful | `evidence/M13/formula_result.json`, `evidence/M13/verify_report.json` |
| continuity positive | actual `[25.0, 35.0]` vs oracle `[25, 35]` | `evidence/M13/run_result.json` |
| defaults case | actual `[20.0]` vs oracle `[20]` (not gating) | `evidence/M13/run_result.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M13/negative_results.json` |
| mutation proof | scratch copies corrupted → rc 2/2/2, rc 3, rc 1; control rc 0; frozen hashes unchanged | `recovery/selfcheck_result.json` |
| OQ enumeration | 31 models / 165 drivers / 40 ratio drivers enumerated by script; counts quoted, not typed | `evidence/M13/oq_enumeration.json`, `evidence/M13/oq_rulings.json` |
| D mapping | **NOT DONE** - this attempt is the synthetic formula scope only; nothing is claimed | `evidence/M13/qualification.json` |
| E probe | **NOT DONE** (needs D and I-10-A) | - |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M13/qualification.json` |

Runner verdict: `pass`, exit code `0`, triggered conditions `[]`
(`evidence/M13/run_result.json` → `exit_code_semantics`).

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M13.py`, which imports only `argparse`, `hashlib`, `json`,
  `os`, `time` and `decimal` (see the `import_lines` list inside `evidence/M13/oracle_selfcheck.json`).
  It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from
  `evidence/M13/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON
  parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`,
  N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and
  `FileNotFoundError` are recorded as **FAIL**, never as pass.
- Two declared product calls exist **outside** the oracle and are recorded as their own units in
  `commands.json`: the read-only metadata enumeration (`C2-enumerate-driver-bounds`) and the labelled
  post-hoc design probe (`C3-probe-signed-driver`). Neither produces an expected value for this card.

## 3. Results in detail

- Registry formula observed from the isolated copy:
  `revenue = average_aum * management_fee_rate + performance_fee_revenue + other_revenue`
- Registry required: `['average_aum', 'management_fee_rate']`; optional:
  `['performance_fee_revenue', 'other_revenue']`; defaults: `{}`; explicit driver_bounds: `{}`
- Positive hand work: 2000 × 0.01 = 20; 20 + 3 = 23; 23 + 2 = **25**
- Continuity hand work: FY2027 = 2000×0.01 + 3 + 2 = **25**; FY2028 = 2500×0.012 + 4 + 1 = 30 + 5 = **35**
- Defaults hand work: 2000 × 0.01 + 0 + 0 = **20** (both optional drivers fall back to 0.0)
- Rejections and their messages (verbatim from `negative_results.json`):
  - `NEG-CARD`: `driver asset_management.management_fee_rate must be between 0.0 and 1.0: FY2027`
    (the **value-domain** guard, not the length guard)
  - `N01a`: `asset_management.average_aum.FY2027 must be numeric`
  - `N01b`: `asset_management.average_aum.FY2027 must be finite`
  - `N01c`: `asset_management.average_aum.FY2027 must be finite`
  - `N01d`: `asset_management.average_aum.FY2027 must be finite`
  - `N02`: `driver asset_management.average_aum must contain one value per forecast year`
  - `N03`: `missing drivers for asset_management: average_aum`
  - `N04`: `unsupported drivers for asset_management: unknown_driver`
  - `N05a`: `asset_management.years must contain fiscal years`
  - `N05b`: `asset_management.years must contain fiscal years`
  - `CONT-BREAK`: `asset_management.years must be consecutive and increasing`

## 4. Observations (NOT pass/fail; they do not enter the exit code)

- `OBS-BASE-IGNORED`: `base_revenue = 999` → `[25.0]`, identical to the positive;
  the rowwise calculator discards `base_revenue`.
- `OBS-BOUND-INCLUSIVE`: `management_fee_rate = 1.0` → `[2005.0]` (hand work 2000×1.0+3+2), i.e. the
  ratio domain is inclusive at the upper edge while NEG-CARD's 1.1 is refused.
- `OBS-SIGNED-PERF-FEE`: **raised `KeyError` instead of recording a contract fact.** The frozen
  specification used `base=defaults`, which does not contain the `performance_fee_revenue` key, so
  `set_driver_element` could not be applied. This is recorded as-is; the frozen fixtures were **not**
  rewritten to hide it (see `revision_r2.json` item R2-05 and `recovery/probes/signed_driver_probe.json`,
  which answers the same factual question outside the frozen case set: `performance_fee_revenue = -100`
  on the positive base → `ModelRegistryError` "…calculated revenue cannot be negative…").

## 5. Mutation proof (frozen runner, scratch copies only)

`scripts/selfcheck_mutation.py` (`recovery/selfcheck_result.json`):

| Scenario | Mutation applied to the scratch copy | raw rc | expected rc |
|---|---|---|---|
| C-control | none (frozen copies verbatim) | 0 | 0 |
| A-corrupt-value | `oracle.json` `positive.expected_float → [999.0]` | 2 | 2 |
| F-corrupt-shape | `oracle.json` `expected_output_shape.positive.length → 99` | 2 | 2 |
| D-missing-expectation | `oracle.json` `positive.expected_float` deleted | 2 | 2 |
| B-corrupt-negative-case | `cases.json` NEG-CARD value 1.1 → 0.5 (now legal) | 3 | 3 |
| E-harness-error | `--code-root` points at a non-existent directory | 1 | 1 |
| G-corrupt-case-expected | `cases.json` NEG-CARD `expected` → `PythonBuiltinValueError` | 2 | 2 |
| H-drop-negative-case | `cases.json` last case dropped (11 → 10 vs a frozen oracle declaring 11) | 2 | 2 |
| G-pre-fix-runner-... | same corruption, run with `recovery/runner_before_F01_fix.py` | 0 | 0 |
| H-pre-fix-runner-... | same deletion, run with `recovery/runner_before_F01_fix.py` | 0 | 0 |

`frozen_unchanged_by_the_selfcheck = true` and `frozen_still_equals_freeze_time_hashes = true`, so the
corruption never touched the frozen oracle. The last two rows are the F-01 defect demonstration: the
pre-fix runner revision returned rc=0 on exactly the copies that now yield rc=2.
`recovery/selfcheck_result.json` carries the full `exit_code_matrix` (rc 0/1/2/3 all reachable).

Two real harness/plumbing defects were found and are kept in the record instead of being replayed away:
the first `run_card.py` invocation returned **rc=1** (`NameError: name 'key' is not defined`, a runner
defect), and the first r2 append put one separating newline before the boundary marker, which was repaired
by removing exactly that byte (`recovery/oracle_md_before_boundary_repair.bin`, `revision_r2.json` R2-06).
The raw bytes of that first failed invocation were **not retained** (see `recovery/README.md`, F-05).

## 6. oq_rulings enumeration (script-derived counts)

`scripts/enumerate_driver_bounds.py` → `evidence/M13/oq_enumeration.json` →
`scripts/build_oq_rulings.py` → `evidence/M13/oq_rulings.json`.
Enumerated by the implementer session by running that script against the isolated read-only copy
(automated; no human counting). The independent reviewer of 2026-09-20 re-implemented the enumeration and
corrected the predicate: a driver is a ratio driver when `spec.dimensions[driver] == "ratio"` (the narrower
`ModelSpec.ratio_drivers` set structurally misses `direct_growth.growth_rate`, domain `(-1, inf)`,
hard-coded at `scripts/model_registry.py:287-288`). The authoritative registry totals are therefore
**41/4** (41 ratio drivers, 4 of them not bounded [0,1]), consistent with the M05–M08 r3 correction; the
narrower predicate's numbers (40/3) are recorded side by side and every disagreement is listed in
`oq_enumeration.json`. Counts for this model: 2 required, 2 optional, **2 optional drivers without an
explicit default** (both silently filled with 0.0 when omitted), **2 signed & unbounded drivers**
(`performance_fee_revenue`, `other_revenue`), 1 driver with an inclusive upper bound of 1.0.
Registry-wide the silent-zero-fill surface is **31 optional driver slots across 24 models**
(`oq_rulings.json.enumerated_counts_with_units` labels the units).
The OQ list in `oq_rulings.json` mirrors `handoff.json:open_questions` one-to-one (OQ-01..OQ-05).

## 7. Judgement calls the reviewer should attack first

1. **The invalid observation (OBS-SIGNED-PERF-FEE).** The frozen case set contains an observation that
   cannot be built as specified. I did not repack `cases.json` (rule: do not repack frozen fixtures; and
   the correct pre-freeze fix is impossible after the run). Decide whether (a) keeping the invalid
   observation plus a labelled post-hoc probe is acceptable, or (b) the card must be re-run with a
   corrected observation, which requires a declared repack of `cases.json` with old/new hashes and a
   re-run of the product.
2. **`defaults` and `observations` are not gating.** A reviewer may argue that a failed observation should
   at least force rc=2. The runner's contract is explicit (only positive/continuity faithfulness and the
   refusals gate), and `exit_code_semantics.triggered` lists every condition, so nothing is hidden - but
   this is a deliberate scope choice, not an accident.
3. **rc=2 masks rc=3.** Precedence is `1 > 2 > 3`; when a positive mismatch and an unrejected negative both
   hold, the runner returns 2 while still listing `negative_case_not_rejected` in `triggered`. Decide
   whether the verdict code should instead be order-independent (e.g. a bitmask).
4. **`base_revenue` is discarded.** The registry accepts `base_revenue` (and validates it non-negative) but
   `_rowwise` deletes it. For this model that is invisible; a reviewer should confirm the same contract
   fact for M14/M15/M16 rather than assume it.
5. **The non-negative-revenue終检 vs a signed performance fee.** `performance_fee_revenue` is legitimately
   signed (clawback), yet a negative total revenue is refused outright. Whether the disclosure-adaptation
   stage needs a different convention is an accounting decision for I-10-A, not decided here.
6. **Isolated-checkout provenance (OQ-01).** I-00-B binds the isolation *plan* and the two-stage command
   rule but does not materialise a checkout tree; this attempt therefore materialises its own read-only
   snapshot (`iso/checkout_scripts`, hashes equal to production). If the intended binding is a checkout
   materialised by I-00-B, that is a scope deviation to record - the code under test is byte-identical
   either way.
7. **pytest was not installed.** No offline wheel exists in the local pip cache and installing it would
   need network (forbidden). The card does not require re-running the historical suite, and no pytest
   command was executed; a reviewer who requires the historical suite for this card must say so explicitly,
   because it would change the attempt's scope.

## 8. What this card does NOT claim

- It does **not** claim the model is accurate, nor that any mapping generalises.
- It does **not** claim `disclosure_adaptation` (unmapped: no real-company disclosure mapping exists here).
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated specification,
  the existing implementation is retained.
- It does **not** claim that the synthetic positive proves anything about real asset managers (e.g. that a
  period-end AUM may stand in for the average - card_M13.md L42 refuses exactly that).

## 9. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M13.py --out-root <scratch attempt>` and diff the generated
   `input.json`/`cases.json`/`oracle.json` against the frozen ones; then re-run
   `scripts/run_card.py` and diff `run_result.json`.
2. Run `scripts/verify_card.py`, `scripts/verify_r2_boundary.py` and `scripts/validate_json_tree.py`;
   all three must exit 0. `commands.json` also carries a computed `argv_path_check`: every absolute
   path in every recorded argv exists on disk, and the only path outside this attempt is the
   read-only production root passed to the verifier.
3. Confirm the isolated copy still hashes equal to production (`evidence/M13/source_manifest.json`,
   `after/source_hashes.txt`).
4. Confirm BOTH frozen-body boundaries: `before/oracle_md_v1.json` sha256 == sha256(oracle.md bytes
   before the single r2 marker) (r2 byte offset 10692), and `revision_r2.json`'s recorded post-append
   hash == sha256(oracle.md bytes before the single r3 marker); exactly one r2 and one r3 section.
5. Read `evidence/M13/oq_rulings.json` and re-run the enumeration script to check the quoted counts
   (predicate: `spec.dimensions[driver] == "ratio"`).
6. Pick a case the implementer did not use (e.g. `management_fee_rate = 0.0`, or a two-year path with a
   fractional AUM) and freeze its expectation **before** running it.
7. Adjudicate the OQ-01…OQ-05 items in `handoff.json` / `decision.md` (same numbering in
   `oq_rulings.json.open_questions_mirroring_handoff`) and point-check revision r3.

## 10. Revision r3 — response to the independent review (2026-09-20)

The independent reviewer returned **accepted_scoped (formula qualification only)** for this card and
listed findings F-01..F-05 plus two notes. Revision r3 handles them in the tool and evidence layers only
— **no frozen expectation, tolerance, case or refusal condition was changed**:

| Finding | What r3 did |
|---|---|
| F-01 | `scripts/run_card.py` now cross-checks each case's declared `expected` against the type the runner actually counts, plus the case count / id set against `oracle.json`; any inconsistency is an expectation gap and yields **rc=2** (previously rc=0). The pre-fix revision is kept at `recovery/runner_before_F01_fix.py` and demonstrated red on the same corrupted scratch copy (see the two extra rows in section 5). |
| F-02 | ratio predicate corrected to `spec.dimensions[driver] == "ratio"`; registry totals 40/3 → **41/4** (`direct_growth.growth_rate (-1, inf)` recovered); `oq_enumeration.json` / `oq_rulings.json` regenerated; section 6 rewritten. |
| F-03 | `oq_rulings.json` OQ list now mirrors `handoff.json:open_questions` one-to-one (OQ-01..OQ-05); `decision.md` and this file renumbered; all `<file>.py:<line>` pointers audited by `scripts/audit_doc_pointers.py` → `evidence/M13/doc_pointer_audit.json`, which also records the explicit search for the five residue tokens the reviewer listed (**none of them exists anywhere in this attempt outside the audit script's own data**; the line pointers that are present are the verified product ones - `model_registry.py:233/308/335/352-353` - plus the M05–M08 r3 artifacts, which this attempt opened read-only and re-checked: `f07_enumerate.py:60` really is `dim = spec.dimensions[driver]`, and `docfix_r3.json` really records `ratio_drivers_total_was 40` → `now 41` with `missing_driver_added = direct_growth.growth_rate, domain (-1, inf)`). |
| F-04 | `scripts/finalize_hashes.py` writes its own by-products before the inventory, excludes `after/rerun_sha256.json` itself from `files`, and adds `self_reference_note`, `combined_digest_scope` and `concurrently_mutable` marks, so the inventory and the combined digest are now reproducible. |
| F-05 | `recovery/README.md` states explicitly that the first failed invocation's raw bytes are not retained; the r3 pipeline saves every self-check scenario's stdout/stderr, and future first failed invocations go to `recovery/first_invocation_*.{stdout,stderr}.txt`. |
| note (c) | the invalid observation `OBS-SIGNED-PERF-FEE` now carries an **append-only** annotation in `cases.json` (`not_executable_as_frozen`, `construction_error`, pointing at the labelled probe) — no expectation changed; `evidence/M13/cases_annotation_repack.json` proves the only difference from the frozen revision is those two added keys. |
| note (units) | `oq_rulings.json` now separates slots from models: **31 optional slots without an explicit default across 24 models**, with unit labels. |

Status after r3: `formula` remains `review_pending` (the implementer never self-signs; r3 goes back for a
point review), `disclosure_adaptation` remains `unmapped`, `accuracy` remains `unproven`.
