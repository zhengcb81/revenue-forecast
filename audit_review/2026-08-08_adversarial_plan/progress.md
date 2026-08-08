# 审查进度日志

## 实施回执（WU-3.1 fail-closed 状态和路径过滤）

```json
{
  "work_unit": "WU-3.1",
  "baseline_commits": {"revenue": "cbee0c2", "filing": "0d58b3e", "wiki": "74a7b74"},
  "red_test_ids": ["test_quarantined_document_not_reused (was REUSED_EXACT before fix)", "test_upstream_rejected_document_not_reused (was REUSED_EXACT)", "test_rejections_path_not_reused (was REUSED_EXACT)", "test_query_hides_non_active_by_default (upstream_rejected leaked)", "test_resolver_defense_in_depth_rejects_leaked_document"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/src/company_wiki/source_catalog/service.py (query active-only default)", "company-wiki/src/company_wiki/source_catalog/resolver.py (source_status defense-in-depth + .rejections path filter)", "company-wiki/tests/contract/test_source_catalog_fail_closed.py (7 tests)", "company-wiki/tests/contract/test_source_catalog_url_enrichment.py (explicit active+incomplete query)", "company-wiki/tests/contract/test_source_catalog_dropbox_probe.py (real sha256 fixture)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_fail_closed.py -v", "python -m pytest tests/contract/test_source_catalog_url_enrichment.py -q"],
  "repo_commands": ["python -m pytest tests/contract -q (960 passed, 1 pre-existing flaky→fixed)"],
  "cross_repo_commands": ["not_applicable + company-wiki only WU"],
  "tests_collected_before": 1616,
  "tests_collected_after": 1623,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "production_evidence": {"previously_leaked_candidates": "189 upstream_rejected + 1 quarantined documents; 635 dayu .rejections active locations", "post_fix": "all fail-closed; zero rejected candidates reach success receipt"},
  "mutation_proof": {"query_allowlist_revert": "RED (test_query_hides_non_active_by_default failed)", "resolver_check_removal": "RED (test_resolver_defense_in_depth_rejects_leaked_document failed)"},
  "reviewer": "pending (agent-skills:code-reviewer)",
  "review_findings": [],
  "status": "implemented → focused 22 green → contract suite green → pending independent review"
}
```

## 实施回执（WU-2A.0~2A.2 Dropbox 配置启用 — 用户决策后完成）

```json
{
  "work_unit": "WU-2A.0/2A.1/2A.2",
  "baseline_commits": {"revenue": "6dc6cd6", "filing": "cdcbf58", "wiki": "96d112d"},
  "user_decision": "2026-08-08: 先只做配置 + 记录缺口 (E2E 按负例验收)；runtime 缺口按 F-034 修正记录",
  "red_test_ids": ["test_probe_missing_when_directory_kind_not_reusable (RED before config)", "test_config_dbx_01... (RED under mutation: directory removed from reusable)", "test_config_dbx_03... (RED under mutation: Dropbox allowance removed)"],
  "red_exit_code": 1,
  "changed_files": [
    "wiki: config/source_catalog.yaml (reusable_root_kinds +directory), tests/contract/test_source_catalog_dropbox_probe.py, tests/contract/test_dropbox_config_invariants.py",
    "filing: config/company_wiki.json (+Dropbox/Stock), tests/test_dropbox_config_invariants.py"
  ],
  "focused_commands": ["python -m pytest tests/contract/test_dropbox_config_invariants.py -q", "python -m pytest tests/test_dropbox_config_invariants.py -q", "python -m pytest tests/contract/test_source_catalog_dropbox_probe.py -v"],
  "repo_commands": ["filing full offline: 118 passed + 27 subtests (46.03s)", "wiki related contracts: 13 passed"],
  "cross_repo_commands": ["CONFIG-DBX-04: wiki YAML realpath == filing JSON allowance realpath (test in filing repo)"],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "runtime_diff": {"wiki_src_scripts": "empty", "filing_scripts_tools": "empty", "revenue_scripts": "empty"},
  "config_hashes": {"source_catalog": "384ef4818fd4835cdecf34de1ba309afd6db3861b87d108bd84f5950d1ef6fa8", "company_wiki_json": "cfcb8dbeaa2b5ce40f44294beae4033c6fff486232da43a405054afa4db0f7aa"},
  "mutation_proof": {"remove_directory_from_reusable": "RED (DBX-01 failed)", "remove_dropbox_allowance": "RED (DBX-03 failed)"},
  "known_gap": "F-034 revised: directory-root sidecar metadata not persisted to acquisition/dayu_meta keys → resolver._source_metadata()={} → form_type/identity/https_url fail. Probe test asserts current MISSING behavior with flip-to-REUSED_EXACT block documented.",
  "status": "configuration_enabled (user-decision mode); production_reuse_verified NOT claimed — runtime gap documented, E2E-DBX positive cases deferred until scanner fix decision"
}
```

- WU-2A.0~2A.2 提交：wiki `(see log)`、filing `(see log)`。CONFIG-DBX-01~04 全绿；探针 2 项全绿（已知缺口断言）。
- **剩余**：E2E-DBX-01~10（正例需 scanner 修复后按 REUSED_EXACT 验收；负例可先做）、WU-2A.4 生产 canary（前置 WU-3.1）、WU-2A.5 回滚门（可做）。

## 实施回执（WU-2A.0 配置能力 RED 探针 — BLOCKED）

```json
{
  "work_unit": "WU-2A.0",
  "baseline_commits": {"revenue": "6dc6cd6", "filing": "cdcbf58", "wiki": "96d112d"},
  "red_test_ids": ["test_probe_missing_when_directory_kind_not_reusable", "test_probe_reused_exact_when_directory_kind_reusable"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/tests/contract/test_source_catalog_dropbox_probe.py", "revenue-forecast/audit_review/2026-08-08_adversarial_plan/progress.md"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_dropbox_probe.py -v"],
  "repo_commands": ["not_applicable + probe-only WU; no config/runtime change"],
  "cross_repo_commands": ["not_applicable + blocked before filing-fetch side"],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "status": "user decision 2026-08-08: 先只做配置 + 记录缺口 (E2E 按负例验收)。blocked 解除，进入配置-only 快车道；runtime 缺口按 F-034 修正记录，不伪称复用可用"
}
```

### Blocker 根因（WU-2A.0 探针证据链）

1. **scanner.py:1072-1077**：`document_metadata` 只对 `company_raw`/`dayu_portfolio` 根把 sidecar 元数据写入 `acquisition`/`dayu_meta` 嵌套键；`directory` 根两者均为 `null`。
2. **resolver.py `_source_metadata()`（:275-283）**：只读 `metadata["acquisition"]`/`metadata["dayu_meta"]` → directory 根文档恒返回 `{}`。
3. 空 metadata 连锁失败（真实 resolver 输出）：
   - `form_type_mismatch`（form_type 缺失）
   - `identity_unverifiable_strict`（market/security_id 缺失，弱身份 fail-closed）
   - `capture_incomplete`（https_url 缺失 → capture_ready=False）
4. **生产 catalog 佐证**：dropbox root 下无 active 官方财报（annual 371 全 retired、quarterly 56 retired、semi 128 retired；唯一 active semi-annual 的 metadata 实际 root_id=company_raw）。
5. 替代路径不可行：改 Dropbox kind 为 dayu_portfolio 违反 §2.4（禁改 kind/path/priority）且 scanner dayu 分支要求 portfolio/meta.json 结构（Dropbox 是 重点关注/*.pdf.source.json，不匹配）；无其它受支持 kind 能表达。

### F-034 修正

原 F-034 声称"当前 schema 已能通过两处配置完成"。探针证伪：**两处配置是必要条件但非充分条件**——resolver 的身份/form/url 读取依赖 `_source_metadata()`，而 directory 根扫描不持久化 sidecar 元数据到该函数可读的键。要启用 Dropbox 复用，最小 runtime 修改是：scanner 对 directory 根（或至少 dropbox_stock 的 重点关注 子树）把 sidecar 元数据写入 `acquisition` 键（≈ 数行，属 WU-2A.0 明令禁止的 runtime 改动，须用户另行授权）。

### 探针测试保留

`test_source_catalog_dropbox_probe.py` 两个测试作为能力边界 RED 证据保留在仓库（当前红灯是正确状态——证明能力缺失）；不得标绿、不得 skip。

## 实施回执（WU-1.2 清理并冻结静态质量范围）

```json
{
  "work_unit": "WU-1.2",
  "baseline_commits": {"revenue": "1bb810a", "filing": "43330550fb3ea77d36acd92e26861377564a7607", "wiki": "fdc196f+6f732cb"},
  "red_test_ids": ["RED1: appended unused import → ruff check 2 errors", "RED2: appended syntax error → compileall error", "RED3: duplicate test → check_unique_test_symbols exit 1 (WU-1.1 mutation)"],
  "red_exit_code": 1,
  "changed_files": [
    "revenue: scripts/revenue_core.py (25 dup constants removed, F821 Path import, E402 noqa re-export, __all__ 71 names, 13 private re-imports dropped), 9 split modules (F401 auto-fix), 6 test files, tools/check_unique_test_symbols.py, tools/mutation_patrol.py, tools/release_checklist.py, e2e/run_revenue_forecast_e2e.py, .github/workflows/quality.yml",
    "filing: .github/workflows/quality.yml (ruff + compileall + import smoke)",
    "wiki: tests/contract/test_source_catalog_reusable_roots.py (unused pytest), .github/workflows/ci.yml (ruff gate)"
  ],
  "focused_commands": ["ruff check scripts tests tools e2e --no-cache (revenue 185→0)", "python -m compileall -q scripts tests tools e2e"],
  "repo_commands": ["python -m pytest tests -q (revenue 301)", "python e2e/run_revenue_forecast_e2e.py (PASS)", "filing pytest offline 115 passed (47.31s)", "wiki ruff check src tests/unit tests/contract scripts (pass)"],
  "cross_repo_commands": ["not_applicable + per-repo static gates; cross-repo CI wiring belongs to WU-7.1"],
  "tests_collected_before": 0,
  "tests_collected_after": 0,
  "collection_delta": "not_applicable + no test collection changes (WU-1.1 handled symbols; this WU is lint/CI only)",
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "per_file_ignores_added": 0,
  "per_file_ignores_kept": "wiki scripts/*.py E402/E741/F401 (legacy sys.path pattern, 104 isolated errors — pre-existing, not expanded); wiki 4 unit-test E402 files (pre-existing)",
  "revenue_ruff_delta": "185 errors → 0 (F401×149→~0, F811×25→0, E402×9→0, F841×1→0, F821×1→0)",
  "api_surface_verified": "revenue_core.__all__ 71 names all importable; FORECAST_SCHEMA_VERSION=3.7; external imports intact",
  "reviewer": "agent-skills:code-reviewer (agentId a782593d0ce270fb0)",
  "review_findings": [
    {"severity": "minor", "desc": "wiki 存量 per-file ignores 无 issue ID/到期日/owner 注释", "resolution": "accepted as follow-up; 非本 WU 新增，WU-7.1 补注"},
    {"severity": "minor", "desc": "revenue_core 内联 noqa 无 issue 注释", "resolution": "accepted as follow-up; 行级豁免 + __all__ 背书，未违反门禁"},
    {"severity": "minor", "desc": "revenue 根目录 NUL 残留文件（Windows 设备名）", "resolution": "noted; 非本 WU 引入，不擅自删除"}
  ],
  "status": "accepted (mutation-proved RED for unused-import and syntax-error; all gates green)"
}
```

- 过程记录：revenue_core.py 修改曾因 RED 恢复操作失误被 `git checkout` 回滚到 HEAD（WU-1.2 变更丢失），已用幂等脚本完整重建并复验（ruff 0、API 完整、301 tests、E2E PASS）。教训：RED mutation 后恢复必须用备份副本而非 git checkout（文件未提交时 checkout 会回到旧 HEAD）。
- WU-1.2 提交：revenue `4706d66`（含安装同步 --apply，pre-commit 全绿）、filing `cdcbf58`、wiki `96d112d`。

## 实施回执（WU-1.1 消除 company-wiki 静默少收集）

```json
{
  "work_unit": "WU-1.1",
  "baseline_commits": {"revenue": "851154a", "filing": "43330550fb3ea77d36acd92e26861377564a7607", "wiki": "6f732cb"},
  "red_test_ids": ["DUPLICATE gate probe: 11 F811 redefinitions reported by isolated Ruff before fix", "gate mutation probe: duplicate def → exit 1"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/tests/contract/test_source_catalog_worker.py", "company-wiki/pyproject.toml", "company-wiki/tools/check_unique_test_symbols.py", "company-wiki/tests/contract/test_check_unique_test_symbols.py", "company-wiki/.github/workflows/ci.yml", "revenue-forecast/audit_review/2026-08-08_adversarial_plan/progress.md"],
  "focused_commands": ["python tools/check_unique_test_symbols.py", "python -m pytest tests/contract/test_source_catalog_worker.py -q", "python -m pytest tests/contract/test_check_unique_test_symbols.py -q", "ruff check tests/contract/test_source_catalog_worker.py --select F811 --isolated", "ruff check tests/contract/test_source_catalog_worker.py (configured)"],
  "repo_commands": ["python -m pytest tests/unit tests/contract -q (run 1, run 2, run 3 — teardown stability)"],
  "cross_repo_commands": ["not_applicable + company-wiki only WU"],
  "tests_collected_before": 1608,
  "tests_collected_after": 1617,
  "collection_delta_explained": "baseline 1608 + WU-0.2 snapshot 8 + WU-1.1 renamed alt variant 1 = 1617; 10 identical duplicates removed with no collection loss (they were shadowed); worker file 35→36 collected",
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "flaky_note": "run 2 flaky: test_terminating_supervisor_does_not_leave_an_orphan_worker; run 3 flaky: test_m14_concurrent_init_produces_one_v1_schema (different test each run — classic concurrency flake under full-suite load). Verified NOT introduced by WU-1.1: both files untouched by this WU; standalone runs green (orphan 3×, bootstrap file 24/24; m14 1×, migrations file 22/22); run 1 full-suite green. Matches A-F09 known teardown race; WU-7.2 nightly stress gate is the designated fix venue. No skip/xfail/ignore added.",
  "mutation_proof": {"duplicate_def_probe": "RED (gate exit 1, DUPLICATE reported)", "scope_fix": "per-class seen dict verified by test_same_name_in_different_classes_is_not_duplicate"},
  "duplicate_disposition": {"10_identical_removed": "second definition block deleted, first kept, content byte-identical", "1_differing": "test_logon_delay_is_worker_interruptible_and_double_click_controls_exist: second (weaker, missing Start-Process + Join-Path asserts) renamed to _alt and kept; first (stronger) restored as collected"},
  "reviewer": "agent-skills:code-reviewer (agentId aa16ab2f4b20af94f)",
  "review_findings": [
    {"severity": "major", "desc": "gate 测试文件未使用 import pytest (F401)", "resolution": "fixed: 删除该 import，ruff 三文件全绿 + 5 gate tests 通过，commit 已追加"},
    {"severity": "minor", "desc": "ci.yml 无 ruff 步骤，F811 例外移除仅本地强制", "resolution": "accepted as follow-up: 属 WU-1.2/WU-7.1 CI 门范围，不在本 WU 扩展"}
  ],
  "status": "accepted (major finding fixed and re-verified; minor deferred to WU-1.2/WU-7.1)"
}
```

## 实施回执（WU-0.2 生产快照夹具生成器）

```json
{
  "work_unit": "WU-0.2",
  "baseline_commits": {"revenue": "6a08310", "filing": "43330550fb3ea77d36acd92e26861377564a7607", "wiki": "325086af1a5d966f1f01b389109dd26d1b6a63bc"},
  "red_test_ids": ["test_requires_readonly_flag", "test_deterministic_output", "test_schema_and_root_policy_anonymized", "test_sample_row_cap_and_depath", "test_status_distributions_present", "test_catalog_readonly_and_no_side_files", "test_busy_timeout_set"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/scripts/snapshot_catalog.py", "company-wiki/tests/contract/test_snapshot_catalog.py", "revenue-forecast/audit_review/2026-08-08_adversarial_plan/progress.md"],
  "focused_commands": ["python -m pytest tests/contract/test_snapshot_catalog.py -q"],
  "repo_commands": ["python -m pytest tests/unit tests/contract -q (company-wiki full)", "ruff check scripts/snapshot_catalog.py tests/contract/test_snapshot_catalog.py"],
  "cross_repo_commands": ["not_applicable + no cross-repo contract touched; producer-only WU"],
  "tests_collected_before": 1608,
  "tests_collected_after": 1616,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {
    "emit_raw_path_in_root_policy": "RED (test_schema_and_root_policy_anonymized failed)",
    "mode_rw": "green (query_only still blocks — dual defense)",
    "mode_rw_plus_no_query_only": "RED (test_open_readonly_rejects_writes failed)"
  },
  "production_probe": {"snapshot_sha256_twice": "9d24f376b3a77e7d9417f7f4a7142bf2d59502c1c8738763377995e9f3a3543c (identical both runs)", "path_leak": "Users=0 Dropbox=0 dayu-agent=0 .source_catalog=0 C:/=0 C:\\=0; 'company-wiki' only inside urn:company-wiki:document:sha256:... logical IDs"},
  "reviewer": "agent-skills:code-reviewer (agentId a0bae001048838606)",
  "review_findings": [
    {"severity": "minor", "desc": "_samples fetchall 全量后再截断", "resolution": "fixed: SQL LIMIT 下推，commit 6f732cb，复验 8 passed + ruff 全绿"},
    {"severity": "minor", "desc": "busy_timeout 测试为源码文本检查", "resolution": "accepted as-is; 连接拒绝写已有行为级测试"},
    {"severity": "minor", "desc": "no-flag 测试未断言精确 exit code 2", "resolution": "accepted as-is; 门禁足够"}
  ],
  "status": "accepted"
}
```

- WU-0.2 补充说明：生产 catalog 快照抽样显示 documents 分布 active=13797/quarantined=1/retired=9501/upstream_rejected=189，locations active=24972/missing=6/quarantined=1/retired=21526；root policy 与配置一致（company_raw=10/dayu_portfolio=20/dropbox_stock=30）。快照确定性由生产库两次运行 sha256 相同证明；脱敏检查确认无绝对路径泄漏（`company-wiki` 仅出现在 document_id URN 命名空间，属逻辑标识符非路径，测试的 FORBIDDEN_SUBSTRINGS 已注明该例外）。
- WU-0.1 已 accepted（reviewer agentId ab036f82c1b11e84d，3 minor findings，其一已修复并复验 5 passed + ruff 全绿）；commit `6a08310`；计划文档 commit `26e1614`。

## 实施回执（WU-0.1 基线清单与只读保护）

```json
{
  "work_unit": "WU-0.1",
  "baseline_commits": {"revenue": "14770c1a3b90c4916d80240b72d74a73eae90743", "filing": "43330550fb3ea77d36acd92e26861377564a7607", "wiki": "325086af1a5d966f1f01b389109dd26d1b6a63bc"},
  "red_test_ids": ["test_requires_readonly_flag", "test_collects_baseline_facts", "test_catalog_opened_readonly", "test_probe_root_unchanged"],
  "red_exit_code": 1,
  "changed_files": ["tools/audit_baseline.py", "tools/tests/test_audit_baseline.py", "audit_review/2026-08-08_adversarial_plan/progress.md"],
  "focused_commands": ["python -m pytest tools/tests/test_audit_baseline.py -v"],
  "repo_commands": ["python -m pytest tests -q", "ruff check tools/audit_baseline.py tools/tests/test_audit_baseline.py"],
  "cross_repo_commands": ["python tools/audit_baseline.py --read-only --catalog <wiki>/.source_catalog/catalog.sqlite3 --config <wiki>/config/source_catalog.yaml --config <filing>/config/company_wiki.json --repos <3 repos> --probe-roots <dropbox>"],
  "tests_collected_before": 301,
  "tests_collected_after": 301,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "real_root_hash_before": {"companies": "479d07d7336b9fcfdf52138987fa42ab5a0abb3130af901a5748f501b3b78e8d", "dayu": "370f26ee11ece9bbab90aadf9e77d2dcca45a74ed341c52a99bbac94f298d9d6", "dropbox": "0e352f5bad0328ad1966fa9a8880e6208fb23c626e5cb7d62036c59fff38dd46"},
  "real_root_hash_after": {"companies": "479d07d7336b9fcfdf52138987fa42ab5a0abb3130af901a5748f501b3b78e8d", "dayu": "370f26ee11ece9bbab90aadf9e77d2dcca45a74ed341c52a99bbac94f298d9d6", "dropbox": "0e352f5bad0328ad1966fa9a8880e6208fb23c626e5cb7d62036c59fff38dd46"},
  "config_hashes": {"source_catalog": "eb0018d9046c339d2d1074ba0d9d4603893ac7014e8407e1d060adb57d4b6db7", "root_policy_export": "c4567d5d19e23084eb7789cfafcca4e394c1ad86e1e45b216ca85ab58a7facef"},
  "mutation_proof": {"mode_rw_only": "green (no behavioral change, query_only still blocks)", "mode_rw_plus_no_query_only": "RED (test_open_catalog_readonly_rejects_writes failed)"},
  "reviewer": "agent-skills:code-reviewer (agentId ab036f82c1b11e84d)",
  "review_findings": [
    {"severity": "minor", "desc": "工具未自动采集测试收集数，由 receipt 手工记录", "resolution": "accepted as-is; collection 由 receipt 承担"},
    {"severity": "minor", "desc": "collect_catalog 内重复 PRAGMA query_only", "resolution": "accepted as-is; 纵深防御"},
    {"severity": "minor", "desc": "roots/scan_runs 降级时 error 仍为 None", "resolution": "fixed: 降级时写入 error 说明并重跑 5 passed + ruff 全绿"}
  ],
  "status": "accepted"
}
```

- WU-0.1 事实补充：生产 catalog 只读采样确认 user_version=0、3 roots、167 scan_runs、documents=23488、locations=46505、size=49,272,315,904 bytes、最近 scan `completed_with_errors`（dropbox `Product_Revenue_Forecast_Model.xlsx` empty file）；三仓 HEAD 与计划基线一致；company-wiki dirty（`llm_cost_log.csv`、`source_manifests/archive/`）为用户修改，本 WU 未触碰。

## 2026-08-08

- 新需求：用户明确 Dropbox 不应被排除，要求优先只改配置并补齐测试/案例；开始重新核验当前 config schema 是否能安全表达“只允许 dropbox_stock，不放开所有 directory”。
- 方法：继续按 planning-with-files 更新原三件套；产品实施仍未开始。

- 完成：完整读取 `planning-with-files/SKILL.md`，创建本轮隔离工作区。
- 完成：确认三个项目 CodeGraph 均已初始化并记录索引规模。
- 完成：盘点三个仓库根目录，确认历史规划与审计资产存在。
- 当前：Phase 1，恢复最初设计目标、历史问题和前次审查结论。
- 完成：用 CodeGraph 盘点三个项目结构；定位复用、下载抑制、冷启动、真实工具一致性等现有测试资产。
- 完成：枚举相关历史计划、审计、设计与验证文档，明确优先读取集合。
- 完成：读取 2026-08-03 `audit_review` 三份底稿，提取当时全量测试证据、14 项发现及 A-D 改进阶段；全部标记为“历史声明待复核”。
- 完成：读取 2026-08-08 `review_audit` 与后续实施镜像，提取 N-01~N-11、R1~R9 和声称的实施证据；识别 `IMPLEMENTATION_PLAN.md` 总览/正文状态冲突。
- 完成：读取 filing-fetch 历史规划、E2E 设计、SKILL 与变更记录；确认其确定性 E2E 不等价于三真实根目录复用验收。
- 完成：读取 company-wiki portfolio reuse 两轮规划与总设计；确认最终决策为 Strategy B 配置驱动只读复用，Strategy A 自动 promotion 已弃用。
- 完成：CodeGraph 深查 filing-fetch 与 company-wiki 复用主链；确认多根 handle 校验、dayu metadata enrichment、resolver 复用测试与 section 子系统存在，尚待生产配置/索引/调用证据闭环。
- 完成：核对当前双侧复用配置和三根文件资产；确认 Dropbox 虽被扫描配置引用，但未进入 reusable kinds 或 allowed handle roots。
- 完成：只读检查生产 catalog schema；确认 artifacts/evidence_spans 可承载衍生物谱系，但复用/只读策略仅存在于外部配置。
- 完成：确认三个真实根均已被生产 catalog 扫描；记录位置/文档/衍生物统计及连续扫描带错误状态。
- 修正：初次文件数受 `.gitignore` 影响，已用不受 ignore 规则影响的枚举纠正 companies 实际规模。
- 问题：一次 SQLite 查询引用不存在的 roots.read_only；已按 schema 改写待重跑。
- 问题：一次 artifacts/evidence 大 join 无输出；后续拆分单条查询并记录退出码。
- 完成：检索三项目现有复用、下载抑制、衍生物和新鲜度相关测试；识别组合场景与 consumer 零调用断言的明显空白。
- 完成：逐行审阅 reusable roots、download suppression、section/reconciliation、filing E2E、revenue client/source 测试；确认当前 E2E 是 companies-only reuse smoke，衍生物未进入 consumer 契约。
- 完成：审阅 resolver/acquisition 真实代码与 section 调用图；确认无 latest gap 语义、reuse 命中即跳过 discovery、resolver 全库扫描、section query 未接 consumer。
- 完成：生产 catalog 只读抽样多根财报；观察到 company_raw 多期共存、dayu `.rejections` location 与 upstream_rejected 文档，已转化为状态过滤验收项。
- 完成：审阅 SourceCatalog.query 与 EvidenceQueryService；确认 query 未排除 rejected/quarantined、全表物化，且衍生物路径选择缺少完成/绑定/版本门。
- 完成：读取 core-section 与 catalog-space-remediation planning 三件套及 company-wiki 主计划相关段；确认子计划状态/checkbox/DoD/实际执行存在系统性漂移，章节能力未接 consumer。
- 完成：审阅三仓库 CI/pre-commit/coverage 配置并执行测试收集；确认关键质量门未进 CI、company-wiki 通过 F811 ignore 容忍重复测试定义。
- 问题：一次 PowerShell 命令误用 bash 续行符，已改为数组参数并成功执行。
- 问题：一次 PowerShell 中文输出编码错误，已切换显式 UTF-8；未把乱码输出用作证据。
- 修改范围：仅新增 `audit_review/2026-08-08_adversarial_plan/` 下三个 Markdown 工作文件。
- 完成：三仓当前基线测试均通过——revenue-forecast `301 passed + 106 subtests`（12.86s）；filing-fetch 离线/隔离集 `115 passed, 1 skipped + 27 subtests`（55.58s，明确排除 real-tool conformance 与 download E2E）；company-wiki unit+contract `1608 passed`（362.56s）。这些结果仅证明现有收集范围，不代表用户全链路已达标。
- 完成：只读 Ruff 复核——filing-fetch 代码/测试/E2E 全绿；revenue-forecast 的产品相关目录有 185 个 Ruff 错误；company-wiki 配置口径仅报 1 个 unused import，但以 isolated F811 复核确认 `test_source_catalog_worker.py` 有 11 个重复测试定义，被项目级 ignore 隐藏。
- 完成：记录审查基线提交：revenue-forecast `14770c1a...`、filing-fetch `43330550...`、company-wiki `325086af...`。company-wiki 已有 `llm_cost_log.csv` 修改和 `source_manifests/archive/` 未跟踪内容，本轮未触碰；revenue 仅新增本审查目录。
- 当前：把审查结论、历史问题追踪、E2E 情景矩阵和弱模型执行闸门固化为最终实施计划；仍未修改任何产品代码、测试或配置。
- 已更新：原计划的工作包继续保留，并新增 Dropbox config-only 的 WU-2A.0~2A.5；长期 root-id RootPolicy 降为条件性 WU-2B，不再是启用 Dropbox 的前置。
- 已更新：在原 27 个 E2E 基础上增加 E2E-DBX-01~10，共 37 个唯一场景 ID；Dropbox 场景要求 runtime diff=0、两侧配置原子部署、跨进程零下载/零写入和真实只读 canary。
- 已更新：`findings.md` 汇总 34 项发现，新增 F-034 证明 config-only 可行性；保留分维度验收、两轮历史问题追踪、filing-fetch 专项矩阵和 14 项风险登记。
- 完成：最终自审确认 3 个 planning 文件存在、无 `待审查/待定义/TODO/TBD` 占位、原六项要求及追加 Dropbox 硬需求逐条映射，产品实施状态明确为全部 pending。
- 最终复核：计划中现有 37 个唯一 E2E ID、4 个 CONFIG-DBX 测试 ID、findings F-001~F-034；Markdown `git diff --check` 无异常，工作区仍只新增本审查目录。
- 最终修改范围：仅 `revenue-forecast/audit_review/2026-08-08_adversarial_plan/` 三个新 Markdown 文件；未触碰 filing-fetch/company-wiki 产品文件，未下载文件，未写生产 catalog。
- 本轮状态：规划与审查完成；等待用户后续明确授权后，才可从 WU-0.1 开始实施。
- 追加核验：CodeGraph 证明当前 `ROOT_KINDS` 仅含 company_raw/directory/dayu_portfolio，生产配置中 Dropbox 是唯一 directory root；因此无需 runtime 改动即可通过 YAML 追加 `directory`、filing JSON 追加 Dropbox path 启用。
- 追加计划：新增 WU-2A.0~2A.5、CONFIG-DBX-01~04、E2E-DBX-01~10、runtime forbidden-path diff、生产只读双层验收和精确回滚；若状态过滤负例暴露 F-024，先由独立 WU-3.1 修复通用 resolver，再部署 Dropbox 配置，不能在 Dropbox WU 偷改 runtime。
- 追加治理：新增弱模型 12 步执行清单、F-001~F-034 closure ledger 和“已知问题可闭环但未知缺陷不能绝对保证”的保证边界。
