# 目标架构与系统不变量

## 1. 三仓职责

### company-wiki：数据湖控制面与事实所有者

唯一拥有以下能力：

- RootPolicy、SourceAdapter registry、admission policy。
- 文件扫描、内容去重、NormalizedFilingMetadata、identity binding。
- active/shadow/legacy assertion、activation epoch、cohort 与回滚。
- resolver、gap plan、download authorization、canonical writer。
- ArtifactHandle、SourceBundle、失效判定和 provenance。
- catalog schema migration、生产只读 canary 和数据质量指标。

### filing-fetch：薄编排器

只负责：

- 校验 FilingRequest。
- 调用 company-wiki identify/resolve/ensure/close-gap。
- 在用户显式授权后传递下载授权；不得自行决定 root 是否安全。
- 深度校验并原样转发 ResolutionEnvelope、SourceHandle、SourceBundle 和 AcquisitionTrace。
- 不保存第二份 root policy，不实现第二套 latest、identity、artifact 或 admission 逻辑。

### revenue-forecast：终端消费者与跨仓总验收入口

只负责：

- 从 filing-fetch 获取已验证的 ResolutionEnvelope。
- 按 artifact compatibility contract 选择可复用产物。
- 只重算缺失/失效角色，记录权威 parser/LLM/download 调用事件。
- 对输入内容执行或消费明确的 prompt-injection 审核回执。
- 编排当前三仓 compatibility triplet 的全链 E2E 与发布门。

## 2. 数据面目标流

```text
Revenue SourcePreparation
  -> FilingFetch resolve_filing
    -> CompanyWiki identify
    -> Resolver(normalized assertions + RootPolicy snapshot)
       -> exact hit: ResolutionEnvelope(handle + bundle + trace)
       -> latest hit, provider confirms current: same envelope, download=0
       -> gap: authorization-bound CloseGap transaction
            -> discover metadata
            -> fetch only approved candidates to staging
            -> canonical writer commit to companies
            -> rescan/normalize/assert
            -> re-resolve
            -> envelope(downloaded_new trace)
  -> ArtifactSelector(bundle, consumer compatibility)
  -> only missing roles recompute
  -> auditable RevenueSourceRecord
```

## 3. RootPolicy 2.x 最小字段

每个 root 必须显式提供，禁止再由 `kind` 猜权限：

| 字段 | 含义 |
|---|---|
| `root_id` | 稳定、不承载业务语义的 ID |
| `path_ref` | 可展开的路径引用；禁止产品代码写绝对用户路径 |
| `adapter_id` / `adapter_version_range` | 唯一扫描/规范化 adapter |
| `admission_profile_id` | filing、research、generic 等准入策略 |
| `read_only` | 是否禁止写入此 root |
| `reusable_for_filing` | 是否可成为 filing handle 来源 |
| `allowed_document_kinds` | 允许复用的文档种类 |
| `canonical_write_target` | 下载完成后唯一写入目标；外部 root 必须为空 |
| `priority` | 决定 canonical location 的稳定优先级 |
| `cohort` | 渐进激活与回滚范围 |

安全不变量：消费者不得通过本地 allowlist 扩大 RootPolicy；filing-fetch 只能验证 company-wiki 返回的 policy snapshot hash。

## 4. NormalizedFilingMetadata 不变量

可复用 filing 必须具备可验证的：

- canonical entity、market、security_id；
- document_kind、fiscal_year、period kind、period_end；
- provider、provider_document_id、source_url；
- published/filed/retrieved 时间；
- content_sha256、mime type、byte size；
- adapter id/version、normalization status；
- evidence pointers 与 normalization hash。

禁止从文件名猜测后直接标记 capture-ready。无法证明的字段进入 remediation queue；不得通过默认值、公司名伪装 security_id 或人工编辑数据库绕过。

## 5. 激活与回滚不变量

- runtime policy 必须是可持久化、版本化、可签名/哈希的单一 snapshot。
- 每次 request 在开始时固定 `policy_hash + activation_epoch + cohort`，请求期间不得漂移。
- active resolver 只读取与 request snapshot 相同 epoch/cohort 的 active assertion。
- flag 关闭时，即使数据库存在 active row，也不得影响响应。
- shadow row 永不影响 active response。
- cohort 激活/回滚必须单事务、幂等，并产生不可变 receipt。
- 回滚测试必须改变真实 resolver 响应，而不是只修改内存 dict。
- 迁移和回滚不删除原 assertion、artifact 或真实根文件。

## 6. SourceBundle 与 artifact 不变量

一个 artifact 仅在以下全部相等时可复用：

- source document/content hash；
- artifact bytes hash；
- artifact schema；
- generator 名称和版本；
- 上游输入 bundle hash；
- 对 analysis 类产物，还包括 engine/model/prompt/policy hash。

旧 artifact 无法证明绑定时必须标为 `legacy_unbound`，保留但不可复用。SourceBundle 必须由 company-wiki 生产入口返回，filing-fetch 只转发，revenue 必须真实调用 selector。

## 7. 完成后的禁止项

- production scanner/resolver 中出现 `root.kind == company_raw/dayu_portfolio/directory`。
- resolver 读取 `acquisition`、`dayu_meta` legacy 容器。
- filing-fetch 存在独立 `allowed_handle_roots` 安全策略。
- sibling repo 通过固定目录推断且没有显式配置/manifest。
- `prompt_injection_status="not_detected"`、`download_calls=0 if handle else 1` 等伪证据。
- 标名 E2E 但只调用单个 helper 或只断言返回类型。
- release receipt 标记 accepted，但 reviewer/policy hash/commands/HEAD 不可机器验证。

