# I-13-BC · 合并卡（阶段 B 独答 + 阶段 C 定级）—— 独立买方 reviewer + 行业 reviewer 复审报告

- 被审 attempt：`execution_runs/I-13-BC/a20260926-01`（`status=review_pending`，两段：独答 B + 定级 C）
- 复审人：独立买方 reviewer + 行业 reviewer（合并单元双面，卡文 Owner 面；本件只出报告，**不写卡状态**、不产生 `ACCEPT` 写入、不改任何 `status`/`decision`）
- 报告面：本文件 + 同目录 `reviewer_report.sha256`（**写入面 = 2 个新文件**，被审 7 件与上游全部只读、收尾复哈希）

---

**VERDICT: ACCEPT —— P1×0（数值/推导、`124,248.63` 红线、封盘 `f2178768…`、`M1` 必红四项全过）；P2×1、P3×4 随附。⭐ 首要裁定：「最终报告」两读法 → 本人采**采用读法**（最终交付报告面 = `I-07-E calibration_validation_summary.md` 可得）⇒ **阶段 B 不 `STOP`、整卡不 `STOP`**；严格读法登记在案不采纳（若采 ⇒ 本卡交付物落 `blocked`，仍是 ACCEPT 合格交付，`P1` 不因它触发）。Q3 `not_answerable` 判定正确、consensus 明写不可得合规、分类机械推导自算一致、14 模型三栏 accuracy 14/14 = `unproven`、变异绿臂 `rc=0` / `M1 rc=3(J2)` / `M3 rc=3(J1,J5)` 全部本人复跑复现。**

---

## 一、回源面（V2-4 只读清单，全部实际读到）

| # | 件 | 本人动作 | 结果 |
|---|---|---|---|
| 1 | `oracle.md` 27,249 B · `f1f9240a…` | 全读 208 行 | ✅ 与 handoff `written_files` 一致；mtime 21:20:59 **先于全部产物**（冻结时序实证） |
| 2 | `reviewer_answers.json` 27,844 B · `df599de9…` | 全读 280 行 | ✅ |
| 3 | `final_scorecard.json` 27,097 B · `06976e80…` | 全读 264 行 + 机读复算 | ✅ |
| 4 | `verification.json` 8,638 B · `ed069b7c…` | 全读 84 行 | ✅ |
| 5 | `handoff.json` 20,486 B（自指不记自身 sha） | 全读 160 行 | ✅ |
| 6 | `_verify_i13bc.py` 11,535 B · `6d35df40…` | 全读 225 行 | ✅ 判据 J1–J6 与 oracle §6 冻结件对齐 |
| 7 | `_run_mutations.py` 5,112 B · `15510571…` | 全读 136 行 | ✅ 原件/副本分离，before/after 快照比对 |
| 8 | `_mut/`（M1–M6 ×6 臂 36 件 + `mutation_summary.json` = 37 件） | 抽验臂输出 + 机读 summary | ✅ `originals_untouched=true` |
| 9 | 合并卡 `card_I-13-BC.md` 2,528 B · `56d1dad5…` | 全读 36 行 | ✅ L3/L5/L12/L27/L36 逐字 |
| 10 | 原卡 `card_I-13-B.md` 1,668 B · `bd5abc55…` / `card_I-13-C.md` 1,448 B · `575393ab…` | 全读各 25 行 | ✅ 判据权威，逐字引用见 §二/§三/§四 |
| 11 | 上游 `I-13-A/a20260926-01`：`handoff.json`（`accepted_scoped`、`status_transition`、carrier `7f0c379c…`、`three_way_match=true`）· `reviewer_report.md` 14,143 B · `buy_side_scorecard.json` | 实读 | ✅ 分类输入 `B01..B08=1,1,1,1,1,1,2,1`、`total=9/16`、`zeros_present=0`、`HB3=not_established` |
| 12 | `I-07-E/…/calibration_validation_summary.md` 26,132 B · `a2304fdd…` | 全读 153 行 | ✅ 阶段 B 作答报告面（§A–§F 定位见 §三） |
| 13 | `I-11-C/…/parameter_mapping.json` 54,875 B · `d542b34d…` | 定域读 L45-L117 / L525-L531 / L592-L597 / L840-L851 / L1262-L1291 | ✅ 溯源链抽验依据 |
| 14 | store `OPEN2-C2-REGISTRATION/…/hypotheses_v3.json` 61,231 B · `b2063ac8…` | 定域读 L1-L8 / L320-L325 / L544-L547 / L620-L624 / L855-L859 | ✅ 回执 R-1 逐字引文核对 |
| 15 | 尺：`common_research_cards.md` L8-L11 / L155-L164 / L291-L312；`research_cards.md` L516-L526 / L537-L604 | 定域读 | ✅ 评分规则、CAGR 规则、三栏禁令、原卡同文逐字一致 |

**14 件上游 sha 本人独立复算：14/14 一致**（含封盘 `f2178768…` 51,697 B、store `b2063ac8…` 61,231 B）；本 run `written_files` 6/6 复算一致；mtime 时序 `oracle 21:20:59 → reviewer_answers 21:25:09 → final_scorecard 21:27:56 → 两 py → verification 21:34:10 → handoff 21:34:34` ✅「oracle 先冻结」实证。

---

## 二、⭐ 首要裁定：「最终报告」两读法（本复审核心职权）

### 裁定
> **采「采用读法」**：`card_I-13-B` L13「只用最终报告」= **本链最终交付的报告面** `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md`（sha `a2304fdd…`，26,132 B，153 行全读，研究草稿形态）。
> ⇒ **该报告面可得 ⇒ 阶段 B 不 `STOP`、整卡不 `STOP`**；走查结论、缺口路由与阶段 C 定级全部维持。
> **严格读法**（须独立成篇正式最终研究报告 ⇒ 授权回源面内不存在 ⇒ `STOP` 判 `blocked` ⇒ 整卡 `STOP`）**登记在案、不采纳**；两读法与推翻条件实现者已如实预登记（`reviewer_answers.final_report_identification`），**本站裁定、不改状态**。

### 逐字依据（采用读法）
1. **前提绑定同客体** —— `card_I-13-B` L9 前提逐字：「**完整输出已评分，可区分事实、假设、未知。**」而 I-13-A `buy_side_scorecard.scored_object.primary_artifact` 逐字即 `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md (sha a2304fdd…, 26132 B)`。⇒ 动作1 的「最终报告」与前提的「完整输出」必须是同一对象；否则卡片前提与动作指向两件产物，而**回源面内不存在任何第三件报告形态产物**。
2. **验收用词是「最终交付」** —— L23 逐字：「具体问题可用**最终交付**独立回答；缺失需回到对应卡，不能在总结里虚报补齐。」可得的最终交付即该 summary，且其上游 `I-07-E/handoff` 已 `accepted_scoped`（carrier `6b48a2f5…`、`three_way_match=true`）——即**已被审过的交付件**。
3. **全族依赖指向同一客体** —— `research_cards.md` L539：I-13-A「依赖：**I-07-E、I-11-C**」；`card_I-13-B` L5 依赖 I-13-A。I-13 全族的审阅客体自始是 I-07-E 交付面，中间无另一份「正式报告」载体。
4. **报告自述其为交付件** —— summary L1 标题逐字「I-07-E 校准/验证汇总表（**研究草稿** · 全量数值 proposed/mapped_not_released）」；§E L135 逐字「**下一步归属：交 I-13 买方验收**」。
5. **卡文的不合格判据是内容性的，不是形态性的** —— L20 逐字：「**报告只能给目标数，无法回答驱动/时点/约束→STOP_INVESTOR_USE**」；合并卡 L27 逐字「阶段 B：**最终报告不可得** ⇒ `STOP` 判 `blocked`」用词为**可得（availability）**，全卡无「独立成篇/正式/发布件」限定语。严格读法的形态要件是**从卡外引入的**。
6. **框架三档语义反证** —— `common_research_cards.md` L293 与 `card_I-13-C` L23 明确认可中间档「研究草稿可审阅」。若采严格读法，则本链 `research_draft_needs_review` 档自相矛盾地不可达（该档的存在前提恰是「草稿形态报告可被审阅」），与 I-13-A 已落定 `accepted_scoped` 的同一客体判定直接冲突。

### 反例（用以界定采用读法的边界，严格读法本应获胜的场景）
- **(a) 裸数值/manifest 面**：若回源面内只有数字表或 manifest、无法区分事实/假设/未知 ⇒ 两读法**均**判「报告不可得」→ `STOP`。本次不成立：summary 153 行、§A 冻结表/§B 18 槽位/§C 驱动口径/§D 验证/§E 三公司结果/§F 红线登记齐备，L9 前提（可区分事实、假设、未知）经本人通读成立。
- **(b) 链外独立成篇正式报告**：即便某份正式报告独立成篇，只要不属本链最终交付，仍不可作答面 ⇒ 说明「独立成篇正式」**既非文本要件、也不是充分条件**；判据是**交付归属 + 内容可答性**，不是形态。
- **(c) 正式报告后发且与草稿面冲突**：此时采用读法自动让位（见恢复规则），不得以草稿面答案顶替——这是严格读法唯一有实益的适用场景。

### 兼容影响
- **采用读法（本案）**：阶段 B `stop_triggered=false` 成立；整卡不 `STOP`；`classification` 维持机械推导 `research_draft_needs_review`；本件可进入「一次复审 → 一次落定（父直写）」；I-12 / I-16-A / I-16 / I-17 依赖顺序另派不受影响。
- **若采严格读法**：阶段 B 转 `STOP(blocked)` ⇒ 按合并卡 L27 + 父 21:1x「任一段 `STOP` ⇒ 整卡 `STOP`」fail-closed ⇒ **本卡交付物落 `blocked`**（该 `blocked` 仍是 ACCEPT 合格交付，`P1` 不因它触发）；`final_scorecard` 的分类**推导输入不变**（仍 `research_draft_needs_review`），STOP 记账与分类推导分两本账，改判由复审/父直写执行——**本人本次不写任何状态**。

### 恢复规则
1. **生效条件**：报告面 = I-07-E summary（sha `a2304fdd…` / 26,132 B / 153 行）且同时满足 L9（可区分事实、假设、未知）与 L20 内容判据。
2. **失效触发（任一即重判）**：① `formal_publication_slot` 脱离 `blocked`、正式最终研究报告发布；② 报告面 sha 变更/被替换；③ owner 或有权复审明文采严格读法。触发 ⇒ 阶段 B 五问对**新报告面全量重答**，并按 `reviewer_answers.final_report_identification.overturn_condition` 记账。
3. **不随读法变化的部分**：Q3 缺口与 G1–G8 路由、三栏 `accuracy=unproven`、红线只登记不消费、封盘/store 零字节、`params_released=false`。

---

## 三、阶段 B 独答复核（Q1–Q5 + 预期对照 + 溯源链）

| 问 | 实现者判 | 本人复核 |
|---|---|---|
| Q1 增长从何而来 | `partial` | ✅ 基情景 ZJ 持平（summary L36-L39/L68）、MSFT 三分部增速持续（L17/L54-L56）、情景带 D1±5%/D2±10% 成对联动（L71/L88）、小米 0 槽位（L16/L60/L131）逐条可定位；`partial` 理由（无贡献占比 → Q3）成立 |
| Q2 何时确认 | `partial` | ✅ 生效期间可答（summary L15/L17；PM L52-L53 年度粒度）；确认时点缺、机制链止于环节名——store L546 逐字核中「产量计划本身不构成收入确认；且原文声明为指导性指标、不构成承诺」 |
| **Q3 最大三项驱动贡献** | **`not_answerable`** | ✅ **判定正确**：报告面只有 D1-D7 驱动注册（summary L83-L84）与逐参数敏感性带，**无任何贡献分解产物**；冻结规则为线性单通道可加（PM L1279 逐字「任一情景 收入增量=Σ(各驱动单通道增量)；同一事件不得贡献两个及以上通道；违反⇒STOP_SCENARIO」）但**各通道增量未被计算**；`interaction_allocation=none` + `numeric_contribution_shares=[]` 合 `card_I-13-B` L14 禁令；带幅序登记显式标注「≠贡献、不得引用为贡献」。与 I-13-A `B06=1`（贡献分解未完整说明）一致，**不新增 0、不新增硬阻断** |
| Q4 高情景失败约束 | `answerable`（7 条） | ✅ 抽 4 条回源：EA-6 联合约束（L71/L88）· 产销库存上限（store L323 逐字核中）· `BLOCKED-6b` 154 千克 `NOT_SIGNED`（summary L44；PM L530「库存桥 154 千克容差未签」、L596「同铜：BLOCKED-6b」逐字核中）· 红线禁消费（L139-L147）；另 3 条（L47/L81 计划对照、H4 `threshold_review_status=not_reviewed`、EA-4 纯分析师判断 L69/L106）均可定位 |
| Q5 推翻基情景的证据 | `answerable`（3 条） | ✅ 库存释放一次性登记与持平基线张力（L15/L43-L44/L68，产量 878,180/82,743 vs 销量 884,943/83,161 与 summary 逐位一致）· u-N5 语义张力（349,079,082,852 ÷ 109,977,556,345 = **3.1735**，与 L70「约 3.17 倍」一致）· EA-4 反证（L17/L69/L23） |

**预期对照（动作3）**：`consensus_availability="unavailable"` + `consensus_statement` 明写「授权回源面内无可靠 consensus/market-implied 数据（禁联网、I-12 未做、清单外零读）」+ `consensus_numbers=[]` + `market_implied_numbers=[]` ⇒ **`card_I-13-B` L15「明确写不可得，不编数字」逐字合规**；口径差异登记 5 项（u-N5 层级、红线两值分母、产量/销量、总/净额含 234,970,146,412 抵销、Cloud 聚合口径）≥ 卡片要求，且**每项都归因口径而非市场分歧**，无预期差主张。

**溯源链 7 条（要求 ≥5），本人抽 2 条自验**：
- **CH-1**（差额法基期）：`349,079,082,852 − 165,858,644,874 − 29,212,610,830 − 44,030,270,803 = 109,977,556,345`（差=0，**本人逐位自算 ✅**）；`low/high = 104,478,678,528 / 115,476,434,162` 与 PM L45-L117（row1 `new_value` 逐位）与 summary L36 三方一致 ✅；`joint_scenario_constraint`（PM L111）与 EA-6 表述一致 ✅。
- **CH-5**（抵销恒等式）：`584,049,229,264 − 234,970,146,412 = 349,079,082,852`（**自算 ✅**）；PM L843-L897 实为 `ZIJIN_SEGMENT_RECONCILIATION_FY2027` 行、`original_value` 逐字同式 ✅；store L622 claim 逐字核中「…必须显式扣除内部抵销 234,970,146,412 元（2025年），否则会高估收入约 67%」 ✅；summary L48/L111 定位 ✅。
- 附：回执 R-1 抽 4 条逐字复核（store L4 / L323 / L546 / L856-L858）**全部逐字一致**，「摘要或 manifest 名不代替实际读取」（L16）成立。

**复核面五项（动作2）**：五项齐、复算值全标 `review_recompute_not_released` ✅；本人复算抽验：四分部 base 合计 `=349,079,082,852` ✅；high 逐行和 `=366,533,036,995`、low 逐行和 `=331,625,128,710`（逐位相等）✅；CAGR 规则按 L163：ZJ `(0.95)^(1/2)−1 ≈ −2.53%`、`(1.05)^(1/2)−1 ≈ +2.47%` ✅、base 0.00% 为 EA-3 假设推论非伪造 ✅、小米 `undefined` + 绝对增量不可得 ✅；MSFT h=1 ⇒ CAGR=g，带换算 `1.16×0.95−1=0.102`、`1.16×1.05−1=0.218`、`1.3×0.95−1=0.235`、`0.99×1.05−1=0.0395` 逐位 ✅；MSFT 单年增量 `139,996×0.16≈+22,399`、`137,791×0.30≈+41,337`、`54,052×(−0.01)≈−541` ✅。

**停止判据**：`STOP_INVESTOR_USE` 未触发（报告面非「只能给目标数」——驱动 D1-D7、生效期间、7 条约束、3 条反证均可答；Q3 属 L23「缺失→回对应卡」情形）✅ 本人同意；`STOP_ACCOUNTING` 未触发（情景≠概率 `probability_claims_count=0`、产量/销量、总/净额三重区分字段齐）✅ 本人同意。

---

## 四、阶段 C 定级复核

### 4.1 分类机械推导（本人自算）
```
规则（common_research_cards.md L293 逐字）：任一硬阻断或任一维度0→blocked；没有0但存在1→research_draft_needs_review；全部八维2且独立签署→buy_side_review_ready
established_hard_blocks = []      （HB1..HB7 全 not_established；HB3=not_established 承 I-13-A 复审裁定 carrier 7f0c379c…）
dimension_scores = B01..B08 = 1,1,1,1,1,1,2,1   （I-13-A buy_side_scorecard sha e74631c7…，total=9/16）
zeros_present = 0 ;  存在 1 的维度 = 7
⇒ 机械结果 = research_draft_needs_review      ✅ 与产物 classification 逐字一致（本人机读复算 match=True）
```
`buy_side_review_ready` 不可达的三重理由（7 维为 1 / 缺独立全维签署 / `card_I-13-C` L20 未解 blocking issue + 缺独立签名）登记完整 ✅；三资格状态分列且互不替代：`research_reviewable=research_draft_needs_review` / `deployment_usable=false` / `forecast_accuracy=unproven`（机读 distinct=3）✅。

### 4.2 逐模型三栏（机读 + 抽 3 行）
- 机读：`rows=14`（与 `row_count` 声明一致）、三栏 `status`/`detail` **无一为空**、`accuracy != unproven` 者 **0 行（14/14 = `unproven`）**、pass-like `row_status` **0 行**、`rows_claiming_formal_delivery=0` ✅。
- **抽 1 `MS-PBP-M05`**：formula `accepted_scoped_not_extrapolated`（0.102/0.16/0.218 逐位 ✅）· disclosure `not_granted`（summary L130/L134 `STOP_DISCLOSURE_ADAPTATION` ✅）· accuracy `unproven` · `row_status=disclosure_not_granted_no_formal_delivery`（非 pass）⇒ **公式栏 PASS 未盖披露栏** ✅。
- **抽 2 `ZJ-ELIM-05`**：formula `contract_arithmetic_signed_tolerance`（恒等式差=0 自算 ✅）· disclosure `audited_caliber_h_elim_05`（store L622 ✅）· accuracy `unproven`（「恒等式可核≠预测准确性」语义正确）· `row_status=research_draft_only_not_ready` ✅。
- **抽 3 `XM-EV-M03`**：formula `historical_reconstruction_only`（411,082 辆×251,171 元 + other_revenue 2,800,000,000 元，summary L16 ✅）· disclosure `signed_case_limited`（4 case 之一，L134 ✅）· accuracy `unproven` · `row_status=blocked_gap_no_fy2027_path`（缺位如实登记）✅。
- 旁证：披露不授予两行 `MS-PBP-M05`/`MS-IC-M06` 均 `not_granted` 且 `row_status` 非 pass ✅；未见 I-10-A 案的 `ZJ-TRADE`/`ZJ-OTHER`/`MSFT-MPC` 登记为 `not_registered_in_read_face`（不虚报已签）✅；18 槽位覆盖 = 13 紫金 + 5 微软（`5/18 not_executable` 与 summary L60 一致）✅。

### 4.3 保留清单（五项）与停止条件
`retained` 五项齐 ✅：三源 doc sha（`01819e1c…`/`ffd73376…`/`e3de0053…40ecfff` 64 位并登记 u-N4）+ 载体 hash（PM `d542b34d…`、store `b2063ac8…`、封盘 `f2178768…`、summary `a2304fdd…`、EA `9f8b844e…`）+ `M01-M31` 逐模型 hash **显式登记不可得（不虚报）** + `as_of=2026-09-18`（gap-U2 如实）+ 当前限制 8 条 + 触发更新条件 8 条 + 下次卡与 owner 5 条。
`stop_conditions_evaluated`：`ready_prohibition.applied=true`（结果非 ready）✅；`STOP_PROVENANCE` 未触发（无任何 host_receipt/发布主张、`publication_card_walked=false`、`index_modified=false`）✅ 本人同意；动作4 未走发布卡 ✅；`independent_buy_side_signoff.status=pending_not_produced`（不代签、不自签）✅。

---

## 五、变异复跑（本人只读重跑，原件零改动）

`python -B _verify_i13bc.py --root <root> --plan <plan-root>`（`--plan` = `.planning/2026-09-19-three-project-history-audit`）：

| 臂 | oracle 冻结期望 | 本人实测 rc | 具名违例 | 判 |
|---|---|---|---|---|
| GREEN（原件） | 0 | **0** `ALL_INVARIANTS_OK` | — | ✅ |
| **M1 一栏 PASS 盖另一栏**（派单点名，必须红） | 3 / J2 | **3** | `J2: row MS-PBP-M05 row_status pass-like despite unproven accuracy / non-granted columns` | ✅ **必红命中** |
| M2 accuracy 改 verified | 3 / J2 | 3 | `J2: row ZJ-SMT-M09 accuracy.status != unproven` | ✅ |
| **M3 越权 `ready`** | 3 / J5(,J1) | **3** | `J1` ×2（`deployment_usable != false`、`classification must not be buy_side_review_ready`）+ `J5` ×2（`rule-derived=research_draft_needs_review`、ready 无全维2+独立签署） | ✅ |
| M4 `params_released=true` + 消费标记 | 3 / J1(,J3) | 3 | `J1` + `J3` ×2 | ✅ |
| M5 编造 consensus + 贡献份额 | 3 / J4 | 3 | `J4` ×3 | ✅ |
| M6 情景改标概率 + 产量/销量互换 | 3 / J4 | 3 | `J4` ×3 | ✅ |
| `GREEN_AFTER_MUTATIONS` / 定稿绿臂 | 0 | **0**（`mutation_summary.json` 记 `originals_untouched=true`） | — | ✅ |

`_mut` 与原件字节关系：`mutation_summary.before/after` 逐件相同；本人另复算 `oracle/reviewer_answers/final_scorecard` 三件 sha 与 before 快照逐字一致、`verification`/`handoff` 为定稿后追加写（`ed069b7c…` / 自指）⇒ **原件未被红臂污染** ✅。目录计数 44 件 = 顶层 7 + `_mut` 37，无 `__pycache__`（`-B` 执行）✅。

---

## 六、`OPEN-2` 红线 + 封盘（收尾复哈希）

**红线 `124,248.63`（真值 `38,175.95`）只登记不消费 → ✅ 未破**

| 检查（本人独立扫描五件正文） | 结果 |
|---|---|
| 红线族 token（14 个变体）出现行 | **6 行**：`oracle.md` L53/L152/L154（派单逐字 + §4 登记区）、`reviewer_answers.json` L108/L120（`registered_not_consumed`）、`handoff.json` L9（派单逐字含「红线…只登记不消费」） |
| 上述 6 行语境标记 | **6/6 带 `红线`/`只登记`/`registered_not_consumed`**，无一行落在产出语境 |
| `final_scorecard.json` / `verification.json` | 红线族 token **0 处** |
| `consumed_for_forecast` 消费主张 | 4 个 JSON **0 处**；`oracle.md` 3 处均为 J3 判据/M4 变异描述（见 F-2） |
| `params_released=true` | 0 处（`params_released=false` 于 handoff 与 J1/J3 双锁） |
| `open2_ban_observed` | `true`（handoff + `reviewer_answers.red_line_registration`） |
| `classification != buy_side_review_ready` | ✅ 机读 `research_draft_needs_review` |
| 红线值未进任何路径/增量/CAGR/贡献/敏感性产出 | ✅ 相关复算全部标 `review_recompute_not_released` / `mapped_not_released` / `registered_not_consumed` |

**封盘与 store → ✅ 零字节**：`I-11-A/…/hypotheses.json` = `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` / **51,697 B**；store `hypotheses_v3.json` = `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` / **61,231 B**（本人收尾复哈希，含在 14/14 一致内）。
**git 面（只读复测）**：`git -c core.quotepath=false diff HEAD --name-only` → `total=3830`、`non_planning=0`，与 handoff 声明逐字一致；**本人全程未跑 `git status`、无任何 git 写**。

---

## 七、发现清单

| id | 级 | 发现 | 处置建议 |
|---|---|---|---|
| **F-1** | **P2** | **原卡证据路径未落地、也未登记路径映射**：`card_I-13-B` L25 声明四件 `evidence/I-13-B/{investor_walkthrough.md, source_read_receipts.json, scenario_constraints.json, expectation_comparison.json}`，`card_I-13-C` L25 声明四件 `evidence/I-13-C/{delivery_qualification.json, open_items.json, handoff_manifest.json, independent_buy_side_signoff.md}`；本 attempt 顶层 7 件 + `_mut` 37 件 = 44 件，**无 `evidence/` 子目录**。内容其实齐备（五问/回执/scenario/expectation → `reviewer_answers.json`；delivery_qualification/open_items → `final_scorecard.json`；handoff_manifest → `handoff.json`），但 `oracle §2/§5(P1-P12)` 与 `handoff.changed_paths` **均未登记该重映射**；同链 `I-13-A` 已按卡文路径实建 `evidence/I-13-A/`（同句式）⇒ 按卡文证据路径回源会落空、易被后续自动校验误判「证据缺失」。非数值/红线/封盘问题 ⇒ **不构成 P1**。 | 落定时以**追加式**登记 4+4 件路径映射（不回改本 attempt）；`independent_buy_side_signoff.md` 归签核站另出 |
| **F-2** | P3 | 校验器 `J3` 扫描文件面 = 4 个 JSON（`names` 列表），**不含 `oracle.md`**，而 `oracle.md` 中确有 `consumed_for_forecast` 字面 3 处（L156/L187/L198，全为 J3 判据与 M4 变异描述语境、无消费主张）⇒「红线 token 零出现」类表述易被误读为全覆盖。附带机读小疵：`verification.structure_probes.qualification_statuses_distinct` 把布尔 `false` 序列化为字符串 `"False"`（类型混排，仅呈现）。 | 后继校验器把 `oracle.md` 纳入扫描或显式登记豁免；序列化统一类型 |
| **F-3** | P3 | `reviewer_answers.action2_verification.increments` 记「参数带算术增量 **±**17,453,954,143 元（四分部 ±5% 带线性求和）」：5% 线性带与 high 侧逐位和 = `+17,453,954,143`，但 **low 侧逐位和 = `−17,453,954,142`**（逐行 0.25 元级 round-to-nearest 累积）⇒ `±` 单值掩盖 1 元不对称。标 `review_recompute_not_released`、零传播 ⇒ **非 P1**。 | 后继卡改为「high +143 / low −142」双值呈现 |
| **F-4** | P3 | `oracle §4` / 上游 summary L144 的「差 **3.25×/3.26×**」：本人自算 `2,880,807 ÷ 885,141 = 3.2546`、`124,248.63 ÷ 38,175.95 = 3.2546` ⇒ 单一比值 3.25×；`3.26×` 在授权回源面内**无对应推导**。该串系 `REMEDIATION_REGISTER L3951 → I-07-E summary L144 → 本件 oracle §4` 逐字继承，**非本件新推导**，且只在登记语境出现。 | 归上游 P2-1 勘误链，本件只登记、不回改 |
| **F-5** | P3 | `per_model_columns.parameter_slots` 跨行重叠呈现：`ZIJIN_MINERAL_COPPER/GOLD_SALEABLE_VOLUME_FY2027` 同时列在 `ZJ-MIN-M09` 与 `ZJ-VOL-03` 两行（压缩写法），易被读成重复计数；**实际覆盖数仍正确**（13 紫金 + 5 微软 = 18 槽位，与 PM `rows_total=18` 一致），不影响任何分值或结论。 | 落定时注明「跨行引用、非重复槽位」 |
| **F-6** | — | **P1 = 0**：无数值/推导错（§三/§四全部自算通过）、无红线破（§六 6/6 语境）、封盘/store 零字节、`M1` 必红命中（§五 `rc=3(J2)`）。 | — |

---

## 八、边界（没做的事 / 未核实事项）

- **写入面 = 2 个新文件**：`reviewer_report.md` + `reviewer_report.sha256`；attempt 内原 44 件（顶层 7 + `_mut` 37，含 `_mut/**`）**字节与 sha 零改动**（收尾复算与 `handoff.written_files` 6/6、`mutation_summary.before` 逐字一致）；写后复点：顶层 9 件（原 7 + 本 2）、递归 46 件（原 44 + 本 2）。
- **不写卡状态**：无 `status`/`decision`/`decision_sha256` 写入，不产生 `ACCEPT`、不改 `review_pending`、不落 `blocked`；**不代签**（`independent_buy_side_signoff.md` 未出——写入面被限于 2 个新文件，签核件是否由本工位出具由父裁定）。
- **未做的事**：不解除任何 `OPEN-2/3/5/6` 与 `BLOCKED-*`（含 `BLOCKED-6b` 3/4 签、`ruling_6b L110` 重判）· 不放行任何参数 · 不触发 falsifier/自动动作 · 不派 `I-16-A`/`I-12`/`I-16`/`I-17` · 不写五份计划文件 · 不写 `.planning` 之外 · **未跑 `git status`**（只用一次只读 `git diff HEAD --name-only` 复测）· **未联网**（零检索）· 未读 I-12 测试/准确性结果与产品仓/company-wiki 原始报表 · 未重开上游「`not_executable` 槽位 ⇒ 整卡 blocked」字面之争（已登记，归有权方）。
- **`unverified`（无法从产物自证，凭自述登记）**：① 禁联网 / `provenance` 四件未触发；② gate0 三步探针已删无残件；③ 未读 I-12 封存件（只能证明其 sha 被登记、无法证明未打开）；④ 「禁 `git status`」在实现者侧未跑（本人侧同样未跑）。已独立核实的对项：冻结时序 mtime ✅、上游 14/14 与本 run 6/6 复哈希 ✅、`git diff non_planning=0` ✅、变异 8 臂 rc ✅、红线 6 行语境 ✅。
- **两读法之外的裁定**：本人仅裁定本卡上交的「最终报告」读法之争；分类、HB 系列、`BLOCKED-6b` 等既有裁定一并不重开。
