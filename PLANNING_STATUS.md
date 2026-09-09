# Planning 当前状态与历史路由

> **2026-09-09 深夜最新覆盖（22:00 运行后，只读核对）**：daily 触发成功——`run_id=20260909T210001Z`、`ok=true`、`problems=[]`、`legacy_hits=[]`；权威账本 `company-wiki/.source_catalog/legacy_periods.json` 开 **period 9**（`started_at 2026-09-09T21:00:21Z`、hits=0、sample 62 文档）。**FC-705 门仍 `close_allowed=false`**：last-two = P7（23:59:41 ✗）+ P8（24:00:11 ✓）；预计 **2026-09-10 22:00 运行后**（P8+P9 两个连续 ≥24h 零 hit）转 true。**R9 批 3 范围修正**：09-02 的「无生产读者 backfill/promoter」已过时——`backfill_v2`（`dropbox_governance.py:22` 生产导入）、`portfolio_promoter`（`cli.py:27` CLI 导入）、`_scan_root_v1`（`scanner.py:1401` 生产分派 + parity）、`legacy_bridge_enabled`（`resolver.py:322`/`architecture_gate.py`）均有活跃调用者，仅 `artifact_backfill.py` 零生产读者；批 3 需技术门 + owner 政策门双重满足并重新拆分，清单见 [r9_batch3_checklist.md](assurance/runs/2026-09-02_remaining-gap-closure/r9_batch3_checklist.md)。**Worker v5 独立轨道全部完成**：V5-0/R/1/2/3 completed，正式冻结 51 项 + 三轴独立审查 `accepted`（SQL/性能、生命周期/安全、测试/DAG），四轮整改关闭 14 P1 + 3 P2；仍 PLAN_ONLY。GP-009 累积 Daily **4/7**、Weekly 0/2（下次 09-13 04:30）、Monthly 1/1、drill 1/1。本轮仅文档 + 只读核对，未删除/未实施/未恢复 worker。

> **2026-09-08 当前规划覆盖：R4**。按用户要求，整改的唯一活动编排现为[虚拟数据湖收敛计划](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)，配套[真实测试/审计矩阵](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-test-matrix.md)与[旧WP迁移表](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/r4-transition.md)。四个增量A/B/C/D及独立收入M取代旧15包/95门执行顺序；原117项、GP和原始负例保留。下方较早“15包/旧总计划为准”仅指当时交付，不再驱动执行。v5继续独占worker正式合同，仅约束对应后台能力，不阻普通本地读取。本次仅文档，没有复验源码/运行状态或授权实施；下方HEAD和daily均为历史观测，未来实施重新锁定输入。

> **2026-09-07最新覆盖**：其他任务继续推进，wiki HEAD=d92f8bf、revenue=6682ecf、filing=89c8bdb。最新daily为20260906T210001Z、ok=false/空triplet；默认观察账本已改到wiki路径，revenue旧ledger的green不可替代。revenue旧closure工具/测试及CI step已实际删除，wiki批3延后，不能再按下方旧快照重复删除或称“只等时间”。详见[并发状态差异与未验证边界](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md)；下方9/6事实保留为当时观测，相关原反证在新HEAD须独立重验。本轮仅同步文档，没有执行这些代码/删除/运行。

> 最新核对2026-09-06，观测HEAD为2ff20d9；本页是非执行性状态覆盖层，不修改冻结证据，不授权下载、生产处理、任务注册或legacy删除。用户本次批准文档同步与步骤细化。原痛点效果及下一步唯一整改编排见[新审计及15包计划](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/README.md)，全部整改仍未实施；旧GP组保留为历史工作/批准记录。

> **2026-09-08 最新观测修正（本地只读核对）**：调度已连续触发成功——09-06 22:00（P2 关闭 25.3h、P3 开启）、09-07 22:00（P6 关闭 25 天零 hit、P7 开启）；最新 daily=`20260907T210001Z`、period=7。本仓 `2ff20d9` 修复 `--run-daily` 参数（已由真实触发验证）；`56ba0eb` 补 manifest `cat-file` 的 `safe.directory`（SYSTEM 上下文 triplet 检查）。**FC-705 门仍 close_allowed=false**（权威账本在 wiki `.source_catalog/legacy_periods.json`；last-two = P5 历史 hits=6 短窗 + P6 合格，待 P7 于 09-08 22:00 完成后满足）。上方 9/07 段的 HEAD/daily 为当时快照。

## 活动计划全量索引（2026-09-08，防遗漏路由）

> 本表是**全部活动计划与审计入口的唯一路由**：任何新计划必须先登记在此，再进入执行讨论。当前**全部整改均为 NOT_IMPLEMENTATION_AUTHORIZED**。

| # | 计划/文档 | 入口 | 状态 | 边界 |
|---|---|---|---|---|
| 1 | **R4 虚拟数据湖收敛计划**（唯一活动编排，44 步：A8/B10/C10/D10/M6+） | [simplified-execution-plan.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md) | PLAN_ONLY / NOT_IMPLEMENTATION_AUTHORIZED | 每步需精确授权；DR/VR/AR 独立审查；1→3→7 批次 |
| 2 | R4 真实测试矩阵（36 组：L/P/O/M） | [simplified-test-matrix.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-test-matrix.md) | 全 pending | 继承原反例；mock 只可诊断 |
| 3 | R4 旧 WP 迁移表（WP00-14） | [r4-transition.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/r4-transition.md) | PLANNING_ONLY | 只调归属 |
| 4 | **架构减法诊断**（R4 依据） | [data-lake-simplification/README.md](../company-wiki/docs/plans/data-lake-simplification-2026-09-07/README.md) | 只读诊断已交付 | 未运行真实业务/性能 |
| 5 | R4 接班手册 | [execution-handbook.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-handbook.md) | 待授权 | 15 包/逐步检查点 |
| 6-8 | 分面手册（控制面 WP00/11/12/14、数据面 WP01-07、模型面 WP08-10/13） | [control](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-control-plane.md) / [data](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-data-plane.md) / [model](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-model-plane.md) | 待授权 | G0–G5 独立审查；真实动作各自批准 |
| 9 | R2/R3 总计划（15 包，被 R4 取代） | [remediation-plan.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/remediation-plan.md) | 历史领域细节 | 不作执行编排 |
| 10 | R4 计划独立审查 | [r4-independent-review.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/r4-independent-review.md) | accepted_for_planning_delta | 不授实施 |
| 11 | R4 文档验证 | [r4-document-validation.json](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/r4-document-validation.json) | 文档核验通过 | 非产品测试 |
| 12 | 原目标索引 117 项 | [unit-ledger.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/unit-ledger.md) | 53 CONTRADICTED + 58 PARTIAL + 6 HISTORICAL_ONLY | 非生产重跑 |
| 13 | 机器门展开 95 门 | [gate-dag.json](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/gate-dag.json) | 全 pending | 只验计划结构 |
| 14 | 审计报告群 | [revenue-audit](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/revenue-audit.md) / [assurance-audit](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/assurance-audit.md) / [gp-audit](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/gp-audit.md) / [upstream-asset-audit](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/upstream-asset-audit.md) / [legacy-inheritance](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/legacy-inheritance.md) | 只读审计已交付 | 需独立复核 |
| 15 | 独立审查群 | [assurance](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/assurance-independent-review.md) / [retention](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/retention-independent-review.md) / [plan](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/remediation-plan-independent-review.md) / [consistency](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/document-consistency-review.md) | 历史/计划级 | 不绑定 R4 当前版本 |
| 16 | 并发差异覆盖（9/7） | [current-delta-2026-09-07.md](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md) | 覆盖 9/6 观测 | 旧反证须新 HEAD 复验 |
| 17 | **Worker v5 独立计划**（V5-0/R/1/2/3 **全部 completed**，2026-09-09） | [v5 README](../company-wiki/docs/plans/source-catalog-worker-recovery-v5-2026-09-03/README.md) / [task_plan](../company-wiki/docs/plans/source-catalog-worker-recovery-v5-2026-09-03/task_plan.md) | V5_2_COMPLETED / PLAN_ONLY / NOT_IMPLEMENTATION_AUTHORIZED | 与主线不合并；H01 为恢复前置；冻结 51 项 + 三轴审查 accepted |
| 18 | GP 组（本仓历史执行/批准 + 部署尾项） | [remaining-gap-closure](assurance/runs/2026-09-02_remaining-gap-closure/task_plan.md) | 历史 + 部署尾项 | 不并行领取；旧批准不扩为新许可 |
| 19 | 文档同步（9/4，历史） | [planning-sync-2026-09-04](../company-wiki/docs/plans/planning-sync-2026-09-04/task_plan.md) | 历史交付 | 历史 hash 库存非当前合同 |

**登记纪律**：新增计划/审计目录必须先在上表登记入口与边界，再进入任何执行讨论；未登记的计划视为未授权。

## 当前事实

- 原CA/ZR DAG机器登记accepted 117/117，state为completed/J_terminal；旧FC/WU/ZR的pending、current_next和首卡提示不再是活动队列。历史accepted只表示当时范围，不证明目前所有生产能力持续健康。
- [remaining-gap-closure](assurance/runs/2026-09-02_remaining-gap-closure/task_plan.md)保留历史执行/批准，新整改不从旧勾选领取。GP-006只完成临时sibling roots非阻断CI子集，真实roots门未完。GP-008参数已在2ff20d9改为`run-daily`，但重注册后的实际Action及自然触发仍缺独立证据。
- GP-009保留owner重注册daily/weekly历史记录；latest观测daily manifest为20260905T194055Z、period2、ok=true但绑定旧2cbd585；一个ended_at完整窗口，第二个未完、close_allowed=false。两个实际completed且各≥24h/hits=0及真实7/2/1/1尚不能宣称完成，未来时间/重复run/skip等门仍需修复，不按日历放行。
- GP-010已授权并部分执行：normalized7/7、receipt7/7、summary6/7；1份安全拒绝为预期fail-closed；9/4规则分节后七份目标研报sections=5/7，另2份列表式文档仍缺。registry197/197 passed不等于生产语义7/7闭环。
- N-1/R9已有A+B批准历史，但未执行删除；GP-008及真实观察证据仍阻塞。revenue批1+2同一commit、随后wiki批3独立commit是当前批次口径；本页不触发执行。

## 各组处置

9/6逐项效果审计覆盖117项，发现证据范围缩减及当前模型/发布/资料链反例，不能把“历史accepted”解释为原完整目标已解决。矿业单位/期间权属/真实模型消费/事务发布/历史回测分别纳入WP08–10；完成证明/CI/调度/真实旅程/退出纳入WP00/11–14。详见[revenue效果审计](../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/revenue-audit.md)。本表历史文件处置保持，不破坏plan_inputs或终局收据hash。

| 文档组 | 今日处置及权威关系 |
|---|---|
| 根task_plan/findings/progress | 根TERMINAL_NOTICE覆盖的历史；原ZR408停点已被后续state接管，正文保留 |
| IMPLEMENTATION_PLAN.md | R1～R9历史实施记录；旧FCAP路由由本页覆盖，pending不重开 |
| review_audit四文档 | 历史审查/roadmap/实施日志；旧R/FC状态均不作为领取指令 |
| audit_review根README及三件套 | README是hash绑定的旧控制页；state终局优先，正文“只能领取CA001”不可照跑；三件套已归档 |
| audit_review/2026-08-08_adversarial_plan | 审查完成、旧WU规范被取代；整个包只读 |
| audit_review/2026-08-09_data_lake_refactor_plan | 74WU与旧观察日志为历史；旧72/84场景和period序列不能继承为当前证据 |
| audit_review/2026-08-09_full_completion_assurance_plan | FCAP r2/71FC/95场景冻结输入；旧FC150x和R9被CA继承，不重开 |
| audit_review/2026-08-12_zijin_skill_run_audit | 固定真实运行审计包；只证明当时run，不是继续下载/处理授权 |
| audit_review/2026-08-13_three_repo_completion_rebaseline_plan | 25CA总计划/manifest只读；当时“实施全pending/首卡CA001”由state终局覆盖 |
| audit_review/2026-08-13_zijin_data_lake_remediation_plan | 92ZR与102场景、架构/迁移规范冻结附录；不独立领取 |
| assurance/runs/session-2026-08-13四文档 | CA/ZR实施工作记忆；末尾已交接9/2GP，首页旧ZR206不是当前停点 |
| assurance/runs/2026-09-02_remaining-gap-closure六文档 | 活动续接记录；当前覆盖声明优先于9/2/9/3快照，保留批准原文与历史日志 |
| .review-zr407-20260818内company-wiki/filing-fetch planning | 历史独立review克隆；包含根、四docs/plans组和归档计划副本，不是新增活动队列，不修改/删除 |
| .tmp*测试目录 | 非活动计划；可读ZR408三组未找到planning副本，13个拒绝访问tmp内是否有副本未知 |

`assurance/unified_completion/manifests/plan_inputs.json`的44项hash本次逐项重算全匹配。六个日期audit包均由TERMINAL_NOTICE关闭；CA306契约仅允许包内TERMINAL_NOTICE这个新文件，不在六包内增加CURRENT_STATUS，也不重算manifest来隐藏文档漂移。

## 阅读覆盖与局限

本轮按canonical planning-with-files边界全文覆盖93/93份、25,163行；新增本页后为94份。范围包含根4件、review_audit4件、audit_review根4件、六个日期计划包递归71件、session4件与活动GP6件。46份冻结输入的当前SHA-256重算46/46匹配。逐文件证据见[范围复核](../company-wiki/docs/plans/planning-sync-2026-09-04/revenue-scope-inventory.md)及[主审计记录](../company-wiki/docs/plans/planning-sync-2026-09-04/revenue-forecast-audit.md)。

明确排除：`assurance/fc` 16份与`unified_completion/receipts` 194份是执行/审查证据，不是planning-with-files计划正文；由state/manifest/receipt链解释。13个拒绝访问的`.tmp-*`目录属于临时review/fixture范围，其内部是否另有Markdown保持UNKNOWN；因此结论是canonical范围完整，不扩张为整个文件系统绝对无遗漏。`.review-zr407-20260818`不含revenue自身planning克隆。

本轮仅做本地只读证据核对及planning文档建议；没有重跑生产审核、外部provider/LLM、任务注册或legacy删除。下一步修复/部署核验必须另按活动计划的允许范围与独立review要求进行。
