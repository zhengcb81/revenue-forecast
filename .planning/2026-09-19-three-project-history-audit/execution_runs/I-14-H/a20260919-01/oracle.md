# I-14-H oracle.md — natural_window.py 两个产品级缺陷（oracle 侧证据）

attempt：`execution_runs/I-14-H/a20260919-01`。本卡 oracle 侧：缺陷各有可失败用例
（RED→GREEN）+ 冻结期望更正以追加式 provenance 留痕。**status=review_pending，未自签。**

## 1. SUT 身份与生产树搜索结论

- 生产树搜索：`revenue-forecast/scripts/`（29 个 .py）与 `filing-fetch/scripts/`（2 个 .py）
  均**无** `natural_window.py`（内容 grep "natural_window" 零命中）。与 I-14-B 一致：
  SUT 是 attempt-local 隔离副本，生产树只读未动。
- 锚点 = I-14-B `iso/natural_window.py`（`SUT_VERSION="i14b-after-2"`，已含 J16/J15 修复）。
  本 attempt 三份字节验证副本（本轮运行前后 sha256 不变）：

| 副本 | sha256 | 角色 |
|---|---|---|
| `iso/natural_window.py` | `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` | 修复后工作副本（GREEN 被测物） |
| `before/natural_window.i14b-after-2.py` | `7fff6f0c…`（同上） | 修复后字节验证 pre-image |
| `before/natural_window.r1sut.py` | `495a44111a854bd5b76d39aeae91d11ab789fe48bb8bcbc9ae3af4b87d8c5b95` | 缺陷版 r1 修订（RED 被测物，= I-14-B reviewer 核验过的 r1） |

## 2. 两个缺陷（r1sut 代码位置）

1. **缺陷① `claim.basis` 无枚举校验**：`before/natural_window.r1sut.py:157-178`
   的 if/elif 分发对未登记 basis（`''`/`null`/缺键/`'wall_clock'`/容器）全部落到
   `allowed=None` ⇒ 无任何 refusal ⇒ J1/J2/J3/J11 整段被跳过 ⇒ **claim 被 accept**。
   修复形态（I-14-B r2 已落）：`BASIS_REGISTRY` 封闭枚举
   `{sample_span, command_total, observation_plus_quick_check, sum_of_windows, union_of_windows}`；
   未登记/空串/`null`/缺键一律 `R-BASIS-UNKNOWN`（`iso/natural_window.py:60-66, 199-203`）。
2. **缺陷② quick_check 计入自然观察时长**：`before/natural_window.r1sut.py:143-144`
   把 `(qc_started, qc_finished)` 追加进观察区间 ⇒ `union_of_windows`/`sum_of_windows`
   量得 **2220**（37 min）而非 **1740**（29 min）⇒ 不诚实的 2220 被 accept、
   诚实的 1740 被 reject（**方向倒置**）。修复形态：观察区间只含观察阶段
   （无 `windows[]` 时 `intervals=[(started_at, observation_finished_at)]`，quick_check
   永不进入，`iso/natural_window.py:174-182`）+ J15（声明窗覆盖 quick_check 即拒，`:163-172`）。

W1 算术（oracle 断言原文）：观测 00:00–00:29 = **1740 s**；quick_check 00:29–00:37 =
**480 s**；命令总耗时 00:00–00:37 = **2220 s**。1740+480=2220 的数值巧合正是叠加法的诱因。
本卡只验证计时算法，不构成真实观察资格。

## 3. oracle 材料（复用前次冻结，本轮逐字节复核未变）

| 文件 | sha256 | 说明 |
|---|---|---|
| `harness/cases.json`（r1 pre-image） | `5d8c459277da88b8361b520bee1424f079dc1d9c08744433cae0d30cdbb67d64` | = I-14-B r1 34-case 冻结用例 |
| `harness/frozen_expectations.json`（r1 pre-image） | `3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b` | 含被更正的 `expected.W1.computed.union_seconds=2220` |
| `harness/cases.i14h.json` | `40260c2425cbe4e708f36c294fa07fe01ac608b3c13bd1a4d3eafddd9762aeda` | 14 case = W1+C2 逐字携带 + H1–H12（W1 事实上每次只变 claim.basis 一个字段） |
| `harness/frozen_expectations.i14h.json` | `bffb11c2727d2227f3b1c345577f9acb7aeb2bae03949bad06741d990164d17a` | 更正后期望 + 追加式 provenance |
| `evidence/freeze_instant.json` | `4703a6c4ca86353d63b06875e6f9f5d4608a7fcedbc8d92a7a7bd81984f05118` | 冻结时刻 2026-09-21T18:39:46Z，**先于任何 SUT 运行** |

冻结材料由 `harness/build_cases_i14h.py`（`c40fac28a3235a7151a01e6e54ca62bd7ec6d01e629186a28788692cca5aecdf`）
在冻结时刻机械合成，**从不调用 SUT**；每个期望值或逐字携带自 r1 pre-image，或按卡片
规定的修复语义 + 手算导出（1740/480/2220）。H1–H12 的期望即本卡缺陷的裁决书：
H1–H6 `R-BASIS-UNKNOWN`、H7 负对照 `R-TOTAL-AS-OBS`、H8 诚实 1740 accept、
H9/H10 不诚实 2220 reject、H11/H12 J15 改名变体 `R-QC-IN-OBS`。

## 4. 期望更正（W1，追加式 provenance，I-14-B oracle.md §11.4 同形态）

- 旧值 **2220**（并集含 quick_check）→ 新值 **1740**（观察区间口径）；另新增锚定断言
  `sum_seconds=1740`、`observation_interval_count=1`、`quick_check_overlap_seconds=0`、
  `quick_check_in_observation_intervals=false`。
- 原因：**该冻结值本身就是缺陷②的一部分**（2220 被接受而诚实的 1740 被拒，方向倒置）。
  旧值**保留**于 `frozen_expectations.i14h.json` 的 `expected_superseded` 与
  `errata[0]`（含 old/new/`pre_image_sha256`/`changed_at_utc`/原因），并附 r1→i14h
  期望映射的机械 unified diff（`errata[0].diff_from_r1_expected_map`）。
  **从未"没有过 2220"；r1 两份冻结正文逐字节未动。**

## 5. 时序声明（卡片第 5 条）

与 I-14-B r2 相同，本卡沿用"先改实现、后冻结期望"的次序（实现 = I-14-B r2 的
J16/J15，2026-09-20 落地；期望 = 2026-09-21 冻结）。如实声明的独立性证明：

1. 期望在冻结时刻**先于本轮任何 SUT 运行**（freeze_instant.json）；
2. 期望值由 `build_cases_i14h.py` 从 r1 pre-image + 卡片语义 + 手算合成，从不调用 SUT；
3. `before/cmd-PYTEST-red-r1sut` 用**字节验证的缺陷版 r1**独立复现两个缺陷
   （9 个缺陷用例全部 FAIL，含 r1 实测 `union_seconds=2220.0`）——期望若"照修好的
   实现写"，这些 RED 用例不可能在 r1 上以恰好相反的裁决失败。

## 6. RED→GREEN 运行记录（本轮唯一新增执行）

测试文件：`harness/test_i14h_natural_window.py`（190 行，12 个用例；SUT 由 `I14H_SUT`
环境变量选择，缺省 = 修复后工作副本）。运行命令（未建任何 venv，直接 Miniconda）：

```
C:\Miniconda\python.exe -X utf8 -B -m pytest -p no:cacheprovider --basetemp harness\scratch\pytest-i14h-green -v harness\test_i14h_natural_window.py     # GREEN, rc 0
C:\Miniconda\python.exe -X utf8 -B -m pytest -p no:cacheprovider --basetemp harness\scratch\pytest-i14h-red   -v harness\test_i14h_natural_window.py     # RED, I14H_SUT=before\natural_window.r1sut.py, rc 1
```

| 运行 | SUT | 结果 | rc | 证据 |
|---|---|---|---|---|
| GREEN | `iso/natural_window.py`（i14b-after-2） | **11 passed, 1 xfailed** | 0 | `after/cmd-PYTEST-green/stdout.txt`（`1329f50122cbd03deafb62edc7d259b49c294407153627f127f90bdfa869ae6f`） |
| RED | `before/natural_window.r1sut.py`（r1） | **9 failed, 2 passed, 1 xfailed** | 1（预期） | `before/cmd-PYTEST-red-r1sut/stdout.txt`（`0342c075eca1ae6cbfbc8f14b4abd7b3e2f68ea7ad9faf2f478ee2d71a29b936`） |

RED 明细：缺陷① 4 用例（`wall_clock`/`''`/`null`/缺键均被 r1 accept）+ 缺陷② 5 用例
（观察区间含 qc 得 2220.0；诚实 1740 被拒；不诚实 2220 union/sum 被 accept；改名窗变体
被 accept）全部 FAIL。两用对照在两个修订上均 PASS（W1 sample_span 基线、
`command_total` 已登记 basis 仍按 `R-TOTAL-AS-OBS` 实质裁决）——证明套件本身健全、
修复不是"一律拒绝"。测试文件 sha256：
`147cdc1c589bef458ba2d741568f22bfd56600cefcfc7757d030accc4630f935`。

## 7. 已知残留（记录，不在本卡修）

**容器 basis 批崩溃（reviewer P4 / T1-10 P-3）**：`i14b-after-2` 对 list/dict basis 在
`basis not in BASIS_REGISTRY` 处抛 `TypeError`（unhashable）⇒ 整批 rc 4 崩溃，而非逐 case
拒绝。r1 则静默 accept。测试文件以 `xfail` 用例 `test_container_basis_refused_per_case`
记录该残留；逐 case `R-BASIS-UNKNOWN` 的要求已冻结于 H5/H6 期望，留给下一个实现修卡。
因该残留，`run_cases.py` 全 14-case 门（会因单条容器 basis 崩掉整批）推迟到残留修复后运行。

## 8. 退出判据映射与清理声明

- 缺陷① 可失败用例：4 个 d1 用例 RED→GREEN ✓；缺陷② 可失败用例：5 个 d2 用例 RED→GREEN ✓
- 期望更正追加式留痕：§4（expected_superseded + errata + 机械 diff）✓
- 本轮**未创建 venv**（直接 `C:\Miniconda\python.exe`）；前次失败尝试遗留的
  `iso/venv/` 已于本轮删除（仅含 pip venv 文件，删除前后 `iso/natural_window.py`
  sha256 不变）；无 `__pycache__` 落盘（`-B` + `-p no:cacheprovider`）。
- 生产三仓只读未动；`SUT_VERSION` 未改；冻结正文未回改。
