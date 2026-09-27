# WC-6-ADAPTER-DISPATCH 复审裁决落定（review.md）

> **本文件由 carrier-landing 簿记 pass 创建，创建前本 attempt 无 `review.md`。**
> 创建前本 attempt 根仅含：`binding.json` / `changes.diff` / `commands.json` / `decision.md` / `handoff.json` / `oracle.md` / `reviewer_report.md` / `reviewer_report.sha256`，以及 `after/` `before/` `evidence/` `harness/` `inputs/` `iso/` `recovery/` 目录。
> **本文件只转录，不产生新裁决、不自签**：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`。
> 转录者 = carrier-landing 簿记执行者（与实现者、复审者均非同一人）；本 pass 未重跑任何命令、未联网、未跑测试、未做 git 写操作。

---

## 0. 裁决来源（唯一权威）

| 项 | 值 |
|---|---|
| carrier（唯一权威） | `reviewer_report.md`（本 attempt 内，全程只读） |
| 字节 | **33362 B** |
| sha256 | **`661e833ce86f2ac639c7d2d91f7e43dc98d0231d69408a8d5252e41567b7c4cb`** |
| 侧车 | `reviewer_report.sha256`（**85 B**，内容 `661e833c…7c4cb␣␣reviewer_report.md` + LF；本 pass 只读，0 字节写入；落定时独立重哈希 == 侧车 == 派发钉值，MATCH） |
| 总行数 | **263 行**（LF-only、0 CR、末行带 LF） |
| 裁决行 | 第 **263** 行；字节区 **[33346, 33361]**（0-based，含行尾 LF，16 B）；该行 sha256 `ffd796ea6572fdaf4dce6d9984e6e9294cf8c0c564ce345d73132bf29aa1b3b4` |
| 裁决行文本 | `VERDICT: ACCEPT` |

字节区定义（与本计划既往落定一致）：0-based 字节偏移，按文件处于上述 sha256 状态时计算；单行区**含**行尾 LF；多行区**含**内部 LF、**不含**末尾 LF。
本 pass 复算的其余区段（供父/后续复算）：§2 两非目标 [14879,19367] / `e00ad6f9…`、§3 REM-95 [19375,22986] / `1c522d1d…`、§4 幂等永拒 [22994,25680] / `68c682ad…`、§5 边界 [25688,27199] / `57cb25be…`、§6 发现 [27207,30829] / `4abe034f…`、§7 未验证 [30837,32372] / `74189fce…`、§8 结论 [32380,33361] / `e82e054e…`。

---

## 1. 裁决转录

**`VERDICT: ACCEPT`**（`reviewer_report.md:263`）。

- **P1 = 0 ⇒ 本裁决不是 `changes_required`**（报告 §6 首行「**P1：0 条。**」）。
- 发现计数：**P1 = 0 / P2 = 2 / P3 = 4**，另有一组未验证项（报告 §7，共 6 条）。
- 据此，`handoff.json` 顶层 `status` 由 `review_pending` 落为 **`accepted_scoped`**（scoped，**非 clean**：P2-1/P2-2 随卡移交，P3-1..P3-4 为证据/归档完整性项）；`status_before` 保留原值 `review_pending`；权威写入 `status_authority`（carrier = `reviewer_report.md`，行号/字节区/sha256 全值 + `verdict_line_text`）；`status_history` 追加两条（round 1 载判 + carrier landing 转录）。
- 本 pass **不签署任何验收**：`implementer_signed=false`、`verdict_is_transcribed_not_authored=true`。

### 1.1 发现表（原文摘要 + 处置 + 是否阻断）

| id | 级别 | 原文摘要（转录自报告 §6） | 处置 | 是否阻断 |
|---|---|---|---|---|
| **P2-1** | P2 | `wc6_common.strip_volatile` 的 marker `"now"` 命中 `known_quarantined` **子串** ⇒ 该键被从**所有**字节比对中**静默剔除**，oracle §4 明文要求的不变量**实际未被比较**（`compare_*.json > idempotency` 里 `known_quarantined` 恒为 `null`，读者会误以为「已比较相等」）；复审者用原始 `scan_runs.report_json` 独立补证 ⇒ **结论为真、证据有洞**；建议改整键匹配并补披露。**（关键发现，逐字随卡携带，不得弱化）** | **本卡不改**（oracle/binding/harness 已冻结，且报告明示「建议（低成本）…本卡不改」）⇒ **随卡移交父代理/登记册**：`strip_volatile` 改整键精确匹配/白名单（或对 `scan_runs.report_json` 单独按 oracle §4 键表比对），并在 decision §7 item4 / oracle §4 披露补 `known_quarantined` 一格，登记册该句补「known_quarantined 由复审以原始 report_json 独立证等」。 | **否**（P2 不阻断 ACCEPT；报告 §8 判 ACCEPT） |
| **P2-2** | P2 | REM-95 关闭文案**必须同时**记下 C1 第二表面 `documents.metadata_json.acquisition` 无 remediation 键**仍未修**（若不记则升 P2）。owner = 登记册/父代理，非实现者；本卡已如实披露（decision §9、handoff `open_questions` 第 1 条），故计为**处置前置条件**而非实现者过失。**（关键发现，逐字随卡携带，不得弱化）** | **路由父代理**：登记册处置 REM-95 时**必须显式记下该未覆盖面**（另立一行，或在 REM-95 行加注「C1 第二表面未修，另派」）；**本 pass 不改登记行**。 | **否**（不阻断本卡裁决；但**是 REM-95 关闭文案的前置条件**，漏记则升级为 P2） |
| **P3-1** | P3 | 引文与证据不匹配（claim 为真、证据文件缺半边）：`evidence/complexity_before_after.json` 的 `iso_after_per` 两处皆 `{}`，而 `evidence/README.md`、decision §3、登记册「逐函数同」都以该文件为引文；复审者 AST 独立复算证实 claim 成立（§1.4a）。 | 证据完整性问题：应补录 iso 侧逐函数值（补录属本卡既有证据面，父代理决定是否派补录）。 | 否 |
| **P3-2** | P3 | 冻结命令表里有未执行的命令：`commands.json` 声明 `fam_live_before (--cwd live)` 与 compare 对 `["fam_before","fam_live_before"]`，但 evidence 中无任何 live 家族文件、`handoff.commands_executed` 也未列该条；仅有 `disclosures.no_live_family_run=true` + decision §7 item8 披露（理由：他 agent 并发跑 live 套件）。披露在，账不平。 | 应在 commands.json 侧标注 dropped（或在 `commands_executed` 记 `not_executed`）；本 pass 不改 `commands.json`（既有 carrier 只读）。 | 否 |
| **P3-3** | P3 | handoff 里的命令 id 不在冻结清单：`commands_executed` 含 `CMD-WC6-RESCAN-<label>`（三臂），而 `commands.json.commands[]` 无 RESCAN 条目（该臂系 oracle 冻结后新增，decision §7 item9 已披露）⇒ 归档不一致。 | 建议补一行命令条目，或注明其为 scan 的第二次调用；本 pass 只记录，不改 `commands.json`。 | 否 |
| **P3-4** | P3 | 计数措辞：登记册「一一五」写「披露**四桩**（post-freeze rescan 臂、比较器剔 volatile 清单、mutation1 宿主败原样留、同哈希副本删记账、binding harness 哈希并列重录）」——括号内实为**五项**。 | 建议改为「五桩」或拆分；登记册归父，本 pass 不改。 | 否 |

> 计数核对：P1=0、P2=2（P2-1、P2-2）、P3=4（P3-1..P3-4）——与报告 §6 及 §8 结论行「**发现：P1 = 0、P2 = 2、P3 = 4**」一致。

---

## 2. 复审者实测 rc 清单（逐条抄录，不许改数）

> 全部为复审者**自己重跑**的原始 rc（报告 §1.2/§1.4/§1.5）；本 pass **未重跑任何一条**，仅转录。
> harness rc 图例（既有 `handoff.json > raw_exit_codes.harness_legend`）：`0` evidence written / `1` harness failure / `2` no verdict / `3` frozen comparison failed。

| # | 复审者实测项 | rc / 结果 |
|---|---|---|
| 1 | `pin_sources.py after` | **0** |
| 2 | `prepare.py` ×4（`green_r` / `repeat_r` / `mut_r` / `red_r`） | **0 ×4**；tree_sha 全 **`37be0c5a607cf7c4619b6381bb2eae808966e8152f875c56e9024f7ad615ad58`** |
| 3 | 四臂（red / green / mut / repeat）× 4 阶段（scan / rescan / resolve / cfg01）**harness rc** | **0**（每臂 4 阶段 harness rc 均为 0） |
| 4 | 同上四臂 **product rc** | **`scan=0` / `rescan=0` / `resolve=0` / `cfg01=1`** |
| 5 | RED 臂 `locations.error` | **NULL ×4** |
| 6 | GREEN 臂 `locations.error` | **3 串 + clean NULL** |
| 7 | MUTATION 臂 `locations.error` | **NULL ×4** |
| 8 | REPEAT 臂（repeat_postfix）`locations.error` | 与 **GREEN 同** |
| 9 | `compare_runs` red-vs-green / green-vs-mutation / green-vs-repeat | **0 / 0 / 0** |
| 10 | `reason_chain` | **0**（**4 探针 × 4 跳全中 oracle 字面**，`all_hops_match=true`） |
| 11 | 家族 `fam_rerun3`（修复态）与 `fam_rerun_pre`（pre-image） | 均 pytest **rc1 = 427P / 39F / 8S**（各 474 outcomes） |
| 12 | `compare_family fam_rerun_pre fam_rerun3` | **rc0**；`status_changed=[]`、`only_in_a=[]`、`only_in_b=[]` |
| 13 | 复杂度自算（逐函数 McCabe，live vs iso-fixed） | `adapter_dispatch` **4 == 4**、`scanner` **140 == 140**，**逐函数同** |

（对应报告原表：#1=R1、#2=R2/R5/R8/R12、#3-4=R3/R5/R8/R12 及 §1.2 汇总行、#5=R12、#6=R9/§1.2 汇总、#7=R8、#8=R5/R6、#9=R13/R9/R6、#10=R4、#11-12=§1.5、#13=§1.4a。完整 R1–R15 原表见 `reviewer_report.md` §1.2，只读。）

---

## 3. 两非目标裁（逐字转录自报告 §2）

### 裁① `documents.metadata_json.acquisition` 缺 `remediation` 键 —— **不属本卡（WC-6/REM-95）范围**

> **判为非目标的理由**：
> 1. **权威规格文本只写列**：REMEDIATION_REGISTER :1718「**WC-6｜REM-95：补救原因持久化至 `locations.error`**」；:1709 REM-95 定义「adapter_dispatch 丢补救原因→locations.error=NULL」。两处均未把 `documents.metadata_json` 列入修法。
> 2. **卡内冻结契约禁止它**：oracle §3 G-2 冻结「整个 dump 唯一允许的字节变化是 P2/P3/P4 的 `locations.error`」；若把 remediation 写进 `acquisition`，`documents.metadata_json`（outcome allowlist 字段）必然变化 ⇒ 与本卡自己的 RED/GREEN 字节证**自相矛盾**，只能另卡。
> 3. **修改面显著更宽**：`group_metadata → collector_name/version/retrieved_at + manifest + documents.metadata_json`（scanner.py:699-708 路径）是载荷/身份面改动；且 `no_sidecar`/`broken_sidecar` 两文档的 `acquisition` 整体为 `null`，要加 `remediation` 就得**凭空造出一个 acquisition 对象**，属 schema/行为变更，远超「诊断列」。
> 4. **可观测性已达成**：修复后读者经 `service.query() → document.locations[].error` 已能看到原因（我 R4 实测 H4 命中），`acquisition` 键不是达成 REM-95 目标的必要条件。
>
> **反例（何时它才算本卡内）**：若 REM-95 规格原文写成「持久化至 `locations.error` **与** `documents.metadata_json.acquisition`」，或 oracle 冻结时把 documents 面列为允许变化项，则它属本卡——**两者都不成立**。
>
> **结论与必办路由**：属 **C1 观察的第二表面，非 REM-95 规格面**。I-07-C 复审原文（reviewer_report:83）本就把它归为「NOT this card's fix surface → route to the REMEDIATION ledger」。**要求**：登记册在处置 REM-95 时**必须显式记下该未覆盖面**（另立一行或在 REM-95 行加注「C1 第二表面未修，另派」），否则违反 owner 原话「发现的缺陷都要全部修复」（§76）而无账可查。若关闭 REM-95 时未记录 → 该条升级为 **P2**。**本卡本身已如实披露**（decision §9、handoff `open_questions` 第 1 条），不计为本卡缺陷。

⇒ 落定：本 pass 只把它记为 **必须路由（P2-2）**；**不改登记行、不改 acquisition 面**。

### 裁② 四桩披露（post-freeze rescan 臂 / 比较器剔 volatile 清单 / mutation1 宿主败 / 同哈希副本删）+ binding harness 哈希并列重录 —— **基本充分，一处实质缺口（P2-1）**

> | 披露 | 复审者的核验 | 充分性 |
> |---|---|---|
> | post-freeze 新增 `rescan` 臂 | decision §7 item9 + handoff `disclosures.rescan_arm_added_after_oracle_freeze`（oracle sha 仍 `f59aa27d…`）+ 四臂 `rescan/` 证据文件俱在 + 我重跑复现 | ✅ 充分（但见 P3-3：该臂的命令 id 不在 commands.json 冻结清单里） |
> | 比较器剔 volatile 清单 | decision §7 item4 列了实测 volatile 键（scan `run_id`、resolve `retrieved_at`、`observed_at`、`*_at/mtime/…`）+ `wc6_common.VOLATILE_MARKERS` 源码 + oracle §4 声明 | ⚠ **不完整**：清单未包含 `"now"` 子串导致的 `known_quarantined` 剔除 ⇒ **P2-1** |
> | mutation1（utf8NoBOM 宿主失败、突变未落盘） | 目录 `evidence/mutation_attempt1_mutation_not_applied/` 存在且各阶段齐全；其 `scan/normalized.json` 诊断与 `green` **逐字节相等**（即「跑的是修复码」这一披露为真） | ✅ 充分（原样保留、未覆盖） |
> | 同哈希副本删除记账 | decision §7 item6 记 sha `0c5ac1a2…`、已删；attempt 根现存恰 6 个声明文件、无游离件 | ✅ 一致（被删文件本体不可再验 → 该单点**未证实**，但与根目录现状不矛盾） |
> | binding harness 哈希并列重录 | 逐个比 10/10 相等（§1.0）；binding 注记保留了首冻值 `wc6_common 2513fda2…/prepare a6da5275…/run_stage 7bf5fdc7…/compare_runs f1d362b0…` | ✅ 充分 |
> | （附）`no_live_family_run` | handoff `disclosures.no_live_family_run=true` + decision §7 item8 给出理由（他 agent 并发跑 live 套件） | ✅ 披露在，但命令表账不平 → P3-2 |

⇒ 落定：**唯一实质缺口 = P2-1**（volatile 清单漏 `known_quarantined`），随卡移交。

---

## 4. REM-95 关闭裁（逐字转录自报告 §3）

**代码态逐跳（行号为 iso-fixed 现值）**：H0 `sidecar.py:5-7` 承诺 → H1 `sidecar.py:60`/`:74` 计算（词表 `_validate_sidecar :90-119`）→ **H1→H2 丢弃缝（本卡修复点）`adapter_dispatch.py:81` `error=item.evidence.get("remediation"),`** → H2 `scanner.py:44-61` `_Candidate.error` → H3 `scanner.py:1096` 全仓唯一 `INSERT INTO locations`，末位 `:1125` `item.error if item.error is not None else candidate.error`（观察错误优先，保 `known_error` 等式闸门 `:740-746` 不被改写）→ H3′ `scanner.py:989-1000` 计数只看 `item.error`、`known_error` 只在异常分支 `:738-746` 计算 → H4 `service.py:653-660/:683` → `document.locations[].error`。

**运行时逐跳**：`reason_chain.py chain_r` rc=0、`all_hops_match=true`，4 探针 × 4 跳全中 oracle 冻结字面（clean→NULL、no_sidecar→`missing_sidecar`、broken_sidecar→`sidecar_parse_failed`、mismatch→`missing_identity:canonical_entity_id;content_hash_mismatch;path_escape:canonical_path`）。

> **关闭裁（原文）**：
> **关闭裁**：REM-95 的丢弃缝（`sidecar → evidence → _Candidate.error → locations.error → service.query`）**已确实关闭**，四跳在我自己的执行中逐跳命中 oracle 冻结字面，且 outcome 面逐字节不变（§1.2 R13）。
>
> **但「关闭登记行」的措辞有前置条件**：
> 1. 依 REMEDIATION_REGISTER 第 4 行纪律「每项修复走九步协议（隔离副本+冻结 oracle+独立复核+**零生产合并**）；生产晋升仍是独立 owner 决定」，本卡已满足卡片级修复与独立复核，**但 live CW 仍为 pre-image（我现场哈希 `6a72e7c5…`/`f039d5f8…` 未变）⇒ 生产缺陷仍在**。
> 2. 因此我的建议处置：REM-95 = **「已修待晋升（FIXED-verified / 复审通过，pending promotion）」**，**不可**记为生产面 CLOSED；晋升 `changes.diff` 到 live CW 是 owner 独立决定（另卡/另授权）。
> 3. 关闭文案必须带上裁①的未覆盖面（C1 第二表面）。

⇒ 落定（`handoff.json > rem95_state`）：**`review_accepted_pending_promotion`** —— 即「复审通过、待晋升」；**不是 `closed`**。
**不可记生产 CLOSED**：复审现场哈希 live 仍 `6a72e7c5…`（adapter_dispatch）/ `f039d5f8…`（scanner），**生产缺陷未修**；**晋升是 owner 独立决定**（`promotion_is_owner_decision = true`）。

---

## 5. 幂等永拒裁（逐字转录自报告 §4）

> **判断：足以拒绝（针对该方案本身），但「永久」有边界。**
>
> **支持拒绝的三条独立证据（我实测/实读）**
> 1. **静态路径穷尽**：全仓唯一 `INSERT INTO locations` 在 `scanner.py:1096`；计数只在 `:989-1000`（`item.error` 真值时 `errors+1`、`known_error` 假则 `new_errors+1`、append `error_details`），而 `known_error` **只**在异常分支 `:738-746` 计算 ⇒ 若把补救原因放进 `_ObservedFile.error`，则每次扫描 `errors/new_errors/error_details` 都非零，且成功路径永远 `known_error=False` ⇒ **每次 rescan 都把同一条补救记成 NEW error**（计数永不收敛）。这是代码结构上的必然，不是抽样推断。
> 2. **正向幂等实证（我重跑）**：本方案下红/绿双臂首扫与二扫 `diagnostic_identical_across_rescan=true`、`errors=0/new_errors=0/error_details=[]` 完全相同，诊断不抖动。
> 3. **家族旁证**：我两侧 `test_repeated_empty_source_is_a_known_quarantine_and_recovers`、`test_scan_is_idempotent_and_tombstones_missing_locations…`、`test_scan_deduplicates…` 等 quarantine/幂等用例 **pre/post 同为 passed** ⇒ 观察错误的等式闸门与既有隔离语义未被本修复触碰。
>
> **边界（「永久」的适用范围）**
> - **被拒的是「把补救原因写进 `_ObservedFile.error`」这一具体方案**，在当前 `scanner.py` 结构下（计数路径与 `known_error` 计算位置不变）。它**不排斥**未来能保持 fail-closed 计数不变的设计（独立诊断列/表；或让 `_observe_file` 在成功路径也做等式读回的 remediation-aware 闸门）——那些必须**重跑本套幂等+fail-closed 组合证**再谈。
> - **实证覆盖的缺口**：四臂探针里**没有任何一个带观察错误**（四臂 `errors` 全 0），所以三元表达式「观察错误优先」那一支（`item.error is not None`）**未被本卡探针直接触发**；它只由家族里 quarantine 用例与代码阅读支撑。这是该永拒结论的证据边界，须如实记账。
> - 幂等双臂证据本身受 P2-1 影响：`known_quarantined` 未被比较器比较；我用**原始 report_json** 独立补上了这一格（四臂皆 0、原始报告除时间/id 外全等），故结论不依赖被污染的那一格。
>
> **结论**：可以据此外加代码结构论证，**在本卡语境下永久拒绝 `_ObservedFile.error` 方案**；拒绝理由应记为「(i) 计数/闸门结构必然性 + (ii) 本方案幂等双臂实证 + (iii) 家族幂等用例两侧同」，并注明上面两条边界。

⇒ 落定：**足以拒绝 `_ObservedFile.error` 方案**（静态路径穷尽 + 双臂幂等实证 + 家族 quarantine/幂等用例两侧同）；**边界必须随行携带**：仅拒该方案于当前 scanner 结构；四臂无带观察错误的探针（`errors` 全 0），三元「观察错误优先」支只由家族用例 + 代码读支撑。

---

## 6. 未验证项清单（报告 §7 逐条转录）+ 边界声明

### 6.1 未能重跑 / 未证实项（报告 §7，共 6 条，逐条）

1. **`fam_live_before`（live CW 只读见证跑）——未重跑**：实现者亦未执行（P3-2）；我判断在本会话对 live CW 跑整套家族有让测试写生产树的风险（且沙箱会对 tmp_path 全线报错），故**只做字节核验**：`source_pins_before.json` 证明修前 iso==live（503 件全等），因此 pre-fix 的 iso 家族结果可代表 live 字节面；但「live 树上跑」这一命令本身**未证实**。
2. **mutation 臂实现者原突变文件字节（decision §5 所记 `b9460305…`）——未证实**：突变注入后已按恢复流程覆盖，其字节不可复现；我用自己的突变字节（`ec8d22be…`，occurrences=1）复现了**语义**（诊断回 NULL、outcome 不变）。
3. **「同哈希副本已删」的被删文件本体——未证实**（已删即不可再验）；仅能证实现根目录无游离件。
4. **登记册钉时字节 `f8cd3ac4…` ——不可复现**（登记册被计划层后续追加）；REM-95 规格行文本与行号未变，我按现行文本裁。
5. **绝对家族基线 443P/23F —— 跨会话未复现**（我的环境 427P/39F，18 条环境敏感差异）；**同树前==后等式已复现（rc 0）**，故卡契约成立，绝对计数只在各自会话内有意义。
6. 前两次家族重跑（`fam_rerun`/`fam_rerun2`）**作废**（环境 PermissionError 338/474），已如实记于 §1.5；其输出只存在于 scratch（临时目录），非本 attempt 证据。

### 6.2 边界声明

**（a）复审者自己的边界核验（报告 §5，转录）**

| 边界 | 复审者实测 | 结论 |
|---|---|---|
| live CW 503 件 manifest 前后同（`41c2271d…`） | 既有 before/after 证据均 `41c2271dbaf26bcf2f564d48eb0705e467bbf7b2dc05f85f914fdcced047d739`、`live_key_sources_drifted_vs_before=[]`；他自己又跑了一次 `pin_sources.py after`（rc 0）得到同一 manifest 与空漂移 | ✅ 零产写 |
| 生产树零写 | `git diff HEAD --name-only -- . ":(exclude).planning"` = **0 行（count=0，rc 0）**；attempt 内既有文件 mtime 全部早于复审时刻 | ✅ |
| 60 文件家族面 0 新增 skip/xfail | `family_files.json file_count=60`；前后两侧 skipped 均为同一 8 条 id；`changes.diff` 中 `skip\|xfail` 命中 0、测试文件命中 0 | ✅ |
| family「同树前==后」 | `compare_family fam_rerun_pre fam_rerun3` **rc 0、status_changed=[]** | ✅（跨会话绝对计数不可复现，见 §1.5） |
| 既有证据链未被改动 | attempt 最新 mtime = 06:18:32（handoff）；复审只新增 2 个文件 | ✅ |
| 登记册钉哈希 | 现值 `33c7505e…` ≠ binding 钉 `f8cd3ac4…`（270337 vs 223551 B）；REM-95 相关行 :1502/:1709/:1718/:1739 文本与行号未变 | ⚠ 计划层并发追加，**钉时字节不可复现**（环境事实，非本卡改动） |
| 无 git 变更操作 / 无网络 | 仅 `git diff HEAD --name-only`（只读）；未联网 | ✅ |

复审者另披露的环境偏差（报告 §0.5，转录）：本会话文件沙箱下 pytest 以 `mode=0o700` 创建的目录立即对创建者自身不可访问，导致家族重跑前两次（`fam_rerun`、`fam_rerun2`：338/474 ERROR at setup）作废；加 scratch `sitecustomize.py` mkdir-mode 垫片（PYTHONPATH 注入，不改产品、不改测试树）后才完成家族重跑。该偏差**双向对称**（pre/post 两侧同一环境），故不破坏「前==后」可比性。

**（b）本 carrier-landing pass 自身的边界（本 pass 实测/声明）**

- **写入面 = 仅本 attempt 目录**：本 pass 只写 3 个文件 —— `review.md`（新建）、`handoff.json`（status 面改写）、`evidence/WC-6-ADAPTER-DISPATCH/qualification.json`（新建）。**未写** `REMEDIATION_REGISTER.md` / `progress.md` / `findings.md` / `task_plan.md` / `OWNER_DECISIONS.md`；未改 `.planning` 之外任何产品文件；**无 git 写操作**；**未联网**；**未跑测试**。
- **复审报告只读**：`reviewer_report.md`（33362 B / `661e833c…7c4cb`）与 `reviewer_report.sha256`（85 B）落定前后字节不变；既有 carrier（`oracle.md`/`binding.json`/`commands.json`/`decision.md`/`changes.diff`/`harness/**`/实现者 `handoff.json`@06:18:32 的既有裁决字节）一律只读，`handoff.json` 仅在 status 面改写，前像 sha256+字节已记（`87f87e7b4868ac4ad2bf145b91fb3630d3b3da42f91498ef64af6c184dc4ed7b` / **13238 B**），前像文本以 `status_authority.pre_verdict_authority` 与 `status_historical_pre_verdict` / `reviewer_status_historical_pre_verdict` 保留。
- **不自签**：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`。
- **落定核验**：`git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` 计数 = **0**（本 pass 写入 `handoff.json` 之后实测；`review.md`/`qualification.json` 均在 `.planning` 内，全部写完后复测仍为 0，最终值随本 pass 结果报告一并交父）。
- **不做**：不写五份计划文件；不改 `reviewer_report*`；不改 REM-95 登记行（登记册归父）；不碰其他卡；不改任何 status 之外的既有裁决字节；不产生新裁决。

---

## 7. 落定清单

| 文件 | 状态 |
|---|---|
| `review.md` | 本文件，**新建**（创建前本 attempt 无 `review.md`） |
| `handoff.json` | `status: review_pending → accepted_scoped` + 新增 `status_before` / `status_transition` / `status_rounds` / `status_history` / 重写 `status_authority`（carrier 钉 + 前像保留）/ 更新 `reviewer_status` / 新增 `carried_findings` / `unverified` / `rem95_state` / `promotion_is_owner_decision`；JSON 写后 `json.load` 重解析 |
| `evidence/WC-6-ADAPTER-DISPATCH/qualification.json` | **新建**：`formula = not_applicable_with_reason`、`disclosure_adaptation = unmapped`、`accuracy = unproven`、`granted_scope` / `not_granted`、`verdict_is_transcribed_not_authored = true`、`status_authority` 镜像、`carried_findings` 镜像 |

**REM-95 状态（随卡携带）**：`FIXED-pending-review` → **`review_accepted_pending_promotion`（复审通过、待晋升）**；**不可记生产 CLOSED**；晋升 = owner 独立决定。
