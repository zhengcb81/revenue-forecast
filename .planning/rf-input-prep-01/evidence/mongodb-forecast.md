# MONGODB, INC.营收预测

- 信息截止日：2026-11-08
- 财年截止日：01-31
- 币种与单位：USD million
- 基期营收：2,006.44
- 预测版本：rf-input-prep-01-mongodb-fy2025-v1

## 核心营收结论

| 情景 | 终值营收 | CAGR | 营收增量 |
|---|---:|---:|---:|
| low | 2,424.25 | 6.5% | 417.81 |
| base | 2,993.79 | 14.3% | 987.35 |
| high | 3,448.82 | 19.8% | 1,442.38 |

## 未来收入主要驱动力

1. **Atlas consumption expansion** — Atlas revenue is recognized on measured consumption; continued workload migration and new application demand raise consumed workload, while disclosed macro pressure slows the growth of existing applications. （Base终年增量 902.92；占正向驱动 91.4%；证据 limited）
2. **Enterprise estate and large-cohort expansion** — Growth in Direct Sales Customers and in the at-least-$100,000 ARR cohort supports term-license and support revenue, whose growth is far slower than Atlas. （Base终年增量 61.44；占正向驱动 6.2%；证据 limited）
3. **Contracted backlog and deferred-revenue conversion** — Remaining performance obligations and deferred revenue give bounded visibility into near-term recognized revenue, including services delivered alongside deployments. （Base终年增量 23.00；占正向驱动 2.3%；证据 limited）

## 历史营收

| 年度 | 营收 | 口径 | 换算 | 来源ID |
|---:|---:|---|---|---|
| 2023 | 1,284.04 | 未声明 | — | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 |
| 2024 | 1,683.01 | 未声明 | — | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 |
| 2025 | 2,006.44 | 未声明 | — | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 |

### 口径可比性

- FY2023→FY2024：口径未声明或可比依据不足（basis not declared on the left observation）；沿用既有数值比较，不视为已核实口径；同比 31.1%。
- FY2024→FY2025：口径未声明或可比依据不足（basis not declared on the left observation）；沿用既有数值比较，不视为已核实口径；同比 19.2%。

### 基数采用

- 实际采用 FY2025 历史观测（2,006.44 USD million，口径 未声明，来源 urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）作为预测基数锚点；与报告总额参数一致（参数 reported_total = 2,006.44，容差 1e-06，差值 0.00）；未附原始值换算记录。

## 九维研究覆盖

- 进入模型：5；数据缺口：3；当前不重要：1。
- 本表用于防止研究漏项，不直接给CAGR或置信度加分。

| 维度 | 状态 | 结论 | 营收传导 | 参数ID | 来源ID | 理由 |
|---|---|---|---|---|---|---|
| company_foundation | modeled_driver | MONGODB, INC. reports as a single operating segment; FY2025 total revenue reconciles exactly to three disclosed revenue categories. | Recognized subscription and services revenue under ASC 606 equals the reported consolidated total. | reported_total, atlas_base, other_subscription_base, services_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | Base perimeter verified against the audited FY2025 consolidated statements of operations. |
| growth_curve | modeled_driver | FY2023-FY2025 revenue grew from 1,284.0 to 2,006.4 USD million, with Atlas-related revenue rising from 808.3 to 1,405.2. | Atlas consumption growth plus a slower-growing term-license and support base drives the consolidated curve. | atlas_growth_2026_base, atlas_growth_2027_base, atlas_growth_2028_base, other_subscription_growth_2026_base, services_growth_2026_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | Three consecutive audited years and the disclosed category split establish the historical curve; forward levels remain analyst assumptions. |
| industry_market | data_gap | No independent database-market size or growth series was read under the bounded one-source research budget. | Market growth would bound Atlas consumption expansion, but no measured market series enters the model. | — | — | A market forecast without a bound, checked primary source would be an invented input; the gap is disclosed instead. |
| competition | data_gap | Competitive share and pricing evidence is limited to issuer risk-factor statements; no independent share or price series was checked. | Competitive pricing would change monetization of consumed workload, which the model does not calibrate. | — | — | Issuer-authored risk language cannot calibrate a competitive price or share path. |
| capacity | immaterial | Delivery capacity is procured cloud infrastructure under multi-year commitments; no disclosed capacity ceiling constrains recognized revenue in the horizon. | Atlas capacity is elastic third-party cloud capacity, so capacity is a cost input rather than a revenue ceiling. | — | — | The filing describes non-cancelable cloud capacity commitments as a margin matter, not a revenue constraint. |
| technology | modeled_driver | The disclosed platform roadmap (vector search, stream processing, search nodes) expands the addressable workload set but has no published revenue conversion. | New workload capabilities raise eligible consumption, which the Atlas growth assumption is conditioned on. | atlas_growth_2027_base, atlas_growth_2028_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | Product capability is mapped only to the growth assumption it informs; no separate revenue line is invented. |
| policy | data_gap | Data-privacy and AI regulation are described qualitatively; no quantified revenue exposure or dated compliance cost was disclosed. | Regulatory change could alter regional demand or hosting topology, which is not calibrated. | — | — | No quantified exposure was read, so the model cannot carry a policy-driven adjustment. |
| customers | modeled_driver | Direct Sales Customers exceeded 7,500 (from 6,400 two years earlier) and customers with at least $100,000 of ARR/MRR rose to 2,396; over 53,100 Atlas customers were reported. | Larger enterprise cohorts expand committed subscription revenue, which informs the other-subscription growth assumption. | other_subscription_growth_2026_base, other_subscription_growth_2027_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | Customer and cohort counts are disclosed stocks; they inform direction and level discipline but do not by themselves produce a revenue path. |
| demand | modeled_driver | Demand growth is measured only through consumption; the filing discloses slower growth of existing Atlas applications under macro pressure. | Consumption growth of existing and new applications drives usage-based Atlas revenue. | atlas_growth_2026_base, atlas_growth_2027_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | Demand evidence is issuer-disclosed and directional; the magnitude stays an analyst assumption. |

## 管理层沟通与营收目标覆盖

- 已检查官方沟通类别：0/6；重大/相关目标：0；已进入情景：0；独立基准比较：0；未建模：0。

| 沟通类别 | 状态 | 结论 | 目标ID | 来源ID |
|---|---|---|---|---|
| latest_annual_filing | incomplete | FY2025 Form 10-K (filed 2025-03-21) read for the revenue note, MD&A revenue discussion and risk factors. A later FY2026 Form 10-K original exists in local storage but is not a capture-ready registered source (no published_date in the catalog projection), so the latest audited annual report could not be incorporated and completeness is not claimed. | — | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 |
| latest_results_release | incomplete | No official results release was retrieved in this bounded source acquisition; quarterly guidance wording is therefore not represented in the target ledger. | — | — |
| latest_earnings_call | incomplete | No official earnings-call transcript was retrieved; call commentary is not represented. | — | — |
| latest_investor_presentation | incomplete | No investor presentation was retrieved; presentation-only targets are not represented. | — | — |
| latest_strategy_communication | incomplete | The FY2025 10-K strategy and MD&A sections were read; no dated numeric revenue target appears in them, and later strategy communications were not acquired. | — | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 |
| material_announcements_since_last_filing | incomplete | No post-FY2025-filing announcement set was acquired, so post-filing material targets are not represented. | — | — |

| 目标 | 强度 | 原始目标 | 来源期间 | 测量口径/模型期间 | 业务口径 | 处理 | 映射情景 | 模型兑现度 |
|---|---|---:|---|---|---|---|---|---|

## 年度情景路径

| 年度 | Low | Base | High | Base同比 |
|---:|---:|---:|---:|---:|
| 2026 | 2,180.07 | 2,316.54 | 2,443.71 | 15.5% |
| 2027 | 2,315.67 | 2,650.18 | 2,929.06 | 14.4% |
| 2028 | 2,424.25 | 2,993.79 | 3,448.82 | 13.0% |

## 三情景经营驱动

| 分部 | 情景 | 驱动 | 年度 | 参数ID | 数值 |
|---|---|---|---:|---|---:|
| MongoDB Atlas-related | low | growth_rate | 2026 | atlas_growth_2026_low | 0.12 |
| MongoDB Atlas-related | low | growth_rate | 2027 | atlas_growth_2027_low | 0.09 |
| MongoDB Atlas-related | low | growth_rate | 2028 | atlas_growth_2028_low | 0.07 |
| MongoDB Atlas-related | base | growth_rate | 2026 | atlas_growth_2026_base | 0.20 |
| MongoDB Atlas-related | base | growth_rate | 2027 | atlas_growth_2027_base | 0.18 |
| MongoDB Atlas-related | base | growth_rate | 2028 | atlas_growth_2028_base | 0.16 |
| MongoDB Atlas-related | high | growth_rate | 2026 | atlas_growth_2026_high | 0.27 |
| MongoDB Atlas-related | high | growth_rate | 2027 | atlas_growth_2027_high | 0.24 |
| MongoDB Atlas-related | high | growth_rate | 2028 | atlas_growth_2028_high | 0.21 |
| Other subscription (Enterprise Advanced and related) | low | growth_rate | 2026 | other_subscription_growth_2026_low | 0.00 |
| Other subscription (Enterprise Advanced and related) | low | growth_rate | 2027 | other_subscription_growth_2027_low | -0.02 |
| Other subscription (Enterprise Advanced and related) | low | growth_rate | 2028 | other_subscription_growth_2028_low | -0.03 |
| Other subscription (Enterprise Advanced and related) | base | growth_rate | 2026 | other_subscription_growth_2026_base | 0.04 |
| Other subscription (Enterprise Advanced and related) | base | growth_rate | 2027 | other_subscription_growth_2027_base | 0.04 |
| Other subscription (Enterprise Advanced and related) | base | growth_rate | 2028 | other_subscription_growth_2028_base | 0.03 |
| Other subscription (Enterprise Advanced and related) | high | growth_rate | 2026 | other_subscription_growth_2026_high | 0.09 |
| Other subscription (Enterprise Advanced and related) | high | growth_rate | 2027 | other_subscription_growth_2027_high | 0.08 |
| Other subscription (Enterprise Advanced and related) | high | growth_rate | 2028 | other_subscription_growth_2028_high | 0.07 |
| Services | low | growth_rate | 2026 | services_growth_2026_low | 0.08 |
| Services | low | growth_rate | 2027 | services_growth_2027_low | 0.07 |
| Services | low | growth_rate | 2028 | services_growth_2028_low | 0.06 |
| Services | base | growth_rate | 2026 | services_growth_2026_base | 0.12 |
| Services | base | growth_rate | 2027 | services_growth_2027_base | 0.11 |
| Services | base | growth_rate | 2028 | services_growth_2028_base | 0.10 |
| Services | high | growth_rate | 2026 | services_growth_2026_high | 0.15 |
| Services | high | growth_rate | 2027 | services_growth_2027_high | 0.14 |
| Services | high | growth_rate | 2028 | services_growth_2028_high | 0.13 |

## 分部驱动与收入确认

| 分部 | 模型 | 基期营收 | 确认时点 | 触发条件 | 列报 |
|---|---|---:|---|---|---|
| MongoDB Atlas-related | direct_growth | 1,405.18 | mixed | Consumption of the managed database service during the period (usage-based). | gross |
| Other subscription (Enterprise Advanced and related) | direct_growth | 538.68 | mixed | Delivery and transfer of control of the term licence, with support recognized ratably over the contract term. | gross |
| Services | direct_growth | 62.58 | mixed | Delivery of consulting and training services over the engagement period. | gross |

## Base情景增量归因

| 项目 | 终值营收增量 |
|---|---:|
| MongoDB Atlas-related | 902.92 |
| Other subscription (Enterprise Advanced and related) | 61.44 |
| Services | 23.00 |
| 公司级调整 | 0.00 |
| 合计 | 987.35 |

## 收入增长驱动树

### Atlas consumption expansion

- 结论：Atlas revenue is recognized on measured consumption; continued workload migration and new application demand raise consumed workload, while disclosed macro pressure slows the growth of existing applications.
- 因果链：Existing and new applications consume more database workload → Consumed usage is billed monthly in arrears → Usage-based revenue is recognized as the service is delivered → Atlas-related revenue grows at the modelled rate
- Base终年增量：902.92；正向增量占比：91.4%
- 归因分部：MongoDB Atlas-related=100.0%
- 模型参数：atlas_growth_2026_base, atlas_growth_2027_base, atlas_growth_2028_base
- 持续性：uncertain；Consumption growth has persisted for three audited years but the issuer discloses macro-driven slowing of existing applications, so persistence is not assumed structural.
- 领先指标：Quarterly Atlas consumption growth disclosed in later filings；Remaining performance obligations recognised within twelve months
- 可证伪条件：Atlas revenue growth below 7% in any forecast year；Disclosed consumption growth turning negative
- 反证检索：found；The filing itself discloses macro-driven slowing of existing Atlas applications; the low case is built around that headwind rather than dismissed.
- 证据状态：limited
- 支撑证据：
  - [issuer_recognition_disclosure/direct] Atlas revenue is usage-based and billed in arrears, so consumption is the recognized-revenue driver.（Claim: claim_ev_atlas_consumption_basis；来源: urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）
  - [issuer_operating_disclosure/one_step] Atlas rose to 70% of total revenue from 63% two years earlier, evidencing sustained consumption growth.（Claim: claim_ev_atlas_mix；来源: urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）
  - [issuer_counterevidence/contrary] The issuer reports slower-than-historical growth of existing Atlas applications.（Claim: claim_ev_atlas_macro_slowdown；来源: urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）

### Enterprise estate and large-cohort expansion

- 结论：Growth in Direct Sales Customers and in the at-least-$100,000 ARR cohort supports term-license and support revenue, whose growth is far slower than Atlas.
- 因果链：Direct sales expands the enterprise customer count → Large customers standardize additional workloads → Term licences and support renew and expand → Other subscription revenue grows modestly
- Base终年增量：61.44；正向增量占比：6.2%
- 归因分部：Other subscription (Enterprise Advanced and related)=100.0%
- 模型参数：other_subscription_growth_2026_base, other_subscription_growth_2027_base, other_subscription_growth_2028_base
- 持续性：uncertain；Customer counts grew each year, but the disclosed category grew only 3.2% in FY2025 as customers migrated workloads to Atlas, so expansion is modelled as low growth.
- 领先指标：Disclosed Direct Sales Customer count；Customers with at least $100,000 ARR
- 可证伪条件：Other subscription revenue declining in the base case；Direct Sales Customer count contracting
- 反证检索：searched_none_found；The filing discloses customer-count expansion and single-digit category growth; no contrary evidence on the enterprise base was found within the opened filing.
- 证据状态：limited
- 支撑证据：
  - [issuer_operating_disclosure/one_step] Direct Sales Customers grew from over 6,400 to over 7,500 in two years.（Claim: claim_ev_direct_sales_customers；来源: urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）
  - [issuer_operating_disclosure/one_step] Customers with at least $100,000 of ARR or annualized MRR rose to 2,396.（Claim: claim_ev_large_customer_cohort；来源: urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）

### Contracted backlog and deferred-revenue conversion

- 结论：Remaining performance obligations and deferred revenue give bounded visibility into near-term recognized revenue, including services delivered alongside deployments.
- 因果链：Contracted backlog and deferred revenue are carried into the period → Obligations are satisfied as services are delivered → Previously deferred amounts are recognized as revenue → Services and support revenue is partly supported by that stock
- Base终年增量：23.00；正向增量占比：2.3%
- 归因分部：Services=100.0%
- 模型参数：services_growth_2026_base, services_growth_2027_base, services_growth_2028_base
- 持续性：uncertain；Backlog is a bounded stock that converts within roughly three years; it supports the near-term path but is not a multi-year growth mechanism.
- 领先指标：Remaining performance obligations at each period end；Deferred revenue balance
- 可证伪条件：Services revenue contracting while backlog grows；Backlog conversion slower than the disclosed twelve-month share
- 反证检索：data_gap；No independent evidence on services attach or backlog cancellation was read; the high case could therefore be exceeded or missed without a checked signal.
- 证据状态：limited
- 支撑证据：
  - [issuer_contract_disclosure/direct] 748.0 USD million of remaining performance obligations existed at FY2025 year end, 59% due within twelve months.（Claim: claim_ev_rpo_stock；来源: urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）
  - [issuer_contract_disclosure/one_step] 18% of FY2025 revenue came from deferred revenue outstanding at the start of the period.（Claim: claim_ev_deferred_revenue_share；来源: urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8）

### 驱动归因对账

- 驱动归因的分部增量：987.35
- 分部增量合计：987.35
- 未归入经营驱动排名的公司级调整：0.00
- 与公司总增量差额：0.00

## 敏感性

| 参数 | 冲击类型 | 请求值(下/上) | 有效值(下/上) | 截断 | 下行终值 | 基准终值 | 上行终值 | 最大相对影响 |
|---|---|---|---|---|---:|---:|---:|---:|
| atlas_growth_2028_base | percentage_point | 0.14/0.18 | 0.14/0.18 | {'down': False, 'up': False} | 2,954.00 | 2,993.79 | 3,033.59 | 1.3% |
| other_subscription_growth_2028_base | percentage_point | 0.02/0.04 | 0.02/0.04 | {'down': False, 'up': False} | 2,987.97 | 2,993.79 | 2,999.62 | 0.2% |
| services_growth_2028_base | percentage_point | 0.09/0.11 | 0.09/0.11 | {'down': False, 'up': False} | 2,993.01 | 2,993.79 | 2,994.57 | 0.0% |

## 预测置信度

- 等级：low
- 分数：49.0/100
- 驱动证据覆盖率：100.0%

| 组成 | 得分 |
|---|---:|
| verified_claim_quality | 14.0 |
| verified_claim_coverage | 25.0 |
| source_freshness | 5.0 |
| revenue_weighted_explicit_models | 0.0 |
| historical_accuracy | 0.0 |
| revenue_weighted_sensitivity_coverage | 5.0 |

### 质量硬门

- base_reconciliation：通过
- recognition_contract：通过
- scenario_consistency：通过
- research_coverage：通过
- management_target_coverage：通过
- growth_driver_tree：通过

## 反证指标与数据缺口

### 反证指标
- 未提供。

### 数据缺口
- industry_market: No independent database-market size or growth series was read under the bounded one-source research budget.
- competition: Competitive share and pricing evidence is limited to issuer risk-factor statements; no independent share or price series was checked.
- policy: Data-privacy and AI regulation are described qualitatively; no quantified revenue exposure or dated compliance cost was disclosed.
- growth_driver:deferred_and_backlog_visibility: counterevidence search is incomplete
- management_communication:latest_annual_filing: incomplete
- management_communication:latest_results_release: incomplete
- management_communication:latest_earnings_call: incomplete
- management_communication:latest_investor_presentation: incomplete
- management_communication:latest_strategy_communication: incomplete
- management_communication:material_announcements_since_last_filing: incomplete

## 参数—证据claim映射

| 参数ID | 身份 | 数值 | 期间 | 维度 | Claim ID | 来源ID | 支持类型 | 定位 | 短摘录 |
|---|---|---:|---|---|---|---|---|---|---|
| reported_total | reported_fact | 2,006.44 | FY2025 | revenue | claim_reported_total_2025 | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | exact_value | Consolidated Statements of Operations Data - Revenue table, Total revenue row | Subscription \| $ \| 1,943,864 \| 97 \| % \| $ \| 1,627,326 \| 97 \| % \| $ \| 1,235,122 \| 96 \| % Services \| 62,579 \| 3 \| 55,685 \| 3 \| 48,918 \| 4 \| Total revenue \| 2,006,443 \| 100 \| 1,683,011 \| 100 \| 1,284,040 \| 100 |
| atlas_base | reported_fact | 1,405.18 | FY2025 | revenue | claim_atlas_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | exact_value | Note 9 Revenue - Disaggregation of Revenue, row 'MongoDB Atlas-related' | Subscription product categories and services: \| MongoDB Atlas-related \| $ \| 1,405,184 \| $ \| 1,105,351 \| $ \| 808,263 \| Other subscription \| 538,680 \| 521,975 \| 426,859 \| Services \| 62,579 \| 55,685 \| 48,918 \| Total \| $ \| 2,006,443 \| $ \| 1,683,011 \| $ \| 1,284,040 \| |
| other_subscription_base | reported_fact | 538.68 | FY2025 | revenue | claim_other_subscription_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | exact_value | Note 9 Revenue - Disaggregation of Revenue, row 'Other subscription' | Subscription product categories and services: \| MongoDB Atlas-related \| $ \| 1,405,184 \| $ \| 1,105,351 \| $ \| 808,263 \| Other subscription \| 538,680 \| 521,975 \| 426,859 \| Services \| 62,579 \| 55,685 \| 48,918 \| Total \| $ \| 2,006,443 \| $ \| 1,683,011 \| $ \| 1,284,040 \| |
| services_base | reported_fact | 62.58 | FY2025 | revenue | claim_services_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | exact_value | Note 9 Revenue - Disaggregation of Revenue, row 'Services' | Subscription product categories and services: \| MongoDB Atlas-related \| $ \| 1,405,184 \| $ \| 1,105,351 \| $ \| 808,263 \| Other subscription \| 538,680 \| 521,975 \| 426,859 \| Services \| 62,579 \| 55,685 \| 48,918 \| Total \| $ \| 2,006,443 \| $ \| 1,683,011 \| $ \| 1,284,040 \| |
| atlas_growth_2026_low | analyst_assumption | 0.12 | FY2026 | ratio | claim_atlas_growth_2026_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related low 2026 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2026_low | analyst_assumption | 0.12 | FY2026 | ratio | claim_atlas_growth_2026_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| atlas_growth_2027_low | analyst_assumption | 0.09 | FY2027 | ratio | claim_atlas_growth_2027_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related low 2027 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2027_low | analyst_assumption | 0.09 | FY2027 | ratio | claim_atlas_growth_2027_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| atlas_growth_2028_low | analyst_assumption | 0.07 | FY2028 | ratio | claim_atlas_growth_2028_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related low 2028 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2028_low | analyst_assumption | 0.07 | FY2028 | ratio | claim_atlas_growth_2028_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| atlas_growth_2026_base | analyst_assumption | 0.20 | FY2026 | ratio | claim_atlas_growth_2026_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related base 2026 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2026_base | analyst_assumption | 0.20 | FY2026 | ratio | claim_atlas_growth_2026_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related base 2026 growth assumption | We had over 53,100 MongoDB Atlas customers as of January 31, 2025. |
| atlas_growth_2027_base | analyst_assumption | 0.18 | FY2027 | ratio | claim_atlas_growth_2027_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related base 2027 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2027_base | analyst_assumption | 0.18 | FY2027 | ratio | claim_atlas_growth_2027_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related base 2027 growth assumption | We had over 53,100 MongoDB Atlas customers as of January 31, 2025. |
| atlas_growth_2028_base | analyst_assumption | 0.16 | FY2028 | ratio | claim_atlas_growth_2028_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related base 2028 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2028_base | analyst_assumption | 0.16 | FY2028 | ratio | claim_atlas_growth_2028_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related base 2028 growth assumption | We had over 53,100 MongoDB Atlas customers as of January 31, 2025. |
| atlas_growth_2026_high | analyst_assumption | 0.27 | FY2026 | ratio | claim_atlas_growth_2026_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related high 2026 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2026_high | analyst_assumption | 0.27 | FY2026 | ratio | claim_atlas_growth_2026_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related high 2026 growth assumption | We had over 53,100 MongoDB Atlas customers as of January 31, 2025. |
| atlas_growth_2027_high | analyst_assumption | 0.24 | FY2027 | ratio | claim_atlas_growth_2027_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related high 2027 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2027_high | analyst_assumption | 0.24 | FY2027 | ratio | claim_atlas_growth_2027_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related high 2027 growth assumption | We had over 53,100 MongoDB Atlas customers as of January 31, 2025. |
| atlas_growth_2028_high | analyst_assumption | 0.21 | FY2028 | ratio | claim_atlas_growth_2028_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related high 2028 growth assumption | During the year ended January 31, 2025, MongoDB Atlas revenue represented 70% of our total revenue, as compared to 66% in the prior year, reflecting the continued growth of MongoDB Atlas since its introduction in June 2016. |
| atlas_growth_2028_high | analyst_assumption | 0.21 | FY2028 | ratio | claim_atlas_growth_2028_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the MongoDB Atlas-related high 2028 growth assumption | We had over 53,100 MongoDB Atlas customers as of January 31, 2025. |
| other_subscription_growth_2026_low | analyst_assumption | 0.00 | FY2026 | ratio | claim_other_subscription_growth_2026_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) low 2026 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2026_low | analyst_assumption | 0.00 | FY2026 | ratio | claim_other_subscription_growth_2026_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| other_subscription_growth_2027_low | analyst_assumption | -0.02 | FY2027 | ratio | claim_other_subscription_growth_2027_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) low 2027 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2027_low | analyst_assumption | -0.02 | FY2027 | ratio | claim_other_subscription_growth_2027_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| other_subscription_growth_2028_low | analyst_assumption | -0.03 | FY2028 | ratio | claim_other_subscription_growth_2028_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) low 2028 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2028_low | analyst_assumption | -0.03 | FY2028 | ratio | claim_other_subscription_growth_2028_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| other_subscription_growth_2026_base | analyst_assumption | 0.04 | FY2026 | ratio | claim_other_subscription_growth_2026_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) base 2026 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2026_base | analyst_assumption | 0.04 | FY2026 | ratio | claim_other_subscription_growth_2026_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) base 2026 growth assumption | The number of customers with $100,000 or greater in ARR and annualized MRR was 2,396, 2,052 and 1,651 as of January 31, 2025, 2024 and 2023, respectively. |
| other_subscription_growth_2027_base | analyst_assumption | 0.04 | FY2027 | ratio | claim_other_subscription_growth_2027_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) base 2027 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2027_base | analyst_assumption | 0.04 | FY2027 | ratio | claim_other_subscription_growth_2027_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) base 2027 growth assumption | The number of customers with $100,000 or greater in ARR and annualized MRR was 2,396, 2,052 and 1,651 as of January 31, 2025, 2024 and 2023, respectively. |
| other_subscription_growth_2028_base | analyst_assumption | 0.03 | FY2028 | ratio | claim_other_subscription_growth_2028_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) base 2028 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2028_base | analyst_assumption | 0.03 | FY2028 | ratio | claim_other_subscription_growth_2028_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) base 2028 growth assumption | The number of customers with $100,000 or greater in ARR and annualized MRR was 2,396, 2,052 and 1,651 as of January 31, 2025, 2024 and 2023, respectively. |
| other_subscription_growth_2026_high | analyst_assumption | 0.09 | FY2026 | ratio | claim_other_subscription_growth_2026_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) high 2026 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2026_high | analyst_assumption | 0.09 | FY2026 | ratio | claim_other_subscription_growth_2026_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) high 2026 growth assumption | The number of customers with $100,000 or greater in ARR and annualized MRR was 2,396, 2,052 and 1,651 as of January 31, 2025, 2024 and 2023, respectively. |
| other_subscription_growth_2027_high | analyst_assumption | 0.08 | FY2027 | ratio | claim_other_subscription_growth_2027_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) high 2027 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2027_high | analyst_assumption | 0.08 | FY2027 | ratio | claim_other_subscription_growth_2027_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) high 2027 growth assumption | The number of customers with $100,000 or greater in ARR and annualized MRR was 2,396, 2,052 and 1,651 as of January 31, 2025, 2024 and 2023, respectively. |
| other_subscription_growth_2028_high | analyst_assumption | 0.07 | FY2028 | ratio | claim_other_subscription_growth_2028_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) high 2028 growth assumption | Total revenue growth reflects increased demand for our platform and related services. Subscription revenue increased by $316.5 million primarily due to an increase of $269.4 million from our Direct Sales Customers, inclusive of the impact from Direct Sales Customers who were self-serve customers of MongoDB Atlas in the prior-year period. |
| other_subscription_growth_2028_high | analyst_assumption | 0.07 | FY2028 | ratio | claim_other_subscription_growth_2028_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Other subscription (Enterprise Advanced and related) high 2028 growth assumption | The number of customers with $100,000 or greater in ARR and annualized MRR was 2,396, 2,052 and 1,651 as of January 31, 2025, 2024 and 2023, respectively. |
| services_growth_2026_low | analyst_assumption | 0.08 | FY2026 | ratio | claim_services_growth_2026_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services low 2026 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2026_low | analyst_assumption | 0.08 | FY2026 | ratio | claim_services_growth_2026_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| services_growth_2027_low | analyst_assumption | 0.07 | FY2027 | ratio | claim_services_growth_2027_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services low 2027 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2027_low | analyst_assumption | 0.07 | FY2027 | ratio | claim_services_growth_2027_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| services_growth_2028_low | analyst_assumption | 0.06 | FY2028 | ratio | claim_services_growth_2028_low | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services low 2028 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2028_low | analyst_assumption | 0.06 | FY2028 | ratio | claim_services_growth_2028_low_headwind | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Item 7 MD&A - macro headwind disclosure on existing Atlas application growth | During the year ended January 31, 2025, the macroeconomic environment negatively impacted our business. For instance, we experienced slower than historical growth rates for our existing MongoDB Atlas applications. |
| services_growth_2026_base | analyst_assumption | 0.12 | FY2026 | ratio | claim_services_growth_2026_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services base 2026 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2026_base | analyst_assumption | 0.12 | FY2026 | ratio | claim_services_growth_2026_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services base 2026 growth assumption | As of January 31, 2025, we had over 7,500 customers that were sold through our direct sales force and channel partners, as compared to over 7,000 and over 6,400 such customers as of January 31, 2024 and 2023, respectively. |
| services_growth_2027_base | analyst_assumption | 0.11 | FY2027 | ratio | claim_services_growth_2027_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services base 2027 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2027_base | analyst_assumption | 0.11 | FY2027 | ratio | claim_services_growth_2027_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services base 2027 growth assumption | As of January 31, 2025, we had over 7,500 customers that were sold through our direct sales force and channel partners, as compared to over 7,000 and over 6,400 such customers as of January 31, 2024 and 2023, respectively. |
| services_growth_2028_base | analyst_assumption | 0.10 | FY2028 | ratio | claim_services_growth_2028_base | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services base 2028 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2028_base | analyst_assumption | 0.10 | FY2028 | ratio | claim_services_growth_2028_base_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services base 2028 growth assumption | As of January 31, 2025, we had over 7,500 customers that were sold through our direct sales force and channel partners, as compared to over 7,000 and over 6,400 such customers as of January 31, 2024 and 2023, respectively. |
| services_growth_2026_high | analyst_assumption | 0.15 | FY2026 | ratio | claim_services_growth_2026_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services high 2026 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2026_high | analyst_assumption | 0.15 | FY2026 | ratio | claim_services_growth_2026_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services high 2026 growth assumption | As of January 31, 2025, we had over 7,500 customers that were sold through our direct sales force and channel partners, as compared to over 7,000 and over 6,400 such customers as of January 31, 2024 and 2023, respectively. |
| services_growth_2027_high | analyst_assumption | 0.14 | FY2027 | ratio | claim_services_growth_2027_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services high 2027 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2027_high | analyst_assumption | 0.14 | FY2027 | ratio | claim_services_growth_2027_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services high 2027 growth assumption | As of January 31, 2025, we had over 7,500 customers that were sold through our direct sales force and channel partners, as compared to over 7,000 and over 6,400 such customers as of January 31, 2024 and 2023, respectively. |
| services_growth_2028_high | analyst_assumption | 0.13 | FY2028 | ratio | claim_services_growth_2028_high | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services high 2028 growth assumption | As of January 31, 2025, the aggregate transaction price allocated to remaining performance obligations was $748.0 million. Approximately 59% is expected to be recognized as revenue over the next 12 months 37% in 13 to 36 months and the remainder thereafter. |
| services_growth_2028_high | analyst_assumption | 0.13 | FY2028 | ratio | claim_services_growth_2028_high_peer | urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8 | rationale_support | Segment context for the Services high 2028 growth assumption | As of January 31, 2025, we had over 7,500 customers that were sold through our direct sales force and channel partners, as compared to over 7,000 and over 6,400 such customers as of January 31, 2024 and 2023, respectively. |

## 参数来源

| ID | 等级 | 类型 | 发布方 | 日期 | 定位 | 标题 |
|---|---:|---|---|---|---|---|
| [urn:company-wiki:source:sha256:b37880685db65034ed1dd023d943352399c4c88179df2b52a9572bff687b88b8](https://www.sec.gov/Archives/edgar/data/1441816/000144181625000057/mdb-20250131.htm) | 1 | regulatory_filing | company-wiki | 2025-03-21 | 1 | mdb-20250131 |
