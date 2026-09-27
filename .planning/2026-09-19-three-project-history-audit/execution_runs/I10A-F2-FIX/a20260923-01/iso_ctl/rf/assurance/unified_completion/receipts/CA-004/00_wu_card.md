# CA-004 工作单元卡（preflight）— 旧 71 FC、R0~R9 与 FC-150x 机器处置表

- 领取时间：2026-08-13T23:05Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-004`；机器状态 units.CA-003.status=accepted + closure 存在。
- 依赖：CA-002、CA-003（均 accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01（验收假绿与历史证据漂移）：把 completion_audit.md 的逐 Phase 结论固化为机器注册表，使旧 66/71 不能再被当作当前完成，71 FC + R0~R9 + FC-150x 每项都有机器验证的 disposition 与 successor。
2. **production entrypoint 是什么？** 旧 `tools/closure_gate.py`（子串判定 accepted）与旧 registry（自由文本状态）；新控制面 assurance/unified_completion + 冻结的 legacy 投影表。
3. **哪个 current-triplet 行为是 RED？独立 oracle 如何证明？** RED-A：closure_gate 实测 66/71（`"accepted" in status` 子串匹配自由文本如 "**accepted（-a/-b/-c/-d…）→ Phase 9 COMPLETE**"）。RED-B：旧 registry FC-1301 依赖列 = "FC-1301(链)"（自依赖）；Phase14 R0~R9 不在 71 行状态机；旧注册表现仅 47 行。
4. **允许改哪些文件？** 新增 `assurance/unified_completion/legacy/**`、receipts/CA-004/**、uc/legacy_disposition.py 的修复。**禁止**：旧计划目录任何文件、产品代码/配置/CI、catalog/roots。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-101（依赖 CA-004）。不解决：严格状态机/Closure 2.0（CA-101~109）、旧计划的 terminal notice（CA-306）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-003 accepted（机器状态）；closure 提交进行中。
- [x] 三仓 HEAD：revenue 为 CA-003 closure 提交（领取时重读）；filing `83c638e…`；wiki `ef125ed…`。
- [x] 冻结规范 hash：manifest-verify 严格 OK；三个 legacy 源文件（legacy_fc_status_registry/legacy_transition_matrix/completion_audit）是 14 内容文件之一，hash 冻结。
- [x] 工作文件 allowlist 不重叠；state.json/locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path 副本；真实构建只读冻结文件。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）；filing/wiki 只读。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：工具代码已实现（随 2f51672 落地），领卡时补 RED 归档与真实构建——`already_satisfied_candidate` 部分（代码与测试已存在），但 RED/真实工件/receipt/复核仍需完整走 20 步。
- **Production callers before / after**：before=0；after=legacy-build/verify CLI（assurance 工具）。
- **Scenario IDs / real tier**：治理工具卡；测试层 T0（解析/验证/变异）+ 真实冻结表构建。
- **RED command and exact expected failure**：见 receipts/CA-004/red/。
- **Independent oracle**：冻结表 hash（manifest）、旧 closure_gate 实测输出、旧 registry 行级证据。
- **Atomic implementation steps**：RED 归档 → legacy-build（71/31/26/9/5/10 全验证）→ legacy-verify → receipt → 复核 → closure。
- **Negative / fault / mutation / race**：负例（未知 successor、缺 successor、计数不符、环、源漂移）已由 8 测试覆盖；真实构建验证。
- **Side-effect budget**：仅写 assurance/unified_completion/**；旧计划目录/产品代码/catalog/roots 零写。
- **Migration, idempotence and rollback**：无迁移；工件 exclusive publish/CAS；rollback=删除工件。
- **Evidence paths**：`assurance/unified_completion/receipts/CA-004/`。
- **Acceptance criteria**：71 FC + 10 waves + 5 closure items 无遗漏/重复；DAG 无环；每个 contradicted/stale/pending 都有 successor；旧 owner 未写 terminal notice 前旧执行入口保持只读冻结。
- **Stop conditions / handoff**：同 CA-001（弱模型清单 §9）。
