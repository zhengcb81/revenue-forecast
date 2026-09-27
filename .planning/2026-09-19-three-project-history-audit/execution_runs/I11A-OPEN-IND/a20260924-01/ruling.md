# I-11-A OPEN-2/3/5/6 行业维度裁定（矿业 + 软件/云）

- 卡：`I-11-A` · 被审 attempt（**只读**）：`execution_runs/I-11-A/a20260919-01`（`status=accepted_scoped`，封盘）
- 本载体：`execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md`
- 角色：`industry_specialist_reviewer`（矿业 + 软件/云两个行业面）
- 起草时间（UTC）：`2026-09-24T20:34:43Z`
- 本文件**不是** I-11-A 的验收结论，**不改变** I-11-A 任何 `status`/字段，**不代签**任何命题。

---

## ① 身份与授权引用（原文逐字）

授权来自 `.planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md`（本读取时点 sha256 `c13feca44a052f8238b32ab7db5de367859ddfc78cd0cc0b1bdefb80659bc6b7`，64,386 B）：

1. **§十 L116（owner 原话逐字）**：
   > 「16 照建议；W05-1 A；W05-2 A；W06-1 A；M08 三步照办；I-04-D R2-3 选 LIMITATION；I-14-A D1/D2 指派运维与 SLO owner；**I-11-A OPEN-2/3/5/6 指派会计+行业 reviewer**；新立卡全部照建议开；I-08-B CONFLICT、I-00-B 追认、三条口径确认：同意。」

2. **§十 L127（执行行逐字）**：
   > | **I-11-A OPEN-2/3/5/6** | **指派**：会计 + 行业（矿业/软件）reviewer | 编排层按此派单；**OPEN-2/3/5/6 阻塞 I-11-B / I-07-E** | **I-11-B / I-07-E**（待专家裁定） |

3. **§十一 L144（第二批逐字）**：
   > | 2 | I-11-A OPEN-2/3/5/6 | **派新 subagent** 当行业 reviewer | 编排层创建独立行业 reviewer subagent |

4. **卡文本身对行业 reviewer 的职责定义**：`execution_v2/card_I-11-A.md` L5「Owner：行业reviewer主责」；L16 动作 4「行业reviewer审定可观测性、时间滞后及是否已在基期/其他driver反映」；L20–L21 停止条件「无法定位模型driver/收入确认环节→仅保留定性未量化；来源晚于as_of或原文无法核查→STOP_EVIDENCE」。

**我 = 上述指派的执行**，但**只裁行业维度**。

### 分工声明（必须随本文件传播）

| 维度 | 归属 | 本文件是否裁 |
|---|---|---|
| OPEN-2：当量换算系数的**行业来源/口径/跨公司可比性**、参数标注方式 | 本工位（矿业行业 reviewer） | **裁** |
| OPEN-2：系数能否入表、证据等级、`STOP_DISCLOSURE_ADAPTATION` 是否解除、会计口径的可核性 | `I11A-OPEN-ACCT`（会计 reviewer） | **不裁** |
| OPEN-3：FY2027 **应沿用哪套建模分部**、重分类对行业建模的实质影响、"旧分部+标注"是否可接受 | 本工位（软件/云行业 reviewer） | **裁** |
| OPEN-3：2026-09-02 8-K 的**证据等级**、是否满足"可核验来源"、能否进入本地语料的授权 | `I11A-OPEN-ACCT`（会计 reviewer）+ filing-fetch/owner | **不裁**（我只声明其为放行前置） |
| OPEN-5："可读性**由谁解决**"（工具/依赖/环境权限） | 环境/依赖 owner（I-00-B 侧） | **不裁**（`BLOCKED-pending-owner`） |
| OPEN-5：原文不可读期间**港股分部命题/参数的行业处置**与替代来源分级 | 本工位 | **裁** |
| OPEN-6：占位阈值**哪些有资格给数**（分行业）、数值与反例 | 本工位（矿业/软件各自） | **裁** |
| OPEN-6："审定阈值用什么基础才允许给数"的**基础规则** | `I11A-OPEN-ACCT`（会计面） | **不裁、不重复** |

---

## ② 范围声明

**本文件裁定**：`OPEN-2`（矿业面）、`OPEN-3`（软件与云面）、`OPEN-5`（行业面部分）、`OPEN-6`（行业面部分）。

**本文件明确不裁（`not_in_scope`）**：

- 会计/披露维度的任何结论（证据等级、能否入表、披露适配资格、`threshold_basis` 的基础规则）——归 `I11A-OPEN-ACCT`；
- OPEN-5 的归属问题（谁修可读性）——归环境/依赖 owner，本文件写 `BLOCKED-pending-owner`；
- OPEN-1（pdftotext 作为取文路径，owner 已于 §十一 L147 裁定）、OPEN-4（位置枚举，schema owner）、OPEN-7（分部集合是否最小建模块，owner 已裁"维持"）、OPEN-8（oracle 页号措辞，独立 reviewer 已给意见）、OPEN-9（模板超集，owner 已裁）、OPEN-10（reviews mtime 口径，owner 已裁）、OPEN-11（矿业库存判定式跨期可得性，**卡文指派给矿业行业 reviewer，但 owner §十/§十一 只派了 2/3/5/6 给本工位，故未派给我**）、OPEN-12（是否另立校验器卡，owner/统计 reviewer）；
- I-11-A 的 `status`、`handoff.json`、`review.md` §5 裁决、任何既有证据文件——**一律只读**；
- 任何产品代码/参数幅度（low/base/high）——本文件不产生、不放行。

---

## ③ 逐条裁定表

### OPEN-2 · 矿业行业维度：紫金"铜当量换算系数"从何而来

**裁定（RULING）——行业可接受的来源分级与口径**

| 级别 | 来源 | 行业上可否作为 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的口径基础 |
|---|---|---|
| **A** | **公司在同一份定期报告中同时披露**：(i) 换算系数/换算口径（含价格假设、回收率/选冶损失、其他换算因子）与 (ii) 同口径的**当量销量**，且当量收入口径与之匹配 | 唯一可作 **base** 的来源 |
| **B** | 分析师按公开价格序列 + 公司披露的回收率/品位**自算**的系数（`factor_basis=analyst_assumption`） | **仅可作 low/high 情景的显式假设**，必须报敏感性；**不得**作 base、**不得**标"已审定" |
| **C** | 套用**其他公司/行业平均**的当量系数或"元/吨铜当量"单位收入 | **不可**（跨公司不可比，见下） |
| **C'** | 用**资源/储量报告**的当量品位（价格法、含回收率）去折算**销量** | **不可**（口径错配：资源品位口径 ≠ 销售量口径） |
| **C''** | 把实现者自设的"1 千克金 = 24 吨铜当量"示意值当已审定值放行 | **不可**（无来源，属占位） |

**本地核验（可复核，非转述）**：对 `CN-ZIJIN-AR2025`（sha256 `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d`，79,925,886 B）做**全文**取文扫描（`pdftotext -enc UTF-8`，工具 sha256 `252d2b345662ba6d3705d79d53dad059aa8ef14f9dcf3afe015facbf1ca995e0`，26,118 行输出）：

- `铜当量` **0** 处、`吨铜当量` **0** 处、`铜金属当量` **0** 处；
- `换算系数` **0** 处、`折算系数` **0** 处、`换算` **0** 处；
- `当量` 共 26 处，全部为 `当量碳酸锂` / `当量 碳`（锂与碳当量）语境，另有 1 处 `露采边际品位：当量铜 0.2%`（**资源边际品位**口径，不是销量换算）。

⇒ **A 类来源在 FY2025 年报中不存在**：公司没有披露任何用于把金/银/锌销量折成"铜当量销量"的系数。因此命题 2 的 `original_value`（`109977556345/885141`）是实现者**从两项原始披露推导**的值，`hypotheses.json:170` 已如实写明"不是披露原文数字"——该自述在行业面**成立**。

**跨公司可比性风险（裁定：不可比）**

- 行业基准（**外部获取**，见 provenance `EXT-02`）：加拿大 NI 43-101 体系下的 Form 43-101F1 Item 19(m) 要求：
  > "(m) when the grade for a polymetallic mineral resource or mineral reserve is reported as metal equivalent, report the individual grade of each metal, and consider and report the recoveries, refinery costs and all other relevant conversion factors in addition to metal prices and the date and sources of such prices."
- 该条**对紫金无约束力**（紫金非加拿大申报人，且该条针对资源/储量品位披露），此处仅作**行业口径基准**：即"当量"只有在**换算依据被同时披露**时才是可核量。
- 由价格假设、回收率、产品结构三家不同 ⇒ 各公司的"元/吨铜当量"**不是同一个量**；且本式分母含金/银/锌全部矿产品（`hypotheses.json:175` 口径暴露二），把混合单位收入当"铜价"或与同行对标会直接失真。

**敏感性（复算，标注为 reviewer 自算而非披露值）**：卡内已给两点差分"系数 +1 吨/千克 ⇒ 分母 +83,161 吨 ⇒ 单位收入 −10,670.89 元/吨"（`hypotheses.json:175`、`mechanism_review.md:117-119`）。按同一分母公式三点复算（`109,977,556,345 ÷ (884,943 + 83,161×k)`）：k=20 ⇒ ≈43,160；k=24 ⇒ 124,248.63；k=28 ⇒ ≈34,224 元/吨铜当量。**这是数量级级别的口径风险，不是小数点级噪声**——这也是系数取值必须 fail-closed 的行业理由。

**在 I-11-B 参数 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 上的标注要求（行业面）**

1. 维持 `pending_professional_decision`，`low/base/high` 保持 `null`；**不得**因本裁定获得放行；
2. `unit`（现为 `人民币元/吨铜当量`，`hypotheses.json:169`）必须追加标注：
   - `unit_basis = derived_not_disclosed`（分母为推导值，非披露值）；
   - `conversion_factor_value = null`（**不填任何数**）、`conversion_factor_basis = analyst_placeholder_rejected`、`factor_source_in_filing = none`；
   - `cross_company_comparable = false`；
   - `sensitivity_note`：写入"系数每 +1 吨/千克 ⇒ −10,670.89 元/吨"及三点示意（k=20/24/28），并标明为 reviewer 复算；
3. **首选口径替换（强烈建议 I-11-B 采用）**：不做当量合并，改为两个已披露量——「矿产品分部对外收入（元）」+「分金属销量（铜 884,943 吨 / 金 83,161 千克 / 锌 / 银，p44 产销量表）」分别落参数；这样 `double_count_exclusion` 中"铜当量折算系数只允许出现一次"的约束自然消失（`hypotheses.json:189/193`）；
4. 若坚持当量口径：必须同时登记系数的 value/basis/source 三点，且**不得**与同行"元/吨铜当量"做对标（`comparability_warning` 必填）；
5. 该参数的 `falsifier.observable`（`hypotheses.json:195`，"下一年度分部收入 ÷ 铜当量销售量"）在口径未定前**不可执行**，须与 OPEN-6 的阈值裁定一并处理（见下）。

**反例（什么会推翻本裁定）**

- 在紫金 FY2025 或 FY2026 定期报告/产销公告中找到**公司自披露**的铜当量系数与对应当量销量，且会计 reviewer 认可其与分部收入同口径 ⇒ A 类来源成立，第 2/3 条标注可降级、系数取值不再 BLOCKED；
- 出现监管或行业统一的换算标准（如交易所明文规定 A 股矿企销量必须按统一系数折当量）⇒ C 类"不可比"结论需重估；
- 若证明 I-11-B 的模型只能吃单一"单位收入"参数且无分产品槽位 ⇒ 首选口径替换（第 3 条）需回到 I-10-A 扩展模型而不是改系数。

**兼容影响（下游参数）**

- `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027`：单位、幅度、可用性（首要受影响）；
- `ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027` / `ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027`：若改首选口径，两参数的语义不变但"折算只出现一次"的约束失效/改写；
- `ZIJIN_PLAN_*_PLACEHOLDER`：不受影响（计划值只进情景对照）；
- OPEN-6 的 H2 阈值 observable 定义（口径变 ⇒ 观测量变）；
- I-07-E 披露适配（**归会计面**，我只声明受本裁定的口径选择影响）。

**恢复规则（追加式，不回改）**

- 新证据（新一期年报披露了系数、或口径被改）⇒ **新建 attempt** 重新取证并在本目录**追加**新 ruling 文件（如 `ruling_r2.md`）+ 新 provenance 条目；**不得**修改本文件、不得修改 I-11-A 任何既有文件；旧裁定与旧 provenance 条目全部保留，形成可追溯的更正链。
- 若新证据推翻某条，新文件写 `supersedes: ruling.md#OPEN-2`，旧条保留并标注 `superseded_by`。

**被拒替代方案**

- 直接采用 24 吨/千克示意值放行（把占位当已审定）；
- 用同行/行业平均系数或同行"元/吨铜当量"倒推紫金（C 类不可比）；
- 用资源储量报告的当量品位口径折算销量（C' 口径错配）；
- 用券商研报的"当量产量"反推（二手来源，违反卡文"原文无法核查→STOP_EVIDENCE"）；
- 把单位改回"元/吨铜当量"却不标注未披露（口径漂移，最容易被下游误读）。

**BLOCKED 子项**：给 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 一个**可放行的系数取值/单位收入数值** ⇒ `BLOCKED`（缺公司披露的系数与当量销量口径；本地全文扫描为 0 命中）。

---

### OPEN-3 · 软件与云行业维度：FY2027 起微软建模分部

**裁定（RULING）——FY2027 建模分部应为新两分部；"旧分部 + 标注"只可作基期/桥接，不可作 FY2027 报告口径**

**本地可核事实（先说，因为它是本卡的证据底线）**

- `US-MSFT-10K-FY2026`（sha256 `e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff`，8,585,615 B）全文（去标签后）检索：
  - `Agents and Infra` **0** 处；
  - `reportable segment` 3 处，其中明文写：
    > "we have reported our financial performance based on the following three segments: Productivity and Business Processes, Intelligent Cloud, and More Personal Computing."
  - `reclassif*` 3 处**全部**是 `Amount(s) reclassified from accumulated other comprehensive loss`（OCI 重分类），**不是分部重分类**；`realignment` 0 处 ⇒ **10-K 正文没有任何分部变更预告**。
- 本地语料枚举：`company-wiki/companies/MICROSOFT CORP/raw/` 下**只有** 10-K 与 `.source.json` 两个文件；`company-wiki/companies/**` 共 33,126 个文件中，文件名匹配 `8-K|8K` 的**为 0**。
  ⇒ 卡内"`2026-09-02 8-K` 原文不在本地可核来源"的登记**经本工位独立枚举复核属实**（`decision.md:399`、`mechanism_review.md:148-151`）。

**外部取得的重分类原文（必须标为外部获取，不得冒充本地可核）**

`https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965d8k.htm`（直接取回 **HTTP 403**，SEC UA 政策；改经 `r.jina.ai` 文本渲染取回 **HTTP 200**），Item 7.01 原文：

> "On September 2, 2026, Microsoft Corporation (the "Company") posted presentation materials to its Investor Relations website titled "FY27 Segments and Investor Metrics" announcing a change in reportable segments and investor metrics. **Beginning in fiscal year 2027, the Company will manage its operations under this updated reporting structure and report its financial performance based on two reportable segments: (1) Agents and Infra and (2) Devices and Consumer.** A copy of the presentation materials is furnished as Exhibit 99.1 to this report."
> "The exhibit furnished on this report under Regulation FD provides a description of our updated reporting structure and **presents summary financial information and historical data on a basis consistent with the updated reporting structure**."
> "…shall not be deemed to be "filed" for purposes of Section 18 of the Securities Exchange Act of 1934…"

Item 9.01(d)：Exhibit 99.1 = "Investor Presentation, dated September 2026, titled "FY27 Segments and Investor Metrics""（`.../d291965dex991.htm`）。
二级来源（`stocktitan`、`analystlens`，均标为 secondary）另给出重述后 FY2026 两分部收入 `Agents and Infra $268.1B / Devices and Consumer $63.7B` 与 FY27Q1 新分部指引区间，仅作**佐证**，不作为数值来源。

**行业判断（实质影响）**：**重大，且是结构性的**，理由三条：

1. 自 FY2027 起公司**按新两分部经营与报告**，PBP/IC/MPC 不再是报告分部 ⇒ 用旧三分部做的 FY2027 分部增速**无法与公司实际披露对账**；
2. 公司**已按新结构重述 FY2025/FY2026 历史**（8-K Exhibit 99.1 自述）⇒ 行业标准做法是"重述历史 + 在新口径上建模"，此时旧口径的历史数只能当**桥接层**；
3. 该 8-K 是 **Regulation FD "furnished" 而非 "filed"**（Section 18 不视为 filed）⇒ 它是发行人正式披露，但**证据等级需会计面单独认定**（我不裁）。

**"沿用旧分部 + 显式标注口径风险"是否可接受**：**部分可接受**——

- ✅ 可接受为：(a) FY2025/FY2026 **基期层**（本地 10-K 是 primary，口径为重分类前），(b) **过渡桥**，前提是必须带 `segment_basis = pre_reclassification_legacy`、必须有"旧三分部 ⇄ 新两分部"的桥接表、必须写失效条件（"若 FY2027 披露采用新分部，本口径作废并触发 rebuild"）；
- ❌ 不可接受为：FY2027 的**报告分部口径**；也不可接受在**无桥接表**的情况下把旧分部历史数与新分部数据混用/并列；更不可接受"沿用旧分部但声称口径无变化"。

**I-11-B / I-07-E 应沿用哪套分部（结论）**

| 用途 | 应采用 |
|---|---|
| FY2027 及以后的**建模/预测维度** | **新两分部：Agents and Infra / Devices and Consumer**（待原文进入本地语料后落参数） |
| FY2025/FY2026 **基期与历史对照** | 旧三分部（本地 10-K primary）**或** 8-K 重述后的两分部历史（须外部→本地化），二者**不得混算增速** |
| 过渡情景 | 旧三分部保留为 legacy 情景 + 桥接表 + 失效条件 |

**参数放行门槛（fail-closed）**：由于重分类原文**不在本地可核来源**（本工位已枚举复核），而外部抓取不得冒充本地可核证据 ⇒

> `MSFT_PBP_REVENUE_FY2027` / `MSFT_IC_REVENUE_FY2027` / `MSFT_MPC_REVENUE_FY2027` **维持不可放行**；I-07-E 的微软分部口径**维持未冻结**，直至 (i) 8-K 与 Exhibit 99.1 进入本地可核语料（filing-fetch 授权获取 + hash 登记），且 (ii) 会计 reviewer 认定其证据等级。
> 新两分部的参数**同样不可放行**——因为它们的取数目前只存在于外部来源。**两条路都不得在当前状态下放行。**

**反例（什么会推翻本裁定）**

- Exhibit 99.1 实际**未**按新结构重述历史 ⇒ "桥接层"要求降级，旧三分部历史可继续直接使用；
- FY2027 10-K（预计 2027-07/08）**仍按 PBP/IC/MPC 报告**（重分类撤回、延后或仅用于 KPI）⇒ 本裁定的"新两分部"必须改回三分部；
- 若重分类只涉及**投资者指标**而未改变**报告分部** ⇒ 三分部继续有效，我这条裁定作废；
- 若新两分部在 FY2027 首份 10-K 中**无法追溯**到本地 10-K 的三分部 ⇒ 桥接表必须由公司披露提供，否则 I-07-E 不得冻结任何一套。

**兼容影响（下游参数）**

- I-11-B：`MSFT_PBP/IC/MPC_REVENUE_FY2027`（三个参数名与 driver 映射可能整体重建；参数注册表变更属 I-10-A/owner，我只声明受影响）；
- `H-US-MSFT-SEG-01` 的 falsifier 与 `revert_rule`（`hypotheses.json:652` 已写"回到 rebuild required，以新分部的历史对照表重建基期，不改旧快照"——**本裁定确认该 revert_rule 成为现实路径**）；
- `MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER`（命题 7 的 Microsoft Cloud 聚合定义可能随新口径重定义）；
- `MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027`（命题 8：产品行与**新**分部的交叉关系改变）；
- I-07-E（分部口径冻结、三公司基期口径一致性）、I-12（准确性样本的历史口径）。

**恢复规则（追加式）**

- 8-K/Exhibit 99.1 进入本地语料后：**新建 attempt** 重新取证并更新本裁定（追加 `ruling_r2.md` + 新 provenance 条目，标 `supersedes`）；**不回改** I-11-A、**不回改**本文件；
- 本裁定中"外部获取"的条目永久保留 `evidence_class=external`，即使日后本地化也不改写历史条目，只新增 `local_ingested_at` 条目。

**被拒替代方案**

- 默认沿用三分部并直接放行（忽略 as_of 之后的披露）；
- 用二级来源（stocktitan/analystlens/新闻）充当 8-K 原文（二手不得原文化）；
- 把外部抓取的 8-K 当作"本地可核来源"（外部不得冒充本地）；
- 因"原文不在本地"就断言"重分类不存在"（本地缺失 ≠ 事实不存在，本次外部检索已证伪该推断）；
- 三分部与两分部混用而无桥接表（增速不可比、双计风险）。

**BLOCKED 子项**：①8-K 原文进入本地可核来源；②`MSFT_*_REVENUE_FY2027` 三个参数放行；③I-07-E 微软分部口径冻结 ⇒ 均 `BLOCKED`（缺本地原文 + 待会计面证据等级）。

---

### OPEN-5 · 行业维度：原文不可读期间的港股分部处置

**裁定（行业处置 = RULING；归属 = BLOCKED-pending-owner）**

**A. 归属问题——`BLOCKED-pending-owner`**

"港股（小米）年报原文可读性**由谁解决**（对象流解析 / 离线 PDF 库 / 合规外部工具 / 依赖升级）"属**环境与依赖 owner（I-00-B 侧）权限**，涉及解释器隔离、禁网、外部工具审批（OPEN-1 已由 owner 单独裁定并限定为"降级为交叉核对路径"）。**我不代裁**，缺的是：owner 对修复路径（工具库 or 依赖 or 外部工具）的指派与授权。见 §⑤ BLOCKED-1。

**B. 行业处置（我裁）——原文不可读期间**

1. **港股分部命题保持零产出**：`HK-XIAOMI-AR2025` 维持 `STOP_EVIDENCE / not_readable`；本次 `not_readable` 判定**不得**改写为"已验证"（卡文原话，`decision.md:227-228`：「可读性恢复后（工具或依赖变更），**新建 attempt 重新取证**；不得把本次的 `not_readable` 判定改成"已验证"」）；
2. **I-11-B / I-07-B 的港股分部参数维持 `_PLACEHOLDER` 且不得放行**：不存在任何港股分部数值，`low/base/high` 不得被填；任何"看起来可用"的港股分部参数一律视为未审定；
3. **不接受二手补位**：审计目录里的小米研究稿、新闻、数据商、wiki 均**不可**作为分部数值来源（`decision.md:214-230` 已拒，本裁定确认）；
4. **不接受"行业常识"补位**：即使某人认为小米分部结构"众所周知"，常识不是可核原文（`decision.md:219-222`）。

**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**

| 级别 | 来源 | 证据等级 | 使用条件 |
|---|---|---|---|
| ① | **同一发行人、同一报告期**的其他**可读原文**官方文件（HKEX 披露易 PDF 文本层正常者、全年业绩公告、中期报告、公司 IR 的年报 HTML/可读 PDF） | `company_primary_disclosure`（与年报同级，但必须标注**文件类型与期间**） | 必须：原文可定位（页码/锚文本或章节）+ 原始 sha256 + 期间与年报一致；跨期文件必须标 `period_mismatch_risk` |
| ② | 交易所/监管公告（HKEX） | `regulator_primary_disclosure` | 同上 |
| ③ | 券商研报 / 新闻 / 数据商 / wiki | `secondary_lead_only` | **仅可作线索**，**不得**进参数、**不得**进命题的 `cited_values` |
| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | `external_retrieval_not_local` | 必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径 |

> 口径提示（行业）：港股分部披露口径与 A 股/美股**不同源**（如小米按手机 × IoT × 互联网服务 × 智能电动汽车等披露），若用非原文补齐会形成跨市场口径混合，I-07-E 必须标注 `segment_basis=cross_market_unverified`，否则三公司基期口径不可比。

**反例（什么会推翻本裁定）**

- 环境 owner 解决可读性后，若新 attempt 实测仍读不出原文 ⇒ B 部分（保持不可用）继续有效，C 表不启用；
- 若出现①类可读原文且含分部收入 ⇒ B 的"零产出"解除，港股命题可重新走正常取证（仍需会计面定证据等级）；
- 若 owner 裁定"本计划只做 CN/US 样本、港股不纳入适用范围"⇒ 本裁定的港股部分整体转为 `not_applicable_with_reason`（须 owner 明文写入卡适用范围，不由实现者默认）。

**兼容影响（下游参数）**

- I-07-B（港股 case：若要港股分部参数必须先解决 OPEN-5）；
- I-11-B：任何 `*_HK_*` / 港股分部参数维持 `_PLACEHOLDER`；
- I-07-E：三公司基期/分部口径冻结中的港股一栏保持"缺信息显式保留"；
- I-12：准确性样本不得把港股列入可用样本（`sample_manifest.json` 的 `HK-XIAOMI-2025` 未被消费，`handoff.json:13`）。

**恢复规则（追加式）**

- 可读性恢复（工具或依赖变更）⇒ **新建 attempt 重新取证**；不得把本次 `not_readable` 改成"已验证"；
- 本裁定的更新同样走"新文件追加 + `supersedes` 标注"，不回改。

**被拒替代方案**

- 用审计目录小米研究稿替代原文；
- 用行业常识/公开认知补分部结构；
- 把 `not_readable` 就地改成 `verified`（明文禁止）；
- 用外部抓取件静默顶替本地原件（必须按④登记为外部）；
- 让 I-11-B 先按占位值跑起来再补证据（把占位当已审定）。

---

### OPEN-6 · 阈值的行业维度（8 条命题）

**先校准计数（本地实测）**：`validation_report.json → counts.threshold_bases = {arithmetic_identity: 4, professional_judgement_required: 3, disclosure_definition: 1}`，与我对 `hypotheses.json` 的逐条检索一致：

| 命题 | 阈值文本 | `threshold_basis` |
|---|---|---|
| H-CN-ZIJIN-SEG-01 | `0`（允许 \|差\| ≤ 1 元） | `arithmetic_identity` |
| **H-CN-ZIJIN-SEG-02** | **相对偏离 ±5%** | **`professional_judgement_required`** |
| H-CN-ZIJIN-VOL-03 | 披露可判定式（销售量 ≤ 生产量 + 期初库存…） | `arithmetic_identity` |
| **H-CN-ZIJIN-PLAN-04** | **实际产量 ÷ 计划产量 ∈ [0.9, 1.1] 之外即显著偏离** | **`professional_judgement_required`** |
| H-CN-ZIJIN-ELIM-05 | `0`（允许 \|差\| ≤ 1 元） | `arithmetic_identity` |
| H-US-MSFT-SEG-01 | `0`（分部加总，允许 ±1 USD million 舍入） | `arithmetic_identity` |
| **H-US-MSFT-SEG-02（Microsoft Cloud）** | **披露定义判定（可复算 + 组成行互斥，否则保持 unquantified）** | **`disclosure_definition`**（R2 改判） |
| **H-US-MSFT-SEG-03** | **拆分层级判定（云/许可拆分 + 席位 + 每单位收入）** | **`professional_judgement_required`** |

⇒ 判断类共 **4** 条（H2/H4/H7/H8），其中 **3 条 pjr + 1 条 disclosure_definition**。
⚠️ **登记一处不一致（不回改，只上报）**：`handoff.json:9`（carry 第 4 条）与 `mechanism_review.md:211`（OPEN-6 行）写成"**4** 条 `professional_judgement_required`"，与脚本计数（3）不符；`decision.md:163`、`mechanism_review.md:18`、`review.md:28` 的 4/3/1 才是正确口径。**引用时以 `validation_report.counts` 为准。**

**裁定（RULING）——我有资格给数的 / 必须保持未审定的**

| # | 阈值 | 裁定 | 数值 | `basis`（行业面） |
|---|---|---|---|---|
| **H4** | 计划达成率 `[0.9, 1.1]` | ✅ **采用**（矿业面给数） | **0.90 – 1.10**（±10%） | `professional_judgement`（本 reviewer，矿业面） |
| **H8** | 拆分层级判定 | ✅ **采用 + 两点修订**（不涉及幅度数） | 无（判定式） | `professional_judgement`（本 reviewer，软件面） |
| **H7** | Microsoft Cloud 聚合口径 | ✅ **维持 `disclosure_definition`**（不给数，本就非幅度） | 无（判定式） | `disclosure_definition` |
| **H2** | 单位收入 ±5% | ❌ **不采用占位值；替代数值 `BLOCKED`** | — | `BLOCKED` |
| H1/H3/H5/H6 | 恒等式 `0`（±1 元 / ±1 USD mn 舍入） | 行业面**无异议**（恒等式无需专业裁量）；"用什么基础才允许给数"的规则**归会计面**，我不重复 | `0` | `arithmetic_identity` |

**H4 给数的依据与反例**

- 依据（`basis=professional_judgement`，矿业面）：对大型在产矿企，**年度产量计划达成率落在 ±10% 内通常视为"计划基本达成"**；超出 ±10% 才对"计划是否对当期生产有指示性"构成实质质疑。区间双侧对称是必要的：低于 90% 说明计划高估产能，高于 110% 说明计划低估、同样失去指示性。
- 该阈值**只判定"管理层目标的达成"**，不判定模型精度；计划值本身不是独立证据（`calibration.management_target_is_not_independent=true`），故阈值不得被 I-11-C 当作准确性判据。
- **反例**：新项目**爬坡年**、重大**并购并表年**、**不可抗力/长周期检修年**——这些结构性年份即使偏离 >10% 也不应判定"计划失真"。⇒ `revert_rule` 必须补一条**"爬坡/并表/不可抗力年豁免分支"**，否则阈值会在结构性年份误触发。
- **放行条件**：本条仅为**行业面审定**；是否可标 `threshold_basis` 升级、以什么基础允许给数，**由 `I11A-OPEN-ACCT` 依其基础规则确认**，在此之前 I-11-B/I-11-C 不得据此触发。

**H2 不给数的理由（fail-closed）**

1. **观测量口径未定**：observable = "分部收入 ÷ **铜当量销售量**"（`hypotheses.json:195`），而分母依赖 OPEN-2 中尚未裁定来源的系数 ⇒ 阈值在口径未定前**没有定义**；
2. **±5% 对该观测量在行业上过紧且无区分力**：该值是**混合金属**的隐含单位收入，铜、金价的年度波动本身常达两位数百分比，固定 ±5% 会被"价格变动"单独触发，无法区分"量价机制失效"与"正常价格波动"——一个必然被噪声触发的阈值**不是**可推翻条件；
3. 价格归一化所需的**基准（用哪条价格序列、哪个期间、是否 TC/RC 净价）**本工位没有可核依据 ⇒ 给数即"看起来完成"。
   ⇒ **替代数值 `BLOCKED`**（缺：OPEN-2 口径裁定 + 价格归一化基准）。
- **反例**（会让我改判接受 ±5%）：若用本地可核的历史序列证明该 observable 在**价格中性年份**的历史波动确实 ≤5%，则 ±5% 可恢复为可审定值。

**H8 采用 + 两点修订**

- 采用"拆分层级判定"：披露 **云/许可拆分 + 单位量（席位）+ 每单位收入** ⇒ `pending` 解除；仅披露其中一项 ⇒ 保持 `pending`（**该语义正确**，不得放宽为"解除"）。
- 修订 (a) **来源集合放宽**：原文写"FY2027 10-K（或 8-K 附件）"，行业上席位/ARPU 属运营指标，**通常在业绩发布与补充材料而非 10-K 披露** ⇒ 来源集合应为"发行人**原始披露**全集（10-K / 8-K exhibit / 业绩发布与补充材料）"，且必须各自登记 `source_type` 与 `independence_group`（十篇转述同一发布会算一个来源）。
- 修订 (b) 仅披露其中一项时，**允许登记备选 driver（`direct_growth/growth_rate`）作为候选**，但**不得**据此校准幅度，`state` 仍为 `pending_professional_decision`。
- 不给幅度数（该阈值本就不是幅度）。

**H7 维持，附一条行业提示**

- 判据（"必须由发行人给出**可复算**的披露组成行且各组成行**互不重叠**"）**认可**；不满足即保持 `unquantified`（现语义正确，不得放宽为按比例拆分）。
- 行业提示：新分部口径（OPEN-3）下 **Microsoft Cloud 的 KPI 定义可能被重定义** ⇒ 必须在 FY2027 首次披露后**复核定义**，否则本判定式会拿旧定义去卡新披露、产生假阴性。

**反例（会推翻 OPEN-6 某条裁定的证据）**

- H4：若公司披露的计划本身含"区间指引"或"爬坡年特殊口径"⇒ ±10% 的双侧对称假设需改为单侧或公司自定义区间；
- H8：若发行人明确把席位/ARPU 列为非披露 KPI（永不披露）⇒ 该命题应从 `pending` 转 `unquantified`，而不是继续等；
- H7：若 10-K 给出 Microsoft Cloud 的可复算组成行 ⇒ 立即满足判定式，可进入下一层（仍需会计面）；
- H2：见上"反例"。

**兼容影响（下游参数/触发器）**

- I-11-B：H4 阈值影响 `ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER` / `ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 的达成判定（**注意这两个参数仍是 `_PLACEHOLDER`，阈值审定不等于参数放行**）；
- I-11-B：H2 阈值未定 ⇒ `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的 falsifier 不可执行（与 OPEN-2 联动）；
- I-11-B/I-07-E：H7 判定式受 OPEN-3 分部口径变更影响；H8 影响 `MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027` 的解除条件；
- I-11-C：复用 `falsifier.threshold / threshold_basis / revert_rule` 结构，本工位的修订（H8 来源集合、H4 豁免分支）需同步；
- 校验器 `validate_hypotheses.py` 的 `threshold_basis` 闭集：本裁定**未新增枚举值**，不触发 schema 变更（若会计面要新增 `industry_reviewer_approved`，须按 DEC-6 恢复规则同步校验器，属会计面/实现者）。

**恢复规则（追加式）**

- 任一阈值被进一步证据修订 ⇒ 新建 attempt + 追加 `ruling_r2.md` + `supersedes` 标注；旧阈值版本保留供 I-12 评分（与 `decision.md:174-175` 的恢复规则一致）；
- **不得**在本文件内就地改数。

**被拒替代方案**

- 把 ±5% 直接当已审定值放行（DEC-6 明文禁止的 (a) 方案）；
- 把 0.9–1.1 当占位而不给依据（我已给依据与豁免分支，但**不等于**会计面已审定）；
- 为"凑齐三条 pjr"而强行给 H2 一个数字（无口径、无基准 ⇒ 违反 fail-closed）；
- 把 H7 的判定式改回幅度阈值（口径混淆）。

---

## ④ Provenance 摘要

完整逐条见同目录 `provenance.json`（UTF-8 无 BOM、LF、写后重解析）。

- **本地证据条目**：11 条（`LOC-01`…`LOC-11`），全部含文件路径 + 行号 + sha256（或命令 + 工具 sha256 + 实测计数）；
- **外部条目**：12 条（`EXT-01`…`EXT-12`），其中 **成功取回 9 条 / 失败 3 条**（`sec.gov browse-edgar 403`、`sec.gov Archives 8-K 直连 403`、`microsoft.gcs-web.com PDF content-type 不支持`）；**实际进入裁定引用的外部条目 5 条**（`EXT-02` OSC/Form 43-101F1 条款；`EXT-05` SEC 8-K 原文（经 `r.jina.ai` 渲染）；`EXT-06`/`EXT-07` stocktitan、analystlens 二级佐证；`EXT-08` DuckDuckGo 检索索引页用于定位）；
- **工具失败记录**：1 条（`TOOL-01`：`web_search` 端点返回非 JSON 错误，改用 `web_fetch` 直取 + DuckDuckGo HTML 检索）；
- **合计 provenance 条目**：24 条。
- **取证时间窗（UTC）**：`2026-09-24T20:20Z – 20:34:43Z`（本 session；`web_fetch` 未提供逐请求时间戳，故外部条目统一登记该窗口与记录时点，**不伪造精确到秒的单条时间**）。
- **快照**：**未落任何快照文件**（写入面被限定为 3 个文件）⇒ 外部条目 `snapshot_path = null`、`snapshot_sha256 = null`，仅登记 URL + 取回窗口 + 原文引文。
- **外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`；`2026-09-02 8-K` 条目显式写明"**本地不可核，外部获取，不得作为本地可核证据放行**"。

---

## ⑤ `BLOCKED` 清单（缺什么）

| # | BLOCKED 项 | 缺什么 | 归谁 |
|---|---|---|---|
| **BLOCKED-1** | OPEN-5 归属：**谁解决港股年报原文可读性**（对象流解析 / 离线 PDF 库 / 合规外部工具 / 依赖升级） | 环境/依赖 owner 的路径指派与授权（I-00-B 侧；OPEN-1 类比） | **`BLOCKED-pending-owner`**，我不代裁 |
| **BLOCKED-2** | OPEN-2：给出**可放行的铜当量系数取值 / 单位收入数值** | 公司披露的换算系数与**同口径当量销量**（本地全文扫描 0 命中）；或 owner 授权的 B 类情景假设 + 会计面认可 | 矿业 reviewer（本工位）+ 会计面；当前**阻塞** |
| **BLOCKED-3** | OPEN-2：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 进入 I-11-B 校准 | BLOCKED-2 + 会计面证据等级 | I-11-B **阻塞** |
| **BLOCKED-4** | OPEN-3：2026-09-02 8-K 与 Exhibit 99.1 **进入本地可核来源** | filing-fetch 授权获取 + hash 登记（本地 0 个 8-K 已枚举复核） | filing-fetch / owner + 会计面 |
| **BLOCKED-5** | OPEN-3：`MSFT_PBP/IC/MPC_REVENUE_FY2027` 放行、I-07-E 微软分部口径冻结 | BLOCKED-4 + 会计面证据等级；新两分部参数同样因只存于外部而不可放行 | I-11-B / I-07-E **阻塞** |
| **BLOCKED-6** | OPEN-6：H2 单位收入阈值的**替代数值**（±5% 不采用） | OPEN-2 口径裁定 + 价格归一化基准（价格序列/期间/净价口径） | 矿业 reviewer + 会计面；**保持 `professional_judgement_required` 未审定** |
| **BLOCKED-7** | OPEN-5 行业处置：港股分部命题与 I-11-B 港股参数 | 非"缺证据待补"，而是**按规定保持不可用**；解锁条件见 §③ OPEN-5 C 表 + BLOCKED-1 | I-07-B / I-11-B 港股参数 **保持 `_PLACEHOLDER`，不得放行** |

> 本工位**未给任何"看起来完成"的值**：H2 无替代数、系数无取值、8-K 无本地化、港股无命题。

---

## ⑥ 边界声明（可核）

1. **零产品写**：本工位**没有**创建/修改 `.planning` 之外的任何文件；对 `company-wiki` 的两次操作为**只读取文与哈希**（`pdftotext` 输出到管道、`Get-FileHash`），未落盘、未改字节。
2. **零 git 写**：未执行 `git add` / `commit` / `checkout` / `stash` / `restore` / `reset` 任何变体。
3. **零 I-11-A 改动**：`execution_runs/I-11-A/a20260919-01` 下**未写入任何字节**（只读 `decision.md` / `review.md` / `handoff.json` / `binding.json` / `evidence/**`）。
4. **零 status 变更 / 零代签**：不改 I-11-A 的 `status`、`reviewer_status`、`status_authority`、`open_questions`；不写任何 `approved_frozen`；本文件不构成验收。
   - `handoff.json` → `does_not_claim_I11A_acceptance = true`。
5. **git 可核计数**：`git -c core.quotepath=false diff HEAD --name-only`

   | 时点 | total | **non-`.planning`** |
   |---|---|---|
   | 开工前基线（本工位首次写入之前） | 3821 | **0** |
   | 收尾复测（三个文件写入并校验之后） | 3822 | **0** |

   - **`git_diff_non_planning = 0`（要求值 0，实测 0）**；
   - total 由 3821 → 3822 的 +1 落在 `.planning/**` 内（本仓库存在并发写入方，porcelain 计数本就在双向变动）；
   - 本工位三个新文件经 `git ls-files --others --exclude-standard` 复核为**恰 3 个未跟踪路径**（`ruling.md` / `provenance.json` / `handoff.json`），且 `git diff HEAD --name-only` 中**含 `I11A-OPEN-IND` 的路径数 = 0**（新文件未跟踪，不进 `git diff HEAD`）；
   - 仓库内其余 3821/3822 条差异均为**本次工作之前已存在**的他人改动，本工位未触碰。
6. **被审对象未被改动（哈希复核）**：收尾时重新计算 `I-11-A/a20260919-01` 关键文件 sha256，与开工前读取值逐一相同——`decision.md e9c96f02…`、`review.md 4938e745…`、`handoff.json e4dafd16…`、`binding.json 9d9c89a7…`、`evidence/I-11-A/hypotheses.json f2178768…`（5/5 `unchanged=True`）。
7. **载体自检**：三个文件均 **UTF-8 无 BOM**、**CR=0（纯 LF）**；`provenance.json`、`handoff.json` 写后重解析 `OK`。
