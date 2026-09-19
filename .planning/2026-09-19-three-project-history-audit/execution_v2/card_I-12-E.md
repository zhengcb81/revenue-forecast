本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-12-E · 分范围判定准确性并保留失败

Parent：I-12；状态：planned；Owner：统计与行业reviewer；依赖：I-12-D。

前提：

- 冻结阈值已在结果前批准；全量结果可见。

动作：

1. 对每个预注册主要比较按冻结阈值判supported/unsupported/inconclusive，保留负skill和失败层。
2. 把结果限定到数据集、模型版本、行业、生命周期、披露质量与horizon；未覆盖分层标unproven。
3. 把公式资格、披露适配和准确性三栏合并呈现，但禁止一栏PASS覆盖另一栏不足。
4. 记录误差来源为数据/定义/驱动/时点/结构/随机，生成后续研究问题；不在本轮评分中修预测。

停止：

- 把31公式通过或少数公司拟合直接称准确率提升→STOP_CLAIM。
- 没有达到统计判定条件却宣称普遍有效→STOP_RELEASE_WORDING。

验收：结论与预先规则一致；无覆盖领域、负结果和不确定性显式保留。

证据：`evidence/I-12-E/accuracy_qualification.json`、`evidence/I-12-E/limitations.md`、`evidence/I-12-E/error_taxonomy.json`、`evidence/I-12-E/independent_statistical_review.md`。
