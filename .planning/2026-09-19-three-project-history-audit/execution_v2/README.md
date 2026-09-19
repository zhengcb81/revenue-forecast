# 细化后的实施入口

先读[START_HERE](START_HERE.md)，再由[调度表](dispatch.md)领取一张卡。不要把[原总纲](../implementation_plan.md)当成可一次交给弱模型的大任务。

18项原义务已拆为86张卡，其中31张逐模型卡；调度表链接到独立单卡文件，不必整本阅读。[修订和验证记录](revision_review.md)及[有界独立干读](independent_dry_read.md)说明实际检查范围与未取得资格。

| 需要做什么 | 文档 |
|---|---|
| 明确开工前提、步骤、专业判断和停止点 | [执行协议](START_HERE.md) |
| 查原I-00…17对应哪些子卡及依赖 | [调度表](dispatch.md) / [结构化索引](dispatch.json) |
| 基线、验收器、真实旅程、测量、部署 | [集成执行卡](root_cards.md) |
| 配置、扫描/注册、工件、审核、维护 | [Wiki执行卡](wiki_cards.md) |
| 最新性、deadline/并发、签名、发布事务 | [Filing及发布执行卡](filing_cards.md) |
| 每一种收入模型的单位、手算和拒绝条件 | [31模型卡](model_cards.md) |
| 定性进入参数、准确性评估和买方交付 | [研究执行卡](research_cards.md) |
| 固定三市场案例，不随失败换样本 | [场景矩阵](scenario_matrix.md) / [原件定位与hash](sample_manifest.json) |
| 审核结果、失败接续、上下文交接 | [独立验收与接续](review_and_handoff.md) |
| 证明较弱模型能否正确实施 | [待执行的隔离试点](pilot.md) |

JSON用于依赖/覆盖核对；卡片Markdown和原总纲共同定义义务。若两者冲突，停止受影响卡并更正索引，不能选更容易通过的一份。执行时只带指定卡和必需前置上下文，避免把整套文档塞进弱模型上下文。

本次文档干读与结构检查不等于产品通过。所有产品卡仍planned；真实live未绑定样本保持未就绪。部署、统计设计、会计口径、并发与事务等专业决策在明确冻结前，不能由弱模型自行猜测。
