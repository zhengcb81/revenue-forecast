# R6-RF-INPUT 本线进度

## 2026-10-08

- 开工：工作树/分支/基线核实（codex/cmrf-input-semantics-20261008 @ 72ce94c1，干净）；读施工卡、三线 README/handoff、follow_up_plan/root_cause_remediation、RF SKILL 与 input-construction/input-schema/management-targets；CodeGraph 式核实实际实现入口与测试基建（详见 findings.md）。
- PWF：本线 docs `docs/implementation/cmrf-input-semantics-20261008/`；根级历史 PWF 未动。
- RED：`tests/test_input_quantity_conversion.py`、`tests/test_management_target_semantics.py`、`tests/test_evidence_input_lineage.py`；三文件 52 failed（缺三模块 API + 真语义反例：peer 自动 triangulated、同摘录混用不拒、伪 pp 算术自洽）。
- GREEN-1（I1）：`scripts/research/input_quantities.py`（convert_input_quantity / build_sensitivity_test / validate_input_quantity_record）+ `analysis/sensitivity.py` 接入（双重重算 + 输出透传）。单测 23 passed；golden 行为锁不漂移。
- GREEN-2（I2）：`contracts/constants.py` 新枚举（quarterly_period、raw_value_kind、currency/presentation basis）；`research/targets.py` 新语义解析（季度/定性/区间/未定年/转换扩围/material 门/unmodeled_reason）；`scripts/research/input_targets.py`（build_management_target）；`revenue_report.py` 渲染同步。单测 13 passed；既有目标/report 套件 52 passed 零漂移。
- GREEN-3（I3/I4）：`scripts/research/input_evidence.py`（bind_parameter_evidence + narrative span→正式 source/capture/claim）；`contracts/document.py` evidence_role 严格解析 + 参数级 history-only/反证拒绝；`research/drivers.py` peer 剔除出 triangulation + 按摘录哈希的同文支持/反证拒绝 + peer limitation。单测 17 passed。
- E2E：`tests/test_input_semantics_e2e.py` 8 passed——独立根真实子进程链 lint→fix_hashes--check→revenue_forecast(formal+registry)→revenue_backtest create→publication_registry lookup/audit；peer 变体（收入不变、triangulated→limited、limitation 出现 peer）与支持源变体（input_sha256/claim hash 变、registry 新 anchor、收入不变）；unknown published_date 具名拒绝。
- 集中回归：相关既有套件 196 passed；全量 1387 passed / 99 failed（排除 5 个稀疏环境受限文件）；99 个失败经基线 72ce94c1 同批文件复跑对照**全部预存**（HEAD-only 差集为空），零新增；golden 锁未动。
- 提交：0bcbae93（I1-I3 实现+单测+PWF）；第二批 E2E+findings/progress/HANDOFF/handoff.json 见 handoff.json commits。

## 未做/归 MAIN

- 未跑 `tests/test_narrative_source_preparation_e2e.py`（需 CWP producer checkout + PyMuPDF，属 MAIN 集成大节点）。
- 未改 assurance/runs、output、生产配置、compatibility/current.json、CI、旧快照；golden 哈希未重算。
- 三公司完整新研究、新 canonical 摘要消费、独立语义审查、第二组泛化：归 MAIN。


## MAIN合并后兼容修复

合并后的真实冻结三公司回放发现，中微未定年计划和微软季度目标已有rationale/measurement_rationale，却被新增可选unmodeled_reason字段重复阻断。两类责任测试真实2个subtest RED，保留业务解释、原话、无年度比较和收入不变断言；取消重复要求，显式无效字段仍拒绝。腾讯同一历史表格正反证据混用仍是需重做研究的实质缺口，不改封存输入/快照，不加公司白名单。
