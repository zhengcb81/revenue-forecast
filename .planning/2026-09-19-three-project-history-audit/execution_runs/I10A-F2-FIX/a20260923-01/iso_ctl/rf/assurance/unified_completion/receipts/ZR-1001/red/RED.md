# RED.md — ZR-1001 release 预备（阶段 I 首卡）

## 探针（全部在当前机器实跑）

- **G1 无 release 就绪聚合**：grep release_readiness/release_authorization → 零命中；三仓 HEAD fingerprint、catalog integrity、容量/耗时预算无统一验证。
- **G2 无备份/回滚预飞检查**：无备份可读性验证；无回滚点记录/步骤预飞机制。
- **G3 无用户授权标记**：无 release 窗口授权机制（未授权 → 不进入窗口）。

## 既有能力（不重复建设）

- uc manifest/state 机制（HEAD triplet 可查）；daily/weekly ledger + release_gate（ZR-902~904）；全量测试基线 881+106（~150s）。

## 结论

G1~G3 为真实缺口（`still_missing`）；实施 = `tools/release_readiness.py`（fingerprint/integrity/预算/备份/回滚预飞/授权聚合）+ 测试钉死，产品零改动。
