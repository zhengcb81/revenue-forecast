# decision.md — I-05-A / a20260919-01（D-W05 专业决策）

实现者：本 attempt（wiki producer 实施者角色）。
本文件**不是**决策签署，而是把 D-W05 需要具名高级 reviewer 选择的事项写成 **OPEN**，
并如实声明本 attempt 在哪两项上**只复用了既有已冻结契约**（不构成新决策）。

## 0. 结论摘要

| 编号 | 事项 | 状态 | 本 attempt 是否实施 |
|---|---|---|---|
| FROZEN-1 | sections 消费者必须走同一把 `validate_artifact` 资格门 | **既有契约**（卡片 step 3 明文 + `artifact_handle` 已是通用门） | ✅ 已实施（`section_query.py`） |
| FROZEN-2 | 既有 failed/stale sections 行不得满足"已有 sections"过滤 | **既有语义**（既有代码注释已声明"newest VALID"意图；卡片 step 4 明文） | ✅ 已实施（`section_extractor.py`，只加 `status='completed'`） |
| OPEN-1 | 重算准入的完整条件（旧 generator 版本是否算"我的产物"；stale 判定依据） | **未签** | ❌ 未实施（n2b 如实记为 observation） |
| OPEN-2 | `selected_roles` / `recompute_plan` / `artifact_read_events` / `producer_invocations` 的权威位置与事件 schema | **未签** | ❌ 未实施 |
| OPEN-3 | raw/artifact 的 verified-read API 与 `ArtifactHandle` 的边界（D-W05 原文点名） | **未签** | ❌ 未实施 |
| OPEN-4 | 冗余 catalog markdown producer 退役后，旧 markdown 工件的兼容读语义 | **未签** | ❌ 未实施 |
| OPEN-5 | `not_applicable` 与 `missing`/`failed` 的对外区分位置 | **未签** | ❌ 未实施（当前只有 valid / invalid / 缺席） |

**为什么 FROZEN-1/2 不算"弱模型自行设计"**：

- FROZEN-1 不新增字段、不新增枚举、不改 schema：它把既有通用门 `artifact_handle.validate_artifact`
  （`artifact_handle.py`，哈希与卡片锚点一致）接到既有消费者上。卡片本身即写"接通 section 查询与默认
  bundle 的同一资格门"。
- FROZEN-2 只把过滤条件从"存在任意 sections 行"收紧为"存在 **status='completed'** 的 sections 行"。
  被拒绝的替代方案（见 §OPEN-1 的 D 选项）会引入版本语义，本 attempt 明确不做。
- 两项都不触碰 D-W05 点名的 schema 权威位置、事件 schema、发布包事务或迁移。

## 1. OPEN-1：重算准入与 same-role 选择（需签名）

> **r2 必答依据（复审 F-I05A-05 实测）**：当唯一 sections 行是 `0.9.0/completed` 时，
> producer 侧 `completed=0, eligible=0`（"存在 completed 行即跳过"），而消费者侧因 `0.9.0`
> 不在 `GENERATOR_REGISTRY` 而拒（`sections_binding_error`）——**正常管道无法自愈**。
> 签署者因此必须回答："哪些 generator 版本算'我的产物'"必须由**过滤条件与资格门共享同一版本集**，
> 否则两个组件各自正确、合起来死锁。证据：`after/review-attack-probes.json.m5_old_version_deadlock`。
> 本 attempt **未**自行加版本比较（理由见选项 B 的实测反驳）。

现状：`extract_sections_catalog` 的过滤 ≈ "存在任意 sections 行"（修复前）/"存在 completed sections 行"（本 attempt）。
`source_bundle.build_source_bundle` 另有一套 same-role 规则："最新 VALID 胜出，其余 valid 行标 `artifact_superseded_by_newer`"。
`section_query` 修复前**没有任何**选择规则（SQLite 未排序 first row）；r2 起与 bundle 对齐为"最新 VALID 胜出"。

**反例（本 attempt 实测）**：
- `before/n3`：两条 sections 行共存（`0.9.0` completed 先插入、`1.0.0` completed 后插入）→ 修复前消费者返回
  `STALE-OLD-VERSION` 旧内容（`before/case_results.json.n3`）。
- `after/n2b`：只有 `0.9.0` completed 行时，重算**不**发生（`completed=0`）——本 attempt 有意不修。

**选项与后果**

| 选项 | 内容 | 后果 | 兼容性 |
|---|---|---|---|
| A | 只要求 `status='completed'`（本 attempt 采用） | failed 行不再阻塞重算；旧版本 completed 行仍被视为已完成 | 与既有测试一致：`test_source_catalog_section_extractor` 的幂等断言依赖"存在即跳过" |
| B | `status='completed' AND generator_version=<当前常量>` | 生产者升级版本后自动重算全部文档（大范围重写） | 会改变现有仓库语义：仓库里写入方并非都使用 `models.SECTION_EXTRACTOR_VERSION`（本 attempt 实测该常量在别处被用作别的语义值），一刀切会误触发全量重算 |
| C | 复用 `build_source_bundle` 的"最新 VALID 胜出 + superseded 记账" | 生产者与消费者共用一套选择契约（D-W05 建议方向） | 需要把 bundle 的选择逻辑抽到共享位置；`source_bundle.py` 属卡片允许修改范围 |
| D | 以 `artifact_bindings` 为准（`artifact_read_model` 的 bound/legacy 语义） | 最强，但当前 sections 行通常无 binding 行 | 需要迁移/回填规则（本卡禁止猜填） |

**必须由 reviewer 冻结**：选 A/B/C/D 之一或组合；若选 B，必须同时冻结"哪些写入方共享同一版本常量"，
否则重算范围不可预测。

## 2. OPEN-2：四个名字的权威位置与事件 schema（需签名）

卡片/父义务要求把 `selected_roles`、`recompute_plan`、`artifact_read_events`、`producer_invocations` 分开。
本 attempt **未**新增任何事件表或事件字段，因为 D-W05 要求先冻结事件 schema
（role/artifact/hash/bytes_read/调用 ID/尝试次数/失败归属）。现在只有：
- RF 侧 `source_preparation.py` 的 `reuse_receipt.artifact_read` / `producer_events`（I-05-B/C 范围）；
- CW 侧 `producer_events` 表（`store.py:322`）。
**需要 reviewer 决定**：事件权威位置在 CW 还是 RF；`artifact_read` 是"角色选择"还是"实际读取"（后者属 I-05-B）。

## 3. OPEN-3：raw/artifact 的 verified-read API（需签名）

**r2 更正（复审 F-I05A-04）**：r1 曾写"允许根由路径反推，但 containment 检查仍会 fail-closed 拒绝"——
**该表述是错的**：根由被校验路径自身的 `parents[3]` 推出时，候选路径恒在该根之内，
`artifact_path_outside_allowed_root` **不可达**（复审实测 m3 在 r1 版本下仍 `returned` 并读取了 catalog 外的文件）。
r2 已改为由 **DB 位置**推出允许根（`_catalog_derived_paths`，见 `section_query.py:160-172`），该门重新可达。

**需要 reviewer 决定**：是否进一步改为显式传入 catalog/derived 根（例如由调用方从 `CatalogConfig` 传入），
而不是从 `catalog.sqlite3` 的父目录推导；以及是否要让 `as_of_date` 与
`service.query_source_bundle` 对齐（本卡传 `""`，该处传 `published_date`，见 OPEN-7）。
**被拒绝的替代方案**：把 `SourceHandle` 的原件 API 直接套到 `ArtifactHandle` 上（D-W05 明确禁止）。

## 4. OPEN-4：退役 markdown producer 的兼容读（需签名）

`artifact_dag.ROLE_DEPENDENCIES` 仍有 `markdown: ["normalized"]` 与 `summary: ["markdown"]`，
但本 attempt 实测：`sections` 与 `normalized` 完全不需要 markdown 即可消费（`after/default-producer-artifacts.json`
的 `P2_bundle`：`valid_roles=[normalized, sections]`，`markdown`/`summary`/`consumer_analysis` 缺席而 bundle 正常）。
**需要 reviewer 决定**：是否把 `summary` 的父依赖从 `markdown` 改为 `normalized`（会改变 DAG 与失效传播），
以及旧 markdown 工件是"兼容读"还是"标记 superseded"。

## 5. OPEN-5：`not_applicable` vs `missing`（需签名）

本 attempt 实测：删掉 summary 行后，bundle 既不放 `valid_handles` 也不放 `invalid`，而是**缺席**
（`absent_roles=["consumer_analysis","markdown","summary"]`）。
这满足"不伪造派生物"，但**不满足**"状态区分 not_applicable 与 missing/failed"（父义务 I-05 第 6 条）。
**需要 reviewer 决定**：把该区分放在 bundle 的返回结构（新增 `not_applicable` 映射）、
还是放在调用方（例如 `bundle_status` 的枚举扩展）。任何新增枚举都会影响跨仓消费者，须先冻结。

## 6. 恢复规则（本 attempt 差异）

- 只改 attempt 内 `iso/`；生产仓零写入（`after/prod-anchor-hashes-after.json` 与 `after/prod-porcelain-after.json` 留证）。
- `recovery/README.md` 写明 NA 理由（纯读路径、无持久状态迁移；异常路径已被真实反例覆盖）。
- 撤回方式：删除 `iso/fixed/` 的两份副本并让 `iso/cw/src` 回到生产字节即可（本 attempt 已这样做过两次，
  用于生成 `before` 证据，见 `commands.json` C2/C5 与 r2 的 C10/C12 顺序说明）。

## 7. OPEN-7：`as_of_date` 在两处不一致（复审 F-I05A-07，需签名）

`section_query.py` 走 `validate_artifact` 时传 `as_of_date=""`，而
`service.query_source_bundle`（同一把校验器）传 `document["published_date"]`。
因此 r1 的"同一资格门"表述**过强**，r2 已在代码注释与 `review_r2_disposition.md` 中限定为
"同一校验器、参数集不同"。

**需要 reviewer 决定**（三条路，各有后果）：

| 选项 | 内容 | 后果 |
|---|---|---|
| A | 保持 `""` 并**明确记载**（当前做法） | 该路径不做 as-of 门；字节一致性门仍然生效。与 `service` 不一致但不会误拒"审计时点尚未发布"的文档 |
| B | 与 `service` 对齐，传 `published_date` | 两处同参数；但会让 `published_date > now[:10]` 的工件被拒（本 attempt 实测触发过），语义上把"发布日"当"as-of 上界" |
| C | 修改校验器的 as-of 判定（例如只对 as_of 存在时才比） | 影响所有调用方与 `artifact_handle.py`（本卡锚点文件），需跨仓回归 |
- 若 reviewer 否决 FROZEN-1/2，无需任何产品仓回滚动作。
