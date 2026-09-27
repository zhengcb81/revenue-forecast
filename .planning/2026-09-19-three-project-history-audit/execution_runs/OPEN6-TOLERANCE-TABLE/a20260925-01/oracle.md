# OPEN6 · 恒等式容差对照表 —— 编制 oracle（先冻结，后编制）

- 工位：`evidence_compiler`（证据编制工位，**只制表、不裁**）
- 产出目录：`execution_runs/OPEN6-TOLERANCE-TABLE/a20260925-01/`（**新建**，本工位唯一写入面）
- 载体：`I-11-A` 的 4 条 `threshold_basis = arithmetic_identity` 阈值
- 用途：为 `BLOCKED-6b` 提供**逐条对照原文舍入粒度**的证据表；**不**判定 `BLOCKED-6b` 是否可解、**不**签署任何容差值
- 生成时间（UTC）：2026-09-25T00:00Z（编制窗口以 provenance 内文件 mtime/sha 为准）

---

## ① 授权引用（逐字，回源）

| 授权点 | 原文（逐字） | 出处 |
|---|---|---|
| **C5**（MERGE 解锁条件第 5 条） | 「OPEN-6：threshold_review_status 落地 + H4 四要件补齐 + H2 基准 + 恒等式容差对照表」 | `execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` **L122**，bytes `[11330,11437)`，sha256 `b7314a22ebea453d4df6e6a93df62b993e0b179140feb67dfa0ec52b18b5878` |
| C5 的分解项（同条解锁条件的 OPEN-6 内条目） | 「4 条恒等式容差对照原文舍入粒度（BLOCKED-6b）」 | 同上 handoff.json **L108**，bytes `[9785,9857)` |
| **任务定义 `BLOCKED-6b`** | 「**BLOCKED-6b**：4 条 `arithmetic_identity` 的**容差**是否与其来源舍入粒度一致（含 ±1 USD million）—— 需逐条对照原文舍入粒度复核后签署（规则已给，值未审）」 | `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md` **L297**，bytes `[32795,33005)`，sha256 `f3040df0081f6653c0d18ac334890bf0aff12175aeacbd8e31485972bb329c2` |
| `BLOCKED-6b` 分派行 | 「BLOCKED-6b ｜ 4 条恒等式阈值的容差是否匹配披露舍入粒度 ｜ 逐条对照原文舍入粒度 ｜ 会计 reviewer（我）在拿到对照表后补裁 / 行业 reviewer 会签」 | 同上 ruling.md **L323**，bytes `[35734,35923)` |
| 编表判据（A-6.2 第 1 行） | 「`arithmetic_identity` ｜ 4（`hypotheses.json` L88 / L311 / L524 / L649） ｜ **可用**（等式判定） ｜ 舍入容差必须**显式**且**不超过来源披露的舍入粒度**（如"允许 \|差\| ≤ 1 元"对应元位披露），容差依据须写明；不得自由放大」 | 同上 ruling.md **L240–L242**，bytes `[26593,27309)` |
| 给数四要件（本表**不**使用于签署，仅登记边界） | 「审定一个阈值必须同时具备**可复算观测量 + 可核基础 + 非实现者签署（decision_sha256） + 追加式版本化**，否则一律维持 `not_reviewed`」 | 同上 ruling.md **L226**（A-6.1/A-6.3 段） |

> **本工位身份**：上述 C5 与 `BLOCKED-6b` 指派的**证据编制者**。我只产出"对照表"；`BLOCKED-6b` 的**补裁权**在会计 reviewer、**会签**在行业 reviewer（见上 L323 逐字）。

---

## ② 冻结：要编哪 4 条

清单**回源**取自两处机器/人工清点，二者一致：

1. `validation_report.json → counts.threshold_bases = {arithmetic_identity: 4, …}`（`I-11-A/a20260919-01/evidence/I-11-A/validation_report.json` **L29**）；
2. `hypotheses.json` 全文检索 `threshold_basis` = `arithmetic_identity` 的 4 处：**L88 / L311 / L524 / L649**（与 ACCT ruling A-6.2 逐字列示一致）；
3. 行业面同一清单：`I11A-OPEN-IND/a20260924-01/ruling.md` **L270–L279**（H1/H3/H5/H6 四行）。

| 行 | `threshold_id`（= `hypothesis_id`） | 业务别名 | 命题状态 | 当前登记容差（逐字） |
|---|---|---|---|---|
| R1 | `H-CN-ZIJIN-SEG-01` | H1 | `pending_professional_decision` | `0（算术恒等式，允许披露四舍五入引入的 \|差\| ≤ 1 元）` |
| R2 | `H-CN-ZIJIN-VOL-03` | H3 | `pending_professional_decision` | 披露可判定式（**无数值容差**） |
| R3 | `H-CN-ZIJIN-ELIM-05` | H5 | `unquantified` | `0（算术恒等式，允许 \|差\| ≤ 1 元）` |
| R4 | `H-US-MSFT-SEG-01` | H6 | `pending_professional_decision` | `0（分部加总恒等式，允许 ±1 USD million 舍入）` |

**当前登记出处（两版均核，文本逐字相同）**

| 行 | `hypotheses.json`（a20260919-01，sha `f2178768…f79a28`，51697 B） | `hypotheses_v2.json`（I11A-HYP-APPROVE a20260925-01，sha `32c22208…d7859`，55213 B） |
|---|---|---|
| R1 | L85–L88，bytes `[3806,4096)` | L85–L88，bytes `[4170,4460)` |
| R2 | L308–L311，bytes `[17700,18424)` | L332–L335，bytes `[21216,21940)` |
| R3 | L521–L524，bytes `[30621,30870)` | L545–L548，bytes `[34137,34386)` |
| R4 | L646–L649，bytes `[36843,37142)` | L670–L673，bytes `[40359,40658)` |

> `threshold_review_status` 字段**尚不存在**（BLOCKED-6c，属编排层/schema 侧）；本表**不新增、不修改**该字段，也**不修改** `threshold_basis`。

---

## ③ 判据（本表如何算"够 / 过宽 / 过严"）

### 3.1 符号

- `g` = **该恒等式所用每个披露数在原文中的舍入粒度**（实测，见 §4 方法）。
- `ε = g/2` = 单项在 round-half-to-nearest 假设下的**最大舍入误差**。
- `n` = 恒等式中**独立被舍入的披露项个数**（含等号另一侧的合计项）。
- `L = n · g / 2` = **舍入误差下限**：纯舍入模型下 `|Δ|` 可能达到的最大值 ⇒ 容差若 `< L`，则连纯舍入都能造成**假阳性**。
- `L_int` = 因披露值是粒度的整数倍，`|Δ|` 本身是 `g` 的整数倍 ⇒ 实际可达上界 = `floor(L/g) · g`。
- `U = g` = **A-6.2 上限**（ACCT ruling L240 逐字："舍入容差必须显式且**不超过来源披露的舍入粒度**"）。
- `τ` = **当前登记容差**（逐字抄录，不改写）。

### 3.2 比较标签（每行给两个方向，外加冲突判定）

| 标签 | 判据 | 含义 |
|---|---|---|
| `过严` | `τ < L` | 当前容差小于纯舍入可能产生的差异 ⇒ 假阳性风险 |
| `够` | `L ≤ τ ≤ U` | 既覆盖舍入、又不超出披露粒度 |
| `过宽` | `τ > U` 或 `τ` 明显大于 `L` | 容差超出披露粒度/超出舍入可解释范围，等式判定失去区分力 |
| `不可比` | 未登记数值容差 | 无对象可比 ⇒ 该行比较结论标 `NOT_ESTABLISHED` |
| `RULE_CONFLICT` | `L > U` | **A-6.2 上限与舍入下限互相矛盾**（`n ≥ 3` 时必然出现），本表只**登记**该事实，**不**裁哪一边为准 |

### 3.3 舍入模型假设（显式，且其适用性本身未确立）

- **模型 A（本表 L 的计算前提）**：原文各数为 `g` 的四舍五入结果 ⇒ 每项误差 `≤ g/2`，`n` 项代数和误差 `≤ n·g/2`。
- **模型 B**：原文各数是账簿**精确值**（元位/百万位即精确，无再舍入）⇒ 恒等式应**精确为 0**，所需容差下限 `L = 0`。
- **两模型哪一个适用于这些披露：`NOT_ESTABLISHED`** —— 已在盘上语料检索"四舍五入/舍入/取整"（`CN-ZIJIN-2025.txt` **0 命中**）、`round*`（`US-MSFT-2026.txt` 仅命中 `ground/surround/around` 等子串，**无舍入政策声明**）。**不猜、不以常识代填**，留会计 reviewer 选定模型。
- 本表**两模型并列呈现**：`L_A = n·g/2` 与 `L_B = 0`；`τ` 对两者的比较分别标注。

### 3.4 `NOT_ESTABLISHED` 的定义（fail-closed）

某行/某子项满足下列之一即标 `NOT_ESTABLISHED`，**且必须列出检索过的位置**：

1. 该恒等式任一操作数的**披露粒度**在盘上语料中找不到可定位原文（文件 + 行号/字节区 + 逐字引文）；
2. 存在"比较对象"缺失（例如阈值未登记数值容差，无 `τ` 可比）；
3. 原文页在盘上语料中**无可提取文本**（图像页/空页），无法在该页本身实测；
4. **禁止**用默认值、行业常识、或"把现有容差抄成结论"来填补。

---

## ④ 取证方法（先冻结，后执行）

1. **文本面（行号 + 字节区 + 逐字引文）**：以盘上已有的年报全文抽取件为准，逐条 `grep` 定位后 `read` 上下文；字节区按 **UTF-8 无 BOM、行以 `\n` 分隔**累计计算（起始 0，半开区间 `[start,end)`）。
2. **页码面（只读复核）**：用 PyMuPDF 1.26.7（全局 `C:\Miniconda\python.exe`）**只读**打开 PDF，核对锚点所在 leaf 与纯文本页的 `textlen/images`，**不落任何中间文件**。
3. **禁网**：全部证据取自盘上语料；未发起任何网络请求。
4. **禁 git 写**：未执行 `git status`（题面禁用）；仅在收尾执行 `git diff HEAD --name-only` 统计非 `.planning` 条目。
5. **写入面**：仅 `execution_runs/OPEN6-TOLERANCE-TABLE/a20260925-01/` 四个文件；`.planning` 之外（含 `company-wiki`）**零写入**。

### 4.1 本表使用的语料（全部只读）

| # | 文件 | sha256 | 字节 | 用途 |
|---|---|---|---|---|
| S1 | `.planning/…/execution_runs/I-10-A/a20260923-01/evidence/I-10-A/source_extracts/CN-ZIJIN-2025.txt` | `196f2c5419fe7d67d50e1b6a13da641e225be515be46aeb53af2b203fe423591` | 763644 | 紫金 2025 年报全文抽取（pymupdf 1.26.7，352 leaf；源 PDF sha `01819e1c…a8f343d`，79,925,886 B） |
| S2 | `.planning/…/I-10-A/a20260923-01/evidence/I-10-A/source_extracts/US-MSFT-2026.txt` | `8da453c191394c1530a7d036018b0a8ede34fa43a8c78c36bd12293f6d64fabe` | 356348 | 微软 FY2026 10-K 文本（源 htm sha `e3de0053…40ecff`） |
| S3 | `C:\Users\郑曾波\Projects\company-wiki\companies\紫金矿业\raw\financial_reports\annual\2025-03-21_cninfo_1222870413_紫金矿业集团股份有限公司2024年年报报告.pdf` | `004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89` | 32100114 | 紫金 2024 年报（**只读**；`filing_date=2025-03-21`，`retrieved_at=2026-08-01T07:10:51Z`，sidecar `.source.json`）—— R2 的跨期"上一期期末库存" |
| S4 | `.planning/…/I-11-A/a20260919-01/evidence/I-11-A/extract/arithmetic_oracle.json` | —（12555 B） | — | A1–A7 精确有理数复算（操作数、`difference`） |
| S5 | `.planning/…/I11A-OPEN-ACCT/a20260924-01/ruling.md` | `f3040df0…329c2` | 37355 | 判据 A-6.1/A-6.2/A-6.3、BLOCKED-6b |
| S6 | `.planning/…/I11A-OPEN-IND/a20260924-01/ruling.md` | —（39207 B） | — | 4 条清单表（L270–L279）与行业面"恒等式无异议"（L292） |
| S7 | `.planning/…/I11A-OPEN-MERGE/a20260924-01/handoff.json` | `b7314a22…b5878` | 21808 | C5 原文 |
| S8 | `.planning/…/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` | `f2178768…f79a28` | 51697 | 4 条阈值登记本体 |
| S9 | `.planning/…/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json` | `32c22208…d7859` | 55213 | 当前（a20260925-01）登记，文本逐字复核 |

### 4.2 已检索但**未**命中的位置（供 `NOT_ESTABLISHED` 回溯）

- `CN-ZIJIN-2025.txt` 检索 `四舍五入|舍入|取整` → **0 命中**；
- `US-MSFT-2026.txt` 检索 `round|Round|ROUND` → 7 命中全为 `ground/surround/around` 等词内子串，**无舍入政策句**；
- `CN-ZIJIN-2025.txt` **leaf 116–117**（印刷页 9–10，`合并利润表`）在盘上抽取件中为**空页标记**（`<<<PAGE 116>>>`/`<<<PAGE 117>>>` 后无文本），PyMuPDF 只读复核 `textlen=0, images=1` ⇒ **该页本身无法实测**；
- `CN-ZIJIN-2025.txt` 检索 `营业总收入` → 0 命中；`349,079,082,852` 共 7 处（L992 / L3769 / L25950 / L26015 / L26049 / L34996 / L35017），**均不在 leaf 116–117**；
- 紫金 2025 年报 `产销量情况分析表` **只披露期末库存量与三项同比变动**，**不披露期初库存**（S1 L4274–L4320；与 `hypotheses.json` L312 `observability_note` 一致）⇒ 期初库存须跨期取。

### 4.3 已登记的坐标不一致（**不回改、只登记**）

`I-11-A/…/extract/P1_zijin_pages.json` 的 `pdf_page` 字段与 PyMuPDF 只读实测 leaf **相差 ±1**（产销量表：P1 `pdf_page=44` vs 实测 `leaf 45`；分部报告 2025 表：P1 `pdf_page=327` vs 实测 `leaf 326`，两者印刷页码均为 `- 219 -`）。本表**以 S1 抽取件的行号 + 字节区为主坐标**，并同时登记三方坐标，**不判定**谁对谁错。

---

## ⑤ 范围边界（自我约束，交付时逐条核对）

1. **只读取证与编制**：不改任何产品/卡载体；`hypotheses.json` / `hypotheses_v2.json` / `decision.md` / 各 `ruling.md` / 各 `handoff.json` 全程只读。
2. **只制表，不裁**：不判 `BLOCKED-6b` 是否可解、不签署容差值、不改 `threshold_basis` / `threshold_review_status`、不解除任何 `BLOCKED`、不产生 `ACCEPT`、不代签 `decision_sha256`。
3. **fail-closed**：粒度找不到原文 ⇒ `NOT_ESTABLISHED` + 列出检索位置；**不猜、不用默认值填**。
4. **零 `.planning` 外写**（含 `company-wiki`；本轮不涉 §二十七 #2）；零 git 写；**禁用 `git status`**；禁网。
5. **产出仅四件**：`oracle.md`（本文件）、`tolerance_table.json`、`tolerance_table.md`、`handoff.json`；JSON 写后 `json.load` 重解析；UTF-8 无 BOM、LF。
6. 收尾执行 `git diff HEAD --name-only`，非 `.planning` 条目须为 0。

---

## ⑥ 交付物之间的关系

```
oracle.md（本文件：冻结范围 + 判据 + 方法）
   └── tolerance_table.json（机器可读，逐行含证据/推导/比较）
         └── tolerance_table.md（人读版 + 每条推导公式 + 给会计 reviewer 的提请语）
               └── handoff.json（sha256/字节、计数、releases_nothing / does_not_sign_tolerance）
```
