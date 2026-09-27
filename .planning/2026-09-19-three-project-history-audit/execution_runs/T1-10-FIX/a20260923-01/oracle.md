# T1-10-FIX oracle（**运行前冻结** · 2026-09-23）

卡：**T1-10-FIX** / attempt `a20260923-01`。
修复源（权威）：**M-T-REVIEW 的 T1-10 返修块** ——
`execution_runs/M-T-REVIEW/a20260923-01/landing_package/t1_review_flips.md` L28–40（sha256 `90bcefb9…`），
载体行 `reviews/T1_rulings.md` L18 + `acceptance_rulings.md` L87。
**范围冻结**：只修**缺陷①**（claim.basis 枚举校验非全函数）+ fabricated-green 负控；
缺陷②（union/sum 计入 quick_check）及其追加式 provenance **维持接受、字节不触**。
Owner order：「发现的缺陷都要全部修复」——本卡对**缺陷①的全部已发现入口**闭合（见 §2 入口清单），
对**范围外新发现**（§7）只登记移交，不扩刀。

本文件在**任何探针运行之前**写成；RED/GREEN/MUTATION/负控的期望值先于观测冻结。
SUT：`worktree/i14b/iso/natural_window.py`（隔离副本，基线 sha256 `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` = I-14-B r2）。
源树 **READ-ONLY**；一切观测走隔离副本，交付走 `changes.diff`（零生产合并）。

---

## 1. 冻结的畸形 basis 负例族（malformed-case list）

探针形状逐字取自 **T1-10 的块**：`T1-10/a20260920-01/scripts/verify_t1_10.py` L99–116（`GOOD_FIELDS`/`window_case`）
与 L171–201（basis sweep 八探针）；`t1_10_defect_verification.json` → `A_basis_shape_sweep` 实测行
（`list_of_registered`/`dict_object`/`tuple_like_via_json` rc=4 无报告；标量五探针 rc=0）。
全部 case 为 `window_accounting`、W1 良构计时字段、`frozen_now=2026-09-20T02:56:38Z`、
claim 秒数 1740（= union_of_windows 良构主张）。**只动 claim/claim.basis，不动任何计时字段。**

| id | 形状类 | tamper | RED 期望（基线 r2 SUT） | GREEN 期望（修复后 SUT） |
|---|---|---|---|---|
| **B1** | basis 类型不符：JSON **数组**（T1-10 `list_of_registered`） | `claim.basis=["union_of_windows"]` | **rc=4、无报告、stdout `internal_error: unhashable type: 'list'`、全批 0 裁决** | rc=0、报告写出、`reject_claim`+`["R-BASIS-UNKNOWN"]`、`basis_registered=false`、全批裁决 |
| **B2** | basis 类型不符：JSON **对象**（T1-10 `dict_object`） | `claim.basis={"name":"union_of_windows"}` | **rc=4、无报告、`unhashable type: 'dict'`、全批 0 裁决** | 同 B1 的干净拒绝 |
| **B3** | basis **载体**类型不符：`claim` 是 JSON 数组（P4「claim 为 list ⇒ rc 4」；basis 不可读) | `claim=["union_of_windows"]` | **rc=4、无报告、`'list' object has no attribute 'get'`、全批 0 裁决** | rc=0、`reject_claim`+`["R-BASIS-UNKNOWN"]`、`computed.basis=null`、`basis_registered=false` |
| **B4** | missing-required：claim 缺 `basis` 键（oracle §11.5 X3 形状） | `claim` 无 basis | rc=0 `reject`+`R-BASIS-UNKNOWN` | **与基线逐字节相同** |
| **B5** | unknown-key：claim 带无关键 + 合法 basis | `claim={"basis":"union_of_windows","unrelated":"x"}` 1740 | rc=0 `accept_claim` | **逐字节相同** |
| **B6** | 对照：登记值 | `basis="union_of_windows"` 1740 | rc=0 `accept_claim` | **逐字节相同** |
| **B7** | 未登记串（T1-10 `unregistered_str`） | `basis="wall_clock"` | rc=0 `reject`+`R-BASIS-UNKNOWN` | **逐字节相同** |
| **B8** | null（T1-10 `null`） | `basis=null` | rc=0 reject | **逐字节相同** |
| **B9** | 标量非串（T1-10 `scalar_non_str`） | `basis=5` | rc=0 reject | **逐字节相同** |
| **B10** | 空串（T1-10 `empty_str`） | `basis=""` | rc=0 reject | **逐字节相同** |
| **B11** | 嵌套容器 | `basis=[["x"]]` | **rc=4、`unhashable type: 'list'`** | 同 B1 的干净拒绝 |
| **B12a/b/c** | 载体真值非对象：`claim="s"` / `claim=5` / `claim=true` | — | **rc=4、`'str'/'int'/'bool' object has no attribute 'get'`** | 同 B3 的干净拒绝 |

- **≥3 个会崩的形状冻结为：B1、B2、B3（另加 B11、B12a/b/c 共 6 个）**；
  B4–B10 是**必须保持不变**的邻域（missing/unknown/标量语义已由 oracle §11.3 冻结）。
- **崩溃 = 「J16 裁决机关失灵」的观测面**：(a) CLI rc∈{4}、`internal_error`、**报告未写出、全批 0 裁决**；
  (b) 直调 `classify()` 抛**未捕获 traceback**（`TypeError`/`AttributeError`）。两者都须捕获。

## 2. 冻结：缺陷① 的**全部入口**（"补全覆盖至全部入口" 的判定对象）

`iso/natural_window.py` 中读取/消费 `claim.basis` 的全部落点（grep `basis` 冻结如下）：

| # | 行 | 入口 | 基线行为（畸形输入） |
|---|---|---|---|
| E1 | `:199` | 载体读取 `(fields.get("_claim") or {}).get("basis")` | `_claim` 为真值非对象 → **AttributeError 崩**（B3/B12） |
| E2 | `:202` | J16 守卫 `if basis not in BASIS_REGISTRY:` | 不可哈希 basis → **TypeError 崩**（B1/B2/B11） |
| E3 | `:247` | 报告字段 `"basis_registered": basis in BASIS_REGISTRY` | 不可哈希 basis → **TypeError 崩**（即使 E2 被单独补好也会在此崩） |

**闭合判据**：E1/E2/E3 全部对任意 JSON 值**全函数**（永不抛）；畸形 → 与邻域标量**同一拒绝语义**
（`reject_claim` + `R-BASIS-UNKNOWN` + `basis_registered=false`，拒绝码引用 oracle §11.3 L227 既有文档，**不新增 R-\* 码**）。
**已知不足（如实冻结）**：reviewer P4 的「isinstance 守卫在 J16 前」最小修法**只补 E2**——E3 的 set 成员测试仍会崩；
本卡取 reviewer 首选修法（`BASIS_REGISTRY` set→tuple，`review.md:353`）一次覆盖 E2+E3，另补 E1 载体守卫。

## 3. 冻结不变量（invariants）

- **I-1 缺陷② 不触**：`changes.diff` 只含 `iso/natural_window.py` + 新增测试文件；
  **不触** `frozen_expectations*.json` / `cases*.json` / `oracle.md` / `run_cases.py` / `mutate.r2.py` / 既有测试（sha=pin 值）；
  `expected_superseded.W1…old==2220` 修复后仍可读；diff 变更行 ∩ `:174–:197`（quick_check 区间/J15/J6 计算区）= ∅。
- **I-2 良构输入行为逐字节相同**：对 `harness/cases.r2.json`（34 case）与 `harness/cases.json`（20 case），
  基线 SUT 与修复 SUT 的 `--report` 输出 **sha256 相等**（逐字节）；且 runner 门两版均 rc=0、mismatch=0、34/34。
- **I-3 rc 冻结域**：SUT rc ∈ **{0, 2, 4}**（oracle §8-errata L188）；畸形 basis 的 GREEN rc **=0**（全部裁决、报告写出）；
  RED rc=4 属既有域但是「剥夺裁决」形态，本卡判为缺陷① 的证据而非合规态。
- **I-4 拒绝语义等同邻域**：B1/B2/B3/B11/B12 的 refusals 集合 == B7–B10 的 refusals 集合 == `{R-BASIS-UNKNOWN}`。
- **I-5 不自填 oracle**：`oracle.md`（I-14-B）**一字不改**；P4 遗留的「字段类型错误属 schema 级 rc 2 还是
  per-case 拒绝」归属裁定**仍待 reviewer**（review.md:353 / T1-10 decision §7.1）——本卡按 M-T-REVIEW 返修块指定的
  GREEN 语义（与相邻标量校验同语义 = per-case 拒绝）执行，**不构成 oracle 裁定**。

## 4. 冻结：MUTATION 臂（非空洞性）

| 臂 | 变异（对**修复后** SUT 的 scratch 副本） | 期望 |
|---|---|---|
| **MUT-G1** | 修法①回退：`BASIS_REGISTRY = (…)` → `= {…}`（set） | B1/B2/B11 **崩溃回归**（rc=4/internal_error）→ 守卫承重 |
| **MUT-G2** | 修法②回退：载体守卫 → 原行 `(fields.get("_claim") or {}).get("basis")` | B3/B12 **崩溃回归**（rc=4）→ 守卫承重 |
| **MUT-G3** | 结构不变量：`mutate.r2.py:99` 锚行 `    if basis not in BASIS_REGISTRY:  # J16 / P1` 在修复后 SUT 中出现**恰好 1 次**（grep 计数） | J16 变异机关**未被修法破坏**；20 臂证明 before==after 全红 |

## 5. 冻结：fabricated-green 负控（T1-8 式，≥1 声明、双向）

T1-8 参照：`T1-8/a20260920-03` 毒化 **11 声明仍 rc=0 / 11-of-11 `PASS_rejected` = 伪造的绿**
（decision.md §2、`verify_t8_pre3.py` sha `0c23dc9c…`）。本面负控**至少同等强度**（毒化数 ≥11、逐条 raw 落盘）：

| 臂 | 毒化对象（隔离副本上的篡改） | 期望（**不得变绿**） |
|---|---|---|
| **NC-1 输入侧（claim 声明）** | cases.r2 副本中**全部 18 个 window case 的 `claim.basis` 毒化为 `["union_of_windows"]`**（容器 = 缺陷① 形状；18 ≥ 11） | SUT rc=0、**34/34 全裁决**（机关未被批量毒化炸毁）；runner **rc=1、ok=false**、mismatch ≥3（W1/W5/X5 声明 accept 实得 reject）——**非绿** |
| **NC-2 断言侧（expectation 声明）** | expectations 副本中**全部 18 个 window case 的声明 verdict 翻转**（accept↔reject；X1–X4 另清空 refusals 声明；18 ≥ 11） | runner **rc=1、ok=false**、18 个 window case_id **全部**入 mismatches——**非绿**（对照 T1-8 的 rc=0/11-11 绿） |
| **PC 正对照** | 无毒化原样跑 | runner rc=0、ok=true、mismatch=0（负控有区分度，非永红） |

## 6. 冻结：回归面（before == after）

| 面 | 命令载体 | 冻结判据 |
|---|---|---|
| r1 族测试 | `pytest harness/tests/test_i14b_natural_window.py` | before==after：failed=0（r1 oracle §11.6 记 32 passed，实测数如实记录） |
| r2 族测试 | `pytest harness/tests/test_i14b_natural_window_r2.py` | before==after：failed=0、passed 计数相等 |
| J16/20 臂变异机关 | `harness/mutate.r2.py --out …` | before==after：`mutation_count=20`、`all_mutants_red_again=true`、`all_expected_cases_red=true`，且 MUT-15 红案 = X1–X4 |
| 冻结 case 门 | `harness/run_cases.py --cases cases.r2.json --expectations frozen_expectations.r2.json` | before==after：rc=0、ok=true、mismatch=0、accepted_ineligible=0 |
| grep 面 | 固定锚行集（J16 守卫行、BASIS_REGISTRY 定义、`basis_registered` 行、MUT-15 锚、测试 `sorted(SUT.BASIS_REGISTRY)`） | 修复后全部在场；既有测试/runner/mutator 文件 sha == pin |
| 新负例族测试 | `harness/tests/test_i14b_natural_window_basis_total.py`（本卡新增，diff 内） | before（基线 SUT）：**RED**（TypeError traceback 落盘）；after：GREEN 全过 |

## 7. 范围外发现的登记位（只登记，不修——移交编排层按 owner order 立卡）

探针附带（与 basis 无关的同类非全函数，reviewer P4 部分点名）：E-adj-1 `clock_source` 的 `TRUSTED_CLOCKS`（set）成员测试（`:338`）遇容器崩；E-adj-2 日历 `claim.status` 读取（`:343`）载体真值非对象崩；E-adj-3 `windows/sampled_at/ledger.daily` 容器型（P4 已点名）；E-adj-4 时间戳畸形 `_parse`（schema 级 = **reviewer 归属**，I-5 不自填）。**实测行见 evidence/verification.json `adjacent_discovery`**；本卡不改。
