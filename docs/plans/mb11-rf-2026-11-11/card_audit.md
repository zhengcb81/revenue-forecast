# MB-RF 施工卡逐条审计（2026-11-12）

审计对象：`company-wiki/docs/plans/module-boundaries-2026-11-11/harness_lanes/MB-RF.md`
代码基线：`6341759b`；B2 代码 tip：`d368eff6`；分支 `codex/mb11-rf`。
结论：**B2 全部满足；整卡 A/B/C 其余项未全面完成，不能把本分支当作整卡交付。**

## 1. 逐条状态

| 卡片要求 | 状态 | 证据 / 缺口 |
|---|---|---|
| A0-1 为 compare/scope/publication 公开合同建立失败或已满足证据 | PARTIAL | compare/publication 已由 B1 并入 main（`e060a8607`、`058be4fd6`、`6341759b9`）；scope/subject/verified-compare 的 RED 与实现见 B2（`b2_scope_red.log`、`tests/rf_verified_scope/`）。publication 的 B2 之外合同未在本轮重证。 |
| A0-2 当前回归入口 + 参考分支反例 | PARTIAL | 当前入口均已跑（`test_report_catalog_rf_job_import`、`test_rf_job_concurrency`、`test_rf_job_recovery`、`test_rf_job_boundary_regression`、`test_decoupled_source_port`、`test_d4_narrative_consumption_port`）；`tests/b37_publication_sources`、compare、deployment、catalog 均通过。`tests/b37_scope_binding` 在本工区不存在（候选私有 fixture），未迁移；`tests/b34_publication`/`tests/b35_lineage` 另行运行 129 passed / 1 failed（失败用例不引用 B2 模块，见 §3）。 |
| A0-3 旧 job facade / rf-input-prep 不整体并入 | NO_CHANGE_PROVEN | 未改 `rf_job_facade.py`、未并入 `rf-input-prep-01` 的 118 项研究产物；B2 未新增第二套 job/reader。 |
| A0-4 四个 assurance 生成物不写、旧失败保留 | NO_CHANGE_PROVEN | `git diff 6341759b..HEAD` 不含 `assurance/runs/{daily_alert.jsonl,monthly_manifest.json,weekly_alert.jsonl,weekly_manifest.json}`。 |
| A0-5 rf-impl / `3b00b938` 原型不建第二 reader | NO_CHANGE_PROVEN | B2 未新增 reader，只注入公开 subject port；未改 CWP/StockWiki。 |
| B2-1 公开 DTO/reader，禁止 catalog 私有面 | DONE | 四模块只经 `get_report/get_run/get_source_snapshot`；`PublicOnlyCatalog` + AST 测试；无 sqlite/StockWiki/CWP 导入。 |
| B2-2 准则/财年/多分部 golden，显式绑定，无默认 | DONE | 8 组 golden（IFRS/US GAAP × 06-30/12-31 × 1/3 分部）、24 分部、H1、600 期；缺字段/日历负例。 |
| B2-3 缺源/重复源/身份/期次/冲突的稳定语义 | DONE | 命名错误码与负例见 `test_negative_semantics.py`。 |
| B2-4 保留 `import-rf-job`、完整结果、无任意截断 | DONE | `report_catalog_identity_cli.py` 零 diff；help/源码回归；600 期 append、>1MiB 完整响应；compare 64KiB 与 owner artifact bound 均为既有预算。 |
| B2-5 定向通过 + 受影响回归 + 独审绑定 tip + handoff | DONE | 57 passed；选定 313 例 309 passed/1 failed/3 skipped；三轮审查最终绑定 `d368eff6`；handoff/review 已提交。 |
| 全卡共用规则：列活动入口/逻辑模块/公开面/状态 owner/依赖方向，含兼容/退休分类 | GAP | 未形成整卡运行时入口清单；本审计只给出 B2 切片归属。 |
| A/B/C-1 交付闭包：canary 不依赖 CWP SQLite/schema/DAG，未使用则移出交付/退休 | GAP | `scripts/processed_artifact_canary.py` 仍 `import sqlite3`、读 `catalog.sqlite3`，且 `installation_manifest.installable_files()` 仍把它列为可安装文件；除自身与复杂度 ratchet 外无调用者。 |
| A/B/C-2 计算/研究/报告职责：report 直接消费 leaf，core 编排调用 report | GAP | `revenue_report.py` 仍 `from revenue_core import (...)`；`revenue_core.py:442` 运行时 `from revenue_report import validate_published_forecast`；`revenue_publication.py`、`schema_compatibility.py` 也从 core 导入。 |
| A/B/C-3 来源边界：无 CWP/FF 包、不可读上游 DB 时 public commands 仍可 prepare/read | PARTIAL | `test_decoupled_source_port.py` 通过，但它 patch 了 `reader.subprocess.run`/`prepare._run_filing_fetch` 等私有 helper，不满足卡片“只通过 public fixture、不能 patch 上游私有 helper”的严格口径；未做无 CWP 包 + 不可读 DB 的子进程公开入口验证。 |
| A/B/C-4 历史 admission：B34 profile 显式版本兼容、默认路径无 CWP 内部布局 | PARTIAL | `tests/b34_publication`/`b35_lineage` 有覆盖（129 passed / 1 failed，失败不引用 B2 模块）；未单独写“默认路径无 CWP 布局”的合同测试，也未在 handoff 中明确 profile 兼容证据。 |
| A/B/C-5 作业/目录：code root 与 data root 分开，只读不建库，恢复不重算 | PARTIAL | `test_rf_job_*`、catalog/recovery 测试通过；B2 scope state 已用独立 `--data-root`；未形成整卡 code/data root 的集中证据。 |
| A/B/C-6 安装和独审：canonical installer、临时目标、空 cwd、不部署全局 | PARTIAL | 安装测试存在 `tools/tests/test_sync_installations.py`、`test_g3_skill_package.py`、`test_g5_selective_install.py`、`test_architecture_runtime_manifest.py`，本轮未运行；未做临时 destination 的实际安装/入口验证。 |
| 出口：模型/研究 leaf、runtime 副作用、report/catalog/jobs、source adapters 边界清楚；越层工具消失或公开委托；历史 profile 隔离有证据；安装/兼容/公开端口通过 | NOT MET | 上述 GAP/PARTIAL 未关闭。 |
| 并线交接：作者交分支 + 精确 diff + 包级测试 + 独审绑定 tip | DONE | 分支已推送；B2 代码 tip `d368eff6`，文档 tip `32f55253`；未合并 main。 |
| 不写其他 owner 仓 / Dashboard release / 生产报告 / 全局 skills | DONE | 未改 CWP/StockWiki/Dashboard；未部署全局 skills；未重跑预测。 |

## 2. 参考测试与文件名核对

- `tests/b37_scope_binding/`：本工区不存在；候选版本依赖 StockWiki 私有 fixture 与固定形状，B2 未迁移，改用 `tests/rf_verified_scope/` 的公开泛化合同。
- `tests/b37_publication_sources/`：存在并通过。
- `tests/b34_publication/`、`tests/b35_lineage/`：存在；本轮运行 **129 passed、1 failed、31 subtests passed**。失败为 `tests/b34_publication/test_native_cli.py::test_two_management_processes_replay_then_current_stock_revocation_refuses`（`identity_not_resolved`），该用例不导入任何 B2 新模块，`report_catalog_identity_resolver.py`/`report_catalog_identity_cli.py` 相对基线零 diff；归为既有/环境问题，未冒充通过。
- `tests/test_module_boundary_closure.py`：不存在（卡片证明库提到的文件名），本轮未新建占位测试；若继续整卡，应以它承载 canary/report-core/source/profile/install 的闭包证据。
- `AGENTS.md`：本工区不存在（只有 `agents/` 目录），开工时无可读的 AGENTS 文件。

## 3. 整卡未完成项的建议顺序

1. **Canary 退休**：确认无调用者后把 `scripts/processed_artifact_canary.py` 加入 `RETIRED_RUNTIME_FILES`，保留源文件作历史审查资料；补安装闭包测试。
2. **report/core 解耦**：把 `ENGINE_VERSION`、`build_workflow_compliance_receipt` 移到 leaf（`contracts.constants` / 新 `contracts.workflow_receipt`），`revenue_report`/`revenue_publication`/`schema_compatibility` 改从 leaf 导入，`revenue_core` 保留 re-export；core 仅保留运行时调用 report。
3. **来源边界严格测试**：无 CWP/FF 包、不可读上游 DB、公开 reader command，子进程跑 `source_preparation` 公开入口；失败不扫描邻仓目录；不 patch 私有 helper。
4. **历史 profile 证据**：补默认路径无 CWP 布局依赖的合同测试，明确 B34 v2 profile 的 retained 绝对路径兼容正例与缺失证据反例。
5. **安装隔离**：在临时 destination + 空 cwd 跑 `sync_installations.py --apply/--check`，验证 canary 不再分发、公开入口可启动。
6. **整卡闭包测试与独审**：新建 `tests/test_module_boundary_closure.py` 汇总上述证据，重跑整卡受影响回归并做最终独立审查。

## 4. 结论

- 对 **B2 切片**：完成、可交付、独审 PASS。
- 对 **整张 MB-RF 卡**：未全面完成；`canary`、`report/core`、严格来源边界、历史 profile 证据、安装隔离与整卡闭包测试仍需继续。
- 本文件不修改既有 B2 handoff 的代码结论；它是整卡审计，避免把 B2 切片误报为整卡交付。
