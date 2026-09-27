# RED.md — ZR-1105 最终需求—证据 closure ledger（Phase 11 收官卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1105 验收套件**：glob tests/**/*zr1105* → 零命中。
- **G2 无最终 closure ledger 组合验收**：legacy_disposition（71 FC projection）、legacy_gate、state.json（accepted 真源）、CA-305 六问题映射各自存在；无"六目标 machine pass + 需求→证据覆盖 + 旧计划只读投影 + validator exit-0 + ledger 完整性"一体验收。
- **G3 真实现状（只读确认）**：113 accepted 仅 ZR-1105 自身 preflight；**发现吸收卡**（CA-201/ZR-901/ZR-801 不在 state——README §7 由 CA 链吸收）。

## 既有能力（不重复建设）

- legacy_disposition（71 FC/10 waves/5 closure items successor 映射 + verify）；legacy_gate.report；state.json；CA-305 GOAL_EVIDENCE 映射（六问题→证据单元）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1105_closure_ledger.py`（6 tests：C1 六目标 machine pass；C2 需求→证据覆盖；C3 旧计划只读投影（含吸收卡）；C4 validator exit-0；C5 ledger 完整性），产品零改动。
