# recovery/ — 恢复边界与停止条件记录（I-09-C / a20260922-01）

## 恢复边界（card 原文，逐字）

> 只停止测试进程并保留scratch证据；恢复上一个完整测试包；真实registry/用户包绝不触碰；失败退回I-09-B并保留反例

## 本卡实际执行

- **只停止测试进程**：全部 kill 均为 `TerminateProcess(4242)`，且每次都先核对
  `barrier_<pid>.json` + `pid_<pid>.json`（new_run manifest）→ 未登记 PID 的 kill 次数 = **0**。
  （manifest 同时登记 `os.getpid()` 与 launcher `parent_pid`，两者均在登记范围内；
  launcher 追加终止只在子进程死后 30 s 未退出时发生，且记录于 `fault.json.launcher_kill`。）
- **恢复上一个完整测试包**：每个 fault 例先 seed **P0**（完整上一发布），故障只作用于 P1；
  所有 verdict 均检查 `p0_not_deleted_or_rewritten`（字节级 hash 前后相等）与 `p0_consumable`。
- **真实 registry / 用户包绝不触碰**：全部 registry 是 `evidence/cases/<case>/state/registry/`
  或 `evidence/tpub|PC3|PC5` 下的新建隔离路径；`REVENUE_PUBLICATION_REGISTRY` 每子进程显式注入；
  生产 `artifacts/registry/publications.jsonl` 零读写升级（未打开过）。
- **失败退回 I-09-B 并保留反例**：F5（锁未实现，不可构造）与 F12（stdout 断管 rc=120 超出冻结
  数值域）作为反例原样保留于各自 `verdict.json`/`pipe_controls.json`，进 `handoff.carried_findings`。

## 恢复类证据位置

- 每个 fault 例的两次恢复：`evidence/cases/<case>/recovery1.json`、`recovery2.json`
  （各为**全新进程**）+ `reader_after_recovery1.json`、`reader_after_recovery2.json`。
- P-C4a（恢复中再 kill）：`evidence/cases/PC4a_kill_during_recovery/recovery_killed.json`
  → 其后两次干净恢复 → 幂等/链/P0 检查见该例 `verdict.json`。
- P-C4b（损坏成员 hash）：`corruption.json` → fail-closed 诊断 → 两次恢复收敛。

## 现场清理说明（如实披露）

- `--force` 重跑会 `copy_inputs()` → 先 chmod 清除只读位再 `rmtree` **本 case 自己的** scratch
  `state/`（含其隔离 registry），再重建。这是 case 级隔离重置，不是“删历史行来变绿”：
  - 被覆盖的唯一一轮：K1/K2/K3 首轮（harness PID 缺陷轮），已按
    `evidence/k_arms_first_attempt_supersession.md` 披露（旧 verdict 字节不可恢复）。
  - F7（torn line）例的 registry **从未**被修复或删行：两次恢复 fail-closed，
    `registry_bytes_unchanged_no_history_deletion` 检查通过。
- 无任何停止条件触发（详见 `handoff.json.stop_condition_log`）。
