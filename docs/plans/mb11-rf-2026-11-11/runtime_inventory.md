# RF 交付 runtime 入口与边界清单（MB-RF 整卡）

本清单对应 MB-RF 卡“全卡共用完成规则”的活动入口/逻辑模块/公开面/状态 owner/依赖方向要求。只列 RF 仓实际交付内容，不把 `tests/`、`tools/`、历史 review 资料当 runtime。

## 1. 活动入口

| 入口 | 类型 | 公开面 | 状态 owner | 兼容/退休 |
|---|---|---|---|---|
| `scripts/revenue_forecast.py` | 计算/报告 CLI | stdin 输入、JSON/Markdown 输出、`--validate-only` | 无（调用 core；formal 模式由 core 注册 publication） | 保留 |
| `scripts/source_preparation.py` | 来源准备 CLI | `FilingRequest` → RevenueSourceRecord；`--result-envelope` | 无（来源由 CWP/FF owner 持有） | 保留；旧 normalized-body reader 非默认 |
| `scripts/report_catalog_cli.py` | catalog 只读 CLI | list/get run/report/model/calculation/trace/source-snapshot | `artifacts/report_catalog/catalog.jsonl`（`ReportCatalog`） | 保留 |
| `scripts/report_catalog_compare_cli.py` | 比较 CLI | stdin `CompareRequest` → `rf-report-comparison/1` | 只读 | 保留 |
| `scripts/report_catalog_identity_cli.py` | 管理 CLI | resolve / import-w09 / import-research-attempt / import-research-publication / **import-rf-job** | catalog + research publication | 保留，B2 未改 |
| `scripts/report_catalog_verified_compare_cli.py` | scope CLI | get-bindings / compare / append-binding | `<data-root>/artifacts/report_scope/verified_scope_bindings.jsonl` | 新增（B2） |
| `scripts/rf_job_facade.py` | durable job 入口 | job 提交/恢复 | job 记录目录 | 保留；旧 job facade 未整体并入 |
| `scripts/processed_artifact_canary.py` | 历史诊断 | 无 | 无 | **退休**：不进入 `installable_files`，源文件保留 |

## 2. 逻辑模块与公开面

| 模块 | 公开面 | 依赖方向 |
|---|---|---|
| `revenue_core.py` | 编排、`run_forecast`、旧 `ENGINE_VERSION`/`SKILL_VERSION`/`build_workflow_compliance_receipt` re-export | → leaf contracts / forecast / research / analysis；运行时 → `revenue_report.validate_published_forecast` |
| `revenue_report.py` | `render_markdown`、`validate_forecast_output`、`validate_published_forecast` | → leaf contracts/forecast/research/analysis；**不导入** `revenue_core` |
| `revenue_publication.py` | publication receipt 构造/校验 | → `contracts.constants` / `contracts.evidence` |
| `schema_compatibility.py` | schema/engine 兼容矩阵 | → `contracts.constants` / `contracts.evidence` |
| `contracts/constants.py` | schema/enum/engine 常量（含 `ENGINE_VERSION`） | 纯 leaf |
| `contracts/workflow_receipt.py` | `build_workflow_compliance_receipt` | → `contracts.constants` / `contracts.evidence` |
| `report_catalog.py` | `ReportCatalog` 公开 reader/writer、`import_w09` | JSONL owner state；不依赖邻仓 |
| `report_catalog_compare.py` | `compare_reports`、`validate_request` | → catalog 公开 reader |
| `report_catalog_subject_resolver.py` | `SubjectQuery`/`SubjectSnapshot`/`SubjectResolver`/`FrozenSubjectResolver` | 公开 subject port；不导入 StockWiki |
| `report_catalog_scope_binding.py` | scope DTO、`build_scope_binding`、`validate_scope_binding`、`ScopeBindingStore` | → catalog 公开 reader + subject port |
| `report_catalog_verified_compare.py` | `compare_verified_scope` | → `compare_reports` + scope/subject 公开面 |
| `company_wiki_source_reader_v2.py` / `source_preparation.py` | SourceRef v2 公开 reader/port | → 外部 public reader command；不导入 CWP/FF 包 |
| `report_catalog_research_publication.py` | 历史 publication admission（v1/v2 profile） | 相对路径 layout；不导入 sqlite/CWP |
| `installation_manifest.py` | 可安装 runtime 清单 | `RETIRED_RUNTIME_FILES` 排除 canary/processing_demand |

## 3. 状态 owner

| 状态 | owner | 形式 |
|---|---|---|
| report catalog | `ReportCatalog` | append-only JSONL |
| scope bindings | `ScopeBindingStore` | append-only JSONL，独立 `artifacts/report_scope/` |
| durable jobs | `rf_job_facade` / job 记录 | 文件记录；recovery 不重算已完成阶段 |
| publication registry | `publication_registry` | 可重建 JSONL 索引 |
| source artifacts | CWP/FF owner | RF 只读公开 SourceRef/reader 端口 |

## 4. 兼容/退休分类

- **保留**：catalog/compare/identity/job/source 现有公开入口与 schema。
- **新增（B2）**：subject/scope/verified-compare 公开模块与薄 CLI；既有 `rf-report-catalog/1`、`rf-report-comparison/1` 不变。
- **退休**：`processed_artifact_canary.py` 不再分发（源文件保留）；`processing_demand.py` 已在 `tools/legacy/`；旧 job facade 不整体并入；候选 `b37_scope_binding` 私有实现未导入。

## 5. 依赖方向结论

`CLI → owner 模块 → 公开 reader/leaf contract`；`revenue_report → leaf`，`revenue_core → report` 仅保留运行时回调；scope/subject/verified-compare 不反向依赖 core/report，也不导入 CWP/StockWiki 私有模块。安装闭包由 `installation_manifest` 与 `tools/sync_installations.py` 统一持有。
