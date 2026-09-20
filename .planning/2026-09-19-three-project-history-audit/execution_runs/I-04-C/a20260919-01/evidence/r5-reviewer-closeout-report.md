# 收尾复核报告（独立 reviewer session）

- 输出目录：`%TEMP%\closeout-review-20260920-035508`（本报告为唯一交付物；生产仓库全程只读，未写入任何生产路径）
- 复核时间：2026-09-20（本地）
- 环境：Windows / PowerShell 5.1.26100.9444；隔离解释器一律使用各 attempt 的 `iso\venv\Scripts\python.exe`（未使用全局 Miniconda python）
- 被复核 attempt：
  - I-00-A `…\execution_runs\I-00-A\a20260919-01\`
  - I-15-A `…\execution_runs\I-15-A\a20260919-01\`
  - I-04-C `…\execution_runs\I-04-C\a20260919-01\`
- 独立性声明：本报告全部结论来自**我亲自执行的命令的原始输出**或我亲自重算的哈希/算术；实现者的自述、`handoff.json`/`review.md` 的结论栏一律只作为**被审数据**，不作为证据。凡我未复现的事实，均在每节末"未验证项"中列出。

统一口径：本复核只在 `%TEMP%` 下写文件；对生产仓只执行 `git rev-parse/log/status/ls-files`、`Get-FileHash`、`Get-Item` 与只读 SQLite 查询；两个 I-15-A / I-04-C 的耗时复现均在 `%TEMP%` 的**副本**中运行（I-15-A 副本放在 `…\iso-run\execution_runs\…` 以满足其自身的 `guard_scratch` 路径门）。运行后已核对：两个 attempt 目录内（含 `iso\venv`）**没有**任何一个文件的 mtime 晚于 `2026-09-20 03:55`，即我的复现未向生产仓写入任何字节。

```
=== files modified inside the two attempt dirs since 2026-09-20 03:55 (my session) ===
--- I-15-A: 0 files newer than 2026/9/20 3:55:00 (excl iso/venv) ---
    (iso/venv files newer: 0)
--- I-04-C: 0 files newer than 2026/9/20 3:55:00 (excl iso/venv) ---
    (iso/venv files newer: 0)
```

---

# 卡一 I-00-A（errata 确认）

## 裁决：**可以 closed**（限 review.md:5 的只读基线清点资格）

### 1. 盘上确实没有 reviewer 的确认文字（先证"缺"）

命令：

```powershell
Select-String -Path "<attempt>\review.md" -Pattern "errata|wrong-capture|重采|替换"
Get-ChildItem <attempt> -File | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower() + "  " + $_.Length + "  " + $_.Name }
```

原始输出摘录：

```
review.md:  1397dc47c526224d4b70e7bc521cd6ec4937a5f0e89c418e6ef9a8c7cb4b45e5  4356  review.md
errata_fix_note.md: 6db8f90dcadad7a6acf8b7254917500182c80836e6f2f9906d83b36a2e81f476  329
handoff.json: ec54ae42f95a9c15606221ae3ec65d8b4738904db1cf3025a1f5ff52e275a28d  1888
（Select-String 仅命中 review.md 第 22 行——即原始【阻断项】本身）
```

文件 mtime 顺序也自证：`review.md` 11:02:22 → errata 产物 `git_*` 11:05:23/11:05:32、`errata_fix_note.md`/`handoff.json` 11:05:39。**reviewer 的 review.md 在 errata 之前就已封笔，其后没有被追加任何确认段落**。任务描述"盘上检索不到任何 reviewer 的确认文字"成立。

### 2. 两份证据是否**真的按仓重采**——成立（三重独立证据）

（a）HEAD/提交时间与各仓现网逐字一致：

```powershell
foreach($r in @("company-wiki","filing-fetch","revenue-forecast")){ git -C "C:\Users\郑曾波\Projects\$r" rev-parse HEAD; git -C "C:\Users\郑曾波\Projects\$r" log -1 --format="%H%n%cI" }
```

```
company-wiki   : f39bd5a64224cd0c7aa098f23f64bf3811fa8939 / 2026-09-19T08:42:58+01:00   （= git_company-wiki.txt 第1行）
filing-fetch   : d35b6f5b09f1a7dad37d226504bf998802a852d7 / 2026-09-15T22:12:54+01:00   （= git_filing-fetch.txt 第1行）
revenue-forecast: e9544495…（现 HEAD，已前进）/ 2026-09-20T03:54:00+01:00
```

`git_company-wiki.txt`（135 B，sha256 `3112cd3e4c5aea00beffcc0d59c1bab7d87ef2dac441ab3ac96a0a6fd98d9dce`）内容：HEAD 行 + `## fcap` + ` M .coverage` / ` M coverage.json`（各出现两次）；`git_filing-fetch.txt`（123 B，sha256 `43b964e376e77e30f4531bab71fcd7d6afa84496fe506328e675812eec6c160c`）内容：HEAD 行 + `## fcap` + `?? git_filing-fetch.txt`（两次）。

（b）company-wiki 的 dirty 集与 baseline.json 一致，且两文件在该仓确为 tracked：

```powershell
git -C C:\Users\郑曾波\Projects\company-wiki ls-files --error-unmatch .coverage coverage.json
→ .coverage
  coverage.json
```

（c）采集形态可复现（证明重复条目是工具产物而非"又抄错了"）。我在 `%TEMP%` 新建仓、`git init -b fcap`、提交后改动 `.coverage`/`coverage.json`，再拼接 `git log -1 --format="%H %cI"` + `git status -sb` + `git status --porcelain`：

```
8b580a09… 2026-09-20T04:00:10+01:00
## fcap
 M .coverage
 M coverage.json
 M .coverage
 M coverage.json
```
算术校核：`67(HEAD行) + 8(## fcap) + 30 + 30 = 135` = 盘上 `git_company-wiki.txt` 的字节数；filing-fetch 侧 `67 + 8 + 24 + 24 = 123` = 盘上字节数。**两份新文件的字节结构被逐字解释。**

### 3. `*.wrong-capture.txt` 确为"错捕"——成立；但盘上只有**两份**，不是三份

```powershell
Get-ChildItem <attempt> -Recurse -Force -Filter "git_*" | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()+"  "+$_.Length+"  "+$_.Name }
```

```
032316914e5245af1b8f580fe6766c67bd11df024429b5c61e47a118ab388d5f  3002  git_revenue-forecast.txt
032316914e5245af1b8f580fe6766c67bd11df024429b5c61e47a118ab388d5f  3002  git_company-wiki.wrong-capture.txt
032316914e5245af1b8f580fe6766c67bd11df024429b5c61e47a118ab388d5f  3002  git_filing-fetch.wrong-capture.txt
```

三份**逐字节相同**（3002 B）。即：被更名保存的两份 wrong-capture 就是 revenue-forecast 的捕获内容，而 `git_revenue-forecast.txt` 本身正确、无需更名——所以"三个 `*.wrong-capture.txt`"这一前提与盘上不符，实际是**两个**。

"时间是当时"的证明（不能用今天的 porcelain 判旧文件错，只能判当时是否捕对）：

```powershell
git -C C:\Users\郑曾波\Projects\revenue-forecast reflog --date=iso -n 15
→ 2c5384b HEAD@{2026-09-19 08:45:31 +0100}: commit: R4/BAR 记录：第二处 fetchall + 记录事务守卫（被驱动）；登记 F-COV-01 / F-ZR409-01
→ 3a674f6 HEAD@{2026-09-19 22:48:26 +0100}: commit: 审计计划+实施段：…（HEAD 于 22:48 才前进）
```

即捕获时刻（10:55）revenue-forecast 的 HEAD 确为 `2c5384bb`，与错捕文件第 1 行一致。另有两处**只有 revenue-forecast 才有**的指纹：

```
错捕内容含 "?? .planning/"（本计划根即在 revenue-forecast）
错捕内容含 warning: could not open directory '.tmp-zr408-unit/': Permission denied
Test-Path 实测：revenue-forecast\.tmp-zr408-unit = True ; company-wiki = False ; filing-fetch = False
```

（`git_company-wiki.wrong-capture.txt` 与 `git_filing-fetch.wrong-capture.txt` 的 mtime 均为 `2026-09-19 10:55:37`，与更名保留一致。）

### 4. 残留观察（不阻断 closed）

- **条目重复**：两份新文件都把 `git status -sb` 与 `git status --porcelain` 串在一起输出（见 §2c 复现）。
- **`?? git_filing-fetch.txt` 自指行**：该行只能来自"输出重定向落在 filing-fetch 工作树内"。`findings.md:57` 独立记录了同一事件（"越界写 2"），给出的 sha256 `43b964e376e7…c160c` 与我算出的 attempt 内副本哈希**完全相同**、mtime `2026-09-19 11:05:23` 也相同，并记录该文件已从生产树删除。我实测复核了"已复原"：

```powershell
git -C C:\Users\郑曾波\Projects\filing-fetch status --porcelain     → （空）
Get-ChildItem C:\Users\郑曾波\Projects\filing-fetch -Recurse -Force -Filter "git_filing*"  → （无）
git -C C:\Users\郑曾波\Projects\filing-fetch ls-files "*git_*"      → （无）
```

  结论：生产树无残留；attempt 内那份就是当时被写入生产树文件的逐字节副本。它使该证据"字面上不再显示 clean"，但**不影响仓库归属**（HEAD/时间/分支三字段均为 filing-fetch 自身）。
- 记账瑕疵：reviewer 的修复约束是"不动其它任何交付物"，而 `handoff.json` 在 11:05:39 被改动，且写入 `reviewer_status: "accepted_scoped_pending_errata_confirm"` —— 这是 reviewer 从未在盘上出具的结论（`review.md:3` 是 `changes_required`）。属记账口径问题，不构成对 errata 本身的否定；现应据本确认段落更新。

### ▶ 可原样粘贴进 `review.md` 的确认文字（独立 reviewer session，errata 确认）

```
## errata 确认（独立 reviewer session，2026-09-20；本段由 reviewer 出具，实现者转录不得改动）

结论：**本卡可以 closed**。review.md:22 的【阻断项】已按其限定的修复动作完成，并经本次独立复核逐项核实：

1. 两份证据已按仓重采，且**归属正确**：`git_company-wiki.txt` 的 HEAD `f39bd5a6…` 与提交时间
   `2026-09-19T08:42:58+01:00` 与 company-wiki 现网 `git rev-parse HEAD` + `git log -1 --format=%cI`
   逐字相同；`git_filing-fetch.txt` 的 `d35b6f5b…` / `2026-09-15T22:12:54+01:00` 与 filing-fetch 现网
   逐字相同；两者互不相同。company-wiki 的 dirty 集 `{.coverage, coverage.json}` 与 baseline.json 记录
   一致，且这两个文件在 company-wiki 均为 tracked。
2. `*.wrong-capture.txt` **确为错捕**并只读保留：`git_company-wiki.wrong-capture.txt`、
   `git_filing-fetch.wrong-capture.txt` 与未更名的 `git_revenue-forecast.txt` **逐字节相同**
   （sha256 `03231691…`，3002 B）；其内容为 revenue-forecast 的 HEAD `2c5384bb`（reflog 显示该 commit
   时间 `2026-09-19 08:45:31 +0100`，直到 `22:48:26` HEAD 才前进）、含 `?? .planning/`，并带只有
   revenue-forecast 才存在的 `.tmp-zr408-unit*` 权限告警（实测该目录在 revenue-forecast 存在、在另两仓
   不存在）。原判"两份文件是 revenue-forecast 复制件"成立，现已被替换。注：盘上只有**两份**
   wrong-capture 文件（`git_revenue-forecast.txt` 本身正确，无需更名）。
3. 残留观察（**不阻断 closed**，已登记）：两份新捕获的条目重复来自把 `git status -sb` 与
   `git status --porcelain` 串联输出——本次用独立 git 仓复现，产物结构逐字段一致且恰好 135 B
   （67+8+30+30）。`git_filing-fetch.txt` 另含 `?? git_filing-fetch.txt`：该行只能来自一次**越界输出
   重定向**（findings.md:57 已记录同一 sha256 `43b964e3…c160c` 与 mtime `11:05:23`，该文件已从生产树
   删除）。实测复核：filing-fetch `git status --porcelain` 为空、全树无 `git_*` 残留、`ls-files` 无匹配
   ⇒ 生产树已复原，attempt 内副本即当时被写入文件的逐字节副本。故"内容与 baseline 的 clean 声明字面
   不符"是自指产物，不影响仓库归属判定。
4. 授权范围不变：本确认**仅针对只读基线清点资格**（沿用 review.md:5 的范围限定），**不授予**任何产品
   修复、代码/配置修改、scan/fetch/worker 执行、生产 DB 或写目录变更、公式/预测准确性或旧 PASS 继承
   资格。
5. 记账：`handoff.json` 的 `reviewer_status` 应据本段改为"errata 已由独立 reviewer 确认，本卡在
   review.md:5 范围内 closed"；原值 `accepted_scoped_pending_errata_confirm` 是 reviewer 未出具过的
   状态，不得据此扩张资格。
```

### 本节未验证项

1. **无法回放 company-wiki 在 11:05 时刻的 porcelain**：该仓 HEAD 未动，但 `.coverage`/`coverage.json` 现 mtime 为 `2026-09-19 23:04:28`、已不再显示为 modified，`CLAUDE.md`/`README.md` 另被 I-00-D 修改。我只能证明"新捕获的 HEAD/时间/dirty 集与 baseline 及各仓身份字段一致"，不能证明当时 porcelain 的逐行原貌。
2. **无法证明 company-wiki 的采集动作本身是纯只读**：filing-fetch 一侧有 `??` 自指行作为越界写实证，company-wiki 一侧无自指行，故"未在其工作树内落文件"只是**推断**（无正面证据，也无反面证据）。
3. **无法确定执行重采的确切命令与会话**（无 session log；构造是行为等价复现，不是原命令回放）。
4. 未复核 `capability_probe_small.sqlite3` 与 47G 生产 DB 的其余基线事实（本轮范围只是 errata；review.md:9/17 的 8 个 config hash 也未由我重算）。

---

# 卡二 I-15-A（证据/诊断资格）

## 裁决：**`accepted_scoped`——仅证据/诊断；产品实施仍 blocked，不授予产品实施资格**

### 1. 冻结先于运行（可否证的时序证据）

```
oracle.md     mtime 2026-09-20 01:28:15
binding.json  mtime 2026-09-20 01:28:04
before_pass/cmd-C1 mtime 2026-09-20 01:28:58   ← 首次运行
harness/archive_verifier.py  mtime 01:30:18
harness/tests/test_i15a_prune_verified_set.py mtime 01:30:42
after_pass/cmd-C7 mtime 01:30:47               ← 交付的那一次运行
```

`oracle.md` 的 W15-R1..R8 与固定样本（5 span；期望 delete `{a1,a2}` / retain `{a3,b1,c1}`）在任何运行之前写定；期望常量在 `harness/archive_verifier.py` 中为预列常量，非由产物推导。**注**：`archive_verifier.py` 在 `before_pass` C1..C5（01:28:58–01:30:09）之后还被改过一次；交付证据取的是 C7（01:30:47，晚于 verifier/test 的最后写入），故交付运行自洽；但 C6 与 C7 的用例数不同（见 §2），说明早期迭代用的是较早修订——不是期望值事后拟合（oracle 更早），但要如实记录。

### 2. 五类反例：机制在产品源码中可核，结果在隔离副本中被我复现

（a）产品源码逐行核对（只读）：

```
prune_retired_evidence.py:27-30  _DELETE_BATCH = DELETE … WHERE document_id IN (SELECT … source_status='retired')   ← 删所有 retired 的 span，从不查归档
prune_retired_evidence.py:66-76  oldest = 目录名排序取第一个；due = (today - date.fromisoformat(oldest)).days >= retention_days；today = datetime.now(...)
prune_retired_evidence.py:114-123 直接进入锁+批删循环（无 plan hash、无按行 digest、无 TOCTOU 复检）
prune_retired_evidence.py:125-142 收据在**整个循环结束之后**才写
archive_retired_evidence.py:48-51 目录按当日 yyyy-mm-dd；:65 gzip.open(out_path, "wt") 截断写；:87-92 只对账 rows_written == total
```

即"空目录也删 / 同日覆写 / 时钟取目录名 / TOCTOU / 崩溃后不可恢复"五类反例的机制**真实存在**，不是叙述产物。

（b）记录在案的那次运行，其原始输出我直接读过：

```
after_pass\cmd-C7\stdout.txt  末尾：  6 failed, 5 passed in 1.82s
before_pass\cmd-C6\stdout.txt 末尾：  6 failed, 4 passed in 1.93s
```

C7 的 6 个 FAILED 恰为：`test_w15_p1_prune_deletes_only_the_verified_set`、`test_w15_p2_second_apply_is_idempotent_for_the_authorised_set`、`test_w15_n1_empty_old_directory_is_not_authorisation`、`test_w15_n2_directory_name_is_not_the_retention_clock`、`test_w15_n3_mutation_after_plan_must_abort_not_silently_shrink`、`test_w15_n4_interrupted_batch_leaves_a_receipt_of_what_was_deleted`。

（c）**我的独立复现**（副本置于 `%TEMP%\…\iso-run\execution_runs\I-15-A\a20260919-01\`，用该 attempt 的 iso venv python `-B`）：

```
=== RUN pytest (isolated copy under an execution_runs path, -B) ===
6 failed, 5 passed in 6.73s
=== pytest exit code: 1 ===
（6 个失败名与 C7 完全一致；5 个通过 = 真实归档验证、损坏归档拒绝、manifest 冲突检测、restore 证明、同日覆写检测）
```

顺带得到一个正面结论：**该 harness 的隔离门是硬门**——我第一次把副本放在不含 `execution_runs` 的普通 TEMP 路径时，11/11 全部以 `SystemExit: BINDING-REFUSED (not under execution_runs)` 失败；换到含 `execution_runs` 的路径才复现 6/5。

（d）攻击项 3（"WAL 里也许还有被删的行"）我做了实测：在我重跑副本的 `n4-crash` 现场，

```
evidence_spans: ['c1']
documents: [('doc-A','retired'),('doc-B','retired'),('doc-C','active')]
freelist_count: 0 ; journal_mode: wal ；该目录下无 catalog.sqlite3-wal
receipt files: （无任何 prune-retired*）
```

⇒ 崩溃后 4 行（a1,a2,a3,b1）**确实不能从任何持久工件恢复**；收据缺失这一条反例成立。（更深层的页级取证不在本卡声明范围。）

### 3. 我独立复算的 oracle 值

```powershell
& <iso-python> -B -c "…open(gzip).read() → sha256；gzip.decompress → json rows；canonical json digest…"
```

```
gzip_sha256 4798b9719528223b8614d2ff6e22939cd60bd1427ce9c22da5d576317e1b9556
rows 3
span_ids ['a1', 'a2', 'c1']
digests {'a1': '615eed4ade8db004', 'a2': '64e883ee393cadf7', 'c1': 'e46e0b5ba5118e55'}
```

与 `after_pass/evidence/restore-proof.json` 的 `pre_delete_digests`（a1 `615eed4ade8db004b6b57faa7162924482f3cbdfa9818033bf994687a6c8dd61`、a2 `64e883ee393cadf75f511d7e95678ced71eb7530e97ae81d96f54843d2cc0e7a`）逐字相符；与 `archive-verified-manifest.json` 的 archive_sha256 相符。**F-I15A-01 的更正成立**：扫描 attempt 内 117 个文件，无一命中 `85d2f08e…`（含前缀扫描），而 `4798b971…` 出现在交付 gzip 与两处 scratch 源文件。

### 4. 记录一致性：`changes.diff` 与产品哈希台账

- `changes.diff`（sha256 `dbb44c12ea81805df70f83e66b787c58b5ccc50c7053d95c7f33b62f7bddeda7`，1980 B）自述"**Empty by design**"，并列出 7 个产品文件的哈希。
- **本卡 `iso/` 内没有任何实现补丁**：`Get-ChildItem <attempt>\iso -Force` 顶层只有 `venv`（即"iso 内补丁哈希"在 I-15-A 上**无对象可核**；任务书中"iso/ 内实现补丁 + changes.diff 哈希"这一项不适用于本卡，可能与他卡（I-14-A/I-14-C）混淆）。
- 与之等价的台账我全部实测，**9/9 命中现网**：

```
MATCH  len=4658  2358c73b…  src\company_wiki\source_catalog\prune_retired_evidence.py
MATCH  len=3291  143fef01…  src\company_wiki\source_catalog\archive_retired_evidence.py
MATCH  len=63563 1a783240…  src\company_wiki\source_catalog\store.py
MATCH  len=15807 2303d3e5…  src\company_wiki\source_catalog\lock.py
MATCH  len=10798 65230572…  src\company_wiki\source_catalog\models.py
MATCH  len=4529  a40d54a3…  src\company_wiki\source_catalog\section_query.py
MATCH  len=7786  b4db781a…  src\company_wiki\source_catalog\reconcile_retire_state.py
MATCH  len=3211  e0727c70…  tests\contract\test_source_catalog_prune_retired.py
MATCH  len=3500  0a4195b1…  tests\contract\test_source_catalog_archive_retired.py
```

- 副作用面：`worker_control.json` 实测 sha256 `9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd`（与冻结值相同）；生产 catalog 实测 `size=49677344768  mtime=2026-09-19 07:31:35 (+08) / 06:31:35Z`（**只用 Get-Item，未打开**）；`company-wiki` porcelain 仅 ` M CLAUDE.md`、` M README.md`（既有用户/I-00-D 改动），`filing-fetch` porcelain 为空。

### 5. D-W15 五项未签 ⇒ 产品实施仍 blocked

```
decision.md 抬头： "This is a proposed decision, submitted for signature by the storage-maintenance owner and the independent data-recovery reviewer."
D-W15-1 标题： "(proposal, needs signature)" ；D-W15-4 同；D-W15-2/3/5 为 proposal
handoff.json.blocked_by: ["D-W15 specialist decision (schema/transaction/recovery) is unsigned; implementation must not start before it …"]
PLAN 内检索：task_plan.md/progress.md 均把 D-W15 列为未签 owner 门；reviews/ 下无任何签署工件
```

我确认：**五项全部未签，产品实施不得开工，不得执行任何生产 prune**。本 attempt 只交付冻结规则、独立验证器、实测反例与建议决策（`decision.md` 末尾"Non-decisions"三条亦与实测一致）。

### 6. 我另外发现的记账/证据瑕疵（不改变裁决）

- `handoff.json` 自相矛盾：`reviewer_status` = `"PENDING independent review"`，同文件 `review_r2_outcome` 却称已返回 `accepted_scoped`（`review.md:3` 亦自述"Written by the implementer… NOT an acceptance"）。**此前的 r2 结论在盘上没有任何独立载体**；本段即为该结论的落盘载体。
- `review.md` 的证据引用统一缺 `after_pass/` 前缀（树中不存在顶层 `evidence/` 目录，实际文件在 `after_pass\evidence\`）。
- 负例退出码记录不一致：`binding.json` 写"exits 98 with BINDING-REFUSED"，`commands.json` 的 CMD-I15A-C8 记 expected/raw rc=0；我实测脚本自身 rc=0（拒绝信息打在 JSON 输出里）。二者需统一口径。
- `evidence/pytest_full_stdout.txt` 只是 C7 stdout 的副本（18739 B，与 `after_pass/cmd-C7/stdout.txt` 同尺寸），不构成第二份独立证据。
- 未验证（原样保留）：真实的 25.7M 行 / 49.7GB 规模 prune；`worker-pause` 的锁内位置（属卡三 C2）；`archive_retired_evidence.py:65` 的 `"wt"` 覆写风险只被"测量"，未修。

### ▶ 可原样粘贴进 `review.md` 的裁决正文

```
## 独立 reviewer 裁决（2026-09-20，独立 session；范围：冻结证据/诊断）

**裁决：`accepted_scoped` —— 仅限"冻结证据 + 诊断反例"范围；不授予产品实施资格；产品实施仍 blocked。**

1. 冻结成立：`oracle.md`（sha256 `7ad1ac77…`）mtime `01:28:15` 早于本 attempt 任何一次运行（首个运行目录
   `before_pass/cmd-C1` 为 `01:28:58`）；W15-R1..R8 与固定样本（5 span，期望 delete `{a1,a2}` /
   retain `{a3,b1,c1}`）在任何实测输出之前写定，期望常量在 `harness/archive_verifier.py` 中为预列常量，
   不由产物推导。
2. 五类反例有可复现证据，且我在**隔离副本**中重跑复现：`6 failed, 5 passed`，失败恰为 P1、P2-幂等、
   N1-空目录、N2-时钟、N3-TOCTOU、N4-崩溃（记录原文 `after_pass/cmd-C7/stdout.txt` 末尾
   `6 failed, 5 passed in 1.82s`，与 commands.json C7 一致）。产品侧机制我逐行核对：
   `prune_retired_evidence.py:27-30` 删除"所有 retired 文档的全部 span"（从不查归档）、`:66-76` 以
   `archive/` 下**最老目录名**与 `datetime.now()` 计算 due、`:114-123` 直接批删、`:125-142` 收据在整
   循环结束后才写；`archive_retired_evidence.py:48-51` 按当日目录、`:65` 以 `"wt"` 截断写快照。
3. 我独立复算的 oracle 值：交付 gzip sha256 `4798b971…`，解压 3 行、span_ids `[a1,a2,c1]`，按
   `sha256(json.dumps(row,sort_keys=True,separators=(",",":")))` 复算得 a1 `615eed4ade8db004…`、
   a2 `64e883ee393cadf7…`，与 `restore-proof.json` 的 `pre_delete_digests` 逐字相同。F-I15A-01 更正
   成立：attempt 内 117 个文件无一命中 `85d2f08e…`。
4. 攻击项回应：① 期望值非事后拟合（见 1）；② 交付件内容由我自行解压复算（见 3）；③ 崩溃后 4 行确认
   无法从任何持久工件恢复——重跑副本的 `n4-crash` 现场为 `evidence_spans=['c1']`、无 `-wal`、
   `freelist_count=0`、无任何 `prune-retired*` 收据；④ `guard_scratch` 为硬门：副本放在不含
   `execution_runs` 的路径时 11/11 直接 `BINDING-REFUSED`，放到合规路径后复现 6/5；生产路径（含
   `.source_catalog`）被拒且 `opened_connections=[]`。
5. 记录一致性：`changes.diff`（sha256 `dbb44c12…`）声明本卡零改动，其 7 个产品文件哈希与现网逐一相符，
   `binding.json` 另两个只读邻居亦相符 ⇒ 9/9 命中。**说明**：本卡 `iso/` 内没有实现补丁（顶层只有
   `venv`），故"iso 内补丁哈希"无对象可核；等价的产品哈希台账已通过。生产 catalog 为
   `49,677,344,768 B / mtime 2026-09-19T06:31:35Z`（只读 Get-Item，未打开）；`worker_control.json`
   sha256 `9fcbe233…` 未变。
6. **D-W15 五项仍未签**：`decision.md` 自述为"proposed decision, submitted for signature"，D-W15-1..5
   均标注需签署；PLAN 内无任何签署工件；`handoff.json.blocked_by` 明列未签的 D-W15。⇒ **产品实施仍
   blocked，不得开工，不得执行任何生产 prune**。
7. 保留记账问题（不改变裁决）：`handoff.json.reviewer_status` 仍为 `PENDING independent review`，与同
   文件 `review_r2_outcome`（称已返回 accepted_scoped）自相矛盾；此前的 r2 结论在盘上无载体，**本段即
   该结论的落盘载体**。另：`review.md` 引用证据统一缺 `after_pass/` 前缀；`binding.json` 写负例
   "exits 98"而 `commands.json` C8 记 expected/raw rc=0（实测 0）；`evidence/pytest_full_stdout.txt`
   只是 C7 stdout 的副本。
8. 资格边界：本 `accepted_scoped` 仅覆盖该 attempt 的冻结证据与诊断结论，**不授予**产品实施、生产
   prune、schema/事务/恢复机制选择、真实 25.7M 行 / 49.7GB 规模正确性，以及固定时钟可注入、旧归档
   升级、产品侧 restore 入口等未实现能力的任何资格。
```

---

# 卡三 I-04-C（r3 的 3 项 still-required 是否关闭）

## 裁决：**`accepted_scoped`（限本 attempt 的设计文本与模拟结果）**，附 1 条 P3 文字性 erratum；C2 仍为 owner 门且不阻塞签收

`review.md:114` 的 §5「reviewer 结论」在盘上确为空（`:116-120` 全为占位符）；handoff.json 的 `blocked_by` 为 `[]`。

### 1. still-required ①（错误码/超时用例）：**关闭**（我复跑复现）

实现侧（`sim/kernel.py` 的 `FileLock.__init__(code=…)`／`lease_lock()` 传 `code="lease_lock_timeout"`）与冻结文本一致，且 4 个**真超时**用例在盘上有原始进程输出：

```
F-T1 stdout.A.txt: "code": "lease_lock_timeout", "action": "lease_lock_timeout", "writes": 0,
                   "error": "lease_lock_timeout: lock filing_fetch_pause.lock wait > 0.05s"
F-T2 stdout.A.txt: "code": "lease_lock_timeout", … "wait > 0.0s", "writes": 0  （且 journal 无 lock_acq）
F-T3 stdout.A.txt: exit 信封 "action": "release_fail_closed", "cleanup_status": "failed:lease_lock_timeout",
                   "writes": 0；enter 信封 "action": "paused_by_us"（请求段结果未被清理段污染）
```

我的隔离副本复跑（`%TEMP%\…\I04C-copy`，用该 attempt 的 iso venv python）：

```
cases=28 pass=28 fail=0 harness_error=0 failing_checks=0
F-T1 PASS (7 checks) / F-T2 PASS (3 checks) / F-T3 PASS (6 checks) / F-T4 PASS (8 checks)
scheduler SUMMARY: {"failures": [], "total_seconds": 64.409}
```

### 2. still-required ②（队列跨预算边界 + 队列成本）：**关闭**（我复跑复现同一结论，数值随调度浮动）

F-T4 现场（我复跑）：6 个 enter-only 参与者、注入临界区保持 H=0.4 s、锁预算 1.0 s ⇒

```
P0 paused_by_us (lock_wait 0.000397, writes 1)
P2 paused_by_us (lock_wait 0.592609, takeover owner_pruned:dead, writes 2)
P1/P3/P4/P5 lease_lock_timeout ("wait > 1.0s", writes 0)
budget_consumed_by_queueing: {"P0": 0.0, "P2": 0.593}    （attempt 记录为 {"P0":0.0,"P2":0.572}）
refcount 中途 entries 非空、收尾 entries [] 且 resume_required=false
```

锁预算公式与队列代价文本已进入正文：`decision.md:68-69`（ADR-2 `lock_budget_for(x)=min(x,LOCK_MAX_SECONDS=60)` 且保留 v1.2 更正注记）、`:138`、`:229`、`:245`、`:392`、`:465+`（§14 F-I04C-12）、`oracle.md` R3-2。

### 3. still-required ③（陈旧文本与 F-LK2 数值）：**关闭**（原文保留 + 追加更正，且"追加"经我独立运行证明）

- 原文**确实保留**：`decision.md:410`（§13.5 仍印 `[12, 19, 7, 26, 43]`）后紧跟 `:414` 更正段（自述"原文一字未删"）；`decision.md:69`/`:245` 的更正注记里仍引用旧文本 `min(10.0, 相位预算)`／`min(10, 相位预算)`；`review.md:49`（P3-4 旧行）后紧跟 `:53-63` 更正段。
- "只追加、未删改"由我**亲自运行**其只读校验器得到：

```powershell
& <I-04-C iso python> -B sim/verify_r4_appendonly.py
→ APPEND-ONLY PROOF (round 4)
  [PASS] decision.md: reconstructed sha256 == pre-change sha256  (bb9bb0f401e573409842afd7bfc7a17eb3d5dd52b79e134f41417f1aa0a6f479)
  [PASS] review.md:   reconstructed sha256 == pre-change sha256  (8cc116bced471b721bf28f1a15f9daf3e875e720ad9cb3e7eb0ebd3966289a57)
  VERDICT: APPEND-ONLY CONFIRMED   （exit=0）
```

- F-LK2 真值：`evidence/flk2-recompute.txt` 末段 `TRUTH: finals [16,35,10,56,18] => lost_updates [184,165,190,144,182] (range [144,190]), expected 200`，且其 C1 证伪旧组（`200-[12,19,7,26,43]=[188,181,193,174,157] ≠ [197,185,191,198,14]`）。算术自校验：`200-16=184, -35=165, -10=190, -56=144, -18=182` 全部成立（与父代理 C1 结论一致）。
- 我另跑锁与 legacy 反例套件（`cases=7 pass=7 fail=0`），**我这轮的 F-LK2 组是 `finals=[16,6,25,115,8] ⇒ lost=[184,194,175,85,192]`**，与记录组不同，但同样满足 `lost = 200 - finals` 且 `determinism="NOT deterministic…"` —— 这从另一角度证实：该组本质是调度相关，卡片只作定性断言是正确的；被更正的只是"印在正文里的那组数与证据不符"。

### 4. C2（OPEN-3）仍为 owner 裁定项，且不阻塞

`decision.md:396`（"OPEN-3 交叉引用（C2 登记）… 登记为 **OPEN-3 = owner 门（C2）**"）、`handoff.json` 的 `owner_gates[0]`（`kind: "OWNER RULING item, not an implementation item"`，`status: "open_owner_ruling"`，`does_not_block: "does not block the accepted_scoped sign-off"`）、`review.md:26`（OPEN-3 行把"60 s 上限命名/边界"与"是否允许 `worker-pause` 在锁内"一并列为 owner 待裁）三处一致；`handoff.json.blocked_by = []`。

### 5. 生产仓零改动：成立

```
git -C C:\Users\郑曾波\Projects\filing-fetch status --porcelain  → （空）
iso/filing-fetch 与生产 filing-fetch 逐文件 SHA256 对比 → 无 DIFF、无 ISO-ONLY
  （精确口径：iso 共 118 个文件，覆盖 SKILL.md / pyproject.toml / config / references / scripts / tests /
   tools；与生产同路径文件 0 个哈希不同，且 iso 无任何生产不存在的文件。生产侧另有 270 个文件不在 iso：
   165 .mypy_cache、65 e2e、13 .ruff_cache、10 根目录文件、5 .pytest_cache、5 .codegraph、4 assurance、
   2 .githooks、1 .github —— **scripts|tests|tools|config|references|src 下没有任何生产独有的文件**，
   即 iso 是完整源码/内容树而非抽样。）
(Get-FileHash C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py).Hash
  = 046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088  ← 与卡片锚点/run-summary 完全相同
git -C C:\Users\郑曾波\Projects\company-wiki status --porcelain
  →  M CLAUDE.md /  M README.md   （既有用户改动 + I-00-D 的两处边界文本，非本卡）
```

### 6. 我新发现的问题（均不推翻上述三条关闭结论）

- **[P3-erratum E1｜数字引用错] `review.md:24`** 写"`evidence/phase-wall.txt`（F-L2d 8 并发最大等待 **9.87 s**、相位墙 **13.2 s**）"，而该文件当前且最后一次写入的内容是：

```
{"case":"F-L2d", … "max_lock_wait_seconds": 9.782719, "phase_wall_seconds": 13.386}
```

  应为 **9.78 s / 13.4 s**（9.87 疑为数字换位）。这与本卡 still-required ③ 同类（卫生级），建议同轮文字更正；不改变设计结论。
- **[P3｜断言强度] `sim/cases_timeout.py:206-211`** 的子句 `not any(lease in successful_ids is False for lease in view["entries"])` 在 Python 中是**链式比较**（`(lease in successful_ids) and (successful_ids is False)`），恒为 `False`，故该子句恒真、永不失败。最小复现：

```
clause value = True
same clause with a WRONG entry = True      ← 放入错误条目仍判 True
```

  同一 check 的其余合取项（`all(lease in successful_ids …)`、`view["entries"] != []`）仍有意义，故该 check 未失效，但其"漏判面"确实存在。另 `:213-216` 的"the queue wait is reported" 断言传的是 `True`（记录装置而非断言），`:201-203` 的 winners+joiners 计数在构造上近乎恒真。建议下一轮加强，不影响本次复现结论。
- **[P3｜证据缺口，已由我补齐] CMD-I04C-08 无原始日志**：`commands.json:233` 与 `handoff.json:184` 声称 "8 passed / 109 deselected"，但 attempt 内检索 `deselected` 只命中这两个**声明**文件，没有任何 raw log。我从 `iso/filing-fetch` 的 TEMP 副本独立重跑：

```
8 passed, 109 deselected in 0.32s      （exit=0）
```

  结论：该声明**为真**，但实现者未留原始日志（本卡其余命令均有 raw log）。建议补留证据或标注"由 reviewer 复现"。

### ▶ 可原样粘贴进 `review.md §5` 的裁决正文

```
## 5. reviewer 结论（独立 reviewer session，2026-09-20）

- 第二轮结论：`accepted_scoped`（**限定：仅本 attempt 的设计文本与模拟结果**；不含任何产品实现/部署资格）
- 复算过的 oracle：
  ① 我在隔离副本（%TEMP%，不写生产仓）重跑协议套件：`cases_in_log=28 pass=28 fail=0 harness_error=0
     failing_checks=0`，其中 F-T1/F-T2/F-T3/F-T4 = 7/3/6/8 checks 全 PASS；`sim/static_check.py` S1–S4
     全 PASS；锁与 legacy 套件 `7 pass / 0 fail`。
  ② F-LK2：我复算 `200 − finals == lost_updates` 恒成立；`evidence/flk2-recompute.txt` 的真值组
     `[16,35,10,56,18] ⇒ [184,165,190,144,182]`（range [144,190]，expected 200）逐项自洽；旧组
     `[12,19,7,26,43] ⇒ [197,185,191,198,14]` 与之矛盾（C1 证伪）。我这一轮的实测组为
     `[16,6,25,115,8] ⇒ [184,194,175,85,192]`，与记录组不同但同守 `lost = 200 − finals`，且
     `determinism = NOT deterministic` ⇒ 该量只能定性断言，卡片口径正确。
  ③ 追加性：我亲自运行 `sim/verify_r4_appendonly.py` ⇒ `APPEND-ONLY CONFIRMED`（decision.md 重建
     sha256 `bb9bb0f4…`、review.md `8cc116bc…` 与改前快照逐字相等）；旧文本 `[12,19,7,26,43]`、
     `min(10.0, 相位预算)` 在 `decision.md:69/245/410` 与 `review.md:49` 均**原样保留**，更正在其后追加。
- 三项 still-required 的逐条处置结论：
  ① 错误码/超时用例 —— **关闭**。请求段 `code/action = lease_lock_timeout` 且 `writes=0`（F-T1，预算
     0.05 s，真外部持锁）；预算 0 时不尝试加锁（F-T2，journal 无 `lock_acq`）；清理段
     `cleanup_status=failed:lease_lock_timeout` + `action=release_fail_closed`，义务与 owner 证据保留、
     worker 仍 paused（F-T3）。
  ② 队列跨预算边界 + 队列成本 —— **关闭**。F-T4（6 参与者 × H=0.4 s，锁预算 1.0 s）⇒ 4 人超时零写、
     成功者 {P0,P2}、超时者绝不入 refcount、收尾 entries=[] 且 resume_required=false；队列代价以
     `budget_consumed_by_queueing` 记录（本次 {P0:0.0,P2:0.593}，attempt 记录 0.572，属调度浮动）；
     `(N−1)·H` 模型与"排队消耗下载预算"已写入 ADR-2 正文/§5 码表/§14 F-I04C-12 与 oracle R3-2。
  ③ 陈旧文本与 F-LK2 数字 —— **关闭**。见上"追加性"与"F-LK2"两条；正文旧值保留、更正追加，未删改。
- C1（§13.5 与 review §1 的 F-LK2 过时值）：**关闭**（真值 `[16,35,10,56,18] ⇒
  [184,165,190,144,182]`；`verify_flk2.py` 13/13；追加性证明见上）。其中"父代理已复算"与本次独立复算
  结论一致。
- C2 = OPEN-3：**仍为 owner 裁定项，且不阻塞本次签收**。待裁两项：(a) 上限常数 60（
  `lock_budget_for(x)=min(x,60)`）的命名与边界验收；(b) `worker-pause` 是否允许留在锁内。三处登记一致
  （`decision.md:396` 及 §8 O-3、`handoff.json.owner_gates[0]`「OWNER RULING item…
  does_not_block: does not block the accepted_scoped sign-off」、本文件 §6 OPEN-3 行）；
  `handoff.json.blocked_by = []`。owner 未裁前实现继续使用冻结值 60。
- 生产仓零改动：**确认**。`filing-fetch` porcelain 为空；`iso/filing-fetch` 的 118 个文件与生产同路径文件
  SHA256 全部相同且无 iso 独有文件（生产多出的 270 个文件均为缓存/e2e/CI/规划文档，代码与内容目录下无
  生产独有文件）；生产 `scripts/fetch_filing.py` = `046cc7dc…`（与卡片锚点相同）；`company-wiki`
  porcelain 仅 ` M CLAUDE.md` / ` M README.md`（既有用户改动 + I-00-D，非本卡）。
- 未复现/未验证项：真实 provider/worker/wiki 并发；DECLARED 判活与真实探针的等价性（I-04-D 前置）；
  POSIX/SMB 锁语义；真实 PID 复用检测；同进程多线程 scope；`worker-pause` 锁内位置的取舍（=C2）；
  `I04C-08` 的原始日志缺失（该声明已由我在 TEMP 副本复现 `8 passed, 109 deselected`，但 attempt 内
  无 raw log）。
- 需实现者同轮做的文字性 erratum（**不改变本裁决**）：
  E1 `review.md:24` 的 "最大等待 9.87 s、相位墙 13.2 s" 与所引 `evidence/phase-wall.txt` 不符，该文件
     记录为 `max_lock_wait_seconds=9.782719`、`phase_wall_seconds=13.386`，应改为 9.78 s / 13.4 s；
  E2 `sim/cases_timeout.py:206-211` 的 `lease in successful_ids is False` 是链式比较、恒为 False，该子句
     永不失败；`:213-216` 的"queue wait is reported"断言传 `True`。建议加强（本轮不影响结论，因为
     F-T4 的实质合取项与我的复跑一致）。
- 授予的资格：本 attempt 的设计文本与模拟结果（ADR-1..12 + R1–R5 分支表 + 错误码/超时与队列边界口径 +
  F-T1..F-T4 与既有 28 例的模拟通过事实）。
- **明确不授予**：任何产品实现/合并/部署资格；真实并发、真实锁语义与真实判活的等价性；生产 pause
  refcount 的任何写入；I-04-D/E 及以后的实现资格。
- reviewer：独立 reviewer session（本次收尾复核），2026-09-20。
```

### 本节未验证项

1. 未在**生产 attempt 目录内**重跑（那会写生产仓）；所有复跑都在 `%TEMP%` 副本 + junction 到该 attempt 的 iso venv，故我复现的是"同一份 sim 代码 + 同一解释器"的行为，不构成对实现者当次运行环境的字节级还原。
2. 未复核 `decision.md`/`oracle.md` 的全部 12 条 ADR 文本与 `review.md` §1 的每条 P1/P2/P3（本轮范围是 3 项 still-required + C2 + 生产零改动）；`F-L4a` 的 LIMITATION、ADR-10e 并发转让不变式仍属未证项（handoff 亦自认）。
3. `evidence/hashes.txt` 的 43 项清单我只做了代表性校验（关键文件 + 生产锚点），未逐行重算全部 43 项。
4. 未评估 C2 两项待裁的技术优劣（属 owner 裁定，不属复核范围）。

---

# 跨卡未验证清单（汇总）

1. 三卡的全部结论均基于"盘上载体 + 我的隔离复现"，**没有任何一次对生产运行环境的字节级还原**；I-00-A 的历史 porcelain、I-15-A 的 r2 reviewer 身份、I-04-C 当次运行环境均在不可回放之列。
2. 我未打开 49.7 GB 生产 catalog（仅 `Get-Item` 取 size/mtime），未对 `assurance/`、D: 盘、worker 做任何触达。
3. 生产仓只读校验只覆盖与本三卡相关的路径与哈希；`revenue-forecast` 自身的既有脏文件（`SKILL.md`/`references/*`/`CHANGELOG.md`/`assurance/runs/daily_alert.jsonl`）按任务前提视为用户既有改动，本轮未做内容比对。
4. 任务书对卡二"`iso/` 内实现补丁"的表述在 I-15-A 上无对象（`iso/` 只有 venv），对卡一"三个 `*.wrong-capture.txt`"的表述与盘上不符（只有两个）——两处均已按盘上事实处理并写明。
