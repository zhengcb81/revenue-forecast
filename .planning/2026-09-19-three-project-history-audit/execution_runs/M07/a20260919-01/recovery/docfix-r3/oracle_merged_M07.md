# M07 · services — 冻结 oracle（运行前写定）

Card: M07（`execution_v2/card_M07.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M07/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 第 1–5 节全部数值预期来自**手算**，并由本 attempt 内独立脚本 `scripts/oracle_M07.py`
  用 Python 标准库复算；该脚本**不 import** 产品任何模块。
- **绝不**通过调用 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M07.md` L8「可计费小时/床日×利用率×U/小时或床日；人数先转活动量」
  与 L39「手算：10000×0.6=6000；6000×0.02+2=122」。实现入口 `model_registry.py:227` 仅在冻结后用于定位。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 可计费容量 × 利用率 × U/活动单位 × 时点因子 + 其他收入` | `card_M07.md` L8、L39 |
| 必填 driver | `billable_capacity`、`utilization`、`billing_rate` | `card_M07.md` L9 |
| 可选 driver / 默认 | `timing_factor` 默认 `1`；`other_revenue` 默认 `0` | `card_M07.md` L9 |
| 单位 | `billable_capacity` = 可计费工时/床日等**活动量**；`utilization` = 无量纲利用率；`billing_rate` = **U/小时或床日**；`other_revenue` = U；输出 = U | `card_M07.md` L8 |
| 量纲 | 活动 × 比例 × (U/活动) = U | 量纲自检 |
| 允许范围 | 容量非负；`utilization` 与 `timing_factor` 为比例（[0,1]）；`billing_rate` 非负 | 通用契约 |
| 人数转换 | **人数必须先转活动量**（FTE → 可计费工时/床日），不得人数 × 小时单价 | `card_M07.md` L8、L45 业务负例 |
| 利用率分母 | "可计费容量" 的定义域（毛可用 vs 扣除非计费时间）必须明示，不得二次乘利用率 | `card_M07.md` L43、L45 |
| 固定项目 | 项目制固定总价不得机械按工时开票确认 | `card_M07.md` L37 披露采集项 |
| 确认时滞 | 模型内无时滞项；`other_revenue` 是加项，不是递延项 | 通用契约 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；不允许负容量/负费率 | 通用契约 |

## 2. 合成正例（positive）

输入（=`card_M07.md` L12-37 原文）：

```json
{"model_id": "services", "base_revenue": 0,
 "drivers": {"billable_capacity": [10000], "utilization": [0.6], "billing_rate": [0.02],
             "timing_factor": [1], "other_revenue": [2]},
 "years": [2027]}
```

手算（逐步）：10000 × 0.6 = 6000；6000 × 0.02 = 120；120 × 1 = 120；120 + 2 = **122**。

**期望输出 = `[122]`**（与卡片 L39 原文一致）。输出长度 = 1 = `len(years)`。
容差 = `1e-9 × max(1, 122)` = 1.22e-7。

## 3. 默认值案例（defaults）

省略 `timing_factor` 与 `other_revenue`（均为 optional）：

```json
{"model_id": "services", "base_revenue": 0,
 "drivers": {"billable_capacity": [10000], "utilization": [0.6], "billing_rate": [0.02]},
 "years": [2027]}
```

手算：10000 × 0.6 × 0.02 × **1（默认）** + **0（默认）** = **120**。
**期望输出 = `[120]`**，长度 1。

## 4. 连续性案例（continuity）

`services` 是**逐年独立的流量模型，不是存量桥** → 存量桥资格 **not_applicable_with_reason**；
适用的是跨年财年连续性。

- Continuity positive：`years=[2027,2028]`，
  `billable_capacity=[10000, 12000]`，`utilization=[0.6, 0.55]`，`billing_rate=[0.02, 0.025]`，
  `timing_factor=[1, 1]`，`other_revenue=[2, 0]`
  手算：2027 = 10000×0.6×0.02×1+2 = 120+2 = **122**；
        2028 = 12000×0.55×0.025×1+0 = 6600×0.025 = **165**。
  期望 = `[122, 165]`。此例**先**运行通过。
- Continuity 断裂 patch：`years=[2027,2029]` → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `billable_capacity`。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `utilization = [1.01]` | `ModelRegistryError` |
| N01a | `billable_capacity[0] = True` | `ModelRegistryError` |
| N01b | `billable_capacity[0] = float('nan')` | `ModelRegistryError` |
| N01c | `billable_capacity[0] = float('inf')` | `ModelRegistryError` |
| N01d | `billable_capacity[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `billable_capacity = []` | `ModelRegistryError` |
| N03 | 删除 `billable_capacity` | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError` |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]` | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive） | `ModelRegistryError` |

合计 **11 个负例**。仅 `ModelRegistryError` 计通过；import/file 错误记为 FAIL。

NEG-CARD 语义：利用率 > 100% 表示超出可计费容量，卡片 L41 明确要求拒绝。
本卡沿用现行比例域作为拒绝条件，**不声称**经济上永不可能（`common_model_cards.md` L11）。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999` | 输出与正例相同 | `_rowwise` 丢弃 `base_revenue`；设计观察 |
| OBS-DEFAULT-EQUIV | 显式给出 `timing_factor=[1]`、`other_revenue=[0]` | 输出与默认值案例（第 3 节）相同 | 证明"省略"与"显式默认"等价；不是新契约 |

`OBS-DEFAULT-EQUIV` 是对 M07 最重要的接线探针：它把"默认值 = 1/0"从文档声明变成可复核事实，
同时**不**授权在缺披露时填 0/1（`common_model_cards.md` L22）。

## 7. 卡片文字 vs 实现公式串（须核对）

卡片未给实现公式串。运行后从隔离副本读取 `MODEL_REGISTRY["services"].formula`，
与第 1 节公式逐项比对（尤其：`timing_factor` 乘在 `billing_rate` 之后、`other_revenue` 为加项）。

## 8. 拒绝条件

| ID | 拒绝条件 | 冻结预期 | 可运行时执行 |
|---|---|---|---|
| R1 | `utilization` > 1 或 < 0 | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)` | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 空/非连续/非整数 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值/bool 冒充数值 | `ModelRegistryError` | 是（N01a-d） |
| R7 | 用员工人数 × 小时单价（量纲错误） | **业务拒绝**：人数必须先转可计费活动量 | 否 |
| R8 | 已实现计费小时再乘一次利用率（重复折算） | **业务拒绝**：需 `special_review` | 否 |
| R9 | 项目制固定总价按工时比例机械确认 | **业务拒绝**：需 `special_review` | 否 |
| R10 | 利用率分母口径未明示（毛可用 vs 净可用） | **业务拒绝**：STOP_DISCLOSURE_ADAPTATION | 否 |

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
本节追加前 `oracle.md` sha256 = `1eeb6806b82cb7fc70265fac512d263693e041076d195f4a0720dcbc3c9a3591`。

复审结论（独立 session 给出）：**M07 = accepted_scoped（仅 formula 资格）**

### 本轮处置清单

- F-M07-01 (source_manifest wording)
- F-M07-02 (mapped vs derived driver count)
- OQ-02 ruling
- **F-M07-01 更正**：`source_manifest.json` 的 `oracle_document.honest_gap` 原文称「pre-run hash was captured in commands.json」，但 `commands.json` 只记 argv/rc、不含 oracle.md 的 sha256。已改写该句，并补 `mtime_ordering`（oracle.md mtime 早于产品 stdout mtime）作为可核链条。
- **OQ-02 裁定（复审）**：`monetization_rate` 无 [0,1] 界**不是契约缺口**，只是命名歧义；枚举证据见 `evidence/M07/oq_rulings.json`。
- **OQ-04 裁定（复审维持）**：`model_registry.py:335` 静默补 0 成立；登记不改代码。
- **F-M07-02 更正**：`review.md` 明确写出计数口径——3 个必填中 1 个 `reported`（utilization 93.5%）、1 个 `derived`（billable_capacity 为实施者年化的下界）、1 个 `missing`（billing_rate）；`mapped_vs_missing` 只计 `reported`（1/3），**不把 derived 计入 mapped**。

### 未改动的内容（防止误读为「为过审而改」）

- 正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、停止条件、披露数值**一律未改**。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。

---

## 修订 r3（重复 r2 段折叠 · provenance gap 记录；只增不删既有正文）

本节由修订 r3 **插入**，位置 = 被折叠的第二段 r2 节的**原起点**（也就是保留段末尾；该位置同时也是文件末尾）。它只做两件事：（1）处置 F-M08-06 报出的「同一文件内两段重复的 r2 节 + 同一 hash 账本出现两个互斥基准」；（2）以 provenance gap 方式保留那条不能充当基准的 hash 值。**v1 冻结正文（第 0–10 节）、第一段 r2 节、全部冻结期望（正例/连续性/默认值/负例）、容差、拒绝条件、披露数值一律逐字节未改；实现与产品一行未动。**

### 合并账（本卡）

- 字节账（精确）：`合并前整文件 11469 字节 − 被折叠的重复段 1903 字节 + 本节 4147 字节 = 合并后整文件 13713 字节`。合并前 `oracle.md` sha256 = `ca4543b16aabb2963694f1c34fa6e5a56021de5db80cacde68eee7246d01d646`；合并前后完整 hash 账见 `evidence/M07/docfix_r3.json`。
- 被折叠的是**第二段 r2 节**（该节的二级标题 + 正文，纯重复）：它与紧邻其前的第一段 r2 节，除「本节追加前 `oracle.md` sha256」这一行外**逐字节相同**（归一化比对见 `recovery/docfix-r3/f06_dedupe.out.txt`）。被折叠段 = `pre[6564:]`。
- 保留段 = 文件前缀 `[0, 6564)`，共 9566 字节 = v1 冻结体 + 分隔块 + 第一段 r2 节 + 分隔块；本节的起点正是该前缀的末尾。因此 `live[:9566] == pre[:9566]` **逐字节成立**（live 以 pre 的完整 r2 正文为前缀），本节紧接其后插入。
- 合并前原文逐字节留档：`recovery/docfix-r3/oracle_pre_M07.md`（去重不销毁历史）。

### 两个基准的裁定（同一账本不得有两个互斥基准）

- **权威基准（保留）**：`1eeb6806b82cb7fc70265fac512d263693e041076d195f4a0720dcbc3c9a3591` = 本卡 v1 冻结体的 sha256，可在 char_offset 5305 处复现（7645 字节，即第 10 节末行之后的旧节末尾 EOF，等于 reviewer r1 记录的 v1 值）。
- **provenance gap（原值照录保留，但不得用作基准）**：`9da4b1ec7ea348641ab1f97c37ea2930d69f007e414875eefeed7476a5005d75`。穷举本文件全部字节切点后，该值**只能**在 char_offset 6555（9557 字节）以 as-is 前缀复现；而该前缀 = v1 冻结体 + **第一段 r2 正文**（不含其后的分隔块），也就是**已经包含上一段 r2 的中间写缓冲**，并不是「本节追加前」的文件状态。故其来源不可考（provenance gap）：原值照录于此，仅作历史留档，**不得作为任何 hash 账本的基准**，也不得据此推断冻结体被改过。
  - 复核脚本与原始输出：`recovery/docfix-r3/f06_brute.out.txt`（穷举 0..len(txt) 全部字节切点 × 4 种切法，`9da4b1ec7ea348641ab1f97c37ea2930d69f007e414875eefeed7476a5005d75` 命中 1 次）与 `f06_classify.out.txt`（该切点的逐字符邻域与行尾统计）。
  - 说明：按「行边界 + rstrip」的常规切法确实无法复现该值（rstrip 会吃掉 CRLF 的 `\r`，本文件 v1 区为 LF、r2 追加区为 CRLF，行尾混用），reviewer 的结论在那种切法下成立；本节的补充是：在字节级穷举下它可复现，但复现出来的是中间缓冲，因此仍不构成可用基准。
  - 折叠后该前缀依然是本文件的真实字节前缀（保留段末尾、本节起点之前），故该值在折叠后取得了确定含义；但它描述的仍是中间缓冲，不能当基准。

### 未改动的内容（防止误读为「为过审而改」）

- 第 0–10 节与第一段 r2 节**逐字节未变**；正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、披露数值**一律未改**。
- 冻结期望文本的分段逐字比对、以及「live = pre[:9566] + 本节」的重建等式，见 `recovery/docfix-r3/f06_verify.out.txt`。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。

---
