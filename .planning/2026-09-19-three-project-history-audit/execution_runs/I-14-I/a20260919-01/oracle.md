# I-14-I oracle.md — 容器 basis 的逐例拒绝 + 两个硬编码键派生（I-14-H 强制收尾残卡 / RIDER）

attempt：`execution_runs/I-14-I/a20260919-01`。本卡是 I-14-H 独立 reviewer 的**强制收尾条件**
（`I-14-H/a20260919-01/review.md` sha256 `97997d6d…`）的唯一兑现路径。
**status=review_pending；实现者不自签（implementer_never_signs_acceptance）。**

## 0. 本卡范围与不可声称项

只做四件事：(1) `iso/natural_window.py:202` 的 basis 成员测试加类型护栏 → **逐例**拒绝而非整批崩溃；
(2) 冻结 list/dict/set/tuple/嵌套容器 + 负例（登记字符串 basis）的期望；(3) 解除 I-14-H 的 xfail；
(4) 把 `:241`/`:248` 两个**硬编码字面量**改为**派生值**并补**可失败**断言。
外加补跑全 14-case 门至 rc 0 并落盘。

**不**授予：真实自然观察资格、真实 UI 即时性、SLO/性能、`disclosure_adaptation`（保持 unmapped）、
`accuracy`（保持 unproven）。全部用例为 **SYNTHETIC-TIMER-ONLY** 合成时间输入。
**不**改 `SUT_VERSION`、**不**放宽冻结期望、**不**回改冻结正文、**不**把门改成 12 例。

## 1. 修复前事实（冻结期望之前实测，见 `before/CMD-I14I-PREFIX-PROBE/`）

对未修改的 SUT（`iso/natural_window.py`，sha256 `7fff6f0c…`，逐例直接调用 `classify`，
18 个 basis 取值）实测结果 —— **这是"缺陷的确切边界"，本卡的期望据此分档，既不扩大也不缩小**：

| basis 取值类别 | 实测行为 | 崩溃/裁决 |
|---|---|---|
| 登记字符串（`sample_span`/`union_of_windows`/`command_total`） | 正常按实质裁决 | 无崩溃 |
| 未登记字符串（`wall_clock`/`''`） | `R-BASIS-UNKNOWN` | 无崩溃 |
| `null` / 缺键 | `R-BASIS-UNKNOWN` | 无崩溃 |
| `int` / `float` / `bool`（可哈希标量） | `R-BASIS-UNKNOWN` | 无崩溃 |
| **`list`（含空列表、含嵌套）** | **`TypeError: unhashable type: 'list'` @ `:202`** | 整批 rc 4 |
| **`dict`（含空字典、含嵌套）** | **`TypeError: unhashable type: 'dict'` @ `:202`** | 整批 rc 4 |
| **`tuple`（可哈希）** | `R-BASIS-UNKNOWN` | 无崩溃 |
| **`set`（可哈希）** | `R-BASIS-UNKNOWN` | 无崩溃，**但报告 JSON 无法序列化**（见 §1.1）|

⇒ reviewer 的归因**成立且精确**：崩溃是 **list/dict 专属**，不是"容器通病"。
`set`/`tuple` 的"碰巧正确"**不被当作已覆盖**——它们各自单独冻结（§3），且 `set` 暴露了一个
前次未披露的**附属缺陷**（§1.1）。

全 14-case 门修复前实测（`before/CMD-I14I-PREFIX-CASES14/`）：
`ok=false`、`sut_raw_returncode=4`、`error=sut_cli_nonzero`、
SUT CLI 输出 `{"ok": false, "error": "internal_error", "detail": "unhashable type: 'list'"}`、
`mismatch_count` 字段根本未生成、`sut_report.json` **不存在**、整批中止。⇒ I-14-H 的条件成立。

### 1.1 附属缺陷（本卡一并修，理由是它使"逐例裁决"仍无法落盘）

`computed["basis"]` 直接回填 claim 的原始 basis 值（`:246`）。当 basis 是 `set` 时，
`json.dumps(report)` 抛 `TypeError: Object of type set is not JSON serializable`
——SUT 会在**写报告**那一步崩掉，即使裁决本身已经正确。
「逐例拒绝」若不修这一处，遇到 set basis 仍会整批中止（只是换了崩溃点）。
**期望：修复后 `computed["basis"]` 的值集合只含 JSON 原生标量（字符串或 null）。**
这**不**放宽任何既有期望：14 个冻结用例中 computed 里出现 `basis` 的只有 W1/C2（字符串/null），
其余用例的 `expected[cid].computed` 为空对象，故该改动对冻结门**零影响**（§5 以实测核对）。

## 2. 期望冻结声明（时序）

本文件与 §3/§4 的期望表在**任何**对修复版 SUT 的运行之前写定，且：
(1) 期望值由**手算**（W1 算术 1740/480/2220）与**卡片语义**导出，**从不调用 SUT**；
(2) 修复前实测（§1）只用于**界定缺陷边界**（哪些类型崩、哪些不崩），**不**用于产生期望值；
(3) 下述每个期望都能在**未修改的** SUT 上以相反结果失败（RED），或在修复前的
    `iso` 上直接崩溃——若期望是"照修好的实现写着抄"，就不可能在修复前以恰好相反的方式失败。

## 3. 容器/负例矩阵的冻结期望（逐例，`classify` 直接调用）

共同事实（除特别说明）：观测 00:00–00:29 = **1740 s**，quick_check 00:29–00:37 = **480 s**，
命令总耗时 00:00–00:37 = **2220 s**，无 `windows[]`，`sampled_at` 两个样本。

| # | basis 取值 | 期望 verdict | 期望 refusals（有序→比对时排序） | 语义理由 |
|---|---|---|---|---|
| C1 | `["union_of_windows"]`（list，= H5） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 未登记容器；**必须逐例拒绝，不得整批崩溃** |
| C2 | `{"kind":"union_of_windows"}`（dict，= H6） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 同上 |
| C3 | `["union_of_windows","sample_span"]`（多元素 list） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 元素"像登记名"不使容器变成登记项 |
| C4 | `{"kind":["union_of_windows"]}`（嵌套容器） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 嵌套深度不豁免 |
| C5 | `[{"kind":"union_of_windows"}]`（嵌套容器） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 同上 |
| C6 | `{"union_of_windows"}`（**set**，可哈希） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 修复前已"碰巧正确"；此处**显式冻结**，并要求结果可 JSON 序列化（§1.1） |
| C7 | `("union_of_windows",)`（**tuple**，可哈希） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 同上 |
| C8 | `[]`（空 list） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 空容器不是"缺键"，仍是未登记值 |
| C9 | `{}`（空 dict） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | 同上 |
| C10 | `0`（int） / C11 `1.0`（float） / C12 `True`（bool） | `reject_claim` | `["R-BASIS-UNKNOWN"]` | "非字符串一律未登记"（卡片措辞），标量同档 |
| **N1** | `"union_of_windows"`，claim `natural_observation_seconds=1740` | **`accept_claim`** | `[]` | **阴性对照**：类型护栏不得误拒登记字符串 |
| **N2** | `"command_total"`，claim `2220` | `reject_claim` | `["R-TOTAL-AS-OBS"]` | **阴性对照**：登记 basis 仍按**实质**裁决（命令总耗时不是观察时长），且**不得**出现 `R-BASIS-UNKNOWN` |

N1/N2 是"过度拟合"防线：若把护栏写成一律拒绝，N1 会失败；若回到 r1 的静默 accept，
C1–C12 会全部失败（r1 实测对 C1/C2 **也** accept）——两个方向都被钉住。

## 4. 两个硬编码键的冻结期望（`:241` / `:248`）

**缺陷陈述**（reviewer unverified-list #4，本轮于 §1 复现）：两者是字面量 `False`，
从不派生，故 `run_cases.py` 的 `REQUIRED_KEYS` 形状门与 pytest 对它们的断言**恒真**；
且在快检**确实进入**观察区间的情景下仍报 `False`——**字面量与事实相反**。

**规定派生语义（本卡采用，写入代码注释与断言）：**

- `quick_check_in_observation_intervals` := `quick_check_overlap_seconds > 0`
  —— 即"被测为观察区间的那些区间里，是否有任何一段与 quick_check 相交"。
  这是对**测得事实**的陈述，非对主张的陈述。
- `sum_used_for_natural_duration` := 该 case 的 basis 确实取用了
  `sum_seconds` 作为自然时长（即 `basis == "sum_of_windows"` 且已登记）
  —— 即"这句自然时长到底是不是求和口径"。

**逐情景冻结期望**（`keys = (quick_check_in_observation_intervals, sum_used_for_natural_duration)`）：

| 情景 | windows[] | basis | 手算 union / sum / overlap / qc_overlap | 期望 keys | 理由 |
|---|---|---|---|---|---|
| W1 诚实 1740 | 无 | `sample_span` | 1740 / 1740 / 0 / 0 | `(False, False)` | 无重叠；口径不是求和 |
| W4 重叠窗求和 | `[00:00–00:29],[00:20–00:49]` | `sum_of_windows` | **2940 / 3480 / 540 / 480** | **`(True, True)`** | 观察区间与 quick_check 相交 480 s；且求和口径被采用 |
| W5 重叠窗并集 | `[00:00–00:29],[00:20–00:49]` | `union_of_windows` | 2940 / 3480 / 540 / 480 | **`(True, False)`** | 相交为真；口径不是求和 |
| H11/H12 改名窗 | `[00:00–00:29],[00:29–00:37]` | `union_of_windows` | **2220 / 2220 / 0 / 480** | **`(True, False)`** | 卡片第 6 条点名的情景：修复前恒 `False`，**与事实相反** |
| 边界：求和但不相交 | `[00:00–00:29],[01:00–01:29]` | `sum_of_windows` | 1740 / 3480 / 1740 / 0 | **`(False, True)`** | 无相交；但求和口径**仍被采用** ⇒ 两键**互不蕴含**，防止用一个键冒充另一个 |
| 边界：无观察区间 | 无 | `sum_of_windows` | intervals=[] ⇒ 0 / 0 / 0 / 0 | `(False, True)` | 口径仍被采用；无区间故无相交 |

**这四个键值组合 `(F,F) (T,T) (T,F) (F,T)` 全部出现**，因此两个键各自都**可失败**、
且**不互相冒充**——这正是 reviewer 要求的"判别力"，且修好后**修好前必然失败**（恒 `False`）。

**与冻结门的相容性核对（手算，见 §5 实测）：** 14 个冻结用例中 computed 里显式断言这两键的
只有 **W1**（`quick_check_in_observation_intervals: false`，与 `(False, _)` 相容）；
其余用例 `H*` 的 `expected[cid].computed` 为空对象，`run_cases.py` 只做 `REQUIRED_KEYS` 形状门
（存在性，不比取值）。故派生化对全 14-case 门的期望**零冲突**。

## 5. 全 14-case 门期望（本卡的退出判据）

用**未修改的** `harness/run_cases.py`（`f2a07d0b…`）+ **未修改的** `cases.i14h.json`（`40260c24…`）
+ **未修改的** `frozen_expectations.i14h.json`（`bffb11c2…`）跑修复版：

- `sut_raw_returncode` = **0**（修复前 4）
- `mismatch_count` = **0**（修复前该字段不存在，整批中止）
- `accepted_ineligible_count` = **0**
- `ok` = **true**、`case_count` = 14、门 runner rc = **0**
- **H12 必须实际通过**：`verdict=reject_claim`、`refusals=['R-CLAIM-EXCEEDS','R-QC-IN-OBS']`、
  `computed.quick_check_overlap_seconds=480`、`computed.union_seconds=2220`
  （H12 无 pytest 对应用例，是本卡必须点名确认的一条）

`cases_report.json` 落盘位置：`execution_runs/I-14-H/a20260919-01/evidence/I-14-I/`
（卡片第 5 条："落到 I-14-H attempt 的证据目录（新增 attempt 或 `after/` 子目录）"）。

## 6. pytest 期望（xfail 解除）

- I-14-H 的 `test_container_basis_refused_per_case` **移除 `@pytest.mark.xfail`**，
  并升级为 §3 的 C1–C12 参数化矩阵。
- 新增 N1/N2 阴性对照与 §4 的可失败断言。
- 期望：修复版上 **全部 PASSED、0 xfailed、0 xpass-strict 失败**，pytest rc = **0**；
  修复前版本上：容器用例**以 `TypeError` 崩溃**、派生键用例**以 `AssertionError` 失败** ⇒ RED。
- 反向臂：对 `before/natural_window.i14b-after-2.py`（= 未修改的 SUT）与
  `before/natural_window.r1sut.py`（缺陷版 r1）跑同一套件，记录原始输出
  （r1 对 C1/C2 是**静默 accept**，即卡片第 3 条要求"不得退化回去"的那一支）。

## 7. 恢复规则（卡片"恢复"段）

回退 `iso/natural_window.py:202` 的类型护栏与 `:241`/`:248` 的派生化即可回到本卡起点
（`before/natural_window.i14b-after-2.py` 字节即该起点）。本次全 14-case 门落盘报告与
I-14-H 的 xfail 原始记录**保留**，作为"修复前确实过不了"的证据，不得删除。

## 8. 不可声称项复查（交审时逐条确认）

- `disclosure_adaptation` = **unmapped**；`accuracy` = **unproven**。
- 真实自然观察 / 真实 UI 即时性 / SLO-性能：**NOT GRANTED**（沿用 I-14-B/I-14-H）。
- 本卡**未**改 `SUT_VERSION`；**未**回改任何冻结正文；**未**触碰生产树。
- 实现者**不**自签：status=review_pending，等独立 reviewer 复算。

---

## 9. 冻结后实测结果（AS-OF 记录，非预测；本节在期望冻结之后追加）

本节只**记录**第 3/4/5/6 节预测与实测的对照。**期望本身未做任何修改**（追加式纪律）；
`oracle.md` 正文第 1–8 节即冻结时内容，其 sha256 见 `evidence/freeze_instant.json`
（冻结时刻 `2026-09-21T19:59:53Z`，冻结时 `iso/natural_window.py` 仍为修复前 `7fff6f0c…`）。
本次追加后 oracle.md 的 sha256 会变，属**追加式**记录，不是回改。

### 9.1 修复后 SUT 身份

`iso/natural_window.py` 修复后 sha256 = `9edb95155202432ed01b2c68d06f74a00882287e934cda6cead0e14140493b04`
（23162 B，修复前 `7fff6f0c…` / 20293 B）。`before/natural_window.i14b-after-2.py`
运行前后逐字节不变（`7fff6f0c…`），即 RED 臂的被测物仍是原版。

### 9.2 第 5 节（全 14-case 门）实测 —— **达成**

| 量 | 修复前 | 修复后（CMD-I14I-GATE-CASES14） | 第 5 节预测 |
|---|---|---|---|
| 门 runner rc | 1 | **0** | 0 ✓ |
| `sut_raw_returncode` | **4** | **0** | 0 ✓ |
| `mismatch_count` | 字段不存在（整批中止） | **0** | 0 ✓ |
| `accepted_ineligible_count` | — | **0** | 0 ✓ |
| `ok` | false | **true** | true ✓ |
| `case_count` | 14 | 14 | 14 ✓ |
| `sut_report.json` | **未生成** | 已生成（21416 B） | — ✓ |
| `sut_version` | — | `i14b-after-2` | 未改 ✓ |

重复运行（`CMD-I14I-GATE-CASES14-REPEAT`，**全新 out-dir**）得到**完全相同**的数字与
**相同** `sut_sha256` ⇒ 判定可重复、幂等。

**H12（第 5 节点名确认项）实测通过**：`verdict=reject_claim`、
`refusals=['R-CLAIM-EXCEEDS','R-QC-IN-OBS']`、`computed.union_seconds=2220.0`、
`computed.quick_check_overlap_seconds=480.0`。见 `after/CMD-I14I-AUDIT-POSTFIX/stdout.txt`
（44 项检查全过）。

### 9.3 第 4 节（派生键）实测 —— 达成，且判别力落在**冻结门自己**的用例上

修复后全 14-case 报告里，两键不再是常量：

| 用例 | `quick_check_in_observation_intervals` | `sum_used_for_natural_duration` | 与第 4 节预测 |
|---|---|---|---|
| W1 | `False` | `False` | (F,F) ✓ |
| H10（`sum_of_windows`） | `False` | **`True`** | (F,T) —— **键确实被派生** |
| H11 / H12（改名窗，overlap 480） | **`True`** | `False` | (T,F) ✓ |
| H5 / H6（容器 basis） | `False` | `False` | (F,F) ✓ |

⇒ **在冻结期望所覆盖的 14 个用例内部**，两个键各自都取到了两个不同值。
修复前它们在全部 14 例中恒为 `False`（取值集合大小 = 1，reviewer 实测），
故"形状门恒真"这一弱化**已在门本身之内**被消除，不只靠新增 pytest 用例。

### 9.4 第 3 节（矩阵）与第 6 节（pytest）实测

- **GREEN**（修复版，`after/CMD-I14I-GREEN-SUITE`）：**45 passed, 0 failed, 0 xfailed**，rc 0。
  其中容器矩阵 12 例 ×2 组（裁决 + 可序列化）全过，另有"一个毒例不拖垮整批"用例。
- **RED-前缀**（`before/natural_window.i14b-after-2.py`）：**25 failed / 20 passed**，rc 1。
  失败**精确**落在两类：(a) 含 list/dict 的容器行（`TypeError`），
  (b) 5 个 d3 派生键用例（`AssertionError`，实测字面量 `False` 与事实相反）。
  **`set` / `tuple` / `int` / `float` / `bool` 的裁决行在此臂 PASS** —— 与第 1 节的
  "崩溃是 list/dict 专属"实测**逐项吻合**；但它们的"可序列化"行**FAIL**（`set`），
  即第 1.1 节的附属缺陷被这套件抓住。
- **RED-r1**（`before/natural_window.r1sut.py`）：**43 failed / 2 passed**，rc 1。
  容器行失败原因是 **r1 静默 `accept_claim`**（越权方向，卡片第 3 条禁止回退到的那一支）；
  `test_d1_registered_string_basis_not_over_refused` 亦失败，原因是 r1 把诚实的 1740
  union 主张 **reject**（缺陷②的方向倒置）—— 与本卡无关但同向佐证。
- **xfail 解除的直接证据**（`after/CMD-I14I-GREEN-I14HSUITE`）：把 I-14-H 的套件
  **原样**（保留 xfail）跑在修复版上，得到 **11 passed, 1 xpassed**，rc 0。
  即 `test_container_basis_refused_per_case` 从"记录残留的 xfail"变为**真通过**；
  本卡在自己的套件里把该 `xfail` 装饰器**删除并升级为 12 行矩阵**，
  故 GREEN 计数为 `45 passed / 0 xfailed`，没有任何 xfail 残留。

### 9.5 落盘与只读核对

- `cases_report.json` 已落到 **I-14-H attempt 的证据目录**：
  `execution_runs/I-14-H/a20260919-01/evidence/I-14-I/`，并附 `sut_report.json` 与
  `sut_cli.*`（runner 原生产物）。卡片的"退出"条目要求"落到 I-14-H attempt 的证据目录
  （新增 attempt 或 `after/` 子目录）"，此处取"新增子目录"一支。该目录**新增**，未改动
  I-14-H 任何既有文件。
- 生产树只读：`git -C <revenue-forecast> status --porcelain -- scripts` 输出 **0 字节**（空）。
- 冻结材料在本次运行前后逐字节不变：`cases.i14h.json` `40260c24…`、
  `frozen_expectations.i14h.json` `bffb11c2…`、`run_cases.py` `f2a07d0b…`、
  `cases.json` `5d8c4592…`、`frozen_expectations.json` `3ba2bb17…`（后者正文仍为 2220）。
