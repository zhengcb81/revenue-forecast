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

## 2026-10-28 作者C节完成（交接）

- 独立初审：S1（需求符合度/架构/边界语义）报2项P0（F1 /4能力位误聚合可被判used、F2 elimination约束漏出wired闭包）+F3/F4及P3备注；S2（测试真实性/错误路径/清理）无P0、5项P1（断言弱/错误路径未测）。初审原文落盘`delivery/w20-rf-adoption/review/initial.{md,json}`。
- 修复（8b221153）：`_span_support_use`按reader契约重写（仅support授予支撑、context/unresolved绑定被标记不服从、/4未分组=unresolved）；约束索引与引擎`_constraint_uses`逐类型同构（elimination/sum_cap/linked_ratio）；`receipt_formula_refs_missing`宽松记录；KNOWN_CONSUMPTION_FIELDS对齐/3；/3回退parent_source_refs；删除items_capped；--pretty独占创建；新增/4三态、约束三形状、formula_refs缺/错、CLI失败分支、wire拒绝链路、n/2n强化（t1>0.02下限）、BIREN字节级对比、offline_guard文档声明。
- 独立复审：全新agent逐条核销14项全FIXED+独立探针（含引擎`parameter_uses`交叉验证），新发现仅4项P3备注，**OPEN_findings=[]，verdict PASS**。落盘`delivery/w20-rf-adoption/review/final.{md,json}`。
- 最终实测：单元24 passed（1.80s）、e2e 2 passed（5.98s）、回归106 passed（6.25s）、ruff clean；e2e背靠背重跑无残留。
- 交付：`delivery/w20-rf-adoption/handoff.{md,json}`（tested_code_commit=reviewed_code_commit=8b221153）。
- 推送：分支`codex/w20-rf-adoption-20261028`推至origin。

## 2026-10-29 R1返工（ROOT验收CHANGES_REQUESTED → 修复）

- ROOT返工单三项：RF-R1/P1 receipt仅查键存在未验整链；RF-R2/P2 同span多路径只留首条；RF-R3/P2 gzip绕过字节上限。ROOT证据：rf-review.{md,json}+rf-evidence/probe.py（本机重放确认）。
- RED：10个新测试失败记录（链5例/聚合3例/gzip2例，含截断gzip未捕获EOFError崩溃）。
- 修复：(1) `_evaluate_dependency`重写为共享receipt-resolution：span材料→canonical parent经capture映射到RF本地source→提供source_id/locator/parser与运输span逐边核对→claim归属/材料/target边→param存在→run公式边；缺hash仍宽松unknown（链走span自身parent哈希）；新增命名码receipt_source_mismatch/receipt_span_hash_mismatch/receipt_locator_mismatch/receipt_parser_mismatch/receipt_claim_source_mismatch/receipt_claim_material_mismatch/receipt_claim_target_mismatch/span_material_not_provided。(2) span按canonical聚合全部intact路径cited_by并集+内容排序去重，invalid路径保留各自诊断（span_dependencies_aggregated info替换误导性的"several receipts"）；顺序/拆分回执不变性测试。(3) `_gunzip_bounded`流式解压最多limit+1即命名resource_limit，截断/损坏→input_decompress_failed，失败不留半输出。
- ROOT探针重放：foreign_span→unverifiable+receipt_span_hash_mismatch；wrong_explicit_source_id→unverifiable+receipt_source_mismatch；two_valid_bindings→used+slot_years[2026,2027]；gzip_bound→rejected resource_limit。
- 实测：单元34+e2e 2=36 passed（7.14s）；回归106 passed；ruff clean。
## 2026-10-29 R1返工收尾（复验PASS）

- 独立复审第一轮（a1edda18）：三项ROOT返工全FIXED，但新发现[P2] F1——/3多父投影parent_sha固定取refs[0]，span实际父在refs[1]时合法回执被误判unverifiable（三条假诊断）。OPEN=[F1]。
- 修复（e4657377）：span_material按每个span自身source_id在(source_ref+parent_source_refs)解析实际父；span展示字段同源。新增RED→GREEN测试test_projected_multi_parent_context_resolves_actual_span_parent（真实validate_narrative_response+consume+run_forecast链）。
- 独立复审第二轮（e4657377）：F1 FIXED、全部探针无回归、F2裁定不阻塞，OPEN_findings=[]，verdict PASS。记录落盘delivery/w20-rf-adoption/review/rework-review.md；原initial/final审查保留。
- 最终实测（复审agent）：W20全量37 passed（5.81s）；回归106 passed（3.44s）；ruff clean；工区clean。
- handoff.md/json刷新：tested/reviewed_code_commit=e4657377，文件SHA按e4657377字节更新（README与e2e未改动保留原SHA），补rework节与RF-R1/R2/R3逐项PASS。
