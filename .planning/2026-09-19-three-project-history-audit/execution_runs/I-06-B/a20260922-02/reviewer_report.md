# reviewer_report.md — I-06-B / a20260922-02（独立复审 · 第 9 步接续）

- 复审对象：`execution_runs\I-06-B\a20260922-02`（九步执行法，交审时 status=`review_pending`、`implementer_signed=false`）
- 复审身份：**独立 reviewer（签署方）**；本报告不代签 implementer / owner 任一方（never self-sign）
- 复审时间窗：2026-09-22 23:16–23:2x（在 FIX 卡仍在途期间进行）
- 工具面：仅 `read` / `grep` / `pwsh`（只读 + `%TEMP%` 复跑）；**未执行任何 git 动词**；未写产品树、未写历史 attempt
- 对照面：`execution_runs\FIX-W06-GAPS\a20260922-01`（READ-ONLY，其时点态被当作比较面）

---

## 0. 结论

**VERDICT = ACCEPT WITH FINDINGS（通过，带 7 条 findings；本卡 scope = 可失败测试套件，交付面成立）**

- 三臂计数、8 项 RED→GREEN 翻转、8 项双绿守卫、2 项 blocked 双红，全部按盘上证据复核相符；
- 三条指定 spot 复跑（A@snap2 / A@original / J@snap2）**逐条符合预期**；
- 5 项条款映射抽样逐字对到 SOURCE 裁定文本，未见杜撰条款；
- 边界（零产品写、历史 attempt 未动、无 git、stdlib-only）在**文件元数据层面**成立；
- 7 条 findings 中 1 条 MEDIUM 涉及「honesty-not-deletion」的字节面（F-01），1 条 MEDIUM 涉及 binding 的 pre-run 自述不可核（F-02），其余为 LOW/INFO。

---

## 1. 复跑证据（reviewer 自跑；全部写入 `%TEMP%`）

| # | 目标 | 命令（实际执行） | 结果 | 判定 |
|---|---|---|---|---|
| R1 | case A on snap2 iso | `python scripts/run_cases.py --iso fixed --case A --out %TEMP%\rev_i06b_A_snap2` | `A PASS`（A1/A2/A3 全 ok，`key_version=request-identity-v2`，两行两键两 request_sha256） | ✅ 预期 GREEN |
| R2 | case A on ORIGINAL iso | `python scripts/run_cases.py --iso original --case A --out %TEMP%\rev_i06b_A_orig` | `A FAIL` = `A1_two_rows_distinct_ids, A2_distinct_demand_keys, A3_row_binds_own_request_sha256`（rows=1、key1==key2=07a602c1…、row2 request_sha256 停留首请求） | ✅ 预期 RED＝静默合并 |
| R3 | case J on snap2 iso | `python scripts/run_cases.py --iso fixed --case J --out %TEMP%\rev_i06b_J_snap2` | `J PASS`；`J1` detail = `type=PromptInjectionReviewError text='disposal authorization unavailable: ignore_reason'`，前缀 = `disposal authorization unavailable: `；`J2 product-semantic rows = 0` | ✅ 预期 GREEN＋前缀命中 |
| R4 | case L3 现盘补充跑 | `python scripts/run_cases.py --iso fixed --case L3 --out %TEMP%\rev_i06b_L3_now` | `L3 FAIL`：`L3a_pin_test_exists ok=true`（文件已在）/ `L3b_pin_test_pins_frozen_sentence ok=false`（源码文本非连续串） | ⚠️ 见 F-03 |

复跑后的 `%TEMP%\rev_i06b_*` 四个目录为 reviewer 证据（保留）；reviewer 产生的 3 个 `i06b_*` scratch 目录已删除，实现者原有 93 个 `i06b_*` scratch 未动。

---

## 2. 逐项核验（对应委派清单 1–6）

### 2.1 交付件

- **oracle.md 冻结先于运行**：`CreationTime=2026-09-22 22:54:32` < 首个 RED run `started_at=23:06:27`；`LastWriteTime=23:12:44` < snap2 run `started_at=23:12:48` ⇒ **APPEND-1 写于 snap2 运行之前**（4 s 余量，时序成立）。
- **APPEND-1 = 追加而非重写**（文本面证据）：正文 §4 仍写「fixed 快照 = **15 GREEN / 3 RED（A,H2,L3）**」且 A 行 `期望 fixed` 仍为 `RED→blocked`——与最终 16G/2R 结果**故意不一致**；若发生整文件重写，正文计数会被改平。`APPEND-1` 标题自带「additive-only；original 列一字未改」。⇒ 追加形态成立；**pre-append 原始字节未留存**（见 §4-3）。
- **binding.json 全 sha 锚 re-hash**：`oracle.md 6b55191f…`、`scripts/run_cases.py 16561244…`、`scripts/_worker_claim.py 8003c96f…`、`evidence/{red,green,green_snap1_0b6e723e}/summary.json = 0193a199… / 22765e7a… / ab62a185…` —— **6/6 命中**。
- **iso 快照 re-hash**：original 店 `7bc5feb0…`（= I-06-A iso/candidate 与 FIX before/candidate 三方同一字节）、`orig_pi` `7b22f239…`+`f900a13d…`、`rf/source_preparation 91a6dc32…`、`rf/processing_demand fcdfcad8…`、`cw/processing_demand 90f232ed…`；**snap2 = `cd071322…`(store) + `88154de4…`(pi) + `17f0dc58…`(guard) + `c712addb…`(__init__)** —— 与 binding `iso_snapshots` **逐位相符**。snap1 `0b6e723e…` 的字节已随 iso/fixed 刷新离盘（见 F-05），其「P7 之前」性质由 `green_snap1/A.json` 的 key1==key2==`07a602c1…`（与 original 同键）行为面佐证。
- **changes.diff**：`77793 B（≈77 KB）`；3 个 `--- /dev/null` 新文件头 = `scripts/run_cases.py`、`scripts/_worker_claim.py`、`oracle.md`；reviewer 从 diff 逐行重建三文件并重算 sha256，与盘上活文件**逐字节相同**（58569/1618/14405 B）。⇒ only-harness-new-files 成立。
- **handoff.json**：`status=review_pending`、`implementer_signed=false`、`unmapped=[]`、`blocked_by=[]` —— 4/4 相符。
- **commands.json 自缺陷记录 vs honesty-not-deletion**：两条自缺陷（`record_kwargs` reviewer kwargs 重复、GBK `UnicodeEncodeError`）在 `commands.json:19`、`decision.md §4.3`、`handoff.json honesty_notes[2]` 三处如实记载；**但原始首跑工件未留存** —— `evidence/red/{I,J}.json` 与 `run_log.txt` 全部为 23:06:27–30 末次运行产物，attempt 内 grep `record_kwargs|TypeError` 在 evidence 下 0 命中；首跑仅剩 `%TEMP%` 的 `i06b_*` scratch（23:05:37–23:05:56 两批）可证其存在 ⇒ 见 **F-01**。

### 2.2 计数（盘上 summary.json 逐臂复核）

| 臂 | GREEN | RED | 红集合 | 结论 |
|---|---|---|---|---|
| RED baseline（original） | **8** | **10** | `A,C,D,E,F1,F2,H2,I,J,L3` | ✅ 与指定红集合**逐项相同**（10 项） |
| GREEN snap1（`green_snap1_0b6e723e`） | **15** | **3** | `A,H2,L3` | ✅ |
| GREEN snap2（`green`） | **16** | **2** | `H2,L3` | ✅ |

- **8 项 RED→GREEN 翻转**：`A(snap2) + C,D,E,F1,F2,I,J(snap1+snap2)` = 8 ✅（handoff `red_to_green_flips_caught_from_fix_card` 列表 8 条逐项相同）
- **8 项双绿守卫**：`B,G,H1,K,L1,L2,M1,M2` ✅（snap1 与 snap2 两臂 verdicts 均 PASS）
- **2 项双红 blocked**：`H2,L3` ✅
- snap1→snap2 仅 `A` 一处翻转，与「P7 键修订在 snap2 时点已落」自洽；`run_log.txt` 三臂时间轴 23:06:27–30 / 23:06:39–41 / 23:12:48–50 与 summary `started_at/finished_at` 一致。

### 2.3 与 FIX 卡已落工作的交叉核对（8 翻转 ↔ FIX 证据）

| 翻转 | FIX 对应 GREEN 证据（FIX attempt 内实存） | 复核 |
|---|---|---|
| P7 → A | `evidence/p7_key_c8c9c10_GREEN.txt`（23:05:59，c8/c9/c10 distinct_ids/distinct_keys=true）+ `p7_key_c8c9c10_RED.txt` | ✅ |
| P1 → C | `evidence/GREEN_P1_migration.txt` + `scripts/s_p1_migration.py` | ✅ |
| P1-e → F1 | 同上 `GREEN_P1_migration.txt` L82–84：`DemandStoreUnavailable … [store_owned=True]`（S6 迁移器旁路三路径类型化） | ✅ |
| P2-B → D | `evidence/GREEN_P2_claim_refusal.txt`：`code=DemandStateError, text="demand … is not claimable"` | ✅ |
| P3 → E | `evidence/GREEN_P3_lease_expiry.txt`：`lease expired` / `expire()` rc=0 / 过期后行 lease 清空 | ✅ |
| P5-b → J | `evidence/GREEN_P5_receipt.txt` L16–21：`disposal authorization unavailable…` 5 负 1 正 | ✅ |
| P6-A → I | `evidence/GREEN_P6_concurrent.txt`（P6-A 计数守恒、对照 `maps_06` 的 lost_write_count=7 RED 形态） | ✅ |
| P6-B → F2 | 同文件 L19–23：`PromptInjectionReviewError: store busy/lock timeout: OperationalError: database is locked` | ✅ |

- **snap2 一致性（binding 钉住）**：I-06-B `iso/fixed` 逐字节 = binding `fixed_snap2` 四条 sha ✅；`fixed_pi` 三文件与 FIX 现盘 `iso/pi_pkg` **同字节**（88154de4 / 17f0dc58 / c712addb）。
- **FIX 仍在演化**（review 中实时观察）：FIX `iso/candidate/processing_demand_store.py` 于 **23:20:13 被改写**（21675→22164 B，`cd071322…`→`1bbcf9ce…`，diff 起点为新增 "Oracle APPEND D" docstring）⇒ snap2 与 FIX 现盘已非同一时点，**GREEN 半场只对 snap2 有效**（见 F-07；这正是双快照纪律要防的情形）。
- **L3（两 blocked 红之一）**：RF 产品 `tests\test_message_contract_pins.py` **已落盘** —— `CreationTime 2026-09-22 23:17:17`（晚于本 attempt handoff 23:14:04）、sha `41da045c…`，与 FIX `iso\rf\test_message_contract_pins.py` 同 sha；**candidate 侧变体**在 FIX `iso\candidate\test_candidate_message_pins.py`（sha `4de498b9…`）。产品侧现状态 =「已落待验」：R4 复跑 `L3a=true / L3b=false`，详见 **F-03**。
- **H2（另一 blocked 红）**：consumer_analysis 的 gaps 校验者**在盘上任何位置均未见实现** —— RF `scripts|tests`、CW `src`、`execution_runs/**.py` 三处 grep（`validate_gaps|gaps_validat|consumer_analysis.{0,60}not_applicable|_demand_gaps`）仅命中：(a) I-06-B 自身用例 H2、(b) 候选 `w06a_candidate_patch._demand_gaps`（只枚举 `normalized,summary,sections,markdown` 四角色，无 consumer_analysis 条目、无 `missing/unsupported/not_applicable` 状态词表）⇒ **blocked 归属诚实**，欠 OPEN-5 C6 实施载体。

### 2.4 条款映射抽样（5 项，逐字对 SOURCE 裁定）

| 抽样 | decision.md / oracle.md 所引条款 | SOURCE 原文（grep 命中行） | 结论 |
|---|---|---|---|
| A | OPEN-4 §4.3「不得拿回执绑定当 demand 键」；OPEN-5 C1 / §4.5 条 1 | OPEN-4 `ruling.md:137`「**不得**拿回执绑定当 demand 键（c8/c9/c10 静默合并重演）」；OPEN-5 `ruling.md:183-185`（键= `sha256(canonical_json({source_sha256, review_policy, role_set, request_identity}))`，request_identity 覆盖 as_of_date/target/payload digest）、`:202-204` C1「仅 as_of_date 不同 ⇒ 两个不同 demand_id；行内 request_sha256 == 该请求实际哈希」 | ✅ 逐字相符；无杜撰 |
| C | OPEN-5 C4（同库同迁移） | OPEN-5 `ruling.md:210-212`「demand 表经 `_apply_additive_migrations` 落 catalog.sqlite3；prune 不删除非 terminal 行」 | ✅（用例另引 FIX oracle P1-c/P1-d 与 probe01，属修复卡自证面，已如实分列） |
| E | OPEN-5 C5（权限=OPEN-3） | OPEN-5 `ruling.md:213-214`「无有效 lease 的 resume ⇒ DemandStateError 等价拒绝；lease 过期 resume ⇒ 拒绝；全程无自动 resume」；`ruling.md:174`「崩溃恢复 = 显式 expire 等价物 + 显式重 claim」 | ✅ |
| H1/H2 | OPEN-5 C6（三值 + GAP-2 只能 missing/阻断） | OPEN-5 `ruling.md:215-218` C6「`missing / unsupported / not_applicable` 可区分三值；`consumer_analysis` 缺入口时**不得**记为 not_applicable 或伪装 ok；GAP-2 仍阻塞期间（登记册 :902）只能落阻断/missing 态」；`ruling.md:197-198` §4.5 条 6 三值不得混同 | ✅ H2 两断言 = C6 两条义务的直接编码 |
| J | OPEN-6 C1/C2/C3（§5，身份落地前零行） | OPEN-6 `ruling.md:167` C1 负例「无授权元组调用写入口写 detected_and_ignored ⇒ 被拒 fail-closed」、`:168` C2 授权元组必填、`:169` C3「**身份落地前零行**：产品语义 detected_and_ignored 行 = 0」 | ✅ 逐字相符 |
| M1/M2（附加） | OPEN-4 条件 C5①/C5② | OPEN-4 `ruling.md:151`「① policy 版本号变、内容哈希不变 ⇒ 仍 hit；② role_set/请求身份变 ⇒ 原回执仍 hit、demand 按 OPEN-2 A 得新键。这两条正是本裁定解锁给 I-06-B 的可失败测试清单」 | ✅ |
| B/G（附加） | 「OPEN-5 §4.3 恢复规则」/「OPEN-4 §4.3 恢复规则（C5_C6）」 | OPEN-5 `ruling.md:158`（§4.3 持久化介质下的恢复规则：迁移/写失败 ⇒ C7 契约 fail-closed）、OPEN-4 `ruling.md:139`（回执失效不自动关 demand、demand 关闭不改回执） | ✅ 两处 §4.3 均落到真实存在的「恢复规则」条目 |

裁定源本身校验：`rulings_transcribed_2026-09-22.md` sha `5ef8d863…` = binding/handoff 所记；三 SOURCE ruling 文件在盘（OPEN4 `42062 B`、OPEN5 `46901 B`、OPEN6 `52560 B`）。

### 2.5 边界

- **零产品写（RF+CW）**：声明只读根 `RF scripts/ tests/`、`CW src/` 在 22:45–23:15 窗口内的 mtime/CreationTime 扫描 —— `RF scripts/` 无文件变动、`CW src/` 无文件变动；`RF tests/` 仅两文件，且均**晚于本 attempt 最后写入（handoff 23:14:04）才出现在树上**：`test_fc905b_trusted_receipt.py`（L=23:15:07）、`test_message_contract_pins.py`（C=23:17:17，源 mtime 23:12:33 为复制继承）⇒ 归 FIX 卡落地，非本 attempt。**限制**：本轮禁 git ⇒ 未跑 porcelain（见 §4-1）。
- **历史 attempt 未动**：`I-06-B\a20260919-01\handoff.json` `CreationTime=LastWriteTime=2026-09-20 15:47:06`（早于本 attempt 两天）、sha `daaff3f40ba48ed36fa9cde89fde490c6a23ec433aa451562a32d3cebd934d80`；该树在 22:30–23:30 窗口内 0 个非 iso 文件变动。
- **无 git 动词**：`commands.json` 的 6 条 command 串内无 git；`git_commands: []`；attempt 全文 grep `\bgit\b` 仅命中 binding/handoff/decision/run_cases 文档串里的「无 git」自述。
- **stdlib-only**：`run_cases.py` import 集 = argparse, contextlib, hashlib, importlib, inspect, io, json, os, re, sqlite3, subprocess, sys, tempfile, time, traceback, pathlib + `__future__`；`_worker_claim.py` = argparse, importlib, json, sys, pathlib。**零第三方依赖**；scratch 走 `tempfile.mkdtemp(prefix="i06b_")` ⇒ `%TEMP%` 内。

### 2.6 双快照纪律

- binding `iso_snapshots` **两份快照的 sha256 齐备**（snap1 三条、snap2 四条 + source mtime 注记）✅；**运行时间戳不在 binding**，落在 `evidence/*/summary.json` 的 `started_at/finished_at`（23:06:27 / 23:06:39 / 23:12:48）⇒ 部分满足，见 **F-04**。
- **GREEN 证据 as-of 快照标注**：靠目录名 `green_snap1_0b6e723e/` + binding 锚 + handoff/decision/oracle 三处文字声明；**证据文件内部（case JSON / summary.json）只带 `iso:"fixed"`、不带快照 sha** ⇒ 部分满足，见 F-04。三处文字均明确「as-of 快照 ≠ 修复卡验收」（handoff `honesty_notes[0]`、decision §4.1、oracle §1 判定行）✅。
- **APPEND-1 早于 snap2 运行**：oracle `LastWrite 23:12:44` < snap2 `started_at 23:12:48` ✅；正文冻结 `Creation 22:54:32` < 首个运行 23:06:27 ✅。

---

## 3. Findings（编号）

**F-01（MEDIUM）honesty 有文、字节面不足 —— 首跑原始工件未留存**
`commands.json` 第 2 条 notes 写「strictly incremental: no evidence deleted, run_log.txt rewritten once」，但盘面是：`evidence/red/{A..M2}.json` 与 `run_log.txt` 全部为末次运行（23:06:27–30）覆盖写，首跑（`%TEMP%` scratch 证明存在于 23:05:37–39 与 23:05:54–56 两批）的 `I.json`/`J.json`（`record_kwargs` kwargs 重复的 TypeError 形态）与首段 run_log 均已不在。⇒ 「两条自缺陷已如实记录」成立，「raw first-run artifacts present」**不成立**；同句的 `no evidence deleted` 与 `run_log rewritten` 自相矛盾。影响：自缺陷的**原始证据不可独立复核**（只剩 `%TEMP%` scratch + 三处文字自述）。建议：此类自缺陷工件按 `evidence/red_selfdefect_round1/` 保留，或把 notes 改为如实的「overwritten, not preserved」。

**F-02（MEDIUM）binding 的「pre-run 写就」自述在盘上不可核**
`binding.json` `protocol` 字段写「step 2 (binding) written before any run」，但该文件 `CreationTime = LastWriteTime = 2026-09-22 23:13:21`（三臂运行 23:06–23:12 之后），且内容内嵌 `evidence_anchors`（只能在运行后存在）⇒ 盘上**不存在**任何 pre-run 版本。同理 `frozen_artifacts.run_cases.py` 的落盘 mtime=23:06:24（首跑 23:05 之后、末次 RED 前 3 s），即 harness 在首跑后被修过（commands.json 已披露）。⇒ 九步法「step 2 先于任何运行」在盘上仅对 **oracle.md** 有元数据证明（22:54:32）。建议：step 2 落盘即取 sha 并另存 `binding_freeze.sha256`，后续扩写用 dated APPEND。

**F-03（LOW）L3b 断言过严 —— 已落盘的产品 pin 测试会继续判 RED**
`run_cases.py:1107` 用**源码文本连续子串** `MP1 in text` 判定；RF `tests\test_message_contract_pins.py` 的 `BLOCK_SENTENCE` 由两段相邻字面量拼成，断行点在 `…blocked per ` / `policy (…)`，故源码文本**不含** MP-1 连续串；reviewer 用 `ast` 复算：运行期常量 `BLOCK_SENTENCE == MP-1` 且 `count == 1`（该测试自身用 AST 常量断言产品侧，语义正确）。⇒ R4 实测 `L3a=true, L3b=false`；**照 recovery/README 的复跑命令，L3 不会翻绿**。影响仅限 L3 一例（H2 仍真红）。处置二选一：产品 pin 测试改为单段字面量，或 I-06-B 侧 L3b 改为 AST/运行期等价判定（属 harness 改动 → 新 attempt/dated APPEND，不由本报告代改）。

**F-04（LOW）双快照标注只到「目录 + 文档」层，未进证据文件**
binding 记了两份快照 sha，但**没有运行时间戳**；`summary.json` / 各 case JSON 内**没有快照 sha**（两臂都写 `iso:"fixed"`），as-of 归属依赖目录名 `green_snap1_0b6e723e` 与三处文字声明。当前可追溯（binding 锚 + 时间轴 + A 例行为差异三重互证），但机器可读的 as-of 标签缺失。建议：summary 增 `snapshot_sha256` 与 `started_at` 写入 binding。

**F-05（LOW）snap1 字节已离盘，`0b6e723e…` 只剩声明**
snap2 刷新覆盖了 `iso/fixed/cand/processing_demand_store.py`，snap1 的原始字节在本 attempt 与 FIX 侧均不可再取（FIX 现盘已到 `1bbcf9ce…`）。⇒ snap1 sha **不可复算**；其「P7 之前」性质仅由 `green_snap1/A.json`（key1==key2==`07a602c1…`，与 original 同键）行为面佐证。建议：快照刷新按 `iso_fixed_snapN/` 并存而非覆盖（recovery/README 已有同向流程，执行层用了覆盖）。

**F-06（INFO）reviewer 自身副作用披露**
本报告前的 R1–R4 复跑在 `iso/{fixed,original}` 下产生 4 个 `__pycache__`（CreationTime 23:19:30–31，实现者末次运行后树上 0 个 pycache）。reviewer 已**立即删除**该 4 目录：`iso/` 回到 18 个 `.py` 文件、`__pycache__` 计数 0；**残留影响限于 4 个目录的 LastWriteTime**（现均为 reviewer 清理时刻 23:30:49；复审前实测值 = `iso\fixed\cand` 23:14:30、`iso\fixed\fixed_pi` 23:14:30、`iso\original\cand` 23:10:04、`iso\original\orig_pi` 23:10:06，形如实现者自己的 pycache 清理时刻）。文件字节、交付件、binding 锚均未变。`%TEMP%` 下 reviewer 的 3 个 `i06b_*` scratch 已删除，4 个 `rev_i06b_*` 复跑输出保留为 reviewer 证据，`%TEMP%\rev_i06b_verify_hashes.py` 为本轮校验脚本。除 `reviewer_report.md` 与 `reviewer_report.sha256` 外，attempt 内无 reviewer 写入物。后续复跑请带 `-B` 或 `PYTHONDONTWRITEBYTECODE=1`。

**F-07（INFO）FIX 卡在本复审期间继续演化**
FIX `iso/candidate/processing_demand_store.py` 于 23:20:13 由 `cd071322…` 变为 `1bbcf9ce…`（21675→22164 B，新增 Oracle APPEND D docstring）；FIX 的 `changes.diff`、mutation 证据、产品 `tests/` 落盘均在 23:14–23:2x 期间持续更新。⇒ 本报告的 GREEN 判定一律 **as-of snap2**，与 FIX 验收互不替代（FIX 有其独立复审）。

---

## 4. 未验证 / 限制（如实）

1. **git porcelain 未跑**（本轮边界禁 git 动词）：零产品写以 RF `scripts/ tests/`、`CW src/` 的 mtime/CreationTime 扫描 + `binding.product_anchors` 活字节复算为据；RF 仓全量扫描一次超时（120 s），只完成声明只读根与仓顶层 2 层扫描。`.git` 目录 `LastWriteTime=23:22:32` 表明窗口内有 git 活动，**归属未能判定**（时点在本 attempt 最后写入 23:14:04 之后，倾向 FIX 落产品测试所致）。
2. **snap1 `0b6e723e…` 字节**不可复算（F-05）；**pre-append oracle 原始字节**与 **pre-run binding 版本**均未留存（F-02），相应自述只能由元数据时序 + 文本内不一致性间接支持。
3. **复跑面为抽样**：只自跑 A×2、J、L3 共 4 次；三臂 18×3 的完整计数取自已验 sha 的 summary.json，未整臂重跑（整臂重跑会按 recovery/README 覆写同名用例 JSON，属 attempt 写入，超出本轮边界）。
4. **8 项双绿守卫的「可失败性」未由 reviewer 变异验证**（只核其两臂 PASS 与条款映射）；守卫的 mutation 证真属实现者侧未交付项之一（oracle §4 只声明「变异/回归即红」为守卫性质）。
5. **RF 产品 pin 测试自身是否通过 pytest 未跑**（会写 `__pycache__`/`.pytest_cache` 到产品树，越界）；F-03 只判 L3b 与该测试源码形态的关系。
6. **FIX 卡交付物未审**：本报告只把 FIX 当比较面读取；`GREEN_*.txt`、mutation、产品 `tests/` 落盘均按「存在 + 关键串命中」核，未做 FIX 侧逐字复算。
7. 中文渲染：本次会话部分 `pwsh` 输出经 GBK 控制台出现 mojibake（如 `§→搂`），**盘上文件为 UTF-8 正常**（以 `read` 工具核 oracle/裁定原文为准）。

---

## 5. 若验收通过的 scope 声明（供落定）

1. **本卡验收对象 = 可失败测试套件本身**（18 例、三臂证据、条款映射、边界），不含产品实现、不含修复卡验收。
2. **L3 翻绿条件**：产品 pin 测试已落（`RF tests\test_message_contract_pins.py`, sha `41da045c…`, FIX 侧 candidate 变体 `iso\candidate\test_candidate_message_pins.py`）；但 F-03 使其**复跑仍 RED(L3b)**。复跑命令（写 `%TEMP%`，避免覆写本 attempt 证据）：
   `python scripts/run_cases.py --iso fixed --case L3 --out %TEMP%\rev_L3_after_pin`
   翻绿前置二选一：① pin 测试 `BLOCK_SENTENCE` 改单段字面量（产品侧/修复卡侧动作）；② I-06-B 侧 L3b 判定改 AST 等价（harness 改动 → 新 attempt + dated APPEND，按本计划 freeze-before-run 纪律）。
3. **H2 归属**：OPEN-5 **C6 实施载体**欠账（consumer_analysis 的 gaps 校验者：GAP-2 期间只能 `missing/blocked`、拒绝 `not_applicable/ok` 伪装）；RF/CW/execution_runs 三处 grep 均未见实现，候选 `_demand_gaps` 无该角色条目 ⇒ **OPEN-5 C6 implementation carrier owed**，不由本卡承载。
4. **GREEN-as-of-snapshot ≠ FIX acceptance**：本报告对 8 项翻绿的判定绑定 `cd071322…/88154de4…` 快照与 23:12:48 运行；FIX 卡在 23:14 之后继续改动（F-07），**FIX 取得其独立复审**，本报告不构成对 FIX 的任何验收。
5. F-01/F-02 的补救属流程改进项，不阻断本卡（其内容自述方向为如实，缺的是留存/时点证明）。

---

## 6. 复审复算清单（本报告引用的 sha256，均为 reviewer 现场重算）

```
oracle.md                                    6b55191f2d7c5b1325464e177df8a21754ce08c679a297ec96c3828799c2ef8c
scripts/run_cases.py                         1656124425564bc553cc5c6c9918e3a355157016bc1a4b8f34713967d9115930
scripts/_worker_claim.py                     8003c96fc1fa06a1301dd41d815ad150df3febf74a856af9eaa3497a93028774
evidence/red/summary.json                    0193a199355d18d94e0737265923c927ad9367b8848baca03420d3b6e342c27e
evidence/green/summary.json                  22765e7ac24b6051b861affb0569d89b4e527c57835c883426d542794f0d6d2d
evidence/green_snap1_0b6e723e/summary.json   ab62a185f54c86bfaa83a6d001160f595e7e6b71616b46cfc1b5c48dbc3909a6
iso/original/cand/processing_demand_store.py 7bc5feb0cb5e50227a49ac7322c654f84b04f4b71d9d6578571f0899405b8f7f
iso/fixed/cand/processing_demand_store.py    cd07132212cacb14f9f1dc04bc2155cb5b080b99fc3146119dcf052958d66d40 (snap2)
iso/fixed/fixed_pi/prompt_injection.py       88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33 (snap2)
iso/fixed/fixed_pi/prompt_injection_guard.py 17f0dc58f6530f0f0f8dbe5099cd655edfe3b7b4404300e3e594ef38534ed31b (snap2)
iso/fixed/fixed_pi/__init__.py               c712addbc3c2592d39cb6fde3a0d40307d2387055adaadece4177b546857f67f (snap2)
rulings_transcribed_2026-09-22.md            5ef8d863e3656962836f83eee4ddd87e8712b174491715cbd856b8593fcb8d91
RF scripts/source_preparation.py (live)      91a6dc32466e9d67b9d034ac345349ee683f6d5fd9486a67cd3ade009c6ebf4d
RF scripts/processing_demand.py (live)       fcdfcad8ebd1fc20febf3c157dcd20ad92708fd69d00373ef9a943e5a820afc1
CW prompt_injection.py (live)                7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618
CW prompt_injection_guard.py (live)          f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08
CW processing_demand.py (live)               90f232edb7804f78a16c6b4e865255cd607a1d0dc30384fc1cd6faa1833ac88b
RF tests/test_message_contract_pins.py       41da045cacd4e902fbd0ca5dbc7b21fa134ecb2a1dea1ac023ab419b98b0e2d4 (post-attempt, FIX-landed)
I-06-B a20260919-01 handoff.json             daaff3f40ba48ed36fa9cde89fde490c6a23ec433aa451562a32d3cebd934d80 (mtime 2026-09-20 15:47:06)
changes.diff (77793 B, reconstructs 3 files byte-identical)
```

上表 19 条 sha256 由 reviewer 以脚本逐条现场重算并与报告内所记值比对（`MISMATCHES: 0`）；凡与 `binding.json` / `handoff.json` 记载重叠的条目（oracle、两 harness 脚本、三份 summary、original/snap2 iso、rulings、RF/CW 产品锚）**逐位相符**。`changes.diff` 为 77793 B 且可重建三文件字节相同。

---

## 7. 自检与签署

- **REM-79 自检**：`python execution_runs\REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py reviewer_report.md`（attempt 内 tools/，非 repo-root）⇒ 本报告实测 `0 violation(s) across 1 file(s)`，exit=0；`.sha256` 对本文件最终字节计算。
- **签署**：独立 reviewer（本报告 = 第 9 步接续的验收载体）；`implementer_signed` 维持 `false`（由实现者侧另行签署），本报告**不代签任何其他方**。
- 报告文件：`reviewer_report.md` + `reviewer_report.sha256`（本次复审的唯一写入物）。
