本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-11-C · 独立反方审查与触发更新

Parent：I-11；状态：planned；Owner：未参与参数设定的独立研究reviewer；依赖：I-11-B。

前提：

- 冻结参数版本，reviewer先读原始证据再读结论。

动作：

1. 逐命题提出一个可证伪替代解释，并搜集已有证据中的反例，不允许只复述结论。
2. 填写falsifier的观测量、阈值、日期、来源路线和恢复规则；阈值必须专业审定。
3. 分别检查事实错、机制错、幅度错、时点错四种失败；在收益预测中逐项标风险，而非统一降低一个信心分。
4. 变更触发时创建新版本与delta，不覆盖旧快照；保留旧预测供I-12评分。

停止：

- 无独立reviewer或反证只有空泛风险词→STOP_REVIEW。
- 触发更新会改写旧预测而非新增版本→STOP_LINEAGE。

验收：每个量化命题都有可执行触发器、反方判断和保留历史的更新规则。

证据：`evidence/I-11-C/challenge_review.md`、`evidence/I-11-C/falsifiers.json`、`evidence/I-11-C/change_policy.json`、`evidence/I-11-C/qualitative_decision.json`。
