# 发现

- B37 是分叉候选，不能整体 fast-forward 或 cherry-pick 其完整树；git diff main..candidate 涉及 628 文件、约 35k 行增加。
- 卡片指定的产品差额是 19 路径；其中 4 个完全相同，9 个需逐 hunk 适配，6 个主线缺失。
- 主要风险在 compare/scope/subject/publication DTO 的一致性；不能恢复直接读 CWP 私有 SQLite 的旧链路。
- 本工作树使用 RF 自有分支 codex/mb11-rf，与 RF 主线和既有 release 工区隔离。


## compare合同接收中的新发现

- 基线缺少 report_catalog_compare.py；加入该模块和固定 compare CLI 后，B37 新增合同测试51 passed/1 skip，证明主体实现可使用当前 ReportCatalog owner readers，而不需覆盖当前 catalog 模块。
- 原候选有 MAX_COMPARED_ROWS=512 与 MAX_OUTPUT_BYTES=1MiB 两个固定结果门槛，且无配置/owner工作预算依据。它们可能拒绝完整合法比较结果；已删除并补600期、长locator、>1MiB CLI完整JSON回归。
- MAX_METRICS=32对当前仅支持的revenue一项及重复项校验没有约束效用，已删除冗余计数上限。64KiB输入上限仍作为小型请求入口的资源保护；有效的四字段请求自身受字段和值形状约束。
- Decimal 4,096位/8,192精度限制用于限定精确算术资源消耗；尚未证明会触及有效报告输入，暂不在这次compare端口修改中动它。
