# S6 P2-05 RF 发现

- `rf-p1` 干净、精确等于正式 origin/main。用户主工区进度分叉，含日周运行产物及计划修改。其他 RF 和 Dashboard 工区仍登记在 Git，不纳入本卡写入。
- 现有日志归 `rf_local_diagnostics`、发布归 `rf_feedback_outbox`、进程边界归 `rf_cli_feedback`。老日志轮转在同一锁内使用标准库破坏性归档，拿锁失败即静默返回。早期 CLI 只覆盖 forecast、source、job 与 catalog，现行源码指纹缺失使整条诊断失败。
- 已有 PWF 的日跑与周跑分别通过 CWP 状态和 FF 收据，月度业务入口已退役，历史 verify 与宿主管理指令继续可认识。实际 Windows 任务不属于这次测试写域。
- 入口准确清单、命令和历史协议在 Step 0 后补齐。


## Step 0 公开入口与故障路径

| 组 | 精确入口 | 基线最早故障与协议 |
|---|---|---|
| 计算与研究 | scripts/revenue_forecast.py、revenue_backtest.py、research_projection.py、research_support_diagnostics.py、generate_input_template.py、lint_input.py、fix_hashes.py | forecast 的装饰器可给 F4 结案但缺本地真栈；其他入口存在解析、文件、旧业务返回漏记。保持实际 JSON、Markdown、检查清单和退出。 |
| 采集消费 | scripts/source_preparation.py、narrative_source_preparation.py、financial_statement_source.py、filing_fetch_client.py | 仅 source_preparation 已注册早期反馈。保留来源 stdout 和 read/refusal stderr 的真实机器信封。使用 FF/CWP 的公开传输，禁止探入跨仓。 |
| 目录与发布 | scripts/report_catalog_cli.py、report_catalog_compare_cli.py、report_catalog_identity_cli.py、report_catalog_identity_resolver.py、report_catalog_verified_compare_cli.py、publication_registry.py | 仅主目录 CLI 已注册反馈。比较和部分来源的 stderr 是单份 JSON；不能加文本。公开子命令和原冻结报告结构保持。 |
| 作业与 F4 | scripts/rf_job_cli.py、rf_job_feedback.py；rf_job_facade.ProductionStageRunner 作为实际业务子进程组合根 | 保存真实 job/attempt，StageRunner 调用源、计算和发布 CLI。F4 独立所有 get-failure、lookup、reconcile-batch、triage、report、get-report、get-triage、flush；对照原记录且冷查不再次录制业务。找到旧格式依赖原 identity 字面比较。 |
| 调度与管理 | tools/daily_t2_schedule.py、daily_t2_runner.py、weekly_t3_schedule.py、weekly_t3_runner.py、monthly_broker_schedule.py | 日周成功/失败通过 AssuranceRun 留现行副本与 owner；启动拒绝、日志写失败可能遗漏。月任务原 run/register 退役，已发布的 verify/query/unregister 仍能解析，原运行留痕继续保留。隔离测试不执行宿主管理动作。 |
| 发布诊断 | tools/release_readiness.py、release_gate.py、slo_probe.py | 工程发布的可操作 owner 命令，保持现有资格逻辑。release_readiness 仍可能丢弃 CWP 子进程 stderr；按真实类型留证。 |

其余工具下的测试驱动、benchmark、预推脚本、合约检查、计划核对、之前退役的 processed_artifact_canary 和 monthly_broker_runner 保留原归属，不能替代业务入口或当作完成证据。安装清单出厂仍无 console scripts 声明。

原生静态扫描覆盖 117 份 RF runtime 源码（不修改原基线）。AT-11 三项为 CWP 源读取抑制真正原因、生成模板无显式异常因果、F4 异常路径直接 print 至机器 stdout。现有独立副本 P1-05 分支从同版继续，范围对照已完成。
