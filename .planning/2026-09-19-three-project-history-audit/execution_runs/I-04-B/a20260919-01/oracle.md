# I-04-B oracle（运行前冻结；签署后不得为实现结果改写）

来源：卡片 `card_I-04-B.md` 的正反例表 + `execution_runs/I-04-A/a20260919-01/decision.md v2`（已签署）
的 D1–D5。数字全部可从这两处独立推导；模型时钟用例是**数学验证**，真实进程用例只用**桩脚本**。

## 冻结的模型时钟预期（修前必须红、修后必须绿）

| Case | 注入 | 冻结预期 | 修前实测（RED 证据） |
|---|---|---|---|
| **F-B1** | deadline=10；首次子调用消耗 9 并抛 catalog_busy；jitter=0；backoff=5 | 子调用**恰 1 次**；退避 = min(5, **返回后**剩余 1) = **1.0**；无第二次调用；请求结束 ≤ 10 | `sleep.call_args_list == [call(5.0)]`（用调用前过期剩余 10 得到 5）⇒ 结束时 14 > 10 |
| **F-B2a** | now=100，deadline=90，需要 worker-status | 请求阶段调用数 **0**；**不得**出现 10 秒请求预算；`action == "deadline_exhausted"` | `_run` 被调用 1 次且 `timeout=10.0`（`max(10, min(-10,60))`） |
| **F-B2b** | 只剩 0.2 秒 | 传给子调用的 timeout ≤ **0.2**（>0），不得抬到 10 | 传入 `10.0` |
| **F-B3** | fatal / worker_paused，预算充足 | 不自动重试；子调用 1 次；不 sleep；原错误码保留 | 修前即绿（回归护栏） |
| **F-B5** | 首次成功且 worker stopped / 用户已暂停 | 无多余调用（仅 worker-status），不 pause/resume | 修前即绿（回归护栏） |

## 冻结的真实进程预期（受控桩，无 wiki/provider/worker）

| Case | 注入 | 冻结预期 |
|---|---|---|
| **F-B4**（清理） | 真子进程 0.30 s 作为 worker-resume；C = max(30, 2×5+5) = 30 | `cleanup_calls=1`；`cleanup_status="restored"`；`cleanup_elapsed_seconds` **是独立键**（≥0.25 且 ≤ C+ε）；`pause_action` 记录；真实墙钟 ≤ C+ε |
| **F-B4b**（请求段超时） | 真子进程 3.0 s 作为 worker-status，预算 0.6 s | 子进程被按时杀掉：实测 ≤ 0.6+ε 且 ≥ 0.3；`action == "no_status"`（worker-status 失败的既有语义） |
| **F-B4c**（分账） | 同一次 attempt 的请求段与清理段 | `request_deadline`/`request_elapsed` 与 `cleanup_elapsed_seconds` **分别报告**；不得合并成一个 wall 数字（历史 "10→14" 事故的反面） |

## 冻结的 ε 与 C

- **C = max(30.0, 2×resume_wait + graceful)**（默认 30.0）；`_cleanup_timeout()` 恒等于 C。
- **ε**：本卡按 I-04-A D4 **预先承诺的程序**重测（真实 CLI import 链 + 并发负载 + kill/reap 延迟；
  n≥50/案、≥2 会话；ε := 2×max(p95)，上限 2 s）。重测触发是程序本身，不是"某次测试失败"；
  重测值记录于 `after/i04b_real_timing.json`，为**一次**允许的重签。

## 附加冻结约束（复审判定用）

- 每个请求阶段子调用的 `timeout` = **调用时刻**的剩余（返回后重算再退避）；清理用 C。
- 阶段/预算类型必须出现在日志或 stats：`pause_action`、`cleanup_status`。
- **不得**引入新的最小 timeout 下限；**不得**把清理耗时并入请求 elapsed。
- pid 存活探测（tasklist）计入独立计数 `liveness_calls`，失败记 `liveness_probe_failed`。
- 既有非 live 用例必须继续通过：允许**只**更新被时钟脚本消费次数影响的 fixture，
  断言与意图不得放宽（本次仅两处 side_effect 列表 + 一处 main 路径脚本）。

## 运行后澄清（**不改变任何冻结值**；落实 I-04-A 重签携带的 `F-BA2A-R2-residual`）

I-04-A 复审随签携带的强制口径要求：清理验收按**子调用**、相位总墙钟**单列报告且不设验收上限**。
本次实测（`after/i04b_real_timing.json`）恰好给出该口径的必要性证据：

| 量 | 实测 | 归属 |
|---|---|---|
| 请求段（真桩 3s，预算 0.6s） | **0.6136 s** | 请求子调用（≤ 0.6+ε ✓） |
| 清理子调用（真桩 0.30s resume） | **0.405 s** | `cleanup_elapsed_seconds`（≤ C+ε ✓） |
| 清理**相位**墙钟 | **0.8613 s** | 含 `_unregister` 的 tasklist 存活探测 ≈ **0.456 s**（R-P 行） |

⇒ **验收口径**：`worker-resume` 子调用 ≤ C+ε；**每个** pid 探测各自 ≤ min(20, 相位预算)；
**相位总墙钟不设上限、只作报告**（`_register`/`_unregister` 的探测次数随 refcount 条目数变化，
把它并入 C 的验收会在多参与者场景下产生假 RED）。
**登记的产品侧缺口（不在本卡范围内）**：信封目前只报 `cleanup_elapsed_seconds`（子调用）与
`liveness_calls`/`liveness_probe_failed`（次数），**未**单列探测耗时与相位墙钟；候选承接卡 =
**I-04-E**（保留失败前真实副作用计数）或 I-04-C/D（lease 协议）。本卡不新增未签字段。

## 复审修复轮补记（reviewer F-B4B-01…10；**不改变任何冻结值**）

1. **`F-B4B-01`（P1）已修**：探测 timeout 现为 **`min(_PID_PROBE_MAX_SECONDS=20.0, 相位预算)`**，
   两相位一致；新用例断言每个探测 ≤20 s，同时断言请求段 CLI 调用仍拿未封顶的 60 s（相位预算）。
2. **`F-B4B-02`（P2）已修**：`_register` **在探测那一刻现算** `_request_remaining()`（不再用
   worker-status 之前的旧值）；`__enter__` 的 joined 与主路径各加预算守卫（≤0 ⇒ `deadline_exhausted`、
   **零探测**）。新用例覆盖 0.1 s 剩余 ⇒ 授予 0.1，以及预算耗尽 ⇒ 零探测。
3. **`F-B4B-03`（P2）已补证**：新增走 `main()` 的 download 路径用例，断言**信封**同时携带
   `request_deadline`/`request_elapsed` 与 `cleanup_calls`/`cleanup_elapsed_seconds`/`cleanup_status`/
   `pause_action`/`liveness_calls`/`liveness_probe_failed`（分账在信封层可见）。
4. **`F-B4B-04`（P2）已改**：相位墙钟**只报告不设上限**（打印 + 模块级记录；证据
   `after/i04b-phase-wall-reported.txt` = 0.9071 s），子调用仍受 C+ε 约束。
5. **ε 两次签署的合并口径**：第一版程序（3 个进程内会话、无原始样本）得 **0.57**；
   按 `F-B4B-07/08` 修订后的程序（**两次独立调用、真正时间分离、保留原始数组、p95 定义写死**）
   池化后 worst p95 = **0.1907** ⇒ 2×= **0.38**。**签名值取两者最大值 `0.57`**——保留更保守的一侧，
   使"协议改进"不可能被读成"事后放宽"；此后不得再放宽。
6. 其余：`F-B4B-06`（TimeoutExpired 注释）、`F-B4B-09`（删除 `max(0.001,·)`，改为非正预算**报错**）、
   `F-B4B-10`（`unittest.main()` 入口移到文件末尾、commands.json 记录真实 basetemp）均已处置。


