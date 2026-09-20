# M26 · store_cohorts — 冻结 oracle（运行前写定）

Card: M26（`execution_v2/card_M26.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M26/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 第 1、2、3、4 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M25_M28.py`（sha256 `d443b5d5bcf5f49f8f442df71b99f774a74422d393f038b9dca14bbe9a6a6e5e`）
  用 Python 标准库（`decimal`/`json`/`hashlib`）复算。该脚本**不 import** 产品任何模块
  （`model_registry` / `model_extensions` 均不出现），自检见 `evidence/M26/oracle_selfcheck.json`
  （`product_import_present = false`）。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M26.md` L8「店数桥；新店生产率为成熟店倍数，可大于1；收入U/成熟店年」与
  L48 原文手算「20+5−2=23；成熟暴露20−1=19；新店暴露5×0.4×0.75=1.5；20.5×10=205」。
  实现入口 `scripts/model_registry.py:308`、注册 `scripts/model_extensions.py:190` 仅在冻结之后
  用于定位调用点；本卡公式串是从卡片与手算独立写出的，运行后再与实现的公式串逐项比对。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式 | `收入 = (期初店数 − 闭店数×闭店损失系数 + 新店数×新店收入系数×新店生产率) × U/成熟店年` | `card_M26.md` L8、L48 |
| 店数桥（必须先成立） | `期末店数 = 期初店数 + 新店数 − 闭店数`；跨年 `期初(t) = 期末(t−1)` | `card_M26.md` L48、L118 |
| 必填 driver | `opening_stores`、`new_stores`、`closed_stores`、`closing_stores`、`new_store_revenue_fraction`、`closure_lost_fraction`、`new_store_productivity`、`annual_revenue_per_mature_store` | `card_M26.md` L9 |
| 可选 driver / 默认 | 无（`optional = ()`，卡片 L9 写「可选默认：`{}`」） | `card_M26.md` L9 |
| 单位 | 店（store）；`new_store_revenue_fraction`/`closure_lost_fraction` 无量纲比例；`new_store_productivity` 为「新店/成熟店」倍数；`annual_revenue_per_mature_store` = U/成熟店年；输出 = U | `card_M26.md` L8 |
| 量纲 | 店 × 倍数 × (U/店) = U | 量纲自检 |
| 语义域 | 四个店数 driver 为 `quantity` 维（下界 0）；`new_store_revenue_fraction`、`closure_lost_fraction` 为 `ratio` 维 → [0,1]；`new_store_productivity` 虽为 `ratio` 维但卡片 L8 明示**可大于 1**，故实现必须给它显式上界 | `card_M26.md` L8 + 通用契约 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；`closed_stores` 不得超过期初店数；收入非负 | 通用契约 |
| 业务口径 | 新店翌年归入期初成熟店是简化；多年爬坡不能默认已覆盖，需 `special_review` | `card_M26.md` L54 |

## 2. 合成正例（positive）

输入（=`card_M26.md` L12-46 原文）：

```json
{"model_id": "store_cohorts", "base_revenue": 0,
 "drivers": {"opening_stores": [20], "new_stores": [5], "closed_stores": [2],
             "closing_stores": [23], "new_store_revenue_fraction": [0.4],
             "closure_lost_fraction": [0.5], "new_store_productivity": [0.75],
             "annual_revenue_per_mature_store": [10]},
 "years": [2027]}
```

手算（逐步，未取整）：

1. 店数桥：20 + 5 − 2 = **23**（= 冻结的 `closing_stores`，桥成立）。
2. 成熟店暴露：20 − 2×0.5 = 20 − 1 = **19**。
3. 新店暴露：5 × 0.4 × 0.75 = **1.5**。
4. 收入：(19 + 1.5) × 10 = 20.5 × 10 = **205**。

**期望输出 = `[205]`**（与卡片 L48 原文一致）。
- 输出长度 = 1 = `len(years)`；年份应与 `years` 相同（`years` 长度、输出长度、输出字段集三项都断言）。
- 容差：`abs(actual − expected) <= 1e-9 × max(1, abs(expected))` = 2.05e-7。

## 3. 默认值案例（defaults）

本卡 `optional = ()`、`defaults = {}`，**没有**可选 driver，因此不存在"省略后取默认"的案例。
可运行且有意义的 defaults 案例是**全零显式输入**：

```json
{"model_id": "store_cohorts", "base_revenue": 0,
 "drivers": {"opening_stores": [0], "new_stores": [0], "closed_stores": [0], "closing_stores": [0],
             "new_store_revenue_fraction": [0], "closure_lost_fraction": [0],
             "new_store_productivity": [0], "annual_revenue_per_mature_store": [0]},
 "years": [2027]}
```

手算：桥 0+0−0=0 成立；成熟暴露 0−0=0；新店暴露 0×0×0=0；收入 (0+0)×0 = **0**。

**期望输出 = `[0]`**，长度 1。
- 该案例证明"零"必须显式给出，本卡不主张"缺披露可填零"（`common_model_cards.md` L22）。**不 gating**。

## 4. 连续性案例（continuity）

`store_cohorts` 是**存量桥模型**（`EXTENSION_OPENING_BALANCES` 中有
`base_stores_parameter_id` / `opening_stores` / `quantity`），故 STOP_BRIDGE 的连续性检查**适用**，
不得标 not_applicable。

- Continuity positive（= `card_M26.md` L60-107 原文）：

```json
{"years": [2027, 2028],
 "drivers": {"opening_stores": [20, 23], "new_stores": [5, 0], "closed_stores": [2, 0],
             "closing_stores": [23, 23], "new_store_revenue_fraction": [0.4, 0.4],
             "closure_lost_fraction": [0.5, 0.5], "new_store_productivity": [0.75, 0.75],
             "annual_revenue_per_mature_store": [10, 10]}}
```

  手算：FY2027 同第 2 节 = **205**。
  FY2028：桥 23 + 0 − 0 = 23 = 期末（成立），且 期初(2028)=23 = 期末(2027)（成立）；
  成熟暴露 23 − 0 = 23；新店暴露 0×0.4×0.75 = 0；收入 23 × 10 = **230**。
  期望 = `[205, 230]`（与卡片 L103-107「手算期望为230」一致）。此例**先**运行通过。
- Continuity 断裂 patch（= `card_M26.md` L108-118 原文）：
  `opening_stores=[20, 24]`、`closing_stores=[23, 24]`。
  两年**各自**平衡（20+5−2=23；24+0−0=24），但 期初(2028)=24 ≠ 期末(2027)=23 → 预期
  `ModelRegistryError`（连续性）。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `opening_stores`。每个负例用**新的 deepcopy 独立输入**，互不共享可变对象；
全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 | 说明 |
|---|---|---|---|
| NEG-CARD | `closing_stores = [24]`（卡片 L50 原文负例） | `ModelRegistryError` | 桥 20+5−2 = 23 ≠ 24，库存桥不成立 |
| N01a | `opening_stores[0] = True` | `ModelRegistryError` | bool 不是数值 |
| N01b | `opening_stores[0] = float('nan')` | `ModelRegistryError` | 非有限 |
| N01c | `opening_stores[0] = float('inf')` | `ModelRegistryError` | 非有限 |
| N01d | `opening_stores[0] = float('-inf')` | `ModelRegistryError` | 非有限 |
| N02 | `opening_stores = []` | `ModelRegistryError` | 路径长度 ≠ 1 |
| N03 | 删除 `opening_stores` | `ModelRegistryError` | 缺必填 |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError` | 未知字段 |
| N05a | `years = []` | `ModelRegistryError` | 年度域 |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` | True 不是财年 |
| CONT-BREAK | 第 4 节断裂 patch（基于 continuity_positive，先验 positive） | `ModelRegistryError` | 跨年连续性 |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；
`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（drivers/years 不变） | 输出与正例**相同** | `_rowwise` 丢弃 `base_revenue`；设计观察，不作为通过条件 |
| OBS-PRODUCTIVITY-BOUND | `new_store_productivity = 1.5` | **不设预期、不设判定** | 卡片 L8 明示新店生产率**可大于 1**；本驱动维度是 `ratio`，若只按 `ratio` 默认域 [0,1] 就会被误拒。探测目的正是把"实现是否给了显式上界"这件事记成可核事实，而不是把它当作通过条件 |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L48 给出算式与手算 205，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["store_cohorts"].formula`，与第 1 节公式逐项比对；若不一致，**记录差异**而不是
修改期望值。特别核对第 1 节与实现是否都把 `new_stores × new_store_revenue_fraction ×
new_store_productivity` 三项相乘（而非把生产率当作成熟店收入的一部分）。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | 店数桥 `期初+新店−闭店 ≠ 期末` | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 跨年 `期初(t) ≠ 期末(t−1)` | `ModelRegistryError` | 是（CONT-BREAK） |
| R3 | 闭店数超过期初店数 | `ModelRegistryError` | 否（本卡未设例；见第 9 节） |
| R4 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R5 | 缺必填 driver / 未知 driver | `ModelRegistryError` | 是（N03、N04） |
| R6 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R7 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R8 | `new_store_productivity < 0` | `ModelRegistryError` | 否（本卡未设例；见第 9 节） |
| R9 | 新店翌年归入期初成熟店的简化、多年爬坡 | **业务拒绝**：需 `special_review` | 否（不是运行时契约） |
| R10 | 存量无法锚定基期（无 `base_stores_parameter_id`） | **业务拒绝**：STOP_BRIDGE | 否（披露侧） |

## 9. 未覆盖面（诚实声明，供 reviewer 攻击）

- **R3（闭店数超过期初店数）未被本卡任何负例打到**：NEG-CARD 的拒绝来自**店数桥**（R1），
  不是"闭店超过期初"这条专属上限。要覆盖 R3，需要一个 `closed_stores=[21]` 且
  `closing_stores=[4]`（使桥仍然成立）的例；本卡**未运行**该例，留给 reviewer 作为
  未用于编写修复的保留案例。
- **R8（新店生产率为负）未被本卡负例打到**。
- 本卡不重写公式：无独立反例与经审定规格时保留已修实现（`card_M26.md` L148）。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M26/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，
  且需"一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅"；本 attempt 不产出 D 的签署件。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计；该设计不存在；本卡不作准确性主张。

## 11. 停止条件自检（`card_M26.md` L131-136）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥（本卡适用）：连续性不成立 → `STOP_BRIDGE`。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。
