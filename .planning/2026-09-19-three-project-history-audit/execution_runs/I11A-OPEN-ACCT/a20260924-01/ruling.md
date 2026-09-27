# I-11-A 开放问题 · 会计/披露维度裁定（accounting specialist reviewer）

- card：`I-11-A`
- 本载体 attempt：`execution_runs/I11A-OPEN-ACCT/a20260924-01`
- 角色：`accounting_specialist_reviewer`（会计 reviewer，会计/披露口径维度）
- 被审对象：`execution_runs/I-11-A/a20260919-01/`（accepted_scoped 封盘 attempt，**只读**）
- 生成时间（UTC）：2026-09-24T20:2x:xxZ（外部取证实测窗口 2026-09-24T20:23:20Z – 20:23:31Z，另有一次同窗口内的先前尝试，见 provenance.json）
- 本文件是**新增裁定载体**：不修改 I-11-A 的任何 `status`/字段、不代签、不构成对 I-11-A 的验收。

---

## ① 身份与授权引用（owner 原文，逐字）

| 授权点 | 原文（逐字） | 出处 |
|---|---|---|
| 指派 | 「…**I-11-A OPEN-2/3/5/6 指派会计+行业 reviewer**…」 | `OWNER_DECISIONS.md` §十 **L116**（owner 2026-09-20 原话） |
| 执行行 | 「**I-11-A OPEN-2/3/5/6** | **指派**：会计 + 行业（矿业/软件）reviewer | 编排层按此派单；**OPEN-2/3/5/6 阻塞 I-11-B / I-07-E** | **I-11-B / I-07-E**（待专家裁定）」 | `OWNER_DECISIONS.md` §十 **L127** |
| 第二批 | 「| 2 | I-11-A OPEN-2/3/5/6 | **派新 subagent** 当行业 reviewer | 编排层创建独立行业 reviewer subagent |」 | `OWNER_DECISIONS.md` §十一 **L144** |
| 职权边界（评审意见格式） | 「以下先写`decision.md`，由对应专业reviewer给出明确选项及理由，之后再实施：…财期/重述/收入总净额和payability归属；不可识别模型参数；样本/基准/统计阈值及概率校准…审查意见至少包含选择、理由、反例、兼容影响、恢复规则、拒绝的替代方案。不得用"按最佳实践"代替决定。」 | `execution_v2/START_HERE.md` **L47** |
| fail-closed 依据 | 「…**专业决策未定先blocked**。」 | `execution_v2/START_HERE.md` **L36**（九步第 4 步） |
| 不代签依据 | 「review_pending | 正反例/恢复/差异证据齐全 | **实现者不能自签accepted**」 | `execution_v2/START_HERE.md` **L26** |
| 卡停止条件 | 「来源晚于as_of或原文无法核查→**STOP_EVIDENCE**」；「无法定位模型driver/收入确认环节→仅保留定性未量化」 | `execution_v2/card_I-11-A.md` **L21**、**L20** |

**我 = 上述指派的执行者之一（会计维度）**。以下只裁我有资格裁的维度；越权部分一律标 `BLOCKED` 或 `NOT_IN_MY_SCOPE`。

---

## ② 范围声明（我裁什么、不裁什么）

**我裁（会计/披露维度）：**

1. `OPEN-2`：铜当量换算系数在**会计/披露口径**上可接受的来源分级、使用时**必须披露什么**、以及**无公司披露时的替代方案与 fail-closed 默认**。
2. `OPEN-3`：分部口径变更在会计上的**可接受证据等级（什么才算"已核"）**、8-K 原文本地不可得时的 fail-closed 处置、以及"沿用 as_of 时点分部 + 显式口径风险标注"是否可接受。
3. `OPEN-6`（**规则面**）：占位阈值在审定前能否被下游当作已审定值使用；审定一个阈值**必须具备什么证据基础**（我给"用什么基础才允许给数"的规则）。

**我不裁（明确让位）：**

- `OPEN-2` 的**矿业地质/市场维度**：具体系数取值（例如 1 千克金 = 24 吨铜当量是否合理）、品位/回收率/价格假设的行业惯例、可比矿山做法 —— 归**矿业行业 reviewer**（另有工位）。
- `OPEN-3` 的**微软业务实质**：FY2027 应该按什么分部建模、新分部架构的商业含义、八条业务曲线的行业判断 —— 归**行业 reviewer（软件与云）**。
- `OPEN-6` 的**阈值数值本身**（±5%、[0.9, 1.1] 是否恰当）—— 归**行业/专业 reviewer**；我只给"给数的前置条件"。
- `OPEN-5`：`NOT_IN_MY_SCOPE`（见 §3.4）。
- I-11-A 的签收/状态/`approved_frozen` 写入 —— 我**不代签、不改状态**。

**分工声明（须写进任何下游引用）**：OPEN-2 / OPEN-3 是**双 reviewer 联合裁定项**，本文件只覆盖其中的**会计与披露口径半区**；行业半区未裁定前，OPEN-2/OPEN-3 **不得**被记为"已全部裁定"，I-11-B / I-07-E 的相应解锁**不因本文件而成立**。

---

## ③ 逐条裁定

### 3.1 本文件使用的两套分级（先定义，后引用）

**来源可采性分级（OPEN-2 用，会计面）**

| 级 | 定义 | 可否支撑"已冻结参数" |
|---|---|---|
| **S1** | 公司/发行人**同一期间原文披露**：可定位到页/表/锚文本，doc sha256 已绑定，至少一条独立路径复核 | 可 |
| **S2** | **准则/监管或交易所明文口径**，且其全部输入（价格序列、回收率、payability…）本身可核、算术可复算；须由**非实现者** reviewer 显式"采用"并留 `decision_sha256` | 可（须带"采用声明"） |
| **S3** | 第三方独立估计（行业调研均值、可比公司做法），方法论不可复核 | **否**：只可用于敏感性带（low/high），不可作点估计放行 |
| **S4** | 分析师自设/示意假设（本卡的"1 千克金 = 24 吨铜当量（示意值）"） | **否**：只能以 `_PLACEHOLDER` + `expert_assumption` 登记 |
| **S0** | 不可得 / 不可核 | **否**：参数保持 `_PLACEHOLDER`，**不得放行** |

**披露证据等级（OPEN-3 用，会计面）**

| 级 | 定义 | 可支撑什么 |
|---|---|---|
| **E1 已核** | 申报原文**本地归档**：URL + 取回 UTC + 文件 sha256 + 逐字引文 + 至少一条独立复核路径（同本卡 P1/P2 双路径精神） | 参数、口径声明、"已核"字样 |
| **E2 可引未归档** | 在线取回但只留 URL/时间/引文，未落本地归档 | **仅**叙述与风险提示；**不得**支撑参数或"已核" |
| **E3 二手** | 研究稿、web 工具转录、新闻、搜索摘要 | **仅**用于提出问题 |
| **E0** | 记忆 / 共识 / "众所周知" | 不是证据 |

---

### 3.2 OPEN-2 · 会计/披露维度裁定

**裁定（一句话）：RULING —— 铜当量换算系数只有 S1（公司原文披露）与 S2（全输入可核、经非实现者签署采用的准则化口径）两类来源可支撑冻结；S3 仅可作敏感性带、S4 示意值不可作参数；本地语料当前**无任何 S1/S2**，故 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 必须按 S0 处置 —— 参数保持 `_PLACEHOLDER`、I-11-B 不得放行幅度校准，替代方案是回退到"分部对外收入 + 分金属销量"的无换算口径（或整条转 `unquantified`）。**

#### 裁定 A-2.1：可接受的系数来源类型（会计面排序）

1. **S1 公司披露**（首选，唯一无需附加条件即可冻结的来源）：公司在与分子同一报告期的年报/公告/技术报告中给出铜当量系数或可推出该系数的完整要素。
2. **S2 准则/监管化口径**（次选，需附加条件）：采用有明文定义的换算口径（价格基准、回收率、payability、包含金属范围全部写明），且每个输入自身可核、算术可复算；须由**非实现者**会计/行业 reviewer 显式"采用"，留 `decision_sha256` 与生效范围（`hypothesis_id`/`parameter_id`）。
3. **S3 行业标准/调研均值/可比公司做法**：**不得**作为点估计冻结；**仅**允许用来设定敏感性带（low/high），并按 `expert_assumption` 登记、单列 `independence_group`，不得因使用它而放行参数。
4. **S4 分析师自设/示意值**：**不得**作为参数（本卡 `1 千克金 = 24 吨铜当量（示意值）` 正属此类）。
5. **反向推导（用收入 ÷ 假设价 × 假设量倒算系数）**：循环论证，**不可采**。

> 说明：以上是**可采性**规则，不含任何具体系数值；"24 吨/千克是否接近市场惯例"属矿业行业 reviewer 的半区，我不裁。

#### 裁定 A-2.2：使用系数时**必须披露**的最小集合（缺一即视为披露不足）

1. 系数值 + 单位 + 换算方向（哪一种金属 → 铜当量）+ **纳入/排除**的金属范围（金/银/锌/钼是否计入）；
2. 价格假设：所用价格序列、币种、基准日（`as_of`），及其原文出处；
3. 回收率 / 品位 / payability（TC/RC、应付比例）假设及其出处；
4. 分母的完整算式与两项原始披露值（本卡：`885,141 = 884,943 吨 + 83,161 千克 × 24`），含页码/表号/锚文本/doc sha256；
5. **敏感性**：系数每 +1 吨/千克 ⇒ 分母 +83,161 吨 ⇒ 单位收入 −10,670.89 元/吨（**两点差分、非偏导**；分母单独 +1 吨仅约 0.14 元/吨）；
6. 来源等级声明：`source_tier ∈ {S1,S2,S3,S4,S0}` + 明示"公司是否披露"（当前：**未披露**）；
7. **单次使用声明**：系数只在量的口径转换中出现一次（对应 `hypotheses.json` L189 `double_count_check`），价格侧不得二次折算；
8. **口径警示**：元/吨铜当量**含全部矿产品**，不得当作铜价使用（对应 L175 口径暴露二）。

#### 裁定 A-2.3：无公司披露时的替代方案（fail-closed 阶梯）

1. **单位回退（首选）**：只用披露单位计量 —— 收入侧用**分部对外收入（元）**，量侧用**分金属销量**（铜 吨、金 千克），不做混合金属分母；单位经济学若必须给出，按金属分别给（并须符合 M09 `realized_price` 的 driver 注册规则，见兼容影响）。
2. **接口不可回避时**：若下游接口强制要求"元/吨铜当量"字段，则该字段**必须**带 `_PLACEHOLDER` 后缀 + `unit_conversion_status = undisclosed` + `source_tier = S0`，且任何脚本不得对其取值。
3. **整条回退**：若连分金属口径也无法闭合，按卡停止条件转 `unquantified`（保留叙述机制链），并由 I-10-A 披露适配侧记录 `STOP_DISCLOSURE_ADAPTATION` —— 与独立 reviewer 已签意见一致（review.md L126：「铜当量系数未披露，该式判 STOP_DISCLOSURE_ADAPTATION 是正确的」）。
4. **明确结论：不可得 ⇒ 参数保持 `_PLACEHOLDER` 且不得放行**（本条被 owner 题面点名，予以确认）。

#### 依据（本地可核）

- `decision.md` **L398**（OPEN-2 行：问题、敏感性 −10,670.89、裁定人=会计+矿业行业 reviewer、阻塞 I-11-B 幅度校准）、**L410–411**（OPEN-2/3/5/6 阻塞 I-11-B）。
- `hypotheses.json` **L168**（parameter_id）、**L170–175**（推导式、"公司未披露铜当量换算系数…示意值，不是披露值"、敏感性、两点差分声明、整条式进入 `STOP_DISCLOSURE_ADAPTATION`）、**L189/L193**（系数只出现一次的双计规则）、**L196–197**（其 falsifier ±5% 为 `professional_judgement_required`）。
- `mechanism_review.md` **L117–119**（"公司未披露…该系数**不是参数**，是待裁定项"）。
- `review.md` **L125–126**（disclosure_adaptation not granted 且该式 `STOP_DISCLOSURE_ADAPTATION` 正确）、**L160**（P2-6 已改写为两点差分）。
- `START_HERE.md` **L36/L47**（专业决策未定先 blocked；不可识别模型参数属专业审查；意见须含六要素）。
- 本次独立检索：以 ripgrep 在 `.planning` 之外检索 `铜当量|当量`，**0 命中**（唯一相关命中为 `.planning` 内本卡产物与 `audit_review/.../ZIJIN/annual_2025_selected_pages.json` 中的"当量碳酸锂/金当量储量"，均非铜当量口径）。方法与边界见 provenance.json `method_notes`。
- **`basis`**：A-2.1/A-2.2/A-2.3 = `professional_judgement`（会计可采性与披露充分性判断，授权见 §① L47）；"本地无 S1" = 本地检索事实（见上，**不含**"公司全文从未披露"这一超出检索面的断言 —— 全文级断言仍以被审 attempt 的抽取结论为准，其自身登记为未披露）。

#### 反例（什么会推翻本裁定）

- 找到紫金在**同一报告期**原文中的铜当量系数或可推出系数的完整要素（价格+回收率+范围）并完成本地归档 ⇒ A-2.1 升级为 S1，参数可在**非实现者签署**后放行，A-2.3 的 `_PLACEHOLDER` 约束解除；
- owner 明文裁定"允许 S3 均值作点估计" ⇒ A-2.1 第 3 条被推翻（须以 owner 决议原文追加登记）；
- 若证实下游接口**只消费相对变化**、不消费绝对水平 ⇒ A-2.3 第 2 条的严格度可下调，但仍须带 S0 标注。

#### 兼容影响（下游参数会怎么变）

- **I-11-B**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的幅度校准**继续阻塞**；若采纳替代方案，需改为分金属单位收入或直接用分部对外收入路径 —— 新 parameter_id 必须先在 `model_cards.md` 注册并通过 `validate_hypotheses.py` 的 `REGISTERED` 检查（否则触发 `E_UNKNOWN_DRIVER`/唯一性规则），这属于**接口变更**，须由 I-10-A/I-11-B 侧登记；`STOP_CALIBRATION`（`card_I-11-B.md` L20）在 S0 期间应触发。
- **I-10-A（披露适配）**：须把"铜当量系数未披露"登记为披露缺口，公式层保持 `STOP_DISCLOSURE_ADAPTATION`。
- **I-07-E**：`card_I-07-E.md` L8 要求冻结"币种单位"，须显式记录"元/吨铜当量 为未披露换算口径"，不得当作公司口径。
- **OPEN-6 交互**：命题 2 的 falsifier 观测量本身依赖铜当量分母 ⇒ 该 ±5% 阈值在 OPEN-2 解决前**不可观测、不可审定**（审定顺序：OPEN-2 → OPEN-6 该条）。

#### 恢复规则（追加式，不回改）

新证据到达时：新建裁定条目 `OPEN-2-ACCT-R2`（含新 provenance 条目、来源等级、decision_sha256），**不修改**本条正文；`hypotheses.json` 侧只能新增版本（`decision.decision_sha256` 指向新裁定记录），旧快照保留供 I-12 评分（与 decision.md DEC-6 恢复规则 L174–175 同构）。

#### 被拒替代方案

1. 把示意值 24 吨/千克当作已披露值直接冻结 —— 违反"只用可核验来源"（card L9）与 L175 自述；
2. 用第三方研报均值代替披露 —— 方法论不可复核，属 S3，只能进敏感性带；
3. 用收入 ÷（假定价格×假定量）倒算系数再代回原式 —— 循环论证；
4. "先给数、后补来源"（把 S0 值写成 base 再说）—— 违反 START_HERE L36「专业决策未定先blocked」；
5. 因"系数敏感"就把整条命题删掉 —— 过度收缩；命题可保留为 pending/unquantified，机制链与可观测性结论仍有价值。

#### BLOCKED（本裁定中缺证据、不给值的部分）

- **BLOCKED-2a**：铜当量换算系数的**具体取值**及其行业合理性 —— 缺 S1/S2 证据且属矿业行业 reviewer 半区。
- **BLOCKED-2b**："公司全文从未披露铜当量系数"的**全文级断言** —— 我只做了 `.planning` 外的全文检索与被审 attempt 抽取复核，未独立解析紫金 PDF 全文；在拿到可复核的全文检索记录前不作为已核事实使用。

---

### 3.3 OPEN-3 · 会计/披露维度裁定

**裁定（一句话）：RULING —— 分部口径变更的"已核"标准 = E1（8-K/10-K 分部附注原文本地归档：URL+取回 UTC+sha256+逐字引文+独立复核路径）；当前本地语料只有**自述"非来源捕获"的 web 工具转录与二手研究稿（E3）**，本次我方在线取回亦未取得原文（SEC HTTP 403）⇒ 不得记为已核；原文补齐前，"沿用 as_of=2026-09-18 时点的 PBP/IC/MPC 分部 + 显式口径风险标注"**可接受为临时、不可签发的建模假设**，但**不可**表述为"FY2027 分部已核/仍为三分部"，也**不可**反向表述为"已重分类为两分部"，且不得用于 I-11-B 幅度校准放行。**

#### 裁定 A-3.1：什么才算"已核"（可接受证据等级）

- **E1 = 已核**（唯一可支撑"分部口径已确定"的等级）：申报原文本地归档 + sha256 + 逐字引文 + 独立路径复核（与本卡 P1/P2 双路径、`arithmetic_oracle` 同精神）；分部重分类还须附**重述后的基期分部数据**（否则不可比）。
- **E2 = 可引未归档**：只能进入叙述与风险提示。
- **E3 = 二手**：只能提出问题。本地实例自证其等级 —— `audit_review/2026-09-18_real_company_skill_audit/MSFT/official_reclassification.web_tool_response.json` **L2** 逐字：`"purpose": "Actual web tool response log; not a source capture or host attestation receipt"`；`MSFT/research.md` **L35** 属研究稿判断。二者**均不足以**支撑分部口径结论。
- **E0 = 不是证据**。

#### 裁定 A-3.2：8-K 原文本地不可得时的 fail-closed 处置

1. 命题 `H-US-MSFT-SEG-01` 维持 `pending_professional_decision`（现状已如此，`hypotheses.json` L572–573），**不得**升 `approved_frozen`；
2. 分部基准字段应携带 `segment_basis_status = as_of_carry_forward_unverified`（或等价显式标注）+ 风险说明："as_of 之后存在指向重分类的外部线索，原文未归档"；
3. 参数 `MSFT_PBP_REVENUE_FY2027` / `MSFT_IC_REVENUE_FY2027` / `MSFT_MPC_REVENUE_FY2027` / `MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027` 一律按**未放行**处理 —— **判定依据是命题 `state`，不是 `_PLACEHOLDER` 后缀**（这四个 id 无后缀；`_PLACEHOLDER` 只是更明显的标记，见 mechanism_review L49–50）。下游脚本必须以 `state=…_professional_decision` 为门，缺此门即为缺陷；
4. **不得**在任何产物中出现"FY2027 分部已核"或"已按新分部建模"字样，**除非** E1 已归档；
5. 反向同样 fail-closed：也不得把 E3 线索写成"已确认重分类"。

#### 裁定 A-3.3：沿用 as_of 时点分部 + 显式口径风险标注是否可接受

**可接受，但仅限"临时、不可签发"**，且必须同时满足：

1. 显式标注（A-3.2 第 2 条），并在 I-07-E 的"分部口径冻结"（`card_I-07-E.md` L8）中把该标注一并带入；
2. **不得**跨基准计算增长率：若后续 E1 确认重分类，**必须先按新分部重述/重建基期，再计算增速** —— 基准不一致的增长率在会计上不可比、直接无效。此点与命题自带的 `revert_rule`（`hypotheses.json` **L652**：「若分部数或口径变化…本命题回到 'rebuild required'：以新分部的历史对照表重建基期，**不改旧快照**」）一致，我予以会计面背书；
3. I-07-E 提到的"微软重述"等已审关键口径（`card_I-07-E.md` **L9**）必须来自审定记录（E1 + decision_sha256），不得引用研究稿；
4. `calibration.selection_rule` 已写明"不使用未经核验的 2026-09-02 8-K 八线口径"（`hypotheses.json` **L636**）—— 该约束在 E1 归档前**继续有效**。

#### 依据（本地可核 + 本次外部取证）

- 本地：`decision.md` **L399**（OPEN-3 行）、`review.md` **L69–70**（「10-K 仍按 PBP/IC/MPC 编制（`Agents and Infra` 出现 0 次），as_of 之后的重分类 8-K 原文不在本地可核来源，故八线口径既未引用也未否定」）、`mechanism_review.md` **L148–151**（同上 + 本卡禁网）、`hypotheses.json` **L665**（`refuted_by` 记载同一事实）、**L636**、**L652**、`START_HERE.md` L36/L47。
- 本地（反面证据的等级自证）：`official_reclassification.web_tool_response.json` **L2**（"not a source capture"）与 **L4**（`"retrieved_date": "2026-09-19"`）；`MSFT/research.md` **L35**。
- 外部（E3/E2 以下，**不作本地事实**，全部落 provenance.json）：
  - SEC 8-K exhibit 99.1：`https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm` → **HTTP 403**「Your Request Originates from an Undeclared Automated Tool」（取证窗口 2026-09-24T20:23:20Z–20:23:31Z）；
  - SEC 全文检索 `https://efts.sec.gov/LATEST/search-index?q=...&forms=8-K` → **HTTP 403**（同上拒止页）；
  - `https://html.duckduckgo.com/html/?q=%22FY27+Segments+and+Investor+Metrics%22+Microsoft` → HTTP 200，摘录（**搜索引擎摘要，E3**）：「On September 2, 2026, Microsoft Corporation (the "Company") posted presentation materials to its Investor Relations website titled "FY27 Segments and Investor Metrics" announcing a change in reportable segments and investor metrics.」；另两条摘要称「Beginning in fiscal year 2027, the Company will manage its operations under this updated reporting structure and report its financial performance based on two …」（webull）与「自2027财年起，微软将把沿用的三大报告分部……重组为两个：Agents and Inf…」（雪球）。
  - **结论**：本次取证**未取得 E1/E2**；线索指向"确有重分类披露"，但在 E1 归档前不得写成事实。
- **`basis`**：A-3.1/A-3.2/A-3.3 = `professional_judgement`（证据等级与可比性规则）；403/200 状态与引文 = 实测外部取证（见 provenance）。

#### 反例（什么会推翻本裁定）

- E1 归档到位（例如以合规 UA/镜像取回 8-K 与 exhibit 99.1 并落 sha256）且显示**未发生**分部重分类 ⇒ A-3.2 的限制解除，as_of 沿用升级为"已核"；
- 同上但显示**已重分类** ⇒ A-3.3 第 2 条（必须重述重建基期）立即生效，I-11-B 的微软分部参数须按新基准重建；
- owner/编排层裁定"带出具方回执的在线取回即可视为 E1（无需本地归档）" ⇒ A-3.1 的定义被推翻（须追加登记）。

#### 兼容影响（下游参数会怎么变）

- **I-11-B**：`MSFT_PBP/IC/MPC_REVENUE_FY2027`、`MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027` 的校准条件未满足；若 E1 确认重分类，`MSFT_*` 全族参数的**基期与命名**都要重建（新旧分部不可直接沿用同一 id 语义）。
- **I-07-E**：L8/L9 两项（分部口径冻结、微软重述）在 E1 前只能标"待审定"，正式发布格应 blocked（`card_I-07-E.md` L10 的签名资格要求）。
- **I-10-A**：分部披露适配资格必须以 E1 为输入。
- 与 OPEN-6 的交互：命题 6 的 `threshold_basis=arithmetic_identity`（分部加总差=0）**仍可用**（该恒等式在任何分部集合下都成立），但"分部集合是否还是 PBP/IC/MPC"不是阈值问题，属 OPEN-3/OPEN-7。

#### 恢复规则（追加式，不回改）

E1 归档后新建 `OPEN-3-ACCT-R2`（附 provenance：URL、取回 UTC、sha256、逐字引文、复核路径），不修改本条；被审 attempt 的 `hypotheses.json`/`refuted_by` **保持原样**（历史不回改），由 I-11-B/I-07-E 以新证据新建版本承载。

#### 被拒替代方案

1. 用 `official_reclassification.web_tool_response.json` 当"8-K 原文" —— 该文件 L2 自述非来源捕获，属 E3；
2. 用二手研究稿（`MSFT/research.md`）的"新两分部 268,127 / 63,712"直接建模 —— 未经 E1，且属另一 reviewer 的业务实质半区；
3. 用搜索引擎摘要当作原文引用 —— 摘要可能截断/改写；
4. 因原文不可得就把命题 6 标 `unquantified` —— 过度收缩：其恒等式部分（A5/A7）已被本地复算，保留 pending 更准确；
5. 直接"按新分部建模并声称已核" —— 违反 A-3.1 与 START_HERE L36。

#### BLOCKED（本裁定中缺证据、不给结论的部分）

- **BLOCKED-3a**：FY2027 建模分部**究竟**是否仍为 PBP/IC/MPC（或变为两分部/八线）—— 缺 E1；业务实质半区归行业 reviewer（软件与云）。
- **BLOCKED-3b**：8-K/exhibit 原文的取得 —— 本次 SEC 端点 403（见 provenance `external_retrieval_failures`），`web_search` 工具亦报端点错误不可用；需要环境/依赖 owner 提供合规取文路径（登记为取证能力缺口，非本裁定事项）。

---

### 3.4 OPEN-5 · `NOT_IN_MY_SCOPE`

**`NOT_IN_MY_SCOPE`**：港股（小米）年报原文可读性属**环境/依赖 owner + 行业 reviewer** 的裁权（`decision.md` L401），本文件不予裁定，仅登记其阻塞关系不变（阻塞任何港股份部命题与 I-11-B 港股参数）。

---

### 3.5 OPEN-6 · 规则面裁定（"用什么基础才允许给数"）

**裁定（一句话）：RULING —— 占位阈值在专业审定前**不得**被下游当作已审定值使用：凡被下游消费的阈值必须携带 `threshold_basis` **且**显式 `threshold_review_status`（默认 `not_reviewed`）；`threshold_basis=professional_judgement_required` 且 `threshold_review_status≠reviewed` 的阈值**不得触发任何自动动作**（falsifier 触发、情景切换、校准边界、I-11-C 反方检验），只能作为"已登记的待审观察条件"；审定一个阈值必须同时具备**可复算观测量 + 可核基础 + 非实现者签署（decision_sha256） + 追加式版本化**，否则一律维持 `not_reviewed`。**

#### 裁定 A-6.1：占位阈值在审定前的使用禁令

1. **不得**当作已审定值：任何读取 `falsifier.threshold` 的下游脚本必须先读 `threshold_basis` 与 `threshold_review_status`；二者缺一或状态为 `not_reviewed` ⇒ **fail-closed**：阈值不参与判定（命题仍可登记观察，但不得据此宣布"被推翻/未被推翻"）。
2. **必须**带 `threshold_basis` + 显式未审定标注：这是**必要非充分**条件 —— 有 `threshold_basis` 只说明"依据类型已登记"，不等于"已审定"；两者必须分字段（新增 `threshold_review_status` 为**追加字段**，与 DEC-6 的超集策略一致，不改 I-11-A 既有字段）。
3. **判定基准是字段而非后缀**：`_PLACEHOLDER` 后缀只用于参数 id；阈值的可用性只看 `threshold_basis` + `threshold_review_status`。同理，**没有**后缀的参数（如 `MSFT_PBP_REVENUE_FY2027`）只要命题 `state=pending_professional_decision` 就同样未放行。
4. **计数以机器产出为准**（decision.md DEC-9，L234–252）：`validation_report.counts.threshold_bases` = `arithmetic_identity 4 / professional_judgement_required 3 / disclosure_definition 1`（`validation_report.json` **L28–32**）。
   **发现一处口径不一致（须下游注意）**：`handoff.json` **L9/L244** 与 `mechanism_review.md` **L211** 仍写"4 条 `professional_judgement_required`"（R2 改判前的旧数），而 `review.md` **L75–76** 与 `decision.md` **L402** 已是"3 条 + 1 条 `disclosure_definition`"。**以 `validation_report.json` 的机器计数为准（3+1）**；本条属**追加更正提示**，我**不回改**上述任何文件。

#### 裁定 A-6.2：三类 `threshold_basis` 的可使用范围

| 类别 | 条数 | 审定前可否使用 | 条件 |
|---|---|---|---|
| `arithmetic_identity` | 4（`hypotheses.json` L88 / L311 / L524 / L649） | **可用**（等式判定） | 舍入容差必须**显式**且**不超过来源披露的舍入粒度**（如"允许 |差| ≤ 1 元"对应元位披露），容差依据须写明；不得自由放大 |
| `professional_judgement_required` | 3（L197 ±5%、L418 [0.9,1.1]、L862 拆分层级判定） | **不可用**（不得触发判定/校准/评分） | 须先取得审定记录（A-6.3） |
| `disclosure_definition` | 1（L757 Microsoft Cloud 聚合口径） | **可用**（是/否型判定，非幅度） | 判定必须可对原文重跑（引页/表）；**披露不存在 ⇒ 维持 `unquantified`，不得以任何数值替代** |

#### 裁定 A-6.3：审定一个阈值的**证据要求**（给数的前置条件）

必须**同时**满足，缺一即维持 `not_reviewed`：

1. **观测量可复算**：`falsifier.observable` 指向具体披露行/表，`source_route` 可定位，`observation_date`/滞后明确（本卡已具备，`hypotheses.json` 各 falsifier 字段）；
2. **数值有可核基础**，且属于以下之一并写明：
   - (i) **来源自身的披露容差/定义**（原文写明的舍入、可比口径）；
   - (ii) **同口径历史离散**：同一披露指标在 ≥2 个可比披露期上的实际波动，计算过程与所用原文一并归档（可复算）；
   - (iii) **准则/监管/交易所明文定义**（引原文）；
   - (iv) **专家假设**：允许，但必须标 `expert_assumption` 并给出敏感性区间，**永远不得**被记为"等同披露依据"；
3. **签署身份**：非实现者（本卡为会计/行业 reviewer），裁定记录带 `decision_sha256`、日期、作用域（`hypothesis_id` + `parameter_id`）；
4. **追加式版本化**：审定后写入命题**新版本**（`decision.decision_sha256` 指向审定记录），旧阈值与旧版本保留供 I-12 评分（decision.md DEC-6 恢复规则 **L174–175**），**不回改**历史；
5. **跨卡同步**：`threshold_basis` 若新增枚举值，必须同步 I-11-A 与 I-11-C 两侧校验器（DEC-6 L170–172、DEC-14 L364–365），否则按未知值拒绝。

#### 依据（本地可核）

- `decision.md` **L153–177**（DEC-6：两类阈值、占位 + `threshold_basis=professional_judgement_required`、其"反例"正是"占位阈值诱导下游按此执行"）与 **L402**（OPEN-6 行：3 条未审定 + 1 条改判 `disclosure_definition`）；
- `review.md` **L75–76**（3 条未审定 + 1 条 R2 改判）、**L160**（P2-6 处置）；
- `validation_report.json` **L28–32**（机器计数 4/3/1）、**L170–176 / L210–216**（`E_THRESHOLD_BASIS_INCONSISTENT` / `E_THRESHOLD_BASIS_UNKNOWN` 反例已被拒 —— 说明"依据类型诚实性"已有机器检查，但**没有**"是否已审定"的机器检查，正是本裁定要补的字段）；
- `hypotheses.json` **L196–197 / L417–418 / L861–862 / L756–757 / L87–88 / L310–311 / L523–524 / L648–649**；
- `card_I-11-B.md` **L13**（"缺数据就标 expert_assumption"）、**L20**（`STOP_CALIBRATION`）、**L23**（"专业reviewer签署后方可进入forecast"）；
- `START_HERE.md` **L36/L47**（专业决策未定先 blocked；统计阈值属专业审查）。
- **`basis`**：A-6.1/A-6.2/A-6.3 = `professional_judgement`（规则面裁定，授权见 §① L47；fail-closed 依据 L36）。

#### 反例（什么会推翻本裁定）

- 有 reviewer 主张"占位阈值可先用、事后补签" ⇒ 推翻 A-6.1（与 DEC-6 反例段与 START_HERE L36 直接冲突，除非 owner 明文豁免并追加登记）；
- 校验器新增 `threshold_review_status` 后出现**大批**历史阈值被判不可用、导致 I-11-C 完全无法启动 ⇒ A-6.1 的实施方式（追加字段 + 默认 not_reviewed）需按实际情况重议，但**"未审定不得当已审定"这一实质不因此改变**；
- 若 owner 裁定 `disclosure_definition` 也需数值化 ⇒ A-6.2 第 3 行的"可用"范围收窄。

#### 兼容影响（下游参数/逻辑会怎么变）

- **I-11-B**：校准与情景逻辑必须新增"阈值门"：`threshold_review_status=not_reviewed` 时，`STOP_CALIBRATION`/触发器不得因该阈值而动作；`expert_assumption` 标注（L13）须与 `threshold_review_status` 对齐。
- **I-11-C**：复用 falsifier 结构（DEC-6 L170–172），须接受新字段；否则未审定阈值会被当作反方检验的判据。
- **I-11-A 校验器**：当前对 `threshold_basis` 只做闭集 + 一致性检查、**无**"审定状态"检查（`validation_report` 反例清单可证）；若在 I-11-A 侧补该检查，属**新规则**，须按 DEC-14 流程补反例并重跑 21 例计数 —— 该改动属 I-11-A 卡的实现者/编排层，**我只提出要求，不代改**。
- **I-12**：旧阈值版本必须保留（评分需可回溯）。
- **OPEN-2 交互**：命题 2 的 ±5% 观测量依赖铜当量分母 ⇒ 该条审定必须排在 OPEN-2 之后。

#### 恢复规则（追加式，不回改）

阈值审定后：新建 `OPEN-6-ACCT-R2`（附审定记录 sha256、证据链、作用域），命题新增版本并保留旧版本；本条正文与 `threshold_basis=professional_judgement_required` 的历史标注**一律不改**，只追加状态。

#### 被拒替代方案

1. "把 ±5%、[0.9,1.1] 直接写成已审定" —— 越权（decision.md DEC-6 已拒方案 (a)）；
2. "阈值全留空等 I-11-C" —— 使 falsifier 五要素不全（DEC-6 已拒方案 (b)）；
3. "只在 md 里写一句'未审定'、不落字段" —— 下游脚本读不到，等同可用（本裁定 A-6.1 第 1 条针对此）；
4. "用实现者自签的 decision_sha256 补齐状态" —— 违反 START_HERE L26 与 `E_STATE_APPROVED_BY_IMPLEMENTER`；
5. **给出具体阈值数值** —— 超出我的裁权与本条范围（题面明令），属 BLOCKED。

#### BLOCKED（本裁定中缺证据、不给值的部分）

- **BLOCKED-6a**：3 条 `professional_judgement_required` 阈值的**数值**是否恰当（±5%、[0.9,1.1]、拆分层级判定）—— 需行业/专业 reviewer 按 A-6.3 给出证据与签署；我**不给数**。
- **BLOCKED-6b**：4 条 `arithmetic_identity` 的**容差**是否与其来源舍入粒度一致（含 ±1 USD million）—— 需逐条对照原文舍入粒度复核后签署（规则已给，值未审）。
- **BLOCKED-6c**：`threshold_review_status` 字段的**落地实现与校验器改动** —— 属 I-11-A 实现者/编排层与 schema 侧，我只给要求。

---

## ④ 证据与 provenance 摘要

- **外部来源数：3**（另含 1 次重定向未跟随的失败尝试、1 次 `web_search` 工具端点错误，均入 provenance 的 `external_retrieval_failures`）：
  1. `https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm` — HTTP **403**（拒止页引文见 provenance `ext-01`）；
  2. `https://efts.sec.gov/LATEST/search-index?q=...&forms=8-K` — HTTP **403**（`ext-02`）；
  3. `https://html.duckduckgo.com/html/?q=%22FY27+Segments+and+Investor+Metrics%22+Microsoft` — HTTP **200**，三条摘要引文（`ext-03`）。
  - 取证窗口（UTC）：2026-09-24T20:23:20Z – 20:23:31Z（复跑轮），另有一次更早的同内容尝试（≤ 2026-09-24T20:23:04Z）。
  - **快照未保存**：本载体写入面被限定为 3 个文件（ruling.md / provenance.json / handoff.json），故 `snapshot_path = null`、`snapshot_sha256 = null`；引文逐字转录于 provenance.json。
  - 全部外部证据在本裁定中**只作 E3/E2 以下线索使用**，未作为本地事实。
- **本地证据：13 条**（路径 + sha256 + 字节 + 引用行号 + 引文，见 provenance.json `local_evidence`），含被审 attempt 的 `decision.md` / `review.md` / `handoff.json` / `hypotheses.json` / `validation_report.json` / `mechanism_review.md`，授权文件 `OWNER_DECISIONS.md`，执行协议 `START_HERE.md`，三张卡文件，以及两份 `audit_review` 侧文件。
- **本地检索**：`.planning` 之外 `铜当量|当量|Agents and Infra` 的 ripgrep 结果已记录（方法边界见 provenance `method_notes`；隐藏目录默认不入扫描，故 `.planning` 内部由我另行显式读取）。

## ⑤ `BLOCKED` 项清单（缺什么）

| id | 内容 | 缺什么 | 交给谁 |
|---|---|---|---|
| BLOCKED-2a | 铜当量系数具体取值与行业合理性 | S1/S2 级来源（或 owner 豁免决议） | 矿业行业 reviewer |
| BLOCKED-2b | "公司全文从未披露铜当量系数"的全文级断言 | 独立的紫金 PDF 全文检索记录 | 矿业行业 reviewer / 环境 owner |
| BLOCKED-3a | FY2027 微软分部究竟为何（PBP/IC/MPC vs 新架构） | E1：8-K/Exhibit 原文本地归档（sha256+引文+复核路径） | 行业 reviewer（软件与云）+ 会计（E1 到位后我可补裁） |
| BLOCKED-3b | 取得申报原文的合规路径 | SEC 端点 403；`web_search` 工具端点错误不可用 | 环境/依赖 owner |
| BLOCKED-6a | 3 条判断类阈值的数值 | A-6.3 的证据与非实现者签署 | 行业/专业 reviewer |
| BLOCKED-6b | 4 条恒等式阈值的容差是否匹配披露舍入粒度 | 逐条对照原文舍入粒度 | 会计 reviewer（我）在拿到对照表后补裁 / 行业 reviewer 会签 |
| BLOCKED-6c | `threshold_review_status` 落地与校验器改动 | I-11-A 实现者/编排层与 schema 侧动作 | 编排层 / schema owner |

> fail-closed 声明：以上任一项在补齐前，**不得**被下游当作"已裁定/已审定"；我宁可留 BLOCKED 也不给"看起来完成"的值。

## ⑥ 边界（自我约束核对）

- **零产品写**：本载体只在 `execution_runs/I11A-OPEN-ACCT/a20260924-01/` 下新建 `ruling.md`、`provenance.json`、`handoff.json` 三个文件；未在 `.planning` 之外创建/修改任何文件。
- **零 git 写**：未执行 `git add` / `commit` / `checkout` / `stash` / `restore` / `reset`。交付时 `git -c core.quotepath=false diff HEAD --name-only` 共 3821 条、**非 `.planning` 条目 = 0**（复核于 2026-09-24T20:23Z；最终值另见 handoff.json `git_diff_non_planning`）。
- **零 status 变更**：未修改 I-11-A 的 `status`/`decision`/`state`/任何字段；被审 attempt 全程只读。
- **零代签**：`implementer_signed = false`；**且不声称"已验收 I-11-A"** —— 本文件只出具**会计/披露维度**的裁定，I-11-A 的验收状态仍以既有独立 reviewer 的 `accepted_scoped`（review.md §5 转录）为准，我不新增也不修改它。
- 本文件自身为**追加式新载体**；任何更正以 `R2` 条目追加，不回改本文件正文（如需修订，另建 revision 并在 handoff.json 登记链条）。
