# M22 · milestone_royalty · 里程碑与销售分成 — 冻结 oracle（运行前写定）

Card M22（`execution_v2/card_M22.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M22/a20260919-01`。
本文在**任何产品代码运行之前**写定；写入后不得为贴合结果而修改，运行后的对账只允许以**追加**节形式补记（见文末「运行后对账」节）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M22.py` 用 Python 标准库（`decimal`/`json`/`hashlib`/`os`/`argparse`）复算。
  该脚本**不 import** 产品任何模块（`model_registry` / `model_extensions` 均不出现），
  自检记录见 `evidence/M22/oracle_selfcheck.json`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M22.md` L8、L36「手算：500×0.08+12+3=55」。
- 入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_registry.py:242`。 该入口仅在冻结之后用于定位调用点。
- `evidence/M22/oracle.json` 可由该脚本**逐字节重生成**（无时间戳、无随机量、无字典序依赖）。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | revenue = eligible_sales × royalty_rate + milestone_revenue + service_revenue | `card_M22.md` L8 |
| 必填 driver | `eligible_sales`、`royalty_rate` | `card_M22.md` L9 |
| 可选 driver / 默认 | `milestone_revenue`（默认 0）、`service_revenue`（默认 0） | `card_M22.md` L9 |
| 单位 | 合同可分成销售 U × 分成率；里程碑/服务是已确认 U。 | `card_M22.md` L8 |
| 适用 | 授权药物、专利、内容，开发授权至成熟。 | `card_M22.md` L7 |
| 硬约束 | 输出长度 = `len(years)`；逐年检查；非有限值/布尔冒充数值一律拒绝 | 通用契约 |
| 比例域 | 维度为 `ratio` 的 driver 默认域 [0,1]；本卡**不声称**经济上永不可能 | `common_model_cards.md` L11 |
| 存量桥 | `milestone_royalty` **不是存量桥**（无期初/期末对账项），STOP_BRIDGE → **not_applicable_with_reason**；适用的连续性检查只有财年连续性。 | `card_M22.md` L133 |

## 2. 合成正例（positive）

输入 = `card_M22.md` 合成输入原文（逐字段一致）：

```json
{
 "model_id": "milestone_royalty",
 "base_revenue": 0,
 "drivers": {
  "eligible_sales": [
   500
  ],
  "royalty_rate": [
   0.08
  ],
  "milestone_revenue": [
   12
  ],
  "service_revenue": [
   3
  ]
 },
 "years": [
  2027
 ]
}
```

手算（逐步，未取整）：

- 500 x 0.08 = 40; 40 + 12 + 3 = 55

**期望输出 = `['55.00']`**（与卡片手算一致）。
- 输出长度 = 1 = `len(years)`；输出年份应为 `[2027]`。
- 逐值容差 = `1e-9 × max(1, |expected|)` = `[5.5e-08]`。
- 除数值外还比对**输出结构**：类型为 list、长度等于 `len(years)`、每个元素为有限 float（见 `formula_result.json` 的 `structure_checks`）。

## 3. 默认值案例（defaults）

只给必填 driver，省略全部可选 driver：

```json
{
 "model_id": "milestone_royalty",
 "base_revenue": 0,
 "drivers": {
  "eligible_sales": [
   500
  ],
  "royalty_rate": [
   0.08
  ]
 },
 "years": [
  2027
 ]
}
```

手算：milestone_revenue omitted -> 0; service_revenue omitted -> 0; 500 x 0.08 = 40。

**期望输出 = `['40.00']`**，长度 1。
- 该案例证明默认值确实被应用，且**没有**被错当成「必填缺失」。
- 默认值不是缺披露时填零/一的授权（`common_model_cards.md` L22）；本案例只检验契约行为。
- 默认值案例**不参与**运行器退出码判定（`defaults_ok_not_gating`）。

## 4. 连续性案例（continuity）

本卡无存量桥，故 CONT-BREAK 采用**财年断裂**：`years = [2027, 2029]`（缺 2028），预期 `ModelRegistryError`。

- Continuity positive：`years = [2027, 2028]`；手算：
  - FY2027 = 500 x 0.08 + 12 + 3 → 55.00
  - FY2028 = 0 x 0.08 + 4 + 0 → 4.00
  期望 = `['55.00', '4.00']`。此例**先**运行通过，才允许应用断裂 patch。
- Continuity 断裂 patch：`years = [2027, 2029]`（缺 2028，财年不连续）
  → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `eligible_sales`。每个负例使用**新的 deepcopy 独立输入**，互不共享可变对象；全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在冻结输入基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `royalty_rate = float('1.01')`（基于 `positive`） | `ModelRegistryError` |
| N01a | `eligible_sales[0] = True`（基于 `positive`） | `ModelRegistryError` |
| N01b | `eligible_sales[0] = float('nan')`（基于 `positive`） | `ModelRegistryError` |
| N01c | `eligible_sales[0] = float('inf')`（基于 `positive`） | `ModelRegistryError` |
| N01d | `eligible_sales[0] = float('-inf')`（基于 `positive`） | `ModelRegistryError` |
| N02 | `eligible_sales = []`（基于 `positive`） | `ModelRegistryError` |
| N03 | 删除 `eligible_sales`（基于 `positive`） | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]`（基于 `positive`） | `ModelRegistryError` |
| N05a | `years = []`（基于 `positive`） | `ModelRegistryError` |
| N05b | `years = [True, ...]`（基于 `positive`） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 `continuity_positive`） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

NEG-CARD 语义：`royalty_rate` 是卡片 L9 的必填比例项；`1.01` 越出 ratio 契约 [0,1]，冻结预期为 `ModelRegistryError`。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（基于 `positive`） | 与 `positive` 相同 | the royalty calculation ignores base_revenue at this entry point; design observation only, not a pass condition |
| OBS-DEFAULT-EQUIV | {"milestone_revenue": [0], "service_revenue": [0]}（基于 `defaults`） | 与 `defaults` 相同 | explicit 0/0 equals the omitted default; makes the documented default falsifiable |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L51/… 只给出算式与手算结果，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["milestone_royalty"].formula`，与第 1 节公式逐项比对；
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
| R8-BIZ | 概率加权潜在付款当作已确认收入 | **业务拒绝**：需 `special_review`，本卡记录为披露缺口 | 否（不是运行时契约） |
| R9-BIZ | 研发事件与商业条件未分开 | **业务拒绝**：需 `special_review` | 否 |
| R10-BIZ | 阶梯分成率被压成单一费率而未披露 | **业务拒绝**：需 `special_review` | 否 |

R8-BIZ–R10-BIZ 是**业务拒绝**条件（卡片「专业决策/业务负例」节），不在运行时契约内，因此在运行时负例表里不计入 pass/fail；它们属于 `disclosure_adaptation` 的 STOP 条件。
## 9. 披露采集与基期锚点（D/E 输入，不在本卡授予资格）

- 披露采集项：分成基础、阶梯率、地域期限、里程碑触发、义务与确认金额（`card_M22.md` L40）。
- 基期锚点：无（本卡卡片未给基期锚点字段）。
- 本卡只交付 A–C 公式证据；D/E 由 I-10-A 先行执行，F 需 I-12 冻结设计。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M22/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，且需「一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅」。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），该设计不存在；本卡不作准确性主张。

## 11. 停止条件自检（卡片「停止条件」节）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 1 节）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

---

（以下为运行后追记节，由 `scripts/append_oracle_run_section.py` 追加；
上方正文在运行前冻结，追加不改动任何期望值。）