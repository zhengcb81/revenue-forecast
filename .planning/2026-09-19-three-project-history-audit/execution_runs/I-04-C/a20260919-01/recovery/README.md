# I-04-C 恢复边界与回退配方

本卡是**设计卡**：没有改任何产品代码，所以"回退"只涉及本次尝试目录内的产物。

## 0. 恢复边界（卡片原文 + 本卡实际做法）

- **不迁移生产 lease 文件**：`.source_catalog/filing_fetch_pause.*` 一个字节都没动；
  本卡从未读写 `C:/Users/郑曾波/Projects/{filing-fetch,company-wiki,revenue-forecast}` 下的任何运行期状态。
- **决策不成立则保留旧问题未关闭**：若独立 reviewer 判 `changes_required` 或 `blocked`，
  本卡不产生任何"已修"结论；问题回到 I-04 原义务，由 owner 决定是否进 I-04-D。
- 生产核查：`evidence/hashes.txt` 里 `PRODUCTION_UNCHANGED=true`，
  `filing-fetch` 工作树在本卡期间只有既有的未跟踪文件 `git_filing-fetch.txt`（非本卡产生）。

## 1. 复现本次全部证据（从零）

```powershell
$A = "C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-04-C\a20260919-01"
$PY = "$A\iso\venv\Scripts\python.exe"

# 1) 编译检查
& $PY -B -m py_compile "$A\sim\kernel.py" "$A\sim\participant.py" "$A\sim\stub_worker.py" `
    "$A\sim\harness.py" "$A\sim\cases_core.py" "$A\sim\cases_ownership.py" `
    "$A\sim\cases_legacy.py" "$A\sim\stress.py" "$A\sim\scheduler.py"

# 2) 协议套件（每 case 前会自动清空自己的目录）
& $PY -B "$A\sim\scheduler.py" run F-L1 F-L2a F-L2b F-L2c F-L2d F-L3 F-L4a F-L4b F-L4c F-L4d F-L4e `
    F-W1 F-W2 F-W4 F-W4b F-W5 > "$A\evidence\run-all.txt" 2>&1
& $PY -B "$A\sim\parse_run.py" "$A\evidence\run-all.txt" "$A\evidence\failures.txt"

# 3) 锁原子性 + RED 反例
& $PY -B "$A\sim\scheduler.py" run F-LK1 F-LK2 F-LK3 F-L1-nolock-guard F-L1-nolock F-L2a-legacy F-Lgw1 `
    > "$A\evidence\lock-and-legacy.txt" 2>&1
& $PY -B "$A\sim\parse_run.py" "$A\evidence\lock-and-legacy.txt" "$A\evidence\lock-and-legacy-failures.txt"

# 4) 冻结哈希（并复核生产 hash）
& $PY -B "$A\sim\freeze_evidence.py"
```

预期（与 `evidence/` 的现状一致）：步骤 2 退出码 1（有 6 个 case 带失败检查），
步骤 3 退出码 1（两个 legacy 反例停在它自己的运行期守卫上），步骤 1/4 退出码 0。

## 2. 回退本次尝试

本卡的**唯一**写入范围是 `execution_runs/I-04-C/a20260919-01/**`。整体回退：

```powershell
Remove-Item -Recurse -Force "…\execution_runs\I-04-C\a20260919-01"
```

回退后需要检查的外部事实（应全部保持原样）：

```powershell
(Get-FileHash 'C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py' -Algorithm SHA256).Hash
# 期望：046CC7DC4E3FF2F4F59BE05DEF8961A85A12E6290ADEF43A3C53103C63B9D088
git -C 'C:\Users\郑曾波\Projects\filing-fetch' status --porcelain
# 期望：只有既有的未跟踪文件（本卡不产生任何条目）
```

## 3. 部分回退

- **只回退模拟内核的某条规则**：`sim/kernel.py` 是唯一实现点；`decision.md` 的 ADR 编号与
  `sim/kernel.py` 的注释一一对应（ADR-9/9b/9c/10/11、`lock_budget_for`）。改动后必须整跑步骤 2，
  不允许只跑单个 case 就宣布通过（隔离与一致性由调度器保证）。
- **只重跑单个 case**：`& $PY -B "$A\sim\scheduler.py" run <case>`；它会先删除
  `evidence/run/<case>`，所以单跑**不会**污染其它 case 的原始证据。
- **不确定的现场**：不要删 `evidence/run/<case>/`；里面有 journal、refcount/owner 快照与
  参与者的原始 stdout/stderr，是判定"规则缺口 vs 调度缺口"的唯一依据。

## 4. 已知的失败重跑风险

- F-L2d 的并发计数依赖机器负载（临界区里有一次 `worker-status` 子进程）。若重跑时
  `pause_calls` 数量变化，先看 `evidence/run/F-L2d/journal.jsonl` 的 `lock_acq.waited`，
  再判断是调度问题还是规则问题 —— **不要**通过调大 `request_budget` 或放宽断言来"修"它。
- `evidence/run/**` 里的 `alive.<pid>.<holder>.<tag>.json` 是**判活申报**文件：
  有残留说明该参与者是被 crash 注入杀死的（或重跑前未清目录）。调度器每次都会清目录，
  手工调试时才会看到残留。
