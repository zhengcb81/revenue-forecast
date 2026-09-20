# M20 decision record — cohort_subscription（客户流量与时间暴露）

Card M20（`execution_v2/card_M20.md`），model_id `cohort_subscription`，
attempt `execution_runs/M20/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`handoff.json`、`review.md` 一致。

`START_HERE.md` 要求在实施任何落入专业决策范围的事项之前写 `decision.md`：跨进程锁与崩溃恢复、
发布包事务边界、财期/重述/收入总净额与 payability 归属、不可识别模型参数、样本/基准/统计阈值与
概率校准、部署迁移与自然观察资格。

## 1. 本 attempt 实际范围（A–C）

本 attempt 只执行卡片动作 A、B、C。范围内**没有**跨进程锁、发布事务、持久化写入或部署：被测对象是
纯内存函数 `calculate_registered_model`（无状态、无锁、无文件副作用）。

以下专业决策在**本 attempt 范围内不成立**，记为 `not_applicable_with_reason`：

| 决策类别 | 结论 |
|---|---|
| 跨进程锁 / 崩溃恢复 | not_applicable_with_reason：纯函数，异常后无可回滚状态（见 `recovery/README.md`） |
| 发布包事务边界 | not_applicable_with_reason：本 attempt 不产生任何发布包 |
| 部署迁移与自然观察资格 | not_applicable_with_reason：未部署、未做自然观察 |
| 样本/基准/统计阈值与概率校准 | not_applicable_with_reason：A–C 不做统计评估；准确性是第三种独立资格 |

## 2. 存在、但**本 attempt 未作**的专业决策（不写结论，只登记）

D 动作在卡片中是 `[professional_decision_required]`，本 attempt **没有**作出任何结论，也**没有**产出
任何披露映射（卡片明示该类文件不阻塞 A–C，且不得虚填）：

- DEC-M20-1：**时点因子不得无依据默认"年中"**（卡片 L57）。注册表的默认值是 `timing_factor = 1.0`
  （不是 0.5），本卡的合成正例也显式给 `[1]`；真实公司若只说"年内陆续签约"，
  时点因子必须由专业角色依据发生月份裁定，不能由实现者拍。实测边界：`timing_factor=[0.0]` 被接受
  （`evidence/M20/extra_probes.json` 的 `PROBE-TIMING-ZERO` = 5.0）。
- DEC-M20-2：**不同价格 / 同年新增又流失的群组需要专业拆分**（卡片 L57）。本模型用两个比例
  （新客收入比例、流失损失比例）近似，无法表达价格分层或同年内"新增后又在同年流失"的群组；
  是否可接受该近似，属专业裁定。
- DEC-M20-3：**客户桥的会计边界**。`ending_customers` 是输入而不是推算结果，模型只校验一致性
  （年内平衡 + 跨年连续），因此"桥本身是否可信"是披露问题。
- DEC-M20-4：`usage_revenue` 在注册表中**没有**显式 default 项（维为 revenue 的普通 driver），
  省缺时被 `spec.defaults.get(driver, 0.0)` 静默补 0；对"用量收入未找到"这类情况，
  静默 0 与"确实没有用量收入"不可区分（`OQ-02`）。
- DEC-M20-5：桥容差。实现用 `math.isclose(rel_tol=1e-9, abs_tol=1e-9)`；实测
  `opening=[100, 120.000000000001]` 被容忍（`PROBE-CONTINUITY-TOLERANCE`），
  而 1 户错配被拒（CONT-BREAK）。该容差是否需要收紧属专业裁定。

## 3. 指向 handoff 的开放项（不得留陈旧措辞）

`handoff.json` 的 `next_step_number = 4`（第一条未完成的卡片动作就是 D），
`next_action` 写明 reviewer 复验后由专业角色启动 D；开放项逐条列在 `handoff.json.open_questions`
（源自 `evidence/M20/oq_rulings.json`）：

| OQ id | 处置方（`requires_ruling_from`） |
|---|---|
| OQ-01 隔离绑定来源（I-00-B 未物化 checkout） | owner（调度/绑定） |
| OQ-02 省缺可选 driver 被静默补 0（本模型：`usage_revenue`） | owner（改产品需另立卡） |
| OQ-03 卡片业务负例（年中默认、群组拆分）不可运行时拒绝 | 行业/会计 reviewer（I-10-A / D） |
| OQ-04 桥/暴露的数值边界与容差观测 | 独立 reviewer（accept / amend / reject） |
| OQ-05 本卡 attempt 的流程历史（1 趟测量 + 6 趟收尾） | 独立 reviewer（r2 后已成为 `oq_rulings.json` 的真实条目，指向 `process_history.json`） |

## 4. 本 attempt 未出现"为过审而改"

`oracle.md` 自写定后**一字未改**。卡片自带的两年连续性用例（含 `negative_patch`）在运行前就被
逐字冻结为 continuity_positive 与 CONT-BREAK，并在 oracle.md 里写明期望错误语义
（"第二年 opening 比第一年 closing 多 1"）；运行后实测消息为
`cohort customer continuity failed: FY2028`，与冻结预期一致。本卡流水线只跑一次，14/14 单元 rc = 期望值。

状态：`formula = review_pending`（待独立 reviewer，实现者不自签）；
`disclosure_adaptation = unmapped`；`accuracy = unproven`。
