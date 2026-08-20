# ZR-602 工作单元卡（preflight）— F2：asset facts basis 契约（resource≠reserve 语义 + ownership/标准/measurement date/单位归一）

- 领取时间：2026-08-21T08:50Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-602`，ZR-601 accepted + closure→ZR-602（phase=F_revenue_mining，F2 第二卡）；锁 ZR-602（owner=zr602-implementer，ttl 86400s）。
- 依赖：F1（✅ ZR-701~706/710）+ ZR-601（✅ asset facts 数学契约）。Registry 依赖列=ZR-601。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F2 第二卡：**asset facts basis 契约**——资产事实（resource/reserve/grade/capacity/permit）的计量基础必须显式声明且可审计：resource≠reserve 语义隔离、ownership basis（100%/权益/并表）、报告标准（reporting_standard）、measurement date 必填、单位一致性。ZR-601 已钉死储量 stock-flow 数学契约；本卡钉死事实的**basis 元数据层**（缺省 fail-closed，不伪造口径）。
2. **production entrypoint 是什么？** `scripts/forecast/segments.py::calculate_model_path`（驱动校验：missing/unsupported drivers）+ `scripts/contracts/document.py::validate_parameters`（参数 schema 门）+ `scripts/contracts/constants.py`（词汇真源）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 resource≠reserve 语义隔离无钉死**：segments.py 已拒绝跨模型驱动注入（`unsupported drivers` 探针实证：resource 拒 reserve 驱动、reserve_depletion 拒 resource 驱动），但无测试钉死"语义不可互换"；MODEL_SPECS 驱动词汇不相交无断言。
   - **G2 basis 元数据完全缺失（真实产品缺口）**：参数 schema（PARAMETER_REQUIRED 7 键）无 ownership_basis/reporting_standard/measurement_date 任何词汇；generate_input_template 无 basis 键；asset fact 参数无法声明"100%/权益/并表、标准、measurement date"——缺省不 fail-closed。
   - **G3 单位一致性缺失（真实产品缺口，基础版）**：unit 是自由字符串（探针：make_parameters 全 "test"），同一 asset fact 族驱动单位漂移（kt vs t）无一致性门；完整换算表归 ZR-610 会计 ADR（本卡只做一致性门 + 词汇）。
4. **允许改哪些文件？** revenue：`scripts/contracts/constants.py`（加性词汇）、`scripts/contracts/document.py`（basis 键完整性校验 + asset fact 族驱动参数 basis 必填）、`scripts/forecast/segments.py`（asset fact 族驱动 unit 一致性门）、`tests/test_models.py::make_parameters`（加性 basis 键支持）、新 `tests/test_zr602_asset_facts_basis.py`；revenue receipts/ZR-602/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM、单位换算表（归 ZR-610）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-603~608（F2 后续）。本卡不做：ownership/consolidation timeline（ZR-603）、表格抽取/冲突（ZR-604）、单位换算表与会计 ADR（ZR-610）、mine-year operations/commercial layer（ZR-605/606）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-601 accepted（closure.next=ZR-602；revenue closure commit 2ba0368）。
- [x] triplet 冻结：revenue（ZR-601 closure 提交后 2ba0368）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：
  - P1：`calculate_model_path` 对 extra driver 拒绝（"unsupported drivers for resource: opening_reserves" / "…for reserve_depletion: saleable_volume"）——resource≠reserve 语义隔离机制已存在。
  - P2：scripts 全仓 grep `ownership|consolidat|reporting_standard|measurement_date|basis` 零命中（仅 time_basis 无关）；PARAMETER_REQUIRED 无 basis。
  - P3：unit 无任何一致性/归一逻辑（document.py 仅要求 unit 非空字符串）。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（asset facts basis 契约：探针驱动修复 G2/G3 + 钉死 G1）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G2/G3 真实产品缺口；G1 机制已存在待钉死。
- **Acceptance criteria**：
  - **C1 resource≠reserve 语义隔离（杀 G1）**：resource 模型拒绝 reserve 驱动注入、reserve_depletion 拒绝 resource 驱动注入（ForecastInputError "unsupported drivers"）；MODEL_SPECS 驱动词汇不相交（resource ∩ reserve_depletion required = ∅）；asset fact 族模型清单注册为常量（零硬编码：resource/reserve_depletion 为通用矿业模型名）。
  - **C2 basis 契约（杀 G2）**：`ASSET_FACT_OWNERSHIP_BASES`（one_hundred_percent/equity_share/consolidated）与 `ASSET_FACT_BASIS_REQUIRED`（ownership_basis/reporting_standard/measurement_date）注册入 constants；参数携带 `basis` 键时必须为 dict 且三键齐全（ownership_basis ∈ 枚举、reporting_standard 非空、measurement_date ISO 合法），半成品/非法值 ForecastInputError；asset fact 族（resource/reserve_depletion）驱动参数 basis 必填（缺 basis → ForecastInputError）。
  - **C3 单位一致性（杀 G3 基础版）**：asset fact 族驱动参数的 unit 必须一致（同维度驱动 unit 归一后等价；归一 = 去空白/统一小写/显式前缀枚举），跨期/跨驱动单位漂移拒绝；换算表不实现（ZR-610 ADR）。
  - 质量门：revenue tests/ 全量无回归；ruff clean；ratchet 绿。
- **Stop conditions / handoff**：改模型公式语义、实现单位换算表、改 ModelSpec 契约、真实 catalog 写、下载、LLM → 立即停止。

## Annex：asset facts basis 判定矩阵

| 场景 | 期望 |
|---|---|
| reserve 驱动注入 resource 模型 | ForecastInputError（unsupported drivers） |
| resource 驱动注入 reserve_depletion 模型 | ForecastInputError |
| 参数带 basis 但缺 ownership_basis | ForecastInputError（半成品 fail-closed） |
| ownership_basis 非法枚举 | ForecastInputError |
| reporting_standard 空 | ForecastInputError |
| measurement_date 非 ISO/非法 | ForecastInputError |
| asset fact 族驱动参数缺 basis | ForecastInputError（必填） |
| asset fact 族驱动 unit 漂移（kt vs t） | ForecastInputError（一致性） |
| 非 asset fact 参数无 basis | 通过（加性不破坏既有） |
