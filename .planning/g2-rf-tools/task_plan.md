# Task Plan: G2-RF-TOOLS — RF可选工程工具和收尾流程简化

Use this file as the durable roadmap for the task. Create it before complex work and keep it current as phases change.

## Goal

把 `tools/release_readiness.py`、`run_coverage_gates.py`、`final_ratchet.py`、`release_checklist.py`、`session_checklist.md`、`.coveragerc` 改成「默认只读本仓 + 明确指定的版本化输入、数值仅诊断、全套只在集中命令」，同时保留三 scanner API、`fail_under=0`/`PER_MODULE_MINIMUM={}` 兼容形状与日常 11 文件短 CI 职责。

## Next Step

写 `docs/implementation/g2-rf-tools/{HANDOFF.md,handoff.json}`，普通 commit 到 `codex/g2-rf-tools` 并 push 同名施工分支（不合 main、不写 installed）。

## Current Phase

Phase 5

## Phases

### Phase 1: 基线核对与隔离

- [x] 只读核对 main=`e241389adeda37bc9cbb53d7831063718552a936`、三个 owner 文件未提交、worktree/分支归属
- [x] 建 `_g2/revenue-forecast` worktree 分支 `codex/g2-rf-tools`
- [x] 建 `.planning/g2-rf-tools/{task_plan,findings,progress}.md`
- **Status:** complete

### Phase 2: 现状盘点（只读）

- [x] 读五个目标文件 + 三个既有测试 + `uc/quality.py::_revenue_coverage` + `quality.yml` + `pre_push_gate.py`
- [x] 确认 scanner 兼容面（ca303/ca304/zr1102 真实导入）
- [x] 确认 `sync_installations.py` 写集含 tests 不含 tools
- **Status:** complete

### Phase 3: RED → 实现

- [x] 写/改 `tests/test_zr1001_release_readiness.py`、`test_zr906_final_ratchet.py`、`test_ca303_arch_quality.py`（仅工具职责）
- [x] 新增 `tests/test_rf_optional_tools_e2e.py`、`test_rf_coverage_report.py`、`test_rf_release_checklist.py`
- [x] 改 `tools/release_readiness.py`（默认只读、not_supplied、零写、显式输入真实失败）
- [x] 改 `tools/run_coverage_gates.py`（默认报告已有结果、`--run` 才跑一次、scratch、不 erase）
- [x] 改 `tools/final_ratchet.py`（默认轻检查、`--full` 才跑 coverage、mypy 真实结果诊断）
- [x] 改 `tools/release_checklist.py`（真实 returncode、删 EXPECTED_RED、薄委托）
- [x] 改 `tools/session_checklist.md`、`.coveragerc`
- **Status:** complete

### Phase 4: 集中真实 CLI 节点

- [x] 集中 pytest（6 文件，107 passed / 69.57s）+ ruff + pre_push_gate + `git diff --check`
- [x] ca303 定向（10 passed；C5 为 worktree mtime 既有漂移，`--mtime off` 复验 hash+size OK）+ ca304/zr1102 scanner 兼容面（19 passed, 1 skipped）
- [x] 真实 subprocess CLI：默认/check-only/显式完整/错误路径；`assurance/**` 1392 文件 SHA+mtime 前后一致、根 `.coverage*` 无新增
- [x] 时长与用例数如实记录在 `progress.md`（不设数字门）
- **Status:** complete

### Phase 5: 恢复与交付

- [x] 清理本轮临时根与 caches、核三 owner 日志与主仓未动
- [ ] 写 `docs/implementation/g2-rf-tools/{HANDOFF.md,handoff.json}`（`g2-lane-handoff/1`）
- [ ] 普通 commit 到 `codex/g2-rf-tools`（可 push 同名分支，不合 main、不写 installed）
- **Status:** in_progress

## Key Questions

1. 默认模式在隔离 RF（无 FF/CWP/backup/197 样本）是否零阻断且零文件写？ → 由 `test_rf_optional_tools_e2e.py` 断言
2. 明示非法配置 / 坏 SHA / pytest rc=2 无 FAILED / mypy 缺失异常超时是否真实非零？ → 由错误路径子进程断言
3. `uc.quality._revenue_coverage` 能否读 `fail_under=0` + `PER_MODULE_MINIMUM={}`？ → 由 `test_rf_coverage_report.py` 断言

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| 每个 gate 输出 `ok` + `status`（ok/red/not_supplied/diagnostic） | 「未提供报告 not_supplied，而非伪称已验真」；数值只诊断 |
| capacity / coverage / mypy 错误数 → diagnostic，工具失败 → red | TDD：低 coverage/任意历史错误计数不单独阻断；工具异常仍失败 |
| `--record-rollback PATH` 显式才写，check-only 零写 | 不造 probe/rollback/receipt/.coverage；发布由既有发布层处理 |
| `run_coverage_gates --run` 必须给 `--scratch DIR` | coverage 文件全部在显式 scratch，不 erase 用户现存 `.coverage` |
| `final_ratchet` 默认 = scanner+complexity+type，coverage not_supplied；`--full` 才跑一次 | 「显式完整模式才调用一次离线责任组」 |
| `release_checklist` 薄委托 `pre_push_gate.py` + `release_readiness.py`，按真实 rc | 不另复制一套全测；删 EXPECTED_RED/迁移文档/MATCH·apply/mutation |
| 不改 `quality.yml`、`pre_push_gate.py`、`uc/quality.py` | 卡片写集禁止；旧 quality-verify 三仓冻结要求退出本卡施工说明 |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| 旧 final_ratchet 默认递归拉起全套 coverage（RED 阶段 900s 超时） | 1 | kill 本 lane 进程；RED 分片 deselect；实现后默认不启动 coverage |
| zr1001 四用例漏 `["fingerprints"]` 索引、一条用错 repo 名 | 1 | 补索引；改用不在 REPOS 的名字 |
| coverage 用例把 `.coveragerc` 当数据文件 | 1 | glob 只认 `.coverage`/`.coverage.*` |
| release_checklist docstring 含退役控制名字面量 | 1 | 改写为语义描述 |
| `_g2/` 无兄弟 checkout 导致 pre_push_gate 红 | 1 | 显式导出 `FF_V2_CODE_ROOT`/`CWP_V2_CODE_ROOT`（既有 env 覆盖） |
| 临时根只读文件删不掉 | 1 | chmod 后再删，删前核路径/归属/reparse |

## Notes

- 三个 owner 日志（`assurance/runs/daily_alert.jsonl`、`weekly_alert.jsonl`、`weekly_manifest.json`）保留，不能 checkout/reset/暂存。
- `scripts/**`、forecast/calculation/evidence/narrative/source adapter/closure 规则一律不写。
- 缺 hash 诊断、已提供而不符失败的现行业务 closure 不改，也不恢复早期全 path 强制 hash。
