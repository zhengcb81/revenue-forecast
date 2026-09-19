# 可独立分簇的第二波工作

> 初始分派提案，已由 root 的实际 owner 分配及最终 [read_coverage.json](read_coverage.json) 取代，不表示以下簇仍无人审阅。

所有审阅只写本审计的 reviews/wiki 下分簇子目录；不修改 company-wiki。原始清单是 ../../inventory/company-wiki.json；业务正文 scope 由 root 定义。条目 verdict 只允许 supported_scoped / contradicted / insufficient_evidence / not_deployed / superseded / historical_only / not_applicable。每条须原文 path+line、历史声明与状态、历史证据范围、当前证据、建议。重复字节保留映射；不运行旧修复命令。

1. **根/旧 CW 历史**：根 task_plan.md、task_plan_cw_recovery_20260725.md、task_plan_v2.md、findings/progress/log、恢复副本、docs/archive 与旧架构说明。重建“实施/审查通过/生产验证”何时被混用；按独立 CW 编号而非段落关键词统计。
2. **R4/painpoint/FC**：docs/plans/painpoint-outcome-audit-2026-09-05、planning-sync-2026-09-04、assurance/fc。逐项审包括 PASS 与关闭项，核验 package/install、真实 canary、消费生产路径，避免冻结条目数代替业务运行。
3. **专项能力**：portfolio-reuse-fix、portfolio-reuse-automatic、core-section-extraction、catalog-space-remediation、data-lake-simplification 及相应 ADR/contracts。检查 scope、默认开关和当前调用路线。

本 agent 当前保留 v5/旧 worker recovery 主线。docs/contaminated_entries_review.md 的公司引用正文只作被审对象，不核验每个财务事实；工程断言/计数/污染判定须独立审查。
