# ZR-708 RED 探针证据

- 日期：2026-08-23
- 探针：tests/test_backtest.py 17 tests 全绿（snapshot 确定性/不可覆盖/tamper 拒绝/actuals 校验/metrics 重算/accuracy hash-linked/accuracy→confidence 消费/伪造灵敏度拒绝/swap hash 拒绝/legacy engine 拒绝）；accuracy record → historical_accuracy_records → run_forecast → confidence.historical_accuracy 消费链已通。
- drift verdict: **already_satisfied**——既有能力在当前 triplet 全绿，无需产品修复。
- 修复：test-only 重验——新 `tests/test_zr708_backtest_reverify.py` 钉死关键契约（snapshot 不可变/accuracy 消费链/四层 hash），作为重验证据存档。
