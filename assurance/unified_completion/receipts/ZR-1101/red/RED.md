# RED.md — ZR-1101 机器 closure gate（Phase 11 首卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1101 验收套件**：glob tests/**/*zr1101* → 零命中。
- **G2 无机器 closure gate 组合验收**：closure_gate/receipt_validator/verify_closure_ledger 工具在位；无"accepted 单元全链路（11+12+13/14）+ 无 known-gap/blocked 误关 + receipts canonical + triplet 40-hex + 时间戳一致 + triplet 对象存在"一体验收。
- **G3 真实现状（只读确认）**：109 accepted，仅 ZR-1101 自身 preflight_locked（无其他 pending/blocked）；**发现历史命名差异**：ZR-805 用 14_closure_receipt（早期约定）且 ZR-601 等早期 12 无 base_triplet——机器门需兼容。

## 既有能力（不重复建设）

- closure_gate/receipt_validator（canonical hash 校验）；verify_closure_ledger（CI 面）；state.json（accepted 真源）；CA-301 已证 189/189 receipts canonical；receipts/** 全量。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1101_closure_gate.py`（6 tests：C1 全链路 + 无误关；C2 receipts canonical + triplet；C3 closure 覆盖 + 工具面；C4 时间戳一致；C5 triplet 对象存在），产品零改动。
