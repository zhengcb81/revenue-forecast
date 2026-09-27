# CW-GATE-UNBLOCK-2 / a20260923-01 复审裁决落定（review.md）

> **本文件由 carrier-landing 簿记 pass 创建，创建前本 attempt 无 `review.md`。**
> 创建前本 attempt 根仅含：`binding.md` / `changes.diff` / `commands.md` / `decision.md` / `final_report.md` / `handoff.json` / `handoff.md` / `oracle.md` / `recovery.md` / `reviewer_report.md` / `reviewer_report.sha256`，以及 `evidence/`（67 个文件，平铺）与 `scratch/`。
> **本文件只转录，不产生新裁决、不自签**：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`。
> 转录者 = carrier-landing 簿记执行者（与实现者、复审者均非同一人）；本 pass 未重跑任何命令、未联网、未跑测试、未做任何 git 写操作，未改复审报告与既有 carrier 的任何字节（`handoff.json` 状态面转录除外）。

---

## 0. 裁决来源（唯一权威）

| 项 | 值 |
|---|---|
| carrier（唯一权威） | `reviewer_report.md`（本 attempt 内，全程只读） |
| 字节 | **24683 B** |
| sha256 | **`a5a8ede563b6218c51ff9e3595ecd3370b12d284ba84158717b415d23ef4a114`** |
| 侧车 | `reviewer_report.sha256`（**85 B**，内容 `a5a8ede563b6218c51ff9e3595ecd3370b12d284ba84158717b415d23ef4a114  reviewer_report.md` + LF；本 pass 只读，0 字节写入；落定时独立重哈希 == 侧车 == 派发钉值，MATCH） |
| 总行数 | **244 行**（LF-only、0 CR、末行带 LF，文件末字节 = `0x0A`） |
| 裁决行 | 第 **7** 行；字节区 **[551, 570]**（0-based，含行尾 LF，20 B）；该区 sha256 `F378376C192F6D3C42293C19D1591D6C647057E540667A9AE417294E65B36EEB`；行文本（不含 LF）sha256 `C17E9A504395D86C43EAE21193B702E70BCFA7DD297C2A025B9470573795F2CE` |
| 裁决行文本 | `**VERDICT: ACCEPT**` |
| 结尾裁决行 | 第 **244** 行；字节区 **[24663, 24682]**（20 B）；sha256 与第 7 行同 = `F378376C…65B36EEB` |
| 计数行 | 第 **31–33** 行；字节区 **[1933, 1989]**（57 B）；sha256 `7F22B6890774A2F819B72D0994F8860B3D9442A04ADD1F568900DF70751238E1`；文本 = `\| **P1** \| **0** \|\n\| **P2** \| **3** \|\n\| **P3** \| **4** \|` |
| 分级规则（第 9 行原文） | 「有 P1 ⇒ `changes_required`；本次 **P1 = 0**，故按规则为 ACCEPT；P2/P3 为建议在后续修订/下一张卡中消化的更正项。」 |

字节区定义（与本计划既往落定一致）：0-based 字节偏移，按文件处于上述 sha256 状态时计算；单行区**含**行尾 LF；多行区**含**内部 LF、**不含**末尾 LF。
本 pass 复算的其余区段（供父/后续复算）：§0 纪律自查 行13–25 `[744,1881]`/`374AE5C9…`、§1 发现分级+P2/P3 行27–74 `[1883,7997]`/`95FA8188…`、§2 逐条实测 行76–212 `[7999,22268]`/`F646BA38…`、§3 未验证 行216–224 `[22275,23715]`/`6C1DE8FF…`、§4 我没有做的事 行228–235 `[23722,24454]`/`D8566367…`、§5 自验 行239–244 `[24461,24682]`/`75D9854E…`。

---

## 1. 裁决转录

**`VERDICT: ACCEPT`**（`reviewer_report.md:7`，同文第 244 行复述）。

- **P1 = 0 ⇒ 本裁决不是 `changes_required`**（报告 §1 首行「| **P1** | **0** |」，第 31 行）。
- 发现计数：**P1 = 0 / P2 = 3 / P3 = 4**（报告 §1 表，行 31–33），另有 7 条未验证项（报告 §3）。
- 据此，`handoff.json` 顶层 `status` 由 `review_pending` 落为 **`accepted_scoped`**（scoped，**非 clean**：P2-1/P2-2/P2-3 随卡移交，P3-1..P3-4 为证据/归档完整性项）；`status_before` 保留原值 `review_pending`；权威写入 `status_authority`（carrier = `reviewer_report.md`，行号/字节区/sha256 全值 + `verdict_line_text`）；`status_history` 追加两条（round 1 载判 + carrier landing 转录）。
- 本 pass **不签署任何验收**：`implementer_signed=false`、`verdict_is_transcribed_not_authored=true`。

### 1.1 P2 三条（原文摘要 + 处置 + 是否阻断）

| id | 原文摘要（转录自报告 §1 P2，**逐字随卡携带，不得弱化**） | 处置 | 是否阻断 |
|---|---|---|---|
| **P2-1｜双跑同树并发未披露** | 实测时间线（数据文件由 pytest-cov 在会话结束时写入，顺序自洽）：`beforeB.coverage` **06:21:39** → `cov_beforeB.json` **06:21:47** → footer **06:21:51**；duration `1117.38s` ⇒ 起跑 ≈ **06:03:14**（= 日志文件创建 06:03:11）。`afterB.coverage` **06:25:50** → `cov_afterB.json` **06:25:57** → footer **06:26:01**；duration `1110.03s` ⇒ 起跑 ≈ **06:07:27**。⇒ 两跑**重叠 ≈ 14 分 24 秒**，且两份日志 header 的 `rootdir` **都是** `%TEMP%\cwgu2\repo`（同一棵树）。旁证：`34-…log` 文件创建时间 09-23 23:39:40，与其内容所对应的 06:07 起跑不符 ⇒ 该日志文件被截断复用；但两个 coverage 数据时间戳是运行时写入，不受影响。影响：①「CI 等价双跑」在 CI 中是**单跑 + 干净检出**，这里是同树并发，成色下降；② +1 失败（zr409 指纹竞态）的**更直接候选成因就是同树并发的另一跑**，报告把它写成背景 "concurrent-writer noise"，未提同树并发；③ `final_report`/`decision §8`/`handoff`/`51` 全部未披露并发（grep `concurrent\|parallel\|Start-Job\|simultaneous\|overlap\|并发\|同时跑`，命中仅 zr409 措辞与测试内注释）。**不升 P1 的理由**：三行归因的判据与数据已由复审者独立复算/重跑（§2.1），结论不依赖两跑是否隔离；且数据文件经 `COVERAGE_FILE` 隔离（`beforeB.coverage` / `afterB.coverage` 各自独立），失败集差集仅 1 条。 | **随卡移交父代理/登记册**：后续 CI 等价跑必须串行 + 干净检出并**显式披露并发面**；zr409 +1 失败的成因叙述改按「同树并发」候选记账。本 pass 不改 `final_report`/`decision`/`51` 任何字节。 | **否**（P2 不阻断 ACCEPT；报告 §1 规则明示 P1=0 ⇒ ACCEPT） |
| **P2-2｜净增算错** | `final_report.md:80` 与 `decision.md:223` 写「split deltas of only **+9 / +2 / +14** net units」。复审者按同报告 `40` 号分母独立重算：obs `353−344=+9` ✓；pi `254−252=+2` ✓；prune `406−395=**+11**`（stmts `310−303=+7`，branches `96−92=+4`）✗ **+14 无出处**。结论方向不受影响（+11 与 +14 同量级，都远小于 −9.2 点缺口），但这是归因② 明细里的算术错误，须更正。 | **随卡移交**：`final_report:80`、`decision:223` 的 `+14` 应改 `+11`（stmts +7 / branches +4）。本 pass **不改**既有 carrier（erratum 由父代理决定是否派）。 | **否** |
| **P2-3｜证据未入账 + 措辞冲突** | `evidence\37b-DIAG-pristine-3modules-CI-equiv-full.log`（**19,504 B**，rootdir `%TEMP%\dsh-nedzqX\cwgu3j\repo` = pristine 模块副本，`collected 2906 items`，跑到 34% 大面积 `E` 后中断）与 `evidence\48-DIAG-activation-control-vs-pristinecopy.log`（对照：控制副本同样 `PermissionError … pytest-of-…`）**不在** `evidence\INDEX.md`、`handoff.evidence_paths`、`handoff.evidence_sha256`、`final_report §E` 任何一处（程序化比对：磁盘 **67** 个证据文件，manifest **64** 条，缺的正是 **`37b`/`48`/`build_handoff.py`**；**64/64** 条 sha+bytes 与磁盘全一致）。由此 `final_report §F.1`「`37` diagnostic completion — **not executed**」与 `§A.4`「this session cannot execute a CI-equivalent full suite **at all**」与 37b 的存在不符：**本会话确实启动过一次 CI 等价全量跑**（只是因 tmp 沙箱大面积 setup 错误而拿不到测量）。「pristine 重测**未取得** ⇒ 未证实」这个结论本身**没被读成已证实**（四处披露齐全），所以是**披露精度问题，不是结论造假**。 | **随卡移交**：证据账补录 `37b`/`48`/`build_handoff.py` 三条（INDEX / handoff evidence_paths / evidence_sha256 / final_report §E），并把 §F.1 `not executed` 与 §A.4 `at all` 改为「已启动、未取得测量」。本 pass **不改证据账**（改了会破坏 P2-3 的如实记录）。 | **否** |

### 1.2 P3 四条（原文摘要 + 处置 + 是否阻断）

| id | 原文摘要（转录自报告 §1 P3） | 处置 | 是否阻断 |
|---|---|---|---|
| **P3-1｜`decision §0–§7.5` 前缀证明未证实** | 该 attempt 下文件**全部未被 git 跟踪**（`git ls-files <attempt>` = 0 行），attempt 内也不存在任何早于 §8 追加时刻的 `decision.md` 基线 sha（grep `A25112A0`/`decision.md … sha`，仅命中 close-out 自述）。软证据（支持 append-only，但非字节证明）：① `decision.md` 创建于 09-23 21:34:33、最后写于 09-24 21:33:19（= §8 追加时刻）；② **§0–§7.5（1–204 行）内不出现任何 close-out 证据号**（`39a/39b/45/46/47/49/51/52/53/cov_beforeB/cov_afterB/归因先在` 命中全部落在 213 行以后的 §8，第 44 行命中是 git sha `f39bd5a` 的子串）；③ §7.5 仍把 `37` 写成「待执行的诊断」。结论：**未证实（无基线）**，但无反证。 | 随卡移交：后续卡对该 attempt 落基线 sha 或纳入 git 跟踪；本 pass 只转录，不补证。 | 否 |
| **P3-2｜`evidence/40` (b) 表 archive pristine 标签错** | `evidence\40` 的 (b) 表把 archive 的「pristine(CW)」标成 `141/30 / 2A236072`，不成立。复审实测：CW 生产树 `archive_retired_evidence.py` = **123/30 = 153**，sha `BBE855E4…`；`%TEMP%\cwgu3\repo` 里的 archive 实为 **split 版**（sha `2A236072…` == iso）。即 `attr_3modules.py` 的 `CWGU3` 副本对 archive 不是 pristine。影响面：A.4 上界表只列 obs/pi/prune 三行（这三行的 `CWGU3` 已逐一 sha 比对 == CW 生产树，完全一致），40 的 archive 行本就判 `inconclusive` ⇒ **结论不受影响**，但 (b) 表标签对 archive 是错的。 | 随卡移交：`40` 号 (b) 表 archive 行标注更正（123/30/`BBE855E4`）；本 pass 不改证据。 | 否 |
| **P3-3｜`final_report §B`「No test file was created or modified」仅限本会话** | 复审对 `changes.diff` 逐文件统计 `+def test_`：新增测试只在 **2 个文件** —— 新车 `test_archive_retired_evidence_fail_closed.py` **+12**、既有 face `tests/contract/test_source_catalog_prune_retired.py` **+1**（`test_prune_dry_run_reports_span_volume`）。即本卡**整体**是「+12 新测 + 9 个 face 改写（其中 1 个 face 净增 1 条）」。这些都在 §7.5 站规成文之前、也都在 BEFORE-B 之前完成（`33b` collected 2894 已含该 face），**不构成违反 §7.5**，但 §B 措辞易被读成「本卡未加测」。 | 随卡移交：`final_report §B` 措辞限定为「close-out 会话未加测」；本 pass 不改。 | 否 |
| **P3-4｜`45` 号 extra-files 清单漏列 1 项** | `45` 写「extra files in copy: 5」；复审独立遍历副本（同样排除 `__pycache__/.pytest_cache/.ruff_cache/.mypy_cache`）得 **6**：45 列的 5 项 + **`pyw.txt`**（2 B，mtime 09-24 21:23:30，仅存在于副本、iso 侧无）。pytest 不收集该文件，**对判据无影响**，纯清单遗漏。 | 随卡移交：`45` 清单补 `pyw.txt`；本 pass 不改。 | 否 |

> 计数核对：P1=0、P2=3（P2-1..P2-3）、P3=4（P3-1..P3-4）——与报告 §1 表（行 31–33）一致；`carried_findings` 已在 `handoff.json` 逐条落盘并镜像至 `evidence/CW-GATE-UNBLOCK-2/qualification.json`。

---

## 2. 复审者实测逐条抄录（不许改数）

> 全部为复审者**自己实测/自己重跑**的原始数字（报告 §2）；本 pass **未重跑任何一条**，仅转录。

### 2.1 归因①（归因先在）—— **成立，且经复审者独立重跑**

**(a) 同判据 / 同 rootdir / 同 pytest —— 逐字核过**
- `39a` / `39b` 头部完全一致：`cmd: FC1204_COVERAGE_GATE=1 python -m pytest -q tests/contract/test_fc1204_coverage_ratchet.py`；`rootdir: …\Temp\dsh-nedzqX\cwgu2j\repo (pytest.ini)`（**两臂同一字符串**）；`Python 3.13.9, pytest-9.1.1, pluggy-1.5.0, cov-7.0.0`（**同一版本**）；两臂唯一变量 = `coverage.json`（`7C966B73…` vs `8B185037…`）。
- 判据文件 sha 四处一致 = **`FA0001209BB43BF49E63CA9B9D9463485E6F35B1B8ACCB69D0E7F78DEFE31C85`**：CW 生产树 / iso / 实现者的判定副本 / **复审者自己的副本**。
- 判定副本与 iso 的同一性复审者**独立重做**（**678** 个文件全量 sha 比对）：`hash differences = 0`，`only-in-iso = 0`，`only-in-copy = 0`（与 45 一致，仅 45 漏列 `pyw.txt`）。

**(b) 复审者独立重跑（其自己的副本 `%TEMP%\dsh-DVYjk0\rev_gu2\repo`，rootdir 又与两者都不同）**
- AFTER-B 数据（`coverage.json` sha `7C966B73…`）→ **rc=1**，`1 failed, 1 passed`，断言逐字：
  `observability.py 65.7% < 91% (frozen); prompt_injection.py 48.4% < 73% (frozen); prune_retired_evidence.py 77.8% < 87% (frozen)` ⇒ **与 36 / 39a 完全一致**（tier1 PASSED）。
- BEFORE-B 数据（`coverage.json` sha `8B185037…`）→ **rc=1**，`1 failed, 1 passed`，断言逐字：
  `archive_retired_evidence.py 85.4% < 95% (frozen); observability 65.7 < 91; prompt_injection 48.4 < 73; prune_retired_evidence 77.8 < 87` ⇒ **与 39b 完全一致**。
- **结论：三行红数值在两臂完全相同（65.7 / 48.4 / 77.8），唯一位移是 archive 85.4→100.0。**

**(c) 复审者自己解析两份 coverage JSON**（数据文件实测：`cov_beforeB.json` **1,186,762 B / `8B185037…`**；`cov_afterB.json` **1,186,681 B / `7C966B73…`**，与 A.1、45、40 一致）

| module | BEFORE-B | AFTER-B | floor |
|---|---|---|---|
| observability.py | 283 stmts / 198 cov / 70 br / 34 cbr = **232/353 = 65.7%**（miss 85 L / 36 B） | **完全相同** 232/353 = 65.7% | 91 |
| prompt_injection.py | 178 / 94 / 76 / 29 = **123/254 = 48.4%**（miss 84 / 47） | **完全相同** 123/254 = 48.4% | 73 |
| prune_retired_evidence.py | 310 / 255 / 96 / 61 = **316/406 = 77.8%**（miss 55 / 35） | **完全相同** 316/406 = 77.8% | 87 |
| archive_retired_evidence.py | 141 / 127 / 30 / 19 = **146/171 = 85.4%**（miss 14 / 11） | 141 / **141** / 30 / **30** = **171/171 = 100.0%**（miss 0 / 0） | 95 |

**(d) archive 位移「恰为本卡 12 测所修、三行未被触碰」—— 复审者的核法**
- `30` BEFORE-A 家族跑：2 tests → `127/141 + 19/30 = 85.38%`；`32` AFTER-A 家族并集：17 tests（2 face + 3 prune face + **12 新测**）→ `141/141 + 30/30 = 100.0%`。新增量只有那 12 测。
- `33b` collected **2894**（= 2906 − 12，新车未进 BEFORE-B）；`34` collected **2906**，该文件行 `tests\contract\test_archive_retired_evidence_fail_closed.py ............` = **12 个点全过**。
- 两跑 FAILED 行差集（复审者独立 diff）：only-in-34 = `tests/contract/test_zr409_fourth_root_real_journeys.py::test_c2_journey_dayu_only_real_sample`（**1 条**），only-in-33b = **0**。
- 三个模块在双臂逐字节级覆盖数据完全一致 ⇒ **12 测未触碰那三行**。

**(e) 计划侧核对**：`REMEDIATION_REGISTER.md:2149` 预登记的处置正是「归因先在 ⇒ 按 TRIAGE 家族 C 先例（数据源=跑面）核 BEFORE-B 同判」；家族 C 先例本身在 register **1616/1759** 行有实体记载（复现布局病、数据源=跑面而非 sha 回归）⇒ **先例引用非杜撰**。

### 2.2 归因②（拆分被算术排除）—— 复审者自己重算，上界三值全对

用 coverage 的 `PythonParser`（同一套规则）独立解析 **CW 生产树**与 **iso** 的四个文件：

| module | pristine(CW) stmts/br | split(iso) stmts/br | 分母 pristine / split | 与 `40` 是否一致 |
|---|---|---|---|---|
| observability.py | 272 / 72 | 283 / 70 | **344 / 353** | ✓ |
| prompt_injection.py | 176 / 76 | 178 / 76 | **252 / 254** | ✓ |
| prune_retired_evidence.py | 303 / 92 | 310 / 96 | **395 / 406** | ✓ |
| archive_retired_evidence.py | 123 / 30 | 141 / 30 | 153 / 171 | `40` 的 pristine 列错（P3-2） |

- **pristine 分母**：obs **344**（272+72）、pi **252**（176+76）、prune **395**（303+92）。
- **上界三值**：obs `232/344 = 67.44 → 67.4%` < `floor−0.5 = 90.5` ✓；pi `123/252 = 48.81 → 48.8%` < `72.5` ✓；prune `316/395 = 79.99 → 80.0%` < `86.5` ✓ —— 与报告宣称的 **67.4 / 48.8 / 80.0** 完全一致。
- **缺口点数**：`65.7−91 = −25.3`、`48.4−73 = −24.6`、`77.8−87 = −9.2` ✓。
- **拆分净增单元**：`+9 / +2 / **+11**` ⇒ 报告写 `+14` = **算错（P2-2）**。
- **稳健性检验（复审者补的）**：上界式 `metric_pristine ≤ C_split/T_pristine` 依赖「拆分不会减少被覆盖单元数」，而 obs 分支数其实 **72 → 70（−2）**，故非严格定理。**加 20 个单元宽裕余量重算**：`(232+20)/344 = 73.3%`、`(123+20)/252 = 56.7%`、`(316+20)/395 = 85.1%`，**仍全部 < floor−0.5**（prune 到 **+25 才 86.3%**、+26 才 86.6% 失守）⇒ **结论稳健**，最保守读法下「拆分致红」在数量级上也不成立。
- **分母与 coverage JSON 对齐**：JSON 侧 obs `283/70`、pi `178/76`、prune `310/96` == 静态解析 split 值 ✓；`attr_3modules.py` 用的 `cwgu3` 对 obs/pi/prune 的 sha == CW 生产树（`EDCBECCB…` / `88154DE4…` / `0C99BBE0…`，复审者实测四处一致）✓。

### 2.3 「不补测」是否合规 —— 合规，冻值/95 阈零动（复审者自算）

- **`decision §7.5` 铁律确在其文**（原文，`decision.md:200-201`）：「Per the standing rule: STOP-and-report; **NO self-lowering of any floor; NO unauthorized test additions to those modules; the parent decides the follow-up card.**」⇒「不得擅自给这三模块加测、须 owner 裁」**属实**。
- **四行冻值与 95 阈（复审者直接读判据文件 + 自算 sha）**：
  - `tests\contract\test_fc1204_coverage_ratchet.py` = **5,786 B / `FA0001209BB43BF49E63CA9B9D9463485E6F35B1B8ACCB69D0E7F78DEFE31C85`**（== oracle A.0）；内容：`TIER2 prompt_injection.py: 73`、`FROZEN archive_retired_evidence.py: 95`、`observability.py: 91`、`prune_retired_evidence.py: 87`；TIER1 全 95。
  - `tests\contract\test_fc1204_complexity_ratchet.py` = **4,866 B / `BCD01361E3025F99A78D8DB8452116D05D81DE685A4895D7B6FF34D7E93BB3F2`**（== oracle A.0）；表值 `archive 7 / observability 6 / prompt_injection 15 / prune_retired_evidence 12`。
  - 两个文件在 **CW 生产树、iso、实现者判定副本、复审者副本** 四处 sha 相同 ⇒ **零动**。
- **`changes.diff` 内容验证（比基线 sha 更硬的端点证明）**：**15 个** `diff --git` 头；对每条 `index OLD..NEW` 用 `git hash-object` 实测 —— **15/15 的 OLD == 当前 CW 生产树文件的 blob**（NEW 文件则 CW 侧确为 ABSENT）；**15/15 的 NEW == iso 最终文件的 blob** ⇒ 现存 `changes.diff` 精确编码 CW→iso 的完整增量，任何字节篡改都会破坏端点匹配；且 diff 中**不含** `fc1204` / `coverage_ratchet` / 棘轮表 ⇒ **冻结值不可能被这份交付改动**。
- `changes.diff` 实测 **66,831 B / `100B19202F551A7B16137CA2A83B5D732FB17490B7802D6C9FC0972D2B04E611`**（与 47/final_report/handoff 一致）；**mtime 09-23 23:02:56，早于 close-out（09-24 21:07 起）约 22 小时** ⇒「close-out 期间一字节未动」**成立**。
- `oracle.md` 实测 **15,768 B / `48E30A9D…`**，mtime 09-23 21:32:43 ⇒ close-out 期间未触 ✓。

### 2.4 门 6 步 —— 复审者读 `evidence/50-gate-fullrun.log` 逐条核 rc

| 步 | 结论 | rc |
|---|---|---|
| 1 ruff | `All checks passed!` | **0** |
| 2 compileall | — | **0** |
| 3 config_doctor | `OK: …\config\source_catalog.yaml healthy` | **0** |
| 4 complexity-ratchet | `2 passed in 9.88s` | **0** |
| 5 host_assumption_guard | `violations=96; new=0; baseline=71; registered_hashes=5` | **0** |
| 6 contract-meta | `99 passed in 124.54s` | **0** |
| 整门 WHOLE GATE | 6 项 `ok` + `pre-push gate GREEN` | **0** |
| 7 extra: unique-test-symbols | `OK: 276 test file(s), no duplicate test_* definitions` | **0** |

⇒ **门 6 步全绿 + 整门 rc0 + unique-symbols rc0 属实**（判定树 rootdir = iso）。

### 2.5 CI 双跑诚实性 —— 逐项核

| run | 字节（实测） | items | FAILED 行 | footer（逐字） | 判定 |
|---|---|---|---|---|---|
| `33`（被杀） | **27,418** | 2894（partial） | — | **无 footer**，末行停在 `[47%]` | **VOID 属实**，未当产物 |
| `33b` BEFORE-B | **631,418** | **2894** | **62** | `=== 62 failed, 2822 passed, 10 skipped, 487 warnings in 1117.38s (0:18:37) ===` | COMPLETE |
| `34` AFTER-B | **624,448** | **2906** | **63** | `=== 63 failed, 2833 passed, 10 skipped, 485 warnings in 1110.03s (0:18:30) ===` | COMPLETE（判定源） |

- sha 实测：`33b = DA87EA835AE0F17D…`、`34 = 379B7491DBCDD792…`、`33 = 49B8FFB4CB24E146…`，与 `51`/`handoff` 一致。
- **被杀那次确实 VOID**：`cov_beforeB.json` 落盘时刻 **06:21:39/47 == 33b 结束时刻**，被杀的 `33` 停在 00:44 且从未写出 coverage 数据 ⇒ **判定源确为 33b 而非被杀那次**。
- **失败集差集**（独立 diff）：only-in-34 = zr409 那 1 条；only-in-33b = 0。
- **分类 34+12+17=63 复审独立复算通过**：`test_relevance` 12 条 + `tests/unit` 1 条 + acceptance 10 条 + contract 40 条 = 63；contract 内 34 条为 `FileNotFoundError`（iso 缺件）、其余 6 条进 OTHER；OTHER = 10 acceptance + 5 contract + 1 unit + zr409 = **17** ⇒ **34 + 12 + 17 = 63** ✓。
- **本卡 10 个测试文件命中 0**：用 10 个文件名对 34 的 FAILED 行过滤 → **0** ✓。
- **+1=zr409 其隔离绿**：`46` 记录 **2 次** `rc=0 / 1 passed`；**复审者在自己副本再跑第 3 次：`1 passed`，`RC=0`** ⇒ 3 个绿样本支撑「指纹竞态、非本卡所致」。
- **iso 缺件实为 iso 副本假象（53）**：抽验 12 条路径，CW 侧全 **EXISTS**，`candidate-manifest.json` 确实 **MISSING**（iso 侧亦缺），姊妹 `golden_corpus.json` EXISTS ⇒ **17/18 + 姊妹 存在，1 缺** 属实。
- **命令等价性**：`ci.yml` L63 = `python -m pytest tests/ -q --tb=short --cov=src/company_wiki/source_catalog --cov-branch --cov-report=json \|\| true`、L64 = `FC1204_COVERAGE_GATE=1 python -m pytest tests/contract/test_fc1204_coverage_ratchet.py -q`；与 `commands.md §5`、判定命令一致 ✓。
- **唯一不达标处 = P2-1（两跑同树并发未披露）**。

### 2.6 未证实面原样携带 —— 核过，**不得读成已证实**

- `37` 号日志复审者读了：确为 `coverage/sqldata.py … _open_db → _read_db` 的 `INTERNALERROR`（**416 B**）⇒ pristine 三模块同跑面直测**未取得**。
- 四处披露齐全且一致：`final_report §A.4 item 3`（"…is **未证实**"）、`§F.1`、`decision §8.1 UNVERIFIED`、`handoff.unverified[0]` ⇒ **没有把「未证实」写成「已证实」**。
- 同时确认 **37b/48 的存在**（P2-3）：它们**支持**「本会话拿不到测量」这一实质判断，但使 `§F.1` 的 `not executed` 与 `§A.4` 的 `at all` 措辞不准、且这两份证据没进任何账。
- 复审者对沙箱的实测：`%TEMP%` 根**可写文件、不可建目录**（`MKDIR FAILED: Access denied`），session temp 可建目录 ⇒ 与 49 的阻断叙述方向一致；判据的 2 个测试不依赖 `tmp_path`，故能在其副本里跑起来（已跑）。

### 2.7 边界（复审者实测）

- **零产品写（两个仓都查了）**：本仓 `git diff HEAD --name-only` → total **3822**，非 `.planning` **0** ✓（禁用 `git status`，未使用过一次）。产品仓（company-wiki）`git diff HEAD` = **3 个**已修改文件（`CLAUDE.md`、`README.md`、`src/company_wiki/source_catalog/artifact_dag.py`），**mtime 全为 2026-09-23 13:08:38**（早于本 attempt 最早产物 ≥19:50），内容分属 I-16 边界提示与 D-W05 注释，**均不在本卡 15 文件内** ⇒ **非本卡写入**。
- **`handoff.json`**（改前）：27,455 B、**UTF-8 无 BOM**、`json.loads` 解析 rc=0；`status = review_pending`、`implementer_signed = false`、`reviewer_status = awaiting_second_party_review`、`completed_steps = 9`（全部 `status=completed`）⇒ 与自述一致 ✓。
- **交付物 sha 全部实测**（与 handoff `deliverables` 逐条一致，**8/8** 匹配）：`final_report.md` 16,879 / `5A36D735C7045F02…`；`decision.md` 22,428 / `A25112A0B6DC93D0…`；`handoff.json` 27,455 / `6B89F089B608038E…`；`oracle.md` 15,768 / `48E30A9DDC5D7EE7…`；`changes.diff` 66,831 / `100B19202F551A7B…`；`binding.md` 8,743 / `4E533A39…`；`commands.md` 5,536 / `96EEFC3B…`；`recovery.md` 2,089 / `29B6E4E9…`；`handoff.md` 3,194 / `1D40D1C7…`。
- **handoff 证据账目**：`evidence_sha256` **64 条** sha+bytes 与磁盘 **64/64 全匹配**；缺口仅 `37b`/`48`/`build_handoff.py`（P2-3）。
- **`decision §0–§7.5` 前缀**：见 P3-1（无基线 ⇒ 未证实，软证据支持 append-only）。
- **九步自述核对（§2.8）**：`handoff.completed_steps = 9`，id 1–9 全 `completed`，每步都有 evidence 指针；其中第 9 步（close-out 归因）正是本次复审对象 ⇒ **九步全 = 属实**。
- **零网络 / 零 git 写**：复审者侧自证；实现者侧无反证（日志与 `commands.md` 未见任何网络或 git 写命令，产品仓 3 个改动的 mtime/内容都与本卡无关）。

---

## 3. 两非目标裁 + REM-95 关闭裁 + 幂等永拒裁（载体核对与本卡对应裁决转录）

> **载体核对（必读，避免张冠李戴）**：本 pass 逐字检索本卡实现者载体 `final_report.md`（§A–§F，224 行）与 `decision.md §8`（§8.1–§8.5，行 205–252）——**不存在**「两非目标裁」「REM-95 关闭裁」「幂等永拒裁」任何字样或对应内容。这三条是 **`WC-6-ADAPTER-DISPATCH/a20260923-01`** 卡复审报告 §2/§3/§4 的裁决（REM-95 = adapter_dispatch 丢补救原因；幂等永拒 = `_ObservedFile.error` 方案），其 `review.md` 已由既往 carrier-landing 落定。
> **跨卡搬运 = 新裁决，本 pass 不做、不臆造。** 下面逐字转录**本卡载体中实际存在**的对应面裁决（非目标裁×2、关闭/放行类、零动/永拒类、后续 owner 裁）。

### 3.1 两非目标裁（本卡对应面）

**非目标裁① —— 三行覆盖红（obs/pi/prune）**不属本卡 coverage mandate**
> `decision.md:188-189`（§7.5）原文：「**Not this card's coverage mandate** (scoped to `archive_retired_evidence.py` — which JUDGED PASS at 100.0% ≥ 95). Candidate causes: (a) the FC-1204 splits' new wrapper lines/arcs, (b) PRE-EXISTING floor staleness …」
> `decision.md:200-201` 站规原文：「Per the standing rule: STOP-and-report; **NO self-lowering of any floor; NO unauthorized test additions to those modules; the parent decides the follow-up card.**」
⇒ 落定：本卡**只报不修**，三行红登记为家族既有债（data source = 跑面）；补测或重冻一律由 **owner/后续卡** 裁。

**非目标裁② —— 既有测试债（未触碰文件的历史失败）**out of scope，仅作 CI 预测依据上报**
> `decision.md:171-175`（§7 item 4）原文：「Pre-existing test debt OBSERVED in untouched files during the full-suite runs (`test_cw1_source_contract_receipt`, `test_cw_228_receipt`, `test_fixture_packaging`, `test_cold_start`, `test_pdf_*`, `test_fc906b` one case, …) — identical failure sets before/after my diff (BEFORE-B vs AFTER-B comparison) → not introduced by this card; **out of scope** (no product behavior change in the diff); reported as CI-prediction basis.」
⇒ 落定：**不进本卡修复面**，只作 `final_report §D.3` CI 预测的依据上报。

### 3.2 关闭 / 放行类裁决（本卡对应面，转录自 `final_report` / `decision §8`）

| 裁 | 原文要点 | 落定状态 |
|---|---|---|
| **归因裁**（§8.1 / `final_report §A.4`） | 「**归因先在 (data source = CI-equivalent full-suite run surface), per TRIAGE family-C precedent; the 12 new tests are excluded as a cause (measured).**」；上界 `C_split/T_pristine` = 67.4/48.8/80.0 %，全 < floor−0.5 | 已由复审者**独立重跑证实**（§2.1/§2.2）⇒ 归因结论**成立**；`attribution_state = pre_existing_attributed_to_run_face` |
| **不补测裁**（§8.2 / `final_report §B`） | 三因：① 卡自身规则（BEFORE-B 同红 ⇒ 不加测、登记家族债）② `§7.5` 站规（不得擅自给这三模块加测，owner 裁）③ 本会话跑不了测试（`49`）；`changes.diff` 不变（`100B1920…`/66,831 B）、`BCD01361…`/`FA000120…` 不变、95/91/73/87 全按实测记录 —— **zero self-lowering** | **合规**（复审 §2.3 认定）；⚠ 措辞范围见 **P3-3** |
| **双跑裁**（§8.3 / `51`） | `33b` 631,418 B/2894/`62 failed, 2822 passed, 10 skipped, 1117.38s`；`34` 624,448 B/2906/`63 failed, 2833 passed, 10 skipped, 1110.03s`；被杀 `33`（27,418 B，无 footer）保持 **VOID**；+1 = zr409（隔离绿 ×2，`46`），本卡 10 个测试文件 0 命中（`52`） | 复审逐项核过 **属实**（§2.5）；⚠ 未披露同树并发 → **P2-1** |
| **三件交付 + CI 预测裁**（§8.4 / `final_report §D`） | D.1 15 文件表；D.2 四行终值 = archive **100.0 ≥ 95 GREEN**、obs **65.7 < 91**、pi **48.4 < 73**、prune **77.8 < 87**（三行 = 家族既有债）；D.3 CI 预测表 —— 只有 coverage gate 的 tier-2/frozen 断言预测 **RED**，inherited not card-caused | 数字经复审实测复核一致；结论方向不变（P2-2 仅 `+14→+11` 更正） |
| **后续 owner 裁** | `final_report.md:192-193`：「**Follow-up owner decision required** (either a dedicated card adding fail-closed exception-path tests for obs/pi/prune, or an explicit floor re-freeze ruling) — **no self-lowering performed**」；`final_report §F.3`：「No test additions for obs/pi/prune rows (§B) — parent/owner decision.」 | **未执行、未代裁**：本 pass 不补测、不重冻、不晋升 |

### 3.3 零动 / 永拒类裁决（本卡对应面）

> 本卡载体中最接近「永拒」语义的裁决是**冻结值零动 + 零自降的永久约束**（转录自 `decision §8.2` / `§6`）：
> 「`changes.diff` unchanged (sha `100B1920…`, 66 831 B); ratchet table `BCD01361…` / coverage-ratchet file `FA000120…` unchanged; 95 / 91 / 87 / 73 all recorded as measured — **zero self-lowering**」；`decision §6`：「Table updates are only ever sanctioned DOWNWARD after a deliberate split; NOT needed here … **Raising any frozen value is forbidden.**」
⇒ 落定：**本卡未动任何冻结值/阈值**（复审 §2.3 四处 sha 一致 + `changes.diff` 15/15 端点证明 + diff 不含 `fc1204`/`coverage_ratchet`）；**`handoff.frozen_values_untouched = true`**。
> 本卡载体中**无**「幂等永拒裁」；`_ObservedFile.error` 方案的永拒属 WC-6 卡，**不在本卡账上**。

---

## 4. 未验证项 + 边界声明

### 4.1 复审 §3「未验证 / 未能验证项」逐条（7 条，原文转录）

1. **CI 等价全量跑无法在本会话复现**：沙箱禁止在 `%TEMP%` 根建目录、pytest `tmp_path` 的 0o700 目录不可写 ⇒ 复审者**没有**重跑 `33b`/`34`（2906 项）。两跑的 footer/计数/差集是其对**既有 raw 日志**的独立解析，**不是重跑**。
2. **pristine 模块同跑面直测（`37`/`37b`）**：未取得 ⇒「CW HEAD 未改源也三行红」**仍为未证实**；复审者没有把它当成已证实，也没有能力在本会话补上。
3. **`decision §0–§7.5` 的字节级前缀证明**：缺基线 sha、文件未纳管 git ⇒ **未证实**（仅软证据，见 P3-1）。
4. **`changes.diff` 与「被审那一版」逐字节相同**：无历史基线；只能给出**端点等价证明**（15/15 index blob 匹配 CW 与 iso）+ mtime 早于 close-out 22 小时。
5. **34 号日志 23:39:40 创建时间对应的历史内容**已被截断覆盖，无法还原（不影响 06:07 起跑的推断，后者由 coverage 数据时间戳独立支撑）。
6. **`zr409` 指纹竞态的根因**：只拿到第 3 次绿样本，未做根因分析；`tests/unit/test_contradiction_detector` 两跑同红也未查因（实现者已声明 uninvestigated）。
7. **39b/39a 之外的独立「第二判定源」**：复审者做的是独立副本重跑（同一份 coverage JSON）；**没有**独立产出第三份 coverage 测量。

（实现者侧原有 6 条 `unverified` 保留不动，一并在 `handoff.unverified` 中以 `implementer §…` / `reviewer §3` 前缀区分来源，见 `unverified_source`。）

### 4.2 复审者「我没有做的事」（报告 §4 逐条）

- 没有修改 `.planning` 之外的任何文件；没有修改本 attempt 的任何既有字节；只新建 `reviewer_report.md` + `reviewer_report.sha256`。
- 没有创建/修改 `handoff.json`，没有改 `status`，没有替实现者落定，没有签署任何东西。
- 没有执行任何 git 写操作；**没有用过 `git status`**；没有联网。
- 没有重跑 CI 等价全量、没有重跑 33/34、没有修改 `changes.diff`、没有给那三模块补测、没有动任何冻结值。
- 没有把「未证实」写成「已证实」，没有为凑绿而构造样例；缺证据处一律标「未证实」。
- 没有对 P2/P3 之外的第三方（owner/上层卡）发任何外向请求。

### 4.3 本 carrier-landing pass 自身的边界（本 pass 声明）

- **写入面 = 仅本 attempt 目录**：本 pass 只写 3 个文件 —— `review.md`（新建）、`handoff.json`（status 面转录）、`evidence/CW-GATE-UNBLOCK-2/qualification.json`（新建）。**未写** `REMEDIATION_REGISTER.md` / `progress.md` / `findings.md` / `task_plan.md` / `OWNER_DECISIONS.md`；未改 `.planning` 之外任何文件（**尤其 `company-wiki` 产品仓**）；**无 git 写操作**；**未联网**；**未跑测试**。
- **复审报告只读**：`reviewer_report.md`（24683 B / `a5a8ede5…f4a114`）与 `reviewer_report.sha256`（85 B）落定前后字节不变（落定后复测同值）。
- **既有 carrier 只读**：`final_report.md` 16879/`5A36D735…`、`decision.md` 22428/`A25112A0…`、`handoff.json`（除状态转录）27455/`6B89F089…` 前像已记、`oracle.md` 15768/`48E30A9D…`、`changes.diff` 66831/`100B1920…`、`evidence/**` —— 除 `handoff.json` 状态转录外 **0 字节改动**。
- **不自签**：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`。
- **落定核验**：`git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` 计数 = **0**（本 pass 写入前基线 total=3824/非 `.planning`=0；三件产物写完后复测仍为 0，最终值随本 pass 结果报告一并交父）。
- **不做**：不写五份计划文件；不改 `reviewer_report*`；不补测、不动冻值；不晋升；不改证据账（P2-3 保持如实未入账状态，随卡移交）；不产生新裁决。

---

## 5. 落定清单

| 文件 | 状态 |
|---|---|
| `review.md` | 本文件，**新建**（创建前本 attempt 无 `review.md`） |
| `handoff.json` | `status: review_pending → accepted_scoped` + 新增 `status_before` / `status_transition` / `status_authority` / `status_history` / 更新 `reviewer_status` / 新增 `carried_findings`（P2-1..P2-3 + P3-1..P3-4 逐条）/ `unverified` 追加复审 §3 七条 + `unverified_source` / `attribution_state` / `no_new_tests_added_by_this_card` / `frozen_values_untouched` / `verdict_is_transcribed_not_authored`；JSON 写后重解析；改前前像 sha `6B89F089B608038E9FF20D895DF702C7CEA2A89B927EE5BE9B8B8E6C86DD90A0` / 27455 B 已记 |
| `evidence/CW-GATE-UNBLOCK-2/qualification.json` | **新建**：`formula = not_applicable_with_reason`、`disclosure_adaptation = unmapped`、`accuracy = unproven`、`granted_scope` / `not_granted`、`verdict_is_transcribed_not_authored = true`、`status_authority` 镜像、`carried_findings` 镜像 |

**卡状态（随卡携带）**：`review_pending` → **`accepted_scoped`**（P1=0 ⇒ ACCEPT，但 scoped 非 clean：P2-1/P2-2/P2-3 + P3-1..P3-4 随卡移交）；**不自签**、**不晋升**、**不补测**、**不动冻值**。
