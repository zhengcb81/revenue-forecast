# M12 · bank_revenue — 冻结 oracle（运行前写定）

Card: M12（`execution_v2/card_M12.md`）；Parent I-10；状态 planned；调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M12/a20260919-01`；model_id: `bank_revenue`。
入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；
注册：`scripts/model_registry.py:232`。
本文件在**任何产品代码运行之前**写定；写定后不得为贴合运行结果而修改。

## 0. 独立性与口径声明（最重要）

- 第 2–6 节全部数值预期来自**手算**（见每处 `hand_work`），由本 attempt 内独立脚本
  `scripts/oracle_cards_M09_M12.py` 用 Python 标准库（`argparse`/`hashlib`/`json`/`os`/`decimal`）复算，
  生成 `evidence/M12/oracle.json`。该脚本**不 import** 产品任何模块；自检见
  `evidence/M12/oracle_selfcheck.json` 的 `product_import_present=false`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 运行器 `scripts/run_card.py` 只调用一个产品入口 `calculate_registered_model(**input)`，
  expected 只从 `evidence/M12/oracle.json` 读取。
- 容差 `abs(actual-expected) <= 1e-9*max(1,abs(expected))`；先比结构/长度/字段集，再逐值比数值。
- 公式出处：`card_M12.md` L6（入口/注册）、L8（单位/口径）、L9（必填/可选）、L42（手算 34）。

## 1. 公式 / 单位 / 口径（冻结）

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 平均生息资产 × 资产收益率 − 平均付息负债 × 资金成本 + 手续费收入 + 其他收入` | `card_M12.md` L8 |
| 必填 driver | `average_earning_assets`、`asset_yield`、`average_interest_bearing_liabilities`、`funding_cost`、`fee_revenue` | `card_M12.md` L9 |
| 可选 driver / 默认 | `other_revenue` 默认 `0` | `card_M12.md` L9 |
| 单位 | 余额类 = U；`asset_yield`/`funding_cost` = 年度小数（**可负**）；`fee_revenue`/`other_revenue` = U（已确认净额）；输出 = U | `card_M12.md` L8 |
| 量纲自检 | U × 无量纲 = U；利息净额与手续费同为 U，可加减 | 本文件 |
| 适用阶段 | 银行增长、成熟和资产负债重定价 | `card_M12.md` L7 |
| 利率域 | **负利率允许**，不得重加 0–1 限制 | `card_M12.md` L48 |
| 口径禁令 | 净息差（NIM）**不等于**资产收益率，不得替代 | `card_M12.md` L48 |
| 当前不支持 | **总收入负值**（现行契约拒绝） | `card_M12.md` L48 + `scripts/model_registry.py:352` |
| 硬约束 | 输出长度 = `len(years)`；逐年独立 | `scripts/model_registry.py:349` |

## 2. 正例（positive，卡片原文输入）

输入（= `card_M12.md` L13-40 原文，逐字）：

```json
{"model_id": "bank_revenue", "base_revenue": 0,
 "drivers": {"average_earning_assets": [1000], "asset_yield": [0.04],
             "average_interest_bearing_liabilities": [800], "funding_cost": [0.02],
             "fee_revenue": [8], "other_revenue": [2]},
 "years": [2027]}
```

手算（逐步，不取整）：

1000 × 0.04 = 40；800 × 0.02 = 16；40 − 16 = 24；24 + 8 = 32；32 + 2 = **34**。
（卡片 L42 写作 `40−16+10=34`。）

**期望输出 = `[34]`**（与 `card_M12.md` L42 原文一致）。
- 结构期望：`list`，长度 1 = `len(years)`，元素 `float`、有限。
- 逐值容差 = `1e-9 × 34` = `3.4e-08`。
- 注：实现用 `math.fsum` 求和；`1000×0.04` 与 `800×0.02` 在二进制浮点下落在 `40.0`、`16.0`，
  故实际值应为精确的 `34.0`；即使有极小舍入差也远在容差内。

## 3. 默认值案例（defaults）

省略可选 `other_revenue`（5 个必填 driver 全部保留）：

```json
{"model_id": "bank_revenue", "base_revenue": 0,
 "drivers": {"average_earning_assets": [1000], "asset_yield": [0.04],
             "average_interest_bearing_liabilities": [800], "funding_cost": [0.02],
             "fee_revenue": [8]},
 "years": [2027]}
```

手算：40 − 16 + 8 + **0（默认）** = **32**。**期望输出 = `[32]`**，长度 1。
- 该案例证明卡片 L9 声明的可选默认在**行为上**成立。
- 记录事实（不是失败）：该默认由 `scripts/model_registry.py:335` 隐式补 0 实现，
  注册表里 `bank_revenue` 的 `defaults` 为空；见第 8 节 OQ-1。默认值**不是**缺披露时填零的授权。

## 4. 连续性（continuity）

`bank_revenue` 是**逐年独立的流量模型，不是存量桥**（余额以"平均余额"形式作为 driver 输入，
模型内没有期初/期末对账项），因此"存量断裂"不适用（对应卡片 L63 的 `not_applicable`）。
可适用的连续性检查是**跨年财年连续性 + 同输入集下的逐年独立复算**：

- Continuity positive：`years=[2027, 2028]`，
  `average_earning_assets=[1000, 1200]`、`asset_yield=[0.04, 0.045]`、
  `average_interest_bearing_liabilities=[800, 1000]`、`funding_cost=[0.02, 0.025]`、
  `fee_revenue=[8, 9]`、`other_revenue=[2, 0]`，`base_revenue=0`。
  手算：2027 = 40 − 16 + 8 + 2 = **34**；2028 = 54 − 25 + 9 + 0 = **38**。期望 = `[34, 38]`。
  此例**先**运行并通过，之后才允许跑基于它的断裂 patch。
- Continuity 断裂 patch：`years=[2027, 2029]`（缺 2028，财年不连续）→ 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05，共 11 个）

首个必填 driver = `average_earning_assets`。每个负例都在**新的 deepcopy 独立输入**上构造，
全部在内存中构造、**不经 JSON 解析器**。

| 例 | 变换（在冻结输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `asset_yield=[0]`、`funding_cost=[0.1]`、`fee_revenue=[0]`、`other_revenue=[0]`（`card_M12.md` L44 指定的专属负例） | `ModelRegistryError`（总收入 0−80+0+0 = −80 < 0） |
| N01a | `average_earning_assets[0] = True` | `ModelRegistryError` |
| N01b | `average_earning_assets[0] = float('nan')` | `ModelRegistryError` |
| N01c | `average_earning_assets[0] = float('inf')` | `ModelRegistryError` |
| N01d | `average_earning_assets[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `average_earning_assets = []` | `ModelRegistryError`（路径长度 ≠ 1） |
| N03 | 删除 `average_earning_assets` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive，先验 positive） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：异常类型必须是 `ModelRegistryError`；
`ImportError` / `ModuleNotFoundError` / `FileNotFoundError` / 其它异常类型**一律不得**计为通过。
共同负例编号与语义取自 `common_model_cards.md` L26-30。

NEG-CARD 语义（本卡最容易误读的一例）：被拒的是**总收入为负**这一总量闸
（`card_M12.md` L48「总收入负值当前不支持」），**不是**利率域闸——
利率域对 `asset_yield`/`funding_cost` 是刻意放开为 `(-inf, inf)` 的（见第 6 节 OBS-NEG-RATE-*、
第 8 节 OQ-2）。因此本负例**不能**被读成"利率必须为正"。
本卡也不声称负总收入在经济上永不可能（`common_model_cards.md` L11），只声称现行契约拒绝它。

## 6. 观察项（非 pass/fail；有明确期望的会被比对并打印，但不改变退出码）

| ID | 变换 | 冻结期望 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（drivers/years 不变） | 与正例相同 `[34]` | `_rowwise` 丢弃 `base_revenue`；设计观察 |
| OBS-NEG-RATE-ACCEPTED | `asset_yield=[-0.01]`、`average_interest_bearing_liabilities=[0]`、`funding_cost=[0]`（`fee_revenue`、`other_revenue` 保持 8、2） | `[0.0]` | 手算：1000×(−0.01) − 0×0 + 8 + 2 = −10 + 10 = 0。证明**负利率被接受**（`card_M12.md` L48），且总量恰好为 0 不被拒（仅 `< 0` 被拒） |
| OBS-NEG-RATE-TOTAL-NEG | 仅 `asset_yield=[-0.01]`（其余同正例） | `ModelRegistryError` | 手算：−10 − 16 + 8 + 2 = −16 < 0。与上一条配对，证明**起约束作用的是总量闸，而不是利率域闸** |
| OBS-FEE-SIGNED | `fee_revenue=[-5]`（其余同正例） | `[21.0]` | 手算：40 − 16 − 5 + 2 = 21。证明 `fee_revenue` 是带符号 driver（负手续费/退回可表达） |
| OBS-RATE-GT1 | `asset_yield=[0.5]`（其余同正例） | `[494.0]` | 手算：500 − 16 + 8 + 2 = 494。证明利率域上界也未被人为压到 1；即"ratio 维默认 [0,1]"**不适用**于 `asset_yield` |

卡片 L48 的"净息差（NIM）不等资产收益率"是**披露层**口径禁令，
模型内没有 NIM 字段，运行时**不可观测**，故不构造伪造用例，只在第 8 节登记。

## 7. 契约保真检查（结构/长度/字段集，门控）

| 检查 | 冻结期望 | 出处 |
|---|---|---|
| 注册公式串 | `revenue = average_earning_assets * asset_yield - average_interest_bearing_liabilities * funding_cost + fee_revenue + other_revenue` | `card_M12.md` L8 文字 |
| `required` 集合 | `{average_earning_assets, asset_yield, average_interest_bearing_liabilities, funding_cost, fee_revenue}` | `card_M12.md` L9 |
| `optional` 集合 | `{other_revenue}` | `card_M12.md` L9 |
| `dimensions` | `average_earning_assets=monetary_balance`、`asset_yield=ratio`、`average_interest_bearing_liabilities=monetary_balance`、`funding_cost=ratio`、`fee_revenue=revenue`、`other_revenue=revenue` | `card_M12.md` L8 |
| 输出容器 | 内置 `list` | `model_registry.py:308` 返回注解 |
| 输出长度 | `== len(years)` | `card_M12.md` L53 |
| 元素类型集 | `{float}`，全部有限 | `model_registry.py:351` |
| 年份对齐 | 输出第 i 项对应 `years[i]`；oracle 的 `years` 必须等于输入的 `years` | `card_M12.md` L53 |
| 有效默认行为 | 省略 `other_revenue` → 与显式 0 相同（第 3 节） | `card_M12.md` L9 |
| 声明默认（记录项） | 注册表 `defaults` 实测为空；卡片声明的默认由隐式补 0 实现 | `card_M12.md` L9 + `model_registry.py:335` |
| 利率域 | `asset_yield`、`funding_cost` 的**显式** driver_bounds 为 `(None, None)`，即 `(-inf, inf)` | `card_M12.md` L48 |

## 8. 拒绝条件（R 表）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行执行 |
|---|---|---|---|
| R1 | 总收入为负 | `ModelRegistryError` | 是（NEG-CARD、OBS-NEG-RATE-TOTAL-NEG） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值或 bool 冒充数值 | `ModelRegistryError` | 是（N01a-d） |
| R7 | 利率被强行限制在 0–1（**不得**作为拒绝条件） | 必须**接受**负利率与大利率 | 是（OBS-NEG-RATE-ACCEPTED、OBS-RATE-GT1） |
| R8 | 用 NIM 代替资产收益率 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R9 | 手续费未取已确认净额 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R10 | 生息资产/付息负债用期末余额冒充平均余额 | **业务拒绝**：需 `special_review` | 否（披露层） |

## 9. 三种资格（本卡只可能更新 formula）

- `formula`：由本卡 A–C 结果决定，记为 `review_pending`；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。
- `accuracy`：保持 **unproven**。

## 10. 停止条件自检（`card_M12.md` L59-64）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 4 节，模型内无期初/期末对账项；余额以平均余额 driver 进入）。
- 准确性：`STOP_ACCURACY`（不存在 I-12 冻结设计）。

## 11. 披露适配（D）与后续（E/F）：本 attempt 的边界

D 是 `[professional_decision_required]`（`card_M12.md` L55），本 attempt **不主张**完成 D：

- 只产出**来源勘察**（`evidence/M12/disclosure_source_survey.json`）与**未映射清单**
  （`evidence/M12/disclosure_mapping.json`：每个 driver 一行、`state=missing`、写出所需披露内容；
  **不填任何数值**）。
- 原因：D 要求逐字段标注原文/原单位/转换/参数 ID/期间/范围，并由行业/会计 reviewer 处理
  `special_review`（平均余额 vs 期末余额、年化口径、利息净额与手续费净额、并表范围）与基期锚点；
  本 attempt 没有该签署，也没有为**一个已结束期间**做收入对账。
- E（`card_M12.md` L56）由 I-10-A 先行执行；本 attempt 不产出三情景 wiring。
- F（`card_M12.md` L57）需 I-12 冻结设计，不存在，故 `accuracy` 保持 `unproven`。
