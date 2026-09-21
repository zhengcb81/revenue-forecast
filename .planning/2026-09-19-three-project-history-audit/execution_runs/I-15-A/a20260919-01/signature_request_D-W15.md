# D-W15 送签单 — 生产 prune 的五项专业决定

> **这不是决策本身。** 本文件是 owner 依 `OWNER_DECISIONS.md` 第十三节 **T1-3 / T2-4** 授权、
> 由编排层起草的**送签请求（signature request）**，送给 `wiki_cards.md` §D-W15 指定的两位签署者：
>
> - **存储维护 owner（storage-maintenance owner）**
> - **独立数据恢复 reviewer（independent data-recovery reviewer）**
>
> **签署者必须直接编辑 `decision.md`**（把 D-W15-1…5 的 "proposal, needs signature" 改为
> 明确选择 + 理由 + 反例 + 兼容/回滚），**不在本文件上签字**。本文件不产生任何裁定。

---

## 1. 为什么现在送

| 事实 | 出处 |
|---|---|
| owner 已裁定 **D-W15 五项暂不签**，产品实施维持 `blocked` | `OWNER_DECISIONS.md` §13 **T1-3** |
| owner 已**授权按 `decision.md` 的 proposed 方案改写** `prune_retired_evidence.py` 与 `archive_retired_evidence.py` | 同上 |
| 但**改写后须由数据恢复 reviewer 复签**方可执行任何生产 prune | 同上 |
| 最终签署方 = 数据恢复 reviewer + 存储维护 owner | `OWNER_DECISIONS.md` §13 **T2-4**（TIER-2） |

> **纪律（第 7 条）**：owner 的总授权只解除了「**联系与启动的许可**」。
> 本节记录的是**送签动作已完成**，**不是五项已签**。任何把本文件读成「D-W15 已签」的落地，
> 等同伪造签名。

---

## 2. 待签的五项（逐项摘要 + 送签时要求签署者回答的问题）

`decision.md` 的 D-W15-1…5 已给出 proposed 方案与**实测反例**。签署者需逐项给出：
**选择**（接受 propose / 替换成什么）· **理由** · **反例** · **兼容影响** · **恢复规则** · **被拒绝的替代方案**。

### D-W15-1 Archive manifest schema（`decision.md` §D-W15-1）

**proposed**：`schema_version = "archive-verified-manifest-1.0"`，字段见 proposal 正文；
行摘要口径 `sha256(json.dumps(row, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8"))`。

**实测反例（已复现）**：`n1-same-day-overwrite.json` —— 同日两次归档，第一次 sha `bccfe6a2…`（ids `{a1,a2,c1}`）、
第二次 `7efa681c…`（ids `{a1,a2,a3,b1}`），**两次都报 `ok: true`** ⇒ 仅凭 count 对账无法区分，
gzip 文件的 hash 也不能证明「文件里装的就是你要删的那一行」。

**要求签署者回答**：
1. 接受该 schema 与行摘要口径，还是替换（若替换，给出完整字段表 + 摘要口径）？
2. manifest 落在**文件**（`artifacts/gates/` 下）还是 **DB 表**？（后者是 schema change，需另立卡）
3. 旧无 manifest 归档如何处置——维持「不可用于 prune 直到另有验证规程」（propose 的兼容立场），还是要求一次性升级？注意 `W15-R8` 禁止**猜测补造**证明。

### D-W15-2 Retention clock（`decision.md` §D-W15-2）

**proposed**：`due = (now_utc − manifest.verified_completed_at).days >= retention_days`，`now` 作显式注入参数（harness 固定时钟 `2026-09-19T00:00:00Z`）。

**实测反例（已复现）**：`n2-clock.json` —— 目录名 `2021-01-01` 而 `verified_completed_at = 2026-09-18T00:00:00Z`（仅 1 天）⇒ 现行代码算出 `due: true` 并删了 4 行。**目录名不是证据。**

**要求签署者回答**：接受「以经验证完成时间计算 + 固定时钟显式注入」？是否接受「拒绝以文件 mtime 为时钟」（mtime 不在已验证 manifest 内、一次 copy/restore 即可静默延长窗口）？

### D-W15-3 Exact set + plan hash + TOCTOU（`decision.md` §D-W15-3）

**proposed**：dry-run 输出 `{span_ids, plan_hash, archive_sha256, verified_completed_at, retention_days}`；
`apply` 在**锁内**重读归档（sha256 必须匹配）、重读每个计划行的摘要与 `documents.source_status`、重算 plan hash，
**任一不符即中止整个 apply**。

**实测反例（已复现）**：`fault-recovery.json` —— 冻结 plan 为 `{a1,a2}` 后改 `a2.raw_text`，
现行代码删掉了 `a1, a2, a3, b1` —— 既删了「摘要已不匹配的行」，也删了两个**从未进入 plan** 的行。

**要求签署者回答**：接受「整批中止、要求重做 plan」？确认**明令禁止**「静默收窄集合」——即只删仍然匹配的子集并报成功（冻结 oracle 已禁止，请复核该措辞）？锁复用 `CatalogOperationLock(config.catalog_dir, operation="prune_retired_evidence")` 是否认可？

### D-W15-4 Batch receipts and crash recovery（`decision.md` §D-W15-4）

**proposed**：(a) 先算出精确 id 集合，(b) 写一份 `pending` receipt 命名完整 plan，(c) 每批提交后追加已提交 id，
(d) 重启时读 receipt，只对**仍存在**的 id 重新计划，**永不放宽集合**。

**实测反例（已复现）**：`n4-crash-receipt-absence.json` —— 现行 receipt 在**整轮循环之后**才写
（`prune_retired_evidence.py:125-142`）。第一批提交后崩溃 ⇒ 4 行已删而 `receipt_files: []`，
**实际删了哪些集合从任何持久工件都无法恢复**。

**要求签署者回答**（这是 `START_HERE.md` 明确保留给专业决定的「跨进程锁与崩溃恢复机制」）：
1. receipt 的持久介质选哪个——**同一个 SQLite DB 的某张表**，还是 `artifacts/gates` 下的 **JSON 文件**？
2. `pending` receipt 与批提交之间的事务边界如何划（receipt 先落、还是同事务）？
3. 崩溃重启时的**幂等**判据：按 receipt 的 id 集合重放，还是按「行是否仍存在」重算？

### D-W15-5 Restore protocol（`decision.md` §D-W15-5）

**proposed**：恢复以**行摘要同一性**证明，不以行数证明。

**实测证据**：`restore-proof.json` —— 归档中的 `a1/a2` 恢复到独立空 scratch catalog 后摘要完全相同
（`615eed4a…`、`64e883ee…`）；同归档内的 `c1`（其文档仍 active）被**拒绝**（`refused_ids: ["c1"]`）。

**要求签署者回答**：接受「以摘要同一性而非行数证明」？是否接受「拒绝『重跑归档器』型恢复」（归档器读当前状态，无法复现已删行）？确认该证明的 **scratch-only 范围**——它**不**授权生产 prune、**不**授权 D 盘迁移。

---

## 3. 签署落点与形式（硬要求）

签署者请在 `decision.md` 中按 `START_HERE.md` 的「必须交专业审查」条款，**逐项**给出：

> 选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 拒绝的替代方案

并在文件头把

> `> **This is a proposed decision, submitted for signature by ...**`

改为已签署状态（写明签署人、角色、时间、依据）。

**禁止**：
- 不得以「按最佳实践」代替决定（`START_HERE.md` 明文禁止）。
- 不得在未签署前由实现者或编排层**代签**、也**不得**据此启动任何生产 prune。
- 不得改 `archive_retired_evidence.py` 既有 `"wt"` 截断写快照行的**历史证据**；该项修正在 T1-3 授权范围内，但须在签署后随实现落地。

## 4. 签署后的解锁链（预告，不构成承诺）

签署完成 ⇒ 授权按 T1-3 改写两个产品文件（含 `archive_retired_evidence.py:65` 的 `"wt"` 截断修正）
⇒ 改写须过独立 reviewer ⇒ 之后方可执行**任何**生产 prune。在签署到位之前，
`I-15-A` 的产品实施**维持 `blocked`**，其证据/诊断资格（`accepted_scoped`）**不受影响、也不外扩**。

---

## 5. 本次送签动作的自证

| 项 | 值 |
|---|---|
| 起草人 | 编排层（owner 执行人，非签署者） |
| 授权依据 | `OWNER_DECISIONS.md` §13 **T1-3**（授权按 proposed 改写）+ **T2-4**（签署归他方） |
| 被送签载体 | `execution_runs/I-15-A/a20260919-01/decision.md`（送签时 `18a12d9e564a3131…`，6850 B） |
| 本文件写入了什么 | 仅新增本送签单；**未修改** `decision.md`、`oracle.md`、`review.md`、`handoff.json`、任何产品源码 |
| 不产生 | 任何裁定、任何签名、任何 `status` 变化 |
