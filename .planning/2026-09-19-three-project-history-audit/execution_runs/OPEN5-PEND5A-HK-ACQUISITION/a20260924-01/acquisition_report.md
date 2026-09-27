# OPEN-5 · PEND-5a 港股（小米 1810.HK）可读替代件取证报告

- 卡：`OPEN-5`（I-11-A 开放问题）· 恢复路径 **PEND-5a = S1 的一半**（联网取可读替代件）
- 工位：`OPEN5-PEND5A-HK-ACQUISITION`，角色 `controlled_acquisition`
- attempt 目录：`.planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/`
- 授权（逐字）：`OWNER_DECISIONS.md` **§二十六 #1**（L541）owner 原话 **「授权」**；父侧转述原话 **「1，授权」**；派单原文 **「派 8abdd519 = OPEN5-PEND5A-HK-ACQUISITION」**；硬边界原文见 `provenance.json.authorization.hard_bounds_verbatim`
- 取证时间窗（UTC，实测真实时刻，未改写）：**2026-09-24T22:04:02Z – 2026-09-25T20:43:08Z**（会话中断约 22 小时，09-24 记录原样保留，09-25 为续跑新动作）
- 本报告**不做证据等级判定**（等级归会计面）、**不解除 OPEN-5**、**不改 I-11-A 任何状态**

---

## 0. 结论速览（只报观察到的形态，不定级）

| 对象 | 期间 | 观察形态 | 中文锚词命中（本卡探针） |
|---|---|---|---|
| **attempt04**：港交所原站《截至2025年12月31日止年度之全年業績公告》 | **FY2025，与原文件同期间**（文件类型不同：业绩公告，非年报） | **`E1-COMPLETE`（五要素 5/5 齐，原站直取、非代理）** | **4/5**（小米 47 / 收入 158 / 分部 77 / 毛利 101 / 年度報告 0），独立第二路径 4/5 |
| **attempt08**：发行人官网《Xiaomi 2025 AR_EN》= 年报本体英文版 | **FY2025，与原文件同期间同一篇（语言不同）** | **`E1-COMPLETE`（五要素 5/5 齐）**，但中文锚词 0/5 | 中文 **0/5**（英文正文）；英文锚词 5/5 |
| attempt01/02：中文年报本体（原站 / 发行人官网） | FY2025 = 同期间**同一件**（sha 与原文件全等） | **`BLOCKED`**（正文无一处可读，缺④逐字引文） | **0/5**（与原文件同形态） |
| attempt07：r.jina.ai 代理渲染中文年报 | FY2025（代理转录） | **`BLOCKED`**（乱码）+ **`external_retrieval_not_local=true`** | **0/5** |
| attempt05：发行人中文业绩演示稿 | FY2025 | **`BLOCKED`**（中文整段不可抽） | 0/5 |
| attempt06：英文年报 URL 猜测 | — | **失败**（HTTP 404，错误页留痕） | 不适用 |

> **一句话**：原文件的**中文年报本体仍然取不到可读件（BLOCKED，未造绿样）**；同期间可读、五要素齐全的替代件是**港交所原站的 FY2025 全年业绩公告（4/5 中文锚词，两条独立抽取路径互证）**，另取得**同期间年报英文版**（英文锚词 5/5、中文 0/5）。二者的定级与"能否替代年报支撑命题"**由会计面裁定，本工位不代判**。

---

## 1. 目标与原文件基线

原文件 `HK-XIAOMI-AR2025`：2026-04-28 hkexnews `12127452`、4,405,561 B、sha `ffd733761633f464…`，正文因字体**无 `/ToUnicode` + 内嵌子集无 `cmap`** 不可读（封盘 attempt 判定：**0 命中**）。

本工位优先级：①港交所原站可读 PDF → ②发行人官网 → ③交易所公告 → ④研究稿/新闻=仅线索。

---

## 2. 尝试台账（成功与失败全部登记；详表在 `provenance.json.external_evidence` / `failed_tool_attempts`）

### 2.1 字节取证 8 次

| # | URL（原样） | 取回 UTC | HTTP | 字节 | sha256 前16 | 方法 | 结果 |
|---|---|---|---|---|---|---|---|
| ext-01 | `www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800527_c.pdf` | 2026-09-24T22:06:27Z | **200** | 4,405,561 | `ffd733761633f464` | 直取原站 | 同原文件字节 ⇒ 不可读（0/5） |
| ext-02 | `ir.mi.com/…/2026/04/28/5-31-40/Xiaomi 2025 AR_c.pdf` | 2026-09-24T22:08:18Z | **200** | 4,405,561 | `ffd733761633f464` | 直取发行人官网 | 与 ext-01 逐字节相同 ⇒ 不可读 |
| ext-03 | `ir.mi.com/…/2026/03/24/5-35-52/25Q4 CN AC Xiaomi.pdf` | 2026-09-24T22:08:20Z | **200** | 1,044,325 | `d0975600c9186836` | 直取发行人官网 | 与 ext-04 逐字节相同 |
| **ext-04** | `www1.hkexnews.hk/listedco/listconews/sehk/2026/0324/2026032400609_c.pdf` | 2026-09-24T22:09:26Z | **200** | 1,044,325 | `d0975600c9186836` | **直取原站** | ✅ **可读，4/5 锚词** |
| ext-05 | `ir.mi.com/…/2026/03/24/6-22-11/Xiaomi Corp_25Q4_ER_CHN vF.pdf` | 2026-09-24T22:11:29Z | **200** | 5,221,344 | `b71853f52daab027` | 直取发行人官网 | 0/5 ⇒ 弃用 |
| ext-06 | `www1.hkexnews.hk/…/2026/0428/2026042800527.pdf` | 2026-09-24T22:11:31Z | **404** | 2,057（错误页） | `1d56c1549bda2f9f` | 直取原站 | 失败，错误页留痕 |
| **ext-07** | `r.jina.ai/https://www1.hkexnews.hk/…/2026042800527_c.pdf` | 2026-09-24T22:11:39Z | **200** | 873,816 | `a44064f13f6ee8a0` | **第三方代理** | 0/5 乱码 ⇒ 失败；**`external_retrieval_not_local=true`** |
| **ext-08** | `ir.mi.com/…/2026/04/28/5-29-08/Xiaomi 2025 AR_EN.pdf` | 2026-09-25T20:37:56Z | **200** | 3,556,507 | `b787f0290513e48a` | 直取发行人官网 | ✅ 年报本体英文版可读（英 5/5、中 0/5） |

### 2.2 发现类与失败的工具尝试

- `web_search`：**2 次端点错误**（DeepSeek 端点返回非 JSON：`SyntaxError: Unexpected token 'e'`），与 `I11A-OPEN-ACCT` 登记的端点故障同族 ⇒ 改走 `web_fetch`。
- `web_fetch` 取 PDF：**1 次** `unsupported content type "application/pdf"` ⇒ 字节落盘改用 `probe/dl.py`。
- `curl.exe`(schannel)：**2 次** `SEC_E_NO_CREDENTIALS`；`Invoke-WebRequest`：**2 次**「基础连接已经关闭」⇒ 本机 Windows TLS 通道不可用，python urllib(OpenSSL) 可用（原站实测 **200**，`Content-Length: 4405561`，`Last-Modified: Tue, 28 Apr 2026 08:30:42 GMT`）。
- `filing-fetch`：**未执行**其 ensure/download（落盘点 = company-wiki 产品仓，按纪律不执行）；其只读 reuse 也是 reuse-first 同一份不可读字节，对本卡无增益。
- 发现类 `web_fetch`：DuckDuckGo HTML ×3、`ir.mi.com` 目录页 ×2（**仅线索，不作一手**）。

**合计外部请求 ≈ 20 次**：字节取证 8、发现类 5、失败的工具/通道尝试 7。

---

## 3. 可读性自检数据（本卡目的）

锚词：`小米` / `收入` / `年度報告` / `分部` / `毛利`，**≥3 命中即过**；原文件为 **0 命中**。

| 文件 | 抽取路径 | rc | 抽出字符（CJK） | 小米 | 收入 | 年度報告 | 分部 | 毛利 | **命中词数** |
|---|---|---|---|---|---|---|---|---|---|
| **attempt04**（业绩公告，原站） | P1 `tools/pdf_text.py -B` | 0 | 18,150 | 0 | 0 | 0 | 0 | 0 | **0/5**（工具不支持 Adobe-CNS1） |
| attempt04 | P2 `pdftotext` Xpdf 4.00 | 0 | 127,723 | 1 | 0 | 0 | 0 | 0 | **1/5**（stderr 刷 `Unknown character collection 'Adobe-CNS1'`） |
| attempt04 | **P3 PyMuPDF 1.26.7** | 0 | 45,593（**23,481** CJK） | **47** | **158** | 0 | **77** | **101** | **4/5 ✅** |
| attempt04 | **P4 pdfminer.six 20260107（独立路径）** | 0 | 61,520（**23,481** CJK） | **15** | **21** | 0 | **18** | **21** | **4/5 ✅** |
| attempt01（中文年报原站） | P1 `pdf_text.py -B`（415/415 页） | 0 | 13,227 | 0 | 0 | 0 | 0 | 0 | **0/5 ❌** |
| attempt01 | P3 PyMuPDF（415/415 页） | 0 | 298,689（55,698 CJK 乱码） | 0 | 0 | 0 | 0 | 0 | **0/5 ❌** |
| attempt05（中文演示稿） | P1 `pdf_text.py -B`（38/38 页） | 0 | 5,224 | 0 | 0 | 0 | 0 | 0 | **0/5 ❌** |
| attempt07（第三方代理文本） | 文本锚词计数 | 1 | 460,387 | 0 | 0 | 0 | 0 | 0 | **0/5 ❌** |
| attempt08（年报英文版） | P3 PyMuPDF | 0 | 951,018 | 0 | 0 | 0 | 0 | 0 | **中 0/5**；英文 Xiaomi 920 / Revenue 33 / Annual Report 3 / Segment 9 / Gross profit 7 = **5/5** |
| attempt08 | P4 pdfminer.six（独立路径） | 0 | 1,022,506 | 0 | 0 | 0 | 0 | 0 | 中 0/5；英文 **5/5**（Xiaomi 919） |

**抽样片段（字节区，均可在 `probe/*.extracted.txt` 复算）**

1. `probe/attempt04_fitz.extracted.txt` L10 `[499,560]`：`截至2 0 2 5 年1 2 月3 1 日止年度之全年業績公告`
2. 同文件 L7 `[346,358]`：`小米集团`
3. 同文件 L88 `[2306,2410]`：`比增長25.0%。業務分部來看，2025年，我們的「手機×AIoT」分部收入為人民幣3,512`
4. 独立路径 `probe/attempt04_pdfminer.extracted.txt` L218 `[11799,11905]`：`5.4% 。「手機×AIoT」分部毛利率達到歷史新高的21.7% ，同比增長0.5個百分點 。2025`
5. 反面对照 `probe/attempt01_fitz.extracted.txt` L3 `[25,92]` 可读封面 `股份代號：1810（港幣櫃台）及 81810（人民幣櫃台）`；L141 `[3118,3169]` 正文乱码 `1810灭㷱⸥㪅⎲灮⎌81810灭Ṽ㯓⸥㪅⎲灮`

> **根因复核（与 OPEN5-ENVOWNER 一致）**：中文年报 = Type0/Identity-H 子集字体、无 `/ToUnicode`、无 `cmap` ⇒ **任何路径都取不出**（P1/P3 均 0）；业绩公告的中文以 **Adobe-CNS1 字符集**编码，**文本层完整**，只是 `pdf_text.py`（明文声明不做 CID without ToUnicode）与缺 CMap 文件的 Xpdf 读不出 ⇒ 换带 Adobe-CNS1 的抽取器即可读。**这不是把乱码当可读**：4/5 命中来自 23,481 个 CJK 字符的完整文本层，且两库互证。

---

## 4. 五要素自检表（E1：①本地归档 ②文件 sha256 ③取回 UTC ④逐字引文 ⑤独立复核路径）

### 4.1 主替代件 attempt04（港交所原站 · FY2025 全年业绩公告）

| 要素 | 判定 | 证据 |
|---|---|---|
| ① 本地归档 | ✅ | `corpus/attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf`（落本计划目录内；未写产品仓） |
| ② 文件 sha256 | ✅ | `d0975600c918683636d4679328fa1eaa4a7a14b53950440d53005c831829b62b`（Get-FileHash 复核 = 下载回执） |
| ③ 取回 UTC | ✅ | `2026-09-24T22:09:26Z`（dl.py 实时回执） |
| ④ 逐字引文 ≥3 | ✅ | q-01/q-02/q-03（fitz 抽取件，带行号+字节区）+ q-04（pdfminer 抽取件），合计 4 条 |
| ⑤ 独立复核路径 | ✅ | PyMuPDF 与 pdfminer.six **两库独立**抽取同字节：中文锚词均 4/5、CJK 均 23,481；另有 pdftotext 路径记录其能力缺口（1/5） |
| **观察形态** | **`E1-COMPLETE`** | 五要素 5/5；**等级判定不做，归会计面** |

### 4.2 年报本体英文版 attempt08（发行人官网 · FY2025）

| 要素 | 判定 | 证据 |
|---|---|---|
| ① 本地归档 | ✅ | `corpus/attempt08_irmi_xiaomi_ar2025_en.pdf` |
| ② 文件 sha256 | ✅ | `b787f0290513e48a95078ed2a68dc1e240da68d204e5dd9aedc59b66a7c75ec2` |
| ③ 取回 UTC | ✅ | `2026-09-25T20:37:56Z` |
| ④ 逐字引文 ≥3 | ✅ | q-08/q-09（2 条英文正文引文，带行号+字节区）＋ 英文锚词计数记录；**中文逐字引文 0 条**（正文为英文） |
| ⑤ 独立复核路径 | ✅ | PyMuPDF（951,018 字符 / 英 5/5）与 pdfminer.six（1,022,506 字符 / 英 5/5） |
| **观察形态** | **`E1-COMPLETE`**（语言差异必须随行标注） | 中文锚词 0/5 ⇒ **不满足本卡中文锚词探针** |

### 4.3 中文本体年报 attempt01 = attempt02（原站 / 发行人官网，同 sha）

| 要素 | 判定 | 证据 |
|---|---|---|
| ① 本地归档 | ✅ | `corpus/attempt01_hkexnews_xiaomi_ar2025_zh.pdf`、`attempt02_irmi_xiaomi_ar2025_zh.pdf` |
| ② 文件 sha256 | ✅ | `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c` = **原文件登记 sha 全等** |
| ③ 取回 UTC | ✅ | `2026-09-24T22:06:27Z` / `2026-09-24T22:08:18Z` |
| ④ 逐字引文（正文） | ❌ | 正文 0 锚词，无一段可读正文可引；仅封面 q-05 可读、q-06 为乱码样张 |
| ⑤ 独立复核路径 | ⚠️ 部分 | P1（pdf_text.py）与 P3（PyMuPDF）独立一致：**均 0/5**（复核的是"不可读"这一事实） |
| **观察形态** | **`BLOCKED`** | 缺④；**维持不可读，不造绿样** |

### 4.4 其余

- attempt07（第三方代理）：①②③ 有，④ 仅元数据行、⑤ 无意义 ⇒ **`BLOCKED`**，且 **`external_retrieval_not_local=true`**。
- attempt05：④⑤ 不成立 ⇒ **`BLOCKED`**。
- attempt06：HTTP 404 ⇒ 失败尝试留痕。

---

## 5. 期间交叉登记（不同期间/不同文件不得当同一件）

| 文件 | 期间 | 与原文件（HK-XIAOMI-AR2025，FY2025 年报）关系 | 能否支撑 OPEN-3/OPEN-5 所需期间 |
|---|---|---|---|
| 原文件 / attempt01 / attempt02 | **FY2025**（截至 2025-12-31） | **同期间、同一篇、字节全等**（sha `ffd73376…`） | 期间一致，但**正文不可读 ⇒ 不能提供可核原文** |
| **attempt04 / attempt03** | **FY2025**（标题逐字：`截至2025年12月31日止年度之全年業績公告`） | **同期间、不同文件类型**：年度**业绩公告**（2026-03-24 刊发）≠ 年度报告（2026-04-28 刊发） | **期间可覆盖 FY2025**；但它**不是年报**（无年报全文附注/审计年报结构），**能否替代年报支撑命题由会计面裁定**，本工位不代答 |
| attempt08 | **FY2025**，年报本体 **英文版** | 同一篇年报的**另一语言版本**（中文锚词 0/5） | 期间一致；语言差异显著，**中文命题不能直接以它充当中文原文** |
| attempt05 | FY2025 | 同期间，业绩**演示稿**（二手呈现，非申报原文） | 不可读且非原文形态 |
| attempt07 | FY2025 | 同一篇的**第三方代理转录** | 乱码 + 代理转录，不作原文 |

> 明示：**本工位没有把任何不同时期的文件当同一件**；上表"同期间"均指同一财年 FY2025，"不同文件类型/不同语言/代理转录"逐项标注。

---

## 6. 第三方代理标注（必须明说）

- **经第三方代理的仅 1 件：attempt07（`https://r.jina.ai/...`）** ⇒ `external_retrieval_not_local = true`，`retrieval_method = third_party_proxy_r_jina_ai`，其字节是**代理返回的 Markdown 文本，不是原站 PDF 字节**；结果仍为 0 锚词，**已按失败处理**。
- **attempt01/04/06 = 港交所原站直取**（python urllib → `www1.hkexnews.hk`，无中间代理，HTTP 200）⇒ `external_retrieval_not_local = false`。
- **attempt02/03/05/08 = 发行人官网 ir.mi.com 直取** ⇒ `external_retrieval_not_local = false`。
- 搜索引擎（DuckDuckGo HTML）只用于发现 URL，其摘要**不作一手证据**。
- 原站**没有 403**（与上一站 SEC 403 情形不同）；上一站教训中的 403 标注义务在本卡未触发，但代理件仍按义务显式标注。

---

## 7. 边界：本工位**没有**做的事

1. **没有写产品仓**：未写 `company-wiki` / `filing-fetch` / `revenue-forecast` 产品路径，**未写 `companies/{entity}/raw/`**；未执行 `filing-fetch --allow-download`（其落盘点是产品仓）。
2. **没有 git 写操作**：全程只跑只读 `git diff HEAD --name-only` / `ls-files --others` / `status --porcelain`；无 add/commit/checkout/stash/restore/reset。
3. **没有判定会计证据等级**：只报观察形态（`E1-COMPLETE` / `BLOCKED`），**等级归会计面**（§二十四 #3 执行纪律原文：「取证的证据等级由会计面定，不由取证方自定」）。
4. **没有解除 OPEN-5**：`OPEN-5` 对 I-11-B 港股参数、I-07-B 港股 case 的阻塞**原样**；未改 I-11-A 任何 `status`/`state`/`not_readable` 字段，未代签。
5. **没有把 `not_readable` 改成"已验证"**：封盘 attempt `I-11-A/a20260919-01` 只读（其 `tools/pdf_text.py` 仅被 `-B` 执行，未修改）。
6. **没有造绿样**：中文年报本体判 `BLOCKED`；没有把乱码、二手稿、不同期间文件冒充可读原文。
7. **没有判行业面处置规则、没有放行任何 `_PLACEHOLDER` 参数、没有产生 ACCEPT**。
8. **没有对 S2→S5 其余步代劳**：S2（能力自检复核）、S3（新建 attempt 重新取证）、S4（双路径复核）、S5（行业复裁 + 会计定级）仍归各自角色。

---

## 8. 产出清单与写入面

- `provenance.json`（全部尝试，成功与失败；E1 五要素证据；9 条逐字引文带行号/字节区）
- `acquisition_report.md`（本文件）
- `handoff.json`（卡片回执）
- `corpus/`：8 个实际取得的字节文件（含 1 个 404 错误页留痕）
- `probe/`：抽取与探针脚本 7 个、探针结果 JSON 12 个、抽取文本 8 个、引文定位 JSON 4 个

**写入面**：全部位于本 attempt 目录内（`.planning/…/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/`）；`.planning` 之外创建/修改 = **0**。

**git 实测（只读）**：`git diff HEAD --name-only` 总计 **3826** 条，**非 `.planning` = 0**；untracked 非 `.planning` 46 条，全部为既有 `.tmp-r41-mutation/*` 等历史路径，与本工位无关。
