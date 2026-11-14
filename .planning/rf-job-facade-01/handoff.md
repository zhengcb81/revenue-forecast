# OWNERPKG-REVENUE-FORECAST-01 · 交接文件（handoff）

日期：2026-11-08 · 分支 `codex/rf-job-facade-01` · 基线 `28d646d3`（codex/dashboard-rf-b37-release tip）
交付完全体 commit：**`e4b38459f54db16e0de8e436690c2eb8c7cd13a1`**

## 1. 交付了什么

rf-job/1 公共 job façade：`scripts/rf_job_facade.py` + `scripts/rf_job_cli.py` +
`config/rf_job_deployment.example.json` + 6 个测试文件（37 rf_job tests +
45 boundary/catalog 部署回归）+ 全套验收证据（`.planning/rf-job-facade-01/evidence/`）。

Dashboard 侧四路由（固定 argv，业务 JSON 无路径/命令串/凭据）：

```
python scripts/rf_job_cli.py [--owner-root <dir>] [--deployment-config <path>] \
  submit | get-status --job-id | act --job-id --action reconcile|resume | list-jobs [--limit N]
```

- submit 请求：`{schema_version:"rf-job/1", workflow:"full_research", company_query,
  information_as_of, horizon_end_year, scenario_set, source_snapshot_ids, idempotency_key,
  limits_ref, forecast_input}`（forecast_input 为完整 RF 输入文档内容，façade 不发明预测内容）
- JobView 必填七字段对齐 Dashboard 合同；status=unknown ⇔ status_known=false ⇔
  allowed_actions=["reconcile"] 配对由回归测试钉住
- job store：`<owner-root>/artifacts/rf_jobs/`（durable，原子写，幂等索引只存 key 的 SHA-256）
- **catalog 登记不在 façade 内**（G-m8-RF-05/§3.3）：job 成功后由操作者/Dashboard 走
  既有显式管理命令 `report_catalog_identity_cli.py import-research-attempt` 登记；
  JobView.catalog_history 声明此边界（this_job_registered=false）

## 2. 验收证据索引（§5）

| §5 | 证据 |
|---|---|
| 5.1 命令形状 | evidence/help-*.txt（5 个路由真实 --help） |
| 5.2 幂等 | drill_summary.json 步骤 5.2（同 key 同 owner_job_id、attempts 重放前后一致、0.3s no-op） |
| 5.3 恢复演练 | drill_summary.json 步骤 5.3×4：taskkill /T /F 真实杀进程树→get-status→reconcile→resume→succeeded，source 未重跑；每阶段 elapsed/观测如实记录 |
| 5.4 失败样本 | natural_failure_jobview.json（真实自然失败，0 下载） |
| 5.5 费用 | cost_known_sample.json（known 0.00）+ cost_unknown_sample.json（unknown null） |
| 5.6 边界回归 | test_rf_job_boundary_regression.py + test_report_catalog_deployment.py = 45 passed |
| 5.7 诚实标注 | evidence/README.md（NOT_RUN 清单）；findings F-04/F-07 限制登记 |
| §8-1 重审 | review-report.md + review-part1..4-*.md（OPEN P1=0，OPEN P2=0，P3×5 随交） |

## 3. 红线核验（§3 全过）

- 引擎零改动：8 个既有引擎/CLI 文件对基线 diff=0 行（重审分片3 逐文件核验）
- 预算：演练 0 新下载/0 付费调用/0 网络出站；wall/downloads 运行时闸门 + limits_ref 映射
- 边界：façade 无任何 import 路由，管理登记独立；assert_read_only_command 行为钉住
- 不复制 Dashboard 代码；数据根零触碰；演练只写 rf-facade-drill 工作区

## 4. v1 已知限制（P3 随交，详见 findings F-04/F-07）

1. 阻塞式 submit（job 从创建起 durable，中断/恢复语义完整——真实演练验证）
2. catalog 登记为外部显式管理步骤（G-m8-RF-05 边界）
3. source_snapshot_ids v1 只记录不映射
4. company_query 与 forecast_input.company_name 无硬核对；information_as_of 与
   forecast_input.as_of_date 强制相等
5. compute 被杀在"registry 已追加/result 未落盘"窗口时，resume 重试可能产生同锚点
   重复登记行（确定性引擎→同 result SHA，audit 不报冲突；不静默去重）
6. budget.wall_seconds_used 只累计成功 attempt elapsed（FND-H4）
7. act 无 idempotency_key 槽位、list-jobs 无 cursor（FND-C1）
8. max_cost_usd 只校验不执行金额闸门（FND-C2/R2，与"无定价表"自洽）
9. drill.py 写死本机演练根（FND-R1，证据工具）

## 5. §8-1 独立重审

4 个独立审查分片（未参与实现）：完整性全 delivered、准确性命令复核全过（pytest 37、
边界 45、mypy Success、drill 重跑 ×2 全 PASS）、红线 6/6 PASS、诚实性如实。
两个 P2 修复并复验关闭（FND-H1 证据提交、FND-A1 unknown↔false 配对修复+回归测试）。
**OPEN P1=0、OPEN P2=0**；5 个 P3 随 handoff 交回（findings F-07）。

## 6. §8-3 并线状态（不能安全并线）

主线 main 是 docs-only 的 D 线收口（90c562ac），本分支基线是 b37-release 线
（28d646d3）——并线=把 b37 基线整体并入 main 的大规模整合，且主线有在途 D 线
收口在途（D4-02 复核已过、待 D4-06 ROOT 组合验收）。**不满足"安全并线"条件**
（§8-3.1），按 §8-3.2 落盘显式交接任务（见 task_plan.md 交接任务段）。

**Dashboard 消费方式**：按固定候选 commit 消费，不追踪分支名：
`e4b38459f54db16e0de8e436690c2eb8c7cd13a1` ← 见 handoff.json 的
release_tag_or_commit_for_dashboard（40 位可 rev-parse）。

## 7. Dashboard 接入指引（MODULE-m8-RF-executor 新卡）

1. 绑定固定 commit `e4b38459f54db16e0de8e436690c2eb8c7cd13a1`（handoff.json），
   checkout 或 archive 该 commit 的 scripts/rf_job_cli.py + config/rf_job_deployment.example.json
2. Dashboard 侧部署参数：--owner-root（绝对存在的目录，job store 宿主）+ --deployment-config
   （source 阶段真实链路部署参数 + limits.refs 预算表）
3. 按 rf-job/1 四路由对接 submit/get-status/act/list-jobs；错误为 stderr 命名 JSON
   （exit 2）——映射到 Dashboard 的 unknown_requires_reconcile
4. E12 三类真实隔离命令验收由 Dashboard 侧执行（本包 §7）；RF 侧演练边界已备案
   （0 下载/0 付费/0 网络出站）
5. handoff.json 的 PWF 路径清单供 dashboard 对照时间线（§8-2）
