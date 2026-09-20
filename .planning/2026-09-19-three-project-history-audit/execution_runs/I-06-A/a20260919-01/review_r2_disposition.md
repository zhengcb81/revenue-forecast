
---

# r2 — 复审处置（追加式；**未自签；产品仓仍为零改动**）

复审结论：**I-06-A = blocked（保持 blocked）**。F-I06A-01..05 逐条处置如下；F-I06A-06/07 复审判定 PASSED。
**所有改动仍在 attempt 内（`iso/candidate` + `iso/rf_fixed`）；`iso/rf` 与生产仓字节不变。**

## r2.1 逐条处置

| id | 复审严重度 | 处置 | file:line（attempt 内） | 复验结果 |
|---|---|---|---|---|
| F-I06A-01 | high | **写成 D-W06 OPEN-2 的必答依据，不自决**。新增真实 CLI 探针 `c10`（仅 `as_of_date` 2026-09-19→2027-03-31）+ 第三进程查询 `c11`；独立重算并留证两个 request 的 canonical sha256 | 探针：`scripts/w06a_cases.py`（`c10-same-source-asof-only-changed` / `c11-query-after-asof-change`）；结论：`decision.md` OPEN-2 段 | `c10` rc=3 且**复用同一 `demand_id`**（该次为 `demand-84179f79057143d4`，实际值以 `after/demand.cross-process.json` 为准）；`request_hashes.asof_only_changed=4bddf9e6…0b84` 与行内 `request_sha256=d8afcf31…dd62`（第一次请求）不一致 ⇒ 新请求未被绑定 |
| F-I06A-02 | medium | **已修候选**：登记失败不再抛走安全判定；`demand_store_error=…` 作为**同一条阻断**的附加子句；该情形不出现 `demand_queued` | `iso/candidate/w06a_candidate_patch.py:63-139`（`_register_demand` 返回 `store_error` 而不 raise）、`:142-180`（`block_message` 先写安全判定，再附 store 错误） | `after/cli-logs/c7-store-unwritable/stderr.txt` 同时含 `prompt injection not reviewed` 与 `demand_store_error=demand_store_unavailable:`，**不含** `demand_queued`；rc=3；DB 行数不变 |
| F-I06A-03 | medium | **已改**：文档不再硬写会随运行变化的 demand ID；改为引用 `after/demand.cross-process.json`（并在本文件举例时注明"以留存 JSON 为准"） | `decision.md`（候选实测表）、本文件 r2.1 | 留存证据中的 ID 与文档引用一致（`after/demand.cross-process.json.demand_ids_in_stderr`） |
| F-I06A-04 | low-med | **默认值统一**为 `normalized,sections`，并把"角色集合的权威来源与规范化形式"写入 D-W06 OPEN-2 待裁项 | `iso/candidate/w06a_candidate_patch.py:91`（默认 `"normalized,sections"`）；`decision.md` OPEN-2 | 与 `commands.json` 的 `RF_W06_ROLE_SET="normalized,sections"` 一致 |
| F-I06A-05 | low | **已补** `recovery/README.md`（NA + 理由：无产品实现、候选 DB 仅在 `%TEMP%`、失败路径已覆盖） | `recovery/README.md` | 文件存在 |
| F-I06A-06/07 | — | 复审 PASSED：attempt 内写未批准候选、产品仓 0 改动不违反"D-W06 前不得实施" | `handoff.json.blocked_by` 与 `review.md` 顶部 | 候选保持 `UNRATIFIED`；handoff 明确"不得被后续卡直接提升为产品实现" |

## r2.2 新的 raw rc 与命令

- `w06a_apply_candidate.py` → rc 0（`iso/candidate-manifest.json`：`source_preparation.py`
  从 `5ec16eaf…ce46` → `1a837fc0…469e`；候选模块哈希见该 manifest）。
- `w06a_cases.py before baseline` → rc 0（产品 rc=3/3、0 行）。
- `w06a_cases.py after candidate` → rc 0；**产品调用 rc=3 ×6**（c1/c3/c5/c7/c8/c10）、
  **查询进程 rc=0 ×4**（c2/c4/c6/c9/c11 中 c11 为第 5 个查询，合计 5 次查询 rc=0）、store 行数 2、paused 未变。
- `w06a_evidence.py before|after` → rc 0；`w06a_make_diff.py` → rc 0（529 行）。

## r2.3 新的哈希

| 文件 | sha256 |
|---|---|
| `iso/candidate/processing_demand_store.py` | `7bc5feb0cb5e50227a49ac7322c654f84b04f4b71d9d6578571f0899405b8f7f`（未变） |
| `iso/candidate/w06a_candidate_patch.py` | `113e90b0855400f6563ace77ca2fb16729d1b6b06631deceeeddf1c8991fc87b` |
| `iso/rf_fixed/scripts/source_preparation.py` | `1a837fc0047f31a68d14d9ca1b4487d30b9dc33529cb332c905bd0affe75469e` |
| `iso/rf/scripts/source_preparation.py` | `5ec16eaf0fe480126b680f6e069717ebfc218ae39531372a380cfcc9b91bce46`（生产字节，未变） |

## r2.4 遗留（仍未解决）

1. **OPEN-2 键定义**：是否把请求身份纳入幂等键（当前不含 ⇒ c8/c9/c10 都会静默并入旧需求）；
   以及 `role_set` 的权威来源。
2. **OPEN-1/3/4/5/6** 未签（持久 owner 位置、claim/lease、审核方法、消费/恢复接口、`detected_and_ignored` 归属）。
3. **阻断文案的兼容性**：候选把安全判定与 store 错误拼在同一条消息里；未搜索 RF/FF 中对该文案的文本断言。
4. **候选仍未做 additive migration / 并发 claim / 跨进程 lease 过期**验证。
5. 本 attempt **不构成任何产品实施资格**；候选不得被后续卡直接提升为产品实现。
