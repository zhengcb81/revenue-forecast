# 紫金矿业未来五年营收预测（隔离 draft 摘要）

> 这不是 formal publication。严格 schema 3.7 输入、完整计算和强输出校验已经通过，
> 但标准 source-preparation 被共享 catalog 的 `not_reviewed` 安全状态拦截；官方 Markdown renderer
> 又无法接受合法 draft receipt。本摘要只从未修改的强校验 `draft_result.json` 读取数值。

- 信息截止日：2026-08-12
- 基期：FY2025，营收 349.079 十亿元
- 模型：四个外部收入报告分部，全部使用 `direct_growth` fallback
- 输入 SHA-256：`5a6a8b3a3ee3172dd6af027c78b65f85601c56f46eb29d9d9e1ab3c9051c1067`
- 结果 SHA-256：`a8e64f78a174a36f21f1becdee3ba3b51005e02e064bd02a2e1949433ca3f8ca`
- publication registry：未写入

## 核心结论

| 情景 | FY2030 营收（十亿元） | FY2025→FY2030 CAGR | 五年营收增量（十亿元） |
|---|---:|---:|---:|
| low | 369.794 | 1.16% | 20.714 |
| base | 516.409 | 8.15% | 167.330 |
| high | 627.829 | 12.46% | 278.750 |

概率加权（20%/60%/20%）FY2030 营收为 **509.370 十亿元**，
隐含 CAGR 为 **7.85%**。该概率是分析师校准，不是公司指引。

## 年度三情景路径

| 年度 | Low营收 | Base营收 | High营收 | Base同比 |
|---:|---:|---:|---:|---:|
| 2026 | 354.225 | 404.230 | 440.151 | 15.80% |
| 2027 | 364.343 | 443.569 | 503.622 | 9.73% |
| 2028 | 376.849 | 481.688 | 564.368 | 8.59% |
| 2029 | 369.794 | 499.703 | 599.061 | 3.74% |
| 2030 | 369.794 | 516.409 | 627.829 | 3.34% |

单位：人民币十亿元。

## Base 分部路径

| 外部收入分部 | FY2025A | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---:|---:|---:|---:|---:|---:|
| 矿产品 | 109.978 | 142.971 | 168.706 | 194.011 | 203.712 | 211.860 |
| 冶炼产品 | 165.859 | 182.445 | 191.567 | 201.145 | 207.179 | 213.395 |
| 贸易 | 29.213 | 30.381 | 30.989 | 31.609 | 32.241 | 32.885 |
| 其他 | 44.030 | 48.433 | 52.308 | 54.923 | 56.571 | 58.268 |

## 主要增长驱动

1. **Mine output ramp, commodity prices and asset mix**：FY2030 Base 增量 101.883 十亿元，占正向驱动 60.89%；证据状态 `triangulated`。
2. **Smelting throughput, feed availability and metal prices**：FY2030 Base 增量 47.536 十亿元，占正向驱动 28.41%；证据状态 `limited`。
3. **Other-business delivery and normalization**：FY2030 Base 增量 14.238 十亿元，占正向驱动 8.51%；证据状态 `limited`。
4. **Trading turnover and principal-agent presentation mix**：FY2030 Base 增量 3.673 十亿元，占正向驱动 2.19%；证据状态 `limited`。

矿产品是最大增量来源，但模型没有把每座矿拆成销量×价格×权益×并表×内部抵销。
因此驱动排名是报告分部归因，不是逐矿收入预测。

## FY2026 增长率敏感性对 FY2030 Base 的影响

| 分部参数 | 冲击 | 下行终值 | 基准终值 | 上行终值 | 最大相对影响 |
|---|---:|---:|---:|---:|---:|
| `mineral_growth_FY2026_base` | ±5.0pct | 508.260 | 516.409 | 524.557 | 1.58% |
| `smelting_growth_FY2026_base` | ±5.0pct | 506.709 | 516.409 | 526.109 | 1.88% |
| `trade_growth_FY2026_base` | ±3.0pct | 515.460 | 516.409 | 517.358 | 0.18% |
| `other_growth_FY2026_base` | ±5.0pct | 513.760 | 516.409 | 519.058 | 0.51% |

## 置信度

- 引擎评分：**42.0/100（low）**。
- 主要原因：显式运营模型占比为 0.0；没有不可变历史回测；十个研究维度仍为 material data gap。
- 驱动证据覆盖率：60.00%。
- 六个质量硬门（base 对账、收入确认、情景一致性、研究覆盖、管理层目标覆盖、驱动树）均通过。

## 关键数据缺口

- No source discloses FY2026-FY2030 revenue for each mine; the model stops at four external-revenue report segments.
- The complete mine-level bridge for volume, grade, recovery, price, ownership, consolidation and internal eliminations is unavailable.
- Trade revenue contains both gross principal and net agent presentation, while the current segment schema permits only one presentation label.
- The other segment mixes point-in-time product/project revenue with over-time operating services, while the current segment schema permits one timing label.
- Company production guidance principally ends at FY2028; FY2029-FY2030 base growth is an explicit source-free analyst fade.
- No frozen multi-year commodity-price, treatment-charge or foreign-exchange curve is included.
- Seven Dropbox broker PDFs have no bound normalized Markdown, summary, evidence spans or semantic tags in the catalog.
- The standard filing-fetch to revenue source-preparation path remains blocked by missing shared prompt-injection review despite exact-file reuse.
- The investor presentation and results-call transcript were not captured as stable source snapshots.
- All four segments use direct_growth fallback, so explicit operational-model revenue share is zero.
- industry_market: A frozen commodity-price and treatment-charge curve was not available in the reusable source set.
- competition: Peer supply additions and cost-curve positioning are not explicitly modeled.
- technology: Recovery, grade-control and process-technology changes are not quantified by mine.
- policy: Jurisdiction, royalty, permitting and export-policy changes are not modeled by asset.
- customers: Customer concentration and offtake contract terms are not separately disclosed for the four segments.
- demand: End-market demand is represented only indirectly through scenario growth rates.
- reserves_and_resources: Group and major-project resources are available, but complete mine-level reserves are not structured for model use.
- mine_asset_geography: Major mines, countries and 2025 production are discoverable, but not linked to a complete mine-year revenue identity.
- regulatory_permits: Permit status and renewal dates are not available as a current, source-linked asset ledger.
- broker_research: Seven Dropbox broker PDFs are indexed as physical documents but have no reusable bound artifacts.

## 来源与信任边界

- 两份年报来自 company-wiki canonical 路径，物理 hash 与 catalog 完全一致；本轮 filing-fetch 第三次调用内部返回 exact reuse、下载数为 0。
- 标准 revenue source record 因共享文档 `prompt_injection_status=not_reviewed` 被 fail-closed；本次只在隔离目录做自报式只读审阅，未回填 catalog。
- 2025 Results 和 Norton 项目新闻只有隔离 HTML 快照；没有进入 company-wiki、索引、normalize、chunk 或 tag。
- 七份 Dropbox 券商 PDF 均可读且 hash 正确，但全部没有 artifact/evidence span/tag，因此没有作为强契约模型来源。

| 来源 | 类型 | URL |
|---|---|---|
| 紫金矿业集团股份有限公司2025年年度报告 | audited_filing | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=601899&announcementId=1225023658&announcementTime=2026-03-20%2016:00 |
| 紫金矿业集团股份有限公司2024年年度报告 | audited_filing | https://www.cninfo.com.cn/new/disclosure/detail?stockCode=601899&announcementId=1222870413&announcementTime=2025-03-21%2016:00 |
| 2025 Results — Production & Guidance | company_release | https://www.zijinmining.com/investor/2025-newyeji.htm |
| Zijin’s Australia Operation Completes New Crushing System | company_release | https://www.zijinmining.com/news/news-detail-122827.htm |

## 验证说明

- `validate_document(..., Collector())`：通过。
- `run_forecast(..., mode='draft')`：连续两次通过，canonical 输出一致。
- publication registry：运行前后 hash/size 完全一致。
- formal publication：未尝试。
- 官方 `render_markdown`：失败并保留为审计发现（`ForecastInputError: publication_receipt gate_ids mismatch`）。
