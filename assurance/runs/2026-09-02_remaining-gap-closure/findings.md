# 审查发现（2026-09-02 全面审查）

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
