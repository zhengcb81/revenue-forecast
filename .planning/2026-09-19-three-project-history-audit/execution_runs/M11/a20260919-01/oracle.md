# M11 · infrastructure — 冻结 oracle（运行前写定）

Card: M11（`execution_v2/card_M11.md`）；Parent I-10；状态 planned；调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M11/a20260919-01`；model_id: `infrastructure`。
入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；
注册：`scripts/model_registry.py:231`。
本文件在**任何产品代码运行之前**写定；写定后不得为贴合运行结果而修改。

## 0. 独立性与口径声明（最重要）

- 第 2–6 节全部数值预期来自**手算**（见每处 `hand_work`），由本 attempt 内独立脚本
  `scripts/oracle_cards_M09_M12.py` 用 Python 标准库（`argparse`/`hashlib`/`json`/`os`/`decimal`）复算，
  生成 `evidence/M11/oracle.json`。该脚本**不 import** 产品任何模块；自检见
  `evidence/M11/oracle_selfcheck.json` 的 `product_import_present=false`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 运行器 `scripts/run_card.py` 只调用一个产品入口 `calculate_registered_model(**input)`，
  expected 只从 `evidence/M11/oracle.json` 读取。
- 容差 `abs(actual-expected) <= 1e-9*max(1,abs(expected))`；先比结构/长度/字段集，再逐值比数值。
- 公式出处：`card_M11.md` L6（入口/注册）、L8（单位/口径）、L9（必填/可选）、L33（手算 400×0.5+10=210）。

## 1. 公式 / 单位 / 口径（冻结）

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 实际计费活动量 × U/同活动单位 + 其他收入` | `card_M11.md` L8 |
| 必填 driver | `billable_volume`、`tariff` | `card_M11.md` L9 |
| 可选 driver / 默认 | `other_revenue` 默认 `0` | `card_M11.md` L9 |
| 单位 | `billable_volume` = 实际计费活动量（同活动单位）；`tariff` = U/同活动单位；`other_revenue` = U；输出 = U | `card_M11.md` L8 |
| 量纲自检 | 活动量 × (U/活动量) = U | 本文件 |
| 适用阶段 | 公用事业、管网、收费交通**投产后**业务 | `card_M11.md` L7 |
| 专业禁令（披露层） | 吞吐量**不当然**全额计费；补贴与容量费**不可重复加入** | `card_M11.md` L39 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；收入不得为负（现行契约） | `scripts/model_registry.py:349-353` |

## 2. 正例（positive，卡片原文输入）

输入（= `card_M11.md` L13-31 原文，逐字）：

```json
{"model_id": "infrastructure", "base_revenue": 0,
 "drivers": {"billable_volume": [400], "tariff": [0.5], "other_revenue": [10]},
 "years": [2027]}
```

手算（逐步，不取整）：

400 × 0.5 = 200；200 + 10 = **210**。

**期望输出 = `[210]`**（与 `card_M11.md` L33 原文一致）。
- 结构期望：`list`，长度 1 = `len(years)`，元素 `float`、有限。
- 逐值容差 = `1e-9 × 210` = `2.1e-07`。

## 3. 默认值案例（defaults）

只给必填 driver，省略可选 `other_revenue`：

```json
{"model_id": "infrastructure", "base_revenue": 0,
 "drivers": {"billable_volume": [400], "tariff": [0.5]},
 "years": [2027]}
```

手算：400 × 0.5 + **0（默认）** = **200**。**期望输出 = `[200]`**，长度 1。
- 该案例证明卡片 L9 声明的可选默认在**行为上**成立。
- 记录事实（不是失败）：该默认由 `scripts/model_registry.py:335` 隐式补 0 实现，
  注册表里 `infrastructure` 的 `defaults` 为空；见第 8 节 OQ-1。默认值**不是**缺披露时填零的授权。

## 4. 连续性（continuity）

`infrastructure` 是**逐年独立的流量模型，不是存量桥**（无期初/期末对账项），
因此"存量断裂"不适用（对应卡片 L54 的 `not_applicable`）。
可适用的连续性检查是**跨年财年连续性 + 同输入集下的逐年独立复算**：

- Continuity positive：`years=[2027, 2028]`，
  `billable_volume=[400, 500]`、`tariff=[0.5, 0.6]`、`other_revenue=[10, 0]`，`base_revenue=0`。
  手算：2027 = 400×0.5+10 = **210**；2028 = 500×0.6+0 = **300**。期望 = `[210, 300]`。
  此例**先**运行并通过，之后才允许跑基于它的断裂 patch。
- Continuity 断裂 patch：`years=[2027, 2029]`（缺 2028，财年不连续）→ 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05，共 11 个）

首个必填 driver = `billable_volume`。每个负例都在**新的 deepcopy 独立输入**上构造，
全部在内存中构造、**不经 JSON 解析器**。

| 例 | 变换（在冻结输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `billable_volume = [-1]`（`card_M11.md` L35 指定的专属负例） | `ModelRegistryError` |
| N01a | `billable_volume[0] = True` | `ModelRegistryError` |
| N01b | `billable_volume[0] = float('nan')` | `ModelRegistryError` |
| N01c | `billable_volume[0] = float('inf')` | `ModelRegistryError` |
| N01d | `billable_volume[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `billable_volume = []` | `ModelRegistryError`（路径长度 ≠ 1） |
| N03 | 删除 `billable_volume` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive，先验 positive） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：异常类型必须是 `ModelRegistryError`；
`ImportError` / `ModuleNotFoundError` / `FileNotFoundError` / 其它异常类型**一律不得**计为通过。
共同负例编号与语义取自 `common_model_cards.md` L26-30。

NEG-CARD 语义：`billable_volume=-1` 触发的是**值域**拒绝（`activity` 维默认 `[0, inf)`），
不是长度拒绝，也不是 JSON 解析器拒绝。本卡**不声称**负计费量在经济上永不可能
（`common_model_cards.md` L11），只声称现行契约拒绝它。

## 6. 观察项（非 pass/fail；有明确期望的会被比对并打印，但不改变退出码）

| ID | 变换 | 冻结期望 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（drivers/years 不变） | 与正例相同 `[210]` | `_rowwise` 丢弃 `base_revenue`；设计观察 |
| OBS-TARIFF-NEG | `tariff = [-1]`（其余不变） | `ModelRegistryError` | 记录 `revenue_per_activity` 维默认下界为 0：负费率/退款率在当前入口无法表达。驱动域检查先于计算器，故消息应指向 `infrastructure.tariff`；同时总收入也会因 400×(−1)+10 = −390 < 0 被拒——运行器记录实际消息以说明哪道闸先触发 |

卡片 L39 的两条专业禁令（"吞吐量不当然全额计费"、"补贴和容量费不可重复加入"）是**披露层**语义，
模型内没有对应字段，运行时**不可观测**，故不构造伪造用例，只在第 8 节登记。

## 7. 契约保真检查（结构/长度/字段集，门控）

| 检查 | 冻结期望 | 出处 |
|---|---|---|
| 注册公式串 | `revenue = billable_volume * tariff + other_revenue` | `card_M11.md` L8 文字 |
| `required` 集合 | `{billable_volume, tariff}` | `card_M11.md` L9 |
| `optional` 集合 | `{other_revenue}` | `card_M11.md` L9 |
| `dimensions` | `billable_volume=activity`、`tariff=revenue_per_activity`、`other_revenue=revenue` | `card_M11.md` L8 |
| 输出容器 | 内置 `list` | `model_registry.py:308` 返回注解 |
| 输出长度 | `== len(years)` | `card_M11.md` L44 |
| 元素类型集 | `{float}`，全部有限 | `model_registry.py:351` |
| 年份对齐 | 输出第 i 项对应 `years[i]`；oracle 的 `years` 必须等于输入的 `years` | `card_M11.md` L44 |
| 有效默认行为 | 省略 `other_revenue` → 与显式 0 相同（第 3 节） | `card_M11.md` L9 |
| 声明默认（记录项） | 注册表 `defaults` 实测为空；卡片声明的默认由隐式补 0 实现 | `card_M11.md` L9 + `model_registry.py:335` |

## 8. 拒绝条件（R 表）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行执行 |
|---|---|---|---|
| R1 | `billable_volume` 为负（值域） | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值或 bool 冒充数值 | `ModelRegistryError` | 是（N01a-d） |
| R7 | `tariff` 为负（退款/负费率） | `ModelRegistryError` | 间接（OBS-TARIFF-NEG） |
| R8 | 吞吐量不全额计费却按全额计费 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R9 | 补贴与容量费重复加入 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R10 | 阶梯费率未按监管生效日切分 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R11 | 总收入为负 | `ModelRegistryError`（`model_registry.py:352`） | 间接（见 OBS-TARIFF-NEG） |

## 9. 三种资格（本卡只可能更新 formula）

- `formula`：由本卡 A–C 结果决定，记为 `review_pending`；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。
- `accuracy`：保持 **unproven**。

## 10. 停止条件自检（`card_M11.md` L50-55）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 4 节，`infrastructure` 无存量对账项）。
- 准确性：`STOP_ACCURACY`（不存在 I-12 冻结设计）。

## 11. 披露适配（D）与后续（E/F）：本 attempt 的边界

D 是 `[professional_decision_required]`（`card_M11.md` L46），本 attempt **不主张**完成 D：

- 只产出**来源勘察**（`evidence/M11/disclosure_source_survey.json`）与**未映射清单**
  （`evidence/M11/disclosure_mapping.json`：每个 driver 一行、`state=missing`、写出所需披露内容；
  **不填任何数值**）。
- 原因：D 要求逐字段标注原文/原单位/转换/参数 ID/期间/范围，并由行业/会计 reviewer 处理
  `special_review`（计费量口径、阶梯费率、监管生效日、容量费与补贴的归属）与基期锚点；
  本 attempt 没有该签署，也没有为**一个已结束期间**做收入对账。
- E（`card_M11.md` L47）由 I-10-A 先行执行；本 attempt 不产出三情景 wiring。
- F（`card_M11.md` L48）需 I-12 冻结设计，不存在，故 `accuracy` 保持 `unproven`。
