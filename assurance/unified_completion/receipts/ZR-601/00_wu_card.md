# ZR-601 工作单元卡（preflight）— F2：asset facts 矿业资产事实契约（储量 stock-flow/resource 行式）

- 领取时间：2026-08-21T00:40Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-601`，ZR-710 accepted + closure→ZR-601（phase=F_revenue_mining，F2 首卡）；锁 ZR-601（owner=zr601-implementer）。
- 依赖：F1（✅ ZR-701~706/710）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F2 首卡：**asset facts（矿业资产事实）**——储量/资源量的资产事实模型（reserve_depletion 的 stock-flow 平衡与年际连续性、resource 的行式 revenue 公式）作为可审计事实契约钉死；缺省资产事实诚实 fail-closed（不伪造）。model_registry 已有 _reserve_depletion/_spec 实现与 test_models 基础覆盖（balance/continuity 拒绝），但资产事实的数学断言（平衡/连续性/非负）与缺省路径无完整钉死。
2. **production entrypoint 是什么？** `scripts/model_registry.py`（ModelSpec 注册 + calculate_registered_model）→ revenue_forecast 模型族。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 资产事实数学断言不完整**：stock-flow 平衡（opening+additions-depletion==closing）与连续性（closing[t-1]==opening[t]）有测试但**非负性**（储量/产量/回收率不可负）与多期序列断言无钉死。
   - **G2 缺省诚实无完整测试**：resource 模型缺 saleable_volume、reserve_depletion 缺 opening_reserves 等缺省路径 fail-closed 无完整矩阵。
   - **G3 行式公式/模型族一致性无独立钉死**：resource 行式公式（saleable_volume×realized_price+other_revenue）与 reserve_depletion（depletion×recovery_rate×realized_price+other_revenue）的确定性公式无独立断言。
4. **允许改哪些文件？** revenue：新测试 `tests/test_zr601_asset_facts.py`；若探针发现真实缺口（如缺省路径不 fail-closed）则修 model_registry.py；revenue receipts/ZR-601/**。禁止：改模型公式语义（存量 spec 不变）、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-602~608（F2 后续）。本卡不做：会计 ADR（ZR-610）、ownership/consolidation、mine-year operations、asset→segment→group reconciliation（后续卡）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-710 accepted（closure.next=ZR-601）。
- [x] triplet 冻结：revenue（ZR-710 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：model_registry 有 resource/reserve_depletion spec + test_models 覆盖 balance/continuity 拒绝 + zero depletion；非负性/缺省矩阵/公式独立断言缺。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（asset facts 契约钉死 + 探针驱动修复）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 stock-flow 数学契约（杀 G1）**：reserve_depletion 多期序列（3 期）——每期 opening+additions-depletion==closing（平衡）、closing[t-1]==opening[t]（连续性）、全驱动非负（储量/回收率/价格 ≥0，违者 ForecastInputError）；探针验证现有实现是否强制非负。
  - **C2 缺省诚实（杀 G2）**：resource 缺 saleable_volume/realized_price、reserve_depletion 缺 opening_reserves/additions/depletion/closing_reserves/recovery_rate 任一 → ForecastInputError（fail-closed 不伪造）；参数驱动缺失同理。
  - **C3 公式/注册表一致（杀 G3）**：resource 行式公式与 reserve_depletion 公式独立断言（确定性计算值与手算一致）；model_registry 的 spec（drivers/units/formula 文本）与实现 calculator 一致（文本公式非空 + 计算结果匹配手算）。
  - 质量门：revenue tests/ 全量无回归；ruff clean；ratchet 绿。
- **Stop conditions / handoff**：改存量模型公式语义、改 ModelSpec 契约、真实 catalog 写、下载、LLM → 立即停止。

## Annex：asset facts 判定矩阵

| 场景 | 期望 |
|---|---|
| 3 期 stock-flow 平衡（opening+additions-depletion==closing） | 每期通过；违者 ForecastInputError |
| 连续性 closing[t-1]==opening[t] | 通过；违者 ForecastInputError |
| 负储量/负回收率/负价格 | ForecastInputError（非负强制，探针验证） |
| resource 缺 saleable_volume | ForecastInputError（不伪造） |
| reserve_depletion 缺任一驱动 | ForecastInputError |
| resource 行式公式手算 | 计算结果 == 手算（确定性） |
