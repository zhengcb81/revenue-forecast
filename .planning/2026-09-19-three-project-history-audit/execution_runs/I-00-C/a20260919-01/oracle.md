# I-00-C 冻结预期（运行前已写判定规则）
门规则（新 UC-SCEN-GATE 语义，见 iso/_pkgdir/uc/scenarios.py::scenario_gate）：
- passed/expected_failure_pass 标签单独不足；必须：tier 显式（matrix_defined 不等价满足）
- evidence_path 存在；有 fixture_hash 或 oracle 绑定（裸标签=196项历史缺陷形态）
- oracle 对象若 validated_commands==[] 且 invariants==[] => empty_commands_and_invariants
- required_capability 未被 covered_capabilities 覆盖 => 拒（READ10 型错映射）
- closure.py::closure_report 使用同一 scenario_gate；narrowed successor 无 linkage 不清原义务(CA-206/301/302 形)

六负例预期（改后必须全拒）：
N1 全passed无绑定 -> red（197项全部拒）
N2 READ10 错证据 -> 拒；覆盖能力的对照样 -> 受限接受
N3 旧 accepted 遮新 changes_required -> revision_select 拒
N4/N5 oracle 空 commands/空 invariants -> 拒
N6 narrows successor 无 linkage -> 原义务保持 pending 且打 narrowing 告警
正例：一个 tier/证据/hash/oracle/capability 齐 -> 仅该场景限域完成
跨入口：下层 197 红 => closure old_plan_verdict=incomplete
旧历史：production vc 仓 uc/ 未触碰（git 确认+patch仅作用于iso副本）
