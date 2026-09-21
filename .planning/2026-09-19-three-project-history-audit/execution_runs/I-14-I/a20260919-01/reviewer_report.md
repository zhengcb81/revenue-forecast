# I-14-I 独立复核（independent reviewer）

卡片：`execution_v2/card_I-14-I.md`（容器 basis 的逐例拒绝 + 两个硬编码键派生，I-14-H 强制收尾残卡 / RIDER）
attempt：`execution_runs/I-14-I/a20260919-01`
复核者：独立 reviewer（**非**实现者；实现者未自签，`implementer_signed=false` 已核实）
本报告为**只读复核**：未修改 attempt 内任何既有文件，未写入生产树。

---

## 结论：ACCEPT（条件式，`accepted_scoped`）

卡片的**全部退出判据均经独立复算成立**：全 14-case 门 rc 0；xfail 已解除且经"字节未改的 I-14-H 套件"
证明为**真通过**；两个 RED 臂双向可失败；`:241`/`:248` 确为派生值；冻结正文与生产树零改动。
实现者第 1–10 项声明中，**9 项完全成立**，**1 项（第 4 项后半"判别力可见于冻结门内部"）措辞过强、
经变异测试证伪**（见 F-1）。该措辞不改变退出判据的成立，但会误导下游读者对"门本身能证明什么"的判断，
故本卡为**条件式验收**，附 6 项强制后续（见 §8）。

**验收证据**：14/14 冻结用例端到端门 rc 0（`mismatch_count=0` / `accepted_ineligible=0` / SUT rc 0）
+ 45 例 rider 套件 45 passed / 0 xfailed。⇒ **I-14-H 的"12/14 冻结用例 + 12 例 pytest 套件"限定可以解除**，
但仅限该限定本身；I-14-H 的其余 NOT GRANTED 项（真实自然观察 / 真实 UI 即时性 / SLO / `disclosure_adaptation` /
`accuracy`）一律不变。

### 逐卡条结论

| 卡条 | 要求 | 结论 |
|---|---|---|
| 1 | `:202` 类型护栏 → 逐例拒绝而非整批崩溃 | **成立**（修复后 0 崩溃；修复前 10 个取值在 `:202` 抛 TypeError） |
| 2 | H5/H6 冻结期望可满足 | **成立**（门 rc 0，H5/H6 均 `reject_claim` + `R-BASIS-UNKNOWN`） |
| 3 | 不得退化为 r1 静默 accept | **成立**（r1 臂 43F/2P；r1 对全部 27 个取值均 `accept_claim`，实测） |
| 4 | list/dict/set/tuple/嵌套分别冻结 + 阴性对照 | **成立**（N1/N2 过；set/tuple 显式冻结） |
| 5 | 全 14-case 门 rc 0 并落盘 I-14-H 证据目录 | **成立**（落盘字节与门产物**逐字节相同**，已核） |
| 6 | `:241`/`:248` 改派生值并补可失败断言 | **成立**（派生语义正确、4 个组合齐全、4 例可失败）；但"判别力落在冻结门内"**不成立** → F-1 |
| 7 | 不放宽期望 / 不回改冻结正文 / 不改 `SUT_VERSION` | **成立**（五个冻结材料与 I-14-H 逐字节相同） |
| 8 | 不授予真实资格 | **成立**（`disclosure_adaptation=unmapped`；`accuracy=unproven`；SYNTHETIC-TIMER-ONLY） |

---

## 1. 我实际执行的复算（全部为本轮独立重跑，非引用实现者输出）

复核环境：`C:\Miniconda\python.exe` 3.13.9 + pytest 9.1.1（与实现者一致，实测确认）。
所有产物写入 attempt 之外的临时目录 `%TEMP%\i14i-reviewer-bfecd191\`；attempt 内**零写入**。

| # | 复算 | 结果 |
|---|---|---|
| R1 | 22 个关键 artifact 的 sha256 逐项重算（含 §7 列出的 13 个核心哈希 + 8 个证据 stdout + `changes.diff`） | **全部与 `handoff.json` 记载逐字符吻合** |
| R2 | 用未修改 `run_cases.py`（`f2a07d0b…`）+ 未修改 i14h 冻结材料跑全 14-case 门 | **rc 0**；`ok=true` / `case_count=14` / `mismatch_count=0` / `accepted_ineligible_count=0` / `sut_raw_returncode=0` |
| R3 | R2 的 `sut_report.json` 与实现者门产物对比 | **21416 B，逐字节完全相同**（`11f27c8e…`）⇒ 判定确定性可复现 |
| R4 | R2 的 15 个语义字段与**已落盘** `I-14-H/…/evidence/I-14-I/cases_report.json` 对比 | **15/15 相同**（`generated_at_utc` 亦相同 ⇒ 落盘件确为该产物原件） |
| R5 | 落盘件 vs `after/CMD-I14I-GATE-CASES14/gate/cases_report.json` 字节比对 | **逐字节相同**（`e8925fdc…`） |
| R6 | 对**未修改 SUT** 跑同一门（修复前基线） | **rc 1** / SUT rc 4 / `error=sut_cli_nonzero` / `"unhashable type: 'list'"` / `sut_report.json` 不存在 / `mismatch_count` 字段不存在 |
| R7 | **字节未改**的 I-14-H 套件（`archive_test_i14h_original.py`，`147cdc1c…`，与 I-14-H 原件**逐字节相同**）跑修复版 SUT | **11 passed, 1 xpassed, rc 0**；`test_container_basis_refused_per_case` → **XPASS** |
| R8 | 同一字节未改套件跑**修复前** SUT | **11 passed, 1 xfailed, rc 0**；同一用例 → **XFAIL** |
| R9 | rider 套件跑修复版 / 修复前 / r1 | **45 passed** rc 0 ／ **25 failed, 20 passed** rc 1 ／ **43 failed, 2 passed** rc 1 |
| R10 | 我自写的 27 取值 basis 边界探针，跑三个 SUT | 修复前：崩溃点**精确落在 `:202`**；修复后 **0 崩溃** |
| R11 | SUT **真实 CLI** 端到端（7 例含 list/dict/tuple 的中毒批） | 修复前 **rc 4，报告未生成**；修复后 **rc 0，报告生成**，7 例全部逐例裁决 |
| R12 | 变异测试：把两个派生键**改回硬编码 `False`**（其余字节不动）跑未修改门 | **rc 0 / mismatch 0** ⇒ 门对派生化**完全不敏感** → F-1 |
| R13 | 同一变异体跑 rider 套件 | **4 failed** ⇒ 判据确实存在，但在 rider 套件不在门内 |
| R14 | 实现者 `audit_postfix.py` 对**我自己的**门产物跑 | **checks=44 failures=0** |
| R15 | 生产树只读、冻结材料回落核对 | `git status --porcelain -- scripts` **0 字节**；`git diff` / `git diff --cached` 亦空 |

### R7 + R8 是"claim 2"的决定性证据（已亲验）

```
I-14-H 套件（xfail 保留，字节未改） vs 修复前 SUT  ->  test_container_basis_refused_per_case XFAIL
I-14-H 套件（xfail 保留，字节未改） vs 修复后 SUT  ->  test_container_basis_refused_per_case XPASS
```

**同一份测试字节**、同一断言、仅 SUT 一个变量 ⇒ xfail 不是"被删除后换了个测试"，而是**该断言真的由失败转为通过**。
这是本卡最强的一条证据，独立复现成立。另核实：rider 套件内 `@pytest.mark.xfail` **0 命中**（唯一的 `xfail`
字样是第 182 行的注释），归档件内 **1 命中**且留在原处。

---

## 2. Findings

### F-1（新发现，中等）"判别力落在冻结门内部"**不成立**——门对派生键完全不敏感

实现者 `oracle.md §9.3` 与 `handoff.json` 称：修复后 W1=(F,F)、H10=(F,T)、H11/H12=(T,F)，
故"'形状门恒真'这一弱化**已在门本身之内**被消除，不只靠新增 pytest 用例"。

**该结论经变异测试证伪。** 我把修复版 SUT 的这两行改回硬编码字面量（其余字节不动，
变异体 `2265bd0d…`），用**未修改的** `run_cases.py` + **未修改的**冻结期望跑全 14-case 门：

```
REVIEWER-MUTANT-KEYS-REVERTED -> ok=true, case_count=14, mismatch_count=0,
                                 accepted_ineligible_count=0, sut_raw_returncode=0, rc 0
```

**门照过。** 机制已在源码层核实：

- `run_cases.py:177-180` 对 `REQUIRED_KEYS` 只做**存在性**检查（`if key not in computed`），不比取值；
- 全 14 个冻结用例中，`quick_check_in_observation_intervals` **仅被 W1 约束且值为 `False`**；
  `sum_used_for_natural_duration` **在 14 例中完全无取值约束**（27 个 computed 约束键里没有它）；
- 因此 `(F,T)`/`(T,F)` 只是**门报告里的可观察值**，不参与门的 pass/fail。

更值得注意的对称性：**修复前的"恒真弱化"同样也不影响门通过**；修复前门从未通过，唯一原因是
**批中止（rc 4）**。也就是说，门对"这两个键"从来就没有判别力——修复前后都是如此。
`handoff.json` 的 `derived_keys_discharge.discrimination_inside_the_frozen_gate` 字段因此是对门能力的**过度陈述**。

**修复该弱化所需的判据确实存在，但在 rider 套件**：第 12 行变异体使 rider 套件 **4 failed**
（`test_d3_renamed_window_reports_quick_check_inside_observation`、`…overlapping_sum_claim_reports_both_keys_true`、
`…overlapping_union_claim_reports_overlap_only`、`…disjoint_sum_claim_reports_sum_used_without_overlap`），
覆盖 (F,F)/(T,T)/(T,F)/(F,T) 四组合 —— 这是**真的可失败**，本条不影响卡条的实体成立。

**性质**：措辞/能力归属问题，**不**是数据造假，**不**是判据缺失，**不**是否定本卡。
但它会让下游把"门 rc 0"误读为"派生键已被门证明"，故须在验收文本中显式更正。

### F-2（新发现，低-中）CF-I14I-2 的修复**只完成了一半**：`classify()` 仍回填原始 `claim`

修 `computed["basis"]` **确实是必要的**（我独立复现了修复前的序列化崩溃，见下），
但它**并不足以**消除"写了报告就崩"这一类失败。修复版 `iso/natural_window.py:502` 仍是：

```python
"claim": case.get("claim"),          # 原始 claim 里的 basis 原封不动回填进 verdict
```

我用修复版 SUT 实测（同一 `classify` 调用、同一 7 例批）：

```
SET        computed.basis='<non-string basis: set>'   dumps(computed)=ok   dumps(verdict)=RAISE Object of type set is not JSON serializable
FROZENSET  computed.basis='<non-string basis: frozenset>'  dumps(computed)=ok   dumps(verdict)=RAISE ...
BYTES      computed.basis='<non-string basis: bytes>'      dumps(computed)=ok   dumps(verdict)=RAISE ...
OBJECT     computed.basis='<non-string basis: object>'     dumps(computed)=ok   dumps(verdict)=RAISE ...
DICT/LIST/STR_OK                                            dumps(computed)=ok   dumps(verdict)=ok
=> 整批 report 的 json.dumps: RAISE TypeError: Object of type set is not JSON serializable  (批仍会中止)
```

即：**修复后的 SUT 仍存在一条"裁决正确但报告写不出 ⇒ 整批中止"的路径**，只是位置从
`computed["basis"]` 移到了 `claim["basis"]`。这与 CF-I14I-2 想要消除的失败模式**同类**。

**同时必须给出该发现的边界（这是本条的定性关键，请勿扩大）：**

- 该路径**在冻结门内结构性不可达**：门的 14 个用例来自 `cases.i14h.json`，是 **JSON 解析**产物，
  JSON 不存在 `set`/`frozenset`/`bytes`/`object` 字面量；H5/H6 携带的是 list/dict，而 list/dict
  **可**序列化。⇒ 门 rc 0 **不受本条影响**，本卡退出判据**不受本条影响**。
- 该路径只在**进程内直接调用 `classify()`** 且传入非 JSON 原生类型时可达。
- 因此这是**潜伏**项（latent），不是本卡的实体缺陷，**不**构成退回理由。

**并须更正实现者对该缺陷的表述**：CF-I14I-2 在 `handoff.json` 中的原话是
"`computed['basis']` echoed the raw claim value … so `json.dumps(report)` raised"。
严格说，修复前 `json.dumps(report)` 的失败**并非**由 `computed['basis']` 单独造成：
`claim['basis']` 同样会让它失败，故**只改 `computed` 并不足以**让那句话成立。
修复前的实际崩溃源有**两个**，实现者修了其中一个。这一表述需要在下游文本中更正。

### F-3（确认，信息级）"list/dict 专属"的归因**精确成立**，且我把它收窄得更准

我的 27 取值探针（与实现者 18 取值探针**独立编写**）在修复前 SUT 上的实测：

| 取值类别 | 修复前实测 | 修复后 |
|---|---|---|
| 登记字符串 / 未登记字符串 / `""` / `null` / 缺键 | 正常裁决，无崩溃 | 同 |
| **`list`（含空、含嵌套、含 list-of-list）** | **`TypeError: unhashable type: 'list'` @ `:202`** | 逐例 `R-BASIS-UNKNOWN` |
| **`dict`（含空、含嵌套）** | **`TypeError: unhashable type: 'dict'` @ `:202`** | 逐例 `R-BASIS-UNKNOWN` |
| `set` / `frozenset` / `tuple`（可哈希） | `R-BASIS-UNKNOWN`，**无崩溃** | 同 + 可序列化 |
| `int` / `float` / `bool` | `R-BASIS-UNKNOWN`，无崩溃 | 同 |
| **`tuple` 内含 list/dict（不可哈希）** | **同样在 `:202` 崩溃** ← 我新加的边界 | 逐例 `R-BASIS-UNKNOWN` |

崩溃点**逐例都精确落在 `:202`**，与卡片归因一致。我新增的边界说明：
"崩溃是 list/dict 专属"应更准确地表述为**"崩溃是*不可哈希*专属；list/dict 是其在 JSON 输入下的全部可达形式"**——
`("union_of_windows",)` 不崩，但 `(["union_of_windows"],)` **崩**。修复后的类型护栏
（先判 kind 再判登记）**两种都覆盖**，比"只挡 list/dict"更强，方向上无风险。

### F-4（确认，信息级）set/tuple 的"反过拟合"证明**成立**

修复前臂 25 个失败中，**7 个**是含 list/dict 的容器裁决行、**12 个**是可序列化行、
**5 个**是 d3 派生键行、**1 个**是"毒例不拖垮整批"；而
`test_container_basis_refused_per_case[set]` / `[tuple]` / `[int-zero]` / `[float-one]` / `[bool-true]`
**全部 PASS**。即"set/tuple 的裁决碰巧正确"与"list/dict 崩溃"被**分离**开，
类型护栏既没有过拟合（不是一律拒绝：N1/N2 与 H7/H8 等登记字符串仍按实质裁决），
也没有欠拟合（list/dict/嵌套/不可哈希 tuple 全被挡）。**这是本卡设计得最好的一处。**

### F-5（确认，信息级）H12 实测通过

我自己的门产物中：

```
H12: verdict=reject_claim  refusals=['R-CLAIM-EXCEEDS','R-QC-IN-OBS']
     union_seconds=2220.0  quick_check_overlap_seconds=480.0  basis='union_of_windows'
```

三项与卡片第 5 节点名要求**逐项吻合**。H12 无 pytest 对应用例（I-14-H CF-I14H-3 覆盖缺口）
仍然存在，但冻结门现已真正通过，缺口已按其设计被门覆盖。

### F-6（确认，信息级）派生语义正确、四组合齐全；W4/W5 算术**经复核无误**

修复后源码：`quick_check_in_observation_intervals = (qc_overlap_seconds > 0)`；
`sum_used_for_natural_duration = (basis_kind == "str" and basis == "sum_of_windows")` —— 与卡片第 6 条规定语义一致。
两个键**互不蕴含**，`(F,F)`/`(T,T)`/`(T,F)`/`(F,T)` 在 rider 套件中**四组合齐全且各自可失败**（F-1 的变异体证明 4 例会红）。

**本轮一度怀疑 `oracle.md §4` 的 W4/W5 一行（`2940 / 3480 / 540 / 480`）中两个末位值互换，遂逐项重算并撤回该怀疑：**
按其自身给出的 windows `[00:00–00:29],[00:20–00:49]` + quick_check `00:29–00:37` 独立手算得
`sum=3480`、两窗重叠 `=540`、`union=2940`、quick_check 与观察区间相交 `=480`
⇒ 与该行 `union / sum / overlap / qc_overlap = 2940 / 3480 / 540 / 480` **逐项吻合，无笔误**。
（记录此次自我更正，以免下游误信一份不存在的"勘误要求"。）

**仅存一处情景命名歧义（不构成缺陷，但会误导下游）**：`oracle.md §4` 用 "W4 重叠窗求和 / W5 重叠窗并集"
命名 `(True, True)` / `(True, False)` 两个**新**情景，但 **W4/W5 并不在 14 例冻结门内**——
该门的用例集合实测为 `['W1','H1'…'H12','C2']`，而 W4/W5 属于 r1 前像 `cases.json` 的 20 例集合
（另一组输入，其自身实测 `quick_check_overlap_seconds = 0.0`）。
§4 的表格本身**未**对 W4/W5 这两个冻结用例断言 `(True, True)`，故这不是期望错误；
但它解释了下游为何会误以为"门内已出现 `(T,T)`"——**门内没有**（见 F-1 与 §7 的取值组合统计）。

### F-7（确认，信息级）卡片引用的行号在修复后已漂移

卡片与 oracle 用 `:202`（护栏）、`:241`/`:248`（两个键）指位。修复版中实际位置为
**`:252`（护栏）、`:291`、`:298`**（`:202` 在修复版是 `if qc_started is not None…`）。
`changes.diff` 的 hunk 头（`@@ -198,8 +252,9 @@` 等）**已正确反映新行号**，故这是卡片正文的陈旧指位，
不是实现缺陷。下游若按 `:241`/`:248` 检索修复版会**读错行**，建议在验收文本中改按
**符号名**（`_basis_kind` / `quick_check_in_observation_intervals` / `sum_used_for_natural_duration`）指位。

---

## 3. 对 CF-I14I-2 的范围裁决（reviewer ruling）

**裁决：留在 I-14-I 内 —— 不拆分。** 但附两项条件（见下），且**不得**把该改动表述为已彻底闭合。

**理由（三条，逐条对应卡片条文）：**

1. **它落在卡片第 1 条的授权范围之内，而非之外。** 卡片第 1 条的修复指令是
   "在成员测试前加类型护栏（例如 `isinstance(basis, str)`；**非字符串一律归入未登记** ⇒ `R-BASIS-UNKNOWN`），
   **逐例**拒绝，而不是让整批崩溃"。卡片的**实现目标**（observable goal）是"**逐例**裁决、**不再整批崩溃**"。
   set basis 在修复前**恰好**使"整批崩溃"以另一种形式发生（`json.dumps` 处），
   所以修 `_basis_repr` 是让卡片第 1 条**真正达成**的必要步骤，而非顺带扩张。
   `handoff.json` 自述的 `why_it_might_be_out_of_scope`（"卡片字面只授权改成员测试"）
   是**过度保守**的自限——按文义解会得出"修了护栏但仍会整批崩溃"的荒谬结果。
2. **零外部性。** 冻结期望中 computed 含 `basis` 的只有 W1/C2，且都为字符串/`null`；
   `basis` 在 14 例中**无任何取值约束**；r1 前像材料未动。故该改动对冻结门**结构上不可能有影响**，
   而我实测门 rc 0、`mismatch_count=0`、落盘件逐字节相同，**证实**了这一点。
3. **改动最小且方向 fail-closed。** `_basis_repr` 把非字符串回填为 `"<non-string basis: T>"`，
   不会让任何非字符串值在下游冒充登记 basis，方向与卡片的 fail-closed 要求一致。

**条件（必须随验收文本一并记录）：**

- **(a) 表述更正**：须写明"CF-I14I-2 修的是 `computed["basis"]`；`classify()` 仍原样回填 `claim`，
  故非 JSON 原生 basis 仍会使**进程内**整批报告不可序列化（F-2）。此路径在门内不可达，
  不影响本卡，但**该失败模式并未被完全消除**。"
- **(b) 不扩权**：本条**不**授权扩大 `claim` 回填的改动；把它一并改掉属**新卡**范围（见 §8 后续项 2），
  因为那会改变 verdict 的公开形状，需要自己的期望与红绿证据。

**若上游坚持要拆**：可接受的替代方案是**不拆但显式登记**——在 `handoff.json` 的
`carried_findings` 里把 CF-I14I-2 的 `class` 从"NEW FINDING, disclosed"改为
"IN-SCOPE CONSEQUENCE of card item 1（卡片第 1 条的必要推论）"，因为按上述推理它并非"新范围"。
我倾向于前者（保留 finding 编号，更正 class 措辞）。

---

## 4. `SUT_VERSION` 是否应 bump 的裁决

**裁决：不 bump 是正确的，但需要一个显式的、可机检的 r3 标识。**

- 卡片第 7 条明文"**不得**改 `SUT_VERSION` 掩盖差异"；且不改可让"冻结材料仍能识别它所冻结的修订"。
  实测：修复版 `SUT_VERSION = "i14b-after-2"` 与修复前**逐字符相同**（`:79` vs 前像 `:55`）；
  r1 为 `"i14b-after-1"`。**两者不能靠版本串区分**，只能靠 sha256（`9edb9515…` vs `7fff6f0c…`）。
- **风险**：门报告里的 `sut_version` 字段对"是否已应用 r3"**零信息量**；下游若只看该字段，
  会把修复前/修复后视为同一修订。这正是卡片第 7 条想要防的事，实际却仍然发生。
- **建议（不阻塞本卡）**：保留 `SUT_VERSION` 不变，改为在**报告里新增一个不与它冲突的字段**
  （例如 `sut_sha256`/`revision_note: "r3"`）以机检区分——注意 `run_cases.py:121` 已独立记录
  `sut_sha256`，故**门产物本身已能区分**，缺的只是下游读者的默认习惯。
  `changes.diff` 与源码注释里已写有 "r3 (I-14-I…)" 字样，故 r3 标记**已存在但未进入可机检字段**。
  ⇒ 建议在 `qualification.json` 落地时把 `sut_sha256=9edb9515…` 与 `revision="r3"` 一并写入。

---

## 5. 实现者 10 项声明的逐项裁定

| # | 声明 | 裁定 |
|---|---|---|
| 1 | 14-case 门 rc 0，各计数 | **成立**（R2/R4/R5，且落盘件与门产物逐字节相同） |
| 2 | xfail 已解除且为真通过；I-14-H 套件字节未改给出 11P+1 XPASSED | **成立**（R7/R8；这是本卡最强证据，已亲验 XFAIL→XPASS 同一份字节） |
| 3 | 双向可失败：修复前 25F/20P；r1 43F/2P | **成立**（R9，计数与失败行归属逐项吻合） |
| 4 | 派生键已派生；W1=(F,F)/H10=(F,T)/H11/H12=(T,F)；修复前 14 例恒 False | **前半成立、后半措辞过强**：取值表成立（R2），修复前恒 False 由**源码字面量**证明；但"判别力**落在冻结门内**"被 R12 证伪 → **F-1** |
| 5 | list/dict 专属而非容器通病；set/tuple 裁决行在修复前臂 PASS | **成立**（R10/F-3/F-4；并收窄为"不可哈希专属"） |
| 6 | H12 通过：双拒绝码、union 2220.0、overlap 480.0 | **成立**（R2/F-5） |
| 7 | CF-I14I-2 修复 + 请 reviewer 裁决范围 | **修复成立但不完整**（F-2）；范围裁决见 §3：**留在本卡** |
| 8 | 冻结件未改：`frozen_expectations.json` 仍 2220；`cases.i14h.json` `40260c24…`；`run_cases.py` `f2a07d0b…` | **成立**（R1/R15，五个冻结材料与 I-14-H 副本**逐字节相同**） |
| 9 | 生产树零写入 | **成立**（R15：`git status`、`git diff`、`git diff --cached` 对 `scripts` 全空） |
| 10 | `SUT_VERSION` 未 bump | **成立**；裁决见 §4 |

---

## 6. 未验证 / 存疑清单（unverified list）

1. **实现者的 pytest basetemp 目录**（`harness/scratch/pytest-i14i-*`）**已被删除**，我无法核对
   其当时两次运行的原始 basetemp。缓解：我在**自己的** basetemp 下重跑三臂，得到**完全相同的计数**
   （45P / 25F+20P / 43F+2P）与相同的失败行归属，故结论不受影响。
2. **`CF-I14I-3`（审计脚本运算符优先级瞬时缺陷）无法事后验证**：实现者自述"修正后的运行**原地替换**了
   缺陷运行，故缺陷运行不在证据树内"。现存事实只有：现版本 `audit_postfix.py`（`67f2f30b…`）对
   **我自己的**门产物给出 44/0。⇒ 该缺陷**曾经发生**这一点属**仅有自述、无证据**（与 I-14-H 的
   CF-I14H-4"无法证明"同类）。影响：无——审计脚本只是便利检查器，**门是未修改的 `run_cases.py`**。
3. **`oracle.md` 的"冻结前"内容无法独立验证其冻结时序**。`evidence/freeze_instant.json`
   （`d343ae60…`，时刻 `2026-09-21T19:59:53Z`）声称冻结时 SUT 仍为 `7fff6f0c…`。
   我可核实的是**结果自洽**：`before/` 前像现仍为 `7fff6f0c…`，且期望值在修复前 SUT 上确实**以相反结果失败或崩溃**
   （R9/R10）——这排除了"期望照修复后的实现抄写"的可能，但不构成对**时刻**的独立证明。
   `oracle.md` 现 sha256 `3842f2d4…`（17246 B），与 `handoff.json` 记载的冻结值 `7879ba39…`（12017 B）**不同**，
   差异为追加的 §9（`handoff.json` **已主动披露**该文件当前哈希会变，并明确要求"用 Get-FileHash 重算，
   不要相信写入文件的值"）⇒ 披露充分，不记为缺陷。
4. **`disclosure_adaptation` / `accuracy` / 真实自然观察 / 真实 UI 即时性 / SLO**：本轮**未新增任何验证**，
   维持 `unmapped` / `unproven` / NOT GRANTED。全部 14 例与 45 例均为 `SYNTHETIC-TIMER-ONLY` 合成时间输入。
   **不得**被解读为已获得。
5. **W4/W5 情景命名**：`oracle.md §4` 以 "W4/W5" 命名"重叠窗求和/并集"情景，但这两个 id 在
   14 例冻结门内**并不存在**（门内为 `W1 + H1…H12 + C2`；W4/W5 属 r1 前像 `cases.json` 的另一组输入）。
   我已逐项重算并确认 §4 表格的 `2940 / 3480 / 540 / 480` 手算**无误**（见 F-6），
   亦确认 §4 **未**对 W4/W5 断言 `(True, True)`。残留不确定性仅在于"命名是否会让下游误读"，
   属表述层面，无需进一步核实。
6. **I-14-H 的验收措辞何时解除**：本报告只证明**解除的实体条件已满足**；
   更新 I-14-H 的 `qualification.json` / `handoff.json` 承运文本属**台账动作**，
   reviewer 不做（`implementer_never_signs_acceptance` 同理，reviewer 也不改被审对象的承运件）。

---

## 7. 实体核对：数字与哈希（本报告全部引自本轮独立重算）

**我的门重跑（R2/R4）**

```
runner rc                     = 0        (期望 0)
ok                            = true
case_count                    = 14
mismatch_count                = 0
accepted_ineligible_count     = 0
accepted_ineligible           = []
sut_raw_returncode            = 0        (修复前 4)
sut_version                   = "i14b-after-2"
sut_accepted_claim_count      = 3
sut_refusal_code_count        = 12
sut_sha256                    = 9edb95155202432ed01b2c68d06f74a00882287e934cda6cead0e14140493b04
cases_sha256                  = 40260c2425cbe4e708f36c294fa07fe01ac608b3c13bd1a4d3eafddd9762aeda
expectations_sha256           = bffb11c2727d2227f3b1c345577f9acb7aeb2bae03949bad06741d990164d17a
runner_sha256                 = f2a07d0b85c5dcb3a233d9010ad9deead70b22535ab82a61414d2ef7f54f7c23
sut_report.json               = 21416 B, 与实现者门产物逐字节相同 (11f27c8e…)
```

**派生化在门报告内的取值（我的产物）**：`W1=(F,F)`、`H10=(F,T)`、`H11=(T,F)`、`H12=(T,F)`；
出现 3 个不同组合（`(T,T)` 只在 rider 套件中出现）；修复前两键为源码字面量 `False`（不可随用例变化）。
**14 例中这两键的取值约束**：`quick_check_in_observation_intervals` 仅 W1（`False`）；
`sum_used_for_natural_duration` **无**。

**关键哈希（本轮重算，与 `handoff.json` 记载全部吻合）**

```
iso/natural_window.py (FIXED)              9edb95155202432ed01b2c68d06f74a00882287e934cda6cead0e14140493b04  23162 B
before/natural_window.i14b-after-2.py       7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796  20293 B
before/natural_window.r1sut.py             495a44111a854bd5b76d39aeae91d11ab789fe48bb8bcbc9ae3af4b87d8c5b95  17498 B
harness/run_cases.py (UNMODIFIED)          f2a07d0b85c5dcb3a233d9010ad9deead70b22535ab82a61414d2ef7f54f7c23   8390 B
harness/cases.i14h.json (UNMODIFIED)       40260c2425cbe4e708f36c294fa07fe01ac608b3c13bd1a4d3eafddd9762aeda  26630 B
harness/frozen_expectations.i14h.json      bffb11c2727d2227f3b1c345577f9acb7aeb2bae03949bad06741d990164d17a  13100 B
harness/frozen_expectations.json (r1前像)  3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b   4069 B  (正文仍为 union_seconds 2220)
harness/test_i14i_natural_window.py        16ff4561299fc184efe292f114b909a668497c9c86610260519e128805919b59  18651 B  (xfail 装饰器 0)
harness/archive_test_i14h_original.py      147cdc1c589bef458ba2d741568f22bfd56600cefcfc7757d030accc4630f935   8143 B  (= I-14-H 原件，逐字节相同)
gate cases_report.json (landed == impl)    e8925fdcf3a99727b63401b29fe893588a1777e4a7361c6f8d66cdcfc327a288   1647 B
gate sut_report.json                       11f27c8ee0cb84a95ee82ffc90a3ba40633a7fb29bfda650a08405529bd26af3  21416 B  (== 我的重跑)
pre-fix gate cases_report.json             91ff3a5d64c22b0caa5d291d17c486a9ade7a1188df429fc629e3d0ec4716413   1521 B
I-14-H/a20260919-01/review.md              97997d6d26af5a1fd36e486c508a027642f4492af1f5415fe3f25bc929e130b2
变异体（两键改回字面量）                    2265bd0d7fe4a950d737e77ef6409991d9d30978b4eb61a54b33cb0cb71944f0   (reviewer 临时产物，未落 attempt)
```

**生产树**：`git status --porcelain -- scripts` = 0 字节；`git diff --stat` / `git diff --cached --stat` 对 `scripts` 亦空。
SUT 位于 attempt 内、不在生产树。**零生产写入，已机检。**

---

## 8. 强制后续项（随验收一并移交）

1. **更正 F-1 的能力陈述**：任何下游文本不得再写"派生键的判别力已落在冻结门内部"。
   正确表述为："派生键的**可失败判据在 rider 套件**（4 例覆盖四组合）；冻结门**不**校验这两个键的取值，
   门的 rc 0 只证明其余 14 例端到端一致 + 批不再中止。"
   （可选、非阻塞：给 `frozen_expectations.i14h.json` **追加** H10/H11 的这两键期望以让门获得判别力——
   但那是**新卡**范围，须沿用追加式 provenance，本卡不得回改冻结正文。）
2. **登记 F-2 的潜伏项**：为 `classify()` 的 `claim` 回填单独立卡（或并入下游加固卡）。
   要求：非 JSON 原生 basis 在**任何**报告写出路径上都不中止整批；须自带红绿证据。
3. **消除 F-6 的情景命名歧义**：`oracle.md §4` 宜改为**不复用** "W4/W5" 这两个 id
   （它们属 r1 前像 `cases.json` 的 20 例集合、**不在**本卡的 14 例冻结门内），
   改用"重叠窗求和/并集"这类描述性情景键；按追加式标注，**不得**回改 §3/§4 冻结表本身。
4. **登记 F-7 指位漂移**：验收文本改用符号名指位（`:202`→`:252`，`:241`→`:291`，`:248`→`:298`）。
5. **解除 I-14-H 的"12/14"限定**：实体条件已满足；承运件更新属台账动作，由 carrier-landing 执行。
6. **台账**：把 `sut_sha256=9edb9515…` 与 `revision="r3"` 写入 I-14-I 的 `qualification.json`
   （见 §4），以便下游区分修复前/后（二者 `SUT_VERSION` 相同）。

---

## 9. 边界声明

- `disclosure_adaptation` = **unmapped**；`accuracy` = **unproven**（本卡未触及）。
- 真实自然观察资格 / 真实 UI 即时性 / SLO-性能：**NOT GRANTED**（沿用 I-14-B / I-14-H）。
- 全部用例为 **SYNTHETIC-TIMER-ONLY** 合成时间输入；**未**观察、测量或完成任何真实自然周期。
- 本卡**未**改 `SUT_VERSION`、**未**回改任何冻结正文、**未**触碰生产树。
- reviewer 只读：未修改 attempt 内任何既有文件；本轮全部产物写在 attempt 之外的临时目录。
- **reviewer 不自签实现者的工作**：本报告的 ACCEPT 是 reviewer 对**证据**的裁定；
  实现者仍为 `implementer_signed=false` / `implementer_never_signs_acceptance=true`。

---

## 10. 本报告自身的可核验性

本报告由独立 reviewer 撰写，所有数字来自 §1 的 R1–R15 本轮重跑。若要复核本报告：

1. 重算 §7 的 13 个哈希，与表中值比对；
2. 用 `harness/run_cases.py` + `harness/cases.i14h.json` + `harness/frozen_expectations.i14h.json`
   对 `iso/natural_window.py` 重跑，应得 rc 0 与上表计数，且 `sut_report.json` 应等于 `11f27c8e…`；
3. 把 §7 的变异体（两键改回 `False`）跑同一门，应得 **rc 0**（复现 F-1）；
4. 把同一变异体跑 `harness/test_i14i_natural_window.py`，应得 **4 failed**（复现 F-1 的判据归属）；
5. 用 `I14H_SUT` 指向 `before/natural_window.i14b-after-2.py` 跑 `harness/archive_test_i14h_original.py`，
   应得 `1 xfailed`；指向 `iso/natural_window.py` 应得 `1 xpassed`（复现 R7/R8）。

### 附：本报告的自我更正记录（保留，不静默覆盖）

- **对 F-6 的一次自我更正**：本报告初稿曾断言 `oracle.md §4` 的 W4/W5 行
  （`2940 / 3480 / 540 / 480`）中 `quick_check_overlap_seconds` 与 `overlap_seconds` **互换、有笔误**，
  并据此在 §8 写入一条"勘误"要求。**该断言是错的**：逐项手算（见 F-6）得两窗重叠 `540`、
  quick_check 与观察区间相交 `480`，与 §4 表格**逐项吻合**。我已在 F-6、§6.5、§8.3 三处**撤回**该断言
  并改为"情景命名歧义"。此处保留记录，以免下游按一份不存在的勘误去改冻结文档。
- 复核过程中我还曾**误判** F-2 的严重性一次：最初的探针对**整个 `classify()` 返回值**做 `json.dumps`，
  于是把 `claim` 回填造成的失败与 `computed` 的失败混在一起，一度疑似"修复后 set 仍会中止整批"。
  经核对实现者探针与本卡退出判据的真实序列化对象（**`computed`**）后，已把 F-2 的定性收窄为
  **潜伏项 / 门内不可达**（见 F-2 的边界说明）。两次更正的方向都是**削弱**我自己的指控，
  记录在此以便下游判断本报告的校准方向。
