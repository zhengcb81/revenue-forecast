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

**Round 52（2026-09-20）新增：T1-16 卡内完成 —— M02-01「被忽略字段是否仍受域约束」的**口径确认**，**结论为「已核查、裁定的事实前提在当前构建上经**执行复现**成立」**（**未改任何产品代码、未改任何被裁定载体**）。落点 `execution_runs/T1-16/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-16**，TIER-1）：**选 A（保持 fail-closed）**。理由：`base=-5` 实测仍被拒 ⇒ **现行为已是 fail-closed**；改 B（忽略未用字段）会放松校验面，风险大于收益。

**本卡比 T1-17 / T1-24 更强一档**：T1-17 / T1-24 核验的是「裁定的**采纳形态**已在**文书**中成立」；**T1-16 核验的是关于产品的事实前提**。裁定**选 A = 「保持现行为」**，其理由是一条**关于产品、而非文书**的断言。**若该前提为假**（产品已不再拒绝负 base），「选 A」就是**在选一个不存在的东西**，甚至是在**产品已漂移到 B 的情况下宣称选了 A**。⇒ 必须**以执行复现该前提，而不是引证** —— 引证该卡**自己记录的观测**等于**引证被检验的东西本身**（循环论证）。与 T1-13 的方向性信任同一纪律。

**五条命题全成立（`scripts/verify_t16.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **S-1** | 校验器对 `base_revenue` 执行的是**统一的、dispatch 前的**负数检查，**与该模型是否真的用到该字段无关** | **holds** | ①源码：检查在 `calculate_registered_model` 内、**先于** dispatch；②**执行探针**：对 `direct_revenue`（`del base_revenue`，**不用**）与 `direct_growth`（`current = base_revenue`，**真用**）**双双抛错** ⇒ 该检查**不可能**是模型条件性的 |
| **S-2** | 对 `direct_revenue`，该字段**确实被忽略**：`base=999` 与 `base=1` 输出**完全相同** | **holds** | 实测 `base_1 = base_999 = [10.0, 12.0]`；源码 `model_registry.py:98` `del base_revenue, years` |
| **S-3** | 拒绝是**真实的** `ModelRegistryError`，消息形态**与记录一致** | **holds** | 实测 `ModelRegistryError: direct_revenue.base_revenue cannot be negative`；与 `evidence/M02/run_result.json > observations[OBS-NEG-BASE].message` **一致** |
| **S-4** | 被否的**选项 B 不在生效** —— 负 base **绝不被静默忽略**，守卫**无条件** | **holds** | 负 base 对该「忽略字段」模型**仍抛错**（**若为 B 本应返回值**）；守卫为裸 `if base < 0: raise …`，**无模型成员测试** |
| **S-5** | 裁定**不命令写**：冻结证据**未被触碰**，门**仍登记为 owner 保留**（**未自裁**） | **holds** | 产品文件改动 `[]`；`M02` 卡目录改动 `[]`；`open_questions` 仍载 `requires_owner_or_specialist_ruling`；`review.md` 载 `CLOSED-AS-RESERVED` |

**为何 S-1 要用两个模型而不只看源码**：只看源码**不足以**支撑「**统一性**」这一普遍命题 —— 源码可能被别处覆写、被下游绕过、或根本不是被执行路径。探针**刻意挑两个模型**（一个 `del`s 字段、一个**消费**它）；**若检查是模型条件性的**（正是选项 B 的某种形态），**二者必然不同**。**实测二者都抛错 ⇒ 结构性不依赖模型。** ⇒ **普遍性主张只能靠「在应当相同的多个实例上实测相同」来支持；单点观测在原理上无法支持它。**

**为何**不写入**即是执行**：裁定选 A = **保持现行为** ⇒ **任何编辑都会偏离裁定所选的行为**。本卡正是**通过不写入来完成它**。且 M02-01 仍为 owner 保留项（S-5 已证）—— 裁定**给出了答案**，但**不改变**「该卡当时把它登记为 `requires_owner_or_specialist_ruling`」这一历史事实为真 ⇒ **回写为「已裁」正是 T1-21 禁止的那类回改**。

**本卡自行犯下并已修正的两项错误（均为 harness 缺陷，非产品缺陷；如实登记）**：
1. **`@dataclass` 加载期 `AttributeError: 'NoneType' object has no attribute '__dict__'`** —— 根因：`importlib` 加载时**未先把模块注册进 `sys.modules`**，而 `@dataclass` 经 `sys.modules[cls.__module__]` 解析注解 ⇒ 模块缺席即崩。修正：`exec_module` **之前**先 `sys.modules[spec.name] = mod`。**若误判为产品缺陷，会得出「产品不可导入」的错误结论。**
2. **`ModelSpec.get` 不存在** —— 根因：按 **dict** 写探针，而 `ModelSpec` 是 **frozen dataclass**。修正：按声明字段（`required + optional`，`ratio_drivers` 给无量纲值）构造驱动。⇒ **又是「判据/假设必须匹配对象形态」，这次连对象的**类型**都假设错了。**

**⚠️ 本卡**不**声称 M02 的 D/E 步骤已解决**（`decision.md` 载 E 属 I-10-A、F 需 I-12 冻结设计）；**只**回答 M02-01 这一项。

**产物**：`scripts/verify_t16.py`（17518 B / `2c31cfa5…`）、`decision.md`（7508 B / `c100d8e4…`）、`t16_m02_01_fail_closed_scope.json`（4197 B / `70ade848…`）、`handoff.json`（8104 B / `c6944fd6…`）。**边界**：产品代码改动 **0 处**；被裁定对象写入 **0 次**；未做 `status` 转移（M02 保持 `accepted_scoped`）；未代签；产品文件 **0 条**；生产锚点 `scripts/model_registry.py` = `9ec6529550f189a4…` **一致**（**必要**：裁定的前提是关于**这个**构建的）；全部 JSON 可解析且登记哈希**零失配**。

**Round 53（2026-09-20）新增：T1-18 卡内完成 —— I-14-B D-1 时间容差冻结**及其限度**的口径确认，**结论为「已核查、裁定的**两半**都在盘上成立」**（**未修改任何被裁定载体**）。落点 `execution_runs/T1-18/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-18**，TIER-1）：**确认** `frozen_tolerance_seconds = 5`、`capture_latency_tolerance_seconds = 5`（合法带 `[1, 86] s`）。**但签字 ≠ 可开真实窗口**：真实 30/60/120 **维持 `blocked`**（见 T1-9）。

**为何本卡有**两半**且必须**同时**成立**：裁定同时做两件**方向相反**的事 —— ①**确认冻结值**（追认 reviewer 的冻结）；②**确认一条限度**（签字**不**授予开窗权）。⇒ **只核验 ①** 是危险的：可在「那条使其不可被主张的边界已被侵蚀」时去「证明」资格已就绪；**只核验 ②** 则忽视了被追认的值本身。⇒ 两半是**独立的腿**，且第二半须对照裁定所引的**原始标准**（T1-9）来测，而非对照被弱化的复述。

**五条命题全成立（`scripts/verify_t18.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **U-1** | 冻结**在生效**、**值**为所追认的 `5 / 5`；签署者是**独立 reviewer**（非实现者），签名行在场 | **holds** | `frozen_tolerance_seconds = 5`；review 载 `` `capture_latency_tolerance_seconds` 同为 5 ``；`frozen_by = independent reviewer session (DSH agent session-b0e4a430ca7d)`，**不含** implementer；`frozen_at_utc = 2026-09-20T03:15:44Z` |
| **U-2** | 合法带 `[1, 86] s` 是**推导出来的**（**两个独立界**），非偏好选择；冻结值 `5` **落于**带内 | **holds** | **下界 1**：L1 实测 `tol=0.9 拒 / 1.0 起通过` ⇒ <1 s 会**误杀合法即时截图**；**上界 86**：L2 实测 `tol ≤ 86 拒 / 87 起通过`（历史累计等待 29/88/207）⇒ ≥87 s 会让**已复现的缺陷通过**；带在 review 与**裁定本身**均有记载 |
| **U-3** | **限度完好**：真实 30/60/120 仍 `blocked`、`blocked_by` 仍**点名缺哪些前置**；**无人把签名转成运行** | **holds** | **8/8** 子检查全 ok：`blocked_by` 载 `30/60/120` + `BLOCKED` + 缺前置（`pre-placed recorder`/`owner authorisation`）+ 需 `new attempt + new binding`；`reviewer_status` 载 `real UI-immediacy qualification (stays blocked)`；自然观察仍 `NOT granted (17 rows still pending)` |
| **U-4** | **被拒形态不在场**：实现者的 `5 s` 仍标 `NOT frozen`；无文本称冻结**足以开窗**；裁定的**否定句**在场 | **holds** | `unmarked_proposal_sites = []`；`window_opening_claims = []`；否定句 `签字不等于可以开真实窗口` 在场 |
| **U-5** | 裁定**不命令写**：本卡**未触碰** I-14-B；冻结四行**逐字节完好** | **holds** | I-14-B 卡目录改动 `[]`；产品文件改动 `[]`；冻结四行逐字节在场 |

**为何 U-2 不是装饰**：裁定引的是一个**带**。带的断言形态是「**低于 1 是错的，且 87 及以上是错的**」= **双侧主张**，需要**两个界**且**分别独立**推导。**若只核验「值是 5 且在 [1,86] 内」，就等于把「被要求核验的那个带」当成前提。** **判据必须匹配对象形态：对象是带，判据就必须是两个界而非一个点。** 两个界来自**相反的关切**（诚实样本不被误杀 vs. 已复现缺陷不被放行），这才使「带」有意义。

**本卡自行犯下并已修正的两项判据误报（首跑 U-1 / U-3 双 FAIL，对象本身无缺陷）**：
1. **U-1：判据要求了错误的表层形式。** review 把该值写成 `` 同为 5 ``（"likewise 5"），我却在找 `capture_latency_tolerance_seconds = 5`。⇒ **要求某一特定写法的判据，会把「确实在场的值」报成缺失。**
2. **U-3：判据分不清「陈述」与「否认」。** 原文 `签字只把它从"blocked"变为"可开卡"，不等于已运行` —— **一句含「运行」二字的否认句**；我的探针只 grep `运行/ran`，**命中该否认**，报出**与事实相反**的结论。⇒ **判据必须只统计「肯定且无否定」的陈述。** **与 T1-24 Q-4 完全同源**：**一句否认句里含有关键词，会把「明确否认」读成「明确主张」。**

**为何不改任何载体**：两半已在盘上成立 ⇒ 无写入需求；且 D-1 的注册仍如实写着「实现者提议 5 s、NOT frozen」（U-4 已证仍标 `NOT frozen`），那是**冻结前**原文，reviewer 选择保留，`oracle.md` §11.2 已明写「实现者不得回改这四行」——**回改它才是错的**（依 T1-12 ①，旧值必须留存）。

**⚠️ 本卡**不**授权开真实窗口**：真实 30/60/120 **维持 `blocked`**（U-3 已证）；T1-9 亦维持**不授权**新建 UI/进程捕获路径。**「签字 ≠ 可开窗」这条限度本身，就是本卡要核验并在场的对象之一。**

**产物**：`verify_t18.py`（18121 B / `008268a3…`）、`decision.md`（7179 B / `927525d2…`）、`t18_i14b_d1_tolerance_scope.json`（4023 B / `e6be51ca…`）、`handoff.json`（**9322 B** / **`af03ebc6bf30b41452e58bfee1707cab4f371b59150737bc93c84f5abc134c93`**）。**边界**：被裁定对象写入 **0 次**；未做 status 转移（I-14-B 保持 `accepted_scoped`、真实窗口维持 `blocked`）；未代签（未替 reviewer 追签、未替 owner 授权开窗）；产品文件 **0 条**；生产锚点 `9ec6529550f189a4…` **一致**；JSON 全部可解析、登记哈希 **3/3 MATCH**。

> **本批第九张「已核查」收口的 T1 卡**（T1-14、T1-27、T1-19、T1-20、T1-21、T1-24、T1-17、T1-16、T1-18）。本张新增的关键区分：**当裁定同时「追认一个值」并「确认一条限度」时，两半必须分别核验** —— 只验前半会**放过边界的侵蚀**，只验后半会**忽视被追认的值**。另：**「带」是双侧主张，单点判据在原理上无法支持它**；以及**否认句含关键词**再次导致误报（与 T1-24 同源）。

**Round 54（2026-09-20）新增：T1-26 卡内完成 —— I-14-A D1/D2/D3「owner 层面放行」的**半授权**口径确认，**结论为「已核查、授权的两半都在盘上成立，且授权未越界」**（**未修改任何被裁定载体、未做任何晋升**）。落点 `execution_runs/T1-26/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-26**，TIER-1）：**owner 层面放行** —— **授权将该补丁的晋升流程启动**，但 **D1/D2/D3 的专业签字仍属他方**（见 TIER-2）。**未获该三方签字前仍禁止**把 `iso/slo_probe_patched.py` 拷进 `RF/tools/`；**I-16 实测前必须先提供 bundle 测量文件**。

**为何这条裁定不能用「去核验有没有做」来处理**：它**一句话里做两件方向相反的事** —— **授予一个许可**（启动晋升流程）**同时保留使其生效的东西**（三条专员签字），并**重申一条既有禁令**。**「授权启动某事」是许可、不是动作；许可本身不留痕迹** ⇒ 「它被做了没有」是一个**范畴错误**的问题。⇒ **本卡能核验的不是「授权是否被执行」，而是「授权没有越界」**。

**本卡存在是为了堵住哪种崩溃**：把「**owner 层面放行**」读成「**禁令解除**」或「**三条签字到手**」，于是**把补丁拷进 `tools/`（即 `RF/tools/`）**。这正是本批执行纪律第 7 条 **「总的批准」不得膨胀为「所有的结论」** 最具体的一种形态。

**六条命题全成立（`scripts/verify_t26.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **V-1** | 授权腿是**许可**形态，且**未留任何产物** | **holds** | 裁定用动词 `授权…晋升流程启动`；`tools/` 下晋升/变更窗口同名之物 `[]`；晋升测试副本 `tools/tests/test_slo_probe_patched.py` **不存在**；补丁**仅存在于本 attempt 内**（`iso/` 与 `harness/` 两处，**逐字节相同** `14932c74…`） |
| **V-2** | 保留腿**仍被保留**：D1/D2/D3 各自仍属他方，**无载体读成已签** | **holds** | D1 → **非本探针作者的运维 reviewer**（`must NOT be the author of this probe`）、状态仍 `UNSIGNED — blocks promotion`；D2 → **生产 SLO / 探针 owner**、仍 `awaiting owner confirmation`；D3 → **I-16**、仍 `awaiting I-16`；伪造签名主张扫描 `[]` |
| **V-2b** | **判据本身有的放矢**（自检）：开火与不开火两侧都正确 | **holds** | 合成「真已签」样本 **5/5 命中**、零漏报；合成「只是签名词汇」样本 **7/7 不命中**、零误报 ⇒ **V-2 的 PASS 不是空过** |
| **V-3** | 禁令**在盘上**且**指名 `RF/tools/`** | **holds** | 四载体齐备（`decision.md`/`review.md`/`oracle.md`/`handoff.json.promotion_blocked`）且**均指名目的地**；`statement` 明写 `must NOT be copied into RF/tools/` |
| **V-4** | **禁令被遵守**（**承载本卡**）：补丁**真的不在**产品路径上 | **holds** | 生产 `tools/slo_probe.py` **内容** == 冻结**补丁前**像；字节差异**仅换行**；工作副本 == `HEAD`（`413aad5f…`）；`tools/` 下 `slo_probe*` 仅 `tools/slo_probe.py` + `tools/tests/test_slo_probe.py` |
| **V-5** | TIER-2 登记**仍写「待裁方」**，未膨胀为「owner 已裁」 | **holds** | T2-5/6/7 三行**均指名待裁方**且**均为「授权送签」**；越界登记 `[]`；执行纪律条文在场 |

**为何 V-4 承载本卡**：**禁令只有在「文件真的不在」时才成立。** 「禁令已登记」是文书事实，「禁令被遵守」是**产品事实** —— 后者**只能靠执行核对**，不能靠引证禁令自身（那是**循环论证**）。

**本卡自行犯下并已修正的**四类**判据误报（首跑 V-1/V-2/V-4/V-5 四 FAIL，对象本身均无缺陷）**：

1. **V-1 —— 判据按「文件名关键词」界定对象。** 我用 `promot` 字样全仓扫描，命中**无关子系统的 `portfolio_promoter.py`**。⇒ **名字碰撞，不是证据。** 修法：**按目的地界定**（本仓「晋升」只有一个目的地 = `tools/slo_probe.py`）。
2. **V-2 —— 判据检验了「签」的词汇，而非「已签」这个谓词（连续四稿皆错）。**（1）**逐行关键词 grep** 命中**禁令本身**（`must not happen until D1 is signed`）；（2）**段落级共现** 命中**无关子句**（`the reviewer independently confirmed the --as-of-date fact`）；（3）**子句级** 仍命中三处**非主张**（`**Signer:** I-16` = 指认谁**将要**签；`It fails closed` = **fail-closed 术语**；`for the D2 signature` = **尚待产出的文书名词**）；（4）把 `accepted` 当签动词，命中 `is **not** self-accepted`（**命令不得自签**），且 `—` 破折号**把那句从中间切开**，否定护栏失效。⇒ **判据必须检验「已签」这个谓词，而不是「签」这套词汇**；且 `accepted` 必须剔除（本语料里它多指 **reviewer 对卡的 `accepted_scoped`**，与「专员签署一项决定」是**不同谓词**）。
3. **V-4 —— 判据的比对面不匹配所问的问题；此项险些得出反向的严重错误结论。** 首跑用**原始字节 sha256** 比「生产 vs 前像」，得 `production_is_still_the_pre_patch_image: false` ⇒ 若照此收口，结论将是 **「补丁已被晋升」** —— **本卡存在的理由本身被误报为已发生**。根因：本仓 **`core.autocrlf = true`**，`iso/` 副本在盘上是 **CRLF**（142 行）、出库的生产文件是 **LF**，**两者内容完全相同**。⇒ **原始字节哈希在跨它们比较时会报出不存在的差异。** 修法：**这是内容问题，判据就按内容比**（归一化换行），并把「字节差异仅为换行」**显式写成一条可读证据**。**这是本仓第 6 次命中同一族陷阱**，且**代价最高的一次**（会把「禁令被完美遵守」报成「禁令已被突破」）。
4. **V-5 —— 判据把「禁令本身」当成「违规」。** TIER-2 前言明写 `本类**不得**记为「owner 已裁」`，我的关键词 grep **把这条禁令读成了越界登记**。⇒ **同一张卡内第三次**命中「否认句含关键词」缺陷（与 T1-24 Q-4、T1-18 U-3 同源）。

**为什么「不改任何载体」就是执行**：裁定**没有命令任何写入**。它**授予一个许可**并**重申一条禁令**，二者在盘上**均已在位**：授权腿的许可**本就无形**（V-1 已证无产物；**为它造产物反而把许可变成了动作，即越权**）；保留腿的三条签字**本就仍属他人**（V-2；**替其出签即伪造签名**）；禁令**本就在盘上**（V-3）且**已被遵守**（V-4）。⇒ **本卡正确的动作是「核验并保持」，不是「编辑」。**

> **本批第十张「已核查」收口的 T1 卡**（T1-14、T1-27、T1-19、T1-20、T1-21、T1-24、T1-17、T1-16、T1-18、T1-26）。本张新增的三条关键区分：**①「授权启动某事」不能被核验为「已完成」，只能被核验为「未越界」**（许可无形，有形即越权）；**②禁令只有在「文件真的不在」时才成立** —— 务必执行核对、不得引证禁令自身；**③「一个永不开火的判据，靠没开火什么也证明不了」** ⇒ 判据的 PASS 必须附**响应性自检**（喂合成正负样本，两侧都要对）。

**产物**：`verify_t26.py`（**24001 B** / `c6c921b4c721aebcd9378b650e2128137819a053bde4964750ac308a71fa1d11`）、`decision.md`（**11861 B** / `a7a0deaea29ac3b445b5a8da9c0392616cac885305a19d5b7eb2b47c01c511c1`）、`t26_i14a_d1d2d3_release_scope.json`（**3314 B** / `e574097c3c7f2816f157aa9d142df0b916aa02c52eec217e47d3bba89cb27b97`）、`handoff.json`（**11663 B** / **`ef00b04ad868ec661b1478382b9ab53ef56192c05a7b3d3833b0754b53e99b16`**）。**边界**：被裁定载体写入 **0 次**；**晋升动作 0**（补丁未入 `tools/`）；status 转移 **0**；未代签（未替三条决定出签）；产品文件 **0 条**；生产锚点 `9ec6529550f189a4…` **一致**；JSON 全部可解析、登记哈希 **3/3 MATCH**。

**⚠️ 本卡**不**授权**：**把 `iso/slo_probe_patched.py` 拷进 `RF/tools/`**（**在 D1 由非本探针作者的运维 reviewer 签署前仍禁止**）；**I-16 的生产测量**（仍**须先提供 bundle 测量文件**）；**签署 D1/D2/D3**（属他方 TIER-2，**本卡不签任何东西**）。

**Round 55（2026-09-20）新增：T1-5 落地 —— 为 8 个扩展模型补最小回归**，**结论为「新回归已写、已跑绿、且已入库」**（**未改任何既有测试、未改产品源码、生产锚点未变**）。落点 `execution_runs/T1-5/a20260920-01/` + `tests/test_model_extensions_anchor.py`。

**裁定**（`OWNER_DECISIONS.md` §13 **T1-5**，TIER-1）：**授权实施**（owner 职权内，属验收基准加固）；交由模型卡批次执行，**新增回归须独立 oracle、不得回改既有冻结件**。

> **本卡性质与前面九张不同**：T1-5 是**授权实施**（要真写代码），不是口径确认。故本卡的收口判据是**「已入库」**，不是「形态已在盘上」。

**⚠️ 发现并修正的一处「已完成」失真**：本轮核对时发现 task list 把 T1-5 记为 completed，但该交付物**从未入库、也从未记入本文件**：

| 检查 | 结果 |
|---|---|
| `git log -- tests/test_model_extensions_anchor.py` | **空**（无任何提交） |
| `grep T1-5 task_plan.md` | **空**（本文件从未提及） |
| 文件是否在盘上 | **在**（7378 B） |

⇒ **交付物是真的，但未落地 —— 一个没有历史的产物。** 本卡把它**入库**。

**回归为何是**这一条**（而非重复既有公式套件）**：`tests/test_model_extensions.py` **已经**证明**公式**及其经济不变量；它**没有**证明、而 20260920 生产树回滚**恰好摧毁**的，是扩展层**被挂载**这件事 —— ①八个 spec 真的**挂在产品所构建的那个 registry 上**；②`model_extensions.py` 作为**受版本控制的真实内容**存在；③`driver_bounds` 机制存活。**公式套件测不出「挂载丢失」**，因为**公式在孤立状态下照样通过**。

**六项检查**（`tests/test_model_extensions_anchor.py`，**6/6 OK**）：

1. 注册的恰是**命名的八个原型**（用**卡包冻结的身份清单**比对，不是回读 registry）；
2. 产品 registry（`MODEL_REGISTRY`）**含全部八个** —— **这正是回滚所移除的**；
3. registry 是 24 核心模型的**严格超集**（未替换任何东西）；
4. 每个扩展 spec **声明了开余额桥**（使存量/流量校验成为可能）；
5. `driver_bounds` 在**三个声明非默认域的 spec 上存活**；
6. `model_extensions.py` 作为**非空内容**存在，且 `model_registry.py` **仍指名挂载点**。

**独立 oracle**：八个模型名取自**卡包冻结的身份清单**，**不是**从被测 registry 回读；边界断言**由卡文推出**。**无任何期望值是由调用被测代码产生的。**

**变异臂（证明判据「有的放矢」）**：**「一个跑不绿的判据什么也保护不了」**，故**实测响应性**而非断言 —— 在**副本**上（`.tmp-t15-mutation`，已删除）复现**回滚本身**：把 `] + list(build_extension_specs(ModelSpec, ModelRegistryError)))` 换成 `])`，使 `MODEL_REGISTRY` **失去扩展挂载**。

- **结果**：**`FAILED (failures=8)`，exit 1** —— 八个模型**全部**报 `not found in MODEL_REGISTRY`。
- 第二变异（改挂载点符号名）⇒ **导入期失败**（`ImportError`，exit 1），证挂载点引用是**承载的**。
- ⇒ **回归对「本卡所命名的失效模式」确有响应。**

**既有套件未受扰动**：`tests.test_model_extensions` **26/26 OK**（新文件**新增**一套件，**未修改**既有文件）。

**新增教训**：**「任务已标完成」≠「交付物已落地」。** 工作树中的一个文件**没有历史** —— `git log -- <path>` 为空 + 文件在盘上 = **未落地的产物**。**收卡时必须核验交付物是「已提交」，不只是「在场」。**

**产物**：`tests/test_model_extensions_anchor.py`（**7378 B** / `954e08ac4ea19a6953da3c435f9028956d073acad06a5db4f253660c180524f9`）、`handoff.json`（**5344 B** / `b121244bce9c60c2974df8225f4270a68af10fba0b77d4114c239bb3f240179f`）。支撑哈希：`scripts/model_extensions.py`（`9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`）、`scripts/model_registry.py`（`9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`，**未变**）。**边界**：既有冻结件改动 **0**；既有测试改动 **0**；产品源码改动 **0**；期望值回读 **无**；status 转移 **0**。

**Round 56（2026-09-20）新增：T1-8 **前置项 ③** 卡内完成 —— rc 归类与「期望缺失」口径，**结论为「该统一要求所指的差异不成立；被要求做的统一对产品是 no-op」**（**未改任何 runner、未回改任何历史 rc、未改任何冻结证据**）。落点 `execution_runs/T1-8/a20260920-01/`：

**裁定**（`OWNER_DECISIONS.md` §13 **T1-8**，TIER-1）：**授权推广**跨批 runner 修复，按「建议」形态（**只改各批自己的副本**、`before/` 留旧版、**不回改历史 rc、不动冻结证据**、每批补「改 `expected` ⇒ rc=3」变异臂）。四项前置**须先满足**：①不退回 `isinstance`；②登记 schema 约束「`expected` 只能是裸类型名」；③**先修 rc 归类与「期望缺失」口径**；④逐批按 runner sha256 登记命名空间。**本卡只处理第 ③ 项，不执行推广。**

> **本卡性质**：既非口径确认、也非实施，而是**核验 + 事实更正**。第 ③ 项在盘上的唯一载体是 `execution_v2/START_HERE.md` 第 111–115 行（由 **T1-19** 追加节写入）。**本卡回答的就是那一句。**

**被检验的主张**（`START_HERE.md` 第 114–115 行原文）：「当前 `cases.json` 缺 `expected` 时的归类（**现为 `rc=3`**，而登记口径写 `rc=2`）须先按本表**统一到 `rc=2`**，再推广 runner。」

**结论**：**该句的前提有一条是错的，而它要求的处置是一个空操作。** 一个 `expected` **不可用**（缺键/非字符串/空串）的用例，在**每一个能触达该分支的 runner 世代里都已经是 `rc=2`**。`rc=3` 属于**在场但错误**的声明 —— **那是正确语义，且不得被「统一」成 rc=2**。

**六条命题（`scripts/verify_t8.py`，`overall = PASS` / exit 0）**：

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **P-1** | 「缺 `expected` ⇒ `rc=3`」在**任何一批**都不成立 | **holds** | `rc3_classification_observed = []`；能触达该分支的三族（M13–16 / M17–20 / M25–28）**全部归 rc=2** |
| **P-2** | **runner 代码里不存在**把「缺 `expected`」映到 rc=3 的路径 | **holds** | 68 份 runner 副本全扫；`paths_to_rc3_for_missing_expected = []` |
| **P-3** | rc 词表**按 runner sha256 分代**，每族都能按 sha 指名（T1-19 的要求） | **holds** | 八族 **八个不同 sha256**（`b5fcc685` / `fd3a11c9` / `997c553b` / `9e4a6450` / `94619a98` / `a5ee7599` / `eab01162` / `9ea69c72`） |
| **P-4** | 冻结证据**确实把**「声明不可用（无裁决 = rc=2）」与「声明在场但错误（判负 = rc=3）」**分开** | **holds** | 五项子检查全 True（见下） |
| **P-5** | 今天**没有任何** `cases.json` 省略 `expected`，故该分歧**从未在实际 rc 上兑现** | **holds** | 31 个 `cases.json` / 347 个负例 / **0 个缺键**；值类型 `{'str': 347}` |
| **P-6** | 「统一到 rc=2」对**产品代码**是 no-op，且本卡**未写任何东西** | **holds** | 产品文件改动 `[]`；生产锚点 `9ec65295…` **一致**；runner 编辑 **0** |

**P-4 是本卡的实质发现 —— 冻结自检里已有恰好这两条臂**：

```
M17 MISSING declaration   -> rc = 2   not_judged = ['N02']   mismatch = []       usable = False
M17 DIFFERENT declaration -> rc = 3   not_judged = []        mismatch = ['N02']  usable = True
M13 PRE-FIX declares-nothing-usable -> rc = 0     <- 修复前：完全看不见
M13 PRE-FIX shape-violated          -> rc = 0     <- 修复前：完全看不见
```

**为什么「不改」才是对的、而不是「也是对的」**：`rc=3` 的语义是「**判了，且没通过**」，`rc=2` 是「**判不了**」。把在场但错误的声明压到 rc=2，会**抹掉「判不了」与「判了没通过」的区别** —— 于是一个声明被篡改的卡会从「判负」降级为「无裁决」，即**篡改声明从「失败」变成「无法判定」**。**一个把「判负」读成「判不了」的口径，会让篡改比不篡改更容易通过。**

**「能触达该分支的只有三族」**：另外五族（M01–04 / M05–08 / M09–12 / M21–24 / M29–31）的 runner **把 `expected` 当下标读**（`case["expected"]`），缺键会抛 `KeyError` —— 它们**没有**「缺 `expected` 的归类」这回事，因此不可能给出 rc=3，也谈不上「统一」。

**本卡自行犯下并已修正的判据错误（如实登记于 `decision.md` §5 与 `handoff.json`）**：首跑 **P-4 FAIL，对象本身无缺陷** —— 我的判据断言 `m17_g.exit_code == m17_f.exit_code == 2`，注释写「两臂共享整数 2，只能靠词汇分开」；**实测 `m17_f.exit_code = 3`**。根因：**我从「词汇能分开」顺手推断出「整数相同」，没有先测量被比较的量就写下了比较运算**。修正：按实测重写，并把**被检验后被否决的读法**显式写进证据 JSON 的 `reading_that_was_tested_and_rejected`。⇒ **本项目第 13 次同源教训**（判据必须匹配被判定对象的形态），**新变体是「方向」而非「类型」**：不是量不可比，而是**我假设了相等**。**可分离 ≠ 同码。**

**为何本卡不执行「统一」、也不执行推广**：①**统一是空操作**（P-1/P-2/P-4/P-5 已证）—— 执行它**要么什么都不做，要么造成损害**；②**T1-8 仍是「授权推广」**，且前置 **①④ 尚未落实**（②的登记形态已由 `M17-M20/…/rc_namespace.json` 承载）；③**本卡不改任何 runner** —— 依 **T1-11**，改 `scripts/run_card.py` 须整体重跑重冻并记为新 rN，**非本卡授权范围**。

**⚠️ 移交编排层 / owner 的提示（本卡不做）**：
1. **`START_HERE.md` 第 111–115 行需一条追加式勘误**（**T1-12 ① 形态**）：「现为 `rc=3`」**不成立**；应更正为「缺 `expected`（不可用声明）**现为 `rc=2`**；`rc=3` 属**在场但错误**的声明，**系正确语义、不得统一**」，并补记**能触达该分支的只有三族**。**本卡未执行** —— T1-8 授权的是推广 runner，**不含**编辑 `START_HERE.md`。
2. **`rc_namespace.json` 的 `runner_sha256_by_batch` 有一处与实测不符**：`M21-M24` 记 `d02057de`（附注「已移至 `a5ee7599`」）⇒ 实测盘上为 **`a5ee7599c37e`**。**该表自述「NOT VERIFIED BY THIS BATCH」**，属**自认未经核验的声称**而非把未经核验说成实测；建议按 T1-12 ① 追加一行，**不回改原值**。
3. **`adjudicated_by` 仍写 `PENDING`** —— 按 **T1-21** 口径**不构成缺陷**（记录的是当时状态）。

**产物**：`scripts/verify_t8.py`（**19341 B** / `32a7baf01ec5523532ea74c85e7c028a0fde7dfd4bea44ff0b6f866e6743ae64`）、`t8_precondition3_rc_classification.json`（**19934 B** / `f2253b3566b86cb40205092427ca84996d780bf76f97289e5221dcf880d10f65`）、`decision.md`（**9464 B** / `1e183e9bc91c0e723badb7eaf7ad64c0577c3fe0be0859a16de50520e04c2644`）、`handoff.json`（**7867 B** / `c00d4a9b9dd3b5a709cf805d1b62b25ea7a4dad198ca2f169588bc023bf1b34d`）。**边界**：runner 编辑 **0**；**回改历史 rc 0**；冻结证据写入 **0**；`START_HERE.md` 写入 **0**；`rc_namespace.json` 写入 **0**；产品文件 **0 条**；生产锚点 `9ec6529550f189a4…` **一致**；`status` 转移 **0**；代签 **0**；全部 JSON 可解析且登记哈希 **3/3 MATCH**。

> **`handoff.json` 不登记自身哈希（自指）**；其 sha256 只记于本文件与 memory。

---

## Round 57（2026-09-20）新增：T1-10 卡内完成 —— `natural_window.py` 两个产品级缺陷，**结论为「②早已修好且追加式 provenance 已按裁定落地；①的枚举校验已加但**不是全函数**，留下一个**未闭合的残留**」**（**未改任何冻结件、未建生产文件、未做删除**）。落点 `execution_runs/T1-10/a20260920-01/`

**裁定**（`OWNER_DECISIONS.md` §13 **T1-10**）：**授权立卡修复**（产品 + 计划双侧）①`claim.basis` 补**枚举校验**；②修正 `union_of_windows`/`sum_of_windows` 把 quick_check 计入自然观察时长。**②已烧进冻结期望**（W1 `union_seconds=2220`）⇒ 修复须同时以**追加式 provenance** 更正期望，**不得回改冻结正文**。

**先厘清一件事：这是「产品级缺陷」，但不是「生产树里的文件」**。全仓（排除 `.planning/`）**不存在** `natural_window.py`；唯一实例是被测件 `I-14-B/a20260919-01/iso/natural_window.py`，且 **I-14-B 的 D-6 明写该产物刻意不进入生产树**。⇒「产品级」指**产品级形态的缺陷**（该分类器若晋升进生产树会带走的缺陷），**不是**"某个生产文件里的缺陷"。故本卡**不创建、不修改任何生产文件**；按 **T1-9**，**晋升进生产树**属另一张卡、当前无授权。

**缺陷 ② —— 早已修好（P-1 PASS）**。被测件 sha256 = `7fff6f0c1e8ab2…`（= I-14-B 记录的 r2 修订；该轮为回应独立 reviewer 的 `changes_required`，已由该 reviewer **`accepted_scoped`** 结案，P1/P2 两个阻断项确认闭合）。②在代码里的落点：观察区间**只由观察阶段**构成、quick_check **永不进入**（`iso/natural_window.py:174-185`），并另加 **J15** 拒「把 quick_check 改名成第二个窗」的变体（`R-QC-IN-OBS`）。裁定要求的「追加式更正、不回改正文」**盘上已经是这个形态**：

| 要素 | 实测 |
|---|---|
| 新值 | `expected.W1.computed.union_seconds = 1740` |
| 旧值**保留** | `expected_superseded["W1"][…]["old"] = 2220`（**正是裁定引用的数**） |
| 前像 | `pre_image_sha256 = 3ba2bb17…`；r1 期望在 `harness/archive/` **逐字节可读** |
| 勘误条目 | `errata[0] = ERR-I14B-R2-01`，含 r1→r2 期望的**机械 unified diff**（182 行） |
| r1 原位文件 | `oracle.md`/`cases.json` **未被覆盖**；17 个 r1 文件全量归档 |

⇒ **②不存在未完成项**；本卡只确认并登记，**不得重复"修"**。

**缺陷 ① —— 枚举校验已加，但非全函数（P-2 PASS / P-3–P-6 暴露完全性缺口）**。盘上确已有 `BASIS_REGISTRY = {…}`（**set**）+ `if basis not in BASIS_REGISTRY: refusals.append("R-BASIS-UNKNOWN")`（`:60` / `:202`）。**标量域上工作**：`'wall_clock'`/`''`/`None`/`5`（非串标量）**全部** `reject_claim` + `R-BASIS-UNKNOWN`；登记值 `accept_claim`。**容器域上崩塌**——`set` 成员测试对**不可哈希**值**抛异常**：

| 探针 | `basis` 类型 | rc | 报告 | 结果 |
|---|---|---:|---|---|
| `registered_str` | `str` | 0 | 有 | `accept_claim` |
| `unregistered_str` / `empty_str` / `null` / `scalar_non_str` | `str`/`null`/`int` | 0 | 有 | `reject_claim` / `R-BASIS-UNKNOWN` |
| **`list_of_registered`** | **`list`** | **4** | **无** | `internal_error: unhashable type: 'list'` |
| **`dict_object`** | **`dict`** | **4** | **无** | `internal_error: unhashable type: 'dict'` |

`main()` 的异常处理器把整个进程变成 **rc=4 且不写任何报告**（`:468-473`）。

**危害形态：这是「剥夺裁决」，不是「拒绝主张」（P-4/P-6）**。`R-BASIS-UNKNOWN` 是**对该 case 判负**；rc=4 是**对该 case 判不了**——且**连带把同批所有 case 一起判不了**。实测爆炸半径：

| 臂 | 批次 | rc | 已裁决 | 连带未裁决 |
|---|---|---:|---:|---:|
| **A** 12 良构 + 1 个 `basis=[list]` | 13 | **4** | **0** | **13** |
| **B** 12 良构 + 1 个 `basis='wall_clock'`（串） | 13 | 0 | 13 | **0** |
| **C** 1 calendar + 6 window 良构 + 1 个 `basis={dict}` | 8 | **4** | **0** | **8** |

**对照臂 B** 证明：爆炸半径属于**值的形态**（容器），**不属于「被拒绝」本身**。**臂 C** 证明伤害**跨 class**——一个 `window_accounting` case 的容器 `basis` 会把**与之无关的 `calendar` case** 一起打成「判不了」。**J16 存在的全部理由就是「把 `basis` 输入域锁死在封闭枚举内」，而恰在输入域最坏一侧（结构错误的 `basis`），J16 不开火，而是把整个裁决机关炸掉** ⇒ 护栏本身成了**单点故障**（SKILL 陷阱 13「护栏要致命不要误报」的反面：**一个畸形用例可以让整批合规用例无法被验收**）。

**该缺口已由 reviewer 登记但从未闭合（P-8）**：`review.md`「新增发现」**P4**（标注**非阻断**）已记同一现象并给最小修法（`set` 改 `tuple`，或 J16 前加 `isinstance(basis, str)` 守卫；并在 oracle §11 明确「字段类型错误」属 schema 级 rc 2 还是 per-case 拒绝）。**实测**：`oracle.md` §11 **未回答**该问题（`字段类型`/`unhashable`/`rc 4`/`internal_error`/`isinstance` 五词**全部缺席**）；`BASIS_REGISTRY` 至今**仍是 `set`**。⇒ 残留是**reviewer 已指出、实现者未采纳、oracle 未定口径**的**敞口**。

**今天打不到，但正是 J16 管的那个面（P-7）**：31 个负例（`cases.r2.json` + `cases.json`）中 **0 个** `basis` 是容器类型 ⇒ 残留**潜伏**。**但不构成「可以不管」**：`cases.json` 是**输入**，J16 的**职责**就是**管输入域**。「今天恰好没人这么写」是**样例覆盖**论证，不是**全函数性**论证。

**F 段附带发现（P-9/P-10，新增、非阻断、不改任何值）**：复算 I-14-B 记录的 7 个关键哈希，**5 个逐字节可复算，2 个不行**：

| 文件 | 记录值 | 盘上（= HEAD blob） | 复算条件 |
|---|---|---|---|
| `harness/frozen_expectations.r2.json` | `6f814d0a…` | `a24d8ab3…` | **仅 `LF→CRLF` 变换后**才等于记录值 |
| `harness/cases.r2.json` | `c00a3a00…` | `23d89fb2…` | **仅 `LF→CRLF` 变换后**才等于记录值 |
| 其余 5 个（r1 期望 / `cases.json` / `oracle.md` / SUT / `run_cases.py`） | — | 同记录值 | **原样** ✅ |

**根因**：本仓 `core.autocrlf = true`。那两个文件是 **r2 轮新建**的，sha256 在 **CRLF 工作副本**上算得并写进 `binding.json`/`commands.json`/`handoff.json`；**提交进 git 的 blob 是 LF**。⇒ 记录值**不是提交字节的 sha256**，而是**另一个字节域**的。**关键限定**：HEAD blob 与盘上文件**同**为 `a24d8ab3…` ⇒ **内容自提交以来未变**；坏的**不是内容**，是**「哈希取在哪个字节域上」没写明**。⇒ **本项目第 6 次同源教训重演**（判据须匹配被比对量的形态；这里"比对面"是**行尾规范化前/后**），**且恰好命中 T1-13 的同一条**。

**本卡没有做的事**：改 `iso/natural_window.py`（是 r2 冻结件、其 hash 被 5 处 evidence 引用；改它须**整体重跑重冻记为新 rN**，同 **T1-11** 互锁对纪律——T1-10 授权的是"立卡修复"，本卡性质是核验）；建生产 `natural_window.py`（D-6 明禁 + T1-9 未授权）；改 `oracle.md` §11（T1-12 ① 属编排层）；改 CRLF 哈希（冻结件，按 T1-12 ① 追加式登记，不回改原值）；任何 `status` 转移。

**⚠️ 移交编排层（本卡不做）**：
1. **①的残留**：授权一张**继承 I-14-B r2** 的新修订卡，把成员测试改为**对容器安全**的写法（reviewer 已给最小修法），**并同时**在 `oracle.md` §11 追加**「字段类型错误属 schema 级 rc 2 还是 per-case 拒绝」**的裁定 —— **该口径属专业判断，须由该卡 reviewer 出具，不可由实现者自填**（同 T1-24/T1-21 纪律）。
2. **F 段哈希域缺口**：按 **T1-12 ①** 在 I-14-B 的 `binding.json`/`commands.json`/`handoff.json` **追加**一行，写明「`cases.r2.json` 与 `frozen_expectations.r2.json` 的记录 sha256 取自 **CRLF 工作副本**；提交 blob 为 LF，其 sha256 分别为 `23d89fb2…`/`a24d8ab3…`」。**不回改原值。**
3. **②** 无需移交：已由 I-14-B r2 自轮闭合并经 reviewer `accepted_scoped`。

**本卡自身的过程披露（如实）**：①`verify_t1_10.py` 首跑 `TypeError: window_case() missing 1 required positional argument: 'basis'` —— **我自己的脚本 bug**（良构臂省略了该参数而参数无默认值）；已修，**未污染证据**。②证据文件**首版非幂等**（三次运行三个哈希）—— 根因：捕获的 stdout 回显了**随机 temp 目录**的报告路径；**两轮修正**（弃记 temp 路径 → 仅替换字面路径**不够**，因 stdout 是 **JSON 编码**过的、反斜杠**已加倍**，且 `mkdtemp` 后缀可能含 `_`，故改为**按 `t1_10_<随机>` 形状正则脱敏**）；**终态连跑 4 次同哈希**。⇒ **又一次同族教训**：**「我替换了那个路径」≠「那个路径不再出现」——编码后的形态是另一个被比对面**（与 F 段 CRLF 缺口**同源**）。③幂等调试遗留的 `run_a.json`/`run_b.json` **原样保留**（用户明令不删），**非本卡交付物、handoff 不登记**，由编排层决定去留。

**产物**：`scripts/verify_t1_10.py`（**24335 B** / `544ae0adb3a969209eee5ab5ddbdb781a63a5a6a2b615d8025386b22223ab983`）、`t1_10_defect_verification.json`（**12763 B** / `22ead5c549311acea517bdf9819fcf97ad04c24c48edfb82cfc5451cabcb413c`）、`decision.md`（**14031 B** / `d7fe3ebb8dcc6868…`）、`handoff.json`（**12934 B** / `cb18c036e85af238abf30cf682a7b94173172752c489f6fbd339ea6f595515ec`）。**边界**：产品文件 **0 条**；生产锚点 `9ec6529550f189a4…` / `9939480b717d5a49…` **一致**；**被核验件写入 0 次**（SUT/`cases*.json`/`frozen_expectations.*`/`oracle.md`/`review.md`/`run_cases.py`/`binding.json`/`commands.json`/`handoff.json` 全只读）；**删除 0 次**；`status` 转移 **0**；代签 **0**；**十命题全 PASS**（`overall = PASS` / exit 0）；两 JSON 可解析；登记哈希 **3/3 MATCH**。

> **`handoff.json` 不登记自身哈希（自指）**；其 sha256 只记于本文件与 memory。

**Round 57 补记（**追加**，不改上文）**：上述证据在落笔后**新增一个交付件**并**重生成了 `handoff.json`**（因原 handoff 未登记该件），故**两个哈希以上文为准需更正**：`handoff.json` 现为 **12934 → 13086 B**、sha256 **`cb18c036e85af238abf30cf682a7b94173172752c489f6fbd339ea6f595515ec` → `ed206347b00b86d96629e917a2c33f8054f9e323accc40f2d2d2ab0934501306`**。新增件 `append_only_proof_round57.json`（**676 B** / `fb7bf6a0a8e9e602…`，**完整 sha256 见 `handoff.json` 的 `artefacts` 表**）是本次 `task_plan.md` 追加的**机械证明**：以 HEAD blob（`e76138cb…`，与登记的**前像常量一致**）为基准，`prefix_bytes_preserved = True`、opcodes = `['equal','insert']`、**`deleted_chars = 0`**、`inserted_chars = 6436` ⇒ **`APPEND_ONLY = True`**。`verify_t1_10.py` / `t1_10_defect_verification.json` / `decision.md` 三者哈希**未变**（与上文一致）。**handoff.json 自身哈希仍不登记（自指）**。

**Round 57 再补记（**追加**，上文补记里的两个**字节数**我写错了，以此处为准）**：`handoff.json` 实测 **13153 B**（不是 13086 B），sha256 `ed206347b00b86d96629e917a2c33f8054f9e323accc40f2d2d2ab0934501306`（**该值上文写对了**）。`append_only_proof_round57.json` 实测 **676 B**（上文写对），sha256 **`fb7bf6a0a8e9e602d89abbffa8d2116e4f2391cdaa82c18c3b02345dcb9918a4`**。**记录哈希一律以 `handoff.json` 的 `artefacts` 表为权威**（该表在写盘后逐条回读复算，**4/4 MATCH**）；本文件的散文数字仅为提示，**不得用作比对依据**。⇒ 又一次同族提醒：**字节数这类"我顺手写下的数字"必须先量再写**（本项目第 13/14 次同源教训的轻量变体）。

---

## Round 58 — T1-8 前置 ① / ④：把「不退回 `isinstance`」变成一个**可判定谓词**，并逐代按 sha256 登记

**卡**：`execution_runs/T1-8/a20260920-02`（承接 `a20260920-01` 的前置③）。**权限**：`OWNER_DECISIONS.md` §13 **T1-8**（TIER-1）。**性质**：**核验 + 事实登记**，**不执行推广**。

### 前置①的问题：「不退回 `isinstance`」**字面上没说它禁止什么**

一条禁令只有在其**被禁止的属性可被检出**时才有约束力。本卡先把它变成可判定的谓词：

> **`PASS_rejected` 是由 `isinstance(exc, ModelRegistryError)` 单独决定的，还是受「异常**精确类型名**」等式约束的？**

**判据不是「有没有调用 `isinstance`」** —— 八代全部调用它（用于 `FAIL_wrong_exception_type` vs `FAIL_import_or_file_error` 的分流）。**禁用形态**的精确文本是那个三元式：`"PASS_rejected" if is_target else (...)`，即 **`PASS_rejected ⟺ is_target`**。

### 结论：**八代中五代是禁用形态**（八代**八个不同 sha256** ⇒ 正合前置④的登记形态）

| 批次族 | runner sha256（前 12） | 类型**名**等式 | `PASS_rejected` 由 `isinstance` **单独**决定 |
|---|---|---|---|
| **M01-M04** | `b5fcc68563f5` | — | **是（禁用）** |
| **M05-M08** | `fd3a11c9226a` | — | **是（禁用）** |
| M09-M12 | `997c553b0b9e` | `raised_matches_expected_name` | 否 |
| **M13-M16** | `9e4a6450d6ab` | — | **是（禁用）** |
| M17-M20 | `94619a98f576` | `declared_ok = raised_name == declared` | 否 |
| M21-M24 | `a5ee7599c37e` | `expected_type_matches_raised` | 否 |
| **M25-M28** | `eab0116220df` | — | **是（禁用）** |
| **M29-M31** | `9ea69c72dced` | — | **是（禁用）** |

⇒ **①经本卡核验后是「可判定」而非「已满足」**：**五代仍处禁用形态**，故**推广仍不得先行**。**④的登记表**（上表）已由本卡给出；`rc_namespace.json` 的**写入属编排层**。

### 谓词分叉的**方向** —— 本卡必须先纠正我自己的一个错误判据

**首版 MRO 探针结论是「无分叉」，而那个结论是错的。** 它按**声明名**构造异常（对 `ValueError`/`TypeError`/`KeyError` 各自取其**自身**），再比较两谓词 —— 而那是一个**两谓词必然一致**的域。**分叉是单侧的，且落在目标的「子孙」一侧**：

| 形态 | 精确类型名 | `isinstance` | 名等式 | 分叉 |
|---|---|---|---|---|
| 目标自身 | `ModelRegistryError` | True | True | 否 |
| **目标的子类** | `SubclassOfTarget` | **True** | **False** | **是** |
| 目标基类下的兄弟 | `SiblingUnderBase` | False | False | 否 |
| 目标基类自身 | `ValueError` | False | False | 否 |

目标 MRO = `ModelRegistryError → ValueError → Exception → BaseException → object`。⇒ **`isinstance` 向「目标的子孙」放宽，不向 `ValueError` 放宽**。**直接后果**：那 4 个 declared=`ValueError` 在 `isinstance` 判据下**也会被正确拒绝** ⇒ **「声明的 `ValueError` 会假过」这个直觉说法不成立**；真正会假过的是**类型名不是目标名、但它是目标子类**的异常。

⇒ **本项目第 16 次同源教训**：**判据的「方向」也要匹配对象** —— 本次错不在量、不在面、不在域，而在**我把「放宽的方向」搞反了**。已写入 skill 陷阱 16。

### 冻结证据**已经实例化过**这个区分（关键发现）

全域 **147** 个 `cases.json` 中，仅 **8 个异构**（`expected` 取值分布：`ModelRegistryError:1620 / None:20 / TypeError:4 / ValueError:4`）：

```
M09…M12 /recovery/selfcheck/B/evidence/M09/cases.json     {'TypeError': 1, 'ModelRegistryError': 10}
M25…M28 /recovery/selfcheck/cases/F1/evidence/M25/cases.json  {'ValueError': 1, 'ModelRegistryError': 10}
```

`M09` 的**五臂是一套完整变异对照**（**五臂全部**由 `997c553b` 执行）：

| 臂 | `NEG-CARD.expected` | 变异 | 实测 rc |
|---|---|---|---|
| A | `ModelRegistryError` | oracle 正例期望值 → `[999.0]` | **2**（no_verdict_fidelity） |
| **B** | **`TypeError`** | **声明改写为非目标名** | **3**（`FAIL_wrong_exception_type`） |
| C | `ModelRegistryError` | 变异值 → `0`（不再被拒） | **3**（`FAIL_not_rejected`） |
| D | `ModelRegistryError` | 正例期望缺失 | **2** |
| **E** | `ModelRegistryError` | **无变异（对照）** | **0**（`pass`） |

**B 臂的关键三元组**（`run_result.json` 实读）：`expected='TypeError'` / `raised='ModelRegistryError'` / **`is_target_type=True` 而 `raised_matches_expected_name=False`** ⇒ **两谓词在一次真实冻结运行上分叉，且只有名等式能把它判负**。`E` 为**未变异对照** ⇒ 差异**归因于声明改写**，非环境。

> **该臂独立于 T1-8 的价值**：B 是一次真实运行，其中**冻结声明与被拒异常不一致**，而**产品确实被该 case 所指的护栏正确拒绝**。**一个 `isinstance`-only 的 runner 会把同一次运行记为 PASS** —— 这正是前置①要防的盲区。

### 推广要求与实测**直接冲突**（移交裁定层，本卡不解决）

裁定要求「**每批补「改 `expected` ⇒ rc=3」变异臂**」。但 `M25-M28` 是**唯一**带 `case_contract` 的一代：

```
"declared_expected_exception": "ModelRegistryError",
"rule": "every case's `expected` must equal declared_expected_exception ... otherwise
         the harness refuses to issue a verdict (rc=1)"
```

**F1 臂实测**：把 `expected` 改成 `'ValueError'` ⇒ **`raw_rc = 1`**（`harness_error=True`，`frozen case contract violated`），**不是 rc=3**。⇒ **该字面要求在装了契约闸门的批次上不可满足**；照抄进 `M25-M28` 会写下**与实测相反的期望值**（把 rc=1 记成 rc=3），即在推广里**植入一个假期望**。**须由裁定方出具澄清**（T1-24/T1-21 纪律）。这也**再次印证前置④**：**「声明被改写」在各代映射到的 rc 并不唯一，不得按整数跨批聚合**。

### 移交编排层（本卡不做）

1. **`task_plan.md` 的 T1-8 段需一条追加式更正**：此前记「前置 ①④ 仍未落实」；**更精确的形态**是「**④ 的登记表已由本卡 §3 给出（8 代 / 8 个 sha256）**；**① 的判定结果是「五代禁用、三代合规」**」。按 **T1-12 ①** 追加，**不回改正文**。
2. **裁定层须澄清变异臂的字面要求**（见上），建议改为「**每批补一条『声明被改写 ⇒ 失败』的臂，其具体 rc 按该代契约为准**」（M25-M28 → 1，M09-M12 → 3）。
3. **`rc_namespace.json` 建议按 T1-12 ① 追加两列**（不回改原值）：`pass_rejected_predicate`（`isinstance-only` / `name-equality`）与 `case_contract_present`（`yes` / `no`）。
4. **前置②的语义可能与 `M25-M28` 的契约重叠**：契约要求 `expected` **必须等于** `declared_expected_exception`，比「只是裸类型名」**更强** ⇒ 前置②的登记形态或需与之对齐（**属裁定层**）。

### 产物

| 产物 | 字节 | sha256 |
|---|---|---|
| `scripts/verify_t8_pre1.py` | **26146** | `23213d948047c80dc349d3624d84bb8c49bb42c575fa42f33ae2cd64e9c80ddf` |
| `t8_pre1_pre4_verification.json` | **16057** | `5fb6e414b57a649b9a7754e56d035dc324f67986b5ce3f413d48fe1933a51697` |
| `decision.md` | **14660** | `f6153120cf0caf0eb2c42a397542aec7a454a4f580ff99d09b0804363fb65f68` |
| `handoff.json` | **12221** | `4933d892a28a9da4986fb0f47d4b53eb3675c2b01e3765b322055cd82ddeeb34`（**不登记自身哈希，自指**） |

**幂等性**：证据 JSON **连跑 4 次同哈希**；内含**无环境取值**（无 temp 路径 / 时间戳 / 随机名），全为常量、哈希或**从冻结证据读出**的值。

**边界**：runner 编辑 **0**；**回改历史 rc 0**；冻结证据写入 **0**；`START_HERE.md` 写入 **0**；`rc_namespace.json` 写入 **0**；**产品文件 0 条**；生产锚点 `scripts/model_registry.py` = `9ec6529550f189a4…` **一致**；`status` 转移 **0**；**代签 0**；**删除 0**。**六命题全 `holds`，`overall = PASS`**；登记哈希 **3/3 MATCH**。

**本卡自身的过程披露（如实）**：①`verify_t8_pre1.py` **首跑被自己的 FATAL 护栏拦下** —— `FATAL: wrong plan dir: …\.planning`（我把 `PLAN` 少算了一层：card 的 parent 才是 `execution_runs`）。**这正是陷阱 13「护栏要致命不要误报」的正面案例**，**未污染任何证据**。②MRO 探针首版**在同谓词域上比较**，得出错误的「无分叉」，已在 §4 如实登记并改在**目标子类**上重测。③未跟踪的 `.tmp-r41-mutation/` 系**本轮之前** T1-5 遗留（mtime Sep 20 18:31，`git log --all` 为空），**本轮未触碰、未删除**，已在 handoff 中登记以免被误认为本卡产物。

> **⚠️ 关于 `handoff.json` 的字节数与哈希**：以 `task_plan.md` 上文与 `handoff.json` 的 `artefacts` 表为准（写盘后逐条回读复算）。本段任何数字均为提示，**不得用作比对依据**。

---

## Round 59 — T1-8 续查：裁定所列「不推广的代价」**与实测不符**，且**低估**了缺陷

**卡**：`execution_runs/T1-8/a20260920-03`（承接 `a20260920-02`）。**权限**：`OWNER_DECISIONS.md` **§7 第 2 项** + **§13 T1-8**（TIER-1）。**性质**：**核验 + 事实对账**，**不执行推广**（**加补，不修订** `a20260920-02`）。

### 为什么要查这一句

上一卡把前置①的**判据**做成可判定谓词并给出**结果**，但**没核对推广决策真正依赖的一件事**：裁定用「**不推广的代价**」来正当化推广，而该代价**是以实测结果的形式写下的**：

> §7 第 2 项：**不推广的代价**：M05–M16 / M21–M31 各批的"逐例拒绝语义"仍无自动门（**改 `expected` 后仍 rc=0**，四批 reviewer 各自独立命中）。

**关于结果的断言，只有在其所指结果确实是发生的那个结果时才可用。**

### 结论：括注**为假**，且**假在「低估缺陷」的方向**

**在 `isinstance`-only 的代上，把全部 11 条声明都投毒成 `"ImportError"` 之后，runner 仍是 `rc=0` / `verdict=pass` / **11/11 `PASS_rejected`**。**

而**精确名判据下同一输入是 rc=3**（因为 `type(exc).__name__ == "ImportError"` 对每条 case 都为 `False`）。

⇒ **判决不是「没有门开火」，而是「门开火了 11 次、每次都把拒绝判成了正确」，于是整批报出一个干净的 pass。** 记下的 `rc=0` 是**一个被伪造出来的绿**的症状，**不是缺失检查**的症状。

**对推广的直接后果**：裁定所开的变异臂（「改 `expected` ⇒ rc=3」）若装到这些代上，**观察到的仍会是 `rc=0` / `PASS_rejected`，因而仍然失败**。把当前行为读成「仍 rc=0」，会诱出「门只是缺了」这一结论 —— 而**观测数字**在**一个糟得多的成因**下是同一个。

### 反事实（同一份投毒输入的两种判据）

```
场景：11 条 case 全部声明 'ImportError'，而产品抛的是目标异常
  出厂判据（isinstance）    通过 11/11  ->  verdict = pass   （实测 rc=0）
  精确名判据（== 类型名）    通过  0/11  ->  verdict = fail   （应为 rc=3）
```

⇒ **同一输入、同一产品行为，两个判据给出相反判决。** 这正是前置①所防的盲区，**本卡第一次把它量化**。

### 证据：三卡 reviewer 各自独立命中，且代由 JSON 复算

`execution_runs/M29|M30|M31/a20260919-01/review.md` 的 **P2 节**：

> **M29**：P2：`run_card.py` **从不比较** `cases.json[*].expected`。我把 NEG-CARD 的 `expected` 改成 `"ValueError"`、改成 `42`、把全部 11 条改成 `"ImportError"` 后重跑，三卡仍 **rc=0 pass**。负例判定只看 `isinstance(exc, ModelRegistryError)`。……（对照反例：补丁改 no-op → rc=3 `FAIL_not_rejected`；篡改 `oracle.json` 正例 → rc=3）

**M30 / M31 各自独立记录同一现象**（措辞不同）。**三卡实跑的 runner 由 `mutation_selfcheck.json` 复算**（不采信散文）：三卡**同为 `9ea69c72dced4158`**、六臂 rc 皆为 `[3,0,3,2,1,0]`，与上一卡分类表一致（**禁用形态**）。`M29/scripts/run_card.py` 复核：`isinstance-only = True`、`name-equality = False`。**该代自己的 `mutation_selfcheck.json` 不含「改 `expected`」臂** —— 那条实验**只存在于 reviewer 散文里**。

### 交叉验证（本卡的价值所在）

**缺陷命中集合与禁用形态集合吻合**：本卡**从 reviewer 散文**推得该代缺逐例绑定，上一卡**从代码文本**推得同一结论 ⇒ **两条独立路径同结论**，且**第二条路径从未读过分类结论**。

### 附加发现：15 张卡**有**正控制，3 张卡**没有**

为把「缺陷命中」与干扰项分开，本卡**三次修正匹配判据**（见下），最终得：

- **缺陷命中（改写后仍绿）：3 张卡** —— **M29 / M30 / M31**（同属 `9ea69c72`，禁用形态）
- **正控制（改写后正确转红 rc=3）：15 张卡** —— M13–M20、M22–M28
- **规则复述（既非实验也非命中）：10 个文件**

**裁定的「四批」**：实测缺陷命中 **3 张卡**，裁定**多算一处**；**以实测为准**，但该差异**不影响实质**（不推广确实有代价）。

### 本卡自行犯下并已修正的判据错误（三次，如实登记）

| # | 判据 | 结果 | 错在哪 | 修正 |
|---|---|---|---|---|
| 1 | 含「改成…」且含 `ImportError` | **24 个文件** | **过松**：每张卡都复述「`PASS_rejected` 要求 `isinstance`、`ImportError` 记为 FAIL」，被当成命中 | 加「必须含绿结局」 |
| 2 | 同上，要求**单空格**跨越 | **0 个文件** | **过紧**：报告**在句中硬换行**，单空格锚点**跨不过换行** | **先归一化空白** |
| 3 | 只要「改成…绿」 | **4 个文件** | **误报**：把 `M22` 的**正控制**（改写→**rc=3**）算成命中 —— 读到了**后文另一从句**的 `rc=0` | 结局 token 必须**附着于改写**，**转红即排除** |

⇒ **一般式（本项目第 17 次同源）**：**「匹配一段散文」的判据，难点不在关键字，而在「关键字的管辖范围」** —— 同一个 `rc=0` 可能属于**另一个从句**；同一句话在**硬换行**下不再是一句话。**判据的「管辖范围」（scope）也是对象形态的一部分**：第 6 次错在**面**、第 16 次错在**方向**、本次错在**范围**。已写入 skill 陷阱 17。

**正面做法**：先归一化空白；把**结论 token 绑定到其真正的主语**；再用**反向样本**（正控制、规则复述）做**误报测试** —— 本例正是 **M22** 这个反向样本暴露了第 3 版判据。

### 移交

1. **§7 第 2 项的括注需一条追加式更正**（**T1-12 ①**，不回改正文）：把「改 `expected` 后仍 rc=0」更正为「**仍 `rc=0` 且 `verdict=pass`、11/11 `PASS_rejected`** —— 即**拒绝逐条开火且被逐条判为正确**，属**伪造的绿**，不是缺失的门」；并建议把「四批 reviewer」更正为「**三张卡（M29/M30/M31）**」。
2. **推广的变异臂验收判据须改写**：不能以「观察到 rc=0」验收，须以「**观察到 rc=3**」验收 —— 在禁用形态的批次上，**装臂后必须转红，否则臂本身没生效**。该请求与 `a20260920-02` §8.2 **是同一件事的两面**，建议**合并出具**。
3. **`M29/M30/M31` 的 `mutation_selfcheck.json` 不含「改 `expected`」臂**（现有六臂 A/B0/B/C/D/E）⇒ 若推广要求每批补该臂，三卡**需补**；建议**待裁定澄清后由批次自己补**。

### 产物

| 产物 | 字节 | sha256 |
|---|---|---|
| `scripts/verify_t8_pre3.py` | **20904** | `0c23dc9cb4c35b7be8b0483429a240252d13ce197be18c6b4c386f219b28840d` |
| `t8_pre3_cost_reconciliation.json` | **14693** | `fe77d938068707d5726a13bfbf3cca5c28d7c5dd4ada75251239a150624cc8be` |
| `decision.md` | **9103** | `c10078856b1c0367023ca0d8c11c1ed3719b6e1760996a2dfb3d6299083ae6d1` |
| `handoff.json` | **10366** | `6ac4fdd87435a3dd56e48400bb34d1af9409ceccb06450337af8174a61d5e795`（**不登记自身哈希，自指**） |

**幂等性**：证据 JSON **连跑 4 次同哈希**（`fe77d938…`）；内含**无环境取值**。

**边界**：runner 编辑 **0**；**`review.md` 写入 0**（只读）；冻结证据写入 **0**；**回改历史 rc 0**；`status` 转移 **0**；**代签 0**；**删除 0**；**产品文件 0 条**；生产锚点 `scripts/model_registry.py` = `9ec6529550f189a4…` **一致**；**六命题 `overall = PASS`**；登记哈希 **3/3 MATCH**。

**过程披露（如实）**：①匹配判据**三次修正**（24 → 0 → 4 → 3），前两版分别是**过松**与**过紧**，第三版被 `M22` 这个**反向样本**证伪；全部如实登记于 §5 与 handoff 的 `matcher_revisions`（**这是本卡的方法论核心，不是附带的调试痕迹**）。②未跟踪的 `.tmp-r41-mutation/` 系**本轮之前** T1-5 遗留，**未触碰、未删除**。

---

### Round 59 收口补记：追加式证明（含上一轮遗留缺陷的当场修正）

**Round 59 后像**：`task_plan.md` 追加本段**之前**为 **141422 B**，sha256
`e9d29a90e50234c4297d128729b6736fcf04e20647d3dc62fa9e22878bf051b1`（= Round 59 正段的后像，
= 本轮追加的**前像**）。本补记追加后另行登记新后像。

#### 追加式证明（`execution_runs/T1-8/a20260920-03/append_only_proof_round59.json`）

| 字段 | 值 |
|---|---|
| `APPEND_ONLY` | **true** |
| `pre_image_bytes` / `pre_image_sha256` | `133308` / `f4dbd83b8a24d1a57e1158e9c9483fafa1a698ae449fd91dbcc47b767ad254b4` |
| `post_image_bytes` / `post_image_sha256` | `141422` / `e9d29a90e50234c4297d128729b6736fcf04e20647d3dc62fa9e22878bf051b1` |
| route 1（difflib） | opcodes `['equal','insert']`、`deleted_chars=0`、`inserted_chars=4600` |
| route 2（裸前缀） | `common_prefix_bytes=133308` == `len(前像)` |
| `pre_image_constant_reproduced` | **true** |
| 幂等性 | 连跑同哈希 `0a89e8ee39e31f50f54ff649d19c2aa6a52ff24078ab4d2f4f117cabd793f080` |

⇒ **两路独立一致**：**`APPEND_ONLY = True`**。

#### 当场修正的上一轮遗留缺陷（`a20260920-02` 的证明脚本）

**事实**：**已提交**的 `a20260920-02/append_only_proof_round58.json` 在磁盘上**被改写成了 Round 59 的数据**。
**根因**：上一轮脚本 `verify_append_only_round58.py` **把自己的输出路径硬编码成 Round 58 的文件名**，
故为 Round 59 **复用它时便就地覆盖了 Round 58 的已提交证据**。
**性质**：**「回改冻结证据」（误伤，后果与有意回改相同）**。
**上一轮的解释需订正**：我上轮把 `pre_image_constant_reproduced = false` 解释为
「预期行为、不是缺陷」—— 该**结论侥幸正确（追加性确实未受损）**，但**归因不完整**：
**真正的缺陷是「该文件本不该被覆盖」**，而不只是「常量该更新」。

**处置（追加式，删除 0）**：
1. **恢复** `append_only_proof_round58.json` 为 **HEAD 原像**（取自 `git show HEAD:…`，**不用 `git checkout --`**）；
   核验：`git diff` **为空**，sha256 = `26d811612d0d748ca70ef73829c5af547d1dadc0d9ae11bfafe4e47812dce842`。
2. **新建** `a20260920-03/append_only_proof_round59.json`，**置于本卡目录内**，与 Round 58 **两不干涉**。
3. **参数化脚本**为 `.planning/_pwf_tmp/verify_append_only.py`（`--round` / `--out` / `--attempt` /
   `--expect-bytes` / `--expect-sha256` 全为参数；默认输出路径**按轮次命名**；未提供常量时**记 `null` 而非报假 false**）。
4. **原脚本保留未删**（遵用户「不做删除操作」）。

#### 新护栏自身犯的错（本项目**第 18 次同源**，如实登记）

为防缺陷再现，我在参数化脚本中加了**跨轮覆盖护栏**（`--out` 既有文件不属本轮则 `FATAL` 拒写）。
**首版护栏把我自己的输出拒掉了**：它在**原始文本**里搜 `round59` / `ROUND 59` 两种**紧贴**写法，
而产物把该事实写作 **`"round": 59`** —— 隔着一个空格与两个引号。

⇒ **一般式**：**当被检验的「事实」在文件里有确定的结构位置时，判据必须读那个位置，不得读它的拼写**。
这是**第 15 次**（字节域/拼写形态）的**同族复现**：那次是「**换了拼写 ≠ 换了形态**」，
这次是「**读拼写 ≠ 读形态**」。

**修正**：改为 `json.loads` 后读 `round` / `target` **结构字段**。并补两项测试：
- **幂等测试**：同轮重复运行，输出 sha256 不变 ✅
- **负向测试**：强行把 round 60 写入 round 59 的文件 → `exit=1`、**文件未变** ✅（**有区分度，非永真护栏**）

⇒ **护栏自身也必须做「误报测试」与「漏报测试」；只跑通过路径的护栏，等于没测过护栏。**
已写入 skill 陷阱 18。

#### Round 59 收口补记（二）：把「护栏测试」做完 —— 含一次**无法失败的测试**

提交 `9d569747` 后，按上一段的自我标准继续，又发现两处问题，均已修正并登记。

**(a) 空 delta 拒写护栏（新增）**：提交后再跑证明脚本时，`HEAD` 已含被证文本 ⇒ 前后像相同 ⇒ 会产出**「插入 0 字节」的证明**却仍写 `APPEND_ONLY = true` —— **把沉默当证据**。新增护栏：`inserted == 0 and deleted == 0` ⇒ **拒写**（除非 `--allow-empty-delta`）。**测试**：提交后重跑 ⇒ `FATAL: … the measured delta is EMPTY …`、`exit=1` ✅ **已触发并生效**。

**(b) round/stage 护栏：第一次测试根本没测到它** —— 一个 round 内可有**多个追加边界**（正段、收口补记），**各有不同前像**，故**各需自己的证明文件**；已加 `--stage` 并让守卫同时校验 `round` 与 `stage`。

- **第一次测试**：造非空 delta，用 `--stage closure` 指向属于 `section` 的路径，期望被拒。**结果：它成功了（`exit=0`）** —— 因**目标路径当时并不存在**，守卫的「既有文件」分支**未进入**，**无对象可比**。⇒ **这条测试无法失败，因此它不是测试**；如实登记，未悄悄换一条能过的测试掩盖。
- **闭合（双向）**：

| 方向 | 装置 | 观测 |
|---|---|---|
| **应当拒绝** | **先创建**一个可解析、记录 `stage: section` 的目标文件，再以 `--stage closure` 指向它（工作树有非空 delta） | `FATAL: … it records stage 'section', not 'closure'`、`exit=1`、**目标文件一字未改** ✅ |
| **应当放行** | 同一文件，改用**匹配的** `--stage section` | 正常写出证明、`exit=0` ✅ |

⇒ **护栏双向有区分度**：**既非永真，亦非永假**。只做「应当拒绝」那一半，它与「一律拒绝」无法区分。

**(c) 探针残留处置（不删除）**：测试在卡内留下 `append_only_proof_round59_section.json` 与 `append_only_proof_round59_guardprobe.json`，其 delta 均为**临时探针行**（58 B / 36 B，**均已撤销**），却**长得像正式证明**。按「不做删除操作」，**两者均保留**，但**原地改写为显式测试记录**（首字段 `DO_NOT_READ_AS_A_PROOF: true`，并指向真正的证明 `append_only_proof_round59.json`）。⇒ **一般式：在不删除的前提下，必须让残留物「自证其身份」；「留着」不等于「可以留着不管」。**

**(d) 本节新增判据错误（本卡累计第 4 次）**：**以 `--out` 指向尚不存在的路径来测「覆盖护栏」** ⇒ **该测试无法失败**（护栏分支未进入）。修正：**先创建目标文件再测**，并补**反向**（匹配 stage 应放行）测试。

⇒ **一般式（本项目第 19 次同源）**：**一个「无法失败」的测试不是测试。** 自检问句：**「这个装置要怎样才会红？」** 答不出来即为无效装置。**与陷阱 13 配套**：13 说护栏要**致命**；本条给出**如何证明它致命** —— **让被禁止的形态真实出现一次**。**已写入 skill 陷阱 20。**
