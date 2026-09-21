# I-10-B 兼容性影响清单（卡文第 3 点硬要求）

- 卡：`execution_v2/card_I-10-B.md`（来源 `OWNER_DECISIONS.md` §13 **T1-22**）
- attempt：`a20260919-01`
- 生成时间：2026-09-20
- 状态：**planned（未自我升格）**。I-10-B 未落地生产：`scripts/model_registry.py` 仍为修复前前像。
- 证据脚本：`scripts/compute_compat.py`、`scripts/scan_frozen_impact.py`、`scripts/frozen_regression_rerun.py`

---

## 0. 生产锚点复核（卡文第 6 点，每次复算）

| 文件 | 字节 | sha256 | 与绑定值 |
|---|---|---|---|
| `scripts/model_registry.py` | 26446 | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` | **一致** |
| `scripts/model_extensions.py` | 14475 | `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911` | **一致** |

**无漂移。** 生产文件即**修复前（BEFORE）**状态；本卡修复**尚未**写入生产。

---

## 1. 值域变更全清单（BEFORE → AFTER 差分）

**判据说明（重要）**：本节判定的是「`(lo, hi)` 相较修复前**是否发生变化**」，
**不是**「最终下界是否为 `-inf`」。后者会把**修复前就已存在的** `-inf` cell
（如 `other_revenue` 14 个、`bank_revenue.asset_yield`、`bank_revenue.funding_cost`、
`aum_fee_bridge.market_change`、`renewable_generation.*` 两个价格 driver 等）
误并进变更集，既**夸大**波及面，又**掩盖**真实变更。

| 指标 | BEFORE | AFTER |
|---|---|---|
| 模型数 | 31 | 31 |
| `(model, driver)` 边界单元数 | **165** | **165** |
| 单元的键集合是否逐一相同 | — | **是** |

### 1.1 实际发生变化的单元：**恰好 5 个**

| # | 模型 | driver | 声明 | 有显式默认 | BEFORE | AFTER | 变化方向 |
|---|---|---|---|---|---|---|---|
| 1 | `cohort_subscription` | `usage_revenue` | optional | 否 | `[0.0, inf)` | `[-inf, inf)` | 下界放宽 |
| 2 | `retail_franchise` | `franchise_system_sales` | optional | 否 | `[0.0, inf)` | `[-inf, inf)` | 下界放宽 |
| 3 | `retail_franchise` | `supply_revenue` | optional | 否 | `[0.0, inf)` | `[-inf, inf)` | 下界放宽 |
| 4 | `subscription` | `usage_revenue` | optional | 否 | `[0.0, inf)` | `[-inf, inf)` | 下界放宽 |
| 5 | `subscription_arr_bridge` | `usage_revenue` | optional | 否 | `[0.0, inf)` | `[-inf, inf)` | 下界放宽 |

**5/5 均为：下界放宽、上界不变、且该 driver 在对应模型上都是「optional 且无显式默认」。**
无上界收紧，无新增拒绝，无任何单元被移出 165 集合。

### 1.2 未变化的 driver：**126 个**（逐个列出见 §4）

`changed_cells_exactly_match = True`；`unexpected_neg_inf = []`；`missing_neg_inf = []`。

---

## 2. 修复前就已 `-inf` 的单元（**不属本次变更**，列出以绝歧义）

共 **37 个** cell 在 **BEFORE 就已** `[-inf, inf)`：

| driver | 出现模型数 |
|---|---|
| `other_revenue` | 14 |
| `usage_revenue` | 3（**其中 3 个为本次变更**，见 §1.1） |
| `milestone_revenue` | 2 |
| `service_revenue` | 2 |
| `performance_fee_revenue` · `market_change` · `recognized_performance_fees` · `asset_yield` · `fee_revenue` · `funding_cost` · `royalty_revenue` · `backlog_remeasurements` · `contract_changes` · `contract_price_per_mwh` · `merchant_price_per_mwh` · `reserve_revisions` · `ancillary_revenue` · `fixed_revenue` | 各 1 |

### 2.1 名字硬编码任意性的实测证据（缺陷②之「名字与语义不符」）

`recognized_performance_fees`、`reserve_revisions`、`backlog_remeasurements`
**均不在** `_SIGNED_DRIVERS`，却**早已**经 `driver_bounds` 元数据到达 `(-inf, inf)` ——
证明「同一语义角色、两种名字待遇」。这正是缺陷②要改的东西。

---

## 3. 受影响的历史冻结用例——**核心发现**

### 3.1 方法

冻结件只可能通过两条路径被边界改动影响：
- **(a) 喂入一个「新允许/新拒绝」的值** —— 若有，`PASS_rejected` 会翻成失败。
- **(b) 省略某个 optional driver，依赖旧的静默补 0** —— 若有，`defaults` 相位会翻成失败。

对全 `M01–M31` 证据树做全量 JSON 扫描（`scan_frozen_impact.py`，扫描 **1579** 个 JSON），
分类为 `CASE_TARGET` / `VALUE_BEARING` / `REFERENCE_ONLY`。

### 3.2 路径 (a)：值域放宽 —— **无任何**用例喂入负值

| 分类 | 数量 | 说明 |
|---|---|---|
| `CASE_TARGET` | 17 | 三个 driver 出现在某 `case.driver` 位 |
| `VALUE_BEARING`（含**负值**） | **1** | 见下 |
| `VALUE_BEARING`（仅正值） | 81 | 值在 `[0, inf)` 内，**不受放宽影响** |
| `REFERENCE_ONLY` | 47 | 仅枚举清单/哈希表/散文提及，无行为耦合 |

**唯一** 的负值命中：

> `M14/a20260919-01/recovery/probes/signed_driver_probe.json`
> —— 这是**探针，不是冻结用例**。文件自身第 4 行写明：
> `"purpose": "post-hoc design probe (NOT a frozen case, NOT the oracle)"`。

17 个 `CASE_TARGET` 落点为 `cases.json` / `oq_rulings*.json`；逐个核对后，
**其 `value` 均为正数或「类型/长度」类负例**（`__bool__` / `nan` / `inf` / `-inf` / 空数组 / 未知 driver），
**无一**依赖「负的实数值应被 `[0, inf)` 拒绝」。

**结论 (a)：值域放宽不改变任何冻结用例的判定。**

### 3.3 M14 对值域旧行为的**书面记录**（追加式勘误对象）

两处把「负值被 bound 拒绝」记为**契约边界**，均自带「不门禁」声明：

| 载体 | 原文要点 |
|---|---|
| `evidence/M14/cases.json` → `extra_observations[OBS-SUPPLY-BOUND]` | `supply_revenue = -1`；`why`: 「supply_revenue is **NOT** a signed driver in this registry, so a negative supply sale is **refused by the driver bound (lower bound 0.0)** … **records the contract boundary, does not gate**」 |
| `evidence/M14/oq_rulings.json` → `open_questions_mirroring_handoff["OQ-03"]` | 「this model has **NO signed/unbounded driver**, so a negative supply revenue or franchise system sale is refused by the driver bound (0.0) rather than by an accounting judgement. Recorded by OBS-SUPPLY-BOUND and `recovery/probes/signed_driver_probe.json`; **whether internal eliminations need a signed convention is a D/E decision.**」 |

**关键**：`OQ-03` **本身就是一个未决开放问题**，且明写「属 D/E 决策」。
I-10-B 缺陷②即是对该 OQ 的裁定。
**`OBS-*` 是 observation（不门禁）；`OQ-03` 是 open question（未裁）。**
⇒ 两者**都不是** pass condition，故 **§3.2 的结论 (a) 成立**：
**没有任何冻结判定被值域放宽推翻。**

### 3.4 路径 (b)：省略 optional driver —— **四张卡的 `defaults` 相位全部翻转**

**这是本卡最严重的兼容性发现。** 实跑对照（`frozen_regression_rerun.py`）
对 M05 / M14 / M20 / M24 的 `positive` / `continuity_positive` / `defaults` 三相位，
分别用 **BEFORE** 与 **AFTER** 注册表调用真实入口
`calculate_registered_model(model_id, base_revenue, drivers, years)`：

| 卡 | 模型 | 相位 | BEFORE | AFTER | 翻转 |
|---|---|---|---|---|---|
| M05 | `subscription` | positive | `ok [620.0]` | `ok [620.0]` | — |
| M05 | `subscription` | continuity_positive | `ok [550.0, 880.0]` | `ok [550.0, 880.0]` | — |
| **M05** | `subscription` | **defaults** | `ok [600.0]` | **`ModelRegistryError`** | **是** |
| M14 | `retail_franchise` | positive | `ok [65.0]` | `ok [65.0]` | — |
| M14 | `retail_franchise` | continuity_positive | `ok [65.0, 84.8]` | `ok [65.0, 84.8]` | — |
| **M14** | `retail_franchise` | **defaults** | `ok [50.0]` | **`ModelRegistryError`** | **是** |
| M20 | `cohort_subscription` | positive | `ok [195.0]` | `ok [195.0]` | — |
| M20 | `cohort_subscription` | continuity_positive | `ok [195.0, 240.0]` | `ok [195.0, 240.0]` | — |
| **M20** | `cohort_subscription` | **defaults** | `ok [220.0]` | **`ModelRegistryError`** | **是** |
| M24 | `subscription_arr_bridge` | positive | `ok [215.0]` | `ok [215.0]` | — |
| M24 | `subscription_arr_bridge` | continuity_positive | `ok [215.0, 250.0]` | `ok [215.0, 250.0]` | — |
| **M24** | `subscription_arr_bridge` | **defaults** | `ok [210.0]` | **`ModelRegistryError`** | **是** |

抛出的消息（逐卡）：

| 卡 | 消息 |
|---|---|
| M05 | `missing driver for subscription: usage_revenue has no explicit default` |
| M14 | `missing driver for retail_franchise: franchise_system_sales has no explicit default` |
| M20 | `missing driver for cohort_subscription: usage_revenue has no explicit default` |
| M24 | `missing driver for subscription_arr_bridge: usage_revenue has no explicit default` |

**根因**：四张卡的 `defaults` 输入块**都省略了至少一个「optional 且无显式默认」的 driver**：

| 卡 | 模型 | `defaults` 块省略的 optional driver | 其中有显式默认的吗 |
|---|---|---|---|
| M05 | `subscription` | `timing_factor`, `usage_revenue` | `timing_factor` 有(1.0)；`usage_revenue` **无** |
| M14 | `retail_franchise` | `franchise_system_sales`, `recognized_fee_rate`, `supply_revenue` | 三者**全无** |
| M20 | `cohort_subscription` | `churned_customer_lost_fraction`, `new_customer_revenue_fraction`, `timing_factor`, `usage_revenue` | 前三者有；`usage_revenue` **无** |
| M24 | `subscription_arr_bridge` | `usage_revenue` | **无** |

**这些 `defaults` 相位的冻结期望成立，恰恰依赖缺陷①的「静默补 0」。**
最直白的书面自证是 M24 `evidence/M24/oracle.json` → `hand_notes.defaults`：

> 「**usage_revenue omitted -> 0**; 200 - 15 + 15 + 10 + 0 = 210」

同理 M05 `oracle.json` 的 `defaults.hand_work = "200 x 3 x 1 + 0"`（末项 0 即省略的 `usage_revenue`）。

**这不是缺陷，而是修复的预期后果**：缺陷①的定义就是「把『不存在』与『没找到』编码成同一输入」。
四张卡的 `defaults` 相位正是踩在这个歧义上。

### 3.5 §3.4 与 §3.2 的关系——为什么没有矛盾

- **值域放宽（缺陷②）**：**零**冻结判定受影响（§3.2）。
- **省缺即抛（缺陷①）**：**四张卡的一个相位**受影响（§3.4）。

两者是同卡两项修复的**独立**后果，必须分开陈述。卡文第 3 点说的
「改②会改变部分 driver 的值域上下界」，其关注点是②；但真正产生冻结用例
影响的其实是**①**，故本节一并登记，**不**让①的后果藏在②的叙述后面。

---

## 4. 126 个未变化 driver 的逐个列出（卡文「25 个既有 driver 须逐个列出」）

`compute_compat.py` 输出 `drivers_unchanged`（126 项）。**其 `(lo, hi)` 在 BEFORE/AFTER 逐字节相同。**

### 4.1 变化 driver 全集（3 个）

`franchise_system_sales`、`supply_revenue`、`usage_revenue`

### 4.2 未变化 driver（126 个）

```
ancillary_revenue, asset_yield, average_customers, average_owned_stores,
backlog_remeasurements, base_revenue, churned_customer_lost_fraction,
churned_customers, closing_arr, contract_changes, contract_price_per_mwh,
ending_customers, expansion_arr, expansion_revenue_fraction, fee_revenue,
fixed_revenue, franchise_system_sales*, funding_cost, gross_retention_rate,
lost_arr_revenue_fraction, market_change, merchant_price_per_mwh,
milestone_revenue, new_arr, new_arr_revenue_fraction, new_customer_revenue_fraction,
new_customers, opening_arr, opening_customers, other_revenue,
performance_fee_revenue, recognized_fee_rate, recognized_performance_fees,
reserve_revisions, revenue_per_customer, revenue_per_owned_store,
royalty_revenue, service_revenue, timing_factor, usage_revenue*
```

\* 见 §4.1：这三个 driver **仅在其被列出的具体模型上**变化；
在其余模型上的同名 driver 单元**未变化**。逐 cell 数据见 `compatibility_cells.json`。

---

## 5. 追加式勘误登记（依 T1-12，**不回改任何冻结件**）

**T1-12 原文**：「一律采用 **① 形态**（追加新节 + 行级『第 X 行已过时，以本节为准』标注）；
**不外扩**就地编辑授权。」

**本卡不执行该登记** —— 卡文第 5 点明确「**不得**为本卡扩大 allowlist 去改 31 张 M 卡的正文或证据」。
故此处只**产出待登记清单**，交由编排层按 T1-12 形态落地：

| 待登记项 | 载体 | 追加式更正后的口径 |
|---|---|---|
| E-1 | `M05 evidence/M05/oracle.json` → `defaults` | 追加：「`defaults` 相位依赖旧静默补 0；缺陷①落地后该相位将抛 `ModelRegistryError`。已过时，以本注为准。」 |
| E-2 | `M14 evidence/M14/oracle.json` → `defaults` | 同上（`franchise_system_sales` 等三者无默认） |
| E-3 | `M20 evidence/M20/oracle.json` → `defaults` | 同上（`usage_revenue` 无默认） |
| E-4 | `M24 evidence/M24/oracle.json` → `defaults` | 同上；并标注 `hand_notes.defaults` 的「omitted -> 0」为修复前口径 |
| E-5 | `M14 evidence/M14/cases.json` → `extra_observations[OBS-SUPPLY-BOUND]` | 追加：「`supply_revenue` 自 I-10-B 起为语义角色可冲回 ⇒ `[-inf, inf)`；该 observation 描述的是修复前边界。」 |
| E-6 | `M14 evidence/M14/oq_rulings.json` → `open_questions_mirroring_handoff["OQ-03"]` | 追加：「OQ-03 已由 I-10-B 缺陷②裁定：改为语义角色规则；『NO signed/unbounded driver』不再成立。」 |
| E-7 | `M14 recovery/probes/signed_driver_probe.json` | 追加：「探针结论（负值被拒绝）为修复前行为；缺陷②后同输入应被接受。」**探针非冻结用例**，按 T1-24 口径处理 |

**均须**：旧值原样保留、追加新节、行级标注「已过时，以本节为准」；**禁止**回改为「从未如此」。

---

## 6. 退出判据自评（卡文末行）

| 判据 | 状态 | 依据 |
|---|---|---|
| 「省缺不再静默补 0」 | **已成立**（isolated） | §3.4 四卡 `defaults` 全部抛 `ModelRegistryError`；`verify_i10b.py` after 相位 7/7 rc=0 |
| 「符号按语义角色判定」 | **已成立**（isolated） | `_REVERSAL_CAPABLE_DIMENSIONS` ∩ `_REVERSAL_CAPABLE_DRIVERS` + `_is_reversal_capable()`；`_SIGNED_DRIVERS` 降为废弃别名 |
| 「兼容性影响逐项列出」 | **已成立** | §1（5 个 cell）、§3.2（零冻结判定受影响）、§3.4（四卡一个相位受影响）、§4（126 个未变） |

**本卡状态仍为 `planned`** —— 未落地生产，未获独立验收，**不自我升格**。
