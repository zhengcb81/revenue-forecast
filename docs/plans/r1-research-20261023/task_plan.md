# W09-RF-RESEARCH 独立实施计划

唯一施工卡：[W09-RF-RESEARCH](C:/Users/郑曾波/Projects/company-wiki/docs/plans/du11-source-closure-2026-10-18/harness_lanes/20261023/W09-RF-RESEARCH.md)。本目录是本包唯一PWF执行队列，父母仓状态由ROOT维护。

## 目标与责任

正式来源引用与角色、最大驱动经营桥、主/压力原生预测及通用买方研究方法。详细输入、允许写集、真实命令、测试矩阵和输出字段以卡及共享INTERFACES/INPUTS为准。代码base `10bf611166013bd68ce14bfa19bb70e89a92dd5b`，支线`codex/r1-w09-research-20261023`，start HEAD `42393ea1ca75dc28e751308246dbf856180882bd`。

## Next Step

A/B/C 研究主体全部完成；独立审查两轮（第一轮 FAIL→修复，第二轮 PASS_WITH_MINOR，三条尾项已收尾）。剩余动作仅：commit、写 handoff.md/handoff.json、push 支线。

| 大节点 | 状态 | 完成条件 |
| --- | --- | --- |
| A 恢复和冻结 | done | 输入/版本、预写判据、独立组件桥已完成；无缺陷处如实记录 |
| B 实施/研究 | done | 49项修复、RPO、经营桥、主/压力原生链、方法卡写回、泛化例 |
| C 交付 | done | 两轮独立审查、全部问题修复并复审通过、清理收据；只剩 commit/handoff 机械步骤 |

## A 大节点实际结论（替代原"pending"）

- 冻结：`delivery/w09/inputs/readonly-inputs.json` 记录 29 项只读输入的真实绝对路径、SHA-256、字节数与用途；全部与卡上预期 SHA 一致（`mismatch_logical_names: []`）。
- 预写判据：`delivery/w09/research/acceptance-checkpoints.json` 在写出任何新数字之前保存，含 10 项语义判据与 5 条"不得当作 GREEN"的反向清单。
- 独立基准：`delivery/w09/research/component-bridge.json` 全部用 Decimal 从原生 pointer 与已核验页偏移重算，未复用准备脚本的 PASS 布尔值。

## B 大节点实际结论

- 49 claim 全部重绑/降级并逐条留痕：`delivery/w09/research/claim-changes.json`（49 行、无重复；另列 9 条 union 外同缺陷修复与 1 条 RPO 需求修复，均不计入 49）。
- 角色：31→26 mechanism、18→21 conversion、0→2 history_base；18 条价格反控全部保留为 `conversion_assumption`。
- RPO：`reported_fact`→`management_guidance`，角色 `history_base`→`value_range`，数值不变，无 DAG 消费。
- 原生链：主/压力各 validate→compute/render→snapshot，共 6 次，全部 exit 0、input/output complete、冻结输入 SHA == builder request SHA；输出与封存旧输出逐位相同。
- 方法卡：三张各补最小必要段落；泛化用不同业务结构的离线合成例（订阅平台+项目服务）检验。

## C 大节点状态

- 独立审查：`delivery/w09/review/independent-review.{md,json}`。
- 修复记录：`delivery/w09/review/review-fixes.md`。
- 最终复审：`delivery/w09/review/final-independent-review.{md,json}`。
- 清理：`delivery/w09/cleanup/receipt.json`（tmp 已清空、scratch 已移除、24 个被取代的 request attempt 目录已删，六个正式 capture 保留）。

## 诚实边界

本包通过不等于经济质量认证或整公司通过。经验校准仍未验证（`observed_range` 全为 null、12 项校准全 `unverified`）；未消费 W08 新摘要、未导入中央 run、未做 W12 四路审查。这些属 ROOT 后续动作。
