# OWNERPKG-REVENUE-FORECAST-01 · 独立审查分片报告 · Part 2（准确性：命令复核与证据链）

- 审查分片：accuracy — 命令复核 + 证据链（未参与实现，未改任何实现代码）
- 审查日期：2026-11-08
- Worktree：`C:/Users/郑曾波/Projects/rf-job-facade-01-wt`，分支 `codex/rf-job-facade-01`，HEAD `8cd4e18a`
- Python：`C:/Miniconda/python.exe`
- 对照合同：`investment-dashboard/handoffs/owner-requests/revenue-forecast/BUILD-PACKAGE.md` §2（G-m8-RF-01..05）
  及其并入的 `investment-dashboard/handoffs/owner-requests/COMMON-JOB-FACADE.md`（G-m8-COMMON-01/02/03）

---

## 1. 命令复核记录

初跑时 exit code 经管道捕获（取到的是 `tail` 的退出码），为严谨起见全部命令以无管道方式重跑并复核 exit code 与输出。结论一致。

| # | 命令 | Exit code | 关键输出 | 预期 | 判定 |
|---|------|-----------|----------|------|------|
| 1 | `python -m pytest tests/ -q -k rf_job` | 0 | `36 passed, 3404 deselected in 25.27s` | 36 passed | 符合 |
| 2 | `python -m pytest tests/test_rf_job_boundary_regression.py tests/test_report_catalog_deployment.py -q` | 0 | `45 passed in 15.90s` | 45 passed | 符合 |
| 3 | `python -m mypy scripts/rf_job_facade.py scripts/rf_job_cli.py` | 0 | `Success: no issues found in 2 source files` | Success | 符合 |
| 4 | `python .planning/rf-job-facade-01/evidence/drill.py` | 0 | 8 行 `PASS`，0 行 `FAIL`（两次重跑均如此） | exit 0，8 步全 PASS | 符合 |

说明：drill 运行了两次（首次跑 + 无管道 exit-code 复跑）。脚本自清理重建 `C:/Users/郑曾波/Projects/rf-facade-drill`，两次均写且仅写该目录（脚本内 `DRILL_ROOT` 唯一写根，无 network 相关 import）。以下证据链核对以**当前盘上（第二次）**的 `drill_summary.json` / `budget_observation.json` 为准，首次跑样本一并记录。

## 2. 演练证据链核对（drill_summary.json，schema rf-job-drill/1）

`failures: []`，`steps ok: 8/8`。逐项：

- **5.1 help outputs**：PASS。产出 root/submit/get-status/act/list-jobs 五份 help 文本。
- **5.2 幂等重提交**：PASS。程序化比对 `stage_attempts_before == stage_attempts_after` → **True**（逐 attempt 的 attempt_no/elapsed_seconds/exit_code/observations/status 全等，JSON 深比较）；`idempotent_replay=True`、`same_owner_job_id=True`、第二次提交后 `status=succeeded`、第二次提交耗时 0.294s → 未重复编排，符合 G-m8-RF-03「同 idempotency_key 重复提交返回既有 owner_job_id 且不重复运行完整研究」。
- **5.3 kill→恢复链**：PASS。链条：kill（进程树终止，submit rc=1）→ 重启 `get-status` → `status=interrupted`、`status_known=true`、`allowed_actions=[resume, reconcile]` → `reconcile`（rc=0，权威核原，未自动重发）→ `resume` → `final_status=succeeded`、`publication_registered_lines=2`。**source_attempts 数不变**：kill 时 `source_attempts_at_kill` 长度 1（attempt_no=1，completed，`source_outcome=reused_existing`），resume 后 `source_attempt_count=1` → 已完成阶段未重跑，符合 G-m8-RF-04。
  - 注：kill 命中点随进程时序漂移——第一次跑命中 compute（source completed / compute interrupted / publication pending），第二次跑命中 publication（source completed / compute completed / publication interrupted）。两次均为合法 mid-run kill，链条判定与门条件不变；当前盘上证据为 publication 命中版。
- **5.4 自然失败 JobView**：PASS。真实失败（非造假）：owner_job_id `rfjob-20261108-0cf9d2199fef`，source attempt exit_code=3、status=failed；JobView `status=failed`、`allowed_actions=[resume, reconcile]`、`cost={"currency":"USD","value":"0.00"}`、`cost_state=known`（0 下载 + 0 付费调用 → 已知零成本）。
- **5.5 费用 known/unknown 两态**：PASS。known 样本 `{"currency":"USD","value":"0.00"}` + `cost_state=known`；unknown 样本 `cost=null` + `cost_state=unknown`（interrupted job）。

### 预算边界（budget_observation.json，schema rf-job-drill-budget/1）

- `new_downloads_total: 0`，`paid_model_calls_total: 0` —— 与操作者批准的演练预算边界（0 新下载 / 0 付费调用 / 0 网络出站）一致。
- 证据透明度：5.4 失败 attempt 的 observations 记录 `acquisition_calls: 1`（filing-fetch 复用调用），`download_events: 0`。该分类（filing-fetch 本地复用调用计为 acquisition_calls、不计 paid_model_calls）在代码注释（`scripts/rf_job_facade.py`）、单元测试断言（`tests/test_rf_job_status_contract.py::test_natural_source_failure_exposes_failed_attempts`）与 commit `853c26d9` 三处一致，且复用调用产生 0 新下载、0 付费调用——复核认为分类正确、证据链诚实（见 FND-A2，CLOSED）。

## 3. JobView 七字段核对表

实现：`scripts/rf_job_facade.py`（job_view L1227-1260、_cost_projection L1194-1224、_allowed_actions L1184-1191、derive_live_status L1127-1150、常量 L59-89、owner_job_id 生成 L781-783）。合同：BUILD-PACKAGE §2 G-m8-RF-02/03/04 + COMMON-JOB-FACADE G-m8-COMMON-01/02/03（JobView 必填字段 owner_job_id/status/status_known/allowed_actions/cost/cost_state/recovery_capability/return context）。

| 字段 | 合同要求 | 实现核对 | 演练/测试真实样本 | 判定 |
|------|----------|----------|-------------------|------|
| owner_job_id | durable job ID，owner 权威 | `rfjob-{YYYYMMDD}-{uuid12}`（L781-783），持久于 JobStore，跨进程死亡存活；幂等重放同 id | drill 5.2 `same_owner_job_id=True`（kill→resume→二次提交全链同一 id `rfjob-20261108-be3082f61c19`）；5.4 样本 `rfjob-20261108-0cf9d2199fef` | 符合 |
| status | 六态枚举 | 常量 L59-64：queued/running/succeeded/failed/interrupted/unknown；derive_live_status 只返回这六态（L1150 兜底 queued， corrupt 记录 → unknown） | drill：running（at_kill）、interrupted（get-status）、succeeded（resume 终态）、failed（5.4）；queued 由单测 `test_queued_job_resumes_from_scratch` 覆盖 | 符合 |
| status_known | unknown 时 false | `job_view` 恒 true（L1236）；`_unknown_view`（job 文件不可读时，get_status L1339-1341 / list_jobs L1352）→ `status=unknown, status_known=false, allowed_actions=[reconcile]`，有测试锁定（`test_rf_job_recovery.py:84-97`）。**例外见 FND-A1**：job 文件可解析但 attempt 语义损坏时，job_view 输出 unknown+true | drill get-status（可读 job）`status_known=true`；corrupt-file 测试 false | 基本符合，FND-A1（P2, OPEN） |
| allowed_actions | queued=[resume]；running=[]；succeeded=[]；failed/interrupted=[resume,reconcile]；unknown=[reconcile] | `_allowed_actions` L1184-1191 与矩阵逐项一致；单测 `test_allowed_actions_matrix`（`test_rf_job_status_contract.py:95-101`）六行全断言；act 对越权动作拒绝（`action_not_allowed`，`test_resume_of_succeeded_job_is_refused`） | drill：interrupted→[resume,reconcile]、succeeded→[]、失败→[resume,reconcile]、unknown→[reconcile]（corrupt-file 测试） | 符合 |
| cost | DecimalValue\|null | `_cost_projection`：非 queued 且全部 attempt 带观测且付费模型调用=0 → `{"currency":"USD","value":"0.00"}`；否则 null。付费调用>0 时**不发明金额**、保持 unknown（L1220-1223，诚实） | drill 5.5 known `{"currency":"USD","value":"0.00"}` / unknown `null`；5.4 失败 job 已知零成本 | 符合 |
| cost_state | known\|unknown\|not_applicable | queued→not_applicable；total_attempts=0→not_applicable；running 或观测不全或付费调用>0→unknown；全观测且零付费→known（L1194-1224） | drill 5.5 两态真实样本；queued→not_applicable（单测 L118） | 符合 |
| recovery_capability | durable_owner_job + 每类命令声明 durable_owner_job\|short_request_only\|unavailable | job 级 `durable_owner_job`（L1240）+ `command_recovery` L80-89：rf_job.submit/get_status/act/list_jobs=durable_owner_job；source_preparation/revenue_forecast/publication_registry.audit=short_request_only；report_catalog.management_import=unavailable（如实声明，符合红线 §3-6） | drill 5.4 样本完整 8 条 command_recovery；符合 G-m8-RF-04 | 符合 |

补充（合同第 8 项 return context）：`job_view` 含 `result` 字段（L1249）；drill 5.3 resume 成功后 `publication_registered_lines=2`。存在且非空，符合。

**核对结论：七字段全部在场，语义与 §2/Dashboard 合同对齐；唯一偏差为 FND-A1（status_known 配对边缘情形）。**

## 4. Findings

### FND-A1 · status=unknown 可与 status_known=true 同时输出（P2，OPEN）

- **位置**：`scripts/rf_job_facade.py` `job_view` L1236（`status_known` 硬编码 True）；`derive_live_status` L1131/L1136 返回 `STATUS_UNKNOWN` 的路径；`act` reconcile 持久化路径 L1394-1395。
- **复现**（临时探针，FakeStageRunner，无真实研究/无网络，临时目录已自清理）：提交成功后，把 job JSON 中某 attempt 的 `status` 改为非法值 `bogus_state`（JSON 仍合法）→ `get_status` 返回 `status=unknown, status_known=True, allowed_actions=[reconcile]`；随后 `act(reconcile)` 返回并**持久化** `status=unknown, status_known=True`。
- **合同偏差**：BUILD-PACKAGE §2 G-m8-RF-04 / COMMON-JOB-FACADE G-m8-COMMON-02 将 `status=unknown` 与 `status_known=false` 配对（unknown 语义 = owner 无法权威核原状态）；unknown+true 是自相矛盾配对，Dashboard 若以 `status_known=false` 为 unknown_requires_reconcile 触发条件，会把该视图当已核实状态。
- **缓解**：allowed_actions 仍为 `[reconcile]`（矩阵正确）；job 文件完全不可读的路径走 `_unknown_view`，配对正确且有测试锁定；facade 自身只写入封闭状态集，触发需外部损坏可解析记录，公共 API 不可达。
- **建议**：`job_view` 在 `status == STATUS_UNKNOWN` 时将 `status_known` 置 False（或让 `_derive_stage_status` 返回 None 的路径统一走 unknown 视图构造），并补一条针对「可解析但语义损坏」的测试。reviewer_status: **OPEN**。

### FND-A2 · filing-fetch 调用计为 acquisition_calls 而非 paid_model_calls（P3，CLOSED）

- **核对**：5.4 失败 attempt observations 含 `acquisition_calls: 1, download_events: 0`；budget 只累计 `new_downloads` / `paid_model_calls`。分类在代码注释、单测断言（`test_rf_job_status_contract.py`，明言 FF `calls` 是公司 wiki 本地子进程计数，绝非付费模型调用）与 commit `853c26d9` 三处一致；复用调用 0 新下载 0 付费，操作者批准的预算边界（0/0/0）成立，证据链无隐瞒。reviewer_status: **CLOSED**（无需整改）。

（无其他准确性 finding。FND-A1 之外，七字段语义、幂等、kill 恢复链、预算账本均与合同一致。）

## 5. 结论

- 4 条验证命令全部符合预期（exit 0；36 passed / 45 passed / mypy Success / 8 步全 PASS）。
- 演练证据链完整可信：5.2 幂等零重编排（before==after 程序化深比较为 True）、5.3 kill→interrupted→reconcile→resume→succeeded 且 source attempt 恒为 1、budget 双零、5.4/5.5 真实样本在场。
- JobView 七字段核对：全部在场且语义对齐 §2 合同；1 个 P2 OPEN finding（FND-A1，边缘触发、有缓解、修复面小），1 个 P3 CLOSED finding（FND-A2，复核确认分类正确）。
- 本分片未修改任何实现代码；仅新增本报告与两个临时目录内的一次性探针（已自清理）。
