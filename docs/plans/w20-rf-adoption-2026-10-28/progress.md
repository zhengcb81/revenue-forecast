# 实施进度

2026-10-28 ROOT只完成工区与施工文档准备，尚未实施本卡或运行测试。三个大节点均未开始；作者接手后按实际记录，交接前必须真实独立agent审查、修复和复审。

## 2026-10-28 作者A节完成

- 工区核验：HEAD=`0991e25d5dca667a3fdafb7bc5ebf0e546a2272b`（=冻结基线），分支=`codex/w20-rf-adoption-20261028`，status仅本plan目录4个untracked（ROOT预置施工文档，归A首批提交）。稀疏检出含scripts/tests/tools/docs，未复制`.planning`历史。
- 四路只读调查（RF输出合同/叙述证据链/既有工具与测试/W16交接与SKILL），结论与冻结设计写入findings.md A1/A2。核心判定：仓内无既有采用观察工具，新建`tools/narrative_adoption_audit/`。
- 基线绿色：`python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_recognition_bridge.py tests/test_du11_narrative_citation_context.py tests/test_du11_narrative_citation_consumption.py tests/test_research_support_diagnostics.py` → **76 passed in 5.15s**。
- 主仓、company-wiki、其他工区零写入。

## 2026-10-28 作者B节完成

- RED证据：先写`tests/test_w20_narrative_adoption_audit.py`，运行报`ModuleNotFoundError: No module named 'tools.narrative_adoption_audit'`。
- 实现：`tools/narrative_adoption_audit/{__init__,audit,cli}.py`+`README.md`（纯核心+薄CLI；状态机/诊断/资源界按findings A2冻结设计）。
- 测试：单元15个（同源采用/display key不拼接/context不当支撑/summary无trace→not_observed/口径诊断/多节点去重/旧格式兼容/hash错配与宽松/未知字段/确定性/线性n/2n+资源界/闭包差分/CLI不覆盖/snapshot交叉/异常回执）+ e2e 2个（direct_revenue真实子进程全链[stub传输→真consume工具→真forecast CLI→真audit CLI→真snapshot]；direct_growth biren+unwired变体）。
- 转绿过程中修正的真实问题：`parameter_formula_refs`需dict参；快照身份哈希含完整存储结果→绑定经`snapshot.forecast_result.result_sha256`；publication registry追加后置只读→清理需先chmod；narrative多视图support需显式`citation_view`消歧（既有契约行为）。
- 验证：W20两文件**17 passed**；回归（recognition_bridge+DU11 wire/context/consumption+support_diagnostics+W20）**98 passed in 18.15s**；ruff clean。
- 提交：A=`c71b79e2`，B=`65af44b9`。暂不推远端（工区无remote配置，交接时核实记录）。
