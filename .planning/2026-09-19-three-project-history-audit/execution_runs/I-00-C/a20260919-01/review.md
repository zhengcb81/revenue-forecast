# I-00-C 独立审查结论（a20260919-01）

**结论：accepted_scoped**

## 每项核对点（一句话）

1. **N1（全部passed无证据）**：run_checks.py 用真实 197 项裸 registry fixture（fixture_hash/oracle 全 null，hash d25e6f06…）跑 scenario_gate，unsatisfied=197、closure_ready=false，通过；与审查前检查行为一致。
2. **N2（READ10错映射）**：required_capability="deadline" 而 covered_capabilities=["artifact"] 被拒（evidence_does_not_cover_required_capability:deadline），且对照组覆盖能力时受限接受，正反对照成立。
3. **N3（同一有效组合旧PASS新FAIL）**：rev1 旧 accepted + rev2 新 changes_required 时，revision_select 判最新 verdict=changes_required 并报 "stale accepted must not win"，不被旧 accepted 解锁，通过。
4. **N4/N5（空commands/空invariants）**：oracle 对象 validated_commands==[] 且 invariants==[] 被拒（empty_commands_and_invariants），且 receipt 层 REQUIRED_BY_KIND["implementer"] 含 "commands"，双层成立。
5. **N6（CA206窄化不清原义务）**：无 linkage 的 narrowed successor 下原义务 CA-206 保持 pending 且打 "narrowed successor without linkage" 告警，通过。
6. **P1（正例）**：tier/证据路径/fixture_hash/oracle/capability 齐全的单场景 closure_ready=true 且仅限该范围，通过。
7. **X1（跨入口）**：下层 197 红 → closure.closure_report 输出 old_plan_verdict="incomplete"（复用同一 scenario_gate，非旁路汇总），通过。
8. **独立复跑**：本人在 attempt cwd 用 `iso/venv/Scripts/python.exe run_checks.py` 复跑，RC=0、all_pass=true，与 after/checks_result.json 一致；未修改任何被测文件。
9. **oracle 独立性**：oracle.md 已在运行前冻结判定规则，非由被测函数生成；N2/N3 添改正反对照样均为独立构造的合成 payload，未见把 expected 反推自实现、或将检查红改绿的痕迹。
10. **scenario_gate 规则符合卡内要求**：scenarios.py:146-193 中 matrix_defined/未知 tier 不能等价满足、裸标签需 fixture/oracle 绑定、capability 覆盖校验、空 commands/invariants 判拒，全部与卡内 oracle.md 规则一致。
11. **生产文件未被本卡修改**：复算 sha256，assurance/unified_completion/uc/scenarios.py=524fc1e6…、closure.py=952abfe0…，与 handoff input_hashes 一致；两份 patch 均为“原件→iso副本”单向 diff，允许范围仅 iso 内两文件，未越界。
12. **git 干净性**：`git status --porcelain assurance/unified_completion` 无 uc/ 输出（也无任何输出），生产 uc 未触碰。
13. **步骤4（组合键/时间排序专业冻结）**：attempt 以 revision_select 的 supersedes 链+CAS 单一最新版本实现“不取最后JSON、不信旧accepted标签”（N3 覆盖旧新组合），设计方向合理，但该设计决定按 START_HERE.md 第47条属专业决策门，尚未由专业 reviewer 以 decision.md 形式冻结 — 记为 open question，不阻断本卡（见下）。

## 复算记录

- iso/_pkgdir/uc/scenarios.py sha256 = 5876635a…（与 handoff current_source_hashes 一致）
- iso/_pkgdir/uc/closure.py sha256 = b422daed…（一致）
- iso/scenario_registry_fixture.json sha256 = d25e6f06…（与 before/registry_sha.txt、input_hashes.registry_assert_hash 一致）
- run_checks.py 复跑 RC=0，11 项检查全 pass。

## 问题清单（均不阻断）

- **open question**：步骤4“最新有效结果”的组合键/时间排序需专业 reviewer 正式冻结（decision.md 级别）。当前 revision_select 用 supersedes 链而非独立时间戳排序；刀叉/环/未知 supersedes 已拒，但“同 verdu 无 supersedes 链、无时间戳”的跨文件并列组合尚未由专业决策覆盖。
- **open question**：closure.py 对无 schema-v1 收据的存量单元标 "legacy" 而非 incomplete（CA-304 迁移范围）；若 CA-304 交付后仍有 legacy 项而 old_plan_verdict 允许 "complete_scoped"，将构成回退，须在 CA-304 重新评估。
- **瑕疵**：commands.json 中 I00C-run-checks argv 的 venv 路径被转义损坏（`\u000benv`），属文案转录缺陷，不影响实际执行与 hash 证据链。
- **瑕疵**：N4 的 receipt 层检查仅为 required 字段存在性验证，深度弱于 gate 层双层验证，但不构成绕过。

## 限定申明

本卡接受仅授予以下资格：**完成门判定不再失真（限弱模型执行卡验收用途）** 的资格，以及隔离副本内对 scenario_gate/closure 判定逻辑的修复内容被独立复验通过。本卡**不授予**生产部署资格、不授予任何产品行为/预测准确性认证、不授予对 assurance/unified_completion 生产文件的修改权（生产落地须另走变更窗口卡并保留本手记）；SCEN/闭环判定仅是证据格式检查，不构成人工语义 oracle，也不能替代 I-01 至 I-17 的真实证据义务。
