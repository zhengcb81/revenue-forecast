# OPEN5-S4-DUAL-PATH-VERIFY · oracle（**先冻结**）

- **卡 / 步**：`OPEN-5` 恢复路径 **S4（双路径复核 + provenance）**
- **attempt**：`execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/`
- **角色**：`implementer_s4`（编排层派单的实现者）；**独立 reviewer 那一半由父另派，本工位不自任**
- **写入面**：仅 `execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/`（`.planning` 内）

---

## 0. 冻结声明

本文件在**任何复核/取文/比对动作之前**写入；本 attempt 内全部测量产物的 mtime 必须晚于本文件。
判据一经冻结不改；若执行中发现判据必须修订 ⇒ 另建 `oracle-addendum.md` 并写明原因，**不改本文件**。

---

## 1. 授权（逐字回源）

1. `execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` **L165（S4 定义，逐字）**：
   > `| **S4** | **双路径复核 + provenance**：两条独立取文路径互证（承 P1/P2 精神），登记文件 sha256、页码/锚文本、取回 UTC；外部件按 IND C 表 **④** 标 `external_retrieval_not_local`、**永不冒充本地** | 实现者 + 独立 reviewer | S1/S3 授权 | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |`

   - ⚠️ **回源勘误（必须登记）**：派单转述的失败分支写作「复核不一致 ⇒ 该来源**不可用**」；`ruling.md` L165 表内原文为「**该来源不可引用，维持不可读处置**」。**以文件原文为准**，转述属同族的「转述改变措辞」（本计划父侧错误第 18/20 起同族）。两者在处置后果上同向（该来源不得引用 + 维持不可读），但**字面不同，按原文执行**。
2. 同文件 **L166 = S5**（行业复裁 + 会计定级；受理人 = 行业 reviewer + 会计 reviewer，「本载体不代行」）—— **那是下一站，本工位不做**。
3. 同文件 **L174–L179（边界，逐字要点）**：「即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）」；DEC-8 恢复规则「不得把本次的 `not_readable` 判定改成"已验证"」。
4. `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/` —— **S3 全部产物**（只读）：`_work/path_compare.json`（已摆输入与方法、明写 `verdict_left_to=S4`）、`reacquisition.json`、`handoff.json`、`provenance.json`、`_work/*`。
5. `OWNER_DECISIONS.md` **§二十六 #1/#2**（两路授权：#1 `PEND-5a` owner 原话「授权」；#2 `PEND-5b` owner 原话「要」→ 澄清答「两项都要」）。
6. `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` **L234（IND C 表 ④，逐字）**：
   > `| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | `external_retrieval_not_local` | 必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径 |`
   及同文件 **L360（OPEN-11 语义，逐字）**：「**外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`」；**L261**：「用外部抓取件静默顶替本地原件（必须按④登记为外部）」= 明令被拒。

---

## 2. 范围边界（S4 only）

**只做三面**：
1. **面1 = 双路径互证**：按 `_work/path_compare.json` 已列的两种方法**自己重跑一遍**（不采信 S3 的数字），逐路径逐页给出命中与行号/字节区证据；
2. **面2 = provenance 完整性**：逐条核 S3 `provenance.json` 是否齐备「文件 sha256 / 页码 / 锚文本 / 取回 UTC / 外部件 ④ 标注」；本工位自己的 provenance 也按同一标准登记；
3. **面3 = 一致性结论**：三选一（`CONSISTENT` / `PARTIAL` / `NOT_USABLE`），给理由。

**不做（明令，逐条）**：
1. 不改 S3（`OPEN5-S3-REACQUISITION/a20260925-01`）、S1 两站（`OPEN5-PEND5A`/`OPEN5-PEND5B`）、封盘 `I-11-A/a20260919-01` 任何字节 —— **只读**；
2. 不把任何 `not_readable` 改成「已验证」（L174–179；**S5 未走完前一律仍按不可读处置**，**即使本工位判 `CONSISTENT` 也一样**）；
3. **不判会计证据等级**（`level_claimed = null`）、**不重裁 IND C 表行业处置规则**；
4. **不解除 `OPEN-5`**、不放行 `_PLACEHOLDER` 参数、不产生 `I-11-B` 的 ACCEPT、不代签；
5. **不自任独立 reviewer**（S4 受理人 = 实现者 + 独立 reviewer，reviewer 那一半由父另派）；
6. 不写五份计划文件（`task_plan.md` / `findings.md` / `progress.md` / `IMPLEMENTATION_PLAN.md` / `PLANNING_STATUS.md` 等）；
7. **写入面 = 本目录**；不写 `.planning` 之外任何路径（**含 `company-wiki` 产品仓**）；零 git 写；**禁用 `git status`**；**禁止联网**（全部复核在盘上已完成的产物之间做）。

---

## 3. 受核输入（全部只读，先登记 sha256 再用）

| 代号 | 对象 | 路径 | 期望 sha256 / 字节 |
|---|---|---|---|
| **U1-origin** | `HK-XIAOMI-AR2025` 原文件 | `company-wiki/companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf` | `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c` / 4,405,561 B / 415 页 |
| **U2-sub04** | 替代件（港交所原站 FY2025 业绩公告） | `OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf` | `d0975600c918683636d4679328fa1eaa4a7a14b53950440d53005c831829b62b` / 1,044,325 B |
| **U3-sub08** | 替代件（发行人官网 年报英文版） | `OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/attempt08_irmi_xiaomi_ar2025_en.pdf` | `b787f0290513e48a95078ed2a68dc1e240da68d204e5dd9aedc59b66a7c75ec2` / 3,556,507 B |
| **A-artifacts** | S3 路径 A 的 OCR 重建文本 + origin 文字层文本（10 页 ×2） | `OPEN5-S3-REACQUISITION/a20260925-01/_work/ocr_text/*.txt` | 逐件 sha 必须全等于 `path_compare.json` / `reacquisition.json` 登记值 |
| **S3-meta** | S3 元数据 | `path_compare.json` `b503e4a8…`、`reacquisition.json` `f948276a…`、`handoff.json`、`provenance.json` `3e44f7e9…` | 全等才可用作对照 |

**sha 不全等 ⇒ fail-closed：该输入按未核验处理，不下结论。**

**锚词（承 S3 冻结，不改）**：`小米` · `收入` · `年度報告` · `分部` · `毛利`（中文 5 个）；`Xiaomi` · `Revenue` · `Annual Report` · `Segment` · `Gross profit`（英文 5 个，仅用于 U3）。
**抽样页（承 S3 冻结，不改）**：`1, 2, 30, 43, 47, 115, 160, 337, 355, 399`（1-based，10 页）。

---

## 4. 方法（**逐字承 `_work/path_compare.json`，本工位重跑，不采信 S3 数字**）

### M1 — A（OCR 重建）↔ B1（原文件文字层），同 10 页
> 原文：「Same sampled pages: normalise (whitespace-stripped) both the OCR reconstruction and the origin text layer; check (a) whether any full OCR line (>=8 CJK chars) occurs verbatim in the origin layer (expected: no — origin layer is GID-garbled), and (b) whether the readable cover fragment present in the origin layer also appears in the OCR text (expected: yes — readable-in-both cross-check).」

- 归一化 `norm(s) = re.sub(r"\s+", "", s)`（去空白，**不改字形、不改语言**）。
- **(a)** 每页取 OCR 中 `CJK(U+4E00–U+9FFF) 计数 ≥ 8` 的整行（**每页上限 40 行**，承 S3 同参），逐行查是否逐字出现在该页 origin 文字层归一化文本中。
- **(b)** origin 第 1 页可读封面片段 `股份代號…`（正则 `股份代號[^\n]{0,60}`）是否出现在该页 OCR 归一化文本中。
- **M1-补（本工位新增的反向覆盖检查，先冻结）**：从每页 origin 文字层中抽取**可读区** = (i) ASCII 可打印连串 `[\x20-\x7e]{4,}` 且含字母，或 (ii) `U+4E00–U+9FFF` 正常汉字连串长度 ≥2（排除 `U+3400–U+4DBF` 等 GID 乱码区），逐个查其在同页 OCR 归一化文本中的**复现情况**，分类：
  - `reproduced` = 归一化后逐字出现在 OCR 中；
  - `miss` = 未出现（**覆盖缺口，不计矛盾**）；
  - `numeric_conflict` = 未出现、且 origin 该可读区含阿拉伯数字串，而 OCR 同页存在**同长不同值**的数字串读取 ⇒ 计为**矛盾**。

### M2 — B2（替代件 attempt04）fitz ↔ pdfminer 跨库
> 原文：「Same substitute file: for every anchor, take the first-hit line of library 1 (normalised) and search it in library 2's normalised text; also compare per-page anchor presence sets.」

- 同一文件、同一冻结锚词；两库各自产出带 `<<<PAGE n>>>` 标记的全文；
- (i) 每锚词取 fitz 首命中行（归一化）在 pdfminer 全文归一化文本中搜命中（`first_line_fitz_found_in_pdfminer`）；
- (ii) 每锚词的**逐页命中集合**求交/并，并单列 `pdfminer-only` 与 `fitz-only` 页；
- (iii) **锚词级命中集合**（word-level）两侧必须相同。
- **本工位重跑方式**：**不读 S3 的 extract 文件**，直接对 U2 原 PDF 用全局 `PyMuPDF 1.26.7` 与 `pdfminer.six 20260107` **重新抽取**（抽取算法：fitz `page.get_text()`；pdfminer `extract_pages` + `LTTextContainer.get_text()`，带同款页标记），再比对；随后**另比**我的抽取与 S3 登记的 extract 文件 sha256 是否全等（全等 = S3 抽取可复现）。

### M2′ — B2′（替代件 attempt08 英文年报）双库 + 双语
- 对 U3 同样跑 fitz 与 pdfminer 两库；分别统计中文 5 锚词与英文 5 锚词；
- 判据看**语言面自洽**（见 §5-U3）。

---

## 5. 判据（**三种一致性结论，先冻结**）

### 5.1 分面判定（每面取 `CONSISTENT` / `PARTIAL` / `NOT_USABLE`）

**U1 = origin 本体（A ↔ B1）**
| 判定 | 条件（全部满足） |
|---|---|
| `CONSISTENT` | (a) 逐字命中行**全部落在 origin 可读区**（预期 = 仅封面 1 行）；(b) 封面片段复现 = true；A 锚词 ≥3/5 且 B1 全文档 = 0/5；且 M1-补 的 `reproduced / total` = **100%**、`numeric_conflict = 0` |
| `PARTIAL` | (a)(b) 形态成立且 `numeric_conflict = 0`（**无矛盾**），但 `reproduced / total < 100%`（互证只覆盖 origin 可读区的一部分；origin 正文因 B1 乱码**根本没有第二路可互证**） |
| `NOT_USABLE` | 出现下列任一：`numeric_conflict > 0`；(b)=false（origin 可读而 OCR 未复现封面）；(a) 命中落在可读区之外；A 与 B1 的锚词形态与预期相反（如 B1 > 0 且读出乱码以外内容） |

**U2 = attempt04 替代件（fitz ↔ pdfminer）**
| 判定 | 条件（全部满足） |
|---|---|
| `CONSISTENT` | 两库**锚词级命中集合相同**；每锚词两库命中页**交集非空**；`pdfminer-only` 页 = 0；`first_line` 跨库命中数 = 两库共命中锚词数 |
| `PARTIAL` | 锚词级集合相同、`first_line` 全中，但存在页级差集（recall 差）或某锚词命中页交集为空 |
| `NOT_USABLE` | 锚词级集合不同（含一库 0 命中另一库 >0）；或某锚词 `first_line` 跨库搜不到（同一文件两库读出不同文本） |

**U3 = attempt08 替代件（双库 × 双语）**
| 判定 | 条件 |
|---|---|
| `CONSISTENT` | 两库中文锚词同为 0/5、英文锚词同为 5/5（语言面自洽），且**明确不作中文可读结论** |
| `PARTIAL` | 两库英文 5/5 但中文 0/5 与另一库不一致，或某英文锚词只在一库出现 |
| `NOT_USABLE` | 两库对同一语种给出相反结论（如一库中文 >0 另一库 =0 且非语言面原因） |

### 5.2 总判定 `consistency_result`（三选一）
| 值 | 条件 |
|---|---|
| **`CONSISTENT`** | U1、U2、U3 **三面全为 `CONSISTENT`** ⇒ 各来源**可用于 S5** |
| **`PARTIAL`** | 至少一面 `CONSISTENT`、至少一面 `PARTIAL`、**无** `NOT_USABLE` ⇒ 逐来源写清**哪些可用、哪些不可用** |
| **`NOT_USABLE`** | **任一面 `NOT_USABLE`** ⇒ 该来源不可引用、维持不可读处置（S4 失败分支，**这是合格结果**） |

**总判定分面归属规则（先冻结，避免事后挪动）**：
- `consistency_result` 针对**本轮可被 S5 消费的来源集合**给一个总值；
- 若某来源判 `NOT_USABLE` 而其他来源 `CONSISTENT` ⇒ 总值取 **`NOT_USABLE`**（fail-closed，就低不就高），并在报告中写明是哪一面触发、影响哪个来源；
- **绝不为推进链而判一致**：任何"差不多、方向对"都不升级为 `CONSISTENT`。

### 5.3 `NOT_USABLE` 的触发条件（汇总，失败分支）
1. M1 出现 `numeric_conflict`（同页数字读取矛盾）或封面可读片段未被 OCR 复现；
2. M2 两库锚词级命中集合不同 / `first_line` 跨库搜不到；
3. M2′ 两库对同一语种结论相反；
4. 任一受核输入 sha256 与 §3 期望值不全等；
5. 证据缺项（页码 / 锚文本 / 字节区 / sha 任一缺失）却仍被登记为「命中」⇒ 该命中不计，计数降级；若降级后跌破通过线 ⇒ 该面判 `NOT_USABLE`。

### 5.4 provenance 完整性判据（面2）
每条来源/产物条目必须齐 **P1–P5**，缺一项即登记为「缺项」（**不补写、不代填、只登记**）：
- **P1** `sha256`（文件级）
- **P2** `page`（页码，或明确 `whole_document`）
- **P3** `quote`/锚文本（可定位到行/字节区）
- **P4** `utc`（取回 UTC；本地既有字节可显式写 `n/a_local_bytes`，但须说明**未证实**）
- **P5** 外部件按 IND C 表 ④：**URL + 取回时间 + sha256** 三件齐，且标 `external_retrieval_not_local`、`substitute_not_origin`（永不冒充本地/origin）

### 5.5 边界复述（L179，任何结论都压在其下）
**即使 `consistency_result = CONSISTENT`，在 S5（行业复裁 + 会计定级）走完之前，一律仍按不可读处置**：港股命题零产出、参数维持 `_PLACEHOLDER`、`not_readable` 一字不改。

---

## 6. fail-closed 条款

1. 两条路径不一致 ⇒ **该来源 `NOT_USABLE`**，不为推进而判一致；**`NOT_USABLE` 是合格结果**。
2. 缺证据写「未证实」，**不造绿样**、不放宽阈值、不改锚词、不改抽样页。
3. JSON 写后必须 `json.load` 重解析；UTF-8 无 BOM；纯 LF。
4. 结束前 `git diff HEAD --name-only` 非 `.planning` = 0；零 git 写；**禁用 `git status`**。
5. 本工位**不重跑 OCR 引擎**（理由：全局 `rapidocr 3.8.1 / onnxruntime 1.26.0 / pypdfium2 4.30.0` ≠ S3 的 `3.9.2 / 1.30.0 / 5.13.0`，跨版本重跑不构成同条件复现，反而会引入不可比噪声）⇒ **A 路的数字按「对 S3 落盘 OCR 重建文本（sha 逐件核验全等）重算」得出**，并在报告中如实写明「A 未重跑 OCR 引擎」这一**未证实项**，不冒充独立重跑。
