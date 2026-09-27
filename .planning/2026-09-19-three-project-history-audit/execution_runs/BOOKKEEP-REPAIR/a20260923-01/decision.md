# BOOKKEEP-REPAIR / a20260923-01 — decision.md（逐项映射 + 原值留痕证明 + 注记准文 + register 折入块）

- CARD：BOOKKEEP-REPAIR（记录级修复，零产品代码）；PLAN = `.planning/2026-09-19-three-project-history-audit`；父 session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`。
- 范围：22 项（原 9 + 扩 5〔#10–14〕+ 2〔#15–16〕+ BL-2/#18〔#17–18〕+ 2〔#19–20〕+ 2〔#21–22〕），全部落点=计划记录文件（PWF 三文档、登记册行内注记、attempt 簿记件），execution_v2 冻结件与 reviewer 载体 0 字节。
- 通则：**append-style + 原值留痕**；本文件自称结论域=「2026-09-23 盘上字节 + 本卡 commands.json 所列命令实测输出」；未外推至产品质量、预测准确性、真实 provider 行为或任何 NOT GRANTED 资格。本 pass **零 git 命令**、零产品写、零自签。

## §1 逐项映射总表（22 项）

| # | 项（来源） | 动作落点 | after-state 判定 | 原值留痕 |
|---|---|---|---|---|
| 1 | PWF 同步缺口（GOAL ⑤） | findings.md 尾部 2026-09-23 节（I-07-C 含 holdout 双结果 + I-09-C 条）；task_plan.md 尾部 2026-09-23 节（DW15-prune-repair 正名 + I-07-C 卡号） | ✅ 两节在盘；DW15-prune-repair/I-07-C/I-09-C 可检索 | 既有行 0 改动（纯尾部追加） |
| 2 | REM-79 四行补域（AUDIT-DESIGN R1a/§8、REM-94） | task_plan.md:1630、findings.md:633、findings.md:684、progress.md:1060 行内域限定 | ✅ checker rc=0 | 行内追加、原文逐字保留（限定词后缀式） |
| 18 | progress.md:1060 计数限定（INTEGRITY F7） | 并入 #2：「全＝该段所列 4 类余项，N=4」 | ✅ 带实数计数 | 同上 |
| 2b | checker「four files」面（本 pass 补齐） | REMEDIATION_REGISTER.md 同类 7 行（155/411/1092/1192/1202/1560/1605 附近）行内域限定 | ✅ **checker 对 4 文件（task_plan/findings/progress/register）= 0 violations, rc=0** | 行内追加；披露：register 7 行=checker 实扫出的同族实例（超出派单 4 行、按 owner「每一个都要修复」一并修） |
| 3 | I-14-F-R1 review.md stub 双口径（D4） | `I-14-F-R1/a20260922-01/review.md` 落地式翻转（status→`accepted_scoped` + status_authority 转录块 + `verdict_is_transcribed_not_authored:true` + 载体钉） | ✅ 头行状态=accepted_scoped | 原文全文 6029 B 逐字节留存：兄弟件 `review_stanb_stub_historical_20260923.md`（sha `7f180899…`）+ 新 review.md 内 `review_stanb_stub_historical` 字段逐字注入（python 验证 byte-equal=True） |
| 4 | B1-I08C review.md 槽（D4） | 新建 `B1-I08C-product-fixes/a20260921-01/review.md`（转录 `accepted_with_conditions` + §9 条件 + 词汇映射注记 + 双钉） | ✅ 槽位落定 | 新建件；既有件 0 字节 |
| 7 | B1 原卡回填（DEV-2.2） | 同 attempt（与 #4 收敛）：`handoff.json` status `review_pending→accepted_with_conditions` + `status_before_bookkeeping_fix`/`status_authority`/`status_semantic_mapping`/`status_flip_bookkeeping` 字段 | ✅ JSON 重解析通过 | 原 `note_on_status` 值逐字保留在 `note_on_status_historical_pre_verdict`；其余键值 0 改动 |
| 5 | 验收词词汇映射（D4 全局） | 本文件 §2 映射表 + §6 折入块 | ✅ 8 处超界+8 自查补全形全映射 | 追加式 |
| 6 | I-14-D r2-r5 补 pin（GOAL ⑤ 面5） | `<ATTEMPT>/i14d_report_pins.json`（r2–r5 全值钉、post-hoc 声明） | ✅ 4/4 钉在 | 载体 0 字节（retro-pin=测今钉） |
| 8 | D8 提交信息欠复述 | 本文件 §3 注记（commit 不可变=注记式）+ §6 折入块 | ✅ | 追加式 |
| 9 | 「注册时点版本」限定（FAB-1 残留） | REMEDIATION_REGISTER.md 五引用行（§72/§74/§75/§77/§78）行内三元组注记 `(sha256, 版本域, 留存位)` | ✅ 5/5 | 行内追加；RESPONSES.md 已有勘误=0 触碰；README.md 无引用命中=0 触碰 |
| 10 | B5 binding 失配（D7） | 新建 `B5-fix-g1a-g3/a20260922-01/binding_erratum_20260923.md` | ✅ 两哈希全值+现值复算+归因 | 原 binding.json/自报件 0 字节 |
| 11 | _provenance.json:75 陈旧字节（D12） | `outward_requests/_provenance.json` 尾部新键 `errata_2026_09_23` | ✅ JSON 解析通过 | 原行 7087 B 字面保留 |
| 12 | 批 8/9 门记录（DEV-2.1） | 本文件 §4 正式门记录行（register 形式）+ §6 折入块 | ✅ 两行齐 | 追加式（补账转正式，时点如实） |
| 13 | D6 冻结次序注记 | 本文件 §5 准文（供 RF-RATCHET-FIX/REST-A 两卡 review 引用；两卡未动） | ✅ 准文在 | 追加式 |
| 14 | D10 意外真实下载 | 本文件 §5 注记行（引用 `E2E-EXPAND/a20260923-01/evidence/accidental_auto_gate_run/`，存在性已核） | ✅ | 追加式 |
| 15 | D1b 证据件缺失（最高项） | 新建 `B1-I08C-product-fixes/a20260921-01/evidence_erratum_20260923.md` | ✅ 勘误+实测搜证 3+1 方法 | **未创建 production_anchors.txt**（铁律遵守）；commands.json 0 字节 |
| 16 | D1c 族 4 小项 | 本文件 §5「D1c 族注记表」+ §6 折入块 | ✅ 4 行 | 追加式 |
| 17 | BL-2 bind-time 钉漂移 | 本文件 §5 注记行（含三元组格式提示） | ✅ | 追加式 |
| 19 | B5 harness 可重定位性 | 新建 `B5-fix-g1a-g3/a20260922-01/harness_relocatability_erratum.md` + `scripts_fixed/` 两修复版副本 | ✅ 副本 ast.parse 过；输出 argv[1]/env 可重定位 | **原脚本 0 字节**（before=after sha 自证） |
| 20 | I-06-B 历史破门注记 | 本文件 §5 三行 + §6 折入引用 | ✅ | 注记式（历史不可回改） |
| 21 | R5-06 `_review_i14d_r5_20260922/` 未跟踪 | 存在性核验 + 本文件 §5 注记 + 收尾清单 git add 项 | ✅ 30 件在盘 | 注记式；真入库=随下一批（本 pass 零 git） |
| 22 | §八十四 引用规范 | 本文件凡引该节=全称「§八十四 REGISTRY-CLOSURE 处置汇总（42 行/40 mandate 项）」 | ✅ | 撞号规避（双「八十四」其一已改「八十五」） |

## §2 验收词词汇映射表（#5；D4 全局——8 处超界 + 自查补全）

**现值语义映射表（canonical）**：`ACCEPT` ≡ `accepted_scoped`；`ACCEPTED_SCOPED` ≡ `accepted_scoped`（大小写变体）；
`ACCEPT (verified)` ≡ `accepted_scoped(verified)`；`accepted_with_conditions` ≡ `accepted_scoped` + carried_findings（带遗留件）；
`ACCEPT WITH FINDINGS` ≡ `accepted_scoped` + carried_findings；`ACCEPT（条件式）` ≡ `accepted_scoped`（条件=carried/域限定注记随文）；
`ACCEPT — scope-limited` ≡ `accepted_scoped`（带域限定）；`ACCEPT (sign-off as reviewer…)` ≡ `accepted_scoped`；
`ACCEPTED — SCOPED` ≡ `accepted_scoped`；`NOT ACCEPTED AS-IS — measured core verified…` ≡ `changes_required`。
冻结契约 `review_and_handoff.md:15` 四值结论域 = `accepted_scoped / changes_required / blocked / not_applicable_with_reason`——上列词形均为其超界写法，本表只做语义映射、**不回改任何历史 verdict 原词**。

**8 处超界（AUDIT-DESIGN D4 计数域）**：

| # | 词形 | 位置 | 映射 |
|---|---|---|---|
| 1 | `accepted_with_conditions` | `B1-I08C-product-fixes/a20260921-01/reviewer_report.md:16` | accepted_scoped + carried_findings |
| 2 | `ACCEPT`（`**ACCEPT.**` one-line L511） | `B3-I05C-delivery-fixes/a20260921-01/reviewer_report.md` §10（review.md:32 转录） | accepted_scoped |
| 3 | `ACCEPT`（`**Verdict: ACCEPT**`） | `CW-TEST-DEBT/a20260922-01/reviewer_report.md:7/:328`（review.md 转录） | accepted_scoped |
| 4 | `ACCEPT (scoped), with findings F1–F7` | `FIX-W06-GAPS/a20260922-01/reviewer_report.md:11` | accepted_scoped（F1–F7 carried） |
| 5 | `ACCEPT` | `I-02-D/a20260919-01/review.md:5`（「结论：**ACCEPT**」） | accepted_scoped |
| 6 | `ACCEPT（条件式）` | `I-14-H/a20260919-01/review.md:9` | accepted_scoped（条件式=限定随文） |
| 7 | `ACCEPT — scope-limited` | `TTL-30D-POLICY/a20260922-01/review.md:3` | accepted_scoped（域限定） |
| 8 | `ACCEPT (sign-off as reviewer…)` | `RF-E2E-ADAPT/a20260923-01/reviewer_report.md:7`（+L288 复述） | accepted_scoped |

**自查补全形（grep verdict 行全域扫出，D4 句内另列/邻族）**：

| # | 词形 | 位置 | 映射 |
|---|---|---|---|
| 9 | `ACCEPTED_SCOPED`（大写） | `I-07-B/a20260923-01/review.md:3` | accepted_scoped（大小写变体） |
| 10 | `ACCEPT WITH FINDINGS（通过，带 7 条 findings…）` | `I-06-B/a20260922-02/reviewer_report.md:13` | accepted_scoped + carried_findings |
| 11 | `ACCEPT（6 条 findings 全为 INFO…）` | `I-06-B/a20260923-01/reviewer_report.md:14` | accepted_scoped（findings=INFO） |
| 12 | `ACCEPT（条件式，accepted_scoped）` | `I-14-I/a20260919-01/reviewer_report.md:10` | accepted_scoped（自带映射） |
| 13 | `ACCEPTED — SCOPED` | `I-14-F/a20260919-01/reviewer_report.md:10` | accepted_scoped |
| 14 | `ACCEPT (verified)` | `F-EE1-FIX/a20260923-01/reviewer_report.md:9/:317` | accepted_scoped(verified) |
| 15 | `**Verdict: ACCEPT** (scope-limited to the three composed faces…)` | `GUARD-MERGE/a20260922-01/reviewer_report.md` L7–L9 | accepted_scoped（域限定） |
| 16 | `NOT ACCEPTED AS-IS — measured core verified…` | `B5-plan-level-remediation/a20260921-01/review.md:4`（VERDICT BACKFILL 转录） | changes_required |

## §3 D8 注记（#8；commit 不可变=注记式）

`ac4ebd04…`（CW 晋升提交）的提交信息**未复述 I-14-D 随行欠账**：C12 promotion precondition、F-REV-D-02 死 `_VALUE`、F-REV-D-03 atom 缺口。
载体层仍在（`PROMOTION-PREP/a20260922-01/promotion_batch_manifest.md:75` 携带清单、`PROMOTION-EXEC/a20260922-01/review.md:120`
「accepted as carried declarations, not re-verified」，载体 `e13a87d9…`）。**提交信息不可变 ⇒ 本注记即收口形态**：该三欠账随
promotion_batch_manifest 携带口径继续有效，任何引用 `ac4ebd04` 的下游件须连同本注记一并读（scope=注记、非改史）。

## §4 批 8/9 正式门记录行（#12；DEV-2.1 补账转正式——register 形式，格式对齐批 1–3 行式）

| 批 | 窗口（端点=commit） | 提交数 | 门记录 | 判定 |
|---|---|---|---|---|
| 8 | `a31fd7ed..977fa1e8` | 1 | **门 10/10 绿**（2026-09-23 17:18 push log；原始日志存 `execution_runs/PUSH-LOGS-ARCHIVE/a20260923-01/`） | VERIFIED（本行=补账转**正式门记录**；补账时点晚于推送=记录纪律偏差 DEV-2.1 保留计列） |
| 9 | `977fa1e8..b7a6a116` | 1 | **门 10/10 绿**（2026-09-23 19:51 push log；同上归档） | VERIFIED（同上；批 9 暂存滑点=§64 第 11 例已自纠、独立计列） |

## §5 注记准文与族注记（#13/14/16/17/20/21）

### D6 冻结次序准文（#13；供 RF-RATCHET-FIX / RF-RATCHET-REST-A 两卡 review 引用——两卡字节未动）

> **冻结次序偏差 = 补偿核已做**（D6 如实挂账）：`RF-RATCHET-FIX/a20260923-01/oracle.md` §8（L131–139）自披露 oracle 冻结**前**已跑
> verbatim RED（exit 4 保存）+ 两轮 RED 复现 + §3 两轮测量扫描与 CC 表；`RF-RATCHET-REST-A/a20260923-01/ORACLE.md` §2 L24
> 「Card's expected actuals (22 / 17 / 114) re-derived independently ✓」= 冻结前实测数值——对 `START_HERE.md:36` 第 4 步（先冻结）→
> 第 5 步（才运行修改前检查）的次序有偏差。**补偿核**（两卡 review 引此为准文）：①独立于被测对象的双实现复算——REST-A 的
> ast.walk 孪生与被测 `_max_complexity` 对 43 个扫描文件逐文件一致（0 分歧）；②冻结后 judged 重跑与冻结预期逐项相等——FIX 的
> 「binding → judged RED re-run must match §2 exactly」；③raw 全留存（`evidence/red`、`evidence/measure`）。**补偿核做毕 ≠ 次序合规**：
> D6 按已披露偏差挂账（AUDIT-DESIGN 追补 A3「维持」口径一致）。

### D10 意外真实下载注记（#14）

E2E-EXPAND RUN-R2 因测试 argv 漏写 `--live never`，runner 默认 auto gate 探测 cninfo 并**执行一次真实下载**（超出该登记册冻结网络
范围）——已全量披露（`E2E-EXPAND/a20260923-01/commands.json:96/:99` `__history`+`result_run1`「DISCLOSED DEVIATION…EXECUTED one real
download outside this registry's frozen network scope」）、删除证明在案、证据位=`execution_runs/E2E-EXPAND/a20260923-01/evidence/accidental_auto_gate_run/`
（本 pass 存在性核验 ✓）。后续 RUN-R3 由 owner「给你真实下载复测授权」覆盖=**仅覆盖 retest，不追认 RUN-R2 的意外下载**（不追认照录）。

### D1c 族注记表（#16；四行=各卡自陈类低风险）

| # | 项 | 原自陈位置（引文） | 性质 |
|---|---|---|---|
| 1 | B1-PREREQ 名称漂移 | `B1-PREREQ/a20260922-01/oracle.md:137` 引 `evidence/final_integrity_check.txt`，盘上实为 `final_integrity_check.stdout.txt` | 自披露（F-2 名称漂移）；内容在、名不符 |
| 2 | GATE-OQ-FIX 四预登记名合并 | `GATE-OQ-FIX/a20260922-01/oracle.md:122-127` 预登记 `compileall.txt/ast_check.txt/help_smoke.txt/ruff_two_files.txt` → 实际合并为 `ast_compileall_ruff.txt`+`ast_and_help_smoke.txt` | 自披露（handoff F-11「substance of every pre-registered check present」） |
| 3 | CFI14FR1 标签重号 | `CFI14FR1-SAMPLE/a20260922-01/commands.json:53/:78-97` 预登记 `01_with_hook.lastfailed.json`、`03_redirect_probe.*` → 盘上 `00_baseline…/02_rerun…/04_redirect_probe.*` | 自披露（`reviewer_report.md:108`「merely label strings moved」） |
| 4 | B5 POST1 中间像不在盘 | `B5-plan-level-remediation/a20260921-01/reviewer_report.md:255`「The POST1 intermediate image does not exist on disk. `e7cb90fc…`（16 314 B）is a recorded value, not a file I can hash」 | 自披露（F-6）；记录值不可复现=留档不补 |

### BL-2 注记（#17；LOW/预期漂移）

`PROMOTION-EXEC/a20260922-01/binding.json:82` `protected_before_hashes["company-wiki/README.md"]`
= `302bd10b386b4aad425b812edd2cbbf05f4d7d12a28865404172eae2f1858512`（bind-time 前像钉）vs 活件
`fdc75e0a72da96d5c7cad07c702b9c6249a0cdfbd4638a4f7050dcedde2f4dd2`/13877 B（2026-09-23 本 pass 实测=父报值 ✓；CW 工作树 dirty=
artifact_dag/CLAUDE/README 三件预存）= **可变产品文件 bind-time 钉的正常漂移类，非断链**。三元组格式提示（bind-time 钉同式记录）：
`302bd10b…（sha256=302bd10b386b…8512、版本域=bind-time 2026-09-22 前像、留存位=execution_runs/PROMOTION-EXEC/a20260922-01/binding.json:82）`。
（派单写作 `PROMOTION-EXEC/a20260921-01/binding.json:82`——该 attempt 名实际为 `a20260922-01`，以实测为准。）

### I-06-B 历史破门注记（#20；三行）

1. **历史例外已披露**：`I-06-B/a20260919-01` 在 I-06-A blocked 期间（其 handoff 自记 blocked_by 两行原文）被实现并 accepted——当时已披露、在案（AUDIT-GOAL ④ 破门嫌疑 1 例）。
2. **现行链以取代版为准**：`I-06-B/a20260922-02` / `a20260923-01`（W06-1 幂等键在 OPEN-2-A 裁不足后的修复面）。
3. **不可回改历史**：该 acceptance 留档不撤销、不改字；处置形态=注记式记录修。

### R5-06 注记（#21）

`execution_runs/_review_i14d_r5_20260922/`（I-14-D r5 独立复审工作件）**存在 ✓**：`DISPATCH.md` 8473 B + `scratch/` 29 件
（`claims467.py`/`diff45.py`/`hashes.py`/`linediff45.py`/`negative_controls.py`/`rowbyrow.py`/`sweep.py` + r3/r4/r5 世代 oracle/rule 扫描 JSON 各组）。
**pinned 位置**=该目录盘上原位（未另立 pin——载体层引用其产出 `reviewer_report_r5.md`，四轮 pin 见本卡 `i14d_report_pins.json`）；
**未随批入库原因**=批次暂存纪律家族（登记册 §64 第 11 例同族：批 9 暂存滑点自纠后加 `if($active.Count -gt 0){throw}` 硬守卫 ⇒ 在飞期
产物不再随批卷入，本目录属复审工作件、后继无人为其单列 add）——非丢失、盘上完好。**真入库动作=随下一批
`git add execution_runs/_review_i14d_r5_20260922/`**（本 pass 零 git 命令，列入收尾清单交父执行）。
（来源=「§八十四 REGISTRY-CLOSURE 处置汇总（42 行/40 mandate 项）」所转 R5-06 回执；本行按 #22 全称引用规范书写。）

## §6 register 折入块（供父折入 `REMEDIATION_REGISTER.md`——本 pass 对 register 仅做 #2/#9 行内注记，节写入归父）

> 折入目标节：「七十七」节或其后续节（父裁）；行式对齐既有节。

1. **BOOKKEEP-REPAIR 22 项收口行**：PWF 缺口（#1）✅、REM-79 四行+register 同族 7 行补域（#2/18/2b，checker 4 文件 rc=0）✅、
   I-14-F-R1 stub 翻转（#3，stub 6029 B 双留存）✅、B1-I08C review 槽+回填（#4/7，`accepted_with_conditions`≡accepted_scoped+carried
   映射在案）✅、词汇映射 16 形（#5）✅、I-14-D r2-r5 补 pin（#6，post-hoc 声明）✅、D8 注记（#8）✅、三元组注记 5 行（#9）✅、
   B5 binding 勘误（#10）✅、_provenance:75 勘误（#11）✅、批 8/9 正式门记录（#12）✅、D6 准文（#13）✅、D10 不追认（#14）✅、
   D1b 勘误禁补件（#15）✅、D1c 族表 4 行（#16）✅、BL-2 注记（#17）✅、B5 harness 修复版副本（#19，原脚本不动）✅、
   I-06-B 破门注记 3 行（#20）✅、R5-06 注记+收尾 git add 项（#21）✅。
2. **D1c 族注记表** = 本 decision §5 表 4 行（原自陈位置引文在）。
3. **批 8/9 门记录行** = 本 decision §4 表（10/10 门绿、17:18/19:51 push log、PUSH-LOGS-ARCHIVE 归档位）。
4. **D8 注记行** = 本 decision §3（ac4ebd04 提交信息欠复述 I-14-D 三欠账；载体层携带口径继续有效）。
5. **词汇映射行** = 本 decision §2 表（8 处超界+8 自查形→四值 canonical）。
6. **I-06-B 破门三行** = 本 decision §5。
7. **R5-06 行** = 本 decision §5（收尾清单：下一批 `git add execution_runs/_review_i14d_r5_20260922/`）。
8. 引用规范（#22）：本卡凡引 REGISTRY-CLOSURE 汇总节 =「§八十四 REGISTRY-CLOSURE 处置汇总（42 行/40 mandate 项）」全称。

## §7 边界与未授予

`disclosure_adaptation = unmapped`、`accuracy = unproven` 维持；本卡不授予任何验收/晋升/资格；B1-I08C 的 `accepted_with_conditions`
六项 §9 条件**未**关闭（仅状态回填+映射）；门①语义残余（D2）=owner 判断位，随主偏离报告呈；M01–M20 独立验收（D9）=M-T-REVIEW 卡面。

## §8 REM-79 自查记录（本卡自身文书）

checker `1.2.0-correction2` 对本 attempt 文书实跑：**decision.md / oracle.md / recovery.md = 0 violations**；
`README.md` 首跑 1 处（"All fixes…" 散文）→ 已按带域措辞改写归零；`changes.diff` = 12 处命中**全部位于 `-` 侧修前历史行**
（原值留痕转录本体，补域=篡改 before 文本）——按 REM-79 语料转录类裁为**非真阳**并显式登记（见 changes.diff 头注），
原文一字未改。正典面（task_plan/findings/progress/REMEDIATION_REGISTER 四文件）= **rc=0，0 violations**（before/after 双录在 evidence/）。

## F-R erratum (landing)

> Append-only 勘误（carrier landing 周期追加，2026-09-24 凌晨随父 §九十四 折入周期）；本节为唯一更正载体，上文原文一字未改（含 §8/changes.diff 头注的「12」原值留痕）。来源 = 独立复审 `reviewer_report.md`（sha256 `a37feef7980bf6288af810dbc036e1fda7e3dd236e8108cca6f57219795c396c`，20930 B，侧车内容匹配，verdict `accepted_scoped`）§7 carried findings F-R1..F-R6——全为文书级、不阻断收口。

- **F-R1（计数更正 12 → 11）**：本文件 §8 与 `changes.diff` 头注称 changes.diff `-` 侧命中 **12**；实测（复审自跑 + 本卡 `evidence/rem79_selfcheck_attempt.txt` 自录，二者一致）= **11**，命中行 = **L14/29/32/50/56/59/62/65/68/71/74**。**权威计数 = 11**；原文「12」保留不回改（erratum 风格）。裁处性质不受影响：仍为转录类非真阳、`-` 侧全中。
- **F-R2（冻结 oracle 20 项 vs 本决策交付 22 项）**：oracle §1 冻结 **20 项**（原 9 + 扩 5〔#10–14〕+ 2〔#15–16〕+ BL-2/#18〔#17–18〕+ 2〔#19–20〕；22:40:13 后未再追加）；本文件 §1 交付 **22 项**，多出 **#21（R5-06 `_review_i14d_r5_20260922/` 注记 + 收尾 git add 项）** 与 **#22（§八十四 全称引用规范）** —— 两项均为**冻结后追加面（post-freeze scope additions，派单时点晚于 oracle 冻结、未回写 oracle 追加件）**，按 oracle 自定「更正走 append-only 勘误」口径在此登记序差；两项均已落盘且已经本次独立复审（§3-i、§2 逐行读验、§9 收口 22 项含 #21/#22）。
- **F-R3（attempt README 名不符）**：attempt `README.md` 末行列交付为 `binding.md / commands.md / handoff.md`，盘上实件 = `binding.json / commands.json / handoff.json`（同 D1c 名不符族）。**一句更正待随下一批折入 README**；本 landing 写面 = 仅本 erratum + 规定三件，README 字节未动（只读登记）。
- **F-R4（handoff 证据枚举欠 3 件）**：`handoff.json` `deliverables` 原列 evidence 8 件，盘上 `evidence/` = **11 件**，欠列 = **`rem79_before.stderr.txt`（0 B）/ `rem79_after_final2.txt` / `rem79_selfcheck_attempt.txt`** —— 三件在此枚举补列，且本 landing 已将三条补入 `handoff.json` `deliverables`（`f_r4_supplement` 标记）。
- **F-R5（PowerShell `-replace` 数组形披露 → register 行已落）**：文档式 `$t -replace ('pat','rep')` 数组形**静默 no-op** → 以 `[regex]::Replace` 等价复算 **MATCH `73feb0593b44ffeb448bc5f5b1cea9800f4cc9fb59f40ca19e9aae8038c104fa`（37086 B）** + 「37135 bytes」正文 vs `report_pin.json` `bytes_hashed: 37086` 的 **49 B 笔误注记**（以 JSON 钉值为准）。记录面 = 本卡 `commands.json` CMD-BKR-04 + B1 `review.md`「钉法复核注记（诚实披露）」；**register 登记行已由父在本 landing 周期折入**（`REMEDIATION_REGISTER.md` §九十四（parent §94）L1856 行内 F-R 折入行，含本条披露行）——本卡对 register 的权限面不含节写入（§6 头注），故归父折入即告完成。
- **F-R6（register 并发写已披露）**：本卡 after 钉 `5dda68f5…`/210952 B 被父方并发/后续折入超越——复审末测 live `f8cd3ac492c179c7284c891a3c705aca468c563cbcdaebcb2fd53908310aed8f`/223551 B、mtime `2026-09-23 23:40:08` 晚于本卡末写 `23:17:57` = **+12596 B**；**post-fix/并发折入引入的新无界行 = 0**（复审自跑 3 次 checker 全 0/0 rc=0，末次在该折入之后）。披露载体 = binding `concurrent_writer_disclosure`；本 landing 时点 register live = `2e9f3a4041b91cbdc7176891d70ff0113fa197c85dcce67c96cd4701b7756699`/227689 B、mtime `2026-09-23 23:49:54`（父 §九十四 F-R fold 后）。纪律 = **checker-after-every-fold**（复审 §9 建议、父已采纳）：每折一次重跑四文件 checker 并留证，折入不得回退 0/0 态。
