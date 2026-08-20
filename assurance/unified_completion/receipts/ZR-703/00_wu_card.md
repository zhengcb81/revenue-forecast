# ZR-703 工作单元卡（preflight）— F1：schema 文档/注释漂移清理 + 迁移 allowlist 一致性

- 领取时间：2026-08-20T18:15Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-703`，ZR-502 accepted + closure→ZR-503（phase=F_revenue_mining）；锁 ZR-503（owner=zr703-implementer）。
- 依赖：ZR-702（✅ schema 真源 + generator 闭环）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F1 第三卡（REV-01/03 收尾）：**constants/validator/linter/generator/docs/help/fixtures 一致**——"3.6 只在 migration allowlist"。现状：`FORECAST_SCHEMA_VERSION="3.7"`（contracts/constants.py:16），`SUPPORTED_FORECAST_SCHEMA_VERSIONS={3.4, 3.6, 3.7}`，但 generate_input_template.py / fix_hashes.py / lint_input.py 的 docstring/注释/CLI help 仍硬编码"schema 3.6"——与真源常量 3.7 不一致（REV-01/03 "docs 一致"缺口）；SUPPORTED_FORECAST_SCHEMA_VERSIONS 与 schema_compatibility.py 的迁移表（COMPATIBLE_VERSIONS）需要验证一致（3.4 是否仍在有效迁移路径上）。
2. **production entrypoint 是什么？** scripts/ 文档/注释层（docstring、CLI argparse help、README）——产品逻辑不变，只清理文档漂移。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 文档 3.6 硬编码与 FORECAST_SCHEMA_VERSION 3.7 不一致**：generate_input_template.py:1/41/238、fix_hashes.py:1、lint_input.py:1 的注释/docstring 仍说"3.6"。
   - **G2 SUPPORTED_FORECAST_SCHEMA_VERSIONS 含 3.4——与 schema_compatibility COMPATIBLE_VERSIONS 一致吗？** 3.4 在哪条迁移路径上？验证。
   - **G3 generator 输出 schema_version == FORECAST_SCHEMA_VERSION 无独立钉死测试**（702 测试覆盖 generator 闭环但未断言 schema_version 字段）。
4. **允许改哪些文件？** revenue：scripts/generate_input_template.py（注释改常量引用）、scripts/fix_hashes.py、scripts/lint_input.py（注释改引用）+ schema_compatibility.py（若有不一致）+ 新增测试 `tests/test_zr703_schema_drift_cleanup.py`（C1 注释漂移清理 + C2 迁移 allowlist 一致性 + C3 generator 输出 schema_version == FORECAST_SCHEMA_VERSION）；revenue receipts/ZR-703/**。禁止：改产品逻辑语义（常量值本身、validator 语义）、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-704（draft/formal 互换/故障注入）。本卡不做：publication/recovery 故障注入（ZR-704/705）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-502 accepted（closure.next=ZR-503）。
- [x] triplet 冻结：revenue（ZR-502 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：FORECAST_SCHEMA_VERSION="3.7"，但 5 处注释/docstring 硬编码"3.6"；SUPPORTED_FORECAST_SCHEMA_VERSIONS={3.4,3.6,3.7}；schema_compatibility.COMPATIBLE_VERSIONS 含 3.4/3.6/3.7。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（注释清理 + 迁移一致性 + generator schema_version 测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 注释漂移清理（杀 G1，REV-01 文档一致）**：generate_input_template.py / fix_hashes.py / lint_input.py 的 docstring/CLI help 中"schema 3.6"替换为引用 `FORECAST_SCHEMA_VERSION` 动态值（import + f-string 或直接说"schema {version}"），使注释随常量漂移自动更新；测试 grep "schema 3.6" 在注释中不再出现。
  - **C2 迁移 allowlist 一致性（杀 G2）**：`SUPPORTED_FORECAST_SCHEMA_VERSIONS` 中每个版本在 `schema_compatibility.COMPATIBLE_VERSIONS` 中有 ≥1 条正向迁移路径（非孤立项）；`FORECAST_SCHEMA_VERSION` 本身也在其中；测试断言。
  - **C3 generator 输出 schema_version 钉死（杀 G3）**：`build_template()["schema_version"] == FORECAST_SCHEMA_VERSION`；test filler 填充后跑 `prepare_forecast(mode="draft")` 的结果中 `result["schema_version"] == FORECAST_SCHEMA_VERSION`；单独测试钉死。
  - 质量门：revenue 全量 tests/ 无回归；ruff clean；tools 复杂度 ratchet 绿；skill-sync 前置。
- **Stop conditions / handoff**：改常量值本身、改 validator 语义、真实 catalog 写、下载、LLM → 立即停止。

## Annex：文档漂移清理清单

| 文件 | 行 | 现状（3.6） | 修后 |
|---|---|---|---|
| generate_input_template.py | 1/41/238 | "schema 3.6" | "schema {FORECAST_SCHEMA_VERSION}" |
| fix_hashes.py | 1 | "schema 3.6" | "schema {version}" |
| lint_input.py | 1 | "schema 3.6" | "schema {version}" |
| schema_compatibility.py | 33-34 | 注释 | 3.6 只在 migration allowlist（保留） |
