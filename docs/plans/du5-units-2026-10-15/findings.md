# 调查记录

先读取construction_card.md中的真实现状；标明已复现/静态假说/已有正确行为。不能把准备文档当已完成实现。用户资料处理授权沿用，本卡0供应商调用，不增加许可JSON。

## A 节点调查（2026-10-15）

### 实际调用面（函数签名与调用方）

- `scripts/research/input_quantities.py`：`convert_input_quantity(value, *, input_unit, engine_unit)`、`validate_input_quantity_record(record, *, field)`、`build_sensitivity_test(*, parameter_id, value, input_unit, shock_semantics, name=None)`；三份平行手写表 `_UNIT_ALIASES/_UNIT_FAMILY/_UNIT_SCALE`，`_SHOCK_SEMANTICS` 再枚举货币拼写（usd/rmb 6 个，无 HKD）。
- `scripts/analysis/sensitivity.py::calculate_sensitivities` 是唯一实际 consumer：只核对 `engine_value == shock_value` 数值相等 + `validate_input_quantity_record` 重算，从不核对记录单位与真实 parameter 单位。
- 参数真实单位绑定：`contracts/document.py` 要求 monetary 维度 parameter `currency == data["currency"]`、`scale == data["unit"]`（如 "USD"/"million"、"CNY"/"亿"）。非 monetary 参数不带 currency。
- 其他调用方：`tools/model_generalization_matrix/native.py`（convert_input_quantity_strict = convert + validate）、bootstrap 透传、W07/W08 组合测试；`tests/test_input_semantics_e2e.py`（只读，percent 相对 shock 打在 revenue 维度参数上，必须继续通过）。

### 已复现缺陷（真实 calculate_sensitivities/run_forecast 路径反例，非静态推测）

1. 自洽 USD 记录配 HKD 参数（同数字5）直接进入计算：`run_forecast` 接受，shock_value=5 打在 HKD million 参数上（A 节点探针 H1）。RED 测试 `test_self_consistent_usd_record_on_hkd_parameter_is_rejected`。
2. 自洽记录尺度与参数尺度不符（usd_thousand 记录打在 USD million 参数上）同样被接受，1000 倍错位静默通过（探针 H2）。RED 测试 `test_self_consistent_record_with_wrong_scale_is_rejected`。
3. 记录 `conversion`（因子血统）文本可篡改不被发现：`validate_input_quantity_record` 只要求非空字符串，不重算比对（RED 子测试 conversion）。

### 已有正确行为（正控，保留不虚报缺陷）

- pp additive 打在金额维度参数被现有入口拒绝（percentage_point requires ratio dimension）。
- usd_million→rmb_million 跨币在 convert 层拒绝（"incompatible unit conversion"）；share↔money、money↔count 家族混用拒绝；伪造 engine_value 被重算拒绝。
- percent 相对 shock 打在 revenue 维度参数正常通过（tests/test_input_semantics_e2e.py 冻结行为，requested 104.5/115.5）。
- 旧 USD/RMB/share/count 记录与旧 builder 默认输出逐字节冻结（LegacyFreezeTests 内嵌样例，含 conversion 文本）。

### A 节点 RED 收据

`receipts/red-first-behavior.json`（50 failed / 94 passed；真实语义 RED，含 HKD 词汇缺失、跨币拒绝原因不符、参数单位核对缺失、engine_unit 真转换缺失；冻结正控通过）。W08 更新：C01-HKD-C 拒绝原因改跨币、新增 C01-HKD-L（5十亿=5000百万正控）与 C01-UNK-C（wan_yuan 未知拼写反例），原跨币场景/组/未知拒绝保留。

### 设计决定（供 B/C 执行）

- 有限 Currency×Scale 推导：currency 别名 usd/rmb/cny(→rmb)/hkd；尺度 unit(元)/thousand(千)/10k(万/wan)/million(百万)/100m(亿/yi)/billion(十亿)。规范名 `{cur}_{scale}`，旧规范名全部保留。无币种"万元/wan_yuan/亿"不进词汇表（unknown/error，不默认 RMB）；参数层 scale "万"/"亿" 由 parameter.currency 显式上下文解析。
- consumer 共用 helper `validate_input_quantity_for_parameter(record, *, parameter, shock_type, field)`：重算 + shock 语义（percent/pp/bp=share-of-total，absolute=money/count 严格分开）+ dimension（money↔revenue/monetary_balance/backlog；monetary-per-unit 明确诊断不剥分母；count↔quantity/activity/coverage_units）+ currency family + scale 核对；参数 currency/scale 无法解释给明确诊断。
- `build_sensitivity_test` 增可选 `engine_unit`：缺省旧输出逐字节不变；显式传入真转换（share 目标限 ratio/basis_point 引擎契约单位），shock_value 取转换值进入 revenue delta。
- `validate_input_quantity_record` 增 conversion 文本精确重算比对（旧记录 conversion 由旧代码生成，格式保持逐字节一致，重算语义不变）。
