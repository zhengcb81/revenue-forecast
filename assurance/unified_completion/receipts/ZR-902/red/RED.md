# RED.md — ZR-902 实际调度每日 Windows T2（阶段 H 首卡）

## 探针（全部在当前机器实跑）

- **G1 无实际 schedule**：`schtasks /query /fo csv` 实测 396 个 Windows 任务，grep revenue/daily_t2/t2_runner/company_wiki → 零命中；`tools/daily_t2_runner.py` 存在但从未被调度（脚本存在 ≠ 实际运行，AUD2-01 RED）。
- **G2 无 freshness 门**：`assurance/runs/` 下最近 report.json = 2026-08-13（fc1302-preflight/fc1302-verify/phase14-r1-verify），距今 9 天——无"最近 run ≤24h"判定，旧绿可被沿用（AUD2-02 RED）；grep daily_manifest/freshness/stale → 零命中。
- **G3 无 release 消费门**：无任何机制消费 daily run 状态（缺 run/半报告/旧绿 → release 红，AUD2-03 RED）；grep release gate/daily → 零命中。

## 既有能力（不重复建设）

- `tools/daily_t2_runner.py`（FC-1102）：真实 catalog mode=ro 检查（triplet/samples/scan health/legacy/schema drift/latency/roots fingerprint/trends）+ 报告隔离（assurance/runs/{run_id}/report.json）+ 非零退出——runner 本体完备。
- ZR-806 固定 5 样本唯一/新鲜语义已钉死（本卡消费其样本检查）。

## 结论

G1~G3 全部为真实缺口（`still_missing`）；实施 = `tools/daily_t2_schedule.py`（注册/查询/run 包装/台账/freshness/告警/release 门）+ 测试钉死三态判定与消费门，产品零改动。
