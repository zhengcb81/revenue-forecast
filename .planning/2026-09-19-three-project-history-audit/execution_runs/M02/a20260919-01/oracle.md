# M02 · direct_revenue — 冻结 oracle（运行前写定）

Card: M02（`execution_v2/card_M02.md`），Parent I-10。Attempt `execution_runs/M02/a20260919-01`。
本文在**任何产品代码运行之前**写定；写入后不得为贴合结果而修改。

## 0. 独立性声明

- 全部数值预期来自**手算**与独立脚本 `scripts/oracle_M02.py`（仅 `decimal`/`json` 标准库，
  **不 import 产品任何模块**），以及**已披露的年报原文**。
- **绝不**调用 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 实现入口仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式 | `R[t] = revenue[t]`（逐项直接复制；`base_revenue` 被**忽略**） | `card_M02.md` L8、L31 |
| 注册公式串（预期） | `revenue[t] = direct_revenue[t]` | 卡片未给串；冻结后核对 |
| 必填 driver | `revenue` | `card_M02.md` L9 |
| 可选 driver / 默认 | 无；`optional = ()`，默认 `{}` | `card_M02.md` L9 |
| 单位 | 收入为**年度确认金额 U**，同币种同尺度；**不是订单、GMV、保费或收款** | `card_M02.md` L8 |
| 允许范围 | 每个值有限且 `>= 0`（dimension `revenue` → `[0, +inf)`）；负值拒绝 | I-10 表 + `model_ledger.jsonl` 第 2 行 "直接入口现拒绝非有限值及负值" |
| 维度 | `revenue: revenue`（金额，非比率、非数量） | 卡片 |
| 来源字段 | 已披露/已审定收入定义、期间、原始出处、路径估计依据、未拆分原因 | `card_M02.md` L35 |
| 驱动独立性 | **无驱动**：模型不从任何经营量推导收入，因此不提供增长因果解释 | I-10 表 |
| 确认时滞 | 模型内无时滞项；`revenue[t]` 即该财年确认收入，等于输入值 | I-10 表 |
| 硬约束 | 输出长度 = `len(years)`；`years` 连续递增；`base_revenue` 对输出无影响 | 卡片 L42 |
| 不可识别参数 | 所有经营驱动（量、价、产能、客户、backlog…）均不可识别；**收入本身的合理性不可由模型检验** | I-10 表 |
| 适用 | 各阶段**有证据**的兜底；尤其复杂会计收入（如 IFRS 17、受监管收入）尚不可安全拆分时 | `card_M02.md` L7 |

## 2. 合成正例（positive）

输入（=`card_M02.md` L12-29 原文）：

```json
{"model_id": "direct_revenue", "base_revenue": 0,
 "drivers": {"revenue": [80, 0, 120]}, "years": [2027, 2028, 2029]}
```

手算：逐项复制 → **期望输出 `[80, 0, 120]`**（卡片 L31 原文一致）。

- 长度 3 = `len(years)`。
- 容差 `1e-9 × max(1, |expected|)`：2027/2028/2029 分别为 8e-8、1e-9、1.2e-7。
- 维度断言：`revenue[2] = 0` 时必须保留为 **0**，不得被当成缺失而填默认（本模型无默认）。
- `base_revenue = 0` 是**刻意**的：证明 `base_revenue` 不参与输出（对照实验见第 5 节）。

## 3. 运行负例 A（卡片专属）

只替换 `drivers` 为 `{"revenue": [80, -1, 120]}` → 预期 `ModelRegistryError`。
通过判据：目标异常类型必须是 `ModelRegistryError`；`ImportError`/`FileNotFoundError` **不得**计为通过。
经济语义：负营业收入在通用模型中不接受；若真实业务（如银行）披露落在契约外，
应**停适配并由专业 reviewer 审定**，禁止裁零或改口径造通过（`common_model_cards.md` L11）。

## 4. 公共负例 N01–N05

首个必填 driver = `revenue`。每例新的 deepcopy 独立输入，内存构造（不经 JSON 解析器）。

| 例 | 变换 | 冻结预期 |
|---|---|---|
| N01a | `revenue[0] = True` | `ModelRegistryError` |
| N01b | `revenue[0] = float('nan')` | `ModelRegistryError` |
| N01c | `revenue[0] = float('inf')` | `ModelRegistryError` |
| N01d | `revenue[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `revenue = []` | `ModelRegistryError` |
| N03 | 删除 `revenue` | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1,1,1]` | `ModelRegistryError` |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True, 2028, 2029]` | `ModelRegistryError` |

## 5. 连续性 / 对照实验

`direct_revenue` 是**纯流量直给**模型，没有期初/期末存量桥，因此存量桥资格为
**not_applicable_with_reason**。本卡适用的"连续性"是**年度路径语义**：

- Continuity positive：`revenue = [50, 60]`，`years = [2027, 2028]` → 手算 `[50, 60]`，先运行通过。
- Continuity 断裂 patch：`years = [2027, 2029]` → 预期 `ModelRegistryError`（财年必须连续）。
- **对照实验（base 无关性，先冻结预期）**：同一 `drivers`，把 `base_revenue` 从 `0` 改为 `999`
  → 预期输出**不变**，仍为 `[80, 0, 120]`。若 base 改变了输出，即为公式与卡片口径不符。
- **探索性（非通过/失败判据）**：`base_revenue = -5` 的实际行为。契约预期按
  `calculate_registered_model` 语义应为 `ModelRegistryError`（base 不得为负）；无论观察结果如何，
  都作为**设计观察**记录并交 reviewer，因为本模型完全不使用 `base_revenue`，
  "忽略的字段是否仍须满足域约束"是一个需要专业决定的语义问题（见 `decision.md` DEC-M02-3）。

## 6. 拒绝条件

| ID | 拒绝条件 | 冻结预期 |
|---|---|---|
| R1 | 任一 `revenue` 值为负 | `ModelRegistryError` |
| R2 | 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` |
| R3 | 缺 `revenue` | `ModelRegistryError` |
| R4 | 未注册 driver | `ModelRegistryError` |
| R5 | `years` 空/非连续/非整数（含 `True`） | `ModelRegistryError` |
| R6 | 非有限或 bool 冒充数值 | `ModelRegistryError` |
| R7 | **业务拒绝**：来源或直接估计依据不明 | 必须停止；"公式简单不增加信心"（卡片 L37），记 `STOP_DISCLOSURE_ADAPTATION` |
| R8 | **业务拒绝**：把订单/GMV/保费/收款当作收入填入 | 口径错误；`revenue` 只能是已确认收入 |

## 7. 披露映射（至少一份实际披露）

- **实体**：紫金矿业集团股份有限公司；**口径**：合并营业收入（年度确认金额）。
- **期间**：FY2025（2025-01-01 至 2025-12-31）。
- **原文**：FY2025 年报 P15「主要会计数据」表，行「营业收入」，列「2025 年」= `349,079,082,852` 元。
- **出处**：`cninfo:1225023658`，PDF sha256 `01819e1c…`（见 `disclosure_mapping.json`）。
- **对账**：`direct_revenue` 把已披露收入原值填入 → 重建值 = 披露值，残差恒为 0。
  **该残差为 0 是构造性的、不含信息量**：它只证明"复制"动作正确，**不能**证明收入的来源、
  期间、总净额或口径正确，也**不构成**准确性证据。必须在 `historical_reconciliation.json`
  与 `qualification.json` 中明写此点，防止被读成"对账通过 ⇒ 预测可用"。
- **精度与单位**：单位为元、尺度 1；输入用 `float`（`349079082852.0`，2^53 ≈ 9.0e15，
  该值 < 2^53，故 **float 可精确表示**，无舍入误差）。

## 8. 三种资格

- `formula`：由 A–C 结果决定；实现者不自签 accepted。
- `disclosure_adaptation`：**unmapped**。D 需行业/会计 reviewer 逐字段签署，
  且需"一个已结束期间收入对账 + 生产 forecast 入口映射经独立审阅"；本 attempt 只交最小映射。
- `accuracy`：**unproven**。F 需 I-12 冻结设计；且本模型无驱动，
  第 7 节零残差**不构成**任何准确性证据。

## 9. 停止条件自检

- 正例不等或负例未被拒 → `STOP_FORMULA`，先记录反例，不改实现。
- 披露缺出处/单位/期间/总净额不明 → `STOP_DISCLOSURE_ADAPTATION`（本卡来源齐备）。
- 存量桥 → **not_applicable**（第 5 节理由）。
- 准确性 → `STOP_ACCURACY`（无 I-12 设计，不作准确性主张）。
