# CA-103 工作单元卡（preflight）— revision selector 与独立 reviewer 配对

- 领取时间：2026-08-14T02:25Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-103`；units.CA-102.status=accepted + closure。
- 依赖：CA-102（accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01：消除"取第一个 implementer receipt"的任意性——显式 revision 链（supersedes）、唯一有效 pair（最新 implementer revision + 唯一 reviewer 决策）、实现者/复核者分离、finding closure 强制后继。
2. **production entrypoint 是什么？** assurance/unified_completion/receipts/** 的 receipt 集合；closure-advance 的 accepted 前置。
3. **哪个 current-triplet 行为是 RED？** (a) 无 revision 元数据——同一单位多个 receipt 时"第一个"是任意的；(b) 无 reviewer 配对校验（reviewer 可引用任意 receipt，可为 self）；(c) changes_required 后旧 accepted 可回退覆盖；(d) P1/P2 finding 无强制后继。
4. **允许改哪些文件？** uc/revision.py、tests/test_revision.py、receipts/CA-103/**。禁止：产品代码/配置/CI/catalog/roots/旧计划。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-104（依赖 CA-102）。不解决：command registry（CA-104）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-102 accepted（机器状态）。
- [x] 三仓 HEAD：revenue=a745e06（领取时重读）；filing/wiki 未变。
- [x] manifest-verify 严格 OK。
- [x] 工作文件 allowlist 不重叠；locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`still_missing`——无 revision selector。
- **Production callers**：before=0；after=revision-select CLI + closure 前置校验。
- **Scenario IDs / real tier**：治理工具卡；T0 契约/变异测试。
- **RED**：见 receipts/CA-103/red/。
- **Independent oracle**：supersedes 链图校验、canonical hash 引用一致性、身份分离。
- **Acceptance criteria**：唯一有效 pair；rejected/changes_required 不被旧 accepted 覆盖；P1/P2/P3 未关 finding 阻断 phase exit。
- **Stop conditions / handoff**：同 CA-001。
