# OPEN5-S4-DUAL-PATH-VERIFY · 独立复审报告（reviewer）

| 项 | 值 |
|---|---|
| 卡 / 步 | `OPEN-5` 恢复路径 **S4（双路径复核 + provenance）** |
| 被复审 attempt | `execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/`（实现者交付，自记 `next_station = S4 独立 reviewer 父另派`） |
| 复审角色 | `independent_reviewer_s4`（**与实现者非同一人**；只写复审报告，**不写卡状态、不改任何既有字节**） |
| 复审写入面 | 仅本目录**新建** `reviewer_report.md` + `reviewer_report.sha256`（其余全部既有字节 0 改动，见 §六） |
| 复审执行面 | 生产树**只读**；全部测试/抽取在 `%TEMP%\s4rev\`（`C:\Users\郑曾波\AppData\Local\Temp\dsh-D2yhS9\s4rev\`）**隔离副本**；零 git 写；**未使用 `git status`**；**未联网** |
| 判据回源 | `execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` L165 / L166 / L174–179；`execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` C 表 ④（L234）+ OPEN-11（L360）；被审卡 `oracle.md` + `oracle-addendum-A/B.md` |

---

VERDICT: ACCEPT

> 判级依据：**未发现 P1**。核心产出（`consistency_result = NOT_USABLE`）经我独立复算**成立**，是 fail-closed 的**合格产出、不是缺陷**；与 S3 数字**逐项全等**；三个新增面我各跑一遍**全部复现**；**未发现任何越权**。
> 下列 **P2×3 / P3×2** 均为「报告文本/计数/清单完备性」层面的缺陷，不改变任何结论，可在 S5 消费前由本卡补记（**复审工位不代改**）。

---

## 一、七项独立复核表

| # | 复核项 | 我的方法（独立实现，未复用其脚本） | 实测结果 | 判定 |
|---|---|---|---|---|
| **1** | `consistency_result = NOT_USABLE` 是否成立 | 在 `%TEMP%` 副本内：`pypdfium2 4.30.0` + `PyMuPDF 1.26.7` **各自重抽** origin 10 张抽样页文字层；对 S3 落盘 OCR 文本（先验 sha）用**我自己写的** `digit_tokens`（`\d+(?:[,.]\d+)*` → 纯数字串，≥3 位入集合）独立算 `D_ocr \ D_origin`（≥5 位计矛盾），并**按字节回读原文件核对 byte window** | **`numeric_conflict = 3`（逐条复算全中，见 §二）**；两变体（pdfium / fitz 文字层）**同样 3 处**；M1 头条 `92 / 1 / 1`、A 锚词 `5/5`、可读区覆盖 `112/173/9 = 294 → 0.380952` **与其实测逐位相同**；U2/U3 = `CONSISTENT` 依 `oracle §5.1` 条件复核成立 ⇒ 总值 `NOT_USABLE`（`§5.2` 任一面 `NOT_USABLE`） | **成立** |
| **2** | 与 S3 数字是否真一致 | 读 S3 `_work/path_compare.json` + `reacquisition.json` **原始登记**，与我的独立重算逐项对表（未采信被审卡的 `diffs_vs_s3`） | M1 `92/1/1`、封面 `1`、A `5/5`、B1 `415 页 / 0/5`、M2 逐锚词 fitz/pdfminer 逐页命中集合 `5=5 / 28=28 / 0=0 / 23=23 / 19=19` 与 `5=5 / 13=13 / 0=0 / 13=13 / 9=9`、首现行跨库 `4`、`pdfminer-only = ∅`、B2′ 中 `0/5`、英 `5/5`（词级）+ 5 个英文首现行页码逐条相同（p7/p8/p112/p10/p8）**全部相等** | **全等**（唯一"差"是口径差，见 P3-2） |
| **3** | S3 登记文件 sha 是否真全等 | 对 `raw_measurements.json:s3_artifact_integrity.detail` 的**每一条**重算 sha256；并把 S3 **自己的登记源**（`handoff.json:written_files`、`path_compare.json` 逐件 sha）拿来交叉比对 | **101 条登记全部 `recompute == recorded == actual`，`missing=0`**；其中 **50 条**同时与 S3 自身登记值相等；**但 101 条只覆盖 51 个不同落盘文件**（路径写法重复，见 P2-2） | **全等（计数口径有误，见 P2-2）** |
| **4** | 三个新增面（S3 未做）各跑一遍 | ①数字两路比对：我自己实现（10 页 ×2 文字层变体）；② `attempt08` 的 `pdfminer.six 20260107` 全量 415 页重抽 + 双语锚词 + 首现行跨库；③ `pypdfium2 4.30.0` 全量 415 页扫 B1 | ① `3` 处矛盾（同上）；② `pdfminer 415 页`、中 `0/5`、英 `5/5`、首现行跨库 `5/5`、`pdfminer-only = ∅`（fitz-only 仅 `Xiaomi p242`）；③ `415 页 / 298,151 字符 / 0/5` | **三面全部复现**（② 的 sha 见 P2-1） |
| **5** | G1–G7 分级是否恰当、有无漏报第 8 项 | 逐条读 S3 `provenance.json` 26 条原始条目，按 `oracle §5.4` P1–P5 我自己点算（`missing sha256 / utc / quote / page / note`） | **G2/G3 = hard 恰当**；**G4/G5/G6/G7 = medium/medium/medium/low 恰当**；**G1 = hard 偏重（我判 medium，P3-1）**；**确有漏报的第 8 项：P2 `page`/`whole_document` 缺失于 16/26 条**（见 P2-3） | 分级**基本恰当，漏报 1 项** |
| **6** | `L165` 措辞差是谁的错 | 回源逐字读 `I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` **L165 原文**；再全盘搜「该来源不可用」的派单落盘记录 | L165 原文 = `复核不一致 ⇒ 该来源不可引用，维持不可读处置`（**S4 的三处引用与原文逐字一致**）；「该来源不可用」这一转述**在盘上无任何落盘派单记录**（仅出现在 S4 自己的勘误处） | **不是工位找茬**：按文件原文执行 + 显式登记差异 = 正确纪律；**「父的错」这一归属不可考（unverified），但两者处置同向、无后果差** |
| **7** | 越权检查 | 读 `handoff.json` + `dual_path_verify.json` 全部边界字段，并**到产物正文里找反证**（有无定级/重裁/解卡/放行/下 S5 结论/自任 reviewer 的痕迹） | `level_claimed=null`、`releases_nothing=true`、`open5_released=false`、`placeholder_params_released=false`、`accept_produced=false`、`evidence_grading_done=false`、`industry_rule_regraded=false`、`self_reviewer_claimed=false`、`independent_reviewer="由父另派，本工位不自任"`、`prior_not_readable_preserved=true`、`still_not_readable_disposition=true`；正文仅有「可**提交** S5 定级（本工位不定级）」的**提请语**，无任何 S5 结论；五份计划文件 mtime **全在本卡窗口外** | **未越权（6 项全部未犯）** |

---

## 二、3 处数字冲突 —— 我的复算（逐条坐实）

方法：`%TEMP%\s4rev\rev1_numeric.py`（rc=0）；OCR 文本取 S3 落盘件（sha 先验），origin 文字层由**我**从 `origin.pdf` 副本重抽（`pypdfium2 4.30.0` 与 `PyMuPDF 1.26.7` 双变体）；`byte_window_matches_file` = 我按 `byte_start/byte_end` **回读原文件字节**与 token 比对。

| # | 页 | OCR 侧（我的复算） | 行/字节区 | 字节回读 | origin 同页（我的复算） | 性质 |
|---|---|---|---|---|---|---|
| 1 | **30** | `1,007,26139,166,303` → 归一化 `100726139166303`（15 位） | **line 35 / byte 1482–1501**（与被审卡一致） | **全等 ✓** | `1007261`、`39166303` **均在**（两个独立 token） | 粘连/分隔缺失：两个 origin 值作为子串都在 |
| 2 | **47** | `1,000,001` → `1000001`；原行 `(1,000,001m1` | **line 54 / byte 775–784** | **全等 ✓** | `1000000` **在**；OCR 侧 `1000000` **不在** | 转写差错：末位 0→1 + 行尾 OCR 垃圾 |
| 3 | **47** | `6,000,00` → `600000` | **line 53 / byte 765–773** | **全等 ✓** | `6000000` **在**；OCR 侧 `6000000` **不在** | 转写差错：丢一位 |

- **同页算术自洽性**（我独立验证）：origin p47 = `6,000,000 = 1,000,000 + 5,000,000` ✓；OCR p47 = `600,000 / 1,000,001 / 5,000,000` **不自洽** ⇒ **分歧侧在 OCR**，与被审卡判读一致。
- **全域复算**：10 张抽样页中**只有 p30 / p47 / p355** 存在任何 token 差；p355 差异为 `ocr_only 566/868` vs `origin_only 59990/898`，**均 <5 位不计矛盾**（`origin_only` 方向本就是 `miss`），与被审卡"如实披露"一致；其余 7 页**双向完全一致**。
- **稳健性**：即使把 p30 判为"分隔伪影"不计，**p47 仍有 2 处真值级分歧** ⇒ U1 `NOT_USABLE` **不依赖 p30 这一条**。
- 判据时序无事后挪动：`oracle.md` 23:41:19Z → `addendum-A` 23:43:35Z → `addendum-B` 23:46:09Z → `s4_measure.py` 23:57:48Z → 测量产物 23:58:00–23:58:45Z（**我实测 mtime**）⇒ **判据先于测量冻结**。
- 未做像素级核字（与被审卡同口径）：「哪一侧等于视觉真值」**我同样标未证实**；但「两路读出不同数」这一**事实**已由字节区坐实。

---

## 三、与 S3 数字比对 / 101 抽验 / 三个新面实测数

### 3.1 与 S3（`path_compare.json` + `reacquisition.json`）逐项

| 项 | S3 登记 | 我的独立重算 | 相等 |
|---|---|---|---|
| M1 受检 OCR 行 | 92 | 92 | ✓ |
| M1 逐字命中行 | 1（封面） | 1 | ✓ |
| 封面片段复现 | 1 页 | 1 页 | ✓ |
| A（OCR）锚词 | 5/5（命中页同） | 5/5 | ✓ |
| B1（origin 文字层） | 415 页 / 0/5 | 415 页 / 0/5（**fitz 与 pypdfium2 双库**） | ✓ |
| M2 fitz 逐页命中（小米/收入/年度報告/分部/毛利） | 10 / 28 / 0 / 23 / 19 | 10 / 28 / 0 / 23 / 19 | ✓ |
| M2 pdfminer 逐页命中 | 5 / 13 / 0 / 13 / 9 | 5 / 13 / 0 / 13 / 9 | ✓ |
| M2 首现行跨库 / `pdfminer-only` | 4 / ∅ | 4 / ∅ | ✓ |
| B2′ 中文锚词 | 0/5 | 0/5（fitz 与 pdfminer 双库） | ✓ |
| B2′ 英文锚词（词级） | 5/5 | 5/5（双库）；首现行页 p7/p8/p112/p10/p8 逐条同 | ✓ |

### 3.2 「101 个登记文件」抽验（我全量重算，> 要求的 ≥10 个）

- **101 条登记 → 101/101 重算相等，0 不符、0 缺失**；抽样明细（`cat | file | S4_recorded | 我的 sha | S3 自身登记`）：
  `_work/extract|origin_fitz_full.txt|d628cf53a8cbb898|=|—`、`attempt04_fitz|5d20c2816c0ba2ed|=`、`attempt04_pdfminer|d70d499642477638|=`、`attempt08_fitz|990075a686350d49|=`、`manifest_after|9fde832de1ace101|=`、`manifest_before|a55bb34fc1f56f41|=`、`ocr_text|s3_pathA_p0001.ocr|1d46a6406050670e|=|path_compare 1d46a6406050670e`、`…p0001.origin_textlayer|7f1420f7092e1442|=|7f1420f7092e1442`、`…p0002.ocr|f45ef7e0f9a3519f|=|f45ef7e0f9a3519f`、`…p0002.textlayer|36ad940bc40fb9d2|=|36ad940bc40fb9d2`、`…p0030.ocr|c0ed505265bd17b9|=|c0ed505265bd17b9`、`…p0030.textlayer|220b0dc6bd54a47d|=|220b0dc6bd54a47d`、`…p0043.ocr|24961c529243dbff|=|24961c529243dbff`、`…p0047.ocr|678ac54c3ffd2650|=|678ac54c3ffd2650`。
- **50 条**同时与 **S3 自己的登记值**（`handoff.written_files` / `path_compare` 逐件）相等 ⇒ S3 登记本身可信、本轮未被动过。
- **口径更正（P2-2）**：101 条 = **51 个不同文件**（`ocr_text 20 个 ×3 种路径写法` + `renders 10 个 ×2` + `21 个 ×1` = 101 条登记），**全部 101 条路径都落在 S3 attempt 目录内**。
- **S4 自身 7 个受核输入**我复算：`origin ffd73376…da7c / 4,405,561`、`attempt04 d0975600…9b62b`、`attempt08 b787f029…75ec2`、`path_compare b503e4a8…2159`、`reacquisition f948276a…6430a`、`S3 provenance 3e44f7e9…a3d05`、`S3 oracle 24d4d4e2…e30a9` ⇒ **与 oracle §3 期望值全等**。
- **S4 抽取可复现性（我自己跑）**：我的 fitz 全文抽取（`<<<PAGE n>>>\n` 格式）sha = `d628cf53a8cbb898…` / 709,398 B ⇒ **与其登记文件逐字节全等**。

### 3.3 三个新增面的实测 raw 数

| 面 | 我的实测 | 被审卡自报 | 结论 |
|---|---|---|---|
| ① 数字两路比对 | `numeric_conflict = 3`（p30×1、p47×2）；变体 A/B 一致；覆盖 `112/173/9=294 → 0.380952` | `3`、`0.380952` | **复现 ✓** |
| ② `attempt08` pdfminer 补跑 | 415 页；中 `0/5`（0 命中页）；英 `5/5`（Xiaomi 175 页 / Revenue 14 / Annual Report 2 / Segment 7 / Gross profit 6）；首现行跨库 `5/5`；`pdfminer-only = ∅` | 中 `0/5`、英 `5/5`、首现行 `5/5`、无 pdfminer-only | **复现 ✓**（sha 见 P2-1） |
| ③ B1 第二库 pypdfium2 | 415 页 / **298,151** 字符 / 锚词命中 `0/5` | 415 / 298,151 / 0/5 | **复现 ✓** |
| （附）attempt04 M2 fresh | 词级集合相等、逐页集合与 S3 全等、首现行跨库 `4` | 4/4、集合相同 | **复现 ✓** |

---

## 四、G1–G7 分级判定 + 第 8 项

| id | 实现者判级 | 我的判定 | 理由（我实测） |
|---|---|---|---|
| **G1** `counts` vs `entry_count` | hard | **medium（偏重，P3-1）** | 属实：`counts 4+10+4=18` ≠ `entry_count 26`（我点算 by kind：`authorization 4 / capability_report 1 / acquisition_report 1 / origin_file 1 / substitute_file 2 / ocr_engine_env 1 / ocr_page_render 10 / probe_or_deliverable 6 = 26`）。但 26 条**条目本身可定位、sha/utc 齐**，仅汇总字段不自洽 ⇒ 不影响任何一条证据的可用性 |
| **G2** 外部件无 URL | hard | **hard ✓ 恰当** | 我核 `in-02/in-03` 确无 `url` 字段，只有 `retrieval_method` 站点名；IND C 表 ④ 要求 **URL+取回 UTC+sha256 三件齐**，缺 URL 即不得按 ④ 引用 |
| **G3** `external_retrieval_not_local=false` | hard | **hard ✓ 恰当** | 与 IND C 表 ④ 及 OPEN-11 L360「所有 `EXT-*` 一律标 `external_retrieval_not_local`」直接冲突；S4 自己按 ④ 标 `true` 并登记分歧、两边不回改 —— 处置正确 |
| **G4** origin 无 URL / `utc=n/a_local_bytes` | medium | **medium ✓ 恰当** | 我回源产品仓 sidecar `<pdf>.source.json`：确有 `source_url=https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800527_c.pdf`、`retrieved_at=2026-09-19T04:52:10Z`、`content_sha256=ffd73376…` ⇒ "可回源补齐而未补"属实；且 `oracle §5.4 P4` 明许 `n/a_local_bytes`（须标未证实）⇒ 不升 hard |
| **G5** auth-01..04 无 sha / auth-04 `note=verbatim` | medium | **medium ✓ 恰当** | 我核 4 条确无 `sha256`（缺 sha 的恰是 `auth-01..04 + in-04 = 5` 条）；`auth-04` 的 `quote` 含 **S4/S3 自己的澄清语**（`→ 澄清「两项都要…」`）⇒ **确非逐字**，标注失实；auth-01..03 的 note 带 L227-L228/L164/L179 行号，auth-04 无行号 |
| **G6** 32 个盘上文件未进 provenance | medium | **medium ✓ 恰当（附口径说明，P3-2）** | 我独立遍历：S3 目录 52 个文件，**36 个**不在 `provenance.json` 条目内（其列出的 32 = 36 − `provenance.json`/`handoff.json` 自身 − `manifest_before/after.json`）；列出的 32 项**条目名全部属实**，但**总数未写明被排除的 4 个** |
| **G7** in-04 venv 无 sha/manifest | low | **low ✓ 恰当** | 且被审卡**如实标"本工位未独立复算 ⇒ 未证实"**，未造绿样 |
| **第 8 项（漏报）** | 未登记 | **应补记为 G8（medium）** | `oracle §5.4 P2` 要求每条带 `page`（或明确 `whole_document`）：我点算 **16/26 条缺 `page`**（`auth-01..06`、`in-01..04`、`out-reacquisition.json`、`out-reacquisition_report.md`、`out-oracle.md`、`out-pathA_probe.json`、`out-pathB_probe.json`、`out-path_compare.json`），**其中 `in-01/02/03` 是三份 PDF 输入件**。附带：`in-01/02/03` 也**只有 note、无 P3 锚文本**（P3 要求可定位到行/字节区）⇒ 建议 G8（P2/page）+ G9（P3/输入件锚文本，可并入 G8）一并交 S5 |

---

## 五、`L165` 措辞差 —— 回源判定

- **L165 原文（我逐字回源）**：`… | 实现者 + 独立 reviewer | S1/S3 授权 | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |`。
- **被审卡三处引用**（`oracle.md §1`、`s4_report.md §授权`、`handoff.json:authorized_by.S4_definition_verbatim.quote`）**与原文逐字一致** ✓。
- **「派单转述 = 该来源不可用」**：我在 `execution_runs/**`（`*.md` / `*.json`）、计划根 `*.md`、`execution_v2/dispatch.json` 全盘搜索，**该措辞除被审卡自己的勘误处外 0 命中** ⇒ 派单原文**无落盘记录**。
- **判定**：
  1. 这**不是工位找茬** —— 工位做的是「以文件原文为准执行 + 显式登记转述差」，正是本计划反复要求的回源纪律；且两者**处置同向**（该来源不得引用 + 维持不可读）。
  2. 「**父的错**」这一归属：**方向合理但不可考（记 unverified）** —— 盘上没有派单文本可比对；能确证的只有 **L165 原文与 S4 引用一致**。
  3. 对 S4 交付**不扣分**（不计缺陷）。

---

## 六、越权检查（逐项，含正文反证）

| 越权项 | 期望 | 实测 | 结论 |
|---|---|---|---|
| 判会计证据等级 | 不得 | `level_claimed = null` + `level_claimed_note`；正文无任何 C 表①/②等级判定 | **未犯** |
| 重裁 IND C 表 | 不得 | `industry_rule_regraded = false`；正文只"提请 S5 按 ④ 裁" | **未犯** |
| 解 `OPEN-5` | 不得 | `open5_released = false`、`releases_nothing = true` | **未犯** |
| 放行 `_PLACEHOLDER` | 不得 | `placeholder_params_released = false`；`boundary_L179` 明写"更不解除任何处置" | **未犯** |
| 下 S5 结论 | 不得 | 只有 §四"给 S5 的提请语"；`next_station` = reviewer → S5 | **未犯** |
| 自任 reviewer | 不得 | `self_reviewer_claimed = false`、`independent_reviewer = "由父另派，本工位不自任"` | **未犯** |
| 改 prior `not_readable` | 不得 | `prior_not_readable_preserved = true`、`prior_not_readable_verdict_changed = false`、`still_not_readable_disposition = true` | **未犯** |
| 写五份计划文件 | 不得 | 我实测 mtime：`implementation_plan.md 2026-09-20`、`OWNER_DECISIONS.md 2026-09-25T23:21Z`（早于本卡 oracle 23:41Z）、`task_plan/findings/progress/REMEDIATION_REGISTER` 均在 **2026-09-26 05:59–07:11Z（本卡 00:09Z 交付之后）** | **未犯** |
| 越出写入面 / git 写 / `git status` / 联网 | 禁 | 我复跑 `git diff HEAD --name-only`：**非 `.planning` = 0**；`git write = 0`、`git_status_used = false`、`network_used = false`；`company-wiki` 原件与 sidecar mtime = `2026-09-19T04:52Z`（本卡窗口外） | **未犯** |

---

## 七、分级（P1 = 无 ⇒ `ACCEPT`）

### P2（应在 S5 消费前补记，**本复审工位不代改**）

1. **P2-1 · `s4_report.md` L66 的 sha 与交付文件不符**：§1.0 表第 5 行写 `attempt08 pdfminer | 我的 sha256 = 6f29f209…`，但 `_work/extract/s4_attempt08_pdfminer.extracted.txt` 的**实际 sha = `c55dc630dc4390b15a9f6dfed3bb7d174377cfd3849aad4d7463903637821f88` / 1,016,147 B**（`handoff.json:written_files` 与 `dual_path_verify.json:fresh_extraction_new.sub08_pdfminer` **都登记为 `c55dc630…`，且与盘上字节相符**）。`6f29f209` 在本卡产物中**只出现这一次**，不对应任何已登记产物。
   - **我的交叉证据**：我**独立重跑**同方法（`extract_pages` + `LTTextContainer` + `<<<PAGE n>>>\n`）得到的文本 sha **恰好 = `6f29f209…`**（1,016,147 B，与交付文件同长）；与交付文件**仅在 p243 附近一处文本块排序上差 1,616 个字符**（`ndiff=1616`，CR 均为 0），**锚词结果完全不受影响**（中 0/5、英 5/5、`pdfminer-only = ∅` 与我的 run 一致）。
   - 影响：**报告表格里这一格 sha 不可用于核验交付文件**；机器可读登记（handoff / dual_path_verify）正确，结论不受影响。

2. **P2-2 · 「101 个落盘文件」计数失实 + 证据范围外推**：
   - 我实测：**101 条登记 = 51 个不同文件**（`20 个 ocr_text ×3 种路径写法`、`10 个 renders ×2`、`21 个 ×1`；去重直方图 `1×21 / 2×10 / 3×20`），且**101 条路径全部位于 S3 attempt 目录内**。
   - 因此 `s4_report.md §1.0 / §五-1` 与 `handoff.json:s3_s1_bytes_evidence = "101 files re-hashed"` 的**"101 个文件"表述不实**（实为 51 个文件的 101 条登记），且用它**外推自证"未改 S1 两站、封盘 I-11-A"超出其覆盖范围**。
   - **实质结论仍然成立**（我独立佐证）：51 个 S3 文件全部与 S3 自身登记相等；`attempt04/attempt08` 与 oracle 期望 sha 相等；**封盘 `I-11-A` 已被 git 跟踪（`git ls-files` = 103 个），我复跑 `git diff HEAD --name-only` 中 `I-11-A / S3 / PEND5A / PEND5B` 命中 = 0**。

3. **P2-3 · provenance 缺项清单漏报第 8 项**：G1–G7 未覆盖 `oracle §5.4 P2 (page / whole_document)` —— **16/26 条缺 `page`**（含 `in-01/02/03` 三份 PDF 输入件）；`in-01/02/03` 同时缺 P3 锚文本（只有通配 note）。清单以「缺项如下」呈现 ⇒ **完备性表述过头**，S5 引用前应补 G8（见 §四）。

### P3（可留档，不阻断）

4. **P3-1 · G1 分级偏重**：`counts` 字段不自洽属实，但属汇总字段缺陷（26 条条目均完整可定位），我判 **medium** 而非 hard。保守方向（更严）不构成风险，仅登记口径差异。
5. **P3-2 · 两处口径未写明**：(a) `§1.2` 两库「总字符」基数不同 —— fitz `295,785`（**含 415 个 `<<<PAGE n>>>` 标记**，我复算 `289,668 + 5,702 + 415 = 295,785`）vs pypdfium2 `298,151`（**不含标记**，我复算同值）；(b) G6 的 `32` 未写明其已排除 `provenance.json`/`handoff.json` 自身与 2 个 manifest（我数为 36）。两者均不影响任何锚词/一致性结论。

---

## 八、unverified（我未证实 / 无法证实的项）

1. **3 处数字分歧中哪一侧等于视觉真值** —— 我**未重跑 OCR 引擎、未做像素级核字**（同被审卡口径，oracle §6.5）；我证实的是「两路读数不同」这一**字节级事实**。
2. **A 路（OCR）独立重跑** —— 全局 `rapidocr 3.8.1 / onnxruntime 1.26.0 / pypdfium2 4.30.0` ≠ S3 的 `3.9.2 / 1.30.0 / 5.13.0`，跨版本不构成同条件复现；我的 A 面数字是对 **sha 核验全等的 S3 落盘 OCR 文本**重算。
3. **派单原文措辞** —— 盘上无 S4 派单落盘记录，「派单写作『该来源不可用』」**不可考**（见 §五）。
4. **`PEND-5B` venv manifest（410 MB / 3110 文件）** —— 我**未独立复算**（与 G7 同口径，标未证实）。
5. **`git status` 类证据** —— 按纪律**禁用**，故未跟踪/未提交面的证据仅来自 `git diff HEAD --name-only` + `git ls-files` + sha 重算；**未跟踪的非 `.planning` 新增文件**无法在本纪律下穷举。
6. **`attempt08` pdfminer 两次抽取的差异成因** —— 我只确证「同长、p243 局部排序差 1,616 字符、锚词结果相同」，**未定位**被审卡两次抽取的具体代码差（其 `_work` 脚本只保留最终一版）。
7. **可读区覆盖率 38.0952%** 的分母含乱码串夹带的正常汉字（冻结定义所致）⇒ 是**下界**（与被审卡披露一致）。

---

## 九、边界：我**没有做**的事（逐条）

1. **未改** 本 attempt 任何既有字节：`oracle.md`(14,801 B)、`oracle-addendum-A/B.md`、`dual_path_verify.json`(147,718 B)、`s4_report.md`(18,657 B)、`handoff.json`(18,710 B)、`_work/**` —— 交付前后 sha 全部一致（§六 实测）。
2. **未写卡状态**：不写任何 `card_*.md`、不改 `state/status/verdict/next_station`。
3. **未改** S3 / S1 两站 / 封盘 `I-11-A` / 产品仓 `company-wiki` **任何字节**（只读 + 哈希）。
4. **未重跑 OCR 引擎、未做像素级核字**。
5. **未判会计证据等级、未重裁 IND C 表、未解 `OPEN-5`、未放行 `_PLACEHOLDER`、未下 S5 结论、未自任"双重角色"代签**。
6. **零 git 写**；**未使用 `git status`**（仅 `git diff HEAD --name-only` / `git ls-files`，均只读）；**未联网**。
7. **测试只在 `%TEMP%\s4rev\` 隔离副本**（`origin.pdf`/`attempt04.pdf`/`attempt08.pdf`/S3 ocr_text 等均为副本），生产树上只做只读读取与哈希。
8. **未写** `.planning` 五份计划文件；**未写本目录以外任何路径**（写入面 = 本目录新建 2 件）。
9. **未替被审卡"修正"任何数字或分级** —— P2/P3 只登记、留给本卡/父处置。

---

## 十、我的 raw 实测 rc / sha

| 脚本（`%TEMP%\s4rev\`） | 用途 | rc | 产物 sha256 |
|---|---|---|---|
| `rev1_numeric.py` | ① M1 头条 + 数字两路比对（双文字层变体） | **0** | `rev1_out.json` = `fb53efece7db9dbabba1c4bd70cf656e5e0c47237764aebb0265d7cd1600bb9c`（6,898 B） |
| `rev2_sha.py` | ③ 101 条登记 sha 全量重算 + S3 交叉比对 | **0** | 控制台：`files_checked 101 / mismatch 0 / missing 0 / 与 S3 自登记差 0`（首跑因分隔符写法 `exit 1`，修正后 rc=0） |
| `rev3_faces.py` | ②③① `attempt08 pdfminer` / B1 pypdfium2 / attempt04 M2 | **0** | `rev3_out.json` = `ac032a5294f62d12409bc08d2b779d3a4f072d0b0550d9a44f939694e2db3f3f`（4,722 B）（首跑因源 PDF 未入副本 `exit 1`，补拷后 rc=0） |
| `rev4_vs_s3.py` / `rev5_perpage.py` | ② 与 S3 逐项对表 / 逐页集合比对 | 1（`rev4` 字段名 `KeyError`，由 `rev5` 取代） / **0** | 输出见 §3.1 |

**关键输入 sha（我实测）**：`origin.pdf = ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c`（4,405,561 B）· `attempt04.pdf = d0975600c918683636d4679328fa1eaa4a7a14b53950440d53005c831829b62b` · `attempt08.pdf = b787f0290513e48a95078ed2a68dc1e240da68d204e5dd9aedc59b66a7c75ec2` · 我的 fitz 全文抽取 = `d628cf53a8cbb898…`（与登记逐字节全等）· 我的 attempt08 pdfminer 文本 = `6f29f209053eb124…`（对应报告 L66）vs 交付文件 `c55dc630dc4390b1…`。

**被审 7 件既有字节（写前实测，与 `handoff.written_files` 逐件相符）**：`oracle.md 14,801 → e4fa02fcf3991529…` · `oracle-addendum-A.md 2,649 → e0cafbfdf3f249f0…` · `oracle-addendum-B.md 2,691 → 9e94143f1553d42c…` · `dual_path_verify.json 147,718 → 218a4195bcd72637…` · `s4_report.md 18,657 → 7987f5de4926f0e2…` · `handoff.json 18,710 → 29e6971f72275cef…` · `_work/raw_measurements.json 201,785 → 3ec2114b9f3845d6…`。

**纪律终检**：`git diff HEAD --name-only` 非 `.planning` = **0**（本复审工位复跑实测）；`OPEN5-S3-REACQUISITION / PEND5A / PEND5B / I-11-A / OPEN5-S4-*` 在 diff 中命中 = **0**。
