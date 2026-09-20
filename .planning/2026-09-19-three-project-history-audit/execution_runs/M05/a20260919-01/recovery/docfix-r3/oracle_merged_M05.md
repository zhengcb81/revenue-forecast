# M05 · subscription — 冻结 oracle（运行前写定）

Card: M05（`execution_v2/card_M05.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M05/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

## 0. 独立性声明（最重要）

- 第 1、2、3、4 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M05.py` 用 Python 标准库（`decimal`/`json`/`hashlib`）复算。
  该脚本**不 import** 产品任何模块（`model_registry` / `model_extensions` 均不出现）。
  自检命令见 `evidence/M05/oracle_selfcheck.json`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M05.md` L8「单位/口径：年度平均付费客户×U/客户年；用量收入单列」与
  L36「手算：200×3+20=620」；`implementation_plan.md` I-10 表。
  实现入口 `model_registry.py:225` 仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 年度平均付费客户 × U/客户年 × 时点因子 + 用量收入` | `card_M05.md` L8、L36 |
| 必填 driver | `average_customers`、`revenue_per_customer` | `card_M05.md` L9 |
| 可选 driver / 默认 | `timing_factor` 默认 `1`；`usage_revenue` 默认 `0` | `card_M05.md` L9 |
| 单位 | `average_customers` = 年度平均付费客户数（户）；`revenue_per_customer` = U/客户年；`usage_revenue` = U（金额，单列）；输出 = U | `card_M05.md` L8 |
| 量纲 | 客户 × (U/客户) = U；`timing_factor` 无量纲比例 | 量纲自检 |
| 允许范围 | 客户数与 ARPU 非负；`timing_factor` 为比例 | 通用契约（ratio 维 [0,1]） |
| 平均口径 | 必须是**期间平均**客户数，不得用期末客户代平均 | `card_M05.md` L42 业务负例 |
| 总净额 | ARPU 若已含用量收入，则不得再加 `usage_revenue`（重复计算） | `card_M05.md` L42 业务负例 |
| 确认时滞 | 模型内无时滞项；订阅期间分摊（递延确认）**不由本模型表达** | 卡片 L40 披露采集项 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；不允许负客户/负 ARPU | 通用契约 |

## 2. 合成正例（positive）

输入（=`card_M05.md` L12-34 原文）：

```json
{"model_id": "subscription", "base_revenue": 0,
 "drivers": {"average_customers": [200], "revenue_per_customer": [3],
             "timing_factor": [1], "usage_revenue": [20]},
 "years": [2027]}
```

手算（逐步，未取整）：

200 × 3 = 600；600 × 1 = 600；600 + 20 = **620**。

**期望输出 = `[620]`**（与卡片 L36 原文一致）。
- 输出长度 = 1 = `len(years)`；年份应与 `years` 相同。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 6.2e-7。

## 3. 默认值案例（defaults，本卡新增要求）

省略 `timing_factor` 与 `usage_revenue`（两者均为 optional），只给必填 driver：

```json
{"model_id": "subscription", "base_revenue": 0,
 "drivers": {"average_customers": [200], "revenue_per_customer": [3]},
 "years": [2027]}
```

手算：200 × 3 × **1（默认）** + **0（默认）** = **600**。

**期望输出 = `[600]`**，长度 1。
- 该案例证明默认值确实被应用，且**没有**被错当成"必填缺失"。
- 注意：默认值不是缺披露时填零/一的授权（`common_model_cards.md` L22）。

## 4. 连续性案例（continuity）

`subscription` 是**逐年独立的流量模型，不是存量桥**（无期初/期末对账项），
因此"存量断裂"不适用（STOP_BRIDGE → not_applicable，理由同 M01 第 5 节）。

适用的连续性检查是**跨年财年连续性**：

- Continuity positive：`base_revenue=0`，`years=[2027,2028]`，
  `average_customers=[180, 220]`，`revenue_per_customer=[3, 4]`，
  `timing_factor=[1, 1]`，`usage_revenue=[10, 0]`
  手算：2027 = 180×3×1+10 = 540+10 = **550**；2028 = 220×4×1+0 = **880**。
  期望 = `[550, 880]`。此例**先**运行通过。
- Continuity 断裂 patch：`years=[2027,2029]`（缺 2028，财年不连续）
  → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `average_customers`。每个负例用**新的 deepcopy 独立输入**，互不共享可变对象；
全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `timing_factor = [1.5]` | `ModelRegistryError` |
| N01a | `average_customers[0] = True` | `ModelRegistryError` |
| N01b | `average_customers[0] = float('nan')` | `ModelRegistryError` |
| N01c | `average_customers[0] = float('inf')` | `ModelRegistryError` |
| N01d | `average_customers[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `average_customers = []` | `ModelRegistryError`（路径长度 ≠ 1） |
| N03 | 删除 `average_customers` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive，先验 positive） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；
`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

NEG-CARD 语义：`timing_factor=1.5` 使收入口径不再是"期间分摊比例"，
卡片 L9 只把 `timing_factor` 列为可选比例项；本卡沿用现行 ratio 契约（[0,1]）作为拒绝条件，
**不声称**经济上永不可能（`common_model_cards.md` L11）。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（drivers/years 不变） | 输出与正例**相同** | `_rowwise` 丢弃 `base_revenue`；记录为设计观察，不作为通过条件 |
| OBS-ALT-CONV | 见第 7 节 | 仅登记，不设预期 | 记录卡片文字与实现公式串是否一致 |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L36 只给出算式与手算 620，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["subscription"].formula`，与第 1 节公式逐项比对；
若不一致，记录差异而不是修改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | `timing_factor` 越出比例域 | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空/非连续/非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R7 | 用**期末**客户数代替期间平均客户 | **业务拒绝**：需 `special_review`，本卡记录为披露缺口 | 否（不是运行时契约） |
| R8 | ARPU 已含用量又叠加 `usage_revenue`（重复计算） | **业务拒绝**：需 `special_review` | 否 |
| R9 | 用量收入未单列而与订阅收入混计 | **业务拒绝**：`usage_revenue` 必须单列 | 否 |
| R10 | 客户数/ARPU 为负 | `ModelRegistryError`（通用非负域） | 间接（N01d 为非有限） |

## 9. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M05/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，
  且需"一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅"；本 attempt 只提供最小映射证据。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），
  该设计不存在；本卡不作准确性主张，也不从公式通过外推准确性。

## 10. 停止条件自检（卡片 L53-58）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 4 节）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

---

## 修订 r2（独立复审意见的追加处置，非重写）

本节由修订 r2 **追加**。上方正文（v1 冻结版）**逐字未改**：正例/连续性/默认值预期、容差、负例清单、披露数值**一律未改**，实现与产品也**一行未动**。
本节追加前 `oracle.md` sha256 = `ae1986f61c03daa6ac633ffcc9eaf36060de08f1f39bf8f8c90e5315fe4e943a`。

复审结论（独立 session 给出）：**M05 = accepted_scoped（仅 formula 资格）**

### 本轮处置清单

- F-M05-01 (source_manifest pre-run-hash wording)
- F-M05-02 (self-check argv path + scope)
- **F-M05-01 更正**：`source_manifest.json` 的 `oracle_document.honest_gap` 原文称「pre-run hash was captured in commands.json」，但 `commands.json` 只记 argv/rc、不含 oracle.md 的 sha256。已改写该句，并补 `mtime_ordering`（oracle.md mtime 早于产品 stdout mtime）作为可核链条。
- **OQ-02 裁定（复审）**：`monetization_rate` 无 [0,1] 界**不是契约缺口**，只是命名歧义；枚举证据见 `evidence/M05/oq_rulings.json`。
- **OQ-04 裁定（复审维持）**：`model_registry.py:335` 静默补 0 成立；登记不改代码。
- **F-M05-02 更正**：`commands.json` 的 G 单元 argv 已改指真实 scratch 路径`M05/a20260919-01/recovery/selfcheck/scripts/run_card.py`，并注明该自检**只覆盖 M05**、其余三卡共用同一 runner（sha256 `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`，四份一致）。

### 未改动的内容（防止误读为「为过审而改」）

- 正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、停止条件、披露数值**一律未改**。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。

---

## 修订 r3（重复 r2 段折叠 · provenance gap 记录；只增不删既有正文）

本节由修订 r3 **插入**，位置 = 被折叠的第二段 r2 节的**原起点**（也就是保留段末尾；该位置同时也是文件末尾）。它只做两件事：（1）处置 F-M08-06 报出的「同一文件内两段重复的 r2 节 + 同一 hash 账本出现两个互斥基准」；（2）以 provenance gap 方式保留那条不能充当基准的 hash 值。**v1 冻结正文（第 0–10 节）、第一段 r2 节、全部冻结期望（正例/连续性/默认值/负例）、容差、拒绝条件、披露数值一律逐字节未改；实现与产品一行未动。**

### 合并账（本卡）

- 字节账（精确）：`合并前整文件 12592 字节 − 被折叠的重复段 1900 字节 + 本节 4152 字节 = 合并后整文件 14844 字节`。合并前 `oracle.md` sha256 = `fb8213ff988878b31f0bec31231f1542ab34089860cbc3a23fcc94e3eec6612f`；合并前后完整 hash 账见 `evidence/M05/docfix_r3.json`。
- 被折叠的是**第二段 r2 节**（该节的二级标题 + 正文，纯重复）：它与紧邻其前的第一段 r2 节，除「本节追加前 `oracle.md` sha256」这一行外**逐字节相同**（归一化比对见 `recovery/docfix-r3/f06_dedupe.out.txt`）。被折叠段 = `pre[7107:]`。
- 保留段 = 文件前缀 `[0, 7107)`，共 10692 字节 = v1 冻结体 + 分隔块 + 第一段 r2 节 + 分隔块；本节的起点正是该前缀的末尾。因此 `live[:10692] == pre[:10692]` **逐字节成立**（live 以 pre 的完整 r2 正文为前缀），本节紧接其后插入。
- 合并前原文逐字节留档：`recovery/docfix-r3/oracle_pre_M05.md`（去重不销毁历史）。

### 两个基准的裁定（同一账本不得有两个互斥基准）

- **权威基准（保留）**：`ae1986f61c03daa6ac633ffcc9eaf36060de08f1f39bf8f8c90e5315fe4e943a` = 本卡 v1 冻结体的 sha256，可在 char_offset 5835 处复现（8774 字节，即第 10 节末行之后的旧节末尾 EOF，等于 reviewer r1 记录的 v1 值）。
- **provenance gap（原值照录保留，但不得用作基准）**：`afeefe438e977ad4b449497baeac5c38eb4c003d5f7712d7079da37cbad4e0ce`。穷举本文件全部字节切点后，该值**只能**在 char_offset 7098（10683 字节）以 as-is 前缀复现；而该前缀 = v1 冻结体 + **第一段 r2 正文**（不含其后的分隔块），也就是**已经包含上一段 r2 的中间写缓冲**，并不是「本节追加前」的文件状态。故其来源不可考（provenance gap）：原值照录于此，仅作历史留档，**不得作为任何 hash 账本的基准**，也不得据此推断冻结体被改过。
  - 复核脚本与原始输出：`recovery/docfix-r3/f06_brute.out.txt`（穷举 0..len(txt) 全部字节切点 × 4 种切法，`afeefe438e977ad4b449497baeac5c38eb4c003d5f7712d7079da37cbad4e0ce` 命中 1 次）与 `f06_classify.out.txt`（该切点的逐字符邻域与行尾统计）。
  - 说明：按「行边界 + rstrip」的常规切法确实无法复现该值（rstrip 会吃掉 CRLF 的 `\r`，本文件 v1 区为 LF、r2 追加区为 CRLF，行尾混用），reviewer 的结论在那种切法下成立；本节的补充是：在字节级穷举下它可复现，但复现出来的是中间缓冲，因此仍不构成可用基准。
  - 折叠后该前缀依然是本文件的真实字节前缀（保留段末尾、本节起点之前），故该值在折叠后取得了确定含义；但它描述的仍是中间缓冲，不能当基准。

### 未改动的内容（防止误读为「为过审而改」）

- 第 0–10 节与第一段 r2 节**逐字节未变**；正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、披露数值**一律未改**。
- 冻结期望文本的分段逐字比对、以及「live = pre[:10692] + 本节」的重建等式，见 `recovery/docfix-r3/f06_verify.out.txt`。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。

---
