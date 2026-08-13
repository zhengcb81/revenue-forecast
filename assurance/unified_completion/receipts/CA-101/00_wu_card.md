# CA-101 工作单元卡（preflight）— 严格工作单元状态机与 DAG

- 领取时间：2026-08-14T01:05Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-101`（current_phase=B_evidence_closure_2_0）；units.CA-004.status=accepted + closure。
- 依赖：CA-004（accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01（假绿/状态自由文本）：以 machine JSON registry + 单向合法迁移 + 依赖门 + CAS + 单 writer 取代 Markdown 子串判定。
2. **production entrypoint 是什么？** assurance/unified_completion/state.json（v1 最小 schema）+ uc.cli state-update/closure-advance；旧 tools/closure_gate.py（子串判定，CA-109 隔离）。
3. **哪个 current-triplet 行为是 RED？** (a) state-update 允许 pending→accepted 直接跳跃（无迁移校验）；(b) 任何调用者可写 accepted（无 reviewer 身份/角色门）；(c) DAG 无环校验缺失（dag 模块只解析不验环）；(d) 无 per-unit 锁，并发写仅靠通用 CAS；(e) 非法状态文本被拒但合法枚举内的乱序不被拒。
4. **允许改哪些文件？** uc/（新增 strict_state.py + dag/state/cli 加固）、tests/（property tests）、receipts/CA-101/**。禁止：产品代码/配置/CI/catalog/roots/旧计划。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-102（依赖 CA-101）。不解决：receipt 内容寻址 schema（CA-102）、revision selector（CA-103）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-004 accepted（机器状态）；closure 提交已落地。
- [x] 三仓 HEAD：revenue=CA-004 closure 提交（领取时重读）；filing/wiki 未变。
- [x] manifest-verify 严格 OK；env/codegraph/legacy 基线工件存在且验证过。
- [x] 工作文件 allowlist 不重叠；locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`still_missing`——状态机无迁移表/依赖门/环校验/单 writer 语义。
- **Production callers**：before=state-update/closure-advance（宽松）；after=同一入口加严格门。
- **Scenario IDs / real tier**：治理工具卡；T0 property tests。
- **RED**：见 receipts/CA-101/red/。
- **Independent oracle**：状态迁移表对照、CAS 冲突、依赖图环检测、reviewer 身份字段。
- **Atomic implementation steps**：见 session 计划 B.1。
- **Acceptance criteria**：property test 生成非法图全部拒绝；Markdown 渲染只读视图；closure 只读机器真源。
- **Stop conditions / handoff**：同 CA-001。
