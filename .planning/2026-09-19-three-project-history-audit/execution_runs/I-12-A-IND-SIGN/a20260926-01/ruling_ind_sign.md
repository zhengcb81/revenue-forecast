# ruling_ind_sign.md —— I-12-A 行业面会签裁定书（行业 reviewer · 行业半边）

> role：`industry_reviewer_i12a` · attempt：`execution_runs/I-12-A-IND-SIGN/a20260926-01` · 日期：2026-09-26（UTC+01）
> 被审对象：`execution_runs/I-12-A/a20260926-01/`（`accepted_scoped`；`professional_approval.json` 全 `unsigned`；STOP① `BLOCKED_PROFESSIONAL_DECISION` 仍在）
> 依据：卡文 `execution_v2/card_I-12-A.md` L5 Owner 行「**Owner：统计reviewer和行业reviewer共同签字**」+ L20 STOP 路径逐字「**任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION。**」
> 冻结判据：本目录 `oracle.md`（sha `40adafdc050f173080158d5a36a396bf47e2781b6f178aa17a79bb24a4aacfe7`）§3-§5 · 载体：`ind_signatures.json`
> **边界**：本件只裁行业面；**不代统计面签**（6 项阈值逐项 `deferred_to_statistics`）· **未读任何测试/准确性结果**（封存令）· 不改 `I-12-A` 任一字节 · 不产生 `ACCEPT` · `releases_nothing=true`

---

## 一、裁定总表

| id | field | 对象 | 裁定 | decision_sha256 |
|---|---|---|---|---|
| `IND-01` | 4 | `vintage_class` 硬分 | **SIGNED** | `3f14421a…45479` |
| `IND-02` | 4 | 信息截点 `available_at<=origin` / 披露日缺失不入池 | **SIGNED** | `7af0b90c…3768c5` |
| `IND-03` | 2 | 分部口径：合并/分部不双计、segment 等权 | **SIGNED** | `005856dd…196a88` |
| `IND-04` | 6 | gross/net = 对外销售收入（E5 抵销） | **SIGNED** | `ae2e5a3c…449d936` |
| `IND-05` | 6 | 实际值 = 首次披露（重述仅 secondary） | **SIGNED** | `7672e130…3305b17` |
| `IND-06` | 6 | 财年对齐 / 重组不回溯 / 并购断点新 series | **SIGNED** | `f7d5a011…cb1bfb9` |
| `IND-07` | 6 | 跨币种绝对误差展示（汇率来源） | **NOT_SIGNED** | `NOT_SIGNED` |
| `IND-08` | 3 | 公司池纳入/排除与分层结构 | **SIGNED** | `0453d74c…5dcf45` |
| `IND-09` | 8 | 朴素 baseline + 季节性 not_applicable 获批 | **SIGNED** | `9707656f…e688f68` |
| `IND-10` | 9 | `low/high` = 情景非统计区间 | **SIGNED** | `466c5aa1…07de17` |
| `IND-11` | 11 | cluster=entity / block=origin | **SIGNED** | `717d5106…bd2ed27` |
| `DEF-01` | 5 | 时间切分折数/切点/窗口 | `deferred_to_statistics` | `NOT_SIGNED` |
| `DEF-02` | 10 | 样本量/功效/CI 宽度 | `deferred_to_statistics` | `NOT_SIGNED` |
| `DEF-03` | 11 | 置信水平 α | `deferred_to_statistics` | `NOT_SIGNED` |
| `DEF-04` | 11 | 重抽样次数与种子 | `deferred_to_statistics` | `NOT_SIGNED` |
| `DEF-05` | 11 | 多重比较校正 | `deferred_to_statistics` | `NOT_SIGNED` |
| `DEF-06` | 12 | 成功/失败阈值（**重叠项**） | `deferred_to_statistics`（**行业半签 OUTSTANDING**） | `NOT_SIGNED` |

**`signed_count = 10`** · 行业面应裁 11 项全部出具裁定（10 签 + 1 `NOT_SIGNED`）· 统计面 6 项 **0 签**（无一代签）
**`industry_countersign_complete = false`**（fail-closed：`IND-07` 未签 + `DEF-06` 行业半签未完成）
**`statistics_sign_still_needed = true`**（98869ea8 并行在飞；6/6 本面未签 ⇒ STOP① 对统计面持续成立）

---

## 二、行业面逐项裁定（选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒方案）

### IND-01 · 字段 4 `vintage_class` 硬分 —— **SIGNED** `3f14421a021705288ac0bbf7ed8f36874a294cfc8fde50157bcb405c71d45479`
- **选择**：数据层以 `vintage_class` 硬分；primary 池只准 `true_vintage`；`post_hoc_reconstruction` 只进 sensitivity/secondary；primary 出现重建观测即判失败。
- **理由（依据）**：`card_I-12-A.md:L15` 动作 3 逐字「严格区分真实历史vintage与重建实验」；`evaluation_design.json:L130-L134`（`vintage_classes` + `separation_rule`）。
- **反例**：两类混池 ⇒ 事后重述口径冒充 origin 时点可得信息，skill 系统性虚高，卡文动作 3 被破坏。
- **兼容影响**：与统计面 6 项零重叠（无数值）；为字段 5 提供观测级标记，切点/折数仍归 `DEF-01`。
- **恢复规则**：primary 观测 `vintage_class` 缺失或 = post_hoc ⇒ 剔除并计数记 reason_code；须入 primary ⇒ 改 design 版本 + 重新双签。
- **被拒方案**：按 `model_version` 标记替代硬分；按数据来源路径事后推断；「primary 以重建为主」方向倒置。

### IND-02 · 字段 4 信息截点 —— **SIGNED** `7af0b90c47db86d0ca18de723f6de511c401c62e72b03ae16c510c24963768c5`
- **选择**：`available_at<=origin` 严格成立（违反 = 泄漏观测，剔除并计数、不静默丢弃）；披露日缺失 ⇒ `unavailable` 不入池（fail-closed，禁止默认可用）。
- **理由**：`evaluation_design.json:L123`（hard_constraint）、`L129`（missing_publish_date_rule）、`L127`（小米 gap-U2 登记 null）。
- **反例**：默认「缺失 = 可用」让 origin 后公开信息入池，skill 虚高且不可审。
- **兼容影响**：与 `DEF-01` 互补不重叠（观测可得性 vs 切分折数）；不含阈值。
- **恢复规则**：补登记可核 `available_at`（sha 可核且 <= origin）后同版本 append 入池；改 design ⇒ 新探索版本。
- **被拒方案**：按 `as_of` 近似披露日；插补默认更早日期。

### IND-03 · 字段 2 分部口径与重复权重 —— **SIGNED** `005856dd9b3e9ab599654d8ef0f4a0427e9776d99a55dd4fbe13357abf196a88`
- **选择**：合并 = Σ四分部对外销售收入；同一 `origin×horizon` 合并与分部并存 ⇒ 只计分部层，合并行仅作 `driver_reconciliation` 校验；entity 内 segment 等权。
- **理由**：`evaluation_design.json:L76-L78`（segment_weight / merge_vs_segment_rule / duplicate_rule）。
- **反例**：合并与分部同值同时入池 ⇒ 同一收入计两次，误差池分母翻倍稀释，WAPE/skill 虚高且不可归因。
- **兼容影响**：macro/micro 并报已在字段 9 冻结（filled、非 6 项）；方差估计方法归 `DEF-03/DEF-04`。
- **恢复规则**：恒等式破（合并 ≠ Σ分部）⇒ 剔除误差池、记 reason_code、只进 reconciliation 残差，修复前不入 primary。
- **被拒方案**：合并行优先；双行取平均；按收入规模加权 segment。

### IND-04 · 字段 6 gross/net 统一 —— **SIGNED** `ae2e5a3cfc685f66c0fdc27a4ee4bc17a43e636a30bbed5c7f1581fb8449d936`
- **选择**：统一为对外销售收入（net of internal，E5 抵销口径）；含内部交易的分部总计不得作收入基期/actual。
- **理由**：`evaluation_design.json:L158`（字段 6 定义）、`L169`（gross_net，含「否则高估约 67%，上游 §C4」**转引**）。
- **反例**：以含内部交易分部合计作基期 ⇒ 内部转移重复计入，基期/增速系统性高估，误差分母全错。
- **兼容影响**：纯口径、零阈值；「约 67%」转引未独立复核（oracle §4 残余 1），本签只锁口径不锁该数值。
- **恢复规则**：仅 gross 披露 ⇒ 记 reason_code 不入 primary，补可核 net 后再入；口径改判须改 design 版本 + 重签。
- **被拒方案**：gross × 经验折扣系数（不可核）；逐实体混用 gross/net。

### IND-05 · 字段 6 实际值定义 —— **SIGNED** `7672e130f2f27b62e6a6bf16ceb3a2d561e193e470db39f82a0247d3d3305b17`
- **选择**：primary actual = 首次披露值（as-originally-reported）；最终重述仅 secondary，且 origin 时点不可得者不得入 primary。
- **理由**：`evaluation_design.json:L163-L164`。
- **反例**：重述值入 primary ⇒ 引入 origin 后才存在的会计调整信息，与 `available_at<=origin` 冲突。
- **兼容影响**：与 IND-01 vintage 硬分同向（重述 = post_hoc）；零阈值重叠。
- **恢复规则**：重述登记为 secondary（`vintage_class=post_hoc`）；升 primary 须新版本 + 双签 + origin 可得性证明。
- **被拒方案**：重述作 primary（look-ahead）；首披与重述取均值。

### IND-06 · 字段 6 财年 / 重组 / 并购 —— **SIGNED** `f7d5a011ce828e4cfffb92f63ec43662f0dd79a93439b2676de6a1cd3cb1bfb9`
- **选择**：统一 FY 标签 + 显式财年截止（微软 6-30、紫金/小米 12-31），不同截止期不当同一 horizon；重组不回溯（回溯 = 新 vintage）；并购断点后单列新 series、不跨断点算误差。
- **理由**：`evaluation_design.json:L167-L170`。
- **反例**：跨财年混层 ⇒ 日历年错配；跨并购断点续算 ⇒ 断点两侧不可比却同池。
- **兼容影响**：支撑字段 7 分层（filled、无需签）；切分折数归 `DEF-01`；零阈值。
- **恢复规则**：财年错配观测剔除并计 reason_code；断点未登记 ⇒ 补登记后按新 series 重算（同版本记 append）。
- **被拒方案**：按自然年重切财年数据；备考口径回溯拼接；不分财年混层平均。

### IND-07 · 字段 6 跨币种绝对误差展示 —— **NOT_SIGNED** `NOT_SIGNED`
- **裁定**：**不签（维持 PENDING）**。
- **not_signed_reason（fail-closed）**：无可核的 origin 前可得汇率来源 —— 本面禁联网、回源面不含任何汇率登记 ⇒ 无法给出「文件+行号」级依据，不以近似汇率凑签（`evaluation_design.json:L166` 自身即标 PENDING「不伪造」）。
- **反例**：用 as_of 汇率换算 origin 前误差 = 引入 origin 后信息；用假定固定汇率先签后补 = 挑方便值（卡文动作 1 禁）。
- **兼容影响**：不阻断无量纲主路径（`L165` 已限定跨实体只用 WAPE/Skill/bias），故不阻断 IND-04/05/06；但属行业面未签项 ⇒ 直接导致 `industry_countersign_complete=false`。
- **恢复规则**：补登记 origin 前可得汇率（来源 sha 可核 + 取数时点 <= origin + 时区）后按同版本补签；此前跨币种绝对金额误差一律不汇总、不出数。
- **被拒方案**：固定汇率（如 7.0）凑签；as_of 汇率换算。

### IND-08 · 字段 3 公司池与分层 —— **SIGNED** `0453d74c7b7397154a349515dea68252125445501884093151bd3565195dcf45`
- **选择**：三家公司 frame（紫金 A+H / 小米 HK / 微软 US）；纳入 = 原文可核 sha + `available_at<=origin` 已登记 + 分部口径可对齐；小米因 gap-U1/U2 fail-closed 排除并记 reason_code（带 reentry）；退市/失败/并购不静默剔除；分层 = 市场×行业×生命周期×可得披露条件，层间不合并单一平均。
- **理由**：`evaluation_design.json:L90`、`L92-L96`、`L100`、`L102-L110`；`professional_approval.json:L39`（行业 scope 字段 3）。
- **反例**：为凑样本给小米补假数据入池 = 伪造；静默剔除退市/并购公司 = 池选择性偏倚不可审。
- **兼容影响**：只签结构与理由；层内最小 n / 功效 / CI 宽度归字段 10（`DEF-02`）；可评 entity = 2 ⇒ 不足时按字段 10 降级描述性，**本签不放行样本结论**。
- **恢复规则**：解 gap-U1/U2 后按同版本 append 入池；池结构变更 ⇒ 新 design 版本 + 重签。
- **被拒方案**：小米按零增长入池；不记排除理由；扩池到审计外公司凑 n。

### IND-09 · 字段 8 朴素 baseline + not_applicable 获批 —— **SIGNED** `9707656f7b65e5235d31d433c08a16a9d73cf9ed361f1e74e88db0f52e688f68`
- **选择**：primary = 最后可得同口径年度收入不变（与上游 EA-3 同形）；secondary = 上一可得同比延续；**「季节性同季」= `not_applicable` 由行业面获批**（可得序列是年度分部收入，无同季可比序列）；baseline 不可得 ⇒ `undefined` 计数，不改用其他 baseline。
- **理由**：`evaluation_design.json:L194`、`L196-L199`（`approval=pending_reviewer`）、`L201`（tie_in 字段 1 分母）；`professional_approval.json:L40`（行业 scope：字段 8 + not_applicable 项）。
- **反例**：无同季序列硬造季节 baseline = 拿噪声当基准、skill 分母失真；baseline 不可得时偷换更弱 baseline = 挑方便值。
- **兼容影响**：baseline 是字段 1 primary 的分母，本签零阈值数值；not_applicable 获批**仅限「季节性同季」整项**；与 `DEF-01..06` 零重叠。
- **恢复规则**：登记到可比同季序列 ⇒ 该 not_applicable 失效，须改 design 版本 + 重签方可启用季节 baseline。
- **被拒方案**：标 not_applicable 却声称覆盖季节性；以 3 个月移动平均代同季；primary 改 YoY 延续（与 EA-3 不同形）。

### IND-10 · 字段 9 `low/high` = 情景 —— **SIGNED** `466c5aa1c01583afd184a40a714dd2525360e404d7ad0a4b68a6c0bf1c07de17`
- **选择**：`low/high` = 情景带非统计区间：只评 `scenario_containment` 且同时报 `interval_width`；禁称 80%/90% 置信覆盖；`interval_score`/`pinball` 禁用。
- **理由**：`card_I-12-A.md:L15` 动作 3 逐字「低/高情景没有概率标签就只评情景包含率」；`evaluation_design.json:L215-L216`。
- **反例**：给情景带标「90% 覆盖」或用 interval_score = 声称不存在的名义概率，把敏感性设计误报为精度主张。
- **兼容影响**：只锁语义边界；字段 12 的「可接受包含率」**数值**归 `DEF-06`（统计面出值后行业回签），零数值重叠。
- **恢复规则**：上游补事前声明的名义概率与 tau ⇒ 开新 design 版本双签后才可启用 interval_score/pinball，本版不得追溯启用。
- **被拒方案**：base 当中位数、low/high 当 10/90 分位；极宽区间换高包含率且不报宽度。

### IND-11 · 字段 11 cluster/block 单位 —— **SIGNED** `717d5106f1d4a10543d1841a97fe385c6b5eb2502eb5a2e899940d695bd2ed27`
- **选择**：cluster = entity（同集团分部强相关）；block = origin（时间块）；重叠 horizon 按 origin 聚簇、方差按 origin block 估计，不假设观测独立。
- **理由**：`evaluation_design.json:L243-L244`；`professional_approval.json:L41`（行业 scope：字段 11 cluster/block 单位）。
- **反例**：把 `entity×segment` 当独立观测 ⇒ 同集团分部相关性被忽略，方差低估、CI 收窄、显著性虚高。
- **兼容影响**：**只签单位选择**；置信水平 / 重抽样次数与种子 / 多重比较校正归 `DEF-03/04/05`，本面一个都不碰。
- **恢复规则**：跨集团合并样本或 origin 层不足 ⇒ cluster/block 定义重议，改 design 版本 + 重签。
- **被拒方案**：cluster=segment；block=财年；不聚簇直接 i.i.d. 重抽样。

---

## 三、与统计面 6 项阈值的分工（互补不重叠；重叠项如实标 `deferred_to_statistics`）

| # | 统计面 6 项（`professional_approval.json` L57-L64） | 本面处置 | 与行业面关系 |
|---|---|---|---|
| 1 | 字段 5 时间划分折数/切点/窗口长度（`DEF-01`） | `deferred_to_statistics`，0 签 | 与 IND-02 互补（观测可得性 vs 切分） |
| 2 | 字段 10 最小样本量/功效/可接受 CI 宽度（`DEF-02`） | `deferred_to_statistics`，0 签 | IND-08 只签池/分层结构，不签 n |
| 3 | 字段 11 置信水平 α（`DEF-03`） | `deferred_to_statistics`，0 签 | IND-11 只签 cluster/block 单位 |
| 4 | 字段 11 重抽样次数与随机种子（`DEF-04`） | `deferred_to_statistics`，0 签 | 同上，重抽样参数不碰 |
| 5 | 字段 11 多重比较校正（`DEF-05`） | `deferred_to_statistics`，0 签 | 行业面无对应项 |
| 6 | 字段 12 成功/失败阈值（`DEF-06`，**重叠**） | `deferred_to_statistics` + **行业半签 OUTSTANDING** | 卡文 Owner 条款与 `professional_approval.json:L42` 要求双签：统计面出值后**行业回签**（早于解封） |

> 结果：本面**未代签任何统计阈值**；6 项对 STOP① 的解除力 = 0。`DEF-06` 双签未齐 ⇒ 即便统计面 6/6 落签，仍须行业回签 + 新版本重冻 + 编排层解封指令，方可解 STOP①。

---

## 四、红绿变异（原件与 `I-12-A` 三件字节不动；红臂在 `_mut/Rx/` 副本执行）

校验器：`_verify_ind_sign.ps1`（K1-K5，冻结自 oracle §4）· legend：`0`=ALL_INVARIANTS_OK · `1`=harness 失败 · `2`=无裁决 · `3`=不变量违例

| id | 变异 | 期望 rc | 实测 rc | 击杀判据 | 结果 |
|---|---|---|---|---|---|
| `GREEN` | 原件（oracle + ind_signatures + handoff） | **0** | **0** | K1-K5 全 OK | ✅ |
| `R1` | `handoff.statistics_sign_still_needed` true→false | 3 | **3** | `K1_release_lock` FAIL（具名 1 处） | ✅ 击杀 |
| `R2` | `IND-01.decision_payload` 改 1 段（sha 不改） | 3 | **3** | `K4` 签署载荷哈希不符 | ✅ 击杀 |
| `R3` | `DEF-06.ruling` →`SIGNED` + 伪造 sha（行业代签统计阈值） | 3 | **3** | `K4` 具名 6 处（signed_by / 非统计 6 项 / 六要素 / 载荷哈希 / 代签 / signed_count 10≠11） | ✅ 击杀 |
| `R4` | `source_hashes` 中 `professional_approval.json` 改 1 hex | 3 | **3** | `K3_source_integrity` FAIL | ✅ 击杀 |
| `R5` | `handoff.industry_countersign_complete` false→true（谎报完成） | 3 | **3** | `K4` FAIL（True ≠ 计算值 False） | ✅ 击杀 |
| `GREEN_FINAL` | 定稿后原件复跑 | **0** | **0** | K1-K5 全 OK | ✅ |
| 红臂定稿复跑 | R1-R5 在定稿件上重跑 | 3×5 | **3×5** | 与上表一致（变异字段在两版逐字一致） | ✅ |

红臂原始输出逐字：`_mut/R1..R5/verifier_output.txt`。

---

## 五、残余与边界（不隐藏）

1. **`IND-07` `NOT_SIGNED`**：跨币种绝对误差展示缺 origin 前可核汇率来源（禁网 + 回源面无汇率登记）；不伪造、不凑签。
2. **`DEF-06` 行业半签 OUTSTANDING**：字段 12 需统计 + 行业共同签字，本并行轮无值可签 ⇒ `industry_countersign_complete=false`；统计面出值后须行业回签（早于解封）。
3. **转引未独立复核**：上游 §C4/E5 恒等式与「约 67%」转引自 `evaluation_design.json:L77/L169`（本面未回读 `calibration_validation_summary.md`，封存纪律）。
4. **STOP① 未解除**：本面只登记签署事实与未签残余；裁定权在独立复审/编排层；不改任何卡 `status`/`decision`/`decision_sha256`。
5. **OPEN-2 红线**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 只登记不消费 —— 未作任何裁定输入、阈值或分层。
6. **没做的事**：未读测试集/准确性结果 · 未代统计面签任何一项 · 未放行参数 · 未产生 `ACCEPT` · 未派 `I-12-B` · 未跑任何 git 命令（含禁用的 `git status`）· 未联网 · 未写 `.planning` 之外（`git_diff_non_planning=0`）。
