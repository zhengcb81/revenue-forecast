# Phase 13 WU 卡片 — 可观测性、健康度、性能与容量（FC-1301~1304）

> 创建 2026-08-13。Owner: company-wiki 为主 + revenue 工具侧。前置：Phase 12 COMPLETE ✓（FCAP 63/71）。生产只读 preflight 见 findings 62。

## FC-1301：统一 reason/outcome taxonomy — implemented

- **发现**：observability.REASONS（1.0，28 codes）落后于生产实际发射的 50 个 reason 字面量。
- **交付**：注册全部缺码 → 1.1（78 codes，按 adapter/acquisition、artifact 门、worker/控制面、latest/gap、documents/scan、llm 分组）；新审计门 `test_fc1301_reason_taxonomy.py`（AST 扫生产源码 reason 字面量，未注册 → 红；描述非空检查；版本检查）。
- **M**：注入 `reason="unregistered_drift_code"` 发射 → 门红（unregistered reason codes…）；还原后绿。

## FC-1302：scan health/error budget — implemented

- **根因（findings 62）**：155→242 增长 = Dropbox 根一个用户空 Excel 每 20 分钟被重复计错（unchanged=true、new_errors=0）。累计 error-run 数不是健康信号。
- **交付**：T2 runner scan_health 重构为增量语义——new_errors_24h（预算 0）+ recurring_unchanged_runs_24h（诚实计数）+ interrupted delta（预算 5）；completed_with_errors 总数降为信息性。新测试 test_fc1302_scan_health.py（recurring 不 fail / new errors fail / interrupted delta fail）。
- **生产验证**：exit 0，33 recurring / 0 new——242 总数不再误报。

## FC-1303：真实 catalog SLO — implemented

- **交付**：`tools/slo_probe.py`（只读；exact/latest/bundle p50/p95/p99 + peak RSS；冻结预算 exact/latest/bundle p95=5s、RSS=2GB；psutil Windows RSS，无 psutil 诚实 None 跳过）。
- **生产实测**：p95 ~0.6s（3 查询类），RSS 21MB——远低于预算，exit 0。
- **契约测试**：tools/tests/test_slo_probe.py（预算冻结 + 百分位序统计 + 只读契约扫描）。

## FC-1304：容量和并发故障 — verified（无新机制，证据引用）

- **既有证据（全部实测通过）**：CAP-01~05（unchanged 不重 hash/mtime 重 hash/10 并发 resolve 无死锁/并发读零写，test_capacity_concurrency.py 11 passed）；MIG 灾难演练（test_disaster_drill_fc405.py）；single-flight + 有界锁（test_close_gap_concurrency_fc804.py + operation_lock 14 passed）；MIG-07 原子性（FC-405）。
- **容量快照（生产只读）**：catalog.sqlite3 = 47GB（2026-08-13）。磁盘余量此前 99% 问题已由用户 D4 决策（不迁 D:）+ catalog-space 退役处理；持续监控归 FC-1302 T2。
- 无新代码——验证型 FC，证据在既有 receipts + 本次重跑记录。

## exit gate（Phase 13）

- T2 报告含健康阈值 + SLO verdict；155→242 有可解释基线（findings 62：单文件重复错误 + 增量语义）。

## 不变式

- 生产全程只读（T2/SLO probe/验证重跑均 mode=ro）；零生产写入。
- 阈值全部实测后冻结；taxonomy 加法式（码只加不删，仅可弃用）。
