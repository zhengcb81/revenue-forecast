# Task Plan: 三项目历史承诺逐项独立复审

## Goal
完整清点revenue-forecast、filing-fetch、company-wiki及子目录内planning-with-files历史文档与关联验收证据，对每条独立承诺/修复/通过声明重新判定，解释历史验收与真实运行之间的落差，形成可执行且不可虚报完成的新实施计划。本轮只审查和写审计/计划材料，不实施产品修复。

## Plan Binding
PLAN_ID: 2026-09-19-three-project-history-audit
PWF_PLAN_ROOT: C:/Users/郑曾波/Projects/revenue-forecast
Owner: root。所有代理加入同一计划，只写各自reviews子目录。命令内显式pin仅影响该子进程，不宣称已更改宿主hook环境；不改变共享active_plan指针。

## Next Step
产品实施已推进至 **65/86 卡已建**（计数经 2026-09-20 round 35 补记账归一，以盘上载体为准）。**盘上独立 `accepted_scoped` = 61 张**：全部 `M01–M31`（31 张，qualification 均为 **仅 formula**）+ `I-00-B/C/D`、`I-01-A`、`I-02-A…E`、`I-03-A…D`、`I-04-A…E`、`I-05-A/B`、`I-06-B`、`I-07-A`、`I-08-B`、`I-09-A/B`、`I-11-A`、`I-14-A/B/C`、`I-15-A`（30 张；其中 I-14-A 仅隔离测量、I-15-A 仅证据/诊断、I-11-A 仅设计契约、I-14-C 仅证据与判据且明确不含促销）。**`review_pending` = 3 张**：**I-00-A**（限定只读基线；盘上最新独立结论仍为 `changes_required`）、**I-05-C**（**D-W05 producer entry 已于 2026-09-20 16:45 获 owner 批准 ⇒ GAP-1 解除、可进入真实实现**；仍余 GAP-2「RF `consumer_analysis` owner 未提供 entry」硬阻塞与 GAP-3「事件 schema 待 reviewer」；注意 **批准 ≠ 验收**，`status` 保持 `review_pending`）、**I-08-A**（其 reviewer **明文禁止**把「已接受」写入任何载体 ⇒ 不得走常规载体路径，须单独商定收口方式）。**`blocked` = 1 张**：**I-06-A**（`D-W06` 五问未签；OPEN-2 幂等键缺请求身份为决定性项）。**未建 = 21 张**：`I-10-A`、`I-12-A…E`、`I-13-A…C`、`I-16-A/B`、`I-17-A/B`。全部改动留 `execution_runs/<card>/<attempt>/` 各自 `review.md`；**生产零代码合并**（唯一生产写入是 owner 授权的 `5db4734a`：把 `scripts/model_registry.py` 扩展版 + `scripts/model_extensions.py` 纳管，属版本控制层动作而非产品行为变更；历史事故：I-14-C 曾直接改生产工作树已回退为 HEAD，2026-09-20 pre-commit 门另致生产树被重置到 HEAD 一次、已用补丁 `--exclude=.planning/*` 子集恢复并逐文件复算，见 findings.md 隔离巡检节）。产品资格均限实施声明范围；`disclosure_adaptation` 全卡 `unmapped`、`accuracy` 全卡 `unproven`，无一张外推。**Round 39 总授权（2026-09-20 17:0x，owner 原话「给你所有批准」）**：已按权限归属拆为 **TIER-1 可裁（28 项，已裁）** / **TIER-2 需他方（15 项，owner 仅授权联系与启动，最终裁定仍待该方）** / **TIER-3 知悉（5 项）**，详见 `OWNER_DECISIONS.md` 第十三节。**执行纪律第 7 条**：「总的批准」不得膨胀为「所有的结论」—— 把 TIER-2 记为「owner 已裁」等同伪造签名。本批同时**归档闭合第九节第 16 项**（扩展模型版纳管，已由提交 `5db4734a` 完成）。

**下一步唯一动作**：①**I-05-C 可实现** —— owner 已于 2026-09-20 16:45 批准 `D-W05` producer entry，`produce_for_demand` 可从 mock-only 转真实实现（接 CW `service.py` 现有 producer，不新增重复 parser，调用事件记在实际调用边界）；但 **GAP-2 仍阻塞 `consumer_analysis` 角色**（producer 不存在、真实 LLM 能力未验证）⇒ 须 RF `consumer_analysis` owner 提供入口，**不得造绿色样例补全**；**GAP-3** 待 reviewer 批准事件 schema。②等 owner 签 `D-W06` 六项（**OPEN-2 幂等键是否含请求身份为决定性**）解锁 I-06-A。③I-08-A 收口方式待单独商定（reviewer 明文禁止写入「已接受」）。④派实现者对 6 张卡的陈旧 `reviewer_status` 字段对齐（**只改该字段、不动裁决字节**）。

**Round 41（2026-09-20）新增：TIER-2 三封对外请求函已起草完毕（TIER-2 唯一真正解锁的动作）**。落点 `.planning/2026-09-19-three-project-history-audit/outward_requests/`，**纯新增、未改任何既有载体**：

| 函 | 文件 | 字节 | sha256（前 16） | 覆盖 TIER-2 项 | 收件方 |
|---|---|---|---|---|---|
| **A** | `A_DW06_OPEN-4-5-6.md` | 9120 | `87d4431611d24f95` | **T2-1** OPEN-4 · **T2-2** OPEN-6 · **T2-3** OPEN-5 | wiki 来源审核 owner + 安全 reviewer + RF 消费 owner |
| **B** | `B_signature_trust_domain.md` | 12509 | `84a7988da2a70388` | **T2-8** D7 · **T2-9** D1/D2/D3 · **T2-10** D6 · **T2-11** D5 · **T2-13** I09A-1…6 · **T2-15** | 跨仓双方 + 安全域 + revenue publication owner + invest-core 消费 owner |
| **C** | `C_I-05-C_gap2_gap3.md` | 8724 | `b0ef5fda63ebfdc5` | **T2-14**（部分）· I-05-C GAP-2 / GAP-3 | RF `consumer_analysis` owner + 独立 reviewer |
| 索 | `README.md` | 3134 | `8d0a66516aa3d04c` | 索引 + 共同约束 | — |

**四封函的共同纪律（已逐条写入正文）**：不得代签；不得以「按最佳实践」代替决定；每项须给**选择·理由·反例·兼容影响·恢复规则·被拒绝的替代方案**；不得编造证据（缺样本则维持 `blocked`、不造绿色样例）；**裁决前不得把具体秒数/字节数写成规范值**（函 B 对 `W`/`T`/`L` **刻意留空**）；回执一律落各卡自己的载体，**不在函上签字**。**自证**：西里尔/异体字符扫描 0 命中；四文件 UTF-8 全部可解析；`_provenance.json`（3775 B）JSON 合法。**本动作不产生任何裁定、签名或 `status` 变化**。

**第十四节已登记（R-1/R-2 清除事实 + M31 勘误，T1-23 / T1-25）**：`OWNER_DECISIONS.md` 45616 → **50052 B**（+4436），`prefix_bytes_preserved = True`（后缀追加、前像逐字节保留），新 sha256 `62827d230f4d5a6c…`。核实结论：**R-1 已清除**（三卡 live `OQ-04.title` 已改，旧标题完整保留于 `live_record_corrections.R-1.superseded_title`）；**R-2 已清除**（`write_binding.py` 四副本 M31 常量已更正为七驱动 / `True` / `divergence_note = None`，文件头有 F-02 撤回 banner，旧值保留于 `evidence/M31/binding.json` 的 `errata.superseded_values`）；清除时间 `2026-09-20T03:38:5x` **早于**第四批记账 ⇒ §8-10 / T1-25 的「R-1/R-2 清除前不得关闭」为**事实滞后**，其**前提已达成**；**M31 勘误经实测验明为误读**（`card_M31.md:9` 与 `model_cards.md:2818` 七项含 `net_revenue_per_unit`、`byte-identical = True`）。**只登记、不改冻结证据、不做 `status` 转移**；M31 是否正式关闭仍归其 reviewer。

**I-06-A 候选已按两条 owner 裁定修订为 rev2（仍为 UNRATIFIED）**。落点 `execution_runs/I-06-A/a20260919-01/`：

| 产物 | 字节 | sha256（前 16） | 说明 |
|---|---|---|---|
| `iso/candidate/processing_demand_store_rev2.py` | 21290 | `b3eafcfaaf529bdb` | rev2 候选，**UNRATIFIED** |
| `oracle_rev2_open2_optionA.json` | 4911 | — | **运行前冻结**的独立预期（期望值由裁定文本手推，非调用被测函数生成） |
| `scripts/verify_rev2_open2_optionA.py` | — | — | 独立验证器（纯 scratch，不动生产） |
| `rev2_verification_result.json` | 5660 | — | **28/28 passed，raw rc = 0** |
| `evidence_rev2_mutant_key_dropped.py` | 21726 | `fe6acfd43147e963` | 变异体（键退回 v1 三元组） |
| `rev2_provenance.json` | 4099 | — | 全程 provenance |

**两条裁定的落地**：①**OPEN-2 选项 A** —— 幂等键改为六元 `{key_version, source_sha256, review_policy, role_set, request_identity}`，其中 `request_identity = {as_of_date, target{document_kind,entity}, payload_sha256(其余字段)}`；`key_version` 升 `2.0.0`（v1 行与 v2 行**不得**视为同一需求）。②**OPEN-1 选项 A** —— store 形状改写为 CW `store.py` 的 `_apply_additive_migrations` 风格（`CREATE TABLE IF NOT EXISTS` + 具名索引，可原样抬进 `store.py`），**弃用** v1 自建独立 SQLite 文件形状。

**被测缺陷（c8/c9/c10 实测）**：三个**不同**请求全部返回同一 `demand_id=demand-84179f79057143d4`，且行内 `request_sha256` 保持**第一个**请求的 `d8afcf31…`（第二个请求实际哈希 `4bddf9e6…`）⇒ 静默合并。**rev2 后**：三个不同请求产生**三行**（`rows for this source == 3`），同一请求重提仍复用同一行（`created=False`）。

**变异证明（关键）**：把 `demand_key()` 退回 v1 三元组 ⇒ **28 项中 10 项变红**（`raw rc = 3`），其中 `rows for this source` 实测退回 **1**，**精确复现** v1 缺陷。⇒ 这道门**确实在测这条裁定**，不是「碰巧通过」。

**未做（边界）**：未把候选提升为产品实现（`UNRATIFIED` 保持）；**未关闭 OPEN-4/5/6**（仍待函 A 三方）；**未改任何 `status`**（I-06-A 仍 `blocked`）；未改 v1 候选、未改任何冻结证据/门/产品源码；未声称真实 LLM 能力（`consumer_analysis` 仍 GAP-2 阻塞）。**生产锚点复算**：`scripts/model_registry.py` = `9ec6529550f189a4…` **一致**；HEAD 树 `scripts/` **0 条**；工作树 `git diff HEAD --name-only` **11 条全部在 `.planning/` 内**。

**Round 42（2026-09-20）新增：I-10-B（T1-22）卡内完成 —— 含一项 high 级兼容性发现**。落点 `execution_runs/I-10-B/a20260919-01/`，**纯新增、未改任何既有载体**：

| 产物 | 字节 | 说明 |
|---|---|---|
| `changes.diff` | 6098 | 隔离副本 vs 生产前像的统一 diff，两处修复各一个 hunk |
| `compatibility_impact.md` | 14457 | 卡文第 3 点硬要求：5 个变化 cell + 双路径判定 + 126 个未变 driver + E-1…E-7 清单 |
| `decision.md` | 8384 | DEC-I10B-1…5 |
| `binding.json` / `commands.json` / `handoff.json` | 9446 / 5324 / 5948 | 锚点、隔离、缺陷、兼容性声明、10 条命令（0 条触产品树） |
| `compatibility_cells.json` | 6070 | 165 cell 全量 BEFORE/AFTER 差分 |
| `frozen_impact_scan.json` | 25287 | 1579 个 JSON 分类（CASE_TARGET 17 / 负值 1 / REFERENCE_ONLY 47） |
| `frozen_regression_rerun.json` | 4580 | 四卡三相位实跑对照 |
| `scripts/`（4 个验证器） | — | `verify_i10b.py` / `compute_compat.py` / `scan_frozen_impact.py` / `frozen_regression_rerun.py` |

**两处修复（隔离副本内，`iso/rf/scripts/model_registry.py` 30116 B / `62f864b9ab3f144e`）**：①**省缺即抛** —— `drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))` 改为「无显式 default 时抛 `ModelRegistryError`」；**刻意不补显式 0**（仍无法区分「没找到」）。②**语义角色符号** —— 新增 `_REVERSAL_CAPABLE_DIMENSIONS ∩ _REVERSAL_CAPABLE_DRIVERS` + `_is_reversal_capable()`；`_SIGNED_DRIVERS` 降为**仅供导入的废弃别名**；符号须**同时**满足 dimension 闸门与角色位，故数量/比率型 driver 不可能被误改。**验证**：before 6/6（缺陷可见）→ after **7/7 raw rc = 0**，本轮重跑复现一致；含 R-B1-N1（省缺必抛）、R-B1-N3（**显式 0.0 仍被接受** ⇒ 区分了省略与显式）、R-B2-N1（`franchise_system_sales` 负值**必须被接受**）、R-B2-N2（无名 driver **不得**凭名字获得符号）。

**边界变更全清单**：165 个 `(model, driver)` 单元中**恰好 5 个**变化，**全部为下界放宽、上界不变**：`cohort_subscription.usage_revenue`、`retail_franchise.franchise_system_sales`、`retail_franchise.supply_revenue`、`subscription.usage_revenue`、`subscription_arr_bridge.usage_revenue`，均 `[0.0, inf)` ⇒ `[-inf, inf)`；**126 个 driver 未变**。**判据修正（第 6 次同源教训）**：首版把「最终下界是否为 `-inf`」当变更集是**错的** —— 修复前**就已有 37 个 cell** 在 `[-inf, inf)`（`other_revenue` 14 个、`bank_revenue.asset_yield`/`funding_cost`、`aum_fee_bridge.market_change` 等），该判据**同时**夸大波及面并**掩盖**真实变更集；改为对 `(lo, hi)` **对**做 BEFORE/AFTER **差分**。⇒ **判据必须匹配被判定对象的形态：值域变更用差分、不用终态**。

**⚠️ high 级发现 F-I10B-1（兼容性，必须随卡移交给编排层）**：**省缺即抛使 M05 / M14 / M20 / M24 四张卡的 `defaults` 相位全部从 `ok` 翻转为 `ModelRegistryError`**（实跑对照）：M05 `[600.0]`、M14 `[50.0]`、M20 `[220.0]`、M24 `[210.0]` **皆抛**。**根因**：四卡的 `defaults` 输入块**都省略了**至少一个「optional 且无显式默认」的 driver（M05/M20/M24 为 `usage_revenue`；M14 为 `franchise_system_sales`/`recognized_fee_rate`/`supply_revenue` 三者），其冻结期望成立**恰恰依赖缺陷①的静默补 0** —— 最直白的书面自证是 `M24 evidence/M24/oracle.json > hand_notes.defaults` 明写「**usage_revenue omitted -> 0**; 200 - 15 + 15 + 10 + 0 = 210」。**四卡的 `positive` 与 `continuity_positive` 相位全部未变**。**处置**：非缺陷、是**修复的预期后果**（缺陷①的定义就是「把『不存在』与『没找到』编码成同一输入」）；依 **T1-12 ① 形态**（追加新节 + 行级「第 X 行已过时，以本节为准」标注）**追加式勘误、不回改**；**卡文第 5 点禁止本卡扩大 allowlist 改 31 张 M 卡的正文/证据** ⇒ 本卡**只产出待登记清单 E-1…E-7**、**未执行任何编辑**。

**值域放宽路径（缺陷②）零冻结判定受影响**：全 M01–M31 证据树 **1579** 个 JSON 扫描；`CASE_TARGET` 17 个其 `value` 全为**正数**或**类型/长度类负例**（`__bool__`/`nan`/`inf`/`-inf`/空数组/未知 driver），**无一**依赖「负的实数值应被 `[0, inf)` 拒绝」；唯一负值命中件 `M14/recovery/probes/signed_driver_probe.json` **自述** `"purpose": "post-hoc design probe (NOT a frozen case, NOT the oracle)"`；M14 另两处把旧行为记为契约边界（`cases.json > extra_observations[OBS-SUPPLY-BOUND]`、`oq_rulings.json > open_questions_mirroring_handoff[OQ-03]`），**均自带「不门禁 / 属未决 D/E 决策」声明** ⇒ 不是 pass condition。**缺陷②的名字硬编码任意性有实测证据**：`recognized_performance_fees` / `reserve_revisions` / `backlog_remeasurements` **均不在** `_SIGNED_DRIVERS`，却**早已**经 `driver_bounds` 元数据到达 `(-inf, inf)` —— 同一语义角色、两种名字待遇。

**基线实测与卡文数字吻合**：31 个模型 / **31** 个 `optional-without-default` 槽位 / **24** 个受影响模型，与 `card_I-10-B.md:14` 所述完全一致。

**未做（边界）**：**未落地生产**（`scripts/model_registry.py` 仍为前像 **26446 B / `9ec6529550f189a4…`**，与绑定值一致、无漂移）；**未改任何冻结件**（0 个）；**未做任何 `status` 转移**（I-10-B 保持 `planned`，**不自我升格**）；**未代签** —— M14 `OQ-03` 原文自述**属 D/E 决策**、本卡独立验收**属 TIER-2 须他方出具**，均未记为已裁。**新增忽略**：`execution_runs/.gitignore` 增 `*/a*/_scratch_import/`（导入暂存，可由 `compute_compat.py` 确定性重建）。**自证**：8 个 JSON 全部 `json.load` OK；西里尔/异体字符扫描 **0 命中**。

**Round 43（2026-09-20）新增：T1-6 卡内完成 —— 「不一致」的真实形态查清 + 补回缺失的守卫用例（含一项 medium 级漂移发现 D-1…D-8）**。落点 `execution_runs/T1-6/a20260920-01/`，**纯新增、未改任何既有载体**：

| 产物 | 字节 | 说明 |
|---|---|---|
| `iso/cases_pre.json` | 6185 | 前像本地副本（`263b78b3…`，与冻结件逐字节相同） |
| `iso/cases_t16.json` | 7440 | **候选后像**（`29933fe2…`，**未写入冻结件**） |
| `changes.diff` | 2276 | 两个 hunk，**零删除行** |
| `decision.md` | — | 权限、不一致真实形态、选项比较、可达性实测、边界 |
| `commands.json` | 10382 | 6 步可复现命令日志（含实际观测值与哈希） |
| `binding.json` / `handoff.json` | 9990 / 7508 | 锚点、双相位验证、漂移登记、边界 |
| `t16_landing_report.json` / `t16_verification.json` | 1309 / 6701 | 落地自检 4 判据 + 冻结 runner 验证 |
| `run_result_pre.json` / `run_result_post.json` | 36297 / 40346 | 冻结 runner 双相位原始输出 |
| `scripts/land_t16.py` / `verify_t16.py` | 7652 / 7378 | 落地器 / 验证器 |

**裁定与范围**（`OWNER_DECISIONS.md` §13 **T1-6**，TIER-1）：选 (c) —— 「在 `cases.json` 重新加回一个**输入不同**的跨年用例（可达值 `{"opening_arr":[200,250],"closing_arr":[251,251]}` ⇒ `stock-flow balance failed: FY2027`），**无需改正文**」。三点范围读出：①仅 `cases.json`；②必须**输入不同**；③**编辑必须是加法的**。

**⚠️ 「不一致」的真实形态查清（实测，非推断）**：T1-6 所述「卡文与 `cases.json` 不一致」**不是数字不同** —— 实测 **`card_patch_equals_current = True`**，卡文 `negative_patch` 与盘上 `CONT-BREAK` 的输入**逐字节相同**。真正的缺口是**另一个守卫的用例缺失**：`review.md:128-129` 的 reviewer 最小修法有**两半** —— ①保留 `CONT-BREAK` 原值并补上 `expect_message_contains = "stock-flow balance failed: FY2027"`；②新增 `CONT-BREAK-CROSSYEAR`（值 `[200,250]/[250,251]`）。**实际只落地了「一半的一半」**：最终冻结件只保留单一 `CONT-BREAK`（**卡文原值 + CROSSYEAR 消息 `continuity failed: FY2028`**），reviewer 处方中的 own-balance 用例**缺失**、item-1 的消息要求**未施加**。**盘上的书面佐证且与实体不符**：`revision_r2.json` 的 `P2-3` 称「implemented as `CONT-BREAK-CROSSYEAR`」（**无此 id**）、`card_specific` 称「`CONT-BREAK` 的拒绝消息被冻为 `'stock-flow balance failed: FY2027'`」（**实际是 `continuity failed: FY2028`**）。⇒ 现存用例只行使**跨年锚定**守卫（FY2027 关 ≠ FY2028 开），**FY2027 自身平衡**守卫**不可达**。

**可达性实测（落地前先测，`t16_reachability_probe.py`，四判据全 True）**：对照组 `continuity_positive` → `ok [215.0, 250.0]`；现行 `CONT-BREAK`（`[200,251]/[250,251]`）→ `opening_arr continuity failed: FY2028`（**跨年守卫**）；**T1-6 裁定值（`[200,250]/[251,251]`）→ `opening_arr stock-flow balance failed: FY2027`**（**FY2027 自身平衡守卫**）；卡文 `negative_patch` **逐字节等于**现行值。两类负例**抛同一异常类但消息不同** —— 这正是「类型断言不足、必须冻消息」的理由。**⚠️ 消息前缀差异如实登记**：T1-6 写的期望串是 `stock-flow balance failed: FY2027`，**实测完整消息**为 `opening_arr stock-flow balance failed: FY2027`（带 `opening_arr ` 前缀）；子串判定成立，故冻结的是**子串**，**不改裁定文本**。

**落地（纯追加，`iso/cases_t16.json`）**：新增 `CONT-BREAK-OWNBALANCE`（`kind=set_driver_multi`、`expected=ModelRegistryError`、`base_input=continuity_positive`、值 `{"opening_arr":[200,250],"closing_arr":[251,251]}`、`expect_message_contains="stock-flow balance failed: FY2027"`）+ 其 id 追加进 `required_message_ids`（2 → 3 项）。`delta_bytes = +1255`、用例 11 → 12、**零删除**。**四条完整性判据全绿**：`pre_existing_cases_unmodified` / `renderer_is_faithful` / `existing_cases_rendered_identically` / `changed_fields_are_exactly_intended`（**变化顶层字段恰为 `cases` 与 `required_message_ids`**）。**为何不用前后缀字节判据**：本次是「就地字段编辑 **+** 追加」的复合形态，纯前缀/纯后缀都不覆盖其形状 ⇒ 改为**直接证明**结构主张：(i) 渲染器对前像逐字节往返成立；(ii) 追加后前 11 个用例渲染逐字节相同；(iii) 恰增 1 个 id、**零删除**；(iv) 无其他顶层键变化。**同 I-10-B 教训：判据必须匹配编辑形态。**

**冻结 runner 双相位验证 OVERALL = PASS（7/7）**：`pre rc = 0` / `post rc = 0`；`negative summary {'total': 12, 'passed': 12, 'failed': []}`；新用例 `PASS_rejected ... message_requirement_met= True - opening_arr stock-flow balance failed: FY2027`；现行 `CONT-BREAK` 两相位判定**未变**（`opening_arr continuity failed: FY2028`）；`required_message_ids` 三项 `ok= True`；`shared_cases_unchanged = True`；`positives_unchanged = True`。**runner 为冻结件本身**（`M24/a20260919-01/scripts/run_card.py`），**非重实现**，仅重定向 `--cases`/`--out`。**闸门说明**：`required_message_ids` 是**硬门** —— runner 在执行**任何**负例前先断言每个 id 存在于 `cases` 且 `expect_message_contains` 非空，缺失即 **rc=3**；故新用例的 id **必须**入列（否则「存在但无门」的用例可被删除而运行仍绿）。

**⚠️ medium 级发现 F-T16-5：M24 attempt 内已存在 8 项登记漂移（D-1…D-8），非本轮造成**：D-1 `handoff.json` 的 `cases.json` 记 `df12c66a…`（盘上 `263b78b3…`）；D-2 `source_manifest.json` 同上；D-3 `input.json` 记 `ccfc2f8e…`（盘上 `7f60e7d8…`）；D-4 `oracle.json` 记 `bab13806…`（盘上 `3da88501…`）；D-5 `after/rerun_sha256.json` 全套哈希与盘上**均**不一致；D-6 `recovery/selfcheck/selfcheck_result.json` 记 `263b78b3…` **且** `frozen_hashes_unchanged=true` ⇒ 与同目录世代在**跨文件层面不自洽**；D-7 `revision_r2.json` 的声称与盘上不符（**正是 T1-6「不一致」的书面表现之一**）；D-8 `handoff.json` 的 `qualifications.formula = review_pending` 而同文件 `status = accepted_scoped`。**解释**（非结论）：**至少两个世代并存** —— 早期世代（`binding.json` / `after/rerun_sha256.json`）记 `df12c66a…`/`ccfc2f8e…`/`bab13806…`；后期世代（`recovery/selfcheck` + 盘上实体）记 `263b78b3…`/`7f60e7d8…`/`3da88501…`；`handoff.json` 与 `source_manifest.json` **未随世代推进同步**。**处置：仅登记、不回改**（**不属 T1-6 授权范围**）。

**未做（边界）**：**未写入冻结件**（`M24 .../evidence/M24/cases.json` 仍为 **6185 B / `263b78b3…`**，本 attempt **从未以写模式打开**该文件）；**未落地生产**（`scripts/model_registry.py` = **26446 B / `9ec6529550f189a4…`**，与绑定值一致、无漂移）；**未做任何 `status` 转移**（T1-6 保持 `planned`，**不自我升格**）；**未代签**（独立验收属 TIER-2，未记为已裁）；**未处置 D-1…D-8**；**未改卡文正文**（T1-6 明示 `无需改正文`，且卡文第 5 点禁止本卡扩大 allowlist 去改 31 张 M 卡的正文或证据）。**自证**：`git diff HEAD --name-only` **全部在 `.planning/` 内、0 条产品文件**；9 个 JSON 全部 `json.load` OK 且与 `handoff.json` 登记哈希**零失配**；西里尔/异体字符与弯引号扫描 **0 命中**。**提交** `3a7f9c2c`（12 files / 2185 insertions / 0 deletions）；按 **T1-27** 核对提交后 hook 的 `[INFO] Restored changes from …` 行 ⇒ 工作树完整、冻结件与生产锚点哈希均未变。

**Round 44（2026-09-20）新增：T1-14 卡内完成 —— I-11-A OPEN-1 登记核查，**结论为「已核查的 no-op」**。落点 `execution_runs/T1-14/a20260920-01/`，**纯新增、未改任何既有载体**：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-14**，TIER-1）：**均采纳** —— **OPEN-1** 允许 `pdftotext.exe` 作**交叉核对路径**、**永不作为任何被引用数值的唯一来源**；须把**绝对路径 + sha256 `252d2b34…`** 写进 `binding.json`、**禁止为取文升级 Git**；**OPEN-8** 接受以 `P1_vs_prior_offset.json` 择优规则为准、**不回改 oracle 正文**。拆为五项可分离义务：**O-3（把路径与哈希写进 `binding.json`）是唯一「待办之事」**；O-1/O-2/O-5 是长期规则，O-4 是长期禁令（作为**条件**核查，而非作为任务执行）。

**核心发现：O-3 盘上已成立。** `I-11-A/a20260919-01/binding.json > external_tools.pdftotext` 已载 `path = C:/Program Files/Git/mingw64/bin/pdftotext.exe`、`sha256 = 252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0`、`version = pdftotext version 4.00 (Xpdf, …)`。**但「字段存在」与「字段为真」是两个不同的事实** —— 登记了一个哈希，若那个哈希**不是实际会运行的那个工具**的哈希，则登记毫无价值。故**做四项独立验证**而非只读一眼。

**四项命题全成立（`scripts/verify_t14.py`，任一失败即 FAIL）**：**P-1** 登记的路径是**绝对**路径（`C:/…`，驱动器号）且 sha256 为 **64 位十六进制** —— 相对路径会静默相对于未来某次运行的 cwd 解析，正是 `I-00-B` 要防的那类缺陷，故绝对性是**实质**要求；**P-2** 登记哈希**精确等于**该路径下二进制的实际哈希（`disk_sha256` 与登记值逐字符相同，**1537966 B**）—— 此命题是 O-3 的意义所在；**P-3** `pdftotext -v` 报 `pdftotext version 4.00`，与登记所载版本一致 —— 若无此检查，**可在同一路径换成另一个工具并同步更新登记**，哈希相符而登记的版本串变成谎言；**P-4** Git 安装树 mtime = **2025-11-08 10:56:42**，`binding.json` mtime = **2026-09-20 15:48:16**，**相差 ≈ 316 天** ⇒ 本卡未导致升级（当前 Git `2.55.0.windows.3`）。

**⚠️ P-4 的证据力限度已如实登记（未隐去）**：**mtime 比较是证据、不是证明** —— 保留 mtime 的就地补丁**不会**被本方法捕获。命题记为「依现有证据成立」，限度写入 JSON。**声称多于方法所能支持，正是本项目纪律所要防的越权。**

**为何未做任何编辑（三条独立理由）**：①**字段已存在且已验证为真** —— 重写同值只产生无信息量的 diff，无谓地使冻结件哈希失效；②`binding.json` 是 `handoff_status = review_pending` 的 attempt 的**冻结件**，写入它会**事后改变 reviewer 被要求审的东西**；③owner 在此的职权是**裁定处置**，不是**撰写一个冗余编辑** —— 执行 no-op 编辑会看起来像进展而实际什么都没改变。**原则：授权是许可，不是义务。** 义务**已解除**。

**产物**：`decision.md`（8136 B / `9e9ff11c…`）、`handoff.json`、`t14_register_verification.json`（2148 B / `4653ca93…`）、`scripts/verify_t14.py`（7436 B / `245fd298…`）。**边界**：`binding.json` **写入 0 次**（记 `register_under_test` = `9d9c89a7…` / 6322 B，`written_by_this_attempt = false`）；未做任何 `status` 转移（T1-14 保持 `planned`）；未代签；未升级 Git；`git diff HEAD --name-only` **全部在 `.planning/` 内、0 条产品文件**；2 个 JSON 可解析且与 `handoff.json` 登记哈希**零失配**。**提交** `b9639b8c`。

**Round 45（2026-09-20）新增：T1-27 卡内完成 —— 追加块存储脆弱性缓解审计，**结论为「已核查的长期纪律」**。落点 `execution_runs/T1-27/a20260920-01/`，**纯新增、未改任何既有载体**：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-27**，TIER-1）：**采纳缓解建议** —— **授权编排层更频繁地提交 `.planning`**（关键 attempt 的追加块尽早入库），并在**每次提交后强制核对** hook 的 `[INFO] Restored changes from <patch>` 行。**其所应对的风险**（同文件第 108 行，第九节第 18 项）：追加的 reviewer 裁决块**只存在于工作树** —— 一次 `git checkout -- .` 会把它退回已提交的纯基座并**丢掉追加块**；**若再次提交后 hook 失败，未提交的 attempt 追加成果同样处于风险中**。

**⚠️ 该失效模式不是假设，已发生一次**：`execution_runs/_isolation_incidents/20260920-precommit-stash-production-rollback/INCIDENT.md`（8505 B / `c326e38e…`）记载：pre-commit 门把未暂存改动导出为补丁（557,924 B），随后 `git checkout -- .` 因 3 个被并发占用的 scratch 文件 `unable to unlink … Invalid argument` **返回 255**，补丁**未被回放** ⇒ 生产工作树被重置到 HEAD（`scripts/model_registry.py` 由锚定 `9ec65295…`/26446 B 变为 HEAD 版 `1f2639e1…`/19703 B，四模型与 `driver_bounds` 机制整体消失）。⇒ **hook 的契约是 stash → `git checkout -- .` → replay；若 replay 失败，工作树停在重置态且补丁未被回放。**

**三半缓解全查（owner 的句子只点了两件；incident 记录点了第三件、结构性的一件 —— 只查被点名的两件会把触发器留在原地）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **H-1** | 关键 attempt 的追加块**尽早**入库 | **holds** | 触及本计划的提交 **41** 次；本轮 **2 张卡 → 2 次提交**（`3a7f9c2c` T1-6、`b9639b8c` T1-14），**不是攒到会话末批量提交** |
| **H-2** | 每次提交后 hook 的 `[INFO] Restored changes from <patch>` 行**已被核对** | **holds** | 生产锚点 `9ec65295…` **完好**；本轮两个 stash 补丁在盘上；两次提交均打印 `Stashing …` **与** `Restored changes from …` |
| **H-3** | 事故**根因**（内嵌 `.git` 扰乱父仓库）已被**结构性移除** | **holds** | 3 个内嵌仓库**全部被覆盖、0 个未覆盖**；`git status` **不报 `bad object`**；**内嵌仓库仍在盘上（一个文件都没删）** |

**H-3 覆盖明细（每条规则精确映射到实际含 `.git` 的目录）**：`I-06-A/.../iso/ff/.git` ← `*/a*/iso/`；`I-14-C/.../r5/diff-apply-check/tree/.git` ← `*/a*/r5/diff-apply-check/`；`I-14-C/.../r5/diff-repo/.git` ← `*/a*/r5/diff-repo/`。**为何 H-3 最关键**：**H-1/H-2 是程序性的**（限制爆炸半径，触发器仍上膛）；**H-3 是结构性的**（移除触发器）—— **一个需要频繁触发的程序，严格劣于一个已被消除的病因**；owner 的两半缓解若单独施行，恰恰就是前者。

**⚠️ H-2 的证据力限度如实登记（未隐去）**：**事后审计无法重新观察过去的 hook 行**。能诚实断言的是：锚点**现在**完好、本轮的 stash 补丁在盘上。逐次核对是一项**纪律**，由这两个补丁 + 完好锚点佐证，而非某段脚本可回放。限度写入 JSON。

**红/绿判据**：`Stashing` **+** `Restored` = 正常；**只见 `Stashing` 不见 `Restored`**，或出现 **`Rolling back fixes`** = **红色告警**。红色告警处置：抽查生产锚点 → 用该次补丁的 `--exclude=.planning/*` 子集回放 → 复算 → **记录时点**（窗口重要，因为窗口内取的哈希是**误报、不是发现**）。

**为何未做任何编辑**：T1-27 的两项指示动作**均已生效** —— 其一「授权更频繁提交」是**授权**、不是待排期任务（由按卡提交行使）；其二「每次提交后核对 hook 行」是**长期纪律**（本轮两次提交均已执行）；第三半（H-3）此前已作为 `.gitignore` 变更实现，本卡**验证**它而非重做它。**先验证；只有验证失败才编辑。**

**产物**：`decision.md`（9547 B / `67a9e1e2…`）、`handoff.json`、`t27_hygiene_audit.json`（3669 B / `ce9c45ae…`）、`scripts/audit_t27.py`（8779 B / `d0a98d70…`）。**边界**：**0 外部写入**；`.gitignore` **未重编**（既有规则仅验证）；**内嵌仓库删除 0 个**；生产锚点完好；`git diff HEAD --name-only` **全部在 `.planning/` 内、0 条产品文件**；2 个 JSON 可解析且与 `handoff.json` 登记哈希**零失配**。

**⚠️ 值得泛化的模式（本轮第三次命中同源教训）**：**本轮三张卡中有两张（T1-14、T1-27）以「已核查的 no-op」收口** —— 要求本就成立。**收到授权时「必须做点什么」的冲动，正是这两张卡存在所要抵制的失效模式**；执行 no-op 编辑会**看起来像进展而实际什么都没改变**，甚至无谓地使冻结件哈希失效。**授权是许可，不是义务。**

**Worktree 状态（2026-09-20 round 36 已修复，读盘前必看）**：本工作树曾发生**分支误切事故** —— 一次后台 `git checkout` 实际执行了 `checkout main`（`git reflog`：`15:05:08 checkout: moving from fcap to main`），使 fcap 独有的 **1758 个 tracked 文件**在工作树中消失（`git status` 曾报 1699 条 `' D'`），另有 **62 个文件**残留 `main` 内容。已用 blob 直读法（`git ls-tree -r -z` + `git cat-file --batch`，绕过 index）三趟恢复完毕，终态 **`' D'` = 0、`git diff HEAD` 仅剩 5 条**（3 条本轮记账 + 2 条已登记的内嵌 `.git` scratch 目录）。**两条读取纪律**：①`git status --porcelain` 的 `' M'` **不是**内容差异的证据（本次 146 条 `' M'` 中 79 条即 54% 为 index 陈旧伪差异），判据必须用 `git diff HEAD --name-only`；②本仓库 `core.autocrlf = true`，**不得用「on-disk 字节 == blob」作恢复判据**，须用 `git diff <ref> -- <path>` 是否为空（本次裸字节比对曾误报 62 例假失败）。详见 findings.md Round 36 节。

## Current Phase
Phase 1–6 complete。**Phase 7 实施推进 started**，已建 65/86 卡。**当前口径（2026-09-20 round 35 归一，取代此前全部计数）：61 `accepted_scoped` / 3 `review_pending` / 1 `blocked` / 21 未建。** **旧口径一律作废**：round 34 的「57/86」、本文件原「19 张盘上可核 + 8 张条件性接受 + 3 张待补裁决」与更早的「28/86」均为**按会话内回传**记账，而**载体落定（`d4a42f5a` 落 19 张及后续批次）与 M08 三步转正发生在记账之后** ⇒ 盘上状态跑在账本前面。**本次归一的取证方式**：逐卡读 `execution_runs/<card>/a20260919-01/handoff.json` 的**顶层** `status`（位于文件末尾，须取最后一个匹配键或直接 JSON 解析，**不得用首个匹配** —— 该字段在 JSON 内部子对象中大量重用，首个匹配会读到子状态）并交叉核对 `evidence/<CARD>/qualification.json`。

**Round 36（2026-09-20）新增：工作树分支误切事故已确诊并完全恢复**。`git reflog` 证实 `15:05:08 checkout: moving from fcap to main` —— 一次后台 `git checkout` 实际切到了 `main`，而 `main` 比 `fcap` 少 19500 个文件。事故被误判一整个 round 的原因：`task_plan.md` 在 fcap 与 main 上**内容相同**，故「被重置为 fcap 版」与「工作树被切成 main」在该文件上表现完全重合。**纪律（新增，最重要的一条）**：判定「文件为何变了」**不得只用「它变成了什么」**，唯一可靠判据是 `git reflog` 的 `checkout: moving from … to …` 行。**恢复终态（已实测）**：`' D'` 1699 → **0**；`git diff HEAD` 仅 **5** 条（3 条本轮记账 + 2 条已登记内嵌 `.git` scratch 目录）；三趟恢复全程绕开 index，**未修 index、未删除任何文件、未写裁决字节、未改载体字段、未动生产仓库**。**记账文件哈希三趟前后不变**：`progress.md` 112641 B / `6958954d…`、`task_plan.md`（本文件，round 36 后）见 `## Next Step` 末段、`findings.md` round 36 后 39426 B / `daf8a26d…`。

**Round 36 追加的读取纪律（与上文 round 35 的两条并列）**：③`git status --porcelain` 的 `' M'` **不得**当作内容差异（本次 146 条中 79 条即 54% 为伪差异），须用 `git diff HEAD --name-only`；④本仓库 `core.autocrlf = true` + `.gitattributes` 声明 `eol=lf`，**on-disk 字节本就不等于 blob**，恢复判据必须是 `git diff <ref> -- <path>` 是否为空，裸字节比对会误报（本次误报 62 例）。

## Phases
### Phase 1: 冻结范围和建立历史证据清单
- [x] 阅读planning-with-files技能并创建独立命名计划
- [x] 递归清点三项目及归档/子目录，保存路径、hash、大小、重复版本与排除理由
- [x] 冻结当前三repo HEAD/dirty状态、生产policy与上轮真实失败证据
- [x] 为每条历史承诺建立原文位置和对应审查者
- **Status:** complete

### Phase 2: 三项目独立逐项复审
- [x] revenue-forecast：历史方法、契约、验证/发布/安装声明及通过项
- [x] filing-fetch：身份/复用/下载/错误/worker/跨根声明及通过项
- [x] company-wiki：原件/扫描/注册/迁移/审查/策略/激活/运行声明及通过项
- [x] 每条结论附当前证据、历史验收环境、适用范围、状态和剩余缺口
- **Status:** complete

### Phase 3: 跨项目独立复核与针对性复现
- [x] 对三个审查者结论交叉复审，包括判定通过项
- [x] 比较历史commit/config/安装副本/fixture与实际生产入口
- [x] 必要时只读诊断或隔离目录运行现有检查，保留完整原始日志
- [x] 区分回归、未部署、环境阻断、证据不足、设计未完成和越界通过
- **Status:** complete

### Phase 4: 覆盖率审计与根因归纳
- [x] 确保每份文档、每个独立条目均有判定或明确未证实原因
- [x] 重复文档保留映射；旧版不直接沿用新版的通过状态
- [x] 解释测试为什么未能拦住真实失败，构建可定位的因果链
- **Status:** complete

### Phase 5: 新实施计划与交付复核
- [x] 写实施顺序、依赖、边界、回滚、验收场景、证据格式和停止条件
- [x] 区分本轮已完成审计与未来尚未执行的修复
- [x] 独立审核新计划和覆盖表，校验链接/证据hash
- [x] 更新task_plan/findings/progress并交付
- **Status:** complete

### Phase 6: 将总纲细化为低歧义执行包
- [x] 复读总纲，识别实现锚点、案例、设计决策和验收步骤缺口
- [x] 拆分I-00至I-17执行卡与31模型逐项卡，保留原义务映射
- [x] 固定真实场景案例、独立验收、命令绑定、失败恢复和上下文接续规则
- [x] 独立干读代表卡、修正歧义，验证依赖/引用/覆盖并重新封存
- **Status:** complete

### Phase 7: 实施推进（2026-09-19 起，产品实施）
- [x] I-00-A 冻结基线（三仓HEAD/447G注意点等，accept）a20260919-01
- [x] I-00-B 绑定锚点+3/3样本精确hash一致 accept
- [x] I-00-C 验收器证明范围（隔离副本场景门，13/13校验）accept_scoped
- [x] I-00-D 活动指南（生产 CLAUDE.md/README.md 两处边界文本，差异保留 changes.diff）accept
- [x] I-01-A D-W01 共用effective配置判定（五组正反例+N1逐根辅 fail-closed）accept_scoped
- [x] I-02-A D-W02 ScanReport回执契约+writer四道门（6用例，N3a/b/c独立）accept_scoped
- [x] I-02-A/B/C/D/E（隔离，全 accepted_scoped）
- [x] I-03-A/B/C/D（契约+选择+绑定+事务，全 accepted_scoped）
- [x] I-04-A deadline/预算契约设计卡（两轮独立复审后 accepted_scoped：r1 changes_required 1P1/2P2/5P3 全处置，r2 重签；v2 决策=返回后重算剩余、TimeoutExpired 终态、pid 探测入表、C=max(30,2×resume_wait+graceful)、ε 临时签署+预承诺重测、B 仅请求段）
- [x] I-04-B 实施卡（隔离副本：退避改"返回后重算剩余"、请求预算去 `max(10,…)` 下限、清理独立 C、探测 `min(20,相位预算)`、信封分账字段；修前 RED 5 failed→修后 10 passed，T-FILING 126 passed；两轮复审：r1 changes_required 1P1/4P2/5low 全处置 → r2 **accepted_scoped**，条件 C1/C2 均已处置）
- [x] I-04-C 设计卡（跨进程 lease/所有权/恢复协议；三轮复审：r1 changes_required（ADR-10"最后退出者非 owner 且无义务"分支会留永久 paused、认领周期缺 owner 证据校验、计数/报告不符 9/16）→ r2 修 → r3 **accepted_scoped**；随签 **C1**（§13.5 与 review §1 P3-4 的 F-LK2 过时值 `[12,19,7,26,43]`）**已关闭**（真值 `[16,35,10,56,18] ⇒ lost [184,165,190,144,182]`，`verify_flk2.py` 13/13，父代理复核 hash 与只追加证明），**C2**=OPEN-3（60 s 上限命名/边界 + `worker-pause` 是否留在锁内）登记为 **owner 裁定项**，明写不阻塞签收）
- [x] I-07-A（accepted_scoped；更正：`config.legal_fifth_root` planned 计数、census 真值 3440 组、`future_lake` 实为 1 行 `README.md`）
- [x] I-14-A（accepted_scoped，仅隔离测量修复；D1 未签 ⇒ 不提升进 `RF/tools/`；bundle 未测量恒 exit 2 属契约变更）
- [x] M01–M04（**仅 formula 资格**，accepted_scoped）
- [x] M05–M07（**仅 formula 资格**，accepted_scoped）
- [x] **M08 = accepted_scoped（仅 formula）** —— owner 三步已全部完成并经独立复核：①裁定读法 C 权威；②owner 作为执行人更正 4 个文件各 1 处（`100+40−5−10−15−60=50` → **`100+40−5+−10+−15+−60=50`**，各 +2 B；`100+40−20=120` 另一模型**未触碰**），前像逐字节保全于 `execution_runs/M08/a20260919-01/recovery/owner_ruling_20260920_index_correction/`（4 份 pre-image + `provenance.json` + 含 owner 原话的 `PROVENANCE.md`），修正后两个 JSON `json.load` OK，**期望 `[50]` 不变**，提交 `b07d9b95`；③reviewer（`4acc1ab4`）独立复算全通过——字节级重建等式 `now_prefix + pre_region + now_suffix == pre` 四份全 True、同 `code_root 9ec65295…` 复跑 **rc=0**、`[50.0]` 成立、负例 11/11、`tolerances_ok True`、观测 `OBS-SIGN-B=85.0 / OBS-SIGN-NEG=55.0 / OBS-REMEASURE-USED=65.0` 与 r1/r2/r3 完全一致、冻结件逐字节未变、**P1=0**。随签 **F-M08-R1（P2）**：`execution_v2/validation.json` 4 条 index hash 陈旧（因索引刚被更正）⇒ 已派实现者重跑 `validate_execution_pack.py` 刷新并保留旧快照为 provenance，**不影响 formula 资格**
- [x] **M09–M31（全部 23 张，仅 formula 资格，accepted_scoped）** —— 其中 M09–M12 经载体落定执行器处理，因其 reviewer 采**零写入模式**（`review.md` 无卡内裁决区），报告已按字节固化为 `execution_runs/<CARD>/a20260919-01/evidence/<CARD>/reviewer_report_m09m12.md`（注意：`evidence/` 在 attempt 内，不是计划根那个）（40679 B / `5a44fd4e…`，父代理复算 4/4 hash 一致）；M13–M16、M17–M20、M21–M24、M25–M28、M29–M31 均经转录落定 + 批次级 `batch_handoff.md` 封盘
- [x] **I-05-A = accepted_scoped**（转录 + 载体落定 + 封盘完成）：报告按字节固化（`evidence/I-05-A/reviewer_report_r4.md` 15827 B / `d9567713…`）；裁决块转录（`review.md` 8843→13061 B，块在 byte 9213..13030 = 行 104–116，**字节级精确前缀**）；**4 项 P3 以追加更正落地**（oracle **新增附录 D**：前像字节数 14924→**23204 B**；正文与附录 A/B/C 一字未改）；封盘 `sealed_at_utc 2026-09-20T07:32:23Z`、清单 966 行、42 个 JSON 全部可解析。**provenance gap 已如实登记**：`23101 B/d64c8ce2…` 为**来源未确定/不可复现的引用值**（`%TEMP%\planrev4` 下不存在任何 23101 B 文件），按八要素内容签名 + 盘上字节落定处置，不追另一版本
- [x] **I-14-C = accepted_scoped（范围＝证据与判据成立；不含产品化授权）** —— r5 独立复核：T3 标本 rc=3 **0 泄漏 + 27 保真**、T4 0/0、以 **1 字符注入**证明保真判据逐条目生效、`r5-changes.diff` 在无本地 git 配置覆盖下 `--check`/`-p1` 均 rc=0 且字节复原 T4、**82 passed 三次**、抖动 48 行重算翻转成立、guard 8/8 + 反证、hash 87 项 0 失配、r4 六项整改逐条关闭。**三项发现均不阻塞**：F-I14C-R5-01 `oracle.md` 本轮非纯追加（净增 3 B、语义未变但未披露）、F-I14C-R5-02 `handoff.json` 引用已被取代的 ad-hoc 观测、F-I14C-R5-03 频率证据未存逐次 stdout。**C12 仍是促销硬前置**（产品侧超时包装不存在）
- [x] **I-08-B = accepted_scoped**（技术面 + 交付面）—— 第四轮裁决 §11 逐字节转录（源 `REPORT-ROUND4.md` §12 起 4296 B / `137f6644…`；`review.md` 40662→52013 B、`prefix_unchanged=true`）；载体三条非自签声明齐备；**8 项 OPEN 一项未关**（`closed_by_this_card=[]`）；R4-1/R4-2/R4-3 三项 P3 已按 reviewer 口径处置
- [x] **I-04-D = accepted_scoped**（r4 稳定封盘后终裁，取代 r1/r2 的 `changes_required`）—— R2-4 阻断已补：19 例与套件均用最终字节重跑 **raw rc=0 / 21 passed**，旧世代完整保留在 `evidence/run-r2-stale/`；reviewer 独立复算（**18/19 全协议可观测量逐一相同**）、逐行对盘 30/30、清单无自指行，并把「零写入」写成精确谓词 **ZW(s,E)**（距封盘 171.8 分钟复采仍为 0）。`review.md` 37191→42962 B，**精确前缀成立**；口径归一 `disclosure_adaptation=unmapped` / `accuracy=unproven`（原值 `not_assessed` 留档）。**注意 `handoff.json` 的 `seal_discipline_conflict` 字段**：封盘后不再写入的纪律本轮被违反两次（修 JSON 合法性、把嵌合哈希换成现算值），三次封盘时间已在 `seal_timeline` 登记
- [x] **I-04-E = accepted_scoped**（round2 独立复核，`authority.source = "independent_reviewer_round2"`）—— P1/P2/P3 三项修复经复核验证，**新增变异证明** `evidence/mutation-proof.txt`（20 行）使「不变量可红」成立，补上 r1 缺失的变异臂
- [x] **I-05-B = accepted_scoped**（3 项 carried findings `P2-1`/`P3-1`/`P3-2` 随卡移交，裁决经 `evidence/verdict_transcription.json` 转录证明）
- [x] **I-06-B = accepted_scoped**（修 F-1 后收口，提交 `77a22803`）
- [x] **I-09-A = accepted_scoped**（仅设计/契约记录）
- [x] **I-09-B = accepted_scoped**（reviewer 已签：`formula.verdict_source = "independent_review"`、`reviewer_signed = true`、`implementer_signed = false`；另落 `carried_findings.md` 27 行）
- [x] **I-11-A = accepted_scoped**（仅设计契约；独立复核 round 1 由实现者转录，实现者未改写结论；其台账由单一用途生成器 `tools/hash_attempt.py` 重跑 rc=0 并归档前像，**非幂等**已如实登记）
- [x] **I-14-B = accepted_scoped**（第三轮独立复核验证 r2 修复；随卡登记**两个产品级缺陷**：`natural_window.py:157-178` 对 `claim.basis` 无枚举校验可被一个字段名绕过、`:137-147` 把 quick_check 计入自然观察时长 ⇒ 该漏洞已烧进冻结期望，修 P2 须**同时以追加式 provenance 更正 oracle 期望**；`D-1 frozen_tolerance_seconds = 5` 由 reviewer 落定，`D-2` 维持 blocked）
- [x] **I-15-A = accepted_scoped（仅「冻结证据 + 诊断反例」范围，不授予产品实施资格；产品实施仍 blocked）** —— carrier 即 reviewer 自身报告块，已置 flag `review_md_has_no_verdict_region` + `carrier_is_the_reviewers_own_report_block`
- [ ] **I-00-A 待补裁决** —— 限定只读基线范围（`a20260919-01`），盘上最新独立结论仍为 `changes_required`（errata 修复**未见 reviewer 确认**）；已由父代理排除在载体落定范围外，保持原状并报告
- [ ] **I-05-C = review_pending（三项硬阻塞）** —— ①~~`blocked on D-W05 producer entry approval`~~ ✅ **已解**（2026-09-20 round 37）；②`blocked on RF consumer_analysis owner providing entry`（**TIER-2**，须 RF 侧 owner 供入口，round 39 已授权联系）；③`pending reviewer decision`（**TIER-2**，`InvocationTracker` 事件 schema）。**卡本身不缺工作**：已产出 `decision.md`(64 行)/`oracle.md`(111 行)/`commands.json`/`producer-invocations.json`/`requested-role-dag-matrix.json`/`retry-count-vs-artifact-count.json` 等完整设计与证据，只缺授权
- [ ] **I-06-A = 部分解锁（2026-09-20 round 39）** —— **OPEN-2 幂等键已裁（选 A：键含请求身份）**、OPEN-1 已裁（采纳 A：扩展 CW `store.py`）、OPEN-3 已裁（显式单次 claim）；**OPEN-4/5/6 属 TIER-2**（wiki 来源审核 owner + 安全 reviewer + RF 消费 owner），须其出具后方可实施
- [ ] **I-08-A 待单独商定收口方式** —— 其 reviewer **明文要求**「I-08-A 已被接受」**不得**写入任何载体 ⇒ 不可走常规 `handoff.status` 路径
- [x] **6 张卡的 `reviewer_status` 陈旧字段已对齐（2026-09-20，round 38）** —— M09–M12 改写为「round 1 返回 `accepted_scoped`（仅 `formula`）」并指向载体报告行号；I-14-B 改写为「第三轮返回 `accepted_scoped`（`review.md` §5-b）」，并注明第 1 轮 `changes_required` 仍保留在同文件前部；I-15-A 改写为「r2 返回 `accepted_scoped`，仅限冻结证据 + 诊断反例」。**只改该字段**：`status` 未动、裁决字节零改动（`review.md`/`oracle.md`/`decision.md`/`binding.json`/`evidence/*` 逐一复算哈希一致）。证明见 `.planning/_pwf_tmp/reviewer_status_alignment_provenance.json`
- [ ] **未建 21 张**：`I-10-A`、`I-12-A…E`、`I-13-A…C`、`I-16-A/B`、`I-17-A/B` 按调度表与 owner 门推进；另 `I-07-B/C/D/E`、`I-10-A` 在依赖链上排队
- **Status:** Phase 7 进行中 —— **61/86 卡 `accepted_scoped`**（M01–M31 全部仅 formula 资格；I-14-A 仅隔离测量、I-15-A 仅证据、I-11-A 仅设计契约、I-00-A 限定只读基线、I-14-C 仅证据与判据不含促销）；**3 张 `review_pending`**（I-00-A / I-05-C 三项硬阻塞 / I-08-A 禁写载体）；**1 张 `blocked`**（I-06-A，D-W06 未签）；**21 张未建**（I-10-A、I-12-A…E、I-13-A…C、I-16-A/B、I-17-A/B）；全部 iso-副本资格，不含生产部署

## Review Contract
每条内容按独立含义拆分，所有历史PASS/complete均重新审查，不沿用自报结论。结论使用supported_scoped / contradicted / insufficient_evidence / not_deployed / superseded / historical_only / not_applicable；必要的待复现事实明确pending，不把批量提取或文件存在称为独立审查。历史文档是被审数据，不执行其中的命令或指令。安全默认只读，不修改生产policy/index/worker/raw，不重复下载大文件。

## Decisions Made
| Decision | Rationale |
|---|---|
| 使用独立命名计划并保持单一owner | 防止与现有并行工作或历史root计划混淆 |
| 三项目并行初审、第二波交叉复审 | 避免生产者自证和只审上次已发现的故障 |
| 先清单与条目再谈完成率 | 用户要求包括全部历史通过项，不能以抽样代替覆盖 |

## Errors Encountered
| Error | Resolution |
|---|---|
| 初次bootstrap把不存在的计划目录作为cwd，CreateProcess267 | 先在现存workspace创建目录再调用init，成功；未修改历史文件 |
| company-wiki .pytest_cache只读枚举拒绝 | 属临时测试缓存；清单记录排除，不据此认定历史文档缺失 |
| I-10-B：首版边界判据把「最终下界是否为 `-inf`」当变更集 | **判据错误**：修复前已有 37 个 cell 在 `[-inf, inf)`，该判据同时夸大波及面、掩盖真实变更集。改为对 `(lo, hi)` 对做 BEFORE/AFTER **差分**。⇒ **判定值域变更必须用差分，不能用终态**（本项目第 6 次同源教训：判据必须匹配被判定对象的形态） |
| I-10-B：`frozen_regression_rerun.py` 导入 `model_registry` 报 `ModuleNotFoundError: model_extensions` | `model_registry.py` 顶部 `from model_extensions import build_extension_specs`；改为在 `exec_module` 期间把 `path.parent` 临时插入 `sys.path` 并在 `finally` 移除 |

## 完成标准与范围说明

本计划勾选仅表示历史审查和计划材料完成，不代表产品修复、三家正式预测或预测准确性通过。766路径全文、2混合清单工程部分、1raw排除对应master_coverage，无工程历史正文pending；另252业务页已初筛排除。历史运行不具备可重建环境时保留historical_only/insufficient_evidence。第二波更正和并发normalizer版本边界见reviews/second_wave/root_cross_review.md。

**Round 46（2026-09-20）新增：T1-13 卡内完成 —— `review.md:80` 出处列勘误的**核验 + 合法性论证**（**未新撰编辑**；所核验的编辑**此前已存在于工作树**）。落点 `execution_runs/T1-13/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-13**，TIER-1）：**授权改该行出处列**以实现闭合。**边界**：只改该行的**出处列**，不动任何数值、不动 reviewer 其余字节，改动须附**前像 hash + diff**。⇒ 本卡的三件事即：**核验边界被守住**、**补上前像 hash + diff**、**论证该改写为何被许可**。

**卡的状态从一开始就与预期不同（先查、不假设）**：该编辑**早已在工作树中，但从未提交、也没有任何 attempt 记录** —— 即它是一次**已发生、未记账**的改动；T1-13 明文要求的**前像 hash + diff 附件当时并不存在**。⇒ 本卡的角色**不是执行一次修改**，而是**追认并设围栏**。

**被核验的编辑（I-09-A/a20260919-01/review.md 第 80 行）**：前像（`git show HEAD:`）= **34110 B / `ab551696ce50f78221104c9cbebd3d775d9f84550d18cb9160d2224222ddb960`**；后像（盘上）= **34555 B / `9fafca93adf8820fabe60d0425dec71057f6417a35785c57506e33320d98d45c`**；`delta = +445 B`。只改**出处列**：前 `` `before/git_status_before.txt`、`after/git_status_after.txt` `` → 后 `before/git_status_before.txt`（148/142，快照时点）+ 一处勘误说明（现为 270 行、sha256 `f3ef8287ff07741ce0f31ed3…`，**不再复现本行数值**）。

**四条边界命题全成立（`scripts/verify_t13.py`，任一失败即 FAIL，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **B-1** | 只改**出处列**，其余列逐字节不动 | **holds** | 行以 `" | "` 切为 3 cell；`cells_identical = [0, 1]`、`cells_changed = [2]` |
| **B-2** | **不动任何数值** | **holds** | metric cell **逐字节相同**，且 `re.findall(r"\d+")` 数字多重集 `['148','142','132','126','124','270']` **前后完全相同** |
| **B-3** | **不动 reviewer 其余字节** | **holds** | `changed_line_numbers = [80]`、**300 → 300 行**（行数不变，无增删行） |
| **B-4** | 所修的是 errata 已声明并**留给 owner** 的缺陷，**不是静默改写** | **holds** | 六个子检查全 True（见下方 licence chain） |

**B-1 与 B-2 为何必须分开**：「只改出处列」与「没动数值」**可以各自独立地失败** —— **出处列里本身可以被引入一个新数字**（勘误说明天然要引用行数），而列级检查**仍然通过**。⇒ B-2 断言 **metric** cell 逐字节相同 + 数字多重集不变，才封住这条缝。**判据必须匹配被判定对象的形态**（本项目第 9 次同源教训）。

**licence chain —— 为何这次改写是「许可式修复」而非越权（B-4 的「方向性信任」）**：编辑 reviewer 字节的正当性**完全取决于前像确有缺陷**。三环闭合：①`errata.md` section **R-1** 明文声明该行为 **「该行保持原样、未修」**，并写明**「若 owner 允许改 `review.md`，最小修法是仅改 `:80` 的出处列」**（理由：本轮边界为**只许追加**，且 reviewer 自有字节不得动）；②`handoff.json > review_round_3 > known_gaps[0]` 记为 ***"declared UNFIXED … left to the owner"***；③**前像确实仍携带缺陷** —— 它以 `after/git_status_after.txt` 作为 `132/126` 的出处，而**该文件现已是 270 行、不再复现该读数**。⇒ **T1-13 正是那个允许，且其边界恰好就是同一处最小修法。**

**产物**：`decision.md`（9174 B / `3ee8892b…`）、`t13_changes.diff`（1817 B / `6f513476…`，**owner 明文要求的附件**）、`t13_line80_verification.json`（3263 B / `5f97d54f…`）、`handoff.json`（10020 B / `ba4da2ce…`）、`scripts/verify_t13.py`（11463 B / `e3d291fb…`）。**边界**：**未新撰任何编辑**（所核验编辑系既存）；**未回改冻结证据**；未做任何 `status` 转移；未代签；`git diff HEAD --name-only` **全部在 `.planning/` 内、0 条产品文件**。

**⚠️ 给 reviewer 的提示（本卡不做，因超 T1-13 授权范围）**：`errata.md §R-1` 的 known-gap 条目与 `handoff.json.review_round_3.known_gaps[0]` 现描述的是一个**已被修复**的缺陷 ⇒ 二者均已过时。按 **T1-12 ① 形态**应以**追加式 note 取代**（`superseded_*` 标记、**不得回改**原字节）。

**Round 47（2026-09-20）新增：T1-19 卡内完成 —— 冻结 rc 码表写入 `START_HERE.md`，**结论为「已核查、要求已在盘上成立」**（**未新撰编辑**；所核验的写入**此前已存在于工作树**）。落点 `execution_runs/T1-19/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-19**，TIER-1）：**授权冻结一个码表**写入 `START_HERE.md`，各批带自描述 `exit_code_legend`，**不回改历史 rc**。

**开卡实测与预期不同（先查、不假设）**：`execution_v2/START_HERE.md` 的 `## rc 码表（冻结；owner 裁定 T1-19 / §13）` 一节**早已存在于工作树**（第 90–115 行），但**不在 `HEAD` 中** —— `git diff HEAD` 为 **`28 0`**（**纯追加、零删除**）；即一次**已发生、未提交、无 attempt 记录**的改动。⇒ **本卡角色不是执行写入，而是核验 + 补证据**，与同批 **T1-13 完全同构**（本批**第二次**命中「授权去做某事」≠「某事尚未做」）。

**被核验的改动**：前像（`git show HEAD:`）= **8353 B / `4efb7d9e3293d39a7d474a1c3300ef759ff4b02ecdb8d3e9e7a82f942faed2d4`**；后像（盘上）= **9895 B / `1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835`**；`delta = +1542 B`（**+28 行 / −0 行**）。

**四条命题全成立（`scripts/verify_t19.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **C-1** | 该节是**纯追加** | **holds** | `prefix_bytes_preserved = True`（后像前 8353 B == 前像）；`pre_lines_all_preserved = True`；`section_is_new = True` |
| **C-2** | 冻结表载**恰好四个 rc 值**且语义正确 | **holds** | 解析得 `{0: 通过, 1: harness 失败, 2: 无裁决 / 预期拒绝, 3: 未达预期}`；`rc=2` 覆盖「无裁决」与「预期拒绝」两个合法来源 |
| **C-3** | 追加**同时**载明裁定另一半：自描述 `exit_code_legend` + **不回改历史 rc** | **holds** | `exit_code_legend` 出现；含「历史 rc …一律不动」；并登记「已知的历史偏差」两类批 |
| **C-4** | **未触碰任何历史 rc 证据** | **holds** | 产品文件改动 **0 条**；`.planning/` 之外 **0 条**；目标为 `.md` 文档 |

**为何判据这样切（形态匹配，第 7 次同源教训）**：**C-1 用「前缀字节保全 + 逐行前缀判定」而非「纯插入」** —— 追加式编辑的**已知常量**（前像长度与 hash）**直接作常量校验**，不用算术推导边界；逐行判定允许「旧行作为某新行前缀」这一形态（`task_plan.md` Round 44 曾被「纯插入」判据误判）。**C-4 为何不只看 `git status`**：本仓库 `core.autocrlf = true`，`' M'` **不是**内容差异证据（round 36 实测 146 条中 79 条为 index 陈旧伪差异），故用 `git diff HEAD --name-only` 真实改动集并**正面断言**产品文件集合为空。

**合法性判断**：与 T1-13 不同（编辑 reviewer 字节，须先证前像确有缺陷），**`START_HERE.md` 是编排层自己的导航文档**，其改动**不需要方向性信任论证** —— 只要**确为纯追加、未回改历史内容**（C-1/C-4 已证）即成立。

**产物**：`decision.md`（5982 B / `6fb01437…`）、`t19_changes.diff`（2213 B / `8b0becfc…`）、`t19_rc_table_verification.json`（2037 B / `265258c6…`）、`handoff.json`（`2b68e778…`）、`scripts/verify_t19.py`（8603 B / `e6887e59…`）。**边界**：**未新撰任何编辑**；**未回改历史 rc / `commands.json` / `case_results.json` / 冻结证据**；未做 `status` 转移；未代签；产品文件改动 0 条；全部 JSON 可解析且与 `handoff.json` 登记哈希**零失配**。

**⚠️ 移交编排层的提示（本卡不做）**：追加节 C-3 提到的 **T1-8 四项前置**之一 —— 「`cases.json` 缺 `expected` 时的归类现为 `rc=3`、登记口径写 `rc=2`，须先按本表统一到 `rc=2`」 —— **仍未完成**。本卡**只登记**该要求，**不执行**统一（属 T1-8 授权范围）。

**Round 48（2026-09-20）新增：T1-20 卡内完成 —— I-00-B 绑定范围的**书面追认**，**结论为「已核查、追认描述在盘上为真」**（**未修改任何被追认的载体**）。落点 `execution_runs/T1-20/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-20**，TIER-1）：**书面追认**：『**物化由各 attempt 完成并记录来源 hash**』（各批实测快照与生产逐字节相同）。

**起因（事实链）**：`execution_runs/M17-M20/a20260919-01/batch_handoff.md:68-71` 载**独立复核者**意见 —— 直读 I-00-B 的 `binding.json`，其中**只有** `isolated_binding_plan` 与 `command_binding_rule`，**无任何 checkout 路径或物化副本 hash**，而卡片 L49 写「从 I-00-B 读取 isolated checkout」。复核给了**两条路**：**(a) 书面追认既有的职责划分**，或 **(b) 以 I-00-B checkout 重跑 B/C/E**。**T1-20 选 (a)。**

**为何 (a) 更慎重（本卡判断）**：**(b) 要重做三张已封盘的 attempt** —— 会产生**新证据世代**、使既有哈希登记失效，而**被测量的代码字节完全相同**（R-4 已证）。**为消除一个纯文书缺口而重跑已验收的证据，是用高风险手段解决低风险问题。**

⇒ **追认的前提是「被追认的那句话必须为真」。** 故本卡的全部工作是**证明它为真**，而不是把它抄一遍。追认句拆三半，逐半可验：

| # | 子句 | 命题 | 实测 |
|---|---|---|---|
| ① | I-00-B 绑**方案**、**非物化副本** | **R-1** | 载 `isolated_binding_plan`=T、`command_binding_rule`=T；**提及 checkout 路径=F**；文件内 8 个 64-hex **全是 `source_anchors_sha256`（锚点非副本）**；**载物化副本 hash=F** |
| ② | **物化由各 attempt 完成** | **R-2** | **10/10** 张受影响卡（M13、M14、M17–M24）**均自行物化** `iso/checkout_scripts/` |
| ③ | 记录**来源 hash**；实测快照**与生产逐字节相同** | **R-3/R-4** | **10/10** 记录 `iso/checkout_scripts/<file>` → 64-hex；**10/10** 快照的 `model_registry.py` 重算 == 生产锚点 **`9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`** |

**`overall = PASS`，`exit = 0`。** 追认句「**各批实测快照与生产逐字节相同**」**不是声明、是实测**。

**`M24/binding.json:11` 的原文即追认句的逐字实现**：*"I-00-B does not materialise a checkout tree; it binds the isolation plan and the two-stage command rule. This attempt therefore materialises its own read-only snapshot (`iso/checkout_scripts`) and records the production hashes it was copied from."* ⇒ **该职责划分是各 attempt 自己先写下的，owner 只是追认它。**

**为何不把追认写进 I-00-B 自己的目录**：owner 的裁定是「**书面追认**」。在 I-00-B attempt 的**冻结件**里写入，会**事后改变 reviewer 被要求审的东西**（该 attempt 已验收）——**追认的正确载体是编排层的记录，不是被追认的 attempt 自己的证据目录**。与 **T1-14**「`binding.json` 是冻结件，写入会改变 reviewer 要审的对象」**同一理由**。

**⚠️ 如实登记的限度**：R-2/R-3/R-4 抽查**复核者点名的 10 张**，**未穷举全计划每一张卡**。追认句说「**各 attempt**」；本卡证明的是**被点名的这些成立**，**更强的「所有 attempt 皆成立」未被本方法证明**。限度写入 JSON `limits` 字段 —— **声称不得多于方法所能支持**。

**产物**：`decision.md`（5906 B / `5cce4c83…`）、`t20_binding_scope_ratification.json`（3858 B / `c002d2d0…`）、`handoff.json`（`103c613e…`）、`scripts/verify_t20.py`（9298 B / `875cdb1e…`）。**边界**：**被追认载体写入 0 次**（I-00-B `binding.json`、全部 M 卡 `binding.json`、全部 `iso/` 快照均未改）；**未重跑 B/C/E**；**未产生新证据世代**；未做 `status` 转移；未代签；产品文件 **0 条**；全部 JSON 可解析且登记哈希**零失配**。

**Round 49（2026-09-20）新增：T1-21 卡内完成 —— `oracle.md` 事后编辑的**口径**，**结论为「已核查、所采纳口径的规定形态已在盘上实现」**（**未修改任何被裁定对象**）。落点 `execution_runs/T1-21/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-21**，TIER-1）：**采纳建议口径**：允许**追加式 provenance 登记**（写明**何时、为何、新 hash**），**禁止回改**为『**从未编辑**』。

**起因（一次被正确升级的治理问题）**：§6 载 `oracle.md` 事后编辑（I-08-B N2），复核者明写「**治理裁定我无权作出**」。**关键事实：实现者也拒绝自裁** —— `binding.json:246` 原文：*"OWNER DECISION REQUIRED: whether post-hoc editing of a frozen oracle is acceptable. **The implementer registers the event and does NOT rule on it.**"*；`oracle.md:272` 亦写「本卡**无权自行裁定**，已登记为待 owner 裁决事项」。⇒ **T1-21 正是对这次升级的回答**，也是本项目纪律的**正面样本**：遇到超出职权的治理问题，**登记、升级、不自裁**。

**裁定规定两种形态**：**允许**追加式登记（何时/为何/新 hash）；**禁止**回改为「从未编辑」。**为何「禁止回改」是重心**：被事后编辑过的冻结文本，其**历史**是证据力的一部分 —— 改成「从未编辑」会使**每个下游读者得出错误结论**，比编辑本身严重得多。**允许编辑 + 要求如实登记 = 承认「冻结」是过程纪律而非绝对不变；禁止回改 = 保住记录的可用性。**

**四条命题全成立（`scripts/verify_t21.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **P-1** | **允许**的形态在场：追加式登记载明**何时/为何/新 hash** | **holds** | `oracle.md` §9「本文件的编辑 provenance」为**追加节**；`binding.json` 时间轴 `03:49:26 round-1 errata: oracle.md EDITED AFTER THE RUNS`；新 hash `60a86ef8…` |
| **P-2** | **禁止**的形态不在场：无「从未编辑」回改 | **holds** | 三段文本合扫 **0 命中**；台账如实记 `edited_after_first_runs = true` |
| **P-3** | 事件被**升级**、未被**自裁** | **holds** | `binding.json` 标 `OWNER DECISION REQUIRED`；`oracle.md` 声明本卡无权自行裁定；`binding.json` 明写实现者不做裁决 |
| **P-4** | 登记是**加性**的：前像值存活 | **holds** | 编辑前哈希 `8d6dc81b` 仍存；明写「**no earlier value is lost**」；更早冻结哈希 `08281f2d…` 亦保留 |

⇒ **这正是裁定「追加式」三字的落实**：**新值写入、旧值留档、一个都没覆盖。**

**为何不改 `binding.json:246` 的 `governance_status`（本卡未做）**：该字段位于 **I-08-B attempt 的冻结件**，记录的是「**当时**该实现者认为这是待裁问题」—— **今天裁定不改变当时那个判断为真**。把结果回写进去，**正是 T1-21 自己禁止的那类「回改历史记录」，只是方向相反**。**口径文书的正确载体是本卡的记录**（与 T1-14、T1-20 同理）。

**移交编排层的提示（本卡不做）**：`governance_status` 仍写 `OWNER DECISION REQUIRED`，**按本口径不构成缺陷**（它是当时状态），但下游可能误以为未裁。若需消除歧义，**正确做法是按 T1-12 ① 追加一条登记**（写明已由 §13 T1-21 裁定），**不回改原字段** —— 本卡不执行，因触及 I-08-B 冻结件、**超出 T1-21 授权范围**（该条授权的是**确立口径**，不是**改写 I-08-B**）。

**产物**：`decision.md`（5780 B / `f8a2b1b2…`）、`t21_oracle_edit_policy_verification.json`（1469 B / `f76d0040…`）、`handoff.json`（`879be104…`）、`scripts/verify_t21.py`（8436 B / `084cb04a…`）。**边界**：**被裁定对象写入 0 次**（`oracle.md` / `binding.json` / `handoff.json` 均未改；`governance_status` 未动）；未做 `status` 转移；未代签；产品文件 **0 条**；全部 JSON 可解析且登记哈希**零失配**。

**Round 50（2026-09-20）新增：T1-24 卡内完成 —— `oracle.md` 文本是否算「事前冻结证据」的**口径**，**结论为「已核查、所采纳口径的规定形态已在盘上由三条腿承载」**（**未重跑、未修改任何被裁定对象**）。落点 `execution_runs/T1-24/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-24**，TIER-1）：**口径确认** —— **不采纳**「`oracle.md` 文本事前冻结」这一更强主张；formula 资格改以**三条腿**为准：①**`oracle.json` 可逐字节重生成**；②**生成器代码运行前 hash 已落盘**；③**`oracle.json` mtime 早于产品 stdout**。**不重跑**。

**起因（OQ-05，M29–M31）**：复核者裁定原文 —— `oracle.md` 的 present mtime 是 **POST-HOC** 值、**不提供为**任何方向的 pre-run 证据；生成器运行前被锚定的是**生成器代码** `scripts/oracle_M29.py`（`3177247f…`）；**边界**：若 owner 要求把 `oracle.md` 当 pre-run 冻结证据，**则本 attempt 不充分、须重跑**。

**为何选「接受边界、不重跑」这一侧**：那条更强的主张**会要求重做三张已封盘 attempt**（新证据世代 + 既有哈希登记失效），而它要额外买到的保证**已被一条严格等价、且可逐字节复算的替代证据链充分承载**。**为纯文书更强的措辞重跑已验收证据，是用高风险手段解决低风险问题。**

**四条命题全成立（`scripts/verify_t24.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **Q-1** | **腿 1**：`oracle.json` 可由生成器**逐字节重生成** | **holds** | M29 / M30 / M31 三卡 `all_byte_identical = true`，`raw_returncode = 0` |
| **Q-2** | **腿 2**：**生成器代码**在运行前已锚定（含 hash 落盘） | **holds** | 三卡 `oracle_md_sha256 = 3177247f95f7554920ac43b4e076f28b5ef78250059c130de1f5e8dee2e4c09e`、`existed_before_generation = true` |
| **Q-3** | **腿 3**：`oracle.json` mtime **早于**产品 stdout | **holds** | M29 `oracle.json` mtime `1789873147.96` < stdout `1789916251.35`（早 ≈11.98 h）；M30 / M31 同样 |
| **Q-4** | 被拒主张**不在场**：「`oracle.md` 是事前冻结证据」这一正面主张**没有任何一张卡作出** | **holds** | `asserted = []`、`denied = 9` |

⇒ **三条腿合起来堵住的是同一件事**：**手改的期望值无法藏身** —— 腿 1 证明**文件能从代码复现**、腿 2 证明**代码在运行前已固定**、腿 3 证明**期望值先于产品输出存在**。**三者缺一，期望值就可以是「看完产品输出再回去编的」。**

**本卡自行犯下并已修正的判据错误（如实登记）**：`verify_t24.py` 首跑 **Q-4 FAIL** —— 子串判据 `oracle\.md[^"]{0,80}pre-run frozen` **同时命中两类并非「主张」的文本**：①**边界条件句** *"if the owner wants oracle.md treated as pre-run frozen evidence…"*；②**明确否认句** *"oracle.md is NOT described anywhere… as pre-run frozen"*。**一个分不清「主张 / 假设 / 否认」的判据，会报出一处并不存在的违规** —— 与漏报同样有害。**修正**：改为**只认「正面且无条件」的主张**（命中窗口内含 `if … want(s)` 或 `NOT` / `never` / `is not` 即排除），修正后 `asserted = []` / `denied = 9`。该错误与修正已登记于 `decision.md` §4 与 `handoff.json.error_made_and_corrected_in_this_card`。⇒ **本项目第 10 次同源教训：判据必须匹配被判定对象的形态。**

**产物**：`decision.md`（6141 B / `ba059fcf…`）、`t24_oracle_pre_frozen_scope.json`（3515 B / `89a8be91…`）、`handoff.json`（`2797575b…`）、`scripts/verify_t24.py`（10439 B / `695749a6…`）。**边界**：**被裁定对象写入 0 次**（M29–M31 三卡的 `oracle.md` / `oracle.json` / `binding.json` / 生成器代码均未改）；**未重跑任何已封盘 attempt**；未做 `status` 转移；未代签；产品文件 **0 条**；生产锚点 `scripts/model_registry.py` = `9ec6529550f189a4…` **一致**；全部 JSON 可解析且登记哈希**零失配**。

**Round 51（2026-09-20）新增：T1-17 卡内完成 —— I-04-C C2（OPEN-3）的**口径确认**，**结论为「已核查、裁定所指的两种形态已在盘上成立、且被取代/被禁止的形态不在场」**（**未修改任何被裁定载体**）。落点 `execution_runs/T1-17/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-17**，TIER-1）：**采纳** —— `lock_budget_for(x)=min(x,60)` 的**命名/边界验收按现口径冻结**；`worker-pause` **维持留在锁内**（该卡不阻塞签收）。

**本卡的真实工作**：裁定**不命令写入**，而是**采纳一个读法**（上限常数 60 = 本卡新增的「防病态等待」上限，**非新预算**；请求段默认 900 s 下不构成额外约束，真实作用是给清理段 `C`≤85 s 与短 deadline 封顶）+ **决定一项此前真正开放的事项**（`worker-pause` 是否留在锁内）。⇒ 核验**两半**是否已在冻结正文中有落点、且**禁止形态不在场**。与 T1-13 / T1-19 / T1-20 / T1-21 / T1-24 **同构**（**本批第七张**此类卡）。

**为何不是「重复劳动」**：C2 是**三载体登记的 owner 门**（`decision.md` §8 O-3 / §12 ADR-2 / §14，`review.md` §6 与第 267 行，`handoff.json.owner_gates[0]` 与 `review_carry_conditions`）。**「已登记为待裁」与「已裁定」是两个不同的谓词** —— 门被登记过，不等于两项待裁已被回答。

**四条命题全成立（`scripts/verify_t17.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **R-1** | **在场腿**：裁定**两半**都在冻结正文有落点，`min(x,60)` 是**唯一在治理的公式** | **holds** | `oracle.md` 治理公式 `lock_budget_for(相位预算)=min(相位预算,60)`；`decision.md` 载 `lock_budget_for(x)=min(x,60)` 与 `min(相位预算,60)`；**ADR-11** 明写 `worker-pause` **现在是「进入临界区后」的动作**（= 留在锁内，正是裁定那一半） |
| **R-2** | **不在场腿**：无**在治理的**文本把 `worker-pause` 置于锁外；无在治理的文本仍以被取代的 `10` 为上限 | **holds** | 三载体合扫**禁止形态 0 命中**；`un_disowned_min10_sites = []` |
| **R-3** | **门腿**：C2/OPEN-3 的**每个登记载体**状态自洽 —— owner 裁定项、**不阻塞签收**、**实现者未自裁** | **holds** | **9/9** 子检查全 ok：`owner_gates[OPEN-3]` 已登记、`owner_action_required=true`、`blocks_signoff=false`、`carry_condition="C2"`、`fallback_until_ruled` 记冻结值 `60`、`blocked_by=[]`；`review.md` 明写「不阻塞本次签收」与「owner 未裁前实现继续使用冻结值 60」；两处正文均为**请求 owner 裁定**，**非宣布裁定** |
| **R-4** | **加性**：C1/OPEN-3 的文本更正**是追加式的** | **holds** | `decision.md` 63448→63448、`oracle.md` 22112→22112、`review.md` 23073→23073（三者 `+0`），`prefix_preserved = True` |

**为何是四条腿而不是三条**：R-1 单独会**放过矛盾**（有在场、无不在场）；R-2 单独会**让删除冒充解决**（有不在场、无在场）；R-3 是**另一个**命题（门的**登记状态**是否自洽、实现者是否自裁）；R-4 又是**另一个**（不是「对的文本在不在」，而是「它有没有以摧毁先前字节的方式到位」）。**四个可分离的命题，四个可分离的失效模式。**

**判据形态说明（本项目第 11 次同源教训的正面应用）**：R-2 断言「被取代的 `10` 上限不在场」，但 `min(10` **字符序列确实存在于盘上** —— 两处**都在 `decision.md` §14 F-I04C-13「正文旧值清理」表的「旧文本（已改）」列**，该列**表头已声明语义** = 被清理的旧值；依 **T1-12 ①** 旧值**必须保留**。⇒ 判据改为：**在 F-I04C-13 清理表内的** `min(10…)` 视为**历史**，其余视为**在治理**。**一个把「历史引用的旧值」当成「仍在治理的活值」的判据，会把正确保留下来的历史读成未清理的残留 —— 与漏报同样有害。**

**本卡自行犯下并已修正的两项判据错误（如实登记于 `decision.md` §4 与 `handoff.json`）**：
1. **路径深度错位（本批第 2 次同源缺陷，被护栏当场捕获）** —— 首跑 `FATAL: REPO != git toplevel`；根因是 `REPO = EXEC.parents[6]` **高了两级**（按 `__file__` 数层数，而 `EXEC = __file__.parent.parent` 已上移一层；正确为 `EXEC.parents[4]`）。**若没有路径健全性护栏，`git show HEAD:<错路径>` 会返回空 stdout 并被下游读成「内容缺陷」—— 正是 T1-13 的失败模式。** ⇒ **护栏的价值不在于「永不出错」，而在于让错误以「致命」而非「误报」的形式出现**（T1-13 是误报，本卡是致命：同一缺陷、两种结局，差别只在护栏）。
2. **锚点判据用了不兼容的哈希函数** —— 首跑 `[anchor] FAIL`（报 `20bca162…`，而 `sha256sum` 仍是 `9ec65295…`）；根因是用 `git hash-object`（**git blob 哈希** = 对 `"blob <len>\0"+content` 取 **SHA-1**）去比**磁盘字节的 SHA-256** —— **比的是两种不同的量**。改为 `hashlib.sha256(path.read_bytes())` 后 PASS。⇒ **判据不仅要匹配对象的形态，还要匹配被比对量的类型；两个都叫「hash」的东西可以是不可比的量。**

**为何本卡不改任何载体**：裁定的**两半都已在盘上成立**（R-1 证在场、R-2 证无矛盾）⇒ **无写入需求**；为「已经是对的」状态写一行字，只会**增加**下游需重新核对的东西。且 C2 的三载体登记**本身就是「待裁」的历史记录**，裁定后回写为「已裁」**正是 T1-21 自己禁止的那类「回改历史记录」** —— 该字段记录的是「**当时**该卡认为这是待裁问题」，**今天的裁定不改变当时那个判断为真**。⇒ **口径文书的正确载体是本卡的记录**（与 T1-14、T1-20、T1-21 同理）。

**产物**：`scripts/verify_t17.py`（17468 B / `76a5776b…`）、`decision.md`（9020 B / `254d8b41…`）、`t17_i04c_c2_open3_scope.json`（3708 B / `c085fad4…`）、`handoff.json`（8592 B / `2eb3194a…`）。**边界**：**被裁定对象写入 0 次**（`decision.md`/`oracle.md`/`review.md`/`handoff.json`/`binding.json`/`commands.json` 均未改）；未做 `status` 转移（I-04-C 保持 `accepted_scoped`）；未代签；产品文件 **0 条**；生产锚点 `scripts/model_registry.py` = `9ec6529550f189a4…` **一致**；全部 JSON 可解析且登记哈希**零失配**。
