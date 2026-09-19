本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-13-A · 买方交付逐项评分

Parent：I-13；状态：planned；Owner：独立买方reviewer，不参与该预测设定；依赖：I-07-E、I-11-C。

前提：

- 预测包及证据可读；可以没有I-12准确性优势，但必须诚实标未证实。

动作：

1. 按buy_side_dimensions逐维打0/1/2并引用产物页/字段；缺失不靠总分补偿。
2. 先核hard_blocks，再看评分；每个blocking issue写可复现样例、影响收入/场景/决策和所需修正。
3. 全2才给buy_side_review_ready；任何0为blocked，只有1没有0则research_draft_needs_review。总分仅展示，不作自动放行阈值。

停止：

- 任一hard_block成立→blocked，禁止以总分或文字解释豁免。
- 未证明准确性只能写unproven，不因这一事实自动否定可审阅的研究草案。

验收：每个分值可由明确证据复核；不把分值或ready标签解释为投资建议正确率。

证据：`evidence/I-13-A/buy_side_scorecard.json`、`evidence/I-13-A/blocking_issues.json`、`evidence/I-13-A/artifact_references.json`。
