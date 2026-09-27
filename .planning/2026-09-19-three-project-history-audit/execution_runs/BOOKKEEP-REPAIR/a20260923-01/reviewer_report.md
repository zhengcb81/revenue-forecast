# BOOKKEEP-REPAIR / a20260923-01 — reviewer_report.md（独立复审）

- Card / attempt：**BOOKKEEP-REPAIR**（记录级修复，22 项，零产品代码）/ `execution_runs/BOOKKEEP-REPAIR/a20260923-01`
- Reviewer：**独立复核（delegated reviewer subagent，父派 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`）**；复审时点 2026-09-23（本地）
- 复审方法：只读（read/grep/pwsh + 只读 `git status`/`git show`）；本报告是本次复审写出的 2 件文件之一（`reviewer_report.md` + `.sha256` 侧车），余处零写入
- 实现方状态：`handoff.status = review_pending`、`implementer_signed = false`、`implementer_self_acceptance = false` —— **实现方从不自签，验收权在本报告**

## 0. VERDICT

**`ACCEPTED_SCOPED`（= accepted_scoped；带下列 findings 与限定，carried 见 §7）**

- 结论词按冻结契约四值域（`review_and_handoff.md:15`）给为 `accepted_scoped`；本卡自己的词汇映射表（decision §2）中 `accepted_with_conditions ≡ accepted_scoped + carried_findings` 同族。
- 授予域＝**本卡 22 项记录级修复的簿记收口**（域＝2026-09-23 盘上字节 + 本卡 commands.json 所列命令 + 本次复审自跑输出）。**未授予**：任何产品质量判定、晋升、`disclosure_adaptation` 仍 `= unmapped`、`accuracy` 仍 `= unproven`、B1-I08C §9 六条件的关闭、D2/D3/D7/D9 的实体裁决。
- Headline gate（REM-79 四文件 after 态）：**本次复审自跑 = 0 violations / rc=0**（域＝task_plan.md、findings.md、progress.md、REMEDIATION_REGISTER.md 四件，2026-09-23 复审时点）—— 见 §2。

## 1. 交付面与冻结次序（live re-hash）

| 检查 | 结果 |
|---|---|
| 交付件齐备 | `oracle.md`/`binding.json`/`commands.json`/`decision.md`/`changes.diff`/`handoff.json`/`recovery.md`/`i14d_report_pins.json`/`evidence/`（11 件）/attempt `README.md` —— 10/10 面在盘 ✓ |
| oracle 先冻结 | oracle `2026-09-23 22:40:13`；修复写面 mtime 依次 `22:43:39`（progress）→`22:47`（findings/task_plan）→`22:55`（I-14-F-R1 review）→`22:56`（B1 review+handoff）→`23:02`（_provenance）→`23:04+`（各 erratum）—— **0 件修复写早于冻结时点** ✓；before 测量（22:22）先于冻结、其值录于 oracle §0，序=测量→冻结→修复 ✓ |
| binding 三向一致 | oracle §0 before 值 == binding `before_sha256` == recovery.md §1 == evidence/sha_tables 表 A（域＝本卡四 PWF/记录件与被触碰件的 before 列）✓ |
| 触碰件 live 复算 | 15 条 `touched_files` 中 14 条 live sha==binding `after_sha256` ✓；第 15 条 `REMEDIATION_REGISTER.md` 见 §2（父方并发追加，已披露、非本卡） |
| 冻结载体 live 复算 | `untouched_frozen_attestations` 18 条 live sha==钉值（I-14-F-R1 report `8ce87ef6…`/sidecar `dbbe3e29…`、B1 report `6bfd2922…`、B1 commands `d76d14f9…`、I-14-D r2 `58f92dd7…`/r3 `c617c43a…`/r4 `f27a85a5…`/r5 `9f8fdba9…`、B5 两 binding、B5-fix 两原脚本 `71dbaf29…`/`e8f89b73…`、I-06-A/B rulings `5ef8d863…` 双卡同字节、I-05-C handoff `7c4f4719…`、PROMOTION-EXEC binding `2626314d…`、plan README `4ee64e33…`）✓ |
| JSON 可解析 | 本卡 `binding.json`/`commands.json`/`handoff.json`/`i14d_report_pins.json` + 被改 `_provenance.json` + B1 `handoff.json`（`ConvertFrom-Json` OK，`status=accepted_with_conditions`、`status_before_bookkeeping_fix=review_pending`、`implementer_signed=false`、`implementer_self_acceptance=false`、`note_on_status_historical_pre_verdict` 在）✓ |
| handoff 口径 | `status=review_pending`、`implementer_signed=false`、`unmapped_or_unproven` 8 条含 D2/D3/D7/B1-§9/D9/#21 git-add 项、`no_self_sign` 声明在 ✓ |

## 2. REM-79 headline gate（本次复审自跑）

- 工具：`execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py`（`1.2.0-correction2`）；`PYTHONIOENCODING=utf-8`、`python -X utf8 -B`。
- **本次复审命令**：`python -X utf8 -B <tools>/check_domain_assertions.py task_plan.md findings.md progress.md REMEDIATION_REGISTER.md` → 输出 `0 violation(s) across 4 file(s)`，**rc=0** ✓（复审期共自跑 3 次、全部 0/0；**末次在父方 `23:40:08` 折入之后**；与本卡 `evidence/rem79_after_final.txt/.json` 双录一致）。
- Before 基线（本卡存证，本次复审核对一致）：PWF 三文档 rc=1 / 4 violations（`task_plan.md:1630[全部]`、`findings.md:633[all]`、`findings.md:684[none]`、`progress.md:1060[全部]`）+ register 补充跑 rc=1 / 7 violations（L155/411/1092/1192/1202/1560/1605）= **四文件合计 11 violations（before）**。
- 四条原 flagged 行 + register 7 条同族行**逐行读验（same-line domain 已在盘）**：
  - `task_plan.md:1630` …（域限定·BOOKKEEP-REPAIR 2026-09-23：全＝上行所列 10 个探索脚本）
  - `findings.md:633` …（域限定…：ALL＝drift_patrol 该次所列 7 项自检，即 version、installation、config、docs、dependencies、schema、manifest）
  - `findings.md:684` …（域限定…：NONE＝批次 3 产品面零改动，域＝scripts/tests/tools/config 4 个产品目录）
  - `progress.md:1060` …（域限定…：全＝该段所列 4 类余项，N=4，即 owner 两问 / owner 晋升决定 / 外部 / 新轨道）
  - register `L155`（没有＝…仅指该 1 个 B5 目录的已提交基座）、`L411`（none＝…域＝REM-11 这 1 条闭包）、`L1092`（All＝…对象＝所述 2 个文件）、`L1192`（All＝…域＝本条所改 1 个文件）、`L1202`（None＝…域＝该 1 个活探针的旧键读数）、`L1560`（NONE＝…计数 N=0）、`L1605`（「每一个」＝owner 令原词，域限定…域＝审计问题处置矩阵所列各行、以 2 项令为界）
- **register 并发追加计数（三数分列）**：①本卡修复所据 before=`3a23fc99…`/188440 B、本卡修复后钉=`5dda68f5…`/210952 B（12 处行内追加=7 补域 + 5 三元组，逐行已读）；②本次复审**初测** live=`0634305e…`/216801 B（复审开始时）；③本次复审**末测** live=`f8cd3ac492c179c7284c891a3c705aca468c563cbcdaebcb2fd53908310aed8f`/223551 B、mtime `2026-09-23 23:40:08.903` 晚于本卡末写 `23:17:57` ⇒ 父方并发/后续折入累计 **+12596 B**（对 binding after 钉 210952 言）。**post-fix / 并发折入引入的新无界行 = 0**（本次复审 3 次 checker 自跑全 rc=0，末次检查在该折入之后）；**本卡 before 态四文件 violations = 11**（4+7）、**after 态 = 0**——诸数分列、不混记。
- 注记：register 是活文档，父方每折一次须重跑 checker（采纳该纪律，见 §9）。

## 3. Key item spot-checks（a–j 全做，live）

| # | 项 | 复审结果 |
|---|---|---|
| a | task_plan.md 尾节 | ✓ 尾节 `## 2026-09-23 — BOOKKEEP-REPAIR 补记（…DW15-prune-repair 正名 + I-07-C 卡号）` 在 L2068–2073（全文 2073 行）；L2072=DW15-prune-repair 正名（含 FAB-3/D12 名指缺陷注记、`a9b9076f…` 钉）、L2073=I-07-C 卡号（锚 `c3c3f533…`、accepted_scoped、holdout 双结果指引）；既有行仅 L1630 行内追加 1 处 |
| b | findings.md 尾节 | ✓ L703–717：I-07-C 条含 **holdout 双结果**（洛阳钼业 **603993 FY2021**、`dfeb7c54…`/6,610,553 B → ①SCAN PASS ②RESOLVE=先声明实测负例）+ F-REV-1→REM-95/F-REV-7→REM-96；I-09-C 条（`673c10bc…`、OPEN_IN_ACCEPTED_SCOPE、SC-1..SC-7）✓ |
| c | I-14-F-R1 review.md 翻转 | ✓ 头行 `Status: **accepted_scoped**`；`status_authority` 转录块在（verdict 词、裁决作者=独立复核、carrier 表）；`verdict_is_transcribed_not_authored: true` + `implementer_signed: false`；carrier pin **`8ce87ef6…`**/15841 B（live 复算==侧车）；**双留存均在**：兄弟件 `review_stanb_stub_historical_20260923.md` sha==before `7f180899…`/6029 B（且 mtime=2026-09-22 09:41:21=原件时点，Copy 保留时标）**且**新 review.md 内 `review_stanb_stub_historical` 字段含该全文（本次复审 `String.Contains(sibling)==True` 逐字节等同） |
| d | B1-I08C review+handoff | ✓ 新 `review.md`（`e6513e34…`/7581 B）：`accepted_with_conditions` 原词转录 + **§9 六条件**（F1/F2/F3/F7/F4-F5/owner 晋升序，L35–40）+ 词汇映射注记（`accepted_with_conditions ≡ accepted_scoped` 带遗留件）+ carrier 双钉（as-stands `6bfd2922…` + PENDING-form `73feb059…`）；`handoff.json` live `51f39149…`/28595 B（before `c5696e78…`/26788 B），键 `status_before_bookkeeping_fix`/`status_authority`/`status_semantic_mapping`/`status_flip_bookkeeping`/`note_on_status_historical_pre_verdict` 全在，JSON 重解析 OK |
| e | i14d_report_pins.json | ✓ 四报告 live 复算 == 钉值：r2 `58f92dd7…`/39824、r3 `c617c43a…`/44008、r4 `f27a85a5…`/51860、r5 `9f8fdba9…`/49279；`pin_nature` 明记 RETRO-PINS=post-hoc ✓ |
| f | D1b | ✓ `evidence_erratum_20260923.md`（`06f9a2f6…`/3886 B）在，声明「未产出/登记时点即缺/不补件」+ 3+1 搜证法 + 方法边界披露；**`production_anchors.txt` 不存在（本次复审自搜）**：B1-I08C 全树 0 hits、plan 根 depth4 0、`.planning` depth5 0、RF 仓（排除深层 .planning 情形）depth6 0、`before/` 实列 22 件仅 `production_anchors.json` 2782 B |
| g | B5 | ✓ `binding_erratum_20260923.md`（`f2cd0363…`）记录 **记录值 `06ff8064…` vs 实测 `96733875…`**（全值并列、两次实测复算、归因=后续父批/落定面 best-known、精确时点交 AUDIT-INTEGRITY 面）；`harness_relocatability_erratum.md`（`8bd5c1f0…`）+ `scripts_fixed/` 两副本已读：`OUT_DIR = argv[1] > env B5FIX_OUT_DIR > 历史默认`、`B5FIX_PLAN`/`B5FIX_PROD` 可覆盖、RELOCATABLE banner 在；**原脚本不动**：`scripts/verify_append_fixed.py`=`71dbaf29…`/9980、`scripts/verify_boundaries.py`=`e8f89b73…`/10467（live==before）✓ |
| h | RESPONSES.md | ✓ **本卡 0 字节**：live `1cfeef0f…`/2302 B、mtime `2026-09-23 21:36:18` —— 早于本卡 before 测量（22:22）与冻结（22:40）⇒ 不在本卡写窗内；本卡 binding `touched_files` 无 RESPONSES 条目、oracle 负清单明记不动。旁证：`git status` 显示 ` M outward_requests/RESPONSES.md`（=相对 HEAD 的 +10/-0 预存差异，非本卡）；三元组注记落位=register **L1449(§72)/L1483(§74)/L1501(§75)/L1541(§77)/L1563(§78)**，逐行已读，格式 `(sha256, 版本域, 留存位)` 齐（`37413f78…[267:42329]`/`74f5c835…[42566:89467]`/`8aabac09…[89705:139501]`，版本域=2026-09-22 转录快照）✓ |
| i | R5-06 | ✓ `execution_runs/_review_i14d_r5_20260922/` 实在：**30 件**（`DISPATCH.md` 8473 B + `scratch/` 29 件，抽列 claims467.py/diff45.py/hashes.py/linediff45.py…）；本卡注记在 decision §5「R5-06 注记」；**收尾清单 git add 项**在 decision §5（`git add execution_runs/_review_i14d_r5_20260922/` 随下一批）+ handoff `unmapped_or_unproven` 第 8 条 ✓（本卡零 git，真入库交父） |
| j | 冻结面 0 字节 | ✓ `git status --porcelain -- <execution_v2>` 空（123 项 tracked 无改动）；I-14-D 目录、I-14-F-R1/B1-I08C `reviewer_report.md`、I-06-A/B rulings 路径 status 空；rulings live `5ef8d863…`/139717 双卡同字节；四 I-14-D 报告 live==钉（见 e）—— 0 字节改动成立 |

## 4. Vocabulary map completeness（decision §2 抽验 6 形，≥4 要求）

| §2 行 | 引用 | 读行实证 | 判定 |
|---|---|---|---|
| 超界 #1 | `B1-I08C…/reviewer_report.md:16` | L16 ``**`accepted_with_conditions` — the card's security claims are CONFIRMED…`` | 词形与表一致 ✓ |
| 超界 #4 | `FIX-W06-GAPS…/reviewer_report.md:11` | L11 `## VERDICT — ACCEPT (scoped), with findings F1–F7` | 一致 ✓ |
| 超界 #5 | `I-02-D/a20260919-01/review.md:5` | L5 `## 结论：**ACCEPT**` | 一致 ✓ |
| 超界 #7 | `TTL-30D-POLICY…/review.md:3` | L3 `Status: **ACCEPT — scope-limited (`accepted_scoped`)**.` | 一致 ✓ |
| 超界 #8 | `RF-E2E-ADAPT…/reviewer_report.md:7` | L7 `- **Verdict: ACCEPT (sign-off as reviewer, 4 findings — none blocking)**…` | 一致 ✓ |
| 超界 #16 | `B5-plan-level…/review.md:4` | L4 `…**NOT ACCEPTED AS-IS — measured core verified /` | 词形一致；映射 `changes_required` 与四值域相符 ✓ |
| 自查 #9 | `I-07-B/a20260923-01/review.md:3` | L3 `Status: **`ACCEPTED_SCOPED`** (attempt `a20260923-01`).` | 一致 ✓ |

结论：8 处超界 + 自查补全形的 file:line 引用抽验 **7/7 命中且词形与表相符**；表声明「只做语义映射、不回改历史 verdict 原词」与盘上原词留存相符（本次复审未见任何历史 verdict 被改词）。

## 5. 两项自陈披露的核验

1. **B1 文档式 PowerShell `-replace` 数组形静默不替换 → `[regex]` 等价复算 MATCH `73feb059…`（37086 B）+ 49 B 笔误注记**：记录实在——`commands.json` CMD-BKR-04（result 含 MATCH 全值 + 数组形 no-op 披露）+ B1 `review.md` §「钉法复核注记（诚实披露）」（`$t -replace ('pat','rep')` 静默不替换机理、`[regex]::Replace` 重跑 MATCH、正文「37135 bytes」vs `report_pin.json` `bytes_hashed: 37086` 以 JSON 钉值为准）；本次复审读两处，推理链完整。**register 侧注记**：register 现行 12 处行内注记=7 补域 + 5 三元组，**不含**该条——其归位=父方 §6 折入块/后续节（本卡对 register 的权限面=行内 #2/#9，节写入归父，见 decision §6 头注），故此披露**在本卡文件面已登记、register 折入待父**（列 §9 收尾）。
2. **本卡 changes.diff `-` 侧转录行裁为非真阳**：记录实在——`changes.diff` 头注（`-` 侧行=修前历史行逐字转录、补域=篡改 before 文本、按 REM-79 语料转录类记「转录类非真阳」并显式登记）+ decision §8 同式。**本次复审自跑**：checker 对 `changes.diff` = **11 violations，全部位于 `-` 侧**（L14/29/32/50/56/59/62/65/68/71/74）⇒ 裁处成立（非真阳）。**计数偏差见 §7 F1**：本卡 `evidence/rem79_selfcheck_attempt.txt` 自录亦为 11，而 decision §8 与 changes.diff 头注写「12」。

## 6. 边界核验（zero-git / 零产品写）

- `git status --porcelain`（只读）：**staged 条目 0**（首列无 `M `/`A `/`D `）⇒ 与「本卡零 git 命令（尤其零 add/commit）」相容。
- 改动的 tracked 文件 10 件**全在 `.planning` 记录树内**（OWNER_DECISIONS/REMEDIATION_REGISTER/B1 handoff/I-14-F-R1 review/RF-STEP9-TRIAGE oracle〔兄弟卡〕/findings/RESPONSES〔预存〕/_provenance/progress/task_plan）；其中归属本卡=7 件（四 PWF+register、_provenance、I-14-F-R1 review、B1 handoff），余 3 件（OWNER_DECISIONS、RF-STEP9-TRIAGE oracle、RESPONSES）mtime 均早于本卡写窗或属并发兄弟。
- 产品路径（`.planning` 之外）：**modified=0**；untracked 仅 `.tmp-r41-mutation/`（mtime 2026-09-20 18:31）与 `assurance/unified_completion/manifests/plan_inputs.json.bak`（mtime 2026-09-21 07:09）—— 两件均早于本卡 2 日/2 日余 ⇒ **归本卡的产品写 = 0**。
- 本卡新建 untracked 件与 binding `touched_files` 一一对应（B1 review+erratum、B5 两 erratum+scripts_fixed/、I-14-F-R1 兄弟件、BOOKKEEP-REPAIR 目录）✓。
- handoff `unmapped_or_unproven` 8 条在位：disclosure_adaptation=unmapped、accuracy=unproven、D2、D3、D7、B1-§9、D9、#21 git-add ✓（=派单所列 D2/D3/D7/B1-§9/D9/#21 全覆盖）。

## 7. Findings（carried；均为文书级，不阻断收口）

- **F-R1（计数偏差，需一处更正）**：`decision.md §8` 与 `changes.diff` 头注称 changes.diff `-` 侧命中 **12**；实测（本卡自录 `rem79_selfcheck_attempt.txt` + 本次复审自跑）均为 **11**。裁处性质（转录类非真阳、`-` 侧全中）不受影响。⇒ 建议按 append-only 把 §8/头注的 12 更正为 11（或补一句「12=含 handoff `-` 侧未命中行」的口径说明）。
- **F-R2（冻结 oracle 与交付范围差 2 项）**：oracle §1 冻结 **20 项**（派单行=`…#19–20 = 20 项`，mtime 22:40:13 后未再追加）；decision §1 交付 **22 项**（多出 #21 R5-06 注记、#22 §八十四 引用规范）。两项均文书注记类、其内容已在 decision/handoff 披露；但按 oracle 自定「如需更正走 append-only 勘误」，**范围扩容未回写 oracle 追加件**。⇒ 建议父折入时补一条 oracle append（记录 #21/#22 的派单时点），或在 register 折入块显式登记该序差。
- **F-R3（attempt README 陈旧）**：attempt `README.md` 末行列交付为 `binding.md / commands.md / handoff.md`，盘上实件=`binding.json / commands.json / handoff.json`（名不符类，同 D1c 族）。⇒ 一句更正即可。
- **F-R4（handoff deliverables 枚举欠 3 件 evidence）**：handoff `deliverables` 列 evidence 8 件，盘上 `evidence/` 11 件（另有 `rem79_before.stderr.txt`、`rem79_after_final2.txt`、`rem79_selfcheck_attempt.txt`）。均为存证件，建议补列。
- **F-R5（披露 1 无 register 行）**：见 §5.1——register 折入块（decision §6）未点名 PowerShell 数组形披露；父折入时补一行即可（不属本卡权限面）。
- **F-R6（register 并发写）**：`REMEDIATION_REGISTER.md` before/after 钉被父方并发追加超越（末测 live 223551 B=对本卡 after 钉 +12596 B、mtime `23:40:08` 晚于本卡末写 `23:17:57`；复审期实测到该次写入，写入后 checker 仍 0）——本卡已在 binding `concurrent_writer_disclosure` 如实披露，非缺陷；仅要求每次折入后重跑 checker（§9）。

## 8. 未证 / 方法边界（unverified）

1. `production_anchors.txt` **全域**不存在：本次复审为有界搜索（RF depth6 排深层 .planning、`.planning` depth5、plan 根 depth4、B1-I08C 全树）= 0 hits；iso/venv 等超大树上递归会超时（与本卡披露同边界）。全域断言依赖 AUDIT-DESIGN 的先证，本次不升级该断言。
2. 「RESPONSES.md 本卡 0 字节」为 **mtime+写窗+binding 缺项+负清单**四重旁证；无本卡开跑前的全值 pre-pin（oracle §0 未列 RESPONSES），故以间接证据收束（`1cfeef0f…`/2302 B 为复审时点值）。
3. oracle §0 的 before 全值**不可在事后独立重测**（文件已过 after 态）；本次以三处交叉一致（oracle==binding==recovery/sha_tables）核其内部一致性。
4. 「本卡零 git 命令」为自陈 + 只读观察（staged=0、改动面与 binding 相符）相容，非可直接证明的命题。
5. attempt `README` 首跑 1 violation 后改写归零的历史一跑：仅存 decision §8 叙述，无首跑存证；现值 0 已复核。
6. B5 binding 失配的**精确改者/时点**：本卡如实记 best-known 归因并交 AUDIT-INTEGRITY 面——本次复审维持该未证状态（不升格）。
7. 父方 register 并发追加的**逐行归属**：未逐行归因（超出本卡与本复审的写面），仅计数其违规贡献=0。

## 9. Scope-if-accepting + 收尾清单（交父）

- **收口范围**：22 项以「已转录关闭/取代 + 已路由」收口（本卡为记录级修复：20 项按 oracle 冻结判据 + #21/#22 按 decision §1〔F-R2 序差已记〕）；**REM-79 after-state 四文件 = 0 violations / rc=0**（本次复审自跑证明，域＝task_plan/findings/progress/REMEDIATION_REGISTER 四件于复审时点）。
- **下一批 git add 项（本卡与本次复审均零 git，列父执行）**：
  1. `git add execution_runs/_review_i14d_r5_20260922/`（30 件，R5-06 / handoff #21）；
  2. `execution_runs/BOOKKEEP-REPAIR/a20260923-01/`（含本 `reviewer_report.md` + `.sha256` 侧车）；
  3. `execution_runs/B1-I08C-product-fixes/a20260921-01/review.md` + `evidence_erratum_20260923.md`；
  4. `execution_runs/B5-fix-g1a-g3/a20260922-01/binding_erratum_20260923.md` + `harness_relocatability_erratum.md` + `scripts_fixed/`；
  5. `execution_runs/I-14-F-R1/a20260922-01/review_stanb_stub_historical_20260923.md`；
  6. 本次复审**未**发现新的需入库漏项（域＝本次 porcelain 所见 untracked 条目中的本卡/复审产物）。
- **register fold 建议（采纳）**：把 decision §6 折入块 + §7 披露 + §5 F-R1/F-R2 更正 + §5.1 PowerShell 披露行折入登记册；**每折一次后重跑 `check_domain_assertions.py` 四文件并留证**（活文档纪律；本次复审后 live 态仍=0/0，折入不得回退该态）。
- **实现方不自签**：本 attempt 保持 `implementer_signed=false`；本报告为独立复核的验收文书，附 `.sha256` 侧车钉本报告字节。

---
独立复核（independent reviewer）· 2026-09-23 · VERDICT = `accepted_scoped`（含 F-R1..F-R6 carried；未授予晋升/资格/准确性）
