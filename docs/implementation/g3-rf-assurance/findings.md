# G3-RF-ASSURANCE findings

## 1. 环境与基线（Phase 1）

- 施工仓 worktree：`C:/Users/郑曾波/Projects/_g3/RF-ASSURANCE/revenue-forecast`，分支 `codex/g3-rf-assurance`，base `1a2f9428a599504eb8355fcaebf86c6cbcaccbb3`。
- 原仓 `Projects/revenue-forecast` 有 3 个已修改的 owner 日志（`assurance/runs/{daily_alert,weekly_alert}.jsonl`、`weekly_manifest.json`）——本卡禁止写，worktree 内这 3 个文件保持干净。
- **邻仓在本卡环境缺失**：`DEFAULT_REPOS["filing"|"wiki"]` 解析到 `root.parent/{filing-fetch,company-wiki}` = `Projects/_g3/RF-ASSURANCE/{filing-fetch,company-wiki}` → 不存在。真实邻仓在 `Projects/{filing-fetch,company-wiki}`（只读探查过）。
  这正是卡 RED 清单里的“邻仓不在”。
- 真实邻仓存在时：`company-wiki/tests/contract/test_fc1204_complexity_ratchet.py` **已不存在**（wiki 已演化）→ `_wiki_complexity` 会 `ValueError`。因此“邻仓在但其历史规格文件缺失”必须按 scope 报告，不能当失败。
- python 3.13.9，ruff 0.15.18（与 CI pin 一致）。

### 基态（base commit，worktree 内实测）

| 测试包 | 结果 |
|---|---|
| `assurance/.../tests/test_zr104_quality.py` | **RED**：`strict_targets` 抛 `ValueError: no 'python -m mypy' command found in .github/workflows/quality.yml` |
| `assurance/.../tests/test_manifest.py` | 1 failed（`test_real_repo_offline_reverification`：30 条 mtime drift），14 passed |
| `tools/tests/test_sync_installations.py` | 4 passed |
| `tests/test_ca303_arch_quality.py` | 1 failed（C5 `manifest-verify` 默认 strict mtime），10 passed（C4 mypy/C3 ratchet 都过） |

`python -m uc.cli manifest-verify --mtime off` 在本 worktree → `OK` exit 0，**没有真实 hash/size 漂移**（即卡里说的“与本项无关真实坏SHA”不存在）。

## 2. quality.py 实际入口 / caller / 副作用

导入 API（必须保持）：`freeze`、`verify`、`strict_targets`、`compute_baseline`、`check_critical_complexity`、`product_tree_sha`、`MAX_CRITICAL_COMPLEXITY`、`PRODUCT_TREE_PATHS`、`SCHEMA_VERSION`/`UNIT`/`REPO_ORDER`/`DEFAULT_REPOS`/`FROZEN_AT_UTC`/`NEW_FILE_MAX`，以及 `_revenue_coverage`（`tests/test_rf_coverage_report.py`、`tools/run_coverage_gates.py` 文档都引用它作 AST reader）。

- 唯一生产 caller：`uc/cli.py:43-44` `quality_freeze` / `quality_verify` → 子命令 `quality-freeze`（写 `assurance/unified_completion/quality/quality_baseline.json`，CAS）、`quality-verify`（problems 非空 → exit 1）。
- 测试 caller：`tests/test_zr104_quality.py`（导入 `MAX_CRITICAL_COMPLEXITY/PRODUCT_TREE_PATHS/check_critical_complexity/compute_baseline/freeze/product_tree_sha/verify`）。
- **没有外部 caller** 用 `_verify_*` 内部函数 → 可安全把 ratchet 比较逻辑搬进新 report 模块。
- 写副作用：只有 `freeze()` 通过 `casfile.cas_update/exclusive_publish` 写 baseline；`verify/compute_baseline/strict_targets/check_critical_complexity` 全只读（`git rev-parse` 只读）。
- `_verify_*` 五组比较（types/coverage/complexity/hardcoding/dead_callers）+ `product_trees` 相等 + `input_hash` 相等，现在全部是**退出码门**（进 `problems` → exit 1）。

### 谁是“历史解码”、谁是“真当前用户工具”

| 符号 | 判定 | 依据 |
|---|---|---|
| `strict_targets(revenue)` | **真当前工具，但已失真** | 读 `quality.yml` 找内联 `python -m mypy`；该 workflow 现已委托 `run: python tools/pre_push_gate.py`，内联 mypy 只剩在 `tools/pre_push_gate.py:94`（targets=`scripts/contracts/` `scripts/schema_compatibility.py` `scripts/filing_fetch_client.py` `scripts/trust_anchor.py` → rglob 展开 = 冻结的 7 个文件，与 baseline 完全一致） |
| `strict_targets(filing/wiki)` | 邻仓自己的 CI 定义（仍是内联 mypy） | `filing .github/workflows/quality.yml:36`、`wiki .github/workflows/ci.yml:46` 仍内联 `python -m mypy` |
| `_revenue_coverage` | **历史报告解码器（保留）** | G2 已把 `.coveragerc fail_under=0`、`PER_MODULE_MINIMUM={}`；`tests/test_rf_coverage_report.py` 显式断言它还能 AST-read |
| `_verify_coverage` 的“floor 丢失/下降” | **退休工程门 → 诊断** | 84→0 / 8 模块 floor→`{}` 是 G2 刻意退休，不是弱化 |
| `_verify_types` / `_verify_complexity` / `_verify_hardcoding` / `_verify_dead_callers` / `product_trees` / `input_hash` | **诊断** | 卡：覆盖率/复杂度/固定历史数量/无关邻仓HEAD/旧workflow文本差异是诊断；跨仓 product_tree 漂移按历史对比报告 |
| `check_critical_complexity` | 真当前工具（AST McCabe，零依赖） | 被 `_complexity_for` 文案引用，语义未变，保留 |
| `freeze` | 真当前工具（一次性 CAS 写） | 保留，不新增重冻要求 |

## 3. manifest.py 实际入口 / caller / 副作用

- `verify(repo_root, manifest_path, check_mtime=True)` → `list[str]` problems；`check_mtime=False` 已存在（hash+size 仍校验）。
- `build(repo_root, output, force_sha256=None)` → 写 manifest（exclusive 或 CAS）。
- caller：
  - `uc/cli.py:79-91 _require_no_drift()`（`check_mtime: bool = True` 默认）→ 被 `state-bootstrap(179)`、`lock-acquire(126)`、`state-update(230)`、`closure-advance(542)`、`env-freeze(764)` 调用。
  - `uc/cli.py:110-122 cmd_manifest_verify`：`getattr(args, "mtime", "strict") == "strict"`。
  - CLI 五处 `--mtime {strict,off}` **默认 strict**：`manifest-verify(876-883)`、`lock-acquire(885-895)`、`state-update(914-926)`、`closure-advance(978-989)`、`env-freeze(994-1001)`。
  - `tools/drift_patrol.py:136` 已经显式传 `--mtime off`。
  - 测试：`test_manifest.py`（默认 strict 的两处）、`test_zr905_audit_self_test.py:209/217`、`test_zr907_drift_patrol.py:79`（都显式 `check_mtime=False`，不受默认值影响）、`tests/test_ca303_arch_quality.py::test_c5_manifest_verifies_offline`（子进程跑 `manifest-verify` 默认值）、`tests/test_ca301_clean_checkout.py`（显式 `env-freeze --mtime off`）。
- 副作用：`verify` 纯只读；`build` 写。
- **缺口 1（路径逃逸）**：`verify` 直接 `repo_root / entry["rel_path"]`，`rel_path` 为绝对路径或含 `..` 时会读到仓外文件并可能“通过”。卡要求“路径逃逸…仍非零”→ 必须补。
- **缺口 2（坏输入未干净失败）**：manifest 文件缺失/非法 JSON → `FileNotFoundError`/`JSONDecodeError` 直接冒泡（traceback，非零但不干净）。卡要求“缺文件…仍非零”且“不能通过 build/update 自动修复坏输入”。
- `assurance/unified_completion/README.md:21-22,35` 文档写的是“严格：hash+size+mtime / `--mtime off` 干净 checkout 模式”——**不在本卡写集**，改默认值后会文档漂移 → 交 MAIN 精确接线表。

## 4. sync_installations.py 实际入口 / caller / 副作用

- `ROOT_FILES = (".gitignore","CHANGELOG.md","SKILL.md")`；`ROOT_DIRECTORIES = ("agents","config","references","scripts","tests")`。
- `installable_files`：缺目录 → `FileNotFoundError`；`manifest` = path→sha；`installation_diff` = **期望(owned) ∪ 实际(整棵树减 output/ignored)** 全量比对 → 任何残留/未知文件都算 DIFF（“全 MATCH 门”）；`sync_installation` = **整目录替换**（staging → `os.replace` 旧树到 backup → 换新树 → 只恢复 `output` → 删 backup）→ 未知文件/用户配置会被删。
- `main()`：无 `--apply` 时纯读（check-only 0 写）✓；`--apply` 写；`--print-manifest`/`--import-from` 只读/写 canonical。
- caller：
  - `tools/drift_patrol.py:66`（check 模式，只读）
  - `tests/test_zr804_platform_shape.py:169-180` `_sync_installations()` → **真实 `--apply` 到 `~/.agents`、`~/.codex`**（本卡禁止在用户安装目录 apply，所以本卡不跑这个测试）
  - `tests/test_fc1004_platform.py:89,99` → `--apply --destination <tmp>`（两个 tmp 树比对，集合改了仍然两两相等 → 不受影响）
  - `tests/test_rf_release_checklist.py:63`、`tests/test_ci_smoke_plan.py:26,40` 断言这些门**不**在 release/smoke 集合里
  - `tools/release_checklist.py`（G2 已移除 sync 仪式，源码里不得再出现 `sync_installations`）
- **真实运行时闭包实测（静态扫描 `scripts/ agents/ config/ references/` 全部文本）**：
  ```
  tests:0   tools:0   assurance:0   audit_review:0   compatibility:0   e2e:0   examples:0
  ```
  → 运行时**没有任何**对 `tests/`、`tools/` 的 import 或路径引用。`scripts/revenue_forecast.py` 顶部只 `from revenue_core ... / from revenue_report ...`。
  → “纯 tests/** 全部移除后漏掉真正 runtime import”的风险 = 0（有扫描证据）。
- **边界外 caller（卡要求只交 MAIN 精确接线表）**：
  - `scripts/revenue_forecast.py:73-95` `--version` 自带 `_root_directories = {"agents","config","references","scripts","tests"}`（注释明写 “Match tools/sync_installations.py installable_files”）。**不在本卡写集（禁止改预测）**。包装集合一改，canonical 与安装副本的 `manifest_sha256` 就不再相同 → `tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity` 的 `copy_out.stdout == canonical_out.stdout` 断言会红。→ HANDOFF 精确接线项。
- 三个安装副本现状（只读探测）：`~/.agents/skills` 与 `~/.codex/skills` 各 24 个文件 DIFF（本来就落后）；`~/.claude/skills` 的 `revenue-forecast` 是指向 `~/.agents` 的链接，被 `unique_destinations` 去重。**本卡不 --apply**。
- `references/*.md` 有 4 处文档性提到 `tests/test_*.py`（贡献者指引，非 runtime import）→ 交 MAIN 文档残留。

## 5. CI / hook（只读，不改）

- `.githooks/pre-push` → `python tools/pre_push_gate.py`（ruff on scripts/tests/tools/e2e + mypy 4 文件 + 11 个 SMOKE_TESTS）。`tests/test_ca303_arch_quality.py`、`test_zr104`、`test_manifest`、`test_sync_installations` 都**不在**这 11 个 smoke 文件里。
- `.github/workflows/quality.yml`：sparse-checkout 不含 `assurance/`、`audit_review/`，只跑 `tools/pre_push_gate.py`。
- 所以本卡改动不影响日常 CI 的 107 项；卡要求的最后跑一次 `python tools/pre_push_gate.py` 用作回归确认。

## 6. 关键决策（写前定）

1. **quality 层 → 报告**：`failures`（闭集：真正输入损坏 / 显式输入不可读 / 非法配置 schema+unit / 实际进程非零）+ `diagnostics`（其余全部：ratchet 数值比较、product_tree 历史漂移、邻仓 not_available、退休 coverage 门、旧 workflow 文本差异）。`verify()` 返回值仍是 `list[str]`（= failures），`cmd_quality_verify` 只按 failures 决定退出码；新增 `uc/quality_report.py` 承载报告与 `run_probe`。
2. **类型目标委托**：`strict_targets` 先读该仓 CI workflow 的内联 `python -m mypy`（filing/wiki 仍如此）；找不到内联则跟随 workflow 里对 `tools/*.py` 的**委托**（`python tools/<x>.py`），AST 解析被委托文件里的 `-m mypy` 目标 —— revenue 因此解析到 `tools/pre_push_gate.py`。不恢复 workflow 内联 mypy、不执行 YAML 文本、不重新冻结。
3. **scope 规则**：`revenue`（本仓）源文件缺失/损坏 → failure；`filing`/`wiki` 任何解析失败或目录缺失 → `{"status":"not_available","scope":...}` 诊断，绝不造 0、绝不隐式复制 revenue 的集合；git/tree 解析失败（含非 git 的 scratch root）→ `not_available` + scope。
4. **manifest**：`verify(..., check_mtime=False)` 默认（SHA+size），`check_mtime=True` = 显式旧 strict；CLI 五处 `--mtime` 默认 `off`、`strict` 显式；默认模式额外打印 mtime `NOTE:` 诊断（不改退出码）；新增路径逃逸拒绝 + `ManifestError` 干净退出 1；`verify`/`manifest-verify` 全只读、绝不触发 build 修复。
5. **包装**：`ROOT_DIRECTORIES = ("agents","config","references","scripts")`（`tests/` 退出默认运行包，静态扫描证明无 runtime import）；`installation_diff` 只比 owned runtime；`sync_installation` 改为 tmp staging + 定点逐文件原子替换，保留未知文件/用户配置/`output`，不再整目录替换；`import_installation`/`unique_destinations`/`main` 旧签名不变。

## 7. 实施后的补充事实（Phase 3-6）

- `scripts/contracts/*.py` 恰好 4 个文件 → 委托 `tools/pre_push_gate.py` 后解析出的 revenue strict 目标集 = 4 + `schema_compatibility.py` + `filing_fetch_client.py` + `trust_anchor.py` = **7 个文件，与冻结 baseline 完全一致**，即类型维度零漂移。
- revenue 产品子树当前 `958b0b40…` ≠ 冻结 `6bcba49a…`（P5/叙述/G2 之后 scripts 变过）；filing 冻结 `18f0a8df…`、wiki 冻结 `3eaac52d…` 在真实邻仓现 HEAD 下分别是 `c671919d…`、`e35f4c8d…`。三者全部按**历史对比报告**，不再阻断。
- 真实邻仓 `company-wiki` 里 `tests/contract/test_fc1204_complexity_ratchet.py` **已不存在** → 若把“邻仓在但规格文件缺失”当失败，`verify` 会在别人的主仓 checkout 变红。因此 scope 规则定为：**本仓(revenue)不可读 = failure；邻仓不可读/缺失 = not_available 诊断**。
- `python -m uc.cli manifest-verify --mtime off`（改动前/后同一结果）= `OK` exit 0，**没有**与本项无关的真实坏 SHA，因此不存在需要如实上报的剩余坏哈希。
- 路径逃逸缺口实测：base 时把 `../secret.md`（存在且 SHA/size 匹配）塞进 manifest → `verify` 返回 `[]`；现在返回 `path escapes repository root`。
- 包装集合改动的边界外 caller 实测（只读，未动用户安装目录）：
  - 新集合 `installable_files(REPO_ROOT)` = **75 个文件**（root 3 + agents/config/references/scripts），无 `tests/`、`tools/`、`assurance/`。
  - tmp 安装后 `python scripts/revenue_forecast.py --version`：canonical `manifest_sha256=c58de2c159dcfcf5`，安装副本 `76b37ec851b558eb` → **不一致**，原因就是 `scripts/revenue_forecast.py:81` 自带的 `_root_directories` 仍含 `"tests"`（该文件不在本卡写集）。→ HANDOFF 精确接线项。
- 三个安装副本（`~/.agents`、`~/.codex`，`~/.claude` 是指向 `.agents` 的链接被去重）在**改动前就已 24 文件 DIFF**；本卡未执行 `--apply`，DIFF 只会因集合收敛而变小，不会被本卡修复。
- 本卡 13 个改动/新增 Python 文件单独 `ruff check`：`All checks passed!`；`pre_push_gate` 的 ruff 段（scripts/tests/tools/e2e）同样全绿。
