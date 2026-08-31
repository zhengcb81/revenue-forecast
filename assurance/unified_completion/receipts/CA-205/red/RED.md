# RED.md — CA-205 原子报告/freshness/告警与 release 消费（阶段 H CA 部分第四卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-205 验收套件**：glob tests/**/*ca205* → 零命中。
- **G2 无 CA-205 组合验收**：ZR-904 覆盖 release_gate 机制（atomic publish/SLI/alert/no-stale）但无"dashboard 与 release 同 schema 消费 + 故障矩阵全红 + 恢复幂等 + 报告 sample/command 完整字段"一体验收；REQUIRED_REPORT_FIELDS 仅 (run_id, started_at, triplet, ok, report_sha256)，不含 sample/command。
- **G3 机制在位（不重复建设）**：tools/release_gate.py（validate_report/publish_report/publish_all_pending/compute_sli/release_decision/append_alert/pending_alerts/mark_acked）；tools/audit_dashboard.py（collect_reports/release_gate，T2/T3 run-dir 布局）。

## 既有能力（不重复建设）

- ZR-904 release_gate 全机制；FC-1104 audit_dashboard（T2≤24h/T3≤7d 门 + ledger 原子写）；daily/weekly ledger（ZR-902/903）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca205_atomic_report.py`（7 tests：C1 原子 publish 完整字段 + dashboard 同 schema；C2 故障矩阵全红；C3 恢复幂等；C4 alert ack/retry + sink 响亮失败；C5 无 stale-green 复活），产品零改动。
