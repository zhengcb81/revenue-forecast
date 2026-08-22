# ZR-713 工作单元卡（preflight）— F2：紫金 rolling-origin 历史回测

- 领取时间：2026-08-23T08:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-713`，ZR-712 accepted + closure→ZR-713；锁 ZR-713。
- 依赖：ZR-708（✅ 不可变 snapshot/backtest）、ZR-712（✅ ConfidencePolicy 反博弈）。Registry 依赖列=ZR-708,ZR-712。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 紫金 rolling-origin 历史回测——严格 as-of 无 future actual（每次窗口只用该时点前已发布信息）；company/segment/mine-volume 三层分层；四层 immutable hashes；窗口不足无法形成回测时触发 rating cap（诚实降级而非假装）。
2. **production entrypoint 是什么？** 复用 `scripts/revenue_backtest.py`（create_snapshot/validate_snapshot/validate_actuals/evaluate_snapshot，as-of 校验已存在：actuals_as_of >= snapshot_as_of）+ 新 `scripts/rolling_backtest.py`（rolling-origin 引擎）。
3. **RED？** 探针：revenue_backtest 已有单窗口 snapshot/actuals 基础设施（as-of 校验）；rolling-origin 词汇零命中——多窗口滚动回测、严格 as-of 无泄漏、三层分层、cap 触发零实现。
4. **允许改哪些文件？** revenue：新 `scripts/rolling_backtest.py`、新 `tests/test_zr713_rolling_backtest.py`；revenue receipts/ZR-713/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-709（F2 合流：紫金五年预测用户旅程终验）。本卡不做：五年用户旅程终验（ZR-709）、阶段 G 真实 E2E。

## Acceptance criteria
- **C1 严格 as-of 无 future actual**：run_rolling_backtest 每次窗口仅使用 as-of 时点前已发布的 actuals——未来窗口的实际值绝不进入当前窗口评估（逐窗口断言：窗口 i 的 actuals 集 ⊆ 发布日 ≤ 窗口 i as-of 的 actuals）；违反泄漏 → ForecastInputError。
- **C2 三层分层**：company/segment/mine-volume 三层各自独立回测——company 层用 actual_company_revenue、segment 层用 actual_segment_revenue、mine-volume 层用 operating units（ZR-605 契约）驱动；每层输出独立 wape/metrics。
- **C3 四层 immutable hashes + cap**：每窗口输出 {snapshot_id, actuals_sha256, evaluation_sha256, record_sha256} 四层 hash 链（篡改拒绝）；窗口数 < 最小观测（默认 2）→ 无法形成回测 → 触发 cap（返回 capped=True + rating 上限提示），不伪造 metrics。
