# ZR-713 RED 探针证据

- 日期：2026-08-23
- 探针：scripts/revenue_backtest.py 有 create_snapshot/validate_snapshot/validate_actuals/evaluate_snapshot 单窗口基础设施（as-of 校验：actuals_as_of >= snapshot_as_of，snapshot 四层字段 identity）；grep rolling scripts → 零命中。
- drift verdict: `still_missing`——rolling-origin 多窗口引擎、严格 as-of 无 future actual 泄漏、三层分层、cap 触发零实现。
- 修复：新 `scripts/rolling_backtest.py`（run_rolling_backtest：逐窗口 as-of 截断 + company/segment/mine-volume 三层 + 四层 hash + 窗口不足 cap）+ 测试钉死。
