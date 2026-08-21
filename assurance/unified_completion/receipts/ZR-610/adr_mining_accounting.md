# 通用矿业数据、单位、ownership/consolidation/internal-sales ADR
# ZR-610 Architecture Decision Record

- 日期：2026-08-22
- 状态：冻结（accepted）
- 范围：revenue-forecast 矿业模型链的会计与数据契约
- reviewer：独立会计 reviewer（reviewer-zr610-accounting-independent）

---

## 1. 逐矿贡献 = 模型估计，非披露事实

**决策**：revenue-forecast 中逐矿贡献（mine-level revenue contribution）是模型估计（model estimate），不是披露事实（disclosure fact）。

**理由**：
- 上市公司通常只在分部报告（segment reporting）中披露集团层面收入，逐矿贡献是非公开信息或需要假设推导。
- 模型驱动参数（depletion × recovery_rate × realized_price 等）来自公开数据 + 分析师假设，逐级推导后的逐矿贡献是估计值。
- 模型估计必须诚实标注（kind=analyst_assumption 或 reported_fact with explicit source），不得伪装为披露事实。

**规则**：
- 模型输出（calculate_model_path / calculate_registered_model）不携带"disclosed"标记——所有输出默认为 modeled。
- kind=reported_fact 的参数必须有 source_ids（来源），且来源必须可追溯。
- 逐矿贡献不用于审计或监管申报——仅供投资分析参考。

---

## 2. resource ≠ reserve 语义隔离

**决策**：resource（资源量）与 reserve（储量）在模型族中严格隔离，不可互换。

**实现**（ZR-602/601）：
- MODEL_SPECS 中 resource（saleable_volume × realized_price）与 reserve_depletion（opening_reserves/additions/depletion/closing_reserves/recovery_rate × realized_price）驱动词汇不相交。
- calculate_model_path 拒绝跨模型驱动注入（"unsupported drivers"）。
- 驱动维度：resource 使用 quantity（saleable_volume），reserve_depletion 使用 reserve_volume——两个独立维度。

**规则**：
- 矿业事实（AssetFact）必须声明 kind（resource / reserve / grade / capacity / permit），不可混用。
- resource 模型不接受 reserve 驱动，反之亦然。
- 同一资产的 resource 与 reserve 数据可并存，但必须分别建模、分别输出。

---

## 3. Basis 元数据必填

**决策**：资产事实参数必须声明 basis 元数据（ZR-602 加性契约——携带即强制完整）。

**basis 三字段**：
- `ownership_basis`：资产收入的口径基础
  - `one_hundred_percent`：资产收入按 100% 基础报告（集团份额需额外折算）
  - `equity_share`：收入已按权益法折算（apply_ownership_share 拒绝——防止 Kamoa/Porgera 双重折算）
  - `consolidated`：合并口径收入（consolidated 收入不在此层折算——合并报表顶层行已含 100% 子公司收入）
- `reporting_standard`：报告标准（如 JORC 2012 / NI 43-101 / PRC 储量标准等——非枚举，自由文本非空）
- `measurement_date`：计量基准日（ISO 日期——事实适用的截止时点）

**规则**：
- 参数携带 `basis` 键时必须完整合法（三字段齐全 + ownership_basis ∈ 枚举 + reporting_standard 非空 + measurement_date ISO 合法）——半成品/非法值 ForecastInputError。
- 缺少 `basis` 键的参数不受影响（加性兼容——存量输入无需迁移）。
- 全量必填的接入点由 ZR-605 MineYearOperation 输入合同或下游消费方在输入层强制。

---

## 4. Ownership Timeline（所有权时点）

**决策**：资产所有权有时效性——收购生效日前后适用不同份额。

**实现**（ZR-603）：
- ownership timeline = effective-dated entries：[{effective_date, ownership_fraction}, ...]
- lookup = latest entry with effective_date ≤ on_date
- 早于首条 effective_date → fail-closed（不隐式回溯——收购前不能假装有权益）
- period 内 fraction 变更 → 默认拒绝（不静默平均），显式 allow_pro_rata=True 才日加权

**链式权益**：
- effective_group_share(chain, on_date) = 多级连乘（集团 60% × 中间体 70% × 矿山 = 0.42）——一次性计算，防止 Kamoa/Porgera 双重折算。

**apply_ownership_share 语义表**（与 ZR-602 basis 枚举对齐）：
| basis | 行为 |
|---|---|
| one_hundred_percent | revenue × effective_share（折算为集团可归属收入） |
| equity_share | 拒绝（"ownership share already applied"——Kamoa/Porgera 防线） |
| consolidated | 拒绝（"consolidated basis revenue is not equity-discounted at this layer"） |

---

## 5. 单位归一与一致性

**决策**：同一 asset fact 族（resource / reserve_depletion）的驱动参数，同维度必须声明相同单位（归一化后等价）。

**实现**（ZR-602）：
- asset_ownership._check_asset_fact_unit_consistency：按 MODEL_DRIVER_DIMENSIONS 分组，归一化（strip+lower）后比较——kt vs t 跨驱动/跨期漂移拒绝。
- 换算表（kt↔t 等）不在本 ADR 范围——若需换算，由输入层在 prepare 时显式转换，不得在模型层隐式转换。

**规则**：
- 同维度驱动（如 reserve_depletion 的 5 个 reserve_volume 驱动）必须声明相同单位。
- 跨维度驱动（如 reserve_volume vs ratio vs revenue_per_unit）单位天然不同——无限制。
- 单位声明缺失（unit 为空）在 validate_parameters 已被拒绝（unit 是必填字段）。

---

## 6. 冲突保存与人工 Review

**决策**：同一事实（definition/period/unit/scenario 相同）的多个来源冲突时，不静默覆盖——保留双 assertion + resolution status。

**实现**（ZR-604）：
- 参数可携带 assertion_status（primary/secondary）标识来源角色
- 参数可携带 resolution_status（accepted/rejected/pending_review/under_review）跟踪 review 结果
- 冲突参数若均携带 resolution_status 且至多一个 accepted → 允许共存（冲突已解决）
- 否则保持原行为硬失败（backward compatible）

**规则**：
- 不静默覆盖旧值——两个来源均被保留，人工 review 决定取舍。
- resolution_status = accepted 的参数为权威来源——至多一个。
- 缺少 resolution_status 的冲突参数保持原行为 ForecastInputError（不隐式降级）。

---

## 7. 地区层级

**决策**：资产可声明地区信息（country/region），用于检索与分析。

**实现**（ZR-603）：
- segment 可携带 `geography` 键：{country: str required, region: str optional}
- geography_index(segments) → {country: {region|None: [资产名]}} 可检索索引
- 缺少 geography 的资产不可静默省略（fail-closed）

**规则**：
- country 非空 str 必填（当声明 geography 时）
- region 可选非空 str
- 地区信息用于检索与分析，不影响模型计算

---

## 8. 会计 ADR 边界

**本 ADR 冻结的决策**：
1. 逐矿贡献 = 模型估计（非披露事实）
2. resource ≠ reserve 语义隔离
3. basis 元数据三字段（ownership_basis/reporting_standard/measurement_date）
4. ownership timeline 时点语义 + 链式权益一次连乘
5. 单位一致性门（同维度驱动同单位）
6. 双 assertion + resolution status 冲突解决
7. 地区层级声明与检索

**本 ADR 不冻结的决策**（移交后续卡）：
- 单位换算表（kt↔t 等具体换算规则）→ ZR-611 或 ZR-605/606 按需
- 内部交易/elimination（internal sales/冶炼/贸易）→ ZR-607
- asset→segment→group reconciliation → ZR-608
- MineYearOperation 输入合同（volume/grade/recovery/payable/product/period/scenario）→ ZR-605
- 商业量价层（price/payability/TC-RC/premium/byproduct/FX/royalty）→ ZR-606

---

## 9. 独立会计 Reviewer 确认

- reviewer：reviewer-zr610-accounting-independent
- verdict：accepted（待确认）
- 确认内容：以上 8 条决策的会计合理性、与通用矿业会计实务的一致性、逐矿贡献=模型估计的诚实性声明。
