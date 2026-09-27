# RED.md — CA-206 不可豁免自然时间 soak（阶段 H CA 部分收官卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-206 验收套件**：glob tests/**/*ca206* → 零命中。
- **G2 无 soak 窗口计算器**：tools/ 与 uc/ 全量 grep soak/window/自然时间 → 无窗口累积逻辑；daily_t2_schedule/weekly_t3_schedule 只有单次 freshness 判定（fresh/stale/missing），无"7 Daily + 2 Weekly + 1 Monthly + 1 alert drill 累积窗口"。
- **G3 机制在位（不重复建设）**：ZR-902/903 ledger（write_ledger/read_ledger/freshness_status）+ ZR-904 release_gate（alert ack/retry）+ ZR-905 audit 自检——窗口判定的输入（run ledger + alert journal）与输出消费（release gate）均在。

## 既有能力（不重复建设）

- ZR-902 daily ledger/freshness；ZR-903 weekly ledger/blocked；ZR-904 release_gate alert ack + SLI；ZR-905 audit self-test；CA-202~205 各自验收。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca206_soak_window.py`（13 tests：纯函数窗口计算器——daily 连续 7 天链（缺失/陈旧/重复/复制/not-ok 断链）、weekly distinct 周 + 最新新鲜、monthly ≤35d、alert drill ack、聚合确定性 + 未满 PENDING），产品零改动。
