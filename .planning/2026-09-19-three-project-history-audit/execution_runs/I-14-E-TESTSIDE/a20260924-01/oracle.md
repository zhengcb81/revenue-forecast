# I-14-E-TESTSIDE oracle.md — 重启节点测试侧时序修法的**冻结判据**

attempt：`execution_runs/I-14-E-TESTSIDE/a20260924-01`（目录名沿用派单给定的 `a20260924-01`；
实际作业跨 09-24/09-25，两个时段的 mtime 分别保留、不改写）。
**冻结时刻：2026-09-25T20:40Z（UTC）** —— 先于本 attempt 的**任何一次** pytest 运行（红/绿/变异）
（`before/freeze_instant.json` 记录本文件 sha256）。

本卡是**施加卡**：只改测试侧时序、不动产品代码。`status=review_pending`，实现者不自签。
冻结后只允许**追加式** erratum（`oracle-addendum-*.md`）；上文一字不改。

---

## 1. SUT 身份与 iso 绑定（来源 `before/hashed_before.json`，copy 阶段零写源仓）

| 项 | 值 |
|---|---|
| 产品测试（真正的 SUT，**本卡唯一允许改动面**） | `iso/tests/contract/test_source_catalog_worker_bootstrap.py`，40868 B，sha256 `32515aa6…c005c1`（= 真仓同名文件，也 = 源卡 I-14-E binding 的 `CW_test_file` 同值） |
| 节点① `child_without_runtime` | `test_child_without_runtime_session_is_terminated_and_restarted`（893–917 行） |
| 节点② `logon_wrapper_quoted` | `test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths`（1039–1119 行）—— **本卡不施加，见 §2** |
| 真实启动器（只读） | `iso/scripts/source_catalog_worker.ps1` sha256 `5c12cd74…bc311`（= 源卡 anchor 同值）；看门狗在 `.ps1:351-373` |
| 登录包装器（只读） | `iso/scripts/source_catalog_worker_at_logon.ps1` sha256 `70b4d7d7…be5a1c` |
| iso 产品树 | `iso/src` 152 文件，manifest `34ee472e…92af` = 真仓 `CW/src` manifest（逐字节相同） |
| iso scripts | `iso/scripts` 135 文件，manifest `e7ccf6e3…847f` = 真仓 `CW/scripts` |
| iso tests（改动前） | `iso/tests` 348 文件，manifest `369aa19e…1c8e` = 真仓 `CW/tests`（拷贝忠实性已比对） |
| 真仓 HEAD | `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121`（branch `fcap`；`status --porcelain` 3 行，**拷贝前既有**，本卡未改） |
| 运行解释器 | `venv/Scripts/python.exe`（3.13.9；源卡 `I-14-E/a20260919-01/iso/venv` 的**字节副本**，避免对源卡 attempt 产生任何写入） |
| 树个数 | **单树**（CW_HEAD 副本）。树差异不是本卡对象——源卡 H2 已用 T0/T0b 字节相同对照证否，本卡不重做 |

**结构性前提（可证伪）**：节点①测试体不 import 任何 `company_wiki.*`；被启动的子进程是测试自己写进
tmp 项目的假 `cli.py`（由 cwd 解析），启动器是 iso 与真仓**字节相同**的同一 `.ps1`。⇒ 施加结果与"哪棵树"无关。

## 2. 采用的修法（运行前写死）

### 2.1 采用：**建议 1（推荐）+ 语义上界钳制**

```
t0  = 同一次测试内实测的启动带宽（见 2.2 口径）
H   = -WorkerHangTimeoutSeconds = min( max(2.0, 4 * t0), t0 + 3.0 )   # 秒
```

三个常数全部由**源卡原始数据**导出，不是"调到刚好通过"：

| 常数 | 作用 | 手算依据（源卡原始数据） |
|---|---|---|
| 系数 **4** | 下界：H 必须盖住"子进程②（立即退出型）的完整启动寿命" | 源卡全部独立测量的最坏上尾 = **2.486 s**（`child-lifetime-popen-cpu8` Q1 max）与 **2.303 s**（同条件 Q2 max）。需 `4*t0 ≥ 2.486` ⇒ `t0 ≥ 0.6215`。源卡 cpu8 实测 t0 最小值：popen **0.656**、startproc（看门狗自己的口径）**0.642** —— 均 > 0.6215 ⇒ `H ≥ 2.568 > 2.486 > 2.303` ✓ |
| 地板 **2.0** | 只在 `t0 ≤ 0.5`（快机分支，`4*t0 < 2.0`）时生效 | 该分支下源卡最坏观测 = `startproc-quiet` Q2 max **1.164 s**；再加冻结带自身"最后一个子进程干净退出" max **0.622 s** —— 均 < 2.0 ✓ |
| 上界 **t0 + 3.0** | **节点自身语义的必需**（不是可选优化） | 见 2.3 |

### 2.2 t0 的测量口径（与看门狗逐条对齐）

看门狗口径（`.ps1:327-333, 351-373`）：`$StartedAt = Get-Date` **之后** `Start-Process -FilePath $PythonExe
-ArgumentList @('-m','company_wiki.source_catalog.cli','--config',…,'worker','--worker-config',…)
-WorkingDirectory $ProjectRoot -RedirectStandard{Output,Error} …`，uptime = `((Get-Date)-$StartedAt).TotalSeconds`
（**不含** PowerShell 启动 / Add-Type 编译 / 锁获取）。

因此 t0 = 用**同一段 PowerShell 脚本**、**同一个假项目**、同样的 argv/cwd/重定向，测
"Start-Process → `.source_catalog/fake_worker_count.txt` 首次落盘"的时长，轮询粒度 5 ms，
deadline 60 s（超时=探针失败=该次运行如实红，不回退默认值）。测得后**删除 marker**，
被断言的那次运行从与原测试完全相同的状态（无 count 文件）开始。
预热子进程随即 Kill 并等待退出；其 stdout/stderr 重定向写在**项目外**的探针目录，不污染项目。
（偏差登记：源卡建议 1 原文写"预热启动"未指明是否同一项目；本卡取**同一项目 + 事后删除 marker**，
与原文一致，且保证磁盘位置/路径长度与被断言运行完全相同。）

### 2.3 为什么必须加上界（否则会从"另一种红"换成"第三种红"）

行为表 `[{"sleep_seconds":5},{"exit_code":0}]` ⇒ 子进程①在**写出 count 之后 5 s**（≈ `t0 + 5 s`）自行
干净退出；若 `H ≥ t0 + 5`，看门狗永不触发 ⇒ 事件里没有 `child_unresponsive` ⇒
`next(e for e in events if status == "child_unresponsive")` 抛 `StopIteration` ⇒ **该节点仍然红**。

- 裸公式 `max(2.0, 4*t0)` 越界条件：`4*t0 ≥ t0 + 5` ⇒ **`t0 ≥ 1.667 s`**；
  源卡 cpu8 实测 Q1 **p90 = 2.133 s**（popen，n=25）与 max 2.486 s —— 即观测带里 ≥10% 的样本落在越界区。
- 取上界 `t0 + 3.0` ⇒ 触发余量恒 ≥ **2 s**（`H ≤ t0+3 < t0+5`），且不触碰任何下界常数。
- 该上界是"保住节点自身要证的产品语义"，不是放宽断言；断言 `== 2`、
  `unresponsive/restarting.reason == "session_start_timeout"` **一字未改**。

### 2.4 外层 `timeout=15` **保持不变**（手算足以覆盖）

单次运行墙钟 ≤ `H`（子进程①被杀）+ 子进程②完整寿命 + PowerShell/重定向开销
≤ `(t0+3) + t0 + 2 ≈ 2*t0 + 5`；源卡最坏 t0 = 2.486 ⇒ **≤ 10 s < 15 s** ✓。
故本卡**只改 `-WorkerHangTimeoutSeconds` 一个参数**，面最小。

### 2.5 **不采用**的两条 + 未施加的节点②（写死，避免事后改口）

| 选项 | 处置 | 理由 |
|---|---|---|
| **建议 3**（`assert … == 2` → `>= 2`） | **弃用** | 卡片第 4 条把它明确定性为"事后放宽"，采用前提是**测试维护者书面说明为什么"重启次数"不是该节点的产品语义**。本卡**未取得**该书面理由 ⇒ 按卡片原文弃用。放宽断言还能让"变异打红"失去支点（0.5 s 常量下 `>= 2` 恒绿），故它同时不满足本卡的变异要求。 |
| **建议 2**（重启后的子进程写新鲜 `worker_runtime.json` 再退出） | **不单用** | 源卡实测：`Start-Process` 到写出 runtime 之间 `$Runtime` 仍为 null，看门狗仍走 uptime 分支 ⇒ 单独不解决问题（源卡 `proposed-test-side-change.md` §建议 2 原文）。与建议 1 合用不冲突，但会把改动面从"1 个参数"扩到"行为表 + 参数"，在能用更小改动达成时不取。 |
| **节点②**（15/15/20 s 三预算改导出） | **不施加，登记 unverified** | 红先于绿是本卡硬纪律。源卡 M-B 端到端：`band-logon-quiet` **8/8 通过**、`band-logon-cpu8` **8/8 通过**（合计 16/16），源卡自己的 H5 结论就是"**未观测到抖动带**"⇒ **复现不出红** ⇒ 没有任何可附的变异证明。M-C 窗口确实擦线（cpu8 `events_seconds` 6/8 ≥ 15 s、`exit_seconds` max 21.593 ≥ 20 s），但那是窗口测量、不是节点失败，且源卡已如实标注 `exit_seconds` 是**上界**（探测循环自身每轮 0.3–1 s）。按"缺证据写未证实、不造绿色样例"，本卡**不动它**，只在 handoff 的 `unverified` 里登记。 |

### 2.6 禁止的"看起来能过"的做法（照抄源卡，本卡重申）

- 阈值不得取"刚好不再失败"的数（例如 0.7 s）——源卡独立测量上尾到 2.5 s；
- 不得把 `~25%` 观测值升格为规范常量（源卡第 6 条）；
- 不得改产品代码/配置/启动器来让测试变绿（卡片第 2 条，违反即 P1）。

---

## 3. expected（**全部由源卡原始数据手算**，不由本卡重跑生成）

### 3.A 冻结 24×2 观测带（我对源卡 `evidence/frozen_band_raw_record.json` 89150 B 独立复数）

完整性：48/48 行 stdout 与冻结 capture 逐字节相同、48/48 有 launcher 事件（复数结果与源卡一致）。

| 轮/树 | 运行 | 失败 | `child_started` 直方图 |
|---|---|---|---|
| pass1 / T0 | 12 | **3** | 2×9, 3×3 |
| pass1 / T4 | 12 | **2** | 2×10, 3×2 |
| pass2 / T0 | 12 | **3** | 2×9, 3×3 |
| pass2 / T4 | 12 | **4** | 2×8, 3×2, 4×2 |
| 合计 | 48 | **12** | 2×36, 3×10, 4×2 |

- 每树 24 次：T0 **6/24**、T4 **6/24**；翻转：pass1 失败更多者 T0（3>2）、pass2 是 T4（4>3）。
- 12 次失败全部同一条断言：`assert 3 == 2` ×10、`assert 4 == 2` ×2。
- 失败运行"第 2 个子进程被看门狗杀掉时的 uptime"：n=12，min **0.507**、median **0.537**、max **0.588**。
- 通过运行"最后一个子进程干净退出的 uptime"：n=36，min 0.113、median 0.2245、**max 0.622**。

**手算结论 A**：写死的 `0.5 s` **落在观测带内部**（0.507–0.588 被杀 / 至 0.622 干净退出）
⇒ 25% 红是"带内现象"，不是随机噪声；只要分布右移（负载）失败率上升。

### 3.B 独立带宽（源卡 `after/child-lifetime-*.json`，不经 pytest、不经看门狗）

| 条件/方法 | n | Q1 min/med/max | Q2 min/med/max | ≥0.5 s |
|---|---|---|---|---|
| popen / quiet | 30 | 0.402 / 0.5805 / 2.050 | 0.440 / 0.6905 / 1.721 | 18 / 24 |
| popen / **cpu8** | 25 | **0.656** / 1.287 / **2.486** | **0.753** / 1.351 / **2.303** | **25 / 25** |
| popen / cpu12 | 20 | 0.576 / 0.8225 / 1.696 | 0.569 / 0.9075 / 2.083 | 20 / 20 |
| startproc / quiet | 8 | 0.508 / 0.541 / 1.415 | 0.800 / 0.954 / 1.164 | 8 / 8 |
| startproc / **cpu8** | 8 | 0.642 / 0.8495 / 2.109 | 1.012 / 1.130 / 1.762 | 8 / 8 |

（Q1 = 行为选择首次落盘；Q2 = 立即退出型子进程寿命。startproc = 看门狗自己的启动口径。）

**手算结论 B**：cpu8 下**每一个**实测样本都 ≥ 0.5 s（25/25）⇒ 写死 0.5 s 时该条件**必然**越线。

### 3.C E-red（修前，写死 0.5 s）

- 依据 A+B：`0.5 < min(全部 cpu8 样本) = 0.642/0.656` ⇒ 子进程②必被杀 ⇒ `child_started ≥ 3` ⇒
  `assert … == 2` 必红；负载更重时（源卡 A1 登记的 8.8 核环境负载 + 其他会话 pytest 战役）会退化为
  `subprocess.TimeoutExpired`（源卡 M-B 实测 **18/18 失败、0 通过**，cpu8 条件）。
- **判据（预注册）**：C1 条件下 N=6 次中 **≥1 次红**即"复现红"成立；
  点期望为 6/6（源卡同条件 18/18、17/18、9/9）。

### 3.D E-green（施加后，H = `min(max(2.0, 4*t0), t0+3.0)`）

每一条都可由**该次运行自己记录的 t0 / 事件时间线**判定（不是"感觉变稳了"）：

1. `rc == 0`，断言原文不含 `E `；
2. `child_started` 恰为 **2**，`unresponsive.reason == restarting.reason == "session_start_timeout"`，
   最后一个子进程 `exit_code == 0`、`reason == clean_exit`；
3. **下界成立**：`H > 该次运行子进程②的完整寿命`（手算预注册：H ≥ 2.568 > 源卡最坏 2.486/2.303，
   见 2.1 表）；
4. **上界成立**：`H < 该次运行子进程①的实际退出时刻`（由上界 `t0+3` 与"count 落盘后再睡 5 s"保证，
   余量 ≥ 2 s）；
5. 负载条件与红臂**相同**（见 §4），并且绿臂阶段的独立负载探针读数不显著低于红臂
   （若绿臂负载明显更轻，绿不计入"同条件绿"，须补跑）。
- **判据**：N=6 全绿；任何一次红即如实报告（不删数据、不加跑凑绿）。

### 3.E E-mutation（M1）

- 变异体 **M1** = 把导出公式**退回写死 0.5 s**（其余（含 t0 探针、记录）保持不变，隔离被变异元素）。
- 依据 A+B 同 3.C：**预注册 ≥1 次红（期望 6/6）**。若 M1 不红 ⇒ 新判据无判别力 ⇒ 本卡判据不成立，如实报。
- 可选 M2（`H = 2.0` 常量，只留地板）**不纳入必做项**：其红与否取决于 `Q2 ≤ 2.0` 的比例，源卡数据
  （cpu8 Q2 max 2.303）下是概率性的，**不作为**本卡的变异证据。

### 3.F 边界与不变量（自证）

- `iso/src/**`、`iso/scripts/**` 运行前后逐字节相同（manifest 相等）；
- 真仓 `company-wiki/{src,scripts,tests}`、`pytest.ini`、根 `conftest.py` 运行前后逐字节相同；
- `changes.diff` **只含 `tests/**`**（逐文件披露）；
- 结束前 `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` **= 0**。

---

## 4. 负载条件与运行协议（冻结）

**条件**（全部取自源卡已测量过的负载形态）：

| 代号 | 定义 | 出处 |
|---|---|---|
| **C1**（主） | `cpu`：**8 个忙循环进程**（源卡 `harness/load.py` 语义：8×`while True: x=(x+1)%1000003`，启动后 1.5 s 稳态），叠加**当时环境负载** | 源卡 M-B `band-child-cpu8`（18/18 失败）、M-A cpu8（25/25 ≥0.5 s） |
| C2（预注册升级） | `cpu`：**12 个忙循环** | 源卡 M-A `child-lifetime-*-cpu12` |
| C3（预注册升级） | `spawn`：8 忙循环 + 持续拉起短命 python 进程 | 源卡 M-B `band-child-spawn`（9/9 失败） |

**环境负载独立测量**（不许"感觉变稳了"）：
- 阶段前/中/后各取 ≥1 次 3 s 窗口的进程 CPU 差分 ⇒ `busy_cores`（12 逻辑核为分母），外加每次运行的
  `sleep20_overshoot_ms`、`cpu_loop_300k_ms`、每 pass 的 `spawn_python_pass_ms_median`
  （源卡 cpu8 参考值：spawn 中位 **1042.8 / 882.0 ms**；其"安静"臂当时实为 ~8.8 核环境负载）。
- 记录环境差异（本机 09-25 实测 ambient 约 1.3/12 核，明显轻于源卡当时的 ~8.8 核）——
  因此**红臂优先用 C1**；若 C1 复现不出红，按 §3.C 的升级阶梯走，并逐级如实登记。

**臂与 N（冻结）**：

| 臂 | 内容 | N | 判据 |
|---|---|---|---|
| 红（修前） | 未改动的 iso 测试（写死 0.5 s），C1 | 6 | ≥1 红（§3.C） |
| 绿（施加后） | `H = min(max(2.0,4*t0), t0+3)`，**同条件 C1** | 6 | 6/6 绿 + §3.D 逐条成立 |
| 变异 M1 | 绿版但 `H` 写死 0.5 s，**同条件 C1** | 6 | ≥1 红（§3.E） |

**每次运行记录**：rc、verdict、断言原文、墙钟、launcher 事件时间线（statuses / attempt / uptime /
`hang_timeout_seconds`）、t0 与导出的 H（绿臂）、`CW-BASETEMP-DECISION` 行、两个负载探针、
stdout capture（原样入 attempt）。单次 driver 超时 **90 s**（超时计为红，不重跑掩盖）。

**运行形态（与源卡 M-B 同形）**：`-m pytest -p no:cacheprovider -q -B`、
`suite::node` 单节点、逐次全新空 basetemp、stripped env（仅
`PYTHONDONTWRITEBYTECODE=1, PYTHONUTF8=1, PATH, SYSTEMROOT, TEMP, TMP, PYTHONPATH=iso/src`）、
`cwd` 为该次运行目录。

## 5. 路径与环境决定（写死，避免事后辩解）

1. **一切写入物理落在本 attempt 目录**（卡文写入边界）。实测 Win32 `MAX_PATH=260` 下长路径不可写
   （证据：`r/` 探针目录，`Set-Content`/Python `open` 均报 "Could not find a part of the path"/
   `FileNotFoundError`；`LongPathsEnabled` 未启用；`subst` 被沙箱拒绝）。
   ⇒ 运行目录用 **8.3 短名路径**遍历同一物理目录：短根 =
   `…\REVENU~1\PLANNI~1\2026-0~1\EXECUT~2\I-14-E~2\A20260~1`（75 字符，长根 131 字符），
   `cwd = 短根\w`（77），`basetemp = 短根\w\<tag>`（≤ 83）。
2. **`CW_SHORT_BASETEMP_DISABLE=1`**（产品自带的 A/B 开关，`iso/conftest.py` 第 60 行）：
   - 不关的话，产品的短 basetemp 约定会把 basetemp **迁到 `%TEMP%/cw-pytest-basetemp/…`**，
     那是 `.planning` 外路径，本卡边界禁止；
   - 迁移后的 fallback 至少 `75+1+25=101` 字符 ⇒ 最坏生成路径 `101+125=226` **超出**产品自己校准的
     210 干净包络（`WIN32_PATH_LIMIT=210, GENERATION_RESERVE=150`）；
   - 关掉后 basetemp ≤83 ⇒ 最坏 `83+125=208 ≤ 210` ✓，与源卡有效 basetemp（78–84 字符，其记录
     "80/81 字符 → 12/12 通过"）同量级。
   - 每次运行的 decision 行由 `CW_BASETEMP_DECISION_FILE` 落盘，作为证据。
3. 根 `conftest.py`、`pytest.ini`、`tests/**` 全量拷贝进 iso ⇒ pytest 收集链与真仓**同形**。
4. 单树、单解释器、无网络（产品 hermetic fixture 自带 `COMPANY_WIKI_NETWORK=blocked`）。

## 6. 禁止事项（原卡 + 本卡）

1. 不改产品代码：`iso/src/**`、`iso/scripts/**` 与真仓 `src/**`、`scripts/**` 必须字节不变（违反即 P1）；
2. 不写真仓 `company-wiki/tests/**` —— 施加结果只以 `changes.diff` 交付（应用属晋升）；
3. expected 不得由重跑生成；冻结后只许追加式 erratum；
4. 不改源卡 `I-14-E/a20260919-01` 任何字节与 status；不碰其他卡；不写五份计划文件；
5. 禁止 git 写操作（只允许 `rev-parse/status/diff` 这类只读）、禁止联网；
6. 不代签 ACCEPT；不晋升；GREEN 必附变异证明，缺证据写"未证实"，**不造绿色样例**。

## 7. 预期产物

| 路径 | 内容 |
|---|---|
| `before/hashed_before.json` | 改动前全部锚点清单（真仓 + iso） |
| `before/freeze_instant.json` | 本文件冻结时刻与 sha256 |
| `oracle.md` / `oracle-addendum-*.md` | 冻结判据 / 追加式 erratum |
| `red/band-red.json` + `red/captures/` | 红臂原始 rc/断言/事件/负载 |
| `green/band-green.json` + `green/captures/` | 绿臂（含 t0、导出 H、负载） |
| `mut/band-mut-m1.json` + `mut/captures/` | 变异臂 |
| `after/hashed_after.json` + `before/final_hashes.json` | 前后逐字节自证 |
| `after/changes.diff` + `after/changes.manifest.json` | 只含 `tests/**` 的逐文件施加结果 |
| `after/analysis.md` | 三臂对照与判据逐条判定 |
| `handoff.json` / `review.md` | `status=review_pending`、`implementer_signed=false`；reviewer 独立判定 |
