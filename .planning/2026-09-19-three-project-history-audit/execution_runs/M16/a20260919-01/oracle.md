# M16 · real_estate_rental — 冻结 oracle（运行前写定）

Card: M16（`execution_v2/card_M16.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M16/a20260919-01`。
本文在**任何产品代码运行之前**写定；正文写入后不为贴合结果而修改（修订只允许在文件末尾**追加**一节
「修订 r2」，且追加前正文的 sha256 必须在**真实行边界**可复现，见文末标记行）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算（十进制）**，并由本 attempt 内独立脚本
  `scripts/oracle_M16.py` 用 Python 标准库（`decimal`/`json`/`hashlib`）复算。
  该脚本**不 import** 产品任何模块；自检证据：`evidence/M16/oracle_selfcheck.json`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M16.md` L8「单位/口径：年度平均已租m²×U/m²年；已租面积不能再乘出租率」
  与 L33「手算：1000×0.03+2=32」。实现入口 `scripts/model_registry.py:308`
  （注册 `scripts/model_registry.py:236`）仅在冻结之后用于定位调用点。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | `revenue = 年度平均已租面积 × U/m²年 + 其他收入` | `card_M16.md` L8、L33 |
| 必填 driver | `average_occupied_area`、`rent_per_area` | `card_M16.md` L9 |
| 可选 driver / 默认 | `other_revenue` 默认 0 | `card_M16.md` L9 |
| 单位 | 面积 = m²（**已租**、年度平均）；`rent_per_area` = U/m²年（**年化**）；其他收入 = U | `card_M16.md` L8 |
| 量纲 | m² × (U/m²年) = U/年；加其他收入仍为 U | 量纲自检 |
| 允许范围 | 已租面积 ≥ 0（含端点 0）；`rent_per_area` ≥ 0；其他收入带符号 | 通用契约 + `evidence/M16/oq_enumeration.json` |
| 双重计数禁忌 | **已租面积不能再乘出租率**（没有再乘一次占用比例） | `card_M16.md` L8、L39 |
| 月租/年租 | 月租转年租必须**显式**换算，不得隐含 | `card_M16.md` L39 业务负例 |
| 会计口径 | 现金租金与直线法会计租金不同；免租期处理属披露适配阶段 | `card_M16.md` L37、L39 |
| 硬约束 | 输出长度 = `len(years)`；逐年独立；输出每个元素为有限 float | 通用契约 + `common_model_cards.md` L20 |

## 2. 合成正例（positive）

输入（=`card_M16.md` L12–31 原文）：

```json
{"model_id": "real_estate_rental", "base_revenue": 0,
 "drivers": {"average_occupied_area": [1000], "rent_per_area": [0.03],
             "other_revenue": [2]},
 "years": [2027]}
```

手算（逐步，未取整）：

1000 × 0.03 = **30**；30 + 2 = **32**。

**期望输出 = `[32]`**（与卡片 L33 原文一致）。
- 保真期望：容器 `list`、长度 1、元素类型 `float`、全部有限、年度 `[2027]`。
- 容差：`abs(actual - expected) <= 1e-9 × max(1, abs(expected))` = 3.2e-8。

## 3. 默认值案例（defaults，非 gating）

```json
{"model_id": "real_estate_rental", "base_revenue": 0,
 "drivers": {"average_occupied_area": [1000], "rent_per_area": [0.03]},
 "years": [2027]}
```

手算：1000 × 0.03 + **0（默认）** = **30**。**期望输出 = `[30]`**。

## 4. 连续性案例（continuity）

`real_estate_rental` 是**逐年独立的流量模型**（把已租面积与租金直接映射为收入），
"存量断裂"不适用（STOP_BRIDGE → **not_applicable_with_reason**）。
适用的是**跨年财年连续性**：

- Continuity positive：`years=[2027, 2028]`，`average_occupied_area=[1000, 1200]`，
  `rent_per_area=[0.03, 0.032]`，`other_revenue=[2, 3]`。
  手算：FY2027 = 1000×0.03 + 2 = 30 + 2 = **32**；
  FY2028 = 1200×0.032 + 3 = 38.4 + 3 = **41.4**。期望 = `[32, 41.4]`。
- Continuity 断裂 patch：`years=[2027, 2029]` → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `average_occupied_area`。每个负例使用**新的 deepcopy 独立输入**，不经 JSON 解析器。
card-specific 负例用 `set_driver_element`，命中**下界守卫**而非数组长度守卫。

| 例 | 变换（在指定 base 输入上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `average_occupied_area[0] = -1`（base=positive） | `ModelRegistryError`（下界 0.0） |
| N01a | `average_occupied_area[0] = True` | `ModelRegistryError` |
| N01b | `average_occupied_area[0] = float('nan')` | `ModelRegistryError` |
| N01c | `average_occupied_area[0] = float('inf')` | `ModelRegistryError` |
| N01d | `average_occupied_area[0] = float('-inf')` | `ModelRegistryError` |
| N02 | `average_occupied_area = []` | `ModelRegistryError`（长度 ≠ `len(years)`） |
| N03 | 删除 `average_occupied_area` | `ModelRegistryError`（缺必填） |
| N04 | 增加 `unknown_driver = [1]` | `ModelRegistryError`（未知字段） |
| N05a | `years = []` | `ModelRegistryError` |
| N05b | `years = [True]` | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（base=continuity_positive） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；导入/文件错误不得算通过。

## 6. 观察项（非 pass/fail 设计观察，不参与退出码）

| ID | 变换 | 冻结预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（base=positive） | 与正例**相同** = `[32]` | `_rowwise` 丢弃 `base_revenue` |
| OBS-BOUND-INCLUSIVE | `average_occupied_area[0] = 0` | `[2]`（手算 0×0.03 + 2） | 面积域下端**含端点**：0 接受、−1 拒绝（NEG-CARD） |
| OBS-SIGNED-OTHER | `other_revenue[0] = -1` | `[29]`（手算 30 − 1） | 其他收入是带符号 driver，负值被接受且总收入仍非负 |

## 7. 卡片文字 vs 实现公式串

运行后从隔离副本读取 `MODEL_REGISTRY["real_estate_rental"].formula`（预期
`revenue = average_occupied_area * rent_per_area + other_revenue`）并逐项比对；
不一致时**记录差异**，不改期望值。特别核对：注册的 driver 集合里**没有**出租率/占用率 driver，
即"已租面积不能再乘出租率"在契约层面成立（卡片 L8）。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 运行时可否执行 |
|---|---|---|---|
| R1 | `average_occupied_area` 为负 | `ModelRegistryError` | 是（NEG-CARD + OBS-BOUND-INCLUSIVE 对照） |
| R2 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R3 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R4 | 未注册 driver（例如把出租率当 driver 传入） | `ModelRegistryError` | 是（N04 的同类机制） |
| R5 | `years` 为空 / 非连续 / 非整数财年 | `ModelRegistryError` | 是（N05a/N05b、CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a–d） |
| R7 | 已租面积再乘出租率（双重折扣） | **业务拒绝**：卡片 L8 明确禁止；契约没有该 driver | 间接（不存在该 driver，无法传入） |
| R8 | 月租当成年租直接使用 | **业务拒绝**：须显式换算（`card_M16.md` L39） | 否（披露适配阶段） |
| R9 | 现金租金与直线法会计租金混用 | **业务拒绝**：需会计审定（L37） | 否 |
| R10 | `other_revenue` 为负 | 契约事实：带符号、接受（OBS-SIGNED-OTHER） | 是（观察项记录事实） |

## 9. 三种资格（本卡只填 formula）

- `formula`：由 A–C 结果决定（`evidence/M16/qualification.json`）；实现者**不自签**，状态 `review_pending`。
- `disclosure_adaptation`：保持 **unmapped**（本 attempt 纯合成）。
- `accuracy`：保持 **unproven**（无 I-12 冻结设计）。

## 10. 停止条件自检（`card_M16.md` L50–55）

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
  优先级 `1 > 2 > 3`；`run_card.py` 的模块 docstring 与 `evidence/M16/qualification.json`
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
  `scripts/selfcheck_mutation.py`，副本位于 `recovery/selfcheck/evidence/M16/`）。
- **R2-03（保真口径）**：正例不只看数值，还比对输出**结构/长度/元素类型/有限性/年度**；
  变异场景 F 把冻结形状的 `length` 改成 99，runner 因保真不符返回 2 而不是 0。
- **R2-04（打印与证据一致）**：`evidence/M16/stdout.txt` 是进程 stdout 的原始抓取，
  `scripts/verify_card.py` 断言其逐行等于 `run_result.json` 的 `printed_lines` 并复现
  `printed_sha256`，因此"打印值"不可能与证据文件不一致。
- R2-05：冻结的观察项全部按规格构造成功，没有需要在事后补探针的观察项。

事后探针 `recovery/probes/signed_driver_probe.json`：对 driver `other_revenue` 取值 `-100.0`，实测 raised=`ModelRegistryError` actual=`None`，判定为 the signed driver passed the guard and the row was refused later by the non-negative-revenue check。

### 未改动的内容（防止误读为"为过审而改"）

- 正例/连续性/默认值预期、容差、11 个负例及其期望错误、拒绝条件、停止条件**一律未改**；
  唯一失效的观察项如实记录，**没有**为了让证据好看而重打包 `input.json`/`cases.json`/`oracle.json`。
- 冻结的三个证据文件在冻结时的 sha256：
  `input.json`=641b938b767bd22318572db0e1dc11e964fa106ba5d5419760b8288f71670e07、`cases.json`=fffb558223238091b4920e29d194f3c4b04f030d491cba8552ea8065873b2a70、`oracle.json`=2f300c78acd0035a09f1005957a5a97a7698d15fb8ee0b660bcaa6acfb228c92
- 产品仓零改动；`changes.diff` 为 NO PRODUCT CHANGE 声明。
- `formula` 状态仍为 `review_pending`（实现者不自签），`disclosure_adaptation` 仍为 `unmapped`，
  `accuracy` 仍为 `unproven`。
<!-- R3-APPEND-BOUNDARY: everything above this line is the r2-reviewed frozen oracle body -->

## 修订 r3（对独立复核 F-01…F-05 的处置，非重写）

本节由修订 r3 **追加**，是 `oracle.md` 中**唯一**的一节「修订 r3」。
上方正文（v1 冻结版）与 r2 节逐字未改；产品仓库一行未动。r3 节的追加前 hash 记录在
`evidence/M16/revision_r3.json` 的 `boundary.sha256_of_bytes_before_the_marker`，并可由
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
| F-03 | `oq_rulings.json` 的 OQ 列表改为**与 `handoff.json:open_questions` 一一对应**（编号同源），`decision.md`/`review.md` 的编号同步；并对全部文档指针做了可执行审计（`scripts/audit_doc_pointers.py` → `evidence/M16/doc_pointer_audit.json`）。 |
| F-04 | `finalize_hashes.py` 先写自产物再清点，且**把 `after/rerun_sha256.json` 自身排除**在清单与 combined digest 之外，新增 `self_reference_note` 与 `combined_digest_scope`，并对并发的 `after/git_status_*.txt` 标记 `concurrently_mutable`。 |
| F-05 | `recovery/README.md` 显式声明：首次 rc=1 调用（runner 的 `NameError`）与 `setup_isolation.ps1` 早期修订的**原始字节未留存**，只有 `raw_rc` 与叙述为证；今后首次失败调用一律把 stdout/stderr 原样另存。 |
| (c) | 观察项 `OBS-SIGNED-PERF-FEE` 按复核建议做**追加式标注**（不改语义）。`evidence/M16/cases.json` 追加了**只增不改**的标注字段（观察项 (c)）：旧 sha256 `fffb558223238091b4920e29d194f3c4b04f030d491cba8552ea8065873b2a70` → 新 sha256 `fffb558223238091b4920e29d194f3c4b04f030d491cba8552ea8065873b2a70`，差异经脚本 `build_cases_annotation_repack.py` 证明**仅为该字段**；`input.json` / `oracle.json` 逐字节未变，所有期望值/容差/拒绝条件未变。 |
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
| `evidence/M16/oq_enumeration.json` | `af003c2acbd6b99085d7318f0f489fda565abd8de3b98a19062603279f5574d2` | `4e5e5a4f3da951deb72123aa14fb6d1f8f350eafd139fb3e953337b771f6bd66` |
| `evidence/M16/oq_rulings.json` | `e7ba09517bcdf9a818e5340687ac81de462ccf6eee12116962925465ab0558be` | `2fa34ad9f7c19d2a1fcab82797a4aebf3bb7708dc4fe4780e66d6bbf1fd19d85` |
| `evidence/M16/input.json` | `641b938b767bd22318572db0e1dc11e964fa106ba5d5419760b8288f71670e07` | `641b938b767bd22318572db0e1dc11e964fa106ba5d5419760b8288f71670e07` |
| `evidence/M16/oracle.json` | `2f300c78acd0035a09f1005957a5a97a7698d15fb8ee0b660bcaa6acfb228c92` | `2f300c78acd0035a09f1005957a5a97a7698d15fb8ee0b660bcaa6acfb228c92` |
| `evidence/M16/cases.json` | `fffb558223238091b4920e29d194f3c4b04f030d491cba8552ea8065873b2a70` | `fffb558223238091b4920e29d194f3c4b04f030d491cba8552ea8065873b2a70` |
| `evidence/M16/run_result.json` | `e79ecacd8e124233b7f61b66c5ee491683d3ccfcabb3425d8697a828beb93110` | `c88f345c3b6ae308e8d412c25e8ddf10648eb6b9d1980134f48ea5f5d9967961` |
| `evidence/M16/stdout.txt` | `311858e49730dfa3ee45bc3f564828c18a24d76984abeaa5218e7b25f27dff52` | `4031a60f1dd8133392a7cb2d4e3e7fbd4ff79543a566c2626f2e14deba2a5af1` |
| `after/rerun_sha256.json` | `c8bf4f9427f98ba9c64a34b72410b52c90d9def762ee6834be587dafb5cd0782` | `8a2188fe0251d8f606cfd97e7760e9dbfa0a2304de48e54b33275cf35a5cba2c` |
| `oracle.md` | `c71605d7bb9480b6c93976dafb9a05b3b9597dedbf9ff0740e44cd8aaa25dc3e` | `c71605d7bb9480b6c93976dafb9a05b3b9597dedbf9ff0740e44cd8aaa25dc3e` |

### 未改动的内容（防止误读为"为过审而改"）

- **正例/连续性/默认值期望值、容差、11 个负例及其期望错误、拒绝条件、停止条件一律未改**；
  上述表中 `input.json` / `oracle.json` 两行若显示旧=新，即为证据。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。
- `formula` 仍为 `review_pending`（实现者不自签，r3 后交回复核者点验），
  `disclosure_adaptation` 仍为 `unmapped`，`accuracy` 仍为 `unproven`。
