# recovery/README.md — I-06-A / a20260922-02

## 撤回规则（rollback）

- **生产仓改动 = 0**：本 attempt 只写了本 attempt 目录。撤回 = 删除
  `execution_runs/I-06-A/a20260922-02/iso/`、`iso-mutant/`、`scripts/`、`evidence/`、`changes.diff`
  及各文档即可；`company-wiki` 与 `revenue-forecast` 产品树**无需任何动作**（从未写入）。
- `before/` = 生产原件快照，保留即为审计基线，删除不影响产品。

## 迁移失败 / 数据非法 / 权限不足时的恢复界限

- 迁移是 **additive-only**（建表 / 补列，`_apply_additive_migrations` + `ensure_processing_demand_columns`），
  不删列、不改列、不删行。失败 ⇒ 编码化 `DemandStoreUnavailable`（fail-closed），**无内存兜底**，
  行数不变（W06A2-N2 实证）。
- 半途中断的迁移可安全重跑（幂等：`CREATE TABLE IF NOT EXISTS` + PRAGMA table_info 补列）。
- 所有隔离数据库只存在于用例 `%TEMP%\w06a2-*` 临时目录，删除无副作用；**不触碰任何生产 pending**。
- demand 行豁免文档 prune/archival（schema 无外键），且 terminal 行**永不**被迁移删除；
  demand 行的唯一状态迁移入口 = 显式生命周期调用（register/claim/complete/fail/reclaim_expired）。

## 崩溃恢复语义（store 侧，OPEN-3）

- worker 崩溃后 running + lease 过期的需求**不会**被自动回收/自动接管：须**显式** `reclaim_expired(now)`
  后重新 `claim(owner, lease_seconds)`。无后台 scheduler、无自动 resume（W06A2-N3 实证）。
- resume/complete 的**消费执行**恢复面 = I-06-B（本 attempt 不实现、不声称）。
