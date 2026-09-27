# OPEN5-S3-REACQUISITION · S3 新建 attempt 对 HK 原文重新取文报告

- **卡 / 步**：`OPEN-5` 恢复路径 **S3**（DEC-8 恢复规则）· attempt = `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/`
- **角色**：`implementer_s3`（编排层派单的实现者）
- **授权（逐字回源）**：
  - `decision.md` **L227–228（DEC-8）**：「**恢复规则**：可读性恢复后（工具或依赖变更），新建 attempt 重新取证；不得把本次的 `not_readable` 判定改成"已验证"。」
  - `I11A-OPEN5-ENVOWNER/…/ruling.md` **L164（S3）**：「**新建 attempt 重新取证**（卡文 DEC-8 恢复规则）：在**全新 attempt** 中对 HK 原文重新取文；**封盘 attempt `I-11-A/a20260919-01` 与本次 `not_readable` 判定一律不动**」；执行方「编排层派单的实现者（新 attempt）」。
  - 同文件 **L179（边界）**：「即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（…参数维持 `_PLACEHOLDER`）。」
  - `OWNER_DECISIONS.md` **§二十六 #1/#2**：`PEND-5a` owner 原话「**授权**」、`PEND-5b` owner 原话「**要**」→ 澄清「**两项都要（PEND-5b 装 + E1 交会计面）**」。
  - 能力来源：`OPEN5-PEND5B-OCR-CAPABILITY/…/capability_report.md` = **`CAPABLE`**；可读替代件来源：`OPEN5-PEND5A-HK-ACQUISITION/…/acquisition_report.md`（attempt04 **4/5**、attempt08 英文 **5/5**）。
- **执行时间窗（UTC，实测，未改写）**：`oracle.md` 冻结 **2026-09-25T22:53:18Z** → 只读 manifest（前）**22:55:08Z** → 路径 A 探针 **22:57:52Z – 23:01:00Z**（182,449 ms）→ 路径 B 探针 **22:59:48Z – 22:59:59Z** → 比对与汇总 **23:0x–23:13:58Z** → `handoff.json` **23:14:09Z** → 收尾复核（只读 manifest 后、git diff、编码扫描）**23:1xZ**。
- **`oracle.md` 先冻结**（sha `24d4d4e242010a29…`，写于任何探针之前；本报告不改它）。

---

## 0. 结论速览

| 字段 | 值 |
|---|---|
| **`readability_result`** | **`readable`** —— 依冻结判据 oracle §4.3：路径 A 对 **sha 全等的原文件字节**产出 **5/5 锚词命中**（≥3/5 = A-pass） |
| 路径 A（OCR，`ocr_reconstruction`） | **rc=0，5/5 锚词**；同页 origin 文字层 **0/5**（对照）；零 OCR 失败页 |
| 路径 B1（原文件文字层，全 415 页） | **0/5**（295,785 字符）⇒ 单独不可读，与封盘结论一致 |
| 路径 B2（替代件 attempt04，双库） | PyMuPDF **4/5** + pdfminer.six **4/5**，两库命中词一致 ⇒ **B-pass** |
| 路径 B2′（替代件 attempt08 英文版） | 中文 **0/5**；英文 **5/5**（`Xiaomi 920 / Revenue 33 / Annual Report 3 / Segment 9 / Gross profit 7`） |
| `ocr_reconstruction` | **true**（路径 A 全部文本字段；永不冒充 origin 文本） |
| 旧 `not_readable` 判定 | **原样保留**（`prior_not_readable_preserved=true`）；封盘与 S1 两站 **manifest 前后逐文件 sha 全等** |
| 解锁动作 | **零**：不解 `OPEN-5`、不放行参数、不产生 ACCEPT、不定级（`releases_nothing=true`） |

> **一句话**：在全新 attempt 中，路径 A（OCR）对原文件字节重新取文得到 **5/5 锚词**、路径 B1 复证原文件文字层仍 **0/5**、路径 B2 用 S1 的可读替代件双库各 **4/5**；据冻结判据 S3 记 `readable`，但按 ruling L179，**S4/S5 走完前一切仍按不可读处置**。

---

## 1. 目标与基线（开跑前核验）

| 项 | 值 |
|---|---|
| 对象 | `HK-XIAOMI-AR2025` = `C:\Users\郑曾波\Projects\company-wiki\companies\小米集團－Ｗ\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf` |
| 字节 / sha256 | **4,405,561 B** / **`ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c`**（Get-FileHash 实测 = 派单值 ✓；脚本内 `--expect-sha` fail-closed 复核通过） |
| 页数 / mtime | 415 / `2026-09-19T04:52:11Z`（收尾复测未变） |
| 处置 | **只读**：仅 hash、渲染、文字层读取；未复制、未改字节、未写产品仓 |

---

## 2. 路径 A —— OCR 重新取文（`ocr_reconstruction`）

- **引擎**：`rapidocr 3.9.2 + onnxruntime 1.30.0`（CPU）· 渲染 `pypdfium2 5.13.0`，200 dpi —— **只读复用** `OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/venv/`（`PYTHONDONTWRITEBYTECODE=1`、`PYTHONPATH` 指向**本 attempt** 的 `_shim/`、`TEMP/TMP` 指向本 attempt 的 `_tmp/`；**该 venv 一个字节未写**，见 §5 manifest）。
- **抽样页（oracle 冻结）**：`1, 2, 30, 43, 47, 115, 160, 337, 355, 399`（10/415 = 2.4%）。
- **rc=0**；OCR 失败页 **0**；OCR 总字符 7,740；墙钟 182,449 ms；页均置信 0.923–0.991。
- **证据落盘**：每页 `renders/s3_pathA_p####.png`（含 png sha256）+ `ocr_text/s3_pathA_p####.ocr.txt`（含文本 sha256）+ 同页 `…origin_textlayer.txt`（对照，含 sha256）；逐条命中含**页 / OCR 行号 / 字节区**。

### 2.1 锚词命中（命中数 / 命中页）

| 锚词 | 命中页数 | 命中页 |
|---|---|---|
| `小米` | **3** | 1, 30, 160 |
| `收入` | **2** | 115, 337 |
| `年度報告` | **8** | 1, 2, 43, 47, 115, 337, 355, 399 |
| `分部` | **1** | 337 |
| `毛利` | **1** | 337 |
| **合计（锚词×页）** | **15** | **锚词 5/5** |

**同页 origin 文字层对照 = 0/5**（10 页全部 `False`；文字层非空，35–1,367 字符但无一处锚词）⇒ 与 RC-1 根因、与 PEND-5b 实测一致。

### 2.2 抽样片段（带页 / 行 / 字节区；**全部 `ocr_reconstruction`**）

| # | 页 | 行 | 字节区 `[start,end)` | 片段（重建文本，非原文提取） |
|---|---|---|---|---|
| A-1 | 1 | 3 | `[70,76]` | `小米集团`（模型按简体字形输出，误差类型=简繁，引用前须核字） |
| A-2 | 1 | 5 | `[156,168]` | `2025年度報告` |
| A-3 | 2 | 1 | `[3,15]` | `本年度報告(英文及中文版)已於本公司網站www.mi.com及聯交所網站` |
| A-4 | 115 | 11 | `[770,776]` | `…並結合其對收入、運營成本、資本開支、資產減值、供應鏈穩定…` |
| A-5 | 160 | 15 | `[1419,1425]` | `…小米汽車建立了系統化的功能安全與預期功能安全管理及開發流程…` |
| A-6 | 337 | 6 | `[90,96]` | `分部資料及收入（续）` |
| A-7 | 337 | 7 | `[166,172]` | `截至2025年及2024年12月31日止年度的分部業績及收入資料如下：` |
| A-8 | 337 | 45 | `[691,697]` | `毛利/(虧損)` |
| A-9 | 337 | 29 | `[498,504]` | `分部收入` |

（每条的完整行文本与该页 png/文本 sha 见 `reacquisition.json → paths.A_ocr.per_page[].ocr_first_evidence`。）

---

## 3. 路径 B —— 可读替代件 / 文字层

### 3.1 B1 原文件自身文字层（对照，PyMuPDF 全 415 页）

- 抽出 **295,785 字符**（`extract/origin_fitz_full.txt`，sha256 登记于 `reacquisition.json`）。
- **5 个锚词命中数全部 = 0，命中页并集为空**（抽样 10 页逐页亦 0）⇒ **B1 单独不可读**，与封盘 attempt 的 `not_readable` 事实完全一致（**本次未改其判定**）。

### 3.2 B2 替代件 `attempt04`（港交所原站 FY2025 全年业绩公告，**双独立库**）

- 输入（**只读复用 PEND-5a corpus**）：`OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf`，**1,044,325 B**，`sha256=d0975600c918683636d4679328fa1eaa4a7a14b53950440d53005c831829b62b`，取回 UTC `2026-09-24T22:09:26Z`，`retrieval_method=direct_from_origin_site_www1.hkexnews.hk`，`external_retrieval_not_local=false`，**`substitute_not_origin=true`**。

| 锚词 | PyMuPDF 命中数 / 页 | pdfminer.six 命中数 / 页 |
|---|---|---|
| `小米` | 47 / 1,3,4,5,6,7,8,9,55,59 | 15 / 1,3,4,7,8 |
| `收入` | 158 / 1,2,5,…,49,50（28 页） | 21 / 2,5,6,7,8,11,13,17,21,26,29,30,35（13 页） |
| `年度報告` | **0** | **0** |
| `分部` | 77 / 2,5,7,8,…,49,50（23 页） | 18 / 2,5,8,15,16,20,22,24,29,31,32,33,34（13 页） |
| `毛利` | 101 / 1,2,5,…,49（19 页） | 21 / 5,6,15,16,23,24,32,33,34（9 页） |
| **命中词数** | **4/5** | **4/5**（两库命中词一致 = True） |

**抽样片段（带页 / 行 / 字节区）**

| # | 库 | 锚词 | 页 | 行 | 字节区 | 片段 |
|---|---|---|---|---|---|---|
| B-1 | fitz | `小米` | 1 | 7 | `[340,346]` | `小米集团` |
| B-2 | fitz | `分部` | 2 | 87 | `[2316,2322]` | `比增長25.0%。業務分部來看，2025年，我們的「手機×AIoT」分部收入為人民幣3,512` |
| B-3 | fitz | `毛利` | 1 | 29 | `[1290,1296]` | `毛利`（财务摘要行） |
| B-4 | pdfminer | `分部` | 2 | 84 | `[2623,2629]` | `比增長25.0% 。業務分部來看 ，2025年 ，我們的「手機×AIoT」分部收入為人民幣3,512` |
| B-5 | pdfminer | `毛利` | 5 | 173 | `[11842,11848]` | `5.4% 。「手機×AIoT」分部毛利率達到歷史新高的21.7% ，同比增長0.5個百分點 。2025` |
| B-6 | pdfminer | `小米` | 1 | 10 | `[581,587]` | `小米集团（「本公司」）董事（「董事」）會（「董事會」）欣然公佈本公司及其附屬公司（統稱「本` |

> 与 PEND-5a 记录**逐数一致**（fitz 47/158/0/77/101、pdfminer 15/21/0/18/21）⇒ S1 成果被**原样复核**，未重取、未改写。

### 3.3 B2′ 替代件 `attempt08`（年报英文版）

- 输入：`corpus/attempt08_irmi_xiaomi_ar2025_en.pdf`，**3,556,507 B**，`sha256=b787f0290513e48a95078ed2a68dc1e240da68d204e5dd9aedc59b66a7c75ec2`，取回 UTC `2026-09-25T20:37:56Z`，`retrieval_method=direct_from_issuer_site_ir.mi.com`，`external_retrieval_not_local=false`，**`substitute_not_origin=true`**。
- **中文锚词 0/5**（英文正文）；**英文锚词 5/5**：`Xiaomi` 920（首现 p7 `[3315,3321]`）、`Revenue` 33（p8 `[4518,4525]`）、`Gross profit` 7（p8 `[4586,4598]`）、`Segment` 9（p10 `[7515,7522]`）、`Annual Report` 3（p112 `[250928,250941]`）。
- **不作为中文可读结论**；语言差异随行标注。

---

## 4. 五要素自检（E1：①本地归档 ②文件 sha256 ③取回 UTC ④逐字引文 ⑤独立复核路径）

### 4.1 本 attempt 的 HK 原文 OCR 取文（路径 A）

| 要素 | 判定 | 证据 |
|---|---|---|
| ① 本地归档 | ✅ | `renders/*.png`（10 张，逐张 sha256）、`ocr_text/*.ocr.txt`（10 份，逐份 sha256）、`ocr_text/*.origin_textlayer.txt`（10 份）—— 全落本 attempt 目录 |
| ② 文件 sha256 | ✅ | 原文件 `ffd73376…22da7c` = 派单基线（脚本 `--expect-sha` fail-closed 通过）；每页 png/文本 sha 见 `reacquisition.json` |
| ③ 取回 UTC | ✅（形态不同，如实登记） | **本 attempt 无外部取件**：`retrieved_utc = null`、`retrieval_method = local_bytes_no_external_retrieval_this_attempt`、`external_retrieval_not_local = false`；OCR 完成 UTC 见 `pathA_probe.json → finished_utc` |
| ④ 逐字引文 ≥3 | ✅ | §2.2 共 **9 条**（页/行/字节区齐备），p337 单页即 4 个锚词全中 |
| ⑤ 独立复核路径 | ✅（部分，余留 S4） | 同页 **origin 文字层独立抽取**（0/5 对照，独立于 OCR）+ **B2 双库互证**；**真正的双路径同页同段互证按 ruling 属 S4**，本 attempt 已把两路输出与比对方法落盘（§6） |
| **观察形态** | **`E1-COMPLETE`（OCR 形态）** | **证据等级不判（归 S5）** |

### 4.2 替代件 `attempt04` / `attempt08`（路径 B2/B2′）

| 要素 | attempt04 | attempt08 |
|---|---|---|
| ① 本地归档 | ✅ PEND-5a `corpus/`（**只读复用，未复制进产品仓**） | ✅ 同 |
| ② 文件 sha256 | ✅ `d0975600…829b62b` | ✅ `b787f029…a7c75ec2` |
| ③ 取回 UTC | ✅ `2026-09-24T22:09:26Z`（沿用 PEND-5a 实时回执） | ✅ `2026-09-25T20:37:56Z` |
| ④ 逐字引文 ≥3 | ✅ 本 attempt 新增 6 条（B-1…B-6，带页/行/字节区） | ✅ 5 条英文首现定位（页/字节区） |
| ⑤ 独立复核路径 | ✅ PyMuPDF + pdfminer.six **两独立库**，命中词一致 | ✅ 本 attempt PyMuPDF 抽取（PEND-5a 另有 pdfminer 记录） |
| **观察形态** | **`E1-COMPLETE`，`substitute_not_origin=true`**（中文 4/5） | **`E1-COMPLETE`，`substitute_not_origin=true`**（中 0/5、英 5/5） |

> **边界照录**：attempt04 是**业绩公告**（非年报本体）、attempt08 是**英文版**；**能否替代年报 / 证据等级，归 S5 会计面，本工位不代判**。

---

## 5. 与 S1 两站成果的**字节关系**（只读复用，零字节改动）

对三个只读参考目录做 **sha256 级 manifest（逐文件 path|bytes|sha256 聚合）**，探针前后各一次：

| 目录 | 文件数 | 聚合 sha256（前 → 后） | 结论 |
|---|---|---|---|
| `I-11-A/a20260919-01`（封盘） | 1,961 | `76858344183a1ed1…` → `76858344183a1ed1…` | **完全一致，一个字节未改** |
| `OPEN5-PEND5A-HK-ACQUISITION/a20260924-01` | 44 | `34741d2d6286dbfe…` → `34741d2d6286dbfe…` | **完全一致**（仅读取 `corpus/attempt04`、`attempt08` 两件） |
| `OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01` | 3,110 | `abeb5b06f6462f3e…` → `abeb5b06f6462f3e…` | **完全一致**（venv 只读执行；`PYTHONDONTWRITEBYTECODE=1`，无 `__pycache__` 落其目录） |

（明细：`_work/manifest_before.json` / `_work/manifest_after.json`，逐文件 5,115 条 `path|bytes|sha256`。）

- **原文件字节关系**：本 attempt 未下载、未复制、未移动 HK 原文；读取前后 `sha256` 与 `mtime` 不变。
- **替代件字节关系**：`attempt04`/`attempt08` 的 sha256 与 PEND-5a `acquisition_report.md` §2.1 登记**逐字相同** ⇒ 本 attempt **消费的是 S1 的原字节**，非重取、非改写。
- **判定字节关系**：封盘 `not_readable` 判定、`I-11-A` 的 `decision.md`/`hypotheses.json`/`source_map.json`/`mechanism_review.md`/`handoff.json` **全部未触碰**；PEND-5a/PEND-5b 的 `capability_report.md`/`acquisition_report.md`/`provenance.json`/`handoff.json` **全部未触碰**。
- **产品仓**：`company-wiki` **只读**（仅 `Get-FileHash` 与解析读取），未写任何文件；本轮不涉 §二十七 #2。

---

## 6. 给 S4 铺路（双路径输出 + 各自 sha + 比对方法）

落盘 `_work/path_compare.json`（sha256 记于 `reacquisition.json → s4_staging`），**只摆输入与方法，不下 S4 结论**（`verdict_left_to = S4`）：

**比对方法**
1. **A vs B1（同页）**：两侧文本做**去空白归一化**后比较 —— (a) 任一 OCR 长中文行（≥8 汉字）是否**逐字**出现在同页 origin 文字层；(b) origin 文字层中**可读片段**（封面 `股份代號：1810…`）是否被 OCR 复现。
2. **B2 fitz vs pdfminer（同文件同段）**：取库 1 的锚词首现行（归一化）搜库 2 全文；并比对**逐页锚词命中集合**。

**已摆好的输入与实测**
- A vs B1：10 页、**92 行**长中文 OCR 行受检，**逐字命中 origin 文字层 = 1 行**（即封面可读片段，`fragment_present_in_ocr = true`）；正文页 **0 行** ⇒ 「OCR 读出的正文在文字层里根本不存在」——与 RC-1 一致，**正是 S4 要复核的形态**。
- B2：4 个命中锚词的首现行**跨库逐字命中 = 4/4**；两库命中词集合一致；逐页命中集合交/并集已列（`per_anchor.page_set_intersection/union`）。
- 每个输入文件的 **sha256** 均登记在 `path_compare.json` 与 `reacquisition.json`（png / ocr.txt / origin_textlayer.txt / 提取件）。

---

## 7. 边界：本工位**没有**做的事

1. **没有**改封盘 `I-11-A/a20260919-01` 任何字节；**没有**把本次 `not_readable` 判定改成「已验证」（DEC-8 明令）。
2. **没有**改 `OPEN5-PEND5B-OCR-CAPABILITY` 与 `OPEN5-PEND5A-HK-ACQUISITION` 任何字节（manifest 前后全等为证）。
3. **没有**解除 `OPEN-5`：按 ruling **L179**，**S4/S5 走完前一律仍按不可读处置**；港股命题零产出、参数维持 `_PLACEHOLDER`。
4. **没有**放行任何 `_PLACEHOLDER` 参数、**没有**产生 `I-11-B` 的 ACCEPT、**没有**代签。
5. **没有**写五份计划文件（`task_plan.md`/`findings.md`/`progress.md` 等）。
6. **没有**判会计证据等级（S5）与行业复裁（S5）；**没有**下 S4 双路径一致性结论（只铺路）。
7. **没有**写 `.planning` 之外任何路径（含 `company-wiki` 产品仓）；**零 git 写**；**未用 `git status`**。
8. **没有**把 CN 样本（`CN-ZIJIN-AR2025`）自检当 HK 结论 —— 本 attempt **不跑 CN 样本**，CN 自检仅作 S2 既有记录被引用。
9. **没有**造绿样：B1 全篇 0 命中如实登记；attempt08 中文 0/5 如实登记；OCR 简繁混写与字形近似误差（如 `小米集团` 应为 `小米集團`、`IoT→loT`）如实标注，引用前须人工核字。

---

## 8. 产物与写入面

| 文件 | 说明 |
|---|---|
| `oracle.md` | **先冻结**的判据、路径定义、`not_readable` 条件、范围边界（sha `24d4d4e2…`） |
| `reacquisition.json` | 逐路径逐页结果 + 证据（命中页/行/字节区、png 与文本 sha、文字层对照） |
| `provenance.json` | 授权逐字、输入/输出 sha256、引擎与渲染版本、`ocr_reconstruction` 标记 |
| `reacquisition_report.md` | 本文件（含五要素自检与 S1 字节关系） |
| `handoff.json` | 卡片回执（`role=implementer_s3`、`readability_result`、`paths_run`、`written_files`、`git_diff_non_planning=0`） |
| `_work/` | 脚本 7 个（`s3_pathA_ocr.py` / `s3_pathB_textlayer.py` / `s3_path_compare.py` / `s3_assemble.py` / `s3_make_handoff.py` / `s3_manifest.py` / `s3_normalise_lf.py`）、`pathA_probe.json`、`pathB_probe.json`、`path_compare.json`、`manifest_before/after.json`、`renders/`（10 PNG）、`ocr_text/`（20 份）、`extract/`（4 份） |
| `_shim/sitecustomize.py` | 本 attempt 自有 mkdir shim（**复制机制，不引用对方文件**） |

**写入面**：全部位于 `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/`；`.planning` 之外创建/修改 = **0**。

**编码自检（纪律 6）**：全部写入文件 **UTF-8 无 BOM、纯 LF**（41 个文本/脚本/JSON/MD 全量扫描：BOM = 0、CRLF = 0）。其中 10 份 origin 文字层转储因 pdfium `get_text_range()` 返回值自带 `\r`，已按纪律归一为 LF（`_work/s3_normalise_lf.py`）；**原始字符串的 sha256 保留为各页 `text_layer_sha256`**，可由重跑探针逐字复算。JSON 全部写后 `json.load` 重解析通过。

**git 实测（只读）**：`git diff HEAD --name-only`（`core.quotepath=false`）总计 **3,826** 条，**非 `.planning` = 0**；untracked 非 `.planning` = **48** 条，全部为既有 `.tmp-r41-mutation/*` 历史路径，本 attempt **0 条**。零 `add/commit/checkout/stash/reset/restore`。
