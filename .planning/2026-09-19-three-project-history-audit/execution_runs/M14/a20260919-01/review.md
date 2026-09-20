# M14 · retail_franchise — implementer review record

Card M14 (`retail_franchise`), Parent I-10, card title `M14 · retail_franchise · 直营加盟与供应收入`.
Attempt `execution_runs/M14/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M14/source_manifest.json`, `before/setup_receipt.json` |
| B positive | `[65.0]` vs independent oracle `[65.0]`, tolerance [6.5e-08]; structure/length/type/finiteness faithful | `evidence/M14/formula_result.json`, `verify_report.json` |
| continuity positive | actual `[65.0, 84.8]` vs oracle `[65.0, 84.8]` | `evidence/M14/run_result.json` |
| defaults case | actual `[50.0]` vs oracle `[50.0]` (not gating) | `evidence/M14/run_result.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M14/negative_results.json` |
| mutation proof | scratch copies corrupted -> rc 2/2/2, rc 3, rc 1; control rc 0; frozen hashes unchanged | `recovery/selfcheck_result.json` |
| OQ enumeration | 31 models / 165 drivers / 40 ratio drivers enumerated by script; counts quoted, not typed | `evidence/M14/oq_enumeration.json`, `oq_rulings.json` |
| D mapping | **NOT DONE** - this attempt is the synthetic formula scope only; nothing is claimed | `evidence/M14/qualification.json` |
| E probe | **NOT DONE** (needs D and I-10-A) | - |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M14/qualification.json` |

Runner verdict: `pass`, exit code `0`, triggered conditions `[]`
(`evidence/M14/run_result.json` -> `exit_code_semantics`).

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M14.py`, which imports only `argparse`, `hashlib`,
  `json`, `os`, `time` and `decimal` (see `import_lines` in
  `evidence/M14/oracle_selfcheck.json`). It never imports `model_registry` or
  `model_extensions`; `product_import_present` is `false`.
- `scripts/run_card.py` (sha256 `e709408f7f6518be63fc00d5c4c444c8738dbf1ba7a53383c3821882c9054c9e`) calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only
  from `evidence/M14/oracle.json`.
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

- Registry formula observed from the isolated copy: `revenue = average_owned_stores * revenue_per_owned_store + franchise_system_sales * recognized_fee_rate + supply_revenue`
- Registry required: `["average_owned_stores", "revenue_per_owned_store"]`; optional: `["franchise_system_sales", "recognized_fee_rate", "supply_revenue"]`; defaults: `{}`;
  explicit driver_bounds: `{}`
- Effective bounds enumerated from the isolated copy: `{"average_owned_stores": [0.0, "inf"], "revenue_per_owned_store": [0.0, "inf"], "franchise_system_sales": [0.0, "inf"], "recognized_fee_rate": [0.0, 1.0], "supply_revenue": [0.0, "inf"]}`
- Hand work (from `oracle.md`, decimal, unrounded): 10 × 5 = 50；200 × 0.04 = 8；50 + 8 = 58；58 + 7 = 65
- Continuity hand work: FY2027 = 10×5 + 200×0.04 + 7 = 50 + 8 + 7 = 65；FY2028 = 12×5.5 + 240×0.045 + 8 = 66 + 10.8 + 8 = 84.8
- Defaults hand work: 10 × 5 + 0 × 0 + 0 = 50（三个 optional driver 全部回落到 0.0）
- Rejections and their messages (verbatim from `negative_results.json`):

| Case | Rejection message | Verdict |
|---|---|---|
| `NEG-CARD` | `driver retail_franchise.recognized_fee_rate must be between 0.0 and 1.0: FY2027` | `PASS_rejected` |
| `N01a` | `retail_franchise.average_owned_stores.FY2027 must be numeric` | `PASS_rejected` |
| `N01b` | `retail_franchise.average_owned_stores.FY2027 must be finite` | `PASS_rejected` |
| `N01c` | `retail_franchise.average_owned_stores.FY2027 must be finite` | `PASS_rejected` |
| `N01d` | `retail_franchise.average_owned_stores.FY2027 must be finite` | `PASS_rejected` |
| `N02` | `driver retail_franchise.average_owned_stores must contain one value per forecast year` | `PASS_rejected` |
| `N03` | `missing drivers for retail_franchise: average_owned_stores` | `PASS_rejected` |
| `N04` | `unsupported drivers for retail_franchise: unknown_driver` | `PASS_rejected` |
| `N05a` | `retail_franchise.years must contain fiscal years` | `PASS_rejected` |
| `N05b` | `retail_franchise.years must contain fiscal years` | `PASS_rejected` |
| `CONT-BREAK` | `retail_franchise.years must be consecutive and increasing` | `PASS_rejected` |
- `NEG-CARD` is refused by the **value/domain guard**, not by the array-length guard
  (`driver retail_franchise.recognized_fee_rate must be between 0.0 and 1.0: FY2027`) - the failure mode this batch previously suffered from.

## 4. Observations (NOT pass/fail; they do not enter the exit code)

| ID | Mutation / base | Observed | Why recorded |
|---|---|---|---|
| `OBS-BASE-IGNORED` | set_base_revenue | `[65.0]` | the rowwise calculator discards base_revenue; design observation only, not a pass condition |
| `OBS-BOUND-INCLUSIVE` | set_driver_element | `[257.0]` | the ratio domain is INCLUSIVE at the upper edge: 1.0 is accepted while NEG-CARD's 1.1 is refused; records the edge, does not gate |
| `OBS-SUPPLY-BOUND` | set_driver_element | raised `ModelRegistryError` | supply_revenue is NOT a signed driver in this registry, so a negative supply sale is refused by the driver bound (lower bound 0.0) rather than by the non-negative-revenue check; records the contract boundary, does not gate |


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

`frozen_unchanged_by_the_selfcheck = true` and
`frozen_still_equals_freeze_time_hashes = true`, so the corruption never touched the
frozen oracle. The exit-code scope is therefore empirically reachable: 0, 1, 2 and 3 were all
observed.

## 6. oq_rulings enumeration (script-derived counts)

`scripts/enumerate_driver_bounds.py` -> `evidence/M14/oq_enumeration.json` ->
`scripts/build_oq_rulings.py` -> `evidence/M14/oq_rulings.json`.
Enumerated by the implementer session by running that script against the isolated read-only copy
(automated; no human counting); **no independent reviewer has examined it yet**, and no reviewer
is named as an author. Counts: 31 registered models / 165 drivers / 40 ratio
drivers / 3 ratio drivers whose bounds are not [0,1]; for this model:
2 required, 3 optional,
**3 optional drivers without an explicit default**
(`franchise_system_sales`, `recognized_fee_rate`, `supply_revenue`), **0 signed & unbounded drivers**
(none), 5 drivers with a lower bound of exactly 0.0.

## 7. Judgement calls the reviewer should attack first

1. **`defaults` 与 `observations` 不参与退出码。** 有人会主张失败的观察项至少应触发 rc=2；
  本 runner 的契约是显式的（只有正例/连续性保真与拒绝条件 gate），且
  `exit_code_semantics.triggered` 会列出全部触发条件——但这是有意的范围选择，不是疏漏。
2. **rc=2 会遮蔽 rc=3。** 优先级 `1 > 2 > 3`：正例不符与未被拒绝的负例同时成立时返回 2，
   但 `triggered` 仍列出 `negative_case_not_rejected`。是否需要与顺序无关的判定码由 reviewer 决定。
3. **`base_revenue` 被丢弃。** 注册表校验 `base_revenue` 非负，但 `_rowwise` 直接丢弃它；
   本模型看不出影响，reviewer 应确认这是契约事实而非本卡的实现选择。
4. **加盟系统销售的量纲被当作 U（金额）而非数量。** `franchise_system_sales` 的 dimension 是 `revenue`，
   即实现假定它是"已折成金额的系统销售额"；卡片 L8 说它乘确认费率，语义一致，
   但 reviewer 应确认这与"GMV 不能全部并表"（L45）在披露适配阶段如何衔接。
5. **`supply_revenue` 非带符号**：内部抵销（退货/返利）若为负，会在 driver 守卫处被整行拒绝，
   而不是留待会计处理。是否需要扩展属 D/E 阶段决定。
6. **隔离 checkout 的 provenance（OQ-01）。** I-00-B 只绑定隔离方案与两阶段命令规则，未物化 checkout 树；
   本 attempt 自建只读快照。若 owner 期望 I-00-B 物化 checkout，则属范围偏差，被测代码字节相同。
7. **未安装 pytest。** 本地 pip 缓存没有可离线安装的 pytest wheel，装它需要联网（禁止）；
   本卡 A–C 不需要重跑历史套件，且未执行任何 pytest 命令。若 reviewer 要求历史套件，需显式说明，
   因为那会改变本 attempt 的范围。

## 8. What this card does NOT claim

- 不声称模型准确，也不声称任何映射可泛化。
- 不声称 `disclosure_adaptation`（本 attempt 没有任何真实公司披露映射，保持 `unmapped`）。
- 不改写公式：在没有独立反例、也没有经审定规格的情况下保留既有实现。
- 不声称合成正例能证明真实加盟商业务的任何结论（例如"加盟系统销售可全额并表"——卡片 L45 明确拒绝）。

## 9. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M14.py --out-root <scratch attempt>` and diff the generated
   `input.json`/`cases.json`/`oracle.json` against the frozen ones; then re-run
   `scripts/run_card.py` and diff `run_result.json`.
2. Run `scripts/verify_card.py` and `scripts/verify_r2_boundary.py`; both must exit 0.
3. Confirm the isolated copy still hashes equal to production (`evidence/M14/source_manifest.json`,
   `after/source_hashes.txt`).
4. Confirm the frozen-body boundary: `before/oracle_md_v1.json` sha256 == sha256(oracle.md bytes
   before the single marker) (byte offset 9367), and that exactly one r2 section exists.
5. Read `evidence/M14/oq_rulings.json` and re-run the enumeration script to check the quoted counts.
6. Pick a case the implementer did not use and freeze its expectation **before** running it.
7. Adjudicate the OQ-01..OQ-04 items in `handoff.json` / `decision.md`.
