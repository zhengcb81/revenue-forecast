# ZR-507 工作单元卡（preflight）— ProcessingDemand API（enqueue/dedupe/claim/heartbeat/retry/complete）

- 领取时间：2026-08-19T20:22Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-507`，ZR-506 accepted + closure→ZR-507；锁 ZR-507（owner=zr507-implementer）。
- 依赖：ZR-501~506（✅）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第七卡：**ProcessingDemand API**（authoritative_execution_plan：`ProcessingDemand` enqueue/dedupe/claim/heartbeat/retry/complete 与公平调度）。codegraph_freeze 已注册 `ProcessingDemand` 为 wiki「required but expected missing」符号（CA-003 findings：wiki 中未发现独立类）——本卡实现独立 ProcessingDemand 队列 API；scheduler 公平性（deadline/cost budget）为 ZR-508。消费者（filing-fetch 下载、LLM 处理）将用它提交处理需求。
2. **production entrypoint 是什么？** 新 `src/company_wiki/source_catalog/processing_demand.py`：`ProcessingDemand` dataclass + `DemandQueue`（enqueue/dedupe/claim/heartbeat/retry/complete/expire）——纯内存纯函数库（无 DB/IO），为 ZR-508 scheduler 提供确定性的 demand 语义基元。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 ProcessingDemand 不存在**：wiki 无 ProcessingDemand 类/队列（grep 0 命中；codegraph_freeze 期望缺失注册）。
   - **G2 无去重/租约语义**：无 enqueue 按 key 去重、claim 租约 + heartbeat 续租、超时回收、retry 退避。
   - **G3 无 consumer-priority 隔离**：consumer 提交的 priority 不得覆盖全局队列序（防插队）。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/processing_demand.py` + 新测试 `tests/contract/test_zr507_processing_demand.py`；revenue receipts/ZR-507/** + codegraph_freeze 期望缺失更新（ProcessingDemand 实现后从 expected-missing 移至 present，属于本卡 closure 范围）。禁止：真实 catalog 写、下载、LLM、改 admission/schema、DB/IO（本卡纯内存）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-508（scheduler 公平性/deadline/cost budget）。本卡不做：scheduler 调度循环（ZR-508）、HTML capture（ZR-509）、完整 attribution（ZR-510）、持久化存储（后续卡）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-506 accepted（closure.next=ZR-507）。
- [x] triplet 冻结：revenue（ZR-506 closure 提交后）、wiki `cbc6d8c…`、filing `5a1c18f…`。
- [x] 现状事实：wiki 无 ProcessingDemand（grep 0 命中）；codegraph_freeze wiki 目标含 "ProcessingDemand"（required but expected missing，registered）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（processing_demand.py + 测试）+ revenue（receipt + codegraph_freeze 更新）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 ProcessingDemand 模型（杀 G1）**：`ProcessingDemand` dataclass（demand_id/key/kind/priority/status/attempts/lease_owner/lease_until/retry_at/created_at/updated_at）+ `DemandQueue` API：enqueue（按 key 去重——重复 key 返回既有 demand 不新增）、claim（就绪 demand 按 priority desc + created asc 序出队 + 租约）、heartbeat（续租）、complete（终态）、fail/retry（attempts+1 + 指数退避 retry_at）、expire（租约超时回收回就绪）。
  - **C2 生命周期闭环（杀 G2）**：enqueue→claim→complete 全链；claim 后未 heartbeat → 超时回收可再 claim；fail 后 retry_at 未到不可 claim、到后可 claim；attempts 上限后永久失败（terminal）。
  - **C3 consumer-priority 隔离（杀 G3）**：低优先级 demand 先入队、高优先级后入队 → claim 仍按 priority 先出队；consumer 无法在 enqueue 后修改全局序（priority 不可变）；同 priority 按 FIFO。
  - **C4 确定性**：同操作序列两次运行结果一致（纯内存无随机）；clock 注入（now 参数）保证 heartbeat/超时/退避可测。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超（新文件 max≤10）；独立 reviewer 复放；codegraph_freeze 期望缺失更新后 codegraph-verify 通过。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、DB/IO → 立即停止。

## Annex：ProcessingDemand 语义矩阵

| 操作 | 语义 |
|---|---|
| enqueue(key, kind, priority) | 新 demand；key 已存在 → 返回既有（dedupe） |
| claim() | 就绪（无租约/租约过期）中 priority desc + created asc 首个；设租约（lease_until=now+ttl） |
| heartbeat(now) | 租约内续租；无租约/过期 → 拒绝 |
| complete(id) | 仅租约持有者可终态完成 |
| fail(id) | attempts+1；退避 retry_at=now+backoff^attempts；超上限 → terminal_failed |
| expire(now) | 租约超时 → 回就绪（可再 claim） |
| priority 不变性 | enqueue 后不可改（consumer 不能插队） |
