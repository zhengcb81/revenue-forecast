# ZR-701 工作单元卡（preflight）— F1 首卡：draft/formal 显式 artifact + 纯 prepare_forecast + ProcessingDemand 提交

- 领取时间：2026-08-19T20:56Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-701`，ZR-510 accepted + closure→ZR-701（phase=F_revenue_mining）；锁 ZR-701（owner=zr701-implementer，nonce 6b785ace…）。
- 依赖：ZR-001~206（✅ revenue 基线）、ZR-507（✅ wiki ProcessingDemand 契约）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F 首卡（F1 入口）：**单一 schema 真源 + generator→linter→engine 闭环 + 显式 Draft/Formal artifact + 原子发布 + source-preparation 提交 ProcessingDemand**（authoritative_execution_plan §8 F1）。现状：revenue_forecast.py 的 `run_forecast`（revenue_core）已是纯计算、`--validate-only` 已零写（无测试钉死）；publication_registry 只有 formal 发布；source_preparation 不提交 ProcessingDemand（执行计划："source-preparation 真正提交 ProcessingDemand"）。
2. **production entrypoint 是什么？** revenue `scripts/`：revenue_forecast.py（CLI 主入口）→ revenue_core.run_forecast（纯引擎）→ publication_registry（发布 receipt）→ source_preparation.prepare_source（上游处理）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 无显式 prepare_forecast 纯函数**：run_forecast 是 de facto 纯函数但无显式命名/契约测试（CLI 内联调用）。
   - **G2 validate-only 零写无钉死**：--validate-only 行为存在但无测试断言"零写"（无输出文件、无 publication registry 写入）。
   - **G3 无 Draft artifact**：publication_registry 仅 formal；draft（未验证）与 formal（已验证）无显式区分。
   - **G4 source_preparation 不提交 ProcessingDemand**：prepare_source 无 demand enqueue（ZR-507 契约未接入）。
4. **允许改哪些文件？** revenue：`scripts/revenue_forecast.py`（prepare_forecast 提取）、`scripts/publication_registry.py`（draft kind）、`scripts/source_preparation.py`（demand 提交）、新增 `scripts/processing_demand.py`（与 wiki ZR-507 同契约纯内存实现）+ 测试 `tests/test_zr701_f1_draft_formal.py`；revenue receipts/ZR-701/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema、跨仓 import（revenue 独立实现同契约）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-702~706（F1 后续）。本卡不做：矿山会计桥（ZR-610 等 F2）、真实 E2E（阶段 G）、可信回测/置信度（后续）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-510 accepted（closure.next=ZR-701；DAG 权威解锁 ZR-701）。
- [x] triplet 冻结：revenue（ZR-510 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：revenue_forecast.py main 内联 run_forecast（无 prepare_forecast 命名）；--validate-only 已存在（无零写测试）；publication_registry 无 draft kind；source_preparation 无 ProcessingDemand。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（prepare_forecast/发布 draft/ProcessingDemand 提交）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G4。
- **Acceptance criteria**：
  - **C1 纯 prepare_forecast（杀 G1）**：`prepare_forecast(data, *, collector=None) -> dict` 纯函数（包 run_forecast + validate_forecast_output，无 IO 副作用）；CLI main 改用之；确定性测试（同输入同输出）。
  - **C2 validate-only 零写钉死（杀 G2）**：测试断言 `--validate-only` 下（a）无输出/markdown 文件创建（tmp 目录空）、（b）publication registry 无写入（receipt 数不变）。
  - **C3 Draft/Formal 显式 artifact（杀 G3）**：publication_registry 支持 `draft`（未验证）与 `formal`（强验证）两类记录——draft 记录不含 validated_input_sha256（诚实未验证），formal 含（既有契约保持）；测试两类区分。
  - **C4 ProcessingDemand 提交（杀 G4）**：revenue 新增 `scripts/processing_demand.py`（与 wiki ZR-507 同契约：enqueue key 去重/claim 租约/heartbeat/complete/fail 退避/expire——纯内存 + clock 注入，同契约测试）；source_preparation.prepare_source 成功路径 enqueue（key=source 标识，kind="source_preparation"），重复准备 dedupe；测试。
  - **C5 原子发布（附加）**：formal 发布 receipt 与 artifact 强绑定（payload sha 一致）测试。
  - 质量门：revenue 全量 470+106 无回归；ruff clean；mypy 基线不新增错误；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、跨仓 import、修改 wiki ZR-507 契约 → 立即停止。

## Annex：F1 首卡判定矩阵

| 场景 | 期望 |
|---|---|
| prepare_forecast(valid data) | 返回 result dict（无 IO）；两次调用结果一致 |
| --validate-only | 零写（无文件创建、无 registry 写入） |
| publication_registry draft 记录 | 无 validated_input_sha256（未验证诚实） |
| formal 记录 | 含 validated_input_sha256 + payload sha 绑定 |
| prepare_source 成功 | enqueue demand（key 去重：重复准备不新增） |
| demand 生命周期 | claim/heartbeat/complete/fail 退避/expire（同 wiki 契约） |
