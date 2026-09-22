# I-14-E-APPLY oracle.md — 施加 I-14-E 实测导出的测试侧时序修复

attempt：`execution_runs/I-14-E-APPLY/a20260921-01`
**冻结时刻：2026-09-21T23:10:00Z（UTC）**，先于本 attempt 的任何一次运行（`before/freeze_instant.json`）。

本卡是**实施卡**：把 I-14-E **已测量、未施加**的测试侧修改（`I-14-E/a20260919-01/after/proposed-test-side-change.md`
§"建议 1（推荐）"）施加到**隔离副本**中的产品测试文件上。

**父裁定（本卡授权来源）**：I-14-E 实现者正确登记了口径冲突（卡片正文说"修产品测试时序假设"，
派发边界说"生产只读"）。`OWNER_DECISIONS.md` §13 T1-7 明确授权一张卡可以"修产品测试时序假设"。
本 apply-card 即该授权。**生产仓就地只读**——修复只活在 `iso/`，晋升是另一个 owner 决策。

`status=review_pending`，实现者不自签。

---

## 1. SUT 身份与绑定（运行前记录）

| 项 | 值 |
|---|---|
| 被修改的产品测试（SUT） | `tests/contract/test_source_catalog_worker_bootstrap.py` |
| 生产副本 sha256（就地只读，不改） | `32515aa60d5fbfbca0778ee68e778ada7ff3bcf238f91930bb621d84aec005c1` |
| 生产路径 | `C:\Users\郑曾波\Projects\company-wiki\tests\contract\test_source_catalog_worker_bootstrap.py` |
| 隔离副本（本卡的 SUT） | `iso/tests/contract/test_source_catalog_worker_bootstrap.py`（运行前 = 生产字节相同） |
| 真实启动器（不改） | `scripts/source_catalog_worker.ps1` sha256 `5c12cd740cc3…` |
| 登录包装器（不改） | `scripts/source_catalog_worker_at_logon.ps1` sha256 `70b4d7d71285…` |
| 隔离树 A | `iso/T0/` = 上面的文件（测试在 `<T0>/scripts/` 解析启动器，`Path(__file__).parents[2]`） |
| 隔离树 B | `iso/T0b/` = `iso/T0/` 的**字节相同**第二副本（身份对照，用于把"结果差异"与"树身份"解耦） |
| 运行解释器 | `iso/venv/Scripts/python.exe` 3.13.9，pytest 9.1.1（= I-14-E venv 的字节副本） |
| 口径基准 | **整数秒** `-WorkerHangTimeoutSeconds`——启动器把它当 ps1 的参数用；见 §3 的表示约束 |
| 环境 | 12 逻辑核 / 15.8 GB；机器与他人会话共享，每次运行记录负载探针 |

**运行前就成立的结构性前提**：节点①的测试体不 import 任何 `company_wiki.*`；被启动的子进程是测试自己
写进 tmp 项目的假 `cli.py`（只用 stdlib，由 cwd 解析）。因此本卡的改动**不可能**影响脱敏树差异
（I-14-C/I-14-E 已证 T0 vs T4 的差异只在 `source_catalog/{cli,observability,worker}.py`，而节点①根本不加载它们）。
本卡因此只保留 **T0 / T0b** 两棵字节相同的树，把预算花在**载荷臂**（quiet / cpu8 / mutation）上。

---

## 2. 施加的改动（运行前冻结的精确形态）

### 2.1 现状（生产，未改）

```python
# ISO line 893-917 (生产同)
def test_child_without_runtime_session_is_terminated_and_restarted(tmp_path):
    project = _prepare_fake_launcher_project(
        tmp_path,
        [{"sleep_seconds": 5, "exit_code": 0}, {"exit_code": 0}],
    )
    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=0.5,      # <-- 写死
        child_poll_milliseconds=100,
    )
    ...
    assert len([e for e in events if e["status"] == "child_started"]) == 2
```

### 2.2 目标（本卡施加）

新增**一个同文件内的 helper**（不改任何既有 helper 的语义），把 hang timeout 从**同一次测试内实测的
子进程启动带宽**导出：

```python
_LAUNCH_SAMPLES = 3                    # 预热启动样本数
_LAUNCH_MARGIN_FACTOR = 4.0            # t0 -> hang timeout（I-14-E 建议 1 的系数）
_HANG_TIMEOUT_FLOOR_SECONDS = 2.0      # I-14-E 建议 1 的下限
_HANG_TIMEOUT_CEILING_SECONDS = 4.0    # 由节点自身产物导出（见 §2.4），不是"调到刚好通过"

def _measure_child_launch_latency(tmp_path, samples=_LAUNCH_SAMPLES) -> float:
    """预热启动 N 次"立即退出"型假子进程，返回 launch -> clean_exit 的**最大值** t0。

    走的是真实启动器（`_run_real_worker_launcher`），因此测得的量就是看门狗
    `(Get-Date) - $StartedAt` 所比较的那个量，且包含 PowerShell `Start-Process` 的开销
    ——I-14-E 的独立测量明确区分了这两条路径（startproc 中位数 0.954 s > popen 0.691 s）。
    哨兵行为表是 `[{"exit_code": 0}]`（只有一条），所以每个子进程都"立即退出"；
    取**最大**而非中位数是刻意的保守选择（会让 hang 更大，被 §2.4 的 4.0 s 上界兜住）。
    """

def _derive_worker_hang_timeout_seconds(tmp_path) -> int:
    """t0 = 实测；hang = ceil(clamp(4.0 * t0, 2.0, 4.0))。"""
```

**为什么走真实启动器而不是直接 spawn**：I-14-E 的独立测量用 `popen`（不含 `Start-Process` 开销）
与 `startproc`（含）两条路径量同一件事，得到 quiet 中位数 0.691 s vs 0.954 s。看门狗比较的是
**监督者自己**的 `(Get-Date) - $StartedAt`，即**含** `Start-Process` 的那条路径；只量 popen 会
系统性低估。走真实启动器同时保证"测的就是它要比的那个量"。

**预热样本之所以不会被 0.5 s 看门狗污染**：真实启动器默认 `-WorkerHangTimeoutSeconds` = 0.5 s，
会把某个预热子进程当成挂死杀掉 → 那次样本报 `child_unresponsive`（有 `uptime_seconds`）而不是
`exited`，随后重启的下一个样本照常"立即退出"。两种形态都提供"launch → 该子进程寿命"的读数，
所以样本仍然有效；本卡把两种形态都计入，并在产物里分开计数（见 `after/analysis.md`）。

然后节点①改为：

```python
    hang_timeout_seconds = _derive_worker_hang_timeout_seconds(tmp_path)
    completed = _run_real_worker_launcher(
        project,
        timeout=15,                                # 不变
        worker_hang_timeout_seconds=hang_timeout_seconds,   # 由实测导出
        child_poll_milliseconds=100,               # 不变
    )
```

### 2.3 **不改**的东西（写进 oracle，避免事后辩解）

1. `assert ... child_started ... == 2` 一字不改（不得放宽为 `>= 2`；I-14-E 明确**不建议**建议 3）；
2. 该节点对产品语义的断言全部保留（`child_unresponsive.reason == "session_start_timeout"`、
   `restarting.reason == "session_start_timeout"`、`returncode == 0`、事件序列）；
3. `timeout=15` 与 `child_poll_milliseconds=100` 不变；
4. 不改任何产品源码 / 启动器 / 配置；
5. **生产三仓就地零写入**（`after/final_hashes.json` 逐字节证明）；
6. 不采用 I-14-E 的建议 2（"让第二个子进程写新鲜 runtime"）作为本卡的修法——I-14-E 自己标注了它
   **不能单独解决问题**（Start-Process 到写出 runtime 之间 `$Runtime` 仍为 null）。本卡只做建议 1。

### 2.4 语义合法性边界（**运行前推导，不是事后**）

节点①的产品语义是"**没有 runtime 会话且仍然活着的子进程会被终止并重启**"。这一语义要求派生出的
hang timeout 落在**开窗**里，窗口两端都可从测试**自身的产物**读出，不需要外部常数：

| 边界 | 值 | 由什么导出 |
|---|---|---|
| 下界（必须能容忍"干净退出"型子进程） | 子进程 launch→exit 的上尾 | I-14-E 实测 quiet 1.72 s / cpu8 2.30 s / startproc 1.16 s；本卡同条件复测 |
| 上界（必须仍能杀掉"挂死"的第一个子进程） | 第一个子进程的寿命 = `sleep_seconds 5` + 其启动延迟 | 测试自己的行为表 `{"sleep_seconds": 5}` |
| 本卡采用的取整安全上限 | **4.0 s** | `5 s` 睡眠 − 1 s 余量：4.0 s 时第一个子进程至少再活 2 s 以上，看门狗必杀 |

⇒ `hang ∈ (max(2.0, 4·t0) capped at 4.0)`。**若 4·t0 > 4.0 则取 4.0**：这不是放宽，而是把
"看门狗必须仍在第一个子进程的 5 s 睡眠内开火"这条产品语义写成硬上限。**本卡必须在产物里报告
每次运行实际记录到的 hang timeout**（从该次运行自己的 `worker_launcher_events.jsonl` 的
`worker_hang_timeout_seconds` 字段读出，不靠日志转述）。

**表示约束（I-14-E 未覆盖，本卡补充记录）**：启动器把该值作为 ps1 参数使用，而 I-14-E 的冻结记录里
所有 `child_unresponsive` 的 uptime 都落在 `[0.50, 0.72]`，说明 0.5 s 是**忠实施加**的。本卡施加的是
**整数秒**（`ceil(clamp(4·t0, 2.0, 4.0))`，即 2/3/4），以消除"ps1 参数格式把小数吃掉"这一未知风险；
**取整方向一律向上**，只会让窗口更宽，且被 §2.4 的 4.0 s 硬上限兜住。
**这条是本卡的保守选择，须在 review 里复核。**

**已知残余风险（运行前自愿登记，不作为事后辩解）**：若本次测试内测到的 `t0` 偏小、而**随后那次**
运行的子进程延迟恰好落在分布的上尾，派生值仍可能不够（I-14-E 实测 quiet 的 `4·max` 也只有
6.9 s 才覆盖 p99，而 §2.4 的上界只允许 4.0 s）。因此判据 R1 是 **8/8**，并已事先写明：
若不达 8/8，如实登记为"该修法在本机本时段不足"，不调判据。

---

## 3. "测试现在稳健（robust）"的**操作性定义**（运行前冻结）

本卡**不**声称"永不失败"。以下是可判定的操作定义，四条全过才算 robust：

| # | 判据 | 判定方式 |
|---|---|---|
| **R1** | **载荷下不再随机红**：`iso/` 修复版节点①在 `+8 忙循环`（cpu8）下 **8/8 通过** | bench runner 逐次运行记录 rc/verdict |
| **R2** | **安静下不回归**：同一修复版在 quiet 下 **8/8 通过** | 同上 |
| **R3** | **仍然可失败（反空转）**：一个**真的挂死**的子进程仍必须被抓住——看门狗仍以 `session_start_timeout` 杀掉它，于是 `child_started` 变成 3，而节点①的断言是 `== 2` ⇒ **节点①会红** | fail-ability 节点（§5）：要求**看门狗确实开火**、被杀 uptime 落在派生预算内、且**节点①自己的断言在这种输入下为假** |
| **R4** | **突变证明**：把派生**退回写死 0.5 s**（其余字节相同）后，同一 cpu8 载荷下必须**重新变红** | 突变臂必须 ≥ 6/8 失败 |

**判据的反面（同样运行前冻结）**：

- R1 若出现"通过是因为派生值大到看门狗永不触发" —— 由 R3 单独否掉（R3 证明派生值确实会开火）；
- R1 若通过率不足 8/8，本卡**如实登记为"该修法在本机本时段不足"**，不改判据、不加大载荷到刚好通过；
- R4 若突变臂仍然绿色，则说明本卡的 iso 环境与 I-14-E 的载荷相关性**不可复现**，本卡的 R1 结论
  **不得**被读成"修复有效"，只能读成"环境不同"。

**为什么 R3 是必须的**：一个"永不触发的 derived timeout"比原来的 bug **更糟**——它会把
"没有 runtime 会话的子进程会被终止"这条产品语义变成空转断言。I-14-E 的测量（p99 2.30 s、
max 2.303 s、startproc max 1.164 s）只给出"下界要多高"，**不**给出"上界在哪"；上界唯一的来源
就是"第一个子进程还活着"这件事本身，所以 R3 是直接检验 §2.4 那个窗口非空。

---

## 4. 运行计划（冻结；臂与次数在运行前写定）

坐标：`A = <ATT>`，`PY = A/iso/venv/Scripts/python.exe`。

| 臂 | 条件 | 树 | 次数 | 期望 |
|---|---|---|---|---|
| **B1** | quiet，`-p no:cacheprovider`，每次新建 basetemp，交错 T0/T0b | T0,T0b | 4 次 × 2 轮 × 2 树 = **16** | 16/16 绿（R2） |
| **B2** | cpu8（8 忙循环，与 I-14-E 同形），其余同上 | T0,T0b | 4 次 × 2 轮 × 2 树 = **16** | 16/16 绿（R1） |
| **B3（突变）** | cpu8，其余同上，SUT = `iso/mutant-fixed-0.5/`（派生退回写死 0.5 s） | T0,T0b | 3 次 × 2 轮 × 2 树 = **12** | ≥ 8 红（R4） |
| **B4（反空转）** | cpu8 + quiet，fail-ability 节点（§5） | T0,T0b | 3 次 × 2 轮 × 2 树 × 2 条件 = **24** | **全红**（R3） |

- 每次运行记录：rc / verdict / 断言原文 / 节点墙钟 / **该次运行实际记录到的 hang timeout** /
  launcher 事件时间线（status 序列、attempt、被杀 uptime、干净退出 uptime、被杀次数）/ 负载探针。
- 载荷由 `harness/load.py`（= I-14-E 的同一份，字节副本）生成并在条件结束时回收。
- 每次运行前清扫本 driver 自己 scratch 根下遗留的启动器/子进程（匹配 `-ProjectRoot` 含本 root，
  不碰其他会话）。

**不做什么**（写进 oracle）：

1. 不改生产仓（就地只读）；
2. 不放宽任何断言；
3. 不用"载荷大到必红"或"载荷小到必绿"去凑判据；
4. 不把本机本时段的结果升格为规范常量。

---

## 5. 反空转（fail-ability）节点的精确形态

在 `iso/` 的测试文件里**新增**一个节点（生产文件里没有它，故属于"本卡新增证据"，
须在 handoff 里单列）：

```python
@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell launcher integration")
def test_derived_hang_timeout_still_terminates_a_genuinely_hung_child(tmp_path):
    """R3 反空转证明：派生出的 hang timeout 仍会杀掉一个真正挂死的子进程。

    生产节点①的假子进程是"立即退出"型，派生出的 timeout 一旦过大就会变成空转断言。
    这里把**重启后的那个子进程**换成真挂死型（sleep 30、不写 runtime），
    因此看门狗必须在 timeout 内开火 → 出现第 3 次 child_started → 节点①的断言 `== 2` 必然失败。
    本节点断言"上述失败确实发生"。
    """
    hang_timeout_seconds = _derive_worker_hang_timeout_seconds(tmp_path)
    project = _prepare_fake_launcher_project(
        tmp_path,
        [{"sleep_seconds": 5}, {"sleep_seconds": 30}, {"exit_code": 0}],
    )
    completed = _run_real_worker_launcher(
        project, timeout=15,
        worker_hang_timeout_seconds=hang_timeout_seconds,
        child_poll_milliseconds=100,
    )
    assert completed.returncode == 0, completed.stderr
    events = _launcher_events(project)
    unresponsive = [e for e in events if e["status"] == "child_unresponsive"]
    assert unresponsive, "watchdog never fired: the derived timeout is vacuous"
    assert all(e["reason"] == "session_start_timeout" for e in unresponsive)
    assert all(e["uptime_seconds"] <= hang_timeout_seconds + 1.0 for e in unresponsive)
    starts = [e for e in events if e["status"] == "child_started"]
    assert len(starts) == 3, "hung child was not caught -> the derived timeout is vacuous"
```

**判定（口径澄清，写于见到任何 B4 数据之前）**：B4 臂的**pytest 节点应当 GREEN**——该节点断言的是
"挂死子进程**被抓住**"，抓住就通过。R3 的实质是把这句话翻过来验：

- **(a)** 看门狗开火：≥1 条 `child_unresponsive`，reason 全为 `session_start_timeout`；
- **(b)** 被杀 uptime ≈ 派生的 hang timeout（落在 `[hang − poll, hang + 1.0]` 内），而不是某个无关的值；
- **(c)** 该次运行的 `child_started` 计数 **== 3**，于是**节点①的 `== 2` 断言在这种输入下必然为假**。
  节点里写了 `assert len(starts) == 3` 把 (c) 直接变成执行判据；同时原始事件时间线被逐次留档，
  reviewer 可以脱离日志自己重数。

**因此 B4 的失败形态是明确的**：若看门狗从未开火（派生值大到永不触发），`unresponsive` 为空、
`starts` 仍为 2 → 该节点 **RED**，R3 不成立。若 B4 出现任何 RED，本卡必须报 **blocked**，
不得报 review_pending 通过。

（**先前的措辞**"B4 必须每一次都失败"指的是**节点①**在该输入下的结果，不是指 B4 这个节点的
pytest verdict；此处按可判定的形式重述，不改变任何判据的实质。）

---

## 6. 预期产物

| 路径 | 内容 |
|---|---|
| `oracle.md` | 本文件（运行前冻结） |
| `before/freeze_instant.json` | 冻结时刻 + 逐文件 hash + 生产只读基线 |
| `before/binding_hashes.json` | iso/T0/T0b/venv/生产锚点 hash 与相等性证明 |
| `after/bench-*.json` + `after/bench-captures*/` | B1/B2/B3/B4 逐次运行记录与 stdout/事件 |
| `after/fail-ability.json` | R3 的判定证据（含 (a)(b)(c) 三条逐次核对） |
| `after/analysis.md` + `after/analysis.json` | R1–R4 逐条判定 |
| `after/diff.patch` | 施加的改动（unified diff，iso vs 生产） |
| `after/mutation.diff` | 突变改动（fixed-0.5 vs iso） |
| `after/final_hashes.json` | **生产仓就地未被写入**的逐字节证明 |
| `handoff.json` / `review.md` | status=review_pending；reviewer 独立判定 |
