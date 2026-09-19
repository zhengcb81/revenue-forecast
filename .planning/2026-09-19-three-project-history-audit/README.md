# 三项目历史审查与后续实施入口

审查日期：2026-09-19。root 与三名独立代理分区审查，再交叉复核。此次完成的是历史审查和新实施计划；**产品修复尚未执行**。

先读[审查结论](audit_report.md)，再看[详细实施计划](implementation_plan.md)。本轮工作状态见[task_plan](task_plan.md)、[发现记录](findings.md)、[实施与验证记录](progress.md)。

用户后续要求提高较弱模型可执行性，新增[执行包v2入口](execution_v2/README.md)：逐卡依赖、固定样本/预期、31模型卡、专业设计门、独立验收和接续规则。所有产品卡仍待实施；原v1终审不自动覆盖新增文档，v2复核单独记录。

## 覆盖范围

初选769个工程历史/上下文路径。最终766份Markdown全文完成阅读与语义判定（含完整版本映射）；2份是同一污染清单的主本/旧副本，只审工程结构、计数和来源链，业务投资事实明确排除；1份误命中的raw新闻排除。另252份公司/行业业务生成页面在初筛已明确排除。全部历史planning正文、子计划、执行卡、验收报告及已通过项纳入，不以原PASS作为本轮通过依据。

| 原项目/保存位置 | 全文审查路径 | 其它处置 |
|---|---:|---|
| revenue主线 | 397 | 313由revenue代理；6早期+26八月九日+24实跑由root；28八月十三日由另一代理 |
| revenue内嵌历史副本 | 113 | 另1份混合业务污染清单仅工程审查；相同文本与全部差异分别映射 |
| filing-fetch | 11 | 含全部历史正文及关联审查上下文 |
| company-wiki | 245 | 另1份混合清单工程审查、1份raw新闻排除 |
| **合计** | **766** | **3个路径另有明确处置，无未审工程历史正文** |

[逐文件覆盖CSV](master_coverage.csv)及[带证据链接的JSON](master_coverage.json)记录原路径、初始hash、审查hash、阅读方式和审查账本；[旧副本差异审查](snapshot_review.json)保留114副本对应关系。文件数不等于独立问题数、测试数或产品通过数。部分运行历史无法重新建立当时环境，结论是historical_only或insufficient_evidence，没有强行重签。

## 逐条审查导航

| 分区 | 主要阅读入口 | 原文与判定 |
|---|---|---|
| Revenue原义务、勾选、模型与全部自有正文 | [分区报告](reviews/revenue/review.md) | [313份正文发生记录](reviews/revenue/source_semantic_ledger.jsonl)、[262原单元](reviews/revenue/item_ledger.csv)、[776勾选](reviews/revenue/checklist_ledger.jsonl)、[31模型](reviews/revenue/model_ledger.jsonl) |
| Filing复用/下载/错误/安装/证据 | [分区报告](reviews/filing/review.md) | [逐条CSV](reviews/filing/item_ledger.csv)、[收据字段](reviews/filing/receipt_ledger.jsonl) |
| Wiki v5/旧worker/工程上下文 | [分区报告](reviews/wiki/review.md) | [1,263条CSV](reviews/wiki/item_ledger.csv)、[完整阅读范围](reviews/wiki/read_coverage.json) |
| Wiki根历史/CW/WR/早期专项 | [分区报告](reviews/wiki_legacy/review.md) | [原文逐块账本](reviews/wiki_legacy/item_ledger.jsonl)、[补充证据](reviews/wiki_legacy/supplemental_item_ledger.jsonl) |
| 8/13 CA/ZR原计划及强要求 | [独立分区报告](reviews/aug13_independent/review.md) | [97人工判断](reviews/aug13_independent/manual_cases.json)、[原文账本](reviews/aug13_independent/item_ledger.jsonl) |
| 8/9 WU/FCAP原计划 | [68人工判断](reviews/aug09_plans/manual_cases.json) | [全部原文](reviews/aug09_plans/item_ledger.jsonl) |
| 早期Revenue及原审计正文 | [49人工判断](reviews/early_revenue/manual_cases.json) | [全部原文](reviews/early_revenue/item_ledger.jsonl) |
| 跨项目痛点与规划同步 | [60人工判断](reviews/cross_history/manual_cases.json) | [全部原文](reviews/cross_history/item_ledger.jsonl)、[当前隔离反例](reviews/cross_history/current_recheck.json) |
| Wiki早期归档 | [30人工判断](reviews/wiki_archive/manual_cases.json) | [全部原文](reviews/wiki_archive/item_ledger.jsonl) |
| 8/12及9/18真实公司运行 | [58人工判断](reviews/company_cases/manual_cases.json) | [全部原文](reviews/company_cases/item_ledger.jsonl)、[独立算术/hash](reviews/company_cases/independent_checks.json) |
| 最早三市场计划及架构减法诊断 | [5人工判断](reviews/final_context/manual_cases.json) | [全部原文](reviews/final_context/item_ledger.jsonl) |

同一段话可能同时对应原工作单元、文档区间和当前反例，所以这些计数不能相加当缺陷总数。查某条旧PASS时，先按覆盖表定位文件，再在相应账本按原路径/行号/原文查判断；同一版本的多次提及均保留。

## 判定含义

| 判定 | 含义 |
|---|---|
| supported_scoped | 支持明确限定的命题，可能只是规范合理、算术正确、局部实现或历史证据；不是全产品通过 |
| contradicted | 有具体反例或文本/证据矛盾；需看对象是规划、历史声明还是当前代码 |
| insufficient_evidence | 无法证明声明的强范围；不自动等于产品一定错误 |
| not_deployed | 实现/规划尚未进入实际部署或消费者；大量v5条目原本就是未来计划 |
| superseded | 后继取代或已退役；保留原义务追溯，不重新启动旧方案 |
| historical_only | 保留当时事实/状态，不重建或认证旧运行环境 |
| not_applicable | 有明确不适用范围，不作为通过样本 |

## 独立性、验证与现场边界

[主审交叉复核](reviews/second_wave/root_cross_review.md)、[31模型及关键反例第二复核](reviews/second_wave/filing_cross_review.md)、[root 175个case第二复核](reviews/wiki/cross_review.md)保存更正及未外推边界。已有修复被保留，普通文件host_signed、整组发布事务、deadline、refcount、验收器等当前反例另列。

[最终报告与实施计划独立终审](reviews/second_wave/final_review.md)和[收入分区的计划终审](reviews/revenue/final_plan_review.md)保存最终审阅结论。[交付完整性核对](delivery_validation.json)及[独立计数/hash核对](reviews/second_wave/final_review_checks.json)绑定收尾后的文档；这些检查不代表产品修复已经通过。

[现场完整性](evidence/final_integrity.json)核对旧基线357产品文件，其中356相同；normalizer的并行提交差异已单列[版本证据](evidence/concurrent_normalizer_verified.json)。本审计没有创作该产品修改。3个生产配置/策略/worker控制文件字节不变。不能由此宣称整个动态工作区或数据库始终不变。

关联机器材料另有[清单](inventory/associated_evidence.json)，按支持具体声明的需要读取、重算或重放；清单1335项不等于1335项全部独立运行验证。没有重新下载年报、启动worker、生产清理、替换旧收据或发布正式投资预测。
