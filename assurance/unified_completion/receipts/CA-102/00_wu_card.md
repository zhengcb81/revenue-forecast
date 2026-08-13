# CA-102 工作单元卡（preflight）— 内容寻址 receipt schema

- 领取时间：2026-08-14T01:50Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-102`；units.CA-101.status=accepted + closure。
- 依赖：CA-101（accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01：receipt 是证据系统的原子单位——分型（implementer/reviewer/closure）、必填字段、canonical hash 可重算、任何篡改必红。
2. **production entrypoint 是什么？** assurance/unified_completion/receipts/** 的 JSON receipt；旧 FC receipt（assurance/fc/**）为历史。当前无机器校验（缺 canonical hash）。
3. **哪个 current-triplet 行为是 RED？** (a) 现有 receipt 无 canonical hash——scratch 篡改后无任何工具检出；(b) commands/scenarios 为空的 receipt 无门（治理卡 scenario_results=[] 属正常，需显式 scenario_note 豁免）；(c) 旧 FC-1001 receipt `policy_sha256: "not-applicable"` 滥用；(d) 伪 hash（历史前科已修复，新 schema 必须在机器层再防）。
4. **允许改哪些文件？** uc/receipt.py、tests/test_receipt.py、receipts/CA-102/**。禁止：产品代码/配置/CI/catalog/roots/旧计划。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-103/CA-104（依赖 CA-102）。不解决：revision selector（CA-103）、command registry（CA-104）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-101 accepted（机器状态，含合法迁移路径证据）。
- [x] 三仓 HEAD：revenue=6028af7（领取时重读）；filing/wiki 未变。
- [x] manifest-verify 严格 OK。
- [x] 工作文件 allowlist 不重叠；locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`still_missing`——无 receipt 机器校验器。
- **Production callers**：before=0；after=receipt-validate CLI。
- **Scenario IDs / real tier**：治理工具卡；T0 契约/变异测试。
- **RED**：见 receipts/CA-102/red/。
- **Independent oracle**：canonical hash 重算、git 对象存在性、字段分型表。
- **Acceptance criteria**：canonical hash 可重算；未知字段/版本 N/N-1 策略；任何内容篡改必红。
- **Stop conditions / handoff**：同 CA-001。
