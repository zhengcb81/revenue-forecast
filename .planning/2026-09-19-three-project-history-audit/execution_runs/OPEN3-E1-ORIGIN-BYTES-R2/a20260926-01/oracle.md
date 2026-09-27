# oracle.md · `OPEN3-E1-ORIGIN-BYTES-R2` / `a20260926-01`（**先冻结**）

- **卡**：`OPEN3-E1-ORIGIN-BYTES-R2`（`MERGE` 七条 **`C3` 第 1 步**的**证据取证**层）｜ **attempt**：`execution_runs/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01`
- **role**：`evidence_acquirer`（证据取证工位）｜ **父**：`session-19074bf0-0205-4315-af73-9db57597275a`
- **冻结时刻（UTC）**：见 `provenance.json` 的 `oracle_frozen_utc`（本文件判据一经落盘即不再改；其后的 §五 只追加实测原始输出，不回改判据正文）
- **本工位要解的缺口**：`origin_bytes_retrieved = 0` → `BLOCKED-NEEDS-ORIGIN-BYTES`（门核 `db46a988`：「`C3` 是最硬的一条」）
- **本工位不判等级、不解除任何 BLOCKED**（见 §六 不授予清单）

---

## §〇 授权与网络口径（逐字回源，不采信派单转述）

### 0.1 网络：**本会话不禁网**（项目默认 = 允许）

> **`progress.md`（`.planning/2026-09-19-three-project-history-audit/progress.md`）L1244 逐字**：
> 「**网络口径（本轮明确，需入册）**：允许 `web_search`/`web_fetch` 取证（专家 reviewer 职权），但**每条外部证据必须落 `provenance.json`**（URL + 取回 UTC + 原文引文 + 快照 sha）；**外部来源不得冒充本地可核事实**——I-11-A 已登记「2026-09-02 8-K 原文不在本地可核来源」，联网取到须显式标注为**外部获取**。」

> **`REMEDIATION_REGISTER.md` §153 更正块逐字（L3788–L3796）**：
> 「**⚠️【更正 · 2026-09-26 13:15】** 本节原文写「`filing-fetch` 但**本会话禁网**」——**这是错的，已实测推翻**：`https://example.com` **HTTP 200 ⇒ 会话不禁网**。」
> 「| `progress L1244`（网络口径，本轮明确） | **项目默认 = 允许** | **「允许 `web_search`/`web_fetch` 取证（专家 reviewer 职权）」**，外部证据须落 `provenance.json`（URL+取回 UTC+引文+快照 sha）、**不得冒充本地可核** |」
> 「**⇒ `AR2023` 取回的真正阻断 = `company-wiki` 可写（即 `B1`）+ 取回后须落 provenance，而非网络。**」

### 0.2 `OWNER_DECISIONS.md` **L543**（「禁联网」的**真正出处**）逐字

> `## 二十六` 表格第 3 行：「| **3** | **E1 等级现交会计面裁** | **「要」**（澄清答确认） | 派 `1e143a7e` = `OPEN3-E1-ACCT-RULING`。**只定级、不重取**（禁联网；若必须看原站字节 ⇒ 判 `BLOCKED-NEEDS-ORIGIN-BYTES` 而**不自己去取**）；`fail-closed`——**不得为推进链抬高等级**；`releases_nothing=true` |」

**为什么本卡不受 L543 约束（本工位逐字论证）**：
1. **L543 的受约束对象被原文点名** = 「派 `1e143a7e` = **`OPEN3-E1-ACCT-RULING`**」，其事项栏是「**E1 等级现交会计面裁**」，动作栏是「**只定级、不重取**」⇒ 该「禁联网」是**给『定级工位』的卡级纪律**（定级者不得自行取证，否则定级与取证同源、失去独立性）。
2. **同一行还规定**：「若必须看原站字节 ⇒ 判 `BLOCKED-NEEDS-ORIGIN-BYTES` 而**不自己去取**」—— 这句**本身就把『取字节』外派给了另一个工位**；`BLOCKED-NEEDS-ORIGIN-BYTES` 这个名目**存在的意义就是等待一个专门去取字节的工位**。本工位正是那个工位。
3. **`REMEDIATION_REGISTER` §153 更正表已把三条口径分层**（L3792–L3795）：`L541` = owner 授权联网 · **`L543` = owner 按卡禁网（仅 E1 定级工位）** · **`L1244` = 项目默认允许** · `L1186`「零网络」= **父自己加的保守默认，不是会话限制**。
4. **父的更正**：本卡派单明写「你此前的派单惯例里可能有『禁网』字样 —— 那是给**复审工位**的保守默认，对**本卡不适用**」，出处即 §153 更正块。
5. ⇒ **结论**：本卡**受 `L1244` 约束（须落 provenance、不得冒充本地可核）**，**不受 `L543` 的「禁联网」约束**；但本工位**仍不判等级**（等级归会计面，与 L543 的隔离精神一致）。

### 0.3 落点授权

- **`OWNER_DECISIONS.md` §二十七 #2**（2026-09-25）owner 选择「**落产品仓（与 filing-fetch 同流）（建议）**」⇒ 「允许 origin 字节**经 filing-fetch 既有机制落 `company-wiki/companies/{entity}/raw/…`**，本计划目录**另存镜像与 sha 校验**；仍标 `external_retrieval_not_local` 如实；**等级判定归会计面**；本裁**不解除 `OPEN-3`、不产生 ACCEPT**」。
- **§三十一 #2**（2026-09-26）：`raw/financial_reports/{kind}/` **按「`raw/…` 下」理解，含 `raw/other/`** —— **8-K 按诚实 kind `current_report` 落 `raw/other/`**，**不改 `canonical_writer` 映射、不谎报 `quarterly_report`**。
- **§三十**（B2 扩闸授权）与 **§三十二**（B2 晋升授权）已给，但 §三十二 记载 **晋升 `blocked`**（`git apply` 事故后两文件已复原）⇒ **本工位不假定 B2 改动已在生产**，须**实测**。

### 0.4 上一轮为什么 BLOCKED（逐字回源，不采信派单）

- `execution_runs/OPEN3-E1-ORIGIN-BYTES/a20260925-01/handoff.json`：`status=BLOCKED`；`origin_bytes_retrieved=0`；阻断 **B1 落点**（`company-wiki` 在 `workspace-write` 下全域拒写，filing-fetch `attempt to write a readonly database` / `downloads=0`）、**B2 机制**（dayu `L1112/L1124 if include_exhibits and form_type == "6-K"` ⇒ 8-K 不下 exhibit）、**B3 形态**（诚实 kind → `raw/other/`，§三十一 已解）。
- 要取的两个 URL（上一轮 `target_documents` 逐字）：
  - `https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965d8k.htm`（8-K 本体）
  - `https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm`（Exhibit 99.1）

---

## §一 门 0 判据（纪律 16/17：**能力门前置，自己探**）

**必须在本工位自己做一次真实写探针，不得采信父的探针结果。**

### 1.1 探针对象（4 处，逐处独立判定）

| # | 目录 | 为什么探 |
|---|---|---|
| P0 | `.planning/.../execution_runs/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/`（本工位产出目录） | 本工位基本写入面 |
| P1 | `C:\Users\郑曾波\Projects\company-wiki\companies` | filing-fetch / origin 字节授权落点 |
| P2 | `C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog` | 父声明的探针面之一 |
| P3 | `C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\dayu\fins\downloaders` | 父声明的探针面之一 |

### 1.2 探针动作（三步**全部**成功才算过）

1. **写**：在目录内创建唯一命名临时文件 `_gate0_probe_<pid>_<n>.tmp`，写入固定载荷 `GATE0-PROBE-a20260926-01`（25 字节）→ **rc 必须 = 0**
2. **回读**：读回全部字节并逐字比对载荷（长度 25 + 内容相等）→ **rc 必须 = 0 且比对 = TRUE**
3. **删除**：删除该临时文件并 `Test-Path` 确认不存在 → **rc 必须 = 0 且残留 = FALSE**

### 1.3 门 0 判定

- **P0 必须过**（否则本工位无法产出任何东西）。
- **P1 过** ⇒ 允许走「filing-fetch 落产品仓」分支；**P1 拒** ⇒ **该分支不执行**（不换方法、不换落点），只落本计划目录，并如实判 `blocked`/`BLOCKED-PARTIAL`（见 §四）。
- **任一探针失败 ⇒ 立即停在原地、报 `blocked` 并明写「无写权限」**；**禁止**任何可能破坏原状的替代方法。
- **明确禁用的替代方法（纪律 16 的教训）**：`git apply` · `>` 重定向覆盖已存在文件 · 删除-重写 · `git checkout/restore` · 任何先删后写的补丁路径。**本工位全程 0 次 git 写**。

---

## §二 取证步骤（冻结）

### S1 回源确认文档身份（**先读记录，后取字节**）

- URL 必须与 §0.4 上一轮 `target_documents` **逐字一致**；任何不确定 ⇒ `blocked`（不猜、不换相似文档）。
- 文档身份锚：`accession = 0001193125-26-380280`、`CIK = 789019`、`filer = MICROSOFT CORP`、`form = 8-K`、`item = 7.01`、报告日 `2026-09-02`。

### S2 取回**原始响应字节**（下载型机制，非文本转写）

1. **机制必须是下载型**（逐字依据 `OPEN3-E1-ACCT-RULING/a20260924-01/ruling.md` **L126**）：
   > 「harness `web_fetch` **只回文本、不产响应字节** ⇒ **即使 SEC 直取成功，走 `web_fetch` 也不构成 origin 字节捕获**；R1 必须用**下载型**机制（如 filing-fetch `--allow-download` 改落盘点 / dayu-agent 等价物 / owner 指定的其它落盘工具）。」
2. **候选机制（按序，命中即停，全部如实登记）**：
   - **M1 `filing-fetch` 既有机制**（`--allow-download`，与 §二十七 #2 同流）→ 落 `company-wiki/.../raw/other/`（§三十一）。
   - **M2 等价下载型 HTTP 取回**（`Invoke-WebRequest -OutFile` / `requests.get(stream)` 等**逐字节落盘**的下载），带**已声明 UA**（SEC 要求 `Name Contact@email` 形式）；产物 = 响应体原始字节文件 `origin_bytes/*.htm` + 本计划目录镜像。
   - **M3 `web_search`/`web_fetch`**：**仅**用于辅助定位/交叉引文，**其文本永不计入 `origin_bytes_retrieved`**（L126 明文）。
3. **HTTP 状态必须逐条登记**：`200` 才可计入 origin 字节；`403/429/5xx/重定向到非目标页` ⇒ **不计入**、按 §四 判 `blocked`。

### S3 落盘与四要素

1. 字节文件落 **本工位产出目录**（`origin_bytes/` + 镜像 `origin_bytes.bin` 说明），**sha256 立即复算**；
2. **再读回复算一次 sha256**（写后重读，两次一致才成立）；
3. 若 M1 成功：**同时**记录产品仓文件 sha + 产品仓 `git diff HEAD --name-only` 的**新增路径**；
4. `provenance.json` 必须齐 §三 全部字段，**缺一 ⇒ `blocked`**。

### S4 量化登记

- `origin_bytes_retrieved`：**实测字节数**（0 → 实测）
- `origin_sha256`：实测
- 对照 `I11A-OPEN-ACCT/ruling.md` **E1 五要素**（L66 / L153）逐项判定：① 申报原文本地归档 ② 文件 sha256 ③ 取回 UTC ④ 逐字引文 ⑤ 至少一条独立复核路径
- 满足 ⇒ 如实报「字节层已补」，**仍不判 E1**；不满足 ⇒ 判 **`BLOCKED-PARTIAL`** 并列出缺项。

---

## §三 `provenance.json` 必备字段（**缺一即 `blocked`**）

每条外部证据至少：

| 字段 | 说明 |
|---|---|
| `url` | 完整 URL（逐字） |
| `retrieved_utc` | 取回 UTC（秒级） |
| `http_status` | 整数；`null` 不可接受于成功条目 |
| `bytes` | 响应体字节数（整数，= 文件长度） |
| `sha256` | 响应体 sha256（十六进制 64 位） |
| `verbatim_quote` | **原文逐字引文**（≥1 段，可本地复核；含锚文本） |
| `mechanism` | 下载型机制名（M1/M2/M3 分类 + 具体命令族） |
| `user_agent` | 实际发出的 UA |
| `external_retrieval_not_local` | **必须 = `true`**（L1244：联网取到须显式标注为外部获取） |
| `document_identity` | accession / CIK / filer / form / item / report_date |
| `landed_path` | 落盘路径（本计划目录；若 M1 成功则另有产品仓路径） |
| `product_repo_sha256` / `product_repo_new_paths` | 仅 M1 成功时必填 |

另须：`oracle_frozen_utc`、`gate0`（4 处探针原始输出 + bool）、`attempts[]`（含失败的，逐条读秒）、`previous_round_verification`（上一轮 4 语料 sha 复测）。

---

## §四 `blocked` 触发条件（**fail-closed，任一命中即判 `blocked` / `BLOCKED-PARTIAL`**）

1. **门 0 任一探针写/回读/删除失败** ⇒ `blocked`（原话「无写权限」），停手；
2. **URL 不确定**或与上一轮记录不逐字一致 ⇒ `blocked`；
3. **HTTP ≠ 200**（含 403「Undeclared Automated Tool」、429、5xx、验证码/风控页）⇒ 该条**不计入** `origin_bytes_retrieved`；两目标均未取得 ⇒ `blocked`；
4. **响应体是 SEC 错误页/拦截页**（内容形态判别，非 200 判别）⇒ 不计入；
5. **取到的是相似文档而非目标 accession**（`0001193125-26-380280` 不匹配）⇒ **不冒充**，`blocked`；
6. **`provenance.json` 缺 §三 任一字段** ⇒ `blocked`；
7. **写后读回 sha 与首算不一致** ⇒ `blocked`（文件完整性破坏）；
8. **只有文本转写、无原始响应字节**（web_fetch 产物）⇒ 不计入，`blocked`；
9. **任一被禁替代方法被触发（`git apply` 等）** ⇒ `blocked` 并如实登记为事故。

**部分成功处置**：仅一个目标文档取得字节、另一个未取得 ⇒ 判 **`BLOCKED-PARTIAL`**（如实列 1/2），**不得**判 `blocked-green`、**不得**判满足。

---

## §五 变异清单（红/绿判别力；本节**追加**实测原始输出，不改上文判据）

### 5.1 预设变异（冻结时定义）

| # | 变异（人为注入的坏输入） | 期望 | 判别依据 |
|---|---|---|---|
| G | 正常：目标 URL + 200 + 真实 8-K 体 | **绿（通过）** | §二 S2/S3 |
| R1 | 传入 SEC 拦截页（`Undeclared Automated Tool`）体当 origin 字节 | **红（blocked）** | §四 #4 |
| R2 | 传入**另一份** 8-K（不同 accession）的字节 | **红（blocked）** | §四 #5 |
| R3 | 传入 `web_fetch` 文本转写（非响应字节） | **红（blocked）** | §四 #8 / L126 |
| R4 | 传入 sha256 缺失或与文件复算不符的条目 | **红（blocked）** | §四 #6/#7 |
| R5 | 门 0 探针拒绝（模拟 P1 拒写） | **红（blocked）** | §四 #1 |
| R6 | 缺 `verbatim_quote` 或缺 `retrieved_utc` | **红（blocked）** | §四 #6 |

### 5.2 实测输出（探针与取回完成后**追加**，逐条读秒）—— **本节为追加式，§一~§四与§5.1 判据正文一字未改**

#### 5.2.1 门 0 探针原始输出（逐字，另有独立件 `gate0_probe_raw.txt`）

```
payload = "GATE0-PROBE-a20260926-01"（24 字节；§1.2 原文误写为 25 字节，实测 24，此处如实更正）
probe PID = 16680
P0_output_dir | dir=...\OPEN3-E1-ORIGIN-BYTES-R2\a20260926-01 | exists=True | WRITE_rc=0 | READBACK_rc=0 | match=True (len=24) | DELETE_rc=0 | residual_exists=False
P1_company_wiki_companies | dir=C:\Users\郑曾波\Projects\company-wiki\companies | exists=True | WRITE_rc=ERR: Exception calling "WriteAllText" with "3" argument(s): "Access to the path 'C:\Users\郑曾波\Projects\company-wiki\companies\_gate0_probe_16680_2.tmp' is denied." | READBACK_rc=NA | match=NA | DELETE_rc=NA | residual_exists=NA
P2_cw_source_catalog | dir=C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog | exists=True | WRITE_rc=ERR: ... '...\source_catalog\_gate0_probe_16680_3.tmp' is denied. | READBACK_rc=NA | DELETE_rc=NA | residual_exists=NA
P3_dayu_downloaders | dir=C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\dayu\fins\downloaders | exists=True | WRITE_rc=ERR: ... '...\downloaders\_gate0_probe_16680_4.tmp' is denied. | READBACK_rc=NA | DELETE_rc=NA | residual_exists=NA
```

- **判定**：P0 **PASS**；P1/P2/P3 **DENIED** ⇒ `gate0_writability_passed = false`（对产品仓目标目录）。
- **分支处置**：**产品仓落点分支停手** —— 未运行 `filing-fetch --allow-download`，未尝试 `git apply`/`>` 重定向/删除-重写/checkout 任何替代写法（纪律 16）；三处 probe 文件在创建前即被拒 ⇒ 产品仓 **0 字节残留**。
- **与父探针的关系**：父 2026-09-26 14:0x「三处全 OK」为**带 `danger-full-access` 提权**所测；本工位无提权（审批禁用、子代理权限固定）⇒ 两份探针都为真，**这正是纪律 16/17 要求自探的理由**。

#### 5.2.2 取回窗口与结果（全部读秒）

| # | 机制 | 目标 | UTC（Z） | HTTP | 字节 | sha256（前 16） | 计入 origin 字节 |
|---|---|---|---|---|---|---|---|
| A1 | PS5.1 `Invoke-WebRequest` / .NET `HttpClient` | SEC | 13:0x | — | — | — | 否（TLS 握手失败「基础连接已经关闭」） |
| A2 | `curl.exe`（schannel） | SEC | 13:0x | — | — | — | 否（rc=35 `SEC_E_NO_CREDENTIALS`） |
| A3 | harness `web_fetch`（**文本型**） | 8-K Ex99.1 | — | **403** | — | — | 否（未声明 UA 拦截页；且非下载型） |
| A4 | Python `urllib`（声明 UA，**下载型 M2**） | EDGAR index | 13:29:40 | **200** | 17,557 | `618f010b…` | 否（身份确认件） |
| A5 | 同上 | **`d291965d8k.htm`** | 13:29:40→13:29:41 | **200** | **28,665** | `a3d0bbf6411bb2b…` | **是** |
| A6 | 同上 | **`d291965dex991.htm`** | 13:29:41→13:29:42 | **200** | **34,288** | `47a0a4a1d6a335ff…` | **是** |
| A7 | 同上 | EDGAR 完整申报 `.txt`（**独立路径**） | 13:30:33→13:30:36 | **200** | 2,721,504 | `d82838ac92ed3e8b…` | 否（复核件） |
| A8 | Python `http.client` 原始头复取 | 8-K（第 3 次） | 13:38:59 | **200** | 28,665 | `a3d0bbf6411bb2b…` | 否（稳定性复测，sha 三次一致） |

**`origin_bytes_retrieved = 62,953`（2/2 目标均 200）**；`origin_bytes.bin` = 两份响应体首尾相接，`sha256 = cf84c29048ab314e329758975e101804ba3032f28e2b22d0373f46e3d3c9db1e`。

#### 5.2.3 变异判别力实测（`mutation_results.json`）

**`discrimination_ok = true`（1 绿 + 6 红全部按预期）**：

| # | 变异 | 期望 | 实测触发 |
|---|---|---|---|
| G | 正常目标 URL + 200 + 真实 8-K 体 | 绿 | `accepted=true`，0 失败 ✅ |
| R1 | SEC 拦截页当 origin 字节（真实取回，HTTP 403 / 4,819 B / `2922be22…`） | 红 | V1 + V7 + V4 ✅ |
| R2 | 同申报 index 页冒充目标文档 | 红 | V6 + V4 ✅ |
| R3 | `web_fetch` 文本转写 | 红 | V8 + V2b + V4 ✅ |
| R4 | sha256 与复算不符 | 红 | V2 ✅ |
| R5 | 门 0 拒写仍尝试落产品仓 | 红 | V10 ✅ |
| R6 | 缺 `verbatim_quote` / `retrieved_utc` | 红 | V4 + V3 ✅ |

#### 5.2.4 保真度发现（如实登记，**不作等级判断**）

- 响应体含一个**边缘注入脚本** `<script type="text/javascript" src="/QQpw/SBxk/Vaws3/_e/ukQ/ahaE2chLLGzQfS/Ji1MAQ/Zg9QCV/p9Knc"></script>`（8-K 位于 [28544,28650]、Ex99.1 位于 [34147,34253]）；**`Content-Length: 28665` 与实收字节数一致**、响应头为 SEC 的 S3+Akamai 头（`x-amz-request-id`、`X-Akamai-Transformed`、`Set-Cookie: bm_sz`）⇒ **该脚本确属本客户端收到的 HTTP 响应体**，非本地改写。
- **去掉该注入后，两份 origin 内容与 EDGAR 完整申报归档副本（2026-09-02 as-filed）逐字节相同**（8-K：剥 `<XBRL>` 包裹与尾换行后 `byte_identical=true`；Ex99.1：剥 `<DOCUMENT>/<TEXT>` 包裹后 `byte_identical=true`）⇒ **⑤ 独立复核路径成立**。
- **8 条引文在 origin 载体上重跑**（ACCT L163）：**去空白归一化 8/8 命中**；**空白敏感 7/8** —— 唯 Q1 差 2 处空格（origin `(1) Agents` / 语料 `(1)Agents`）。**是否构成 ACCT C5「不一致」由会计面裁，本工位不裁。**

---

## §六 不授予清单（本工位**没有**的权力）

- **不解除 `OPEN-3`**（只补字节，等级仍归会计面）
- **不解 `B1` / `BLOCKED-NEEDS-ORIGIN-BYTES`**（只把证据交上去，解除归复审/有权方）
- **不判 E1/E2 等级**（`level_claimed = null`）
- **不产生 `ACCEPT`** · **不放行任何参数** · **不代签** · **不改任何 `status/state/decision/decision_sha256`**
- **不碰两半区裁定 / 封盘 `I-11-A` / `OPEN6-TOLERANCE-*` / `BLOCKED6C-*` / `OPEN6-H2-*` 任一字节**
- **不碰 `.planning` 内别人的卡** · **不改产品仓既有文件** · **0 次 git 写**（禁 `add/commit/push/checkout`，**禁 `git status`**，只用 `git diff HEAD --name-only`）
- **不做 `filing-fetch`/dayu 产品代码改动**（§三十/§三十二 的产品改动归另卡）
