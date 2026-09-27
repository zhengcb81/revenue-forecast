# 项目总目标、当前痛点与成功定义

> 这是下一轮实施的“北极星”文档。任何工作单元若不能明确推进本文某个目标，就不得进入主线。

## 1. 一句话目标

把 `company-wiki`、`filing-fetch`、`revenue-forecast` 建成一条可泛化、可审计、可持续验证的研究资料与收入预测链：先在所有获准的本地 data-lake roots 中复用可信原文和已处理成果，只在确有缺口且得到授权时下载；随后按需求补处理并生成可回溯的公司/分部/资产级收入预测。

紫金矿业只是复杂真实 canary，不是产品特例。最终还必须通过第二家结构不同的矿企和一家非矿业公司，且产品代码中公司名、证券代码、矿名、Dropbox/dayu/companies 名称硬编码为零。

## 2. 用户可感知的最终行为

一次预测请求必须逐阶段回答：

1. 找到了哪些逻辑文档；分别位于哪些获准 roots；本次真正选择了哪个 location。
2. 本地覆盖了哪些期间和修订版；provider 是否存在更晚期间或同期间新版。
3. 哪些原文被精确复用，哪些只做内容等价复用；为什么不是另一个候选。
4. 是否下载；若下载，授权、候选、字节、提交位置、调用次数是什么；若不下载，依据是什么。
5. 文档是否经过身份、安全、Markdown、表格、切片、标签、摘要、事实抽取；哪些可直接复用，哪些必须补处理。
6. 处理需求是否真的进入 worker、是否去重、是否完成；第二次调用是否零重复解析/LLM。
7. 预测采用哪些来源、运营事实、分析师假设和压力情景；来源覆盖到哪一年。
8. 对矿业公司，哪些矿/矿群、商品、产品、地区、资源/储量、产量、权益和并表口径可用；逐矿收入能否与分部及集团外部收入勾稽。
9. 若任何层失败，返回已完成阶段的事实和精确 blocker，不能把“FY2025 已复用且零下载”吞成一个泛化 fatal。
10. 同一请求再次执行时，只重算真正失效的节点，不从头读取和处理全部材料。

## 3. 三仓边界

| 仓库 | 唯一职责 | 明确禁止 |
|---|---|---|
| `company-wiki` | 通用 data lake：root policy、物理发现、document/location identity、freshness、来源生命周期、安全、派生产物、处理需求、broker/网页语义、事实和谱系 | 预测收入；把外部 root 当写目标；按消费者复制第二套目录逻辑 |
| `filing-fetch` | 薄财报编排：请求校验、调用 catalog、判断 gap、按授权调用市场 provider、staging/canonical commit、透明传递各阶段 receipt | 自建 root allowlist、重新判定 artifact/safety、通用研报下载、默认假设只有 `companies` 可复用 |
| `revenue-forecast` | 研究消费者：声明所需来源/产物/事实，构建可审计分部或资产模型，情景、回测、置信度、draft/formal 发布 | 直接遍历个人目录、维护第二个索引、私自下载、把资源量当储量、用产量×价格冒充可确认收入 |

## 4. 当前不能关闭的具体痛点

### P01 验收系统会产生假绿

- 旧计划登记为 66/71，但严格 current-triplet 独立证明为 0/71；31 项有可保留实现、26 项被当前行为反证、9 项证据陈旧、5 项 pending。
- scenario coverage 主要证明 ID 在测试或 receipt 文本中出现，不证明指定层级真的执行并通过。
- closure 漏检 filing-fetch receipt、缺失 receipt、reviewer/hash/revision、R0～R9、精确 current triplet、dirty/upstream、命令重放和证据新鲜度。
- `accepted` 用字符串包含判断；状态表有非法状态文本和自依赖。

### P02 “只读查询”实际会初始化写型数据库

- 生产 resolver 构造 `CatalogStore` 时会 `mkdir`、普通连接、WAL、DDL/migration/commit。
- 独立 readonly canary 是旁路，不等于生产调用链。
- 真实使用已出现 raw `database is locked` 被包装成 fatal；live worker 并发下的有界重试和阶段证据未闭合。

### P03 data lake root 泛化只到了一半

- RootPolicy/adapter/sidecar/v2 scanner 有资产，但生产配置仍为 v1，scanner 默认仍走 v1。
- Dropbox 和 dayu 的文件已被扫描，不等于消费者能使用。
- filing-fetch 没收到完整 policy snapshot/eligible roots，`validate_handle` 回退到 `<wiki>/companies` containment；因此物理排他的 Dropbox-only/dayu-only 生产链不可达。
- global canonical location 与“本请求获准且健康的 location”没有分离。
- 同一请求内部还有策略旁路：CLI resolve 显式加载 runtime policy，但 acquisition/close-gap 内部可用缺省 `SourceResolver(..., runtime_policy=None)` 回到 v1/legacy；最终 envelope 又可能附当前 policy hash，形成“v1结果披着v2回执”的假一致。
- 审查时从当前 `source_catalog.yaml` 导出的 RootPolicy hash 与 runtime snapshot 的 `policy_hash` 不相等，且导出的三个 root 没有显式 `reusable_for_filing`；当前 activation 因而不是可从配置复算的不可变授权快照。
- 实库存在21个 `dayu_portfolio` 独有的 active filing（15 annual、3 semi、2 quarterly、1 regulatory），不是抽象边界问题：它们会被当前 filing-fetch 的 companies containment 拒绝。Dropbox 的少量“独有 filing”中至少4个标题以 `.pdf.source` 结尾且日期为空，属于sidecar JSON被v1扫描为年报/半年报的假阳性，证明catalog同时有漏用与污染。
- v2 metadata生产覆盖也远未达到全量：当前 verified+active assertions 只有少量canary，而resolve active/legacy off与ensure/close-gap默认v1+bridge并存，可能让同一请求前后看到不同文档集合。

### P04 freshness 与最小下载不完整

- `newer_revision` 已存在于 GapPlan，却没有进入 filing 的 actionable close-gap；同期间更正版可能不下载。
- close-gap 只取一个 missing item；revision 时间语义仍可能用 provider ID 字典序近似。
- 缺少 exact/equivalent/missing/ambiguous/unusable 与 current/newer-period/newer-revision/not-published/unknown 的正交矩阵。

### P05 已处理成果的复用不可信

- 旧 normalized/summary 大量缺 `source_sha`/schema；validator 对空 source hash 反而放行。
- artifact backfill 写 shadow binding 表，生产 bundle 不读它。
- producer events 由 artifact INSERT/role 推断，不是 parser/LLM attempt、cache hit、failure、retry 的真实 journal。
- role DAG/最小失效主要存在于测试 seam；缺失产物时 revenue 只返回“应处理”事件，不真正提交 ProcessingDemand。

### P06 安全状态与消费状态割裂

- 紫金年报在 filing 层精确复用、零下载，但 `prompt_injection_status=not_reviewed` 阻塞 revenue-ready。
- 生产安全 reviewer 写入入口几乎只有测试调用；绝大多数实库文档没有安全 assertion。
- 下游失败会遮蔽上游复用/下载事实，用户误以为全链都失败。
- 风险已不是纯理论：active Dropbox 文档约有800份 completed summary，其中649份标记为 `source_catalog_llm_summary`；metadata显示529份使用 `minimax/MiniMax-M3`、120份使用 `mimo/mimo-v2.5-pro`，但这些文档当前仅1份有关联的 prompt-injection review receipt。Dropbox root又未显式声明 privacy class，worker选择也未按root privacy/receipt过滤。catalog不能单独证明历史网络去向或当时授权状态，必须先审计 provider/model/egress receipt，并把 private/rights/LLM egress 设为P0数据治理门。

### P07 Dropbox 券商研报尚不是一等语义来源

- 实库虽有 PDF、page/span/table-index 基础，但七份重点研报的 published date、可消费 artifact、tag/fact 均未闭环。
- JSON sidecar 被当成独立 primary；v2 sidecar adapter 没有生产切入。
- 无正式的 broker identity、多实体 section/table attribution、保真表格 artifact、chunk/tag/fact、privacy/rights gate。
- 长江比较报告绑定 Unresolved，证明单实体默认会污染或丢失多实体内容。

### P08 revenue 输入、验证和发布合同漂移

- runtime schema 为 3.7，生成器、文档、帮助仍有 3.6；capture 实际 10 键而文档曾写 9 键。
- generator 返回成功但其产物被 linter/engine 拒绝：缺 `management_targets`、非法状态、claim/dimension/recognition/history/hash 等错误。
- `--validate-only` 会走 formal 并写 publication registry。
- draft receipt 与公共 renderer 的 gate contract 不兼容。
- formal registry 先 append、输出后写，缺 prepare/commit/recovery/idempotence，可能留下孤儿或重复发布。

### P09 矿业预测只能做分部 fallback，不能可信回答逐矿问题

- 现有 `reserve_depletion` 是有用公式底座，但没有 mine×commodity×product×year×scenario。
- 缺 asset identity/地区、resource 与 reserve 分离、ownership timeline、consolidation/equity method、payability、TC/RC、FX、byproduct、内部流转和抵销。
- 没有 mine→external segment→group accounting bridge，不能把“产量×价格”直接称为收入。
- 紫金资料没有披露逐矿 2026～2030 营收；系统必须能诚实输出 data gap/模型估计边界，而不是伪精确。

### P10 E2E 与动态审核没有覆盖真实用户旅程

- companies-only、临时 catalog、fake PDF、预置 rows/events 很多；Dropbox/dayu-only、同期间修订、实际 worker、真实多实体表格、逐矿勾稽没有全链证据。
- 某些 E2E 把结构化失败也算 runner 成功，或绕过 revenue→filing。
- Windows 中文/长路径和默认 GBK subprocess 已出现失败；不能以环境噪声整体忽略。
- 三仓 workflow 只有 push/PR，无 schedule；Daily/Weekly 脚本没有真实 scheduler、报告新鲜度、告警送达和自然时间 soak。

### P11 代码质量门冻结了债务，没有消除债务

- root/公司/路径硬编码仍存在于 scanner、canonical writer、CLI、SLO、replay 与动态审核。
- 高复杂度阈值主要冻结在 150/140/103 等高位；部分命令允许 `|| true`。
- compatibility manifest 陈旧，CI 可能拉旧 sibling 组合而掩盖 current HEAD 回归。
- 旧 R9 仍有四个明确 RED；在新链完成前删除 legacy 会失去回滚。

## 5. 不推倒重来的资产

以下只作为“候选资产”，不继承旧 accepted 状态：RuntimePolicy/Activation/CAS/rollback、RootPolicy/adapter 骨架、normalized identity/resolver、GapPlan/authorization/staging/single-flight、ArtifactHandle/SourceBundle/selector、page-aware parser/spans、IsolatedLake/三进程 runner、receipt/mutation/quality 工具、类型/覆盖率/复杂度 ratchet、T2/T3/dashboard 脚本、backtest 数学和 95 个业务场景词汇。

每项必须在当前 triplet 先跑既有测试，再跑能杀死已知旁路的 mutation；通过后标 `already_satisfied`，否则进入最小修复。禁止为了“统一”重写已经可靠的公式或事务机制。

## 6. 六个最终成功问题

最终 closure 必须逐项给出 machine evidence，任何一个为否都不能 complete：

1. 重构是否完全成功，legacy 是否在观察期后安全移除？
2. Dropbox/dayu/未来 root 是否在功能层从 revenue 入口真实复用？
3. 复用、时效、下载、处理、broker、网页、预测、发布和矿业目标是否全部实现或以明确的受控 data gap 表达？
4. 是否存在真正运行的 PR/Daily/Weekly/Monthly/发布前动态审核，并能自证没有停摆或复用旧绿？
5. E2E 是否覆盖真实 roots、文档状态、provider、worker、故障、Windows 和跨行业泛化？
6. 产品核心是否无 root/company/path 特判、无不可达双实现，复杂度/类型/文档/契约是否持续改善？

“测试很多”不是答案；每项必须链接到 current triplet、真实场景结果、独立 oracle、side-effect ledger、review receipt 和证据新鲜度。
