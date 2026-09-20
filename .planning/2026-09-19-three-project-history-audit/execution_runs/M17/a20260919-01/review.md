# M17 · implementer review record — licensing_commercial（商业销售与许可收入）

Card M17（`execution_v2/card_M17.md`），Parent I-10，model_id `licensing_commercial`，
attempt `execution_runs/M17/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`decision.md`、
`handoff.json` 一致。

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. 做了什么（可复核的清单）

| 步骤 | 结果 | 证据 |
|---|---|---|
| A 绑定 | 生产两文件只读复制进本 attempt，副本与生产 hash 相等；模型契约从隔离副本读回 | `binding.json`、`evidence/M17/source_manifest.json` |
| 冻结 | `oracle.md`（手算）→ `oracle.json`（独立 stdlib 脚本生成）→ 首次产品 stdout，mtime 顺序成立 | `evidence/M17/source_manifest.json` → `mtime_ordering` |
| B 正例 | 实测 `[110.0]` vs 手算期望 `[110]`，abs_diff 0.0，容差 1.1e-07 | `evidence/M17/stdout.txt`、`run_result.json` |
| B 保真 | 输出为扁平 `list`、长度 1 = `len(years)` = `len(expected)`、元素为普通有限 `float` | `run_result.json` → `fidelity` |
| B 连续性 | 实测 `[110.0, 169.0]` vs 期望 `[110, 169]` | `run_result.json` → `continuity_positive` |
| B 默认值 | 实测 `[80.0]` vs 期望 `[80]`（记录用，**不参与判定**） | `run_result.json` → `defaults` |
| C 负例 | 11/11 以 `ModelRegistryError` 拒绝；`ImportError`/文件错误单列计数且**不**计通过 | `evidence/M17/negative_results.json` |
| 保真重生成 | 同一脚本重生成 `input/oracle/cases.json`，三个文件 sha256 **逐字节相同** | `evidence/M17/oracle_regen_proof.json` |
| 变异证明 | 篡改**副本**后 runner 变红：rc 3 / rc 3 / rc 2 / rc 1；未篡改副本 rc 0；冻结件 hash 未变 | `evidence/M17/mutation_selfcheck.json` |
| 边界探针 | 非判定性实测：负数里程碑被接受(90.0)、总收入为负被拒 | `evidence/M17/extra_probes.json` |
| D/E/F | **未做**（D 需专业决策；E 属 I-10-A；F 需 I-12 冻结设计） | `decision.md`、`handoff.json` |

## 2. oracle 的独立性（本卡要害）

- 期望值来自 `scripts/oracle_M17.py`（stdlib：`argparse`/`hashlib`/`json`/`os`/`decimal`），
  `evidence/M17/oracle_selfcheck.json` 记录其 import 行且 `product_import_present = false`。
- runner `scripts/run_card.py` 只调用**一个**产品函数
  `calculate_registered_model(model_id, base_revenue, drivers, years)`，期望只从
  `evidence/M17/oracle.json` 读。
- 负例全部在内存中由**新的 deepcopy** 构造，不经 JSON 解析器（N01a 用真 `bool`，
  N01b-d 用真 `float('nan'/'inf'/'-inf')`），故"解析器拒绝"不可能冒充"模型拒绝"。
- `PASS_rejected` 要求 `isinstance(exc, model_registry.ModelRegistryError)`；
  `ImportError`/`ModuleNotFoundError`/`FileNotFoundError` 记为 **FAIL**。
- 卡片引用的行号（入口 308、注册 237）在隔离副本上**逐行复核**：
  `entry_point_anchor_ok=true`、`registration_anchor_ok=true`（`source_manifest.json`）。

## 3. 结果明细（含实际异常消息）

- registry formula：`revenue = treated_units * net_revenue_per_unit + milestone_revenue + royalty_revenue + service_revenue`
- required `['treated_units', 'net_revenue_per_unit']`；optional `['milestone_revenue', 'royalty_revenue', 'service_revenue']`；declared defaults `{}`
- effective bounds：`treated_units [0.0, inf]`、`net_revenue_per_unit [0.0, inf]`、
  `milestone_revenue/royalty_revenue/service_revenue ['-inf','inf']`（signed drivers）
- 11 个负例消息：
  - `NEG-CARD`：driver licensing_commercial.treated_units must be between 0.0 and inf: FY2027
  - `N01a`：licensing_commercial.treated_units.FY2027 must be numeric
  - `N01b/c/d`：licensing_commercial.treated_units.FY2027 must be finite
  - `N02`：driver licensing_commercial.treated_units must contain one value per forecast year
  - `N03`：missing drivers for licensing_commercial: treated_units
  - `N04`：unsupported drivers for licensing_commercial: unknown_driver
  - `N05a/b`：licensing_commercial.years must contain fiscal years
  - `CONT-BREAK`：licensing_commercial.years must be consecutive and increasing
- 退出码：产品单元 `B-product-run` 原始 rc = **0**（= 期望 0）；runner 打印值经回读校验与
  `run_result.json` 一致（`printed_matches_evidence_file: True`）。

## 4. 观察项与探针（均**不**参与退出码）

- `OBS-BASE-IGNORED`：`base_revenue=999` 时输出仍为 `[110.0]` → `_rowwise` 丢弃 `base_revenue`。
  这是设计观察：**本模型不吃 base_revenue**，若下游以为 `base_revenue` 会加进去就会错。
- `OBS-DEFAULT-EQUIV`：显式写三个金额项 `[0]` 与省缺结果相同（`[80.0]`）→ "默认 0"可被证伪。
- `PROBE-NEG-MILESTONE`：`milestone_revenue=[-5]` → `[90.0]`，**被接受**（signed 域）。
- `PROBE-NEG-TOTAL-REVENUE`：`milestone_revenue=[-200]` → `ModelRegistryError`（总收入为负）。

## 5. 请 reviewer 优先攻击的点

1. **`oracle.md` 第 1 节的描述性错误（已登记，未修补）。** 该行原写三个金额项为 `[0, inf)`；
   实测为 `(-inf, inf)`。冻结的期望值不受影响，`oracle.md` 有意未改（冻结件不得为贴合结果而改）。
   请判定"登记而非修补"是否可接受，或要求以 r2 追加节更正。
2. **负的"已确认金额"被接受。** 卡片 L8 称三个许可项为"已确认金额"，实现允许负数
   （`_SIGNED_DRIVERS`），唯一的负值守卫是**总收入不得为负**。这意味着单笔负数冲回可静默通过。
   请判定这属于契约缺口（需另立卡）还是命名/口径问题。
3. **单位错配与"潜在里程碑"完全不可运行时拒绝**（卡片 L45 的业务负例）。计算器只看数值域，
   因此 `disclosure_adaptation` 必须保持 `unmapped`；请确认没有把公式通过与披露适配混同。
4. **默认值 0 的来源。** 三个金额项的"默认 0"在注册表中**没有**显式 default 项，是被
   `spec.defaults.get(driver, 0.0)` 静默补的（`OQ-02`：31 个可选 driver 注册表级同现象）。
   对"里程碑未确认"这类字段，静默 0 与"我们没找到"不可区分。
5. **连续性用例的性质。** 本模型是逐年独立模型，`CONT-BREAK` 只是"财年不连续"的拒绝，
   不能当作存量桥证据；请确认第 4 节的 `not_applicable_with_reason`（存量桥）措辞无夸大。
6. **流程透明性：本 attempt 重跑过。** 首次流水线 13 个单元全绿后，发现 (a) `oracle.md` 描述行有误、
   (b) 缺少实测边界探针，于是**新增非判定性探针单元 C2 并修正了一个探针常量**
   （`PROBE-NEG-MILESTONE` 的期望从 105.0 改为 90.0：patch 是**替换**而非叠加，故
   `40×2+(-5)+5+10=90`），随后整条流水线重跑，14/14 单元 rc = 期望值。
   `oracle.md` 在两次之间**一字未改**，`oracle.json` 逐字节相同（`oracle_regen_proof.json`）。
   请判定这种"重跑 + 声明"是否满足"每次命令独立记录"的要求。
7. **隔离绑定的来源。** I-00-B 绑定的是隔离**方案**，未物化 checkout；本 attempt 自行物化只读快照
   （hash 与生产相等）。若预期是 I-00-B 物化的 checkout，属范围偏差，需 owner 裁定（`OQ-01`）。
8. **pytest 未安装。** `A0b` 单元实测离线探测 rc = 1（`--no-index --no-cache-dir`，无本地 wheel，
   网络禁用），故本 attempt 的 venv 内没有 pytest；本卡没有任何命令需要 pytest，
   且卡片明示历史 97 tests/216 subtests 不能替代本卡结果。

## 6. 本卡**不**主张什么

- 不主张模型准确，也不主张一家公司的映射可外推（`accuracy = unproven`）。
- 不主张 `disclosure_adaptation`：D 需要行业/会计 reviewer 签署的逐字段映射 + 一个已结束期间的
  收入对账 + 生产 forecast 入口映射经独立审阅；本 attempt 一个都未产出。
- 不重写公式：无独立反例且无经审定规格时保留现行实现（本卡零产品改动）。

## 7. 建议 reviewer 动作

1. 在 scratch 里重跑 `scripts/oracle_M17.py --card M17 --out-root <scratch>`，
   与冻结 `oracle.json/input.json/cases.json` 逐字节比对。
2. 重跑 `scripts/run_card.py`（argv 见 `commands.json` 的 `B-product-run`），比对
   `run_result.json` 与 `negative_results.json`。
3. 确认隔离副本 hash 仍等于生产（`evidence/M17/source_manifest.json`）。
4. 复算一个本卡未使用的 oracle：建议把 `treated_units` 换成 `[7]`、`net_revenue_per_unit` 换成 `[3]`，
   手算 7×3+15+5+10 = 41，先冻结再运行。
5. 裁定 `evidence/M17/oq_rulings.json` 的 OQ-01…OQ-05（其中 OQ-02 的计数已由
   `scripts/enumerate_registry.py` 的原始输出给出：31 个可选 driver 无显式 default）。

---

退出码自检（本卡自带，非 M05 共享）：见 `evidence/M17/mutation_selfcheck.json`。

| case | 篡改（仅作用于 `recovery/selfcheck/` 的副本） | 实测 rc | 期望 rc | 证明 |
|---|---|---|---|---|
| A | `oracle.json` 的 `positive.expected_float` 每个值 +1 | **3** | 3 | 被篡改的期望无法躲在 rc=0 后面 |
| B | `cases.json` 的 N04 驱动名换成已注册的 `milestone_revenue` | **3** | 3 | 未被拒绝的负例会被判为负 |
| C | `oracle.json` 的 `positive.expected_float`/`tolerances` 各多一项 | **2** | 2 | 保真不符时 runner 拒绝给判定 |
| D | scratch 副本删除 `cases.json` | **1** | 1 | harness 失败与判定失败可区分 |
| E | 未篡改副本 | **0** | 0 | 绿是可恢复的，不是一次性侥幸 |

冻结件在 A–E 之后重新 hash，与运行前一致（`frozen_evidence_unchanged: true`）。

### 记录收尾单元（不产生任何产品行为）

`H-write-handoff`（从磁盘证据生成 `handoff.json`）与 `Z-close-attempt`（写 `commands.json` 与
`after/final_deliverable_hashes.json`）在测量流水线之后**单独**由 `scripts/run_closing.py` 执行，
各有独立 command-run-id 记录：`evidence/M17/runs/H-write-handoff/`、`evidence/M17/runs/Z-close-attempt/`。
`commands.json` 由 Z 自己写，所以 Z 自己的 rc.json 是在它返回**之后**才刷新的：`commands.json` 中
Z 的 `raw_rc`（当前为 0）来自**同 argv 的上一次执行**，该口径已写进 `commands.json` 里该单元的
`raw_rc_note`；**最近一次执行**的 raw rc 始终在 `evidence/M17/runs/Z-close-attempt/rc.json`
（该文件自述其 stdout/stderr 的 sha256）与 `pipeline_run.json`。这是"可复现、不编造"的写法，
不是把未知填 0。`after/final_deliverable_hashes.json` 按构造排除它自己与 `runs/Z-close-attempt/**`
（原因写在该文件的 `excluded_from_the_table` 字段里）。

---

状态：`formula = review_pending`；`disclosure_adaptation = unmapped`；`accuracy = unproven`。
