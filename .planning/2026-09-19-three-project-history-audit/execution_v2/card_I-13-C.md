本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-13-C · 冻结交付资格与接续清单

Parent：I-13；状态：planned；Owner：主审和独立买方reviewer；依赖：I-13-B。

前提：

- 全部阻断项已逐项判定；资格状态不相互替代。

动作：

1. 按评分规则确定blocked/research_draft_needs_review/buy_side_review_ready。
2. 逐模型列公式、披露、准确性三栏；准确性未证实也必须明写，禁止改成已验证预测。
3. 保留source及模型hash、as_of、当前限制、触发更新条件、下次需执行卡和owner。
4. 仅在上游真实发布/回执流程合格时走其既定发布卡；本卡只审阅资格，不自行补写host_receipt或改索引。

停止：

- 任何未解决blocking issue或缺独立签名→不得正式标ready。
- 无真实运行/消费/发布证据却只凭receipt文件存在→STOP_PROVENANCE。

验收：明确区分研究可审阅、部署可用、预测准确性；保留所有未证实事项。

证据：`evidence/I-13-C/delivery_qualification.json`、`evidence/I-13-C/open_items.json`、`evidence/I-13-C/handoff_manifest.json`、`evidence/I-13-C/independent_buy_side_signoff.md`。
