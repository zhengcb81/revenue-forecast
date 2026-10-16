# DU5-RF-UNITS 独立施工计划

状态：DONE；2026-10-15。工作目录 `C:/Users/郑曾波/Projects/revenue-forecast-du5-units`。

分支 `codex/du5-rf-units-20261015`；源码基线 `090a63109a62507a23adcaa774cf65021e7c4614`；仅自己的文档seed额外提交。

先读 [施工卡](construction_card.md)、[接口与交接](INTERFACES.md)；两者给出完整范围、禁止重叠路径和验收。

## A：实际问题、接口和TDD

**Status:** done（2026-10-15）

读完 input_quantities/sensitivity/W08/调用面并冻结旧行为；确认三处真实缺陷（自洽USD记录配HKD参数、尺度错位记录、conversion因子文本可篡改）经 run_forecast 真实路径复现；先写真实行为 RED（receipts/red-first-behavior.json）。

## B：共同根因实现与集中回归

**Status:** done（2026-10-15）

Currency×Scale 唯一责任层（USD/RMB含CNY别名/HKD × 元/千/万/百万/亿/十亿）落地，build_sensitivity_test 增可选 engine_unit 真转换，consumer 经 validate_input_quantity_for_parameter 核对真实 parameter 单位。集中回归 216 passed + smoke 416 passed；ruff/mypy 干净；zr804 三个安装副本失败为稀疏工作树缺目录的环境问题，照实保留。

## C：公开入口E2E、恢复与交付

**Status:** done（2026-10-15）

run_e2e.py 走公开 CLI --validate-only 与 run_forecast 正式路径：7.25亿=725百万、5十亿=5000百万及反向独立手算一致，converted shock 进入最终 revenue delta（+725），同数字不同币种拒绝、记录重算篡改拒绝、旧USD/RMB不回归；sentinel/registry 隔离恢复，temp 全删（receipts/e2e-run.json、e2e-cleanup.json）。交付 references/money-unit-conversion.md、handoff.md/json；正常 commit 后 STOP。

## Next Step

ROOT 接收 handoff 后再将本能力放入原三/新三预测 E2E；本卡通过不等于预测经济质量通过。
