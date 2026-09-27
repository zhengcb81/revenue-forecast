# T3 套件两连败 只读诊断（2026-09-27）

- 诊断工位：`role=diagnostician_t3`，授权：`§四十裁定三`（owner §四十）
- 纪律遵守：只读；未改任何产品码/数据；复现全部在 `%TEMP%\t3-diag-repro\`；零 git 命令；零联网
- 产出目录：`execution_runs/T3-DIAG/a20260927-01/`

## 一、结论（TL;DR）

**两连败根因**：周计划任务以 **SYSTEM 服务账户**运行（注册脚本 `-UserId 'SYSTEM'`，触发器周日 04:30，与 log 内 `[04:30:26/27]` 时间戳吻合），Playwright 在 Windows 按 `%LOCALAPPDATA%\ms-playwright` 解析浏览器；SYSTEM 的 LOCALAPPDATA 指向 `C:\WINDOWS\system32\config\systemprofile\AppData\Local`，其下 **`ms-playwright` 目录根本不存在**。`tools/weekly_t3_schedule.py` 的 GP-009 修复（2026-09-08）只补了 `USERPROFILE`（第 116-118 行），**没有覆盖 `LOCALAPPDATA`/`PLAYWRIGHT_BROWSERS_PATH`**，对 Playwright 的路径解析完全无效。于是 `test_download_cn_annual_report` 在浏览器初始化即死，CLI 返回 2，pytest 断言 `rc==0` 失败 → 套件 exit 1。

**归因**：纯环境/部署问题（浏览器二进制未为 SYSTEM 账户安装）。**不是**产品码回归、**不是** wiki sha 变化（bf0c8b27→dbe47450 无关）、**不是**测试自身缺陷（测试如实暴露了环境故障）。证据见下。

## 二、两败逐条归因

### 09-20（weekly-run-20260920T033000Z.log，3,660B，sha256 20b255a2…）

| 项 | 内容 |
|---|---|
| 失败用例 | `DownloadE2E::test_download_cn_annual_report`（宁德时代 FY2024，经 StockInfoDLSimple/cninfo） |
| 断言行 | `tests/test_e2e_download.py:144` `self.assertEqual(rc, 0, out + err)` → `AssertionError: 2 != 0` |
| 根错误 | `adapter stockinfo-cninfo discover exited 1: Browser init failed: BrowserType.launch: Executable doesn't exist at C:\WINDOWS\system32\config\systemprofile\AppData\Local\ms-playwright\chromium_headless_shell-1194\chrome-win\headless_shell.exe` |
| 阶段 | `stage: "ensure"`，`attempts: 1, calls: 3, downloads: 0` —— 死在浏览器初始化，未发出任何下载 |
| 套件结果 | `1 failed, 3 passed in 111.45s`（`F...`：仅 CN 用例失败；US/HK 走 dayu-agent、第 4 例用种子数据，均不依赖 Playwright） |

### 09-27（weekly-run-20260927T033001Z.log，3,684B，sha256 dd9123ea…）

与 09-20 **逐项相同**（同用例、同断言行、同根错误、同 build 1194、同 `downloads: 0`），仅时长 92.01s。两败是**同一故障的周重复**，非新回归。

## 三、决定性证据链

1. **文件系统事实**（Test-Path 实测）：
   - `C:\WINDOWS\system32\config\systemprofile\AppData\Local\ms-playwright` → **不存在**（整个目录缺失）
   - `C:\Users\郑曾波\AppData\Local\ms-playwright\chromium_headless_shell-1194\chrome-win\headless_shell.exe` → **存在**（报错点名的正是这个 build）
2. **Playwright 路径解析只看 LOCALAPPDATA**：`python -m playwright install chromium --dry-run`（只打印不下载）在正常环境解析到 `C:\Users\郑曾波\AppData\Local\ms-playwright\...`；把 `LOCALAPPDATA` 换成 systemprofile 路径后立即解析到 `C:\WINDOWS\system32\config\systemprofile\AppData\Local\ms-playwright\...`。runner 的 `USERPROFILE` 补丁不影响此解析。
3. **同码异境的一手对照**：09-13 当天 19:40/19:42 两次**手动**运行（argv 带 `tools/` 前缀 = 仓库根手动调用，交互用户环境）`4 passed` 全绿（weekly-run-20260913T194021Z.log 78.35s、…194234Z.log 56.02s）；周日 SYSTEM 运行同套件必红。**同一产品码，唯一系统差异 = 运行账户的 LOCALAPPDATA。**
4. **%TEMP% 隔离复现**（见 §四）：模拟 SYSTEM 环境 → rc=1 且错误串与 log 逐字节一致（含 build 1194，playwright 1.56.0/chromium 141）；用户环境基线 → rc=0 `LAUNCH-OK`。

### 时间线（解释"为什么 09-13 之后才连败"）

| 时间 | 事件 |
|---|---|
| 09-06 03:30Z | 周日 SYSTEM 运行：套件整体 skip → `blocked`（GP-009 之前的 `Path.home()` 问题） |
| 09-08 | GP-009：runner 给 `USERPROFILE` 打补丁 → 工具能找到，套件开始**真跑** |
| 09-13 06:48Z | 周日 SYSTEM 运行：CN 用例同因失败；当时报告文件机制缺失（F-B01-10），**无 log 可查** → `not-ok` |
| 09-13 19:40/19:42 | 当晚修复 F-B01-10/B.VR903-05 后**手动**验证：`4 passed` ×2（交互用户环境，全绿） |
| 09-20 03:30Z | 周日 SYSTEM 运行：同因失败，报告机制已生效 → 两连败之第一败 |
| 09-27 03:30Z | 周日 SYSTEM 运行：同因失败 → 第二败 |

即：GP-009 让套件"能跑"之后，凡 SYSTEM 上下文的真实运行**从未绿过**；09-13 的绿色记录全部来自交互用户环境的手动验证，掩盖了 SYSTEM 侧浏览器缺失。

## 四、当前复现结果（2026-09-27，%TEMP% 隔离）

- 方式：`%TEMP%\t3-diag-repro\repro_browser.py`，同一段 `chromium.launch(headless=True)` 代码跑两遍，仅环境不同（`USERPROFILE` 按 runner 原样补丁；`PLAYWRIGHT_BROWSERS_PATH` 清空；模拟组把 `LOCALAPPDATA` 指向 systemprofile）。**零联网**（只启动并立即关闭浏览器）；解释器 `C:\Miniconda\python.exe`（playwright 1.56.0，即套件子进程链实际使用的解释器）。
- **基线（用户环境）：rc=0，`LAUNCH-OK`** —— 浏览器二进制本身完好。
- **模拟 SYSTEM 环境：rc=1**，`BrowserType.launch: Executable doesn't exist at C:\WINDOWS\system32\config\systemprofile\AppData\Local\ms-playwright\chromium_headless_shell-1194\chrome-win\headless_shell.exe` —— 与两份 log 的报错路径**逐字节一致**。
- **结论：故障条件今天仍在 → 下个周日仍将 exit 1，未自愈。**

### 未做的复现及原因（如实声明）

- **未重跑整套 T3 套件/真实 CN 下载用例**：该用例需访问 cninfo（禁联网），且 `run-weekly` 会写 `weekly_manifest.json`/`weekly_alert.jsonl`/新 log（禁写仓库）。上面的模拟复现已覆盖决定性条件（浏览器解析路径），不影响结论。

## 五、排除项（给证据）

| 假设 | 裁定 | 证据 |
|---|---|---|
| 产品码改动 | **排除** | ① 09-13 两次手动全绿（同码）；② 失败点在浏览器初始化（`stage: ensure`、`downloads: 0`），尚未执行任何产品断言；③ 同链路的 US/HK 真实下载用例在两败中均通过 |
| wiki sha 变化 bf0c8b27→dbe47450 | **排除** | triplet 只是运行时记录的三仓库 git HEAD（weekly_t3_schedule.py L265-267）；测试用 `IsolatedWiki` 临时 wiki（生产 wiki 仅在 setUp 拷贝 security_master，且两败中 setUp 均已成功）；失败发生在任何 wiki 内容访问之前 |
| 测试自身缺陷 | **排除**（有改进空间） | 测试正确暴露了环境故障；它自己的门控/种子逻辑正常。改进建议见 §六-3 |
| 数据缺失 | **排除** | `downloads: 0, calls: 3`：死在 discover 之前的浏览器初始化，根本没到数据层 |

## 六、建议修复方向（供实施者，本工位未改任何代码）

1. **最小修复（推荐）**：`tools/weekly_t3_schedule.py::_run_t3_suite` 在现有 `env["USERPROFILE"]` 补丁旁补一行同源推导：`env["LOCALAPPDATA"] = str(profile / "AppData" / "Local")`（或显式 `env["PLAYWRIGHT_BROWSERS_PATH"] = str(profile / "AppData" / "Local" / "ms-playwright")`）。与 GP-009 同思路，把 Playwright 实际读取的变量一并指向真实用户 profile。
2. **替代方案**：以 `PLAYWRIGHT_BROWSERS_PATH` 指向机器级共享目录（如 `C:\ProgramData\ms-playwright`）安装一次浏览器，runner 与交互会话统一读该变量；对"服务账户无用户 profile"的场景最稳。
3. **哨兵改进（防再误判）**：CN 用例/适配器可在 `launch` 前预检浏览器二进制，缺失时打印 `T3-SUITE-COULD-NOT-RUN` 哨兵——runner 会据此判 `blocked`（机器问题）而非 `not-ok`（产品背锅）。当前因 3 例通过、达到 verdict，heuristic 分支不会触发，`not-ok` 分类符合设计但归因成本高（本次诊断即为代价）。
4. **前提提醒**：修好浏览器路径后，SYSTEM 账户还必须能访问 cninfo 出网，套件才可能真绿；超出本工位范围，实施者需一并验证。

## 七、诊断局限

- `schtasks /query /tn revenue_weekly_t3` 拒绝访问（非提升会话）；`Get-ScheduledTask` 全表扫描亦未见该任务的动作（不可见性受 ACL 限制）。SYSTEM 运行上下文改由三条间接证据支撑：注册脚本 `-UserId 'SYSTEM'`、报错路径在 systemprofile、log 内 `[04:30:26/27]` 与注册触发器"周日 04:30"吻合。
- 09-13 06:48Z 的失败无报告文件（F-B01-10 修复前的历史缺口），只能由 `weekly_alert.jsonl` 第 2 行佐证。
