# 三仓库统一完成保障计划清单

> 生成日期：2026-08-13  
> 计划状态：编制与自审完成；产品实施全部未开始。  
> 并发所有权：本目录持有详细计划；根README持有唯一控制面；其余五个日期目录和三仓产品只读。  
> **入口覆盖：本文件现在只是详细附录的完整性清单。唯一执行入口和`current_next`位于根 [audit_review/README.md](../README.md)。**  
> 本清单不记录自身hash，避免自引用；下列14个内容文件在更新manifest版本前不得静默改变。

## 1. 结论摘要

- 旧 `2026-08-09_full_completion_assurance_plan` 不能以complete关闭：机器账本66/71、FC-1501～1505 pending，R9强门4/4 RED。
- 严格current-triplet口径：71项中31项有未独立复验实现、26项被当前行为反证、9项证据陈旧、5项pending，0项可直接继承为current complete。
- 三仓保留了大量基础资产，但真只读、RootPolicy全请求一致、Dropbox/dayu consumer、revision下载、artifact lineage、ProcessingDemand、broker语义、revenue合同/发布、逐矿会计桥、真实E2E和动态调度均未完整闭环。
- 本计划面向所有公司；紫金是复杂canary，另强制第二异构矿企和非矿企。
- 旧计划只有在新计划全部验收后才能由旧owner标`closed_superseded_incomplete`；历史证据不改写。

## 2. 观察到的三仓截面

这些是审计观察值，不是未来实施基线。第一张实施卡必须CA-001/CA-002/ZR-001重新冻结。

| 仓库 | HEAD | branch | upstream | dirty entries |
|---|---|---|---|---:|
| revenue-forecast | `c3a0519303d78dfe283bea6247da53163b926dc8` | `fcap` | 未设置 | 4 |
| filing-fetch | `83c638e76e40890262746cdf02b6df495dcb4031` | `fcap` | 未设置 | 0 |
| company-wiki | `ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875` | `fcap` | 未设置 | 4 |

CodeGraph可查询，但filing/company索引新鲜度不足以证明匹配这些HEAD；本轮为避免与并发程序争锁没有重建，CA-003要求独占重建并记录indexed commit。

## 3. 内容文件hash

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `authoritative_execution_plan.md` | 13,386 | `2a18294bad809978f6fc60a573764fdb8cfc91c5ea0c8ec4bc141fe3a6e8f6c9` |
| `completion_assurance_registry.md` | 14,931 | `861e28f9dc72864347041ef1a8b0deabf38afdb3581ffce5050cb794f361f3e7` |
| `completion_audit.md` | 9,916 | `90cd878206c548693ad176b1427064e8689169b7bb2eae0d492f06f3f24012fe` |
| `current_state_audit.md` | 10,068 | `fc7552617f80ff13565db79ea6cca2413009b205a8b066be3b80ffef7a1a77d9` |
| `findings.md` | 19,499 | `af6d64bc97f47daff8b2e02dfe608cf8fd9eb36b104a26a82ef6971fa45b6ae5` |
| `input_snapshot.md` | 5,154 | `18ce4be32fbab9c689469a70938277c3190eefcc699585b6157d9fb90a0d60cc` |
| `legacy_fc_status_registry.md` | 5,649 | `fa38c1e727ca6982fc911688a4db87bacfcfa65389ed1f949c1a6f77946ddc44` |
| `legacy_transition_matrix.md` | 8,805 | `cfd0de189c801564c65e8361106b8f915873593c2d1fa00e95ced163836cc34e` |
| `plan_self_audit.md` | 7,202 | `cfa336073a9a1c424e0e819f7a38a2abc5d4299e0b363fc033b0ade86a6907ad` |
| `progress.md` | 6,759 | `4ec709564e94b4f3d7e18d69660ab04bd1ca95c37f0758a5f40b4b549d4e72a7` |
| `project_goal_and_pain_points.md` | 12,015 | `055181150156719e7dfe7b68989af4f96d2081853f247ed64d9495a99859061b` |
| `task_plan.md` | 8,997 | `4466c40594b253aaed7571ee777ce72c86e8f3b672b01751572175f254d99bb0` |
| `traceability_and_acceptance.md` | 10,423 | `2be87284fda7ab326c27618367319dccb7bf79e30e26b76d95594ca7b8275bb6` |
| `weak_model_execution_checklist.md` | 8,144 | `099b6db13843314a8bb03490ed52e9b64771f8561e8547cd58b817c9258e0c8d` |

## 4. 冻结annex

| 内容 | 文件hash | 数量/用途 |
|---|---|---|
| 目标架构 | `288995a9b9e4c2f6848fd28d35d6fc9297248f5fc674f18a61dc2ac79de34f6b` | 三仓职责、Reader、RootPolicy、生命周期、broker、矿业合同 |
| ZR工作单元 | `72c70eb6df9bf9cd04e8a9e42ad795477da9c28f30db291d7b8d1dda3d5de709` | 92个，全部pending |
| 新场景矩阵 | `e08cbe4e93b933bd01bc758dcef5aeee194417bde0d23d05ea0bc011e03cac8a` | 102个 |
| 弱模型20步手册 | `b20a8b886261118a0b1449809f63db8de4f57f6099061115c9af8761c95ba132` | 每个ZR/CA强制执行 |
| 旧场景矩阵 | `21e9201296aa048bd61e1125525a0eadb8ac1deb5bed76a641f05b3099f1d3c5` | 95个继续mandatory |

新计划另有25个CA工作单元。总计117个原子单元，197个唯一业务场景；场景的required tier会展开为更多machine results，不能按197个ID出现次数计pass。

## 5. 机器自审结果

- CA：25定义、25唯一、0未定义精确引用、0自依赖。
- ZR：92定义、92唯一、0未定义精确引用。
- 场景：旧95唯一、新102唯一、合计197、交集0；冻结hash全部匹配。
- 旧计划：71 FC、R0～R9、FC-1501～1505全部有successor。
- 文件：14个内容文件非空，无tmp/lock/bak；manifest生成前git仅显示本新目录untracked。
- 状态：本轮计划Phase A～F完成；未来产品Phase A～J全部pending，唯一首卡CA-001。
- 产品改动：0；配置、数据库、索引、测试、CI、六个日期目录改动：0。根历史三文件仅增加归档路由。

## 6. 附录完整性与实施领取规则

1. 重算本表14个内容文件和5个annex hash；不符先CA-001审查plan drift。
2. 领取前先读根`audit_review/README.md`；不得从某个看似简单的ZR或旧R9/FC-150x开始。当前首卡必须CA-001，然后由machine DAG决定下一卡。
3. 先让Closure 2.0能诚实判旧计划不完整，再实现产品功能；不能先追求全绿。
4. 每个已有资产先跑current production RED/mutation；已满足走already-satisfied，禁止无谓重写。
5. required real tier缺样本/权限/网络只能blocked；blocked不算pass。
6. 生产migration/cohort/R9必须等相应phase、明确授权、before/rollback和独立review。
7. 自然时间门（7 Daily、2 Weekly、1 Monthly、1 alert drill、两个legacy zero-hit周期）不可豁免。
8. 六个最终问题逐项machine pass后，才允许CA-306关闭旧计划入口。

## 7. 审计/复核完整阅读顺序（不是任务领取顺序）

1. `project_goal_and_pain_points.md`
2. `current_state_audit.md`
3. `completion_audit.md`
4. `legacy_transition_matrix.md`
5. `legacy_fc_status_registry.md`
6. `authoritative_execution_plan.md`
7. `completion_assurance_registry.md`
8. `traceability_and_acceptance.md`
9. `weak_model_execution_checklist.md`
10. 冻结ZR registry、scenario matrix和implementation runbook
11. `plan_self_audit.md`

该顺序先解释“为什么”，再告诉实施者“当前哪里坏、旧任务怎么迁、按什么顺序做、每一步怎样证明”，避免弱模型陷入局部代码而失去全局目标。
