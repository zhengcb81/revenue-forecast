# RED.md — ZR-903 实际调度每周/发布前 T3（阶段 H 第二卡）

## 探针（全部在当前机器实跑）

- **G1 无周调度**：`schtasks /query /fo csv` 实测 396 个 Windows 任务零本项目条目；grep weekly_t3/weekly schedule/ZR-903 → 零命中；T3 套件（filing-fetch tests/test_e2e_download.py）存在但从未被调度（AUD2-01 RED）。
- **G2 无 ≤7d freshness 门**：无 weekly ledger/freshness 机制（grep weekly_manifest/freshness → 零命中）；无"旧绿不沿用"判定（AUD2-02 RED）。
- **G3 无 blocked 告警/release 消费**：无 release 消费 weekly run 状态的机制；T3 套件因凭据/网络缺失而全 skip 时无显式 blocked 记录（CA-203 RED："网络/凭据缺失被记 pass"——AUD2-03 RED）。

## 既有能力（不重复建设）

- ZR-805 已钉死 T3 授权语义（opt-in 门/journey 零下载 oracle/单一下载器）；T3 套件本体在 filing-fetch（FILING_FETCH_E2E_DOWNLOAD=1 + 临时 wiki）。
- ZR-902 的调度机制（台账/freshness/告警/release 门/schtasks 封装）为本卡同型复用模板。

## 结论

G1~G3 全部为真实缺口（`still_missing`）；实施 = `tools/weekly_t3_schedule.py`（run-weekly 调 T3 套件 opt-in + weekly ledger ≤7d + blocked 告警 + release 门 + schtasks weekly）+ 测试钉死三态/告警/消费门/全 skip→blocked 语义，产品零改动。
