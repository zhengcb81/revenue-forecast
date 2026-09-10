# GP 组尾项关闭记录（2026-09-08）

> 本页是 2026-09-08 按 owner「把未关闭的项目一一处理掉」指令执行的**结案记录**。
> 原则不变：只用机器证据结案，不用勾选代替运行；时间型项目只记录真实累积进度与预计满足日期，
> 不提前宣称完成。原始批准/收据字节不改。

## 1. GP-006（真实 roots 门）——已关闭

**原缺口**：`real-roots` CI job 为 `continue-on-error: true` 且真实 catalog 套件不在阻断式 CI。

**根因（两个，均在 2026-09-08 定位）**：

1. **平台相关哈希**：`compatibility/current.json` 的 `contract_registry_sha256` /
   `command_registry_sha256` 是按 Windows **CRLF 工作树字节**算的；提交的 blob 是 LF
   （`.gitattributes: *.json eol=lf`）。ubuntu `verify` job 把
   `tests/test_compatibility_manifest.py` 列入 `--ignore`，所以该缺陷只在
   windows `real-roots` job 暴露（并被 continue-on-error 掩盖）。
2. **E2E 夹具硬编码本地布局**：filing-fetch 的 `IsolatedWiki` 把
   `PRODUCTION_WIKI` 解析为 `~/Projects/company-wiki`，revenue 的
   `config/filing_fetch.json` 指向 `${USERPROFILE}/Projects/filing-fetch`；
   CI 把兄弟仓克隆到检出目录旁，两个查找都失败。

**修复**：

- registry 哈希按 LF 规范字节重算（`37669f68…` / `d290b994…`；scenario 原本正确）；
- `real-roots` job 在测试前用 junction 复刻本地兄弟仓布局，并**移除
  `continue-on-error`**（该 job 自此为阻断门）；
- `tools/pre_push_gate.py` 增加同款 real-roots 套件 + 需要生产 catalog 的
  REAL_DATA 套件（本地强制；CI 侧要进阻断门需自托管 runner，已如实标注）；
- ZR-105 字节绑定按 **LF 规范化** quality.yml 哈希重绑（`98a92f52…`）。

**证据**：revenue CI **#119（6f041f8）** `verify` 与 `real-roots` **双绿**；对照 #118 的
`real-roots` 为 failure。本地门全绿（含 real-roots 55 passed / real-data 43 passed）。

## 2. GP-008（部署 Action + 自然触发）——已关闭

- 注册器参数缺陷已于 `2ff20d9` 修复（`run-daily` 位置子命令 + 生产默认路径）。
- **自然触发证据**：09-06、09-07 两次 22:00（本地）自然触发，`started_at`
  分别为 `2026-09-06T21:00:28Z` / `2026-09-07T21:00:29Z`；观察期号连续推进
  （P2 关→P3 开、P6 关→P7 开），证明**已注册任务实际执行的是 `run-daily` 且生产默认
  参数生效**——这是 Action 正确性的行为证据。
- **独立读取注册 Action 文本仍受限**：非提权会话 `schtasks /query` 返回
  `Access is denied`（SYSTEM 任务），本记录如实披露该边界，不伪造查询结果。
- 09-08 22:00 为第三次自然触发（见 §6 运行记录）。

## 3. GP-009（自然时间审核）——机制已修，累积中

### 3.1 已修复的机制缺陷（此前会**永久**无法累积）

| 缺陷 | 影响 | 修复 |
|---|---|---|
| weekly T3 在 SYSTEM 上下文找不到下载工具（`Path.home()` = system profile） | 每周 T3 全 skip → weekly 窗口永远无法出现 ok run | `tests/test_e2e_download.py` 工具路径改为**兄弟仓优先、`~/Projects` 回退**；`tests/e2e_support/isolated_wiki.py` 的 `PRODUCTION_WIKI` 同款处理；`tools/weekly_t3_schedule.py` 运行 T3 前把 `USERPROFILE` 设为从仓库位置推导的真实 profile |
| `test_download_rejects_corrupted_local_copy` 硬编码种子文件名 | 该用例恒失败（FileNotFoundError），与产品代码无关 | 改为发现种子 PDF（断言恰好一份） |
| 无任何 monthly 机制 | CA-206 C3 无来源 | 新增 `tools/monthly_broker_runner.py`（只读审计 7 份紫金 broker 语料的 normalized+sections）与 `tools/monthly_broker_schedule.py`（run-monthly/register/query/verify，35 天窗口，任务 `revenue_monthly_broker`） |

### 3.2 真实累积证据

| 项目 | 目标 | 当前 | 说明 |
|---|---|---|---|
| Daily T2 | 7 连续日 | **2/7**（09-06、09-07；09-08 22:00 为第 3 次） | 预计 2026-09-12 满足 |
| Weekly T3 | 2 次、间隔 ≥7 天、均 ok | **0/2** | 09-06 首跑为 blocked（机制缺陷，已修）；下次 2026-09-13 04:30 起累积，且需 provider 可用（cninfo 偶发 upstream_timeout） |
| Monthly | 1 次（35 天内） | **1/1 ✓**（机制 + 任务注册均已完成） | 首次真实运行 `20260908T203214Z`、第二次 `20260908T212321Z`，均 `ok=true`、broker 语料 7/7 完整；任务 `revenue_monthly_broker` 已于 09-08 注册（每月 1 日 05:00，SYSTEM） |
| Alert drill | 1 条带 ack 的告警 | **1/1 ✓** | 真实告警 `20260907T210001Z` 经 `release_gate.py ack` 确认（`acked: true`） |

证据文件：`assurance/runs/monthly_manifest.json`、
`assurance/runs/20260908T203214Z/monthly_broker_report.json`、
`assurance/runs/daily_alert.jsonl`。

### 3.3 尚未完成的自然时间部分（不可压缩）

- Daily 还差 4 次（09-06/07/08 已完成 3 次）、Weekly 还差 2 次（且需 ≥7 天间隔）。
- **monthly 任务注册：已完成**（2026-09-08，owner 在管理员 PowerShell 执行
  `C:\Miniconda\python.exe tools\monthly_broker_schedule.py register` → 输出
  `registered monthly task revenue_monthly_broker`）。注册函数自带 `schtasks /query`
  自校验，因此该输出即"任务确实可查"的证据；非提权会话无法复核（见下）。
- 修复一处新调度器自身缺陷：`New-ScheduledTaskTrigger` **没有** `-Monthly` 参数
  （参数集仅 Once/Daily/Weekly/Startup/Logon），原写法在注册时必然
  `ParameterBindingValidationException`。现改为 `schtasks /create /sc MONTHLY /d 1 /st 05:00`
  + `Set-ScheduledTask` 应用电源/唤醒设置，并加源码级回归测试与 PowerShell 设置构造测试。
- **新增修复（假信号）**：`schtasks /query` 在非提权会话返回 `Access is denied`，
  旧代码把它当成 `missing`——任务明明注册成功却显示"未注册"。现统一为三态
  `registered / missing / unknown`（无法读取时报 `unknown (run elevated)`），
  daily/weekly/monthly 三个工具共用 `query_task_status()`，并加 2 个回归测试。
  实测：`task=revenue_monthly_broker status=unknown detail=cannot read task (run elevated): ERROR: Access is denied.`

## 4. N-1 / FC-150x —— 关闭记录

批准内容（2026-09-03）为「FC-1501~1505 N-1 关闭确认，successor 链 accepted，旧目录冻结不改写」。
机器核对 `assurance/unified_completion/state.json`：successor 单元
**CA-107/108/109、CA-201、CA-301~306 全部 `accepted`**（117/117 账本），FC-1501~1505
本身已不在账本中（被 successor 取代）。**N-1 关闭条件已由机器状态满足并在此记录**；
旧目录/收据保持冻结，不重签。

## 5. GP-010（七份紫金研报语义处理）

- 代码层：wiki `623e831`「fix(GP-010): broker list-style section headings
  (sections 5/7 → 7/7)」——列表式/无分隔符编号标题被识别。
- 语料层（只读核对生产 catalog）：7 份紫金 broker 文档
  **全部具备 `sections` artifact（7/7）**；`summary` 6/7，缺的 1 份为
  `1711c700…`（国联民生 20260324），是 `_FORBIDDEN_OUTPUT` 安全门正确 fail-closed，
  **不得为凑数绕过**，保持拒绝。
- **欠抽取刷新（2026-09-08 补做）**：新规则会让旧的 5 份 artifact 少一个
  「盈利预测与投资建议」分节。已用生产 CLI（`extract-sections --document-id … --force`，
  无 LLM、无门禁绕过）刷新 5 份：
  - 6/7 现为统一的 `earnings_forecast + risk_warning` 两分节；
  - 长江证券 20240304（多实体对比报告）刷新后仍为 3 分节
    （`investment_highlights + risk_warning×2`），规则下未产生 earnings_forecast——
    如实保留，不强行造节；
  - 刷新前已确认这些 artifact 在仓库内**无任何引用**（grep 零命中），不破坏冻结收据；
  - 刷新后月度审计重跑仍 `ok=true`、7/7（`run_id=20260908T212321Z`）。
- 结论：sections 缺口已关闭；summary 的 1 份按「预期安全拒绝」记录，不是待办缺陷。

## 6. 运行记录与剩余边界

### 6.1 2026-09-08 22:00 daily（自然触发）

- `latest_run_id=20260908T210001Z`、`observation_period=8`、**`ok=true`**、
  `started_at=2026-09-08T21:00:10Z`（=22:00:10 本地，自然触发）。
- `report.json`：`triplet.heads` = revenue `add326a` / filing `8e484bb` / wiki `d25d79e`
  （三仓真实 HEAD），`manifest_missing=[]`、`policy_freshness.matches=true`、
  `legacy_hits=[]`、`problems=[]`。`56ba0eb` 的 `safe.directory` 修复在真实触发中生效。
- 当日另修一处同类缺陷：`daily_t2_schedule._head()` 缺 `safe.directory=*`，SYSTEM 上下文
  git 因 dubious ownership 返回空 → 账本出现"ok=true 但 triplet 为空"的失真记录；已修复并加回归测试。

### 6.2 FC-705 关闸（**仍未开**，差 19 秒）

P7 已关闭，但窗口 = `2026-09-07T21:00:29Z → 2026-09-08T21:00:10Z` = **23:59:41**，
比 24h 短 19 秒（本次调度比前一次早启动 19 秒）。因此
`close_gate.reasons = ["period 7: window 23:59:41 is shorter than 24h"]`，
`close_allowed=false`。

按窗口规则推导（不按日历放行）：

| 运行 | 关闭的窗口 | last-two | 判定 |
|---|---|---|---|
| 09-09 22:00 | P8 | P7(短) + P8 | 仍 false（P7 在末两窗内） |
| **09-10 22:00** | P9 | P8 + P9（若均 ≥24h） | **预计 true** |

即：**R9 批 3 最早在 2026-09-10 22:00 运行通过后具备执行条件**；届时应按
`n1_r9_removal_request.md §3.2` 执行（独立 commit + 三仓 CI 全绿 + legacy-gate 复扫
findings=0）。若任一窗口再次 <24h 或 hits≠0，继续等，不提前删除。

### 6.3 其他修复（当日发现）

- `monthly_broker_runner.run()` 的报告目录改为跟随账本所在目录——此前 hermetic 测试会在
  仓库 `assurance/runs/<run_id>/` 留下报告残留（已删除该残留并加测试断言）。
- 推送门顺序：安装一致性同步移到 real-roots/real-data 之前（real-data 内的 drift patrol
  断言安装副本一致，顺序颠倒会产生假红）。

### 6.4 剩余边界

> **2026-09-10 更正**：本节原有两处与本文 §3.3/§5 自相矛盾（monthly 注册、GP-010 刷新），已就地更正；计数按 09-10 实测更新。保留原判断的其余部分。

- **R9 批 3（wiki）**：技术门 = FC-705 门。**2026-09-10 22:00 实测：仍未开**——P9 窗口 **23:59:52（差 8 秒）**；last-two = P8（24:00:11 ✓）+ P9（✗）→ `close_allowed=false`。owner 已授权根治（`41117ce`：runner 真实等待补足 24h），**门预计 2026-09-12 22:00 确定性打开**。**政策门仍未开**（owner 2026-09-06 决定延后至 v2 迁移稳定）。范围结论**再次更正**：先前"仅 `artifact_backfill.py` 零生产读者"**已证伪**（该模块自带运维 CLI `--mode dry-run|apply`、被 3 个契约测试导入、FC-906 卡片标注「FC-901 工具，不改」、冻结 v5 基线有 ZR1005-C1~C4 验收行）→ **当前没有任何小批满足机械删除条件**，owner 的"执行 3a"指令**暂停执行、未删除任何文件**。执行清单见 [r9_batch3_checklist.md](r9_batch3_checklist.md)。
- **调度抖动（2026-09-10 发现 → 同日已授权并根治）**：窗口时长 = 相邻两次 daily 运行的间隔；任务按 22:00 触发但有 ±20 秒抖动，因此间隔 = 24h ± 抖动差，**凡今晚比昨晚早哪怕 1 秒即 <24h**。实测 P7 −19s、P8 +11s、P9 −8s → 约一半的夜晚被判 SHORT，而零 hit 的实质条件每晚都满足（P7~P10 全 hits=0），**卡住门的只是秒级抖动**。**根治已实施（owner 2026-09-10 授权，revenue `41117ce`）**：`run_daily` 在调用只读 observer 前，若当前开放窗口距满 24h 还差 ≤180 秒，则**真实等待**补足再运行——**不放宽 24h 阈值**、不回溯时间戳（observer 记录的仍是实际运行时刻）、提前数小时的手动重跑**不补**（其窗口保持短窗，fail-closed 不变）。新增 `open_period_started_at()`/`window_wait_seconds()` + 6 条 hermetic 测试（含"等待发生在 observer 之前"的行为断言）；对真实账本模拟：准点触发等 13s、早 30 秒等 43s、迟到等 0s。**生效时点**：从 2026-09-11 22:00 运行起；届时 P10 恰满 24h（仍 false，因 last-two 含 P9 短窗），**門预计 2026-09-12 22:00 确定性打开**（P10+P11 均 ≥24h）。
- **GP-009 自然时间（2026-09-10 实测）**：Daily **5/7**（09-06~09-10；还差 09-11、09-12）、Weekly 0/2（首次 09-13 周日 04:30，第二次需 ≥7 天间隔）、Monthly 1/1 ✓、Alert drill 1/1 ✓；首次**自然**月度运行 2026-10-01 05:00。
- ~~**monthly 任务注册**：需 owner 提权执行 …（已提供，未执行）~~ → **更正：已完成**（2026-09-08 owner 提权执行 `tools\monthly_broker_schedule.py register`，输出 `registered monthly task revenue_monthly_broker`，注册函数自带 `schtasks /query` 自校验；见 §3.3）。
- ~~**GP-010 后续（owner 决策）**：… 是否 `--force` 刷新 … 留给 owner 决定。~~ → **更正：已于 2026-09-08 补做**（5 份 `--force` 刷新，刷新前确认仓库内无引用；刷新后月度审计 7/7 仍 `ok=true`；见 §5）。
- **CI 根因协议**：README/planning 指向 + 门禁顺序已闭环；三仓全量回归见 §7。后续每次推送仍按该协议（本仓 pre-push gate → push → 自盯 CI 至绿）。

## 7. 三仓完整验证闭环（2026-09-08）

| 仓库 | 全量回归 | CI（最新推送） |
|---|---|---|
| revenue-forecast | 1108 passed / 1 failed —— `test_ca202_daily_t2_runner::test_c1_runner_report_shape_and_triplet` 断言"报告内 triplet == 当前仓库 HEAD"，而该轮回归期间**本 agent 正在推送**（revenue HEAD 2f57c14→add326a→1da366a）；单独重跑通过。**根因=并发推送竞态，非产品缺陷**（CI 检出不可变，不受影响） | #122（1da366a）success |
| company-wiki | 2668 passed / 7 skipped | #78（d25d79e）success |
| filing-fetch | hermetic 356 passed / 7 skipped（门禁内） | #46（8e484bb）success |

**结论**：三仓全量回归 + CI 自盯闭环成立；唯一红灯已定位为并发推送竞态并有单独重跑证据。

