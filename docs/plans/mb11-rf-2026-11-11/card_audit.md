# MB-RF 施工卡逐条审计（2026-11-12）

审计对象：`company-wiki/docs/plans/module-boundaries-2026-11-11/harness_lanes/MB-RF.md`
代码基线：`6341759b`；整卡代码 tip：`ec2e2f2e`；分支 `codex/mb11-rf`。
结论：**整卡 A0 + B2 + A/B/C 1–6 已按卡内要求完成；两项既有失败已证明在基线存在，不作为本卡回归。**

## 1. 逐条状态

| 卡片要求 | 状态 | 证据 |
|---|---|---|
| A0-1 为 compare/scope/publication 公开合同建立失败或已满足证据 | DONE | compare/publication 已由 B1 并入 main（`e060a8607`、`058be4fd6`、`6341759b9`）；scope/subject/verified-compare 的 RED 见 `b2_scope_red.log`，实现与正反例见 `tests/rf_verified_scope/`。 |
| A0-2 当前回归入口 + 参考分支反例 | DONE | 当前 6 个入口全部在整卡回归中通过；`tests/b37_publication_sources`、compare、deployment、catalog 通过；`tests/b37_scope_binding` 在本工区不存在（候选依赖 SW 私有 fixture，未迁移）；`tests/b34_publication`/`tests/b35_lineage` 运行通过，除 1 项已在基线复现的 `identity_not_resolved`。 |
| A0-3 旧 job facade / rf-input-prep 不整体并入 | NO_CHANGE_PROVEN | `rf_job_facade.py` 零 diff；未并入 `rf-input-prep-01` 的 118 项研究产物；未新增第二套 job/reader。 |
| A0-4 四个 assurance 生成物不写、旧失败保留 | NO_CHANGE_PROVEN | `git diff 6341759b..HEAD` 不含 `assurance/runs/{daily_alert.jsonl,monthly_manifest.json,weekly_alert.jsonl,weekly_manifest.json}`。 |
| A0-5 rf-impl / `3b00b938` 原型不建第二 reader | NO_CHANGE_PROVEN | 未新增 reader，只注入公开 subject port；未改 CWP/StockWiki。 |
| B2-1 公开 DTO/reader，禁止 catalog 私有面 | DONE | 四模块只经 `get_report/get_run/get_source_snapshot`；`PublicOnlyCatalog` + AST 测试；无 sqlite/StockWiki/CWP 导入。 |
| B2-2 准则/财年/多分部 golden，显式绑定，无默认 | DONE | 8 组 golden（IFRS/US GAAP × 06-30/12-31 × 1/3 分部）、24 分部、H1、600 期；缺字段/日历负例。 |
| B2-3 缺源/重复源/身份/期次/冲突的稳定语义 | DONE | 命名错误码与负例见 `test_negative_semantics.py`。 |
| B2-4 保留 `import-rf-job`、完整结果、无任意截断 | DONE | `report_catalog_identity_cli.py` 零 diff；help/源码回归；600 期 append、>1MiB 完整响应；compare 64KiB 与 owner artifact bound 均为既有预算。 |
| B2-5 定向通过 + 受影响回归 + 独审绑定 tip + handoff | DONE | 57 passed；B2 三轮审查绑定 `d368eff6`；整卡回归与复核见 §3。 |
| 全卡共用规则：列活动入口/逻辑模块/公开面/状态 owner/依赖方向，含兼容/退休分类 | DONE | `runtime_inventory.md` 列出活动入口、模块公开面、状态 owner、依赖方向与退休分类。 |
| A/B/C-1 交付闭包：canary 不依赖 CWP SQLite/schema/DAG，未使用则移出交付/退休 | DONE | `processed_artifact_canary.py` 加入 `installation_manifest.RETIRED_RUNTIME_FILES`；`installable_files/manifest` 排除；源文件保留；`test_module_boundary_closure.py` 证明无 runtime 引用。 |
| A/B/C-2 计算/研究/报告职责：report 直接消费 leaf，core 编排调用 report | DONE | `ENGINE_VERSION` 移入 `contracts.constants`；`build_workflow_compliance_receipt` 移入 `contracts/workflow_receipt`；report/publication/schema_compatibility 改从 leaf 导入；core 保留 re-export 与运行时回调；`-S` 子进程证明 `import revenue_report` 不加载 `revenue_core`。 |
| A/B/C-3 来源边界：无 CWP/FF 包、不可读上游 DB 时 public commands 仍可 prepare/read | DONE | `test_module_boundary_closure.py` 用 `-S` + 空 `PYTHONPATH` 子进程、公开 reader command、不可读目录式 catalog handle、邻仓 `catalog.sqlite3` 哨兵；成功保留完整 SourceRef，失败抛 `SourceVersionTransportError`，哨兵 atime/size/mtime/hash 不变，reader 仅调用 1 次。 |
| A/B/C-4 历史 admission：B34 profile 显式版本兼容、默认路径无 CWP 内部布局 | DONE | `publication_layout` v1/v2 相对/版本化、默认 `publication_version="v1"`、v0 拒绝；模块不导入 sqlite/CWP；既有 `tests/b34_publication`/`b35_lineage` 真实正反例通过（除基线已复现失败）。 |
| A/B/C-5 作业/目录：code root 与 data root 分开，只读不建库，恢复不重算 | DONE | `test_module_boundary_closure.py` 断言 catalog/job 模块无 sqlite3、`ReportCatalog` 用 `.jsonl` 且不建文件；`test_rf_job_recovery`/`test_report_catalog_deployment` 覆盖恢复与 code/data root 分离；B2 scope state 用独立 `--data-root`。 |
| A/B/C-6 安装和独审：canonical installer、临时目标、空 cwd、不部署全局 | DONE | `test_module_boundary_closure.py` 在空 cwd 跑 `sync_installations.py --apply/--check` 到临时 destination；安装树含全部入口与 `contracts/workflow_receipt.py`、不含 canary；check 零 drift；`-S` 导入安装后 runtime；`tools/tests` 安装测试 20 passed。 |
| 出口：模型/研究 leaf、runtime 副作用、report/catalog/jobs、source adapters 边界清楚；越层工具消失或公开委托；历史 profile 隔离有证据；安装/兼容/公开端口通过 | DONE | 上述各项均有关闭证据；整卡回归 561 passed、2 项基线已复现失败、3 skipped、31 subtests。 |
| 并线交接：作者交分支 + 精确 diff + 包级测试 + 独审绑定 tip | DONE | 分支已推送；整卡代码 tip `ec2e2f2e`；未合并 main；handoff/review/runtime_inventory 已更新。 |
| 不写其他 owner 仓 / Dashboard release / 生产报告 / 全局 skills | DONE | 未改 CWP/StockWiki/Dashboard；未部署全局 skills；未重跑预测。 |

## 2. 参考测试与文件名核对

- `tests/b37_scope_binding/`：本工区不存在；候选版本依赖 StockWiki 私有 fixture 与固定形状，未迁移，改用 `tests/rf_verified_scope/` 的公开泛化合同。
- `tests/b37_publication_sources/`：存在并通过。
- `tests/b34_publication/`、`tests/b35_lineage/`：存在并通过（1 项 `identity_not_resolved` 已在基线归档树上复现；`test_simultaneous_managers_append_only_once` 为并发/临时目录时序问题，相关文件零 diff）。
- `tests/test_module_boundary_closure.py`：本轮新建，14 passed，承载 canary/report-core/source/profile/jobs/install 证据。
- `AGENTS.md`：本工区不存在（只有 `agents/` 目录），开工时无可读 AGENTS 文件。

## 3. 整卡回归与独审

- 整卡回归：`full_card_regression_final.log` / `full_card_junit_final.xml`，**561 passed、2 failed、3 skipped、31 subtests passed、195.40s**。
- 两项失败均为基线已复现：`test_single_owner_guard` 的 subprocess allowlist（4 个既有脚本）与 `tests/b34_publication/test_native_cli.py::test_two_management_processes_replay_then_current_stock_revocation_refuses`（`identity_not_resolved`，基线归档树同样失败）。
- B2 三轮独立审查绑定 `d368eff6`；整卡第一轮 `326149cd` CHANGES_REQUESTED、第二轮 `9404984d` 仅文档/推送 blocker、第三轮 `ec2e2f2e` **PASS**；详见 `review.md`。

## 4. 结论

- **B2 切片**：完成、可交付、三轮独审 PASS。
- **整张 MB-RF 卡**：A0、B2、A/B/C 1–6 与出口均有关闭证据；两项基线失败不冒充通过。
- 残余风险：真实 CWP/StockWiki 生产组合由 ROOT 执行；整棵 `tests/` 树存在既有收集失败（`test_zr1008` 缺 `test_zr709`、`test_ca204`），不在本卡扩围。
