# M13 · asset_management — 冻结 oracle（运行前写定）

Card: M13（`execution_v2/card_M13.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M13/a20260919-01`。
本文在**任何产品代码运行之前**写定；正文写入后不为贴合结果而修改（修订只允许在文件末尾**追加**一节
「修订 r2」，且追加前正文的 sha256 必须在**真实行边界**可复现，见文末标记行）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算（十进制）**，并由本 attempt 内独立脚本
  `scripts/oracle_M13.py` 用 Python 标准库（`decimal`/`json`/`hashlib`）复算。
  该脚本**不 import** 产品任何模块（`model_registry` / `model_extensions` 均不出现在其 import 行）。
  自检证据：`evidence/M13/oracle_selfcheck.json`（含 `product_import_present=false` 与 import 行清单）。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M13.md` L8「单位/口径：平均可收费AUM为资产U；费率年度化；业绩报酬只计已确认金额」
  与 L36「手算：2000×0.01+3+2=25」。实现入口 `scripts/model_registry.py:308`
  （注册 `scripts/model_registry.py:233`）仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 平均可收费AUM × 管理费率 + 业绩报酬（已确认） + 其他收入` | `card_M13.md` L8、L36 |
| 必填 driver | `average_aum`、`management_fee_rate` | `card_M13.md` L9 |
| 可选 driver / 默认 | `performance_fee_revenue` 默认 0；`other_revenue` 默认 0 | `card_M13.md` L9 |
| 单位 | `average_aum` = 资产 U（货币余额）；`management_fee_rate` = 年化比例；业绩报酬与其他收入 = U | `card_M13.md` L8 |
| 量纲 | U × 比例 = U；三项相加仍为 U | 量纲自检 |
| 允许范围 | AUM 非负；管理费率为比例；业绩报酬为**带符号**金额（可负）；其他收入带符号 | 通用契约 + 本 attempt `evidence/M13/oq_enumeration.json` |
| 平均口径 | AUM 必须是**期间平均可收费**规模，不得用期末 AUM 代平均 | `card_M13.md` L42 业务负例 |
| 总净额 | 业绩报酬只计**已确认**金额；未结晶潜在报酬不得计入 | `card_M13.md` L8、L42 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；输出每个元素为有限 float | 通用契约 + `common_model_cards.md` L20 |

## 2. 合成正例（positive）

输入（=`card_M13.md` L12–34 原文）：

```json
{"model_id": "asset_management", "base_revenue": 0,
 "drivers": {"average_aum": [2000], "management_fee_rate": [0.01],
             "performance_fee_revenue": [3], "other_revenue": [2]},
 "years": [2027]}
```

手算（逐步，未取整）：

2000 × 0.01 = **20**；20 + 3 = **23**；23 + 2 = **25**。

**期望输出 = `[25]`**（与卡片 L36 原文一致）。
- 保真期望（结构/长度/字段集）：容器 `list`、长度 1 = `len(years)`、元素类型 `float`、全部有限、
  年度 = `[2027]`。冻结在 `oracle.json` 的 `expected_output_shape.positive`。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 2.5e-8。

## 3. 默认值案例（defaults，非 gating）

省略两个 optional driver（`performance_fee_revenue`、`other_revenue`），只给必填 driver：

```json
{"model_id": "asset_management", "base_revenue": 0,
 "drivers": {"average_aum": [2000], "management_fee_rate": [0.01]},
 "years": [2027]}
```

手算：2000 × 0.01 + **0（默认）** + **0（默认）** = 20 + 0 + 0 = **20**。

**期望输出 = `[20]`**，长度 1。
- 该案例证明可选 driver 的零默认确实被应用，且**没有**被错当成"必填缺失"。
- 注意：默认值不是缺披露时填零/一的授权（`common_model_cards.md` L22）；本卡在
  `evidence/M13/oq_rulings.json` 的 OQ-02 登记"省略即断言为零"的风险，但不改产品。

## 4. 连续性案例（continuity）

`asset_management` 是**逐年独立的流量模型，不是存量桥**（无期初/期末对账项），
因此"存量断裂"不适用（STOP_BRIDGE → **not_applicable_with_reason**）。
适用的连续性检查是**跨年财年连续性**：

- Continuity positive：`base_revenue=0`，`years=[2027, 2028]`，
  `average_aum=[2000, 2500]`，`management_fee_rate=[0.01, 0.012]`，
  `performance_fee_revenue=[3, 4]`，`other_revenue=[2, 1]`。
  手算：FY2027 = 2000×0.01 + 3 + 2 = 20 + 5 = **25**；
  FY2028 = 2500×0.012 + 4 + 1 = 30 + 5 = **35**。期望 = `[25, 35]`。此例**先**运行通过。
- Continuity 断裂 patch：`years=[2027, 2029]`（缺 2028，财年不连续）
  → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `average_aum`。每个负例使用**新的 deepcopy 独立输入**，互不共享可变对象；
全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。
card-specific 负例用 `set_driver_element`（而不是整体替换数组），因此它命中的是**值域守卫**，
不是数组长度守卫。

| 例 | 变换（在指定 base 输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `management_fee_rate[0] = 1.1`（base=positive） | `ModelRegistryError`（比例域 [0,1]） |
| N01a | `average_aum[0] = True` | `ModelRegistryError` |
| N01b | `average_aum[0] = float('nan')` | `ModelRegistryError` |
| N01c | `average_aum[0] = float('inf')` | `ModelRegistryError` |
| N01d | `average_aum[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `average_aum = []` | `ModelRegistryError`（长度 ≠ `len(years)`） |
| N03 | 删除 `average_aum` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]`（仅首年替换 True） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（base=continuity_positive，先验两年正例） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；
`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

NEG-CARD 语义：`management_fee_rate=1.1` 使年化费率越出比例域，卡片 L9 只把该 driver 列为比例项；
本卡沿用现行 ratio 契约（[0,1]，含端点）作为拒绝条件，**不声称**经济上永不可能
（`common_model_cards.md` L11）。

## 6. 观察项（非 pass/fail 设计观察，不参与退出码）

| ID | 变换 | 冻结预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（drivers/years 不变，base=positive） | 输出与正例**相同** = `[25]` | `_rowwise` 丢弃 `base_revenue`；记录为设计观察，不作为通过条件 |
| OBS-BOUND-INCLUSIVE | `management_fee_rate[0] = 1.0`（base=positive） | `[2005]`（手算 2000×1.0+3+2） | 证明比例域上端**含端点**：1.0 被接受而 NEG-CARD 的 1.1 被拒 |
| OBS-SIGNED-PERF-FEE | `performance_fee_revenue[0] = -100`（base=defaults） | `ModelRegistryError`（`calculated revenue cannot be negative`） | 业绩报酬是带符号 driver、无下界，因此回拨式负值通过 driver 守卫后，被"收入不得为负"的终检拦下；记录契约边界 |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L36 给出算式与手算 25，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["asset_management"].formula`，与第 1 节公式逐项比对；
若不一致，**记录差异**而不是修改期望值。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | `management_fee_rate` 越出比例域 | `ModelRegistryError` | 是（NEG-CARD；同一边界的 1.0 由 OBS-BOUND-INCLUSIVE 对照） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R5 | `years` 为空 / 非连续 / 非整数财年 | `ModelRegistryError` | 是（N05a/N05b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a–d） |
| R7 | 用**期末** AUM 代替期间平均可收费 AUM | **业务拒绝**：需 `special_review`，本卡记录为披露缺口 | 否（不是运行时契约） |
| R8 | 未结晶业绩报酬计入已确认收入 | **业务拒绝**：业绩报酬只计已确认金额 | 否 |
| R9 | 负值带符号 driver 使整行收入为负 | `ModelRegistryError`（现行终检） | 是（OBS-SIGNED-PERF-FEE；记录事实，不判业务对错） |
| R10 | 缺可选 driver 时被静默补零，等于断言"没有该项收入" | 契约事实（`model_registry.py:335`）；登记为 OQ-02，不改产品 | 是（defaults 案例 + 枚举） |

## 9. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M13/qualification.json`）；实现者**不自签** accepted，
  状态为 `review_pending`，只由独立 reviewer 授予。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，
  且需"一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅"；本 attempt 是纯合成公式卡，
  **没有**任何真实公司披露映射。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），
  该设计不存在；不得从公式通过外推准确性。

## 10. 停止条件自检（`card_M13.md` L53–58）

- positive 不等 / 保真不符 / 应拒绝负例未拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处、单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`（本卡 D 未开工）。
- 存量桥：**not_applicable_with_reason**（第 4 节：非存量模型）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

## 11. runner 退出码口径（本卡适用）

`scripts/run_card.py` 的退出码**承载判定**：`0=pass`、`1=harness error`、
`2=no-verdict（期望缺失或保真不符）`、`3=negative-case 未按期望拒绝`；多条件同时成立时优先级 `1 > 2 > 3`，
且全部触发条件逐条写入 `run_result.json` 的 `exit_code_semantics.triggered`。
`observations` 与 `defaults` **不参与**退出码。
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
  优先级 `1 > 2 > 3`；`run_card.py` 的模块 docstring 与 `evidence/M13/qualification.json`
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
  `scripts/selfcheck_mutation.py`，副本位于 `recovery/selfcheck/evidence/M13/`）。
- **R2-03（保真口径）**：正例不只看数值，还比对输出**结构/长度/元素类型/有限性/年度**；
  变异场景 F 把冻结形状的 `length` 改成 99，runner 因保真不符返回 2 而不是 0。
- **R2-04（打印与证据一致）**：`evidence/M13/stdout.txt` 是进程 stdout 的原始抓取，
  `scripts/verify_card.py` 断言其逐行等于 `run_result.json` 的 `printed_lines` 并复现
  `printed_sha256`，因此"打印值"不可能与证据文件不一致。
- R2-05 记录一个**按冻结规格无法构造**的观察项（不重写冻结件以掩盖）:

  - `OBS-SIGNED-PERF-FEE`: raised `KeyError` - 'performance_fee_revenue'

  该观察项不参与退出码（observed 非 gating），本卡 formula 判定不受影响；它想记录的契约事实改由 `recovery/probes/signed_driver_probe.json` （事后探针，明确标注非冻结用例）回答。

事后探针 `recovery/probes/signed_driver_probe.json`：对 driver `performance_fee_revenue` 取值 `-100.0`，实测 raised=`ModelRegistryError` actual=`None`，判定为 the signed driver passed the guard and the row was refused later by the non-negative-revenue check。

### 未改动的内容（防止误读为"为过审而改"）

- 正例/连续性/默认值预期、容差、11 个负例及其期望错误、拒绝条件、停止条件**一律未改**；
  唯一失效的观察项如实记录，**没有**为了让证据好看而重打包 `input.json`/`cases.json`/`oracle.json`。
- 冻结的三个证据文件在冻结时的 sha256：
  `input.json`=f4700cc24dd8d3f8df2660ff614bd7a6e92b44068c71f326a50fd4f03ce4e64d、`cases.json`=0353e544234eb8ea2557c055d99e1feafd962d771f127c46f4bda0ad10ac06f9、`oracle.json`=ab3a1f30fbad93da34a8786cdf3b4d532bca394ffc7ca1beb7214d6703a0e7b3
- 产品仓零改动；`changes.diff` 为 NO PRODUCT CHANGE 声明。
- `formula` 状态仍为 `review_pending`（实现者不自签），`disclosure_adaptation` 仍为 `unmapped`，
  `accuracy` 仍为 `unproven`。
<!-- R3-APPEND-BOUNDARY: everything above this line is the r2-reviewed frozen oracle body -->

## 修订 r3（对独立复核 F-01…F-05 的处置，非重写）

本节由修订 r3 **追加**，是 `oracle.md` 中**唯一**的一节「修订 r3」。
上方正文（v1 冻结版）与 r2 节逐字未改；产品仓库一行未动。r3 节的追加前 hash 记录在
`evidence/M13/revision_r3.json` 的 `boundary.sha256_of_bytes_before_the_marker`，并可由
`scripts/verify_r2_boundary.py` 在**真实行边界**（本标记行处）重新复现。本文件对每个修订只有
一个基准，不存在互斥的"追加前 hash"。

### 触发：独立复核（2026-09-20）判定 `accepted_scoped`（仅 formula）+ 5 项整改

独立复核者自写脚本、未调用本 attempt 的任何脚本，独立复算正例、自造 35 条负例（应拒而被接受 0 例）、
自建 harness replay、独立复现本 attempt 的验证脚本、逐字节复核冻结前缀 hash 与 1 字节边界修复，
并给出 **F-01…F-05 + 观察项 (c) + 计数单位** 整改清单。r3 逐条处置如下（工具层与证据层改动，
**不改任何冻结期望/容差/拒绝条件**）：

| 编号 | 处置 |
|---|---|
| F-01 | `run_card.py` 增加 **期望声明一致性**：逐 case 校验 `expected` 是否等于本 runner 实际据以判定的类型、case 数量与 id 集合是否与 `oracle.json` 的 `negative_count`/`negative_ids` 一致，并校验 kind/base_input；任何不一致 → `expectation_declaration_inconsistent` → **rc=2**，不再静默 rc=0。rev r1（只 `isinstance` 判定）保留在 `recovery/runner_before_F01_fix.py` 作为对照。 |
| F-02 | `enumerate_driver_bounds.py` 的 ratio 谓词改为**权威**的 `spec.dimensions[driver] == "ratio"`（并同时记录旧谓词 `ratio_drivers` 集合的计数与两者全部分歧条目），注册表口径由 40/3 更正为 **41/4**，与 M05–M08 r3 更正口径一致；`oq_enumeration.json` / `oq_rulings.json` 已重生成。 |
| F-03 | `oq_rulings.json` 的 OQ 列表改为**与 `handoff.json:open_questions` 一一对应**（编号同源），`decision.md`/`review.md` 的编号同步；并对全部文档指针做了可执行审计（`scripts/audit_doc_pointers.py` → `evidence/M13/doc_pointer_audit.json`）。 |
| F-04 | `finalize_hashes.py` 先写自产物再清点，且**把 `after/rerun_sha256.json` 自身排除**在清单与 combined digest 之外，新增 `self_reference_note` 与 `combined_digest_scope`，并对并发的 `after/git_status_*.txt` 标记 `concurrently_mutable`。 |
| F-05 | `recovery/README.md` 显式声明：首次 rc=1 调用（runner 的 `NameError`）与 `setup_isolation.ps1` 早期修订的**原始字节未留存**，只有 `raw_rc` 与叙述为证；今后首次失败调用一律把 stdout/stderr 原样另存。 |
| (c) | 观察项 `OBS-SIGNED-PERF-FEE` 按复核建议做**追加式标注**（不改语义）。`evidence/M13/cases.json` 追加了**只增不改**的标注字段（观察项 (c)）：旧 sha256 `0353e544234eb8ea2557c055d99e1feafd962d771f127c46f4bda0ad10ac06f9` → 新 sha256 `54399cd26596421ebae22b6efbdf7be19ea1af576ae0f69b8c193ba524702fb0`，差异经脚本 `build_cases_annotation_repack.py` 证明**仅为该字段**；`input.json` / `oracle.json` 逐字节未变，所有期望值/容差/拒绝条件未变。 |
| 计数单位 | `oq_rulings.json` 新增 `enumerated_counts_with_units`，把 registry 级计数标成 slot（(model,driver) 对）与 model 两种单位：31 slot / 24 model。 |

### 变异自检矩阵（先红后绿；冻结件未动）

| 实测 rc | 场景 |
|---|---|
| 0 | C-control, G-pre-fix-runner-corrupt-case-expected, H-pre-fix-runner-drop-negative-case |
| 1 | E-harness-error |
| 2 | A-corrupt-value, F-corrupt-shape, D-missing-expectation, G-corrupt-case-expected, H-drop-negative-case |
| 3 | B-corrupt-negative-case |

其中 `G/H-...` 为 F-01 新增场景；`G/H-pre-fix-runner-...` 是**修复前** runner 修订在同一份被污染副本上的
实测结果（rc=0，即复核报告所述缺陷的可复现证据）。详见 `recovery/selfcheck_result.json`
（含 `exit_code_matrix`、`pre_fix_runner_revision` 与冻结件前后 hash）。

### 本次改动的旧→新 hash（工具层与证据层）

| 文件 | 旧 sha256 | 新 sha256 |
|---|---|---|
| `scripts/run_card.py` | `e709408f7f6518be63fc00d5c4c444c8738dbf1ba7a53383c3821882c9054c9e` | `9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194` |
| `evidence/M13/oq_enumeration.json` | `093f9657d5d934f59fa1665927883e4dbc0fb489f2934f7be553b0e5f51c6f2d` | `814019ef6b7b6e7e65ee79324f2ab95028b01cb3b340450dcf3ac2990ee54541` |
| `evidence/M13/oq_rulings.json` | `186120a8c398367f9da2ec85abcfa40318a06153bdb3b3f1ec54011260056510` | `1f5be1b78e305d3d9566bb47434d99ebfd7e76f0c7bd6e78fac499fc438d79a9` |
| `evidence/M13/input.json` | `f4700cc24dd8d3f8df2660ff614bd7a6e92b44068c71f326a50fd4f03ce4e64d` | `f4700cc24dd8d3f8df2660ff614bd7a6e92b44068c71f326a50fd4f03ce4e64d` |
| `evidence/M13/oracle.json` | `ab3a1f30fbad93da34a8786cdf3b4d532bca394ffc7ca1beb7214d6703a0e7b3` | `ab3a1f30fbad93da34a8786cdf3b4d532bca394ffc7ca1beb7214d6703a0e7b3` |
| `evidence/M13/cases.json` | `0353e544234eb8ea2557c055d99e1feafd962d771f127c46f4bda0ad10ac06f9` | `54399cd26596421ebae22b6efbdf7be19ea1af576ae0f69b8c193ba524702fb0` |
| `evidence/M13/run_result.json` | `2b3bc8465a5eb811d2b7f6ce79345b93a3814bb6f29bf2492340fb64f9b7098d` | `e798caf7c1cf25c5fc78fb4e94a968a771efb55025bae464da5be8c19a56a55e` |
| `evidence/M13/stdout.txt` | `c051fabbf035800a35d7d4e4c0af5303804c9a2f976f926dedde2b1596dc1940` | `57f21bc8df6ff37e1a5eac439dfb1ed344d9c2dbb2984c6ecd3468cdc04819ad` |
| `after/rerun_sha256.json` | `fa1f4a2a5603f7735dfa6366bc0f929f7ad689de9e487e232b0173398bf93f70` | `fa1f4a2a5603f7735dfa6366bc0f929f7ad689de9e487e232b0173398bf93f70` |
| `oracle.md` | `4e71f45c2032a555e450da6cb2e20f28083bd95a48bab1ddf3a50b1be61d47ce` | `4e71f45c2032a555e450da6cb2e20f28083bd95a48bab1ddf3a50b1be61d47ce` |

### 未改动的内容（防止误读为"为过审而改"）

- **正例/连续性/默认值期望值、容差、11 个负例及其期望错误、拒绝条件、停止条件一律未改**；
  上述表中 `input.json` / `oracle.json` 两行若显示旧=新，即为证据。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。
- `formula` 仍为 `review_pending`（实现者不自签，r3 后交回复核者点验），
  `disclosure_adaptation` 仍为 `unmapped`，`accuracy` 仍为 `unproven`。
