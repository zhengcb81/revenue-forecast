# RED.md — ZR-905 审核机制自测试（阶段 H 第四卡）

## 探针（全部在当前机器实跑）

- **G1 无八类 AUD2 失败注入套件**：grep audit_self_test/AUD2 → 零命中（仅 scenario_matrix 与 ZR-902/903/904 卡描述提及 AUD2 语义）；无测试把 AUD2-01~08 八类失败模式注入 ledger/freshness/release gate/SLI/manifest/reviewer-gate 机制并断言全红——**审核机制本身未经受检**。

## 既有能力（不重复建设）

- ZR-902/903：daily/weekly ledger + freshness 三态 + alert journal + release_gate 纯函数。
- ZR-904：compute_sli（十项指标含 catalog 回归推导）、release_decision（fresh+完整+SLI 全绿）、validate_report（自 hash 链）、publish_all_pending（原子发布）。
- uc：manifest-verify（AUD2-07 漂移检测）、strict_state.ReviewerGateError（AUD2-08）。

## 结论

G1 为真实缺口（`still_missing`）；实施 = `tests/test_zr905_audit_self_test.py`（八类 AUD2 注入 + 恢复幂等），产品零改动。
