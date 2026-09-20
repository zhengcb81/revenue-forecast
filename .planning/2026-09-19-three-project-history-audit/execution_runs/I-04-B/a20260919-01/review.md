# I-04-B 独立复审记录（两轮）

- reviewer：独立只读子代理 `1a721c67-3f05-4b98-8e87-6afd565cec6c`（两轮同一会话；只读，只在 `%TEMP%\i04b_review\` 建逐字节副本复跑）。
- **第 1 轮 `changes_required`（1×P1 / 4×P2 / 5×low）→ 作者修订 → 第 2 轮 `accepted_scoped`**（附 2 项非阻断条件 C1/C2 + 3 项 carry）。
- 授予范围：隔离副本内的预算规则修复（退避返回后重算、请求预算无下限、清理 `C=max(30,2r+g)`、探测 `min(20,相位预算)` 且现测、`pause_action`/`cleanup_*` 分账字段、相位墙只报告、`ε=0.57`）。
- **不授予**：真实 provider/worker 资格（I-07/I-16）、跨进程 lease 并发（I-04-C/D）、产品信封的探测耗时/相位墙字段（I-04-E）。

## 第 1 轮发现与处置

| id | 严重度 | 发现（摘） | 处置 |
|---|---|---|---|
| F-B4B-01 | **P1** | 探测 timeout 未按签署的 `min(20,·)` 封顶：`_pid_is_alive` 直接用相位预算（实测请求段授 44.9998、清理段 85.0） | 新增 `_PID_PROBE_MAX_SECONDS = 20.0` + `min(...)`；新用例 `test_i04b_f_b4d` 断言两相位探测各 ≤20 且 CLI 调用仍拿未封顶相位预算；复审复测 20.0/20.0 |
| F-B4B-02 | P2 | 请求段探测用"worker-status 之前"算的过期预算（虚拟钟实测超出 deadline 0.9 s） | 预算改为**在调用点现读**并传入（round-2 又收敛为"只读一次"）；新用例 `test_i04b_f_b4e` |
| F-B4B-03 | P2 | 冻结的 F-B4c（请求/清理分账）在**信封层零证据** | 新用例 `test_i04b_f_b4c` 走 `main()` 的 download 路径，断言信封同时含 8 个新键（复审复跑通过；nit：其中一条 `*0` 断言恒真，见下） |
| F-B4B-04 | P2 | F-B4 给**相位墙钟**设了验收上限，违反 I-04-A 随签口径 | 删除该断言，改为只报告；证据 `after/i04b-phase-wall-reported.txt`（作者 0.9071 s / 复审 0.9144 s） |
| F-B4B-05 | P2 | 交付缺 `handoff.json`（decision/recovery 亦缺） | 补三者（decision=NA 指向 I-04-A v2；recovery=回退配方；handoff=完整字段 + 承接） |
| F-B4B-06 | low | TimeoutExpired 注释仍写 `(retryable)` | 注释改为 TERMINAL（**行为不变**） |
| F-B4B-07 | low | "≥2 个时间分离会话"仅名义满足 | 程序改为 `--session quiet|load` **两次独立进程调用**（记录 UTC/monotonic 起点） |
| F-B4B-08 | low | 原始样本未落盘，p95 无法独立复算 | 每案保留 `raw` 数组；复审用 raw 重算 p95 **完全一致** |
| F-B4B-09 | low | `max(0.001, timeout)` 构成新最小 timeout | 删除，改为非正预算**报错**（round-2 演化为 R2-01） |
| F-B4B-10 | low | commands.json 陈旧（basetemp 不存在、观测是旧数、新命令未绑定、iso_patching 声明不成立） | round-2 后重写 `commands.json`（8 条命令全绑定、观测刷新、注明 basetemp 为临时目录），并给 iso_patching 的旧数字加 round-1 标注 |

## 第 2 轮

- 逐条核对 01…08 **真处置**（含复跑反例：探测 44.9998→20.0、85.0→20.0；过期预算超时 0.9 s→0.0；相位墙 0.9144 s 无上限）。
- **新矛盾专项**：探测封顶后与 R-P 行、`F-B4/F-B4d/F-B4e` 的相位预算语义、以及 R2 口径（子调用 ≤C+ε、相位墙只报告）**均无矛盾**；`min(20,remaining) ≤ remaining` 保证探测不可能越过 deadline。
- 两个被触碰的既有用例：**各 6 条断言与生产文件逐字节相同**（只改了时钟脚本与注释）；iso 与生产 39 个共同文件**仅允许的 2 个**不同；changes.diff 行多重集与复审的直接 diff 一致。

### 随签条件（非阻断）与处置

| 条件 | 内容 | 处置 |
|---|---|---|
| **C1** | `F-B4B-09` 的 `ValueError` 在"守卫读 → `_register` 内部再读"之间存在微秒窗口，可逃出 `__enter__` 被 `main()` 记成 `fatal/exit 1`（应为 `deadline_exhausted`）；移植生产前必修 + 增边界子案 | **已修**（`condition_c1_fix.py`）：**只读一次**——`__enter__` 现读 `probe_budget` 并作为参数传入 `_register`，`_prune_pause_entries` 的断言降级为不可达的内部不变量；**边界子案已加**（三值时钟 `[0.0, 5.0, 100.0]`/deadline=10 ⇒ 无异常逃出、首个探测=5.0、随后撤回 refcount 用清理预算 `min(20,C)=20`、终态 `deadline_exhausted`；`[0.0,100.0,100.0]` ⇒ 零探测 + `deadline_exhausted`） |
| **C2** | 命令记录未更新：4 条新命令未绑定、观测陈旧、`iso_patching.md` 的"已记录真实 basetemp"声明不成立 | **已修**：`commands.json` 重写（8 条命令，含两次 ε 会话与 merge、相位墙证据的 `-s` argv 与"basetemp 为临时目录"说明）；`iso_patching.md` 旧数字标注为 round-1 |

### carry（移交下游）

1. **I-04-E**：产品信封需增加**探测耗时**与**清理相位墙钟**字段（本卡只报子调用耗时与探头次数）。
2. **I-04-C/D**：跨进程 lease/refcount 并发（本卡只证单进程路径）。
3. **持续口径**：相位墙**只报告、不设验收上限**（R2 残留），已写进 `handoff.json`。

### 复审 not_verified（照录）

未在真实多参与者 refcount/慢 tasklist 下验证封顶与相位墙（结论来自注入 `subprocess.run` + 虚拟钟）；未运行真实 provider/wiki/worker；R2-01 竞态用注入时钟复现、**真实概率未量化**；相位墙证据 argv 由复审自行以 `-s` 复现；I-04-E 是否接受字段承接需其 owner 确认；`handoff.json` 的 `reviewer_agent_id` 无法自证。

### 复审复现的数字（照录）

`-k i04b` = 10 passed / 117 deselected / 2 subtests；T-FILING = 126 passed / 1 deselected / 41 subtests；探测授权 20.0/20.0；`C(40,5)=85.0`；过期反例超时 0.9→0.0；相位墙 0.9144 s 无上限；两用例断言与生产逐字节相同；生产 `046cc7dc…088` / `3087daf0…` / HEAD `d35b6f5` 未变。
