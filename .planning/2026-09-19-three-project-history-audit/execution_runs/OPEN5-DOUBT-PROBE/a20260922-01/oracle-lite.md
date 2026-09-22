# OPEN5-DOUBT-PROBE · a20260922-01 · oracle-lite（冻结于任何探针运行之前）

任务：复验 T2-SIM-OPEN5-RF 模拟裁定 §7 存疑 1/2（+ 父追加的 OPEN-4/OPEN-6 存疑面探针 5/6）。
写入边界：只写本 attempt 目录 + %TEMP% 隔离副本/隔离 DB；PRODUCT(revenue-forecast)/CW(company-wiki)/计划其余文件全部只读；不跑 git。

## 定位勘误（先于断言，作为被测对象定义）

- 存疑原文在 **I-06-A** `handoff.json:146`（阻断文案跨仓文本断言未排查）与 `:147`（候选未验证 additive migration / 并发 claim / lease 过期）；
  `:153` = 候选 known-insufficient / UNRATIFIED。裁定把行号写成 `handoff.json` 而 I-06-B handoff 仅 135 行，实锚 = I-06-A handoff。
- 被测候选（PRIMARY）：`execution_runs/I-06-A/a20260919-01/iso/candidate/processing_demand_store.py`
  （sha256=7bc5feb0cb5e50227a49ac7322c654f84b04f4b71d9d6578571f0899405b8f7f，与 I-06-A handoff 记载一致）
  ——含 `DurableDemandStore._initialize()` + `DEMAND_SCHEMA`（SQLite 迁移的真实函数名；OPEN-1 裁定指向的 `_apply_additive_migrations` 是 CW store.py:1072 的生产机制名，候选按其形状重写为 CREATE TABLE IF NOT EXISTS + BEGIN IMMEDIATE）。
- 被测候选（SECONDARY，I-06-B 实际行使面）：`execution_runs/I-06-B/a20260919-01/iso/cw/src/company_wiki/source_catalog/processing_demand.py`
  （sha256=90f232edb7804f78a16c6b4e865255cd607a1d0dc30384fc1cd6faa1833ac88b，与 CW 产品字节一致的纯内存 `DemandQueue`）。
- 阻断文案定义点：RF `scripts/source_preparation.py:153-156`（安全判定）；候选 `w06a_candidate_patch.py:131-164`（`demand_queued`/`demand_store_error=` 子句）。
- 探针 5/6 被测：CW 产品 `src/company_wiki/source_catalog/prompt_injection.py::record_prompt_injection_review`（hash 以实测为准，期望 7b22f239…）。

## 各探针运行前冻结断言

### P1 additive migration（候选 `DurableDemandStore._initialize` / `DEMAND_SCHEMA`）
- P1-a fresh DB：首次 migrate 后 `processing_demands` 表 + 索引存在，rc=0。
- P1-b 重复 migrate（同一 DB 连跑两次）：第二次**不报错、不重建表、不复制行**（幂等）。
- P1-b2 「N-1 schema」DB（同表缺后加列 lease_owner/lease_until/attempts 等）：migrate 后**要么**补列（additive）**要么**显式失败；
  若静默不补列、随后 INSERT 崩溃 ⇒ FAIL（additive migration 不成立）。
- P1-c 带既有行的 N-1 DB：migrate 后旧行全部保留；新增列取合理默认（attempts=0、lease NULL 等）。
- 记录：每次运行 rc、migrate 前后 `sqlite_master` schema dump。

### P2 并发 claim（同一 demand，两个 OS 进程同时 `claim(owner, lease_seconds)`）
- 断言 A：**恰好一个**赢家（只有一行 status=running / 只有一个进程拿到非空 claim）。
- 断言 B：输家得到**有定义的拒绝**（拒绝码/文案可记录）。候选现状 `claim()` 无参 demand 选择 + 返回 None ⇒ 若拒绝只是无文案的 null ⇒ B 判 FAIL(undefined-refusal) 并记录实际形态。
- 辅测：内存 `DemandQueue.claim(demand_id=...)` 双线程同抢 ⇒ 输家应得 `DemandStateError`，记录其确切文案。
- 若 claim 实现不存在 ⇒ ABSENT-implement-first + 精确证据行（候选实有 claim()，故预期可跑）。

### P3 lease 过期（C5：过期后 resume ⇒ 必须 REJECT）
- P3-a 候选：claim(lease_seconds=1) → 睡 >1s → 「resume」。断言：resume 被拒。候选**无 resume API** ⇒ 预期记 ABSENT（无 resume 实现，C5 无法在候选上满足/违反），
  同时实测最接近面：过期后原 owner complete/续租、以及第三人 re-claim 是否成功——记录**实际**行为（含 running+lease 过期是否永远无人能再 claim 的搁浅面）。
- P3-b 内存 DemandQueue：lease_seconds 极小 + 推进 now 过期后 complete() ⇒ 必须 `DemandStateError("lease expired")`（= REJECT，符合 C5）；expire() 后须显式 re-claim 才回到 running。
- 禁止断言任何数值规范（300s/1s 均为夹具）。

### P4 阻断文案跨仓文本断言排查（存疑 2 / C8 现状）
对下列每条文案建表：消息 → 定义处 → 断言处（测试是否钉住确切文本）→ 漂移判定：
1. `not_reviewed` 状态令牌（RF source_preparation.py:152-156 / CW prompt_injection.py 及 envelope 产生点）
2. `prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status=...)` 全文
3. `cases_json_declared_expectation_missing`（预期：两仓零命中 ⇒ ABSENT，记录检索范围）
4. `demand_store_error=` 附加子句、`demand_queued demand_id=…`（候选 w06a_candidate_patch.py）
5. demand/claim 拒绝文案：`no ready demand to claim` / `is not claimable` / `lease expired` / `lease owned by` / `no demand`
6. resume 拒绝文案（若有）
断言：每条标注 pinned（有测试钉确切文本）/ unpinned（仅类型或宽松正则断言）/ drifted（定义与断言不一致）/ absent。

### P5 假回执面（OPEN-6 存疑 / OPEN-4 存疑面；`record_prompt_injection_review`）
- P5-a 格式合法但虚构 `evidence_sha256`（任意 64 小写 hex，无真实扫描背书）+ status=not_detected ⇒
  被拒 ⇒ I-06-B N3 结论**收窄**（如实报）；被接受 ⇒ 证实「只拦格式非法」，假回执面存在。
- P5-b reviewer="zr302-test-FAKE" 自由字符串 ⇒ 记录是否可冒用。
- P5-c 不带 source_sha256/policy_hash 写 status=detected_and_ignored ⇒ 预期被接受（双绑定可选=写入侧敞口）；若被拒则如实报。
- P5-d 对照：格式非法 evidence（如 'ABC'）⇒ 必须 `PromptInjectionReviewError('evidence_sha256 must be a lowercase SHA-256')`。
- 全部在隔离 sqlite（自有 documents 表）上跑。

### P6 并发写回执原子性（OPEN-4/OPEN-6 存疑）
- 8 个 OS 进程并发 `record_prompt_injection_review` 同一 document_id（不同 evidence/reviewer）+ 一组「写+evaluate 读」交错：
  - 记录：是否有未捕获 `database is locked`（逐进程 rc/traceback）、回执行丢失（最终 metadata_json 中 receipt 数/形态）、读到半写状态（读侧是否抛异常或读到截断 JSON）。
  - 语义记录：同文档多次写是 last-writer-wins 覆盖（单 key）还是追加；读后是否总能读到**完整** receipt。
  - 与 REMEDIATION_REGISTER.md §二十一 L592「零 lock 原语」陈述对齐或矛盾（如实记）。

## 判定词汇

每探针：PASS / FAIL / ABSENT-implement-first / RECORD-ONLY（探针 5 的 OPEN-6 归属不判对错，只记实测面）。
两个存疑项回答：RESOLVED-YES / RESOLVED-NO / REMAINS-OPEN，附证据文件。
