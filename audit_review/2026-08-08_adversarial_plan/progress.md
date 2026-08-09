# 审查进度日志

## 2026-08-09 — Dropbox/Data Lake 架构调查

- 用户要求：只调查，不改代码；解释为何 Dropbox 完整启用不能仅改配置，以及当前实现是否因硬编码/紧耦合偏离通用 data-lake 构想。
- 已完成：重读 planning-with-files、现行计划、F-034 修正和实施回执；确认三仓已推进到新 HEAD，旧审查基线已失效。
- 已记录：revenue 当前有未提交 closure-ledger/CI/audit 工具工作，wiki 有日志/测试/archive 工作；全部视为他人/进行中变更并保持不动。
- 当前：刷新用户已授权的三个 CodeGraph 索引，然后沿当前真实调用链取证。
- 索引刷新尝试 1：`codegraph init -i` 仅确认三仓已初始化；CLI 明示应改用 `codegraph index`，已记录并切换命令。
- 完成：按用户授权执行 `codegraph index`；当前索引为 revenue 86 files/1558 nodes/1472 edges，filing 16/421/405，wiki 369/8036/7667，均成功。
- 初步结构结论：catalog 物理层已统一 sources/documents/locations/artifacts，但 filing semantic metadata 仍硬编码 `acquisition/dayu_meta`；SQL fiscal-year 下推和 resolver 读取都只认这两种 profile，故不是通用 indexed-root 模型。

## 实施回执（WU-10.2 closure ledger — ACCEPTED）

```json
{
  "work_unit": "WU-10.2",
  "baseline_commits": {"revenue": "73a23c6", "filing": "2d9eb3b", "wiki": "9b7e856"},
  "red_test_ids": ["test_schema_missing_required_field_fails", "test_schema_invalid_status_fails", "test_id_coverage_missing_finding_fails", "test_id_coverage_missing_risk_fails", "test_id_coverage_missing_historical_fails", "test_check_test_refs_missing_file_fails", "test_check_test_refs_skipped_requires_exemption", "test_honesty_rows_lists_unresolved"],
  "red_exit_code": 1,
  "changed_files": ["revenue: tools/verify_closure_ledger.py (new)", "revenue: tools/tests/test_verify_closure_ledger.py (new, 12 tests)", "revenue: audit_review/2026-08-08_adversarial_plan/closure_ledger.json (new, 99 rows)", "revenue: audit_review/2026-08-08_adversarial_plan/closure_ledger.md (new)", "revenue: .github/workflows/quality.yml (closure ledger gate)", "revenue: tools/tests/test_audit_baseline.py (GBK fix: subprocess encoding=utf-8)", "wiki: tests/contract/test_check_unique_test_symbols.py (GBK fix: subprocess encoding=utf-8)"],
  "focused_commands": ["python tools/verify_closure_ledger.py --ledger ... --repo revenue/filing/wiki ×3"],
  "repo_commands": ["python -m pytest tools/tests/test_verify_closure_ledger.py -q (12 passed)"],
  "cross_repo_commands": ["ledger 引用的 pytest ref 在三仓真实 collect+run（44 唯一引用）"],
  "tests_collected_before": 0,
  "tests_collected_after": 12,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "RED：模块不存在时 8 个测试收集失败（ModuleNotFoundError）",
  "semantics": "账本全集 = F-001~F-034 + 历史矩阵 21 行 + R-001~R-014 + 30 场景 = 99 行；90 cleared / 4 not_a_defect / 5 partial（F-034、A-F06、C-Space、R-014、E2E-R03）——按计划不宣称全部消除；schema 校验 + id 覆盖 + 每 repo 引用真实 collect/run/无 skip 豁免；superseded 行均有当前证明（CodeGraph/guard/compat test）；发布 manifest（CI closure ledger gate）校验 revenue 侧引用",
  "reviewer": "pending WU-10.1 reviewer verdict applied (aa2ec46bebdc35040)",
  "review_findings": [
    {"severity": "minor", "desc": "WU-10.1 reviewer 建议：test_audit_baseline/test_check_unique_test_symbols 的 subprocess 应传 encoding=utf-8（Windows GBK 环境性失败）", "resolution": "fixed: 两文件 subprocess.run 加 encoding=utf-8（5 passed 各自验证）"},
    {"severity": "minor", "desc": "ledger 首跑发现 5 个引用文件不存在（凭名猜测）", "resolution": "fixed: 换真实文件（test_verify_plan_gates.py / tools/tests 目录 / wiki test_check_unique_test_symbols.py / revenue test_attestation.py）"},
    {"severity": "minor", "desc": "DBX 10 行重复引用同一文件致验证器慢跑", "resolution": "fixed: check_test_refs 按 (nodeid, exemption) 去重（44 唯一引用）"}
  ],
  "status": "accepted (三仓 44 唯一引用全部真实 collect+run 通过，exit 0；88/99 cleared + 7 honest-open partial 如实标注；CI gate 接线 quality.yml)"
}
```

## 实施回执（WU-10.1 独立全链验收 — ACCEPTED）

```json
{
  "work_unit": "WU-10.1",
  "reviewer": "agent-skills:code-reviewer (agentId aa2ec46bebdc35040，未参与实施)",
  "verdict": "accepted",
  "task1_replay": {"revenue": "343 passed/0 failed/0 skipped (+106 subtests)", "wiki": "1697 passed/0/0", "filing": "142 passed/0/7 skipped (全部有据：symlink 平台豁免、4 下载需显式 env、生产快照缺失、conformance 无样本)", "filing_golden": "run_companies_reuse_only_e2e.py STEP 10 golden identical, repo_head=2d9eb3b6", "mock_only": "非 mock-only：E2E-D01/D02/D03 驱动真实 select_reusable_artifacts（spy 被调即 raise + 字节级 hash 校验）；fail_closed 驱动真实 scan→SQLite→resolver 全链；bundle_compat 驱动真实 validate_handle 深校验"},
  "task2_mutations": [
    {"dimension": "B status", "file": "wiki resolver.py:453", "mutation": "移除 source_status 防御检查", "red": "test_resolver_defense_in_depth_rejects_leaked_document (REUSED_EXACT)", "restored": true, "green_after": "fail_closed 8 passed"},
    {"dimension": "C hash", "file": "wiki artifact_handle.py:108", "mutation": "sha256 比较反转", "red": "test_valid_artifact_passes 等 7 个", "restored": true, "green_after": "artifact_handle 12 passed"},
    {"dimension": "D latest", "file": "wiki resolver.py:844", "mutation": "_pick_latest max→min", "red": "test_latest_as_of_picks_most_recent + test_latest_as_of_respects_as_of_cutoff", "restored": true, "green_after": "latest_mode 3 passed"}
  ],
  "task3_diff_audit": {"threshold_lowering": "none（.coveragerc fail_under=84 零 diff；PER_MODULE_MINIMUM 是新增非降低）", "ignore_widening": "none（三仓 .gitignore 零 diff；wiki per-file-ignores 未新增）", "test_deletion": "none（基线后无 tests/*.py --diff-filter=D；历史删除经 merge-base 证实在基线前）", "real_root_writes": "none（canary 前后 catalog stat 一致：size=49278910464, mtime=1786227457；零写命令）"},
  "task4_canary": {"companies": "AMD/Alphabet/Apple/MongoDB/NVIDIA 真实目录", "dayu": "1548/2020/300346/3696/3896 证券代码目录", "dropbox": "pdf/xlsx + .source.json lineage 成对", "lineage": "只读 catalog roots 表路径精确指向三根；locations company_raw=33092/dayu=3585/dropbox=9828", "zero_unnecessary_calls": "调用清单仅 ls×3 + 只读 SELECT×2 + shadow probe --read-only；无 parser/LLM/网络/scan"},
  "task5_gap": {"result": "metadata-only 确认：本地 FY2024 + provider FY2025 → gap=[2025] 仅此；GAP 状态 discover=1 fetch=0 staging 零文件；allow_download=False → download_required_but_not_allowed 零写入；未授权/未知 accession 拒绝", "tests": ["test_local_old_gap_new_period", "test_coordinator_latest_as_of_returns_gap_without_fetch", "test_allow_download_false_with_no_existing_source_returns_missing_no_fetch", "test_coordinator_rejects_unauthorized_accession", "test_validate_rejects_unknown_accession"]},
  "task6_parser_llm_zero": {"result": "parser=0 (E2E-D01) / LLM=0 (E2E-D02) / chunker=0 (E2E-D03)，spy 被调即 raise", "tests": ["test_e2e_d01_normalized_artifact_parser_zero", "test_e2e_d02_valid_summary_llm_zero", "test_e2e_d03_sections_used_instead_of_full_rerun"]},
  "task7_reproducible": {"verifier": "revenue 4 / wiki 5 / filing 1 plans 全绿 exit 0", "config_hashes_match": true, "receipt_spotcheck": "WU-9.1/9.2 revenue 73a23c6==HEAD；WU-6.2-5th/WU-4.1/WU-7.1 基线经 merge-base 证认为祖先"},
  "residual_risks": [
    "Windows GBK 环境性：PYTHONIOENCODING=utf-8 前缀下 test_audit_baseline.py(1)/test_check_unique_test_symbols.py(2) 因 subprocess text=True 用 GBK 解码 UTF-8 输出失败——无前缀全绿，CI ubuntu 不受影响；建议测试内传 encoding='utf-8'",
    "_pick_latest published_date 过滤与 resolver.py:534 第一层 as_of 过滤构成防御纵深（仅移除第二层不翻红）——设计冗余非测试弱点",
    "F-034 Dropbox runtime 缺口维持（配置已启用，正例未验）",
    "E2E-F04 symlink Windows 非管理员 skip（已知豁免）",
    "filing 4 下载 E2E + conformance 需显式 env/生产样本，CI 排除（任务明示豁免）"
  ],
  "status": "accepted"
}
```

## 实施回执（WU-9.3 latest/download rollout 代码门验证）

```json
{
  "work_unit": "WU-9.3",
  "baseline_commits": {"revenue": "73a23c6", "filing": "2d9eb3b", "wiki": "9b7e856"},
  "red_test_ids": ["not_applicable: 本 WU 验证已有门的接线，无新 RED（门本身在 WU-4.2/4.3 已 RED→GREEN）"],
  "red_exit_code": 0,
  "changed_files": [],
  "focused_commands": ["grep 验证三代码门 + 阅读 acquisition/authorization/collector 实现"],
  "repo_commands": ["not_applicable（零改动）"],
  "cross_repo_commands": ["not_applicable"],
  "tests_collected_before": 0,
  "tests_collected_after": 0,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "not_applicable（rollout 门验证为代码接线证据，非新逻辑）",
  "semantics": "门 1 metadata-only GapPlan：acquisition.py:48 GAP 状态 + _gap_plan_result 'Nothing is downloaded and nothing is written'（仅 allow_download=True 且授权有效才进入）；门 2 显式授权单文档下载：authorization.py validate_download_authorization 绑定 request_id+gap_plan_hash+provider+accessions+max_items/max_bytes+expires_at（authorization.py:89-115），acquisition.py:409-424 强制校验；门 3 多 gap batch：数量/大小上限在授权 receipt，域名门在 announcement_collector.py validate_official_announcement_url + _OfficialRedirectHandler 逐跳校验（HTTPS-only + official domains）。rollback：latest/download 仅经 request.allow_download + 授权启用，exact reuse（query_source_bundle/select_reusable_artifacts）独立路径不受影响。生产 flip 需观察完整 scan 周期（未满）——状态为 ARMED 而非 complete",
  "reviewer": "pending (agent-skills:code-reviewer)",
  "review_findings": [],
  "status": "armed (代码门全部验证；生产观察门未满；batch 域名上限为 SSE/SZSE collector 级，filing 下载路径域名由授权 accession 绑定约束——如实记录为 rollout 剩余门)"
}
```

## 实施回执（WU-9.1/9.2 安全迁移与分根启用）

```json
{
  "work_unit": "WU-9.1 + WU-9.2",
  "baseline_commits": {"revenue": "73a23c6", "filing": "09f8a7d", "wiki": "73a23c6"},
  "red_test_ids": ["not_applicable + read-only shadow probe is the gate (no RED) "],
  "red_exit_code": 0,
  "changed_files": ["wiki: scripts/shadow_resolver_probe.py (production read-only shadow)"],
  "focused_commands": ["python scripts/shadow_resolver_probe.py --read-only --catalog .source_catalog/catalog.sqlite3"],
  "repo_commands": ["wiki ruff (clean)"],
  "cross_repo_commands": ["发布配置对原子验证（wiki directory reusable + filing Dropbox allowance）"],
  "tests_collected_before": 0,
  "tests_collected_after": 0,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "not_applicable + shadow probe is read-only sampling (mode=ro, query_only)",
  "semantics": "WU-9.1 shadow 探针在生产 catalog 只读采样（候选分布 + scan 状态）；WU-9.2 发布配置对原子（hash 384ef481/cfcb8dbe 与 Phase 2A 一致）",
  "reviewer": "pending (agent-skills:code-reviewer)",
  "review_findings": [],
  "status": "implemented → shadow probe verified on production → pending independent review"
}
```

## 实施回执（WU-7.1 三仓 PR 门 + WU-8.3 planning verifier）

```json
{
  "work_unit": "WU-7.1 + WU-8.3",
  "baseline_commits": {"revenue": "7737f3e", "filing": "09f8a7d", "wiki": "a42bb40"},
  "red_test_ids": ["coverage gates: company_wiki_source 54%, revenue_forecast 57% (<60%)", "core-section F-027: Phase 1-3 completed with unchecked [ ]"],
  "red_exit_code": 1,
  "changed_files": [
    "revenue: tools/run_coverage_gates.py (pytest runner), tools/verify_plan_claims.py (timed gate/apply-conflict/findings/###-headings/archive-exempt), tools/tests/test_verify_plan_gates.py (4 tests), .github/workflows/quality.yml (coverage + verifier), tests/test_bundle_artifact_selection.py (coverage tests)",
    "filing: .github/workflows/quality.yml (config doctor + verifier + pinned clone a42bb40), tools/verify_plan_claims.py",
    "wiki: .github/workflows/ci.yml (verifier), tools/verify_plan_claims.py, docs/plans/core-section-extraction/* (F-027 resolution)"
  ],
  "focused_commands": ["python tools/verify_plan_claims.py --plan-dir . (三仓)", "python tools/run_coverage_gates.py (TOTAL 89%, 0 failures)"],
  "repo_commands": ["revenue 313 tests", "filing 136 tests", "wiki 1024+ contract"],
  "cross_repo_commands": ["verifier 三仓一致；core-section F-027 修复后 wiki 5 plans 全绿"],
  "tests_collected_before": 313,
  "tests_collected_after": 313,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"verifier_M1_emoji_regex": "RED (冲突行归零证明扩展真实生效)", "coverage_unittest_to_pytest": "company_wiki_source 54%→passing"},
  "semantics": "coverage 门进三仓 CI（unittest discover 漏 pytest 测试——修复）；verifier 覆盖三仓 + docs/plans + findings.md + 时间门 + apply 冲突",
  "reviewer": "agent-skills:code-reviewer (agentId ab6594153a1aef558)",
  "review_findings": [
    {"severity": "important", "desc": "coverage 未进三仓 CI", "resolution": "fixed: revenue coverage gates (TOTAL 89%, 0 failures) + filing/wiki 补门"},
    {"severity": "important", "desc": "filing 缺 config doctor", "resolution": "fixed: 三 allowance 校验"},
    {"severity": "important", "desc": "filing clone 浮动 main", "resolution": "fixed: pinned a42bb40"},
    {"severity": "important", "desc": "时间门未实现", "resolution": "fixed: ≥28 天证据 + gate 测试"},
    {"severity": "important", "desc": "production-apply 检查未实现", "resolution": "fixed: 冲突检测 + 规则行豁免"},
    {"severity": "important", "desc": "findings.md 未扫描", "resolution": "fixed: plan-dir 三件套"},
    {"severity": "important", "desc": "verifier 未接 filing/wiki CI", "resolution": "fixed: 三仓接线"},
    {"severity": "critical", "desc": "checkbox 正则误判表格文字（### 标题支持回归）", "resolution": "fixed: 列表项锚定 + gate 测试进 CI"},
    {"severity": "important", "desc": "gate 测试未进 CI + 硬编码路径", "resolution": "fixed: pytest tests tools/tests + 可移植路径"}
  ],
  "status": "accepted (WU-7.1 verdict_a + WU-8.3 verdict_b 均 accepted；三仓 verifier 4/1/5 plans 全绿)"
}
```

## 实施回执（WU-6.2 场景矩阵 — E2E-F03/F04 第五批 + 最终盘点）

```json
{
  "work_unit": "WU-6.2 (fifth batch + final coverage)",
  "baseline_commits": {"revenue": "3bf2a03", "filing": "8400a6f", "wiki": "8f1094e"},
  "red_test_ids": ["E2E-F03 doctor tests (YAML fixture syntax fixes)", "E2E-F04 symlink fence (skipped on Windows non-admin)"],
  "red_exit_code": 1,
  "changed_files": ["wiki: scripts/config_doctor.py (cross-repo drift checks), tests/test_config_doctor.py (2 tests)", "filing: tests/test_bundle_compat.py (E2E-F04)"],
  "focused_commands": ["python -m pytest tests/test_config_doctor.py -q", "python -m pytest tests/test_bundle_compat.py -q"],
  "repo_commands": ["wiki: production doctor verified healthy", "filing: 4 passed 1 skipped (symlink platform limit)"],
  "cross_repo_commands": ["E2E-F03: wiki doctor × filing allowance cross-check"],
  "tests_collected_before": 1658,
  "tests_collected_after": 1661,
  "skipped_tests": ["E2E-F04 symlink (Windows 无管理员权限跳过；逻辑由平台支持环境验证)"],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "not_applicable + fail-fast/fence assertions are the gates",
  "semantics": "F03: doctor 检测第二个 directory root + 两侧 Dropbox realpath 漂移；F04: symlink 越界被 path fence 拒绝",
  "reviewer": "agent-skills:code-reviewer (agentId a4cd242d145282c09)",
  "review_findings": [
    {"severity": "critical", "desc": "D06 兼容性未实现", "resolution": "fixed: expected_provenance 参数 + M-D06 mutation 翻红"},
    {"severity": "critical", "desc": "D05 拒绝路径未被捕获（M1 无效 mutation）", "resolution": "fixed: reason 断言 + 双向不变量 + M-D05 对冲 mutation 翻红（D04+D05）"},
    {"severity": "important", "desc": "D03 无 chunker spy", "resolution": "fixed: chunker spy 零调用断言"},
    {"severity": "important", "desc": "F03 realpath 漂移分支无测试", "resolution": "fixed: test_e2e_f03_dropbox_realpath_drift_fails"},
    {"severity": "important", "desc": "F04 无全平台越界测试", "resolution": "fixed: test_e2e_f04_plain_outside_path_rejected"}
  ],
  "status": "accepted (M-D06/M-D05 对冲 mutation 实证；2 critical + 4 important 全修复)"
}
```

**WU-6.2 最终场景覆盖（37 场景）**：
- **E2E-L01~L07（7）**：WU-4.2 GapPlan 测试 ✅
- **E2E-R01/02/04/05/06/07（6）**：WU-3 系列测试 ✅
- **E2E-R03（1）**：依赖 Dropbox runtime 修复（用户决策：先配置+记录缺口）⏳
- **E2E-R08（1）**：本批新增 ✅
- **E2E-D01~D06（6）**：全部新增（parser/LLM/chunker 零调用 + 兼容）✅
- **E2E-F01（1）**：HTML-as-PDF quarantine ✅
- **E2E-F02（1）**：顺序去重 fetch=1 ✅
- **E2E-F03（1）**：doctor 跨仓漂移 fail-fast ✅
- **E2E-F04（1）**：symlink 越界 fence ✅（Windows skip）
- **E2E-F05（1）**：机制存在（completed_with_errors + error_details 披露 + 生产证据）✅
- **E2E-F06（1）**：机制存在（revenue/filing E2E 双跑 golden）✅
- **E2E-DBX-01~10（10）**：探针 + config invariants + 用户决策缺口模式 ✅/⏳

已覆盖 34/37，3 个依赖外部条件（R03 依赖 runtime 修复决策、F04 平台、F05/F06 机制验证）。

## 实施回执（WU-6.2 场景矩阵 — E2E-D03/D05/D06 第四批）

```json
{
  "work_unit": "WU-6.2 (fourth batch)",
  "baseline_commits": {"revenue": "223a886", "filing": "a7fd0d2", "wiki": "8f1094e"},
  "red_test_ids": ["E2E-D03 sections fixture", "E2E-D05 misbound summary", "E2E-D06 provenance compat"],
  "red_exit_code": 1,
  "changed_files": ["revenue: tests/test_bundle_e2e_d01.py (E2E-D03/D05/D06)"],
  "focused_commands": ["python -m pytest tests/test_bundle_e2e_d01.py -q"],
  "repo_commands": ["python -m pytest tests -q (313 passed + 106 subtests)"],
  "cross_repo_commands": ["E2E-D 系列 6 场景全部完成（D01/02/03/04/05/06）"],
  "tests_collected_before": 310,
  "tests_collected_after": 313,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "not_applicable + spy-raise/fail-closed assertions are the gates",
  "semantics": "D03 sections 复用不整篇重读；D05 错绑定 summary 拒绝只重算该 role；D06 consumer analysis 需 engine/model/prompt/input-bundle 全兼容才复用",
  "reviewer": "pending (agent-skills:code-reviewer)",
  "review_findings": [],
  "status": "implemented → focused green → pending independent review"
}
```

**WU-6.2 场景覆盖更新**：37 场景已覆盖 28 个。待后续：E2E-F03~F06×4、R03×1、DBX 正例（依赖 scanner 修复决策）×若干。

## 实施回执（WU-6.2 场景矩阵 — E2E-F02 第三批）

```json
{
  "work_unit": "WU-6.2 (third batch)",
  "baseline_commits": {"revenue": "94bbfe1", "filing": "a7fd0d2", "wiki": "0e6f739"},
  "red_test_ids": ["E2E-F02 (coordinator-only STAGED twice — corrected to service layer)", "E2E-F02 (writer staging mismatch — fixed staging_root)"],
  "red_exit_code": 1,
  "changed_files": ["wiki: tests/contract/test_source_catalog_acquisition.py (E2E-F02)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_acquisition.py -q"],
  "repo_commands": ["wiki contract baseline (7 acquisition tests green)"],
  "cross_repo_commands": ["not_applicable + company-wiki only"],
  "tests_collected_before": 1657,
  "tests_collected_after": 1658,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "not_applicable + fetch-count assertion is the gate",
  "semantics": "E2E-F02 顺序去重：同 accession 首次 ensure IMPORTED/fetch=1，二次 REUSED/fetch=0（单线程架构下顺序去重）",
  "reviewer": "pending (agent-skills:code-reviewer)",
  "review_findings": [],
  "status": "implemented → focused green → pending independent review"
}
```

**WU-6.2 场景覆盖更新**：37 场景中已覆盖 24 个（L01-L07×7、R01/02/04/05/06/07×6、R08、D01/02/04×3、F01、F02、DBX 探针×10 中已落实部分）。待后续批次：E2E-D03/05/06×3、F03~F06×4、R03×1。

## 实施回执（WU-6.2 场景矩阵 — E2E-R08/F01 第二批）

```json
{
  "work_unit": "WU-6.2 (second batch)",
  "baseline_commits": {"revenue": "94bbfe1", "filing": "a7fd0d2", "wiki": "64e543f"},
  "red_test_ids": ["E2E-R08 broker research fixture (classification check)", "E2E-F01 HTML-as-PDF (PDF magic gate)"],
  "red_exit_code": 1,
  "changed_files": ["wiki: tests/contract/test_source_catalog_dropbox_probe.py (E2E-R08)", "wiki: tests/contract/test_source_catalog_acquisition.py (E2E-F01)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_dropbox_probe.py -q", "python -m pytest tests/contract/test_source_catalog_acquisition.py -q"],
  "repo_commands": ["wiki contract (1018+ passed baseline)"],
  "cross_repo_commands": ["not_applicable + company-wiki only"],
  "tests_collected_before": 1655,
  "tests_collected_after": 1657,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "not_applicable + negative-scenario assertions are the gate",
  "semantics": "E2E-R08 broker research 不满足 annual 请求；E2E-F01 HTML 冒充 PDF 被 magic gate 拒绝",
  "reviewer": "pending (agent-skills:code-reviewer)",
  "review_findings": [],
  "status": "implemented → focused green → pending independent review (WU-6.2 场景覆盖盘点见下)"
}
```

**WU-6.2 场景覆盖盘点**（37 场景）：
- **E2E-L01~L07（7）**：全部由 WU-4.2 GapPlan 测试覆盖（coordinator GAP/fetch=0、up-to-date zero gap、not published、revision、provider offline、future excluded）
- **E2E-R01/02（2）**：reusable_roots + fail_closed active 测试覆盖
- **E2E-R04/05（2）**：determinism 测试覆盖（三根同 hash priority、同 period 不同 hash ambiguous）
- **E2E-R06（1）**：fail_closed 8 测试覆盖（retired/quarantined/upstream_rejected/.rejections）
- **E2E-R07（1）**：既有 stale-file 测试覆盖
- **E2E-R08（1）**：本批新增（broker 负例）
- **E2E-D01/02/04（3）**：首批新增（parser=0/LLM=0/stale role）
- **E2E-F01（1）**：本批新增（HTML-as-PDF quarantine）
- **E2E-DBX-01~10（10）**：探针 + config invariants + 用户决策的已知缺口模式
- **E2E-D03/05/06（3）**、**E2E-F02~F06（5）**、**E2E-R03（1）**：待后续批次

## 实施回执（WU-6.2 场景矩阵 — E2E-D01/02/04 首批）

```json
{
  "work_unit": "WU-6.2 (first batch)",
  "baseline_commits": {"revenue": "058d146", "filing": "a7fd0d2", "wiki": "5fbc2f2"},
  "red_test_ids": ["E2E-D01 parser spy (fixture deep-check iterations)", "E2E-D02 llm spy", "E2E-D04 stale-normalized"],
  "red_exit_code": 1,
  "changed_files": ["revenue: tests/test_bundle_e2e_d01.py (3 tests)"],
  "focused_commands": ["python -m pytest tests/test_bundle_e2e_d01.py -v"],
  "repo_commands": ["python -m pytest tests -q (310 passed + 106 subtests)"],
  "cross_repo_commands": ["E2E-D01/02/04 cross-repo artifact-reuse assertions (parser/LLM=0 spy)"],
  "tests_collected_before": 307,
  "tests_collected_after": 310,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": "not_applicable + spy-raises-if-invoked is the mutation (parser/LLM 被调用即红)",
  "semantics": "E2E-D01 有效 normalized → parser=0；E2E-D02 有效 summary → LLM=0；E2E-D04 stale normalized 只重算该 role",
  "reviewer": "agent-skills:code-reviewer (agentId ae1250c3fbb30bd79)",
  "review_findings": [
    {"severity": "suggestion", "desc": "E2E-D01 死代码行（无 assert 的表达式）", "resolution": "fixed: 删除 + 补 artifact hash 校验断言"},
    {"severity": "suggestion", "desc": "D01 未验证 artifact hash 与文件字节", "resolution": "fixed: content_sha256 对文件字节校验"},
    {"severity": "info", "desc": "D04 全链重跑防回归需 consumer 接线（WU-6.3）", "resolution": "accepted as WU-6.3 范围"},
    {"severity": "info", "desc": "依赖 DAG 语义歧义（role-scoped vs cascade）", "resolution": "documented: role-scoped producer attestation（WU-5.4 只重算该 role）"}
  ],
  "status": "accepted (M1/M2/M3 mutation-proved: spy-raise gate real; 其余 34 场景分批继续)"
}
```

## 实施回执（WU-6.1 可观测 spy 和 fixture builder）

```json
{
  "work_unit": "WU-6.1",
  "baseline_commits": {"revenue": "f76d2e9", "filing": "57ff0bf", "wiki": "5fbc2f2"},
  "red_test_ids": ["ModuleNotFoundError: spy_log (4 tests)"],
  "red_exit_code": 1,
  "changed_files": ["filing: tests/e2e_support/spy_log.py (new), tests/e2e_support/test_spy_log.py (4 tests)"],
  "focused_commands": ["python -m pytest tests/e2e_support/test_spy_log.py -q"],
  "repo_commands": ["filing full offline: 135 passed + 27 subtests (41.54s)"],
  "cross_repo_commands": ["not_applicable + shared test support; consumed by WU-6.2 E2E matrix"],
  "tests_collected_before": 130,
  "tests_collected_after": 135,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"append_to_write": "RED (no-rewrite test failed)"},
  "semantics": "SpyLog append-only JSONL + fsync; read_events deterministic; cross-process subprocess visibility",
  "reviewer": "agent-skills:code-reviewer (agentId af2ae826d29e95ed5)",
  "review_findings": [
    {"severity": "minor", "desc": "read_events 严格解码，崩溃残留半行会抛", "resolution": "accepted; hermetic 临时目录下不适用"},
    {"severity": "minor", "desc": "Windows 文本模式 CRLF，splitlines 兼容", "resolution": "accepted; 跨平台一致"},
    {"severity": "minor", "desc": "WU-6.1 其余项（三根临时目录/adapter spy/clock 等）未在本 commit", "resolution": "accepted as WU-6.2 范围；本 commit 交付 spy 原语"}
  ],
  "status": "accepted (4 tests; M1 append→write mutation-proved; fsync 为不可测耐久保证如实记录)"
}
```

## 实施回执（WU-5.4 revenue consumer 零重复处理）

```json
{
  "work_unit": "WU-5.4",
  "baseline_commits": {"revenue": "07140d6", "filing": "57ff0bf", "wiki": "80fb475"},
  "red_test_ids": ["ImportError: select_reusable_artifacts (5 tests)"],
  "red_exit_code": 1,
  "changed_files": ["revenue: scripts/company_wiki_source.py (select_reusable_artifacts), tests/test_bundle_artifact_selection.py (6 tests)"],
  "focused_commands": ["python -m pytest tests/test_bundle_artifact_selection.py -q"],
  "repo_commands": ["python -m pytest tests -q (307 passed + 106 subtests)"],
  "cross_repo_commands": ["not_applicable + bundle shape inherited from WU-5.2/5.3"],
  "tests_collected_before": 301,
  "tests_collected_after": 307,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"reusable_check_removed": "RED (non-reusable-entry test failed)"},
  "semantics": "select_reusable_artifacts returns verified artifact path/hash per requested role; fail-closed on missing/invalid; malformed bundle raises",
  "reviewer": "agent-skills:code-reviewer (agentId a80bb696f5695c0bf)",
  "review_findings": [
    {"severity": "minor", "desc": "跨仓 RED 验收项（parser=0/chunker=0/LLM=0）无本仓断言", "resolution": "accepted as WU-6.2 E2E-D01~D06 范围；本 WU 只交付选择函数，回执已如实标注"},
    {"severity": "minor", "desc": "forecast receipt 记录 artifact ids/hash/fallback 无消费者接线", "resolution": "accepted as WU-6 范围；选择原语已交付"},
    {"severity": "minor", "desc": "合并卫生：代码并入 docs commit 0511010", "resolution": "recorded in commit-note 07658d1"},
    {"severity": "suggestion", "desc": "select_reusable_artifacts 未复检 path/content_sha256 存在性", "resolution": "accepted; WU-5.1/5.2 validator 语义兜底"}
  ],
  "status": "accepted (6 tests; M1 reusable-check and M2 malformed-bundle both mutation-proved)",
  "commit_note": "WU-5.4 代码（company_wiki_source.py + 测试）因 git add 时序被并入 docs receipt commit 0511010（提交卫生瑕疵，代码内容正确且 307 tests 全绿；不重写历史）"
}
```

## 实施回执（WU-5.3 SourceBundle 契约扩展）

```json
{
  "work_unit": "WU-5.3",
  "baseline_commits": {"revenue": "07140d6", "filing": "3b5b713", "wiki": "5fbc2f2"},
  "red_test_ids": ["company-wiki: 3 query_source_bundle tests (method absent)", "filing: 3 bundle compat tests (fixture deep-check failures)"],
  "red_exit_code": 1,
  "changed_files": [
    "wiki: store.py (artifacts +schema_version/source_sha256 additive migration), service.py (query() artifact columns + query_source_bundle), tests/contract/test_source_catalog_query_bundle.py (3 tests)",
    "filing: tests/test_bundle_compat.py (3 tests)"
  ],
  "focused_commands": ["wiki: python -m pytest tests/contract/test_source_catalog_query_bundle.py -q", "filing: python -m pytest tests/test_bundle_compat.py -q"],
  "repo_commands": ["filing full offline: 130 passed + 27 subtests (41.63s)"],
  "cross_repo_commands": ["bundle compat both directions (handle with/without source_bundle validates)"],
  "tests_collected_before": 1652,
  "tests_collected_after": 1655,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"migration_disabled": "RED (migration test failed)"},
  "semantics": "artifacts schema_version/source_sha256 now persisted so WU-5.1 gates apply to real rows; query_source_bundle returns source + verified artifacts in one call; filing-fetch accepts optional bundle both directions",
  "reviewer": "pending (agent-skills:code-reviewer)",
  "review_findings": [],
  "status": "implemented → focused green → pending independent review"
}
```

## 实施回执（WU-5.2 SourceBundle query）

```json
{
  "work_unit": "WU-5.2",
  "baseline_commits": {"revenue": "0269d51", "filing": "3b5b713", "wiki": "d33d422"},
  "red_test_ids": ["ModuleNotFoundError: source_bundle (5 tests)"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/src/company_wiki/source_catalog/source_bundle.py (new)", "company-wiki/tests/contract/test_source_catalog_source_bundle.py (5 tests)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_source_bundle.py -q"],
  "repo_commands": ["ruff check source_bundle.py + tests (clean)"],
  "cross_repo_commands": ["not_applicable + company-wiki only WU"],
  "tests_collected_before": 1647,
  "tests_collected_after": 1652,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"isolation_broken": "RED (invalid_artifact_isolated test failed)"},
  "semantics": "invalid artifact isolated — sibling roles and source stay reusable; bundle hash changes when any role state changes",
  "reviewer": "agent-skills:code-reviewer (agentId ae5c4f83fb0504d73)",
  "review_findings": [
    {"severity": "important", "desc": "同 role 多 artifact 未定义（dict 覆盖 + valid/invalid 矛盾）", "resolution": "fixed: 最新 valid 胜出，旧 valid 标 superseded；确定性按 created_at"},
    {"severity": "important", "desc": "RED 场景覆盖不足（仅部分存在）", "resolution": "fixed: 5 个新场景测试（同 role/两 generator/旧 source 新 summary/summary-sections stale/hash 不符）"},
    {"severity": "important", "desc": "bundle hash 未绑定 invalid 子 handle", "resolution": "fixed: digest 含 invalid role/reason"},
    {"severity": "suggestion", "desc": "invalid 代表选择非规则化", "resolution": "fixed: earliest (created_at, artifact_id) + 输入顺序无关测试"},
    {"severity": "suggestion", "desc": "模块 docstring 滞后", "resolution": "fixed"}
  ],
  "status": "accepted (all reviewer findings fixed; 22 tests + mutation-proved)"
}
```

## 实施回执（WU-5.1 ArtifactHandle validator）

```json
{
  "work_unit": "WU-5.1",
  "baseline_commits": {"revenue": "0269d51", "filing": "3b5b713", "wiki": "1d00b81"},
  "red_test_ids": ["ModuleNotFoundError: artifact_handle (8 tests)"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/src/company_wiki/source_catalog/artifact_handle.py (new)", "company-wiki/tests/contract/test_source_catalog_artifact_handle.py (8 tests)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_artifact_handle.py -q"],
  "repo_commands": ["ruff check artifact_handle.py + tests (clean)"],
  "cross_repo_commands": ["not_applicable + company-wiki only WU"],
  "tests_collected_before": 1639,
  "tests_collected_after": 1647,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"status_check_removed": "RED (pending test failed)", "hash_check_removed": "RED (hash test failed)"},
  "reviewer": "agent-skills:code-reviewer (agentId a84da0d878ee2175a + ae5c4f83fb0504d73)",
  "review_findings": [
    {"severity": "major", "desc": "source_sha 未校验", "resolution": "fixed: artifact_source_sha_mismatch + 测试 + mutation"},
    {"severity": "major", "desc": "future as_of 未校验", "resolution": "fixed: artifact_source_as_of_future + 测试 + mutation"},
    {"severity": "major", "desc": "schema_version 未校验", "resolution": "fixed: artifact_schema_unsupported + 测试 + mutation"},
    {"severity": "minor", "desc": "reason code 内嵌动态值", "resolution": "fixed: 全部稳定常量"},
    {"severity": "minor", "desc": "created_at 缺失 fail-open", "resolution": "fixed: artifact_created_at_malformed + 测试 + mutation"},
    {"severity": "minor", "desc": "store artifacts 表缺 schema_version/source_sha256 列，gate 对 DB 数据不生效", "resolution": "accepted as WU-5.3/5.4 wiring 项；接线时补列"}
  ],
  "status": "accepted (12 tests; 4 new gates mutation-proved; store column wiring deferred to WU-5.3/5.4)"
}
```

## 实施回执（WU-4.3 授权绑定与最小下载 — receipt 引擎）

```json
{
  "work_unit": "WU-4.3 (engine stage)",
  "baseline_commits": {"revenue": "0eef82b", "filing": "3b5b713", "wiki": "c62dd61"},
  "red_test_ids": ["ModuleNotFoundError: authorization (8 tests)"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/src/company_wiki/source_catalog/authorization.py (new)", "company-wiki/tests/contract/test_source_catalog_download_authorization.py (8 tests)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_download_authorization.py -q"],
  "repo_commands": ["ruff check authorization.py + tests (clean)"],
  "cross_repo_commands": ["not_applicable + runtime wiring (filing-fetch CLI authorization + coordinator validation) deferred to WU-4.3 stage 2"],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"accession_check_removed": "RED (unknown_accession test failed)", "expiry_removed": "RED (expired test failed)"},
  "reviewer": "agent-skills:code-reviewer (agentId a123ec4677b42a5c5)",
  "review_findings": [
    {"severity": "major", "desc": "provider 绑定未在 validate 中强制执行", "resolution": "fixed: validate 拒绝 provider 不一致候选 + 测试 (1d00b81)"},
    {"severity": "major", "desc": "无授权为 0 门禁悬空（authorization=None 时照常 fetch，兼容设计）", "resolution": "accepted as WU-6 E2E 项；由 plan 驱动下载器层强制"},
    {"severity": "minor", "desc": "expires_at 无格式校验（字典序比较）", "resolution": "accepted as follow-up; 调用方约束 + WU-6 E2E"},
    {"severity": "minor", "desc": "coordinator 层 plan-hash 自引用", "resolution": "accepted; 委托签发方绑定（已注释）"},
    {"severity": "minor", "desc": "累计 caps 不在本层跟踪", "resolution": "accepted; 调用方传累计计数"},
    {"severity": "minor", "desc": "并发去重/旧文件不变/fetch 计数门禁属 WU-6 级", "resolution": "accepted as WU-6 E2E 项"}
  ],
  "status": "accepted (engine + coordinator wiring mutation-proved; provider binding fixed post-review)"
}
```

## 实施回执（WU-4.2 metadata-only discovery 与 GapPlan）

```json
{
  "work_unit": "WU-4.2",
  "baseline_commits": {"revenue": "0eef82b", "filing": "3b5b713", "wiki": "478ca5e"},
  "red_test_ids": ["ModuleNotFoundError: gap_plan (7 tests)", "coordinator latest_as_of → REUSED early-return (was not GAP)"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/src/company_wiki/source_catalog/gap_plan.py (new)", "company-wiki/src/company_wiki/source_catalog/acquisition.py (GAP status + coordinator branch)", "company-wiki/tests/contract/test_source_catalog_gap_plan.py (8 tests)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_gap_plan.py -q"],
  "repo_commands": ["python -m pytest tests/contract/test_source_catalog_acquisition.py tests/contract/test_source_catalog_adapter_process.py tests/contract/test_source_catalog_gap_plan.py -q (17 passed)"],
  "cross_repo_commands": ["not_applicable + company-wiki only WU (filing-fetch consumption belongs to WU-4.3)"],
  "tests_collected_before": 1631,
  "tests_collected_after": 1639,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"provider_error_ignored": "RED (unavailable test failed)", "missing_detection_removed": "RED (local_old_gap test failed)"},
  "semantics": "latest_as_of no longer short-circuits on local reuse — provider metadata decides reuse vs gap; provider_unavailable keeps local and never claims up-to-date; future-dated candidates excluded from gap",
  "reviewer": "agent-skills:code-reviewer (agentId a5117a568c07f0d4d) — first pass rejected, fixes committed 63484a4, re-verification in progress",
  "review_findings": [
    {"severity": "major", "desc": "gap_hash 非顺序无关（reuse 仅按 fiscal_year 排序）", "resolution": "fixed: 排序键 (fiscal_year, provider_document_id) + 回归测试"},
    {"severity": "major", "desc": "SourceAcquisitionService.ensure 无 GAP 分支 → RuntimeError", "resolution": "fixed: SourceEnsureStatus.GAP 分支"},
    {"severity": "major", "desc": "latest_as_of+allow_download=True 绕过 GapPlan 直接 fetch", "resolution": "fixed: latest_as_of 始终先返回 metadata-only plan，fetch=0 + 回归测试"},
    {"severity": "minor", "desc": "冗余局部 import build_gap_plan", "resolution": "fixed: 模块级 import"},
    {"severity": "minor", "desc": "测试冗余（两场景相同）+ 缺 provider_error 端到端", "resolution": "accepted as follow-up; 补了 hash 顺序与 allow_download 回归"}
  ],
  "status": "implemented → reviewer fixes committed → re-verification in progress"
}
```

## 实施回执（WU-4.1 versioned FilingRequest 和 LatestPolicy）

```json
{
  "work_unit": "WU-4.1",
  "baseline_commits": {"revenue": "e75d5eb", "filing": "0d58b3e", "wiki": "fbcfa3c"},
  "red_test_ids": ["filing: 7 mode contract tests (schema 1.2 unknown field)", "wiki: 3 latest-mode tests (mode field absent before)"],
  "red_exit_code": 1,
  "changed_files": [
    "filing: scripts/filing_contracts.py (schema 1.2 + mode validation), scripts/fetch_filing.py (--mode passthrough), tests/test_latest_mode.py (9 tests), e2e/expected/*.json (request_id golden refresh)",
    "wiki: src/company_wiki/source_catalog/resolver.py (SourceRequest.mode + _pick_latest + cap 1000), src/company_wiki/source_catalog/cli.py (--mode), tests/contract/test_source_catalog_latest_mode.py (3 tests)"
  ],
  "focused_commands": ["filing: python -m pytest tests/test_latest_mode.py -q (9 passed)", "wiki: python -m pytest tests/contract/test_source_catalog_latest_mode.py -q (3 passed)"],
  "repo_commands": ["filing: 126 passed + 27 subtests; isolated-wiki E2E 15 passed", "wiki: 37 resolver-related passed; contract 967 passed", "revenue: 301 passed + E2E PASS"],
  "cross_repo_commands": ["test_e2e_hk_old_sidecar_reuse (filing CLI → real wiki resolver, HK old sidecar) — passed after cap fix"],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "mutation_proof": {"filing_latest_as_of_allows_fiscal_year": "RED (forbids test failed)", "wiki_pick_latest_disabled": "RED (2 latest tests failed)"},
  "regression_found_and_fixed": "WU-3.2 cap-shadowing fix pushed fiscal_year into SQL json_extract, which missed title-derived years (old HK sidecar) → resolver now keeps fiscal_year in Python (authoritative, title-aware) with cap 1000; test_e2e_hk_old_sidecar_reuse red→green",
  "golden_note": "request_id changed because mode enters request identity hash (intended schema evolution); snapshot_sha256/https_url/canonical_tail unchanged",
  "reviewer": "agent-skills:code-reviewer (agentId a1bf6544e84caa211)",
  "review_findings": [
    {"severity": "minor", "desc": "future as_of / 跨市场 form 混淆无显式新测试（既有测试间接覆盖）", "resolution": "accepted as follow-up; WU-4.2/6.2 E2E 矩阵补显式用例"},
    {"severity": "minor", "desc": "filing 校验 latest_as_of+fiscal_year 拒绝，wiki SourceRequest 仅校验 mode 取值（分层不变量不对称）", "resolution": "accepted; 严格契约由 filing 边界执行，resolver 保留 CLI 直接调用语义"},
    {"severity": "minor", "desc": "legacy 1.1 无 deprecation warning 通道（结构性信号替代）", "resolution": "accepted; 1.2 无 mode 请求收到明确错误提示升级"}
  ],
  "status": "accepted (mutation-proved: latest_as_of forbids fiscal_year and _pick_latest both flip red)"
}
```

## 实施回执（WU-3.3 多候选确定性和冲突语义）

```json
{
  "work_unit": "WU-3.3",
  "baseline_commits": {"revenue": "e75d5eb", "filing": "0d58b3e", "wiki": "4f8b95d"},
  "red_test_ids": ["test_same_hash_three_roots_picks_priority_primary_preserves_all (fixture IntegrityError before model fix)", "test_same_period_different_hash_is_ambiguous", "test_determinism_across_100_random_insert_orders (tmp-path sig false positive → root-relative tail)"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/tests/contract/test_source_catalog_determinism.py"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_determinism.py -v"],
  "repo_commands": ["python -m pytest tests/contract/test_source_catalog_determinism.py tests/contract/test_source_catalog_sql_pushdown.py tests/contract/test_source_catalog_fail_closed.py -q (16 passed)"],
  "cross_repo_commands": ["not_applicable + company-wiki only WU"],
  "tests_collected_before": 1628,
  "tests_collected_after": 1631,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "determinism_evidence": "100 random INSERT orders → identical result signature per request (FY2025 / FY2024 each 1 sig across 100 runs)",
  "semantics_evidence": "same hash 3 roots → REUSED_EQUIVALENT, canonical=company_raw (priority 10), 2+ equivalent locations preserved; same period diff hash → AMBIGUOUS, download_required=False",
  "mutation_proof": "not_applicable + determinism gate is the mutation (shuffle order); fixture model fixes verified via IntegrityError→pass",
  "reviewer": "agent-skills:code-reviewer (agentId a1dbfc17667b28172) — first pass rejected",
  "review_findings": [
    {"severity": "critical", "desc": "insert_order 参数从未使用，100 次随机构建实际相同，门禁空转；按插入顺序选 canonical 的 mutation 存活", "resolution": "fixed: insert_order 现在真正驱动 INSERT 序列；反转 priority 的 mutation 翻红；20 次随机顺序 canonical 恒为 company_raw"},
    {"severity": "minor", "desc": "RED 清单仅覆盖 2/6 场景（强/弱身份混合、主件/附件、同 accession 修订版、mtime 逆序未覆盖）", "resolution": "accepted as follow-up; mtime 不参与判定路径（fixture 已注明），其余场景归 WU-4/WU-6 E2E 矩阵"},
    {"severity": "minor", "desc": "固定插入顺序下测试无法区分 priority 与插入顺序语义", "resolution": "fixed: 门禁现在用随机顺序驱动，且新增 mutation 验证（反转 priority 翻红）"}
  ],
  "status": "accepted (critical gate-tautology fixed; mutation-proved priority semantics)"
}
```

## 实施回执（WU-3.2 SQL 下推和索引）

```json
{
  "work_unit": "WU-3.2",
  "baseline_commits": {"revenue": "cbee0c2", "filing": "0d58b3e", "wiki": "16873b5"},
  "red_test_ids": ["test_query_filing_candidates_exists_and_filters_in_sql (AttributeError before)", "test_resolver_uses_sql_pushdown_not_all_table_query (boom probe)", "test_explain_query_plan_hits_dedicated_indexes", "test_100k_candidate_lookup_within_slo"],
  "red_exit_code": 1,
  "changed_files": ["company-wiki/src/company_wiki/source_catalog/service.py (query_filing_candidates + explain_filing_candidates_plan)", "company-wiki/src/company_wiki/source_catalog/resolver.py (pushdown call)", "company-wiki/src/company_wiki/source_catalog/store.py (4 covering indexes)", "company-wiki/tests/contract/test_source_catalog_sql_pushdown.py (4 tests)"],
  "focused_commands": ["python -m pytest tests/contract/test_source_catalog_sql_pushdown.py -q"],
  "repo_commands": ["python -m pytest tests/contract -q (966 passed)"],
  "cross_repo_commands": ["not_applicable + company-wiki only WU"],
  "tests_collected_before": 1623,
  "tests_collected_after": 1627,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "slo_evidence": "100k-doc fixture lookup: 4.56s seed + query within 2.0s SLO (warm)",
  "semantic_guard": "resolver keeps entity/root filtering in Python: _entity_matches (issuer anchoring/alias/sibling ticker) and identity-conflict-before-root-check (Phase 15.3) preserved; 40 resolver-related tests green",
  "mutation_proof": {"revert_to_all_table_query": "RED (test_resolver_uses_sql_pushdown_not_all_table_query failed)"},
  "reviewer": "agent-skills:code-reviewer (agentId acbac88dcb58555c9)",
  "review_findings": [
    {"severity": "critical", "desc": "WU-3.2 提交不含 fail_closed 测试适配，HEAD 下测试红", "resolution": "fixed: 适配已随 4f8b95d 提交"},
    {"severity": "major", "desc": "limit=100 截断旧年度请求（150 active 中 FY2019 被前 100 FY2025 遮蔽 → MISSING→不必要下载）", "resolution": "fixed: resolver 两层查询（fiscal_year 精确层 + 宽泛层）+ 回归测试 test_old_period_not_shadowed_by_cap（AMBIGUOUS, download_required=False）"},
    {"severity": "major", "desc": "SLO 断言 2.0s vs 计划 500ms；实测 1128ms；N+1 查询；无 RSS 度量", "resolution": "fixed: entities/locations 批量 IN 查询（43ms warm, 0.3MB peak）；SLO 测试改 p95≤500ms + RSS≤100MB 并测 resolver 实际路径"},
    {"severity": "minor", "desc": "EXPLAIN 断言仅查任意 idx_，不验证主查询命中目标索引", "resolution": "accepted as follow-up; 索引已建且 explain 覆盖主查询"},
    {"severity": "minor", "desc": "签名与计划原文偏差（无 period/as_of 参数）", "resolution": "accepted; 与本 WU 验收清单一致（kind/status SQL 过滤 + root/entity 可选）"}
  ],
  "status": "accepted (reviewer findings fixed: commit gap, cap shadowing, SLO alignment; 5 pushdown tests + 40 resolver-related green)"
}
```

- 过程教训：SQL 层先做了 entity 精确过滤，破坏了 resolver 的 issuer 锚定/别名/同 issuer 兄弟 ticker 语义（8 个既有测试红）——修正为 SQL 只下推 kind/status（无争议硬条件），entity/root/identity 保留 Python 层权威匹配。identity-conflict-before-root-check 语义（Phase 15.3 fail-closed）也因此保留。

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
  "reviewer": "agent-skills:code-reviewer (agentId ae36506081b9aa80c)",
  "review_findings": [
    {"severity": "minor", "desc": "test_rejections_path_not_reused 由查询层拦截，未直接驱动 resolver .rejections 过滤（删过滤不翻红）", "resolution": "fixed: 新增 test_resolver_rejects_leaked_active_rejections_path（active+泄漏场景），删过滤现在翻红；8 passed + mutation proved"}
  ],
  "status": "accepted (mutation-proved: query allowlist, resolver status check, .rejections filter all flip red)"
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
## 2026-08-09 Dropbox / Data Lake 架构调查（续）

- 已完成：从当前代码复核 `RootSpec/CatalogConfig`、scanner 三类根枚举、Dropbox admission、分类、实体推断、document metadata 写入、resolver metadata 读取与 handle capture-ready 门。
- 关键证据：配置只能开放 root-kind 与路径围栏，不能声明目录布局/sidecar/identity/classification adapter；Dropbox sidecar 虽参与扫描与 manifest，却没有进入 resolver 只认的 `acquisition/dayu_meta` 语义容器。
- 初步判断：物理文件/哈希/location 目录层已具有多根数据湖特征；filing 语义摄取层仍是 company_raw 与 dayu 两套特例，通用 directory 只是弱语义兜底，不是可插拔数据源。
- 下一步：核对 filing-fetch/revenue 消费端是否继续含 root 特例，读取当前生产配置与 catalog 的 Dropbox 状态/metadata 分布，并审阅现有 probe/E2E 能否证明真实用户路径。
- 变更范围：仅更新审计 Markdown；没有改动产品代码、测试、配置或生产数据。
- 下游复核：filing-fetch 的多根 canonical-path allowance 已是配置驱动；它不会自行解释目录，只会深校验 company-wiki 产生的 capture-ready handle。`source_bundle` 是可选增强，不能绕过 handle 门，因此不能修复 Dropbox ingest 语义丢失。
- 当前配置实证：company-wiki 已把 `directory` 列入 reusable kinds，filing-fetch 已把 Dropbox 列入 allowed roots；配置步骤已执行而语义缺口仍在，原 config-only 假设被当前状态直接否证。
- revenue 消费端：路径本身基本根无关，并已支持从 verified SourceBundle 复用 normalized/summary/sections/analysis；它要求上游先产出合格 handle/bundle，不承担任意根的语义提升。
- 生产 catalog 只读实证：Dropbox 有 9,828 个原件 locations / 9,789 个文档；370 annual、56 quarterly、128/129 semi 均 retired，唯一 active semi 实际由 company_raw 提供主 metadata 与 active 原件。当前没有可证明的 Dropbox-only active filing。
- 对抗样本：普通 Dropbox 券商报告因标题含“年报/半年报”被误分为 annual/semi filing，且 focus 外 `.source.json` 曾被当独立原件；现虽 retired，不代表分类架构已泛化。
- 分层判断：company_raw 作为唯一 canonical 写入目标是合理所有权边界；问题集中在读取侧用 root kind/id/中文路径决定 layout、sidecar、entity 与语义 schema。
- 更正新鲜度判断：Dropbox root 在 2026-08-08 已扫；`重点关注` 0 行是 82 个受支持文件被专用 admission policy 全部排除，而非漏扫。目录现有 161 文件、5 PDF、无 sidecar/MD；scan receipt 缺 per-prefix 排除原因可观测性。
- 测试复核：Dropbox probe 的实际断言已证明 config-only 后仍 MISSING；但模块总说明仍声称 config-only 成功，broker 负例尾部还留有错误的“未来改为 REUSED_EXACT”注释。配置 invariant 只锁白名单/realpath，未验证业务闭环。
- 动态验证：company-wiki 相关 21 passed；filing-fetch 8 passed/1 skipped；revenue bundle 17 passed。绿色包含“Dropbox config-only 后仍 MISSING”的 known-gap 断言，不能当成功验收。
- 衍生物生产实证：Dropbox 关联文档有 normalized completed 1,782、summary 948、sections 7；但 official filing 的这些 artifacts 全属于 retired 文档，无法经 resolver/handle/bundle 到达下游。
- SourceBundle 实现复核：`query_source_bundle/build_source_bundle` 按 document/source SHA、artifact validation、allowed roots、generator/version 与 bundle hash 工作，未按来源 root 分支；下一检查点是确认它是否已接入实际 resolver/CLI，而不只是独立 query 与测试。
- 调用图结论：`query_source_bundle` 仅被 2 个 contract test 调用；revenue `select_reusable_artifacts` 的 14 个调用者全部是测试。生产 resolver/CLI/client 未串联 bundle，已处理资产复用尚是能力孤岛。
- 新的紧耦合证据：company_raw 缺 URL 时，scanner 按公司名从任意 dayu meta 取首个 URL 补齐，缺文档/期间/hash identity join，存在 URL 与原件错绑风险；通用 directory 的 entity 又必须先存在于 company_raw 目录词典。
- 测试进一步确认：URL enrichment fixture 刻意使用不同 bytes，却只按 company name 复制 URL，未覆盖同公司多期/identity/hash 绑定；当前绿测在固化 workaround，而非证明 provenance 正确。
- 调查问题：首次对生产 `document_retire_audit` 与 Dropbox official docs 做组合聚合时命令完成但无输出；未据此下结论，改为拆分小查询核对 audit 行数/原因/覆盖率。
- retire audit 核实：9,499 个 legacy sidecar 因缺 source_url 被 Phase 15.6 批量退休并二次 reconciliation 记账；Dropbox 主 metadata 的 103 个 annual/quarterly/semi 财报全部在该批。retirement 为终态，配置不能复活。
- dayu 对照：其 config-only 绿测依赖 scanner 中完整硬编码的 dayu layout/meta/identity adapter；scanner 用 `else` 承载该分支。这个成功不能外推为任意 directory/new kind 已泛化。
- 正面边界：`latest_as_of` 与 gap planner 已按日期/期间/provider identity 工作且根无关；Dropbox 文档因前置语义/status 门未形成 local handle，所以该层没有可用输入。
- 物理层结论：roots/sources/documents/locations/artifacts/evidence 已分层、按 hash 跨根去重、按 active+priority 选 canonical，是真正的数据湖基础；缺口集中在统一语义 adapter/normalizer 及主链组装。
- 硬编码分布：来源特例主要集中于 company-wiki scanner/admission/focus cleanup/resolver；filing-fetch/revenue 下游较根无关。`_enumerate_root` 单函数约 360 行承载三套 layout，属于可明确定位的架构热点。
- 调查问题：首次 PowerShell literal 计数命令因管道表达式语法错误；改为显式 `$rows` 聚合后成功，未影响任何文件。
- 最终裁决：物理数据湖已成形，语义数据湖未成立；config-only 在当前代码/数据下不可能。小型 Dropbox 特例补丁可让单一 probe 转绿，但不能实现通用 indexed-root adapter，也不解决 retired/provenance/entity/SourceBundle 主链。
- 最终验证：三仓 `git diff --check` 通过；本轮仅修改 revenue-forecast 审计目录下 task_plan/findings/progress 三个 Markdown。filing-fetch 工作树无变化；company-wiki 仅保留调查前已有的 `llm_cost_log.csv` 与 `source_manifests/archive/` 用户内容。
- 调查状态：completed；未修改产品代码、测试、配置、生产 catalog 或三处真实资产目录。CodeGraph 仅按用户授权刷新索引。
