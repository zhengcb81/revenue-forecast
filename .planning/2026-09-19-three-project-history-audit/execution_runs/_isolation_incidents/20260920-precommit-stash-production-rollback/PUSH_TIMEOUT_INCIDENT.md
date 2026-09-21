
---

## 推送连续失败的真根因（2026-09-21 22:0x，症状第三次出现但根因不同）

**症状**：`git push` 连续失败，但本地 `drift_patrol` 七项 **ALL_GREEN**、本地 gate 单独跑也 GREEN，`git fetch` 显示 `ahead=5 behind=0`（无分叉）。

**完整输出揭示的真根因**（此前只看到 `error: failed to push some refs`，因为我把输出过滤得太窄）：
```
subprocess.TimeoutExpired: Command ['python', '-m', 'pytest', '-q', '--tb=short',
  'tests/test_zr803_chaos_recovery.py', 'tests/test_zr1103_journey_reverify.py',
  'tests/test_ca203_weekly_t3.py', 'tests/test_fc1101_ci_manifest.py',
  'tests/test_compatibility_manifest.py', 'tests/test_fc1002_three_process_e2e.py',
  'tests/test_ca302_three_journeys.py'] timed out after 600 seconds
PUSH BLOCKED by pre-push gate (CI root-fix protocol). Fix the root cause; do not bypass.
```

**根因**：**编排层自身的并发 subagent 把机器压满** —— I-14-E 正在跑 pytest 重启带战役、B1/B3/B5 在跑各自测试套件，导致 pre-push 门的 7 个 E2E 文件（含**三进程旅程**）超出 **600 s** 上限。**这不是测试失败，是超时。**
**交叉印证**：这正是 I-14-F / I-14-E 两卡独立记录并立卡的"**并发负载带**"现象（I-14-F 观测到"本机有来自其他会话的并发 pytest 战役，PID 已记录"）。

**教训（方法层面，重要）**：
> 我用 `Select-String` 过滤推送输出，把决定性信息（`TimeoutExpired` + `PUSH BLOCKED ... Fix the root cause`）**滤掉了**，于是连续三次只看到 `failed to push some refs`，并据此作出"门红 / 规格漂移 / 分叉"的**错误推断**，白花三轮。
> **新纪律**：推送失败时**必须捕获完整原始输出**（至少最后 15 行），**不得先过滤再看**；过滤只用于已确认成功的路径。

**正确处置**：等并发 subagent 落盘、机器静默后再推送；或把 E2E 套件视为"已知负载敏感项"，在低负载窗口重试。**不得绕过门**（门自身提示即为 `do not bypass`）。

**状态留痕**：本事件发生时 `unpushed = 5`，本地 gate `ALL_GREEN`，生产锚点完好。
