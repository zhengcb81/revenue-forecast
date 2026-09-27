# AUDIT-GOAL 独立审计报告 — 目标-进展对照（goal-vs-reality 追溯审计）

- 审计对象：`.planning\2026-09-19-three-project-history-audit` 计划全案（task_plan.md / REMEDIATION_REGISTER.md / OWNER_DECISIONS.md / findings.md / progress.md）+ `execution_runs\` 全部 attempt 载体 + `revenue-forecast` 仓 git 只读历史
- 审计基准 A = owner goal revision 4 五项判据（原文逐字，见 §2）；基准 B = owner 后续指令链（见 §4）
- 审计时点：2026-09-23（快照制；审计期间计划仍在推进，凡时点差异均已标注）
- 审计方式：6 名独立评审 subagent 分面并行 + 主审亲测复核（哈希重算、git 只读、盘上文件核验）；全程只读目标仓与计划目录，唯一写入 = 本 attempt 目录
- 本审计员角色 = 独立审计员（report+sidecar 即签名），**非实现者**；`implementer_signed=false`

## VERDICT

**`DEVIATIONS-found`** — 目标整体在轨推进（①已达成、②实质达成但记录与纪律有可核偏差、③登记行级处置存在缺口、④在 owner 语义下守住零破门但有 1 例历史破门嫌疑与 1 项语义替代、⑤五面纪律强保持但 PWF 三文档同步对 3 卡有缺口且违规均已自纠留痕）；**未发现硬捏造**（claim-vs-disk 类 4 项中 FAB-1 经本审计员字节级复证降级为口径差并已由父 §72 勘误处置，FAB-2/3 已注记，FAB-4 保持 UNVERIFIED，详见 §1）。目标达成率：92 张执行卡中 **72（严口径）/73（含 I-14-D r7 载体）** 已 `accepted_scoped`，16 张未开工（其中 I-10-A 门已开、审计快照后已派 `1f99d8b2` 运行中），与"全部完成"仍有可核差距（§7）。

---

## §1 捏造嫌疑（最高严重度单列：声称存在而盘上无 / claim-vs-disk）

主审独立重算确认（详见 `evidence/independent_crosschecks.md` §4）：

| # | 严重度 | 项 | 声称 | 盘上实测 | 定性 |
|---|---|---|---|---|---|
| FAB-1 | ~~HIGH~~ → **LOW（已处置并复证，口径类）** | `outward_requests\RESPONSES.md:7` 对 `T2-SIM-OPEN6-SEC\a20260922-01\ruling.md` 的 sha256 钉 | `8aabac09…` | 活文件重算 `5cb476767a934885…`（另两函活文件钉相符） | **pin-vs-live 口径差，非捏造、非丢失**：父方 §72 勘误称"登记钉=注册时点版本、其字节逐字保全于 `I-06-B\a20260919-01\rulings_transcribed_2026-09-22.md` BEGIN/END 段内"——**本审计员字节级独立复证成立**（自提 3 段转录体 strip-marker 后哈希 = `37413f78…`/`74f5c835…`/**`8aabac09…`** 三钉逐一 MATCH）；活文件系注册后 dated-append（自 char 22394 分叉）。处置=RESPONSES.md 勘误行+C8 判据精确化+三文件冻结令（2026-09-23，均已在盘核到）。**残留要求**：引用该钉处应带"注册时点版本"限定语。 |
| FAB-2 | MEDIUM（已注记） | `execution_runs\OUTWARD-LETTERS-UPDATE\`（OWNER_DECISIONS.md:427 称「已派 ea7ecf69」） | 名指该 attempt 目录 | **盘上不存在**（exists=False） | 指针/记账缺陷：工作真、指针错（函件更新实体在 `outward_requests\` 三函更新段+_provenance 前缀证明已核到）。父方 §73 已落勘误注记。 |
| FAB-3 | LOW（已注记） | `DW15-REPAIR`（OWNER_DECISIONS.md:357） | 名指该目录 | 不存在；实为 `DW15-prune-repair\` | 改名未回填；父方 §73 已注记。 |
| FAB-4 | LOW/UNVERIFIED | 批 5 首轮 ruff F401/BOM/宿主字面红态的字节级红→修证据 | register 叙述为证 | 红态工作树字节从未入库（pre-amend 提交不含该文件，SA-PUSH 复测） | 该红→修差分仅存于散文记录，git 不可复原；终态已独立核净。未处置，保持 UNVERIFIED。 |

硬捏造（凭空声称工作/证据存在）：**0 例**。SA-REM/SA-DEFECT/SA-CHAIN/SA-PUSH 共 50+ 指针抽核全部盘上命中（哈希钉 100% 相符，唯 FAB-1 一钉例外）。反向案例（真件被说成丢失）已由计划自身纠出并勘误（F-REV-B1P-01）。

## §2 五项判据对照表（基准 A，逐条 = MET/PARTIAL/DEVIATED/BLOCKED）

| 判据 | 结论 | 关键证据（行/哈希） | 独立核法 |
|---|---|---|---|
| ① 8 个在飞卡全部收口并派独立复审/载体落定为 accepted_scoped | **MET** | 8 卡名→8 attempt 目录 1:1；8/8 独立复审 verdict=`accepted_scoped`；8/8 落定三件（review.md/handoff/qualification.json）在盘（`evidence/criterion1_eight_cards.md`） | 主审对 8 份 reviewer_report 逐一 `Get-FileHash` 重算 = 各 sidecar 钉（8/8 相符）；I-14-D 另做双前缀字节证（26172B/22100B 均 MATCH） |
| ② 门绿后推批 1；B1/B3/I-14-D 收口后攒批 2；不绕过任何门、门红修根因 | **PARTIAL（实质达成，记录/纪律偏差 4 项）** | 9 个推送窗口 36 提交全在 origin/main，HEAD==origin/main==`b7a6a116`，ahead=0；批 1=21 提交（"20+"核符）；批 2=`6f74b056..3861f08d` 在 I-14-D/B3/B5/B1-PREREQ 四前置齐后推（progress.md:1038/1050）；**零绕门**：4 个拦门事件根因修全部落在码/测（ruff F401、U+FEFF BOM+宿主字面、E2E 回执契约、600s 超时），门文件在窗口内仅 2 次改动且均 owner 授权（`6f74b056` 一行 600→1200；`95df2661` real-data 步 1800） | 主审 `git cat-file -t` 核 10/10 边界 sha=commit；SA-PUSH 逐窗 `rev-list --count` 重数 + 门文件全史 `git log --follow` + bypass 词扫描（no-verify/deselect 0 命中） |
| ③ REM-01…REM-79 按依赖逐项处置 | **PARTIAL（行级缺口）** | 全表 REM-01…86 共 86 行：处置 76（FIXED 45 + 隐式修 10 + 裁定 8 + 注记结转 13）；**判据域内（REM-01…79）10 行无任何处置记录**（REM-05/06/07/08→登记的修卡"B2"从未开跑（register:100）；16/17→"B4"同；25=owner 选择未落；30=F-5 落在勘误集外；35；67①③（register:263 明写"未处理"））；另 10 行仅隐式闭环（行文未回填）；REM-78/79 编号混用 | SA-REM 抽 25 行 + 29 指针重验（哈希钉 16/16 相符、git sha 7/7 真）；主审亲核 register:100/263 等静默丢行原句 |
| ④ 19 卡链依赖门打开后按九步执行；零破门 | **PARTIAL（owner 语义决定 + 1 例历史破门嫌疑）** | 已行卡 I-07-B/C/D、I-09-C、I-06-A 实现批全部门依据在先（I-09-C 的 binding 晚于 I-08-C 载体落定 38 分钟=干净时序）；等待表 16 张卡全部零 attempt（其中 **I-10-A 门已全开**：I-07-B✓+M01-M31 31/31✓，只欠派单）；**破门嫌疑 1 例**：I-06-B\a20260919-01 在 I-06-A blocked（其 handoff 自记 blocked_by）时被实现并 accepted（后被 09-22/23 两 attempt 取代，已披露）；**语义替代 1 项**：函 A「TIER-2 外部回执」盘上实为 role-play 模拟裁定 + owner 终确「全部接受」生效（RESPONSES.md:3 明写「非外部方真实签署」）——若判据要求真实外部签署，则该门从未按字面打开 | SA-GATE-DEP 逐卡 blocked_by/时序核 + 40 卡依赖表；主审亲核 I-06-B handoff blocked_by 原文、I-14-D/I-08-C 载体时序 |
| ⑤ 五条纪律：隔离副本 / oracle 先冻结 / 独立 reviewer / 生产零合并 / 历史产物不改 + PWF 三文档同步 | **PARTIAL（五面强保持；PWF 同步对 3 卡有缺口）** | 10-attempt×6 面抽样（SA-DISC，`evidence/report_SA-DISC.md`）：约 50 次独立重哈希**零失配**、10/10 复审 pin 相符、10/10 无冻结时序倒挂、生产零合并 10/10 有锚证且 live porcelain 复核干净；**缺口**=PWF 三文档同步：findings.md 缺 I-07-C/I-09-C 两卡条目、task_plan.md 缺 DW15-prune-repair 与 I-07-C 卡号；I-14-D 的 r2-r5 四份复审报告无 pin（稳定=散文级）；隔离副本 2 例 WEAK（GATE-TIMEOUT/I-08-C 按披露设计在生产树只读/一行授权改动） | 主审 `Get-FileHash` 复算 8/8 pin + I-14-D 双前缀 + 冻结时序 2 例实测；批 9 暂存滑点（3 张在飞卡 13 件被卷入 `b7a6a116`）已自纠并加硬守卫（register §64，第 11 例流程类） |

## §3 判据细目

### 3.1 ① 8 卡收口（8 卡名 → 8 attempt 目录）

| 目标项 | attempt | 独立复审 verdict（复审报告行） | 落定三件 | pin 复算 |
|---|---|---|---|---|
| GATE-TIMEOUT-1200 | GATE-TIMEOUT-1200\a20260922-01 | accepted_scoped（report L6） | review.md 9432B / handoff.json / evidence\GATE-TIMEOUT-1200\qualification.json 15182B | 2a66abae… ✓ |
| DW15-prune-repair | DW15-prune-repair\a20260922-01 | accepted_scoped（`## RULING` 三态） | 3445B / ✓ / 4202B | a9b9076f… ✓ |
| B5-fix-g1a-g3 | B5-fix-g1a-g3\a20260922-01 | accepted_scoped（33 次子进程复跑复审） | 8073B / ✓ / evidence\B5-fix\qualification.json 11354B | 69ea3b03… ✓ |
| I-08-C oracle 重冻 | I-08-C\a20260919-01 | accepted_scoped（report_r2，scope 含"append-only oracle re-freeze (revision r4)"） | 17098B / ✓ / 5882B | ee5046a5… ✓ |
| I-14-F-R1 150/60 | I-14-F-R1\a20260922-01 | accepted_scoped（应用 owner §16 E-1「E-1: 150/60」） | 6029B / ✓ / 7969B | 8ce87ef6… ✓ |
| INVEST-CORE 护栏 | INVEST-CORE-ATTEST-GATE\a20260922-01 | accepted_scoped（复审自跑 RED 7/3、GREEN 10、变异 M1） | 12968B / ✓ / 18727B | 09b4e13e… ✓ |
| I-14-E-APPLY 重跑 | I-14-E-APPLY\a20260921-01 | accepted_scoped（Q1 裁 option (ii)，带 scope 语句） | 5358B / ✓ / 3220B | feaec562… ✓ |
| I-14-D r6 复审回收 | I-14-D\a20260919-01 | r6=`changes_required`（§9 修单）→ r7=`accepted_scoped`（report_r7 §0 L11） | 31094B / handoff_r6.json（=accepted_scoped 载体） / 12090B | cc6da8d3… ✓（r6 钉 f1c9761d… ✓） |

注（非偏差，口径披露）：I-14-D 的验收载体 = `handoff_r6.json`（status_authority 指认 report_r7，transcribed_not_authored=true），顶层 `handoff.json` 按追加式设计保留历史 `review_pending`；r7 通报的 carried 未闭清单（F-REV-R3-02/03/05/06..10、R4-02、R5-03..08 "registered-unaddressed"）已在 §5 台账归位，无静默丢。

### 3.2 ② 推送纪律与"零绕门"（批 1-9 对表）

| 批 | 窗口（重验端点均=commit） | 提交数 | 门记录 | 判定 |
|---|---|---|---|---|
| 1 | ab20cebe..6f74b056 | 21 | findings.md:655「pre-push gate GREEN — safe to push」+ 抓取在案 | VERIFIED |
| 2 | 6f74b056..3861f08d | 1 | progress.md:1052 门 10/10 绿（含 real-roots+real-data） | VERIFIED（带病：2 gitlink 随批，见下） |
| 3 | 3861f08d..4b1c690b | 3 | findings.md:682 门 10/10 | VERIFIED（3c=gitlink 治愈） |
| 4 | 4b1c690b..865428f8 | 5 | register:1097 门 10/10、gate=1800 版 | VERIFIED |
| 5 | 865428f8..b0d016a6 | 2 | register:1213 推送 rc=0 门 10/10（窗口=批5/5c 两提交；另 1 个 pre-amend 悬空提交 0d10ae8f + 2 次被门拦回） | VERIFIED（"5a/5b/5c"标签与 git 不 1:1 对应，INC-2） |
| 6 | b0d016a6..262659e4 | 1 | progress.md:1148 门 10/10 | VERIFIED（记录偏薄） |
| 7 | 262659e4..a31fd7ed | 1 | progress.md:1158 门 10/10 | VERIFIED（记录偏薄） |
| 8 | a31fd7ed..977fa1e8 | 1 | **无门绿行**（仅 register:1323 推送意图书面 + :1331 CI run #312 佐证已推） | **UNVERIFIED 门记录** |
| 9 | 977fa1e8..b7a6a116 | 1 | **无门绿行**（register:1362 冻结于"批 9 推送中"） | **UNVERIFIED 门记录** |

拦门根因修复（抽 4 例：3 主线 + 1 前置；4 例的修复面均为码/测，门与基线零改动）：
1. **ruff F401**（批 5 轮 1）：`tests/test_message_contract_pins.py:30` 未用 import → 只删该 import（`git diff 0d10ae8f 1fa090fe --stat`=恰 1 文件）；门/基线零动。
2. **U+FEFF BOM + 宿主字面**（同轮）：自伤 BOM（自记第 9 例自纠）+ 测试烤死 `C:\Users\…` → 同一测试文件改 `Path(__file__).resolve().parents[1]`+env 覆写；host-assumption 守卫本身未动（门文件日志复测）。
3. **E2E 回执契约 fail-closed**（批 5 轮 2，RF-E2E-ADAPT）：CW 合面引入 state_domain fail-closed 而 RF 夹具铸旧式回执 → 修 4 个 tests/ 夹具文件让其走 CW 真写手；`b0d016a6` 不触 tools/、changes.diff 零 skip/xfail/deselect/pytest.mark（grep 复测）；变异还原复现 4F 红=合规证。
4. **600s 超时**（批 1 前置）：owner 授权一行 600→1200（§16 B=a），红/绿活体成对留证，测试选择集 55/65 计数不变。

门文件全史判定（SA-PUSH `git log --follow` 复测）：窗口内恰 2 次门改动——`6f74b056`（一行超时，§16 授权）与 `95df2661`（real-data 步 1800 + f2 120→300，§18 B=全批授权）；**无任何削弱性门改动、无绕行旗标**（no-verify/deselect 提交信息 0 命中；register:903 明令永不设绕过旗标）。

② 判据的偏差项（**不绕门=守住；记录与前置解释=偏差**）：
- **DEV-2.1**：批 8/9 无**当批**门绿记录（INC-1）——已推但门结果未随批入账。父方 §73 已**事后补账**（批 8 门 10/10 绿=09-23 17:18 push log；批 9 门 10/10 绿=19:51 push log）；补账非 contemporaneous 记录，"门绿才推"对这两批以补账+间接推定成立（门文件与选择集两批内未变），记录纪律偏差保留计列。
- **DEV-2.2**："B1/B3/I-14-D 收口后攒第 2 批"按计划自述口径执行（批 2 四前置=I-14-D/B3/B5/**B1-PREREQ**，progress.md:1038「全齐」后推）；但字面所指的 **B1 原卡 `B1-I08C-product-fixes` 至今 handoff=`review_pending`**（复审词 `accepted_with_conditions`，无 review.md 落定件），其状态回填被明记为"父/owner 权"（progress.md:1009）且未完成——字面口径未满足，属已披露的口径替代。
- **DEV-2.3**：批 2 带病推送 2 个 mode-160000 内嵌 gitlink（findings.md:671-673 自记"属运气非护栏"），批 3c 治愈、远端历史已修补。
- **DEV-2.4**：批 9 暂存纪律滑点——3 张在飞修卡 13 件产物被卷入 `b7a6a116`（register §64 自纠，第 11 例流程类；已加 `if($active.Count -gt 0){throw}` 硬守卫）。

### 3.3 ③ REM 处置（抽样 + 全量普查）

- 抽样 25 行（含强制 REM-01/47/48/49/54/79/80/84 + 85 + 合并行 59/60/61）：CLOSED-VERIFIED 16、CLOSED-CLAIM-ONLY 2、CARRIED-WITH-NOTE 3、OPEN 2；指针抽核 29 个（哈希钉 16、git sha 7、目录 6）**全部盘上命中**。
- 全量普查 REM-01…86：FIXED 45 / 隐式修 10 / 裁定 8 / 注记结转 13 / **OPEN 10**。
- 判据域（REM-01…79）行级处置轨迹 = 59/79 显式 + 10 隐式；**10 行零处置**（③ 的"一条不许静默丢"在此失守）：REM-05/06/07/08（修卡"B2"登记未跑，register:100）、REM-16/17（"B4"同，:102）、REM-25（"需 owner 选"无选择记录，:51）、REM-30（F-5 不在 ERR-I14FR1 勘误集内，:56）、REM-35（措辞修正无下文，:62）、REM-67①③（register:263 明写"未处理"）。
- 依赖序 3 例全合规（REM-59/60/61→62→63；REM-43 前置门 r2 过审前不得 closed；REM-49=晋升硬前置先于 PROMOTION-EXEC）；1 例轻微（REM-24"与 REM-18 同批"实质随批落地但行未回填）。
- 编号混用（MEDIUM）：REM79-MECHANIZATION 机制化的是 REM-78 的规则（带域断言行文），register 后文以"REM-79"记功；REM-78 行（:353）仍留"仍欠机制化"。主审裁定：按 register:215/240 亲核，**REM-62=已闭环**（SA-DEFECT 之 OPEN 判系读了 :198 旧快照，见 `evidence/independent_crosschecks.md` §6）。

### 3.4 ④ 19 卡链依赖门（零破门）与等待表

零破门判定（SA-GATE-DEP 逐卡 + 主审抽核）：
- I-09-C（门=I-08-C 收口）：I-08-C 验收载体 report_r2（09-22 09:33）→ 落定 09:59 → I-09-C binding 10:11，**38 分钟干净时序**，GATE-RESPECTED。
- I-07-B/C/D：各自前置 handoff 钉在先（I-07-C 钉 I-07-B handoff `e43cf258…`、I-07-D 钉 I-09-C oracle），全部 GATE-RESPECTED。
- I-06-A（门=函 A TIER-2 外部回执）：门依据 = RESPONSES.md 三函登记 + OWNER_DECISIONS §19「全部接受」终确（生效链明写"→ I-06-A 首条解除 → 19 卡链开闸"）；实现 attempt a20260922-02 的 oracle/binding 时序在门后，GATE-RESPECTED **按 owner 重定义的门语义**。
- **破门嫌疑 1 例**：I-06-B\a20260919-01 在 I-06-A blocked 时实现并 accepted（其 handoff 自记 blocked_by 两行原文，主审亲核），其 W06-1 幂等键后被 OPEN-2-A 裁不足；已被 09-22/23 attempts 取代但该 acceptance 留档。
- **语义替代（交 owner 裁）**：函 A 门的盘上实质 = role-play 模拟裁定转录（三函自身抬头禁称"TIER-2 已签"）+ owner 终确；若判据④按字面要求真实外部回执，则 I-06-A 之门按字面未开、其后 19 卡链开局均需重新定性（现全部卡片证据对此均如实披露，无隐藏）。父方 §72 已将"门①正确表述=owner 终确模拟裁定解除（非外部回执）"入册随下游携带，§73 请 owner 确认维持授权例外或改判——**本审计员维持该语义项计列，待 owner 复确认**。
- 历史破门嫌疑 1 例已由父方 §73 登记为"已披露的历史例外、现行链以取代版为准"——**本审计员维持 DEV 计列不撤销**（历史 acceptance 仍在档）。

等待表（16 张零 attempt，非目标自述的 13 张——目标列举的 I-07-B…I-07-E/I-09-C 中前三张+I-09-C 已完成）：

| 卡 | 等什么 | 等谁 | 备注 |
|---|---|---|---|
| I-10-A | **无——门已全开**（I-07-B✓ + M01-M31 31/31✓） | 仅欠派单（owner/编排） | **审计快照后已派 `1f99d8b2` 运行中**（父方 §73）——本表计列以审计时点为准 |
| I-07-E | I-10-A、I-11-B、I-11-C | 其他卡 | 链首待开 |
| I-11-B / I-11-C | I-10-A / I-11-B | 其他卡 | |
| I-12-A…E | I-07-E→A→B→C→D 链 | 其他卡 | 5 张链式 |
| I-13-A | I-07-E + I-11-C | 其他卡 | |
| I-13-B / I-13-C | I-13-A / I-13-B | 其他卡 | |
| I-16-A | I-07-E、I-13-A/B/C（+I-14-D/E 验收面） | 其他卡 + owner 生产晋升语境 | |
| I-16-B / I-17-A | I-16-A / I-16-B（+自然观察时间） | 其他卡 | |
| I-17-B | I-17-A + I-12 + I-13 | 其他卡 | |

（函 A 已按 owner 终确关闭；函 B 信任根仍外部挂起但只闸 P5-b 身份链，不闸上述 16 张。）

### 3.5 ⑤ 五条纪律（10-attempt 抽样）

SA-DISC 对 10 张 attempt（GATE-TIMEOUT-1200、I-08-C、I-14-D、DW15-prune-repair、B5-fix-g1a-g3、I-14-F-R1、INVEST-CORE-ATTEST-GATE、I-14-E-APPLY、I-07-C、I-09-C）逐张核 6 面，结果表见 `evidence/report_SA-DISC.md`。要点：

- **面3 复审独立性**：10/10 的 verdict 均由独立复审写就、`implementer_signed=false`；连 I-14-D r1..r7 在内共 17 份复审报告、约 50 次独立重哈希**零失配**（10/10 sidecar 内容相符）。
- **面2 oracle 先冻结**：10/10 无冻结时序倒挂；主审另实测 2 例（GATE-TIMEOUT `oracle_freeze.json` 08:26:39 < 首跑产物 08:30:29；I-08-C `oracle.md` 19:50:51 < runner 产物 20:28:22）。弱证已披露：B5 批文件 CT/LWT 元数据异常、I-14-F-R1 `before/` 树系跑后拷贝——此类以内容钉（`oracle.sha256`、per-arm `oracle_document_freeze.json`）补强，非仅凭时间戳。
- **面4 生产零合并**：10/10 锚证在案（porcelain/生产锚哈希快照），live 只读 porcelain 复核干净；生产改动只经 owner 授权父提交路径（`6f74b056`/`95df2661`/PROMOTION-EXEC/CW `ac4ebd0`+`5d72529`+`bf0c8b2`）。
- **面5 历史产物不改**：抽算稳定（已钉件 100% 相符）；**缺口**=I-14-D 的 r2-r5 四份复审报告无 pin（MEDIUM 1，稳定=散文级）、`handoff_r2.json` 缺件（MEDIUM 2）。
- **面1 隔离副本**：8/10 PASS；2 例 WEAK 系披露设计（GATE-TIMEOUT=owner §16-B 授权一行就地改+锚前像 `.orig`；I-08-C=binding 明写无隔离副本、生产树就地只读）。
- **面6 PWF 同步**：progress.md 10/10 在案；**findings.md 缺 I-07-C、I-09-C 两卡条目；task_plan.md 缺 DW15-prune-repair、I-07-C 卡号**（LOW 2）——⑤ 在此扣分，判 PARTIAL 的主因。
- **父侧卫生**（MEDIUM 3，已由计划自披露）：父批次提交曾把 6 个内嵌 git 仓记为 mode-160000 gitlink（I-14-D 内 4 + INVEST roundtrip 2）；attempt 级零合并未破，系经授权父提交漏入索引，后批治愈。
- **审计期间新增的两项开放稳定性事项**（父方 §72/§73 入册、定位中，本审计员照实计列）：①B5 自记 `boundary_verification.json` 中 `binding.json` 记录哈希 `06ff8064…` ≠ 实测 `96733875…`（B5 树在其 handoff 后被改动，改动者待 AUDIT-INTEGRITY 面定位）；②I-07-D 的 F02/F03/F04 判决 raw 字节经 %TEMP% 授权清理未留副本 ⇒ 新证据留存政策（judged-run raw 必须入 attempt/evidence）已立，本案不可重算。

已知纪律违规 = DEV-2.4（批 9 暂存滑点，自纠+硬守卫），与"历史产物不改"无涉。

## §4 owner 指令链逐条对表（基准 B）

| # | 原话 | 执行落点 | 完整性 |
|---|---|---|---|
| D1 | 「A-1: 1, A-2: 授权, B: 全批, C:更新函件」（OWNER_DECISIONS.md:420 §18） | A-1→M01-M04-PROPAGATE\a20260922-01（accepted_scoped，20 跑 7722 文件零漂）；A-2→START_HERE.md:228-241 append-3（REM-84 关闭）；B→PROMOTION-EXEC（10/11 字节准，**B-6c 实测 59过→31败回归即停+回滚**，后经 MODEL-ORACLE-ALIGN 重落）+GATE-OQ-FIX（OQ-01/02）；C→三函追加式更新段+_provenance.json 前缀证明 | EXECUTED-WITH-DISCLOSURE（C 的名指 attempt 目录缺失= FAB-2；B-6c 停回滚如实） |
| D2 | 「fail的全部要修复」（register:981 §39） | OPEN5-DOUBT-PROBE P1-P6 探针→FIX-W06-GAPS 12 组修面（accepted_scoped，变异 12/12 红） | FULLY-EXECUTED（P5-b 暂缓→fail-closed 升级为追加式留痕） |
| D3 | 「全部接受」（§19）+ TTL=A 30 天 | 三 T2 裁定生效→RESPONSES.md 登记→I-06-A 首条解除→19 卡链开闸；TTL-30D-POLICY（cap=2592000s，RED 9→GREEN 16/16，2 变异红集精确） | EXECUTED-WITH-DISCLOSURE（TTL 仅 iso、生产未落——"落产品策略"勿读作已在生产） |
| D4 | 「发现的缺陷都要全部修复」（register:1025 §41） | 全量缺陷台账（§5）：登记+路由全覆盖、0 无主；FIX-W06-GAPS 等修卡落地 | PARTIAL——登记/路由全，但 16 项"登记未修"+登记行级 10 处静默丢（§5） |
| D5 | 「所有存疑都要确认」 | 22 条存疑收口账（register §42/§43）：19 关闭确认 + 3 随修关 + 0 无主；构成核对 8+6+8=22（三函编号清单），算术 17+3+2=22→19+3+0=22 两向皆合；抽 6 条端到端（存疑→裁答→执行）全通 | FULLY-EXECUTED（1 项分区细节松散：C7 消歧项不在 22 编号内，算术仍成立） |
| D6 | e2E 四约束（覆盖情形/主要步骤/真实数据/自建独立环境+数据/用后恢复/小规模） | E2E-EXPAND\a20260923-01（oracle.md:5 逐字载）：跨仓全链套件+RF-E2E-ADAPT 根因修（55 GREEN）；真实数据=复审 PROVEN+真实下载；独立环境+删除证明 post_absent；小规模（时标重导 1×2 ≤50MB、3 文件 diff、quality.yml 未动） | FULLY-EXECUTED（KEEP-RED→F-EE1 缺陷卡→live 复测通过） |
| D7 | 「给你真实下载复测授权…」→「同意」（CI 修序列三外发动作） | 真实下载复测：轮1 瞬态 skip 如实记、轮2 S1=pass（downloads==1、deletion 证明）；三外发动作（①CW 推 ②manifest wiki 钉改 ③RF 推）=执行序在 register:1384，随 CW-GATE-UNBLOCK-2/RF-RATCHET 系列在飞 | retest=EXECUTED-WITH-DISCLOSURE；三外发动作=PENDING-ROUTED（外部动作按约定如实路由） |

## §5 缺陷全量处置表（「发现的缺陷都要全部修复」核——一条不许静默丢）

全量清点 ≈110 缺陷单元（族表详见 `evidence/report_SA-DEFECT.md`；下为族级处置汇总 + 违"全部修复"清单）：

| 族 | 单元数 | 处置汇总 |
|---|---|---|
| I-14-D r1（F-REV-D-01…05 / REM-04…08） | 5 | D-01=FIXED（r6 码修+r7 记录，REM-81 关，主审亲核 r7 载体）；**D-02/03/04/05=登记未修**（路由卡"B2"未跑） |
| C 泄漏矩阵（C1-C13 各面） | ~14 | C1-C9/C11/C12=FIXED（r2-r6 类展宽，N5f-N5w）；C10=registered_open（按设计定价挂起）；C12/C13=路由立卡（I-14-C 前置/I-18-A）；I-04-C C1=FIXED、C2=owner 裁定闭；I-04-E C1/C2=FIXED |
| F-REV-R2（4） | 4 | 全 FIXED（r3）；REM-62=已落地（register:215，主审裁定） |
| F-REV-R3（10） | 10 | R3-01/04=FIXED（r4）；**R3-02/03/05/06-10=登记未修**（8 项） |
| F-REV-R4（4） | 4 | R4-01/05/06=FIXED（r5/替代更正）；R4-02=钉住不改+更正入 C5.5 |
| F-REV-R5（8） | 8 | R5-01/02=FIXED（r6/替代更正）；**R5-03…08=登记未修**（R5-08 载荷形经 r7 部分闭） |
| F-REV-R6（5） | 5 | R6-01/03/05=FIXED（r7 落定，主审亲核）；R6-02=半修（父侧 1 处+r7 2 处）；R6-04=known/carried |
| F-REV-B1P（7） | 7 | B1P-01=FIXED（含对源头 B1 源复审 F4 的勘误）；B1P-02=RETRACTED（假缺陷）；B1P-03/05=FIXED；B1P-04=carried+hash-pin 政策；R2-01=won't-fix 登记；r1 测试文件 18236B=不可逆真损 |
| F-REV-1…8（I-07-C） | 8 | 2/3/4=FIXED（落定三件）；5=在修（改线 scan/ensure 触发）；6/8=INFO 记录；**1(C1)/7=路由无 REM 号**（无可闭行=追迹缺口） |
| F-F05-cause / F-F06-audit（I-07-D） | 2 | 台账路由（修面已定义：cause 三字段持久化 / 成员判定值域匹配），**尚未修** |
| F-EE1 | 1 | FIXED（CW `bf0c8b2`+复审 ACCEPT(verified)+live 复测轮2 S1=pass） |
| P1-P6 探针 | ~13 | P1×3/P2-B/P3-A/B/P4-SCOPE/P5-a/P5-c/P6-A/B=FIXED（12 组修面，探针 01-06 证据在盘）；P5-b=临时 fail-closed 修+全链 EXTERNAL-BLOCKED（函 B 信任根）；P3 resume"缺陷"=RETRACTED（按设计未建） |
| 棘轮 8+2（RF 8 行+CW 4 行+测试方法缺陷+缺口 D+coverage 债） | ~15 | 测试方法缺陷=FIXED（全量扫描标准）；RF 8 行/ CW 4 行=IN-PROGRESS（RF-RATCHET-FIX/REST-A/REST-B/CW-GATE-UNBLOCK-2 分卡在飞）；缺口 D=升级必做路由；coverage 85.4<95=在修（不降 95 冻结值） |
| OQ 系 | 5 | OQ-01/02=FIXED（GATE-OQ-FIX，批 4 负载实证关闭）；**OQ-03=OWNER-BLOCKED**；OQ-I10B-2=OPEN（REM-24）；OQ-I10B-3=RETRACTED |
| 假缺陷/自纠（RETRACTED） | 12 | 全部留档撤回（31 槽位/24 模型、M31 F-02、"r1 stdout 丢失"假陈述、F6 假分歧、判据自伤 ×6+、62 裸字节假失败、REM-79 末 2 条 0 真阳、19 卡 regex 假 GATE-OPEN 等） |
| 其他产品缺陷 | ~12 | natural_window ×2→I-14-H；model_registry→I-10-B（残 REM-17/18/24）；D-W15 prune 5 类=iso 内修毕、**生产执行 OWNER-BLOCKED**；I-03 字典序=FIXED；**I-04-C E1/E2=登记"待做"无下文**；F12=OPEN 双轨；F5=裁定无动作；14 项 CW 存量败=CW-TEST-DEBT 在修；CI 红集=在修/待 owner 放行 |

**处置计数**：FIXED-with-evidence ≈42｜FIXED-no-action 3｜FIXED-claim-only 4｜半修 2｜IN-PROGRESS 12｜ROUTED 21｜OWNER-BLOCKED 3｜EXTERNAL-BLOCKED 2｜RETRACTED 12｜**OPEN-UNROUTED 0**。
**违"全部修复"的欠账（非静默丢、但未修）**：①登记行级 10 行零处置（§3.3）；②登记未修 16 项（F-REV-D-02…05、R3-02/03/05/06-10、R5-03…08、REM-17/18/24、I-04-C E1/E2、F12）；③无 REM 号路由 2 项（F-REV-1、F-REV-7）；④棘轮 12 行+CI 红集在修中。

## §6 22 条存疑收口账（「所有存疑都要确认」核）

构成：OPEN-4#1-8（8）+ OPEN-5#1-6（6）+ OPEN-6#1-8（8）=22；终态 19 关闭确认 + 3 随修自动关 + 0 无主（register §43:1064 封存；progress.md:1108）。抽 6 条端到端（存疑原文→裁答→执行落点）全通：O4#1（模拟裁定待终确→§19 全部接受→RESPONSES 登记）、O5#1（additive migration→P1 FAIL→FIX ①真迁移器）、O4#7（TTL 数值→TTL=A→TTL-30D-POLICY）、O5#2（阻断文案→P4 九行扫→P4-SCOPE 钉住）、O6#7（I-05-B 入口未读→确认"缺席 by-design"、不伪造接口）、O6#8（role_set 篡改面→grep 双证零引用→前瞻约束入 I-06-B）。分区小疵：C7 消歧项属"边界补充记"而非 22 编号之一（算术仍 19+3+0=22 成立）。

## §7 目标差距表（goal 自述「≈66/92」→ 现值）

| 口径 | 数 | 明细 |
|---|---|---|
| 执行卡总量（dispatch.md 自记 92 张） | 92 | 逐卡 handoff 状态普查（`evidence/independent_crosschecks.md` §8） |
| **accepted_scoped（严口径=顶层 handoff）** | **72** | 较 goal 自述 ≈66 **+6**（I-07-B/C/D、I-09-C、I-06-A/B 转正等） |
| accepted_scoped（含 I-14-D r7 载体） | 73 | I-14-D 实质已闭（report_r7+handoff_r6） |
| review_pending | 4 | I-00-A（review.md 结论=changes_required 一项证据缺陷待修）、I-08-A（复审禁写 accepted 字样，实质 verdict 在 review.md §5.5）、I-14-E（**按设计不接受**：授权源自 owner 裁定而非验收，明记不得"修"成 accepted）、I-14-D（顶层历史值，实已闭） |
| **未开工（零 attempt）** | **16** | I-07-E、I-10-A、I-11-B/C、I-12-A…E、I-13-A…C、I-16-A/B、I-17-A/B（其中 I-10-A 门已全开、即刻可派） |
| 目标① 8 在飞卡 | 8/8 已闭 | 全 accepted_scoped（§3.1） |
| 非 92 卡的在飞修卡（审计时点活跃） | 5+2 接续 | RF-RATCHET-FIX、RF-RATCHET-REST-A、RF-RATCHET-REST-B、CW-GATE-UNBLOCK-2、RF-STEP9-TRIAGE（CI 修序列，owner 已「同意」三外发动作）；审计期间 CW-GATE-UNBLOCK 与 RF-RATCHET-FIX 相继基建夭折 → 各起 -2 接续卡（§70/§71，前 attempt 原样入史） |
| owner 挂起项 | 5 | OQ-03（GATE 超时策略）、REM-25（124/150 选择）、B1 原卡状态回填、REM-80 的 31/31 正式追认、载体 countersign |
| 外部挂起项 | 3 | 函 B 信任根（P5-b 身份链全修）、INVEST-CORE 合入（invest-core owner+测试设计卡欠账）、三函真实送达（发不发归 owner） |

差距结论：仓内自主可推进面已近乎见底（①⑤达成、②实质达成），**剩余差距=16 张未开工卡（链式依赖）+ 登记欠账（§5）+ owner/外部闸**。目标"直至全部完成"尚未达成，但在轨、无失控迹象。

## §8 Unverified 清单（明示未核/不可核项）

1. 批 8/9 的 pre-push 门绿结果无记录，无法从文书直接核（DEV-2.1）。
2. 批 5 首轮 F401/BOM/宿主字面红态字节未入库，红→修差分不可 git 复原（FAB-4）。
3. T2-SIM-OPEN6-SEC ruling.md mtime（23:19）晚于引用其 sha 的 RESPONSES.md/§19（22:22/22:08）——内容哈希链自洽，时序属 UNVERIFIABLE（疑为事后 touch/批量还原）。
4. 2026-09-19/20 各 attempt 树共享 mtime 簇（09-20 15:46-48），亚日级开跑次序不可仅凭 mtime 证明。
5. REM-54「已提交」的 git 提交未复验（文件+哈希已验）；register 未引 sha。
6. F-REV-R5-03…08 逐条描述在 r5 复审载体内（五文书检索面外），逐条内容未复核。
7. 门文件内容哈希标签（cf09ade8/3df161a7/0d290326）为文书自述，本次只核内容事实未复算该三标签。
8. CI/GitHub run（#309-312 等）无网络不可核，采信文书归因。
9. 复审报告全文未由主审逐行重读（以 verdict 行+哈希钉+抽段方式核）。
10. I-00-A 的 changes_required"一项证据缺陷"未重新裁判。
11. OPEN-5#3/4/5 三条存疑标题未逐字读出（SA-CHAIN 以终格"已解除"核其闭）。
12. SA-DISC 的 10-attempt 六面细目以该员报告为准，主审只复核其中 pin/前缀/冻结时序三面。
13. I-07-D 的 F02/F03/F04 判决 raw 字节已被授权清理且无副本留存（父方 §72(3)），其判决不可重算（本审计员未尝试重算）。
14. B5 `boundary_verification.json` 记录的 `binding.json` 哈希与实测不符（§3.5），改动者/时点未定位（AUDIT-INTEGRITY 面在办）。
15. 批 8/9 门绿的 push log 本体未由本审计员读验（采信父方 §73 补账行的引用）。

## §9 方法与覆盖面统计

- 编制：主审 AUDIT-GOAL + 6 名独立评审 subagent（SA-PUSH/SA-REM/SA-DEFECT/GATE-DEP/CHAIN/DISC 分面并行，互不通气；主审对其最高严重度结论逐一独立复核后才采信——FAB-1/2/3、静默丢行、I-06-B 破门嫌疑均由主审亲测坐实，REM-62 一处评审间矛盾由主审裁定）。
- 覆盖：execution_runs 全部 140 attempt 目录枚举；92 卡逐卡状态普查；8 在飞卡全深核（哈希 8/8+前缀 2/2）；REM 25 行抽样+86 行普查+29 指针复核（100% 命中，1 钉例外=FAB-1）；推送 9 窗口 36 提交全验端点+计数；门拦事件 4 例根因档案+门文件全史；依赖表 40 卡+零破门 8 卡深核+等待表 16 卡；10 attempt 六面纪律抽样；指令 7 条全溯；存疑 22 条全枚举+6 条端到端；缺陷 ≈110 单位全台账。
- 边界：无网络（CI/外部回执不可核）；reviews\ 子树深部因权限拒绝未扫；本审计员只写本 attempt 目录，未改任何计划产物（audit 不实施、不代改）。
- 时点漂移声明：审计期间计划仍在推进（登记册由 §70 增至 §73、I-10-A 开派、CW-GATE-UNBLOCK/RF-RATCHET-FIX 接续、RESPONSES.md 勘误行落地）；本报告基准=2026-09-23 含 §73 在内的盘上状态，凡快照后变化均已标注。

## §10 REM-79 自查记录（checker=REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py，PYTHONIOENCODING=utf-8）

1. 工具身份：v1.2.0-correction2（stdlib-only，声明 never writes）。
2. 冻结语料复跑（rc 语义与 REM79 卡 verify_summary 冻结表一致）：pos_i14d_review_L349.md:4 与 pos_round76_original.md:4 各命中 1 条（2 violations across 4 files），neg_domain_lines.md / neg_no_marker_lines.md 零命中；exit=1（有违规）符合冻结预期。记录：`evidence/rem79_checker_corpus_run.txt`。
3. 本报告自扫：见下方 SELF-CHECK 记录（工具对 audit_report.md 的输出原样存 `evidence/rem79_selfcheck_report.txt`）。

SELF-CHECK（RUN 4 = 终稿扫描）：checker v1.2.0-correction2、PYTHONIOENCODING=utf-8 对本报告终稿 → **0 violation(s) across 1 file(s)，rc=0**。前序记录：RUN 1 冻结语料 = 2 violations/rc=1（与 REM79 卡冻结预期表一致，pos 样本各命中 1 条、neg 零命中）；RUN 2 本报告首稿 = 1 violation（L69 无域「全部」）→ 按带域措辞改写后 RUN 3 rc=0；RUN 4 插入本自检块后的终稿复扫结果即上行。四跑原始输出：`evidence/rem79_selfcheck_report.txt`。

---

## 独立审查员签名

- 独立审计员：**AUDIT-GOAL**（目标-进展对照审查员；owner 令派出；与 AUDIT-DESIGN/AUDIT-INTEGRITY 并列三员，各自独立）
- 签名载体 = 本报告 `audit_report.md` + 侧钉 `audit_report.md.sha256` + `evidence/` 21+ 份取证件
- 身份声明：本审计员全程对目标仓与计划目录**只读**；`implementer_signed=false`；本审计员**未**实施任何修复、**未**代改任何登记行、**未**授予任何验收；报告内一切验收语均系转录被审对象的既有 verdict 并附独立复核注记
- 日期：2026-09-23
