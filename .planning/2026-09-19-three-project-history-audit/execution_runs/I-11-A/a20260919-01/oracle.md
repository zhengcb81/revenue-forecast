# I-11-A oracle（在生成命题与运行校验之前冻结）

card_id: I-11-A   attempt_id: a20260919-01   role: implementer（本文件不构成验收）
冻结时间顺序：本文件先于 `evidence/I-11-A/hypotheses.json`、`source_map.json`、`mechanism_review.md`
的生成，也先于 `tools/validate_hypotheses.py` 的首次运行。任何事后修改以“R2 附录”追加，不改写本正文。

---

## 0. 本卡要冻结的对象与不作的事

本卡把**定性判断**转成**可证伪命题**：命题必须带来源、机制链、模型 driver、时点、双计排除、
可推翻条件（观测量 + 阈值 + 观察日 + 来源路线 + 恢复规则）。本卡**不**校准参数幅度（I-11-B）、
**不**做反方独立审查（I-11-C）、**不**给出任何收入预测值、**不**授予三资格中的任何一项。
“按要求填满模板”不等于“命题为真”。

三条资格在本卡的状态与边界（分开陈述，禁止混同）：

| 资格 | 本卡状态 | 本卡可以声称的 | 本卡不得声称的 |
|---|---|---|---|
| formula（公式） | `not_applicable_here` | 25 张 M 卡在本卡的映射里只被**引用**（`model_id`/`driver_name` 取自 M 卡正文），本卡不运行任何模型 | 公式通过；任何数值输出正确 |
| disclosure_adaptation（披露适配） | `not_granted` | 只做“原始披露 → 原文串/页码/单位”的只读取证 | 某公司/分部口径已适配通过；未经 I-10-A 的适配不得称为适配 |
| accuracy（准确性） | `not_granted` | 无 | 任何准确性、覆盖率、优于基准的说法 |

---

## 1. 输入绑定（运行前已核，值见 `binding.json` 与 `evidence/I-11-A/source_probe.json`）

| source_doc_id | 绝对路径 | sha256（期望） | 字节 |
|---|---|---|---|
| CN-ZIJIN-AR2025 | `...company-wiki\companies\紫金矿业\raw\financial_reports\annual\2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf` | `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d` | 79,925,886 |
| HK-XIAOMI-AR2025 | `...company-wiki\companies\小米集團－Ｗ\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf` | `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c` | 4,405,561 |
| US-MSFT-10K-FY2026 | `...company-wiki\companies\MICROSOFT CORP\raw\financial_reports\annual\2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm` | `e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff` | 8,585,615 |
| PRIOR-EXTRACT-ZIJIN | `...revenue-forecast\audit_review\2026-09-18_real_company_skill_audit\ZIJIN\annual_2025_selected_pages.json` | `cbda5abb248d9c5f032a681befbd2bc4012896c8bdfef2192490995c358c07eb` | 91,539 |

### 0.1 冻结顺序的如实披露（重要）

本文件的 §1–§9 是在**命题生成与校验脚本编写之前**写下的；但有两项**观测**发生在写本文件之前，
如实登记，不用“先冻结”掩盖：

1. `tools/probe_source_bytes.py`（raw sha256/结构探测）先运行 → 表内 sha256 与字节数是**实测值**，
   不是先验期望值；实际约束是 O-1 的“必须与 I-00-A 基线一致”，该一致性在运行后核对。
2. `tools/page_offset_match.py` 的偏移最优解在写本文件前已跑出一次（用于确认 P1 是否可用）。
   O-5 因此冻结的是**判定规则**（按精确命中页数最多、差异 token 最少选优；命中 0 则弃用），
   而偏移**取值**由脚本每次运行重算并落盘，不由我口头指定。
3. 命题本身（`hypotheses.json`）与校验运行**严格在本文件之后**，未从结果回改期望值。

**O-1（期望）**：三个 raw 文件的实测 sha256 必须与 I-00-A 基线一致（上表）。
不一致 → 立即停止本卡写入，改出漂移报告（START_HERE 第 78 行）。
**O-2（期望）**：`HK-XIAOMI-AR2025` 实测 `/ObjStm` > 0（对象流型 PDF）；本 attempt 的解释器
无 PDF 库且禁网，因此我方可用的两条取文路径对该文件的可读性**不预设**，按 §6 的实测结果决定。

## 2. 取文路径与“可核原文”的定义

本 attempt 允许两条**互相独立**的取文路径，两者都必须记录 argv/退出码/输出面：

- **P1 = `tools/pdf_text.py`**：纯标准库（`re`/`zlib`）的 PDF 取文器，在 attempt 隔离解释器内运行。
  支持经典 xref 对象 + FlateDecode + Form XObject(`Do`) + `/Contents` 数组 + Type0/Identity-H 的
  ToUnicode CMap + TrueType 的 WinAnsiEncoding；**不支持**对象流（ObjStm）/xref 流型文档，
  不支持 LZW/JPX/加密。
- **P2 = `pdftotext.exe` (Xpdf 4.00, `C:\Program Files\Git\mingw64\bin\pdftotext.exe`,
  sha256 `252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0`)**：外部独立实现的
  命令行工具，与 P1 无共享代码。用它作**第二条独立路**（只读、无网络、只写 attempt 目录）。

**O-3（口径）**：“可核原文”= 能在**至少一条**路径的输出里定位到该原文字符串，且该路径的
sha256/argv/输出文件已归档到本 attempt。只用 P2 定位而不记录 P2 的 argv 与输出 → 不算可核。
未记录页码与单位 → 不算可核。

**O-4（页面索引口径，必须在每条命题里写明）**：本卡统一使用
`page_index_basis = "pdf_leaf_1based"`（PDF 物理页，从 1 开始），并以锚文本同时给出定位串。
**O-5（期望）**：`PRIOR-EXTRACT-ZIJIN` 的 `pdf_page` 与 P1 的 `pdf_leaf_1based` 之间存在**常量偏移**，
偏移值必须由 `tools/page_offset_match.py` 在 offset ∈ {-1,0,1,2} 中按“精确多重集命中页数最多、
差异 token 最少”选出并落盘；不得由我口头指定。若最优 offset 的精确命中页数为 0 → 停止引用该
artifact 作为交叉证据，并把差异写入 `mechanism_review.md`。

**O-6（P1 正确性判据，先冻结）**：在最优 offset 下，对**每个**被引用页面，
P1 文本中出现的每个**被引用数值**都必须满足：去掉千分位逗号后，该数字串出现在
`PRIOR-EXTRACT-ZIJIN` 同页文本中。任一引用数值不满足 → 该命题的来源判 `rejected`，
不得改数字去迁就提取器。数字串的形态差异（如 P1 相邻字段粘连成 `109110.45`）
**不算通过**：必须用“该值所在字段的独立原始串”比对，粘连串不得作为来源证据。

**O-7（HK 与 US 的原文可得性判据）**：
- US：P1 不处理 HTM；改用 `tools/msft_figures.py`（纯标准库 `html.parser`）解析，且收入表必须
  能被完整读出（三旧分部 + 合计）。
- HK：允许 P1（若支持该文件结构）或 P2（若输出中文可读）。两条都不可读 → 该 source 判
  `not_readable_in_this_attempt`，其命题**不得**填入原文串，只能登记为
  `unquantified / STOP_EVIDENCE`（卡正文“来源晚于 as_of 或原文无法核查 → STOP_EVIDENCE”）。

## 3. 命题结构判据（先冻结；校验脚本按此实现）

`evidence/I-11-A/hypotheses.json` 是数组，元素字段齐全性按 `common_research_cards.md` 的
I-11 参数模板逐字段核对。除模板字段外，本卡追加以下**强制**字段（模板未列但验收要求）：
`state`、`state_reason`、`page_index_basis`、`anchor_text`、`evidence_path`、
`double_count_exclusion`、`refuted_by`（数组）、`independent_contract_claims`（数组）、
`machine_verifiable`、`falsifier_candidates`、`reviewer`。

### 3.1 状态机（只允许三态 + 两个停止码）

| state | 进入条件 | 禁止 |
|---|---|---|
| `unquantified` | 机制链无法定位到某个已注册 `parameter_id`，或缺少可观测的对应用量/价格字段；保留叙述 | 强行加百分点；删除命题 |
| `pending_professional_decision` | 机制链与 driver 已定位，但“是否已在基期/其他 driver 反映”“阈值是否合适”等需行业/会计 reviewer 裁定 | 由我自签 approved |
| `approved_frozen` | **仅**在 `reviewer` 给出独立签署后才可出现；本 attempt 内我不得写此状态 | 由实现者写入 |
| `STOP_EVIDENCE` | 原文无法核查、来源晚于 `as_of`、或来源不属四类 `source_type` | 用二手转述补足 |
| `STOP_DISCLOSURE_ADAPTATION` | 单位/期间/总净额/并表范围不能确定 | 用“大致”数字 |

**O-8（先冻结的期望分布）**：本 attempt 的命题里
`approved_frozen` 计数必须为 **0**（无独立 reviewer 参与）；
`pending_professional_decision` 计数必须 **≥1**（存在需行业 reviewer 裁定的可观测性/时点问题）；
每条命题必须恰好属于上述五态之一。任何“全部 approved”或“全部 unquantified”的分布都视为
**未完成卡内第 4 步**，必须在 `mechanism_review.md` 记录原因。

### 3.2 `source_type` 闭集与独立性分组

- 闭集：`company_disclosure` / `independent_observation` / `management_target` / `analyst_assumption`
  / `synthetic`。**`synthetic` 只允许出现在工具的单元测试里，不得出现在 `hypotheses.json`。**
- 管理层目标必须单列 `source_type = management_target`，且
  `calibration.management_target_is_not_independent = true`。
- `independence_group` 归并规则（先冻结）：
  `ZIJIN-AR2025`、`ZIJIN-MGMT-PLAN-2026`、`MSFT-10K-FY2026` 各为一个独立组；
  同一份原文的 PDF 版与 HTML 版、同一场电话会的十篇转述，都算**同一组**。
  **O-9（期望）**：`management_target` 与同一实体同一年度的 `company_disclosure`
  必须落在**不同组**，但**不得**互为独立证据；`calibration` 里不得把管理层目标记为
  independent evidence。

### 3.3 机制链与参数映射

- `mechanism_chain` 必须有 ≥3 环，且**最后一环**必须落到“收入确认/期间归属”语义。
- `parameter_mapping.model_id` 必须取自 `execution_v2/model_cards.md` 的 31 个已注册 model_id；
  `driver_name` 必须取自该 model 卡的“必填/可选”driver 列表。**O-10（期望）**：所有 `model_id`
  与 `driver_name` 都能在 `model_cards.md` 中按字面命中；命中失败的命题判
  `pending_professional_decision`（不是 unquantified：机制存在但没有已注册参数可落）。
- 一个命题对应**唯一** `parameter_id`；确需多个时必须显式列出且说明分摊规则。
  **O-11（期望）**：不得出现两个命题用不同 `parameter_id` 表示同一驱动（同 model_id + 同 driver_name
  + 同 effective_period ⇒ 必须同 `parameter_id`）。违反 → 判为双计风险，必须在
  `double_count_exclusion` 里写明并被 `mechanism_review.md` 列为待裁定。

### 3.4 falsifier（可推翻条件）先冻结的合格判据

`falsifier` 必须同时具备：
1. `observable`：一个**具体观测量**（不是“风险上升”这类词）；
2. `threshold`：可与观测量直接比较的数值/枚举边界，且注明**依据类型**（算术恒等式 / 原始披露口径差 / 专业审定阈值）；
3. `observation_date`：该观测量何时可以观测到（不得是“未来某时”）；
4. `source_route`：从哪份披露/哪个章节取得（可执行到 source_doc_id + 章节锚文本）；
5. `revert_rule`：被推翻后的动作（回到上一已证实值 / 停止该参数进入 I-11-B / 新建版本而不改旧快照）。
**O-12（期望）**：算术恒等式类阈值必须能被 `tools/verify_arithmetic.py` 用有理数精确复算
（差为 0）；口径差类阈值必须给出两个被比较原始串的出处；专业审定阈值类必须带
`threshold_basis = "professional_judgement_required"` 并进入 `pending_professional_decision`。
**O-13（期望）**：每条命题的 `falsifier.threshold` 不得为 null；`source_route` 不得为空。

### 3.5 每条命题必须预登记的反例（本卡硬要求）

除 falsifier 外，每条命题必须有 `refuted_by`（≥1 条），内容形如“什么观测会推翻它”，
并与 `falsifier` 一致（不得互相矛盾）。
**O-14（期望）**：`refuted_by` 条数 ≥ 命题数（每条至少 1 条），且每条至少包含
一个能由原始披露在未来某一确定观察日判定的动作。

## 4. 计数与枚举的落盘要求（禁止手抄计数）

**O-15（期望）**：`source_map.json` 必须由 `tools/build_source_map.py` 生成，其中
`documents` 数组的元素个数、每条 `cited_values` 的条数，都由脚本在运行时统计并写入
`counts` 字段；`hypotheses.json` 的 `state` 分布同样由 `tools/validate_hypotheses.py`
统计后写入 `evidence/I-11-A/validation_report.json`。
**O-16（期望）**：`mechanism_review.md` 中出现的每个计数（命题数、各状态数、各来源类型数、
开放项数）必须能在 `validation_report.json` 或 `source_map.json.counts` 中找到同值字段；
review.md 与 handoff.json 里的计数也必须同源。手写计数与脚本计数不一致 → 本卡禁止交审，
先修脚本再重跑。

## 5. 算术 oracle（先手算，后复算；全部用有理数精确比较）

| 编号 | 命题（被检验的恒等式） | 手算 | 期望 |
|---|---|---|---|
| A1 | 紫金 2025 四分部**对外**销售收入之和 = 公司营业收入 | 109,977,556,345+165,858,644,874+29,212,610,830+44,030,270,803 = 349,079,082,852 | 差 = 0 |
| A2 | 紫金 2025 四分部（对外+内部）总计 − 抵销 = 公司营业收入 | 584,049,229,264 − 234,970,146,412 = 349,079,082,852 | 差 = 0 |
| A3 | 紫金 2024 四分部对外销售收入之和 = 2024 公司营业收入 | 74,089,365,354+181,141,823,725+29,386,475,085+19,022,292,989 = 303,639,957,153 | 差 = 0 |
| A4 | 紫金产销量表：销售量 − 生产量（2025，四产品） | 金 +418 kg；铜 +6,763 t；锌 +3,914 t；银 +872 kg | 四者均为正，且与库存变动方向一致 |
| A5 | 微软 FY2026 三旧分部收入之和 = 合并收入 | 139,996+137,791+54,052 = 331,839 | 差 = 0 |
| A6 | 微软 FY2026 按产品/服务分解之和 = 合并收入 | 129,425+101,997+21,790+19,817+17,084+15,176+9,175+9,006+8,260+109 = 331,839 | 差 = 0 |
| A7 | 微软 FY2025 同两项 | 120,810+106,265+54,649 = 281,724；98,435+87,767+23,455+17,812+17,314+13,878+7,404+7,827+7,760+72 = 281,724 | 差 = 0（两式各自） |

A1–A7 的每个加数都必须能在 P1 或 HTM 解析输出里按原始串定位；任一加数定位失败 →
对应命题的来源判 `rejected`，**不得**改用“两个数相减得到”的派生值当独立来源。
A4 只声明“四产品销量均高于产量”，**不**由此推断库存桥闭合（库存还受并购范围/在产品影响）。

## 6. 取文路径的实测期望（运行前冻结的判断，不是结果）

- E1：P1 对 `CN-ZIJIN-AR2025` 的 `classic_pages` 期望 = 352。
- E2：P1 对 `CN-ZIJIN-AR2025` 第 327 页（财务报表附注-续 分部报告-续）期望能读出中文正文与
  “对外销售收入”行；若读出的行内字段次序与 `PRIOR-EXTRACT-ZIJIN` 不一致，判为
  **布局差异**（记为已知限制），但只要被引用数值串本身可定位，来源仍算可核。
- E3：P2 对 `CN-ZIJIN-AR2025` 期望输出可读中文（用于第二条独立路）。
- E4：P2 对 `HK-XIAOMI-AR2025` 的**预设**：可能因该文件的字体/编码方案输出不可读；
  若不可读，则按 O-7 判 `not_readable_in_this_attempt`，并把“HK 原文可读性”登记为开放项。
  **不得**用任何二手转述（含 revenue-forecast 审计目录里的研究稿）替代 HK 原文。

## 7. 校验脚本先冻结的**必须拒绝**案例（正反例，运行前写死）

`tools/validate_hypotheses.py` 必须对下列每个反例报错，且错误码固定：

| 错误码 | 反例输入 | 期望行为 |
|---|---|---|
| `E_EMPTY_FIELD` | 任一必填字段为 `null`/`""` | 拒绝 |
| `E_SOURCE_TYPE_CLOSED` | `source_type = "synthetic"` | 拒绝 |
| `E_BAD_PAGE_BASIS` | `page_index_basis != "pdf_leaf_1based"` 而给的是打印页码 | 拒绝 |
| `E_MGMT_TARGET_INDEPENDENT` | `source_type = management_target` 且 `independence_group` 与同实体披露同组 | 拒绝 |
| `E_UNKNOWN_MODEL` | `model_id` 不在 31 个注册 model_id 中 | 拒绝 |
| `E_UNKNOWN_DRIVER` | `driver_name` 不在该 model 卡的 driver 列表 | 拒绝 |
| `E_DUPLICATE_PARAMETER` | 两个命题同 `parameter_id` 但不同 driver/期间 | 拒绝 |
| `E_MISSING_FALSIFIER` | `falsifier` 五要素缺一 | 拒绝 |
| `E_MISSING_REFUTED_BY` | `refuted_by` 为空 | 拒绝 |
| `E_NO_DOUBLE_COUNT_RULE` | `double_count_exclusion` 为空 | 拒绝 |
| `E_SOURCE_HASH_MISMATCH` | 命题引用的 `source.sha256` 与实际文件不符 | 拒绝 |
| `E_ANCHOR_NOT_FOUND` | `anchor_text` 在对应的取文输出中找不到 | 拒绝 |
| `E_STATE_APPROVED_BY_IMPLEMENTER` | `state = approved_frozen` 且 `reviewer` 非独立 | 拒绝 |
| `E_LISTED_VALUE_NOT_IN_EVIDENCE` | 引用数值串在 `evidence_path` 输出中找不到 | 拒绝 |

**O-17（期望）**：反例集必须**真的运行**（每条一个独立 patch），并保存原始输出；
不得只写“已覆盖”。正例（当前 `hypotheses.json`）必须全部通过，且正例通过不能取消反例。

## 8. 停止条件（触发即停并记录，不用“下一步再说”代替）

- S1：raw sha256 与 I-00-A 基线不符 → 停止，出漂移报告。
- S2：`anchor_text` 在任何路径都定位不到 → 该命题 `STOP_EVIDENCE`，且不得换成别的页码/别的数字。
- S3：某命题需要 `approved_frozen` 才能进入下一步 → 停在 `pending_professional_decision`，交行业 reviewer。
- S4：发现卡正文与上游原义务（`implementation_plan.md` I-11、`research_cards.md` I-11 与 I-11-A）
  存在算式/口径矛盾 → 停下，写 `decision.md` 的冲突节 + `handoff.owner_action_required`，
  **不得**自行改索引文档、不得换例子绕过。
- S5：同一命令两次相同失败 → 停止盲重试，比较失败原因与绑定后交 owner。

## 9. 本卡明确不产生的东西（防止下游误用）

- 不产生任何参数幅度（low/base/high 数值）→ I-11-B。
- 不产生 `approved_frozen` 命题 → 需行业 reviewer。
- 不产生 HK 的原文数值 → 原文在本 attempt 不可读（若 E4 成立）。
- 不产生准确性证据、不产生预测、不产生发布资格。
