# M24 · subscription_arr_bridge · ARR 存量与收入时点 — 冻结 oracle（运行前写定）

Card M24（`execution_v2/card_M24.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。
Attempt: `execution_runs/M24/a20260919-01`。
本文在**任何产品代码运行之前**写定；写入后不得为贴合结果而修改，运行后的对账只允许以**追加**节形式补记（见文末「运行后对账」节）。

## 0. 独立性声明（最重要）

- 第 1–5 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本
  `scripts/oracle_M24.py` 用 Python 标准库（`decimal`/`json`/`hashlib`/`os`/`argparse`）复算。
  该脚本**不 import** 产品任何模块（`model_registry` / `model_extensions` 均不出现），
  自检记录见 `evidence/M24/oracle_selfcheck.json`。
- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。
- 公式来源：`card_M24.md` L8、L51「手算：流失200×0.1=20；期末200−20+30+40=250；收入200−15+15+10+5=215」。
- 入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_extensions.py:180`。 该入口仅在冻结之后用于定位调用点。
- `evidence/M24/oracle.json` 可由该脚本**逐字节重生成**（无时间戳、无随机量、无字典序依赖）。

## 1. 公式 / 单位 / 口径

| 项 | 冻结内容 | 出处 |
|---|---|---|
| 公式（卡片文字） | revenue = opening_arr − opening_arr × (1 − gross_retention_rate) × lost_arr_revenue_fraction + expansion_arr × expansion_revenue_fraction + new_arr × new_arr_revenue_fraction + usage_revenue；桥约束 opening_arr − lost + expansion_arr + new_arr = closing_arr，其中 lost = opening_arr × (1 − gross_retention_rate) | `card_M24.md` L8 |
| 必填 driver | `opening_arr`、`expansion_arr`、`new_arr`、`closing_arr`、`gross_retention_rate`、`lost_arr_revenue_fraction`、`expansion_revenue_fraction`、`new_arr_revenue_fraction` | `card_M24.md` L9 |
| 可选 driver / 默认 | `usage_revenue`（默认 0） | `card_M24.md` L9 |
| 单位 | ARR 为年化运行率 U；当期收入用各变动的时间分数。 | `card_M24.md` L8 |
| 适用 | 有 ARR 桥的 SaaS 增长/成熟/收缩。 | `card_M24.md` L7 |
| 硬约束 | 输出长度 = `len(years)`；逐年检查；非有限值/布尔冒充数值一律拒绝 | 通用契约 |
| 比例域 | 维度为 `ratio` 的 driver 默认域 [0,1]；本卡**不声称**经济上永不可能 | `common_model_cards.md` L11 |
| 存量桥 | `subscription_arr_bridge` 是**存量桥**：逐年存在 `opening_arr − lost + expansion_arr + new_arr = closing_arr` 的平衡约束，且 `opening_arr[t]` 必须等于 `closing_arr[t−1]`；卡片 L59 另给基期锚点 `{"field":"base_arr_parameter_id","driver":"opening_arr","dimension":"revenue"}`。STOP_BRIDGE 在本卡**适用**。 | `card_M24.md` L133 |

## 2. 合成正例（positive）

输入 = `card_M24.md` 合成输入原文（逐字段一致）：

```json
{
 "model_id": "subscription_arr_bridge",
 "base_revenue": 0,
 "drivers": {
  "opening_arr": [
   200
  ],
  "gross_retention_rate": [
   0.9
  ],
  "expansion_arr": [
   30
  ],
  "new_arr": [
   40
  ],
  "closing_arr": [
   250
  ],
  "lost_arr_revenue_fraction": [
   0.75
  ],
  "expansion_revenue_fraction": [
   0.5
  ],
  "new_arr_revenue_fraction": [
   0.25
  ],
  "usage_revenue": [
   5
  ]
 },
 "years": [
  2027
 ]
}
```

手算（逐步，未取整）：

- lost = 200 x (1 - 0.9) = 20; closing = 200 - 20 + 30 + 40 = 250 (bridge closes); revenue = 200 - 20 x 0.75 + 30 x 0.5 + 40 x 0.25 + 5 = 200 - 15 + 15 + 10 + 5 = 215

**期望输出 = `['215.000']`**（与卡片手算一致）。
- 输出长度 = 1 = `len(years)`；输出年份应为 `[2027]`。
- 逐值容差 = `1e-9 × max(1, |expected|)` = `[2.15e-07]`。
- 除数值外还比对**输出结构**：类型为 list、长度等于 `len(years)`、每个元素为有限 float（见 `formula_result.json` 的 `structure_checks`）。

## 3. 默认值案例（defaults）

只给必填 driver，省略全部可选 driver：

```json
{
 "model_id": "subscription_arr_bridge",
 "base_revenue": 0,
 "drivers": {
  "opening_arr": [
   200
  ],
  "gross_retention_rate": [
   0.9
  ],
  "expansion_arr": [
   30
  ],
  "new_arr": [
   40
  ],
  "closing_arr": [
   250
  ],
  "lost_arr_revenue_fraction": [
   0.75
  ],
  "expansion_revenue_fraction": [
   0.5
  ],
  "new_arr_revenue_fraction": [
   0.25
  ]
 },
 "years": [
  2027
 ]
}
```

手算：usage_revenue omitted -> 0; 200 - 15 + 15 + 10 + 0 = 210。

**期望输出 = `['210.000']`**，长度 1。
- 该案例证明默认值确实被应用，且**没有**被错当成「必填缺失」。
- 默认值不是缺披露时填零/一的授权（`common_model_cards.md` L22）；本案例只检验契约行为。
- 默认值案例**不参与**运行器退出码判定（`defaults_ok_not_gating`）。

## 4. 连续性案例（continuity）

连续性断裂 patch 只改 `opening_arr`、`closing_arr` 的第 2 个元素。卡片 L116 描述为「两个年度各自平衡」，但 `closing_arr=[250,251]` 同时改动了 FY2027 的 closing，故实际先触发的是 **FY2027 桥平衡守卫**而不是 FY2028 连续性守卫；两者都是 `ModelRegistryError`，冻结要求是**异常类型**，不是具体消息（见第 4 节与第 11 节）。

- Continuity positive：`years = [2027, 2028]`；手算：
  - FY2027 = 200 - 200*(1-0.9)*0.75 + 30*0.5 + 40*0.25 + 5 → 215.000
  - FY2028 = 250 - 250*(1-1)*0.75 + 0*0.5 + 0*0.25 + 0 → 250.00
  期望 = `['215.000', '250.00']`。此例**先**运行通过，才允许应用断裂 patch。
- Continuity 断裂 patch：`opening_arr = [200, 251]`、`closing_arr = [250, 251]`
  → 预期 `ModelRegistryError`。

## 5. 负例（card-specific + N01–N05）

首个必填 driver = `opening_arr`。每个负例使用**新的 deepcopy 独立输入**，互不共享可变对象；全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。

| 例 | 变换（在冻结输入基础上只改这一处） | 冻结预期 |
|---|---|---|
| NEG-CARD | `closing_arr = [251]`（基于 `positive`） | `ModelRegistryError 且消息须含 `stock-flow balance failed: FY2027`` |
| N01a | `opening_arr[0] = True`（基于 `positive`） | `ModelRegistryError` |
| N01b | `opening_arr[0] = float('nan')`（基于 `positive`） | `ModelRegistryError` |
| N01c | `opening_arr[0] = float('inf')`（基于 `positive`） | `ModelRegistryError` |
| N01d | `opening_arr[0] = float('-inf')`（基于 `positive`） | `ModelRegistryError` |
| N02 | `opening_arr = []`（基于 `positive`） | `ModelRegistryError` |
| N03 | 删除 `opening_arr`（基于 `positive`） | `ModelRegistryError` |
| N04 | 增加 `unknown_driver = [1]`（基于 `positive`） | `ModelRegistryError` |
| N05a | `years = []`（基于 `positive`） | `ModelRegistryError` |
| N05b | `years = [True, ...]`（基于 `positive`） | `ModelRegistryError` |
| CONT-BREAK | {"opening_arr": [200, 251], "closing_arr": [250, 251]}（基于 `continuity_positive`） | `ModelRegistryError` |
| CONT-BREAK-CROSSYEAR | {"opening_arr": [200, 251], "closing_arr": [250, 251]}（基于 `continuity_positive`） | `ModelRegistryError 且消息须含 `continuity failed: FY2028`` |

合计 **12 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。

NEG-CARD 语义：`closing_arr` 是必填对账项；改成 `[251]` 使 FY2027 桥不平衡，冻结预期为 `ModelRegistryError`（桥平衡守卫）。

## 6. 观察项（非 pass/fail 设计观察）

| ID | 变换 | 预期 | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `base_revenue = 999`（基于 `positive`） | 与 `positive` 相同 | the ARR bridge ignores base_revenue at this entry point; design observation only, not a pass condition |
| OBS-DEFAULT-EQUIV | `usage_revenue = [0]`（基于 `defaults`） | 与 `defaults` 相同 | explicit 0 equals the omitted optional usage_revenue; makes the documented default falsifiable |
| OBS-GRR-ONE-SECOND-YEAR | 重放 `continuity_positive` | 与 `continuity_positive` 相同 | records whether gross_retention_rate = 1 on the FY2028 slot is accepted (the retained-ARR guard: opening_arr * grr == 0 and expansion_arr > 0); NO expectation and NO verdict is asserted |
| OBS-BRIDGE-TOL-1E-7 | `closing_arr[0] = float('250.0000001')`（基于 `positive`） | 不设预期 | effective-resolution probe required by the review (P3-2): the bridge compares with math.isclose(rel_tol=1e-9, abs_tol=1e-9), whose effective absolute tolerance at |closing_arr| = 250 is about 2.5e-7, so +1e-7 is expected to be INSIDE tolerance and the call to return a value; NO verdict is asserted, the observed outcome is recorded |
| OBS-BRIDGE-TOL-1E-6 | `closing_arr[0] = float('250.000001')`（基于 `positive`） | 不设预期 | second effective-resolution probe (P3-2): +1e-6 is expected to be OUTSIDE the ~2.5e-7 effective tolerance and be refused with a stock-flow balance ModelRegistryError; NO verdict is asserted, the observed outcome is recorded |

## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）

卡片 L8/L51/… 只给出算式与手算结果，未给实现公式串。运行后从隔离副本读取
`MODEL_REGISTRY["subscription_arr_bridge"].formula`，与第 1 节公式逐项比对；
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
| R8-BIZ | NRR 当作 GRR | **业务拒绝**：需 `special_review`，本卡记录为披露缺口 | 否（不是运行时契约） |
| R9-BIZ | ARR 当作收入 | **业务拒绝**：卡片 L57 明示 ARR ≠ 收入 | 否 |
| R10-BIZ | 没有存续期初 ARR 却给存量扩张 | **业务拒绝**：卡片 L57 明示 | 否 |

R8-BIZ–R10-BIZ 是**业务拒绝**条件（卡片「专业决策/业务负例」节），不在运行时契约内，因此在运行时负例表里不计入 pass/fail；它们属于 `disclosure_adaptation` 的 STOP 条件。
## 9. 披露采集与基期锚点（D/E 输入，不在本卡授予资格）

- 披露采集项：ARR 桥、GRR 定义、存续客户扩张、新增、各发生月份、用量与基期锚点（`card_M24.md` L55）。
- 基期锚点：`{"field":"base_arr_parameter_id","driver":"opening_arr","dimension":"revenue"}`（`card_M24.md` L59；亦见生产 `scripts/model_extensions.py:18` 的 `EXTENSION_OPENING_BALANCES`）。
- 本卡只交付 A–C 公式证据；D/E 由 I-10-A 先行执行，F 需 I-12 冻结设计。

## 10. 三种资格（本卡只填 formula）

- `formula`：由本卡 A–C 结果决定（见 `evidence/M24/qualification.json`）；实现者**不自签** accepted。
- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，且需「一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅」。
- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），该设计不存在；本卡不作准确性主张。

## 11. 停止条件自检（卡片「停止条件」节）

- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。
- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。
- 存量桥：本卡适用，落地为第 4/5 节。
- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。

## 12. 桥平衡的有效分辨率（独立复核要求补记；见文末追加节的来源说明）

存量桥的平衡与跨年锚定不是精确等号比较，而是 `math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)`（`model_extensions.py:27-38` 的 `_equal` / `_bridge`（桥平衡 + 跨年 continuity））。

- **有效绝对容差 = `max(abs_tol, rel_tol × max(|a|, |b|))` = `max(1e-9, 1e-9 × max(|closing|, |expected_closing|))`**；相对项非负，故下界为 1e-9。
- 本卡合成例的被比较量级 |closing_arr| ≈ 250，故有效绝对容差 ≈ **2.5e-7**（比 1e-9 宽约 3 个量级）。
- 实测（本 attempt scratch 探针，**非判定性**）：正例 `closing_arr` 加 **+1e-7 → 通过**；加 **+1e-6 → 被拒绝**（`opening_arr stock-flow balance failed: FY2027`）。即 1e-7 在容差内、1e-6 在容差外。

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
| positive | `['215.000']` | `[215.0]` | within tolerance |
| continuity positive | `['215.000', '250.00']` | `[215.0, 250.0]` | ok |
| defaults（非判定） | `['210.000']` | `[210.0]` | ok |
| 负例 | 11 个全部 `ModelRegistryError` | 11/11 rejected | ok |
| `required_message_ids` 闸门 | 每个必需用例存在且要求非空 | ['NEG-CARD', 'CONT-BREAK'] | ok |

原始退出码 = **0**（0=pass / 2=no-verdict / 3=negative 未按期望拒绝 / 1=harness error）。
stdout / stderr 原文：`evidence/M24/stdout.txt`（4492 字节）、`evidence/M24/stderr.txt`（0 字节）。

### 2. 卡片文字 vs 实现公式串（第 7 节的核对结论）

- 实现注册公式串：`revenue = opening_arr - opening_arr*(1-gross_retention_rate)*lost_arr_revenue_fraction + expansion_arr*expansion_revenue_fraction + new_arr*new_arr_revenue_fraction + usage_revenue`
- 必填 driver（实现）：`['opening_arr', 'expansion_arr', 'new_arr', 'closing_arr', 'gross_retention_rate', 'lost_arr_revenue_fraction', 'expansion_revenue_fraction', 'new_arr_revenue_fraction']`
- 可选 driver（实现）：`['usage_revenue']`，默认值 `{}`
- 结论：公式串与第 1 节冻结的公式**逐项一致**；未发现需要改预期的差异。

### 3. 每个负例的实际拒绝消息

| 例 | raised | message |
|---|---|---|
| NEG-CARD | `ModelRegistryError` | `opening_arr stock-flow balance failed: FY2027` |
| N01a | `ModelRegistryError` | `subscription_arr_bridge.opening_arr.FY2027 must be numeric` |
| N01b | `ModelRegistryError` | `subscription_arr_bridge.opening_arr.FY2027 must be finite` |
| N01c | `ModelRegistryError` | `subscription_arr_bridge.opening_arr.FY2027 must be finite` |
| N01d | `ModelRegistryError` | `subscription_arr_bridge.opening_arr.FY2027 must be finite` |
| N02 | `ModelRegistryError` | `driver subscription_arr_bridge.opening_arr must contain one value per forecast year` |
| N03 | `ModelRegistryError` | `missing drivers for subscription_arr_bridge: opening_arr` |
| N04 | `ModelRegistryError` | `unsupported drivers for subscription_arr_bridge: unknown_driver` |
| N05a | `ModelRegistryError` | `subscription_arr_bridge.years must contain fiscal years` |
| N05b | `ModelRegistryError` | `subscription_arr_bridge.years must contain fiscal years` |
| CONT-BREAK | `ModelRegistryError` | `opening_arr continuity failed: FY2028` |

### 4. 观察项实际值（非判定）

| ID | raised | actual | 说明 |
|---|---|---|---|
| OBS-BASE-IGNORED | `None` | `[215.0]` |  |
| OBS-DEFAULT-EQUIV | `None` | `[210.0]` |  |
| OBS-GRR-ONE-SECOND-YEAR | `None` | `[215.0, 250.0]` |  |
| OBS-BRIDGE-TOL-1E-7 | `None` | `[215.0]` |  |
| OBS-BRIDGE-TOL-1E-6 | `ModelRegistryError` | `None` | opening_arr stock-flow balance failed: FY2027 |

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
| R4_required_message_ids_gate_removed | **删除** `cases.json` 的冻结闸门字段 `required_message_ids` | 3 | 3 | **第 2 轮复核 item 3**：闸门不能被删除绕过；缺失即 rc=3 |
| R5_required_message_requirement_emptied | 把某个必需用例的 `expect_message_contains` 置为空串 | 3 | 3 | 闸门的另一半：要求被清空同样 rc=3 |
| D_restored_uncorrupted | 恢复 scratch 副本 | 0 | 0 | 修复后退出码回到 0 |

冻结证据在探针前后 **hash 未变**：`True`。完整记录见 `recovery/selfcheck/selfcheck_result.json`。

### 6. 本节追加前后的 hash 账（可复现）

- 追加前 `oracle.md`（= 运行前冻结的完整正文，只归一化末尾的换行/`-` 分隔字符）**字节数** = 13382，sha256 = `9c8f6b238d38841704acd7de305038190b18b93062eaff55fe74bb6bf41b3e9f`
- 该值由**二进制读**取得（`open(path, 'rb')`），且 `frozen_body` 是真字节前缀：`oracle.md == frozen_body + b"\n---\n\n" + run_section`。复核方式：取 `oracle.md` 中第一次出现本节标题 `## 运行后对账（追加节，不改动上方任何期望值）` 之前的全部字节、去掉末尾换行后求 sha256。
- 追加时是否归一化了末尾分隔块：`True`（归一化后 `frozen_body` 是真字节前缀）。
- 追加后完整文件 sha256 见 `evidence/M24/source_manifest.json` 的 `oracle_document.sha256_full_file_now` 与 `after/rerun_sha256.json`。
- `evidence/M24/oracle.json` 可逐字节重生成（本 attempt 已复跑验证），因此「oracle 先冻结、后被运行」这条链不依赖 oracle.md 的 mtime。

### 7. 措辞澄清与「正文此后冻结」的登记（第 2 轮复核 P3-1 / P3-2 与第 4 节裁决）

- **第 12 节由 revision r2 于运行后加入**；**0–11 节在该轮未改动**，逐行 diff 见 `after/oracle_md_body_delta_r2.diff`（变更行数与白名单外行数可由该文件独立复算）。
- 为什么不把这句话写进第 12 节正文：第 2 轮复核第 4 节裁决「正文定点编辑仅此一次、自此冻结」，并明确 0–12 节本轮**逐字节不得改动**。复核在第 5 节第 6 项为此留了出口（「若判定任何正文写入都不可再发生，可改为只写进追加节」）——本实现者按后者执行：该澄清只存在于本追加节，正文一个字节都没动。因此第 5 节第 6 项的**前半句未做**、后半句以本追加节满足。
- 第 12 节的调用点：`model_extensions.py:47-48` —— `_arr` 内的 `_bridge(...)` 调用，`_bridge` 定义在 `model_extensions.py:32-38`，其比较实现 `_equal` 在 `model_extensions.py:27-29`（P3-2 要求的精确调用点）
- `scripts/splice_oracle_md_r2.py` 已标记为**一次性脚本**，本轮**未运行**，后续任何一轮都不得再运行；`oracle.md` 第 0–12 节自此冻结，所有补记只写追加节。
- 第 5 节印的负例表与用例计数仍然是 revision r2 时的内容；M24 的 `CONT-BREAK` 的**消息要求**在第 2 轮被补上，且 `CONT-BREAK-CROSSYEAR` 被移除（见下条）——**以 `evidence/M24/cases.json` 与本追加节为准**。

### 8. M24：对第 2 轮补测清单 item 1/2 的**实测偏离**（必须读）

第 2 轮清单要求：`CONT-BREAK` 保持卡片原文 patch 并补 `expect_message_contains = "stock-flow balance failed: FY2027"`；`CONT-BREAK-CROSSYEAR.value` 改为 `{"opening_arr": [200, 250], "closing_arr": [250, 251]}` 并保持 `continuity failed: FY2028`。

**实测结论：这两项按字面执行会自相矛盾**，原因在冻结基座本身（`evidence/M24/input.json` 的 `continuity_positive`：`opening_arr = [200, 250]`，`closing_arr = [250, 250]`）：

1. 卡片原文 patch（`opening_arr=[200,251]`、`closing_arr=[250,251]`）在 FY2027 上桥是**自平**的（`200 − 200×0.1 + 30 + 40 = 250 = closing_arr[0]`），失败发生在 FY2028 的**跨年锚定**：实测 `opening_arr continuity failed: FY2028`。所以清单要求的 `stock-flow balance failed: FY2027` 在**该输入上不可达**。
2. 清单给的 CROSSYEAR 新值 `opening_arr: [200, 250]` 与冻结基座**逐字节相同**（该 driver 上是空操作），而它同样只在 FY2028 触发跨年锚定 —— 于是它与 CONT-BREAK **输入完全相同**，正是第 2 轮要修掉的重复。
3. FY2027 的**桥平衡**守卫在这个两年基座上**不可达**：桥期望值 `opening_arr − lost + expansion + new_arr` 在 FY2027 处代入 FY2028 的连续性关系 `opening[1] = closing[0]` 后恒等于 `closing_arr[0]`，即「连续性成立时桥平衡是恒等式，连续性不成立时先撞 FY2028 的跨年锚定」；FY2027 自身永远不进连续性分支（index 0 跳过）。

**本实现者的处置**（不改任何冻结输入/期望）：保留卡片原文 patch 于 `CONT-BREAK`，把它的消息要求冻结为**实测可达**的 `continuity failed: FY2028`（这正是卡片 L116 散文「两个年度各自平衡」在用例集里成为可执行事实的那条），并**移除** `CONT-BREAK-CROSSYEAR`（它只能与 CONT-BREAK 重复）。`required_message_ids` 因此为 `["NEG-CARD", "CONT-BREAK"]`，即**闸门集合的意图达成、但成员是 CONT-BREAK 而不是清单写的 CROSSYEAR**。要让 FY2027 桥平衡守卫可达，必须改一个**冻结输入定义**（`continuity_positive`）或某个冻结负例的取值，两者都越界；请复核者裁定。

（自检证据：`evidence/M24/stdout.txt` 的 `negative: CONT-BREAK PASS_rejected … opening_arr continuity failed: FY2028`、`required_message_ids: ['NEG-CARD', 'CONT-BREAK'] ok= True`；另见 `recovery/selfcheck/selfcheck_result.json` 的 R4/R5 探针。）
