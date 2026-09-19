# 独立验收与上下文接续

每张执行卡使用这里的共用验收步骤；卡片里的专属oracle不可被这里的格式检查替代。

## reviewer固定操作

1. 先读parent I-xx原义务和具体卡；比较本次实际范围。被移出范围的要求必须保留独立待办与依赖，不因拆卡消失。
2. 不先看实现者“通过”摘要；先看输入/源/config/安装指纹、命令、raw退出码和原始输出，再看业务结果。
3. 对比修改前与修改后同一反例。若反例已修，检查是否确实是同一攻击面，接受无需修改的局部复验；不要求人为失败。
4. 复算至少一个卡片专属oracle。expected从被测函数、同一parser或同一helper生成的，一律不能视为独立验证。
5. 从输入维度预先保留一个实现者未用于编写修复的变化案例：例如另一root名、不同修订ID、另一并发时序、不同单位。审查前记录其预期与hash，不看运行结果后选样。不要求秘密传输，也不把未披露要求事后加给实现者。
6. 对状态性卡检查异常后重启/重试和最终持久化，不仅检查异常是否抛出。恢复必须在隔离目录，验证仍可使用上个完整版本。
7. 若卡涉及跨仓入口，至少一次从消费者真实入口到目标后果；mock/helper测试不能替代。明确network/fixture/live层级。
8. 检查allowlist外diff、读取内容与仅选择角色、调用事件与产物事件、elapsed与自然时间、公式正确与准确性分开。
9. 写结论：accepted_scoped / changes_required / blocked / not_applicable_with_reason。列资格与未获资格；只有原义务明确不适用且有依据时可标NA，不能把缺样本标NA。

## 交付最小目录（未来实施时创建）

```text
execution_runs/<card-id>/<attempt-id>/
  binding.json       # 当前代码、配置、输入、隔离目录
  decision.md        # 如需专业设计；无则明确不适用原因
  commands.json      # 每次调用的argv/cwd/timeout/预期
  oracle.md          # 运行前冻结的独立预期
  before/           # 修改前原始日志、状态与hash
  after/            # 修改后原始日志、状态与hash
  recovery/         # 异常后恢复；纯函数可说明NA
  changes.diff      # 仅本次允许修改，与既有dirty分离
  review.md         # 独立结论和保留案例
  handoff.json      # 下一次从哪里继续
```

不能仅交文件名/hash；reviewer需读实际内容。不得执行本轮历史审计脚本后覆盖其旧checks.json来冒充新证据，复制逻辑到新attempt输出目录并绑定当前代码。审计脚本若内嵌旧路径，先做只读检查及路径替换审查，不能直接运行。

## handoff字段与接收动作

`handoff.json`必须有card_id、attempt_id、status、completed_steps、next_step_number、next_action、input_hashes、current_source_hashes、changed_paths、commands_executed、raw_exit_codes、expected_exit_codes、open_questions、blocked_by、evidence_paths、reviewer_status。列表允许空，但未完成原因必须明确；不能写“继续完善”作为next_action。

接手者只读卡片、binding、oracle、decision、review和handoff，再读与下一步有关的源码。先重新验证当前文件hash；一致才从next_step继续，不重复下载、不重做已成功写入。变化则按START_HERE漂移分支暂停受影响步骤。

## 上级完成条件

所有适用子卡被独立接受 + 原义务矩阵无缺口 + 必须的跨卡用户旅程成功，三者缺一不可。31模型的公式卡通过只获得公式资格；实际披露适配与准确性分别验收。真实公司数据管道成功只获得来源链资格；没有正式建模和发布包，仍不能叫预测成功。

普通只读查询不依赖自然观察全部完成；生产持续服务承诺不得跳过其观察资格。替代样本、放宽预算、取消审核门和重新写旧PASS都不能用来关闭blocked。
