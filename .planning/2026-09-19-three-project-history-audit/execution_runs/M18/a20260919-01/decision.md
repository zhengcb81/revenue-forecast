# M18 decision record — advertising（曝光填充与CPM）

Card M18（`execution_v2/card_M18.md`），model_id `advertising`，
attempt `execution_runs/M18/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`handoff.json`、`review.md` 一致。

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

- DEC-M18-1：`eligible_impressions` 的口径——"填充前曝光机会"必须与已填充曝光区分。
  卡片 L42 明示"已填充曝光不再乘填充率"。计算器无法判断输入到底是哪一种，
  因此这是**披露/适配**问题，不是公式问题。
- DEC-M18-2：无效流量（IVT）与平台分成（gross/net）是否已在
  `revenue_per_thousand_impressions` 中体现；卡片 L40 要求采集"平台分成、无效流量、总净额口径"。
- DEC-M18-3：`fill_rate` 的 100% 端点。ratio 域 `[0,1]` 含端点，实测 `fill_rate=[1.0]` 被接受
  （`evidence/M18/extra_probes.json` 的 `PROBE-FILL-EXACT-1` = 10100.0），而 1.2 被拒（NEG-CARD）。
  若业务上"填充率恰好 100%"需要人工复核，应由专业角色裁定，本 attempt 不改代码。
- DEC-M18-4：`other_revenue` 属 `_SIGNED_DRIVERS`（`model_registry.py:265-269`），有效域
  `(-inf, inf)`，即负数"其他收入"（冲回）会被接受；是否需要非负约束属专业裁定。

## 3. 指向 handoff 的开放项（不得留陈旧措辞）

`handoff.json` 的 `next_step_number = 4`（第一条未完成的卡片动作就是 D），
`next_action` 写明 reviewer 复验后由专业角色启动 D；开放项逐条列在 `handoff.json.open_questions`
（源自 `evidence/M18/oq_rulings.json`）：

| OQ id | 处置方（`requires_ruling_from`） |
|---|---|
| OQ-01 隔离绑定来源（I-00-B 未物化 checkout） | owner（调度/绑定） |
| OQ-02 省缺可选 driver 被静默补 0（本模型：`other_revenue`） | owner（改产品需另立卡） |
| OQ-03 卡片业务负例（已填充曝光重复乘、IVT、总净额）无法全部运行时拒绝 | 行业/会计 reviewer（I-10-A / D） |
| OQ-04 数值域与边界观测（含 `PROBE-FILL-EXACT-1`） | 独立 reviewer（accept / amend / reject） |
| OQ-05 重跑与探针的流程声明 | 独立 reviewer |

## 4. 本 attempt 未出现"为过审而改"

`oracle.md` 自写定后**一字未改**；冻结期望值、容差、负例清单、拒绝条件均未修改。
`OBS-THOUSAND-ONCE` 的数值期望（16100）在运行前就写进 oracle 脚本，运行后实测相符，
是**先冻结后验证**，不是事后补写。

状态：`formula = review_pending`（待独立 reviewer，实现者不自签）；
`disclosure_adaptation = unmapped`；`accuracy = unproven`。
