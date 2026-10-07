# G3-RF-ASSURANCE progress

施工仓：`C:/Users/郑曾波/Projects/_g3/RF-ASSURANCE/revenue-forecast`，分支 `codex/g3-rf-assurance`，base `1a2f9428a599504eb8355fcaebf86c6cbcaccbb3`。
scratch 测试根 `.planning/g3-rf-assurance/scratch`（运行前 absent；本次运行结束已删除恢复 absent）。
全离线；模型调用 0、下载 0、生产写 0、用户安装目录写 0。

## Phase 1 — 探索（完成）

- 读卡与 `quality.py / manifest.py / cli.py / sync_installations.py` 及4个责任测试；grep 出全部 caller 与写副作用（明细见 `findings.md` §2-§4）。
- 基态实测（base commit，本 worktree）：
  | 包 | 结果 |
  |---|---|
  | `test_zr104_quality.py` | RED（`strict_targets` ValueError：workflow 无内联 mypy） |
  | `test_manifest.py` | 1 failed（30 条 mtime drift）/ 14 passed |
  | `test_sync_installations.py` | 4 passed |
  | `test_ca303_arch_quality.py` | 1 failed（C5 默认 strict mtime）/ 10 passed |
- 关键事实：本卡独占 worktree **没有邻仓**（`../filing-fetch`、`../company-wiki` 不存在）；真实邻仓在 `Projects/`，且 `company-wiki` 已演化到 `tests/contract/test_fc1204_complexity_ratchet.py` 不存在。
- 运行时闭包静态扫描（72 文件）：`tests/tools/assurance/audit_review/compatibility/e2e/examples` 引用数全部为 0 → 移除 `tests/**` 不会漏掉真实 runtime import。证据脚本 `runtime_closure_scan.py`。

## Phase 2 — RED（完成）

卡要求的7项 RED 先写后实现，同一批测试在实现前跑出 **37 failed / 36 passed**：

| RED 目标 | 测试 | base 结果与原因 |
|---|---|---|
| 委托当前 mypy 入口 | `test_g3_quality_reporting::test_revenue_type_targets_follow_current_mypy_entry`、`::test_scratch_workflow_delegation_resolves_type_targets` | FAILED：`ValueError: no 'python -m mypy' command found in .github/workflows/quality.yml` |
| coverage 门退休 | `::test_retired_coverage_gate_no_longer_blocks_verify` | FAILED：ValueError（strict_targets）先炸；同因 |
| 邻仓不在 | `::test_sibling_repo_absent_reports_not_available_with_scope`、`::test_revenue_dimension_is_computed_in_scratch_repo` | FAILED：`compute_baseline` 对缺失邻仓 `git rev-parse` 抛 ValueError |
| 干净 checkout 同 SHA/size 不同 mtime | `test_g3_manifest_checkout::test_clean_checkout_same_sha_size_different_mtime_verifies` | FAILED：默认校验报 7 条 mtime drift |
| 同 size 换字节 | `test_same_size_byte_swap_is_caught_by_sha` | **base 即绿**（SHA 本就拦住）→ 记为守卫而非 RED |
| 实际进程 return2 无 FAILED 字样 | `test_probe_failure_is_judged_by_exit_code_not_text` | **导入错误 RED**（`uc.quality_report` 尚不存在）——按卡“夹具/导入错误单独记录” |
| 独立安装包不带 repo tools | `test_g3_skill_package::test_installable_set_is_the_runtime_closure`、`test_tmp_installation_runs_public_entry_without_repository_tools` | FAILED：`tests/` 仍在安装集合里 |

另有两条独立的 **夹具/导入错误**，与行为无关，单独记录：

1. 卡给的责任命令 `python -m pytest -q assurance/.../test_zr104_quality.py assurance/.../test_manifest.py tools/tests/... tests/test_ca303...` 在 base 就**收集失败**：pytest 9.1.1 同会话内 `tests/conftest.py` 与 `assurance/unified_completion/tests/conftest.py` 同名，后者被前者覆盖，`test_manifest.py` 的 `from conftest import REPO_ROOT` 抛 `ImportError`。最小复现：`pytest assurance/.../test_manifest.py tests/test_ca303_arch_quality.py`。修复（写集内）：`test_manifest.py` 改为本地 `REPO_ROOT = Path(__file__).resolve().parents[3]`，不再 import conftest。
2. 子进程 stdout 含非 ASCII（CLI 的 `—`、中文用户名路径）时 `text=True, encoding="utf-8"` 无 `errors` 会在读线程里抛 `UnicodeDecodeError`。新增/修改的子进程调用补 `errors="replace"`（含 CA303 C5）。

## Phase 3-5 — 实现（完成）

- **quality → 报告**：`uc/quality.py` 的类型目标改为“workflow 内联 mypy 优先，否则只读跟随 `tools/*.py` 委托（AST，不执行 YAML）”；`compute_baseline` 对缺失 scope 返回 `not_available`+scope、对本仓不可读返回 `error`；`verify()` 只返回 failures。新增 `uc/quality_report.py`（`build_report` / `run_probe` / `type_check_command`），旧 `_verify_*` 比较全部降为 diagnostics。
- **manifest 默认 SHA+size**：`verify(check_mtime=False)` 默认；`mtime_diagnostics()` 供诊断；`check_mtime=True` 为显式旧 strict；新增路径逃逸拒绝、缺失/非 JSON manifest → `ManifestError`；`_collect` 单一代码路径保证库/CLI/测试语义一致；全部只读。
- **cli**：5 处 `--mtime` 默认 `off`、`getattr(args,"mtime","off")`；`_require_no_drift` 默认 SHA+size；`manifest-verify` 默认打印 `NOTE:` mtime 诊断；`ManifestError` 干净 exit 1；新增 `quality-report --root/--baseline/--json/--run-types`；`quality-verify` 打 `QUALITY-NOTE`（诊断，不改退出码）与 `QUALITY-VIOLATION`（失败，exit 1）。
- **包装**：`ROOT_DIRECTORIES = ("agents","config","references","scripts")`（`tests/` 退出默认运行包）；`installation_diff` 只比 owned runtime；`sync_installation` 改 tmp staging + 逐文件原子替换，保留未知文件/用户配置/`output`/旧残留，不再整目录替换；`manifest`/`import_installation`/`unique_destinations`/`main` 签名与语义不变，`main` 默认仍只读。
- **SKILL.md** 新增 “Installation and repository layout” 一节，说明技能包与仓库工程工具的职责边界（未动研究方法与源证据规则）。

## Phase 6 — 集中测试（完成）

| 命令 | exit | 秒 | passed | failed | 说明 |
|---|---|---|---|---|---|
| 责任包（卡4文件 + 本卡4个新包，单次混合运行） | **0** | 20 | **74** | 0 | `74 passed in 16.11s` |
| `ruff check <13 个改动文件>` | 0 | <2 | — | 0 | `All checks passed!` |
| `python -m pytest -q assurance/unified_completion/tests/` | 1 | 238 | 228 | 13 | 13 项与 base **完全相同**（stash 对照），与本卡无关 |
| `python -m pytest -q tools/tests/` | 0 | 8 | 29 | 0 | — |
| 受影响根测试（`test_zr905/zr907/rf_coverage_report/rf_release_checklist/ci_smoke_plan/fc1004/ca301`） | 1 | 46 | 56 | 7 | 7 项与 base 相同；另 base 有第8项 `fc1004::test_install_sync_gate_detects_drift` **本卡修复转绿** |
| `python tools/pre_push_gate.py`（卡要求最后跑一次，未改其11包） | 1 | 8 | 105 | 2 | ruff+mypy 全绿；2 项失败是 `test_p5_source_default_cli_e2e` 需要邻仓 `_g3/RF-ASSURANCE/filing-fetch`，**base 完全相同**（独占 worktree 无邻仓；卡禁止写其他仓） |

`test_zr804_platform_shape.py` **按卡禁止未运行**（它会向 `~/.agents`、`~/.codex` 真实 `--apply`）。其身份断言的实测影响见 `HANDOFF.md`“边界外 caller”。

## Phase 7 — 交付（进行中）

- `docs/implementation/g3-rf-assurance/{task_plan.md,findings.md,progress.md,HANDOFF.md,handoff.json}` + 证据 `runtime_closure_scan.py`。
- 提交 1 `e9f9405936c8b123b17592538d1bf70f76d8a6a5`（代码+测试+SKILL+规划/HANDOFF/扫描证据）；提交 2 `87129d124c86a2926f993f4cf73a161f043dd112`（handoff.json）。工作树 clean，不合 main。
- **push 结果：被 `.githooks/pre-push` 拦截，未推送、未绕过 hook。** 根因是 `tools/pre_push_gate.py` 里 `tests/test_p5_source_default_cli_e2e.py` 的2项需要 `../filing-fetch`、`../company-wiki`，本独占 worktree 没有邻仓；同命令在 base commit **完全相同**（105 passed / 2 failed），与本卡改动无关。卡禁止写其他仓（且全离线、下载0），故无法在此环境补齐邻仓；也禁止 `--no-verify`。分支已在共享 ref 存储中（原仓 `git rev-parse codex/g3-rf-assurance` = `87129d12`），MAIN 可直接本地并线，或在带邻仓的 checkout 里复核精确 CI 后再推。
