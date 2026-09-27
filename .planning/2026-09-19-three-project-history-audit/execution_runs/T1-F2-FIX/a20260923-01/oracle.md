# T1-F2-FIX oracle（**运行前冻结** · 2026-09-23）

卡：**T1-F2-FIX** / attempt `a20260923-01`。两个同族非全函数缺陷的续修卡，源自主卡
**T1-10-FIX 的 decision §6 范围外登记**（`execution_runs/T1-10-FIX/a20260923-01/decision.md` L108–117，
sha `146797…` 见 binding.json）与 owner order「发现的缺陷都要全部修复」。
**范围冻结 = F-1 + F-2 两缺陷 + 负控 + 锚核**；F-3 只作 pending-ruling 声明（§4，**不自填**）；
T1-10-FIX §6 表中「P4 已登记未复测」的 `windows`/`sampled_at`/`ledger.daily` 容器族**不在本卡范围**（同批续修卡，移交）。

- **修复前置层（prerequisite pin）**：T1-10-FIX 的 `changes.diff` =
  **`625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac`**（+229 −4，11534 B，两文件）。
  其落地态 = 修复后 `iso/natural_window.py` **`064e5381444d35a8ab1184d6c8d2eaa839a40f96c704ae7995fa3b660c7e273d`**
  （= I-14-B r2 基线 `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` + 其两处修复）。
- **合并序（merge order）**：**theirs first（625ecfe4…），mine second**。本卡 `changes.diff` 的
  **左侧 = T1-10-FIX 修复后 iso（064e5381…）**，由 difflib 对该 fixed iso 生成 ⇒ hunks 天然落在其修复树之上。
  其变更行（r2 基线编号 {60,66,199,200} → 修复后编号 60–74 / 207–217）与本卡两处 hunk 的位置关系：
  本卡 F-1 hunk 在 **56±**（其前首 hunk 起于 60）、F-2 hunk 在 **360±**（其 E1 hunk 止于 217）——
  生成后在 decision.md 登记实测 context 区间；无论是否重叠，基址恒为其修复树（协调令已确认）。
- SUT（隔离副本）：`worktree/i14b/iso/natural_window.py`；RED 基线副本 =
  `worktree_before/i14b/iso/natural_window.py`（= 064e5381…）；diff 左侧留档 =
  `worktree/baseline/natural_window.t1_10fixed.pristine.py`（064e5381…）。
- 源树 **READ-ONLY**（写入 0 次，pin 复核）；交付 **仅 changes.diff**（零生产合并、**无 git**、无删除）。
- **F-2 语义 = 父方 pre-freeze 裁定**（见 §3 逐字引）；**F-3 = pending-ruling**（见 §4）。
- 本文件在**任何探针/套件/变异/负控运行之前**写成；一切 RED/GREEN/MUT/NC 期望值先于观测冻结。
- `frozen_now = 2026-09-20T02:56:38Z`（沿用 I-14-B oracle §3/§4，不重设）。

---

## 1. 两缺陷的行级表（冻结；行号 = 本卡 before 树 = T1-10-FIX 修复后文件，括号内 = r2 基线编号）

| id | 判据 | 入口（before 行） | before 代码 | 畸形输入下的行为（T1-10-FIX 实测 §6，本卡 RED 复测） |
|---|---|---|---|---|
| **F-1** | **J7** 只有可信时钟可完成窗口（oracle §2 L64） | 定义 `:56`（同）`TRUSTED_CLOCKS = {"system_utc", "scheduler_trusted"}`（**set**）+ 成员测试守卫行 `:355`（**基线 :338**）`if clock_source not in TRUSTED_CLOCKS:  # J7` | set 成员测试**先哈希探针** | `clock_source=["system_utc"]` → **rc=4、无报告、全批 0 裁决**、raw `internal_error: unhashable type: 'list'`（direct：`TypeError`）。**reviewer P4 未点名此条**（T1-10-FIX decision §6 F-1 行，新发现） |
| **F-2** | **J11** 主张不得超过事实（oracle §2 L68） | 载体读取 `:360`（**基线 :343**）`claim_status = (fields.get("_claim") or {}).get("status")` | 真值非字典 claim 载体 → `.get` **AttributeError** | `claim=["pending"]` → **rc=4、无报告、全批 0 裁决**、raw `'list' object has no attribute 'get'`（P4「claim 为 list」的日历落点；T1-10-FIX 只修了 basis 落点 E1） |
| F-3（**非本卡**） | 时间戳 `_parse` | `:82-88` | 畸形 iso → `ValueError` | `started_at="not-a-timestamp"` → rc=4 `Invalid isoformat string` —— **schema 级 rc 归属 = pending，见 §4** |

**修法（冻结的修复设计，只动两处）**：

- **F-1 = set→tuple**（与 T1-10-FIX E2/E3 同一 trick）：`TRUSTED_CLOCKS` 定义行改 **tuple**；
  **守卫行 `:355` 文本一字不动**。依据（锚核先行，见 §6）：`mutate.r2.py` MUT-7 的文本钉是**守卫行**
  `"    if clock_source not in TRUSTED_CLOCKS:  # J7"`（mutate.r2.py:63），**不钉定义行** ⇒ set→tuple 不破 MUT-7。
  tuple 成员测试用 `==` 逐元素比较、不哈希 ⇒ 对一切 JSON 值**全函数**；不可读（容器）时钟
  `∉` 可信集 ⇒ 走既有 **`R-SIMULATED-CLOCK`**（J7 本就是无条件拒：「即使账本本身合规」）。
  报告字段 `sorted(TRUSTED_CLOCKS)`（`:499`）对 tuple 语义不变 ⇒ 正常路径字节同。
- **F-2 = isinstance-dict 守卫（E1 模板形状）+ fail-closed 读替身**（父方 pre-freeze 裁定，§3）：
  ```
  claim = fields.get("_claim")
  if not isinstance(claim, dict):
      claim = {"status": "complete"}      # 读替身（fail-closed），见 §3
  claim_status = claim.get("status")
  if claim_status == "complete" and computed_status != "complete":  # J11   ← 文本一字不动
  ```
  即：**载体先验（同 T1-10-FIX E1 模板 `claim = fields.get("_claim"); if not isinstance(claim, dict): …`）**，
  畸形载体读作**最强主张 status="complete"** ⇒ **未改动的 J11 行**在事实不足 complete 时拒
  **`R-CLAIM-EXCEEDS`**（既有码：oracle §2 J11 / §11.3 P2 行，**不新增 R-\* 码**）。
  真正**缺键**（dict 载体无 status 键 / claim 缺失→classify 已归一为 `{}`）走**原路径字节不变**（事实定）。

## 2. 冻结探针族与期望（RED=before=064e5381…；GREEN=after=修复后）

**事实族（calendar fields，逐字取自 pin 的 `harness/cases.r2.json` 对应 case，探针脚本引用不重抄）**：
`F-C1` = oracle §4 C1 攻击账本（7 条同未来瞬时、全空 hash、weekly/monthly/alerts 齐 → 拒
`R-EMPTY-EVIDENCE`+`R-FUTURE-CLOCK`+`R-SAME-INSTANT`，daily_count=0 → **pending**）；
`F-C2` = C2（daily5/weekly1/其余0、合规 → **pending**、无违规）；
`F-C3` = C3（四窗全齐 → **complete**、无违规）；
`F-EMPTY` = T1-10-FIX adjacent 探针同款（空账本 → pending、无违规）。
所有 F-1 探针 `clock_source` 之外的字段 = F-C? 原字节；所有 F-2 探针 `clock_source="system_utc"`（J7 隔离）。

### F-1 族（facts=F-C3，claim=C3 原 dict → 正常时 accept）

| id | tamper（仅 clock_source） | RED 期望（before） | GREEN 期望（after） |
|---|---|---|---|
| **K1** | `["system_utc"]`（T1-10-FIX adjacent 同款） | **rc=4、无报告、0 裁决**、raw `unhashable type: 'list'`；direct `TypeError` | rc=0、`reject_claim`+`["R-SIMULATED-CLOCK"]`、computed.clock_source 原样回显、direct 不抛 |
| **K2** | `{"source":"system_utc"}` | 同上、`'dict'` | 同 K1 干净拒绝 |
| **K3** | `[["x"]]` 嵌套 | 同上、`'list'` | 同 K1 |
| **K4** | `"system_utc"`（对照=原值） | rc=0 `accept` | **行字节相同** |
| **K5** | `"simulated_clock_advanced_by_7_days"`（C5 同串） | rc=0 `reject`+`[R-SIMULATED-CLOCK]` | **行字节相同** |
| **K6** | `5`（可哈希标量，从未崩过） | rc=0 `reject`+`[R-SIMULATED-CLOCK]` | **行字节相同** |
| **K7** | 键缺失（clock_source absent） | rc=0 `reject`+`[R-SIMULATED-CLOCK]` | **行字节相同** |
| **K8** | `true`（bool，可哈希） | rc=0 `reject`+`[R-SIMULATED-CLOCK]` | **行字节相同** |

### F-2 族（clock_source=system_utc；carrier=claim 本体）

| id | carrier tamper | facts | RED 期望（before） | GREEN 期望（after，§3 语义） |
|---|---|---|---|---|
| **S1** | `["pending"]` | F-EMPTY | **rc=4、0 裁决**、raw `'list' object has no attribute 'get'`；direct `AttributeError` | rc=0 `reject`+**`["R-CLAIM-EXCEEDS"]`**（事实 pending ⇒ fail-closed 拒） |
| **S2** | `["complete"]` | **F-C1**（父方指定探针账本） | 同上 | rc=0 `reject`+**`["R-CLAIM-EXCEEDS","R-EMPTY-EVIDENCE","R-FUTURE-CLOCK","R-SAME-INSTANT"]`**（fail-closed 拒加入 J11 码；其余=账本既有码） |
| **S3** | `"pending"`（str） | F-C2 | raw `'str' object has no attribute 'get'` | rc=0 `reject`+`["R-CLAIM-EXCEEDS"]` |
| **S4** | `5`（int） | F-C2 | raw `'int' …` | 同 S3 |
| **S5** | `true`（bool 真值） | F-C2 | raw `'bool' …` | 同 S3 |
| **S6** | `["pending"]` | **F-C3（complete 事实）** | rc=4 崩 | **rc=0 `accept`、refusals=[]** —— 冻结边界（§3.3）：事实支持一切状态主张，既有词表无码可拒；父方裁定的拒明确 scope 为「对 pending 事实拒」 |
| **S7a/b/c** | 缺键侧对照：`{}` / `{"other":1}` / claim 键整体缺失 | F-C2 | rc=0 `accept`（dict/缺失**从未崩**） | **行字节相同**（缺键=原路径，事实定） |
| **S8** | claim=`{}`（**缺键**） | **F-C1** | rc=0 `reject`+`["R-EMPTY-EVIDENCE","R-FUTURE-CLOCK","R-SAME-INSTANT"]`（**无** R-CLAIM-EXCEEDS） | **行字节相同** —— 与 S2 成对 = 「**缺键≠畸形**」的可判定对照 |
| **S9** | `{"status":"complete"}`（=C1 原样） | F-C1 | rc=0 `reject`+四码含 R-CLAIM-EXCEEDS | **行字节相同** |
| **S10** | `{"status":"pending"}`（=C2 原样） | F-C2 | rc=0 `accept` | **行字节相同** |

### 联合批与臂（爆炸半径，T1-10-FIX A/C 同形）

| id | 批内容 | RED 期望（before） | GREEN 期望（after） |
|---|---|---|---|
| **J1** | [W-GOOD(window B6), C3-GOOD, C2-GOOD, **BAD-F1**(F-C3+clock 容器), **BAD-F2**(F-C2+carrier 容器)]（BAD-F1 在前） | **rc=4、0/5 裁决**、raw `unhashable type: 'list'` | rc=0、**5/5 裁决**、拒={BAD-F1 `[R-SIMULATED-CLOCK]`, BAD-F2 `[R-CLAIM-EXCEEDS]`}、其余 3 个 accept |
| **J1b** | 同 J1 但 **BAD-F2 在前** | **rc=4、0/5**、raw `'list' object has no attribute 'get'` | 同 J1 |
| **Arm A**（F-1 隔离） | 6× C3-GOOD + 1× BAD-F1（**仅 clock_source 不同**） | **rc=4、0/7** | rc=0、7/7、**仅 BAD-F1 被拒**`[R-SIMULATED-CLOCK]` |
| **Arm B**（对照：可哈希坏串，pre-existing 正确拒绝） | 6× C3-GOOD + 1× clock="simulated_…"（仅串不同） | rc=0、7/7、仅其被拒 | **同 before（不变）** |
| **Arm C**（跨类联合） | 1× W-GOOD + 2× C3-GOOD + 2× C2-GOOD + BAD-F1 + BAD-F2 = 7 | **rc=4、0/7** | rc=0、7/7、**仅 {BAD-F1, BAD-F2} 被拒**、其余 5 accept |

**崩溃判据**（=「裁决机关失灵」观测面，两缺陷同款）：(a) CLI **rc=4**、stdout `internal_error`、
**报告未写出、全批 0 裁决**；(b) 直调 `classify()` 抛**未捕获 traceback**（`TypeError`/`AttributeError`）。
GREEN 判据：rc=0、报告写出、全批裁决、拒码 ∈ oracle 既有词表、stderr 空、无 internal_error、direct 不抛。

## 3. F-2 语义（**父方 pre-freeze 裁定** —— 逐字引用，冻结权威）

> 【父方 pre-freeze 裁定：F-2 = fail-closed + 缺键≠畸形】1. present-but-malformed（claim.status 真值存在但非字典）
> → 结构化拒绝（fail-closed）：拒码=你 oracle 词表中最贴的既有码（如 R-CLAIM-EXCEEDS 类=对 pending 事实拒、
> 或你判定更贴的既有 refusal——披露选择理由）；probe 探针沿你 §4 C1 攻击账本、GREEN=rc0+该拒码+only-BAD rejected。
> 2. 真正缺键（key absent）→ 行为字节不变=事实定…… 3. 依据：basis 先例=缺键走原行为、不可读→R-BASIS-UNKNOWN 拒
> （T1-10-FIX 的 E1 修法）——「不可读≡缺键」与该先例自相矛盾；status=时钟攻击面，畸形当缺=绕过
> FUTURE-CLOCK/SAME-INSTANT 检查=旁路开口。父方 pre-freeze 裁定、引登记册本轮回执为凭。
> 4. 与 F-3（时间戳畸形 rc 归属=pending T1-10-FIX 复审裁）同边界披露；MUT-7 锚安全✓照你核（定义行不钉）。

（发信方 = 父代理 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`，本 attempt 收令时刻 2026-09-23 ~05:56 后；
逐字件录于 `binding.json.parent_pre_freeze_ruling`；**盘上登记册回执尚未落册** —— 作为移交项记入 handoff，
不因缺回执而改写本裁定内容。）

### 3.1 拒码选择与理由（披露）

选 **`R-CLAIM-EXCEEDS`**（既有码）：它是 oracle 词表中**唯一**的日历 claim 类拒绝
（§2 J11「claim.status==complete 但计算为 pending → 拒」；§11.3 P2 行同码）。语义映射：
**不可读载体 = 主张不可核验 = 按最强主张（status="complete"）读入**，随后**一字未动的 J11 行**在
事实不足 complete 时拒此码 —— 复用既有判据、零新码、MUT-11 锚行不变。
**不选**其它码的理由：`R-SIMULATED-CLOCK` 属 J7（时钟源字段，另一入口）、`R-UNKNOWN_CLASS` 属类别、
`R-BASIS-UNKNOWN` 属窗口 basis 封闭枚举（日历 claim 无 basis 语义）——均不描述「主张不可核验」。
**不新增 R-\***（T1-10-FIX oracle I-4 同纪律）。

### 3.2 缺键≠畸形（不变量，S7/S8/S9/S10 为其可判定对照）

缺键/缺失 claim（dict 或 classify 归一的 `{}`）→ `status=None` → J11 不触发 → **事实定**，
与 before **行字节相同**；畸形（真值非字典）→ fail-closed 拒（事实 pending 时）。二者在同 F-C1 事实下
（S2 拒含 R-CLAIM-EXCEEDS vs S8 拒不含）可判定区分。

### 3.3 冻结边界：complete 事实 + 畸形载体 = accept（S6）

J11 语义是「主张不得超过事实」；事实 complete 时**任何**状态主张都不超限，既有词表**无码可拒**，
凭空拒 = 自填 oracle（禁）。父方裁定的拒明确 scope 为「**对 pending 事实拒**」，S6 与此一致。
此点与 §4 同性质地登记为**语义边界披露**（如复审另有口径，属一行式跟进，不在本卡自决）。

### 3.4 本裁定不构成 I-14-B oracle 修订

`oracle.md`（I-14-B，sha `bdd0407a…`）一字不改（pin）；F-2 GREEN 语义按**父方 pre-freeze 裁定**执行，
与 T1-10-FIX I-5「按返修块指定语义执行、不构成 oracle 裁定」同构。

## 4. F-3 声明（**out-of-scope · pending-ruling · 不自填**）

畸形时间戳（`started_at="not-a-timestamp"` → `_parse` → rc=4 `Invalid isoformat string`）属
**schema 级 rc 归属问题**（rc=2 fail-closed vs per-case 拒绝 vs 维持 rc=4）：该裁定权在
**T1-10-FIX 的复审 reviewer（已派发，裁定可能中途到达）**。T1-10-FIX 明确拒绝自填（其 oracle I-5、
decision §6 F-3 行、§8 边界），**本卡继承该边界**：本卡 oracle **只声明 F-3 = out-of-scope-pending-ruling**，
不判定 rc 归属、不改 `_parse`、不把 rc=4 判为合规态也不判为非合规态（= 状态未定，待裁）。
RED 探针**不跑** F-3（跑即等于自选立场）；其 before 观测引 T1-10-FIX evidence（rc=4 raw）为登记凭据。

## 5. 冻结不变量（invariants）

- **I-1 正常路径字节同**：对 `harness/cases.r2.json`（34 case）与 `harness/cases.json`（20 case），
  before/after 两 SUT 的 `--report` 输出 **sha256 相等**；冻结门两版均 rc=0/mismatch=0/34-34；
  探针稳定行（K4–K8、S7a/b/c、S8、S9、S10、Arm B）before==after **行字节相同**。
  **显式涵盖「缺键半」**：dict 载体/缺键路径（S7/S8/S9/S10）零行为变化。
- **I-2 拒绝语义词表不变**：SUT 内 `"R-*"` 码集合 before==after（无新码）；全部 GREEN 拒码 ∈
  {R-SIMULATED-CLOCK, R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT} ⊂ oracle §2/§11.3 既有词表。
- **I-3 锚点完好（修后复读）**：`mutate.r2.py` 三锚行在 after SUT **恰一次**且**文本 byte-identical**：
  MUT-7 `"    if clock_source not in TRUSTED_CLOCKS:  # J7"`、
  MUT-11 `"    if claim_status == \"complete\" and computed_status != \"complete\":  # J11"`、
  MUT-15 `"    if basis not in BASIS_REGISTRY:  # J16 / P1"`；
  `sorted(TRUSTED_CLOCKS)` 报告位在场；r2 测试 `sorted(SUT.BASIS_REGISTRY)` 行随文件 pin 不动；
  20 臂变异机关 before==after 全红（逐臂 cases_red 相等，MUT-7→C5、MUT-15→X1–X4）。
- **I-4 rc 冻结域**：SUT rc ∈ {0,2,4}（oracle §8-errata）；GREEN 探针 rc=0 全裁决；
  RED rc=4 = **缺陷证据**（剥夺裁决形态），不判为合规态。
- **I-5 不自填**：F-3 rc 归属 pending（§4）；F-2 完整事实边界按父方裁定 scope 冻结（§3.3）；
  I-14-B oracle/review/期望/cases/runner/mutator/既有三测试 = pin 一字节不动。
- **I-6 前置层不回退**：T1-10-FIX 的修复行（BASIS_REGISTRY tuple @60–74、E1 载体守卫 @207–217、
  J16 守卫、basis 家族语义）在 after 树保持其交付态；本卡 hunks ∩ 其变更区 = ∅（生成后实测登记）；
  其 changes.diff `625ecfe4…` 与 23 测试套件/探针 39 检查为**继承面**（见 §8）。
- **I-7 边界**：源树写入 0、git 0、删除 0、状态迁移 0、签名 0、晋升 0；交付仅 changes.diff。

## 6. 冻结 MUTATION 臂（非空洞性；对 after SUT 的 scratch 副本）

| 臂 | 变异 | 期望 |
|---|---|---|
| **MUT-F1** | 修法①回退：`TRUSTED_CLOCKS = (…)` → `= {…}`（set） | K1/K2/K3 **崩溃回归**（rc=4、无报告、raw unhashable）⇒ tuple 守卫承重 |
| **MUT-F2** | 修法②回退：载体守卫块 → 原行 `claim_status = (fields.get("_claim") or {}).get("status")` | S1/S3 **崩溃回归**（rc=4、raw AttributeError）⇒ 守卫承重 |
| **MUT-A1** | 锚 grep 计数：MUT-7 / MUT-11 / MUT-15 三锚行在 before 与 after SUT **各恰 1 次**，且 after 行文本 == before 行文本（byte-identical） | 变异机关未被修法破坏（「re-read anchor tests after fix」的静态半） |
| **MUT-A2** | `TRUSTED_CLOCKS` 定义恰一次；`sorted(TRUSTED_CLOCKS)` 位恰一次；`BASIS_REGISTRY` tuple 形态恰一次（T1-10-FIX 前置层未回退） | 全部 =1 |
| **MUT-A3** | **20 臂 `mutate.r2.py` 整跑**（before 树与 after 树各一轮） | mutation_count=20、all_mutants_red_again、all_expected_cases_red 两树均 true，且逐臂 `cases_red` 列表 **before==after**（MUT-7→C5、MUT-15→X1–X4；动态半=锚语义复读） |

## 7. 冻结负控（light，T1-8/T1-FIX 式：毒化声明 ⇒ runner **不得**绿；raw 全落盘）

参照：T1-8 `a20260920-03` 毒化 11 声明仍 rc=0/11-11 绿 = **伪造的绿**；本面方向必须相反。

| 臂 | 毒化 | 期望（**不得变绿**） |
|---|---|---|
| **PC 正对照** | 无 | runner **rc=0、ok=true、mismatch=0**（负控非永红） |
| **NC-1 输入侧（≥1 clock_source + ≥1 claim.status 载荷）** | cases 副本：**C3.clock_source → `["system_utc"]`**（clock 声明 accept 将被 J7 拒翻转）+ **C2.claim → `["pending"]`**（status 载荷 accept 将被 fail-closed 拒翻转） | SUT **rc=0、34/34 全裁决**（机关未被毒化炸毁——before 树同毒化=rc4 全灭，即修复承重）；runner **rc=1、ok=false**、mismatch 含 {C3, C2}、gate 内嵌 cases_sha256 ≠ 冻结 pin ⇒ **非绿**（双向可检：判决通道 + sha 通道） |
| **NC-2 声明侧（≥1 clock_source + ≥1 claim.status 声明）** | expectations 副本：**C5（clock case）verdict→accept/refusals→[]** + **C4（claim.status case）verdict→accept/refusals→[]** | runner **rc=1、ok=false**、mismatch ≥4 行、含 {C5, C4} ⇒ **非绿**（与 T1-8 毒化仍绿**方向相反**） |

## 8. 冻结回归/继承面（before == after == 绿；family run）

| 面 | 命令载体 | 冻结判据 |
|---|---|---|
| r1 族套件（含 **J7/calendar 锚测试** `test_simulated_clock_cannot_complete_a_window`、C1–C7） | `pytest harness/tests/test_i14b_natural_window.py` | before==after：failed=0、passed 相等（T1-10-FIX 实测 32，实测数如实记录） |
| r2 族套件 | `pytest harness/tests/test_i14b_natural_window_r2.py` | before==after：failed=0、passed 相等（18） |
| **T1-10-FIX 新 23 测试套件**（basis 家族，继承） | `pytest harness/tests/test_i14b_natural_window_basis_total.py`（I14B_SUT=各树 SUT） | before==after：**23 passed / 0 failed** |
| **T1-10-FIX 探针 39 检查**（继承，其脚本逐字复制到 `scripts/inherit_probe_t1_10_fix.py`，sha 与原件相等） | `probe --phase after --sut <before|after SUT>`（其配对守卫 = sha≠r2 基线，两树均满足） | **39/39 PASS 两树各一轮**；其 adjacent 行如实记录（before：rc4/rc4/rc4 → after：**rc0/rc0/rc4**，rc4=F-3 pending） |
| r2 冻结门 | `run_cases --cases cases.r2.json --expectations frozen_expectations.r2.json` | before==after：rc=0、ok、mismatch=0、34/34 |
| r1 门（既有 superseded 差） | `run_cases --cases cases.json …` | before==after **字段相等**（W1 union 2220 superseded 为既有态，不判绿——与 T1-10-FIX 同口径） |
| 20 臂变异机关 | `harness/mutate.r2.py --out …` | 见 §6 MUT-A3 |

## 9. 边界与不自签

源树 **READ-ONLY**；交付 **changes.diff only**（左侧=064e5381…）；无 git、无删除、无状态迁移、无签名、无晋升；
oracle（I-14-B）与本文件运行后**一字不改**；F-1/F-2 处置 = **FIXED-pending-review**（本卡不自签、不收口）；
F-3 = **inherited-pending-ruling**；P4 已登记未复测容器族 = **inherited-not-in-scope**（移交续修卡）。

---

# APPENDIX（**追加式扩围** · 2026-09-23 · 仍先于任何探针运行；上文 §1–§9 字节未动）

**追加依据（父方扩围令，逐字要点）**：「T1-10-FIX 复审已 ACCEPT + F-3 已裁 → 你的 T1-F2-FIX scope 追加
**P4 容器族**（复审活测同机制 rc4、建议并入本卡、父裁采纳）：①`windows` dict 容器 → rc4 `string indices…`；
②`sampled_at` dict 容器 → rc4 `Invalid isoformat 'a'`；③`ledger.daily` dict 容器 → rc4 `string indices…`
（基线同值实测于 T1-10-FIX 修复后树）……不变量加一条=时间戳类畸形**不归你**……**合并序更新**：
T1-10-FIX(`625ecfe4`) first → 你(基于其 fixed iso `064e5381`) second → T1-F3-FIX third……oracle 若已冻则按
追加文 (APPEND) 补 P4 三落点+批负控（append-only 注记）」。随后父方一句确认：
「**P4 evidence-degraded 模式照准，APPEND 补文入册即冻**」+ 下述两条必载不变量（§A.3/§A.5）。
发信方 = `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`；逐字件录于 `binding.json.parent_expansion_order`。

**取代注记（append-only）**：§9 末行「P4 已登记未复测容器族 = inherited-not-in-scope」自本追加起
**被本节取代**（P4 三落点扩围入本卡）；原句按追加式纪律**保留为冻结前像**，不就地抹除。
**合并序（三层版，取代上文两层序）**：T1-10-FIX `625ecfe4…` **first** → 本卡（左基 = 其 fixed iso `064e5381…`）
**second** → **T1-F3-FIX third**（其 scope = `_parse` 时间戳区 `:82-88`）。本卡三处 hunk 区间
（F-1 ≈`:50-59`、F-2 ≈`:357-362`、P4 ≈`:441-445`）与 `_parse :82-88` **行不交**（生成后实测登记于 decision.md）。

## A.1 P4 三落点行级表（before 树 = T1-10-FIX 修复后文件行号；RED raw = 父方引述的复审活测值，本卡 RED 复测）

| id | 落点 | 读点行 | RED raw（复审实测/本卡复测） |
|---|---|---|---|
| **P4-①** | `windows` 载体为 **dict** | `_all_timestamps :126-128` + `derive_window :163-166`（2 读点） | rc=4、无报告、0 裁决、`TypeError: string indices must be integers` |
| **P4-②** | `sampled_at` 载体为 **dict** | `_all_timestamps :124` + `derive_window :145`（2 读点） | rc=4、`ValueError: Invalid isoformat string: 'a'`（dict 迭代出键串进 `_parse`——**载体形态所致**，非时间戳串本身畸形） |
| **P4-③** | `ledger.daily` 载体为 **dict** | `derive_calendar :315`；同族并列读点 `weekly :333` / `monthly :345` / `alerts :351`（ledger 1+4 读点） | rc=4、`TypeError: string indices must be integers`（alerts 形态为 `'str' object has no attribute 'get'`） |

**修法（父方照准的 evidence-degraded 模式 + 单点入口归一）**：在 `classify()` 取得 `fields` 之后**单点**插入
归一守卫（isinstance 模式，同 T1-10-FIX E1 模板的「入口验证」）：present-but-not-list 的 `windows`/`sampled_at`
→ `[]`；present-but-not-dict 的 `ledger` → `{}`；ledger 内 present-but-not-list 的
`daily/weekly/monthly/alerts` → `[]`（**键缺失一律不动**，保证正常路径字节同）。
**单点覆盖 2+2+4 共 8 个读取落点** = 结构上满足「全部入口」标准（T1-10-FIX MUT-G4 教训：只补一处 ≠ 全部入口）；
逐落点的 RED/GREEN 探针与 MUT 回退见 §A.2/§A.4。**③ 的范围披露**：`ledger.daily` 与
`weekly/monthly/alerts` 是同一 statement 组内**同形状并列读点**（复审只点名 daily）——一并归一，
否则留下三个同机制 rc4 兄弟 = 「补一处漏三处」；此扩同族披露于 decision.md。

## A.2 P4 探针族与期望（RED=before=064e5381…；GREEN=after；与 §2 同表纪律）

事实族沿 §2 的 F-C2/F-C3 与窗口 GOOD_FIELDS；**武器化探针（父方不变量 2，raw 必入 evidence）**标 ★。

| id | 形状（tamper 仅动该载体） | RED 期望（before） | GREEN 期望（after） |
|---|---|---|---|
| **P4-W1** | 窗口 facts=GOOD_FIELDS、`windows={"w1":{…}}`（dict）、claim=union **1740**（如实） | **rc=4、0 裁决、`string indices must be integers`**；direct `TypeError` | rc=0、**accept**（回退 obs_finished 证据派生区间；见 §A.3 安全论证——降级只降不升，如实主张仍被支持） |
| **P4-W2 ★** | 同 W1 但 claim=union **2220**（超主张武器化） | 同上崩 | rc=0、`reject`+**`["R-CLAIM-EXCEEDS"]`**（武器化仍被拒=J11 承重） |
| **P4-S1 ★** | `sampled_at={"a":"…Z"}`（dict）、其余 GOOD、claim=union 1740 | **rc=4、`Invalid isoformat string: 'a'`** | rc=0、`reject`+**`["R-NO-SAMPLES"]`**（键在且窗内样本<2 ⇒ J4 既有码；武器化仍走保守路） |
| **P4-L1 ★** | F-C3 facts 但 `ledger.daily`→dict、claim=`{"status":"complete"}` | **rc=4、`string indices must be integers`** | rc=0、`reject`+**`["R-CLAIM-EXCEEDS"]`**（计数归 0 ⇒ pending ⇒ J11 既有码；武器化仍被拒） |
| **P4-L2**（对照） | F-C2 facts 但 `ledger.daily`→dict、claim=`{"status":"pending"}` | rc=4 崩（同 L1 机制） | rc=0、**accept**（主张未超降级后事实；缺证据不造罪名也不放行超主张） |
| **P4-STAB-W** | `windows=[{window_id,…},…]` 正常列表（W5 形：union 2400） | rc=0 accept | **行字节相同** |
| **P4-STAB-S** | `sampled_at` 正常 30 串 | rc=0（W1 族原样） | **行字节相同** |
| **P4-STAB-L** | ledger 正常 dict（C1/C2/C3 原样 = S9/S10 已含） | rc=0 | **行字节相同** |
| **PT-1**（**pending-routed，不判**） | `started_at="not-a-timestamp"`（时间戳串畸形） | rc=4 `Invalid isoformat …` | **after 同 rc=4 —— 记录为 pending-routed → T1-F3-FIX，不入 PASS/FAIL、不自修不判合规性** |
| **PT-2**（**pending-routed，不判**） | `sampled_at=["not-a-timestamp"]`（**列表载体 + 坏时间戳串**） | rc=4 | **同 PT-1：时间戳形状归 T1-F3-FIX（载体是 list，不触发本卡归一守卫；分界=载体形态 vs 串内容）** |

**P4 批/臂（负控，照 F-1/F-2 同标准）**：

| id | 批内容 | RED 期望 | GREEN 期望 |
|---|---|---|---|
| **J2**（P4 批） | [P4-W2, P4-S1, **C3-GOOD**, P4-L1, **W1-GOOD**] = 5 | **rc=4、0/5、raw=首毒形状错误** | rc=0、**5/5 裁决**、拒={P4-W2 `R-CLAIM-EXCEEDS`, P4-S1 `R-NO-SAMPLES`, P4-L1 `R-CLAIM-EXCEEDS`}、{C3-GOOD, W1-GOOD} accept ⇒ **only-BAD rejected** |
| **J3**（四族联合） | [W1-GOOD, C3-GOOD, C2-GOOD, BAD-F1, BAD-F2, P4-W2, P4-S1, P4-L1] = 8 | **rc=4、0/8** | rc=0、**8/8**、仅 5 个 BAD 被拒、3 个 GOOD accept |
| **Arm-D**（P4 隔离） | 6× W1-GOOD + 1× P4-S1（仅 sampled_at 不同） | **rc=4、0/7** | rc=0、7/7、**仅 P4-S1 被拒** `R-NO-SAMPLES` |

## A.3 不变量 I-8（父方原文必载，逐字）——windows 归一空的安全论证

> **畸形 windows 归一 []/{} → 回退 obs_finished 证据派生区间——畸形 windows 在任何情形下不得比证据派生默认
> 更宽地扩大可接受区间（只降不升=攻击者控制值永不进计算）**

配套冻结推论：归一路径产生的 union/sum/overlap **只由证据派生默认（obs_finished 区间/样本）决定**，
容器内任何攻击者控制值**永不进入计算**；故 degrade 只会**降低**可被主张支撑的上限，超主张必撞既有
`R-CLAIM-EXCEEDS`（P4-W2 ★ 即其可判定证明）。批 BAD 用**超主张变体**（only-BAD rejected 证门仍承重）。

## A.4 MUTATION 臂追加

| 臂 | 变异 | 期望 |
|---|---|---|
| **MUT-P4** | 回退 `classify()` 入口归一守卫块（还原为 `fields = dict(case.get("fields") or {})` + 原样透传） | **三形状逐落点崩溃回归**：P4-W2 rc=4 `string indices`、P4-S1 rc=4 `Invalid isoformat 'a'`、P4-L1 rc=4 `string indices`（均无报告、0 裁决）⇒ 守卫承重、非空洞 |

## A.5 不变量 I-9（父方必载第 2 条）——每落点反武器化负探针

每个载体的 degrade 路径各配一个「**武器化尝试必须仍被拒/仍走保守路**」探针，raw 全入 evidence：
**windows-BAD 超主张 → `R-CLAIM-EXCEEDS`（P4-W2 ★）**、**sampled_at 畸形 → `R-NO-SAMPLES`（P4-S1 ★）**、
**ledger 畸形 + complete 主张 → J11 `R-CLAIM-EXCEEDS`（P4-L1 ★）**。三探针的 RED raw 与 GREEN raw
分别落 `evidence/before/probes/raw/` 与 `evidence/after/probes/raw/`，并在 decision.md 逐条点名。

## A.6 不变量 I-10（时间戳类 = pending-routed，不归本卡）

时间戳串内容畸形（`_parse` 抛 `Invalid isoformat`，含 PT-1/PT-2）= **F-3 已裁后由 T1-F3-FIX 独立修轨**
（`R-TIMESTAMP-MALFORMED`/rc 归属随其 §11.8 追加文，父方引其复审报告 §7.3 为载体；本卡不复述其内容、不自填）。
本卡承诺：(a) hunks ∩ `_parse :82-88` = ∅；(b) PT-1/PT-2 只记录 pending-routed、**不入 PASS/FAIL**；
(c) 本卡不引入 `R-TIMESTAMP-MALFORMED`、不改任何时间戳解析路径（词表不变量 I-2 继续成立）。
**注意**：P4-② 的 RED 形态虽以 `Invalid isoformat 'a'` 为 raw，其根因是 **dict 载体迭代出键串**（载体形态缺陷）
⇒ 归本卡；分界判据 = **载体形态（本卡）vs 列表内串内容（T1-F3-FIX）**，PT-2 即该分界的可判定对照。

## A.7 负控与回归面的追加冻结

- 负控 §7 不变（PC/NC-1/NC-2 照旧）；P4 的「批负控」= §A.2 的 J2/J3/Arm-D（同 F-1/F-2 标准），
  加上 §A.5 三武器化探针 raw。
- 回归面 §8 不变（r1/r2/23 测试/39 探针/r2 门/20 臂）——P4 归一守卫不得改变其中任何一值（I-1 继续涵盖：
  正常 list/dict 载体全部走原路径）。
- 前置层不变量 I-6 继续成立；本节新增 pin：T1-10-FIX 复审 ACCEPT 载体与 F-3 裁定载体（见 binding.json
  扩围引证；盘上文件若在本 attempt 期间落成，补记 sha 于 decision.md「关键指纹」——只增不改）。
