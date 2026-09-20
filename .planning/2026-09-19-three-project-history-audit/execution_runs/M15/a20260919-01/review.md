# M15 · transport — implementer review record

Card M15 (`transport`), Parent I-10, card title `M15 · transport · 运力利用与收益率`.
Attempt `execution_runs/M15/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M15/source_manifest.json`, `before/setup_receipt.json` |
| B positive | `[160.0]` vs independent oracle `[160.0]`, tolerance [1.6e-07]; structure/length/type/finiteness faithful | `evidence/M15/formula_result.json`, `verify_report.json` |
| continuity positive | actual `[160.0, 196.8]` vs oracle `[160.0, 196.8]` | `evidence/M15/run_result.json` |
| defaults case | actual `[150.0]` vs oracle `[150.0]` (not gating) | `evidence/M15/run_result.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M15/negative_results.json` |
| mutation proof | scratch copies corrupted -> rc 2/2/2, rc 3, rc 1; control rc 0; frozen hashes unchanged | `recovery/selfcheck_result.json` |
| OQ enumeration | 31 models / 165 drivers / 41 ratio drivers enumerated by script; counts quoted, not typed | `evidence/M15/oq_enumeration.json`, `oq_rulings.json` |
| D mapping | **NOT DONE** - this attempt is the synthetic formula scope only; nothing is claimed | `evidence/M15/qualification.json` |
| E probe | **NOT DONE** (needs D and I-10-A) | - |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M15/qualification.json` |

Runner verdict: `pass`, exit code `0`, triggered conditions `[]`
(`evidence/M15/run_result.json` -> `exit_code_semantics`).

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M15.py`, which imports only `argparse`, `hashlib`,
  `json`, `os`, `time` and `decimal` (see `import_lines` in
  `evidence/M15/oracle_selfcheck.json`). It never imports `model_registry` or
  `model_extensions`; `product_import_present` is `false`.
- `scripts/run_card.py` (sha256 `9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194`) calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only
  from `evidence/M15/oracle.json`.
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

- Registry formula observed from the isolated copy: `revenue = capacity * utilization * yield + ancillary_revenue`
- Registry required: `["capacity", "utilization", "yield"]`; optional: `["ancillary_revenue"]`; defaults: `{}`;
  explicit driver_bounds: `{}`
- Effective bounds enumerated from the isolated copy: `{"capacity": [0.0, "inf"], "utilization": [0.0, 1.0], "yield": [0.0, "inf"], "ancillary_revenue": ["-inf", "inf"]}`
- Hand work (from `oracle.md`, decimal, unrounded): 1000 × 0.75 = 750；750 × 0.2 = 150；150 + 10 = 160
- Continuity hand work: FY2027 = 1000×0.75×0.2 + 10 = 150 + 10 = 160；FY2028 = 1200×0.7×0.22 + 12 = 840×0.22 + 12 = 184.8 + 12 = 196.8
- Defaults hand work: 1000 × 0.75 × 0.2 + 0 = 150（ancillary_revenue 回落到 0.0）
- Rejections and their messages (verbatim from `negative_results.json`):

| Case | Rejection message | Verdict |
|---|---|---|
| `NEG-CARD` | `driver transport.utilization must be between 0.0 and 1.0: FY2027` | `PASS_rejected` |
| `N01a` | `transport.capacity.FY2027 must be numeric` | `PASS_rejected` |
| `N01b` | `transport.capacity.FY2027 must be finite` | `PASS_rejected` |
| `N01c` | `transport.capacity.FY2027 must be finite` | `PASS_rejected` |
| `N01d` | `transport.capacity.FY2027 must be finite` | `PASS_rejected` |
| `N02` | `driver transport.capacity must contain one value per forecast year` | `PASS_rejected` |
| `N03` | `missing drivers for transport: capacity` | `PASS_rejected` |
| `N04` | `unsupported drivers for transport: unknown_driver` | `PASS_rejected` |
| `N05a` | `transport.years must contain fiscal years` | `PASS_rejected` |
| `N05b` | `transport.years must contain fiscal years` | `PASS_rejected` |
| `CONT-BREAK` | `transport.years must be consecutive and increasing` | `PASS_rejected` |
- `NEG-CARD` is refused by the **value/domain guard**, not by the array-length guard
  (`driver transport.utilization must be between 0.0 and 1.0: FY2027`) - the failure mode this batch previously suffered from.

## 4. Observations (NOT pass/fail; they do not enter the exit code)

| ID | Mutation / base | Observed | Why recorded |
|---|---|---|---|
| `OBS-BASE-IGNORED` | set_base_revenue | `[160.0]` | the rowwise calculator discards base_revenue; design observation only, not a pass condition |
| `OBS-BOUND-INCLUSIVE` | set_driver_element | `[210.0]` | the ratio domain is INCLUSIVE at the upper edge: 1.0 is accepted while NEG-CARD's 1.1 is refused; records the edge, does not gate |
| `OBS-YIELD-GT1` | set_driver_element | `[1135.0]` | card_M15.md L42 warns that the manufacturing 0-1 yield bound must NOT be transplanted to transport yield; this probe records whether the implementation applies such a bound (it does not: yield has dimension revenue_per_unit) |
| `OBS-SIGNED-ANCILLARY` | set_driver_element | `[130.0]` | ancillary_revenue is a signed driver: a negative ancillary amount is admitted and still leaves total revenue non-negative; records the contract boundary, does not gate |


## 5. Mutation proof (frozen runner, scratch copies only)

`scripts/selfcheck_mutation.py` (`recovery/selfcheck_result.json`):

| Scenario | Mutation applied to the scratch copy | raw rc | expected rc |
|---|---|---|---|
| C-control | none | 0 | 0 |
| A-corrupt-value | oracle.json:positive.expected_float -> [999.0] | 2 | 2 |
| F-corrupt-shape | oracle.json:expected_output_shape.positive.length -> 99 | 2 | 2 |
| D-missing-expectation | oracle.json:positive.expected_float deleted | 2 | 2 |
| B-corrupt-negative-case | cases.json:NEG-CARD value {"__float__": 1.1} -> {"__float__": 0.5} (now inside the driver domain) | 3 | 3 |
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

`scripts/enumerate_driver_bounds.py` -> `evidence/M15/oq_enumeration.json` ->
`scripts/build_oq_rulings.py` -> `evidence/M15/oq_rulings.json`.
Enumerated by the implementer session by running that script against the isolated read-only copy
(automated; no human counting). The independent reviewer of 2026-09-20 re-implemented the
enumeration and corrected the predicate: a driver is a ratio driver when
`spec.dimensions[driver] == "ratio"` (the narrower `ModelSpec.ratio_drivers` set structurally
misses `direct_growth.growth_rate`, domain `(-1, inf)`, hard-coded at
`scripts/model_registry.py:287-288`). The authoritative registry totals are therefore
**41/4** (41 ratio drivers, 4 of them not bounded [0,1]), consistent with the M05-M08 r3
correction; the narrower predicate's numbers (40/3) are still recorded side by side,
and every predicate disagreement is listed in `oq_enumeration.json`.
Counts for this model: 3 required, 1 optional,
**1 optional drivers without an explicit default**
(`ancillary_revenue`), **1 signed & unbounded drivers**
(`ancillary_revenue`), 3 drivers with a lower bound of exactly 0.0.
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
3. **`yield` 无上界。** OBS-YIELD-GT1 证明实现接受 `yield = 1.5`；这在运输语义下正确（单价），
   但 reviewer 应确认"无上界"不会让数量级错误（例如把百分比当单价）静默通过——契约层没有量纲检查。
4. **容量与价格的量纲一致性没有被实现检查。** 卡片 L42 要求"容量和价格必须同量纲"，
   但注册表只记录 `quantity` / `revenue_per_unit` 两个标签，不做交叉校验；这只能靠披露适配阶段保证。
5. **利用率分母不显式。** `utilization` 只是一个 [0,1] 比例，实现不知道分母是 ASK 还是吨公里；
   卡片 L40 要求披露该分母，属 D 阶段事项。
6. **辅助收入的符号问题。** `ancillary_revenue` 带符号且无下界，负值被接受；
   若燃油附加既含在 yield 又计入辅助收入，实现不会发现重复（卡片 L40）。
7. **隔离 checkout 的 provenance（OQ-01）** 与 **未安装 pytest（OQ-05）**：同 M13/M14，属需 owner/reviewer 明示的事项。

## 8. What this card does NOT claim

- 不声称模型准确，也不声称任何映射可泛化。
- 不声称 `disclosure_adaptation`（本 attempt 没有任何真实公司披露映射，保持 `unmapped`）。
- 不改写公式：在没有独立反例、也没有经审定规格的情况下保留既有实现。
- 不声称"利用率 1.0 被接受"等价于"满载一定可实现"；那属业务判断，不是本卡结论。

## 10. Revision r3 - response to the independent review (2026-09-20)

The independent reviewer returned **accepted_scoped (formula qualification only)** for this card
and listed findings F-01..F-05 plus two notes. Revision r3 handles them in the tool and evidence
layers only - **no frozen expectation, tolerance, case or refusal condition was changed**:

| Finding | What r3 did |
|---|---|
| F-01 | `scripts/run_card.py` now cross-checks every case's declared `expected` against the type the runner actually counts, plus the case count / id set against `oracle.json`; any inconsistency is an expectation gap and yields **rc=2**. The pre-fix revision is kept at `recovery/runner_before_F01_fix.py` and demonstrated red (rc=0 -> rc=2) on the same corrupted scratch copy. |
| F-02 | ratio predicate corrected to `spec.dimensions[driver] == "ratio"`; registry totals 40/3 -> **41/4** (`direct_growth.growth_rate (-1, inf)` recovered); `oq_enumeration.json` / `oq_rulings.json` regenerated. |
| F-03 | `oq_rulings.json` OQ list now mirrors `handoff.json:open_questions` one-to-one (OQ-01..OQ-05); `decision.md` / `review.md` numbering aligned; document pointers audited by `scripts/audit_doc_pointers.py` -> `evidence/M15/doc_pointer_audit.json` (including an explicit search for the residue tokens the reviewer listed). |
| F-04 | `scripts/finalize_hashes.py` writes its own by-products before the inventory, excludes the manifest itself from `files`, and adds `self_reference_note`, `combined_digest_scope` and `concurrently_mutable` marks, so the inventory is now reproducible. |
| F-05 | `recovery/README.md` states explicitly that the first failed invocation's raw bytes are not retained; from r3 on, first failed invocations are saved verbatim as `recovery/first_invocation_*.stdout.txt` and `recovery/first_invocation_*.stderr.txt`. |
| note (c) | not applicable to this card: every observation here is constructible as frozen (`evidence/M15/cases_annotation_repack.json` proves `cases.json` is byte-identical to the frozen revision). |
| note (units) | `oq_rulings.json` carries `enumerated_counts_with_units` (slots vs models). |

The exit-code matrix observed by the mutation self-check is in
`recovery/selfcheck_result.json` -> `exit_code_matrix`. Status after r3: `formula` remains
`review_pending` (the implementer never self-signs; r3 goes back for a point review),
`disclosure_adaptation` remains `unmapped`, `accuracy` remains `unproven`.

## 9. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M15.py --out-root <scratch attempt>` and diff the generated
   `input.json`/`cases.json`/`oracle.json` against the frozen ones; then re-run
   `scripts/run_card.py` and diff `run_result.json`.
2. Run `scripts/verify_card.py` and `scripts/verify_r2_boundary.py`; both must exit 0.
3. Confirm the isolated copy still hashes equal to production (`evidence/M15/source_manifest.json`,
   `after/source_hashes.txt`).
4. Confirm BOTH frozen-body boundaries: `before/oracle_md_v1.json` sha256 == sha256(oracle.md
   bytes before the single r2 marker) (r2 byte offset 8478) and
   `revision_r2.json`'s recorded post-append hash == sha256(oracle.md bytes before the single r3
   marker); exactly one r2 and one r3 section must exist.
5. Read `evidence/M15/oq_rulings.json` and re-run the enumeration script to check the quoted
   counts (predicate: `spec.dimensions[driver] == "ratio"`).
6. Pick a case the implementer did not use and freeze its expectation **before** running it.
7. Adjudicate the OQ-01..OQ-05 items in `handoff.json` / `decision.md` (same numbering in
   `oq_rulings.json`) and point-check revision r3.
