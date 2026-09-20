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
| OQ enumeration | 31 models / 165 drivers / 40 ratio drivers enumerated by script; counts quoted, not typed | `evidence/M16/oq_enumeration.json`, `oq_rulings.json` |
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
- `scripts/run_card.py` (sha256 `e709408f7f6518be63fc00d5c4c444c8738dbf1ba7a53383c3821882c9054c9e`) calls exactly one product function,
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
  `e709408f7f6518be63fc00d5c4c444c8738dbf1ba7a53383c3821882c9054c9e`), so no card-specific runner can drift.

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

`frozen_unchanged_by_the_selfcheck = true` and
`frozen_still_equals_freeze_time_hashes = true`, so the corruption never touched the
frozen oracle. The exit-code scope is therefore empirically reachable: 0, 1, 2 and 3 were all
observed.

## 6. oq_rulings enumeration (script-derived counts)

`scripts/enumerate_driver_bounds.py` -> `evidence/M16/oq_enumeration.json` ->
`scripts/build_oq_rulings.py` -> `evidence/M16/oq_rulings.json`.
Enumerated by the implementer session by running that script against the isolated read-only copy
(automated; no human counting); **no independent reviewer has examined it yet**, and no reviewer
is named as an author. Counts: 31 registered models / 165 drivers / 40 ratio
drivers / 3 ratio drivers whose bounds are not [0,1]; for this model:
2 required, 1 optional,
**1 optional drivers without an explicit default**
(`other_revenue`), **1 signed & unbounded drivers**
(`other_revenue`), 2 drivers with a lower bound of exactly 0.0.

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

## 9. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M16.py --out-root <scratch attempt>` and diff the generated
   `input.json`/`cases.json`/`oracle.json` against the frozen ones; then re-run
   `scripts/run_card.py` and diff `run_result.json`.
2. Run `scripts/verify_card.py` and `scripts/verify_r2_boundary.py`; both must exit 0.
3. Confirm the isolated copy still hashes equal to production (`evidence/M16/source_manifest.json`,
   `after/source_hashes.txt`).
4. Confirm the frozen-body boundary: `before/oracle_md_v1.json` sha256 == sha256(oracle.md bytes
   before the single marker) (byte offset 8495), and that exactly one r2 section exists.
5. Read `evidence/M16/oq_rulings.json` and re-run the enumeration script to check the quoted counts.
6. Pick a case the implementer did not use and freeze its expectation **before** running it.
7. Adjudicate the OQ-01..OQ-04 items in `handoff.json` / `decision.md`.
