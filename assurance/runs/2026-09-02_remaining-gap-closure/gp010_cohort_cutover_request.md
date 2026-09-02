# GP-010 Cohort Cutover 授权申请：七份紫金研报语义处理

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

**等待 KD-08 批准后执行。**
