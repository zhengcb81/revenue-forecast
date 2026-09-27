# ZR-708 工作单元卡（preflight）— F2：重验不可变 snapshot/backtest 基础接线

- 领取时间：2026-08-23T06:40Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-708`，ZR-707 accepted + closure→ZR-708；锁 ZR-708。
- 依赖：F1（✅ 全部）。Registry 依赖列=ZR-707 相关链。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 重验不可变 snapshot/backtest 基础接线——卡片语义："已有能力若当前 triplet 全绿则 **already_satisfied**；否则修复；accuracy record 实际可被 forecast 消费"。
2. **production entrypoint 是什么？** `scripts/revenue_backtest.py`（create_snapshot/validate_snapshot/validate_actuals/evaluate_snapshot）+ `run_forecast` 的 historical_accuracy_records 消费链。
3. **RED？** 探针：tests/test_backtest.py 17 tests 全绿（snapshot 确定性/tamper 拒绝/不可覆盖/accuracy hash-linked/accuracy→confidence 消费链/非未来 actual/伪造灵敏度拒绝/swap hash 拒绝/legacy engine 拒绝）；accuracy record → historical_accuracy_records → run_forecast → confidence.historical_accuracy 消费链已通（test_accuracy_record_flows_automatically_into_confidence）——**already_satisfied**（当前 triplet 全绿，无需产品修复）。
4. **允许改哪些文件？** revenue：新 `tests/test_zr708_backtest_reverify.py`（重验钉死全链）；revenue receipts/ZR-708/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-712（confidence 反博弈，依赖 ZR-708）。本卡不做：confidence policy 版本化（ZR-712）、紫金 rolling-origin（ZR-713）。

## Acceptance criteria
- **C1 already_satisfied 重验**：既有 backtest 基础设施（snapshot 不可变/确定性、tamper 拒绝、actuals 校验、accuracy record）在当前 triplet 全绿——重验测试钉死关键契约，不修复已正确机制。
- **C2 accuracy record 消费链**：evaluate_snapshot 产出的 accuracy_record → historical_accuracy_records → run_forecast → confidence.historical_accuracy 实际消费（wape 一致 + 组件贡献 >0）；tampered record 拒绝。
- **C3 不可变接线**：snapshot 覆盖拒绝、未来 actual 拒绝、四层 hash 链接（record_sha256）——重验断言。
