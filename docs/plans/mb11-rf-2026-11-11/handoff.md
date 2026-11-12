# MB-RF 整卡交付交接

> 范围：MB-RF 施工卡的 A0、B2 与 A/B/C 1–6。逐条状态与证据见 `card_audit.md`；运行时入口/模块/公开面/状态 owner/依赖方向见 `runtime_inventory.md`。本交接不声称 ROOT 已合并 `main`。

## 1. 基线与交付

- 代码基线：RF `main` / `origin/main` = `6341759b9cdfd13e8aa7d51d5c755e361046da0c`。
- 整卡最终代码 tip：`ec2e2f2e79c44ec6075e3a5bdb172b5f0c54b70a`。
- 提交链：`940e05b4`（B2 公开模块）→ `2ec16368`（B2 审查修复）→ `d368eff6`（B2 测试锁）→ `326149cd`（canary/report-core 整卡改造）→ `9404984d`（来源/安装证据强化）→ `ec2e2f2e`（闭包测试去重；仅测试文件）。
- 分支：`codex/mb11-rf`；已推送 `origin/codex/mb11-rf`；目标主线 RF `main`；未合并主线。
- 产品/测试改动（相对基线）：
  - 新增：`scripts/report_catalog_subject_resolver.py`、`report_catalog_scope_binding.py`、`report_catalog_verified_compare.py`、`report_catalog_verified_compare_cli.py`、`scripts/contracts/workflow_receipt.py`、`tests/rf_verified_scope/`、`tests/test_module_boundary_closure.py`。
  - 修改：`scripts/contracts/constants.py`（`ENGINE_VERSION`）、`scripts/installation_manifest.py`（canary 退休）、`scripts/revenue_core.py`（re-export/回调）、`scripts/revenue_report.py`（改 leaf 导入）、`scripts/revenue_publication.py`、`scripts/schema_compatibility.py`（改 leaf 导入）、`scripts/revenue_forecast.py`（修正 pure/zero-IO 文案）。
  - 未改：`report_catalog.py`、`report_catalog_compare*.py`、`report_catalog_identity_cli.py`、`report_catalog_rf_job_import.py`、CWP/StockWiki/Dashboard、`assurance/runs/*`、全局 skills。

## 2. 卡片要求逐项

| ID | 要求 | 根因/先红 | 归属与兼容 | 最终证明 |
|---|---|---|---|---|
| RF-A0 | 收敛旧 release 差额；保留 main durable job/recovery/source ports；不合旧 facade/研究产物 | 候选整树与 main 分叉；scope 候选私调私有面 | 仅接 19 路径中仍属当前合同的部分；B1 compare/publication 已在 main | `card_audit.md` A0 行；`git diff` 不含旧 facade/118 研究产物/assurance |
| RF-B2-1 | 公开 DTO/reader，禁止 catalog 私有面 | 候选 import `_clean_id/_json/_index/_exact_report/_public_report/_read_json/_compare_pair/_identity_reasons` | RF owner 新增模块；只经 `get_report/get_run/get_source_snapshot`；既有协议零改动 | `test_public_contract.py`；`PublicOnlyCatalog` + AST；`b2_scope_red.log` |
| RF-B2-2 | IFRS/US GAAP、06-30/12-31、多分部 golden；显式绑定无默认 | 候选固定 IFRS/12-31/单分部/FY-only | 公开 DTO 显式字段；FY 日历必须匹配 `period_end` | 8 组 golden、24 分部、H1、600 期；缺字段/日历负例 |
| RF-B2-3 | 缺源/重复源/身份/期次/冲突的稳定语义 | 候选依赖 SW 私有身份与固定形状 | RF 命名错误码；来源经公开 snapshot reader | `test_negative_semantics.py` 全错误码 |
| RF-B2-4 | 保留 `import-rf-job`、完整结果、无任意截断 | 候选删除该命令并加 512 行/1MiB 门槛 | `report_catalog_identity_cli.py` 零 diff；compare 64KiB / append owner artifact bound | `test_cli.py`；600 期 append；>1MiB 完整响应；job 导入回归 |
| RF-B2-5 | 定向 + 受影响回归 + 独审绑定 tip + handoff | — | 三轮 B2 审查绑定 `d368eff6` | 57 passed；313 例 309 passed/1 failed/3 skipped；`review.md` |
| RF-A/B/C-1 | canary 不依赖 CWP SQLite/schema/DAG；未使用则退休 | canary 仍 `import sqlite3` 且可安装 | 加入 `RETIRED_RUNTIME_FILES`；源文件保留 | `test_module_boundary_closure.py`：不可安装、无 runtime 引用、安装树不含 |
| RF-A/B/C-2 | report 直接消费 leaf；core 编排调用 report | report 仍 `from revenue_core import (...)`；core 运行时回调 report | `ENGINE_VERSION`/workflow receipt 移 leaf；core re-export 兼容 | `-S` 子进程 `core_loaded False`；AST 回调仅函数内；golden/schema/output 回归 |
| RF-A/B/C-3 | 无 CWP/FF 包、不可读上游 DB 时 public commands 仍可 prepare/read | 既有测试 patch 私有 helper，不满足严格口径 | 公开 `prepare_registered_source_result` + 真实 reader 子进程 | `-S` + 空 `PYTHONPATH`；不可读目录 config；邻库哨兵 atime/size/mtime/hash 不变；reader 仅 1 次；失败 `SourceVersionTransportError` |
| RF-A/B/C-4 | B34 profile 显式版本兼容；默认路径无 CWP 布局 | 只有路径/import 级证据 | 保留 v1 默认、v2 版本化；既有 b34/b35 真实正反例 | `publication_layout` v1/v2、默认 v1、v0 拒绝；无 sqlite/CWP 导入；b34/b35 回归 |
| RF-A/B/C-5 | code/data root 分开；只读不建库；恢复不重算 | 需集中证据 | `ReportCatalog` JSONL owner state；job recovery 既有测试 | closure：无 sqlite3、`.jsonl` 不建文件；`test_rf_job_recovery`/deployment |
| RF-A/B/C-6 | canonical installer、临时目标、空 cwd、不部署全局 | 原未做临时 destination | `sync_installations.py` 显式 destination | closure：apply/check JSON、零 drift、安装树含入口与新 leaf、不含 canary、`-S` 导入；tools 安装测试 20 passed |
| 全卡共用规则 | 活动入口/模块/公开面/owner/依赖方向/兼容退休清单 | — | — | `runtime_inventory.md` |
| 出口 | 边界清楚、越层工具消失/公开委托、profile 隔离有证据、安装/兼容/端口通过、独审无未修问题 | — | — | 见 §4/§5；整卡回归 561 passed/2 已知失败/3 skipped/31 subtests |

## 3. 公开接口变化

默认无既有协议变更；新增均为可加性：

- `report_catalog_subject_resolver`：`SubjectQuery`、`SubjectSnapshot`、`SubjectResolver`、`FrozenSubjectResolver`；fixture `rf-subject-snapshot-fixture/1`。
- `report_catalog_scope_binding`：`build_scope_binding`、`validate_scope_binding`、`ScopeBindingStore`、`list_scope_bindings`、`exact_scope_pair`；schema `rf-report-scope-binding/1`、`rf-report-scope-bindings/1`；state `<data-root>/artifacts/report_scope/verified_scope_bindings.jsonl`。
- `report_catalog_verified_compare`：`compare_verified_scope`；`rf-verified-scope-comparison/1`；请求增加 `left_binding_id`/`right_binding_id`。
- `report_catalog_verified_compare_cli`：`get-bindings` / `compare` / `append-binding`；`--data-root`、`--subject-fixture`、可选 `--owner-root`。
- `contracts/workflow_receipt.py`：`build_workflow_compliance_receipt` leaf；`revenue_core` 继续 re-export。
- `installation_manifest`：canary 进入 `RETIRED_RUNTIME_FILES`，不再分发。

ROOT 可直接用 `docs/plans/mb11-rf-2026-11-11/fixtures/subject-snapshot-example.json` 作为 `--subject-fixture` 样例；真实 StockWiki 组合由 ROOT 用公开 subject fixture/CLI 绑定。

## 4. 实际测试

环境：Windows，`C:/Miniconda/python`（Python 3.13.9），pytest 9.1.1；临时根 `C:/Temp/mb11*`，结束后删除。

| 命令 | 退出码 | pass/fail/skip | 耗时 | 日志 |
|---|---|---|---|---|
| `pytest tests/test_module_boundary_closure.py -q` | 0 | 14/0/0 | 9.32s | `full_card_closure.log`（本轮） |
| `pytest tests/rf_verified_scope -q` | 0 | 57/0/0 | 6.68s | `b2_scope_focused_final.log` |
| 整卡综合回归（closure + B2 + 卡片证明库 + report/publication + b34/b35 + source） | 1 | 561/2/3 + 31 subtests | 195.40s | `full_card_regression_final.log` / `full_card_junit_final.xml` |
| `pytest tools/tests/test_sync_installations.py tools/tests/test_g3_skill_package.py tools/tests/test_architecture_runtime_manifest.py -q` | 0 | 20/0/0 | 28.37s | 本轮终端记录 |

- 两项失败均为基线已复现、非本卡引入：
  1. `tests/test_single_owner_guard.py::test_subprocess_use_is_limited_to_contract_clients`：allowlist 缺 4 个既有 subprocess 脚本，HEAD 树同样失败。
  2. `tests/b34_publication/test_native_cli.py::test_two_management_processes_replay_then_current_stock_revocation_refuses`：`identity_not_resolved`；在基线 `6341759b` 的 `scripts/tests/delivery/config` 归档树上同样失败。
- 3 个 skip 为既有环境/合同 skip（Dashboard 合同目录、默认 catalog 跨 owner 链接、模型族输出固定）。
- Ruff（整卡改动文件）通过；mypy policy（`scripts/contracts/`、`schema_compatibility.py`、`filing_fetch_client.py`、`trust_anchor.py`、`company_wiki_narrative_contracts.py`）通过；pre-commit/pre-push smoke 12 passed。
- 未执行：整个 `tests/` 树（既有收集失败 `test_zr1008` 缺 `test_zr709`、`test_ca204`）；真实 CWP/StockWiki 生产组合；网络/模型/预测/收费调用。

## 5. 独立审查

- B2 三轮：agent-32545490（`940e05b4`）、agent-023442c1（`2ec16368`）、agent-deb118d7（`d368eff6`），均 PASS；修复提交 `2ec16368`、`d368eff6`。
- 整卡审查：agent-8079d52d 在 `326149cd` 给出 CHANGES_REQUESTED（handoff 未更新、inventory 缺失、来源/安装证据偏弱、zero-IO 文案）；本轮已修复并提交 `ec2e2f2e`，整卡复核结果见 `review.md`。
- 详细发现、修复与复核见 `review.md`；代码审查绑定 `ec2e2f2e`，本 handoff 为之后的文档提交。

## 6. 隔离与恢复

- 测试目录初始状态：每次运行前新建空的 `C:/Temp/mb11*` 短根；结束状态：只删除本次自建目录，最终无残留；仓内未留 pytest 临时产物。
- 未改生产原件/配置/既有 WIP；`assurance/runs/{daily_alert.jsonl,monthly_manifest.json,weekly_alert.jsonl,weekly_manifest.json}` 未写入；未部署全局 skills；未改 CWP/StockWiki/Dashboard。
- 业务网络调用 0、模型调用 0、费用 0/unknown；仅 Git fetch/push。
- 安装测试只写临时 destination；check 阶段 `written=[]`、`remaining_selected_drift=0`。

## 7. 安装/部署/CI/合并状态

- 安装/部署：未执行全局安装；临时 destination 安装/检查已在闭包测试中通过。
- CI：未运行远端 CI；本地 Ruff/mypy/pre-commit/pre-push smoke 通过。
- 合并：分支已推送，`main` 未合并；ROOT 接收后需在集成树重跑整卡回归并绑定 `ec2e2f2e`。
- ROOT 下一步命令：

```powershell
C:/Miniconda/python -B -X utf8 -m pytest tests/test_module_boundary_closure.py tests/rf_verified_scope tests/test_single_owner_guard.py tests/test_architecture_dependency_uses.py tests/test_decoupled_source_port.py tests/test_golden_behavior_lock.py tests/test_model_registry_contract.py tests/test_rf_job_boundary_regression.py tests/test_rf_job_recovery.py tests/test_rf_job_concurrency.py tests/test_report_catalog_rf_job_import.py tests/test_d4_narrative_consumption_port.py tests/test_report_catalog_compare.py tests/test_report_catalog_deployment.py tests/test_report_catalog.py tests/test_report_catalog_identity_resolver.py tests/b37_publication_sources tests/test_output_report.py tests/test_schema_compatibility.py tests/test_zr702_schema_source_of_truth.py tests/test_zr703_schema_drift_cleanup.py tests/test_publication_pipeline.py tests/test_publication_registry.py tests/b34_publication tests/b35_lineage tests/test_company_wiki_source_reader_v2.py tests/test_r1_source_boundary.py -q -p no:cacheprovider
```
