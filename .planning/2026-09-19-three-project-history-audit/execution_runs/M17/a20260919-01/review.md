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

---

## revision r2 review — 独立 reviewer 的 r2 判定（原文转录，不得改写）

判定：**changes_required**（四卡一致：M17 / M18 / M19 / M20）。
**范围严格限定**：本判定只针对 r2 交付物中的"审计元数据"，**不针对公式**。
公式资格的证据经 r2 复核**未发生变化、且仍然成立**：四卡 12 个冻结文件
（input.json / oracle.json / cases.json）的 sha256 与本 reviewer r1 记录逐一相同；
run_result.json 仍为 verdict=pass、rc=0、11/11 PASS_rejected、declared_expectation_mismatch=0；
runner 5307d2cc… 经注入测试证明按**精确类型名**比较声明期望（下详）。
因此：**完成下列 3 项 P2 与 2 项随附动作后，四卡 formula 可签 `accepted_scoped`（仅 formula）**，
且**不需要重跑任何产品测量**。
未授予：disclosure_adaptation 保持 `unmapped`（= 零产出，非部分完成）；accuracy 保持 `unproven`。
P1 = 0（无应拒被接受、无假绿、无公式反例）。

### 已闭合（r1 的 P2/P3）
- r1-P2-1 **闭合**：`run_card.py` 现按精确类型名比较 `cases.json` 的逐例 `expected`。
  本 reviewer 自建两组注入验证区分度：
  (a) 声明被篡改而实际类型正确（N02.expected:="ValueError"）→ rc=3、mismatch=1、FAIL_declared_expectation_mismatch（r1 时该注入为 rc=0）；
  (b) 声明正确而实际类型被替换为其**子类**（注入 `_ReviewerSubclassProbeError(ModelRegistryError)`，isinstance 仍为 True）→ rc=3、mismatch=1。
  第 (b) 组是决定性证据：若实现退回 isinstance 比较，该例会被误判为 PASS_rejected。第 6 变异臂 F 亦独立复现（rc=3）。四卡结果逐行相同。
- r1-P2-2 **闭合**：M18/19/20 的 OQ-05 现为按卡生成（"executed 1 time(s)"，C2 来源按卡区分），与 M18 review.md §5.6 一致，r1 的自相矛盾消除。
  M17 的"3 趟测量执行（声明）vs 2 个重写世代（法证可观测）"**并存处理诚实、可接受**：两个数各自标注口径、差异被显式解释（process_history.json 的 forensic_explanation 与 declared_vs_observed），且实现者明确拒绝把 3 改写成 2。本 reviewer 的 r1 法证只能给出"≥2 个写入世代"，与 3 相容但不能证实；不视为失真。
- r1-P3-1 **闭合**：四卡 oq_rulings.json 现含 OQ-01…OQ-05。
- r1-P3-2 **闭合**（M20）：改为公式化容差 + 带内/带外实测；其数值得本 reviewer 独立复现（1.2e-7 → [195.0, 240.00000024]；1.201e-7 → ModelRegistryError）。
- r1-P3-3 **闭合**：新增 P-write-process-history 单元与 process_history.json。
- r1-P3-4 **闭合**：随 P3-1 消解。
- **本 reviewer r1 明确要求的冻结件动作已正确完成**：M17 oracle.md 追加 `## 13. 修订 r2`，append-only。
  独立验证：截断到 11768 字节 → sha256 9c8021ee…（= 追加前 hash，逐位相同）；11768 前一个字节为 LF（真实行边界）；
  行 184/185 为空行、行 186 为 `## 13.` 标题；r2_sections_in_oracle_md=1（无重复追加）；
  失败首趟与成功趟的 post-append hash 均为 c9971428…（⇒ --repair-restore + 重新追加是无损往返，**无不可逆污染**）；
  M18/19/20 的 oracle.md 未变。失败趟的 rc=3 与原始 stdout/stderr 如实留档于 runs/R2-append-oracle-addendum/first_execution_failed/。
  本 reviewer 认可 `unchanged_since_generation=false` 是**正确**取值，其含义由 frozen_body_reproducible_by_truncation=true 精确限定。

### 必须修改（P2）
- **P2-A【四卡】两张 hash 清单表未达 drift=0，且相对 r1 是回归。**
  本 reviewer 逐条复算：after/final_deliverable_hashes.json 漂移 M17=25/151、M18=24/142、M19=24/142、M20=25/142；
  evidence/<CARD>/evidence_hashes.json 漂移 M17=14/100、M18=13/91、M19=13/91、M20=14/91。
  漂移项的 sha256 **与 size_bytes 同时不符**（例：M17 commands.json 声称 66917，实际 65909）。
  时序证据：表内 generated_utc = 03:16:24–03:16:28，而每一个漂移项的磁盘 mtime 均为 03:17:53
  ⇒ 表是"最后一次写盘之前"的快照。r1 时同一张表实测为 135/135、drift=0 ⇒ 这是 r2 引入的回归。
  因此简报中"修后两表逐条复算 drift=0"**不可复现，必须撤回或改述**。
  修法：让写表严格成为最后一次写盘；表内写 drift_count/verified_utc；收尾单元在 drift_count!=0 时非零退出；
  排除清单必须恰好覆盖自指文件（表自身、Z 自己的 capture 记录、recovery/closing_run.json、recovery/r2_run.json）；
  修完重跑一次收尾序列并给出实测 drift_count=0。
- **P2-B【批次】rc_namespace.json 不是合法 JSON。**
  本 reviewer 对四卡 attempt + 批次目录共 249 个 .json 做全量解析扫描，唯一失败者即此文件
  （Expecting value: line 11 column 29）：其 runner_sha256_note 使用了 Python 风格的括号内隐式字符串拼接，JSON 不允许。
  该文件是"禁止未标注命名空间的跨卡 rc 聚合"这条硬要求的机器可读副本，必须可被机器读取。
  修法：合并为单个字符串 + 单元内加 json.load 回读自检 + 把"249 个 JSON 全部可解析"作为实测输出。
- **P2-C【M17】两个追加记录文件互相矛盾，且各自含一个错值。**
  revision_r2.json 的 mechanism_proof.line_boundary_is_real = **false**（错，且与紧邻的 note 自相矛盾），
  而 oracle_addendum_record.json 的 boundary_is_a_real_line_boundary = **true**（对）；
  oracle_addendum_record.json 的 added_section_header_line_number = **184**（错），
  而 revision_r2.json 的 r2_section_locations[0].line_number = **186**（对；本 reviewer 实读文件确认行 186 为 `## 13.`）。
  根因定位到两行实现：pack_card.py:160 把"是否为真实行边界"误写成"该偏移是否指向 `## ` 标题"；
  append_oracle_addendum.py:155 用追加前前缀的换行数计算标题行号。
  影响：只读 revision_r2.json 的人会得出"追加前 hash 未能在真实行边界复现 ⇒ 冻结纪律被破坏"这一**错误且严重**的结论，而事实相反。
  修法：修正那两行；重生成这两个 JSON；**oracle.md 必须保持 c9971428… 不变、r2_sections_in_oracle_md=1**，
  不得再次追加或截断（若偏好 append-only，可在这两个 JSON 内追加 boundary_metadata_correction，但不得只修一个）。

### 随附（P3，应与 P2 同批处理）
- **P3-1**：`--repair-restore` 这次对冻结 oracle.md 的破坏性操作**没有独立命令记录**
  （commands.json 的 18 个单元中无任何 repair 条目）。结果状态我已独立验证（无损往返、纯追加），
  缺的是该次调用的 argv/rc/stdout 自证。请补记录，或写明 honest_gap。
- **P3-2**：`verdict_reasons` 把"声明不符"误报为 `negatives_not_rejected:<id>`
  （本 reviewer 的 I1/I2/I6/I7/I8 五组注入均如此，而那些例子里产品确实抛了 ModelRegistryError）；
  且 `declared_expectation_mismatch` 计入了"未抛异常"的情形（I5 注入：raised=None 而该计数=1），不是互斥分类。
  请把 reason 改为中性表述（如 negatives_failed:<ids>）并让两个计数互斥。
- **P3-3**：`cases.json` 缺少 `expected` 键时实测 rc=3/FAIL_declared_expectation_mismatch，
  而 oracle.md §11 与 rc_namespace.json 把"冻结期望缺失"定义为 rc=2。请二选一：
  代码上把负向声明缺失归入"无判定"，或把 rc=2 的适用范围明确限定为"仅正向冻结期望缺失"。
- **P3-4**：process_history.json 的 closing_passes 声明 6 趟（末趟 03:16:24.624 结束），
  但 **03:17:53 那一代写入未被任何一趟命名**（含 commands.json、handoff.json、recovery/closing_run.json、
  recovery/selfcheck_result.json、recovery/selfcheck/*、runs/{B,C2,E,G-pack,H,Z}/rc.json、12 个 evidence/MXX/*.json）；
  且 commands.json 中 Z 的 rc_recorded_utc = 03:15:17.812，早于最后一次 Z 执行（03:16:24.087）。
  请命名该代或写明 `additional_unnamed_generations >= 1` 的 honest_gap。
  另：`declared_vs_observed.reconciliation` 是跨卡常量，文案写 "differ for M17" 却被复制到 M18/19/20（那三卡 declared=1=observed=1），请按卡参数化。
- **P3-5**：`revision_r2.json.independent_review_received=true` /
  `independent_review_verdict_received="accepted_scoped (formula qualification only)"`
  是本 reviewer **r1 headline 的忠实转录**（不是自签，不算失实），但它省略了 r1 附带的两项 P2 条件，
  且在 r2 判定为 changes_required 之后会被读成"复核已签收"。
  请**追加**（勿覆盖）r2 结论字段；batch_handoff.md 第 7-8 行的同一表述也请补上 r2 结论。
- **P3-6（可选，一行）**：review.md §5.6 的 r1 正文仍叙述 2 趟，与 process_history.json 的 3 趟并存；
  r2 节已解释口径，建议加一句交叉引用。

### 跨批复用意见（应要求给出）
5307d2cc… 的"精确类型名"比较**可以作为跨批复用方案**：本 reviewer 扫描了**全部 31 张卡**的冻结 cases.json，
其声明集合**无一例外**恰好是 `'ModelRegistryError'`，故严格等值比较不会在任何现存卡上产生假红。前置条件四项：
(1) 保持精确类型名语义，不得退回 isinstance；
(2) 写入 schema 约束并登记"`expected` 只能是裸异常类型名"——本 reviewer 的 I8 注入证明把声明写成
    M20 卡片 L123 自己使用的复合写法 `"ModelRegistryError/continuity"` 会得到 rc=3（假红），
    今天 31 张卡都不是复合写法，故不是现存缺陷，但未来照抄卡片原文的卡会红；
(3) 先修 P3-2/P3-3，否则新批次继承这两个新问题；
(4) 逐批按 runner sha256 登记命名空间。实测当前各批 runner：
    M01–M04 b5fcc685（无声明强制）、M05–M08 fd3a11c9（无）、M09–M12 997c553b（无）、
    M13–M16 9e4a6450（有，机制不同）、**M17–M20 5307d2cc（有，精确类型名）**、
    M21–M24 d02057de（无）、M25–M28 eab01162（有，机制不同）、M29–M31 9ea69c72（无）。
    ⇒ 简报"那些批的副本仍是 fd3a11c9/9ea69c72"只对 **M05–M08 与 M29–M31** 成立，其余批次各有不同状况。

### 本次仍未验证 / 原样承接（不得当已证）
r1 的 11 条未验证项全部保留，另加：
1. M17 `measurement_pipeline_executions_declared=3` 无法独立证实（字节证据只给出"≥2 个写入世代"，3 与其相容但不可证；已正确标注为 declared）；
2. `closing_executions_declared=6` 与文件系统不一致（至少 03:17:53 那一代未被命名）；
3. 03:17:53 那一代写入的**触发者**无法确定（只证明其存在，不做推测性归因）；
4. `--repair-restore` 的原始输出未留档，其"双向校验通过"只有声称；我验证的是结果状态；
5. M13–M16/M25–M28 的声明一致性机制只做关键字级判别，未评估其等价性，也未评估这些批次任何交付质量；
6. M21–M24/M25–M28/M29–M31 的 rc 语义未核验，不推断；
7. M19/M20 的 r2 节我只读开头 1400 字符与关键字命中统计，未逐字读完；
8. M17/M18/M19 的探针列表未逐条重跑（仅重核 M20 的 BAND 一对数值）。

—— 独立 reviewer，2026-09-20T03:25Z，零写入模式（写入仅限 %TEMP%\m17m20-review-r2-20260920-041815\）


### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。要点：
①上方法庭级判定与"必须修改（P2）"三项、随附 P3-1…P3-6 已逐条处置，处置证据见本卡
`review.md` 的 r2 处置节、`evidence/M17/oq_rulings.json`、`evidence/M17/revision_r2.json`、
`process_history.json`、`after/final_deliverable_hashes.json`（含 `drift_count`/`verified_utc`）与
`evidence/M17/hash_table_selfcheck.json`；
②实现者**未**自签 accepted：`formula` 仍为 `review_pending`，等 reviewer 点审；
③§5.6 的 r1 正文写"2 趟"是 r1 当时的口径，与 `process_history.json` 的"声明 3 趟测量执行"并存，
两者口径已在 r2 节与 `process_history.json.forensic_explanation` 中显式说明（**交叉引用，不改写 r1 正文**）；
④`disclosure_adaptation = unmapped`（零产出）；`accuracy = unproven`。

---

## revision r3 review — 独立 reviewer 的最终判定（原文转录，不得改写）

判定：**accepted_scoped（仅 formula 资格）** —— M17 / M18 / M19 / M20 四卡同判。

**授予范围严格限定为 formula。**
未授予 `disclosure_adaptation`（保持 `unmapped`，含义是**零产出**：四卡证据树中不存在
`disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、
`forecast_integration.json`，不是"部分完成"）；未授予 `accuracy`（保持 `unproven`，一次评估都没做，
I-12 冻结设计不存在）。本判定不构成、也不得被用于推导任何披露适配或准确性结论。
实现者未自签：`formula.state` 仍为 `review_pending`、`handoff.json.status = review_pending`。

**P1 = 0，P2 = 0。** 指定的六项验证全部通过，逐项证据如下。

### ① 两张 hash 表真的 drift=0，且由 V 单元在收尾之后实测 —— 通过
- 我全量复算冻结世代 8 张表：M17 evidence 108 / final 167、M18–M20 evidence 94 / final 153，
  **逐条 drift=0、missing=0**；两表自述 `drift_count/missing_count/verified_utc/drifted_paths` 齐备，
  `hash_table_selfcheck.json` 与之一致。
- V 在 Z 之后：四卡 `H → Z → V` 时间戳依次递增（V 于 03:44:36.236 / 38.628 / 40.746 / 42.651 开始，
  Z 分别于 03:44:36.082 / 38.463 / 40.572 / 42.513 结束），V 的权威 rc.json 四卡 `raw_returncode=0`。
- 我自造污染并做了四段测试（我自己临时副本、真实 argv）：
  干净副本 **rc=0 drift=0** → 污染 `qualification.json` **rc=3 drift=1+1** →
  再污染 `oracle.md` **rc=3 drift=2+2** → 两文件逐字节还原 **rc=0 drift=0**。
  ⇒ "drift=0" 是被测量的输出，该单元在污染时变红、还原后恢复绿。
- 上一轮"修后两表逐条复算 drift=0"的主张**已按实现者自述撤回**，改述为"表内 drift_count + V 单元在
  verified_utc 的实测"——本 reviewer 认可该改述，并确认撤回是必要的（上轮我测到 24–25 条漂移）。

### ② `rc_namespace.json` 合法 + 280 个 JSON 全量可解析 —— 通过
我独立扫描同一范围：**scanned=280，unparseable=0**；`rc_namespace.json` 可被 `json.load` 解析，
含四个命名空间（M17–M20 修复前后、M05–M08、以及显式的 "other batches … NOT VERIFIED BY THIS BATCH"），
M17–M20 修复后 runner sha256 = `94619a98…`，rc=2 语义已把"任何用例声明的 `expected` 不可用"纳入。

### ③ P2-C 两处根因已修且两文件一致；`oracle.md` 确未变 —— 通过
`revision_r2.json.mechanism_proof.line_boundary_is_real = true`、
`oracle_addendum_record.json.added_section_header_line_number = 186`，两者
`boundary_byte_offset = 11768`、`added_section_header_byte_offset = 11770`，且两文件各自**追加**了
`boundary_metadata_correction`（保留旧值 false / 184 与更正后值）。
`oracle.md` 实测 `sha256 = c9971428…`、14234 B、214 行、r2 节数 = 1（标题在第 186 行），
截断到 11768 字节复现追加前 hash `9c8021ee…` ⇒ **未再追加、未再截断**。
`--repair-restore --dry-run`（R2b）与 `--rebuild-record-only`（R2c）各有独立 rc 留档，
原始 `--repair-restore` 已按我的 P3-1 以 `declared_unrecorded_commands` 登记 argv 与 `captured=false`。

### ④ 互斥分类与 rc=2 语义 —— 通过
我自造臂复现（新 runner `94619a98…`）：
臂 B（N04 不抛）→ **rc=3**、`reasons=['negatives_not_rejected:N04']`、`not_rejected=1`、`mismatch=0`；
臂 F（N02 声明篡改为 `ValueError`）→ **rc=3**、`reasons=['declared_expectation_mismatch:N02']`、
`mismatch=1`、`not_rejected=0`；
臂 G（删除 N02 的 `expected`）→ **rc=2**、`verdict=no_verdict`、
`reasons=['cases_json_declared_expectation_missing:N02']`、该例 `NOT_JUDGED_declaration_unusable`。
交付件 `mutation_selfcheck.json` 含七臂 `A=3 B=3 C=2 D=1 F=3 G=2 E=0`，`frozen_evidence_unchanged=True`。

### ⑤ 转录逐字节 —— 通过
我从自己 r2 报告的 ```markdown 围栏按字节重抽：verdict 块 **11463 B**、batch 块 **1318 B**，
sha256 分别为 `6cc56b43c8f28a2f…` / `d7ee0baabeb14a09…`，与 `transcription_proof.json` 记录一致；
四卡 `review.md` 与 `batch_handoff.md` 中**各恰好出现 1 次**且逐字节相同，我的正文之后紧跟
`### 实现者附注（非 reviewer 文字，另起一段以便区分）` ⇒ 转录忠实、作者分离清晰。

### ⑥ 新 runner 的跨批复用前置 —— 满足 3/4
(1) 精确类型名语义保持：我重放"声明正确但实际异常被替换为 `ModelRegistryError` 的**子类**"
（isinstance 仍为 True）→ **rc=3**、`FAIL_declared_expectation_mismatch` ⇒ 退回 isinstance 会漏过，故语义正确；
(3) P3-2/P3-3 已修（见 ④）；
(4) 命名空间表按 runner sha 逐批登记；
**(2) 未闭合**：`cases.json.expected` 必须为"裸异常类型名"这一约束**仍未文档化**。我重放
复合声明注入（`"ModelRegistryError/continuity"`，即 M20 卡片 L123 自己的写法）→ **rc=3 假红**。
今天 31 张卡的声明集合**无一例外**恰为 `'ModelRegistryError'`（我重新全量扫描确认），
故不构成现存缺陷，属**前向风险**：任何未来卡若照抄卡片原文的 `expected_negative` 就会红。
⇒ 复用该 runner 前，请在 runner docstring、`rc_namespace.json` 与批次交接各加一句
"`expected` 只能是裸异常类型名；复合原因写进 `why`"，或让比较接受 `declared.split('/')[0].strip()`。

### r3 遗留（全部 P3，不阻断本判定；修法只许追加或重算记录，`oracle.md` 禁止再改）
- **P3-A**：`card_units.verifier_units()`（含 V）**没有任何 driver 执行**——`run_closing.py` 只调用
  `closing_units`，而 `verifier_units` 仅被 `write_commands.py` / `write_process_history.py` 用于罗列；
  `recovery/closing_run.json` 的 units 也不含 V。V 的 argv/rc/stdout 已完整留档且我已用该 argv 手工复现，
  但"最后一步"不可由单一命令复现。修法：`run_closing.py` 先跑 `closing_units` 再跑 `verifier_units`
  （一行），或新增 `run_verify.py` 驱动并在 `review.md`/`handoff.json` 写明 V 的执行方式。
- **P3-B**（M18/19/20）：`revision_r2.json.mechanism_proof.prefix_hash_equals_base_hash = false` 是
  scratch 演示把截断点放在 marker 偏移（= base 长度 + 1）所致；我实测在 **base 长度**处截断即可复现
  base hash（`d8be42a9…` / `a55fa54d…` / `b43abd8d…`，均 True）。该字段对无追加节的三卡是**空泛值**
  （`r2_sections_in_oracle_md=0`、`frozen_body_reproducible_by_truncation=null`），但与相邻的
  `line_boundary_is_real: true` 并排会被读成自相矛盾。修法（记录级，`oracle.md` 不动）：
  演示分支改在 base 长度处截断，或加 `"applicable": false`。
- **P3-C**：见 ⑥(2)。
- **P3-D**：`declared_expectation_not_met` 是 `not_rejected` ∪ `declared_expectation_mismatch` 的**并集**计数
  （我的臂 B 得 1/0、臂 F 得 1/1），建议在 `exit_code_semantics.reason_namespace` 里明写这一点，
  以免被当成 `declared_expectation_mismatch` 的别名。
- **P3-E（环境）**：父 agent 简报里的表 hash（`d19d4180…`/`7b717ac9…`/`7ca8db2c…` 等）与
  "evidence 条目 109/94/94/94"属**已被 03:44 收尾覆盖的 03:40 世代**；冻结世代实测为
  M17 final `d71860ae…` / evidence `19fe0c7a…`、M18 `05fbeba7…`/`ba7eeeb7…`、
  M19 `7057b921…`/`29892747…`、M20 `fc14f74c…`/`c76d14e3…`，证据表条目为 **108**/94/94/94。
  核验请以上列值为准。

### 环境事实与本 reviewer 的读数为准范围
1. **卡目录在本次复核期间仍在被写入（moving target）**：我 03:42:53Z 开始抓取 hash 后，实测到
   `scripts/card_units.py` 03:43:20、`scripts/pack_card.py` 03:43:31、`scripts/write_process_history.py` 03:43:52
   被改写，随后两表、`commands.json`、`handoff.json`、`process_history.json`、V 输出与四卡 V rc.json
   在 03:44:34–03:44:43 被改写。因此我最初的临时副本曾把 **03:40 世代的表**与 **03:43 世代的脚本**
   混在一起（表现为 3 条 pseudo-drift），我已废弃该副本并改在**稳定的 03:44:43 世代**上重做全部测量
   （稳定性以 03:45:31Z 与 03:46:46Z 两次采样 mtime 完全一致证明）。**本判定只对该世代有效。**
2. **编排层 pre-commit 事故**（`execution_runs/_isolation_incidents/20260920-precommit-stash-production-rollback/INCIDENT.md`）：
   pre-commit 门导出未暂存补丁后执行 `git checkout -- .`，因 3 个并发占用的 `.planning/.../I-04-D/.../scratch/*/stderr.A.txt`
   返回 255，补丁未回放，生产工作树被重置到 HEAD；窗口 **04:35:31–04:5x（本地）= 03:35:31–03:5x（UTC）**。
   我在该窗口内的三次生产测量均为**锚定值**（`model_registry.py = 9ec65295…`、
   `model_extensions.py = 9939480b…`），**未观测到 `production_hashes_unchanged=false`**；
   我首次测量（03:42:53Z）之前的状态我未测、不作归因。
   对本批复核的实质影响：**不存在**——四卡只用 `--code-root <attempt>/iso/checkout_scripts`，
   且我三次核对四卡 iso 副本两文件均 = 锚定值，故生产工作树的回滚不可能影响任何公式结论。
3. `PLAN\reviews` 未被本批写入（307 个可读条目，最新 mtime 2026-09-19T09:05:32Z）；
   `company-wiki` porcelain 2 行（既有用户改动）、`filing-fetch` 空。

### 仍未验证（不得当已证）
r1/r2 的未验证项全部保留，另加：M17 `measurement_pipeline_executions_declared=3` 与
`closing_executions_declared=7` 不可独立证实（已正确标注为 declared）；03:17:53Z 那一代写入的触发者
仍不可归因（`process_history.json` 以 `additional_unnamed_generations: 1` 的 honest_gap 登记）；
更早一次 V 执行曾返回 rc=3 的原因在最终交付件中已不可考；M13–M16/M25–M28 的声明一致性机制未评估等价性；
M01–M04/M09–M12/M21–M24/M29–M31 的 runner 未重读。

—— 独立 reviewer，2026-09-20T03:52Z，零写入模式（写入仅限 %TEMP%\m17m20-review-r3-20260920-044253\）


### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。

**世代边界（重要）**：上方法庭级判定由独立 reviewer 针对**冻结世代
`2026-09-20T03:44:34Z–03:44:43Z`**（四卡最后一次收尾 + V 单元）作出，只对该世代有效。本转录以及
r3 遗留项 P3-A…P3-D 的处置都发生在该世代**之后**，故本卡目录此后存在更新的记录；判定所依据的世代值
已用**只读快照**保存于 `evidence/M17/generation_20260920T034434Z/`（含当时的
`evidence_hashes.json`、`after/final_deliverable_hashes.json`、`after/hash_table_verification.json`、
`handoff.json`、`commands.json`、`process_history.json`、`qualification.json`、`revision_r2.json`、
`source_manifest.json` 及各自 sha256），可据此逐条比对"哪些文件在判定世代之后被改写"。

**流程要求（reviewer 明示并登记为约束）**：宣布本卡完成后**不得再写入 attempt 目录**；任何后续写入都会
使本判定失效、必须重新点审。若确需写入，应先保存世代快照，写入后重跑 `run_closing.py`
（其内含 V 单元）并重新登记世代。

**r3 遗留项处置（只涉及脚本与记录文件；`oracle.md` 未再改动）**：P3-A 已让 `run_closing.py` 在收尾单元
之后**同一命令内**执行 `verifier_units()`（含 `V-verify-hash-tables`），并在 `recovery/closing_run.json`
记录两阶段单元清单与 raw rc；P3-B 已把无追加节分支的演示截断点改到 **base 长度**处（并加 `applicable`
标记）；P3-C/P3-D 以**文档**形式落在 `rc_namespace.json` 与批次交接（**不改 `run_card.py` 一个字节**，
以保持 reviewer 已验证的 runner sha `94619a98…` 不变）；P3-E 的世代覆盖事实登记在批次交接与
`generation_manifest.json`。`disclosure_adaptation` 与 `accuracy` **未动**。
