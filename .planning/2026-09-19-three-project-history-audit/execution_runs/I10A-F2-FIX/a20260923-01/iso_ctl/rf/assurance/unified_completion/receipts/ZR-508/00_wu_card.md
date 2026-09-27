# ZR-508 工作单元卡（preflight）— scheduler 公平性（aging/deadline/cost budget）

- 领取时间：2026-08-19T20:29Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-508`，ZR-507 accepted + closure→ZR-508；锁 ZR-508（owner=zr508-implementer）。
- 依赖：ZR-507（✅，ProcessingDemand API）。Registry 依赖列=ZR-507。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第八卡：**scheduler 公平性（deadline/cost budget）**（authoritative_execution_plan：ProcessingDemand 与公平调度）。ZR-507 交付 demand 队列基元；本卡交付**调度决策层**：高优先级不饿死低优先级（aging）、deadline 逼近紧急调度、kind 级 cost budget 限流——消费者（filing-fetch 下载、LLM 处理）按调度器决策执行。
2. **production entrypoint 是什么？** 新 `src/company_wiki/source_catalog/scheduler.py`：`DemandScheduler`（包装 DemandQueue）——`schedule_once(now)` 返回本次应执行的 demand（或 None）；aging/deadline/budget 均为调度器侧全局策略，不修改 demand 原始 priority（ZR-507 C3 保持）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 无调度器**：wiki 无 scheduler（grep 0 命中）；DemandQueue 裸 claim 是严格 priority 序——低优先级在持续高优先级流下饿死。
   - **G2 无 deadline 语义**：无 deadline 逼近紧急调度。
   - **G3 无 cost budget**：无 kind 级预算限流。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/scheduler.py` + 新测试 `tests/contract/test_zr508_scheduler.py`；revenue receipts/ZR-508/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema、DB/IO（纯内存）、修改 ZR-507 ProcessingDemand 契约（priority 不可变等）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-509（官方公告/新闻/HTML capture）。本卡不做：HTML capture（ZR-509）、完整 attribution（ZR-510）、持久化调度状态（后续卡）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-507 accepted（closure.next=ZR-508）。
- [x] triplet 冻结：revenue（ZR-507 closure 提交后）、wiki `bd337c4…`、filing `5a1c18f…`。
- [x] 现状事实：wiki 无 scheduler（grep 0）；DemandQueue claim 严格 priority desc + created asc（ZR-507，本卡保持其契约）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（scheduler.py + 测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 aging 公平性（杀 G1）**：`DemandScheduler.schedule_once(now)` 用 `effective_priority = priority + aging_bonus(wait_seconds)`（等待越久 bonus 越高，aging 窗口可配）→ 低优先级 demand 等待足够久后必然被调度（不饿死）；高优先级仍先于等同样久的低优先级；原始 priority 不可变（ZR-507 契约保持）。
  - **C2 deadline 紧急（杀 G2）**：enqueue 时带 deadline → deadline 逼近（< urgency_window）的 demand effective_priority 提升（紧急加成）；已过 deadline 的 demand 仍可被调度但打 `deadline_expired` 标记（诚实，不丢弃）。
  - **C3 cost budget（杀 G3）**：`set_budget(kind, limit)` + `spend(kind, cost)`；kind 累计消费 ≥ limit → 该 kind 暂停出队（schedule_once 返回 None 或其它 kind）；budget 重置后恢复。
  - **C4 确定性 + 契约保持**：同操作序列两次运行结果一致（clock 注入）；ProcessingDemand 契约零改动（ZR-507 测试全绿）；schedule_once 返回的 demand 必须经 claim 语义（租约）。
  - 质量门：wiki unit 787 + 受影响 contract 无回归（含 ZR-507 14）；ruff clean；复杂度 ratchet 不超（新文件 max≤10）；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、DB/IO、改 ZR-507 契约 → 立即停止。

## Annex：调度语义矩阵

| 场景 | 期望 |
|---|---|
| 高 prio 持续流入 + 低 prio 等待 | aging bonus 使低 prio 等待 ≥ window 后被调度（不饿死） |
| 同等待时长 | 高 prio 先 |
| deadline 逼近（< urgency_window） | effective_priority 紧急加成 |
| deadline 已过 | 仍可调度 + deadline_expired 标记 |
| kind budget 耗尽 | 该 kind 不出队；重置后恢复 |
| 无就绪 demand | schedule_once → None |
| 返回 demand | 必须已 claim（running + 租约） |
