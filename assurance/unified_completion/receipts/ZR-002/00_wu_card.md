# ZR-002 工作单元卡（共享证据关闭）— command/scenario/receipt schema 冻结与写锁

- 领取时间：2026-08-14T04:55Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-002`；units.ZR-003.status=accepted + closure.next=ZR-002。
- 依赖：ZR-001（accepted ✅）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** A0 收尾：ZR-002 要求冻结 command/scenario/receipt schema、计划写锁和 shared-resource lock。按 README §7 重叠主题表（"receipt、command、closure validator → CA-101～109 → ZR-002、ZR-103；只实现CA版本；ZR目标用同一receipt关闭"），本卡以 CA 链同一实现验收，不写第二套代码。
2. **production entrypoint 是什么？** assurance 工具链：`uc/commands.py`（CA-104）、`uc/receipt.py`（CA-102）、`uc/lock.py`+`uc/casfile.py`（CA-001）、`uc/strict_state.py` per-unit 锁（CA-101）、`scenarios/scenario_registry.json`（CA-105）。
3. **哪个 current-triplet 行为是 RED？** 本卡无 RED：目标行为已由 CA 链实现并 accepted（already_satisfied 证据路径，runbook §8）。旧账本命令缩减/无锁行为已在 CA-001/104 的 RED 中演示并修复。
4. **允许改哪些文件？** `receipts/ZR-002/**` 与 `state.json`。禁止任何产品/assurance 代码改动（共享证据关闭不得顺手改 CA 实现）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-101~105（依赖 ZR-002）。本卡不新增 validator/lock 代码；若 CA 证据失效则必须回 blocked 并重新裁决，不得静默降门。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（assurance owner）。
- **Current-state drift verdict**：`already_satisfied_candidate` —— ZR-002 四要素逐一映射 CA 链：
  | ZR-002 要素 | CA 实现 | 证据 |
  |---|---|---|
  | command schema/attestation（命令不能被实施者缩减） | CA-104 | `uc/commands.py` 冻结 spec + 不可变结果（output hashes、secret-free、replay-diff）+ `command-run/replay` CLI + tests/test_commands.py |
  | scenario registry 有 hash | CA-105 | `scenarios/scenario_registry.json`（sha256 a350a3c9…）197 场景机器注册表 |
  | receipt schema 冻结 | CA-102 | `uc/receipt.py` content-addressed（canonical hash、N/N-1、triplet git-object 校验） |
  | 计划写锁 + shared-resource lock（并发写入 mutation 被拒） | CA-001 + CA-101 | `uc/lock.py`+`uc/casfile.py` 单 writer/CAS/代际守卫；`uc/strict_state.py` per-unit 锁；mutation-run 30/30 全杀 |
- **Acceptance criteria**：本卡 receipt 引用上述 CA 验收并复跑 mutation-run + receipt-validate 门；独立 reviewer 确认映射无遗漏、CA 门未降。
- **Stop conditions / handoff**：CA 证据不可复现 → blocked 并回 CA 对应单元裁决。
