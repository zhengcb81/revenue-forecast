# ZR-709 工作单元卡（preflight）— F2 合流：紫金五年预测用户旅程终验 fixture

- 领取时间：2026-08-22T13:50Z（本地 +0100）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-709`，ZR-713 accepted + closure→ZR-709；锁 ZR-709（owner=zr709-implementer）。
- 依赖：ZR-705~708、ZR-710~713、ZR-609、ZR-611 全部 accepted ✅（state.json 核对）。Registry 依赖列=ZR-705~708,ZR-710~713,ZR-609,ZR-611。
- base_triplet：revenue 86c8516（ZR-713 closure）、wiki 26a6b22、filing 5a1c18f；ZR registry hash 72c70eb6… 与冻结规范一致。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 合流终验——把 F1（generator/draft/formal/validate-only/publication 事务）与 F2 矿业链（operating units→commercial terms→ownership→elimination→reconciliation→schema 3.8 opt-in→confidence/backtest）接成一条**紫金五年预测用户旅程**：自动复用财报/研报且补齐依据可解释；mine/product 贡献与分部勾稽或诚实 gap；draft 可渲染、结果可重放。
2. **production entrypoint 是什么？** `scripts/source_preparation.py::prepare_source`（真实跨仓复用链，fake roots T1）→ `scripts/revenue_forecast.py::prepare_forecast`（draft/formal）→ `revenue_report.render_markdown` → `mine_year_operation/commercial_terms/asset_ownership/internal_flow/reconciliation/schema_optin` 契约模块 → `processing_demand.DemandQueue`。
3. **RED？** grep zr709/紫金 journey → 零命中：无任何测试把「source preparation 复用 → 五年矿业输入构建 → 分部勾稽/gap → draft 渲染 → formal 重放」串成一条旅程；各卡只有孤立验收。
4. **允许改哪些文件？** revenue：新 `tests/test_zr709_zijin_journey.py`；receipts/ZR-709/**、locks/ZR-709.lock.json、state.json、README 镜像、planning docs。禁止：产品代码语义改动、真实 catalog/root 写、下载、LLM 外发。（预期 test-only，与 ZR-609/ZR-611/ZR-708 同型）
5. **下一单元解锁？** F 阶段全闭（24/24）→ 阶段 G 首卡 ZR-802（组合旅程）。本卡不做：阶段 G 真实三 root E2E、T2 生产 catalog 访问。

## Acceptance criteria

- **J1 自动复用财报/研报，补齐依据可解释**：真实 `source_preparation.prepare_source` 子进程链在 fake wiki root 上命中年报（regulatory_filing）与研究沟通（company_release/investor_presentation 类）两类来源——reuse_receipt 逐项可解释（outcome/policy_hash/download_calls=0/parser_calls/llm_calls/artifact_read）；缺失文档不伪造，落 ProcessingDemand 队列（补齐路径 = 显式 demand，非编造数据）。
- **J2 mine/product 贡献与分部勾稽或诚实 gap（五年）**：FY2026–FY2030 五年输入（schema 3.8 opt-in + operating_units 七字段契约）；每矿×年经 derive_saleable_volume × commercial_terms（TC/RC/royalty/byproduct/FX）→ ownership 权益链 → internal flow 消除 → mine/product 贡献合计与 resource 模型 segment 收入 reconcile_layer 勾稽（reconciled_modeled）；无产量数据的分部走 fallback_segment_listing/gap_report 诚实 gap，绝不产量×价格冒充确认收入。
- **J3 draft 可渲染、结果可重放**：prepare_forecast(draft) 结果可直接 render_markdown（零发布注册）；formal 两次运行 result_sha256 位级一致（确定性重放）；publication registry 记录 formal 条目；snapshot create→validate 回放 PASS。

## 边界

- 不改产品代码（若发现真实缺口则按流程 RED 登记，最小修复需另行评估）；
- 不触真实 company-wiki catalog / Dropbox / dayu roots（T1 hermetic fixtures）；
- 不下载、无 LLM egress、不动用户 dirty 文件。
