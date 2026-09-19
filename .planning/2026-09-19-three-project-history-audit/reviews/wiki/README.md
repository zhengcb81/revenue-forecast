# wiki 审计交付索引

本分区正文阅读和逐条账本已完成；主审最终覆盖汇合另由 root 负责。本目录没有产品修复。

- [最终分区报告](review.md)：结论、覆盖、局限、判定统计与自我更正。
- [逐项账本](item_ledger.jsonl) / [CSV](item_ledger.csv)：1,263 条；不是 1,263 个运行测试。
- [最终阅读覆盖](read_coverage.json)：103 MD 全文路径、1 工程字段部分、1 业务排除；[路径行号/ID校验](ledger_validation.json)。
- [第二波交叉复核](cross_review.md) / [被审版本hash](cross_review_snapshot.json)：根报告/计划与 175 个人工 case 的判定对象。
- [当前只读诊断](readonly_diagnostics.json)：doctor、51 冻结项、配置控制前后 hash；其中历史 git exit128 失败记录保留。
- [历史Git成功读取](historical_git_readonly.json)：使用命令局部 safe.directory，三次 exit0；不改持久 Git 设置。
- [工程字段复算](engineering_context_checks.json)、[旧版本全文映射](old_version_mapping.json)、[旧机器计划差异](old_machine_item_review.md)、[冻结意见演变](freeze_issue_timeline.json)、[独立规划结构检查](plan_structure_checks.json)。

`worklog.md`、`v5_semantic_notes.md`、`handoff_clusters.md` 保留推进轨迹，里面早期 pending 表述不是当前完成状态。`scope_inventory_summary.json`、`file_coverage_pending.json`、`unassigned_engineering_context.json` 是初始清点/分派阶段文件，**不能作为当前未审或已审统计**。最终状态只看 read_coverage 与 review；其他 owner 的文件不能由本目录代签全文。

各生成脚本只是将已人工阅读的判断格式化为 JSON/CSV/元数据，不能当作新的独立 reviewer 或运行通过证据。旧阶段脚本可能恢复当时状态，未经审查不要重跑覆盖最终账本。
