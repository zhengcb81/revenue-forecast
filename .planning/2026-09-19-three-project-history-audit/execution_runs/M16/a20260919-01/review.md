# M16 · real_estate_rental — implementer review record

Card M16 (`real_estate_rental`), Parent I-10, card title `M16 · real_estate_rental · 已出租面积租金`.
Attempt `execution_runs/M16/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M16/source_manifest.json`, `before/setup_receipt.json` |
| B positive | `[32.0]` vs independent oracle `[32.0]`, tolerance [3.2e-08]; structure/length/type/finiteness faithful | `evidence/M16/formula_result.json`, `verify_report.json` |
| continuity positive | actual `[32.0, 41.4]` vs oracle `[32.0, 41.4]` | `evidence/M16/run_result.json` |
| defaults case | actual `[30.0]` vs oracle `[30.0]` (not gating) | `evidence/M16/run_result.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M16/negative_results.json` |
| mutation proof | scratch copies corrupted -> rc 2/2/2, rc 3, rc 1; control rc 0; frozen hashes unchanged | `recovery/selfcheck_result.json` |
| OQ enumeration | 31 models / 165 drivers / 41 ratio drivers enumerated by script; counts quoted, not typed | `evidence/M16/oq_enumeration.json`, `oq_rulings.json` |
| D mapping | **NOT DONE** - this attempt is the synthetic formula scope only; nothing is claimed | `evidence/M16/qualification.json` |
| E probe | **NOT DONE** (needs D and I-10-A) | - |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M16/qualification.json` |

Runner verdict: `pass`, exit code `0`, triggered conditions `[]`
(`evidence/M16/run_result.json` -> `exit_code_semantics`).

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M16.py`, which imports only `argparse`, `hashlib`,
  `json`, `os`, `time` and `decimal` (see `import_lines` in
  `evidence/M16/oracle_selfcheck.json`). It never imports `model_registry` or
  `model_extensions`; `product_import_present` is `false`.
- `scripts/run_card.py` (sha256 `9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194`) calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only
  from `evidence/M16/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a
  uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- Two declared product calls exist **outside** the oracle and are recorded as their own units in
  `commands.json`: the read-only metadata enumeration (`C2-enumerate-driver-bounds`) and the
  labelled post-hoc design probe (`C3-probe-signed-driver`). Neither produces an expected value.
- The card runner, the mutation self-check, the evidence packer and the verifier are the same
  bytes as in the sibling M13/M14/M15/M16 attempts (`scripts/run_card.py` sha256
  `9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194`), so no card-specific runner can drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = average_occupied_area * rent_per_area + other_revenue`
- Registry required: `["average_occupied_area", "rent_per_area"]`; optional: `["other_revenue"]`; defaults: `{}`;
  explicit driver_bounds: `{}`
- Effective bounds enumerated from the isolated copy: `{"average_occupied_area": [0.0, "inf"], "rent_per_area": [0.0, "inf"], "other_revenue": ["-inf", "inf"]}`
- Hand work (from `oracle.md`, decimal, unrounded): 1000 × 0.03 = 30；30 + 2 = 32
- Continuity hand work: FY2027 = 1000×0.03 + 2 = 30 + 2 = 32；FY2028 = 1200×0.032 + 3 = 38.4 + 3 = 41.4
- Defaults hand work: 1000 × 0.03 + 0 = 30（other_revenue 回落到 0.0）
- Rejections and their messages (verbatim from `negative_results.json`):

| Case | Rejection message | Verdict |
|---|---|---|
| `NEG-CARD` | `driver real_estate_rental.average_occupied_area must be between 0.0 and inf: FY2027` | `PASS_rejected` |
| `N01a` | `real_estate_rental.average_occupied_area.FY2027 must be numeric` | `PASS_rejected` |
| `N01b` | `real_estate_rental.average_occupied_area.FY2027 must be finite` | `PASS_rejected` |
| `N01c` | `real_estate_rental.average_occupied_area.FY2027 must be finite` | `PASS_rejected` |
| `N01d` | `real_estate_rental.average_occupied_area.FY2027 must be finite` | `PASS_rejected` |
| `N02` | `driver real_estate_rental.average_occupied_area must contain one value per forecast year` | `PASS_rejected` |
| `N03` | `missing drivers for real_estate_rental: average_occupied_area` | `PASS_rejected` |
| `N04` | `unsupported drivers for real_estate_rental: unknown_driver` | `PASS_rejected` |
| `N05a` | `real_estate_rental.years must contain fiscal years` | `PASS_rejected` |
| `N05b` | `real_estate_rental.years must contain fiscal years` | `PASS_rejected` |
| `CONT-BREAK` | `real_estate_rental.years must be consecutive and increasing` | `PASS_rejected` |
- `NEG-CARD` is refused by the **value/domain guard**, not by the array-length guard
  (`driver real_estate_rental.average_occupied_area must be between 0.0 and inf: FY2027`) - the failure mode this batch previously suffered from.

## 4. Observations (NOT pass/fail; they do not enter the exit code)

| ID | Mutation / base | Observed | Why recorded |
|---|---|---|---|
| `OBS-BASE-IGNORED` | set_base_revenue | `[32.0]` | the rowwise calculator discards base_revenue; design observation only, not a pass condition |
| `OBS-BOUND-INCLUSIVE` | set_driver_element | `[2.0]` | the area domain is INCLUSIVE at the lower edge (0 is accepted, -1 is refused by NEG-CARD); records the edge, does not gate |
| `OBS-SIGNED-OTHER` | set_driver_element | `[29.0]` | other_revenue is a signed driver: a negative other amount is admitted and still leaves total revenue non-negative; records the contract boundary, does not gate |


## 5. Mutation proof (frozen runner, scratch copies only)

`scripts/selfcheck_mutation.py` (`recovery/selfcheck_result.json`):

| Scenario | Mutation applied to the scratch copy | raw rc | expected rc |
|---|---|---|---|
| C-control | none | 0 | 0 |
| A-corrupt-value | oracle.json:positive.expected_float -> [999.0] | 2 | 2 |
| F-corrupt-shape | oracle.json:expected_output_shape.positive.length -> 99 | 2 | 2 |
| D-missing-expectation | oracle.json:positive.expected_float deleted | 2 | 2 |
| B-corrupt-negative-case | cases.json:NEG-CARD value {"__float__": -1} -> {"__float__": 0.5} (now inside the driver domain) | 3 | 3 |
| E-harness-error | none | 1 | 1 |
| G-corrupt-case-expected | cases.json:NEG-CARD expected 'ModelRegistryError' -> 'PythonBuiltinValueError' (a type this runner never counts as a refusal verdict) | 2 | 2 |
| H-drop-negative-case | cases.json: dropped case CONT-BREAK (case count 11 -> 10 while oracle.json still declares 11) | 2 | 2 |
| G-pre-fix-runner-corrupt-case-expected | cases.json:NEG-CARD expected 'ModelRegistryError' -> 'PythonBuiltinValueError' (a type this runner never counts as a refusal verdict) | 0 | 0 |
| H-pre-fix-runner-drop-negative-case | cases.json: dropped case CONT-BREAK (case count 11 -> 10 while oracle.json still declares 11) | 0 | 0 |

`frozen_unchanged_by_the_selfcheck = true` and
`frozen_still_equals_freeze_time_hashes = true`, so the corruption never touched the
frozen oracle. The exit-code scope is therefore empirically reachable: 0, 1, 2 and 3 were all
observed.

## 6. oq_rulings enumeration (script-derived counts)

`scripts/enumerate_driver_bounds.py` -> `evidence/M16/oq_enumeration.json` ->
`scripts/build_oq_rulings.py` -> `evidence/M16/oq_rulings.json`.
Enumerated by the implementer session by running that script against the isolated read-only copy
(automated; no human counting). The independent reviewer of 2026-09-20 re-implemented the
enumeration and corrected the predicate: a driver is a ratio driver when
`spec.dimensions[driver] == "ratio"` (the narrower `ModelSpec.ratio_drivers` set structurally
misses `direct_growth.growth_rate`, domain `(-1, inf)`, hard-coded at
`scripts/model_registry.py:287-288`). The authoritative registry totals are therefore
**41/4** (41 ratio drivers, 4 of them not bounded [0,1]), consistent with the M05-M08 r3
correction; the narrower predicate's numbers (40/3) are still recorded side by side,
and every predicate disagreement is listed in `oq_enumeration.json`.
Counts for this model: 2 required, 1 optional,
**1 optional drivers without an explicit default**
(`other_revenue`), **1 signed & unbounded drivers**
(`other_revenue`), 2 drivers with a lower bound of exactly 0.0.
Registry-wide, the silent-zero-fill surface is 31 optional driver slots
across 24 models (unit labels are recorded in
`oq_rulings.json.enumerated_counts_with_units`). The OQ list in `oq_rulings.json` mirrors
`handoff.json:open_questions` one-to-one (OQ-01..OQ-05), so the numbering cannot diverge between the
two files.

## 7. Judgement calls the reviewer should attack first

1. **`defaults` 与 `observations` 不参与退出码。** 有人会主张失败的观察项至少应触发 rc=2；
   本 runner 的契约是显式的，且 `triggered` 会列出全部条件——但这是有意的范围选择。
2. **rc=2 会遮蔽 rc=3。** 优先级 `1 > 2 > 3`；同时成立时返回 2 但 `triggered` 仍列出
   `negative_case_not_rejected`。是否需要与顺序无关的判定码由 reviewer 决定。
3. **`rent_per_area` 的量纲（月 vs 年）没有任何契约约束。** 实现只知道它是"每面积收入"；
   月租误当年租不会被计算器发现（卡片 L39 明确要求显式换算），必须由披露适配阶段绑定。
4. **`other_revenue` 带符号**：负值被接受（实测 29.0），因此"其他收入"既可能掩盖费用，
   也可能在总额非负时静默吸收错误。reviewer 应确认该 driver 在披露阶段的口径。
5. **"已租面积不能再乘出租率"只靠 driver 集合保证。** 契约里没有 occupancy driver，
   所以双重折扣需要人为构造 `unknown_driver`（被拒绝）；这一点已在 `D-M16-3` 说明。
6. **免租期/直线法**：实现没有免租期参数，卡片 L37 的直线法确认属 D 阶段；
   本卡不声称已处理。
7. **隔离 checkout 的 provenance（OQ-01）** 与 **未安装 pytest（OQ-05）**：同 M13/M14/M15。

## 8. What this card does NOT claim

- 不声称模型准确，也不声称任何映射可泛化。
- 不声称 `disclosure_adaptation`（本 attempt 没有任何真实公司披露映射，保持 `unmapped`）。
- 不改写公式：在没有独立反例、也没有经审定规格的情况下保留既有实现。
- 不声称"已租面积 0 被接受"等价于"空置无需建模"；那属业务判断。

## 10. Revision r3 - response to the independent review (2026-09-20)

The independent reviewer returned **accepted_scoped (formula qualification only)** for this card
and listed findings F-01..F-05 plus two notes. Revision r3 handles them in the tool and evidence
layers only - **no frozen expectation, tolerance, case or refusal condition was changed**:

| Finding | What r3 did |
|---|---|
| F-01 | `scripts/run_card.py` now cross-checks every case's declared `expected` against the type the runner actually counts, plus the case count / id set against `oracle.json`; any inconsistency is an expectation gap and yields **rc=2**. The pre-fix revision is kept at `recovery/runner_before_F01_fix.py` and demonstrated red (rc=0 -> rc=2) on the same corrupted scratch copy. |
| F-02 | ratio predicate corrected to `spec.dimensions[driver] == "ratio"`; registry totals 40/3 -> **41/4** (`direct_growth.growth_rate (-1, inf)` recovered); `oq_enumeration.json` / `oq_rulings.json` regenerated. |
| F-03 | `oq_rulings.json` OQ list now mirrors `handoff.json:open_questions` one-to-one (OQ-01..OQ-05); `decision.md` / `review.md` numbering aligned; document pointers audited by `scripts/audit_doc_pointers.py` -> `evidence/M16/doc_pointer_audit.json` (including an explicit search for the residue tokens the reviewer listed). |
| F-04 | `scripts/finalize_hashes.py` writes its own by-products before the inventory, excludes the manifest itself from `files`, and adds `self_reference_note`, `combined_digest_scope` and `concurrently_mutable` marks, so the inventory is now reproducible. |
| F-05 | `recovery/README.md` states explicitly that the first failed invocation's raw bytes are not retained; from r3 on, first failed invocations are saved verbatim as `recovery/first_invocation_*.stdout.txt` and `recovery/first_invocation_*.stderr.txt`. |
| note (c) | not applicable to this card: every observation here is constructible as frozen (`evidence/M16/cases_annotation_repack.json` proves `cases.json` is byte-identical to the frozen revision). |
| note (units) | `oq_rulings.json` carries `enumerated_counts_with_units` (slots vs models). |

The exit-code matrix observed by the mutation self-check is in
`recovery/selfcheck_result.json` -> `exit_code_matrix`. Status after r3: `formula` remains
`review_pending` (the implementer never self-signs; r3 goes back for a point review),
`disclosure_adaptation` remains `unmapped`, `accuracy` remains `unproven`.

## 9. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M16.py --out-root <scratch attempt>` and diff the generated
   `input.json`/`cases.json`/`oracle.json` against the frozen ones; then re-run
   `scripts/run_card.py` and diff `run_result.json`.
2. Run `scripts/verify_card.py` and `scripts/verify_r2_boundary.py`; both must exit 0.
3. Confirm the isolated copy still hashes equal to production (`evidence/M16/source_manifest.json`,
   `after/source_hashes.txt`).
4. Confirm BOTH frozen-body boundaries: `before/oracle_md_v1.json` sha256 == sha256(oracle.md
   bytes before the single r2 marker) (r2 byte offset 8495) and
   `revision_r2.json`'s recorded post-append hash == sha256(oracle.md bytes before the single r3
   marker); exactly one r2 and one r3 section must exist.
5. Read `evidence/M16/oq_rulings.json` and re-run the enumeration script to check the quoted
   counts (predicate: `spec.dimensions[driver] == "ratio"`).
6. Pick a case the implementer did not use and freeze its expectation **before** running it.
7. Adjudicate the OQ-01..OQ-05 items in `handoff.json` / `decision.md` (same numbering in
   `oq_rulings.json`) and point-check revision r3.
> ## INDEPENDENT REVIEW VERDICT — M16 (`real_estate_rental`) — `accepted_scoped` (formula qualification ONLY)
>
> Reviewer: an independent reviewer session (对抗式定点评测), 2026-09-20.
> **This verdict is scoped to `formula` and to nothing else.**
> `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`; stages D, E and F were
> **not** performed and are **not** covered by this verdict.
>
> ### What was verified, and how
>
> The reviewer did **not** reuse the implementer's scripts to reach any conclusion. The reviewer
> wrote its own harness, its own predicate enumeration, its own negative-case set, its own mutation
> matrix and its own structural differ, and read the frozen artifacts and the isolated
> `iso/checkout_scripts` directly.
>
> **(1) Formula faithfulness — pass, on the frozen evidence.**
> Reviewer-re-implemented arithmetic, with reviewer-chosen inputs (not the card's): M13
> fee-vs-performance/other separation, M14 owned-store-vs-recognised-fee separation, M15
> capacity×utilization×yield chain (including utilization = 1.0 at the closed upper edge and a
> negative ancillary item), M16 area×rent. Then the frozen evidence was replayed end-to-end by the
> reviewer's own runner: positive / continuity / defaults = [32.0] / [32.0, 41.4] / [30.0]; **11/11 negatives refused with `ModelRegistryError`** for every
> card; `not_rejected = 0`, `wrong_exception_type = 0`, `import_or_file_error = 0`.
> Observations reproduced: `OBS-BASE-IGNORED` (base_revenue discarded by `_rowwise`), `OBS-BOUND-INCLUSIVE` = 2.0, `OBS-SIGNED-OTHER` = 29.0.
> 35 reviewer-authored negatives produced **no case of "should-refuse-but-accepted"**.
>
> **(2) Frozen artifacts unchanged — pass.**
> For M16, `input.json`, `oracle.json` and `cases.json` are **byte-identical** to the reviewer's round-2 record — the M13 `cases.json` annotation exception does **not** apply here.
> Cross-card note for the record: M13's `cases.json` changed `0353e544…` → `54399cd2…`, and a
> **recursive structural diff** against the preserved pre-fix baseline
> (`recovery/before_fixes/cases.json`, which the reviewer confirmed equals its own round-2 baseline
> byte-for-byte) shows **exactly 2 key additions and nothing else** —
> `extra_observations[2]{not_executable_as_frozen, construction_error}` on `OBS-SIGNED-PERF-FEE`;
> its `cases` block (11 negatives) is byte-identical, `n_keys_removed = 0`, `n_values_changed = 0`.
> No expectation, tolerance or refusal condition was touched on any of the four cards.
> `oracle.md` is a **pure append**: the frozen-body hash still reproduces at the r2 boundary
> (`a9f07e39…`@8495`), the r3 boundary offset equals the r2-stage byte length exactly
> (11957), there is exactly one r2 heading and one r3 heading, and
> `recovery/before_fixes/oracle.md` equals the reviewer's round-2 record of the whole file.
> 199 JSON files across the four attempts parse under a **strict** parser with
> `Infinity`/`-Infinity`/`NaN` rejected: **0 violations, 0 BOM**.
>
> **(3) The five round-2 findings — all closed.**
> **F-01** (self-check was silently insensitive to `cases.json`'s declared expectation): the new
> runner (`9e4a6450…`) is verified to catch **7/7 reviewer-authored injections** —
> `expected` renamed, a negative case dropped, `negative_count` falsified, `negative_ids` falsified,
> unknown `kind`, missing `base_input`, and a removed positive expectation — returning **rc=2**
> (`expectation_declaration_inconsistent`) where the **pre-fix runner `e709408f…` returned rc=0**
> on the same corrupted copies. The control still returns **rc=0 with 11/11 negatives and unchanged
> positives/continuity/defaults**, so no legitimate case was turned red. The pre-fix bytes are
> preserved as `recovery/runner_before_F01_fix.py` and hash to the round-2 value.
> **F-02**: the reviewer's own predicate differential confirms the authoritative counts
> **ratio 41 / not-in-[0,1] 4**, with `A ⊆ B` (empty difference), the sole difference being
> `direct_growth.growth_rate (-1, inf)`. Keeping the superseded 40 alongside, under an explicitly
> named `..._by_registry_ratio_set` field, is **accepted and preferable to deletion**.
> **F-03**: the OQ list now mirrors `handoff.json` item-for-item (OQ-01…OQ-05 on all four cards),
> and the persisted `doc_pointer_audit.json` reproduces exactly (60 pointers on this card,
> dangling 0, residue empty).
> **F-04**: the combined digest is now reproducible by an independent recomputation over the
> `files` map for all four cards, the manifest excludes itself, and the concurrently mutable
> `after/git_status_*` by-products are labelled.
> **F-05 / observation (c)**: `recovery/README.md` declares the missing raw bytes of the first
> failed invocation as a provenance gap instead of papering over it, and the non-constructible
> observation is now self-describing (`not_executable_as_frozen` + `construction_error`) with the
> factual question answered by a labelled probe.
> **Unit labels**: slot counts (31) and model counts (24) are now both given, with an explicit
> `unit_note` explaining that earlier batches quoted one or the other unlabelled.
>
> **(4) The reviewer's own round-2 error, retracted.**
> The round-2 report claimed that `handoff.json` still carried five residue tokens
> (`handoff.json:346` etc.). **That claim was the reviewer's own measurement artifact and is
> withdrawn**: the numbers were string lengths of the `open_questions` array printed by a faulty
> diagnostic command, not file content. The implementer's statement that the tokens cannot be
> reproduced is **correct**. No residue ever existed and nothing was deleted.
>
> ### Carried findings (do not block this verdict)
>
> * **F-r3-01 (P3, wording).** `cases_annotation_repack.json` for M14/M15/M16 says an annotation was
>   appended "on the observation with id NONE" while `all_differences_found` is empty and the file
>   hashes are unchanged. The scope sentence should read "no annotation applied on this card".
>   **Boundary: only that record file may be rewritten; `cases.json`/`oracle.json`/`input.json` must
>   stay byte-identical.**
> * **F-r3-02 (P2, cross-card environment, owner decision).** Production
>   `scripts/model_registry.py` changed back to a pre-extension revision
>   (`9ec65295…` → `1f2639e1…`, 31 → 23 models, `driver_bounds` / `driver_value_bounds` /
>   `_SIGNED_DRIVERS` gone) and `scripts/model_extensions.py` is now untracked. **This does not
>   affect this card's verdict**: the object under test is the frozen `iso/checkout_scripts`
>   (`9ec65295…`, unchanged, and the value the runner recorded as imported). But the three
>   "isolated equals production" self-checks are now **historical, not current**, and the reviewer's
>   `verify_card.py` on a pristine copy correctly reports
>   `isolated_snapshot_still_equals_production: False`. **Boundary: append a time-stamped drift note;
>   do not rewrite the historical hash fields and do not make the check pass by editing it.**
> * **F-r3-03 (P3, governance).** `handoff.json.reviewer_status`, `oq_rulings.json.attribution.
>   reviewed_by` and the `oracle.md` r3 section contain the reviewer's verdict wording written by
>   the implementer. The content was checked and **matches the reviewer's actual ruling point for
>   point, with no embellishment**, and transcription was authorised by the delegating agent; the
>   reviewer's only reservation is that an evidence file's `reviewed_by` text should ideally be
>   recorded by the reviewer or replaced by a pointer.
> * **F-r3-04 (P3, inventory scope).** `files` still includes `scripts/__pycache__/*.pyc`
>   (M15/M16 now list one that no longer exists). Does not affect digest reproducibility or any
>   evidence, but it is inconsistent with the by-product policy F-04 established.
> * **F-r3-05 (P3, design trade-off — no change requested).** With precedence `1 > 2 > 3`, a
>   simultaneous rc=2-and-rc=3 condition returns 2 while `exit_code_semantics.triggered` still lists
>   every condition. The reviewer rules this **acceptable**: the triggered list is a complete audit
>   record and both codes are failure states. The real gap is the **cross-batch rc legend**, which is
>   an owner-level matter (round-2 F-07), not a defect of this card.
>
> ### Verdict
>
> **M16 `real_estate_rental` = `accepted_scoped` (formula only).**
>
> The implementer correctly left `handoff.json.status` and `qualification.formula` at
> `review_pending` and never self-signed; the acceptance above is issued by the reviewer, and it is
> the implementer's/hand-off owner's call to record it in `qualification.json`.
>
> ### Not verified by this reviewer
>
> The *cause* of the production rollback (deliberate or concurrent accident); whether that rollback
> affects any other card's verdict (each has its own frozen isolate, which this reviewer did not
> re-examine); the exact number and ordering of writes to the production file inside the review
> window; and a full replay of the other three cards' observations to "bit-identical to r2" strength.
