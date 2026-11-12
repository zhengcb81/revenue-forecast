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

## 结论与残余风险

- 本卡 B2 范围内无可行动未修问题；三轮审查最终绑定源码 tip `d368eff6f8ce`。
- 范围外：单 owner 守卫 allowlist 缺口、`test_module_boundary_closure.py` 缺名、全树 `pytest tests` 既有收集失败、真实 `ReportCatalog` captured-markdown 往返、`scope_comparison_shape_mismatch` 分支未构造。均不冒充已通过，交 ROOT/后续卡。
