# RED.md — ZR-1006 broker processing demand 最小 cohort（阶段 I 第六卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1006 验收套件**：glob `tests/**/*zr1006*` → 零命中。
- **G2 无 broker cohort 组合验收**：test_zr507_processing_demand.py / test_zr508_scheduler.py 无 broker/1→3→7/质量门/失败隔离组合断言（grep cohort/最小 → 零命中）；ZR-507 仅队列生命周期、ZR-508 仅公平调度（aging/deadline/cost），均未与"七份紫金 broker 最小 cohort"绑定。
- **G3 生产现状（只读确认）**：golden corpus 7 份 broker 样本在 production catalog 全部 `broker_research` + `active` + artifact_count=0（probe：documents=6521 broker_research、artifacts=7962、summary=2963；七份样本零 artifact 逐一确认）；2026-08-12 审计同结论（零 artifact/span/tag）。

## 既有能力（不重复建设）

- ZR-507 `processing_demand.py`（DemandQueue：enqueue dedupe/claim 优先级/lease/heartbeat/complete/fail 退避/expire/attempt cap）；ZR-508 `scheduler.py`（DemandScheduler：aging/deadline urgency/cost budget）；ZR-501~506 broker 契约测试；ZR-1005 artifact_backfill + temp catalog seed 模式；golden_corpus.json 7 份紫金 broker 样本（frozen sha256）。

## 结论

G1~G3 为真实缺口（`still_missing`）；实施 = company-wiki `tests/contract/test_zr1006_broker_cohort.py`（9 tests：C1 生产只读快照 + C2 ramp 1→3→7 + C3 质量门 + C4 成本/SLO + C5 失败隔离），产品零改动。
