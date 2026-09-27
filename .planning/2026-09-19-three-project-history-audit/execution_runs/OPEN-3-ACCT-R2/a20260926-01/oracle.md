# oracle.md · `OPEN-3-ACCT-R2` / `a20260926-01`（**先冻结**）

- **卡**：`OPEN-3-ACCT-R2`（`MERGE` 七条 **`C3` 的第 3 步**：对已取回的 `origin` 字节做 **`E1` 等级裁定**）｜ **attempt**：`execution_runs/OPEN-3-ACCT-R2/a20260926-01`
- **role**：`accounting_reviewer`（会计/披露 reviewer，**非实现者**）｜ **父**：`session-19074bf0-0205-4315-af73-9db57597275a`
- **裁定对象（只读）**：`execution_runs/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/`（`origin_bytes.bin` + `origin_bytes/` 5 件 + `provenance.json` + `ruling_e1_bytes.md` + `_analysis_output.json` + `mutation_results.json` + `oracle.md` + `handoff.json`）
- **对照对象（只读）**：`execution_runs/OPEN3-E1-ACCT-RULING/a20260924-01/`（上一轮 E1 裁定）· `execution_runs/OPEN3-E1-ACQUISITION/a20260924-01/corpus/`（既有 4 份语料）与其 `provenance.json`（8 条引文）· `OWNER_DECISIONS.md` · `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md`（E0–E3 / S0–S4 定义）· `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md`（C 表）
- **冻结时刻**：本文件落盘即冻结；§五 只追加实测原始输出，**不回改 §一~§四与 §六 判据正文**
- **上轮结论（被本卡复裁）**：`BLOCKED-PARTIAL`，五要素 4/5（① ❌ = 缺 origin 响应字节层），`BLOCKED-NEEDS-ORIGIN-BYTES` 为 ① 的补齐条件
- **本卡不解除任何东西**（见 §六）；**禁联网**（见 §〇.3）

---

## §〇 授权与边界（逐字回源，不采信派单转述）

### 0.1 授权出处

> `OWNER_DECISIONS.md` **§二十七 #2**（2026-09-25）执行映射逐字：「**本条以 owner 本裁为准，取代 §二十四 L498 在该场景的适用**：允许 origin 字节**经 filing-fetch 既有机制落 `company-wiki/companies/{entity}/raw/…`**，本计划目录**另存镜像与 sha 校验**；仍标 `external_retrieval_not_local` 如实；**等级判定归会计面**；本裁**不解除 `OPEN-3`、不产生 ACCEPT**」
>
> `OWNER_DECISIONS.md` **§三十一** 执行映射逐字：「**8-K 按诚实 kind `current_report` 落 `company-wiki/companies/{entity}/raw/other/`** —— **不改 `canonical_writer` 映射、不谎报 `quarterly_report`**」；#2 逐字：「该条写的 `company-wiki/companies/{entity}/raw/financial_reports/{kind}/` **按「`raw/…` 下」理解，含 `raw/other/`** —— 本节即该澄清的**唯一授权出处**」；#3 逐字：「**仍须满足**：经 **`filing-fetch` 既有机制**取回、**本计划目录另存镜像与 sha 校验**、标 `external_retrieval_not_local` 如实、**等级归会计面**」
>
> 上一轮 R2 复裁条件（`OPEN3-E1-ACCT-RULING/a20260924-01/ruling.md`）：**L124–L128（R1 恢复规则）**、**L163（④ 恢复规则）**、**L185（⑤ 恢复规则）**、**L247（C1）**、**L251（C5）**、**L290（反例 1）**、**L293（反例 4）** —— 逐字要点：「origin 响应字节落进本计划目录……⇒ ① 可升 ✅ ⇒ 本卡新建 `R2` 载体复裁」；「**若 R1 落盘后内容与现有语料不一致** ⇒ 现有 4 文件降 E3、8 条引文作废，重新取证」；「R1 origin 落盘后，**在新载体上重跑同一套字节区校验**（不得复用本卡结论），通过后方可把引文升级为"已核"引用」。

⇒ **本卡授权成立**：等级裁定权 = 会计面（§二十七 #2「等级判定归会计面」+ L543 的工位指定）；被裁对象 = 已取回的 origin 字节。

### 0.2 `OWNER_DECISIONS` **L543** 逐字（本卡适用的纪律部分）

> 「| **3** | **E1 等级现交会计面裁** | **「要」**（澄清答确认） | 派 `1e143a7e` = `OPEN3-E1-ACCT-RULING`。**只定级、不重取**（禁联网；若必须看原站字节 ⇒ 判 `BLOCKED-NEEDS-ORIGIN-BYTES` 而**不自己去取**）；`fail-closed`——**不得为推进链抬高等级**；`releases_nothing=true` |」

### 0.3 本卡的网络口径：**禁联网（自加并保持）**

- L543 原文的受约束对象是「`OPEN3-E1-ACCT-RULING` 定级工位」；R2 取证卡已据 `progress.md L1244` 论证其不受约束并完成取回。
- **本卡 = 定级卡**，与 L543 的受约束对象同类（**只定级、不重取**），且派单明写「本卡是定级、不重取」「不需要联网」「字节已在盘上」。
- ⇒ **本工位网络请求 = 0**（全部判定用**盘上字节的本地计算**）。若定级必须看原站 ⇒ 按 L543 判 `BLOCKED-NEEDS-ORIGIN-BYTES` 而**不自己去取**（本卡不预期触发，因 origin 字节已在盘）。
- 由此产生并必须如实登记的**局限**：R2 `provenance.json` 中的**响应头自报**（`Content-Length` / Akamai 头 / `Set-Cookie`）**无原始头部落盘件**，本工位**无法独立复核**（只能核文件字节数与内容）⇒ 见 §三 Q1① 的限定。

### 0.4 写入面与只读清单

- **写入面 = 仅** `execution_runs/OPEN-3-ACCT-R2/a20260926-01/`（新建目录）。
- **只读**：`OPEN3-E1-ORIGIN-BYTES-R2`、`OPEN3-E1-ACCT-RULING`、`OPEN3-E1-ACQUISITION`、`OPEN3-E1-ORIGIN-BYTES`、两半区 `I11A-OPEN-ACCT` / `I11A-OPEN-IND` / `I11A-OPEN-MERGE`、封盘 `I-11-A`、`OWNER_DECISIONS.md`、`progress.md`、`task_plan.md`、五份计划文件。
- **禁**：写 `.planning` 之外任何文件（产品仓落点不归本卡）· `git` 写 · `git status` · 联网。
- 收尾须**复哈希自证**：被裁定对象与上游载体读前/读后 sha256 一致。

---

## §一 五问判据（冻结）

### Q1 —— `E1` 五要素在 **origin 层**是否全部成立？

| # | 要素（`I11A-OPEN-ACCT` L66/L153 原文） | 本卡判据（可本地复算） | fail-closed 触发 |
|---|---|---|---|
| ① | 申报**原文**本地归档 | 两份 `sec.gov` 目标响应体以**文件形式**在盘；`origin_bytes.bin` = 两文件首尾相接且总字节 = 62,953；**且**剥离边缘注入后内容与 EDGAR as-filed 归档副本**逐字节相同**（否则"原文性"不成立） | 任一不成立 ⇒ ① ❌ |
| ② | 文件 sha256 | 我**实测复算** 5 个 origin 件 + `origin_bytes.bin`，与 R2 `handoff.origin_sha256` **五值逐一相同** | 任一不符 ⇒ ② ❌ ⇒ 整件 `blocked` |
| ③ | 取回 UTC | `provenance.json` 有到秒的 `retrieved_utc`（四窗口）；与 `attempts[]` 读秒、`date_header` 自报互证；**窗口式 = 诚实形式**（上轮 3.3 已确认可接受） | 无 UTC 或与盘上事实矛盾 ⇒ ③ ❌ |
| ④ | 逐字引文**在 origin 载体上重跑**（ACCT L163） | 8 条引文（源 `OPEN3-E1-ACQUISITION/provenance.json verbatim_quotes[Q1..Q8]`）**由本工位自己重跑**，三法并列（见 §二 M1/M2/M3），**不采信 R2 自报 8/8、7/8** | 任一条 **M1（去空白）也不命中** ⇒ ④ ❌ ⇒ C5 触发 |
| ⑤ | 至少一条独立复核路径 | EDGAR 完整申报 `.txt`（as-filed 副本，2,721,504 B）为**独立 artifact**；判据 = origin 剥离注入后 ↔ 归档 inner 副本**逐字节相同**（两份都要） | 任一份不逐字节相同 ⇒ ⑤ ❌ + origin 保真存疑 |

**判定档位**：5/5 ⇒ ① 的"origin 层限定"解除；4/5 ⇒ `BLOCKED-PARTIAL`（沿用上轮 4.3 落点）；出现"语料↔origin 内容矛盾" ⇒ 见 Q2 C5。

### Q2 —— ⭐ `origin ↔ 既有语料` 一致性（**C5 裁定**）

**待裁两项事实（须本工位实测复现）**：
- **(a)** Q1 引文空格差：origin `(1) Agents` vs 语料 `(1)Agents`（R2 自报"仅 2 处空格差"）
- **(b)** `edge_injected_script` 在 8-K 与 EX99.1 **双命中**（含 `raw_sha` 与字节跨度 `[28544,28650]` / `[34147,34253]`）

**C5「不一致」的触发判据（冻结，四选一命中即触发）**：
1. 任一引文在 origin 上 **M1（去空白归一化）不可定位**；
2. 全量 token 双向比对中出现**无法归因的数值 token 差异**（数字不同、缺数字、多数字）；
3. 去空白后 origin 正文与语料正文存在**词序/词形/整句**差异，且**不能**归因于渲染器头部、图片 URL、表格换行等**排版性差异**（归因须逐条列出）；
4. **origin 自身保真不成立**：剥离注入后 ≠ EDGAR as-filed 副本（⇒ 此时降的不是语料，是 origin 本身与 S 等级）。

**明确**（不触发也要写明理由）：
- **仅空白差异**（空格 / 换行 / NBSP / 标签边界），且判据 1–3 均不成立 ⇒ **不构成 C5「不一致」**，登记为**转写排版差**，**4 份语料不降 E3**，但**必须在裁定里逐字披露该差异**。
- **`edge_injected_script`**：按**传输层注入、非申报正文**处理，判据 = (i) 注入片段**不在** as-filed 归档副本内；(ii) 剥离注入后 origin 正文与归档**逐字节相同**；(iii) 语料为**文本渲染**（r.jina.ai / W3C html2txt），天然不含 `script` 标签 ⇒ **不构成正文不一致**；**但**必须登记 `raw_sha`/`stripped_sha`/字节跨度/双命中事实，且**任何后续落产品仓必须同时登记 raw 与 stripped 两个 sha**。

**C5 触发的后果（fail-closed，反向也成立）**：既有 4 份语料**降 `E3`**、8 条引文**作废**、需重新取证 ⇒ 本卡 **E1 不成立**、定级回落 `BLOCKED-PARTIAL`。

### Q3 —— `E1` 等级

按 `I11A-OPEN-ACCT` **L66/L153（E1）/ L154（E2）/ L155（E3）/ L156（E0）** 逐条核，四选一：`E1-COMPLETE` · `E2` · `E3` · `BLOCKED-PARTIAL`。
- **`E1-COMPLETE`** 需：Q1 五要素 5/5 **且** Q2 未触发 C5 **且** L153 的附加要件（**重述后的基期分部数据**）在 origin 载体上可定位。
- **等级 ≠ 解除**：即便 `E1-COMPLETE`，`OPEN-3` 状态、参数放行、`ACCEPT` 一律不由本卡授予（§六）。
- L190 对称：**不得**自造或放宽 E1 定义（如"带限定的 ✅"——上轮 6.2.9 明确拒绝）。

### Q4 —— `S` 来源等级

按 `I11A-OPEN-ACCT` **L56–L60（S1/S2/S3/S4/S0）** 逐项，并逐项对 `I11A-OPEN-IND` **C 表（L229–L234，①②③④）** 过一遍：
- **S1** = 同一发行人**同一期间原文披露** + 可定位锚文本 + doc sha256 绑定 + **至少一条独立路径复核** ⇒ 可支撑冻结。
- 必须保留 `external_retrieval_not_local = true`（`progress L1244` + §二十七 #2 + IND L198/L360：**外部条目永久保留，只可新增 `local_ingested_at`**）。
- `kind` 诚实登记：8-K = `current_report` ⇒ 落 `raw/other/`（§三十一），**不得**谎报 `quarterly_report`。
- **S ≠ 放行**：S1 只解决"来源可采性"；参数放行仍需 ACCT **L226** 四要件（含**非实现者 `decision_sha256`**）+ MERGE 七条。
- fail-closed：若 Q2 判据 4 命中（origin 保真不成立）⇒ 本件来源**降 `S0`**。

### Q5 —— 解除还是维持 `BLOCKED-NEEDS-ORIGIN-BYTES`

**两个层次必须分开裁**（混同即违规）：
- **(i) 字节这一维的实质条件**（`origin_bytes_dimension_resolved: bool`）：Q1 五要素 5/5 **且** Q2 未触发 C5 **且** Q4 ≥ S1 ⇒ `true`；否则 `false`。
- **(ii) 名目的正式解除**：`BLOCKED-NEEDS-ORIGIN-BYTES` / `OPEN-3` / `B1` 的**状态变更权不在本卡**（`releases_nothing=true`）⇒ 本卡只给 **可回源核验的条件清单**，不改任何 `status/state/decision`。

**剩余阻断（须逐条列，禁止因"字节已解"而一笔勾销）**：
- **B1**：产品仓（`company-wiki`）落点 0 字节（R2 门 0 P1/P2/P3 全 DENIED；本会话同样审批禁用 ⇒ 预期仍 DENIED，若需实测按 §五 变异 G0 只读确认）；
- **B2**：`filing-fetch` 分支未跑 ⇒ 无 immutable provenance sidecar、产品仓 `git diff` 新增路径 `[]`；且 §三十二 记载**晋升 `blocked`**；
- **C5**：由本卡 Q2 裁定（裁完即消或转为新阻断）；
- **B3**：已由 §三十一 定口径（`raw/other/`），不再是阻断，但**落地仍待 B1/B2**。

---

## §二 引文重跑方法（冻结；三法并列，数字必须一起报）

设 `strip(html)` = 去除全部标签（`<...>`）、解码 HTML 实体（`html.unescape`），**不做空白处理**。

| 法 | 名称 | 定义 | 说明 |
|---|---|---|---|
| **M1** | **去空白归一化**（ws-insensitive） | `norm(s)` = 去除全部空白字符（` \t\n\r\f\v` + `\xa0` + 全角空白）后比对子串 | 与上轮 path B「去空白后子串匹配」同族；**对空白盲**，故须与 M2/M3 并报 |
| **M2** | **空白折叠**（ws-preserved / 空白敏感） | `collapse(s)` = 每个空白连续段折叠为**一个半角空格**、两端去空白；**不增删空格**；比对子串 | 能捕获 `(1)Agents` vs `(1) Agents`；对标签换行鲁棒 |
| **M3** | **严格**（ws-strict） | `strip(html)` 原样（空白一个不动）比对子串 | 最严；标签换行会误伤，故只作参考、不作单独否决依据 |

**同时必须重跑的两项前置校验（否则 ④ 无意义）**：
- **P-A**：8 条引文的 `byte_span` 落在对应 **corpus path A** 文件上，切片解码后与 `text` **逐字节相同**（8/8 才算引文记录本身可信）；
- **P-B**：8 条引文在 **corpus path B**（`*.verify-w3c-html2txt.txt`）上 M1 命中（复核上轮 ④ 的 path B 结论）。

**主报数**：**去空白 = M1 命中数/8**；**空白敏感 = M2 命中数/8**（M3 单列参考）。**任一与 R2 自报（8/8、7/8）不符 ⇒ 以我的实测为准并在裁定中明写差异。**

---

## §三 全量一致性比对（Q2 的证据，冻结）

- **T1 逐字节**：`origin_bytes.bin` vs 两 `.origin` 拼接；5 件 sha 实测 vs 自报五值。
- **T2 注入片段**：两份 origin 的 `[28544,28650]` / `[34147,34253]` 原始字节是否等于自报 `script_html`；两处是否**逐字节相同**；index 件与完整申报件是否**0 命中**；剥离后 sha/字节数是否等于自报 `6328d056…/28559`、`557161af…/34182`。
- **T3 独立路径**：从完整申报 `.txt` 中定位 8-K 与 EX-99.1 的 inner 副本，与"origin 剥离注入后（EX99.1 另剥 `<DOCUMENT>/<TEXT>` 包裹）"**逐字节**比对（两份）。
- **T4 全量 token 双向比对**（ACCT L185「与现有两路再做一次全量比对」）：`strip(origin)` 文本 ↔ 4 份语料，数字 token 与单词 token 双向差集，**逐条归因**（渲染器头部 / 图片 URL / 表格换行 / 空白）；**无法归因者 = C5 触发**。

---

## §四 `blocked` 触发（fail-closed，任一命中即降级或维持 `BLOCKED`，**不为推进而定级**）

1. 任一 origin 件实测 sha ≠ 自报五值，或 `origin_bytes.bin` ≠ 两文件拼接/总字节 ≠ 62,953 ⇒ **`blocked`**（完整性破坏）；
2. **P-A 失败**（引文在 corpus path A 字节区不逐字）⇒ 上游引文记录失真 ⇒ ④ ❌ ⇒ `BLOCKED-PARTIAL`；
3. 任一引文 **M1 不命中** origin ⇒ C5 触发 ⇒ 4 语料降 `E3`、引文作废 ⇒ **`BLOCKED-PARTIAL` 且 E1 不成立**；
4. T3 任一份 **≠ 逐字节相同** ⇒ origin 保真不成立 ⇒ ① ❌、⑤ ❌、**S 降 `S0`** ⇒ `blocked`；
5. T4 出现**无法归因的数值/内容差异** ⇒ C5 触发 ⇒ 同 #3；
6. Q1 任一要件不成立 ⇒ 按上轮 4.3：只能落 `E2` 或 `BLOCKED-PARTIAL`，**且**若"已落盘归档"事实成立则 `E2` 定义冲突 ⇒ 取 `BLOCKED-PARTIAL`；
7. 写入面越出本卡目录 / 任何 `git` 写 / 使用 `git status` / 任何联网 ⇒ **事故 ⇒ `blocked`** 并如实登记；
8. 需要看原站才能定级而盘上证据不足 ⇒ 按 L543 判 `BLOCKED-NEEDS-ORIGIN-BYTES`，**不自己去取**。

---

## §五 变异清单（红/绿判别力；§5.2 追加实测，不改判据）

### 5.1 预设变异（冻结时定义）

| # | 变异（人为注入的坏输入） | 期望 | 判别依据 |
|---|---|---|---|
| **G0** | 只读确认：产品仓三处目录**可读性**（不写） | 只报事实（不作写探针 —— 本卡不落产品仓） | §〇.4 |
| **G1** | 正常：真实 8-K origin + 真实 Q1 引文 ⇒ 全套校验 | **绿（通过）** | §二 / §三 |
| **R1** | 用 SEC 拦截页（`_mutation_R1_sec_block_page.htm`，4,819 B）冒充 8-K origin | **红** | sha 不在登记表 + 引文 M1 不命中 |
| **R2** | 用 EDGAR index 件冒充 8-K origin | **红** | 同上 |
| **R3** | 用 **corpus `.md` 语料**冒充 origin 载体 | **红** | sha 不在 `origin_sha256` 登记表（正是"转写件冒充 origin"） |
| **R4** | 真实 origin 拷贝**翻转 1 字节** | **红** | ② sha 复算不符 |
| **R5** | 引文**改一个数字**（`$268,127` → `$268,126`）后在 origin 上重跑 | **红** | M1/M2/M3 全不命中（证明引文校验有判别力） |
| **R6** | 引文**改一个词**（`Agents` → `Agent`）后在 origin 上重跑 | **红** | M1/M2/M3 全不命中 |
| **R7** | **空白变异对照**（在引文中**只加/去一个空格**） | **M1 绿、M2 红**（**登记为已知盲区**，非判别力缺陷 —— 这正是 M2 必须并报的原因） | §二 |

**判别力合格线**：`discrimination_ok = true` ⇔ **G1 绿 + R1–R6 全红**（R7 按设计 M1 绿/M2 红，单独登记）。

### 5.2 实测输出（**追加式**；§一~§四与 §5.1 判据正文一字未改）

**执行环境**：`python 3.13.9`（本机），零联网；脚本 `verify_e1.py`、原始输出 `_verification_raw.json`（同目录）。

#### 5.2.1 T1 完整性（要素①②）

| 对象 | 实测字节 | 实测 sha256（前 16） | 与 R2 `handoff.origin_sha256` 五值 | 字节自报 |
|---|---|---|---|---|
| `d291965d8k.htm.origin` | 28,665 | `a3d0bbf6411bb2b2…` | ✅ | ✅ |
| `d291965dex991.htm.origin` | 34,288 | `47a0a4a1d6a335ff…` | ✅ | ✅ |
| `origin_bytes.bin` | 62,953 | `cf84c29048ab314e…` | ✅ | ✅ |
| `_identity_…index.htm` | 17,557 | `618f010b6e56597c…` | ✅ | ✅ |
| `_independent_…submission.txt` | 2,721,504 | `d82838ac92ed3e8b…` | ✅ | ✅ |
| `_mutation_R1_sec_block_page.htm` | 4,819 | （R2 登记 `2922be22…`） | ✅ | ✅ |

- **`origin_bytes.bin == 8-K ∥ EX99.1` 逐字节成立**（`bin_is_concat = True`，偏移 `[0,28665)` / `[28665,62953)`）。
- **既有 4 份语料 sha 实测全部一致**：`096c7d9d…` / `5927de03…` / `20392f0e…` / `56b0460b…`（与 ACQUISITION `handoff` 及上轮裁定 §② 一致）⇒ 待裁对象 **0 字节变更**。

#### 5.2.2 T2 边缘注入脚本（Q2(b) 实测）

| 检查 | 实测 |
|---|---|
| `[28544,28650]` 原始字节 == 自报 `script_html` | **True** |
| `[34147,34253]` 原始字节 == 自报 `script_html` | **True** |
| 两处片段**逐字节相同** | **True**（同一 `src=/QQpw/SBxk/…` 路径） |
| 出现次数：8-K / EX99.1 | **1 / 1**（双命中成立） |
| 出现次数：EDGAR index 件 / 完整申报件 | **0 / 0**（as-filed 内不存在） |
| 8-K 剥离后 | 28,559 B · `6328d05612511965…` ✅ 与自报一致 |
| EX99.1 剥离后（保 SGML 包裹） | 34,182 B · `557161af7ac2f2ee…` ✅ 与自报一致 |

#### 5.2.3 T3 独立复核路径（要素⑤）

| 对象 | origin（剥注入） | as-filed 归档 inner | 逐字节相同 | 归档内偏移 |
|---|---|---|---|---|
| 8-K | 28,559 B · `6328d056…` | 28,559 B · `6328d056…` | **True** | 1,178 |
| EX-99.1（剥 `<DOCUMENT>/<TEXT>` 包裹） | 34,070 B · `4cb79b6e…` | 34,070 B · `4cb79b6e…` | **True** | 29,857 |

（归档 8-K 的 `<TEXT>` 内层带 `<XBRL>…</XBRL>` 包裹，28,575 B；只剥离该字面标记后与 origin 剥注入内容**完全相同**。）

#### 5.2.4 引文重跑（要素④；**自己重跑，不采信自报**）

| 法 | 定义 | 命中 | 明细 |
|---|---|---|---|
| **P-A** | 引文 `byte_span` 落在 corpus path A 上**逐字节相同** | **8/8** | 引文记录本身可信 |
| **P-B** | corpus path B 上 **M1** 命中 | **8/8** | 复核上轮 ④ 的 path B 结论 |
| **M1 去空白**（主报数） | 去全部空白后子串 | **8/8** | rc=0 |
| **M2 空白折叠**（主报数·空白敏感） | 空白连续段→单空格、不增删 | **7/8** | **Q1 未命中**，其余 7 条命中 |
| **M3 严格**（参考） | 原样子串 | 3/8 | 标签换行所致，仅登记、不单独否决 |

- 与 R2 自报（去空白 8/8、空白敏感 7/8、Q1 差 2 空格）**完全一致**（我独立复现）。
- R2 `provenance` 登记的两个原始 ASCII 锚点字节区**复核通过**：8-K `[21796,21866]`、EX99.1 `[3079,3139]`（切片 == 锚文本，2/2）。
- **Q1 空格差的字节级定位**：origin 原始 HTML 为 `(1)&#160;Agents … (2)&#160;Devices`（**U+00A0 NBSP ×2**）；corpus 为 `(1)Agents … (2)Devices`（**0 个空白字符**）。⇒ **纯空白类差异**，去空白后完全相同。

#### 5.2.5 T4 全量 token 双向比对（ACCT L185；Q2 的证据）

| 对 | 数值 token 差 | 归因（逐条） |
|---|---|---|
| 8-K ↔ corpusA `.md` | origin 独有 `{0000789019, 09}`；corpus 独有 `{06, 20, 31}` | 前者 = origin 的 iXBRL header 事实（不可见元数据，corpusA 未含）；后者 = r.jina.ai 渲染头 `Published Time: Wed, 02 Sep 2026 20:31:06 GMT` |
| 8-K ↔ corpusB `.txt` | **0 / 0** | — |
| EX99.1 ↔ corpusA `.md` | **0 / 0** | — |
| EX99.1 ↔ corpusB `.txt` | corpus 独有 `{21, 5, 8}` | = html2txt 输出的图片 `alt="Slide 21/5/8"` 图注（origin 标签属性被剥除）；**非数值矛盾** |

⇒ **数值侧 0 个无法归因的矛盾**（`decision.md L27` 的失效条件「互相矛盾的被引用数值」**未触发**）。

**但词/段侧发现两处新差异（R2 自报与派单均未提及，由本工位全量比对得出）**：

1. **`amplifying` vs `amplifies`（EX99.1 同一句）** —— 字节级实测：
   | 文件 | `amplifying` | `amplifies` |
   |---|---|---|
   | origin `d291965dex991.htm.origin` | **1** | 0 |
   | as-filed 完整申报归档 | **1** | 0 |
   | corpusA `Exhibit99-1.md` | 0 | **1** |
   | corpusB `Exhibit99-1.verify-w3c-html2txt.txt` | 0 | **1** |
   同句上下文：`…to ensure AI empowers every person, ▯ their agency and ambition. That is what we mean by a frontier ecosystem…` ⇒ **词级内容不一致**（不可归入 §一 Q2 允许的排版归因清单）。
2. **corpusA 缺 8-K 签名页整段** —— origin 与 corpusB 均含 `Date: September 2, 2026 / /s/ Alice L. Jolla / Alice L. Jolla / Corporate Vice President and Chief Accounting Officer`；**corpusA 全无**（corpusA 正文止于 `104 Cover Page Interactive Data File`）⇒ **整段缺漏**（非渲染器头部/图片 URL/表格换行）。

⇒ **Q2 判据 3 命中 ⇒ C5「不一致」成立**（详见 §一 Q2 与裁定正文）。

#### 5.2.6 变异判别力（`rc` 约定：**0 = 该变异按预期表现**）

| # | 变异 | 期望 | 实测 | rc |
|---|---|---|---|---|
| G1 | 真实 8-K origin + 真实 Q1，**M1∧M2∧M3 全套** | 绿 | **未通过**：M2/M3 拒绝 Q1（NBSP 差） | **1** |
| G1b | 验收规则（登记 sha + **8/8 M1** + P-A 8/8） | 绿 | 通过 | **0** |
| R1 | SEC 拦截页冒充 8-K origin | 红 | 检出（sha 不在登记表 + 引文不命中） | 0 |
| R2 | EDGAR index 件冒充 8-K origin | 红 | 检出 | 0 |
| R3 | corpus `.md` 转写件冒充 origin 载体 | 红 | 检出 | 0 |
| R4 | origin 拷贝翻转 1 字节 | 红 | 检出（sha 复算不符） | 0 |
| R5 | 引文改一个数字（`$268,127→$268,126`） | 红 | M1/M2/M3 全拒 | 0 |
| R6 | 引文改一个词（`Agents→Agent`） | 红 | M1/M2/M3 全拒 | 0 |
| R7 | **仅空白变异**（给 Q1 补一个空格） | M1 绿 / M2 红 | 符合（M1=True、M2=False） | 0 |

- **`discrimination_ok = true`**（`G1b` 绿 + R1–R6 六红全检出）。
- **`discrimination_ok_literal_G1 = false`** —— **如实登记**：§5.1 写的 G1 用 Q1 且要求"全套校验"，其 `rc=1` **不是**判别力缺陷，而是**该变异恰好测到了 Q2(a) 那个空白差**（M2/M3 对 NBSP 缺失的正确拒绝）。**不回改 §5.1 判据**，以 G1b（= §一 Q1④ 冻结的验收规则）作为绿样。
- **R7 是已知盲区登记**：M1 对空白盲，故 M2 必须并报 —— 这正是 Q1 差异能被 M2 抓住而 M1 放过的原因。

---

## §六 不授予清单（本卡**没有**的权力）

- **不解除 `OPEN-3`**（等级 ≠ 解除）· **不解除 `BLOCKED-NEEDS-ORIGIN-BYTES` / `B1` / `B2` 的任何状态**（只给判定与条件清单）
- **不落产品仓**（`company-wiki` / `dayu-agent` **0 字节**；产品仓落点是父的第 ① 件）
- **不放行任何参数**（`MSFT_*_FY2027` 系列与新两分部参数一律维持未放行）
- **不产生 `ACCEPT`** · **不代签矿业面** · **不改任何 `status/state/decision/decision_sha256`**
- **不写五份计划文件**（`task_plan.md` / `findings.md` / `progress.md` / `audit_report.md` / `delivery_validation.json`）· **不写 `.planning` 之外任何路径**
- **不碰两半区裁定 / 封盘 `I-11-A` / `OPEN6-TOLERANCE-*` / `BLOCKED6C-*` / `OPEN6-H2-*` 任一字节**
- **不联网**（0 次网络请求）· **0 次 `git` 写** · **禁 `git status`**（只用 `git -c core.quotepath=false diff HEAD --name-only`）
- **不改 E1/S 定义**（ACCT L190 对称：放宽与收紧都须 owner 追加登记）
