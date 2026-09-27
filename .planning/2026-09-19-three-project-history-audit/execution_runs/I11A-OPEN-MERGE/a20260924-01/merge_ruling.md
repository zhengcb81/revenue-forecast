# I-11-A 开放问题 · 父级合并裁定（parent merge adjudicator）

- 本载体 attempt：`execution_runs/I11A-OPEN-MERGE/a20260924-01`
- 角色：`parent_merge_adjudicator`（**父级合并裁工位**）
- 父代理 id：`session-19074bf0-0205-4315-af73-9db57597275a`
- 被裁对象（**全程只读**）：`execution_runs/I-11-A/a20260919-01/`（accepted_scoped 封盘 attempt）、`execution_v2/card_I-11-A.md`、`execution_v2/card_I-11-B.md`
- 合裁输入：`I11A-OPEN-ACCT/a20260924-01`（会计/披露半区）与 `I11A-OPEN-IND/a20260924-01`（行业半区：矿业 + 软件/云），**两半均已交付**
- 生成日期（UTC 会话日）：2026-09-24

**本工位性质（先读这一条）**：我不是第三个专家。我**只做①合成、②两半对照、③冲突/含糊检测、④对父问题的明确回答**；**不新增任何专业判断**、**不解除任何 BLOCKED**、**不代签**、**不改任何 status**、**不取证（禁网）**、**不择一**。

> `does_not_claim_I11A_acceptance = true`
> `adds_no_new_domain_judgement = true`

---

## ① 身份与授权链（含两半各自 sha256）

### 1.1 授权原文（逐字，转引自两半 provenance 条目 `loc-01` / `LOC-01`，两半对 `OWNER_DECISIONS.md` 记录同一 sha256 `c13feca44a052f8238b32ab7db5de367859ddfc78cd0cc0b1bdefb80659bc6b7` / 64,386 B）

| 授权点 | 原文（逐字） | 出处（两半一致引用） |
|---|---|---|
| owner 原话 | 「…**I-11-A OPEN-2/3/5/6 指派会计+行业 reviewer**…」 | `OWNER_DECISIONS.md` §十 **L116**（ACCT `loc-01` / IND `LOC-01`） |
| 执行行 | 「\| **I-11-A OPEN-2/3/5/6** \| **指派**：会计 + 行业（矿业/软件）reviewer \| 编排层按此派单；**OPEN-2/3/5/6 阻塞 I-11-B / I-07-E** \| **I-11-B / I-07-E**（待专家裁定） \|」 | §十 **L127** |
| 第二批 | 「\| 2 \| I-11-A OPEN-2/3/5/6 \| **派新 subagent** 当行业 reviewer \| 编排层创建独立行业 reviewer subagent \|」 | §十一 **L144** |

⇒ 编排层（父代理）派出两路专家的授权成立；本工位是父代理对**已交付两半**的合成，**授权链不含任何"第三个专业裁定席位"**。

### 1.2 两半输入（sha256 = 本工位实测复算；`ruling.md`/`provenance.json` 与两半自报值逐一相同）

| 半区 | 文件 | 字节 | sha256（实测） | 与自报值一致？ |
|---|---|---|---|---|
| 会计/披露 | `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md` | 37,355 | `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2` | ✅（`ACCT handoff.json` L150-151 自报一致） |
| 会计/披露 | `…/I11A-OPEN-ACCT/a20260924-01/provenance.json` | 18,975 | `81b045bc636375738fbad1ae02515ea316cd28fbb6b8b156fbb084b22e9c10f1` | ✅（自报 20 条：13 本地 + 3 外部 + 2 外部失败 + 2 本地检索） |
| 会计/披露 | `…/I11A-OPEN-ACCT/a20260924-01/handoff.json` | 11,555 | `79f9c878c8ead003226ab1bc5671b2eadb964570fdb55d4a95f4a4c9c1aa8225` | 自报 `sha256: null`（自指不可自证），由本工位外部复算填入 |
| 行业（矿业+软件/云） | `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` | 39,207 | `8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b` | ✅（`IND handoff.json` L199-200 自报一致） |
| 行业（矿业+软件/云） | `…/I11A-OPEN-IND/a20260924-01/provenance.json` | 25,031 | `71187a55f4b407c387bb9baa8c6e013864d65b3f9875791c1ccf1e3c44bfa079` | ✅（自报 24 条 = 11 本地 + 12 外部 + 1 工具） |
| 行业（矿业+软件/云） | `…/I11A-OPEN-IND/a20260924-01/handoff.json` | 22,988 | `0a14f29ce31d371c6ef347123abd56316e40077de14526bc846938f8bc9be17e` | 自报 `sha256: null`（自指不可自证），由本工位外部复算填入 |

### 1.3 两半的自我限定（决定本工位能不能"合成出解锁"）

- 会计半区（`ACCT ruling.md` **L44**）：「OPEN-2 / OPEN-3 是**双 reviewer 联合裁定项**，本文件只覆盖其中的**会计与披露口径半区**；行业半区未裁定前，OPEN-2/OPEN-3 **不得**被记为"已全部裁定"，I-11-B / I-07-E 的相应解锁**不因本文件而成立**。」
- 会计半区（`ACCT handoff.json` **L176-L177**）：`"I-11-B": "NOT unlocked by this carrier…"`、`"I-07-E": "NOT unlocked by this carrier (same reason)"`。
- 行业半区（`IND ruling.md` **L7**）：「本文件**不是** I-11-A 的验收结论，**不改变** I-11-A 任何 `status`/字段，**不代签**任何命题。」
- 行业半区（`IND handoff.json` **L255**）：「…(3) **do NOT start I-11-B until BLOCKED-2..BLOCKED-6 clear**; this station's rulings are additive carriers and **do not unlock anything by themselves**.」

⇒ 两半**都声明自己不解锁**；因此本工位**也不可能**通过"合成"产生解锁 —— 合成只能得出两半已有的结论与其交集/差集。

---

## ② 四条 OPEN 的状态表（两半原句对照 + 冲突检测 + 解锁条件）

状态取值域：`RULED_BOTH_HALVES` / `RULED_WITH_BLOCKED_VALUE` / `BLOCKED` / `OWNER_ONLY`。

### 总表

| OPEN | 状态 | 冲突检测 | 一句话理由 |
|---|---|---|---|
| **OPEN-2** | `RULED_WITH_BLOCKED_VALUE` | `NO_CONFLICT`（+1 条范围注记 `AMBIGUITY_REGISTERED`，见 §2.1「范围注记」） | 来源分级/披露要求/替代阶梯两半一致；**系数取值与参数放行两半同判 BLOCKED** |
| **OPEN-3** | `RULED_WITH_BLOCKED_VALUE` | `NO_CONFLICT`（+1 条范围注记 `AMBIGUITY_REGISTERED`，见 §2.2「范围注记」） | 证据等级 E1 规则（会计）与分部选择（行业）互补且互相让位；**E1 未满足 ⇒ 证据 BLOCKED** |
| **OPEN-5** | `OWNER_ONLY` | `NO_CONFLICT` | 卡文所问"由谁解决可读性"两半均不裁；行业面另出的**处置规则不解除阻塞** |
| **OPEN-6** | `RULED_WITH_BLOCKED_VALUE` | `NO_CONFLICT` | 规则面（会计）+ 分行业给数（行业）互补；**H4 四要件不齐、H2 无替代数 ⇒ 取值 BLOCKED** |

---

### 2.1 OPEN-2 · 铜当量换算系数从何而来

**状态：`RULED_WITH_BLOCKED_VALUE`**

#### 两半原句对照

**会计/披露半区**（`execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md`）

- **L75**（裁定一句话）：「RULING —— 铜当量换算系数只有 S1（公司原文披露）与 S2（全输入可核、经非实现者签署采用的准则化口径）两类来源可支撑冻结；S3 仅可作敏感性带、S4 示意值不可作参数；本地语料当前**无任何 S1/S2**，故 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 必须按 S0 处置 —— 参数保持 `_PLACEHOLDER`、I-11-B 不得放行幅度校准，替代方案是回退到"分部对外收入 + 分金属销量"的无换算口径（或整条转 `unquantified`）。」
- **L79**：「**S1 公司披露**（首选，唯一无需附加条件即可冻结的来源）」；**L82**：「**S4 分析师自设/示意值**：**不得**作为参数（本卡 `1 千克金 = 24 吨铜当量（示意值）` 正属此类）」；**L83**：「**反向推导（用收入 ÷ 假设价 × 假设量倒算系数）**：循环论证，**不可采**。」
- **L103**：「**明确结论：不可得 ⇒ 参数保持 `_PLACEHOLDER` 且不得放行**（本条被 owner 题面点名，予以确认）。」
- **L100**（替代首选）：「**单位回退（首选）**：只用披露单位计量 —— 收入侧用**分部对外收入（元）**，量侧用**分金属销量**（铜 吨、金 千克），不做混合金属分母…」
- **BLOCKED 子项 L142-143**：「**BLOCKED-2a**：铜当量换算系数的**具体取值**及其行业合理性 —— 缺 S1/S2 证据且属矿业行业 reviewer 半区。」「**BLOCKED-2b**："公司全文从未披露铜当量系数"的**全文级断言** —— …在拿到可复核的全文检索记录前不作为已核事实使用。」

**行业半区**（`execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md`）

- **L65**（A 级行）：「**公司在同一份定期报告中同时披露**：(i) 换算系数/换算口径…与 (ii) 同口径的**当量销量**…｜**唯一可作 base** 的来源」
- **L69**（C'' 行）：「把实现者自设的"1 千克金 = 24 吨铜当量"示意值当已审定值放行｜**不可**（无来源，属占位）」
- **L77**：「⇒ **A 类来源在 FY2025 年报中不存在**：公司没有披露任何用于把金/银/锌销量折成"铜当量销量"的系数。」
- **L71-L75**（本地全文扫描，可复核）：「`铜当量` **0** 处、`吨铜当量` **0** 处、`换算系数` **0** 处、`折算系数` **0** 处、`换算` **0** 处；`当量` 共 26 处，全部为 `当量碳酸锂` / `当量 碳`…另有 1 处 `露采边际品位：当量铜 0.2%`（**资源边际品位**口径，不是销量换算）。」
- **L90**（参数标注要求）：「1. 维持 `pending_professional_decision`，`low/base/high` 保持 `null`；**不得**因本裁定获得放行；」
- **L96**：「3. **首选口径替换（强烈建议 I-11-B 采用）**：不做当量合并，改为两个已披露量——「矿产品分部对外收入（元）」+「分金属销量（铜 884,943 吨 / 金 83,161 千克 / 锌 / 银，p44 产销量表）」分别落参数…」
- **L127**：「**BLOCKED 子项**：给 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 一个**可放行的系数取值/单位收入数值** ⇒ `BLOCKED`（缺公司披露的系数与当量销量口径；本地全文扫描为 0 命中）。」

#### 冲突检测：`NO_CONFLICT`

两半在同一问题上的**可执行结论逐条一致**：

| 子问题 | 会计面 | 行业面 | 判定 |
|---|---|---|---|
| 公司同期原文披露的系数 | S1 可冻结（L79） | A 级可作 base（L65） | 一致 |
| 24 吨/千克示意值 | S4 不得作参数（L82） | C'' 不可（L69） | 一致 |
| 倒算/反推系数 | 不可采（L83） | 被拒替代方案「用券商研报的"当量产量"反推」（L124） | 一致 |
| 本地是否存在可用来源 | 「无任何 S1/S2」（L75） | 「A 类来源…不存在」+ 0 命中（L77） | 一致 |
| 当前参数处置 | `_PLACEHOLDER`、不放行（L75/L103） | `pending_professional_decision`、`low/base/high = null`、不放行（L90） | 一致 |
| 首选替代口径 | 「分部对外收入 + 分金属销量」（L100） | 「分部对外收入 + 分金属销量」（L96） | 一致 |
| 取值本身 | BLOCKED-2a（L142） | BLOCKED（L127） | 一致（同为 BLOCKED） |

⇒ **`NO_CONFLICT`**：无任何一条子问题上两半给出互相排斥的可执行指令。

#### 范围注记 `AMBIGUITY_REGISTERED`（fail-closed，未由本工位择一）

- **原句 A（会计面）** `ACCT ruling.md` **L81**：「S3 行业标准/调研均值/可比公司做法：**不得**作为点估计冻结；**仅**允许用来设定敏感性带（low/high），并按 `expert_assumption` 登记、单列 `independence_group`，不得因使用它而放行参数。」
- **原句 B（行业面）** `IND ruling.md` **L67**：「| **C** | 套用**其他公司/行业平均**的当量系数或"元/吨铜当量"单位收入 | **不可**（跨公司不可比，见下） |」
- **本工位处置（不代裁）**：两句字面覆盖对象有重叠，但**所问不同**（A 问"可否进敏感性带"，B 问"可否作该参数的口径基础"），两半**未就"同行/行业均值可否进 low/high"同时表态**。我**不替任一半扩写、也不择一**；该子问题登记为 `BLOCKED-UNADJ-1`，**本合并裁定对该子用法授予任何许可**（fail-closed：本载体 `grants_nothing`）。若父代理判定其应升级为 `CONFLICT`，则 OPEN-2 按 fail-closed 铁律降级为 `BLOCKED`，逐字原句即上 A/B 两句。

#### 解锁条件（逐条可执行）

1. **S1/A 级证据到位**：紫金在**同一报告期**定期报告/产销公告中同时给出换算系数口径与同口径当量销量，并**本地归档**（URL + 取回 UTC + 文件 sha256 + 逐字引文 + 独立复核路径）—— 对应会计面 E1 形态（`ACCT ruling.md` L66/L153）与行业面 A 级（`IND ruling.md` L65）。
2. **非实现者签署**：由会计 + 矿业 reviewer 出具新裁定条目 `OPEN-2-ACCT-R2` / `ruling_r2.md`，带 `decision_sha256`、日期、作用域（`hypothesis_id` + `parameter_id`），**追加式、不回改**（`ACCT ruling.md` L130；`IND ruling.md` L116-117）。
3. **命题与参数换版**：`hypotheses.json` 只**新增版本**（`decision.decision_sha256` 指向新裁定记录），旧快照保留；`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 方可脱离 `pending_professional_decision`。
4. **若走替代口径**：新 parameter_id 必须先在 `model_cards.md` 注册并通过 `validate_hypotheses.py` 的 `REGISTERED` 检查（`ACCT ruling.md` L123），否则 `E_UNKNOWN_DRIVER`。
5. **BLOCKED-2b**：补一份独立的紫金 PDF 全文检索记录（`ACCT ruling.md` L143），才能使用"全文从未披露"这一断言。
6. **`AMBIGUITY_REGISTERED / BLOCKED-UNADJ-1`**：需两半（或 owner）对"同行/行业均值可否进 low/high"出具**一致**明示意见。

---

### 2.2 OPEN-3 · FY2027 微软建模分部

**状态：`RULED_WITH_BLOCKED_VALUE`**（规则已裁；**证据（E1）BLOCKED**）

#### 两半原句对照

**会计/披露半区**（`ACCT ruling.md`）

- **L149**（裁定一句话）：「RULING —— 分部口径变更的"已核"标准 = E1（8-K/10-K 分部附注原文本地归档：URL+取回 UTC+sha256+逐字引文+独立复核路径）；当前本地语料只有**自述"非来源捕获"的 web 工具转录与二手研究稿（E3）**，本次我方在线取回亦未取得原文（SEC HTTP 403）⇒ 不得记为已核；原文补齐前，"沿用 as_of=2026-09-18 时点的 PBP/IC/MPC 分部 + 显式口径风险标注"**可接受为临时、不可签发的建模假设**，但**不可**表述为"FY2027 分部已核/仍为三分部"，也**不可**反向表述为"已重分类为两分部"，且不得用于 I-11-B 幅度校准放行。」
- **L153**（E1 定义）：「**E1 = 已核**（唯一可支撑"分部口径已确定"的等级）：申报原文本地归档 + sha256 + 逐字引文 + 独立路径复核…」
- **L154**（E2 定义）：「**E2 = 可引未归档**：只能进入叙述与风险提示。」
- **L160-L162**（fail-closed 处置）：「1. 命题 `H-US-MSFT-SEG-01` 维持 `pending_professional_decision`…**不得**升 `approved_frozen`；…3. 参数 `MSFT_PBP_REVENUE_FY2027` / `MSFT_IC_REVENUE_FY2027` / `MSFT_MPC_REVENUE_FY2027` / `MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027` 一律按**未放行**处理 —— **判定依据是命题 `state`，不是 `_PLACEHOLDER` 后缀**…」
- **L163**：「4. **不得**在任何产物中出现"FY2027 分部已核"或"已按新分部建模"字样，**除非** E1 已归档；」
- **让位句 L213**：「**BLOCKED-3a**：FY2027 建模分部**究竟**是否仍为 PBP/IC/MPC…缺 E1；**业务实质半区归行业 reviewer（软件与云）**。」
- **L214**：「**BLOCKED-3b**：8-K/exhibit 原文的取得 —— 本次 SEC 端点 403…需要环境/依赖 owner 提供合规取文路径。」

**行业半区**（`IND ruling.md`）

- **L133**（裁定）：「RULING —— FY2027 建模分部应为新两分部；"旧分部 + 标注"只可作基期/桥接，不可作 FY2027 报告口径」
- **L147**（外部取得声明）：「`https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965d8k.htm`（直接取回 **HTTP 403**，SEC UA 政策；改经 `r.jina.ai` 文本渲染取回 **HTTP 200**），Item 7.01 原文：」
- **L171**（结论表）：「| FY2027 及以后的**建模/预测维度** | **新两分部：Agents and Infra / Devices and Consumer**（**待原文进入本地语料后落参数**） |」
- **L164-L165**：「✅ 可接受为：(a) FY2025/FY2026 **基期层**…(b) **过渡桥**，前提是必须带 `segment_basis = pre_reclassification_legacy`…」「❌ 不可接受为：FY2027 的**报告分部口径**…」
- **L175-L178**（放行门槛）：「由于重分类原文**不在本地可核来源**…⇒ `MSFT_PBP_REVENUE_FY2027` / `MSFT_IC_REVENUE_FY2027` / `MSFT_MPC_REVENUE_FY2027` **维持不可放行**；I-07-E 的微软分部口径**维持未冻结**，直至 (i) 8-K 与 Exhibit 99.1 进入本地可核语料（filing-fetch 授权获取 + hash 登记），且 (ii) **会计 reviewer 认定其证据等级**。新两分部的参数**同样不可放行**——因为它们的取数目前只存在于外部来源。**两条路都不得在当前状态下放行。**」
- **让位句 L160**：「该 8-K 是 **Regulation FD "furnished" 而非 "filed"**…⇒ 它是发行人正式披露，但**证据等级需会计面单独认定（我不裁）**。」
- **L208**：「**BLOCKED 子项**：①8-K 原文进入本地可核来源；②`MSFT_*_REVENUE_FY2027` 三个参数放行；③I-07-E 微软分部口径冻结 ⇒ 均 `BLOCKED`（缺本地原文 + 待会计面证据等级）。」

#### 冲突检测：`NO_CONFLICT`

- **互相让位、无重叠裁权**：会计面把"分部究竟为何"让给行业面（L213）；行业面把"证据等级/能否入表"让给会计面（L160、L177(ii)）。两半各自只裁对方声明不裁的那半 ⇒ **不构成冲突**。
- **同一动作指令一致**：`MSFT_*_REVENUE_FY2027` 参数在两半下**都**是"未放行"（ACCT L162 vs IND L177）；命题 `H-US-MSFT-SEG-01` **都**不得升 `approved_frozen`（ACCT L160 + IND L175 的 fail-closed 门槛）；"新两分部落参数"必须等本地语料（IND L171/L177），而"本地归档才叫已核"正是会计面 E1（ACCT L153）—— **同一个门槛的两种表述**。

#### 范围注记 `AMBIGUITY_REGISTERED`（fail-closed，未由本工位择一）

- **原句 A（会计面）** `ACCT ruling.md` **L168**：「**可接受，但仅限"临时、不可签发"**」（对"沿用 as_of 时点分部 + 显式口径风险标注"，未在句中限定只用于 FY2025/FY2026 基期）。
- **原句 B（行业面）** `IND ruling.md` **L165**：「❌ 不可接受为：FY2027 的**报告分部口径**；也不可接受在**无桥接表**的情况下把旧分部历史数与新分部数据混用/并列…」
- **本工位处置（不代裁）**：E1 到位前，两半对**全部 MSFT 参数的放行判断完全相同（均不放行）**，故该范围差**当前不产生任何冲突动作**；E1 到位后按两半各自的恢复规则处理（会计 `OPEN-3-ACCT-R2`，行业 `ruling_r2.md` + `supersedes`）。该子问题（"临时建模假设"是否覆盖 FY2027 年度）登记为 `BLOCKED-UNADJ-2`，**本合并裁定不授予任何许可**。若父代理判定其应升级为 `CONFLICT`，OPEN-3 按 fail-closed 降为 `BLOCKED`。

#### 解锁条件（逐条可执行）

1. **E1 归档（核心缺口）**：由 **filing-fetch 授权获取**（需 owner 授权，因 SEC 端点 403）把 `2026-09-02 8-K`（`d291965d8k.htm`）与 `Exhibit 99.1`（`d291965dex991.htm`）落本地语料，登记 **URL + 取回 UTC + 文件 sha256 + 逐字引文 + 至少一条独立复核路径**（`ACCT ruling.md` L66/L153；`IND ruling.md` L371 BLOCKED-4）。
2. **会计面补裁**：新建 `OPEN-3-ACCT-R2`（附 E1 provenance + `decision_sha256`），认定证据等级；**不回改**本裁定与被审 attempt 的 `refuted_by`（`ACCT ruling.md` L201）。
3. **行业面复裁**：8-K 本地化后新建 `ruling_r2.md` 标 `supersedes`（`IND ruling.md` L197）；外部条目永久保留 `evidence_class=external`（L198）。
4. **命题/参数换版**：`H-US-MSFT-SEG-01` 与 `MSFT_*` 参数在新版本上重裁；若确认重分类，**先按新分部重述/重建基期，再算增速**（`ACCT ruling.md` L171，与 `hypotheses.json:652` 的 `revert_rule` 一致）。
5. **环境/依赖 owner** 提供合规取文路径（BLOCKED-3b，`ACCT ruling.md` L214）。
6. **`AMBIGUITY_REGISTERED / BLOCKED-UNADJ-2`** 需两半对"临时建模假设的适用年度"出具一致意见。

---

### 2.3 OPEN-5 · 港股（小米）年报原文可读性由谁解决

**状态：`OWNER_ONLY`**（卡文所问的**归属**问题：两半均不裁，归环境/依赖 owner）

#### 两半原句对照

**会计/披露半区**（`ACCT ruling.md` **L220**）：「**`NOT_IN_MY_SCOPE`**：港股（小米）年报原文可读性属**环境/依赖 owner + 行业 reviewer** 的裁权（`decision.md` L401），本文件不予裁定，仅登记其阻塞关系不变（阻塞任何港股份部命题与 I-11-B 港股参数）。」

**行业半区**（`IND ruling.md`）

- **L216-L218**：「**A. 归属问题——`BLOCKED-pending-owner`** …属**环境与依赖 owner（I-00-B 侧）权限**…**我不代裁**，缺的是：owner 对修复路径（工具库 or 依赖 or 外部工具）的指派与授权。」
- **L222-L225**（行业**处置**规则，非归属裁定）：「1. **港股分部命题保持零产出**：`HK-XIAOMI-AR2025` 维持 `STOP_EVIDENCE / not_readable`；本次 `not_readable` 判定**不得**改写为"已验证"…」「2. **I-11-B / I-07-B 的港股分部参数维持 `_PLACEHOLDER` 且不得放行**…」「3. **不接受二手补位**…」「4. **不接受"行业常识"补位**…」
- **L229-L234**（替代来源分级，供 owner 解锁后使用）：① 同发行人同期间可读原文 `company_primary_disclosure`；② 交易所/监管公告 `regulator_primary_disclosure`；③ 研报/新闻/wiki `secondary_lead_only`（仅线索）；④ 外部抓取件 `external_retrieval_not_local`（必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**）。

#### 冲突检测：`NO_CONFLICT`

- 归属问题：会计面 `NOT_IN_MY_SCOPE` vs 行业面 `BLOCKED-pending-owner` —— **同一结论（两半均不裁、归 owner）**，无冲突。
- 行业面的"处置规则"是**在 owner 解锁前保持不可用**的约束，**不与会计面任何句子冲突**（会计面只登记阻塞关系不变，L220）。

#### 解锁条件（逐条可执行）

1. **环境/依赖 owner（I-00-B 侧）** 出具修复路径指派与授权（对象流解析 / 离线 PDF 库 / 合规外部工具 / 依赖升级）—— 这是本条唯一能动的开关（`IND ruling.md` L218、`IND handoff.json` L178 BLOCKED-1）。
2. 可读性恢复后：**新建 attempt 重新取证**，**不得**把本次 `not_readable` 就地改成"已验证"（`decision.md` L227-228，经 `IND ruling.md` L222 转引）。
3. 取到可读同期间原文后：按行业面 C 表 ①/② 级登记（文件类型 + 期间 + sha256 + 定位符），**证据等级仍由会计面认定**（`IND ruling.md` L241）。
4. 在此之前：`*_HK_*` / 港股分部参数维持 `_PLACEHOLDER`，I-07-B/I-11-B 港股侧不得放行（`IND ruling.md` L223、L374）。

---

### 2.4 OPEN-6 · 占位阈值是否按此采用

**状态：`RULED_WITH_BLOCKED_VALUE`**（规则面两半一致已裁；**取值/落地 BLOCKED**）

#### 两半原句对照

**会计/披露半区**（`ACCT ruling.md`）

- **L226**（裁定一句话，含"给数四要件"）：「RULING —— 占位阈值在专业审定前**不得**被下游当作已审定值使用：凡被下游消费的阈值必须携带 `threshold_basis` **且**显式 `threshold_review_status`（默认 `not_reviewed`）；`threshold_basis=professional_judgement_required` 且 `threshold_review_status≠reviewed` 的阈值**不得触发任何自动动作**（falsifier 触发、情景切换、校准边界、I-11-C 反方检验），只能作为"已登记的待审观察条件"；**审定一个阈值必须同时具备可复算观测量 + 可核基础 + 非实现者签署（decision_sha256） + 追加式版本化**，否则一律维持 `not_reviewed`。」
- **L231**：「2. **必须**带 `threshold_basis` + 显式未审定标注：这是**必要非充分**条件 —— 有 `threshold_basis` 只说明"依据类型已登记"，不等于"已审定"…（新增 `threshold_review_status` 为**追加字段**…）」
- **L240-L242**（A-6.2 三类可用范围）：`arithmetic_identity` 4 条 **可用**（容差须显式且≤来源舍入粒度）；`professional_judgement_required` 3 条 **不可用**（不得触发判定/校准/评分）；`disclosure_definition` 1 条 **可用**（是/否型；披露不存在 ⇒ 维持 `unquantified`）。
- **L248-L256**（A-6.3 给数的前置条件，五条，其中前四条即"四要件"）。
- **L296-L298**（BLOCKED）：「**BLOCKED-6a**：3 条 `professional_judgement_required` 阈值的**数值**是否恰当（±5%、[0.9,1.1]、拆分层级判定）—— 需行业/专业 reviewer 按 A-6.3 给出证据与签署；**我给不数**。」「**BLOCKED-6b**：4 条 `arithmetic_identity` 的**容差**是否与其来源舍入粒度一致…（规则已给，值未审）」「**BLOCKED-6c**：`threshold_review_status` 字段的**落地实现与校验器改动** —— 属 I-11-A 实现者/编排层与 schema 侧，我只给要求。」

**行业半区**（`IND ruling.md`）

- **L268**（计数校准）：「`validation_report.json → counts.threshold_bases = {arithmetic_identity: 4, professional_judgement_required: 3, disclosure_definition: 1}`」；**L281**：「⇒ 判断类共 **4** 条（H2/H4/H7/H8），其中 **3 条 pjr + 1 条 disclosure_definition**。」
- **L288**（H4 行）：「| **H4** | 计划达成率 `[0.9, 1.1]` | ✅ **采用**（矿业面给数） | **0.90 – 1.10**（±10%） | `professional_judgement`（本 reviewer，矿业面） |」
- **L291**（H2 行）：「| **H2** | 单位收入 ±5% | ❌ **不采用占位值；替代数值 `BLOCKED`** | — | `BLOCKED` |」
- **L299**（H4 放行条件）：「**放行条件**：本条仅为**行业面审定**；是否可标 `threshold_basis` 升级、以什么基础允许给数，**由 `I11A-OPEN-ACCT` 依其基础规则确认**，**在此之前 I-11-B/I-11-C 不得据此触发**。」
- **L330**（兼容影响）：「I-11-B：H4 阈值影响 `ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER` / `ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 的达成判定（**注意这两个参数仍是 `_PLACEHOLDER`，阈值审定不等于参数放行**）；」
- **L376**：「> 本工位**未给任何"看起来完成"的值**：H2 无替代数、系数无取值、8-K 无本地化、港股无命题。」

#### 冲突检测：`NO_CONFLICT`

- 分工互补：会计面裁"用什么基础才允许给数"（`ACCT ruling.md` L40 让位句：「`OPEN-6` 的**阈值数值本身**…归**行业/专业 reviewer**；我只给"给数的前置条件"」）；行业面裁数值并**明确回头受会计面规则约束**（`IND ruling.md` L299、`IND handoff.json` L130 `release_condition`）。
- 计数一致：两半都以 `validation_report.counts` 为准并各自登记不一致（ACCT L234 / IND L282）。
- 结论一致：H2 两半同为 BLOCKED（ACCT BLOCKED-6a 含 ±5%；IND L291 不采用且无替代数）。
- **不存在**"会计面允许未审定阈值触发"或"行业面声称阈值已审定"这类可执行对立指令 ⇒ `NO_CONFLICT`。

#### 解锁条件（逐条可执行，按阈值分列）

| 阈值 | 缺什么 | 谁签/什么动作 |
|---|---|---|
| **H4 `[0.9,1.1]`** | "给数四要件"后 3 件（见 §3.2 逐件核对）：可核基础按 A-6.3 第 2 条落为四类之一（含 `expert_assumption` 标注 + 敏感性区间）、非实现者 `decision_sha256`、命题新版本 | 会计面按 A-6.3 确认（IND L299 点名）+ 行业面会签；写入 `hypotheses.json` **新版本** |
| **H2 ±5%** | OPEN-2 口径裁定 + 价格归一化基准（价格序列/期间/净价口径） | 矿业 reviewer + 会计面（IND L373 BLOCKED-6；ACCT BLOCKED-6a） |
| **H8 拆分层级判定** | 两点修订（来源集合放宽到发行人原始披露全集；单披露时可登记备选 driver 候选）需落到命题新版本；且按 A-6.3 留 `decision_sha256` | 行业面（软件）+ 会计面确认 |
| **H7 disclosure_definition** | 无需给数；但须按 IND L319 在 FY2027 首次披露后复核 Microsoft Cloud KPI 定义（受 OPEN-3 影响） | 行业面复核 + 会计面（A-6.2 第 3 行规则） |
| **4 条 arithmetic_identity 容差** | 逐条对照原文舍入粒度的对照表（BLOCKED-6b） | 会计 reviewer 拿到表后补裁 + 行业 reviewer 会签 |
| **字段落地** | `threshold_review_status` 字段与校验器改动（BLOCKED-6c；并按 DEC-14 补反例、重跑 21 例） | I-11-A 实现者 / 编排层 / schema owner |

---

## ③ 核心问题：I-11-B 能否开工？

# 结论：**I-11-B — BLOCKED（不能开工）**

### 3.1 依据链（逐环可核）

**环 1 — 被审 attempt 自述（父已核）**（`execution_runs/I-11-A/a20260919-01/handoff.json`）

- **L6**：`"I-11-B MUST NOT start from this attempt: 0 propositions are approved_frozen, and OPEN-2/OPEN-3/OPEN-5/OPEN-6 block parameter calibration"`
- **L7**：`"I-11-B: parameter_id values ending in _PLACEHOLDER (…) are reserved but NOT approved for use"`
- **L9**：`"I-11-B: the 4 thresholds marked threshold_basis=professional_judgement_required must be signed off first (OPEN-6)"`（计数口径见 §⑥）
- **L226**：「…rule on OPEN-2/3/5/6 before anyone starts I-11-B. … **Do NOT start I-11-B from this handoff.**」
- **L227**：`"next_step_number": "independent review; then owner disposition of OPEN-2/3/5/6; then I-11-B (blocked until then)"`
- **L229 / L236**（`not_granted` 列表）：`"any approved_frozen proposition (0 written by the implementer)"`、`"I-11-B / I-11-C / I-07-E unlock"`
- **L298**：`"approved_frozen": 0`；**L321**：`"hypotheses": "8 (6 pending_professional_decision, 2 unquantified, 0 approved_frozen)"`
- 同 attempt `review.md` **L175-L176**（经 ACCT provenance `loc-07` 转引）：「I-11-B / I-11-C / I-07-E = **NOT unlocked**（0 条 approved_frozen，且 OPEN-2/3/5/6 阻塞参数校准与触发器生效）。」
- `decision.md` **L410-L411**（经两半 provenance 转引）：「没有任何一项阻塞本卡签收；但 **OPEN-2 / OPEN-3 / OPEN-5 / OPEN-6 阻塞 I-11-B**，因此 I-11-B 不能在本次之后自动开工。」

**环 2 — 两半合起来是否产生了任何 `approved_frozen` 命题/参数？ ⇒ 没有（0 条）**

| 检查点 | 事实 | 出处 |
|---|---|---|
| 两半的写入面 | 各自仅 3 个文件（ruling/provenance/handoff），**均不含 `hypotheses.json`/`handoff.json`(I-11-A)/任何 status 字段** | ACCT provenance `write_surface` L13-L17；IND provenance `discipline_attestation.files_written` L382-L386 |
| 两半的自我声明 | ACCT：`implementer_signed=false`、`i11a_acceptance_claimed=false`、`status_fields_changed=0`（ACCT handoff L170-L173）；IND：`does_not_claim_I11A_acceptance=true`、`does_not_change_I11A_status=true`（IND handoff L15-L16）、`status_fields_changed=0`（IND provenance L390） | 直接引文 |
| 命题状态 | 仍是 `6 pending_professional_decision + 2 unquantified`，`approved_frozen = 0` | `validation_report.json` L13-L18（counts）；`I-11-A/handoff.json` L298/L321 |
| 参数放行 | ACCT：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 保持 `_PLACEHOLDER`、I-11-B 不得放行幅度校准（ACCT L75）；`MSFT_*` 一律未放行（ACCT L162）。IND：`low/base/high` 保持 null、不得因本裁定获得放行（IND L90）；MSFT **两条路都不得放行**（IND L178）；HK 参数维持 `_PLACEHOLDER`（IND L223） | 两半原文 |
| 触发器 | ACCT A-6.1：pjr 且未审定 ⇒ **不得触发任何自动动作**（ACCT L230）；IND H4：**在此之前 I-11-B/I-11-C 不得据此触发**（IND L299） | 两半原文 |
| 两半自己的结论 | ACCT handoff L176：`"I-11-B": "NOT unlocked by this carrier…"`；IND handoff L255：`do NOT start I-11-B until BLOCKED-2..BLOCKED-6 clear…do not unlock anything by themselves` | 直接引文 |

⇒ **两半合计 `approved_frozen` 增量 = 0，参数放行增量 = 0，触发器放行增量 = 0。** I-11-B 的开工前提（`card_I-11-B.md` L9「I-11-A命题已批准」+ L23「专业reviewer签署后方可进入forecast」）**未满足**。

**环 3 — fail-closed 铁律的直接后果**：本工位是合成席位，**无权**把"0 → 1"；任何 BLOCKED 项在补齐前**不得**被下游当作已裁定/已审定（`ACCT ruling.md` L326 的 fail-closed 声明 + `IND ruling.md` L376）。

### 3.2 易误读点 (a)：行业面给了 **H4 = [0.90, 1.10]** —— 这等于该命题 `approved_frozen` 吗？

# 判定：**否。H4 不等于 `approved_frozen`；`threshold_review_status` 仍应视为 `not_reviewed`。**

**"给数四要件"逐件核对**（要件定义逐字来自 `ACCT ruling.md` **L226**：「审定一个阈值必须同时具备**可复算观测量 + 可核基础 + 非实现者签署（decision_sha256） + 追加式版本化**，否则一律维持 `not_reviewed`」；细则见 A-6.3 **L248-L256**）：

| # | 要件 | H4 现状 | 判定 | 依据 |
|---|---|---|---|---|
| ① | 可复算观测量 | `falsifier.observable = "FY2026 实际披露：年报产销量表矿产金/矿产铜的实际产量与销售量，对照计划值 105 吨/120 万吨"`，且 `observation_date`、`source_route` 齐备 | ✅ 满足 | `hypotheses.json` L416-L421；ACCT A-6.3 第 1 条 L248 |
| ② | 数值有可核基础（四类之一：来源披露容差 / 同口径历史离散可复算 / 准则监管明文 / 明示 `expert_assumption`+敏感性区间） | 行业面给的是**行业判断理由**：「对大型在产矿企，年度产量计划达成率落在 ±10% 内通常视为"计划基本达成"…」（`IND ruling.md` **L296**），**未**按 A-6.3 第 2 条落为四类之一，**未**标 `expert_assumption`、**未**给敏感性区间、**未**附同口径历史离散计算 | ❌ 不满足 | `IND ruling.md` L296；`ACCT ruling.md` L249-L253 |
| ③ | 非实现者签署 + `decision_sha256` | 命题记录仍为 `"decision": "pending"`、`"decision_sha256": null`；两半载体中**没有任何一条 H4 的 `decision_sha256`** | ❌ 不满足 | `hypotheses.json` **L443-L447**；两半 handoff 均无 H4 决议哈希 |
| ④ | 追加式版本化（命题新版本承载审定，旧阈值保留） | 未发生：两半写入面均不含 `hypotheses.json`；H4 仍在原版本上 | ❌ 不满足 | ACCT provenance `write_surface`；IND provenance `files_written` |

**结论：四要件 1/4 满足 ⇒ 不齐 ⇒ 按 ACCT L226 一律维持 `not_reviewed`**（该字段本身尚未落地 = BLOCKED-6c，`ACCT ruling.md` L298）⇒ 按 A-6.1（L230）该阈值**不得触发任何自动动作**。

**两半自己的限定句（防止被误读为"已解锁"）**：

- `IND ruling.md` **L299**：「本条仅为**行业面审定**…**在此之前 I-11-B/I-11-C 不得据此触发**。」
- `IND ruling.md` **L330**：「**注意这两个参数仍是 `_PLACEHOLDER`，阈值审定不等于参数放行**」
- `IND handoff.json` **L130**：`"release_condition": "industry sign-off only; threshold_basis upgrade still requires the accounting station's basis rule"`
- `ACCT ruling.md` **L296**（BLOCKED-6a）：`[0.9,1.1]` 的数值是否恰当仍列在会计面 BLOCKED 清单内。

⇒ **H4 = "规则面/行业面给数"，不是"命题已批"**；`H-CN-ZIJIN-PLAN-04` 的 `state` 仍是 `pending_professional_decision`（`hypotheses.json` **L356-L358**，`decision_sha256 = null` 见 L447），`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER` / `ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 仍不可用。

### 3.3 易误读点 (b)：行业面经 `r.jina.ai` **外部取得 8-K 原文** —— 满足会计面 E1 吗？

# 判定：**否，E1 未满足；OPEN-3 证据仍 BLOCKED。**

**E1 五要素逐项核对**（E1 定义逐字来自 `ACCT ruling.md` **L66** 与 **L153**：「申报原文**本地归档**：URL + 取回 UTC + 文件 sha256 + 逐字引文 + 至少一条独立复核路径」）：

| 要素 | 行业面实际状态 | 判定 | 依据（行业面自述） |
|---|---|---|---|
| 本地归档 | **无**：「**快照**：**未落任何快照文件**（写入面被限定为 3 个文件）⇒ 外部条目 `snapshot_path = null`、`snapshot_sha256 = null`」 | ❌ | `IND ruling.md` **L359**；`IND provenance.json` `snapshot_policy` L13-L17 |
| 文件 sha256 | **无**：EXT-05 `"snapshot_sha256": null` | ❌ | `IND provenance.json` **L270-L271** |
| 取回 UTC | **只有会话窗口**：`"retrieved_utc": "2026-09-24T20:20:00Z/2026-09-24T20:34:43Z (session window)"`，并自述「web_fetch 未提供逐请求时间戳…**不伪造精确到秒的单条时间**」 | ❌ | `IND provenance.json` L8-L12、L266 |
| 逐字引文 | **有**（Item 7.01/9.01 原文引文完整） | ✅ | `IND provenance.json` L267；`IND ruling.md` L149-L153 |
| 独立复核路径 | **无**：原站直取 **403**，改经第三方文本渲染代理 `r.jina.ai` 单一路径；行业面自述「r.jina.ai is a third-party text-rendering proxy; the original host refused the direct request (403). Content is therefore EXTERNAL and NOT locally verifiable.」 | ❌ | `IND ruling.md` **L147**；`IND provenance.json` **L265** |

**⇒ 5 要素缺 4（本地归档 / sha256 / 取回 UTC / 独立复核路径），只满足逐字引文 ⇒ 不构成 E1；最好情况也只到会计面的 E2。**

**E2 的后果（会计面已明文规定）**：

- `ACCT ruling.md` **L154**：「**E2 = 可引未归档**：只能进入叙述与风险提示。」
- `ACCT ruling.md` **L160-L164**：命题不得升 `approved_frozen`；`MSFT_*` 一律未放行；不得写"已按新分部建模"字样（除非 E1 归档）。
- `ACCT ruling.md` **L190**（反例，即"在线取回算 E1"这一误读被明文拒绝）：「owner/编排层裁定"带出具方回执的在线取回即可视为 E1（无需本地归档）"⇒ A-3.1 的定义被推翻（须追加登记）。」—— **本工位不代 owner 做该裁定。**
- 行业面**自述一致**：EXT-05 `locality_warning`：「This is EXTERNAL acquisition. It does NOT satisfy the plan's locally verifiable source requirement and **must not be used to release I-11-B / I-07-E parameters until ingested locally with a hash**」（`IND provenance.json` **L269**）；`IND ruling.md` **L204** 把"把外部抓取的 8-K 当作'本地可核来源'"列为**被拒替代方案**；BLOCKED-4/5（L371-L372）要求 filing-fetch 授权获取 + hash 登记。

⇒ **OPEN-3 状态维持 `RULED_WITH_BLOCKED_VALUE`，其 BLOCKED 部分 = 证据（E1）；`MSFT_PBP/IC/MPC_REVENUE_FY2027`、`MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027`、I-07-E 微软分部口径冻结全部维持不放行；新两分部参数同样不放行（只存在于外部）。**

### 3.4 I-11-B 开工的完整解锁清单（当前全部未满足）

1. **≥1 条命题达到 `approved_frozen`**（或由 owner 明文改判开工门槛）——需**非实现者 reviewer** 在**新 attempt/新版本**上写入 `decision.decision_sha256`，本工位与两半均无此写入面。
2. **OPEN-2**：系数取值解 BLOCKED（S1/A 级证据 + 双 reviewer 签署）或改走"分部对外收入 + 分金属销量"替代口径并在 `model_cards.md` 注册新 parameter_id（ACCT L123）。
3. **OPEN-3**：8-K + Exhibit 99.1 **本地归档 E1**（filing-fetch 授权 + hash）→ 会计面 `OPEN-3-ACCT-R2` 补裁证据等级 → 行业面 `ruling_r2.md` 复裁分部集合。
4. **OPEN-5**：环境/依赖 owner 指派可读性修复路径 → 新 attempt 重新取证（否则港股侧全部维持 `_PLACEHOLDER`）。
5. **OPEN-6**：`threshold_review_status` 字段与校验器落地（BLOCKED-6c）；H4 补齐四要件后由会计面确认；H2 补 OPEN-2 口径 + 价格归一化基准；4 条恒等式容差对照表（BLOCKED-6b）。
6. **OPEN-11（本轮未派，见 §⑤）**：矿业行业 reviewer 确认"上一期披露期末库存"的跨期可得性，否则 `H-CN-ZIJIN-VOL-03` 判定式不可判定须转 `STOP_DISCLOSURE_ADAPTATION`（阻塞 I-11-B 对该参数的产能约束使用）。
7. **`card_I-11-B.md` L9**：I-10-A 为实际采用的公司/分部/模型签署披露适配口径（**仍缺**：`review.md` 记载 `disclosure_adaptation = NOT granted`）。

---

## ④ 边界声明：「规则已立 ≠ 参数已批」

**这是一条必须随本文件传播的分界线。**

| 维度 | 两半**已经**做到的（规则面） | 两半**没有**做到、也**无权**做到的（参数面） |
|---|---|---|
| 产物形态 | 来源分级（S0-S4 / A-B-C）、证据等级（E0-E3）、阈值给数四要件、fail-closed 阶梯、替代口径建议、参数标注要求 | `hypotheses.json` 的命题状态、`decision.decision_sha256`、`low/base/high` 取值、`threshold_review_status`、任何 `status` 字段 |
| 命题状态 | 保持/确认 `pending_professional_decision` / `unquantified` | **`approved_frozen` 仍为 0**（`validation_report.json` L15-L18、`I-11-A/handoff.json` L298） |
| 参数 | 规定"必须保持 `_PLACEHOLDER`/null、不得放行" | **没有任何一个参数脱离 `_PLACEHOLDER` 或 `null`** |
| 触发器 | 规定"未审定不得触发" | 未放行任何触发器（H4/H8 仍 `not_reviewed`） |
| 验收 | 明确 `does_not_claim_I11A_acceptance = true` | I-11-A 仍是既有的 `accepted_scoped`，本工位不新增、不修改 |

**一句话**：**两半交付的是"许可证的申领条件"，不是"许可证"。** `threshold_basis` 有值 ≠ `threshold_review_status = reviewed`；`threshold_review_status = reviewed` ≠ 命题 `approved_frozen`；命题 `approved_frozen` 才是 `card_I-11-B.md` L9「I-11-A命题已批准」的字面要求。**当前三者全为否 ⇒ 规则已立、参数未批、I-11-B 不开工。**

---

## ⑤ 未派 / 授权缺口清单（父必须知道）

派单事实：owner 只派了 **OPEN-2 / OPEN-3 / OPEN-5 / OPEN-6**（§十 L116/L127 + §十一 L144），两半均已交付。

### 5.1 卡文要求但本轮**未被授权/未派**的项（授权缺口）

| # | OPEN | 卡文写给谁（`decision.md`） | 本轮状态 | 缺口性质 | 影响 |
|---|---|---|---|---|---|
| **G1** | **OPEN-11** | 「命题 3 的库存判定式需要"上一期披露的期末库存"作为期初库存，其跨期可得性由谁确认（R2 新增，review P2-8）｜**矿业行业 reviewer**｜…若不可得则该式不可判定，须转 `STOP_DISCLOSURE_ADAPTATION`｜**阻塞 I-11-B 对该参数的产能约束使用**」（`decision.md` L405） | **未派**：owner 两批派单只写 OPEN-2/3/5/6 | **最直接的授权缺口**：卡文指派的角色（矿业行业 reviewer）本轮**已在场**，但派单文本未含 OPEN-11 | `H-CN-ZIJIN-VOL-03` 判定式可判定性未定 ⇒ I-11-B 该参数产能约束用法未解锁 |
| **G2** | **OPEN-4** | 「`pdf_leaf_1based` / `table_index_0based` 是否需成为披露字段的规范枚举值｜**schema owner**」（`decision.md` L400） | 本轮未派；`OWNER_DECISIONS.md` 内**未见**针对 I-11-A OPEN-4 的裁定行（L62 仅在清单中提及；L133 保持未决清单列的是 1/7/8/9/10；L147 亦未裁 OPEN-4） | 归 schema owner，**无本轮授权、无已登记 owner 裁定** | 跨卡页码复用口径未定（不阻塞 I-11-B 开工主链，但属未清授权） |
| **G3** | **OPEN-12** | 「是否需要为"校验器完备性"另立一张专业卡（统计/工程 reviewer）｜**PLAN owner / 统计 reviewer**」（`decision.md` L408） | 本轮未派；`OWNER_DECISIONS.md` 内**未见**针对 I-11-A OPEN-12 的裁定行 | 归 PLAN owner / 统计 reviewer，**无本轮授权、无已登记 owner 裁定** | I-11-C 是否复用同一校验器未定 |

**行业面独立确认 G1**（两半原文，可直接转引）：

- `IND ruling.md` **L51**：「…**OPEN-11（卡文指派给矿业行业 reviewer，但 owner §十/§十一 只派了 2/3/5/6 给本工位，故未派给我）**、OPEN-12（是否另立校验器卡，owner/统计 reviewer）…」
- `IND handoff.json` **L191**：`"OPEN-11 (assigned in the card to the mining industry reviewer, but the owner's dispatch at §十/§十一 sent only OPEN-2/3/5/6 to this station; NOT dispatched to me)"`

**授权缺口条数 = 3（G1 OPEN-11、G2 OPEN-4、G3 OPEN-12）**，其中 **G1 是本轮最直接的缺口**（角色已在场却未获派）。

### 5.2 非缺口（已由 owner 裁定，非本轮派单，列此以示清点完整）

| OPEN | 归谁 | 状态 |
|---|---|---|
| OPEN-1 | PLAN owner / 环境规范 | **owner 已裁**：§十一 L147「I-11-A OPEN-1 允许 pdftotext 降级为交叉核对」 |
| OPEN-7 | 行业 reviewer | **owner 已裁**：§十一 L147「OPEN-7 分部集合维持」 |
| OPEN-8 | 独立 reviewer | **owner 已裁**：§十一 L147「OPEN-8 接受择优规则」 |
| OPEN-9 | `common_research_cards.md` owner | **owner 已裁**：§十一 L147「OPEN-9 升级超集」 |
| OPEN-10 | PLAN owner | **owner 已裁**：§十一 L147「OPEN-10 采用最新文件 mtime」 |

> 清点口径说明：本工位为完成"未派事项清点"，**只读**核对了 `decision.md` 的 OPEN 表（L397-L408）与 `OWNER_DECISIONS.md` 中 `I-11-A` 相关行（L62/L116/L127/L133/L144/L147）；该核对**不新增 provenance 条目**（`provenance.json` 仅引用两半已有条目），也不构成对任何 OPEN 的裁定。

---

## ⑥ 计数不一致登记（登记不回改）

**不一致双方原句：**

| 出处 | 原句（逐字） |
|---|---|
| `execution_runs/I-11-A/a20260919-01/handoff.json` **L9** | `"I-11-B: the 4 thresholds marked threshold_basis=professional_judgement_required must be signed off first (OPEN-6)"` |
| 同上 **L244** | `"OPEN-6 (industry reviewers): accept or replace the four professional_judgement_required thresholds (e.g. +/-5% unit revenue drift, 0.9-1.1 plan attainment band)?"` |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/mechanism_review.md` **L211** | 「OPEN-6 \| 8 条命题的 `falsifier.threshold` 中 **4 条标为 `professional_judgement_required`**（±5%、0.9–1.1 计划达成区间等），阈值是否按此采用…」 |
| **机器计数（权威）** `evidence/I-11-A/validation_report.json` **L28-L32** | `"threshold_bases": { "arithmetic_identity": 4, "professional_judgement_required": 3, "disclosure_definition": 1 }` |

**登记结论（两半已各自发现并同判，本工位照登）**：判断类命题**共 4 条**（H-CN-ZIJIN-SEG-02、H-CN-ZIJIN-PLAN-04、H-US-MSFT-SEG-02、H-US-MSFT-SEG-03），其中 **3 条 `professional_judgement_required` + 1 条 `disclosure_definition`**；`handoff.json` L9/L244 与 `mechanism_review.md` L211 的"4 条 pjr"是 **R2 改判前的过期表述**。
**引用一律以 `validation_report.counts` 为准（4 / 3 / 1）。**
**本工位不回改**上述任何文件（`ACCT ruling.md` L234 已作同样登记；`IND ruling.md` L282 已作同样登记；`IND provenance.json` LOC-07 的 `quote` 内也已附 NOTE）。

---

## ⑦ 边界（自我约束核对，可核）

1. **零产品写**：本工位仅在 `execution_runs/I11A-OPEN-MERGE/a20260924-01/` 下新建 `merge_ruling.md`、`provenance.json`、`handoff.json` 三个文件；**`.planning` 之外创建/修改文件数 = 0**。
2. **零 git 写**：未执行 `git add` / `commit` / `checkout` / `stash` / `restore` / `reset` 任何变体；只执行只读的 `git … diff HEAD --name-only` 与 `ls-files --others`。
   - 开工前基线（本工位首次写入之前）：`total = 3824`，**`non_planning = 0`**；
   - 收尾复测见 `handoff.json` `git_diff_observed`：**`git_diff_non_planning = 0`（要求 0，实测 0）**。
   - `total` 的波动来自并发写入方（两半各自也观测到 3821 → 3822），与本工位无关；本工位的 3 个新文件为**未跟踪**路径，不进入 `git diff HEAD`。
3. **零 status 变更**：未修改 I-11-A 的 `status` / `reviewer_status` / `status_authority` / `open_questions` / `decision` / `state` / 任何字段；被审 attempt 与两半载体**全程只读**。
4. **零代签**：`implementer_signed = false`；**不声称"已验收 I-11-A"**（`does_not_claim_I11A_acceptance = true`）；I-11-A 的 `accepted_scoped` 仍以既有独立 reviewer 判定为准，我既不新增也不修改。
5. **零新增专业判断**：`adds_no_new_domain_judgement = true` —— 本文件不含任何系数取值、阈值取值、分部选择、证据等级新定义；所有专业结论均为两半原文转引（带文件+行号）。两半未同时表态的子问题一律登记为 `BLOCKED-UNADJ-*`（`AMBIGUITY_REGISTERED`），**不择一、不放行**。
6. **零取证/零联网**：本工位未发起任何网络请求；`provenance.json` **只引用两半已有 provenance 条目并标注 `source`**，外部来源条目**零新增**。
7. **零解除 BLOCKED**：两半的 BLOCKED 清单（ACCT：BLOCKED-2a/2b/3a/3b/6a/6b/6c；IND：BLOCKED-1…7）**全部原样保留**，本工位一条也未关闭。
8. **载体自检**：三个文件均为 UTF-8 无 BOM、纯 LF；两个 JSON 写后重解析通过（详见 `handoff.json` `file_format`）。
