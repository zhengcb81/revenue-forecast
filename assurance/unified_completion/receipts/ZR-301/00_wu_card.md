# ZR-301 工作单元卡（preflight）— additive source-lifecycle assertion schema + readiness evaluator

- 领取时间：2026-08-17T19:20Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-301`；units.ZR-206.status=accepted + closure.next=ZR-301；`uc next` 解锁列表含 ZR-301；阶段 D 首卡。
- 依赖：ZR-203（accepted ✅）。Registry 依赖列=ZR-203。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 来源状态机。现状：`documents.source_status` 单一字段（active/incomplete/quarantined/retired/upstream_rejected）掩盖不同缺口；phase 3 task_plan 要求"以追加 assertion 表达 identity、capture、safety、freshness、artifact、semantic readiness，不再用单一 active 掩盖不同缺口"。ZR-301 建立**shadow-only** 的逐源八阶段 readiness 求值器：identity/resolution/freshness/acquisition/safety/artifact/semantic/consumer 可组合；不覆盖历史；consumer requirements 决定 ready。
2. **production entrypoint 是什么？** 本卡**只读 shadow 求值**：输入为 reader（`ReadOnlyCatalogReader`）+ 既有 catalog 证据（assertions/locations/artifacts/evidence_spans/scan_runs）；输出为 `SourceReadiness` 结构（每阶段 satisfied/unsatisfied/unknown + blocker + next action）。**不写 catalog、不接生产 CLI、不改 source_status 语义**（后续卡 ZR-303 统一决策图再接线）。
3. **哪个 current-triplet 行为是 RED？** 单一 `active` 无法表达"identity 已验但 safety 未审"等组合缺口；没有按 consumer requirements 计算 ready 的求值器；八阶段 taxonomy（ZR-101）没有 per-source 求值消费点。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/source_lifecycle.py`（新模块，复杂度≤10）+ `tests/unit/test_source_lifecycle.py` + `tests/contract/test_zr301_readiness.py`；revenue 侧 receipts/ZR-301/** 与 state.json。禁止：写 catalog、改 source_status 语义、接生产入口、改 reader/锁/schema、真实 catalog 写。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-302（prompt-injection receipt 生成/缓存/失效）与 ZR-303（统一 machine decision graph 接线）。本卡不把求值结果写入生产（shadow only）；不实现 safety receipt 本身（ZR-302）；不做 artifact validator 归一（ZR-304）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-206 accepted（机器状态；closure.next=ZR-301；阶段 D）。
- [x] triplet 冻结（领取时重读）：revenue `3d0d097…`（closure 后）、filing `0e5d209…`、wiki `3ea0039…`。
- [x] 现状代码事实：observability.py 已有 `CrossRepoStage` 八阶段 + `STAGES_BY_REASON`（78 codes）+ `validate_stage_event`（fail closed）；`source_metadata_assertions` 表（decision/evidence_basis/content_sha256/visibility_state）；`documents.source_status` 单一字段；无 readiness 求值器。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品新模块）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——无 per-source readiness 求值器。
- **Acceptance criteria**：
  - `LIFECYCLE_SCHEMA`/`LIFECYCLE_SCHEMA_VERSION`：版本化 assertion schema（stage/reason/evidence_basis/status），未知 stage/reason fail closed（复用 STAGES_BY_REASON）。
  - `ConsumerRequirements`：required_stages 校验（未知 stage 拒绝）；empty requirements = 不要求任何阶段（ready=True）。
  - `evaluate_source_readiness(reader, source_id, requirements)`：对八阶段逐项求值（identity=verified assertion 存在；resolution=exact/latest 命中；freshness=as_of/period 满足；acquisition=active location 存在；safety=prompt review 非 not_reviewed（无 receipt 数据则 unknown，绝不伪绿）；artifact=有效 artifact 存在；semantic=无 semantic blocker；consumer=source_status 非 blocked），输出每阶段 verdict + blocker + next action；ready = 所有 required stage satisfied（unknown 不算 satisfied——fail closed）。
  - shadow only：函数零写（仅 reader 查询）；单元测试断言无 execute/commit/DDL。
  - hermetic 测试：八阶段各自 satisfied/unsatisfied/unknown 矩阵、requirements 校验、unknown 不伪绿、非锁错 fail closed、shadow 零写断言、复杂度≤10。
  - wiki unit/contract 全绿；独立 reviewer 复放。
- **Stop conditions / handoff**：写 catalog、改 source_status、接生产入口、改 reader → 立即停止。

## Annex：八阶段求值信号（shadow，来自既有证据）

| 阶段 | satisfied 信号 | unknown 条件 |
|---|---|---|
| identity | source 有 decision='verified' assertion | 无 assertion 行 |
| resolution | 有 exact_hit/latest_selected 类 reason 事件或唯一 handle | 无事件记录 |
| freshness | 存在满足 as_of/period 的 active location/assertion | 无 period 数据 |
| acquisition | active location 存在（字节在位） | 无 location |
| safety | prompt review receipt 非 not_reviewed | 无 review 记录（绝不伪绿） |
| artifact | 至少一个有效 artifact（校验通过） | 无 artifact 记录 |
| semantic | 无 semantic blocker reason | 无 semantic 事件 |
| consumer | source_status 不在 blocked 集合 | —（source_status 恒有值） |
