# M25 · installed_base_aftermarket — 冻结 oracle（运行前写定）

Card: M25（`execution_v2/card_M25.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M25/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 第 1、2、3、4 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M25_M28.py`（sha256 `d443b5d5bcf5f49f8f442df71b99f774a74422d393f038b9dca14bbe9a6a6e5e`）
  用 Python 标准库（`decimal`/`json`/`hashlib`）复算。该脚本**不 import** 产品任何模块
  （`model_registry` / `model_extensions` 均不出现），自检见 `evidence/M25/oracle_selfcheck.json`
  （`product_import_present = false`）。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M25.md` L8「装机台数桥×年度暴露×付费覆盖率×U/付费台年」与 L48 原文手算
  「200+40−20=220；暴露200+40×0.25−20×0.5=200；200×0.5×3=300」。
  实现入口 `scripts/model_registry.py:308`、注册 `scripts/model_extensions.py:185` 仅在冻结之后
  用于定位调用点；本卡的公式串是**从卡片与手算独立写出**的，运行后再与实现的公式串逐项比对。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式 | `收入 = (期初装机 + 新增装机×新增收入系数 − 退役装机×退役损失系数) × 付费覆盖率 × U/付费台年` | `card_M25.md` L8、L48 |
| 库存桥（必须先成立） | `期末装机 = 期初装机 + 新增装机 − 退役装机`；跨年 `期初(t) = 期末(t−1)` | `card_M25.md` L48、L118 |
| 必填 driver | `opening_installed_units`、`new_installed_units`、`retired_units`、`closing_installed_units`、`new_unit_revenue_fraction`、`retirement_lost_fraction`、`attach_rate`、`annual_revenue_per_attached_unit` | `card_M25.md` L9 |
| 可选 driver / 默认 | 无（`optional = ()`，卡片 L9 写「可选默认：`{}`」） | `card_M25.md` L9 |
| 单位 | 台（unit）；`new_unit_revenue_fraction`/`retirement_lost_fraction`/`attach_rate` 无量纲比例；`annual_revenue_per_attached_unit` = U/付费台年；输出 = U | `card_M25.md` L8 |
| 量纲 | 台 × 比例 × 比例 × (U/台) = U | 量纲自检 |
| 语义域（实现契约，运行前从卡片与公共规则推定，运行后核对） | 四个台数 driver 为 `quantity` 维（下界 0）；`new_unit_revenue_fraction`、`retirement_lost_fraction`、`attach_rate` 为 `ratio` 维 → 默认 [0,1]；无显式 `driver_bounds` | `common_model_cards.md` L24-30 + 通用契约 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；`retired_units` 不得超过期初装机；收入非负 | 通用契约 |
| 业务口径 | 当期新增退役不属于期初退役群组；设备龄差与合同/耗材重复收费需 `special_review` | `card_M25.md` L54 |

## 2. 合成正例（positive）

输入（=`card_M25.md` L12-46 原文）：

```json
{"model_id": "installed_base_aftermarket", "base_revenue": 0,
 "drivers": {"opening_installed_units": [200], "new_installed_units": [40], "retired_units": [20],
             "closing_installed_units": [220], "new_unit_revenue_fraction": [0.25],
             "retirement_lost_fraction": [0.5], "attach_rate": [0.5],
             "annual_revenue_per_attached_unit": [3]},
 "years": [2027]}
```

手算（逐步，未取整）：

1. 库存桥：200 + 40 − 20 = **220**（= 冻结的 `closing_installed_units`，桥成立）。
2. 年度暴露：200 + 40×0.25 − 20×0.5 = 200 + 10 − 10 = **200**。
3. 收入：200 × 0.5 × 3 = **300**。

**期望输出 = `[300]`**（与卡片 L48 原文一致）。
- 输出长度 = 1 = `len(years)`；年份应与 `years` 相同（`years` 长度、输出长度、输出字段集三项都断言）。
- 容差：`abs(actual − expected) <= 1e-9 × max(1, abs(expected))` = 3e-7。

## 3. 默认值案例（defaults）

本卡 `optional = ()`、`defaults = {}`，**没有**可选 driver，因此不存在"省略后取默认"的案例。
可运行且有意义的 defaults 案例是**全零显式输入**：

```json
{"model_id": "installed_base_aftermarket", "base_revenue": 0,
 "drivers": {"opening_installed_units": [0], "new_installed_units": [0], "retired_units": [0],
             "closing_installed_units": [0], "new_unit_revenue_fraction": [0],
             "retirement_lost_fraction": [0], "attach_rate": [0],
             "annual_revenue_per_attached_unit": [0]},
 "years": [2027]}
```

手算：桥 0+0−0=0 成立；暴露 0+0×0−0×0 = 0；收入 0×0×0 = **0**。

**期望输出 = `[0]`**，长度 1。
- 该案例证明"零"是一个**必须显式给出**的输入，而不是实现替披露补的默认值；
  本卡不主张"缺披露可填零"（`common_model_cards.md` L22）。此案例**不 gating**。

## 4. 连续性案例（continuity）

`installed_base_aftermarket` 是**存量桥模型**（`EXTENSION_OPENING_BALANCES` 中有
`base_installed_units_parameter_id` / `opening_installed_units` / `quantity`），故 STOP_BRIDGE 的
连续性检查**适用**，不得标 not_applicable。

- Continuity positive（= `card_M25.md` L60-107 原文）：

```json
{"years": [2027, 2028],
 "drivers": {"opening_installed_units": [200, 220], "new_installed_units": [40, 0],
             "retired_units": [20, 0], "closing_installed_units": [220, 220],
             "new_unit_revenue_fraction": [0.25, 0.25], "retirement_lost_fraction": [0.5, 0.5],
             "attach_rate": [0.5, 0.5], "annual_revenue_per_attached_unit": [3, 3]}}
```

  手算：FY2027 = (200 + 40×0.25 − 20×0.5)×0.5×3 = 200×1.5 = **300**；
  FY2028：桥 220 + 0 − 0 = 220 = 期末（成立），且 期初(2028)=220 = 期末(2027)（成立）；
  暴露 220 + 0 − 0 = 220；收入 220×0.5×3 = **330**。
  期望 = `[300, 330]`（与卡片 L103-107「手算期望为330」一致）。此例**先**运行通过。
- Continuity 断裂 patch（= `card_M25.md` L108-118 原文）：
  `opening_installed_units=[200, 221]`、`closing_installed_units=[220, 221]`。
  两年**各自**平衡（220+0−0=220；221+0−0=221），但 期初(2028)=221 ≠ 期末(2027)=220 → 预期
  `ModelRegistryError`（连续性）。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `opening_installed_units`。每个负例用**新的 deepcopy 独立输入**，互不共享可变对象；
全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 | 说明 |
|---|---|---|---|
| NEG-CARD | `retired_units=[201]`、`closing_installed_units=[39]`（卡片 L50 原文负例） | `ModelRegistryError` | 退役 201 > 期初 200；桥 200+40−201=39 也成立，故**拒绝只可能来自退役群组上限**这一条专属语义 |
| N01a | `opening_installed_units[0] = True` | `ModelRegistryError` | bool 不是数值 |
| N01b | `opening_installed_units[0] = float('nan')` | `ModelRegistryError` | 非有限 |
| N01c | `opening_installed_units[0] = float('inf')` | `ModelRegistryError` | 非有限 |
| N01d | `opening_installed_units[0] = float('-inf')` | `ModelRegistryError` | 非有限 |
| N02 | `opening_installed_units = []` | `ModelRegistryError` | 路径长度 ≠ 1 |
| N03 | 删除 `opening_installed_units` | `ModelRegistryError` | 缺必填 |
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
| OBS-DEFAULT-ZERO | 重放 defaults 案例 | 仅登记，不设预期 | 记录"零必须显式给出" |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L48 给出算式与手算 300，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["installed_base_aftermarket"].formula`，与第 1 节公式逐项比对；
若不一致，**记录差异**而不是修改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | 退役台数超过期初装机群组 | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 库存桥 `期初+新增−退役 ≠ 期末` | `ModelRegistryError` | 是（间接：NEG-CARD 的期末 39 与桥一致，故不覆盖此条；桥不成立的情形由 CONT-BREAK 覆盖跨年一侧） |
| R3 | 跨年 `期初(t) ≠ 期末(t−1)` | `ModelRegistryError` | 是（CONT-BREAK） |
| R4 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R5 | 缺必填 driver / 未知 driver | `ModelRegistryError` | 是（N03、N04） |
| R6 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R7 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R8 | 比例类 driver 越出 [0,1] | `ModelRegistryError` | 是（间接：见第 9 节"未覆盖面"，本卡未单独设例） |
| R9 | 当期新增退役置于期初退役群组；设备龄差与合同/耗材重复收费 | **业务拒绝**：需 `special_review` | 否（不是运行时契约） |
| R10 | 存量无法锚定基期（无 `base_installed_units_parameter_id`） | **业务拒绝**：STOP_BRIDGE | 否（披露侧） |
| R11 | 收入为负 | `ModelRegistryError`（通用非负域） | 间接：任何负收入路径都先被比例/数量下界拦住 |

## 9. 未覆盖面（诚实声明，供 reviewer 攻击）

- **比例域越界（R8）未被本卡任何负例真正打到**：NEG-CARD 的拒绝来自"退役群组上限"（R1），
  而非任一 `ratio` 值越界。要覆盖 R8，需要一个 `new_unit_revenue_fraction=[1.5]` 之类的例，
  本卡**未运行**该例，留给 reviewer 作为未用于编写修复的保留案例（`review_and_handoff.md` 第 5 条）。
- 本卡不重写公式：无独立反例与经审定规格时保留已修实现（`card_M25.md` L148）。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M25/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，
  且需"一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅"；本 attempt 不产出 D 的签署件。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），
  该设计不存在；本卡不作准确性主张，也不从公式通过外推准确性。

## 11. 停止条件自检（`card_M25.md` L131-136）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥（本卡适用）：连续性不成立 → `STOP_BRIDGE`。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

---

## 修订 r2（独立复核后的口径核对；追加节，非重写）

独立复核 **P2-1 不适用于本卡**：复核明确指出"**M25 的文档反而准确**"。核对如下，不改正文：

- NEG-CARD 的 patch 是 `kind="set_driver_multi"`（同时改 `retired_units=[201]` 与
  `closing_installed_units=[39]`），**不使用** `{"__float__": …}` 信封，因此不存在
  M26/M27/M28 那种"值被赋成 dict、被通用长度守卫提前拦下"的缺陷；
  实测消息为 `retired_units exceeds opening installed cohort: FY2027`，与第 5 节的
  "拒绝只可能来自退役群组上限"一致。
- 复核 P3-1 指出我此前的**转述**把 `period_hours` 的域说成开区间 `(0, inf)`；
  实际是闭区间 `[0, ∞)`（`:342` 用 `lower <= number`）。该转述出现在**口头报告**中，
  本文件从未这样写；已在本卡记录中一并更正，实质结论未变。
- 本卡在 **P3-3** 之后按 LF 重写 JSON 证据（原为 CRLF），故 `evidence/M25/*.json` 的 sha256
  与 r1 记录不同；数值与期望**一律未改**。详见 `evidence/M25/revision_r2.json` 与
  `evidence/M25/line_ending_and_blob_hashes.json`。
- 本批唯一真正"改前原样"的 `recovery/precorrection/` 就在本卡：
  `recovery/precorrection/oracle.json`（sha256 `bbe21218…`）的 defaults 期望是**错值 300**，
  与冻结件 `bbaf00ea…` 不同；其余三卡的 v1 与冻结件逐字节相同（复核 P3-7）。
