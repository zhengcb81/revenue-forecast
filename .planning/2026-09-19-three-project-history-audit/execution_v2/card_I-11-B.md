本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-11-B · 校准参数幅度和联合情景

Parent：I-11；状态：planned；Owner：行业/会计reviewer决策，弱模型执行已签规则；依赖：I-11-A、I-10-A。

前提：

- I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。

动作：

1. 按contract arithmetic、历史经验或外部可比选择校准方法，保存选择依据与样本；缺数据就标expert_assumption。
2. 明确low/base/high值、单位、起止年份、原值→新值、转换公式；管理层目标不得用作独立准确性证据。
3. 用dependency_control列共享驱动及约束，检查同一事件是否同时在销量、价格、额外收入重复出现。
4. 按qualitative_synthetic_example手算复核实施机制，再执行真实已审定映射；不复制示例数字到真实公司。

停止：

- 幅度无来源又未明确分析师假设→STOP_CALIBRATION。
- 独立调高多个有关联driver导致不可能的联合情景→STOP_SCENARIO。

验收：参数幅度、相关性及收入增量能够复核；专业reviewer签署后方可进入forecast，不等同准确性通过。

证据：`evidence/I-11-B/parameter_changes.json`、`evidence/I-11-B/calibration_samples.json`、`evidence/I-11-B/joint_scenarios.json`、`evidence/I-11-B/hand_oracle.json`、`evidence/I-11-B/professional_decision.md`。
