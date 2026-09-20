# 隔离事件记录（父 agent 巡检，2026-09-20）

本文件记录本轮巡检中发现并处置的**生产仓库越界写入**与**不可归因的生产树变化**。
所有判断都附证据（路径、sha256、mtime、porcelain）。未做任何 `reset/stash/restore`；用户既有改动一律保留。

## 巡检口径

- 三个生产仓库：`C:\Users\郑曾波\Projects\{revenue-forecast,company-wiki,filing-fetch}`。
- 冻结基线：`execution_runs/I-00-A/a20260919-01/baseline.json` + `git_<repo>.txt`（2026-09-19 08:45 采集）。
- 判定方法：当前 `git status --porcelain`（剔除 `.planning/` 路径）与基线逐条 `Compare-Object`；
  另对基线登记过 hash 的文件做 sha256 复算。

## 事件 I-1：评审脚本把预注册文件写进生产仓库根（已处置）

- 文件：`C:\Users\郑曾波\Projects\revenue-forecast\prereg_expectations.json`
- 事实：size 3877 B，mtime `2026-09-20 02:59:55`，sha256 `35fbc83ded2707c8c611bc16276b826e05e0e256c6e39967ab09a2bc54a03a9f`
- 内容：M05–M08 四卡的**正例/连续性/defaults 预注册期望**（`M05.positive.hand = "200*3*1+20"` 等），
  与 M05–M08 定点复核 reviewer 的临时目录
  `%TEMP%\m05m08-review-20260920-025942\prereg_expectations.json` 同源（该目录创建于 02:59:42）。
- 归因：审计自身的 reviewer 脚本以**相对路径**写盘、而进程 cwd 恰为生产仓库根，属**我方越界写**，非用户文件。
- 处置：原件**先保全**为同目录
  `prereg_expectations.json.copied-from-repo-root`（sha256 与原件相同，已复算），随后从生产仓库根**删除**。
  副本同时存在于上述 `%TEMP%` 目录。删除后 porcelain 中不再出现该条目。

## 事件 I-2：`filing-fetch/git_filing-fetch.txt`（已处置）

- 文件：`C:\Users\郑曾波\Projects\filing-fetch\git_filing-fetch.txt`
- 事实：size 123 B，mtime `2026-09-19 11:05:23`，sha256 `43b964e376e77e30f4531bab71fcd7d6afa84496fe506328e675812eec6c160c`
- 内容（自指，证明是采集命令自身的输出被重定向到仓库根）：
  ```
  d35b6f5b09f1a7dad37d226504bf998802a852d7 2026-09-15T22:12:54+01:00
  ## fcap
  ?? git_filing-fetch.txt
  ?? git_filing-fetch.txt
  ```
- 归因：I-00-A 基线采集时以 `cwd = filing-fetch` 执行并把输出重定向到相对路径，落到了生产仓库根；
  该文件正是 I-00-A `dirty_evidence` 里登记的那一个。
- 处置：attempt 目录 `execution_runs/I-00-A/a20260919-01/git_filing-fetch.txt` 已有**逐字节相同**的保全副本
  （sha256 相同，已复算），故直接从生产仓库删除。删除后 `filing-fetch` 的 `git status --porcelain` 为**空**。

## 事件 I-3：`assurance/runs/daily_alert.jsonl` 新增一行（不归因本计划，未回退）

- 文件：`C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\daily_alert.jsonl`（porcelain ` M`）
- 新增内容（`git diff` 唯一差异，一行）：
  ```json
  {"at_utc": "2026-09-19T21:00:48.352933+00:00", "exit_code": 1, "outcome": "not-ok",
   "reason": "T2 runner produced a verdict: scan health: 2 NEW errors in the last 24h (budget 0)
              (ledger: latest daily run reported not-ok)",
   "run_id": "20260919T210001Z", "status": "stale"}
  ```
- 归因：格式与 `run_id` 口径即本仓每日告警作业自身的写法（`20260919T210001Z` 定时运行号，
  `at_utc 21:00:48Z` = 本地 22:00:48），**早于**本计划任何卡触碰该路径的时间：
  I-08-A 的 `after/git_status_after.txt`（mtime `2026-09-20 01:19:23`）里该条已是 ` M`。
  本计划所有卡都禁止写 `assurance/`，且无任何卡产出该文件——**不归因于本次审计**。
- 处置：**不回退**（可能是用户自有自动化产物，回退等于破坏用户数据）。仅登记，供 owner 判断。

## 事件 I-4：生产树若干"既有脏文件"在 `2026-09-20 02:24:00` 被批量重写（内容未变）

- 现象：`revenue-forecast` 中 `CHANGELOG.md`、`SKILL.md`、`references/*.md`、`assurance/runs/daily_alert.jsonl`
  的 mtime 同为 `2026-09-20 02:24:00`，接近本计划的一次提交（reflog：`02:23:50 reset: moving to HEAD`、
  `02:23:58 commit 7d7ea1e`）。
- 证据（内容未变）：`SKILL.md` 磁盘 sha256 `45e4e343eba4f6e766cdb163d21c35a7f7beeb603d3c8b237339de440dc47806`
  **等于** I-00-A 基线登记值（26378 B），即 mtime 变了、字节没变。
- 局限（诚实声明）：基线只登记了 `revenue-forecast/SKILL.md` 与两仓 `SKILL.md` 的 hash，
  其余 `references/*`、`CHANGELOG.md` 无基线 hash，**无法证明字节未变**；只能证明
  ①它们的 porcelain 条目与基线逐条相同；②`git diff` 仍只显示用户既有改动。
  为便于今后比对，本记录落盘当前值：
  | 文件 | sha256 |
  |---|---|
  | `CHANGELOG.md` | `bcba3dd50278b677ef0af63725a5d635763a40bd9f92089dfc37ff17529c0a8e` |
  | `references/backtesting.md` | `84336ecb1373baecf079949155f891121e70612ad150811532c129c556055196` |
  | `references/model-library.md` | `be45db0758f38d788839716477b14ec9cdd238c6160327b44a23fe01188920fa` |
  | `references/resource-business-guidance.md` | `93ebdadcc77a7f1fcc60dd64e7ece640b238b53e28fa93c793d84eddba7f27ba` |
  | `assurance/runs/daily_alert.jsonl` | `3d1f50fe7035df12d28fdb692314875ce0e6f1e2d971ca1605463b0d79ece559` |
- 归因：**未确定**（`.githooks` 与 `.git/hooks` 中均无 `stash`；`git stash list` 为空；工作区内容未被回退；`tools/pre_push_gate.py` 正文亦无 stash/checkout；其第 8 步 install-sync 的写目标是 `~/.agents`、`~/.codex` 安装根，其中 `~/.claude/skills/revenue-forecast` 只是指向 `~/.agents/...` 的 Junction，**都不是本仓库**）。
  登记为 provenance gap，不声称已解释。
- **第二次同类现象（登记，未解释）**：`2026-09-20 03:41:57` 同一批文件（`CHANGELOG.md`、`SKILL.md`、`references/*`、`e2e/expected/*.json`、`assurance/runs/daily_alert.jsonl`）mtime 再次被批量刷新，时点与本计划的第二次 `git push`（pre-push 门运行，`.mypy_cache`/`.ruff_cache` 于 03:42 更新）重合。两次现象都紧邻 git 提交/推送时点，且都**只触及既有的脏文件**、内容不变 —— 与"恢复后再写回"的形态一致，但**未找到执行该操作的具体步骤**，故仍按 provenance gap 登记，不推断机制。
- **内容不变的旁证（独立第三方复核）**：I-08-B 的独立 reviewer 对 02:24:00 批次的 61 个非 `.planning` 产品文件做了 `before/source_hashes.txt` 全量重算，**24/24 路径 drift=0**，并据此判定"内容零变化，mtime 不可作为零写入判据"。该结论与本记录一致，且**不依赖**本记录的解释。

## 生产不可变复核（同一轮巡检）

- `company-wiki` porcelain 仅 ` M CLAUDE.md`、` M README.md`（与基线一致，属用户既有改动）。
- 生产三模块磁盘 sha256（CRLF 工作区，与 HEAD blob 的 LF 形态天然不同，故另记 `git hash-object` 供对照）：
  `worker.py e83179915333…`（git `5d700302ca4b`）、`observability.py a73826aa10c9…`（git `d9ce30dfeb14`）、
  `cli.py fad88c60294a…`（git `c5038a9db4ec`）——与 I-14-C 收尾实测一致，未被本计划改动。
- 生产目录库不变量：`.source_catalog\catalog.sqlite3` size `49677344768` B、
  mtime `2026-09-19T06:31:35Z`、`-wal` 0 B（均与基线一致）；`-shm` 32768 B mtime `2026-09-20T02:25:33Z`
  （并发卡的只读触达，非写入）。
- `filing-fetch` porcelain 处置后为空；`revenue-forecast` 的 `.planning/` 之外条目与基线集合相比，
  仅少掉本计划**已提交**的 `assurance/runs/2026-09-11_r4-phase-b/*`（见 commit `a0ae426`、`7d7ea1e`），
  多出事件 I-3 的一条。
