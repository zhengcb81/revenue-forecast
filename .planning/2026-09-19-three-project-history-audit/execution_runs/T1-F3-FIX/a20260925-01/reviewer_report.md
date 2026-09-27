# T1-F3-FIX 独立复审报告（合并序第三腿 · attempt `a20260925-01`）

**复审工位**：独立复审（与实现者非同一人）· **父 agent**：`session-19074bf0-0205-4315-af73-9db57597275a`
**复审对象**：`execution_runs/T1-F3-FIX/a20260925-01`（实现者 subagent，`implementer_signed=false`）
**写入面**：本目录内两个新建文件 `reviewer_report.md` + `reviewer_report.sha256`（除此之外零字节写入）

VERDICT: ACCEPT

---

## 0. 复审方法（先回源、再独立复跑）

**回源读（不是读转述）**

1. `execution_runs/I-14-B/a20260919-01/oracle.md` 的 `### 11.8`（L274–294；文件 28930 B / `b1eb5d0cf83dd8f0…` = 派发登记值，只读）。另验：该文件**前 26554 B 的 sha256 = `bdd0407ab577ed45…`**（登记的前像），且 `### 11.8` 恰好起于偏移 **26554** ⇒ §11.8 是纯追加、其前字节一字未改。
2. `T1-10-FIX/a20260923-01/review.md` §7（L73–131，sha `1ab78c3d712ecef4…`/24335 B ✓）与 `reviewer_report.md` §7.3（L159–216，sha `96847e0a9e2d01db…`/30247 B ✓），两处内容互为逐字副本（amendment text 一致）。
3. 本卡 `oracle.md`（31227 B / `ba17f83740104190…`，含两条 append-only erratum）、`handoff.json`（19808 B）、`decision.md`、`evidence/after/invariants.json`（9093 B / `c608fce75d9abe99…`）、`binding.json`、`commands.json`、`evidence/freeze.json`、`evidence/line_zones.json`、`evidence/after/line_disjointness.json`、`evidence/instrument_runs/README.md`。

**隔离复跑（测试只在 `%TEMP%` 副本，生产树只读）**

- 驱动：`scripts/verify_t1_f3_fix.py`（59379 B / `c311fe9722158bc9…` = 登记值）；我在 `%TEMP%\f3rev` 下按**相同目录深度**复制整个 attempt（排除 ACL 坏掉的 `_pytest_tmp`）+ `invariants` 需要经 `ATTEMPT.parents[2]` 解析的 5 个前置被 pin 文件（I-14-B `oracle.md`、两前置卡的 `changes.diff`+`handoff.json`；另多复制了 T1-10 的 `review.md`/`reviewer_report.md` 供回源读），并在 `%TEMP%\f3rev2` 再建一份**完全未动的干净副本**作对照。
- 复跑子命令：`probes / gates / suites / ncmissing / vocab / batch / mutations / invariants`（before 相一律显式 `--sut <baseline/natural_window.t1_f2fixed.pristine.py>`；after 相用默认 worktree SUT）；`mut20` 因不接 `--sut`，在第二份副本上**先换回左像跑 before、再换回修复像跑 after**（见 §3 末）。
- 解释器：系统 `python 3.13.9` + `pytest 9.1.1`（实现者用 I-14-B venv `python.exe 3.13.9`，`commands.json` 登记 pytest 9.1.1 ⇒ 同版本；**结果与其实测逐项一致**）。
- **独立算法**（不运行他们的 `analyze_chain.py`）：自写 unified-diff 应用器 + hunk 解析器 + `difflib` 行号映射 + 词表正则 + oracle 前缀哈希 + mtime 时序检查（脚本留在 `%TEMP%`，不属交付物）。

---

## 1. 逐项核验表（派发单九项 + 特别项）

| # | 项目 | 我的实测 | 判定 |
|---|---|---|---|
| 1 | 词表 16 → 17（口径 `\bR-[A-Z0-9-]+\b`） | 左像 `9b1ebda2…` = **16**；修复像 `d1ced6ac…` = **17**；`after−before = {R-TIMESTAMP-MALFORMED}`；`before−after = ∅`；16 码集合与 T1-10-FIX reviewer 报告 §7 列表**逐字一致** | ✅ |
| 1b | 「裸正则多计」说法 | 裸式 `R-[A-Z0-9-]+`：左像 = **17**、修复像 = **18**；两像 bare-only 多出的 token 均为 **`R-UNKNOWN`**（`R-UNKNOWN_CLASS` 被 `_` 截断）。⇒「裸=17、带 `\b`=16、多计一个假码」**独立验证为真** | ✅ |
| 1c | 既有 16 码未被改 | 16 个码在两像均原样存在；集合差双向为空（词表层）；`R-UNKNOWN_CLASS` 两像均仍在源码中 | ✅ |
| 2 | 四变异臂必须真红 | A：TS1–TS5 **5/5 rc=4、无报告、0 裁决**；B：**5/5 翻 `accept_claim`、refusals=[]**（危险 accept）；C：TS1 `started_at="not-a-timestamp"`、TS5 为其列表原值 ⇒ **不再 null**；D：**TS1=4、TS5=4、TS2/3/4=0**。四臂 anchor 出现次数均 = 1，驱动 `all_arms_red=true` rc=0 | ✅ |
| 3 | 修前/修后关键行 | 修前 TS1–5：rc=4、`report_written=false`、stdout `{"ok": false, "error": "internal_error", "detail": "Invalid isoformat string: 'not-a-timestamp'"}`（TS5 = `"'list' object has no attribute 'endswith'"`）、**0 裁决**、直调 `classify()` 抛 `ValueError`（Traceback 5/5）；修后 TS1–5：**rc=0、报告写出、`reject_claim`、`["R-TIMESTAMP-MALFORMED"]`、受影响时间字段 null**；**DOC-2 两像均 rc=2** `malformed_input` 逐字节同；**CTRL-4 两像均 rc=4** `"'str' object has no attribute 'get'"` 逐字节同 | ✅ |
| 4 | 批次负控 + 逐字节 | before `[BAD,W1,X5,C1]` = **rc=4 / 无报告 / 0 裁决**；after = **rc=0 / 报告写出 / case_count=4 / 4 条 verdict**（其中 `accept_claim` 恰 2 条：W1、X5 `accept []`，C1 仍按既有四码 reject，BAD 单独 `reject + 新码`）；`verdicts[1:]` 与只跑 `[W1,X5,C1]` 的 `verdicts` **逐字节相同**；良构-only 报告 sha before==after = `41bf0a402ee3cc23b9be49920f1546f04852604ce048c6ca617f6406d6a99648`（我的两像 + 他们登记值三者相同） | ✅ |
| 5 | NC-MISSING 7 行不被破坏 | 7 行 before==after **逐字节全等**；`S7a/S7b/S7c = accept_claim []`；`S8 = reject [R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]`，**不含 `R-CLAIM-EXCEEDS`**；`K7 = [R-SIMULATED-CLOCK]`；`S9 = 四码`；`S10 = accept []` | ✅ |
| 6 | 行不交界 | 见 §4：三外部区我独立重算**全部与派发值相等**，`foreign_hits = {}`；`_parse` 本体 `{89–95}` **包含**我的 `{89–92}` | ✅ |
| 7 | 合并链重建 | 见 §5：两步均**逐字节 True** | ✅ |
| 8 | `changes.diff` | 见 §6：29067 B / `693d6239fd958545…` / **+539 −23 / 恰 2 文件** / `src/`·`scripts/` 头 0 条 / 应用到左像逐字节重建修复后 SUT 与新测试 | ✅ |
| 9 | oracle 先冻后跑 + 两条 erratum | 见 §7：冻结体 24326 B = `539dbb389c3e70b9…` 仍是当前文件**不间断字节前缀**；`evidence/before` 101 个文件**全部早于 SUT 修改**；两条 erratum 只追加 | ✅ |
| 特别 A | ERRATUM-1 性质 | 见 §7.1：**合法追加式更正**，非事后改期望 | ✅ |
| 特别 B | 不自填 B1/B4/B5/B3 | 见 §8：**正确**；四条路径我逐条实测 before==after 逐字节不变 | ✅ |
| 特别 C | 仪器纠偏 IC-1/2/3 | 见 §9：全部在 SUT 修改之前（最晚 21:30:47Z < 21:33:43Z，SUT 之后 0 个文件）；IC-3 插件 sha 与对方登记值相同 | ✅ |
| 特别 D | 未跟踪路径披露 | 见 §10：**如实**（一处分组标签 ±1） | ✅（P3） |

**驱动聚合（我复跑）**：`probes` before 12/12、after 22/22；`gates` before==after（r2 `runner_rc=0/ok/34/34/mismatch 0`、`sut_report sha beb06495fcd93b2c…`；r1 `runner_rc=1/mismatch [W1]/sha 6fa04855e76205fa…`）；`suites` before `32/18/23/29` 全 0 failed + 新族 `6 passed/13 failed`，after `32/18/23/29` 全 0 failed + 新族 **`19 passed/0 failed`**；`ncmissing` 两相全绿；`vocab` 两相 check=true；`batch` 两相全绿；`invariants` **31 checks / 31 passed / PASS**（在「原始 RED 证据 + 我自己的 GREEN 复跑」的副本上与「完全未动的原始副本」上各跑一次，均 31/31）。

---

## 2. 词表 16 → 17 与「裸正则多计」的独立验证

我的独立脚本（不引用驱动的 `vocab_of`）在两像上各跑两条正则：

| 口径 | 左像 `9b1ebda2…` | 修复像 `d1ced6ac…` | 集合差 |
|---|---|---|---|
| `\bR-[A-Z0-9-]+\b`（冻结口径） | **16** | **17** | `after−before = {R-TIMESTAMP-MALFORMED}`、`before−after = ∅` |
| `R-[A-Z0-9-]+`（裸式） | **17** | **18** | 同上多一个新码；bare-only 恒为 `{R-UNKNOWN}` |

- 16 码（`\b` 口径，两像共有）：`R-ANCHOR-NOT-SHARED, R-BASIS-UNKNOWN, R-CLAIM-EXCEEDS, R-DUP-RUN-ID, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-LABEL-ANCHOR, R-NO-INTERVAL, R-NO-SAMPLES, R-POSTHOC-CAPTURE, R-QC-IN-OBS, R-SAME-INSTANT, R-SAMPLE-OUTSIDE, R-SIMULATED-CLOCK, R-SUM-OVERLAP, R-TOTAL-AS-OBS` —— 与 T1-10-FIX `reviewer_report.md` §7 列出的 16 码**逐字一致**。
- **实现者说法核验**：左像上裸式确为 17、带 `\b` 确为 16，且差集恰为 `R-UNKNOWN`（`R-UNKNOWN_CLASS` 中 `_` 是 word char，`\b` 版本在 `N` 与 `_` 之间无边界，因此整 token 被排除；裸式则被截成 `R-UNKNOWN`）。⇒ **该说法成立，`\b` 口径是唯一能复现 reviewer 16 码表的口径**。
- 归属：新增码的唯一授权来源是 §11.8 ③b（原文：「本节为该码的唯一授权来源；词表自 16 码增至 17 码」）；源码中**未出现第二个时间戳码**。

---

## 3. 四变异臂 + 批次负控：我的实测

| 臂 | 变异（驱动 anchor 出现次数=1） | mutant sha256（前16）/ 字节 | 我实测 | 冻结期望 | 判定 |
|---|---|---|---|---|---|
| MUT-F3-A | 整个 `_parse` 还原为修前原文 | `47788debe8b32622` / 30048 | TS1=4, TS2=4, TS3=4, TS4=4, TS5=4，全部 `report_written=false`、0 裁决 | 5/5 回 rc=4/无报告/0 裁决 | ✅ 真红 |
| MUT-F3-B | 删掉 `refusals.append("R-TIMESTAMP-MALFORMED")` | `bb2a3d136a166e11` / 30857 | 五臂全 rc=0，`verdict=accept_claim`、`refusals=[]` | 5/5 翻 accept（危险 accept） | ✅ 真红 |
| MUT-F3-C | `_echo_ts` 改回 `fields.get(key)` | `9fdf20649345971e` / 30785 | TS1 `computed.started_at = "not-a-timestamp"`；TS5 = 其列表原值 ⇒ **均非 null**（verdict 仍 reject） | TS1/TS5 不再 null（G2 红） | ✅ 真红 |
| MUT-F3-D | 删 `if started is None: obs_finished = None` 降级 | `a4f4987283275560` / 30849 | **TS1=4、TS5=4**（无报告）；**TS2=0、TS3=0、TS4=0**（仍 reject + 新码） | §6：TS-1 回 rc=4；ERRATUM-2 E2-c：TS-5 也须红，TS-2/3/4 仍绿属预期 | ✅ 真红 |

**批次负控（我的两像实测）**

| 臂 | 我实测 |
|---|---|
| B-NEG（before `[BAD,W1,X5,C1]`） | rc=**4**、`report_written=false`、**0 裁决**（炸批，区分度在） |
| B-POS（after 同批） | rc=**0**、报告写出、**4 条 verdict**；`verdicts[0] = reject_claim + ["R-TIMESTAMP-MALFORMED"]` |
| B-BYTE-1 | `json(verdicts[1:]) == json(good_only.verdicts)` ⇒ **逐字节相同 = true** |
| B-BYTE-2 | 良构-only 报告 sha 前后相等 = `41bf0a402ee3cc23…`（与实现者登记值一致） |

**附加（超出派发清单，我顺带复跑）**：20 臂变异棘轮 `mut20` —— 在第二份副本上**把左像还原进 worktree**后跑 before、再还原修复像跑 after：两相均 `mutation_count=20 / all_mutants_red_again=true / all_expected_cases_red=true / load_bearing=20`。（说明：该子命令不接 `--sut`，相位标签取决于当时 worktree 内的 SUT，故必须换像才能诚实复现 before。）

---

## 4. 行不交界：我从两前置 `changes.diff` 独立重算

方法：解析 D1/D2 的 hunk 头与 hunk 体 → 取**新侧 added/replaced 行**（仅 `' '`/`'+'` 消耗新侧行号）→ T1-F2 的新侧本来就在 L2，直接用；T1-10 的新侧在 L1，用 `difflib.SequenceMatcher(L1, L2)` 做等长/替换/删除/插入映射到 L2；defect-2 区 `{182–205}@L1` 同样映射。我的改动行集由 `difflib(L2, 修复像)` 按与他们相同的保守插入口径（插入记为前后两行）算出。

| 区 | 派发/实现者登记值 @L2 | **我的重算** | 相等 |
|---|---|---|---|
| T1-10-FIX 新增 | `{67–75, 81, 214–224}` | `{67–75, 81, 214–224}` | ✅ |
| T1-F2-FIX 新增 | `{56–63, 367–379, 461–476}` | `{56–63, 367–379, 461–476}` | ✅ |
| defect-2 | `{189–212}` | `{189–212}` | ✅ |
| `_parse` 本体 | `{89–95}` | L2:89 = `def _parse(ts: str) -> datetime:`（修前体） ⇒ 确为 `_parse` 本体 | ✅ |
| 我的改动+插入行集 | `89-92,104-105,123-124,130,132,134-135,150-151,152,167,170-173,249-250,253,259,287-288,417-419,424,489-490,515-516` | 同一集合（我的合并表示把 `150-151,152` 合成 `150-152`，行集相同） | ✅ |

- **交集**：我的行集 ∪ 三个外部区 = **∅**（`foreign_hits = {}`）；与 `{89–95}` 的关系 = **包含**（`89–92 ⊆ 89–95`）。
- **加严复核**：即使把外部区放大到**含上下文的整 hunk 包络**（T1-10 映射后 `64–84 / 211–227`，T1-F2 `53–66 / 364–382 / 458–479`），交集仍为 ∅ ⇒ 结论对口径不敏感。
- **内容抽查**（L2 实读）：`67–75/81` = T1-10 的 `BASIS_REGISTRY = (`…`)` 注释+元组；`56–63` = T1-F2 的 `TRUSTED_CLOCKS = (...)` 注释+元组；`189–195` = defect-2 的 quick_check/`[(started, obs_finished)]` 区；`461–464` = T1-F2 的 P4 容器归一块 —— 与 oracle §3 的描述逐条吻合。
- 与 `evidence/after/line_disjointness.json`（`715021966b9ed8fa…`，sha 已核）记录值**一致**。

---

## 5. 合并链独立重建（逐字节）

用我自己的 unified-diff 应用器（非 `analyze_chain.py`）：

| 步 | 输入 | 我算出的 sha256 | 目标 | 结果 |
|---|---|---|---|---|
| 1 | `apply(D1 625ecfe45f3d713a…, L0 7fff6f0c1e8ab202…)` 20293 B | `064e5381444d35a8…` | L1（`T1-10-FIX/.../worktree/i14b/iso/natural_window.py` 21416 B） | **逐字节相等 = True** |
| 2 | `apply(D2 bc87bf81bc53aad1…, L1)` | `9b1ebda2b75c4d11…` | L2（本卡 `baseline/…pristine.py` 与 `T1-F2-FIX` worktree，均 23534 B） | **逐字节相等 = True** |

前置齐备、可复现，本卡确实从合并末态起算。

---

## 6. `changes.diff` 判定

- 29067 B · sha256 `693d6239fd958545bc05ad8d246758f2bb47a4ca10de37187c2f9454fadaf5ba` = 派发/登记值 ✓
- 独立计数：**`lines_added=539`、`lines_removed=23`、文件数=2** ✓（`+++ b/` 头：`iso/natural_window.py`（修改）、`harness/tests/test_i14b_natural_window_timestamp_total.py`（新增））
- **`+++ b/src/` 0 条、`+++ b/scripts/` 0 条** ✓（不动生产 `src/`、不把脚本夹带进 diff）
- **可逆重建**：把 diff 应用到左像 `9b1ebda2…` ⇒ 重建文本 sha `d1ced6ac566d41cb…` 与修复后 SUT **逐字节相同**；新增测试重建 sha `5e6644fa508a185c…` 与 `worktree/.../test_i14b_natural_window_timestamp_total.py` **逐字节相同** ✓
- `diff_stats.json`（2530 B / `cfcfe46d…`）与我的独立重数五项（bytes/sha/added/removed/files）全部相等（驱动 `invariants` 的对应 check 亦 PASS）。
- 判定：**diff 与登记值、与两像状态完全自洽，可作为落库/合并候选交父方裁**（合并序 D1 `625ecfe4…` → D2 `bc87bf81…` → 本卡 `693d6239…`）。本复审**不裁**是否落库。

---

## 7. oracle「先冻后跑」与两条 erratum

**冻结与追加（我实测）**

- 当前 `oracle.md` 31227 B / `ba17f83740104190…`；**前 24326 B 的 sha256 = `539dbb389c3e70b9df68004c93b5ccce9091046dc2fcd130f90d051eda81ef63`** = `handoff`/`freeze.json` 登记的冻结体 ⇒ **冻结体是当前文件不间断字节前缀**（一字未回改）。
- `ERRATUM-1` 起于偏移 **24332**、`ERRATUM-2` 起于 **27082**，均在 24326 之后 ⇒ **纯追加**；文件无 BOM、无 CRLF。
- **时序（UTC）**：oracle 冻结体 mtime `21:15:15` → `freeze.json` 落盘 `21:25:10` → `evidence/before` 最晚 `21:31:38`（101 个文件，**晚于 SUT 修改的 = 0**）→ **SUT 修改 `21:33:43`** → oracle 两条 erratum `21:40:49` → `changes.diff` `21:41:40` → `decision.md` `21:42:48` → `handoff.json` `21:45:57`。
- `evidence/instrument_runs/**` 最晚 `21:30:47`，**晚于 SUT 修改的 = 0**。

### 7.1 ERRATUM-1 的性质判定：**合法的追加式更正**（非事后改期望）

判据逐条（按派发单给的三条）：

1. **可从冻结输入独立重算**：✓ 我用 §4 冻结常量 + 修复后 SUT 自身定义（`offset = _secs(anchor_at, sampled)`、`offsets.append(int(round(offset)))`、`errors.append(abs(offset - float(label["name"])))`、`label_count = len(labels)`）手算：label0 offset=**0**、label1 `sampled_at` 畸形 ⇒ 不贡献时序事实、label2 offset=`00:00:10−00:00:00`=**10** ⇒ **`label_offsets_seconds = [0, 10]`**；`errors = [0,0]` ⇒ `max_error = 0.0`；latency `max = 0.0`；`label_count = 3`。**与观测无关地**得出同一值。
2. **只动该单值**：✓ 冻结体内仍是 `label_offsets_seconds=[0,0]`（我字节级确认：`[0,0]` 在前 24326 B 内为真、`[0,10]` 为假），更正只存在于追加段；前缀哈希证明其余期望一字未改。
3. **其余期望一字未改**：✓ 同上前缀证明；TS-1/2/3/5、DOC-2、CTRL-4、§5 九条不变量、§6 四臂、§7 批次负控、§8 边界均在冻结体内。

**结论**：该笔误（把 offsets 写成 errors）**唯一由冻结输入决定**，且实现者已如实披露「GREEN 首跑发现该红之后追加」「该条不作为先于观测冻结的证据、标注更正后复测」——`handoff.unverified` 亦重申。这是**合法的 append-only 更正**，不是按结果改 oracle。同步改到测试断言（新族中 `label_offsets_seconds == [0,10]`，`[0,0]` 断言 0 处）与 erratum 同源同值 ✓。

### 7.2 ERRATUM-2 逐条核

| 项 | 内容 | 我的核验 |
|---|---|---|
| E2-a | E7（`derive_calendar` 三处 None 守卫）未实施 | ✓ 我的改动行集在 L2 **318–357 段为 0 行**（我的行集最近的是 287–288 与 417–419）⇒ 改动面确实比计划更小 |
| E2-b | MUT-F3-A 执行取法 = 整函数还原 | ✓ 驱动 `ARM_A` 的 old 锚是**完整新 `_parse`**（含 docstring/isinstance/try）、new 是**修前体**，anchor 恰 1 次；实测 5/5 rc=4 = 冻结期望。补充：只删 `except` 两行会留下 `try:` 无子句 ⇒ 语法错 rc=1，且 isinstance 护栏会让 TS-5 保持绿，与同一行冻结的「TS-1…TS-5 全部」自相矛盾 ⇒ 该澄清是**实现冻结期望的必要手段，且未放宽判据** |
| E2-c | MUT-F3-D 红判据（TS-1 **与** TS-5 都须红；TS-2/3/4 仍绿属预期） | ✓ 实测 `TS1=4, TS2=0, TS3=0, TS4=0, TS5=4`。冻结 §6 只要求 TS-1 红 ⇒ 新增的 TS-5 要求**更严**，非放宽；TS-2/3/4 冻结未要求红 |
| E2-d | 新增边界 B5（`labels[].name` 非数值 → rc=4） | ✓ 我独立实测 `"abc"` 与 `null` 两形：两像均 rc=4、stdout 逐字节相同 |
| E2-e | §3 声明的实测行集与 `changes.diff` 统计 | ✓ 与我第 4、6 节的独立重算**逐项相等** |

**结论**：ERRATUM-2 未改动任何冻结判据，只登记「计划落点被更小落点取代 / 变异执行细节澄清 / 新边界 / 实测结果」，与 §4/§5/§6/§7/§8 的冻结值不冲突（前缀证明）。

---

## 8. 「不自填 B1 / B4 / B5 / B3」是否正确：**正确**

**授权相交的读法（回源）**

- §11.8 ③b（唯一授权来源）只给：`_parse` 抛 `ValueError` 的**时间戳畸形**形状 + **一个**新码 `R-TIMESTAMP-MALFORMED`（「本节为该码的唯一授权来源」）+ 受影响时间字段置 null。
- §11.8 ③a 把容器/载体族划给 T1-F2-FIX；§11.8 rc=2 的枚举只列「`--cases` 不可解析 / 顶层缺 `cases`/`frozen_now_utc` / `frozen_now_utc` 不可解析」三形，**未列类型错**。
- 本卡冻结 oracle §5 **I-2「缺键行为不变（NC-MISSING）」**、§8 项 1 明写「缺键路径一字不改」。⇒ **两令相交 ⇒ 不自填是对的**；给非时间戳字段配码 = 引入第二个新码 = 越权。

**我的行为实测（两像对照，证明「没碰」是真的没碰）**

| 边界 | 形状 | before | after | 判定 |
|---|---|---|---|---|
| B1 | window case 缺 `fields["started_at"]` | rc=4、无报告、`detail "'started_at'"` | **逐字节相同** | 未自填 ✓ |
| B4 | 顶层 `"cases":"abc"`（CTRL-4） | rc=4、`"'str' object has no attribute 'get'"` | **逐字节相同** | 未自填 ✓ |
| B5 | `labels[].name = "abc"` / `= null` | rc=4、`could not convert string to float: 'abc'` / `float() argument must be … not 'NoneType'` | **逐字节相同（两形）** | 未自填 ✓ |
| B3 | `windows = ["x"]` / `ledger.daily = ["x"]` | rc=4、`string indices must be integers, not 'str'` | **逐字节相同（两形）** | 未自填 ✓ |

四条**是否该改成 per-case 拒绝、配哪个码** = 裁权在 owner，本复审**不裁**，仅确认实现者「未自填、如实登记为 open_questions」这一处置**正确**。

补充证据：新测试族里专设 `test_missing_required_timestamp_key_still_raises_keyerror`（`test_i14b_natural_window_timestamp_total.py:334`），把「缺键仍 KeyError→rc=4」**钉成断言** ⇒ 「不自填」不是漏做，而是被测试固化的有意边界。

---

## 9. 仪器纠偏 IC-1 / IC-2 / IC-3（IC-4 见 §7.1）

- **全部在 SUT 修改之前**：`evidence/instrument_runs/**` 最晚 mtime `21:30:47Z`，SUT 修改 `21:33:43Z`，**晚于 SUT 的文件数 = 0**；README 自述「三次仪器运行期间 SUT 字节恒为 `9b1ebda2…`」与 `freeze.json.sut_worktree_at_freeze`（`9b1ebda2…`、`equals_baseline=true`）一致。
- **只改仪器不改判据**：IC-1 改的是 direct-classify 子探针的输入切片（`['cases']` → `['cases'][0]`）并整族重跑；IC-2 改的是**期望表的码序**（`sorted`），实测值自始未变 —— 我复跑的 `S9 = [R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]`（字典序）与之一致；IC-3 只加 pytest 目录 mode 的插件。
- **IC-3 插件 sha**：本卡 `scripts/pytest_tmp_acl_plugin.py` = `e96890fe3275a6ef72063b0c112afdd6607a2b4ae50c08cdd8664594f0002aa3` / **1725 B**，与 `T1-F2-FIX` 目录内同名文件**逐字节相同**，且等于其 `decision.md` 的登记值 ✓。
- **我的复跑也依赖它**：在 `%TEMP%` 副本上，去掉 `_pytest_tmp` 父目录会精确复现 IC-3 描述的 `FileNotFoundError [WinError 3]`；补上父目录后 5 个套件计数与登记值完全一致 —— 插件与旁路（`g1_` 前缀）确实只影响目录 mode，不影响断言。

---

## 10. 未跟踪路径披露核对（只核、不删）

- 强制项 `git -c core.quotepath=false diff HEAD --name-only` 我在复审结束前实测：**total = 3826、非 `.planning` = 0**（与 `freeze.json.git_boundary_before_run` 记录的 `3826 / 0` 相同）。
- 额外 `git ls-files --others --exclude-standard`：**非 `.planning` 可见条目 = 48**（`.tmp-r41-mutation/**` 45 + `h2.log` + `h2.log.err` + `assurance/unified_completion/manifests/plan_inputs.json.bak`），另有 `probe_root_m700/` 因权限 git 无法枚举（warning: Permission denied）。
- 与实现者披露的 50 对账：`45 + 1 + 2 + probe_root_m777/f.txt + probe_root_m777kw/f.txt(各 1 B) = 50` ✓ **总数对得上**；这 2 个 `probe_root_m777*` 已由父方移入 `I-14-E-TESTSIDE/a20260924-01/evidence/probe_root_removed_from_repo_root/` 并从仓库根消失（我实读到两份 1 B `f.txt`）⇒ 现在 48 = 50 − 2 ✓。
- **归属与处置**：`h2.log` mtime `2026-09-25 21:01:12`（早于本卡 freeze `21:25:10`）、`.tmp-r41-mutation/**` mtime `2026-09-20`、`plan_inputs.json.bak` `2026-09-21` ⇒ **均非本卡命令产物**；**无一落在 `execution_runs/T1-F3-FIX/**`**；实现者「只披露不删除」的处置**如实且恰当**（删除他卡文件本就越界）。
- 唯一瑕疵见 P3-4（分组标签 `(46)` 实为 45，总数 50 正确）。

---

## 11. 只读边界（本复审自身）

- 生产树零写入；本 attempt 内仅新建 `reviewer_report.md` + `reviewer_report.sha256` 两个文件；未触 `handoff.json`/status/任何既有字节（交付前后我对 18 个登记 sha 全部复核，见 §12 前置哈希表）。
- 未使用 `git status`；git 调用仅两条只读：`git -c core.quotepath=false diff HEAD --name-only`、`git ls-files --others --exclude-standard`；无 add/commit/checkout/restore/reset/stash。
- 无联网；测试全部在 `%TEMP%` 隔离副本；**未修改** I-14-B `oracle.md`、两前置卡、五份计划文件。
- 沙箱曾拒绝一次 `%TEMP%` 内自建目录写入（`tempfile.mkdtemp` 的 0o700 → 本机 ACL），我改为普通 `mkdir` 后成功，**未做第 2 次以上重试**；另我第一次复制时排除 `_pytest_tmp` 导致套件复跑报 `WinError 3`（环境差异，非产品缺陷），补建父目录后复跑正常，已在 §9 记录。

---

## 12. 哈希复核（我实算，全部 = 登记值）

| 对象 | 实测 sha256（前16） | 字节 |
|---|---|---|
| 本卡 `oracle.md` | `ba17f83740104190` | 31227 |
| 冻结体（前 24326 B） | `539dbb389c3e70b9` | 24326 |
| `handoff.json` | `b636707f23a44774` | 19808 |
| `decision.md` | `cb848f058258f23c` | 12296 |
| `binding.json` / `commands.json` | `a89f3bd2b9ba21c6` / `90117d88fb834966` | 8866 / 9381 |
| `changes.diff` | `693d6239fd958545` | 29067 |
| `diff_stats.json` | `cfcfe46d1b5ab791` | 2530 |
| 左像 `baseline/…pristine.py` | `9b1ebda2b75c4d11` | 23534 |
| 修复后 SUT | `d1ced6ac566d41cb` | 30210 |
| 新测试族 | `5e6644fa508a185c` | 16144 |
| `scripts/verify_t1_f3_fix.py` | `c311fe9722158bc9` | 59379 |
| `scripts/analyze_chain.py` | `6eb4ddede5808140` | 8687 |
| `scripts/pytest_tmp_acl_plugin.py` | `e96890fe3275a6ef` | 1725 |
| `evidence/after/invariants.json` | `c608fce75d9abe99`（31/31 PASS） | 9093 |
| `evidence/after/line_disjointness.json` | `715021966b9ed8fa` | 2146 |
| `evidence/after/mutations/results.json` | `8859313a136456d1` | 801 |
| `evidence/instrument_runs/README.md` | `137b1459ba22b15e` | 3404 |
| `recovery/README.md` | `7914ed64b63f3510` | 2069 |
| **I-14-B `oracle.md`（权威）** | `b1eb5d0cf83dd8f0` | 28930 |
| T1-10-FIX `changes.diff` / `handoff.json` | `625ecfe45f3d713a` / `e6b9a94a40313b9a` | 11534 / 26509 |
| T1-F2-FIX `changes.diff` / `handoff.json` | `bc87bf81bc53aad1` / `662b7895114399c1` | 20153 / 43425 |
| T1-10-FIX `review.md` / `reviewer_report.md` | `1ab78c3d712ecef4` / `96847e0a9e2d01db` | 24335 / 30247 |

`binding.json` 的 harness pin 与 `freeze.json.harness_pins`（10 个 harness 文件）**逐项相等且等于 binding 登记值**（`I-7a/I-7b` 我复跑均 PASS）。

---

## 13. 发现分级

**P1：无。P2：无。**

P3（不阻断，供父方/下轮参考）：

1. **P3-1（文档精度）** 冻结 oracle §3 表中 T1-F2-FIX 的「**新侧全 hunk** = `53–63 / 364–379 / 458–476`」与 difflib 头本身不符（`@@ -53,7 +53,14 @@` 的新侧全 hunk 实为 `53–66`；另两处实为 `364–382`、`458–479`）—— 该列实际给的是「上下文起点 → 改动终点」。**受影响的断言口径是「新增内容 = 56–63 / 367–379 / 461–476」，我重算完全正确；且即便按整 hunk 包络加严，交集仍为 ∅** ⇒ 结论不受影响。
2. **P3-2（判据覆盖）** `cmd_mutations` 对臂 4 的红判据只要求 `TS1/TS5 == rc=4`，**不校验 `TS2/3/4` 仍 rc=0**（E2-c 声称其为预期）。实测确为 0/0/0，但驱动未把该预期固化为 check。
3. **P3-3（判据覆盖）** `cmd_batch` after 相的 `B-BYTE-2` check 是硬编码 `ok=True` 占位（真正跨相比较放在 `invariants`）；我已**自行逐字节验证**良构-only 报告 sha 前后相等，故事实成立，但该子命令单独跑时会给人「B-BYTE-2 已验」的错觉。
4. **P3-4（披露精度）** `handoff.boundary.untracked_non_planning_disclosure` 把 `.tmp-r41-mutation/**` 记作 **(46)**，我实测 **45**（总数 50 正确：45+1+2+2）。
5. **P3-5（复现性提示）** 驱动的 `probes/gates/ncmissing/vocab/batch` 的 `--sut` **默认指向 worktree（修复像）**，复审者若不显式传 `--sut <left image>` 会把 `--phase before` 静默跑在修复像上；`commands.json` 里 before 相显式带了 `--sut`，故实现者没错，但这是驱动的易错点（我复跑时全部显式传参）。
6. **P3-6（表述计数）** oracle §5 I-7 / handoff / decision.md 称「**11 个 harness pin**」，而 `binding.json.harness_pins_byte_identical_through_the_run` 实为 **10 个 harness 文件**（另含 1 条 I-14-B oracle + 2 条目录级 0 字节声明 + 1 条 note，共 14 键）；若把 oracle 计入则为 11 个被 pin 文件，但那样 §5 又把它与「I-14-B oracle」并列重复计数。实质（全部 pin 三次 sha 相等）我已验证成立。
7. **P3-7（观测口径）** `evaluate_probes` 的 GREEN `computed` 比较只比对冻结期望表里**列出的键**（多余键不会失败）；良构路径的字节同一性由 `gates` 另行覆盖，故风险有限。
8. **P3-8（证据易碎性，非产品缺陷）** `invariants` 的 temporal 检查读的是 `evidence/before/**` 的 **mtime**；我在第一份副本上**就地重跑 before 相**后该项翻红（30/31），把原始 before 证据原样还原后即回 31/31，且生产树上该检查本为真（101 文件最晚 `21:31:38` < SUT `21:33:43`，晚于者 0）。⇒ 该 check 对「复审者就地重跑」敏感，建议将来改用证据内嵌的 run 时间戳或在 after 相重新落盘前先快照 before。

---

## 14. 未验证 / 限制（unverified）

1. **`evidence/before/*` 由脚本早期版本生成**（handoff 自曝的三处差异：S9 码序表、TS4 GREEN 表、变异臂定义）—— 旧版本未留存，**我无法逐字节比对两版脚本**；但我在隔离副本上**独立复跑 before 相全部判据**（probes 12/12、gates、suites 32/18/23/29、ncmissing 7/7、vocab 16、batch B-NEG、mut20 20/20），结果与其登记值一致 ⇒ 该披露对结论无实质影响。
2. **未复跑 `freeze` 与 `diff` 子命令**（二者会覆写 `evidence/freeze.json` / `changes.diff` / `diff_stats.json`，越我写入面）；改为对这些产物做哈希与内容独立核验。
3. **新测试族 16144 B 我未逐行通读**：实读到 **15 个 `def test_*`**，其中 1 个按 `TS_CASES = {TS1…TS5}`（5 例）参数化 ⇒ **14 + 5 = 19 例**；TS-4 断言值为 `[0, 10]`（`[0, 0]` 断言 0 处）；并以 empirically RED（6 passed/13 failed）→ GREEN（19 passed/0 failed）验证。
4. **未裁** `changes.diff` 是否落库/合并、未裁 B1/B4/B5/B3 四条边界的最终归属、未裁 F-1/F-2/P4 复审结论 —— 均属父方/owner。
5. 解释器差异：实现者用 I-14-B venv `python.exe`，我用系统 `python`（同为 3.13.9，pytest 同为 9.1.1），结果逐项一致，但我未逐文件比对两解释器环境。
6. `probe_root_m700/` 因权限不可枚举，我只能确认其**存在**与 git 无法列出，未核其内容（父方已登记「删不掉」）。
7. 实现者称「4 个未跟踪文件 mtime 落在本卡时间窗内」—— 现存项中最早的 `h2.log` 为 `21:01:12`（早于 freeze `21:25:10`），被移走的两个 `probe_root_m777*` 我已无法取其原 mtime，**该句只作部分核实**。
8. 我在 `%TEMP%` 副本上的**第一次** `invariants` 出现 30/31（唯一红 = temporal），原因见 P3-8：是我先在同一副本重跑了 before 相，把 `evidence/before/**` 的 mtime 刷新到 SUT 修改之后。**这不是实现者的缺陷**：还原原始 before 证据后 31/31，未动的干净副本亦 31/31，且我独立在生产树上算过该判据为真。报告中所有 31/31 均指还原后/干净副本的结果。

---

## 15. 我**没有**做的事（边界声明）

1. 没有修改本 attempt 的任何既有字节（`oracle.md` / `handoff.json` / `changes.diff` / `decision.md` / `evidence/**` / `scripts/**` / `_pytest_tmp/**` 全部原样；§12 表内全部登记 sha 逐一复核相等）。
2. 没有写 `handoff.json`、没有改 status、没有替实现者落定，**没有在 handoff 里写任何 verdict 词**；本报告的 `VERDICT:` 只属于我这份 reviewer 文件。
3. 没有裁 B1/B4/B5/B3 四条边界（只判断「不自填」是否正确 —— 结论：正确）。
4. 没有修改 `I-14-B/oracle.md`（`§11.8` 只读，**未追加**）、没有改两前置卡任何字节或 status。
5. 没有写五份计划文件（`task_plan.md` / `findings.md` / `progress.md` / `REMEDIATION_REGISTER.md` / `OWNER_DECISIONS.md`）。
6. 没有执行任何有状态 git 命令、**没有用 `git status`**、没有 add/commit/merge/apply/晋升任何 `changes.diff`（零生产合并）。
7. 没有联网。
8. 没有删除或改动任何未披露/已披露的未跟踪路径（只披露核对）。
9. 测试没有在生产树上跑 —— 全部在 `%TEMP%` 隔离副本；沙箱拒绝后没有绕道重试超过 1 次。
10. 没有把本复审的中间产物（脚本、副本、临时目录）写进 attempt 或生产树。
