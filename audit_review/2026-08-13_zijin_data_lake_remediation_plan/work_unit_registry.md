# ZR 工作单元注册表

> 所有单元初始状态均为 `pending`。表中“通过”仅描述未来验收条件，不是当前结论。每个单元必须使用 `implementation_runbook.md` 的20步流程和独立 reviewer。

## Phase 0：重新基线化

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-001 | revenue + 三仓 | 无 | 冻结 current triplet，重放紫金 exact reuse、旧 artifact、Dropbox、draft renderer 等生产反例 | `drift_ledger.json`；每项为 still-failing/already-satisfied/superseded/blocked；禁止仅看旧 receipt |
| ZR-002 | assurance owner | ZR-001 | 冻结 command/scenario/receipt schema、计划写锁和 shared-resource lock | registries 有 hash；并发写入 mutation 被拒；命令不能被实施者缩减 |
| ZR-003 | assurance owner | ZR-001 | 将紫金年报、七份研报、错误 strategy HTML 和预测 input/result 注册为脱敏 golden corpus | source/content hashes、预期实体/角色/期间、只读权限、无内容泄漏；样本缺失=>blocked |
| ZR-004 | plan owner | ZR-001 | 只读处置旧全面计划每个未完/完成项 | `legacy_plan_disposition.md`：keep/reopen/already-satisfied/deprioritize/cancel/superseded；不修改旧计划 |

## Phase 1：护栏、可观测性与契约基座

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-101 | company-wiki | ZR-002 | 版本化跨仓阶段/原因/事件 taxonomy | identity→consumer 八阶段 schema；unknown reason fail；N/N-1 contract tests |
| ZR-102 | revenue assurance | ZR-002,ZR-003 | 建 hermetic 三进程 T1 runner | revenue→filing→wiki 三真实 subprocess；provider/LLM 仅边界 spy；禁止真实 sibling/root |
| ZR-103 | assurance owner | ZR-002 | closure/receipt/command validator | 篡改 hash、同一 reviewer、缺命令、skip、triplet 漂移、越权 side effect 全拒绝 |
| ZR-104 | 三仓 | ZR-002 | 冻结类型、覆盖率、复杂度、硬编码、死生产 caller 基线和 ratchet | 无阈值下降；新增/改关键函数 complexity≤10；public contracts strict type |
| ZR-105 | 三仓 CI | ZR-101~104 | current-triplet required gate，不再验证陈旧/浮动组合 | 任一仓变更触发受影响三仓；collected/skip delta 受控；三仓 HEAD 精确绑定 |

## Phase 2：Catalog 真只读与并发可靠性

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-201 | company-wiki | ZR-101,ZR-104 | 定义无写能力 `CatalogReader` protocol/connection factory | 构造不存在 DB 不创建；OS read-only 成功；无 mkdir/WAL/DDL/migration/seed/commit |
| ZR-202 | company-wiki | ZR-201 | 在 Reader 上实现 typed identify/query/status/resolve/bundle/health queries | schema mismatch fail closed；query-only property/mutation；无任意写 SQL API |
| ZR-203 | company-wiki | ZR-202 | 将所有只读生产入口从 `CatalogStore` 重接 Reader | CodeGraph production caller gate；Writer initializer 对只读入口 caller=0；旧结果 golden 等价 |
| ZR-204 | company-wiki | ZR-203 | 统一 DB busy/locked、operation lock、timeout、paused reason taxonomy | raw SQLite/CLI/JSON 所有形态映射；非锁错误不得误标 retryable |
| ZR-205 | filing-fetch | ZR-204 | deadline-aware retry 和阶段错误透明转发 | 指数退避、jitter/上限、deadline；最终成功/失败均保留零下载和调用次数；无 sleep 超 deadline |
| ZR-206 | company-wiki + assurance | ZR-203~205 | live writer + 49GB级只读 SLO/压力验收 | READ 场景全绿；p50/p95/p99、锁等待/内存阈值；生产 T2 零写指纹 |

## Phase 3：来源状态机、安全与派生产物谱系

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-301 | company-wiki | ZR-203 | additive source-lifecycle assertion schema + readiness evaluator | shadow only；八阶段可组合；不覆盖历史；consumer requirements 决定 ready |
| ZR-302 | company-wiki | ZR-301 | prompt-injection scanner/reviewer receipt 的生成、缓存与失效 | source/policy hash 绑定；not_reviewed 不伪绿；命中/忽略/过期/篡改场景 |
| ZR-303 | company-wiki | ZR-301,ZR-302 | 统一 safety、identity、artifact、semantic readiness 计算 | 一个 machine decision graph；每个 blocker 有 next action；状态不互相矛盾 |
| ZR-304 | company-wiki | ZR-301 | producer attempt/result、artifact-created journal、ArtifactHandle、唯一 reusable view/validator 与生产 bundle 绑定真源 | source SHA mandatory；失败无artifact也有attempt；区分历史与calls_this_request；`artifact_bindings`/metadata/columns 归一为一条生产读取语义；未知 role/version fail closed |
| ZR-305 | company-wiki | ZR-304 | 在生产 bundle 已消费唯一 view 后，执行 legacy artifact 五桶 dry-run/migration | bindable/hash mismatch/missing bytes/unknown generator/legacy_unbound；apply 后真实 SourceBundle 命中；不猜、不删、幂等、可恢复 |
| ZR-306 | company-wiki + revenue | ZR-304 | SourceBundle role DAG 与最小失效 | 只重算缺失/依赖子树；source bytes/producer/model/prompt 变更的失效范围有 property tests |
| ZR-307 | filing + revenue | ZR-303,ZR-306 | 分阶段 envelope/receipt 即使下游失败也可见 | safety blocked 仍显示 exact reuse/download=0；错误不得吞 handle/bundle/trace |

## Phase 4：跨 roots 通用复用、时效与下载

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-401 | company-wiki | ZR-203 | RootPolicy 3.0 schema/strict loader/snapshot hash | 无隐式默认扩大权限；Dropbox `privacy_class=private_user`；外部 root write target 配置加载即失败；N/N-1 明确 |
| ZR-402 | company-wiki | ZR-401 | adapter registry，把 path/sidecar 差异隔离在 adapter | core 无 root kind/ID 特判；unknown adapter fail；adapter contract mutation |
| ZR-403 | company-wiki | ZR-402 | 泛化 document/location dedupe 与 resolver，并分离全局canonical与本次eligible location | companies/dayu/Dropbox/future_lake 同算法；policy→health→priority→稳定tie-break；读取不写canonical；扫描/配置顺序随机化稳定 |
| ZR-404 | company-wiki | ZR-403 | envelope 带 policy snapshot、候选排除 trace、canonical location rationale | policy/epoch/cohort/source hash 一致；路径脱敏；冲突 fail closed |
| ZR-405 | filing-fetch | ZR-404 | 透明验证任意 policy-allowed root，不再默认 companies allowlist | Dropbox-only/dayu-only 成功；filing 不能扩大 policy；path containment/symlink 负例 |
| ZR-406 | company-wiki | ZR-403 | 正交 local-match 与 provider freshness/coverage planner | exact/equivalent/missing/ambiguous/unusable × current/newer_period/newer_revision/not_published/unknown/future；as_of防泄漏；非自然年/修订去重 |
| ZR-407 | filing + wiki | ZR-406 | authorization-bound GapPlan/CloseGap 支持 missing 与 newer_revision | 无授权 discover/fetch=0；授权 scope/hash/TTL/候选精确；只补真实缺口 |
| ZR-408 | company-wiki | ZR-407 | staging→validate→canonical commit、re-resolve、single-flight/recovery | 下载只写 companies；两并发最多一次 fetch/commit；中断恢复；第二次零下载 |
| ZR-409 | 三仓 | ZR-401~408 | 配置新增 future_lake + 三真实 root 用户旅程 | 只改配置/adapter fixture；产品 core diff=0；EX/LT/DL/IDX/UJ 场景全部绿色 |

## Phase 5：Dropbox 研报、网络研究与按需处理

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-501 | company-wiki | ZR-301,ZR-401 | `broker_research` 文档/准入/metadata contract | publisher/authors/date/entities/security IDs/page count；filename 仅 proposal |
| ZR-502 | company-wiki | ZR-501 | sidecar 与原文角色分离、首页身份验证 | `.source.json` 不成为年报/研报；错误文件名/首页矛盾 fail/review |
| ZR-503 | company-wiki | ZR-501 | 多实体文档与 section/table attribution | 紫金 vs 陕西煤业等比较报告不串实体；全文主实体不覆盖局部归属 |
| ZR-504 | company-wiki | ZR-501 | 页码/阅读顺序保真的 normalized Markdown | 每页 locator；重复页眉脚/两栏/图片页 golden；source hash 绑定 |
| ZR-505 | company-wiki | ZR-504 | table artifact：行列、merged cells、脚注、单位、截图 locator | 代表性七份 PDF golden table cell/row/column/footnote fidelity 达阈值 |
| ZR-506 | company-wiki | ZR-503~505 | section/chunk/tag/fact assertion | 不跨 entity/table；actual/estimate/target、period、unit、ownership 等必填；可逆回源 |
| ZR-507 | company-wiki | ZR-306 | `ProcessingDemand` API、幂等 dedupe、成本/隐私授权和 receipt | consumer 不改全局 priority；同需求合并；完成后第二次 producer=0；private_user 未授权不得发往外部 LLM |
| ZR-508 | company-wiki | ZR-507 | scheduler 公平性、deadline、重试与 cost budget | filing/研报不互相饿死；priority inversion/failure/restart 有界；无重复 LLM |
| ZR-509 | company-wiki | ZR-501~506 | 官方公告/新闻/HTML capture 的身份、快照、索引与处理 | URL 200/hash 但 title/entity错必须拒；有效来源可保存→索引→MD/chunk/tag |
| ZR-510 | company-wiki + revenue | ZR-503~509 | 七份紫金 Dropbox PDF + 两个官方 HTML 真实只读 canary | 7/7 metadata/MD/table/chunk/tag；长江多实体正确；检索召回/精确率与零错归门 |

## Phase 6：矿山事实、运营模型与会计桥

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-601 | company-wiki | ZR-506 | AssetFact schema、asset type、canonical alias | 单矿/矿群/公司聚合体/项目分开；别名有时效和证据；循环/碰撞拒绝 |
| ZR-602 | company-wiki | ZR-601 | resource/reserve/grade/capacity/permit facts + basis | resource≠reserve；100%/权益/并表、标准、measurement date 必填；单位归一 |
| ZR-603 | company-wiki | ZR-601 | ownership/consolidation timeline 与地区层级 | Kamoa/Porgera 不二次乘权益；收购生效日前后不同；country/region 可检索 |
| ZR-604 | company-wiki | ZR-602,ZR-603 | 从表格抽取、冲突保存与人工 review | Bisha kt/t、3Q 状态、锂合计差额等冲突不静默覆盖；双 assertion+resolution status |
| ZR-605 | revenue + company-wiki | ZR-604,ZR-610 | MineYearOperation 输入合同 | volume/grade/recovery/payable/product/period/scenario；必须遵守已批准矿业 ADR；缺字段有 gap，不默认为0 |
| ZR-606 | revenue | ZR-605 | 商业量价层：price/payability/TC-RC/premium/byproduct/FX/royalty | 每个变量有来源/假设/期限；多商品与副产品不重复计价；敏感性可重算 |
| ZR-607 | revenue | ZR-603,ZR-606 | ownership/consolidation/internal flow/accounting bridge | equity vs consolidation、内部转冶炼/贸易、gross/net、elimination 可追踪 |
| ZR-608 | revenue | ZR-607 | asset→external segment→company reconciliation 与诚实 fallback | 容差内才标 modeled；不闭合则回退到分部并列 gap；禁止产量×价格伪收入 |
| ZR-609 | 三仓 | ZR-604~608,ZR-610,ZR-611 | 紫金 pilot + 第二家不同结构矿企泛化 | 紫金主要资产覆盖、逐矿可回答范围清楚；第二家公司无需产品硬编码 |
| ZR-610 | revenue + accounting reviewer | ZR-604 | 冻结通用矿业数据、单位、ownership/consolidation/internal-sales ADR | 无产品代码；独立会计review accepted；明确逐矿贡献是模型估计、不是披露事实 |
| ZR-611 | revenue | ZR-605~608,ZR-610 | 通用多矿合成E2E：控股、权益法、多金属、内供、跨币种、爬坡、gap、residual | 每类formula/reconciliation/mutation可重算；生产代码公司/矿名hardcode=0 |

## Phase 7：revenue-forecast 契约、模型和发布闭环

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-701 | revenue | ZR-101 | schema machine truth 统一 runtime/schema/docs/linter/generator | 3.7 单一版本；capture 10键一致；漂移 patrol 反例失败 |
| ZR-702 | revenue | ZR-701 | generator 产出最小与矿业模板，并运行真实引擎 | management/claims/recognition/dimensions 全合法；validate_document + draft full run 绿色 |
| ZR-703 | revenue | ZR-701,ZR-702 | linter 成为快速子集且不宣称引擎等价；文档/样例同步 | linter clean+engine fail 的已知负例保留；docs examples 自动执行 |
| ZR-704 | revenue | ZR-701 | 拆纯 `prepare_forecast` 并实现真正零写 `validate-only` | 不调用 formal/register/sign/network/subprocess/write；registry/filesystem before/after不变；formal payload数值零回归；help准确 |
| ZR-705 | revenue | ZR-701 | draft/formal validate+render+output-mode/receipt 闭环 | draft render成功且不发布；formal一次注册；篡改任一 hash/gate fail；N/N-1测试 |
| ZR-706 | revenue | ZR-307,ZR-507 | source-preparation 消费阶段 envelope、bundle、ProcessingDemand | 已处理0 producer；pending可等待/返回；downstream fail仍保留reuse/download receipt |
| ZR-707 | revenue | ZR-608,ZR-610,ZR-711 | 扩展模型组合与 schema 表达 mixed recognition/gross-net | mine×commodity×product + segment bridge；贸易/其他不靠单一错误 presentation 近似 |
| ZR-708 | revenue | ZR-707 | 重验不可变snapshot/backtest基础接线 | 已有能力若当前triplet全绿则already_satisfied；否则修复；accuracy record实际可被forecast消费 |
| ZR-709 | revenue + 三仓 | ZR-705~708,ZR-710~713,ZR-609,ZR-611 | 紫金五年预测用户旅程终验 fixture | 自动复用财报/研报，补齐依据可解释；mine/product贡献与分部勾稽或诚实gap；draft可渲染、结果可重放 |
| ZR-710 | revenue | ZR-705 | formal publication prepare/commit 原子性与恢复 | output/registry/sign/rename/进程中断故障无静默孤儿；append-only；成功精确一次committed |
| ZR-711 | revenue | ZR-701,ZR-610 | additive schema 3.8 opt-in 与3.7兼容/converter | 3.7 canonical hash零回归；3.8 operating units/consolidation；converter只加gap不猜值；flag可回滚 |
| ZR-712 | revenue | ZR-708 | 版本化 ConfidencePolicy 与反博弈 | duplicate/split/plug/zero-impact/one-observation/wrong-record mutations全杀；rating caps可重算 |
| ZR-713 | revenue | ZR-708,ZR-712 | 紫金 rolling-origin 历史回测 | 严格as-of无future actual；company/segment/mine-volume分层；四层immutable hashes；无法形成则触发cap |

## Phase 8：真实 E2E、故障与可移植性

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-801 | assurance | 各功能 phase | 合并旧95场景与 READ/BR/MINE/REV 新场景到 machine registry | 无重复/遗漏；owner/oracle/budget/tier/timeout/freshness 齐全；本计划 `scenario_matrix.md` |
| ZR-802 | assurance | ZR-801 | 组合旅程：existing/partial/missing/stale/conflict across roots | 从 revenue 入口；三进程；第二次调用；阶段 receipt 与调用预算准确 |
| ZR-803 | assurance | ZR-801 | chaos/property/mutation：锁、中断、磁盘、篡改、顺序、时钟 | critical mutation 100% kill；普通阈值冻结；故障后幂等恢复 |
| ZR-804 | 三仓 | ZR-802 | Windows中文/空格/大小写、Linux、installed skill | golden trace 语义一致；UTF-8 stdio；无 sibling 固定路径 |
| ZR-805 | filing + assurance | ZR-407,ZR-408 | CN/HK/US T3 首次下载+二次零下载 | 临时 wiki；真实 provider；网络缺失 blocked；下载/commit严格授权 |
| ZR-806 | assurance | ZR-510,ZR-609,ZR-709 | 真实 T2 三 root、broker、artifact、mine、forecast 样本 | 生产 catalog/source roots 零写；样本唯一/新鲜；用户旅程全部绿 |

## Phase 9：动态审核与全面代码质量

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-901 | 三仓 CI | ZR-801~804 | PR current-triplet required checks | T0/T1/quality/architecture/receipt/mutation；无 skip；旧 pin 仅N-1 |
| ZR-902 | assurance ops | ZR-806 | 实际调度每日 Windows T2 | schedule/runner/权限/原子报告/<=24h freshness/release消费全证明；不仅是脚本存在 |
| ZR-903 | assurance ops | ZR-805 | 实际调度每周/发布前 T3 | <=7d；凭据/网络 blocked告警；provider contract drift 可见 |
| ZR-904 | assurance | ZR-902,ZR-903 | SLI/dashboard/release gate | reuse/download avoidance/artifact/consumer-ready/broker fidelity/misattribution/mine conflict/forecast/backtest/render 指标 |
| ZR-905 | assurance | ZR-904 | 审核机制自测试 | 陈旧、错triplet、缺样本、半报告、指纹变化、指标恶化、schedule未运行均让 release 红 |
| ZR-906 | 三仓 | ZR-104,全部实现 | hardcode/dead path/complexity/type/coverage/encoding 最终 ratchet | root特判0、关键legacy caller0、critical coverage阈值、Windows错误0；required check |
| ZR-907 | 三仓 docs | ZR-701,ZR-906 | contract/doc/sample/skill-package drift patrol | schema版本/字段/引用文件/installed skill hash 不一致即CI失败 |

## Phase 10：渐进迁移与发布

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-1001 | release owner | Phase 0~9 accepted | 生产副本、容量、备份可读性、回滚命令预飞 | integrity/fingerprint、耗时/空间预算、用户授权；未满足不进入窗口 |
| ZR-1002 | company-wiki | ZR-1001 | Reader 先上线，writer保持原行为 | read shadow/golden/SLO；rollback路由；无 schema/data 迁移 |
| ZR-1003 | company-wiki | ZR-1002 | lifecycle/safety/RootPolicy shadow assertions | 两动态周期 diff 全解释；active response不变；rollback仅关flag |
| ZR-1004 | company-wiki+filing | ZR-1003 | companies→dayu→Dropbox→future root 小 cohort | 每 root T2/UJ；external write=0；同 request rollback恢复 |
| ZR-1005 | company-wiki | ZR-1003 | legacy artifact 分桶与最小 canary backfill | 先dry-run；不可证明不绑定；幂等/resume；零删除；artifact reuse T2 |
| ZR-1006 | company-wiki | ZR-1004,ZR-1005 | broker processing demand 最小 cohort | 七份紫金先1→3→7；质量门/成本/SLO；失败不污染旧 artifact |
| ZR-1007 | revenue | ZR-1006,ZR-609 | mine facts/model shadow 与旧分部模型对比 | 差异归因、reconciliation、backtest；不自动替换生产预测 |
| ZR-1008 | revenue + 三仓 | ZR-1007 | source/revenue 新链 cohort cutover | 用户旅程、draft/formal、SLO、side effects、rollback；观察期 |
| ZR-1009 | 三仓 | ZR-1008 | legacy 路由/代码删除 | ≥2动态周期 zero-hit、CodeGraph caller=0、N-1结束批准；删除后全矩阵/回滚绿 |

## Phase 11：独立终验和关闭

| ID | Owner | 依赖 | 原子目标 | Mandatory 证据/退出条件 |
|---|---|---|---|---|
| ZR-1101 | closure validator | 全部mandatory ZR | 机器 closure gate | 无 pending/blocked/known-gap 被误关；所有 receipt/paths/hashes/freshness有效 |
| ZR-1102 | 独立 reviewer | ZR-1101候选 | 对抗式三仓代码/架构/旁路审查 | 不复用实施者结论；生产 reachability、硬编码、测试孤岛、伪计数全部复核 |
| ZR-1103 | 独立 reviewer | ZR-1102 | 真实用户旅程复验 | companies/dayu/Dropbox、旧+新、已处理、broker/mine、CN/HK/US、Windows中文路径 |
| ZR-1104 | release owner+reviewer | ZR-1103 | 观察期与真实 rollback drill | 连续7次 Daily T2、2次 Weekly T3、1次 Monthly 紫金 shadow、1次告警自检；legacy hit=0；一次 cohort rollback/re-activate；自然时间门不得人工豁免 |
| ZR-1105 | closure owner | ZR-1104 | 生成最终需求—证据 closure ledger 与旧计划状态投影 | 六目标逐项 machine pass；旧计划只读映射；validator exit 0 后整体才 complete |

## 依赖主链

```text
ZR-001..004
 -> ZR-101..105
 -> ZR-201..206
 -> ZR-301..307
 -> ZR-401..409
 -> ZR-501..510
 -> ZR-601..611
 -> ZR-701..713
 -> ZR-801..806
 -> ZR-901..907
 -> ZR-1001..1009
 -> ZR-1101..1105
```

允许的受控并行：Reader 完成后，来源状态机与 RootPolicy schema可分支；broker 处理与 revenue contract 可在各自前置冻结后并行；scenario registry、共享 schema、迁移和生产 rollout 始终单 writer。
