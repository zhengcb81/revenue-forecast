# I-04-D 回滚与恢复配方

适用对象：独立 reviewer，或接手本卡下一步的 agent。
attempt 根 `<A>` = `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-04-D\a20260919-01`。
PLAN 根 `<P>` = `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`。
本卡 `status = review_pending`，实现者不自签 accepted。以下命令都是 argv 风格；`<...>` 是占位符，不是字符串拼接。

---

## 1. 把 iso 副本恢复到基线（逐字节）

**基线 = I-04-B 的已验收输出**，不是生产代码：

- 基线路径：`<P>\execution_runs\I-04-B\a20260919-01\iso\filing-fetch\scripts\fetch_filing.py`
- 基线 sha256：`dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c`（56405 bytes）

恢复方式（二选一，都只碰 `<A>\iso`，不碰生产）：

1. 只回滚被测源码这一个文件（最小回滚，用于"上个完整版本仍可用"的验证）：

```
robocopy "<P>\execution_runs\I-04-B\a20260919-01\iso\filing-fetch\scripts" "<A>\iso\filing-fetch\scripts" "fetch_filing.py" /NJH /NJS
```

2. 整树回滚（把整个 iso 副本恢复到 I-04-B 形态；`/E` 复制子目录并排除 `__pycache__`，与本卡建立副本时同法）：

```
robocopy "<P>\execution_runs\I-04-B\a20260919-01\iso\filing-fetch" "<A>\iso\filing-fetch" /E /XD __pycache__
```

回滚后必须复算并核对：

```
powershell -NoProfile -Command "(Get-FileHash -LiteralPath '<A>\iso\filing-fetch\scripts\fetch_filing.py' -Algorithm SHA256).Hash.ToLower()"
```

期望值 = `dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c`。**不相等就停下**：说明回滚没到位，或基线被别的东西动过（此时按 START_HERE 的漂移分支暂停受影响步骤，而不是继续跑）。
注意：整树回滚**不会**删除 `iso/filing-fetch/scripts/i04d_*.py` 与 `iso/filing-fetch/tests/test_fetch_filing_lease.py`（robocopy 是复制，不是镜像）。若要彻底回到 I-04-B 状态，回滚后手动删掉这四个本卡新增文件（它们的 hash 见 §3）。

**隔离要求**：恢复/演练请在 `<A>` 下的 scratch 目录里做（或整树复制一份再恢复），不要就地覆盖后直接继续跑——保留现场是 START_HERE 的第 8 步要求。

---

## 2. 重新施加本卡的实现（patch）

本卡的实现是**确定性生成**的，不是手改。先做只读预检（证明补丁与基线逐字匹配、列出将做的 5 处编辑、不写盘；本卡的 `I04D-02-patch-dry-run`，rc=0）：

```
<A>\iso\venv\Scripts\python.exe -X utf8 <A>\scratch\patch_i04d.py --check
```

再施加：

```
<A>\iso\venv\Scripts\python.exe -X utf8 <A>\scratch\patch_i04d.py --apply
```

- **幂等**：重复执行得到同一份输出。
- **拒绝条款**：**基线的 sha256 不匹配它就拒跑**（这是脚本的硬校验，不是提示）。所以第 1 步的回滚必须精确到 `dc593a75…af1c`；如果你手上的基线 hash 不同（例如 I-04-B 产物被换过），patch 会拒绝执行——这时**不要**绕过校验去手改源码，应先把差异报给 owner。
- 施加后的期望结果：`<A>\iso\filing-fetch\scripts\fetch_filing.py` = sha256 `a72546c50401a4b1876288bea6b6d7e4a72db9c39fd028c7bfb75a6f929ad198`（126274 bytes），并落盘 §3 列出的三个 helper 与一个测试文件。

---

## 3. 重跑两套检查（确切 argv）

工作目录都是 `<A>\iso\filing-fetch`。**命令的权威登记表是 `<A>\commands.json`**（8 条已跑命令的 argv/cwd/`expected_returncode`/`raw_returncode`/产物，另有 `not_run` 的变异证明）；下面的 argv 与它一致。本卡**不**把 `scratch/REPORT.md` 里的摘要行当证据。

**(a) 18 项 lease 断言套件（RED 与 GREEN 用的是同一条 argv，各自独立的 basetemp）：**

```
<A>\iso\venv\Scripts\python.exe -X utf8 -B -m pytest tests/test_fetch_filing_lease.py -q -p no:cacheprovider --basetemp=<A>\recovery\basetemp-<新编号>
```

- 在**基线**（回滚后、未 patch）上跑：期望 `rc = 1`，`17 failed, 2 passed, 2 skipped in 14.59s`（原始日志 `before/i04d-red.txt`，sha256 `c632a3a8d260b343dd8af24ff777a80c2b2f4f56665c4bd98f9499dd67b0e92f`；那次调用的 basetemp 是 `before/lease-pytest`）。
- 在**本卡输出**（patch 后）上跑：`rc = 1`，`18 passed, 3 failed`（原始日志 `after/i04d-green.txt`，sha256 `f8220c7d29c82cde12ff44e267523c12698dc64ab58e2d6f45fc7afddf2a3115`；那次调用的 basetemp 是 `after/lease-basetemp` —— `after/` 下另有 `lease-pytest-green/`、`lease-basetemp2/3/4/` 等同名旧 basetemp，**不要**用目录名推断是哪一次运行，以 `commands.json` 的 `I04D-06-t-filing-green` 与日志内容为准）。**这 3 个失败是已知的 harness 顺序敏感断言，不是全绿**；性质与处置见 `review.md` §3 与 §5(a)。
- `--basetemp` 必须指向**本次新建的空目录**（临时目录或 `<A>\recovery\` 下的新目录）。**绝不能**指向 attempt 根、`evidence/` 根、`before/`、`after/` 或上一次的 basetemp：pytest 会清理 basetemp 目标（本卡构建期就踩过一次 case 根被 basetemp 清掉的坑）。
- 失败案例的测试节点名（供 `-k` 单点复现，取自 basetemp 目录名，前 30 字符）：`test_f_l5_ownership_transfer_i0`、`test_f_l5_two_processes_one_pa0`、`test_f_l6_sequential_cycles_ea0`、`test_f_l6b_exactly_one_resume_0`、`test_f_l7_inner_release_remove0`、`test_f_l7b_and_l7c_nesting_var0`、`test_f_l8d_owner_evidence_chan0`、`test_f_l9a_user_pause_is_respe0`、`test_f_l9c_user_pause_during_o0`、`test_l8a_w1_no_owner_marker_is0`、`test_l8b_w2_takeover_resumes_b0`。单点复现示例：

```
<A>\iso\venv\Scripts\python.exe -X utf8 -B -m pytest tests/test_fetch_filing_lease.py -q -p no:cacheprovider --basetemp=<A>\recovery\basetemp-l8a-w1 -k test_l8a_w1_no_owner_marker_is0
```

**(b) 19 例真实多进程调度案例**（主证据；每个案例一个独立 run 目录）：

```
<A>\iso\venv\Scripts\python.exe -X utf8 <A>\iso\filing-fetch\scripts\i04d_schedule.py run I04D-CASE-<case> --out <A>\recovery\run\<case>
```

案例名（`evidence/run/` 下的 19 个目录，前缀 `I04D-CASE-`）：`F-L5`、`F-L6`、`F-L6b`、`F-L7`、`F-L7b`、`F-L7c`、`F-L8a-W1`、`F-L8a-W1b`、`F-L8b-W2`、`F-L8c-W4`、`F-L8d`、`F-L8g-UNKNOWN`、`F-L8h-WRITEFAIL`、`F-L9a`、`F-L9c`、`F-LK-TIMEOUT`、`F-LK-TIMEOUT-ZERO`、`F-LK-HOLDER-CRASH`、`F-LK-NEVER-UNLINK`。
复核时看每例的 `summary.json`：`pause_calls`、`resume_calls`、`lock_acquisitions`、`final_lease`、`final_worker_state`、`harness_error`、`participants.<tag>.{pid,exit_code,elapsed_seconds}`；以及 `report.<tag>.json` 与 `worker.jsonl`（"谁真的发了 pause/resume"由 journal 里的 `pid`/`ppid` 判定）。
**每例都要用新的 `--out` 目录**；不要覆盖 `evidence/run/` 下的原始记录（原始记录是本次交审的证据，重跑只能写到 recovery/ 或下一 attempt）。

崩溃注入按 oracle.md §1/§5 的固定点与退出码：W1 → 90、W2 → 91、W4 → 92，只由 `I04D_HOOKS=crash:<point>:<code>` 触发。

---

## 4. 本卡可能起过的进程，以及 kill 规则

本卡起过的进程只有三类，**全部是测试角色**：

1. `iso/venv/Scripts/python.exe` 起的**参与者进程**（`i04d_participant.py`，tag 形如 `A`/`B`/`P0`…）——真实独立子进程，每个都记录在 `evidence/run/<case>/summary.json` 的 `participants.<tag>.pid`。
2. 同一解释器起的**假 worker 命令进程**（`i04d_fake_worker.py`）——每次调用都往 `worker.jsonl` 写一行，含自己的 `pid` 与 `ppid`。
3. **调度器**进程（`i04d_schedule.py`，其输出目录见 §6 的 case 根）。

**kill 规则（硬性）：**

- **只允许 kill 记录在 `<A>\evidence\run\<case>\summary.json` 的 `participants.<tag>.pid` 里、且属于本 attempt 的 pid**（配合 `started_monotonic`/`finished_monotonic` 判断它是否仍在跑）。
- **绝不 kill 真实 worker**（company-wiki 的 worker / service 进程）。
- **绝不 kill 未知 pid**：拿不准就先只读采集（`Get-Process -Id <pid>`、`Get-CimInstance Win32_Process`），把现场写进 scratch，然后交 owner 判断。卡片的"失败停止条件"明确写了：需要 kill 未知 PID 即停止。
- 崩溃注入案例的退出码是**计划内**的（90/91/92/93），不是需要清理的异常；`ImportError`、`FileNotFoundError`、栅栏超时、未采集**都不算通过**，也都不构成"可以随便杀进程"的理由。
- 栅栏（gate）卡住时：先看 `hook-probe.log` 与 `gate.*.reached` 标记文件判断卡在哪个 gate，写清现场，再决定是否终止该案例的参与者；不要用 sleep 猜时序。

---

## 5. 绝对不要做的事

1. **不要碰生产仓**：`C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py`（本卡交付时仍为 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`）、company-wiki、revenue-forecast 的受版本控制源码。不要把任何命令路径指向生产 catalog：`C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3`（49,677,344,768 bytes、mtime `2026-09-19T06:31:35Z`、`-wal` 0 bytes——这个不变量必须保持）。
2. **不要删除真实所有权文件**：公司的 owner 标记 / pause refcount 属于生产状态。回滚代码不等于可以删生产所有权文件。
3. **不要主动 resume 真实 worker**：任何路径都不许对真实 worker 发 `worker-resume`。
4. **不要写 PLAN/reviews**：`<P>\reviews` 是只读的，其 mtime 必须保持 `before/03-reviews-mtime.txt` 记录的值。
5. **不要在仓里 `git add` / `commit` / `restore` / `stash`**：用户原有的 dirty tree（company-wiki 的 `M CLAUDE.md`、`M README.md` 等）不是本卡的改动，不许 reset/stash 掉。
6. **不要用全局 Miniconda 解释器**跑本卡的任何命令：只用 `<A>\iso\venv\Scripts\python.exe`（3.13.9 / pytest 9.1.1）。
7. **不要联网**，不要起真实 provider。
8. **不要把变异做在 `iso/` 主副本上**——只在 scratch 副本上做（见 §7）。
9. **不要重写 oracle.md 的冻结期望**去贴合实测；oracle 只能追加（追加区以 `# 追加` 开头）。
10. **不要在 `evidence/run/` 上原地重跑**，也不要在 `--basetemp` 里指向任何既有证据目录。

---

## 6. case 根的归属与清理

案例的 wiki/run 根不在 attempt 目录里，而在：

```
<P>\execution_runs\I-04-D\runs<pid>\
```

例如 `summary.json.dir` 记录的 `…\execution_runs\I-04-D\runs41272\I04D-CASE-F-L5`。
原因（FACTS §7）：ledger 的唯一临时名会追加到案例路径后，深根会撞上 Windows 经典路径长度限制——这是 harness 约束，不是协议约束。

- 这些根属于本 attempt，**不**属于 `a20260919-01` 目录本身。因此"changed_paths 全在 attempt 内"这句话对它们是例外，`handoff.json` 已显式登记。
- **当本 attempt 关闭（被接受或改判后归档）时，可以删除** `<P>\execution_runs\I-04-D\runs<pid>` 这些目录；删除前先确认对应案例的 `evidence/run/<case>/summary.json` 已在 attempt 内落盘（那才是交审证据）。
- **关闭之前不要删**：还需要用它复验 `report.*.json`、`worker.jsonl`、gate 标记与锁文件残留。若 reviewer 要求复验终态（例如 `F-LK-NEVER-UNLINK` 的 0 字节锁文件），必须从这些根直读，因为 `summary.json` 只是快照。
- 删除时**只删 `runs<pid>` 这一层**，不要用通配符去删 `execution_runs/I-04-D` 下的 `a20260919-01`。

---

## 7. scratch-only 变异配方（唯一安全的实验方式）

变异证明**本次没有跑**（`review.md` §6）。要做，只能在 scratch 副本上做，且必须留证：

1. 复制副本（不要动 `iso/`）：`robocopy <A>\iso\filing-fetch <A>\scratch\mutants\<Mn>\filing-fetch /E /XD __pycache__`
2. 在副本里做**单点回退**（M1–M11 各一条判据，见 `review.md` §6 的表），并记下副本 `scripts/fetch_filing.py` 的 sha256 作为该变异体身份。
3. 跑该变异点名的案例（argv 形状与 §3(b) 相同，只是把脚本路径换成副本、`--out` 指向 `<A>\scratch\mutants\<Mn>\run`）。
4. 记录 **raw rc** 与"是否按期望变红"的字段级证据，写进 `<A>\scratch\mutants\<Mn>\`。
5. 收尾证明主副本没被污染：

```
powershell -NoProfile -Command "(Get-FileHash -LiteralPath '<A>\iso\filing-fetch\scripts\fetch_filing.py' -Algorithm SHA256).Hash.ToLower()"
```

必须仍是 `a72546c50401a4b1876288bea6b6d7e4a72db9c39fd028c7bfb75a6f929ad198`。**不相等 = 变异污染了主副本**，立即停止并保留现场。
6. 前置缺口（不要跳过）：M9 引用的 N14（两进程同时持久化）案例目前**不存在**，需先补；M3/M4/M5/M7/M8/M10/M11 在 `oracle.md` §7 只给了期望，没有可运行 argv，需先补齐或记为 blocked。**不得**声称任何变异结果。

---

## 8. 一句话恢复顺序

回滚（§1 校验 hash `dc593a75…af1c`）→ patch（§2，hash 校验通过才跑）→ 复算 `a72546c5…a436` → 跑 §3(a) 与 §3(b) → 只在 `recovery/` 或下一 attempt 写新证据 → 全程不碰生产、不删生产所有权文件、不 resume 真实 worker、不写 PLAN/reviews。
