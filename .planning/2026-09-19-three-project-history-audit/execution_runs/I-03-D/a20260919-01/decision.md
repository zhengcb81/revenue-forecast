# I-03-D 决策文档 — 事件类型冻结、有界批次 remaining_gap 语义、barrier seam 与 fake provider 面

- 卡片：I-03-D（父 I-03）；attempt：a20260919-01；角色：company-wiki 来源负责人；filing 为消费者 reviewer。
- 控制器约束：禁止修改三仓源码/测试/生产DB/raw；只写本目录 A；禁止网络；URL 仅字符串；fake provider 仅在 A 内。
- 生产锚点（执行前重算与卡一致，零漂移）：
  - `close_gap.py` = `117c8166…`（174 execute、326 _fetch_and_commit）
  - `authorization.py` = `f858a369…`（99 validate）
  - `gap_plan.py` = `d18391b7…`
- 基线选择：iso/override 三文件以 **I-03-C 已产出 override**（gap_plan `f0452bea…`、authorization/close_gap 为 C 卡 override 副本）为基础继承（I-03-C 是本卡已通过依赖，其 D6/D5 排序/绑定校验面是消费端的前件）；本卡唯一新增改动面 = close_gap.py、authorization.py 的计划/额度边界。changes.diff 同时给出 vs 生产原件与 vs 继承基线两个视角。

## 1. 事件类型表（冻结；不得用单 fetch 数字替代）

四类事件共享 I-02 侧 journal envelope 字段（取自 I-02-C/E override 的 `acquisition_journal.py` 行信封：`schema_version="1.0" / recorded_at / request_id / provider / provider_document_id / source_url / canonical_path / content_sha256 / error / error_type / outcome / payload_json`）。每类事件是逐条结构化记录，`CloseGapResult.fetch_events` 保留为旧版兼容计数，但**不构成事件证据本体**。

| 事件类型 | 必填共享字段 | 类型特有 payload 键 | 语义边界 |
|---|---|---|---|
| `provider_fetch_attempt` | schema_version, outcome=event_type, recorded_at, request_id, provider, provider_document_id, source_url | `txn_id`, `authorization_receipt_hash`, `binding_plan_hash`, `declared_remote_size`(可为 null), `gate`: pre-validate 结果或拒绝短语 | 每次"获准下载启动"一条；validate 拒绝不产生本事件（fetch=0 无流量），只记拒绝结果 |
| `bytes_received` | schema_version, outcome=event_type, request_id, provider, provider_document_id, source_url | `txn_id`, `chunk_index`, `chunk_bytes`, `cumulative_bytes`, `max_bytes`, `over_cap`(bool), `stream_stopped`(bool) | **每个 chunk 一条**；物理收到的字节如实记录（含把累计推过额度的那个 chunk）；`over_cap=true` 单独另记单 chunk 超额 |
| `raw_saved` | schema_version, outcome=event_type, request_id, provider, provider_document_id, source_url, canonical_path, content_sha256 | `txn_id`, `byte_size`(实际收到的字节，可与声明的 remote_size 不同), `over_cap_received`(bool) | raw 落盘才发；**合格 commit 前置**：cumulative ≤ max_bytes 且 stream 未 over_cap 停止；超额路径保留已收字节计数但本事件不发 |
| `registration_succeeded` | schema_version, outcome=event_type, request_id, provider, provider_document_id, canonical_path, content_sha256 | `txn_id`, `attempt_id`, `gates`（引用 I-02-C R1–R7 门序号表）, `idempotent` | 注册成功才发；G-D8 重试只走本事件，新增 fetch=0 |

- 拒绝/失败作为 `txn_result`（status=rejected/failed + reason + fetch_events）记录，不混入四事件流。
- 事件留档 = after/provider-events-ledger.json（每 case 一节 + 全局汇总），事件序列可重放断言（G-D7 的累计 120、G-D8 的 fetch=1/raw_saved=1/registered=0）。

## 2. remaining_gap 语义（D5 有界批次落地）

- 常量 `MAX_BATCH_SIZE = 8`（D5 冻结）；**单次场景实际批次上限 = min(binding.max_items, MAX_BATCH_SIZE)** —— 明确单据化：G-D6 授权 max_items=1 时实际=1，不是 8；I-03-A C15 的 8 截断由 max_items≥8 的场景点（C 处记录为语义常量已实现，本卡用 max_items=1 演示同一截断机制）。
- 批内排序 = `_batch_key` / D5 冻结序（继承 I-03-B override，新期间优先）。
- 每个 actionable 候选必须有显式终态，事务结果携带 `gap_items: {candidate_id: {state, reason}}`，state ∈ `completed` / `pending_authorized_not_fetched`（超额/失败截断处） / `pending_next_batch`（超出批次上限，显式待补） / `blocked_ambiguous` / `blocked_conflicting` / `blocked_unknown_metadata` / `completed_reused` / `raw_saved_registration_pending`（G-D8 第一次执行：raw 已落盘、注册门注入失败 → 下一次执行按 I-02-C R1–R7 门序恢复注册）。
- 关闭宣称：`status=completed` 仅当 `remaining_count == 0`；否则 `completed_partial` + `processed_count` + `remaining_count` + pending accession 列表。**选择 actionable[0] 之后对全计划报完成是违规**（两缺期 max_items=1 场景：仅 1 个 completed，另 1 个必须显式 pending_next_batch，remaining_gap>0）。
- 缺期区分已完成/待补：`remaining_gap_semantic.json` 按期（period_key）输出 covered / pending，不全计划报绿；`no_gap` 仍只作计划级处置（继承 I-03-A D4）。

## 3. barrier seam（测试 harness 控制点，不进产品）

- 定义：确定性插入点 = **首次（锁前）rediscover 成功之后、锁内 rediscover 之前**。harness 在此处注入 mutation（URL/date/policy 变更，G-D5），让锁内 rediscover 看到变化后的世界，验证真实校验出口（`validate_close_gap_binding` + `validate_download_authorization` + stale_gap_hash 门）旧 binding fail-closed。
- 实施：iso 副本 `close_gap.py` 顶层 `_BARRIER_HOOK = None`（no-op）；执行器在两条 rediscover 之间调用 `_barrier(txn_id)`。产品码零改动：测试 harness `import` iso 副本后以 `_BARRIER_HOOK = fn` 注入（模块级属性替换），并在通常执行下 hook=None 语义 = 恒 no-op。锁本身单进程 harness 内为确定性单线程点（真实跨进程锁面归 I-02/生产 owner），decision + oracle 单据化该替代。
- 锁前/锁内两计划 + gap_hash + binding hash 全部存档（close-gap-matrix.json 中 per-case `plan_before_lock` / `plan_in_lock`）。

## 4. fake provider 面（仅 A 内）

`A/samples/fake_provider.py`：脚本化 fake adapter，具备：
- `discover()` 返回内存 metadata 候选（含 period/filed/url/amended/size 序列）；
- `chunks(pid)` 可编程：逐 chunk bytes 流（60/60）、谎报 `declared_size`（如 80 实发 120）、中途抛异常、返回空列表、超额单 chunk（>全面额）；
- catalog/store 用 tmp 隔离 sqlite 最小壳（attempt 内建，非生产 registry）：只存已注册 content_sha256 → registered 状态（最小 sourcing 壳，供 R 门与 G-D8 幂等重试）；**不出借**给生产，不禁用（fake 只在 A 内）。
- 无网络：URL 只做字符串比较/落档。

## 5. G-D8 的重试注册面（引用 I-02-C 实现）

注册门实现引用 **I-02-C R1–R7 门**（I-02-C review.md 第 6 条逐门读实码的顺序）：R1 root policy reusable → R2 root 内 containment（case 树内 resolve）→ R3 `<raw>.source.json` 相邻 sidecar → R4 身份/字段完整（缺即 provenance_incomplete，不从文件名补）→ R5 现行字节重算 sha256+size == sidecar → R6 request 身份显式且一致 → R7 已注册同 bytes retired/quarantined 拒。iso 注册壳按同序逐门走（记录每门谓词结果），幂等：同 bytes 已注册 → registration_succeeded(idempotent=true) 无新增。下载成功+注册注入失败：fetch=1/raw_saved=1/registered=0，raw 保留现场；第二次调用只恢复缺失注册（fetch=0，无 provider_fetch_attempt/bytes_received 新事件）。

## 6. 未决/blocked（引用）

- I-02 恢复项：G-D8 的"真实重试注册由 I-02 实现"——本卡以 I-02-C 已经验收的 `register_existing_raw` 语义为引用实现（路径：`execution_runs/I-02-C/a20260919-01/iso/override/canonical_writer.py`），真实生产接线/CLI 归 I-02 owner；I-02 对应恢复项未完成时本卡不得关闭（关闭标准原文）。
- provider 穷尽知识声明（I-03-A 遗留）：not_published 保持保守 false，与本卡无关但再登记。
- 真实 provider / 生产写入归 I-07；本卡 fake 通过不覆盖 live 资格。
