# M08 · project_backlog — 冻结 oracle（运行前写定）

Card: M08（`execution_v2/card_M08.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M08/a20260919-01`。
本文在**任何产品代码运行之前**写定；本文件写入后不得为贴合结果而修改。

> ## 冻结前已发现的卡片/上游冲突（本卡头号未决问题）
>
> 卡片 L42 那一行 `100+40−5−10−15−60=50` 与它自己给出的**符号**不自洽，可区分出三种读法：
>
> | 读法 | 内容 | 同一输入的手算值 | 出处 |
> |---|---|---|---|
> | **A** | 卡片**印出的算术**：把 `contract_changes` 的**数值 10 直接减掉**，并把 `−15` 重估也减掉 | **50** | `card_M08.md` L42 的算式与答案 |
> | **B** | 卡片**印出的符号**（`− 合同变更`）套在"带符号金额"约定上：负的合同变更**增加**在手订单，故再减一次变 +10 | **70** | `card_M08.md` L8「变更与重估为带符号金额」＋ L42 的符号 |
> | **C** | **上游文档与实现公式串**：`+ 合同变更`（带符号相加） | **50** | `docs/buy_side_model_audit_2026-09-18.md:42`；`scripts/model_registry.py:228` |
>
> 读法 A 与 C 对**这一组**输入给出同一个数 50，但对符号相反的输入会分叉
> （`contract_changes=+10` 时 A 给 65、C 给 85，见第 6 节 OBS-SIGN-B），
> 因此 A 与 C 虽然数值巧合一致，**公式并不同**；B 则与两者都不同。
>
> 依 `execution_v2/README.md:20`「卡片Markdown和原总纲共同定义义务。若两者冲突，**停止受影响卡并更正索引**，
> 不能选更容易通过的一份」，本卡：
> 1. **不修改**卡片冻结的期望值（第 2 节仍写卡片原文 `[50]`），并如实运行记录真实结果；
> 2. 同时给出读法 B（70）与读法 C（50）的独立手算值，以及区分 A/B/C 的符号探针；
> 3. 把冲突登记为 `evidence/M08/card_conflict.json` 与 `decision.md` DEC-M08-1，交 owner/专业裁定；
> 4. **不自行判定**哪一读法正确，也**不据此修改产品**。

## 0. 独立性声明（最重要）

- 第 1–5 节全部数值预期来自**手算**，并由本 attempt 内独立脚本 `scripts/oracle_M08.py`
  用 Python 标准库（`decimal`/`json`/`hashlib`）复算；该脚本**不 import** 产品任何模块。
- **绝不**通过调用 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M08.md` L8、L42、L50-103；上游 `docs/buy_side_model_audit_2026-09-18.md:42`。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 期初 + 新签 − 取消 − 合同变更 + 非履约重估 − 期末`（卡片用减号） | `card_M08.md` L42 |
| 公式（上游文字/实现） | `revenue = 期初 + 新签 − 取消 + 合同变更 + 非履约重估 − 期末`（加号） | `docs/buy_side_model_audit_2026-09-18.md:42`；`model_registry.py:228` |
| 必填 driver | `opening_backlog`、`bookings`、`cancellations`、`contract_changes`、`closing_backlog` | `card_M08.md` L9 |
| 可选 driver / 默认 | `backlog_remeasurements` 默认 `0` | `card_M08.md` L9 |
| 单位 | 全部为**同一币种、同一范围、同一确认口径的金额 U**；输出 = U | `card_M08.md` L8 |
| 符号 | 变更与重估为**带符号金额**（可为负） | `card_M08.md` L8 |
| 量纲 | 金额 − 金额 = 金额 | 量纲自检 |
| 存量桥 | 本模型**就是**存量桥：必须满足期初+流入−流出=期末，且跨年 `opening[t] = closing[t-1]` | `card_M08.md` L50-103 |
| 重估剔除 | `backlog_remeasurements`（外汇/合并口径变化）必须单列，**不得**把未解释残差默认当收入 | `card_M08.md` L48；`model_ledger` 同项 |
| 确认时滞 | 订单减少 ≠ 收入；残差法只在所有存量变化完整列出时成立 | `card_M08.md` L48 |
| 硬约束 | 输出长度 = `len(years)`；逐年桥自平衡；跨年连续 | `card_M08.md` L50-103 |

## 2. 合成正例（positive）—— 冲突所在

输入（=`card_M08.md` L12-40 原文）：

```json
{"model_id": "project_backlog", "base_revenue": 0,
 "drivers": {"opening_backlog": [100], "bookings": [40], "cancellations": [5],
             "contract_changes": [-10], "backlog_remeasurements": [-15],
             "closing_backlog": [60]},
 "years": [2027]}
```

**读法 A（卡片 L42 印出的算术）—— 本卡冻结的期望：**

100 + 40 = 140；140 − 5 = 135；135 − 10 = 125（把 `contract_changes` 的**数值 10** 减掉）；
125 − 15 = 110（`−15` 重估也减掉）；110 − 60 = **50**。

**期望输出 = `[50]`**（与卡片 L42 答案一致）。容差 = `1e-9 × max(1, 50)` = 5e-8。

**读法 B（卡片 L42 印出的符号 `− 合同变更`，套在带符号金额约定上）：**

100 + 40 = 140；140 − 5 = 135；135 − (−10) = 145（负的合同变更使在手订单**增加**）；
145 + (−15) = 130（重估按 L8 是带符号加项）；130 − 60 = **70**。

**读法 C（上游文档 + 实现公式串 `+ 合同变更`）：**

100 + 40 = 140；140 − 5 = 135；135 + (−10) = 125；125 + (−15) = 110；110 − 60 = **50**。

三种读法下「−15 重估必须剔除（单列为桥的一项、不得当收入残差）」都成立。
第 6 节把读法 B、C 登记为**设计观察**，因此 A/B/C 三个值都会如实出现在证据里，
但 `formula_result.json` 的通过判据仍只用读法 A（卡片冻结期望）。
**重要提示（防止误读为通过）**：A 与 C 在本组输入上巧合地都得 50，这**不是**"实现与卡片一致"的证明——
第 6 节 OBS-SIGN-B 用 `contract_changes=+10` 把 A（65）与 C（85）区分开。

## 3. 默认值案例（defaults）

`backlog_remeasurements` 是唯一 optional（默认 0），因此"默认值案例"就是**省略该字段**的桥：

```json
{"model_id": "project_backlog", "base_revenue": 0,
 "drivers": {"opening_backlog": [100], "bookings": [40], "cancellations": [5],
             "contract_changes": [-10], "closing_backlog": [60]},
 "years": [2027]}
```

- 读法 A：100+40−5−10+**0（默认）**−60 = **65**（把 `contract_changes` 数值 10 减掉）。
- 读法 B：100+40−5−(−10)+**0（默认）**−60 = **85**。
- 读法 C：100+40−5+(−10)+**0（默认）**−60 = **65**。

**默认值案例期望（读法 A）= `[65]`**，容差 = 6.5e-8。读法 B/C 见第 6 节登记。

该案例同时证明：省略 `backlog_remeasurements` 不会把桥自动配平
（65 ≠ 50，也不是"残差作收入"的臆造值），即"缺重估不能自动把残差认作收入"。

## 4. 连续性案例（continuity，卡片 L50-103 原文）

两年 positive：

```json
{"model_id": "project_backlog", "base_revenue": 0, "years": [2027, 2028],
 "drivers": {"opening_backlog": [100, 60], "bookings": [40, 0], "cancellations": [5, 0],
             "contract_changes": [-10, 0], "backlog_remeasurements": [-15, 0],
             "closing_backlog": [60, 60]}}
```

手算（读法 A）：2027 = 50（第 2 节）；2028 = 60+0−0−0+0−60 = **0**。
**期望 = `[50, 0]`**（卡片 L87-90 原文）。
- 第 2 年 opening 60 = 第 1 年 closing 60 → 跨年连续成立。

Continuity 断裂 patch（卡片 L92-102 原文，只改这两项）：
`opening_backlog=[100, 61]`、`closing_backlog=[60, 61]`。
- 两个年度**各自**平衡（2027: 100+40−5−10−15−61... 注意 2027 的 closing 仍为 60，未改）
  实际 patch 只把第 2 年 opening 与第 2 年 closing 都设为 61：
  2028 = 61+0−0−0+0−61 = 0 仍自平衡，但**第 2 年 opening(61) ≠ 第 1 年 closing(60)**。
- **期望：`ModelRegistryError`（continuity）**。
- 该负例在两种读法下预期相同（只依赖 opening/closing 对账，与 `contract_changes` 符号无关）。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `opening_backlog`。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `closing_backlog = [500]`（桥严重不平衡） | `ModelRegistryError` |
| N01a | `opening_backlog[0] = True` | `ModelRegistryError` |
| N01b | `opening_backlog[0] = float('nan')` | `ModelRegistryError` |
| N01c | `opening_backlog[0] = float('inf')` | `ModelRegistryError` |
| N01d | `opening_backlog[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `opening_backlog = []` | `ModelRegistryError` |
| N03 | 删除 `opening_backlog` | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError` |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]` | `ModelRegistryError` |
| CONT-BREAK | 基于 continuity positive 应用卡片 L92-102 的 patch（先验两年 positive） | `ModelRegistryError` |

合计 **11 个负例**。仅 `ModelRegistryError` 计通过；import/file 错误记为 FAIL。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999` | 输出与正例相同 | `_project_backlog` 丢弃 `base_revenue`；设计观察 |
| OBS-SIGN-B | 基于 defaults、`contract_changes = [+10]` | **仅登记实际值，不设预期** | 区分 A/B/C 的探针：手算 A = 65、B = 65、C = 85；因此该探针能把 C 与 A/B 分开 |
| OBS-REMEASURE-USED | 省略 `backlog_remeasurements`（= 第 3 节默认值案例） | 输出**不等于**正例 | 省略后各读法值（65/85/65）与该读法正例值（50/70/50）都不同，证明重估项确实参与公式 |

`OBS-SIGN-B` 手算（`contract_changes = +10`）：A：100+40−5−10+0−60 = **65**；B：100+40−5−(−10)+0−60 = **65**；
C：100+40−5+(+10)+0−60 = **85**。该探针可把 C（加号读法）与 A/B 分开。

`OBS-SIGN-NEG` 手算（`contract_changes = −20`）：A：100+40−5−20+0−60 = **55**；
B：100+40−5−(−20)+0−60 = **95**；C：100+40−5+(−20)+0−60 = **55**。
该探针可把 B 与 A/C 分开。两组探针合起来即可唯一识别 A/B/C 中的哪一个被实现。
两个探针都只登记实际值，**不作为**通过条件，也不据此宣布实现错误。

## 7. 卡片文字 vs 实现公式串（本卡必须逐字核对）

从隔离副本读取 `MODEL_REGISTRY["project_backlog"].formula`，与本文件第 1 节两行逐项比对；
把结果写入 `evidence/M08/formula_string_check.json`。这是本卡冲突的**主要客观证据**：
实现公式串与上游文档一致、与卡片文字不一致时，属**文档缺陷**（卡片/索引待更正），
而不是"为过审改实现"的理由。

## 8. 拒绝条件

| ID | 拒绝条件 | 冻结预期 | 可运行时执行 |
|---|---|---|---|
| R1 | 年度桥不平衡（期初+流入−流出 ≠ 期末） | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 跨年 `opening[t] ≠ closing[t-1]` | `ModelRegistryError` | 是（CONT-BREAK） |
| R3 | 必填 driver 长度 ≠ `len(years)` | `ModelRegistryError` | 是（N02） |
| R4 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R5 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R6 | `years` 空/非连续/非整数 | `ModelRegistryError` | 是（N05a/b） |
| R7 | 非有限值/bool 冒充数值 | `ModelRegistryError` | 是（N01a-d） |
| R8 | 把订单减少全额当收入 | **业务拒绝**：订单减少不全是收入 | 否 |
| R9 | 缺重估时把未解释残差默认认作收入 | **业务拒绝**：`card_M08.md` L48 | 否（第 3 节给出算术反例） |
| R10 | 不同币种/范围/确认口径的订单金额混用同一桥 | **业务拒绝**：需 `special_review` | 否 |

## 9. 三种资格（本卡只填 formula，且本卡 formula 受阻）

- `formula`：**blocked**——卡片的冻结期望与上游文档/实现公式串在 `contract_changes` 符号上冲突，
  按 `README.md:20` 停止受影响卡并更正索引；裁定前不授予 formula 资格。
- `disclosure_adaptation`：**unmapped**。
- `accuracy`：**unproven**。
- 本卡**未**修改任何产品文件；见 `changes.diff`。

## 10. 停止条件自检

- 正例不等于卡片冻结期望 → `STOP_FORMULA` 的**触发条件**；本卡按协议
  「先记录反例，不重写实现」处理，并附上第二读法的独立手算值。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：本模型适用；连续性正例与断裂负例都要执行（第 4 节）。
- 准确性：`STOP_ACCURACY`。

---

## 修订 r2（独立复审意见的追加处置，非重写）

本节由修订 r2 **追加**。上方正文（v1 冻结版）**逐字未改**：正例/连续性/默认值预期、容差、负例清单、披露数值**一律未改**，实现与产品也**一行未动**。
本节追加前 `oracle.md` sha256 = `47481cab511f2bdf655ffbe3ff1f2d0b0d21c1f8c599cbb101c98124b2d57011`。

复审结论（独立 session 给出）：**M08 = blocked，且复审明确裁定 blocked 正确、不得改成读法 C 后通过**

### 本轮处置清单

- F-M08-01 (stale commands.json hash)
- F-M08-02 (disclosure impact anchored to reading C)
- F-M08-03 / F-M06-02 class (review.md title)
- F-M08-04 (L42 quotation corrected)
- F-M08-05 (sign-probe base_input)
- owner remediation three-step list
- OQ-04 named risk
- **F-M08-02 更正（最重要）**：r1 的披露影响只报读法 A（隐含确认 36.1210 亿元 / 残差 2.3610 亿元 / 6.99%）。本附录按复审要求把结论锚定到**实现读法 C**。核对后的完整结果见 `evidence/M08/disclosure_impact_readings.json`：
  - 重估取 0（FY2023 未披露，只有 0 与披露相容）：A/B/C **都**给出隐含确认 36.1210 亿元、残差 2.3610 亿元（6.99%）；
  - 重估取卡片合成值 −15 亿元作敏感性探针：读数降到 21.1210 亿元，残差升到 **12.6390 亿元（37.44%）**；
  - 因此诚实结论是**区间 2.36 - 12.64 亿元**，而不是单一的有利端数字；r1 只报了有利端。
  - 三种读法在这份历史对账上必然收敛，因为唯一能区分它们的两个驱动（取消、合同变更）未披露、只能记 0；在卡片冻结的合成输入上（两驱动已知）三者相差 20（A 50 / C 50 / B 70）。这是**披露缺口**的性质，不是符号问题不成立的证据。
- **F-M08-04 更正**：`card_M08.md` L42 **并没有印符号公式**，只印算式 `100+40−5−10−15−60=50`。r1 把一句符号式当作 L42 原文引用，属引用错误，已在 `card_conflict.json` 更正；实质冲突不变（唯一印出的算式蕴含「减去 10 的数值」，与三处上游/实现的「按带符号相加」在符号相反或大小未知的输入上分歧）。
- **F-M08-05 更正**：两个符号探针的基准已显式标注：`base_input = defaults`（省略重估的输入），并附上在正例基准下读法 C 会读到 70.0 / 40.0 的说明。
- **owner remediation（三步，实施者与 reviewer 都不能自签改卡）**：见 `handoff.json` 的 `owner_action_required`：① owner/I-10 专业裁定读法 C 权威（四处互证）；② 索引 owner 更正 card_M08.md L42 与 `model_cards.md`/`dispatch.md`（**算式与期望 [50] 不变**）；③ 索引更正后由独立 reviewer 在同一 code_root（`9ec65295…`）复跑留档，即可按 accepted_scoped（仅 formula）签收。
- **OQ-04 具名风险（复审维持）**：`model_registry.py:335` 对未列入 `spec.defaults` 的可选驱动静默补 0；对 `project_backlog.backlog_remeasurements` 而言，「没有重估」与「没查到重估」不可区分，桥会把未知量静默变成已确认收入。登记不改代码。

### 未改动的内容（防止误读为「为过审而改」）

- 正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、停止条件、披露数值**一律未改**。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。

---

## 修订 r3（重复 r2 段合并 · provenance gap 记录；追加式更正，非重写）

本节由修订 r3 **追加**，只做两件事：（1）处置 F-M08-06 报出的「同一文件内两段重复的 r2 节 + 同一 hash 账本出现两个互斥基准」；（2）以 provenance gap 方式保留那条不能充当基准的 hash 值。**v1 冻结正文（第 0–10 节）、第一段 r2 节、全部冻结期望（正例/连续性/默认值/负例）、容差、拒绝条件、披露数值一律逐字节未改；实现与产品一行未动。**

### 合并账（本卡）

- 合并前 `oracle.md` sha256 = `ff68cc5e01f87035e62d801727ddfa50bf9fd85bb30a4f799a4bf2eda36edbb1`（19745 字节）。合并前后完整 hash 账见 `evidence/M08/docfix_r3.json`。
- 被删除的是**第二段 r2 节**（该节的二级标题 + 正文，纯重复）：它与紧邻其前的第一段 r2 节，除「本节追加前 `oracle.md` sha256」这一行外**逐字节相同**（归一化比对见 `recovery/docfix-r3/f06_dedupe.out.txt`）。
- 保留段 = 文件前缀 `[0, 10247)`，共 16160 字节 = v1 冻结体 + 分隔块 + 第一段 r2 节 + 分隔块。
- 合并前原文逐字节留档：`recovery/docfix-r3/oracle_pre_M08.md`（去重不销毁历史）。

### 两个基准的裁定（同一账本不得有两个互斥基准）

- **权威基准（保留）**：`47481cab511f2bdf655ffbe3ff1f2d0b0d21c1f8c599cbb101c98124b2d57011` = 本卡 v1 冻结体的 sha256，可在 char_offset 8177 处复现（12557 字节，即第 10 节末行之后的旧节末尾 EOF，等于 reviewer r1 记录的 v1 值）。
- **provenance gap（原值照录保留，但不得用作基准）**：`b0d5f2093825dbbe7121cd8ac254669fb95562147a121724dee5c85e29bc7249`。穷举本文件全部字节切点后，该值**只能**在 char_offset 10247（16151 字节）以 as-is 前缀复现；而该前缀 = v1 冻结体 + **第一段 r2 正文**（不含其后的分隔块），也就是**已经包含上一段 r2 的中间写缓冲**，并不是「本节追加前」的文件状态。故其来源不可考（provenance gap）：原值照录于此，仅作历史留档，**不得作为任何 hash 账本的基准**，也不得据此推断冻结体被改过。
  - 复核脚本与原始输出：`recovery/docfix-r3/f06_brute.out.txt`（穷举 0..len(txt) 全部字节切点 × 4 种切法，`b0d5f2093825dbbe7121cd8ac254669fb95562147a121724dee5c85e29bc7249` 命中 1 次）与 `f06_classify.out.txt`（该切点的逐字符邻域与行尾统计）。
  - 说明：按「行边界 + rstrip」的常规切法确实无法复现该值（rstrip 会吃掉 CRLF 的 `\r`，本文件 v1 区为 LF、r2 追加区为 CRLF，行尾混用），reviewer 的结论在那种切法下成立；本节的补充是：在字节级穷举下它可复现，但复现出来的是中间缓冲，因此仍不构成可用基准。
  - 合并后该前缀依然是本文件的真实字节前缀（保留段末尾、r3 节前的 9 字节分隔块之前），故该值在合并后取得了确定含义；但它描述的仍是中间缓冲，不能当基准。

### 未改动的内容（防止误读为「为过审而改」）

- 第 0–10 节与第一段 r2 节**逐字节未变**；正例/连续性/默认值/负例的**期望值**、容差、拒绝条件、披露数值**一律未改**。
- 冻结期望文本的分段逐字比对、以及「合并后 = 保留段 + 本节」的重建等式，见 `recovery/docfix-r3/f06_verify.out.txt`。
- 公式与阈值未放宽；`formula` 状态见 `qualification.json`（M05/M06/M07 = review_pending，M08 = blocked）。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。

---
