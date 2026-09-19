本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-00-C — 修复现有验收器的证明范围
Parent：I-00。依赖：I-00-B。Owner：验收工具负责人；独立审查者验收。

锚点：RF/assurance/unified_completion/uc/scenarios.py::closure_report、verify；RF/assurance/unified_completion/scenarios/scenario_registry.json；RF/tools/receipt_validator.py::validate_receipt；RF/tools/closure_gate.py::_validate_receipts；../reviews/aug13_independent/checks.py（旧探针只读其逻辑，不覆盖旧输出）；../reviews/aug13_independent/review.md。state的具体更新路径由I-00-B通过现行调用链绑定。允许改：这些现有验收入口及最小测试；禁止新造另一套完成状态产品。

1. 在隔离目录保存当前197场景的原义务、tier、证据路径、输入/oracle绑定；明确未知tier不能等价满足。
2. 冻结六负例：全部passed但无证据；READ10引用不测deadline的测试；同一有效组合旧PASS后新FAIL；空commands；空invariants；删除CA206/301/302原义务仅保留缩小卡。六者都不得解锁相应业务完成。
3. 冻结正例：一个明确适用场景具备真实输入、原始执行结果、独立oracle、正确tier/版本与结论；只允许该范围完成。预期非0错误案例应保留raw rc，经expected rc和业务断言认定负测成功。
4. 专业reviewer先确定旧状态迁移和“最新有效结果”的组合键/时间排序，禁止弱模型只取最后一个JSON或只信accepted标签。
5. 在原验收器内修补证据与义务关联，重跑六负一正并检查旧历史不被改写。任何格式验证不得冒充人工语义oracle。
6. 跨入口调用现有汇总器验证：下层blocked对应上层仍blocked，不能仅在备注保留缺口却summary=true。

退出：六负例都拒绝，正例仅限域接受；原义务与后继分开。恢复：撤回本次隔离修改，不改旧registry/receipt。设计未冻结时blocked，不能为了全绿删除场景。
