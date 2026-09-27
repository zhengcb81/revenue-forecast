# ZR-602 RED 探针证据（drift_classified → red_proved）

- 日期：2026-08-21
- 探针命令与结果（全部在 revenue-forecast CWD，base python）：

## P1：resource≠reserve 语义隔离机制已存在（待钉死）

```
C:\Miniconda\python.exe -c "…calculate_model_path('resource', 0, ids, params, YEARS, 'base') 注入 opening_reserves…"
→ ForecastInputError: unsupported drivers for resource: opening_reserves
C:\Miniconda\python.exe -c "…注入 saleable_volume 到 reserve_depletion…"
→ ForecastInputError: unsupported drivers for reserve_depletion: saleable_volume
```

- 机制位置：`scripts/forecast/segments.py:53-54`（`missing = required - driver_ids` / `extra = driver_ids - allowed`，`require(not extra, "unsupported drivers…")`）。
- 判定：G1 机制正确、零产品缺口；仅缺"语义不可互换"的钉死测试与 MODEL_SPECS 词汇不相交断言。

## P2：basis 元数据完全缺失（真实产品缺口）

```
grep ownership|consolidat|reporting_standard|measurement_date|basis scripts/*.py → 零命中（仅 time_basis 无关项）
schema_fields.PARAMETER_REQUIRED = (parameter_id, kind, value, unit, period, definition, source_ids) → 无 basis 键
document.py validate_parameters → unit/period/definition 仅要求非空字符串；无 basis 结构校验
generate_input_template add_parameter → 无 basis 键
```

- 判定：G2 真实缺口——asset fact 参数无法声明"100%/权益/并表、报告标准、measurement date"；携带半成品 basis 也不会被拒。需修复：constants 词汇 + document.py basis 键完整性门 + asset fact 族驱动参数 basis 必填。

## P3：单位一致性缺失（真实产品缺口，基础版）

```
unit 值：make_parameters 全 "test"；document.py 仅 require(unit 非空 str)；无一致性/归一逻辑
```

- 判定：G3 真实缺口——asset fact 族驱动单位漂移（kt vs t）无一致性门。本卡只做一致性门 + 显式前缀枚举；换算表归 ZR-610 会计 ADR（已与 ZR-610 卡片边界对齐："冻结通用矿业数据、单位…ADR"）。

## drift verdict

- `still_missing`：G2/G3 需产品修复（探针驱动）；G1 机制已存在，test 钉死。
- 修复边界：constants.py（加性词汇）、document.py（basis 完整性 + asset fact 族 basis 必填）、segments.py（unit 一致性门）、tests/test_models.py make_parameters（加性 basis 支持）；不动模型公式语义、不动 ModelSpec 契约、不实现换算表。
