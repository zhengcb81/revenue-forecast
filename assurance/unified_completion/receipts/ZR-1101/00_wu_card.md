# ZR-1101 工作单元卡（preflight）— Phase 11：机器 closure gate

- 领取时间：2026-08-31T19:12Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1101`（CA-306 closure → ZR-1101，DAG 解锁）；锁 ZR-1101（owner=zr1101-implementer，nonce 44f6daf7…）。
- 依赖：全部 mandatory ZR/CA（阶段 A~J 全闭 ✅，109 accepted）。

## 领取前五问

1. **推进哪个用户目标/痛点？** Phase 11 首卡——机器 closure gate（registry："无 pending/blocked/known-gap 被误关；所有 receipt/paths/hashes/freshness 有效"）。现状缺口（RED）：无机器 closure gate 组合验收。
2. **production entrypoint 是什么？** `state.json`（accepted 真源 + closure 记录）；`receipts/**`（11/12/13/14 receipts）；`closure_gate`/`receipt_validator`/`verify_closure_ledger`（工具面）；git 三仓对象库（triplet 有效性）。
3. **RED？** glob tests/**/*zr1101* → 零命中；无"全链路 + 无误关 + canonical + triplet + 时间戳"一体验收；**发现历史命名差异（14 closure / 早期 12 无 base_triplet）需兼容**。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1101_closure_gate.py`；receipts/ZR-1101/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、旧计划目录写入（CA-306 约束）、registry 写、下载、LLM。
5. **下一单元解锁？** ZR-801 处置（scenario registry 由 CA-105 吸收）→ 全部闭环。本卡不做：旧 ledger 改写。

## Acceptance criteria

- **C1 全链路 + 无误关**：每个 accepted 单元有 11+12+13/14 receipts + state reviewer/closure.by/next；无 known-gap/blocked 标 accepted。
- **C2 receipts canonical + triplet**：全部 11/12 canonical hash 重算一致；result_triplet 全 40-hex（早期 12 无 base_triplet 容忍；14 closure 命名接受）。
- **C3 closure 覆盖 + 工具面**：machine state 每 accepted 单元有 closure.by；verify_closure_ledger 可导入。
- **C4 时间戳一致**：closure.at_utc ≤ state.updated_at_utc（无 future-dated）。
- **C5 triplet 对象存在**：每单元 result_triplet 三仓 commit 均为有效 git 对象。
- **C6 质量门（卡级）**：revenue 全量零回归（基线 1027+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 只读校验 + git cat-file；零网络/下载/LLM；旧 closure_ledger.json（旧计划）不改写（CA-306 约束）。
