# oracle · OPEN-2 C2 第二分支「注册」判据（先冻结，后执行）

- 工位：`execution_runs/OPEN2-C2-REGISTRATION/a20260926-01`（新建）
- 角色：`implementer_registration`（实现者·注册面；**非 reviewer、不代签、不裁专业问题**）
- 被执行动作：C2 第二分支的**最后一步「注册」**——`model_cards.md` 追加 4 个新 `parameter_id` + `hypotheses` 新版本 + `decision_sha256`
- 本文件是**判据冻结件**：写入后立即算 sha256 并记入同目录 `registration.md` §①，**之后**才允许执行 §4 的写入；执行期间不回改本正文，任何更正只能追加 `oracle_r2.md`
- 冻结时点：本文件写入时（执行前）
- 网络：0 请求；git 写：0；**`git status` 不执行**（收尾只用 `git -c core.quotepath=false diff HEAD --name-only`）

---

## 1. 授权链（逐字，回源）

### 1.1 C2 题面（原文）

`execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` **L119**（该文件 sha256 `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878`，21,808 B，本工位复算）：

> `OPEN-2：系数取值解 BLOCKED（S1/A 级证据 + 双签）或落实『分部对外收入 + 分金属销量』替代口径并注册新 parameter_id`

同文件 **L54**：

> `走替代口径则新 parameter_id 须在 model_cards.md 注册并通过 REGISTERED 检查`

### 1.2 前一工位的未竟项（原文）

`execution_runs/OPEN2-SUBSTITUTE-CALIBER/a20260925-01/handoff.json`（该文件 sha256 由本工位在 §7 冻结前实测，值登记于 `registration.md` §①）：

- L21 `c2_branch2_remaining_work`：
  > `model_cards.md 新增 parameter_id 注册 + hypotheses.json 新版本 + decision.decision_sha256（均属实现者/编排层写入面，本工位无该权限）⇒ OPEN-2 与 I-11-B 维持 BLOCKED`
- L20 `c2_branch2_fully_discharged`：`false`
- 同目录 `ruling.md` §⑤ 第 1 条：`『注册』（model_cards.md 新增 + hypotheses.json 新版本 + decision.decision_sha256）属实现者/编排层，本工位无该写入面 ⇒ c2_branch2_fully_discharged = false`

### 1.3 前一工位的裁定（本工位**只回源核验、不重裁**）

`OPEN2-SUBSTITUTE-CALIBER/a20260925-01/ruling.md` sha256 `f927c44cacacb6d0db8e9d1cc09aa559d74427837fd885c4cd0081dbca899e53`（35,872 B）· `substitute_caliber.json` sha256 `649a9ff8d1a4490aedbe863ee52a338ba7b30c50408d7ca5f0a9361daa622e72`（30,612 B）· `oracle.md` sha256 `f5c4529095534013e4dee39b40d42d24ab435030ef81290dfa5ab0e97419f945`（11,035 B）—— 三值均由本工位在冻结前复算，与该工位 `handoff.json.written_files` 登记值逐一相同。

---

## 2. 本轮只判什么、不判什么

**判（四步，逐条判据见 §3）**：

1. **C-1…C-5 逐条回源复核**（不采信前一工位结论；任一不成立 ⇒ **不注册**、判 `blocked` 并给实测依据）；
2. **命名规则**：自行检索是否存在「逐字构词规则文档」，找到即以其为准，未找到才沿用归纳规则；
3. **注册**：`model_cards.md` 追加 4 个 id（前像/后像 sha + 前缀不变证明）＋ `hypotheses_v3.json`（同形、只动注册相关条目）＋ `decision_sha256`（preimage 冻结于 §5，写入前后各复算一次且两值必须相同）；
4. **校验器**：`tools/validate_hypotheses.py` 的 `validate()` 对新版本 `errors = 0`（只调 `validate()`，不跑 `main()`，不写 `__pycache__` 到封盘）。

**不判 / 明确不做（行不交界）**：

1. **不解除 `OPEN-2`**（注册完成与否、OPEN-2 是否解 BLOCKED 是两件事，均不由本文件宣布）；
2. **不放行任何参数**：4 个新 id 的 `low/base/high` 一律 `null`、`released=false`、`state=pending_professional_decision`；不给任何幅度、单价、阈值数值作为放行值；
3. **不改 `_PLACEHOLDER`**：`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER` 与被封参数 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的落点、`falsifier.threshold_basis` 一个字节不动；
4. **不关任何 `BLOCKED-*`**（ACCT `BLOCKED-2a/2b/3a/3b/6a/6b/6c`；IND `BLOCKED-1…7`）；
5. **不产生 `I-11-B` 的 ACCEPT**、不写 `approved_frozen`、不声称 I-11-A/I-11-B 验收；
6. **不改封盘 `I-11-A/a20260919-01` 任何字节**（含 `hypotheses.json`、`decision.md`、`tools/*.py`；新命题版本只写本 attempt 目录）；
7. **不改既有 14 个 `parameter_id`**、**不改 `validate_hypotheses.py`**；
8. **不代签**任何 reviewer/owner；**不写五份计划文件**；**不改 `OPEN2-SUBSTITUTE-CALIBER` 的任何字节**；
9. **不联网、零 git 写、不执行 `git status`、不写 `.planning` 之外任何路径**（含 `company-wiki`）。

**写入面（恰 6 个文件）**：

- ① 本 attempt 目录 5 件：`oracle.md`（本文件，先冻结）、`hypotheses_v3.json`、`model_cards_append.md`、`registration.md`、`handoff.json`
- ② `execution_v2/model_cards.md` —— **只允许在文件末尾追加新 id 条目**；既有行一字不动（前像 sha 先记、追加后证明**前缀字节不变**，本计划 T1-12 ① 形态）

---

## 3. 判据（STRICT，冻结）

记 `REG_OK = C1 ∧ C2 ∧ C3 ∧ C4 ∧ C5 ∧ N1`。**六条全部成立才执行注册；任一不成立即 fail-closed 判 `blocked`（不注册），并把实测依据写进 `registration.md`。**

### C-1 两槽独立：收入侧与量侧分别落参数，禁止跨层相除（源：oracle P3）

必须**同时**满足：

- (a) 收入槽与量槽在封盘 `hypotheses.json` 中**已分别落参数**（收入槽 `ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027` = `direct_revenue/revenue`；量槽 `ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027`、`ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027` = `resource/saleable_volume`）；
- (b) 本工位**写入的每一个字段**不得出现跨层相除：任何新条目的 `original_value` / `conversion_formula` / 说明文本中不得出现 `分部对外收入 ÷ 分金属销量`（或任何 分部收入÷销量 形态）的合成式；
- (c) `model_cards.md` 追加块必须显式写 `factor_basis = none`、不得出现「铜当量」折算系数；
- (d) 复核前一工位对该禁令的实证：`109,977,556,345 ÷ 884,943` 的比值（禁用构造）**不进入**任何注册字段（本工位自行复算该比值，仅用于证明「知道它、且拒绝它」）。

### C-2 单位经济学若给，只能同表同注配对（源：oracle P4）

- (a) 追加块中单位经济学 id 的 `unit_basis = disclosed_same_table_pairing`；
- (b) 同表同注**实证**（本工位自己读 `extract/P2_zijin_44_48.txt`）：`按产品划分的销售详情` 表同表披露 `单价（不含税）/ 销售数量 / 金额（万元）` 三列，且该表表注为「本表不含非控股企业的相关数据。」；`②产销量情况分析表` 表注为「本表不含非控股企业相关数据。」；
- (c) 量侧取数表的锚文本 `②产销量情况分析表` 与 `按产品划分的销售详情` 各自可定位；
- (d) 同表同注配对的算术复算：`单价 × 销售数量 ≈ 金额` 相对误差 ≤ 0.1%（本工位独立复算，不引用前一工位 rc）。

### C-3 收入路径只允许一条进入模型，另一侧只作对账（源：oracle P5）

- (a) 追加块必须逐字写入单收入路径规则（`direct_revenue` 与 `resource` 二选一进收入路径、另一侧只作对账；价格变化不得再作额外收入叠加；同一笔销量不得重复计入）；
- (b) 新增 id 全部落在**既有**模型槽（`resource.realized_price` / `resource.saleable_volume`），**不新增模型、不新增命题**，因而不产生第二条收入路径；
- (c) 封盘命题既有的 `double_count_exclusion` / `dependency_control` **一字不改**。

### C-4 新 `parameter_id` 在 `model_cards.md` 注册并通过 REGISTERED / 唯一性检查

- (a) `model_id`/`driver_name` 必须在 `tools/validate_hypotheses.py` 的 `REGISTERED` 表内（`resource` → `saleable_volume` / `realized_price` / `other_revenue`；L21–L75、L187–L190）；
- (b) 与既有 **14** 个 `parameter_id` **零冲突**（唯一性：L197–L213 `E_DUPLICATE_PARAMETER`；一个 id 只能一命题 × 一 driver × 一 `effective_period`）；
- (c) 4 个新 id 落点符合 `decision.md` **DEC-5 L125–L135**「只落到 `model_cards.md` 已注册的 model_id/driver_name，落不下的判 pending」；
- (d) 追加后 `validate()` 对 `hypotheses_v3.json` 返回 **`errors = 0`**（并以封盘原文件 `errors = 0` 作基线对照，证明同一 harness 同为绿）。

### C-5 不放行：`low/base/high` 保持 `null`；被封参数的 `_PLACEHOLDER` 与 `threshold_basis` 一律不动

- (a) 追加块 4 条：`low = base = high = null`、`released = false`、`state = pending_professional_decision`、`threshold_basis_touched = false`、`placeholder_suffix_removed = false`；
- (b) `hypotheses_v3.json`：既有 **14** 个 id 全部在位且字符串不变；8 条 `state` 不变；8 条 `falsifier.threshold_basis` 与封盘基线逐条相同；8 条 `decision.decision` 字符串不变；3 个 `_PLACEHOLDER` id 原样；`low/base/high` 全部 `null`（新旧条目均是）；
- (c) 封盘与裁定载体收尾复算 sha256 与开工前逐一相同（`hypotheses.json f2178768…`、`decision.md e9c96f02…`、`validate_hypotheses.py`、`ruling.md f927c44c…`、`substitute_caliber.json 649a9ff8…`、`oracle.md f5c45290…`、MERGE `handoff.json b7314a22…`）。

### N1 命名规则（自行检索，不采信工位自报）

检索范围（冻结）：`execution_v2/*.md`（含 `model_cards.md`、`START_HERE.md`、`card_I-11-A.md`、`common_*_cards.md`）、`execution_v2/*.json`（`dispatch.json`、`model_cards.json`、`research_cards.json`）、`I-11-A/a20260919-01/{decision.md,oracle.md,review.md,mechanism_review.md}`、`I-11-A/.../tools/{validate_hypotheses.py,build_hypotheses.py}`、计划根 `*.md`（`OWNER_DECISIONS.md`、`REMEDIATION_REGISTER.md`、`task_plan.md`、`findings.md`、`implementation_plan.md`、`README.md`）。
检索词（冻结）：`命名|构词|命名法|词法|命名规则|naming|naming_rule|全大写下划线|ISSUER|parameter_id`。
判定：**找到逐字构词规则 ⇒ 以其为准**（与工位归纳冲突时以文档为准并登记）；**全部不命中逐字构词规则 ⇒ 沿用归纳规则** `{发行人}_{范围或分部}_{指标}_{期间 FY20xx}[_PLACEHOLDER]`，并如实登记 `explicit_naming_rule_document = NOT_FOUND（本工位独立检索复核）`。

---

## 4. 执行顺序（本节在 §7 冻结登记之后才允许动）

1. **写 `oracle.md`（本文件）→ 立即复算 sha256**（先冻结）；
2. 追加前记 `model_cards.md` **前像**（sha256 + 字节数）；按 §5 规格生成追加文本，**只在文件末尾追加**；追加后复算**后像** sha256，并做**前缀不变证明**（新文件前 `N` 字节的 sha256 == 前像 sha256）；
3. 复算 `model_cards.md` **后像** sha256 ⇒ 代入 §5 manifest ⇒ **第一次**计算 `decision_sha256`（写入前）；
4. 生成 `hypotheses_v3.json`（同形 8 元素数组；只动注册相关条目），写入 `decision.decision_sha256` 与块内 `provenance`；写后 `json.load` 重解析；
5. 调 `validate()`（只调它，`-B`，不跑 `main()`，不写报告、不落 `__pycache__`）⇒ 要求 `errors = 0`；
6. 写 `model_cards_append.md`、`registration.md`、`handoff.json`（写后 `json.load` 重解析）；
7. **第二次**计算 `decision_sha256`（全部写入后）—— **两值必须逐字符相同**，否则判 `blocked` 并登记；
8. 收尾核验：封盘/裁定载体 sha 不变；`model_cards.md` 前缀不变；UTF-8 无 BOM、CR=0；`git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` = 0。

---

## 5. `decision_sha256` 的 preimage（冻结，可被任何第三方独立复算）

```
decision_sha256 = SHA256( preimage_bytes )   （小写十六进制）
preimage_bytes  = <OPEN2-SUBSTITUTE-CALIBER/a20260925-01/ruling.md 的原始字节，35872 B>
                  || 0x0A
                  || UTF8( 下方 manifest 文本，无尾随换行 )
manifest =
OPEN2-C2-REGISTRATION/1
station=execution_runs/OPEN2-C2-REGISTRATION/a20260926-01
role=implementer_registration
decision_source=execution_runs/OPEN2-SUBSTITUTE-CALIBER/a20260925-01/ruling.md
decision_source_sha256=f927c44cacacb6d0db8e9d1cc09aa559d74427837fd885c4cd0081dbca899e53
substitute_caliber_sha256=649a9ff8d1a4490aedbe863ee52a338ba7b30c50408d7ca5f0a9361daa622e72
oracle_source_sha256=f5c4529095534013e4dee39b40d42d24ab435030ef81290dfa5ab0e97419f945
hypotheses_supersedes_sha256=f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28
model_cards_preimage_sha256=855b5e2d06cc02a1c103316224a428fcfc7a1cc8fb3cfbf07f1f066a552855ab
model_cards_postimage_sha256=<追加完成后实测值填入，冻结时未知>
parameter_ids=ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027|ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027|ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027|ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027
conditions=C-1|C-2|C-3|C-4|C-5
decision=professional_reviewer_ruling_bound_by_hash_not_an_approval
state=unchanged_pending_professional_decision
low=base=high=null
released=false
```

**作用域（冻结）**：该 sha 封存的是「**前一专业 reviewer 的裁定记录 + 本次注册动作**」这一**绑定关系**；它**不是**任何命题的批准签署、**不是**阈值审定、**不是**参数放行。`decision.decision` 字符串保持原文 `pending`，`professional_reviewer` / `reviewer` 字段**不改**（本工位不代签）。

**复算纪律**：manifest 的每一项在第一次计算时即固定；第二次计算必须**从盘上重新读取** `ruling.md` 字节与 `model_cards.md` 现字节重算，不得复制第一次的结果。

---

## 6. 预期副作用与登记（fail-closed，先写后测）

1. **`model_cards.md` 末尾追加会改变最后一个卡片段的段哈希**：`execution_v2/validate_execution_pack.py` L25–L36 以「卡片标题 → 下一个卡片标题（最后一个则到文件尾）」提取段并比对 `dispatch.json` 的 `source_section_sha256` 与 `card_*.md` 正文。本工位**实测追加前基线**：32 个段绑定、**0 错**、最后绑定卡 = `I-10-B` ⇒ 追加后**预期新增 2 条**（`stale extracted card source I-10-B`、`single-card body differs from source I-10-B`）。
2. **处置（冻结）**：**如实实测并登记**（追加前后各跑一次同一段绑定检查），**不修改 `dispatch.json`、不改 `card_I-10-B.md`**（两者均不在本工位写入面）；把「由编排层按 T1-12 ① 同步刷新 `source_section_sha256` / 卡文正文」列为移交项。
3. **已知基线红**：`execution_v2/validation.json`（2026-09-21 检查）已有 **32 条** `source binding changed or missing`（产品仓脚本漂移）⇒ 该验证器**当前本就不通过**；本副作用**不改变其红/绿状态**，但新增 2 条可归因于本追加的条目，必须登记而非隐瞒。
4. **不写 `execution_v2/validation.json`**（跑 `validate_execution_pack.py` 会覆写它 ⇒ 超出写入面），故用**只读复算脚本**复现 L25–L36 的同一判定式。

---

## 7. 冻结登记

- 本文件写入后计算 sha256，**先**把该值记入 `registration.md` §①，**再**执行 §4；
- §3 判据、§5 preimage、§4 顺序在冻结后**不得修改**；实现细节需调整只能追加 `oracle_r2.md` 并作废本轮 `decision_sha256`；
- 实测结果（含 C-1…C-5 逐条、命名规则检索、校验器 rc、两次 `decision_sha256`、前缀证明、`git diff` 计数）原样抄入 `registration.md` 与 `handoff.json`。
