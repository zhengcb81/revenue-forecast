# 紫金矿业未来五年营收预测与技能调用对抗式审计

> 信息截止日：2026-08-12。运行开始于 2026-08-12，最终整理于 2026-08-13。  
> 业务输入始终只有“紫金矿业，预测未来五年收入增速”；Dropbox、矿山、预处理等用户关注点没有追加给原生技能，只作为旁路观察项。  
> 本报告是调查和 draft 研究产物，不是 formal publication，也没有实施产品修复。

## 一、结论先行

### 预测结果

| 情景 | FY2026营收 | FY2027营收 | FY2028营收 | FY2029营收 | FY2030营收 | FY2025→2030 CAGR |
|---|---:|---:|---:|---:|---:|---:|
| Low | 3,542.25亿元 | 3,643.43亿元 | 3,768.49亿元 | 3,697.94亿元 | 3,697.94亿元 | 1.16% |
| Base | 4,042.30亿元 | 4,435.69亿元 | 4,816.88亿元 | 4,997.03亿元 | 5,164.09亿元 | **8.15%** |
| High | 4,401.51亿元 | 5,036.22亿元 | 5,643.68亿元 | 5,990.61亿元 | 6,278.29亿元 | 12.46% |

Base 同比增速依次为 **15.80%、9.73%、8.59%、3.74%、3.34%**。以 20%/60%/20% 分配 Low/Base/High 的分析师概率后，FY2030 概率加权营收约 **5,093.70亿元**，隐含 CAGR **7.85%**。

这组数字通过了 schema 3.7 输入校验、完整 draft 计算、强输出校验和第二次确定性重算；但引擎置信度只有 **42/100（low）**。核心原因是四个分部全用 direct_growth 回退模型，显式运营模型占比为零，缺商品价格曲线、矿山收入桥和历史回测。

### 用户六个重点的状态

| 问题 | 状态 | 简明结论 |
|---|---|---|
| 1. 是否复用了已下载财报 | **文件层通过；端到端不通过** | filing-fetch 第三轮内部复用 FY2025 exact 文件、零下载；但共享 prompt_injection_status=not_reviewed，revenue-ready source record 被拦截 |
| 2. 是否下载更多；依据是什么 | **没有下载** | 本轮从未授权 allow-download，且最新 FY2025 exact 年报已存在；决定依据是权限+期间/身份命中，不是模型判断“资料已经够了” |
| 3. 是否研究矿种、国家、储量和逐矿营收 | **部分满足** | 主动研究了主要矿种、矿山/公司、国家、持股、资源量和2025产量；没有完整逐矿储量，也没有任何来源披露逐矿五年营收，因此没有伪造 |
| 4. 财报/Dropbox是否有MD、切片、标签，可否当场处理 | **财报部分可读；Dropbox不满足** | 年报有 partial MD、summary和大量 spans，但绑定不合格；七份研报全部零 artifact/span/tag；技术上可处理，本轮未改 worker 或优先级 |
| 5. 网络搜索、新闻下载/索引/处理/保存 | **搜索发生；共享沉淀未发生** | 搜索并阅读多份官方材料；仅两个有效 HTML 保存到隔离审计目录，未进入 company-wiki、索引、MD、切片或标签 |
| 6. 其他问题 | **发现多项结构缺陷** | 真只读查询不存在、锁错误错分、旧 artifact 谱系断裂、generator 无效、validate-only 有写副作用、draft renderer 不可用等 |

## 二、预测到底建了什么

### 基期与对账

- FY2024 营收：3,036.39957153亿元。
- FY2025 营收：3,490.79082852亿元，同比增长 14.96%。
- FY2025 四个**外部收入**报告分部精确对账：

| 分部 | FY2025A | Base FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---:|---:|---:|---:|---:|---:|
| 矿产品 | 1,099.78亿元 | 1,429.71亿元 | 1,687.06亿元 | 1,940.11亿元 | 2,037.12亿元 | 2,118.60亿元 |
| 冶炼产品 | 1,658.59亿元 | 1,824.45亿元 | 1,915.67亿元 | 2,011.45亿元 | 2,071.79亿元 | 2,133.95亿元 |
| 贸易 | 292.13亿元 | 303.81亿元 | 309.89亿元 | 316.09亿元 | 322.41亿元 | 328.85亿元 |
| 其他 | 440.30亿元 | 484.33亿元 | 523.08亿元 | 549.23亿元 | 565.71亿元 | 582.68亿元 |

采用外部收入而不是各分部总收入很重要：FY2025 内部销售约 2,349.70亿元并被全额抵销。直接使用矿山产量、冶炼量和贸易额相加会严重重复计算。

### Base 增长率假设

| 分部 | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 | 依据边界 |
|---|---:|---:|---:|---:|---:|---|
| 矿产品 | 30% | 18% | 15% | 5% | 4% | FY2026–2028参考官方产量规划；以后无来源衰减 |
| 冶炼产品 | 10% | 5% | 5% | 3% | 3% | 历史分部基数与保守恢复；无完整量价桥 |
| 贸易 | 4% | 2% | 2% | 2% | 2% | 历史近乎持平且总额/净额口径不透明 |
| 其他 | 10% | 8% | 5% | 3% | 3% | FY2025高基数后逐步正常化 |

FY2026 Base 低于官方 Q1 营收同比 +24.79%，避免把季度金属价格和量价共振机械年化。FY2029–2030 明确是 source-free analyst fade，不把只覆盖 FY2028 的管理层规划伪装成更长期目标。

### 为什么没有按每座矿预测收入

官方和券商材料确实能提供很多矿山事实，但从矿山产量到集团外部收入还需要：逐矿年度销量、品位与回收率、可支付金属、产品形态、TC/RC、伴生品分摊、特许权费、实际售价/折价、汇率、持股、并表方式、内部销售和抵销。

年报按“矿产品、冶炼、贸易、其他”披露外部收入，不按每座矿披露外部客户收入。只做“资源量或产量×金属价格”既不能处理 Kamoa/Porgera 的权益口径，也不能对账冶炼、贸易和内部抵销。因此本次宁可明确留下数据缺口，也不输出虚假的逐矿精确数。

完整主要矿山矩阵见 [mine_coverage_matrix.md](mine_coverage_matrix.md)。

## 三、filing-fetch：复用了什么，为什么仍然失败

### 三次真实调用

1. 第一次，无下载授权：company-wiki resolve 在 restricted DB 上报 attempt to write a readonly database。
2. 第二次，同一请求、仍无下载授权：等待约 60 秒后报 database is locked，且被错误包装成 fatal/non-retryable。
3. 第三次，同一请求：filing-fetch 已返回内部 handle/envelope；revenue 随后因 prompt_injection_status=not_reviewed fail closed。

第三次可以从代码和 journal 联合证明为 outcome=reused_existing、download_events=0：本轮 acquisition journal 没有追加，而 read-only exact/equivalent resolution 的结构性 envelope 固定为零下载。FY2025 与 FY2024 PDF 的实际 SHA-256 分别为：

- 01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d
- 004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89

两者都与 catalog document ID 和 .source.json 完全一致，并同时存在 companies/Dropbox location。历史 journal 证明它们最初分别在 2026-07-31、2026-08-01 经 cninfo 下载；这不是本轮行为。

### 必须拆成五层看

| 层次 | 结论 |
|---|---|
| 文件发现/filing resolution | 成功 |
| 本轮新下载 | 0 |
| 共享安全审查 | 未完成 |
| 已有派生 MD/summary 可信复用 | 不满足当前绑定合同 |
| revenue-ready source record | 失败 |

所以一句“已经复用”或“没有复用”都不准确：**文件层确实复用了，端到端消费层没有成功。** 完整事件见 [trace/filing_fetch_events.md](trace/filing_fetch_events.md)。

### 下载更多文件的决策依据

- 用户没有给本轮开放下载授权；请求和命令都未包含 allow-download。
- as-of 2026-08-12 的最新年度报告 FY2025 已 exact 命中，期间和身份都满足；filing-fetch 没有理由再下载一份。
- filing-fetch 的职责是监管财报，不负责券商报告或新闻。
- 本轮没有“因为模型还缺价格曲线或逐矿营收就擅自下载更多”。资料是否充分被记录为 data gap，而不是反向扩大下载权限。

## 四、已有财报处理成果能不能复用

| 文档 | normalized MD | summary | evidence spans | source binding | 结论 |
|---|---|---|---:|---|---|
| FY2025年报 | partial | completed | 14,118 | source_sha256=null；无 producer event | 人工可读，生产契约不可复用 |
| FY2024年报 | partial | completed | 16,986 | source_sha256=null；无 producer event | 人工可读，生产契约不可复用 |

人可以很快从 FY2025 summary/MD 找到集团营收、矿种、储量资源汇总、2026/2028 产量计划和四分部外部收入；但逐矿资源/储量大表被拆成大量 flat cells，矿名、国家、资源量、储量、品位和年限容易错列。

更关键的是，新 SourceBundle 合同要求 source hash 和 producer/schema/model/prompt 绑定。旧 artifact 缺 source_sha256 和 producer events，导致“已经付过解析/LLM成本且人类可读，但生产 consumer 必须 fail closed”的迁移断层。不能通过放宽校验解决；应做可审计 backfill/migration。

## 五、Dropbox 七份券商研报

七份原 PDF 7/7 hash 与 catalog 一致、未加密、可抽取；六份含有高价值的逐矿资源/储量/产量表。但它们全部：

- published_date=NULL
- artifact_count=0
- evidence_span_count=0
- metadata_assertion_count=0
- 没有 MD、summary、section、页码级切片、结构化表格或矿山语义标签

长江证券报告还绑定 unresolved entity，且其中的 2028E 表是陕西煤业 ROE，不是紫金预测；如果只做关键词检索会发生严重错归。

最有价值的几份是天风 2024-12、国盛 2025-01、国联民生 2026-03：它们提供逐矿权益、资源/储量、品位、证照、历史/未来产量等表格。但公司营收通常只预测到 2026–2028，没有逐矿营收，也没有到 2030 的公司营收。

完整逐份页码和风险见 [dropbox_broker_report_audit.md](dropbox_broker_report_audit.md)。

### 能不能当场处理或提 worker 优先级

技术上能从原 PDF 提取内容，当前也存在 worker/normalize 管线；但没有经过验收的“consumer 以 source SHA + 所需字段提交幂等优先处理请求”的接口。直接改全局 worker priority 会把调查变成产品状态修改，并与正在处理约 20,020 个 Markdown backlog 的 worker 竞争。

因此本次没有现场生成共享 MD、没有入队、没有提优先级。正确方向是需求队列和回执，而不是让 revenue skill 直接操纵 worker。

## 六、网络补缺到底发生了什么

原生研究主动搜索并阅读了官方：2025 Results、Reserves and Resources、2026 Q1、H1运营更新、Allied Gold交易变更、Norton投产、年度业绩说明会/演示入口等。

### 对预测有用的新增认识

- 官方 2026/2028 分矿种产量规划支持矿产品增长，但明确不构成实际产量承诺。
- Q1 营收同比 +24.79%，矿产金增长而 Kamoa 相关铜产量承压，说明不能只保留正面证据。
- H1 金、锂增长强，Kamoa 是反证；H1 利润增长不能替代收入增速。
- Allied Gold 全资收购终止，改为约 9.2% 战略持股，不能把其矿山收入并表。
- Norton 2Mtpa破碎系统投产是具体但集团影响较小的执行证据。

### 保存/索引状态

- company-wiki：没有下载、没有 ingest、没有索引、没有 MD、没有切片、没有标签。
- 隔离审计目录：有效保存 2025 Results 和 Norton 两个 HTML snapshot，用于 hash/claim；它们不是共享数据湖来源。
- Q1/H1/Allied Gold：仅浏览器事件，没有本地快照；因此没有绑定进强契约参数。
- 原拟 strategy URL 直连后返回了完全无关的“紫金中学运动场扩建工程”页面；该快照被排除并保留为 source identity 负例。

完整事件见 [trace/web_events.md](trace/web_events.md) 与 [trace/source_review.md](trace/source_review.md)。

## 七、额外发现的系统问题

### P0：复用链可靠性

1. CatalogStore.__init__ 对 resolve/query/status 也执行 WAL、DDL、migration、fingerprint seed 和 commit；所谓 read-only reuse 不是操作系统层面的只读，并与后台 worker 抢写锁。
2. 原始 sqlite3.OperationalError: database is locked 没有归一到 catalog_locked，导致技能声称可重试、真实却 fatal。
3. 提示注入审查、artifact binding、producer event 和派生文件是四套不一致状态；旧资料可人工使用却不能生成可信复用回执。
4. 顶层 revenue 错误吞掉了上游已成功 reuse/零下载事实，没有给用户可见的分阶段 redacted receipt。

### P0：revenue 工具自身契约不闭合

1. 官方 input generator 缺 management_targets，claim 类型/字段错误，direct model/driver dimension 错配，recognition 不完整，管理状态使用非法值；现有测试只过弱 linter，没有过真实引擎。
2. --validate-only 实际调用 formal run_forecast 并写 publication registry，和 CLI 文案“without writing”冲突。
3. 合法 draft 已通过强校验，但 render_markdown 再走 formal-only receipt validator，报 publication_receipt gate_ids mismatch；current-schema legacy render 也被拒绝，导致“能生成 draft JSON、不能合法渲染 draft”。
4. run_forecast docstring 声称 top-level 会有 formal_output_mode=draft，实际该值只在 publication_receipt 内；本次 receipt 最初读顶层得到 null。
5. 技能包缺它自己引用的 session checklist 和 TRUST_BOUNDARY template；仓库副本存在，说明发布打包完整性校验不足。

### P1：数据湖语义质量

1. Dropbox .source.json sidecar 被当成独立 annual report，甚至优先生成 artifact，而真正券商 PDF 未处理。
2. 网络 URL 的 HTTP 200/hash 不能证明文档身份；strategy URL 返回无关页面就是直接反例。
3. Catalog 没有足够的矿山/国家/期间/口径/actual-estimate 标签合同；同矿别名和公司聚合体易错。
4. 官网本身也有单位/状态矛盾，如 Bisha kt/t、3Q“在建/已投产”，所以 ingestion 必须保留冲突而非静默择一。
5. 当前 presentation/timing schema 对贸易“总额+净额混合”、其他“时点+时段混合”过粗，只能写近似并登记 gap。

### P1：模型质量

1. 四分部全部 direct_growth，只能回答集团/分部增速，不能回答逐矿收入。
2. 没有金、铜、锂、锌等商品价格和TC/RC/汇率曲线；情景把这些风险隐含在增长率中。
3. 没有 immutable historical backtest；置信度相应为低。
4. 只有矿产品驱动实现了两来源/两证据类型三角验证，其余三个分部证据有限。

## 八、系统性改进建议（本次不实施）

### 1. 把读模型从写模型真正拆开

- 新增无 DDL、无 migration、无 seed、无 WAL 切换的 CatalogReader；resolve/query/status 在 OS read-only DB + live writer 下必须通过。
- migration/seed 只能在显式 maintenance/startup 阶段运行。
- 将 raw SQLite lock、operation lock 和暂停状态统一为结构化错误码，保留 deadline/backoff 和分阶段回执。

### 2. 建立统一的来源状态机

建议显式状态链：discovered → identity_verified → captured → injection_reviewed → normalized → structured → chunked/tagged → artifact_bound → consumer_ready。每一步绑定 source SHA、producer、schema、model/prompt、时间和错误；不再用一个 active 掩盖“只有物理文件”。

对旧年报做一次可审计迁移：只有验证原文件 hash、派生文件完整性和可恢复 producer 信息后才 backfill；无法证明的 artifact 保持 legacy/untrusted，不伪造零调用。

### 3. 把券商研报做成一等文档类型

- 从文件名+首页提取日期、券商、公司和证券代码；支持比较型报告多实体绑定。
- 保存页码/表号/行列/单位/actual-estimate/资源-储量/100%-权益-并表口径。
- 建立矿山别名和语义事实层，避免长江报告把陕西煤业预测归给紫金。
- consumer 用 source SHA + 字段需求提交幂等优先处理请求，不能直接改 worker 全局优先级。

### 4. 建立通用 mine-year 运营层，不做紫金硬编码

推荐四层模型：

1. asset facts：矿山、国家、矿种、持股、并表、资源/储量、品位、产能、投产节点；
2. mine-year operations：产量、回收率、可售量、产品形态、实现价/TC-RC/副产品；
3. accounting bridge：权益与并表、内部销售、冶炼/贸易流转、总额/净额、收入确认；
4. reported segment reconciliation：逐层勾稽到四外部收入分部和公司总收入。

只有四层闭合后，才能可靠回答逐矿收入；资料不足时必须停在分部层并输出 gap。

### 5. 修复 revenue 工具契约并以真实引擎验收

- generator 输出必须直接通过 validate_document + draft full run，而不是仅过 linter。
- --validate-only 必须断言 registry 字节/hash 不变；或改名明确会 formal publish。
- draft renderer 要有正式支持路径，并测试 draft/formal 两类 receipt。
- 统一 top-level/receipt 的 output mode 契约；修正文档 3.6/3.7 与 capture 9/10 键漂移。

### 6. 固化动态 E2E，而不是重复人工审计

最小真实场景矩阵应覆盖：

- companies/dayu/Dropbox 三 root 中 exact、equivalent、缺失、陈旧、重复位置；
- live worker 持锁下 exact reuse，OS read-only catalog 下 query/resolve；
- 文件已存在但 injection review 缺失/通过/检测到并忽略；
- PDF 已处理且 binding 有效、legacy artifact 缺 hash、只有 summary、partial MD、零 artifact；
- broker 比较报告多实体、旧/新报告并存、单位冲突、别名、2028目标不得变2030事实；
- 不授权下载/授权下载、最新报告已存在/缺失、amendment、下载后 canonical import；
- parser/LLM budget 必须与真实 producer events 对账；
- source URL 200但 title/entity不匹配必须 fail；
- validate-only registry 不变、draft render 成功、formal registry 只追加一次；
- 逐矿事实必须带 source SHA、页码、表号、单位、期间和口径，并可回到报告分部恒等式。

## 九、验证和非修改声明

- 严格输入：65 parameters、32 claims、4 sources、4 segments。
- validate_document(..., Collector())：通过。
- run_forecast(..., mode=draft)：连续两次通过；canonical 输出一致。
- 独立反算：四分部逐年加总、Low≤Base≤High、三情景 CAGR、base 对账、概率和与六个质量门全部通过。
- publication registry：最终封存重跑的前后 size 都是 1,423,114、SHA-256 都是 `5b3c7306...8c0be4e`，证明该次 draft 没有写 registry。较早检查点曾是 size 1,417,078、SHA-256 `07b51fbe...4556b`；两次检查之间有其他 agent/进程并发活动，故只能证明每次本地 before/after 不变，不能把跨时段的全局变化归因给本审计。
- formal publication：未尝试；没有 attestation provider 签名。
- 本审计没有创作 revenue/filing/company-wiki 产品代码或配置改动，也没有调用显式 ingest/index/metadata/worker-priority 写接口；目标级 acquisition journal/文件/artifact 证据显示本轮零下载、零新 artifact。
- 但 reuse-only source-preparation 会构造具有 DDL/seed/commit 能力的 `CatalogStore`，一轮因此遇到只读写失败，另一轮遇到锁；后台 worker 也持续写库。所以不能诚实保证 company-wiki DB 的每个字节未被该进程初始化路径触碰，更不能用全库 mtime 归因。
- 三个产品工作树在运行期间还出现了其他 agent 的提交和未提交改动；本审计没有覆盖或回滚它们。由本审计创作的持久文件仅位于本审计目录，最终运行基线见 `RUN_MANIFEST.md`。

## 十、主要交付物

- [预测摘要](outputs/draft_report.md)
- [严格输入 JSON](outputs/input_v1.json)
- [完整 draft 结果 JSON](outputs/draft_result.json)
- [验证回执](outputs/validation_receipt.json)
- [独立反算检查](outputs/post_run_checks.json)
- [最终运行快照与哈希](RUN_MANIFEST.md)
- [矿山覆盖矩阵](mine_coverage_matrix.md)
- [Dropbox 研报审计](dropbox_broker_report_audit.md)
- [完整过程日志](progress.md)
- [累计发现](findings.md)
- [信任边界](TRUST_BOUNDARY.md)

这次运行的正确结论不是“技能完全失败”或“技能已经完整解决”：它能给出一个严格可验证、分部可对账的集团五年 draft，但本地资料复用、安全审查、派生产物复用、Dropbox语义摄取和逐矿收入模型仍未形成真正的端到端闭环。
