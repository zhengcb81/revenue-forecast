# OPEN5-S5-ACCT-GRADING · oracle（**先冻结**）

- **卡 / 步**：`OPEN-5` 恢复路径 **S5 · 会计半区（会计定级）**
- **attempt**：`execution_runs/OPEN5-S5-ACCT-GRADING/a20260926-01/`（计划目录 `.planning/2026-09-19-three-project-history-audit/` 下，**新建**）
- **角色**：`accounting_reviewer_s5`（会计/披露 reviewer，非实现者）
- **写入面**：仅本目录（`.planning` 内）；**S4 / S3 / S1 两站 / 封盘一律只读**
- **行业面**：`S5` 的另一半（行业复裁）由父**另派**，**本工位不代签、不代裁**

---

## 0. 冻结声明

本文件在**任何 G2/G3 回源核验、任何来源等级登记、任何证据等级判定之前**写入并冻结。
判据一经冻结不改；若执行中发现判据必须修订 ⇒ 另建 `oracle-addendum.md` 写明原因，**不改本文件**。
本文件冻结时刻之后产生的全部测量（sha256 复算、逐字引文核验、脚本跑批）才进入结论。

---

## 1. 授权（逐字回源）

### 1.1 S5 定义（唯一授权来源）

`execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` **L166（逐字）**：

> `| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | 行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） | 任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |`

- **受理人** = 行业 reviewer + **会计 reviewer**（本工位 = 会计那一半）；
- **失败分支** = **任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER`**；
- 「**本载体不代行**」= ENVOWNER 载体不代行；两个 reviewer 各自行使**各自专业裁定权**。
- ⚠️ **转述差异登记**：派单把出处写作「`OWNER_DECISIONS §二十四` 执行纪律第 3 条」、分隔符用全角 `｜`；文件原文为「§二十四 执行纪律第 3 条」、半角 `|`。**以文件原文为准**（同族：转述改变措辞；S4 已登记过第 18/20 起）。

### 1.2 边界（L174–L179，逐字）

- **L174**：「卡文原话（`decision.md` **L227–L228**）：「可读性恢复后（工具或依赖变更），**新建 attempt 重新取证**；不得把本次的 `not_readable` 判定改成"已验证"。」」
- **L179**：「即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。」

⇒ **本工位即使会计面判过，也不解除 L179；S5 的行业那一半未走完前，港股命题仍零产出、参数仍 `_PLACEHOLDER`。**

### 1.3 「证据等级由会计面定」的原文出处

`.planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md` **§二十四 执行纪律第 3 条，L504（逐字）**：

> `- **取证（选项 3）的证据等级由会计面定，不由取证方自定**；取不到就维持 BLOCKED，**不造绿色样例**。`

同节 **L502（逐字）**：「**「授权」是许可不是动作**：四项均**不产生任何 ACCEPT、不解除任何 BLOCKED、不改任何 status**；`I-11-B` 仍 BLOCKED（解锁 7 条条件未满足）。」

### 1.4 IND 已裁的 C 表（登记来源等级的尺子）

**回源勘误（必须登记）**：派单把 C 表指到 `execution_runs/I11A-OPEN11-IND/a20260924-01/ruling.md`；**实测该文件没有 C 表**（grep `C 表|港股|小米|external_retrieval_not_local` 仅命中其自身 §④ 标题、L293「`OPEN-5`（港股可读性）… 不涉及」、L295「外部证据一律标 `external_retrieval_not_local`」）。**C 表实际在 `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` L227–L234**（S4 亦按此引用，见 `s4_report.md` L20）。**以文件原文为准。**

`I11A-OPEN-IND/a20260924-01/ruling.md`：

- **L227（标题，逐字）**：「**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**」
- **L231（①，逐字）**：
  > `| ① | **同一发行人、同一报告期**的其他**可读原文**官方文件（HKEX 披露易 PDF 文本层正常者、全年业绩公告、中期报告、公司 IR 的年报 HTML/可读 PDF） | \`company_primary_disclosure\`（与年报同级，但必须标注**文件类型与期间**） | 必须：原文可定位（页码/锚文本或章节）+ 原始 sha256 + 期间与年报一致；跨期文件必须标 \`period_mismatch_risk\` |`
- **L232（②，逐字）**：`| ② | 交易所/监管公告（HKEX） | \`regulator_primary_disclosure\` | 同上 |`
- **L233（③，逐字）**：`| ③ | 券商研报 / 新闻 / 数据商 / wiki | \`secondary_lead_only\` | **仅可作线索**，**不得**进参数、**不得**进命题的 \`cited_values\` |`
- **L234（④，逐字）**：
  > `| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | \`external_retrieval_not_local\` | 必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径 |`
- **L240/L241（C 表启用的反例条件，逐字要点）**：「环境 owner 解决可读性后，若新 attempt 实测仍读不出原文 ⇒ B 部分（保持不可用）继续有效，**C 表不启用**」；「若出现**①类可读原文且含分部收入** ⇒ B 的"零产出"解除，港股命题可重新走正常取证（**仍需会计面定证据等级**）」
- **L261（被拒替代方案，逐字要点）**：「用外部抓取件静默顶替本地原件（必须按④登记为外部）」
- **L360（OPEN-11 语义，逐字）**：「**外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`；`2026-09-02 8-K` 条目显式写明"**本地不可核，外部获取，不得作为本地可核证据放行**"。」

> 补强（同族先例）：`I11A-OPEN11-IND/a20260924-01/ruling.md` **L295（逐字）**：「本工位**只引用**其 E 分级与「给数四要件」作为本卡判据，**不裁**证据等级与舍入容差（那是 ACCT 半区）；外部证据一律标 `external_retrieval_not_local`。」

### 1.5 会计面等级体系（本工位的尺子）

`execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md`：

- **L52–L60 来源可采性分级（S1/S2/S3/S4/S0）**，其中 S1 =「公司/发行人**同一期间原文披露**：可定位到页/表/锚文本，doc sha256 已绑定，至少一条独立路径复核」；S0 =「不可得 / 不可核 ⇒ 参数保持 `_PLACEHOLDER`，**不得放行**」。
- **L64–L69 披露证据等级（E1/E2/E3/E0）**，逐字：
  - `E1 已核` =「申报原文**本地归档**：URL + 取回 UTC + 文件 sha256 + 逐字引文 + 至少一条独立复核路径（同本卡 P1/P2 双路径精神）」→ 可支撑「参数、口径声明、"已核"字样」；
  - `E2 可引未归档` =「在线取回但只留 URL/时间/引文，未落本地归档」→ **仅**叙述与风险提示；
  - `E3 二手` =「研究稿、web 工具转录、新闻、搜索摘要」→ **仅**用于提出问题；
  - `E0` =「记忆 / 共识 / "众所周知"」→ 不是证据。
- **L153（A-3.1，逐字要点）**：「**E1 = 已核**（唯一可支撑"分部口径已确定"的等级）：申报原文本地归档 + sha256 + 逐字引文 + 独立路径复核…」
- **L188（E1 的外部取回先例，逐字要点）**：「E1 归档到位（**例如以合规 UA/镜像取回 8-K 与 exhibit 99.1 并落 sha256**）且显示…」⇒ **E1 与「外部取回 + 本地归档」不矛盾**；④ 的 `external_retrieval_not_local` 是**反冒充标记**，与 E1 并存而非互斥。
- **L218–L220（OPEN-5 · `NOT_IN_MY_SCOPE`，逐字）**：「**`NOT_IN_MY_SCOPE`**：港股（小米）年报原文可读性属**环境/依赖 owner + 行业 reviewer** 的裁权（`decision.md` L401），本文件不予裁定，仅登记其阻塞关系不变（阻塞任何港股份部命题与 I-11-B 港股参数）。」
  ⇒ 该文件**未**裁 S5 的定级；L166（§1.1）**新授**了「证据等级由会计面认定」⇒ 本工位据此**只裁证据等级与来源登记**，不越界裁可读性归属与行业处置。

### 1.6 S4 已定的边界（**只读接受，不推翻**）

`execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/`（`s4_report.md` / `dual_path_verify.json` / `handoff.json` / `oracle.md`）：

1. `consistency_result = NOT_USABLE`，触发面 = **U1 origin 本体**（`numeric_conflict = 3`：p30 `1,007,26139,166,303`、p47 `1,000,001`、p47 `6,000,00`）⇒ 按 **L165**「该来源不可引用，维持不可读处置」；
2. **U2 attempt04 = `CONSISTENT`**、**U3 attempt08 = `CONSISTENT`**（attempt08 中文面 0/5，仅英文面可用）；
3. **S4 给 S5 的提请（`s4_report.md` L196–L200 逐字要点）**：「**origin 本体按 L165 不可引用、不进入定级**；attempt04/attempt08 的双路径互证已成立 ⇒ **S5 请按 IND C 表 ④ + 会计面定级补裁**，且 **G2/G3 是 S5 引用前必须先补的 provenance 硬缺项**」；
4. S4 登记的 **G2**（`in-02`/`in-03` 无 URL，URL 只在 PEND-5a `provenance.json` ext-04/ext-08）与 **G3**（`external_retrieval_not_local=false` 口径 vs ④ 语义冲突）。

---

## 2. 范围边界（**只做四步；不做清单**）

**做**：

1. **补 G2/G3 硬缺项（只在本工位记录里补，不回改 S3/S4/S1/封盘）**；
2. **按 C 表 ①/② 登记来源等级**（attempt04 / attempt08 逐个；origin 本体不进入定级）；
3. **会计面定级**（逐来源给证据等级 + 理由 + 依据：文件 + 行号/字节区 + 逐字引文）；
4. **判断港股参数是否可以动**（只裁我这一半）。

**不做（明令，逐条）**：

1. **不写** S4（`OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01`）、S3（`OPEN5-S3-REACQUISITION/a20260925-01`）、S1 两站（`OPEN5-PEND5A-HK-ACQUISITION`、`OPEN5-PEND5B-OCR-CAPABILITY`）、封盘 `I-11-A/a20260919-01` **任何字节** —— G2/G3 只在本工位记录里补；
2. **不下 S4 结论**、不改 `consistency_result`、不改 `numeric_conflict`；
3. **不代签行业面**（不裁 C 表启用与否、不解除 IND B 部分、不复裁行业处置规则）；
4. **不解除 `OPEN-5`**、**不放行任何参数**（`low/base/high` 仍 `null`、`_PLACEHOLDER` 维持）、**不产生 `I-11-B` 的 ACCEPT**、**不把任何 `not_readable` 改成「已验证」**；
5. **不写** 五份计划文件；**不写** `.planning` 之外任何路径（**含 `company-wiki` 产品仓**）；
6. **零 git 写**；**禁用 `git status`**；**禁止联网**（只用盘上既有产物 + 本地只读解析）。

---

## 3. 受核输入（全部只读；sha 先登记后使用）

| 代号 | 对象 | 路径（相对计划目录） |
|---|---|---|
| **IN-01** | ENVOWNER ruling（L165/L166/L174–179） | `execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` |
| **IN-02** | IND C 表 | `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` |
| **IN-03** | ACCT 等级体系 | `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md` |
| **IN-04** | S4 全部产物 | `execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/{s4_report.md,dual_path_verify.json,handoff.json,oracle.md}` |
| **IN-05** | S3 provenance（`in-02`/`in-03` 口径 `false`） | `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/provenance.json` |
| **IN-06** | PEND-5a provenance（ext-04 / ext-08 的 URL + 取回 UTC + sha256；ext-07 第三方代理） | `execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json` |
| **IN-07** | 外部件字节（本工位复算 sha256） | `execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf`、`corpus/attempt08_irmi_xiaomi_ar2025_en.pdf` |
| **IN-08** | 逐字引文载体（本工位按 line+byte_range 复核） | `execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/probe/*.extracted.txt` |
| **IN-09** | origin 本体（**只登记，不进定级**） | `execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/attempt01_hkexnews_xiaomi_ar2025_zh.pdf`（sha 与产品仓原文件相同 `ffd73376…`） |
| **IN-10** | OWNER 执行纪律 | `OWNER_DECISIONS.md` L490–L504 |

**sha 不全等 / 文件不可读 ⇒ fail-closed：该输入按未核验处理，不下结论。**

---

## 4. 判据（**冻结**）

### 4.1 G2 —— 外部件 provenance 三件套（URL + 取回 UTC + sha256）

对每个**外部抓取件** `x ∈ {attempt04, attempt08}`，`G2(x) = true` 当且仅当 **全部**满足：

- **G2a URL**：在 **IN-06**（PEND-5a `provenance.json`）的 `external_evidence` 中找到与 `x` 对应条目（ext-04 / ext-08），其 `url` 为完整 `https://…` 串；
- **G2b 取回 UTC**：同条目 `retrieved_utc` 为 `YYYY-MM-DDTHH:MM:SSZ` 形态，**且**盘上 corpus 文件的 `LastWriteTimeUtc` 与之**逐字相等**（旁证）；
- **G2c sha256**：同条目 `sha256` 与**本工位在 IN-07 上重算**的 sha256 **全等**，且与 IN-05（S3 `in-02`/`in-03`）、IN-04（S4 `own_provenance`）登记值**三方全等**；
- **G2d 记录落位**：三件套由**本工位**写入 `acct_grading.json → g2_resolution`（**不回改 S3/S4/PEND-5a**）。

**任一条不满足 ⇒ `G2 = false` ⇒ 该件** `blocked`**（不得定级）。**

### 4.2 G3 —— `external_retrieval_not_local` 口径

**判据（按 ④ 语义裁）**：凡经外部取回、用于替代不可读本地原件的港股相关 PDF，在**本工位记录**中必须登记 **`external_retrieval_not_local = true`** 且 **`substitute_not_origin = true`**，并在 `g2_g3_resolved.divergence` 中**逐条登记两边口径分歧**：

- 口径 A（PEND-5a `ext-04`/`ext-08`、S3 `in-02`/`in-03`）：`false`，语义 = 「非第三方代理」（只有 `ext-07` r.jina.ai 代理才 `true`）；
- 口径 B（IND C 表 ④、OPEN-11 L360、S4 `own_provenance`）：`true`，语义 = 「外部取回件一律标外部、永不冒充本地可核」。

**本工位采用口径 B**（依据：④ L234 + L360 + L261；④ 的 `使用条件` 明写「永不冒充本地可核」，其 `证据等级` 列本身就是 `external_retrieval_not_local`）。
**两边都不回改**，只在本工位记录登记分歧。
**若 ④ 原文不可得 / 语义无法判定 ⇒ `G3 = false` ⇒ `blocked`。**

> G3 同时约束定级：**任何被标 `true` 的件，其等级结论必须显式声明「外部取回件，永不冒充本地原件 / 不冒充 origin」**，否则该等级**不予登记**。

### 4.3 C 表来源登记规则（L166「按 C 表①/②登记来源等级」）

冻结的判别函数（对每个被定级来源 `s`）：

| 条件 | 登记行 |
|---|---|
| 文件是**发行人自己**的披露（年报 / 业绩公告 / 中期报告 / IR 可读 PDF），且同一报告期 | **①** `company_primary_disclosure`（**必须**标注 `document_type` + `period`；跨期须标 `period_mismatch_risk`） |
| 文件内容是**交易所/监管方自身**的公告行为 | **②** `regulator_primary_disclosure` |
| 券商研报 / 新闻 / 数据商 / wiki / **第三方代理渲染件** | **③** `secondary_lead_only`（**仅线索**，不得进参数与 `cited_values`） |
| 外部取回的港股年报 PDF（本地原件不可读） | **④** `external_retrieval_not_local`（**作为外部身份标记，与①/②叠加登记，永不冒充本地**） |

- **① 与 ④ 并存不是矛盾**：① 是「文件的来源级别」，④ 是「取回路径的外部身份」。二者在本工位记录里**同时登记**。
- 宿主站点不改变文件性质：港交所披露易上**发行人**的全年业绩公告仍按 **①** 登记（① 明列「全年业绩公告」）；**第三方代理（r.jina.ai）渲染的文本**一律 **③**，不得升格。
- ① 的使用条件（L231）逐条核：**原文可定位（页码/锚文本/行+字节区）**、**原始 sha256**、**期间与年报一致**。

### 4.4 会计面定级判据（E 系列 + S 系列，缺一即降级）

**E1（六要素，全部满足才 E1）**：

| # | 要素 | 本工位的核法 |
|---|---|---|
| E1a | 申报原文**本地归档**（字节落盘在本计划目录，sha 绑定） | IN-07 文件存在 + sha 复算 |
| E1b | **URL** | G2a |
| E1c | **取回 UTC** | G2b |
| E1d | **文件 sha256** | G2c |
| E1e | **逐字引文**（可定位到行 + 字节区） | 对 IN-08 按 `line`/`byte_range` 取字节，**与引文逐字全等**；且引文载体文件自身 sha256 与登记值全等 |
| E1f | **至少一条独立复核路径** | ① S4 的双库互证（U2/U3 = `CONSISTENT`）**且** ② **本工位自己**用全局 PyMuPDF/pdfminer 对 IN-07 重新抽取并命中同一引文 |

- 六要素全 ⇒ **`E1`**；
- 有归档但缺 URL/UTC/sha（**不可能出现在本工位，因为 G2 已是前置**）⇒ `E2`；仅二手 ⇒ `E3`；无 ⇒ `E0`。
- **E1 的效力受 ④ 约束**：`external_retrieval_not_local=true` 的件，E1 结论只对其**文件自身所载内容**成立，**永不等于「本地原件已核」**。

**S 系列（可采性）**：`S1` = 同期间公司原文披露 + 可定位 + doc sha256 绑定 + ≥1 独立路径复核（ACCT L56）；`S3` = 第三方独立估计（只可进敏感性带）；`S4` = 分析师示意值；`S0` = 不可得/不可核 ⇒ `_PLACEHOLDER` 不得放行。
**语言面限制单独登记**：中文锚词 0/5 的件，`usable_faces = ["en"]`，**不可作中文原文来源**（承 S4 U3）。

### 4.5 origin 本体排除规则（L165 / S4，**不得推翻**）

`HK-XIAOMI-AR2025`（origin 本体）**不进入定级**：`graded = false`、`level = null`、`admissible = false`，处置维持 S4 `NOT_USABLE` + L165「该来源不可引用，维持不可读处置」+ `STOP_EVIDENCE / not_readable`。
**任何给 origin 赋等级的输出 = 违反本判据。**

### 4.6 港股参数判定（L166 失败分支 + L179）

`hk_parameters_released` **必须为 `false`**，除非**全部**同时成立：

1. L179 的 S3/S4/S5 **三个站都走完**（S5 = 两个受理人：行业 + 会计）；
2. **行业面已复裁通过**（非本工位裁）；
3. 会计面（本工位）定级通过；
4. ENVOWNER §⑦ 的解锁前置全部满足（本工位一条也不能代解）。

⇒ **本工位的输出中 `hk_parameters_released = false` 恒成立**（行业面由父另派，本工位不代签 ⇒ 条件 2 在本工位视角内永不满足）。

### 4.7 `blocked` 触发条件（**任一即 blocked，这是合格结果**）

1. `G2 = false`（URL / UTC / sha256 三件任一缺失或复算不全等）；
2. `G3 = false`（④ 语义不可得，或本工位无法判定口径）；
3. 受核输入 sha 不全等 / 文件不可读；
4. 逐字引文核验失败（行/字节区取不出全等文本）；
5. 定级要素（E1 六要素）不全却仍要给出 E1 ⇒ **必须降级或 blocked，不得为推进而定级**。

---

## 5. 红绿变异清单（**先冻结**）

脚本：`_work/s5_grade.py`（本工位自己写，只读输入，输出到 `_work/`）。**退出码约定**：`0` = 基线判定与冻结期望全等；`2` = 触发 §4.7 `blocked`；`3` = 与冻结期望不符（判据空转或漏判）。

| # | 变异 | 期望（冻结） |
|---|---|---|
| **R0（绿·基线）** | 不改判据，真实输入 | rc=**0**：`g2=true`、`g3=true`、attempt04 → `①+④ / E1 / S1`、attempt08 → `①+④ / E1 / S1(usable=en)`、origin → **excluded（level=null）**、`hk_parameters_released=false`、attempt07（r.jina.ai 第三方代理）→ **③ / E3，不通过** |
| **M1（红·判据改弱 ⇒ 不该通过的必须能通过）** | 弱化 G2：`require_url=false`、`require_utc=false`；并弱化 C 表：`tier_filter=off`（③/代理件也按 ① 处理） | **attempt07（第三方代理渲染件）由「不通过」翻转为「通过」** ⇒ 证明判据非空、baseline 拒绝它是判据作用而非样本缺失；rc=0（变异体自身跑通）但 `should_pass_flip = true` 计入红 |
| **M2（红·origin 排除被弱化）** | `exclude_origin=false`（允许给 origin 定级） | origin **被赋等级**（应被排除）⇒ 红 |
| **M3（红·blocked 分支）** | 剥离 attempt04 记录中的 URL（模拟 G2a 缺失） | 判定 = `blocked`（§4.7-1），rc=**2** ⇒ 红（blocked 分支确实会响） |
| **M4（红·引文核验失败分支）** | 把 attempt04 的一条引文 `byte_range` 篡改 1 字节 | `E1e = false` ⇒ 该件降级/阻塞，rc=2 ⇒ 红 |

---

## 6. fail-closed 条款

1. G2/G3 补不齐 ⇒ **`blocked`**，`blocked` 是**合格结果**，不为推进而放行；
2. 定级不足以支撑港股命题 ⇒ **如实判不足**，不升格、不造绿样；
3. 引文/字节区核验不到 ⇒ 该要素判缺，不以「大概在」放行；
4. JSON 写后 `json.load` 重解析；UTF-8 **无 BOM**；**纯 LF**；
5. 结束前 `git diff HEAD --name-only`（`-c core.quotepath=false`）非 `.planning` = **0**；零 git 写；**禁用 `git status`**；
6. 任何结论都在 **L179** 与 **S4 `NOT_USABLE`** 之下，不覆盖、不推翻。

---

## 7. 写入面

**恰好**：`oracle.md` · `acct_grading.json` · `s5_acct_report.md` · `handoff.json`（四件产出）+ `_work/` 下的脚本与测量 JSON。
`.planning` 之外创建/修改 = **0**；`company-wiki` **只读且本工位不打开**（origin 只经由 PEND-5a 的本地副本登记，不进定级）。
