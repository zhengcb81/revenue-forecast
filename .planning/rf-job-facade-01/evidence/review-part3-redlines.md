# OWNERPKG-REVENUE-FORECAST-01 — 独立审查分片：§3 红线核验（part 3）

- 审查分片：review-part3-redlines（未参与实现）
- worktree：`C:/Users/郑曾波/Projects/rf-job-facade-01-wt`（分支 `codex/rf-job-facade-01`，HEAD `8cd4e18a`）
- 基线：`28d646d3`（`git merge-base --is-ancestor` 确认为 HEAD 祖先）
- 核验日期：2026-11-08
- 依据：`investment-dashboard/handoffs/owner-requests/revenue-forecast/BUILD-PACKAGE.md` §3 红线全节（6 条）
- 测试运行：`C:/Miniconda/python.exe -m pytest`
  - `tests/test_rf_job_boundary_regression.py`：**7 passed**（1.22s）
  - `tests/test_rf_job_facade.py test_rf_job_facade_cli.py test_rf_job_recovery.py test_rf_job_cost.py test_rf_job_status_contract.py`：**29 passed**（24.35s）
- 工作树状态：仅 `.planning/.../evidence/{budget_observation,drill_summary,natural_failure_jobview}.json` 三个证据文件未提交（CRLF 提示），无实现代码改动。

## 总体结论

**§3 六条红线全部 PASS，0 个 OPEN 的 P1/P2 finding**；2 个 P3 记录性 finding（FND-R1、FND-R2），不构成拒收项。

---

## R-1（§3.1）不重写引擎 — **PASS**

要求：source_preparation/revenue_forecast/backtest/catalog 等既有命令的算法与语义零改动；job façade 只是编排层与状态层。

证据：
- `git diff 28d646d3..HEAD --name-only`：仅 24 个**新增**文件——`.planning/rf-job-facade-01/**`（11 个 PWF/证据文件）、`config/rf_job_deployment.example.json`、`scripts/rf_job_cli.py`、`scripts/rf_job_facade.py`、`tests/test_rf_job_{facade,facade_cli,recovery,cost,status_contract,boundary_regression}.py`。无任何既有文件被修改或删除。
- `git diff 28d646d3..HEAD --stat -- scripts/ tools/ e2e/`：仅 `scripts/rf_job_cli.py`(+158)、`scripts/rf_job_facade.py`(+1437)、`config/rf_job_deployment.example.json`(+34)，共 1629 insertions、0 deletions（tools/、e2e/ 无变更）。
- 逐文件 `git diff 28d646d3..HEAD -- <file>`，全部为 **0 行 diff**：`scripts/source_preparation.py`、`scripts/revenue_forecast.py`、`scripts/revenue_backtest.py`、`scripts/report_catalog_cli.py`、`scripts/report_catalog_identity_cli.py`、`scripts/publication_registry.py`、`scripts/revenue_core.py`、`scripts/revenue_publication.py`。
- façade 以固定 argv 子进程调用既有脚本（`rf_job_facade.py:91-93`：`_SOURCE_SCRIPT=source_preparation.py`、`_COMPUTE_SCRIPT=revenue_forecast.py`、`_AUDIT_SCRIPT=publication_registry.py audit`），是纯编排/状态层。

结论：引擎与 CLI 算法语义零改动，façade 只做编排。**PASS**

## R-2（§3.2）不碰既有 loop/WIP/主线与数据根 — **PASS**

要求：施工在独立分支+worktree；不动其他 worktree；不动 `C:/Users/郑曾波/Projects/revenue-forecast` 数据根里的既有数据。

证据：
- 施工在独立 worktree `rf-job-facade-01-wt` / 分支 `codex/rf-job-facade-01`（本分片只读核验，未改实现）。
- 实现文件（scripts/rf_job_*、config、tests/test_rf_job_*）中 grep `Projects/revenue-forecast`、`郑曾波`、硬编码盘符路径：**零命中**——没有写死数据根路径。
- 全部目录创建点（`rf_job_facade.py:140,221,597,677,697,737`）都派生自 `JobStore.store_root = owner_root/"artifacts"/"rf_jobs"`（line 535），即 job store 只在 `--owner-root` 给定目录下创建；`resolve_owner_root`（392-415）要求绝对路径且已存在，不创建根目录本身。
- 验收演练（drill.py:33,141-174）使用独立 `DRILL_ROOT=C:/Users/郑曾波/Projects/rf-facade-drill` + IsolatedLake 隔离湖 + 独立 `owner/` 根，未触碰数据根。

结论：数据根无引用、无写入；store 严格限于 owner-root 下。**PASS**（drill 的机器绑定路径见 FND-R1）

## R-3（§3.3）写读边界不放松 — **PASS**

要求：`--owner-root` 边界保持（9 只读 + import-w09 写）；façade 自身不得把可信根传给写命令；管理登记仍走显式写路径。

证据：
- (a) façade 子进程命令仅三处构建（`_stage_command`，rf_job_facade.py:828-858）：source（`--result-envelope/--request-file/--filing-fetch-root/--company-wiki-config/--company-wiki-catalog-config/--source-reader-receipt-version/--timeout-seconds`）、compute（`input --output --markdown`）、publication（`audit --result`）。grep `--owner-root`：三个命令**均不含**，且有显式注释（859-860）"no stage command ever receives the trusted owner root"。`SubprocessStageRunner.run`（674-703）原样执行 command，不追加参数；env 只注入 `REVENUE_PUBLICATION_REGISTRY`（job 工作区路径）。
- (b) façade import 仅 stdlib（json/os/subprocess/sys/time/uuid/datetime/pathlib/typing），**不 import** report_catalog_deployment/report_catalog 写入口。（boundary 回归测试 import report_catalog_deployment 属钉住行为，正确。）
- (c) `tests/test_rf_job_boundary_regression.py` 钉住：READ_ONLY_COMMANDS == 恰 9 命令 frozenset（list-runs/list-reports/get-run/get-report/get-model/get-attempt/get-calculation/get-calculation-trace/get-source-snapshot，行 31-35）；WRITE_COMMANDS == {"import-w09"}（38-39）；`assert_read_only_command("import-w09", ...)` 抛 `DeploymentError` 且 code=="owner_root_write_forbidden"（42-45）；façade 四命令 submit/get-status/act/list-jobs 均不在 catalog 命令集（72-78）。实测 7 passed。

结论：边界未放松且有回归钉。**PASS**

### R-3b（§3.3）管理登记独立 — **PASS**

- façade/CLI 中 grep `import_w09`/`import_research_attempt`/`import_research_publication`：无任何函数调用，仅文档与声明字符串（rf_job_facade.py:25、1253）。
- `JobView.catalog_history`（rf_job_facade.py:1250-1255）显式声明：`cli: scripts/report_catalog_cli.py`、`registration: "external explicit management import: scripts/report_catalog_identity_cli.py import-research-attempt"`、`this_job_registered: False`。job façade 不合并管理登记。

## R-4（§3.4）预算闸门 — **PASS**

要求：实施期除验收演练外不跑真实研究；演练预算边界先报操作者确认。

证据：
- `.planning/rf-job-facade-01/evidence/budget_observation.json`：两 job 汇总 `new_downloads_total: 0`、`paid_model_calls_total: 0`（wall_seconds_used 7.15s/0.0s，limits_ref 均为 drill-0usd）。
- drill.py 部署配置（147-172）：source `request_template.filing_intent = "reuse_only"`（162 行）；limits `drill-0usd = {max_cost_usd:"0.00", max_wall_seconds:900, max_new_downloads:0, max_attempts_per_stage:3}`（167-170），default_ref 同引用——演练零下载、零成本上限。
- `_enforce_budget`（rf_job_facade.py:1031-1048）：每 stage 完成后（1027 行调用）`wall_seconds_used > max_wall_seconds` 或 `new_downloads > max_new_downloads` 即置 job FAILED 并抛 `budget_exceeded` 终止管线；`_orchestrate`（1051-1068）把 stop 原因写入持久 job。另有 stage 级 attempt 预算（945-947，max_attempts_per_stage）。
- Deployment 校验（345-356）：`max_cost_usd` 必须为非负 decimal 字符串，否则 `deployment_config_invalid`。
- 测试覆盖：`tests/test_rf_job_cost.py:77 test_budget_gate_stops_the_pipeline`（wall 预算超限 → source 后停止、不进 compute），29 个 rf_job 测试全过。

结论：演练零消耗、闸门实现且有测试。**PASS**（max_cost_usd 的运行时语义见 FND-R2）

## R-5（§3.5）不复制 Dashboard 代码 — **PASS**

要求：JobView 字段语义按 §2 对齐，但实现是本仓原生代码；不 import dashboard 仓任何模块。

证据：
- 全部新文件 grep `investment-dashboard|investment_dashboard|dashboard`：仅 2 处**注释/命名级**提及——`scripts/rf_job_facade.py:24` docstring "the operator or the dashboard admits the run through the existing explicit management command"；`config/rf_job_deployment.example.json:25` limits_ref 名 `dashboard-drill-0usd`（纯标签）。无任何 dashboard 仓模块 import（façade 仅 stdlib；CLI 仅 import rf_job_facade 自身）。
- JobView 字段（owner_job_id/status/status_known/allowed_actions/cost/cost_state/recovery_capability/command_recovery/stages/scope/limits_ref/budget/created_at/updated_at/idempotent_replay/result/catalog_history，1227-1260）为本仓原生实现，语义按 §2 合同对齐。

结论：无代码复制、无跨仓 import。**PASS**

## R-6（§3.6）诚实登记 — **PASS**

要求：决定不做的子项如实声明 unavailable/short_request_only，不伪造语义。

证据：
- `COMMAND_RECOVERY`（rf_job_facade.py:80-89）：`rf_job.submit/get_status/act/list_jobs = durable_owner_job`；`source_preparation`/`revenue_forecast`/`publication_registry.audit = short_request_only`；**`report_catalog.management_import = "unavailable"`**，并附诚实理由注释（77-79：管理导入不是 façade 命令、无法由 façade 恢复）。JobView 与 _unknown_view 均携带该声明（1241、1274）。
- 成本投影同样诚实：`paid_model_calls > 0` 时 `cost=None, cost_state="unknown"`（1220-1223，注释明言"不发明价格"）；无观察的 attempt → unknown；queued → not_applicable。
- CLI（rf_job_cli.py）无任何 subprocess/写命令调用路径；tests/test_rf_job_* 中 grep `--owner-root` 与 `import-w09` 组合：**零命中**——不存在把 --owner-root 传给写命令的测试或实现路径。

结论：不可恢复项如实 unavailable，无伪造语义。**PASS**

---

## Findings

### FND-R1
- severity: P3
- 位置：`.planning/rf-job-facade-01/evidence/drill.py:33`（另 37 行 `FF_ROOT = Path.home()/"Projects"/"filing-fetch"`）
- 描述：验收演练脚本把 `DRILL_ROOT` 写死为机器绑定绝对路径 `C:/Users/郑曾波/Projects/rf-facade-drill`。该路径是独立演练 scratch 根，**不是**受保护数据根 `Projects/revenue-forecast`，且 drill.py 是证据工具而非交付实现（不在 scripts/ 交付面）。
- reproduction: `grep -n "DRILL_ROOT =" .planning/rf-job-facade-01/evidence/drill.py`
- root_cause: 演练脚本按本机一次性运行编写。
- retest/建议: 若他机复跑演练，可改为环境变量/tempdir 参数；对红线无影响。
- reviewer_status: ACKNOWLEDGED（记录性，不阻塞交接）

### FND-R2
- severity: P3
- 位置：`scripts/rf_job_facade.py:345-356`（校验）、`1031-1048`（运行时闸门）、`1220-1223`（诚实成本投影）
- 描述：`max_cost_usd` 在 Deployment 加载时校验为非负 decimal 字符串，但**没有**直接按金额的运行时闸门——运行时闸门是 `max_wall_seconds` 与 `max_new_downloads`（外加 stage 级 max_attempts_per_stage）。这与实现自洽：本部署无价格表，façade 拒绝发明金额，观测到 `paid_model_calls > 0` 时 cost_state 如实记 `unknown`（cost=null），因此"金额闸门"无从执行。
- reproduction: 读 `_enforce_budget`（仅 wall/downloads 两闸）与 `_cost_projection`（无定价路径）。
- root_cause: owner 部署无定价表，成本只能投影为 0.00/unknown（诚实语义优先于伪造金额闸门）。
- retest/建议: Dashboard 侧消费 JobView 时应以 `cost_state` 而非 cost 数值做预算判断；若未来接入定价表可再加金额闸门。属设计权衡而非红线违反。
- reviewer_status: ACKNOWLEDGED（记录性，不阻塞交接）

## 汇总

| 红线 | 结论 |
|---|---|
| §3.1 不重写引擎 | PASS（8 个引擎/CLI 文件 0 行 diff；仅新增 façade/CLI/config/tests/PWF） |
| §3.2 不碰数据根/其他 worktree | PASS（数据根零引用；store 仅在 owner-root 下；演练用独立隔离根） |
| §3.3 写读边界不放松 | PASS（stage 命令无 --owner-root；façade 无 catalog 写入口 import；9+1 边界被回归测试钉住且 7 passed） |
| §3.3 管理登记独立 | PASS（无 import_* 调用；catalog_history 显式声明外部显式登记路径） |
| §3.4 预算闸门 | PASS（演练 0 下载 0 paid call；filing_intent=reuse_only、max_new_downloads=0；wall/downloads 闸门+max_cost_usd 非负校验，有测试） |
| §3.5 不复制 Dashboard 代码 | PASS（仅 2 处注释/标签级提及；零跨仓 import） |
| §3.6 诚实登记 | PASS（management_import=unavailable 如实声明；无 owner-root 写命令路径；成本 unknown 语义诚实） |

**Finding 计数：2（P3×2，均 ACKNOWLEDGED；P1=0，P2=0，OPEN 的 P1/P2 = 0）**
