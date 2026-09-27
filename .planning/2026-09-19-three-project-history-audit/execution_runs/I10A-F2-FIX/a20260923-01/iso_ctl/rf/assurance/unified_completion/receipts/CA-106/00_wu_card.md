# CA-106 工作单元卡（preflight）— 独立 oracle 与 side-effect ledger

- 领取时间：2026-08-14T04:10Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-106`；units.CA-105.status=accepted + closure。
- 依赖：CA-104、CA-105（均 accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01/P06（伪计数）：side-effect 计数必须来自 ledger/journal/OS fingerprint，而非被测对象的自述 summary；隐私路径脱敏但 hash 可核。
2. **production entrypoint 是什么？** receipts 的 side_effect_counts 声明字段（无测量来源）；无独立 oracle。
3. **哪个 current-triplet 行为是 RED？** (a) 旧 FC receipt 与现有 receipt 的 side_effect_counts 是声明值（无 ledger 支撑）；(b) 无 root fingerprint before/after 机制；(c) 无隐私脱敏规范（receipt 里出现绝对路径）。
4. **允许改哪些文件？** uc/ledger.py、tests/test_ledger.py、receipts/CA-106/**。禁止：产品代码/配置/CI/catalog/roots。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-107（依赖 CA-101~106）。不解决：三仓全量 receipt 搜索（CA-107）、mutation suite（CA-108）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-105 accepted（机器状态）。
- [x] 三仓 HEAD：revenue=CA-105 closure 提交（领取时重读）；filing/wiki 未变。
- [x] manifest-verify 严格 OK。
- [x] 工作文件 allowlist 不重叠；locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`already_satisfied_candidate`（ledger 模块已随 CA-105 closure 提交并 8 测试通过）——RED/真实工件/receipt/复核仍完整走 20 步。
- **Production callers**：before=0；after=ledger 库 API（CLI 由后续 runner 使用）。
- **Scenario IDs / real tier**：治理工具卡；T0 契约/变异测试。
- **RED**：见 receipts/CA-106/red/。
- **Independent oracle**：OS 级 root fingerprint diff、ledger 与声明计数对账。
- **Acceptance criteria**：被测 summary 与独立 ledger 不一致即红；隐私路径脱敏但 hash 可核；T2 生产 roots 零写（fingerprint 只读）。
- **Stop conditions / handoff**：同 CA-001。
