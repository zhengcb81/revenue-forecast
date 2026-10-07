# Progress Log (G2-RF-TOOLS)

## Session: 2026-10-07

### Phase 1: 基线核对与隔离

- **Status:** complete
- **Started:** 2026-10-07 (local)
- Actions taken:
  - 只读核对：main=`e241389adeda37bc9cbb53d7831063718552a936`（`Use public information date for narrative source eligibility`）；`git status --short` 仅三个 owner 文件 modified；无 g2 分支/worktree。
  - `git worktree add -b codex/g2-rf-tools 'C:/Users/郑曾波/Projects/_g2/revenue-forecast' main`（目标目录/分支原先均 absent，无覆盖）。
  - 建 `.planning/g2-rf-tools/{task_plan.md,findings.md,progress.md}`。
  - 环境：Python 3.13.9 / pytest 9.1.1 / ruff 0.15.18 / mypy 1.19.0 / coverage 7.12.0。
- Files created/modified: `.planning/g2-rf-tools/*`

### Phase 2: 现状盘点（只读）

- **Status:** complete
- Actions taken:
  - 读 `tools/{release_readiness,run_coverage_gates,final_ratchet,release_checklist}.py`、`session_checklist.md`、`.coveragerc`、`tests/test_zr1001_*`、`test_zr906_*`、`test_ca303_*`、`uc/quality.py::_revenue_coverage`、`quality_baseline.json`、`.github/workflows/quality.yml`、`tools/pre_push_gate.py`、`tools/sync_installations.py`。
  - 确认 scanner 消费者：`test_ca303_arch_quality.py`、`test_ca304_r9_removal.py`、`test_zr1102_adversarial_audit.py`。
  - 确认 `PER_MODULE_MINIMUM` 必须写成 `ast.Assign`（**不能**加注解，否则 `uc.quality._top_level_assignments` 读不到）。
- Findings: 见 `findings.md`。

### Phase 3: RED → 实现

- **Status:** complete
- RED（先于实现，实测）：

| # | command | exit_code | count | seconds |
|---|---|---|---|---|
| R1 | `python -B -m pytest -q --tb=no -p no:cacheprovider tests/test_zr1001_release_readiness.py --basetemp <tmp>` | 1 | 25 failed / 6 passed | 6.05 |
| R2 | `python -B -m pytest -q --tb=no -p no:cacheprovider tests/test_zr906_final_ratchet.py -k "not c4_mypy_without_version_banner and not c4_type_failure_makes" --basetemp <tmp>` | 1 | 10 failed / 11 passed / 2 deselected | 1.33 |
| R3 | `python -B -m pytest -q --tb=no -p no:cacheprovider tests/test_rf_optional_tools_e2e.py -k "not e4_default_is_green" --basetemp <tmp>` | 1 | 15 failed / 4 passed / 1 deselected | 5.82 |
| R4 | `python -B -m pytest -q --tb=no -p no:cacheprovider tests/test_rf_coverage_report.py -k "c1" --basetemp <tmp>` | 1 | 3 failed / 13 deselected | 0.85 |
| R5 | `python -B -m pytest -q --tb=no -p no:cacheprovider tests/test_rf_release_checklist.py -k "c1 or c2 or c3" --basetemp <tmp>` | 1 | 11 failed / 1 passed / 2 deselected | 60.79 |
| R6 | `python -B -m pytest -q --tb=no -p no:cacheprovider tests/test_ci_smoke_plan.py --basetemp <tmp>` | 0 | 3 passed（对照组） | 0.65 |
| R7 | 旧 `python -B tools/release_readiness.py`（真实 CLI 探针） | 1 | `fingerprints: RED`、`integrity: RED catalog unreadable`、`rollback: RED rollback point requires complete three-repo HEADs`、`backup` 写 `.read-probe` | ~1 |

  - R2/R3 各 deselect 2/1 条：在**旧**工具上跑它们会启动本卡明令禁止的全套 coverage（`final_ratchet` 默认无条件跑 `run_coverage_gates`），会递归拉起多层 `coverage run -m pytest tests`。第 3 步实测确实出现了该失控（900 秒超时前递归 spawn），已按 `_g2` + `revenue-forecast` 精确匹配 kill 掉全部本 lane 进程（未触碰其他 harness lane 的 python 进程），随后只 deselect 这三条“必然触发旧全套”的用例完成 RED。
  - R5 的 `test_c3_unknown_argument_is_a_configuration_error` 让旧 release_checklist 真跑了它自带的全套 `pytest tests`（60.79s），证明旧工具完全没有参数校验。
- 实现（全部在 `_g2/revenue-forecast`）：
  - `tools/release_readiness.py` — 默认只读本仓；`not_supplied`/`diagnostic` 状态；check-only 零写；`--catalog/--scenario-registry/--backup-dir/--expect-head/--budget-mb/--record-rollback/--json`。
  - `tools/run_coverage_gates.py` — 默认只报告已有结果；`--run --scratch DIR [--target]` 才跑一次；`COVERAGE_FILE` 全落 scratch；不 `erase` 用户 `.coverage`；`PER_MODULE_MINIMUM = {}`。
  - `tools/final_ratchet.py` — 默认 scanner+complexity+type；coverage `not_supplied`；`--full --coverage-scratch DIR` 才委托一次；mypy 真实结果（缺失/无 banner/rc≥2/超时 → RED，错误数仅诊断）。
  - `tools/release_checklist.py` — 薄委托 `pre_push_gate` / `release_readiness` / `publication_registry audit`，按真实 rc；删 `EXPECTED_RED`、固定迁移文档、安装 MATCH/apply、mutation 巡检。
  - `tools/session_checklist.md` — 改写为“相关责任/大节点 + owner 保护 + 正常 commit/push + 真实待办”。
  - `.coveragerc` — `fail_under = 84` → `0`（附注释说明仅为历史报告解码）。
  - `tests/test_zr1001_release_readiness.py`、`test_zr906_final_ratchet.py` 重写；`test_ca303_arch_quality.py` 仅改 C4 工具职责；新增 `tests/test_rf_optional_tools_e2e.py`、`test_rf_coverage_report.py`、`test_rf_release_checklist.py`。

### Phase 4: 集中真实 CLI 节点

- **Status:** complete
- GREEN：

| # | command | exit_code | count | seconds |
|---|---|---|---|---|
| G1 | `python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_zr1001_release_readiness.py tests/test_zr906_final_ratchet.py tests/test_rf_optional_tools_e2e.py tests/test_rf_coverage_report.py tests/test_rf_release_checklist.py tests/test_ci_smoke_plan.py --basetemp 'C:/Users/郑曾波/Projects/_g2/tmp-g2-rf-pt'` | 0 | **107 passed** | 69.57 |
| G2 | `python -B -m ruff check tools tests` | 0 | All checks passed | <1 |
| G3 | `python -B tools/pre_push_gate.py` | 0 | ruff + public contract types + 11 文件离线行为组 **107 passed**；`pre-push/CI checks GREEN` | ~30 |
| G4 | `git diff --check` | 0 | 无空白错误（仅 autocrlf 提示） | <1 |
| G5 | `python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_ca303_arch_quality.py --basetemp <tmp>` | 0* | **10 passed / 1 failed**（C5 `manifest-verify --mtime strict`） | 4.32 |
| G6 | `python -B -m uc.cli manifest-verify --mtime off`（在 `assurance/unified_completion` 下） | 0 | `OK: frozen inputs re-verified (hash+size; mtime skipped)` | <1 |
| G7 | `python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_ca304_r9_removal.py tests/test_zr1102_adversarial_audit.py --basetemp <tmp>` | 0 | **19 passed, 1 skipped**（scanner 兼容面） | 4.67 |

  \* G5 的唯一失败是 `test_c5_manifest_verifies_offline`：`manifest-verify --mtime strict` 报 `audit_review/**` 的 mtime drift，全部指向 worktree checkout 时间 `2026-10-07 09:42:49`，与本卡写集（`tools/**`、`tests/**`、`.coveragerc`）无关；G6 用 `--mtime off` 证明 hash+size 全部复验通过。卡片已写明“ca303 三仓 manifest 冻结旧漂移不作为扩散改造理由”。
- 真实 CLI 证据（全部为 subprocess 实跑，非 mock）：
  - 默认 check-only：`fingerprints: NOT_SUPPLIED`、`integrity: NOT_SUPPLIED`、`scenario_evidence: NOT_SUPPLIED`、`capacity: DIAGNOSTIC`、`backup: NOT_SUPPLIED`、`rollback: NOT_SUPPLIED`，exit 0。
  - `--budget-mb not-a-number` / `--expect-head no-equals-sign` → **exit 2**（argparse 配置错误）。
  - `--expect-head revenue=<错误 40-hex>` → **exit 1** + `RED`；匹配的真 HEAD → exit 0。
  - `--scenario-registry <仓内已提交合法 registry>` → exit 0 且 `scenario_evidence: OK ... scenarios`；篡改 evidence_path → exit 1。
  - `--backup-dir <tmp>` → exit 0 且 tmp 内容 SHA/mtime 不变（无 `.read-probe`）；缺失目录 → exit 1。
  - `--catalog <tmp sqlite>` → exit 0 只读探针；缺失 → exit 1。
  - `final_ratchet --print-json` 默认 → `coverage: not_supplied`、`type` 真实结果，仓库 `.coverage*` 与 `assurance/` 前后不变。
  - `final_ratchet --full`（无 `--coverage-scratch`）→ 非 0 且提示 `coverage-scratch`；带 scratch + target → coverage 数据只落 scratch。
  - `run_coverage_gates --run`（无 `--scratch`）→ 非 0；`--target <不存在文件>` → 非 0（pytest rc）；`PYTHONPATH` 注入坏 `coverage.py` → 非 0；`--timeout 1` + 慢用例 → 非 0；默认报告模式在 `PYTHONPATH` 注入 `pytest.py`（`SystemExit(9)`）下仍 exit 0 → 证明默认不启动 pytest。
- before/after（G1–G7 全部跑完后与节点开始前逐文件比对）：
  - `assurance/**`（含三个 owner 日志、`rollback_manifest.json`、`backup/`）**1392 个文件 SHA + mtime 完全一致**。
  - 仓库根 `.coverage*` 集合前后一致（均为 `{}`，未产生任何 coverage 数据文件）。
  - `git status --porcelain -uall` 前后差异 = 本卡写集本身（9 修改 + 5 新增），无额外临时文件。
- 环境说明：本 worktree 的 `pre_push_gate` 依赖兄弟 checkout，节点运行时显式导出
  `FF_V2_CODE_ROOT=C:/Users/郑曾波/Projects/filing-fetch`、
  `CWP_V2_CODE_ROOT=C:/Users/郑曾波/Projects/company-wiki`
  （`tests/test_p5_source_default_cli_e2e.py::_env_roots` 的既有 env 覆盖；主仓默认
  `../filing-fetch`、`../company-wiki` 在 `_g2/` 下不存在）。主仓无需此变量。

### Phase 5: 恢复与交付

- **Status:** complete
- Actions taken:
  - 清理 `C:/Users/郑曾波/Projects/_g2/tmp-g2-rf-pt`（先核绝对路径包含 `_g2`、无 symlink/reparse、只读文件先 `chmod` 再删）、`_g2/g2_before.json`。
  - 清理本轮产生的 `.mypy_cache/`、`.pytest_cache/`、`.ruff_cache/`、各处 `__pycache__/`（均 gitignored，基线 absent）。
  - `tests/_g2_ruff_probe.py` 已由用例 finally 删除；`assurance/backup/` 只剩 `README.md`。
  - 三 owner 日志在本 worktree 与 HEAD 一致；主仓 `e241389a` + 三 owner 文件未提交原状未动。
- 写 `docs/implementation/g2-rf-tools/{HANDOFF.md,handoff.json}`（`schema_version=g2-lane-handoff/1`，必备键齐全，四个外部计数全 0）。
- 实现 commit：`8a2c7fe9c25155631a01b083684b8524b38ccc40`；handoff 紧随其后的 commit。
- Files created/modified: 见 `task_plan.md` Phase 3 与 handoff `changed_files`。

## Test Results

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| 集中 pytest（6 文件） | 见 G1 | 全绿 | 107 passed | PASS |
| ruff tools/tests | G2 | 0 | All checks passed | PASS |
| pre_push_gate | G3 | 0 | GREEN | PASS |
| git diff --check | G4 | 0 | 0 | PASS |
| ca303 | G5 | 工具/扫描器绿 | 10 passed, 1 failed（C5 mtime drift，既有） | PASS（工具职责）/ 记录既有漂移 |
| ca304 + zr1102 | G7 | scanner 兼容面绿 | 19 passed, 1 skipped | PASS |

## Error Log

| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-10-07 | 集中 pytest 900 秒超时：旧 `final_ratchet` 默认无条件跑 `run_coverage_gates` → 递归 `coverage run -m pytest tests` 多层 spawn | 1 | 按 `_g2`+`revenue-forecast` 精确匹配 kill 本 lane 进程（其他 lane 未动）；RED 改为分片 + deselect 必然触发旧全套的 3 条用例；实现后默认模式不再启动 coverage |
| 2026-10-07 | `test_c1_unknown_repo_expectation_is_red` 用 `filing`（属于 REPOS） | 1 | 改用不在 REPOS 的 `stockwiki` |
| 2026-10-07 | 四个 zr1001 用例漏了 `["fingerprints"]` 索引 | 1 | 补齐索引 |
| 2026-10-07 | `test_c3_run_keeps_every_coverage_file_in_its_scratch` 把 `.coveragerc` 当数据文件 | 1 | glob 改为只认 `.coverage` / `.coverage.*` |
| 2026-10-07 | `release_checklist` docstring 含 `EXPECTED_RED`/`sync_installations` 字面量导致 C1 断言失败 | 1 | 改写为语义描述（代码本身早已移除） |
| 2026-10-07 | `test_c4_cli_green_end_to_end` 因 `_g2/` 下无兄弟 checkout 而红 | 1 | 导出 `FF_V2_CODE_ROOT`/`CWP_V2_CODE_ROOT`（该测试既有 env 覆盖）；并给断言补上诊断提示 |
| 2026-10-07 | heredoc 写入的字符串里混进真实换行 → `SyntaxError` | 1 | 改为独立 `hint` 变量再拼接 |
| 2026-10-07 | 临时根删除遇 `PermissionError`（publication registry 文件只读） | 1 | `os.chmod` 清只读后再删 |

## 5-Question Reboot Check

| Question | Answer |
|----------|--------|
| Where am I? | Phase 5（complete） |
| Where am I going? | 已交付；MAIN 集中复核并线 + 定点安装同步 |
| What's the goal? | RF 可选工程工具默认只读、数值仅诊断、全套只在集中命令 |
| What have I learned? | 见 `findings.md` |
| What have I done? | 见上 |

---

*Update this file after completing a phase, running validation, or encountering an error.*
