# M01 · direct_growth — 冻结 oracle（运行前写定）

Card: M01（`execution_v2/card_M01.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M01/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 本文全部数值预期来自**手算**与**本 attempt 内独立脚本**
  `scripts/oracle_M01.py`（只用 Python `decimal`/`json` 标准库，不 import 产品任何模块），
  以及**已披露的真实年报原文**。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 本人未读取产品实现来"凑"预期：第 1 节公式来源是卡片正文
  （`card_M01.md` 第 8 行"单位/口径"、第 31 行手算）与 `implementation_plan.md` I-10 表的
  公式族描述；第 3 节实现入口锚点仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式 | `R[t] = R[t-1] × (1 + g[t])`，`R[0] := base_revenue`（即首年输出 = `base_revenue × (1+g[0])`） | `card_M01.md` L8、L31 |
| 注册公式串（预期） | `revenue[t] = revenue[t-1] * (1 + growth_rate[t])` | 卡片未给串；此串为实现锚点，冻结后核对 |
| 必填 driver | `growth_rate` | `card_M01.md` L9 |
| 可选 driver / 默认 | 无；`optional = ()`，默认 `{}` | `card_M01.md` L9 |
| 单位 | 基期收入与输出同币种同尺度（U = 统一货币单位）；`growth_rate` 为**年度小数**（无量纲） | `card_M01.md` L8 |
| 允许范围 | `growth_rate ∈ [-1, +∞)`（允许 -1 → 归零；禁止 < -1，禁止 -100% 以下的"复活"含义） | I-10 表 + `model_ledger.jsonl` 第 1 行 "现允许归零" |
| 维度 | `growth_rate: ratio`（注意：ratio 维度本身**不**蕴含 [0,1]，由 `growth_rate` 专属区间覆盖） | 卡片 + 计划 I-10 表 |
| 来源字段 | 基期收入（已披露收入或已审定基期锚点）；逐期增长率（管理层/研究假设） | 卡片 L35 |
| 驱动独立性 | 单驱动模型：`growth_rate` 直接决定收入，**不区分量/价/并购/汇率**；因此不能用于解释增长来源 | I-10 表 |
| 确认时滞 | 模型内无时滞项；`R[t]` 是**年度确认收入**，不是订单、GMV 或收款 | I-10 表 |
| 硬约束 | 输出逐年复利；不允许负收入输出；`years` 必须为连续递增整数财年 | 卡片 L42 |
| 不可识别参数 | **价格 / 销量 / 组合 / 并购并表 / 汇率 / 产能 / 库存** 全部不可识别；本模型无法把增长率分解为任何经营驱动 | I-10 表 |
| 生命周期适用 | 成熟稳定业务的短期兜底、收缩清退（`g = -1`）；**零基数商业化不适用**（0 × 任何数 = 0，不会复活） | `card_M01.md` L7、L37 |

## 2. 合成正例（positive）

输入（=`card_M01.md` L12-29 原文）：

```json
{"model_id": "direct_growth",
 "base_revenue": 200,
 "drivers": {"growth_rate": [0.1, -0.5, -1]},
 "years": [2027, 2028, 2029]}
```

手算（Decimal，精确）：

| 年 | 递推 | 输出 |
|---|---|---|
| 2027 | 200 × (1 + 0.1) = 200 × 1.1 | **220** |
| 2028 | 220 × (1 + (-0.5)) = 220 × 0.5 | **110** |
| 2029 | 110 × (1 + (-1)) = 110 × 0 | **0** |

**期望输出 = `[220, 110, 0]`**（卡片 L31 原文一致）。

- 输出长度 = 3 = `len(years)`；年份必须与 `years` 相同。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))`
  → 2027: 2.2e-7，2028: 1.1e-7，2029: 1e-9。作者独立计算，未取整后再比。
- 附加维度断言：`growth_rate[2] = -1` 时输出必须**恰为 0**（不是负数、不是 NaN、不被拒）。

## 3. 运行负例 A（卡片专属）

在上述输入中**只**替换 `drivers` 为 `{"growth_rate": [-1.01, -0.5, -1]}`：

- 预期：`ModelRegistryError`（`growth_rate < -1` 越出 `[-1, inf)`）。
- 通过判据：**目标异常类型是 `ModelRegistryError`**。
  `ImportError` / `FileNotFoundError` / `TypeError`（含 import 期错误）**不得**计为通过。
- 反例语义：`-1.01` 会使收入变成负数，"负收入"在通用模型中被拒绝；
  卡片 L37 要求不能把该情形当作可通过。

## 4. 公共负例 N01–N05（`common_model_cards.md` L26-30）

首个必填 driver = `growth_rate`。每个负例用**新的 deepcopy 独立输入**，互不共享可变对象。

| 例 | 变换 | 冻结预期 | 备注 |
|---|---|---|---|
| N01a | `growth_rate[0] = True` | `ModelRegistryError` | 不得由 JSON 解析器代拒（用内存输入，不经 JSON） |
| N01b | `growth_rate[0] = float('nan')` | `ModelRegistryError` | 非有限 |
| N01c | `growth_rate[0] = float('inf')` | `ModelRegistryError` | 非有限 |
| N01d | `growth_rate[0] = float('-inf')` | `ModelRegistryError` | 非有限（且越下界） |
| N02 | `growth_rate = []` | `ModelRegistryError` | 路径长度 ≠ `len(years)` |
| N03 | 删除 `growth_rate` | `ModelRegistryError` | 缺必填字段 |
| N04 | 增加 `unknown_driver = [1,1,1]` | `ModelRegistryError` | 未知字段 |
| N05a | `years = []` | `ModelRegistryError` | 年度 |
| N05b | `years = [True, 2028, 2029]` | `ModelRegistryError` | bool 不是财年 |

## 5. 连续性（continuity）负例

卡片 L43："有 continuity_case 则先验证两年 positive 再应用断裂 patch"。
`direct_growth` 是**流量/增长率模型，不是存量桥**（无 opening/closing 对账项），
因此"存量断裂"不适用；本卡适用的是**跨年增长率语义连续性**：

- Continuity positive：`base_revenue=100`，`growth_rate=[0.1, 0.05]`，`years=[2027,2028]`
  → 手算 `[110.0, 115.5]`（100×1.1=110；110×1.05=115.5）。此例**先**运行通过。
- Continuity 断裂 patch：`years=[2027,2029]`（跨年不连续，缺 2028）
  → 预期 `ModelRegistryError`（财年必须连续）。
- 存量桥资格：对 `direct_growth` 记为 **not_applicable_with_reason**
  （该模型没有期初/期末存量桥，I-10"存量无法锚定基期"停止条件对应 STOP_BRIDGE 不适用；
  但"基期锚点"仍必须在 D 资格中提供，见第 7 节）。

## 6. 数值独立性验证（本 attempt 独立脚本）

`scripts/oracle_M01.py` 用 `decimal.Decimal` 逐项复算第 2、5 节的数值，
并把结果写 `evidence/M01/oracle.json`；其 `harness_sha256` 与产品源码 hash 一并入
`source_manifest.json`。若 oracle 脚本 import 产品模块，视为本卡失败。

## 7. 披露映射（D 资格的最小要求：至少一份实际披露）

本卡 D 步骤要求 `per_driver_disclosure_mapping`：逐字段原文、原单位、转换、参数 ID、期间、范围。

**基期锚点**：紫金矿业集团股份有限公司 FY2024 已披露营业收入
`303,639,957,153 元`（来源与页码见 `evidence/M01/disclosure_mapping.json`）。
**增长率依据**：同一报告期"本期比上年同期增减(%) = 14.96"（= 公司自己披露的同比口径），
以及 FY2025 实际 `349,079,082,852 元`。

**重要边界（不得越界宣称）**：
- 上述是**已结束期间的已披露事实**，用于 *historical_mapping_probe*（低/中/高三键同值接线），
  **不是**三情景预测，**不是**准确性证据。
- 用 FY2024 基期 + 公司披露的 14.96% 增长率**预测** FY2025 时，
  独立复算预测值 = `303,639,957,153 × 1.1496 = 349,064,494,744.53 元`，
  而 FY2025 实际披露 = `349,079,082,852 元`，**残差 = -14,588,107.47 元**
  （公式预测偏低 0.0042%）。该残差**否证**"direct_growth 可作真实预测"的主张：
  单一增长率不能表达量/价/并购/汇率/权益产量与内销抵销（I-10 表"并购/汇率分桥"与"内销抵销"）。
  因此本卡的**公式资格 ≠ 准确性资格**，本卡不授予 accuracy。

## 8. 拒绝条件（本卡必须记录并执行）

| ID | 拒绝条件 | 冻结预期 |
|---|---|---|
| R1 | `growth_rate < -1` | `ModelRegistryError` |
| R2 | `growth_rate` 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` |
| R3 | 缺 `growth_rate` | `ModelRegistryError` |
| R4 | 未注册 driver | `ModelRegistryError` |
| R5 | `years` 为空 / 非连续 / 非整数财年（含 `True`） | `ModelRegistryError` |
| R6 | 非有限值（`nan`/`inf`/`-inf`，含 bool 冒充数值） | `ModelRegistryError` |
| R7 | 输出为负收入 | `ModelRegistryError`（由 -1.01 反例覆盖） |
| R8 | 零基数商业化用本模型"复活"收入 | **业务拒绝**：`base_revenue=0` 时任何 `g` 都得 0，需改用经营模型；不得当适配通过 |
| R9 | 用一条恒定 CAGR 掩盖周期/转型 | **业务拒绝**：见第 7 节残差，须记 `special_review` |

## 9. 三种资格（本卡只填 formula）

- `formula`：**由本卡 A–C 结果决定**（见 `evidence/M01/qualification.json`）；实现者不自签 accepted。
- `disclosure_adaptation`：保持 **unmapped**。理由：D 需逐字段 `per_driver_disclosure_mapping`
  经行业/会计 reviewer 签署，且需"一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅"；
  本 attempt 只提供最小披露映射与历史对账证据，未获独立审阅，**不得**填通过。
- `accuracy`：保持 **unproven**。理由：F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），
  本卡无该设计；第 7 节残差本身即否证性证据，不是准确性证明。

## 10. 停止条件自检（卡片 L48-53）

- 若 positive 不等或应拒绝的负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 若披露缺出处/单位/期间/总净额不明 → `STOP_DISCLOSURE_ADAPTATION`（本卡披露来源齐备）。
- 存量桥：**not_applicable**（第 5 节理由）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计；不作准确性主张）。


---

## 修订 r2（独立复审后追加，非重写）

本节由修订 r2 追加。**上方正文（v1 冻结版）逐字未改**；本节只补充说明与更正索引。
本节追加前的 `oracle.md` sha256 = `88635eb46df3c3d13f6ac0bc9af884d1b8d92aac50c6f7703c2f29a7a227d99f`（mtime 2026-09-20 01:15:15），追加后 hash 见
`evidence/M01/source_manifest.json` 的 `oracle_versions` 索引。

- **F-M01-01（首跑证据与版本溯源）**：首跑 `stderr` 已被成功重跑覆盖，**如实记为不可恢复**；
  首跑命令、rc=1 与 `KeyError: 'continuity'` 回溯的出处见
  `evidence/M01/first_run_forensics.json`（明确标注为会话转录捕获，非原始文件）。
  oracle 脚本 v1 由已记录的**单token改动**逆推重建，存为
  `scripts/oracle_M01.v1.reconstructed.py`（状态 RECONSTRUCTED，非原始字节），
  v1/v2 的 sha256 与 `oracle.md` 各版时间戳一并登记在 `source_manifest.json` 的 `oracle_versions`。
  **诚实缺口**：`oracle.md` 首冻版 hash 当时未记录（source_manifest 在重跑后才生成），无法证明
  "运行前冻结版本未被按结果回改"；本节只保证 v1 正文未被改写。
- **F-M01-02（退出码无效）**：`run_card.py` 与 `run_M01.py` 的 `return 0` 已改为
  verdict-carrying：rc=0 仅当 positive 在容差内、连续性正例通过且**全部**负例被
  `ModelRegistryError` 拒绝；rc=2 表示 harness 未产出裁决（**可达**：positive 输入损坏使产品抛错时触发）；rc=3 表示裁决为负；rc=1 表示 guard 之外的 harness 缺陷直接抛出。详见 `review.md` 的 r3 更正面。
  重跑后的新 raw rc 见 `evidence/M01/revision_r2.json`。
- **F-M01-03（交付目录/编码）**：已补 `after/`（复跑 hash）、`recovery/README.md`（NA 理由）、
  `changes.diff`（无产品改动声明）；`before/git_status_revenue-forecast.txt` 已重存为 UTF-8。
- **F-M02-01（待裁定）**：本卡不受影响（M01 的 `_direct_growth` 真实使用 `base_revenue`），
  跨模型一致性问题记在 M02 的 `handoff.json.open_questions`，等待 owner/专业裁定。

### r2 未改动的内容（防止误读为"为过审而改"）

- 正例/负例预期、容差、披露映射数值、拒绝条件、停止条件、三资格结论**一律未改**。
- 公式与阈值未放宽；`formula` 仍为 `review_pending`（未自签 accepted）。
