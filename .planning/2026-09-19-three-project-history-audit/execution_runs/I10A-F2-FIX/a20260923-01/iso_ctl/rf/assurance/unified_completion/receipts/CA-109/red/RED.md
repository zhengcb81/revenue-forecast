# CA-109 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：CI workflow 调用旧 gate 语义

`revenue/.github/workflows/quality.yml:46-47` 运行
`python tools/verify_closure_ledger.py --ledger audit_review/2026-08-08_adversarial_plan/closure_ledger.json ...`
——CI 门直接依赖旧 closure 工具与旧计划 ledger（子串判定语义，见 CA-004 RED）。

## RED-B：旧 gate 与 Closure 2.0 结论分歧

旧 closure_gate 实测 `accepted_fcs=66`（子串），Closure 2.0 判旧计划
`incomplete`（26 contradicted + 5 pending + 197 unsatisfied + R9 冻结）——
旧语义与新架构 gate 必须红的一致性正是本卡的隔离目标。

## 新工具对照（本卡实现）

`uc.legacy_gate`：三仓 gate 表面 caller 扫描（排除旧工具自身与测试）、每个
引用登记为 P2 finding + successor=CA-201、verdict=isolated/callers_found；
真实扫描登记 LEGACY-CALLER-001（quality.yml，successor=CA-201）。
旧历史 ledger 保持只读展示（closure-report 已只读读取）。
