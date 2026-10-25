# W16-RF-BASIS 独立施工计划

## Next Step

B：按冻结设计先写 RED 测试（tests/test_w16_revenue_basis.py 单元 + tests/test_w16_revenue_basis_cli.py CLI E2E 矩阵），实现 `scripts/research/revenue_basis.py` 单一 owner，接线 contracts/document.py、revenue_report.py、lint_input.py、generate_input_template.py；legacy 与 golden 行为保持。

## 目标

完成construction_card.md所有适用需求，关键行为真实执行，独立agent全面审查并修复全部本范围问题，测试恢复后交接。不能把工程组件通过说成主线公司内容验收通过。

## 大节点

- [x] A 真实边界/既有PWF与代码调查；先冻结独立预期和接口。（2026-10-25：缺口/设计/E2E矩阵/B07来源已冻结入 findings.md）
- [ ] B 根因TDD、共享owner实现或薄编排；兼容与实际入口接线。
- [ ] C 集中相关单元/集成/CLI端到端，独立agent完整审查，全部修复/复测/复审。
- [ ] 提交代码与独立审查证据，handoff.md/json、恢复/空间收据齐全。

每阶段变更更新本文件、findings/progress和唯一Next Step。外部阻塞具体记录，不重复盲跑失败，不加小节点审批。
