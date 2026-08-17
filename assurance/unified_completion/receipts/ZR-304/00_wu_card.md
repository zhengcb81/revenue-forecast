# ZR-304 工作单元卡（preflight）— producer attempt/result + artifact-created journal + 唯一 reusable view/validator 与生产 bundle 绑定真源

- 领取时间：2026-08-17T21:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-304`；units.ZR-303.status=accepted + closure.next=ZR-304；`uc next` 解锁列表含 ZR-304。
- 依赖：ZR-301（accepted ✅）。Registry 依赖列=ZR-301。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 派生产物谱系真源。现状：artifact INSERT 由 `trg_artifact_producer_event` 触发器写入 `producer_events`（append-only），ArtifactHandle（WU-5.1）已做 fail-closed 校验，`artifact_bindings` 表 + backfill 已存在，`build_source_bundle` 已消费唯一 view。但：**(a)** 失败且无 artifact 的 producer 运行没有任何 attempt 记录（触发器只在 INSERT 时触发——parser/LLM 失败即消失）；**(b)** `count_producer_events` 只有全量历史计数，无法区分"本次请求 calls_this_request"与历史事件；**(c)** `artifact_bindings`/`artifacts.metadata_json`/`artifacts` 列多头，无一条归一的生产读取语义（ZR-304 要求 `artifact_bindings`/metadata/columns 归一为一条生产读取语义）；未知 role/version 须 fail closed。
2. **production entrypoint 是什么？** 本卡 shadow 侧（与 ZR-301~303 同纪律）：新增 `producer_journal.py`（attempt/result 记录读取 + calls_this_request 区分，只读 side）+ `artifact_read_model.py`（唯一生产读取语义，只读）；失败 attempt 的**写入**走既有 store 写路径的增量（若需）。不接生产 CLI。
3. **哪个 current-triplet 行为是 RED？** parser/LLM 失败无 artifact 时零 attempt 证据（调用预算无法对账）；`count_producer_events` 无法回答"本次请求调用了几次"；artifacts 读语义多头。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/producer_journal.py` + `src/company_wiki/source_catalog/artifact_read_model.py`（新模块，复杂度≤10）+ 增量扩展 `producer_events.py`（calls_this_request 查询）+ `store.py`（如需失败 attempt 写路径，最小 diff）+ `tests/unit/` 测试；revenue 侧 receipts/ZR-304/** 与 state.json。禁止：改 reader/锁、接生产入口、真实 catalog 写、下载。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-305（legacy 五桶 migration）与 ZR-306（role DAG 最小失效）。本卡不迁移 legacy artifact（ZR-305）；不做 role DAG 失效（ZR-306）；不接生产入口。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-303 accepted（机器状态；closure.next=ZR-304）。
- [x] triplet 冻结（领取时重读）：revenue `32ad84c…`（ZR-303 closure 后）、filing `0e5d209…`、wiki `77ce0f3…`。
- [x] 现状代码事实：`producer_events` 表 + `trg_artifact_producer_event` 触发器（仅 INSERT 时记录）；`count_producer_events` 全量历史计数；`ArtifactHandle`（WU-5.1 fail-closed）；`artifact_bindings` 表（binding_id/artifact_id UNIQUE/source_id/content_sha256/bundle_hash/evidence_basis/visibility_state）；`build_source_bundle` 唯一 view 消费者；无失败 attempt 记录、无 calls_this_request 区分、无归一读取模型。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品新模块）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——失败 attempt 零证据；calls_this_request 缺失；读语义多头。
- **Acceptance criteria**：
  - `producer_journal.py`：`record_attempt(connection, document_id, producer_name, producer_version, *, outcome, artifact_role, request_id, created_at)`（outcome ∈ {succeeded, failed}；request_id 可空=历史事件）写入新增的**独立追加表 `producer_attempts`**（不改既有 `producer_events` 表/触发器——冻结 journal 语义零风险）；`attempts_for(document_id, *, request_id=None)` 读取；`calls_this_request(store, document_id, request_id)` 精确计数本次请求（区分历史）；失败无 artifact 也有 attempt（成功 attempt 由写路径记录，与 artifact-trigger 事件互补、皆 append-only）。
  - `artifact_read_model.py`：`read_artifacts(reader, document_id)` 归一 `artifact_bindings`（有则以其 source_id/content_sha256/bundle_hash 为准）+ `artifacts` 列 + metadata_json 为一条生产读取语义（bindings 缺失时回退 artifacts 列并如实标记 binding='legacy'）；未知 role/version fail closed（复用 ArtifactHandle 语义）；source SHA mandatory（无 content_sha256 的 artifact 行不可读）。
  - `producer_events.py` 增量：`count_producer_events(store, document_id, request_id=None)` 增加 request_id 过滤（None=历史全量，保持既有行为）。
  - hermetic 测试：成功/失败 attempt 记录（失败无 artifact 有记录）、calls_this_request 与历史分离、归一读取（bindings 优先/legacy 回退/source SHA mandatory/未知 role fail closed）、复杂度≤10、wiki unit 全绿。
  - 独立 reviewer 复放。
- **Stop conditions / handoff**：改 reader/锁语义、接生产入口、真实 catalog 写 → 立即停止。

## Annex：读语义归一优先级

1. `artifact_bindings`（有 binding 行：source_id/content_sha256/bundle_hash/visibility_state 为准）
2. `artifacts` 列（无 binding 行：列值 + metadata_json 合并，标记 binding='legacy'）
3. source SHA mandatory：两条路径都要求 content_sha256/source_sha256 存在，否则不可读（fail closed）
4. 未知 artifact_role/generator_version 走 ArtifactHandle 校验 → 不可复用（fail closed）

## Annex 2：producer attempt 表设计

- 新增 `producer_attempts` 表（CREATE TABLE IF NOT EXISTS，additive）：attempt_id PK、document_id、artifact_role、producer_name、producer_version、outcome（succeeded|failed）、request_id（可空）、created_at。
- 与既有 `producer_events`（artifact INSERT 触发器）互补：attempts 覆盖成功与失败（失败无 artifact 也有记录）；events 由触发器自动记录成功产物的产生。两者皆 append-only。
- `calls_this_request` 只读 `producer_attempts` 且按 request_id 过滤——历史事件（request_id NULL）永不混入本次计数。
