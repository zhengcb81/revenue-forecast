# MB-RF B2 交付交接

> **范围声明**：本交接只覆盖 B2 切片（scope/subject/verified-compare）。整卡 A/B/C 的 canary、report/core、严格来源边界、历史 profile 证据、安装隔离与整卡闭包测试**未交付**，逐条状态见 `card_audit.md`。不得把本文件当作整张 MB-RF 卡已完成证明。

## 1. 基线与交付

- 代码基线：RF `main` / `origin/main` = `6341759b9cdfd13e8aa7d51d5c755e361046da0c`（B1 compare 与部署/来源回归已在主线）。
- 最终代码 tip：`d368eff6f8ce`（父 `2ec16368f9d1`，其上 `940e05b4cd82`）。
- 分支：`codex/mb11-rf`；已推送 `origin/codex/mb11-rf`。远端当前 tip 为后续交接文档提交 `d17be476`（仅 PWF/日志/本文件，不含产品改动）；代码审查仍绑定 `d368eff6`。pre-push 固定 smoke **12 passed**；未合并主线。
- 目标主线：RF `main`。ROOT 尚未接收/合并，本交接不声称 `MERGED`。
- 实际产品 diff（仅新增，未改任何既有生产模块）：

| 类型 | 路径 |
|---|---|
| 产品 | `scripts/report_catalog_subject_resolver.py` |
| 产品 | `scripts/report_catalog_scope_binding.py` |
| 产品 | `scripts/report_catalog_verified_compare.py` |
| 产品 | `scripts/report_catalog_verified_compare_cli.py` |
| 测试 | `tests/rf_verified_scope/{__init__.py,conftest.py,fixtures.py,test_public_contract.py,test_golden_contract.py,test_negative_semantics.py,test_cli.py}` |
| PWF/证据 | `docs/plans/mb11-rf-2026-11-11/{task_plan.md,findings.md,progress.md,review.md,handoff.md,handoff.json,b2_*.log,b2_*.xml}` |

`git diff 6341759b..d368eff6` 共 21 文件、+2205/-1；除 PWF 外全部为新增，`report_catalog.py`、`report_catalog_compare*.py`、`report_catalog_identity_cli.py`、`report_catalog_rf_job_import.py` 无 diff。

## 2. 卡片要求逐项

| ID | 要求 | 根因/先红 | 归属与兼容 | 最终证明 |
|---|---|---|---|---|
| RF-B2-1 | 公开 DTO/reader 暴露 scope/subject/verified-compare；调用方不得读 catalog 私有面 | 候选直接 import `_clean_id/_json/_index/_exact_report/_public_report/_read_json/_compare_pair/_identity_reasons` 并依赖 SW 私有 CLI/DB；当前主线无这四个入口（`b2_scope_red.log`：入口缺失 1 failed） | RF owner 新增公开模块；只经 `get_report/get_run/get_source_snapshot`；既有 catalog/compare 协议零改动 | `test_public_contract.py`：`PublicOnlyCatalog` 私有访问即断言失败；AST 检查无私有符号/邻库导入；`test_owner_modules_import_no_catalog_privates_or_neighbour_stores` |
| RF-B2-2 | Golden 覆盖 IFRS/US GAAP、06-30/12-31、多分部；期次/主体/scope/比较对象沿公开字段绑定；不得默认 IFRS/12-31/单分部 | 候选固定 `accounting_basis=="IFRS"`、`fiscal_year_end=="12-31"`、`len(segments)==1`、FY-only | RF owner 公开 DTO 显式字段；FY 坐标要求 `period_end` 月日=声明财年结束日；H1/Q 不受 FY 限制 | `test_golden_contract.py`：8 组准则×日历×分部、24 分部、H1、600 期；缺字段负例 |
| RF-B2-3 | 缺源/重复源/身份/期次不匹配/冲突 scope 的稳定结果或错误 | 候选依赖 SW 私有身份与固定形状，错误语义不可复用 | RF owner 命名错误码；来源经公开 snapshot reader 核对 | `test_negative_semantics.py`：`scope_source_missing`、`scope_duplicate_source`、`scope_evidence_invalid`、`scope_identity_mismatch`、`*_scope_coordinate_not_covered`、`scope_binding_conflict`、`scope_binding_stale`、`scope_binding_not_found`、`scope_period_calendar_mismatch`、`scope_anchor_mismatch`、`scope_store_invalid`、`scope_store_busy` |
| RF-B2-4 | 保留 `import-rf-job` 管理入口与 CLI 行为；完整结果、无任意行/字节截断 | 候选 CLI 会删除 `import-rf-job`；候选有 512 行/1MiB 等无预算依据门槛 | 未改 `report_catalog_identity_cli.py`；compare 保留已发布 64KiB 请求预算，append 证据用 owner 既有 `MAX_ARTIFACT_BYTES` | `test_cli.py`：help/源码断言 `import-rf-job`；600 期 append/回读；>1MiB 完整响应；`tests/test_report_catalog_rf_job_import.py` 在组合回归中通过 |
| RF-B2-5 | 定向通过后跑受影响回归一次；独立审查绑定最终 tip | — | 三轮只读审查，最终绑定 `d368eff6` | 定向 57 passed；选定组合 313 例 309 passed/1 failed/3 skipped；审查 PASS（见 `review.md`） |

整卡其他 A/B/C 项（canary 退休、report/core 解耦、严格来源边界、历史 profile 证据、安装隔离、整卡闭包测试）本轮**未交付**；逐条状态、证据与建议顺序见 `card_audit.md`。

## 3. 公开接口变化

默认无既有协议变更；以下均为**新增可选项/新模块**，不影响现有 `rf-report-catalog/1`、`rf-report-comparison/1`、`import-rf-job`：

- `report_catalog_subject_resolver`：`SubjectQuery`、`SubjectSnapshot`、`SubjectResolver` port、`FrozenSubjectResolver.from_public_fixture(path)`；fixture schema `rf-subject-snapshot-fixture/1`，snapshot schema `rf-report-subject-snapshot/1`。
- `report_catalog_scope_binding`：`build_scope_binding`、`validate_scope_binding`、`ScopeBindingStore`、`list_scope_bindings`、`exact_scope_pair`；binding schema `rf-report-scope-binding/1`，read schema `rf-report-scope-bindings/1`；state 路径 `<data-root>/artifacts/report_scope/verified_scope_bindings.jsonl`。
- `report_catalog_verified_compare`：`compare_verified_scope`；schema `rf-verified-scope-comparison/1`；请求在既有 4 字段上增加 `left_binding_id`/`right_binding_id`。
- `report_catalog_verified_compare_cli`：`get-bindings --report-id`、`compare`（stdin 请求）、`append-binding`（stdin 证据）；共享 `--data-root`、`--subject-fixture`，可选既有 `--owner-root`。

ROOT 消费所需的本地 fixture 入口：`tests/rf_verified_scope/fixtures.py`（`subject_snapshot`/`write_subject_fixture`/`evidence` 均为公开 wire 形状）；可直接使用的 JSON 样例为 `docs/plans/mb11-rf-2026-11-11/fixtures/subject-snapshot-example.json`。真实 StockWiki 组合由 ROOT 用公开 subject fixture/CLI 绑定，RF 作者未改 SW。

## 4. 实际测试

环境：Windows，`C:/Miniconda/python`（Python 3.13.9），pytest 9.1.1；临时根 `C:/Temp/mb11b2*`，结束后删除。

| 命令 | 退出码 | pass/fail/skip | 耗时 | 日志 |
|---|---|---|---|---|
| `python -B -X utf8 -m pytest tests/rf_verified_scope -q -p no:cacheprovider` | 0 | 57/0/0 | 6.68s | `b2_scope_focused_final.log` |
| `python -B -X utf8 -m pytest tests/rf_verified_scope tests/test_report_catalog_rf_job_import.py tests/test_rf_job_concurrency.py tests/test_rf_job_recovery.py tests/test_rf_job_boundary_regression.py tests/test_decoupled_source_port.py tests/test_d4_narrative_consumption_port.py tests/test_report_catalog_compare.py tests/test_report_catalog_deployment.py tests/test_report_catalog.py tests/test_report_catalog_identity_resolver.py tests/test_single_owner_guard.py tests/test_architecture_dependency_uses.py tests/test_golden_behavior_lock.py tests/b37_publication_sources -q -p no:cacheprovider` | 1 | 309/1/3 | 91.31s | `b2_combined_final_tip2.log` / `.xml` |

- 唯一失败：`tests/test_single_owner_guard.py::test_subprocess_use_is_limited_to_contract_clients`。已用 HEAD 树复算证明 allowlist 在 B2 前已缺 `report_catalog_identity_resolver.py`、`report_catalog_rf_job_import.py`、`report_catalog_source_alias.py`、`rf_job_facade.py`；新模块无 `subprocess`。属既有缺口，交 ROOT。
- 3 个 skip 为既有环境/合同 skip（Dashboard 合同目录、默认 catalog 跨 owner 链接、模型族输出固定）。
- Ruff（4 模块+新测试）通过；mypy（4 模块）通过；pre-commit 与 pre-push 固定 smoke 12 passed。
- 未执行：整个 `tests/` 树（本工区存在既有收集失败：`test_zr1008` 导入缺失的 `test_zr709`，`test_ca204` 亦报错）；真实 StockWiki/CWP 组合；网络/模型/预测/收费调用。

## 5. 独立审查

- 第一轮：agent-32545490，绑定 `940e05b4`，PASS；F1–F4 本卡修复（修复提交 `2ec16368`），F5 交 ROOT，F6/F7 记录。
- 第二轮：agent-023442c1，绑定 `2ec16368`，PASS；N1–N3 修复（修复提交 `d368eff6`），N4/N5 证据卫生处理。
- 第三轮复核：agent-deb118d7，绑定 `d368eff6`，PASS；确认 N1–N3、无新增越界。
- 详细发现、修复与复核见 `review.md`；最终代码审查绑定 `d368eff6`，本 handoff 仅为之后的文档提交。整卡其余 A/B/C 项未进入本轮审查，见 `card_audit.md`。

## 6. 隔离与恢复

- 测试目录初始状态：每次运行前新建空的 `C:/Temp/mb11b2*` 短根；结束状态：只删除本次自建目录，最终 `ls /c/Temp/mb11b2*` 无残留；仓内未留 pytest 临时产物。
- 未改生产原件/配置/既有 WIP；`assurance/runs/{daily_alert.jsonl,monthly_manifest.json,weekly_alert.jsonl,weekly_manifest.json}` 未写入；未部署全局 skills；未改 CWP/StockWiki/Dashboard。
- 业务网络调用 0、模型调用 0、费用 0/unknown；仅发生 Git fetch/push。
- 工作树在代码提交后干净；handoff 文档提交后仍保持干净（日志随文档提交）。

## 7. 安装/部署/CI/合并状态

- 安装/部署：未执行全局安装；未改部署根；**整卡的临时 destination 安装隔离尚未执行**（见 `card_audit.md` A/B/C-6）。
- CI：未运行远端 CI；本地 Ruff/mypy/pre-commit/pre-push smoke 通过。
- 合并：分支已推送，`main` 未合并；ROOT 接收后需在集成树重跑本段受影响测试并绑定最终代码 tip。
- 整卡剩余：canary 退休、report/core 解耦、严格来源边界、历史 profile 证据、安装隔离与 `test_module_boundary_closure.py` 未交付，不能按整卡 `MERGED` 处理。

ROOT 下一步（一条可执行命令，先在独立集成工区核对 `origin/main` 与提交祖先关系）：

```powershell
C:/Miniconda/python -B -X utf8 -m pytest tests/rf_verified_scope tests/test_report_catalog_rf_job_import.py tests/test_rf_job_concurrency.py tests/test_rf_job_recovery.py tests/test_rf_job_boundary_regression.py tests/test_decoupled_source_port.py tests/test_d4_narrative_consumption_port.py tests/test_report_catalog_compare.py tests/test_report_catalog_deployment.py tests/test_report_catalog.py tests/test_report_catalog_identity_resolver.py tests/test_single_owner_guard.py tests/test_architecture_dependency_uses.py tests/test_golden_behavior_lock.py tests/b37_publication_sources -q -p no:cacheprovider
```

真实组合时使用公开入口：

```powershell
C:/Miniconda/python -B scripts/report_catalog_verified_compare_cli.py --owner-root <RF owner workspace> get-bindings --report-id <report-id> --data-root <RF data root> --subject-fixture <ROOT-frozen subject fixture.json>
```
