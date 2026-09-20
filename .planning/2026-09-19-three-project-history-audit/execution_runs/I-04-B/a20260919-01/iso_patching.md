# I-04-B iso 补丁说明（隔离副本 only；生产 `filing-fetch` 未改动）

生产锚点 `scripts/fetch_filing.py` sha256 `046cc7dc…088`（HEAD `d35b6f5`）**字节未动**；
本卡只改 `execution_runs/I-04-B/a20260919-01/iso/filing-fetch/` 下的**副本**。

## 产品侧补丁（20+1 处，全部可复核：见 `changes.diff`）

| 补丁 | 位置 | 内容（对应 I-04-A v2） |
|---|---|---|
| P-a | `_run_company_wiki_json_retry` except 分支 | **子调用返回后重算 `remaining`** 再算退避（D3；修掉"9s 调用 + 5s 过期退避 = t=14"） |
| P-b | 常量区 | `_CLEANUP_BUDGET_MIN_SECONDS = 30.0`（D2 下限） |
| P-c | `_pid_is_alive` | 增加 `timeout` 形参（去掉硬编码 20s），`TimeoutExpired` 显式重抛供上层计数（D1 R-P） |
| P-d | `_prune_pause_entries` | 收 `timeout`/`stats`，逐次计 `liveness_calls`，探测超时计 `liveness_probe_failed`（保守仍视为存活） |
| P-e | `PausedWorkerScope` | `_remaining()` → **`_request_remaining()`（无下限）** + **`_cleanup_timeout()`（= C 公式）**（D1/D2） |
| P-f / f2 / f3 / f4 | `__enter__` | 请求阶段预算守卫（`remaining<=0` ⇒ `action="deadline_exhausted"`、不发调用）；worker-status/pause 用请求预算；pause 前二次守卫并在必要时撤回 refcount；pause 失败路径的 resume 用 C |
| P-g / g2 | `_register` / `_unregister` | 收 `timeout`，透传给探测并计数 |
| P-h / h2 | `__exit__` | 记 `pause_action`；清理用 `timeout=C`；记 `cleanup_calls` / `cleanup_status` / `cleanup_elapsed_seconds`（**独立键**，不并入请求） |
| P-i | `_normalize_stats` | 新增 `liveness_calls` / `liveness_probe_failed` / `cleanup_calls` / `cleanup_status` 默认键；统计字典注解放宽为 `dict[str, Any]`（值类型已异构） |
| P-j / j2–j6 | `_stamp_request_timing` + `main()` | 记录并输出 `request_deadline` / `request_elapsed` / `pause_action` / `cleanup_*` / `liveness_*`（成功与失败信封都带） |
| **P-j5b**（首轮绿后修） | `main()` 的 `except FilingFetchError` | 戳记**加条件守卫**：`request_error` 在 `stats` 存在之前就抛出，无条件戳记会 `UnboundLocalError`（3 个既有 request_error 用例抓到；这正是"先跑既有套件"的价值） |

## 测试侧改动（隔离副本）

1. **新增 7 条** `I04BDeadlineBudgetTests`（F-B1、F-B2a、F-B2b、F-B3、F-B5、F-B4、F-B4b），追加在
   `tests/test_fetch_filing.py` 末尾；模型时钟用例明确声明是**数学验证**；F-B4/B4b 用**真桩进程**（临时目录），
   无 wiki/provider/worker。
2. **两处既有用例的时钟脚本**（**断言一字未改**）：
   - `test_catalog_locked_until_deadline_is_upstream_error`：`side_effect=[100,100,105,108]` → `[100,100,100,105,105,108]`（每次重试多一次"返回后重读"），期望仍为 `call_count==2`、`sleep==[call(5.0), call(3.0)]`、`attempts==2`。
   - `test_failure_envelope_preserves_stage_attempts_calls_downloads`：走 `main()`，脚本改为 8 个值（main 起点 + deadline + 每轮预算 + 每次重读 + 失败戳记），期望仍为 `attempts==2 / calls==2 / downloads==0`。
3. `EPSILON_S`：0.4（临时）→ **0.57**（`scripts/i04b_real_timing.py` 预先承诺程序重测后**一次**重签）。

## 结果

| 阶段 | 结果 | 证据 |
|---|---|---|
| 修前基线 T-FILING | 116 passed / 1 deselected / 39 subtests | `before/t-filing-baseline.txt` |
| 修前新用例（RED，round-1 的 7 条） | **5 failed, 2 passed**（F-B1 `[call(5.0)] != [call(1.0)]`；F-B2a `worker-status` 在截止后被以 `timeout=10.0` 发出；F-B2b `10.0 > 0.2`；F-B4 缺新常量；F-B4b 真进程 3s 桩**未**被杀） | `before/i04b-red.txt` |
| 修后新用例（round-1） | 7 passed（2 subtests） | `after/i04b-green.txt`（round-2 后为 **10 passed**） |
| 修后 T-FILING（round-1） | 123 passed / 1 deselected / 41 subtests | `after/t-filing.txt`（round-2 后为 **126 passed**） |
| 真实进程轨迹 + ε 重测 | 请求段 0.6136 s（预算 0.6）/ 清理子调用 0.405 s / 清理相位墙钟 0.8613 s；**ε=0.57（第一版程序口径）**；round-2 按复审修订为两次独立调用 + 原始样本留档后池化得 0.38 —— 签名取三者最大值 0.57（见 commands.json 的 estimator_note 与 oracle.md 补记） | `after/i04b_real_timing.json` |

## 复审修复轮（reviewer F-B4B-01…10；`scripts/review_fixes*.py`）

| 发现 | 处置（全部在隔离副本内） |
|---|---|
| **F-B4B-01 P1** 探测没按签署的 `min(20,·)` 封顶（实测授予 44.9998/85.0） | 新增常量 `_PID_PROBE_MAX_SECONDS = 20.0`；`_pid_is_alive` 改为 `timeout=min(_PID_PROBE_MAX_SECONDS, timeout)`；**新用例** `test_i04b_f_b4d_pid_probe_is_capped_at_twenty_seconds` 断言两相位探测各 ≤20 且 CLI 调用仍拿到未封顶的 60 s（相位预算） |
| **F-B4B-02 P2** 请求段探测用过期预算（虚拟钟实测超 deadline 0.9 s） | `_register(*, joined)` **内部现算** `self._request_remaining()`（不再收调用方传入的旧值）；`__enter__` 在 joined 与主路径**各加预算守卫**（≤0 ⇒ `deadline_exhausted`、不发探测）；**新用例** `test_i04b_f_b4e_probe_uses_the_budget_read_at_that_moment`（0.1 s 剩余 ⇒ 授予 0.1；预算耗尽 ⇒ 零探测） |
| **F-B4B-03 P2** F-B4c 分账缺信封级证据 | **新用例** `test_i04b_f_b4c_envelope_reports_request_and_cleanup_separately`：走 `main()` 的 download 路径（真 pause/resume 流程）断言信封同时含 `request_deadline`/`request_elapsed` 与 `cleanup_calls`/`cleanup_elapsed_seconds`/`cleanup_status`/`pause_action`/`liveness_*` |
| **F-B4B-04 P2** F-B4 对相位墙钟设了验收上限 | 删除 `assertLessEqual(wall, C+ε)`；改为**只报告**（`I04B_REPORTED_PHASE_WALLS` + 打印），实测输出见 `after/i04b-phase-wall-reported.txt`（0.9071 s） |
| **F-B4B-05 P2** 缺 handoff.json / decision / recovery | 本卡补 `handoff.json`（含 F-B4B-01/02/04 与 I-04-E 承接）、`decision.md`（NA：设计在 I-04-A v2）、`recovery/README.md`（回退配方） |
| **F-B4B-06 low** TimeoutExpired 注释仍写 `(retryable)` | 注释改为"surfaces as upstream_error and is TERMINAL（不在重试集内）"，**行为不变** |
| **F-B4B-07/08 low** 会话未真正分离、原始样本未留档 | `scripts/i04b_real_timing.py` 重写：`--session quiet|load` 每次**独立进程调用**（记录 `session_started_utc`/`monotonic`），**保留每案原始数组**，并把 p95 定义写死为"升序 `int(0.95*(n-1))`、不插值"；`--merge` 事后汇总 |
| **F-B4B-09 low** `max(0.001, timeout)` 等于新最小 timeout | 删除；改为 `_prune_pause_entries` 前置 `if timeout <= 0: raise ValueError(...)`（调用方保证 >0） |
| **F-B4B-10 low** commands.json 的 basetemp 路径不存在；新用例类在 `__main__` 之后 | `commands.json` 记录**实际使用的** basetemp 并注明 pytest basetemp 为临时目录；`unittest.main()` 入口**移到文件末尾**，新用例类在其之前可被直接执行收集 |

复审修复轮后的结果：新用例 **10 passed**（2 subtests）、T-FILING **126 passed / 1 deselected / 41 subtests**（`after/i04b-green.txt`、`after/t-filing.txt`）。

