# decision.md — I-06-B / a20260922-02

实现者：本 attempt（九步执行法，第 1–8 步完成，第 9 步 = 接续待独立 review）。
Scope = **写可失败测试套件**（demand/receipt 系统，按已 ratify 三裁定）；**测试先行、零产品写入**。
Gate：letter A 前置「OPEN-4 出裁之前 I-06-B 不可写可失败用例」已由 owner 终确「全部接受」
（2026-09-22, OWNER_DECISIONS §十九）解除。

## 1. 结果计数

| 运行 | GREEN | RED | 总数 | 证据 |
|---|---|---|---|---|
| RED baseline（original iso = I-06-A 候选 7bc5feb0 + CW/RF 产品字节） | **8** | **10** | 18 | `evidence/red/` |
| GREEN vs fixed **snap1**（修复卡 iso 初拷 0b6e723e，P7 之前；保留） | 15 | 3 | 18 | `evidence/green_snap1_0b6e723e/` |
| GREEN vs fixed **snap2**（APPEND-1 后刷新 cd071322/88154de4；**最终 GREEN 半场**） | **16** | **2** | 18 | `evidence/green/` |

- **RED→GREEN 翻转（= 本套件抓到的修复卡缺陷，8 项）**：A, C, D, E, F1, F2, I, J。
- **双红（blocked，2 项）**：H2（OPEN-5 C6 实施面）、L3（修复卡 P4 Face 2 产品 pin 测试未落）。
- **双绿守卫（8 项）**：B, G, H1, K, L1, L2, M1, M2（可失败守卫：变异/回归即红；本次两臂皆绿）。

## 2. 用例表（每例 → ratify 裁定条款 → 两臂判定）

| # | 用例 | ratify 条款（逐例映射） | RED original | GREEN snap2 | 抓到的修复卡缺陷 / blocked 归属 |
|---|---|---|---|---|---|
| A | 幂等键含请求身份 ⇒ 两请求两行两键、request_sha256 各归各（c8/c9/c10 反例翻正） | **OPEN-2 选项 A**（owner 2026-09-20；OPEN-5 C1 与 §4.5 条 1；OPEN-4 §4.3「不得拿回执绑定当 demand 键」红线） | **RED**（单行静默吸收：同 id 同键、row request_sha256 停留首请求） | **GREEN**（修复卡 APPEND-A **P7** 键修订后翻绿） | 修复卡 **P7-SCOPE**（原范围明示 OUT-OF-SCOPE，parent 增量后 supersession） |
| B | not_reviewed ⇒ 先登记（行 + gaps/resolves_by）再阻断；阻断句安全判定开头 + demand_queued 可恢复；store 失败 ⇒ demand_store_error= 且无 demand_queued | I-06-A C1/C7_r2、**OPEN-2b c7 错误契约**、OPEN-5 §4.3 恢复规则 | GREEN | GREEN | 守卫（修复卡 C7 契约族同向） |
| C | N-1 库 `_initialize` 恰补 6 列、2nd run 幂等、旧行保留、补后 register+claim 可用 | **FIX oracle P1-c/P1-d**、probe01（P1-b2 new_columns_added=[]）、**OPEN-5 C4** | **RED**（CREATE IF NOT EXISTS 空转，0 列补上） | **GREEN** | 修复卡 **P1**（additive migrator） |
| D | 双 claim 顺序 + 双进程竞态恰一赢家；输家 = store 自有异常 + M-D1 逐字文案，绝不裸 None/TypeError | **FIX oracle P2-B**、probe02 assert-B FAIL、**OPEN-6 §7.4 C5 适用说明①**（编码化 fail-closed） | **RED**（裸 None；无 demand_id 参数 TypeError；竞态输家裸 None） | **GREEN** | 修复卡 **P2-B**（DemandStateError + M-D1 文案） |
| E | running+过期行（lease_until=0 强制）⇒ 显式 `expire(*,now)` 回收（返回数、lease 清空）⇒ 可再 claim 无搁浅；过期未回收时 = M-D1 定义拒绝 | **FIX oracle P3-A/P3-B**、probe03（永久搁浅）、**OPEN-3 显式 expire 等价物**、**OPEN-5 C5** | **RED**（无 expire；by-id TypeError；generic 裸 None 搁浅） | **GREEN** | 修复卡 **P3-A/P3-B**（expire 入口 + "lease expired"） |
| F1 | 迁移器旁路后 N-1 库上 claim/list_active/register 只出 store 自有类型 + 契约文案，绝不裸 `sqlite3.OperationalError` | **FIX oracle P1-e**、probe01 claim 裸抛、**OPEN-5 C5** 错误契约 / OPEN-6 C5 适用说明① | **RED**（claim 裸 OperationalError；list_active 裸 IndexError） | **GREEN** | 修复卡 **P1-e**（全路径类型化包装） |
| F2 | connA 持写锁 + connB timeout=0 写回执 ⇒ `PromptInjectionReviewError` 前缀 `store busy/lock timeout:`，绝不裸 `database is locked` | **FIX oracle P6-B**、probe06 Phase-A2、**OPEN-6 §7.4 F** | **RED**（裸抛 OperationalError） | **GREEN** | 修复卡 **P6-B**（writer/reader 包装） |
| G | 回执失效（tampered）不关 demand 行（C5_C6 形态 2 行 active）；demand 终态化不改回执字节（前后 sha 相等） | **OPEN-4 §4.3 恢复规则**（回执失效不自动关 demand、demand 关闭不改回执；I-06-A C5_C6 实测） | GREEN | GREEN | 守卫（两域天然解耦；变异耦合即红） |
| H1 | gaps 三值 missing/unsupported/not_applicable 往返逐值可区分（长度 3、set 相等） | **OPEN-5 C6**（函 C 三值 `missing/unsupported/not_applicable`）、OPEN-4 §4.5 条 6 | GREEN | GREEN | 守卫 |
| H2 | GAP-2 期间：(a) consumer_analysis=not_applicable 的 gap 必须拒绝；(b) 阻塞请求必须落 consumer_analysis 条目且态 ∈{missing,blocked} | **OPEN-5 C6**（登记册:902 一手出处：GAP-2=阻塞；不得伪装 ok / 记 not_applicable） | **RED**（无验证者、_demand_gaps 无该条目） | **RED** | **blocked-on-implementation**：OPEN-5 C6 实施检验面（gaps 校验者尚无任何一方实现；修复卡 oracle 范围不含 gaps 语义） |
| I | 确定性读-改-写交错（A 读旧值→B 全写→A 落写）⇒ 每次 ack 读回可证（主回执或 audit trail）；acks+rejections==2 零第三态 | **FIX oracle P6-A**、probe06 lost_write_count=7、**OPEN-6 §7.4 F**（冲突即拒、静默=敌）、OPEN-4 §4.1 反例 (i) 同族 | **RED**（I2：B 的 ack 无处可证 = 静默顶掉） | **GREEN** | 修复卡 **P6-A**（CAS + audit trail） |
| J | 无授权元组 + 无信任根写 detected_and_ignored ⇒ 拒绝（前缀 `disposal authorization unavailable: `）且产品语义行数 = 0 | **OPEN-6 C1/C2/C3**（§5：身份落地前零行）、**FIX oracle P5-b** fail-closed 形态 | **RED**（J1 写入被收、J2 语义行数=1） | **GREEN** | 修复卡 **P5-b**（disposal gate）+ P5-c 双绑定必填同门 |
| K | 类无 resume/complete 属性；CLI 不接受 resume/complete（exit 2）；RF 产品入口无 resume 命令 ⇒ 断言接口不存在 | **OPEN-5 事实确认**（handoff L240「不得假装存在」）+ §6.1；**FIX oracle P3 边界**（resume/complete 归 I-06-B 实施卡） | GREEN | GREEN | 守卫（若有人假装存在即红——I-06-B 本卡持续守此诚实） |
| L1 | MP-1 阻断句：RF 产品 :154-156 两段字面量拼接逐字 == 冻结句；候选 patch base 调用逐字 == ；apply 锚 join 逐字 ==（三副本收敛） | **P4-SCOPE M-P2#14**、**OPEN-5 C8**（handoff L146 悬置：跨仓文本断言钉住） | GREEN | GREEN | 守卫（钉本身 = 本套件交付；1-byte 变异即红） |
| L2 | `demand_store_error=` / `demand_queued` / paused-worker 三支：冻结夹具下 block_message **全串逐字相等**（非子串） | **P4-SCOPE M-P2#18**、**OPEN-2b c7 错误契约** | GREEN | GREEN | 守卫（clause pin） |
| L3 | RF `tests/test_message_contract_pins.py` 存在且含 MP-1 逐字断言 | **P4-SCOPE Face 2**（FIX oracle P4）、**OPEN-5 C8** 钉住 | **RED**（文件不存在） | **RED** | **blocked-on-fix-card**：P4 Face 2 是修复卡明示交付物（其 oracle §0 carve-out），产品测试面不在本 attempt 写权限内（零产品写入边界） |
| M1 | policy 仅版本标签变（内容哈希不变）⇒ evaluate 仍 `hit`；签名无版本参数；内容哈希变 ⇒ `ignored` 对照 | **OPEN-4 条件 C5①**（裁定 §5 明文「解锁给 I-06-B 的可失败测试清单」两条新正例之一） | GREEN | GREEN | 守卫（正例 + N2b 对照双臂） |
| M2 | role_set/请求身份变 ⇒ 原回执仍 `hit`（回执域无角色/请求轴）；role_set 变 ⇒ demand 新键（键域入角色） | **OPEN-4 条件 C5②** + §4.3 分域（请求身份的 demand 新键半条由 A 断言） | GREEN | GREEN | 守卫 |

## 3. 哪些修复卡修复被本套件抓到（RED original → GREEN fixed）

| 修复卡组 | 承载用例 | RED 形态（original 实测） | GREEN 快照 |
|---|---|---|---|
| **P7（APPEND-A，键修订）** | A | 同 id/同键单行吸收、request_sha256 停留首请求 | snap2 |
| **P1（additive migrator）** | C | `new_columns=[]` 空转、补后 register/claim 崩 | snap1+snap2 |
| **P1-e（错误型包装）** | F1 | claim 裸 `OperationalError: no such column: lease_until`；list_active 裸 `IndexError` | snap1+snap2 |
| **P2-B（定义拒绝）** | D | 输家裸 `None`（code=null, text=null）；by-id `TypeError` | snap1+snap2 |
| **P3-A/P3-B（过期回收）** | E | 无 `expire`；running+过期永久搁浅；by-id `TypeError` | snap1+snap2 |
| **P5-b（处置门）+ P5-c** | J | 无授权元组/无信任根写入被收，产品语义行数=1 | snap1+snap2 |
| **P6-A（CAS+audit）** | I | B 的 ack 读回不可证 = 静默顶掉（probe06 同形） | snap1+snap2 |
| **P6-B（锁包装）** | F2 | 裸 `sqlite3.OperationalError: database is locked` | snap1+snap2 |

未被本套件覆盖的修复卡组（如实）：**P4 Face 1 的变异证真臂**（其自证）、**P5-a 载荷绑定正负例**（其自证；
本套件 J 例经由 P5-a 校验链间接行使）、**C7 state_domain 双负例**（其自证；本套件经 fixed 写入/读取链
间接行使但不断言 C7 文本）、**P4 Face 2**（= 用例 L3，双红待其落地）。

## 4. 快照纪律与诚实记录

1. 修复卡在本 attempt **进行中**（evidence 时间戳 22:29–23:05 持续增长；其 store 源 mtime 23:04:28）。
   本套件因此采用**双快照**：snap1（0b6e723e，P7 前）与 snap2（cd071322，APPEND-A 后），
   两次运行证据都保留；binding.json 记录全部 sha256。GREEN 半场结论 = as-of 快照，不作修复卡验收。
2. **oracle 冻结纪律**：正文先于任何运行写就；P7 落地属事后事实，按本计划通行的 dated-append 形态落
   `APPEND-1`（additive-only、original 列一字未改、**先于 snap2 运行**写就），snap1 结果原样保留。
3. **harness 自身两处缺陷已修并如实记录**（非被测面）：① `record_kwargs` reviewer 参数重复
   （证据 I.json/J.json 曾以 TypeError 形态暴露——正是 evidence-driven 修复）；② GBK 控制台
   UnicodeEncodeError（stdout reconfigure utf-8）。修复后完整重跑两臂，最终 evidence 全部来自修复后运行。
   （首版 I/J 与两批首跑的残存面见 §4 条5 索引 `evidence/red_first_run_recovered/index.md`。）
4. **零越界**：产品树/历史 attempt 零写入（本 attempt 全部写入落在自身目录 + `%TEMP%/i06b_*`）；
   无 git、无网络；套件仅 stdlib+sqlite3。
5. **复审 F-01 缺陷记录（首跑工件覆盖）** —— 增补于复审 ACCEPT WITH FINDINGS（`reviewer_report.md` §3 F-01）
   之后，append 形态；18 用例判定与 oracle 冻结正文一字未动：
   - **缺陷类 = 证据保留**：run1（23:05:37–39，GBK 崩溃于 case G 打印）与 run2（23:05:54–56，I/J 被
     record_kwargs reviewer-kwarg TypeError 污染）的 `evidence/red/*.json` 与两段 `run_log` 被 run3
     （23:06:27–30）**同名覆写**（未执行删除命令）；原 commands.json 同句内
     「no evidence deleted / run_log rewritten」**自相矛盾**且高估了留存面。
   - **修复**：① 抢救 `%TEMP%` 两批 scratch（13+20 目录，%TEMP% 原件未删未动）入
     `evidence/red_first_run_recovered/`（`manifest.json` sha256 `e5736d7a3d3da907…`）；
     ② 转录件 `transcription_first_run_observed.md`（执行者会话直读的 run2 首版 I/J 全文 + run1 崩溃
     控制台输出，**明确标注为转录、非原始字节**，不伪造为原始工件）；③ commands.json 改为如实两段式
     （原句逐字保留于 `__historical.original_notes_sentence_before_F01_fix`）；④ 三处文字自述各带索引行：
     本条（decision.md §4 条5 ⇔ `evidence/red_first_run_recovered/index.md`）、commands.json
     `first_run_recovered_index`、handoff.json `honesty_notes[2]`。
   - **不可恢复（如实 ABSENT，未伪造）**：run1/run2 的 `evidence/red/*.json` 与 `run_log.txt` 原始字节。
6. **复审 F-02 注记（binding pre-run 自述更正）**：`binding.json` 盘上定稿 = 2026-09-22 23:13:21（三臂运行
   之后、内嵌 evidence_anchors），其 `protocol` 原句「step 2 (binding) written before any run」对**本文件**
   在盘上不可核，已改写为如实两段（原句逐字保留于 `binding.json.__historical`）；**盘上 pre-run 证明件仅
   `oracle.md`**（CreationTime 22:54:32 < 首跑 23:06:27；APPEND-1 LastWrite 23:12:44 < snap2 运行
   23:12:48）；`scripts/run_cases.py` mtime 23:06:24 = 首跑后修订，该修订史已由 commands.json
   CMD-I06B2-RED-ORIGINAL 披露（并入 §4 条5 的 F-01 记录）。九步法 step 2 的时序主张自此只以
   oracle.md 元数据为证，不以 binding 自述为证。

## 5. 未映射 / 未签

- **unmapped = []**：18/18 用例均映射到 ratify 裁定条款（逐例见 §2 表第 3 列）。
- **unsigned**：本 attempt 不代签任何方；handoff.json `implementer_signed=false`；
  独立 reviewer 验收另行进行（第 9 步接续）。
