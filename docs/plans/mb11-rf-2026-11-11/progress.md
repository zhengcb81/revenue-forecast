# 进度

- 已基于 RF 当前 main 建立 C:/Users/郑曾波/Projects/mb11-rf。
- 已记录参考候选和全树差额，明确只处理原 MB-RF 卡中的最小公开合同路径。
- 开工时先记录的基线：无compare模块；当前job/recovery/source-port相关回归51 passed。后续各阶段结果按下文分别记录。


## compare模块接收进展（本轮）

- 只测试的B37 RED：当前main收集失败，`ModuleNotFoundError: report_catalog_compare`，见 `b37_compare_red.log`。
- 先接入 compare.py 与固定CLI，B37 synthetic比较合同 51 passed/1 skip；job/recovery/source-port既有基线51 passed。
- 独立审查指出 512行及1MiB响应固定门槛无预算依据。已移除，并以600期完整归属和>1MiB完整CLI响应覆盖；compare+job/recovery/source-port合并回归102 passed/1 skip（门槛修正前），门槛修正后compare套件52 passed/1 skip。
- 门槛修正后的ruff与mypy均通过。测试使用仓外Temp basetemp，运行后已删除；环境性skip是未设置Dashboard合同目录。
- compare代码最终由 `e060a8607` 并入RF `main`，PWF进度随后记录于 `33d880826`；compare功能不是本工作树剩余待并的项目。
- 独立只读审查对 compare 三文件给出 PASS；结果和范围保存在 review/compare_api_review.md。审查指出的“每行完整期次、左右定位都保留”断言已补上并重测。
- 最终compare测试52 passed/1环境skip；Ruff、mypy通过。此前102 passed/1 skip是去掉结果门槛之前的组合回归，只作补充证据，不冒充门槛修正后的全组合结果。

- compare并入main后的既有主线观测：compare + job/recovery/source-port 为102 passed、2 skipped，固定push smoke为12 passed；本轮更新的更完整组合是171 passed、1 skipped。main上的 `assurance/runs/daily_alert.jsonl` 有后台追加，本次保留原内容，不纳入提交或回滚。

- 发布记录：第一次push误从 company-wiki 根执行，Git因本地 refspec 不存在拒绝，未更新远端；随后从 RF 仓成功推送功能分支并快进 main。`058be4fd6` 当前已在两处。

## B37部署与来源测试增量

- 从候选中独立保留了 `tests/test_report_catalog_deployment.py` 和 `tests/b37_publication_sources/`；publication-source owner实现与main同blob，无生产代码复制。
- 锁文件测试原本要求稳定的 `catalog.jsonl.lock` 不存在，与RF `OwnerFileLock` 协议冲突。改成检查根目录文件集不变且锁未持有；没有更改owner锁实现。
- 首轮长 `--basetemp` 下出现4个RF-job用例路径创建失败；短临时根使用相同命令复验后，最终聚焦集合为171 passed、1 skipped、71.41s。最终日志为 `b37_combined_final.log`，首轮失败数与根因在findings.md留档；pytest basetemp均在命令结束后清除。
- 独立只读审查 PASS，见 `review/deployment_source_regressions.md`。最终部署文件单测38 passed；Ruff通过。测试文件与PWF已由提交 `058be4fd6` 推送到 `codex/mb11-rf`，并快进进入 RF `main` / `origin/main`；两次push的固定smoke各12 passed。
- scope/subject/verified-comparison测试中的3个缺口和候选实现跨模块私有调用/市场范围固定问题已归因并写入findings.md。对应候选代码留在源分支，不复制到本工区；scope功能后续先补公开边界和泛化测试，再判断并线。

## B2 公开 scope/subject/verified-compare（本轮）

- A（RED）：先建 `tests/rf_verified_scope/`，以 `test_b2_public_scope_entrypoints_are_available` 证明当前主线缺少4个公开入口，`b2_scope_red.log` 为 `1 failed`；失败原因是能力缺失，不是依赖/权限/fixture 错误。
- B（实现）：新增 `scripts/report_catalog_subject_resolver.py`、`report_catalog_scope_binding.py`、`report_catalog_verified_compare.py`、`report_catalog_verified_compare_cli.py`。未改 `report_catalog.py`、`report_catalog_compare*.py`、`report_catalog_identity_cli.py` 等既有公开实现；`import-rf-job` 入口保持原样。
- 公开面：`SubjectQuery`/`SubjectSnapshot`/`FrozenSubjectResolver`；scope 坐标/证据/绑定 DTO、`build_scope_binding`、`validate_scope_binding`、`ScopeBindingStore`、`list_scope_bindings`、`exact_scope_pair`；`compare_verified_scope` 只消费公开 `compare_reports` 与公开 reader，原始 left/right 行不被改写。
- 依赖隔离：静态 AST 检查四模块不引用 `_index/_exact_report/_public_report/_compare_pair` 等 catalog 私有符号，不 import sqlite3/stockwiki/CWP；运行时用 `PublicOnlyCatalog`（私有属性访问即断言失败）跑通全部构建/比较用例。
- 泛化合同：8组 golden（IFRS/US GAAP × 06-30/12-31 × 1/3 分部）、24 分部、H1 期次、600 期完整结果、>1MiB CLI 响应；无 IFRS/12-31/单分部/FY-only 默认。
- 负例：缺源 `scope_source_missing`、重复源 `scope_duplicate_source`、见证不在精确捕获源 `scope_evidence_invalid`、身份不匹配 `scope_identity_mismatch`、期次不覆盖 `*_scope_coordinate_not_covered`、scope 冲突 `scope_binding_conflict`、绑定陈旧 `scope_binding_stale`、错绑定 `scope_binding_not_found`；空 scope 视图不创建数据根。
- 定向结果：`b2_scope_focused.log` 为 **42 passed / 0 failed / 0 skipped / 4.15s**；Ruff 与 mypy（4 个新模块）通过。
- 受影响回归一次：`b2_combined_final.log` / `b2_combined_junit.xml` 为 **294 passed、1 failed、3 skipped、102.74s**。唯一失败是 `tests/test_single_owner_guard.py::test_subprocess_use_is_limited_to_contract_clients`；已用 HEAD 树证明该 allowlist 在 B2 前已缺 4 个既有 subprocess 脚本，新模块不含 subprocess，故为既有缺口、非本卡回归，列入 ROOT 范围外发现。
- 3 个 skip 是既有环境/合同 skip：Dashboard 合同目录未配置（compare）、默认 catalog 拒绝跨 owner 链接（catalog）、模型族输出未固定（golden lock）。`tests/test_module_boundary_closure.py` 在本工区不存在，按卡片要求记为文件名核对结果，不当作产品失败。
- 临时目录：回归使用 `/c/Temp/mb11b2-*` 新短根，结束后只删除本次创建的目录；未改生产原件/配置/既有 WIP，未跑预测、网络或收费调用。

## B2 独立审查与修复（本轮）

- 首轮独立只读审查（agent-32545490，绑定 `940e05b4`）结论 **PASS**，无阻断项；提出 4 项本卡可行动小问题，已全部修复：
  - F1 `append-binding` 误用 compare 的 64KiB 请求预算，600 期合法证据（约 104KB）被拒。改为 append 路径使用 owner 既有 `MAX_ARTIFACT_BYTES`（64MiB）预算；`compare` 请求仍用已发布 64KiB 预算。新增 CLI 600 期证据入库与回读测试。
  - F2 golden 对准则/分部主要是输入回显，缺“省略即拒绝”的负例。新增 6 个必需字段逐一缺失的 `scope_evidence_invalid` 负例。
  - F3 若干可达错误分支无测试；FY 空日期语义未说明。新增 `scope_period_calendar_mismatch`、`scope_anchor_mismatch`、`scope_store_invalid`（断链）、`scope_store_busy`、resolver 与 report 身份不匹配负例；新增 FY 空日期=显式 FY 粒度正例（与既有 compare 合同一致，非默认）。
  - F4 scope 状态原写在 catalog owner 的 `artifacts/report_catalog/` 下。改到独立的 `artifacts/report_scope/verified_scope_bindings.jsonl`，即使 `--data-root` 指向 owner 工作区也不占用 catalog owner 目录。
- 审查确认的残余风险：B2 测试用手写公开 wire 假件，未做真实 `ReportCatalog` 往返；真实快照还要求 `original_format=="captured_markdown"`，假件未建模，契约漂移可能漏检。记录为残余风险，不声称已覆盖。
- 修复后 B2 定向 **55 passed / 0 failed / 0 skipped**（提交日志 `b2_scope_focused_final.log` 记录 6.38s；更早一次本地运行 5.71s 未覆盖日志，不混用）；Ruff/mypy 复核通过。
- 第二轮独立审查（agent-023442c1，绑定 `2ec16368`）结论 **PASS**，提出 3 个本卡小项：N1 新 state 路径无回归锁、N2 只测了截断行未测伪造行哈希、N3 CLI docstring 仍写“请求预算继承 compare”。已补 N1/N2 测试、修正 N3 文案，并校正本条耗时记录。
- 审查同时确认：最终组合日志只覆盖选定用例，不是整个 `tests/` 树；本工区 `pytest tests` 存在既有收集失败（`test_zr1008` 导入缺失的 `test_zr709`，`test_ca204` 亦报错），属既有问题，列给 ROOT，不在本卡扩围。
- 组合回归历史：`2ec16368` 上为 307 passed/1 failed/3 skipped（`b2_combined_final_tip.log`）；补 N1/N2 两例后最终 `d368eff6` 上为 **309 passed、1 failed、3 skipped、91.31s**（`b2_combined_final_tip2.log` / `_tip2.xml`，共 313 例）。唯一失败仍是既有 subprocess allowlist 缺口。
- 第三轮复核（agent-deb118d7，绑定 `d368eff6`）结论 **PASS**，确认 N1–N3 已修、无新增越界；仅提示本条用例数与未提交日志，已在本节与 handoff 中校正/纳入提交。

## 整卡对照审计（2026-11-12）

- 逐条对照 MB-RF 卡与 handoff_contract 后确认：**B2 切片完成**；**整卡 A/B/C 未全面完成**。详见 `card_audit.md`。
- 整卡未交付项：canary 仍可安装且 `import sqlite3`；`revenue_report.py` 仍从 `revenue_core` 导入、core 运行时回调 report；严格“无 CWP/FF 包、不可读上游 DB、不 patch 私有 helper”的来源边界测试缺失；B34 历史 profile 默认路径无 CWP 布局的合同证据未单列；临时 destination 安装隔离未执行；`tests/test_module_boundary_closure.py` 不存在。
- 参考测试补充：`tests/b34_publication` + `tests/b35_lineage` + `test_model_registry_contract.py` 运行 **129 passed、1 failed、31 subtests passed**；失败用例不导入 B2 模块，identity resolver/cli 零 diff，归为既有/环境问题。
- handoff 已加范围声明与 `MB-RF-CARD-REMAINING = NOT_DELIVERED`，避免把 B2 切片误报为整卡交付。

## 整卡收尾（2026-11-12）

- 代码提交：`326149cd`（canary 退休、report/core 解耦、整卡闭包测试）、`9404984d`（来源/安装证据强化与 zero-IO 文案修正）、`ec2e2f2e`（闭包测试去重，仅测试文件）。
- Canary：加入 `RETIRED_RUNTIME_FILES`，不再进入 `installable_files/manifest`；源文件保留；无 runtime 引用。
- report/core：`ENGINE_VERSION` 移入 `contracts.constants`，workflow receipt 移入 `contracts/workflow_receipt`；report/publication/schema 改 leaf；core re-export 兼容；`-S` 子进程证明 report 不加载 core。
- 来源边界：公开 `prepare_registered_source_result` 子进程测试，无 CWP/FF 包、空 PYTHONPATH、目录式不可读 catalog handle、邻库哨兵 atime/size/mtime/hash 不变、reader 仅 1 次；失败 `SourceVersionTransportError`。
- 历史 profile：v1 默认、v2 版本化、v0 拒绝、相对路径、无 sqlite/CWP 导入；b34/b35 真实正反例通过（除基线已复现 identity 失败）。
- 安装：临时 destination + 空 cwd 跑 `sync_installations.py --apply/--check`，零 drift，安装树含入口与新 leaf、不含 canary，`-S` 导入安装后 runtime；tools 安装测试 20 passed。
- 整卡回归：`full_card_regression_final.log` / `full_card_junit_final.xml`，**561 passed、2 failed、3 skipped、31 subtests passed、195.40s**；两项失败为基线已复现（allowlist、B34 identity）。
- 整卡闭包：`full_card_closure.log`，**14 passed、9.32s**。
- 文档：`card_audit.md` 全量状态、`runtime_inventory.md` 入口/模块/owner/依赖清单、`handoff.md/json` 绑定 `ec2e2f2e`。
