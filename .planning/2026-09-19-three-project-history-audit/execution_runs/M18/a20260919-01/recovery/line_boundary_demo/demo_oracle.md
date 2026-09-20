# M18 · advertising · 曝光填充与CPM — 冻结 oracle（运行前写定）

Card: M18（`execution_v2/card_M18.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M18/a20260919-01`。model_id：`advertising`。
标题、卡号、model_id 与 `decision.md` / `handoff.json` / `review.md` 保持一致。

本文件在**任何产品代码运行之前**写定；写定后不得为贴合结果而修改。本 attempt 目前是 **r1**，
`oracle.md` 内**没有、也不得出现第二个「修订 r2」节**（见 `evidence/M18/revision_r2.json`）。

## 0. 独立性声明（最重要）

- 下列全部数值预期来自**手算**，并由本 attempt 内独立脚本 `scripts/oracle_M18.py` 用 Python
  标准库（`decimal` / `json` / `hashlib` / `argparse` / `os`）复算落盘。该脚本**不 import** 产品任何模块。
- **绝不**调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M18.md` L8「填充前曝光机会÷1000×填充率×U/千次已变现曝光」、L9 必填/可选、
  L36「手算：1000000÷1000×0.8×10+100=8100」。实现入口与注册行号在使用前用隔离副本**逐行核对**
  （`evidence/M18/source_manifest.json` 的 `card_document_anchors_verified`）。
- 冻结顺序：`oracle.md`（本文件）→ `evidence/M18/oracle.json`（脚本生成）→ 首次产品 stdout。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | 曝光机会 ÷ 1000 × 填充率 × U/千次曝光 + 其他收入 | `card_M18.md` L8、L36 |
| 实现公式串（须核对，不得为对齐而改预期） | `revenue = eligible_impressions / 1000 * fill_rate * revenue_per_thousand_impressions + other_revenue` | 隔离副本 `model_registry.py` 注册行 |
| 必填 driver | `eligible_impressions`、`fill_rate`、`revenue_per_thousand_impressions` | `card_M18.md` L9 |
| 可选 driver / 默认 | `other_revenue`，卡片默认 `0` | `card_M18.md` L9 |
| 单位 | `eligible_impressions` = 填充前曝光机会（次）；`fill_rate` = 比例（无量纲）；`revenue_per_thousand_impressions` = U/千次已变现曝光；`other_revenue` = U（金额）；输出 = U/年 | `card_M18.md` L8 |
| 量纲 | 次 ÷ 1000 × 比例 × (U/千次) = U；金额项单列相加 | 量纲自检 |
| 有效域（来源：`model_registry.py:265-293`；运行时以 `registry_enumeration.json` 为准） | `eligible_impressions` = activity `[0, inf)`；`fill_rate` = ratio `[0, 1]`；`revenue_per_thousand_impressions` = revenue_per_activity `[0, inf)`；`other_revenue` 属于 `_SIGNED_DRIVERS`（`model_registry.py:265-269`）故为 `(-inf, inf)` | 枚举 + 源码 |
| 千次换算 | **只做一次**；不得先换成已填充曝光再乘一次填充率 | `card_M18.md` L42 业务负例 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；曝光/CPM 非负 | 通用契约 |

## 2. 合成正例（positive）

输入（=`card_M18.md` L12-34 原文，逐字段一致）：

```json
{"model_id": "advertising", "base_revenue": 0,
 "drivers": {"eligible_impressions": [1000000], "fill_rate": [0.8],
             "revenue_per_thousand_impressions": [10], "other_revenue": [100]},
 "years": [2027]}
```

手算（逐步，未取整）：1000000 ÷ 1000 = **1000**；1000 × 0.8 = **800**；800 × 10 = **8000**；
8000 + 100 = **8100**。

**期望输出 = `[8100]`**（与卡片 L36 原文一致）。
- 输出长度 = 1 = `len(years)`；返回对象是纯数字列表（`year` 标签不可观测，唯一与年度相关的可观测量是长度）。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 8.1e-6。

## 3. 默认值案例（defaults；记录用，**不参与判定**）

省略可选 driver `other_revenue`：

```json
{"model_id": "advertising", "base_revenue": 0,
 "drivers": {"eligible_impressions": [1000000], "fill_rate": [0.8],
             "revenue_per_thousand_impressions": [10]},
 "years": [2027]}
```

手算：1000 × 0.8 × 10 = 8000；+ 0 = **8000**。**期望输出 = `[8000]`**，长度 1。
- 证明省缺可选 driver 被当作 0，且**没有**被错当"必填缺失"。
- 默认值不是缺披露时填零的授权（`common_model_cards.md` L22）；见 `OQ-02`。

## 4. 连续性（本卡为逐年独立模型）

`advertising` 由 `_rowwise` 实现：**逐年独立、无期初/期末对账项**，"存量断裂"不适用
（STOP_BRIDGE → not_applicable_with_reason）。适用检查是**跨年财年连续性**：

- Continuity positive（`base_revenue=0`，`years=[2027,2028]`）：
  `eligible_impressions=[1000000, 1500000]`，`fill_rate=[0.8, 0.75]`，
  `revenue_per_thousand_impressions=[10, 12]`，`other_revenue=[100, 0]`。
  手算 2027：1000 × 0.8 × 10 + 100 = 8000 + 100 = **8100**；
  手算 2028：1500 × 0.75 = 1125；1125 × 12 = 13500；+ 0 = **13500**。**期望 = `[8100, 13500]`**，先运行通过。
- Continuity 断裂 patch（CONT-BREAK）：`years=[2027,2029]` → 预期 `ModelRegistryError`
  （`years must be consecutive and increasing`）。

## 5. 负例（卡片专属 + N01–N05 + 断裂，共 11 个）

首个必填 driver = `eligible_impressions`。每个负例在**新的 deepcopy**、且**在内存中**构造
（不经 JSON 解析器），故 JSON 解析器拒绝不可能冒充模型拒绝。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `fill_rate = [1.2]`（卡片 L38 原文） | `ModelRegistryError`（ratio 域上界 1） |
| N01a | `eligible_impressions[0] = True` | `ModelRegistryError` |
| N01b | `eligible_impressions[0] = float('nan')` | `ModelRegistryError` |
| N01c | `eligible_impressions[0] = float('inf')` | `ModelRegistryError` |
| N01d | `eligible_impressions[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `eligible_impressions = []` | `ModelRegistryError`（长度 ≠ len(years)） |
| N03 | 删除 `eligible_impressions` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive，先验 positive） | `ModelRegistryError` |

通过判据：必须是 `ModelRegistryError`；`ImportError` / `ModuleNotFoundError` / `FileNotFoundError`
**不得**计为通过。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999` | 输出与正例相同（`[8100]`） | `_rowwise` 丢弃 `base_revenue`；只登记 |
| OBS-DEFAULT-EQUIV | 在 defaults 上显式写 `other_revenue=[0]` | 输出与 defaults 相同（`[8000]`） | 使"默认 0"可被证伪 |
| OBS-THOUSAND-ONCE | 在正例上把 `eligible_impressions` 换成 `[2000000]` | **数值期望 `[16100]`**：2000 × 0.8 × 10 + 100 = 16000 + 100 | 卡片 L42「千次换算只做一次」的**可测**半边；若再除一次 1000 会得 16.1，故该期望能区分两种实现 |

OBS-THOUSAND-ONCE 的期望写在 `oracle.json` 的 `observation_expected` 中（与正例同样由手算得出，
不来自产品）；但它**不进入 runner 退出码**，只作为保真观测。

## 7. 卡片文字 vs 实现公式串

卡片只给算式与手算 8100，未给实现公式串。运行后从隔离副本读取 `formula` 字段与第 1 节逐项比对；
若不一致，**记录差异**而不是修改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | `fill_rate` 越出比例域（>1 或 <0） | `ModelRegistryError` | 是（NEG-CARD；边界值 1.0 由 C2 探针测量） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空 / 非连续 / 非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R7 | 已填充曝光又被乘一次填充率 | **业务拒绝**：需 `special_review`，本卡记为披露缺口 | 否（不是运行时契约：计算器无法判断 `eligible_impressions` 是否已是填充后数量） |
| R8 | 曝光机会被重复做千次换算 | 部分可测（OBS-THOUSAND-ONCE 数值期望） | 是（作为观测，不进退出码） |
| R9 | 无效流量（IVT）未剔除却按已变现曝光计价 | **业务拒绝**：需专业拆分 | 否 |
| R10 | 平台分成口径（gross/net）未声明 | **业务拒绝**：总净额不明 → STOP_DISCLOSURE_ADAPTATION | 否 |

## 9. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M18/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 是 `[professional_decision_required]`；本 attempt
  **未产出**任何披露映射（卡片 L68 明示其不阻塞 A–C，且不得虚填）。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计，该设计不存在。

## 10. 停止条件自检（`card_M18.md` L53-58）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，先记录反例，不重写实现。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`（本卡成立）。
- 存量桥：**not_applicable_with_reason**（第 4 节）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

## 11. runner 退出码口径（本批 M17–M20）

| rc | 含义 |
|---|---|
| 0 | pass：正例在冻结容差内、输出保真（长度/字段集）、连续性正例通过、11 个负例全部以 `ModelRegistryError` 拒绝 |
| 1 | harness error：runner 自身无法给出判定 |
| 2 | no verdict：冻结期望缺失，或观测输出与冻结形状**保真不符** |
| 3 | 判定为负：正例抛错或超容差、连续性不符、或至少一个负例未被按期望拒绝 |

优先级：1 > 2 > 3 > 0。与同批历史 M05–M08 runner 的差异（2/3 语义调整）显式登记在
`evidence/M18/run_result.json` 的 `exit_code_semantics.delta_vs_M05_M08_runner` 与 `review.md`。

## 12. 保真（fidelity）规则

输出必须是扁平序列、长度同时等于 `len(years)` 与 `len(expected)`、每个元素是普通 `int`/`float`
（bool 不算）且有限；`year` 标签不可观测这一点在 `fidelity` 块显式记录为
`year_labels_observable: false`。打印值必须与证据文件一致（runner 写完文件后回读比较）。

---

状态：`formula` = review_pending（待独立 reviewer）；`disclosure_adaptation` = unmapped；
`accuracy` = unproven。本文件不构成任何 acceptance。
