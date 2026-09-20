# M19 decision record — gaming（活跃用户付费变现）

Card M19（`execution_v2/card_M19.md`），model_id `gaming`，
attempt `execution_runs/M19/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`handoff.json`、`review.md` 一致。

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

- DEC-M19-1：**期间口径**。`active_users` 与 `revenue_per_payer` 必须同期间（卡片 L8「同期间同去重」）。
  若把 DAU 与"年度 ARPPU"相乘，公式照样给出数字，但经济含义错误（卡片 L42 业务负例）。
  计算器内没有期间信息，故这是披露/适配决策，不是公式决策。
- DEC-M19-2：**流水 ≠ 收入**。渠道费、递延确认（道具/时长卡）必须另行桥接；卡片 L40 要求采集
  "渠道费、流水/递延/收入桥"。是否用净额、递延比例多少，属专业裁定。
- DEC-M19-3：**去重口径**。活跃用户与付费用户是否同一去重口径（账号/设备/自然年）需专业裁定；
  计算器只把它们当作两个数字。
- DEC-M19-4：`payer_conversion` 的 100% 端点。ratio 域 `[0,1]` 含端点：实测 `payer_conversion=[1.0]`
  被接受（`evidence/M19/extra_probes.json` 的 `OBS-PAYER-BOUNDARY` = 20010.0），而 1.1 被拒（NEG-CARD）。
- DEC-M19-5：`other_revenue` 属 `_SIGNED_DRIVERS`（`model_registry.py:265-269`），负数（冲回）会被接受；
  是否需要非负约束属专业裁定。

## 3. 指向 handoff 的开放项（不得留陈旧措辞）

`handoff.json` 的 `next_step_number = 4`（第一条未完成的卡片动作就是 D），
`next_action` 写明 reviewer 复验后由专业角色启动 D；开放项逐条列在 `handoff.json.open_questions`
（源自 `evidence/M19/oq_rulings.json`）：

| OQ id | 处置方（`requires_ruling_from`） |
|---|---|
| OQ-01 隔离绑定来源（I-00-B 未物化 checkout） | owner（调度/绑定） |
| OQ-02 省缺可选 driver 被静默补 0（本模型：`other_revenue`） | owner（改产品需另立卡） |
| OQ-03 卡片业务负例（DAU×年度 ARPPU、流水≠收入）不可运行时拒绝 | 行业/会计 reviewer（I-10-A / D） |
| OQ-04 数值域与边界观测（含 `OBS-PAYER-BOUNDARY` = 20010） | 独立 reviewer（accept / amend / reject） |
| OQ-05 流程声明 | 独立 reviewer |

## 4. 本 attempt 未出现"为过审而改"

`oracle.md` 自写定后**一字未改**。边界期望（`OBS-PAYER-BOUNDARY` = 20010）在运行前写入 oracle 脚本，
运行后实测相符。本卡流水线只跑一次，14/14 单元 rc = 期望值。

状态：`formula = review_pending`（待独立 reviewer，实现者不自签）；
`disclosure_adaptation = unmapped`；`accuracy = unproven`。
