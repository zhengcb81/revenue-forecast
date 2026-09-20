# M14 · retail_franchise — 冻结 oracle（运行前写定）

Card: M14（`execution_v2/card_M14.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M14/a20260919-01`。
本文在**任何产品代码运行之前**写定；正文写入后不为贴合结果而修改（修订只允许在文件末尾**追加**一节
「修订 r2」，且追加前正文的 sha256 必须在**真实行边界**可复现，见文末标记行）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算（十进制）**，并由本 attempt 内独立脚本
  `scripts/oracle_M14.py` 用 Python 标准库（`decimal`/`json`/`hashlib`）复算。
  该脚本**不 import** 产品任何模块；自检证据：`evidence/M14/oracle_selfcheck.json`
  （含 `product_import_present=false` 与 import 行清单）。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M14.md` L8「单位/口径：平均直营店×U/店年；加盟系统销售×确认费率；供应收入另列并抵销内部交易」
  与 L39「手算：10×5+200×0.04+7=50+8+7=65」。实现入口 `scripts/model_registry.py:308`
  （注册 `scripts/model_registry.py:234`）仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 平均直营店数 × U/店年 + 加盟系统销售 × 确认费率 + 供应收入` | `card_M14.md` L8、L39 |
| 必填 driver | `average_owned_stores`、`revenue_per_owned_store` | `card_M14.md` L9 |
| 可选 driver / 默认 | `franchise_system_sales` 默认 0；`recognized_fee_rate` 默认 0；`supply_revenue` 默认 0 | `card_M14.md` L9 |
| 单位 | 直营店 = 店数（平均口径）；单店收入 = U/店年；加盟系统销售 = U（系统销售额，非并表收入）；确认费率 = 比例；供应收入 = U | `card_M14.md` L8 |
| 量纲 | 店 × (U/店) = U；U × 比例 = U；三项相加仍为 U | 量纲自检 |
| 允许范围 | 店数、单店收入、加盟系统销售、供应收入非负；确认费率为比例 | 通用契约 + `evidence/M14/oq_enumeration.json` |
| 平均口径 | 直营店数必须是**期间平均**店数，不得用期末店数代平均 | `card_M14.md` L43 披露采集 + L45 业务负例 |
| 总净额 | 加盟系统销售**不能全部并表**，只有确认费率那一部分进收入；供应收入需抵销内部交易 | `card_M14.md` L8、L45 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；输出每个元素为有限 float | 通用契约 + `common_model_cards.md` L20 |

## 2. 合成正例（positive）

输入（=`card_M14.md` L12–37 原文）：

```json
{"model_id": "retail_franchise", "base_revenue": 0,
 "drivers": {"average_owned_stores": [10], "revenue_per_owned_store": [5],
             "franchise_system_sales": [200], "recognized_fee_rate": [0.04],
             "supply_revenue": [7]},
 "years": [2027]}
```

手算（逐步，未取整）：

10 × 5 = **50**；200 × 0.04 = **8**；50 + 8 = **58**；58 + 7 = **65**。

**期望输出 = `[65]`**（与卡片 L39 原文一致）。
- 保真期望：容器 `list`、长度 1、元素类型 `float`、全部有限、年度 `[2027]`
  （冻结在 `oracle.json` 的 `expected_output_shape.positive`）。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 6.5e-8。

## 3. 默认值案例（defaults，非 gating）

省略三个 optional driver：

```json
{"model_id": "retail_franchise", "base_revenue": 0,
 "drivers": {"average_owned_stores": [10], "revenue_per_owned_store": [5]},
 "years": [2027]}
```

手算：10 × 5 + 0 × 0 + 0 = 50 + 0 + 0 = **50**。
**期望输出 = `[50]`**，长度 1。
- 该案例证明可选 driver 的零默认被应用；但"省略 ≠ 披露为零"（`common_model_cards.md` L22），
  风险登记在 `evidence/M14/oq_rulings.json` 的 OQ-02，不改产品。

## 4. 连续性案例（continuity）

`retail_franchise` 是**逐年独立的流量模型**（无期初/期末对账项），"存量断裂"不适用
（STOP_BRIDGE → **not_applicable_with_reason**）。适用的是**跨年财年连续性**：

- Continuity positive：`years=[2027, 2028]`，
  `average_owned_stores=[10, 12]`，`revenue_per_owned_store=[5, 5.5]`，
  `franchise_system_sales=[200, 240]`，`recognized_fee_rate=[0.04, 0.045]`，`supply_revenue=[7, 8]`。
  手算：FY2027 = 10×5 + 200×0.04 + 7 = 50 + 8 + 7 = **65**；
  FY2028 = 12×5.5 + 240×0.045 + 8 = 66 + 10.8 + 8 = **84.8**。期望 = `[65, 84.8]`。
- Continuity 断裂 patch：`years=[2027, 2029]` → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `average_owned_stores`。每个负例使用**新的 deepcopy 独立输入**，不经 JSON 解析器。
card-specific 负例用 `set_driver_element`，命中**值域守卫**而非数组长度守卫。

| 例 | 变换（在指定 base 输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `recognized_fee_rate[0] = 1.1`（base=positive） | `ModelRegistryError`（比例域 [0,1]） |
| N01a | `average_owned_stores[0] = True` | `ModelRegistryError` |
| N01b | `average_owned_stores[0] = float('nan')` | `ModelRegistryError` |
| N01c | `average_owned_stores[0] = float('inf')` | `ModelRegistryError` |
| N01d | `average_owned_stores[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `average_owned_stores = []` | `ModelRegistryError`（长度 ≠ `len(years)`） |
| N03 | 删除 `average_owned_stores` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]` | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（base=continuity_positive） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；导入/文件错误不得计为通过。

## 6. 观察项（非 pass/fail 设计观察，不参与退出码）

| ID | 变换 | 冻结预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（base=positive） | 与正例**相同** = `[65]` | `_rowwise` 丢弃 `base_revenue`；设计观察 |
| OBS-BOUND-INCLUSIVE | `recognized_fee_rate[0] = 1.0`（base=positive） | `[257]`（手算 50 + 200×1.0 + 7） | 证明比例域上端**含端点**：1.0 接受、1.1 拒绝 |
| OBS-SUPPLY-BOUND | `supply_revenue[0] = -1`（base=positive） | `ModelRegistryError`（driver 下界 0.0） | `supply_revenue` **不是**带符号 driver，负供应收入被 driver 守卫直接拒绝，而不是被"收入非负"终检拒绝 |

## 7. 卡片文字 vs 实现公式串

卡片 L8/L39 给出算式与手算 65，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["retail_franchise"].formula` 并逐项比对；不一致时**记录差异**，不改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 运行时可否执行 |
|---|---|---|---|
| R1 | `recognized_fee_rate` 越出比例域 | `ModelRegistryError` | 是（NEG-CARD + OBS-BOUND-INCLUSIVE 对照） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空 / 非连续 / 非整数财年 | `ModelRegistryError` | 是（N05a/N05b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a–d） |
| R7 | 用**期末**直营店数代替期间平均店数 | **业务拒绝**：需 `special_review` | 否（不是运行时契约） |
| R8 | 把加盟系统销售**全额并表** | **业务拒绝**：只有确认费率部分进收入 | 否（披露适配阶段） |
| R9 | 一次加盟费递延与供应收入重复确认 | **业务拒绝**：需会计审定 | 否（披露适配阶段） |
| R10 | 负供应收入 | `ModelRegistryError`（现行 driver 下界） | 是（OBS-SUPPLY-BOUND；记录事实） |

## 9. 三种资格（本卡只填 formula）

- `formula`：由 A–C 结果决定（`evidence/M14/qualification.json`）；实现者**不自签**，状态 `review_pending`。
- `disclosure_adaptation`：保持 **unmapped**（本 attempt 纯合成，无真实公司披露映射）。
- `accuracy`：保持 **unproven**（无 I-12 冻结设计；不从公式通过外推准确性）。

## 10. 停止条件自检（`card_M14.md` L56–61）

- positive 不等 / 保真不符 / 应拒绝负例未拒绝 → `STOP_FORMULA`（先记录反例，不重写实现）。
- 披露缺出处、单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`（D 未开工）。
- 存量桥：**not_applicable_with_reason**（第 4 节）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

## 11. runner 退出码口径（本卡适用）

`scripts/run_card.py`：`0=pass`、`1=harness error`、`2=no-verdict（期望缺失或保真不符）`、
`3=negative-case 未按期望拒绝`；优先级 `1 > 2 > 3`，触发条件逐条写入
`run_result.json` 的 `exit_code_semantics.triggered`。`observations` 与 `defaults` 不参与退出码。
<!-- R2-APPEND-BOUNDARY: everything above this line is the frozen oracle body (v1) -->

## 修订 r2（追加处置，非重写）

本节由修订 r2 **追加**，是 `oracle.md` 中**唯一**的一节「修订 r2」。
上方正文（v1 冻结版）逐字未改：正例/连续性/默认值预期、容差、负例清单、拒绝条件**一律未改**；
产品仓库一行未动。本节追加前 `oracle.md` 的 sha256 记录在 `before/oracle_md_v1.json`，
并可由 `scripts/verify_r2_boundary.py` 在**真实行边界**（本标记行处）重新复现：
上方字节的 sha256 必须仍等于该记录值。本文件只有一个基准，不存在第二个互斥的"追加前 hash"。

### r2 记录的事项

- **R2-01（口径登记，非重写）**：本卡 runner 的退出码口径为
  `0=pass / 1=harness error / 2=no-verdict(期望缺失或保真不符) / 3=negative-case 未按期望拒绝`，
  优先级 `1 > 2 > 3`；`run_card.py` 的模块 docstring 与 `evidence/M14/qualification.json`
  记录同一口径。此登记不改变任何期望值。
- **R2-02（变异自检结果，先红后绿）**：对**副本**注入变异后 runner 确实变红，随后恢复；
  冻结的 `input.json` / `cases.json` / `oracle.json` 在自检前后 hash 不变，且仍等于冻结时的 hash。

  | 场景 | 实测 rc | 期望 rc | 结果 |
  |---|---|---|---|
| C-control | 0 | 0 | ok |
| A-corrupt-value | 2 | 2 | ok |
| F-corrupt-shape | 2 | 2 | ok |
| D-missing-expectation | 2 | 2 | ok |
| B-corrupt-negative-case | 3 | 3 | ok |
| E-harness-error | 1 | 1 | ok |

  证据：`recovery/selfcheck_result.json`、`recovery/selfcheck/**`（标准库脚本
  `scripts/selfcheck_mutation.py`，副本位于 `recovery/selfcheck/evidence/M14/`）。
- **R2-03（保真口径）**：正例不只看数值，还比对输出**结构/长度/元素类型/有限性/年度**；
  变异场景 F 把冻结形状的 `length` 改成 99，runner 因保真不符返回 2 而不是 0。
- **R2-04（打印与证据一致）**：`evidence/M14/stdout.txt` 是进程 stdout 的原始抓取，
  `scripts/verify_card.py` 断言其逐行等于 `run_result.json` 的 `printed_lines` 并复现
  `printed_sha256`，因此"打印值"不可能与证据文件不一致。
- R2-05：冻结的观察项全部按规格构造成功，没有需要在事后补探针的观察项。

事后探针 `recovery/probes/signed_driver_probe.json`：对 driver `franchise_system_sales` 取值 `-100.0`，实测 raised=`ModelRegistryError` actual=`None`，判定为 the driver guard refused the negative value outright。

### 未改动的内容（防止误读为"为过审而改"）

- 正例/连续性/默认值预期、容差、11 个负例及其期望错误、拒绝条件、停止条件**一律未改**；
  唯一失效的观察项如实记录，**没有**为了让证据好看而重打包 `input.json`/`cases.json`/`oracle.json`。
- 冻结的三个证据文件在冻结时的 sha256：
  `input.json`=8cba525c5fabff447ce7f0d81027028281c60c2abea9464d653e6f8f54f3c551、`cases.json`=ba998e44e0b7e8ca2f7789f748a5c59149e7c93d02e97e0cf6e81af308dcb28b、`oracle.json`=bb3807c461b1d21857885b92b075554080f2903ee896e9541e8899aa80d1dac5
- 产品仓零改动；`changes.diff` 为 NO PRODUCT CHANGE 声明。
- `formula` 状态仍为 `review_pending`（实现者不自签），`disclosure_adaptation` 仍为 `unmapped`，
  `accuracy` 仍为 `unproven`。
