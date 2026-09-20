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
| F | `cases.json` 中 N02 的 `expected` 改成 `ValueError`（该例仍抛 `ModelRegistryError`） | **3** | 3 | 声明期望被**按精确类型名**强制：`ModelRegistryError` 是 `ValueError` 子类，若用 isinstance 就会漏过（`declared_expectation_mismatch=1`） |
| E | 未篡改副本 | **0** | 0 | 绿是可恢复的，不是一次性侥幸 |

冻结件在 A–F 之后重新 hash，与运行前一致（`frozen_evidence_unchanged: true`）。

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

## revision r2 — response to the independent review

Independent review of r1: **accepted_scoped（仅 formula 资格）**，并给出 2 项 P2、4 项 P3、1 项
明确要求的追加动作。本节**只追加**：上方正文（r1）除自检表新增 F 行外未改；**冻结期望、容差、
负例清单、拒绝条件一律未改**；产品仓零改动。除明确标注的 M17 `oracle.md` 追加节外，没有改任何冻结件。

### P2-1（runner 不比较 `cases.json` 的逐例 `expected`）→ 已按 (b) 修

- `scripts/run_card.py` 现在对每个负例比较**异常精确类型名**与 `cases.json` 的 `expected`：
  `declared_ok = isinstance(declared, str) and type(exc).__name__ == declared`；
  **不用 isinstance 做该比较**（`ModelRegistryError` 是 `ValueError` 子类，用 isinstance 会让
  `expected="ValueError"` 的篡改漏过）。判定优先级：不是目标类型 → `FAIL_wrong_exception_type`；
  是目标类型但声明不符 → `FAIL_declared_expectation_mismatch`；两者都成立 → `PASS_rejected`。
- 新增计数 `negative_counts.declared_expectation_mismatch`，`negative_summary` 增加
  `declared_expectations_in_cases_json` 与 `declared_expectation_comparison`；
  `negative_results.json` 的 `frozen_expectation` 不再是硬编码字符串，而是从冻结 `cases.json`
  逐例声明的集合导出，并标 `declared_expectations_enforced: true`。
- 第 11 节 rc=3 的口径同步改为"未被**按声明期望**拒绝"，并在 `run_result.json` 的
  `exit_code_semantics` 里写明；runner sha256 由 `9ea69c72…` 变为 **`5307d2cc…`**（四卡字节相同）。
- 新增第 6 个变异臂 **F**（篡改 N02 的 `expected` → `ValueError`）：实测 **rc=3**、
  `declared_expectation_mismatch=1`；B 臂现在也同时给出 `declared_expectation_mismatch=1`
  （未抛异常即声明未满足）。A/B/C/D/F 全红、E 恢复绿，`frozen_evidence_unchanged=true`。
- 真实运行（未篡改）：`declared_expectation_mismatch=0`、11/11 `PASS_rejected`、
  `verdict=pass`、`exit_code=0`；每条负例消息逐条记录在 `negative_results.json`。

### P2-2（`handoff.json` 的 OQ-05 是跨卡常量，与 M18–M20 的 review.md 自相矛盾）→ 已按卡参数化

- 复核人的**文件系统法证结论被采纳为事实基线**：M18/19/20 各只跑**1 趟**测量流水线；
  M17 的目录创建/文件写入时间差与"第 14 个目录晚创建"指纹成立。
- 但 G 时间戳只能区分"被重写过的世代数"，不能区分"argv 相同的多次执行"。实施 session 的记录是：
  **M17 = 3 趟测量执行**（13 单元 → 14 单元[探针常量仍 105.0] → 14 单元[常量更正为 90.0]），
  **M18/19/20 = 1 趟测量执行**（14 单元）；四卡另有 **6 趟收尾执行**（含本节所在的这一趟）。
  两个数字都写进 `process_history.json`：`measurement_pipeline_executions_declared` 与
  `rewritten_generations_forensically_visible`，并在 `forensic_explanation` 里说明何时二者会不同。
- **不采用"2 趟测量"作为执行次数**：它是可观测的**重写世代数**，与 session 记录的执行次数不是
  同一口径；若按 2 写会与本 session 的实际命令记录不符。两个口径都明示，读者可自行核对。
- **C2 单元的来源按卡区分**：M17 是"首趟之后新增"；M18/19/20 是"随模板交付的既有单元"。
  OQ-05 文本由 `scripts/write_handoff.py` 按卡生成（不再是常量字符串），并指向 `process_history.json`。
- 本节所在收尾趟之后，B/C2/E/G 四个单元各被**重新执行一次**（P2-1 与 P3-2 的修复），
  同样记入 `process_history.json` 的 `post_review_unit_reexecutions_declared`。

### P3-1（`oq_rulings.json` 无 OQ-05 条目）→ 已补

`evidence/M17/oq_rulings.json` 的 `rulings` 现为 `['OQ-01','OQ-02','OQ-03','OQ-04','OQ-05']`；
OQ-05 含 `requires_ruling_from: independent reviewer` 与 `pointer: process_history.json`。
`decision.md §3` 与 `review.md §7.5` 的引用因此成立。

### P3-2（M20 的容差探针举例低估 5 个数量级）→ M20 已修，M17 不适用

M17 的探针列表未变（该问题属 M20）。M20 的表述改为公式化并给出**实测**边界，见该卡 r2 节。

### P3-3（`pipeline_run.json` 无 passes/run_history）→ 已补 `process_history.json`

新增单元 **P-write-process-history** 产出 `process_history.json`：把"**观测到的**每个单元最后一次
执行（rc/开始/结束/stdout sha256）"与"**声明的**历史趟次（含被覆盖的更早执行）"分开记录，
并列出 `honest_gaps`（被覆盖的 stdout/rc、本文件自身所在趟只能算声明）。`handoff.json` 增加
`process_history_pointer` 与 `process_history_summary`。`pipeline_run.json` 保持原样（它只描述
最后一趟流水线，这一点现在由上述指针补齐）。

### P3-4（`review.md §7.5` 要求裁定不存在的 OQ-05）→ 随 P3-1 消解

### 复核人明确要求的追加动作（M17 `oracle.md`）→ 已执行，append-only

- 新增单元 **R2-append-oracle-addendum**，在**复核结论之后**作为独立命令执行，rc/stdout 单独留档：
  `evidence/M17/runs/R2-append-oracle-addendum/`。
- `oracle.md` **只追加** `## 13. 修订 r2（仅更正描述行，不动任何期望值）`；**§1 一个字符未改**，
  冻结期望、容差、判据一律未改；追加前 sha256 =
  `9c8021eebd01aa27a9963db8ac869ac6a067eb24af17439164f3cb61bc42fa69`，
  可在**真实行边界**（首个追加字节偏移 11768）截断复现：`truncated_prefix_equals_pre_append_hash=true`、
  `boundary_is_a_real_line_boundary=true`（记录见 `evidence/M17/oracle_addendum_record.json`）。
  节内写死三件事：错在何处 / 正确域与源码出处（`model_registry.py:265-269`、`:289-290`）/
  实测证据（`PROBE-NEG-MILESTONE`=90.0 被接受、`PROBE-NEG-TOTAL-REVENUE`=ModelRegistryError），
  并声明冻结期望未受影响、范围**仅限 M17**（M18/19/20 的 §1 行经复核正确）。
- `evidence/M17/revision_r2.json` 现为 `revision=r2`、`r2_sections_in_oracle_md=1`、
  `oracle_md_sha256_before_addendum=9c8021ee…`、`mechanism_proof` 为**对当前文件实时复验**
  （截断到 11768 后与追加前 hash 相等）。
- **一次失败执行也如实留档**：本单元**第一次**执行时追加正确（截断可复现追加前 hash），但边界
  判断比较了错误的字节范围，导致 rc=3；随后用 `--repair-restore`（双向 hash 校验：当前文件等于
  记录的追加后 hash、截断结果等于记录的追加前 hash）把 `oracle.md` **字节级还原**，修正比较后重新
  追加，rc=0。失败那一趟的原始 rc/stdout/stderr 与旧记录保存在
  `evidence/M17/runs/R2-append-oracle-addendum/first_execution_failed/`，并写进
  `oracle_addendum_record.json` 的 `repair_history`。因此 `oracle.md` 的
  `unchanged_since_generation=false` 是**预期**结果，其含义由
  `frozen_body_reproducible_by_truncation=true` 精确限定。

### 批次级两项（已在批次交接件落地）

- `execution_runs/M17-M20/a20260919-01/rc_namespace.json` + `batch_handoff.md`：
  按"卡 → runner sha256 → rc 语义"给出命名空间表（M17–M20 修复后 sha256 `5307d2cc…`：
  `1=harness`、`2=无判定`；M05–M08 `fd3a11c9…`：`2=harness`、未定义 1），并明文**禁止未标注命名空间的
  跨卡 rc 聚合**。
- 两处显眼位置写明"**`unmapped` 的含义是零产出，不是部分完成**"。

### 本次仍未验证 / 原样承接（不得当已证）

①M17 第 1 趟（13 单元）的原始输出已被后续执行覆盖，"首跑 13 单元全绿"只有本 session 的声明与
`process_history.json` 的声明口径；②`probe_extra.py` 常量曾为 105.0 无法由字节证据证明（只能给出
mtime 关系与声明）；③`oracle.md` 在各趟之间未被改写只能由"同字节改写 + 伪造 mtime"不可排除的方式
证明（r2 追加节额外提供了截断复现证据）；④M05–M08 结论未评估；⑤其它并发 session 未评估（本批
porcelain 行数与 M05–M08 目录内并发写入未归因）；⑥`PLAN\reviews` 全树扫描受权限限制；
⑦披露采集项与真实公司披露的对应关系未评估；⑧`_SIGNED_DRIVERS` 其余名字的业务正当性未评估；
⑨`oracle_M17.py` 未逐行审阅（独立性证据是行为层）；⑩`iso\venv` 未与模板做全树 hash 比对。

---

状态：`formula = review_pending`；`disclosure_adaptation = unmapped`（= **零产出**，不是部分完成）；
`accuracy = unproven`（完全未做评估）。实现者**未**自签 accepted。
