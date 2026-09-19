本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-00-B — 绑定当前源码、样本和命令
Parent：I-00。依赖：I-00-A。Owner：集成负责人和各卡owner。资格：每卡开工前提。

锚点：RF/scripts/source_preparation.py；RF/scripts/revenue_forecast.py；各分区卡声明的现行函数；旧真实命令位于RF/audit_review/2026-09-18_real_company_skill_audit/runs/*/run.json。允许写：binding/commands与隔离测试；不修改旧run.json。

1. 用CodeGraph定位卡片函数和调用方，读当前源、参数解析与测试；保存符号位置和sha。旧行号不一致只说明需更新绑定，不能按旧行硬改。
2. 读取[样本清单](sample_manifest.json)和[固定矩阵](scenario_matrix.md)，重算所需原件hash；样本不符先blocked，不按公司名找一个相似年报替换。
3. 从旧命令获取已证实参数，但不直接重放其中--allow-download或生产cwd；把cwd/config/output/db依赖绑定到隔离目录。入口没有隔离能力时先提出最小依赖注入修复卡，不能猜一个不存在的--config参数。
4. 两阶段绑定：实现前冻结基线命令、隔离环境、允许改路径及专业决定；新接口/测试明确planned、不执行，但不阻断获准编辑。实现后读新源码和参数，再编写commands.json每条真实argv、cwd、超时、expected rc、业务结果、写目录和网络目标；所有null/unbound填完并由reviewer核查后才运行该命令。
5. 测试命令使用当前源码中真实存在的test文件/nodeid；先只收集需要的测试，记录确切收集数；若导入副作用不能隔离则停止，不把collect失败当“无测试”。
6. 将入口、依赖、样本和命令一起绑定到具体卡attempt；后续卡可复用未变部分，但变动必重核。

验收：故意配置生产DB或不存在参数，绑定必须不准执行；合格的纯读取命令能够找到精确模块。这里只验命令可定位，不认证产品行为。停止：路径或权限不明确。交付binding.json、commands.json与source anchors。
