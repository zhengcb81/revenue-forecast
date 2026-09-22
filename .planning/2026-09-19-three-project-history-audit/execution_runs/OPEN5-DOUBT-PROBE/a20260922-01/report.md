# OPEN5-DOUBT-PROBE · a20260922-01 · 终报

任务：复验 T2-SIM-OPEN5-RF 模拟裁定 §7 存疑 1/2（父追加：OPEN-4/OPEN-6 存疑面探针 5/6）。
全部实测在 %TEMP%\open5-doubt-probe 隔离副本/隔离 sqlite 上跑；PRODUCT/CW/计划树其余文件零写入、零 git。
冻结断言见 `oracle-lite.md`（先于全部探针写就）。

## 0. 定位勘误（被测对象）

- 存疑原文实锚 = **I-06-A** `handoff.json:146`（阻断文案跨仓文本断言未排查）/`:147`（候选未验证 additive migration / 并发 claim / lease 过期）/`:153`（候选 known-insufficient、UNRATIFIED）。
  裁定所写 `handoff.json:147` 等行号不在 I-06-B handoff（该文件仅 135 行，:44-57/:55/:86 等其余锚确属 I-06-B）。
- 被测候选 PRIMARY：`I-06-A\iso\candidate\processing_demand_store.py`（sha256=7bc5feb0…8b8f7f，与 I-06-A handoff 记载一致）；
  迁移真实函数名 = `DurableDemandStore._initialize()` + `DEMAND_SCHEMA`（OPEN-1 裁定指向的 `_apply_additive_migrations` 是 CW `store.py:1072` 生产机制名）。
- SECONDARY（I-06-B 实际行使面）：`I-06-B\iso\cw\...\processing_demand.py`（=产品 CW 字节 90f232ed…）与 RF 产品 `scripts\processing_demand.py`（fcdfcad8…）。
- 探针 5/6 被测 = CW 产品 `prompt_injection.py`（实测 hash=7b22f239…618，与 I-06-B 记载相符）。

## 1. 逐探针判定

### P1 additive migration — **FAIL**（升级面不成立）
- P1-a fresh 首迁：rc=0，表+索引建出 ✓
- P1-b 同库连迁 2/3 次：rc=0、schema 不变、行数 1→1 无重复 ✓（幂等 ✓）
- P1-b2 N-1 库（缺 request_sha256/request_json/candidate_marker/attempts/lease_owner/lease_until 6 列）：`_initialize` **静默 rc=0 不补列**（CREATE TABLE IF NOT EXISTS 空转），物理表仍 11 列
- P1-c N-1 库旧行 2/2 保留 ✓，但后续代码硬崩：`register()`→`DemandStoreUnavailable: … no column named request_sha256`；`claim()`→**裸** `OperationalError: no such column: lease_until`（连类型化包装都没有）；"新列合理默认"无从谈起（列从未加上）
- ⇒ additive migration 仅在全新库成立；**从 N-1 升级的路径断裂**，且失败形态不一致（一处包装、一处裸抛）

### P2 并发 claim — **PARTIAL**
- 断言 A「恰好一赢家」**PASS**：候选 SQLite store 双进程抢单一 demand_id，5/5 轮 1 赢 1 输（BEGIN IMMEDIATE 生效，无双 running/双写）
- 断言 B「输家有定义拒绝」候选 **FAIL**：输家 `claim()` 仅返回 `None`——无错误码、无文案（refusal={"shape":"None return value","code":null,"text":null}）
- 对照内存 `DemandQueue.claim(demand_id=…)` 双线程同抢（CW 副本 90f232ed + 产品 fcdfcad8 双份）：输家得 **`DemandStateError: demand 'pd-0' is not claimable`**（有定义）✓
- 候选 claim() 无 demand_id 参数（只能抢"最老 ready"），本探针以单 demand 队列等价实现"同一 demand_id"

### P3 lease 过期（C5） — **ABSENT-implement-first**（候选）+ PASS（内存队列）+ 新缺陷
- P3-0 候选 API 面 = `register/list_active/claim`（CLI 仅 list/claim），**无 resume、无 complete**；源内 'resume' 仅命中 docstring `:282 "never resumes anything"`。I-06-B 侧同样无 resume 入口（与 `original-request-resume.json:39-42` 一致）
- P3-a 实测 claim(w1, lease_seconds=1)+睡 1.4s → `getattr(store,'resume')` = **`AttributeError: 'DurableDemandStore' object has no attribute 'resume'`** ⇒ C5（过期 resume ⇒ REJECT）在候选上**不可测**（无 resume 面）——**candidate lacks resume implementation — original doubt CONFIRMED as still-open for the future implementation**
- **新缺陷（搁浅）**：过期后同 owner、第三方 re-claim 均得 `None`，行永远停 `running`（claim 只选 `status IN ('pending','failed')`）；候选也无 complete/expire 回收入口 ⇒ 违背 OPEN-3「lease 过期回收只能显式触发」的"显式触发"形状（根本没有触发点）
- P3-b 内存队列 C5 **PASS**：过期后 `complete()/heartbeat()` → `DemandStateError: lease expired` = REJECT ✓；错 owner → `lease owned by 'w1'` ✓；显式 `expire()` 回 ready、再显式 re-claim 成功 ✓（无自动 resume/scheduler）

### P4 阻断文案跨仓文本断言排查（存疑 2） — 排查**完成**（9 行表见 `04_blocked_message_sweep.md`）
- PINNED×2：`not_reviewed` 令牌（CW resolver.py:918/1078/1088 生产；tests 6+ 处等值断言）；`unknown ruleset hash`（guard.py:98 ↔ test:122 match）
- UNPINNED×5：完整阻断句（唯一产品定义 RF source_preparation.py:154-156，测试仅 `match="not reviewed|blocked"` 宽松正则；另有 2 份手抄副本 candidate patch:139-142 / apply 锚:51-52 当前三份一致）；`demand_store_error=`/`demand_queued`（仅候选 w06a_candidate_patch.py:157/:161 定义，产品零定义零断言）；六个 demand/claim 拒绝串（RF:89,100,102,112,132,134 = CW:103,118,120,130,150,152 逐字相同；测试只钉异常类型）；`{field} must be a lowercase SHA-256`（产品测试零断言）；parser/llm counts 文案（宽松正则）
- ABSENT×2：`cases_json_declared_expectation_missing`（PRODUCT scripts/tests/全仓 *.py、CW src/tests/scripts **全部零命中**；`ruling.md` 本体也无此串）；resume 拒绝文案（无实现）
- ⇒ C8 要求的"排查记录"已交付；C8 的"钉住"仍未满足（点名的完整阻断句 + `demand_store_error=` 两条都未钉）

### P5 格式合法虚构假回执（追加，OPEN-6/OPEN-4 存疑面） — **敞口 CONFIRMED**（3/3）+ 对照 PASS
- P5-a 虚构但格式合法 `evidence_sha256=ffa4c89b…`（无扫描背书）+ status=not_detected **ACCEPTED** 且 `read_prompt_injection_review` 可读回 ⇒ **假回执面存在**；I-06-B N3「只拦格式非法」结论**成立、未收窄**
- P5-b `reviewer="zr302-test-FAKE"` **ACCEPTED** ⇒ reviewer 身份是可冒用自由字符串
- P5-c `detected_and_ignored` 不带 source_sha256/policy_hash **ACCEPTED** ⇒ 双绑定写入侧可选=写入敞口（与 OPEN-6 裁定 C2 描述吻合）
- P5-d 对照 `'ABC'` → `PromptInjectionReviewError: evidence_sha256 must be a lowercase SHA-256`（精确命中）PASS

### P6 并发写回执原子性（追加，OPEN-4/OPEN-6 存疑） — **RECORD-CONFIRMED**（无撕裂；但 last-writer-wins 静默覆盖 + 无锁原语实证）
- Phase A（默认 sqlite timeout=5s）8 进程同写一 document：8/8 commit 成功、**零 lock 异常**、documents 行不丢、metadata 单 key ⇒ **last-writer-wins 覆盖**（7/8 写入被静默顶掉，无历史/无冲突检测）
- Phase A2（timeout=0）：7/8 进程拿到**未包装** `sqlite3.OperationalError: database is locked`（`record_prompt_injection_review` 无任何锁处理/重试，异常裸露给调用方），1/8 写成功
- Phase B（4 写 + 4 读交错）：读者共 658 次 `read_prompt_injection_review`，**0 撕裂读、0 异常**（只见 None（写前）或完整 receipt）；原子性来自单 UPDATE+commit
- 与 REMEDIATION_REGISTER.md:592「grep iso+生产两树 零 lock 原语」**对齐/实证相符**：无锁原语，竞争要么靠 sqlite busy-wait 静默串行化、要么以裸 lock 异常暴露；同文档多 reviewer 互相覆盖无痕迹

## 2. 两个存疑项的回答

**存疑 1（候选 additive migration / 并发 claim / lease 过期 未验证）= RESOLVED-YES（"未验证"缺口已闭合，三行为均实测）**
——但按实测内容分项：additive migration **FAIL**（升级面断裂）、并发 claim **PARTIAL**（排他 PASS、拒绝无定义）、lease 过期 **ABSENT-implement-first**（无 resume/complete 面，C5 不可测）。
若问的是"三行为是否成立"则 **RESOLVED-NO**：两个真缺陷（N-1 迁移崩、running+过期 lease 永久搁浅）+ 一个实现缺失（resume），候选维持 UNRATIFIED/known-insufficient 的判断被实测加固。

**存疑 2（阻断文案跨仓文本断言未排查）= RESOLVED-YES（排查缺口已补，9 行一致性表交付）**
——附属敞口 **REMAINS-OPEN**：C8 的"钉住"未做（现状 2 pinned / 5 unpinned / 2 absent，C8 点名两条均 unpinned）。

## 3. 证据清单（sha256）

| 文件 | sha256 |
|---|---|
| `oracle-lite.md` | a1a3647d3f818dc526335e4de631393e7796d1ec24a987431ac327b21265a4d6 |
| `evidence/01_additive_migration.txt` | 9a41c4de0db9e86905ff708d23ae7458363bb330c33127b55a4fca4e95e5d398 |
| `evidence/02_concurrent_claim.txt` | bd8cad3e7f9ad3b7831e0f6b5ebc4b7c5d51ae610ed88cde58ff4758061ef7a9 |
| `evidence/03_lease_expiry.txt` | e5f998476097998d39bb8e86c9a6fd0d8e7f8abd8182eb0cee9ad5354a605589 |
| `evidence/04_blocked_message_sweep.md` | c1cba4d49bf8defcf798372aa9e919508a15b7ca468bf510e504d5fc33ba5fd9 |
| `evidence/05_fake_receipt.txt` | 6dd180bb5a42577d8636a821b5b4de175483a70c9e8f3afb0d22757abc0c1625 |
| `evidence/06_concurrent_receipt_writes.txt` | ce83826e34ff7b3f4dd056819051b324c147675b458d0f656a1f22705e5774cb |
| `scripts/p1_additive_migration.py` | 4bdffa5e75daa76284ca39eaeab8157b939ffe0aa6d41d9d1ebb7f1ed9cf92e5 |
| `scripts/p2_concurrent_claim.py` | 6634d9600a2b223606869c465bc3e2f24d87daa472235e3fb79ce389b6d6e7ec |
| `scripts/p3_lease_expiry.py` | 03e67b5d0a3baa338c319863cabb379cc7007a1406c087858e4d68bf99e48d42 |
| `scripts/p5_fake_receipt.py` | de1b6a2a2b860be2171c913aeffd4d6def65022d29c2d61c31c333321d6deaff |
| `scripts/p6_concurrent_receipt_writes.py` | c6e2d33399fa3568fa838c36f8ff68b7e83c51af21303ba4a238871e00afc35e |

被测锚点 hash（实测）：candidate `processing_demand_store.py`=7bc5feb0cb5e50227a49ac7322c654f84b04f4b71d9d6578571f0899405b8f7f；CW `prompt_injection.py`=7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618；RF `scripts/processing_demand.py`=fcdfcad8ebd1fc20febf3c157dcd20ad92708fd69d00373ef9a943e5a820afc1；CW `processing_demand.py`=90f232edb7804f78a16c6b4e865255cd607a1d0dc30384fc1cd6faa1833ac88b。

## 4. 纪律自证

- 只写 `execution_runs/OPEN5-DOUBT-PROBE/a20260922-01/**` + `%TEMP%\open5-doubt-probe\**`（隔离 DB/副本）；PRODUCT/CW/计划树其余字节零改动；零 git 命令。
- P4 为纯只读 grep/read 排查；P1/P2/P3/P5/P6 全部 import %TEMP% 副本、sqlite 库建在 %TEMP%。
