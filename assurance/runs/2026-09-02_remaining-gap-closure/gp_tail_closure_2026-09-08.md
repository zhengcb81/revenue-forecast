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
| Monthly | 1 次（35 天内） | **1/1 ✓** | 首次真实运行 `20260908T203214Z`，`ok=true`，broker 语料 7/7 完整 |
| Alert drill | 1 条带 ack 的告警 | **1/1 ✓** | 真实告警 `20260907T210001Z` 经 `release_gate.py ack` 确认（`acked: true`） |

证据文件：`assurance/runs/monthly_manifest.json`、
`assurance/runs/20260908T203214Z/monthly_broker_report.json`、
`assurance/runs/daily_alert.jsonl`。

### 3.3 尚未完成的自然时间部分（不可压缩）

- Daily 还差 5 次、Weekly 还差 2 次（且需 ≥7 天间隔）。
- 任务注册（monthly 新任务）需 owner 提权执行：
  `python tools\monthly_broker_schedule.py register`（已提供，未执行）。

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
- 结论：sections 缺口已关闭；summary 的 1 份按「预期安全拒绝」记录，不是待办缺陷。

## 6. 运行记录与剩余边界

- 2026-09-08 22:00 daily：见 `assurance/runs/daily_manifest.json`（本节随运行更新）。
- **FC-705 关闸**：`close_gate_allowed=false`（last-two 含 P5：hits=6 且 1:45:55 短窗）。
  P7 自 `2026-09-07T21:00:29Z` 开启，需 09-08 22:00 运行完成后重评；若 P7 窗口 <24h，
  需再等一个窗口，**不按日历放行**。
- **R9 批 3（wiki）**：仍以 FC-705 门为前置，门开即按
  `n1_r9_removal_request.md §3.2` 执行（独立 commit + 三仓 CI 全绿 + legacy-gate 复扫）。
- CI 根因协议两项（README/planning 指向协议、三仓完整验证闭环）：见
  `ci_root_fix.md §6` 后续更新。
