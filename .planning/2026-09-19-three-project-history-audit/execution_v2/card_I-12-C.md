本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-12-C · 冻结预测与基线后解封实际值

Parent：I-12；状态：planned；Owner：执行者按设计运行；独立reviewer保管实际值；依赖：I-12-B。

前提：

- 样本和设计已冻结，对应模型至少公式资格通过，所用真实映射有披露资格。

动作：

1. 同一sample只使用origin以前资料构造驱动；保存模型、配置、参数、source manifest hash及运行日志。
2. 按冻结规则产生各baseline；baseline缺必需历史期就标not_applicable，不用未来资料补齐。
3. 在读取实际值前冻结forecast、low/base/high语义、预测时间、版本和hash；重跑必须有原因且保留旧版本。
4. 解封实际值后只做评分，不再调参；需调参进入新训练轮并使用未见过的测试集。

停止：

- 预测冻结晚于读取实际值→该样本只能exploratory。
- 模型披露映射未通过→STOP_MODEL_ADAPTATION；不阻止其他已合格模型继续。

验收：每个可评分样本有冻结预测和公平基线；没有真实历史vintage的样本清晰分组。

证据：`evidence/I-12-C/forecast_vintages.jsonl`、`evidence/I-12-C/baseline_vintages.jsonl`、`evidence/I-12-C/forecast_manifest.json`、`evidence/I-12-C/run_logs.json`、`evidence/I-12-C/unblind_receipt.json`。
