# CA-108 工作单元卡（preflight）— Closure mutation/negative suite

- 领取时间：2026-08-14T05:30Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-108`；units.CA-107.status=accepted + closure。
- 依赖：CA-107（accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01：至少 30 个 critical mutation 全部被 Closure 2.0 击杀（漏仓/漏 receipt/错 revision/自签/命令缩减/skip/blocked/旧 triplet/dirty/无 schedule/半报告/代理 SLO/伪零/缺样本/R9 未过/finding 未关）。
2. **production entrypoint 是什么？** CA-101~107 的验证器（receipt/revision/strict_state/ledger/scenarios/closure）。
3. **哪个 current-triplet 行为是 RED？** 各验证器没有 mutation 保证——单点缺陷可静默通过（对应 30 个 mutation 的基线）。
4. **允许改哪些文件？** uc/mutations.py、tests/test_mutations.py、receipts/CA-108/**。禁止：产品代码/配置/CI/catalog/roots/旧计划。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-109（依赖 CA-107、CA-108）。不解决：旧 gate 隔离（CA-109）。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）。
- **Current-state drift verdict**：`still_missing`——无 mutation suite。
- **Acceptance criteria**：critical mutation kill=100%；新增 closure 分支必须同时新增 mutation；mutation runner 失败不能用 skip 代替。
- 其余字段同 CA-101~107 模式。
