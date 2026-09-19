本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-12-A · 专业冻结评估设计

Parent：I-12；状态：planned；Owner：统计reviewer和行业reviewer共同签字；依赖：I-07-E。

前提：

- 上游证据资格/版本边界可用；无需等待完整I-07或I-10准确性结果。

动作：

1. 逐项填写evaluation_design_fields，未定项标PENDING，不由弱模型选择方便通过的阈值。
2. 选择primary endpoint、baseline、权重、样本最小数量/功效、成对比较、cluster/block方法、CI和多重比较校正。
3. 严格区分真实历史vintage与重建实验；低/高情景没有概率标签就只评情景包含率。
4. 将设计、reviewer身份、签署、版本和SHA256冻结；测试集结果在此之前保持封存。

停止：

- 任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION。
- 已看测试结果后变更设计→新探索版本，旧结果不得追认确认性成功。

验收：evaluation_design_fields全部完成或有获批not_applicable；SHA256冻结在结果解封前。

证据：`evidence/I-12-A/evaluation_design.json`、`evidence/I-12-A/professional_approval.json`、`evidence/I-12-A/design_manifest.json`。
