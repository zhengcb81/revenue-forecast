# M27 · renewable_generation — 冻结 oracle（运行前写定）

Card: M27（`execution_v2/card_M27.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M27/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 第 1、2、3、4 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M25_M28.py`（sha256 `d443b5d5bcf5f49f8f442df71b99f774a74422d393f038b9dca14bbe9a6a6e5e`）
  用 Python 标准库（`decimal`/`json`/`hashlib`）复算。该脚本**不 import** 产品任何模块
  （`model_registry` / `model_extensions` 均不出现），自检见 `evidence/M27/oracle_selfcheck.json`
  （`product_import_present = false`）。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M27.md` L8「平均已投产MW×期间小时×弃电前容量因子×(1−弃电率)=MWh；电价U/MWh」
  与 L48 原文手算「2×8760×0.5=8760MWh；电价0.5×40+0.5×20=30；8760×30+1200=264000」。
  实现入口 `scripts/model_registry.py:308`、注册 `scripts/model_extensions.py:196` 仅在冻结之后
  用于定位调用点；本卡公式串是从卡片与手算独立写出的，运行后再与实现的公式串逐项比对。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式 | `收入 = 平均已投产MW × 期间小时 × 弃电前容量因子 × (1−弃电率) × (合约比例×合约电价 + (1−合约比例)×市场电价) + 其他收入` | `card_M27.md` L8、L48 |
| 必填 driver | `average_commissioned_mw`、`period_hours`、`pre_curtailment_capacity_factor`、`curtailment_rate`、`contracted_share`、`contract_price_per_mwh`、`merchant_price_per_mwh` | `card_M27.md` L9 |
| 可选 driver / 默认 | `other_revenue`，卡片 L9 声明默认 `0` | `card_M27.md` L9 |
| 单位 | MW；小时；`pre_curtailment_capacity_factor`/`curtailment_rate`/`contracted_share` 无量纲比例；电价 U/MWh；`other_revenue` = U 金额；中间量 MWh；输出 = U | `card_M27.md` L8 |
| 量纲 | MW × h × 比例 × 比例 = MWh；MWh × (U/MWh) = U | 量纲自检 |
| 语义域 | `average_commissioned_mw` 为 `quantity`（下界 0）；`period_hours` 为 `activity`（下界 0，但**0 小时不可接受**，卡片 L50 的负例正是 `period_hours=[0]`）；三个比例为 `ratio` → [0,1]；**两个电价的语义域必须显式放宽**（含负电价可能），不能落进 [0,1]；`other_revenue` 为 `revenue` 维（可负） | `card_M27.md` L8、L50、L54 + 通用契约 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；期间小时必须为正；总收入不得为负 | 通用契约 |
| 业务口径 | 平均MW不再乘时间；净容量因子不能重复扣弃电；负电价可输入但总收入负值不支持 | `card_M27.md` L54 |

## 2. 合成正例（positive）

输入（=`card_M27.md` L12-46 原文）：

```json
{"model_id": "renewable_generation", "base_revenue": 0,
 "drivers": {"average_commissioned_mw": [2], "period_hours": [8760],
             "pre_curtailment_capacity_factor": [0.5], "curtailment_rate": [0],
             "contracted_share": [0.5], "contract_price_per_mwh": [40],
             "merchant_price_per_mwh": [20], "other_revenue": [1200]},
 "years": [2027]}
```

手算（逐步，未取整）：

1. 上网电量（弃电前 → 弃电后）：2 × 8760 × 0.5 = **8760** MWh；(1 − 0) = 1，故 8760 × 1 = **8760** MWh。
2. 综合电价：0.5 × 40 + (1 − 0.5) × 20 = 20 + 10 = **30** U/MWh。
3. 售电收入：8760 × 30 = **262800** U。
4. 加其他收入：262800 + 1200 = **264000** U。

**期望输出 = `[264000]`**（与卡片 L48 原文一致）。
- 输出长度 = 1 = `len(years)`；年份应与 `years` 相同（`years` 长度、输出长度、输出字段集三项都断言）。
- 容差：`abs(actual − expected) <= 1e-9 × max(1, abs(expected))` = 2.64e-4。

## 3. 默认值案例（defaults）

省略 `other_revenue`（唯一 optional），只给七个必填 driver：

```json
{"model_id": "renewable_generation", "base_revenue": 0,
 "drivers": {"average_commissioned_mw": [2], "period_hours": [8760],
             "pre_curtailment_capacity_factor": [0.5], "curtailment_rate": [0],
             "contracted_share": [0.5], "contract_price_per_mwh": [40],
             "merchant_price_per_mwh": [20]},
 "years": [2027]}
```

手算：售电收入仍为 8760 × 30 = 262800；`other_revenue` 按卡片 L9 声明的默认 `0` → 262800 + 0 = **262800**。

**期望输出 = `[262800]`**，长度 1。
- 本卡是四卡中**唯一**有真实 optional driver 的卡，因此这个案例同时暴露一个必须登记的差异：
  卡片 L9 声明 `other_revenue` 默认 `0`，而实现把该驱动保留为 optional 但 `defaults = {}`。
  运行后由 runner 记录 `defaults_declared_check`（非 gating），把"库替披露补 0"这件事变成可核事实。
- 默认值不是缺披露时填零的授权（`common_model_cards.md` L22）。

## 4. 连续性案例（continuity）

`renewable_generation` **不是**存量桥模型：它没有 `EXTENSION_OPENING_BALANCES` 条目，没有期初/期末
对账项，`_renewable` 是逐年流量计算。因此"存量断裂"**不适用**
（STOP_BRIDGE → `not_applicable_with_reason`，理由同 M05 第 4 节）。

卡片 L58-120 **没有**给出两年连续性用例（`card_M27.md` 无该节），故本卡采用与 M05 相同的
**跨年财年连续性**检查：

- Continuity positive：`years=[2027, 2028]`，
  FY2027 = 第 2 节 = **264000**；
  FY2028：MW=5、小时=8760、弃电前容量因子=0.45、弃电率=0.1、合约比例=0.4、
  合约电价=42、市场电价=25、其他收入=0。
  手算：上网电量 5 × 8760 × 0.45 = 19710 MWh；×(1−0.1) = 17739 MWh；
  综合电价 0.4 × 42 + 0.6 × 25 = 16.8 + 15 = 31.8 U/MWh；
  17739 × 31.8 = **564100.2** U；+0 = **564100.2**。
  期望 = `[264000, 564100.2]`。此例**先**运行通过。
- Continuity 断裂 patch：`years=[2027, 2029]`（缺 2028，财年不连续）→ 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `average_commissioned_mw`。每个负例用**新的 deepcopy 独立输入**，互不共享可变对象；
全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 | 说明 |
|---|---|---|---|
| NEG-CARD | `period_hours = [0]`（卡片 L50 原文负例） | `ModelRegistryError` | 期间小时必须为正；0 小时不产生电量 |
| N01a | `average_commissioned_mw[0] = True` | `ModelRegistryError` | bool 不是数值 |
| N01b | `average_commissioned_mw[0] = float('nan')` | `ModelRegistryError` | 非有限 |
| N01c | `average_commissioned_mw[0] = float('inf')` | `ModelRegistryError` | 非有限 |
| N01d | `average_commissioned_mw[0] = float('-inf')` | `ModelRegistryError` | 非有限 |
| N02 | `average_commissioned_mw = []` | `ModelRegistryError` | 路径长度 ≠ 1 |
| N03 | 删除 `average_commissioned_mw` | `ModelRegistryError` | 缺必填 |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError` | 未知字段 |
| N05a | `years = []` | `ModelRegistryError` | 年度域 |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` | True 不是财年 |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive，先验 positive） | `ModelRegistryError` | 财年不连续 |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；
`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（drivers/years 不变） | 输出与正例**相同** | `_rowwise` 丢弃 `base_revenue`；设计观察，不作为通过条件 |
| OBS-NEG-PRICE | `merchant_price_per_mwh = -20` | **不设预期、不设判定** | 卡片 L54 说负电价**可以输入**。探测记录实现是否真的放宽了两个电价的上界；只登记事实，不把它当通过条件，也不据此声称经济结论 |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L48 给出算式与手算 264000，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["renewable_generation"].formula`，与第 1 节公式逐项比对；若不一致，**记录差异**
而不是修改期望值。特别核对 `(1−curtailment_rate)` 只出现一次（不得重复扣弃电），
以及 `other_revenue` 是加在最后（不得参与混合电价）。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | `period_hours <= 0` | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver / 未知 driver | `ModelRegistryError` | 是（N03、N04） |
| R4 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R5 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R6 | 三个比例类 driver 越出 [0,1] | `ModelRegistryError` | 否（本卡未设例；见第 9 节） |
| R7 | 任一电价被错误压进 [0,1]（负电价合法却被拒） | **不得拒绝**（方向相反的失败） | 是（OBS-NEG-PRICE 覆盖此面，但**不设判定**；若被拒则登记为契约缺口线索） |
| R8 | 总收入为负 | `ModelRegistryError`（通用非负域） | 间接 |
| R9 | 净容量因子重复扣弃电；平均MW再乘时间 | **业务拒绝**：需 `special_review` | 否（不是运行时契约） |

## 9. 未覆盖面（诚实声明，供 reviewer 攻击）

- **R6（三个比例越界）未被本卡任何负例打到**：NEG-CARD 的拒绝来自 `period_hours`（R1）。
  要覆盖 R6，需要一个 `curtailment_rate=[1.5]` 之类的例；本卡**未运行**该例，留给 reviewer 作为
  未用于编写修复的保留案例。
- OBS-NEG-PRICE **刻意不设判定**：它是方向相反的风险（合法的负电价被错误拒绝），
  把它设成"必须不抛"会与 R8（收入非负）纠缠，故只登记事实。
- 本卡不重写公式：无独立反例与经审定规格时保留已修实现（`card_M27.md` L82）。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M27/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，
  且需"一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅"；本 attempt 不产出 D 的签署件。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计；该设计不存在；本卡不作准确性主张。

## 11. 停止条件自检（`card_M27.md` L65-70）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 `special_review` 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 4 节）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。
