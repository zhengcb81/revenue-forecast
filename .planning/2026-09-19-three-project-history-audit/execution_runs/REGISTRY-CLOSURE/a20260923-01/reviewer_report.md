# REGISTRY-CLOSURE / a20260923-01 — independent reviewer report（独立复核点验报告）

- card：**REGISTRY-CLOSURE**（goal-item③ 残留排干）｜attempt：`execution_runs\REGISTRY-CLOSURE\a20260923-01`
- reviewer role：独立复核（本卡实现者未自签 —— `binding.json:2 implementer_signed=false` 合规；本报告=verdict 载体，签署见 §12）
- 复核方式：read / grep / pwsh（Get-FileHash / Get-ChildItem）+ 只读 git（`show` / `status --porcelain`）+ %TEMP% 内 `git apply` 实验；**零产品写入、零状态性 git、零网络动词**；本报告为其二件产物之一（另一件=`.sha256`）。

## 0. Verdict

**ACCEPTED-SCOPED — 签署（signed），附 2 条非阻断 findings + 3 条 INFO。**

- 42 条处置行 / 40 mandate 项映射、五类 class 计数（16/13/11/2/1）、计数对账（25/24 vs "16"）、登记册 §八十四 汇总节、≥10 行跨五类独立点验——**全部通过**。
- **F-R1（MEDIUM，仅拦 `git apply` 落地路径）**：`changes.diff:20` 首个文件头被写成 `#--- a/…`（注释前缀）⇒ 按原样 `git apply --check` **失败 rc=128**（`patch fragment without header at line 22`）。补丁**内容**本身完全有效（该行改回 `--- ` 后：check rc=0、apply rc=0、py_compile OK ×2、纯注释 PASS）→ 落地前置条件：合并波 `git apply` 前修正该 1 行（或按 commands.md 既有"手插"回退）。
- **F-R2（LOW）**：attempt 自身两处节号记载陈旧（decision 汇总节预览 / handoff carried-5 均写 §七十九），实际入册=§八十四（commands.md:21 正确记 §八十四）。登记册本身正确、heading 恰 1 次、无重号残留（§85/§86 撞号更正在案）。

## 1. Scope（含 owner 事后投票转录 — post-close parent record；**未改卡表任何一行**）

- 本报告**不回改** decision.md 处置表 / 登记册 / 任何封存件；以下为**转录性 scope 注记**。
- **owner 双票（OWNER_DECISIONS §23，:481-486，卡关闭后落笔）**：
  1. **REM-24 = 追认**（owner 原话「1，追认」）：M14 OQ-03 的 **D/E 层按现状签收**、内部冲减**不需要**单独 signed 约定 ⇒ 卡内该行的 **OWNER-BLOCKED 已被外部解除**，REM-24 = CLOSED（owner-ratified）。
  2. **F12 = 记为待修**（owner 原话「2，记为待修」）：冻结 rc 数值域**维持 {0,2} 不改**；实测 rc=120（finalization flush 失败自报）=**记为待修产品缺陷** ⇒ **WC-4-RC120 已激活派出**（flush 失败路径落域内 rc=2+错误文本保留；SA-DEFECT 机制错述随修更正）。
  - 事后者记录于登记册 §八十六(:1741 owner 待票新增 2) / §八十七(:1745-1751 双票落地)。⇒ 卡内 **OWNER-BLOCKED 2 → 0**（关闭后达成）。
- 复核时点卡状态保持原样：`status=review_pending` / unsigned（本报告即签点）。

## 2. 交付物核验（deliverables — 全 7 件 + evidence + 登记册节）

| 项 | 结果 |
|---|---|
| `oracle.md` 冻结 | **PASS**：实测 sha256 = `16e4f2a07873a6a42342c57048ead393dd986660b10b1927e8d78916c44d156f`，与 `oracle.sha256` / `binding.json:6` **逐字节一致**；mtime 22:37:42 早于全部处置产物（changes.diff 22:51 / decision 22:54）⇒ **oracle 先冻后动（freeze-first）成立**。 |
| `binding.json` | PASS：`decision_sha256`、`changes_diff_sha256`、**两目标文件 sha**（r6 树 `2f644994…`、生产 `edcbeccb…`）实测**全 MATCH** ⇒ 目标文件至今字节未动（零源写实证）。 |
| `commands.md` / `recovery.md` / `evidence\`（9 件） | 在；命令日志含失败尝试如实记录（3-strike 内）；recovery 给出复算路径。 |
| `decision.md` 42 行表 | 见 §4/§5。 |
| `changes.diff` | 见 §6（内容 PASS；首头格式 defect = F-R1）。 |
| `handoff.md` | PASS：`status: review_pending`、`implementer_signed=false`、**`disclosure_adaptation: unmapped` + `accuracy: unproven` 缺省清单在**（:5）、unmapped/unproven 声明齐。 |
| 登记册 §八十四 汇总节 | **PASS**：heading `## 八十四、【REGISTRY-CLOSURE 处置汇总…】`（:1655）**恰 1 次**；表体=A/B/C/D/E 压缩版，计数行（:1658）与 decision 完全一致（16/13/11/2/1=42 行标注），WC-1..6 规格、路由汇总、7 条 sweep 新发现均在（:1660-1726）。 |
| INFO（不改判） | `oracle.sha256` 落盘 mtime 22:55:22（与 binding 同批、commands 步骤 20 如实并列记录）——钉 sidecar 晚于内容冻结写出；内容冻结先行已由 mtime+hash 一致性证明。 |

## 3. 独立点验 ≥10 处置行（跨全部五类 — 独立证据，不信任其 dispositions 自证）

| # | 行 / class | 独立证据（本复核实测） |
|---|---|---|
| 1 | **A1 REM-05 / CLOSED-NOW** | changes.diff J1 = **2 hunk 注释插入 × 2 目标**（`#---` 头修正后整补丁 apply rc=0）；**本复核自跑 AST 解析**：r6 树与生产 `_VALUE` assigns=1 / loads=0 → **DEAD 两树一致**；`evidence/rem05_behavior_identity.txt` 20 形态 `all_identical=true` + compile OK（UTF-16 文件已读全文）；纯注释 PASS（+11/−2×2，0 非注释行）。 |
| 2 | **A2 REM-06 / WORK-CARD** | 其 evidence `key_is_credential_context` 实测：`token2/secret2/password2/api_key2=[false,false]`（非凭据键）、形态 `token=AAA token2=BBB → token=<redacted> token2=BBB`（后缀键明文）⇒ WC-1 路由成立。 |
| 3 | **A3 REM-07 / WORK-CARD（劣化=sweep⑥）** | **本复核自跑独立探针**（r6 树 `redact_text`）：`Authorization:\ndoc=17\nstage=summarize` → `Authorization:\n<redacted>` ⇒ **两键全吞**；`I-14-D handoff.json:144` 逐字在案「the narrowing saves stage=summarize」⇒ 陈旧声明在 r6 树为假 **CONFIRMED**。 |
| 4 | **A4 REM-08 / SUPERSEDED** | `I-14-D binding.json:72` 逐字：「r2/F-REV-D-05 correction: …claimed 'one-line tree-pointing change'. **It never did**…」+ conftest `783b1774…/275B` ✓。 |
| 5 | **A5 REM-16 / CLOSED-NOW** | 读 `evidence/rem16_command_runs_registration.txt`（7 目录清单+第 7 `r2-verify-before/` 补登记）；**独立盘核** `I-10-B\...\command_runs\` 实测 **7 个子目录恰含 `r2-verify-before`** ✓。 |
| 6 | **A7 REM-25 / SUPERSEDED** | `OWNER_DECISIONS:365` 原话「**E-1: 150/60**」、`:375` 裁行 `GENERATION_RESERVE=150 ⇒ 阈值 60`、`:400` 复核 in-effect ✓；I-14-F-R1 decision §1-§3 实读：**210/124/86→210/150/60 应用 + docstring 真数字表 + 边界 60/61 双 pin（unit+sweep）** ✓。审计"选择未落"=误判 CONFIRMED。 |
| 7 | **A8 REM-30 / SUPERSEDED** | I-14-F-R1 decision:189-191 逐字「F-5's comment misstatements and unpinned boundary are **fixed directly**…」✓；**生产测试头注在盘**（CW `test_short_basetemp_convention.py:11` "BOUNDARY pair 60/61 pinned…closes I-14-F F-5"、:17 真值 174/154/119/84/82/360/78）+ 用例 :83/:86 **60/61 两半双 pin** ✓。 |
| 8 | **A9 REM-35 / SUPERSEDED** | I-14-I `handoff.json.derived_keys_discharge.discrimination_inside_the_frozen_gate` 现文逐字「**CORRECTED BY THE CARRIER-LANDING PASS** per reviewer finding F-1…**the gate's rc 0 must NOT be read as 'the derivation is gate-proven'**」✓（旧文保留标 SUPERSEDED）。 |
| 9 | **B1/B2 REM-09/10 / CLOSED-NOW** | I-14-I handoff：`reviewer_status=…accepted_scoped… full 14-case gate reaches rc 0 / mismatch_count=0 / accepted_ineligible=0`、`gate_result ok=true case_count=14 runner_rc=0`、`bookkeeping.status_transition review_pending→accepted_scoped` ✓；git `980c9b7a` 实读：「I-14-I complete (14-case gate rc 0, xfail now true pass)」✓。 |
| 10 | **B4 REM-24 / OWNER-BLOCKED（sweep④反向误判）** | M14 `oracle.md:323/334/336/380` 逐字：「**D/E 层是否追认由 owner 决定**」`status: "carried_not_resolved"` ⇒「**本节只登记，不代裁**」「未裁、不代裁」✓ ⇒ 登记落地 ≠ 追认，owner 位改判 **CONFIRMED**（最危险一类的反向误判属实；其后 §23 已追认=外部解除，见 §1）。 |
| 11 | **B10 REM-78 / CLOSED-NOW（机制化）** | `REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py` **在盘存在**；register:760/:827/:837 三处实记 v1.2.0-correction2 + 常规自检路径 ✓；`:353` REM-78「仍欠机制化」=陈旧行文、`:352` REM-79「✅已实际使用（old∖new 与 new∖old 双差集，结论异于 r5）」逐行实读 ✓；`:436`（原 :435）「**REM-79**（带域断言机制化）」= **误标实证**（带域断言=REM-78 行文本 :331）⇒ D1 消歧注记有据。 |
| 12 | **C16 F12 / WORK-CARD+OWNER 双轨** | SA-DEFECT:165 逐字「F12（断管归一化）\| **断言在返回后开火**」vs I-09-C `handoff:54` 逐字「rc=120 … **CPython stdio flush failure at finalization**…stderr 'Exception ignored on flushing sys.stdout: OSError [Errno 22]'」+ `pipe_controls.json` A=0/B=120/C=0 + reviewer_report:46 `probe_f12.py:65` C.stderr 误标 ✓ ⇒ 机制勘误（sweep⑦）与双轨路由 **CONFIRMED**。 |
| 13 | **C10a R5-03 / CLOSED-NOW** | `reviewer_report_r5.md:471-481` 复审给定唯一读法逐字（"the breaks and the indentation that follows them are consumed…"）与 J2 替换文逐字吻合；`evidence/r503_patch_production.diff` 在 ✓；apply 后该 4 行纯注释、compile OK ✓。 |
| 14 | **D1/D2 / CLOSED-NOW + WC-5** | 同第 11 条行证据；WC-5 规格在 decision:96-97 + register:1717 ✓。 |
| 15 | **E1 REM-95 / WORK-CARD（WC-6）** | register:1312 C1(F-REV-1) 逐字与 decision E1 吻合（`_to_scanner_candidate` 丢补救原因→`locations.error=NULL`）；**WC-6 规格在**（decision:99-100 + register:1718）✓。 |
| 16 | **E2 REM-96 / EXTERNAL-BLOCKED** | register:1307 holdout 实测「criterion-(i) 合格 ∩ https-source_url-capable = **0**」（10,596 件）+ :1313 **F-REV-7 register 行**（=REM-96 文本源）✓；数据轨=外部依赖，路由成立 ✓。 |

**覆盖**：CLOSED-NOW ×5 行、SUPERSEDED ×4 行、WORK-CARD ×4 行、OWNER-BLOCKED ×2 行、EXTERNAL-BLOCKED ×1 行 = **16 行 ≥10，五类全覆盖**。

## 4. 计数对账（F2 — CONFIRMED，未信其自述）

- **SA-DEFECT 版**（`report_SA-DEFECT.md:185`）：「16（F-REV-D-02/03/04/05、REM-62、R3-02/03/05/06-10、R5-03…08、REM-17/18/24、I-04-C E1/E2、F12）」逐项展平 = **4+1+3+5+6+3+2+1 = 25 单元**。
- **AUDIT-GOAL 版**（`audit_report.md:168`）：同串**无 REM-62** = **24 单元**。
- 两版自称 "16" **与任一实枚举都不符**；两版差 = 恰好 REM-62（1）⇒ 25 vs 24 ✓ 与卡述一致。
- 卡"全部 25 单元逐一处置"复算：C 组 **17 条处置行**（C5/C6/C9a-e/C10a-f/C12/C14/C15/C16）+ **8 条交叉引用单元**（C1-C4=4、C7、C8、C11、C13）= **25** ✓。

## 5. 42=40 映射（CONFIRMED — 无静默丢行）

- **decision 表实测 45 行表格行 − 3 非处置行（`C1–C4` 交叉引用行、`C9`/`C10` 组头行）= 42 条处置行** ✓（ids 全列：A1-A9,A10①,A10③ | B1-B10 | C5,C6,C9a-e,C10a-f,C12,C14,C15,C16 | D1,D2 | E1,E2）。
- **40 mandate 项 → 42 行**：A 组 10 项→11 行（**A10 拆①③** ✓）、B 组 10 项（REM-79 对照行归入 D2）、C 组 16 项→17 处置行（C9/C10 展开为逐 ID 行；C1-C4/C7/C8/C11/C13 交叉引用不另计 ✓）、D 1+1、E 2→2；**无任何 oracle 项缺位**（A1-A10/B1-B10/C1-C16/D/E 全部映射核过）。
- class 标签和 = 16+13+11+2+1 = **43 = 42 行 + 1**：差额恰为 **C16/F12 一行双 class**（WORK-CARD+OWNER-BLOCKED 同格）——见 F-R3。
- 登记册 §八十四:1658 计数行与 decision/handoff **三处一致**（16/13/11/2/1）。

## 6. changes.diff 实验（%TEMP%，独立于其自证）

- 结构：**4 hunk = 2 注释级修复 × 2 目标**（J1=REM-05 注释插入 ×2；J2=F-REV-R5-03 改写 ×2）✓ 与头注一致。
- **纯注释证明**：对两目标把 apply 结果与原文件 difflib 对比 → 每目标 **+11/−2，added_non_comment=0、removed_non_comment=0 → COMMENT-ONLY PASS**；apply 后 **py_compile OK ×2**。
- **`git apply --check`（原样）= FAIL rc=128**：`error: patch fragment without header at line 22: @@ -284,6 +284,15 @@` —— 根因 `changes.diff:20 = "#--- a/iso/…"`（首文件头带注释前缀；:39/:58/:72 三个头均为裸 `--- ` 正常）→ **F-R1**。
- **单行修正后（`#--- `→`--- `，恰 1 处替换）**：`--check rc=0` → `apply rc=0` → `py_compile OK ×2`，%TEMP% 镜像内完成（`%TEMP%\rc_a20260923_01_apply*`）。⇒ 补丁内容有效、锚点在位、行为面零变；**落地时先修该头行**。
- **零源/封存写**：两目标 sha 与 binding 冻结值 **仍 MATCH**（§2）；其 evidence/iso 副本仅在本 attempt 目录内（允许写域）。
- **porcelain**：`company-wiki` = 恰 3 个既有用户改动（CLAUDE.md/README.md/artifact_dag.py，与 I-14-F-R1 复审记录同）⇒ **本卡 0 产品写入**；`revenue-forecast` 122 条中本卡可归因 = 仅 `?? .planning/…/REGISTRY-CLOSURE/`（自身允许写域），**无任何产品源/封存载体改动**；非 .planning 的 2 条（`.tmp-r41-mutation/`、`plan_inputs.json.bak`）属并发他卡，与本卡无关。

## 7. 其 sweep 7 条抽验（spot 5/7）

- **①REM-25 ②REM-30 ③REM-35 三例 stale-OPEN 误判**：全部 CONFIRMED（§3 第 6/7/8 行——审计判 OPEN/"无下文"时，owner 裁决/直修/措辞更正均已在盘）。
- **④REM-24 反向误判（最危险类）**：CONFIRMED（§3 第 10 行逐字）。
- **⑥REM-07 劣化**：CONFIRMED（§3 第 3 行——本复核独立探针两键全吞 + handoff:144 陈旧句逐字）。
- **⑦SA-DEFECT F12 机制错述**：CONFIRMED（§3 第 12 行——SA-DEFECT:165 原措辞 vs I-09-C:54 机制原文）。
- ⑤（REM-08/18/62/16 过期状态读）：抽 REM-08 即 CONFIRMED（§3 第 4 行）；其余随各行证据在册。
- ⇒ 7/7 抽中 6 条 CONFIRMED（唯一未逐字复算者：REM-18 的 4/4 前缀尺寸数列，见 §9）。

## 8. Findings（本复核新出）

| ID | 级 | 内容 | 处置建议 |
|---|---|---|---|
| **F-R1** | **MEDIUM**（拦 `git apply` 路径，不拦判定） | `changes.diff:20` 首文件头 = `#--- a/…` ⇒ 原样 `git apply --check` rc=128。内容已证完全有效（单行修正后 check/apply 双 rc=0 + compile OK×2 + 纯注释 PASS）。 | 合并波落地**前置**：应用前把该行改回 `--- `（或走 commands.md 既有"手插"回退）；作为 J1 落地清单第一条。 |
| **F-R2** | LOW | 节号记载陈旧：`decision.md:120` 汇总节预览 heading 写 `## 七十九、…`、`handoff.md:30` carried-5 写「登记册本节号=七十九」；**实际入册=§八十四**（`commands.md:21` 正确记 八十四；§79 已被父占用）。handoff 该句按终态为假。 | 汇总节/交接勘误注记一行（append-only）；登记册本体无须动（§85/§86 撞号更正在案、heading 恰 1 次）。 |
| **F-R3** | INFO | 42 的成因表述：decision:5 写「A10 拆①③、F12 拆双轨」，但**物理行上 F12/C16 是单行双 class**（class 标签和 43 = 行 42 + 1）；行数 42 与无丢项均实证成立，仅成因句与物理行形不完全同构。 | 无需改表；下游按"行 42 / class 标签 43（F12 双计）"读。 |
| **F-R4** | INFO | 行号引用漂移：oracle/decision 引 `register:1311/1312`（REM-95/96），复核时点实测在 :1312/:1313（+1，父侧并发追加所致）；`register_sha256_at_freeze=468dc316…` 因 append-only 已不可事后重算（设计如此）。 | 下游引用以行文本为锚（父 §75 纪律已同此）；无动作。 |
| **F-R5** | INFO | `oracle.sha256` sidecar mtime 22:55（末批与 binding 同写，commands:20 如实记录），晚于内容冻结 22:37；内容冻结先行由 mtime+hash 一致证明。 | 无动作（下卡可同批钉，惯例提示）。 |

## 9. Unverified（明示不核/未核，不作通过依据）

1. **REM-18 的 4/4 前缀尺寸数列**（M05 14790→18889 等）未重测——其 `E1E7-ERRATA-LANDING accepted` 结论采信 register/复审在案记录。
2. **`register_sha256_at_freeze`（468dc316…）** 无法事后重算（登记册 append-only 已推进 + 父侧并发追加）——**不可复验-by-design**，非缺陷。
3. **REM-21（B3）/ REM-56/59/60/61（B5-B8）/ REM-62（C5）/ REM-64（B9）/ C9d audit §10 族核 / REM-67③ "N5f–N5w/R7a-R7d 全非该形"枚举 / REM-06 "95 行 rule table"计数**：未逐字复算（类外抽验已 ≥16 行）；其证据指针在 decision 行内可循，**双审计清单外的其余载体证据以盘上为准**（handoff carried 已同此声明）。
4. **C6 "review.md `overall PASS` 0 命中"** 未重 grep（该行为 CLOSED-NOW 带披露，披露原文已在 decision 行内）。
5. 历史 attempt 内脚本一律未执行（recovery.md:14 自设纪律，本复核遵守）——REM-78 的"五轮实战自扫"细节采信 register 记载（工具存在+词表迭代表已核）。

## 10. Boundary attestation（边界自证）

- **零网络动词**：commands.md 全日志仅 read/grep/hash/difflib/`git diff --no-index`（只读，弃用原因如实记）；本复核同样零网络。
- **零状态性 git**：卡仅 `git diff --no-index`（读）；本复核用 `git show`/`git status --porcelain`（读）与 `%TEMP%` 内 `git apply`（临时镜像，仓外）。**两仓 HEAD/索引未动。**
- **attempt 自洽**：F-R2 为唯一内部记载不一致（预览/交接 vs 终态节号）；其余 oracle↔binding↔decision↔handoff↔登记册 哈希/计数/class 全互洽。
- **handoff 缺省清单在**：`disclosure_adaptation: unmapped` / `accuracy: unproven` / `verdict_authority: 待独立 reviewer` ✓。
- **永不自签**：实现者 `implementer_signed=false` 未被触碰；本签署为独立复核方（非实现者）。

## 11. Scope-if-accepting（接受后范围携带 — 转录）

- **42 行处置表**已按原样转录入登记册 §八十四（唯一行级回填；历史行零改）。
- **owner 路由项终态**：REM-24 = **closed by OWNER_DECISIONS §23（追认）**；F12 数值域 = **已裁（{0,2} 维持、rc=120 待修）→ WC-4 running（WC-4-RC120 已派）**；卡内 OWNER-BLOCKED 2→0 为**关闭后**外部达成（§1 转录，不回改卡表）。
- **WC-1..6 路由**（register §86:1739 + §87）：**WC-1 已派**（I-14-D-R8，d28ac9ef）、**WC-6 已派**（REM-95-ADAPTER-DISPATCH，9d8cb419）、**WC-4 已派**（owner 票后激活；原 owner-gated=现已解除）；**WC-2/WC-3/WC-5 排队待槽**（规格随取于本卡 decision）。
- **BOOKKEEP +2 已落**：① R5-06 note（`_review_i14d_r5_20260922/` 补入 git → BOOKKEEP-REPAIR 同批）；② REF §八十四 **full-name 交叉引用**（引用带节标题消歧，沿 §35 纪律）。
- **J1/J2 hunk = 合并波清单**：J1（REM-05 注释 ×2 目标）+ J2（R5-03 唯一读法改写 ×2 目标），**落地前置=F-R1 头行修正**；落用前独立复核（handoff carried-2 已同此）。

## 12. 签署（signature）

- **Verdict：ACCEPTED-SCOPED（signed）** —— 2026-09-23；生效条件：F-R1 随合并波修正、F-R2 随汇总节勘误注记（均非阻断）。
- signer：**独立 reviewer**（父会话 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 委派）；**实现者未自签保持**（`implementer_signed=false`）。
- 本报告 + `reviewer_report.sha256` 为本卡仅有的 reviewer 侧产物；未写任何其它文件。

### REM-79 常设自检（tools/check_domain_assertions.py，PYTHONIOENCODING=utf-8）

- 命令：`PYTHONIOENCODING=utf-8 python <REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py> reviewer_report.md`
- 结果（对本文件最终字节，签署前运行）：**`0 violation(s) across 1 file(s)`，exit rc=0 — PASS。**
