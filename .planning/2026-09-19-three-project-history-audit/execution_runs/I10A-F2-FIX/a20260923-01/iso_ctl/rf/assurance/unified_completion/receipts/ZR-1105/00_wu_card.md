# ZR-1105 工作单元卡（preflight）— Phase 11：最终需求—证据 closure ledger（收官卡）

- 领取时间：2026-08-31T20:27Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1105`（ZR-1104 closure → ZR-1105）；锁 ZR-1105（owner=zr1105-implementer，nonce 0c0ad4b9…）。
- 依赖：ZR-1104（观察期/rollback drill，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** Phase 11 收官卡——最终需求—证据 closure ledger（registry："六目标逐项 machine pass；旧计划只读映射；validator exit 0 后整体 complete"）。现状缺口（RED）：无最终 closure ledger 组合验收。
2. **production entrypoint 是什么？** `legacy_disposition`（71 FC/10 waves/5 closure items successor 投影 + verify）；`legacy_gate.report`（三仓诚实报告）；`state.json`（accepted 真源）；CA-305 GOAL_EVIDENCE 六问题映射；receipts/**（11/12/13/14）。
3. **RED？** glob tests/**/*zr1105* → 零命中；无组合验收；**发现吸收卡（CA-201/ZR-901/ZR-801 不在 state，README §7）**。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1105_closure_ledger.py`；receipts/ZR-1105/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、旧计划目录写入、下载、LLM。
5. **下一单元解锁？** ZR-801 处置 → 全部闭环。本卡不做：旧计划 terminal notice 写入（CA-306/owner 动作）。

## Acceptance criteria

- **C1 六目标 machine pass**：每成功问题的证据单元全 accepted（CA-305 映射）。
- **C2 需求→证据覆盖**：每 accepted 单元有 11/12/13-or-14 receipts + reviewer + closure.by。
- **C3 旧计划只读投影**：71 FC rows + 5 closure items → accepted CA successor 或吸收卡（CA-201/ZR-901/ZR-801 per README §7）；旧目录永不改写。
- **C4 validator exit-0**：legacy disposition verify fresh（problems==[]）+ legacy_gate 诚实报告。
- **C5 ledger 完整性**：从 state 生成 ledger = 每 accepted 单元一条（implementer/reviewer/closure），每问答案完整（无聚合替代）。
- **C6 质量门（卡级）**：revenue 全量零回归（基线 1057+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 只读映射（state/receipts/disposition）；零网络/下载/LLM；旧计划目录零写入。
