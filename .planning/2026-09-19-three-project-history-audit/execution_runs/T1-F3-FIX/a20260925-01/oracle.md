# T1-F3-FIX oracle（**运行前冻结** · 2026-09-25 · attempt `a20260925-01`）

**卡**：`T1-F3-FIX`（F-3 独立修轨）· **实现者**：父派 subagent（不自签 ACCEPT）· **父 agent**：`session-19074bf0-0205-4315-af73-9db57597275a`。

**冻结声明**：本文件在本卡**任何 SUT / harness / pytest 运行之前**写成并落盘；RED、GREEN、变异、批次负控、词表、行不交界的**期望值全部先于观测**给出。冻结后本文件**只许追加式 erratum**，一字不回改。冻结前只发生过两类操作：(a) 只读文件读取与 sha256 计算；(b) `scripts/analyze_chain.py` —— 一个**只读** unified-diff 解析 + difflib 行号映射脚本（读三份文本、写 `evidence/line_zones.json`），**不执行任何产品代码、不产生任何 expected**。

**权威原文（回源读，非转述）**：`execution_runs/I-14-B/a20260919-01/oracle.md` 的 `### 11.8` 节（L274–294，全文 294 行；文件 sha256 `b1eb5d0cf83dd8f059d7f011427447a4b79b211c19167f0190b2c140cb34ade6` / 28930 B，只读、零写入；前像 `bdd0407a…` / 26554 B）。两处 `T1-10-FIX` 载体亦已回源读：`review.md` §7（L73–131，sha `1ab78c3d…` / 24335 B）、`reviewer_report.md` §7.3（L159–216，sha `96847e0a…` / 30247 B，`reviewer_report.sha256` 读回一致）。协议：`execution_v2/START_HERE.md`、`execution_v2/review_and_handoff.md`。

**SUT**：`worktree/i14b/iso/natural_window.py`（隔离副本；源树 **READ-ONLY**，交付只走 `changes.diff`，零生产合并）。

---

## 1. 从 `### 11.8` 读到的裁定要点（逐条，逐字回源）

| # | §11.8 原文要点 | 本卡落点 |
|---|---|---|
| ① | **rc=2 = 仅「文档/调用域」的输入畸形**：`--cases` 不可解析、顶层缺 `cases`/`frozen_now_utc`、或 `frozen_now_utc` 本身不可解析 —— 即 `main()` 在**进入任何 case 判定之前**失败的那批形状（既有实现 L461–466）。fail-closed 在此**不剥夺任何裁决（此时本无裁决）**。 | `_parse` 变全函数后，`main()` 里 `_parse(frozen_now)` 不再抛错 ⇒ **必须显式补一道 None 检查并 raise**，否则 rc=2 域会塌成 rc=4/traceback。见 §5 的 `DOC-2` 探针。 |
| ② | **rc=4 = 仅真正的内部错误**（实现自身缺陷）。**用户提供的单 case 字段**类型/格式错误不属于 rc=4：把它记成 rc=4 既属误分类，又**复现缺陷①的「剥夺裁决」形态**（报告不写出、整批 0 裁决）。 | RED 形态（rc=4 / 无报告 / 0 裁决）就是本卡要消灭的观测面；`CTRL-4` 探针同时证明 rc=4 机关**未被整体吞掉**。 |
| ③ | **单 case 字段的类型/格式错误 = per-case 拒绝**：该 case 记 `reject_claim`、**整批照常裁决、报告照常写出、SUT rc=0**；与 §11.3 标量校验同语义。 | GREEN 判据的主体（§5 表 GREEN 列）。 |
| ③a | `basis` 容器 / `claim` 载体非对象 / `clock_source` 容器 / `windows`、`sampled_at`、`ledger.daily` 为容器 → **按既有码拒绝**（basis/载体族 = `R-BASIS-UNKNOWN`；时钟 = `R-SIMULATED-CLOCK`；**载体不可读 ≡ 缺键**）。 | **不归本卡**：这是 T1-F2-FIX 的 F-1/F-2/P4 面，已 `accepted_scoped`。本卡**不新增、不改写**这些码与路径（不变量 I-4）。 |
| ③b | **时间戳畸形（`_parse` 抛 `ValueError`，如 `started_at="not-a-timestamp"`）→ `reject_claim` + 新码 `R-TIMESTAMP-MALFORMED`**（**本节为该码的唯一授权来源**；**词表自 16 码增至 17 码**），**无法解析的时间字段在 `computed` 中置 `null`，其余派生量按可得事实计算**。 | 本卡的**全部**机制：`_parse` 全函数化 + 新码 + `computed` 时间字段置 null + 其余量按可得事实。 |
| ④ | **变异/回归要求**：任一畸形单 case 字段**不得使任何其他 case 的裁决丢失** —— 回归面同缺陷①：**批次臂 rc=0、坏 case 单独被拒、良构 case 输出逐字节不变**；且须带「**单畸形 case 不可炸批**」的批次负控。 | §7 批次负控（含 before 炸批的区分度对照）。 |
| ⑤ | 触发与授权链：`I-14-B review.md:353`（P4 提请）→ `T1-10-FIX oracle §7 E-adj-4 / I-5`（实现卡拒绝自填）→ 本裁定（T1-10-FIX 独立 reviewer，2026-09-24，N=1）。 | 本卡**不代填**任何未裁事项；边界见 §9。 |
| ⑥ | 落点分工：**F-3（时间戳 `_parse` 非全函数）→ 独立修轨 T1-F3-FIX**（机制 = 解析全函数化，与 F-1/F-2 的成员/载体守卫不同，且 T1-F2-FIX 已派未含此项）；两卡共用本节文本。 | 本卡只动 `_parse` 时间戳轨；与 T1-F2-FIX 的行不交界见 §3。 |

**§11.8 追加文的两处易误读点（照 `reviewer_report.md` §7.3 读回）**：(i) 「rc=4 仅真内部错误」**不是**说所有 rc=4 都要消灭 —— 而是说**用户单 case 字段错不许再落进 rc=4**；(ii) 新码 `R-TIMESTAMP-MALFORMED` **只有一个授权来源 = 本节**，任何别处不得再引入第二个时间戳码。

---

## 2. 影像与合并序（本卡实测，非引用）

| 影像 | sha256 | 字节 | 行 | 角色 |
|---|---|---|---|---|
| L0 = `I-14-B/iso/natural_window.py` | `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` | 20293 | 497 | r2 生产前像（canonical pin10） |
| D1 = `T1-10-FIX/changes.diff` | `625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac` | 11534 | — | 第一层 |
| L1 = T1-10-FIX 修复后 iso | `064e5381444d35a8ab1184d6c8d2eaa839a40f96c704ae7995fa3b660c7e273d` | 21416 | 514 | 中间像 |
| D2 = `T1-F2-FIX/changes.diff` | `bc87bf81bc53aad17f5c2f1047db467c64a92ec0b431499d94a438e8cbd3f3ca` | 20153 | — | 第二层 |
| L2 = T1-F2-FIX 修复后 iso | `9b1ebda2b75c4d1124d0d20a95d7a16cb31b8d9564c1c90da9b4d2d77eaa3ba2` | 23534 | 549 | **本卡左像 / RED 前像 / diff 左基** |

- **两前置均 `accepted_scoped`**（`T1-10-FIX` handoff 26509 B / `e6b9a94a…`；`T1-F2-FIX` handoff 43425 B / `662b7895…`，两者 `implementer_signed=false`）。
- **本卡独立重建合并链**（`scripts/analyze_chain.py`，只读）：`apply(D1, L0) == L1` **逐字节 True**；`apply(D2, L1) == L2` **逐字节 True**（重建 sha = `9b1ebda2…`）。⇒ 前置齐备且可复现，本卡从合并末态起算。
- **本卡左像副本**：`baseline/natural_window.t1_f2fixed.pristine.py`（`9b1ebda2…` / 23534 B，复制时校验相等）；iso 拷贝来源 = `T1-F2-FIX/a20260923-01/worktree/i14b/`（346 文件 / 4077963 B，只读复制，回写 0 字节）。

---

## 3. 行不交界声明（**冻结**；测量方法与数据先于修改给出）

**坐标系**：下表前两列是**在本卡左像 L2（`9b1ebda2…`，549 行）上的实测行号**，由 `scripts/analyze_chain.py` 从两份前置 `changes.diff` 的 hunk 头 + difflib 行号映射算出（原始数据：`evidence/line_zones.json`）。派发单引用的 `{…}` 是**在 L1（`064e5381…`）上的原值**，本表逐条给出 L1 → L2 的映射，不采信转述。

| 外部区（派发单给的原值 @L1） | 原值 @L1（实测） | 映射到本卡左像 L2（实测） | 内容 |
|---|---|---|---|
| **T1-10-FIX `{60-74, 207-217}`** | 新侧行 `60–68`、`74`、`207–217`（包络 `60–74` / `207–217`） | **`67–75`、`81`、`214–224`**（包络 `67–81` / `214–224`） | `BASIS_REGISTRY` set→tuple 注释+元组（75=`BASIS_REGISTRY = (`，81=`)`）；E1 claim 载体守卫 |
| **T1-F2-FIX `{56, 360}`（改动目标行）** | `56` = `TRUSTED_CLOCKS = {…}`；`360` = 日历 `claim.status` 载体读行 | **`56–63`**（56–62 注释 + 63 `TRUSTED_CLOCKS = (`）；**`367–379`** | F-1 J7 tuple 化；F-2 载体守卫 |
| **T1-F2-FIX `{53-59, 357-363, 439-444}`（hunk 旧侧行）** | `53–59` / `357–363` / `439–444`（= difflib hunk `@@ -53,7 +53,14 @@`、`@@ -357,7 +364,19 @@`、`@@ -439,6 +458,22 @@`） | 新侧全 hunk = **`53–63`** / **`364–379`** / **`458–476`**（其中**新增内容** = `56–63` / `367–379` / `461–476`；458=`def classify(`、477=`fields["_claim"]` 为上下文） | P4 容器归一块在 L2 的 `461–476` |
| **defect-2 `{182-205}`** | `182–205`（= r2 基线 `174–197` + T1-10 的 8 行位移） | **`189–212`** | quick_check 区间 / J15 / J1–J3 union 计算 / J5·J4·J4b·J15·J6 拒绝块 —— T1-10-FIX oracle I-1 明令其 diff 变更行与之交集为 ∅，缺陷②**维持接受、字节不触** |
| **`_parse` 本体 `{82-88}`** | `82–88` | **`89–95`**（`def _parse(` 实测 = L2:89） | **← 本卡唯一授权作用面** |

**本卡计划改动落点（在 L2 上，冻结于修改之前）**：

| # | 计划改动 | 落点（L2 旧行） | 所属自由区 |
|---|---|---|---|
| E1 | `_parse` 全函数化（`isinstance` + `except ValueError → None`） | **89–95** | `82–188`（= `_parse` 本体区，唯一授权） |
| E2 | 新增 `_echo_ts` / `_bad_ts_slot` / `_malformed_time_fields` / `_TS_FLOOR` 四个纯函数与常量（插在 `_opt` 之后） | 插入点 **104–107 之间**（纯插入，旧行改动集为空） | `82–188` |
| E3 | `_all_timestamps` 跳过解析不出的时间戳 | **123–136** | `82–188` |
| E4 | `derive_window`：`started` 不可解析 ⇒ 观察窗两端不可用；`sample_stamps` 过滤；`command_total` 守卫；`explicit` 窗口对过滤 | **145–173** | `82–188`（上界 173 < 189） |
| E5 | `computed` 三处时间回显改走 `_echo_ts`；`schedule_lag_seconds` 守卫 | **248–261** | `225–363`（下界 248 > 224） |
| E6 | `_eligible` 排序键加时间地板、J6 加 None 守卫 | **281–315** | `225–363` |
| E7 | `derive_calendar` daily/weekly/monthly 三处 None 守卫 | **318–357**（上界 357 < 364） | `225–363` |
| E8 | `derive_login` 标签时间 None 守卫（`label_count`、evidence_kind 检查保留全量标签） | **412–430** | `380–457` |
| E9 | `classify` 在分派**之后**追加新码（`refusals` 在分派内被整体重赋值，故必须后置） | 插入点 **488–489 之间**（纯插入；`461–476` 是 T1-F2-FIX 的新增内容，不得触） | `477–549` |
| E10 | `main()` 文档域补 `frozen_now is None → raise`（保住 rc=2） | **512–518** | `477–549` |
| E11 | 新增测试族 `harness/tests/test_i14b_natural_window_timestamp_total.py` | **新文件** | 不在任何既有文件的行空间内 |

**断言（冻结）**：本卡 `changes.diff` 在 L2 上的**改动行集**（added + replaced 的旧行）与上表四个外部区
`{67–75, 81, 214–224}` ∪ `{56–63, 367–379, 461–476}` ∪ `{189–212}` 的**交集必须为空**；
与 `_parse` 本体区 `{89–95}` 的关系是**包含**（本卡的作用面）而非冲突。**测量在修改完成后落盘** `evidence/after/line_disjointness.json`（同 `analyze_chain.py` 的口径），并在交付消息中报告；oracle 里先冻结判据与区间。

> 说明：上下文行（unified diff 的 context）天然可能落入他卡区，**不计为改动行**；本声明的口径 = **added/replaced 行**，与两前置卡交付时的口径（`T1-10-FIX`「新增块 60–74 / 207–217」、`T1-F2-FIX`「new-side 56–63 / 367–379 / 461–476」）一致。

---

## 4. 冻结的畸形时间戳探针族（期望**手算**，先于运行）

**公共常量**（逐字取自 `harness/tests/test_i14b_natural_window_container_total.py:50-63` 与 T1-10-FIX oracle §3）：

```
FROZEN_NOW = "2026-09-20T02:56:38Z"
GOOD_FIELDS = {
  "started_at": "2026-09-20T00:00:00Z",
  "observation_finished_at": "2026-09-20T00:29:00Z",
  "sampled_at": ["2026-09-20T00:%02d:00Z" % i for i in range(0, 30, 2)],   # 15 个，00:00…00:28
  "quick_check_started_at": "2026-09-20T00:29:00Z",
  "quick_check_finished_at": "2026-09-20T00:37:00Z",
  "command_finished_at": "2026-09-20T00:37:00Z"}
```

手算锚：00:00→00:29 = **1740 s**；00:29→00:37 = **480 s**；00:00→00:37 = **2220 s**；样本 00:00→00:28 = **1680 s**。

| id | 形状（只动一个字段） | claim | **RED 期望（左像 `9b1ebda2…`）** | **GREEN 期望（修复后 SUT）** |
|---|---|---|---|---|
| **TS-1** | 窗口：`started_at="not-a-timestamp"` | `{"basis":"sample_span","natural_observation_seconds":1680}` | **rc=4**；stdout `{"ok":false,"error":"internal_error","detail":"Invalid isoformat string: 'not-a-timestamp'"}`；**报告未写出**；**整批 0 裁决** | **rc=0**、报告写出、`verdict=reject_claim`、`refusals=["R-TIMESTAMP-MALFORMED"]`；`computed.started_at=null`、`observation_finished_at="2026-09-20T00:29:00Z"`（可解析者不置 null）；`observation_span_seconds=1680.0`（**样本事实仍可算**）、`sample_count=15`、`first_sampled_at="2026-09-20T00:00:00Z"`、`last_sampled_at="2026-09-20T00:28:00Z"`、`quick_check_seconds=480.0`、`command_total_seconds=null`（依赖坏起点）、`schedule_lag_seconds=null`、`union_seconds=0.0`、`sum_seconds=0`、`overlap_seconds=0.0`、`observation_interval_count=0`、`observation_intervals=[]`、`quick_check_overlap_seconds=0.0`、`basis="sample_span"`、`basis_registered=true` |
| **TS-2** | 窗口：`sampled_at[3]`（00:06）改 `"not-a-timestamp"` | `{"basis":"union_of_windows","natural_observation_seconds":1740}` | **rc=4**、同上 detail、无报告、0 裁决 | **rc=0**、`reject_claim`、`["R-TIMESTAMP-MALFORMED"]`；`computed.started_at="2026-09-20T00:00:00Z"`（**未受影响者不置 null**）、`sample_count=14`、`observation_span_seconds=1680.0`、`union_seconds=1740.0`、`sum_seconds=1740.0`、`observation_interval_count=1`、`observation_intervals=[["2026-09-20T00:00:00Z","2026-09-20T00:29:00Z"]]`、`command_total_seconds=2220.0`、`basis_registered=true` |
| **TS-3** | 日历：`ledger.daily[4].started_at="not-a-timestamp"`（另 4 条 09-11…09-14 良构） | `{}`（claim 缺 status） | **rc=4**、detail `Invalid isoformat string: 'not-a-timestamp'`、无报告、0 裁决 | **rc=0**、`reject_claim`、`["R-TIMESTAMP-MALFORMED"]`；`computed = {daily_count:4, daily_same_day_runs_dropped:0, weekly_count:0, monthly_count:0, alert_count:0, window_status:"pending", clock_source:"system_utc"}`（**坏条目不入链，可得事实照算**） |
| **TS-4** | 登录：`login_check.labels[1].sampled_at="not-a-timestamp"`（0/5/10 s 锚点、全 `live_ui_capture`） | 不参与判定 | **rc=4**、同 detail、无报告、0 裁决 | **rc=0**、`reject_claim`、`["R-TIMESTAMP-MALFORMED"]`；`computed.label_count=3`（标签数是可得事实，**不因坏时间戳丢失**）、`anchor_event_id="E1"`、`shared_anchor_event_id="E1"`、`label_offsets_seconds=[0,0]`、`label_offset_max_error_seconds=0.0`、`capture_latency_max_seconds=0.0` |
| **TS-5** | 窗口：`started_at=[2026-09-20]`（**类型**错而非格式错） | 同 TS-1 | **rc=4**、detail `'list' object has no attribute 'endswith'`、无报告、0 裁决 | **rc=0**、`reject_claim`、`["R-TIMESTAMP-MALFORMED"]`、`computed.started_at=null`（§11.8「**类型**/格式错误」同码） |
| **DOC-2** | 顶层 `frozen_now_utc="not-a-timestamp"`（**文档域**） | — | **rc=2**、`{"ok":false,"error":"malformed_input","detail":"Invalid isoformat string: 'not-a-timestamp'"}`、无报告 | **与 RED 逐字节相同**（rc=2 域不得被全函数化吃掉；本行为本卡唯一允许的「before==after 且非 0」行） |
| **CTRL-4** | 顶层 `"cases":"abc"`（非 list，文档已解析） | — | **rc=4**、`internal_error`、detail `'str' object has no attribute 'get'` | **与 RED 逐字节相同**（证明 rc=4 机关**未被整体吞掉**，本卡不是把异常一律吃掉） |

**崩溃的判定口径**（与 T1-10-FIX 同）：(a) CLI `rc∈{4}` + stdout `internal_error` + **报告未写出** + **整批 0 裁决**；(b) 直调 `classify()` 抛未捕获 `ValueError`。两者任一即 RED。

**GREEN 的三条硬判据**（每条都被一个变异臂反证，见 §6）：
- **G1** rc=0 + 报告写出 + `case_count` 全裁决 + `refusals` 含 `R-TIMESTAMP-MALFORMED` + `verdict=reject_claim`；
- **G2** `computed` 里**受影响**的回显时间字段（`started_at`/`scheduled_at`/`observation_finished_at` 中**在输入里存在且解析不出**的那些）= `null`，**未受影响者逐字节保持原样**；
- **G3** 其余派生量按可得事实计算（上表逐字段手算值）。

---

## 5. 冻结不变量（invariants）

- **I-1 良构输入逐字节不变**：`harness/run_cases.py --cases cases.r2.json --expectations frozen_expectations.r2.json` 在左像与修复像上 **rc / ok / mismatch / case 计数 / `sut_report` sha256 全部相等**；`cases.json` 门同样 before==after（其既有 `expected_superseded` W1 差使 rc=1 属既有态，**两像同值**）。四个既有测试套件 before==after：`test_i14b_natural_window.py` 32、`..._r2.py` 18、`..._basis_total.py` 23、`..._container_total.py` 29，**failed 全 0、passed 计数相等**。`harness/mutate.r2.py` 20 臂两像均 `mutation_count=20 / all_mutants_red_again=true / all_expected_cases_red=true`。
- **I-2 缺键行为不变（NC-MISSING）**：按 T1-F2-FIX 的 7 行 `K7, S7a, S7b, S7c, S8, S9, S10` 自建同构探针，before/after 逐字段比对 **7/7 `equal=true`**；且语义固定为 **`S7a`/`S7b`/`S7c` = `accept_claim` + `[]`；`S8` = `reject_claim` + `["R-EMPTY-EVIDENCE","R-FUTURE-CLOCK","R-SAME-INSTANT"]`（**不含 `R-CLAIM-EXCEEDS`）**；`S9` = 四码；`S10` = `accept_claim []`。
- **I-3 词表 16 → 17**：口径 = `set(re.findall(r"\bR-[A-Z0-9-]+\b", sut_source))`（**词边界**；裸正则会把 `R-UNKNOWN_CLASS` 截成 `R-UNKNOWN` 而多计一个假码，故必须带 `\b` —— 冻结前已在左像上实测：裸式 = 17、带 `\b` = 16，与 T1-10-FIX reviewer 报告 §7 列出的 16 码逐字一致）。**冻结期望：左像 16 → 修复像 17，`after − before == {R-TIMESTAMP-MALFORMED}`，其余 16 码集合相等、一字不改。**（oracle §2 十四码 + §11.3 `R-BASIS-UNKNOWN`、`R-NO-INTERVAL` = 16，正是「词表 16」的出处。）
- **I-4 两前置卡的既有语义不触**：`R-BASIS-UNKNOWN` / `R-SIMULATED-CLOCK` / `R-CLAIM-EXCEEDS` / P4 容器归一路径 / J7 tuple / J11 守卫行 / `BASIS_REGISTRY` 元组 —— 全部**一字不改**（E1–E10 落点与它们行不交，见 §3）。
- **I-5 rc 冻结域**：SUT rc ∈ {0, 2, 4}。畸形时间戳（TS-1…TS-5）= **0**；文档域（DOC-2）= **2**；真正内部错（CTRL-4）= **4**。
- **I-6 行不交界**：见 §3 断言，测量落 `evidence/after/line_disjointness.json`。
- **I-7 pin 不回写**：§binding 列的 11 个 harness pin + 两前置卡 + I-14-B oracle，before/after/delivery 三次 sha 全等。
- **I-8 diff 可逆重建**：把 `changes.diff` 应用到左像 `9b1ebda2…` ⇒ 得到的文本与修复后 SUT **逐字节相同**；新增测试文件同样**逐字节重建**。
- **I-9 只读边界**：`git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` 条数 **= 0**；两前置卡目录 0 字节写入；I-14-B `oracle.md` 0 字节写入（`§11.8` 只读，本卡**不追加**）；五份计划文件 0 字节写入。

---

## 6. 冻结的变异臂（非空洞性；全部作用于**修复后** SUT 的 scratch 副本）

| 臂 | 变异 | 期望（必须**红**） |
|---|---|---|
| **MUT-F3-A** | 把 `_parse` 改回**不捕获 `ValueError`**（删掉 `except ValueError: return None`，恢复原抛出） | TS-1…TS-5 全部**回 rc=4 / 无报告 / 整批 0 裁决**（G1 红） |
| **MUT-F3-B** | 去掉**新码**（把 `R-TIMESTAMP-MALFORMED` 那次 `append` 删掉） | TS-1…TS-5 的 `refusals` 不再含新码、`verdict` 翻成 `accept_claim`（G1 红）；词表退回 16 |
| **MUT-F3-C** | 让 `computed` 的**时间回显不置 null**（`_echo_ts` 改回直接 `fields.get(key)`） | TS-1 / TS-5 的 `computed.started_at` 不再是 `null`（G2 红） |
| **MUT-F3-D**（加验） | 去掉 `started` 不可解析 ⇒ 观察窗两端不可用的降级（删 `if started is None: obs_finished = None` 与 `command_total` 守卫） | TS-1 回 rc=4（在 defect-2 区的 `[(started, obs_finished)]` 上抛 `TypeError`）⇒ 证明**降级路径承重**，也证明我没有靠改 defect-2 区过关 |

每臂：**变异体 sha256 + raw rc + raw stdout/stderr 逐条落盘** `evidence/after/mutations/`。缺证据即写「未证实」，**不造绿色样例**。

---

## 7. 冻结的批次负控（§11.8 第 ④ 条明列的验收面）

**素材**：`BAD` = TS-2（`sampled_at[3]` 畸形窗口 case）；`GOOD` = `harness/cases.r2.json` 中的 `W1`、`X5`、`C1` 三个良构 case（**在运行前选定**，不看结果挑样）。

| 臂 | 批次 | 期望（左像 / 修复像） |
|---|---|---|
| **B-NEG** | `[BAD, W1, X5, C1]` 跑**左像** | **rc=4、无报告、整批 0 裁决**（炸批，区分度对照） |
| **B-POS** | `[BAD, W1, X5, C1]` 跑**修复像** | **rc=0**、报告写出、`case_count=4`、**全 4 case 均有 verdict**；`verdicts[0]` = `reject_claim` + `["R-TIMESTAMP-MALFORMED"]` |
| **B-BYTE-1** | `[W1, X5, C1]`（仅良构，同序）跑修复像 | 与 **B-POS 的 `verdicts[1..3]` 逐字节相同**（坏 case 不污染良构输出） |
| **B-BYTE-2** | `[W1, X5, C1]` 跑**左像** vs **修复像** | 报告**逐字节相同**（良构路径本身也没动） |

---

## 8. 冻结的范围边界（**不修、如实登记**）——本节写在运行之前

1. **缺键（KeyError）路径一字不改**：`fields["started_at"]`、`window["started_at"]`、`entry["started_at"]`、`label["sampled_at"]`、`label["name"]` 缺键时仍抛 `KeyError` → rc=4。理由：§11.8 只授权「`_parse` 抛 `ValueError`」这一形状配新码；派发单不变量又明令「**缺键行为不变**」。本卡**不代填**，登记为**边界**（见交付消息 open question）。
2. **容器**（`windows`/`sampled_at`/`ledger.*` 非 list、`claim` 载体非对象、`clock_source` 容器）**不触** —— §11.8 ③a 归 T1-F2-FIX（已 `accepted_scoped`）。
3. **`windows`/`labels` 元素本身非对象**（如 `windows=["x"]`）仍 `TypeError` → rc=4：这不是 `_parse` 的 ValueError，属 §11.8 ③a 的「载体」族与 F-1/F-2/P4 轨，**不在本卡授权机制内**；登记为边界。
4. **顶层 `cases` 类型错**（`"cases":"abc"`）仍 rc=4：§11.8 的 rc=2 枚举只列了「不可解析 / 缺键 / `frozen_now_utc` 不可解析」三形，未含「类型错」，故不改；`CTRL-4` 把它作为 rc=4 机关仍活着的对照臂。
5. **`R-UNKNOWN_CLASS` 不改**：未知 class 不做时间戳扫描（`_malformed_time_fields` 对未知 class 返回空），行为逐字节不变。
6. **`""` / `null` 与「缺键」的界线（冻结判据）**：**字段键存在**且 `_parse(值)` 解析不出 ⇒ 判畸形（含 `""`、`null`、非串类型）；**键不存在** ⇒ 不判（保持原路径）。理由：键存在就是「类型/格式错误」，且可避免「坏 `started_at` 被当缺键静默 accept」。**实测**：`harness/cases.json`、`cases.r2.json` 与四个既有测试文件中，时间戳字段的 `null`/`""` 出现次数 = **0**，故该判据不改变任何既有良构输出。

---

## 9. 证据落点（预期）

```
evidence/line_zones.json                       # 冻结前：合并链 + 三方行区（只读分析）
evidence/before/…  evidence/after/…            # probes / gates / suites / mut20 / nc-missing /
                                               # vocab / batch_nc / mutations / invariants /
                                               # line_disjointness / pins
changes.diff                                    # iso/natural_window.py + 新增测试族（difflib，无 git）
handoff.json                                    # status=review_pending, implementer_signed=false
```

**九步对照**：1 领取 = 本文件头 + binding；2 绑定 = `binding.json`；3 读证据 = §1 + §2 + 只读分析；4 **冻结预期 = 本文件（已先于任何运行落盘）**；5 修前复现 = §4 RED 列；6 最小修改 = 只动 iso + 一个新测试文件；7 修后同输入重跑 = §4/§5/§6/§7；8 交审 = `changes.diff` + 全量 raw + `handoff.json`；9 接续 = 父派独立复审（本卡**不代签**）。

---

## ERRATUM-1（**append-only**，2026-09-25；冻结后首次追加，上文一字未改）

**性质**：一处**手算算术笔误**的更正，不是「按结果改 oracle」。更正可**完全由 §4 已冻结的输入常量独立重算得出**，与观测输出无关；先写出重算，再与实测比对。

- **更正对象**：§4 表 TS-4 行 GREEN 列中的 `label_offsets_seconds=[0,0]`。
- **冻结原文**：`label_offsets_seconds=[0,0]`、`label_offset_max_error_seconds=0.0`、`capture_latency_max_seconds=0.0`、`label_count=3`、`anchor_event_id="E1"`、`shared_anchor_event_id="E1"`、`refusals=["R-TIMESTAMP-MALFORMED"]`、rc=0。
- **独立重算（只用 §4 冻结输入：`anchor_at=2026-09-20T00:00:00Z`，label 名 0/5/10，label0 `sampled_at=00:00:00Z`、label1 `sampled_at=not-a-timestamp`、label2 `sampled_at=00:00:10Z`）**：
  - 实现的 offsets 定义是 `int(round(_secs(anchor_at, sampled_at)))`（= **绝对偏移**），errors 定义是 `abs(offset - float(label["name"]))`（= **对目标偏移的误差**）。
  - label0：offset = 0 s → `0`；error = `0 − 0 = 0`。
  - label1：`sampled_at` 畸形 → 该标签**不贡献时序事实**（§6 判据：标签本身仍计数、仍查 evidence_kind）。
  - label2：offset = `00:00:10 − 00:00:00` = **10 s** → `10`；error = `10 − 10 = 0`。
  - ⇒ **`label_offsets_seconds = [0, 10]`**；`label_offset_max_error_seconds = max(0,0) = 0.0`；`capture_latency_max_seconds = max(0.0, 0.0) = 0.0`；`label_count = 3`。
- **错误根因**：我把「offsets」误当成了「errors」（把 `label_offsets_seconds` 写成 `[0,0]`）。**errors 才是 `[0,0]`**；二者在本探针里恰好都以 0.0 收敛到同一 `max_error`，掩盖了该笔误。
- **更正后**：TS-4 GREEN 期望 = `label_offsets_seconds=[0, 10]`，其余逐字**不变**（含 `label_offset_max_error_seconds=0.0`、`capture_latency_max_seconds=0.0`、`label_count=3`、两个 anchor id、`refusals=["R-TIMESTAMP-MALFORMED"]`、rc=0）。
- **不涉及**：TS-1 / TS-2 / TS-3 / TS-5 / DOC-2 / CTRL-4 的全部期望、§5 全部不变量、§6 四条变异臂、§7 批次负控、§8 边界 —— **一字未改**。
- **同步**：`harness/tests/test_i14b_natural_window_timestamp_total.py` 中对应断言同步为 `[0, 10]`（该断言与本 erratum 同源同值）。
- **披露**：本 erratum 在 GREEN 首跑**发现该红**之后追加；因此 TS-4 这一条**不作为「先于观测冻结」的证据**，其可判据部分（rc / verdict / 新码 / `label_count` / `max_error` / anchor id）**仍属冻结面**，只有 `label_offsets_seconds` 一个数值由本 erratum 更正。该条在交付报告中如实标注为 **「更正后复测」**。

---

## ERRATUM-2（**append-only**，2026-09-25；第二次追加，上文一字未改）

**性质**：实施后登记 —— ①一处**计划落点被更小的落点取代**；②两处 §6 变异臂**执行细节的澄清**；③一条 §8 **新增边界**；④§3 声明的**实测结果**。**§4 的全部 GREEN/RED 期望值、§5 的九条不变量、§6 的四条臂与其期望、§7 批次负控、§8 已有六项边界：一字未改。**

### E2-a §3 落点表 E7 未实施（改动面比计划更小）

- 计划中 E7 = `derive_calendar` 的 daily/weekly/monthly 三处 None 守卫（L318–357）。
- **实测 diff 在 318–357 段的改动行数 = 0**（`evidence/after/line_disjointness.json` 的改动行集里没有该段）。
- 原因：**E6（`_eligible` 入口过滤）已使 `daily`/`weekly`/`monthly` 里留下的每条记录的 `started_at` 必可解析**，下游 `when`/`latest`/月度推导**不可能再拿到 None**，故三处守卫为**冗余**，按「最小修改」不写。
- 影响：**改动集严格变小**，行不交界更宽裕；TS-3 的 GREEN 期望（`daily_count=4`）与判据不受影响，仍按 §4 冻结值执行（实测一致）。

### E2-b §6 MUT-F3-A 的实际变异体（澄清，非改判）

- §6 冻结原文：「把 `_parse` 改回**不捕获 `ValueError`**（删掉 `except ValueError: return None`，恢复原抛出）⇒ **TS-1…TS-5 全部回 rc=4**」。
- 只删 `except` 两行会留下 `if not isinstance(ts, str): return None` 护栏，**TS-5（类型错，非格式错）不会回 rc=4**，与同一行冻结的「TS-1…TS-5 全部」**自相矛盾**；且只删 `except` 会使 `try:` 无子句 ⇒ 语法错误 ⇒ rc=1（首跑实测，已留档 `evidence/after/mutations/arm1.json` 的前一版）。
- **执行取法**：把**整个 `_parse` 函数还原为修前原文**（= 「改回不捕获 ValueError」的完整含义 —— 修前的 `_parse` 既不捕获也不 isinstance 守卫）。该臂的 mutant 即**修前 `_parse` 的逐字副本**。
- 实测：TS-1…TS-5 **5/5 回 rc=4 / 无报告 / 0 裁决** ✓ 与 §6 冻结期望逐字一致。

### E2-c §6 MUT-F3-D 的红判据（比冻结更严）

- §6 冻结只写了「TS-1 回 rc=4」；实作要求 **TS-1 与 TS-5 都回 rc=4**（两者的 `started_at` 都读不出，降级路径在二者上都承重）。
- TS-2 / TS-3 / TS-4 在该臂下**仍 rc=0** 属**预期**：它们的 `started_at` 可解析，降级路径本来就不参与；该臂不因此失效。实测 `arm4`: `TS1=4, TS2=0, TS3=0, TS4=0, TS5=4`。

### E2-d §8 新增边界项 7（不修、如实登记）

- **`login_check.labels[].name` 非数值**（如 `"abc"` / `null` / 列表）时，`float(label["name"])` 抛 `ValueError`/`TypeError` → 仍 **rc=4**。
- 不修的理由：`name` **不是时间戳字段**，§11.8 只授权了「时间戳畸形 → `R-TIMESTAMP-MALFORMED`」这**一个**新码（且是该码唯一授权来源），给非时间戳字段配码 = 越权自填。
- 同族已登记边界（§8 项 1/3/4）一并保留。**提请父方裁**：是否需要为「非时间戳字段类型错」另开裁权。

### E2-e §3 声明的实测结果（`evidence/after/line_disjointness.json`）

- 本卡在左像 L2（`9b1ebda2…`，549 行）上的**改动 + 插入**行集（1-based，保守把插入点记为其前后两行）：
  `89-92, 104-105, 123-124, 130, 132, 134-135, 150-151, 152, 167, 170-173, 249-250, 253, 259, 287-288, 417-419, 424, 489-490, 515-516`
- 与 §3 三个外部区 `{67-75, 81, 214-224}` ∪ `{56-63, 367-379, 461-476}` ∪ `{189-212}` 的**交集 = ∅（实测 `foreign_hits = {}`）**；与 `_parse` 本体区 `{89-95}` 的关系 = **包含**（`89-92 ⊆ 89-95`）。
- 修复后 SUT：`d1ced6ac566d41cb6b9c829074c7422393ee8aa9f2e74b191d2de6face97b7f0`（30210 B / 671 行）。
- `changes.diff`：29067 B / sha256 `693d6239fd958545bc05ad8d246758f2bb47a4ca10de37187c2f9454fadaf5ba` / **+539 −23 / 2 文件**（`iso/natural_window.py` 修改 + 新增测试族）；应用到左像可**逐字节重建**修复后 SUT 与新测试文件（invariants I-8 ✓）。


