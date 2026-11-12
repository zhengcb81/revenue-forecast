# MB-RF B2 独立审查记录

审查对象：`scripts/report_catalog_subject_resolver.py`、`report_catalog_scope_binding.py`、`report_catalog_verified_compare.py`、`report_catalog_verified_compare_cli.py` 及 `tests/rf_verified_scope/`。
审查性质：只读独立审查；未修改作者文件，未代作者提交。

## 第一轮（绑定 940e05b4）

- 审查者：agent-32545490-f57c-4e4e-b3e8-c6093e5967a0（general-purpose，只读）
- 结论：**PASS**，无阻断项。
- 确认：四模块只经 `ReportCatalog` 公开 `get_report`/`get_run`/`get_source_snapshot` 读数；无 `_index`/`_exact_report`/`_public_report`/`_compare_pair` 等私有符号；无 sqlite/StockWiki/CWP 导入；`import-rf-job`、`rf-report-comparison/1` 和 catalog reader 未改；verified-compare 复用公开 `compare_reports`，原始 left/right 行未被改写；600 期与 >1MiB 输出无截断。
- 发现与处置：
  - F1（minor，本卡）：`append-binding` 误用 compare 的 64KiB 请求预算，600 期合法证据（约 104KB）被拒。修复：append 改用 owner 既有 `MAX_ARTIFACT_BYTES`；compare 保留 64KiB；新增 600 期 CLI 入库/回读测试。
  - F2（minor，本卡）：准则/分部断言偏输入回显，缺“省略即拒绝”。修复：补 6 个必需字段逐一缺失的负例。
  - F3（minor，本卡）：若干可达错误分支无测试、FY 空日期语义未说明。修复：补日历不匹配、锚点不匹配、截断行、伪造行哈希、锁占用、resolver 身份不匹配负例；补 FY 空日期=显式 FY 粒度正例。
  - F4（minor，本卡）：scope 状态写在 catalog owner 的 `artifacts/report_catalog/` 下。修复：改到 `artifacts/report_scope/verified_scope_bindings.jsonl`，并加路径回归。
  - F5（major，ROOT 范围）：`tests/test_single_owner_guard.py::test_subprocess_use_is_limited_to_contract_clients` 的 allowlist 在基线已缺 4 个既有 subprocess 脚本，非本卡引入；不在 B2 扩 allowlist 换绿，交 ROOT。
  - F6（info，卡范围）：`tests/test_module_boundary_closure.py` 在本工区不存在，按卡“开工核对后记入 PWF”，不建占位。
  - F7（残余风险）：B2 测试为手写公开 wire 假件，未做真实 `ReportCatalog` 往返；真实快照的 `captured_markdown` 约束未建模。

## 第二轮（绑定 2ec16368）

- 审查者：agent-023442c1-42db-446a-9300-923acec7570d（general-purpose，只读）
- 结论：**PASS**，F1/F4 确认修复，F2/F3 为有效补覆盖；无新增越界。
- 新发现与处置：
  - N1（minor，本卡）：新 state 路径无回归锁。修复：`test_scope_store_never_uses_the_catalog_owner_directory` 断言精确相对路径且不含 `artifacts/report_catalog`。
  - N2（minor，本卡）：只测截断行，未测伪造行哈希。修复：新增伪造 `line_sha256` 用例；原截断用例更名为 `test_scope_store_truncated_line_is_named`。
  - N3（nit，本卡）：CLI docstring 仍称请求预算继承 compare。修复：区分 compare 64KiB 与 append 的 owner artifact bound。
  - N4（证据卫生）：最终组合日志为未跟踪文件，且组合只覆盖选定用例而非整个 `tests/` 树。处置：日志随 handoff 提交；PWF 明确“选定 313 例”与全树既有收集失败。
  - N5（nit）：progress 耗时与提交日志不一致。处置：以提交日志为准改写。

## 第三轮复核（绑定 d368eff6）

- 审查者：agent-deb118d7-2c52-4fba-9866-7bc8c9d6acc3（general-purpose，只读）
- 结论：**PASS**，无阻断项；N1–N3 逐项确认修复，diff 仅含 docstring 与测试/日志/文档，无新增私有访问、邻库导入、subprocess 或截断。
- 复核运行：`pytest tests/rf_verified_scope` → **57 passed / 7.31s**；读取 `b2_combined_final_tip2.log/.xml` → **313 例、309 passed、1 failed、3 skipped、91.31s**，唯一失败为既有 allowlist 用例。
- 仅提示用例数文案与未提交日志，已在 PWF 与本次 handoff 提交中处理。

## 整卡第一轮（绑定 326149cd）

- 审查者：agent-8079d52d-ee06-433c-b534-bf8c97e5d99c（general-purpose，只读）
- 结论：**CHANGES_REQUESTED**。代码层 canary/report-core/profile 基本通过；交付与证据层未闭合。
- 发现与处置：
  - Handoff blocker：handoff/card_audit/review 仍写 B2-only、commit 为 `d368eff6`、`MB-RF-CARD-REMAINING=NOT_DELIVERED`；已在 `9404984d` 更新为整卡状态，最终代码 tip 为 `ec2e2f2e`。
  - 运行时清单 GAP：已新增 `runtime_inventory.md`，列入口/模块/公开面/状态 owner/依赖方向/兼容退休分类。
  - `revenue_forecast.py` pure/zero-IO 误称：已改为“引擎无隐藏 clock/network/disk 输入；formal 注册 publication，draft 不写”。
  - 来源边界证据偏弱：已改为 `-S` + 空 `PYTHONPATH`、目录式不可读 catalog handle、邻库哨兵 atime/size/mtime/hash 全部不变、reader 仅 1 次、成功断言完整 SourceRef、失败断言 `SourceVersionTransportError` 且不含邻库路径。
  - 安装证据偏弱：已断言 apply/check JSON、零 drift、安装树含全部入口与新 leaf、不含 canary、`-S` 导入安装后 runtime。
  - 历史 profile 默认路径：已补默认 `publication_version="v1"` 与 v1 相对路径断言。
- 整卡回归（`9404984d`）：**561 passed、2 failed、3 skipped、31 subtests**；两项失败为基线已复现的 allowlist 与 B34 identity 用例。`ec2e2f2e` 仅改测试文件（2+/2−），不改变生产代码或测试数。

## 整卡第二轮复核（绑定 9404984d，docs tip 当时未提交）

- 审查者：agent-2310675d-40c5-43d3-b134-fb4840b21936（general-purpose，只读）
- 结论：**CHANGES_REQUESTED**，但唯一 blocker 是交付物未提交/`pushed: true` 与实际不符；代码层六项修复已确认成立。
- 处置：提交并推送文档 `d1b1ac4c`；`handoff.json` 的 `changed_paths` 44 项与 `git diff 6341759b..HEAD` 集合完全一致；闭包测试在最终 tip 复跑 14 passed；测试文件去重提交 `ec2e2f2e`。

## 整卡第三轮复核（绑定 ec2e2f2e / docs d1b1ac4c）

- 审查者：agent-bfcecaf8-d90f-41f6-89f3-6a4660102c2a（general-purpose，只读）
- 结论：**PASS**。确认工作树干净、local == remote、handoff commit/pushed/changed_paths 一致；`card_audit` 无 B2-only/NOT_DELIVERED 现行结论；契约字段齐备；closure 实跑 **14 passed**；回归日志 561/2/3/31 自洽；两项失败为基线已复现；`ec2e2f2e` 仅测试文件变化。
- 低危文档项已修：`progress.md` 提交链补回 `9404984d`；closure 耗时统一为 9.32s；本复核记录与 handoff reviewer 字段补齐。

## 结论与残余风险

- B2 三轮审查绑定 `d368eff6`，PASS；整卡改造/证据强化绑定 `ec2e2f2e`，第三轮复核 PASS。
- 回归日志/junit 无内嵌 commit hash，是 `9404984d` 提交前工作树运行结果；其后 `ec2e2f2e` 仅测试文件去重，生产代码相同。
- 范围外：单 owner 守卫 allowlist 缺口、B34 `identity_not_resolved`（基线已复现）、B34 并发/临时目录时序、全树 `pytest tests` 既有收集失败、真实 CWP/StockWiki 生产组合。均不冒充已通过，交 ROOT。
- 范围外：单 owner 守卫 allowlist 缺口、B34 `identity_not_resolved`（基线已复现）、B34 并发/临时目录时序、全树 `pytest tests` 既有收集失败、真实 CWP/StockWiki 生产组合。均不冒充已通过，交 ROOT。
