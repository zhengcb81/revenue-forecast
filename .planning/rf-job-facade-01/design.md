# rf-job/1 设计（OWNERPKG-REVENUE-FORECAST-01）

日期：2026-11-07 · 基线 28d646d3 · 分支 codex/rf-job-facade-01

## 1. 定位与红线映射

 façade = 编排层 + 状态层。既有引擎/CLI **零改动**（§3.1：对既有 CLI 文件 git diff 为空）。
 部署根只由部署 argv 给；业务 JSON 不含路径/命令串/凭据（§2 G-m8-RF-01）。
 管理登记（import-*）**不在 façade 内**（§2 G-m8-RF-05、§3.3）：job 完成后由操作者/Dashboard
 走既有显式管理命令 `report_catalog_identity_cli.py import-research-attempt` 登记 catalog；
 façade 的 publication 阶段产出"登记就绪"证据（artifact 清单+SHA），并在 JobView 里明示
 catalog 登记为外部显式步骤（G-m8-RF-02 的"区分 catalog 历史 run 与活 job"）。

## 2. 新增文件

- `scripts/rf_job_facade.py` — 核心库：请求校验、job store（durable 状态）、阶段编排、
  reconcile、恢复、费用投影、锁。
- `scripts/rf_job_cli.py` — 公共 CLI（rf-job/1 固定路由）。
- `config/rf_job_deployment.example.json` — 部署配置示例（真实键名+示例值）。
- `tests/test_rf_job_facade.py` — 编排逻辑单测（注入 fake stage runner；
  明确标注：不作为跨仓真实证据）。
- `tests/test_rf_job_facade_cli.py` — 真实子进程集成（真实 revenue_forecast.py +
  真实 publication_registry.py audit + 真实 source_preparation.py 对 IsolatedLake fixture）。
- `tests/test_rf_job_boundary_regression.py` — §5.6 边界回归（9 只读+import-w09 集合钉住 +
  assert_read_only_command 行为钉住）。

## 3. rf-job/1 协议（固定路由）

```
python scripts/rf_job_cli.py [--owner-root <dir>] [--deployment-config <path>] \
    submit --request-json '<json>'        # 或 stdin
python scripts/rf_job_cli.py ... get-status --job-id <id>
python scripts/rf_job_cli.py ... act    --job-id <id> --action reconcile|resume
python scripts/rf_job_cli.py ... list-jobs [--limit N]
```

退出码：0 成功；2 命名错误（stderr JSON：{schema_version, error:{code,message}}）；
3 内部错误。stdout 一律 JSON（schema_version "rf-job/1"）。路径less 错误（不回显物理路径）。

### submit 请求（业务 JSON，无路径）

```json
{
  "schema_version": "rf-job/1",
  "workflow": "full_research",
  "company_query": "药明康德",
  "information_as_of": "2026-11-02",
  "horizon_end_year": 2026,
  "scenario_set": ["low", "base", "high"],
  "source_snapshot_ids": [],
  "idempotency_key": "<opaque>",
  "limits_ref": "<opaque>",
  "forecast_input": { "...": "完整 RF 输入文档（schema 3.x，内容而非路径）" }
}
```

- `forecast_input`：compute 阶段的完整输入文档。façade 从不发明预测内容（无"输入组装"阶段）；
  提交时用引擎的 `validate_document` 做 fail-fast 校验，并与 scope 交叉核对
  （scenario_set ⊆ 文档各 segment 场景键的并集；文档 forecast_years ⊆ ≤horizon_end_year）。
  偏差即命名错误，不静默收窄。
- `company_query`：驱动 source 阶段的必要字段（包内 ForecastScope 字段清单缺它则无法取源；
  作为显式补充字段登记于 handoff，b37 run.json 同款）。
- `source_snapshot_ids`：来源快照声明，校验形状并记录进 job scope 供追溯；
  v1 不把它机械映射为阶段输入（诚实登记，见 findings F-04）。
- `idempotency_key` 只存 SHA-256（不落原始键值）。
- `limits_ref` 必须命中部署配置 `limits.refs` 表，否则命名错误 `limits_ref_unknown`。

### 部署 argv（可信，非业务输入）

- `--owner-root <绝对存在的目录>`：job store 根（`<root>/artifacts/rf_jobs/`，按需创建）。
  校验规则是 façade 自己的（绝对路径+存在+目录），**不**复用 resolve_owner_root 的
  受管 catalog 门槛（生产根可能尚无受管 catalog——零行≠无数据；登记是独立显式步骤）。
  不修改既有 report_catalog_deployment.py。
- `--deployment-config <path>`：可信部署配置（含阶段命令部署参数与预算表）。

### 部署配置（trusted）

```json
{
  "schema_version": "rf-job-deployment/1",
  "python": "<interpreter>",
  "stages": {
    "source": {
      "filing_fetch_root": "...", "company_wiki_config": "...",
      "company_wiki_catalog_config": "...",
      "source_reader_receipt_version": "2.2", "timeout_seconds": 150.0,
      "request_template": {"schema_version": "1.2", "market": "CN",
        "document_kind": "annual_report", "fiscal_year": 2025,
        "filing_intent": "reuse_only"}
    },
    "compute": {"timeout_seconds": 300.0},
    "publication": {"timeout_seconds": 60.0}
  },
  "limits": {"refs": {"<limits_ref>": {"max_cost_usd": "0.00",
      "max_wall_seconds": 900, "max_new_downloads": 0,
      "max_attempts_per_stage": 3}}, "default_ref": "<limits_ref>"}
}
```

source 阶段请求 = request_template + {company_query, as_of_date}（来自 scope）。
request_template 用 **v2 SourceRef 形状**（schema_version "2.0" + mode "exact"，
同 b37 真实链路 `execution/requests/annual2025.json`）；filing_intent=reuse_only 默认
→ 0 新下载（预算闸门）。

## 4. Job store（durable，崩溃安全）

```
<owner-root>/artifacts/rf_jobs/
  index/idempotency.json     {key_sha256: {owner_job_id, request_sha256, created_at}}
  index/jobs.jsonl           追加式 {owner_job_id, created_at}（list-jobs 用）
  jobs/<id>/job.json         rf-job-state/1（原子写：tmp+fsync+os.replace）
  jobs/<id>/attempts/<stage>-<n>.json   {stage, attempt_no, started_at, ended_at,
                              status: running|completed|failed|interrupted,
                              exit_code, command_shape, observations, result_sha256}
  jobs/<id>/logs/<stage>-<n>.{stdout,stderr}.txt
  jobs/<id>/stages/source/{request.json,result-envelope.json}
  jobs/<id>/stages/compute/{input.json,result.json,report.md}
  jobs/<id>/stages/publication/audit.json（audit 输出）
  jobs/<id>/registry/publications.jsonl（compute formal 经 env REVENUE_PUBLICATION_REGISTRY 写）
  locks/<id>.lock            {pid, host, started_at}；pid 死亡→stale
```

写序：先落 attempt 记录（running）再起子进程；子进程退出后补 exit/observations/result SHA。
原子替换保证任一时刻崩溃后 job.json 要么旧要么新，无半份。

## 5. 阶段编排（固定 argv，子进程）

- source：`source_preparation.py --result-envelope --request-file ... --filing-fetch-root ...
  --company-wiki-config ... --company-wiki-catalog-config ... --source-reader-receipt-version 2.2
  --timeout-seconds T`（全部部署参数来自 config）。
- compute：`revenue_forecast.py <input.json> --output result.json --markdown report.md`
  + env REVENUE_PUBLICATION_REGISTRY=<job ws>/registry/publications.jsonl。
  formal 模式发布登记在此发生（既有写路径，沿 run_forecast→register_publication）。
- publication：`publication_registry.py audit --result result.json`（只读验证，
  env 同上；exit 0 = 注册链干净）。

## 6. 状态机与 JobView

status: queued|running|succeeded|failed|interrupted|unknown

| status | status_known | allowed_actions |
|---|---|---|
| queued（0 attempts，无锁）| true | [resume] |
| running（锁活着）| true | [] |
| succeeded（三阶段均 completed 且 publication audit 干净）| true | [] |
| failed（末次 attempt exit≠0 记录在案）| true | [resume, reconcile] |
| interrupted（attempt running 无 exit 且锁死）| true | [resume, reconcile] |
| unknown（job.json 缺失/损坏/schema 不识别）| false | [reconcile] |

- submit = 落 durable 记录后**同步**跑完三阶段（阻塞式提交，如实登记为 v1 限制；
  中途被杀 → attempts 留 running 痕迹 + 锁死 → 重启后 get-status/reconcile 可核原状态）。
- get-status：只读推导（job.json+attempt 记录+锁存活检查），不修复不写盘。
- act reconcile：重推导**并修复** job.json（权威=磁盘上 attempt 记录+阶段 artifact+SHA）；
  已完成阶段按 artifact SHA 复核后标记 completed，不重跑。
- act resume：从未完成的首阶段继续；completed 阶段跳过（不重放写命令）；
  failed/interrupted 阶段以 attempt_no+1 重试；受 max_attempts_per_stage 约束。
- unknown 且 status_known=false → allowed_actions=['reconcile']（G-m8-RF-04）。

### JobView（Dashboard 合同必填 + 诚实扩展）

```json
{
  "schema_version": "rf-job/1",
  "kind": "rf_job",
  "owner_job_id": "rfjob-...",
  "status": "...", "status_known": true,
  "allowed_actions": ["..."],
  "cost": {"currency": "USD", "value": "0.00"},
  "cost_state": "known|unknown|not_applicable",
  "recovery_capability": "durable_owner_job",
  "command_recovery": {
    "rf_job.submit": "durable_owner_job", "rf_job.get_status": "durable_owner_job",
    "rf_job.act": "durable_owner_job", "rf_job.list_jobs": "durable_owner_job",
    "source_preparation": "short_request_only", "revenue_forecast": "short_request_only",
    "publication_registry.audit": "short_request_only",
    "report_catalog.management_import": "unavailable"
  },
  "stages": [{"stage", "status", "attempts": [{"attempt_no","status","exit_code",
      "started_at","ended_at","observations"}]}],
  "scope": {...}, "limits_ref": "...",
  "created_at", "updated_at",
  "result": {"stage_artifacts": {...含 sha256...}}（成功时）,
  "catalog_history": {"cli": "scripts/report_catalog_cli.py",
    "registration": "external: report_catalog_identity_cli.py import-research-attempt",
    "this_job_registered": false}
}
```

### cost/cost_state 投影（G-m8-RF-03）

每 attempt 记录 observations：{elapsed_seconds, download_events, model_calls}。
- known：所有已完成 attempt 都带观测，且累计 paid model_calls=0 且 download_events 全 0
  （reuse_only 固然为 0）→ value="0.00"；若部署配置提供 pricing 表则按表计价（v1 无表，
  出现 >0 paid calls 一律 unknown，不猜价）。
- unknown：任一 attempt 被中断/无观测（如 drill 的 killed source attempt）→ cost=null。
- not_applicable：queued（尚无任何 attempt）。
limits_ref→部署配置 limits.refs 键映射；未知名→limits_ref_unknown 拒绝提交。

## 7. recovery_capability（G-m8-RF-04）

job 级 durable_owner_job；command_recovery 逐类声明（见上）。façade 之外的
catalog 管理登记如实声明 unavailable（不是 façade 命令，不可由 façade 恢复）。

## 8. 测试与证据映射（§5）

1. 命令形状：`--help` 四路由输出存 evidence；说明对齐 rf-job/1。
2. 幂等：单测（fake runner 记录调用次数：第二次 submit 0 次编排）+ 真实 CLI 幂等演练
   （两次真实 submit，同一 owner_job_id、第二次日志显示 no-op）。
3. 恢复演练：真实 CLI 进程提交 → 中途杀进程 → 重启 get-status → reconcile → resume →
   succeeded；每阶段耗时/观测如实存 evidence（预算边界先报操作者确认）。
4. 真实失败样本：compute 阶段用真实非法输入（自然失败，exit 2）JobView 存 evidence。
5. 费用投影：known（reuse_only 完整成功链）+ unknown（被杀 attempt）真实样本。
6. 边界回归：test_rf_job_boundary_regression.py + 既有 test_report_catalog_deployment.py 全绿。
7. 诚实标注：NOT_RUN 项、mock/单测 vs 真实演练的区分全部写进 evidence/NOT_RUN.md。

## 9. 已知限制（v1，如实登记）

- 阻塞式 submit（submit 调用时长≈研究时长）；无后台 worker。
- source_record 与 forecast_input 的公司/期间一致性不做硬校验（记录进 job state）。
- compute 若在"注册表已追加但 result.json 未落盘"的窗口被杀，resume 重试会产生同锚点
  重复登记行（确定性引擎→同 result SHA，audit 不报冲突；诚实标注，不做静默去重）。
- v1 不编排 import-research-attempt（G-m8-RF-05 边界），登记就绪证据由 publication 阶段产出。
