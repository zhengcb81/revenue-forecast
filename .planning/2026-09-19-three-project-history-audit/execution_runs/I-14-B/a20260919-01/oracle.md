# I-14-B oracle（运行前冻结）

- card：I-14-B 自然时间与UI观察证据（parent I-14）
- attempt：`execution_runs/I-14-B/a20260919-01`
- 实现者：本 attempt 的实现者（模型）；独立 reviewer：**未指定，尚未审阅**
- **冻结时刻 `frozen_now = 2026-09-20T02:56:38Z`**（本机时区 GMT Standard Time +01:00，本地 2026-09-20 03:56:38）。见证：`evidence/freeze_instant.json`（sha256 见 `handoff.json`）。**任何晚于 `frozen_now` 的时间戳在本卡一律判为 future clock。**
- 本文件在**任何 case 运行之前**写成。`before/` 内的 RED 证据必须晚于本文件。
- 本卡**不修改生产代码**：`revenue-forecast`、`filing-fetch`、`company-wiki` 只读。全部写入限于本 attempt 目录。

## 0. 本卡授予与不授予

**授予（拟）：** 自然时间字段的**分列口径**与**重叠不相加**的计时/分类算法；合成时间输入下"观测 29 分钟而不是 37 分钟"的计算正确性；自然日/周/月需求ID到 I-17 待运行日历的映射；30/60/120 秒检查的**算法级**锚点/容差判据。

**明确不授予：**
1. **不授予真实自然观察资格。** 本 attempt 没有任何真实自然周期被观察完成；全部日历项保持 pending。
2. **不授予真实 UI 即时性资格。** 30/60/120 秒的真实检查在本 attempt 为 **blocked**（UI 捕获能力未具备，见 §6）。
3. **不授予 SLO/性能资格**（那是 I-14-A / I-16 的范围）。本卡**消费** I-14-A 的已冻结结论，不重新论证、不推翻：
   - bundle 未测量时恒 exit 2；rc 不可观测（旧工具无 per-call rc）；
   - tree-sum peak RSS 高估 ≈ 11 MB；`calls.failed`=6；catalog_dir 标量解析器限制；
   - `iso/slo_probe_patched.py` 因 **D1/D2/D3 未签**，**不得**进入 `RF/tools/`（本卡不复制、不提升）。
4. 本卡不改变 worker 的 `desired_state=paused`（`worker_control.json` 只读取 hash，不写）。

## 1. 输入字段（必须分列，不得合并）

窗口/观察记录的原始字段：

| 字段 | 含义 | 备注 |
|---|---|---|
| `scheduled_at` | 预定时间（计划窗口起点） | 可与 `started_at` 不等，差值单列 |
| `started_at` | 命令/阶段实际开始 | |
| `sampled_at[]` | **原始采样时间戳列表** | 观察时长的唯一合法来源 |
| `observation_finished_at` | 观察/采样阶段结束 | |
| `quick_check_started_at` / `quick_check_finished_at` | quick_check 自己的窗口 | **不属于观察窗** |
| `command_finished_at` | 整个命令结束 | |
| `windows[]` | 同一会话的多个子窗口 `{window_id, started_at, finished_at}` | 用于重叠判据 |
| `claim` | 被测主张 `{status, natural_observation_seconds, basis}` | `basis∈{sample_span, command_total, observation_plus_quick_check, sum_of_windows, union_of_windows}` |
| `ledger` | 自然日历账本 `{daily[],weekly[],monthly[],alerts[]}`，每条含 `run_id/started_at/ok/report_sha256` | |
| `clock_source` | 判定所用时钟来源 | 可信集 = `{system_utc, scheduler_trusted}` |
| `login_check` | `{anchor_event{event_id,anchor_at,source}, labels[{name,sampled_at,captured_at,evidence_kind,evidence_sha256}]}` | `evidence_kind=="live_ui_capture"` 才算即时捕获 |

### 派生量（SUT 必须输出，且分别标注）

- `observation_span_seconds = max(窗内 sampled_at) − min(窗内 sampled_at)`；**样本 <2 → `null`（未测量 ≠ 0）**
- `sample_count`
- `quick_check_seconds = quick_check_finished_at − quick_check_started_at`
- `command_total_seconds = command_finished_at − started_at`
- `union_seconds = |∪ windows|`（区间并集测度）
- `sum_seconds = Σ |window|`
- `overlap_seconds = sum_seconds − union_seconds`
- `schedule_lag_seconds = started_at − scheduled_at`

**禁止语义（写进输出、永不用作自然时长）：** `sum_seconds` 只在 `overlap_seconds>0` 时作为**反例诊断**出现，字段名固定 `forbidden_sum_seconds`；任何把它当作自然时长的判定必须被拒。

## 2. 冻结判据（每一条都要有可证伪的反例）

| 判据 | 语义 | 拒绝码 |
|---|---|---|
| J1 重叠不相加 | 多个重叠窗口的自然时长取**并集**；用 Σ 冒充 → 拒 | `R-SUM-OVERLAP` |
| J2 命令总耗时不是观察时长 | `basis=="command_total"` 且 `command_total>observation_span` → 拒 | `R-TOTAL-AS-OBS` |
| J3 quick_check 不进观察窗 | `basis=="observation_plus_quick_check"`，或 claimed==span+qc，或 claimed 落在与 quick_check 重叠处 → 拒 | `R-QC-IN-OBS` |
| J4 未测量不是 0 | 样本 <2 → span=`null`；申明 0 秒 → 拒 | `R-NO-SAMPLES` |
| J5 样本必须在窗内 | 任一 `sampled_at` 落在 `[started_at, observation_finished_at]` 之外 → 拒 | `R-SAMPLE-OUTSIDE` |
| J6 未来时钟 | 任一原始时间戳 > `frozen_now` → 拒 | `R-FUTURE-CLOCK` |
| J7 模拟时钟 | `clock_source ∉ {system_utc, scheduler_trusted}` → 拒（**即使账本本身合规**） | `R-SIMULATED-CLOCK` |
| J8 空证据 hash | 自然日历有效条目 `report_sha256` 为空 → 该条不计，且拒 | `R-EMPTY-EVIDENCE` |
| J9 重复 run_id | 同一窗口内 `run_id` 重复 → 只计首次，且拒 | `R-DUP-RUN-ID` |
| J10 同一瞬时≠连续 | 同一窗口内多个条目 `started_at` 完全相同 → 不构成"连续日"链，且拒 | `R-SAME-INSTANT` |
| J11 主张不得超过事实 | `claim.status=="complete"` 但计算为 pending/incomplete → 拒 | `R-CLAIM-EXCEEDS` |
| J12 登录锚点 | 标签 N 的 `|sampled_at −(anchor_at+N 秒)|>tol` → 拒 | `R-LABEL-ANCHOR` |
| J13 同一事件锚点 | 三个标签的 `anchor_event.event_id` 不全相同 → 拒 | `R-ANCHOR-NOT-SHARED` |
| J14 即时捕获 | `evidence_kind != "live_ui_capture"` 或 `captured_at − sampled_at > capture_tol` → 拒（事后日志不得造即时证据） | `R-POSTHOC-CAPTURE` |

链规则（自然日历，逐条固定）：daily 条目计入需 `ok==true` **且** run_id 在本窗口内唯一 **且** `report_sha256` 非空 **且** `started_at ≤ frozen_now` **且** 与上一条**UTC 日期不同**、间隔 `≤ 25 h`。最长连续链 `daily_count`；`daily_count ≥ 7` 才算 daily 窗完成。weekly：`ok` 且 hash 非空 且不晚于 `frozen_now` 且**不同周**且两两间隔 `≥ 7 d`，最新一条距判定时钟 `≤ 7 d`；计数 ≥2。monthly：`ok` 且 hash 非空 且不晚于 `frozen_now` 且距判定时钟 `≤ 35 d`；计数 ≥1。alert：`acked==true` 计数 ≥1。四窗全完成才 `status=="complete"`，否则 `pending`，**永不可豁免**。

## 3. 合成时间用例的 oracle（本卡 #2 的核心，手算）

**W1 输入（合成，仅验证计时算法）：** `scheduled_at=started_at=2026-09-19T00:00:00Z`，`sampled_at` = 00:00…00:29 每 60 s 共 30 个；`observation_finished_at=00:29:00Z`；`quick_check_started_at=00:29:00Z`、`quick_check_finished_at=00:37:00Z`；`command_finished_at=00:37:00Z`。

手算：00:00→00:29 = **1740 s = 29 min**；00:29→00:37 = **480 s = 8 min**；00:00→00:37 = **2220 s = 37 min**。

| 用例 | 主张 | 期望计算 | 期望判定 | 期望拒绝码 |
|---|---|---|---|---|
| W1 | eligible 1740 s，`sample_span` | span=1740，qc=480，total=2220，union=2220，overlap=0，count=30 | accept | — |
| W2 | eligible 2220 s，`command_total` | 同上 | **reject** | `R-TOTAL-AS-OBS`（超出 480 s = quick_check） |
| W3 | eligible 2220 s，`observation_plus_quick_check` | 同上 | **reject** | `R-QC-IN-OBS` |

**oracle 断言原文：** 观测 0:00–0:29、结束后 quick_check 8 分钟 ⇒ **观测时长 = 29 分钟，不是 37 分钟**。37 分钟是命令总耗时（包含 quick_check），不得作为观测时长；1740+480=2220 的数值巧合正是叠加法的诱因，语义必须分开。**该用例只验证计时算法，不构成真实观察资格。**

| 用例 | 输入 | 手算期望 | 期望判定 | 拒绝码 |
|---|---|---|---|---|
| W4 | 窗A 00:00–00:29、窗B 00:20–00:40，主张 2940 s（`sum_of_windows`） | union=**2400**、sum=**2940**、overlap=**540** | **reject** | `R-SUM-OVERLAP` |
| W5 | 同 W4 两窗，主张 2400 s（`union_of_windows`） | union=2400、sum=2940（标 `forbidden_sum_seconds`） | accept | — |
| W6 | 仅 1 个样本 00:05，主张 0 s | span=**null**（未测量） | **reject** | `R-NO-SAMPLES` |
| W7 | 窗 00:00–00:29，样本含 00:31，主张 1740 s | 窗内 span=1740；越界样本检出 | **reject** | `R-SAMPLE-OUTSIDE` |

W4 手算：重叠区 00:20–00:29 = 9 min = 540 s；并集 00:00–00:40 = 40 min = 2400 s；Σ = 29+20 = 49 min = 2940 s。

## 4. 自然日历用例的 oracle

`frozen_now = 2026-09-20T02:56:38Z`。

| 用例 | 账本 | 主张 | 手算期望 | 期望判定 | 拒绝码 |
|---|---|---|---|---|---|
| C1 **历史攻击复现** | daily 7 条**不同 run_id** 但**同一未来瞬时** `2026-10-01T03:30:00Z`，weekly 2 条 `2026-10-01T04:30Z`/`2026-10-08T04:30Z`，monthly 1 条 `2026-10-01T05:00Z`，alert 1 条 acked；**全部 `report_sha256=""`** | complete | daily_count=**0**，status=**pending** | **reject** | `R-FUTURE-CLOCK`, `R-SAME-INSTANT`, `R-EMPTY-EVIDENCE`（+`R-CLAIM-EXCEEDS`） |
| C2 | daily 5 条 `2026-09-10..14T03:30Z`（唯一 id、非空 hash），weekly 1 条，monthly 0，alert 0 | pending | daily_count=5，status=pending | accept | — |
| C3 | daily 7 条 `2026-09-08..14T03:30Z`；weekly `2026-09-06T04:30Z`,`2026-09-13T04:30Z`（相隔 7 d，最新距 frozen_now 6.94 d ≤7 d）；monthly `2026-09-08T05:00Z`；alert 1 acked | complete | 四窗完成 → status=**complete** | accept | — |
| C4 | daily 6 条 `2026-09-08..13T03:30Z` + 其余同 C3 | complete | daily_count=**6** → pending | **reject** | `R-CLAIM-EXCEEDS` |
| C5 | 账本同 C3，但 `clock_source="simulated_clock_advanced_by_7_days"` | complete | 记录合规但时钟不可信 | **reject** | `R-SIMULATED-CLOCK` |
| C6 | daily 7 条不同日期但最后两条 **run_id 相同** | complete | daily_count=**6** → pending | **reject** | `R-DUP-RUN-ID`（+`R-CLAIM-EXCEEDS`） |
| C7 | 账本同 C3 但 daily 全部 `report_sha256=""` | complete | daily_count=**0** → pending | **reject** | `R-EMPTY-EVIDENCE`（+`R-CLAIM-EXCEEDS`） |

**C3 的限定（必须与结论同时陈述）：** C3 只证明"算法在全部规则被满足时能给出 complete"，其账本是**手写合成 fixture**，**不是**真实自然观察，**不得**被引用为任何周期的完成。真实周期资格由 I-17-A 决定，且当前全部 pending。

**C1 是历史缺陷的复现，不是杜撰：** `reviews/revenue/review.md:13` 记载"本轮受控反例用 7 个不同 ID、同一未来时间、空证据 hash 获得 complete"。本 attempt 用**只读导入生产纯函数**（`RF/tests/test_ca206_soak_window.py`，sha256 `b8169d64…4fe2`）复跑同一输入，记录其返回值作为 RED 侧见证（`before/cmd-CA206REPRO/`）。该复现只读、不写生产、不修改该文件。

## 5. 重叠不相加的"能证伪它的反例"

必须存在**同输入下把判据回退会重新变红**的变异（见 §7 MUT）。W4/W5 是主反例：主张 Σ=2940 与并集 2400 相差 540 s，若实现把重叠窗口相加，W4 会被 accept（错误）或 W5 会被 reject（错误）——两者都能被金标准区分。W2/W3 是 quick_check 混入的反例：37 vs 29。C1/C4/C5/C6/C7 是"用未来时钟/模拟时钟/空 hash/重复 id 凑够周期"的反例。

## 6. 登录 30/60/120 秒检查（#3）：容差预注册 + 能力边界

### 6.1 容差必须在试验前由 reviewer 冻结 —— 现状

```
TOLERANCE PRE-REGISTRATION (I-14-B §6)
  label_offset_tolerance_seconds   : proposed = 5      (implementer proposal, NOT frozen)
  capture_latency_tolerance_seconds: proposed = 5      (implementer proposal, NOT frozen)
  frozen_by                        : independent reviewer session (DSH agent session-b0e4a430ca7d), delegated by parent session-bfecd191-fbc3-4a66-8ed1-6562479bf102
  frozen_at_utc                    : 2026-09-20T03:15:44Z
  frozen_tolerance_seconds         : 5
  reviewer_signature_line          : "frozen_tolerance_seconds = 5   reviewer=independent reviewer session (session-b0e4a430ca7d)   utc=2026-09-20T03:15:44Z"
```

**截至本 attempt，没有任何 reviewer 冻结容差 ⇒ 真实 30/60/120 秒检查未运行，状态 blocked。** 实现者**不得**自签该值。

### 6.2 合成输入上的算法级验证（不是试验）

用 `--tolerance-seconds` 作为**显式输入参数**（不是硬编码常数）在合成输入上跑**容差扫描** tol ∈ {0,1,2,5,10,20,30,60,86,87,90} s：

- L1（诚实锚点：偏移 30/60/120 精确，`live_ui_capture`，捕获延迟 1 s）→ 任意 tol ≥ 0 均 accept。
- L2（历史累计等待：偏移 **29/88/207** s，`live_ui_capture`，延迟 1 s）→ **tol ≤ 86 全部 reject**；tol = 87 起 accept。手算：标签 120 的误差 |207−120| = **87 s** 是最大误差，故边界恰为 87。
- L2b（同 L2 但 `evidence_kind="post_hoc_log"`）→ **任意 tol ≤ 600 都 reject**（`R-POSTHOC-CAPTURE` 与容差无关）。
- L3（偏移精确但 `captured_at = sampled_at + 3600 s`，`post_hoc_log`）→ reject（`R-POSTHOC-CAPTURE`）。
- L4（一个快照 09:00:30 被贴上 30/60/120 三个标签）→ reject（`R-LABEL-ANCHOR`, `R-SAME-INSTANT`）；手算最大误差 |30−120| = 90 s。
- L5（三个标签各自不同 `anchor_event.event_id`）→ reject（`R-ANCHOR-NOT-SHARED`）。

**为什么这不构成"事后挑容差"：** 扫描把 tol 当输入并报告**判定随 tol 变化的边界**，不选一个让结果好看的 tol；结论是"历史累计等待模式在 tol ≤ 86 s 内一律被拒"。proposed=5 s 落在该稳定区间内。真实试验仍待 reviewer 冻结后另行开卡。

### 6.3 UI 捕获能力

判据：若实际支持的 UI 捕获能力未具备 ⇒ 标 **blocked**，**不得**用事后日志伪造即时截图。能力探测（只读，`harness/probe_ui_capture.py`）检查：隔离解释器内可用的捕获工具链、仓库中是否存在"预布置记录器"、是否存在交互式桌面会话。**预期：不具备**（本 attempt 不启动 worker/浏览器/后台常驻进程）。若探测结果与"不具备"不符，以探测原始输出为准并在 review.md 更正。

## 7. 变异清单（§9 执行，逐条回退证明对应反例重新变红）

| 变异 | 回退的判据 | 期望重新变红的用例 |
|---|---|---|
| MUT-1 | J1：改成重叠窗口相加 | W4（错误 accept）或 W5（错误 reject） |
| MUT-2 | J2：允许 `command_total` 当观察时长 | W2 |
| MUT-3 | J3：允许 span+quick_check | W3 |
| MUT-4 | J4：单样本返回 0 而非 null | W6 |
| MUT-5 | J5：忽略越界样本 | W7 |
| MUT-6 | J6/J7：接受未来或模拟时钟 | C1 或 C5 |
| MUT-7 | J8：允许空 hash | C7 |
| MUT-8 | J9：允许重复 run_id | C6 |
| MUT-9 | J10：忽略同一瞬时 | C1 |
| MUT-10 | J12：不校验标签偏移 | L2 |
| MUT-11 | J13：不要求共享锚点 | L5 |
| MUT-12 | J14：接受事后日志/不校验捕获延迟 | L3 |
| MUT-13 | J11：claim complete 优先于计算 | C4 |

## 8. 退出码契约（SUT CLI）

`iso/natural_window.py --cases <in.json> --report <out.json>`

| rc | 含义 |
|---|---|
| 0 | 全部 case 已判定，且**没有任何不合规主张被 accept** |
| 2 | 输入畸形 / schema 不符（fail-closed） |
| 3 | **存在不合规主张被 accept**（反作弊违规，本卡核心失败语义） |
| 4 | 内部错误 |

runner（`harness/run_cases.py`）另判 per-case 期望：cfg 全部匹配 → rc 0；否则 rc 1，并把不匹配逐条落盘。**期望 rc 与 raw rc 分开记录，skip/timeout/未采集不算通过。**

## 8-errata（**在任何运行之前**写成，追加式）

§8 原写 SUT rc `3 = 存在不合规主张被 accept`。写实现时发现该契约**自指**：要数出"不合规主张被 accept"，SUT 必须先具备本卡正在验证的那套判据；于是 BEFORE 版本可以永远返回 0 而"看起来合规"，这正是历史缺陷的形态。改为：

- **SUT CLI rc**：`0` = 报告已写出且每个 case 都已判定；`2` = 输入畸形（fail-closed）；`4` = 内部错误。
- **反作弊门放在 oracle 一侧**：`harness/run_cases.py` 用 `harness/frozen_expectations.json`（运行前手写）逐 case 比对 `verdict`/`refusals`/关键派生量；全匹配 → rc 0，否则 rc 1，并单列 `accepted_ineligible_count`（SUT accept 而 oracle 判必拒的 case 数）。

理由与影响：门的位置从被测件移到独立预期，不改任何 case、不改任何期望值、不改任何数值。`before/` 的 RED 以 runner rc=1 + `accepted_ineligible_count` 为准。

### 8-errata-2：输出形状契约（在 r1 证据运行之前加入）

`harness/run_cases.py` 增加**形状检查**（`REQUIRED_KEYS`）：按卡正文"`scheduled_at`/`started_at`/`sampled_at`/`finished_at` 与 quick_check **分别记录**，不得合并成单一耗时"，每个 case 的 `computed` 必须**逐字段存在**（缺字段即算不匹配）：

- window：`scheduled_at, started_at, first_sampled_at, last_sampled_at, observation_finished_at, observation_span_seconds, sample_count, samples_outside_window, quick_check_seconds, command_total_seconds, schedule_lag_seconds, union_seconds, sum_seconds, overlap_seconds, sum_used_for_natural_duration`
- calendar：`daily_count, weekly_count, monthly_count, alert_count, window_status, clock_source`
- login：`anchor_event_id, shared_anchor_event_id, label_offsets_seconds, label_offset_max_error_seconds, capture_latency_max_seconds, label_count`

时序声明：`before/cmd-CASES-r0/` 是**加入形状检查之前**的一次探索性 RED（runner rc=1，57 处不匹配，12 处不合规主张被 accept），**原样保留**、不覆盖。加入形状检查后**同一命令**重跑为 `before/cmd-CASES-r1/`，作为 RED 主证据。该改动只能**增加**不匹配（更严格），不可能让结果变好，故不构成"事后放宽/挑选 oracle"。

## 9. 需求ID → I-17 待运行日历（#4）

规则：`started_at/due_at` **必须来自真实运行启动**，不得沿用本文档日期，不得用模拟 clock 推到期；未到即 `pending`；只有到时点才可记完成。映射表与只读普查见 `evidence/calendar_mapping.json`（由脚本生成，不手抄）。**本 attempt 全部行保持 pending。**

## 10. 与 I-14-A 的接口

本卡不复制 `iso/slo_probe_patched.py` 进 `RF/tools/`。本卡的 `observation_span_seconds`/`quick_check_seconds`/`command_total_seconds` 三个量与 I-14-A 冻结规则 `M1/M2/M4` 同义并**引用**其命名，不重定义 M3/M5/M6。`calls.failed`=6、tree-sum 高估 ≈11 MB、rc 不可观测等结论按 I-14-A 原样引用，本卡不重测。
