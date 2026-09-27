# I10A-F2-FIX a20260923-01 — recovery

状态占位（oracle 冻结时补全）。

- 产品面：RF 仓库 **READ-ONLY**；全部产品改动发生在 `iso/rf/**`（RF 的隔离副本），交付=本 attempt 的 `changes.diff`。
- 无 git；命令面 network=0。
- 若中断：从 `commands.json` 的逐条 argv 重放；oracle sha 记录在 `oracle.md` 头部与 `evidence/run_log.jsonl`（ORACLE-FREEZE 条目之后才是判据运行）。
- 基线证据：`evidence/family_before_junit.xml`（iso 未改基线全套）、`evidence/probe_before/**`（I-10-A 探针 4 case × 5 臂）。
- 修复仅动 `scripts/forecast/calc.py`、`scripts/forecast/segments.py`（产品面）；测试面夹具改动逐文件披露于 `decision.md` 与 `changes.diff`。
