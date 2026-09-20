# M09 · resource — 冻结 oracle（运行前写定）

Card: M09（`execution_v2/card_M09.md`）；Parent I-10；状态 planned；调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M09/a20260919-01`；model_id: `resource`。
入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；
注册：`scripts/model_registry.py:229`。
本文件在**任何产品代码运行之前**写定；写定后不得为贴合运行结果而修改。

## 0. 独立性与口径声明（最重要）

- 第 2–6 节全部数值预期来自**手算**（见每处 `hand_work`），由本 attempt 内独立脚本
  `scripts/oracle_cards_M09_M12.py` 用 Python 标准库（`argparse`/`hashlib`/`json`/`os`/`decimal`）复算，
  生成 `evidence/M09/oracle.json`。该脚本**不 import** 产品任何模块
  （`model_registry` / `model_extensions` 均不出现在 import 行里）；自检见
  `evidence/M09/oracle_selfcheck.json` 的 `product_import_present=false`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 运行器 `scripts/run_card.py` 只调用一个产品入口 `calculate_registered_model(**input)`，
  expected 只从 `evidence/M09/oracle.json` 读取。
- 容差 `abs(actual-expected) <= 1e-9*max(1,abs(expected))`；先比结构/长度/字段集，再逐值比数值。
- 公式出处：`card_M09.md` L6（入口/注册）、L8（单位/口径）、L9（必填/可选）、L33（手算 30×4+2=122）；
  公共规则见 `execution_v2/common_model_cards.md` L15-32。

## 1. 公式 / 单位 / 口径（冻结）

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 已售可结算数量 × U/同数量单位 + 其他收入` | `card_M09.md` L8 |
| 必填 driver | `saleable_volume`、`realized_price` | `card_M09.md` L9 |
| 可选 driver / 默认 | `other_revenue` 默认 `0` | `card_M09.md` L9 |
| 单位 | `saleable_volume` = 已售可结算数量（同数量单位）；`realized_price` = U/同数量单位；`other_revenue` = U；输出 = U | `card_M09.md` L8 |
| 量纲自检 | 数量 × (U/数量) = U；`other_revenue` 为 U，可加 | 本文件 |
| 适用阶段 | 矿业、能源、农产品**投产后至衰退** | `card_M09.md` L7 |
| 单位一致性禁令 | **不得混用**矿石吨 / 精矿吨 / 金属吨 | `card_M09.md` L8 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；收入不得为负（现行契约） | `scripts/model_registry.py:349-353` |

## 2. 正例（positive，卡片原文输入）

输入（= `card_M09.md` L13-31 原文，逐字）：

```json
{"model_id": "resource", "base_revenue": 0,
 "drivers": {"saleable_volume": [30], "realized_price": [4], "other_revenue": [2]},
 "years": [2027]}
```

手算（逐步，不取整）：

30 × 4 = 120；120 + 2 = **122**。

**期望输出 = `[122]`**（与 `card_M09.md` L33 原文一致）。
- 结构期望：Python `list`，长度 1 = `len(years)`，元素类型 `float`，全部有限，顺序对应 `years` 顺序。
- 逐值容差 = `1e-9 × max(1, 122)` = `1.22e-07`。

## 3. 默认值案例（defaults）

只给必填 driver，省略可选 `other_revenue`：

```json
{"model_id": "resource", "base_revenue": 0,
 "drivers": {"saleable_volume": [30], "realized_price": [4]},
 "years": [2027]}
```

手算：30 × 4 + **0（默认）** = **120**。**期望输出 = `[120]`**，长度 1。
- 该案例证明卡片 L9 声明的可选默认 `other_revenue=0` 在**行为上**成立。
- 同时记录一个事实（不是失败）：该默认由 `scripts/model_registry.py:335` 的隐式补 0 实现，
  注册表里 `resource` 的 `defaults` 是空的；见第 8 节 OQ-1。默认值**不是**缺披露时填零的授权
  （`common_model_cards.md` L22）。

## 4. 连续性（continuity）

`resource` 是**逐年独立的流量模型，不是存量桥**（无期初/期末对账项），
因此"存量断裂"不适用（对应卡片 L54 的 `not_applicable`）。
可适用的连续性检查是**跨年财年连续性 + 同输入集下的逐年独立复算**：

- Continuity positive：`years=[2027, 2028]`，
  `saleable_volume=[30, 45]`、`realized_price=[4, 5]`、`other_revenue=[2, 0]`，`base_revenue=0`。
  手算：2027 = 30×4+2 = **122**；2028 = 45×5+0 = **225**。期望 = `[122, 225]`。
  此例**先**运行并通过，之后才允许跑基于它的断裂 patch。
- Continuity 断裂 patch：`years=[2027, 2029]`（缺 2028，财年不连续）→ 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05，共 11 个）

首个必填 driver = `saleable_volume`。每个负例都在**新的 deepcopy 独立输入**上构造，
全部在内存中构造、**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在冻结输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `saleable_volume = [-1]`（`card_M09.md` L35 指定的专属负例） | `ModelRegistryError` |
| N01a | `saleable_volume[0] = True` | `ModelRegistryError` |
| N01b | `saleable_volume[0] = float('nan')` | `ModelRegistryError` |
| N01c | `saleable_volume[0] = float('inf')` | `ModelRegistryError` |
| N01d | `saleable_volume[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `saleable_volume = []` | `ModelRegistryError`（路径长度 ≠ 1） |
| N03 | 删除 `saleable_volume` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive，先验 positive） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：异常类型必须是 `ModelRegistryError`；
`ImportError` / `ModuleNotFoundError` / `FileNotFoundError` / 其它异常类型**一律不得**计为通过。
共同负例编号与语义取自 `common_model_cards.md` L26-30。

NEG-CARD 语义：`saleable_volume=-1` 触发的是**值域**拒绝（`quantity` 维默认 `[0, inf)`），
不是长度拒绝，也不是 JSON 解析器拒绝；这与同批卡 r1 被打回的"名不副实负例"不同
（该负例确实覆盖了值域路径，运行器记录实际错误消息以便核对）。
本卡**不声称**负销售量在经济上永不可能（`common_model_cards.md` L11），
只声称现行契约拒绝它。

## 6. 观察项（非 pass/fail；有明确期望的会被比对并打印，但不改变退出码）

| ID | 变换 | 冻结期望 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（drivers/years 不变） | 与正例相同 `[122]` | `_rowwise` 丢弃 `base_revenue`；设计观察 |
| OBS-PRICE-NEG | `realized_price = [-1]`（其余不变） | `ModelRegistryError` | 记录 `revenue_per_unit` 维默认下界为 0；即负实售价在当前入口无法表达。驱动域检查先于计算器，故消息应指向 `resource.realized_price`；同时总收入也会因 -28 < 0 被拒——运行器记录的**实际消息**用来说明哪一道闸先触发 |

卡片 L8 的"不得混矿石吨/精矿吨/金属吨"是**披露层**约束：本模型没有单位字段，
运行时无法观测，故**不构造**伪造用例，只在第 7 节披露栏登记为不可运行验证项。

## 7. 契约保真检查（结构/长度/字段集，门控）

除数值外，运行器必须核对下列**冻结契约**（与数值不符同等计入"保真不符"）：

| 检查 | 冻结期望 | 出处 |
|---|---|---|
| 注册公式串 | `revenue = saleable_volume * realized_price + other_revenue` | `card_M09.md` L8 文字 |
| `required` 集合 | `{"saleable_volume", "realized_price"}` | `card_M09.md` L9 |
| `optional` 集合 | `{"other_revenue"}` | `card_M09.md` L9 |
| `dimensions` | `saleable_volume=quantity`、`realized_price=revenue_per_unit`、`other_revenue=revenue` | `card_M09.md` L8 |
| 输出容器 | 内置 `list`（不是 tuple/dict/生成器） | `model_registry.py:308` 返回注解 |
| 输出长度 | `== len(years)` | `card_M09.md` L44 |
| 元素类型集 | `{float}`，全部有限 | `model_registry.py:351` |
| 年份对齐 | 输出第 i 项对应 `years[i]`；oracle 的 `years` 必须等于输入的 `years` | `card_M09.md` L44 |
| 有效默认行为 | 省略 `other_revenue` → 与显式 0 相同（第 3 节） | `card_M09.md` L9 |
| 声明默认（记录项） | 注册表 `defaults` 实测为空；卡片声明的默认由隐式补 0 实现 | `card_M09.md` L9 + `model_registry.py:335` |

## 8. 拒绝条件（R 表）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行执行 |
|---|---|---|---|
| R1 | `saleable_volume` 为负（值域） | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf）或 bool 冒充数值 | `ModelRegistryError` | 是（N01a-d） |
| R7 | 混用矿石吨/精矿吨/金属吨（单位口径） | **业务拒绝**：需 `special_review` | 否（模型无单位字段，不可运行验证） |
| R8 | 回收/应付/加工费重复扣减 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R9 | 用生产量代替销售量 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R10 | 总收入为负 | `ModelRegistryError`（`model_registry.py:352`） | 间接（见 OBS-PRICE-NEG） |

## 9. 三种资格（本卡只可能更新 formula）

- `formula`：由本卡 A–C 结果决定，记为 `review_pending`；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。
- `accuracy`：保持 **unproven**。

## 10. 停止条件自检（`card_M09.md` L50-55）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 4 节，`resource` 无存量对账项）。
- 准确性：`STOP_ACCURACY`（不存在 I-12 冻结设计）。

## 11. 披露适配（D）与后续（E/F）：本 attempt 的边界

D 是 `[professional_decision_required]`（`card_M09.md` L46），本 attempt **不主张**完成 D：

- 本 attempt 只产出**来源勘察**（`evidence/M09/disclosure_source_survey.json`：本地真实文件路径 + sha256 +
  文件类别）与**未映射清单**（`evidence/M09/disclosure_mapping.json`：每个 driver 一行，
  `state=missing`，写出该 driver 需要披露里的什么内容；**不填任何数值**）。
- 原因：D 要求逐字段标注原文/原单位/转换/参数 ID/期间/范围，并由行业/会计 reviewer 处理
  `special_review` 与基期锚点；本 attempt 没有该签署，也没有为一个**已结束期间**做收入对账。
- E（`[executable_after_D]`，`card_M09.md` L47）由 I-10-A 先行执行，本 attempt 不产出三情景 wiring，
  更不把任何 probe 称作情景或准确性证据。
- F（`card_M09.md` L48）需 I-12 冻结设计，不存在，故 `accuracy` 保持 `unproven`。
