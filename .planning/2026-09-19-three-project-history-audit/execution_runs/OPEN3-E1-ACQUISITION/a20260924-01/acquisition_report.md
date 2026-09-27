# OPEN3-E1-ACQUISITION · 取证报告（a20260924-01）

- **card**：`OPEN3-E1-ACQUISITION` ｜ **role**：`controlled_acquisition`
- **授权依据（逐字）**：`OWNER_DECISIONS.md` **§二十四**（2026-09-24 深夜）第 **3** 行 —— 问题「`OPEN-3` 的 E1 取文（SEC 直连 403、`web_search` 端点故障，行业 reviewer 仅经 `r.jina.ai` 取到文本且**快照 sha=null** ⇒ 会计面判『至多 E2、不得支撑参数』）」→ owner 选择「**授权 filing-fetch 路径**」→ 执行映射「授权用 **filing-fetch / 受控抓取**把 2026-09-02 8-K Item 7.01（含 Exhibit 99.1 若可得）落成**本地语料文件**，记 **URL + 取回 UTC + sha256 + 逐字引文**（E1 五要素），满足后**交会计面定等级**。**取证产物只落本计划目录内**，不写 company-wiki 或其他产品仓」；执行纪律第 504 行「取证（选项 3）的证据等级由会计面定，不由取证方自定」。
- **E1 定义来源**：`I11A-OPEN-ACCT/a20260924-01/ruling.md` **L66/L153**（申报原文本地归档 + URL + 取回 UTC + 文件 sha256 + 逐字引文 + 至少一条独立复核路径）；「缺 4」清单来源：`I11A-OPEN-MERGE/.../merge_ruling.md` **L313**（缺 本地归档 / sha256 / 取回 UTC / 独立复核路径）。

---

## 一、五要素自检表

| # | 要素（会计面原文） | 判定 | 证据 |
|---|---|---|---|
| ① | **原文本地归档**（路径 + 字节数） | ✅（带路径限定 ⚠） | 4 个文件落 `corpus/`：`MSFT_8K_2026-09-02_Item7.01.md` **3,789 B**、`…Item7.01.verify-w3c-html2txt.txt` **5,183 B**、`…Exhibit99-1.md` **27,586 B**、`…Exhibit99-1.verify-w3c-html2txt.txt` **28,536 B**。⚠ **限定**：SEC 原站直取 4 次全部 403，本地字节 = 工位对 harness `web_fetch` 返回文本（第三方代理渲染结果）的逐字转写，**不是 origin HTTP 响应字节** |
| ② | **文件 sha256** | ✅ | `096c7d9df55ab46…`（8-K 主）、`5927de0367d1097a…`（8-K 复核）、`20392f0e110568fa…`（Exhibit 主）、`56b0460b4e635b59…`（Exhibit 复核）；对**已写入字节**计算，复算一致 |
| ③ | **取回 UTC（精确到秒）** | ✅ | 每次尝试均真实读秒两次（发起前/返回后，`yyyy-MM-ddTHH:mm:ssZ`），记为窗口。4 个语料文件取回窗口：A4 `21:20:45Z–21:20:56Z`、A5 `21:21:03Z–21:21:11Z`、A19 `21:26:35Z–21:26:42Z`、A20 `21:26:49Z–21:26:54Z`（2026-09-24）。⚠ 非服务端时间戳，未伪造单点时刻 |
| ④ | **逐字引文**（≥3 段，带字节区） | ✅ | 8 条，全部带 `[start,end)` 字节区，见 §二（Q1–Q3 = 8-K Item 7.01；Q4–Q8 = Exhibit 99.1） |
| ⑤ | **独立复核路径** | ✅（带路径限定 ⚠） | **两条不同运营方/引擎**的路径取回同一原文：path A `r.jina.ai` 渲染代理 ↔ path B **W3C `www.w3.org/services/html2txt`**；8 条引文**逐条**在两份独立文件中各自定位到字节区（去空白子串匹配，因 path B 硬换行重排版）。⚠ **限定**：两条**都是第三方代理**，无一条是原站直取（SEC 直连 403）；若会计面要求「至少一条非代理/原站路径」，本项应判 ❌ |

**统计**：5/5 要素逐项可举证；其中 ①⑤ 各带一条路径级限定。

### 结论：`E1-PARTIAL`

**不自评 `E1-COMPLETE`**，缺的是两条「原生层」：

1. **缺 origin 响应字节**：全部 4 份语料来自第三方文本服务（r.jina.ai / W3C html2txt），本地 sha256 锁定的是**转写字节**，不是 sec.gov 直连返回的 HTML 字节（直连 4 次 403：A1/A3 及原站策略说明见 provenance）。
2. **缺非代理复核路径**：⑤ 的两条路径虽属不同运营方，但同为代理取文；无原站直取样本可作第二层交叉。

> 若会计面把「原文」严格定义为 origin 字节、或把「独立复核路径」要求为至少一条非代理路径 ⇒ 本件相应降为 **E2 / BLOCKED-PARTIAL（缺 ①、⑤ 的原生层）**。
> **等级判定权不在本工位**：按 `OWNER_DECISIONS` §二十四 执行纪律，证据等级由会计面定；本报告只交形态与证据，**未判 E1/E2、未解除 OPEN-3、未改任何 status**。

---

## 二、逐字引文（8 条，全部双路径交叉确认）

| id | 文件 | 行 | 字节区 | 引文（首句/关键段） |
|---|---|---|---|---|
| Q1 | `corpus/MSFT_8K_2026-09-02_Item7.01.md` | L65 | `[2098,2649]` | “On September 2, 2026, Microsoft Corporation (the “Company”) posted presentation materials to its Investor Relations website titled “FY27 Segments and Investor Metrics” announcing a change in reportable segments and investor metrics. **Beginning in fiscal year 2027, the Company will manage its operations under this updated reporting structure and report its financial performance based on two reportable segments: (1)Agents and Infra and (2)Devices and Consumer.** A copy of the presentation materials is furnished as Exhibit 99.1 to this report.” |
| Q2 | 同上 | L67 | `[2651,2888]` | “The exhibit furnished on this report under Regulation FD provides a description of our updated reporting structure and **presents summary financial information and historical data on a basis consistent with the updated reporting structure**.” |
| Q3 | 同上 | L69 | `[3022,3125]` | “…shall not be deemed to be “filed” for purposes of Section 18 of the Securities Exchange Act of 1934…” |
| Q4 | `corpus/MSFT_8K_2026-09-02_Exhibit99-1.md` | L23 | `[1917,2144]` | “**Beginning with FY27, we will transition from our current three reporting segments, Productivity and Business Processes, Intelligent Cloud, and More Personal Computing, to two segments: Agents and Infra and Devices and Consumer.**” |
| Q5 | 同上 | L41 | `[5467,5521]` | “**We will transition to two reporting segments for FY27.** Agents and Infra will include the Microsoft Cloud, productivity and server licensing, and our consulting and support businesses.Devices and Consumer will include our Windows, XBOX, and advertising businesses.” |
| Q6 | 同上 | L89 | `[15807,15855]` | slide 15 重述表：“Revenue $61,672 $64,441 $67,438 $74,576 **$268,127** …” + 同页 “Segment History as Restated”（Agents and Infra FY2026 = $268,127M；Total FY2026 = $331,839M） |
| Q7 | 同上 | L119 | `[24785,24892]` | slide 20：“**Agents and Infra Revenue of $75.15 to $75.75 billion Devices and Consumer Revenue of $14.7 to $15.2 billion**” |
| Q8 | 同上 | L5 | `[155,217]` | “FY27 Segments and Investor Metrics September 2026 Exhibit 99.1” |

双路径确认：每条均在对应 `*.verify-w3c-html2txt.txt` 中命中同一句（去空白后字节区见 `provenance.json` → `verbatim_quotes[].independent_path_b_confirmed`）。

---

## 三、尝试清单（成功与失败全记，21 次）

| 窗口 (2026-09-24 UTC) | 方法 | 目标 | 结果 |
|---|---|---|---|
| 21:18:59–21:19:06 | 直连 sec.gov | 8-K | **403**（拒止页） |
| 21:20:21–21:20:23 | filing-fetch 只读 reuse 探针 | 8-K | `not_found`，exit 2，`downloads=0`（下载路径按 owner 边界未执行） |
| 21:20:24–21:20:32 | 直连 sec.gov | Ex-99.1 | **403** |
| 21:20:45–21:20:56 | r.jina.ai 代理 | 8-K | **200 → 语料 1** |
| 21:21:03–21:21:11 | r.jina.ai 代理 | Ex-99.1 | **200 → 语料 3** |
| 21:21:28–21:21:33 | sec.report 镜像 | 8-K | 失败（fetch failed） |
| 21:21:44–21:21:56 | `web_search` 工具 | 搜索 | **失败**（端点返回不可解析 JSON —— owner 记载的端点故障仍未恢复） |
| 21:22:27–21:22:52 / 21:25:36–21:26:04 | allorigins raw 代理（含重试） | 8-K | 522 ×2 |
| 21:22:58–21:23:03 | codetabs 代理 | 8-K | 503 限流 |
| 21:23:17–21:23:23 | sec.report 重试 | 8-K | 失败 |
| 21:23:33–21:23:38 | DDG html 搜索 | 搜索 | 200（E3 摘要，定位镜像） |
| 21:23:46–21:23:53 | stocktitan | 8-K | 200 但为 AI 摘要+截断，不可用 |
| 21:24:00–21:24:04 | cbonds | 8-K | 403 challenge |
| 21:24:09–21:24:20 | webull | 8-K | 200 但仅标题，不可用 |
| 21:24:51–21:24:55 | DDG `site:microsoft.com` | 第一方 | 200，**0 结果**（无 microsoft.com 第一方副本） |
| 21:25:14–21:25:21 | microlink API | 8-K | 200 但无正文载荷 |
| 21:26:18–21:26:23 | DDG 整句短语检索 | 搜索 | 200，0 结果 |
| 21:26:35–21:26:42 | **W3C html2txt** | 8-K | **200 → 语料 2（独立复核路径）** |
| 21:26:49–21:26:54 | **W3C html2txt** | Ex-99.1 | **200 → 语料 4（独立复核路径）** |
| 21:32:41–21:32:46 | r.jina.ai 再取 | 8-K | 200，逐段核对已存文件（修正封面页 2 处转写） |

**计数**：总 **21** 次 —— 取到文档正文 **5**、搜索结果 **3**、部分/不可用 **3**、失败 **9**、结构化 miss **1**；落盘语料 **4**（来源 A4/A5/A19/A20）。
**是否经第三方代理：是 —— 4 份语料全部经第三方**（r.jina.ai ×2、W3C html2txt ×2）；SEC 原站直取成功次数 = **0**。

---

## 四、边界自证

- 写入面：仅 `execution_runs/OPEN3-E1-ACQUISITION/a20260924-01/`（5 个文件：corpus×4 + provenance.json + acquisition_report.md + handoff.json）。
- **未写** company-wiki / filing-fetch / dayu-agent / 任何产品仓；**未**写 `.planning` 之外任何路径；**未**执行任何 git 写操作。
- **未做**：不判 E1/E2 等级、不改 `I-11-A` 任何字节、不解除 `OPEN-3`、不写任何 status、不写 `companies/{entity}/raw/`。
