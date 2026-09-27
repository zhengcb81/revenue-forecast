# OPEN5-S5-IND-RULING · oracle（**先冻结**）

- **卡 / 步**：`OPEN-5` 恢复路径 **S5 · 行业复裁 + 会计定级** 的**行业那一半**（会计半区已由 `OPEN5-S5-ACCT-GRADING/a20260926-01` 交付，本工位**只读引用、不代签、不推翻**）
- **attempt（本目录，新建）**：`execution_runs/OPEN5-S5-IND-RULING/a20260926-01/`
- **角色**：`industry_reviewer_s5`（矿业/软件行业 reviewer，**非实现者**）
- **写入面**：仅本目录；**S4 / S3 / S1 两站 / 封盘 `I-11-A` / 会计半区 一律只读**，一个字节不改
- **本文件冻结时刻之后**才允许做回源核验、自抽测量、四点裁定、红绿变异。

---

## 0. 冻结声明

本 `oracle.md` 在**任何四点裁定、任何自抽测量、任何红绿变异之前**写入并冻结。判据一经冻结不改；若执行中发现判据必须修订 ⇒ 另建 `oracle-addendum.md` 写明原因，**不改本文件**。本文件冻结后产生的全部测量（sha256 复算、自抽文本、锚词计数、脚本跑批）才进入结论。

---

## 1. 授权（逐字回源）

### 1.1 S5 定义（唯一授权来源）

`execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` **L166（逐字）**：

> `| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | 行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） | 任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |`

- **受理人** = **行业 reviewer（本工位）** + 会计 reviewer（已交，只读引用）；
- **失败分支** = **任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER`**；
- **即使两面都过**，也只是「**通过后才谈港股命题与参数**」—— 授权是许可不是动作（`OWNER_DECISIONS.md` **L502**：「**「授权」是许可不是动作**：四项均**不产生任何 ACCEPT、不解除任何 BLOCKED、不改任何 status**」）⇒ **通过 ≠ 放行**。

### 1.2 边界（ENVOWNER **L174–L179**，逐字）

- **L174**：`卡文原话（decision.md L227–L228）：「可读性恢复后（工具或依赖变更），新建 attempt 重新取证；不得把本次的 not_readable 判定改成"已验证"。」`
- **L176**：`S3 明文要求"新建 attempt"，恢复取证发生在新 attempt，本载体与封盘 attempt 都不产生任何"已验证"字样；`
- **L177**：`本载体不写 hypotheses.json / source_map.json / mechanism_review.md / handoff.json（I-11-A 的），不改任何 state/status/not_readable 字段 —— §⑦ 的写入面自证；`
- **L178**：`handoff.json 显式带 does_not_claim_I11A_acceptance=true、unlocks_nothing=true；`
- **L179**：`即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 _PLACEHOLDER）。`

⇒ **本工位即使行业面判过，也不解除 ENVOWNER §⑦ 的解锁前置（L188–L193），不产生任何 `approved_frozen`，不放行任何 `_PLACEHOLDER`。**

### 1.3 IND 已裁的 C 表（**裁定权与「是否启用」在行业面**）

**回源勘误（登记，不回改）**：派单把 C 表指到 `execution_runs/I11A-OPEN11-IND/a20260924-01/ruling.md`；**实测该文件没有 C 表**（全文 325 行，`C 表` / `external_retrieval_not_local` 零命中；其 L234/L240/L241/L261 是 OPEN-11 自身的读法/兼容/被拒方案行，语义不同）。**C 表实际在 `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md`（399 行）L227–L234 / L240–L241 / L261 / L360**，行号与派单引用**逐一对得上**（会计半区 `oracle.md §1.4` 与 S4 `s4_report.md L20` 亦按此引用）。**以文件原文为准。**

`execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md`：

- **L227（标题，逐字）**：`**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**`
- **L231（① 行，逐字）**：
  > `| ① | **同一发行人、同一报告期**的其他**可读原文**官方文件（HKEX 披露易 PDF 文本层正常者、全年业绩公告、中期报告、公司 IR 的年报 HTML/可读 PDF） | \`company_primary_disclosure\`（与年报同级，但必须标注**文件类型与期间**） | 必须：原文可定位（页码/锚文本或章节）+ 原始 sha256 + 期间与年报一致；跨期文件必须标 \`period_mismatch_risk\` |`
- **L232（② 行，逐字）**：`| ② | 交易所/监管公告（HKEX） | \`regulator_primary_disclosure\` | 同上 |`
- **L233（③ 行，逐字）**：`| ③ | 券商研报 / 新闻 / 数据商 / wiki | \`secondary_lead_only\` | **仅可作线索**，**不得**进参数、**不得**进命题的 \`cited_values\` |`
- **L234（④ 行，逐字）**：
  > `| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | \`external_retrieval_not_local\` | 必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径 |`
- **L240（反例 1，逐字）**：`- 环境 owner 解决可读性后，若新 attempt 实测仍读不出原文 ⇒ B 部分（保持不可用）继续有效，C 表不启用；`
- **L241（反例 2，逐字）**：`- 若出现①类可读原文且含分部收入 ⇒ B 的"零产出"解除，港股命题可重新走正常取证（仍需会计面定证据等级）；`
- **L261（被拒替代方案，逐字）**：`- 用外部抓取件静默顶替本地原件（必须按④登记为外部）；`
- **L360（逐字）**：`- **外部 ≠ 本地**：所有 \`EXT-*\` 一律标 \`evidence_class=external_retrieval_not_local\`；\`2026-09-02 8-K\` 条目显式写明"**本地不可核，外部获取，不得作为本地可核证据放行**"。`
- **B 部分（L220–L225，处置规则）**：港股分部命题**零产出**、参数维持 `_PLACEHOLDER`、**不接受二手补位**、**不接受行业常识补位**（B-3/B-4 **始终有效，C 表启用不解除它们**）。

> **「C 表是否启用」的裁定权在本工位**（派单 + 会计半区 §6 第 2 条明文：这是行业面裁权）。

### 1.4 会计半区交付（**只读引用，不代签、不推翻**）

`execution_runs/OPEN5-S5-ACCT-GRADING/a20260926-01/`：`acct_grading.json`（42,499 B，sha256 `3a5623afb19a19bdf9b83520595980810e41d14072131769639c00c5a69b0eda`）· `s5_acct_report.md`（23,861 B，sha256 `0bfbedaead34929cdd994e5e1a3660d642d6720a50a9f95c8041ff8f3cb9fd5c`）· `handoff.json`（11,326 B）· `oracle.md`（sha `32c28419…`）。

- 会计面已裁：attempt04 = `①+④ / E1 / S1 / usable=["zh-Hant"] / admissible=true`；attempt08 = `①+④ / E1 / S1 / usable=["en"] / admissible=true`；attempt07（r.jina.ai 代理）= `③ / E3 / S0 / admissible=false`；origin = **排除在定级外（`level=null`）**；`hk_parameters_released=false`；G2/G3 已在其记录内补齐（`back_written=false`）。
- 会计半区 **§6 给行业面的 7 条会签提请**（逐条回源读过，原文见 `s5_acct_report.md` L172–L182），本工位要裁的是其中 4 条（第 1–5 条中的四点），第 6/7 条作边界确认与未证事项登记。
- **证据等级由会计面认定**（`OWNER_DECISIONS.md` **L504**：`- **取证（选项 3）的证据等级由会计面定，不由取证方自定**；取不到就维持 BLOCKED，**不造绿色样例**。`）⇒ **本工位不改 E/S 等级，只裁：C 表启用与否 + 来源登记的行业面承认 + 用途/语言面/口径四点。**

### 1.5 S4 已定边界（**只读接受，不下 S4 结论**）

`execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/`：`consistency_result = NOT_USABLE`（触发面 = U1 origin 本体，`numeric_conflict = 3`）；U2 attempt04 = `CONSISTENT`；U3 attempt08 = `CONSISTENT`（英文 5/5、中文 0/5）；7 项 provenance 缺项 G1–G7；提请语 `s4_report.md` L196–L200。
ENVOWNER **L165**：`复核不一致 ⇒ 该来源不可引用，维持不可读处置`。

---

## 2. 范围边界（**只裁四点；不做清单**）

**做（四点，来自会计面 §6 会签提请）**：

1. **C 表是否启用**（IND L240/L241 裁定权在本工位）+ 对 attempt04 / attempt08 / attempt07 **逐条**承认与否会计面的 `①+④ / ①+④ / ③` 登记；
2. **attempt04 文件类型用途**（全年业绩公告，非年报）⇒ 行业口径下**可用于哪些命题、不可用于哪些**；
3. **attempt08 英文面限制**（中文锚词 0/5、`usable=["en"]`）⇒ 英文面在港股命题中的**可用范围**；
4. **G3 口径会签**（会计 `true` vs `PEND-5a/S3 false`）⇒ 按 IND L234/L360 裁哪一口径为准（**两边都不回改，只登记**）。

**不做（明令，逐条）**：

1. **不代签会计面**：不改 E1/E3/S1/S0、不改 `usable_faces`、不改 `admissible`、不重做会计四步；
2. **不放行港股参数**：`hk_parameters_released` 恒 `false`，`_PLACEHOLDER` 维持，`low/base/high = [null,null,null]`；
3. **不解除 `OPEN-5`**、不解除 ENVOWNER §⑦、不产生 `I-11-B` 的 `ACCEPT`、不产生任何 `approved_frozen`；
4. **不改 `NOT_USABLE`**、不下 S4 结论、不改 `numeric_conflict`、不把任何 `not_readable` 改成「已验证」；
5. **不给 origin 赋级**（`HK-XIAOMI-AR2025` 排除在定级外）；
6. **不写** S4 / S3 / S1 两站 / 封盘 `I-11-A` / 会计半区 / `I11A-OPEN-IND` **任何字节**（只读引用）；
7. **不写**五份计划文件；**不写** `.planning` 之外任何路径（含 `company-wiki`）；
8. **零 git 写**；**禁用 `git status`**；**禁止联网**（只用盘上既有产物 + 本地只读解析/自抽）。

---

## 3. 受核输入（全部只读；sha 于冻结后登记到 `_work/input_hashes.json`）

| 代号 | 对象 | 路径（相对计划目录） |
|---|---|---|
| **IN-01** | ENVOWNER ruling（L165 / L166 / L174–L179 / §⑦） | `execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` |
| **IN-02** | IND C 表与 B 部分（L220–L261 / L360） | `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` |
| **IN-03** | 会计半区交付三件 + oracle | `execution_runs/OPEN5-S5-ACCT-GRADING/a20260926-01/{acct_grading.json,s5_acct_report.md,handoff.json,oracle.md}` |
| **IN-04** | S4 产物（`NOT_USABLE` / U2 / U3 / G1–G7 / own_provenance） | `execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/{s4_report.md,dual_path_verify.json,handoff.json,oracle.md}` |
| **IN-05** | S3 provenance（`in-02`/`in-03` 口径 `false`） | `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/provenance.json` |
| **IN-06** | PEND-5a provenance / handoff（ext-04 / ext-07 / ext-08；owner 解锁链） | `execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/{provenance.json,handoff.json}` |
| **IN-07** | 替代件字节（本工位复算 sha256） | `execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf`、`…/attempt08_irmi_xiaomi_ar2025_en.pdf`、`…/attempt07_rjina_xiaomi_ar2025_zh_proxy.txt` |
| **IN-08** | S3 可读性结论（路径 A 5/5 / B1 0/5 / B2 4·5/5） | `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/reacquisition_report.md` |
| **IN-09** | owner 解锁授权（§二十六 #1「1，授权」） | `OWNER_DECISIONS.md`（L490–L504 执行纪律；L539–L548 §二十六） |
| **IN-10** | 本工位自抽工件（冻结后产出，写在本目录 `_work/`） | `_work/extract/*.txt`、`_work/measure_*.json` |

**sha 不全等 / 文件不可读 / 判据源行找不到 ⇒ fail-closed：按未核验处理，判 `blocked`。**

---

## 4. 判据（**冻结**）

### 4.1 J1 —— **C 表是否启用**（IND L240 / L241 的反例条件，行业面裁权）

`c_table_adopted = true` 当且仅当 **J1-1 ∧ J1-2 ∧ J1-3 ∧ J1-4** 全部成立：

- **J1-1（owner 解锁链在盘上可核）**：IN-06 `handoff.authoritized_by` 指向 `OWNER_DECISIONS.md §二十六 #1` 的 owner 原话授权，且 PEND-5a 站点确实存在并交付（`result=delivered`）。⇒ 对应 IND **L227**「供 **owner 解锁后**使用」的前置。
- **J1-2（S3/S4 已走完且结论可核）**：IN-08 记录路径 A（origin 字节 OCR）锚词 **5/5**、B1（origin 文字层）**0/5**、B2/B2′ 替代件 **4/5 与英文 5/5**；IN-04 记录 U2/U3 = `CONSISTENT`、U1 = `NOT_USABLE`（`consistency_result` 实测仍为 `NOT_USABLE`）。
- **J1-3（L241 正向条件，核心）**：**存在 ≥1 件通过 ① 三条件的来源，且该件正文明示「分部收入」披露**：
  - ①三条件 = **可定位**（本工位自抽文本中能定位到页/锚文本）∧ **原始 sha256 复算全等**（且与 PEND-5a / S3 / S4 / 会计半区登记值全等）∧ **期间与年报一致**（标题逐字含 `截至2025年12月31日止年度` / `FY2025`）；
  - **含分部收入** = 自抽正文中命中分部收入披露锚词 **≥1**：`分部收入`、`分部收益`、`手機×AIoT`、`segment revenue`、`Segment-wise`（中英任一）。
  - **任一不满足 ⇒ J1-3 = false ⇒ C 表不启用 ⇒ 行业面不通过 ⇒ `blocked`。**
- **J1-4（L240 反向条件的读法，冻结）**：
  - **读法 α（本工位冻结采用）**：L240 的「读不出原文」= **新 attempt 产不出任何可读原文文本**。实测 S3 路径 A 5/5 + 两件 ① 替代件可读 ⇒ **不成立**（C 表不被 L240 否决）。
  - **读法 β（登记，不采用）**：「原文」仅指 **origin 本体字节**（B1 仍 0/5、S4 U1 `NOT_USABLE`）。若采 β ⇒ C 表不启用。
  - **采用 α 的理由（冻结）**：IND **L227** 明写 C 表是「**替代来源**及其证据等级……供 owner 解锁后使用」——替代来源表的存在前提就是 origin 不可读；若 β 成立则该表永无适用场景，与表自身用途直接矛盾。且 L241 用「**出现**①类可读原文」而非「原文件被修复」措辞 ⇒ 启用开关挂在**替代件**上。
  - **登记（不隐瞒）**：α/β 之争属**解释分歧**，本工位采 α 并在报告中显式登记 β；**无论采哪一种，`hk_parameters_released` 都保持 `false`、origin 都保持排除**（分歧只影响「港股命题能否重新走正常取证」，不放行任何参数）。
- **C 表启用的效力范围（冻结，超出即越权）**：
  1. 仅解除 IND **B-1** 中「①类替代件缺位 ⇒ 零产出」的那一层；**B-3（不接受二手补位）/ B-4（不接受行业常识补位）继续有效**；
  2. **origin 本体不因启用而可引用**（L165 + S4 `NOT_USABLE` 维持）；
  3. **参数不放行**（L166「通过后才谈」+ L179 + ENVOWNER §⑦）；
  4. 引用 ④ 标记的件时**永不冒充本地原件**。

### 4.2 J2 —— attempt04 文件类型用途（行业口径）

**步骤 1（类型识别，实测定）**：自抽文本首页/标题是否逐字含 `全年業績公告` 且含 `截至2025年12月31日止年度`，页数 = 59；是否含 `年度報告` 作为文件标题。
**步骤 2（内容清单，实测 presence/absence）**，对下列命题类逐类测其所需证据是否在 attempt04 正文中存在：

| 代号 | 命题类（行业） | 所需证据锚（自抽实测） | 冻结的默认处置 |
|---|---|---|---|
| **A1** | FY2025 分部收入**水平与增速**（港股份部命题主用） | `分部收入` / `手機×AIoT` + 数字 | 存在 ⇒ **可用于**；不存在 ⇒ 禁止 |
| **A2** | FY2025 分部**毛利率/毛利** | `分部毛利率` / `毛利` | 同上 |
| **A3** | FY2025 **总收入与增速**、经营概述 | `總收入`/`收入` + `%` | 同上 |
| **A4** | **分部加总/对账校验**（分部合计 = 合并总额的恒等式） | `分部資料`/`可報告分部`/`分部附註`/`對賬`/`reconciliation` | 缺 ⇒ **禁止**（公告无 IFRS 8 分部附注对账表） |
| **A5** | **已审计**财务报表断言 / 审计意见引用 | `核數師報告`/`無保留意見`/`審計` | 缺 ⇒ **禁止** |
| **A6** | **跨期（五年）财务摘要、附注级科目**（如存货明细、现金流量表附注） | `五年`/`財務摘要`/`存貨` 附注 | 缺 ⇒ **禁止** |
| **A7** | 需要「**年报本体页码/锚文本**」的命题（引文须落年报页） | `年度報告` 标题 / 415 页结构 | 不是年报 ⇒ **禁止**（须改用 attempt08 或另行取文） |

**冻结规则**：A1/A2/A3 **可用**（同期间、公司原文披露、可定位、sha 绑定）；A4–A7 按实测 absence **禁止**；任何**未列类**按「需要什么就测什么，测不到即禁止」（fail-closed）。
**必标项（① must_label，登记不改）**：`document_type = 全年业绩公告（results announcement，非年度报告）`、`period = FY2025`、`period_mismatch_risk = false`、`external_retrieval_not_local = true`（④）。

### 4.3 J3 —— attempt08 英文面在港股命题中的可用范围

- **J3-1 语言面实测**：中文锚词 `小米/收入/年度報告/分部/毛利` 命中数；英文锚词 `Xiaomi/Revenue/Annual Report/Segment/Gross profit` 命中数。
  - 冻结期望 = 中文 **0/5**、英文 **≥4/5**；**英文 <4/5 ⇒ `blocked`（语言面不可核）**；**中文 >0 ⇒ 登记与会计面 `usable=["en"]` 的分歧，并按更严者处置（仍只认 en 面，fail-closed 向限制方向）**。
- **J3-2 跨语言数值一致性**：attempt04（zh）与 attempt08（en）**共同披露**的 ≥2 个数值（总收入、同比增速%）归一化为数字串后必须**相等**；**任一不等 ⇒ `blocked`**（同一份 FY2025 披露的两个语言版本数值必须一致，否则语言面不可交叉引用）。
- **J3-3 冻结的可用范围**：
  - **可用于**：需要**年报本体**页/表定位的命题（A4/A5/A6 类，若其证据确在 EN 年报中）、数值型分部命题（收入/毛利/占比/增速）、与 attempt04 中文件的**数值交叉验证**——但命题必须显式登记 `language_face = en` 且引文用**英文原文逐字**；
  - **不可用于**：任何要求**中文原文逐字引文 / 中文锚词命中**的命题（中文 0/5）；任何以「中文年报原文已核」为口径声明的结论；翻译敏感的**定义性表述**（分部名称、会计政策措辞）未经 attempt04 中文件对照不得单独成立；
  - **不可冒充中文面**：与 ④ 的「永不冒充本地」同构——**英文面不得冒充中文原文面**。

### 4.4 J4 —— `G3` 口径会签（按 IND L234 / L360 裁）

- 实测四点：① IN-06 `ext-04`/`ext-08` = `false`（口径 A，语义=非第三方代理）；② IN-05 `in-02`/`in-03` = `false`（口径 A）；③ IN-02 **L234**（④ 行证据等级列本身 = `external_retrieval_not_local`）+ **L360**（所有 `EXT-*` 一律标 `external_retrieval_not_local`）+ **L261**（外部抓取件必须按④登记为外部）；④ IN-04 `own_provenance` = `true`（口径 B）。
- **裁定规则（冻结）**：**④ 的语义优先**——④ 的「使用条件」明写「**永不冒充本地可核**」，若按口径 A 记 `false` 则该条件无字段承载 ⇒ **口径 B（`true`）为准**；**两边都不回改，只在本工位记录登记分歧**（`back_written = false`）。
- **`blocked` 条件**：④/L360 原文在盘上找不到，或两侧实测值与上述不符 ⇒ `J4 = false ⇒ blocked`。

### 4.5 C 表登记判别函数（**来源登记在行业面的承认**）

| 条件（实测） | 登记行 | 本工位承认？ |
|---|---|---|
| 发行人自己的披露（年报 / 全年业绩公告 / 中期报告 / IR 可读 PDF），同一报告期，可读 | **①** `company_primary_disclosure`（必标 `document_type` + `period`） | 承认（须三条件齐） |
| 交易所/监管方自身公告行为 | **②** `regulator_primary_disclosure` | 本轮**零登记**（不为凑表升格） |
| 券商研报 / 新闻 / 数据商 / wiki / **第三方代理渲染件** | **③** `secondary_lead_only`（仅线索，不得进参数与 `cited_values`） | 承认（= 不可采） |
| 外部取回的港股年报 PDF/文本（本地原件不可读） | **④** `external_retrieval_not_local`（**外部身份标记**，与①/③叠加，永不冒充本地） | 承认（叠加登记） |

- **①与④叠加不是矛盾**：① = 文件的来源级别，④ = 取回路径的外部身份；宿主站点不改变文件性质。
- **attempt07 特判（冻结）**：r.jina.ai 第三方代理渲染件 ⇒ **③**；且其正文锚词实测 0/5（不可读）⇒ **双重不可采**（既非①/④可核路径，内容也不可读）。**升格为 ①/④ 即视为判据被改弱。**
- **origin 本体**：**不进入定级**（`graded=false`、`level=null`、`admissible=false`），处置 = S4 `NOT_USABLE` + ENVOWNER L165。

### 4.6 港股参数与 S5 通过的效力（**恒不放行**）

`hk_parameters_released = false` **在任何分支（含全部变异）下都成立**，因为：

1. L166 只给「**通过后才谈**港股命题与参数」——谈 ≠ 放行；
2. ENVOWNER **§⑦ L188–L193**：不解除 `OPEN-5` 对 `I-11-B`/`I-07-B` 的阻塞、不新增 `approved_frozen`、不放行 `_PLACEHOLDER`、解锁前置须全部满足且「仍不由本载体」；
3. **L179** 在 S5 两面走完前压顶；走完后仍须由**有权方**（实现者/编排层/owner）按各自前置另行处理，**不是本工位的输出**。

### 4.7 `blocked` 触发条件（**任一即 blocked，这是合格结果**）

1. **J1-3 不成立**：无 ① 类通过三条件的来源，**或**① 件正文无分部收入披露 ⇒ C 表不启用；
2. J1-1 / J1-2 不成立（owner 解锁链、S3/S4 结论在盘上不可核）；
3. 受核输入 sha256 复算与登记值**不全等** / 文件不可读 / 判据源行（IND L231/L234/L240/L241、ENVOWNER L166/L179）在盘上找不到；
4. J3-1 英文锚词 `< 4/5`，或 J3-2 跨语言数值不一致；
5. J4 两侧实测与冻结描述不符、或 ④ 语义无法判定；
6. **纪律违例**：S4 `consistency_result` 实测 ≠ `NOT_USABLE`，或任何输出给 origin 赋了等级，或会计半区交付文件 sha 与其 handoff 登记不全等；
7. 会计半区 §6 的四点中有任一点**证据不足**（读不到支撑该点的原文/实测）⇒ 该点判缺，整体 `blocked`。

---

## 5. 红绿变异清单（**先冻结**）

脚本：`_work/s5_ind_grade.py`（本工位自己写；只读输入；测量与输出落本目录 `_work/`）。
**退出码约定**：`0` = 判定通过（PASS，非 blocked）；`2` = 触发 §4.7 `blocked`；`3` = 与本表冻结期望不符（判据空转或漏判）。

| # | 变异 | 冻结期望 |
|---|---|---|
| **R0（绿·基线）** | 不改判据，真实输入 | rc=**0**；`c_table_adopted=true`；attempt04 → `①+④` **承认 + 用途受限清单**；attempt08 → `①+④` **承认 + en 面受限**；attempt07 → `③` **不承认（不可采）**；origin → **excluded（level=null）**；J4 → **口径 B（true）为准**；`hk_parameters_released=false` |
| **M1（红·判据改弱 ⇒ 不该通过的必须能通过）** | `tier_filter=off`（③/代理件按 ① 处理）+ `require_readable=off`（不看锚词） | **attempt07 由「不采」翻转为「采」** ⇒ `should_pass_flip=true`；rc=**0**（变异体自身跑通）⇒ 证明 baseline 拒绝它是**判据作用** |
| **M2（红·origin 排除被弱化）** | `exclude_origin=false` | **origin 被赋等级**（应被排除）⇒ `origin_grade_flip=true`；rc=**0** |
| **M3（红·blocked 分支 1）** | 剥离 attempt04 的 URL（模拟 G2a 缺失） | `verdict=blocked`（§4.7-3），rc=**2** |
| **M4（红·blocked 分支 2）** | 抹去 ① 件正文中全部分部收入锚（模拟 L241 正向条件不成立） | `c_table_adopted=false` ⇒ 行业面不通过，rc=**2** |
| **M5（红·blocked 分支 3）** | 篡改 attempt08 与 attempt04 共享的一个数值（模拟跨语言不一致） | J3-2 失败 ⇒ `blocked`，rc=**2** |

**红绿双向要求**：M1 证明「判据改弱后一个不该通过的来源（attempt07 代理件）确实能通过」；M3/M4/M5 证明 `blocked` 分支确实是红的（rc=2）；M2 证明 origin 排除不是空转。**期望 rc 序列 = `0 / 0 / 0 / 2 / 2 / 2`。**

---

## 6. fail-closed 条款

1. 任一提请点证据不足 ⇒ 判 `blocked` 并给实测，**不为推进而会签**；`blocked` 是合格结果；
2. 承认会计面等级 ≠ 提升用途：用途/语言面限制**只紧不松**（限制方向的偏差可登记，放宽方向的偏差一律拒绝）；
3. 自抽/锚词定位不到 ⇒ 判缺，不以「大概在」放行；
4. **不代签会计面、不放行参数、不解除 `OPEN-5`、不改 `NOT_USABLE`、不给 origin 赋级**——任何分支下都不得输出这些字段为真；
5. JSON 写后 `json.load` 重解析；UTF-8 **无 BOM**；**纯 LF**；
6. 结束前 `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` = **0**；零 git 写；**禁用 `git status`**；**禁联网**。

---

## 7. 写入面

**恰好**：`oracle.md` · `ind_ruling.json` · `s5_ind_report.md` · `handoff.json`（四件产出）+ `_work/` 下的脚本、自抽文本与测量 JSON。
`.planning` 之外创建/修改 = **0**；`company-wiki` **本工位不打开**（origin 只经 PEND-5a 本地副本与 S4 记录只读登记）。
