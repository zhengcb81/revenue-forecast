# ZR-306 工作单元卡（preflight）— SourceBundle role DAG 与最小失效

- 领取时间：2026-08-17T22:40Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-306`；units.ZR-305.status=accepted + closure.next=ZR-306；`uc next` 解锁列表含 ZR-306。
- 依赖：ZR-304（accepted ✅）。Registry 依赖列=ZR-304。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 最小失效。`artifact_dag.py`（WU-803）已有 ROLE_DEPENDENCIES（normalized→markdown→summary→consumer_analysis；sections→normalized）+ `invalidate`（document_hash 全失效；producer-key 变更按下游闭包）+ `select_artifacts`（确定性选择）。registry 要求：**只重算缺失/依赖子树**；**source bytes/producer/model/prompt 变更的失效范围有 property tests**。本卡补齐 property-test 证据并核对 DAG 与生产 bundle 消费一致。
2. **production entrypoint 是什么？** 本卡测试/验收侧：`tests/contract/test_zr306_role_dag.py`（property tests，复用 artifact_dag + source_bundle）；不改产品代码（WU-803 DAG 已实现）。
3. **哪个 current-triplet 行为是 RED？** 无 property tests 证明失效范围正确性（文档哈希全失效、单 role producer-key 变更只失效其下游闭包、缺失依赖子树重算）；无"DAG 失效集 == 生产 bundle 需重算集"的对照。
4. **允许改哪些文件？** company-wiki 新增 `tests/contract/test_zr306_role_dag.py`（如产品缺口则最小改 artifact_dag.py）；revenue 侧 receipts/ZR-306/** 与 state.json。禁止：真实 catalog 写、下载、接生产入口。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-307（filing 分阶段 envelope）与 ZR-507（ProcessingDemand）。本卡不实现 ProcessingDemand（ZR-507）；不接生产入口。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-305 accepted（机器状态；closure.next=ZR-306）。
- [x] triplet 冻结（领取时重读）：revenue（ZR-305 closure commit 后）、filing `0e5d209…`、wiki `080d20c…`。
- [x] 现状代码事实：artifact_dag.py ROLE_DEPENDENCIES（5 role）+ PRODUCER_KEYS（producer_name/version/schema_version/prompt_hash/model_hash/config_hash）+ invalidate（document_hash→全失效；否则下游闭包）+ select_artifacts；source_bundle.build_source_bundle 消费 artifacts（KNOWN_ARTIFACT_ROLES=ROLE_DEPENDENCIES）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（测试/验收）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——无失效范围 property tests。
- **Acceptance criteria**：
  - property tests（假随机/穷举小域）：
    - 文档哈希变更 → 全部 role 失效（全量重算）；
    - 某 role 的 producer-key 变更 → 失效集 == 该 role 的传递下游闭包（含自身），上游不受影响；
    - 缺失依赖子树 → 只重算缺失/依赖子树（不重算已满足的独立分支）；
    - 失效集幂等（同输入同输出）；
    - DAG 无环（拓扑可达性验证）。
  - 对照：`invalidate` 失效集 == 按 ROLE_DEPENDENCIES 手工下游闭包（property 断言）。
  - hermetic 测试全绿；wiki unit/contract 无回归；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、接生产入口 → 立即停止。

## Annex：失效范围矩阵（property 域）

| 变更 | 预期失效集 |
|---|---|
| document_hash | 全部 role |
| normalized 的 producer-key | normalized, markdown, summary, sections, consumer_analysis（全下游） |
| sections 的 producer-key | sections |
| summary 的 producer-key | summary, consumer_analysis |
| consumer_analysis 的 producer-key | consumer_analysis |
| 无变更 | 空集（幂等） |
