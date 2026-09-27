# CA-302 工作单元卡（preflight）— J：三类真实用户旅程终验

- 领取时间：2026-08-31T17:01Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-302`（CA-301 closure → CA-302）；锁 CA-302（owner=ca302-implementer，nonce f5fc2e09…）。
- 依赖：CA-301（clean checkout，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 J 第二卡——三类真实用户旅程终验（registry："从 revenue 入口重放紫金复杂 canary、第二异构矿企、非矿企；覆盖所有 roots、existing/partial/missing/stale/amended、worker、下载、第二次复用；每条八阶段 receipt、side-effect budget、输出/回溯/诚实 gap；任何公司特例或绕过 filing 链失败"）。现状缺口（RED）：三类旅程分项存在无终验组合。
2. **production entrypoint 是什么？** revenue `prepare_forecast`（draft/formal/replay）；`validate_publication_receipt`（receipt 链门）；company-wiki SourceResolver（真实 catalog 只读，missing fail-closed）；scripts/ 零硬编码扫描。
3. **RED？** glob tests/**/*ca302* → 零命中；无"三类旅程 + receipt 完整 + side-effect=0 + 无旁路"一体验收。
4. **允许改哪些文件？** revenue：新 `tests/test_ca302_three_journeys.py`；receipts/CA-302/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 registry 写（tmp 隔离）、下载、LLM、真实 catalog 写。
5. **下一单元解锁？** CA-303（架构硬编码终审，与 CA-302 并行允许）→ CA-304（R9 删除）。本卡不做：真实下载旅程（网络）、worker 真实处理（部署）。

## Acceptance criteria

- **C1 紫金 canary 旅程**：draft 零写 → formal → bit-identical replay；mine 贡献 reconcile（reconciled_modeled）；诚实 gap；缺失文档 fail-closed（production resolver MISSING）。
- **C2 第二矿企旅程**：纯金生产商（单层 100% 链、单货币）F2 链闭合（operation→terms→ownership→reconcile）+ engine 文档路径。
- **C3 非矿旅程**：trading 段 5 年正值（production engine）+ direct_growth 手算 100→110/121。
- **C4 receipt 链完整**：formal receipt 含 formal_output_mode/gate_ids/attestation 且 validate_publication_receipt 通过；draft 零注册（registry 仅 formal 的 1 条）。
- **C5 side-effect budget=0**：三类旅程（canary+replay+draft）registry 恰好 2 条 formal 条目、零 stray 文件。
- **C6 无旁路/无特例**：scripts/ git grep 紫金矿业/601899 → ZERO；三类旅程同 receipt schema（无公司分支）。
- **C7 质量门（卡级）**：相邻回归（ZR-709/609/CA-204）零回退、revenue 全量零回归（基线 982+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- registry 全部 tmp 隔离；真实 catalog 只读（missing fail-closed）；零网络、零下载、零 LLM；worker/下载真实旅程为部署动作（本卡验收引擎旅程语义）。
