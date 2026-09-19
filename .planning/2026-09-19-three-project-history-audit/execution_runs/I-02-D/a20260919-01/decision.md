# I-02-D / a20260919-01 — 决定：注册重入与同 bytes 去重的「完成键 vs attempt 键」冻结（D-W02 延续）

日期：2026-09-19。owner：company-wiki 来源系统实施者。性质：D-W02 延续（I-02-A/B/C 已冻结
scan 契约、错误信封/副作用契约、register-existing 恢复入口；本卡只在其上冻结**幂等/重入/
并发语义**，并修正 canonical_writer.import_staged 现存 dedup 分支的两处缺陷）。不改 oracle
先冻结方案；不改锁机制（无新锁；见末节 open question 归 I-04）。

## 1. 逻辑完成键 vs 审计 attempt 键（冻结）

| 键 | 定义 | 唯一性层级 | 落点 | 允许重复？ |
|---|---|---|---|---|
| **逻辑完成键**（业务唯一性键） | `(content_sha256)` → 唯一有效 source version/location；同 bytes 的 source row 由 `_existing_original`（active company_raw original_primary + 字节重验）判定 | 业务资产层：同一 bytes 在 sources/documents/locations(active original_primary, company_raw) 中**恰好一行/一 location** | catalog sqlite（sources/documents/locations） | **不允许**。重复登记=伪造成 |
| **审计 attempt 键**（每次 attempt 历史键） | `sha256(canonical_json(outcome 全字段))`，即 acquisition_journal.py:87 现行实现——**按完整 outcome 内容 hash 去重，不是按 request 压缩** | 历史层：每次**语义不同的** attempt 一行；完全相同 outcome 的重放不产生新行（append-only 幂等） | acquisition_attempts.jsonl | 允许多条（不同 outcome/错误/reason）；禁止压缩成一条，禁止删除 |

两者关系（冻结规则）：
- 逻辑层幂等**不通过**删审计或跳过 exact resolve 实现（卡退出判据原文）。
- 同 request 多次成功重入：逻辑层 1 行不变；审计层每次调用按其真实 outcome 落 1 行
  （`reused_before_download` / `registered_existing_raw` 同内容 hash 去重为 1 行——现行
  journal 语义，保留）。**重放三次的 journal 行数 = 独立 outcome 语义数，不是 1 也不是 3 的
  强制**；oracle 用 SQL 数 + journal 数逐次对账，而不是「恰好 1 行审计」这种伪压缩。
- journal 去重键**不**加入 request_id 之外的 attempt_id 随机项（attempt_id 由内容派生，
  重放同一 outcome → 同 attempt_id → 不新增行；不同错误 → 不同行）。这与 D-W02
  「attempt_id/fsync/mutex 现行实现」一致，不改。

## 2. 同 bytes 多身份（同 hash、不同 provider identity）处置（冻结选择）

场景：canonical raw bytes hash 相同，但请求/登记携带**不同 provider/provider_document_id**。

设计现状核查（只读）：`_existing_original` 只按 content_sha256 查 active company_raw
original_primary；`register_existing_raw` 的 Gate R6 要求 request 身份 == sidecar 持久身份；
`import_staged` dedup 分支只按 hash 命中即返回 DEDUPLICATED。即：**bytes 是唯一性锚，
provider identity 是 provenance 事实，不是第二行键**——catalog 以 document_id = sha 派生
（source_id_for_sha256），同一 bytes 天然不可能有两行有效 source（DB 层 document_id 冲突）。

选项对照：
- **A（first-row-wins：先查到谁就当谁）**：拒绝（卡明令）。静默把 B 身份的 bytes 归给 A
  登记行，B 的 provenance 丢失，等于伪造「B 已登记」。
- **B（同 bytes 双行并存）**：结构性不可能/不合法——source_id/document_id 由 sha 派生，
  两行即主键冲突；换 ID 即破坏内容寻址不变量。拒绝。
- **C（dedup 前先做身份资格检查；身份不匹配 → 不报 DEDUPLICATED 成功，报
  exact_resolve_identity_mismatch 级失败，保留恢复证据）**：**采用**。
  - 同 bytes 同身份（request.provider/pdoc == 既有行 provenance，或既有行 provenance 即
    sidecar/receipt 身份）→ dedup 合法，返回既有 identity。
  - 同 bytes 异身份 → exact resolve 不可能 REUSED_EXACT（provider_mismatch/
    provider_document_id_not_strong 过滤）→ 修正后 dedup 分支**必须先 exact resolve 成功才
    汇报 dedup 成功**；失败时报 CanonicalImportError
    `exact resolve returned a different identity than the imported target
    (exact_resolve_identity_mismatch)` 级稳定短语（沿用 I-02-A 冻结错误短语词汇，不新造），
    **不删 staging**（可恢复证据保留——import_staged 的 dedup 分支当前先删 staging 再
    resolve，正是被修正点）。
  - 该语义不要求「多身份并存」有定义：异身份组合被**显式拒绝**并留证，而不是被静默合并。
    设计因此是明确的，不构成 open question（对照卡文「若设计不明确→停止该变体」：本组合
    有明确处置=拒绝+留证，故 N1 变体继续执行）。

## 3. 两处缺陷修正（3 允许文件内）

1. **dedup 返回资格检查**（canonical_writer.import_staged 155 行分支）：现行先
   `_remove_staged(staged)` 再 `SourceResolver.resolve(request)`，resolve 结果**不检查**
   就返回 DEDUPLICATED。修正：先 exact resolve（带 identity match 校验，同 I-02-A gate4
   语义：status==REUSED_EXACT 且 match.content_sha256==receipt hash 且
   match.canonical_path==existing resolve）；**resolve 成功后**才 `_remove_staged`；失败
   抛 CanonicalImportError 且 staging 保留（可重试/可恢复）。
2. **staging 清理时点**：同上——「可恢复证据持久化后（=resolve 证明成功返回）才删
   staging」。register_existing_raw 路径无 staging，不涉。

幂等按 §1 冻结键：重入=逻辑层 1 行 + 审计层按真实 outcome 追加。**不新增锁**：两进程
并发经现行 `CatalogOperationLock(canonical_import)` 互斥（一人持锁、另一人
CatalogOperationLockedError）——该行为即「明确可重试竞争」，P2 oracle 接受（不改 lock.py，
不复制 worker scope 锁）。

## 4. N1/N2/N3 边界（冻结，延续 I-02-C R1-R7 不扩大恢复授权）

- N1（同 bytes 异 provider identity）：§2 选项 C。不返回 DEDUPLICATED 成功；staging 或
  已有 canonical raw+sidecar 保留作恢复证据；错误短语为 I-02-A 冻结的
  `canonical file was written but exact provider identity did not resolve` /
  `(exact_resolve_identity_mismatch)`。
- N2（同 request 换 hash/identity/policy）：新 hash=新版本，走新 import（旧 raw 不覆盖——
  hash-suffix 纠偏已冻结）；换 identity/policy → exact resolve 不命中旧完成（request_id
  本身随 identity 变化），不得命中旧 journal 完成态。
- N3（dayu/external 同 bytes 或 retired 同 bytes）：`_existing_original` 只认 company_raw
  active original_primary（dayu root 不算 dedup 目标——现有
  test_writer_dedup_ignores_dayu_portfolio_locations 契约原样保留，不扩大）；retired 同
  bytes：**register-existing** 路径维持 I-02-C R7 拒绝（`existing_raw_status_not_active`，
  不调 _reactivate_if_retired）；**import_staged**（真实 re-download）路径维持 Phase 15.6
  契约（显式用户重获权，reactivates 测试界定）——本卡不改变两者任一边界。

## 5. 兼容影响

1. import_staged dedup 分支顺序变化：resolve 失败时 staging 从「已删」变为「保留」——
   additive 安全（少删文件），无消费方依赖「dedup 失败后 staging 必删」。
2. dedup 分支新增 identity 校验：同 bytes 异身份从「静默 DEDUPLICATED 成功」变为显式
   CanonicalImportError——按 I-02-A/B 错误信封，fail-closed，与 gate4 同语义。
3. 其余路径（register_existing_raw、acquisition_service、journal）零语义变化；journal
   outcomes 集合不变（本卡无需新 outcome）。

## 6. Open questions（不阻塞本卡）

- 跨进程锁的 owner-scope（是否需要 acquisition 级独立锁）→ I-04 owner scope，本卡用现行
  canonical_import 单锁语义，不新增。
- CLI 层并发 harness 不在本卡（服务级两进程 barrier 足以证 P2；CLI 并发属 I-02-E/I-04）。
