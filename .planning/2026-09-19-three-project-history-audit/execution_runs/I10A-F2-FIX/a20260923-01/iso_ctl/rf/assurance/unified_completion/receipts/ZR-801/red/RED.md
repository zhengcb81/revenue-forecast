# RED.md — ZR-801 吸收卡验收：scenario machine registry（Phase 11 终局处置）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-801 验收套件**：glob tests/**/*zr801* → 零命中。
- **G2 registry 在位**：`assurance/unified_completion/scenarios/scenario_registry.json`（CA-105 建立）：197 unique（old95+new102），tier T0~T4 复合。
- **G3 吸收文档**：README §7 明确 scenario machine registry 由 CA-105/106 唯一实现，ZR-801 只定义业务场景。

## 既有能力（不重复建设）

- CA-105 scenario_registry.json（唯一 registry）；uc.cli scenario-build/scenario-verify（唯一算法）；README §7 吸收记录。

## 结论

G1 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr801_scenario_registry.py`（7 tests：C1 registry 完整 197 unique + tier 合法；C2 uc 工具唯一权威；C3 业务面家族在位；C4 无第二 registry；C5 吸收文档在 README §7），产品零改动。
