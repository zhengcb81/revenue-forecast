# CA-109 工作单元卡（preflight）— 旧 gate 隔离与兼容输出

- 领取时间：2026-08-14T06:00Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-109`；units.CA-108.status=accepted + closure。
- 依赖：CA-107、CA-108（均 accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01：旧 closure_gate/receipt_validator/scenario_coverage 只能作 migration reader 或被显式替换；workflow/release 不得继续调用旧语义；无双写状态源。
2. **production entrypoint 是什么？** 三仓 .github workflows、.githooks、tools、scripts、e2e 的旧工具引用。
3. **哪个 current-triplet 行为是 RED？** quality.yml:46-47 在 CI 中调用 verify_closure_ledger.py 作为 gate（旧语义）；故意只跑旧 gate 得绿时新 architecture gate 必须红。
4. **允许改哪些文件？** uc/legacy_gate.py、tests/test_legacy_gate.py、receipts/CA-109/**。禁止：产品代码/配置/CI（CI 重接线归 CA-201，本卡只登记 finding）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-201（依赖 CA-107、ZR-105、ZR-901）。不解决：CI 实际重接线（CA-201）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-108 accepted（机器状态）。
- [x] 三仓 HEAD：revenue=CA-108 closure 提交（领取时重读）；filing/wiki 未变。
- [x] manifest-verify 严格 OK。
- [x] 工作文件 allowlist 不重叠；locks 单 writer。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）；三仓只读扫描。
- **Current-state drift verdict**：`still_missing`——无 caller 扫描/隔离判定。
- **Acceptance criteria**：production/CI caller 只指向 Closure 2.0（旧引用全部登记为 finding + successor）；旧历史 ledger 只读展示；无双写状态源。
- **Stop conditions / handoff**：同 CA-001。
