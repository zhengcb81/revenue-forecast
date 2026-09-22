# 模拟裁定（owner 全权授权 role-play）· 待 owner 终确 · 非外部方真实签署

> 本文件系 owner 全权授权下的**模拟裁定**，供 owner 终确（final confirmation）前审阅。
> 记录性质：**owner-authorized simulated adjudication, pending owner ratification — NOT a real external signature**。
> 落点说明：按任务指令，本裁定落在本 attempt 目录（`execution_runs/T2-SIM-OPEN5-RF/a20260922-01/ruling.md`），
> **不在任何函件上签字**、**不改任何既有载体**。若 owner 终确采纳，由编排层按函 A §4 转录至各卡载体并登记 `RESPONSES.md`。

---

## 1. 身份与管辖域

- **身份**：RF（revenue-forecast）**消费 owner**（consumer owner），TIER-2 外部方 #3。
- **管辖域**：下游消费语义（forecast 语义稳定性、消费/恢复路径的 fail-safe 行为、消费契约稳定）。
  即：一条 processing demand 被消费、原请求被恢复时，**下游 forecast 消费者看到的世界必须不被伪造、不被静默合并、不被默认值填充**。
- **本次裁定项**：函 `A_DW06_OPEN-4-5-6.md` 的 **OPEN-5**（覆盖序映射 T2-3 ↔ OPEN-5 ↔ RF 消费 owner）。
  **已核验归属**：该函自身小节标题 `## 2. OPEN-5 —— 消费 / 恢复命令与原请求恢复接口（RF 消费 owner）`（第 88 行）与收件表（第 8 行）
  一致指派本角色 OPEN-5；函 A **未**给本角色分派其他或相邻项。OPEN-4（第 43 行）、OPEN-6（第 122 行）分属他方，本裁定不越域。
- **相邻但不属本裁定**：函 `C_I-05-C_gap2_gap3.md` 的 GAP-2（`consumer_analysis` 精确入口）同属本角色名下，但属**另一封函**的另一项；
  本裁定**不**代答 GAP-2（见第 6 节不予授予项 7），只在条件 C6 锁定两函**缺失语义必须一致**（函 C §1.3 对齐要求）。

## 2. 裁定原文引用（OPEN-5 逐字，函 A `outward_requests/A_DW06_OPEN-4-5-6.md`）

节标题（第 88 行）：

> ## 2. OPEN-5 —— 消费 / 恢复命令与原请求恢复接口（RF 消费 owner）

§2.1（第 90–96 行）：

> ### 2.1 关键事实：该接口**今天不存在**
>
> `handoff.json` 的 `still_awaiting_other_parties.OPEN-5.fact` 原文：
>
> > **"the interface DOES NOT EXIST today; it must not be pretended into existence"**
>
> ⇒ 请贵方**确认这一事实**，并裁定**它应当是什么**，而不是裁定「它已经是什么」。

§2.2（第 98–108 行）：

> ### 2.2 待裁的四件事
>
> 1. **消费入口**：从哪个真实 CLI / 函数入口消费一条 active demand？
>    与 `I-05-B` 的「消费者读取已验证字节」如何衔接？
> 2. **恢复接口**：原请求被打断后，恢复路径的**输入**是什么
>    （demand ID？原 request 工件？二者都要），**输出**是什么（补产指令？新工件？）？
> 3. **持久化介质**：与 OPEN-1 已裁定的「单一 CW 持久 owner
>    （扩展 `src/company_wiki/source_catalog/store.py`，`catalog.sqlite3`，经既有
>    `_apply_additive_migrations`）」**同一库同迁移机制**，还是另有介质？
> 4. **权限**：谁有权触发恢复？是否需与 OPEN-3 已裁的「显式单次 `claim(owner, lease_seconds)`」
>    共用同一授权？**不得**自动 resume、**不得**起后台 scheduler（OPEN-3 已裁明文）。

§2.3（第 110–118 行）：

> ### 2.3 ⚠️ 已知的不一致（请一并处置）
>
> `handoff.json` 明确记录：
>
> > "the candidate's key does NOT satisfy the newly-ruled OPEN-2 option A, so the candidate is
> > now **known-insufficient** on that point and must be revised before it can be promoted."
>
> 即：**候选实现仍为 UNRATIFIED**，且**已知不足**。请贵方在裁定 OPEN-5 时明确：
> 消费入口的设计是否**依赖**候选实现被修订，若依赖，请写明**修订后的接口契约**。

§4 回执要求（第 147–152 行，适用于本裁定）：每项须含 **选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案**；
不得以「按最佳实践」代替决定；不在函上签字。

## 3. 【裁定】**CONDITIONAL**（有条件裁定）

- **事实确认（§2.1）**：✅ **确认**——消费/恢复接口**今天不存在**，本裁定是「它应当是什么」的规范裁定，
  **不是**对任何既有实现的验收。
- **对 §2.2 四件事**：四项均给出权威选择（下第 4 节），但**不授予无条件放行**。原因：候选实现已知不足（§2.3）、
  消费语义的关键相邻判定（OPEN-4 失效矩阵、OPEN-6 `detected_and_ignored` 下游可见性）尚未出裁、
  GAP-2 缺失语义仍阻塞（登记册 :902）。在这些条件下无条件 APPROVE 等于替未验证的行为背书——拒绝。
- **对 §2.3**：消费入口设计**明确依赖**候选修订；**修订后的接口契约**见第 4 节【§2.3 附】，并以条件 C1–C8 可检验收口。
- **结论效力**：满足 C1–C8 全部检验通过后，消费/恢复接口方可实施；任一条件未过 ⇒ 该接口**维持不存在**
  （比伪造一个存在更可接受——`handoff.json:240` 明文）。

## 4. 理由（逐项：选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案；证据均为实读）

**实读证据基线（本裁定引用的字节，sha256 实算）**：
`scripts/source_preparation.py` = `91a6dc32466e9d67…c6ebf4d`；
`scripts/processing_demand.py` = `fcdfcad8ebd1fc20…5a820afc1`（与 `I-06-A/a20260919-01/handoff.json:94` 记载的
`fcdfcad8…afc1` 一致 ⇒ 该契约自 I-06-A 以来**未漂移**）；
`scripts/company_wiki_source.py` = `7d1bd8f9d9122dc4…ca9e48ce`；
`scripts/model_registry.py` = `62f864b9ab3f144e…dd985081`。

### 4.0 事实前提（§2.1）

- `execution_runs/I-06-A/a20260919-01/handoff.json:235-241`：`OPEN-5.fact = "the interface DOES NOT EXIST today; it must not be pretended into existence"`。
- 同卡 `decision.md:63-66`：「候选只提供 `list` / `claim` 两个只读/单次授权命令；『从原请求恢复』的接口……未实现」。
- `execution_runs/I-06-B/a20260919-01/after/original-request-resume.json:39-42`：`original_request_resume_cli = blocked, "no demand→source_preparation resume interface"`。
- 生产侧实读：`scripts/source_preparation.py:33` `_preparation_demands = DemandQueue()` 为**模块级内存队列**，
  其注释 `:29-32` 自认「In-memory queue (persistence is a later phase)」；全仓 grep 无任何 consume/resume CLI。
  ⇒ **确认：接口不存在，且现状下跨进程不可恢复**（与 `before/demand.cross-process.json` 的 `database_exists=false` 互证）。

### 4.1 待裁 1 —— 消费入口

- **选择**：消费入口 = **RF 侧唯一生产编排入口 `scripts/source_preparation.py`**（其 docstring `:1` 自我定义
  「WU-1000: the single production orchestration entry — source preparation」，CLI `main()` `:191-227`，退出码 0/1/2/3 `:10-11`）；
  demand 的**读取/查询面**留在 CW 单一持久 owner（OPEN-1 选项 A），但**消费动作（恢复执行）必须重入 `prepare_source()` 原链**，
  不得另设旁路入口。与 I-05-B 的衔接：恢复产出的字节必须经
  `company_wiki_source.verify_artifact_reads`（`scripts/company_wiki_source.py:231-249`，
  「`selected_roles` is the PLAN … these events prove IO」）产生 `verified_read_events`（`content_sha256_actual` 对 `declared`、`bytes_read`、`source_sha256`），
  并经 `select_artifact_roles`（`:154-228`）的 request-scoped 产出范围（`_production_scope` `:129-151`，REM-11 后 bundle=None 与 bundle 在场同一规则）。
- **理由**：恢复路径与首跑路径必须是**同一条**受同一套 fail-closed 检查约束的链。首跑链上已有消费侧硬检查：
  `prompt_injection_status == "not_reviewed"` ⇒ 阻断（`source_preparation.py:153-156`）；
  `parser_calls/llm_calls` 缺席 ⇒ 「fail closed instead of fabricating 0」（`:157-162`）；
  resolution envelope 缺失 ⇒ fail closed（`:123-128`）。只有重入原链，这些检查对恢复路径**自动生效**。
- **反例**：若恢复走旁路（例如直接从 demand 行拼装 `RevenueSourceRecord`），则**恰好在恢复路径上**可以绕过
  「not_reviewed 阻断」——而制造该 demand 的原因就是 not_reviewed。恢复路径会成为全链最弱一环：
  被阻断的请求经『恢复』反而未经安全判定进入下游 forecast。
- **兼容影响**：下游消费契约不变——恢复产出仍是 `prepare_source()` 的 record + `reuse_receipt`
  （`:171-184`，含 `artifact_read`/`producer_events`/`artifact_read_events`/`artifact_failed_events`），
  `revenue_forecast.py` 继续只消费已验证 source record（`:7-8`：「stays pure」）。
- **恢复规则**：恢复执行失败 ⇒ 与首跑同一错误契约（JSON `error_code` + rc=3，`:221-224`），demand 行**保持 open**，不得半途关闭。
- **被拒绝的替代方案**：① 新建独立 `resume` 脚本自行拼装 record（旁路检查，如上反例）；② 让 CW 侧 worker/scheduler 自动消费
  （OPEN-3 明文禁止）；③ 以 `select_artifact_roles` 的 PLAN 代替实际读取证据（`source_preparation.py:141-143` 注释明言
  「selection alone cannot prove bytes were consumed」）。

### 4.2 待裁 2 —— 恢复接口的输入与输出

- **选择**：
  - **输入 = 二者都要**：`demand_id` **且** 原 request 工件（request JSON 字节），并**强制绑定校验**：
    从所给 request 字节重算 `request_sha256`，必须**等于**该 demand 行登记的原请求绑定哈希；不等 ⇒ fail-closed 拒绝（不找「最接近的 demand」）。
  - **输出 = 补产指令 +（经原链执行后）原契约的 RevenueSourceRecord**；恢复接口**本身不直接产出、不改写任何 forecast/publication 工件**。
    补产指令 = 结构化（demand_id、request_sha256、gaps、request-scoped `producer_events`、next_action），随后重入 `prepare_source()`。
- **理由**：(a) OPEN-2 选项 A 已裁「幂等键必须含请求身份」（`handoff.json:200-208`，`source_sha256 + review_policy + role_set + request identity`，
  request identity 覆盖 `as_of_date/target/payload digest`）⇒ demand 是**按请求**的，恢复必须证明「我恢复的就是登记的那一次请求」；
  (b) 仅 demand_id 不够：持有 id 者未必持有原请求字节，行内 `request_json` 若被当作唯一真相，便无人校验「现场在恢复什么」；
  仅 request 工件也不够：无法证明恢复者对哪条持久 demand 行使 lease 权（OPEN-3）。
  (c) 输出不产 forecast 工件：`revenue_core.py:427`「invest-* consumers must only accept `"formal"` artifacts」、
  `revenue_publication.py:29,61`（消费者验证入口 = `validate_forecast_output`）——恢复若另开一条工件铸造通道，
  就是 REM-01 类缺陷（登记册 :12：`attestation_status="host_signed"` 纯标签、消费者完全不验签）的同族重造。
- **反例**：c8/c9/c10 实测（`handoff.json:81-90`、`decision.md:104-115`）：同 source/policy/roles 仅 `as_of_date` 不同的第二个请求
  （实际哈希 `4bddf9e6…`）被并入首请求 demand，行内 `request_sha256` 仍是 `d8afcf31…`。
  ⇒ 若恢复只要 demand_id（或只信行内 request_json），恢复者可以**拿着 A 请求的字节恢复 B 请求的 demand 而无任何告警**——
  as_of_date 错接进 forecast 时间轴，直接污染预测语义。这正是消费侧必须设 C3 的原因。
- **兼容影响**：补产指令的 gaps/角色词汇与 `select_artifact_roles`/`_production_scope` 同构（不造第二套角色语言）；
  record schema 不变（`reuse_receipt` 形状稳定，`:171-184`）。
- **恢复规则**：绑定校验失败 / 链上任一 fail-closed 触发 ⇒ demand 保持 open + 结构化错误；`complete` 只能在重入链**成功产出 record 之后**
  按 OPEN-3 lease 语义落（`processing_demand.py:155-172` 的 complete 语义、须持 lease）。
- **被拒绝的替代方案**：① 仅 demand_id（如上反例）；② 输出直接给「新工件」（绕过 `validate_forecast_output` 消费入口）；
  ③ 补产指令里内嵌默认值/估数填 gaps（与「省缺即抛」的今日产品语义相反——`model_registry.py:402-413` 注释与实现：
  「an omitted driver is legal ONLY when `spec.defaults` carries an [explicit default]」，否则 `ModelRegistryError`；
  同族先例 `source_preparation.py:159-162`）。

### 4.3 待裁 3 —— 持久化介质

- **选择**：**与 OPEN-1 已裁选项 A 同一库、同一迁移机制**——扩展 CW `src/company_wiki/source_catalog/store.py`、
  `catalog.sqlite3` 增表、经既有 `_apply_additive_migrations`。**不另立介质**。
- **理由**：单一 owner ⇒ 「当前是否存在该请求的 active demand」只有一个真相源。候选自己的 option-B 形状
  （独立 SQLite 文件，`decision.md:30`）已被 OPEN-1 否决（`handoff.json:197`：「Do NOT adopt the attempt's internal option-B shape」）。
- **反例**：候选的临时库位于 `%TEMP%\w06a\…`，其恢复规则是「删除即可」（`decision.md:100`）。
  作为探针无妨；作为生产恢复规则则意味着**唯一记录『有请求被阻断』的行可以随临时目录消失**——
  消费者永远丢失『还有一次未完成的请求』这个事实。双库并存同理：消费端须先回答『哪个库权威』，这本身就是缺陷。
- **兼容影响**：随 additive migration 增表，无破坏性变更；**必须**明确 demand 行生命周期——
  `decision.md:25` 已指出 OPEN-1 选项 A 的风险「prune/archiving 会连带影响」⇒ demand 行必须**豁免**于文档目录的 prune/archival，
  或有显式 terminal 态保留规则（否则 I-15-A 类清理会连带删掉未决需求）。
- **恢复规则**：迁移失败/写失败 ⇒ C7 契约 fail-closed（`decision.md:88`、`handoff.json:214` 已裁采用：
  rc=3、stderr 含安全判定 + `demand_store_error=` 附加子句、**无** `demand_queued`、行数不变）；**不做内存兜底**。
- **被拒绝的替代方案**：OPEN-1 表中的选项 B（独立 SQLite）/ C（RF 独立 DB）/ D（复用 JSONL 文件队列）（`decision.md:23-28`）；
  RF 侧建库（会把「CW 单一 owner、RF 只提交/查询」倒置）。

### 4.4 待裁 4 —— 权限

- **选择**：**与 OPEN-3 已裁的显式单次 `claim(owner, lease_seconds)` 共用同一授权，不多不少**。
  恢复 = claim 之后 **lease 有效期内**的动作；触发恢复者必须是该 demand 的**当前 lease owner**（resume 前置 = 有效 claim）。
  **不得**自动 resume、**不得**后台 scheduler、lease 过期回收只能显式触发（OPEN-3 明文，`handoff.json:221`）。
- **理由**：claim 语义已在 ZR-507/RF 契约里有可执行定义（`processing_demand.py:92-134`：claim 授 lease、
  `_require_lease` 校验 owner 与有效期、越权 ⇒ `DemandStateError`）。恢复接口复用它，权限面只有一套；
  另设授权主体会产生第二条『可以动手重跑请求』的路径。
- **反例**：若仅凭持有 request 工件即可触发恢复，则任何拿到请求 JSON 的进程都能在无 lease 下重跑原请求，
  与持 lease 的 worker 并发写同一 demand ⇒ 与「并发 claim 未验证」（`handoff.json:147`）叠加成未定义行为。
- **兼容影响**：无新增权限概念；错误面沿用 `DemandNotFoundError/DemandStateError`（`processing_demand.py:39-44`）。
- **恢复规则**：lease 过期后 resume ⇒ 拒绝（fail-closed），须显式重新 claim；崩溃恢复 = 显式 `expire` 等价物 + 显式重 claim，
  不自动接管。
- **被拒绝的替代方案**：① 宽松权限（持 request 即可恢复）；② 自动 resume worker；③ 后台 scheduler 扫描恢复（OPEN-3 禁）；
  ④ 把 lease 秒数写死为规范值（数值不在我职权，见第 6 节 6）。

### 4.5 【§2.3 附】修订后的接口契约（消费入口所依赖的候选修订）——**是，依赖修订**

候选**明确**依赖修订方可支撑消费入口。修订后的接口契约（消费侧要求的最小闭集）：

1. **幂等键**：`demand_key = sha256(canonical_json({source_sha256, review_policy, role_set, request_identity}))`，
   `request_identity` 覆盖 `as_of_date / target / payload digest`（逐字对齐 OPEN-2 选项 A，`handoff.json:205`）。
   候选的三元组键（`decision.md:36-37`）**不得**作为晋升契约。
2. **原请求绑定列**：保留 `request_sha256` **且** `request_json`（候选表已有，`decision.md:38-40`）；
   `request_sha256` 是恢复时的**校验锚**（4.2 输入绑定），不得只存不验。
3. **状态枚举**：沿用既有 ZR-507/RF 契约闭集 `pending/running/completed/failed/terminal_failed`
   （`processing_demand.py:26,100,178`；两侧「pinned by identical contract tests」`processing_demand.py:9-10`），
   消费语义绑定：`completed` = 原请求已成功重跑并产出 record；`terminal_failed` = 放弃且**必须**留 reason；
   `failed` = 可显式重试（backoff 语义沿用 `:174-198`）。
4. **CLI 最小面**：`list`（只读）、`show --demand-id`、`claim(owner, lease_seconds)`（显式单次）、
   `resume --demand-id --request-file`（仅 lease owner）、`complete`/`fail`（lease 内）。
   **无** `resume --all`、**无**自动推进。
5. **错误契约**：登记与恢复两路径同用「安全判定 + `demand_store_error=` 附加子句」（OPEN-2b 已裁采用，`handoff.json:214`）；
   阻断文案的跨仓文本断言须排查后钉住（`handoff.json:146` 悬置项，见第 7 节）。
6. **gaps 词汇**：与函 C 的 `missing / unsupported / not_applicable` 三值**不得混同**（`C_I-05-C_gap2_gap3.md:72-74,136`），
   demand 行记录角色缺失时用同一套语义（见条件 C6）。

## 5. 条件逐条（全部可检验；C1–C8 全过 ⇒ 本裁定的条件解除）

- **C1（键含请求身份）**：修订候选后重跑 c8/c9/c10 型探针（真实 `source_preparation.py` CLI），
  断言：仅 `as_of_date` 不同的两个请求 ⇒ **两个不同** `demand_id`；行内 `request_sha256` == 该请求实际哈希。
  检验物：探针 JSON（类 `after/request-to-demand-binding.json` 形态）。
- **C2（恢复不绕门）**：对 `prompt_injection_status=not_reviewed` 的 demand 执行 resume ⇒ **仍被阻断**
  （`source_preparation.py:153-156` 同一错误契约），直至审核状态真实翻转；`parser_calls/llm_calls` 缺席时 resume ⇒ fail-closed（`:157-162`）。
  检验物：两条反例测试 + rc/错误码记录。
- **C3（输入绑定）**：`resume --demand-id X --request-file mutated.json`（改 `as_of_date`）⇒ **拒绝**并保持 demand open；
  正确字节 ⇒ 通过。检验物：正反两例。
- **C4（同库同迁移 + 生命周期）**：demand 表经 `_apply_additive_migrations` 落 `catalog.sqlite3`；
  文档 prune/archival **不删除**非 terminal demand 行（或显式 terminal 保留规则入迁移注释/文档）。
  检验物：迁移文件 + 一次 prune 后非 terminal 行仍在的测试。
- **C5（权限=OPEN-3）**：无有效 lease 的 resume ⇒ `DemandStateError` 等价拒绝；lease 过期 resume ⇒ 拒绝；
  全程无自动 resume、无后台 scheduler（grep 证明无 scheduler 启动点）。检验物：三例测试。
- **C6（缺失语义与函 C 一致）**：demand 的角色缺失记录使用 `missing / unsupported / not_applicable` **可区分**三值
  （对齐 `W05C-N3`，函 C `:72-74`）；`consumer_analysis` 缺入口时**不得**记为 `not_applicable` 或伪装 `ok`；
  在 GAP-2 仍阻塞期间（登记册 :902「§12 仍 GAP-2=阻塞/GAP-3=待裁」）该角色只能落**阻断/missing**态。
  检验物：schema 字段 + 每枚举值一测。
- **C7（输出不越界）**：resume 全程**零** forecast/publication 工件写入；产出仅为 record + `reuse_receipt`
  （形状 `source_preparation.py:171-184`）与 `verified_read_events`（`company_wiki_source.py:240-247` 字段集）。
  检验物：一次端到端 resume 后的产物清单 + `content_sha256_actual == declared` 断言。
- **C8（错误契约钉住）**：登记/恢复两路径的阻断文案（安全判定 + `demand_store_error=` 子句）完成跨仓文本断言排查并钉住
  （处置 `handoff.json:146` 悬置项）。检验物：断言清单 + 排查记录。

## 6. 不予授予项（明确不给的东西）

1. **不授予**「接口已存在」或任何对 UNRATIFIED 候选的验收/晋级：候选仍 `known-insufficient`
   （`handoff.json:153`），本裁定不使其晋升，任何后续卡不得引用本裁定当作候选已 ratify。
2. **不授予**恢复路径任何形式的放宽：无默认值填充、无缺席即 0、无「先恢复后补审」。
   今日产品语义是**省缺即抛**（`model_registry.py:402-413`：缺显式 default ⇒ `ModelRegistryError`；
   OWNER_DECISIONS.md :69/:228 同向裁定），恢复接口不得反向漂移。
3. **不授予、不预判 OPEN-4 域**：回执失效矩阵（何种变更使旧回执失效、即时还是读时、作废重审 vs 增量补审）属 OPEN-4 两收件方。
   本裁定仅锁消费侧底线：**消费只接受有效且绑定完好的审核结论，`tampered/ignored/expired/absent` 一律不可消费**
   （词汇取自 I-06-B 实测 cache_state：`handoff.json:44-57`）；OPEN-4 出裁后若与此底线冲突，冲突项以 OPEN-4 为准并回本角色复核。
4. **不授予、不预判 OPEN-6 域**：`not_detected / detected_and_ignored` 的**判定归属**属安全 reviewer。
   消费侧底线（作为兼容要求记入条件）：`detected_and_ignored` 在 I-05-B 消费 / I-06-B 恢复必须**可见且为独立状态**，
   不得被静默过滤为 clean——但这只是消费侧要求，**不构成**对该状态归属或授权忽略机制的裁定。
5. **不授予任何数值规范**：lease 秒数、回执 TTL 等一律不写入规范。注意 I-06-B 的 `3600s TTL`
   （`handoff.json:55` N2c 实测）是**测试夹具值**，本裁定**不**核准其为产品默认——数值须按函 A/B 的数值纪律另裁。
6. **不授予**自动 resume、后台 scheduler、`resume --all`、无 lease 的恢复、以删库/清临时目录为生产恢复规则。
7. **不代答函 C 的 GAP-2**（`consumer_analysis` 精确入口路径 / DAG 入边 / LLM 能力边界）：那是另一封函的另一项回执，
   本裁定只锁 C6 的一致性约束。不在本裁定扩大签署范围。
8. **不在任何函件上签字**；本裁定不改变任何卡的 `status`/`reviewer_status`（I-06-A 维持 `blocked`，
   本裁定只是三道门之一的**条件性**回执）。

## 7. 未验证 / 存疑项

### 存疑项__initial（原叙述，逐字保留，2026-09-22 首裁时点）

1. **候选未验证项原样未解**：`additive migration / 并发 claim / lease 过期` 均未验证（`handoff.json:147`）——
   C4/C5 只给出判据，未给通过证据；实施卡须补。
2. **阻断文案跨仓文本断言未排查**（`handoff.json:146`）——已收进 C8，当前仍是敞口。
3. **RF `source_preparation.py` 字节漂移**：I-06-A 绑定 `5ec16eaf…ce46`（`handoff.json:93`）、
   I-06-B 运行后 `8070d60d…31e7`（其 `handoff.json:86` 自记「CHANGED BY ANOTHER CARD」）、
   本裁定实读 = `91a6dc32…bf4d`。⇒ 本裁定引用行号以**今日磁盘字节**为准；实施时若再漂移，须重核 C2/C7 的行号锚。
   （对照：`processing_demand.py` = `fcdfcad8…afc1` 三处一致，无漂移。）
4. **简报所称 commit `5fd82de7` 未获记录佐证**：`REMEDIATION_REGISTER.md` 仅见 `ec307d20`（:965，「PROMOTION 五脚本，770+/64−」）；
   `OWNER_DECISIONS.md` 无 `5fd82de7` 命中。按「no git」约束未跑 git 核验 ⇒ 该哈希**存疑，未采信**；
   但其指称的产品语义（model_registry 省缺即抛）已由**今日磁盘字节**独立证实（`model_registry.py:402-413`），
   guardrails caller-side 对齐一项**未独立核验**。
5. **GAP-2 状态系转引**：「GAP-2=阻塞 / GAP-3=待裁」取自登记册 :902 对 §12 的复述（该册存在重复 §11–§20 编号系，:905），
   未直接读到 §12 原行；不影响 C6 的约束力，但引用时按转引对待。
6. **OPEN-4/OPEN-6 未裁带来的残余耦合**：若 OPEN-4 的失效矩阵选择「作废重审」而非「增量补审」，
   或 OPEN-6 裁定 `detected_and_ignored` 下游**被过滤**，两者都会反压消费/恢复契约——届时本裁定的 4.1/4.2 须随其结论做一致性复核
   （本裁定已预留该接口：第 6 节 3/4 的「出裁后复核」句）。

### 存疑项__reverified（解析态）

> **更新约定（owner 指令经父 agent 转达，2026-09-22）**：本节在探针/实证回报**到齐后**逐条落定；
> **裁定正文（第 1–6 节）与条件 C1–C8 一字不改**。若实证推翻或限缩某条裁定前提，仅如实标注
> 「**前提变化**」并指向受影响条款，**不自行改判**（改判 = 重新呈报 owner 终确）。
> 证据来源分工：存疑 1/2 = 父派探针（I-06-B 候选隔离：additive migration / 并发 claim / lease 过期三探针
> + 阻断文案跨仓文本断言排查）；存疑 3/4/5 = 父并行实证；存疑 6 = 结构性保留（OPEN-4/OPEN-6 出裁后复核，
> 非本轮证据范围）。**本轮不重跑任何探针。**

| # | 存疑项（对应 initial） | 证据 | 解析态（终值三选一） |
|---|---|---|---|
| 1 | 候选 `additive migration / 并发 claim / lease 过期` 未验证（`handoff.json:147`） | 批 #2 六件全齐（探针官终报 + 证据 sha256） | **已解除（终格）**：「未验证」缺口闭合；内容分项 FAIL/PARTIAL/ABSENT **坐实条件必要性、加固 UNRATIFIED**；留置 = `FIX-W06-GAPS` 10 组修复复审后并入 |
| 2 | 阻断文案跨仓文本断言未排查（`handoff.json:146`） | 批 #2 P4 排查报告（9 行表） | **已解除**（排查缺口已补）+ C8 钉住留置实施（`P4-SCOPE` 修复卡） |
| 3 | RF `source_preparation.py` 字节漂移 | 父实证批 #1（内容链 blob pin） | **已解除**（良性：两因 + 一测量伪影更正） |
| 4 | commit `5fd82de7` 未获记录佐证 | 父实证批 #1（git 实证 + 复审 `399f4e60…`） | **已解除** |
| 5 | GAP-2 状态系登记册 :902 转引 | 父实证批 #1（`OWNER_DECISIONS.md:165` 一手出处） | **已解除**（附编号碰撞警示） |
| 6 | OPEN-4/OPEN-6 残余耦合 | 双方裁定原文 + 三方 (c) 文本到齐 | **已解除（终格）**：两反压分支双双相容、零反压；吸收为边界补充记 7 条；留置 2 项落地核验（实施检验面，不属裁定敞口） |

#### 复验记录（逐条；实证批 #1 + 批 #2 六件全齐；存疑 1–6 全部终格，2026-09-22）

**1 → 已解除（终格：「未验证」缺口闭合，三行为均实测）+ 内容分项坐实条件、加固 UNRATIFIED**
探针官终报双存疑回答：存疑 1 = **RESOLVED-YES**（「未验证」缺口闭合）；按内容分项 = **FAIL/PARTIAL/ABSENT**
——若问「三行为是否成立」则 **RESOLVED-NO**（2 真缺陷 + 1 实现缺失）。二者不矛盾：本存疑本体 = 「未验证」，
现验证完成；验证结果**坐实本裁定条件的必要性、加固 §6.1 UNRATIFIED 不授予**。**无前提变化**。
六件终值（证据 sha256：01=`9a41c4de…`/02=`bd8cad3e…`/03=`e5f99847…`/04=`c1cba4d4…`/05=`6dd180bb…`/
06=`ce83826e…`/oracle-lite=`a1a3647d…`）：
- **P1 = FAIL（坐实 C4 + 4.3）**：升级路径断裂——N-1 库 `DurableDemandStore._initialize()` 静默不补列、
  register→`DemandStoreUnavailable`「no column named request_sha256」、claim→**裸** `OperationalError`
  「no such column: lease_until」、旧行保但新列永加不上。⇒ C4 迁移判据必须覆盖 **N-1 库升级路径**；
  claim 裸抛 = **错误面欠定义化第 1 处**（坐实 4.4）。
- **P2 = PARTIAL（坐实 C5/4.4）**：A（恰好一赢家）5/5 ✓；B 输家裸 `None` FAIL（**错误面欠定义化第 2 处**）。
- **P3 = ABSENT + 新缺陷（坐实 4.4/C5）**：无 resume/complete（C5 候选上不可测；内存队列侧 lease-expiry
  全 PASS）；running + lease 过期需求永久搁浅、无显式回收入口（违 OPEN-3「显式 expire 等价物」形状）。
- **P4 = 9 行表**（已录存疑 2；PINNED×2 / UNPINNED×5 / ABSENT×2，含确认本裁定 0 命中该串）。
- **P5 = 敞口 CONFIRMED 3/3（坐实 §6.3 消费底线 + 边界补充记 2/3 + REM-01 引用）**：假回执 / 冒名 /
  无双绑定三形态均可过候选 + 对照 ✓ ⇒ 候选审核面**不验签、可伪造**——消费侧绝不可以现状放行，
  印证 §6.1/§6.2 不授予与「消费只接受有效且绑定完好的审核结论」底线。
- **P6 = RECORD-CONFIRMED 两缺陷 + 三绿**：单 key 静默覆盖丢写 7/8（并发登记互相吃掉——4.2 反例族
  「静默合并/覆盖」坐实）、`timeout=0` 裸抛 `OperationalError`（**错误面欠定义化第 3 处**）；
  三绿 = 8/8 写、零 lock 异常、658 交错读零撕裂。
**错误面欠定义化三处汇总**（P1 claim 裸抛 / P2-B 裸 None / P6-B `timeout=0` 裸抛）⇒ 全部归
`FIX-W06-GAPS` 修复面，按 4.4 错误面（`DemandNotFoundError/DemandStateError` 语义）定形后钉住。
**FIX-W06-GAPS = 10 组修复面**（P1×3 / P2-B / P3-A/B / P4-SCOPE×4 形态 / P5-a / P5-c / P6-A / P6-B），
副本内修、before/ 留旧、红绿可证；落定复审后以「实证 FAIL → 已修复（复审后）」终表并入呈 owner 终确。
**定位勘正（记录）**：候选锚 `7bc5feb0…8b8f7f`（与 `handoff.json` `r2_hashes`
`iso/candidate/processing_demand_store.py = 7bc5feb0cb5e5022…b8f7f` 互证）；迁移真实名
`DurableDemandStore._initialize()+DEMAND_SCHEMA` = **候选内自命名**——最终契约以 OPEN-1 选项 A 形状为准
（CW `store.py` + `_apply_additive_migrations`，本裁定 4.3 / 4.5 条 3），实施时**不得**沿用候选形状。

**2 → 已解除（排查缺口已补）+ C8 钉住留置实施（无前提变化）**
P4 排查报告（`04_blocked_message_sweep.md` 9 行表）实测结论：
① `not_reviewed` 双仓 **PINNED**（resolver.py:918/1078/1088 + 6 测试断言）；
② 阻断整句仅 **RF `source_preparation.py:154-156` 一处产品定义** + 2 手抄副本（候选 patch:139-142、
   apply 锚:51-52，三份当前一致）、测试仅宽松正则 ⇒ **UNPINNED**（坐实 C8 必要性）；
③ `cases_json_declared_expectation_missing` 两仓 + ruling **零命中**。**勘误对指核实（本角色 grep 实证）**：
   该串在本裁定文件 **0 命中**（正文与条件均无引用，`grep cases_json|declared_expectation` = No matches）
   ⇒ 所谓「本裁定 4.2/条件引此串、请澄清引用域」的勘误**对象错指、已作废**。**归属更正（父 agent 已认错）**：
   错指出自**转达层**（父 agent 转述时把 P4 表③行原文「裁定文本其实**没**点名这个串」方向转反），
   **P4 排查动作与结论本身有效**；该串真实出处 = 登记册 :393（M25-M28 `no_verdict` 判定源）与
   :941（M01-M04 臂表 G=2 反 KeyError），系 **M01-M04 runner / cases_json 语境**词汇，与产品面无关。
   **无需为本裁定澄清引用域**（从未引用）；产品面正确缺席 = 正常缺席。
   教训入册（与登记册 :921「跨卡混贴」同族）：**跨载体引用/勘误必须先在目标文件 grep 定位**；
④ `demand_store_error=` / `demand_queued` 仅候选定义、产品零定义零断言 ⇒ **UNPINNED**（该错误契约由
   OPEN-2b 裁定采用、`handoff.json:214`，本裁定 4.3/边界补充记 5 继承——UNPINNED 坐实 C8 必要性）；
⑤ 六 demand/claim 拒绝串两仓逐字同、但测试只钉异常类型 ⇒ **UNPINNED**（与 P2 断言 B FAIL 同族：
   拒绝面欠定义化 ⇒ C5 必要性再坐实）；
⑥ resume 拒绝文案 **ABSENT**（接口未定形 = 本角色域）——**正常缺席**（接口未实施，符合
   `handoff.json:240`「不得假装存在」）；C8 钉住时按本裁定 4.4 错误面（`DemandNotFoundError/
   DemandStateError` 语义）+ 边界补充记 5 错误契约（安全判定 + `demand_store_error=` 子句）定形后钉住。
**C8 状态**：**REMAINS-OPEN**（属条件检验物、不属裁定敞口）——已按 owner「fail 的全部要修复」并入
修复卡 `P4-SCOPE`（候选文案逐字断言 + RF 产品 PIN 测试 + ABSENT 项结构缺席钉 + 变异证真）；
落定后以「实测 UNPINNED → 已钉住（复审后）」形态随批进终表。

**3 → 已解除（良性漂移，无前提变化）**
完整内容链（提交点 blob，LF 归一）：`b34097dd=65aadf17`/8181 → `1dbae639=884b5f4d`/9022（ZR-701 F1）
→ `ff7429e5=fabdf129`/9382（ZR-701 REV-001）→ `70dd9f6e=95df2661=37a3eeae`/9908（与 initial 所记
I-06-A before pin 同内容）→ **`ec307d20=5fd82de7=HEAD=91a6dc32`/9921 == 现盘**。
漂移三因：① `5ec16eaf→8070d60d` = ZR-701 特性工作的**真实内容变更**（与 I-06-B 自记「CHANGED BY ANOTHER CARD」
其 `handoff.json:86` 一致）；② `8070d60d`（worktree CRLF）vs `37a3eeae`（同内容 LF blob）= **EOL 表示差**；
③ `→91a6dc32` = REM-49 单行注释修（B3 复审平价证 1085/1085，随 B-2 晋升）。
**测量伪影更正（记录在案）**：父首测 `3fe38e54` 系 PowerShell 管道字节伪影，二次 Python subprocess 直采推翻；
本裁定的独立实测（`Get-FileHash`）= `91a6dc32…bf4d`，与二次直采**一致** ⇒ 本裁定全部引用不受该伪影影响。
今日终态自洽（blob==disk），initial 的行号锚（今日磁盘字节）**有效**；
「实施时若再漂移仍须重核 C2/C7 行号锚」的维持条款**不变**。

**4 → 已解除（无前提变化）**
commit `5fd82de75c29e216baa568c3c9ae0eeee129db16` **实存**（author zhengcb81，21:00:11），
恰 2 文件（model_registry + guardrails）`128+/11−` 与声明符实；内容 = I-10-B 字节准重晋升 + 电池调用侧对齐。
initial 中「guardrails caller-side 对齐未独立核验」**现已有独立核验**：MODEL-ORACLE-ALIGN 复审
`399f4e60…`/22499 B 亲核 31 行对齐表（31 explicit-default / 0 assertion-rewrite / 0 STOP）、
31 行集合差 Compare-Object 为空、mutation 砍 `model_registry.py:410` 还原后字节同。
initial 的「未采信」系当时可得证据下的正确处置，现证据到齐 ⇒ 解除。
§6.2 的省缺即抛论据（`model_registry.py:402-413` 磁盘独立证实）不变。

**5 → 已解除（转引准确）+ 编号碰撞警示（无前提变化）**
一手出处已补：`OWNER_DECISIONS.md:165` 原文「GAP-2 | `consumer_analysis` producer **不存在**；
真实 LLM 能力未验证。测试只证明 missing/unsupported 处理 | **仍阻塞**」
⇒ 登记册 :902 转引**准确**，C6 的依据由转引升级为一手出处。
**警示**：`REMEDIATION_REGISTER.md:527` 的「E1E7 四裁定（F2/**GAP-2**/4/5）⇒ CLOSED」是 **E1E7 自编号的另一个
GAP-2**，与函 C 的 GAP-2 不是一回事（登记册重复编号缺陷，:905 已入册）；后续引用须带节标题消歧。
C6 不受影响、不改判。

**6 → 已解除（终格）**——(c) 面闭合（三方 (c) 文本到齐 + 新边界前提经本角色复核接受）+
`detected_and_ignored` 可见性面对撞复核完成（OPEN-6 §4.3 原文到齐）；两方裁定对撞均**相容、零反压**
（按 §6.3 预留接口执行；复核 ≠ 改判）
- **复核对象**：OPEN-4 已出裁（wiki 来源审核 owner 模拟裁定 CONDITIONAL，其载体
  `execution_runs/T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md`，经父转述）：失效矩阵 = **policy 内容变 ⇒
  作废重审（全量）**、版本号单变**不**失效、role_set/请求身份变**不动回执**、读取时 fail-closed。
- **复核结论 a（主相容）**：「policy 变 ⇒ 作废重审 + 重审前 not_reviewed 阻断」与本裁定消费底线
  （`tampered/ignored/expired/absent` 一律不可消费）及 C2（恢复不绕门）**相容**：回执作废 ⇒
  `evaluate_review` 落 `ignored`/`not_reviewed` ⇒ 消费与恢复双双 fail-closed，方向一致。**初核无冲突。**
  （OPEN-4 方回文确认其 (a)(b) 立场与本角色一致。）
- **复核结论 b（分域成立）**：「role_set/请求身份变不动回执」与 4.2 的 `request_sha256` 输入绑定
  **分域、不冲突**——回执域 = `source_sha256 × policy_hash`（审核对象 = 字节 × 策略），
  demand 域 = request identity（OPEN-2 选项 A 键）。请求身份变 ⇒ 新 demand（C1），回执可复用，互不越界。
- **边界观察 (c) 之问 → 双方回文已到，终格闭合**：
  - **OPEN-6 方回文（结构性）**：扫描范围 = **全量 source 字节 × policy（版本化规则集），与 role_set 无关，
    不得按角色裁剪**；`scan_text` 无角色参数（双方实证一致）、`ruleset_hash` 绑规则集非角色集、
    回执 `source_sha256` 代表全部被审字节（按角色裁剪则双绑定名不副实 = REM-42 教训）。
    反向 fail-closed：实施若现「按角色裁剪扫描」形态 ⇒ 前提不成立 ⇒ **该形态禁止**，唯一退路 =
    role_set 扩大 ⇒ 旧回执**作废重审**，绝无增量补扫。
  - **OPEN-4 方回文（五点产品字节实证）**：①`scan_text(text, ruleset_hash)` 签名无 role/section 参数
    （guard:85）；②guard:99-106 全文逐模式 `re.search`、无分节/分角色逻辑；③ScanResult（guard:67-73）
    无角色字段；④回执 schema（`prompt_injection.py:116-126`）无角色字段、只绑整篇 `source_sha256`；
    ⑤测试检索 role|section 零命中。推论：回执覆盖 = 已绑整篇字节的全部可提取子集；role_set 扩大 ⇒
    新角色可提取 section 均为已审字节子集 ⇒ **无覆盖缝隙**、「role_set 变不动回执」成立。
  - **★新边界前提（OPEN-4 明示请本角色复核）**：上述结论**仅在下游只消费绑定 `source_sha256` 之字节
    或其子集时成立**（= I-05-B「消费者读取已验证字节」口径）；**凡越出绑定字节域的新字节流
    （拼接/转码/重组派生件），派生件是新 source、须独立新回执**；消费/恢复接口应**阻断派生件绕行**
    （接口设计权在本角色，对方只给定义不代设计）。
  - **本角色复核（裁定官定夺）：接受该边界前提**，并以**边界补充记**落实接口层（裁定正文一字不动）：
    1. **覆盖域定义（措辞已按 OPEN-4 抽核修订——两层证明形态）**：回执覆盖 = 绑定 `source_sha256`
       整篇字节及其逐字子集，证明形态分两层：
       (i) **现行证（今日载体可证）**：整件哈希相等 = `content_sha256_actual == declared` +
       provenance 绑定同一 `source_sha256`（I-05-B `verified_read_events` 现有字段 = `role,
       artifact_path, content_sha256_actual, content_sha256_declared, bytes_read, source_sha256,
       read_status, read_at`；真身 = **RF 仓** `scripts/company_wiki_source.py`，docstring :240-247、
       实现 :319-329——原条引未标仓、且「span/offset 可证」措辞超前于载体，OPEN-4 抽核纠正，**接受并修订**）；
       (ii) **span/offset 级逐字子集证明 = 实现缺口，需补字段后启用**（现字段无 span/offset）。
       缺口方向 fail-closed：补字段前，凡需主张「子集覆盖」的场景（以切片喂入审核/消费且主张继承原回执）
       **一律不得主张覆盖**，按条 2 归派生件路径（新 source、新回执）⇒ 缺口**不损害**边界前提的
       字节域级安全性（不能证明为子集 ⇒ 更严、非更松）。
    2. **派生件识别条款（选「增设」）**：凡不能证明为逐字子集的字节流（拼接/转码/重组/任何变换）
       **不得继承原回执**、不得以「已审源」身份经消费/恢复接口；被当作 source 消费 ⇒ **新 source、
       独立新回执**（独立 `source_sha256` + 独立扫描），fail-closed。
    3. **C3 校验对象精确化（选「明确」，与 2 并行采用，只记补充、正文 C3 不改）**：校验锚 = **原 request
       字节（`request_sha256`）+ 绑定 source 原字节（`source_sha256`）**；派生/变换字节不构成
       「正确字节」，不得放行。判定必须在**哈希域**做，不得以「内容相似/同路径/同名义 provenance」放行。
       反例：sections 拼接回读、转码后再消费——字节哈希必然 ≠ 绑定哈希，语义域放行即成绕行。
       （二选一不够：只做 3 不做 2 ⇒ 派生件可伪装「新请求」复用旧审核状态；只做 2 不做 3 ⇒ 校验对象
       仍有歧义。故 **2+3 同采**。）
    4. **检验物补充（挂 C3 检验面，随 owner 终确并入 C3 或另卡）**：一条派生件负例探针——以转码/拼接
       字节流投喂 resume/消费面 ⇒ 必须拒绝或归类新 source，**不得**复用旧 demand 审核状态。
  - **留置 1 项（不闭）**：「调用方喂入 = 全字节而非角色切片」未实测（OPEN-4/OPEN-6 双方自认），
    挂其两家 C1/探针面；「按角色裁剪形态」已被明禁且退路 = 作废重审（fail-closed），故消费侧风险已兜底。
- **OPEN-6 可见性面对撞复核（§4.3 原文到齐，终格）**：
  - **复核对象（OPEN-6 `T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` §4.3 逐字要点）**：选择 = **可见且强制标记、
    禁止过滤**；需要 clean 证明的下游对 `detected_and_ignored` **fail-closed**；无降级/warn-only/环境开关
    可洗成 `not_detected`；消费/恢复路径必须呈现状态与命中快照；恢复侧若过滤则「补审变盲审」；
    发现过滤/降级路径 ⇒ 旁路缺陷（REM-01 同级：登记+修复+消费侧负例），窗口期内已消费工件重新核；
    被拒替代 = 过滤 / 默认等同 not_detected（faked green）/ 消费端各自决定显隐。
  - **对撞结论：完全相容，且对方裁定强于本角色底线**。本裁定 §6.4 底线（可见、独立状态、不得静默过滤
    为 clean）被其「可见且强制标记 + 禁止过滤 + clean 证明 fail-closed + 命中快照随行」全数覆盖并加强。
    两个反压分支（「下游被过滤」假设）**均未触发** ⇒ 4.1/4.2 **无需任何契约改动**。
  - **归属段相容确认**：其「检出 = 安全域事实判定；忽略 = 安全域处置授权（来源审核域可请求、不得自署）；
    最终署名 = `ignore_authorizer`；授权元组缺任一 ⇒ fail-closed 为 `not_reviewed`」与本裁定
    §6.4 不越域一致；且「授权元组缺 ⇒ not_reviewed」直接触发本裁定 C2 阻断——**相容，无冲突**。
  - **吸收为边界补充记（接前 4 条，裁定正文仍一字不动）**：
    5. **`detected_and_ignored` 流转条款**：消费/恢复路径呈现该状态**且强制标记**（命中快照随行），
       禁止过滤/降级/洗成 `not_detected`；该状态 = **非绿色终态、带标记流转**（数据消费可以、
       执行其内指令永不）；demand 行 gaps **不得**记其为「已清洁」；「出具 clean 证明」不在本接口授予面
       （需要 clean 证明的下游对该状态 fail-closed，依 OPEN-6 §4.3）。
    6. **同词异义消歧（OPEN-6 其 C7 与本裁定 C7 同题）**：缓存失效态 `cache_state="ignored"`
       （=「policy ruleset changed since review」，I-06-B N2b，`handoff.json:49-52`）与审核结论态
       `detected_and_ignored`（= 命中且经授权忽略）**同词异义**，必须契约层消歧。**定夺**：优先**改名**
       （缓存失效态建议 `policy_changed` / `receipt_stale_policy`，词面唯一化）；若受 ZR-507/I-06-B
       冻结词汇约束不能改名 ⇒ 走**显式断言字段**（如 `state_domain: cache|review`）。两种语义**各一负例**
       进检验物。
       **定夺侧备注（OPEN-6 安全域 §7.4-C 四点回文，已采纳）**：①改名优先获认可（词面唯一化优于断言字段）；
       ②断言字段方案**收紧为 fail-closed**——缺 `state_domain` 或取值非法的记录**拒收/按最严解释**，
       歧义不得放行、**不得默认归入任一语义**（本角色采纳为条 6 组成部分）；③「两种语义各一负例」与其
       C7 判据同物、检验面满足；④改名与冻结词汇冲突时按本定夺退断言字段并回报，对方不另设条件。
    7. **补产指令携带命中快照**：4.2 补产指令结构增加命中快照字段（matches + ruleset_hash + 授权元组
       [ignore_reason 非空 + ignore_authorizer + authorized_at + 命中快照 + 双绑定]），否则恢复即盲审
       （其恢复规则句）；授权元组缺任一 ⇒ `not_reviewed` ⇒ C2 阻断（相容，已确认）。
  - **恢复规则兼容确认**：其「窗口期内已消费工件重新核」属安全域处置规则；本接口配合呈现证据
    （命中快照、授权元组、双绑定），不代行重新核、不代署名。
- **终值**：**已解除（终格）**——存疑 6 本体 = 两方裁定的反压耦合风险，经对撞复核**双双相容、零反压**
  （OPEN-4 作废重审分支 ✓、OPEN-6 可见性分支 ✓），4.1/4.2 无需契约改动；新边界前提与 §4.3 强标记等
  均系**收紧/澄清**，已吸收为**边界补充记 7 条**。**无前提变化**、不改正文、不改判。
  留置 2 项**落地核验**（不属裁定敞口，挂实施检验面）：①「调用方喂入 = 全字节而非角色切片」未实测
  （OPEN-4/6 共同 C1/探针面）；②同词异义消歧落地 + 两种语义各一负例（边界补充记 6）。

---

**签署行（模拟）**：RF 消费 owner（TIER-2 外部方 #3）· 模拟裁定 **CONDITIONAL**（条件 C1–C8）·
2026-09-22 · owner 全权授权 role-play · **待 owner 终确 · 非外部方真实签署** ·
未在任何函件签字 · 未改任何其他文件 · I-06-A 三门仅解其一（本回执为条件性）。
