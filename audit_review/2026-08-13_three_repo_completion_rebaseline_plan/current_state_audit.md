# 三仓当前状态对抗式审计

> 审计截面：2026-08-13。代码仍可能由其他程序推进，本文因此是 `ZR-001/CA-002` 的输入，不是未来实施基线。  
> 观察 HEAD：revenue `c3a0519303d78dfe283bea6247da53163b926dc8`；filing `83c638e76e40890262746cdf02b6df495dcb4031`；wiki `ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875`。三仓均在本地 `fcap`，未绑定 upstream；工作树状态分别有4、0、4项，未由本任务修改。

## 1. 总判定

| 问题 | 当前答案 | 不能判“是”的主要证据 |
|---|---|---|
| 重构完全成功了吗 | 否，v1生产链与v2/shadow/contract并存 | R9强门4/4失败；生产调用绕过v2/flags；旧manifest与current triplet分离 |
| Dropbox在filing-fetch功能层可用吗 | 目录和记录在catalog，真实Dropbox-only全链不可用 | filing handle validation默认companies；旧canary选中companies副本；sidecar污染 |
| 所有功能和目标实现了吗 | 否 | revision、artifact lineage、ProcessingDemand、broker语义、revenue contract、逐矿模型和发布事务均有断链 |
| 主要功能被持续动态审核吗 | 否 | workflow无schedule；runner无production caller/新鲜报告/告警/soak |
| E2E覆盖真实使用吗 | 部分，不足以保证 | companies-only、fake/preseed/旁路多；真实root/worker/revision/broker/mine/Windows缺失 |
| 代码质量全面提升了吗 | 部分 | root/company/path硬编码、高CC、双实现、旧pin、误导测试名/注释仍在 |

## 2. `company-wiki`

### 已实现且可保留

- source/document/location 的基本拆分、content SHA去重、strict identity 和 normalized resolver。
- RootPolicy 2.x、adapter registry、sidecar adapter、runtime activation/CAS/rollback 等组件级资产。
- GapPlan/CloseGap、authorization/staging/canonical writer、SourceBundle/ArtifactHandle 的基本形状。
- page-aware PDF解析和大量 cell page/table/row/column span；存量 normalized/summary/sections。
- migration/journal、IsolatedLake、reason taxonomy、质量与SLO工具底座。

### 当前生产断链

1. **读路径有写能力**：`CatalogStore` 初始化会mkdir、普通SQLite连接、WAL、DDL/migration/seed/commit；resolver service懒建该Store。隔离证明构造不存在DB会创建约237,568B数据库。`readonly_canary`直接mode=ro查询，不经过production resolver。
2. **v1/v2同请求分叉**：CLI resolve可显式传runtime policy，acquisition与close-gap内部却可缺省构造v1+legacy resolver。current runtime flags也有多个只有定义无production consumer；flag为true不等于功能实际启用。
3. **policy不能复算**：当前YAML导出hash与runtime snapshot `policy_hash`不同；三个root也没有显式filing复用授权。envelope只有hash，没有可验证root capability snapshot。
4. **v2 metadata覆盖极小**：active v2 assertions主要是少量canary；resolve active/legacy off与ensure/close-gap看legacy全量可能产生候选集合分裂。
5. **location fallback不完整**：preferred location消失时，不会稳定尝试同SHA的下一条policy-eligible副本；声称fallback的测试只测排序helper。
6. **artifact lineage不可信**：completed normalized 4,835中只有177有schema+source SHA；summary 2,963中只有4两者齐全；producer仍可能写空source SHA，validator却只在非空时比较。
7. **shadow binding无消费者**：backfill写 `artifact_bindings`，production bundle查 `artifacts`；迁移判断、validator和consumer真源不一致。
8. **producer telemetry是假代理**：AFTER INSERT按role推断parser/LLM，无法表示attempt、failure、retry、update、cache hit或真实调用次数。
9. **安全/隐私未接生产门**：大多数文档无prompt receipt；Dropbox 649份LLM summary仅1份当前关联review receipt，且root默认public、worker无privacy/receipt过滤。需要历史egress审计，不能仅凭metadata认定合规或违规。
10. **broker不是一等文档**：v1把directory默认broker；JSON sidecar大量成为primary；单实体candidate、多实体事实归属、typed table、chunk/tag/fact、privacy/rights均未闭合。
11. **ProcessingDemand不存在**：worker按固定全局顺序，消费者不能提交幂等、有限预算、可等待/追踪的需求。

### 实库影响证据

- Dropbox active locations约9,225，PDF约5,458、JSON约3,156；“被索引”与“可语义消费”相差很大。
- 21个dayu-only active filings（15 annual、3 semi、2 quarterly、1 regulatory）当前会在filing消费边界被拒绝。
- Dropbox少量所谓独有annual/semi中至少4个是标题以`.pdf.source`结尾、日期为空的sidecar假阳性。
- 真实catalog约49.6GB且存在WAL/SHM/locks，必须以live writer+reader验证，不能用小临时DB替代。

## 3. `filing-fetch`

### 已实现且可保留

- FilingRequest、market routing、identity、exact/equivalent结果、gap/authorization、staging和single-flight骨架。
- CN/HK/US provider适配和若干真实canary；分阶段envelope/handle传输结构。
- 无授权不下载、canonical writer写受管companies等核心安全方向。

### 当前生产断链

1. **external-root handle被默认拒绝**：生产 `_handle_from_resolution/validate_handle` 没收到RootPolicySnapshot/allowed roots，退回 `<wiki>/companies` containment。dayu/Dropbox即使resolve成功也无法复用。
2. **policy只剩hash**：上游envelope未携带可重算eligible-root snapshot，filing既无法验证授权又不能自行扩大授权。
3. **revision不action**：只在`gap_plan.missing`非空时close；`newer_revision`不下载。
4. **只处理一个missing**：close-gap取`missing[0]`，不能按authorization `max_items`稳定闭合多期间/多修订并返回remaining gap。
5. **revision语义偏弱**：provider ID/字符串顺序可能替代filed_at/amendment/revision sequence。
6. **错误透明度不足**：catalog raw lock可能落fatal；下游safety/artifact失败会遮蔽已复用/零下载事实。

## 4. `revenue-forecast`

### 已实现且可保留

- 分部/情景/公式validator、central model registry、formal强门与签名基础。
- source-preparation真实subprocess调用filing，能消费resolution envelope和artifact selector。
- immutable snapshot和backtest误差数学、future-source-date检查等底座。
- `reserve_depletion`等通用资源型公式，不应推倒。

### 当前生产断链

1. **schema真源漂移**：runtime 3.7，文档/生成器/help仍有3.6；capture实际10键但文档曾写9键。
2. **generator无效**：隔离生成rc=0，随后linter rc=2、engine validate-only rc=2并报41项；包括缺management_targets、非法not_checked、history/claim/dimension/currency/hash/recognition问题。
3. **validate-only会写**：有效fixture返回0却创建676B publication registry，因为先跑formal forecast再判断flag。
4. **draft出口断裂**：draft receipt gate_ids为空，公共renderer按formal gate集合校验而失败。
5. **publication非事务**：registry先append、JSON/MD后写；snapshot也先注册再落盘；失败可留下孤儿，重复运行可重复row。
6. **ProcessingDemand是假声明**：缺/坏artifact时只返回事件描述，没有真正enqueue/worker handoff；测试把字符串scheduled当完成。
7. **矿业只能fallback**：无mine/asset identity、地区、商品/产品、resource-reserve basis、ownership/consolidation、TC/RC/FX/byproduct/internal elimination和会计桥。
8. **confidence可博弈**：复制claim、拆参数、单一低误差observation、名义非direct+巨大plug都可能抬分；accuracy record不绑定company/snapshot/evaluation/publication。
9. **真实E2E不足**：fake PDF、preseed catalog/events、UJ旁路；source E2E可能把结构化业务失败当runner成功且CI未运行。

## 5. 测试、CI、动态审核与质量

### 当前测试告诉我们的真实范围

- company/filing seam和contract套件可大量通过，说明组件资产有价值；它们不能证明production cutover。
- 显式 `R9_GATE=1` 当前4/4失败：`backfill_v2`仍可import、`_scan_root_v1`存在、legacy flag存在、scanner hardcode allowlist存在；日常默认skip。
- 旧三进程/动态套件在Windows中文/长路径/GBK下仍有失败；部分cryptography/Git/temp错误属于环境，需要短ASCII控制组区分，但跨平台错误本身也是未完成目标。
- 旧closure当前只报FC-1501～1505 pending，漏掉已知triplet、调度、场景、Dropbox、revision、SLO和revenue问题，证明gate不可信。

### CI/动态机制

- 三仓workflow只有push/pull_request，无cron schedule。
- compatibility current triplet陈旧；CI可能checkout旧siblings而非测试最新组合。
- filing真实tool/download测试长期被排除或依赖opt-in；source preparation用户链未作为required。
- Daily/Weekly/dashboard脚本有硬编码样本/路径、SQL代理latency、错误rc忽略、非原子report、无真实scheduler与alert delivery。
- 当前没有满足7 Daily、2 Weekly、1 Monthly、1 alert drill的自然时间证据。

### 代码质量

- 高复杂度主要冻结在高位，没有按热点持续下降。
- root kind/ID、Zijin/601899、Dropbox和个人相邻仓路径仍存在于产品/assurance/SLO/replay。
- v1/v2、shadow/production、binding/columns、runner/script多套真源并存。
- 部分测试名和注释扩大了实际证明范围；部分workflow允许非强制失败。

## 6. 结论如何影响下一步

- 不能“大爆炸重写”：保留成熟组件，通过current RED和mutation筛选already-satisfied资产。
- 也不能只收五张表：先修Evidence/Closure 2.0，再从Reader、RuntimeContext/RootPolicy、freshness、artifact/processing、broker、revenue、真实E2E和动态调度逐层闭环。
- R9现在冻结；新链经过两个完整动态周期零legacy hit、caller=0和rollback后才分批删除。
- 旧计划最终只能 `closed_superseded_incomplete`；新计划完成才代表用户六项目标真正达成。
