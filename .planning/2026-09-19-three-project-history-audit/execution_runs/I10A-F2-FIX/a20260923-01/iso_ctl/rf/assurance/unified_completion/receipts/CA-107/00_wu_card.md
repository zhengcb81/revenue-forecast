# CA-107 工作单元卡（preflight）— 三仓 Closure 2.0

- 领取时间：2026-08-14T04:40Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-107`；units.CA-106.status=accepted + closure。
- 依赖：CA-101~106（均 accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01：三仓全量 receipt 搜索 + 每 WU 唯一有效证据 + triplet/freshness/review pairing/commands/rollback 验证；旧计划被诚实判 incomplete 且原因集合包含已知缺口。
2. **production entrypoint 是什么？** 三仓 assurance 目录（revenue unified_completion/receipts + assurance/fc；filing/wiki assurance/fc）+ 机器工件（state/legacy/scenario registry）。
3. **哪个 current-triplet 行为是 RED？** 删除 filing receipt、删除 reviewer、篡改 hash、切换 sibling HEAD、遗留 FC150x pending/R9——每种旧 gate 都无精确原因报告（旧 closure_gate 只报"剩五项"）。
4. **允许改哪些文件？** uc/closure.py、tests/test_closure.py、receipts/CA-107/**。禁止：产品代码/配置/CI/catalog/roots/旧计划。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-108（依赖 CA-107）。不解决：mutation suite（CA-108）、旧 gate 隔离（CA-109）、terminal notice（CA-306）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-106 accepted（机器状态）。
- [x] 三仓 HEAD：revenue=CA-106 closure 提交（领取时重读）；filing/wiki 未变。
- [x] manifest-verify 严格 OK；env/codegraph/legacy/scenario 工件齐全。
- [x] 工作文件 allowlist 不重叠；locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）；三仓只读扫描。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`still_missing`——无三仓统一 closure 报告。
- **Production callers**：before=0；after=closure-report CLI。
- **Scenario IDs / real tier**：治理工具卡；T0 契约/变异测试 + 真实三仓报告。
- **RED**：见 receipts/CA-107/red/。
- **Independent oracle**：receipt canonical hash、git 对象、工件 hash 交叉。
- **Acceptance criteria**：旧计划诚实判 incomplete 且原因含已知缺口；不显示"剩五项"。
- **Stop conditions / handoff**：同 CA-001。
