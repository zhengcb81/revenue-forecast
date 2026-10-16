# DU5-RF-UNITS 交接

分支 `codex/du5-rf-units-20261015`；基线 `090a63109a62507a23adcaa774cf65021e7c4614`；实现 commit `db33460b92f5f4c695b976124865f55b57e555a7`（实现）+ `41cbb53c3925b6ce5edad53b562000df7044292f`（独立审查修复与 registry 事件处置）。机器可读版本见 [handoff.json](handoff.json)。

## 交付了什么

单一金额单位描述（Currency×Scale）与真实参数单位一致性：

1. **单位唯一责任层** `scripts/research/input_quantities.py`：删除 `_UNIT_ALIASES/_UNIT_FAMILY/_UNIT_SCALE` 三份平行表与 `_SHOCK_SEMANTICS` 的货币拼写枚举，改为一个有限 Currency×Scale 描述推导（USD、RMB 含 CNY 同币别名、HKD；元/千/万/百万/亿/十亿）。旧规范名（usd_million、rmb_100m 等）与 `rf-input-quantity/1` 记录重算逐字节保持。
2. **可选 `engine_unit` 真转换**：`build_sensitivity_test(..., engine_unit=)` 显式传入时真换算到目标尺度（同币），shock_value 即引擎施加值，进入最终 revenue delta（E2E 证实 +725）；缺省沿旧输出不变。
3. **consumer 共用 helper** `validate_input_quantity_for_parameter`：`scripts/analysis/sensitivity.py` 仅调用它核对记录与真实 parameter 单位——shock 语义（relative/absolute 分离）、dimension（monetary-per-unit 明确诊断不剥分母）、currency family、scale 全部对齐 parameter 的 `currency`/`scale` 绑定；无法解释的参数单位给明确诊断，不猜测。
4. **W08**：`C01-HKD-C` 保留 case/金额/失败预期，拒绝原因从 unknown input_unit 改为跨币不兼容；新增 `C01-HKD-L`（5十亿=5000百万正控）与 `C01-UNK-C`（wan_yuan 真未知拼写反例）；`test_unwritten_unit_is_unknown_not_a_guessed_rate` 同步更新并补未知拼写控制。

## 已复现缺陷与正控（详见 findings.md）

- 缺陷：自洽 USD 记录配 HKD 参数可进入计算；尺度错位记录（1000 倍）静默通过；conversion 因子行可篡改。三者均在真实 `run_forecast`/`calculate_sensitivities` 路径先写 RED 复现。
- 正控（保留）：pp additive 对金额维度拒绝、usd↔rmb 跨币拒绝、伪造 engine_value 拒绝、percent 相对 shock 对 revenue 参数通过（104.5/115.5 冻结）。

## 收据

| 证据 | 路径 |
|---|---|
| 首个行为 RED（34 FAILED + 16 subTests = 50 failed/94 passed） | receipts/red-first-behavior.json |
| 最终集中回归 216 passed + smoke 416 passed + ruff/mypy | receipts/final-central.json |
| 公开入口 E2E 23 checks（含手算 7.25亿=725百万、5十亿=5000百万及反向） | receipts/e2e-run.json |
| 恢复/清理（sentinel、registry 隔离、默认 registry 不变、temp 全删） | receipts/e2e-cleanup.json |
| registry 事件存证与删除记录（见下） | receipts/registry-incident.json |

单位表与公开用法见 [../../references/money-unit-conversion.md](../../references/money-unit-conversion.md)。

## 独立审查与事件披露

独立审查 agent 发现一处高严重性问题并已修复：E2E 驱动最初只给 CLI 子进程重定向 `REVENUE_PUBLICATION_REGISTRY`，进程内 `run_forecast(mode="formal")`（含 A 节点探针）把 12 条链式条目写进了此前不存在的生产 registry `artifacts/registry/publications.jsonl`。处置：全部条目逐字节存证（receipts/registry-incident-removed.jsonl，sha256 `0a1e2cdc…`，均为本卡 synthetic 文档的发布行）后按卡片"新输出原先不存在则删除"删除；驱动现对进程内环境同样重定向并在清理收据中断言默认 registry 运行前后不变（`default_registry_untouched: true`）；修复后 E2E 重跑 23/23 绿。`production_writes=0` 按 INTERFACES 定义仅指生产原件/配置/AUTO；本 registry 事件不因此消失，已在此与 handoff.json known_limits 如实披露，请 ROOT 复核 `artifacts/registry` 缺席并决定是否需要额外处置。

审查同时复核通过：独占范围、设计约束 1-7（含基线源码逐字节冻结实测）、W08 case/金额/失败保留与新控制、集中回归/静态/手算数字全对。

## 接口变更

- `build_sensitivity_test` 新增可选关键字 `engine_unit`（缺省旧行为不变）。
- 新增 `research.input_quantities.validate_input_quantity_for_parameter(record, *, parameter, shock_type, field)`。
- `validate_input_quantity_record` 增加 conversion 文本精确重算比对（旧记录仍逐字节通过）。
- W08 `C01-HKD-C` 的 boundary 描述随拒绝原因一并更新为跨币边界（case ID、金额 7.8、失败预期保留；原"未知拼写"边界原文由新增的 `C01-UNK-C` 承接）。
- 其余函数签名、记录形状、schema 版本均未变。

## 未测/照实保留

- 稀疏工作树缺 `agents/claude/codex`/`e2e` 目录：`test_zr804` 安装副本 3 例失败（本卡前后一致，环境性）、ruff 的 e2e 目标未跑（scripts/tests/tools 干净）。
- 全仓慢 native 套件未跑（非本卡相关集）。
- 收据细节字段含本机临时目录绝对路径与 traceback 文本（非凭证、非原件绑定）。

ROOT 接收后按 handoff.json 的 root_integration_steps 处理；本单元卡通过不代表预测经济质量通过。
