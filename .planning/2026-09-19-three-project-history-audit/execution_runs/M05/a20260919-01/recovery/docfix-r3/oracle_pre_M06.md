# M06 · usage_platform — 冻结 oracle（运行前写定）

Card: M06（`execution_v2/card_M06.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M06/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 第 1–5 节全部数值预期来自**手算**，并由本 attempt 内独立脚本 `scripts/oracle_M06.py`
  用 Python 标准库复算；该脚本**不 import** 产品任何模块。
- **绝不**通过调用 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M06.md` L8「单位/口径：活动单位×U/活动单位；monetization_rate 不是默认概率」
  与 L33「手算：500×0.04+3=23」。实现入口 `model_registry.py:226` 仅在冻结后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 合格活动量 × U/活动单位 + 固定收入` | `card_M06.md` L8、L33 |
| 必填 driver | `eligible_activity`、`monetization_rate` | `card_M06.md` L9 |
| 可选 driver / 默认 | `fixed_revenue` 默认 `0` | `card_M06.md` L9 |
| 单位 | `eligible_activity` = 活动单位数；`monetization_rate` = **U/活动单位（货币/活动，不是百分比概率）**；`fixed_revenue` = U；输出 = U | `card_M06.md` L8；`model_ledger.jsonl` RF-MODEL-usage_platform「不能因名称含 rate 而当百分比」 |
| 量纲 | 活动 × (U/活动) = U；`monetization_rate` 量纲为 revenue_per_activity | 量纲自检 |
| 允许范围 | 活动量非负；`monetization_rate` 非负（比率维 [0,1] 的百分号解释**不适用**） | 通用契约 |
| 会计口径 | 若活动量是 GMV，需与 take rate 单位及**总额/净额**政策对应；principal/agent 不明则停止 | `card_M06.md` L39 业务负例 |
| 补贴/退款 | 补贴、退款、促销转化必须有独立定义，不得隐含在 rate 内 | `card_M06.md` L37 |
| 确认时滞 | 模型内无时滞项；逐期确认 | 通用契约 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；不允许负活动量 | 通用契约 |

## 2. 合成正例（positive）

输入（=`card_M06.md` L12-31 原文）：

```json
{"model_id": "usage_platform", "base_revenue": 0,
 "drivers": {"eligible_activity": [500], "monetization_rate": [0.04], "fixed_revenue": [3]},
 "years": [2027]}
```

手算：500 × 0.04 = 20；20 + 3 = **23**。

**期望输出 = `[23]`**（与卡片 L33 原文一致）。输出长度 = 1 = `len(years)`。
容差 = `1e-9 × max(1, 23)` = 2.3e-8。

## 3. 默认值案例（defaults）

省略 `fixed_revenue`（optional，默认 0）：

```json
{"model_id": "usage_platform", "base_revenue": 0,
 "drivers": {"eligible_activity": [500], "monetization_rate": [0.04]},
 "years": [2027]}
```

手算：500 × 0.04 + **0（默认）** = **20**。**期望输出 = `[20]`**，长度 1。

## 4. 连续性案例（continuity）

`usage_platform` 是**逐年独立的流量模型，不是存量桥**（无期初/期末对账项）→
存量桥资格 **not_applicable_with_reason**；适用的是跨年财年连续性。

- Continuity positive：`years=[2027,2028]`，
  `eligible_activity=[500, 800]`，`monetization_rate=[0.04, 0.05]`，`fixed_revenue=[3, 4]`
  手算：2027 = 500×0.04+3 = 20+3 = **23**；2028 = 800×0.05+4 = 40+4 = **44**。
  期望 = `[23, 44]`。此例**先**运行通过。
- Continuity 断裂 patch：`years=[2027,2029]` → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `eligible_activity`（注意**不是** `monetization_rate`）。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `eligible_activity = [-1]` | `ModelRegistryError` |
| N01a | `eligible_activity[0] = True` | `ModelRegistryError` |
| N01b | `eligible_activity[0] = float('nan')` | `ModelRegistryError` |
| N01c | `eligible_activity[0] = float('inf')` | `ModelRegistryError` |
| N01d | `eligible_activity[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `eligible_activity = []` | `ModelRegistryError` |
| N03 | 删除 `eligible_activity` | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError` |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]` | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive） | `ModelRegistryError` |

合计 **11 个负例**。只有 `ModelRegistryError` 才算通过；import/file 错误记为 FAIL。

NEG-CARD 语义：负的活动量（GMV/调用次数/支付笔数为负）无经济意义，
现行非负域拒绝之；本卡**不声称**经济上永不可能（`common_model_cards.md` L11）。
`monetization_rate` 的边界：**不断言** [0,1]——该 driver 的维是 revenue_per_activity，
名字里的 "rate" 不构成百分比证据（`card_M06.md` L8、L39）。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999` | 输出与正例相同 | `_rowwise` 丢弃 `base_revenue`；设计观察，非通过条件 |
| OBS-RATE-GT1 | `monetization_rate = [1.5]` | **仅登记实际行为，不设预期** | 用于判断 "rate 名称是否被当成比例" 的经验事实；不得据此判定模型错误 |

`OBS-RATE-GT1` 是把卡片 L8/L39 的业务警告变成可复核事实的最小探针：
若实现把 `monetization_rate` 限制在 [0,1]，则 "货币/活动" 语义与契约不一致，
需交专业判定（不自行改实现、不据此宣布失败）。

## 7. 卡片文字 vs 实现公式串（须核对）

卡片未给实现公式串。运行后从隔离副本读取 `MODEL_REGISTRY["usage_platform"].formula`，
与第 1 节公式逐项比对；不一致则记录差异，**不改期望值**。

## 8. 拒绝条件

| ID | 拒绝条件 | 冻结预期 | 可运行时执行 |
|---|---|---|---|
| R1 | 负活动量 | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)` | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 空/非连续/非整数 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值/bool 冒充数值 | `ModelRegistryError` | 是（N01a-d） |
| R7 | GMV、支付额、调用次数混用同一条驱动 | **业务拒绝**：需 `special_review` | 否 |
| R8 | principal/agent（总额 vs 净额）口径不明 | **业务拒绝**：STOP_DISCLOSURE_ADAPTATION | 否 |
| R9 | 补贴/退款未单列而隐含进 rate | **业务拒绝** | 否 |
| R10 | 把 `monetization_rate` 当百分比概率使用 | **业务拒绝** | 否（OBS-RATE-GT1 只记录事实） |

## 9. 三种资格（本卡只填 formula）

- `formula`：由 A–C 结果决定；实现者不自签 accepted。
- `disclosure_adaptation`：**unmapped**（D 需独立签署的逐字段映射与已结束期间对账）。
- `accuracy`：**unproven**（F 需 I-12 冻结设计）。

## 10. 停止条件自检

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，先记录反例。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**。
- 准确性：`STOP_ACCURACY`。

---

## 修订 r2（独立复审意见的追加处置，非重写）

本节由修订 r2 **追加**。上方正文（v1 冻结版）**逐字未改**：正例/连续性/默认值预期、容差、负例清单、披露数值**一律未改**，实现与产品也**一行未动**。
本节追加前 `oracle.md` sha256 = `d335f5ec2a699bef008686249d77f2f9af6e2b6306510e57a83446f92df7e3eb`。

复审结论（独立 session 给出）：**M06 = accepted_scoped（仅 formula 资格）**

### 本轮处置清单

- F-M06-01 (source_manifest wording)
- F-M06-02 (review.md exit-code section title)
- OQ-02 ruling
- **F-M06-01 更正**：`source_manifest.json` 的 `oracle_document.honest_gap` 原文称「pre-run hash was captured in commands.json」，但 `commands.json` 只记 argv/rc、不含 oracle.md 的 sha256。已改写该句，并补 `mtime_ordering`（oracle.md mtime 早于产品 stdout mtime）作为可核链条。
- **OQ-02 裁定（复审）**：`monetization_rate` 无 [0,1] 界**不是契约缺口**，只是命名歧义；枚举证据见 `evidence/M06/oq_rulings.json`。
- **OQ-04 裁定（复审维持）**：`model_registry.py:335` 静默补 0 成立；登记不改代码。
- **F-M06-02 更正**：`review.md` 退出码小节标题改为`(shared runner; self-check performed on M05)`。

### 未改动的内容（防止误读为「为过审而改」）

- 正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、停止条件、披露数值**一律未改**。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。

---

## 修订 r2（独立复审意见的追加处置，非重写）

本节由修订 r2 **追加**。上方正文（v1 冻结版）**逐字未改**：正例/连续性/默认值预期、容差、负例清单、披露数值**一律未改**，实现与产品也**一行未动**。
本节追加前 `oracle.md` sha256 = `c07da2412b2e27faa33405878383001336ef1d8ce88c7c9ffd70a8209ffaea7b`。

复审结论（独立 session 给出）：**M06 = accepted_scoped（仅 formula 资格）**

### 本轮处置清单

- F-M06-01 (source_manifest wording)
- F-M06-02 (review.md exit-code section title)
- OQ-02 ruling
- **F-M06-01 更正**：`source_manifest.json` 的 `oracle_document.honest_gap` 原文称「pre-run hash was captured in commands.json」，但 `commands.json` 只记 argv/rc、不含 oracle.md 的 sha256。已改写该句，并补 `mtime_ordering`（oracle.md mtime 早于产品 stdout mtime）作为可核链条。
- **OQ-02 裁定（复审）**：`monetization_rate` 无 [0,1] 界**不是契约缺口**，只是命名歧义；枚举证据见 `evidence/M06/oq_rulings.json`。
- **OQ-04 裁定（复审维持）**：`model_registry.py:335` 静默补 0 成立；登记不改代码。
- **F-M06-02 更正**：`review.md` 退出码小节标题改为`(shared runner; self-check performed on M05)`。

### 未改动的内容（防止误读为「为过审而改」）

- 正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、停止条件、披露数值**一律未改**。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。
