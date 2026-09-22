# supersession 记录：K1/K2/K3 首轮 verdict 被覆盖（不可恢复的历史损失，如实披露）

- card: I-09-C；attempt: `a20260922-01`；写于 2026-09-22
- 性质：**harness 缺陷轮被修复轮取代是正当的**；问题只在本卡曾对父 agent 说「首轮 all_ok=false **如实保留**」——该措辞在盘上不成立。本文件按 (b) 路径处置：披露覆盖事实、转录我在会话内实际观测到的首轮数值、声明原 verdict 字节不可恢复（不伪造内容）。

## 1. 覆盖事实（时间线）

| 轮次 | 动作 | 盘上结局 |
|---|---|---|
| 第 1 轮（缺陷轮） | 首次全量 `run_fault_matrix.py`（无 `--only`），在 600 s 命令超时处被外层终止；该轮 stdout 未被捕获（工具回执为 `(no output)`） | 写出 `PC1-K1_prepare_before` / `PC1-K2_prepare_after` / `PC1-K3_json_before` 三个 `verdict.json`（all_ok=false）；`PC1-K3b_json_tmp_opened` 停在 pre-fault，无 verdict |
| 观测 | 我在会话内读取三个 verdict + fault.json，确认失败原因（见 §2 转录） | 此时盘上仍为首轮值 |
| 第 2 轮（修复轮） | PID 协议修复后执行 `--only PC1-K1… --only PC1-K2… --only PC1-K3… --only PC1-K3b… --force`；`--force` → `copy_inputs()` 对 `state/` 做 rmtree 后重建 | **三个 case 的首轮 `verdict.json`、`fault.json`、`state/*` 全部被同名文件覆盖/删除** |
| 现状 | 修复轮 verdict 为 all_ok=true（K1/K2/K3 各 26 检查、K3b 27 检查） | **首轮 verdict/fault/state 字节不可恢复**（无 attempt1/round1 副本；首轮全量 stdout 也未落盘——命令超时且无输出回执） |

## 2. 首轮观测转录（来源：本卡会话内工具输出；**非盘上重测**，原文件已被覆盖）

对父 agent 全扩展名递归搜索「零命中 all_ok=false」的解释：**搜索当时（修复轮之后）盘上确已无首轮 verdict**；下列数值是我在覆盖发生前读到的原样内容。

### PC1-K1_prepare_before（首轮）
- `elapsed_seconds = 182.83`
- `rc_expectation_vs_raw`: expected=`kill`, raw=**（空）**
- 失败检查（唯一）：`fault_raw_returncode_is_harness_kill | expected=4242 | actual=(空) | real process termination`
- `fault.json`: `barrier_reached=false`、`registered_in_manifest=false`、`kill` 缺失、`raw` 缺失、
  `harness_problem = "kill case: barrier not reached and process still alive after 60s — left running (kill forbidden for unregistered barrier)"`
- `fault_argv` 里 `Popen.pid = 45816`；同目录 state 实际存在的是 `pid_42452.json`、`barrier_42452.json`、`writer_start_42452.json`（**且无** `writer_exited_42452.json`）

### PC1-K2_prepare_after（首轮）
- `elapsed_seconds = 182.62`；同样唯一失败检查为 `fault_raw_returncode_is_harness_kill`；raw 空；barrier/registered=false；harness_problem 同上

### PC1-K3_json_before（首轮）
- `elapsed_seconds = 182.89`；同样唯一失败检查为 `fault_raw_returncode_is_harness_kill`；raw 空；barrier/registered=false；harness_problem 同上

### PC1-K3b_json_tmp_opened（首轮）
- 无 `verdict.json`、无 `fault.json`（停在 seed/fault 启动阶段，随 600 s 外层超时终止）

## 3. 首轮失败的归因（harness 缺陷，非产品观察）

Windows venv 的 `Scripts\python.exe` 是 **launcher**：它再起一个子解释器执行代码，因此 `Popen.pid`（45816）≠ 实际运行 `writer.py` 的 `os.getpid()`（42452）。首轮 orchestrator 用 `Popen.pid` 去找 `barrier_<pid>.json` / `pid_<pid>.json`，必然找不到 → 每例空等 120 s（barrier 超时）+ 60 s（communicate 超时）≈ 182 s，且按「未登记 PID 不得 kill」的停止条件拒绝 kill → raw rc 为空。**该轮结果只证明 harness 的 PID 假设错误，不构成任何关于产品发布事务的观察。**

## 4. 修复内容（已在修复轮验证）

1. `writer.py`：manifest 同时登记 `pid = os.getpid()` 与 `parent_pid = os.getppid()`（两者都在 new_run manifest 内）。
2. `run_fault_matrix.finish_spawned`：改为「按 mtime 扫描 `barrier_*.json` → 读 barrier 内 pid → 校验 `pid_<pid>.json` 存在 → 只杀该已登记 PID」，并记录 `target_pid` / `kill.ok` / `target_process_still_alive` / `writer_exited_<target>.json` 缺席。
3. kill 判定链改为：barrier 到达 ∧ manifest 登记 ∧ kill 执行 ∧ 退出记录缺席（finally 未运行的直接证据）∧ 目标进程消失；raw rc 与 expected 分列记录（修复轮实测 raw=**4242**，经 launcher 转发）。
4. 同轮另修：`copy_inputs` 删除只读 registry 位（首轮之后曾致 `PermissionError WinError 5`，见 orchestrator 内注释）；P0 输入 as_of 方向（−1 d 违反 claim information set → +1 d）。

## 5. 纪律声明

- 本文件**不伪造**首轮 verdict 内容；§2 明确标注为「会话内工具输出转录、原文件不可恢复」。
- 修复轮的 4 个 verdict 是当前有效记录；首轮失败以本 supersession 为唯一留痕。
- 本记录路径进入 `handoff.json.carried_findings`。
- 判据未被修改：kill 臂的通过标准与首轮相同（4242/退出记录缺席/manifest 登记），变的是 harness 找对 PID。
