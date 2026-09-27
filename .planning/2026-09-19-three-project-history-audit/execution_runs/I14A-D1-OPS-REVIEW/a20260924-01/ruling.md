# I14A-D1-OPS-REVIEW — 独立运维 / SLO reviewer 裁定书（ruling.md）

| 项 | 值 |
|---|---|
| 卡 | `I-14-A`（性能测量先验证失败分支） |
| 被审 attempt（只读封盘） | `.planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/` |
| 本裁定 attempt（唯一写入面） | `.planning/2026-09-19-three-project-history-audit/execution_runs/I14A-D1-OPS-REVIEW/a20260924-01/` |
| 角色 | `independent_ops_slo_reviewer`（独立运维/SLO reviewer） |
| 授权 | `OWNER_DECISIONS.md` §十 L126 + §十一 L143 |
| 探针作者？ | **否**（本人为编排层新建 subagent，未参与 `iso/slo_probe_patched.py` 的任何编写/修改） |
| 实测时间窗（UTC） | 2026-09-24T20:14Z → 20:50Z（`evidence/boundary_checks.txt:captured_utc`） |
| D1 | **RULING（逐项冻结，含 1 项 OPEN ITEM）** |
| D2 | **NOT CONFIRMED as written（骨架确认，2 处原文主张被实测推翻，须追加式更正后复签）** |
| D3 | **未代签 — 仍 `awaiting I-16`**（见 §7） |
| 晋升禁令 | **继续有效**（本裁定**不**解除） |

---

## 1. 身份与授权引用（原文逐字）

### 1.1 被指派事实

本人是编排层按 owner 授权创建的**新 subagent**，与 `iso/slo_probe_patched.py` 无任何作者关系，
因此满足 `OWNER_DECISIONS.md` 与卡内对 D1 签署人的资格要求（「D1 必须由**非本探针作者**签」）。

### 1.2 授权原文（逐字，附行号）

- `OWNER_DECISIONS.md` **L116**（§十 · Owner 签字原话）：
  > 「16 照建议；W05-1 A；W05-2 A；W06-1 A；M08 三步照办；I-04-D R2-3 选 LIMITATION；**I-14-A D1/D2 指派运维与 SLO owner**；I-11-A OPEN-2/3/5/6 指派会计+行业 reviewer；新立卡全部照建议开；I-08-B CONFLICT、I-00-B 追认、三条口径确认：同意。」

- `OWNER_DECISIONS.md` **L126**（执行行）：
  > 「**I-14-A D1/D2** | **指派**：运维 owner 签 D1、SLO/探针 owner 签 D2 | 编排层按此派单（**D1 必须由非本探针作者签**）；未签前 `iso/slo_probe_patched.py` **不得**进 `RF/tools/`」

- `OWNER_DECISIONS.md` **L143**（§十一 · 第二批，第 1 项）：
  > 「1 | I-14-A D1/D2 | **派新 subagent** 当独立运维/SLO reviewer | 编排层创建独立 reviewer subagent（**D1 必须非本探针作者**）」

### 1.3 卡文原文（本人据以确定裁定范围，非据转述）

`execution_v2/card_I-14-A.md`：

- **L9（clause 2）**：「三个固定进程夹具：exit7且stdout似成功；exit0但业务结果失败；进程存活时分配可测内存后退出。前两者必须判业务测量失败，第三者需有PID匹配的存活期间样本，未采到不能记峰值0。」
- **L10（clause 3，D1 的直接依据）**：「**单独冻结采样间隔、平台可用的 peak 方式和测量误差规则，由运维 reviewer 决定；不把合成内存量等同精确 RSS oracle。**」
- **L11（clause 4）**：「保持现有 exact/latest/bundle p95=5秒与peak_rss_gb=2的预算约束，改预算需独立理由，不随测量失败改阈值。」
- **L12（clause 5）**：「成功延迟分布与失败率分开报告；不丢失败请求来宣称服务满足SLO。卡通过仅证明测量器，生产SLO需I-16实际测量。」
- **L13（clause 6，D2 的直接依据）**：「`--catalog`只检查存在，实际resolve使用config；`bundle=exact[:]`是代理计时。**绑定catalog与config不一致必须拒绝或证实实际目标一致**；测真实bundle消费路径，不能以复制exact延迟授予bundle资格。」
- **L15（退出/恢复）**：「三种夹具行为正确；命令总耗时/业务延迟/采样窗口分别记录。恢复：回退测量器隔离差异，不碰生产服务。」

`execution_runs/I-14-A/a20260919-01/decision.md`：

- **L11-13**：`D1 … UNSIGNED — blocks promotion` / `D2 … implemented, awaiting owner confirmation` / `D3 … implemented, awaiting I-16`
- **L15-17**：「Card clause 3 requires the ops reviewer to freeze the sampling interval, the platform-available peak method and the measurement-error rule. The implementer implemented one option, records why, and does **not** self-accept it.」

`execution_runs/I-14-A/a20260919-01/review.md`：

- **L3-6**：「The independent reviewer must re-derive at least one oracle value, **re-run the counterexamples against both tools, and decide D1 (and confirm D2/D3)**.」
- **L348-353**：「**D1/D2/D3 remain unsigned** … and the promotion prohibition stands: `iso/slo_probe_patched.py` must not enter `RF/tools/` until D1 is signed, and before I-16's production measurement a bundle measurement file must be supplied or the default invocation exits 2.」

---

## 2. 范围（裁 / 确认 / 不裁）

| 决定 | 归属 | 本次动作 |
|---|---|---|
| **D1** — 采样间隔、平台可用 peak 方式、测量误差规则 | 运维 reviewer（非探针作者） | **裁定**（逐项，§5） |
| **D2** — `catalog_dir` vs `--catalog` 绑定规则 + parser 已知限制 | SLO/探针 owner | **确认或不确认**（§6） |
| **D3** — bundle 计量要求（改变默认退出语义） | **I-16** | **只报告状态，不代签**（§7） |
| 晋升 `iso/slo_probe_patched.py` → `RF/tools/` | 编排层/后续门 | **不执行、不解除**（§9） |
| 卡状态、I-14-A 任何字段 | 编排层 | **不回写**（§9） |
| 预算阈值（clause 4） | — | **不动**（实测 `BUDGETS` 未变，§4） |

**"both tools" 的界定（按卡文与 attempt 原文，非按转述）**：`review.md:5-6` 的 "both tools" 指

1. **隔离补丁版**：`execution_runs/I-14-A/a20260919-01/iso/slo_probe_patched.py`
   （sha256 `14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e`，与 `review.md:131-132` 记录一致，本人复算一致）；
2. **未修改的产品版**：`iso/tool_prod/slo_probe.py`（sha256 `f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059`）＝ 卡锚点 `RF/tools/slo_probe.py`。
   **补充实测**：产品工作树 `tools/slo_probe.py` 的 sha256 是 `0c9d4a2d911b906ed92dbf31d0f66600d7ad865e4b0021a2bbe0fbd3c0616f86`（5680 B，无 CR），
   attempt 副本是 5822 B（含 142 个 CR）；**去掉 CR 后逐字节相等**，且 `git hash-object tools/slo_probe.py == git rev-parse HEAD:tools/slo_probe.py == 413aad5f788732520ace76acbaebcf06633f34d5`
   ⇒ 两者内容同一、仅行尾不同；卡的 RED 基线成立（此差异记录在 `evidence/boundary_checks.txt` 与 §8）。

**"counterexamples" 的界定**：`oracle.md:79-92`（§4 冻结反例）＝ **E1a / E1b / E1c / E2 / E3 / E4 / E4b / E5 / E6 / E7（含 E7b bundle 对照）**；
本人**按卡文原文**执行，未按转述删减。

---

## 3. 实测方法与隔离

- `fixture_spec.ensure_fixture_root()` 会 **unlink 并重建** `iso/fixture_root/**`（`harness/fixture_spec.py:162-204`），
  直接对封盘 attempt 复跑会改写既有文件 ⇒ **本次把 `harness/`、`iso/fixtures/`、`iso/tool_prod/`、`iso/slo_probe_patched.py`、`iso/venv/`、`iso/company-wiki/`、`company-wiki/` 复制到本人 attempt 下复跑**，
  复制品 sha256 与源逐件相等（`evidence/copied_inputs_sha256.json`，11/11 identical）。
- 本人 attempt 的 fixture_root 由本人的副本创建；**封盘 attempt 一个字节未改**（`git status --porcelain -- execution_runs/I-14-A` ⇒ 空，见 §9）。
- 所有 JSON 写后重解析；UTF-8 无 BOM、LF（`provenance.json` 内附校验）。

---

## 4. counterexamples 实测表（raw rc 为实际观测值）

### 4.1 隔离补丁版 `iso/slo_probe_patched.py`（`evidence/cases_patched_stdout.json`）

| 反例 | 冻结期望 rc | **实测 raw rc** | 期望的业务结果 | 结果 |
|---|---|---|---|---|
| E0-baseline-F4 | 2 | **2** | 快子进程仍被采样、`live_sample` | 见 §4.3（身份断言红） |
| E1a-F1 exit7+成功形 stdout | 4 | **4** | `calls.failed=6`, `failed_kinds={subprocess_rc:6}` | all_ok |
| E1b-F2 exit0+业务失败 | 4 | **4** | `calls.failed=6`, `failed_kinds={business_status:6}` | all_ok |
| E1c-F3 存活分配 | 2 | **2** | `peak 0.267`, `live_sample`, `count_min≥10`, fixture pid 在样本中 | all_ok |
| E2-F3 `--rss-sampler none` | 2 | **2** | `peak=null`, `sampler_disabled`, `peak RSS not measured` breach | all_ok |
| E3-F4 瞬时退出 | 2 | **2** | 仍被采到、`live_sample` | all_ok |
| E7-F4 无 bundle 计量 | 2 | **2** | `bundle.measured=false`, `basis=unmeasured`, bundle breach | all_ok |
| E4 catalog/config 不一致 | 3 | **3** | `error=catalog_config_mismatch`、**0** 次 resolve | all_ok |
| E4b 一致绑定 | 2 | **2** | `consistent=true`、6 次 resolve | all_ok |
| E6 冻结常量/百分位 | 0 | **0** | `BUDGETS` 四项 = 5/5/5/2 | all_ok |

runner 汇总 `all_ok=true`，**runner rc = 0**（耗时 29.8 s）。

### 4.2 未修改产品版 `iso/tool_prod/slo_probe.py`

| 项 | 实测 | 说明 |
|---|---|---|
| 同一 runner（`evidence/cases_prod_stdout.json`） | **runner rc = 1**；10 例中 9 例红 | 产品版不接受 `--resolve-cmd/--resolve-cwd` ⇒ 每例 argparse 拒绝，**raw rc = 2**（stderr 见 `evidence/cases_prod/E1a-*/stderr.txt`）；唯一绿的是 E6（源内常量/百分位） |
| 冻结套件 pytest（`evidence/suite_prod_stdout.txt`） | **rc = 1；10 failed / 2 passed / 1 skipped** | 与 attempt 记录的 RED 基线一致（`review.md:54`） |
| **E5（产品版自身解析路径）** `evidence/e5_prod_baseline/` | **raw rc = 0，`breaches: []`** | 在 stand-in 解析根下**所有子进程失败**，旧工具仍给出绿灯；`bundle_proxy` 与 `exact` 数值**完全相同**（p95 `0.1447072000000844`）＝字面别名；`peak_rss_gb 0.023`（探针自身）；stderr 出现 **6× `UnicodeDecodeError`**（`subprocess._readerthread`），复现 `F-I14A-02`（`review.md:118`） |

> 首次 E5 调用因缺 stand-in 根目录失败（`NotADirectoryError: WinError 267`，raw rc = 1，
> 原始 stderr 保留于 `evidence/e5_prod_baseline_run1_missing_root/`）；补齐 `<attempt>/company-wiki` 副本后复跑如上。**未以推断代替实测。**

### 4.3 冻结套件（补丁版）+ 反例复跑 —— **发现的红**

| 运行 | rc | 结果 |
|---|---|---|
| `evidence/suite_patched_stdout.txt` | **1** | **11 passed / 1 failed / 1 skipped**；失败项＝`test_frozen_case[E0-baseline-F4]`，失败断言＝**`fixture_pid_is_in_samples`** |
| E0 单例复跑 ×5（`evidence/e0_repeat/run1..5`） | runner rc **1×5** | **5/5 红**，且**只有** `fixture_pid_is_in_samples` 红；探针本身 raw rc 每次 = 2 |
| 合计 | — | 本会话 E0 身份断言：**6 红 / 1 绿**（唯一绿＝`--all` 首跑）；封盘 attempt 当时是绿（`I-14-A/a20260919-01/after/E0-baseline-F4/verdict.json` `all_ok=true`） |

失败机理（读报告可核）：E0 失败样本里 `rss_sampled_pids` 只含 **Popen 启动器 pid**，
fixture 自报 `os.getpid()`（如 `11228`）不在其中——Python 3.13 venv `python.exe` 是启动器，
真实解释器是其**后代**；F4 生命周期短于实测采样间隔 ⇒ 首样（spawn 时刻）只看到启动器，`sample_now` 触发时子进程已退出。
**这是"短于采样节拍的子进程可能完全不被观测到"的实测反例**（`evidence/suite_patched_out/E0-baseline-F4/verdict.json`、`evidence/e0_repeat/run*/`）。

### 4.4 其余自跑证据

| 证据 | 文件 | 结果 |
|---|---|---|
| 冻结套件（补丁版） | `evidence/suite_patched_stdout.txt` | 见上 |
| bundle 对照 E7b | `evidence/bundle_control_stdout.json` | **rc = 0**，`pass1=2 / pass2a-copied=0 / pass2b-independent=0`；`production_tool_aliases_bundle_to_exact=true`、`patched_tool_has_no_bundle_alias=true`、`pass1_bundle_unmeasured=true` |
| 独立重算 oracle（攻击点 #1） | `evidence/recompute_p95.py`, `oracle_recompute_E1c.json`, `oracle_recompute_E0.json` | 两次 **rc = 0**：exact p95/p50、latest p95 全部与探针报告相等（E1c exact p95 `2.146402`；E0 `0.126284`）；`budgets` 四项未动 |
| 攻击点 #3（样本在子进程存活期内） | `evidence/e1c_samples_inside_life.json` | 6/6：fixture pid ∈ `rss_sampled_pids`、window ≤ elapsed、`peak_sample_age` < elapsed；**实测节拍 64.0–75.2 ms**（n=26–29 / 1.70–2.06 s） |
| D1 峰值方法三选一实验 | `evidence/d1_peak_method_experiment.py` / `.json` | 见 §5.2 |
| D2 绑定/parser 矩阵（11 行） | `evidence/d2_binding_matrix.py` / `.json` | 见 §6 |

**与 attempt 记录的偏差（如实登记，不回改）**：
- `commands.json:115` 记 `pass2a-copied = 2`，但 attempt 自己留存的 `harness/scratch/suite-final2/bundle-control/pass2a-copied/raw_returncode.txt = 0`，本次复跑亦为 **0** ⇒ 以留存原始文件与本次实测为准，`commands.json` 该行疑似早期运行残留。
- attempt 的 E7b 期望只要求 `basis ∈ {independent, copied_exact}`，两次运行均满足，**不影响 E7 判定**。

### 4.5 本沙箱不可跑 / NOT-RUN 项

| 项 | 状态 | 原因 |
|---|---|---|
| 生产 catalog 上的真实 quick_check 分钟级行为 | **NOT-RUN**（与 attempt 一致） | 属生产负载，卡内明确不做（`review.md:95-97`）；本次亦未打开任何生产 catalog |
| 真实 bundle 消费路径时延 | **NOT-RUN** | 属 I-16 生产测量（§7）；本沙箱无生产入口 |
| 生产 SLO 结论 | **NOT-RUN / 不在范围** | 卡通过只证明测量器（clause 5, `oracle.md` M9） |

---

## 5. D1 裁定 —— 逐项冻结

> 总裁定：**D1 = RULING（逐项冻结）**，同时附 **1 项阻塞卡片验收的 OPEN ITEM**（§5.1 反例 c）。
> 本裁定**不宣布 I-14-A 通过**，**不解除晋升禁令**。

### 5.1 D1-1 采样间隔：冻结为 **标称 50 ms 固定间隔**，并冻结其**有效节拍与适用域**

**(a) 裁定**
- 冻结值：`RSS_SAMPLE_INTERVAL_SECONDS = 0.05`（`iso/slo_probe_patched.py:76`），**固定、不可按用例调节**。
- 同时冻结三条限定（缺一不可，作为签署条款）：
  1. **50 ms 是标称值**；本机实测**有效节拍 64.0–75.2 ms/样**（`evidence/e1c_samples_inside_life.json`），因此**任何精度主张以报告里的 `rss_sample_count` / `rss_sample_window_seconds` 为准，不以常量为准**。
  2. **适用域**：存活 ≥ 约 2×有效节拍（≈150 ms）的进程，PID 身份可保证（F3：6/6 调用 fixture pid 在样本中；本人独立实验 30/30 采样含 fixture pid）。
  3. **短于有效节拍的子进程可能完全不被观测到**；此时报告中的峰值只能按 §5.3 的归属规则读作"启动器归属"，**不得**当作被测程序 RSS。

**(b) 依据（本地可核）**
- `iso/slo_probe_patched.py:76`（常量）、`:188-213`（`RssSampler(interval=…)`、spawn 后立即首样）、`:215-222`（`sample_now`）、`:249-254`（`_tick.wait(interval)` 循环）。
- 实测：`evidence/cases_patched/E1c-*/report.json`（6 调用，count 26–29，window 1.70–2.06 s）；`evidence/d1_peak_method_experiment.json`（32 样 / ~1.7 s，fixture pid 30 样）。
- `oracle.md:124-126`：E1c 采样数下限由 1 提到 10（**收紧**），与本次实测（≥26）不冲突。

**(c) 反例（如实登记）**
- **E0 `fixture_pid_is_in_samples` 本会话 6 红 1 绿**（§4.3）⇒ 冻结的 E0 期望与 50 ms 节拍在短命子进程上**不相容**。
- 结论：**OPEN ITEM（阻塞"三种夹具行为正确"这一退出条件，因而阻塞卡片验收）**，二选一由实现者执行并追加式登记：
  (i) 追加式更正 `fixture_spec`/`oracle` 中 F4 的身份断言（限定到"存活 ≥ 2×有效节拍"的夹具），或
  (ii) 增加 spawn/exit 时刻的确定性采样（使短命子进程的身份可证）。
  **本人不修改封盘 attempt，故只登记、不代改。**

**(d) 兼容影响**
- 不改预算（clause 4）：`BUDGETS` 在每次报告中均 `{"exact_p95":5.0,"latest_p95":5.0,"bundle_p95":5.0,"peak_rss_gb":2.0}`（`evidence/oracle_recompute_*.json: budgets_untouched=true`；源 `:50-55` 与 `iso/tool_prod/slo_probe.py:30-35` 逐字相同）。
- 报告字段、退出码 0/1/2 语义不变；3/4 为新增（`oracle.md:94-105`）。
- 对生产（p95 预算 5 s）：≥ 约 60–100 样/调用，节拍误差对 p95 判定无实质影响；**风险集中在 <150 ms 的快速调用**。

**(e) 恢复规则（追加式，不回改）**
- 改间隔 ⇒ 必须同时给出**新的独立理由 + 新 oracle**（沿用 `decision.md:71-72` 的变更控制），且**不得**为让预算通过而改（clause 4）。
- 回退＝把常量恢复为前值；探针无状态、只写 `--report`，回退不触碰任何产品路径（`decision.md:80-81`）。

### 5.2 D1-2 平台可用 peak 方式：冻结为 **选项 2 —— 固定间隔活采 `rss`，峰值＝进程树求和的最大值**；拒绝选项 1 与选项 3

**(a) 裁定**：采用 `decision.md:46` 已实现的**选项 2**；**选项 1（`peak_wset`）与选项 3（私有 ctypes `GetProcessMemoryInfo`）均不采用**。

**(b) 依据（本人独立实测，非转述实现者理由）** — `evidence/d1_peak_method_experiment.json`
| 观测 | 值 |
|---|---|
| 选项 2：树求和峰值 | **0.2674 GB** |
| 选项 1：`peak_wset` 最大 | **0.2634 GB** |
| 选项 3：ctypes `PeakWorkingSetSize` 最大 | **0.2634 GB** |
| 差值来源 | 树求和含启动器 RSS 4.059 MB ⇒ 0.2674 − 0.2634 ≈ 0.004 GB（与 `decision.md:28-30` 记录的"树求和是保守高估"一致） |
| 选项 1 vs 选项 3 配对比较 | 61 对中 **59 对完全相等**，2 对差 **−65536 B**（读取时序，非不同计数器） |
| 选项 1 单调性 | `option1_peak_wset_monotone_nondecreasing = true`（**生命周期单调**，无法归属到采样窗口） |
| 进程退出后读数 | psutil ⇒ **`NoSuchProcess`**（值不可再取）；ctypes ⇒ 返回 4743168 B（**对已退出 pid 仍可能读到数**，疑似 PID 复用，**归属不安全**） |
| `popen_pid` vs fixture pid | 19024 vs 3236（**不等**），再次复现 `oracle.md:109-115` 的 R1-erratum ⇒ 必须走进程树 |

外部佐证（2 条，`provenance.json` 记 URL/UTC/引文/快照 sha）：
- **Microsoft Learn — PROCESS_MEMORY_COUNTERS**：`PeakWorkingSetSize` ＝ "The peak working set size, in bytes."（**无窗口语义**，是进程级峰值计数器）。
- **psutil `_pswindows.py`**：`memory_info()` 的注释 "Underlying C function returns fields of PROCESS_MEMORY_COUNTERS struct."，且 `"peak_wset": d["PeakWorkingSetSize"]` ＝ `peak_rss=d["PeakWorkingSetSize"]` ⇒ **选项 3 读的就是选项 1 的同一个计数器**，新增一条未经审计的私有系统调用路径**不带来任何新信息**。

**(c) 反例（针对 `decision.md` 自己的论据，登记为论据更正）**
- `decision.md:48-50` 称选项 1/3「includes the interpreter start-up spike」——**本次未复现**：首样 `peak_wset` 与 `rss` 之差 **0.0 MB**，两个 pid 的 `max(peak_wset)` 与 `max(rss)` 之差均 **0.0 MB**（F3 的 256 MB 平台期主导）。
- 因此：**"启动器启动尖峰"这一论据在本机标为 `basis=professional_judgement（未复现）`**；**真正支撑选项 2 的实测理由**是 ①窗口归属 vs 生命周期单调、②退出后不可读/读数歧义、③单进程 vs 进程树、④选项 3 ≡ 选项 1。
- 该更正**不改变裁定结论**（仍选选项 2），但**必须随本裁定一并登记**，不得再以"启动尖峰"作为已证事实引用。

**(d) 兼容影响**
- 报告结构不变：`peak_rss_gb / peak_rss_source / rss_sampled_pids / rss_sample_count* / peak_pid / peak_tree_pids / peak_sample_age_seconds`（源 `:256-279`, `:578-601`）。
- `peak_pid` 仅在样本只覆盖 1 个 pid 时有值，否则 `null` 且由 `peak_tree_pids` 承载 —— 实测 E1c **6/6 调用 `peak_pid = null`、`peak_tree_pids = [启动器, fixture]`**，与 `decision.md:29-30`、`oracle.md:232-233` 一致。
- 树求和的**保守高估**量：本人实测 +4.059 MB；attempt 实测 ≈11 MB（`decision.md:28-30`）⇒ 结论一致，量级随负载浮动，**不得**当作精确 oracle（clause 3 / M7）。
- 未来风险（ops 关注）：psutil 已把 `peak_wset` 放进 `_deprecated`（外部源 2），8.0 有破坏性变更 —— **选项 2 用的是 `rss`，不受该弃名影响**（这是选选项 2 的附加运维理由）。

**(e) 恢复规则**
- 探针只读、无状态、只写 `--report`；回退＝恢复先前 `tools/slo_probe.py`（`decision.md:80-81`），不触碰生产服务与产品路径。
- 若要改回选项 1/3 ⇒ 属"peak 方式变更"，须新独立理由 + 新 oracle，且**不得**用于让预算通过。

### 5.3 D1-3 测量误差规则：冻结为 `decision.md:59-72` 提议的规则（**予以接受**），并追加一条归属限定

**(a) 裁定 —— 接受并冻结下列 5 条**
1. 采样间隔 50 ms 固定（见 §5.1，含其三条限定）。
2. `rss_sample_count == 0` ⇒ `peak_rss_gb: null` + `peak_rss_source: "uncollected:…"/"sampler_disabled"` + 显式 breach「`peak RSS not measured (…) — an unmeasured RSS can never be reported as within budget`」；**永不 0.0、永不绿**。
3. 峰值只归属于 `peak_tree_pids` 所列 pid；采样 pid 集**不含被测程序 pid** 时，该读数**只能读作启动器归属，不得当作被测程序 RSS**（本次新增条款，源自 §4.3 反例）。
4. 合成分配量只作**数量级**比较，**不作精确 RSS oracle**（clause 3 / `oracle.md:59-61`, `:235-237`）。
5. 变更控制：间隔/peak 方式/误差规则的改动**必须**有新的独立理由 + 新 oracle，**不得**为使预算通过而改。

**(b) 依据（实测）**
- E2：`evidence/cases_patched/E2-*/report.json` —— `peak_rss_gb=null`、`peak_rss_source=sampler_disabled`、`breaches` 含该 RSS 条目、raw rc **2**（`iso/slo_probe_patched.py:634-636` 生成 breach，`:660` `return 2 if breaches else 0`）。
- 攻击点 #4（"让无样本分支读成绿"）：RSS breach 在报告中**独立存在**，且**仅凭它**即可强制 exit 2（源码路径如上）。
- 攻击点 #3：样本全部落在存活期内（§4.4，6/6）。
- 合成量对照：fixture 自报 `allocated_mb=256` → 树求和峰值 0.2674 GB（≈274 MB，含 4 MB 启动器）⇒ **只作数量级对照**（M7）。

**(c) 反例 / 残留（登记，不粉饰）**
- **退出码归因未被隔离**：本次 E2 的 `breaches` 同时含 bundle 条目，故"rc=2 仅因 RSS"无法从退出码单独证明；已由 breach 文本 + 源码路径证明 RSS 维度独立致红。**残留＝若要更强证据，需要一次除 RSS 外全绿的对照运行，本次未做（NOT-RUN，原因：补丁版无 bundle 计量时 bundle 必红，见 F-I14A-01）。**
- **归属盲区**：探针本身**不**在 `rss_sampled_pids` 缺少被测 pid 时把 `peak_rss_source` 降级为 uncollected（E0 实测仍标 `live_sample`）⇒ 条款 3 目前**靠报告携带 pid 集 + 复核者判读**实现，尚无机器强制。此为**已登记的限制**，纳入 §5.1 OPEN ITEM 的同一处置（更正期望或补确定性采样）。

**(d) 兼容影响**
- 退出码 0/1/2 语义不变；3（绑定拒绝）/4（测量失败）为新增且为卡核心要求（`oracle.md:104-105`）。
- F-I14A-01（`decision.md:31-35`）已实测确认：**任何未带 `--bundle-measurement` 的调用都会 exit 2**（E0/E1c/E2/E3/E7 实测 rc 均 2，`breaches` 均含 bundle 条目；源 `:628-629`, `:660`）。**签署即代表接受"默认调用永不绿"是有意行为，不是探针坏了。**
- F-I14A-02（`decision.md:36-38`）已实测确认：产品版 stderr 6× `UnicodeDecodeError`、rc 对它不可观测 ⇒ 接受"rc unobservable / unobserved"的降级表述，**不**接受"每个子进程都失败"的强断言。

**(e) 恢复规则**
- 误差规则的任一条被改 ⇒ 追加式更正 + 新 oracle；**不回改** `oracle.md` §1–§8、`decision.md`、`review.md` 任何历史字节。
- 回退测量器＝恢复先前 `tools/slo_probe.py`，隔离差异，不碰生产服务（卡 L15）。

### 5.4 D1 签署状态登记（只登记在本载体）

- **D1 = SIGNED（本裁定即签署），签署人＝本人（独立运维 reviewer，非探针作者）**，
  签署范围**仅限** §5.1–§5.3 冻结的三项及其条款；签署**附带**：
  - §5.1(c) OPEN ITEM 未关闭前，**卡片退出条件"三种夹具行为正确"不得判定通过**；
  - 本签署**不解除** `iso/slo_probe_patched.py` 的晋升禁令（禁令由 D3/I-16 继续持有，见 §7/§9）。

---

## 6. D2 确认 —— **NOT CONFIRMED as written**（安全属性已实测确认；两处原文主张被推翻）

**(确认范围)** `decision.md:83-106`（绑定规则 + parser 已知限制）+ `review.md:85-87`。

### 6.1 已确认（实测，`evidence/d2_binding_matrix.json`，11 行矩阵）

| 性质 | 实测 |
|---|---|
| 一致绑定被接受（quoted / bare / `${PROJECT_ROOT}` 展开 / `catalog.db` 名） | **rc = 2**，`consistent=true`，**6** 次 resolve 真实执行（4 行全绿） |
| 目录不一致 ⇒ 拒绝 | **rc = 3**，`error=catalog_config_mismatch`，**0** 次 resolve |
| 同目录但文件名不在白名单（`weird_name.sqlite3`）⇒ 拒绝 | **rc = 3**，0 次 resolve |
| 产品真实配置形态 `catalog_dir: "${PROJECT_ROOT}/.source_catalog"` | **可解析并接受**（`project_root_expansion` 行 rc=2；出处 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml:2`） |
| block scalar / anchor ⇒ 拒绝（fail-closed） | **rc = 3**，`configured_catalog_dir` 分别为 `"|"` / `"&anchor …"`，0 次 resolve |
| 残余 `${…}` / 缺 `catalog_dir` 键 ⇒ 拒绝 | **rc = 3**，`binding.error = config_unreadable_by_probe_parser`，`detail` 分别为 `unresolved variable in catalog_dir: …` / `catalog_dir not found in …` |
| E4 / E4b 冻结反例复跑 | **rc 3 / 2**，`all_ok=true`（§4.1） |

**读法更正（非缺陷）**：顶层 `error` **恒为** `catalog_config_mismatch`（源 `:522`），parser 具体原因在 `binding.error` / `binding.detail`（源 `:160-164`）。引用 D2 时必须引用 `binding.*`，不能引顶层 `error`。

### 6.2 按原文**不成立**的两处（⇒ as written 不确认）

1. **`catalog.db` 白名单的论据不成立。**
   - 原文：`decision.md:89-92`「the product's config uses the former and **`RF/tools/release_readiness.py` the latter**（`catalog.db`）」。
   - 实测：`tools/release_readiness.py:37` ＝ `CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"`；
     对 `tools/*.py` 全量检索 `.db` / `catalog.db` ⇒ **0 命中**；全工作树（除 `.planning`、`.review-*`）仅 2 处历史文档命中（`assurance/runs/2026-09-11_r4-phase-b/reviews/G5-boundary-observation.json:53`、`audit_review/2026-08-12_zijin_skill_run_audit/progress.md:91`），**均非产品代码**。
   - 后果（clause 6 风险）：`--catalog <dir>/catalog.db` 会被判 `consistent=true` 并执行 6 次 resolve，而解析器按 config 打开的是 `catalog.sqlite3` ⇒ **"证实实际目标一致"对 `catalog.db` 这一名称并未达成**（实测行 `catalog_db_name_consistent` rc=2）。
2. **parser 已知限制清单多写了"inline `#` comments"。**
   - 原文：`decision.md:95-99` / `oracle.md:219-224`「a quoted or bare scalar, `${…}` expansion, **inline `#` comments**」。
   - 实测：`catalog_dir: "<dir>"  # inline comment` ⇒ **rc = 3 被拒**，`configured_catalog_dir` 保留字面引号（`"\"C:\\…\\catalog\""`），因 `_strip_scalar`（`iso/slo_probe_patched.py:82-88`）在"引号分支"里不会再剥注释。
   - 性质：**fail-closed（拒绝而非猜测）**，方向安全；但**原文能力声明不准确**，且意味着"带行内注释的引号配置"会被**误拒**（生产上表现为探针拒测、exit 3）。
   - 影响面：本人检索到的**真实配置不带行内注释**（§6.1），故当前生产形态不受影响。

### 6.3 D2 结论

**`confirmation_D2 = "not_confirmed_as_written"`** —— 理由：§6.1 的安全属性（拒绝不一致、拒绝即零测量、fail-closed、两种已知文件名规则的接受路径）**已被实测确认**；
但 §6.2 两处**原文主张与产品树/实测矛盾**，其中第 1 处直接触及 clause 6 的"必须拒绝**或**证实实际目标一致"。
**恢复规则（追加式）**：由实现者/SLO owner 在 `decision.md` D2 与 `oracle.md` §9.3 追加更正（删除或限定 `catalog.db` 的论据、把"quoted+inline comment"列入已知限制），
或改代码把 `consistent` 收紧为"文件名必须等于 `configured_catalog_file`"；**更正与复签均追加式，不回改本卡历史字节**。

---

## 7. D3 状态（**不代签**）

**(a) 裁定**：**D3 未由本人签署**；状态维持 `implemented, awaiting I-16`（`decision.md:13`, `:108-110`）。

**(b) 依据（实测）**
- `execution_runs/` 下**不存在**任何 `I-16*` attempt（目录枚举为空）；`execution_v2/` 仅有 `card_I-16-A.md`、`card_I-16-B.md`，二者首行均标 **状态 planned**。
- `card_I-16-B.md` clause 3 正是「用 I-14 已验证测量器测业务失败率、时延和内存」⇒ bundle/生产计量**属 I-16，未开工**。
- 全工作树（排除 `.planning`）**未发现任何 bundle 计量文件**（`*bundle*.json` 检索 0 命中）；attempt 内只有两个**控制输入**（`bundle-copied-from-exact.json` / `bundle-independent.json`，由 `run_bundle_control.py:79-92` 生成，非生产计量）。
- 退出语义现状实测：无 `--bundle-measurement` ⇒ `bundle.measured=false`、`basis=unmeasured`、breach、**exit 2**（§4.1/§4.4）。

**(c) 结论（逐字）**：**D3 未签、bundle 计量文件仍缺、晋升禁令继续有效；本裁定不解除禁令。**
在 I-16 提供真实 bundle 消费时延之前，`iso/slo_probe_patched.py` **不得**进入 `RF/tools/`，且默认调用将恒 exit 2（F-I14A-01，已被本次实测确认）。

**(d)/(e)**：D3 若被 I-16 否决，回退路径见 `decision.md:125-127`（保留 `basis` 报告但回到旧退出语义）——**该回退本身需要新的独立理由**，本人不代裁。

---

## 8. provenance 摘要

### 8.1 本地可核依据（全部在本人 attempt 内，只读复算封盘 attempt）

| 类别 | 位置 |
|---|---|
| 复制品哈希对照 | `evidence/copied_inputs_sha256.json`（11/11 identical） |
| 反例原始输出 | `evidence/cases_patched/`、`evidence/cases_prod/`、`evidence/cases_*_stdout.json`、`evidence/suite_*_stdout.txt`、`evidence/bundle_control*`、`evidence/e5_prod_baseline*/`、`evidence/e0_repeat/` |
| oracle 独立重算 | `evidence/recompute_p95.py`、`oracle_recompute_E1c.json`、`oracle_recompute_E0.json`、`e1c_samples_inside_life.json` |
| D1 实验 | `evidence/d1_peak_method_experiment.py`、`d1_peak_method_experiment.json` |
| D2 矩阵 | `evidence/d2_binding_matrix.py`、`d2_binding_matrix.json`、`d2_configs/`、`d2_reports/`、`d2_binding_matrix_run1_mybug.json`（本人脚本首跑缺陷，如实保留） |
| 边界自证 | `evidence/boundary_checks.txt` |
| 结构化 provenance | `provenance.json`（含每条外部证据 URL / 取回 UTC / 原文引文 / 快照 sha256；本地证据 sha256 + 字节） |

### 8.2 外部来源（2 条；**不冒充本地可核事实**）

| # | URL | 取回 UTC | 用途 | 快照 |
|---|---|---|---|---|
| 1 | `https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters`（HTTP 200，页脚 "Last updated on 2024-02-22"） | 2026-09-24T20:48:29Z | 证明 `PeakWorkingSetSize` 是**进程级峰值计数器、无窗口语义** | `evidence/external_sources/msdn_PROCESS_MEMORY_COUNTERS.txt`（sha256 见 `provenance.json`） |
| 2 | `https://raw.githubusercontent.com/giampaolo/psutil/master/psutil/_pswindows.py`（HTTP 200） | 2026-09-24T20:48:29Z | 证明 psutil `peak_wset` ≡ `PeakWorkingSetSize` ⇒ **选项 3 ≡ 选项 1**；并提示 `peak_wset` 已入 `_deprecated` | `evidence/external_sources/psutil_pswindows_memory_info.txt`（sha256 见 `provenance.json`） |

> 两条外部来源仅用于**解释/佐证**；D1 的结论以本地实测（§5.2 表）为准，外部来源不承担任何本地事实。

---

## 9. 边界声明（自证）

| 边界 | 结果 | 证据 |
|---|---|---|
| 产品写入（非 `.planning`） | **0** | `git -c core.quotepath=false diff HEAD --name-only` ⇒ 捕获时刻共 3824 行，**非 `.planning` = 0**（`evidence/boundary_checks.txt`，含 `captured_utc`；`.planning` 行数由并行编排层写入而漂移，**非 `.planning` 计数为本裁定关心的不变量**） |
| `iso/slo_probe_patched.py` 拷入产品路径 | **0 次** | 全树检索该文件名在 `.planning` 之外 **0 命中**；`tools/` 下只有 `slo_probe.py` / `test_slo_probe.py`（及既有 .pyc） |
| git 写（add/commit/checkout/stash/restore/reset） | **0 次** | 本次仅执行只读 `git diff/status/hash-object/rev-parse` |
| 封盘 attempt `I-14-A` 改动 | **0** | `git status --porcelain -- execution_runs/I-14-A` ⇒ **空**；复跑全部在本人副本上执行 |
| 产品锚点 `tools/slo_probe.py` | 未改动 | `git hash-object == git rev-parse HEAD: == 413aad5f788732520ace76acbaebcf06633f34d5`；`git status --porcelain -- tools` ⇒ 空 |
| I-14-A 状态/字段回写 | **0** | D1/D2/D3 签署状态**只登记在本载体**（本文件 + `handoff.json`） |
| 预算改动 | **0** | 每份报告 `budgets` = 5/5/5/2（`evidence/oracle_recompute_*.json`） |
| 晋升 | **未执行** | 见 §7 |

---

## 10. 本人**没有做 / 不能做**的事（明确边界）

1. **未签 D3**（归属 I-16）；未对 bundle 计量做任何生产测量。
2. **未解除晋升禁令**：没有、也不会把 `iso/slo_probe_patched.py` 放进 `RF/tools/` 或任何产品路径。
3. **未回改** `execution_runs/I-14-A/` 与 `.planning` 之外的任何文件；**未**修改封盘 attempt 的 `oracle.md`/`decision.md`/`review.md`/`fixture_spec.py`（§5.1 OPEN ITEM 只登记、不代改）。
4. **未**执行 git 写操作；**未**声明 I-14-A 卡片验收通过（E0 红 ⇒ 退出条件未满足）。
5. **未**在生产 catalog / 真实解析链路上测量；`quick_check` 分钟级行为、真实 bundle 消费路径 = **NOT-RUN**（§4.5）。
6. **未**把任何外部网页内容当作本地事实；外部证据仅 2 条，且逐条落 `provenance.json`。
7. 本沙箱限制：审批提示已禁用，本人无权越出既定权限面；若后续需要在产品代码上做 §6.2 的收紧改动，须由编排层另开受控卡执行。

---

**Append-only 规则**：本裁定若需更正，只允许**新增**载体/追加段落；本文件既有字节不回改。
