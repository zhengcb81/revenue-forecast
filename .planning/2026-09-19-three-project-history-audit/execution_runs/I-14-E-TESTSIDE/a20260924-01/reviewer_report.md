# I-14-E-TESTSIDE / a20260924-01 — 独立复审报告（独立复审工位，非实现者）

复审对象：`execution_runs/I-14-E-TESTSIDE/a20260924-01/` 首版交付（`handoff.json` 53603 B，
sha256 `3f9d4ede5d1f50e8fb02f70ea820b584c5a74037b38b081f47907a8904e4ca92`，
`status=review_pending`、`implementer_signed=false`、`blocked_by` 1 条、`unverified` 5 条）。
授权：`OWNER_DECISIONS.md` §二十五（owner 选项 A，另立施加卡）；卡文 `execution_v2/card_I-14-E-TESTSIDE.md`。
复审时刻：2026-09-25 22:2x（本机时钟；本交付内标注 `Z` 的时间戳 = 本机时间 − 1 h，见 P3-4）。
本报告只写入 `reviewer_report.md` + `reviewer_report.sha256`；**未改本 attempt 任何既有字节，未写 status，未签 ACCEPT。**

VERDICT: blocked

判定要点：实现者声称的 `ENV-OPENPROCESS-ALLACCESS-DENIED` **经我独立复测成立**（原始 winerror 见 §1），
因果链**逐环节坐实**（§2），三臂 18 次运行**无一混入时序断言失败**（§3），
边界与 `changes.diff` **我独立复算通过**（§4、§5），oracle 冻结**先于首跑**（§6）。
⇒ 没有发现"用环境借口掩盖"的迹象（**无 P1**），交付形态是 fail-closed 的正确做法（未造绿样）。
但**红的时序形态、绿 6/6、变异判别力三者在本会话确实无法演示**，其解除条件是**会话权限（owner/派工侧）**，
实现者与我在本会话内都无法解除（审批禁用）⇒ 判 `blocked`（而非 `changes_required`）。
**本报告不解除任何 BLOCKED、不产生 ACCEPT、不改任何卡 status。**

---

## 1. 必核项 1 — `ENV-OPENPROCESS-ALLACCESS-DENIED` 是否成立（我自跑的等价探针）

探针脚本（我自己写，落在 `%TEMP%`，不在 attempt 内）：
`%TEMP%\i14e_reviewer_openprocess_probe.py`、`%TEMP%\i14e_reviewer_handle_probe.ps1`，
解释器 = 本 attempt 的 `venv/Scripts/python.exe`（3.13.9）。

### 1.1 ctypes `OpenProcess` 原始结果（**winerror 逐条实测，非转述**）

| 轮次 | 目标 | 掩码 | 结果 |
|---|---|---|---|
| A（内联） | self pid=10464 | `PROCESS_ALL_ACCESS (0x1F0FFF)` | **handle=0，winerror=5** |
| A | self pid=10464 | `PROCESS_QUERY_LIMITED_INFORMATION (0x1000)` | handle=304（成功） |
| A | pid=4（System） | `PROCESS_ALL_ACCESS` | **handle=0，winerror=5** |
| A | pid=4 | `PROCESS_QUERY_LIMITED` | **handle=0，winerror=5**（受保护进程） |
| B（脚本） | self pid=11220 | `0x1F0FFF` | **handle=0，winerror=5 (0x5 DENIED)** |
| B | self pid=11220 | `0x1000` / `0x0400` | handle=0x1B8，winerror=0（成功） |
| B | **本探针自生子进程** pid=7228 | `0x1F0FFF` | **handle=0，winerror=5** |
| B | 同上 | `0x1000` / `0x0400` | handle=0x1F0，winerror=0（成功） |
| C | **6 个本会话未生成的现有进程**（explorer/powershell/svchost 系，pid 7960/3992/11824/21024/1248/1316） | `0x1F0FFF` | **6/6 全部 winerror=5** |
| C | 其中 4 个普通进程 | `0x1000` / `0x0400` / `PROCESS_TERMINATE(0x1)` | 全部 OK |
| C | 其中 2 个受保护进程（1248/1316） | 上述全部掩码 | 全部 winerror=5 |
| C | 4 个普通进程 | `PROCESS_CREATE_PROCESS (0x2)` | 3 个 winerror=5，1 个 OK |

**结论：`PROCESS_ALL_ACCESS` 对一切被测目标（含本会话自生子进程）一律 `winerror=5 ERROR_ACCESS_DENIED`；
`QUERY_LIMITED/QUERY_INFORMATION/TERMINATE` 对普通目标可用。** 与实现者声称一致。

### 1.2 因果链逐环节核验（读码 + 原始事件，非采信摘要）

| 环节 | 核验方式 | 结果 |
|---|---|---|
| ① `Start-Process … -RedirectStandard* -PassThru` 的 `.Handle` 为 null | **我用 Windows PowerShell 5.1 自跑**（`%TEMP%` 内，`powershell.exe -File`） | **带 redirect → `handle=[]`（IsNull=True）；不带 redirect → `handle=[2852]`** —— 与实现者 addendum-C §C1 行 3/4 完全一致，我在本会话复现 |
| ② `source_catalog_worker.ps1:340-341` | 读 iso 副本原文 | L340 `$ChildHandle = $Child.Handle`；L341 `[CompanyWiki.KillOnCloseJob]::Assign($ChildJobHandle, $ChildHandle)` —— **确实直接消费 `.Handle`**，null ⇒ `Assign` 抛 IntPtr 转换错 |
| ③ 抛错 → `launcher_exception` → exit 1 | 读 ps1 L484-500 | `catch` 内写 `Status='launcher_exception'`、`ExitCode 1`、`Reason='launcher_infrastructure_error'`、`exit 1` |
| ④ supervisor 在看门狗之前退出 | 读 ps1 L321-373 + 事件 | `child_started` 事件写在 `Assign` **之后**（L342-348），看门狗轮询在 L351 起；18/18 次事件文件**只有 2 行** `starting → launcher_exception`，无任何 watchdog/child_started |
| ⑤ `child_started=0` | 逐个读 18 个 `*-events.jsonl` | **red 6/6、green 6/6、mut 6/6 全为 0**（事件文件总行数=2） |
| ⑥ 消息原文 | 18/18 事件一致 | `Cannot convert argument "process", with value: "", for "Assign" to type "System.IntPtr": "Cannot convert null to type "System.IntPtr"."` |
| ⑦ 会话特异性（旁证） | 源卡 `I-14-E/a20260919-01` 原始事件 | 2026-09-21 同一 ps1（sha `5c12cd74…bc311`）产出过 `child_started` + `clean_exit`（uptime 11–12 s 多例）⇒ **当时 `.Handle` 拿得到** ⇒ 阻断是会话/环境差异，不是代码差异 |

**未证实的一环（诚实登记）**：.NET/PS 在 redirect 分支请求的**具体 access mask 没有被直接观测到**
（无 .NET 源码、禁联网）；"该调用要 ALL_ACCESS"是**推断**（只有 ALL_ACCESS 被测为拒绝，
`QUERY_LIMITED/QUERY_INFORMATION` 可用，故该失败调用必请求了 ALL_ACCESS 级以上权限）。
该推断不影响本卡判定：`.Handle` 为 null 与其下游后果均为直接观测事实。

---

## 2. 必核项 2 — 6 次 green 失败形态逐次判定

判定依据 = 每次运行自己的 `green/captures/green-p1-rN.txt` + `green-p1-rN-events.jsonl` + `green/tside-trace.jsonl`。

| # | 失败行 | 断言原文 | 传入 H | 事件序列 | child_started | 判定 |
|---|---|---|---|---|---|---|
| r1 | `test_source_catalog_worker_bootstrap.py:1040` | `assert completed.returncode == 0, completed.stderr`（→ `assert 1 == 0`） | 2.0（t0=0.483） | `starting → launcher_exception` | 0 | **环境 launcher_exception，非时序断言失败** |
| r2 | 同 1040 | 同上 | 2.0（t0=0.2065） | 同上 | 0 | 同上 |
| r3 | 同 1040 | 同上 | 2.0（t0=0.3106） | 同上 | 0 | 同上 |
| r4 | 同 1040 | 同上 | 2.0（t0=0.3095） | 同上 | 0 | 同上 |
| r5 | 同 1040 | 同上 | 2.0（t0=0.4089） | 同上 | 0 | 同上 |
| r6 | 同 1040 | 同上 | 2.0（t0=0.1944） | 同上 | 0 | 同上 |

- **精确表述**：6/6 都停在**启动器 rc 闸门**（`assert completed.returncode == 0`），其直接原因是
  supervisor `rc=1`，而 18/18 事件证明该 rc=1 来自 `launcher_exception`。
  **冻结的时序判据 `assert N == 2` / `TimeoutExpired` 从未被执行**（6 份 capture 中均无 `== 2` 断言文本；
  capture 内 `-WorkerHangTimeoutSeconds` 为 `2.0`，证明改动确实施加进被跑的测试）。
- 同法核红臂 6/6（失败行 **909** = 未改动文件的行号，H=0.5，同为 `launcher_exception`）与
  变异臂 6/6（失败行 1040，H=0.5，同为 `launcher_exception`）⇒ **变异无判别力**，实现者如实登记。
- ⇒ **"6 次 green 失败全是环境 launcher_exception、非时序"成立**；无任何一次是节点时序断言失败 ⇒ **不构成 P1**。
- 附注（对实现者有利/不利两面都记）：`rc==0` 本身是冻结判据 §3.D.1 的第一条，因此
  "**green 6/6 未证实**"的登记是准确的，不是措辞保守。

---

## 3. 必核项 3 — `unverified` 是否如实（有无把未验证写成已验证）

`handoff.unverified` 实为 **5 条**（任务书说"四条"，第 5 条是产品资格声明）：

| # | 原文要点 | 我的核验 |
|---|---|---|
| 1 | green 6/6 under cpu8 **NOT demonstrated**（全部败于环境 launcher_exception） | **属实**（§2 逐次核过） |
| 2 | mutation M1 **未构成判别性红** | **属实**（mut 6/6 与绿同因，H=0.5 vs 2.0 都红） |
| 3 | red 冻结形态**未复现**，观察形态是 `launcher_exception` 而非冻结期望 | **属实**（红臂 6/6 失败行 909 = rc 闸门；事件无 child_started）。注：按冻结 §3.C 字面"N=6 中 ≥1 次红即复现红成立"，红臂**字面上 6/6 红**，实现者**主动不认领**、按 addendum-C §C3 降级 —— 属**从严**方向，不是夸大 |
| 4 | 节点②未施加、无红可复现；引源卡 M-C `events 6/8 ≥15 s`、`exit max 21.593 ≥20 s` | **抽验属实**：源卡 `after/wrapper-latency-cpu8.json` L156/185 确有 `exit_seconds: 21.593 / max: 21.593`；源卡 `band-logon-cpu8` 存在且事件为 `child_started → clean_exit` |
| 5 | 产品资格（`disclosure_adaptation=unmapped`、`accuracy=unproven`）不授予 | 与卡文资格范围一致 |

**未发现任何"未验证写成已验证"**：`nine_steps` 中 step3=`partial`、step4=`not_demonstrable`，与证据一致；
step1/2/5/6/7/8/9 的 `done` 我逐项复算（§4–§6、§8），均成立。
实现者**没有**把三臂任何一条写成绿。

---

## 4. 必核项 4a — 边界与零改动（三 hash 自己复算）

### 4.1 三个边界文件 sha256（我自己算）

| 文件 | 字节 | sha256 |
|---|---|---|
| `before/final_hashes.json` | 4312 | **`aea2dbf036863a5c107306988272a691fed400bdc33ab5442d703759ada79142`** |
| `after/final_hashes.json` | 4312 | **`aea2dbf036863a5c107306988272a691fed400bdc33ab5442d703759ada79142`** |
| `after/boundary_check.json` | 4312 | **`aea2dbf036863a5c107306988272a691fed400bdc33ab5442d703759ada79142`** |

⇒ **三者同值，与任务书给的 `aea2dbf036…` 一致**（内容亦逐字节相同，`all_required_equal=true`、`verdict=BOUNDARY_OK`）。

### 4.2 对**活树**独立复算 manifest（不采信记录，用 `harness/hashes.py` 同款算法我重跑，只读）

| 目标 | 我算的 files / bytes | 我算的 manifest | 记录值 | 判定 |
|---|---|---|---|---|
| `CW/src`（真仓） | 152 / 1870859 | `34ee472e08d7cb441aaa1ee05a9d7c981672696d92c658d79ffb4173a79192af` | 同 | ✓ |
| `CW/scripts`（真仓） | 135 / 1583829 | `e7ccf6e3020cf32433bfe66b9b29d92987fa7b9b714284ac15fd38563355847f` | 同 | ✓ |
| `CW/tests`（真仓） | 348 / 2962813 | `369aa19eb61c469dc4040ce92c80dae7dde779b3ba5e80ba8c42fc8aaa3a1c8e` | 同 | ✓（真仓 tests **零改动**） |
| `iso/src` | 152 / 1870859 | `34ee472e…92af` | 同 | ✓（iso 产品码零改动） |
| `iso/scripts` | 135 / 1583829 | `e7ccf6e3…847f` | 同 | ✓ |
| `iso/tests` | 348 / 2968382 | `c6e510845ba5bb96865c4dc0ca7e0af5032d7c2c40919f26426e64e02d44d456` | 同（= 记录的 after） | ✓（唯一改动面，按预期改变） |

附加：真仓 `company-wiki` 独立检查 —— HEAD `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121`（branch `fcap`）、
`git diff HEAD --name-only` 仅 **3 条既有路径**（`CLAUDE.md`、`README.md`、`src/company_wiki/source_catalog/artifact_dag.py`）、
untracked=0；真仓 `tests/contract/test_source_catalog_worker_bootstrap.py` = **40868 B / `32515aa6…c005c1`（未动）**。
源卡 `I-14-E/a20260919-01` 最新 mtime = **2026-09-22 09:59:08**（早于本 attempt）⇒ **源卡字节未被本卡触碰**。

### 4.3 `git diff HEAD --name-only` 非 `.planning`（我自己跑）

`git -c core.quotepath=false diff HEAD --name-only` → **3826 条，全部 `.planning/**`，非 `.planning` = 0**
（stderr 仅 CRLF 归一化 warning）。**未用 `git status`。**

---

## 5. 必核项 4b — `changes.diff` 是否只含 `tests/**`

- 字节/sha（我复算）：**6533 B / `3952cff55f17b57e189e76c94df1f63dae1dbf4ee13902b3bb04b281bbc6db72`** —— 与 handoff 一致。
- 头部（逐行读全 153 行）：唯一文件 `a/tests/contract/test_source_catalog_worker_bootstrap.py`；
  `---`/`+++` 头 **0 条**指向 `src/` 或 `scripts/`。
- **我在 `%TEMP%` 隔离副本实跑** `git init` + `git apply --check` → **rc=0**；随后 `git apply` → 产物
  **46437 B / `a1cfeb13f3ee4e1c155546daaf59e0b50c08836da62ef6c55e8f6be7baa67fb0`**，
  与 handoff `changes.files[0].after_sha256` 及 iso 现文件**完全一致**。
- 内容判读：只改节点① 的 `worker_hang_timeout_seconds`（0.5 → 导出 H）+ 新增 t0 测量/记录 helper；
  `assert … == 2`、`reason == "session_start_timeout"`、外层 `timeout=15` **均未动**；**未采用建议 3（放宽断言）**。
  ⇒ **不含任何 `src/`、`scripts/`，只含 `tests/**`。**

---

## 6. 必核项 5 — oracle 冻结时序（mtime 我实测）与"只追加不改原文"

| 文件 | 字节 | sha256（我复算） | mtime（本机） |
|---|---|---|---|
| `oracle.md` | 18520 | `4c15948e24a2650bf055dddd02b5cc230b561b89de1cf0f34c9a0e293b28f658` | **21:42:00** |
| `before/freeze_instant.json` | 996 | `b61a2fd0…5597`（`frozen_utc=2026-09-25T20:42:26Z`、`runs_started_before_freeze=0`） | **21:42:26** |
| `oracle-addendum-A.md` | 4198 | `c2f62c89c766b4ad12afb5677dbb0a26035cb229acb7900ca1f6e212ee4f37e7` | **21:46:05** |
| **首份证据** `red/captures-attempt1-infra-invalid/red-p1-r1.txt` | 7611 | — | **21:48:50**（其 band 21:49:10；`red/diag1` 21:51） |
| `oracle-addendum-C.md` | 6071 | `c1b09b31a5c8a010759378fec20c9e2591682db93c23809d0ca65a766ce0f0ce` | **22:07:55** |
| 红臂正式重跑 capture / band | — | — | 22:09:22 / **22:10:35** |
| 绿臂 band | — | — | 22:12:31 |
| 变异臂 band | — | — | 22:14:32 |

判定：
- **`oracle.md` 与 `oracle-addendum-A` 都早于首份证据** ✓（冻结 21:42:26 < 首跑 21:48:50）。
- **`oracle-addendum-C` 晚于首份证据**（22:07:55 > 21:48:50），**早于红臂正式重跑**（22:09:22）——
  它本身是"环境阻断"的 erratum，其 §C4 **主动登记了自己之前已发生的运行**（作废的 attempt1、diag、探针）⇒
  **属如实的事后追加，不是倒填**；但若按"三件都须早于首份证据"的字面口径，则**该条不满足**，如实记为 P3-5。
- **只追加不改原文（前缀复算）**：`oracle.md` 现 sha256 与 `freeze_instant.json` 记录值**完全相同**
  （18520 B / `4c15948e…8f658`）⇒ 冻结后**主文零改动** ✓；addendum-A/C 为**独立文件**，
  各自首行声明"追加式 erratum，上文一字未改"，且 A 只改 §5.1 落点、C 只登记阻断 ⇒ 未回写主文 ✓。
- expected 来源：`oracle.md §3` 明确写"全部由源卡原始数据手算、不由本卡重跑生成"；
  我抽验了源卡侧数字（`wrapper-latency-cpu8 max=21.593`、`band-logon-cpu8` 存在）✓；
  **未逐条复算 §3.A 的 48 行 24×2 手数（见 §9 未验证）**。

---

## 7. 发现分级

### P1 — 无
未发现：失败形态中混入时序断言失败（18/18 均为 rc 闸门 + `launcher_exception`）、
boundary hash 不同值、`changes.diff` 含 `src/`/`scripts/`、产品码/真仓测试被改、造绿样。

### P2（须在重交时修正，但不改变本判定）
1. **`blocked_by.evidence[0]` 指针失效**：原文写"ALL_ACCESS denied / QUERY_LIMITED ok, **recorded in this handoff's `probe_runs`**"，
   但 `handoff.json` **根本没有 `probe_runs` 键**；attempt 内也**没有任何探针原始输出落盘文件**
   （只有 `harness/openprocess_probe*.py` 脚本 + addendum-C §C1 的**转述表**）。
   ⇒ 关键环境证据**缺原始输出**。实质结论我已独立复现（§1），故不推翻判定，但证据包不完整。
2. **`.planning` 之外的写入**：仓库根出现 `probe_root_m700/`、`probe_root_m777/`、`probe_root_m777kw/`
   （各含 1 个 1 B `f.txt`），**created=modified=2026-09-25 21:54:02** —— 与 attempt 内
   `probe_att_m777*/f.txt` **同一秒**，属本卡探针产物，**位于 `.planning` 外**（卡文写入表第 4 行"禁止"），
   且 `after/analysis.md §8.4` **只登记了 attempt 内残留、未披露这三个目录**。
   它们是 untracked ⇒ `git diff HEAD --name-only` 非 `.planning` 仍 = 0（该不变量未破），无任何受跟踪字节被改。
   按卡文 P1 只落在第 3 行（`src/`、`scripts/`）判 **P2**；若 owner 按第 4 行字面零容忍，可上抬，我如实标注两可。

### P3（记录级，不影响判定）
1. `oracle.md` 自述"冻结时刻 2026-09-25T20:40Z"，`freeze_instant.json` 为 `20:42:26Z`（差 2 分钟，以记录文件为准）。
2. `oracle-addendum-C` 标题写"主文与 **A/B** 均未改"，但**不存在 addendum-B**（悬空引用）。
3. `oracle.md §7` 预期产物名 `mut/band-mut-m1.json`，实际交付 `mut/band-mut.json`。
4. 交付内所有 `…Z` 时间戳 = 本机时钟 − 1 h（`handoff.generated_utc 21:21:33Z` ↔ mtime 22:21:35），
   跨 attempt 拼时间线时须统一口径。
5. addendum-C 晚于首份证据（见 §6，属如实事后登记，非倒填）。
6. `before/hashed_before.json.git_revenue_forecast` 记录了 `gbk codec` 解码错误（已如实登记，无实质影响）。

---

## 8. 给 owner 的恢复条件（**我解除不了任何 BLOCKED，仅供派工**）

1. **环境**：提供一个其令牌能对自己的子进程 `OpenProcess(PROCESS_ALL_ACCESS)` 成功的会话。
   **自检口径（二选一即可）**：① `ctypes.OpenProcess(0x1F0FFF, False, 自生子进程 pid)` 返回**非 0 句柄**；
   ② `powershell.exe` 内 `Start-Process … -RedirectStandardOutput/-RedirectStandardError -PassThru` 的
   **`.Handle` 非 null**（本会话实测为 null ⇒ 不满足）。
2. **复跑**：在该会话按 `oracle.md §4` 原样重跑三臂（C1=cpu8、N=6/臂、90 s driver 超时、同 basetemp 口径）；
   **oracle 无需重冻**（expected 全部来自源卡原始数据）；判据以 §3.C/§3.D/§3.E 为准：
   红的**时序形态**（`assert N == 2` / `TimeoutExpired`）、绿 **6/6**（含 §3.D 四条子判据）、变异 **≥1 红且与绿有判别力**。
3. **重交时同时修正**：P2-1（把 `openprocess_probe*` 原始输出落盘并修正 `blocked_by.evidence` 指针）、
   P2-2（删除或披露仓库根 `probe_root_*` 三目录）。
4. **若复跑后绿仍不成立**（同环境、同 oracle）⇒ 届时应判 `changes_required`：回退测试改动、
   `changes.diff` **不得晋升**；保留全部原始日志（卡文"恢复"条）。
5. **晋升（把 `changes.diff` 应用到真 `company-wiki/tests/**`）属独立授权**，本报告不授权、不执行。

---

## 9. 本报告的 `unverified`（我没验成/没验的，缺证据写未证实）

1. **三臂的可演示性**：红的时序形态、绿 6/6、变异判别力 —— 在本会话**无法演示**（同一环境阻断，
   且审批禁用 ⇒ 我不能放宽权限）；我**没有**重跑三臂，因此**不产生任何新的红/绿/变异样本**。
2. **.NET/PS redirect 分支请求的具体 access mask** 未直接观测（推断为 ALL_ACCESS 级，见 §1.2）。
3. **`oracle.md §3.A` 的 24×2 手数复算**（48 行逐行对源卡 `frozen_band_raw_record.json`）**未做**；
   我只抽验了源卡侧的 `21.593`、`band-logon-cpu8` 与 `H5` 措辞。
4. **`harness/tside_probe.py` dir-mode shim 的中立性**、**`%TEMP%` basetemp 落点偏差**（addendum-A §A3）、
   **H 地板 2.0 在"能真正跑到看门狗"的会话里的分布**（open question 3）—— 实现者已列为
   `open_questions_for_reviewer`，**我未裁**（属晋升/验收期需在有效环境下复看的项）。
5. `harness/manual_supervisor_probe.py` 的"2/2 launcher_exception"**我没有原样复跑**
   （会向 attempt 目录写入；改由 §1 的自有探针 + 18/18 事件文件等价覆盖）。
6. `handoff.deliverables` 28 项我按 `bytes/sha256` **全部核过（0 问题）**，但**未**逐个打开阅读
   `harness/run_band.py`、`write_handoff.py` 等驱动实现的正确性。

---

## 10. 边界声明（我做了什么 / 没做什么）

**我做过的写入（共 4 处，均在允许面内）**：
- 本 attempt 内**仅**新建 `reviewer_report.md`、`reviewer_report.sha256`；
- `%TEMP%` 内：`i14e_reviewer_openprocess_probe.py`、`i14e_reviewer_handle_probe.ps1`、
  `i14e_reviewer_manifest_recompute.py`、以及做 `git apply --check` 的一次性隔离副本
  `i14e-rev-c2006867\`（`git init` 只作用于该临时副本）。

**我没有做（逐条对照硬纪律）**：
1. **未改本 attempt 任何既有字节**（`handoff.json`、status、`review.md` 结论栏、oracle、三臂证据、源卡
   `I-14-E/a20260919-01` 全部原样；源卡最新 mtime 仍为 2026-09-22 09:59:08）。
2. **未做任何 git 写操作**；**未执行 `git status`**；用过的 git 全部只读：
   `diff HEAD --name-only`（工作区仓 + 真仓）、`rev-parse`、`ls-files --others --exclude-standard`（只读列未跟踪，
   与 `status` 同类但非该命令 —— 主动披露）、`apply --check`/`apply`（**只在 `%TEMP%` 临时副本**）。
3. **未联网**（无任何 web/下载动作）。
4. **未解除任何 BLOCKED、未签 ACCEPT、未代实现者落定、未改任何卡 status/字节、未晋升 `changes.diff`。**
5. **未重跑红/绿/变异三臂，未造任何绿色样例**（沙箱/权限不可用 ⇒ 如实记"未验证"，未反复硬试：
   探针类命令各跑 1 次即止，远低于 3 次上限）。
6. 结束前自证：`git -c core.quotepath=false diff HEAD --name-only` → 3826 条**全在 `.planning/`**，
   **非 `.planning` = 0**。

**复审人**：独立复审工位（I-14-E-TESTSIDE / a20260924-01）
**结论行**：`VERDICT: blocked`（环境阻断属实、交付 fail-closed 无造假；解除条件见 §8，须 owner/派工侧解环境）
