# T1-10-FIX decision —— 缺陷①（claim.basis 枚举校验非全函数）**已闭合于 changes.diff**；全入口覆盖 + 负例族 + 负控齐；状态 `review_pending`（未自签）

- 卡：**T1-10-FIX** / attempt `a20260923-01`
- 修复源（权威）：**M-T-REVIEW 的 T1-10 `changes_required` 返修块**
  `M-T-REVIEW/a20260923-01/landing_package/t1_review_flips.md` **L28–40**（sha `90bcefb9…`）；
  载体行 `reviews/T1_rulings.md:18`、`acceptance_rulings.md:87`、`decision.md:53`。
  块原文要求：「补全 claim.basis 校验覆盖面至**全部入口**（…立修卡并带**畸形 basis 负例族** +
  **裁决机关不可被单例炸毁的负控**）…建议同步纳入 T1-8 续查的 **fabricated-green 负控**」——四件本卡全部交付。
- 范围：**缺陷① only** + fabricated-green 负控（父卡冻结）；缺陷② 及其 provenance **维持接受、字节不触**（见 §5 实测）。
- 性质：源树 **READ-ONLY**（22 个输入 pin 全程复核不变 = 写入 0 次），交付 **仅 `changes.diff`**（零生产合并、无 git、无删除）。
- 结论：**缺陷① 的三个入口全部全函数化**；RED/GREEN/MUTATION/负控/族回归五面全绿（invariants **33/33**）。
  **收口仍待独立验收**（返修块明文「经独立验收后收口」）——本卡不自签。

---

## 1. 缺陷的行级验证轨迹（line-cited）

**基线 SUT** = I-14-B r2 `iso/natural_window.py`，sha256 `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796`
（与 T1-10/`t1_10_defect_verification.json` 记录值一致，实测复核）。claim.basis 的**读取/消费入口恰有三个**：

| 入口 | 基线行 | 基线代码 | 畸形输入下的行为（实测） |
|---|---|---|---|
| **E1** 载体读取 | `:199` | `basis = (fields.get("_claim") or {}).get("basis")` | `_claim` 为**真值非对象**（list/str/int/bool）→ `AttributeError: … has no attribute 'get'` → **rc=4，无报告，全批 0 裁决**（reviewer P4 原文「claim 为 list ⇒ rc 4」，`review.md:352`） |
| **E2** J16 守卫 | `:202` | `if basis not in BASIS_REGISTRY:  # J16 / P1`（`BASIS_REGISTRY` = **set**，`:60-66`） | list/dict basis → set 成员测试**先哈希探针** → `TypeError: unhashable type` → **rc=4，无报告**（T1-10 P-3 实测；reviewer P4 点名） |
| **E3** 报告字段 | `:247` | `"basis_registered": basis in BASIS_REGISTRY` | 同 E2：**第二个** set 成员测试，独立崩点 |

`main()` 的异常处理器（`:468-473`）把崩溃变成 rc=4 + `internal_error` 且**不写任何报告**——
即 T1-10 P-4/P-6 实测的「**剥夺裁决**」：一个畸形 case 让同批（甚至跨 class）所有 case 全部判不了。
这正是 M-T-REVIEW 裁定的「**护栏成为单点故障**」。

### 修法（changes.diff，只动这两个块）

| 入口 | 修复后行 | 修改 |
|---|---|---|
| E2+E3 | `L68 BASIS_REGISTRY = (` … `)`；守卫行 `L219` 与 `L264` **文本不变** | `set` → **`tuple`**（reviewer P4 首选最小修法原文：「`BASIS_REGISTRY` 由 `set` 改 `tuple`」`review.md:353`）。tuple 成员测试用 `==` 逐个比较、**不哈希探针** ⇒ 对**一切 JSON 值全函数**；**一处修改同时闭合 E2 与 E3**，且两处既有行文本不动 ⇒ `mutate.r2.py:99` 的 MUT-15 锚行**恰好一次保留**、r2 测试 `sorted(SUT.BASIS_REGISTRY)`（`test_…r2.py:150`）不受影响 |
| E1 | `L213-215` | 载体先验：`claim = fields.get("_claim")`；`if not isinstance(claim, dict): claim = {}`；再 `claim.get("basis")`。不可读 basis ≡ **缺键**（oracle §11.3 冻结语义：「未登记/空串/null/**缺键**一律拒」→ `R-BASIS-UNKNOWN`） |

**为什么必须三个入口一起修（本卡的分析贡献，实测证明）**：reviewer P4 的**备选**修法（「在 J16 前加
`isinstance(basis, str)` 守卫」）**单独**应用 = `MUT-G4` 实测（`evidence/after/mutation/scratch/MUT-G4_*.json`）：
B1 仍 **rc=4**（崩溃从 E2 **搬家到 E3**：`unhashable type: 'list'` 发生在 `basis_registered` 的 set 成员测试）、
B3 仍 **rc=4**（E1 未护）。⇒ 「只补守卫点」≠「补全覆盖至**全部入口**」——返修块的措辞是**结构性**要求，
本卡因此取 tuple（一次闭合 E2+E3）+ 载体守卫（闭合 E1），**三入口全绿**。

## 2. 案例表（oracle.md §1 冻结于任何运行之前；B* 形状取自 T1-10 块的 `verify_t1_10.py:99-129/171-201`）

| id | 形状（tamper 仅动 claim） | RED 基线 `7fff6f0c`（evidence/before/probes） | GREEN 修复后 `064e5381`（evidence/after/probes） | MUTATION |
|---|---|---|---|---|
| **B1** | basis=JSON 数组 `["union_of_windows"]` | **rc=4 / 无报告 / 0 裁决**；直调 `TypeError: unhashable type: 'list'` | rc=0 / 报告 / `reject`+`[R-BASIS-UNKNOWN]` / `basis_registered=false`；直调不抛 | **MUT-G1**（tuple→set）崩溃回归 rc=4 ✓ |
| **B2** | basis=JSON 对象 `{"name":…}` | **rc=4** `unhashable type: 'dict'` | 同 B1 干净拒绝 | **MUT-G1** 崩溃回归 ✓ |
| **B3** | 载体=JSON 数组（basis 不可读） | **rc=4** `'list' object has no attribute 'get'` | rc=0 干净拒绝（`computed.basis=null`） | **MUT-G2**（去载体守卫）崩溃回归 ✓ |
| **B11** | basis=嵌套容器 `[["x"]]` | **rc=4** `unhashable type: 'list'` | 同 B1 | MUT-G1 崩溃回归 ✓ |
| **B12a/b/c** | 载体=str/int/bool（真值非对象） | **rc=4** `… object has no attribute 'get'` ×3 | 同 B3 ×3 | MUT-G2（B12a）崩溃回归 ✓ |
| **B4** | missing-required（claim 缺 basis 键） | rc=0 `reject+[R-BASIS-UNKNOWN]` | **逐字节相同**（invariants I-2 行相等） | — |
| **B5** | unknown-key（合法 basis + 无关键） | rc=0 `accept` | **逐字节相同** | — |
| **B6** | 对照：登记值 | rc=0 `accept` | **逐字节相同** | — |
| **B7–B10** | 未登记串 / null / `5` / `""`（T1-10 标量五探针的四个） | rc=0 `reject+[R-BASIS-UNKNOWN]` | **逐字节相同** | — |

**爆炸半径臂**（T1-10 C_blast_radius 同形）：

| 臂 | RED 基线 | GREEN 修复后 |
|---|---|---|
| A：12 良构 + 1×B1 | **rc=4，0/13 裁决（殃及 13）** | **rc=0，13/13 裁决，仅 BAD-LIST 被拒（殃及 0）** |
| B 对照：12 良构 + 1×未登记串 | rc=0，13/13（只伤自己） | rc=0，13/13（不变） |
| C：1 calendar + 6 良构 + 1×B2 | **rc=4，0/8（跨 class 殃及）** | **rc=0，8/8，仅 BAD-DICT 被拒** |

**RED/GREEN/MUTATION（rgm）汇总**：RED = probe before **32/32 checks**（7 崩溃形状 rc=4 + A/C 臂全灭）
+ 新族套件 before **16 failed/7 passed**（FAILED 表含 `[B1] [B2] [B3] [B11] [B12a/b/c]`，traceback 落盘）；
GREEN = probe after **39/39 checks** + 新族套件 **23 passed/0 failed** + r1 套件 **32** + r2 套件 **18**（均 before==after）
+ r2 冻结门 **34/34 rc=0**；MUTATION = **MUT-G1/G2 崩溃回归**（守卫承重、非空洞）+ **MUT-G3** 锚行恰一次
+ 既有 **20 臂变异机关 before==after 全红**（MUT-15 → X1–X4）。

## 3. fabricated-green 负控（T1-8 式，双向，raws 全落盘）

T1-8 参照（`T1-8/a20260920-03/decision.md` L22）：毒化 **11 声明 → 仍 rc=0 / 11-of-11 `PASS_rejected` = 伪造的绿**。
本面**至少同等强度**（毒化数 18 ≥ 11，claim 侧与 assertion 侧各一臂，`evidence/after/negative_control/`）：

| 臂 | 毒化 | 结果（raws：`nc*.runner.stdout.txt` / `cases_report.json` / `nc1_sut_batch.*`） |
|---|---|---|
| **PC 正对照** | 无 | runner **rc=0 / ok=true / mismatch=0** ✓（负控非永红） |
| **NC-1 输入侧** | cases.r2 副本中**全部 18 个 window `claim.basis` → `["union_of_windows"]`**（缺陷① 形状） | SUT **rc=0、34/34 全裁决**（批量毒化**炸不毁机关**）；runner **rc=1 / ok=false / 21 处 mismatch / 18 个 window id 全数入账** ⇒ **未变绿** |
| **NC-2 断言侧** | expectations 副本中**全部 18 个 window 声明 verdict 翻转**（X1–X4 另清空 refusals） | runner **rc=1 / ok=false / 36 处 mismatch / 18 个 window id 全数入账** ⇒ **未变绿**（与 T1-8 的 rc=0 绿**方向相反**） |

⇒ T1-10 面的门**真比较、有区分度**：18 声明（>11）双向毒化全红 + 正对照绿 = **非伪造的绿**。

## 4. 回归与 J16 面（grep + run，before == after）

| 面 | before（基线 `7fff6f0c`） | after（修复 `064e5381`） | 判定 |
|---|---|---|---|
| r1 族套件 `test_i14b_natural_window.py` | **32 passed / 0 failed** | **32 passed / 0 failed** | ✓ 相等 |
| r2 族套件 `test_i14b_natural_window_r2.py` | **18 / 0** | **18 / 0** | ✓ 相等（含 `sorted(BASIS_REGISTRY)`、X1–X4、W1 union=1740 断言） |
| r2 冻结门 `run_cases --cases cases.r2.json` | rc=0 ok 34/34 | rc=0 ok 34/34 | ✓ |
| **SUT 报告字节**（I-2 逐字节） | r2 报告 sha `beb06495…` / r1 报告 sha `6fa04855…` | **完全相同两 sha** | ✓ **良构输入行为逐字节相同** |
| 20 臂变异机关 `mutate.r2.py` | 20/20 全红、`all_expected_cases_red=true` | **同**（逐臂 `cases_red` 列表相等，MUT-15 → X1–X4） | ✓ J16 面未被修法破坏 |
| grep 锚 | J16 守卫行/`basis_registered` 行/MUT-15 锚（1 次）/`sorted(…)` 测试 | **全部在场**（L219/L264 文本未动，锚 1 次） | ✓ |
| r1 门 | rc=1（W1 union 期望 2220） | rc=1（**逐字段相等**） | ✓ 非本卡回归——系缺陷② 已文档化的 `expected_superseded` 增量（§5） |

invariants 总检（`evidence/after/invariants.json`）：**33/33 PASS**——含 pin 全等（oracle/review/runner/mutator/
两测试/两 cases/两 expectations）、拒绝码词表不变（无新 `R-*`）、变更行 ∩ 缺陷② 区 `:174–197` = ∅。

## 5. 缺陷② 与 provenance 未触（实测断言）

1. `changes.diff` **只含两文件**：`iso/natural_window.py`（修改）+ `harness/tests/test_i14b_natural_window_basis_total.py`（新增）；
   变更基线行 = **{60, 66, 199, 200}**（仅 registry 定界 + 载体读取），与 quick_check/J15/J6 计算区 `:174–197` **零交集**。
2. `frozen_expectations.r2.json` **未改**（sha `a24d8ab3…` = pin）：`expected_superseded.W1…old == 2220` 仍可读、
   `expected.W1.union_seconds == 1740` 不变；`cases*.json`/`oracle.md`/`run_cases.py`/`mutate.r2.py`/既有两测试 **全部 sha=pin**。
3. r2 套件的缺陷② 语义断言（`test_w1_union_excludes_quick_check`：union=1740、qc=480、overlap=0）after **仍过**。

## 6. 范围外发现（登记移交——按 owner order「发现的缺陷都要全部修复」须立续修卡；本卡冻结范围=缺陷①，不扩刀）

实测（`evidence/*/probes/family_results.json` → `adjacent_discovery`）：

| 发现 | 入口 | 实测 | 归属 |
|---|---|---|---|
| **F-1（新发现）** J7 `clock_source` 同款非全函数：`TRUSTED_CLOCKS`（**set**）成员测试 `:338` | calendar | `clock_source=["system_utc"]` → **rc=4** `unhashable type: 'list'` | **reviewer P4 未点名**（P4 点了 windows/sampled_at/claim/ledger）；与缺陷① 同族不同判据（J7）——**须立卡**，同款 tuple 修法不破坏 MUT-7 锚 |
| **F-2** 日历载体 `claim.status` 读取 `:343` 无类型守卫 | calendar | `claim=["pending"]` → **rc=4** `'list' object has no attribute 'get'` | P4「claim 为 list」的**日历落点**（本卡只修了 basis 落点 E1）——**须立卡** |
| **F-3** 时间戳畸形 `_parse`（`started_at="not-a-timestamp"`）→ **rc=4** `Invalid isoformat string` | schema | 实测 rc=4 | **schema 级 rc 归属 = reviewer 专属口径**（P4 原文 + 本卡 oracle I-5：**不自填**）；待 reviewer 出 oracle §11 裁定 |
| P4 已登记未复测 | `windows`/`sampled_at` 为 dict、`ledger.daily` 为 dict ⇒ rc 4 | 引 `review.md:352` 原文 | 同批续修卡 |

## 7. 过程披露（本卡自生缺陷与修正，如实登记——三条同族于「判据/环境形态不匹配对象」）

1. **验证脚本路径守卫差一级**（`PLAN = ATTEMPT.parent.parent` 落在 `execution_runs`）→ probe **首跑 rc=1 在 import 即断言失败**、**未写任何证据**（无污染）；修正为经 `EXEC` 上溯后重跑，before 探针 32/32。
2. **pytest `--basetemp` 父目录不存在**（`_pytest_tmp` 未建，pytest 只在 tmp_path 首用时懒建且不递归）→ 基线族套件首跑 **1 error**（fixture 建目录失败）混入结果；建目录后重跑得干净的 **16 failed / 7 passed**。error 那次的原始输出已被覆盖——**如实声明**，其可复核部分（FAILED 表 15 行）与重跑一致。
3. **PowerShell 输出字节域**：`Out-File -Encoding utf8` 带 **UTF-8 BOM**、`*>` 写 **UTF-16LE（0xFF）** → invariants 两度崩在解码（`JSONDecodeError: Unexpected UTF-8 BOM`、`UnicodeDecodeError: 0xff`）；改 `utf-8-sig` + BOM 探测解码后 33/33。**这是本项目「判据必须匹配被比对量字节域」教训（T1-10 F 段 CRLF 同族）在读取侧的又一次复现**。
4. **r1 门 rc=1 属既有状态**（基线同样 rc=1、逐字段相等）：r1 期望 `W1.union_seconds=2220` 已被缺陷② 的追加式 provenance 取代（`expected_superseded.old=2220`），**非本卡回归**。

## 8. 边界（实测）

源树写入 **0**（22 pin 跑后复核全等，`evidence/boundary_check.txt`）；**git 命令 0**；**删除 0**（两树 scratch/中间产物均保留，
`worktree_before/` 基线快照与 `worktree/baseline/…pristine.py` 留档）；`oracle.md` **一字未改**（I-5：P4 的
「字段类型错误属 schema 级 rc 2 还是 per-case 拒绝」**仍待 reviewer**——本卡按返修块指定的 GREEN 语义
（与相邻标量校验同语义 = per-case 拒绝）执行，不构成 oracle 裁定）；**未代签、未晋升、未改任何 status**。

## 9. 关键指纹

| 对象 | sha256 |
|---|---|
| 基线 SUT（r2） | `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` |
| **修复后 SUT** | **`064e5381444d35a8ab1184d6c8d2eaa839a40f96c704ae7995fa3b660c7e273d`** |
| **changes.diff**（+229 −4，11534 B） | **`625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac`** |
| 新增负例族测试文件 | `316e369c9afc9d8df04a425945b97e41378e87f3ac17c721d0ab9ddf90904bfd` |
| MUT-G4（reviewer 备选单独应用）变体 | `4787e3f9b2d0a317ed249507e6b79eec86de3897673bd30523ac9eeae4fba8f2` |
| r2 报告字节（before==after） | `beb06495fcd93b2c4317428beaf282632169685d009165639bcc82b4732a1c79` |
| 修复源载体（M-T-REVIEW t1_review_flips.md） | `90bcefb9aadfe098dee1f16802bdf0af9ac7af9b2d74b21cc10a45e07b26c33b` |
