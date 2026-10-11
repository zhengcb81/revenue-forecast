# W07-RF-MODEL 技术发现

## 原生接口（只读消费，未改）
- `revenue_core.run_forecast(data, mode="draft")`：全程显式 draft，不产 publication receipt。draft 的 receipt gate_ids 与 `validate_published_forecast` 不匹配属预期（后者面向 formal），故工具不调 formal 校验器，只读 result。
- `research.input_quantities.convert_input_quantity`：同族缩放（usd_million→usd_thousand）保经济金额；跨币种/跨族（usd→rmb、percent→usd_million）抛 ForecastInputError "incompatible unit conversion"。
- `research_support_diagnostics.build_support_diagnostics` / CLI：返回 `economic-support-diagnostics/1`，按 segment/year/scenario 报 supported/conditional/unsupported，`economic_truth_inferred=false`。
- `contracts.period_flow.period_flow_months`：跨日历月数手算。越界/倒序窗口在 run_forecast 里拒（"must lie within the FY window" / "period_start before period_end"）。
- `research.timing_bridge.build_quarter_delay_bridge`：共用 joint stress，一次传播；`revenue_constraints` sum_cap 固定跨场景会触 "scenario ordering" 拒。

## 各类边界（手算 vs 引擎逐类相符）
- M01 unit_sales: 10×5=50, 12×5=60；缩放不改金额。
- M02 subscription_arr_bridge: 2026=105, 2027=136.25（closing ARR 125/162.5 ≠ 收入）。缺 new_arr → 拒，非零补。
- M03 commercial_launch: min(1000×0.1,80)×0.5×2=80；min(1200×0.2,300)×1×2=480。0 产能→有限 0；负产能拒（bounds [0,inf]）。
- M05 zero-base: base_revenue=0 → cagr=None（非 0、非错）。
- M06 quarter-delay: Δ2026=-20, Δ2027=+15, Σ=-5（25% 注销，一次施加）。固定共享封顶跨场景 → 拒（scenario ordering），不强行重排。
- M07 target: annual_period 可比→comparison_value 保留；run_rate_at_period_end 无转换 → 拒（"requires explicit annual recognized revenue conversion"），不冒充当年。
- M08 calibrated_document: Segment A/2026 supported，A/2027 与 B/2026 unsupported（单格校准不推定其余）；observed_range=None → unverified，null 保持。

## 工具层修复（非 core 缺陷）
节点 A 行为 RED 的 4 处全在新工具 wrapper/构造层，引擎数学逐类匹配：
1. M01-C 打包 bug（driver 是单对 [in,eng]，误当对列表迭代）。
2. M04-L 观察错字段（应读 period_flow_months，非 revenue）。
3. M06-C 构造错（需先 build_quarter_delay_bridge 再加固定共享封顶，才触 ordering 拒）。
4. M02-C 过窄理由串（改为断言"真合同拒 + 非空理由"，不硬绑引擎措辞）。
均不越界修 scripts/tests；无 ROOT core 修复请求。

## 独立性保证
oracle.py 只从 drivers 手算，不 import/call revenue_core 或 convert_input_quantity。测试用正则查 import 行 + 调用点（不误伤 docstring 散文）。喂错误结果必 FAIL；未执行永不 PASS。
