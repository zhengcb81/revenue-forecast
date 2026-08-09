# ADR WU-201：职责边界冻结（Architecture Decision Record）

> 计划版本：2.1-full-refactor-execution-cards  
> 状态：冻结（contract_frozen）  
> 依据：task_plan 0.7（全面重构裁决）、0.8（strangler 拓扑）、D-001~D-021

## 1. 九项职责边界

| 职责 | 拥有 | 做 | 不做 |
|---|---|---|---|
| RootPolicy | company-wiki config | 决定 root 是否允许扫描/复用、用哪个已注册 adapter/profile、路径与路由范围 | 不解释财报语义；不承载 layout 解析 |
| SourceAdapter | company-wiki source_catalog/adapters | 只枚举文件组并把来源布局转为 NormalizedCandidate | 不写 DB、不决定下载、不绕过 admission、不 import store/resolver/download/parser/LLM |
| NormalizedFilingMetadata | company-wiki source_catalog | 来源无关的财报事实与逐字段 evidence | 不携带 root_id/绝对路径/来源名（留在 location/source 记录） |
| AdmissionPolicy | company-wiki source_catalog/admission | 统一执行 identity/provenance/kind/period/status/hash/path/as-of 安全门 | 不含 root 特例；同一 candidate 只改 root_id 结果相同 |
| Catalog persister | company-wiki store | 事务、幂等、location/artifact/assertion 持久化 | 不含 root 特例；禁止以 root_id 选择 JSON container |
| Resolver | company-wiki source_catalog/resolver | 只查询 active normalized facts 与允许 root | 不解析 sidecar、不按 source 名分支、不 import adapter |
| SourceBundle | company-wiki source_catalog | 把 filing、artifact 与 binding 一次性输出给消费方 | 不改变 DB；不触发 parser/LLM |
| filing-fetch | filing-fetch scripts | reuse-first、latest/gap 与授权下载 | 不重新猜 catalog 语义、不维护来源分支 |
| revenue source-preparation | revenue scripts | 唯一 I/O 编排入口；输出已验证 RevenueSourceRecord | revenue_forecast.py 保持纯计算（无 network/catalog/download） |

## 2. 禁止依赖（ARCH-01~05）

| ID | 禁止边 | 检查方式 |
|---|---|---|
| ARCH-01 | resolver → adapter | AST import gate |
| ARCH-02 | adapter → store（CatalogStore） | AST import gate |
| ARCH-03 | revenue calculator → network（requests/urllib/socket…） | AST import gate |
| ARCH-04 | config → 动态 Python import（importlib/__import__/eval/exec） | AST import gate |
| ARCH-05 | adapter → canonical writer | AST import gate |

外部 root → canonical writer 亦禁止（任何 adapter/route 不得写 companies 之外的外部根）。

## 3. 已冻结的演进方向

- 物理 catalog（roots/sources/documents/locations/artifacts/evidence）、内容 hash、
  多 location、canonical writer、external read-only、status、path fence：**保留演进，不重写**（F-058）。
- source_metadata_assertions 为唯一 assertion ledger：**additive v2 演进**（D-016），不新建第二张表。
- latest/gap、ArtifactHandle/SourceBundle 已验证逻辑：**先 drift audit 再接线**（D-007），不重写。
- scanner 单体流程、acquisition/dayu_meta 容器、root kind 三合一模型、resolver 来源
  特定 JSON 读取、人工拼接生产链：**必须重构**（0.7）。

## 4. 校验

```bash
python audit_review/2026-08-09_data_lake_refactor_plan/tools/architecture_boundaries.py \
  --repo company-wiki --repo filing-fetch --repo revenue-forecast
# 期望 exit 0；新增 adapter 后必须仍为 0（adapter 模块会被 role 规则识别）
```
