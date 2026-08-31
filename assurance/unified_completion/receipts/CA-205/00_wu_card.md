# CA-205 工作单元卡（preflight）— H：原子报告、freshness、告警与 release 消费

- 领取时间：2026-08-31T16:08Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-205`（CA-204 closure → CA-205）；锁 CA-205（owner=ca205-implementer，nonce 2f96ef51…）。
- 依赖：CA-202（Daily T2）、CA-203（Weekly T3）、CA-204（Monthly 泛化）（均 accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H CA 部分第四卡——原子报告/freshness/告警与 release 消费（registry："pending 临时文件→完整校验→原子 publish；dashboard/release 读取同一 schema；告警送达有 ack/重试；过期结果不可续命"）。现状缺口（RED）：ZR-904 有 release_gate 机制无组合验收；REQUIRED_REPORT_FIELDS 不含 sample/command。
2. **production entrypoint 是什么？** `tools/release_gate`（validate_report/publish_report/publish_all_pending/compute_sli/release_decision/append_alert/pending_alerts/mark_acked）；`tools/audit_dashboard`（collect_reports/release_gate，T2/T3 run-dir 布局，ledger 原子写）。
3. **RED？** glob tests/**/*ca205* → 零命中；无"dashboard 同 schema + 故障矩阵 + 恢复幂等 + 完整字段"一体验收。
4. **允许改哪些文件？** revenue：新 `tests/test_ca205_atomic_report.py`；receipts/CA-205/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实报告目录写（tmp 隔离）、下载、LLM。
5. **下一单元解锁？** CA-206（不可豁免自然时间 soak）→ 阶段 J（CA-301~306）。本卡不做：真实调度注册、自然时间累积（CA-206）。

## Acceptance criteria

- **C1 原子 publish + 完整字段 + 同 schema**：pending → validate（triplet/sample/command/hash 完整）→ fsync+replace 原子 publish 无 residue；dashboard（collect_reports T2 run-dir）与 release_gate（validate_report）消费同一 published schema；freshness gate 读取同一报告。
- **C2 故障矩阵全红**：corrupt JSON/tampered hash/wrong triplet/missing field/future/stale/ledger hash mismatch/SLI regression/empty SLI/no report——每类 release 红。
- **C3 恢复幂等**：失败 pending 保留原位；修复后同一 pending 干净 publish（无重复无 residue）；第三次运行 no-op。
- **C4 alert ack/retry**：unacked alerts 保持 pending；ack 精确标记该 run；alert sink 失败是响亮失败（OSError 不静默）。
- **C5 无 stale-green 复活**：future timestamp 与 renamed old-green（hash 链断）拒绝；freshness 按年龄强制。
- **C6 质量门（卡级）**：相邻回归（ZR-904）零回退、revenue 全量零回归（基线 953+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 全 tmp 隔离；零生产写入、零网络、零 LLM；不注册真实调度。
