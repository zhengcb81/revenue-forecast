# 独立重审报告 · 分片1：完整性（OWNERPKG-REVENUE-FORECAST-01）

- 审查分片：review-part1-completeness（§8-1 独立审查，审查者未参与实现）
- 日期：2026-11-08
- 被审 worktree：`C:/Users/郑曾波/Projects/rf-job-facade-01-wt`（branch `codex/rf-job-facade-01`，head `8cd4e18a`，base `28d646d3`）
- 验收正本：`investment-dashboard/handoffs/owner-requests/revenue-forecast/BUILD-PACKAGE.md` §2/§5 + `handoffs/owner-requests/COMMON-JOB-FACADE.md`
- 方法：只读核验实现与证据 + 复跑测试（`pytest -k rf_job` → **36 passed**；`test_rf_job_boundary_regression.py + test_report_catalog_deployment.py` → **45 passed**，与证据声明一致）+ `git diff 28d646d3..HEAD` 对 6 个既有 CLI 文件（source_preparation / revenue_forecast / publication_registry / report_catalog_deployment / report_catalog_cli / report_catalog_identity_cli）确认为**空 diff**。

## 1. 逐G对照表

| G条目 | 结论 | 实现位置 (file:line) | §5 对应证据 | 备注 |
|---|---|---|---|---|
| **G-m8-RF-01** full_research 公共job提交 | **delivered** | `scripts/rf_job_facade.py:425-493`（normalize_request 全字段校验）；`:1300-1331`（submit→{owner_job_id, job_view}）；`:496-524`（forecast_input 引擎 fail-fast + scope 交叉核对）；`scripts/rf_job_cli.py:110-124`（rf-job/1 固定四路由）；commit `60ac299d` | evidence/help-*.txt（§5.1 全路由 --help）；drill_summary.json steps 5.2/5.3（真实 submit exit 0）；README.md §5.1 | ForecastScope 字段逐项核对见 §2.1；请求不收路径/命令串/凭据（normalize_request 无路径字段，forecast_input 为内容文档） |
| **G-m8-RF-02** 阶段/attempt状态与allowed_actions | **delivered** | `scripts/rf_job_facade.py:1335-1342`（get_status 只读推导）；`:1153-1181`（逐stage/attempt视图：status/exit_code/elapsed/observations）；`:1184-1191`（allowed_actions 矩阵）；`:1250-1255`（catalog_history 区分历史run与活job）；commit `709c6fea` | natural_failure_jobview.json（真实失败attempt：exit_code 3 + observations + catalog_history 块）；drill_summary.json 5.3（stage 级状态）；tests/test_rf_job_status_contract.py:26-101 | 重点核对见 §2.2 |
| **G-m8-RF-03** 费用/预算/幂等 | **delivered** | `scripts/rf_job_facade.py:375-380`（limits_ref→limits.refs 映射，未知→`limits_ref_unknown`）；`:1194-1224`（cost/cost_state 投影：DecimalValue形\|null + known/unknown/not_applicable）；`:1309-1320`（同键重放返回既有 owner_job_id 且**不进入编排**）；`:489`（幂等键只存 SHA-256）；`:1031-1048`（max_wall/max_downloads 事后闸门）；commit `e65ba44e`+`853c26d9` | drill_summary.json step 5.2（same_owner_job_id=true、idempotent_replay=true、stage_attempts_before==after、二次提交 0.209s）；cost_known_sample.json / cost_unknown_sample.json（§5.5 两态真实样本）；budget_observation.json | max_cost_usd 不做闸门 → FND-C2；idempotent_replay 标志不落盘 → FND-C3 |
| **G-m8-RF-04** unknown/中断/重启核原/恢复 | **delivered** | `scripts/rf_job_facade.py:1263-1275`（`_unknown_view`：status=unknown、status_known=false、allowed_actions=['reconcile']）；`:1335-1342`（不可读状态→unknown 视图）；`:1380-1406`（reconcile 权威=attempt记录+artifact+SHA，修复不重跑）；`:1410-1417`+`:1054-1056`（resume 跳过 completed 阶段、不重放写命令）；`:945-949`（max_attempts_per_stage）；`:80-89`（COMMAND_RECOVERY 逐命令类声明 durable/short_request/unavailable）；commit `732ff8b0` | drill_summary.json 5.3 四步（真实 `taskkill /T /F` 中断→重启 get-status 显示 source=completed/compute=interrupted→reconcile→resume→succeeded 且 source_attempt_count=1 未重跑）；tests/test_rf_job_recovery.py:81-96（损坏→unknown 只许 reconcile，真实单测钉住） | 重点核对见 §2.3；派生 unknown 路径 status_known 语义 → FND-C4 |
| **G-m8-RF-05** 写/读边界声明（约束项） | **delivered** | façade 无任何 import-* 路由；`scripts/rf_job_facade.py:23-27`（docstring 明示 catalog 登记走外部 `report_catalog_identity_cli.py import-research-attempt`）；`:1250-1255`（catalog_history.registration 外部显式）；`tests/test_rf_job_boundary_regression.py:31-78`（9只读命令集合钉住、WRITE_COMMANDS={"import-w09"} 钉住、assert_read_only_command 拒绝写命令钉住、façade 命令不入接缝）；git diff 既有 CLI = 空 | README.md §5.6（45 passed，本次重审复跑一致）+ §5.7（catalog 登记 NOT_RUN 属边界内声明） | 重点核对见 §2.4；小瑕疵：G-05 回归测试随 G-01 的 feat commit `60ac299d` 入库，无独立 commit（§4 commit 纪律对照验收时注意，非功能缺口） |
| **COMMON-01** durable JobView/get_status/act/list_jobs | **delivered** | `scripts/rf_job_facade.py:1227-1260`（JobView 必填七字段+return context `result.stage_artifacts{sha256}`）；`:1335/1359/1344`（get_status/act/list_jobs）；`:1372-1375`（act 按 allowed_actions 闸门）；durable 保障：`:137-154` 原子写、`:953-966` attempt 先落盘再起子进程、`:190-273` 崩溃容忍锁 | help-*.txt；drill_summary.json（四路由全部真实 exit 0）；test_rf_job_status_contract.py:26-34（必填字段钉住）；test_rf_job_facade_cli.py:110-121（真实子进程 exit 2 + 命名错误envelope） | COMMON-01 建议形状部分采纳（act 无 idempotency_key 槽位、list_jobs 无 cursor、allowed_actions 无独立路由）→ FND-C1 |
| **COMMON-02** unknown/reconcile/恢复语义 | **delivered** | 同 G-m8-RF-04；另核 COMMON-02 特有要求"reconcile 只核原状态、**不自动重发**"：`_reconcile`（:1380-1406）只修复 job.json/attempt 记录，从不调用编排；重发只能经显式 `act resume` | 同 G-m8-RF-04 | 同 G-m8-RF-04 |
| **COMMON-03** 费用/预算投影 | **delivered** | `scripts/rf_job_facade.py:1194-1224`（cost: {"currency","value"} DecimalValue形 \| null；三态投影；paid>0 无定价表→unknown 不猜价 :1219-1223）；`:375-380`（limits_ref 映射部署配置键） | cost_known_sample.json / cost_unknown_sample.json；budget_observation.json；test_rf_job_cost.py:122-137, :140-156（not_applicable 态单测钉住） | not_applicable 真实样本未单列 artifact（§5.5 只要求 known/unknown 两态，已满足）；max_cost_usd 见 FND-C2 |

## 2. 任务指定重点核对项

### 2.1 G-01 ForecastScope 字段交代核对

| 字段 | 交代情况 |
|---|---|
| workflow | `rf_job_facade.py:436-437`，仅接受 `full_research` |
| information_as_of | `:441-449`（ISO 日期校验）+ 与 forecast_input.as_of_date 相等核对 `:508-510` |
| horizon_end_year | `:450-453` + forecast_years ≤ horizon 交叉核对 `:511-515` |
| scenario_set | `:454-459` + ⊆ forecast_input 各 segment 场景键核对 `:516-524` |
| source_snapshot_ids | `:460-465` 校验形状，`:478-485` 写入 job scope 供追溯；**"v1 只记录不映射为阶段输入"的限制已声明**：findings.md F-04 第3条（findings.md:66-68）+ design.md §3 |
| company_query（补充） | `:438-440`；作为显式补充字段登记于 design.md §3（"包内 ForecastScope 字段清单缺它则无法取源"） |
| forecast_input（补充） | `:472-477`，引擎 `validate_document` fail-fast `:496-524` |
| idempotency_key / limits_ref | `:466-471`；键只存 SHA-256 `:489`（test_rf_job_cost.py:59-67 钉住明文不落盘） |

结论：无静默缺字段；两个补充字段均有显式声明，非偷偷扩面。

### 2.2 G-02 "区分 catalog 历史 run 与活 job"

`JobView.catalog_history`（rf_job_facade.py:1250-1255）：`cli=scripts/report_catalog_cli.py`（历史 run 只读查询入口）、`registration=external explicit management import: report_catalog_identity_cli.py import-research-attempt`、`this_job_registered=false`。façade 自身不写受管 catalog（模块 docstring :23-27 + design.md §1）。真实样本：natural_failure_jobview.json 的 catalog_history 块。**delivered**。备注：façade 不代理 catalog 历史查询（Dashboard 直用既有只读 CLI）——这是 design §1 的显式设计决策，非缩水。

### 2.3 G-04 unknown && status_known=false → ['reconcile']

两条路径均落实：
- 状态文档不可读/schema 不识别 → `_unknown_view`（:1263-1275）：status=unknown、status_known=false、allowed_actions=['reconcile']；get_status（:1335-1342）捕获 job_state_unreadable 返回该视图；act 对不可读 job 只许 reconcile（:1366-1371）。单测真实钉住：test_rf_job_recovery.py:81-96。
- 派生矩阵 `_allowed_actions("unknown")==["reconcile"]`（:1189-1190；test_rf_job_status_contract.py:101）。
- 注意：job.json 可读但 stages 记录不可用的"派生 unknown"路径 status_known 硬编码 true（:1236）→ FND-C4（P3，动作语义不受影响）。

### 2.4 G-05 管理登记入口独立（不合并）

façade 四路由（submit/get-status/act/list-jobs）中无任何登记命令；登记语义在 JobView.catalog_history 中明示为外部显式管理步骤；`report_catalog.management_import` 声明 `unavailable`（:88，诚实语义）；边界回归测试钉住既有接缝零放宽且本次复跑 45 passed。**delivered**。

## 3. 缩水/缺口清单（findings）

> 结论先行：**未发现任何"做了但没说"或"没做也没说"的静默缩水**；§2 八个 G 条目全部 delivered。以下为对照 COMMON/合同措辞与诚实登记要求的低危偏差，全部 P3，不阻塞 §6 交接（按 §8-1 需在 handoff 或下轮修复中处置）。

### FND-C1 · COMMON-01 建议形状部分采纳，偏差未逐条声明 · severity P3
- **现象**：COMMON-JOB-FACADE.md §G-m8-COMMON-01 请求形状为 `act(owner_job_id, {action, idempotency_key})`、`list_jobs(cursor, limit) -> bounded JobPage`、独立 `allowed_actions(owner_job_id)`。RF 实现：act 只有 `--action`（rf_job_cli.py:120-121）；list-jobs 只有 `--limit`（:123）无 cursor；allowed_actions 无独立路由（经 JobView 暴露 + act 闸门校验 :1372-1375）。
- **评估**：BUILD-PACKAGE §2 明言并入的是 COMMON 的**验收标准**（其 §"owner侧交付验收标准" 1-4，均满足），形状段为"建议"；且语义安全——reconcile 天然幂等（重推导+修复，无副作用叠加）、resume 受 allowed_actions+per-job 锁双重保护、list 有界（默认 50）。故非 P2。
- **缺口点**：该形状偏差未在 findings.md/handoff 声明，Dashboard E12 适配时才发现会浪费一轮对照。**修复建议**：在 handoff.md 的接口说明中登记三行偏差即可（无代码改动）。
- reviewer_status：OPEN（P3，随 handoff 交回）

### FND-C2 · max_cost_usd 只校验不执行，限制未登记 · severity P3
- **现象**：`Deployment._validate_limits`（rf_job_facade.py:345-356）接受并校验 `max_cost_usd` 格式，但 `_enforce_budget`（:1031-1048）只执行 `max_wall_seconds` 与 `max_new_downloads` 两个闸门；`max_cost_usd` 在 v1 无任何执行语义。
- **评估**：v1 无定价表，paid model_calls>0 一律投投影 unknown（:1219-1223，已声明）； drills 全链 0 付费调用，实际风险为零。但部署配置示例（config/rf_job_deployment.example.json:26）把它写成像生效键一样，而 findings F-04 未登记"max_cost_usd 不做硬闸门"。
- **修复建议**：F-04 或 handoff 补一行登记（或在 deployment config 注释标明 v1 不生效）。
- reviewer_status：OPEN（P3）

### FND-C3 · idempotent_replay 标志只在重放响应中为 true，不落盘 · severity P3
- **现象**：submit 重放路径 `job["idempotent_replay"] = True`（rf_job_facade.py:1319）仅改内存副本后返回视图，未 `save_job`；此后 get-status/list-jobs 读 durable job.json 显示 `idempotent_replay=false`。
- **评估**：合同要求的语义（同键→同 owner_job_id、不重复编排）完全正确（drill 5.2 + test_rf_job_cost.py:35-48 钉住）；仅"本次响应是重放"这一标志不持久，Dashboard 若事后想从 get_status 判断"曾重放过"会得到 false。
- **修复建议**：一行 `self.store.save_job(job)` 或在 handoff 登记该标志为响应级而非持久级。
- reviewer_status：OPEN（P3）

### FND-C4 · "派生 unknown"路径 status_known=true 与 COMMON-02 配对措辞不对称 · severity P3
- **现象**：job.json 可读但 stages 记录不可用时，`derive_live_status` 返回 unknown（:1131,:1136），而 `job_view` 的 status_known 硬编码 True（:1236）——即存在 status=unknown 且 status_known=true 的组合。COMMON-02/G-04 的配对（unknown→status_known=false→['reconcile']）在"状态文档不可读"主路径成立并被单测钉住。
- **评估**：两路径 allowed_actions 均为 ['reconcile']（:1189-1190），Dashboard 动作语义不受影响；但 status_known 字段语义在两条 unknown 路径间不一致，且未声明。
- **修复建议**：派生 unknown 时置 status_known=false（一行改动+一个单测），或在 handoff 登记该组合的语义。
- reviewer_status：OPEN（P3）

### FND-C5 · 三个演练证据文件在最后一次 commit 后有未提交修改 · severity P3
- **现象**：`git status` 显示 evidence/drill_summary.json、budget_observation.json、natural_failure_jobview.json 相对 head `8cd4e18a` 有未提交修改（本次审查所读即磁盘现行版本，内容与 README 声明一致）。
- **评估**：§8-1 要求"原始失败记录保留不改写"；当前磁盘版本是演练最终轮产物，但 git 历史与磁盘不同步，交接对账时会出歧义。
- **修复建议**：§6 交接前将三个文件入库（commit 仅含 evidence，不改实现）。
- reviewer_status：OPEN（P3）

## 4. 声明过的 NOT_RUN/限制核对（诚实性·完整性侧）

| 限制 | 声明位置 | 核对 |
|---|---|---|
| 阻塞式 submit（时长≈研究时长，无后台 worker） | design.md §9-1、findings F-04-1 | 一致，非 §2 缩水（G-01 未要求异步） |
| catalog 登记不在 façade 内 | findings F-04-2、design §1、evidence README §5.7 | 一致，且正是 G-05 要求 |
| source_snapshot_ids 只记录不映射 | findings F-04-3、design §3 | 一致 |
| 真实生产三仓链路 NOT_RUN（用离线 IsolatedLake 真子进程替代） | evidence README §5.7 | 一致，未把单测/FakeStageRunner 冒真实证据（README 明示区分） |
| compute 注册表窗口重复登记行 | findings F-04-5、design §9 | 一致（未做静默去重，如实登记） |

未发现未声明的 NOT_RUN 项。

## 5. 分片结论

- §2 逐条：**G-m8-RF-01/02/03/04/05 + COMMON-01/02/03 全部 delivered**（0 not_delivered），每条均有 §5 对应证据且证据链经本次复跑核验（36+45 passed 与声明一致）。
- **P1：0；P2：0；P3：5**（FND-C1..C5，均为登记/形状/卫生类，无功能缺口）。
- 完整性维度：**0 个 OPEN 的 P1/P2，满足 §8-1 进入 §6 交接的前置条件**；P3 随 handoff 一并交回。
