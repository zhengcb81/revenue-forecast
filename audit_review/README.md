# 三仓库改进项目：唯一执行入口

> **新任务只从本页开始。不要按日期猜计划，不要从任何子目录的 `task_plan.md`、旧 FC、旧 R9 或 ZR 卡片自行开工。**

## 0. 当前控制状态

```yaml
plan_id: TRI-REPO-COMPLETION-2026-08-13-R1
authority: audit_review/README.md
plan_status: ready_for_implementation
implementation_status: in_progress
current_phase: I_gradual_release
current_next: ZR-1003
active_owner: unassigned
lease: none
blocked_reason: none
last_control_update: 2026-08-23
```

这些字段是唯一的人类可读执行游标。实施开始前，第一张且唯一可领取的卡是 **CA-001**。任何其它文件中的 `pending / accepted / complete / next` 都只是历史状态、冻结规范或审计证据，不具有领取权。

CA-001 完成后必须创建机器状态真源 `assurance/unified_completion/state.json`、工作单元锁和 receipt 目录；此后本页只镜像 `current_phase/current_next/owner/blocked_reason`，机器状态优先。若机器状态与本页冲突，停止实施，回到 CA-001 的 CAS/漂移处理，不能自行选择较“新”或较“方便”的状态。

## 1. 30 秒安全启动

1. 只读本页，不先遍历全部 `audit_review`。
2. 确认 `current_next`；现在只能领取 `CA-001`。
3. 读取本页“当前卡必读包”列出的文件并重算所列 hash。
4. 检查是否已有 owner/lease 或其它 planning-with-files 程序正在写同一状态文件；有冲突就停止。
5. CA-001 只建立计划锁、hash/CAS和状态控制；**不得修改产品代码、配置、catalog、roots、CI或旧计划**。
6. 未获得相应阶段授权，不得下载、迁移、生产 apply、外部 LLM 处理或执行 R9 删除。

## 2. 项目总目标

把 `company-wiki`、`filing-fetch`、`revenue-forecast` 建成一条面向所有公司的通用、松耦合、可审计链路：

```text
用户研究请求
 -> 在所有获准的 data-lake roots 查找逻辑文档和可用 location
 -> 复用可信原文及兼容的 MD/表格/切片/标签/摘要/事实
 -> 判断期间、修订版和研究问题仍缺什么
 -> 仅在明确授权下补下载或提交最小 ProcessingDemand
 -> 消费财报、券商研报、公告/新闻和结构化运营事实
 -> 建立可回溯分部/资产收入模型，资料不足时诚实输出 gap
 -> 安全生成 draft/formal、回测、置信度和持续动态审核
```

三仓职责不可互相复制：

| 仓库 | 唯一职责 | 禁止 |
|---|---|---|
| `company-wiki` | data lake 控制面：root policy、document/location identity、freshness、安全、产物、处理需求、broker/web语义和事实 | 预测收入；把外部root当写目标；为不同consumer复制目录逻辑 |
| `filing-fetch` | 薄财报编排：校验请求、调用catalog、按授权补gap、透明传递阶段回执 | 自建root allowlist；重新判断artifact/safety；默认只有companies可复用 |
| `revenue-forecast` | 来源消费者、收入模型、情景、回测、置信度、draft/formal发布 | 遍历个人目录；维护第二索引；私自下载；把产量×价格冒充可确认收入 |

紫金矿业只是复杂真实 canary。最终还必须通过第二家结构不同的矿企和一家非矿业公司；产品核心中公司名、证券代码、矿名、Dropbox/dayu/companies 特判必须为零。

## 3. 六个不可拆分的最终成功条件

只有以下六项全部取得 current-triplet、真实层级、独立 oracle 和 reviewer 的 machine pass，项目才可宣布完成：

1. 重构完全成功：真只读、单一 RuntimeContext/RootPolicy、v1双轨在观察后安全退役。
2. Dropbox/dayu/未来获准root从 revenue 用户入口真实复用；不是“已索引”或复用其它root副本。
3. 原文复用、时效/修订、最小下载、已处理成果、broker/web、ProcessingDemand、预测与发布全部闭环；不能实现的逐矿信息以受控data gap表达。
4. PR、Daily、Weekly、Monthly和发布前审核实际运行，并能发现自身停摆、陈旧、半报告和告警失败。
5. E2E覆盖真实roots、文档状态、provider、worker、故障、Windows/Linux和三类公司。
6. 产品核心无root/company/path硬编码和不可达双实现，复杂度、类型、覆盖、文档和契约持续受门控。

总体“99%”、测试数量、旧 `accepted`、脚本存在或场景ID出现都不能替代任一条件。

## 4. 当前事实：为什么不能从旧收尾继续

- 旧 FCAP 机器账本是 66/71，FC-1501～1505 pending；R9 强制门当前 4/4 RED。
- 严格按当前 triplet，旧71项为：31项有实现但未独立复验、26项被当前行为反证、9项证据陈旧、5项pending；0项可直接继承为当前完成。
- Catalog production读路径仍可能 `mkdir/WAL/DDL/migrate/commit`；只读canary不是production入口。
- 同一请求可能先走v2 resolve，再由ensure/close-gap缺省回v1；当前配置导出policy hash与runtime snapshot不一致。
- filing-fetch 未取得eligible-root snapshot，默认只接受 `<wiki>/companies`；实库至少21份dayu-only filing因此不可用。旧Dropbox canary实际选中了companies副本。
- `newer_revision`能出现在GapPlan，却没有进入下载动作；多gap只处理一个也可能假装闭合。
- 大量存量MD/summary缺可靠source hash/binding；shadow binding没有production reader；producer event不是实际parser/LLM调用日志；ProcessingDemand尚不存在。
- Dropbox已有LLM摘要但安全/隐私回执严重不足，需要P0历史egress审计；现有catalog不足以断言当时是否外发或已授权。
- revenue generator当前产物不能通过真实引擎；`--validate-only`会写registry；draft renderer失败；formal publication非事务。
- 现有矿业公式不能回答可信的逐矿×商品×产品收入或完成会计勾稽。
- workflows没有真实schedule；现有E2E大量停留在companies-only、helper、fake/preseed或旁路层。

详细证据只在需要复核结论时读取 [当前状态审计](2026-08-13_three_repo_completion_rebaseline_plan/current_state_audit.md)，不要把审计文档当任务队列。

## 5. 文档权威层级

发生冲突时严格按下表处理；不得按文件日期、标题或篇幅自行裁决。

| 优先级 | 文件/目录 | 作用 | 是否可领取任务 |
|---:|---|---|---|
| 1 | **本 `audit_review/README.md`** | 唯一控制面、当前游标、阶段顺序、去重与阅读路由 | 是；只能领取`current_next` |
| 2 | [CA注册表](2026-08-13_three_repo_completion_rebaseline_plan/completion_assurance_registry.md) | 25个证据、动态审核和关闭卡的详细定义 | 仅当本页指向某CA |
| 3 | [统一阶段计划](2026-08-13_three_repo_completion_rebaseline_plan/authoritative_execution_plan.md) | A～J阶段边界、前后门、渐进重构路线 | 不能自行选卡 |
| 4 | [ZR注册表](2026-08-13_zijin_data_lake_remediation_plan/work_unit_registry.md) | 92个产品功能需求卡，冻结annex | 仅当本页/机器DAG解锁某ZR |
| 5 | [新102场景](2026-08-13_zijin_data_lake_remediation_plan/scenario_matrix.md) 与 [旧95场景](2026-08-09_full_completion_assurance_plan/scenario_matrix.md) | mandatory行为与真实层级要求 | 只作测试规范 |
| 6 | [20步实施手册](2026-08-13_zijin_data_lake_remediation_plan/implementation_runbook.md)、[弱模型清单](2026-08-13_three_repo_completion_rebaseline_plan/weak_model_execution_checklist.md)、[目标架构](2026-08-13_zijin_data_lake_remediation_plan/architecture_target.md) | 每卡实施纪律与架构边界 | 只作规范 |
| 7 | 最新目录其余audit/findings/progress/transition/traceability文件 | 证据、迁移和解释 | 从不领取 |
| 8 | 所有旧日期目录和根旧planning三文件 | 历史证据 | 从不领取 |

若本页与优先级2～6的冻结规范发生实质冲突：停止在当前卡，登记 `plan_drift`，由CA-001/closure reviewer裁决并版本化本页；不能默默覆盖annex。

## 6. 唯一 A～J 执行顺序

同一时间最多一个工作单元 `in_progress`。表中“工作范围”是唯一阶段归属；具体依赖以CA/ZR注册表为准。

| 阶段 | 工作范围 | 本阶段首卡 | 阶段出口 | 下一阶段 |
|---|---|---|---|---|
| A0 基线与锁 | `CA-001→002→003→004`，再重放`ZR-001/003`；`ZR-002/004`按第7节共享证据关闭 | **CA-001** | 精确triplet、输入hash、CodeGraph indexed commit、strict legacy disposition、机器状态/锁成立 | B |
| B Evidence/Closure 2.0 | `CA-101→102→(103,104)→(105,106)→107→108→109` | CA-101 | 旧证据被诚实判incomplete；receipt/scenario/closure关键mutation 100%杀死 | C |
| C 真只读与契约 | `ZR-101～206`中未被CA共享实现的产品部分 | ZR-101 | production Reader零写、typed queries、锁taxonomy/retry、live WAL/大catalog SLO | D |
| D 生命周期、roots、时效/下载 | `ZR-301～409` | ZR-301 | safety/artifact decision graph、单一RuntimeContext、Dropbox/dayu/future-root、missing+revision闭环 | E |
| E broker/web/处理需求 | `ZR-501～510`及`ZR-304～306`存量迁移部分 | ZR-501 | 七研报语义产物、网页沉淀、真实ProcessingDemand、可信最小重算 | F |
| F revenue与矿业 | `ZR-701～713`和`ZR-601～611`；先`ZR-610`会计ADR，允许两支受控并行后合流 | ZR-701 / ZR-610 | generator/validate/draft/formal发布闭环；矿山会计桥或诚实gap；可信回测/置信度 | G |
| G 真实E2E | `ZR-801～806`的业务测试要求；machine registry由CA-105唯一实现 | ZR-802 | roots×状态×provider×worker×故障×平台×三类公司全绿、zero-skip | H |
| H 动态审核与质量 | `ZR-901～907` + `CA-201→(202,203,204)→205→206` | ZR-901 / CA-201 | current-triplet PR门、7 Daily、2 Weekly、1 Monthly、1 alert drill | I |
| I 渐进发布 | `ZR-1001～1008`；legacy删除由`CA-304`唯一拥有，`ZR-1009`只保留需求 | ZR-1001 | shadow/cohort/rollback全绿，两个完整动态周期legacy hit=0，caller=0 | J |
| J 独立终验与关闭 | `CA-301→(302,303)→304→305→306`；替代`ZR-1101～1105`实现 | CA-301 | 六目标逐项machine pass；旧计划只写terminal notice并关闭旧领取入口 | 完成 |

阶段内括号表示在各自前置满足后可并行，但共享registry/schema/migration/release始终单writer。除表中明确允许的分支外，禁止越级。

## 7. CA/ZR 重叠任务的唯一实现归属

下表防止弱模型实现两套validator、registry、CI或closure。ZR保留业务需求时，使用CA产出的同一实现/receipt验收，不再写第二套代码。

| 重叠主题 | 唯一实现owner | 被吸收/共享的ZR | 处理方式 |
|---|---|---|---|
| 计划锁、triplet、历史处置 | CA-001～004 | ZR-001/002/004的治理部分 | CA先实现；ZR只补产品drift/golden corpus并引用CA receipt |
| receipt、command、closure validator | CA-101～109 | ZR-002、ZR-103 | 只实现CA版本；ZR目标用同一receipt关闭 |
| scenario machine registry | CA-105/106 | ZR-801 | ZR只定义业务场景，不新建registry/coverage算法 |
| current-triplet PR fan-out | CA-201 | ZR-105、ZR-901 | CA拥有调度/attestation；ZR提供required checks |
| Daily/Weekly/Monthly与release freshness | CA-202～206 | ZR-902～905 | CA拥有scheduler/report/alert；ZR提供业务SLI/oracle |
| legacy最终删除 | CA-304 | ZR-1009、旧R9 | CA-304唯一执行、分批rollback并统一签收 |
| 最终独立终验/关闭 | CA-301～306 | ZR-1101～1105、旧FC-1501～1505 | 只运行CA链；ZR/FC作为需求映射，不再建较弱closure |

若发现其它重叠，不能自行选择owner；先在当前卡登记并由CA-101的strict DAG指定唯一owner。

## 8. 当前卡 CA-001：必读包与边界

只需读取以下文件，不必先读全部计划：

1. 本页。
2. [CA-001详细卡](2026-08-13_three_repo_completion_rebaseline_plan/completion_assurance_registry.md#ca-001计划输入锁与并发-cas)。
3. [输入30文件快照](2026-08-13_three_repo_completion_rebaseline_plan/input_snapshot.md)。
4. [最新计划manifest](2026-08-13_three_repo_completion_rebaseline_plan/PLAN_MANIFEST.md)。
5. [20步实施手册](2026-08-13_zijin_data_lake_remediation_plan/implementation_runbook.md)的并发/状态/receipt规则。
6. [弱模型执行清单](2026-08-13_three_repo_completion_rebaseline_plan/weak_model_execution_checklist.md)第1、2、9节。

CA-001的唯一目标：为plan/registry/command/scenario/migration/release等共享资源建立单writer、owner、TTL、hash/CAS和无半写的bootstrap状态。允许写入范围仅为未来统一assurance控制目录、本页控制字段以及CA-001 receipt；产品代码、产品配置、旧计划、catalog、roots和CI全部禁止。

CA-001完成后，机器DAG若无漂移，`current_next`只能变为`CA-002`。

## 9. 每张卡的固定执行流程

每张CA/ZR必须遵循：

```text
读取本页current_next并获取lease
 -> 重算triplet/plan/config/schema/sample hashes
 -> 阅读该卡及前置receipts，声明allowlist/forbidden/预算
 -> 从公开production入口建立current RED和独立oracle
 -> reviewer确认RED有效
 -> 最小实现（不顺手清理、不降门、不新增特例）
 -> focused -> owner repo -> affected siblings -> exact triplet
 -> 指定T0/T1/T2/T3/T4 + fault/mutation/race/第二次幂等
 -> migration/route需要时做before->shadow->rollback->restored
 -> implementer receipt
 -> clean-checkout independent reviewer receipt
 -> closure validator唯一推进状态和current_next
```

实施者最多推进到 `independent_review`，不能自行写 `accepted`。`blocked`必须记录外部条件、尝试、owner和解除条件；required场景blocked仍使项目未完成。skip/xfail、减少collection、脚本存在、旧绿、测试ID文本出现一律不算pass。

## 10. 测试层与不可替代性

| 层 | 必须使用 | 不能证明 |
|---|---|---|
| T0 | pure/schema/property/contract | 跨仓production接线 |
| T1 | 临时roots/catalog、真实revenue→filing→wiki subprocess、边界spy | 真实49GB catalog、私人PDF、provider |
| T2 | 真实catalog/companies/dayu/Dropbox只读、root-exclusive样本 | 外网下载或production cutover |
| T3 | 真实provider+临时wiki，首次下载与二次零下载 | production cohort |
| T4 | 明确授权的最小production cohort与rollback | 长期动态健康 |

T2不能被100个T0替代；无权限、网络、凭据或样本只能记blocked。每层必须有独立receipt、side-effect ledger和新鲜度。

## 11. 写入、安全和停线规则

- `company-wiki/companies`是唯一canonical write store；Dropbox/dayu等外部roots永远零写。
- 没有明确授权，provider discover/fetch/canonical commit及外部LLM egress均为0。
- `private_user + not_reviewed + 无egress授权`时外部LLM调用必须为0。
- 所有迁移先副本dry-run、计数守恒、journal、resume/idempotence和rollback；不可证明的legacy不猜绑定、不删除。
- 不得stash/reset/覆盖用户dirty文件；计划或registry hash漂移立即释放lease并停线。
- 错实体/期间/修订版、外部root写入、未授权下载/外发、冲突静默吞并、required skip、不可解释shadow diff、无rollback迁移、同请求policy漂移均立即停线。
- CodeGraph重建只在CA-003独占窗口执行；用户此前已授权三个目录在需要时重跑，但不得与其他index writer并发。
- R9只在CA-304、两个完整动态周期zero-hit、caller=0、全旅程及rollback通过后分批执行。

## 12. 活状态、冻结规范与会话交接

### 可写活状态

- Bootstrap期间：本页第0节的控制字段，使用CAS小补丁。
- CA-001后：`assurance/unified_completion/state.json`、locks、current execution results和按WU分目录receipts；具体schema由CA-101/102版本化。
- 实施代码/测试：仅限当前卡声明的allowlist。

### 只读冻结规范

- 本页第13节列出的CA/ZR/scenario/runbook/architecture hash对应文件。
- 所有旧日期目录的历史receipt、finding、progress和plan正文。
- 真实roots与production catalog，除非对应T4/migration卡获得明确授权。

### 每次会话结束

1. 写当前卡的命令结果、side effects、errors和receipt；不写口头“基本完成”。
2. closure未接受时，`current_next`保持本卡并记录blocked/remaining。
3. closure接受后，由validator按DAG写唯一下一卡；更新本页镜像和hash。
4. 记录owner/lease释放；不能留下不明in_progress。
5. 不修改冻结计划checkbox来表示实施进度。

### 新会话接手

只读本页和machine state，核对hash/lease，再读取`current_next`的按需包。不要从findings/progress中推断下一步。

## 13. 冻结规范索引与hash

| 规范 | 精确路径 | SHA-256 |
|---|---|---|
| CA卡 | `audit_review/2026-08-13_three_repo_completion_rebaseline_plan/completion_assurance_registry.md` | `861e28f9dc72864347041ef1a8b0deabf38afdb3581ffce5050cb794f361f3e7` |
| A～J详细阶段 | `audit_review/2026-08-13_three_repo_completion_rebaseline_plan/authoritative_execution_plan.md` | `2a18294bad809978f6fc60a573764fdb8cfc91c5ea0c8ec4bc141fe3a6e8f6c9` |
| ZR卡 | `audit_review/2026-08-13_zijin_data_lake_remediation_plan/work_unit_registry.md` | `72c70eb6df9bf9cd04e8a9e42ad795477da9c28f30db291d7b8d1dda3d5de709` |
| 新102场景 | `audit_review/2026-08-13_zijin_data_lake_remediation_plan/scenario_matrix.md` | `e08cbe4e93b933bd01bc758dcef5aeee194417bde0d23d05ea0bc011e03cac8a` |
| 旧95场景 | `audit_review/2026-08-09_full_completion_assurance_plan/scenario_matrix.md` | `21e9201296aa048bd61e1125525a0eadb8ac1deb5bed76a641f05b3099f1d3c5` |
| 20步手册 | `audit_review/2026-08-13_zijin_data_lake_remediation_plan/implementation_runbook.md` | `b20a8b886261118a0b1449809f63db8de4f57f6099061115c9af8761c95ba132` |
| 弱模型机械门 | `audit_review/2026-08-13_three_repo_completion_rebaseline_plan/weak_model_execution_checklist.md` | `099b6db13843314a8bb03490ed52e9b64771f8561e8547cd58b817c9258e0c8d` |
| 目标架构 | `audit_review/2026-08-13_zijin_data_lake_remediation_plan/architecture_target.md` | `288995a9b9e4c2f6848fd28d35d6fc9297248f5fc674f18a61dc2ac79de34f6b` |

任一hash不符都先执行plan-drift审查，不能自动采用修改版。

## 14. 历史目录处置

| 路径 | 处置 | 可引用内容 | 禁止 |
|---|---|---|---|
| `2026-08-13_three_repo_completion_rebaseline_plan/` | 当前详细附录，只读规范+审计 | CA卡、阶段计划、现状、迁移、追踪、自审 | 从其task/manifest自行挑卡；把计划编制状态当产品状态 |
| `2026-08-13_zijin_data_lake_remediation_plan/` | 冻结功能annex | 92 ZR、102场景、架构、runbook | 作为第二执行队列；修改checkbox/hash |
| `2026-08-12_zijin_skill_run_audit/` | 真实运行证据/黄金样本定义 | 紫金财报复用、研报/矿山覆盖和失败trace | 当作只针对紫金的产品计划 |
| `2026-08-09_full_completion_assurance_plan/` | 历史FCAP，最终待CA-306关闭 | 旧95场景、历史receipts和rollout证据 | 领取FC/R9/FC-150x；把66/71当当前完成 |
| `2026-08-09_data_lake_refactor_plan/` | superseded历史计划 | ADR和历史设计背景 | 领取旧WU或release |
| `2026-08-08_adversarial_plan/` | superseded审计/历史计划 | 早期痛点与证据 | 领取旧Phase |
| 根 `task_plan.md/findings.md/progress.md` | 2026-08早期审计归档 | 历史上下文 | 按其FCAP链接执行 |
| 本目录 `progress.md` / `findings.md` | 历史归档（头部声明已关闭） | 早期审计上下文与一次性补记 | 继续追加实施进度/计数 |

**进度记录单一真源（防双写漂移，2026-08-22 起强制执行）：**
- 实施进度逐卡记录只写入 `assurance/runs/session-*/progress.md`（追加式，每卡 closure 后一段）；其余文档一律引用它，不复制详情。
- `accepted N/117` 计数唯一真源是 `assurance/unified_completion/state.json`（closure-advance 自动维护）；文档需要时写"见 state.json"或由脚本读取生成，**禁止手工维护计数**（2026-08-22 曾因手工 +1 漏计一张卡导致 5 份文档 104 处系统性漂移，已全部按 state.json 权威时间线更正）。
- 本目录（audit_review/）的 `progress.md`/`findings.md` 不再追加实施进度；仅本 README 的 `current_phase/current_next` 由 closure-advance 自动镜像（CAS 保护，不漂移）。

旧计划历史文件不移动、不删除、不重写。只有最终CA-306可由旧计划单一owner添加terminal notice：`closed_superseded_incomplete`，指向最终closure ledger；此前一律保持只读。

## 15. 何时才算真正完成

CA-305必须对六个成功条件逐项生成需求→场景→current triplet→结果→side effects→reviewer的machine ledger；CA-306只在全部pass、动态证据仍新鲜、rollback已演练、旧任务全部有successor结果时关闭旧入口。

软件不能保证未来永远没有任何缺陷；本计划的完成含义是：所有已知痛点被关闭，关键同类回归被真实E2E、mutation和持续动态审核自动发现并阻断，而不是依赖下一次人工大审计。
