# T1-10-FIX 独立复审报告 · reviewer_report（card T1-10-FIX / attempt a20260923-01）

- 复审者：**独立 reviewer，N=1**（父代理 session-bfecd191-fbc3-4a66-8ed1-6562479bf102 派单；本文件即 M-T-REVIEW 返修块
  「经独立验收后收口」所要求的**独立验收**载体）。
- 复审时间：2026-09-24（续令 05:56 后完成；前次会话冻结于 recovery.md 之后）。
- 工具边界：**read / grep / pwsh 只读 + %TEMP% 自跑**；产品与卡树零写入（仅本目录下两份报告文件为我所写）；
  无网络；无 state-changing git（我用过的 git 仅 `rev-parse` / `status --porcelain` / `diff --no-index`，均只读且后两者在
  %TEMP% 与只读范围）。
- REM-79 自检：`execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py` v1.2.0-correction2，
  `PYTHONIOENCODING=utf-8`，对象 = 本文件，结果见 §12。

---

## 1. 裁定（verdict）

**ACCEPT —— 缺陷①（claim.basis 枚举校验非全函数）已在其**全部 3 个入口**（E1 载体读取 / E2 J16 守卫 / E3 `basis_registered`）
闭合，且**结构性**地闭合（MUT-G4 证明「只补一个守卫点」不够、tuple+载体守卫一次覆盖三处）；fabricated-green 负控**双向成立**
（18≥11 声明毒化两向皆非绿，正对照绿）；良构行为逐字节不变；缺陷② 区零交集。

据此我**签发独立验收**：T1-10 的 `changes_required` 返修块四项交付（补全覆盖 / 畸形 basis 负例族 / 裁决机关不可被单例炸毁的
负控 / T1-8 式 fabricated-green 负控）在本 attempt **全部达成且经我自跑复现**。T1-10 可按返修块原文收口。

随附裁定（我拥有的唯一裁权，详见 §7.3）：**F-3 = 畸形时间戳 rc=4 的 schema 级 rc 归属 = reviewer-owned，现予裁定**：
单 case 字段的类型/格式错误属 **per-case 拒绝（rc=0、报告写出、整批全裁决）**，rc=2 只属文档/调用域，rc=4 只留真内部错误；
需以**追加式 oracle §11.8** 落文（原文见 §7.3），并把 F-3 放入**独立修轨**（T1-F3-FIX），P4 已登记的容器族则并入
**T1-F2-FIX**（父已派）。

范围与身份：本卡 `handoff.json` 仍 `review_pending` / `implementer_signed=false`（实现者未自签）；我的 ACCEPT 是**复审侧**裁定，
不改写该卡任何 status 字段（边界=只写本报告与其 sidecar）。

---

## 2. 交付物核验（对应原令 §Verify-1）

| 交付物 | 我的实测 | 判定 |
|---|---|---|
| `oracle.md` 运行前冻结 | sha256 `afe8b61a3274e2473fe08db116e362bacf30e7c99facc90ec13d9453c929e4fb`（= handoff 登记值）；mtime `2026-09-23T22:55:38Z`；`evidence/**` 内**早于 oracle 的文件数 = 0**，最早跑批证据 `23:08:30Z`（`before/suite_r1.txt`） | ✓ 冻结先于任何运行 |
| `binding.json` | sha `d43fe183…` = handoff 登记值；**22 个 input pin 我逐个重算（含字节数）：mismatch = 0** | ✓ |
| `commands.json` | `steps` 数组 **19 步**（n=1…19），`git_commands: 0`，4 条 `disclosures` | ✓ |
| `decision.md` | §6 范围外发现表（F-1/F-2/F-3/P4 容器）、§7 过程披露 4 条、§9 关键指纹齐备 | ✓ |
| `changes.diff` | sha `625ecfe4…`、11534 B；我自数 **+229 / −4**；我自跑 **`git apply --check` rc=0**（%TEMP% 干净目录，左侧预置 pristine `7fff6f0c…`），patch 体只含 `iso/natural_window.py` + `harness/tests/test_i14b_natural_window_basis_total.py` | ✓ |
| `handoff.json` | sha `f3f4dd2bc5c08f09f69261a1069a5ec3eedab1206d02951ea6b84195c661a445`（其自述不自登记，此处补报）；`status=review_pending`、`reviewer_status` 明写未验收、`implementer_signed=false`；修复源 `90bcefb9…` + 3 条 row carrier 全部在 22 pin 内且我重算相等 | ✓ 未自签 |
| `recovery.md` | 在；含状态锚 sha 表、before/after 跑序约束、`--basetemp` 父目录前置、无删除声明 | ✓ |
| `evidence/manifest.sha256` | **558 条**（文件带 UTF-8 BOM `ef bb bf`）；我按 15 个抽样位（0,1,2,25,50,99,149,199,249,299,349,399,449,499,557）重算 **15/15 OK** | ✓ |
| `scripts/` | 恰 2 个：`verify_t1_10_fix.py` 39297 B、`make_diff.py` 2920 B | ✓ |
| 修复源原文 | `M-T-REVIEW/…/landing_package/t1_review_flips.md` L28–40 我逐行读过：`changes_required`、返修四件（补全覆盖至**全部入口** / 立修卡+畸形 basis 负例族 / 裁决机关不可被单例炸毁的负控 / 建议纳入 T1-8 fabricated-green 负控）、`经独立验收后收口`；`T1_rulings.md:18`、`acceptance_rulings.md:87`、`decision.md:53` 三行原文与 binding 登记一致 | ✓ |

---

## 3. 轨迹复核（对应原令 §Verify-2）

基线（`worktree/baseline/natural_window.r2.pristine.py`，sha `7fff6f0c…`，与 pin10 `I-14-B/iso/natural_window.py` 同值）：

| 入口 | 行（我实读） | 代码 | 畸形行为 |
|---|---|---|---|
| E1 | **:199** | `basis = (fields.get("_claim") or {}).get("basis")` | 载体真值非对象 → `AttributeError` |
| E2 | **:202** | `if basis not in BASIS_REGISTRY:  # J16 / P1`（registry = **set :60–66**） | list/dict → `TypeError: unhashable type` |
| E3 | **:247** | `"basis_registered": basis in BASIS_REGISTRY` | 同 E2 的第二个 set 成员测试 |
| rc=4 机制 | **:468–473** | `try: verdicts=[classify(...) for c in cases] except Exception → print(internal_error) → return 4` | 报告写在 :475 之后 ⇒ 崩溃即**无报告、0 裁决**（剥夺裁决） |

修复后（`worktree/i14b/iso/natural_window.py`，sha `064e5381…` = handoff 登记值）：registry 元组 **:68**、载体守卫 **:213–215**、
守卫行 **:219**、`basis_registered` **:264**。

**我自己的差分**（%TEMP% 中 `git diff --no-index -U0 base fix`，不依赖其 difflib 脚本）：被替换的旧行恰为
**{60, 66, 199, 200}**；与缺陷② 区 **:174–197 的交集 = ∅**；新增行全是注释 + `BASIS_REGISTRY = (` / `)` + 载体守卫 3 行 +
`claim.get(...)` 两行。

**守卫行文本字节相同**：`    if basis not in BASIS_REGISTRY:  # J16 / P1` 在基线与修复后各 **count = 1**（我 grep 计数）；
该串正是 `mutate.r2.py:99` 的 MUT-15 锚（我实读该行），亦是 `test_i14b_natural_window_r2.py:150` 的 `sorted(SUT.BASIS_REGISTRY)`
所依赖的 enumeration 定义（test 文件 sha `ace07687…` = pin18，**未重录**；pin 重算相等）。

---

## 4. RGM 自跑复现（对应原令 §Verify-3，全部输出落 %TEMP%）

自跑目录：`%TEMP%\t1_10fix_rev_988388640`（用 I-14-B venv Python 3.13.9、`-X utf8 -B`、`PYTHONIOENCODING=utf-8`）。

| 面 | 卡方记录 | **我的自跑** | 判定 |
|---|---|---|---|
| probe `--phase before`（基线） | 32 checks / PASS | **32 / PASS，rc=0** | ✓ |
| probe `--phase after`（修复后） | 39 checks / PASS | **39 / PASS，rc=0** | ✓ |
| RED 6 崩溃形状 | B1/B2/B3/B11/B12a/b/c = rc4、无报告、0 裁决 + 直调 traceback | 我自跑同值（`unhashable type: 'list'/'dict'`、`'list'/'str' object has no attribute 'get'`） | ✓ |
| GREEN 同输入 | rc0、`reject_claim`+`[R-BASIS-UNKNOWN]`、`basis_registered=false`、整批裁决 | 我自跑同值 | ✓ |
| 爆炸半径 A | RED 0/13 → GREEN **13/13，仅 BAD-LIST 被拒** | 两相位我自跑同值 | ✓ |
| 爆炸半径 B（对照） | 13/13 不变 | 同值 | ✓ |
| 爆炸半径 C | RED 0/8 → GREEN **8/8，仅 BAD-DICT 被拒** | 同值 | ✓ |
| probe 计数 | 32/32 → 39/39 | 同值 | ✓ |
| 新族套件 | before **16 failed / 7 passed** → after **23 passed / 0 failed** | 我独立 pytest 六次：before r1 **32/0**、r2 **18/0**、basis **16F/7P**；after r1 **32/0**、r2 **18/0**、basis **23/0** | ✓ |
| r1 / r2 计数 | 32 / 18（before==after） | 同值 | ✓ |
| r2 冻结门 | 34/34 rc0 | 我自跑 before/after 皆 rc=0、mismatch=0、34 case | ✓ |
| r1 门 | rc=1（superseded 增量） | 我自跑 before/after 皆 rc=1、mismatch=1 | ✓（既有态，非本卡回归） |
| **SUT 报告字节** | r2 `beb06495…` / r1 `6fa04855…` | 我算 4 个对象：记录 before、记录 after、**我自跑 before**、**我自跑 after** —— r2 四者同为 `beb06495…`，r1 四者同为 `6fa04855…` | ✓ 逐字节相同 |
| MUT-G1（tuple→set 回退） | B1/B2/B11 rc4 无报告 | 我自跑 PASS，且 `mutation_results.json` 我自跑与记录 **sha 同为 `058ba791…`** | ✓ |
| MUT-G2（去载体守卫） | B3/B12a rc4 无报告 | 同上 | ✓ |
| MUT-G3（锚恰一次） | count=1（fixed + baseline） | 我自跑同值 | ✓ |
| **MUT-G4**（reviewer 备选单独用） | `4787e3f9…`，B1 rc4 `unhashable`（E2→E3 搬家）、B3 rc4 `AttributeError`（E1 未护） | 变体文件在盘且 **sha = `4787e3f9…` 完全相等**；与基线逐行比**恰差 1 行（L202）**；我用保留变体自跑 CLI：**B1 rc=4 `unhashable type: 'list'`、B3 rc=4 `'list' object has no attribute 'get'`**；我又自造同语义守卫（无后缀）得同结果 | ✓ 结构论证成立 |
| 既有 20 臂变异机关 | before==after 全红、`all_expected_cases_red=true`、MUT-15→X1–X4 | 我把两棵树 robocopy 到 %TEMP% 各自重跑 `mutate.r2.py`：两树 **20/20 全红**、逐臂 `cases_red` 列表**逐行相等**（MUT-15 = X1,X2,X3,X4；MUT-16 = W1,X1,X5,X6,X7 …） | ✓ |

probe 结果与记录的**结构化逐叶比对**：before 911 叶中仅 **8 叶**不同、after 1724 叶中仅 **24 叶**不同，且这些差异叶**均为
`stdout_head`/`checks[].detail` 内嵌的 `--report` 绝对路径（我改道 %TEMP% 所致）；rc、verdict、refusals、arms、checks 的
`holds` 值域在两份文件**逐叶相等**（域=除路径串以外的叶子）。

---

## 5. fabricated-green 负控（对应原令 §Verify-4）

我自跑 `verify_t1_10_fix.py nc`（输出到 %TEMP%）→ `nc_results.json` 与记录**字节相同**（双方 sha =
`ec49634ce6973f25d9bf962ba81056774c86d7477449babf08cc70c3b8ecf77d`，幂等）：

| 臂 | 毒化 | 实测 | 绿？ |
|---|---|---|---|
| PC 正对照 | 无 | runner **rc=0 / ok=true / mismatch=0** | 绿（负控非永红） |
| NC-1 输入侧 | `cases.r2` 副本中 **18 个 window `claim.basis` → `["union_of_windows"]`**（18 ≥ T1-8 的 11） | SUT **rc=0、34/34 全裁决**（批量毒化炸不毁机关）；runner **rc=1 / ok=false / 21 mismatch / 18 个 window id 全数入账** | **非绿** |
| NC-2 断言侧 | expectations 副本中 **18 个 window 声明 verdict 翻转**（X1–X4 另清空 refusals） | runner **rc=1 / ok=false / 36 mismatch / 同 18 个 id** | **非绿** |

**与 T1-8 的方向对照（我实读其原文，非转述）**：`T1-8/a20260920-03/decision.md:22`「把全部 11 条声明都投毒成 `ImportError`
之后，runner 仍是 `rc=0` / `verdict=pass` / 11/11 `PASS_rejected`」，其量测记录 `t8_pre3_cost_reconciliation.json:330`
`"measured": "rc=0, verdict=pass, 11/11 PASS_rejected"`。⇒ 同型毒化在 T1-8 得**伪造的绿**、在本面得**双向红**，
方向相反，且本面毒化数（18）高于 T1-8（11）。我未重跑 T1-8 自身脚本（会写入其卡树，超出我的只读边界）——
该对照为**读录级**核验。

---

## 6. 不变量 33/33（对应原令 §Verify-5）

- 对**记录证据**重跑其 `invariants` 子命令 → **PASS，33 checks / failed_checks = 0**。
- 对**我刚自跑产出的新鲜证据**（probe/suite/gate/mutation 全套）再跑同一子命令 → **PASS，33/33**，
  `changed_baseline_lines = [60, 66, 199, 200]`。
- 拒绝码词表：基线与修复后**同为 16 个 `R-*`**（逐值相等，无新增）。
- `expected_superseded.W1…old = 2220` 与 `expected.W1.union_seconds = 1740` 均在读（pin `a24d8ab3…` 相等）。
- 冻结载体 pin 全等：`oracle.md(bdd0407a…)`、`review.md(ab93734d…)`、`changes.r2.diff(660bc943…)`、
  `run_cases.py(f2a07d0b…)`、`mutate.r2.py(4f741cb7…)`、两测试、两 cases、两 expectations —— 我逐个重算相等。

---

## 7. 发现与处置（对应原令 §Verify-6）

### 7.1 F-1（新发现）→ T1-F2-FIX（父已派，本报告只引用）

`clock_source` 的 `TRUSTED_CLOCKS`（**set**，基线 :56 / 修复后同文本）成员测试 **基线 :338 / 修复后 :360**：
`if clock_source not in TRUSTED_CLOCKS:  # J7`。我**在修复后 SUT 上自跑** `clock_source=["system_utc"]` →
**rc=4、无报告、`internal_error: unhashable type: 'list'`**（与记录 `adjacent_discovery.clock_source_container_J7` 同值）。
reviewer P4 未点名此落点（P4 只点了 windows/sampled_at/claim/ledger），故属**新发现**，与缺陷①同族、判据不同（J7）。
**处置：并入父方已派的 T1-F2-FIX**（父令 05:56 明示该卡已派，F-1/F-2 覆盖）；同款 tuple 修法不破坏 MUT-7 锚
（`mutate.r2.py` MUT-7 锚 = `if clock_source not in TRUSTED_CLOCKS:  # J7`，我实读）。注：复审时 `execution_runs/T1-F2-FIX`
目录尚未落盘（我列目录未见），故仅按父令引用、不核其内容。

### 7.2 F-2 → 同一 T1-F2-FIX

日历载体 `claim.status` 读取 **基线 :343 / 修复后 :360 邻近行**：`claim_status = (fields.get("_claim") or {}).get("status")`
无类型守卫。我**在修复后 SUT 上自跑** `claim=["pending"]` → **rc=4、`'list' object has no attribute 'get'`**（= P4「claim 为 list」
的日历落点，本卡只修了 basis 落点 E1）。**处置：T1-F2-FIX**。

**附带实测（P4 已登记未复测的容器族，我补测于修复后 SUT）**：
`windows` 为 dict → rc=4 `string indices must be integers, not 'str'`；`sampled_at` 为 dict → rc=4 `Invalid isoformat string: 'a'`；
`ledger.daily` 为 dict → rc=4 `string indices must be integers, not 'str'`。三者同为**字段形状/载体**类非全函数，
与 F-1/F-2 同机制 ⇒ **建议并入 T1-F2-FIX 同卡**（父裁）；其拒绝语义按 §7.3 的 §11.8 规则执行。

### 7.3 **F-3 = 我的显式裁权：schema 级 rc 归属（reviewer-owned）**

**被裁对象**：`started_at="not-a-timestamp"` → `_parse` 抛 `ValueError: Invalid isoformat string` → `main()` 内部错误处理器
→ **rc=4、无报告、整批 0 裁决**（我在修复后 SUT 自跑复现：rc=4、`report=False`）。该形状在 P4 与本卡 oracle I-5 中被显式
**留待 reviewer**（`review.md:353`：「并在 oracle §11 明确"字段类型错误"属 schema 级 rc 2 还是 per-case 拒绝」；
本卡 `oracle.md` I-5「不自填」、§7 E-adj-4「reviewer 归属」）。**故所有权在我，现裁如下。**

**我读到的 rc 域文本（裁定依据）**：
- I-14-B `oracle.md:177-180`（§8）：`0`=全部 case 已判定且无不合规 accept；`2`=输入畸形/schema 不符（fail-closed）；`4`=内部错误。
- `oracle.md:188`（§8-errata，运行前写成）：`0`=报告已写出且每个 case 都已判定；`2`=输入畸形（fail-closed）；`4`=内部错误。
- `oracle.md:461-466`（实现）：**文档级**畸形（`json.loads` / 缺 `cases` / `frozen_now_utc` 不可解析）已在进入判定前走 **rc=2 `malformed_input`** —— 即 rc=2 的既有落点就是**调用/文档域**。
- `review.md:352`（P4）：rc4 在 §8 已登记、fail-closed、对「不合规被 accept」而言非阻断；但同一段同时提请 §11 澄清归属 —— 就归属措辞而言，P4 自身并未把 rc4 判为终局。
- `decision.md §6 F-3` 行：实测 rc=4、归属「schema 级 rc 归属 = reviewer 专属口径」。

**裁定（选 (b) + 需要 (c) 追加，不取 (a)）**：

1. **rc=2 = 文档/调用域专属**：只覆盖「在进入任何 case 判定之前就失败」的形状（现有 `main()` L461–466 路径）。
   此时本就没有任何裁决存在，故 fail-closed 不构成剥夺。
2. **rc=4 = 真正的内部错误专属**。用户提供的**单 case 字段**类型/格式错误**不是内部错误**；记成 rc=4 会
   (i) 误分类，(ii) **复现缺陷①的剥夺裁决形态**（报告不写、整批 0 裁决），这正是 M-T-REVIEW 已裁定为缺陷的那一种观测面。
   ⇒ (a)「rc=4 schema-class 正确并保留」**被否**：畸形时间戳属**输入**而非内部错误，且其爆炸半径与缺陷①同形。
3. **单 case 字段的类型/格式错误 = per-case 拒绝（rc=0、报告写出、整批全部裁决）**，与 §11.3 标量校验同语义；
   时间戳畸形需**一个新拒绝码 `R-TIMESTAMP-MALFORMED`**（现有 16 码词表中无对应码；缺陷①因存在同语义邻码才免增码），
   该码由下列 §11.8 追加文**唯一授权**入 §11.3 词表，受影响 `computed` 时间字段置 `null`、其余派生量按可得事实计算。
4. **需要 (c) oracle 追加**：§11 本就是「追加式勘误」节（`oracle.md:211-213`），故不改 §1–§10、不回改 §6.1 冻结四行，
   只追加 §11.8。**本卡 oracle 已冻结（sha `afe8b61a…`）且我零写入** ⇒ 追加文交**父/owner** 落到 I-14-B `oracle.md` 末尾
   （或按父方惯例落到承接修卡的 binding 引用），我不落笔。

**追加文原文（我裁定的 amendment text，逐字可用）**：

```markdown
### 11.8 rc 归属裁定：schema 级 vs per-case（reviewer-owned，追加式；触发 = T1-10-FIX F-3 + review.md:353 提请）

- **rc=2 = 仅「文档/调用域」的输入畸形**：`--cases` 不可解析、顶层缺 `cases`/`frozen_now_utc`、
  或 `frozen_now_utc` 本身不可解析 —— 即 `main()` 在**进入任何 case 判定之前**失败的那批形状
  （既有实现 L461–466）。判定对象是本次调用；fail-closed 在此不剥夺任何裁决（此时本无裁决）。
- **rc=4 = 仅真正的内部错误**（实现自身缺陷）。**用户提供的单 case 字段**类型/格式错误不属于 rc=4：
  把它记成 rc=4 既属误分类，又复现缺陷①的「剥夺裁决」形态（报告不写出、整批 0 裁决）。
- **单 case 字段的类型/格式错误 = per-case 拒绝**：该 case 记 `reject_claim`、整批照常裁决、
  报告照常写出、SUT rc=0；与 §11.3 标量校验同语义：
  - `basis` 容器 / `claim` 载体非对象 / `clock_source` 容器 / `windows`、`sampled_at`、`ledger.daily` 为容器
    → 按既有码拒绝（basis/载体族 = `R-BASIS-UNKNOWN`；时钟 = `R-SIMULATED-CLOCK`；载体不可读 ≡ 缺键）；
  - 时间戳畸形（`_parse` 抛 `ValueError`，如 `started_at="not-a-timestamp"`）→ `reject_claim` +
    **新码 `R-TIMESTAMP-MALFORMED`**（本节为该码的唯一授权来源；词表自 16 码增至 17 码），
    无法解析的时间字段在 `computed` 中置 `null`，其余派生量按可得事实计算。
- **变异/回归要求（承接修卡）**：任一畸形单 case 字段不得使任何其他 case 的裁决丢失 —— 回归面同缺陷①：
  批次臂 rc=0、坏 case 单独被拒、良构 case 输出逐字节不变；且须带「单畸形 case 不可炸批」的批次负控。
- 触发与授权链：I-14-B `review.md:353`（P4 提请 §11 明确归属）→ T1-10-FIX `oracle.md §7 E-adj-4 / I-5`
  （实现卡拒绝自填、显式留待 reviewer）→ 本裁定（T1-10-FIX 独立 reviewer，2026-09-24，N=1）。
- 落点分工：**F-3（时间戳 `_parse` 非全函数）→ 独立修轨 T1-F3-FIX**（机制=解析全函数化，与 F-1/F-2 的
  成员/载体守卫不同，且 T1-F2-FIX 已派未含此项）；**F-1/F-2 与 P4 容器族 → T1-F2-FIX**；
  两卡共用本节文本，先落者写入、后落者只引用。
```

**F-3 是否解锁**：**解锁**。所有权争点（reviewer-owned）已由本裁定闭合：F-3 不再是「等 oracle 裁定」的挂起项。
轨道选择 = **独立修轨（T1-F3-FIX）**，理由：机制不同（`_parse` 全函数化 + 新拒绝码 + 新测试族）、
T1-F2-FIX 已派且未含此项（重开范围需父改派）；但 §11.8 文本两卡共用。若父选择合并，本裁定不反对 —— 只要求
合并后仍带 (i) §11.8 追加、(ii) 批次负控、(iii) 良构字节不变三项验收面。

---

## 8. 过程披露核验（对应原令 §Verify-7）

| 披露（`decision.md §7` / `commands.json disclosures`） | 我的核验 | 判定 |
|---|---|---|
| ① 路径守卫差一级 → probe 首跑 rc=1、**零证据写出**、修正后重跑 32/32 | 结构上可证：现脚本 `verify_t1_10_fix.py:43` 的 `assert (PLAN/"task_plan.md").is_file()` 在**任何写盘动作之前**于 import 期执行（`out.mkdir` 首次出现在 :361），断言失败 ⇒ rc=1 且无产物；`evidence/**` 内早于 oracle 的文件数 = 0，且无孤儿/半截文件。**时间线相容**：before 相位证据顺序为 suites `23:08:30` → gates `23:08:40` → mutations `23:08:44` → **probes `23:11:26`（最后）**，与「probe 首跑失败、修正后才落证据」相容（声明的 step 序号 ≠ 实跑序）。**残余**：rc=1 那一次本身无产物可验，属**自述**，我按结构相容接受。 | ✓（结构级；事件本身不可由产物证明） |
| ② `--basetemp` 父目录不存在 → 基线族套件首跑 1 error、建目录后重跑 16F/7P | `_pytest_tmp/` 在盘且含 `before_basis`、`after_basis`；被覆盖的那次 error 输出**无留存（自述）**；我独立重跑得 **16 failed / 7 passed**，与其 FAILED 表（16 行，含 `[B1][B2][B3][B11][B12a/b/c]` 与两条 batch/total 测试）一致 | ✓（重跑值可复现；error 那次不可复核，已如实声明） |
| ③ PowerShell 编码域：`Out-File -Encoding utf8` 带 UTF-8 BOM、`*>` 写 UTF-16LE | 我读字节：`before/after suite_*.txt`、`*.stdout.txt`、`invariants.stdout.txt` 首三字节 = `ff fe …`（UTF-16LE）；`boundary_check.txt` = `ef bb bf`（UTF-8 BOM）；`invariants.json` = `7b 0d 0a`（纯 UTF-8+CRLF）。解码确需 `utf-8-sig`/BOM 探测 | ✓ |
| ④ r1 门 rc=1 属既有态 | 我自跑 before/after r1 门均 rc=1、mismatch=1、差异同为 W1 `union_seconds` 2220→1740（superseded 增量） | ✓ 非本卡回归 |

---

## 9. 边界（对应原令 §Verify-8）

- **22/22 input pin 我复算相等**（哈希 + 字节数双比对，mismatch=0；本次复审**会话开始时**的一次）；
  `evidence/boundary_check.txt` 记录跑后 0 mismatch（写于 `23:19:19Z`，卡运行窗内）。
  **续令轮末次复算（`2026-09-24T05:1xZ`）= 21/22 相等**，唯一失配 **pin #4 `M-T-REVIEW/a20260923-01/decision.md`**：
  `91f6f21b…`(8473 B) → `43936ff6…`(11672 B)，mtime `2026-09-24T05:07:05Z`。我实读该文件：被 pin 的
  **`decision.md:53` 载体行文本逐字未变**（我读得原行），变的是**追加**了一节 F-RV-01…05 落卡注记
  （同批 `review.md`/`handoff.json`/`qualification.json`/`install_log.jsonl` 的 mtime 集中在
  `05:05–05:13Z`，即**与本复审并行的他方 carrier-landing 批次**）。⇒ 该漂移**不属于 T1-10-FIX**
  （其运行窗止于 `09-23T23:24Z`）、**不属于我**（我只写 `reviewer_report.md|.sha256`，见页首与 §9 末条），
  且修复源块载体 `t1_review_flips.md`（pin #1，`90bcefb9…`）**仍相等**。如实登记，不掩盖。
- **I-14-B / T1-10 / T1-8 三树 touched 文件数 = 0**：以 oracle 冻结时刻（`22:55:38Z`）为界扫三树全部文件 mtime，
  **newer-than-oracle = 0**；`git status --porcelain` 限定这三树 → **输出为空（exit 0）**。
  附注：`M-T-REVIEW/reviewer_report.md|.sha256`（mtime `23:11Z`）落在本卡运行窗内，但**不在 22 pin 内**、
  其 4 个 carrier pin 我复算相等 ⇒ 属并行他方产物，归属不在我可断言范围（如实登记）。
- **oracle 未触**：I-14-B `oracle.md` 现算 `bdd0407a…` = pin19 = 跑前记录（before==after）；本卡 `oracle.md` 现算
  `afe8b61a…` = handoff 登记值。
- **无签名/status 移动**：`handoff.json` `implementer_signed=false`、`status=review_pending`、`boundary.signatures=none`；
  我未改其任何字段（我只写本报告与 sidecar）。
- **git**：本卡声明 git=0（`commands.json`）；我的 git 使用仅只读三式（见页首），**无 state-changing git**。
- **我的写入面**：`reviewer_report.md` + `reviewer_report.sha256`（本目录）与 `%TEMP%\t1_10fix_rev_988388640\**`（自跑产物）。
  自跑对卡树的触碰 = 0（20 臂变异机关我是在 %TEMP% 的 robocopy 副本上跑的，因其把 scratch/evidence 写在「所在树」内）。

---

## 10. 未核验 / 限制（如实）

1. **MUT-G4 构造脚本未留档**：`commands.json` step 15 写「see file for full script」，但 `MUT-G4_*.json` 内仅含
   description + probes，缺内联脚本（INFO 级）；所幸**变体文件本体在盘且 sha 与声称完全相等**，行为我已自跑复现，故证据链仍闭合。
2. **`commands.json` 非执行日志**：无终端 transcript 落盘；步序与 mtime 序不完全一致（probe 在 before 相位实际最后跑）。
   我以「记录证据 + 我的全量自跑复现」替代逐字执行核对（所有头号数字均已复现）。
3. **T1-8 对照为读录级**：未重跑 `verify_t8_pre3.py`（会写其卡树），依据 `decision.md:22` 与
   `t8_pre3_cost_reconciliation.json:330` 原文。
4. **deletions=0 不可全证**：只能以「两树各 344 文件俱在 + recovery 声明 + 我未见缺失路径」支持（域=本 attempt 目录树）。
5. **T1-F2-FIX 内容未核**：复审时该卡目录在 `execution_runs/` 下未出现（父令称已派）；我只引用不核验。
6. **changes.diff 未落地**：我只做 `git apply --check`（rc=0），未执行任何 apply/merge（无授权）。
7. **I-14-H 同体副本的传播未裁**（见 §11），属父/owner 决策，不在我的裁权内。
8. **并行写入的 pin 漂移（非本卡、非我）**：pin #4 `M-T-REVIEW/…/decision.md` 在我复审期间被他方追加
   F-RV 节而变更（§9 已给双方哈希与时刻）；本报告中一切以「22 pin 相等」为前提的结论，其**取证时点**
   分别标注为「卡跑后 `23:19:19Z`」与「本复审会话开始」两次（两次皆 0/22 失配）。
   若父需在落定批次里重跑该 pin，请以**追加式注记**登记该漂移来源，而非改判 T1-10-FIX 的边界声明。

---

## 11. 若 ACCEPT 的 scope（对应原令 Scope-if-accepting）

1. **缺陷① CLOSED at all 3 entries**（E1/E2/E3），且是 **G4-proven 的结构性闭合**（单守卫点不够：B1 仍崩于 E3、B3 仍崩于 E1；
   tuple 一次闭合 E2+E3 + 载体守卫闭合 E1）。交付 = `changes.diff` 两文件（`625ecfe4…`，+229 −4，`git apply --check` rc0）。
2. **NC 非伪造绿成立**：PC 绿 + NC-1/NC-2 双向红（18≥11），与 T1-8 的 11-毒化 rc=0/11-11 绿方向相反。
3. **F-1 / F-2 → T1-F2-FIX**（父已派，本报告 §7.1/7.2 引用；P4 容器族我建议同卡并入，父裁）。
4. **F-3 → 按 §7.3 裁定**：per-case 拒绝 + oracle §11.8 追加（原文已给）→ **独立修轨 T1-F3-FIX**（或父改派合并，验收面三项不减）。
5. **changes.diff 两文件的落点（application route，我实测）**：
   - diff 头为 `a/iso/natural_window.py` 与 `b/harness/tests/test_i14b_natural_window_basis_total.py`，
     **path base = I-14-B attempt 根**（`execution_runs/I-14-B/a20260919-01/`，其布局恰为 `iso/` + `harness/`）；
   - 左侧 sha `7fff6f0c…` == **I-14-B 规范源**（pin10）**且 == `I-14-H/a20260919-01/iso/natural_window.py`（逐字节同体）**
     ⇒ 对 I-14-B 可直接 apply；对 I-14-H 亦同体可 apply，**是否传播由父裁**；`I-14-I/.../natural_window.py` = `9edb9515…`
     （另一修订）⇒ 在其上不能直接 apply，需另行 rebase；
   - **产品树外零 SUT**：全项目 `natural_window.py` 仅出现在 `.planning/...` 内（I-14-B / I-14-H / I-14-I / 本卡两棵副本），
     即本 diff **不是对生产源的修改**；新测试文件与 SUT 同 base、**同波次**骑行即可（无需单独迁移通道）。

---

## 12. 关键指纹（我实算）

| 对象 | sha256 |
|---|---|
| `oracle.md`（运行前冻结） | `afe8b61a3274e2473fe08db116e362bacf30e7c99facc90ec13d9453c929e4fb` |
| `binding.json` | `d43fe18320d0dd0c58db11211da9e21c991a9a7b5a192e1bd055b12ee1d8e3af` |
| `commands.json` | `e8cfee7ec11e97944491b9e852e996583505a7cfa19b53e15fcfe7a0560f2f05` |
| `decision.md` | `7adebb7a340a22b49afa67dec94cd8d3cfea2aee25792ca2c574fd0cea9f780d` |
| `handoff.json` | `f3f4dd2bc5c08f09f69261a1069a5ec3eedab1206d02951ea6b84195c661a445` |
| `changes.diff` | `625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac` |
| `recovery.md` | `dd7950be580169a3a757e348ae7cebde9f36001278460bf992a6e6c941aa01da` |
| `evidence/manifest.sha256`（558 条） | `baf83fcda7f7c9133e9038dac1977874246485d6013f427501156f3b42b6c9f2` |
| 基线 SUT（= I-14-B 规范源） | `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` |
| 修复后 SUT | `064e5381444d35a8ab1184d6c8d2eaa839a40f96c704ae7995fa3b660c7e273d` |
| 新族测试文件 | `316e369c9afc9d8df04a425945b97e41378e87f3ac17c721d0ab9ddf90904bfd` |
| MUT-G4 变体 | `4787e3f9b2d0a317ed249507e6b79eec86de3897673bd30523ac9eeae4fba8f2` |
| r2 报告字节（before==after==我自跑×2） | `beb06495fcd93b2c4317428beaf282632169685d009165639bcc82b4732a1c79` |
| r1 报告字节（before==after==我自跑×2） | `6fa04855e76205fa2f65acb4e2808586aac85186fababb350c477513cbd8efbf` |
| 修复源载体 `t1_review_flips.md` | `90bcefb9aadfe098dee1f16802bdf0af9ac7af9b2d74b21cc10a45e07b26c33b` |
| 我自跑 `nc_results.json`（== 记录） | `ec49634ce6973f25d9bf962ba81056774c86d7477449babf08cc70c3b8ecf77d` |
| 我自跑 `mutation_results.json`（== 记录） | `058ba791ef43eb035d1995f7ce9db9c865fcd83e20a60ec48842f7182ecfd186` |

**REM-79 自检**：`check_domain_assertions.py` v1.2.0-correction2 × `PYTHONIOENCODING=utf-8` × 本文件 → 结果：
`rc=0 / 0 violations`（域 = 本报告；若本行与实跑不符，以实跑为准并在 sidecar 记录）。

—— 独立 reviewer N=1 · 2026-09-24 · 续令轮（父 session-bfecd191-fbc3-4a66-8ed1-6562479bf102）
