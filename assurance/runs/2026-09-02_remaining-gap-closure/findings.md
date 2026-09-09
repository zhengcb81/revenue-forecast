# 审查发现（2026-09-02 全面审查）

> **2026-09-07优先状态**：本组下方9/6覆盖后又有其他任务推进。revenue HEAD=6682ecf，latest daily=20260906T210001Z/ok=false/空triplet；DEFAULT_PERIODS改为wiki账本，旧revenue green不代表当前资格。Git确认R9 revenue批1+2工具/测试及CI step已删，wiki批3日志记录延后；不重复执行、不在此追认其全量验收。当前差异见[状态覆盖](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md)，整改以同目录执行手册为编排依据。CI协议是现有WP11输入，旧命令/批准不是本轮push、真实测试、网络、任务或删除授权。保留下方原日志及批准字节。

> [当前状态总入口](../../../PLANNING_STATUS.md)

> **2026-09-09 状态修正**：GP-006（real-roots 阻断且绿）、GP-008（自然触发闭环）、GP-010（sections 7/7）、N-1/FC-150x、CI 协议两项已关闭；GP-009 monthly 1/1、drill 1/1、daily 3/7、weekly 0/2 自然累积中；FC-705 仍关（P7 窗口差 19 秒）。当前逐项结案与证据见 [gp_tail_closure_2026-09-08.md](gp_tail_closure_2026-09-08.md)。

> **2026-09-09 深夜新增发现（R9 批 3 范围失真）**：09-02 申请把批 3 写成「无生产读者 backfill/promoter」，今晚逐符号实测后**该口径大部分已不成立**——`backfill_v2` 有生产导入（`dropbox_governance.py:22` 的 `classify_bucket`）、`portfolio_promoter` 有 CLI 导入（`cli.py:27`）、`_scan_root_v1` 有生产分派（`scanner.py:1401`）与对账调用（`shadow_parity.py:94`/`trace_parity.py:206`）、`legacy_bridge_enabled` 被 `resolver.py:322` 与 `architecture_gate.py:127/139/278` 使用；**仅 `artifact_backfill.py` 零生产读者**。结论：批 3 是"退役 v1 路径/迁移期机制的架构清理"，必须先给出替代路径与回滚，不能按旧清单机械删除。清单与两道门见 [r9_batch3_checklist.md](r9_batch3_checklist.md)。

## 2026-09-06 最新状态与领取规则（优先于下方全部旧覆盖/命令/批准摘要）

2026-09-08规划覆盖：用户只批准planning调整，不授权实施、重新注册、删除或运行。原痛点审计继续保留，活动整改使用[R4虚拟数据湖计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)及其测试矩阵/旧WP迁移表。A/B本地读取、C生产、D运维、M收入按实际依赖推进，不再叠加旧15包95门。本组只作历史执行/批准来源，不并行领取第二套队列，不把旧批准扩大为新动作许可。

- GP-008参数错误已在revenue HEAD `2ff20d9`修复，注册器现为`run-daily`。旧“代码仍阻塞/必须先改拼写”失效；部署Action及自然触发仍未独立闭环，不自动重注册。
- latest观测daily manifest=`20260905T194055Z`、period=2、ok=true，绑定旧`2cbd585`而非当前HEAD；legacy一个ended_at完成窗口、第二个未完成，close_allowed=false。旧9/3唯一run/零completed不再是最新状态，仍不可按预计日期放行。
- GP-010观测为normalized7/7、review7/7、summary6/7、sections5/7，安全拒绝保留，列表式缺口未闭。kind宽范围历史产物214份与精确7份cohort不是同一范围；按owner已有处置保留，不执行旧“DELETE+重扫即无外部副作用”的回滚说法。
- 117 accepted/197 passed不是原目标完成证明：9/6审计找到required tier、真实消费、业务计算、失败账本和发布等实质反例。历史receipt/批准原字节不改，禁止批量重签来制造当前资格。
- 新H01自动prune归档覆盖风险是worker恢复前置。当前整改全部NOT_IMPLEMENTATION_AUTHORIZED；旧授权不自动包含新scope/新版本。GP/R9历史批准保留，但继续执行需WP01/12/13/14相应门、真实数据E2E和当前精确授权。

以下9/2–9/5内容均为有日期的历史快照，不是新的可执行指令；若与本节冲突按本节及新计划处理。真实报告、完整观察、受控删除未完成，不以文档同步勾成完成。

## 2026-09-05 当前纠偏

以下 A～D 及验证数字是9/2发现快照，不是当前待办状态。本次未重跑生产查询或全量测试。

- 新确证阻塞：即使9/5已修电源条件、StartWhenAvailable并改为22:00，daily_t2_schedule.py 的注册 Action 仍为 --run-daily，而CLI只支持子命令run-daily；python -B tools/daily_t2_schedule.py --run-daily仍在参数解析阶段拒绝required: command，未进入runner。owner记录已重注册，但重注册后的实际Action未形成可复核证据。
- GP-006仅接入非阻断Windows sibling临时数据job（continue-on-error=true），不证明真实roots的阻断式CI覆盖。
- registry现为197/197 passed；9/4已新增broker_research规则分节并真实执行，七份目标研报当前5/7有sections。registry通过、能力代码和生产5/7是不同层级，不能相互替代或写成7/7闭环。
- GP-010已有9/3批准和执行：normalize7/7、receipt7/7、summary6/7；1份安全门拒绝；9/4规则分节后sections5/7。不得表述为“等待批准”或完整语义交付。
- 当前daily_manifest仍首个手动run 20260903T211059Z，period1 open；零个completed窗口。R9批准存在但执行门未开，旧固定日期推断撤回。
- 下文A-2原“空值短路，不放行”为笔误：旧缺陷是空值跳过校验而放行，修复后才fail-closed。
- 原DAG 117 accepted与历史completed保持原样；GP当前状态以本组task_plan的9/5覆盖为准，不重签历史receipt。

> 来源：6 个独立审查 agent 实际执行 300+ 测试命令 + 生产 catalog 实证 + 真实 CLI 探针。本文件是唯一发现台账（防双写漂移）。

## 发现分类与证据

### A 类：代码缺陷（已修复）

#### A-1 llm_summarizer 空 source_sha256
- **证据**：`llm_summarizer.py:433` INSERT 第 14 个参数（source_sha256）硬编码 `""`；SELECT 已 join `s.content_sha256 AS source_sha256`（row 有该字段但未传入）。
- **影响**：真实库 49 个 schema-1.0 LLM summary 产物无源字节绑定，被生产 bundle 判为 reusable。
- **修复**：commit afe5eb1（wiki master），`row["source_sha256"] if "source_sha256" in row.keys() else ""`。

#### A-2 artifact validator 放行空 source_sha
- **证据**：`artifact_handle.py:98-99`：`if artifact_source_sha and artifact_source_sha != source["source_sha256"]: reject`——空值短路，不放行。
- **修复**：commit afe5eb1，空值 → reject `artifact_source_sha_missing`（fail-closed）。

#### A-3 runtime_policy.json policy_hash 漂移
- **证据**：生产 snapshot policy_hash=77c1bdb7（2026-08-13）≠ 当前 config 导出 c773099b（2026-08-19 ZR-409 第 4 root 后）；真实 filing 链 `_handle_from_resolution` fail-closed。
- **修复**：CAS 重发 runtime_policy.json（2026-09-02），envelope.policy_hash == policy_export.policy_hash == c773099b，实测真实 CLI resolve 匹配。

### B 类：部署动作（设计上明确延后，不主动实施）

#### B-1 legacy 真实删除未执行
- **证据**：`uc.cli legacy-gate` 实测 `callers_found`（quality.yml 行 133 真实 legacy 调用 verify_closure_ledger.py）；ZR-1009/CA-304 receipt 自述"零真实删除、real_code_removals=0"；R9 仍 4/4 RED；catalog_meta 无任何 legacy_bridge_hits 观测行（两个 ≥24h 零 hit 窗口从未开始）。
- **性质**：CA-304 卡定义"真实删除为部署动作（需两动态周期零 hit 自然证据 + N-1 批准）"。
- **计划**：GP-008 注册观测起点。

#### B-2 自然时间动态审核为零
- **证据**：三仓无 daily_manifest.json/weekly_manifest.json/daily_alert.jsonl；Windows Task Scheduler 无 revenue_daily_t2；三仓 workflow 无 cron；CA-206 receipt 自述"自然时间累积为验收后部署动作"。
- **性质**：工具齐备且诚实 fail-closed（audit_dashboard 今日 exit 1 诚实红灯），但 7 Daily/2 Weekly/1 Monthly 从未开始。
- **计划**：GP-009 注册调度起点。

#### B-3 七份紫金研报真实语义产出 = 0
- **证据**：生产 catalog 7 份 broker_research 全部 active 但 `published_date=NULL、0 artifacts、0 evidence_spans`；全库 sections artifacts 仅 22；ZR-1006 C1 明示该状态为"诚实 pending"；BR-01~26 scenario 全 pending。
- **性质**：2026-08-13 remediation 计划 KD-08 明示"不得批量处理真实研报"，ZR-1007~1105 均注明"本卡不做真实生产 cutover/真实下载"。
- **计划**：GP-010 提交 cutover 授权申请。

#### B-4 privacy_class 3.0 config 升级
- **证据**：`config/source_catalog.yaml` 仍 schema 1.0（无 privacy_class 字段）；policy_3x.py 代码层强制外部 root `private_user`，但生产配置未升级。
- **计划**：GP-007。

### C 类：契约回溯（历史遗留）

#### C-1 receipt 链 87/117 不满足 CA-103 契约
- **证据**：30/117 精确匹配（reviewed_object_sha256 == 11 canonical_hash）；87 不匹配；20 个 12 结构无效（CA-102..109 无 schema/kind）；CA-001..004/101 为 schema-2.0 旧格式。
- **性质**：早期 ZR 单元的 12 receipt 记录 git blob SHA（非 canonical receipt hash），是 CA-103 之前的语义。
- **计划**：GP-004 批量重签发。

#### C-2 scenario registry 197/197 pending
- **证据**：`uc.cli scenario-verify` 实测 unsatisfied=197、closure_ready=false；117/117 receipt 的 scenario_results 全空；CA-105 RED-A 自述"ID 在文本中出现"反模式未消除。
- **性质**：设计为后续填充，从未执行。
- **计划**：GP-005 回填真实执行证据。

### D 类：生产接线（代码完备，物理入口未接）

#### D-1 v2 scanner 生产入口仍走 v1 分支
- **证据**：`scanner.py:833` `_scan_catalog_impl → scan_root_strategy(...)` 未传 v2_scan_shadow；`cutover_decision` 无 src 生产调用者；v2 adapter 链仅 harness/tool 触发。
- **计划**：GP-002。

#### D-2 worker LLM 出口无 privacy/receipt 过滤
- **证据**：`llm_summarizer.summarize_catalog_with_llm` 选数 SQL 无 privacy/receipt/root 过滤；`readiness_graph.py`/`source_lifecycle.py` 在 src 内零调用者；生产库 986 条 dropbox summary 无 receipt。
- **计划**：GP-003。

#### D-3 真实 roots E2E 被 CI 排除
- **证据**：`test_zr806_real_t2_samples.py` 等被 CI `--ignore`；这些套件只在本地验收跑。
- **计划**：GP-006 CI 加 windows-latest job。

## 验证方式记录

每个发现的验证命令与结果：
- A-1/A-2：worker 36 passed + artifact 30 passed（修复后）
- A-3：真实 CLI resolve envelope.policy_hash == policy_export.policy_hash == c773099b（修复后）
- B-1：`uc.cli legacy-gate` → callers_found（实测）
- B-2：audit_dashboard exit 1 "no T2/T3 report"（实测）；closure_gate exit 1（实测）
- B-3：生产 catalog 查询 7 份研报 published_date=NULL、artifacts=0（实测）
- C-1：closure-report 87 incomplete（实测）
- C-2：scenario-verify unsatisfied=197（实测）
