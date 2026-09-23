# Test Co营收预测

- 信息截止日：2026-07-12
- 财年截止日：12-31
- 币种与单位：USD million
- 基期营收：150.00
- 预测版本：2026-07-12-v1

## 核心营收结论

| 情景 | 终值营收 | CAGR | 营收增量 |
|---|---:|---:|---:|
| low | 150.00 | 0.0% | 0.00 |
| base | 181.50 | 10.0% | 31.50 |
| high | 216.00 | 20.0% | 66.00 |

## 未来收入主要驱动力

1. **Modeled revenue path for Segment A** — The registered base-case operating inputs determine Segment A revenue growth. （Base终年增量 21.00；占正向驱动 66.7%；证据 limited）
2. **Modeled revenue path for Segment B** — The registered base-case operating inputs determine Segment B revenue growth. （Base终年增量 10.50；占正向驱动 33.3%；证据 limited）

## 历史营收

| 年度 | 营收 | 来源ID |
|---:|---:|---|
| 2024 | 140.00 | filing |
| 2025 | 150.00 | filing |

## 九维研究覆盖

- 进入模型：2；数据缺口：0；当前不重要：7。
- 本表用于防止研究漏项，不直接给CAGR或置信度加分。

| 维度 | 状态 | 结论 | 营收传导 | 参数ID | 来源ID | 理由 |
|---|---|---|---|---|---|---|
| company_foundation | modeled_driver | Reported revenue perimeter and segment base are reconciled | reported total equals segment external revenue plus adjustments | reported_total, segment_a_base, segment_b_base | filing | — |
| growth_curve | modeled_driver | Direct scenario revenue paths generate the synthetic forecast | registered scenario revenue parameters aggregate by segment | 0_base_2026, 0_base_2027, 1_base_2026, 1_base_2027 | filing | — |
| industry_market | immaterial | industry_market is not material to this synthetic test horizon | no incremental revenue effect is modeled in this fixture | — | — | Synthetic contract test isolates the base and forecast calculation path |
| competition | immaterial | competition is not material to this synthetic test horizon | no incremental revenue effect is modeled in this fixture | — | — | Synthetic contract test isolates the base and forecast calculation path |
| capacity | immaterial | capacity is not material to this synthetic test horizon | no incremental revenue effect is modeled in this fixture | — | — | Synthetic contract test isolates the base and forecast calculation path |
| technology | immaterial | technology is not material to this synthetic test horizon | no incremental revenue effect is modeled in this fixture | — | — | Synthetic contract test isolates the base and forecast calculation path |
| policy | immaterial | policy is not material to this synthetic test horizon | no incremental revenue effect is modeled in this fixture | — | — | Synthetic contract test isolates the base and forecast calculation path |
| customers | immaterial | customers is not material to this synthetic test horizon | no incremental revenue effect is modeled in this fixture | — | — | Synthetic contract test isolates the base and forecast calculation path |
| demand | immaterial | demand is not material to this synthetic test horizon | no incremental revenue effect is modeled in this fixture | — | — | Synthetic contract test isolates the base and forecast calculation path |

## 管理层沟通与营收目标覆盖

- 已检查官方沟通类别：6/6；重大/相关目标：0；已进入情景：0；独立基准比较：0；未建模：0。

| 沟通类别 | 状态 | 结论 | 目标ID | 来源ID |
|---|---|---|---|---|
| latest_annual_filing | checked | Synthetic fixture review found no material forward revenue target. | — | filing |
| latest_results_release | checked | Synthetic fixture review found no material forward revenue target. | — | filing |
| latest_earnings_call | checked | Synthetic fixture review found no material forward revenue target. | — | filing |
| latest_investor_presentation | checked | Synthetic fixture review found no material forward revenue target. | — | filing |
| latest_strategy_communication | checked | Synthetic fixture review found no material forward revenue target. | — | filing |
| material_announcements_since_last_filing | checked | Synthetic fixture review found no material forward revenue target. | — | filing |

| 目标 | 强度 | 原始目标 | 来源期间 | 测量口径/模型期间 | 业务口径 | 处理 | 映射情景 | 模型兑现度 |
|---|---|---:|---|---|---|---|---|---|

## 年度情景路径

| 年度 | Low | Base | High | Base同比 |
|---:|---:|---:|---:|---:|
| 2026 | 150.00 | 165.00 | 180.00 | 10.0% |
| 2027 | 150.00 | 181.50 | 216.00 | 10.0% |

## 三情景经营驱动

| 分部 | 情景 | 驱动 | 年度 | 参数ID | 数值 |
|---|---|---|---:|---|---:|
| Segment A | low | revenue | 2026 | 0_low_2026 | 100.00 |
| Segment A | low | revenue | 2027 | 0_low_2027 | 100.00 |
| Segment A | base | revenue | 2026 | 0_base_2026 | 110.00 |
| Segment A | base | revenue | 2027 | 0_base_2027 | 121.00 |
| Segment A | high | revenue | 2026 | 0_high_2026 | 120.00 |
| Segment A | high | revenue | 2027 | 0_high_2027 | 144.00 |
| Segment B | low | revenue | 2026 | 1_low_2026 | 50.00 |
| Segment B | low | revenue | 2027 | 1_low_2027 | 50.00 |
| Segment B | base | revenue | 2026 | 1_base_2026 | 55.00 |
| Segment B | base | revenue | 2027 | 1_base_2027 | 60.50 |
| Segment B | high | revenue | 2026 | 1_high_2026 | 60.00 |
| Segment B | high | revenue | 2027 | 1_high_2027 | 72.00 |

## 分部驱动与收入确认

| 分部 | 模型 | 基期营收 | 确认时点 | 触发条件 | 列报 |
|---|---|---:|---|---|---|
| Segment A | direct_revenue | 100.00 | point_in_time | customer acceptance | gross |
| Segment B | direct_revenue | 50.00 | point_in_time | customer acceptance | gross |

## Base情景增量归因

| 项目 | 终值营收增量 |
|---|---:|
| Segment A | 21.00 |
| Segment B | 10.50 |
| 公司级调整 | 0.00 |
| 合计 | 31.50 |

## 收入增长驱动树

### Modeled revenue path for Segment A

- 结论：The registered base-case operating inputs determine Segment A revenue growth.
- 因果链：operating evidence informs the base-case inputs → registered model converts the inputs into activity → revenue-recognition rules convert activity into reported revenue
- Base终年增量：21.00；正向增量占比：66.7%
- 归因分部：Segment A=100.0%
- 模型参数：0_base_2026, 0_base_2027
- 持续性：uncertain；Synthetic fixtures do not assert a real-world structural duration.
- 领先指标：actual Segment A revenue versus the modeled annual path
- 可证伪条件：actual Segment A revenue falls below the low scenario
- 反证检索：searched_none_found；The synthetic fixture records no contrary test evidence.
- 证据状态：limited
- 支撑证据：
  - [company_execution/direct] The fixture source supports the modeled path for Segment A.（Claim: claim_growth_driver_Segment_A；来源: filing）

### Modeled revenue path for Segment B

- 结论：The registered base-case operating inputs determine Segment B revenue growth.
- 因果链：operating evidence informs the base-case inputs → registered model converts the inputs into activity → revenue-recognition rules convert activity into reported revenue
- Base终年增量：10.50；正向增量占比：33.3%
- 归因分部：Segment B=100.0%
- 模型参数：1_base_2026, 1_base_2027
- 持续性：uncertain；Synthetic fixtures do not assert a real-world structural duration.
- 领先指标：actual Segment B revenue versus the modeled annual path
- 可证伪条件：actual Segment B revenue falls below the low scenario
- 反证检索：searched_none_found；The synthetic fixture records no contrary test evidence.
- 证据状态：limited
- 支撑证据：
  - [company_execution/direct] The fixture source supports the modeled path for Segment B.（Claim: claim_growth_driver_Segment_B；来源: filing）

### 驱动归因对账

- 驱动归因的分部增量：31.50
- 分部增量合计：31.50
- 未归入经营驱动排名的公司级调整：0.00
- 与公司总增量差额：0.00

## 敏感性

未配置确定性敏感性测试。

## 预测置信度

- 等级：low
- 分数：49.0/100
- 驱动证据覆盖率：100.0%

| 组成 | 得分 |
|---|---:|
| verified_claim_quality | 14.0 |
| verified_claim_coverage | 25.0 |
| source_freshness | 10.0 |
| revenue_weighted_explicit_models | 0.0 |
| historical_accuracy | 0.0 |
| revenue_weighted_sensitivity_coverage | 0.0 |

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
- 未记录数据缺口。

## 参数—证据claim映射

| 参数ID | 身份 | 数值 | 期间 | 维度 | Claim ID | 来源ID | 支持类型 | 定位 | 短摘录 |
|---|---|---:|---|---|---|---|---|---|---|
| reported_total | reported_fact | 150.00 | FY2025 | revenue | claim_parameter_reported_total | filing | exact_value | Revenue note | Evidence supporting parameter reported_total value and definition. |
| segment_a_base | reported_fact | 100.00 | FY2025 | revenue | claim_parameter_segment_a_base | filing | exact_value | Revenue note | Evidence supporting parameter segment_a_base value and definition. |
| segment_b_base | reported_fact | 50.00 | FY2025 | revenue | claim_parameter_segment_b_base | filing | exact_value | Revenue note | Evidence supporting parameter segment_b_base value and definition. |
| a_growth_2026_base | analyst_assumption | 0.10 | FY2026 | ratio | claim_parameter_a_growth_2026_base | filing | rationale_support | Revenue note | Evidence supporting parameter a_growth_2026_base value and definition. |
| 0_low_2026 | analyst_assumption | 100.00 | FY2026 | revenue | claim_parameter_0_low_2026 | filing | rationale_support | Revenue note | Evidence supporting parameter 0_low_2026 value and definition. |
| 0_low_2027 | analyst_assumption | 100.00 | FY2027 | revenue | claim_parameter_0_low_2027 | filing | rationale_support | Revenue note | Evidence supporting parameter 0_low_2027 value and definition. |
| 0_base_2026 | analyst_assumption | 110.00 | FY2026 | revenue | claim_parameter_0_base_2026 | filing | rationale_support | Revenue note | Evidence supporting parameter 0_base_2026 value and definition. |
| 0_base_2027 | analyst_assumption | 121.00 | FY2027 | revenue | claim_parameter_0_base_2027 | filing | rationale_support | Revenue note | Evidence supporting parameter 0_base_2027 value and definition. |
| 0_high_2026 | analyst_assumption | 120.00 | FY2026 | revenue | claim_parameter_0_high_2026 | filing | rationale_support | Revenue note | Evidence supporting parameter 0_high_2026 value and definition. |
| 0_high_2027 | analyst_assumption | 144.00 | FY2027 | revenue | claim_parameter_0_high_2027 | filing | rationale_support | Revenue note | Evidence supporting parameter 0_high_2027 value and definition. |
| 1_low_2026 | analyst_assumption | 50.00 | FY2026 | revenue | claim_parameter_1_low_2026 | filing | rationale_support | Revenue note | Evidence supporting parameter 1_low_2026 value and definition. |
| 1_low_2027 | analyst_assumption | 50.00 | FY2027 | revenue | claim_parameter_1_low_2027 | filing | rationale_support | Revenue note | Evidence supporting parameter 1_low_2027 value and definition. |
| 1_base_2026 | analyst_assumption | 55.00 | FY2026 | revenue | claim_parameter_1_base_2026 | filing | rationale_support | Revenue note | Evidence supporting parameter 1_base_2026 value and definition. |
| 1_base_2027 | analyst_assumption | 60.50 | FY2027 | revenue | claim_parameter_1_base_2027 | filing | rationale_support | Revenue note | Evidence supporting parameter 1_base_2027 value and definition. |
| 1_high_2026 | analyst_assumption | 60.00 | FY2026 | revenue | claim_parameter_1_high_2026 | filing | rationale_support | Revenue note | Evidence supporting parameter 1_high_2026 value and definition. |
| 1_high_2027 | analyst_assumption | 72.00 | FY2027 | revenue | claim_parameter_1_high_2027 | filing | rationale_support | Revenue note | Evidence supporting parameter 1_high_2027 value and definition. |

## 参数来源

| ID | 等级 | 类型 | 发布方 | 日期 | 定位 | 标题 |
|---|---:|---|---|---|---|---|
| [filing](https://www.sec.gov/Archives/edgar/data/1/test.htm) | 1 | exchange_filing | Test Exchange | 2026-03-01 | Revenue note | FY2025 filing |
