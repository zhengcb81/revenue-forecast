# 目标架构、责任边界与不可妥协不变量

> 本文描述目标状态，不表示当前已实现。实施者必须先用当前 triplet 重新验证现状。

## 1. 用户层目标

一个收入研究请求应形成下列闭环：

```text
用户请求（公司 + as_of + 预测范围）
  -> 查找所有配置 root 的已有资料
  -> 复用已有且可信的原文与派生产物
  -> 判断期间/文档角色/研究问题仍缺什么
  -> 仅在授权范围内补齐缺失来源
  -> 新来源进入统一身份、安全、预处理、切片、标签和谱系管线
  -> 消费财报、研报、公告/新闻和结构化矿山事实
  -> 显式运营模型或诚实 fallback
  -> draft/formal 输出、来源回溯、质量评分和持续回归
```

“已有文件”不等于“可消费”；必须分别报告：physical discovery、identity、freshness、safety review、artifact readiness、semantic readiness、consumer readiness。

## 2. 三仓唯一职责

### 2.1 company-wiki：通用数据湖控制面与语义事实所有者

唯一负责：

- root 配置、adapter registry、read/write policy 和路径安全；
- 物理文件发现、内容哈希去重、location 生命周期；
- entity/document identity、期间、来源角色、版本与修订关系；
- source lifecycle、安全审查、处理需求队列和 producer journal；
- normalized Markdown、保真表格、section、chunk、tag、summary、事实 assertion；
- ArtifactHandle、SourceBundle、最小失效 DAG 和 legacy migration；
- broker research、公告/新闻等非 filing 文档的一等摄取；
- 通用矿山/资产事实、冲突与别名，不负责收入预测假设；
- catalog schema migration、只读查询、SLO、健康度和审计事件。

### 2.2 filing-fetch：监管财报的薄编排器

只负责：

- 校验 `FilingRequest`：entity、market、document_kind、exact/latest、as_of；
- 调用 company-wiki identify/resolve/gap/close-gap；
- 只在显式授权有效时调用 CN/HK/US provider；
- 下载到 staging，经 company-wiki canonical writer 只提交到 companies target；
- 深度校验并透明转发 `ResolutionEnvelope`、`SourceHandle`、`SourceBundle`、`AcquisitionTrace`；
- 为每层状态保留用户可见的分阶段结果，即使下游失败也不能吞掉上游零下载/复用事实。

禁止：复制 root policy、在代码中判断 Dropbox/dayu/companies、安全地位、文档 freshness、artifact validity 或通用网页/研报下载。

### 2.3 revenue-forecast：收入研究消费者与终端验收入口

只负责：

- 根据研究问题提出 source/artifact/fact requirements；
- 消费 filing-fetch 与 company-wiki 的已验证 bundle/事实，不读取任意路径绕过合同；
- 仅重算缺失/失效的 consumer-owned analysis；基础解析由 company-wiki producer 完成；
- 构建收入确认一致的分部或资产运营模型、情景、证据树和历史回测；
- 明确区分披露事实、券商预测、分析师外推和压力情景；
- draft/formal validation、render、publication、registry 与 attestation；
- 从用户入口触发三仓 E2E，输出阶段化 reuse/download/processing receipt。

禁止：维护第二套文件索引、root allowlist、source safety 状态、矿山别名表或偷偷下载未授权来源。

## 3. Catalog 读写物理隔离

### 3.1 `CatalogReader`

必须是能力受限对象，而非 `CatalogStore(read_only=True)` 的布尔分支：

- 构造不得 `mkdir`、创建 DB/WAL/SHM、执行 DDL/migration/seed/commit；
- 使用 SQLite URI `mode=ro` 或等价 OS 只读机制，设置 `PRAGMA query_only=ON`；
- 只能暴露预定义 typed queries；不得接受任意写 SQL；
- schema 版本不匹配时结构化失败，不能自动迁移；
- `resolve/query/status/bundle/health` 的生产调用链只能依赖 Reader protocol；
- live writer、DB 文件 ACL 只读、WAL 存在/不存在和大 catalog 下均须通过。

### 3.2 `CatalogWriter` 与 `CatalogMigrator`

- Writer 承担显式事务写入；Migrator 只在 maintenance/change window 运行；
- writer/migrator 的构造和命令名称必须显式暴露写意图；
- migration 有 dry-run、影子 schema、batch journal、resume、idempotence、rollback visibility；
- Reader 永不隐式升级为 Writer。

## 4. RootPolicy 3.0：新增目录只改配置

每个 root 的最小合同：

| 字段 | 约束 |
|---|---|
| `root_id` | 稳定 opaque ID，不承载 companies/dayu/dropbox 语义 |
| `path_ref` | 环境/配置引用；产品代码禁止用户绝对路径 |
| `adapter_id` + `version_range` | 唯一发现/sidecar/身份 adapter |
| `admission_profile_id` | filing、broker_research、announcement、generic 等 |
| `read_only` | 外部 root 必须 true |
| `reusable_document_kinds` | 精确允许的角色集合 |
| `canonical_write_target` | 只有受管 companies target 可 true |
| `priority` | 仅用于 location 选择，不能扩大信任 |
| `cohort` / `enabled` | 渐进激活与即时回滚 |
| `path_safety_profile` | symlink/junction/containment 规则 |

适配器合同负责把不同 sidecar/目录布局归一为同一个 document candidate；核心 resolver 不允许出现 `if root_id/kind == dropbox/dayu/company_raw`。新增 `future_lake` 的验收必须只改 fixture 配置与 adapter registration，不改 resolver/filing/revenue 产品代码。

## 5. 统一来源状态机

```text
discovered
 -> identity_verified
 -> captured
 -> injection_reviewed
 -> normalized
 -> structured
 -> chunked_and_tagged
 -> artifact_bound
 -> semantic_facts_available（适用时）
 -> consumer_ready
```

每一步是可追溯 assertion，不是覆盖式单状态：

- 必须绑定 source/content SHA、producer、schema、model/prompt/policy、时间和输入 bundle hash；
- `not_reviewed` 是状态，不是错误或 `not_detected` 的默认值；
- prompt-injection review 必须有 scanner/reviewer receipt，可缓存复用但 source bytes/policy 变化时失效；
- 失败保留 reason、retryability、next action；不得用 `active` 掩盖只有物理文件；
- consumer-ready 是按 consumer requirements 计算的 view，不是全局永久布尔值。

## 6. ResolutionEnvelope 与阶段化回执

一个用户调用无论最终成功或失败，都返回/记录下列阶段：

1. `identity_result`；
2. `resolution_result`：exact/equivalent/latest/gap/conflict；
3. `freshness_result`：local coverage、provider knowledge、unknown；
4. `acquisition_result`：authorized、discover/fetch/commit 事件；
5. `safety_result`；
6. `artifact_result`：read/recompute/invalid roles；
7. `semantic_result`：事实覆盖与冲突；
8. `consumer_result`：forecast-ready 或具体 data gaps。

顶层失败不得抹掉此前成功阶段。例如安全审查未完成时，仍能证明“FY2025 exact reused、download=0、consumer blocked at safety”。所有计数来自 journal，不由结果倒推。

## 7. ProcessingDemand：按需处理而非篡改全局优先级

消费者提交幂等需求：

```text
demand_id, consumer_id, source_sha256/document_id,
required_roles, required_fact_schemas, as_of/deadline,
priority_class, reason, max_parser_calls, max_llm_calls,
policy_hash, created_at, dedupe_key
```

- 同 source+requirements 只保留一个 active demand；多消费者合并但各有 receipt；
- scheduler 按 admission priority、consumer deadline、cost 和公平性调度；
- revenue 不能直接改 worker 全局 priority 或状态；
- 完成/失败生成 producer event 和 demand receipt；等待超时返回结构化 pending，不静默从头重复处理。

## 8. Broker research 一等文档合同

### 8.1 文档级

- `document_kind=broker_research`；publisher、authors、published_date、covered_entities、security IDs、title、language、page count；
- 比较报告支持多实体及 section/table 级 attribution；不能强绑一个主实体后污染全文；
- 文件名解析只能生成 proposal，必须用首页/正文证据确认；
- `.source.json` 是 sidecar，不得作为独立 annual report 摄取。

### 8.2 内容级

- normalized MD 保留页码和阅读顺序；
- table artifact 同时保留原图/页码、行列结构、merged cells、脚注、单位和 OCR confidence；
- chunk 不得跨 entity/table/section 边界；每个 chunk 带 source SHA、页码范围、document/section/table role；
- tags 最少包括 entity、asset/mine、country/region、commodity、metric、period、actual/estimate/target、unit、ownership/consolidation basis、source date；
- 所有自动 assertion 保留置信度与证据 locator；低置信/冲突进入 review，不静默择一。

## 9. 通用矿山事实与 mine-year 运营层

### 9.1 AssetFact

- stable `asset_id`、canonical name、aliases、asset type（单矿/矿群/公司聚合体/项目）；
- country/region、commodities、ownership timeline、consolidation basis；
- resource/reserve 分开，包含 contained metal、ore tonnage、grade、standard、measurement date、100%/attributable basis；
- capacity/commissioning/permit/status facts 带有效期间；
- 冲突不覆盖：保存双方 assertions、单位归一结果和 conflict status。

### 9.2 MineYearOperation

- asset/year/scenario；ore throughput、grade、recovery、payable production、product form、sales volume；
- realized/reference price、payability、TC/RC、premium/discount、byproduct credit、FX、royalty；
- ownership/consolidation、internal/external flow；每个字段可为空并有 gap reason；
- 披露到 2028 的来源不能直接支持 2029/2030，外推必须显式 analyst assumption。

### 9.3 AccountingBridge

```text
mine/product gross value
 -> payable/price/TC-RC/byproduct adjustments
 -> ownership and consolidation
 -> internal transfer to smelting/trade
 -> external-vs-internal classification and eliminations
 -> reported external segment revenue
 -> consolidated revenue
```

只有 bridge 与年报外部收入在预设容差内对账时，资产级收入才可称为 modeled；否则输出 operating indicators + data gap，禁止“产量×价格”伪精确。

## 10. revenue-forecast 契约闭环

- schema 常量、JSON schema/validator、input generator、linter、文档和样例由一个 machine-readable contract source 生成或验证；
- generator 的最小模板必须直接通过真实 `validate_document` 和 `run_forecast(mode='draft')`；
- `validate-only` 必须调用无写验证路径，并以 registry/catalog/filesystem before/after hash 证明零写；
- draft/formal 都有受支持的 validate+render 路径；draft 永不进入 invest consumer，formal 必须满足 publication/attestation；
- output mode 的唯一字段位置与文档一致，N/N-1 兼容明确；
- source-preparation 能报告分阶段状态并按 ProcessingDemand 等待/复用；
- 矿业优先显式 volume-price/asset bridge；证据不足允许 direct-growth fallback，但置信度、限制和未建模份额必须清晰。

## 11. 全局不变量

1. 没有显式授权，不 discover provider、不 fetch、不 canonical write。
2. Dropbox/dayu 等外部 root 永远零写；新下载只进受管 companies canonical target。
3. 同一 source bytes 跨 roots 共享 document/artifact，不按路径重复处理。
4. identity、安全、artifact 或事实冲突均 fail closed，并给出可处置 reason。
5. 所有昂贵调用和 artifact read 由事件日志证明；不能填伪零。
6. 任何来源只覆盖至某年，不得无声明支持更远年份。
7. 资源量不等于储量；公司聚合体不等于单矿；100%/权益/并表口径不得混用。
8. 测试不得隐式访问真实 sibling repo、用户目录、Dropbox 或生产 catalog。
9. migration/processing 不删除原文和旧 assertions；不可证明的 legacy 保留但不可复用。
10. 历史 complete 不代表当前健康；动态证据过期即失去发布资格。

## 12. 兼容与渐进切换

- 新合同先 additive；旧 reader/producer 进入 N-1 compatibility adapter，不能让新核心继续读 legacy metadata 容器；
- 所有切换遵循 `old active + new shadow -> dual-read diff -> small cohort -> expand -> old off -> observation -> delete`；
- 每个 request 固定 triplet、policy hash、schema version、activation epoch 和 cohort；中途不得漂移；
- rollback 只切可见性/路由，不删除新记录或真实文件；同一 request 的 response 必须恢复到 before trace；
- legacy 删除只有在两个完整动态周期 hit=0、所有 callers=0、rollback 观察完成后才可执行。

