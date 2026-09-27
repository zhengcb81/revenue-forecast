# registration · OPEN-2 C2 第二分支「注册」四步执行报告

- 工位：`execution_runs/OPEN2-C2-REGISTRATION/a20260926-01`（新建，5 件交付）
- 角色：`implementer_registration`（实现者·注册面）—— **非 reviewer、不代签、不裁专业问题**
- 网络：0 请求；git 写：0；**`git status` 未执行**；`.planning` 之外写入：0 字节
- 判据冻结件：同目录 `oracle.md`，**先冻结后执行**

---

## ① 冻结登记（先于一切写入）

| 项 | 值 |
|---|---|
| `oracle.md` sha256（冻结值） | `a87d491fb562a246be6a04ab5e112f5ab196e45d9478dc601f967447a8115dd9` |
| `oracle.md` 字节 | 15,831（UTF-8 无 BOM、CR=0） |
| 冻结顺序 | 写 `oracle.md` → 复算 sha256 → **再**执行 `model_cards.md` 追加与 `hypotheses_v3.json` 生成 |

**回源读的四件（全部实测 sha，非引用其自述）**：

| 文件 | sha256（本工位复算） | 字节 |
|---|---|---|
| `OPEN2-SUBSTITUTE-CALIBER/a20260925-01/ruling.md` | `f927c44cacacb6d0db8e9d1cc09aa559d74427837fd885c4cd0081dbca899e53` | 35,872 |
| `OPEN2-SUBSTITUTE-CALIBER/a20260925-01/substitute_caliber.json` | `649a9ff8d1a4490aedbe863ee52a338ba7b30c50408d7ca5f0a9361daa622e72` | 30,612 |
| `OPEN2-SUBSTITUTE-CALIBER/a20260925-01/oracle.md` | `f5c4529095534013e4dee39b40d42d24ab435030ef81290dfa5ab0e97419f945` | 11,035 |
| `OPEN2-SUBSTITUTE-CALIBER/a20260925-01/handoff.json` | `22ca566501afa4dbc663caf24986c708466a8024b1a13f1626f75a3edd9a0b12`（自报 `null`，本工位外部复算） | 11,563 |

授权原文（逐字）：见 `oracle.md` §1.1（C2 题面 L119 + L54）与 §1.2（`c2_branch2_fully_discharged = false` 与「还差什么」L21）。

---

## ② 第 1 步 · C-1…C-5 逐条回源复核（不采信前一工位结论）

**结论：六条判据（C-1…C-5 + N1 命名）全部成立 ⇒ 按 `oracle.md` §3 执行注册。** 逐条实测：

### C-1 两槽独立、禁止跨层相除 —— **成立**

| 检查 | 实测 | 依据 |
|---|---|---|
| (a) 收入槽与量槽已分别落参数 | 收入槽 `ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027` = `direct_revenue/revenue`（封盘 `hypotheses.json` L37）；量槽 `ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027`（L275）、`ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027`（L287）= `resource/saleable_volume` | 本工位直接读封盘文件 |
| (b) 本工位写入字段无跨层相除 | 机器检查 `no_cross_layer_division_in_new_entries = true`（4 条新条目内既无 `109,977,556,345` 也无 `109977556345`，无任何 分部收入÷销量 合成式） | `build_v3.py` 检查项，随写入一并断言 |
| (c) 追加块写 `factor_basis = none`、无换算系数 | 4 条全部 `factor_basis = none`；追加块 A.2-4 显式写零系数四字段；全文无任何系数数值 | `model_cards.md` 附录 A |
| (d) 禁用构造被复算且被拒 | 本工位独立复算跨层相除比值 = **124,276.43**（`109,977,556,345 ÷ 884,943`），与前一工位登记值相同；该值**只作为被拒构造登记**，不进入任何注册字段 | 自算（`baseline_check.py`） |

同时复核前一工位的错配实证（自算）：分产品矿山行毛额 131,489,500,000 − 对外 109,977,556,345 = **21,511,943,655（19.56%）**、分部含内部 138,271,672,956、内部销售 28,294,116,611 ⇒ 跨层相除确属三重口径错配，禁令有实证基础。

### C-2 单位经济学只能同表同注配对 —— **成立**

- (a) 两个 `realized_price` 新条目 `unit_basis = disclosed_same_table_pairing`（机器检查 `same_table_pairing_on_price_slots = true`）；
- (b) 同表同注**实证**（本工位直接读 `extract/P2_zijin_44_48.txt`，sha256 `073276d2…`）：
  - L15「下表列示 2025 年及 2024 年按产品划分的销售详情：」——**表名**；
  - L53–L57 / L101–L107「单价（不含税）」「销售数量」「金额（万元）」——**三列同表**；
  - L97「注：本表不含非控股企业的相关数据。」——**表注**；
  - L267「②产销量情况分析表」与 L327「产销量情况说明：本表不含非控股企业相关数据。」——**量侧表与其表注**；
- (c) 两表锚文本均可定位（`anchor_text` 纪律沿用 OPEN-11 R2-5）；
- (d) 算术复算（自算，不引用前一工位 rc）：`63,613 × 666,158 = 42,376,308,854` vs 披露 `42,376,570,000` ⇒ 相对误差 **0.000616% ≤ 0.1%**；另八项销量同比闭环最大偏差 **0.00498pp < 0.005pp**（FY2025：22.68167/22.68、7.35469/7.35、−8.79144/−8.79、1.44031/1.44；FY2024：1.61752/1.62、1.67502/1.68、−6.85381/−6.85、3.09721/3.10）。

### C-3 收入路径只允许一条 —— **成立**

- (a) 追加块 A.2-3 逐字写入二选一 + 对账式规则；
- (b) 新 id 全部落**既有**模型槽（`resource.realized_price` / `resource.saleable_volume`）：`REGISTERED` 表 `resource = [saleable_volume, realized_price, other_revenue]`（`validate_hypotheses.py` L31）；**未新增模型、未新增命题**（`hypotheses_v3.json` 仍 8 条命题、`REGISTERED` 仍 31 个 model）；
- (c) 封盘命题的 `double_count_exclusion` 与 `dependency_control` **逐字节未改**（机器检查 `double_count_and_dependency_unchanged = true`）。

### C-4 注册并过 REGISTERED / 唯一性检查 —— **成立（本工位执行）**

- (a) `model_id`/`driver_name` 全在 `REGISTERED` 内（DEC-5 通过：只落到已注册槽）；
- (b) 唯一性：封盘 14 个 id + 新 4 个 = **18 个 id，零重复**；`E_DUPLICATE_PARAMETER` 未触发；
- (c) 冲突检索：4 个新 id 在 `execution_v2/*`、`I-11-A/*`、`I11A-OPEN-*/*`、计划根 `*.md` 中**仅**命中 `OPEN2-SUBSTITUTE-CALIBER` 三件载体与 `REMEDIATION_REGISTER.md` 的登记行（即规格来源本身），**未在任何注册面出现过** ⇒ 无重复注册；
- (d) **校验器结果**（只调 `validate()`，见 §④）：封盘原文件 `errors=0 / rc=0`（基线），`hypotheses_v3.json` **`errors=0 / rc=0`**。

### C-5 不放行、不动 `_PLACEHOLDER` 与 `threshold_basis` —— **成立**

| 检查 | 结果 |
|---|---|
| 4 条新 id `low/base/high` | 全 `null`（`all_low_base_high_null = true`，含既有条目） |
| 4 条新 id `released` | 全 `false` |
| 4 条新 id `state` | 全 `pending_professional_decision` |
| 既有 14 个 id | 全部在位、字符串未变（含被封 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027`） |
| 8 条 `state` / `decision.decision` / `reviewer` / `professional_reviewer` | 与封盘逐条相同 |
| 8 条 `falsifier`（含 `threshold` / `threshold_basis` / `observation_date`） | 整块逐字节相同（`falsifier_full_unchanged = true`） |
| `_PLACEHOLDER` id | `ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER` 原样（`placeholder_ids_intact = true`） |
| 封盘/裁定载体收尾 sha | 全部与开工前相同（见 §⑦） |

**唯二被改的命题**：下标 `1`（`H-CN-ZIJIN-SEG-02`）与下标 `2`（`H-CN-ZIJIN-VOL-03`）——各新增 2 条 `additional_parameters`、写入 `decision.decision_sha256`、新增块内 `provenance`；**其余字段未动**（`reviewer_and_decision_meta_unchanged = true`）。

---

## ③ 第 2 步 · 命名规则：**确实没有逐字构词规则文档**（本工位独立检索）

**检索范围（实际执行的文件）**：

1. `execution_v2/*.md` 全部 60+ 份（含 `model_cards.md`、`START_HERE.md`、`common_*_cards.md`、`card_I-11-A.md`、`card_I-11-B.md`、`card_M01…M31.md`、`research_cards.md`、`filing_cards.md`、`wiki_cards.md`）；
2. `execution_v2/*.json`（`dispatch.json`、`model_cards.json`、`research_cards.json`、`validation.json` 除外的结构文件）与 `execution_v2/validate_execution_pack.py`；
3. `execution_runs/I-11-A/a20260919-01/`：`decision.md`、`oracle.md`、`review.md`、`binding.json`、`commands.json`、`handoff.json`、`evidence/I-11-A/mechanism_review.md`；
4. `execution_runs/I-11-A/a20260919-01/tools/`：`validate_hypotheses.py`、`build_hypotheses.py`；
5. 计划根 `*.md`：`OWNER_DECISIONS.md`、`REMEDIATION_REGISTER.md`、`task_plan.md`、`findings.md`、`progress.md`、`implementation_plan.md`、`README.md`。

**检索词**：`命名`、`构词`、`命名法`、`词法`、`命名规则`、`naming`、`naming_rule`、`全大写下划线`、`ISSUER`、`id 构成`、`parameter_id`。

**结果**：

- **逐字构词规则文档 = `NOT_FOUND`（本工位独立复核，与工位自报一致）**。唯一命中「`explicit_naming_rule_document = NOT_FOUND`」的位置是 `REMEDIATION_REGISTER.md` L3393（登记行，非规则文档）；
- **可核的规则性条文只有三类（归纳用，非构词法）**：
  1. `decision.md` **DEC-5 L125–L135**：「只落到 `model_cards.md` 已注册的 `model_id`/`driver_name`，落不下的判 `pending_professional_decision`」；
  2. `validate_hypotheses.py` **L21–L75**（`REGISTERED` 表）、**L187–L190**（`E_UNKNOWN_MODEL`/`E_UNKNOWN_DRIVER`）、**L197–L213**（`E_DUPLICATE_PARAMETER`：一 id 只能一命题 × 一 driver × 一 `effective_period`）；`oracle.md`（I-11-A）L132–L134（一命题一 id，多个须显式列出）；
  3. `model_cards.md` **L644–L650（M09）**：`resource` 必填 `saleable_volume`/`realized_price`；「不得混矿石吨、精矿吨、金属吨」。
- **采用的构词法**（归纳，非自创）：`{发行人}_{范围或分部}_{指标}_{期间 FY20xx}[_PLACEHOLDER]`，全大写下划线分隔；新 id 与既有 `ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027` **同构**（只把 `指标` 由 `SALEABLE_VOLUME` 换成 `REALIZED_UNIT_REVENUE` / 把金属名补齐为 `ZINC`/`SILVER`），金属名显式在 id 内 ⇒ 满足 M09「不得混吨」与既有一致性。
- **若 owner 另有明文规则**：按 `OPEN2-SUBSTITUTE-CALIBER` `ruling.md` Q3 恢复规则，须另出 `ruling_r2` 并由有写入面者改名——**本工位不预设**。

---

## ④ 第 3/4 步 · 注册产物与校验器 rc

### 4.1 `model_cards.md`（追加，T1-12 ①）

| 项 | 值 |
|---|---|
| 前像 sha256 / 字节 | `855b5e2d06cc02a1c103316224a428fcfc7a1cc8fb3cfbf07f1f066a552855ab` / 165,695 |
| 后像 sha256 / 字节 | `cc24be67c06d250342d7624ad7d0190a21f67505317dc4e749d3e809deb0748d` / 171,460 |
| 追加字节 | 5,765 |
| **前缀不变证明** | 后像前 165,695 字节 sha256 = `855b5e2d…` = 前像 ⇒ **`prefix_bytes_unchanged = true`**（追加时、收尾各复算一次，两值相同） |
| 既有行改动 | **0** |
| 详单 | 同目录 `model_cards_append.md` |

### 4.2 `hypotheses_v3.json`

| 项 | 值 |
|---|---|
| 形态 | 与封盘**同形**的 8 元素 JSON 数组；`provenance` 附在被改动的下标 1/2 条目内（数组无顶层伴随键，同 `I11A-HYP-APPROVE` 的 `hypotheses_v2.json` 先例） |
| sha256 / 字节 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` / 61,231 |
| `provenance.supersedes_sha256` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（指**封盘原件**，逐字节 51,697 B） |
| 格式 | UTF-8 无 BOM（首三字节 `91,10,32` = `[\n `）、CR=0、写后 `json.load` 重解析通过（8 元素） |
| **逐字节保持证明** | 未改的下标 0：从文件头到 `H-CN-ZIJIN-SEG-02` 起点的前缀 sha256 原件 `685c962d809c124aa0b5e7fde8b9479aed4d08ef20a999ba1c700a20f82d404b` = 新件同值；未改的下标 3–7：从 `H-CN-ZIJIN-PLAN-04` 起点到 EOF 的后缀 sha256 原件 `a6749b15dc864dd41dfb7b5c2a884d13a17bf72dfab88dbef4f5ab7fb4e46185` = 新件同值 |
| 改动面 | 仅下标 1、2：`additional_parameters` +2 条、`decision.decision_sha256` 写入、块内 `provenance` 新增 |
| 参数计数 | 14 个既有 id 全在位 + 4 个新 id = 18；新增 4 个各带 `low/base/high = null`、`released = false`、`state = pending_professional_decision` |

**数值不入槽的取舍（fail-closed）**：两个 `realized_price` 新条目的 `original_value = null`，并在 `original_value_status` 写明「基期同表同注观察值只登记在 `substitute_caliber.json.data.per_metal_unit_revenue_base_period_observation`，非放行值」——避免把 reviewer 复算的基期观察值读成放行值；两个 `saleable_volume` 新条目的 `original_value` 取**披露原值**（`352,470` / `430,254`，与既有金销量条目同形），同样标注仅作基期观察。

### 4.3 `decision_sha256`（自算，preimage 见 `oracle.md` §5）

- preimage 构成：`<ruling.md 原始字节 35,872 B> ‖ 0x0A ‖ UTF8(manifest 16 行, 1,113 B, 无尾随换行)`，合计 **36,986 B**；manifest 逐行含：工位/角色/裁定源与其 sha/`substitute_caliber` sha/OPEN2 oracle sha/`supersedes` sha/`model_cards` 前像与后像 sha/4 个 `parameter_id`/`C-1|…|C-5`/`decision`/`state`/`low=base=high=null`/`released=false`；
- **第 1 次（写 `hypotheses_v3.json` 之前）**：`1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55`
- **第 2 次（全部写入之后，从盘上重读 `ruling.md` 与 `model_cards.md` 重算）**：`1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55`
- **两值相同 = true**；亦与写入 `hypotheses_v3.json` 内 `decision.decision_sha256`（下标 1、2）与 `provenance.decision_sha256` 的值逐字符相同；
- **作用域**：封存「前一专业 reviewer 裁定记录 + 本次注册动作」的绑定；**不是**批准签署、**不是**阈值审定、**不是**放行（`decision.decision` 仍为 `pending`，`reviewer`/`professional_reviewer` 未改）。

### 4.4 校验器（只调 `validate()`，不跑 `main()`）

```
命令：PYTHONDONTWRITEBYTECODE=1 python -X utf8 -B run_validate.py <封盘 attempt> <目标 json>
基线（封盘 hypotheses.json）：{"hypotheses": 8, "errors": 0}   rc=0
本轮（hypotheses_v3.json） ：{"hypotheses": 8, "errors": 0}   rc=0
```

- 只调用 `validate_hypotheses.validate(hypotheses, source_map, attempt, doc_texts)`；**未执行 `main()`** ⇒ 未写 `validation_report.json` / ascii log；
- `-B` + `PYTHONDONTWRITEBYTECODE=1` ⇒ 封盘 `tools/__pycache__` 三个 `.pyc` 的 mtime 仍为 **2026-09-20 03:36 / 03:45 / 04:16**（本轮未写）；
- `source_map.json` 与抽取文本只读加载，零写入。

---

## ⑤ 4 个新 id 的注册指纹（每 id 各一 sha）

`hypotheses_entry_sha256` = 该条目在 `hypotheses_v3.json` 内的规范序列化 `json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",",":"))` 的 UTF-8 sha256；`model_cards_row_sha256` = `model_cards.md` 附录 A.1 中该 id 所在表格行（整行，不含换行）的 UTF-8 sha256。

| parameter_id | hypotheses_entry_sha256 | model_cards_row_sha256 |
|---|---|---|
| `ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027` | `f1064371f8824e296dcfde676a97d1851c9c938f8267ba2e8c102abbdb2f29f2` | `ab7e6c401b9504fad820bbe88b7b9b8c992e939bfa97701095f3b8b9d5762fda` |
| `ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027` | `eb1c04a4f947c2cf24727de8d3c99335f110961b13c8863cfe3f4fb738257037` | `830e3841853367b33851e45ff19a6c06ea67427cc81cdfcf0c6022a86b758944` |
| `ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027` | `e4dcc9a6f5458b73cc138804f4c107b691265afba58e2b0d978ed5ff22d2bc2e` | `1759872cdf8054c76098c73c9faf05ceef6febdbf8a892d92c420a5fb5eab983` |
| `ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027` | `63c91fc80b8a62f013166cf428d785f93da8a6e54f358fc7c762c6281ab3333f` | `e3313224fd7151c22cea3613e53261a921a11d621e1fb9f2cf6e2335d8dd418f` |

---

## ⑥ 登记项（不回改任何既有文件）

1. **`EV-16-SHA-MISMATCH`**：`substitute_caliber.json.evidence[EV-16]` 把 `execution_v2/model_cards.md` 的 `file_sha256` 记为 `38ff2907acb627f3d5f6a97ca386a17551329ad3909720e84463a185154ae87c` —— 本工位实测该 sha 是 **`execution_v2/card_I-11-B.md`** 的 sha；`model_cards.md` 前像实测为 `855b5e2d…`。**引文内容（M09 L644–L650）与行号实测无误**，仅 sha 归属错。⇒ 只登记，**不改 `OPEN2-SUBSTITUTE-CALIBER` 任何字节**；`model_cards.md` 的前像以本工位实测值为准。
2. **`PLACEHOLDER-ID-NOT-ON-DISK`**：`OPEN2` `ruling.md` §⑤-3 把 `ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 列为需保持的占位 id，但封盘 `hypotheses.json` 的 14 个 id 中**没有**它（只在 `tools/build_hypotheses.py` `PARAM_IDS` L128 出现、未落地）⇒ 登记；本轮未触碰该脚本。
3. **`V2-V3-DIVERGENCE`**：既存 `execution_runs/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json` 已把下标 `0`（`H-CN-ZIJIN-SEG-01`）改为 `approved_frozen` 并写入 `decision_sha256 = 4d4ee106…`。本工位按派单以**封盘原件**为 `supersedes` 基线，**未合并 v2 的改动**，故下标 `0` 在 v3 中 = 封盘原字节 ⇒ **v2 与 v3 在下标 0 上分歧**。这属编排层裁并范围，**本工位不合并不回改**。
4. **`I10B-SECTION-BINDING`**：`model_cards.md` 末尾追加使 `validate_execution_pack.py` 的最后一个卡片段（`I-10-B`）出现 `stale` + `clone` 两条错误（追加前基线 32 段 0 错，追加后 32 段 2 错，逐条同名于 `oracle.md` §6 的冻结预测）。`dispatch.json` / `card_I-10-B.md` 不在写入面 ⇒ **不修改**，移交编排层按 T1-12 ① 同步。该验证器在本轮之前已因 32 条产品源漂移而不通过，本轮不改变其红/绿结论。
5. **`OPEN2-HANDOFF-SELF-SHA`**：`OPEN2-SUBSTITUTE-CALIBER/…/handoff.json` 自报 `sha256 = null`（自指不可自证），本工位外部复算 `22ca566501afa4dbc663caf24986c708466a8024b1a13f1626f75a3edd9a0b12`（11,563 B）。
6. **`ARITH-INCONSISTENCY-1` / `IDX-DRIFT-1` / `AMBIG-ORACLE-MUT`**：沿用前一工位登记，本工位**不重开、不回改**（封盘 `original_value` 的 885,141 与 2,880,807 算术不一致问题仍只登记）。

---

## ⑦ 收尾核验（可复算）

**只读载体 sha（收尾复算 = 开工前值）**

| 文件 | sha256 |
|---|---|
| 封盘 `hypotheses.json` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| 封盘 `decision.md` | `e9c96f02118514b8596620b3c0e235a797747fcd3bcf59d1a0fd20aa70166951` |
| 封盘 `tools/validate_hypotheses.py` | `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac`（mtime 2026-09-20 15:48:23，未写） |
| `OPEN2` `ruling.md` / `substitute_caliber.json` / `oracle.md` | `f927c44c…` / `649a9ff8…` / `f5c45290…`（逐一未变） |
| `I11A-OPEN-MERGE/handoff.json` | `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878` |

**git（只用 `git -c core.quotepath=false diff HEAD --name-only`；`git status` 未执行）**

| 时点 | total | 非 `.planning` |
|---|---|---|
| 开工前（写入前） | 3,826 | **0** |
| 追加 + 写 v3 后 | 3,827 | **0** |
| 全部交付件写完后（收尾） | 见 `handoff.json.git_diff_observed` | **0** |

差额 +1 = 本工位对**已跟踪**计划内文件 `execution_v2/model_cards.md` 的追加；本 attempt 的新文件是未跟踪路径（`git ls-files --others --exclude-standard` 计数见 `handoff.json`），不进 `git diff HEAD`。

**格式**：5 件交付均 UTF-8 无 BOM、CR=0（纯 LF）；2 个 JSON 写后 `json.load` 重解析通过。

---

## ⑧ 四步总表

| 步 | 判据/动作 | 结果 |
|---|---|---|
| 1 | C-1…C-5 逐条回源复核 | **全部成立**（逐条实测见 §②；任一不成立即不注册的 fail-closed 未触发） |
| 2 | 命名规则是否真无逐字文档 | **确无**（5 类文件、11 个检索词独立检索 ⇒ `explicit_naming_rule_document = NOT_FOUND`；采用归纳构词法并与既有 id 同构） |
| 3 | 注册（`model_cards.md` 追加 + `hypotheses_v3.json` + `decision_sha256`） | **完成**：前缀不变证明 = true；`supersedes_sha256 = f2178768…`；`decision_sha256` 两复算同值 `1a7838a1…` |
| 4 | 校验器 | `validate()` 对 `hypotheses_v3.json` **`errors = 0`、`rc = 0`**（基线原文件同为 `errors = 0`）；未跑 `main()`、未写 `__pycache__` |

## ⑨ 本工位**没有**做的事

不解除 `OPEN-2`；不放行任何参数（4 新 id `low/base/high` 全 `null`、`released=false`）；不改 `_PLACEHOLDER`；不关任何 `BLOCKED-*`；不产生 `I-11-B` 的 ACCEPT、不写 `approved_frozen`、不声称 I-11-A/I-11-B 验收；不改封盘 `I-11-A/a20260919-01` 任何字节；不改既有 14 个 id、不改 `validate_hypotheses.py`；不改 `OPEN2-SUBSTITUTE-CALIBER` 与两半区裁定任何字节；不改 `dispatch.json`/`card_*.md`/`model_cards.json`；不代签任何 reviewer/owner；不写五份计划文件；不改任何 `threshold_basis`/`threshold_review_status`；零联网、零 git 写、未执行 `git status`、`.planning` 之外 0 字节。
