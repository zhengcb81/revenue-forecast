# I-11-A decision.md：冻结定性到参数的可证伪命题（设计决定 + 开放项）

card_id: I-11-A · attempt_id: a20260919-01 · 角色：实现者（弱模型）
状态：`review_pending`（**本文件不构成验收；实现者不自签 accepted**）

决定清单索引：DEC-1 … DEC-12 为本次必须做的设计决定；OPEN-1 … OPEN-8 为无法由我独立决定、
需要 owner/专业 reviewer 裁定的事项。每个决定的格式固定为：
**选项 / 选择与理由 / 反例（什么会推翻这个选择）/ 兼容影响 / 恢复规则 / 被拒绝的替代方案**。
不得用"按最佳实践"代替决定：凡是没有依据的判断，一律登记为开放项而不是写成决定。

---

## DEC-1 取文路径：用自制标准库取文器 + 仓库外控制台工具，而不是全局 Miniconda 的 PDF 库

**选项**
- (a) 用全局 `C:\Miniconda\python.exe`（自带 PyMuPDF 1.26.7 / pdfplumber / pypdf）取文；
- (b) 只用 attempt 隔离 venv（无 PDF 库，禁网）→ 放弃读取 PDF 原文；
- (c) 在隔离 venv 内自制纯标准库取文器（P1），并增加一条**代码不共享**的独立路径
      `pdftotext.exe`（P2，Git for Windows 自带，Xpdf 4.00）交叉验证。

**选择与理由**：选 (c)。(a) 被 START_HERE 明文禁止（"禁止用全局 Miniconda 跑卡"），
且会把未登记的运行时依赖带进证据链；(b) 会让"每命题有可追溯来源"直接失败，等于用工具限制作借口
放弃卡的核心交付；(c) 在隔离解释器内运行、依赖可枚举（只用 `re`/`zlib`/`hashlib`/`json`），
并且用 P2 做独立复现，避免"我的取文器错了但我不知道"。

**反例**：若 P1 与 P2 对同一页给出**互相矛盾**的被引用数值，则 (c) 的可信度假设失效 →
必须停下来人工看 PDF 页面图像，并把该页所有引用作废。本次未出现矛盾（Zijin 恒等式 A1–A3 在两条
路径下都能复算为 0；P1 与 prior artifact 的逐页数值交叉核对通过）。
若 owner 否决使用仓库外工具（OPEN-1），(c) 退化为"只有 P1"的单路径，交叉验证能力消失。

**兼容影响**：不引入 Python 依赖，不改任何 venv 的 site-packages；P2 的存在只影响本 attempt 的
证据面。下游若使用"P2 已被批准"这一表述，必须先取得 OPEN-1 的裁定。

**恢复规则**：若 `pdftotext.exe` 的 sha256 变化（Git 升级），历史证据仍指向本次记录的
sha256 `252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0`；
新版本必须重新生成证据，不得沿用旧输出。

**被拒绝的替代方案**
- 从全局 site-packages 把 `fitz` 复制进 attempt venv：等价于绕过"不用全局解释器"的禁令，
  且二进制扩展的 ABI/版本无法在证据里闭合；
- 用 `pip install pypdf`：本卡禁网，且离线 wheel 不存在（已验证 `--no-index` 失败）；
- 只引用既有审计目录里的文本：那是**二手产物**，不能让"原文可核"成立。

---

## DEC-2 页面索引口径：本卡使用 `pdf_leaf_1based` 与 `table_index_0based`，并显式登记为开放项

**选项**：(a) 用 PDF 阅读器显示的打印页码；(b) 用 PDF 物理页（leaf，从 1 起）；
(c) 用文档内部对象号（page object number）；(d) 用"章节+锚文本"而不给页码。

**选择与理由**：选 (b)（HTML 表格用 0 基序号，理由同构）。紫金年报的 A 股 PDF 的打印页脚与
物理页相差常量 1（例如物理页 327 的页脚为 "-219 -"），直接用打印页码会让下游在重排/替换版式后
错位；物理页号在 PDF 内部可复现（`classic_page_numbers` 的序号即 leaf 序号）。
(d) 单独使用不够：锚文本可能跨页重复，必须与物理页组合。

**反例**：若同一发行人更换版式（增删封面/目录页）导致 leaf 序号整体位移，则历史 `page_span`
失效 → 必须用 `anchor_text` 重新定位并把新 leaf 号写入新版本（不覆盖旧快照）。
本次实测到该风险的具体形态：既有审计产物 `PRIOR-EXTRACT-ZIJIN` 的页号与物理页相差 1，
说明"页号"本身是易漂移的定位键。

**兼容影响**：`common_model_cards.md` 要求披露字段含 `page/table/span`，但未规定索引口径；
若 I-10-A/I-07-E 的采集脚本假定打印页码，本卡的 `page_span` 需要重映射（OPEN-4）。

**恢复规则**：任何页号引用都必须同时给出 `anchor_text`；定位失败即按 oracle S2 判 `STOP_EVIDENCE`，
不得改页码迁就。

**被拒绝的替代方案**：(a) 打印页码——与 PDF 结构无固定关系；(c) 对象号——不同解析器对
对象流的编号可能不同，跨工具不可移植。

---

## DEC-3 命题状态机：只允许五态，`approved_frozen` 在无独立 reviewer 时禁止出现

**选项**：(a) 允许实现者把"证据齐全"的命题标为 approved；(b) 只有 `unquantified`/`pending`
两态；(c) 五态（`unquantified`、`pending_professional_decision`、`approved_frozen`、
`STOP_EVIDENCE`、`STOP_DISCLOSURE_ADAPTATION`），且本卡内 `approved_frozen` 计数必须为 0。

**选择与理由**：选 (c)。卡正文的验收要求"明确 unquantified/approved 状态"，因此 approved 必须
存在于**状态空间**；但 START_HERE 第 26 行规定"实现者不能自签 accepted"，所以本 attempt 的
`approved_frozen` 计数必须为 0，由行业 reviewer 在独立审查中写入。这一条被写成可执行检查
（oracle O-8 + `validate_hypotheses.py` 的 `E_STATE_APPROVED_BY_IMPLEMENTER` 反例），
而不是口号。

**反例**：若下游把 `pending_professional_decision` 当成"实质已批准"继续做幅度校准，则状态机
被绕过。防这一点的具体机制：命题 4/7 的 `parameter_id` 带 `_PLACEHOLDER` 后缀，
使 I-11-B 的脚本无法把它误当已审定参数。

**兼容影响**：I-11-B 的前提是"I-11-A 命题已批准"；本 attempt 产生 **0** 条 approved，
因此 I-11-B **仍未解锁**（这是正确结果，不是缺陷）。I-11-C 依赖 I-11-B，同样未解锁。

**恢复规则**：reviewer 若给出 `changes_required`，按意见新建 revision 并在 `oracle.md` 追加 R2 附录，
不覆盖本次已冻结的正文与证据（recovery/README.md 写明步骤）。

**被拒绝的替代方案**：(a) 会让实现者替专业 reviewer 做经济判断（START_HERE 第 47 行明令禁止）；
(b) 会让"approved"这个下游需要的状态永远无法出现，I-11-B 永远无法开工。

---

## DEC-4 来源类型与独立性：管理层目标必须单列，且与同实体披露不同组

**选项**：(a) 把管理层目标与公司披露合并为"公司来源"一组；(b) 单列 `management_target`，
并把同一年报里的产量计划放进独立组 `ZIJIN-MGMT-PLAN-2026`；(c) 把管理层目标完全排除在命题之外。

**选择与理由**：选 (b)。卡正文动作 2 明确要求"把管理层目标单列 source_type，按原始来源归并
independence_group；十篇转述同一电话会算一个来源"。落到具体实现：
`ZIJIN-AR2025`（合并报表与产销量表）、`ZIJIN-MGMT-PLAN-2026`（经营计划里的 2026 产量计划）、
`MSFT-10K-FY2026` 三组；并且 `calibration.management_target_is_not_independent = true`。
(c) 被拒绝是因为计划值本身是有信息量的情景对照，排除它会丢失"管理层隐含什么"这一买方问题。

**反例**：若把 2026 产量计划与 2025 实际产量放在同一组，"计划达成率"就会被当成独立证据
（同一主体对同一事项的两种陈述不构成独立验证）。`validate_hypotheses.py` 的
`E_MGMT_TARGET_INDEPENDENT` 反例正是针对这一失效模式。

**兼容影响**：I-11-B 的 `calibration.management_target_is_not_independent` 语义被本卡固定为
"必须为 true"；I-12 的准确性样本不得把管理层目标当基准真值。

**恢复规则**：若未来出现**第三方独立观察**（例如交易所公布的行业产量、独立机构价格序列），
它必须落在新的 independence_group，且不得与公司披露互为验证。

**被拒绝的替代方案**：(a) 会让本卡最重要的诚实性要求失效；(c) 过度收缩，丢掉可审计的目标台账。

---

## DEC-5 参数落点：只落到 `model_cards.md` 已注册的 model_id/driver_name，落不下的判 pending

**选项**：(a) 允许自造 driver 名（例如 `brand_strength`、`capacity_utilization_rate`）；
(b) 只允许已注册 driver；落不下时标 `pending_professional_decision`（机制存在但没有已注册参数可落）；
(c) 落不下就一律标 `unquantified`。

**选择与理由**：选 (b)。card 正文动作 3 要求"指定唯一或显式多个 parameter_id"，而参数最终必须
进入 M01–M31 的计算器；自造 driver 名会让 I-11-B 无法执行。(c) 会掩盖"机制清楚、只是缺参数槽"
与"机制本身不清楚"的区别——这两者对 reviewer 的含义完全不同：
前者是接口问题（可在 I-10-A 扩展模型时解决），后者是研究问题（需要新证据）。
本次 8 条命题中 6 条判 `pending`、2 条判 `unquantified`，正是按这个区分落的。

**反例**：若某条命题的 driver 实际上需要"新增模型族"才能表达（例如把云容量与消耗拆开），
那么 pending 会无限期挂着 → 必须升级为 I-10 的模型扩展请求。本次未出现该情形，但
命题 8（许可/云拆分）接近这一边界（缺的是披露而非模型）。

**兼容影响**：`validate_hypotheses.py` 内置了 31 个 model_id 及其必填/可选 driver 列表
（逐字抄自 `model_cards.md`）。若 M 卡的 driver 列表变更，本卡的校验会变得**过严**
（合法 driver 被判 E_UNKNOWN_DRIVER）→ 校验脚本的 `REGISTERED` 必须随 M 卡版本更新，
并重跑反例套件。

**恢复规则**：driver 列表变更时，先更新 `REGISTERED` 并重跑 `validate_hypotheses.py`；
若已有命题的 driver 被下线，该命题退回 `pending_professional_decision` 并保留旧快照。

**被拒绝的替代方案**：(a) 破坏与 I-11-B 的接口，且会让"参数可复核"变成空话。

---

## DEC-6 falsifier 阈值分两类：算术恒等式类直接冻结，判断类保留占位并交专业审定

**选项**：(a) 本卡自行给出全部幅度阈值（例如"±5%"当作已审定）；(b) 全部阈值留空，交 I-11-C；
(c) 分两类：算术恒等式类给**精确值**（差为 0），专业判断类给出**占位阈值**并显式标注
`threshold_basis = "professional_judgement_required"`。

**选择与理由**：选 (c)。(a) 是"用最佳实践代替决定"，且 I-11-C 的验收要求"阈值必须专业审定"，
我无权自定；(b) 会使本卡核心要求（"预先登记什么观测会推翻它"）落空，因为 falsifier 五要素里
`threshold` 为空等于没有可推翻条件。(c) 让每条命题**立刻**具备可执行的推翻条件，
同时把"数值是否合适"这一专业判断明确挂到 OPEN-6。
本次 8 条命题：4 条算术恒等式类（差 0）、4 条判断类（±5%、0.9–1.1 等占位）。

**反例**：若 reviewer 认为占位阈值本身就会诱导下游按此执行（例如把 ±5% 当成已审定），
那么 (c) 的收益被风险抵消 → 缓解手段是 `threshold_basis` 字段 + OPEN-6 + I-11-B 前提未满足
（本卡 0 条 approved）。若 reviewer 仍不接受，可要求把占位阈值改为"仅记录观测量、不给数"，
代价是 falsifier 五要素不全。

**兼容影响**：I-11-C 复用本卡的 `falsifier` 结构，因此 `threshold_basis` 现在是跨卡字段；
I-11-C 若新增枚举值必须同时更新本卡校验脚本，否则会被判为未知值（当前校验只检查非空，
不做枚举白名单，属于有意的宽松）。

**恢复规则**：阈值被专业审定后，写入命题的新版本（`decision.decision_sha256` 填审定记录的 hash），
旧版本保留供 I-12 评分。

**被拒绝的替代方案**：(a) 越权；(b) 不满足卡的验收要求。

---

## DEC-7 双计排除：写成"互斥口径清单"，而不是一句"已检查"

**选项**：(a) 每条命题写"已做双计检查"；(b) 逐条写出**互斥的两套口径**与禁止组合；
(c) 建立全局 driver 依赖图，由脚本检测冲突。

**选择与理由**：选 (b)，并把最危险的一条升级为独立命题（H-CN-ZIJIN-ELIM-05）。(a) 无法复核；
(c) 在当前阶段不可行——因为参数幅度尚未校准（I-11-B），依赖图没有权重与相关性信息，
过早建图会产生"看起来严谨但无内容"的产物。
(b) 的具体产物是每条命题的 `double_count_exclusion` 字段，例如
"584,049,229,264 与 349,079,082,852 不得同时作为收入基期"。

**反例**：若某条命题的双计风险来自**跨命题**而非命题内部（例如命题 1 的 revenue 与命题 5 的
reconciliation 参数指向同一笔收入），(b) 的表达力不足。已知的具体跨命题对：H-CN-ZIJIN-SEG-01
与 H-CN-ZIJIN-ELIM-05（同一合并收入的两种呈现）→ 已在命题 5 里用 `unquantified` 处理
（不单独设可量化 driver），并在 §2.2 表格中列出。

**兼容影响**：I-11-B 的 `dependency_control.shared_driver_ids` 需要跨命题的 driver 复用表；
本卡已提供 `parameter_id` 与 driver 的完整映射（14 个参数），I-11-B 可直接消费。

**恢复规则**：若 I-11-B 发现新的双计组合，必须回到本卡新增命题或修订 `double_count_exclusion`，
不得在幅度层"两个都调小一点"了事。

**被拒绝的替代方案**：(a) 形式主义；(c) 时机不对（会先造无用产物）。

---

## DEC-8 港股来源（小米）：判 `STOP_EVIDENCE` 而不是用二手转述补位

**选项**：(a) 引用 revenue-forecast 审计目录中已有的小米研究稿（含分部收入与假设）；
(b) 只引用小米年报的 raw hash 与 sidecar 元数据，不给任何数值；
(c) 两条路径都不可读时，把该来源标 `not_readable_in_this_attempt` / `STOP_EVIDENCE`，
并在 `source_map.json` 与 `mechanism_review.md` 记录可复核的失败证据。

**选择与理由**：选 (c)。(a) 违反卡正文的停止条件（"原文无法核查 → STOP_EVIDENCE"）
与 review_and_handoff 的"不得仅交文件名/hash"精神——二手研究稿不是原文；
(b) 会让"来源晚于 as_of 或原文无法核查"的判定缺证据。本次实测：标准库路径 0 字符，
`pdftotext` 输出乱码，两者都已落盘可复核。

**反例**：若有人主张"手机/汽车分部收入结构众所周知，可以直接用公开常识建模"，则 (c) 的
"无港股命题"会被视为过度保守 → 但这不是本卡可以自行放宽的：**放宽证据门必须由专业 reviewer
决定**，且常识不是可核原文。若 owner 认为本卡可以只做 CN/US，那也应显式写入卡的适用范围，
而不是让实现者默认。

**兼容影响**：`sample_manifest.json` 的 HK-XIAOMI-2025 样本在本卡**未被消费**；
I-07-B/I-11-B 若需要港股分部参数，必须先解决 OPEN-5。

**恢复规则**：可读性恢复后（工具或依赖变更），新建 attempt 重新取证；不得把本次的
`not_readable` 判定改成"已验证"。

**被拒绝的替代方案**：(a) 用非原文来源冒充实证；(b) 只留 hash 会造成"看起来做了"的假象。

---

## DEC-9 计数与枚举必须由脚本产出

**选项**：(a) 在 md/json 里手写计数（"共 8 条命题、6 条 pending…"）；(b) 全部计数由脚本在
运行时统计并写入机器可读字段，md 文档引用同源字段。

**选择与理由**：选 (b)。卡正文明确"任何'数量/比例/枚举完整性'的声称都要落盘枚举脚本与输出；
不许手抄计数"。实现方式：`build_hypotheses.py` 产出 `source_map.counts`，
`validate_hypotheses.py` 产出 `validation_report.counts`，`mechanism_review.md` 顶部表格逐项标注
来源字段名。

**反例**：若 md 与 json 的计数出现分歧（例如我事后改了一条命题但没重跑脚本），(b) 也会失效。
防这一点：本 attempt 的最终交付前重跑 `build_hypotheses.py` → `validate_hypotheses.py`
→ 重新核对 md 顶部表格（见 handoff 的 `next_action` 与 `commands_executed`）。

**兼容影响**：下游脚本可以只读 json 计数，不必解析 md。

**恢复规则**：任何命题增删后必须重跑三个脚本（build / validate / arithmetic），否则视为交付不完整。

**被拒绝的替代方案**：(a) 已被本 attempt 的实际教训否定——见 DEC-10。

---

## DEC-10 自查抓到"我自己写错的数字"时的处理：改证据源并如实登记，不改期望迁就

**事实**：命题 2 初稿的 `original_value` 写成 `109,977,556,345 ÷ 885,141 = 124,242.28`。
该商无法由任何被引用原始串复算（正确值为 `109977556345/885141 ≈ 124,248.63`；
且 885,141 不是我引用过的任何量——我引用的是铜销量 884,943 吨与金销量 83,161 千克）。

**选项**：(a) 把 oracle 的复算要求放宽（例如允许 ±1% 容差）让错的数字"通过"；
(b) 悄悄改成正确值，不记录；(c) 改正数值、把推导与**敏感性**写进 `conversion_formula`，
并在 `mechanism_review.md` §6 如实登记这是转录错误。

**选择与理由**：选 (c)。(a) 正是 START_HERE 第 5 步禁止的"修改 oracle 来贴合结果"；
(b) 会让 reviewer 无法判断我的其他数字是否也经过复算。

**反例**：若把每个我写错的数字都当成"必须公开的事故"，文档会被噪声淹没 → 判据是
"该数字是否进入了冻结产物（hypotheses/oracle/source_map）"：进入的必须登记，草稿里改掉的不登记。

**兼容影响**：无（仅本 attempt 内部）。

**恢复规则**：reviewer 若发现别的同类错误，按同样方式登记并要求我重跑三个脚本。

**被拒绝的替代方案**：(a) 破坏本卡最重要的证据原则；(b) 隐瞒。

---

## DEC-11 冲突处置：发现卡正文/上游口径冲突时停下登记，不自行改索引文档

**本次发现的冲突/张力（登记，不修改任何上游文件）**

1. **oracle O-6 与实测偏移的措辞冲突**：O-6 写"被引用页面上的被引用数值串必须出现在 prior artifact
   **同页**文本中"，但实测 prior artifact 的页号与 PDF 物理页相差常量 1（择优 offset = +1）。
   该冲突是**我自己写的 oracle 内部不一致**（写 O-6 时偏移尚未测定），已按 OPEN-8 登记；
   oracle 正文**未回改**（按 START_HERE，oracle 只能在运行前冻结，事后修改须以 R2 附录追加）。
2. **`common_model_cards.md` 的披露字段枚举与 PDF 审计现实**：该文件要求 `page/table/span`，
   但未规定页码口径；PDF 审计必须区分物理页与打印页。已按 OPEN-4 登记，属 schema 层问题，
   不属本卡可自行决定的范围。
3. **`common_research_cards.md` 的 I-11 模板与卡正文的字段差**：模板没有
   `state` / `page_index_basis` / `anchor_text` / `evidence_path` / `refuted_by` 等字段，
   而 I-11-A 的验收要求"明确 unquantified/approved 状态"与"可追溯来源"。本 attempt 采取
   **超集**策略（模板字段全保留 + 追加字段），不改模板文件。已按 OPEN-4/OPEN-6 部分覆盖，
   但"模板是否应升级为超集"本身是一个 owner 决定 → **OPEN-9**。

**选择与理由**：登记 + 超集实现 + 不改上游索引文档。START_HERE 第 40 行与用户纪律都禁止
执行者自行改索引文档或换例子绕过。

**反例**：若 reviewer 认为"超集字段"破坏了跨卡 schema 兼容（例如 I-11-B 的脚本按模板严格
校验字段集合），则本卡的输出会被拒 → 届时应由 schema owner 一次性升级模板，而不是让每张卡
各自扩字段。

**恢复规则**：上游文档更新后，本 attempt 的产物**不需要**重写（超集兼容），但
`validate_hypotheses.py` 的字段清单必须与新模板对齐。

**被拒绝的替代方案**：自行修改 `common_research_cards.md` / `research_cards.md` /
`implementation_plan.md`（越权，且会让别的卡失去稳定索引）。

---

## DEC-12 资格边界：三资格分开陈述，本卡只做取证不做适配/准确性

**选项**：(a) 把"命题填满模板 + 恒等式复算通过"表述为"披露适配通过"；
(b) 明确 formula = `not_applicable_here`（本卡不执行任何模型）、disclosure_adaptation = `not_granted`
（I-10-A 所有）、accuracy = `not_granted`（I-12 所有），并在每条命题里重复该三栏。

**选择与理由**：选 (b)。用户纪律与 `common_research_cards.md` 开头都明确"三种资格独立"。
本卡的 8 条命题因此在 `three_qualifications` 字段里逐条携带三栏状态，防止下游只看顶层摘要。

**反例**：若下游把本卡的"pending_professional_decision + 恒等式差 0"读成"该公司口径已适配"，
就会发生资格越界 → 缓解手段是 `PLACEHOLDER` 参数名 + 三栏字段 + mechanism_review §2.3 的提醒。

**兼容影响**：I-07-E 消费披露适配资格时必须来自 I-10-A 的产物，而不是本卡。

**恢复规则**：无（这是边界声明，不会"恢复"）。

**被拒绝的替代方案**：(a) 夸大资格，正是本计划要防的核心失效模式。

---

## 开放项（无法由我独立决定；含裁定人与是否阻塞签收）

| 编号 | 问题 | 裁定人 | 阻塞 I-11-A 签收？ | 阻塞什么 |
|---|---|---|---|---|
| OPEN-1 | 允许使用仓库外控制台工具 `pdftotext.exe` 作为第二条取文路径吗？ | PLAN owner / 环境规范制定者 | 否（已登记 argv/hash/输出） | 若否决，I-11-B 前需另找独立路径 |
| OPEN-2 | 紫金矿产品"铜当量换算系数"从何而来？结论对其高度敏感（每 +1 吨/千克 ≈ 10,670.9 元/吨铜当量） | 会计 reviewer + 矿业行业 reviewer | 否 | I-11-B 对 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的幅度校准 |
| OPEN-3 | FY2027 起微软建模分部是否仍为 PBP/IC/MPC（2026-09-02 8-K 的重分类原文不在本地可核来源） | 行业 reviewer（软件与云）+ 会计 reviewer | 否 | I-11-B/I-07-E 的微软分部选择 |
| OPEN-4 | `pdf_leaf_1based` / `table_index_0based` 是否需成为披露字段的规范枚举值 | schema owner | 否 | 跨卡页码复用 |
| OPEN-5 | 港股（小米）年报原文可读性由谁解决 | 环境/依赖 owner + 行业 reviewer | 否 | 任何港股份部命题 + I-11-B 港股参数 |
| OPEN-6 | 4 条 `professional_judgement_required` 阈值（±5%、0.9–1.1 等）是否按此采用 | 行业 reviewer（分行业） | 否 | I-11-B/I-11-C 的触发器生效 |
| OPEN-7 | 命题 1/6 的分部集合是否就是 FY2027 的最小建模块 | 行业 reviewer | 否 | 分部集合变更时的重建工作 |
| OPEN-8 | oracle O-6 的页号措辞与实测 offset=+1 不一致，如何处置（R2 附录 or 接受择优规则） | 独立 reviewer（oracle 读者） | 否 | 后续读者的页码假设 |
| OPEN-9 | I-11 参数模板是否应升级为本卡的超集字段（`state`/`page_index_basis`/`anchor_text`/`evidence_path`/`refuted_by`） | `common_research_cards.md` 的 owner | 否 | 跨卡 schema 一致性 |
| OPEN-10 | `PLAN/reviews` 目录的 LastWriteTime 实测为 `2026-09-19 09:14:20`，与任务说明要求的 `10:05` 不符；本 attempt 未写入该目录（state_before/after 记录一致，且 285 个文件中无任何文件的 mtime 晚于本 attempt 开始时间） | PLAN owner（核对是否说明有误或期间有他方写入） | 否 | 后续卡对 reviews 只读性的基线判断 |

**没有任何一项阻塞本卡签收**；但 OPEN-2 / OPEN-3 / OPEN-5 / OPEN-6 **阻塞 I-11-B**，
因此 I-11-B 不能在本次之后自动开工。

---

## 本卡明确不做的事（防止下游误读）

- 不给参数幅度（low/base/high 全为 `null`）——属 I-11-B；
- 不写 `approved_frozen` 命题——属行业 reviewer；
- 不引用港股原文——原文在本 attempt 不可读；
- 不做反方独立审查——属 I-11-C；
- 不运行任何模型、不产生预测、不产生准确性证据。
