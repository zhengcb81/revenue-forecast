
## 2026-08-12 — FC-1202 实施完成（三仓；reviewer 后台重放中）

- **触发**：用户「继续，不要停，一直做下去直到项目全部完成。给你全部你需要的授权」。
- **preflight + scope 决策（Interpretation A，findings 58）**：运行时 containment 已正确（FC-501 policy-snapshot 单一源）；触点 = filing CI 失效 doctor 块（FC-501 删了 allowlist 后必红 + 硬编码 3 root 路径）、revenue 客户端兄弟仓默认、filing 相对 root 隐式解析、wiki doctor 兄弟查找、SKILL.md stale。运行时 dayu containment 出范围（R4 backlog）。
- **交付（3 提交）**：revenue `b34097d`（config/filing_fetch.json 严格 loader + prepare_source/CLI --filing-fetch-root 透传 + 10 新测试）；filing `b7ef9cc`（相对 root fail-closed + tools/config_doctor.py 三仓契约 doctor + quality.yml 替换 + SKILL.md 重写 + 11 新测试）；wiki `a6937f3`（doctor --filing-fetch-config 显式参数 + 兄弟查找删除 + dropbox early-return 顺序 bug 修复 + 4 测试）。
- **TDD**：RED（ImportError/断言失败）→ GREEN → M1/M2/M2b/M3/M4/M5 六 mutation 全杀（M2b 首跑存活暴露无 CLI 级测试——补 test_cli_forwards_filing_fetch_root 后再杀）。
- **全量**：revenue 513 passed/1 failed（pre-existing PORT-01 audit_baseline）；filing hermetic 289 passed/6 skipped；wiki 2241 passed/2 failed（pre-existing PORT-01 对）/1 skipped。三仓 ruff/compileall 绿（revenue 1 个 pre-existing F401 在 test_compatibility_manifest.py，记 FC-1204 backlog）。install sync 双仓 MATCH。
- **receipt**：schema 2.0 `assurance/fc/FC-1202/11_implementer_receipt.json`（结构验证 exit 0），提交 `20180f9`；registry FC-1202 → in_progress。
- **reviewer-fc1202-independent**：后台干净 worktree 重放中（F-6 规则；RED-at-base 第二 worktree）。
- **下一步**：reviewer verdict → can_accept → closure；FC-1203 预检已并行启动。
## 2026-08-12 — FC-1203 实施完成（company-wiki；全量套件运行中）

- **FC-1202 先行 ACCEPTED**（reviewer-fc1202-independent 零阻塞；can_accept exit 0；closure 提交 revenue `5ef1079`；FCAP 60/71）。
- **preflight（findings 59 + 修订）**：三仓 AST/CodeGraph 盘点。删除集两度收敛——`evaluate_candidate` 保留（Phase 14 R3/R5 未接线政策，sealed FC-502 契约测试承重；`evaluate_admission` 是 focus-only 不构成替代）；`restore.py` 保留（生产 remediation 工具 wu904_remediation_restore.py 真实调用 restore_asset gates，FC-403 链条）；`validate_flag_state` 保留（runtime_policy 生产调用）。
- **交付（wiki `f58b52e` + comment 提交）**：删除 validate_normalized_filing、entity_resolver.py、reuse_latest_policy.py、atomic_rollback + wu905 脚本 + 4 个测试文件；新门测试 test_fc1203_dead_helpers_absent.py（5 复活 mutation 全杀）；extractive summarizer 注册 GENERATOR_REGISTRY + schema_version 列/metadata 双写 + ISO created_at（M-unregister 击杀）——生产 summarize CLI 产物从必然 rejected 变为可绑定。变更合同 03_change_contract_fc1203.md。
- **验证**：6 新测试 GREEN；邻域 53 passed（policy_and_flags/fc1201 gate/fc502/dbx_fixture/restore_flow/admission_profile/focus_admission）；ruff 干净；全量套件运行中。
- **下一步**：全量 verdict → receipt → 独立 reviewer → can_accept → registry accepted → FC-1204。
## 2026-08-13 — FC-1204 实施中（a/b/c 三子链；基线实测见 findings 60/61）

- **a（coverage）**：filing 新增 test_fc1204_coverage_gap.py（21 测试）——TOTAL 88→91%（≥90 gate 达成），filing_contracts 91→97%；quality.yml 加 --cov-fail-under=90 required 步骤。wiki 新增 tier1_gaps 测试（13 tests：admission 99/policy 100/scheduler 100/visibility 100/restore 补 2 分支）+ test_fc1204_coverage_ratchet.py（Tier1 critical ≥95 required；Tier2 冻结 + FC-1205 目标；FROZEN 其余；FC1204_COVERAGE_GATE=1 环境门——coverage.json 会话末写盘，in-suite 诚实 skip，CI 分两步）。
- **b（complexity）**：三仓 ratchet 测试冻结实测 per-file max-CC + 新文件 ≤10。**revenue `_validate_forecast_output` CC 174→150**：四块提取（_recompute_consolidated_paths/_validate_confidence_block/_validate_theme_analysis/_validate_receipt_blocks，AST 自由变量分析定参数集，helper 全 ≤15），test_output_report 23 passed 锁行为；ratchet 冻结值 174→150。
- **c（type）**：mypy 配置（revenue mypy.ini namespace+follow_imports=skip；wiki pyproject override yaml）。revenue 契约集 45→**0 errors**（require() 宽为 Any truthiness gate + narrows；document.py 4 处 assert/过滤窄化）；wiki 11 契约模块 0 errors；filing 0 errors。三仓 CI 加 mypy required 步骤。
- **提交**：revenue `17e6354`（mypy+ratchet；sync --apply 后 pre-commit 全绿）。filing/wiki 待提交；wiki coverage 全量验证运行中。
- **不可达守卫发现**：fetch_filing.py:657「explicit download requires market and security_id」被 _resolved_company_identity 上游强约束——纵深防御不可达分支，按「绝不伪造」不写人为测试，保留 + 记录。
## 2026-08-13 — FC-1204 ACCEPTED（r3 三轮 review）+ FC-1205 实施中

- **FC-1204 closure**（revenue 65c2b87）：r1 REJECTED（F1 CI mypy 不可复现 + F2 假 mutation 记录）→ r2 REJECTED（F7 ruff E402 + pre-existing F401）→ r3 ACCEPTED（4 info 折叠）。can_accept exit 0。registry + Phase 12 header 更新。**FCAP 62/71**。
- **r1/r2 修复提交**：wiki 925b3e8（follow_imports=skip）、filing 83c638e（gap_plan assert 窄化 + ratchet 33→34）、revenue e40a52c/91cbc13（E402 归顶 + F401 移除——revenue ruff 历史首次全 0；日期翻转修复扩展到 fc1003_uj/fc1004_platform）。
- **FC-1205 PORT-01 修复**（双站点，child 侧 reconfigure UTF-8 + subprocess encoding）：
  - wiki tools/check_unique_test_symbols.py：stdout/stderr reconfigure——2 个 pre-existing 失败消失（5/5 passed，无 PYTHONIOENCODING）。
  - revenue tools/audit_baseline.py：subprocess encoding="utf-8" errors="replace" + 工具 stdio reconfigure——PORT-01 失败消失（5/5 passed）。**revenue 全量首次有望 0 failed**。
  - M1（wiki reconfigure 移除→2 死）+ M2（audit_baseline reconfigure 移除→1 死）击杀 + 还原。
- 全量双仓运行中（revenue + wiki 无 PYTHONIOENCODING）。redaction 核对：observability/worker 无绝对路径硬编码。
- 下一步：全量 verdict → receipt → reviewer → can_accept → **Phase 12 COMPLETE（62→63/71）** → Phase 13。

