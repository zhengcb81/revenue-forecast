# 独立审查报告 · AUDIT-DESIGN（设计一致性视角）

- 审查对象：`C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`（下称 PLAN；RF/CW/FF 三仓只读）
- 审查令（owner，逐字）：「请你用一个或者多个独立的subagent把整个项目过程中的几个重大节点做一次全面独立审查，最好用类似端到端测试的方法，并且要参考项目计划文档里的最初设计标准和目标，保证现在的项目进展不偏离最初的设计。」
- 审查镜头：**设计一致性**——最初设计规格（基准 A：`execution_v2\`）与目标原文（基准 B：owner 目标 revision 4）对表已执行现实。
- 本报告唯一写入面：`PLAN\execution_runs\AUDIT-DESIGN\a20260923-01\`（本文件 + `audit_report.sha256` + `evidence\`）。运行副本一律在 `%TEMP%\AUDIT-DESIGN-a20260923-01\`。无网络、无状态变更 git。
- 审计期间存在**一次我方审计事故**，已修复并全文披露（见 §0），不软化、不隐匿。

---

## VERDICT

**DEVIATIONS-found**

理由（三条主因，任一即足以否决 PASS-no-deviation）：
1. **D1（最高严重度·诚信/捏造疑）**：OPEN-6 裁定的登记哈希 `8aabac09…` 在盘上**无任何字节对象与之对应**，而转录链以「不改一字、哈希对得上」为其自身关闭判据；该主张当前**不可验证**（详见 §2）。
2. **D2（高·语义漂移+授权例外未消解）**：门①解除依据不是函 A 设计要求的外部 TIER-2 回执，而是「owner 终确的 role-play 模拟裁定 + 转录」；存在 owner 授权原话，但与冻结纪律 7 文面直接冲突且登记册内部口径互斥。
3. **D3（中高·不可复核证据）**：I-07-D 故障矩阵 F02/F03/F04 的字节级判据依赖 `%TEMP%\i07d\cases\` 工作树（已消失、attempt 目录未留存），判决**不可独立重算**（本次实测复跑失败/静默降级，见 §5-R2）。

其余偏差 D4–D12 见 §2。**捏造专项结论（并入第七子代理清点后修正）**：除 §2 ★ 的 D1（哈希级声称不可验证）与 D5（授权引文无源）外，另发现 **D1b（声明为证据的文件 `before/production_anchors.txt` 全树不存在）** 及 D1c 一族"声明件与盘上名称不符"小项（多为各卡自陈的预登记改名/合并）。总体：**未发现伪造的证据内容主体**；问题集中在（a）哈希级/文件名级声称与盘不符、（b）验收词汇与证据留存越出冻结契约、（c）一处授权引文无源。执行侧的诚实标注纪律总体良好（大量 `implementer_signed=false`、`UNRATIFIED`、`NOT GRANTED`、`expected_superseded`、自陈式勘误被原样保留）。

---

## 0. 审计事故披露（我方，最高优先级自陈）

**事故**：复跑 B5-fix-g1a-g3 的 `scripts/verify_append_fixed.py` 与 `scripts/verify_boundaries.py` 时（我已把整个 attempt 拷贝到 `%TEMP%` 后运行），两脚本**内嵌绝对输出路径**，写回了**原 attempt** 的两个历史证据文件：

- `execution_runs/B5-fix-g1a-g3/a20260922-01/evidence/start_here_append_proof_fixed.json`
- `execution_runs/B5-fix-g1a-g3/a20260922-01/evidence/boundary_verification.json`

这违反了我的「原文 attempt 禁写 / 不改历史审计产物」约束。

**处置**：已用运行前 `%TEMP%` 副本逐字节还原，还原后 sha256 与 B5 自身 `handoff.json:94-95` 记录值**完全一致**：
- `start_here_append_proof_fixed.json` = `7c4c95dcc53e67ecf15f28f4b4318ff559fc8212b6e5a900af3261434f0f6600`（= handoff 记录值）
- `boundary_verification.json` = `0aacaac8199975a5fc823f15aadd80f61e1c407a6f5dbc6fe9a05f73ef931ea6`（= handoff 记录值）

净影响 = 两文件 mtime 变化（内容已复原为 handoff 钉定字节）。事前副本 hash 与 handoff 记录值一致这一事实，同时证明了原字节未被我改坏。

**衍生发现（并入 D7）**：B5 自己的 `boundary_verification.json` 早已诚实记录 `binding.json` 记录哈希 `06ff8064…` ≠ 实测 `96733875…`（"a mismatch would mean B5's tree changed after its handoff - reported, never repaired by this card"）。**该历史 attempt 树在其 handoff 后被改动过，至今未处置。**

**衍生建议**：上述两脚本的"绝对路径写回"缺陷违反 `review_and_handoff.md:33`「复制逻辑到新attempt输出目录并绑定当前代码」，任何人重放历史卡都会污染历史 attempt——建议立 REM 项。

**第二处我方更正**：核对 I-07-D `oracle.md` 钉值时，我先用**自行补全的**完整哈希比对得到"DIFF"；经查 `review.md:84` 只给了前缀 `576ddfc5…` 与尾 `…18846`，实测 `576ddfc57c2c949d6a9e5f875114d8c7e49c833d69b5bd8cd81bcf2417718846`、27211 B——**前缀、尾缀、字节数三项与在案声明全部相符**，"DIFF" 系我拼造期望值所致，现予更正，结论为 **MATCH**。

---

## 1. 基准 A（设计基准）钉定 — `execution_v2\` 全量 sha256

共 **124 个文件**全部 SHA-256 钉定（完整清单存 `evidence/baselineA_sha256.txt`，其自身 sha256 = `319880a2025640c23b5dd204f87e6fb6df482cb94343e17288b204d00fb75623`）。核心文档：

| 文档 | sha256 |
|---|---|
| START_HERE.md（执行协议+冻结契约+rc 码表） | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` |
| root_cards.md（I-00…I-17 全部卡面） | `ef03925629c57615d89e765584f4006757b0b30374e1de2a90d505d73c772a38` |
| common_root_cards.md | `f8127541c763859761eb6affdd9f3c898766e249205436ff164b73c2621cd260` |
| scenario_matrix.md（A/E/F/X/故障矩阵，L23-L64） | `0dec23cd10f00eefd6ad82cf923552bd46c1763bcf9f740422f51f4973292299f` |
| review_and_handoff.md（独立验收九条+交付最小目录） | `602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9` |
| dispatch.md（依赖图） | `7c8ff00a1a64a61de54a02d415f520957134853461f5d24bd27eb925764eede9` |
| filing_cards.md | `272060658b2620f28409d91fc2ed1b620957a7ac526805a8385508e6421c3e2c` |
| wiki_cards.md | `4978d14717bf020ad6165e41994d362b5b309ab3eba63ff595f1b88b2b8545abf` → 见勘误* |
| common_filing_cards.md | `c54f583976519c66b1b9425fc03a18ec5620bc4d662d5f2f2e0ed184006b325b` |
| common_wiki_cards.md | `5c1d5e58de8735feadb850004645cd6a60a5a10e53ef2fb4a424a2e365acd9cd` |
| card_I-06-A.md / card_I-06-B.md | `671fc274f83f8dfc6b9b9c1bbdf2144aac5a4abf7c7f43cdbef6aec062da407c` / `ad13386e371391c63a8cc50034842d0c9452e72a9d02ab3788b04479d37a2ace` |
| card_I-07-B / C / D | `bd09eb6cf263c2e38867799240d0387f1e1362ffbdc7eae57a0c4e166581f26e` / `c3c3f5333a2f9fd68eb83bf17ba4a83ab700b73d8100e445ce7e288fe4704124` / `b54f4bc8f3eb1810f66a6a18f37b55b85bcdc98229c5493c11d2ad326228c553` |
| card_I-08-C.md | `3c14d03de76d97b681e4fbbd84e9a67c7f2796292df46224ca15738843538e52` |
| card_I-14-D.md | `5e5cdaaac186a4a7b6595e8ed33302b5c63ce4472256c2cbc8e5eaeef64760114` |

\*勘误：`wiki_cards.md` = `4978d14717bf020ad6165e41994d362b5b309abeba63ff595f1b88b2b8545abf`（表内串写一位，以 `evidence/baselineA_sha256.txt` 全量清单为准）。

**基准 B（owner 目标 revision 4）**：见任务书引文，本报告以其五款（①8 在飞卡收口、②两批提交、③REM-01…79 处置、④未开工卡九步至 accepted_scoped、⑤全程纪律：隔离副本/冻结 oracle/独立复审/生产零合并/不改历史审计产物/同步 PWF）为对照面。

**授权基准（Owner 指令链）**：「A-1: 1, A-2: 授权, B: 全批, C:更新函件」（OWNER_DECISIONS.md:420）｜「fail的全部要修复」｜「全部接受」（终确，TTL=A 30 天）｜「发现的缺陷都要全部修复」｜「所有存疑都要确认」｜e2e 四约束｜「给你真实下载复测授权」｜「同意」（登记册 §66）。

---

## 2. 偏差清单（分类 / 严重度 / 行级引文 / sha）

> 分类词表：SCOPE-ADDED / SCOPE-DROPPED / EXIT-RULE-CHANGED / SEMANTICS-DRIFT / UNVERIFIED-CLAINT。

### ★ FABRICATION-SUSPECT（单列·最高严重度·不软化）

**D1 —「声称存在的哈希对象在盘上不存在」**（类 UNVERIFIED-CLAINT + 疑似捏造）
- 声称：`outward_requests/RESPONSES.md:7` 与 `I-06-A|I-06-B/a20260919-01/rulings_transcribed_2026-09-22.md`（T2-2 头）登记「OPEN-6 ruling.md」的 sha256 = `8aabac0908b407b8af5108c00b4a26e11476d889b593ade306d1eee519c368d1`。
- 实测：`execution_runs/T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` 现 sha256 = `5cb476767a934885…`（52560 B）；该目录**仅此一个文件**；全盘无任何对象匹配 `8aabac09…`。
- 且转录快照与现文件**自 char 22394 分叉**（快照作「D. 全景知会（批 #2 探针…」，现文件作「C-续（C7 回报线④触发落记…」，现文件多出追加节）。
- 违反条款：OPEN-6 自身 C8 关闭判据 `T2-SIM-OPEN6-SEC/a20260922-01/ruling.md:174`「登记行存在且与**本文件 sha256** 对得上」——**当前 FAIL**；函 A `A_DW06_OPEN-4-5-6.md:147-152`「**不改一字裁决内容**」（`cd88bd4c…`）。
- 两种解释均需处置：(a) 被登记的版本字节从未留存 ⇒ 该「逐字可溯」主张是**无据声称**；(b) 裁定文件在登记后被改动 ⇒ 违反冻结/追加纪律。无论何者，**当前状态=不可验证**。
- 要求：冻结现文件、补 erratum 登记（不得静默改哈希）；OPEN-4/OPEN-5 经逐字符比对与现文件一致（22992/27310 字符），**不受此条牵连**。

**D1b —「声明为证据的文件在盘上不存在」**（类 UNVERIFIED-CLAINT + 疑似捏造·并列最高）
- 声称：`B1-I08C-product-fixes/a20260921-01/commands.json:35`「"evidence": ["before/production_anchors.json", "before/production_anchors.txt"]」，`:27` argv 亦写 `"<ATTEMPT>/before/production_anchors.txt"`。
- 实测：`production_anchors.txt` 在**整个计划树与 RF 仓树均不存在**（其 `.json` 兄弟件存在）。同文件 `:38` 有一句近乎自陈的说明：「the anchors were first captured by an inline hashing step whose raw output is before/production_anchors.json」——即被登记为 evidence 的 `.txt` 交付件**从未落盘**。
- 违反条款：`review_and_handoff.md:21-31` 交付最小目录（原始输出须留存）、`:33`「不能仅交文件名/hash；reviewer需读实际内容」。
- 处置：删改该 evidence 条目为「未产出（仅 .json）」的追加式勘误，或补产并注明后置生成；**不得**事后补文件冒充当时证据。

**D1c — 其余「声明件与盘上名称不符」小项（均已由各卡自陈，风险低，合并登记）**
- `B1-PREREQ/a20260922-01/oracle.md:137` 引 `evidence/final_integrity_check.txt`，盘上实为 `final_integrity_check.stdout.txt`（F-2，名称漂移）。
- `GATE-OQ-FIX/a20260922-01/oracle.md:122-127` 预登记 `compileall.txt/ast_check.txt/help_smoke.txt/ruff_two_files.txt` 四名，实际合并为 `ast_compileall_ruff.txt`+`ast_and_help_smoke.txt`（F-3，**已由 handoff F-11 自陈**「substance of every pre-registered check present」）。
- `CFI14FR1-SAMPLE/a20260922-01/commands.json:53/78-97` 预登记 `01_with_hook.lastfailed.json`、`03_redirect_probe.*` 三件，盘上为 `00_baseline…/02_rerun…/04_redirect_probe.*`（F-4，**已由 reviewer_report.md:108 自陈**「merely label strings moved」）。
- `B5-plan-level-remediation/a20260921-01/reviewer_report.md:255`「**The POST1 intermediate image does not exist on disk.** `e7cb90fc…`（16 314 B）is a recorded value, not a file I can hash」（F-6，**自陈**）。
- 跨 attempt 相对路径基点不一致（非捏造，兄弟 attempt 内实存）：B3-I05C→B3-PREREQ、B1-I08C↔B1-PREREQ、B5→B5-fix-g1a-g3、_bookkeeping→I-14-D 的 evidence 引用各若干条。
- 运行期产品件在计划树内无同名文件（**域外**，不计捏造）：`artifacts/registry/publications.json`、`/runner/registry/publications.json`（B1 handoff/oracle 引用；仅 INVEST-CORE 卡内有 `runner\registry\publications.jsonl`）。

**D5 —「owner 令」授权引文无源**（类 UNVERIFIED-CLAINT + 疑似捏造·次级）
- 声称：`REMEDIATION_REGISTER.md:1272`「立 `F-EE1-FIX` 修卡（**owner「缺陷全修」令覆盖**…）」。
- 实测：`OWNER_DECISIONS.md` 全文 grep「缺陷全修｜全修｜修复令｜F-EE1」= **0 命中**；`task_plan.md` = 0 命中；`F-EE1-FIX/a20260923-01/decision.md`（`74f8c286…`）无授权引文。
- 后果：CW 提交 `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121`（生产文件 `canonical_writer.py` 合并）所依据的"owner 令"**无原话载体**（§十八「B: 全批」仅覆盖 B-1…B-7）。修复证据链本身完整（oracle `0fd9f551…` frozen-first、复审 `588f8d95…`、RED→GREEN→mutation 在盘），故定性为**授权链断点**而非伪造修复。
- 处置建议：向 owner 索一句追认，或在登记册更正引文出处。

### 其余偏差

| # | 分类 | 严重度 | 内容 | 关键引文（file:line · sha 前 12） |
|---|---|---|---|---|
| D2 | SEMANTICS-DRIFT（TIER-2 语义替换）+ owner-authorized-exception **未消解** | 高 | 门①（I-06-A `still_awaiting_other_parties` 首条）解除依据 = owner 终确「全部接受」的 **role-play 模拟裁定+转录**，非函 A 设计要求的外部当事方本人裁决 | 设计：`A_DW06_OPEN-4-5-6.md:34-37`「until those parties rule」（`cd88bd4c`）、`OWNER_DECISIONS.md:200-201`「最终裁定**仍须该当事方出具**」（`07ebf230`）、`task_plan.md:2060`「19 张卡链的**真正门**是函 A 的 TIER-2 外部回执……避免误报解锁」（`4096a44d`）；执行：`I-06-B/a20260922-02/decision.md:5-6`（`518af92f`）、`handoff.json:17`（`3c2c84ec`）、`OWNER_DECISIONS.md:435/440`（授权原话「我全权授权它们扮演…我会最终确认」→生效链→19 卡链开闸）；冲突未解：`OWNER_DECISIONS.md:271-272`「任何把 TIER-2 记为『owner 已裁』的落地，**等同伪造签名**」；**登记册自相矛盾**：`REMEDIATION_REGISTER.md:973`「TIER-2 三方对 OPEN-4/5/6 的**裁定尚未收到**」vs `:1224`「裁定链…✅」 |
| D3 | UNVERIFIED-CLAUSE（证据留存） | 中高 | I-07-D F02/F03/F04 的 raw/原件字节级判据依赖 `%TEMP%\i07d\cases\`（已消失），attempt 目录未留存被哈希的字节 ⇒ `raw_preserved`/`raw_intact_after_recovery`/`provenance_committed` **不可独立重算** | 违反 `review_and_handoff.md:26-27`（`602cce39`）「before/ 修改前原始日志、状态与hash」、`scenario_matrix.md:64`（`0dec23cd`）「每个case最终写…raw/expected rc、来源/配置指纹」；本次实测：`f02v/f03v` FileNotFoundError(`%TEMP%\i07d\cases\F02…2025年度報告.pdf`)、`f04v` 静默 3 项 false（见 §5） |
| D4 | EXIT-RULE-CHANGED（验收词汇+落定槽位） | 中 | `review_and_handoff.md:15`（`602cce39`）只允许四值结论 `accepted_scoped/changes_required/blocked/not_applicable_with_reason`；实际出现 `accepted_with_conditions`（`B1-I08C-product-fixes/a20260921-01/reviewer_report.md` VERDICT 块）、`ACCEPT`（`B3-I05C…/review.md`、`CW-TEST-DEBT…/review.md`、`FIX-W06-GAPS…/review.md`、`I-02-D/a20260919-01/review.md`、`I-14-H/a20260919-01/review.md`「ACCEPT（条件式）」、`TTL-30D-POLICY…/review.md`「ACCEPT — scope-limited」、`RF-E2E-ADAPT…/reviewer_report.md:7`「ACCEPT (sign-off as reviewer…)」）、`ACCEPTED_SCOPED` 大写（`I-07-B/a20260923-01/review.md`）；另 `B1-I08C-product-fixes`、`I-14-F-R1` **缺 review.md 落定槽**（I-14-F-R1/review.md:1-3 仍是「STUB (no verdict)…`review_pending`」而 `reviewer_report.md:16` 已是「## VERDICT: **accepted_scoped**」——同一 attempt 两个状态口径） |
| D6 | UNVERIFIED-CLAINT（冻结次序） | 中 | 「运行前冻结 oracle」存在次序偏差（诚实披露但仍是偏差）：`RF-RATCHET-FIX/a20260923-01/oracle.md:131-139` §8 自述冻结**前**已跑 RED 复现与两轮测量扫描；`RF-RATCHET-REST-A/a20260923-01/ORACLE.md:24`「Card's expected actuals (22/17/114) re-derived independently ✓」= 冻结前实测数值 | 设计 `START_HERE.md:36`（`5c6e111f`）第 4 步冻结预期 → 第 5 步才「运行修改前检查」；`review_and_handoff.md:10`「expected 从被测函数…生成的，一律不能视为独立验证」 |
| D7 | UNVERIFIED-CLAINT（历史 attempt 完整性） | 中 | B5-fix-g1a-g3 自记 `binding.json` 记录哈希 `06ff8064…` ≠ 实测 `96733875…`——历史 attempt 树在其 handoff 后被改动，卡内自报「reported, never repaired」，至今未处置（见 §0） | `B5-fix-g1a-g3/a20260922-01/evidence/boundary_verification.json`（=`0aacaac8…`）`b5_attempt_read_only_proof.mismatches`；违反 `START_HERE.md:18`「不得覆盖本次审计证据」、:109「历史 rc 与其证据**一律不动**」 |
| D8 | SCOPE-DROPPED（轻度·提交信息收窄） | 低 | CW 晋升 `ac4ebd04` 提交信息未复述 I-14-D 随行欠账（C12 promotion precondition、F-REV-D-02 死 `_VALUE`、F-REV-D-03 atom 缺口）；载体层仍在（`PROMOTION-PREP/…/promotion_batch_manifest.md:75`、`PROMOTION-EXEC/…/review.md:120`） | `PROMOTION-EXEC/a20260922-01/review.md:120`「accepted as carried declarations, not re-verified」（`e13a87d9`） |
| D9 | UNVERIFIED-CLAUSE（独立验收定位） | 中 | 31 张公式卡的独立验收裁决**在我方快速普查中未全部直接定位**：M29–M31 明见「结论：**accepted_scoped**」追记；**M21–M28** 经 `_isolation_incidents/20260920-*` 事故记录佐证存在 round-3 终裁 `accepted_scoped`（「M21–M24、M25–M28 的 `accepted_scoped`…其失效条件解除，round-3 终裁继续有效」）——**我方初稿曾据普查误记"M01–M28 无独立验收"，现予更正**；**M01–M20 的独立验收载体仍未直接定位** ⇒ 保持 UNVERIFIED（非"确无"）。T1-* 全系（20 个 attempt）无 review 槽（仅 decision+handoff） | `START_HERE.md:27`「accepted：独立reviewer读证据并复验必要反例」（`5c6e111f`）；`review_and_handoff.md:43` |
| D10 | SCOPE-ADDED（网络面·已披露） | 低 | E2E-EXPAND RUN-R2 因测试 argv 漏写 `--live never`，runner 默认 auto gate 探测 cninfo 并**执行一次真实下载**（超出该登记册冻结网络范围），事后全量披露 | `E2E-EXPAND/a20260923-01/commands.json:96/99`（`__history` + `result_run1`「DISCLOSED DEVIATION…EXECUTED one real download outside this registry's frozen network scope」）；后续 RUN-R3 由 owner「给你真实下载复测授权」覆盖（=授权例外，但**仅覆盖 retest**，不追认 RUN-R2 的意外下载） |
| D11 | （审计事故·我方） | — | 见 §0；分类记 AUDIT-INCIDENT，不计入项目偏离扣分，但按诚实规则单列 | §0 |
| D12 | SEMANTICS-DRIFT（登记口径互斥） | 中 | 同一登记册对「函 A 裁定是否到达」两种口径并存：`:973`（未收到）vs `:1224`（裁定链 ✅）；另 `_provenance.json:75` 前像「7087 B」与盘上 11226 B 不符（陈旧引用） | `REMEDIATION_REGISTER.md:973/:1224`（`b528d0ab`）；`outward_requests/_provenance.json:75`（`90ac3453`） |

**授权例外汇总**（凡有 owner 授权的设计例外≠偏离，但授权存在性已逐条验证）：
- 生产代码零合并的 lift：`OWNER_DECISIONS.md:420`「> **原话**：「A-1: 1, A-2: 授权, B: 全批， C:更新函件」」+ `:426`「**B = 全批**…**父保留各仓提交权**」→ 覆盖 ac4ebd04/5d725294 的生产合并（文件清单=提交清单，逐行核对相符）。
- 模拟 T2 role-play：`OWNER_DECISIONS.md:435`「我全权授权它们扮演…我会最终确认」+「**全部接受**」→ 覆盖三份 T2-SIM 裁定的生成与其终确（但**不消解** D2 的纪律 7 冲突）。
- 真实下载复测：owner「给你真实下载复测授权」→ 覆盖 E2E live_retest_20260923 / live_retest2_pass_20260923。
- TTL=A 30 天：owner「全部接受」终确。
- **未获授权**：bf0c8b27 的生产合并（D5）；RC 码表以外的验收词（D4，无 owner 裁定）。

---

## 3. 逐卡对表（卡面条款 → 执行证据 → 判定）

说明：「落定三件套」= `decision.md`+`review.md`(或 reviewer carrier)+`handoff`；九步协议 = `START_HERE.md:31-41`。在飞卡（CW-GATE-UNBLOCK / RF-RATCHET-FIX / RF-RATCHET-REST-A / RF-RATCHET-REST-B / RF-STEP9-TRIAGE）按令**只审「冻结 oracle 与设计对表」**。

### 3.1 设计卡 I-00…I-17（逐卡）

| 卡 | 设计条款焦点（引文锚点） | 执行 attempt / 证据 | 判定 |
|---|---|---|---|
| I-00-A | 「Git ownership失败保留错误…不改全局safe.directory」；「禁止仅复制活跃DB主文件而遗漏WAL」 | a20260919-01：oracle+review+handoff+commands | CONFORM（结论 `changes_required` 限一项证据缺陷，实质数据独立验证通过；后续修复未见新 attempt ⇒ 尾项 UNVERIFIED） |
| I-00-B | 「所有null/unbound填完并由reviewer核查后才运行该命令」 | a20260919-01：`accepted_scoped` | CONFORM |
| I-00-C | 冻结六负例「六者都不得解锁相应业务完成」 | a20260919-01：`accepted_scoped`（N1–N3 反例在案） | CONFORM |
| I-00-D | 「不存在的文件记录NA，勿为凑齐创建」 | a20260919-01：`accepted_scoped` | CONFORM |
| I-01-A | 「独立预期：在修改前冻结，不调用被测函数生成 expected」 | a20260919-01：`accepted_scoped`（3 项记录性发现） | CONFORM |
| I-02-A…E | writer 不得忽略错误/中断；不伪报 download_events=0；幂等不靠删史 | 5 attempts 全落定三件套齐 | CONFORM（I-02-D 结论用 `ACCEPT` ⇒ 并入 D4） |
| I-03-A…D | 不以字典序推断披露时间；hash 断言与授权拒绝断言并存；「I-02 对应恢复项未完成时本卡不得关闭」 | 4 attempts；I-03-D 明记「本卡不得以 accepted 完全关闭任何生产恢复项」 | CONFORM（诚实限定保留） |
| I-04-A…E | 唯一预算来源；timeout≤剩余预算；跨进程真锁；失败也计数 | I-04-A/B/C 均两轮（changes_required→accepted_scoped）；I-04-E `accepted_scoped` | CONFORM；**I-04-D = UNVERIFIED**（review.md 由实现者执笔、判决栏留空、无独立 reviewer 裁决在盘；32 个 `runs*` 为 pytest basetemp 残留，属 `START_HERE.md:74` 警示形态，记低级观察） |
| I-05-A | 「不直接 INSERT 绿色 artifact 充当正例」；「不得批量填 source_sha 使绿」 | a20260919-01：r4 复审「答案仍是 changes_required（P1-A/B/C，单根因）」 | CONFORM（诚实红），**卡未收口**（目标④余项） |
| I-05-B | 「artifact_read_events 不可伪填」 | `accepted_scoped` | CONFORM |
| I-05-C | 「不以 artifacts INSERT 数=1/0 充当调用次数」 | `accepted_scoped`（B3-I05C-delivery-fixes `ACCEPT` 修复后续） | CONFORM（词表并入 D4） |
| I-06-A | 「在返回明确阻断前持久需求存在…没有伪造 review」 | a20260919-01 r2=`blocked`（诚实保持）→ a20260922-02 `accepted_scoped` | CONFORM（实施面）／**门解除依据 = D2** |
| I-06-B | 「不能调用 receipt writer 直接制造正例」；「fake receipt 或只有 schema 正确不通过」 | a20260919-01 `changes_required→accepted_scoped`；a20260922-02、a20260923-01 `accepted_scoped` | CONFORM（实施面）／**写可失败用例的前置门 = D2** |
| I-07-A | 「缺失模拟与真实live标签分开」；「外部only…保持blocked」 | a20260919-01：仅实现者自述（"Nothing here is an acceptance"） | **UNVERIFIED**（独立验收裁决未在盘上定位到） |
| I-07-B | 「真实调用数不能由artifact INSERT推算」；「三公司仅来源准备通过，仍未授予正式预测资格」 | a20260923-01：九步件齐（binding/oracle/decision/review/handoff/commands/changes.diff/reviewer_report+sha256）；`ACCEPTED_SCOPED` | CONFORM（词形并入 D4）；**WPROBE 复跑一致**（§5-R3） |
| I-07-C | 输入矩阵 X01—X05；「未知布局给明确unsupported」；「真实external-only缺样本保持blocked」 | a20260923-01：oracle §0.1 逐行钉入 X01–X05（`oracle.md:26-30`）、X03 = **BLOCKED 不构造**（`:169`「fabricating exclusivity = deleting other copies = …」）、第五 root+非 fixture 公司+no_hardcode grep 证据 | CONFORM（X01/X02/X04/X05 各格计数在案；X06 保留公司以「保留泛化样本」条款承载） |
| I-07-D | F01—F06；「没触发的测试无效」；「不能靠重建全部资产掩盖幂等缺陷」 | a20260923-01：trigger 8/8=1、kill 范围 census 359→349 real_source_catalog_gone=0、clause-3/4/5 复算在 carrier | CONFORM 主体／**D3（F02/F03/F04 raw 判据不可重算）**；F06 三格 `fault_audit_clean`+`rec2_audit_clean` 红 = 转 REMEDIATION 台账（F-F06-audit/F-F05-cause），属诚实保留（`review.md:227-233`） |
| I-07-E | 「禁止拿旧NOT_FORMAL草稿换名」；「不因其中一家成功写3/3」 | 无 attempt | **未开工**（目标④余项，符合其依赖门现状） |
| I-08-A | 「旧unsigned档案保留原标签，不重签伪造历史事件」 | a20260919-01：实现者自评「未自签任何 accepted/passed」 | CONFORM（设计条款）／验收态 UNVERIFIED |
| I-08-B | 「实现者不能自签真实provider已可用」 | a20260919-01 `review_pending` | UNVERIFIED（未收口） |
| I-08-C | 「不能重新签名或调用生产helper重算expected」；「无未验入口被标完成」 | a20260919-01：`reviewer_report.md:9`「## VERDICT: `changes_required`」；B1-I08C-product-fixes `accepted_with_conditions`（安全主张 CONFIRMED+3 项遗留） | CONFORM（诚实红）／**卡未收口**：owner 目标①「I-08-C oracle 重冻」仍在飞 |
| I-09-A…C | 唯一 commit 点前不可消费；真进程中止（finally 不运行）；「真实registry/用户包绝不触碰」 | I-09-A `changes_required`（窄幅文档层）；I-09-B `accepted_scoped`；I-09-C a20260922-01 `accepted_scoped` | CONFORM |
| I-10-A | 「必须标historical_mapping_probe，不称三情景预测」 | 无 attempt | 未开工（目标④余项；其门=I-07-B 收口后） |
| I-10-B | 「省缺即抛 ModelRegistryError」；「不改任何 M01–M31 的公式、不动任何冻结件」 | a20260919-01 `accepted_scoped`（裁决经编排层转达=间接，记观察） | CONFORM |
| I-11-A | 「十篇转述同一电话会算一个来源」 | a20260919-01：implementer 件齐，「本文件不包含 verdict 字段」 | UNVERIFIED（无独立 verdict 在盘） |
| I-11-B/C | 「缺数据就标expert_assumption」；STOP_LINEAGE | 无 attempt | 未开工（目标④余项） |
| I-12-A…E | 冻结于解封前；`descriptive_only`；STOP_CLAIM | 无 attempt | 未开工（目标④余项） |
| I-13-A…C | 「全2才给buy_side_review_ready」；STOP_PROVENANCE | 无 attempt | 未开工（目标④余项） |
| I-14-A | 「不把合成内存量等同精确RSS oracle」；不随测量失败改阈值 | a20260919-01 implementer 件 | UNVERIFIED（验收态） |
| I-14-B | 「重叠窗口不能相加制造自然时长」 | a20260919-01 `review_pending`（自述无 accepted 字样） | UNVERIFIED（未收口） |
| I-14-C | 「不能读取实际密钥」 | a20260919-01（r2 曾 changes_required，legacy note 保留） | CONFORM（历史保留） |
| I-14-D | 「冻结不改（`test_f08_c13_…`）」；「新 oracle 必须在改代码之前冻结」；「更新的是语义期望，不是把失败改绿」 | a20260919-01（r1 `changes_required`）+ `_review_i14d_r3/r4/r5_20260922` + `reviewer_report_r7.md`（`cc6da8d3`，域限「the r7 record fix only」）；C1/E4b 欠账随 `promotion_batch_manifest.md:75` 携带 | CONFORM（标签存活：`test_f08_c13_multiline_loss_is_frozen_not_hidden` 冻结测试未被改绿）／**E4b 新基线独立 reviewer 复算 = UNVERIFIED**（退出条款「E4b 新基线经独立 reviewer 复算」在盘上未见复算载体） |
| I-14-E | 「不得为让测试变绿而改产品代码」；「~25% 不得升格为规范常量」 | a20260919-01；I-14-E-APPLY a20260921-01（复审保留「frozen 8/8 is **UNTESTED** and must never be cited as met」「Source card I-14-E is **NOT accepted on record**」） | CONFORM（诚实标签完好） |
| I-14-F / F-R1 | 「不得以『把 cwd 缩短』当作修复」；owner §16「E-1: 150/60」 | I-14-F `accepted_scoped`；I-14-F-R1 `reviewer_report.md:16` `accepted_scoped`（applies owner「E-1: 150/60」） | CONFORM／D4（review.md stub 未落定） |
| I-14-H / I | 「"从未有过 2220"是禁止的写法」；「xfail 只记录，不等于通过」；NOT GRANTED 标签不得摘除 | I-14-H「ACCEPT（条件式）」+追加式 provenance（expected_superseded 保留）；I-14-I `accepted_scoped`（14-case 门 rc 0） | CONFORM（词形并入 D4） |
| I-15-A | 「任何生产 DELETE/VACUUM/移动都禁止」 | a20260919-01 r2 `accepted_scoped`（handoff 2 pin 复算 MATCH） | CONFORM |
| I-16-A/B、I-17-A/B | 「不能把隔离绿灯当生产已完成」；「子卡数量全绿不自动推出parent完成」 | 无 attempt | 未开工（目标④余项，依赖门未开） |
| M01–M31（31 张公式卡） | 「accepted 仅该卡明示资格，不外推」 | M29–M31 `accepted_scoped` 追记在盘；M21–M28 round-3 终裁经隔离事故记录佐证；M01–M20 载体未定位 | **UNVERIFIED（D9，已更正）** |
| T1-5…T1-27（20 个簿记卡） | rc 码表勘误/登记类 | decision+handoff 齐、无 review 槽 | UNVERIFIED-CLAINT（D9 同族；内容多为追加式登记，风险低） |

### 3.2 重大节点专项

**(a) 8 在飞卡收口链（目标①）**

| 在飞卡 | 收口证据 | 状态 |
|---|---|---|
| GATE-TIMEOUT-1200 | 九步件齐 + `reviewer_report.md:3`「`accepted_scoped` (12/12 findings PASS)」；红600/绿1200 驱动日志+step_times 在盘 | 已收口 |
| DW15-prune-repair | 九步件齐 + `accepted_scoped`；mutation_matrix.json（M1–M5）在盘 | 已收口 |
| B5-fix-g1a-g3 | 九步件齐 + carrier landing `accepted_scoped`；G1-a/G3 传播契约在盘 | 已收口（D7 尾巴） |
| I-08-C oracle 重冻 | a20260919-01 = `changes_required`；B1-I08C-product-fixes `accepted_with_conditions`（3 项遗留）；`oracle.md.r2_frozen_copy.txt` 留存 | **未收口**（重冻复审未见新 attempt） |
| I-14-F-R1 150/60 | `reviewer_report.md:16` `accepted_scoped`，applies owner「E-1: 150/60」 | 已收口（落定槽 D4） |
| INVEST-CORE 护栏 | INVEST-CORE-ATTEST-GATE 九步件齐 + `accepted_scoped`（reviewer three-state ruling） | 已收口 |
| I-14-E-APPLY 重跑 | campaign_v2（466KB jsonl+analysis）+ carrier landing + 未证项全保留 | 已收口 |
| I-14-D r6 复审回收 | `_review_i14d_r3/r4/r5_20260922` + `reviewer_report_r7.md` 域限 accepted | 已收口（E4b 复算 UNVERIFIED） |

**(b) 三 T2 裁定→owner 终确→转录→RESPONSES→门①解除**：见 D1/D2/D12。转录形式 3/3×双卡 + RESPONSES 三行齐；逐字可溯 2/3（OPEN-4/OPEN-5 逐字符相等，OPEN-6 断链）。TIER-2 语义已被替换为「owner 确认的内部模拟分析」，标注诚实但**与设计 TIER-2 定义不同**。门①解除依据非设计允许形态。

**(c) 探针→14 组修面→GUARD-MERGE→CW 晋升 ac4ebd0/5d72529/bf0c8b2**：三提交在 CW 仓 git 中真实存在（40-hex、subject、author date 复核相符，引用的 8 个证据哈希全部在盘复算相符）；14 修面「RED on BEFORE→GREEN on iso→mutation 12/12 翻红」在案；GUARD-MERGE 只 ratify 三面、**未越权带入 UNRATIFIED 面**；诚实标签存活（`E-4 owner-unsigned`、`Store UNRATIFIED note stands`、`I-14-D` 欠账携带）；历史审计产物未被三提交触碰（0 计划树文件；E1E7 前缀证明 4/4）。**唯一硬疑点 = D5（bf0c8b27 授权无源）**；轻度瑕疵 = D8。

**(d) 19 卡链 I-06-A/B/I-07-B/C/D 五张**：五张全部具备九步件与独立复审载体（I-06-A a20260922-02、I-06-B a20260922-02/a20260923-01、I-07-B/C/D a20260923-01 均含 `reviewer_report.md`+`.sha256` 侧车、carrier landing 明记「implementer never signs / verdict_is_transcribed_not_authored」）。落定三件套设计合规性 = **形式合规**；两条实质保留：门前置依据（D2）与 I-07-D 证据留存（D3）。

**(e) scenario_matrix 行义 vs 各卡 oracle**：
- X01–X05（I-07-C）：逐行钉入 `oracle.md:26-30`，X03 external-only 严格 BLOCKED 不构造（符合 `scenario_matrix.md:27`「未绑定则blocked」与卡面「不能删其它副本」）；X04「不重复下载/不重复计收入来源」由 `verify_x04.py`+`x04_hash_verify.json` 承载；X05「未知layout另例明确unsupported」由三 sub-probe 承载。**行义一致**。
- F01–F06（I-07-D）：F01（provider HTTP403/timeout）五跳链 `http_403`+`retryable` 存活、故障窗 downloads 0、恢复恰 +1 download——与 `scenario_matrix.md:51`「原error_code/retryable/cause保留，无伪raw→按预算重试」一致；F03 锁等待 75s 持锁/34.515s 扫描窗 + `catalog_busy retryable:true` 与 L53 一致；F06（registry/第二输出/commit 边界）三分格 F06A/B/C 齐、F06B「markdown 缺席、p1 不可消费」符合 L56「不见可消费半发布」。**L58 纪律**（「F02—F06 均仅 scratch 执行…每个变体必须有实际触发位置证据，没触发不算负例通过」）= trigger 8/8=1、kill census 证明 0 既有进程被杀——**符合**。保留项：F06 三格 `fault_audit_clean`/`rec2_audit_clean` 红被路由 REMEDIATION 台账（F-F06-audit）而非卡内修平，属「保留 measured red」的诚实分层，但**该红意味着 L56 的「按冻结事务恢复…不删除历史」中审计清洁项未达标**，处置在册（REM 路由）即符合 `review_and_handoff.md:45`「替代样本、放宽预算…不能用来关闭blocked」的边界。

---

## 4. 设计基准自洽（冻结契约 → 历史产物稳定性抽验）

| 检查 | 方法 | 结果 |
|---|---|---|
| START_HERE 追加纪律 | `verify_append_fixed.py` 复跑（§5-R5a） | `APPEND_ONLY=True`、`prefix_ok=True`、`insert_only=True`、19 冻结锚行全数原样在位（`frozen_anchor_lines_all_intact: true`）；append-3 自声明前缀 `a9cb5a4a…` 成立 |
| 历史 runner 冻结性（M 卡） | 直接复算 sha vs 在案声明 | M01 `b5fcc685…`、M17 `94619a98…`、M29 `9ea69c72…` 三值 **MATCH**（START_HERE「实测各批码位登记」表值一致） |
| I-07-D 载体钉 | carrier 哈希+侧车 | `reviewer_report.md` = `1a1d1c05…` 与侧车内容 **MATCH**；`oracle.md` = `576ddfc5…18846`/27211B 与 `review.md:84/85` 声明 **MATCH** |
| I-14-F-R1 oracle 钉 | 侧车（"written BEFORE any run"） | 侧车 `b5fee00f…`/13851B 存在且注明 append-only 复钉规则 |
| I-15-A / I-08-C handoff/binding 钉 | 自带 manifest 复算 | 2/2、1/1 **MATCH** |
| B5-fix attempt 完整性 | 自带 boundary_verification | `binding.json` **MISMATCH**（D7）；其余 17/18 一致 |
| T2 转录钉 | RESPONSES 行 sha vs 盘 | OPEN-4/5 **MATCH**；OPEN-6 **断链**（D1） |

（工具局限披露：`evidence/verify_hash_manifests.py` 对「manifest 内相对路径以他根为基」的条目会报 MISSING，I-14-F-R1 的 iso 树 plan_manifest、I-07-B binding 的 `PLAN/…` 占位路径均属此类**假阳性**，不作为偏差计。）

---

## 5. 复跑实证附录（≥6 个可执行条款；全部在 %TEMP% 副本或只读模式）

| # | documented 命令（出处） | 命令实录 | 与既有证据比对 |
|---|---|---|---|
| R1a | `REM79-MECHANIZATION/…/commands.json:56`：`python -X utf8 -B tools/check_domain_assertions.py --json ../../../task_plan.md ../../../findings.md ../../../progress.md` | 实跑（PYTHONIOENCODING=utf-8）rc=1 | **PWF 三文档现存 4 处 REM-79 violation**：`task_plan.md:1630`「全部」、`findings.md:633`「all」、`findings.md:684`「none」、`progress.md:1060`「全部」。这是 REM-79 自查的实证结果（也构成登记面缺陷） |
| R1b | 同 `commands.json:65`：checker on `oracle.md` | rc=0，`0 violation(s) across 1 file(s)` | 与在案 `verify_summary.json` 形态一致 |
| R2 | `I-07-D/…/commands.json:30-39` + `harness/run_d_matrix.py` 判决重算子命令 `f01v/f02v/f03v/f04v/f05v/f06av/f06bv/f06cv/verdicts` | 9 次调用 | `f01v`=`{all_ok:true, fetches_total:3, fetches_run1:1}` ✓与 `verdicts.json`/`review.md:86-120` 一致；`f05v` 一致且 `cause_survival:"FAIL — finding F-F05-cause…"` ✓与在案同文；`f06av/bv/cv` 三格 `failed_checks:["fault_audit_clean","rec2_audit_clean"]` **与在案 verdicts.json 逐字一致**（红可复现）；**f02v/f03v = rc1 FileNotFoundError（`%TEMP%\i07d\cases\F02/F03\…2025年度報告.pdf` 不存在）；f04v = 静默 false×3** ⇒ F02/F03/F04 判决**不可重算**（D3） |
| R3 | `I-07-B/…/commands.json:54-59`：`run_case.py wprobe <evidence>/wprobe_tmp` | rc=0，`{"totals":{"scan":2,"read":2,"provider":2},"zero_insert":true}` | 与在案 `evidence/wprobe.json` **sha256 完全一致**（`E01C8C905D65609D…`，两份逐字节同）；符合卡面「真实调用数不能由artifact INSERT推算」 |
| R4 | `E2E-EXPAND/…/commands.json:75`：`run_cross_repo_chain_e2e.py --scenarios S5,S6 --live never --work-root %TEMP%… --evidence-dir %TEMP%…` | rc=0；`E2E-S5: PASS (21.5s)`、`E2E-S6: PASS (15.1s)` | 与在案 RUN-R1 离线判定（S5/S6 PASS、live never）一致；全程零网络声明成立（`--live never`） |
| R5a | `B5-fix-g1a-g3/…/scripts/verify_append_fixed.py` | rc=0：`anchors 19/19…APPEND_ONLY = True` | 冻结契约追加纪律成立；**副作用=写回原 attempt（§0 事故，已还原）** |
| R5b | 同 `scripts/verify_boundaries.py` | rc=1：runner census 68/68 PASS、frozen cases 31/31（347 例 bad=0）PASS、`START_HERE unchanged: False`（=其后 owner 授权追加所致，非违规）、`B5 handoff mismatches: 1`（D7） | 与在案 `boundary_verification.json` 相比：结构性结论一致；差异项均系 B5 之后的合法演进或 D7 |

（另：REM-79 自查亦含在 R1a/R1b；审计工具 `evidence/verify_hash_manifests.py` 属我方新增，只读。）

---

## 6. Unverified 清单（明确列出，不以缺样本充 NA）

1. **I-07-D F02/F03/F04 的 raw 字节判据**（D3）——工作树 `%TEMP%\i07d` 已消失，attempt 内未留存被哈希字节。
2. **OPEN-6 转录源版本**（D1）——登记哈希对象不存在；转录快照与现文件分叉段不可复核。
3. **I-14-D E4b 新基线的独立 reviewer 复算**——退出条款要求「E4b 新基线经独立 reviewer 复算」，盘上未见复算载体。
4. **bf0c8b27 生产合并的 owner 授权**（D5）——原话载体缺失。
5. **I-04-D / I-07-A / I-11-A / I-14-A 的独立验收结论**——盘上仅有实现者自述或判决栏留空。
6. **M01–M28 公式卡的独立验收**（D9）。
7. **I-08-C oracle 重冻的收口**——目标①该项仍 open。
8. **TTL=A 30 天到期处置、目标②两批提交与 pre-push 门现状**——超出本镜头（设计一致性）执行核验范围，仅核到其授权条款存在。
9. 我方工具局限：`verify_hash_manifests.py` 的跨根相对路径条目为假阳性（已在 §4 注明）；对 M17/GATE-TIMEOUT-1200 的自带 manifest 未能解析出 (path,sha) 对，未计入通过数。

---

## 7. 审计方法与覆盖面统计

- **方法**：①基准 A 全量钉 sha（124 文件）；②6 个只读子代理分工抽取（卡面条款 I-00…I-17 两批；execution_runs 证据清点；函 A/T2 链追踪；CW 晋升链追踪；修面卡清点）+ 本审计员独立深审（在飞卡 oracle、scenario_matrix 对表、判决重算、冻结契约抽验、验收词表）；③端到端式复跑 6 组 documented 命令共 15+ 次调用（§5）；④声明-盘上双向核对（哈希钉、侧车、登记 sha、git 提交对象）；⑤捏造专项：链上引用工件逐一验存在 + 哈希验同。
- **覆盖面**：设计面 66 张 I 卡 + 31 张 M 卡 + common/matrix/协议文档**全部读到条款级**；执行面 `execution_runs\` 175 个 attempt 目录**全部清点到文件级**（含 I-04-D 32 个 `runs*` 残留），其中 55 个卡 attempt 做了**裁决级**核对、约 25 个做了**条款级/哈希级**深核；重大节点 (a)–(e) 全部专项覆盖。
- **工具与环境**：只读 PowerShell/`read`/`grep`/`Get-FileHash`/只读 git + Python 3.13.9 单进程只读脚本；无网络调用（R4 显式 `--live never`）；所有运行副本在 `%TEMP%\AUDIT-DESIGN-a20260923-01\`。
- **子代理利用**：7 个独立只读子代理全部回报（函 A/T2 链、CW 晋升链、卡面条款 I-00…I-07、卡面条款 I-08…I-17、修面卡/事故目录清点共 5 个完整交付并经我方抽样复核采信；execution_runs 证据清点 2 个因上下文耗尽仅部分交付，其缺口由我方直审补齐）。第七子代理（25 个 attempt 全量清点+全路径捏造扫描）于定稿后回报，其新增发现 D1b/D1c 与对 D9 的更正已并入本报告并重钉 sha。
- **我方事故**：1 起（§0，已还原、已披露、已派生 REM 建议）。

---

## 8. REM-79 自查记录（机械检查器实跑）

- 工具：`PLAN\execution_runs\REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py`（version `1.2.0-correction2`），`PYTHONIOENCODING=utf-8`、`python -X utf8 -B`。
- 对 PWF 三文档（task_plan.md / findings.md / progress.md，只读实跑）：**rc=1，4 处 violation**（全称量词/无域限定断言）：`task_plan.md:1630`（marker「全部」）、`findings.md:633`（「all」）、`findings.md:684`（「none」）、`progress.md:1060`（「全部」）。
- 对 REM79 卡自身 `oracle.md`（%TEMP% 副本）：rc=0，0 violation。
- 处置建议：按 REM-79 规则为上述 4 行补域限定（追加式更正，不回改原文），并登记为新 REM 项。
- 本报告自身声明域：本报告的全部结论域 =「截至 2026-09-23 21:4x 盘上字节 + 本节所列工具与命令的实测输出」，未外推到产品质量、预测准确性、真实 provider 行为或任何 NOT GRANTED 资格。

---

## 独立审查员（owner 令）AUDIT-DESIGN / N=1

签署面 = 本报告 + `audit_report.sha256` 侧车；本人为独立审查员（非实现者），实现者自签规则不适用于本人，但诚实规则全文适用：本报告已披露我方全部事故（§0）、更正（§0 末）、工具局限（§4 末）与未证事项（§6）。
