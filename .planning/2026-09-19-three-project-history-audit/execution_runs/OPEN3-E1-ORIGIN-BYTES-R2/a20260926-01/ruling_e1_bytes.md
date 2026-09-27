# `OPEN3-E1-ORIGIN-BYTES-R2` · `a20260926-01` — origin 响应字节取证裁定（`ruling_e1_bytes.md`）

- **卡 / attempt**：`OPEN3-E1-ORIGIN-BYTES-R2` / `execution_runs/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01`
- **role**：`evidence_acquirer`（证据取证工位）｜ **父**：`session-19074bf0-0205-4315-af73-9db57597275a`
- **要解的缺口**：门核 `db46a988` 判「`C3` 是最硬的一条」，`origin_bytes_retrieved = 0`
- **oracle**：本目录 `oracle.md`（**先冻结**，判据 §一~§六；§五.2 为执行后追加的实测）
- **先行结论**：**`BLOCKED-PARTIAL`** —— **字节层已补齐（2/2 目标、62,953 B、四件 provenance 齐）**，但 **产品仓落点（§二十七 #2 的 filing-fetch 同流落点）因本工位会话无写权限未达成**，且**等级判定与 BLOCKED 解除不在本工位**。
- **`level_claimed = null`** · **`releases_nothing = true`**

---

## 一、三步执行

### 步 1 · 门 0（纪律 16/17：能力门前置，**自己探，不采信父探针**）

原始输出见 `gate0_probe_raw.txt` 与 `oracle.md §5.2.1`（payload `GATE0-PROBE-a20260926-01`，24 B，PID **16680**）。

| 探针 | 目录 | 写 | 回读 | 删除 | 判定 |
|---|---|---|---|---|---|
| **P0** | 本工位产出目录 `.planning/.../OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01` | **rc=0** | **rc=0** `match=True (len=24)` | **rc=0** `residual=False` | **PASS** |
| **P1** | `C:\Users\郑曾波\Projects\company-wiki\companies` | **ERR `Access to the path '..._gate0_probe_16680_2.tmp' is denied.`** | NA | NA | **DENIED** |
| **P2** | `...\company-wiki\src\company_wiki\source_catalog` | **ERR `...'..._gate0_probe_16680_3.tmp' is denied.`** | NA | NA | **DENIED** |
| **P3** | `...\dayu-agent\dayu-agent\dayu\fins\downloaders` | **ERR `...'..._gate0_probe_16680_4.tmp' is denied.`** | NA | NA | **DENIED** |

⇒ **`gate0_writability_passed = false`**（对产品仓目标目录）；**本工位对 company-wiki / dayu-agent 产品仓「无写权限」**。

**分支处置（纪律 16 硬前置）**：**产品仓落点分支停手** ——
- **未**运行 `filing-fetch --allow-download`；
- **未**尝试 `git apply` / `>` 重定向覆盖 / 删除-重写 / `checkout`-`restore` **任何**替代写法；
- 三处 probe 文件在**创建前**即被拒 ⇒ **产品仓 0 字节残留**、**既有文件 0 改动**。

**与父探针的关系（父已自认）**：父 2026-09-26 14:0x 的「三处全 OK」是**带 `danger-full-access` 提权**跑的；本工位审批禁用、权限固定、无提权 ⇒ **两份探针都为真（父提权可写 / 子工位不可写）**，这恰是纪律 16/17 要求自探的全部理由。**这四条探针输出是「父探针带提权 ≠ 子工位能力」的第一份一手证据。**

### 步 2 · 取证（回源确认 URL → 下载型取回 → provenance）

**S1 回源确认（逐字，不采信派单）**：两个 URL 与上一轮 `OPEN3-E1-ORIGIN-BYTES/a20260925-01/handoff.json` 的 `target_documents` **逐字一致**；并用 EDGAR index（`0001193125-26-380280-index.htm`，HTTP 200）独立确认文档身份：`MICROSOFT CORP (Filer)` · `Period of Report 2026-09-02` · `Accepted 2026-09-02 16:30:24` · `Item 7.01: Regulation FD Disclosure` · `Item 9.01` · 文件清单含 `d291965d8k.htm`、`d291965dex991.htm`。

**S2 机制（必须下载型，ACCT `OPEN3-E1-ACCT-RULING` L126）**：

| # | 机制 | 结果 |
|---|---|---|
| A1 | PS5.1 `Invoke-WebRequest` / .NET `HttpClient` | **FAIL**：`基础连接已经关闭: 接收时发生错误`（TLS 握手） |
| A2 | `curl.exe`（schannel） | **FAIL** rc=35：`AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS` |
| A3 | harness `web_fetch`（**文本型，不产响应字节**） | **HTTP 403**「Your Request Originates from an Undeclared Automated Tool」——**不计入 origin 字节** |
| **A4–A7** | **Python `urllib`（声明 UA）＝ 下载型 M2** | **4× HTTP 200，字节落盘** |
| A8 | `http.client` 原始头复取（第 3 次取 8-K） | 200，sha 与 A5 **三次完全一致** |

**UA（实际发出）**：`revenue-forecast-evidence-audit/1.0 (owner-authorized evidence retrieval; contact: audit-ops@example.com)`

**取回结果（`origin_bytes_retrieved = 62,953`，2/2 目标）**：

| 文档 | URL | 取回 UTC | HTTP | 字节 | sha256 |
|---|---|---|---|---|---|
| MSFT 8-K（Item 7.01/9.01） | `https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965d8k.htm` | `2026-09-26T13:29:40Z`→`13:29:41Z` | **200** | **28,665** | `a3d0bbf6411bb2b2db0bc9deee1541ea44639399e26e1f08adf8df3037ab0878` |
| MSFT 8-K Exhibit 99.1（FY27 Segments and Investor Metrics） | `https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm` | `2026-09-26T13:29:41Z`→`13:29:42Z` | **200** | **34,288** | `47a0a4a1d6a335fffab571789aba597eca0637d2650f0f62371afa10e205b987` |

- 落盘：`origin_bytes/…d291965d8k.htm.origin`、`origin_bytes/…d291965dex991.htm.origin`（**写后读回复算 sha 一致**）
- 打包：`origin_bytes.bin`（8-K `[0,28665)` ∥ Ex99.1 `[28665,62953)`），`sha256 = cf84c29048ab314e329758975e101804ba3032f28e2b22d0373f46e3d3c9db1e`

**S3 provenance（`provenance.json`）四件齐**：`url` · `retrieved_utc` · `verbatim_quote`（含原始 ASCII 锚点字节区，如 8-K `[21796,21866]`、Ex99.1 `[3079,3139]`/`[20323,20331]`/`[30770,30794]`）· `sha256` · **`http_status=200`**，另含 `bytes`、`mechanism`、`user_agent`、`document_identity`、`landed_path`、`external_retrieval_not_local=true`、`gate0`、`attempts[]`、`previous_corpus_reverification`。

### 步 3 · 量化登记

| 指标 | 上一轮（`a20260925-01`） | **本工位** |
|---|---|---|
| `origin_bytes_retrieved` | **0** | **62,953**（2/2 目标，均 200） |
| `origin_sha256` | `null` | 8-K `a3d0bbf6411bb2b…` · Ex99.1 `47a0a4a1d6a335ff…` · 打包 `cf84c29048ab314e…` |
| 产品仓落点 | 0（B1 拒写） | **0（B1 仍拒写，本工位门 0 实测 DENIED）** |
| 网络请求 | 0 | 8 次（6 成功 / 2 机制失败 / 1 次 harness 403 计入背景） |

---

## 二、对 `ACCT` 该缺口的满足度（**形态自检，等级权归会计面**）

`I11A-OPEN-ACCT` L66/L153 的 **E1 五要素**，对 **origin 层**逐项：

| # | 要素 | 上一轮会计面判定 | **本工位之后** | 翻正？ |
|---|---|---|---|---|
| ① | 申报**原文**本地归档（origin 响应字节落盘） | **❌** | **✅ 字节层成立**：两份 sec.gov HTTP 响应体原件落 `.planning` 本计划目录 + `origin_bytes.bin` 打包，写后复读 sha 一致 | **是（字节层）** |
| ② | 文件 sha256 | ✅（对转写字节） | **✅ 对 origin 字节复算**（见上表，两次独立复读一致） | 是（对象换为 origin） |
| ③ | 取回 UTC | ✅（四窗口） | **✅** `2026-09-26T13:29:40Z`–`13:29:42Z`（另有身份件 `13:29:40Z`、独立件 `13:30:33Z`、复测 `13:38:59Z`） | 是（origin 侧） |
| ④ | 逐字引文 | ✅ 8/8（对转写载体） | **✅ 在 origin 载体上重跑**（ACCT L163 要求）：**去空白归一化 8/8**；空白敏感 7/8（Q1 差 2 空格） | 是（新载体重跑） |
| ⑤ | 至少一条独立复核路径 | ✅ 带限定（origin 层无样本） | **✅ 限定解除**：EDGAR 完整申报 `.txt`（HTTP 200，2,721,504 B，`d82838ac…`）为**独立 artifact**；剥去边缘注入脚本/SGML 包裹后 **两份 origin 内容与 as-filed 副本逐字节相同** | 是（origin 层有了样本） |

**结论（如实）**：
- **字节缺口已补**：`origin_bytes_retrieved 0 → 62,953`，四件 provenance **齐**（`URL / UTC / 引文 / sha256 / HTTP=200`）。
- **但整体判 `BLOCKED-PARTIAL`，不判满足**，缺项三条（均**不在字节层**）：
  1. **B1 落点未达**：§二十七 #2 授权的落点是 `company-wiki/companies/{entity}/raw/…`（经 filing-fetch 同流），本工位会话门 0 三处 DENIED ⇒ **0 字节落产品仓**（父将用提权会话另行处理）；
  2. **B2 机制未走**：`filing-fetch --allow-download` 未执行（门 0 前置即败），故**没有 filing-fetch 的 immutable provenance sidecar**、**没有产品仓 `git diff HEAD --name-only` 新增路径**（`[]`）；
  3. **C5 内容一致性未裁**：origin 与既有 4 语料在 Q1 上有 **2 处空格差**、并有**边缘注入脚本**差异 —— 是否构成 ACCT C5 的「不一致 ⇒ 4 文件降 E3」**归会计面裁定，本工位不裁**（同理：①是否正式由 ❌→✅、`E1-COMPLETE` 是否成立，归 `OPEN-3-ACCT-R2`）。

---

## 三、红绿变异（判别力）

`mutation_results.json`：**`discrimination_ok = true`**（1 绿 + 6 红全部按 `oracle §四` V1–V10 触发），明细见 `oracle.md §5.2.3`。要点：
- **R1 用的是真·SEC 拦截页**（`web_fetch` 同款 UA → HTTP **403**、4,819 B、`2922be22…`）⇒ 被 V1+V7 拒；
- **R2** 用同申报 index 页冒充目标文档 ⇒ 被 **V6（URL 必须与冻结的两个目标 URL 逐字一致）** 拒 —— **不拿相似文档冒充 origin**；
- **R5** 用「门 0 已 DENIED 却仍落产品仓」⇒ V10 拒 —— 本工位实际路径**从未触发**该红样。

---

## 四、边界自证

1. **写入面 = 本工位产出目录内 12 个文件**（`oracle.md`、`gate0_probe_raw.txt`、`provenance.json`、`mutation_results.json`、`_analysis_output.json`、`origin_bytes.bin`、`origin_bytes/` 6 个取回件、`ruling_e1_bytes.md`、`handoff.json`），**全部在 `.planning/…/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/` 下**。
2. **`.planning` 之外写入 = 0**；**company-wiki 写入 = 0**（三处 probe 创建前即被拒、无残留）；**dayu-agent 写入 = 0**。
3. **`git diff HEAD --name-only`（只读，**未用 `git status`**）**：
   - **revenue-forecast**：`diff_total_lines = 3830`，**非 `.planning` = 0**
   - **company-wiki**：3 个已跟踪文件有改动（`CLAUDE.md`、`README.md`、`src/company_wiki/source_catalog/artifact_dag.py`），**mtime 均为 2026-09-23 13:08:38（早于本工位 3 天，系他人既有改动）** ⇒ **本工位贡献 = 0**
   - **dayu-agent（仓库根 `Projects\dayu-agent\dayu-agent`）**：**0 行**
4. **git 写 = 0**（未 `add/commit/push/checkout`，未用 `git status`）。
5. **未改任何上游载体**：`OPEN3-E1-ACQUISITION`（corpus ×4 + 3 载体）、`OPEN3-E1-ACCT-RULING`、`OPEN3-E1-ORIGIN-BYTES/a20260925-01`、`I11A-*`、`OWNER_DECISIONS.md`、`progress.md`、`task_plan.md` 全部只读；上一轮 4 语料 sha 复测与自报**一致**（`096c7d9d…` / `5927de03…` / `20392f0e…` / `56b0460b…`）。

---

## 五、不授予（本工位**没有**做的事）

- **未解除 `OPEN-3`**（只补字节，等级仍归会计面）
- **未解除 `BLOCKED-NEEDS-ORIGIN-BYTES` / `B1`**（证据交上去了，解除归复审/有权方）
- **未判 E1/E2 等级**（`level_claimed=null`；`BLOCKED-PARTIAL` 是**本卡对自身缺口满足度的形态判**，不是证据等级裁定）
- **未产生 `ACCEPT`**、**未放行任何参数**、**未代签**、**未改任何 `status/state/decision/decision_sha256`**
- **未碰两半区裁定 / 封盘 `I-11-A` / `OPEN6-TOLERANCE-*` / `BLOCKED6C-*` / `OPEN6-H2-*` 任一字节**
- **未做产品代码改动**（§三十 B2 扩闸 / §三十二 晋升均未触碰）
- **未谎报 kind**（§三十一 `current_report → raw/other/` 口径照录，本工位未落产品仓故不涉及）
- **未用 `web_fetch` 文本冒充 origin 字节**（A3 明确记为不计入）
