# M17 decision record — licensing_commercial（商业销售与许可收入）

Card M17（`execution_v2/card_M17.md`），model_id `licensing_commercial`，
attempt `execution_runs/M17/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`handoff.json`、`review.md` 一致。

`START_HERE.md` 要求在实施任何落入专业决策范围的事项之前写 `decision.md`：跨进程锁与崩溃恢复、
发布包事务边界、财期/重述/收入总净额与 payability 归属、不可识别模型参数、样本/基准/统计阈值与
概率校准、部署迁移与自然观察资格。

## 1. 本 attempt 实际范围（A–C）

本 attempt 只执行卡片动作 A、B、C：绑定隔离环境、跑正例/连续性/默认值、跑 11 个负例。
范围内**没有**跨进程锁、发布事务、持久化写入或部署：被测对象是一个纯内存函数
`calculate_registered_model`（无状态、无锁、无文件副作用），输入是冻结的合成输入。

因此以下专业决策在**本 attempt 范围内不成立**，记为 `not_applicable_with_reason`：

| 决策类别 | 结论 |
|---|---|
| 跨进程锁 / 崩溃恢复 | not_applicable_with_reason：纯函数，异常后无可回滚状态（见 `recovery/README.md`） |
| 发布包事务边界 | not_applicable_with_reason：本 attempt 不产生任何发布包 |
| 部署迁移与自然观察资格 | not_applicable_with_reason：未部署、未做自然观察 |
| 样本/基准/统计阈值与概率校准 | not_applicable_with_reason：A–C 不做统计评估；准确性是第三种独立资格（`accuracy=unproven`） |

## 2. 存在、但**本 attempt 未作**的专业决策（不写结论，只登记）

D 动作在卡片中是 `[professional_decision_required]`，下列判断需要行业/会计 reviewer 明确选项与理由，
本 attempt **没有**作出任何结论，也**没有**产出任何披露映射（卡片明示该类文件不阻塞 A–C，且不得虚填）：

- DEC-M17-1：`treated_units` 的口径选择（患者 / 疗程 / 剂量三选一）以及它与
  `net_revenue_per_unit` 的口径必须同源；卡片 L45 明示"患者不可直接乘每剂价格"。
  计算器只校验数值域，无法判断单位错配。
- DEC-M17-2：三个金额项（里程碑 / 销售分成 / 服务收入）中哪些属于**已确认**收入；
  卡片 L45 明示"潜在里程碑不能当已确认收入"。计算器无法区分"潜在"与"已确认"。
- DEC-M17-3：`milestone_revenue` / `royalty_revenue` / `service_revenue` 在注册表中属于
  `_SIGNED_DRIVERS`（`model_registry.py:265-269`），有效域 `(-inf, inf)`，因此**负数金额会被接受**
  （已测量：`evidence/M17/extra_probes.json` 的 `PROBE-NEG-MILESTONE` 得 90.0）；
  只有**总收入为负**才被拒绝（`PROBE-NEG-TOTAL-REVENUE` 抛 `ModelRegistryError`）。
  这是"已确认金额应为非负"与"实现允许冲回/负数"之间的口径缺口，需要专业裁定，本 attempt 不改代码。
- DEC-M17-4：总净额口径（gross/net）与渠道扣减是否已在 `net_revenue_per_unit` 中体现。

## 3. 指向 handoff 的开放项（不得留陈旧措辞）

`handoff.json` 的 `next_step_number = 4`（第一条未完成的卡片动作就是 D），
`next_action` 写明 reviewer 复验后由专业角色启动 D。开放项由 `handoff.json.open_questions`
逐条列出（源自 `evidence/M17/oq_rulings.json`），逐条 id 与处置方：

| OQ id | 处置方（`requires_ruling_from`） |
|---|---|
| OQ-01 隔离绑定来源（I-00-B 未物化 checkout） | owner（调度/绑定） |
| OQ-02 省缺可选 driver 被静默补 0 | owner（改产品需另立卡） |
| OQ-03 卡片业务负例（单位错配、潜在里程碑）无法运行时拒绝 | 行业/会计 reviewer（I-10-A / D） |
| OQ-04 数值域与边界观测 | 独立 reviewer（accept / amend / reject） |
| OQ-05 本卡 attempt 重跑与探针常量更正的流程声明 | 独立 reviewer |

## 4. 本 attempt 的一个已登记更正（不是"为过审而改"）

`oracle.md` 第 1 节有一行**描述性**表述把三个金额项的有效域写成 `[0, inf)`；运行后的枚举与实测
（`evidence/M17/registry_enumeration.json`、`evidence/M17/extra_probes.json`）表明它们是
`(-inf, inf)`。该行不是期望值，且 `oracle.md` 已冻结，故**有意不改**，只在
`evidence/M17/oq_rulings.json`（OQ-04）与 `review.md` 中登记更正。冻结的期望值未受任何影响。

状态：`formula = review_pending`（待独立 reviewer，实现者不自签）；
`disclosure_adaptation = unmapped`；`accuracy = unproven`。
