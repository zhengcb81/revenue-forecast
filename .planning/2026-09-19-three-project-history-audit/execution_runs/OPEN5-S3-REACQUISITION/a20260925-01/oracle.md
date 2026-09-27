# OPEN5-S3-REACQUISITION · oracle（**先冻结**）

- **卡 / attempt**：`OPEN-5` 恢复路径 **S3** / `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/`
- **角色**：`implementer_s3`（编排层派单的实现者）
- **授权（逐字回源）**：
  1. `execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` **L164（S3 定义）**：「**新建 attempt 重新取证**（卡文 DEC-8 恢复规则）：在**全新 attempt** 中对 HK 原文重新取文；**封盘 attempt `I-11-A/a20260919-01` 与本次 `not_readable` 判定一律不动**」；执行方=「编排层派单的实现者（新 attempt）」；失败分支=「新 attempt 仍不可读 ⇒ 记 `not_readable`（新记录），**旧判定原样**，回到 S1」。
  2. 同文件 **L161–166**（S0–S5 全表）与 **L174–179（边界）**：L179「即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**」。
  3. `execution_runs/I-11-A/a20260919-01/decision.md` **L227–228（DEC-8 恢复规则原文）**：「**恢复规则**：可读性恢复后（工具或依赖变更），新建 attempt 重新取证；不得把本次的 `not_readable` 判定改成"已验证"。」
  4. `execution_runs/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/capability_report.md` —— **`CAPABLE`**（能力复用来源，只读）。
  5. `execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/acquisition_report.md` —— 可读替代件与锚词自检（attempt04 港交所原站 **4/5**、attempt08 英文年报 **5/5**）。
  6. `OWNER_DECISIONS.md` **§二十六 #1/#2**（两路授权：#1 `PEND-5a` owner 原话「授权」、#2 `PEND-5b` owner 原话「要」→澄清「两项都要」）。

## 0. 冻结声明

本文件在**任何探针/取文动作之前**写入（本 attempt 内全部 probe 产物的 mtime 必须晚于本文件）。判据一经冻结不改；如执行中发现判据必须修订，**另建 `oracle-addendum.md`** 并说明原因，**不改本文件**。

## 1. 范围边界（S3 only）

- **只做**：在**全新 attempt** 中对 `HK-XIAOMI-AR2025` 重新取文（两条路径并跑）+ 锚词自检 + provenance + 为 S4 铺路。
- **不做（明令）**：
  1. 不改封盘 `I-11-A/a20260919-01` 任何字节；不把其 `not_readable` 判定改成「已验证」。
  2. 不改 `OPEN5-PEND5B-OCR-CAPABILITY`、`OPEN5-PEND5A-HK-ACQUISITION` 两站任何字节（**只读复用**）。
  3. **不解除 `OPEN-5`**、不判 `OPEN-5` 已解 —— S4/S5 走完前**一律仍按不可读处置**（L179）。
  4. 不放行港股参数（维持 `_PLACEHOLDER`）；不产生 `I-11-B` 的 ACCEPT；不代签。
  5. 不写五份计划文件（`task_plan.md`/`findings.md`/`progress.md`/`implementation_plan.md`/`REMEDIATION_REGISTER.md` 等）。
  6. 不判会计证据等级（归 S5）；不做 S4 的双路径同页同段一致性复核结论（只落盘其输入）。
  7. 不写 `.planning` 之外任何路径（**含 `company-wiki` 产品仓**，本轮不涉 §二十七 #2）；零 git 写；**禁用 `git status`**。
- **写入面**：仅 `execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/`。

## 2. 目标文件基线（开跑前核验，不满足即 fail-closed）

| 项 | 值 |
|---|---|
| 对象 | `HK-XIAOMI-AR2025` = `company-wiki/companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf` |
| 字节 | **4,405,561 B** |
| sha256 | **`ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c`** |
| 页数 | 415 |
| 处置 | **只读**（仅 hash / 渲染 / 文字层读取；不复制进产品仓、不改 mtime） |
| 取回 UTC | 本 attempt **不发生外部取件** ⇒ 路径 A/B 均为本地字节；替代件沿用 PEND-5a 登记的取回 UTC |

## 3. 两条路径定义（并跑，为 S4 铺路）

| 路径 | 定义 | 依赖来源（只读） | 产物标记 |
|---|---|---|---|
| **路径 A = OCR** | 对**原文件**抽样页 `pypdfium2` 渲染 → `rapidocr` OCR → 锚词检索；同页同时登记 origin 文字层对照 | `OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/venv/`（只读引用，`PYTHONDONTWRITEBYTECODE=1`，不写其任何文件） | **`ocr_reconstruction = true`**（图像→文本重建，**永不冒充 origin 文本**） |
| **路径 B = 可读替代件 / 文字层** | B1 = 原文件**自身文字层**（同抽样页，PyMuPDF + pypdfium2 两路）；B2 = PEND-5a 本地替代件 `attempt04`（港交所原站 FY2025 业绩公告）与 `attempt08`（年报英文版）文字层抽取 + 锚词 | `OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/*`（只读复用，逐件登记 sha256）+ 全局解释器 `PyMuPDF/pdfminer.six` | `text_layer`（origin 文本层抽取，非重建）；替代件随行标 `substitute_not_origin` |

**抽样页（冻结，共 10 页，取自 S2 已验证锚词分布 + 对照页）**：`1, 2, 30, 43, 47, 115, 160, 337, 355, 399`（1-based，`200 dpi`）。

**锚词（冻结，5 个）**：`小米` · `收入` · `年度報告` · `分部` · `毛利`。

## 4. 判据（通过线，先冻结）

### 4.1 路径 A（对**原文件**，sha 必须全等于 §2）

| 结果 | 判定 |
|---|---|
| 锚词命中 **≥ 3/5**（逐词登记命中数与命中页） | **A-pass** |
| 命中 1–2/5 | `partial`（**不足以致 `readable`**） |
| 命中 **0/5**，或进程 rc ≠ 0，或 sha 与 §2 不全等 | **A-fail** |

- 每个命中必须登记：**锚词 / 命中页 / OCR 行号 / 片段（含该片段在重建文本中的字节区）/ 该页 png 的 sha256** —— 缺登记 = 该命中不计（不造绿样）。
- 同页 origin 文字层结果**另行登记为对照**（预期 0/5，系 RC-1 根因），**不计入 A-pass**。

### 4.2 路径 B

| 子路 | 判定 |
|---|---|
| **B1 原文件文字层**（同 10 页，两库各跑一次） | 只**登记**命中数（预期 **0/5**）；两库不一致 ⇒ 记「不一致」并 fail-closed 处置该子路 |
| **B2 替代件 `attempt04`**（PyMuPDF + pdfminer.six **两独立库**） | 两库**各 ≥ 3/5** ⇒ **B-pass**；任一库 < 3/5 ⇒ 该库 `fail`，B2 记 `不一致` |
| **B2' `attempt08`（英文版）** | 只登记：中文锚词命中数（预期 0/5）+ 英文锚词 `Xiaomi/Revenue/Annual Report/Segment/Gross profit` 命中（预期 5/5）；**不作为中文可读结论** |

- 替代件命中必须登记：**锚词 / 命中数 / 命中页码或行号 / 抽样片段带行号+字节区**。

### 4.3 `readability_result`（本 attempt 的结论字段）

- **`readable`** ⟺ **A-pass**（路径 A 对原文件 sha 全等的字节产出 ≥3/5 锚词，且逐条证据登记齐全）。
- **`not_readable`** ⟺ A-fail 或 `partial`（含技术失败）。**此为合格结果**（L164 失败分支），旧判定原样保留。
- **路径 B 不单独决定 `readability_result`**（B2 是替代件不是原文件本体）；B2 结果以 `substitute_readable: true/false` 单列登记。
- **即使得 `readable`**：本 attempt **仍不解 `OPEN-5`**、不改旧 `not_readable`、不放行参数、不定级 —— 依 L179，**S4/S5 走完前一律仍按不可读处置**。`readability_result` 只是 S3 的取证观察，不是解锁动作。

### 4.4 fail-closed 条款

1. 任何路径缺证据（页/行/字节区/sha 任一缺失）⇒ 该路径按**未通过**登记，**不放宽阈值**。
2. **不得**把 CN 样本（`CN-ZIJIN-AR2025`）自检通过当 HK 结论（S2 边界明令）——本 attempt **不跑 CN 样本**，只引用 S2 的既有记录并标注其为 S2 成果。
3. 缺证据写「未证实」；**不造绿样**。
4. OCR 产物一律 `ocr_reconstruction`，简繁/字形误差如实登记，引用前需人工核字（S4/S5 事项）。

## 5. 纪律自检点（收尾时逐条核）

1. `I-11-A/a20260919-01`、PEND-5a、PEND-5b 三目录 **manifest 前后比对 = 0 差异**（sha256 级）。
2. JSON 写后 `json.load` 重解析通过；UTF-8 无 BOM；纯 LF。
3. `git diff HEAD --name-only` **非 `.planning` = 0**；无 `git status`；零 git 写。
4. `handoff.json` 必含：`role=implementer_s3`、`authorized_by`（DEC-8 + S3 逐字）、`readability_result`、`paths_run`（A/B 各自 rc + 锚词命中）、`ocr_reconstruction`、`sealed_attempt_untouched=true`、`prior_not_readable_preserved=true`、`releases_nothing=true`、`written_files`（sha256+字节）、`git_diff_non_planning=0`。
