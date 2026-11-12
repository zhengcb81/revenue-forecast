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
