# RED.md — CA-202 Daily T2 实际 scheduler（阶段 H CA 部分首卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-202 验收套件**：glob tests/**/*ca202* + assurance/unified_completion/tests/*ca202* → 零命中。
- **G2 无真实 runner 组合验收**：ZR-902 覆盖 schedule/ledger/freshness/alert/release 纯逻辑（tools/daily_t2_schedule）；FC-1102 tools/daily_t2_runner.run_checks 存在但无"production catalog 完整报告 + 三 root unique 样本 + 零写 oracle + 只读连接/SLO + 缺 run 告警/阻断"组合验收测试。
- **G3 机制在位（不重复建设）**：daily_t2_runner.run_checks（真实 catalog mode=ro + query_only，八类检查 + 精确 triplet）；daily_t2_schedule（write_ledger/freshness_status/append_alert/release_gate）；company-wiki SourceResolver（ZR-806/1004 已证明三 root 只读 resolve）；_shallow_fingerprint oracle（ZR-806）。

## 既有能力（不重复建设）

- ZR-902 ledger/freshness/alert/release 语义；FC-1102 runner 八类检查；ZR-806 真实 T2 样本 + 浅指纹 oracle；ZR-1004 四 root resolve 模式；ZR-902~1009 全链已闭。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca202_daily_t2_runner.py`（10 tests：C1 真实 runner 报告 + 精确 triplet + samples；C2 零写 oracle；C3 三 root unique 样本；C4 只读连接 + SLO；C5 缺 run 告警/阻断 + fresh 放行），产品零改动、Task Scheduler 零触碰。
