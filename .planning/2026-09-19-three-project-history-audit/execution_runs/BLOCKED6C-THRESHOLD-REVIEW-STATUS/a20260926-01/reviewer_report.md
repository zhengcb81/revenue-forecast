# 独立复审报告 — `BLOCKED6C-THRESHOLD-REVIEW-STATUS / a20260926-01`

VERDICT: ACCEPT

被审对象：本 attempt 的**实现者交付**（`oracle.md` 27,126 B / `handoff.json` 30,842 B /
`changes.diff` 15,892 B / `final_verification.json` / `red/` `green/` `l271/` `mut/` `iso/` `iso_patched/` `tools/`）。
复审位与实现者**不是同一人**；本报告**只写复审结论，不写卡状态**，不代其落定、不解除 `BLOCKED-6b`/`OPEN-6`、
不放行任何阈值或参数、不产生 `I-11-B`/`I-11-C` 的 ACCEPT。

**一句话结论**：六项复核**全部实测通过**（红 4/4 放行 · 绿 4/4 拒 + 25/25 · **21 例回归 21/21 未破** ·
**5 变异逐条 rc=1 按预登记翻红** · `L271` 两个计数与 T1/T2/T3 我独立复算完全一致 · `changes.diff` 我独立重算
**字节相同** `+207/−0/7 hunks/1 文件` 纯新增）；两道 fail-closed **均未触发**。
我**裁定采用 U-PRIMARY 主读法**（依据见 §3），故 `trigger_fired=false` 成立、**不建议改判 `blocked`**。
无 P1；记 **2×P2 + 3×P3**。

---

## 0. 复审身份、纪律与写入面

| 项 | 本复审的实际情况 |
|---|---|
| 写入面 | 仅本 attempt 内**两个新建文件**：`reviewer_report.md` + `reviewer_report.sha256`；**本 attempt 既有字节一字未动** |
| 测试位置 | 全部在 `%TEMP%\dsh-Mjicmt\b6c_rev_a20260926\`（把本 attempt 整目录复制过去后运行），**不在生产树跑** |
| 生产树 | **只读**；封盘 `I-11-A/a20260919-01`、两半区裁定、容差裁定、6 份语料全部只读打开 |
| git | 只用 `git -c core.quotepath=false diff HEAD --name-only`（只读）；**未用 `git status`**、**无 git 写** |
| 网络 | **未使用** |
| 环境 | `C:\Miniconda\python.exe` 3.13.9，一律 `-X utf8 -B`（**attempt 内 `__pycache__` 计数 = 0**，已实测） |
| 卡状态 | `handoff.json`（`status=review_pending`、`implementer_signed=false`、`releases_nothing=true`）**原样未改** |

**本 attempt 既有字节复验（复审结束前实测）**：

| 文件 | 字节 | sha256（前 16） | 与 `handoff.deliverables` 是否一致 |
|---|---|---|---|
| `oracle.md` | 27,126 | `6d86f27111f9a121` | ✅ |
| `changes.diff` | 15,892 | `b2ec16ffe1e8f32b` | ✅ |
| `handoff.json` | 30,842 | `88c39b95e0afa99f` | ✅ |
| `final_verification.json` | 12,498 | `5390f9155cf3026a` | ✅（handoff 之外的最后一件，自身不入表） |
| `iso/tools/validate_hypotheses.py`（前像） | 28,549 | `cb49360d15bc044d` | ✅ |
| `iso_patched/tools/validate_hypotheses.py`（后像） | 39,435 | `1085368e3d05cf9b` | ✅ |

⇒ `handoff.deliverables` **36/36 逐件 sha+字节全等**；`handoff.sealed_inputs_reverified` **14/14 全等**（我落盘复算，0 不符）。
`git diff HEAD --name-only` 总数 **3830**、**非 `.planning` = 0**（本复审实测）。
编码实测：`oracle.md`/`changes.diff`/`handoff.json`/`final_verification.json` **UTF-8 无 BOM、`CRLF=0`**。

---

## 1. 回源读（我读的是原文，不采信转述）

| 回源点 | 我读到的原文位置与要点 | 结论 |
|---|---|---|
| `I11A-OPEN-ACCT/a20260924-01/ruling.md`（37,355 B，sha `f3040df0…`，与 oracle §1 登记**全等**） | **L226** 裁定一句话：凡被下游消费的阈值必须带 `threshold_basis` **且**显式 `threshold_review_status`（默认 `not_reviewed`），且**禁令子句自带范围**（`basis=professional_judgement_required` **且** `status≠reviewed` ⇒ 不得触发自动动作）· **L230–L232** A-6.1 四条（fail-closed 是「阈值不参与判定，命题仍可登记观察」，**不是命题作废**）· **L271** 位于 **`#### 反例（什么会推翻本裁定）`** 段（该段首行 = L268）下的**第 2 条** · **L276–L278** 兼容影响，**L278 明令**「若在 I-11-A 侧补该检查，属**新规则**，须按 `DEC-14` 流程**补反例并重跑 21 例计数** —— 该改动属 I-11-A 卡的实现者/编排层，**我只提出要求，不代改**」 · **L298** `BLOCKED-6c` 定义 · **L324** 受理人 = **编排层 / schema owner** | 与派单一致 |
| `OWNER_DECISIONS.md §二十七`（90,624 B，sha `4fe79ba5…` = oracle §1 登记值，**未漂移**） | 三票 = G2/G3 取证授权 · origin 字节落点 · 环境能力；**三票 = 三个许可，不是三个结论** | 已读 |
| ⚠️ `DEC-14` 的真实出处 | **`OWNER_DECISIONS.md` 全文无 `DEC-14` 字样（grep 0 命中）**；`DEC-14` 原文在 `I-11-A/a20260919-01/decision.md` **L345–L369**（sha `e9c96f02…` 与登记全等）：选 (b)「补检查 + 把新增变异固化为反例 + **显式声明仍不完备**」；**L367 恢复规则**「校验器规则变更必须**重跑全部反例并重新计数**；不允许只跑正例」；L364「新增错误码必须同步进 oracle 的 R2 表」 | 派单把 §二十七 当 `DEC-14` 语境属**转述漂移**（父侧同族错误）；`DEC-14` 我按 `decision.md` 原文读，**本卡 §7 的五条合规逐条对得上** |
| 同形先例 `I11A-OPEN12-VALIDATOR-COMPLETENESS/a20260925-01/` | `oracle.md` 16,328 B · `changes.diff` 12,113 B · `run_mutations.py` · `reviewer_report.md` 25,046 B + `reviewer_report.sha256` 85 B · 其 verdict = `ACCEPT` | 本卡形态（校验器改动 + `changes.diff` + 红绿变异 + 不写真仓）与先例**同形**，判定口径沿用 |
| `REMEDIATION_REGISTER.md §一四三`（L3249–L3276） | **B 段第 2 条逐字**：「L271 是**『反例』段的第 2 条**…其语义是『**若实现后出现大批阈值判不可用，才需重议**』—— **字段尚未实现、无从触发。把反例当成了前置条件，属误读**」；L3271「本节原结论『可派但刻意未派』**已作废**」；L3557 再次记「**L271 是反例不是前置**」 | 与我 §3 的裁定同向 |
| 本卡 `oracle.md` §3.2 `B6C-G4` · §5 变异预期 · §6.1 冻结 6 语料 · §6.2 手算 · §3.3 双读法分工 | 见 §2 各项 | 全部实测比对 |

---

## 2. 六项复核表（**全部为我自己跑出来的 raw 值**，不引用实现者自述作证据）

| # | 项 | 实现者声称 | **我的实测** | 判 |
|---|---|---|---|---|
| 1 | **红**：原校验器对 CE-22..25 | 4/4 放行、rc=1 | **rc=1**；`rejected=False` ×4、`observed_codes=[]` ×4；正例 `pass(0 errors)`；原 21 例 `original_21_rejected=21 / accepted_by_mistake=0`；单独跑校验器 main **rc=0**、`counterexample_summary={21,21,0}` | ✅ |
| 2 | **绿**：补丁版 | 正例 0 错、CE 4/4 拒、`{25,25,0}`、`{not_reviewed:8}`、`limitations` 在场 | **rc_cases=0 / rc_main=0**；正例 `pass(0 errors)`；CE **4/4 拒且期望码逐一命中**（各自只出期望那一个码）；`counterexample_summary={cases:25, rejected_as_expected:25, accepted_by_mistake:0}`；`counts.threshold_review_statuses={not_reviewed:8}`、`defaulted=8`、`reviewability_unusable=3`、`summary={records:8, usable:5, unusable:3, unusable_reasons:{judgement_not_reviewed:3}}`；`threshold_review_status_schema.limitations` **在场** | ✅ |
| 3 | ⭐ **21 例回归（`DEC-14`/L278 明令）** | `21/21`、`accepted_ids=[]` | **未变异补丁版上 `original_21_total=21 / rejected=21 / accepted_ids=[]`**、`new_b6c_rejected=4`、套件 `25/25` | ✅ **回归未破** |
| 4 | **变异 M1–M5** | 5/5 rc=1 | 见下表，**逐条 rc 我自己记录** | ✅ |
| 5 | ⭐ **`L271` 双读法量化** | 见 §2.5 | 我**自己重跑 + 自己另写一套脚本独立复算**，两路完全一致 | ✅ |
| 6 | **`changes.diff` 判定** | 15,892 B / `b2ec16ff…` / 1 文件 / `+207/−0/7 hunks` 纯新增 | 见 §2.6，**字节级独立重算相同** | ✅ |

### 2.1 红（J1）— 我自己跑

```
python -X utf8 -B tools/run_cases.py --validator iso/tools/validate_hypotheses.py --attempt iso ...
rc = 1
  CE-22  expect=E_THRESHOLD_REVIEW_STATUS_UNKNOWN        rejected=False observed=-
  CE-23  expect=E_THRESHOLD_REVIEW_STATUS_UNSEALED       rejected=False observed=-
  CE-24  expect=E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED   rejected=False observed=-
  CE-25  expect=E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED   rejected=False observed=-
  CE summary: 0/4 rejected (accepted=['CE-22','CE-23','CE-24','CE-25'])
  target suite: total=21 original_21_rejected=21 new_b6c_rejected=0 rejected_as_expected=21 accepted_by_mistake=0
  positive_case: pass (0 errors)

python -X utf8 -B iso/tools/validate_hypotheses.py iso ...   rc = 0
  {"accepted_by_mistake": 0, "cases": 21, "rejected_as_expected": 21}
```
⇒ `observed` **空**（新键从未被读取），**红成立**；同一份前像 sha = `cb49360d15bc044d…`（28,549 B）与封盘件**逐字节相同**（我另比 `sealed == iso` → `True`）。
我的 `red_cases_report.json` 与归档 `red/ce22_ce25_report.json` 除 `phase/validator/attempt` 三个运行期字段外**逐字段相等**（`==` → `True`）。

### 2.2 绿（J1/J3）— 我自己跑

```
python -X utf8 -B tools/run_cases.py --validator iso_patched/tools/validate_hypotheses.py --attempt iso_patched ...   rc = 0
  CE-22/23/24/25 rejected=True，observed 各自 == 期望码（单码，无第三方码干扰）
  CE summary: 4/4 rejected (accepted=[])
  target suite: total=25 original_21_rejected=21 new_b6c_rejected=4 rejected_as_expected=25 accepted_by_mistake=0
  positive_case: pass (0 errors)

python -X utf8 -B iso_patched/tools/validate_hypotheses.py iso_patched ...   rc = 0
  counterexample_summary = {"cases":25, "rejected_as_expected":25, "accepted_by_mistake":0}
  counts.threshold_review_statuses = {"not_reviewed": 8}
  threshold_review_status_schema.limitations = "DEC-14: adding these checks and this counterexample suite is NOT a completeness proof. …"
```
⇒ 我跑出的 `green_validation_report.json` 与归档 `green/validation_report.json` **`json` 全等（`True`）**；`green/cases_report.json` 同样**全等（`True`）**。

### 2.3 ⭐ 21 例回归（`DEC-14` / ruling L278 明令的那一条）

- **未变异补丁版**：`original_21_total = 21`、`original_21_rejected = 21`、`original_21_accepted_ids = []`、
  `new_b6c_rejected = 4`、`accepted_by_mistake = 0`、正例 `pass`。
- 交叉验证：`validate()` main 的 `counterexample_summary = {25, 25, 0}`（原 21 + 新 4 已按 `DEC-14` **重新计数**，不是只跑正例）。
- 观察到的**良性副作用**（如实登记，非缺陷）：原套件里两条 `E_STATE_APPROVED_BY_IMPLEMENTER` 反例在补丁版上 `observed_codes`
  **额外多出** `E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED`（它们把 `state` 改成 `approved_frozen`，因而同时命中 `B6C-G3`）；
  二者**仍由其期望码拒绝**，计数不受影响。
⇒ **回归未破，`DEC-14` 合规。**

### 2.4 变异 5 条（J2）— 逐条 rc 我自己记录

`make_mutants.py` 在 **%TEMP% 副本内**重跑，5 个变异体 sha256 与 `handoff.deliverables` 登记值**逐一相同**
（`M1 66124dd1…`、`M2 dd0c0fef…`、`M3 c4590217…`、`M4 f69392d1…`、`M5 929a4528…`）。

| # | 变异（我复核了变异体源码） | **我的 rc** | **我实测翻转** | 与 oracle §5 预登记 | 正例 | 原 21 |
|---|---|---|---|---|---|---|
| **M1** | `DEFAULT_THRESHOLD_REVIEW_STATUS = "reviewed"`（默认值翻面） | **1** | `CE-24` 拒→**放行**（`OWN-24` 同步放行）；`CE-25` **仍拒**（显式 `not_reviewed` 不受默认值影响） | ✅ 只列 `CE-24` | `pass` | **21** |
| **M2** | 整块删除 `<B6C-G3>`（`not_reviewed` fail-closed 分支） | **1** | `CE-24`、`CE-25` **同时放行**（`OWN-24`/`OWN-25`） | ✅ | `pass` | **21** |
| **M3** | 删除**既有** `E_THRESHOLD_BASIS_UNKNOWN` 闭集块 | **1** | CE-22..25 **4/4 仍拒**；**`OWN-21`（`threshold_basis="made_up_basis"`）放行** | ✅（含预登记的原 21→20） | `pass` | **20** |
| **M4** | 删除 `B6C-G1` 判定（保留共享 `_trs_*` 赋值） | **1** | `CE-22` 放行（`OWN-22`） | ✅ | `pass` | **21** |
| **M5** | 删除 `B6C-G2` 封缄判定 | **1** | `CE-23` 放行（`OWN-23`） | ✅ | `pass` | **21** |

**我对 M3 口径的独立判断（派单要求我自己裁）—— 该口径成立**，理由四条：
1. **`J3` 的判定对象在 oracle §2 就被冻结为「未变异的补丁版」**：`J3` 全文是「补丁版上正例 pass **且原 21 例逐条仍 rejected**」，
   `oracle §5` 更明写「M3 的特殊预期（预登记）…**不算 J3 的 21 例回归失败**（J3 只在未变异的补丁版上判定）」。
   ⇒ 21→20 只可能出现在变异体上，它**在定义域之外**。
2. **M3 打掉的是补丁前就存在的判据**，`replace_once` 要求锚文本 `count == 1` 否则中止 —— 该次运行**成功**，
   这本身就**反向证明**补丁没有动过 `E_THRESHOLD_BASIS_UNKNOWN` 那一段的字节（与 §2.6 的「纯新增」互相印证）。
3. **M3 下 4 条新反例仍 4/4 拒** ⇒ 变异没有混淆「新判据是否承重」这一命题，`J2` 的判别力读数干净。
4. **失败方向正确**：M3 正是用来证明既有 `threshold_basis` 闭集是**承重**的；它把唯一依赖该闭集的 `OWN-21` 放行 ⇒ **承重性被证实**。

### 2.5 ⭐ `L271` 双读法量化 —— 我**自己重跑** + **自己另写脚本独立复算**

**(a) 重跑实现者的 monitor（只读打开 6 份语料，`rc=0`）**，输出与归档 `l271/l271_report.json`
**字节级相同**（13,461 B、sha `0b19ce662d758a63bd9e50c7ecbe2d40ad79da184cbbf7648e48f08a13926fac`，两侧一致）：

```
corpus sha256 all match: True
record level   N=40 U=14 (35.0%) U_newly=2 A62_usable=28
distinct level N=8  U=4  (50.0%) U_newly=1 A62_usable=5
U-LITERAL      record 40/40  distinct 8/8
T1 v1 usable=5 ar=4 dj=1 blocked=False | literal usable=0 ar=0 dj=0 blocked=True
T1 v2 usable=4 ar=3 dj=1 blocked=False | literal usable=0 ar=0 dj=0 blocked=True
T1 v3 usable=5 ar=4 dj=1 blocked=False | literal usable=0 ar=0 dj=0 blocked=True
T1 v4 usable=4 ar=3 dj=1 blocked=False | literal usable=0 ar=0 dj=0 blocked=True
T2 record hit=False ({'U': 14, 'N': 40, 'pct': 35.0, 'threshold_U_min': 30}) distinct hit=False ({'U': 4, 'N': 8, 'pct': 50.0, 'threshold_U_min': 6})
T3 record hit=False ({'U_newly': 2, 'A62_usable': 28, 'threshold_U_newly_min': 14.0}) distinct hit=False ({'U_newly': 1, 'A62_usable': 5, 'threshold_U_newly_min': 2.5})
L271_trigger_fired=False  literal_A61=True
```

**(b) 我自己另写的一套独立复算**（**不用**他们的 `l271_monitor.py`，直接按 oracle §3.3 的五条规则 + §6.1 语料重打）：

| 项 | 实现者 `l271_report.json` | **我的独立复算** | 一致 |
|---|---|---|---|
| 记录级 `N` | 40 | **40**（8+8+8+8+4+4） | ✅ |
| 记录级 `U`（U-PRIMARY 并集） | 14 (35.0%) | **14 (35.0%)**，`reasons = {judgement_not_reviewed:12, approved_without_review:2}` | ✅ |
| 记录级 `A62_usable` / `U_newly` | 28 / 2 | **28 / 2** | ✅ |
| 去重底层 `N` / `U` | 8 / 4 (50.0%) | **8 / 4 (50.0%)**（8 个 id：`H-CN-ZIJIN-SEG-01/02/VOL-03/PLAN-04/ELIM-05`、`H-US-MSFT-SEG-01/02/03`） | ✅ |
| 去重 `A62_usable` / `U_newly` | 5 / 1 | **5 / 1**（`H-CN-ZIJIN-SEG-01`） | ✅ |
| **T1** 四份 `usable/arith/disc` | 5/4/1、4/3/1、5/4/1、4/3/1 → **全 `blocked=False`** | **完全相同** → 全不命中 | ✅ |
| **T2** | 记录 `14 ≥ 30?` → **False**；去重 `4 ≥ 6?` → **False** | **相同** | ✅ |
| **T3** | 记录 `2 ≥ 14?` → **False**；去重 `1 ≥ 2.5?` → **False** | **相同** | ✅ |
| **U-LITERAL** | 记录 **40/40**、去重 **8/8**；T1 四份全 0 → `blocked=True`；T2/T3 **全命中** | **相同** | ✅ |
| **`trigger_fired`** | **false**（主） / **true**（字面） | **false**（主） / **true**（字面） | ✅ |
| 6 份语料 sha | 全 match | 我另测前 16 位：`f217876804c96335` `32c22208573a71d5` `b2063ac8533a96ba` `ebf6fa4e2f708c39` `1da977bfe05e2354` `3ad403ba75cf545721` → **与 oracle §1 逐条相同** | ✅ |
| 语料是否已携带该字段 | 0 | 我的脚本对**任一**记录含 `threshold_review_status` 会直接 `SystemExit` —— **未触发** ⇒ 确为 **0** | ✅ |

⇒ **记录级 40 / 去重级 8 两个计数、以及 T1/T2/T3，我全部独立复算通过。**

### 2.6 `changes.diff` 判定 —— 我自己重算

```
stored: 15,892 B  sha256=b2ec16ffe1e8f32b01831eb2941e7c99347ac8379ccc3d6a208c9e55a58ef21a  （实测）
我用 difflib.unified_diff(iso/, iso_patched/, n=3, 同样的 fromfile/tofile) 重打 →
  body 与归档 body 逐字节相同 : True
  hunks    = 7        （登记 7 ✅）
  additions= 207      （登记 207 ✅）
  deletions= 0        （登记 0 ✅，纯新增、无删除弱化）
  +++ 行数 = 1        （1 个文件 ✅，只有 iso_patched/tools/validate_hypotheses.py）
  hypotheses.json 出现在 diff 正文 : False   （追加式 schema，不在 diff 内 ✅）
  归档正文 CRLF = 0、BOM = False
前像核对: iso/tools/validate_hypotheses.py == 封盘 I-11-A/.../validate_hypotheses.py → True（28,549 B / cb49360d15bc044d…）
纯新增证明: 前像 504 行**按序全部**出现在后像中 → True (504/504)
既有谓词计数（前像 → 后像）: FALSIFIER_KEYS 2→2 · THRESHOLD_BASES = 1→1 · E_THRESHOLD_BASIS_UNKNOWN 2→2  （原字节未动 ✅）
  （IMPLEMENTER_MARKERS 2→3：**新增了一处调用** `review_seal_ok()`，定义本身未改，且表达式与原 L297 逐字同形）
```
⇒ **15,892 B / `b2ec16ffe1e8f32b…` / 1 文件 / `+207 / −0 / 7 hunks` / 纯新增 / `hypotheses.json` 不在 diff 内 / `FALSIFIER_KEYS`·`THRESHOLD_BASES`·R2 五条原字节未动 —— 六项全部复算通过。**
⇒ **`changes.diff` 未入库不是缺陷**（本卡本来就只出 diff、不改真仓）。

---

## 3. ⭐ 双读法裁定（派单交我裁，实现者未静默选边）

### 3.1 结论

> **我裁定采用 `U-PRIMARY`（oracle §3.3 冻结的主读法）作为判定本卡 J4 / `L271` 触发线的唯一读法。**
> 依据 U-PRIMARY：`T1/T2/T3` **全部不命中** ⇒ `trigger_fired = false` ⇒ **fail-closed 第 1 条未触发 ⇒ 不判 `blocked`**。
> `U-LITERAL` 的量化（40/40、8/8、三线全中）**照实保留**为反事实披露，**不作判据**。
> **若采字面读法 ⇒ 三线全中 ⇒ 按本卡冻结的 `J4` 应判 `blocked`。** 故本裁定是决定性的，我明确落笔、不回避。

### 3.2 逐条依据（四条正证 + 两条段落位置证）

**正证 1 —— 裁定主体的禁令子句自带范围。** ruling **L226** 是 OPEN-6 的「裁定（一句话）」，其禁令原文是
「`threshold_basis=professional_judgement_required` **且** `threshold_review_status≠reviewed` 的阈值**不得触发任何自动动作**」。
字面读法把范围词 `professional_judgement_required` 删掉，等于**改写了裁定主体的量词**。

**正证 2 —— A-6.1 的小节标题即范围。** L228 逐字「裁定 A-6.1：**占位阈值**在审定前的使用禁令」；
`decision.md DEC-6` L156–157 把**占位阈值**定义为 `threshold_basis = "professional_judgement_required"` 的那一类。
A-6.1 第 1 条是**该小节下的第 1 条**，其「二者缺一或 `not_reviewed` ⇒ fail-closed」按标题与 DEC-6 只辖占位阈值。

**正证 3 —— 字面读法会让同一条裁定的 A-6.2 成为死条文。** L236–L242 的 A-6.2 表有一列**列名就叫「审定前可否使用」**，
逐字给 `arithmetic_identity = 可用（等式判定）`、`disclosure_definition = 可用（是/否型判定）`、
`professional_judgement_required = 不可用`。
而**盘上 40 条记录 0 条携带该字段**（我已实测）⇒ 全部落默认 `not_reviewed` ⇒ 字面读法下 **40/40 全不可用**，
A-6.2 那两行「可用」**永远不可能成立**、`DEC-6` 的「两类阈值」之分也随之塌缩。
**一条裁定不会在同一节里既说「审定前可用」又说「只要没审定就一律不可用」** ⇒ 字面读法与 A-6.2 冲突，须让位于明确列举的表格。

**正证 4 —— L271 自己把「实质」与「实施方式」切开了。** L271 逐字：「⇒ A-6.1 的**实施方式**（追加字段 + 默认 `not_reviewed`）
**需按实际情况重议**，但**『未审定不得当已审定』这一实质不因此改变**。」
即：**大批判不可用 ⇒ 触发的是「重议实施方式」这个 owner 动作，不是「实现者的实现错了」**。
字面读法**恰恰会让该反例在字段落地的第一天就必然成立**（40/40 ⇒ 三线全中），
这说明字面读法不是裁定者想要的操作化方式 —— 否则他不会把它写成「什么会推翻本裁定」里的一条。

**段落位置证 1 —— L271 在 `#### 反例（什么会推翻本裁定）` 之下（该段首行 = L268，L271 是其第 2 条）。**
反例段的语义是「**若出现该现象，则本裁定的实施方式需重议**」——它是一个**带后果的触发器**，
**不是**「落地前必须先满足的前置条件」。登记册 §一四三 B.2 已明确记载父曾把它误读成前置条件并自纠
（逐字「**把反例当成了前置条件，属误读**」，L3557 再记一次）。**本次复审确认该自纠正确。**

**段落位置证 2 —— 位置差异改变了 `trigger_fired=true` 的读法。**
若 L271 是前置条件 ⇒ 触发 ⇒ 「实现者不该动手」⇒ 卡本身有问题。
若 L271 是反例（实际位置）⇒ 触发 ⇒ 「**ruling owner 要重议 A-6.1 的实施方式**」，**实质（未审定不得当已审定）继续有效**，
实现者**把该触发如实量化并上交裁定**（而不是自行判死或自行放行）**恰恰是正确处置**。
实现者在 `oracle §3.3` 明写「**此分歧由复审裁定，不由我静默选边**」，并在 `handoff.unverified` 第 2 条再次披露 —— **不静默选边成立**。

### 3.3 该裁定的边界（我同时钉死的东西）

1. **U-PRIMARY 不放松任何实质约束**：`B6C-G3` 仍拒「`state=approved_frozen` 而有效状态 ≠ `reviewed`」，
   `B6C-G2` 仍拒「自称 `reviewed` 却无 A-6.3 封缄」，`B6C-G1` 仍拒闭集外值 ⇒ 「未审定不得当已审定」**逐条落地**。
2. **U-PRIMARY 只放行「计算本身」，不放行「判定动作」**：`arithmetic_identity`/`disclosure_definition` 在 `not_reviewed` 下
   计为可用，是 A-6.2 第 1、3 行明给的「审定前＝可用」；professional 类 12/40 条**仍不可用**（与 A-6.2 一致）。
3. **本裁定只对本卡的 J4 生效**；`A-6.1` 实施方式的**最终效力**仍属 ruling owner（`I11A-OPEN-ACCT`），
   我不代裁、不回改 ruling 任何字节。
4. **若日后 owner 明文采字面读法** ⇒ 按本卡冻结 `J4` 三线全中 ⇒ 本卡应改判 `blocked` 并按 L271 重议实施方式；
   该情形**由我显式登记在此**，不由实现者承担。

---

## 4. `common_filing_cards.md` L17 适用性（oracle §0.1 明令「该判据由复审行使」）

**L17 逐字（我独立回源读到）**：「凡跨项目公共schema、canonical writer、registry或worker API，只有指定owner写；
发现scope外必要改动先记录阻断并交owner补卡，不能为绿灯建立平行框架。」

**我的裁定：L17 不适用（同意实现者 §0.1 的判断，理由为我自读原文后独立得出）**：
1. L17 的四类辖域是**跨项目公共**件；被改对象是 `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py`，
   落在 `.planning` 内、**非产品仓**（`src/`/`scripts/`/产品 `tools/` 计 0 文件，我复核 diff 头与 `git diff` 均一致）；
2. 该文件目前是 `I-11-A` **自己**的校验器；`I-11-C 是否复用同一校验器` 属 `OPEN-12`（owner 已裁「另立校验器专业卡」），
   **跨项目复用尚未发生**，故尚不存在「公共 API 由非 owner 改写」的事实；
3. 本补丁**不建平行框架**：新错误码、新报告块全部进**同一支**校验器与**同一份** `validation_report.json`；
4. 附**前置提醒（P3 级）**：一旦 `OPEN-12` 卡裁 `I-11-C` 复用本校验器，`B6C-G1..G4` 与三新错误码须按
   `A-6.3 第 5 条 / DEC-14 L364` 跨卡同步，**那时 L17 才可能被触发**；届时由 schema owner 收口。

---

## 5. 是否建议改判 `blocked`？

**不建议。** 两道 fail-closed 的实测状态：

| fail-closed | 条件（oracle 冻结） | 我的实测 | 后果 |
|---|---|---|---|
| 第 1 条 | 任一 `L271` 触发线在 **U-PRIMARY** 下命中 | **T1 不命中 / T2 记录 14<30、去重 4<6 不命中 / T3 记录 2<14、去重 1<2.5 不命中** ⇒ `trigger_fired=false` | **未触发** |
| 第 2 条 | 原 21 例在**未变异补丁版**上任一回归 | **21/21 仍拒、`accepted_ids=[]`** | **未触发** |

⇒ 按我裁定的 U-PRIMARY，**两道均未触发 ⇒ 不判 `blocked`**，本卡 `status=review_pending` + `implementer_signed=false`
的交付形态**成立**。（**若采字面读法则必须 `blocked`** —— 见 §3.1/§3.3-4，我已显式登记，不留给下一位猜。）

---

## 6. 发现分级

**P1 = 0 ⇒ `VERDICT: ACCEPT`（可带 P2/P3）。**

### P2（建议在下一张卡/追加式勘误里处置，不阻断本卡）

- **P2-1｜冻结手算 `24` vs 实测 `28` 未记 `erratum`，且 `handoff` 声称「全部匹配」。**
  `oracle §6.3` 的 T3 括注逐字「*手算预期*：2、1 ⇒ 不命中（**U-LITERAL：24、5** ⇒ 命中）」，
  而 `U_newly_literal` 实测 = **28**（记录级）/ 5（去重级）。`24` 恰等于 §6.2 自己的「24 条 arithmetic」，
  漏算了 4 条 `disclosure_definition` ⇒ **属 oracle 内部算术笔误**（§6.2 的 `A-6.2 判可用 = 28` 本身是对的、我实测也是 28）。
  `oracle §6.2/§9` 规定「实测与本表不符 ⇒ 按 `erratum-*` 记录，不回改本表」，
  而 `handoff.L271.matches_oracle_frozen_hand_calculation = true`、step 2 detail 更写
  「**no erratum needed because every measured number matched the frozen hand calculation**」—— **该句对 24/28 这一点不成立**。
  **影响**：`28 ≥ 14` 与 `24 ≥ 14` 同为命中，**T3-literal 结论、U-PRIMARY 全部数字、最终 verdict 均不受影响**；
  纯属**披露/计数纪律**问题 ⇒ **P2，不升 P1**。
- **P2-2｜同一份机器报告里并存两条互相矛盾的读法，且未标注哪条对 `usable` 生效。**
  `green/validation_report.json` 的 `threshold_reviewability.rule` 写 U-PRIMARY（`not_reviewed` 的 arithmetic/disclosure **usable=true**），
  而紧邻的 `threshold_review_status_schema.fail_closed` 逐字写
  「`threshold_review_status` absent **or not_reviewed** ⇒ **the threshold does not participate in any judgement**」（= 字面 A-6.1）。
  对同 26 条记录，一个说「可用」、一个说「不参与任何判定」，**下游 I-11-B「阈值门」/ I-11-C 无法从报告本身判断以谁为准**。
  **方向是 fail-safe 的**（字面串只会导致更保守），且本复审已在 §3 裁定 U-PRIMARY 生效 ⇒ **P2 不升 P1**；
  建议补一行 `reading: "U-PRIMARY governs usable; the fail_closed string is the verbatim A-6.1 item-1 source text (literal reading, counterfactual)"`。

### P3（记录在案即可）

- **P3-1｜补丁内引用路径笔误**：`changes.diff` L24（= `iso_patched` 内 `B6C-SCHEMA` 注释）写
  `ruling execution_runs/I11A-OPEN-ACCT/a20260924-01.md L226`，正确应为 `.../a20260924-01/ruling.md`。仅注释，不影响判定。
- **P3-2｜报告键名与冻结措辞有出入**：`oracle §3.1` 冻结「报告写 `defaulted=true` + **`carried=false`**」；
  实现落的是 `defaulted` + **`threshold_review_status_present`**（语义等价，但无字面 `carried` 键）。
- **P3-3｜M4/M5 是「判定级」而非「整标记块级」变异**（保留共享 `_trs_*` 赋值以免 `NameError`）——
  实现者已在 `handoff.unverified` 第 3 条与 `make_mutants.py` 内如实披露；我复核其源码后认为**该保留在方法上正当**
  （删整块会崩溃、不构成判别力证据），**不扣分**，仅登记。
- **（非扣分，登记册卫生）** `REMEDIATION_REGISTER §一四三` 在 B 段「原结论已作废」（L3271）**之后**仍留有
  「前置 1 / **前置 2：先裁 A-6.1 的实施方式再落字段与校验器**」的原文（L3273–3276）。
  我按 **B 段 + L298/L324 受理人（编排层本就在列）+ L3557「L271 是反例不是前置」**认定该前置**已被推翻**；
  建议父追加一行显式指向，避免下一位再误读一次。

---

## 7. `unverified`（本复审**没有**验证的东西，如实登记）

1. **21,908 文件的全盘 JSON 扫描未复跑**（oracle §6.1 冻结时做过）。我只复核了**冻结的 6 份语料**
   （sha 全等 + 记录数 8/8/8/8/4/4 + 分 basis 24/4/12 + 0 字段携带）。
   ⇒ 「盘上没有第 7 份阈值记录文件」这一断言**未独立复验**。
2. **`T1` 是「可用阈值探针」，不是真的 I-11-C 启动**：真实 I-11-C 代码是否能开机**未测**（超出本卡范围，实现者已披露）。
3. **`A-6.3` 的四要素是否满足**（观测量可复算 / 可核基础 / 非实现者签署 / 追加式版本化）**与本卡无关、我未审**：
   `BLOCKED-6a`（3 条判断类阈值数值）、`BLOCKED-6b`（4 条容差）**仍 `still_blocked`**，本报告**不解锁、不代签**。
4. **实现者未跑任何产品仓测试套件 / CI / lint**（超范围，已披露）；我同样未跑 —— 因为本卡**零产品写**。
5. **`red/` 下的日志与报告带 CRLF**（Windows 控制台 / 校验器写出），实现者已披露并将 `green/` 归一为 LF；
   我核的是**内容全等**而非行尾。
6. **`handoff.continuation.previous_patch_sha_not_recoverable`**（36,030 B 的中间态补丁无 sha 可回填）——
   属系统事件遗留，**我无法验证也未试图恢复**；本 attempt 的**后像**已由 `1085368e3d05cf9b…` 锁定。
7. **`I-11-C` 是否复用同一校验器** 未裁（`OPEN-12` 另立专业卡，owner 已答「是」）。
8. **3 签名阈值审定路径**：本复审**不授予任何审定签署**，`reviewed` 语义的后续使用仍须按 A-6.3 逐条取证。
9. **`red/` 由「上一位 worker」与「续跑 worker」两段完成**：前者的 rc 从未落盘、
   `rc=0` 来自续跑重跑（`red/baseline_recheck_report.json` 与前件 sha 相同 `adcade2f…`）——
   我的独立重跑给出**同样的 0**，但**无法回溯上一位当时的真实 rc**。

---

## 8. 边界（我**没有**做的事）

- **没有**改本 attempt 任何一个既有字节；写入面**只有** `reviewer_report.md` + `reviewer_report.sha256`。
- **没有**写卡状态：`handoff.json` 的 `status`/`implementer_signed`/`releases_nothing` 一字未动。
- **没有**解除 `BLOCKED-6b` / `OPEN-6` / `BLOCKED-6c`，**没有**放行任何参数（`low/base/high` 仍 `null`）。
- **没有**改 `threshold_basis`、没有改任何阈值数值、没有把 `SIGNED`/`approved_frozen` 翻译成 `reviewed`。
- **没有**改封盘 `I-11-A/a20260919-01`、两半区裁定（`I11A-OPEN-ACCT`/`-IND`/`-MERGE`）、`OPEN6-TOLERANCE-*` 任何字节
  —— 14 份封盘输入我逐件复算 sha，**0 不符**。
- **没有**执行 `git add/commit/checkout/stash/restore/reset`，**没有用 `git status`**，**没有联网**。
- **没有**写五份计划文件（`task_plan.md`/`progress.md`/`findings.md`/`OWNER_DECISIONS`/`REMEDIATION_REGISTER`）。
- **没有**跑产品仓测试/CI/lint；**没有**创建/修改任何语料文件（monitor 全程只读打开）。
- **没有**代任何 reviewer 签署，**没有**产生 `I-11-B`/`I-11-C` 的 ACCEPT。

**收尾实测**：`git -c core.quotepath=false diff HEAD --name-only` → 总数 **3830**，**非 `.planning` = 0**；
本 attempt 顶层 4 件 sha 与复审开始时**完全一致**；attempt 内 `__pycache__` 目录数 = **0**。

---

## 9. 给编排层的处置建议

1. **`VERDICT: ACCEPT`**（P1=0 · P2×2 · P3×3），六项复核**全部独立复跑通过**，两道 fail-closed 未触发。
2. **读法已裁定 = `U-PRIMARY`**（§3），`trigger_fired=false` ⇒ **不建议改判 `blocked`**；
   U-LITERAL 三线全中的数字**继续保留在 `handoff`/`l271_report` 里作为反事实披露**。
3. 请把 **P2-1（`erratum` 补登 24→28）** 与 **P2-2（报告内标注哪条读法对 `usable` 生效）**
   作为**追加式勘误**派发（`oracle.md` 正文一字不改，只加 `erratum-*` 附录 / 下一版报告字段）。
4. `L17` **不适用**（§4）；`OPEN-12` 一旦裁 `I-11-C` 复用本校验器，须回来做**跨卡同步 + L17 复评**。
5. 本报告**不产生**对 `BLOCKED-6a/6b`、`OPEN-6`、`OPEN-12` 的任何状态变更。

---

**复审签名**：`implementer_signed = false`（本复审**不代签**）· 复审位与实现者非同一人 ·
全部实测在 `%TEMP%\dsh-Mjicmt\b6c_rev_a20260926\` 隔离副本完成 · 时点 2026-09-26。
