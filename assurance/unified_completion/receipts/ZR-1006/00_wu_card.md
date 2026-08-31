# ZR-1006 工作单元卡（preflight）— I：broker processing demand 最小 cohort

- 领取时间：2026-08-31T12:38Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1006`（ZR-1005 closure → ZR-1006）；锁 ZR-1006（owner=zr1006-implementer，nonce fbe39c47…）。
- 依赖：ZR-1004（四 root 小 cohort，accepted ✅）、ZR-1005（legacy artifact 分桶，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 第六卡——broker processing demand 最小 cohort（registry："七份紫金先 1→3→7；质量门/成本/SLO；失败不污染旧 artifact"）。现状缺口（RED）：七份紫金 broker 样本（golden corpus）在 production catalog 全部 active 且 artifact_count=0（2026-08-12 审计确认零 artifact/span/tag）；ZR-507/508 有 DemandQueue/DemandScheduler 机制但无"broker 1→3→7 最小 cohort + 质量门 + 成本/SLO + 失败隔离"组合验收。
2. **production entrypoint 是什么？** company-wiki `DemandQueue`（ZR-507 纯内存需求队列：enqueue/claim/heartbeat/complete/fail/expire）+ `DemandScheduler`（ZR-508：aging/deadline/cost budget）+ `llm_summarizer`（broker_research document_kind 透传，summary artifact 生成）；真实 catalog 只读。
3. **RED？** grep zr1006 → 零命中；ZR-507/508 测试无 broker cohort/1→3→7/质量门组合；golden corpus 7 份 broker 样本生产现状 = active + 零 artifact。
4. **允许改哪些文件？** company-wiki：`tests/contract/test_zr1006_broker_cohort.py`（新，9 tests）；revenue：receipts/ZR-1006/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog 写、LLM 调用、下载、网络。
5. **下一单元解锁？** ZR-1007（mine facts/model shadow，revenue 卡）。本卡不做：真实 production broker 处理（部署动作）、七份研报的 LLM 摘要生成（真实调用）。

## Acceptance criteria

- **C1 生产快照（只读）**：golden corpus 7 份紫金 broker 样本（changjiang/tianfeng/guosheng/minsheng/tpy×2/glms）在 production catalog 全部 `broker_research` + `active` + 0 artifact——诚实"待处理"状态。
- **C2 ramp 1→3→7**：DemandQueue+DemandScheduler 上 7 份 broker 按 1→3→7 波次处理，每波完成的 key 集合为严格 cohort 前缀；completed 为终态（同一 demand 不可再 claim/处理）。
- **C3 质量门**：仅可证明绑定的 artifact（真实文件存在 + schema_version 1.0 + source_sha256 匹配）可写；不可证明（hash 不匹配/文件缺失）→ 零 artifact 行。
- **C4 成本/SLO**：llm kind 预算耗尽暂停、reset 恢复（新 demand 可调度）；deadline urgency 提升 broker 有效优先级；aging 防止低优先 broker 饿死。
- **C5 失败隔离**：demand fail → backoff → terminal_failed 全程 catalog 行/hash 零变化（旧 artifact 不被污染）；重试成功的 demand 只写自己的新 artifact 行。
- **C6 质量门（卡级）**：company-wiki 相邻契约回归零回退、revenue 全量零回归（基线 896+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- production catalog 只读（C1 仅 SELECT）；队列机制纯内存（注入 clock）；temp catalog 仅用于 artifact 写语义演示；零网络、零下载、零 LLM；七份研报真实 LLM 处理留待部署（非本卡）。
