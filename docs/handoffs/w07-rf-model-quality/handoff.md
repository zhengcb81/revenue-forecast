# W07-RF-MODEL 交接 — 原生模型组合压力测试包

- **Lane**: W07-RF-MODEL
- **状态**: COMPLETE
- **分支**: `codex/w07-rf-model-quality`  基线: `30ddae8ed2a457c418e63b182e7d8c9230fbf3ff`
- **工作目录**: `C:/Users/郑曾波/Projects/_harness_worktrees/w07/rf-model-quality`
- **source_truth_verified**: false  **economic_reasonableness**: not_evaluated

## 做了什么

新增可复用工具 `tools/model_generalization_matrix/`：对原生收入引擎的跨机制组合做**有限、可重复**的压力矩阵（M01–M08）。每类至少一个合法向量 + 一个反例/未知向量，共 **16 个输入**，每个都实际调用原生 draft 引擎（`run_forecast(mode="draft")`）或原生入口（`convert_input_quantity` / `build_support_diagnostics` / `period_flow_months`），并与**独立手算 oracle** 比对。

**不搭第二个预测引擎，不据合成测试宣布买方结论。** 合成向量只演示输入输出形状与数学边界。

## 独立 oracle（不从结果反推）

`oracle.py` 只用冻结 `drivers` + 文档公式/守恒式算期望，**不 import / 不调用**被测引擎。测试断言 oracle 模块无 `import revenue_core`、无 `run_forecast(`。被喂错误结果时用例必 FAIL；未执行的用例永不 PASS。期望与实测严格分列。

## 8 类组合结果（全绿）

| 类 | 组合 | 边界 | 结果 |
|---|---|---|---|
| M01 | quantity×price×currency/unit | 同维缩放不改经济金额；显式货币标签；混单位拒绝/显式转换 | PASS |
| M02 | ARR stock→recognition＋late/churn | closing ARR 非全年收入；缺驱动拒绝不零补 | PASS |
| M03 | capacity/demand/launch fraction | 需求受产能封顶；启动比例算一次；0 产能→有限 0 | PASS |
| M04 | dated control＋cross-FY partial window | 部分窗口按真实覆盖；越界窗口拒绝 | PASS |
| M05 | zero-base launch＋CAGR | 0 基数可算；CAGR undefined=null | PASS |
| M06 | shared shock＋joint scenarios | 共用 shock 传播一次守恒；强制 Low≤Base≤High 的固定共享封顶拒绝 | PASS |
| M07 | management target＋gross/net | 可比年度目标保留原值；run-rate 不冒充当年 | PASS |
| M08 | optional support＋segment/year/scenario | 按格支持；单格校准不推定其余；未知保持 null | PASS |

矩阵计数：total 16 / passed 11 / reject_ok 5 / failed 0 / errored 0 / not_run 0。

## 节点记录

- **A 定义与 TDD**：先冻结 8 类 CaseSpec + 独立 oracle 写入 `cases.py`。行为 RED 实测一次：16 例跑出 2 failed / 1 reject_mismatch / 1 error（M01-C 打包 bug、M04-L 观察错字段、M06-C 构造错、M02-C 过窄理由串）。**引擎数学本身逐类匹配手算 oracle** —— 4 处全是新工具 wrapper/构造层问题，非 core 缺陷，故不越界修、无 ROOT 请求。
- **B 实现与集中快测**：实现 `bootstrap/native/oracle/cases/runner/report/run`。集中快测 `python -B -m pytest -q tools/tests/test_w07_model_generalization.py` → **12 passed**（0.71s）。覆盖：oracle 不被错误结果欺骗、未知 null 不 0、native 异常记为 ERROR 不吞、cleanup 恢复 absent（含异常路径）、输入污染被捕、16 例/8 类结构、oracle 独立性。
- **C 离线 E2E**：`run.py --owned-root ABS --out-root ABS --e2e` → exit 0，一次跑完 16 输入。附真实 CLI 证据：合法 `--validate-only` rc=0 "valid"；拒绝样本 rc=2 "fiscal_year_end is not a valid month-day"（合同原因）；support CLI rc=0 输出 `economic-support-diagnostics/1`。全过程隔离临时目录 `.tmp/w07-<uuid8>`，最终 `restored_absent=true`；`readonly_unchanged=true`（scripts/tests 只读 SHA 保持）；固定 input 4 个 SHA 全 OK。residuals 空。

## 引擎版本

SKILL_VERSION 4.3.0，FORECAST_SCHEMA_VERSION 3.7。

## 交付物

- 工具：`tools/model_generalization_matrix/{__init__,bootstrap,oracle,native,cases,runner,report,run}.py` + `README.md`
- 快测：`tools/tests/test_w07_model_generalization.py`
- 报告 schema：`model-generalization-matrix/1`（`--out-root` 产 `model-generalization-matrix.{json,md}`）
- 本包证据：`docs/handoffs/w07-rf-model-quality/{matrix-e2e.json,matrix-e2e.md,handoff.json,handoff.md}`

## 成本与体积

真实 provider/LLM 调用 0，费用 0。持久体积约 198KB（含报告），远低于 8MiB 上限；scratch 峰值未计量填 null（未做峰值计量）。

## 给 ROOT

`root_next_action: receive/integrate`。无需 core 修复；工具可直接并线。完整报告是手动大节点，不入每次 commit/CI。
