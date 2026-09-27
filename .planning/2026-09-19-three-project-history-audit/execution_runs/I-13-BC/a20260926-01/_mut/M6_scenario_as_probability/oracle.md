# I-13-BC · 合并卡（阶段 B 独答报告 + 阶段 C 评分定级）—— oracle（**先冻结**，产物后写）

> 卡：`execution_v2/card_I-13-BC.md`（2,528 B · sha256 `56d1dad542ca17d13cc820272f3d1717423cde5ef0e5759bf5761fe9b8d96a39`）+ 原卡 `card_I-13-B.md`（1,668 B · `bd5abc55…`）+ `card_I-13-C.md`（1,448 B · `575393ab…`）—— **原卡只读、零字节改动**。
> attempt：`execution_runs/I-13-BC/a20260926-01`（新建）· role：`implementer_i13bc` · 链位：`I-13` 串行链合并执行单元（`I-13-A` 已 `accepted_scoped` 之后）。
> 依赖：`I-13-A/a20260926-01` **`accepted_scoped`**（2026-09-26 21:0x；分类结论 `research_draft_needs_review`、**`HB3=not_established`** 由独立买方复审推翻）+ `I-07-E` summary + `I-11-C` parameter_mapping。
> **本件性质**：合并卡两段连续判断的**实现者**工位（阶段 B 独答走查 → 阶段 C 评分定级）；**不自签**、`status=review_pending`、`releases_nothing=true`、不派 `I-16-A`。
> **冻结时序**：本文件写于 `reviewer_answers.json` / `final_scorecard.json` / `verification.json` / `handoff.json` **之前**；§5 预期与 §6 变异是产物必须逐条对上的**事前判据**，事后不得改写（如需更正 ⇒ 新建 attempt，不覆盖本件）。
> **两段独立冻结点**：§2.A = `oracle_B` 冻结点（阶段 B 判据）；§2.B = `oracle_C` 冻结点（阶段 C 判据）。**任一段 `STOP` ⇒ 整卡 `STOP`（fail-closed，编排层 2026-09-26 21:1x 补充确认）**。

---

## §0 门 0 自探（原始输出，逐字留档）

```
=== GATE0 BEGIN (I-13-BC/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-13-BC\a20260926-01
--- step0 mkdir ---
dir_exists=True
--- step1 write ---
write_ok=True
--- step2 readback ---
readback=gate0 probe I-13-BC a20260926-01 write-readback-delete 2026-09-26T21:18:22.0755186+01:00
--- step3 delete ---
deleted_gone=True
--- step4 sealed sha (read-only) ---
sealed_I-11-A_hypotheses_sha256=f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28
sealed_matches_f2178768=True
sealed_bytes=51697
--- step5 store sha (read-only) ---
store_hypotheses_v3_sha256=b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff
store_matches_b2063ac8=True
store_bytes=61231
--- step6 git diff name-only count (read-only) ---
[stderr] git: warning: in the working copy of '.planning/.../M05/a20260919-01/review.md', CRLF will be replaced by LF the next time Git touches it
（step6 因 pwsh 把 native stderr 升级为终止错误而中断；随即同命令只读重跑：）
git_diff_total=3830
git_diff_non_planning=0
git_diff_exit_ok=True
=== GATE0 END ===
```

- 三步自探（写 / 回读 / 删）= 本会话、零提权、探针已删无残件；封盘与 store 为**只读复哈希**。
- `git diff HEAD --name-only` 只读计数：total=3830（历史/并发写入方均在 `.planning` 内）、**non_planning=0**；**禁 `git status` 未跑**；无 git 写。
- 结论：`gate0_passed=true`；封盘 `f2178768…` 零字节、store `b2063ac8…` 零改动（定稿时再复验一次，见 handoff）。

---

## §1 授权逐字（`authorized_by` 源）

### 1.1 派单（编排层 · 父 `session-19074bf0-0205-4315-af73-9db57597275a`，2026-09-26）
> 「你是编排层派单的**实现者**，开 **`I-13-BC`**（**合并卡**：原 `I-13-B` 独答 + `I-13-C` 评分，owner 批「乙」合并后的执行单元）。依赖 `I-13-A` **已落定 `accepted_scoped`**（2026-09-26 21:0x）。」
> 「**每段独立 `oracle` 冻结点**（`oracle_B.md` + `oracle_C.md` 或单 oracle 内两节）+ **门 0 自探留档** + **变异 ≥3**（含「一栏 PASS 盖另一栏」必须红）。**不放行参数** · **不自签**（复审另派）· **落定父直写** · 封盘 `f2178768…` 零字节。禁五份计划文件 · 禁 `.planning` 外 · 禁 git 写 · **禁 `git status`** · 禁联网。**fail-closed**：最终报告不可得 ⇒ `STOP` 判 `blocked`；任一评分维度证据不足 ⇒ 落 `blocked`/`research_draft_needs_review`（**非 ready**）。**不派 `I-16-A`**（依赖顺序另派）。」
> **红线**：「`124,248.63`（真值 38,175.95）**`OPEN-2` 前只登记不消费**」。
> 父 21:1x 进度确认补充：「**两段各一 oracle 冻结点**，任一段 `STOP` ⇒ 整卡 `STOP`（fail-closed）」（任务与授权不变）。

### 1.2 合并授权（`card_I-13-BC.md` L3，逐字）
> 「**性质**：**owner 授权的执行单元合并**（`2026-09-26` 「先做甲，然后做乙」）—— **不改原两卡判据一字**，作为两段连续判断装进一个执行单元（一次复审 + 一次落定）。」
> L5「**原卡文（判据权威）**：`card_I-13-B.md` · `card_I-13-C.md` —— **只读、零字节改动**。」；L12「**实现者不自签**」；L36「**两段结论同 handoff，`status_authority` 引同一复审报告**」。

### 1.3 `OWNER_DECISIONS.md §三十四`（L745-L780，2026-09-26 15:4x）
- L754 owner 选择「**A**」；L757「改判 `I-11-B` 的开工门槛 —— 以 `MERGE` 七条当前 `5✅ + 2❌` 现状开工；`i11b_unblocked` 的语义从『7/7 才开』改为『**owner 明文许可开工**』」；L758「`C3`/`C5` 的残余**不丢、不隐藏**」。
- L761-L766 硬约束：**oracle 先冻结** / **不放行任何参数** / **不触发任何 falsifier·自动动作** / **实现者不自签 · 独立复审 · 落定走三件套** / `expert_assumption` 必须带敏感性区间 + `equivalent_to_disclosure_basis=false`。
- L769-L775 边界：不解除 `OPEN-2/3/5/6` 与任何 `BLOCKED-*`、不放行参数、**不产生 `ACCEPT`**、不代签。
- L779：「后继卡按卡文依赖顺序**另派**」——本卡 `I-13-BC` 即编排层本轮「另派」机制的行使（`I-13-B`/`I-13-C` 合并为一个执行单元）。

### 1.4 `OWNER_DECISIONS.md §三十七`（L852-L871，2026-09-26 17:5x）
- 授权原话：「**给你授权所有的沙箱操作，不要再问我了**」；覆盖三仓读写 / 系统调用 / 文件落点 / 网络取证。
- 边界：纪律 16/17/18/19/20 继续有效；**生产零未授权改动**；**`git add/commit/push` 不在授权内**。
- 本卡使用面 = **零提权**（全部写入都在本 attempt 目录普通文件）；**网络 = 0**（`provenance` 四件未触发）。

### 1.5 卡文面（原卡逐字要点）
- `card_I-13-B.md` L5「Owner：独立买方reviewer与行业reviewer；依赖：I-13-A。」L9 前提「完整输出已评分，可区分事实、假设、未知。」L13 动作1 五问；L14 动作2「非线性分解方法若未冻结，禁止把交互项随意分配。」；L15 动作3「若无可靠consensus/market-implied数据明确写不可得，不编数字。」；L16 动作4「点开至少一个重要原文来源确认真实内容，摘要或manifest名不代替实际读取。」；L20 停止「报告只能给目标数，无法回答驱动/时点/约束→STOP_INVESTOR_USE。」L21「把低高情景当概率、混淆产量/销量或总净额→STOP_ACCOUNTING。」；L23 验收「具体问题可用最终交付独立回答；缺失需回到对应卡，不能在总结里虚报补齐。」
- `card_I-13-C.md` L5「Owner：主审和独立买方reviewer；依赖：I-13-B。」L9 前提「全部阻断项已逐项判定；资格状态不相互替代。」L13 动作1 三标签；L14 动作2「逐模型列公式、披露、准确性三栏；准确性未证实也必须明写，禁止改成已验证预测。」；L15 动作3「保留source及模型hash、as_of、当前限制、触发更新条件、下次需执行卡和owner。」；L16 动作4「本卡只审阅资格，不自行补写host_receipt或改索引。」；L20 停止「任何未解决blocking issue或缺独立签名→不得正式标ready。」L21「无真实运行/消费/发布证据却只凭receipt文件存在→STOP_PROVENANCE。」；L23 验收「明确区分研究可审阅、部署可用、预测准确性；保留所有未证实事项。」

---

## §2 判据冻结 —— 两段独立 oracle 冻结点

> **回源面声明（V2-4 只读清单）**：本卡派单只读清单 = ① `card_I-13-BC.md` + `card_I-13-B.md` + `card_I-13-C.md` ② 上游 `I-13-A/a20260926-01/`（`buy_side_scorecard.json` · `blocking_issues.json` · `handoff.json`（`accepted_scoped`）· 附 `reviewer_report.md`/`oracle.md` 同 attempt 目录）+ `I-07-E` summary + `I-11-C` `parameter_mapping.json` ③ `OWNER_DECISIONS §三十四`+`§三十七` ④ 红线。
> **定域取尺（回源面声明，同 I-13-A 先例）**：阶段 C 动作1「按**评分规则**」卡内未定义 ⇒ 读 `execution_v2/common_research_cards.md` **L291-L312**（`## I-13评分和硬阻断` 评分规则 + 7 硬阻断 + B01-B08 尺）逐字冻结于 §2.B；卡文 L1（原卡）「先读…[research_cards.md共用规则](common_research_cards.md)…」为其字面授权；另读其 **L11**（M 卡/D-F 资格语义）与 **L156-L163**（sMAPE/CAGR 度量规则）。
> **原文来源实读（card_I-13-B 动作4 要求）**：`execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，sha `b2063ac8…`，**只读**）+ `execution_runs/I-11-C/a20260926-01/parameter_mapping.json`（sha `d542b34d…`）**逐行实际读到**（claim 原文引文见 reviewer_answers.json `source_read_receipts`）。`research_cards.md` 另做定域读（L1-L60 框架结构/参数模板、L521-600 I-12-E 三栏禁令与 I-13 卡原文）以消歧「最终报告」与「一栏 PASS 盖另一栏」判据。**除上述定域读外，清单外零读**（五份计划文件、REMEDIATION_REGISTER 正文、产品仓、company-wiki 原始报表、I-12 测试/准确性结果均未读）。

### 2.A `oracle_B` 冻结点（阶段 B · 独答报告 —— 原卡 `card_I-13-B.md` 判据）

**B-判据1（动作1）五问清单（逐字，逐问作答）**：
1. 增长从何而来 2. 何时确认 3. 最大三项驱动贡献 4. 哪些约束会使高情景失败 5. 哪条证据推翻基情景
— 作答**只用最终报告面**；每问给 `answer` / `answerability ∈ {answerable, partial, not_answerable}` / `evidence_refs`（path:line）；不可答者**明写不可得 + 路由回对应卡**（禁止在总结里虚报补齐）。

**B-判据2（动作2）复核面五项**：收入年路径 · 增量 · CAGR 边界 · 驱动贡献 · 敏感性。逐项给 `review_result` + 复算值（全部标 `review_recompute_not_released`，不得写入任何 released 字段）。
- **非线性分解方法未冻结 ⇒ 禁交互项随意分配**（L14 逐字）：`interaction_allocation = none`（机检判据：产物中不得出现任何驱动贡献份额/百分比归因数字）。
- CAGR 度量按 `common_research_cards.md` L163 逐字：`CAGR=(R_end/R_start)^(1/h)-1`；`R_start>0且h>0` 才可算；零基期记 `undefined` 并报告绝对增量，**不伪造无限增长或 0%**。

**B-判据3（动作3）独立预期对照**：无可靠 consensus/market-implied ⇒ **明写不可得、不编数字**（机检：`consensus` 数字个数 = 0）；检查可预期差异是否来自**口径不同**（总/净额、产量/销量、分部对外 vs 含内部交易、登记除法 vs 公式合成分母）。

**B-判据4（动作4）溯源链 + 原文实读**：答案逐条链 `source→parameter→calculation→output`（≥5 条链）；**点开至少一个重要原文来源确认真实内容**（store `hypotheses_v3.json` claim 原文逐字引文 + sha + 行号），**摘要或 manifest 名不代替实际读取**。

**B-停止判据（逐字）**：
- `STOP_INVESTOR_USE`：报告只能给目标数，无法回答驱动/时点/约束 ⇒ 触发判定见 reviewer_answers.json `stage_b_stop_evaluation`。
- `STOP_ACCOUNTING`：把低高情景当概率 / 混淆产量/销量 / 混淆总净额 ⇒ 三重区分必须显式（机检 J4）。
- **合并卡 L27**：「阶段 B：最终报告不可得 ⇒ `STOP` 划 `blocked`（合格）」+ 父确认「任一段 `STOP` ⇒ 整卡 `STOP`」⇒ **最终报告可得性判定**为本段第一判据（见 reviewer_answers.json `final_report_identification`；严格/宽松两读法均登记，采用读法与推翻条件明写）。

**B-验收（逐字）**：「具体问题可用最终交付独立回答；缺失需回到对应卡，不能在总结里虚报补齐。」

### 2.B `oracle_C` 冻结点（阶段 C · 评分定级 —— 原卡 `card_I-13-C.md` 判据 + `common_research_cards.md` L291-L312 逐字）

**C-判据1（动作1）评分规则（逐字，`common_research_cards.md` L293）**：
> 「任一硬阻断或任一维度0→**blocked**；没有0但存在1→**research_draft_needs_review**；全部八维2且独立签署→**buy_side_review_ready**。总分0–16只展示，不能抵消阻断；该标签不是投资回报保证或准确性认证。」
- 硬阻断 7 条（L295-L301 逐字）与 B01-B08 维尺（L303-L312 逐字）已在 I-13-A oracle §2 冻结，本站**沿用不重定义**；判定输入 = 已落定 `accepted_scoped` 的 `I-13-A` 分值（B01..B08 = 1,1,1,1,1,1,2,1）+ hard_blocks 判定（**`HB3=not_established`** 复审裁定；7 条全 `not_established`）。
- 机械推导（本卡分类唯一推导方式）：`established_hard_blocks=[]` ∧ `zeros_present=0` ∧ 存在 1 的维度=7 ⇒ **`research_draft_needs_review`**（非 ready，缺独立全维签署）。
- **资格状态不相互替代**（卡文 L9）+ 验收「明确区分**研究可审阅 / 部署可用 / 预测准确性**」⇒ 三状态分列字段，禁止互相顶替。

**C-判据2（动作2）逐模型三栏**：每模型列 **公式 / 披露 / 准确性** 三栏；**准确性未证实也必须明写（= `unproven`），禁止改成已验证预测**；「**禁止一栏 PASS 覆盖另一栏不足**」（`research_cards.md` L525 I-12-E 动作3 逐字——即派单点名的「一栏 PASS 盖另一栏」变异判据源）。三栏资格语义（`common_research_cards.md` L11 逐字）：「M卡调度accepted仅指A–C公式/负例资格通过。D–E是实际采用模型的企业披露适配资格，由先行I-10-A完成并供I-11-B及I-07-E消费…F归I-12独立后续…**M accepted绝不等于披露或准确性通过**。」

**C-判据3（动作3）保留清单**：source 及模型 hash · `as_of` · 当前限制 · 触发更新条件 · 下次需执行卡和 owner —— 五项齐、缺项显式登记不可得（不得以「已保留」虚报）。

**C-判据4（动作4）**：仅在上游真实发布/回执流程合格时走其既定发布卡；**本卡只审阅资格，不自行补写 host_receipt 或改索引**（`formal_publication_slot=blocked` ⇒ 不走任何发布卡）。

**C-停止判据（逐字）**：
- 「任何未解决blocking issue或缺独立签名→**不得正式标ready**」（`OPEN-2/3/5/6`、`BLOCKED-6b`（3/4 签）、`gap-U1..U4` 等未解 + 独立签名缺 ⇒ ready 禁止，机检 J1/J5）。
- 「无真实运行/消费/发布证据却只凭receipt文件存在→`STOP_PROVENANCE`」（本站无发布回执主张 ⇒ 判不触发，见 final_scorecard `stop_conditions_evaluated`）。
- **fail-closed（派单）**：任一评分维度证据不足 ⇒ 落 `blocked`/`research_draft_needs_review`（**非 ready**）。

**C-验收（逐字）**：「明确区分研究可审阅、部署可用、预测准确性；保留所有未证实事项。」

---

## §3 上游 sha 冻结（本站**只读复算**，2026-09-26 21:1x；algorithm=sha256）

| # | path（相对 `.planning/2026-09-19-three-project-history-audit/`） | bytes | sha256 | 说明 |
|---|---|---|---|---|
| 1 | `execution_v2/card_I-13-BC.md` | 2528 | `56d1dad542ca17d13cc820272f3d1717423cde5ef0e5759bf5761fe9b8d96a39` | 合并卡文（判据索引） |
| 2 | `execution_v2/card_I-13-B.md` | 1668 | `bd5abc554a230b9c8e6014f28bb444ce8fce290c8dfabad5d424363cd0a69b1d` | 原卡 B（判据权威，只读） |
| 3 | `execution_v2/card_I-13-C.md` | 1448 | `575393ab353a2656e930c2e0b0afb801e0bbd4642fa404b2dce409e9ff8611e6` | 原卡 C（判据权威，只读） |
| 4 | `execution_runs/I-13-A/a20260926-01/handoff.json` | 18472 | `0b466621ff964c8e3347cc96033bf7abd1f800eaf9eda75c3555209ac60a2f97` | 上游落定 `accepted_scoped` |
| 5 | `execution_runs/I-13-A/a20260926-01/evidence/I-13-A/buy_side_scorecard.json` | 15169 | `e74631c72b077a08fe4017fe7fee604923e4095b1c09e60f91128c69a08b290f` | 8 维分值（分类输入） |
| 6 | `execution_runs/I-13-A/a20260926-01/evidence/I-13-A/blocking_issues.json` | 12694 | `c9c6030c7bde35e93b4d54279d0660c31a4bc88ba84491f29db15df3ce9b667e` | 7 条硬阻断判定 |
| 7 | `execution_runs/I-13-A/a20260926-01/reviewer_report.md` | 14143 | `7f0c379c61c75de131c4b87b8fe58f285fb64aafef33f37cba85ac40ccf75d62` | `HB3=not_established` 裁定载体 |
| 8 | `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md` | 26132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` | 完整输出报告面（阶段 B 作答面） |
| 9 | `execution_runs/I-11-C/a20260926-01/parameter_mapping.json` | 54875 | `d542b34d3429f2409417c2d72cb4335ad2fdde5bf1875103b79a0a2abce7192c` | 18 映射行（溯源链） |
| 10 | `OWNER_DECISIONS.md` | 109029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` | §三十四/§三十七 |
| 11 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（**store**，只读） | 61231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 原文来源实读对象，零改动 |
| 12 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘**，只读） | 51697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 零字节改动 |
| 13 | `execution_v2/common_research_cards.md`（定域取尺） | 14736 | `2c6fad2cfba4e096b0f6ed5436158666fdd51265fbc87ad65227f943f27f484b` | L291-L312 评分规则 + L11 + L156-L163 |
| 14 | `execution_v2/research_cards.md`（定域消歧） | 31387 | `5e1e2ffec554b05a27748f0ae3e20ad01fc7dc957555022b83bad2a44d0413fb` | L1-L60 + L521-600 |

**上游落定实测**：`I-13-A` handoff `status="accepted_scoped"`、`status_transition: review_pending -> accepted_scoped`、`status_authority.carrier=reviewer_report.md`（sha 同 #7，`three_way_match=true`）；`score_summary.classification` 实现者原判 `blocked`，**复审裁定 `HB3=not_established` ⇒ 分类机械降为 `research_draft_needs_review`**（`buy_side_scorecard.classification_derivation.overturn_condition` 兑现，reviewer_report §六 机械推导一致）。

---

## §4 ⭐ OPEN-2 红线（**只登记、不消费**）

> 派单逐字：「**红线**：`124,248.63`（真值 38,175.95）**`OPEN-2` 前只登记不消费**」。

- `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 登记除法成立值 = **124,248.63** 元/吨铜当量（109,977,556,345 ÷ 885,141）；store 自写除式真值 = **38,175.95**（按公式合成分母 2,880,807）；差 3.25×/3.26×。I-11-B proposed 三档（118,036.2 / 124,248.63 / 130,461.06）**传播值 = null**；EA-2 系数敏感性（±档 134,919.5 / 113,577.74、两点差分 −10,670.89）**只登记**。
- 本站红线动作：**只登记**该族值与出处（`I-07-E summary §F`、`I-11-C mapping row5 `i11b_proposed_values` 仅存档）；**禁止**进入任何收入路径/增量/CAGR/驱动贡献/敏感性产出/情景/下游映射/复算；`open2_ban_observed=true`。
- 机器可检判据（J3）：本 attempt 全部产物 **不得出现** `consumed_for_forecast` / `params_released=true`；红线族数字只允许出现在带 `registered_not_consumed`/`只登记`/`禁消费`/`存档` 语境的登记字段（`red_line_registration` 块内）；`classification != buy_side_review_ready`。

---

## §5 事前预期（P 系列，两段各自）—— 产物必须逐条复现

| id | 预期（写产物前冻结） |
|---|---|
| P1 | `reviewer_answers.json` 五问（Q1 增长来源/Q2 何时确认/Q3 最大三项驱动贡献/Q4 高情景失败约束/Q5 推翻基情景的证据）逐问齐：`answer` + `answerability` + `evidence_refs`；**Q3 = not_answerable（贡献分解不存在；交互项分配=none）**；Q2 = partial（生效期间可答、收入确认时点缺） |
| P2 | 复核面五项（收入年路径/增量/CAGR 边界/驱动贡献/敏感性）逐项 `review_result` + 复算值全标 `review_recompute_not_released`；CAGR 按 L163 规则（ZJ 基期>0、h=2 可算；MSFT h=1）；`interaction_allocation=none` |
| P3 | `expectation_comparison`：`consensus_availability="unavailable"`（明写不可得）+ consensus/market-implied **数字个数 = 0**；口径差异登记 ≥3（u-N5 语义张力、红线两值口径、总/净额、产量/销量、分部对外 vs 含内部交易） |
| P4 | `source_read_receipts`：**实际打开** store `hypotheses_v3.json`（sha `b2063ac8…`）+ `parameter_mapping.json`（sha `d542b34d…`），逐字 claim 引文 + 行号；`source→parameter→calculation→output` 链 **≥5 条** |
| P5 | `stage_b_stop_evaluation`：`STOP_INVESTOR_USE` 与 `STOP_ACCOUNTING` 均显式判定（含判定依据）；「最终报告」可得性两读法（宽松=最终交付报告面可得 ⇒ 走查执行；严格=须独立成篇正式最终报告 ⇒ 不可得 ⇒ `STOP` 判 `blocked`）**均登记**，采用读法 + 推翻条件明写；情景≠概率、产量≠销量、总≠净三重区分显式 |
| P6 | `final_scorecard.json`：`classification="research_draft_needs_review"` 由规则**机械推导**（`established_hard_blocks=[]` ∧ `zeros_present=0` ∧ 有 1 的维度=7）；三资格状态分列：`research_reviewable=research_draft_needs_review` / `deployment_usable=false` / `forecast_accuracy=unproven`，**互不替代** |
| P7 | `per_model_columns` ≥8 行、每行公式/披露/准确性三栏**齐全**；**accuracy 全部 = `unproven`（明写）**；披露不授予行（`MS-PBP-M05`/`MS-IC-M06`）`row_status != pass`；缺位行（小米 FY2027）显式 |
| P8 | `retained` 五项齐：source hash（三源 doc sha）+ 模型/载体 hash + `as_of=2026-09-18` + 当前限制（gap-U1..U4、u-N4..N6、OPEN-2/3/5/6、BLOCKED-6b、accuracy unproven…）+ 触发更新条件 + 下次需执行卡和 owner |
| P9 | `handoff.json`：`role=implementer_i13bc`、`authorized_by` 逐字、`gate0_passed=true`+原始输出、`open2_ban_observed=true`、`params_released=false`、`status=review_pending`、`implementer_signed=false`、`releases_nothing=true`、`written_files`（bytes+sha）、`git_diff_non_planning=0` |
| P10 | 封盘 `f2178768…` 零字节改动（定稿复哈希）+ store `b2063ac8…` 零改动；`not_dispatched` 含 `I-16-A`（及 I-12/I-16/I-17） |
| P11 | 变异：绿臂 rc=0；红臂 ≥3 且**「一栏 PASS 盖另一栏」必须红**；每臂违例具名（J1..J6）；原件与上游字节不动（before/after 比对） |
| P12 | 两段结论同 handoff（`status_authority` 预留引同一复审报告）；`implementer_signed=false`；不产生 `ACCEPT` |

---

## §6 变异清单（≥3，红绿双向；**副本执行，原件字节不动**）

**校验器**：`_verify_i13bc.py`（python 3.13，只读校验）。**exit code legend（冻结）**：
`0 = ALL_INVARIANTS_OK`；`1 = harness 失败（文件缺失/JSON 不可解析）`；`2 = 本校验器不产生`；`3 = 不变量违例（具名 J1..J6）`。

不变量：
- **J1 release/authority lock**：`handoff.params_released=false` ∧ `implementer_signed=false` ∧ `releases_nothing=true` ∧ `status=review_pending` ∧ `gate0_passed=true` ∧ `git_diff_non_planning=0` ∧ `open2_ban_observed=true`；`final_scorecard.qualification.deployment_usable=false` ∧ `classification != buy_side_review_ready`。
- **J2 三栏独立（一栏 PASS 盖另一栏 = 红）**：`per_model_columns` 每行公式/披露/准确性三栏非空；**accuracy 全部 = `unproven`**（出现 verified/proven/已验证 ⇒ 红）；任一栏不足（`not_granted`/`missing`/`unproven`）时 `row_status` 不得为 pass/qualified、不得以公式 accepted 顶替；全表不得出现「一栏PASS覆盖另一栏」形态主张。
- **J3 open2 红线禁消费**：无 `consumed_for_forecast`；`params_released=true` 零处；红线族数字只在 `registered_not_consumed` 语境；`open2_ban_observed=true`。
- **J4 阶段 B 完整 + 零编造**：五问齐且各带 answerability/evidence；`consensus` 数字 = 0 且 `availability` 明写不可得；`interaction_allocation=none`（不得有贡献份额/归因百分比数字）；情景带不得标概率/置信；产量/销量、总/净额区分标记在位。
- **J5 分类机械一致**：`classification` == 由（established 硬阻断数、0 的个数、是否存在 1）按 §2.B 规则机械推出的标签；三资格状态分列齐全且不互相顶替；存在未解 blocking issue 或缺独立签名时不得标 ready。
- **J6 上游 sha**：§3 表 14 件逐件复算 == 记录值（含封盘 `f2178768…` 与 store `b2063ac8…`）。

| id | 变异（在 `_mut/Mx` 副本上） | 期望 |
|---|---|---|
| GREEN | 原件五件 + 上游 14 件 | rc=0 `ALL_INVARIANTS_OK` |
| **M1**（**一栏 PASS 盖另一栏**，派单点名） | `final_scorecard.json` → 把 `MS-PBP-M05` 行 `disclosure` 由 `not_granted` 改 `granted` 且 `row_status` 改 `pass`（公式栏 PASS 盖过披露不授予） | rc=3 违例含 **J2** |
| M2 | `final_scorecard.json` → 某行 `accuracy` 由 `unproven` 改 `verified`（禁改写为已验证预测） | rc=3 违例含 **J2** |
| M3 | `final_scorecard.json` + `handoff.json` → `classification` 改 `buy_side_review_ready`、`deployment_usable=true` | rc=3 违例含 **J5**（并触发 **J1**） |
| M4 | `handoff.json` → `params_released` `false`→`true`（并塞 `consumed_for_forecast`） | rc=3 违例含 **J1**（并触发 **J3**） |
| M5 | `reviewer_answers.json` → 编造 consensus 数字 + Q3 驱动贡献份额数字 | rc=3 违例含 **J4** |
| M6（备用） | `reviewer_answers.json` → 情景带改标「80% 概率」+ 产量/销量互换 | rc=3 违例含 **J4** |

绿臂在定稿（handoff 写完）后**再跑一次**（`GREEN_FINAL`），证明原件未被红臂污染。

---

## §7 边界（本 unit 不做什么）

不放行任何参数（`params_released=false`）· 不触发任何 falsifier/自动动作 · **不自签**（`implementer_signed=false`；`independent_buy_side_signoff` 归独立买方 reviewer 另派，本站不产签核件）· 不产生 `ACCEPT`、不改任何 `status`/`decision`/`decision_sha256` · 封盘 `f2178768…` 零字节 · store `b2063ac8…` 零改动 · **不派 `I-16-A`**（也不派 I-12/I-16/I-17，依赖顺序另派）· 不写五份计划文件 · 不写 `.planning` 之外 · 禁 git 写、**禁 `git status`**（只用 `git diff HEAD --name-only` 只读计数）· 禁联网（`provenance` 四件未触发）· 不读 I-12 测试/准确性结果、不读产品仓/company-wiki 原始报表 · 红线值只登记不消费 · 交互项不分配 · 残余不隐藏（fail-closed）· 不自行补写 `host_receipt` 或改索引。
