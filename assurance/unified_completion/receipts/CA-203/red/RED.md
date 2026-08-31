# RED.md — CA-203 Weekly/发布前 T3（阶段 H CA 部分第二卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-203 验收套件**：glob tests/**/*ca203*（revenue + filing-fetch）→ 零命中。
- **G2 无 T3 全语义组合验收**：ZR-903 覆盖 schedule/ledger/blocked 纯逻辑；ZR-805 覆盖授权门/journal oracle/flag；FC-803/805 覆盖 LT 场景与真实下载——但无"首次下载→二次零下载（single-flight）→amendment→provider drift→provider/canonical 对账"一体的 CA-203 组合验收。
- **G3 机制在位（不重复建设）**：filing-fetch test_e2e_download.py（opt-in 三市场 + 损坏拒绝 + 二次零下载）；weekly_t3_schedule._suite_outcome（all-skipped blocked）；IsolatedWiki + spy_adapter（真实跨进程 json_command_v1，spy log 为独立 oracle）。

## 既有能力（不重复建设）

- ZR-903 weekly schedule；ZR-805 T3 授权；FC-803 LT-01~09 spy 场景基建；daily_t2_schedule ledger/alert/release（ZR-902）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca203_weekly_t3.py`（8 tests：C1 套件门 + blocked 语义；C2 首次下载/二次零写 single-flight；C3 amendment as-of 切割；C4 provider drift 本地保留；C5 provider/canonical 精确对账），产品零改动、真实 T3/调度零触发。
