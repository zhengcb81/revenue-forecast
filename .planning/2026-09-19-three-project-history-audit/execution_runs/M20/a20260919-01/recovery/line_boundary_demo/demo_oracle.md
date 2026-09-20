# M20 · cohort_subscription · 客户流量与时间暴露 — 冻结 oracle（运行前写定）

Card: M20（`execution_v2/card_M20.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M20/a20260919-01`。model_id：`cohort_subscription`。
标题、卡号、model_id 与 `decision.md` / `handoff.json` / `review.md` 保持一致。

本文件在**任何产品代码运行之前**写定；写定后不得为贴合结果而修改。本 attempt 目前是 **r1**，
`oracle.md` 内**没有、也不得出现第二个「修订 r2」节**（见 `evidence/M20/revision_r2.json`）。

## 0. 独立性声明（最重要）

- 下列全部数值预期来自**手算**，并由本 attempt 内独立脚本 `scripts/oracle_M20.py` 用 Python
  标准库（`decimal` 精度 50）复算落盘；该脚本**不 import** 产品任何模块，且在生成时对客户桥
  平衡做 `assert`（不平衡的"正例"不可能被写成期望）。
- **绝不**调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M20.md` L8「客户同一单位；新客收入比例及流失损失比例显式，年费U/客户年」、
  L9 必填/可选、L51「手算：100+40−20=120；暴露100+40×0.25−20×0.75=95；95×2+5=195」，
  以及卡片自带的两年连续性用例（L59-125）。实现入口与注册行号在使用前用隔离副本**逐行核对**。
- 冻结顺序：`oracle.md`（本文件）→ `evidence/M20/oracle.json`（脚本生成）→ 首次产品 stdout。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | 暴露客户数 × U/客户年 × 时点因子 + 用量收入；暴露 = 期初 + 新客 × 新客收入比例 − 流失 × 流失损失比例 | `card_M20.md` L8、L51 |
| 实现公式串（须核对，不得为对齐而改预期） | `revenue = (opening_customers + new_customers * new_customer_revenue_fraction - churned_customers * churned_customer_lost_fraction) * revenue_per_customer * timing_factor + usage_revenue` | 隔离副本 `model_registry.py` 注册行 |
| 必填 driver | `opening_customers`、`new_customers`、`churned_customers`、`ending_customers`、`revenue_per_customer` | `card_M20.md` L9 |
| 可选 driver / 默认 | `timing_factor` 默认 `1`、`usage_revenue` 默认 `0`、`new_customer_revenue_fraction` 默认 `0.5`、`churned_customer_lost_fraction` 默认 `0.5`（卡片 L9） | `card_M20.md` L9 |
| 单位 | 客户数 = 户（同一单位）；`revenue_per_customer` = U/客户年；`usage_revenue` = U；输出 = U/年 | `card_M20.md` L8 |
| 量纲 | 户 × (U/客户年) × 比例 = U | 量纲自检 |
| 有效域（来源：`model_registry.py:265-293`；运行时以 `registry_enumeration.json` 为准） | 五个客户 driver = quantity `[0, inf)`；`revenue_per_customer` = revenue_per_unit `[0, inf)`；`timing_factor`、`new_customer_revenue_fraction`、`churned_customer_lost_fraction` = ratio `[0, 1]`；`usage_revenue` 维为 revenue 且**不在** `_SIGNED_DRIVERS`，故为 `[0, inf)` | 枚举 + 源码 |
| 客户桥（本模型**是**存量桥） | 年内平衡：`期初 + 新客 − 流失 = 期末`；跨年连续：本期 `期初` = 上期 `期末` | 卡片 L51、L123 |
| 时点 | 不得无依据默认"年中"；不同价格/同年流失群组需专业拆分 | `card_M20.md` L57 业务负例 |
| 硬约束 | 输出长度 = `len(years)`；不允许负暴露（exposure < 0 拒绝） | 通用契约 |

## 2. 合成正例（positive）

输入（=`card_M20.md` L12-49 原文，逐字段一致）：

```json
{"model_id": "cohort_subscription", "base_revenue": 0,
 "drivers": {"opening_customers": [100], "new_customers": [40], "churned_customers": [20],
             "ending_customers": [120], "revenue_per_customer": [2],
             "new_customer_revenue_fraction": [0.25], "churned_customer_lost_fraction": [0.75],
             "timing_factor": [1], "usage_revenue": [5]},
 "years": [2027]}
```

手算（逐步，未取整）：
1. 客户桥：100 + 40 − 20 = **120** = `ending_customers` → 平衡成立；
2. 暴露：100 + 40 × 0.25 − 20 × 0.75 = 100 + 10 − 15 = **95**；
3. 收入：95 × 2 = **190**；190 × 1 = **190**；190 + 5 = **195**。

**期望输出 = `[195]`**（与卡片 L51 原文一致）。
- 输出长度 = 1 = `len(years)`；返回对象是纯数字列表（`year` 标签不可观测，唯一与年度相关的可观测量是长度）。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 1.95e-7。

## 3. 默认值案例（defaults；记录用，**不参与判定**）

只给五个必填 driver：

```json
{"model_id": "cohort_subscription", "base_revenue": 0,
 "drivers": {"opening_customers": [100], "new_customers": [40], "churned_customers": [20],
             "ending_customers": [120], "revenue_per_customer": [2]},
 "years": [2027]}
```

手算：桥 100 + 40 − 20 = 120 平衡成立；暴露 = 100 + 40 × **0.5（默认）** − 20 × **0.5（默认）**
= 100 + 20 − 10 = **110**；收入 = 110 × 2 × **1（默认）** + **0（默认）** = **220**。

**期望输出 = `[220]`**，长度 1。
- 证明三个显式默认值被应用、`usage_revenue` 的省缺被补 0，且**没有**被错当"必填缺失"。
- 注意：`usage_revenue` 在注册表中**没有**显式 default 项，是被 `spec.defaults.get(driver, 0.0)`
  静默补 0 的——这正是 `OQ-02`（"不存在"与"没找到"不可区分）在本模型上的实例。

## 4. 连续性（本卡**是**存量桥，卡片自带两年用例）

`cohort_subscription` 用专用 calculator `_cohort_subscription`，逐年检查**年内客户桥平衡**与
**跨年连续性**（`math.isclose(rel_tol=1e-9, abs_tol=1e-9)`），并有 `exposure < 0` 拒绝。

- Continuity positive = `card_M20.md` L59-125 原文用例（`years=[2027,2028]`，
  `opening=[100,120]`，`new=[40,0]`，`churned=[20,0]`，`ending=[120,120]`，`revenue_per_customer=[2,2]`，
  `new_customer_revenue_fraction=[0.25,0.25]`，`churned_customer_lost_fraction=[0.75,0.75]`，
  `timing_factor=[1,1]`，`usage_revenue=[5,0]`）。
  手算 2027 = 第 2 节 = **195**；
  手算 2028：第二年没有新增/退出/消耗/交付等流量，`opening` = 上期 `closing` = 120；
  桥 120 + 0 − 0 = 120 平衡成立，跨年 120 = 120 连续成立；暴露 = 120 + 0 − 0 = **120**；
  收入 = 120 × 2 × 1 + 0 = **240**。**期望 = `[195, 240]`**（与卡片 `expected_revenue` 一致），先运行通过。
- Continuity 断裂 patch（CONT-BREAK）= 卡片 `negative_patch` 原文：
  `opening_customers=[100,121]`、`ending_customers=[120,121]`。
  两个年度**各自**平衡（第一年 100+40−20=120 ✓；第二年 121+0−0=121 ✓），但第二年 `opening` 121
  比第一年 `closing` 120 多 1 → 预期 `ModelRegistryError`（`cohort customer continuity failed: FY2028`，
  卡片 L123 的 `expected_negative`）。

## 5. 负例（卡片专属 + N01–N05 + 断裂，共 11 个）

首个必填 driver = `opening_customers`。每个负例在**新的 deepcopy**、且**在内存中**构造
（不经 JSON 解析器），故 JSON 解析器拒绝不可能冒充模型拒绝。

| 例 | 变换 | 冻结预期 |
|---|---|---|
| NEG-CARD | 在正例上只把 `ending_customers` 换成 `[121]`（卡片 L53 原文） | `ModelRegistryError`（客户桥不平衡：120 ≠ 121） |
| N01a | `opening_customers[0] = True` | `ModelRegistryError` |
| N01b | `opening_customers[0] = float('nan')` | `ModelRegistryError` |
| N01c | `opening_customers[0] = float('inf')` | `ModelRegistryError` |
| N01d | `opening_customers[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `opening_customers = []` | `ModelRegistryError`（长度 ≠ len(years)） |
| N03 | 删除 `opening_customers` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | 卡片 `negative_patch`（基于 continuity_positive，先验证两年正例） | `ModelRegistryError`（跨年连续性） |

通过判据：必须是 `ModelRegistryError`；`ImportError` / `ModuleNotFoundError` / `FileNotFoundError`
**不得**计为通过。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999` | 输出与正例相同（`[195]`） | `_cohort_subscription` 丢弃 `base_revenue`；只登记 |
| OBS-DEFAULT-EQUIV | 在 defaults 上显式写 `timing_factor=[1]`、`usage_revenue=[0]`、`new_customer_revenue_fraction=[0.5]`、`churned_customer_lost_fraction=[0.5]` | 输出与 defaults 相同（`[220]`） | 使四个默认值可被证伪 |
| OBS-ZERO-CUSTOMERS | 全零客户桥（`opening/new/churned/ending=[0]`，`usage_revenue=[7]`） | **数值期望 `[7]`**：暴露 = 0 + 0 − 0 = 0；0 × 2 × 1 + 7 = 7 | 测量 `exposure < 0` 守卫的**下边界**：暴露恰为 0 必须被接受 |

OBS-ZERO-CUSTOMERS 的期望写在 `oracle.json` 的 `observation_expected` 中（手算得出，不来自产品）；
但它**不进入 runner 退出码**，只作为保真观测。

## 7. 卡片文字 vs 实现公式串

卡片只给算式与手算 195，未给实现公式串。运行后从隔离副本读取 `formula` 字段与第 1 节逐项比对；
若不一致，**记录差异**而不是修改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | 年内客户桥不平衡（期初+新客−流失 ≠ 期末） | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 跨年连续性断裂（本期期初 ≠ 上期期末） | `ModelRegistryError` | 是（CONT-BREAK） |
| R3 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R4 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R5 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R6 | `years` 为空 / 非连续 / 非整数财年 | `ModelRegistryError` | 是（N05a/b） |
| R7 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R8 | 暴露为负（流失损失比例过大） | `ModelRegistryError`（`exposure < 0`） | 间接（下边界 0 由 OBS-ZERO-CUSTOMERS 测量；负暴露未单列运行时例） |
| R9 | 无依据把时点默认成"年中" | **业务拒绝**：默认值为 1.0（非 0.5），且时点是披露问题 | 否（不是运行时契约） |
| R10 | 不同价格 / 同年新增又流失的群组未拆分 | **业务拒绝**：需专业拆分 | 否 |
| R11 | 客户桥容差被用来掩盖真实的 1 户错配 | 否：1.0 的不平衡远大于容差，CONT-BREAK 已拒绝 | 是（CONT-BREAK 即此例） |

## 9. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M20/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 是 `[professional_decision_required]`；本 attempt
  **未产出**任何披露映射（卡片 L151 明示其不阻塞 A–C，且不得虚填）。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计，该设计不存在。

## 10. 停止条件自检（`card_M20.md` L136-141）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，先记录反例，不重写实现。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`（本卡成立）。
- 存量桥：**本卡适用**（第 4 节），正例与断裂例均已执行；若断裂未被拒 → `STOP_BRIDGE`。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

## 11. runner 退出码口径（本批 M17–M20）

| rc | 含义 |
|---|---|
| 0 | pass：正例在冻结容差内、输出保真（长度/字段集）、连续性正例通过、11 个负例全部以 `ModelRegistryError` 拒绝 |
| 1 | harness error：runner 自身无法给出判定 |
| 2 | no verdict：冻结期望缺失，或观测输出与冻结形状**保真不符** |
| 3 | 判定为负：正例抛错或超容差、连续性不符、或至少一个负例未被按期望拒绝 |

优先级：1 > 2 > 3 > 0。与同批历史 M05–M08 runner 的差异（2/3 语义调整）显式登记在
`evidence/M20/run_result.json` 的 `exit_code_semantics.delta_vs_M05_M08_runner` 与 `review.md`。

## 12. 保真（fidelity）规则

输出必须是扁平序列、长度同时等于 `len(years)` 与 `len(expected)`、每个元素是普通 `int`/`float`
（bool 不算）且有限；`year` 标签不可观测这一点在 `fidelity` 块显式记录为
`year_labels_observable: false`。打印值必须与证据文件一致（runner 写完文件后回读比较）。

---

状态：`formula` = review_pending（待独立 reviewer）；`disclosure_adaptation` = unmapped；
`accuracy` = unproven。本文件不构成任何 acceptance。
