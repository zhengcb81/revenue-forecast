# M23 · insurance_service · 保险服务披露映射 — 冻结 oracle（运行前写定）

Card M23（`execution_v2/card_M23.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M23/a20260919-01`。
本文在**任何产品代码运行之前**写定；写入后不得为贴合结果而修改，运行后的对账只允许以**追加**节形式补记（见文末「运行后对账」节）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M23.py` 用 Python 标准库（`decimal`/`json`/`hashlib`/`os`/`argparse`）复算。
  该脚本**不 import** 产品任何模块（`model_registry` / `model_extensions` 均不出现），
  自检记录见 `evidence/M23/oracle_selfcheck.json`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M23.md` L8、L36「手算：100×2×0.5+10=110」。
- 入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_registry.py:243`。 该入口仅在冻结之后用于定位调用点。
- `evidence/M23/oracle.json` 可由该脚本**逐字节重生成**（无时间戳、无随机量、无字典序依赖）。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | revenue = coverage_units × revenue_per_coverage_unit × timing_factor + other_revenue | `card_M23.md` L8 |
| 必填 driver | `coverage_units`、`revenue_per_coverage_unit` | `card_M23.md` L9 |
| 可选 driver / 默认 | `timing_factor`（默认 1）、`other_revenue`（默认 0） | `card_M23.md` L9 |
| 单位 | 覆盖单位必须披露定义；U/覆盖单位不能拿保费充当。 | `card_M23.md` L8 |
| 适用 | 仅有可验证覆盖单位与收入映射的保险业务；复杂 IFRS17 需精算/会计审批。 | `card_M23.md` L7 |
| 硬约束 | 输出长度 = `len(years)`；逐年检查；非有限值/布尔冒充数值一律拒绝 | 通用契约 |
| 比例域 | 维度为 `ratio` 的 driver 默认域 [0,1]；本卡**不声称**经济上永不可能 | `common_model_cards.md` L11 |
| 存量桥 | `insurance_service` **不是存量桥**（无期初/期末对账项），STOP_BRIDGE → **not_applicable_with_reason**；适用的连续性检查只有财年连续性。 | `card_M23.md` L133 |

## 2. 合成正例（positive）

输入 = `card_M23.md` 合成输入原文（逐字段一致）：

```json
{
 "model_id": "insurance_service",
 "base_revenue": 0,
 "drivers": {
  "coverage_units": [
   100
  ],
  "revenue_per_coverage_unit": [
   2
  ],
  "timing_factor": [
   0.5
  ],
  "other_revenue": [
   10
  ]
 },
 "years": [
  2027
 ]
}
```

手算（逐步，未取整）：

- 100 x 2 = 200; 200 x 0.5 = 100; 100 + 10 = 110

**期望输出 = `['110.0']`**（与卡片手算一致）。
- 输出长度 = 1 = `len(years)`；输出年份应为 `[2027]`。
- 逐值容差 = `1e-9 × max(1, |expected|)` = `[1.1e-07]`。
- 除数值外还比对**输出结构**：类型为 list、长度等于 `len(years)`、每个元素为有限 float（见 `formula_result.json` 的 `structure_checks`）。

## 3. 默认值案例（defaults）

只给必填 driver，省略全部可选 driver：

```json
{
 "model_id": "insurance_service",
 "base_revenue": 0,
 "drivers": {
  "coverage_units": [
   100
  ],
  "revenue_per_coverage_unit": [
   2
  ]
 },
 "years": [
  2027
 ]
}
```

手算：timing_factor omitted -> 1; other_revenue omitted -> 0; 100 x 2 x 1 = 200。

**期望输出 = `['200']`**，长度 1。
- 该案例证明默认值确实被应用，且**没有**被错当成「必填缺失」。
- 默认值不是缺披露时填零/一的授权（`common_model_cards.md` L22）；本案例只检验契约行为。
- 默认值案例**不参与**运行器退出码判定（`defaults_ok_not_gating`）。

## 4. 连续性案例（continuity）

本卡无存量桥，故 CONT-BREAK 采用**财年断裂**：`years = [2027, 2029]`（缺 2028），预期 `ModelRegistryError`。

- Continuity positive：`years = [2027, 2028]`；手算：
  - FY2027 = 100 x 2 x 0.5 + 10 → 110.0
  - FY2028 = 120 x 2.5 x 1 + 0 → 300.0
  期望 = `['110.0', '300.0']`。此例**先**运行通过，才允许应用断裂 patch。
- Continuity 断裂 patch：`years = [2027, 2029]`（缺 2028，财年不连续）
  → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `coverage_units`。每个负例使用**新的 deepcopy 独立输入**，互不共享可变对象；全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在冻结输入基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `timing_factor = [1.1]`（基于 `positive`） | `ModelRegistryError 且消息须含 `must be between 0.0 and 1.0: FY2027`` |
| N01a | `coverage_units[0] = True`（基于 `positive`） | `ModelRegistryError` |
| N01b | `coverage_units[0] = float('nan')`（基于 `positive`） | `ModelRegistryError` |
| N01c | `coverage_units[0] = float('inf')`（基于 `positive`） | `ModelRegistryError` |
| N01d | `coverage_units[0] = float('-inf')`（基于 `positive`） | `ModelRegistryError` |
| N02 | `coverage_units = []`（基于 `positive`） | `ModelRegistryError` |
| N03 | 删除 `coverage_units`（基于 `positive`） | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]`（基于 `positive`） | `ModelRegistryError` |
| N05a | `years = []`（基于 `positive`） | `ModelRegistryError` |
| N05b | `years = [True, ...]`（基于 `positive`） | `ModelRegistryError` |
| CONT-BREAK | `years = [2027, 2029]`（基于 `continuity_positive`） | `ModelRegistryError` |

合计 **11 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

NEG-CARD 语义：`timing_factor` 是卡片 L9 的可选比例项；`1.1` 越出 ratio 契约 [0,1]，冻结预期为 `ModelRegistryError`。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（基于 `positive`） | 与 `positive` 相同 | the coverage-unit calculation ignores base_revenue at this entry point; design observation only, not a pass condition |
| OBS-DEFAULT-EQUIV | {"timing_factor": [1], "other_revenue": [0]}（基于 `defaults`） | 与 `defaults` 相同 | explicit 1/0 equals the omitted default; makes the documented default falsifiable |
| OBS-TIMING-BOUND-11 | `timing_factor = [1.1, 0.5]`（基于 `continuity_positive`） | 不设预期 | records whether timing_factor = 1.1 on a 2-year path is refused by the VALUE-domain guard rather than by a length guard; the frozen gating case NEG-CARD is on the 1-year card input where no index 1 exists; NO expectation and NO verdict is asserted |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L51/… 只给出算式与手算结果，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["insurance_service"].formula`，与第 1 节公式逐项比对；
若不一致，记录差异而**不是**修改期望值（见文末「运行后对账」节）。

## 8. 拒绝条件（本卡记录并执行）

| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |
|---|---|---|---|
| R1 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |
| R2 | 缺必填 driver | `ModelRegistryError` | 是（N03） |
| R3 | 未注册 driver | `ModelRegistryError` | 是（N04） |
| R4 | `years` 为空/非整数财年 | `ModelRegistryError` | 是（N05a/N05b） |
| R5 | `years` 非连续递增 | `ModelRegistryError` | 是（CONT-BREAK） |
| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |
| R7 | 卡片专属的**运行时**拒绝条件 | `ModelRegistryError` | 是（NEG-CARD） |
| R8-BIZ | CSM、亏损合同或投资成分不明就做适配 | **业务拒绝**：需精算/会计 `special_review`，本卡记录为披露缺口 | 否（不是运行时契约） |
| R9-BIZ | 拿保费充当 U/覆盖单位 | **业务拒绝**：需 `special_review` | 否 |
| R10-BIZ | 把本模型当成完整 IFRS17 引擎 | **业务拒绝**：卡片 L42 明示不是 | 否 |

R8-BIZ–R10-BIZ 是**业务拒绝**条件（卡片「专业决策/业务负例」节），不在运行时契约内，因此在运行时负例表里不计入 pass/fail；它们属于 `disclosure_adaptation` 的 STOP 条件。
## 9. 披露采集与基期锚点（D/E 输入，不在本卡授予资格）

- 披露采集项：保险服务收入、覆盖单位、CSM/风险调整释放、投资成分排除、再保边界（`card_M23.md` L40）。
- 基期锚点：无（本卡卡片未给基期锚点字段）。
- 本卡只交付 A–C 公式证据；D/E 由 I-10-A 先行执行，F 需 I-12 冻结设计。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M23/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，且需「一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅」。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），该设计不存在；本卡不作准确性主张。

## 11. 停止条件自检（卡片「停止条件」节）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：**not_applicable_with_reason**（第 1 节）。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

## 12. 桥平衡的有效分辨率（独立复核要求补记；见文末追加节的来源说明）

本卡**不是存量桥**（第 1 节：not_applicable_with_reason），故桥平衡比较不适用；本卡的数值比较只有第 2/3 节的 `1e-9 × max(1, |expected|)` 容差。

---

（以下为运行后追记节，由 `scripts/append_oracle_run_section.py` 追加；
上方正文在运行前冻结，追加不改动任何期望值。）
---

## 运行后对账（追加节，不改动上方任何期望值）

本节由 `scripts/append_oracle_run_section.py` 在产品运行**之后**追加。
上方第 0–11 节在运行前冻结，**逐字节未改**；本节只记录实际观测到的值与差异，
不改动任何期望值、容差、负例清单或拒绝条件。

### 1. 实际运行结果

| 项 | 期望（第 2–4 节） | 实际 | 判定 |
|---|---|---|---|
| positive | `['110.0']` | `[110.0]` | within tolerance |
| continuity positive | `['110.0', '300.0']` | `[110.0, 300.0]` | ok |
| defaults（非判定） | `['200']` | `[200.0]` | ok |
| 负例 | 11 个全部 `ModelRegistryError` | 11/11 rejected | ok |

原始退出码 = **0**（0=pass / 2=no-verdict / 3=negative 未按期望拒绝 / 1=harness error）。
stdout / stderr 原文：`evidence/M23/stdout.txt`（3811 字节）、`evidence/M23/stderr.txt`（0 字节）。

### 2. 卡片文字 vs 实现公式串（第 7 节的核对结论）

- 实现注册公式串：`revenue = coverage_units * revenue_per_coverage_unit * timing_factor + other_revenue`
- 必填 driver（实现）：`['coverage_units', 'revenue_per_coverage_unit']`
- 可选 driver（实现）：`['timing_factor', 'other_revenue']`，默认值 `{'timing_factor': 1.0}`
- 结论：公式串与第 1 节冻结的公式**逐项一致**；未发现需要改预期的差异。

### 3. 每个负例的实际拒绝消息

| 例 | raised | message |
|---|---|---|
| NEG-CARD | `ModelRegistryError` | `driver insurance_service.timing_factor must be between 0.0 and 1.0: FY2027` |
| N01a | `ModelRegistryError` | `insurance_service.coverage_units.FY2027 must be numeric` |
| N01b | `ModelRegistryError` | `insurance_service.coverage_units.FY2027 must be finite` |
| N01c | `ModelRegistryError` | `insurance_service.coverage_units.FY2027 must be finite` |
| N01d | `ModelRegistryError` | `insurance_service.coverage_units.FY2027 must be finite` |
| N02 | `ModelRegistryError` | `driver insurance_service.coverage_units must contain one value per forecast year` |
| N03 | `ModelRegistryError` | `missing drivers for insurance_service: coverage_units` |
| N04 | `ModelRegistryError` | `unsupported drivers for insurance_service: unknown_driver` |
| N05a | `ModelRegistryError` | `insurance_service.years must contain fiscal years` |
| N05b | `ModelRegistryError` | `insurance_service.years must contain fiscal years` |
| CONT-BREAK | `ModelRegistryError` | `insurance_service.years must be consecutive and increasing` |

### 4. 观察项实际值（非判定）

| ID | raised | actual | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `None` | `[110.0]` |  |
| OBS-DEFAULT-EQUIV | `None` | `[200.0]` |  |
| OBS-TIMING-BOUND-11 | `ModelRegistryError` | `None` | driver insurance_service.timing_factor must be between 0.0 and 1.0: FY2027 |

### 5. 退出码变异自检（先红后绿）

| 探针 | 篡改 | 原始 rc | 期望 rc | 结论 |
|---|---|---|---|---|
| D_pristine_uncorrupted | （无篡改，scratch 副本） | 0 | 0 | 证明未篡改时仍是 0 |
| A_corrupted_positive_expectation | `oracle.json` 正例 `expected_float += 999` | 3 | 3 | 被篡改的期望不能藏在 rc=0 后面 |
| B_corrupted_negative_assertion | `cases.json` 追加一个产品**不会**拒绝的负例 | 3 | 3 | 负例断言被篡改会变红 |
| C_corrupted_positive_input | `input.json` 正例删除首个必填 driver | 2 | 2 | rc=2 可达：确实无法产生判定 |
| F_corrupted_expected_type | `cases.json` 某负例 `expected` 改成 `ValueError` | 3 | 3 | **复核 P2-1**：`expected` 字段被真正校验，不再只是抄写 |
| G_corrupted_message_requirement | `cases.json` 的 `expect_message_contains` 改成不可能出现的子串 | 3 | 3 | **复核 P2-2/P2-3**：消息要求被真正校验 |
| H_message_requirement_points_at_another_guard | 把 `expect_message_contains` 指向长度守卫的措辞 | 3 | 3 | 消息控制具有区分度：别的守卫的措辞不能冒充值域/连续守卫 |
| D_restored_uncorrupted | 恢复 scratch 副本 | 0 | 0 | 修复后退出码回到 0 |

冻结证据在探针前后 **hash 未变**：`True`。完整记录见 `recovery/selfcheck/selfcheck_result.json`。

### 6. 本节追加前后的 hash 账（可复现）

- 追加前 `oracle.md`（= 运行前冻结的完整正文，只归一化末尾的换行/`-` 分隔字符）**字节数** = 10481，sha256 = `ccd6fb673607521bbd524e9de08bd0e1e7f6d1335af35cf41cfa74a912a4b64f`
- 该值由**二进制读**取得（`open(path, 'rb')`），且 `frozen_body` 是真字节前缀：`oracle.md == frozen_body + b"\n---\n\n" + run_section`。复核方式：取 `oracle.md` 中第一次出现本节标题 `## 运行后对账（追加节，不改动上方任何期望值）` 之前的全部字节、去掉末尾换行后求 sha256。
- 追加时是否归一化了末尾分隔块：`True`（归一化后 `frozen_body` 是真字节前缀）。
- 追加后完整文件 sha256 见 `evidence/M23/source_manifest.json` 的 `oracle_document.sha256_full_file_now` 与 `after/rerun_sha256.json`。
- `evidence/M23/oracle.json` 可逐字节重生成（本 attempt 已复跑验证），因此「oracle 先冻结、后被运行」这条链不依赖 oracle.md 的 mtime。
