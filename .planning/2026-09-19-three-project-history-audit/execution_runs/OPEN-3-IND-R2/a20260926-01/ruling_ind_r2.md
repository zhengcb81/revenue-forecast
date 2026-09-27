# `OPEN-3-IND-R2` · `a20260926-01` — 行业面复裁分部集合（矿业/软件行业 reviewer，`ruling_ind_r2.md`）

- **卡 / attempt**：`OPEN-3-IND-R2` / `execution_runs/OPEN-3-IND-R2/a20260926-01`
- **role**：`industry_reviewer_ind_r2`（矿业/软件行业 reviewer，**非实现者**）｜ **父**：`session-19074bf0-0205-4315-af73-9db57597275a`
- **本卡 = `MERGE` 七条 `C3` 第 4 步（末步）**：按 `OPEN3-E1-ACCT-RULING` **C4**（「会计面 `OPEN-3-ACCT-R2` 认定等级 → 行业面 `ruling_r2.md` 按 `supersedes` 复裁分部集合（IND L197）」）执行；**会计面 `ACCT-R2` 已定 `E1=BLOCKED-PARTIAL`、`S=S1`、4 份语料降 `E3`**，本卡是行业面对**分部集合**的复裁与对 `S1`/C 表的会签。
- **被裁对象（全程只读）**：`OPEN-3-ACCT-R2/a20260926-01/` · `OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/`（origin 62,953 B）· `I11A-OPEN-IND/a20260924-01/ruling.md` · `I11A-OPEN11-IND/` · `OPEN3-E1-ACCT-RULING/a20260924-01/ruling.md` · `OPEN3-E1-ACQUISITION/a20260924-01/`（4 语料 + 取证账）· `OWNER_DECISIONS.md` §二十七/§三十/§三十一/§三十二/§三十四
- **oracle**：本目录 `oracle.md`（**先冻结**后执行；§5.2 为执行后追加实测）
- **网络**：**0 次请求**（本卡是行业面复裁、不重取 origin；`L543` 类比 + 派单明示「不需要网络」）

## 先行结论（一句话）

> **RULING —— 五问：Q1 分部集合 = `齐（内容层）`（逐条字节区见 §③-Q1）· Q2 `C5-direction` = **词形方向 `不确定`（fail-closed）+ 签名页缺段方向**可定为语料 A 侧**（细分裁定）· Q3 **`S = S1` 会签**（同意，附 1 项补登记）· Q4 **IND C 表 ①②③④ 全部同意**（含 `external_retrieval_not_local=true` **永久**、`kind=current_report→raw/other/` 诚实登记）· Q5 **RC1–RC5 同意 + 5 条 IND 侧补充步**。**
>
> **`releases_nothing = true`**：不解除 `OPEN-3`、不解除 `BLOCKED-NEEDS-ORIGIN-BYTES`/`B1`/`B2`、不放行任何参数、不产生 `ACCEPT`、不改 `E1/S` 定义、不改任何 `status/state/decision`、不代签会计面。

---

## ① 身份与授权链（逐字回源，不采信派单转述）

| 环节 | 原文（逐字） | 出处 |
|---|---|---|
| 行业面复裁的机制位 | 「C1/C2 之后：会计面 `OPEN-3-ACCT-R2` 认定等级 → **行业面 `ruling_r2.md` 按 `supersedes` 复裁分部集合**（IND **L197**）→ 命题/参数换版（MERGE **L165**）」 | 上轮 `OPEN3-E1-ACCT-RULING/…/ruling.md` **C4（L169）** |
| IND 对复裁载体的要求 | 「8-K/Exhibit 99.1 进入本地语料后：**新建 attempt** 重新取证并更新本裁定（追加 `ruling_r2.md` + 新 provenance 条目，标 `supersedes`）；**不回改** I-11-A、**不回改**本文件」 | `I11A-OPEN-IND/…/ruling.md` **L197** |
| 外部条目永久性 | 「本裁定中"外部获取"的条目永久保留 `evidence_class=external`，即使日后本地化也不改写历史条目，只新增 `local_ingested_at` 条目。」 | 同上 **L198** |
| 外部 ≠ 本地 | 「**外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`；`2026-09-02 8-K` 条目显式写明"**本地不可核，外部获取，不得作为本地可核证据放行**"。」 | 同上 **L360** |
| C 表（替代来源分级） | 「**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**」；①「**同一发行人、同一报告期**的其他**可读原文**官方文件…`company_primary_disclosure`（与年报同级，但必须标注**文件类型与期间**）\| 必须：原文可定位（页码/锚文本或章节）+ 原始 sha256 + 期间与年报一致；跨期文件必须标 `period_mismatch_risk`」；②「交易所/监管公告（HKEX）\| `regulator_primary_disclosure`」；③「券商研报 / 新闻 / 数据商 / wiki \| `secondary_lead_only` \| **仅可作线索**，**不得**进参数、**不得**进命题的 `cited_values`」；④「外部抓取的港股年报 PDF（若本地原件不可读）\| `external_retrieval_not_local` \| 必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径」 | 同上 **L227/L231-234** |
| C 表反例与被拒替代 | L240-241「若出现①类可读原文且含分部收入 ⇒ B 的"零产出"解除…（仍需会计面定证据等级）」；L261「用外部抓取件静默顶替本地原件（必须按④登记为外部）」 | 同上 **L240-241/L261** |
| 落点诚实登记 | 「**口径**：**8-K 按诚实 kind `current_report` 落 `company-wiki/companies/{entity}/raw/other/`** —— **不改 `canonical_writer` 映射、不谎报 `quarterly_report`**。」＋「该条写的 `…raw/financial_reports/{kind}/` **按「`raw/…` 下」理解，含 `raw/other/`** —— 本节即该澄清的**唯一授权出处**」 | `OWNER_DECISIONS` **§三十一 #1/#2** |
| 8-K 扩闸 | 「**owner 选择（B2）**：**「授权扩闸到 8-K（建议）」**」＋「**先解 B2 ≠ B3 已定、更 ≠ B1 已解**」 | **§三十**（L648/L656） |
| 定级权与纪律 | 「…仍标 `external_retrieval_not_local` 如实；**等级判定归会计面**；本裁**不解除 `OPEN-3`、不产生 ACCEPT**」；L543「**只定级、不重取**（禁联网…）；`fail-closed`——**不得为推进链抬高等级**；`releases_nothing=true`」 | **§二十七 #2**；**L543** |
| 会计面结论（会签对象，逐字） | 「**RULING —— `E1 = BLOCKED-PARTIAL`（五要素 4/5：①②③⑤ 经我独立实测成立、④ 因 C5 不成立）· `S = S1`（IND C 表 ①类 + `external_retrieval_not_local=true` + kind `current_report`→`raw/other/`，但不等于放行）· 既有 4 份语料降 `E3` · `origin_bytes_dimension_resolved = true`…`releases_nothing = true`**」；「**方向未定（如实）**：我**无法**断定错在 origin 侧还是语料侧」 | `OPEN-3-ACCT-R2/…/ruling_acct_r2.md` **L10/L127** |

⇒ **链条闭合**：`§二十七 #2`（等级归会计面）→ `L543`（fail-closed、releases_nothing）→ 上轮 **C4/L169**（会计面定级后行业面复裁分部集合）→ **本卡执行**。

---

## ② 待裁对象与只读自证（sha256 = 本工位实测，读前登记 = `_probe_raw.json → T0_integrity`）

| 文件 | 字节 | sha256（实测） | 与登记/自报 |
|---|---|---|---|
| `origin_bytes.bin` | 62,953 | `cf84c29048ab314e…` | ✅ 一致 |
| `…d291965d8k.htm.origin` | 28,665 | `a3d0bbf6411bb2b2…` | ✅ |
| `…d291965dex991.htm.origin` | 34,288 | `47a0a4a1d6a335ff…` | ✅ |
| `_identity_…index.htm` | 17,557 | `618f010b6e56597c…` | ✅ |
| `_independent_…complete_submission.txt` | 2,721,504 | `d82838ac92ed3e8b…` | ✅ |
| 语料 A `Item7.01.md` / B `…html2txt.txt` | 3,789 / 5,183 | `096c7d9d…` / `5927de03…` | ✅ |
| 语料 A `Exhibit99-1.md` / B `…html2txt.txt` | 27,586 / 28,536 | `20392f0e…` / `56b0460b…` | ✅ |

- `origin_bytes.bin == 8-K ∥ EX99.1`（偏移 `[0,28665)` / `[28665,62953)`）——**本工位独立复算成立**。
- **全部判定数字均为本工位 `ind_probe.py` / `ind_probe_b.py` 在盘上字节的独立重跑**（原始输出 `_probe_raw.json` / `_probe_raw_b.json`），不采信 ACCT/R2 自报。

---

## ③ 五问逐条（结论 · 依据 · 反例 · 兼容影响 · 恢复规则）

### Q1 —— 8-K + Exhibit 99.1 的**分部集合**是否齐？ ⇒ **齐（内容层）**，逐条字节区如下

**坐标约定**：括号内为**文件内偏移**；`EX99.1` 在 `origin_bytes.bin` 内的偏移 = **+28,665**。8-K 为单行长 HTML，故以字节区为主（语料行号见 `OPEN3-E1-ACQUISITION` 报告 §二 Q1–Q8）。

| # | 分部集合要素 | 依据（origin 载体字节区，本工位实测） | 判定 |
|---|---|---|---|
| (i) | **新两分部名称 + 生效期**（8-K Item 7.01） | 「`Beginning in fiscal year 2027, the Company will manage its operations under this updated reporting structure and report its financial performance based on two reportable segments: (1)&#160;Agents and Infra and (2)&#160;Devices and Consumer.`」——`Beginning in fiscal year 2027` @ **21981**；`two reportable segments: (1)…` @ **22136**（区域 **[21796,22350]**，R2 原始 ASCII 锚点 [21796,21866] 同区） | ✅ |
| (ii) | **重述声明**（8-K Item 7.01 第二段） | 「`…presents summary financial information and historical data on a basis consistent with the updated reporting structure.`」@ **22519** | ✅ |
| (iii) | **重述后基期分部数据**（EX99.1 slide 15「Segment History as Restated」，= 会计面 Q6） | `Revenue $61,672 $64,441 $67,438 $74,576 $268,127` 精确跨度 **[20291,20331]**（A&I：FY26 四季 + 年度 268,127 / FY25 50,476…218,783）；**D&C 行** @ **20777**（`Revenue $16,001 $16,832 $15,448 $15,431 $63,712 … $62,941`）；**Total 行** @ **21187**（`$77,673 $81,273 $82,886 $90,007 $331,839 … $281,724`）；标题 `Segment History as Restated` @ **21531** | ✅ |
| (iii-b) | **旧三分部历史**（对照层） | PBP 行 @ **22095**（`Revenue $33,020 $34,116 …`）；IC 行 @ **22527**（`$30,897 $32,907 … $136,365`）；MPC 行 @ **22971**（`$13,756 $14,250 …`） | ✅ |
| (iv) | **FY27Q1 outlook（新口径）**（= 会计面 Q7） | `Agents and Infra Revenue of $75.15 to $75.75 billion` 精确跨度 **[30770,30794]**；`Devices and Consumer Revenue of $14.7 to $15.2 billion` 跨度 **[30827,30849]**（同页 `No change to outlook` 成本行相伴） | ✅ |
| (iv-b) | **FY27Q1 outlook（旧口径，交叉核对）** | @ **29837**：`Total Company Revenue of $89.85 to $90.95 billion` + PBP `$36.7 to $37.0 billion`（@29909）+ IC `$40.95 to $41.25 billion` + MPC `$12.2 to $12.7 billion` —— **总额与新口径可加总对上**（75.15+14.7 = 89.85；75.75+15.2 = 90.95；36.7+40.95+12.2 = 89.85） | ✅ |
| (v) | **旧→新桥接信息**（IND `ruling.md` L164/L185 要求） | **业务线归属定义** @ 7516/7580（`Agents and Infra will include the Microsoft Cloud, productivity and server licensing, and our consulting and support businesses. Devices and Consumer will include our Windows, XBOX, and advertising businesses.`）；**产品线迁移映射 `previously reported` × **12****（偏移 8586/9146/9226/9532/9605/10802/13968/14280 等，例：`GitHub cloud and other developer cloud services…Security Copilot, which were previously reported in Azure`、`LinkedIn Talent Solutions and Sales Solutions, previously reported in LinkedIn, and Healthcare and Life Sciences cloud, previously reported in Azure`、`Revenue previously reported in Other is now reported within Windows OEM and devices and Productivity and server licensing`、`LinkedIn was previously reported as a standalone unit in the Productivity and Business Processes segment. LinkedIn Talent Solutions and Sales Solutions will now be reported in the Ind…`）；**转换声明** @ 3058（`Beginning with FY27, we will transition from our current three reporting segments, Productivity and Business Processes, Intelligent Cloud, and More Personal Computing, to two segments: Agents and Infra and Devices and Consumer.`） | ✅（**形态限定**，见下） |

**形态限定（如实，不夸大）**：
- (v) 的桥接是「**公司披露的定性迁移映射 + 新旧两套历史 + 新旧两套 outlook**」，**不是**一张「旧三段 → 新两段」的**数值桥接表**（幻灯片无该表）；按 IND L165，**旧分部历史数与新分部数据仍不得混算增速**（双计风险），混用仍需另行桥表。
- 反向约束（IND L185 反例）：「若新两分部在 FY2027 首份 10-K 中无法追溯到本地 10-K 的三分部 ⇒ 桥接表必须由公司披露提供」——本件已给出**公司披露的迁移映射与双口径对照**，属「由公司披露提供」的桥接信息形态；**但 I-07-E 是否据此冻结口径不归本卡**（不授予）。

**反例（会推翻本判定）**：任一锚点在 origin 上不存在（**未发生**，本工位逐条命中）；或 FY2027 首份 10-K 报告分部又回到 PBP/IC/MPC（IND L183 反例）⇒ 本分部集合判定连同 IND L133 裁定一并撤销。
**兼容影响**：Q1 齐 ≠ 可引 —— 8 条引文仍 `void_pending_reanchor`（RC2 后方可「已核」）；分部集合内容层齐**不构成解锁**（E1 仍 `BLOCKED-PARTIAL`）。
**恢复规则**：以本表字节区为 RC2 重建引文的锚点集（见 Q5 RC-IND-1）。

---

### Q2 —— ⭐ `C5-direction`（错在 origin 侧还是语料侧）能否定？ ⇒ **分两处裁：签名页缺段「可定 = 语料 A 侧」；词形 `amplifying/amplifies`「不确定」（fail-closed）**

**冻结判据（oracle §1-Q2）**：定向必须有**与 R2 取证会话/实现不同**的第三条独立路**覆盖争议点本身**；盘上 origin 重读只能复核「origin 说什么」，不能定向；语法/文风推断只作辅助观察。

#### (a) 词形 `amplifying` ↔ `amplifies`（EX99.1 同句） ⇒ **`不确定`**

| 载体 | 取得链 | 实测（字节级） |
|---|---|---|
| `origin_ex991`（R2，python urllib 直取，2026-09-26） | sec.gov → 字节落盘（无转写） | `amplifying = 1`，`amplifies = 0` @ **3681**（句：`…to ensure AI empowers every person, amplifying their agency and ambition. That is what we mean by a frontier ecosystem…`） |
| `asfiled_submission`（R2，同会话取回） | EDGAR 完整申报归档 → 字节落盘 | `amplifying = 1`，`amplifies = 0`（SUB 偏移 **33446**） |
| `corpusA_ex`（工位转写 r.jina.ai 渲染，2026-09-24） | sec.gov → r.jina.ai → web_fetch 文本 → **工位转写** | `amplifying = 0`，`amplifies = 1`（@ 2540） |
| `corpusB_ex`（工位转写 W3C html2txt，2026-09-24） | sec.gov → W3C html2txt → web_fetch 文本 → **工位转写** | `amplifying = 0`，`amplifies = 1`（@ 2540） |

- **两族正好 2 : 2、且断口与族界重合**（R2 取回族 ↔ 语料转写族）⇒ **不存在跨族旁证**，按冻结判据**不能定向**。
- **IND 侧独立证据覆盖核查（本工位实测）**：`I11A-OPEN-IND/a20260924-01/provenance.json`（EXT-01…EXT-12）与 `I11A-OPEN11-IND/a20260924-01/provenance.json` 全文检索 `amplif|agency|ambition|Jolla|signature` = **0 命中**（IND 的 EXT-05 r.jina.ai 逐字引文只覆盖 8-K Item 7.01 首段，**不覆盖 EX99.1 争议句**）；`I11A-OPEN-ACCT`/`I11A-OPEN-MERGE`/`OPEN3-E1-ORIGIN-BYTES`/`I-11-A`/`I11A-HYP-APPROVE` 同检索亦 **0 命中** ⇒ **IND 侧没有可用的第三条路覆盖争议词**。
- **辅助观察（仅登记，不作定向依据，fail-closed）**：origin 形态 `…AI empowers every person, amplifying their agency and ambition.` 为分词短语（语法成立）；语料形态 `…every person, amplifies their agency…` 为逗号粘连的第二谓语（语法不成立）⇒ 该形态差异**倾向于**「语料侧转写环节（共享步）改了词形」，但**语法推断不是第三条路**，本卡据此**不定向**。
- **反例（会推翻「不确定」）**：出现任一**覆盖该句**、与 R2 会话/实现无关的原始字节或独立渲染件（如不同会话直取 `d291965dex991.htm` 的响应体、或对 as-filed 归档副本用不同代码独立渲染）且与某一边一致 ⇒ 立即定向并按方向重判 C5 归属。

#### (b) `corpusA` 缺 8-K 签名页整段 ⇒ **方向可定：错在语料 A 侧（漏段）**

| 载体 | `Date: September 2, 2026` | `/s/ ALICE L. JOLLA` / `Alice L. Jolla` | `Corporate Vice President and Chief Accounting Officer` |
|---|---|---|---|
| `origin_8k`（R2 直取） | ✅ @ 26875 | ✅（@ 27777，HTML `<small>` 拆字：`/s/ A<small>LICE</small> L. J<small>OLLA</small>`） | ✅ |
| `asfiled_submission`（R2 取回，EDGAR 归档） | ✅ | ✅（SUB @ 28955） | ✅ |
| **`corpusB_8k`（W3C html2txt 链，与 R2 不同渲染实现）** | ✅（`Date: September 2, 2026 / /s/ ALICE L. JOLLA / Alice L. Jolla / Corporate Vice President and Chief Accounting Officer`） | ✅ | ✅ |
| `corpusA_8k`（r.jina.ai 链） | ❌ 0 | ❌ 0 | ❌ 0（正文止于 `104 Cover Page Interactive Data File` @ 24700 附近） |

- **三条独立链（R2 直取 / EDGAR 归档 / W3C 渲染）均有签名页，唯 `corpusA` 缺** ⇒ 缺段方向 = **语料 A 链条（r.jina.ai 渲染或其转写）**，与 origin 无关。此处 `corpusB` 恰好构成与 R2 **不同实现**的旁证，满足冻结判据的定向门槛。
- **反例**：若签名页只存在于 origin 族、W3C 链也无 ⇒ 方向退回「不确定」（**未发生**）。

#### 裁定

> **`c5_direction_ruling` = 「词形方向 `不确定`（fail-closed，RC1 仍必需）＋ 签名页缺段方向 = 语料 A 侧」。**
> **对会计面 C5 裁定的效力**：`不一致` 成立与 4 语料降 `E3` **维持不变**（词形未定向不改变「不一致」事实本身；签名页一处已定向为语料侧）；若 RC1 后来证明词形错在 origin 侧 ⇒ 按 ACCT 反例改判（降的改为 origin、语料不降 E3），**本卡不预设该结果**。

**兼容影响**：`E1` 五要素 ④ 维持 ❌（引文作废）；`E1` ①⑤ 是否受词形方向影响**取决于 RC1**（若 origin 错则 ① 原文性崩、⑤ 不能自证）——但无论哪个方向，**当前都不得升 `E1-COMPLETE`**（双向论证与 ACCT 一致）。
**恢复规则**：RC1（收窄为**只定向词形一处**）+ RC-IND-4（第三条路必须保存原始字节/渲染输出，不经转写步）。

---

### Q3 —— `S = S1` 是否可会签？ ⇒ **会签（同意 `S1` + 三项强制登记；另补 1 项 IND C 表自带登记）**

**逐要件复核（本工位独立实测）**：

| S1 要件（ACCT S 表） | 本工位核验 | 判定 |
|---|---|---|
| 同一期间原文披露 | 文档身份实测：accession `0001193125-26-380280`、`period_of_report 2026-09-02`、`accepted 2026-09-02 16:30:24`、`Item 7.01/9.01`；EX99.1 覆盖 FY2025/FY2026 重述基期 + FY27Q1 outlook（与被引内容同期） | ✅ |
| 可定位锚文本 | 8 条引文在 origin 载体独立重跑：**M1（去空白）8/8 · M2（空白折叠）7/8 · M3（严格）3/8**（唯一 M2 miss = Q1 NBSP；与 ACCT 自报逐数一致，见 `_probe_raw_b.json → B2`） | ✅ |
| doc sha256 已绑定 | 5 件 + `origin_bytes.bin` + 4 语料实测 sha 全部与登记表一致（T0 all_match） | ✅ |
| ≥1 独立复核路径 | as-filed 完整申报（`d82838ac…`，2,721,504 B）与 origin 剥注入内容逐字节相同 —— **限定：与 origin 同采集会话/实现**（artifact 级独立、非实现级独立；该限定随判定传播） | ✅（带限定） |

**三项强制登记（ACCT L174-177）逐项同意**：① `external_retrieval_not_local = true`（**永久**，IND **L198/L360**）② `kind = current_report` → `company-wiki/companies/{entity}/raw/other/`（**§三十一 #1/#2**，不谎报 `quarterly_report`、不改 `canonical_writer`）③ `raw_sha256 + stripped_sha256` 双登记 + `edge_injected_script` 跨度（8-K `a3d0bbf6…`/`6328d056…`，跨度 **[28544,28650]**；EX99.1 `47a0a4a1…`/`557161af…`，跨度 **[34147,34253]**；inner `4cb79b6e…`）——三处本工位全部独立复算一致。

**本卡补充的第 4 项登记（IND C 表 ① 自带条件，ACCT 三项未列）**：
4. **`period_mismatch_risk` 标注**（IND **L231** 原文「期间与年报一致；**跨期文件必须标 `period_mismatch_risk`**」）：8-K/EX99.1 文档日期 `2026-09-02` 与 FY2026 年报期间（截至 `2026-06-30`）**不同期**；`FY27Q1 outlook` 属**前瞻期间**内容 ⇒ 任何引用须标注期间关系（重述基期 FY2025/FY2026 数据与年报同期间、可直引；outlook 仅可作情景、不得作已实现值）。**这是登记义务的补充，不是 S 定义的修改**（ACCT L190 对称不触发）。

**`S1 ≠ 放行` 维持**：ACCT **L226 四要件**（可复算观测量 ✅ / 可核基础 ⚠ 部分 / 非实现者 `decision_sha256` ❌ / 追加式版本化 ❌）与 **MERGE 七条 7/7** 现状不变 ⇒ **任何 MSFT 参数一律维持未放行**（含新两分部参数）。
**反例**：RC1 证明词形错在 origin 侧 ⇒ S 降 `S0`、① 重判（ACCT 同判）；owner 明文改 S 定义 ⇒ 须追加登记。
**恢复规则**：RC1–RC5 完成并复裁 E1（`OPEN-3-ACCT-R3`）后，`S1` 才由「来源层成立」升为「可进入 L226 四要件评估」。

---

### Q4 —— IND C 表逐项是否同意？ ⇒ **①②③④ 全部同意（附 2 处细化）**

| 行 | ACCT 判定 | **本工位（IND 侧）** | 依据 |
|---|---|---|---|
| ① 内容类型：`company_primary_disclosure` | 适用 | **同意** | 8-K/EX99.1 是**同一发行人、覆盖被引报告期**的公司自身正式披露（Reg FD furnished，Item 7.01/9.01）；原文可定位（本卡 Q1 字节区表）+ 原始 sha256 + 期间标注齐。**细化 1**：必须标注**文件类型**（`current_report` / Exhibit 99.1 furnished under Reg FD，**非 filed**，Section 18 不适用——IND L160 已提示）；**细化 2**：跨期引用须标 `period_mismatch_risk`（见 Q3 第 4 项） |
| ② `regulator_primary_disclosure` | 不适用 | **同意（不适用）** | 存管处 SEC EDGAR ≠ 监管公告：被引对象是**公司自身披露**（filings repository 承载），归 ①；IND C 表 ② 语义是交易所/监管方**自身发布的公告**（如 HKEX 披露易公告），本件不属 |
| ③ `secondary_lead_only` | 不适用 | **同意（不适用）** | 本件非研报/新闻/数据商/wiki。**注**：**4 份语料降 E3 后恰落入 ③ 的处境**——仅可作线索、不得进参数、不得进 `cited_values`（与 ACCT「E3 仅可用于提出问题」同义） |
| ④ `external_retrieval_not_local = true` | 适用（永久） | **同意（永久）** | 本件系联网取回（python urllib 声明 UA）⇒ flag = `true` 且**永久保留**：IND **L198**（只可新增 `local_ingested_at`，不得改写历史条目）、**L360**（`EXT-*` 不得冒充本地可核、不得据此放行）、**L261**（被拒替代：外部抓取件静默顶替本地原件） |

**`kind = current_report → raw/other/` 诚实登记**：**同意**（§三十一 #1/#2 逐字照录；**禁止**谎报 `quarterly_report` 挤进 `financial_reports/quarterly/`、**禁止**改 `canonical_writer` 映射）——IND 侧确认该口径与 `service_helpers.py L117`（`"8-K": "current_report"`）同源一致。
**反例**：若后续证明该 8-K 实为 `filed`（非 furnished）⇒ ① 的文件类型标注需改；若产品落点谎报 kind ⇒ ① 的诚实登记作废、S1 回退。
**兼容影响**：IND `BLOCKED-4`（8-K 进入本地可核来源）的**实质条件已大部分满足**（origin 字节在计划目录、sha 可复算），但**名目关闭与产品仓落点不归本卡**（RC4，父的第①件）；`BLOCKED-5`（参数放行/口径冻结）**不动**。

---

### Q5 —— 恢复链 RC1–RC5 的 IND 侧确认 ⇒ **同意；另补 5 条 IND 侧步（RC-IND-1…5）**

| # | ACCT 恢复链 | IND 侧裁定 | 备注 |
|---|---|---|---|
| RC1 | 定方向：与 R2 不同会话/不同实现的第三条路复核 `amplifying` 与 8-K 签名页 | **同意，且收窄**：签名页一处**本卡已定向**（语料 A 侧，见 Q2(b)）⇒ RC1 **只剩词形一处** | 归取证工位（换会话）；本卡零联网不自取 |
| RC2 | 以 origin 重建 8 条引文（Q1 原样保留 `(1)&#160;Agents` NBSP 形态），新载体登记 sha + 字节区，不回改旧载体 | **同意** + **RC-IND-1**：重建引文的锚点集以**本卡 Q1 字节区表**为准（新增纳入旧三段历史行、双口径 outlook、`previously reported` 映射段），并把 Q1 的**三方空白形态**如实登记（origin = NBSP×2（`&#160;`）/ corpusA = 无空白 / corpusB = 半角空格 + 硬换行） | 归取证工位 |
| RC3 | 4 份旧语料按 `E3` **追加式**重登记（保留旧件与旧 sha + E3 标注 + divergence 登记） | **同意** + **RC-IND-2**：divergence 三件须逐件登记方向（词形=未定向、缺段=corpusA 侧、空白=保真缺陷）；**RC-IND-3**：`corpusB` 的 Q1 空白形态细化入册（ACCT「语料 = 0 空白」实为 corpusA 专属表述） | 归取证/记账工位 |
| RC4 | B1/B2 落点完成 + 产品仓新增路径与 sidecar 实测 | **同意（不归本卡执行）**。**现状更新**：`OWNER_DECISIONS §三十四` 已记「② B2 晋升 ✅」（§三十二 的「晋升 blocked」已被后续授权取代）；**B1 仍缺可写 `company-wiki` 会话**（§三十四 边界明文不解除 B1） | 归父（可写会话） |
| RC5 | 新建 `OPEN-3-ACCT-R3` 复裁 E1；本卡不得被复用为「已裁通过」依据 | **同意** + **RC-IND-5**：`ACCT-R3` 须同时核本卡 Q1 字节区表与 Q3 第 4 项登记（`period_mismatch_risk`）是否落地 | 归会计面 |

**IND 侧新增步（RC-IND-1…5 归属）**：RC-IND-1（引文锚点集）归取证工位；RC-IND-2/3（证据账追加式登记）归取证/记账工位，**且 `EXT-*` 旧条目永不改写（L198/L360），只新增 `local_ingested_at`**；RC-IND-4（第三条路保存原始字节/渲染输出，不经转写步——本次 C5 的教训就是**共享转写步使 A/B 互证失效**）归取证工位；RC-IND-5 归会计面。
**另（本卡即为 IND L197 的载体）**：`ruling_ind_r2.md` + `ind_ruling_r2.json` 就是 L197/C4 要求的「追加 `ruling_r2` + 标 `supersedes`」——**`supersedes: I11A-OPEN-IND/a20260924-01/ruling.md §③-OPEN-3（分部集合部分）`**，实质结论**确认不变**（FY2027 起新两分部）、证据基础升级为 origin 字节；旧载体**不回改**。⚠️ L197 同句的「**重新取证**」部分**不由本卡完成**（定级/复裁卡不重取），仍留 RC1/RC2 取证工位。

---

## ④ 与会计面（`OPEN-3-ACCT-R2`）的衔接 / 分歧

**衔接（会签、不推翻任何一项）**：`E1 = BLOCKED-PARTIAL（4/5）` · `S = S1（≠放行）` · 4 语料 `E3` + 8 引文作废 · `origin_bytes_dimension_resolved = true` · `quotes_status = void_pending_reanchor` · `releases_nothing = true` · 双向论证（无论错在哪侧 E1 都不成立）——行业面**无新证据推翻**，逐项确认。

**分歧 / 细化（3 处，均不改 E1/S 等级）**：

1. **C5-direction 从「整体未定」细分为「签名页可定 + 词形未定」**（ACCT L127「我无法断定错在 origin 侧还是语料侧」）：签名页缺段经三链（含与 R2 不同实现的 W3C 链）定为 **corpusA 侧**；词形维持 `不确定`。⇒ RC1 的工作量收窄为一处。**这是对 ACCT 结论的收窄而非推翻**。
2. **Q1 空白形态的事实细化**（ACCT L92「语料 = `(1)Agents`（0 个空白字符）」）：实测 **corpusA = 无空白**、**corpusB = 半角空格 + 硬换行**（`(1) Agents and\n Infra`）——「语料空白保真缺陷」的登记对象须分开写（corpusA 丢字符、corpusB 折叠为半角空格）。
3. **C 表 ① 的 `period_mismatch_risk` 条件未在 ACCT 三项强制登记内**（IND L231 自带）——本卡补为第 4 项**登记义务**（不改 S 定义，L190 对称不触发）。

**无分歧的旁证**（登记不改判）：`amplifies` 形态语法不成立（逗号粘连）⇒ 倾向「语料转写步改词形」，但**只作辅助观察**，与 ACCT 的 fail-closed 定向立场一致。

---

## ⑤ 红绿变异（判别力；`rc` 约定：**0 = 按预期表现**）

| # | 变异 | 期望 | 实测（本工位） | rc |
|---|---|---|---|---|
| **G1** | 争议词四方计数 | origin/归档 `amplifying=1, amplifies=0`；语料 A/B `0/1` | 逐数复现（origin_ex991 `1/0`、asfiled `1/0`、corpusA_ex `0/1`、corpusB_ex `0/1`；8-K/语料 8-K 双方 `0/0`） | **0** |
| **G2** | 签名页段计数 | origin 1、corpusB 1、corpusA 0 | `Jolla`/`/s/`/`CAO`/`Date: September` 四探针：origin_8k / asfiled / corpusB_8k 全 1、corpusA_8k 全 0 | **0** |
| **G3** | Q1 空白形态四方 | origin = NBSP×2（`&#160;`）；语料 = 非 NBSP | origin = 实体 `&#160;`×2（解码后 U+00A0）；corpusA = 0 空白；**corpusB = 半角空格 + 硬换行**（oracle 预期「语料无空白」仅对 corpusA 成立 ⇒ 按细化登记） | **0**（带事实细化） |
| **G4** | 注入 `<script>` | origin 两件各 1、归档 0、跨度与登记一致 | origin_8k @ **28544**（= 28544+106 = 28650 ✅）、origin_ex991 @ **34147**（→ 34253 ✅）、asfiled/index **0**；剥后 sha 复算 `6328d056…`/`557161af…` 一致 | **0** |
| **G5** | Q6/Q7 与分部集合锚点 | 全部命中并给字节区 | Q6 跨度 **[20291,20331]**、Q7 **[30770,30794]**/**[30827,30849]**、名称/生效期/重述声明/旧三段历史/双口径 outlook 全命中（见 Q1 表） | **0** |
| **R1** | 语料 `.md` 冒充 origin | 红（sha 不在登记表） | corpusA/B 四件 sha 均不在 `origin_sha256` 五值表 ⇒ 拒 | 0 |
| **R2** | 引文数字改一位（`$268,127→$268,126`） | 红（不命中） | origin 上 `$268,126` **0 命中** ⇒ 拒 | 0 |
| **R3** | 仅空白变异 M1/M2 分化 | M1 绿 / M2 红 | Q1 在解码载体上 `M1=True`、`M2=False`（M1 对空白盲、M2 抓住）⇒ 差异化成立 | 0 |
| **R4** | 翻转 1 字节 | 红（sha 不符） | 8-K 第 1000 字节翻转 ⇒ sha 复算不符 | 0 |

- **`discrimination_ok = true`**（G1–G5 全绿 + R1–R4 全红/差异化）。
- **引文层独立复现**（B2，解码 + 归一化）：**M1 = 8/8、M2 = 7/8、M3 = 3/8、原始精确 = 3/8** —— 与 ACCT 自报（8/8、7/8、3/8）**逐数一致**，8 条引文在 corpusA 上 `8/8` 精确命中（其来源即 corpusA，佐证引文系语料基、须 RC2 换 origin 基）。

---

## ⑥ 边界自证（可核）

1. **写入面 = 本目录 9 个文件**：`oracle.md`（先冻结）· `gate0_raw.txt` · `ind_probe.py` · `_probe_raw.json` · `ind_probe_b.py` · `_probe_raw_b.json` · `ind_ruling_r2.json` · `ruling_ind_r2.md` · `handoff.json`；**`.planning` 之外创建/修改 = 0**；产品仓（`company-wiki`/`dayu-agent`）**0 字节**。
2. **门 0 自探（写 + 回读 + 删除三步）**：**PASS**，原始输出 `gate0_raw.txt`（`WRITE: OK / READBACK: OK / DELETE: OK / EXISTS_AFTER_DELETE: False`）。⚠️ 如实登记：该探针只证明**本工位对本目录可写**；对产品仓的写权限**本工位未探未写**（产品落点归父，父与子工位门 0 结果相反已由 R2 卡一手记录，本卡不重复触发）。
3. **零联网**：本工位网络请求 = **0**（`web_fetch`/`web_search`/任何 HTTP 客户端均未调用）。
4. **零 git 写**：未 `add/commit/push/checkout/stash/restore/reset` 任何变体；**未用 `git status`**（派单禁用）；仅跑只读 `git -c core.quotepath=false diff HEAD --name-only` ⇒ **非 `.planning` = 0**（收尾实测值见 `handoff.json`）。
5. **只读面 0 变更**：收尾对 §② 表全部文件复哈希，与读前登记逐一相同（见 `handoff.json → read_only_rehash`）。
6. **未回改**五份计划文件（`task_plan`/`findings`/`progress`/`audit_report`/`delivery_validation`）与 `OWNER_DECISIONS.md`、两半区、封盘 `I-11-A`、`I11A-*`、`OPEN-3-ACCT-R2`、`OPEN3-E1-ORIGIN-BYTES-R2`、`OPEN3-E1-ACQUISITION` 任一字节。

## ⑦ 不授予（本卡**没有**做的事）

- **不解除 `OPEN-3`**（分部集合齐 ≠ 解锁）· **不解除 `BLOCKED-NEEDS-ORIGIN-BYTES` / `B1` / `B2` / IND `BLOCKED-4/5` 任一状态**
- **不放行任何参数**：`MSFT_PBP/IC/MPC_REVENUE_FY2027`、`MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027`、新两分部参数、`*_PLACEHOLDER` 一律维持未放行
- **不产生 `ACCEPT`** · **不代签会计面**（S1 只是会签，不代行定级权）· **不改任何 `status/state/decision/decision_sha256`**
- **不改 `E1/S` 定义**（ACCT L190 对称）· **不回改任何上游载体**（追加式；`supersedes` 只是标注）
- **不冻结 I-07-E 分部口径**、不触发任何 falsifier/自动动作、不动 `H-US-MSFT-SEG-01` 的 `state`
- **不落产品仓**（0 字节）· **不写五份计划文件** · **不写 `.planning` 之外** · **0 次 git 写** · **禁 `git status`** · **0 次联网** · **不重取 origin**（L543）
- **不判词形方向**（`不确定` 即如实结论，不为推进链定向）
