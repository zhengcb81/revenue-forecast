# OPEN5-S5-ACCT-GRADING · 会计面定级报告（`OPEN-5` S5 · 会计半区）

- **卡 / 步**：`OPEN-5` 恢复路径 **S5 · 行业复裁 + 会计定级** 的**会计那一半**（行业那一半由父另派，本工位不代签）
- **attempt**：`.planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-S5-ACCT-GRADING/a20260926-01/`
- **角色**：`accounting_reviewer_s5`（会计 / 披露 reviewer，**非实现者**）
- **授权（逐字）**：`execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` **L166**

  > `| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | 行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） | 任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |`

- **结论速览**：`G2 = true`、`G3 = true`（补齐）· attempt04 → **①+④ / E1 / S1** · attempt08 → **①+④ / E1 / S1（usable=`["en"]`）** · attempt07（代理件）→ **③ / E3 / S0 不通过** · origin → **排除在定级外（`level = null`）** · **`hk_parameters_released = false`** · 红绿变异 rc = `0/0/0/2/2`，与冻结期望全等
- **不授予**：不放行任何港股参数、不解除 `OPEN-5`、不产生 `I-11-B` 的 ACCEPT、不下 S4 结论、不代签行业面

---

## 0. 续跑前已盘到什么（进度盘点）

| 项 | 状态（续跑前实测） | 本轮处置 |
|---|---|---|
| `oracle.md` | **已存在并冻结**，21,551 B，sha256 `32c28419ef12bf614ea4cb4a5944e3214857dc628a4e3888ec96328992ef93ea`，mtime **早于**全部测量文件 | **直接沿用，未改一字节**（含判据 §4、`blocked` 触发 §4.7、变异清单 §5 全部已冻结） |
| `_work/s5_grade.py` | 已写成（420 行，含 §4 判据与 §5 期望），覆盖 5 种模式 | **沿用**；本轮只复跑取 rc |
| `_work/extract/` 四份自抽文本 | 已存在：`s5_attempt04_fitz.txt` 95,648 B · `s5_attempt04_pdfminer.txt` 111,987 B · `s5_attempt08_fitz.txt` 956,886 B · `s5_attempt08_pdfminer.txt` 1,029,246 B | **沿用**（E1f 独立路径② 的载体） |
| `_work/s5_measure_baseline.json` + `m1/m2/m3/m4` | **5 份测量全部已存在**（20,405 / 20,453 / 20,467 / 20,277 / 20,465 B） | **测量已做，不重做**；本轮为取 **rc** 用同一脚本、同一输入、同一判据原样复跑（覆盖同路径测量文件），rc 与 §5 冻结期望**全等** |
| `acct_grading.json` / `s5_acct_report.md` / `handoff.json` | **不存在**（前工位在"测量完成 → 落盘产出"之间被系统事件打断） | **本轮补写**（三件产出） |

⇒ **已完成并跳过的步骤**：① 冻结 oracle ② 判据脚本 ③ 四份独立抽取 ④ G2/G3 测量 ⑤ 五个变异跑批。
⇒ **本轮续做的步骤**：G2/G3 **回源核实并落进本工位记录**、C 表登记、E/S 定级落盘、港股参数判定、三件产出 + 红绿变异 rc 复核。

---

## 1. 第一步：补 `G2 / G3` 硬缺项（**只在本工位记录里补**）

### 1.1 G2 —— provenance 三件套（URL + 取回 UTC + sha256）

**回源路径**：S4 登记的缺口是「`in-02` / `in-03` 无 `url` 字段」（实测 `OPEN5-S3-REACQUISITION/a20260925-01/provenance.json` **L77–L97 确无 `url` 键**）⇒ 本工位回源读取 **PEND-5a `provenance.json` 的 `ext-04` / `ext-08`**（S4 自己的 `own_provenance` 亦载同一 URL，双向核对一致），并对 **IN-07 corpus 字节全量重算 sha256**。

| 要素 | attempt04 | attempt08 |
|---|---|---|
| **G2a URL** | `https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0324/2026032400609_c.pdf` | `https://ir.mi.com/system/files-encrypted/nasdaq_kms/assets/2026/04/28/5-29-08/Xiaomi%202025%20AR_EN.pdf` |
| 依据（文件+行） | `OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json` **L101** | 同文件 **L187** |
| 旁证 | `OPEN5-S4-…/dual_path_verify.json` **L5602** 同 URL | 同文件 **L5619** 同 URL |
| **G2b 取回 UTC** | `2026-09-24T22:09:26Z`（同文件 **L102**） | `2026-09-25T20:37:56Z`（同文件 **L188**） |
| G2b 形态 + 旁证 | 形态合 `YYYY-MM-DDTHH:MM:SSZ`；**盘上 corpus `LastWriteTimeUtc` 与之逐字相等** = `2026-09-24T22:09:26Z` | 形态合；`LastWriteTimeUtc` = `2026-09-25T20:37:56Z`（逐字相等） |
| **G2c sha256** | `d0975600c918683636d4679328fa1eaa4a7a14b53950440d53005c831829b62b` | `b787f0290513e48a95078ed2a68dc1e240da68d204e5dd9aedc59b66a7c75ec2` |
| 三方全等 | PEND-5a L105 = **本工位复算** = S3 `in-02` L81 = S4 L5597 ⇒ **4/4 全等** | PEND-5a L191 = **本工位复算** = S3 `in-03` L92 = S4 L5614 ⇒ **4/4 全等** |
| **G2d 记录落位** | 写入 `acct_grading.json → step1_g2_g3.g2_resolution` | 同 |
| 结果 | **`G2a–G2d = true`，`resolved = true`** | **`true`，`resolved = true`** |

> **G2 补齐 = `true`**。**缺什么**：S3 `in-02`/`in-03` **至今仍缺 `url` 字段** —— 该缺口**不在本工位补**（禁止回改 S3/S4/S1/封盘），只在本工位记录里补齐并登记缺口位置；S3 的 sha 与 UTC 字段本身齐全，故三方 sha 能全等。
> **不回改**：`back_written = false`（PEND-5a / S3 / S4 / 封盘均未改任何字节）。

### 1.2 G3 —— `external_retrieval_not_local` 口径（按 ④ 判定）

- **本工位采用口径 B**：两件替代件在本工位记录中一律登记 **`external_retrieval_not_local = true`** + **`substitute_not_origin = true`**。
- **依据（逐字）**：
  - `I11A-OPEN-IND/a20260924-01/ruling.md` **L234**：`| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | \`external_retrieval_not_local\` | 必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径 |`
  - 同文件 **L360**：`**外部 ≠ 本地**：所有 \`EXT-*\` 一律标 \`evidence_class=external_retrieval_not_local\`；…「本地不可核，外部获取，不得作为本地可核证据放行」。`
  - 同文件 **L261**：`- 用外部抓取件静默顶替本地原件（必须按④登记为外部）；`
- **两边口径分歧登记（均不回改）**：

| 口径 | 值 | 语义 | 出处（实测） |
|---|---|---|---|
| **A** | `false` | 「非第三方代理」（只有 `ext-07` r.jina.ai 才 `true`） | PEND-5a `provenance.json` **L109 / L195**；S3 `provenance.json` **L83 / L94** |
| **B** | `true` | 「外部取回件一律标外部、永不冒充本地可核」 | IND **L234 / L360**；S4 `dual_path_verify.json` **L5605 / L5622** |

- **判定**：④ 的**证据等级列本身就是 `external_retrieval_not_local`**，其使用条件明写「永不冒充本地可核」⇒ 口径 A 与 ④ **语义冲突**，本工位按 ④ 裁为 `true`；`divergence` 与 `back_written=false` 一并落进 `acct_grading.json → step1_g2_g3.g3_resolution`。
- **G3 约束定级**：凡标 `true` 的件，其等级结论**必须显式声明「外部取回件，永不冒充本地原件 / 不冒充 origin」** ⇒ 见第 3 节每条 `external_never_impersonates_local = true`。

> **G3 补齐 = `true`**（④ 原文可得、语义可判，未触发 §4.7-2）。

**⇒ `g2_g3_resolved = true`，`blocked` 触发条件 1/2/3/4 全部未命中，本轮不判 `blocked`。**

---

## 2. 第二步：按 IND C 表 ①/② 登记来源等级

判别函数见 `oracle.md §4.3`（冻结）。**origin 本体不进入定级**（见第 5 节）。

| 来源 | 文件性质 | C 表行 | `evidence_class` | ④ 外部标记 | 必标项（① must_label） |
|---|---|---|---|---|---|
| **attempt04** | 发行人自己在港交所披露易挂的**全年业绩公告**（`document` 逐字：`截至2025年12月31日止年度之全年業績公告（小米集团，港交所披露易原站）`，PEND-5a L111） | **①** + **④** | `company_primary_disclosure` | `true` | `document_type = 全年业绩公告（results announcement，非年度报告）` · `period = FY2025（与 origin 年报同期间）` · `period_mismatch_risk = false` |
| **attempt08** | 发行人官网**年报英文版**（`Xiaomi 2025 AR_EN（2025 年度报告英文版，发行人官网）`，PEND-5a L197） | **①** + **④** | `company_primary_disclosure` | `true` | `document_type = 年度报告英文版（annual report, EN）` · `period = FY2025` · `period_mismatch_risk = false` |
| **attempt07** | **r.jina.ai 第三方代理渲染件**（`https://r.jina.ai/https://www1.hkexnews.hk/...`，PEND-5a L166） | **③** | `secondary_lead_only` | `true` | 仅线索：**不得进参数、不得进命题 `cited_values`** |
| **origin `HK-XIAOMI-AR2025`** | 本地原件（不可读） | **不登记** | — | — | 排除在定级外 |

- **依据（逐字）**：IND **L227**（C 表标题）、**L231**（① 行，含三件使用条件）、**L232**（② 行）、**L233**（③ 行）、**L234**（④ 行）。
- **① 的三件使用条件逐条核**：**原文可定位**（页码/锚文本 + 行 + 字节区，见第 3 节引文表）✅ · **原始 sha256**（三方全等）✅ · **期间与年报一致**（FY2025，`period_same_as_original = true`，PEND-5a L113 / L199）✅ ⇒ 无需 `period_mismatch_risk`。
- **① 与 ④ 叠加不矛盾**：① = 文件的来源级别，④ = 取回路径的外部身份；宿主站点不改变文件性质（港交所披露易上**发行人**的全年业绩公告仍按 ①，① 原文明列「全年业绩公告」）。
- **② 未用到**：本批来源中没有交易所/监管方**自身公告行为**的文件 ⇒ `regulator_primary_disclosure` 本**轮零登记**（不为凑表而升格）。

---

## 3. 第三步：会计面定级（证据等级 + 理由 + 依据）

等级体系取自 `I11A-OPEN-ACCT/a20260924-01/ruling.md`：**E1/E2/E3/E0**（L66–L69）、**S1/S0**（L56/L60）；`OWNER_DECISIONS.md` **L504**：「**取证（选项 3）的证据等级由会计面定，不由取证方自定**；取不到就维持 BLOCKED，**不造绿色样例**。」

### 3.1 定级结论

| 来源 | C 表 | **E 等级** | **S 等级** | 可用语言面 | `admissible` | 理由（摘要） |
|---|---|---|---|---|---|---|
| attempt04 | ① + ④ | **E1 已核** | **S1** | `["zh-Hant"]` | **true** | E1 六要素全（本地归档 + URL + 取回 UTC + 文件 sha256 + 逐字引文 + 独立路径）；同期间公司原文披露 + 可定位 + sha 绑定 + ≥1 独立路径复核 |
| attempt08 | ① + ④ | **E1 已核** | **S1** | **`["en"]`** | **true** | 同上；**中文锚词 0/5 ⇒ 不可作中文原文来源**（承 S4 U3） |
| attempt07（代理） | ③ | **E3 二手** | **S0** | `[]` | **false** | 第三方代理渲染件 = 二手（ACCT L68 / ③ 仅可提问题），非公司原文披露，**不得支撑参数** |
| origin | — | **null（未评）** | **null（未评）** | `[]` | **false** | S4 `NOT_USABLE` + ENVOWNER **L165**「该来源不可引用，维持不可读处置」⇒ 不进入定级 |

### 3.2 E1 六要素逐条（attempt04）

| # | 要素 | 实测 | 依据（文件 + 行/字节区） |
|---|---|---|---|
| E1a | 本地归档（字节落盘 + sha 绑定） | ✅ | `OPEN5-PEND5A-…/corpus/attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf`，sha 复算 `d0975600…` |
| E1b | URL | ✅ | `provenance.json` **L101**（见 §1.1） |
| E1c | 取回 UTC | ✅ | 同文件 **L102** + `LastWriteTimeUtc` 逐字相等 |
| E1d | 文件 sha256 | ✅ | PEND-5a L105 = 本工位复算 = S3 L81 = S4 L5597（**4/4**） |
| E1e | 逐字引文 | ✅ 4/4 | 见 3.4 引文表：载体 sha 全等 + `byte_range` 取字节**逐字全等** + 本工位自抽命中 |
| E1f | ≥1 条独立复核路径 | ✅ 两路 | ① S4 双库互证 `U2 = CONSISTENT`（只读接受）② **本工位自己**用 PyMuPDF + pdfminer.six 全局重抽并命中同一引文（`_work/extract/` 四件） |

### 3.3 E1 六要素逐条（attempt08）

同表结构，差异点：**E1b** = `provenance.json` **L187**；**E1c** = **L188**（`2026-09-25T20:37:56Z`，mtime 逐字相等）；**E1d** = **L191** = 复算 = S3 **L92** = S4 **L5614**（4/4）；**E1e** = `q-08`/`q-09` 2/2 全等；**E1f** = ① S4 `U3 = CONSISTENT`（英文面 5/5、中文面 0/5）② 本工位双引擎重抽命中。

### 3.4 逐字引文（E1e）明细

| id | 引文载体（IN-08） | 载体 sha256（登记 = 复算） | `byte_range` | 逐字全等 | 本工位自抽命中 | 引文逐字 |
|---|---|---|---|---|---|---|
| q-01 | `probe/attempt04_fitz.extracted.txt` | `7d01ca6ef52a20ed3678e20bc4ef82214bc1bec5da8a83a911f59365376350d1` | `[499,560]` | ✅ | ✅ | `截至2 0 2 5 年1 2 月3 1 日止年度之全年業績公告` |
| q-02 | 同上 | 同上 | `[346,358]` | ✅ | ✅ | `小米集团` |
| q-03 | 同上 | 同上 | `[2306,2410]` | ✅ | ✅ | `比增長25.0%。業務分部來看，2025年，我們的「手機×AIoT」分部收入為人民幣3,512` |
| q-04 | `probe/attempt04_pdfminer.extracted.txt` | `21ba5eadedc28849d50ecae4416e1e7cc777b8d560b3e0a60e15089dfe880992` | `[11799,11905]` | ✅ | ✅ | `5.4% 。「手機×AIoT」分部毛利率達到歷史新高的21.7% ，同比增長0.5個百分點 。2025` |
| q-08 | `probe/attempt08_en_probe.extracted.txt` | `a6a918d1c4c6ea64ad1a58f9c04cbb412a91c6bc42c23ffb37bcb944f12b24d4` | `[7517,7633]` | ✅ | ✅ | `RMB457.3 billion, representing a year-over-year increase of 25.0%. Segment-wise, in 2025, revenue of our smartphone ` |
| q-09 | 同上 | 同上 | `[4641,4653]` | ✅ | ✅ | `Gross profit` |
| q-07（对照） | `corpus/attempt07_rjina_xiaomi_ar2025_zh_proxy.txt` | `a44064f13f6ee8a09093ff945ccfa3842d13339764f63f825583105e534684de` | `[194,214]` | ✅ | ✅ | `Number of Pages: 415` |

> 引文**核的是字节、不是印象**：`byte_range` 处取字节后 `decode('utf-8')` 与登记引文**逐字全等**，且载体文件自身 sha256 与登记值全等（§4.4 E1e 的两半）。

### 3.5 独立路径与自抽工件（E1f）+ 诚实登记的限制

- 本工位自抽工件 sha256：`fitz04 = 5d20c281…` · `pdfminer04 = 21ba5ead…` · `fitz08 = 990075a6…` · `pdfminer08 = f5d1077a… / f24c26b5…`（见下）。
- **限制（如实登记，不藏）**：`_work/s5_extract_determinism_attempt04.json` 显示 attempt04 pdfminer 自抽工件 **3 次独立进程字节稳定**（`21ba5ead…`，与 PEND-5a 探针工件同 sha；连同本轮 5 次 `s5_grade` 跑批共 **8 次观测全同**）；`_work/s5_extract_determinism_attempt08.json` 显示 attempt08 pdfminer 自抽工件在 **6 次独立进程中出现 2 个 sha**（`f5d1077a…` / `f24c26b5…`，跨跑批亦然）—— 即**自抽工件字节不稳定**。
- **探针口径说明（不粉饰）**：该探针只对 **pdfminer 自抽文本**做命中判定，故 attempt04 的 `raw = false`（q-01～q-03 的引文载体是 **fitz** 抽取件，跨引擎 raw 匹配本就不成立），其**空白归一化命中 = true**；权威的逐引文判定是按载体引擎配对的 `s5_measure_*.json → quote_checks`（7/7 `byte_exact = true` 且 `found_in_own_extraction = true`）。
- **为何不降级**：E1d 的 sha256 针对 **PDF 本体**（三方全等、恒定）；E1e 锚定**登记引文载体**的字节区全等；E1f 锚定「**同一引文在本工位自抽文本中命中**」，两种布局变体下 raw 与空白归一化**全部命中**。⇒ 判据不以"自抽工件字节全等"为条件，故等级不变；**若行业面/owner 认为自抽工件须字节可复现，请在会签时提出，本工位按其要求另行复测**。

---

## 4. 第四步：港股参数判断 —— **必须维持 `_PLACEHOLDER`**

| 条件（`oracle §4.6`，须全部成立） | 本工位视角 |
|---|---|
| 1. L179 的 S3/S4/S5 **三个站都走完**（S5 = 行业 + 会计两个受理人） | ❌ 行业那一半未走 |
| 2. **行业面已复裁通过**（**非本工位裁**） | ❌ **本工位不代签** |
| 3. 会计面（本工位）定级完成 | ✅ 四步完成 |
| 4. ENVOWNER §⑦ 解锁前置全部满足 | ❌ 本工位一条也不能代解 |

- **结论：`hk_parameters_released = false`（恒成立）**，`low/base/high = [null, null, null]`，`_PLACEHOLDER` 维持，**港股命题零产出**。
- **L179 压顶（逐字）**：`即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 \`_PLACEHOLDER\`）。`
- **L166 失败分支（逐字）**：`任一面未过 ⇒ 港股参数继续 \`_PLACEHOLDER\``；且「**本载体不代行**」⇒ 两个 reviewer 各自行使专业裁定权。
- **如实判足不足**：本工位只给出**来源可采性与证据等级**；港股命题能否成立还取决于 (a) 行业面复裁与 **C 表是否启用**（IND **L240/L241**：`环境 owner 解决可读性后，若新 attempt 实测仍读不出原文 ⇒ B 部分（保持不可用）继续有效，C 表不启用`）——**由行业面裁，本工位不代签**；(b) L179 未解除；(c) 所需分部数据是否齐备。⇒ **本工位不声称"定级已足以支撑港股命题"**，不为推进而升格。

---

## 5. 与 S4 的边界衔接（只读接受，不下 S4 结论）

| S4 已定（只读接受） | 本工位的用法 |
|---|---|
| `consistency_result = NOT_USABLE`（触发面 = **U1 origin 本体**，`numeric_conflict = 3`） | **不改、不下 S4 结论**；origin 按 **L165**「该来源不可引用，维持不可读处置」**排除在定级外**（`graded = false`、`level = null`、`admissible = false`） |
| `U2 attempt04 = CONSISTENT`、`U3 attempt08 = CONSISTENT` | 作为 E1f **路径①**（双库互证）消费；本工位另跑**路径②**（自己重抽），两路齐 → E1f 成立 |
| S4 提请：`s4_report.md` **L198**（逐字）`替代件 attempt04 / attempt08 的双路径互证已成立（U2/U3 = CONSISTENT）⇒ S5 请按 IND C 表 ④ … + 会计面定级补裁` | 本工位照办：①+④ 登记 + E/S 定级 |
| S4 提请 **L199**：`G2/G3 是 S5 引用前必须先补的 provenance 硬缺项` | 本工位**已在自己记录里补齐**（§1），**未回改 S4/S3/S1/封盘任何字节** |
| S4 提请 **L200**：`L179 仍然压顶` | **接受**，本工位即使判过也不解除（§4） |
| S4 `own_provenance` 标 `external_retrieval_not_local = true`（L5605/L5622） | 与 S3/PEND-5a 的 `false` **口径分歧登记在案**（§1.2），两边均不回改 |

---

## 6. 给行业面的**会签提请**（`S5` 另一半 · 父另派）

> 致 `OPEN-5` **行业 reviewer**（S5 L166 受理人之一）。本工位只交会计半区，请**独立行使行业专业裁定权**，不要以本报告替代行业面结论。

1. **请会签本会计面的来源登记与等级**：attempt04 = `①+④ / E1 / S1`（`document_type=全年业绩公告`、`period=FY2025`）、attempt08 = `①+④ / E1 / S1`（`usable_faces=["en"]`）、attempt07 = `③ / E3 / S0 不可采`。
2. **请裁定 C 表是否启用**（IND **L240/L241**）—— 这是行业面裁权，**本工位不代签、不解除 IND B 部分**。
3. **请确认 attempt04 的文件类型用途**：它是**全年业绩公告**（非年度报告），会计面已按 ① must_label 标注文件类型与期间；若行业面要求年报本体口径，请指示是否需另行取文。
4. **请确认 attempt08 的语言面限制**：中文锚词 0/5 ⇒ `usable_faces=["en"]`，**不可作中文原文来源**；若命题需要中文原文，请另行取证（不得由本英文面代签）。
5. **请复核 G3 分歧登记**：口径 A（`false`，S3/PEND-5a）vs 口径 B（`true`，④/OPEN-11/S4）；本工位按 ④ 裁 `true` 且**两边均不回改**——如行业面有异议，请在会签中提出，仍不得回改前站。
6. **边界确认**：两面未齐前，`hk_parameters_released` 恒为 `false`；本报告**不解除 `OPEN-5`、不放行任何参数、不产生 `I-11-B` 的 ACCEPT**。
7. **未证事项同步**（不造绿样）：attempt08 pdfminer 自抽工件跨进程出现 2 个 sha（§3.5）——如需字节可复现性作为行业面条件，请一并指示。

---

## 7. 红绿变异（`oracle §5` 冻结清单，脚本 `_work/s5_grade.py`）

| # | 变异 | 期望（冻结） | 实测 rc | 结果 |
|---|---|---|---|---|
| **R0 绿·基线** | 不改判据，真实输入 | `rc=0`：`g2=g3=true`、attempt04 → `①/E1/S1`、attempt08 → `①/E1/S1(usable=en)`、origin → **excluded（level=null）**、`hk=false`、attempt07 → `③/E3` **不通过** | **0** | ✅ 与期望全等（`expectation_met = true`） |
| **M1 红·判据改弱** | `require_url=false`、`require_utc=false`、`tier_filter=off` | attempt07 由「不通过」**翻转为「通过」** ⇒ 判据非空转 | **0** | ✅ 红：`should_pass_flip = true`（attempt07 `pass=true`、tier 翻成 ①）——证明 baseline 拒绝它是**判据作用**而非样本缺失 |
| **M2 红·origin 排除被弱化** | `exclude_origin=false` | origin **被赋等级**（应被排除） | **0** | ✅ 红：`origin_grade_flip = true`（`level = "E1/S1 (MUTANT)"`） |
| **M3 红·blocked 分支** | 剥离 attempt04 的 URL（模拟 G2a 缺失） | `verdict = blocked`（§4.7-1），`rc=2` | **2** | ✅ 红：`blocked_reasons = ["G2 unresolved for attempt04"]`，attempt04 降 `E2/S0` |
| **M4 红·引文核验失败** | attempt04 `q-01` 的 `byte_range` 篡改 1 字节 | `E1e=false` ⇒ 降级/阻塞，`rc=2` | **2** | ✅ 红：`byte_exact=false` ⇒ attempt04 降 `E2/S0`，`verdict=blocked` |

**红绿结论**：5/5 与冻结期望全等。**判据改弱后一个不该通过的来源（attempt07 代理件）确实能通过**（M1），**`blocked` 分支也确实是红的**（M3/M4 rc=2），**origin 排除也不是空转**（M2）。

---

## 8. 写入面与纪律自查

| 项 | 值 |
|---|---|
| 写入面 | 仅 `execution_runs/OPEN5-S5-ACCT-GRADING/a20260926-01/`（`oracle.md`·`acct_grading.json`·`s5_acct_report.md`·`handoff.json` + `_work/`） |
| `.planning` 之外创建/修改 | **0**（含 `company-wiki` 只读且未打开） |
| git 写 | **0**；**未用 `git status`**；仅用 `git diff HEAD --name-only` 与 `git ls-files --others`（只读） |
| `git diff HEAD --name-only` | 总数 3829 → 3830（**全在 `.planning/`**，漂移来自同工作区其他会话在计划目录内的变动），**非 `.planning` = 0（多次复测恒为 0）** |
| 非 `.planning` untracked | 48（全部为既有 `.tmp-r41-mutation/*` 历史路径，非本工位创建） |
| 联网 | **否**（只用盘上既有产物 + 本地只读解析） |
| 前站字节 | S4 / S3 / S1 两站 / 封盘 `I-11-A` **零写入** |
| 五份计划文件 | **未写** |

## 9. 本工位**没有做**的事（逐条）

1. **未推翻 S4**：`NOT_USABLE` 是 S4 的结论，本工位只读接受，`consistency_result` / `numeric_conflict` 一字未改。
2. **未代签行业面**：不裁 C 表启用与否、不解除 IND B 部分、不复裁行业处置规则。
3. **未下 S4 结论**、未把任何 `not_readable` 改成「已验证」。
4. **未放行港股参数**：`hk_parameters_released = false`，`_PLACEHOLDER` 维持。
5. **未解除 `OPEN-5`**、**未产生 `I-11-B` 的 ACCEPT**（`OWNER_DECISIONS L502`：授权是许可不是动作）。
6. **未给 origin 赋任何等级**（排除在定级外，`level = null`）。
7. **未改 S4 / S3 / S1 两站 / 封盘任一字节**（G2/G3 只在本工位记录里补）。
8. **未写**五份计划文件；**未写** `.planning` 之外任何路径（含 `company-wiki`）。
9. **零 git 写**、**未用 `git status`**、**未联网**。
10. **未修** attempt08 pdfminer 自抽工件的字节不稳定（如实登记为限制，见 §3.5，不以其为放行条件）。
