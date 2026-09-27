# 三仓历史计划最新状态与处置总账

> Status snapshot：2026-08-09；current triplet：revenue `3ce9cc4d3ea91b15aad42eff1f55b72a44834dd7`、filing `c9799b722a97376f9717bcfacfa0685135dcbd15`、wiki `109a1a6a77d7f4b37f849207fbd9e5d8caf2bc07`。
>
> 当前唯一负责“重构完全成功、Dropbox 功能闭环、全部目标、动态审核、真实 E2E、全面质量提升”六项目标的计划是 `FCAP-2026-08-09-r2`。旧计划不得再作为独立执行入口。

## 1. 状态词典

| 状态 | 含义 | 是否进入当前执行队列 |
|---|---|---|
| `current_plan` | 当前唯一主计划 | 是，按 FC registry |
| `completed_historical_scope` | 当时明确范围有交付/证据；不证明当前六目标 | 否，维护回归即可 |
| `completed_audit_only` | 审查、调查或计划编制工作完成；产品未因此完成 | 否 |
| `partially_completed` | 部分交付有证据，其他项目未完成或已漂移 | 仅通过 crosswalk 转入 r2 |
| `superseded` | 目标仍需要，但由 r2 更严格的 FC 取代 | 否，禁止继续旧编号 |
| `cancelled` | 与当前架构边界冲突、已被替代或不再需要 | 否 |
| `deprioritized` | 仍可能有价值，但不阻塞六目标；满足触发条件再立项 | 否 |
| `archived_reference` | 历史、恢复草稿、工具私有草稿或归档文件 | 否 |
| `blocked` | 仍属当前目标但缺外部条件 | 是，只能留在 r2 FC 中 |

## 2. Revenue-forecast 计划清单

| 文件 | 最新状态 | 已完成/保留 | 未完成项目处置 | 当前入口 |
|---|---|---|---|---|
| `task_plan.md` | `completed_historical_scope + superseded_open_items` | 已勾的历史 revenue phases 与审查记录保留 | Phase 18 identity/supersedes/metadata → FC-401/402/702；Phase 19 filing CLI/诊断/错误/文档 → FC-704/802/1205；与 data-lake 无关的研究体验 backlog 降为 P3 | r2 registry |
| `IMPLEMENTATION_PLAN.md` | `completed_historical_scope + superseded` | R0–R9 当时实现与提交保留 | “当前充分完成”声明失效；动态审核、真实复用和泛化转 FC-101~1505 | r2 |
| `review_audit/task_plan.md` | `completed_audit_only` | Phase 1–5 审查全部完成 | “用户裁定后开始实施”取消：后续实施已发生且新剩余工作转 r2 | 无 |
| `review_audit/roadmap.md` | `superseded` | 根因分析与历史设计保留 | 顶部“待批准未实施”已过期；R1–R9 不再独立排队 | r2 |
| `audit_review/task_plan.md` | `completed_audit_only + superseded_execution_plan` | Phase 1–5 审查和计划输出完成 | 旧 Phase 6 实施建议转 r2，对应项不再独立 pending | r2 |
| `audit_review/2026-08-08_adversarial_plan/task_plan.md` | `completed_audit_only + superseded` | 审查、Dropbox 架构调查和计划编制清单完成 | 产品 Phase 0–10 全部由 r2 收紧取代；旧 config-only Dropbox 判断已失效 | r2 |
| `audit_review/2026-08-09_data_lake_refactor_plan/task_plan.md` | `partially_completed_evidence + superseded` | ADR、工具、部分 WU/receipt 作为历史输入保留 | 全部未验收 WU 转入 r2；旧 WU 状态机、72/84 场景和 receipt schema 停用 | r2 |
| `audit_review/2026-08-09_data_lake_refactor_plan/implementation_runbook.md` | `superseded` | 旧卡片仅供需求/失败史参考 | 禁止继续用 WU-* 签发新 receipt | r2 runbook/FC packet |
| `audit_review/2026-08-09_full_completion_assurance_plan/task_plan.md` | `current_plan` | Phase 0 计划基线完成 | Phase 1–15/FC-101~1505 仍 pending | 本文件族 |

## 3. Filing-fetch 计划清单

| 文件 | 最新状态 | 已完成/保留 | 未完成项目处置 | 当前入口 |
|---|---|---|---|---|
| `task_plan.md` | `completed_historical_scope` | v1.3.0 的契约、mock、isolated E2E、opt-in download、live consistency、文档/coverage 均按旧范围完成 | latest 一次闭环、统一 resolver、Dropbox、多根策略、current triplet CI、动态 T3 等是新标准，不回滚旧勾选，转 FC-701/801~805/903/1001~1105/1202 | r2 |

## 4. Company-wiki 当前与历史计划清单

| 文件 | 最新状态 | 已完成/保留 | 未完成项目处置 | 当前入口 |
|---|---|---|---|---|
| `task_plan.md` | `completed_historical_scope + superseded_for_six_goals` | 272 个已勾历史任务、CW-2.24~2.31 等 scoped delivery 保留 | 当前 data-lake/Dropbox/工件/动态审核缺口全部转 r2；根文件不再新增同类任务 | r2 |
| `task_plan_v2.md` | `cancelled/superseded_by_BOUNDARY-0` | 历史架构分析保留 | 22 个未勾项全部取消为活动待办；投资研究范围不再恢复 | 无 |
| `review_plan.md` | `completed_audit_template + cancelled_open_items` | 审查维度可作参考 | 18 个未勾检查项不再单独执行；适用部分被 FC-1201~1304/1502 吸收 | r2 |
| `task_plan_cw_recovery_20260725.md` | `archived_reference` | 已恢复文本和历史证据保留 | 19 个未勾“恢复/旧范围”不作为产品待办；必要证据由 r2 重新核验 | 无 |
| `verification_CW-2.24_plan.md` | `completed_audit_only` | R1/R2.1/R2.2/R2.3 复核结论完成 | index.md duplicate 可视化降 P3；semantic near-duplicate 维持独立 backlog，不阻塞 r2 | 无/r2 去重相关场景 |
| `docs/plans/core-section-extraction/task_plan.md` | `completed_historical_scope` | 13/13 勾选、Phase 1–5 完成 | 后续优化降 maintenance；artifact binding 是否可复用由 FC-901~906 重新验证 | 维护/r2 artifact |
| `docs/plans/portfolio-reuse-fix/task_plan.md` | `superseded_closed` | Strategy A Phase 0–6 的历史实现/实验保留 | 35 个未勾描述不再是活动清单；Phase 7 被 Strategy B 和 r2 取代 | 无 |
| `docs/plans/portfolio-reuse-automatic/task_plan.md` | `completed_historical_scope + superseded_for_generalization` | Strategy B 的 dayu config-driven 窄范围完成 | Strategy A 的 38 个空框全部 `cancelled_by_Strategy_B`；未来 root/Dropbox/production generic path 转 FC-301~705 | r2 |
| `docs/plans/catalog-space-remediation/task_plan.md` | `completed_historical_scope_with_transferred_monitoring` | Phase 1–4 与 Phase 6 的已落地治理/提案/文档保留 | Phase 5 存储迁移 `cancelled_by_D4`；持续健康/SLO 转 FC-1302~1304/1504；旧 42 个空框不再整体代表 pending | r2；未来若触发容量阈值则重新立项 |

## 5. 明确归档/恢复/工具草稿

以下文件统一为 `archived_reference`；其中所有未勾项均不进入当前 backlog，也不需要逐项实施：

- company-wiki `.mimocode/plans/1784577918407-neon-planet.md`；
- company-wiki `.recover-task_plan-before-cw-merge-20260725-115819.md`；
- company-wiki `.recover-task_plan-current-20260725-114504.md`；
- company-wiki `docs/archive/GAP_FIX_PLAN.md`；
- company-wiki `docs/archive/IMPROVEMENT_PLAN.md`；
- company-wiki `docs/archive/KARPATHY_GAPS_PLAN.md`；
- company-wiki `docs/archive/LLM_INTEGRATION_PLAN.md`；
- company-wiki `docs/archive/PLAN.md`；
- company-wiki `docs/archive/REFACTORING_PLAN.md`。

不改写归档正文，以免破坏历史证据；本总账是它们的当前状态覆盖层。

## 6. 旧工作到 r2 的强制 Crosswalk

| 旧主题/条目 | 旧状态处置 | r2 接收位置 | 优先级 |
|---|---|---|---|
| Dropbox config-only / sidecar | 旧方案部分失效并 superseded | FC-301~305、501~505、701 | P0 |
| company/dayu/Dropbox 多根复用 | superseded | FC-601~705 | P0 |
| runtime flags/activation/rollback | 旧 receipt 不充分 | FC-201~205 | P0 |
| v2 assertion/catalog migration | partial evidence | FC-401~405 | P0 |
| identity、多 ticker、多市场 | root Phase 18 superseded | FC-402、702 | P0 |
| exact/latest/gap/download | superseded | FC-801~805 | P0 |
| SourceBundle/artifact selector | test-only evidence superseded | FC-901~906 | P0 |
| 三仓真实 E2E | 旧 72/84 场景 superseded | FC-1001~1005、95 scenarios | P0 |
| 动态审核/current triplet | 旧 R6/R7 部分完成 | FC-101~104、1101~1105 | P0 |
| hardcode/重复策略/死 helper | 旧 cleanup 不充分 | FC-1201~1205 | P1（Phase 14 前必完） |
| scan health/catalog SLO/capacity | 旧 catalog plan 部分完成 | FC-1301~1304 | P1（Phase 14 前必完） |
| legacy disable/delete | 未满足 caller=0 | FC-705、Phase 14 R8/R9、FC-1502 | P1 |
| 人类 `index.md` 重复可视化 | 不影响核心复用 | 独立 backlog | P3 |
| semantic/near duplicate | 不等同 exact filing reuse | 独立受控提案；必要时新增 scenario/FC | P2/P3 |
| 存储盘迁移 | 只有 SLO/容量触发时需要 | FC-1303 finding 后另行授权 | P3 conditional |
| company-wiki 投资研究/估值闭环 | 与 BOUNDARY-0 冲突 | cancelled | 不实施 |

## 7. 当前唯一待办统计

- 当前活动实施队列：r2 的 Phase 1–15、FC-101~1505，共 68 个 implementation FC；Phase 0 的 FC-000~002 仅计划基线已完成。
- 当前 mandatory scenarios：95；目前只是计划定义完成，产品执行状态仍 pending。
- 旧计划中仍显示的空复选框不再自动计入活动待办；其状态必须按本总账解释为 superseded/cancelled/deprioritized/archived。
- 任何未来实施者发现旧项目未在 crosswalk 中，必须先登记并由 reviewer 判断是新增 FC、并入现有 FC、P3 backlog 还是 cancelled；不得直接恢复旧计划执行。

## 8. 所有历史空复选框的集合级处置

> 为保留历史证据，旧正文的空框不做批量伪勾选；下表对每一个空框集合给出当前状态。后续工具统计活动待办时必须排除这些文件，只读取 r2 registry。

| 文件 | 当前已勾/空框 | 空框最新处置 |
|---|---:|---|
| revenue `task_plan.md` | 180 / 387 | 与六目标相关者全部 superseded 到 FC crosswalk；其余研究体验/文档提案降 P3，需重新立项 |
| revenue `IMPLEMENTATION_PLAN.md` | 21 / 0 | 唯一旧延期项已补标 superseded；无活动空框 |
| revenue `review_audit/task_plan.md` | 16 / 0 | 原“批准后实施”已补标 cancelled/superseded |
| revenue `audit_review/task_plan.md` | 16 / 0 | 审查完成；无活动空框 |
| revenue `2026-08-08_adversarial_plan/task_plan.md` | 20 / 0 | 审查/规划完成；产品阶段由状态覆盖整体 superseded |
| revenue 旧 data-lake `task_plan.md` | 0 / 17 | 17 项全部 superseded 到 r2；旧 receipt 不足以补勾 |
| filing `task_plan.md` | 75 / 0 | 历史窄范围完成；无活动空框 |
| company 根 `task_plan.md` | 272 / 0 | 历史 scoped completed；新缺口转 r2 |
| company `task_plan_v2.md` | 0 / 22 | 22 项全部 cancelled/superseded_by_BOUNDARY-0 |
| company recovery draft | 33 / 19 | 19 项全部 archived_reference，不是产品待办 |
| company `verification_CW-2.24_plan.md` | 10 / 0 | Phase 2/3 漏勾已按后文证据回填完成 |
| company `review_plan.md` | 0 / 18 | 18 项取消为独立待办；适用检查转 FC-1201~1304/1502 |
| core-section plan | 13 / 0 | 历史完成；维护态 |
| portfolio-reuse-fix | 13 / 35 | 新增 2 项关闭处置勾选；35 项停止作为待办；Strategy A 历史/Phase 7 均 superseded |
| portfolio-reuse-automatic | 10 / 38 | 10 项 Strategy B 实际完成清单已勾选；38 项 Strategy A 清单取消；泛化目标转 FC-301~705 |
| catalog-space plan | 6 / 42 | 6 项阶段处置已勾选；Phase 5 cancelled_by_D4；长期验收转 FC-1302~1504；42 个旧模板空框不再活动 |
| company `.recover-*` 两份 | 各 68 / 21 | 全部 archived_reference |
| archive `IMPROVEMENT_PLAN.md` | 0 / 11 | archived_reference |
| archive `KARPATHY_GAPS_PLAN.md` | 0 / 24 | archived_reference |
| archive `LLM_INTEGRATION_PLAN.md` | 0 / 25 | archived_reference |
| archive `PLAN.md` | 16 / 9 | archived_reference |
| archive `REFACTORING_PLAN.md` | 0 / 78 | archived_reference |

归档空框不被“取消后打勾”，因为那会改写历史事实；`archived_reference` 本身就是最终关闭状态。
