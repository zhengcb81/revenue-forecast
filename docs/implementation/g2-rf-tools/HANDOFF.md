# G2-RF-TOOLS 交接：RF 可选工程工具与收尾流程简化

**Lane:** `G2-RF-TOOLS` · **branch:** `codex/g2-rf-tools` · **base:** `e241389adeda37bc9cbb53d7831063718552a936`
**delivery commit:** `8a2c7fe9c25155631a01b083684b8524b38ccc40`
**worktree:** `C:/Users/郑曾波/Projects/_g2/revenue-forecast`（本卡独占）

这是一次工程简化交接，不造 authorization/release 签收文件，不重新运行全部已绿的跨仓/付费节点。

---

## 1. 结论

默认可选检查现在**真正只读本仓 + 明确指定的版本化输入**；数值只诊断；全套只在集中命令。
真实类型/测试/配置错误、工具异常、以及**提供了却不符**的 SHA 仍然失败。

| 入口 | 之前 | 现在 |
|---|---|---|
| `tools/release_readiness.py` | 默认读邻仓 `company-wiki/.source_catalog/catalog.sqlite3`、硬要 197 场景 / 2GB / 三仓 HEAD，且**每次写** `assurance/backup/.read-probe` 与被 git 跟踪的 `assurance/runs/rollback_manifest.json`；本 worktree 实测 **exit 1** | 默认 check-only **零文件写**；缺料报 `NOT_SUPPLIED`，数值报 `DIAGNOSTIC`；只有显式 `--catalog / --scenario-registry / --backup-dir / --expect-head / --budget-mb / --record-rollback` 才校验 |
| `tools/run_coverage_gates.py` | `main()` 先 `coverage erase`（抹掉用户现存 `.coverage`），再无条件启动 900 秒全套 pytest + 84% 总门 + 8 模块 40–80 门 | 默认**只报告已有结果**（`--data-file`/`COVERAGE_FILE`/仓根 `.coverage`），无数据即 `not_supplied` 且**不启动 pytest**；`--run --scratch DIR [--target ...]` 才跑一次，数据全落显式 scratch，低数字仅诊断 |
| `tools/final_ratchet.py` | 默认无条件跑 complexity + mypy + coverage（= 又一套全套）；`errors <= 69` 即宣绿 | 默认 = scanner + complexity + type（轻），coverage 为 `not_supplied`；`--full --coverage-scratch DIR` 才委托一次；type 门按**真实 mypy 结果**解释，缺失/无 banner/rc≥2/超时 → 红，错误计数只诊断 |
| `tools/release_checklist.py` | 自复制 `pytest tests` 全套，只解析 `FAILED` 行 + `EXPECTED_RED={"test_structure_targets.py"}` 固定免责（pytest rc=2 无 FAILED 行会误报成功）；另把固定迁移文档、安装全 MATCH/`--apply`、mutation 巡检当每发布资格 | 按**真实 returncode** 薄委托 `pre_push_gate` / `release_readiness` / `publication_registry audit`；上述四类“仪式”全部退出发布资格，不再复制全套 |
| `tools/session_checklist.md` | 每会话全测绿 + 真实 E2E + 安装全 MATCH + 配置 checkout 回 HEAD + 重跑 197 | 改写为：相关责任/大节点、owner 保护、正常 commit/push、真实待办；全套与安装/197 明确列为“只在大节点显式发起” |
| `.coveragerc` | `fail_under = 84` | `fail_under = 0`（附注释：仅为历史报告解码，不决定资格） |
| `run_coverage_gates.PER_MODULE_MINIMUM` | 8 条 40–80 | `{}`（仍为 `ast.Assign` 字面量，可被 `uc.quality._revenue_coverage` 读取） |

## 2. 必须保留的兼容面（已验证）

- **三 scanner**：`scan_hardcode` / `scan_legacy` / `scan_encoding` API 与真反例原样保留。
  真实导入者 `tests/test_ca303_arch_quality.py`、`tests/test_ca304_r9_removal.py`、
  `tests/test_zr1102_adversarial_audit.py` —— 定向实跑 **19 passed, 1 skipped**（G7）。
- **AST/配置读取器**：`uc.quality._revenue_coverage(ROOT)` 直接调用通过，返回
  `total_floor=0.0`、`per_module_floors={}`、`sources` 两键不变（`test_c1_uc_quality_reads_both_shapes`）。
  注意 `PER_MODULE_MINIMUM` **必须**写成 `ast.Assign`，加类型注解会变成 `AnnAssign` 而读不到。
- **日常短 CI**：`.github/workflows/quality.yml` 与 `tools/pre_push_gate.py` **本卡一行未改**；
  `test_ci_smoke_plan.py` 3 passed（单 job、单 gate、run 中仍不含
  `run_coverage_gates/mutation_patrol/sync_installations/verify_plan_claims`）。
- **JSON/CLI 形状**：`final_ratchet --print-json` 仍是六门 `ok` 字典（新增 `status`）；
  `release_readiness` 仍是六门，`detail` 保持 JSON 串，另加 `status`/`problems`。
- **`PYTEST_COVERAGE_EXTRA_ARGS`** 透传保留。

## 3. 验收证据（全部实跑）

### RED（先于实现）

| command | exit_code | count | seconds |
|---|---|---|---|
| `pytest -q --tb=no -p no:cacheprovider tests/test_zr1001_release_readiness.py --basetemp <tmp>` | 1 | 25 failed / 6 passed | 6.05 |
| `pytest … tests/test_zr906_final_ratchet.py -k "not c4_mypy_without_version_banner and not c4_type_failure_makes" --basetemp <tmp>` | 1 | 10 failed / 11 passed / 2 deselected | 1.33 |
| `pytest … tests/test_rf_optional_tools_e2e.py -k "not e4_default_is_green" --basetemp <tmp>` | 1 | 15 failed / 4 passed / 1 deselected | 5.82 |
| `pytest … tests/test_rf_coverage_report.py -k "c1" --basetemp <tmp>` | 1 | 3 failed / 13 deselected | 0.85 |
| `pytest … tests/test_rf_release_checklist.py -k "c1 or c2 or c3" --basetemp <tmp>` | 1 | 11 failed / 1 passed / 2 deselected | 60.79 |
| `pytest … tests/test_ci_smoke_plan.py --basetemp <tmp>`（对照组） | 0 | 3 passed | 0.65 |
| 旧 `python -B tools/release_readiness.py` | 1 | `fingerprints: RED` / `integrity: RED catalog unreadable` / `rollback: RED requires complete three-repo HEADs`；`backup` 写 `.read-probe` | ~1 |

**为什么有 deselect（如实记录，skip 不是 pass）**：旧 `final_ratchet` 默认无条件调用
`run_coverage_gates`，会拉起 `coverage run -m pytest tests`。在 RED 阶段实测因此出现**递归**
（`run_coverage_gates` 的测试又去跑 `run_coverage_gates`）并 900 秒超时；已按
`_g2` + `revenue-forecast` 精确匹配 kill 掉**本 lane 全部进程**（其他 harness lane 的 python 进程未动）。
随后只对“在旧工具上必然启动全套”的 4 条用例做定点 deselect 完成 RED。
实现后默认模式不启动 coverage，这 4 条全部在 GREEN 集中节点里真实通过。

### GREEN（集中节点）

| command | exit_code | count | seconds |
|---|---|---|---|
| `python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_zr1001_release_readiness.py tests/test_zr906_final_ratchet.py tests/test_rf_optional_tools_e2e.py tests/test_rf_coverage_report.py tests/test_rf_release_checklist.py tests/test_ci_smoke_plan.py --basetemp 'C:/Users/郑曾波/Projects/_g2/tmp-g2-rf-pt'` | 0 | **107 passed** | 69.57 |
| `python -B -m ruff check tools tests` | 0 | All checks passed | <1 |
| `python -B tools/pre_push_gate.py` | 0 | ruff + 公共契约 mypy + 11 文件离线行为组 **107 passed** → `pre-push/CI checks GREEN` | ~30 |
| `git diff --check` | 0 | 无空白错误（仅 autocrlf 提示） | <1 |
| `python -B -m pytest … tests/test_ca303_arch_quality.py --basetemp <tmp>` | — | **10 passed / 1 failed**（见 §5 限制） | 4.32 |
| `python -B -m uc.cli manifest-verify --mtime off` | 0 | `OK: frozen inputs re-verified (hash+size)` | <1 |
| `python -B -m pytest … tests/test_ca304_r9_removal.py tests/test_zr1102_adversarial_audit.py --basetemp <tmp>` | 0 | **19 passed, 1 skipped** | 4.67 |

时长与用例数为实测事实，未设任何数字门。

### 真实 CLI 子进程证据（同一实际入口，非 mock PASS）

- **默认 check-only（零写）**：`fingerprints/integrity/scenario_evidence/backup/rollback = NOT_SUPPLIED`、
  `capacity = DIAGNOSTIC`，**exit 0**。
- **returncode=2（配置错误）**：`--budget-mb not-a-number` → 2；`--expect-head no-equals-sign` → 2；
  `release_checklist --not-a-real-flag` → 2。
- **no-FALSE-positive 的“rc=2 无 FAILED”**：`release_checklist` 委托命令 `python -c "raise SystemExit(2)"`
  （stdout 完全没有 `FAILED` 字样）→ `RELEASE-BLOCK: … returned exit code 2`，**exit 1**。
- **坏 SHA**：`--expect-head revenue=<40-hex 但不符>` → exit 1 + `RED`；匹配真 HEAD → exit 0；
  篡改的 scenario registry → exit 1；缺失的显式 registry/catalog/backup → exit 1。
- **显式 coverage 只跑一次**：`run_coverage_gates --run --scratch <DIR> --target tests/test_schema_compatibility.py`
  → exit 0，数据文件全部在 DIR；`--run` 缺 `--scratch` → 非 0；`--target <不存在>` → 非 0；
  `PYTHONPATH` 注入坏 `coverage.py` → 非 0；`--timeout 1` + 慢用例 → 非 0。
- **默认报告不启动 pytest**：报告模式在 `PYTHONPATH` 注入 `pytest.py`（`raise SystemExit(9)`）下仍 **exit 0**。
- **mypy 故障不显示绿**：`PYTHONPATH` 注入空 `mypy.py` → `final_ratchet --print-json` 中
  `type.ok=false / status=red`，**exit 1**；真实 mypy 的 69 条历史错误只作为 diagnostic 输出。
- **final_ratchet `--full`**：无 `--coverage-scratch` → 非 0 且提示 `coverage-scratch`；
  带 scratch+target → `coverage: OK`，数据只落 scratch。

### before / after（节点开始前 vs 全部节点跑完后）

- `assurance/**` **1392 个文件**的内容 SHA + mtime **完全一致**（含三个 owner 日志、
  `rollback_manifest.json`、`assurance/backup/README.md`；`assurance/backup/` 只剩 `README.md`，无 `.read-probe`）。
- 仓库根 `.coverage*` 集合前后一致（均为 `{}`，未产生任何 coverage 数据文件）。
- `git status --porcelain -uall` 前后差异 = 本卡写集本身，无额外临时文件。

## 4. 清理与保护

| 项 | 状态 |
|---|---|
| `C:/Users/郑曾波/Projects/_g2/tmp-g2-rf-pt`（pytest basetemp） | 基线 absent → 已删除（删前核绝对路径包含 `_g2`、无 symlink/reparse；只读 `publications.jsonl` 先 `chmod` 再删） |
| `C:/Users/郑曾波/Projects/_g2/g2_before.json`（本卡快照） | 新建 → 已删除 |
| `.mypy_cache/`、`.pytest_cache/`、`.ruff_cache/`、各处 `__pycache__/` | 基线 absent → 已删除（全部 gitignored） |
| `tests/_g2_ruff_probe.py`（ruff 红路径探针） | 用例 `finally` 内删除，事后核实不存在 |
| `assurance/runs/daily_alert.jsonl`、`weekly_alert.jsonl`、`weekly_manifest.json` | **未提交、未 checkout、未 reset、未暂存**；本 worktree 与 HEAD 逐字节一致 |
| 主仓 `C:/Users/郑曾波/Projects/revenue-forecast` | 仍 `e241389a`，仅三个 owner 文件 modified（原状），本卡未触碰 |
| 其他历史 worktree | 未借用、未清理；其他 harness lane 的 python 进程未动 |
| `git clean` / 跨 shell 整串删除 | 未使用 |
| `scripts/**`、生产 config、forecast/evidence/narrative/source/closure 规则 | 未写 |
| `.github/workflows/quality.yml`、`tools/pre_push_gate.py`、hook | 未改 |
| CWP / FF / SW / ET / IQS / Dayu / installed 技能 | 未写 |

**计数**：`external_provider_calls=0`、`paid_calls=0`、`production_writes=0`、`raw_deleted=0`、
`network/download/llm=0`。不含任何密钥或原始外部响应。

## 5. 限制与既有漂移（如实记录，未在本卡扩大改造）

1. **`tests/test_ca303_arch_quality.py::test_c5_manifest_verifies_offline` 在本 worktree 红。**
   `uc.cli manifest-verify`（默认 `--mtime strict`）报 `audit_review/**` 的 mtime drift，
   全部指向 worktree checkout 时间 `2026-10-07 09:42:49`；本卡写集不包含 `audit_review/`。
   `manifest-verify --mtime off` → **OK（hash+size 全部复验通过）**。按卡片“三仓 manifest 冻结
   旧漂移不作为扩散改造理由”，未扩写 assurance。
2. **`uc.cli quality-verify` 在基线上就已经红**，且**不是**本卡造成的：
   `uc.quality.strict_targets()` 在 `quality.yml` 里找 `python -m mypy` 命令，而该 workflow
   早已改为单步 `python tools/pre_push_gate.py`（文件里只剩 pip 安装行的 `mypy==1.19.0`），
   于是 `compute_baseline()` 在走到 coverage 之前就 `ValueError`。
   卡片要求“strict_targets 旧漂移报告 MAIN、不为此改日常 workflow”，本卡照办。
   待 MAIN 处理 strict_targets 之后，`quality-verify` 才会进一步按 ratchet 语义报告
   coverage floor 从 84 降到 0 的“弱化”；按本卡规定**不重冻 manifest、不扩写整个 assurance**，
   `quality_baseline.json` 保持原样。
3. **本 worktree 的 `pre_push_gate` 需要兄弟 checkout。** `_g2/` 下没有 `filing-fetch` /
   `company-wiki`，而 `tests/test_p5_source_default_cli_e2e.py::_env_roots()` 默认找
   `ROOT.parent`。集中节点显式导出
   `FF_V2_CODE_ROOT=C:/Users/郑曾波/Projects/filing-fetch`、
   `CWP_V2_CODE_ROOT=C:/Users/郑曾波/Projects/company-wiki`（该测试**既有**的 env 覆盖，
   也是 CI 里 `ci_checkout_siblings.py` 的等价本地形态）。主仓在 `../` 就有兄弟，无需此变量。
4. **`--run`（全套）与本仓测试存在有界嵌套**：`run_coverage_gates --run`（默认 target `tests`）
   会跑到本卡的 CLI 驱动用例，而这些用例自己也会显式跑一次**窄 target** 的 `--run`/`--full`。
   嵌套深度为 2（`release_checklist` 经 `pre_push_gate` 为 3）且有界，不会递归；实测集中节点与
   `pre_push_gate` 均绿。若 MAIN 以后给 `--run` 加排除项，属新的设计决定，本卡未擅自加特例。
5. **容量/coverage/mypy 数字不再是门**，只报诊断。真实工具失败、pytest rc≠0（含 rc=2 收集失败）、
   启动失败、超时、非法配置、显式坏 SHA 仍然非零。
6. **缺 hash 仍是诊断、已提供而不符才失败**——本卡未恢复早期全 path 强制 hash，未改任何业务
   closure 规则（`uc.scenarios._evidence_problems` / `closure_report` 一行未动）。

## 6. 合并注意事项（MAIN）

- **已 push** `origin/codex/g2-rf-tools`（新分支）：
  `8a2c7fe9c25155631a01b083684b8524b38ccc40`（实现 + PWF）
  → `19aef7c4`（本交接文档）。push 时 pre-push gate 实跑 GREEN
  （ruff + 公共契约 mypy + 11 文件组 107 passed）；**main 从未 push、未合入、不写 installed**。
  该次 push hook 需要导出 `FF_V2_CODE_ROOT`/`CWP_V2_CODE_ROOT`（lane checkout 无兄弟目录），
  主仓不需要。
- **`installation_sync_pending = true`**：`tools/sync_installations.py` 的写集是
  `.gitignore/CHANGELOG.md/SKILL.md + agents/config/references/scripts/tests`，
  **含 `tests` 不含 `tools`**。本卡改了 6 个 `tests/**` 文件 ⇒ 安装副本待同步。
  交 MAIN 合入后**定点同步**；harness 未 run `--apply`，也未把安装差异变成新门。
- 合入后请复跑原日常快 CI（`python -B tools/pre_push_gate.py`）确认绿。
  不需要重新运行任何已绿的跨仓/付费节点。
- pre-commit hook（`ruff check (WU-1.2)` / `mypy public contracts (FC-1204-c)` /
  `host assumption guard (FC-1307-a)`）在本次 commit 上全部 Passed/Skipped。
- 若 MAIN 之后要退休 `uc.quality._revenue_coverage` 或扩大其读取写集，
  **先给出具体 caller 与反例**，不要擅自写整个 `assurance/`。

## 7. 入口速查

```powershell
# 默认：只读、零写、缺料 not_supplied
python -B tools/release_readiness.py
python -B tools/release_readiness.py --json

# 显式版本化输入（真实校验，坏输入/坏 SHA 非零）
python -B tools/release_readiness.py --expect-head revenue=<40-hex sha>
python -B tools/release_readiness.py --scenario-registry assurance/unified_completion/scenarios/scenario_registry.json
python -B tools/release_readiness.py --catalog <path.sqlite3> --backup-dir <dir> --budget-mb 2048

# 唯一显式写点（check-only 永不写）
python -B tools/release_readiness.py --record-rollback <path.json>

# coverage：默认只报告；--run 才跑一次且数据只落 scratch
python -B tools/run_coverage_gates.py
python -B tools/run_coverage_gates.py --run --scratch <DIR> [--target tests/test_x.py]

# 六门：默认轻检查；--full 才跑 coverage
python -B tools/final_ratchet.py --print-json
python -B tools/final_ratchet.py --full --coverage-scratch <DIR>

# 发布清单：薄委托 + 真实 returncode
python -B tools/release_checklist.py
```
