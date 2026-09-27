# I-07-E 校准/验证汇总表（研究草稿 · 全量数值 proposed/mapped_not_released）

> 卡：`execution_v2/card_I-07-E.md`（sha `9552ac98…`/1,773 B）· attempt：`execution_runs/I-07-E/a20260926-01` · role：`implementer_i07e`
> **性质**：本件为卡文 L10 所允许的**研究草稿**；**正式发布格 = `blocked`（`formal_publication_slot=blocked`）** —— 本工位无正式签名能力，且 `params_released=false`、`implementer_signed=false`、`releases_nothing=true`、`status=review_pending`。
> **数值纪律**：全部数值为校准/映射**登记值**（`proposed_not_released` / `mapped_not_released`，同 H4 (iv) 形态）；store 侧 `low/base/high` 仍 null、两个 `_PLACEHOLDER` 维持；本件**放行任何参数 = 0**。
> **机器校验锚点**：`open2_ban_observed=true` · `synthetic_quarantine_enforced=true` · `params_released=false` · `formal_publication_slot=blocked`。
> **逐项来源**：CP=`I-11-B/a20260926-01/calibration_plan.json`；EAF=`I-11-B/a20260926-01/expert_assumptions.json`；PM=`I-11-C/a20260926-01/parameter_mapping.json`；MV=`I-11-C/a20260926-01/mapping_verification.json`；ST=`OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，只读）；SEAL=`I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（封盘，只读）；I10A=`I-10-A/a20260923-01`；SRC=`I-11-A/a20260919-01/evidence/I-11-A/source_map.json`。

---

## §A 三公司冻结（卡文动作 1：基期 / 分部口径 / 币种单位 / 信息日 / 年度路径 / 来源 claim；缺信息显式保留，不伪造 capture）

| 公司 | 基期 | 分部口径 | 币种单位 | 信息日 | 年度路径 | 来源 claim（doc_id / sha256 / 锚） | 显式保留的缺口 |
|---|---|---|---|---|---|---|---|
| 紫金矿业（CN） | **FY2025 年度实际**（产销量表 + 分部报告对外销售收入行）；FY2026 仅作**管理层目标对照**（不独立） | 四报告分部**对外销售收入**（矿产品/冶炼/贸易/其他）；含内部交易的分部总计不得直接相加；抵销仅在恒等式桥 | 人民币元（量：吨/千克） | 披露/可得 `published_at=available_at=2026-03-20`；`as_of=2026-09-18` | **FY2025（基期）→ FY2027（生效）**：base=最后可得同口径年度值不变（朴素基线 EA-3）；FY2026 计划值只作达成率情景上界 | `CN-ZIJIN-AR2025` / `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d`（I-07-B 前后两次复核一致）/ p327-p328「对外销售收入」、p44「产销量情况分析表」、p56「2026年公司主要矿产品产量计划」；evidence=`I-11-A/extract/P1_zijin_pages.json` | 分金属实现价（铜/金）基期不可复算（无产品线量价行口径）⇒ 槽位显式拒绝出数；库存释放（铜 +6,763 吨 / 金 +418 千克）**不外推为常态** |
| 小米集团（HK） | **FY2025**：仅 I-10-A 已签映射 case 的历史复建值（XM-PHONE-M03：165,200,000 部×1,128.7 元；XM-EV-M03：411,082 辆×251,171 元 + other_revenue 2,800,000,000 元） | 手机出货量×平均售价（p.21 MD&A + 附注 5 产品线收入）；EV 交付量×ASP + 其他收入显式单列一次 | 人民币元（量：部/辆） | `as_of=2026-09-18`；**披露日未在回源面内登记 ⇒ 显式保留** | **缺位（显式保留）**：store 8 条 hypotheses = 紫金 5 + 微软 3，**小米 FY2027 hypothesis/参数槽位 = 0**；不伪造 capture | `HK-XIAOMI-AR2025` / `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c`（I-07-B 前后复核一致）/ p.21「出貨量×平均售價」；解码面：I-10-A `decode_hk_text.py` mapped 272,511 / unmapped 0 | ⭐ **I-11-A `source_map.json` 实测：`HK-XIAOMI-AR2025` = `not_readable_in_this_attempt`（`STOP_EVIDENCE`，no value cited）** ⇒ I-11 命题层零小米条目；FY2027 年度路径**无可核载体** ⇒ 该公司判**明确 blocked-缺位**（fail-closed），不补假数据 |
| 微软（US） | **FY2026**（截至 2026-06-30）三分部收入与已披露增速（PBP 139,996 / IC 137,791 / MPC 54,052 USD mn；+16% / +30% / −1%，仅作对照） | 合并报表**三分部**口径（Productivity and Business Processes / Intelligent Cloud / More Personal Computing）；Microsoft Cloud 聚合**不得**与 IC 并列（E6 PROHIBITED_CO_USE） | USD million（增长率=小数） | `published_at=available_at=2026-07-29`；`as_of=2026-09-18` | **FY2026（基线年）→ FY2027（生效）**：base=FY2026 已披露增速持续（EA-4 纯分析师判断）；g_low/g_high=(1+g)×0.95/1.05−1 | `US-MSFT-10K-FY2026` / store 记 `e3de0053…40ecff`（**63 位，见 u-N4**）vs I-07-B 实测 `e3de0053…40ecfff`（64 位）/ table 74/76、MD&A「Microsoft Cloud revenue」；evidence=`I-11-A/extract/P1_msft_tables.json` | FY2027 增速**无任何已披露/可核来源**（EA-4）；Microsoft Cloud（$214.4bn 叙述值）与 Licensing-vs-Cloud 拆分**无换算公式/无行内拆分** ⇒ 两槽位显式拒绝出数 |

**缺口登记（卡文 L8「缺信息显式保留」的总账）**：
- `gap-U1`（小米年度路径）：无 FY2027 命题/参数载体（I-11-A `STOP_EVIDENCE`）——**blocked-缺位**，不写 3/3 的直接依据。
- `gap-U2`（小米披露日）：`published_at/available_at` 未在回源面内登记。
- `gap-U3`（卡文 L11「H1锁定」）：本卡回源面（I-07-B/C/D、I-08-A、I-09-A/B/C、I-10-A、I-11-A/B/C、store、OWNER_DECISIONS、REMEDIATION_REGISTER）**未检出该口径的已审载体** ⇒ 显式保留，不伪造处理记录（fail-closed）。
- `gap-U4`（卡文 L11「微软重述」）：同上，未检出已审载体 ⇒ 显式保留。
- （对照）卡文 L11「合并/内部抵销」**有**已审载体：H-CN-ZIJIN-ELIM-05 / E5（见 §C）。

---

## §B 校准汇总表（卡文动作 2/3 的参数面；18 槽位逐位对齐 CP 18 `parameters` × PM 18 `mapping_rows`）

> 全部数值 = **登记值，未放行**。`拟定 low/base/high` 列凡有值者状态均为 `proposed_not_released`/`mapped_not_released`；`null` 行为显式拒绝/不可执行。

### B1 紫金（13 槽位）

| # | parameter_id | 模型/驱动 | 单位 | 基期→生效 | 原值 | 拟定 low / base / high（未放行） | 方法 + 依据（文件:行） | EA | 状态 / blocked_by |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027 | direct_revenue / revenue | 人民币元 | FY2025→FY2027 | 109,977,556,345（差额法=H-02 引数双路同值；store 原值 349,079,082,852 见 u-N5） | 104,478,678,528 / 109,977,556,345 / 115,476,434,162 | contract arithmetic（p327/p328 对外销售收入行；349,079,082,852−165,858,644,874−29,212,610,830−44,030,270,803=109,977,556,345，差=0）CP L38-L48；EAF L11-L19/L29-L37/L47-L55；ST L39 | EA-1/3/5 | mapped_not_released；OPEN-2（量价系数）+ unverified-N1/N5 |
| 2 | ZIJIN_SEG_SMELT_EXTERNAL_REVENUE_FY2027 | direct_revenue / revenue | 人民币元 | FY2025→FY2027 | 165,858,644,874 | 157,565,712,630 / 165,858,644,874 / 174,151,577,118 | contract arithmetic ±5%（max\|偏差\|=0.3 元）CP L49-L59；ST L49 | EA-1/3 | mapped_not_released |
| 3 | ZIJIN_SEG_TRADE_EXTERNAL_REVENUE_FY2027 | direct_revenue / revenue | 人民币元 | FY2025→FY2027 | 29,212,610,830 | 27,751,980,289 / 29,212,610,830 / 30,673,241,372 | contract arithmetic ±5%（max\|偏差\|=0.5 元，.5 对称进位）CP L60-L70；ST L56 | EA-1/3 | mapped_not_released |
| 4 | ZIJIN_SEG_OTHER_EXTERNAL_REVENUE_FY2027 | direct_revenue / revenue | 人民币元 | FY2025→FY2027 | 44,030,270,803 | 41,828,757,263 / 44,030,270,803 / 46,231,784,343 | contract arithmetic ±5%（max\|偏差\|=0.15 元）CP L71-L81；ST L63 | EA-1/3 | mapped_not_released |
| 5 | ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027 | resource / realized_price | 人民币元/吨铜当量 | FY2025→FY2027 | 109,977,556,345/885,141（≈**124,248.63**，推导值非披露原文） | **传播值 = null / null / null**（I-11-B proposed 118,036.2 / 124,248.63 / 130,461.06 仅存档于登记区，**禁消费**） | 转换公式分母**不自洽**（884,943+83,161×24=2,880,807 ≠ 885,141；按合成分母商≈**38,175.95**，差 3.25×/3.26×）CP L82-L92；EAF L11-L19/L20-L28；ST L170/L175 | EA-1/2 | **`registered_not_consumed`（⭐OPEN-2 禁消费红线，见 §F）**；`not_executable_no_propagation`；unverified-N2 |
| 6 | ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027 | resource / realized_price | 人民币元/吨 | FY2025（未取得）→FY2027 | null | null / null / null | 无基期：可读面内无铜产品线量价行（CP L93-L103；ST L180）；显式拒绝出数（EA-7） | EA-7 | unmapped_declined_no_number；OPEN-2 |
| 7 | ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027 | resource / realized_price | 人民币元/克 | FY2025（未取得）→FY2027 | null | null / null / null | 金锭（冶炼产品）≠ 矿产金口径（CP L104-L114；ST L199）；显式拒绝出数（EA-7） | EA-7 | unmapped_declined_no_number；OPEN-2 |
| 8 | ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027 | resource / saleable_volume | 吨 | FY2025→FY2027 | 884,943（FY2025 销售量；产量 878,180） | 796,448.7 / 884,943 / 973,437.3 | historical relationship ±10%（逐位相等）；销量 ≤ 产量 + 期初库存；库存释放 +6,763 吨不外推 CP L115-L124；ST L327-L345 | EA-1/3 | mapped_not_released；BLOCKED-6b/OPEN-11（量恒等式约束未闭合） |
| 9 | ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027 | resource / saleable_volume | 千克 | FY2025→FY2027 | 83,161（FY2025 销售量；产量 82,743） | 74,844.9 / 83,161 / 91,477.1 | historical relationship ±10%；+418 千克不外推 CP L126-L135；ST L327-L345 | EA-1/3 | mapped_not_released；BLOCKED-6b（R2 154 千克 NOT_SIGNED） |
| 10 | ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027 | resource / saleable_volume | 吨 | FY2025→FY2027 | 352,470 | 317,223 / 352,470 / 387,717 | historical relationship ±10% CP L137-L146 | EA-1/3 | mapped_not_released |
| 11 | ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027 | resource / saleable_volume | 千克 | FY2025→FY2027 | 430,254 | 387,228.6 / 430,254 / 473,279.4 | historical relationship ±10% CP L148-L157 | EA-1/3 | mapped_not_released |
| 12 | ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER | resource / saleable_volume | 千克（金）/吨（铜） | FY2026（计划年度，对照） | 矿产金 105 吨、矿产铜 120 万吨（AR2025:p56 计划值，**管理层目标**） | 金 94,500 / 105,000 / 115,500；铜 1,080,000 / 1,200,000 / 1,320,000（达成率 [0.9,1.1]，H4 行业面带） | expert assumption + 管理层目标原值；`management_target_is_not_independent=true`（不得作独立准确性证据）CP L159-L169；ST L522-L540 | EA-1/3 | proposed_not_released（**_PLACEHOLDER 维持**）；§三十四 边界 |
| 13 | ZIJIN_SEGMENT_RECONCILIATION_FY2027 | direct_revenue / revenue | 人民币元 | FY2025→FY2027 | 584,049,229,264 − 234,970,146,412 = 349,079,082,852 | 0 / 0 / 0（恒等式偏差，容差 τ=1 元，ACCT R1/R3 SIGNED） | contract arithmetic（纯恒等式，两期可核 FY2025/FY2024）CP L171-L180；ST L626-L644 | （无 EA） | mapped_not_released；store state=unquantified（6b 路径(c)，本卡不改 store） |

### B2 微软（5 槽位）

| # | parameter_id | 模型/驱动 | 单位 | 基期→生效 | 原值 | 拟定 low / base / high（未放行） | 方法 + 依据 | EA | 状态 / blocked_by |
|---|---|---|---|---|---|---|---|---|---|
| 14 | MSFT_PBP_REVENUE_FY2027 | direct_growth / growth_rate | 小数 | FY2026→FY2027 | 0.16（FY2026 已披露增速，仅对照） | 0.102 / 0.16 / 0.218（g_low=51/500、g_high=109/500 逐位相等） | historical relationship + expert assumption（增速持续=纯分析师判断）CP L182-L192；ST L731-L754 | EA-1/4 | mapped_not_released；OPEN-3 |
| 15 | MSFT_IC_REVENUE_FY2027 | direct_growth / growth_rate | 小数 | FY2026→FY2027 | 0.30 | 0.235 / 0.30 / 0.365（47/200、73/200） | 同上 CP L193-L203；ST L731-L754 | EA-1/4 | mapped_not_released；OPEN-3 |
| 16 | MSFT_MPC_REVENUE_FY2027 | direct_growth / growth_rate | 小数 | FY2026→FY2027 | −0.01（不得被集团增长掩盖） | −0.0595 / −0.01 / 0.0395（−119/2000、79/2000） | 同上 CP L204-L214；ST L731-L754 | EA-1/4 | mapped_not_released；OPEN-3 |
| 17 | MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER | direct_revenue / revenue | USD million | FY2026→FY2027（unquantified） | 214,400（叙述值，非表格精确值） | null / null / null | **无可用换算公式**（缺 Microsoft Cloud→分部/产品行完备映射表）CP L215-L225；ST L855-L878 | EA-7 | unmapped_declined_no_number（**_PLACEHOLDER 维持**）；OPEN-3 |
| 18 | MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027 | subscription / composition | USD million | FY2026→FY2027（pending） | 101,997（FY2026 产品行合计口径） | null / null / null | **缺行内拆分**（云/许可分项、平均付费席位、净 ARPU）CP L226-L235；ST L960-L983 | EA-7 | unmapped_declined_no_number；OPEN-3 |

**小计（与 MV `action_1_summary` 逐位一致）**：18 槽位 = **13 可执行/已映射（全部 `mapped_not_released`）+ 5 不可执行/显式拒绝**（REALIZED_UNIT + 两分金属实现价 + MSFT_CLOUD + MSFT_LICENSING）；`synthetic_numbers_in_real_fields=0`；`contract_arithmetic_only=1`（RECON）；经 EA 承接 17 行（RECON 除外）。小米 = **0 槽位**（gap-U1）。

### B3 EA 模板逐条转录核（H4 (iv) 形态；EAF 7 条全量，缺任一字段 ⇒ 该条不成立 ⇒ 对应参数 STOP_CALIBRATION）

| id | 假设（摘要） | 敏感性区间（low/base/high · unit · 带理由摘要） | equivalent_to_disclosure_basis | release_state | blocked_by_residuals | 来源 |
|---|---|---|---|---|---|---|
| EA-1 | 幅度带形状借用行业面已审定阈值带（量 [0.9,1.1]、价/收入 ±5%、增长率按产出收入 ±5% 换算）；带形状=敏感性设计非精度主张 | 各参数 base×0.9/0.95 · base · base×1.1/1.05（g 按 (1+g)×0.95/1.05−1）· 随参数单位 · 锚定 H2/H4 审定带形状，收窄 ±2%/±5% 则 low/high 收缩约 60% | equivalent_to_disclosure_basis=true | not_released | OPEN-6（H4 四要件未齐/口径桥未闭合） | EAF L11-L19 |
| EA-2 | 金→铜当量换算系数 = 24 吨/千克（**示意值**，非披露值）用于 REALIZED_UNIT 分母折算 | 系数 23 ⇒ ≈134,919.5 · 24 ⇒ 124,248.63 · 25 ⇒ 113,577.74 · 人民币元/吨铜当量 · 两点差分：系数每 +1 吨/千克 ⇒ −10,670.89（非偏导） | equivalent_to_disclosure_basis=true | not_released | **OPEN-2**（放行=BLOCKED；参数保持 _PLACEHOLDER） | EAF L20-L28 |
| EA-3 | 基期 = 最后可得同口径年度值不变（FY2025 实际 → FY2027 朴素基线）；FY2025 库存释放效应不外推为常态 | base×0.9/0.95 · FY2025 同口径值 · base×1.1/1.05 · 随参数 · 基线选择对 2 年期 CAGR 敏感性 ±0%（持平）vs 趋势外推 ±10% 以上 | equivalent_to_disclosure_basis=true | not_released | （无） | EAF L29-L37 |
| EA-4 | MSFT 三分部 FY2027 增长率 base = FY2026 已披露增速持续（+16%/+30%/−1%）；low/high 由产出收入 ±5% 换算 | PBP 0.102/0.16/0.218 · IC 0.235/0.30/0.365 · MPC −0.0595/−0.01/0.0395 · 小数 · 带宽=收入 ±5%；注记合计区间与自身带换算不符=unverified-N3（登记） | equivalent_to_disclosure_basis=true | not_released | OPEN-3（MSFT 分部口径全部维持不放行） | EAF L38-L46 |
| EA-5 | 矿产品分部对外收入基期 = 109,977,556,345 元（差额法=H-02 引数法双路同值） | 104,478,678,528（−5%）· 109,977,556,345 · 115,476,434,162（+5%）· 人民币元 · 若认定 store 原值 349,079,082,852 才是该参数语义 ⇒ base 差约 3.17 倍（最大敏感性来源，优先裁并） | equivalent_to_disclosure_basis=true | not_released | unverified-N1/N5 | EAF L47-L55 |
| EA-6 | 联合情景相关性：同一事件驱动的量、价、额外收入三通道沿同一情景档联动；low/high 为成对联动档位 | 联合低档 ≈−14.5% · 各 base · 联合高档 ≈+15.5% · 复合（收入）· 独立极值组合会产生 ≈+21% 不可能联合情景（STOP_SCENARIO 拦截对象） | equivalent_to_disclosure_basis=true | not_released | （无） | EAF L56-L63 |
| EA-7 | **analyst_assumption_declined（显式拒绝出数）**：两分金属实现价、MSFT_CLOUD、MSFT_LICENSING 四槽位不作任何幅度假设，维持 null/unquantified/_PLACEHOLDER | n/a（无数值）· 带设计已预登记（±5% 形状，EA-1）：解锁并取得基期后按同形状出数，无需新方法 | equivalent_to_disclosure_basis=true | not_released（无值可放） | OPEN-2 / OPEN-3 | EAF L65-L73 |

（模板完整性实测：`count=7`、`all_have_sensitivity_interval=true`、`all_equivalent_to_disclosure_basis_false=true`，EAF L75-L77；本卡不新增 EA。）

---

## §C 管理目标、增长驱动与关键口径（卡文动作 2）

### C1 管理目标（独立性受限）
- `H-CN-ZIJIN-PLAN-04` FY2026 计划：矿产金 105 吨 / 矿产铜 120 万吨（AR2025:p56，原文为指导性指标、不构成承诺）⇒ **只作 base 情景对照上界 + 达成率情景**；`management_target_is_not_independent=true`（卡文 L14 + CP `value_policy`）。

### C2 主要增长驱动按 I-11 映射（共享驱动 D1-D7，CP L239-L246 转录）
- D1 realized_price（矿产品实现价）· D2 saleable_volume · D3 other_revenue（XM-EV 映射 2,800,000,000 元，只进一次）· D4 copper_equivalent_coefficient（24 吨/千克，仅量侧一次）· D5 elimination_bridge（234,970,146,412 元，仅恒等式桥）· D6 management_plan_FY2026（独立性受限）· D7 segment_growth_MSFT（三分部建模，与集团增速互斥）。

### C3 同一事件复用检查（E1-E7，CP L249-L255 逐条转录；MV `stop_scenario` 复核）
- E1 库存释放 → 仅销量通道 `ALLOWED_ONCE` ✅ · E2 金→铜当量折算 → 仅量侧一次 ✅ · E3 管理层计划 → 仅情景对照 ✅ · E4 其他收入 2.8e9 → 显式单列一次 ✅ · E5 内部抵销 → 仅恒等式桥 ✅ · E6 Microsoft Cloud ↔ IC = `PROHIBITED_CO_USE` ✅ · E7 FY2026 分部增速 → 三分部建模、集团增速不用 ✅。
- 联合情景约束（EA-6）：S-MIN-PRICE / S-VOL-PRICE / S-MSFT-SEG **成对联动**，禁止量 high×价 high×其他收入 high 独立叠加（≈+21% 不可能联合）⇒ `STOP_SCENARIO` 未触发。

### C4 卡文 L11「已审关键口径」逐项处置
| 口径 | 处置 | 依据 |
|---|---|---|
| 合并/内部抵销 | **沿用已审形态**：合并收入 = Σ四分部对外销售收入；内部销售收入 234,970,146,412 元只出现在抵销桥（H-05/E5），不得作任何参数收入基期（否则高估约 67%） | ST `H-CN-ZIJIN-SEG-01` claim + `double_count_exclusion`；H-CN-ZIJIN-ELIM-05；CP L253；MV J 绿证 |
| H1锁定 | **未检出已审载体 ⇒ gap-U3 显式保留**（不伪造处理记录） | 本件 §A 缺口登记；fail-closed |
| 微软重述 | **未检出已审载体 ⇒ gap-U4 显式保留** | 同上 |

---

## §D 验证汇总（卡文动作 4：独立复算 + 跨根可追溯 + 上游一致性核）

### D1 上游一致性核（24 件 sha 全量复算，详见 `verification.json`）
- oracle §2 冻结的 24 件上游文件 sha256 **全部复算一致**（含封盘 `f2178768…`、store `b2063ac8…`）。
- **层内登记差异（只登记、不更正、不消费）**：
  - `u-N4`：store 内 `US-MSFT-10K-FY2026.doc_sha256` = 63 位（`e3de0053…40ecff`）vs I-07-B 实测 64 位（`e3de0053…40ecfff`）—— 转录层缺陷（F-REV-I10A-1 同物种）。
  - `u-N5`（=unverified-N1 继承）：store H-01 `original_value=349,079,082,852` 与矿产品分部语义张力。
  - `u-N6`（=unverified-N3 继承）：EA-4 注记区间 [320,763, 348,432] 与自身带换算（≈[375,283.38, 414,786.90]）不符。

### D2 独立复算（I-11-C `_recompute_action1.py` 精确有理数，MV `action1_recompute_against_oracle` P1-P8 逐项对照；本站复核其结论并复算关键式）
| 检查 | 结果 | 来源 |
|---|---|---|
| 分部加总（恒等式） | 584,049,229,264 − 234,970,146,412 = 349,079,082,852（差=0）；四分部对外合计=349,079,082,852 逐位；毛总计和 138,271,672,956+189,683,879,295+170,521,025,777+85,572,651,236=584,049,229,264 逐位 | MV P4；ST L626-L644；本站手算复核 ✅ |
| 年度增量/带换算 | SEG×4 ±5%（max 偏差 0.25 元，round-to-nearest）；VOL×4 ±10% 逐位相等；PLAN 达成率带逐位相等；MSFT g 换算（51/500、109/500、47/200、73/200、−119/2000、79/2000）逐位相等 | MV P4 |
| 敏感性 | EA-1 带形状（量 ±10%/价 ±5%/g 换算）+ EA-2 系数两点差分（系数每 +1 吨/千克 ⇒ 单位收入 −10,670.89 元/吨）**登记**（禁消费） | EAF L14/L23 |
| 场景约束 | 18 行逐行携带 `joint_scenario_constraint`（EA-6）；E1-E7 复用检查全过；STOP_SCENARIO=false | MV `stop_scenario` |
| 合成示例数隔离 | 隔离清单（quarantine）= 2/8760/0.5/0.6/0.7/40/20/30/32/34/1200/264000/281520/299040/17520；真实数值字段出现次数 = 0；1,200,000（铜计划吨数）与示例 1200 非复制（collision 先例，属隔离口径对照） | MV P5；`synthetic_quarantine_enforced=true` |
| 跨根来源追溯 | 每行来源 = 文件+行号（CP/EAF/ST/SMC/RECOMP）；store 与封盘失效能追溯到具体输入/产物行 | PM `source.basis`；oracle §2 |

### D3 STOP 判定（MV `stop_verification` 逐字对齐）
- **槽位级 STOP = 5 行**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027`（公式不自洽 unverified-N2 + OPEN-2，not_executable_no_propagation）· `ZIJIN_MINERAL_COPPER/GOLD_REALIZED_UNIT_REVENUE_FY2027`（无基期，unmapped_declined_no_number）· `MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER`（无换算公式 + OPEN-3）· `MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027`（无拆分 + OPEN-3）。规则：数据不足 ⇒ 该槽位不出数、不传播（fail-closed）。
- **卡级 `STOP_CALIBRATION` = 未触发**（从严触发式：每个传播幅度皆可溯源或由 EA+敏感性区间承接）；**字面严格读法登记在案**（存在任一 not_executable 槽位即整卡 blocked——若独立复审采该读法 ⇒ 本卡连同 I-11-B 转 blocked，回滚=作废映射行，零封盘/零 store 改动）；**裁定权=独立复审，本站不自裁**。
- **`STOP_SCENARIO` = 未触发**（见 C3）。

---

## §E 三公司独立结果（卡文动作 5：不因一家成功写 3/3）

| 公司 | 结果 | 形态 | 依据 |
|---|---|---|---|
| 紫金矿业 | **有可审查来源链与产物**（13 槽位全部登记） | 研究草稿（未放行）；1 槽位红线禁消费、2 槽位显式拒绝、4 槽位带 blocked_by | §B1；来源链 CN-ZIJIN-AR2025 全 sha 可核 |
| 微软 | **有可审查来源链与产物**（5 槽位全部处置：3 登记 + 2 显式拒绝） | 研究草稿（未放行）；全部 OPEN-3 不放行 | §B2；I-10-A MS-PBP-M05/MS-IC-M06 = `STOP_DISCLOSURE_ADAPTATION`（不授予） |
| 小米 | **明确 blocked**（缺位）：FY2027 命题/参数 = 0；仅 I-10-A 两条已签历史映射 case（XM-PHONE-M03 / XM-EV-M03，限 FY2025 口径） | fail-closed，不伪造 capture | §A gap-U1；I-11-A `source_map.json` `not_readable_in_this_attempt`（STOP_EVIDENCE） |

- **`3/3` 声明 = 否**（小米 blocked-缺位）；本卡**不授予样本外准确性**（accuracy=unproven；准确性 F 归后继 I-12，卡文 L6/L12）。
- **发布格**：研究草稿 = 在（本件）；**正式发布格 = blocked**（无正式签名能力，卡文 L10）。签名资格记录：disclosure_adaptation = I-10-A 4 case 已签（ZJ-MIN-M09/ZJ-SMT-M09/XM-PHONE-M03/XM-EV-M03，各限本公司/分部/口径/期间）+ 2 case 不授予；formula = M01-M31 accepted_scoped（不外推）。
- 下一步归属：交 **I-13 买方验收**（本卡不派，依赖顺序另派）；样本外准确性归 **I-12**（不派）。

---

## §F ⭐ 红线登记区（P2-1 / OPEN-2：**只登记、不消费**；`open2_ban_observed=true`）

| 登记项 | 值 | 性质 | 处置 |
|---|---|---|---|
| `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 登记除法成立值 | **124,248.63** 元/吨铜当量（109,977,556,345 ÷ 885,141，精确有理数 ≈124,248.6297） | 推导值，非披露原文 | **`registered_not_consumed`** —— 禁止进入任何收入路径/年度路径/分部加总/敏感性产出/情景产出/下游映射 |
| store 自写除式真值 | **38,175.95** 元/吨铜当量（按公式合成分母 2,880,807 的商） | store 先天缺陷对照值 | 只登记；与上值差 **3.25×/3.26×**（REMEDIATION_REGISTER L3951「P2-1 真发现」逐字见 oracle §3） |
| I-11-B proposed 三档 | 118,036.2 / 124,248.63 / 130,461.06 | proposed_not_released 存档 | **传播值 = null**（I-11-C `not_executable_no_propagation` 沿用）；OPEN-2 解锁前不得消费 |
| 系数敏感性（EA-2） | 系数 +1 吨/千克 ⇒ 单位收入 −10,670.89 元/吨 | 两点差分（非偏导） | 只登记 |
| 红线原文出处 | `REMEDIATION_REGISTER.md` L3951 | 落定 `not_granted` 首条 | **「OPEN-2 前禁消费」** 本卡全程遵守 |

---

## §G 本件不做什么（边界自宣）

不放行任何参数（`params_released=false`）· 不触发任何 falsifier/自动动作 · 不自签（`implementer_signed=false`）· 不产生 ACCEPT · 不改任何 status/decision/decision_sha256 · 封盘 `I-11-A/hypotheses.json` 零字节（sha `f2178768…`）· store 零改动（sha `b2063ac8…`）· 不新建 hypotheses 版本（`supersedes` 形态未启用）· 不派 I-12/I-13/I-16/I-17 · 不写五份计划文件 · 不写 `.planning` 之外（`git_diff_non_planning=0`）· 禁 git（含 `git status`）· 禁联网（零外部检索；`external_retrieval_not_local` 未触发）· 示例数字隔离（`synthetic_quarantine_enforced=true`）· 缺信息显式保留、残余不隐藏（fail-closed）。
