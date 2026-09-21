# I-14-H 独立复核（independent reviewer）

- 卡片：I-14-H — `natural_window.py` 两个产品级缺陷（oracle 侧：可失败用例 + 追加式期望更正）
- attempt：`execution_runs/I-14-H/a20260919-01`
- 复核者：独立 reviewer（非实现者）；复核时实现者 `status=review_pending`、`implementer_signed=false`（自签禁止，符合规程）
- 边界：**只读**。本轮未写入 attempt 目录、未触碰任何生产树；所有探针输出写入 `%TEMP%\i14h_rev\`
- 解释器：`C:\Miniconda\python.exe`（Python 3.13.9 + pytest 9.1.1）

## 结论：ACCEPT（条件式）

两个声明的缺陷各自具备**可失败用例**，RED/GREEN 双向在本轮独立复现；冻结 oracle 材料逐字节未变；W1 更正形式合法。
条件：**残留（容器 basis 批崩溃）必须立卡修复，且修复后必须补跑全 14-case `run_cases.py` 门**——该门从未通过，本卡的端到端 oracle 一致性尚未闭环。
残留本身**不**动摇两个声明缺陷的裁决（理由见 §5）。

---

## 1. SUT 位置主张 —— 已独立验证（属实）

对本机两棵生产树做了**文件名搜索 + 内容 grep** 两种方式的独立复核：

| 生产树 | `natural_window*` 文件名命中 | 内容 grep `natural_window` | .py 数 |
|---|---|---|---|
| `revenue-forecast\scripts\` | 0（仅在 `.planning\...\execution_runs` 内命中，非生产） | **0** | 43 |
| `filing-fetch\scripts\` | **0** | **0** | 2 |

⇒ 生产树中确实不存在 `natural_window.py`；SUT 是 attempt-local 隔离副本。**主张 1 成立。**
（oracle.md 称 revenue-forecast/scripts 有 "29 个 .py"，实测 43 个——仅计数口径差异，不影响结论。）

## 2. SHA-256 逐项复核 —— 全部与主张一致

| 文件 | 实测 sha256 | 主张 | |
|---|---|---|---|
| `iso/natural_window.py`（GREEN SUT） | `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` | `7fff6f0c…` | ✓ |
| `before/natural_window.i14b-after-2.py` | `7fff6f0c…`（与 iso **字节相同**） | 同 | ✓ |
| `before/natural_window.r1sut.py`（RED SUT） | `495a44111a854bd5b76d39aeae91d11ab789fe48bb8bcbc9ae3af4b87d8c5b95` | `495a4411…` | ✓ |
| `harness/cases.i14h.json` | `40260c2425cbe4e708f36c294fa07fe01ac608b3c13bd1a4d3eafddd9762aeda` | `40260c24…` | ✓ |
| `harness/frozen_expectations.i14h.json` | `bffb11c2727d2227f3b1c345577f9acb7aeb2bae03949bad06741d990164d17a` | `bffb11c2…` | ✓ |
| `harness/test_i14h_natural_window.py` | `147cdc1c589bef458ba2d741568f22bfd56600cefcfc7757d030accc4630f935` | `147cdc1c…` | ✓ |
| `harness/cases.json`（r1 pre-image） | `5d8c459277da88b8361b520bee1424f079dc1d9c08744433cae0d30cdbb67d64` | 同 | ✓ |
| `harness/frozen_expectations.json`（r1 pre-image） | `3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b` | 同 | ✓ |
| `evidence/freeze_instant.json` | `4703a6c4ca86353d63b06875e6f9f5d4608a7fcedbc8d92a7a7bd81984f05118` | 同 | ✓ |
| `before/cmd-PYTEST-red-r1sut/stdout.txt` | `0342c075eca1ae6cbfbc8f14b4abd7b3e2f68ea7ad9faf2f478ee2d71a29b936` | 同 | ✓ |
| `after/cmd-PYTEST-green/stdout.txt` | `1329f50122cbd03deafb62edc7d259b49c294407153627f127f90bdfa869ae6f` | 同 | ✓ |

**r1 冻结正文未回改的直接证据**：`harness/frozen_expectations.json` 的
`expected.W1.computed.union_seconds` 仍为 **2220**（现读 `2220`，非 1740）——更正只发生在
i14h 新文件里，pre-image 原样保留。

## 3. 双臂独立重跑 —— 与主张逐项吻合

| 臂 | SUT | 本轮实测 | rc | 主张 | |
|---|---|---|---|---|---|
| GREEN | `iso/natural_window.py` | **11 passed, 1 xfailed** | **0** | 11P/1X, rc 0 | ✓ |
| RED | `I14H_SUT=before\natural_window.r1sut.py` | **9 failed, 2 passed, 1 xfailed** | **1** | 9F/2P/1X, rc 1 | ✓ |

RED 失败构成与主张**完全一致**：
- 缺陷① 4 例：`wall_clock` / `''` / `null` / 缺键 → 全部 FAIL（r1 静默 accept）
- 缺陷② 5 例：`observation_intervals_contain_observation_only`、诚实 1740 union、不诚实 2220 union、
  不诚实 2220 sum、改名窗变体 → 全部 FAIL
- RED 输出中实测 **`assert 2220.0 == 1740`**（r1 的 `union_seconds` = **2220.0**）——**主张 3 的数值证据成立**
- 2 个 PASSED 恰为两用对照（W1 `sample_span` 基线 + `command_total` 已登记 basis 的实质裁决）⇒ 套件在两个修订上均非"一律拒绝/一律接受"，**套件本身健全**（这正是"修复不是把一切都拒掉"的阴性对照）

**实现侧定位独立核对**：`iso` vs `r1sut` 的 unified diff = 18 hunks / 84 行，且正是两处声明修复——
`BASIS_REGISTRY` 封闭枚举（`iso:60-66`）+ J16（`iso:202-203`）+ J15 重叠量测（`iso:163-172`）+
观察区间只含观察阶段（`iso:174-182`）。`SUT_VERSION` 分别为 `i14b-after-1`（r1sut）/ `i14b-after-2`（iso）。

## 4. W1 2220→1740 追加式更正 —— 形式合法

与 I-14-B `oracle.md` **§11.4** 同形态，逐项对照成立：

| §11.4 要求 | 本卡 `frozen_expectations.i14h.json` | |
|---|---|---|
| 旧值保留于 `expected_superseded`（含 old/new/`pre_image_sha256`/时刻/原因） | `expected_superseded.W1["computed.union_seconds"]` = old **2220** / new **1740** / `pre_image_sha256` `3ba2bb17…` / `changed_at_utc` `2026-09-21T18:39:46.645567Z` / reason | ✓ |
| 附 r1→i14h 期望映射机械 unified diff（`errata[0].diff_from_r1_expected_map`） | `errata[0]`（id `ERR-I14H-01`）含 `diff_from_r1_expected_map`（`@@ -8,7 +8,11 @@` 将 `union_seconds: 2220` → `1740` 并追加 4 条锚定断言） | ✓ |
| 新增锚定断言 | `sum_seconds=1740`、`observation_interval_count=1`、`quick_check_overlap_seconds=0`、`quick_check_in_observation_intervals=false` —— 已实测全部在 GREEN 中通过 | ✓ |
| "从未没有过 2220" | pre-image 文件 sha 未变且正文仍为 2220（§2 已证） | ✓ |

`pre_image_sha256` 指向的正是现存 r1 文件实测哈希 ⇒ 更正 provenance 可机检、非自述。**合法。**

## 5. 残留（容器 basis 批崩溃）—— 裁决：**正确推迟，但附带强制收尾条件**

**本轮独立复现（不是照抄 oracle）**：

1. 直接对被测模块喂冻结用例 H5/H6：
   - `iso`（修复版）：H5 `basis=['union_of_windows']` → `TypeError: unhashable type: 'list'`；
     H6 `basis={'kind':...}` → `TypeError: unhashable type: 'dict'`
   - `r1sut`：H5/H6 均 `verdict=accept_claim, refusals=[]`（**静默越权**）
2. 全 14-case `run_cases.py` 门：`iso` → SUT 子进程 **`raw_returncode=4`**，CLI 输出
   `{"ok": false, "error": "internal_error", "detail": "unhashable type: 'list'"}`，`sut_report.json` 未生成、整批中止。
3. **精确崩溃行 = `iso/natural_window.py:202` `if basis not in BASIS_REGISTRY:  # J16 / P1`**
   （带 traceback 的在进程内探针确认）。实现者把崩溃归因于该行是**准确的**——`list not in set`
   确实触发 hash 求值。（此点我最初怀疑归因有误，实测证明实现者正确。）

**为什么"推迟"是对的：**

- 两个被裁缺陷与残留**正交**：缺陷①=未登记 basis 被 accept；缺陷②=quick_check 计入时长。
  容器 basis 是**未声明**的第三个问题，且不是本卡两条判据的任何一条。
- 残留**不是本卡引入**：`iso` 与 `before/i14b-after-2.py` 字节相同（`7fff6f0c…`），
  该副本来自 I-14-B 锚点，"检查的是未声明的容器类型"这一脆弱性随该副本一起继承。
- 失败方向是**fail-closed**：崩溃 ≠ 越权接受。它不会让不诚实主张通过，因此不是正确性漏洞，
  而是健壮性/可用性缺陷（严重度低于两条已裁缺陷）。
- 残留已被**如实记录且未自签**：oracle.md §7、handoff `open_questions[0]` 均显式声明，
  并冻结为 H5/H6 期望 + 1 个 xfail 用例，留给后续实现修卡——符合"不掩盖已知缺口"。

**为什么必须附带条件（本卡不能无条件通过）：**

- **全 14-case 端到端门从未通过**。这是对冻结期望的**最强**验收证据，而 H5/H6 的冻结期望
  （逐 case `R-BASIS-UNKNOWN`）**当前实现无法满足**。`xfail` 只记录"现在过不了"，不能替代通过。
- 因此本卡目前的通过证据实际只有 **12-case pytest 套件**（外加下面 §6 我补跑的 12-case 门）。
- **修复残留时必须一并**：修 `iso:202` 的 hash 安全判据（例如先 `isinstance(basis, str)`），
  移除 xfail，**补跑全 14-case 门至 rc 0**，并把该 `cases_report.json` 落到 attempt 证据目录。

⇒ 残留**不**使本卡验收失效（两个声明的缺陷成立且可复现），但使"本卡已完成"**不得**被表述为
端到端 oracle 一致性已闭环。

## 6. 复核者补强证据（超出实现者提交范围）

实现者因残留**推迟**了 `run_cases.py` 门，导致 attempt 中**没有**任何 `cases_report.json`。
为把"逐 case 与冻结期望一致"钉死，我用**未修改的** `run_cases.py`（`f2a07d0b…`）+ **未修改的**
i14h 冻结期望，在 `%TEMP%` 下跑了一次过滤掉 H5/H6 的 12-case 门（探针产物全部落在临时目录，
attempt 记录保持原样）：

| 门 | SUT | 结果 |
|---|---|---|
| 12-case（W1,H1–H4,H7–H12,C2） | `iso`（修复版） | **`ok: true`, mismatch_count 0, accepted_ineligible 0, SUT rc 0** ✓ |
| 12-case 同上 | `r1sut` | `ok false`, **27 mismatches**, **accepted_ineligible = H1,H2,H3,H4,H9,H10,H11** |
| 全 14-case | `iso` | SUT rc 4（残留）；门 ok false |
| 全 14-case | `r1sut` | `ok false`, 31 mismatches, **accepted_ineligible 9**（含 H5/H6 —— r1 静默接受容器 basis） |

价值有两点：
1. 修复版在 **12/14 冻结用例上逐字段零失配**（含被更正的 W1 全部 5 条锚定断言 + H12 双拒绝码），
   远超 pytest 套件 12 例的覆盖；
2. r1 的 `accepted_ineligible` **恰好**是两条缺陷的越权集合 —— 这独立证明期望**不是**"照着修好的
   实现写"的（否则 r1 不会以恰好相反的裁决失败），即 oracle.md §5 的独立性抗辩成立。

## 7. 清理与只读声明 —— 已核

- `iso/venv` **不存在**（`Test-Path` = False）；`iso/` 仅含 `natural_window.py`。
- attempt 内**无** `__pycache__` 残留。
- `-B` + `-p no:cacheprovider` 与声明一致；`harness/scratch/**`（basetemp）已被清理，
  属声明内的一次性产物。
- 本轮复核**未**写入 attempt 目录与生产树；所有探针产物位于 `%TEMP%\i14h_rev\`。

**§7 补充：生产树只读 —— git 机检证明（强于实现者自述）**

两棵生产树**都是 git 仓库**（`revenue-forecast\.git` / `filing-fetch\.git` 均存在），因此可做
前后态比对：

| 检查 | 结果 |
|---|---|
| `git ls-files -- scripts`（revenue-forecast） | **43** 个受版本控制文件 ⇒ `scripts/` 确在版本控制内，非游离目录 |
| `git status --porcelain -- scripts`（revenue-forecast） | **空** ⇒ `scripts/` 无任何改动、无未跟踪文件 |
| `git status --porcelain`（filing-fetch，全仓） | **空** ⇒ 整个 filing-fetch 工作树干净 |
| `git log --all --name-only -- "*natural_window*"`（两仓全历史） | 命中**仅**位于 `.planning\...\execution_runs\I-14-{B,H}\`；**无任何提交**触及 `scripts/` 下的 `natural_window`；filing-fetch 全历史 0 命中 |

⇒ "SUT 不在生产树、生产树未被写入"从"强推断"升级为**可机检证明**。
（附注：`revenue-forecast` 全仓 `git status` 另有 I-14-D / I-08-C / `assurance/unified_completion/manifests/plan_inputs.json`
等他卡改动，均与 I-14-H 及 `scripts/` 无关。历史提交 `cc78c529` 显示 I-14-B 的
`harness/archive/natural_window.after-r1.py` = `495a4411…`，与 `before/natural_window.r1sut.py` 的
归档哈希声明一致；`iso` 内注明 "r1 is preserved byte-identically at harness/archive/natural_window.after-r1.py"，
该声明的归档哈希与实测 `495a4411…` 自洽。）

---

## 未验证 / 存疑清单（unverified list）

1. **`iso/venv/` 曾被删除** —— 现存事实只有"当前不存在"。删除动作本身、以及"删除前后
   `iso/natural_window.py` 哈希不变"无法事后验证（无删除前快照/日志）。当前状态与声明一致。
2. **生产树"未被写入"** —— 已从"强推断"升级为 **git 机检证明**（见 §7 补充）。唯一残留的不确定性：
   本机沙箱对若干**无关**目录（`.tmp-zr408-*`、`reviews/**/scratch`）报 Permission denied，
   使 `git status` 无法枚举这些路径；但 `scripts/` 本身可完整枚举，结论不受影响。
3. **`harness/scratch/pytest-i14h-{green,red}/` 已被删除** —— 我无法核对实现者当时那两次运行的
   原始 basetemp。缓解：本轮重跑得到**完全相同**的计数（11P/1X、9F/2P/1X）与相同的
   `2220.0 == 1740` 断言失败，故结论不受影响。
4. **`sum_used_for_natural_duration` 与 `quick_check_in_observation_intervals` 是硬编码字面量**
   （`iso:241`、`iso:248` 恒为 `False`），并非由区间内容计算得出。`run_cases.py` 的
   `REQUIRED_KEYS` 形状门与 `test_d2_observation_intervals_contain_observation_only` 对这两个键的
   断言因此**恒真**、不承担判别力；缺陷②的真正判别力来自 `union_seconds`/`sum_seconds`/
   `observation_interval_count`/`quick_check_overlap_seconds` 四个**实算**字段（已实测生效）。
   建议后续在残留修卡中顺手把这两个字段改为派生值，避免"形状门"给出虚假安全感。
   —— 这不影响本卡裁决，但属未被实现者披露的弱化点。
5. **H12（改名窗 + 诚实 1740 声称）无 pytest 对应用例**：pytest 的改名窗变体只覆盖 H11 形态
   （主张 2220 → 单拒绝码 `R-QC-IN-OBS`）；H12 的双拒绝码
   `['R-CLAIM-EXCEEDS','R-QC-IN-OBS']` 仅由冻结门覆盖（我补跑的 12-case 门已实测通过）。
   覆盖缺口存在但已被冻结门弥补。
6. **真实观察资格 / 真实 UI 即时性 / SLO / accuracy** —— 沿用 I-14-B 的 NOT GRANTED，
   本卡全部用例为 `SYNTHETIC-TIMER-ONLY` 合成时间输入，本轮未新增验证，也不应被解读为已获得。

## 建议的 status 决定

`ACCEPT`（两个缺陷的 oracle 侧成立、红绿双向可复现、更正形式合法）**且** 附强制后续项：
容器 basis 逐 case 拒绝 → 立实现修卡 → 解除 xfail → **补跑全 14-case 门至 rc 0** 并落盘
`cases_report.json`；在补跑完成前，本卡的验收陈述须限定为"12/14 冻结用例 + 12 例 pytest 套件"。
