# GP-010 Cohort Cutover 授权申请：七份紫金研报语义处理

> **2026-09-07优先状态**：本组下方9/6覆盖后又有其他任务推进。revenue HEAD=6682ecf，latest daily=20260906T210001Z/ok=false/空triplet；DEFAULT_PERIODS改为wiki账本，旧revenue green不代表当前资格。Git确认R9 revenue批1+2工具/测试及CI step已删，wiki批3日志记录延后；不重复执行、不在此追认其全量验收。当前差异见[状态覆盖](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md)，整改以同目录执行手册为编排依据。CI协议是现有WP11输入，旧命令/批准不是本轮push、真实测试、网络、任务或删除授权。保留下方原日志及批准字节。

> [当前状态总入口](../../../PLANNING_STATUS.md)

> **2026-09-09 状态修正**：GP-006（real-roots 阻断且绿）、GP-008（自然触发闭环）、GP-010（sections 7/7）、N-1/FC-150x、CI 协议两项已关闭；GP-009 monthly 1/1、drill 1/1、daily 3/7、weekly 0/2 自然累积中；FC-705 仍关（P7 窗口差 19 秒）。当前逐项结案与证据见 [gp_tail_closure_2026-09-08.md](gp_tail_closure_2026-09-08.md)。

## 2026-09-06 最新状态与领取规则（优先于下方全部旧覆盖/命令/批准摘要）

2026-09-08规划覆盖：用户只批准planning调整，不授权实施、重新注册、删除或运行。原痛点审计继续保留，活动整改使用[R4虚拟数据湖计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)及其测试矩阵/旧WP迁移表。A/B本地读取、C生产、D运维、M收入按实际依赖推进，不再叠加旧15包95门。本组只作历史执行/批准来源，不并行领取第二套队列，不把旧批准扩大为新动作许可。

- GP-008参数错误已在revenue HEAD `2ff20d9`修复，注册器现为`run-daily`。旧“代码仍阻塞/必须先改拼写”失效；部署Action及自然触发仍未独立闭环，不自动重注册。
- latest观测daily manifest=`20260905T194055Z`、period=2、ok=true，绑定旧`2cbd585`而非当前HEAD；legacy一个ended_at完成窗口、第二个未完成，close_allowed=false。旧9/3唯一run/零completed不再是最新状态，仍不可按预计日期放行。
- GP-010观测为normalized7/7、review7/7、summary6/7、sections5/7，安全拒绝保留，列表式缺口未闭。kind宽范围历史产物214份与精确7份cohort不是同一范围；按owner已有处置保留，不执行旧“DELETE+重扫即无外部副作用”的回滚说法。
- 117 accepted/197 passed不是原目标完成证明：9/6审计找到required tier、真实消费、业务计算、失败账本和发布等实质反例。历史receipt/批准原字节不改，禁止批量重签来制造当前资格。
- 新H01自动prune归档覆盖风险是worker恢复前置。当前整改全部NOT_IMPLEMENTATION_AUTHORIZED；旧授权不自动包含新scope/新版本。GP/R9历史批准保留，但继续执行需WP01/12/13/14相应门、真实数据E2E和当前精确授权。

以下9/2–9/5内容均为有日期的历史快照，不是新的可执行指令；若与本节冲突按本节及新计划处理。真实报告、完整观察、受控删除未完成，不以文档同步勾成完成。

## 2026-09-05 当前授权与交付状态（覆盖原申请头尾）

9/3 owner批准已经记录，下文“待批准”“等待KD-08批准后执行”仅为原申请历史，现已失效，不重复申请。实际结果：normalized7/7、review receipts7/7、LLM summary6/7；1份经三次尝试被安全门拒绝，保持fail-closed；9/4规则提取后目标研报sections=5/7，另2份列表式研报仍为0。

申请准备和授权环节已完成，但原“每份3 artifacts”“7次调用”“无安全门命中”验收并未满足，不得统一勾选。summary安全拒绝与broker分节产品缺口分别记录，不能为完成目标绕过安全门。

原末尾“BR保持blocked”是当时生产验收判断；当前scenario registry已登记197/197 passed，且9/4已有规则分节能力/真实执行。registry测试通过、能力实现与目标研报5/7产物不等价。现状态为authorized / partial_execution / safety_rejection_expected / sections_gap_open；本次不重新处理文档或改写registry。

> **申请人**：MiMo-v2.5-pro（AI Agent，Xiaomi MiMo Team）  
> **日期**：2026-09-02  
> **状态**：待批准  
> **关联**：B-3 缺口（task_plan.md）、KD-08 授权要求

## 1. 背景

审查发现七份紫金矿业（601899）研报的真实语义处理未完成：

- **来源**：company-wiki 的 `companies/紫金矿业/raw/` 目录下 7 份 PDF 研报
- **当前状态**：BR-01~26 scenario 全部 pending，0 artifacts / 0 spans
- **根因**：KD-08 明示"不得批量处理真实研报"，需 cohort cutover 授权

## 2. 处理范围

| 项目 | 内容 |
|---|---|
| **文档** | 7 份紫金矿业研报 PDF（券商深度报告/季报点评/行业报告） |
| **处理方式** | LLM 摘要（source_catalog_llm_summary）+ 分节提取（section_extractor） |
| **数据流向** | PDF → normalize（文本提取）→ LLM 摘要/分节 → artifacts 表 |
| **外部调用** | LLM API（MiniMax-M3 或 mimo-v2.5-pro）——单次约 2000 tokens |
| **存储影响** | 每份研报生成 normalized/summary/sections 3 个 artifact（~10KB/份） |

## 3. 安全措施

| 措施 | 说明 |
|---|---|
| **隐私门** | 紫金研报位于 company_raw 根（privacy_class=public），经 GP-003 LLM 出口门允许 |
| **receipt 门** | 每份文档需有效 prompt-injection review receipt（source_sha256 绑定）才进 LLM |
| **内容过滤** | LLM 输出经 _FORBIDDEN_OUTPUT 正则过滤（禁止投资结论/目标价/估值） |
| **审计追踪** | 每次 LLM 调用记录 provider/model/usage/content_hash/artifact_id |
| **回滚** | artifacts 表 DELETE + 重扫即可回滚（无外部副作用） |

## 4. 风险评估

| 风险 | 级别 | 缓解 |
|---|---|---|
| LLM 输出含投资结论 | 低 | _FORBIDDEN_OUTPUT 过滤 + review receipt |
| prompt injection | 低 | receipt 门（GP-003）+ 7 份均为公开券商报告 |
| API 费用 | 低 | 7 份 × ~2000 tokens ≈ 14K tokens，费用可忽略 |
| 数据泄露 | 无 | 紫金研报为公开信息（A 股年报/券商公开报告） |

## 5. 授权请求

请求 KD-08 授权以下操作：

1. 对 7 份紫金研报执行 normalize + LLM 摘要 + 分节提取
2. 处理在本地 wiki catalog 执行（非批量自动化，逐份处理）
3. 处理完成后更新 scenario registry（BR-01~26 status→passed + evidence_path）
4. 全程记录审计日志（LLM 调用/artifact 创建/receipt 生成）

## 6. 验收标准

- [ ] 7 份研报各有 normalized + summary + sections 3 个 artifact
- [ ] 每个 summary artifact 通过 validate_artifact（reusable=True）
- [ ] 每个 summary 有对应 prompt-injection review receipt
- [ ] scenario registry 中 BR-01~26 status=passed
- [ ] 无 _FORBIDDEN_OUTPUT 命中（LLM 输出无投资结论）
- [ ] LLM 调用次数 = 7（无重复/无跳过）

---

## 批准记录

- **批准人**：郑曾波（repo owner）
- **批准时间**：2026-09-03
- **批准内容**：对 7 份紫金研报执行语义处理（normalize + LLM 摘要 + 分节提取）；同时决定**取消生产 catalog 的 private_user 隐私分类**（所有根 public，文件可发外部 LLM，见 config/source_catalog.yaml 注释；GP-003 receipt 门仍强制生效）
- **执行状态**（2026-09-03）：
  - normalize：**7/7 completed**（normalized artifacts 全部 v2-bindable reusable=True）
  - review receipts：**7/7 written**（scan_text 全部 not_detected，source_sha256+policy_hash 绑定）
  - LLM summary：**6/7 completed**（长江/天风/国盛/民生/太平洋金铜/太平洋紫气）
  - 安全门拒绝：**1/7**（国联民生 2025 年报深度点评——LLM 输出复述评级/目标价触发 `_FORBIDDEN_OUTPUT`，3 次重试均拒绝。**正确 fail-closed，不绕过**）
  - sections：0（section_extractor 仅支持 annual/semi_annual/prospectus；broker_research 分节是已知产品缺口 BR-11~17）
  - LLM 调用记录：provider=minimax MiniMax-M3，逐份审计（content_hash/artifact_id 可查）
  - BR-01~26 回填：无法声称 passed（BR-01 需独立黄金集比对；BR-02~26 多数需研报分节/表格基础设施）——保持 blocked 如实记录

**等待 KD-08 批准后执行。**
