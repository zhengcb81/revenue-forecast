# T3-DIAG · a20260927-01 —— 独立复审报告（reviewer，只读诊断 B 级轻审）

VERDICT: ACCEPT（P1 = 0；带 3×P3 + 4×unverified）

- **卡**：`T3-DIAG` ｜ **attempt**：`a20260927-01` ｜ **角色**：`reviewer`（独立复审工位，与诊断工位非同一人）｜ **原状态**：`review_pending`
- **回源被审 3 件（只读）**：`diagnosis.md` 8850B `90908cd9…`、`evidence.json` 7634B `ab0b8c11…`、`handoff.json` 1859B `733444fe…`
- **写入面 = 本目录仅 2 新文件**（`reviewer_report.md` + `reviewer_report.sha256`）；不写卡状态、不改被审 3 件与任何日志；零 git（含未跑 `git status`）、零联网、未装浏览器、未改产品码

## 1. 裁决行 + 发现清单核（四项轻核 #1）

| 核项 | 我的实测（回源） | 卡面声称 | 判定 |
|---|---|---|---|
| 09-20 log 裁决行 | L2 `status=not-ok ok=False exit_code=1`、L3 `detail=T3 suite exit 1`、L4 `argv=['weekly_t3_schedule.py','run-weekly']`；sha256 实算 `20b255a255214c2d…`、3660B | 同 | ✅ 逐字一致 |
| 09-27 log 裁决行 | L2/L3/L4 同上；sha256 实算 `dd9123ea3981de86…`、3684B | 同 | ✅ |
| 两败失败用例 | 两 log L8/L23 均 `DownloadE2E::test_download_cn_annual_report`，L9 `test_e2e_download.py:144`、L11 `AssertionError: 2 != 0`、L17-20 `stage=ensure/attempts=1/calls=3/downloads=0`、L24 `1 failed, 3 passed in 111.45s / 92.01s` | 同 | ✅ |
| `weekly_alert.jsonl` | 恰 4 行：09-06 `blocked`(exit 0, fully skipped)、09-13 `not-ok`(无报告文件)、09-20/09-27 `not-ok`(exit 1) | evidence.alert_journal 4 条同序同值 | ✅ |
| `weekly_manifest.json` | `latest_run_id=20260927T033001Z`、`ok:false`、`triplet.wiki=dbe47450…` | 处置一致 | ✅ |
| 09-13 手动两绿 | 两 log `status=ok ok=True exit_code=0`、`argv=['tools/weekly_t3_schedule.py', …]`、`4 passed in 78.35s / 56.02s` | counter_evidence 同 | ✅（sha 我补算 `0869914d…` / `b6d0e563…`，见 P3-2） |

## 2. ⭐根因核（四项轻核 #2）

- **runner 只补 `USERPROFILE`、未补 `LOCALAPPDATA` —— 属实**：`tools/weekly_t3_schedule.py` L106-123 内 `profile = PROJECT_ROOT.parent.parent`（L116）、`if profile.is_dir(): env["USERPROFILE"] = str(profile)`（L117-118）；全文件 grep `LOCALAPPDATA|PLAYWRIGHT` **0 命中**、`USERPROFILE` 仅 L110 注释 + L118 赋值 ⇒ GP-009 补丁对 Playwright 路径解析无效的判断成立。
- **两 log 失败用例确为 `test_download_cn_annual_report`、死于浏览器初始化 —— 属实**：两 log 根错误同为 `Browser init failed: BrowserType.launch: Executable doesn't exist at C:\WINDOWS\system32\config\systemprofile\AppData\Local\ms-playwright\chromium_headless_shell-1194\chrome-win\headless_shell.exe`，`stage: "ensure"`、`downloads: 0`（未发出任何下载），rc：CLI 返回 2 → 测试 `assertEqual(rc,0)` → 套件 exit 1（L2）。
- **旁证我另核**：① `Test-Path systemprofile\...\ms-playwright` = **False**，`…\chromium_headless_shell-1194\chrome-win\headless_shell.exe`（用户侧）= **True**；② 注册脚本 L293-295 确为 `-Weekly -DaysOfWeek Sunday -At 04:30` + `-UserId 'SYSTEM'`；③ 本机时区 `GMT Standard Time`（UTC+1）⇒ `run_id 03:30Z` = 本地 **04:30**，与 log 内 `[04:30:26/27]` 及触发器三方吻合（诊断 §七 的时间戳论据成立）。

## 3. 复现声明核（四项轻核 #3 —— 我本人自跑，非转述）

- **路径解析（`playwright install chromium --dry-run`，仅打印不下载）**：基线 → `C:\Users\郑曾波\AppData\Local\ms-playwright\chromium_headless_shell-1194`；仅把 `LOCALAPPDATA` 换成 systemprofile → `C:\WINDOWS\system32\config\systemprofile\AppData\Local\ms-playwright\chromium_headless_shell-1194`（两种情形 `USERPROFILE` 均为用户真值）⇒ **解析只看 `LOCALAPPDATA`，`USERPROFILE` 补丁不影响**。
- **launch 双跑（同一段 `chromium.launch(headless=True)` 内联 `%TEMP%` 执行，未建仓内文件，未导航任何页面/零出网）**：基线 **rc=0 / `LAUNCH-OK`**；模拟组（`LOCALAPPDATA`=systemprofile + `USERPROFILE` 按 runner 原样 + `PLAYWRIGHT_BROWSERS_PATH` 清空）**rc=1**，首行错误 `BrowserType.launch: Executable doesn't exist at C:\WINDOWS\system32\config\systemprofile\AppData\Local\ms-playwright\chromium_headless_shell-1194\chrome-win\headless_shell.exe` —— 与两份 log 的报错路径**同串**。
- **诊断自述的 `%TEMP%\t3-diag-repro\repro_browser.py` 实存**（2213B，2026-09-27 10:02），逐行读过：设计与 `evidence.json.repro.design` 描述一致（同段代码两跑、只改环境、清 `PLAYWRIGHT_BROWSERS_PATH`）⇒ **复现声明核 = 通过（我独立复跑得到同 rc/同错误）**。声明的「未重跑整套 T3/真实 CN 用例」理由（禁联网 + `run-weekly` 写仓）属实且已如实登记。

## 4. 四项归因核（四项轻核 #4）

| 归因排除 | 卡面证据 | 我的回源核验 | 判定 |
|---|---|---|---|
| 产品码缺陷 | ①09-13 手动两绿同码 ②失败在浏览器初始化之前 ③US/HK 真实用例两败均过 | ①两 log 实读 `4 passed`、argv 带 `tools/` 前缀（仓库根手动、交互用户环境）②`stage=ensure, downloads=0` 实读 ③两 log `F...`+`1 failed,3 passed`，测试类恰 4 例（cn/us/hk/seeded，us/hk 走 dayu、第 4 例种子，见 `test_e2e_download.py` L128/151/169/193）⇒ 过的 3 例即非 Playwright 链路 | ✅ 排除成立（③为结构推断，记 P3-3） |
| wiki sha `bf0c8b27→dbe47450` | triplet 只是运行时 git HEAD；测试用 `IsolatedWiki`；失败早于内容访问 | runner L265-267 实读 = `_head(...)` 三仓 HEAD 记录；`test_e2e_download.py` L62 `self.wiki = IsolatedWiki(Path(self._temporary.name))`；`stage=ensure/downloads=0` ⇒ 未到任何 wiki 读；manifest `wiki=dbe47450…`（"to"值对上），`bf0c8b27` 在既有 audit 记录中可溯（audit_report.md L107 等） | ✅ 排除成立 |
| 测试自身缺陷 | 测试如实暴露环境故障；门控/种子正常 | L144 断言实读；类级 `skipUnless` 门控（L57-58）未触发（套件真跑到 4 例出结果）；诊断另给哨兵改进建议并自认"有改进空间" | ✅ 排除成立 |
| 数据缺失 | `downloads: 0, calls: 3`，死在 discover 之前 | 两 log L17-20 实读（09-27 同）；`stage: "ensure"` ⇒ 未进数据层 | ✅ 排除成立 |

## 5. 发现分级

| 级别 | 编号 | 发现 | 处置 |
|---|---|---|---|
| **P1** | — | **无**（无归因错、无证据伪造：sha/裁决行/失败行/复现结果全部与我实测一致） | — |
| **P3** | P3-1 | `evidence.json.logs["20260927T033001Z"].key_lines` 漏摘 `"attempts": 1, "calls": 3` 两行（09-20 条有），而 diagnosis §二 称"逐项相同" | 摘录补齐即可；我已在原 log L19-20 实读两行均在，结论不受影响 |
| **P3** | P3-2 | 09-13 两份手动绿 log 未登记 sha256；"手动 vs SYSTEM"的区分靠 argv `tools/` 前缀推断（合理但无命令历史佐证） | 后续卡补 sha；我已补算 `0869914d…`/`b6d0e563…` |
| **P3** | P3-3 | "US/HK/种子 3 例通过"是 `F...` 模式 + 4 用例类结构的推断，log 未打印 passed 名单 | 属 log 粒度限制，非卡面过错 |

**P1 = 0 ⇒ `VERDICT: ACCEPT`（3×P3，不回退本诊断）。**

## 6. Unverified（如实登记）

1. **U1 计划任务注册体**：`schtasks /query /tn revenue_weekly_t3` 我复测同样 **Access denied**（非提升会话）⇒ SYSTEM 上下文仍只有三条间接证据（注册脚本 `-UserId 'SYSTEM'`、systemprofile 报错路径、04:30 时间戳），诊断 §七 已自曝，非隐瞒。
2. **U2 09-13 06:48Z 失败**：无报告文件，仅 `weekly_alert.jsonl` L2 佐证（F-B01-10 修复前历史缺口，诊断已披露）。
3. **U3 整套 T3/真实 CN 下载未复跑**：禁联网 + `run-weekly` 会写 `weekly_manifest.json`/`weekly_alert.jsonl`/新 log；修复后 SYSTEM 能否出网到 cninfo **未验证**（诊断 §六-4 已列为前提）。
4. **U4 套件子进程解释器**：`evidence` 称为 `C:\Miniconda\python.exe`（playwright 1.56.0/chromium 141→build 1194）；我只核了该解释器存在且 dry-run 结果一致，**未**从任务注册体反查 `sys.executable`（受 U1 ACL 限制）。

## 7. 我没做的事（边界声明）

- **没有写卡状态**：`handoff.json`（`review_pending`）、`diagnosis.md`、`evidence.json` 及 4 份日志、`weekly_alert.jsonl`、`weekly_manifest.json`、`tools/weekly_t3_schedule.py` 全部零字节改动（写入面 = 本 2 文件）。
- **没有 git**：0 次 git 命令（含未跑 `git status`）、无 git 写。
- **没有联网**：未调用任何 web 工具；`--dry-run` 仅打印、launch 未导航任何 URL、未下载任何二进制。
- **没有装浏览器、没有改产品码、没有修 runner**（§6-建议修复方向维持"供实施者"性质）；**没有重跑 T3 套件/真实 cninfo 下载**。
- **没有把 U1-U4 当成已验证**，也没有据此升 P1；**没有改动本 attempt 任何既有字节、没有代签 implementer**。
