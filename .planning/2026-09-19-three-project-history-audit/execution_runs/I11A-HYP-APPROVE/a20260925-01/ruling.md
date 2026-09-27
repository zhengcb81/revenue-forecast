# I-11-A `hypotheses.json` 命题裁定 · 行业 reviewer（非实现者）

- 卡：`I-11-A` · 被审 attempt（**全程只读**）：`execution_runs/I-11-A/a20260919-01`
- 本载体（**新建**）：`execution_runs/I11A-HYP-APPROVE/a20260925-01/`（`hypotheses_v2.json` · `ruling.md` · `handoff.json`）
- 角色：`industry_reviewer_non_implementer`（行业 reviewer · 紫金覆盖；即被审文件中 `decision.professional_reviewer = "行业 reviewer（紫金覆盖）"` 的指派对象）
- **本文件只裁 1 条命题**：下标 `0` 的 `H-CN-ZIJIN-SEG-01` 是否**够格到 `approved_frozen`**；其余 7 条**一字不改**
- 取证/复算时间窗（UTC）：仅本地读取与复算，登记时点 `2026-09-25T22:17:51Z`；**本工位网络请求数 = 0**
- 本文件**不是** I-11-A 验收，**不放行**任何参数与阈值，**不解除**任何 `BLOCKED`，**不产生** `I-11-B` 的 ACCEPT

---

## ① 身份与授权链（逐字，不由转述代替）

### 1.1 我是谁

| 项 | 值 |
|---|---|
| `role` | `industry_reviewer_non_implementer` |
| 是否实现者 | **否**。我未参与 `I-11-A` 任何实现步骤；本工位 `handoff.implementer_signed = false`；**不代签**其他角色的任何一项 |
| 写入面 | 仅 `execution_runs/I11A-HYP-APPROVE/a20260925-01/` 下三个文件；`.planning` 之外**零写入**；封盘 attempt **零字节改动**；**零 git 写**（未执行 `git status`，只执行 `git diff HEAD --name-only` 计数）；**零联网** |

### 1.2 授权链 = `i11b_unlock_conditions[0]`（`execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` L118，逐字）

> 「≥1 条命题在新版本上由非实现者 reviewer 写入 `decision.decision_sha256` 并达 `approved_frozen`（或 owner 明文改判开工门槛）」

同文件 `i11b_reason`（L116，逐字节选）：

> 「两半合起来产生的 approved_frozen 命题 = 0、可放行参数 = 0、可触发阈值 = 0：……被审 attempt 仍为 6 pending + 2 unquantified / approved_frozen=0（handoff L298、L321；validation_report L13-L18），且 OPEN-2/3/5/6 的取值与证据仍全部 BLOCKED。**规则已立 ≠ 参数已批**：card_I-11-B.md L9 要求『I-11-A命题已批准』、L23 要求『专业reviewer签署后方可进入forecast』，当前一条都不满足。」

同文件 `i11b_unblocked = false`、`i11b_verdict = "BLOCKED"`（L114–L115）**原样保留**：本工位只补 C1 这一条主路径，**不宣称** C1 之外的任何条件已满足。

### 1.3 卡文与协议对本角色的职权（逐字）

- `execution_v2/card_I-11-A.md` **L5**：「Parent：I-11；状态：planned；Owner：行业reviewer主责，弱模型可整理证据；依赖：I-00-B、I-00-C。」
- 同 **L9**：「基期公司/分部/信息日确定；只用可核验来源。」
- 同 **L16**（动作 4，逐字）：「行业reviewer审定可观测性、时间滞后及是否已在基期/其他driver反映。」
- 同 **L23**（验收，逐字）：「每命题有可追溯来源、机制、driver、时点、双计排除和明确unquantified/approved状态；不要求全部强行量化。」
- `execution_v2/card_I-11-B.md` **L9**：「I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。」
- 同 **L23**：「参数幅度、相关性及收入增量能够复核；专业reviewer签署后方可进入forecast，不等同准确性通过。」
- `execution_v2/START_HERE.md` **L26**：「| review_pending | 正反例/恢复/差异证据齐全 | 实现者不能自签accepted |」；**L36**：「……专业决策未定先blocked。」；**L47**：「……审查意见至少包含选择、理由、反例、兼容影响、恢复规则、拒绝的替代方案。不得用“按最佳实践”代替决定。」
- 被审 attempt `decision.md` **DEC-3**（L79–L83，逐字）：「选 (c)。卡正文的验收要求"明确 unquantified/approved 状态"，因此 approved 必须存在于**状态空间**；但 START_HERE 第 26 行规定"实现者不能自签 accepted"，所以本 attempt 的 `approved_frozen` 计数必须为 0，**由行业 reviewer 在独立审查中写入**。」
- 同文件 **L418**：「不写 `approved_frozen` 命题——属行业 reviewer；」
- 同文件 **L403**（OPEN-7 行，逐字）：「| OPEN-7 | 命题 1/6 的分部集合是否就是 FY2027 的最小建模块 | 行业 reviewer | 否 | 分部集合变更时的重建工作 |」
- `OWNER_DECISIONS.md` **§十一 L147**（owner 2026-09-20 第三批签字行，逐字节选）：「……I-11-A OPEN-1 允许 pdftotext 降级为交叉核对／**OPEN-7 分部集合维持**／OPEN-8 接受择优规则／OPEN-9 升级超集／OPEN-10 采用最新文件 mtime | 逐项登记 |」
- `OWNER_DECISIONS.md` **§二十四 L502–L503**（逐字，逐条适用于本卡）：「**「授权」是许可不是动作**：四项均**不产生任何 ACCEPT、不解除任何 BLOCKED、不改任何 status**；`I-11-B` 仍 BLOCKED（解锁 7 条条件未满足）。」「**不得把本节选择膨胀为「所有结论」**……」

⇒ **我 = 上述授权链所指的非实现者行业 reviewer；我只就命题 `[0]` 是否够格 `approved_frozen` 出具本裁定。**

> `OWNER_DECISIONS.md` 本读取时点 sha256 `fe26a2dbacc42a1e7ca252c08c6d7c7538360883dbc0a9cd072fb4af526d9bbe`（76,005 B，含 §二十四 与 §二十五 之后的追加）——与 `I11A-OPEN11-IND/ruling.md` L52 记录的更早时点 `093cb6864c7c05206e5a1b9e1c7aaee1cd769752a5644b1bd7244135cc2a5020`（67,435 B）不同，差异来自 owner 后续追加；**以本时点为准，不回改任何前批载体**。

---

## ② 命题原文逐字（`execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` 下标 `0`）

- `hypothesis_id`：`H-CN-ZIJIN-SEG-01`
- `claim`（逐字）：

> 「紫金矿业合并营业收入的构成由四个报告分部的**对外**销售收入相加得到；分部收入口径为对外销售收入，不得把含内部交易的分部总计直接相加。」

- `state`（裁前）：`pending_professional_decision`
- `state_reason`（逐字）：

> 「算术恒等式已在 A1/A2/A3 用有理数精确复算（差=0），但'四个分部是否为 FY2027 仍适用的最小建模块'需行业 reviewer 裁定」

- `decision`（裁前，逐字）：

```json
{
  "professional_reviewer": "行业 reviewer（紫金覆盖）",
  "decision": "pending",
  "reason": "算术恒等式已在 A1/A2/A3 用有理数精确复算（差=0），但'四个分部是否为 FY2027 仍适用的最小建模块'需行业 reviewer 裁定",
  "decision_sha256": null
}
```

- `source` 关键字段（逐字）：`doc_id = CN-ZIJIN-AR2025`；`doc_sha256 = 01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d`；`strategy = page_text`；`page_index_basis = pdf_leaf_1based`；`page_span = "327-328"`；`anchor_text = "对外销售收入"`；`source_type = company_disclosure`；`independence_group = ZIJIN-AR2025`；`as_of = 2026-09-18`
- `observation.raw_value`（逐字）：`"109,977,556,345; 165,858,644,874; 29,212,610,830; 44,030,270,803"`
- `falsifier`（逐字，四项）：
  - `observable`：「下一期年报分部报告附注中四分部'对外销售收入'之和与该年合并利润表营业收入之差」
  - `threshold`：「0（算术恒等式，允许披露四舍五入引入的 |差| ≤ 1 元）」
  - `threshold_basis`：`arithmetic_identity`
  - `observation_date`：「2027年年度报告披露日（预计2027-03前后）」
  - `revert_rule`：「若恒等式不再成立，停止把四分部对外收入直接相加作为合并收入路径；回到上一已证实口径并把差异登记为口径桥缺口，不改历史快照。」
- `refuted_by`（逐字，3 条）：「若下一年度出现第五个报告分部或分部重组，四分部加总不再等于合并数（须重建分部映射）」／「若'对外销售收入'行的定义被改为含内部交易，则恒等式失效（须改用抵销桥）」／「若年报把分部合计改为税后或扣除非经常项目口径，则与合并营业收入不同源」
- `double_count_exclusion`（逐字）：「同一集团收入不得同时以'分部对外收入合计'与'含内部交易分部总计'两种口径计入；本命题只允许前者。内部销售收入 234,970,146,412 元（2025年）只能出现在抵销桥中，不得作为任何参数的收入基期。」
- `machine_verifiable`：`["A1","A2","A3"]`；`reviewer`：`行业 reviewer（紫金覆盖）`；`three_qualifications`：`formula = not_applicable_here / disclosure_adaptation = not_granted / accuracy = not_granted`
- `parameter_mapping` 裁前状态：`original_value = "349,079,082,852"`，`low = null`，`base = null`，`high = null`，`effective_period = "FY2025（基期）"`（**本裁定不改其中任何一个字段**）

**待裁问题（`state_reason` + `OPEN-7` 合起来只有一个）**：算术恒等式已复算差=0（我不采信该自述，见 §③ 自行复算），**「四个分部是否为 FY2027 仍适用的最小建模块」需行业 reviewer 裁定。**

---

## ③ 我独立复核了什么（读原文件、自己算，不引用实现者自述作证据）

### 3.1 我逐字读过并重新哈希的文件（sha256 为我本工位实测）

| 文件（相对 `.planning/2026-09-19-three-project-history-audit/`） | sha256（实测） | 字节 | 我读了什么 |
|---|---|---|---|
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 51,697 | **全文 906 行**（8 条命题全读）；实测 `decision_sha256` 出现 8 次全为 `null`、`approved_frozen` 出现 0 次、`state` = 6×`pending_professional_decision` + 2×`unquantified` |
| `execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` | `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878` | 21,808 | **全文 285 行**（`i11b_unlock_conditions[0]`、`i11b_reason` 逐字见 §①）；并**独立复算**其 `source_rulings` 登记的 3 个 sha：`I11A-OPEN-ACCT/ruling.md` = `f3040df0…329c2` ✅、`I11A-OPEN-IND/ruling.md` = `8bc685a4…7f4b` ✅、`merge_ruling.md` = `d214bab…5c1` ✅（**3/3 与我实测一致**） |
| `execution_runs/I11A-OPEN11-IND/a20260924-01/ruling.md` | `c02e255f67f76be9c0a38569454b64cd93f8469d9fc5244e6da2ce7cfc3bb95d` | 38,930 | **全文 325 行**（R1–R6、§3.4 反例、§3.8「四要件 0/4 ⇒ 不授予 approved_frozen」） |
| `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md` | `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2` | 37,355 | L215–L274（A-6.1 / A-6.2 / A-6.3 给数四要件，逐字见 §4.3） |
| `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` | `8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b` | 39,207 | L51（逐字：「OPEN-7（分部集合是否最小建模块，owner 已裁"维持"）……」） |
| `OWNER_DECISIONS.md` | `fe26a2dbacc42a1e7ca252c08c6d7c7538360883dbc0a9cd072fb4af526d9bbe` | 76,005 | L140–L149（§十一）、L490–L505（§二十四） |
| `execution_v2/card_I-11-A.md` | `9567b8dd81411092a87f1b66304f6f038725a085d7184ea9a353ed409a997df1` | 1,433 | 全文 25 行 |
| `execution_v2/card_I-11-B.md` | `38ff2907acb627f3d5f6a97ca386a17551329ad3909720e84463a185154ae87c` | 1,672 | 全文 25 行（L9 / L23 逐字见 §①） |
| `execution_v2/START_HERE.md` | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` | 20,436 | L1–L55（L26 / L36 / L47） |
| `execution_runs/I-11-A/a20260919-01/decision.md` | `e9c96f02118514b8596620b3c0e235a797747fcd3bcf59d1a0fd20aa70166951` | 29,756 | L55–L184（DEC-3 / DEC-6）、L330–L421（DEC-12 / 开放项表 / L418） |
| `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py` | `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac` | 28,549 | L1–L40、L70–L139、L140–L255、L255–L334、L400–L504（`approved_frozen` 机器判据与阈值一致性判据，见 §4.4） |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/extract/P1_zijin_pages.json` | `f1909d136d05bde0230e7fd2761c079026f9a132dd7123109bd7ca7bab85e2cf` | 89,754 | L155–L168（`pdf_page = 326/327/328` 三页原文） |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json` | `3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf` | 13,863 | 只哈希（供校验器输入复跑） |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/validation_report.json` | `dc014e7e7a5699f5692d60d3e7cf76b782d1c64ef7668d5104e077290cb7c9b8` | 5,341 | 只哈希 |

**外部产品仓（company-wiki，只读；我对其只做 `Get-FileHash` 与 `pdftotext … -`（输出只到管道），未写入任何字节）**

| 文件 | sha256（我实测） | 字节 |
|---|---|---|
| `companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf` | `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d` | 79,925,886 |
| 同目录 `2025-03-21_cninfo_1222870413_紫金矿业集团股份有限公司2024年年报报告.pdf` | `004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89` | 32,100,114 |
| 取文工具 `C:\Program Files\Git\mingw64\bin\pdftotext.exe` | `252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0` | 1,537,966 |

（前两行 sha 与 `hypotheses.json` 的 `source.doc_sha256` 逐字相同 ⇒ 我核到的正是该命题引用的同一份文件；pdftotext sha 与 `OWNER_DECISIONS.md` L101 登记值相同。）

### 3.2 我自己做的精确复算（PowerShell `[int64]` 整数加减，非引用他人结果）

命题 `[0]` 的恒等式在**三个财政年度、两份年报**上双路径复算，**6/6 差 = 0**：

| 期 | 路径 A：Σ(四分部对外销售收入) | 路径 B：Σ(分部总计) − 抵销 | 公布的合并营业收入 | 差 |
|---|---|---|---|---|
| FY2025 | 109,977,556,345 + 165,858,644,874 + 29,212,610,830 + 44,030,270,803 = **349,079,082,852** | 584,049,229,264 − 234,970,146,412 = **349,079,082,852** | 349,079,082,852 | **0 / 0** |
| FY2024 | 74,089,365,354 + 181,141,823,725 + 29,386,475,085 + 19,022,292,989 = **303,639,957,153** | 476,803,084,126 − 173,163,126,973 = **303,639,957,153** | 303,639,957,153 | **0 / 0** |
| FY2023 | 62,178,809,312 + 152,879,445,220 + 48,296,807,364 + 30,048,180,982 = **293,403,242,878** | 421,391,715,510 − 127,988,472,632 = **293,403,242,878** | 293,403,242,878 | **0 / 0** |

「公布的合并营业收入」在**同一文件的另外三个独立位置**逐年逐字出现（我逐页抽到，见 3.3）：

- FY2025 年报 leaf 15「近三年主要会计数据」：`2025 年 349,079,082,852`、`2024 年 303,639,957,153`、`2023 年 293,403,242,878`
- 同文件 leaf 43「利润表相关科目变动分析表」：`本期数 349,079,082,852 252,288,843,039`／`上年同期数 303,639,957,153 241,776,168,937`
- 同文件 leaf 252 附注五.54「(2) 营业收入分解信息」：报告分部列 `矿产品/冶炼产品/贸易/其他`，`2025年 合计 349,079,082,852`、`2024年 合计 303,639,957,153`
- FY2024 年报 leaf 15 / leaf 40 / leaf 265：同构给出 `303,639,957,153`（2024）与 `293,403,242,878`（2023）

⇒ 恒等式不是「单表自证」：**分部报告附注、营业收入分解附注、主要会计数据、利润表科目分析**四处独立位置互相咬合，且跨两份年报成立。

### 3.3 我自己做的原文抽取（命令 + 逐字引文；输出只到管道，未落任何文件）

取文命令形如 `pdftotext -enc UTF-8 [-layout] -f <leaf> -l <leaf> <pdf> -`（工具 sha 见 3.1）。全篇扫描用同工具逐页输出并按换页符计页（FY2025 年报 353 页 2.7 s 扫完；FY2024 年报 380 页）。

**关键逐字引文 1 —— FY2025 年报 leaf 325（页脚 `- 218 -`），`十六、其他重要事项 / 1. 分部报告` 开篇：**

> 「根据本集团的内部组织结构、管理要求及内部报告制度，本集团的经营业务划分为矿产品分部、冶炼产品分部、贸易分部和其他分部共四个报告分部。每个报告分部为单独的业务分部，提供不同的产品和劳务。」
> 「本集团管理层已按照上述经营分部分配资源和评估分部的业绩。因此，本年度及上年度的分部报告已按照上述方式呈列。」
> 「本集团有如下4个报告分部：(1) 矿产品分部的产品为矿山产铜、矿山产金、矿山产锌精矿、矿山产铅精矿、矿山产银、矿山产锂、铁精矿、钨精矿、钼精矿，涉及集团矿山企业的各个生产环节，如采矿、选矿和冶炼；(2) 冶炼产品分部的产品为冶炼产铜、冶炼加工金银、冶炼产锌锭、硫酸、电池级碳酸锂；(3) 贸易分部主要为阴极铜等大宗商品的贸易收入；(4) “其他”分部主要包括环保收入、铜管、铜板带、氰化亚金钾等销售收入。」

**关键逐字引文 2 —— FY2025 年报 leaf 326（页脚 `- 219 -`），`2025年` 分部收入表（`-layout` 版式）：**

> `2025年  矿产品  冶炼产品  贸易  其他  抵销  合计`
> `对外销售收入 109,977,556,345  165,858,644,874  29,212,610,830  44,030,270,803  -  349,079,082,852`
> `内部销售收入 28,294,116,611  23,825,234,421  141,308,414,947  41,542,380,433  (234,970,146,412)  -`
> `总计 138,271,672,956  189,683,879,295  170,521,025,777  85,572,651,236  (234,970,146,412)  349,079,082,852`

**关键逐字引文 3 —— 同文件 leaf 327（页脚 `- 220 -`），`2024年` 表：**

> `对外销售收入 74,089,365,354  181,141,823,725  29,386,475,085  19,022,292,989  -  303,639,957,153`
> `总计 95,360,053,889  201,367,589,325  134,062,842,189  46,012,598,723  (173,163,126,973)  303,639,957,153`

**关键逐字引文 4 —— FY2024 年报 leaf 351（`分部报告`）：**

> 「于2024年，本集团根据最新的内部组织结构、管理要求及内部报告制度，决定调整公司分部报告的列报口径，确定了矿产品分部、冶炼产品分部、贸易分部和其他分部共四个报告分部。每个报告分部为单独的业务分部，提供不同的产品和劳务。」
> 「本集团管理层已按照上述修订的经营分部分配资源和评估分部的业绩。因此，本年度及上年度的分部报告已按照上述方式呈列。」

同文件 leaf 352 / leaf 354 给出 2024 年与 2023 年的四分部「总计 − 抵销」行，leaf 265 给出四分部对外收入分解；三者与 3.2 表中 FY2024 / FY2023 数字逐字一致。

**双路径互证（关键）**：被审 attempt 自己的抽取件 `P1_zijin_pages.json`（`pdf_page = 327/328`，sha 见 3.1）中同两页文字与我用 `pdftotext` 独立抽到的 `leaf 326/327` **逐字相同**（同一 `对外销售收入` 行、同一四个数与合计）。⇒ 上述数字**同时存在于实现者的抽取路径与我的独立抽取路径**，不是任何一方的自述。

> **页号口径登记（对 `page_span = "327-328"` 的如实说明）**：被审件用的页索引比 `pdftotext` 的 leaf **大 1**（被审 `pdf_page 327` = `pdftotext leaf 326`，页脚都是 `- 219 -`；被审 `328` = `327`，页脚 `- 220 -`）。这与 `decision.md` DEC-2 / `OPEN-8`（`OWNER_DECISIONS.md` L147「OPEN-8 接受择优规则」）已登记的 offset=+1 一致，也与 `I11A-OPEN11-IND/ruling.md` R2-5 实测的 leaf/打印页跨期漂移一致 ⇒ **跨期定位必须用 `anchor_text`，不得用页号**（我两处引文均以 `anchor_text` 与表内数值定位）。

### 3.4 我**没有**把什么当证据

1. **不引用实现者自述**：`state_reason`「已在 A1/A2/A3 用有理数精确复算（差=0）」与 `machine_verifiable: ["A1","A2","A3"]` **不作为**我的证据；§3.2 的 6 条等式是**我本工位重算**的。
2. **不引用 `validation_report.json` 的结论**（只登记其 sha）；`approved_frozen` 的机器判据是我**读校验器源码**（`validate_hypotheses.py` L292–L302）得到的，不是读报告得到的。
3. **不用外部网络**：本工位 0 次网络请求；外部二手转述一律不用。
4. **不把 pdftotext 当「唯一来源」**：按 `OWNER_DECISIONS.md` T1-14，pdftotext 只是交叉核对路径；本裁定的每个数字都有**两条独立抽取路径**（被审 `P1_zijin_pages.json` vs 我的 `pdftotext`）或**四个独立披露位置**（§3.2）支撑。

---

## ④ 结论与 `decision_sha256` 求值方式

### 4.1 结论：**`approved_frozen`（够格）** —— 三段论证

**（一）可观测、时间滞后、是否已在基期/其他 driver 反映（`card_I-11-A.md` L16 的三项审定）**

- 可观测：`falsifier.observable` 指向「下一期年报分部报告附注四分部对外收入之和 − 该年合并利润表营业收入」，`source_route` 可定位到具体附注；我在**当期**已经把同一观测量在四个披露位置复算闭环（§3.2），即该观测量**当下可复算**。
- 时间滞后：`observation_date = 2027年年度报告披露日（预计2027-03前后）`，滞后明确，且命题未声称已观测到 FY2027。
- 已在基期反映：`double_count_exclusion` 明确把内部销售收入 `234,970,146,412` 元限制在抵销桥内、不得作收入基期；`H-CN-ZIJIN-ELIM-05`（下标 4）以叙述性约束覆盖抵销侧；两者口径互斥，无双重计算。（`H-CN-ZIJIN-ELIM-05` 本身**未被我裁定**，见 §⑦-2。）

**（二）`state_reason` 里唯一的专业问题——「四个分部是否为 FY2027 仍适用的最小建模块」——证据充分**

1. **发行人自身在被引文件里就把它写死了**：FY2025 年报（`doc_sha256 = 01819e1c…`，正是本命题 `source.doc_sha256`）`十六、1.分部报告` 开篇逐字「……划分为矿产品分部、冶炼产品分部、贸易分部和其他分部**共四个报告分部**」＋「本集团有如下**4个报告分部**」并逐条列举产品范围（§3.3 引文 1）。这不是我的推断，是披露原文。
2. **连续三期数值闭环**：FY2023/FY2024/FY2025 三年，四分部对外收入之和恒等于当年合并营业收入，**两条路径差均为 0**（§3.2）——即「四分部 = 最小完备划分」在**三个连续年度**上可复算，不是单期巧合。
3. **跨文件一致**：FY2024 年报（`004f733e…`）独立给出同一四分部口径与同一数值（§3.3 引文 4），并逐字写明「本年度及上年度的分部报告已按照上述方式呈列」。
4. **owner 已裁 `OPEN-7`**：`OWNER_DECISIONS.md` §十一 L147「OPEN-7 分部集合维持」；`I11A-OPEN-IND/ruling.md` L51 亦登记「OPEN-7（分部集合是否最小建模块，owner 已裁"维持"）」。
5. **反面事实已被命题自己覆盖**：发行人**确实在 2024 年变更过分部口径**（§3.3 引文 4 逐字「决定调整公司分部报告的列报口径」）。这一事实**正是** `refuted_by[0]`「若下一年度出现第五个报告分部或分部重组……」与 `falsifier.revert_rule` 存在的理由——风险已显式登记且有回退路径，**不是**把风险藏起来才判 `approved_frozen`。

**（三）`approved_frozen` 的机器判据（读源码，非读报告）**：`validate_hypotheses.py` L292–L302 要求 `reviewer` 非实现者标记且长度 ≥ 8、`decision.decision_sha256` 非空；L233–L237 要求 `threshold_basis = professional_judgement_required` 的命题**必须**保持 `pending`——命题 `[0]` 的 `threshold_basis = arithmetic_identity`，**不在**该禁止之列；`reviewer = "行业 reviewer（紫金覆盖）"`（12 字符，不在 `IMPLEMENTER_MARKERS` 黑名单）。§4.4 我用同一校验器实跑了正例。

### 4.2 结论落到文件

- `state`：`pending_professional_decision` → **`approved_frozen`**
- `decision.decision`：`pending` → **`approved_frozen`**
- `decision.reason`：写入本节结论（含作用域与不授予清单）
- `decision.decision_sha256`：**我本工位计算**，求值方式见 4.3
- `state_reason`：改为如实反映「已由非实现者行业 reviewer 裁定并冻结」（原 `state_reason` 是**待裁**状态的理由，若不改会与 `approved_frozen` 自相矛盾；原文全句抄录保留在本文件 §②）
- 其余 7 条：`state`、`decision`、`decision_sha256`、**全部字段逐字节不变**

### 4.3 `decision_sha256` 的求值方式（可独立复算）

**preimage = UTF-8（无 BOM）字节串 = `<claim 原文逐字>` + `0x0A` + `<下方 BEGIN/END 标记之间的那一行裁定正文>`，无尾随换行；`decision_sha256 = SHA-256(preimage)` 的小写十六进制。**

- `<claim 原文逐字>` = 被审 `hypotheses.json` 下标 `0` 的 `claim` 字段值（原文见 §②，一字未改）；
- `<裁定正文>` = 下方标记块内**单独一行**（我写入时与写入后复取均逐字相同，写入后由我重新提取复算过一次，两次结果一致）：

--- BEGIN RULING TEXT ---
RULING｜H-CN-ZIJIN-SEG-01 → decision=approved_frozen（裁定人：非实现者行业 reviewer（紫金覆盖），作用域仅限本命题命题体，不含任何阈值数值与参数放行）。裁定一：算术恒等式「合并营业收入 = Σ(矿产品/冶炼产品/贸易/其他 四报告分部的对外销售收入)」在 FY2023、FY2024、FY2025 三个连续财政年度、两份本地年报上经本 reviewer 以披露原值整数独立复算，路径 A（Σ对外销售收入）与路径 B（Σ分部总计−抵销）差均等于 0，且与同一文件内「近三年主要会计数据」营业收入、附注五.54「营业收入分解信息」合计、利润表相关科目变动分析表三处独立位置逐年逐字一致。裁定二：「四个报告分部是 FY2027 仍适用的最小建模块」成立，依据为发行人自身披露——FY2025 年报（doc_sha256 01819e1c…）十六、1.分部报告 逐字「本集团的经营业务划分为矿产品分部、冶炼产品分部、贸易分部和其他分部共四个报告分部」「本集团有如下4个报告分部」，FY2024 年报（004f733e…）分部报告 逐字「于2024年，本集团根据最新的内部组织结构、管理要求及内部报告制度，决定调整公司分部报告的列报口径，确定了矿产品分部、冶炼产品分部、贸易分部和其他分部共四个报告分部」「本年度及上年度的分部报告已按照上述方式呈列」，叠加连续三期双路径差为 0 的数值闭环与 owner §十一 L147「OPEN-7 分部集合维持」；发行人曾于 2024 年变更分部口径这一事实已由本命题 refuted_by[0] 与 falsifier.revert_rule 显式覆盖，不因冻结而消失。裁定三：本签署按 fail-closed 收口——不审定任何 threshold（falsifier 的「|差| ≤ 1 元」容差仍属会计面 BLOCKED-6b，A-6.3 四要件由会计面独立判断）、不放行任何 parameter（low/base/high 维持 null、original_value 维持 FY2025 披露值）、不解除 OPEN-2/3/5/6 与 BLOCKED-2a/2b/3a/3b/6a/6b/6c、不构成 I-11-A 验收、不产生 I-11-B 的 ACCEPT；触发 falsifier 或 refuted_by 任一条件时按 revert_rule 回退并新建版本，本快照与本裁定记录不改。
--- END RULING TEXT ---

**复算步骤（任何人都能重跑）**：① 读被审 `hypotheses.json` 取下标 0 的 `claim`；② 从本文件取出两个标记之间的那一行（不含标记行）；③ 拼 `claim + "\n" + ruling_text`；④ 算 SHA-256，应等于 `hypotheses_v2.json` 中 `hypotheses[0].decision.decision_sha256`，也等于 §4.5 的值。

### 4.4 我用冻结校验器实跑的结果（只读调用，不写封盘目录）

命令形态：`python -B -X utf8` + `importlib` 载入被审 attempt 的 `tools/validate_hypotheses.py`（sha `cb49360d…`），只调用其 `validate(hypotheses, source_map, attempt, doc_texts)`，**不执行** `main()`（`main()` 会往封盘目录写 `validation_report.json`，禁止）。输入 = 我的 `hypotheses_v2.json` + 封盘 `source_map.json` + 封盘抽取件（全只读）。实测结果记入 `handoff.json` 的 `validator_check` 字段。

### 4.5 `decision_sha256` 实测值（我本工位计算，非复制）

```
4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f
```

- preimage 字节数 = **2451**（`claim` 196 B + `0x0A` 1 B + 裁定正文 2254 B）
- 三处同值：`hypotheses_v2.json` → `hypotheses[0].decision.decision_sha256`、同处 `hypotheses[0].provenance.decision_sha256`、`handoff.json` → `decision_sha256`
- **求值与复算均在我写入后重新执行过一次**（重新从本文件标记块提取裁定正文 + 从被审 `hypotheses.json` 提取 `claim`，重算 SHA-256，结果与写入 JSON 的值逐字符相同）；复算输入与输出原样登记在 `handoff.json` 的 `decision_sha256_verification` 字段
- 同一 JSON 的 sha（外部复算）：`hypotheses_v2.json` = `32c22208573a71d53033c4535e8d0cb598c61710e06174196033d996999d7859`（55,213 B）

---

## ⑤ 本裁定**不授予**什么（逐条，fail-closed）

1. **不授予任何阈值审定**：`falsifier.threshold`「0（…允许 |差| ≤ 1 元）」的**容差是否与来源披露舍入粒度一致**仍属会计面 `BLOCKED-6b`；我**不给**容差数、**不改** `threshold_basis`、**不新增** `threshold_review_status`、**不把** `not_reviewed` 改成 `reviewed`。按 `I11A-OPEN-ACCT/ruling.md` L226 四要件，阈值审定还需「可复算观测量 + 可核基础 + 非实现者签署（decision_sha256，作用域含 `parameter_id`）+ 追加式版本化」；本 sha 的作用域是**命题**，不是任何阈值或参数（见 §4.3 裁定三）。
2. **不放行任何参数**：`low/base/high` 全部维持 `null`；`original_value = 349,079,082,852` 维持为 FY2025 **披露值**而非校准值；`ZIJIN_SEG_MINERAL/SMELT/TRADE/OTHER_EXTERNAL_REVENUE_FY2027` 四个 parameter_id **不因此可被 I-11-B 取用做幅度**。
3. **不解除任何 BLOCKED**：`OPEN-2`（铜当量系数）、`OPEN-3`（微软 8-K/E1）、`OPEN-5`（港股可读性）、`OPEN-6`（阈值给数）及其 `BLOCKED-2a/2b/3a/3b/6a/6b/6c` 与 IND 侧 `BLOCKED-1…7` 全部原样保留；`OPEN-11` 的四要件 0/4 结论（`I11A-OPEN11-IND/ruling.md` §3.8）不受影响。
4. **不产生 I-11-A 验收**：`handoff.json` → `does_not_claim_I11A_acceptance = true`；我不改封盘 attempt 的任何 `status`/`state`/`review.md`。
5. **不产生 I-11-B 的 ACCEPT**：`I-11-B` 七条解锁条件中本工位只触碰第 1 条（C1）；第 2–7 条（含 `card_I-11-B.md` L9 的 `I-10-A` 披露适配签署、L147 之外的 OPEN 取值解封）**一条未动**；`i11b_unblocked` 维持 `false`。
6. **不授予三资格**：`three_qualifications` 的 `formula / disclosure_adaptation / accuracy` 维持 `not_applicable_here / not_granted / not_granted`——冻结命题 ≠ 披露适配通过 ≠ 准确性通过（`START_HERE.md` L27「仅该卡的明示资格，不外推到产品/预测准确性」）。
7. **不代签任何其他角色**：会计 reviewer、研究负责人、环境/依赖 owner、schema owner、统计 reviewer 各自的项我一项未签（`handoff.implementer_signed = false` 且无任何 `*Signed=true` 字段）。
8. **不裁其余 7 条命题**：下标 1–7（含 `H-CN-ZIJIN-VOL-03` 产能/存货桥）**逐字节保持原状**，理由见 §⑦-2。

---

## ⑥ 反例与被拒替代方案

### 6.1 什么证据会推翻本裁定（反例）

1. **下一期年报出现第五个报告分部，或分部集合/「对外销售收入」行定义变更** ⇒ 按 `refuted_by[0]`/`refuted_by[1]` 与 `falsifier.revert_rule`：停止四分部直加、回退到上一已证实口径、把差异登记为口径桥缺口、**新建命题版本**，本 `approved_frozen` 记录以追加方式标注失效（不改本快照）。
2. **下一期四分部对外收入之和 ≠ 合并营业收入（超出披露舍入粒度）** ⇒ 恒等式被推翻，同上回退；该判定**必须**先由会计面给出舍入容差（`BLOCKED-6b`），否则按 fail-closed **不得**据我本裁定宣布「被推翻/未被推翻」（A-6.1）。
3. **两份年报的分部附注被证明是抽取工具的解析产物而非原文**（例如目视 PDF 页面复核出不同数字）⇒ §3.2/§3.3 全部作废，本裁定立即降级为 `pending_professional_decision`（新版本）。
4. **发行人宣布分部口径将于 FY2027 起再度调整**（正如其 2024 年所做）⇒ `refuted_by[0]` 触发，须先重建分部映射再谈 FY2027 建模块。
5. **owner 明文推翻 `OPEN-7`（分部集合维持）** ⇒ 裁定二失据，按 §7 恢复规则新建 `ruling_r2.md` 并出新版本命题。
6. **发现我引用的任何一条逐字引文在原文件中不存在** ⇒ 属取证失败，按 `START_HERE.md` L36 与 `card_I-11-A.md` L21 转 `STOP_EVIDENCE`。

### 6.2 我拒绝的替代方案

1. **直接采信实现者的 `state_reason`「A1/A2/A3 已复算差=0」而不自己算** —— 违反「执行者自己完整读到关键字段，不能只看上个模型的总结」（`START_HERE.md` L9）与本次派工「回源读，别信转述」。我重算了 6 条等式（§3.2）。
2. **只凭 owner 的 `OPEN-7 分部集合维持` 就冻结** —— owner 授权是**许可不是动作**（`OWNER_DECISIONS.md` L502），且 `OPEN-7` 的裁定未附任何复算证据；我把它当**输入**而非**证据**，证据取自披露原文与我的复算。
3. **为凑 C1 而扩大批准面（一次批 2 条、3 条，或批准 `[2]` 产能/存货桥）** —— 拒绝：`H-CN-ZIJIN-VOL-03` 的存货桥未闭合（`state_reason` 自陈只核到三个数；`I11A-OPEN11-IND/ruling.md` R3 实测金差 154 千克、铜差 1 吨，零容差会假阳性），且其判定式执行前提依赖会计面容差（`BLOCKED-6b`）。**C1 只需 ≥1 条**，不因门槛低就多批。
4. **把 `approved_frozen` 解读为「四个分部参数可进入 I-11-B 校准」** —— 拒绝：`decision.md` DEC-3 反例段逐字「若下游把 `pending_professional_decision` 当成"实质已批准"继续做幅度校准，则状态机被绕过」；反向同理，`approved_frozen` 也不携带幅度。本裁定 §5 显式封死。
5. **修改被审 `hypotheses.json` 就地加签** —— 违反封盘只读纪律；我写的是**新版本** `hypotheses_v2.json`，与 DEC-6 恢复规则（L174–L175「写入命题的新版本，旧版本保留」）一致。
6. **用页号（`page_span = 327-328`）当跨期/跨工具定位键** —— 我实测被审页索引与 `pdftotext` leaf 差 1，且 `I11A-OPEN11-IND/ruling.md` R2-5 实测跨期 42↔44 漂移；一律改用 `anchor_text` + 表内数值定位。
7. **把 `pdftotext` 单一工具的结果当「唯一来源」** —— 每个数字我都要求两条抽取路径或四个披露位置互证（§3.3/§3.4）。
8. **用 `validation_report.json` 的旧计数证明「可批准」** —— 那是裁前状态（`approved_frozen = 0`）；我的判定依据是 §3 的原始证据与 §4 的规则源码。

---

## ⑦ 边界与恢复规则

### 7.1 边界（可核）

1. **写入面 = 3 个文件**，全部在 `execution_runs/I11A-HYP-APPROVE/a20260925-01/`；`.planning` 之外零写入；封盘 attempt `execution_runs/I-11-A/a20260919-01` **零字节改动**（收尾以 sha256 复核 `hypotheses.json` 仍为 `f2178768…`、`decision.md` 仍为 `e9c96f02…`、`review.md` 仍为 `4938e745…`，见 `handoff.json`）。
2. **只动 1 条命题**：`hypotheses_v2.json` 中只有下标 `0` 被改（`state`、`state_reason`、`decision.decision`、`decision.reason`、`decision.decision_sha256`，外加块内 `provenance` 元数据）；下标 `1–7` **逐字节保持原状**（`decision_sha256` 仍 `null`、`state` 不动），`provenance.modified_indices = [0]` 为机器可核声明。
3. **零 git 写 / 零 git 状态探查**：未执行 `git add/commit/checkout/stash/restore/reset`，**未执行 `git status`**；只执行 `git -c core.quotepath=false diff HEAD --name-only` 计数，非 `.planning` 计数在 `handoff.json` 记为 `git_diff_non_planning`。
4. **零联网**：网络请求 0；本文件引用的全部外部数值来自本地已归档的两份 PDF（company-wiki 产品仓，**只读**）。
5. **未裁其余命题**（`H-CN-ZIJIN-SEG-02` 单位收入/铜当量、`H-CN-ZIJIN-VOL-03` 产能与存货桥、`H-CN-ZIJIN-PLAN-04` 管理层计划、`H-CN-ZIJIN-ELIM-05` 抵销、`H-US-MSFT-SEG-01/02/03`）：分别被 `OPEN-2`、`OPEN-11`+`BLOCKED-6b`、`OPEN-6`、会计面抵销口径、`OPEN-3`(E1 缺) 等卡住；**我未裁，也未改其任何一个字节**。`approved_frozen_count = 1`。
6. **对本文件 §3.3 引文的取证局限（如实声明）**：我只用了 `pdftotext` 一种工具的默认/`-layout` 两种版式 + 被审 `P1_zijin_pages.json` 的既有抽取件；**未**目视渲染 PDF 页面、**未**运行被审 attempt 的 P1 取文器（运行会向封盘目录写输出，禁止）。

### 7.2 恢复规则（追加式，不回改）

- 新证据（FY2026/2027 分部口径变更、抽取复核差异、owner 推翻 `OPEN-7`）⇒ 在**本目录追加** `ruling_r2.md` + 新 `hypotheses_v3.json`，标 `supersedes: ruling.md#H-CN-ZIJIN-SEG-01`；**不修改**本文件正文、不修改 `hypotheses_v2.json`、不修改封盘任何字节。
- 命题被推翻时按其 `revert_rule` 回退到上一已证实口径并登记口径桥缺口；旧快照保留供 I-12 评分（`decision.md` DEC-6 恢复规则 L174–L175）。
- 会计面若对 `BLOCKED-6b` 出具容差，须以**新裁定记录 + 命题新版本**落库，**不得**借用本 sha（本 sha 作用域只有命题本体）。
