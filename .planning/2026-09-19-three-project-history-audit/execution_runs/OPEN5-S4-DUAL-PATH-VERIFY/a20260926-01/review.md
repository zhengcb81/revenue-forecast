# OPEN5-S4-DUAL-PATH-VERIFY · a20260926-01 · 载体落定（carrier landing = 簿记转录）

> **写入面前置断言 —— 先 `Test-Path` 断言 `False`，后新建（本文件头即该断言的登记处）**
>
> ```
> PS> Test-Path '<attempt>\review.md'
> review.md exists: False
> PS> Test-Path '<attempt>\evidence'
> evidence exists: False
> PS> Test-Path '<attempt>\evidence\OPEN5-S4-DUAL-PATH-VERIFY\qualification.json'
> qualification exists: False
> ```
>
> 三项断言全部为 **`False`** 之后，本文件与 `evidence/OPEN5-S4-DUAL-PATH-VERIFY/qualification.json` 才被**新建**。
> 本 attempt 此前不存在 `review.md` 与 `evidence/`，无实现者存根需保留。

**Status: `accepted_scoped`** —— 转录自 `reviewer_report.md` **L14** 的 `VERDICT: ACCEPT`。
**本文件不产生任何裁决、不代签、不弱化任何发现。**

| 项 | 值 |
|---|---|
| 卡 / 步 | `OPEN-5` 恢复路径 **S4（双路径复核 + provenance）** |
| 被落定 attempt | `execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/` |
| 本工位角色 | carrier-landing bookkeeping executor（父派簿记落定子代理）—— **只转录，不新裁，不自签** |
| 裁决作者 | `independent_reviewer_s4`（与实现者非同一人）；裁决只存在于 carrier，不存在于本文件的任何字节 |
| 写入面 | 恰 3 处（§9）；本 attempt 既有产物与复审报告及侧车**写 0 字节** |

---

## 1. 载体（carrier）三方一致核对 —— 我自读、自算，未抄派单

| 项 | 值 |
|---|---|
| `reviewer_report.md` 字节 | **25835** |
| 我自算 sha256 | `643c072e797207852d1fc5ca7a35cdab1593ed5702a8e30edeb6a7d8177cad50` |
| 侧车 `reviewer_report.sha256`（85 B，侧车自身 sha `58f68d0844b5148e93f8b9db4eade4b0d878fdfbcda09c50b6b8c4eb4a6bb07e`）内容 | `643c072e797207852d1fc5ca7a35cdab1593ed5702a8e30edeb6a7d8177cad50  reviewer_report.md`（末尾 LF） |
| 派单给定 | `643c072e79720785…`（前 16 位） |
| **三方一致** | ✅ 自算 == 侧车内容 == 派单给定前缀（逐位相同） |

编码实测：**UTF-8 无 BOM**（首三字节 `23 20 4f` = `# O`）；全文 **CR = 0、LF = 194**；末字节 `0x0a`（单个结尾 LF）；按 LF 切分得 195 段、末段为空 ⇒ **行数 = 194**。

---

## 2. 裁决行自定位（行号 + 字节区 + 文本）—— 我自己扫字节找的

```
扫描规则：取「首行文本恰为 VERDICT: ACCEPT」的那一行（0-based 字节偏移逐行累加）
命中共 1 处 —— L14（全文另两处含 'verdict' 字样的是 L127 表格行与 L170 边界条款，均非裁决行）
```

| 项 | 值 |
|---|---|
| 行号 | **L14** |
| 整行字节区（0-based，**含**行尾 LF） | **`[1095, 1110]`**，长度 **16**（15 B 文本 + `0x0a`） |
| 整行 sha256 | `ffd796ea6572fdaf4dce6d9984e6e9294cf8c0c564ce345d73132bf29aa1b3b4` |
| 纯文本字节区（不含 LF） | `[1095, 1109]`，长度 **15**，sha256 `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |
| 行文本 | `VERDICT: ACCEPT` |
| 字节回读核验 | `raw[1095:1110] = 56 45 52 44 49 43 54 3a 20 41 43 43 45 50 54 0a` → `VERDICT: ACCEPT` + LF |
| 裁决词（复审所写） | `ACCEPT` |
| 分级规则行（L133，逐字） | ## 七、分级（P1 = 无 ⇒ `ACCEPT`） |
| 判级依据（L16–L17，逐字） | 见下 |

**复审判级依据原文（L16–L17，逐字）**：

```text
> 判级依据：**未发现 P1**。核心产出（`consistency_result = NOT_USABLE`）经我独立复算**成立**，是 fail-closed 的**合格产出、不是缺陷**；与 S3 数字**逐项全等**；三个新增面我各跑一遍**全部复现**；**未发现任何越权**。
> 下列 **P2×3 / P3×2** 均为「报告文本/计数/清单完备性」层面的缺陷，不改变任何结论，可在 S5 消费前由本卡补记（**复审工位不代改**）。
```

---

## 3. 状态面转录（`handoff.json`）

| 字段 | 值 |
|---|---|
| `status` | `""` → **`accepted_scoped`** |
| `status_before` | **`""`**（空字符串，逐字记录原值；**不是** `null`、**不是** `review_pending`） |
| `status_before_note` | 实测：前像 47 个顶层键中**不存在** `status` 键（key absent，非空值）⇒ 状态面未设。按派单逐字记为空字符串，同时如实登记「键缺席」这一原始事实，不把缺席伪造成一个已存在的字段。 |
| `status_transition` | `"" -> accepted_scoped` |
| `status_history` | **2 条**：① `""` —— 实现者交付时状态面未设、未自签；② `accepted_scoped` —— 本落定工位转录 carrier L14 |
| `status_authority` | carrier = `reviewer_report.md` + 自算 sha + `carrier_bytes=25835` + `carrier_total_lines=194` + `carrier_encoding` + **裁决行 L14 与字节区 [1095,1110]** + `verdict_word_written_by_reviewer=ACCEPT` + `pin_sidecar`（三方一致） |
| `pre_image`（改前自算） | `29e6971f72275cef623ca2b24ecd95dc38b1ad8bbb125a96de1c7ce773c7254e` / **18710 B** / 47 顶层键 / LF-only（CR=0、LF=406） |
| 后像（改后自算） | `88e12c72621da52dac48cf446a1a4f10572fa08d68bc46740b3e13b91d1b7233` / **65590 B** / 61 顶层键 |
| 既有键零改动自证 | 剥离 14 个本次新增键后重新序列化 == 改前镜像**逐字节相同**（18710 B / `29e6971f…`）⇒ 47 个既有键名与值一字未改 |
| 未被触碰的既有值 | `role=implementer_s4`、`consistency_result=NOT_USABLE`、`level_claimed=null`、`open5_released=false`、`placeholder_params_released=false`、`accept_produced=false`、`evidence_grading_done=false`、`industry_rule_regraded=false`、`independent_reviewer_self_claimed=false`、`written_files`(14 件)、`not_done`(12 条) 等全部保持原值 |

新增顶层键（14）：`status` / `status_before` / `status_before_note` / `status_transition` / `status_history` / `status_authority` / `carried_findings` / `reviewer_resolved_items` / `unverified` / `l165_wording_delta_attribution` / `pre_image` / `verdict_is_transcribed_not_authored` / `implementer_signed` / `bookkeeping`（47 → 61）。

`verdict_is_transcribed_not_authored = true`、`implementer_signed = false` 同时写在 `handoff.json` 与 `qualification.json`，两处相等。

---

## 4. `carried_findings` —— 逐字转录，不弱化（7 条）

来源：`reviewer_report.md` §七 分级（L133–L151）**P2×3 + P3×2**（**报告中不存在任何 P1**，§七标题即「P1 = 无 ⇒ ACCEPT」），加按派单要求强制随卡的 2 条定性（§四 G1–G7 分级判定、§五 L165 归属裁定）。
计数：`P1=0 / P2=3 / P3=2 / 编号发现 5 条 + 强制定性 2 条 = 7 条`。全部 `landing_state = carried（未销项）`，本落定不改级、不销项。


### P2-1 · P2 —— `reviewer_report.md` L137–L139，字节区 `[17876, 19009]`，长 1134，sha `e4fd10b8fc41906d87bbc5bffb7d1986933d5a39b7e234197134108f8fdc9b18`

**处置（转录，不改级）**：逐字随卡移交：`s4_report.md` L66 那一格 sha 不可用于核验交付文件；机器可读登记（handoff / dual_path_verify）正确、结论不受影响。复审明示『应在 S5 消费前补记，本复审工位不代改』⇒ 由本卡/父补记。

**`landing_state`**：carried（未销项；本落定不改级、不弱化、不处置）

**复审原文（逐字）**：

```text
1. **P2-1 · `s4_report.md` L66 的 sha 与交付文件不符**：§1.0 表第 5 行写 `attempt08 pdfminer | 我的 sha256 = 6f29f209…`，但 `_work/extract/s4_attempt08_pdfminer.extracted.txt` 的**实际 sha = `c55dc630dc4390b15a9f6dfed3bb7d174377cfd3849aad4d7463903637821f88` / 1,016,147 B**（`handoff.json:written_files` 与 `dual_path_verify.json:fresh_extraction_new.sub08_pdfminer` **都登记为 `c55dc630…`，且与盘上字节相符**）。`6f29f209` 在本卡产物中**只出现这一次**，不对应任何已登记产物。
   - **我的交叉证据**：我**独立重跑**同方法（`extract_pages` + `LTTextContainer` + `<<<PAGE n>>>\n`）得到的文本 sha **恰好 = `6f29f209…`**（1,016,147 B，与交付文件同长）；与交付文件**仅在 p243 附近一处文本块排序上差 1,616 个字符**（`ndiff=1616`，CR 均为 0），**锚词结果完全不受影响**（中 0/5、英 5/5、`pdfminer-only = ∅` 与我的 run 一致）。
   - 影响：**报告表格里这一格 sha 不可用于核验交付文件**；机器可读登记（handoff / dual_path_verify）正确，结论不受影响。
```

### P2-2 · P2 —— `reviewer_report.md` L141–L144，字节区 `[19011, 19913]`，长 903，sha `592a84cf5b4d9e2f4dff764fedfbc5b4c1dd4a3be8224cf836a30471b0acc6c4`

**处置（转录，不改级）**：逐字随卡移交：「101 个落盘文件」实为 51 个文件的 101 条登记，且存在证据范围外推；复审同时记录『实质结论仍然成立』。计数口径须在 S5 消费前更正。

**`landing_state`**：carried（未销项；本落定不改级、不弱化、不处置）

**复审原文（逐字）**：

```text
2. **P2-2 · 「101 个落盘文件」计数失实 + 证据范围外推**：
   - 我实测：**101 条登记 = 51 个不同文件**（`20 个 ocr_text ×3 种路径写法`、`10 个 renders ×2`、`21 个 ×1`；去重直方图 `1×21 / 2×10 / 3×20`），且**101 条路径全部位于 S3 attempt 目录内**。
   - 因此 `s4_report.md §1.0 / §五-1` 与 `handoff.json:s3_s1_bytes_evidence = "101 files re-hashed"` 的**"101 个文件"表述不实**（实为 51 个文件的 101 条登记），且用它**外推自证"未改 S1 两站、封盘 I-11-A"超出其覆盖范围**。
   - **实质结论仍然成立**（我独立佐证）：51 个 S3 文件全部与 S3 自身登记相等；`attempt04/attempt08` 与 oracle 期望 sha 相等；**封盘 `I-11-A` 已被 git 跟踪（`git ls-files` = 103 个），我复跑 `git diff HEAD --name-only` 中 `I-11-A / S3 / PEND5A / PEND5B` 命中 = 0**。
```

### P2-3 · P2 —— `reviewer_report.md` L146–L146，字节区 `[19915, 20275]`，长 361，sha `fcdd127082f69c7a095311a9c16daa0570be50f3b81e78cc36cc39db9ed2d31f`

**处置（转录，不改级）**：逐字随卡移交：provenance 缺项清单漏报第 8 项（16/26 条缺 page，含三份 PDF 输入件）；S5 引用前应补 G8。

**`landing_state`**：carried（未销项；本落定不改级、不弱化、不处置）

**复审原文（逐字）**：

```text
3. **P2-3 · provenance 缺项清单漏报第 8 项**：G1–G7 未覆盖 `oracle §5.4 P2 (page / whole_document)` —— **16/26 条缺 `page`**（含 `in-01/02/03` 三份 PDF 输入件）；`in-01/02/03` 同时缺 P3 锚文本（只有通配 note）。清单以「缺项如下」呈现 ⇒ **完备性表述过头**，S5 引用前应补 G8（见 §四）。
```

### P3-1 · P3 —— `reviewer_report.md` L150–L150，字节区 `[20312, 20539]`，长 228，sha `7a99c729165b8e027192b316b49146b7eaccd116bee0299ec822d2ecec013c15`

**处置（转录，不改级）**：逐字随卡移交：G1 分级偏重（复审判 medium 而非 hard）；保守方向不构成风险，仅登记口径差异。

**`landing_state`**：carried（未销项；本落定不改级、不弱化、不处置）

**复审原文（逐字）**：

```text
4. **P3-1 · G1 分级偏重**：`counts` 字段不自洽属实，但属汇总字段缺陷（26 条条目均完整可定位），我判 **medium** 而非 hard。保守方向（更严）不构成风险，仅登记口径差异。
```

### P3-2 · P3 —— `reviewer_report.md` L151–L151，字节区 `[20540, 20965]`，长 426，sha `b6135a4c4597677a8f40d6d8d77947b6f2846fe1294e6610307aa65260f57755`

**处置（转录，不改级）**：逐字随卡移交：两处口径未写明（两库总字符基数不同 / G6 的 32 未写明排除项）；均不影响任何锚词与一致性结论。

**`landing_state`**：carried（未销项；本落定不改级、不弱化、不处置）

**复审原文（逐字）**：

```text
5. **P3-2 · 两处口径未写明**：(a) `§1.2` 两库「总字符」基数不同 —— fitz `295,785`（**含 415 个 `<<<PAGE n>>>` 标记**，我复算 `289,668 + 5,702 + 415 = 295,785`）vs pypdfium2 `298,151`（**不含标记**，我复算同值）；(b) G6 的 `32` 未写明其已排除 `provenance.json`/`handoff.json` 自身与 2 个 manifest（我数为 36）。两者均不影响任何锚词/一致性结论。
```

### G1-G7-GRADING · qualification_of_provenance_gaps —— `reviewer_report.md` L94–L101，字节区 `[12101, 14997]`，长 2897，sha `5e0b1cd91248e791e19910e3a4a74e972dea918bda047d0ac60a50f81c15d1a1`

**处置（转录，不改级）**：复审对 7 项 provenance 缺项 G1–G7 的分级判定 + 漏报第 8 项，逐字转录：G2/G3=hard 恰当、G4/G5/G6=medium 恰当、G7=low 恰当、G1=hard→改判 medium（偏重）、第 8 项应补记为 G8（medium）+ G9（P3）。本落定不改判。

**`landing_state`**：carried（未销项；本落定不改级、不弱化、不处置）

**复审原文（逐字）**：

```text
| **G1** `counts` vs `entry_count` | hard | **medium（偏重，P3-1）** | 属实：`counts 4+10+4=18` ≠ `entry_count 26`（我点算 by kind：`authorization 4 / capability_report 1 / acquisition_report 1 / origin_file 1 / substitute_file 2 / ocr_engine_env 1 / ocr_page_render 10 / probe_or_deliverable 6 = 26`）。但 26 条**条目本身可定位、sha/utc 齐**，仅汇总字段不自洽 ⇒ 不影响任何一条证据的可用性 |
| **G2** 外部件无 URL | hard | **hard ✓ 恰当** | 我核 `in-02/in-03` 确无 `url` 字段，只有 `retrieval_method` 站点名；IND C 表 ④ 要求 **URL+取回 UTC+sha256 三件齐**，缺 URL 即不得按 ④ 引用 |
| **G3** `external_retrieval_not_local=false` | hard | **hard ✓ 恰当** | 与 IND C 表 ④ 及 OPEN-11 L360「所有 `EXT-*` 一律标 `external_retrieval_not_local`」直接冲突；S4 自己按 ④ 标 `true` 并登记分歧、两边不回改 —— 处置正确 |
| **G4** origin 无 URL / `utc=n/a_local_bytes` | medium | **medium ✓ 恰当** | 我回源产品仓 sidecar `<pdf>.source.json`：确有 `source_url=https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800527_c.pdf`、`retrieved_at=2026-09-19T04:52:10Z`、`content_sha256=ffd73376…` ⇒ "可回源补齐而未补"属实；且 `oracle §5.4 P4` 明许 `n/a_local_bytes`（须标未证实）⇒ 不升 hard |
| **G5** auth-01..04 无 sha / auth-04 `note=verbatim` | medium | **medium ✓ 恰当** | 我核 4 条确无 `sha256`（缺 sha 的恰是 `auth-01..04 + in-04 = 5` 条）；`auth-04` 的 `quote` 含 **S4/S3 自己的澄清语**（`→ 澄清「两项都要…」`）⇒ **确非逐字**，标注失实；auth-01..03 的 note 带 L227-L228/L164/L179 行号，auth-04 无行号 |
| **G6** 32 个盘上文件未进 provenance | medium | **medium ✓ 恰当（附口径说明，P3-2）** | 我独立遍历：S3 目录 52 个文件，**36 个**不在 `provenance.json` 条目内（其列出的 32 = 36 − `provenance.json`/`handoff.json` 自身 − `manifest_before/after.json`）；列出的 32 项**条目名全部属实**，但**总数未写明被排除的 4 个** |
| **G7** in-04 venv 无 sha/manifest | low | **low ✓ 恰当** | 且被审卡**如实标"本工位未独立复算 ⇒ 未证实"**，未造绿样 |
| **第 8 项（漏报）** | 未登记 | **应补记为 G8（medium）** | `oracle §5.4 P2` 要求每条带 `page`（或明确 `whole_document`）：我点算 **16/26 条缺 `page`**（`auth-01..06`、`in-01..04`、`out-reacquisition.json`、`out-reacquisition_report.md`、`out-oracle.md`、`out-pathA_probe.json`、`out-pathB_probe.json`、`out-path_compare.json`），**其中 `in-01/02/03` 是三份 PDF 输入件**。附带：`in-01/02/03` 也**只有 note、无 P3 锚文本**（P3 要求可定位到行/字节区）⇒ 建议 G8（P2/page）+ G9（P3/输入件锚文本，可并入 G8）一并交 S5 |
```

### L165-WORDING-DELTA · attribution_of_L165_wording_delta —— `reviewer_report.md` L107–L113，字节区 `[15051, 16129]`，长 1079，sha `e430ca0ed9b16e62dc9148656f860552057d4d2117fdc3d79999c11f885f8608`

**处置（转录，不改级）**：复审对 L165 措辞差的归属裁定，逐字转录（照原文，见 handoff/review 的 §L165 段）：不是工位找茬；『父的错』方向合理但不可考（记 unverified）；对 S4 交付不扣分。

**`landing_state`**：carried（未销项；本落定不改级、不弱化、不处置）

**复审原文（逐字）**：

```text
- **L165 原文（我逐字回源）**：`… | 实现者 + 独立 reviewer | S1/S3 授权 | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |`。
- **被审卡三处引用**（`oracle.md §1`、`s4_report.md §授权`、`handoff.json:authorized_by.S4_definition_verbatim.quote`）**与原文逐字一致** ✓。
- **「派单转述 = 该来源不可用」**：我在 `execution_runs/**`（`*.md` / `*.json`）、计划根 `*.md`、`execution_v2/dispatch.json` 全盘搜索，**该措辞除被审卡自己的勘误处外 0 命中** ⇒ 派单原文**无落盘记录**。
- **判定**：
  1. 这**不是工位找茬** —— 工位做的是「以文件原文为准执行 + 显式登记转述差」，正是本计划反复要求的回源纪律；且两者**处置同向**（该来源不得引用 + 维持不可读）。
  2. 「**父的错**」这一归属：**方向合理但不可考（记 unverified）** —— 盘上没有派单文本可比对；能确证的只有 **L165 原文与 S4 引用一致**。
  3. 对 S4 交付**不扣分**（不计缺陷）。
```


---

## 5. `reviewer_resolved_items` —— 复审**已下定性**的 4 项（原文，本工位只复述、不自出定性）


### ① `consistency_result = NOT_USABLE` 是否成立（3 处 `numeric_conflict` 的复算结果） —— reviewer_report.md §一/§二/§三/§六（L25–L25）

- 定位：`reviewer_report.md` L25–L25，字节区 `[1734, 2525]`，长 792，sha `b97bef47d57a5312dce9b266b8210da9929641806d13cdd00a36ab7c2d293c99`
- **复审定性（转录）**：**成立**：复审独立重抽 origin 10 张抽样页文字层并自写 digit_tokens 复算，`numeric_conflict = 3` 逐条全中；pdfium/fitz 两变体同样 3 处；M1 头条 92/1/1、A 锚词 5/5、可读区覆盖 0.380952 与被审卡逐位相同；U2/U3 = CONSISTENT 依 oracle §5.1 复核成立 ⇒ 总值 NOT_USABLE（§5.2 任一面 NOT_USABLE）。fail-closed 的合格产出、不是缺陷。

**复审原文（逐字）**：

```text
| **1** | `consistency_result = NOT_USABLE` 是否成立 | 在 `%TEMP%` 副本内：`pypdfium2 4.30.0` + `PyMuPDF 1.26.7` **各自重抽** origin 10 张抽样页文字层；对 S3 落盘 OCR 文本（先验 sha）用**我自己写的** `digit_tokens`（`\d+(?:[,.]\d+)*` → 纯数字串，≥3 位入集合）独立算 `D_ocr \ D_origin`（≥5 位计矛盾），并**按字节回读原文件核对 byte window** | **`numeric_conflict = 3`（逐条复算全中，见 §二）**；两变体（pdfium / fitz 文字层）**同样 3 处**；M1 头条 `92 / 1 / 1`、A 锚词 `5/5`、可读区覆盖 `112/173/9 = 294 → 0.380952` **与其实测逐位相同**；U2/U3 = `CONSISTENT` 依 `oracle §5.1` 条件复核成立 ⇒ 总值 `NOT_USABLE`（`§5.2` 任一面 `NOT_USABLE`） | **成立** |
```

**判级依据 L16–L17（逐字）**：

```text
> 判级依据：**未发现 P1**。核心产出（`consistency_result = NOT_USABLE`）经我独立复算**成立**，是 fail-closed 的**合格产出、不是缺陷**；与 S3 数字**逐项全等**；三个新增面我各跑一遍**全部复现**；**未发现任何越权**。
> 下列 **P2×3 / P3×2** 均为「报告文本/计数/清单完备性」层面的缺陷，不改变任何结论，可在 S5 消费前由本卡补记（**复审工位不代改**）。
```

**§二 复算（L37–L49）（逐字）**：

```text
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
```

### ② 与 S3 数字的一致性 —— reviewer_report.md §一/§二/§三/§六（L26–L26）

- 定位：`reviewer_report.md` L26–L26，字节区 `[2526, 3118]`，长 593，sha `ef2655cf1b9f0963ff7bd0782a99bbbe81a1e14508b288b5cfb7b8384714ad4a`
- **复审定性（转录）**：**全等**：复审读 S3 原始登记并独立重算逐项对表（未采信被审卡的 diffs_vs_s3），M1 92/1/1、封面 1、A 5/5、B1 415 页 0/5、M2 逐锚词两库逐页命中集合、首现行跨库 4、pdfminer-only = ∅、B2′ 0/5 与 5/5 全部相等；唯一『差』是口径差（见 P3-2）。另 §一 第 3 项（L27）：101 条登记全部 recompute == recorded == actual、missing=0，但 101 条只覆盖 51 个不同文件（见 P2-2）。

**复审原文（逐字）**：

```text
| **2** | 与 S3 数字是否真一致 | 读 S3 `_work/path_compare.json` + `reacquisition.json` **原始登记**，与我的独立重算逐项对表（未采信被审卡的 `diffs_vs_s3`） | M1 `92/1/1`、封面 `1`、A `5/5`、B1 `415 页 / 0/5`、M2 逐锚词 fitz/pdfminer 逐页命中集合 `5=5 / 28=28 / 0=0 / 23=23 / 19=19` 与 `5=5 / 13=13 / 0=0 / 13=13 / 9=9`、首现行跨库 `4`、`pdfminer-only = ∅`、B2′ 中 `0/5`、英 `5/5`（词级）+ 5 个英文首现行页码逐条相同（p7/p8/p112/p10/p8）**全部相等** | **全等**（唯一"差"是口径差，见 P3-2） |
```

**§一 第 3 行（L27，S3 登记 sha 抽验）（逐字）**：

```text
| **3** | S3 登记文件 sha 是否真全等 | 对 `raw_measurements.json:s3_artifact_integrity.detail` 的**每一条**重算 sha256；并把 S3 **自己的登记源**（`handoff.json:written_files`、`path_compare.json` 逐件 sha）拿来交叉比对 | **101 条登记全部 `recompute == recorded == actual`，`missing=0`**；其中 **50 条**同时与 S3 自身登记值相等；**但 101 条只覆盖 51 个不同落盘文件**（路径写法重复，见 P2-2） | **全等（计数口径有误，见 P2-2）** |
```

**§3.1 与 S3 逐项（L55–L68）（逐字）**：

```text
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
```

### ③ 三个新面是否站得住 —— reviewer_report.md §一/§二/§三/§六（L28–L28）

- 定位：`reviewer_report.md` L28–L28，字节区 `[3639, 4165]`，长 527，sha `373c590aa6cb23c755cd65d50c474ecb50e801f65074bfbd67de540584793b68`
- **复审定性（转录）**：**三面全部复现**：① 数字两路比对 = 3 处矛盾（复现 ✓）；② attempt08 pdfminer 全量 415 页 + 双语锚词 + 首现行跨库（中 0/5、英 5/5、跨库 5/5、pdfminer-only = ∅，复现 ✓，sha 见 P2-1）；③ pypdfium2 415 页 / 298,151 字符 / 0/5（复现 ✓）。另附 attempt04 M2 fresh 亦复现 ✓。

**复审原文（逐字）**：

```text
| **4** | 三个新增面（S3 未做）各跑一遍 | ①数字两路比对：我自己实现（10 页 ×2 文字层变体）；② `attempt08` 的 `pdfminer.six 20260107` 全量 415 页重抽 + 双语锚词 + 首现行跨库；③ `pypdfium2 4.30.0` 全量 415 页扫 B1 | ① `3` 处矛盾（同上）；② `pdfminer 415 页`、中 `0/5`、英 `5/5`、首现行跨库 `5/5`、`pdfminer-only = ∅`（fitz-only 仅 `Xiaomi p242`）；③ `415 页 / 298,151 字符 / 0/5` | **三面全部复现**（② 的 sha 见 P2-1） |
```

**§3.3 三个新面实测（L79–L86）（逐字）**：

```text
### 3.3 三个新增面的实测 raw 数

| 面 | 我的实测 | 被审卡自报 | 结论 |
|---|---|---|---|
| ① 数字两路比对 | `numeric_conflict = 3`（p30×1、p47×2）；变体 A/B 一致；覆盖 `112/173/9=294 → 0.380952` | `3`、`0.380952` | **复现 ✓** |
| ② `attempt08` pdfminer 补跑 | 415 页；中 `0/5`（0 命中页）；英 `5/5`（Xiaomi 175 页 / Revenue 14 / Annual Report 2 / Segment 7 / Gross profit 6）；首现行跨库 `5/5`；`pdfminer-only = ∅` | 中 `0/5`、英 `5/5`、首现行 `5/5`、无 pdfminer-only | **复现 ✓**（sha 见 P2-1） |
| ③ B1 第二库 pypdfium2 | 415 页 / **298,151** 字符 / 锚词命中 `0/5` | 415 / 298,151 / 0/5 | **复现 ✓** |
| （附）attempt04 M2 fresh | 词级集合相等、逐页集合与 S3 全等、首现行跨库 `4` | 4/4、集合相同 | **复现 ✓** |
```

### ④ 越权检查结论 —— reviewer_report.md §一/§二/§三/§六（L31–L31）

- 定位：`reviewer_report.md` L31–L31，字节区 `[5252, 6030]`，长 779，sha `d65ccf15778d53b1f2f4d4aa4b537a4aa226c8d7fe8956bb71afcbaf9617a5e5`
- **复审定性（转录）**：**未越权（6 项全部未犯）**：`level_claimed=null`、`releases_nothing=true`、`open5_released=false`、`placeholder_params_released=false`、`accept_produced=false`、`evidence_grading_done=false`、`industry_rule_regraded=false`、`self_reviewer_claimed=false`、`independent_reviewer=由父另派本工位不自任`、`prior_not_readable_preserved=true`、`still_not_readable_disposition=true`；正文仅有『可提交 S5 定级』提请语，无任何 S5 结论；五份计划文件 mtime 全在本卡窗口外。

**复审原文（逐字）**：

```text
| **7** | 越权检查 | 读 `handoff.json` + `dual_path_verify.json` 全部边界字段，并**到产物正文里找反证**（有无定级/重裁/解卡/放行/下 S5 结论/自任 reviewer 的痕迹） | `level_claimed=null`、`releases_nothing=true`、`open5_released=false`、`placeholder_params_released=false`、`accept_produced=false`、`evidence_grading_done=false`、`industry_rule_regraded=false`、`self_reviewer_claimed=false`、`independent_reviewer="由父另派，本工位不自任"`、`prior_not_readable_preserved=true`、`still_not_readable_disposition=true`；正文仅有「可**提交** S5 定级（本工位不定级）」的**提请语**，无任何 S5 结论；五份计划文件 mtime **全在本卡窗口外** | **未越权（6 项全部未犯）** |
```

**§六 越权检查逐项（L117–L129）（逐字）**：

```text
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
```


---

## 6. `unverified` —— 复审 §八 逐条（7 条，一条不删、一条不标「已验证」）

来源：§八（L155–L163），条目行 L157–L163，字节区 `[21032, 22419]`，长 1388，sha `58b702e30603be886160468d40f25a7795e5076737beab3ab1ccdfabf015f781`。


1. **3 处数字分歧中哪一侧等于视觉真值** —— 我**未重跑 OCR 引擎、未做像素级核字**（同被审卡口径，oracle §6.5）；我证实的是「两路读数不同」这一**字节级事实**。

2. **A 路（OCR）独立重跑** —— 全局 `rapidocr 3.8.1 / onnxruntime 1.26.0 / pypdfium2 4.30.0` ≠ S3 的 `3.9.2 / 1.30.0 / 5.13.0`，跨版本不构成同条件复现；我的 A 面数字是对 **sha 核验全等的 S3 落盘 OCR 文本**重算。

3. **派单原文措辞** —— 盘上无 S4 派单落盘记录，「派单写作『该来源不可用』」**不可考**（见 §五）。

4. **`PEND-5B` venv manifest（410 MB / 3110 文件）** —— 我**未独立复算**（与 G7 同口径，标未证实）。

5. **`git status` 类证据** —— 按纪律**禁用**，故未跟踪/未提交面的证据仅来自 `git diff HEAD --name-only` + `git ls-files` + sha 重算；**未跟踪的非 `.planning` 新增文件**无法在本纪律下穷举。

6. **`attempt08` pdfminer 两次抽取的差异成因** —— 我只确证「同长、p243 局部排序差 1,616 字符、锚词结果相同」，**未定位**被审卡两次抽取的具体代码差（其 `_work` 脚本只保留最终一版）。

7. **可读区覆盖率 38.0952%** 的分母含乱码串夹带的正常汉字（冻结定义所致）⇒ 是**下界**（与被审卡披露一致）。


---

## 7. `L165` 措辞差的归属 —— **照报告原文**

- 源：§五（L105–L113，字节区 `[15004, 16129]`，长 1126，sha `ce9104192e7c8a8f2533db678aa80355c74daac29c471aafc7e0660f15a368e4`）+ §一 第 6 行（L30，字节区 `[4637, 5251]`，长 615，sha `bad89a72604c5918199d36f3c1fea594002f3cfefdf909bec39806dc2360636e`）。
- **§五 判定原文（L111–L113）**：

```text
  1. 这**不是工位找茬** —— 工位做的是「以文件原文为准执行 + 显式登记转述差」，正是本计划反复要求的回源纪律；且两者**处置同向**（该来源不得引用 + 维持不可读）。
  2. 「**父的错**」这一归属：**方向合理但不可考（记 unverified）** —— 盘上没有派单文本可比对；能确证的只有 **L165 原文与 S4 引用一致**。
  3. 对 S4 交付**不扣分**（不计缺陷）。
```

- **§一 第 6 行「实测 / 判定」原文（L30）**：

```text
| **6** | `L165` 措辞差是谁的错 | 回源逐字读 `I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` **L165 原文**；再全盘搜「该来源不可用」的派单落盘记录 | L165 原文 = `复核不一致 ⇒ 该来源不可引用，维持不可读处置`（**S4 的三处引用与原文逐字一致**）；「该来源不可用」这一转述**在盘上无任何落盘派单记录**（仅出现在 S4 自己的勘误处） | **不是工位找茬**：按文件原文执行 + 显式登记差异 = 正确纪律；**「父的错」这一归属不可考（unverified），但两者处置同向、无后果差** |
```

**归属结论（照报告原文，我未改判、未加强）**：

1. **不是工位找茬** —— 工位做的是「以文件原文为准执行 + 显式登记转述差」，正是本计划反复要求的回源纪律；且两者处置同向（该来源不得引用 + 维持不可读）。
2. 「**父的错**」这一归属：**方向合理但不可考（记 `unverified`）** —— 盘上没有派单文本可比对（「该来源不可用」这一转述在 `execution_runs/**`（`*.md`/`*.json`）、计划根 `*.md`、`execution_v2/dispatch.json` 全盘搜索中**除被审卡自己的勘误处外 0 命中**）；能确证的只有 **L165 原文与 S4 三处引用逐字一致**。
3. 对 S4 交付**不扣分**（不计缺陷）。

⇒ 即：**既不判定「父派单转述差已被证实」，也不判定「工位找茬」；工位纪律被判为正确，父侧归属维持「不可考 / unverified」。**

---

## 8. `evidence/OPEN5-S4-DUAL-PATH-VERIFY/qualification.json`

- `formula` = **`not_applicable_with_reason`**（理由写在 `formula_reason`：本 pass 纯簿记落定，不产生任何预测/公式结果，且 granted_scope 严格限于 S4 证据与判据）
- `disclosure_adaptation` = **`unmapped`**（本落定不触碰）
- `accuracy` = **`unproven`**（本落定不触碰）
- `granted_scope`（**9 条**，严格限于 **S4 双路径复核交付的证据与判据**）：三面路径比对证据、M1 数字两路面、三个新增面实测、与 S3 的逐项一致（101 条 / 51 文件口径）、provenance G1–G7 与第 8 项、`NOT_USABLE` 复算结论、oracle 判据链时序、L165 处置事实登记、复审已写裁决本身
- `not_granted`（**12 条**，至少含以下 8 项）：
  1. **会计证据等级**（归 S5，`level_claimed = null`）
  2. **`OPEN-5` 解除**
  3. **港股 `_PLACEHOLDER` 放行**
  4. **`I-11-B` 的 ACCEPT**
  5. **S5 结论**（行业复裁 + 会计定级）
  6. **IND 行业 C 表重裁**
  7. **晋升（promotion）**
  8. **`origin` 本体的可引用性** —— `consistency_result = NOT_USABLE`，按 `ruling.md` L165「复核不一致 ⇒ 该来源不可引用，维持不可读处置」，**本落定不推翻、不放宽、不引用**
- `status_authority` 镜像、`carried_findings` 镜像、`reviewer_resolved_items` 镜像、`unverified` 镜像、`l165_wording_delta_attribution` 镜像 —— 与 `handoff.json` **逐字段相等**（`qualification` 侧仅多一个 `mirror_of` 注记键）
- `verdict_is_transcribed_not_authored = true`、`implementer_signed = false`
- 文件：**58505 B** / sha `962334ba56035646b9eb436a8c9a84b7197abf82a1dc84e83f73b31146961fad`

---

## 9. 写入面与纪律自证

| # | 写入面 | 状态 |
|---|---|---|
| ① | `handoff.json`（仅状态面 + 转录追加键） | 前像 `29e6971f72275cef623ca2b24ecd95dc38b1ad8bbb125a96de1c7ce773c7254e` / 18710 B → 后像 `88e12c72621da52dac48cf446a1a4f10572fa08d68bc46740b3e13b91d1b7233` / 65590 B（JSON 重解析通过；47 既有键零改动自证通过） |
| ② | `review.md`（本文件） | **新建**（写入前 `Test-Path` = **False**，见文件头） |
| ③ | `evidence/OPEN5-S4-DUAL-PATH-VERIFY/qualification.json` | **新建**（目录一并新建；写入前 `Test-Path` = **False**） |

- `reviewer_report.md` 与 `reviewer_report.sha256`：**本 pass 写 0 字节**（收尾复哈希仍为 `643c072e…` / 25835 B 与 `58f68d08…` / 85 B）。
- 本 attempt 既有产物：`oracle.md` 14801 B · `oracle-addendum-A.md` 2649 B · `oracle-addendum-B.md` 2691 B · `dual_path_verify.json` 147718 B · `s4_report.md` 18657 B · `_work/**`（9 件）—— **收尾逐一复哈希 = `UNCHANGED`**。
- 五份计划文件：**写 0 字节**；`.planning` 之外：**写 0 字节**；零 `git` 写；**未使用 `git status`**；未联网；未跑测试；未跑任何抽取/OCR/比对脚本。
- `git diff HEAD --name-only` 非 `.planning` = **0**（落定前后各测一次，均 0）。

---

## 10. 本工位**没有做**的事

1. 没有改 `reviewer_report.md` / `reviewer_report.sha256` 任一字节（本 pass 写 0 字节）。
2. 没有改本 attempt 既有产物任一字节（`oracle.md`、`oracle-addendum-A/B.md`、`dual_path_verify.json`、`s4_report.md`、`_work/**`）。
3. 没有写五份计划文件；没有写 `.planning` 之外任何路径；没有 git 写；**没有用 `git status`**；没有联网；没有跑测试。
4. 没有产生新裁决、没有自签、没有自任 reviewer、没有代签（`implementer_signed = false`）。
5. **没有推翻 `consistency_result = NOT_USABLE`**（复审判定「成立」，本工位照转）。
6. 没有判会计证据等级（`level_claimed` 仍为 `null`）、没有解除 `OPEN-5`、没有放行港股 `_PLACEHOLDER` 参数、没有产生 `I-11-B` 的 ACCEPT、没有下 S5 结论、没有重裁 IND 行业 C 表、没有晋升。
7. 没有弱化或销项任何 P2/P3 发现（全部 `landing_state = carried`）。
8. 没有改写 `L165` 归属裁定（照报告原文转录）。
9. 没有重跑任何抽取 / OCR / 双路径比对脚本；没有对 `origin` 可引用性做任何放宽。

---

*本文件为簿记落定转录件；裁决只存在于 `reviewer_report.md` L14。本文件自身的 sha256 不在文件内自嵌（自引用不可解算），由落定工位在交付回执中报告。*
