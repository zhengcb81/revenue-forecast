# recovery/ — I-14-E

本卡是测量卡，不改产品代码，因此没有"回退实现"的对象。恢复语义只有三条：

1. **测量副作用**：每次运行都在 short `%TEMP%\i14e-*` 下新建 basetemp 目录；脚本结束即停掉
   自己拉起的负载进程（`harness/load.py` 的 `Load.stop()`）并回收该次运行残留的
   launcher/子进程（`harness/run_band.py` 的 `reap()`，只匹配本次运行事件里记录的 PID），
   条件开始时还会按"`-ProjectRoot` 指向本 driver 自己的 scratch root"这一窄条件清扫上一轮残留
   （`sweep_leftovers()`），因此不会误杀其它会话的进程。
2. **现场保留**：`%TEMP%\i14e-*` 的 scratch 目录**故意不删**（与冻结带同样留现场），
   每次运行的 stdout 与 launcher 事件另外复制进 `after/band-captures-*/`，即使 scratch 被清理
   也能复核。
3. **重复运行**：重跑任一条件不需要恢复步骤；本卡没有写生产仓，也没有改产品测试，
   重跑只会在 `after/` 覆盖本 attempt 自己的证据文件（reviewer 若已读旧值，以
   `after/analysis.json` 与 `handoff.json` 里记录的 hash 为准）。

已知需要人工收尾的情形：若某次运行在 `subprocess.run(timeout=15)` 之后仍留下
`powershell.exe` 形式的 supervisor，可按下述**窄条件**清理（不要无差别杀 powershell）：

```powershell
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
  Where-Object { $_.CommandLine -like '*-File*source_catalog_worker.ps1*' -and
                 $_.CommandLine -like '*i14e-*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

（本 attempt 结束时 `after/final_hashes.json` 记录生产仓锚点未变；scratch 清理状态见
`handoff.json.evidence_paths`。）
