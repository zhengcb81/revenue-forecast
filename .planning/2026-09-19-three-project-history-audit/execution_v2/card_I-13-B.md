本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-13-B · 情景与投资者问题走查

Parent：I-13；状态：planned；Owner：独立买方reviewer与行业reviewer；依赖：I-13-A。

前提：

- 完整输出已评分，可区分事实、假设、未知。

动作：

1. 让reviewer只用最终报告回答：增长从何而来、何时确认、最大三项驱动贡献、哪些约束会使高情景失败、哪条证据推翻基情景。
2. 复核收入年路径、增量、CAGR边界、驱动贡献和敏感性；非线性分解方法若未冻结，禁止把交互项随意分配。
3. 对照独立预期来源；若无可靠consensus/market-implied数据明确写不可得，不编数字。检查可预期差异是否来自口径不同。
4. 将答案逐条链到source→parameter→calculation→output；点开至少一个重要原文来源确认真实内容，摘要或manifest名不代替实际读取。

停止：

- 报告只能给目标数，无法回答驱动/时点/约束→STOP_INVESTOR_USE。
- 把低高情景当概率、混淆产量/销量或总净额→STOP_ACCOUNTING。

验收：具体问题可用最终交付独立回答；缺失需回到对应卡，不能在总结里虚报补齐。

证据：`evidence/I-13-B/investor_walkthrough.md`、`evidence/I-13-B/source_read_receipts.json`、`evidence/I-13-B/scenario_constraints.json`、`evidence/I-13-B/expectation_comparison.json`。
