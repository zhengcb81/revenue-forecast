本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-12-B · 建立无未来信息的样本与实际值

Parent：I-12；状态：planned；Owner：数据整理执行者；独立证据reviewer验收；依赖：I-12-A。

前提：

- 冻结设计可读；仅按已批准数据来源获取方式执行。

动作：

1. 按entity/segment/origin/horizon生成唯一sample_id，记录筛选与排除全量表。
2. 每个输入保留source版本/hash/available_at，逐条验证available_at<=origin；有疑义隔离，不能事后补当时不可得数据。
3. 真实vintage保留原预测；重建实验单独标reconstructed并记录全部假设，不可合并进真实vintage成绩。
4. 按冻结实际值政策处理重述、并购和分部重组；训练、调参、最终测试分组和时间切分必须可审计。

停止：

- future leakage、重复sample或缺origin→STOP_DATASET。
- 分层样本不足→记录limited，不补选表现更好的公司。

验收：独立reviewer可从每个样本追到信息时点与实际值；缺失/排除计数守恒。

证据：`evidence/I-12-B/sample_manifest.jsonl`、`evidence/I-12-B/exclusions.jsonl`、`evidence/I-12-B/source_vintages.jsonl`、`evidence/I-12-B/actuals_policy_application.json`、`evidence/I-12-B/split_manifest.json`。
