# INCIDENT — 编排层提交作业的 pre-commit 补丁未回放，导致生产工作树被重置到 HEAD

- 编号：`20260920-precommit-stash-production-rollback`
- 发现者：**两条独立来源**（互不知情）——`M25–M28` 实现者（04:35 收尾复核时发现 `model_registry.py` 非锚定态）、`I-08-B` 第三方复核（发现 5 个生产文件"变干净"）。父 agent 随后确认根因。
- 时间窗：**2026-09-20 04:35:31 – 04:5x（本地）**（回滚发生于 04:35:31–32，恢复完成为父 agent 本轮）。
- 影响对象：`revenue-forecast` **工作树**中既有的未提交改动（不是任何 attempt 的产物、不是任何冻结件）。
- 定性：**编排层（父 agent）自身造成的生产树状态破坏**，非任何卡实现者所为；已完全恢复并校验。

## 1. 根因（确凿）

父 agent 上一轮的 `git add / commit / push` 作业触发仓库自带的 **pre-commit + pre-push 门**。该门的既有实现是：

1. 把**未暂存改动**导出为补丁：`C:\Users\郑曾波\.cache\pre-commit\patch1789875331-33652`（**557,924 B**，时间 04:35:31）；
2. 执行 `git checkout -- .` 以移除未暂存改动、便于在干净树上跑 hook；
3. 跑完 hook 后再 `git apply` 回放该补丁。

本次第 2 步**失败**：

```
CalledProcessError: command: ('git.EXE','-c','submodule.recurse=0','checkout','--','.') return code: 255
stderr:
  error: unable to unlink old '.planning/.../I-04-D/.../scratch/diagU/I04D-CASE-F-L5/stderr.A.txt': Invalid argument
  error: unable to unlink old '.planning/.../I-04-D/.../scratch/diagV/I04D-CASE-F-L5/stderr.A.txt': Invalid argument
  error: unable to unlink old '.planning/.../I-04-D/.../scratch/diagW/I04D-CASE-F-L5/stderr.A.txt': Invalid argument
[WARNING] Stashed changes conflicted with hook auto-fixes... Rolling back fixes...
```

即：3 个被并发写入的 scratch 文件让 `git checkout -- .` 返回 255，hook 抛出异常退出，**第 3 步的回放从未执行**。结果是 `checkout` 已经把（部分）未暂存改动重置为 HEAD，而补丁留在缓存目录里没人回放 ⇒ 生产工作树"变干净"。

**并发诱因（同一根因的另一面）**：`.planning` 树下存在 **3 个内嵌 `.git` 目录**（attempt 内为 `git apply` 验证而 `git init` 的 scratch 仓库）：
`I-06-A/.../iso/ff/.git`、`I-14-C/.../r5/diff-apply-check/tree/.git`、`I-14-C/.../r5/diff-repo/.git`。
父仓库把它们当作 submodule/gitlink 处理，`git status` 与 hook 的 stash/checkout 因此报 `fatal: bad object HEAD` / `fatal: 'git status --porcelain=2' failed in submodule …`，进一步放大了失败面。

## 2. 观测到的后果（`git status` 对生产路径为空 = "工作树 == HEAD"）

| 文件 | 回滚后（错误态） | 恢复后（正确态，实测） |
|---|---|---|
| `scripts/model_registry.py` | `1f2639e1…`（19703 B，**247 行**；无 `build_extension_specs` 挂载、无 `driver_bounds`、**本批四模型缺失**） | **`9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`（26446 B，354 行）** |
| `scripts/model_extensions.py` | `9939480b…`（未受影响，但仍为 untracked） | `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`（未变） |
| `scripts/revenue_core.py` | `7d4c2487…`（HEAD 版） | `1821fd2a8a4efa2b…`（14136 B） |
| `scripts/contracts/constants.py` | `46983370…` | `278e3e02df15e556…`（5063 B） |
| `scripts/revenue_report.py` | `c7e23770…` | `a85fb48482216dca…`（69765 B） |
| `tests/test_backtest.py` | `d3fcd802…` | `d0972e238066f40e…`（17665 B） |
| `SKILL.md` | `44e91406…` | **`45e4e343eba4f6e7…`（26378 B）—— 与 I‑00‑A 冻结基线登记值一致** |
| `CHANGELOG.md` | （HEAD 版） | `bcba3dd50278b677…`（19601 B） |
| `assurance/runs/{daily_alert.jsonl,weekly_alert.jsonl,weekly_manifest.json}`、`e2e/expected/expected-0e1cc8d4c73d.json`、`references/backtesting.md` | （HEAD 版） | 已回放（见 §3 的同一补丁） |

**行为级后果（M21–M24 实现者实测）**：回滚窗口内 `calculate_registered_model("delivery_pipeline", timing_factor=[1,1.5], 2 年)` 正常返回 `[122.0, 0.0]`，而非冻结预期的 `ModelRegistryError: … must be between 0.0 and 1.0: FY2028`；`hasattr(ModelSpec,"driver_bounds") == False`、`model_registry.driver_value_bounds` 抛 `AttributeError`。即**该窗口内 M21/M22/M23 的判定性值域负例在生产代码上不成立**（attempt 内的 `iso/checkout_scripts` 快照不受影响，仍为锚定值）。

## 3. 恢复处置（父 agent 执行，选项 ①：恢复锚定态）

```powershell
$patch = "$env:USERPROFILE\.cache\pre-commit\patch1789875331-33652"
git apply --check --whitespace=nowarn --exclude=.planning/* $patch   # exit 0
git apply       --whitespace=nowarn --exclude=.planning/* $patch     # exit 0
```

- 排除 `.planning/**` 的原因：该子树在 04:35 之后已被多个 session 重写，补丁对其中若干文件已不可应用（`patch does not apply`）；这与生产路径无关。**未使用** `--reject`、**未**生成任何 `.rej`、**未**丢弃补丁中任何非 `.planning` 路径（`--check` 已证明其全部可应用）。
- 恢复后逐文件 hash 见 §2 第三列，`scripts/model_registry.py` 已回到锚定值 `9ec65295…`。
- 去风险：把 3 个内嵌 scratch 仓库写入 `execution_runs/.gitignore`（`*/a*/r5/diff-apply-check/`、`*/a*/r5/diff-repo/`；`I-06-A/.../iso/ff/` 已被既有 `*/a*/iso/` 覆盖），使父仓库不再递归进入内嵌 `.git`。**未删除任何文件**。校验：`git status` 不再 `fatal`；生产非 `.planning` porcelain 恢复为 51 条（= 事件前 45 条 + 本次回放的 7 条生产路径，符合预期）。

## 4. 对计划资格的影响（父 agent 裁定）

1. **无需改判**：M21–M24、M25–M28 的 `accepted_scoped` 依据的是各 attempt 内 `iso/checkout_scripts` 的**逐字节快照**（`9ec65295…/9939480b…`）；该快照在事件期间**从未改变**，且生产侧现已恢复与之逐字节一致 ⇒ 其失效条件解除，round-3 终裁继续有效。
2. **窗口内告警是正确的**：`2026-09-20 04:35:31–04:5x` 内任何 `production_hashes_unchanged=false` / `anchored_hashes_match=false` **都是正确告警**，不得据此改动任何期望值、冻结件或 oracle。相关卡须**保留**漂移记录（`recovery/production_drift.json` 等）并**追加**恢复记录，时点限定写清。
3. **凡以"生产文件 hash"为验收依据的卡**都必须把它视为**可被外部 git 操作改变的量**；发现不一致时先记录漂移与时点并上报编排层裁定，**永不靠改期望/改冻结件去适配**（M21–M24 与 M25–M28 实现者本次的处理即为范本）。
4. **编排层纪律（新增，必须遵守）**：
   - 在**有 attempt 正在写 scratch 文件时**不执行 `git add/commit/push`（hook 的 stash/checkout 会与被并发占用的文件冲突）；
   - 提交前先确认 `.planning` 下**无内嵌 `.git`**（已有 ignore 兜底，但仍应检查）；
   - 每次 commit/push 后**必须核对 hook 是否打印 `[INFO] Restored changes from <patch>`**；若只看到 stash 而无 restore、或出现 `Rolling back fixes` / `CalledProcessError`，视为**生产树可能已被重置**的红色告警，须立即：`Get-FileHash` 抽查生产锚点 → 用该次 `patch*` 的 `--exclude=.planning/*` 子集回放（`--check` 通过才 apply）→ 复算锚点 → 记录时点。
   - 上游材料：本次补丁 `patch1789875331-33652`（557,924 B）与父 agent 的恢复命令已在本文件留档，可在需要时重放。

## 5. 仍存的不确定性（如实登记，未当已证）

1. `git checkout -- .` 在返回 255 前**究竟重置了哪些路径**未逐条取证（它的 stdout 为空）；本文列的路径来自"补丁内容 + 恢复后实测 + 两份独立复核"，属**重建**而非当时抓拍。
2. 回滚窗口内是否存在**未被补丁覆盖**的第三方并发改动被一并重置，无法判定（这些改动已不可得）。
3. 谁在何时创建了 3 个内嵌 scratch 仓库已可归属（attempt 的 diff-apply 验证），但其 `.git` 内部状态（`bad object HEAD` 的具体成因）未进一步解剖。
4. 该 pre-commit hook 的失败模式是否还会在别的 Windows 并发场景复现，未做穷举测试；本次只做了"忽略内嵌仓库 + 提交后核对 restore 行"两项缓解。

---

## 第二次同类事件（2026-09-21 21:40，无损失）

**现象**：pre-commit hook 的 stash/checkout/replay 周期再次失败：
```
[WARNING] Stashed changes conflicted with hook auto-fixes... Rolling back fixes...
CalledProcessError: git -c submodule.recurse=0 checkout -- .
return code: 255
stderr: error: unable to unlink old
  '.planning/.../execution_runs/I-14-E/a20260919-01/after/campaign-band.log': Invalid argument
```

**根因**：与 2026-09-20 事件**同一**——并发 subagent（I-14-E）正在写入该文件，git checkout -- . 无法 unlink 被占用的文件而返回 255。

**本次与上次的关键差异（为什么没造成损失）**：
1. **生产树锚点全部完好**（复算：model_registry.py 9ec65295…、model_extensions.py 9939480b…、SKILL.md 45e4e343…、evenue_core.py 1821fd2a…）——上次是 model_registry.py 被重置到 HEAD。
2. **暂存区完好**（1219 文件仍在 index 中）。
3. 失败补丁 patch1790023228-48668（6549 B）**只含并发新增的未跟踪文件**（B1 的 suite_fixed.stdout.txt、I-14-E 的 campaign-band.log）+ 我重建的 plan_inputs.json，**不含任何已提交内容的回退**。

**新纪律（第二条时间限定规则）**：
> **不得在并发 subagent 正在写入时提交。** 提交前先确认目标 attempt 目录**静默**（例如最近 60 s 无 mtime 变化）；若某卡正在跑测量/生成，**等它落盘后再提交**，或只提交与它无关的路径。
> 理由：hook 的 git checkout -- . 对**被占用**文件必然失败；失败时补丁**不一定**被回放（上次就没回放）。这是**结构性**风险，不是偶发。

**已验证的缓解**：本 session 每次提交后核对 hook 的 `[INFO] Restored changes from <patch>` 行 + post-push 锚点复算——该纪律在本次事件中使我**能立即判定"无损失"**而不是猜测。
