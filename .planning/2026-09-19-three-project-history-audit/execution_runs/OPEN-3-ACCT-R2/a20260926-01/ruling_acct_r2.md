# `OPEN-3-ACCT-R2` · `a20260926-01` — `OPEN-3` E1 等级复裁（会计/披露 reviewer）

- **卡 / attempt**：`OPEN-3-ACCT-R2` / `execution_runs/OPEN-3-ACCT-R2/a20260926-01`
- **role**：`accounting_reviewer`（会计/披露 reviewer，**非实现者**）｜ **父**：`session-19074bf0-0205-4315-af73-9db57597275a`
- **被裁对象（全程只读）**：`execution_runs/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/`（origin 字节 62,953 B + 5 件取回件 + provenance + 自报形态）
- **规则来源（只读）**：`I11A-OPEN-ACCT/a20260924-01/ruling.md`（E0–E3 / S0–S4）· `I11A-OPEN-IND/a20260924-01/ruling.md`（C 表）· `OPEN3-E1-ACCT-RULING/a20260924-01/ruling.md`（上轮裁定与 R2 复裁条件）· `OWNER_DECISIONS.md` §二十七 #2 / §三十 / §三十一 / §三十二 / L543
- **oracle**：本目录 `oracle.md`（**先冻结**，五问判据 §一 · 方法 §二 · 全量比对 §三 · `blocked` 触发 §四 · 变异 §五 · 不授予 §六；§5.2 为执行后追加的实测）
- **网络**：**0 次请求**（L543 按卡适用于定级工位；字节已在盘 ⇒ 不需要联网）
- **先行结论（一句话）**：
  > **RULING —— `E1 = BLOCKED-PARTIAL`（五要素 4/5：①②③⑤ 经我独立实测成立、④ 因 C5 不成立）· `S = S1`（IND C 表 ①类 + `external_retrieval_not_local=true` + kind `current_report`→`raw/other/`，**但不等于放行**）· 既有 4 份语料降 `E3` · `origin_bytes_dimension_resolved = true`（字节这一维已解除实质条件）· 但 `BLOCKED-NEEDS-ORIGIN-BYTES` / `OPEN-3` / `B1` / `B2` 一律不由本卡解除 · `releases_nothing = true`**
  >
  > **触发本裁定方向的关键事实，是我独立复现出来的第三项（派单与 R2 自报都没有）**：`EX99.1` 同一句 **origin 与 as-filed 归档 = `amplifying`，而既有语料 A/B = `amplifies`**（字节级 1/0 ↔ 0/1），另 `corpusA` 缺 8-K 签名页整段 ⇒ **C5 成立**。

---

## ① 身份与授权链（逐字回源，不采信派单转述）

| 环节 | 原文（逐字） | 出处 |
|---|---|---|
| 定级权归属 | 「…仍标 `external_retrieval_not_local` 如实；**等级判定归会计面**；本裁**不解除 `OPEN-3`、不产生 ACCEPT**」 | `OWNER_DECISIONS` **§二十七 #2** |
| 落点口径 | 「**8-K 按诚实 kind `current_report` 落 `company-wiki/companies/{entity}/raw/other/`** —— **不改 `canonical_writer` 映射、不谎报 `quarterly_report`**」 | **§三十一 #1** |
| 对 §二十七 #2 的澄清 | 「该条写的 `…/raw/financial_reports/{kind}/` **按「`raw/…` 下」理解，含 `raw/other/`** —— 本节即该澄清的**唯一授权出处**」 | **§三十一 #2** |
| 等级工位纪律 | 「派 `1e143a7e` = `OPEN3-E1-ACCT-RULING`。**只定级、不重取**（禁联网；若必须看原站字节 ⇒ 判 `BLOCKED-NEEDS-ORIGIN-BYTES` 而**不自己去取**）；`fail-closed`——**不得为推进链抬高等级**；`releases_nothing=true`」 | **L543（§二十六 #3）** |
| 上轮给 R2 的复裁条件 **C1** | 「**origin 响应字节落进本计划目录**…⇒ ① 可升 ✅ ⇒ 本卡新建 `R2` 载体复裁（或由 ACCT 出 `OPEN-3-ACCT-R2`，ACCT **L201**）」 | 上轮 ruling **L247** |
| 上轮 **C5** | 「**若 R1 落盘后内容与现有语料不一致** ⇒ 现有 4 文件降 E3、8 条引文作废，重新取证 … **fail-closed 反向也成立**」 | 上轮 ruling **L251**（另 L293 反例 4） |
| 上轮 ④ 恢复规则 | 「R1 origin 落盘后，**在新载体上重跑同一套字节区校验**（不得复用本卡结论），通过后方可把引文升级为"已核"引用」 | 上轮 ruling **L163** |
| 上轮 ⑤ 恢复规则 | 「若 R1 落盘 origin 字节，则应把新路径登记为**第三条路径**并与现有两路**再做一次全量比对**（追加式）」 | 上轮 ruling **L185** |
| 禁改定义（对称） | 「E1 定义不得被悄悄改动 … 放宽与收紧两个方向对称适用」 | 上轮 ruling **L190**（引 ACCT L190） |

⇒ **链条闭合**：`§二十七 #2`（定级权归会计面）→ `L543`（只定级、不重取、fail-closed、releases_nothing）→ 上轮 `L247/C5/L163/L185`（R2 复裁条件）→ **本卡执行复裁**。

**L543 适用性（我自己的判断，不采信派单）**：L543 原文点名的是定级工位，其「禁联网」在 R2 取证卡被 `progress L1244` 论证为不适用（那是取证卡）；**本卡是定级卡**，与 L543 的受约束对象同类，且派单明写「本卡是定级、不重取」「不需要联网」⇒ **我按 L543 的最严读法执行：零联网**。副作用（已登记为局限）：R2 自报的响应头（`Content-Length`/Akamai/`Set-Cookie`）**无原始头部件落盘**，我无法独立复核，只能核盘上字节与内容。

---

## ② 待裁对象与只读自证（sha256 = 本工位实测）

| 文件 | 字节 | sha256（实测） | 与自报/上轮登记 |
|---|---|---|---|
| `origin_bytes.bin` | 62,953 | `cf84c29048ab314e…` | ✅ |
| `…d291965d8k.htm.origin` | 28,665 | `a3d0bbf6411bb2b2…` | ✅ |
| `…d291965dex991.htm.origin` | 34,288 | `47a0a4a1d6a335ff…` | ✅ |
| `_identity_…index.htm` | 17,557 | `618f010b6e56597c…` | ✅ |
| `_independent_…submission.txt` | 2,721,504 | `d82838ac92ed3e8b…` | ✅ |
| `_mutation_R1_sec_block_page.htm` | 4,819 | `2922be224c135e1d…` | ✅（含 `Undeclared Automated Tool` 拦截标记，实测命中） |
| R2 `provenance.json` | 19,965 | `21ce23f958e80c2b…` | ✅ |
| R2 `oracle.md` | 19,748 | `977d2069952d7f15…` | ✅ |
| 语料 A `Item7.01.md` / B `…verify-w3c…txt` | 3,789 / 5,183 | `096c7d9d…` / `5927de03…` | ✅ |
| 语料 A `Exhibit99-1.md` / B `…verify-w3c…txt` | 27,586 / 28,536 | `20392f0e…` / `56b0460b…` | ✅ |
| `I11A-OPEN-ACCT/…/ruling.md` | 37,355 | `f3040df0081f6653…` | ✅（与上轮 §1.3 一致） |
| `I11A-OPEN-IND/…/ruling.md` | 39,207 | `8bc685a4964a7fe6…` | ✅ |
| `I11A-OPEN-MERGE/…/merge_ruling.md` | 49,062 | `2d214bab861be4ff…` | ✅ |
| 上轮 `OPEN3-E1-ACCT-RULING/…/ruling.md` | 39,830 | `49799cca2e8cc006…` | ✅（读前读后一致） |
| `OWNER_DECISIONS.md` | 96,826 | `9075f9aac00ded42…` | ⚠ 上轮登记 `068f39e1…`/73,108 B → 已追加 §二十八～§三十二，属**追加式演进**，非篡改；引用以本工位实测为准 |

- **`origin_bytes.bin == 8-K ∥ EX99.1`** 逐字节成立（偏移 `[0,28665)` / `[28665,62953)`）。
- 被裁定对象与上游载体在本卡读取前后 **sha 全部一致 ⇒ 0 字节变更**。

---

## ③ 五问逐条（结论 · 依据 · 反例 · 兼容影响 · 恢复规则）

### Q1 —— `E1` 五要素在 **origin 层**是否全部成立？ ⇒ **4/5（①②③⑤ ✅、④ ❌）**

| # | 要素 | 判定 | 依据（全部为本工位本地实测） |
|---|---|---|---|
| ① | 申报**原文**本地归档 | **✅** | 两份响应体在盘（28,665 / 34,288 B）；`origin_bytes.bin` = 二者拼接；**剥注入后与 as-filed 归档 inner 逐字节相同**：8-K `28,559 B / 6328d056…`（归档偏移 1,178）、EX-99.1 `34,070 B / 4cb79b6e…`（归档偏移 29,857）；文件 mtime `13:29:40Z–13:30:36Z` 与登记窗口一致 |
| ② | 文件 sha256 | **✅** | 5 件 + `origin_bytes.bin` + block page 实测 sha 与 R2 `origin_sha256` 五值逐一相同 |
| ③ | 取回 UTC | **✅** | `provenance` 四窗口 + `attempts[]` 读秒 + mtime 互证；窗口式为上轮 L148 已接受的诚实形式 |
| ④ | 逐字引文**在 origin 载体上重跑** | **❌** | 我自己重跑：**P-A 8/8、P-B 8/8、M1（去空白）8/8、M2（空白敏感）7/8、M3（严格）3/8**，原始 ASCII 锚点 2/2 —— 数字与 R2 自报**完全一致**；**但** Q2 已裁 C5 成立 ⇒ 依上轮 **L251**「8 条引文作废、重新取证」⇒ 以既有语料为基的引文集**作废**，④ 在本卡不成立 |
| ⑤ | 至少一条独立复核路径 | **✅（带限定）** | as-filed 完整申报（`d82838ac…`）与 origin 剥注入内容**逐字节相同（两份）**；四对全量 token 比对**数值矛盾 = 0** |

**反例（会推翻上表）**：
1. 任一 origin 件 sha 实测 ≠ 自报（**未发生**）⇒ ①② 同时 ❌、整件 `blocked`；
2. 任一引文连 M1 都不命中（**未发生**：8/8）⇒ ④ 直接 ❌ 且 C5 判据 1 命中；
3. 若第三条独立路证明 **origin 该词才是错的** ⇒ ① 的原文性崩、⑤ 不能自证 ⇒ ①⑤ ❌，**整件 ≤3/5**；
4. owner 明文登记 E1 定义放宽（ACCT **L190** 对称）⇒ 定义层变化，须新建载体追加登记，**我无权自行改**。

**兼容影响**：
- `OPEN-3` 的 **MERGE §3.4 解锁条件 3**（8-K + EX99.1 本地归档 E1 → ACCT `OPEN-3-ACCT-R2` → IND `ruling_r2.md`）**仍未满足** —— 本卡是该条件的判定环节，结果 = 未过；
- 可用范围 **按 E2 执行**：仅叙述与风险提示；**不得**支撑参数、**不得**出现「已核」「已按新分部建模」（ACCT L154/L163）；
- 上轮从「缺 1（①）」变为「缺 1（④）」：**缺口换了位置，不是进度跃迁**（如实记录，不解锁）。

**恢复规则（追加式，须新建载体，不回改本件）**：见 **Q5 的 RC1–RC5**。

---

### Q2 —— ⭐ `origin ↔ 既有语料` 一致性（**C5 裁定**） ⇒ **构成「不一致」；4 份语料降 `E3`**

#### (a) Q1 空格差 —— **不构成 C5**

- **实测**：origin 原始 HTML = `(1)&#160;Agents … (2)&#160;Devices`（**U+00A0 NBSP ×2**）；语料 = `(1)Agents … (2)Devices`（**0 个空白字符**）。
- **我的重跑**：M1（去空白）命中、M2（空白折叠）**未命中**（Q1 是唯一 M2 miss）；M3 严格未命中。
- **判定**：**纯空白类差异** —— 去空白后逐字相同、全量 token **0 差** ⇒ 不满足 C5 判据 1–4 中的任何一条（判据 1 要求 M1 不命中，实测命中）。**不降级**，但**必须披露**：这是语料的**空白保真缺陷**（语料把 NBSP 整个丢了，不是"换成另一个空格"）。
- **反例**：若差的是字符/数字（例如 `(1)Agents` 实为 `(1)Xgents`）⇒ 判据 1/3 命中 ⇒ 立即转 C5 成立。

#### (b) `edge_injected_script` 双命中 —— **不构成 C5**

- **实测**：`[28544,28650]`（8-K）、`[34147,34253]`（EX99.1）原始字节 == 自报 `script_html`，**两处逐字节相同**；出现次数 8-K=1、EX99.1=1；**EDGAR index 与 as-filed 完整申报 = 0/0**；剥离后 8-K `28,559 B / 6328d056…`、EX99.1 `34,182 B / 557161af…` 全部与自报一致。
- **判定**：这是**传输层注入、非申报正文**：(i) 归档内 0 命中、(ii) 剥离后正文与归档**逐字节相同**、(iii) 既有语料是文本渲染，**构造上不含 `<script>`**（渲染器必然丢弃）⇒ 三者同时成立 ⇒ **不构成正文不一致**。
- **必须随判定传播的登记**：`raw_sha256` 与 `stripped_sha256` **双登记** + 字节跨度；后续任何产品仓落点**必须双 sha 同登**。
- **反例**：若剥离后 ≠ 归档（即注入改了正文）⇒ C5 判据 4 命中 ⇒ **origin 自身保真崩**，降的不是语料是 origin（并连带 S 等级）。

#### (c) 第三项事实（**我独立发现，派单与 R2 自报均未提及**）—— **构成 C5**

按上轮 **L185** 要求做了「与现有两路的全量比对」（`verify_e1.py` → `_verification_raw.json`）：

| 发现 | 字节级证据 | 是否可归入排版归因 |
|---|---|---|
| **EX99.1 同一句 `…every person, ▯ their agency and ambition…`**：origin/归档 = `amplifying`；语料 A/B = `amplifies` | `origin_ex: amplifying=1, amplifies=0`；`archive: 1/0`；`corpusA: 0/1`；`corpusB: 0/1` | **否**（词形差异） |
| **`corpusA` 8-K 缺签名页整段**（`Date: September 2, 2026 / /s/ Alice L. Jolla / Corporate Vice President and Chief Accounting Officer`） | origin 与 `corpusB` 均有；`corpusA` 正文止于 `104 Cover Page Interactive Data File` | **否**（整段缺漏） |

**已逐条归因、不构成矛盾的差异（列全，避免夸大）**：
- origin 独有 `{0000789019, 09}` = origin 的 iXBRL header 事实（不可见元数据；`corpusB` 含、`corpusA` 不含）；
- `corpusA` 独有 `{06, 20, 31}` = r.jina.ai 渲染头 `Published Time: Wed, 02 Sep 2026 20:31:06 GMT`；
- `corpusB` 独有 `{21, 5, 8}` = html2txt 输出的 `alt="Slide 21/5/8"` 图注（origin 标签属性被剥除）；
- `corpusB` 独有单词碎片 = 硬换行把 `notesthreepoint…member` 等长词截断。
- ⇒ **数值侧无法归因的矛盾 = 0**（`decision.md L27` 的「互相矛盾的被引用数值」失效条件**未触发**）——**但 C5 判据 3 是词/段级，已命中**。

> **一个结构性观察（重要）**：`amplifying/amplifies` 这处错**同时存在于语料 A 与语料 B**，而这两条正是上轮 ⑤ 用来互证的路径。**两条同源转写路径共享同一个错 ⇒ A/B 互证在结构上不可能发现它**。这正是 origin 层的价值，也正是 C5 必须生效的理由。

#### 裁定

> **RULING —— 构成「不一致」⇒ C5 触发：既有 4 份语料文件（`MSFT_8K_2026-09-02_Item7.01.md`、`…Item7.01.verify-w3c-html2txt.txt`、`MSFT_8K_2026-09-02_Exhibit99-1.md`、`…Exhibit99-1.verify-w3c-html2txt.txt`）一律降 `E3`（仅可用于提出问题），8 条引文作废，须重新取证。**

- **依据**：上轮 **L251（C5）** / **L293（反例 4）** + ACCT **L155（E3 = 研究稿、web 工具转录、新闻…）** —— 本 4 件本就是工位对 `web_fetch` 返回文本的转写（其 `byte_composition` 自述），现已**实测与申报原文有一处词级不符、一处整段缺漏**。
- **方向未定（如实）**：我**无法**断定错在 origin 侧还是语料侧 —— origin 与 as-filed 同为 R2 一会话取回，语料 A/B 同为工位转写；本卡禁联网，不能用第三条路定向。**所幸不影响定级**：见 Q3 的双向论证。
- **反例（什么会推翻本裁定）**：RC1 的第三条独立路证明 origin 侧错 ⇒ 降的改为 origin（①⑤ 崩），语料 A/B **不降 E3**；证明语料侧错 ⇒ 维持本裁定；证明"两边都对"（例如原文有两个版本）⇒ 需 owner 裁版本口径。
- **兼容影响**：
  - IND 侧 `evidence_class` 登记：旧 `EXT-*` 条目按 IND **L198** 永久保留（只可新增 `local_ingested_at`），**不得**被改写；**新增** `E3` 标注与 divergence 登记须落在**新载体**；
  - 任何**已引用**这 4 件语料做"已核"表述的下游文本，须在新载体上撤回该表述（本卡不回改任何旧文本）；
  - `corpusA` 缺签名页 ⇒ 引用"8-K 已签署/日期"时**不得**以 `corpusA` 为据。

---

### Q3 —— `E1` 等级 ⇒ **`BLOCKED-PARTIAL`**（四选一，fail-closed）

**按 `I11A-OPEN-ACCT` L66/L153/L154/L155/L156 逐条**：①✅ ②✅ ③✅ ④❌ ⑤✅ ⇒ **4/5**。

| 候选 | 是否采纳 | 理由 |
|---|---|---|
| `E1-COMPLETE` | **否** | ④ 因 C5 引文作废；上轮 **L543「不得为推进链抬高等级」** 直接禁止 |
| `E2`（作等级） | **否** | 与「origin 字节已落本地归档、sha 可复算」事实冲突，会错报证据状态（同上轮 §4.2） |
| `E3`（对整件） | **否** | origin 层①②③⑤实测成立，整体不属"研究稿/转录"；**E3 只用于 4 份语料**（见 Q2） |
| **`BLOCKED-PARTIAL`** | **✅** | partial = 4/5 实测成立（不抹掉 origin 取证成果）；blocked = ④ 未达成、C5 未清，fail-closed |

**双向论证（无论错在哪一侧，E1 都不成立 —— 因此不需要联网也能定级）**：
- **若错在语料侧** ⇒ C5 触发 ⇒ 4 文件 E3 + 8 引文作废 ⇒ **④ ❌** ⇒ E1 不成立；
- **若错在 origin 侧** ⇒ ①「申报**原文**」的原文性不成立，且 ⑤ 的独立件与 origin **同代码同会话**不能自证 ⇒ **①/⑤ ❌** ⇒ E1 更不成立。

**附加要件（ACCT L153）已核**：分部重分类的**重述后基期分部数据**在 origin 载体上可定位（Q6 `$61,672 $64,441 $67,438 $74,576 $268,127`，M1/M2 均命中）+ FY27Q1 outlook（Q7 `$75.15 to $75.75 billion` / `$14.7 to $15.2 billion`）⇒ 该要件**在 origin 层成立**（记录事实，**不构成解锁**）。

**反例**：C5 被 RC1 推翻并完成 RC2–RC5 ⇒ 五要素可复裁 5/5 ⇒ `E1-COMPLETE`（须新建 `OPEN-3-ACCT-R3`）。
**兼容影响**：`OPEN-3` 证据面**维持 BLOCKED**；MSFT 四参数与新两分部参数**一律维持未放行**；`H-US-MSFT-SEG-01` 维持 `pending_professional_decision`；I-07-E 分部口径维持未冻结。
**恢复规则**：Q5 的 **RC1–RC5**。

---

### Q4 —— `S` 来源等级 ⇒ **`S1`（带三项强制登记；S1 ≠ 放行）**

**按 IND C 表逐项**（`I11A-OPEN-IND` L229–L234）：

| 行 | 适用？ | `evidence_class` | 判定要点 |
|---|---|---|---|
| **①** 同一发行人、同一报告期的其他可读原文官方文件 | **是（内容类型）** | `company_primary_disclosure` | accession `0001193125-26-380280`、`period_of_report 2026-09-02`、`accepted 2026-09-02 16:30:24`、`Item 7.01/9.01`；**原文可定位**（锚文本实测 2/2 + 8 条引文定位）+ **原始 sha256** + 同期 |
| ② 交易所/监管公告 | 否 | `regulator_primary_disclosure` | 存管处为 SEC EDGAR，但被引对象是公司自身披露 ⇒ 归 ①；跨期文件才需 `period_mismatch_risk` |
| ③ 券商研报 / 新闻 / 数据商 / wiki | 否 | `secondary_lead_only` | 不适用（且这正是语料 4 件现在的处境） |
| ④ 外部抓取（本地原件不可读） | **是（取得方式）** | **`external_retrieval_not_local`** | 本件系联网取回 ⇒ **该 flag 必须 = `true` 且永久保留**（IND **L198/L360**：外部条目永久保留，只可新增 `local_ingested_at`，不得改写为 local） |

**按 ACCT S 表（L56–L60）**：
- **`S1`** = 同一期间原文披露 + 可定位锚文本 + doc sha256 已绑定 + **至少一条独立路径复核** ⇒ **四项在我实测下成立**（独立路径 = as-filed 归档逐字节；限定：与 origin 同采集代码 —— 该限定随判定传播）。
- `S2/S3/S4` 不适用（本件非准则化口径、非第三方估计、非示意值）；`S0` = 不可得/不可核 —— 与"字节在盘且经复算"冲突，**不采用**（否则错报可用性）。

**三项强制登记（缺一即视为登记不足）**：
1. `external_retrieval_not_local = true`（**永久**，不得改写）；
2. **`kind = current_report` → 落 `company-wiki/companies/{entity}/raw/other/`**（§三十一 #1：不改 `canonical_writer` 映射、**不谎报** `quarterly_report`）；
3. **`raw_sha256` + `stripped_sha256` 双登记** + `edge_injected_script` 字节跨度（8-K `a3d0bbf6…/6328d056…`；EX99.1 `47a0a4a1…/557161af…`，inner `4cb79b6e…`）。

**S1 ≠ 放行（必须写进任何下游引用）**：S1 只是参数放行的**必要条件之一**。当前 **E1 = `BLOCKED-PARTIAL`**、**ACCT L226 四要件 0/4 明确满足**（可复算观测量 ✅／可核基础 ⚠ 部分／**非实现者 `decision_sha256` ❌**／追加式版本化 ❌）、**MERGE 七条 7/7 未满足** ⇒ **任何 MSFT 参数一律维持未放行**。
**反例**：RC1 证明 origin 侧错 ⇒ S 降 `S0` 并连带 ① 重判；owner 明文改 E1/S 定义（L190 对称）⇒ 须追加登记。
**恢复规则**：RC1–RC5 完成并复裁 E1 ⇒ S1 由"来源层成立"升为"可进入 L226 四要件评估"。

---

### Q5 —— 解除还是维持 `BLOCKED-NEEDS-ORIGIN-BYTES` ⇒ **字节这一维已解除（`origin_bytes_dimension_resolved = true`）；名目的正式解除与其余阻断一律不由本卡处理**

**两个层次分开裁（混同即违规）**：

| 层次 | 判定 | 理由 |
|---|---|---|
| **(i) 字节这一维的实质条件** | **`true`** | ①字节落盘（62,953 B，拼接属实）②sha 实测五值一致 ③取回 UTC 与 mtime 互证 ⑤as-filed 独立件剥注入后逐字节相同 —— **四项经我独立复算成立**；R2 自报 `origin_bytes_retrieved=62953` 属实；`BLOCKED-NEEDS-ORIGIN-BYTES` 这个名目字面所指的"需要 origin 字节"**已满足** |
| **(ii) 名目的正式解除 / `OPEN-3` 状态** | **不由本卡** | `releases_nothing=true`；L543 与 §二十七 #2 明文本裁**不解除 `OPEN-3`、不产生 ACCEPT** |
| **(iii) E1 是否因此成立** | **否** | ④ 因 C5 作废 ⇒ `BLOCKED-PARTIAL`。**字节维已解 ≠ E1 成立**；即便名目被有权方解除，`OPEN-3` 仍因 **C5（本卡新裁的硬阻断）** 与 **B1/B2** 维持 BLOCKED |

**剩余阻断清单（`remaining_blockers`）**：

| # | 阻断 | 现状（实测/出处） | 归属 |
|---|---|---|---|
| **C5** | origin ↔ 既有语料内容不一致（1 词 + 1 段）⇒ 4 语料 E3、8 引文作废 | 本卡 Q2 已裁，字节级证据见 `_verification_raw.json` | 补救 = 取证工位（新卡） |
| **C5-direction** | 错在 origin 侧还是语料侧**未定** | 需与 R2 **不同会话/不同代码**的第三条路；本卡**禁联网**不可自裁 | 取证工位（换会话） |
| **B1** | 产品仓落点 **0 字节** | R2 门 0 `P1/P2/P3` 全 `Access denied`；本会话**审批禁用、不可提权**（R2 已留一手证据：父的"三处 OK"是提权所测） | **父的第 ① 件** |
| **B2** | `filing-fetch` 分支**未跑** | 无 immutable provenance sidecar、产品仓 `git diff` 新增路径 = `[]`；§三十二 记载**晋升 `blocked`**（`git apply` 事故后两文件已 preimage 还原） | 父 / 另卡（iso→diff→复审→晋升） |
| **B3** | 已由 §三十一 定口径（`raw/other/`） | 不再是阻断，但**落地仍待 B1/B2** | — |
| **ACCT-L226 / MERGE-7** | 参数放行四要件与七条解锁条件 | 0/4、7/7（背景阻断，与本卡并列） | 会计面 / 合并裁 |

**可回源核验的条件清单（RC1–RC5）**：
1. **RC1 · 定方向**：用与 R2 **不同会话、不同实现**的第三条路（独立取回同两 URL，或对已归档 as-filed 副本做独立渲染）复核 `amplifying` 与 8-K 签名页 ⇒ 定出错在哪一侧；
2. **RC2 · 重建引文**：以 origin 为基准重建 8 条引文（**Q1 须原样保留 `(1)&#160;Agents` 形态**），新建载体登记 sha256 + 字节区，**不回改**旧载体；
3. **RC3 · 语料改判落册**：4 份旧语料按 `E3` **追加式**重登记（保留旧件与旧 sha + 新增 E3 标注与 divergence 登记），不就地改写；
4. **RC4 · 落点**：父的第 ① 件完成 B1/B2（见 §⑥ 落点清单），并实测产品仓 `git diff` 新增路径与 sidecar；
5. **RC5 · 复裁**：新建 `OPEN-3-ACCT-R3` 复裁 E1；**本卡不得被复用为"已裁通过"的依据**。

---

## ④ 与上一轮（`OPEN3-E1-ACCT-RULING/a20260924-01`）的差异

| 维度 | 上轮（2026-09-24） | **本卡（R2，2026-09-26）** |
|---|---|---|
| 结论 | `BLOCKED-PARTIAL`，五要素 **4/5** | `BLOCKED-PARTIAL`，五要素 **4/5** —— **同级，但缺的要件换了位置** |
| 缺的要件 | **① 申报原文本地归档**（origin 字节层缺失） | **④ 逐字引文**（C5 引文作废）；①②③⑤ 全部翻正 |
| 上轮给 R2 的条件 | C1（origin 落盘）· C5（不一致⇒降 E3）· L163/L185 | **C1 已满足**；**C5 已触发**（且是上轮没预料到的第三种形态）；L185 的全量比对**由本卡补做** |
| 引文重跑 | path A 字节区 8/8、path B 去空白 8/8（对语料载体） | **origin 载体重跑**：P-A 8/8 · P-B 8/8 · **M1 8/8 · M2 7/8 · M3 3/8** · 锚点 2/2（**自己重跑，不采信 R2 自报 8/8、7/8**） |
| 语料等级 | 未单独定级（可用范围按 E2） | **4 份语料降 `E3`**（C5 成立） |
| S 等级 | 未裁（OPEN-2 侧另议） | **`S1`**（+ 三项强制登记） |
| origin 维 | ① ❌ ⇒ 备 `BLOCKED-NEEDS-ORIGIN-BYTES` | **`origin_bytes_dimension_resolved = true`**（实质条件满足；正式解除不归本卡） |
| 联网 | 零联网（L543） | **零联网**（同 L543；字节已在盘） |
| 关键新增 | — | **`amplifying`/`amplifies` 词级差 + `corpusA` 缺签名页**（上轮与 R2 自报均无）；**两条同源转写路共享同一错 ⇒ A/B 互证结构上发现不了它** |

---

## ⑤ 红绿变异（判别力；`rc` 约定：**0 = 该变异按预期表现**）

| # | 变异 | 期望 | 实测 | rc |
|---|---|---|---|---|
| **G1** | 真实 8-K origin + 真实 Q1，**M1∧M2∧M3 全套** | 绿 | **未通过**：M2/M3 拒绝 Q1（NBSP 差） | **1** |
| **G1b** | 验收规则（登记 sha + **8/8 M1** + P-A 8/8） | 绿 | 通过 | **0** |
| **R1** | SEC 拦截页冒充 8-K origin（真件 `2922be22…`/4,819 B） | 红 | 检出（sha 不在登记表 + 引文不命中） | 0 |
| **R2** | EDGAR index 件冒充 8-K origin | 红 | 检出 | 0 |
| **R3** | **corpus `.md` 转写件**冒充 origin 载体 | 红 | 检出（sha 不在 `origin_sha256` 登记表） | 0 |
| **R4** | origin 拷贝翻转 1 字节 | 红 | 检出（sha 复算不符） | 0 |
| **R5** | 引文改一个数字（`$268,127→$268,126`） | 红 | M1/M2/M3 全拒 | 0 |
| **R6** | 引文改一个词（`Agents→Agent`） | 红 | M1/M2/M3 全拒 | 0 |
| **R7** | **仅空白变异**（给 Q1 补一个空格） | M1 绿 / M2 红 | `M1=True, M2=False` | 0 |

- **`discrimination_ok = true`**（`G1b` 绿 + **R1–R6 六红全检出**）。
- **`discrimination_ok_literal_G1 = false` —— 如实登记，不回改判据**：§5.1 写的 G1 用 Q1 且要求"全套校验"，其 `rc=1` **不是判别力缺陷**，而是该条恰好测到了 **Q2(a) 那个空白差**（M2/M3 对"NBSP 缺失"的正确拒绝）。以 **G1b**（= oracle §一 Q1④ 冻结的验收规则）作绿样。
- **R7 = 已知盲区登记**：M1 对空白盲，**这正是 M2 必须并报的原因** —— Q1 差异 M1 放过、M2 抓住。

---

## ⑥ 给父的**第 ① 件**（产品仓落点）的落点清单

> 本卡**不执行**任何产品仓写入（0 字节）；以下为**只读实测**得出的落点与字段清单，供父在**可写会话**（门 0 硬前置）执行。

### 6.1 目标路径（只读实测：目录已存在、可读）

```
C:\Users\郑曾波\Projects\company-wiki\companies\MICROSOFT CORP\raw\other\
```
- **实体目录实测存在**：`…\companies\MICROSOFT CORP\`（现有先例：`raw\financial_reports\annual\`）。
- **必须落 `raw\other\`**，因为诚实 `kind = current_report` 不是 `_destination_subdirectory()` 三个财报 kind 的 key（§三十一 #1/#2）。
- **禁止**：谎报 `quarterly_report` 以挤进 `financial_reports/quarterly/`；**禁止**改 `canonical_writer.py` 映射。
- **文件名**（先例格式 `{filing_date}_sec_{accession}_{filer} {form} {period}.htm`）：现有件为 `2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm` ⇒ 8-K 侧预计为 `2026-09-02_sec_0001193125-26-380280_MICROSOFT CORP 8-K 2026-09-02.htm`（**具体命名以 filing-fetch/canonical_writer 实际产出为准，我不指定实现**）。
- **两件都要落**：`d291965d8k.htm`（主文档）与 `d291965dex991.htm`（EX-99.1）—— B2 闸门已授权扩到 8-K（§三十），**但 §三十二 晋升 `blocked`** ⇒ 执行前必须**实测** exhibit 闸门是否已在生产。

### 6.2 sidecar（`.source.json`，schema 取自同实体现有件实测）

必备（照现有 schema 回填）：
`adapter_name` · `adapter_version` · `amended` · `byte_size`（28665 / 34288）· `candidate{candidate_id: "sec:0001193125-26-380280", document_kind, entity: "MICROSOFT CORP", filing_date: "2026-09-02", form_type: "8-K", market: "US", provider: "sec", provider_document_id: "0001193125-26-380280", source_url, title, adapter_payload_json{content_sha256, dayu_document_id, primary_filename}}` · `company_name` · `content_sha256` · `document_kind: "current_report"` · `fiscal_period/fiscal_year` · `language: "en"` · `mime_type: "text/html"` · `receipt{http_status: 200, retrieved_at, source_url, staged_path, content_sha256, byte_size, candidate_id, schema_version}` · `request{allow_download, as_of_date, document_kind}`

### 6.3 **本卡新增、必须回填的 provenance 字段**（缺一即视为登记不足）

| 字段 | 值/要求 |
|---|---|
| `external_retrieval_not_local` | **`true`**（永久，IND L198/L360） |
| `kind` / destination | `current_report` → `raw/other/`（§三十一） |
| `raw_sha256` / `stripped_sha256` | 8-K `a3d0bbf6…` / `6328d056…`（28,665 / 28,559 B）；EX99.1 `47a0a4a1…` / `557161af…`（34,288 / 34,182 B），inner `4cb79b6e…`（34,070 B）—— **双登记，缺一不可** |
| `edge_injected_script` | `script_html` 原文 + `span_8k [28544,28650]` + `span_ex991 [34147,34253]` + 「as-filed 内 0 命中、剥离后与归档逐字节相同」 |
| `independent_path` | `…/0001193125-26-380280.txt` · `sha256=d82838ac…` · 2,721,504 B · `byte_identical=true` |
| `url` / `retrieved_utc` / `http_status` / `bytes` / `sha256` / `mechanism` / `user_agent` | 8-K `2026-09-26T13:29:40Z`（200/28665）· EX99.1 `13:29:41Z`（200/34288）· `python urllib（声明 UA）` · `revenue-forecast-evidence-audit/1.0 (owner-authorized evidence retrieval; contact: audit-ops@example.com)` |
| `mirror_path` + mirror sha | 本计划目录 `…/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/origin_bytes/` 与 `origin_bytes.bin`（`cf84c290…`） |
| `document_identity` | accession `0001193125-26-380280` · CIK `789019` · `MICROSOFT CORP` · `8-K` · `Item 7.01 / 9.01` · `period_of_report 2026-09-02` · `accepted 2026-09-02 16:30:24` |
| **C5 / 语料等级登记（新增）** | `corpus_evidence_class = E3`（4 件）· `c5_divergence{amplifying_vs_amplifies, corpusA_missing_signature, q1_nbsp}` · `e1_level = BLOCKED-PARTIAL` · `s_level = S1` · `releases_nothing = true` |
| **引文状态** | `quotes_status = void_pending_reanchor`（RC2 后回填新引文载体 sha；**不得**直接复用旧引文登记为"已核"） |

### 6.4 执行前置（父侧硬条件，来自 §三十二 的事故教训）

1. **门 0 可写探针作为硬前置**（写+回读+删除三步全过才许动），**`git apply --check rc=0` 不校验可写**；
2. 走既有流程：`iso` → `changes.diff` → 独立复审 → 晋升授权；**禁 `git add/commit/push`**；
3. 落地后回传：产品仓 `git diff HEAD --name-only` **新增路径**、sidecar sha、`raw/other/` 实际路径 —— 供 `OPEN-3-ACCT-R3` 复裁时核。

---

## ⑦ 边界自证（可核）

1. **写入面 = 恰 6 个文件**，全在 `execution_runs/OPEN-3-ACCT-R2/a20260926-01/` 下：`oracle.md` · `verify_e1.py` · `_verification_raw.json` · `e1_regrading.json` · `ruling_acct_r2.md` · `handoff.json`；`.planning` 之外创建/修改 = **0**。
2. **只读复哈希自证**：被裁定对象（origin 5 件 + `origin_bytes.bin` + R2 四载体）、4 份语料、上轮裁定、两半区与合并裁、`OWNER_DECISIONS` 收尾实测 sha 与读前登记**全部一致 ⇒ 0 字节变更**。
3. **零联网**：本工位网络请求 = **0**（`web_fetch`/`web_search`/任何 HTTP 客户端均未调用）。
4. **零 git 写**：未 `add/commit/push/checkout/stash/restore/reset` 任何变体；**未用 `git status`**（派单禁用）；只跑只读的 `git -c core.quotepath=false diff HEAD --name-only` ⇒ **总 3,830 行，非 `.planning` = 0**。
5. **产品仓 0 写入**：仅对 `company-wiki\companies` 做**只读**列目录与只读读取（为 §⑥ 落点清单取证），**未创建/修改/删除任何字节**。
6. **未回改五份计划文件**（`task_plan` / `findings` / `progress` / `audit_report` / `delivery_validation`）与 `OWNER_DECISIONS`。
   - **如实登记（并行活动澄清）**：`task_plan.md` / `findings.md` / `progress.md` / `OWNER_DECISIONS.md` / `REMEDIATION_REGISTER.md` 的 mtime 落在 `2026-09-26 13:57–14:22Z`（本卡会话期间）。**本工位的 write/edit 调用共 6 次，全部指向本卡目录**（另在平台 `%TEMP%` 写过 3 个调试脚本，工作区外）；同期存在多个并行工位（`OPEN6B-R2-INVENTORY-BRIDGE`、`OPEN6B-R2-REVERT-UNQUANTIFIED`、`OUTWARD-*` 等同为 `a20260926-01`）⇒ 该 mtime **属并行工位活动，非本卡写入**；`OWNER_DECISIONS.md` 在本卡**读前与读末 sha 均为 `9075f9aac00ded42…`（未变）**。

---

## ⑧ 不授予（本卡**没有**做的事）

- **不解除 `OPEN-3`**（等级 ≠ 解除）· **不解除 `BLOCKED-NEEDS-ORIGIN-BYTES` / `B1` / `B2` 任一状态**（只给判定与条件清单）
- **不落产品仓**（`company-wiki` / `dayu-agent` **0 字节**；落点是父的第 ① 件）
- **不放行任何参数**（`MSFT_PBP/IC/MPC_REVENUE_FY2027`、`MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027` 与新两分部参数一律维持未放行）
- **不产生 `ACCEPT`** · **不代签矿业面** · **不改任何 `status/state/decision/decision_sha256`**
- **不改 E1/S 定义**（ACCT L190 对称：放宽与收紧都须 owner 追加登记）
- **不碰两半区裁定 / 封盘 `I-11-A` / `OPEN6-TOLERANCE-*` / `BLOCKED6C-*` / `OPEN6-H2-*` 任一字节**
- **不写五份计划文件** · **不写 `.planning` 之外任何路径** · **0 次 git 写** · **禁 `git status`** · **0 次联网**
- **不重取 origin 字节**（L543：只定级、不重取；字节已在盘，我只做本地复算）
- **不判行业半区分部集合**（IND `ruling_r2.md` 的 `supersedes` 复裁归行业面，本卡只交会计面等级与 C5 裁定）
