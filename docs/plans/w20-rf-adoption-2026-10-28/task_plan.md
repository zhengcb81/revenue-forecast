# W20-RF-ADOPTION 独立施工计划

状态：C进行中。A完成（c71b79e2）、B完成（65af44b9，单元15+e2e 2全绿，回归98 passed）。唯一执行入口：[construction_card.md](construction_card.md)。本计划PLAN_ID=w20-rf-adoption-2026-10-28，PWF_PLAN_ROOT=docs/plans。

## 大节点

- [x] A：调查已有owner/PWF/commit，冻结适用缺口、接口、正反例、真实有界测试命令（2026-10-28完成；结论=仓内无既有采用观察工具，新建`tools/narrative_adoption_audit/`单一owner；设计冻结见findings.md A2；基线76 passed）。
- [x] B：TDD先RED（ModuleNotFoundError记录于progress），实现`tools/narrative_adoption_audit/{audit.py,cli.py,README.md}`+两测试文件，17 passed+回归98 passed+ruff clean（65af44b9）。
- [ ] C：独立agent初审（进行中）→全部本范围问题修复→独立复审（本范围OPEN清空）→`delivery/w20-rf-adoption/handoff.{md,json}`+`review/`、commit/推分支、回报三路径后STOP。

## C 细步

1. 独立初审：两个general-purpose agent并发（S1=R1-R6需求符合度/架构/硬编码/边界语义；S2=测试真实性/错误路径/清理/资源界），产出findings清单。
2. 修复全部本范围发现，保留证据；重跑相关测试。
3. 独立复审：新agent复验最终实现（绑定最终commit），本范围OPEN必须为空。
4. 交付：delivery/w20-rf-adoption/{handoff.md,handoff.json,review/{initial,final}.{md,json}}；核实remote；回报工区/handoff.md/handoff.json三路径。
