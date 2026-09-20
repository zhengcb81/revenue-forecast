# M28 · aum_fee_bridge — 冻结 oracle（运行前写定）

Card: M28（`execution_v2/card_M28.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M28/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 第 1、2、3、4 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M25_M28.py`（sha256 `d443b5d5bcf5f49f8f442df71b99f774a74422d393f038b9dca14bbe9a6a6e5e`）
  用 Python 标准库（`decimal`/`json`/`hashlib`）复算。该脚本**不 import** 产品任何模块
  （`model_registry` / `model_extensions` 均不出现），自检见 `evidence/M28/oracle_selfcheck.json`
  （`product_import_present = false`）。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M28.md` L8「资产余额流量U；带符号市场变化不等净流入；费率年度化」与
  L54 原文手算「1000+200−100−50=1050；平均1000+50−75−25=950；950×0.01+2=11.5」。
  实现入口 `scripts/model_registry.py:308`、注册 `scripts/model_extensions.py:204` 仅在冻结之后
  用于定位调用点；本卡公式串是从卡片与手算独立写出的，运行后再与实现的公式串逐项比对。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式 | `收入 = (期初AUM + 流入×流入确认系数 − 流出×流出流失系数 + 市场变化×市场变化确认系数) × 管理费率 + 已确认业绩报酬` | `card_M28.md` L8、L54 |
| AUM 桥（必须先成立） | `期末AUM = 期初AUM + 流入 − 流出 + 市场变化`；跨年 `期初(t) = 期末(t−1)` | `card_M28.md` L54、L132 |
| 必填 driver | `opening_aum`、`inflows`、`outflows`、`market_change`、`closing_aum`、`inflow_revenue_fraction`、`outflow_lost_fraction`、`market_change_revenue_fraction`、`management_fee_rate` | `card_M28.md` L9 |
| 可选 driver / 默认 | `recognized_performance_fees`，卡片 L9 声明默认 `0` | `card_M28.md` L9 |
| 单位 | AUM/流入/流出/市场变化 = U（货币余额）；`market_change` **带符号**；四个比例为无量纲；费率年度化（U/U/年）；`recognized_performance_fees` = U；输出 = U | `card_M28.md` L8 |
| 量纲 | U × (1/年) = U/年（本模型按年路径输出 U） | 量纲自检 |
| 语义域 | `opening_aum`/`inflows`/`outflows`/`closing_aum` 为 `monetary_balance`（下界 0）；`market_change` **必须显式放宽为可负**；四个比例为 `ratio` → [0,1]；`recognized_performance_fees` 为 `revenue` 维（可负） | `card_M28.md` L8、L54 + 通用契约 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；时间加权平均 AUM 不得为负；收入非负 | 通用契约 |
| 业务口径 | 不能按年末 AUM 全年收费；市场变化时点与报酬结晶须证据；需 `special_review` | `card_M28.md` L60 |

## 2. 合成正例（positive）

输入（=`card_M28.md` L12-52 原文）：

```json
{"model_id": "aum_fee_bridge", "base_revenue": 0,
 "drivers": {"opening_aum": [1000], "inflows": [200], "outflows": [100], "market_change": [-50],
             "closing_aum": [1050], "inflow_revenue_fraction": [0.25],
             "outflow_lost_fraction": [0.75], "market_change_revenue_fraction": [0.5],
             "management_fee_rate": [0.01], "recognized_performance_fees": [2]},
 "years": [2027]}
```

手算（逐步，未取整）：

1. AUM 桥：1000 + 200 − 100 + (−50) = 1000 + 200 − 100 − 50 = **1050**（= 冻结的 `closing_aum`，桥成立）。
2. 时间加权平均 AUM：1000 + 200×0.25 − 100×0.75 + (−50)×0.5 = 1000 + 50 − 75 − 25 = **950**。
3. 管理费收入：950 × 0.01 = **9.5**。
4. 加已确认业绩报酬：9.5 + 2 = **11.5**。

**期望输出 = `[11.5]`**（与卡片 L54 原文一致）。
- 输出长度 = 1 = `len(years)`；年份应与 `years` 相同（`years` 长度、输出长度、输出字段集三项都断言）。
- 容差：`abs(actual − expected) <= 1e-9 × max(1, abs(expected))` = 1.15e-8。

## 3. 默认值案例（defaults）

省略 `recognized_performance_fees`（唯一 optional）：

```json
{"model_id": "aum_fee_bridge", "base_revenue": 0,
 "drivers": {"opening_aum": [1000], "inflows": [200], "outflows": [100], "market_change": [-50],
             "closing_aum": [1050], "inflow_revenue_fraction": [0.25],
             "outflow_lost_fraction": [0.75], "market_change_revenue_fraction": [0.5],
             "management_fee_rate": [0.01]},
 "years": [2027]}
```

手算：桥与平均 AUM 同第 2 节 → 950 × 0.01 = 9.5；业绩报酬按卡片 L9 声明的默认 `0` → **9.5**。

**期望输出 = `[9.5]`**，长度 1。
- 同 M27：卡片声明默认 `0`，实现保留 optional 但 `defaults = {}`，运行后由 runner 记录
  `defaults_declared_check`（非 gating），把"库替披露补 0"变成可核事实。
- 默认值不是缺披露时填零的授权（`common_model_cards.md` L22）。
- 对照观察 OBS-PERF-OMITTED 证明该驱动**确实被使用**：省略它结果从 11.5 变成 9.5（不相同）。

## 4. 连续性案例（continuity）

`aum_fee_bridge` 是**存量桥模型**（`EXTENSION_OPENING_BALANCES` 中有
`base_aum_parameter_id` / `opening_aum` / `monetary_balance`），故 STOP_BRIDGE 的连续性检查**适用**，
不得标 not_applicable。

- Continuity positive（= `card_M28.md` L64-116 原文）：

```json
{"years": [2027, 2028],
 "drivers": {"opening_aum": [1000, 1050], "inflows": [200, 0], "outflows": [100, 0],
             "market_change": [-50, 0], "closing_aum": [1050, 1050],
             "inflow_revenue_fraction": [0.25, 0.25], "outflow_lost_fraction": [0.75, 0.75],
             "market_change_revenue_fraction": [0.5, 0.5], "management_fee_rate": [0.01, 0.01],
             "recognized_performance_fees": [2, 0]}}
```

  手算：FY2027 同第 2 节 = **11.5**。
  FY2028：桥 1050 + 0 − 0 + 0 = 1050 = 期末（成立），且 期初(2028)=1050 = 期末(2027)（成立）；
  平均 AUM = 1050 + 0 − 0 + 0 = 1050；管理费 1050 × 0.01 = 10.5；+0 = **10.5**。
  期望 = `[11.5, 10.5]`（与卡片 L117-121「手算期望为10.5」一致）。此例**先**运行通过。
- Continuity 断裂 patch（= `card_M28.md` L122-132 原文）：
  `opening_aum=[1000, 1051]`、`closing_aum=[1050, 1051]`。
  两年**各自**平衡（1000+200−100−50=1050；1051+0−0+0=1051），但 期初(2028)=1051 ≠ 期末(2027)=1050
  → 预期 `ModelRegistryError`（连续性）。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `opening_aum`。每个负例用**新的 deepcopy 独立输入**，互不共享可变对象；
全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 | 说明 |
|---|---|---|---|
| NEG-CARD | `closing_aum = [1051]`（卡片 L56 原文负例） | `ModelRegistryError` | 桥 1000+200−100−50 = 1050 ≠ 1051 |
| N01a | `opening_aum[0] = True` | `ModelRegistryError` | bool 不是数值 |
| N01b | `opening_aum[0] = float('nan')` | `ModelRegistryError` | 非有限 |
| N01c | `opening_aum[0] = float('inf')` | `ModelRegistryError` | 非有限 |
| N01d | `opening_aum[0] = float('-inf')` | `ModelRegistryError` | 非有限 |
| N02 | `opening_aum = []` | `ModelRegistryError` | 路径长度 ≠ 1 |
| N03 | 删除 `opening_aum` | `ModelRegistryError` | 缺必填 |
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
| OBS-PERF-OMITTED | 重放 defaults 案例（省略 `recognized_performance_fees`） | 与正例**不相同** | 证明业绩报酬项真的被使用；省略它不是免费的 |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L54 给出算式与手算 11.5，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["aum_fee_bridge"].formula`，与第 1 节公式逐项比对；若不一致，**记录差异**而不是
修改期望值。特别核对 `market_change` 前的符号是 `+`（带符号量）而不是 `−`，
因为卡片 L8 明说"带符号市场变化不等净流入"。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | AUM 桥 `期初+流入−流出+市场变化 ≠ 期末` | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 跨年 `期初(t) ≠ 期末(t−1)` | `ModelRegistryError` | 是（CONT-BREAK） |
| R3 | 时间加权平均 AUM 为负 | `ModelRegistryError` | 否（本卡未设例；见第 9 节） |
| R4 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R5 | 缺必填 driver / 未知 driver | `ModelRegistryError` | 是（N03、N04） |
| R6 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R7 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R8 | `market_change` 被错误压成非负（负市况合法却被拒） | **不得拒绝**（方向相反的失败） | 间接：正例本身就用 `market_change = −50` 且必须通过，故正例即覆盖此面 |
| R9 | 四个比例类 driver 越出 [0,1] | `ModelRegistryError` | 否（本卡未设例；见第 9 节） |
| R10 | 按年末 AUM 全年收费；市场变化时点与报酬结晶无证据 | **业务拒绝**：需 `special_review` | 否（不是运行时契约） |
| R11 | 存量无法锚定基期（无 `base_aum_parameter_id`） | **业务拒绝**：STOP_BRIDGE | 否（披露侧） |

## 9. 未覆盖面（诚实声明，供 reviewer 攻击）

- **R3（时间加权平均 AUM 为负）与 R9（比例越界）未被本卡任何负例打到**：NEG-CARD 的拒绝来自
  AUM 桥（R1）。要覆盖 R3，需要一个 `outflows` 极大而 `opening_aum` 极小的例；要覆盖 R9，
  需要一个 `management_fee_rate=[1.5]` 之类的例。本卡**未运行**这两例，留给 reviewer 作为
  未用于编写修复的保留案例。
- 本卡不重写公式：无独立反例与经审定规格时保留已修实现（`card_M28.md` L162）。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M28/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，
  且需"一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅"；本 attempt 不产出 D 的签署件。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计；该设计不存在；本卡不作准确性主张。

## 11. 停止条件自检（`card_M28.md` L145-150）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥（本卡适用）：连续性不成立 → `STOP_BRIDGE`。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。
