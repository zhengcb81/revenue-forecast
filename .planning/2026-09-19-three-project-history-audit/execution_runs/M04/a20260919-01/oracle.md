# M04 · capacity_utilization — 冻结 oracle（运行前写定）

Card: M04（`execution_v2/card_M04.md`），Parent I-10。Attempt `execution_runs/M04/a20260919-01`。
本文在**任何产品代码运行之前**写定；写入后不得为贴合结果而修改。

## 0. 独立性声明

- 全部数值预期来自**手算**与独立脚本 `scripts/oracle_M04.py`（仅 `decimal`/`json` 标准库，
  **不 import 产品任何模块**），以及**已披露的年报原文**。
- **绝不**调用 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 实现入口仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式 | `revenue[t] = capacity[t] × utilization[t] × yield[t] × unit_revenue[t] × timing_factor[t] + other_revenue[t]` | `card_M04.md` L8、L42 |
| 口径链 | 满年**毛产能件数** → ×利用率 → ×良率 → ×U/合格件 → ×投产比例 → +其他收入 | `card_M04.md` L8 |
| 必填 driver | `capacity`、`utilization`、`yield`、`unit_revenue` | `card_M04.md` L9 |
| 可选 driver / 默认 | `timing_factor` 默认 **1.0**、`other_revenue` 默认 **0.0** | `card_M04.md` L9 |
| 单位 | `capacity` 件数（quantity，满年）；`utilization`/`yield`/`timing_factor` 无量纲比率；`unit_revenue` = **U/合格件**；`other_revenue` 金额（signed） | `card_M04.md` L8 + I-10 表 |
| 允许范围 | `capacity ∈ [0, +inf)`；`utilization ∈ [0,1]`；`yield ∈ [0,1]`；`unit_revenue ∈ [0, +inf)`；`timing_factor ∈ [0,1]`；`other_revenue ∈ (-inf,+inf)` | `card_M04.md` L44 + `model_ledger.jsonl` 第 4 行 "利用率和良率 [0,1]" |
| 来源字段 | 设计/有效/**合格**产能、投产日、利用率分母、良率、库存变化、售价 | `card_M04.md` L46 |
| 驱动独立性 | `unit_revenue` 必须对应"每**合格件**"；产能必须明确是**投入口径**还是**合格品口径** | I-10 表 |
| 确认时滞 | `timing_factor` 仅表达未含在 `capacity` 内的投产时间比例；**已含投产时间的平均产能不得再乘** | I-10 表 |
| 硬约束 | 输出长度 = `len(years)`；`years` 连续递增；输出非负 | 卡片 |
| 不可识别参数 | 实际**产量**、**销量**、库存变化全部不可识别 → **产销差必须外部桥接** | `card_M04.md` L48 |
| 业务负例 | ①合格产能不能重复扣良率；②平均产能不能重复乘投产比例；③产销差须桥接 | `card_M04.md` L48 |

## 2. 合成正例（positive）

输入（=`card_M04.md` L12-40 原文）：

```json
{"model_id": "capacity_utilization", "base_revenue": 0,
 "drivers": {"capacity": [1000], "utilization": [0.8], "yield": [0.9], "unit_revenue": [2],
             "timing_factor": [0.5], "other_revenue": [10]},
 "years": [2027]}
```

手算：`1000 × 0.8 = 800`；`800 × 0.9 = 720`；`720 × 2 = 1440`；`1440 × 0.5 = 720`；`720 + 10 = 730`
→ **期望输出 `[730]`**（卡片 L42 一致）。

- 长度 1 = `len(years)`；容差 `1e-9 × max(1, 730) = 7.3e-7`。
- 顺序敏感性：`yield` 与 `utilization` 都是乘数，交换顺序数值不变；但**产能口径**不同（投入 vs 合格品）
  会重复扣良率，属于 D 阶段口径检查（见第 6 节 R9）。

## 3. 运行负例 A（卡片专属）

只替换 `drivers` 为 `{"utilization": [1.1]}` → 预期 `ModelRegistryError`。
通过判据：目标异常类型必须是 `ModelRegistryError`。

## 4. 公共负例 N01–N05

首个必填 driver = `capacity`。每例新 deepcopy；内存构造（不经 JSON 解析器）。

| 例 | 变换 | 冻结预期 |
|---|---|---|
| N01a–d | `capacity[0] = True / nan / inf / -inf` | 各 `ModelRegistryError` |
| N02 | `capacity = []` | `ModelRegistryError` |
| N03 | 删除 `capacity` | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError` |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]` | `ModelRegistryError` |

## 5. 连续性 / 额外检查

- `capacity_utilization` 是**乘数流量**模型，无期初/期末存量桥 → 存量桥 **not_applicable_with_reason**。
- Continuity positive：`capacity=[100,120]`、`utilization=[0.8,0.8]`、`yield=[0.9,0.9]`、
  `unit_revenue=[2,2]`、`timing_factor=[1,1]`、`other_revenue=[0,0]`，`years=[2027,2028]`
  → 手算 `[144, 172.8]`，先运行通过。
- Continuity 断裂 patch：`years=[2027,2029]` → 预期 `ModelRegistryError`。
- **默认值检查**：只给必填 `capacity=[1000]`、`utilization=[0.8]`、`yield=[0.9]`、`unit_revenue=[2]`
  → 预期 `[1440]`（`timing_factor`=1.0、`other_revenue`=0.0）。
- **额外拒绝检查（冻结预期）**：
  - `yield = [1.2]` → `ModelRegistryError`（ratio 域）
  - `utilization = [-0.1]` → `ModelRegistryError`
  - `capacity = [-1]` → `ModelRegistryError`
  - `unit_revenue = [-2]` → `ModelRegistryError`
  - `other_revenue = [-2000]` → `ModelRegistryError`（净收入为负）

## 6. 拒绝条件

| ID | 拒绝条件 | 冻结预期 |
|---|---|---|
| R1 | `utilization ∉ [0,1]`（如 1.1） | `ModelRegistryError` |
| R2 | `yield ∉ [0,1]`（如 1.2） | `ModelRegistryError` |
| R3 | `capacity < 0` / `unit_revenue < 0` | `ModelRegistryError` |
| R4 | 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` |
| R5 | 缺任一必填 driver | `ModelRegistryError` |
| R6 | 未注册 driver | `ModelRegistryError` |
| R7 | `years` 空/非连续/非整数（含 `True`） | `ModelRegistryError` |
| R8 | 非有限或 bool 冒充数值 | `ModelRegistryError` |
| R9 | **业务拒绝**：合格品产能上再乘 `yield` | 重复扣良率；须把 `yield` 置 1 或改用投入口径产能 |
| R10 | **业务拒绝**：平均产能（已含投产时间）再乘 `timing_factor` | 重复折算，停止 |
| R11 | **业务拒绝**：用产量冒充销量 | 产销差须库存桥，不得直接当已确认收入 |

## 7. 披露映射（至少一份实际披露：中芯国际 2024 年报）

**来源**：中芯国际集成电路制造有限公司 2024 年年度报告
（`C:\Users\郑曾波\Projects\company-wiki\companies\中芯国际\raw\financial_reports\中芯国际：中芯国际2024年年度报告.pdf`，
222 页，PDF sha256 `d0d08d76…`；sidecar 仅含 `market`/`security_id`/`source_title`，
**缺少 provider 回执与 URL**，属**部分溯源**，见 `disclosure_mapping.json` 的 provenance 说明）。

| 参数 | 原文位置 | 原文 | 原单位 | 转换 |
|---|---|---|---|---|
| `capacity`（满年毛产能） | P6「致股东的信」+ P84「(2) 出货量、晶圆产能」 | 「2024 年末，晶圆月产能为 94.8 万片折合 8 英寸标准逻辑」 | 万片/月（8 英寸标准逻辑） | `948,000 片/月 × 12 月 = 11,376,000 片/年`（**年化期末**口径） |
| `utilization` | P6「致股东的信」 | 「产能利用率 85.6%」 | % | `0.856` |
| `units`（已售晶圆，对账用） | P84「(2) 出货量、晶圆产能」 | 「本集团销售晶圆的数量为 802.1 万片折合 8 英寸标准逻辑」 | 万片 | `8,021,000 片` |
| 收入（对账目标） | P8「近三年主要会计数据」 | 行「营业收入」列「2024年」= `57,795,570`（单位：千元，币种：人民币） | 千元 | `57,795,570,000 元`（2023 年 `45,250,425` 千元） |
| `yield` | — | **公司未披露数值良率**；P13/P34 仅定性提及 | — | 令 `yield = 1`：披露的「产能利用率」已是**有效产出/可用产能**口径，良率损失已内含（见 `decision.md` DEC-M04-2） |
| `timing_factor` | — | = 1，因为 `capacity` 用的是**满年**年化产能 | — | 不得再乘投产比例 |
| `other_revenue` | — | = 0，未拆分其他收入 | — | 不假设 |

**对账 A（期末产能年化口径，主映射；容差运行前冻结：相对 0.5%，即 ≤ 8,021 片）**：

```
容量(片/年) = 948,000 × 12 = 11,376,000
× utilization 0.856 = 9,737,856 片
× yield 1            = 9,737,856 片（合格产出）
unit_revenue = 57,795,570,000 / 9,737,856 = 5,935.14... 元/片   ← 由披露收入除以模型产出推导
重建收入 = 9,737,856 × 5,935.14... = 57,795,570,000 元
披露收入 = 57,795,570,000 元（P8）
残差 = 0 元（构造性恒等，不构成独立证据）
```

**与已披露出货量核对（这一步才有信息量）**：模型产出 `9,737,856 片`（年化期末产能口径）
vs 披露已售 `8,021,000 片` → **差 +1,716,856 片，相对 21.40%**，**远超声明的 0.5% 容差**。

**结论（必须如实记录，不得弱化）**：
1. 「期末月产能 × 12」**不是**「年度可用（平均）产能」；中芯 2024 年全年在扩产，期末产能高于全年平均。
2. 因此 `capacity_utilization` 在其**文档化口径**（满年毛产能）下**无法**用"期末产能年化"复现已披露出货量；
   要使用本模型，D 阶段必须提供**平均可用产能**（或引入明确的产能爬坡桥），
   这是一个**未解决的披露适配缺口**，属 `STOP_DISCLOSURE_ADAPTATION` 方向，交行业/会计 reviewer 裁定。
3. 反向推算（仅作诊断，不作为参数）：由披露出货量 8,021,000 与利用率 0.856 可得
   隐含年度可用产能 = `8,021,000 / 0.856 = 9,370,327.10 片`（月均 `780,860.59` 片），
   仅为期末年化产能的 **82.37%**。**不得**用该反推值冒充披露参数（I-10-A 第 3 条禁止用收入倒推参数后称独立验证）。
4. 全文检索「良率」仅命中 P13（风险量产阶段…产品良率提升）与 P34（…产品良率保证）两处**定性**表述，
   无数值良率披露（探针命中数 2）。

## 8. 三种资格

- `formula`：由 A–C 结果决定；实现者不自签 accepted。
- `disclosure_adaptation`：**unmapped**，且本卡**主动记录一处未解决的缺口**（第 7 节结论 2：
  口径分母缺失），因此不得以"有映射"为由填通过。
- `accuracy`：**unproven**（F 需 I-12 冻结设计）。

## 9. 停止条件自检

- 正例不等或负例未被拒 → `STOP_FORMULA`，先记录反例，不改实现。
- 单位/会计/期初锚点/收入历史桥未解决 → `STOP_DISCLOSURE_ADAPTATION`：
  本卡**命中该停止条件**（可用产能分母未披露），故 disclosure 资格保持 unmapped 并显式记录原因。
- 存量桥 → **not_applicable**（乘数流量模型，无 opening/closing 项）；产销库存桥为外部义务，未完成。
- 准确性 → `STOP_ACCURACY`。

---

## 修订 r2 索引（独立复审后追加，非重写）

**本节为事后补记：r2 轮曾声称已追加本节但实际未落盘。**

- 事实（盘上可核）：r2 稿件在 `review.md` 的 `### Frozen expectations were NOT rewritten` 段逐字声称
  "`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body"，
  但盘上 `oracle.md` 当时**没有任何 r2 段**，也从未被追加过。
- 根因（点复审定位）：共享脚本 `scripts/apply_r2_patches.py` 把 `oracle.md` 的追加**写死在
  `if card == "M03":` 分支内**；M01 的 r2 段由仅存在于 M01 的 `scripts/finalize_r2.py` 写入。
  本卡两者都不适用，因此 r2 的处置只落在 `review.md`、`evidence/<card>/revision_r2.json`
  与 `handoff.json`，**oracle 层无载体**。
- 后果与取舍：`source_manifest.json` 对本卡显示 MATCH，**恰恰因为从未追加**，
  **不得**读成"账目更规范"，也不得读成"已响应复审"。
- 本卡追加前状态（点复审实测，本 attempt 复算一致）：**10495 B**，sha256 `1a69465bf1f12e12122e9596e78faf7028f73fae2f6b3431cb199298d24f7c5c`。
  下方补记的其他小节亦为 r4 追加，属同一性质。
- 三点状态索引（本卡适用者）：
  - `F-M01-02`（退出码承载裁决）：CLOSED。`run_card.py` 现为 rc=0 仅在正例在容差内、
    连续性正例通过且全部负例被 `ModelRegistryError` 拒绝时给出；rc=2 = positive 输入损坏致无裁决；
    rc=3 = 裁决为负；rc=1 = guard 之外的 harness 缺陷。本卡自检见
    `recovery/r2_exit_code_selfcheck/selfcheck_result.json`（A=3/B=1/C=0/D=2）。
  - `F-M01-03`（交付目录/编码）：CLOSED。`changes.diff`、`after/`、`recovery/README.md` 已补，
    日志统一 UTF-8。
  - `F-M02-01`（被忽略字段是否仍须满足域约束）：**保留待 owner 裁定**，未自决、未改产品；
    见 `decision.md` DEC-M02-3 与 `handoff.json.open_questions`。
- **本节不改变任何数值结论**：正例/负例预期、容差、披露映射数值、拒绝条件与三种资格均未改动。
