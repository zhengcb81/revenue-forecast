# OWNERPKG-REVENUE-FORECAST-01 · RF job façade 施工计划

Worktree: `C:/Users/郑曾波/Projects/rf-job-facade-01-wt` (branch `codex/rf-job-facade-01`, base `28d646d3`).

## Goal

为 revenue-forecast 仓新增公共 job façade 层（协议 `rf-job/1`），使 Dashboard 能：
提交完整研究（full_research）→ 查询阶段状态 → 中断/重启后核原状态 → 恢复 → 完成 → catalog 登记（沿既有命令）。
**只做编排层与状态层，不重写既有引擎/CLI。**

## 包信息

- 包ID：`OWNERPKG-REVENUE-FORECAST-01`；对应 Dashboard 缺口 G-m8-RF-01…05（+COMMON-01/02/03）
- 施工包：`C:/Users/郑曾波/Projects/investment-dashboard/handoffs/owner-requests/revenue-forecast/BUILD-PACKAGE.md`
- 验收：§5（1命令形状/2幂等/3状态与恢复演练/4真实失败attempt样本/5费用投影/6边界回归/7诚实标注）
- 收口：§8（独立重审agent 0 OPEN P1/P2；PWF 节点更新；并线决策）

## 基线决策（重要）

基线 = `codex/dashboard-rf-b37-release` tip `28d646d3`（2026-11-02），**不是 main**。
理由：§1 现状盘点所述的 report_catalog_cli.py、`--owner-root` 边界（READ_ONLY_COMMANDS 恰 9 个、
WRITE_COMMANDS={"import-w09"}、assert_read_only_command）只存在于 dashboard-rf-b3x 线；
main（90c562ac）没有这套接缝。G-m8-RF-05 要求"保持现状"，故基线必须含该接缝。
b37-release 是 b37 各线（scope/publication）的整合超集，tip 即 docs: seal B37 integrated RF release validation。
详见 findings F-01。

## Nodes
- [x] 读施工包全文 + §3红线全节
- [x] 仓库侦察（目录/惯例/CLI盘点/边界定义位置）
- [x] 基线确认 + worktree/分支建立（28d646d3）
- [x] PWF 登记（本文件 + progress + findings）
- [x] 深读 b37-release 关键 CLI/接缝/测试惯例，产出设计（rf-job/1 形状、job 状态存储、编排方式）
- [x] G-m8-RF-01：full_research 公共 job 提交（submit，幂等键）
- [x] G-m8-RF-02：阶段/attempt 状态与 allowed_actions（get_status）
- [x] G-m8-RF-03：费用/预算/幂等（limits_ref 映射、cost/cost_state 投影、同键不重跑）
- [x] G-m8-RF-04：unknown/中断/重启核原状态/恢复（reconcile、resume、recovery_capability）
- [x] G-m8-RF-05：写/读边界声明保持（约束项 + assert_read_only_command 回归测试）
- [x] 单元测试（pytest，沿仓惯例）
- [x] 验收证据 §5.1-§5.7（演练预算边界先报操作者确认后才跑真实演练）
- [x] §8-1 独立重审 agent（0 OPEN P1/P2 方可交接）——4 分片审查，2×P2 修复后 0 OPEN P1/P2（见 review-report.md）
- [ ] §6 handoff.md/handoff.json + §8-3 并线决策

## Fixed interface decisions（随实现细化，先立骨架）- 协议名 `rf-job/1`；固定 argv/route；请求为固定形状 JSON（ForecastScope + idempotency_key + limits_ref），
  不收路径/命令串/凭据（§2 G-m8-RF-01）。
- 部署根只由部署 argv 给（沿 `--owner-root` 接缝语义）；业务 JSON 不得选根。
- JobView 必填字段对齐 Dashboard 合同：owner_job_id/status/status_known/allowed_actions/cost/cost_state/recovery_capability。
- status=unknown 且 status_known=false → allowed_actions=['reconcile']。
- 恢复不重跑已完成阶段、不重放写命令。
- 管理登记（import-*）入口独立于 job façade，不合并（G-m8-RF-05）。
- 每个 G 条目至少一个独立 commit；提交前 `git branch --show-current` 确认分支。

## §8-3 交接任务（不能安全并线，落盘待触发）

`OWNERPKG-REVENUE-FORECAST-01` 分支 `codex/rf-job-facade-01`
head_commit `e4b38459f54db16e0de8e436690c2eb8c7cd13a1`
已通过独立重审（OPEN P1=0、OPEN P2=0；review-report.md），
**待〈主线 main 的 D 线收口完成（D4-06 ROOT 组合验收关闭）且 owner 侧决定
将 b37-release 线并回 main 时〉由主线任务执行并线**：
`git merge codex/rf-job-facade-01`（或按届时 owner 侧的并线规范），
并线后回归：`pytest tests/ -q -k rf_job`（37 passed 预期）+
`pytest tests/test_rf_job_boundary_regression.py tests/test_report_catalog_deployment.py -q`（45 passed 预期）。
在此之前 dashboard 侧消费以候选 commit
`e4b38459f54db16e0de8e436690c2eb8c7cd13a1` 为准（handoff.json 的
release_tag_or_commit_for_dashboard，可 git rev-parse 解析）。
