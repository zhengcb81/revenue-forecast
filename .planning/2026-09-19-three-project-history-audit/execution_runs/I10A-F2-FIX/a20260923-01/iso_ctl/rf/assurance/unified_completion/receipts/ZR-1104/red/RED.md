# RED.md — ZR-1104 观察期与真实 rollback drill（Phase 11 第四卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1104 验收套件**：glob tests/**/*zr1104* → 零命中。
- **G2 无观察期+drill 组合验收**：CA-206 soak 窗口（7/2/1/1 累积）、CA-304 rollback drill（activation 往返）、FC-705 legacy-hit 门各自存在；无"观察完整性 + legacy-hit 门 + cohort rollback/re-activate + 无人工豁免 + drill journal"一体验收。
- **G3 机制在位（不重复建设）**：test_ca206_soak_window（daily/weekly/monthly/drill_window + soak_status）；test_ca304_r9_removal（close_gate_allowed + CatalogStore activation 往返）；test_dropbox_full_chain_fc505（rollback_activation）。

## 既有能力（不重复建设）

- CA-206 soak 窗口纯函数；FC-705 close_gate_allowed；activation.apply/rollback（ZR-1003/CA-304 已验证）；assertion_service seed。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1104_observation_drill.py`（9 tests：C1 观察完整性 7/2/1/1；C2 legacy-hit 门 + 两零 hit 窗口；C3 cohort rollback/re-activate 往返；C4 无人工豁免；C5 drill journal ack），产品零改动。
