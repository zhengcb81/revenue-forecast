# OPEN3-E1-ORIGIN-BYTES · origin 响应字节取证报告（a20260925-01）

- **card**：`OPEN3-E1-ORIGIN-BYTES` ｜ **attempt**：`execution_runs/OPEN3-E1-ORIGIN-BYTES/a20260925-01` ｜ **role**：`controlled_forensics`（受控取证工位，MERGE 解锁条件 **C3 第一步**）
- **父代理**：`session-19074bf0-0205-4315-af73-9db57597275a` ｜ **工位会话日（UTC）**：2026-09-25
- **先行结论（fail-closed）**：**`BLOCKED` —— origin 响应字节取回 0 个，`origin_bytes=true` 的证据 0 条。** 两个**互相独立**的阻断：
  - **B1（落点）**：本会话 DSH 文件策略 = `workspace-write`，`company-wiki` 产品仓**全域不可写** ⇒ filing-fetch `--allow-download` 在 `ensure` 阶段即失败（`attempt to write a readonly database`，`downloads=0`）；
  - **B2（机制覆盖）**：即使落点可写，filing-fetch 的 US 路径（dayu 适配器）**对 form 8-K 根本不下载 exhibit** ⇒ `d291965dex991.htm`（Exhibit 99.1）origin 字节**不在该机制覆盖面内**。
- **本工位未判任何等级**：`level_claimed=null`、`releases_nothing=true`、`does_not_claim_I11A_acceptance=true`、`adds_no_new_domain_judgement=true`。

> **授权依据（逐字，`OWNER_DECISIONS.md` §二十七 第 2 行，2026-09-25）**
> 问题列：「**origin 响应字节落点冲突**：`E1` 只差 origin 字节，但 `filing-fetch` 下载落盘点 = **`company-wiki` 产品仓**，而 §二十四 L498 写「取证产物**只落本计划目录**」；且 harness `web_fetch` **只回文本、不产响应字节**」
> owner 选择列：**「落产品仓（与 filing-fetch 同流）（建议）」**
> 执行映射列：「⇒ **本条以 owner 本裁为准，取代 §二十四 L498 在该场景的适用**：允许 origin 字节**经 filing-fetch 既有机制落 `company-wiki/companies/{entity}/raw/…`**，本计划目录**另存镜像与 sha 校验**；仍标 `external_retrieval_not_local` 如实；**等级判定归会计面**；本裁**不解除 `OPEN-3`、不产生 ACCEPT**」
> 执行纪律（§二十七 L563）：「**三票 = 三个许可，不是三个结论**：**不解除 `OPEN-4`/`OPEN-12`/`OPEN-3`/`OPEN-5` 任何 BLOCKED**、**不产生 ACCEPT**、**不改任何 status**、**不授权晋升**。」

> **补齐条件原文（会计面 `OPEN3-E1-ACCT-ruling.md` R1 / C1）**：「把 `d291965d8k.htm` 与 `d291965dex991.htm` 的 **sec.gov HTTP 响应体以文件形式**写进本计划目录（本裁已改为产品仓 + 计划目录镜像），登记 URL + 取回 UTC + 文件 sha256 + 逐字引文 + 复核路径……R1 必须用**下载型**机制」——**本工位只尝试下载型机制（filing-fetch），未使用 harness `web_fetch` 混充 origin 字节。**

---

## 一、五要素自检表（照 `OPEN3-E1-ACQUISITION` 格式；判定权归会计面，本表只报形态）

| # | 要素（ACCT L66/L153 原文） | 上一轮会计面判定 | **本工位之后** | 是否翻正 |
|---|---|---|---|---|
| ① | 申报**原文**本地归档（origin 响应字节落盘） | **❌**（4 语料 = harness `web_fetch` 文本转写，非 origin 字节；SEC 直取 0 成功） | **仍 ❌**：本工位取回 origin 字节 **0 个**，`company-wiki` 侧 **0 字节**、计划目录 `mirror/` **0 字节**（见 §三 B1/B2） | **否（未翻正）** |
| ② | 文件 sha256 | ✅（对 4 个**转写字节**复算一致） | 对 **origin 字节**的 sha256：**无对象可算**（0 字节）；上一轮 4 语料 sha **复测一致、0 字节变更**（§四） | 不变（origin 侧 N/A） |
| ③ | 取回 UTC（窗口式） | ✅（A4/A5/A19/A20 四窗口） | 本工位 origin 取回**未发生**（filing-fetch 两次运行均未发出任何 HTTP，`stage=ensure` 前置失败）⇒ **无 origin 取回窗口可登记** | 不变（origin 侧 N/A） |
| ④ | 逐字引文（8 条，双路径） | ✅ 8/8 | 未改动任何语料；**不得**把既有 8 条引文当作 origin 层已核（会计面 R1 要求"在新载体上重跑同一套字节区校验"） | 不变 |
| ⑤ | 至少一条独立复核路径 | ✅（带限定：独立层=实现/运营方层，**origin 层无样本**） | **维持 ✅（带同一条限定）**：本工位新增**第 3 条尝试路径**（filing-fetch → company-wiki → dayu → SEC EDGAR，与 r.jina.ai / W3C html2txt 无共享代码），但该路径**未产出任何字节** ⇒ origin 层样本仍 = 0，**限定未解除** | 不变（仍带限定） |

**统计**：**① 未翻正（❌→❌）**；**⑤ 未变化（✅ 带限定 → ✅ 带同一条限定）**；②③④ 对 origin 侧无可评对象，对既有转写侧维持原判。
⇒ **E1 补齐条件（`BLOCKED-NEEDS-ORIGIN-BYTES` 的 R1/C1）未满足；`OPEN-3` 证据面维持 BLOCKED（本工位不改任何状态）。**

---

## 二、本工位尝试清单（全部真实读秒，成功失败全记）

| # | 窗口（UTC，2026-09-25） | 机制 | 目标 | 结果 |
|---|---|---|---|---|
| A1 | 22:52:29–22:52:32（首跑）／23:01:26–23:01:29（复跑取证） | `filing-fetch` **只读 reuse**（`python scripts/fetch_filing.py --timeout-seconds 300 --debug`，无 `--allow-download`） | MSFT 8-K `current_report` / `form_type=8-K` / FY2026 | **`not_found`**，`exit=2`，`calls=2`，**`downloads=0`**，`reason=no_existing_source_satisfies_request` → 盘上无任何可复用 8-K（与上一轮 A2 及 IND ruling L142「company-wiki 内 8-K 文件数=0」一致） |
| A2 | 22:52:45–22:53:02 | `filing-fetch` **授权下载**（同上 + `--allow-download --timeout-seconds 600`） | 同上，落 `company-wiki/companies/MICROSOFT CORP/raw/…` | **`status=fatal`**，`exit=2`，`stage=ensure`，`attempts=1`，`calls=3`，**`downloads=0`**；原始错误：`company-wiki ensure exited 1: {"error": "attempt to write a readonly database", "error_type": "fatal", "retryable": false, "status": "failed"}` |
| A3 | ≈22:55–22:58 | **写打开探针**（`File.Open(..., ReadWrite)`，不写任何字节） | `company-wiki/.source_catalog/catalog.db`、`.state/state.db`、`companies/MICROSOFT CORP/raw/financial_reports/annual`、（对照）skills 配置文件、（对照）workspace 内 `SKILL.md` | company-wiki 三处 **`Access denied`**、非 workspace 对照 **`Access denied`**、workspace 对照 **RW_OK** ⇒ **workspace-write 策略：session workspace 之外一律拒写** |
| A4 | 22:55–23:02（本地） | **机制覆盖扫描**（读代码 + 解析盘上 449 个 dayu `meta.json`） | exhibit 是否在 8-K 下载面内 | 见 §三 B2：**6-K 23/23 有 exhibit、8-K 0/449** |

- **本工位发出的网络请求 = 0**（A1/A2 是本地子进程调用，均在 `stage=ensure` 的本地目录写阶段失败，**未产生任何 http_status**；A3/A4 纯本地）。⇒ **`provenance.json` 中 `http_status=null` 而非编造 200/403。**
- **未使用 harness `web_fetch` 取任何 origin 内容**（纪律 #2：不得混用）。
- 上一轮 21 次尝试（含 SEC 直连 403 ×2、raw 代理 522/503、filing-fetch 只读探针）为背景，见 `OPEN3-E1-ACQUISITION/provenance.json`，本工位不重复登记。

---

## 三、两个独立阻断（每个都足以单独判 BLOCKED）

### B1 · 落点阻断：`company-wiki` 在本会话**全域不可写**（沙箱/文件策略，非 SEC 网络问题）

- **直接观测**：A2 的 filing-fetch 输出（逐字）——
  `{"schema_version":"1.1","status":"fatal","error":"company-wiki ensure exited 1: {\"error\": \"attempt to write a readonly database\", \"error_type\": \"fatal\", \"retryable\": false, \"status\": \"failed\"}","error_code":"fatal","retryable":false,"stage":"ensure","attempts":1,"calls":3,"downloads":0}`
- **根因证据（company-wiki 自身文档，非我方推断）**：`src/company_wiki/source_catalog/reader.py` **L3–L7** 逐字：
  > 「`CatalogStore.__init__` on a nonexistent path creates a full writable database — mkdir, `PRAGMA journal_mode=WAL`, DDL, additive migrations, seed and commit — and **on an OS-read-only file it crashes with `attempt to write a readonly database`**.」
  ⇒ 该错误 = **对 OS 层只读路径执行建库/写入**，与「DB 被锁（会报 `catalog_locked`）」「worker 暂停（会报 `worker_paused`）」无关。
- **OS 层独立复现（A3）**：对 `catalog.sqlite3`（49,677,344,768 B）、`.state/state.db`、`companies/…/financial_reports/annual` 目录句柄做读写打开 → **`Access to the path … is denied.`**；同一探针对 session workspace 内文件 → **成功**。非 workspace 的第三方路径（skills 配置）同样被拒 ⇒ 这是**会话级 `workspace-write` 策略**，不是 company-wiki 自身 ACL 特例。
- **会话规则核对**：本会话明示「Approval prompts are disabled… do not request sandbox escalation」，且我是权限固定的子代理 ⇒ **不得、也无法申请更宽文件权限**；按纪律 fail-closed 判 **BLOCKED**。
- **痕迹检查**：对 `company-wiki/.source_catalog` 与 `company-wiki/companies` 枚举 `LastWriteTime >= 2026-09-25T00:00:00` → 命中的 2 个文件时间戳为 **21:00:46Z（早于本工位首跑 22:52Z）**；本工位两次 filing-fetch 运行在 company-wiki 内**新增/修改 = 0**（失败发生在写入之前，无残留）。

### B2 · 机制阻断：filing-fetch（dayu US 适配器）**不下载 8-K 的 exhibit** ⇒ Exhibit 99.1 origin 字节机制上取不到

| 层 | 证据（逐字/实测） |
|---|---|
| dayu 远端文件清单 | `dayu/fins/downloaders/sec_downloader.py` **L1105** `filenames: list[str] = [primary_document]`；**L1112 / L1124** `if include_exhibits and form_type == "6-K":`（L1094 文档串：`include_exhibits: 是否包含 exhibit 文件（6-K）。`）⇒ **8-K 的远端清单 = 主文档 + XBRL，永不含 exhibit** |
| company-wiki 适配器 | `source_catalog/dayu_cli_adapter.py` **L389** `file_entry = self._us_primary_entry(value)`；**L474–L490** `_us_primary_entry` 只按 `meta.primary_document` 取唯一条目；**L245–L298** `fetch()` 只把这一个资产 sha256 校验后复制到 staging ⇒ **一个 filing 只产出一个 candidate = primary document** |
| 盘上实测（449 个 meta.json） | 含 exhibit 文件名者 **23 个，form_type 全部 = `6-K`**；**8-K = 0 例**（含 MSFT 全部历史 8-K：`fil_0000950170-25-061032`、`fil_0001193125-25-154103`、`fil_0001193125-26-258667` 等 `files[]` 仅 primary + XBRL）⇒ 与代码闸门完全一致 |
| 路由穷举 | `form_type=6-K` 请求会被 `_forms_for_request`+候选表单闸门过滤掉（目标 filing 的 `form_type=8-K` ≠ `6-K`）；`resolve` 三根（company_raw / dayu_portfolio / directory）只做 reuse，目标 accession `0001193125-26-380280` **不在** dayu portfolio 中（其 2026 accession 最新为 `-26-258667`，2026-06-05）；其余下载型机制在 filing-fetch 内**不存在** |
| ⇒ 结论 | **`d291965dex991.htm` 的 origin 字节在 filing-fetch 既有机制内无可达路径**；这一条**不因沙箱解封而消失**，需产品侧改动（dayu exhibit 闸门扩展到 8-K，或新增 exhibit 级取证通道）+ 相应授权 |

### B3 · 附带的落点形态提示（解封后必须先知道）

`source_catalog/canonical_writer.py` **L90–L101** `_destination_subdirectory`：只有 `annual_report / semi_annual_report / quarterly_report → financial_reports/*`；**其余 kind → `Path("other")`**。8-K 的诚实 kind（`current_report`，与 dayu `service_helpers.py` L117 `"8-K": "current_report"` 同源；或 `regulatory_filing`）会落 `companies/MICROSOFT CORP/raw/other/`，**不是** `raw/financial_reports/{kind}/`；若要落 `financial_reports/quarterly/` 就必须把它谎报为 `quarterly_report` —— **本工位拒绝该做法（元数据造假）**。此形态差异须由 owner/父在解封前确认（仍属 `raw/…`，与 §二十七 #2 的字面一致）。

---

## 四、与上一轮 4 个语料的字节关系（逐 sha，本工位实测复算）

| # | 上一轮语料（`OPEN3-E1-ACQUISITION/a20260924-01/corpus/`） | 字节 | sha256（本工位复测） | 与上一轮自报 | **与 origin 字节的关系** |
|---|---|---|---|---|---|
| 1 | `MSFT_8K_2026-09-02_Item7.01.md` | 3,789 | `096c7d9df55ab46a0ccef21b3ac528b7e59483a91e1b6b32277808bcae801ad1` | ✅ 一致 | **不可比**（本工位 origin 字节 = 0，无对照对象） |
| 2 | `MSFT_8K_2026-09-02_Item7.01.verify-w3c-html2txt.txt` | 5,183 | `5927de0367d1097a6bbb1f59c669a3461eacce43c8115874c5e0a497f7689f1c` | ✅ 一致 | **不可比** |
| 3 | `MSFT_8K_2026-09-02_Exhibit99-1.md` | 27,586 | `20392f0e110568fa4338a1167da3756627b77e606eec85ae113aeebf40373f58` | ✅ 一致 | **不可比** |
| 4 | `MSFT_8K_2026-09-02_Exhibit99-1.verify-w3c-html2txt.txt` | 28,536 | `56b0460b4e635b590c1870153a65adc996d134fd12e2cd6c2670c51ab170956d` | ✅ 一致 | **不可比** |

- **4/4 sha 与上一轮 ACCT ruling §② 实测完全一致、字节数一致** ⇒ 两轮之间**语料 0 字节变更**（上一轮被审对象未被本工位触碰）。
- **同/不同判定**：因 origin 字节为 0，**本轮无法建立任何「同/不同」关系**；一旦 origin 落盘，必须逐文件做「origin(HTML) vs 转写(md/txt)」的内容级比对（会计面 C5：**若 origin 与现有语料不一致 ⇒ 4 文件降 E3、8 条引文作废**）——该比对**本工位未做、也不能做**（无 origin）。
- 形态提示（非实测）：origin 为 SEC 的 HTML 响应体，与 markdown/纯文本转写**必然不同字节**；sha 相同反而是异常信号。

---

## 五、落点判定（`handoff.landing_target_decision` 的正文版）

| 目标物 | 授权落点（§二十七 #2） | 本工位实际落点 | 判定 |
|---|---|---|---|
| **origin 响应字节本体** | `company-wiki/companies/{entity}/raw/…`，经 filing-fetch 既有机制 + 其 immutable provenance sidecar | **0 字节（未产生）** | **`BLOCKED`**：机制调用已按授权发出（A2），落点在 `ensure` 建库/写入阶段被会话文件策略拒绝（B1）；**未**改用任何其他落点、**未**用 web_fetch 文本冒充 origin |
| 镜像 + sha 校验 | 本计划目录 `mirror/` | `mirror/manifest.json`（**0 条目**，如实声明无镜像对象） | **如实空置**，不造绿样 |
| 取证报告/取证元数据/交接 | 本计划目录 | `provenance.json`、`acquisition_report.md`、`handoff.json`、`mechanism_scan.json`、`attempt_A1~A3` | ✅ 全部落 `.planning` 内 |
| 其他任何产物 | **不得落产品仓** | 无 | ✅ company-wiki 新增/修改 = 0；revenue-forecast 非 `.planning` 写入 = 0 |

**为什么不做「把 filing-fetch 指向计划目录内的隔离 wiki 根」这类变通**：派单纪律 #3 ——「若 filing-fetch 的某方法会写出 filing-fetch 允许之外的路径 ⇒ 不执行该方法，报阻断」；§二十七 #2 授权的落点是**真实 company-wiki 产品仓**，自造影子 wiki 根既不在授权落点内，也会产生"看似已入产品仓"的误导样本（纪律 #4 不造绿样）。

---

## 六、边界自证（可核）

1. **写入面 = 恰 7 个文件**，全部在 `execution_runs/OPEN3-E1-ORIGIN-BYTES/a20260925-01/` 下：`attempt_A1_resolve_probe.txt`、`attempt_A2_download.txt`、`attempt_A3_write_scope_probe.txt`、`mechanism_scan.json`、`mirror/manifest.json`、`provenance.json`、`acquisition_report.md`（+ `handoff.json` 自身，不入自报 sha）。
2. **`.planning` 之外的写入 = 0**；**company-wiki 写入 = 0**（含失败尝试的残留检查，见 B1）；**git 写操作 = 0**；**未执行 `git status`**（纪律 #6），收尾只跑只读 `git -c core.quotepath=false diff HEAD --name-only`。
3. **网络 = 0**：本工位 0 次 HTTP 请求；`provenance.json` 无任何 `origin_bytes=true` 条目，也**不登记任何伪造 http_status**。
4. **未改任何上游字节**：`OPEN3-E1-ACQUISITION`（corpus×4 + 3 载体）、`OPEN3-E1-ACCT-RULING`、`I11A-OPEN-ACCT`、`I11A-OPEN-MERGE`、`OWNER_DECISIONS.md` 全部只读。
5. **未做（明确点名）**：未判 E1/E2/BLOCKED-PARTIAL 等级；未解除 `OPEN-3`、未关闭 `BLOCKED-3a/3b`、`BLOCKED-4/5`；未产生 ACCEPT；未改任何 `status/state/decision/decision_sha256`；未写 MSFT 参数；未越出 §二十七 #2 的落点范围；未用 harness `web_fetch` 混充 origin。
