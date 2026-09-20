# M17 · licensing_commercial · 商业销售与许可收入 — 冻结 oracle（运行前写定）

Card: M17（`execution_v2/card_M17.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M17/a20260919-01`。model_id：`licensing_commercial`。
标题、卡号、model_id 与 `decision.md` / `handoff.json` / `review.md` 保持一致。

本文件在**任何产品代码运行之前**写定；写定后不得为贴合结果而修改。本 attempt 目前是 **r1**，
`oracle.md` 内**没有、也不得出现第二个「修订 r2」节**（见 `evidence/M17/revision_r2.json`）。

## 0. 独立性声明（最重要）

- 下列全部数值预期来自**手算**，并由本 attempt 内独立脚本 `scripts/oracle_M17.py` 用 Python
  标准库（`decimal` / `json` / `hashlib` / `argparse` / `os`）复算落盘。
  该脚本**不 import** 产品任何模块；`evidence/M17/oracle_selfcheck.json` 记录其 import 行与
  `product_import_present=false`。
- **绝不**调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M17.md` L8「单位/口径：患者/疗程/剂量选择一种×U/同单位；其他许可项为已确认金额」、
  L9 必填/可选、L39「手算：40×2+15+5+10=110」。实现入口与注册行号在使用前用隔离副本**逐行核对**
  （`evidence/M17/source_manifest.json` 的 `card_document_anchors_verified`）。
- 冻结顺序：`oracle.md`（本文件）→ `evidence/M17/oracle.json`（脚本生成）→ 首次产品 stdout。
  三者 mtime 顺序记录在 `evidence/M17/source_manifest.json` 的 `mtime_ordering`。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | 治疗单位 × 净单价 + 里程碑 + 销售分成 + 服务收入 | `card_M17.md` L8、L39 |
| 实现公式串（须核对，不得为对齐而改预期） | `revenue = treated_units * net_revenue_per_unit + milestone_revenue + royalty_revenue + service_revenue` | 隔离副本 `model_registry.py` 注册行 |
| 必填 driver | `treated_units`、`net_revenue_per_unit` | `card_M17.md` L9 |
| 可选 driver / 默认 | `milestone_revenue`、`royalty_revenue`、`service_revenue`，卡片默认均为 `0` | `card_M17.md` L9 |
| 单位 | `treated_units` = 患者/疗程/剂量（三选一，与净单价同口径）；`net_revenue_per_unit` = U/单位；其余三项 = U（已确认金额）；输出 = U/年 | `card_M17.md` L8 |
| 量纲 | 单位 × (U/单位) = U；三个金额项同为 U，可直接相加 | 量纲自检 |
| 有效域（枚举取得） | `treated_units`、`net_revenue_per_unit`、三个金额项 effective bounds 均为 `[0, inf)`；本模型**不在** `ratio_drivers` 中 | `evidence/M17/registry_enumeration.json` |
| 总净额 | 三个金额项必须是**已确认**金额；潜在里程碑不得计入 | `card_M17.md` L45 业务负例 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；不允许负治疗单位/负净价 | 通用契约 |

## 2. 合成正例（positive）

输入（=`card_M17.md` L12-37 原文，逐字段一致）：

```json
{"model_id": "licensing_commercial", "base_revenue": 0,
 "drivers": {"treated_units": [40], "net_revenue_per_unit": [2],
             "milestone_revenue": [15], "royalty_revenue": [5], "service_revenue": [10]},
 "years": [2027]}
```

手算（逐步，未取整）：40 × 2 = **80**；80 + 15 = **95**；95 + 5 = **100**；100 + 10 = **110**。

**期望输出 = `[110]`**（与卡片 L39 原文一致）。
- 输出长度 = 1 = `len(years)`；返回对象是纯数字列表（`year` 标签不可观测，唯一与年度相关的可观测量是长度）。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 1.1e-7。

## 3. 默认值案例（defaults；记录用，**不参与判定**）

省略三个可选 driver，只给必填：

```json
{"model_id": "licensing_commercial", "base_revenue": 0,
 "drivers": {"treated_units": [40], "net_revenue_per_unit": [2]},
 "years": [2027]}
```

手算：40 × 2 = 80；+ 0 + 0 + 0 = **80**。

**期望输出 = `[80]`**，长度 1。
- 该案例证明省缺的可选 driver 被当作 0（`model_registry.py` 的 `drivers.get(driver,
  [spec.defaults.get(driver, 0.0)] * len(years))`），且**没有**被错当"必填缺失"。
- 默认值不是缺披露时填零的授权（`common_model_cards.md` L22）；见 `OQ-02`。

## 4. 连续性（本卡为逐年独立模型）

`licensing_commercial` 由 `_rowwise` 实现：**逐年独立、无期初/期末对账项**，因此"存量断裂"
不适用（STOP_BRIDGE → not_applicable_with_reason，理由：公式中没有可断裂的存量桥）。
适用的连续性检查是**跨年财年连续性**：

- Continuity positive（`base_revenue=0`，`years=[2027,2028]`）：
  `treated_units=[40,55]`，`net_revenue_per_unit=[2,3]`，`milestone_revenue=[15,0]`，
  `royalty_revenue=[5,4]`，`service_revenue=[10,0]`。
  手算 2027：40×2+15+5+10 = 80+15+5+10 = **110**；
  手算 2028：55×3+0+4+0 = 165+0+4+0 = **169**。**期望 = `[110, 169]`**，先运行通过。
- Continuity 断裂 patch（CONT-BREAK）：`years=[2027,2029]`（缺 2028）→ 预期 `ModelRegistryError`
  （`years must be consecutive and increasing`）。

## 5. 负例（卡片专属 + N01–N05 + 断裂，共 11 个）

首个必填 driver = `treated_units`。每个负例都在**新的 deepcopy** 上构造，且**在内存中**构造
（不经 JSON 解析器），故 JSON 解析器拒绝不可能冒充模型拒绝。

| 例 | 变换（在正例基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `treated_units = [-1]`（卡片 L41 原文） | `ModelRegistryError`（数量域下界 0） |
| N01a | `treated_units[0] = True` | `ModelRegistryError` |
| N01b | `treated_units[0] = float('nan')` | `ModelRegistryError` |
| N01c | `treated_units[0] = float('inf')` | `ModelRegistryError` |
| N01d | `treated_units[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `treated_units = []` | `ModelRegistryError`（长度 ≠ len(years)） |
| N03 | 删除 `treated_units` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 continuity_positive，先验 positive） | `ModelRegistryError` |

通过判据：异常类型必须是 `ModelRegistryError`；`ImportError` / `ModuleNotFoundError` /
`FileNotFoundError` **不得**计为通过（`negative_results.json` 单列计数）。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999` | 输出与正例相同（`[110]`） | `_rowwise` 丢弃 `base_revenue`；只登记，不作为通过条件 |
| OBS-DEFAULT-EQUIV | 在 defaults 上显式写入三个金额项 `[0]` | 输出与 defaults 相同（`[80]`） | 使"默认 0"可被证伪 |

## 7. 卡片文字 vs 实现公式串

卡片只给算式与手算 110，未给实现公式串。运行后从隔离副本读取 `MODEL_REGISTRY` 的
`formula` 字段（`run_result.json` 的 `registry_metadata.formula`），与第 1 节逐项比对；
若不一致，**记录差异**而不是修改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | `treated_units` 为负 | `ModelRegistryError` | 是（NEG-CARD） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空 / 非连续 / 非整数财年 | `ModelRegistryError` | 是（N05a/b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R7 | 患者直接乘每剂价格（单位口径错配） | **业务拒绝**：需 `special_review`，本卡记为披露缺口 | 否（不是运行时契约） |
| R8 | 潜在里程碑当已确认收入 | **业务拒绝**：需 `special_review` | 否 |
| R9 | 三个金额项重复计入已确认收入（重复计算） | **业务拒绝**：需专业拆分 | 否 |
| R10 | 三个金额项为负（退款/冲回） | `ModelRegistryError`（通用非负域） | 间接（非负域，未单列运行时例） |

## 9. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定，状态见 `evidence/M17/qualification.json`；实现者**不自签**
  accepted，`formula` 记为 `review_pending`，由独立 reviewer 出结论。
- `disclosure_adaptation`：保持 **unmapped**。D 是 `[professional_decision_required]`，需逐字段
  披露映射经行业/会计 reviewer 签署，并需"一个已结束期间的收入对账 + 生产 forecast 入口映射
  经独立审阅"。本 attempt **未产出**任何披露映射（卡片 L71 明示这些文件不阻塞 A–C，且不得虚填）。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），
  该设计不存在；本卡不作准确性主张，也不从公式通过外推准确性。

## 10. 停止条件自检（`card_M17.md` L56-61）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`（本卡成立）。
- 存量桥：**not_applicable_with_reason**（第 4 节）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

## 11. runner 退出码口径（本批 M17–M20）

`scripts/run_card.py` 携带判定，**不是**记账式 rc=0：

| rc | 含义 |
|---|---|
| 0 | pass：正例在冻结容差内、输出保真（长度/字段集）、连续性正例通过、11 个负例全部以 `ModelRegistryError` 拒绝 |
| 1 | harness error：runner 自身无法给出判定（证据文件缺失/不可读、产品导入失败、case 循环外的意外异常） |
| 2 | no verdict：冻结期望缺失，或观测输出与冻结形状**保真不符**（长度 ≠ len(years) 或 ≠ len(expected)、元素非普通有限数、容器非扁平序列） |
| 3 | 判定为负：正例抛错或超容差、连续性正例不符、或至少一个负例未被按期望拒绝 |

优先级：1 > 2 > 3 > 0。
**与同批历史 M05–M08 runner 的差异（显式登记）**：那份 runner 用 2 = harness 失败、
3 = 负判定；本批把 harness 失败移到 1，把 2 留给"无法给出判定"。差异同时写入
`evidence/M17/run_result.json` 的 `exit_code_semantics.delta_vs_M05_M08_runner` 与 `review.md`。

## 12. 保真（fidelity）规则

正例不只比数值：

- 输出必须是**扁平序列**，长度同时等于 `len(years)` 与 `len(expected)`；
- 每个元素必须是普通 `int`/`float`（**bool 不算**）且有限；
- 返回对象不带年度字段，故 `year` 标签不可观测——这一点在 `fidelity` 块里显式记录为
  `year_labels_observable: false`，只把"长度"当作与年度相关的可观测量，不用推断冒充观测；
- 打印值必须与证据文件一致：runner 在写完文件后**回读**并比较
  positive / continuity / negative_summary / tolerances_ok / verdict / exit_code，
  把结果写进 `printed_values_match_evidence_file`，并打印同一行。

---

状态：`formula` = review_pending（待独立 reviewer）；`disclosure_adaptation` = unmapped；
`accuracy` = unproven。本文件不构成任何 acceptance。


## 13. 修订 r2（仅更正描述行，不动任何期望值）

本节由**独立复核结论之后**的一次独立命令追加；该命令的 argv / raw rc / stdout 单独留档在
`evidence/M17/runs/R2-append-oracle-addendum/`。**上方正文（r1 冻结版）逐字未改**：
正例/连续性/默认值期望、容差、负例清单、拒绝条件、停止条件与 runner 判定口径**一律未改**。

### 更正内容

- **错在何处**：第 1 节「有效域（枚举取得）」一行的来源列指向
  `evidence/M17/registry_enumeration.json`，但该行把 `milestone_revenue` / `royalty_revenue` /
  `service_revenue` 写成 `[0, inf)`；枚举文件记录的实测值是 `['-inf', 'inf']`，
  即**该行与它自己标注的出处相反**。
- **正确域与源码出处**：这三个金额 driver 属于 `_SIGNED_DRIVERS`（`scripts/model_registry.py:265-269`），
  而 `driver_value_bounds` 对 signed driver 返回 `(-inf, inf)`（同文件 `:289-290`），
  故三个金额项的有效域是 `(-inf, inf)`，**不是**非负域；`treated_units` 与
  `net_revenue_per_unit` 仍为 `[0, inf)`（本卡 NEG-CARD 的成立条件未变）。
- **实测证据**（`evidence/M17/extra_probes.json`，非判定性探针）：
  `PROBE-NEG-MILESTONE`（`milestone_revenue=[-5]`）实测 `[90.0]`（= 40×2−5+5+10），**被接受**；
  `PROBE-NEG-TOTAL-REVENUE`（`milestone_revenue=[-200]`）实测 `ModelRegistryError`——
  实现里唯一的负值守卫是"总收入不得为负"，单笔负数冲回可静默通过。
- **为何"只在别处登记"不充分**：`oracle.md` 是本卡的规范文件。只在 `oq_rulings.json` /
  `review.md` 登记，会让只读 oracle.md 的读者在 **D 阶段**把 signed 域误当非负域，
  从而误判"负数冲回不可能发生"——而这正是 D 需要判断的那类问题。
- **冻结期望未受影响**：没有任何期望值、容差或判据依赖该描述行，因此本节**不含任何数值变更**。
  追加前 `oracle.md` sha256 = `9c8021eebd01aa27a9963db8ac869ac6a067eb24af17439164f3cb61bc42fa69`，该值可在**真实行边界**（本节首行 `## 13.` 的字节偏移
  处）截断复现；证明见 `evidence/M17/oracle_addendum_record.json` 与
  `evidence/M17/revision_r2.json`。
- **范围限定**：本次更正**只**针对 M17。M18 / M19 / M20 的第 1 节有效域行经复核是正确的，
  不得由本节外推为"四卡都有描述错误"。
