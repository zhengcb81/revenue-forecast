# ZR-702 工作单元卡（preflight）— F1：schema 单一真源 + generator→linter→engine 闭环

- 领取时间：2026-08-19T22:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-702`，ZR-701 accepted + closure→ZR-702（phase=F_revenue_mining）；锁 ZR-702（owner=zr702-implementer）。
- 依赖：ZR-701（✅ prepare_forecast/draft 模式）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F1 第二卡：**schema 单一真源（REV-01/03）+ generator 有效（REV-02/04）**（traceability_and_acceptance：constants/validator/linter/generator/docs/help/fixtures 一致；generate→test filler→lint→validate_document→draft full run 一次通过；生产无 test filler）。现状：lint_input.py 本地硬编码 4 组字段元组（TOP_LEVEL/CAPTURE/CLAIM/PARAMETER_REQUIRED，line 28-77）——与 validator（contracts/document.py 分散的 require 调用）、generator（generate_input_template.py 模板）三处各自维护，漂移无 gate；generator→linter→validator→engine 全链无端到端一次通过测试。
2. **production entrypoint 是什么？** `scripts/lint_input.py`（静态预检）→ `scripts/generate_input_template.py`（模板骨架）→ `contracts/document.py validate_document`（契约验证）→ `scripts/revenue_forecast.py prepare_forecast(mode="draft")`（零写引擎，ZR-701）。真源目标：字段清单唯一定义 + 三消费方一致。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 schema 非单一真源（REV-01）**：linter 硬编码字段元组；validator/generator 各自维护同语义字段集；无一致性 gate。
   - **G2 无 generator 闭环（REV-02）**：generate→test filler→lint→validate_document→draft full run 一次通过无端到端测试。
   - **G3 生产无 test filler 无断言（REV-04）**：generator 模板输出的生产语义（FIXME 占位、无预填测试值）无钉死。
4. **允许改哪些文件？** revenue：新增 `scripts/schema_fields.py`（字段清单唯一真源）+ `scripts/lint_input.py`（改 import 真源，删本地硬编码）+ 新测试 `tests/test_zr702_schema_source_of_truth.py`；revenue receipts/ZR-702/**。禁止：改 validator 契约语义（contracts/document.py 只读对照）、改 generator 模板结构、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-703~706。本卡不做：publication/recovery 故障注入（ZR-704/705）、backtest/confidence（ZR-708+）、矿业层（F2）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-701 accepted（closure.next=ZR-702）。
- [x] triplet 冻结：revenue（ZR-701 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：lint_input.py:28-77 硬编码 4 组元组；无 schema_fields 模块；无 generator→engine 端到端测试；FORECAST_SCHEMA_VERSION 由 constants 导入（版本真源已单一，字段清单未单一）。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（schema_fields 真源 + linter 接线 + 闭环测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 单一真源（杀 G1，REV-01）**：新 `scripts/schema_fields.py` 定义 TOP_LEVEL_REQUIRED/CAPTURE_REQUIRED/CLAIM_REQUIRED/PARAMETER_REQUIRED（语义与现 linter 完全一致——纯搬迁零语义变化）；lint_input.py 从真源 import（删本地硬编码）；测试断言 linter 引用与真源同值。
  - **C2 三方一致（杀 G1 端，REV-03）**：generator 模板（build_template）填充后的文档含真源全部 TOP_LEVEL_REQUIRED 键；逐个删除必填键 → validate_document 拒绝（validator 与真源覆盖一致）；capture/claim/parameter 子形状同样对照（lint 与 validator 对同形状错误的可发现性）。
  - **C3 generator 闭环（杀 G2，REV-02）**：端到端测试：build_template → test filler 填充 FIXME → lint_input（0 findings）→ validate_document 通过 → prepare_forecast(mode="draft") 一次通过（零写）。
  - **C4 生产无 test filler（杀 G3，REV-04）**：build_template 原始输出（未填充）含 FIXME 占位且不含任何预填生产/测试值；lint 对未填充模板报 FIXME findings（生产流程不可能静默使用未填充模板）。
  - 质量门：revenue 全量 tests/ 无回归（477+ 基线 + 新增）；ruff clean；tools 复杂度 ratchet 绿；skill-sync 前置（scripts 改动）；mypy 基线不新增。
- **Stop conditions / handoff**：改 validator 契约语义、改 generator 模板结构、真实 catalog 写、下载、LLM → 立即停止。

## Annex：schema 真源判定矩阵

| 场景 | 期望 |
|---|---|
| lint_input 字段元组 | 来自 schema_fields（同值同对象语义） |
| generator 模板填充后文档 | 含全部 TOP_LEVEL_REQUIRED 键 |
| 删除任一必填键 | validate_document 拒绝 |
| generate→fill→lint→validate→draft | 全链一次通过（零写） |
| 未填充模板（FIXME 在） | lint 报 findings（不可静默用于生产） |
