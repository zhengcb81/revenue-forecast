# 独立重审报告 OWNERPKG-REVENUE-FORECAST-01

审查者：4 个独立审查分片（general-purpose agents，均未参与实现，各片独立落盘
review-part1..4-*.md）· 汇总日期：2026-11-08 · 审查基线：`28d646d3`

## 命令复核记录（分片2，review-part2-accuracy.md）

| 命令 | exit | 结果 |
|---|---|---|
| `pytest tests/ -q -k rf_job` | 0 | 36 passed（修复 FND-A1 后 37 passed） |
| `pytest tests/test_rf_job_boundary_regression.py tests/test_report_catalog_deployment.py -q` | 0 | 45 passed |
| `mypy scripts/rf_job_facade.py scripts/rf_job_cli.py` | 0 | Success |
| `drill.py` 重跑（×2 次复核） | 0 | 8 PASS / 0 FAIL，failures=[] |

演练证据链：5.2 `stage_attempts_before == stage_attempts_after`（JSON 深比较 True，
幂等零重编排）；5.3 kill→get-status(interrupted)→reconcile→resume→succeeded，
source attempts 不变（未重跑）；`budget_observation.json` 下载 0、付费 0。

## 逐 G 完整性（分片1，review-part1-completeness.md）

- G-m8-RF-01 delivered（normalize_request 收全 ForecastScope+补充字段，key 只存 SHA；
  source_snapshot_ids 只记录的限制已在 findings F-04 登记）
- G-m8-RF-02 delivered（stage/attempt 只读推导 + allowed_actions 矩阵 +
  catalog_history 区分历史 run）
- G-m8-RF-03 delivered（limits_ref 映射、cost 三态投影、幂等零重编排+真实样本）
- G-m8-RF-04 delivered（unknown↔status_known=false、reconcile 核原、resume 跳过
  completed、taskkill 真实演练 source 未重跑）
- G-m8-RF-05 delivered（边界回归 45 passed、既有 8 个引擎/CLI 文件零 diff）
- COMMON-01/02/03 并入项均 delivered
- 0 not_delivered，无静默缩水

## JobView 字段核对（分片2）

七必填字段全部在场且语义对齐：owner_job_id（durable，幂等同 id）、status（六态）、
status_known（unknown 时 false）、allowed_actions（矩阵逐项一致）、cost
（DecimalValue|null）、cost_state（known/unknown/not_applicable）、
recovery_capability（durable_owner_job + command_recovery 逐类含 management_import
=unavailable）。合同 return context 由 `result` 覆盖。

## 红线核验（分片3，review-part3-redlines.md）—— 6/6 PASS

- §3.1 引擎零改动：8 个既有引擎/CLI 文件对基线 diff 均为 0 行；分支仅新增文件
- §3.2 数据根零触碰：无写死数据根路径；job store 全部派生自 --owner-root
- §3.3 边界不放松 + 管理登记独立：stage 命令无 --owner-root；无 import_w09/
  import_research_* 调用；boundary 回归钉住 9 只读 + import-w09 + assert 拒绝写命令
- §3.4 预算闸门：reuse_only + max_new_downloads=0 + budget_observation 0/0；
  wall/downloads 运行时闸门有测试
- §3.5 无 Dashboard 代码复制：零跨仓 import
- §3.6 诚实登记：management_import 如实 unavailable；paid>0 如实 unknown

## 诚实性（分片4，review-part4-honesty.md）

README NOT_RUN 完整真实；F-04 六条限制与实现一致（抽验属实）；样本均为
drill.py 程序化写出的真实过程产物；task_plan 无"标完成实际没做"。

## Findings 与处置

### 已修复（重审后修复，均有回归/复验）

- **FND-H1/FND-C5（P2→CLOSED）**：重审期间重跑生成的最新演练证据未提交，
  HEAD 证据集与 README 矛盾 → 修复后全量提交，HEAD 与 README 一致。
- **FND-A1（P2→CLOSED）**：attempt 记录状态值非法时 job_view 输出
  status=unknown/status_known=true 且 reconcile 持久化该配对（违反 unknown↔false
  配对）→ 修复：derive 为 unknown 时 job_view/_reconcile 一律 status_known=false；
  回归测试 `test_illegal_attempt_status_keeps_unknown_status_known_false_pairing`
  在套件中（37 passed）。修复后演练重跑 8/8 PASS。
- **FND-H2（P3→CLOSED）**：README 日期引用已修正。
- **FND-H3（P3→CLOSED）**：task_plan Nodes 已回勾。

### P3 随 handoff 交回（OPEN，不阻塞）

- FND-C1：act 无 idempotency_key 槽位、list-jobs 无 cursor（COMMON 建议形状偏差，
  v1 未做，本条即声明）
- FND-C2/FND-R2：max_cost_usd 仅加载期校验，无按金额运行时闸门（与"无定价表"
  设计自洽；运行时闸门为 wall/downloads）
- FND-C3：幂等重放 idempotent_replay 标志不落盘 job.json（仅返回 view 体现）
- FND-H4：budget.wall_seconds_used 只累计成功 attempt 的 elapsed（失败/被杀
  attempt 耗时只在原始 attempt 记录里）
- FND-R1：evidence/drill.py 写死本机演练根路径（证据工具，非交付代码）

## 总结论

**OPEN P1 = 0 · OPEN P2 = 0（两个 P2 修复并复验后关闭）· OPEN P3 = 5（随 handoff 交回）**

可以进入 §6 交接。
