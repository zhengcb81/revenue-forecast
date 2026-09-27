# CA-107 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：旧 closure 只报"剩五项"

`tools/closure_gate.py` 的 problems 集合只覆盖 71 行 FC 状态子串——对 filing 目录
receipt 缺失、reviewer 缺失、evidence 篡改、sibling HEAD 切换、R9 4/4 RED 等均
无逐项精确原因（已实测：其 triplet 检查仅 ancestry，见 CA-002/CA-003 RED）。

## RED-B：三仓 receipt 无统一机器搜索

filing-fetch/company-wiki 的 assurance/fc/** 从未被任何新工具扫描；revenue 的
unified_completion/receipts 之外旧 assurance/fc 亦不在验证范围内。

## RED-C：缺 receipt/缺 reviewer/篡改无精确原因

旧 gate 对删除 filing receipt、删除 reviewer receipt、篡改 hash 的失败模式没有
mutated test 保证（mutation 属 CA-108，本卡先把检测逻辑落进 closure 报告）。

## 新工具对照（本卡实现）

`uc.closure`：三仓全量 receipt 扫描 → 每单元 verdict（machine_valid / legacy /
incomplete + 精确问题列表）→ 聚合报告：legacy 71 FC 处置计数、197 场景
unsatisfied 数、已知缺口清单（R9 RED、FC-150x pending 等）→ 旧计划诚实判
`incomplete` 且原因集合完整。
