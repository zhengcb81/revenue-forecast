# I-14-E：一次 runner 驱动全部证据收集（先看结果，再按需重跑）

本文件不是命令本身，而是**接续说明**：所有实际执行的 argv 已逐条抄进 `commands.json`
（由 `harness/sync_commands.py` 从 `after/campaign.log` / `after/campaign-band.log` 转录，
不是重打一遍）。这里给出**顺序**与**依赖**，便于 reviewer 或下一位执行者按需重跑：

```
1  harness/freeze.py                     -> evidence/freeze_instant.json        (oracle 冻结记录)
2  harness/extract_frozen_band.py        -> evidence/frozen_band_raw_record.json (冻结带原始记录)
3  harness/build_binding_hashes.py       -> evidence/binding_hashes.json        (树/锚点 hash)
4  harness/run_campaign.ps1              -> after/child-lifetime-*.json
                                            after/wrapper-latency-*.json
                                            after/campaign.log
5  harness/run_band_steps.ps1            -> after/band-*.json
                                            after/band-captures-*/, after/campaign-band.log
6  harness/concurrent_activity.py        -> after/concurrent-activity.jsonl      (并发活动采样)
7  harness/collect_artifacts.py          -> after/artifacts-*.json + after/artifacts-*/  (工件存在性)
8  harness/analyze.py                    -> after/analysis.json
9  harness/fail_able_cases.py            -> after/fail-able-cases.json
10 harness/final_hashes.py               -> after/final_hashes.json              (生产仓未被写入)
11 harness/sync_commands.py              -> commands.json
```

依赖与边界：

- 第 4/5 步必须在第 1–3 步之后（先冻结、先绑定）；第 7 步必须在第 5 步之后。
- 第 4 步曾因 `run_campaign.ps1` 里把仓库路径写成**非 ASCII 字面量**而被 PowerShell 解析器
  误码（5 个 M-B 步骤秒退，见 `after/campaign.log` 的 traceback），因此拆出第 5 步用
  `$env:USERPROFILE` 推导路径。这是**已登记的运行器缺陷**，也是为什么 M-A 与 M-B 的日志分成两份。
- 第 6 步与会话并发运行，代价是每 20 s 一次 CIM 查询；它不产生被测进程。
- 全部脚本对生产三仓只读；`%TEMP%\i14e-*` 是 scratch，**故意保留**（reviewer 可复核；见
  `recovery/README.md`）。
