# OPEN5-S5-IND-RULING · 行业复裁报告（`OPEN-5` S5 · **行业半区**）

- **卡 / 步**：`OPEN-5` 恢复路径 **S5 · 行业复裁 + 会计定级** 的**行业那一半**（会计半区已由 `OPEN5-S5-ACCT-GRADING/a20260926-01` 交付 ⇒ 本工位**只读引用、不代签、不推翻**）
- **本载体（新建）**：`execution_runs/OPEN5-S5-IND-RULING/a20260926-01/`（`oracle.md` · `ind_ruling.json` · `s5_ind_report.md` · `handoff.json` + `_work/`）
- **角色**：`industry_reviewer_s5`（矿业/软件行业 reviewer，**非实现者**）
- **授权（逐字，`I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` L166，按行原样取出、未改一字）**：

  > | **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | 行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） | 任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |

- **`oracle.md` 先冻结**：sha256 `549cadfe0c66614b2687da12e094317db9601633718f204ce35ca17de71b07ee`（25,531 B，无 BOM、纯 LF），**在任何四点裁定、任何自抽测量、任何红绿变异之前**写入；此后未改一字节。

## 0. 结论速览

| 项 | 结论 |
|---|---|
| **四点 · P1 C 表是否启用** | ✅ **启用（限定效力范围）**；attempt04 承认 `①+④`、attempt08 承认 `①+④`、attempt07 承认 `③`（= 不可采）—— **与会计面逐条一致** |
| **四点 · P2 attempt04 用途** | 全年业绩公告（FY2025，非年报）⇒ **可用于** A1 分部收入 / A2 分部毛利 / A3 总收入 / A4a 分部加总恒等式 / A5a 公告自述审核状态 / A6b 分部存货；**不可用于** A4b 分部资产负债、A5b 审计意见逐字、A6a 五年摘要、A7 年报本体页码、A8 年报刊发后才披露的内容 |
| **四点 · P3 attempt08 英文面** | 承认 `usable=["en"]`（中文锚词实测 **0/5**、英文 **5/5** 双库）⇒ **可用于**年报本体定位与数值型分部命题（须标 `language_face=en`）；**禁止**中文原文逐字 / 中文锚词类命题 / 英文面冒充中文面 |
| **四点 · P4 G3 口径** | 按 IND **L234/L360** 裁 **口径 B（`external_retrieval_not_local = true`）为准**；两侧实测 A=`false`（PEND-5a/S3）、B=`true`（④/L360/S4）**两边都不回改，只登记** |
| **会计面 vs 行业面分歧** | **无实质分歧**（6 条全部认、2 条登记：① 行业面**追加更严**的用途/语言面限制；② L240/L241 读法 α/β 属解释分歧，本工位采 α 并显式登记 β） |
| **港股参数** | ✅ **`hk_parameters_released = false`**，`_PLACEHOLDER` 维持，`low/base/high = [null,null,null]` |
| **origin** | ✅ **仍被排除**（`graded=false` / `level=null` / `admissible=false`；S4 `consistency_result = NOT_USABLE` 一字未改） |
| **红绿变异 rc** | **`0 / 0 / 0 / 2 / 2 / 2`**（R0/M1/M2/M3/M4/M5），与 `oracle §5` 冻结期望**全等** |
| **`git diff HEAD --name-only` 非 `.planning`** | **0**（总数 3830 → 3830；本工位新文件未跟踪、不进 `git diff HEAD`） |
| **不授予** | 不放行任何港股参数 · 不解除 `OPEN-5` · 不产生 `I-11-B` 的 `ACCEPT` · 不下 S4 结论 · 不给 origin 赋级 · 不代签会计面 |

---

## 1. 回源与授权（含一处**出处勘误**）

### 1.1 C 表出处勘误（登记，**不回改**）

派单把 IND C 表指到 `execution_runs/I11A-OPEN11-IND/a20260924-01/ruling.md`。**实测该文件没有 C 表**：全文 325 行，`C 表` 与 `external_retrieval_not_local` **零命中**；其 L234/L240/L241/L261 是 OPEN-11 自身的「读法 B / 兼容影响 / 被拒方案」行，语义不同。

**C 表实际在 `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md`（399 行）**，且行号与派单引用逐一对得上：**L227**（C 表标题）· **L231**（①）· **L232**（②）· **L233**（③）· **L234**（④）· **L240/L241**（启用/反启用反例）· **L261**（禁静默顶替）· **L360**（外部≠本地）。会计半区 `oracle §1.4` 与 S4 `s4_report.md L20` 亦按此引用 ⇒ **以文件原文为准，两处派单文本不改。**

### 1.2 逐字依据（本工位按行取，杜绝转述；下表除标「摘句」者外均为整行原样）

| 出处 | 逐字 |
|---|---|
| ENVOWNER **L166** | S5 定义（见抬头，含失败分支「任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER`」） |
| ENVOWNER **L179** | ``即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。``（行首 `   - ` 为列表缩进，未计入） |
| ENVOWNER **L165**（摘句，S4 行末格） | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |
| IND **L240** | `- 环境 owner 解决可读性后，若新 attempt 实测仍读不出原文 ⇒ B 部分（保持不可用）继续有效，C 表不启用；` |
| IND **L241** | `- 若出现①类可读原文且含分部收入 ⇒ B 的"零产出"解除，港股命题可重新走正常取证（仍需会计面定证据等级）；` |
| IND **L234**（④ 行，摘句） | `必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径` |
| IND **L360** | ``- **外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`；`2026-09-02 8-K` 条目显式写明"**本地不可核，外部获取，不得作为本地可核证据放行**"。`` |
| `OWNER_DECISIONS` **L504** | `- **取证（选项 3）的证据等级由会计面定，不由取证方自定**；取不到就维持 BLOCKED，**不造绿色样例**。` |
| `OWNER_DECISIONS` **L502**（摘句） | **「授权」是许可不是动作**：四项均**不产生任何 ACCEPT、不解除任何 BLOCKED、不改任何 status** |


**owner 解锁链（J1-1）**：PEND-5a `handoff.authorized_by` = `OWNER_DECISIONS.md §二十六 #1 … owner 原话「1，授权」→ PEND-5a（联网取可读港股替代件）`，`result = delivered` ⇒ IND **L227**「供 owner 解锁后使用」的前置成立。

---

## 2. 四点逐条裁定

### P1 · C 表是否启用 + 三件来源定级会签

**裁定：`c_table_adopted = true`（启用，效力范围受限）；attempt04 = `①+④` ✓、attempt08 = `①+④` ✓、attempt07 = `③`（= 不可采）✓ —— 三件全部与会计面一致。**

四条冻结条件（`oracle §4.1`）逐条实测：

| 条件 | 实测 | 依据 |
|---|---|---|
| **J1-1** owner 解锁链可核 | ✅ `true` | PEND-5a `authorized_by`（§二十六 #1「1，授权」）+ `result=delivered` |
| **J1-2** S3/S4 已走完且结论可核 | ✅ `true` | S3 报告：路径 A（origin 字节 OCR）**5/5 锚词**、B1 文字层 **0/5**、B2/B2′ **4/5 与英文 5/5**；S4：`consistency_result=NOT_USABLE`、U1 `NOT_USABLE`、U2/U3 `CONSISTENT` |
| **J1-3** L241 正向条件（①类 + 含分部收入） | ✅ `true` | attempt04：可定位（分部收入首见 p1、分部附注 p49）· sha `d0975600…` **五方全等**（PEND-5a/S3/S4/会计面/本工位复算）· 期间逐字 `截至2025年12月31日止年度` · URL+UTC+sha 齐（UTC 与盘上 mtime 逐字相等）· **分部收入锚 `分部收入`×16、`手機×AIoT`×68**；attempt08：同上（sha `b787f029…` 五方全等、封面 `2025 ANNUAL REPORT`、**`Segment-wise … RMB351.2 billion`**） |
| **J1-4** L240 反向条件读法 | 采 **α** ⇒ 不成立（见下） | S3 路径 A 5/5 + 两件①替代件可读 |

**L240/L241 读法分歧（显式登记，不隐瞒）**：

- **α（本工位采用）**：L240 的「读不出原文」= **新 attempt 产不出任何可读原文文本** ⇒ 实测产出了 ⇒ 不成立；
- **β（登记、不采用）**：「原文」仅指 **origin 本体字节**（B1 仍 0/5、U1 `NOT_USABLE`）⇒ 若采 β 则 **C 表不启用**；
- **采 α 的理由（冻结于 oracle）**：IND **L227** 逐字为「**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**」——替代来源表的存在前提就是 origin 不可读，β 会使该表**永无适用场景**、与表自身用途矛盾；L241 措辞是「出现①类可读原文且含分部收入」，开关挂在**替代件**上而非原文件修复上。
- **对 owner 的登记**：这是一条**解释分歧**；**无论采 α 还是 β，`hk_parameters_released` 都保持 `false`、origin 都保持排除**，分歧只影响「港股命题能否重新走正常取证」这一层，不放行任何参数。

**启用的效力范围（超出即越权）**：① 只解除 IND **B-1** 中「①类替代件缺位 ⇒ 零产出」那一层；**B-3（不接受二手补位）/ B-4（不接受行业常识补位）继续有效**；② **origin 不因启用而可引用**；③ **参数不放行**（L166「通过后才谈」+ L179 + ENVOWNER §⑦）；④ ④ 标记件**永不冒充本地原件**。

**attempt07 单列理由（会计面之外的第二条）**：其正文中文锚词实测 **0/5**（460,387 字符、CJK 55,700 全为 Adobe-CNS1 族乱码）⇒ 除「③=第三方代理渲染件、二手」外，**内容本身不可读** ⇒ 双重不可采。

### P2 · attempt04 文件类型用途

**裁定：承认其为**同期间**公司原文披露（①），但用途按实测内容清单分档：**

| 类 | 命题类 | 实测 | 处置 |
|---|---|---|---|
| **A1** | FY2025 分部收入水平与增速 | `分部收入`×16、`手機×AIoT`×68、`業務分部`×22（首见 p1；分部附注 **p49**） | ✅ **可用** |
| **A2** | 分部毛利率/毛利 | `分部毛利率`×8、`毛利`×101（含总毛利率 22.3%、手机×AIoT 21.7%） | ✅ **可用** |
| **A3** | 总收入与增速 | `總收入`×34；逐字片段 `集團總收入為人民幣4,573億元`（其后为「同 比增長25.0%」，抽取换行处含一空格） | ✅ **可用** |
| **A4a** | 分部加总 = 合并总收入恒等式 | 分部附注（自抽 p49，标题逐字 `分部資料及收入`）`351,217,174 + 106,069,513 = 457,286,687` 千元 ⇒ **差 0**（本工位复算 `equal=true`）；原文「概無任何重大分部間銷售」 | ✅ **可用** |
| **A5a** | 公告自述的审核状态 | 实测含逐字片段 `截至2025年12月31日止年度的經審核合併業績`（1 次）与 `羅兵咸永道會計師事務所`（2 次），并有核數師「數字一致」程序；**无** `核數師報告`、**无** `無保留意見` | ✅ **可用**（须标来源=公告，非核数师报告） |
| **A6b** | 分部存货 / 按性质划分开支 | p50 可报告分部存货 `74,758,465 / 6,230,987` 千元；p50 附注3 | ✅ **可用** |
| **A4b** | 分部资产/负债划分 | 中文侧 `分部資產` 0 命中；EN 年报原文明示 `no separate segment assets…` | ❌ **禁止**（缺，两来源皆无） |
| **A5b** | 审计意见 / 核数师报告逐字 | `核數師報告` **0**、`無保留意見` **0**（仅「數字一致」程序） | ❌ **禁止**（需改用 attempt08 EN 面或另取文） |
| **A6a** | 五年财务摘要 / 跨期多年序列 | `財務摘要` **0**（`五年`4 次命中全为「五年排名全球前三」营销表述） | ❌ **禁止** |
| **A7** | 年报本体页码/锚文本 | `年度報告` **0**；59 页 vs 年报 415 页 | ❌ **禁止**（改用 attempt08） |
| **A8** | 年报刊发日 2026-04-28 之后才披露的内容 | 公告刊发 **2026-03-24**，早于年报 | ❌ **禁止**（时序上不可能包含） |

**必标项（① must_label）**：`document_type=全年业绩公告（results announcement，非年度报告）` · `period=FY2025` · `publication=2026-03-24` · `external_retrieval_not_local=true`（④） · `language_face=zh-Hant`。
**回答会计面 §6-3**：**不需要为「年报本体口径」重取 attempt04**；凡 A5b/A6a/A7 类需求一律**换源到 attempt08（EN 年报本体）或另行取中文年报本体**（当前本地中文年报仍不可读）。

### P3 · attempt08 英文面限制

**裁定：承认 `usable=["en"]`；英文面可用范围如下。**

| 实测（本工位自抽，双库） | 值 |
|---|---|
| 中文锚词 `小米/收入/年度報告/分部/毛利` | **0/5**（fitz；cjk 仅 182）⇒ 与会计面登记一致 |
| 英文锚词 `Xiaomi/Revenue/Annual Report/Segment/Gross profit` | fitz **5/5**（920/33/3/9/7）、pdfminer **5/5**（919/33/3/9/7） |
| **跨语言共享数值 6 对** | 457.3 / 351.2（億→billion 归一）、351,217.2、457,286.7、25.0%、21.7% ⇒ **equal = 6、conflict = 0** |

**可用于**：① 需要**年报本体**页/表定位的命题（**五年财务摘要** `FIVE-YEAR FINANCIAL SUMMARY`（自抽 p8）、**审计意见** EN 年报核数师报告段（逐字 `Opinion` / `What we have audited` / `auditor’s report`）、分部附注 —— 这三类恰是 attempt04 缺的）；② 数值型港股份部命题（收入/毛利/占比/增速），**必须标 `language_face=en` 并用英文原文逐字引文**；③ 与 attempt04 中文件的**数值交叉验证**（上表 6 对）。

**不可用于**：① 任何要求**中文原文逐字引文 / 中文锚词命中**的命题（中文 0/5）；② 任何「中文年报原文已核」的口径声明；③ 翻译敏感的**定义性表述**（分部名称、会计政策措辞）未经 attempt04 中文件对照单独成立；④ **英文面冒充中文面**——与④「永不冒充本地」同构：**`language_face=en` 不得冒充 `zh-Hant` 原文面**。

**回答会计面 §6-4**：确认 `usable_faces=["en"]`；**若命题需要中文原文，须另行取证，不得由本英文面代签。**

### P4 · `G3` 口径会签

| 侧 | 实测（逐条回源） | 值 |
|---|---|---|
| **A**（语义=非第三方代理） | PEND-5a `ext-04` L109 / `ext-08` L195；S3 `in-02` L83 / `in-03` L94 | **`false` ×4** |
| **B**（语义=外部取回件永不冒充本地） | IND **L234**（④ 行证据等级列本身就是 `external_retrieval_not_local`）、**L360**、**L261**；S4 `own_provenance` L5605 / L5622 | **`true` ×4** |

**裁定：按 IND L234/L360，口径 B（`true`）为准** —— 理由：④ 的「使用条件」明写「**永不冒充本地可核**」，若按 A 记 `false`，该条件**没有字段承载**；且 L360 是「**所有** `EXT-*` **一律**标」的无条件表述。
**两边都不回改**：PEND-5a / S3 的 `false` 原样保留（`back_written = false`），S4 与本工位记录登记分歧。**回答会计面 §6-5：无异议，采同一口径。**

---

## 3. 与会计半区的衔接（§6 七条提请逐条答复）

| # | 会计面提请（`s5_acct_report.md` L176–L182） | 行业面答复 |
|---|---|---|
| **1** | 会签来源登记与等级：attempt04 `①+④/E1/S1`、attempt08 `①+④/E1/S1(en)`、attempt07 `③/E3/S0` | ✅ **逐条承认**（`attempt_levels_confirmed.all_three_confirmed = true`）；**不改** E/S 与 `admissible`，只在其上**追加更严的用途/语言面限制** |
| **2** | 请裁定 C 表是否启用（L240/L241） | ✅ **启用（限定效力）**；附 α/β 读法登记（见 P1） |
| **3** | 请确认 attempt04 文件类型用途 | ✅ 见 P2 分档表；**不需要重取 attempt04**，年报本体需求换源 attempt08 或另取中文年报本体 |
| **4** | 请确认 attempt08 语言面限制 | ✅ 见 P3；中文 0/5 已独立复测确认；**英文面不得代签中文原文面** |
| **5** | 请复核 G3 分歧登记 | ✅ 采口径 B（`true`），**两边均不回改**（见 P4） |
| **6** | 边界确认：两面未齐前 `hk_parameters_released=false` | ✅ **确认并继续**：即使本工位判过，**仍为 `false`**（L166「通过后才谈」≠ 放行；L179 + ENVOWNER §⑦ 仍压顶） |
| **7** | 未证事项：attempt08 pdfminer 自抽工件跨进程 2 个 sha | **登记为限制，不作放行条件，也不构成行业面新阻塞**：行业面要求的可复现性是「**引用绑定登记载体 sha256 + `byte_range`**」（与会计面 E1e 同构），**不以自抽工件字节全等为条件**；若 owner/编排层要求字节级可复现，本工位同意另行提请复测 |

**分歧汇总（逐条）**：**无实质分歧**。登记 2 条非对抗性差异：① 行业面**追加**用途/语言面限制（方向更严）；② L240/L241 的 α/β 解释分歧（行业面裁权，已登记给 owner）。

**不代签会计面（逐条）**：未改 `E1/E3/S1/S0`、未改 `usable_faces`、未改 `admissible`、未重做会计四步、未回改会计半区任何字节（sha 实测 `acct_grading.json = 3a5623af…`、`s5_acct_report.md = 0bfbeaed…`，与其 `handoff.written_files` 登记全等）。

---

## 4. 红绿变异（`oracle §5` 冻结清单，脚本 `_work/s5_ind_grade.py`）

| # | 变异 | 冻结期望 | 实测 rc | 结果 |
|---|---|---|---|---|
| **R0 绿·基线** | 不改判据，真实输入 | `rc=0`：`c_table_adopted=true`、attempt04/08 → `①+④` 承认、attempt07 → `③` 不采、origin → **excluded（level=null）**、G3 → 口径 B、`hk=false` | **0** | ✅ 与期望全等（`expectation_met=true`） |
| **M1 红·判据改弱** | `tier_filter=off`（③/代理件按①）+ `require_readable=off`（不看锚词） | **attempt07 由「不采」翻转为「采」**，`rc=0` | **0** | ✅ 红：`should_pass_flip=true` ⇒ baseline 拒绝 attempt07 是**判据作用**，非样本缺失 |
| **M2 红·origin 排除弱化** | `exclude_origin=false` | origin **被赋等级**（应被排除），`rc=0` | **0** | ✅ 红：`origin_grade_flip=true`（`level="E1/S1 (MUTANT…)"`，**仅测试产物**） |
| **M3 红·blocked 分支 1** | 内存剥离 attempt04 的 URL（模拟 G2a 缺失） | `verdict=blocked`（④ 使用条件 L234 不满足 ⇒ 提请点 1 证据不足） | **2** | ✅ 红：`rc=2`、`c_table_adopted=false` |
| **M4 红·blocked 分支 2** | 抹去①件全部分部收入锚（模拟 L241 正向条件不成立） | `c_table_adopted=false` ⇒ 行业面不通过，`rc=2` | **2** | ✅ 红：`rc=2`、`equal_pairs 6→4`（英文侧锚同时被遮） |
| **M5 红·blocked 分支 3** | 篡改 attempt08 共享值 `Total revenue 457,286.7 → 457,286.9` | J3-2 跨语言比对失败 ⇒ `blocked`，`rc=2` | **2** | ✅ 红：`rc=2`、`conflicts=1` |

**期望 rc 序列 `0 / 0 / 0 / 2 / 2 / 2` —— 实测完全相等（6/6 `expectation_met=true`）。**
红绿双向成立：**判据改弱后一个不该通过的来源（attempt07 代理件）确实能通过（M1）**；**`blocked` 分支确实是红的（M3/M4/M5，rc=2）**；**origin 排除不是空转（M2）**。

---

## 5. 港股参数、origin 与「不授予什么」

1. **`hk_parameters_released = false` 恒成立**（所有分支，含全部变异体输出）；`low/base/high = [null,null,null]`、`_PLACEHOLDER` 维持、港股命题**零产出**。
2. 两面都过只兑现 L166 的前半句「**通过后才谈**港股命题与参数」—— **谈 ≠ 放行**；L179 与 ENVOWNER §⑦（解锁前置须全部满足且「仍不由本载体」）**一条都没解除**。
3. **`origin` 仍被排除**：`graded=false` / `level=null` / `admissible=false`；S4 `consistency_result = NOT_USABLE` **一字未改**。
4. **`OPEN-5` 未解除**、**未产生 `I-11-B` 的 `ACCEPT`**、**未新增任何 `approved_frozen`**。

---

## 6. 只读、写入面与纪律自查

| 项 | 实测 |
|---|---|
| 写入面 | **仅** `execution_runs/OPEN5-S5-IND-RULING/a20260926-01/`（4 件产出 + `_work/` 34 个脚本/测量/自抽件，逐件 sha 见 `handoff.json → written_files`） |
| `.planning` 之外创建/修改 | **0**（含 `company-wiki` **未打开**） |
| 前站只读 sha 复核 | ENVOWNER `ruling.md 2636d463…` · IND `ruling.md 8bc685a4…` · 会计 `oracle 32c28419…` / `acct_grading 3a5623af…` / `report 0bfbeaed…` · S4 `dual_path_verify 218a4195…`（=S4 handoff 登记）/ `s4_report 7987f5de…`（=S4 handoff 登记）· S3 `provenance 3e44f7e9…`（=S3 handoff 登记）· PEND-5a `provenance d06df212…`（=PEND-5a handoff 登记）⇒ **全部与各自登记值全等，零回改** |
| git 写 | **0**；**未用 `git status`**；只用 `git diff HEAD --name-only` / `git ls-files --others`（只读） |
| `git diff HEAD --name-only` | 总数 **3830 → 3830**（基线 3830、收尾 3830，**非 `.planning` = 0**；本工位文件未跟踪、不进 `git diff HEAD`） |
| 非 `.planning` untracked | 48（全部为既有 `.tmp-r41-mutation/*` 历史路径，**非本工位创建**） |
| 联网 | **否**（只用盘上既有产物 + 本地只读解析/自抽） |
| JSON | `ind_ruling.json` / `handoff.json` 写后 `json.load` 重解析 **OK**；UTF-8 **无 BOM**、**纯 LF** |
| 五份计划文件 | **未写** |

---

## 7. 本工位**没有做**的事（逐条）

1. **未代签会计面**：不动 E/S 等级、不动 `usable_faces`、不动 `admissible`、不重做会计四步、不改会计半区任一字节。
2. **未放行港股参数**：`hk_parameters_released = false`、`_PLACEHOLDER` 维持。
3. **未解除 `OPEN-5`**、**未产生 `I-11-B` 的 `ACCEPT`**、未新增 `approved_frozen`（`OWNER_DECISIONS L502`：授权是许可不是动作）。
4. **未改 `NOT_USABLE`**、**未下 S4 结论**、未动 `numeric_conflict`，未把任何 `not_readable` 改成「已验证」。
5. **未给 origin 赋级**（M2 变异体中的 `MUTANT` 字样只存在于 `_work/measure_m2_origin.json` 测试产物，正式产出 `ind_ruling.json` 中 `level=null`）。
6. **未回改** S4 / S3 / S1 两站 / 封盘 `I-11-A` / 会计半区 / `I11A-OPEN-IND` / `I11A-OPEN11-IND` 任一字节。
7. **未写**五份计划文件；**未写** `.planning` 之外任何路径（含 `company-wiki`）。
8. **零 git 写**、**未用 `git status`**、**未联网**。
9. **未给 attempt04 升格为年报**、**未给 attempt08 补中文面**、**未给 attempt07 升格**——三处都是「不为推进而放行」。

---

## 8. 给父的最终状态（self-contained）

1. **四点全部裁定完成**：P1 `c_table_adopted = true`（限定效力 + α/β 读法登记）、P2 attempt04 用途 6 可用 / 5 禁止、P3 attempt08 `en` 面可用范围与四条禁止、P4 G3 采口径 B（`true`）且两边不回改。
2. **三件来源定级会签**：attempt04 `①+④` ✅ · attempt08 `①+④` ✅ · attempt07 `③`（不可采）✅ —— 与会计半区**逐条一致，无实质分歧**；行业面只**追加更严限制**。
3. **S5 两面状态**：会计半区 = 完成（只读引用）；行业半区 = **PASS（四点全部成立）** ⇒ 按 L166 只到「**可谈**港股命题与参数」这一步。
4. **仍不放行**：`hk_parameters_released = false`、`_PLACEHOLDER` 维持、`low/base/high = [null,null,null]`、港股命题零产出、`OPEN-5` 未解除、无 `I-11-B` ACCEPT、origin `level=null`、S4 `NOT_USABLE` 未改。
5. **红绿变异 rc = `0/0/0/2/2/2`**，与冻结期望 6/6 全等。
6. **纪律**：写入面 = 本新目录；`.planning` 外 0；零 git 写；未用 `git status`；未联网；`git diff HEAD --name-only` 非 `.planning` = **0**。
7. **留给 owner/编排层的登记项**：① L240/L241 的 α/β 解释分歧（本工位采 α，登记 β）；② 派单把 C 表出处写成 `I11A-OPEN11-IND`（实为 `I11A-OPEN-IND`，不回改）；③ attempt08 自抽工件字节不稳定（限制，非阻塞）；④ 后续如要港股命题真开工，仍须按 ENVOWNER §⑦ 逐条走完并由有权方处理。
