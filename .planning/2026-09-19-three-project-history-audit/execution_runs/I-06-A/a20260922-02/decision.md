# decision.md — I-06-A / a20260922-02（persistent demand registration，accepted_scoped → review_pending）

实现者：本 attempt（wiki 持久需求 owner / RF 消费实施者角色）。
**本文件不是决策签署、不是自签验收。** 全部决策依据 = 已 RATIFIED 的裁定契约（owner 2026-09-22「全部接受」，
`OWNER_DECISIONS.md §十九`）；实施落在 `iso/` 隔离副本，**生产仓改动 = 0**（独立复审 + owner 提交后才可落地）。

历史载体纪律：`I-06-A/a20260919-01`（09-19 blocked carrier）与两个生产仓全程 **READ-ONLY**，零写入、零 git 操作。

---

## 0. 范围（严格按卡边界）

- **做**：STORE 侧持久需求生命周期 = 阻断前持久登记（register-then-block）+ 幂等键含请求身份 + 原请求绑定列
  + claim/complete/fail/显式回收 的存储 API + c7 错误契约 + gaps 三值语义 + N-1 加法迁移 + TTL 30d policy 上限
  + 回执失效独立性 + 同词异义消歧断言字段。
- **不做（显式留 I-06-B / 后续）**：`resume --demand-id --request-file` 恢复**执行**接口与其可失败测试面
  （原卡边界：resume/complete 消费执行面属 I-06-B）；真实审核执行（全程零 review 行）；CLI adapter 文件
  （**任何裁定都未冻结具体 CLI 文件名** —— 卡文「未冻结具体文件禁止猜建」，只落 store API 面）；RF
  `source_preparation.py` 的调用侧接线（本次实施面 = 父指令步骤 1 冻结的 CW 四文件；接线列为下一载体）。

## 1. 契约来源与逐条实现对照（contract-conformance map）

| ratified 条款 | 实现落点（iso/cw/src/company_wiki/source_catalog/…） | 验证 |
|---|---|---|
| OPEN-1 选项 A / OPEN-5 §4.3：单一持久 owner = CW `store.py` + `catalog.sqlite3` + 既有 `_apply_additive_migrations`；不另立介质 | `store.py:116-229`（`PROCESSING_DEMAND_COLUMNS`/`processing_demands_schema`/`processing_demand_events_schema`/`ensure_processing_demand_columns`）、`store.py:1286-1300`（迁移块：缺表建表、有表补列）、`_DDL` 尾部拼接 `processing_demands_schema + processing_demand_events_schema` | W06A2-P3 |
| OPEN-5 §4.3 兼容影响：demand 行**豁免** prune/archival（+显式保留规则入迁移注释） | `store.py:116-130` 注释（生命周期豁免 + 无 FK 到 documents/sources + terminal 行仅由显式生命周期调用迁移、永不删除）；schema 无外键 | W06A2-N9 |
| FIX-W06-GAPS P1 缺陷类不得复现（N-1 库静默不补列） | `store.py:203-229 ensure_processing_demand_columns`（幂等补列）+ 迁移块 else 分支 | W06A2-P3（变体 A/B：缺表 + 缺 `request_sha256`/`lease_until` 的窄表） |
| OPEN-2 选项 A / OPEN-5 §4.5.1：`demand_key = sha256(canonical_json({source_sha256, review_policy, role_set, request_identity}))`，request_identity **覆盖** as_of_date/target/payload digest（三字段全必填，F6 收紧） | `processing_demand.py:437-452 compute_demand_key`、`:376-407 _validated_request_identity`（缺任一字段=拒绝，垃圾输入不建任务） | W06A2-N1/N11 + `evidence/request-to-demand-binding.json`（c8/c9/c10 反例翻绿） |
| OPEN-5 §4.5.2：保留 `request_sha256` **且** `request_json`；request_sha256 是校验锚 | `processing_demand.py:460-467 request_sha256_of`、`register :617-757`（两列都存、行内值=实际哈希） | W06A2-P1/N1 |
| OPEN-5 §4.5.3：状态闭集 `pending/running/completed/failed/terminal_failed` 沿用 ZR-507；terminal_failed 必留 reason；failed 可显式重试 | 闭集 = 模块既有 `_STATUSES`（`processing_demand.py:44-46`，schema CHECK 同闭集）；`fail :896-947`（terminal 无 reason ⇒ `DemandStateError`；backoff 语义沿用） | W06A2-P4 |
| OPEN-5 §4.5.4：CLI 最小面 list/show/claim/resume/complete\|fail | store API：`get/show/list`（`:757-788`）、`claim :790-868`（显式单次）、`complete :870-895`、`fail :896-947`；**resume/complete 消费执行面 = I-06-B**；CLI 文件未冻结 ⇒ 不建 | W06A2-P4/N4（API 面） |
| OPEN-5 §4.5.5 / OPEN-2b c7 错误契约：安全判定 + `demand_store_error=` 子句；成功报 `demand_queued`（demand_id/gaps/next_action）；失败无 `demand_queued`、无内存兜底、行数不变 | `processing_demand.py:470-480`（两个 clause 函数，逐字 PIN 见 W06A2-C8）、`register_before_block :495-529`（先登记后阻断、verdict 原样透传） | W06A2-C8、W06A2-N2 |
| OPEN-5 §4.5.6 / 函 C：gaps 三值 `missing/unsupported/not_applicable` 可区分、不得混同 | `processing_demand.py:293 GAP_KINDS`、`:410-435 _validated_gaps`（闭集校验，非法值=编码化拒绝，无静默归类、无 clean 态） | W06A2-N7 |
| OPEN-3 / OPEN-5 §4.4=条件 C5：`claim(owner, lease_seconds)` 显式单次授权；lease 过期拒绝；过期回收只可显式；无自动 resume、无后台 scheduler | `claim :790-868`（CAS 一赢家）、`_refusal :826-844`/`_require_lease_row :846-868`（全部编码化拒绝，P2-B/P3-B 类不复现）、`reclaim_expired :948-967`（显式回收入口，防 P3 搁浅） | W06A2-P4/N4/N5、W06A2-N3 |
| OPEN-2b：role_set 权威来源维持 `RF_W06_ROLE_SET`（调用侧），规范化=排序去重逗号串 | `processing_demand.py:364-373 normalize_role_set`（键与行内都用规范化值） | W06A2-N1（role_set 在键内） |
| P6-A 类不复现（并发写冲突=定义拒绝、无静默覆盖/丢写）+ P6-B 类不复现（锁超时等 sqlite 错误包装定义错误） | `register :740-755 _resolve_existing`（同键异载荷 ⇒ `DemandIdempotencyViolation`，绝不静默合并）；所有 sqlite3.Error ⇒ `DemandStoreUnavailable :304-311` | W06A2-N5、W06A2-N2 |
| OPEN-4 §4.3 恢复规则：回执失效不自动关闭 demand；demand 关闭不改写回执 | 实现层**零回执钩子**（processing_demand 全模块不 import 回执面；两域完全独立） | W06A2-N6 |
| OPEN-6（无静默态 + 编码化错误契约） | 编码化错误族 `DemandQueueError → DemandNotFoundError/DemandStateError/DemandStoreUnavailable/DemandRegistrationError/DemandIdempotencyViolation`；gaps 三值闭集 | W06A2-N4/N7 |
| OPEN-5 边界补充记 6（同词异义消歧，留置落地核验②）：`cache_state="ignored"` vs `detected_and_ignored`；断言字段 fail-closed | `prompt_injection_guard.py:127-176`（`STATE_DOMAIN_*`、`state_domain_of`、`require_state_domain`）、`ReviewEvaluation.state_domain :194-201`（非法值/错域 ⇒ 拒收） | W06A2-N10 |
| owner §十九 TTL 定值 = 选项 A：30 天 policy 上限、调用方只可收紧（OPEN-6 C6 机制）；**非有限输入不得放宽**（F1） | `prompt_injection_guard.py:72-117`（`RECEIPT_TTL_POLICY_CAP_SECONDS = 86400*30`、`effective_receipt_ttl :79-97` 含 `isfinite` 门 :92、`effective_review_instant :99-117` 含 :108；`evaluate_review` 双钳制） | W06A2-N8/N8b |
| I-06-A 卡 W06A-P1/P2/N1/N2/N3 固定样本 | 逐条对应 W06A2-P1/P2/N1/N2/N3 | 见下表 + `evidence/` |

## 2. RED / GREEN / MUTATION 逐例表（instrument = `scripts/w06a2_cases.py`，冻结预期 = `oracle.md`）

| 用例 | RED（before = 生产原件） | GREEN（iso = 候选） | MUTATION（三臂 iso-mutant\*，各翻一个 guard） |
|---|---|---|---|
| W06A2-P1 register-before-block | **FAIL**（API 缺席：`no attribute 'CatalogDemandStore'` —— 生产件无持久登记面） | **PASS**（登记先于阻断、verdict 透传、二进程可读、零伪造 review） | PASS |
| W06A2-P2 跨进程幂等重提 | **FAIL**（同上） | **PASS**（同一 demand_id、恰好 1 待办、非 pd-0） | PASS |
| W06A2-P3 N-1 升级路径 | **FAIL**（同上） | **PASS**（变体 A 缺表补表 + 变体 B 窄表补 `request_sha256`/`lease_until`，旧行保留，register/claim 正常） | PASS |
| W06A2-P4 claim/lease 生命周期 | **FAIL**（同上） | **PASS**（一赢家、lease 内 complete/fail、terminal 必留 reason） | **FAIL**（连带，见下注） |
| W06A2-N1 请求身份入键（c8/c9/c10 反例） | **FAIL**（同上；且生产内存队列键无请求身份） | **PASS**（仅 as_of_date 不同 ⇒ 两行两 id、行内 request_sha256 各自正确、旧需求不被关闭） | **FAIL**（变异目标：键丢 request_identity ⇒ 请求再次被静默并入） |
| W06A2-N2 写失败 | **FAIL**（同上） | **PASS**（无 demand_queued、安全判定 + `demand_store_error=` 子句、无内存兜底、行数不变） | PASS |
| W06A2-N3 paused / 无自动推进 | **FAIL**（同上） | **PASS**（线程清单前后不变、登记后仍 pending、零自动 claim） | PASS |
| W06A2-N4 定义拒绝（无裸 None/裸抛） | **FAIL**（同上） | **PASS**（NotFound/StateError/注册拒绝全编码化；lease 过期拒绝并指向显式回收） | PASS |
| W06A2-N5 并发写冲突=定义拒绝 | **FAIL**（同上） | **PASS**（同键异载荷 ⇒ `DemandIdempotencyViolation`、旧行不被覆盖；并发 claim 一赢家+输家编码化拒绝；并发同载荷登记幂等单行） | **FAIL**（连带，见下注） |
| W06A2-N6 回执失效独立性 | **FAIL**（同上） | **PASS**（回执失效 ⇒ demand 行字节不变；关需求 ⇒ 回执字节不变） | PASS |
| W06A2-N7 gaps 三值语义 | **FAIL**（`no attribute 'GAP_KINDS'`） | **PASS**（三值可区分、round-trip 保留；`ok/clean/reviewed_ok/MISSING/None/空` 全拒绝） | PASS |
| W06A2-N8 TTL 30d 上限、只可收紧 | **FAIL**（`no attribute 'RECEIPT_TTL_POLICY_CAP_SECONDS'`。**如实归位（复审 F5）**：「before 代码在 ttl=∞ + 过去 now 下复活过期回执」= 代码真（before guard 无双钳制）+ 兄弟卡 TTL-30D-POLICY 的 RED 实测证；**本卡 RED 未执行该复活行为**（N8 在首个 AttributeError 处即中止）——此行为反例不归本卡 RED 文件） | **PASS**（cap=86400×30；ttl=∞ 截断至 cap ⇒ 仍 expired；收紧至 1h 生效） | PASS |
| W06A2-N9 prune/archival 豁免 | **FAIL**（同上） | **PASS**（全量归档删除后非 terminal 行仍在且可 claim） | PASS |
| W06A2-C8 错误契约逐字 PIN | **FAIL**（`no attribute 'ProcessingDemandRecord'`） | **PASS**（`demand_queued demand_id=… gaps=… next_action=…`、`demand_store_error=<Type>: <msg>` 逐字断言） | PASS |
| W06A2-N10 同词异义消歧 | **FAIL**（`no attribute 'state_domain_of'`） | **PASS**（ignored=cache 域 / detected_and_ignored=review 域；错域/非法 state_domain 拒收） | PASS |
| W06A2-N8b 非有限 ttl/now 门禁（二轮新增，F1） | **FAIL**（`no attribute 'CatalogDemandStore'`；修复前 iso 的**行为红**另证于 `evidence/red_prefix_iso.json`：NaN ttl 令已过期回执 `cache_state='hit'` **复活** = F1 fail-open 原文实录） | **PASS**（`ttl=NaN/+inf`、`now=NaN 数值` ⇒ 编码化 `PromptInjectionGuardError`（含 "finite"）；有限超 cap 维持 CLIP；垃圾字符串 now 维持 tampered） | **FAIL**（nan 臂：去 `isfinite` 门 ⇒ NaN 复活再现） |
| W06A2-N11 请求身份三件套（二轮新增，F6 收紧） | **FAIL**（同上 API 缺席；修复前 iso 的行为红另证于 `red_prefix_iso.json`：两字段身份被**接受**登记 = any-of 缺口原文实录） | **PASS**（6 种 partial identity（2 字段×3、1 字段、空串、None）全部 `DemandRegistrationError`（含 "cover"）+ 零行产出；完整三字段正对照通过） | **FAIL**（identity 臂：校验退化回 any-of ⇒ partial 被接受） |

**汇总（二轮终值）**：RED（before）**0/17**；修复前 iso 增量红 **15/17**（N8b/N11 行为红，`evidence/red_prefix_iso.json`）；
GREEN（iso）**17/17**。MUTATION 三臂：key 臂 14/17（红 = N1 目标 + P4/N5 同 guard 连带）、
nan 臂 16/17（红 = N8b 目标）、identity 臂 16/17（红 = N11 目标）——**每臂恰好红其目标族，其余全绿**。
**变异注**：①key 臂翻 `compute_demand_key` 的 OPEN-2 A 键子句（移除 `request_identity`，`iso-mutant/MUTATION.json`）
⇒ W06A2-N1 红 ✓（as_of_date 分歧请求重新合并 = c8/c9 家族复现）；P4/N5 **连带红**——两用例夹具各登记 2 个身份分歧请求，
同一 guard 被翻后两请求撞键 ⇒ `DemandIdempotencyViolation`（断言链在登记步即失败），同 guard 非二次翻转。
②nan 臂翻 `effective_receipt_ttl` 的 `isfinite` 门（`iso-mutant-nan/MUTATION.json`）⇒ W06A2-N8b 红 ✓（红文即 F1 复活原文）。
③identity 臂把 `_validated_request_identity` 退化回 any-of（`iso-mutant-identity/MUTATION.json`）⇒ W06A2-N11 红 ✓。
三臂均证明用例**非空洞**（可失败、对实现 guard 敏感）。

证据：`evidence/red_before.json`、`evidence/red_prefix_iso.json`、`evidence/green_iso.json`、
`evidence/mutation_iso_mutant.json`、`evidence/mutation_iso_mutant_nan.json`、`evidence/mutation_iso_mutant_identity.json`
（各含逐例 error/traceback/measurement）；一轮原始证据字节保全于 `evidence/round1/`。

## 3. 卡要求的三件专属证据

- `evidence/demand.cross-process.json` —— 7 个**真实独立进程**串行场景：登记→他进程查询→**完全相同**需求重提→
  查询→仅 as_of_date 变→entity 变→查询；断言全绿（同 id 幂等、asof 分歧=第二条、entity 分歧=第三条、
  durable id 非 pd-0、三行可见）。**二轮起自证进程身份（复审 F3 关闭）**：每个子进程在输出信封里自报
  `pid` + 字面 `argv`，`children[]` 逐条记录且断言 `seven_distinct_child_pids`（7 个互异 pid）。
- `evidence/request-to-demand-binding.json` —— c1/c3/c10/c8-c9 四请求的 `request_sha256 ↔ demand_id` 绑定，
  每行 `row_matches_request=true`，`no_silent_absorption=true`（09-19 反例「行内 request_sha256 停留首请求」已消）。
- `evidence/paused-before-after.json` —— 全部登记/查询前后的线程清单不变、全部需求 pending + lease_owner=null、
  `worker_control_touched=false`（无自动 resume/claim/scheduler）。

另：`evidence/prod-unchanged.json`（生产仓零写入 + before/ 副本与真实仓逐文件哈希一致）。

## 4. 设计决策（含裁定文本歧义的字面处置）

1. **介质**：严格 OPEN-1 选项 A 形状——表建在 `catalog.sqlite3`、经 `_apply_additive_migrations`（含 N-1 补列），
   **不沿用** 09-19 候选的 option-B 独立库形状（OPEN-5 §4.3 明文拒绝）。
2. **CLI adapter 不建文件**：OPEN-5 §4.5.4 只定义了 CLI 最小面的**语义**，从未冻结具体文件名；卡文
   「D-W06 明确列出的 store/migration/CLI adapter 文件；未冻结具体文件禁止猜建」⇒ 本 attempt 只保证
   store API 可承载该 CLI（list/show/claim/complete/fail 已有对应方法），文件落点待冻结后由后续载体补。
   **resume/complete 消费执行面（含 `resume --demand-id --request-file` 绑定校验）= I-06-B 的可失败测试面**，
   本 attempt 显式不实现（原卡边界）。
3. **register_before_block 的语义**（先登记后阻断）：返回结构化 `DemandBlock{security_verdict, clause, demand}`，
   verdict **原样透传**（不修改安全判定）；成功 clause=`demand_queued …`，失败 clause=`demand_store_error= …`
   且**无** `demand_queued`（c7 逐字）。这是 STORE 侧契约面；RF 调用侧接线属下一载体。
4. **同键异载荷 = 拒绝**：OPEN-2 A 键含请求身份后，「同键异 request_sha256」只剩调用方身份字段与 request_json
   不一致（如 payload_digest 断言与字节不符）——按 P6-A「冲突即拒、无静默覆盖」落 `DemandIdempotencyViolation`，
   不做静默合并（c8/c9 静默并入同族的反向堵死）。
5. **claim 不接管 lease 过期的 running 行**：OPEN-3「lease 过期回收只能显式触发」⇒ 提供显式
   `reclaim_expired(now)`（P3 搁浅类的解法），claim 对 running 行给编码化拒绝并指向显式回收；无 scheduler/线程。
6. **TTL「now 只可收紧」的字面实现**：裁定负例要求「`ttl=∞` / `now=过去` 复活已过期回执 ⇒ **被拒或被策略上限截断**」。
   本实现取「截断」分支：`effective_ttl = min(caller, 30d cap)`；`effective_now = max(caller now, policy clock)`
   （policy clock = 墙钟，可注入）。⇒ 超 cap 的 ttl 截断至 cap、过去的 now 截断至 policy clock，二者都不能放宽新鲜度窗口。
7. **同词异义消歧走断言字段**（边界补充记 6）：其首选为改名，但 `CACHE_STATES={hit,ignored,expired,tampered,absent}`
   被 ZR-507/I-06-B 冻结测试**与裁定自身词汇**（OPEN-5 §6.3 引「tampered/ignored/expired/absent」）双重钉住 ⇒
   改名=破坏冻结词汇，按裁定给定的退路落**显式断言字段 `state_domain`**（fail-closed：缺省不可能、非法值/错域拒收）。
8. **数值纪律**：不新写任何未裁数值——TTL=owner 已裁 30d 上限；`max_attempts=3 / backoff_base=60` 沿用既有
   ZR-507 `DemandQueue` 产品语义（非新规范）；`lease_seconds` 由调用方给定（OPEN-5 §6.5 明文不入规范）。
9. **append-only 事件表**：`processing_demand_events`（register/claim/complete/fail/reclaim_expired）无 FK
   （producer_events 先例），生命周期留痕可审计；terminal 行永不删除（迁移注释已载保留规则）。
10. **F1 修复 = 修法 (a)：非有限输入=非法输入=编码化拒绝**（二轮复审阻断项，OPEN-6 C6 fail-open 堵死）：
    `ttl=NaN/+inf/-inf` 与数值型非有限 `now` ⇒ `PromptInjectionGuardError`（"must be a finite number/instant"）。
    选择依据：(i) 与本卡既有非法参数处理同族（负 ttl/空 owner/非法 gaps ⇒ 编码化拒绝，「垃圾输入不可建任务」的
    fail-closed 线）；NaN 是**无效数据**而非「超 cap 请求」，把它映射到 cap（窗口最大值）是 fail-open 味道的reinterpret；
    (ii) 与兄弟卡 TTL-30D-POLICY 的 NaN 处置**同形**（"must be a finite number"），使两卡残余分歧只剩
    「有限超 cap 值 CLIP-vs-REJECT」这一个**归一问题——仍留父裁**；(iii) 有限超 cap 值的 CLIP 机制**一字未动**
    （`min(caller, cap)`，W06A2-N8/N8b-③ 钉住），本修复**不预判** CLIP-vs-REJECT（复审 4.3 明示两种收口均不越界）。
11. **F6 收紧 = 裁定逐字「request identity **覆盖** as_of_date / target / payload digest」= 三字段全覆盖、全必填**
    （缺一/None/空串 ⇒ 定义拒）：any-of 读法会让省略字段的分歧请求共键——先撞 `DemandIdempotencyViolation`
    （同键异载荷定义拒），而裁定语义要求**两行**（W06A2-N1 族）；partial identity 在省略字段处正是 c8/c9
    静默合并缺陷的残余入口。收紧方向单调 fail-closed（只多拒不少拒），W06A2-N11 + identity 变异臂证可失败。

## 5. 恢复规则（撤回/失败）

- 生产仓零写入：撤回 = 删除本 attempt 的 `iso/` 与 `iso-mutant/` 即可，产品仓无需任何动作。
- 迁移失败：additive-only（建表/补列），失败即 `DemandStoreUnavailable`（编码化、fail-closed、无内存兜底），
  不触碰任何生产 pending；隔离数据库只存在于各用例 `%TEMP%` 目录。
- 详细见 `recovery/README.md`。

## 6. 未验证 / 存疑项（诚实清单）

1. **RF 调用侧接线未做**（本次冻结面=CW 四文件）：真实 `source_preparation.py` CLI 的登记前移与
   c8/c9/c10 **CLI 级**复探，待 RF 侧载体补（W06A2-N1 已在 store 级证明键语义）。
2. **resume/complete 消费执行面 = I-06-B**（原卡边界，本 attempt 不实现、不声称）。
3. **CLI adapter 文件未冻结** ⇒ 未建、未测（决策 2）。
4. **P4-SCOPE 文案钉住**：本 attempt 钉住了 c7 两个子句的**store 侧**逐字契约（W06A2-C8）；
   RF 阻断整句的跨仓逐字 PIN 属 `P4-SCOPE` 修复卡，不在此重复。
5. **并发面已测**（同进程双线程双连接 claim/登记）；跨进程并发 claim 未单列用例（sqlite IMMEDIATE 事务 +
   CAS rowcount 语义同源，跨进程 idempotency 已测）。
6. **P5-b 身份链**（reviewer 可冒用）= BLOCKED-on-external（函 B 信任根），非本卡面。
7. 「调用方喂入 = 全字节而非角色切片」运行时探针（OPEN-4/6 留置①）不属本卡面。
8. **独立复审未做**：本 attempt = implementer 交付 review_pending；implementer_signed=false。
9. **跨进程并发 claim** 未单列用例（review 复审「re-review path」列的 carried open 之一）；
   同进程并发已测（W06A2-N5），跨进程幂等已测（demand.cross-process）。

## 7. 二轮复审处置记录（reviewer_report.md findings F1–F10 逐条，2026-09-22 晚）

| # | finding（复审原文定位） | 处置 | 落点 |
|---|---|---|---|
| **F1（阻断）** | NaN ttl 放宽旁路（C6 fail-open）：`NaN<0` 过门、`min(NaN,cap)=NaN`、`age>NaN` 恒 False ⇒ 回执永生 | **已修复**（修法 (a)：非有限 ⇒ `PromptInjectionGuardError` 定义拒；有限超 cap 的 CLIP 机制不变，归一留父裁——决策 10） | `prompt_injection_guard.py:79-97/:92`、`:99-117/:108`；oracle §2-再补 W06A2-N8b；红=`red_prefix_iso.json`（复活原文实录）→ 绿=`green_iso.json`17/17 → 变异 nan 臂红 |
| **F2（记录）** | CLIP-vs-REJECT 跨卡分歧（本卡 CLIP vs TTL-30D-POLICY REJECT）——不代裁 | **照录 + 不预判**：本卡有限超 cap 维持 CLIP；NaN 处置与对方同形（"must be a finite number"）以缩小分歧面；归一机制选择仍留父裁（决策 10-ii/iii） | 本节 + 决策 10 |
| **F3（低）** | 跨进程证据缺 pid/argv | **已修复（超出「记 decision 即可」的最低要求）**：子进程输出信封自报 `pid`+字面 `argv`，`children[]` 入 `demand.cross-process.json`，断言 7 个互异 pid | `scripts/w06a2_cases.py`（child 信封）、`scripts/w06a2_evidence.py`（children + 断言） |
| **F4（低）** | handoff 哈希账不全（9 件） | **已修复**：`handoff.json.output_hashes` 扩至全账（3 iso + 4 scripts + oracle + changes.diff + commands/decision/recovery/binding + 全部 evidence（含 round1/）+ 3×MUTATION.json）；未变文件与复审 §1.1 复算值逐一对得上（见 handoff 注） | `handoff.json.output_hashes` |
| **F5（低）** | decision N8 RED 格含未执行的行为断言 | **已修复**：RED 格改为复审口径如实归位——「行为复活=代码真+兄弟卡实测证，本卡 RED 未执行 N8 复活」 | §2 N8 行 |
| **F6（低）** | 身份校验 any-of vs 裁定「覆盖三」 | **已修复（采纳推荐收紧）**：三字段全必填（缺一/None/空串=定义拒）+ 论证入决策 11 + 新增 W06A2-N11（红绿变异三证俱全） | `processing_demand.py:376-407`；oracle §2-再补；identity 变异臂 |
| **F7（低）** | iso-mutant 整文件换行重写（CRLF） | **已修复 + 照录**：mutant 生成器改 `read_bytes/write_bytes` **字节精确**替换（无换行翻译）；三臂 delta=逐字节所声明块。一轮 mutant 的换行伪影算术已由复审核证、不影响其效力；round1 证据字节保全 | `scripts/w06a2_make_mutant.py`（write_mode 注记入各 MUTATION.json） |
| **F8（信息）** | 复审简报 prompt_injection pin 前缀笔误（`7b26…` vs 实测 `7b22f239…39618`） | **照录**：真身三方（real/before/iso）+ binding/handoff 一致为 `7b22f239…39618`（UNCHANGED 断言成立）；系简报转写笔误、无完整性影响（复审自判 INFO） | 本节 + handoff.input_hashes |
| **F9（归属确认，父答）** | 历史 a20260919-01 新增 `rulings_transcribed_2026-09-22.md` 疑似越界 | **已消解（父 agent 确认）**：该文件 = **父转录批**（owner 终确「全部接受」后的授权记账，登记册 §四十三/§十九 入档），非本卡所写、非越界；本卡命令账零指向该树 | 本节 |
| **F10（方法，父答）** | 窗内两仓活动（CW commit `ac4ebd0` 22:19 / RF batch-4 22:24 等） | **已消解（父 agent 确认）**：= 父批次提交 + FIX 测试写，均在本卡冻结面之外；本卡 9+ 条命令全部只指向本 attempt 目录与 `%TEMP%` 隔离库 | 本节 |
