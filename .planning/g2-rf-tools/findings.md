# Findings & Decisions (G2-RF-TOOLS)

## Requirements

- 默认可选检查真正只读本仓 + 明确指定的版本化输入；数值诊断，不要求邻仓/备份/签收。
- 真实类型/测试/配置错误、工具异常、提供的坏 SHA 仍失败。
- 全套仅在集中命令，不每 session 或 helper 重复。
- check-only 成功/失败均零文件写（不造 probe/rollback/receipt/.coverage）。
- 三 scanner API 与真反例保留；`.coveragerc fail_under=0`、`PER_MODULE_MINIMUM={}` 兼容形状保留。

## Research Findings

- 基线：main=`e241389adeda37bc9cbb53d7831063718552a936`（`Use public information date for narrative source eligibility`），`git status --short` 仅三个 owner 文件 modified：`assurance/runs/daily_alert.jsonl`、`weekly_alert.jsonl`、`weekly_manifest.json`。
- 环境：Python 3.13.9、pytest 9.1.1、ruff 0.15.18、mypy 1.19.0、coverage 7.12.0 均可用。
- `tools/release_readiness.py` 现状问题：
  - `REPOS` 指向 `ROOT.parent/filing-fetch` 与 `company-wiki`，`catalog_integrity()` 打开 `company-wiki/.source_catalog/catalog.sqlite3`（邻仓内部 SQLite）。
  - `scenario_evidence_integrity()` 硬要 `total_scenarios == 197`。
  - `capacity_ok()` 硬要 ≤2048MB；`backup_readable()` **写** `assurance/backup/.read-probe`；`write_rollback_point()` **写** `assurance/runs/rollback_manifest.json`（该文件是 git 跟踪的证据文件）→ 默认每次运行都改跟踪文件。
- `tools/run_coverage_gates.py` 现状问题：`main()` 第一步 `coverage erase`（抹掉用户现存 `.coverage`），随后无条件启动 900 秒全套 pytest + 8 模块 40–80 门 + `fail_under=84`。
- `tools/final_ratchet.py` 现状问题：`gate_type()` 用 `errors <= MYPY_BASELINE(69)` 宣称绿；`run_all()` 默认无条件跑 complexity + mypy + coverage（coverage 又跑全套）。
- `tools/release_checklist.py` 现状问题：自己复制 `pytest tests -q` 全测，只解析 `FAILED` 行 + `EXPECTED_RED={"test_structure_targets.py"}` 固定免责（pytest rc=2 收集失败无 FAILED 行会误报成功）；另把固定迁移文档、`sync_installations` 全 MATCH/`--apply`、`mutation_patrol` 当每发布资格。
- `tools/session_checklist.md` 现状要求：每会话全测绿 + 真实 E2E + 安装全 MATCH + 配置 checkout 到 HEAD。
- `.coveragerc` 现状 `fail_under = 84`；`run_coverage_gates.PER_MODULE_MINIMUM` 8 条 40–80。
- 兼容读取器：`assurance/unified_completion/uc/quality.py::_revenue_coverage` 用 configparser 读 `.coveragerc [report] fail_under`、用 AST 读 `tools/run_coverage_gates.py` 的 `PER_MODULE_MINIMUM` 字面量 dict；缺任一 → `ValueError`。故两者必须保留**可解析形状**。
- `quality_baseline.json` 冻结值为 `total_floor: 84.0` + 8 条 per_module_floors；`uc.cli quality-verify` 会拿它和 live 重算比对 → 降为 0 会报 QUALITY-VIOLATION。按卡片：旧 quality-verify 三仓冻结要求**退出本卡施工说明**，不重冻 manifest、不扩写 assurance。
- `uc.quality.strict_targets()` 按旧 workflow 找 mypy 是既有历史漂移 → 报告 MAIN，不改日常 workflow。
- scanner 导入者（必须保留 API）：`tests/test_ca303_arch_quality.py`、`tests/test_ca304_r9_removal.py`（`fr.scan_legacy`/`fr.scan_encoding`）、`tests/test_zr1102_adversarial_audit.py`（`scan_encoding/scan_hardcode/scan_legacy`）。
- `tools/sync_installations.py` 的 `ROOT_DIRECTORIES = (agents, config, references, scripts, tests)` → **tests 在安装集内、tools 不在**。本卡改 tests ⇒ 安装副本待同步，交 MAIN 合入后定点同步；harness 不 run `--apply`。
- `.github/workflows/quality.yml` 只跑 `python tools/pre_push_gate.py` 一步；`test_ci_smoke_plan.py` 断言单 job、单 gate、且 run 中不含 `run_coverage_gates/mutation_patrol/sync_installations/verify_plan_claims` → 本卡不得把这些塞回 workflow。
- `tools/pre_push_gate.py` 的 11 文件离线行为组 + ruff + 公共契约 mypy 是日常 CI 契约，本卡不改。
- `scripts/publication_registry.py audit` 只读（写入仅 register 路径）。
- `SKILL_VERSION = '4.1.0'`，`CHANGELOG.md` 有 `## 4.1.0 (2026-09-18)` 段。
- `assurance/runs/rollback_manifest.json` 与 `assurance/backup/README.md` 是跟踪文件。
- 本仓 `.planning/` 与 `docs/implementation/` 均被 git 跟踪。

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| gate 结构 `{"ok","status","detail"}`，status∈{ok,red,not_supplied,diagnostic} | 「未提供报告 not_supplied，而非伪称已经验真」，同时保留原 JSON/CLI 字段 |
| 邻仓/backup/197/2GB 默认 not_supplied 或 diagnostic | 卡片目标：不要求邻仓/备份/签收；数值诊断 |
| 显式输入 `--catalog/--scenario-registry/--backup-dir/--expect-head/--budget-mb` | 「明确指定的版本化输入」，坏输入/坏 SHA 真实非零 |
| `--record-rollback PATH` 显式才写 | check-only 零写；发布/rollback 由既有发布层处理 |
| coverage 数据只落 `--scratch`，用 `COVERAGE_FILE` 指向 | 不 erase 用户现存 `.coverage`，不在仓根造数据文件 |
| mypy：rc≥2 / 缺失 / 异常 / 超时 → red；rc=0/1 → 按真实错误数 diagnostic | 「不以不超过69宣称无错误」+「不能将 mypy 故障显示绿」+「任意历史错误计数不单独阻断」 |
| `release_checklist` 委托 `pre_push_gate.py` 与 `release_readiness.py`，按真实 rc | 「薄委托既有检查，不再另复制一套全测」 |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
|       |            |

## Resources

- 卡片：`C:/Users/郑曾波/Projects/company-wiki/docs/plans/narrative-evidence-pilot-2026-09-26/harness_lanes/g2_revenue_forecast_optional_tools.md`
- worktree：`C:/Users/郑曾波/Projects/_g2/revenue-forecast`（分支 `codex/g2-rf-tools`）
- 兼容读取器：`assurance/unified_completion/uc/quality.py::_revenue_coverage`
- scanner 消费者：`tests/test_ca303_arch_quality.py`、`test_ca304_r9_removal.py`、`test_zr1102_adversarial_audit.py`

## Visual/Browser Findings

- 无（本卡纯文本工程改造）。

---

*Update this file regularly during research so important evidence remains available after context changes.*
