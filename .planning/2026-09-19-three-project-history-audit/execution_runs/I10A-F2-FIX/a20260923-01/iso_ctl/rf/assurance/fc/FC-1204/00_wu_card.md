# FC-1204 WU 卡片 — 类型、覆盖率、复杂度 ratchet（a/b/c 子链，Interpretation A）

> 创建 2026-08-12。Owner: 三仓。前置：FC-1203 ✓ accepted。基线实测见 findings 60/61。
> 用户全授权（2026-08-12）。a/b/c 子链按 FC-906 先例（runbook §10 过大 FC 拆分）。

## FC-1204-a：branch coverage（阈值实测后冻结，code_quality_plan §3）

1. **filing**：补缺行测试至 TOTAL ≥90（既有 pyproject fail_under=90 从未达）+ filing_contracts ≥95；quality.yml 加 `pytest --cov=scripts --cov-branch --cov-fail-under=90` 步骤（required）。
2. **wiki**：新 ratchet 测试 `tests/contract/test_fc1204_coverage_ratchet.py`——critical 契约链（source_bundle/admission/flags/policy/normalized_meta/runtime_policy/activation/close_gap/artifact_handle/acquisition_journal/canary_registry/producer_events/prompt_injection/url_binding/visibility_bridge/service/resolver/scheduler_policy/restore）≥95%；其余模块冻结实测值（normalizer 55/security_identity 77/startup 61/worker 79/store 83/scanner 91 等——注明 R2-R9 资产/legacy 理由）。门实现：pytest-cov per-module JSON 读值 + 断言（与 coverage run 分离，避免套件加时）。
3. **revenue**：run_coverage_gates.py 已有 branch + fail_under——验证当前绿色并记录基线。

## FC-1204-b：complexity ratchet

1. 每仓 ratchet 测试（AST McCabe，同 findings 60 算法）：冻结 per-module max-CC（实测值）；新/改代码 >10 必败。
2. 拆分顶 2 个纯函数段（行为由既有场景锁定）：
   - revenue `scripts/revenue_report.py:_validate_forecast_output`（CC174/1083 行）→ 按验证块提取纯函数，顺序调用；test_output_report.py ~100 测试锁行为。
   - wiki `resolver.py:SourceResolver.resolve`（CC103/288 行）→ 拆 pipeline 阶段（identity → candidates → handles → envelope）；resolver 契约测试锁定。
3. 其余顶端（cli.main 140、_scan_root_v1 140 [R9]、_scan_catalog_impl 102、worker.run_cycle 99、validate_management_target_coverage 88）冻结 + 记录下降目标（R9/后续）。

## FC-1204-c：strict type check（mypy）

1. 三仓 mypy 配置（ignore_missing_imports=yaml）；契约模块集零容忍：
   - wiki：artifact_handle/source_bundle/runtime_policy/activation/close_gap/policy_2x/canary_registry/normalized_meta/flags/policy/restore（现 1 error）
   - filing：scripts/filing_contracts.py + fetch_filing.py（现 0 error）
   - revenue：contracts/ + schema_compatibility + filing_fetch_client + trust_anchor（现 35 errors，修完）
2. 三仓 CI 加 mypy 步骤（required）。

## exit gate（Phase 12 汇总项）

- filing TOTAL branch ≥90 + contracts ≥95（CI 门）；wiki critical 集 ≥95 + 其余冻结（ratchet 测试）；revenue gates 绿。
- 三仓 complexity ratchet 测试绿；新代码 CC>10 必败；顶 2 拆分后行为零回归（全量套件）。
- mypy 契约模块集三仓 0 error（CI 门）。
- ruff/compileall/unique-test-symbol 跨平台绿（已有）。

## 不变式

- 阈值全部来自实测（findings 60/61），不虚构；任何降低 = 新 FC + owner + 到期。
- 拆分是纯重构：零行为变化（全量套件 + 代表性 fixture hash 不变）；不做跨模块移动。
- 零生产数据/写路径变化；worker 无需重启（不触碰 producer 写路径）。
- 禁止为了过阈值改写/删除测试。
