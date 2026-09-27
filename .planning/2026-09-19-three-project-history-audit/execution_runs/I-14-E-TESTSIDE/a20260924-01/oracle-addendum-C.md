# I-14-E-TESTSIDE oracle.md — Addendum C（**追加式** erratum；主文与 A/B 均未改）

记录时刻：**2026-09-25T21:10Z（UTC）**。本 addendum 登记一个**在红臂第一次重跑之前**就已确证、
并且**本会话权限范围无法解除**的环境阻断。§2 修法、§3 expected、§4 负载与 N、§6 禁止事项
**一字不改**；三臂仍按冻结 N 运行，但其可证性按下文如实降级。

## C1. 阻断事实（全部可复现，探针脚本在 `harness/`）

被测启动器 `source_catalog_worker.ps1`（iso 副本，sha256 `5c12cd74…bc311`，与真仓逐字节相同）
第 340–341 行：

```powershell
$ChildHandle = $Child.Handle
[CompanyWiki.KillOnCloseJob]::Assign($ChildJobHandle, $ChildHandle)
```

在**本会话**中，只要 `Start-Process` 带 `-RedirectStandardOutput/-RedirectStandardError`
（启动器**每次**都带，因为它要把子进程 stdout/stderr 重定向到日志文件），返回的
`System.Diagnostics.Process` 的 **`.Handle` 为 `$null`** ⇒ `Assign` 抛
`Cannot convert argument "process", with value: "", for "Assign" to type "System.IntPtr"`
⇒ 启动器写入 `launcher_exception`、**exit 1**，且**根本到不了看门狗**。

证据链（逐条实测，非推断）：

| # | 探针 | 结果 |
|---|---|---|
| 1 | `harness/manual_supervisor_probe.py`（**不经 pytest**，直接用 iso 的 ps1 + 同一个假项目） | 2/2 次 `rc=1`，事件 `starting → launcher_exception`，消息即上面的 `Assign` 转换错误；`fake_worker_count.txt` 从未生成 |
| 2 | 红臂诊断 `red/diag3`（经 pytest，shim 已生效） | 同一条 `launcher_exception`；测试在 `assert completed.returncode == 0` 处红，`child_started` 计数 0 |
| 3 | PowerShell 内直接对照：`Start-Process … -PassThru` **带** redirect（TEMP 目标 / 仓库目标 / 仅 stdout / 仅 stderr / 加 `-NoNewWindow` / 加 delay+`Refresh()`） | **全部** `handle=[]` |
| 4 | 同上**不带** redirect | `handle=[2960]` ✓ |
| 5 | 裸 .NET：`[System.Diagnostics.Process]::Start($psi)` + redirect（`UseShellExecute=false`） | `handle=[3056]` ✓ —— 说明**不是 .NET 本身**，而是 PS `Start-Process` 在 redirect 分支需要重新 `OpenProcess` |
| 6 | `harness/openprocess_probe.py` / `openprocess_probe2.py`（ctypes `OpenProcess`） | `PROCESS_ALL_ACCESS`（`0x1F0FFF` 与 `0x1FFFFF`）对**一切**目标都是 **`winerror=5 ACCESS_DENIED`** —— 包括本会话自己刚生成的子进程、以及**本会话未生成**的 `explorer`；`PROCESS_QUERY_LIMITED_INFORMATION` / `PROCESS_QUERY_INFORMATION` / `PROCESS_TERMINATE` 可用 |

⇒ 结论：**本会话的进程令牌拿不到 `PROCESS_ALL_ACCESS` 句柄**，而 PS `Start-Process` 的 redirect
分支要的正是这种句柄。产品启动器**在本会话里根本无法成功启动第一个子进程**。

## C2. 为什么这不是"源卡结论变了"

- 源卡 2026-09-21 的同一台机器、同一份 ps1（sha 相同）产出过真实 `child_started` 事件
  （`band-child-*.json` 里每树 7–16 次 start、被杀 uptime 0.5xx s）⇒ **当时 `.Handle` 是拿到的**。
- 本会话为 DSH **workspace-write** 沙箱、**审批已禁用**（派单已声明"权限范围固定、不能在会话内放宽"）。
  `PROCESS_ALL_ACCESS` 被拒属于该进程隔离策略，**不在我可解除的范围内**。
- 因此阻断属于**会话环境**，与本卡修法、与源卡的时序归因**无关**：时序机制（0.5 s 看门狗 vs
  启动带宽）在本会话**根本不会被触发**，因为启动器在第一个 `Start-Process` 之后就退出了。

## C3. 对三臂可证性的后果（如实降级，不造绿）

| 臂 | 冻结判据 | 本会话可证性 |
|---|---|---|
| 红（修前 0.5 s） | §3.C：`assert N == 2` / `TimeoutExpired` 形态的红 | **形态不可证**：本会话所有运行会在更早的 `launcher_exception` 处红。三臂照跑并原样记录 rc/事件/负载，作为"阻断存在"的证据，**不得**读成"时序红被复现"。 |
| 绿（施加后） | §3.D：6/6 绿 | **不可证**（同一阻断）。⇒ `handoff.unverified` 登记为 `green_not_demonstrable_in_this_session`。 |
| 变异 M1（退回 0.5 s） | §3.E：≥1 红 | **不可证**（同上；且退不退回 0.5 s 都红，变异无判别力）⇒ 登记 `mutation_not_demonstrable_in_this_session`。 |

- 修法本身**仍然交付**：`after/changes.diff`（只含 `tests/**`）+ §3 的手算 expected 一起给
  reviewer，由其在能拿到 `PROCESS_ALL_ACCESS` 的会话（或由父把复跑派给权限更宽的会话）执行三臂。
- 本卡**不自签**任何 GREEN；`handoff.json.status=review_pending`、`implementer_signed=false`。
- 解除条件（供父/owner 派工）：在一个能以 `PROCESS_ALL_ACCESS` 打开自己子进程的会话里，
  按本文件 §4 的臂与 N 重跑三臂即可；oracle 无需重冻（expected 全部来自源卡原始数据）。

## C4. 本 addendum 之前已发生运行的登记（透明度）

1. 红臂第 1 次（`red/band-red.json`，N=6，cpu8）：6/6 `rc=1 / verdict=unknown`，全部在
   `tmp_path` fixture 阶段报 `PermissionError [WinError 5]`。原因 = pytest 用
   `mkdir(mode=0o700)` 建 basetemp，而本会话对 `mode=0o700` 目录做了"连 owner 都不可列"的 ACL
   （`os.mkdir.__doc__` 明确写着 *The mode argument is ignored on Windows*，本会话不成立）。
   **该臂整体作废为基础设施故障**，其产物保留在 `red/` 里不删；已加 harness 侧 shim
   （`harness/tside_probe.py`，强制 `mode=0o777` = 恢复 CPython 文档语义），三臂统一生效。
2. 受污染目录 `%TEMP%\i14ets\{d11,r11…r16,probeB,mode700,…}` **无法删除**（rmdir/rmtree 均
   `PermissionError`），故改用全新工作根 `%TEMP%\i14ets-b`（`harness/run_band.py`），三臂共用。
3. 诊断性运行（非臂）：`red/diag*`、`harness/manual_supervisor_probe.py`（2 次）、
   `harness/openprocess_probe*.py` —— 均为定位阻断，不是判据运行。
