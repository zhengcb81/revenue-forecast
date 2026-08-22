# RED.md — ZR-904 SLI/dashboard/release gate（阶段 H 第三卡）

## 探针（全部在当前机器实跑）

- **G1 无统一 SLI/原子发布**：grep release_gate/sli/dashboard/ack → 零命中；assurance/runs 报告（fc1302 等）无自身 hash、无 pending→publish 原子流程（进程中断半报告无防护）。
- **G2 无报告完整性校验**：既有 report.json 无 canonical 自 hash；无 triplet/sample/command 完整性断言。
- **G3 无告警 ack/重试**：ZR-902/903 的 daily/weekly_alert.jsonl 为 append-only，无 ack 状态、无重试；sink 失败无显式失败。
- **G4 无过期不可续命门**：无 future timestamp 拒绝、无旧报告复制（旧绿续命）检测；无 business SLI（AUD2-06）阻断语义。

## 既有能力（不重复建设）

- ZR-710 的 `_atomic_write_text`（tmp+fsync+os.replace）在产品侧已有成熟模式；ZR-902/903 台账/告警 journal/freshness 机制为本卡输入。
- `daily_t2_runner.py` 已有部分检查（triplet/samples/roots fingerprint）——本卡聚合为 SLI 并加发布/完整性/ack 语义。

## 结论

G1~G4 全部为真实缺口（`still_missing`）；实施 = `tools/release_gate.py`（原子发布 + 完整性 + SLI 汇总 + 告警 ack/重试 + 过期拒绝 + release 判定）+ 测试钉死，产品零改动。
