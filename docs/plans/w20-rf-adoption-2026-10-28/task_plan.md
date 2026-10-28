# W20-RF-ADOPTION 独立施工计划

状态：B实施中。A调查已完成并冻结设计（见findings.md A1/A2）。唯一执行入口：[construction_card.md](construction_card.md)。本计划PLAN_ID=w20-rf-adoption-2026-10-28，PWF_PLAN_ROOT=docs/plans。

## 大节点

- [x] A：调查已有owner/PWF/commit，冻结适用缺口、接口、正反例、真实有界测试命令（2026-10-28完成；结论=仓内无既有采用观察工具，新建`tools/narrative_adoption_audit/`单一owner；设计冻结见findings.md A2；基线76 passed）。
- [ ] B：TDD先RED（两测试文件全量失败记录），实现`tools/narrative_adoption_audit/{audit.py,cli.py,README.md}`+`tests/test_w20_narrative_adoption_audit.py`+`tests/test_w20_narrative_adoption_e2e.py`，全部转绿；不改allowlist外文件。
- [ ] C：必要单元+真实CLI端到端（direct_revenue与direct_growth两类驱动模型）、清理恢复收据、独立agent初审→修复→复审（本范围OPEN清空）、`delivery/w20-rf-adoption/handoff.{md,json}`+`review/{initial,final}.{md,json}`、commit/推分支、回报三路径后STOP。

## B 细步

1. RED：先写两测试文件（用例清单见findings.md A2测试包1-11），运行记录ImportError/失败=RED证据。
2. `audit.py`：纯核心——输出投影节点索引（单遍）、输入侧索引（params/claims/sources/by snapshot_sha256）、公式upstream闭包（worklist O(P+E)）、consumption回执join（claim/param/source_sha256/formula_refs四重核）、narrative三件套经真实`validate_narrative_response`、items状态机、诊断、计数、资源界。
3. `cli.py`：argparse界面（findings A2 CLI合同），stdout默认、--output拒绝覆盖、gzip bundle、退出码0/2。
4. `README.md`：用法、状态/原因码语义、"诊断非许可"声明、资源界。
5. 转绿+`ruff check tools/narrative_adoption_audit tests/test_w20_narrative_adoption_*.py`。

## Next Step

写RED测试文件并记录失败输出，随后实现audit.py。
