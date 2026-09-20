# M30 · finite_adoption · finite market adoption — decision.md

**A-C 阶段没有需要专业审查的设计决定；不适用原因如下。**

## 1. 本卡属于哪一类

M29/M30/M31 是 I-10 的公式卡，调度验收范围只有 A–C：绑定、冻结期望并运行唯一入口 `calculate_registered_model`、以及用新 deepcopy 输入执行负例。按 `START_HERE.md` 第 47 行，需要先写 `decision.md` 并交专业审查的是跨进程锁/崩溃恢复、发布包事务边界、writer/producer 契约变更、财期/重述/收入总净额与 payability 归属、不可识别模型参数、样本/基准/统计阈值与概率校准、部署迁移与自然观察资格。

## 2. 逐项判定（not_applicable_with_reason）

| 专业门 | 本卡判定 | 依据 |
|---|---|---|
| 跨进程锁与崩溃恢复 | not_applicable_with_reason | 本卡只调用纯函数，不写任何共享状态、不启 worker、不加锁 |
| 发布包事务边界 | not_applicable_with_reason | 不产出发布包，只产出本 attempt 目录内证据 |
| writer/producer 契约变更 | not_applicable_with_reason | 未改任何产品文件（见 `changes.diff` 为空的显式声明与 `integrity.json`） |
| 财期/重述/总净额/payability | not_applicable_with_reason | A–C 不使用真实披露；这属于 D （披露适配），本卡保持 `unmapped` |
| 不可识别模型参数 | not_applicable_with_reason | A–C 只做合成数值；识别性问题属于 I-11-B |
| 样本/基准/统计阈值/概率校准 | not_applicable_with_reason | 属于 I-12（准确性），本卡保持 `unproven` |
| 部署迁移与自然观察资格 | not_applicable_with_reason | 本卡不部署、不发布 |

## 3. 仍然存在、但不属于 A–C 的专业问题

- D（披露适配）确实需要行业/会计 reviewer：the card's business negative is partly enforceable: the pool identity and cross-year continuity are enforced, but whether a reported figure is a first adoption or a renewal is a disclosure question。本卡据此把 `disclosure_adaptation` 保持 `unmapped`，并把该点记入 `oq_rulings.json` OQ-03。
- 需要 owner 裁定的两项：OQ-01（隔离绑定来源）与 OQ-05（`oracle.md` 被事后按同内容恢复，其当前 mtime 晚于产品 stdout）。两项均已在 `handoff.json` 的 `open_questions` 里指名归属。

## 4. 本文件的签署边界

本文件不构成任何资格授予。`qualification.json` 只更新 `formula`，且状态由 runner 的原始退出码决定；`accepted` 只能由独立 reviewer 写。
