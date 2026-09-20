# M10 · reserve_depletion — 冻结 oracle（运行前写定）

Card: M10（`execution_v2/card_M10.md`）；Parent I-10；状态 planned；调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M10/a20260919-01`；model_id: `reserve_depletion`。
入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；
注册：`scripts/model_registry.py:230`。
本文件在**任何产品代码运行之前**写定；写定后不得为贴合运行结果而修改。

## 0. 独立性与口径声明（最重要）

- 第 2–6 节全部数值预期来自**手算**（见每处 `hand_work`），由本 attempt 内独立脚本
  `scripts/oracle_cards_M09_M12.py` 用 Python 标准库（`argparse`/`hashlib`/`json`/`os`/`decimal`）复算，
  生成 `evidence/M10/oracle.json`。该脚本**不 import** 产品任何模块；自检见
  `evidence/M10/oracle_selfcheck.json` 的 `product_import_present=false`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 运行器 `scripts/run_card.py` 只调用一个产品入口 `calculate_registered_model(**input)`，
  expected 只从 `evidence/M10/oracle.json` 读取。
- 容差 `abs(actual-expected) <= 1e-9*max(1,abs(expected))`；先比结构/长度/字段集，再逐值比数值。
- 公式出处：`card_M10.md` L6（入口/注册）、L8（单位/口径）、L9（必填/可选）、L48（手算 490）；
  两年连续性用例出处：`card_M10.md` L56-118（含 `negative_patch`）。

## 1. 公式 / 单位 / 口径（冻结）

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 存量对账 | `opening_reserves + additions + reserve_revisions - depletion = closing_reserves` | `card_M10.md` L48 |
| 跨年连续性 | `closing_reserves[t-1] == opening_reserves[t]` | `card_M10.md` L116 |
| 收入公式 | `revenue = depletion × recovery_rate × realized_price + other_revenue` | `card_M10.md` L8、L48 |
| 必填 driver | `opening_reserves`、`additions`、`depletion`、`closing_reserves`、`recovery_rate`、`realized_price` | `card_M10.md` L9 |
| 可选 driver / 默认 | `other_revenue` 默认 `0`；`reserve_revisions` 默认 `0` | `card_M10.md` L9 |
| 单位 | 储量类（`opening/additions/depletion/closing/revisions`）同一储量单位；`recovery_rate` 无量纲；`realized_price` = U/同单位；输出 = U | `card_M10.md` L8 |
| 量纲自检 | 储量 × 回收率 = 可售量；可售量 × (U/量) = U | 本文件 |
| 适用阶段 | 储量、消耗及销售衔接**可验证**的开采与衰退业务 | `card_M10.md` L7 |
| 专业禁令（披露层） | 储量若已含回收率则**不可重复扣**；消耗**不当然**等于当期销售 | `card_M10.md` L54 |
| 硬约束 | 输出长度 = `len(years)`；收入不得为负（现行契约） | `scripts/model_registry.py:349-353` |

## 2. 正例（positive，卡片原文输入）

输入（= `card_M10.md` L13-46 原文，逐字）：

```json
{"model_id": "reserve_depletion", "base_revenue": 0,
 "drivers": {"opening_reserves": [1000], "additions": [100], "reserve_revisions": [-50],
             "depletion": [200], "closing_reserves": [850], "recovery_rate": [0.8],
             "realized_price": [3], "other_revenue": [10]},
 "years": [2027]}
```

手算（逐步，不取整）：

1. 存量对账：1000 + 100 + (−50) − 200 = **850** = `closing_reserves` → 平衡成立。
2. 可售量：200 × 0.8 = 160。
3. 收入：160 × 3 = 480；480 + 10 = **490**。

**期望输出 = `[490]`**（与 `card_M10.md` L48 原文一致）。
- 结构期望：`list`，长度 1 = `len(years)`，元素 `float`、有限。
- 逐值容差 = `1e-9 × 490` = `4.9e-07`。

## 3. 默认值案例（defaults，本卡需自行设计输入）

只给 6 个必填 driver，省略可选 `other_revenue` 与 `reserve_revisions`。
**注意**：省略 `reserve_revisions` 等价于 0，若沿用正例的 `closing_reserves=850`，
存量对账会变成 1000+100−200=900 ≠ 850 而被拒。因此本案例的对账量必须与"修订为 0"自洽：

```json
{"model_id": "reserve_depletion", "base_revenue": 0,
 "drivers": {"opening_reserves": [1000], "additions": [100], "depletion": [250],
             "closing_reserves": [850], "recovery_rate": [0.8], "realized_price": [3]},
 "years": [2027]}
```

手算：对账 1000 + 100 + **0（默认）** − 250 = **850** = `closing_reserves` → 平衡成立；
收入 250 × 0.8 × 3 + **0（默认）** = 600。**期望输出 = `[600]`**，长度 1。
- 该案例证明卡片 L9 声明的两个可选默认在**行为上**成立。
- 记录事实（不是失败）：两个默认都由 `scripts/model_registry.py:335` 隐式补 0 实现，
  注册表的 `defaults` 为空；`reserve_revisions` 的这一性质见第 8 节 OQ-1（"没找到修订"与
  "没有修订"不可区分），本卡不改代码。

## 4. 连续性（continuity，卡片 L56-118 原文用例）

本卡是**真存量桥**，连续性必须实际验证：先跑两年 positive，再只应用卡片给定的 `negative_patch`。

- Continuity positive（逐字取自 `card_M10.md` L58-104）：
  `years=[2027, 2028]`；`opening_reserves=[1000, 850]`、`additions=[100, 0]`、
  `reserve_revisions=[-50, 0]`、`depletion=[200, 0]`、`closing_reserves=[850, 850]`、
  `recovery_rate=[0.8, 0.8]`、`realized_price=[3, 3]`、`other_revenue=[10, 0]`；`base_revenue=0`。
  手算：
  - 2027：对账 1000+100−50−200 = 850 = closing → 平衡；收入 200×0.8×3+10 = **490**。
  - 2028：对账 850+0+0−0 = 850 = closing → 平衡；连续性 `opening[2028]=850` = `closing[2027]=850` → 成立；
    收入 0×0.8×3+0 = **0**。
  期望 = `[490, 0]`（与卡片 L101 的 `expected_revenue` 一致）。
- Continuity 断裂 patch（卡片 L106-115 原文 `negative_patch`；卡片 L116 给出 `expected_negative`）：
  `opening_reserves=[1000, 851]`、`closing_reserves=[850, 851]`，其余保持。
  手算：2028 的**自身对账** 851+0+0−0 = 851 = closing → 平衡**成立**；
  但 `opening[2028]=851` ≠ `closing[2027]=850`（多 1）→ 跨年连续性不成立
  → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05，共 11 个）

首个必填 driver = `opening_reserves`。每个负例都在**新的 deepcopy 独立输入**上构造，
全部在内存中构造、**不经 JSON 解析器**。

| 例 | 变换（在冻结输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `closing_reserves = [851]`（`card_M10.md` L50 指定的专属负例） | `ModelRegistryError`（自身对账失败：850≠851） |
| N01a | `opening_reserves[0] = True` | `ModelRegistryError` |
| N01b | `opening_reserves[0] = float('nan')` | `ModelRegistryError` |
| N01c | `opening_reserves[0] = float('inf')` | `ModelRegistryError` |
| N01d | `opening_reserves[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `opening_reserves = []` | `ModelRegistryError`（路径长度 ≠ 1） |
| N03 | 删除 `opening_reserves` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `opening_reserves=[1000, 851]`、`closing_reserves=[850, 851]`（基于 continuity_positive，先验 positive） | `ModelRegistryError`（跨年连续性） |

合计 **11 个负例**。通过判据：异常类型必须是 `ModelRegistryError`；
`ImportError` / `ModuleNotFoundError` / `FileNotFoundError` / 其它异常类型**一律不得**计为通过。
共同负例编号与语义取自 `common_model_cards.md` L26-30。

NEG-CARD 覆盖**存量对账**闸；CONT-BREAK 覆盖**跨年连续性**闸——两者是不同代码路径
（`reserve stock-flow balance failed` 与 `reserve continuity failed`），运行器分别记录实际消息。

## 6. 观察项（非 pass/fail；有明确期望的会被比对并打印，但不改变退出码）

| ID | 变换 | 冻结期望 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999` | 与正例相同 `[490]` | `_reserve_depletion` 丢弃 `base_revenue`；设计观察 |
| OBS-DEFAULT-EQUIV | 默认值案例 + 显式 `other_revenue=[0]`、`reserve_revisions=[0]` | 等于默认值案例 `[600]` | 使"隐式补 0"这一事实可证伪 |
| OBS-REVISION-POS | 正例 + `reserve_revisions=[50]`、`closing_reserves=[950]` | `[490]` | 修订只进对账、不进收入：对账 1000+100+50−200=950 成立而收入不变 |
| OBS-RECOVERY-GT1 | `recovery_rate = [1.5]` | `ModelRegistryError` | 记录 `ratio` 维默认上界 1.0 生效（`recovery_rate` 无显式 driver_bounds） |

卡片 L54 的两条专业禁令（"储量已含回收率不可重复扣"、"消耗不当然等于当期销售"）是**披露层**语义，
模型内没有对应字段，运行时**不可观测**，故不构造伪造用例，只在第 8 节登记。

## 7. 契约保真检查（结构/长度/字段集，门控）

| 检查 | 冻结期望 | 出处 |
|---|---|---|
| 注册公式串 | `revenue = depletion * recovery_rate * realized_price + other_revenue` | `card_M10.md` L8 文字 |
| `required` 集合 | `{opening_reserves, additions, depletion, closing_reserves, recovery_rate, realized_price}` | `card_M10.md` L9 |
| `optional` 集合 | `{other_revenue, reserve_revisions}` | `card_M10.md` L9 |
| `dimensions` | 储量五项 = `reserve_volume`；`recovery_rate=ratio`；`realized_price=revenue_per_unit`；`other_revenue=revenue` | `card_M10.md` L8 |
| 输出容器 | 内置 `list` | `model_registry.py:308` 返回注解 |
| 输出长度 | `== len(years)` | `card_M10.md` L123 |
| 元素类型集 | `{float}`，全部有限 | `model_registry.py:351` |
| 年份对齐 | 输出第 i 项对应 `years[i]`；oracle 的 `years` 必须等于输入的 `years` | `card_M10.md` L123 |
| 有效默认行为 | 省略两个可选 driver → 与显式 0 相同（第 3 节） | `card_M10.md` L9 |
| 声明默认（记录项） | 注册表 `defaults` 实测为空；卡片声明的默认由隐式补 0 实现 | `card_M10.md` L9 + `model_registry.py:335` |

## 8. 拒绝条件（R 表）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行执行 |
|---|---|---|---|
| R1 | 存量对账不平（自身年度） | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值或 bool 冒充数值 | `ModelRegistryError` | 是（N01a-d） |
| R7 | 跨年连续性断裂（`opening[t] ≠ closing[t-1]`） | `ModelRegistryError` | 是（CONT-BREAK） |
| R8 | `recovery_rate` 越出比例域 | `ModelRegistryError` | 间接（OBS-RECOVERY-GT1） |
| R9 | 储量已含回收率又重复乘回收率 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R10 | 用消耗量直接当作当期销售量 | **业务拒绝**：需 `special_review` | 否（披露层） |
| R11 | 总收入为负 | `ModelRegistryError`（`model_registry.py:352`） | 未单独构造（本卡不需要） |

## 9. 三种资格（本卡只可能更新 formula）

- `formula`：由本卡 A–C 结果决定，记为 `review_pending`；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。
- `accuracy`：保持 **unproven**。

## 10. 停止条件自检（`card_M10.md` L129-134）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量基期锚定/桥/跨年连续性：本卡**适用**，故必须在第 4 节实测通过；未通过即 `STOP_BRIDGE`。
- 准确性：`STOP_ACCURACY`（不存在 I-12 冻结设计）。

## 11. 披露适配（D）与后续（E/F）：本 attempt 的边界

D 是 `[professional_decision_required]`（`card_M10.md` L125），本 attempt **不主张**完成 D：

- 只产出**来源勘察**（`evidence/M10/disclosure_source_survey.json`）与**未映射清单**
  （`evidence/M10/disclosure_mapping.json`：每个 driver 一行、`state=missing`、写出所需披露内容；
  **不填任何数值**）。
- 原因：D 要求逐字段标注原文/原单位/转换/参数 ID/期间/范围，并由行业/会计 reviewer 处理
  `special_review`（储量分类、回收定义、消耗与销售的桥）与基期锚点；本 attempt 没有该签署，
  也没有为**一个已结束期间**做收入对账。
- E（`card_M10.md` L126）由 I-10-A 先行执行；本 attempt 不产出三情景 wiring，也不把 probe 称作情景或准确性证据。
- F（`card_M10.md` L127）需 I-12 冻结设计，不存在，故 `accuracy` 保持 `unproven`。
