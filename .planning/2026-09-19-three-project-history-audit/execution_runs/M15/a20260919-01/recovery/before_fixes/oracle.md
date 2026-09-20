# M15 · transport — 冻结 oracle（运行前写定）

Card: M15（`execution_v2/card_M15.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M15/a20260919-01`。
本文在**任何产品代码运行之前**写定；正文写入后不为贴合结果而修改（修订只允许在文件末尾**追加**一节
「修订 r2」，且追加前正文的 sha256 必须在**真实行边界**可复现，见文末标记行）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算（十进制）**，并由本 attempt 内独立脚本
  `scripts/oracle_M15.py` 用 Python 标准库（`decimal`/`json`/`hashlib`）复算。
  该脚本**不 import** 产品任何模块；自检证据：`evidence/M15/oracle_selfcheck.json`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M15.md` L8「单位/口径：客公里/吨公里容量×利用率×U/客公里或吨公里；yield是单价」
  与 L36「手算：1000×0.75×0.2+10=160」。实现入口 `scripts/model_registry.py:308`
  （注册 `scripts/model_registry.py:235`）仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 容量 × 利用率 × 单位收益(yield) + 辅助收入` | `card_M15.md` L8、L36 |
| 必填 driver | `capacity`、`utilization`、`yield` | `card_M15.md` L9 |
| 可选 driver / 默认 | `ancillary_revenue` 默认 0 | `card_M15.md` L9 |
| 单位 | `capacity` = 客公里/吨公里（容量）；`utilization` = 利用率（比例）；`yield` = U/客公里或吨公里（单价）；`ancillary_revenue` = U | `card_M15.md` L8 |
| 量纲 | 容量 × 比例 × (U/容量) = U；加辅助收入仍为 U。**容量与价格必须同量纲** | `card_M15.md` L8、L42 |
| 允许范围 | 容量非负；利用率为比例 [0,1]（含端点）；`yield` 是**单价**，不是制造良率，不受 [0,1] 限制；辅助收入带符号 | `card_M15.md` L42 + `evidence/M15/oq_enumeration.json` |
| 利用率分母 | 利用率分母必须在披露映射中明确（ASK/RPK 或吨公里口径） | `card_M15.md` L40 披露采集 |
| 总净额 | 燃油附加与辅助收入不得与票价收入重复计入 | `card_M15.md` L40 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；输出每个元素为有限 float | 通用契约 + `common_model_cards.md` L20 |

## 2. 合成正例（positive）

输入（=`card_M15.md` L12–34 原文）：

```json
{"model_id": "transport", "base_revenue": 0,
 "drivers": {"capacity": [1000], "utilization": [0.75], "yield": [0.2],
             "ancillary_revenue": [10]},
 "years": [2027]}
```

手算（逐步，未取整）：

1000 × 0.75 = **750**；750 × 0.2 = **150**；150 + 10 = **160**。

**期望输出 = `[160]`**（与卡片 L36 原文一致）。
- 保真期望：容器 `list`、长度 1、元素类型 `float`、全部有限、年度 `[2027]`。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 1.6e-7。

## 3. 默认值案例（defaults，非 gating）

```json
{"model_id": "transport", "base_revenue": 0,
 "drivers": {"capacity": [1000], "utilization": [0.75], "yield": [0.2]},
 "years": [2027]}
```

手算：1000 × 0.75 × 0.2 + **0（默认）** = 150 + 0 = **150**。**期望输出 = `[150]`**。

## 4. 连续性案例（continuity）

`transport` 是**逐年独立的流量模型**，"存量断裂"不适用（STOP_BRIDGE → **not_applicable_with_reason**）。
适用的是**跨年财年连续性**：

- Continuity positive：`years=[2027, 2028]`，`capacity=[1000, 1200]`，
  `utilization=[0.75, 0.7]`，`yield=[0.2, 0.22]`，`ancillary_revenue=[10, 12]`。
  手算：FY2027 = 1000×0.75×0.2 + 10 = 150 + 10 = **160**；
  FY2028 = 1200×0.7×0.22 + 12 = 840×0.22 + 12 = 184.8 + 12 = **196.8**。期望 = `[160, 196.8]`。
- Continuity 断裂 patch：`years=[2027, 2029]` → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `capacity`。每个负例使用**新的 deepcopy 独立输入**，不经 JSON 解析器。
card-specific 负例用 `set_driver_element`，命中**值域守卫**而非数组长度守卫。

| 例 | 变换（在指定 base 输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `utilization[0] = 1.1`（base=positive） | `ModelRegistryError`（比例域 [0,1]） |
| N01a | `capacity[0] = True` | `ModelRegistryError` |
| N01b | `capacity[0] = float('nan')` | `ModelRegistryError` |
| N01c | `capacity[0] = float('inf')` | `ModelRegistryError` |
| N01d | `capacity[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `capacity = []` | `ModelRegistryError`（长度 ≠ `len(years)`） |
| N03 | 删除 `capacity` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]` | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（base=continuity_positive） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；导入/文件错误不得算通过。

## 6. 观察项（非 pass/fail 设计观察，不参与退出码）

| ID | 变换 | 冻结预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（base=positive） | 与正例**相同** = `[160]` | `_rowwise` 丢弃 `base_revenue` |
| OBS-BOUND-INCLUSIVE | `utilization[0] = 1.0` | `[210]`（手算 1000×1.0×0.2 + 10） | 利用率域上端**含端点**：1.0 接受、1.1 拒绝 |
| OBS-YIELD-GT1 | `yield[0] = 1.5` | `[1135]`（手算 1000×0.75×1.5 + 10 = 1125 + 10） | 直接回应卡片 L42：**制造良率的 0–1 边界没有被移植到运输 yield**（yield 量纲为 revenue_per_unit，无上界） |
| OBS-SIGNED-ANCILLARY | `ancillary_revenue[0] = -20` | `[130]`（手算 150 − 20） | 辅助收入是带符号 driver，负值被接受且总收入仍非负 |

## 7. 卡片文字 vs 实现公式串

运行后从隔离副本读取 `MODEL_REGISTRY["transport"].formula`（预期
`revenue = capacity * utilization * yield + ancillary_revenue`）并逐项比对；
不一致时**记录差异**，不改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 运行时可否执行 |
|---|---|---|---|
| R1 | `utilization` 越出比例域 | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空 / 非连续 / 非整数财年 | `ModelRegistryError` | 是（N05a/N05b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a–d） |
| R7 | 把制造良率的 [0,1] 边界当成运输 yield 的边界 | **不适用**：yield 是单价；1.5 被接受（OBS-YIELD-GT1） | 是（观察项记录事实） |
| R8 | 容量与价格不同量纲（如 ASK 配吨公里 yield） | **业务拒绝**：需 `special_review`，属披露适配阶段 | 否（不是运行时契约） |
| R9 | 燃油附加既含在 yield 又计入辅助收入 | **业务拒绝**：需会计审定 | 否 |
| R10 | 利用率分母口径未披露 | **业务拒绝**：披露缺口（`card_M15.md` L40） | 否 |

## 9. 三种资格（本卡只填 formula）

- `formula`：由 A–C 结果决定（`evidence/M15/qualification.json`）；实现者**不自签**，状态 `review_pending`。
- `disclosure_adaptation`：保持 **unmapped**（本 attempt 纯合成）。
- `accuracy`：保持 **unproven**（无 I-12 冻结设计）。

## 10. 停止条件自检（`card_M15.md` L53–58）

- positive 不等 / 保真不符 / 应拒绝负例未拒绝 → `STOP_FORMULA`。
- 披露缺出处、单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 4 节）。
- 准确性：`STOP_ACCURACY`。

## 11. runner 退出码口径（本卡适用）

`scripts/run_card.py`：`0=pass`、`1=harness error`、`2=no-verdict（期望缺失或保真不符）`、
`3=negative-case 未按期望拒绝`；优先级 `1 > 2 > 3`。`observations` 与 `defaults` 不参与退出码。
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
  优先级 `1 > 2 > 3`；`run_card.py` 的模块 docstring 与 `evidence/M15/qualification.json`
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
  `scripts/selfcheck_mutation.py`，副本位于 `recovery/selfcheck/evidence/M15/`）。
- **R2-03（保真口径）**：正例不只看数值，还比对输出**结构/长度/元素类型/有限性/年度**；
  变异场景 F 把冻结形状的 `length` 改成 99，runner 因保真不符返回 2 而不是 0。
- **R2-04（打印与证据一致）**：`evidence/M15/stdout.txt` 是进程 stdout 的原始抓取，
  `scripts/verify_card.py` 断言其逐行等于 `run_result.json` 的 `printed_lines` 并复现
  `printed_sha256`，因此"打印值"不可能与证据文件不一致。
- R2-05：冻结的观察项全部按规格构造成功，没有需要在事后补探针的观察项。

事后探针 `recovery/probes/signed_driver_probe.json`：对 driver `ancillary_revenue` 取值 `-100.0`，实测 raised=`None` actual=`[50.0]`，判定为 the negative value was accepted and produced a value。

### 未改动的内容（防止误读为"为过审而改"）

- 正例/连续性/默认值预期、容差、11 个负例及其期望错误、拒绝条件、停止条件**一律未改**；
  唯一失效的观察项如实记录，**没有**为了让证据好看而重打包 `input.json`/`cases.json`/`oracle.json`。
- 冻结的三个证据文件在冻结时的 sha256：
  `input.json`=d403335d4f22fa583e688c196f45bd66c794004156b0c0ddf5f2f856f25c1c41、`cases.json`=4371f2eeb729de6329dbafdd35aecb123e3f99d68586ae69f1de1eee23dd3b90、`oracle.json`=c68164edbea00bc1d98d0ffd6695e69234987ad3232fa1fa34861be1145af06e
- 产品仓零改动；`changes.diff` 为 NO PRODUCT CHANGE 声明。
- `formula` 状态仍为 `review_pending`（实现者不自签），`disclosure_adaptation` 仍为 `unmapped`，
  `accuracy` 仍为 `unproven`。
