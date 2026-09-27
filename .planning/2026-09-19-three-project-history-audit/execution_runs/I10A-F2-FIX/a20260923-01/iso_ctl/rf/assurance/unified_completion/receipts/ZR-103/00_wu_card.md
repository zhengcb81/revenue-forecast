# ZR-103 工作单元卡（共享证据关闭）— closure/receipt/command validator

- 领取时间：2026-08-14T07:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-103`；units.ZR-102.status=accepted + closure.next=ZR-103。
- 依赖：ZR-002（accepted ✅）。Registry 依赖列=ZR-002。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 契约基座。ZR-103 要求 closure/receipt/command validator 对：篡改 hash、同一 reviewer、缺命令、skip、triplet 漂移、越权 side effect 全部拒绝。按 README §7（"receipt、command、closure validator → CA-101～109 → ZR-002、ZR-103；只实现CA版本；ZR目标用同一receipt关闭"），本卡引用 CA 链同一实现与 receipt，不写第二套 validator。
2. **production entrypoint 是什么？** assurance 工具链：`receipt-validate`（CA-102 canonical/N-N-1/triplet git-object）、`command-run/replay`（CA-104 输出 hash、secret-free）、`revision-select`（CA-103 reviewer 配对）、`closure-report`（CA-107 诚实 incomplete）、`mutation-run`（CA-108 30 mutation）、strict_state reviewer 门（CA-101）。
3. **哪个 current-triplet 行为是 RED？** 无：目标行为已由 CA 链实现并 accepted。若六项拒绝门任一失效（新鲜复跑不绿），本卡 blocked 回 CA 对应单元裁决。
4. **允许改哪些文件？** `receipts/ZR-103/**` 与 `state.json`。禁止任何代码改动。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-104/105。本卡不新增 validator；六项拒绝门的映射见下。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（assurance owner）。
- **Current-state drift verdict**：`already_satisfied_candidate` —— ZR-103 六要素逐一映射 CA 链：
  | ZR-103 要素 | CA 实现 | 证据 |
  |---|---|---|
  | 篡改 hash 拒绝 | CA-102 canonical hash + CA-108 tamper mutations | receipt-validate OK + mutation-run 30/30 |
  | 同一 reviewer 拒绝 | CA-101 reviewer 门（reviewer≠implementer） | strict_state validate_transition |
  | 缺命令拒绝 | CA-104 command attestation（必需命令清单+结果不可变） | command-run/replay CLI + tests |
  | skip 拒绝 | CA-105 scenario registry + CA-107 closure-report 诚实 incomplete | closure-report verdict=incomplete 且 reason set 完整 |
  | triplet 漂移拒绝 | CA-102 triplet git-object 校验 + CA-002 envfreeze | receipt-validate + env-verify |
  | 越权 side effect 拒绝 | CA-106 side-effect ledger（declared vs measured）+ CA-104 secret-free | tests/test_ledger.py + commands tests |
- **Acceptance criteria**：本卡 receipt 引用上述 CA 验收并新鲜复跑 mutation-run + receipt-validate + closure-report + revision-select；独立 reviewer 确认映射无遗漏。
- **Stop conditions / handoff**：CA 证据不可复现 → blocked。
