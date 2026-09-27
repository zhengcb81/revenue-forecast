# OPEN-12 · **cutoff 后交易所公告取得方式** · 受控取证报告

- 工位：`OPEN12-CUTOFF-ANNOUNCE-ACQUISITION` · attempt `a20260925-01`
- 授权：`OWNER_DECISIONS.md` **§二十七 第 1 行**（2026-09-25，owner 原话 **「两条都授权（建议）」**）⇒ **G3 = `OPEN-12` 受控取证授权**
- 配套：§二十四 L498（取证产物只落本计划目录）—— §二十七 #2 对它的定向取代**是否适用本工位**，判定见 **§7 落点判定**
- 写入面：`execution_runs/OPEN12-CUTOFF-ANNOUNCE-ACQUISITION/a20260925-01/`（`corpus/` 3 件 + 本文件 + `provenance.json` + `handoff.json`），**产品仓写入 = 0**
- 取回窗口（会话）：2026-09-25T21:59Z → 22:11Z；尝试 **18** 次（`web_fetch` 17 + `web_search` 1）

> **本工位只到取证层。** 规则/审核层归**交易所公告来源审核**；定级/放行层归**会计面**。
> `releases_nothing = true` · `does_not_claim_I11A_acceptance = true` · `adds_no_new_domain_judgement = true` · `level_claimed = null`

---

## 0. 三层分界（先读，禁止混同）

| 层 | 问题 | 谁的裁权 | 本工位 |
|---|---|---|---|
| **① 取证层** | cutoff 后交易所公告这一**来源是否存在、可得、字节可核** | 本工位（受控取证） | **只做这一层，已交付** |
| **② 规则/审核层** | 该来源**可否被采信/如何审核**（来源分级、`regulator_primary_disclosure` 归属、审核回执） | 交易所公告来源审核 | **不裁** |
| **③ 定级/放行层** | 证据**等级**（E1/E2…）与参数/命题是否放行 | 会计面 | **不裁、不评级**（`level_claimed = null`） |

`merge_ruling.md` L10：「**不新增任何专业判断**、**不解除任何 BLOCKED**、**不代签**、**不改任何 status**」——本工位沿用同一边界。

---

## 1. 授权原文（逐字）

`OWNER_DECISIONS.md` **L552–L565**（§二十七，读取时文件 76,005 B / `fe26a2db…`）：

> | **1** | **G2=`OPEN-4`、G3=`OPEN-12`** 至今未授权未派（合并裁列的授权缺口，**G1 已由 `OPEN-11` 补上**） | **「两条都授权（建议）」** | 派 `OPEN-4`（wiki 来源审核）与 `OPEN-12`（cutoff 后交易所公告取得方式）**受控取证**；**产物只落本计划目录**（同 §二十四 #3 形态）；**不解除任何 BLOCKED、不产生 ACCEPT**；两站交付后**仍须过 MERGE 七条** |

执行纪律逐字（L563–L564）：

> - **三票 = 三个许可，不是三个结论**：**不解除 `OPEN-4`/`OPEN-12`/`OPEN-3`/`OPEN-5` 任何 BLOCKED**、**不产生 ACCEPT**、**不改任何 status**、**不授权晋升**。
> - **#2 是对 §二十四 L498 的定向取代**，适用范围**仅限「origin 响应字节经 filing-fetch 取回」这一场景**；**其余取证产物仍只落本计划目录**。

---

## 2. 回源发现：`OPEN-12` 的**所指不一致**（登记，不裁）

| 出处 | 逐字所指 | 行号 |
|---|---|---|
| 卡载体 `I-11-A/decision.md` | 「是否需要为“**校验器完备性**”另立一张专业卡（统计/工程 reviewer）」→ 归 **PLAN owner / 统计 reviewer**，影响 `I-11-C 是否复用同一校验器` | **L408** |
| 合并裁 `I11A-OPEN-MERGE/merge_ruling.md` **G3 行** | 同卡文表述（「本轮未派；`OWNER_DECISIONS.md` 内**未见**针对 I-11-A OPEN-12 的裁定行」） | **L362** |
| owner 裁定 `OWNER_DECISIONS.md` §二十七 #1 | 「`OPEN-12`（**cutoff 后交易所公告取得方式**）**受控取证**」 | **L558** |

**处置（fail-closed）**：三处对 `OPEN-12` 所指不一致。本工位按 **owner 裁定行的所指**执行取证（授权以 owner 原话为准），**同时登记该不一致**；**不裁**「`OPEN-12` 究竟指哪一个」，**不改**任何 status。⇒ 即使取证成功，也**不得**被读成「卡文 L408 的校验器问题已处理」。

---

## 3. cutoff 时间窗定义 与 公告覆盖关系

### 3.1 时间窗（逐字回源）

| 要素 | 值 | 出处（逐字） |
|---|---|---|
| **cutoff / `as_of`** | **2026-09-18** | `audit_review/2026-09-18_real_company_skill_audit/requests/zijin_2025.json` **L4** `"as_of_date": "2026-09-18"`（`msft_2026.json` L4、`xiaomi_2025.json` L4 同值；`independent/acquisition_aftercheck.json` L70/L164 同值） |
| 停止规则 | 「**来源晚于as_of或原文无法核查→STOP_EVIDENCE。**」 | `execution_v2/card_I-11-A.md` **L21** |
| 捕获不变量 | 「**capture验证要求published<=captured<=as_of。**9/19恢复研究、信息集仍9/18时，不能把实际获取时间伪填前一天。」 | `AUDIT_REPORT.md` **L76** |
| **cutoff 后窗口**（本工位口径） | **(2026-09-18 00:00, 2026-09-25T22:11Z]** | 本工位定义：as_of 之后至取回时点 |
| 时区 | HKEX `DATE_TIME` = 香港时间 UTC+8；eastmoney `notice_date`/`display_time` = 北京时间 UTC+8；SEC `Filing Date` 无时区 → 跨源只按**日期**比较 | 本工位注记 |

### 3.2 时间窗 × 公告覆盖关系（实测）

| 通道 | 一级/三级 | 窗口内返回 | 已载入（不重复采样） | 覆盖判定 |
|---|---|---|---|---|
| **HKEX 披露易**（`titleSearchServlet.do`，全类别 09-18→09-25） | **一级（交易所）** | `recordCnt = 4,920` | 100 条（25/09 19:17 → 25/09 22:55） | ✅ **窗口有覆盖、可得**；❌ 未枚举全窗口（100/4,920） |
| **HKEX**（同接口，09-18→09-20 全类别） | **一级** | `recordCnt = 922` | 100 条（18/09 21:52 → 20/09 19:58） | ✅ **cutoff 当日起即有公告**（窗口首端覆盖已证） |
| **HKEX**（同接口，09-18→09-25，`t1code=40000` 财务报告类） | **一级** | `recordCnt = 748` | 100 条（24/09 18:51 → 25/09 21:24） | ✅ 含**紫金矿业 02899「2026 Interim Report」25/09/2026 12:01** ⇒ **被审计主体的 cutoff 后公告实证存在** |
| **HKEX 公告正文**（`.htm` 文档级） | **一级** | HTTP 200 | 正文渲染文本（**未落盘**） | ✅ 文档级可得；❌ 该件 sha256 缺 |
| **上交所** `query.sse.com.cn` | 一级 | HTTP 200 但 `success:"false"` `系统繁忙...` | — | ❌ **不可得**（反爬/Referer） |
| **巨潮** `hisAnnouncement/query` | 一级 | HTTP **500**（仅接受 POST） | — | ❌ **不可得**（只读 GET 方法） |
| **巨潮** `fulltextSearch` | 一级 | HTTP 200，SPA 模板外壳（`{{ announcementText }}`） | — | ❌ 无数据 |
| **东方财富** 601899 公告 API | **三级**（`external_retrieval_not_local`） | 最新 `notice_date = 2026-09-17`（**cutoff 前**） | 全量 50 条已读 | ⚠️ 该三级 feed 窗口内 0 条；**不能**据此断言交易所无公告（覆盖未证） |
| **SEC** `data.sec.gov` / `www.sec.gov` | 一级 | **HTTP 403 × 2**（`Undeclared Automated Tool`） | — | ❌ **origin 不可得** |
| **r.jina.ai → SEC browse-edgar** | **三级代理**（`external_retrieval_not_local`） | HTTP 200，MSFT 8-K 10 条 | 最新 `Filing Date = 2026-09-02`（cutoff 前），列表内无 ≥2026-09-19 | ⚠️ 仅 `type=8-K&count=10` 的三级可见面；**不作 origin 级结论** |
| **小米 01810 定向查询** | — | `prefix.do` content-type 不受支持（2 次）；eastmoney HK 两次空列表 | 已载入 300 条 HKEX 记录中 `XIAOMI`/`01810` **0 命中** | ❌ **窗口覆盖未证**（0/300 抽样 ≠ 不存在；fail-closed 记未证） |

**一句话**：**来源存在性 = 已证（HKEX 一级，含被审计主体紫金 H 股 cutoff 后公告）**；**可得性 = 部分已证（HKEX 一级 GET 成功；A 股一级与 SEC origin 均不可得）**；**字节可核 = 未证（见 §5.3）**；**覆盖完整性 = 未证（每页仅 100 条，100/4,920；小米、A 股、SEC 三腿未闭合）**。

---

## 4. 尝试台账（18 次，逐条）

| # | 目标 | 方法 | HTTP | 结果 | 三级？ | 落盘 |
|---|---|---|---|---|---|---|
| 01 | `data.sec.gov/submissions/CIK0000789019.json` | web_fetch | **403** | 拒（Undeclared Automated Tool） | 否 | — |
| 02 | 巨潮 `fulltextSearch` | web_fetch | 200 | SPA 外壳，无数据 | 否 | — |
| 03 | `web_search` ×3 查询 | web_search | — | **工具端点故障** | 否 | — |
| 04 | 东方财富 601899 公告 API | web_fetch | 200 | 有数据，最新 2026-09-17（cutoff 前） | **是** | — |
| 05 | hkexnews `prefix.do`（callback） | web_fetch | — | content-type 不受支持 | 否 | — |
| **06** | **HKEX 窗口查询（财务类 09-18→09-25）** | web_fetch | **200** | **748 条，含紫金 02899 cutoff 后公告** | 否 | ✅ `corpus/ext-01…` 55,471 B |
| 07 | `www.sec.gov/cgi-bin/browse-edgar` | web_fetch | **403** | 拒 | 否 | — |
| **08** | **HKEX 窗口查询（全类别 09-18→09-20）** | web_fetch | **200** | **922 条，覆盖 cutoff 当日** | 否 | ✅ `corpus/ext-02…` 60,665 B |
| 09 | r.jina.ai → SEC browse-edgar | web_fetch | — | 超时（30s） | **是** | — |
| 10 | 东方财富 HK 01810 | web_fetch | 200 | `total_hits: 0`（覆盖未证） | **是** | — |
| 11 | `sec.report/CIK/0000789019` | web_fetch | — | fetch failed | **是** | — |
| 12 | 东方财富 HK 1810 | web_fetch | 200 | `total_hits: 0`（覆盖未证） | **是** | — |
| 13 | r.jina.ai → SEC browse-edgar（重试） | web_fetch | **200** | MSFT 8-K 10 条，最新 2026-09-02 | **是** | — |
| 14 | hkexnews `prefix.do`（无 callback） | web_fetch | — | content-type 仍不受支持 | 否 | — |
| 15 | 上交所 `queryCompanyBulletinNew` | web_fetch | 200 | 业务层拒绝 `系统繁忙...` | 否 | — |
| **16** | **HKEX 窗口查询（全类别 09-18→09-25）** | web_fetch | **200** | **4,920 条** | 否 | ✅ `corpus/ext-03…` 57,308 B |
| 17 | HKEX 公告正文 `.htm`（20/09 19:38 件） | web_fetch | **200** | 文档级正文可取（未落盘） | 否 | — |
| 18 | 巨潮 `hisAnnouncement/query` | web_fetch | **500** | 仅 POST，GET 不可 | 否 | — |

**计数**：HTTP 200 = 10 · 403 = 2 · 500 = 1 · 工具级失败 = 5 · **可用数据 = 6** · **已落盘 = 3** · **经第三方 = 6 次（att-04/09/10/11/12/13）**。

---

## 5. 取证层三问（`OPEN-12` 的阻断值实测）

### 5.1 来源**是否存在**？ ⇒ **已证 = YES（一级来源）**

- HKEX 披露易在 (2026-09-18, 2026-09-25] 返回 **4,920** 条公告（全类别），cutoff **当日起**即有条目（`18/09/2026 21:52` 起）。
- 其中**被审计主体紫金矿业 H 股（02899）**：`"STOCK_NAME":"ZIJIN MINING","TITLE":"2026 Interim Report","DATE_TIME":"25/09/2026 12:01","STOCK_CODE":"02899","FILE_LINK":"/listedco/listconews/sehk/2026/0925/2026092500161.pdf"`（`corpus/ext-01…txt` **L5，字节偏移 39,526**）⇒ **cutoff 后交易所公告确实存在**。

### 5.2 来源**是否可得**？ ⇒ **部分已证（按通道分列，fail-closed）**

| 通道 | 结论 |
|---|---|
| HKEX（一级，GET） | ✅ **可得**（3 次 200 + 1 次文档级 200） |
| 上交所（一级，GET） | ❌ **不可得**（业务层拒绝） |
| 巨潮（一级，GET） | ❌ **不可得**（POST-only ⇒ 500；全文本搜索为 SPA 外壳） |
| SEC（一级，GET） | ❌ **不可得**（403 × 2，全域） |
| 小米（HKEX 定向） | ❌ **不可得**（`stockId` 映射接口 JSONP，工具不支持；其余路子覆盖未证） |
| 三级/代理（东方财富、r.jina.ai） | ⚠️ 可得但**不得冒充一级**；均标 `external_retrieval_not_local` |

### 5.3 字节**是否可核**？ ⇒ **未证（这是本次取证的硬阻断）**

1. **origin 响应字节 0 字节**：harness `web_fetch` **只回解码/渲染文本，不产 origin 响应字节**（与 §二十七 #2 提问背景「harness `web_fetch` 只回文本、不产响应字节」逐字一致）。⇒ 三个 `corpus/` 文件是 **harness spill 的 formatted result**（`byte_fidelity = harness_spill_of_formatted_result`），其 `sha256` 只覆盖**实际保存的这 55,471 / 60,665 / 57,308 B**，**不等于 origin 字节哈希**。
2. **原文档字节 0 字节**：窗口内公告正文（含紫金 02899 的 **23 MB PDF**）**未下载**（体积超出受控取证合理范围，未尝试）；唯一文档级尝试（att-17，`.htm`）**未落盘** ⇒ 该件 `sha256 = null`。
3. **3 个已存文件均已重算 sha256**（见 §9 清单），**`provenance.json` 中每条外部条目都有 `url / retrieved_utc / http_status / sha256(或 null+理由) / bytes / verbatim_quote / retrieval_method`，第三方全部显式标注。**
4. ⇒ **“字节可核”在 origin 级为 BLOCKED**；要拿 origin 字节，唯一可行机制是 `filing-fetch`（进入 §二十七 #2 场景）——**本工位未走该路径**（理由见 §7）。

---

## 6. C1–C8 逐条（检验面取自 `T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` §5，L163–L176）

> **前置声明（必须随表传播）**：C1–C8 是 TIER-2 模拟裁定对 **`detected_and_ignored` 落盘**设的条件（owner §十九 已终确），**其字面对象不是交易所公告**。本工位按任务要求逐条给出**在取证层能证与不能证的部分**，并标明每条**归属哪一层**；**不代裁、不改判、不预判验收**（对齐 T2 ruling §7.2「不自行改判」纪律）。

| # | 条件（逐字摘要，出处 §5） | 归属层 | **本工位状态** | 阻断在哪 / 本工位贡献的取证输入 |
|---|---|---|---|---|
| **C1** | **事实/处置分离落地**：扫描器只产事实；`detected_and_ignored` 只能经授权写入口铸造（判据=产品代码审查 + 负例红绿） | 规则/实现层 | **未证**（`NOT_EVIDENCED_AT_ACQUISITION_LAYER`） | 需产品字节审查；本工位**未读产品源、未跑负例**（无写入面、非本层） |
| **C2** | **授权元组必填**（`ignore_reason`+`ignore_authorizer`+`authorized_at`+命中快照+**`source_sha256 × policy_hash` 双绑定**；变异臂逐一删字段⇒红） | 规则/实现层 | **未证**；**但取证层给出反向硬事实** | **C2 所需的 `source_sha256`（对 origin 字节）当前不可算** —— 见 §5.3：origin 字节 0 件。⇒ 任何要求 `source_sha256` 绑定的落地，在本来源上**先卡在取证层**。这是本工位唯一与 C1–C8 有实质交集的输入 |
| **C3** | **身份落地前零行**：签名链落地前不得出现产品语义 `detected_and_ignored` 行 | 规则/实现层 | **未证** | 需 grep 产品树/卡载体；本工位未做（非本层） |
| **C4** | **下游可见**：`I-05-B` 消费 / `I-06-B` 恢复可见且标记，禁过滤（契约负例 + 变异臂） | 规则/实现层 | **未证** | 需接口成形 + 负例测试；本工位未做 |
| **C5** | **无旁路**：不存在 warn-only / 降级 / env bypass（设开关后 fail-closed 行为字节不变） | 规则/实现层 | **未证** | 需代码审查 + 负例；本工位未做 |
| **C6** | **新鲜度不可由调用方放宽**：TTL 上限由 `policy_hash` 绑定；调用方 `now`/`ttl` 只能收紧 | 规则/实现层 | **未证**；**取证层注记** | 本工位 18 次尝试中 **15 次只有 session-window 时间**（工具不提供逐请求 `retrieved_utc`）⇒ 就“新鲜度可核”而言，本工位自身**也是弱时间戳面**（照实登记，不伪造秒值） |
| **C7** | **术语消歧**：`cache_state="ignored"` vs `detected_and_ignored` 契约层消歧，两种语义各一负例 | 规则/契约层 | **未证** | 需契约文本与冻结测试；本工位未做 |
| **C8** | **登记落地**：裁定经 owner 终确后由**编排层**转录登记到卡载体并在 `RESPONSES.md` 登一行，**不改一字裁决内容** | 编排/登记层 | **未证**（本工位**不代登记**） | 本工位只出本目录载体；卡载体、`RESPONSES.md`、任何 `status` **一字未动** |

**C1–C8 汇总**：**已证 0 / 未证 8**（其中 C1–C7 归规则与实现层、C8 归编排登记层，**均不属本工位裁权**）；**本工位在取证层可贡献且已贡献的唯一交集 = C2 的 `source_sha256` 前置：origin 字节不可得 ⇒ 该绑定当前算不出来**。

---

## 7. 落点判定（`landing_target_decision`）

**判定：本工位【不】属于「origin 字节经 filing-fetch」场景 ⇒ 取证产物只落本计划目录。**

判定理由（逐条）：

1. **授权行自带落点**：§二十七 #1 的执行映射逐字写「**产物只落本计划目录**（同 §二十四 #3 形态）」——本工位授权行本身已定落点。
2. **§二十七 #2 的适用范围逐字为**「仅限「**origin 响应字节经 filing-fetch 取回**」这一场景」；**本工位全程只用 `web_fetch` 只读 GET，`filing_fetch_used = false`** ⇒ 不落入该场景。
3. **客观上也未取得 origin 字节**（§5.3）⇒ #2 所讨论的「origin 响应字节」在本工位**根本不存在**，无从进入其落点规则。
4. **§二十四 L498 对本工位完整适用**，故 `corpus/`、`provenance.json`、`acquisition_report.md`、`handoff.json` **全部落在** `execution_runs/OPEN12-CUTOFF-ANNOUNCE-ACQUISITION/a20260925-01/`，**产品仓写入 = 0**。
5. **前瞻（留给父/owner，不代裁）**：若后续确需 origin 字节（E1 形态），须**另行授权走 `filing-fetch`**，届时才进入 #2 场景（产品仓落 + 本计划目录镜像与 sha 校验 + 仍标 `external_retrieval_not_local`）；**本工位未申请、未执行该路径**。

---

## 8. 边界（**我没做什么**）

1. **没解锁 `OPEN-12`**：本交付只回答“来源是否存在/可得/字节可核”，**不产生解锁**；`OPEN-12` 的规则面问题（卡文 L408 所指）与本行所指的不一致也**未裁**。
2. **没改任何 status**：`I-11-A` 的 `handoff.json` / `hypotheses.json` / `decision.md` / 卡载体 **一字节未动**；`status_fields_changed = 0`。
3. **没产生 ACCEPT、没解除任何 BLOCKED、没代签**：`implementer_signed = false`、`level_claimed = null`（**等级判定归会计面**）。
4. **没做来源审核裁定**：交易所公告来源是否可采信/如何分级 ⇒ **归交易所公告来源审核**（规则/审核层）。
5. **没写产品仓**：`company-wiki/`、`companies/{entity}/raw/`、`filing-fetch` 落点 **零写入**；非 `.planning` 改动 = **0**。
6. **没做 git 写操作**：无 `add/commit/checkout/stash/restore/reset`；**未执行 `git status`**；仅只读 `git -c core.quotepath=false diff HEAD --name-only`。
7. **没造绿色样例**：取不到的（A 股一级、SEC origin、小米定向、origin 字节）一律记 **BLOCKED/未证**，`sha256` 缺就写 `null` + 理由，**不以转录冒充字节**。
8. **没联网绕道**：未使用 `pwsh` 网络、未使用任何未授权抓取方法；`web_search` 仅尝试 1 次（工具故障）。

---

## 9. 产物清单（路径 · 字节 · sha256 前 16）

| 文件 | 字节 | sha256（前 16） | 说明 |
|---|---|---|---|
| `corpus/ext-01_hkexnews_titleSearch_financial_20260918-20260925.txt` | 55,471 | `ede179a0bce20b67` | HKEX 一级，财务类窗口 748 条（载入 100，含紫金 02899 cutoff 后件） |
| `corpus/ext-02_hkexnews_titleSearch_all_20260918-20260920.txt` | 60,665 | `9a101bf92ab4d790` | HKEX 一级，cutoff 当日起 3 日全类别 922 条（载入 100） |
| `corpus/ext-03_hkexnews_titleSearch_all_20260918-20260925.txt` | 57,308 | `70eec1a6109661c4` | HKEX 一级，全窗口全类别 4,920 条（载入 100） |
| `provenance.json` | （写后复算见 `handoff.json.written_files`） | 同上 | 18 条外部条目 + 9 条本地源 |
| `acquisition_report.md` | 同上 | 同上 | 本文件 |
| `handoff.json` | 同上 | `null`（自指不可自证） | 交接 |

> `corpus/` 三件的 `byte_fidelity = harness_spill_of_formatted_result`：**是 harness 落盘的响应呈现文本，不是 origin HTTP 响应字节**；`sha256` 覆盖的是**实际保存的字节**。
