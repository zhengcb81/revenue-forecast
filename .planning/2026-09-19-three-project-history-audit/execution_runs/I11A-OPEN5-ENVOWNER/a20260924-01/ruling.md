# I-11-A · OPEN-5 归属裁定（环境/依赖 owner 角色）

- card：`I-11-A`（下游：`I-07-B`、`I-11-B`）
- 本载体 attempt：`execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/`
- 角色：`environment_dependency_owner`（环境/依赖 owner，I-00-B 侧）
- 被审对象（**全程只读**）：`execution_runs/I-11-A/a20260919-01/`（accepted_scoped 封盘 attempt）、`execution_v2/card_I-11-A.md`、`card_I-07-B.md`、`card_I-11-B.md`
- 前置裁定（**只读，不重裁**）：`I11A-OPEN-ACCT/a20260924-01/ruling.md`（`OPEN-5 = NOT_IN_MY_SCOPE`）、`I11A-OPEN-IND/a20260924-01/ruling.md`（归属 `BLOCKED-pending-owner`；**行业处置规则已裁**）、`I11A-OPEN-MERGE/a20260924-01/merge_ruling.md`（`OPEN-5 = OWNER_ONLY`、`NO_CONFLICT`）
- 生成时间（UTC）：2026-09-24（本地实测窗口 2026-09-24T21:0x–21:27Z）
- 本文件是**新增裁定载体**：不修改 `I-11-A` 的任何 `status`/字段、不代签、不解除任何 `BLOCKED`、不构成对 `I-11-A` 的验收。

> `does_not_claim_I11A_acceptance = true`
> `adds_no_new_domain_judgement = true`（本载体只裁「**谁负责解决可读性 + 根因 + 恢复路径**」；**不重裁行业处置规则、不给任何港股数值、不定证据等级**）

---

## ① 身份与授权链（逐字）

### 1.1 本次指派的直接授权：`OWNER_DECISIONS.md` §二十四（2026-09-24 深夜）第 **4** 行

| 列 | 原文（逐字） |
|---|---|
| # | 「**4**」 |
| 问题 | 「**`OPEN-5` 归属**（港股（小米）年报原文可读性由谁解决；两半 reviewer 均判 `BLOCKED-pending-owner`、未代裁）」 |
| **owner 选择** | 「**指定环境/依赖 owner 处理**」 |
| 执行映射 | 「授权**派环境/依赖 owner 角色**裁定该归属问题；恢复后按卡文「**新建 attempt 重新取证、不得把 `not_readable` 改成已验证**」」 |

出处：`OWNER_DECISIONS.md` **L499**（表行），节标题 **L490**：「## 二十四、【已裁定·第五批】Owner 四答（2026-09-24 深夜，选项式问答原话）」。

同节**执行纪律**（逐字，`L502`–`L504`）：

- 「**「授权」是许可不是动作**：四项均**不产生任何 ACCEPT、不解除任何 BLOCKED、不改任何 status**；`I-11-B` 仍 BLOCKED（解锁 7 条条件未满足）。」
- 「**不得把本节选择膨胀为「所有结论」**（执行纪律第 7 条）：选项 1 只解除**门读法**，不授予 `I-08-A` 载体 status 变更；**选项 2/3/4 只授权派工与取证**，裁定仍归各自 reviewer/owner 角色。」
- 「**取证（选项 3）的证据等级由会计面定，不由取证方自定**；取不到就维持 BLOCKED，**不造绿色样例**。」

⇒ **我的授权 = 派工（裁归属）+ 取证准备**；**不等于**任何 ACCEPT / 解锁 / 证据等级认定。

### 1.2 更早的两级派单（本议题的授权链上游，只读引用）

| 授权点 | 原文（逐字） | 出处 |
|---|---|---|
| owner 原话 | 「…**I-11-A OPEN-2/3/5/6 指派会计+行业 reviewer**…」 | `OWNER_DECISIONS.md` §十 **L116** |
| 执行行 | 「\| **I-11-A OPEN-2/3/5/6** \| **指派**：会计 + 行业（矿业/软件）reviewer \| 编排层按此派单；**OPEN-2/3/5/6 阻塞 I-11-B / I-07-E** \| **I-11-B / I-07-E**（待专家裁定） \|」 | §十 **L127** |
| 第二批 | 「\| 2 \| I-11-A OPEN-2/3/5/6 \| **派新 subagent** 当行业 reviewer \| 编排层创建独立行业 reviewer subagent \|」 | §十一 **L144** |
| 取文工具先例 | 「**其余全部授权** … I-11-A OPEN-1 允许 pdftotext 降级为交叉核对…」 | §十一 **L147** |

⇒ 两半专家（会计/行业）已按 §十/§十一 交付并**各自让位于 owner**：会计半区 `ACCT ruling.md` **L220**、行业半区 `IND ruling.md` **L216–L218**。合并席位判 `OWNER_ONLY`（`MERGE merge_ruling.md` **L61**、**L173**）。owner 随后以 §二十四 #4 把**归属**这一项**改派给我**（环境/依赖 owner）——这正是本载体的存在依据。

### 1.3 卡文行号（纪律来源，逐字）

| 内容 | 原文（逐字） | 出处 |
|---|---|---|
| 停止条件 | 「来源晚于as_of或原文无法核查→**STOP_EVIDENCE**」 | `execution_v2/card_I-11-A.md` **L21** |
| 只用可核验来源 | 「基期公司/分部/信息日确定；**只用可核验来源**。」 | `card_I-11-A.md` **L9** |
| 恢复规则 | 「**恢复规则**：可读性恢复后（工具或依赖变更），**新建 attempt 重新取证**；不得把本次的 `not_readable` 判定改成"已验证"。」 | `execution_runs/I-11-A/a20260919-01/decision.md` **L227–L228**（DEC-8） |
| OPEN-5 表行 | 「\| OPEN-5 \| 港股（小米）年报原文可读性由谁解决 \| 环境/依赖 owner + 行业 reviewer \| 否 \| 任何港股份部命题 + I-11-B 港股参数 \|」 | `decision.md` **L401** |
| 阻塞声明 | 「**没有任何一项阻塞本卡签收**；但 OPEN-2 / OPEN-3 / OPEN-5 / OPEN-6 **阻塞 I-11-B**，因此 I-11-B 不能在本次之后自动开工。」 | `decision.md` **L410–L411** |
| 可读性判据（HK） | 「HK：允许 P1（若支持该文件结构）或 P2（若输出中文可读）。两条都不可读 → 该 source 判 `not_readable_in_this_attempt`，其命题**不得**填入原文串，只能登记为 `unquantified / STOP_EVIDENCE`…」 | `oracle.md` **L84–L86**（O-7） |
| 不做的事 | 「不引用港股原文——原文在本 attempt 不可读；」 | `decision.md` **L419** |
| 下游恢复句 | 「恢复：保留已取得raw，只回退当前隔离变更。」＋「运行cwd必须由I-00-B绑定」 | `card_I-07-B.md` **L14** / **L1** |
| I-11-B 前提/停止 | 「I-11-A命题已批准」（**L9**）；「幅度无来源又未明确分析师假设→`STOP_CALIBRATION`」（**L20**）；「专业reviewer签署后方可进入forecast」（**L23**） | `card_I-11-B.md` |

---

## ② OPEN-5 题面原文（逐字）

**封盘 attempt 登记的题面**（`execution_runs/I-11-A/a20260919-01/decision.md` **L401**，逐字）：

> `| OPEN-5 | 港股（小米）年报原文可读性由谁解决 | 环境/依赖 owner + 行业 reviewer | 否 | 任何港股份部命题 + I-11-B 港股参数 |`

**mechanism_review 侧的展开题面**（同 attempt `evidence/I-11-A/mechanism_review.md` **L210**，逐字）：

> `| OPEN-5 | HK-XIAOMI-AR2025 的原文可读性由谁解决（对象流解析能力/离线 PDF 库/合规的外部工具） | 环境/依赖 owner（I-00-B 侧）+ 行业 reviewer | 不阻塞本卡（该来源已判 STOP_EVIDENCE）；**阻塞任何港股份部的命题与 I-11-B 的港股参数** |`

**owner 指派的题面**（`OWNER_DECISIONS.md` **L499** 问题列，逐字）：

> 「**`OPEN-5` 归属**（港股（小米）年报原文可读性由谁解决；两半 reviewer 均判 `BLOCKED-pending-owner`、未代裁）」

**行业半区已裁、本载体不重裁的处置规则题面**（`I11A-OPEN-IND/a20260924-01/ruling.md` **L214/L220**，逐字）：

> 「**裁定（行业处置 = RULING；归属 = BLOCKED-pending-owner）**」
> 「**B. 行业处置（我裁）——原文不可读期间** 1. **港股分部命题保持零产出**：`HK-XIAOMI-AR2025` 维持 `STOP_EVIDENCE / not_readable`；本次 `not_readable` 判定**不得**改写为"已验证"… 2. **I-11-B / I-07-B 的港股分部参数维持 `_PLACEHOLDER` 且不得放行**… 3. **不接受二手补位**… 4. **不接受"行业常识"补位**…」

⇒ **本载体只回答「谁负责解决可读性（+ 根因 + 恢复路径）」这一问。**

---

## ③ 归属裁定（结论 + 依据 + 可执行动作）

### 3.1 裁定（一句话）

> **RULING —— `OPEN-5` 的归属 = 环境/依赖 owner（I-00-B 侧）本角色自持主责：由环境/依赖 owner 负责「可读性修复路径的选型、向上申请执行授权、能力落地与取证环境编排」。工具维护者不承担该归属；filing-fetch / HK 市场工具是候选「手段」而非归属方（且单靠重下同一 URL 不产生可读性）；I-07-B 卡侧只是需求提出方/消费方，不拥有环境能力。归属本身不判 BLOCKED；两条真正动网/动依赖的执行子步判 `PENDING_HIGHER_AUTHORIZATION`（fail-closed，本载体不执行、不预授权）。**

### 3.2 逐个候选的裁定与本地依据

| 候选归属 | 裁定 | 依据（本地可核） | 可执行动作 |
|---|---|---|---|
| **环境/依赖 owner 自己（本角色）** | ✅ **主责归属** | ① `decision.md` **L401** 与 `mechanism_review.md` **L210** 本来就写「环境/依赖 owner（I-00-B 侧）」；② §二十四 #4 由 owner 明文「指定环境/依赖 owner 处理」；③ 实测证明**根因同时落在"文件层无映射"与"环境层取文能力准入"两处**，两者都在 env/dep 域：attempt 隔离 venv **零 PDF 库**、装库需网=禁网、全局解释器有库但被卡规则禁止（`tools/pdf_text.py` **L5–L9** 逐字：「The attempt's isolated venv has no PDF library and installing one needs the network, which is forbidden. The global Miniconda interpreter has PyMuPDF but card rules forbid running cards on the global interpreter.」）——**这条准入边界正是 I-00-B 绑定的产物** | 本载体 §⑤ 给出分步恢复路径；由本角色持有选型与授权申请 |
| **指派工具维护者（`tools/pdf_text.py` 作者）** | ❌ **不承担归属**（不硬指派） | ① 工具**按声明范围工作**：`pdf_text.py` **L17–L18** 明写不做「CID fonts without ToUnicode」，而实测 body 字体恰是 Type0/Identity-H 且**无 ToUnicode**（§④ 探针 F）；② **换工具不是根因修复**：本机 6 条独立取文路径（stdlib / Xpdf pdftotext / MuPDF / pypdf / pdfminer / pypdfium2）对 body 文本**同样乱码**（§④ A/B/C/E）⇒ 修工具无法凭空造出文档里不存在的码→Unicode 映射 | 只登记 **2 条非本载体交付的工具侧改进建议**（不改文件）：(a) 0 字符时仍 `rc=0` 的 fail-open 行为应改为显式失败/告警；(b) 对「Type0 无 ToUnicode」给出可读的能力边界错误串 |
| **走 filing-fetch 的 HK 市场工具（dayu-hkex-cli）** | ⚠️ **不是归属方，是候选手段 A**（且需授权） | ① 本地 sidecar 逐字：`"source_url":"https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800527_c.pdf"`、`"content_sha256":"ffd73376…"`、`"adapter_name":"dayu-hkex-cli"` ⇒ 现有文件**就是该工具取回的原字节**；② filing-fetch 是 **reuse-first**（重复请求不再下载）⇒ **重跑只会复用同一份不可读字节**，不改变内嵌字体映射；③ 只有当它能取到**另一种可读形态**（HTML / 其它渲染 / 同期间公告）时才有用 —— 那是**联网取证**，须 owner 另行授权（§二十四 #3 的授权形态与「取证产物只落本计划目录内」的先例） | 作为 §⑤ **路径 A**；本载体**不执行联网**，只提出授权请求 |
| **由 I-07-B 卡侧提出需求** | ❌ **不是归属方**，但**是需求登记点** | `card_I-07-B.md` **L1**「运行cwd必须由I-00-B绑定」、**L14**「恢复：保留已取得raw，只回退当前隔离变更」—— 卡侧消费来源链、**不拥有环境能力**；`decision.md` **L225**「I-07-B/I-11-B 若需要港股分部参数，必须先解决 OPEN-5」 | I-07-B 侧把「需要港股可读原文」登记为**需求**，由 env/dep owner 汇总进授权申请 |

### 3.3 需要更高层级授权的部分（fail-closed，**不硬指派**）

| id | 内容 | 缺什么 | 交给谁 |
|---|---|---|---|
| **PEND-5a** | 路径 A（联网取可读替代件：同发行人同期间可读原文 / HKEX 公告） | owner 对**网络取文**的明文授权（形态参照 §二十四 #3：URL+UTC+sha256+逐字引文、产物只落本计划目录） | PLAN owner |
| **PEND-5b** | 路径 B（本地 OCR：渲染已实测可用，但 OCR 引擎缺失） | owner 对**依赖安装**（离线包/安装源）与安装位置（隔离 venv vs 全局）的明文授权 | PLAN owner + 环境/依赖 owner 执行 |
| **PEND-5c** | 恢复后**证据等级**认定 | 会计面（行业面 C 表①/②/④分级已由 IND 裁好，等级仍归会计） | 会计 reviewer（本载体不代行） |

> 说明：**归属**这一问不需要更高层级决定（owner 已在 §二十四 #4 指定给我）⇒ 本条**不**判 `BLOCKED-pending-higher-owner`；判 `PENDING_HIGHER_AUTHORIZATION` 的是**执行子步**，在授权到位前一律不动。

### 3.4 归属裁定的反例（什么会推翻它）

- owner 另行明文把 OPEN-5 归属改派给别的角色（须追加登记于 `OWNER_DECISIONS.md`）；
- 实测发现**本地已存在**含正确 ToUnicode 的同期间小米原文（本轮扫描**未发现**，§④ 探针 J）⇒ 归属不变，但恢复路径直接落到"复用本地可读件"，授权需求从 PEND-5a/5b 降级为零；
- 若后续证明乱码**可**由既有本地库修正（例如存在未被本探测覆盖的解码开关）⇒ 3.2 第 2 行"换工具不是根因"的论据被推翻，须以新实测追加登记。

---

## ④ 根因本地实测（命令 + rc + 观测）

**样本**：盘上**有** `HK-XIAOMI-AR2025` 本尊样本，非「无样本可测」。

- 路径：`C:\Users\郑曾波\Projects\company-wiki\companies\小米集團－Ｗ\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf`
- `sha256 = ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c`，`bytes = 4,405,561`（与 sidecar `content_sha256` 一致）
- 另有同字节副本若干（`execution_runs/I-02-C/…/小米集團－Ｗ/…` 等，均 4,405,561 B）

**约束**：只读、禁网；临时输出文件写在本目录内、**取证后已删除**（写入面 = 恰好 3 个文件），其 hash 见 `provenance.json` 条目 `tmp-01..tmp-04`。

| # | 命令（逐字） | rc | 观测（逐字/可复核） |
|---|---|---|---|
| **A** | `python -B -X utf8 <attempt>\tools\pdf_text.py <XIAOMI.pdf> 1,2,3 <out.json>` | **0** | stdout：`page 1 (obj 1): 0 chars` / `page 2 (obj 5): 0 chars` / `page 3 (obj 9): 0 chars`；输出 JSON `classic_pages = 415`；**无错误串**（0 字符仍 `rc=0`） |
| **A2** | 同上，页 `10,20,44` | **0** | `page 10 (obj 31): 0 chars` / `page 20 (obj 61): 0 chars` / `page 44 (obj 133): 0 chars` |
| **B** | `pdftotext.exe -f 1 -l 3 -enc UTF-8 <XIAOMI.pdf> out.txt` | **0** | 1,586 B；首行可读（`股份代號：1810（港幣櫃台）及 81810（人民幣櫃台）`），其后全为 Adobe-CNS1 风格乱码；`contains 小米=False`、`收入=False`、`年度報告=False`、`ANNUAL=False` |
| **B2** | `pdftotext.exe -f 40 -l 46 -enc UTF-8 <XIAOMI.pdf> out.txt` | **0** | 13,557 B；**全段乱码**，`contains 收入=False`、`分部=False` |
| **C** | 全局 `python`（3.13.9/Anaconda）+ **PyMuPDF 1.26.7 / pypdf 6.16.2 / pdfminer.six 20260107** 分别取第 1 页 | 均 **0** | `PyMuPDF pages=415 page1_chars=36`（可读：`股份代號：1810…`）；`pypdf page1_chars=35`；`pdfminer page1_chars=39` ⇒ **只有封面那一小段可读** |
| **C2** | PyMuPDF 扫描第 1–80 页并检索锚词 | 0 | `total_chars=60401`；`小米/收入/分部/年度報告/智能手機/物聯網 → 各 0 页命中`；最密页 53 = 2,119 chars，内容为乱码（`2025⸶\u2e68⟳␌ …`） |
| **D** | PyMuPDF `get_fonts(full=True)` + `xref_object`（第 53/44/1 页） | 0 | body 字体：`basefont=IHDOJK+HYQiHei-DZS-GBK-EUC-H enc=Identity-H type=Type0 tounicode_in_obj=False`、`IHEDBB+HYQiHei-FZS-GBK-EUC-H`、`IHEDCC+HYQiHei-EZS-GBK-EUC-H` 同样 `tounicode_in_obj=False`；**仅封面** `XPGUND+HYQiHei-EES tounicode_in_obj=True` ⇒ 与「全文件仅 1 个 `/ToUnicode`」（`mechanism_review.md` **L137**）一致 |
| **E** | `pypdfium2 4.30.0` 取第 53 页 | 0 | `page53_chars=2167`、`has_shouru=False`、`has_xiaomi=False`，乱码与 MuPDF 同族 |
| **F** | PyMuPDF `extract_font(xref=1831)` + 解析 TrueType 表目录 | 0 | `IHDOJK+HYQiHei-DZS-GBK-EUC-H ttf 679,508 B`；`font tables: ['OS/2','glyf','head','hhea','hmtx','loca','maxp','name','prep']` ⇒ **`cmap` 表缺失**（**无** 码→Unicode 映射可恢复）；`fontTools` 未安装 |
| **G** | PyMuPDF `page.get_pixmap(dpi=150)`（内存渲染，未落盘） | 0 | `pixmap 1241 x 1684 samples_bytes=6269532 format_ok=True` ⇒ **渲染通道完好**（OCR 路径在"出图"这一步可行） |
| **H** | PyMuPDF 扫描**全部 415 页**检索锚词 | 0 | `pages=415 total_chars=289668 cjk_chars=55698`；`小米/收入/年度報告/分部/物聯網/智能手機 → 全部 pages_with_hit=0` ⇒ **全篇无一处正确解码的正文中文** |
| **I** | 依赖盘点：`Get-Command` / `importlib.util.find_spec` / `pip list` | 0 | **隔离 venv**（`I-11-A/a20260919-01/iso/venv`）：`fitz/pypdf/pdfminer/pdfplumber/pdftext/pypdfium2 → 全部 absent`；**全局解释器**：`PyMuPDF 1.26.7 / pypdf 6.16.2 / pdfminer.six 20260107 / pdfplumber 0.11.8 / pypdfium2 4.30.0 / pdftext 0.6.3`；**外部工具**：`tesseract / mutool / pdftoppm / gs / magick / qpdf / pdftk / pdftohtml / ocrmypdf → 全部 absent**；仅 `C:\Program Files\Git\mingw64\bin\pdftotext.exe`（Xpdf **4.00**）在位 |
| **J** | 盘上替代件扫描（只读） | 0 | 同期间小米**年报**仅此一份字节（各副本同为 4,405,561 B）；`companies\小米集团\raw\research\*.pdf` 为 **2018 年券商研报**（二手，IND C 表③级=仅线索）、`raw\news\*.md` 为 wiki/IR 摘要（二手）⇒ **本地不存在①/②级可读同期间原文** |

### 4.1 根因结论（两层，缺一不可）

- **RC-1（文件层，决定性）**：正文中文以 **Type0 / Identity-H 的子集 CJK 字体**排版（basefont 名含 `GBK-EUC-H`），字体字典**无 `/ToUnicode`**，且内嵌子集 TrueType **无 `cmap` 表**（探针 D/F）⇒ **文档内部根本不存在码→Unicode 映射**。任何"按映射取文"的方法（6 条路径全覆盖，探针 A/B/C/E）都只能得到 GID 当码用的乱码；封面那一个带 `/ToUnicode` 的字体可读，恰是反证。
- **RC-2（环境/准入层，决定"谁来修"）**：卡内唯一被准许的取文器是 attempt 自带的纯标准库 `tools/pdf_text.py`（隔离 venv 零 PDF 库、禁网、全局解释器被卡规则禁止 —— `pdf_text.py` **L5–L9**）；而能"绕过映射缺失"的两条真路径（**OCR**、**重新取一份可读件**）分别需要 **依赖安装** 与 **联网授权**，二者都在本角色的管辖边界**之上**、必须 owner 授权 ⇒ 这就是归属落在环境/依赖 owner 的技术根据。

> **一句否定**：**「换工具 / 装个 PDF 库」不是恢复路径**（探针 C/E 已证 5 个库同结果）；把它当方案会得到"看起来修好了"的假象 —— 按 §二十四 执行纪律「不造绿色样例」直接否决。

---

## ⑤ 恢复路径（分步：谁执行 + 需要什么授权 + 失败怎么办）

**路径选型**（本角色裁定）：**A = 重新取得同期间可读原文（首选）**；**B = 本地 OCR（备选）**；**C = 换/升级解析库（否决，见 §4.1）**；**D = 字形轮廓反查 Unicode（否决**：`fontTools` 缺失、需参考字体与高误判率，非受控手段）。

| 步 | 动作 | 谁执行 | 需要什么授权 | 失败时怎么办 |
|---|---|---|---|---|
| **S0** | **归属裁定落地**（本载体 `ruling.md`/`handoff.json`） | 环境/依赖 owner（本角色） | §二十四 #4 已给（派工 + 取证准备） | — |
| **S1** | **提交授权申请**：A 路（联网取可读替代件，走 filing-fetch/受控抓取，产物只落本计划目录，登记 URL+取回 UTC+sha256+逐字引文）与/或 B 路（安装 OCR 依赖：离线包 + 安装位置），二选一或并行；同时把 I-07-B 侧的港股可读原文需求并入同一申请 | 环境/依赖 owner 编排，PLAN owner 决断 | **PEND-5a / PEND-5b（owner 明文授权）**；参照 §二十四 #3 的授权形态 | 未获授权 ⇒ **fail-closed**：维持 `STOP_EVIDENCE / not_readable`，港股命题零产出，**不造绿色样例** |
| **S2** | **落地取文能力并自检**：先在**已知可读**样本（`CN-ZIJIN-AR2025`）上验证该路径能读出锚词，再对 HK 样本跑同一探针；登记 argv/rc/输出 hash | 环境/依赖 owner 指派的工具工位 | S1 的授权 | 自检不过（HK 仍 0 锚词）⇒ 回 S1 换路径；**不得**把"自检通过的 CN 样本"当 HK 结论 |
| **S3** | **新建 attempt 重新取证**（卡文 DEC-8 恢复规则）：在**全新 attempt** 中对 HK 原文重新取文；**封盘 attempt `I-11-A/a20260919-01` 与本次 `not_readable` 判定一律不动** | 编排层派单的实现者（新 attempt） | 编排层派单 + 独立 reviewer 复核 | 新 attempt 仍不可读 ⇒ 记 `not_readable`（新记录），**旧判定原样**，回到 S1 |
| **S4** | **双路径复核 + provenance**：两条独立取文路径互证（承 P1/P2 精神），登记文件 sha256、页码/锚文本、取回 UTC；外部件按 IND C 表 **④** 标 `external_retrieval_not_local`、**永不冒充本地** | 实现者 + 独立 reviewer | S1/S3 授权 | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |
| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | 行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） | 任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |

**步数 = 6（S0–S5）；其中需要 owner 授权的 = 2 步（S1 的 PEND-5a/PEND-5b），需要专业 reviewer 的 = 1 步（S5）。**

---

## ⑥ 与卡文纪律的一致性确认（不违反）

1. 卡文原话（`decision.md` **L227–L228**）：「可读性恢复后（工具或依赖变更），**新建 attempt 重新取证**；不得把本次的 `not_readable` 判定改成"已验证"。」
2. **本方案逐条对齐**：
   - **S3 明文要求"新建 attempt"**，恢复取证发生在**新 attempt**，本载体与封盘 attempt **都不产生任何"已验证"字样**；
   - 本载体**不写** `hypotheses.json` / `source_map.json` / `mechanism_review.md` / `handoff.json`（I-11-A 的），**不改**任何 `state`/`status`/`not_readable` 字段 —— §⑦ 的写入面自证；
   - `handoff.json` 显式带 `does_not_claim_I11A_acceptance=true`、`unlocks_nothing=true`；
   - 即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。
3. **结论：本方案不违反 DEC-8 恢复规则、不违反 O-7 判据、不违反卡停止条件（`card_I-11-A.md` L21）。**

---

## ⑦ 解锁边界（**不解除什么**）

**本裁定只解决「归属 + 根因 + 恢复路径」，以下一律不解除：**

1. **不解除** `OPEN-5` 对 `I-11-B` 港股参数的阻塞（`decision.md` **L401**、**L410–L411**）：`I-11-B` 开工仍需合并席位 §3.4 列的 7 条条件，本载体一条未动；
2. **不解除** 对 `I-07-B` 港股 case 的阻塞（`decision.md` **L225**：「必须先解决 OPEN-5」——本载体**只裁了"谁解决"，没有"已解决"**）；
3. **不解除** IND 已裁的处置规则：港股分部命题**零产出**、`HK-XIAOMI-AR2025` 维持 `STOP_EVIDENCE / not_readable`、二手稿与常识补位继续被拒、替代来源分级与"外部件永不冒充本地"继续有效；
4. **不解除** 任何两半已登记的 BLOCKED（ACCT BLOCKED-2a/2b/3a/3b/6a/6b/6c；IND BLOCKED-1…7；MERGE `BLOCKED-UNADJ-1/2`）；
5. **不新增**任何 `approved_frozen` 命题、**不放行**任何 `_PLACEHOLDER` 参数、**不认定**任何证据等级；
6. **解除的前置条件（不变，须全部满足）**：可读性真的恢复（S2 自检）→ **新 attempt 取证**（S3）→ 双路径复核与 provenance（S4）→ **会计面定级 + 行业面复裁**（S5）→ 才可能由相应 reviewer 谈解锁（**仍不由本载体**）。

---

## ⑧ provenance

- 全部条目见同目录 `provenance.json`（`id / kind / path / utc / quote / sha256`，合计 **47** 条）：
  - **本地文件引用（`kind=local_file`）30 条**：`OWNER_DECISIONS.md`（§十/§十一/§二十四）、`card_I-11-A.md`、`card_I-07-B.md`、`card_I-11-B.md`、封盘 attempt 的 `decision.md` / `oracle.md` / `review.md` / `mechanism_review.md` / `tools/pdf_text.py` / `tools/run_extraction.py`、两半 + 合并裁定、HK 样本 PDF 及其 sidecar；
  - **本地实测（`kind=local_probe`）13 条**：§④ 探针 A/A2/B/B2/C/C2/D/E/F/G/H/I/J（含命令、rc、观测串、被测对象 sha256）；
  - **临时输出（`kind=ephemeral_output`）4 条**：`tmp-01..04`，取证后已删除（写入面 = 3 文件），保留 sha256 供复算；
  - **外部来源 = 0 条**：本载体**未发起任何网络请求**。
- 本文件自身即 §⑧ 所述 3 文件之一；`handoff.json` 记录 `written_files` 的 sha256/字节。

## ⑨ 边界（自我约束核对）

1. **写入面 = 恰好 3 个文件**：`ruling.md`、`provenance.json`、`handoff.json`（均在本新目录下）；`.planning` 之外**创建/修改 = 0**；临时取证文件已删除。
2. **封盘 attempt 只读**：`execution_runs/I-11-A/a20260919-01/` 全程只读（含其 `tools/pdf_text.py` 仅被**执行**、未被修改，执行加 `-B` 禁止 pycache 落盘）。
3. **零 git 写**：未执行 `add/commit/checkout/stash/restore/reset` 任何变体；只跑只读 `git diff HEAD --name-only` / `ls-files --others`。收尾实测：`git diff HEAD` 总计 3,824 条，**非 `.planning` = 0**；untracked 非 `.planning` 46 条全部为**既有**路径（`.tmp-r41-mutation/*`、`assurance/…/plan_inputs.json.bak`），与本载体无关。
4. **零代签 / 零 status 变更 / 零解除 BLOCKED**：见 §⑦。
5. **零联网取港股原文**：本轮**未**下载、未请求 hkexnews/SEC 任何端点；对小米原文只做**本地字节**只读解析。
6. **不重裁行业处置规则**：IND 已裁的 A/B/C 三部分原样保留，本载体仅引用。
7. **JSON 写后重解析通过、UTF-8 无 BOM、纯 LF**（详见 `handoff.json.file_format`）。
