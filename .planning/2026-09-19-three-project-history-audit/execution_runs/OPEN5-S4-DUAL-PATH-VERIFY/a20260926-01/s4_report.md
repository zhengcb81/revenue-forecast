# OPEN5-S4 · 双路径复核 + provenance —— 实现者报告

| 项 | 值 |
|---|---|
| 卡 / 步 | `OPEN-5` 恢复路径 **S4** |
| attempt | `execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/` |
| 角色 | `implementer_s4`（编排层派单的实现者）；**独立 reviewer 由父另派，本工位不自任** |
| 写入面 | 仅本目录（`.planning` 内）；`company-wiki` **只读**；零 git 写；未用 `git status`；未联网 |
| oracle | `oracle.md` `e4fa02fc…`（23:41:19Z 冻结）· `oracle-addendum-A.md` `e0cafbfdf…`（23:43:35Z）· `oracle-addendum-B.md` `9e94143f…`（23:46:09Z） |
| 测量窗口 | `2026-09-25T23:57:59Z → 23:58:45Z`（**晚于 oracle 三件，先冻结后比对 ✓**） |

## 授权（逐字回源）

- **`ruling.md` L165（S4 定义，逐字）**：
  > `| **S4** | **双路径复核 + provenance**：两条独立取文路径互证（承 P1/P2 精神），登记文件 sha256、页码/锚文本、取回 UTC；外部件按 IND C 表 **④** 标 `external_retrieval_not_local`、**永不冒充本地** | 实现者 + 独立 reviewer | S1/S3 授权 | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |`
- ⚠️ **回源勘误**：派单转述的失败分支为「该来源**不可用**」，`ruling.md` 原文为「**该来源不可引用，维持不可读处置**」。**以文件原文为准**（同族：转述改变措辞，父侧错误第 18/20 起）。
- **L166 = S5**（行业复裁 + 会计定级，受理人 = 行业 reviewer + 会计 reviewer，「本载体不代行」）→ **下一站，本工位不做**。
- **L174–179 边界**：S4/S5 走完前**仍按不可读处置**；`not_readable` 一字不改。
- **`OWNER_DECISIONS.md` §二十六 #1/#2**：#1 owner 原话「授权」（PEND-5a）、#2 owner 原话「要」→ 澄清答「两项都要」。
- **IND C 表 ④（`I11A-OPEN-IND/ruling.md` L234）**：外部抓取的港股年报 PDF → `external_retrieval_not_local`，必须登记 **URL + 取回时间 + sha256**，永不冒充本地可核。
- **OPEN-11（同文件 L360）**：「**外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`」。

---

# 零、结论速览

## `consistency_result` = **`NOT_USABLE`**

| 面 | 对象 | 比的两条路径 | 面判定 |
|---|---|---|---|
| **U1** | `HK-XIAOMI-AR2025`（origin 本体） | A(OCR 重建) ↔ B1(原文件文字层，fitz + pypdfium2 双库) | **`NOT_USABLE`** ← 触发面 |
| **U2** | `attempt04`（港交所原站 FY2025 业绩公告） | B2 fitz ↔ pdfminer | `CONSISTENT` |
| **U3** | `attempt08`（发行人官网 年报英文版） | fitz ↔ pdfminer × 中/英双语 | `CONSISTENT` |

**理由（按冻结判据，`oracle.md` §5.1/§5.2/§5.3 + addendum-A/B）**：
1. `oracle.md` §5.2 冻结：**任一面 `NOT_USABLE` ⇒ 总值 `NOT_USABLE`**（就低不就高，避免事后挪动）。
2. U1 满足 `numeric_conflict = 3 > 0`（§5.1 U1 `NOT_USABLE` 行 / §5.3-1）⇒ U1 = `NOT_USABLE`。
3. 附加：origin 正文**根本没有第二条路径可互证**（B1 415 页 0/5、GID 乱码），可读区→OCR 复现覆盖率仅 **112/294 = 38.1%**，唯一逐字互证行 = **封面 1 行**。

> **按 L165 失败分支：origin 本体「不可引用、维持不可读处置」。**
> 即使 U1 判成 `CONSISTENT`，依 **L179** 在 S5 走完前仍按不可读处置 —— 本轮结论更不解除任何处置。

**分来源可用性（写清哪些可用哪些不可用）**

| 来源 | S4 结论 | 可否进 S5 |
|---|---|---|
| `HK-XIAOMI-AR2025`（origin 本体） | **不可用**（双路径复核不一致 + 正文无第二路） | **否** —— 按 L165 维持不可读 |
| `attempt04` 业绩公告 | 双库 4/4 互证成立 | **可提交 S5 定级**，但它是**外部抓取件 + 文件类型非年报**，须按 IND C 表 ①/④ 由 S5 裁（本工位不定级） |
| `attempt08` 年报英文版 | 双库英文 5/5、中文 0/5 语言面自洽 | **仅英文面可提交**；**不可**作中文原文来源 |

---

# 一、面1：双路径互证（**本工位自己跑的数**）

## 1.0 输入核验（先 sha 后用）

- 7 个受核输入（origin / attempt04 / attempt08 / path_compare / reacquisition / S3 provenance / S3 oracle）**sha256 与字节数全部全等** ⇒ `input_hashes._all_match = true`。
- 对 **S3 自己登记过的 101 个落盘文件**逐件重算 sha256：**`mismatched=[]`、`missing=[]`、`all_match=true`** ⇒ S3/S1/封盘只读纪律在本轮未被破坏（本工位一个字节没动）。
- **本工位的抽取全部重新做**（不读 S3 的 extract 结果作为输入）：
  | 抽取 | 我的 sha256 | S3 登记 sha256 | 逐字节全等 |
  |---|---|---|---|
  | origin fitz 全文（415 页） | `d628cf53…` | `d628cf53…` | **✓** |
  | attempt04 fitz（59 页） | `5d20c281…` | `5d20c281…` | **✓** |
  | attempt04 pdfminer | `d70d4996…` | `d70d4996…` | **✓** |
  | attempt08 fitz（415 页） | `990075a6…` | `990075a6…` | **✓** |
  | attempt08 pdfminer | `6f29f209…`（本工位新增） | — | — |

  ⇒ **S3 的抽取产物可从源 PDF 完全复现**（这本身是第一层互证）。

## 1.1 M1 — A（OCR 重建）↔ B1（origin 文字层），同 10 页

方法逐字承 `path_compare.json`（去空白归一化 `norm = re.sub(r"\s+","",s)`；每页 CJK≥8 的 OCR 行、上限 40 行；封面 `股份代號[^\n]{0,60}` 片段反查）。

| 指标 | **本工位实测** | S3 登记 | 差异 |
|---|---|---|---|
| 受检 OCR 行数 | **92** | 92 | 无 |
| 逐字出现在 origin 层的行 | **1**（=封面） | 1 | 无 |
| 封面片段在 OCR 中复现 | **1/10 页** | 1 | 无 |
| A 锚词命中 | **5/5**（小米 1/30/160、收入 115/337、年度報告 1/2/43/47/115/337/355/399、分部 337、毛利 337） | 5/5，同命中页 | 无 |
| B1 同页 origin 锚词 | **0/5**（10 页，两库均 0） | 0/5 | 无 |

**唯一的逐字命中行（证据）**：`page=1`，`ocr_text/s3_pathA_p0001.ocr.txt` = `股份代號：1810（港幣櫃台）及81810（人民幣櫃台）`（sha `1d46a640…`）；origin 层对应片段 `股份代號：1810（港幣櫃台）及 81810（人民幣櫃台）`（多一个空格，去空白后全等）。

**反向覆盖检查（本工位新增，先冻结于 addendum-A）**：origin 每页可读区 → OCR 复现率 **112 / 294 = 38.0952%**
（`reproduced=112`、`miss=173`、`cjk_variant=9`）。其中：
- **`miss` 的分母被 GID 乱码污染** —— 乱码串里夹带的正常汉字（U+4E00–9FFF）按冻结定义也计入可读区，故 38% 是**下界**；
- `cjk_variant` 9 条（p2/p30/p160）为读法差异，按 addendum-A #4 **单列不并入 miss**。

### ⭐ M1 的数字面比对（本工位新增，addendum-B，**是本面判 `NOT_USABLE` 的直接触发项**）

对每页把两侧 ≥3 位数字串归一化成集合；**≥5 位**的 `OCR 有、origin 无` ⇒ `numeric_conflict`：

| # | 页 | 侧 | OCR 字符串 | 行号 / 字节区 | origin 同页 | 判读 |
|---|---|---|---|---|---|---|
| 1 | **30** | ocr_only | `1,007,26139,166,303`（15 位） | **line 35，byte 1482–1501**（`s3_pathA_p0030.ocr.txt` sha `c0ed5052…`） | `1,007,261` + `39,166,303`（两个独立 token） | **分隔缺失**：两个 origin 数在 OCR 里被粘连；两个原值作为子串都在 |
| 2 | **47** | ocr_only | `1,000,001`（7 位） | **line 54，byte 775–784**，整行为 `(1,000,001m1`（`s3_pathA_p0047.ocr.txt` sha `678ac54c…`） | `1,000,000` | **转写差错**：末位 0→1，且行尾带 OCR 垃圾 `m1` |
| 3 | **47** | ocr_only | `6,000,00`（6 位） | **line 53，byte 765–773** | `6,000,000` | **转写差错**：丢一位 |

- 同页 origin 侧另有 `6,000,000 / 1,000,000 / 5,000,000` 三数（`6,000,000 = 1,000,000 + 5,000,000` 算术自洽），OCR 侧对应三数 `6,000,00 / 1,000,001 / 5,000,000` **不自洽** ⇒ 分歧侧在 OCR。
- **未做像素级核字**（本工位不重跑 OCR 引擎，oracle §6.5）⇒「哪一侧等于视觉真值」**标未证实**；但「两条路径读出不同数」这一事实已由字节区坐实。
- 其余 ~180 个数字 token **双向一致**；p355 另有 3 位级差异（`ocr_only 566/868` vs `origin_only 59990/898`），按 addendum-B「≥5 位才计矛盾」**不计入冲突**，此处如实披露。
- **两个变体交叉核验**（fresh pypdfium2 文字层 vs S3 落盘文字层）：`92 / 1 / 1 / 覆盖率 / 3` **完全相同** ⇒ 结论不依赖我用哪一份文字层。

## 1.2 B1 — origin 文字层全文（415 页，**双库独立**）

| 库 | 页数 | 总字符 | 5 锚词命中 |
|---|---|---|---|
| PyMuPDF 1.26.7（本工位新抽） | 415 | 295,785 | **0/5**（每词 0 次、0 命中页） |
| pypdfium2 4.30.0（本工位新抽） | 415 | 298,151 | **0/5** |

两库互相印证 **RC-1 根因（文字层 GID 乱码）**，与 S3 登记的 415 页 / 0/5 **一致**。

## 1.3 M2 — B2（attempt04）fitz ↔ pdfminer 跨库

| 锚词 | fitz 命中页 | pdfminer 命中页 | 交集 | pdfminer-only | 首现行跨库命中 |
|---|---|---|---|---|---|
| 小米 | 10 | 5 | 5 | **0** | ✓（双向） |
| 收入 | 28 | 13 | 13 | **0** | ✓（双向） |
| 分部 | 23 | 13 | 13 | **0** | ✓（双向） |
| 毛利 | 19 | 9 | 9 | **0** | ✓（双向） |
| 年度報告 | 0 | 0 | 0 | 0 | 不适用（两库同 0） |

- **锚词级命中集合两库相同**（对称差 = ∅）→ `4/5`（`年度報告` 两库同 0，因该件是**业绩公告**不是年报，属文件类型差异，非路径矛盾）。
- **首现行跨库搜全文命中 `4/4`**；`pdfminer-only` 页 = **0**（pdfminer 命中页 ⊆ fitz）。
- **逐页命中集合与首现行判定与 S3 `path_compare.json` 完全一致**（程序化比对 `same=true`）。
- ⇒ **U2 = `CONSISTENT`**。

## 1.4 M2′ — B2′（attempt08）双库 × 双语（**S3 未跑 pdfminer，本工位补跑**）

| 语种 | fitz | pdfminer | 结论 |
|---|---|---|---|
| 中文 5 锚词 | **0/5** | **0/5** | 两库同 0 ⇒ 语言面自洽 |
| 英文 5 锚词 | **5/5**（Xiaomi/Revenue/Annual Report/Segment/Gross profit） | **5/5** | 两库同 5，首现行跨库 **5/5**，无 pdfminer-only 页 |

⇒ **U3 = `CONSISTENT`**；**中文 0/5 ⇒ 该件不可作中文原文来源**。

---

# 二、面2：provenance 完整性（逐条核 S3）

判据 = `oracle.md` §5.4 的 **P1 sha256 / P2 页码 / P3 锚文本 / P4 取回 UTC / P5（外部件 ④：URL+取回时间+sha256+外部标记）**。

**S3 `provenance.json` 总体**：26 条；**P4（utc）零缺失** ✓；renders 10 条 P1+P2+P3 齐 ✓。缺项如下（**只登记，不代填、不回改**）：

| # | 严重度 | 条目 | 缺了什么 |
|---|---|---|---|
| **G1** | hard | `counts` vs `entry_count` | `entry_count=26` 但 `counts` 合计 **18**（`inputs 4 + ocr_page_renders 10 + deliverables 4`）；实际 `probe_or_deliverable` 有 **6** 条 ⇒ **counts 字段不自洽** |
| **G2** | hard | `in-02` / `in-03`（两件外部件） | **无 URL** —— 只有站点名（`direct_from_origin_site_www1.hkexnews.hk` / `direct_from_issuer_site_ir.mi.com`）。④ 要求 **URL + 取回时间 + sha256**；URL 只存在于 PEND-5a `provenance.json` ext-04 / ext-08 |
| **G3** | hard | `in-02` / `in-03` 的 `external_retrieval_not_local = false` | 与 **IND C 表 ④** 及 **OPEN-11 L360**「所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`」**语义冲突**。S3 沿用 PEND-5a 的口径（`false` = 非第三方代理）。S3 已带 `substitute_not_origin=true`（不冒充 origin）✓，但**未按 ④ 标外部身份** ⇒ **未完全满足「永不冒充本地」** |
| **G4** | medium | `in-01`（origin） | `utc="n/a_local_bytes"`、无 URL；**可回源补齐而未补** —— 产品仓 sidecar `<file>.source.json` 明载 `source_url=https://www1.hkexnews.hk/…/2026042800527_c.pdf`、`retrieved_at=2026-09-19T04:52:10Z`、`content_sha256=ffd73376…` |
| **G5** | medium | `auth-01…auth-04` | 四条均**无 sha256**；`auth-04` 的 `note` 写 `verbatim` 但 `quote` 实为**转述摘要**（非逐字），也无行号 |
| **G6** | medium | provenance 条目覆盖面 | S3 目录内 **32 个盘上文件未进 provenance 条目**（20 个 `ocr_text/*.txt`、4 个 `extract/*.txt`、7 个 `_work/*.py`、1 个 `_shim/sitecustomize.py`）；它们的 sha 只在 `handoff.json:written_files` ⇒ **provenance.json 内不构成完整证据链** |
| **G7** | low | `in-04`（OCR venv） | 无 sha256 / 无 manifest 摘要；且**本工位未独立复算 venv manifest**（410 MB / 3110 文件）⇒ 标**未证实** |

**本工位自己的 provenance（按同一标准登记，见 `dual_path_verify.json → provenance_review.own_provenance`）**

| 对象 | sha256 | 页码/锚文本 | 取回 UTC | 外部件 ④ 标记 |
|---|---|---|---|---|
| origin `HK-XIAOMI-AR2025` | `ffd73376…da7c` / 4,405,561 B | 415 页双库；抽样 10 页；锚词 0/5 | `2026-09-19T04:52:10Z`（回源 sidecar）+ URL | `false`（产品仓本地原件） |
| `attempt04` | `d0975600…9b62b` / 1,044,325 B | 59 页双库；小米/收入/分部/毛利 4/5 | `2026-09-24T22:09:26Z` + 完整 URL | **`true`**（④ + OPEN-11 L360）；`substitute_not_origin=true` |
| `attempt08` | `b787f029…75ec2` / 3,556,507 B | 415 页双库；中文 0/5、英文 5/5 | `2026-09-25T20:37:56Z` + 完整 URL | **`true`**（④ + OPEN-11 L360）；`substitute_not_origin=true` |
| 本工位产出 | 逐件 sha256+bytes 见 `handoff.json:written_files` | — | `generated_utc` | — |

> **标注分歧如实登记**：S3/PEND-5a 对两件替代件标 `external_retrieval_not_local=false`（口径 = 非第三方代理）；本工位按 **IND C 表 ④** 的语义标 `true`。**两边都不回改**，只在本工位记录中登记分歧，交由 S5/独立 reviewer 裁口径。

---

# 三、与 S3 数字的差异（**有差异必须如实登记**）

## 3.1 完全一致（本工位独立重算后）

M1 `92 / 1 / 1`、A `5/5`（同命中页）、B1 `415 页 / 0/5`、M2 词级集合与**逐页命中集合**与首现行判定（程序化比对 `same=true`）、M2 首现行跨库 `4`、B2′ 中 `0` / 英 `5` —— **全部与 S3 登记相同**。

## 3.2 有差异 / S3 未做的部分

| # | 项 | S3 | 本工位 | 性质 |
|---|---|---|---|---|
| D1 | **数字层面的两路比对** | **未做**（`path_compare.json` 无此面） | **新增，发现 `numeric_conflict = 3`** | **★ 差异且改变结论**：直接触发 U1 `NOT_USABLE` |
| D2 | attempt08 的 pdfminer | **未跑**（只跑 fitz） | 补跑，结论一致（中 0/5、英 5/5） | 新增信息，非矛盾 |
| D3 | B1 的第二库 | 只跑 fitz | 加跑 pypdfium2，同样 0/5 | 新增信息，非矛盾 |
| D4 | origin 每页文字层 | pypdfium2 **5.13.0**（PEND-5B venv） | pypdfium2 **4.30.0**（全局） | 10 页中 **4 页逐字节全等**，6 页差异**仅为数字组间空格 + 一处 `\x98`**（相似度 0.867–0.999）；**M1 头条数字两变体完全相同** |
| D5 | S3 provenance `counts` | 声明合计 18 | 实际 26、`probe_or_deliverable`=6 | **G1** |
| D6 | 派单转述 vs 文件原文 | ruling L165：「该来源**不可引用，维持不可读处置**」 | 派单转述：「该来源不可用」 | **措辞差**，已按文件原文执行 |

## 3.3 「未证实」项（不造绿样）

1. **A 路未重跑 OCR 引擎**（全局 `rapidocr 3.8.1 / onnxruntime 1.26.0 / pypdfium2 4.30.0` ≠ S3 的 `3.9.2 / 1.30.0 / 5.13.0`，跨版本不构成同条件复现）⇒ A 的数字是对 **S3 落盘 OCR 重建文本（sha 逐件核验全等）重算**得出，**不是本工位独立重跑 OCR**。
2. **未做像素级核字** ⇒ 「3 处数字分歧中哪一侧等于视觉真值」未证实。
3. **PEND-5B venv 未独立复算 manifest**（G7）。
4. 可读区覆盖率 38.1% 的分母含乱码串夹带的正常汉字（冻结定义所致）⇒ 是**下界**。

---

# 四、给 S5 的提请语

> **表已备**（`dual_path_verify.json`：逐路径、逐页、逐锚词的比对结果 + 行号/字节区证据 + provenance 缺项 G1–G7）。
> **S4 结论 = `NOT_USABLE`（触发面 = origin 本体）** ⇒ 按 `ruling.md` L165 失败分支，**`HK-XIAOMI-AR2025` origin 本体不可引用、维持不可读处置**，**不进入定级**。
> **替代件 `attempt04` / `attempt08` 的双路径互证已成立**（U2/U3 = `CONSISTENT`）⇒ **S5 请按 IND C 表 ④（外部抓取件：URL + 取回时间 + sha256，永不冒充本地；如判可按 ① 走则须显式标注文件类型与期间）+ 会计面定级补裁**；本工位**不判等级、不重裁行业处置规则**。
> **G2/G3 是 S5 引用前必须先补的 provenance 硬缺项**（外部件 URL 缺失、`external_retrieval_not_local` 口径冲突）。
> **L179 仍然压顶**：即使后续改判，S5 走完前一律仍按不可读处置；港股命题零产出、参数维持 `_PLACEHOLDER`。

---

# 五、本工位**没有做**的事（逐条）

1. **未改** S3（`OPEN5-S3-REACQUISITION/a20260925-01`）、S1 两站（`OPEN5-PEND5A`/`OPEN5-PEND5B`）、封盘 `I-11-A/a20260919-01` **任何字节** —— 101 件重算 sha 全等自证。
2. **未把** 任何 `not_readable` 改成「已验证」；**未改** `prior_not_readable` 任何字段。
3. **不判会计证据等级**：`level_claimed = null`（**S5 归行业 reviewer + 会计 reviewer**）。
4. **未重裁** IND C 表行业处置规则。
5. **未解除 `OPEN-5`**；**未放行 `_PLACEHOLDER`** 港股参数。
6. **未产生** `I-11-B` 的 `ACCEPT`；**未代签**。
7. **未自任独立 reviewer**（S4 受理人 = 实现者 + 独立 reviewer，另一半由父另派）。
8. **未写** 五份计划文件。
9. **未写** `.planning` 之外任何路径（**含 `company-wiki` 产品仓**，对 origin 只做 hash/文字层只读抽取）。
10. **零 git 写**；**未用 `git status`**；**未联网**（全部复核在盘上已完成产物之间做）。
11. **未重跑 OCR 引擎**（理由见 §3.3-1，已标未证实）。

---

# 六、纪律自检

| 项 | 结果 |
|---|---|
| oracle 先冻结后比对 | ✓ 三件 oracle 23:41/23:43/23:46Z，测量 23:57:59Z 起 |
| JSON 写后 `json.load` 重解析 | ✓ `raw_measurements.json` / `dual_path_verify.json` 均已重解析 |
| UTF-8 无 BOM、纯 LF | ✓ |
| 写入面 | 仅 `execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/` |
| `git diff HEAD --name-only` 非 `.planning` 计数 | **0**（见 `handoff.json:git_diff_non_planning`） |
| `git status` | 未使用 |
| git 写命令 | 0 |
