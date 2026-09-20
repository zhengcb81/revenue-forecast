# M24 · subscription_arr_bridge · ARR 存量与收入时点 — 冻结 oracle（运行前写定）

Card M24（`execution_v2/card_M24.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M24/a20260919-01`。
本文在**任何产品代码运行之前**写定；写入后不得为贴合结果而修改，运行后的对账只允许以**追加**节形式补记（见文末「运行后对账」节）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M24.py` 用 Python 标准库（`decimal`/`json`/`hashlib`/`os`/`argparse`）复算。
  该脚本**不 import** 产品任何模块（`model_registry` / `model_extensions` 均不出现），
  自检记录见 `evidence/M24/oracle_selfcheck.json`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M24.md` L8、L51「手算：流失200×0.1=20；期末200−20+30+40=250；收入200−15+15+10+5=215」。
- 入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_extensions.py:180`。 该入口仅在冻结之后用于定位调用点。
- `evidence/M24/oracle.json` 可由该脚本**逐字节重生成**（无时间戳、无随机量、无字典序依赖）。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | revenue = opening_arr − opening_arr × (1 − gross_retention_rate) × lost_arr_revenue_fraction + expansion_arr × expansion_revenue_fraction + new_arr × new_arr_revenue_fraction + usage_revenue；桥约束 opening_arr − lost + expansion_arr + new_arr = closing_arr，其中 lost = opening_arr × (1 − gross_retention_rate) | `card_M24.md` L8 |
| 必填 driver | `opening_arr`、`expansion_arr`、`new_arr`、`closing_arr`、`gross_retention_rate`、`lost_arr_revenue_fraction`、`expansion_revenue_fraction`、`new_arr_revenue_fraction` | `card_M24.md` L9 |
| 可选 driver / 默认 | `usage_revenue`（默认 0） | `card_M24.md` L9 |
| 单位 | ARR 为年化运行率 U；当期收入用各变动的时间分数。 | `card_M24.md` L8 |
| 适用 | 有 ARR 桥的 SaaS 增长/成熟/收缩。 | `card_M24.md` L7 |
| 硬约束 | 输出长度 = `len(years)`；逐年检查；非有限值/布尔冒充数值一律拒绝 | 通用契约 |
| 比例域 | 维度为 `ratio` 的 driver 默认域 [0,1]；本卡**不声称**经济上永不可能 | `common_model_cards.md` L11 |
| 存量桥 | `subscription_arr_bridge` 是**存量桥**：逐年存在 `opening_arr − lost + expansion_arr + new_arr = closing_arr` 的平衡约束，且 `opening_arr[t]` 必须等于 `closing_arr[t−1]`；卡片 L59 另给基期锚点 `{"field":"base_arr_parameter_id","driver":"opening_arr","dimension":"revenue"}`。STOP_BRIDGE 在本卡**适用**。 | `card_M24.md` L133 |

## 2. 合成正例（positive）

输入 = `card_M24.md` 合成输入原文（逐字段一致）：

```json
{
 "model_id": "subscription_arr_bridge",
 "base_revenue": 0,
 "drivers": {
  "opening_arr": [
   200
  ],
  "gross_retention_rate": [
   0.9
  ],
  "expansion_arr": [
   30
  ],
  "new_arr": [
   40
  ],
  "closing_arr": [
   250
  ],
  "lost_arr_revenue_fraction": [
   0.75
  ],
  "expansion_revenue_fraction": [
   0.5
  ],
  "new_arr_revenue_fraction": [
   0.25
  ],
  "usage_revenue": [
   5
  ]
 },
 "years": [
  2027
 ]
}
```

手算（逐步，未取整）：

- lost = 200 x (1 - 0.9) = 20; closing = 200 - 20 + 30 + 40 = 250 (bridge closes); revenue = 200 - 20 x 0.75 + 30 x 0.5 + 40 x 0.25 + 5 = 200 - 15 + 15 + 10 + 5 = 215

**期望输出 = `['215.000']`**（与卡片手算一致）。
- 输出长度 = 1 = `len(years)`；输出年份应为 `[2027]`。
- 逐值容差 = `1e-9 × max(1, |expected|)` = `[2.15e-07]`。
- 除数值外还比对**输出结构**：类型为 list、长度等于 `len(years)`、每个元素为有限 float（见 `formula_result.json` 的 `structure_checks`）。

## 3. 默认值案例（defaults）

只给必填 driver，省略全部可选 driver：

```json
{
 "model_id": "subscription_arr_bridge",
 "base_revenue": 0,
 "drivers": {
  "opening_arr": [
   200
  ],
  "gross_retention_rate": [
   0.9
  ],
  "expansion_arr": [
   30
  ],
  "new_arr": [
   40
  ],
  "closing_arr": [
   250
  ],
  "lost_arr_revenue_fraction": [
   0.75
  ],
  "expansion_revenue_fraction": [
   0.5
  ],
  "new_arr_revenue_fraction": [
   0.25
  ]
 },
 "years": [
  2027
 ]
}
```

手算：usage_revenue omitted -> 0; 200 - 15 + 15 + 10 + 0 = 210。

**期望输出 = `['210.000']`**，长度 1。
- 该案例证明默认值确实被应用，且**没有**被错当成「必填缺失」。
- 默认值不是缺披露时填零/一的授权（`common_model_cards.md` L22）；本案例只检验契约行为。
- 默认值案例**不参与**运行器退出码判定（`defaults_ok_not_gating`）。

## 4. 连续性案例（continuity）

连续性断裂 patch 只改 `opening_arr`、`closing_arr` 的第 2 个元素。卡片 L116 描述为「两个年度各自平衡」，但 `closing_arr=[250,251]` 同时改动了 FY2027 的 closing，故实际先触发的是 **FY2027 桥平衡守卫**而不是 FY2028 连续性守卫；两者都是 `ModelRegistryError`，冻结要求是**异常类型**，不是具体消息（见第 4 节与第 11 节）。

- Continuity positive：`years = [2027, 2028]`；手算：
  - FY2027 = 200 - 200*(1-0.9)*0.75 + 30*0.5 + 40*0.25 + 5 → 215.000
  - FY2028 = 250 - 250*(1-1)*0.75 + 0*0.5 + 0*0.25 + 0 → 250.00
  期望 = `['215.000', '250.00']`。此例**先**运行通过，才允许应用断裂 patch。
- Continuity 断裂 patch：`opening_arr = [200, 251]`、`closing_arr = [250, 251]`
  → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `opening_arr`。每个负例使用**新的 deepcopy 独立输入**，互不共享可变对象；全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在冻结输入基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `closing_arr = [251]`（基于 `positive`） | `ModelRegistryError` |
| N01a | `opening_arr[0] = True`（基于 `positive`） | `ModelRegistryError` |
| N01b | `opening_arr[0] = float('nan')`（基于 `positive`） | `ModelRegistryError` |
| N01c | `opening_arr[0] = float('inf')`（基于 `positive`） | `ModelRegistryError` |
| N01d | `opening_arr[0] = float('-inf')`（基于 `positive`） | `ModelRegistryError` |
| N02 | `opening_arr = []`（基于 `positive`） | `ModelRegistryError` |
| N03 | 删除 `opening_arr`（基于 `positive`） | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]`（基于 `positive`） | `ModelRegistryError` |
| N05a | `years = []`（基于 `positive`） | `ModelRegistryError` |
| N05b | `years = [True, ...]`（基于 `positive`） | `ModelRegistryError` |
| CONT-BREAK | {"opening_arr": [200, 251], "closing_arr": [250, 251]}（基于 `continuity_positive`） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

NEG-CARD 语义：`closing_arr` 是必填对账项；改成 `[251]` 使 FY2027 桥不平衡，冻结预期为 `ModelRegistryError`（桥平衡守卫）。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（基于 `positive`） | 与 `positive` 相同 | the ARR bridge ignores base_revenue at this entry point; design observation only, not a pass condition |
| OBS-DEFAULT-EQUIV | `usage_revenue = [0]`（基于 `defaults`） | 与 `defaults` 相同 | explicit 0 equals the omitted optional usage_revenue; makes the documented default falsifiable |
| OBS-GRR-ONE-SECOND-YEAR | 重放 `continuity_positive` | 与 `continuity_positive` 相同 | records whether gross_retention_rate = 1 on the FY2028 slot is accepted (the retained-ARR guard: opening_arr * grr == 0 and expansion_arr > 0); NO expectation and NO verdict is asserted |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L51/… 只给出算式与手算结果，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["subscription_arr_bridge"].formula`，与第 1 节公式逐项比对；
若不一致，记录差异而**不是**修改期望值（见文末「运行后对账」节）。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R2 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R3 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R4 | `years` 为空/非整数财年 | `ModelRegistryError` | 是（N05a/N05b） |
| R5 | `years` 非连续递增 | `ModelRegistryError` | 是（CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R7 | 卡片专属的**运行时**拒绝条件 | `ModelRegistryError` | 是（NEG-CARD） |
| R8-BIZ | NRR 当作 GRR | **业务拒绝**：需 `special_review`，本卡记录为披露缺口 | 否（不是运行时契约） |
| R9-BIZ | ARR 当作收入 | **业务拒绝**：卡片 L57 明示 ARR ≠ 收入 | 否 |
| R10-BIZ | 没有存续期初 ARR 却给存量扩张 | **业务拒绝**：卡片 L57 明示 | 否 |

R8-BIZ–R10-BIZ 是**业务拒绝**条件（卡片「专业决策/业务负例」节），不在运行时契约内，因此在运行时负例表里不计入 pass/fail；它们属于 `disclosure_adaptation` 的 STOP 条件。
## 9. 披露采集与基期锚点（D/E 输入，不在本卡授予资格）

- 披露采集项：ARR 桥、GRR 定义、存续客户扩张、新增、各发生月份、用量与基期锚点（`card_M24.md` L55）。
- 基期锚点：`{"field":"base_arr_parameter_id","driver":"opening_arr","dimension":"revenue"}`（`card_M24.md` L59；亦见生产 `scripts/model_extensions.py:18` 的 `EXTENSION_OPENING_BALANCES`）。
- 本卡只交付 A–C 公式证据；D/E 由 I-10-A 先行执行，F 需 I-12 冻结设计。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M24/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，且需「一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅」。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），该设计不存在；本卡不作准确性主张。

## 11. 停止条件自检（卡片「停止条件」节）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：本卡适用，落地为第 4/5 节。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

---

（以下为运行后追记节，由 `scripts/append_oracle_run_section.py` 追加；
上方正文在运行前冻结，追加不改动任何期望值。）