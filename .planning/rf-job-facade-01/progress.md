# Progress

## 2026-11-07

- 开工。读施工包 BUILD-PACKAGE.md 全文（§0-§8）。
- 仓库侦察：scripts/tools/tests/.planning 惯例、CLI 盘点、`--owner-root` 接缝位置
  （`scripts/report_catalog_deployment.py:48` READ_ONLY_COMMANDS、:52 WRITE_COMMANDS、:160 assert 断言）。
- **基线决策**：main（90c562ac）与 v3.5.0（71f717bc0）均无 report_catalog CLI 套件与 owner-root 接缝；
  施工包 §1 现状盘点只与 `codex/dashboard-rf-b37-release` 线吻合。选定基线
  = b37-release tip `28d646d3`（2026-11-02，docs: seal B37 integrated RF release validation）。
  该分支含 9 只读命令 + import-w09 边界 + verified_compare/scope_binding 等最全 CLI 集，
  且整合了 b37-scope/b37-publication 的 feat 提交。详见 findings F-01。
- 建分支 `codex/rf-job-facade-01` + worktree `C:/Users/郑曾波/Projects/rf-job-facade-01-wt`
  （`git worktree add ../rf-job-facade-01-wt -b codex/rf-job-facade-01 28d646d3...`）。
- PWF 登记（task_plan/progress/findings）。
- 设计定稿（design.md）：rf-job/1 固定路由 submit/get-status/act/list-jobs；job store 在
  `<owner-root>/artifacts/rf_jobs/`；三阶段编排（source→compute→publication）沿既有命令；
  catalog 登记保持外部显式管理路径（G-m8-RF-05/§3.3，见 design §1 与 findings F-03）。
- G-m8-RF-01 实现：`scripts/rf_job_facade.py`（核心库）+ `scripts/rf_job_cli.py`（CLI）+
  `config/rf_job_deployment.example.json`（示例部署配置）。
  验证：`pytest tests/test_rf_job_facade.py -q` 4 passed；mypy/ruff 干净。
- G-m8-RF-02 契约测试：`tests/test_rf_job_status_contract.py`（JobView 必填字段、
  failed/interrupted attempt 暴露、allowed_actions 矩阵、list-jobs）6 passed。
- G-m8-RF-03 契约测试：`tests/test_rf_job_cost.py`（幂等不重跑、键只存 SHA、
  limits_ref 映射、预算闸门、cost known/unknown/not_applicable）8 passed。
- G-m8-RF-04 契约测试：`tests/test_rf_job_recovery.py`（中断可恢复、reconcile 修复、
  resume 跳过已完成阶段、损坏状态→unknown、queued 恢复）7 passed。
- G-m8-RF-05 边界回归：`tests/test_rf_job_boundary_regression.py`（9 只读命令集合钉住、
  WRITE_COMMANDS={"import-w09"} 钉住、assert_read_only_command 行为钉住、façade 未扩接缝）。
- 真实子进程集成：`tests/test_rf_job_facade_cli.py` 4 passed（IsolatedLake fixture +
  真实 source_preparation/FF/CWP 复用链 0 下载 + 真实 revenue_forecast formal 发布登记 +
  真实 publication_registry audit；另含真实自然失败样本）。
- 全量 rf_job 套件：36 passed；`pytest -k rf_job` 27s。
- 遗留：§5 真实演练证据（evidence/）、独立重审（§8-1）、handoff（§6）待办。

## 2026-11-08

- 演练预算边界上报操作者（0 新下载/0 付费调用/0 网络出站，只写新演练工作区
  `C:/Users/郑曾波/Projects/rf-facade-drill/`），操作者以"继续"回应后执行演练。
- 演练脚本 `evidence/drill.py` 三轮迭代：
  1. IsolatedLake 传参错误（内部再建一层 lake/）→ 修正；
  2. **演练脚本自身缺陷**：轮询每 10ms 打开 job.json 与 façade 的原子 os.replace
     撞 Windows 句柄（WinError 5，rc=3），三次 retry 全失败——改为轮询 logs 目录
     （compute-*.stdout.txt 出现即 kill 信号），kill 前不读 job.json。façade 本身
     无缺陷（heredoc 低频轮询 repro 全链 6.75s 成功）；
  3. 幂等断言过严（写死 attempt==1，未考虑恢复演练历史 attempt 2）→ 改为重放前后
     attempt 数一致。
- **语义修复（853c26d9）**：filing-fetch stderr 的 `calls` 是本地 company-wiki
  子进程调用计数（fetch_filing.py: "every real company-wiki subprocess
  invocation"），非付费模型调用——原映射到 paid model_calls 导致零下载失败
  错报 cost unknown。改为 `acquisition_calls`，失败 job 如实投影 known 0.00。
- **演练结果 8/8 PASS**（evidence/drill_summary.json，exit 0）：
  §5.1 help 五路由；§5.3 kill mid-run→get-status→reconcile→resume→succeeded
  （source 未重跑，被杀 compute attempt 合法重试）；§5.2 幂等重放零编排；
  §5.4 真实自然失败 JobView；§5.5 费用 known/unknown 两态样本。
- §5.6 边界回归：`test_rf_job_boundary_regression.py` + 既有
  `test_report_catalog_deployment.py` = 45 passed，exit 0。
- §5.7 诚实标注写入 `evidence/README.md`（NOT_RUN：真实生产三仓链路、
  catalog 管理登记；FakeStageRunner 不冒跨仓证据）。
- 演练观察：被 kill 过的 job 恢复成功后仍保持 cost_state=unknown（被杀 attempt
  无观测）——诚实保留，不回填。
- **§8-1 独立重审完成**：4 个独立审查分片并发执行（review-part1..4-*.md），
  汇总报告 review-report.md。结论：OPEN P1=0；两个 P2 修复并复验后关闭——
  FND-H1（最新演练证据未提交→已全量提交）、FND-A1（非法 attempt 状态时
  unknown↔status_known=false 配对被破坏→derive unknown 一律 status_known=false，
  附回归测试，rf_job 全套 37 passed）；5 个 P3 随 handoff 交回（findings F-07）。
  修复后演练重跑 8/8 PASS。
