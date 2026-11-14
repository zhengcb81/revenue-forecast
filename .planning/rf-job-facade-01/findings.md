# Findings

## F-01 基线必须在 b37-release 线而非 main (2026-11-07)

施工包 §1 现状盘点（17 个可执行 CLI、report_catalog_cli.py 9 只读+import-w09 写、
`--owner-root` 边界、assert_read_only_command）在 **main（90c562ac）上不存在**——
全仓 grep 零命中；这些只在 `codex/dashboard-rf-b3x` 分支线上：

- `scripts/report_catalog_deployment.py:48` READ_ONLY_COMMANDS（恰 9 个：list-runs、
  list-reports、get-run、get-report、get-model、get-attempt、get-calculation、
  get-calculation-trace、get-source-snapshot）
- `:52` WRITE_COMMANDS = frozenset({"import-w09"})
- `:160` assert_read_only_command 拒绝把可信根继承给写命令

分支拓扑：v3.5.0（71f717bc0）是 main 祖先；b37-release tip `28d646d3`（2026-11-02）
是 b37-scope（21decc17）与 b37-publication feat（80284caf）的整合超集，CLI 最全
（含 verified_compare_cli、subject_resolver、scope_binding、research_publication_sources）。
delivery/dashboard-b37-wuxi-20261102 交付树即产自该线（2026-11-02）。

**结论**：基线 = `codex/dashboard-rf-b37-release` tip `28d646d3`。施工包 §4 的
"当前已发布 release/master HEAD" 按该线解释（仓内无 master/release 分支；main 是
docs-only 的 D 线收口，不含 §1 所述公共面）。该解释连同证据已登记于此，交接时在
handoff.md 明示，供 Dashboard 侧核对。

## F-02 recon 要点（2026-11-07）

- 无 src/；代码在 scripts/（引擎+CLI+contracts）与 tools/；测试 tests/（pytest，199 文件量级），
  全量门禁 `python tools/pre_push_gate.py --ci`（pytest -q）。
- conftest.py session 级把 REVENUE_PUBLICATION_REGISTRY 重定向到 tmp。
- Python 3.12（CI .github/workflows/quality.yml:31）；无 pyproject/setup.py。
- publication registry：JSONL 哈希链 `artifacts/registry/publications.jsonl`
  （scripts/publication_registry.py:53-60，env REVENUE_PUBLICATION_REGISTRY）。
- report catalog：`artifacts/report_catalog/catalog.jsonl` 每行一个 run 对象含 attempts[]；
  **仓内（main）无代码读写它**——读写代码在 b3x 线的 scripts/report_catalog.py。
- ForecastScope/full_research/information_as_of/horizon_end_year/scenario_set/
  source_snapshot_ids 是本包待引入的新概念（全仓零命中），既有近似物：
  delivery/w09/request-scope/local-scope.json（rf-audit-run-scope/1）。
- 无 limits_ref/预算记账模块；既有 resource_limits 形态见
  delivery/w09/request-scope/local-scope.json:10-20（max_cost_usd 等）。
- codex/ 前缀分支是仓内绝对主流惯例；任务包惯例：独立 worktree + codex/ 分支 +
  task_plan 头记录 Worktree/branch/base。

## F-03 source 阶段请求必须用 v2 SourceRef 形状 (2026-11-07)

façade 的 source 请求模板最初按 WU-1201 旧测试写了 schema_version "1.2"，
真实 FF 客户端拒绝（exit 2, request_error）。真实链路（b37
`delivery/dashboard-b37-wuxi-20261102/execution/requests/annual2025.json`）用的形状：

```json
{"schema_version": "2.0", "company_query": "...", "market": "CN",
 "document_kind": "annual_report", "mode": "exact", "fiscal_year": 2025,
 "as_of_date": "...", "filing_intent": "reuse_only"}
```

已改为 request_template schema_version "2.0" + mode "exact"，façade 只注入
company_query + as_of_date。filing_intent=reuse_only 经 FF/ff_financial_statements.py
确认：不需要 acquisition_limits、只查本地 CWP 目录、不联网（预算闸门成立）。

## F-04 v1 诚实限制（随 handoff 交回）(2026-11-07)

1. **阻塞式 submit**：submit 调用时长≈研究时长；job 从创建起即 durable，
   中断/重启后 get-status/reconcile/resume 语义完整（真实演练验证）。
2. **catalog 登记不在 façade 内**：G-m8-RF-05/§3.3 要求管理登记入口独立（不合并）；
   façade 的 publication 阶段产出审计就绪证据，登记由操作者/Dashboard 走
   `report_catalog_identity_cli.py import-research-attempt` 显式完成。
   JobView.catalog_history 明示此边界，this_job_registered=false。
3. **source_snapshot_ids v1 只做声明记录**：校验形状并写入 job scope 供追溯，
   不机械映射为 source 阶段输入（映射语义需 owner 侧定义快照 id↔请求的合同）。
4. **company_query 与 forecast_input.company_name 不做硬核对**（别名/翻译差异合法）；
   information_as_of 与 forecast_input.as_of_date 做相等核对（信息截止日必须一致）。
5. **compute 注册表窗口**：若 compute 在"registry 已追加但 result.json 未落盘"窗口被杀，
   resume 重试 compute 会产生同锚点重复登记行（确定性引擎→同 result SHA，
   publication audit 不报冲突）。未做静默去重，如实登记。
6. **budget-observation 由 façade 记录**：elapsed 由 façade 计时，download/model 计数
   来自 producer receipt / 引擎纯计算属性，不是 b37 式外置 recorder 帧级预算。

## F-05 演练观测不得与原子写竞争（2026-11-08）

Windows 上外部观测进程高频打开 `job.json`（10ms 轮询读）会与 façade 的
tmp+`os.replace` 原子写撞句柄（WinError 5 / 拒绝访问），把 façade 的正常
save 打成 rc=3 internal——**是观测脚本的缺陷，不是 façade 缺陷**（heredoc
低频轮询 repro 全链 6.75s 成功；全部 36 个测试绿）。演练脚本改为轮询
`logs/compute-*.stdout.txt`（阶段开始即创建的文件）作 kill 信号，kill 前
不读 job.json。对 Dashboard 侧的启示：外部监控读 JobView 应低频或经
get-status 路由（进程内读），不要高频裸读 job 文件。

## F-06 filing-fetch `calls` ≠ 付费模型调用（2026-11-08）

`fetch_filing.py` 的 `stats["calls"]` 计数"every real company-wiki
subprocess invocation"（本地 CWP 子进程），不是付费 LLM 调用。façade 曾把它
映射为 paid model_calls，导致零下载自然失败错报 cost_state=unknown
（853c26d9 修复：记为 acquisition_calls，不进付费预算）。

## F-07 独立重审 P3 登记与修复记录（2026-11-08）

4 个独立审查分片（review-part1..4）结论：OPEN P1=0。两个 P2 已修复：

- FND-H1/FND-C5（P2）：重审期间重跑的演练证据未提交 → 修复后全量提交，
  HEAD 证据集与 README 一致。
- FND-A1（P2）：attempt 记录状态值非法时 job_view 输出
  status=unknown/status_known=true（违反 unknown↔false 配对），reconcile
  还持久化该配对 → 修复：derive 为 unknown 时 job_view/_reconcile 一律
  status_known=false（附回归测试 test_illegal_attempt_status_keeps_...，
  rf_job 全套 37 passed）。

随 handoff 交回的 P3（不阻塞，如实登记）：

- FND-C1：act 路由无 idempotency_key 槽位、list-jobs 无 cursor——COMMON
  建议形状偏差，v1 未实现也未在此前声明（本条即声明）。
- FND-C2/FND-R2：max_cost_usd 仅加载期校验（非负+可解析），无按金额的
  运行时闸门——与"无定价表、paid>0 如实 unknown"设计自洽；运行时闸门是
  wall/downloads。
- FND-C3：幂等重放的 idempotent_replay 标志只在返回 view 中体现，不落盘
  job.json。
- FND-H4：budget.wall_seconds_used 只累计成功 attempt 的 elapsed，
  失败/被杀 attempt 的耗时未计入该口径（原始 elapsed 仍在 attempt 记录里）。
- FND-R1：evidence/drill.py 写死本机演练根路径（证据工具，非交付代码）。
- FND-H2/H3：README 日期引用与 task_plan 回勾滞后（已顺手修复）。
