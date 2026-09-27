# BLOCKED6C-THRESHOLD-REVIEW-STATUS oracle（在第一次运行校验器之前冻结）

card_id: `BLOCKED6C-THRESHOLD-REVIEW-STATUS` · attempt_id: `a20260926-01`
role: **I-11-A 实现者侧 / 编排层 schema 侧执行者（`handoff.implementer_signed=false`，交付待独立复审）**
授权: 派单 `17c710a9`（登记册 `REMEDIATION_REGISTER.md` §一四三 B.4）；要求原文 = `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md` **L298 / L324**（`BLOCKED-6c`）
冻结时刻: 本文件写入时刻 **早于** 本 attempt 的**第一次**校验器运行（正例、反例套件、变异、L271 监测均未运行）。
本文件冻结后只允许以 `erratum-*` 追加式附录修订，正文一字不改。

---

## 0. 本卡做什么、不做什么

**做（唯一范围）**：给 `I-11-A/a20260919-01/tools/validate_hypotheses.py` 落地 `falsifier.threshold_review_status`
字段的**识别、闭集、默认值、封缄一致性、机器可用性判定**，并按 `DEC-14` 流程**补反例 + 重跑反例计数**。
**只出 `changes.diff`，改在本 attempt 的 `iso/`/`iso_patched/` 副本。**

**不做（照抄派单硬约束）**：不写产品仓（`dayu-agent`/`company-wiki`/`revenue-forecast` 非 `.planning` 一律不碰）·
不改封盘 `I-11-A/a20260919-01` 任何字节 · 不改 `OPEN6-TOLERANCE-RULING`/`OPEN6-TOLERANCE-TABLE`/两半区裁定
（`I11A-OPEN-ACCT`、`I11A-OPEN-IND`、`I11A-OPEN-MERGE`）任何字节 · 不解除 `BLOCKED-6b` · 不解除 `OPEN-6` ·
不放行任何参数/阈值（`low/base/high` 仍 `null`）· 不产生 `I-11-B`/`I-11-C` 的 ACCEPT · 不代签 ·
不写五份计划文件 · 禁 git 写 · **禁用 `git status`** · 不联网。

---

## 0.1 `common_filing_cards.md` L17 适用性（我自己判断，写明）

**L17 逐字**：「凡跨项目公共 schema、canonical writer、registry 或 worker API，只有指定 owner 写；
发现 scope 外必要改动先记录阻断并交 owner 补卡，不能为绿灯建立平行框架。」

**我的判断：L17 不适用于本卡。** 理由（回源）：
1. L17 的辖域是**跨项目公共**四类件（跨项目 schema / canonical writer / registry / worker API）；
2. `threshold_review_status` 是 **`I-11-A` 计划内数据**：写进本卡自己的 `hypotheses.json` schema 判据与
   `I-11-A` **自己的** `tools/validate_hypotheses.py`（`execution_v2/card_I-11-A.md` 契约内），不落在
   `dayu-agent`/`company-wiki`/`revenue-forecast` 任何产品仓，也不被 registry/worker/writer 消费；
3. 本卡补丁**不新建任何平行框架**：新增错误码与反例进**同一支** `validate_hypotheses.py` 与同一份
   `validation_report.json`，完全沿用 `I-11-A` 已有的报告/反例套件通道。
4. 该判断与登记册 §一四三 B.1 的回源复读结论一致（**我自己复读 L17 原文后独立得出，非采信转述**）。

> 若独立复审认为 `threshold_review_status` 已升格为跨项目公共 schema ⇒ 本卡判 `scope_error`，
> 补丁作废并转 schema owner 补卡。**该判据由复审行使，不由我自行豁免。**

---

## 1. 输入绑定（冻结前已读；sha256 为实测值，如实登记）

| 文件 | sha256 | 字节 |
|---|---|---|
| `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md`（L226/L230-232/L271/L276-278/L298） | `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2` | 37,355 |
| `execution_v2/common_filing_cards.md`（L17） | `c54f583976519c66b1b9425fc03a18ec5620bc4d662d5f2f2e0ed184006b325b` | 6,964 |
| `OWNER_DECISIONS.md`（§二十七/§二十八/§二十九） | `4fe79ba53db5915cb9cab645f448e9861323814f679ec5bb0154a166cd31fe9e` | 90,624 |
| `execution_runs/I-11-A/a20260919-01/decision.md`（**DEC-6** L153-177、**DEC-14** L345-369） | `e9c96f02118514b8596620b3c0e235a797747fcd3bcf59d1a0fd20aa70166951` | 29,756 |
| `execution_runs/I-11-A/a20260919-01/oracle.md`（§7、§R2-1/R2-2） | `83dca500732f9365bbca865b4098729657d994af6ad40b282c26237c9906a890` | 22,418 |
| `execution_runs/I-11-A/a20260919-01/review.md`（§5 P2-5 行） | `4938e745adc3f32582cc6fd70e3e69197385035d0270807d955d2a7c7776daed` | 19,417 |
| `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py`（**被改对象**，前像） | `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac` | 28,549 |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**只读，本卡不改**） | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 51,697 |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json` | `3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf` | 13,863 |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/validation_report.json`（归档基线） | `dc014e7e7a5699f5692d60d3e7cf76b782d1c64ef7668d5104e077290cb7c9b8` | 5,341 |
| 先例卡 `I11A-OPEN12-VALIDATOR-COMPLETENESS/a20260925-01/oracle.md` | `e61cb82bda3e2c6947bcc7caf138b61c70ed79cb8be94c64bb754a055fb5a014` | 16,328 |
| 先例卡 `.../changes.diff`（格式模板） | `860963d42ad747c41d5436fb7460a4e8ca7a0427478633ca81837c64eaf01aaa` | 12,113 |
| 先例卡 `.../ruling.md` | `217b4ab51ee43bf5a440f45e8f479d3b680b4ec80e3240c9a75effb779fba2a0` | 30,489 |
| `REMEDIATION_REGISTER.md`（§一四三 = 本卡派单登记） | `6252d91330c437d143b8eb1a3b4d8aa636f9d64d2e27bd1395d2696b6b82907c` | 443,925 |
| `execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json`（L122 = C5 前/后半） | `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878` | 21,808 |
| `execution_runs/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json`（L271 语料） | `32c22208573a71d53033c4535e8d0cb598c61710e06174196033d996999d7859` | 55,213 |
| `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（L271 语料） | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 61,231 |
| `execution_runs/HYPOTHESES-V4-MERGE/a20260926-01/hypotheses_v4.json`（L271 语料） | `ebf6fa4e2f708c397165127926475d5426afbdef0d93864a795a8640029c4654` | 68,565 |
| `execution_runs/OPEN6-TOLERANCE-TABLE/a20260925-01/tolerance_table.json`（L271 语料） | `1da977bfe05e23545363f123bb1f00e1b21e153849173e5ec9ed9bd8ec315573` | 37,631 |
| `execution_runs/OPEN6B-TOLERANCE-RULING/a20260926-01/tolerance_signed.json`（L271 语料） | `3ad403ba75cf545721b0ba4fa32345d5ecae00c1802e4ca39feb5f19d5f747e8` | 18,082 |

**冻结前已做的输入读取（如实披露）**：我读了上述文件的**相关段落**（ruling L226/L230-232/L271/L276-278/L298、
DEC-6、DEC-14、oracle §7/§R2、`validate_hypotheses.py` 全文、8 条命题的 `state/basis/threshold`、
登记册 §一四三），并做了一次**只读全盘 JSON 扫描**（见 §6 语料枚举表）用于冻结触发线。
**我没有在冻结前运行过 `validate_hypotheses.py` 的任何部分**（没跑正例、没跑反例套件、没跑变异、
没跑 L271 监测）。已建 `iso/` 副本并记前像 sha（与上表逐字一致），**未改任何被改对象**。

---

## 2. 判据（四条，冻结）

- **J1 红→绿**：构造反例 `CE-22…CE-25`（§4）。**当前校验器放行其中任何一条 ⇒ 红成立**；
  补丁后四条必须**全部被拒**（期望错误码在 `observed_codes` 中）。
- **J2 判别力（变异）**：`CE-22…CE-25` 与原 21 例在补丁版上全绿后，逐一删除补丁中的每条新判据
  （`M1…M5`，§5），对应期望码必须**消失 / 翻回收行**（变异红）。**没有变异证明的绿一律不算数。**
- **J3 不破坏正例与原 21 例**：补丁版上正例 `positive_case.verdict=pass`（0 errors），且**原 21 例
  逐条仍 `rejected=true`**（基线取归档 `validation_report.json`：`cases=21,
  rejected_as_expected=21, accepted_by_mistake=0`、`positive_case.verdict=pass`）。
  **任一被打破 ⇒ 本卡判 `blocked`**（fail-closed 第 2 条）。
- **J4 `L271` 反例监测**：按 §6 冻结的语料、规则与触发线量化「被判不可用」条数；
  **任一触发线命中 ⇒ 本卡判 `blocked` 并给量化实测**（fail-closed 第 1 条）。

`CE`/`M` 的 expected **全部手算**（依据：逐行读 `validate_hypotheses.py` L117–L303 + L306–L396 的判定路径），
不由任何一次重跑生成；实测与本表不符 ⇒ 按 `erratum-*` 记录，**不回改本表**。

---

## 3. 字段与规则冻结（schema + 可用性判定）

### 3.1 字段（`falsifier.threshold_review_status`）

| 项 | 冻结值 | 回源依据 |
|---|---|---|
| 位置 | `hypothesis.falsifier.threshold_review_status`（与 `threshold`/`threshold_basis` 同级） | ruling L226「凡被下游消费的阈值必须携带 `threshold_basis` **且**显式 `threshold_review_status`」 |
| 闭集 | `{"not_reviewed", "reviewed"}` | L226 默认值 `not_reviewed` + A-6.3 给出的审定路径（`reviewed`）；**计划内不存在第三个值**，故按未知值拒绝 |
| 默认值（字段缺失时） | `"not_reviewed"` | ruling L226 逐字「（默认 `not_reviewed`）」 |
| 字段缺失是否判**文档错** | **否** | ruling L230 逐字「二者缺一或 `not_reviewed` ⇒ fail-closed：**阈值不参与判定（命题仍可登记观察**…）」—— 缺一的后果是**阈值不可用**，不是**命题作废** |
| 缺失如何记账 | 报告写 `defaulted=true` + `carried=false`，并计入 `counts.threshold_review_statuses` | L226「必须携带…显式」⇒ 必须**机器可见**，但按上一行不拒文档 |
| `reviewed` 的充分条件 | `decision.decision_sha256` 为 64 位小写 hex **且** `reviewer` 长度≥8 且不在 `IMPLEMENTER_MARKERS` | A-6.3 第 3/4 条（非实现者签署 + `decision_sha256`）；被拒替代方案 4「用实现者自签的 `decision_sha256` 补齐状态」 |

**为什么不要求历史文件补字段**：L271 把本裁定的实施方式逐字写作「**追加字段 + 默认 `not_reviewed`**」——
**默认值的存在意义就是让先于字段存在的记录不必回改**，且 A-6.3 第 4 条 / DEC-6 恢复规则 L174-175 明写
「**追加式版本化、不回改历史**」。⇒ **本卡不改 `hypotheses.json` 一个字节**（含本 attempt 的 `iso/` 副本，
其 `hypotheses.json` 与封盘前像 sha 逐字一致）。**若独立复审认为必须回改数据** ⇒ 该改动是**另一个文件**的
补丁，须另派；本 `changes.diff` 只含 `tools/validate_hypotheses.py` 一个文件（§8）。

### 3.2 新增错误码（4 条；补丁内以 `B6C-G*` 标记块包裹，便于变异删除）

| 标记 | 错误码 | 触发条件 | 回源 |
|---|---|---|---|
| `B6C-G1` | `E_THRESHOLD_REVIEW_STATUS_UNKNOWN` | 字段**存在**但值 ∉ `{not_reviewed, reviewed}`（含 `null`/空串/`"approved"`/`"TBD"`） | L226 默认值定义 + A-6.3「缺一即维持 `not_reviewed`」的闭集语义；对齐既有 `E_THRESHOLD_BASIS_UNKNOWN` |
| `B6C-G2` | `E_THRESHOLD_REVIEW_STATUS_UNSEALED` | 值 `== "reviewed"` 但缺 A-6.3 封缄（`decision_sha256` 非 64-hex，或 `reviewer` 空/过短/实现者标记） | A-6.3 第 3/4 条；被拒替代方案 4 |
| `B6C-G3` | `E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED` | `state == "approved_frozen"` 且**有效**状态 ≠ `reviewed`（`detail` 区分「字段缺失（默认 `not_reviewed`）」与「显式 `not_reviewed`」） | L226「凡被下游消费的阈值必须携带…**显式** `threshold_review_status`」+ L271「『**未审定不得当已审定**』这一实质不因此改变」 |
| `B6C-G4` | （不拒，只落报告） | `validation_report.json` 新增 `counts.threshold_review_statuses`、`threshold_reviewability`（逐条 + 汇总）、`threshold_review_status_schema` | L278 要求补的是「审定状态」的**机器检查**；下游 I-11-B「阈值门」、I-11-C「须接受新字段」都要能读到机器结论 |

**原判据一律不动**：补丁**只增不删不改**既有检查（`FALSIFIER_KEYS`、`THRESHOLD_BASES`、R2 五条均保持原字节）。

### 3.3 可用性判定（**U-PRIMARY**，本卡冻结的主规则）

对每条阈值记录，`basis = falsifier.threshold_basis`、`raw = falsifier.threshold_review_status`、
`present = 字段是否存在`、`eff = raw if present else "not_reviewed"`：

```
basis ∉ THRESHOLD_BASES                        → 不可用  reason=unknown_basis
raw 存在且 ∉ 闭集                               → 不可用  reason=unknown_status
eff == "reviewed" 且无 A-6.3 封缄               → 不可用  reason=reviewed_unsealed
basis == professional_judgement_required 且 eff != "reviewed"
                                               → 不可用  reason=judgement_not_reviewed
其余（arithmetic_identity / disclosure_definition，eff = not_reviewed）
                                               → 可用    （A-6.2 第 1、3 行「审定前＝可用」）
```
**并集口径（保守）**：一条记录被判「不可用」= **不满足 U-PRIMARY** **或** 其宿主文档会被补丁校验器拒
（即 `B6C-G1/G2/G3` 命中）。L271 的 `U` 一律按此**保守并集**计数。

**U-PRIMARY 的文本依据（为何不把 `not_reviewed` 一律判不可用）**：
1. `A-6.1` 的**小节标题**是「**占位阈值**在审定前的使用禁令」，而 `DEC-6` L156-157 逐字把**占位阈值**
   定义为 `threshold_basis = "professional_judgement_required"` 的那类；
2. `A-6.2` 表逐字给 `arithmetic_identity` = **可用（等式判定）**、`disclosure_definition` = **可用
   （是/否型判定）**、`professional_judgement_required` = **不可用**（列名就是「审定前可否使用」）；
3. 裁定主体 L226 的禁令子句**自带范围**：「`threshold_basis=professional_judgement_required` **且**
   `threshold_review_status≠reviewed` 的阈值不得触发任何自动动作」；
4. L271 把实施方式写作「追加字段 + **默认 `not_reviewed`**」——默认值只在「缺失 ≡ `not_reviewed`，
   再按范围规则分流」时才有意义。

**同时冻结的反事实规则（U-LITERAL，只测不采）**：A-6.1 第 1 条字面「二者缺一或状态为 `not_reviewed`
⇒ fail-closed」若**不**按小节标题/DEC-6/A-6.2/L226 限定到占位阈值，而是**对全部三类一视同仁**，
则「`eff != reviewed` 一律不可用」。本卡**同时跑出 U-LITERAL 的量化数字**并原样披露（§6/`handoff`），
**但不以它判 J4**——理由见上述 1-4 条；**若独立复审采字面读法 ⇒ 该读法下触发线必然命中 ⇒ 本卡应改判
`blocked` 并按 L271 重议实施方式**。此分歧**由复审裁定，不由我静默选边**（见 `handoff.unverified`）。

---

## 4. 预注册反例 `CE-22…CE-25`（冻结后不得增删）

基命题统一取 `H-CN-ZIJIN-SEG-01`（`basis=arithmetic_identity`，正例下单独通过；实现者自己的套件也用它作 base）。
每条只改所列一处；`CE-24/25` 需同时给**合规** `reviewer`（≥8 字、非实现者标记）与 64-hex
`decision.decision_sha256`，以免撞上既有的 `E_STATE_APPROVED_BY_IMPLEMENTER`，从而**只有新判据能决定红绿**。

| # | 注入 | 规则锚点 | 期望：当前校验器 | 期望：补丁版 | 手算依据 |
|---|---|---|---|---|---|
| **CE-22** | `falsifier.threshold_review_status = "approved"`（`threshold_basis` 保持 `arithmetic_identity` 在场） | ruling L226 闭集 + 默认值定义 | **放行（红）**：`validate()` 从不读该键 | 拒 `E_THRESHOLD_REVIEW_STATUS_UNKNOWN` | L218-244 只遍历 `FALSIFIER_KEYS`，该键不在其中 |
| **CE-23** | `falsifier.threshold_review_status = "reviewed"`，**不给** `decision.decision_sha256` | A-6.3 第 3/4 条 + 被拒替代方案 4 | **放行（红）**：现有 `E_STATE_APPROVED_BY_IMPLEMENTER` 只在 `state==approved_frozen` 分支触发，本条 `state` 不变 | 拒 `E_THRESHOLD_REVIEW_STATUS_UNSEALED` | L292-302 由 `if h.get("state")=="approved_frozen"` 护栏 |
| **CE-24** | `state="approved_frozen"` + 合规 `reviewer` + 64-hex `decision_sha256`；**`threshold_review_status` 缺失**（= 历史真实状态） | ruling L226「必须携带…显式」+ L271「未审定不得当已审定」 | **放行（红）**：三项既有 approved 检查（reviewer 长度/黑名单/sha 非空）全过，无任何审定状态检查 | 拒 `E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED`（detail 记「字段缺失（默认 `not_reviewed`）」） | L226+L271；这是派单 step 3 指名的反例本体 |
| **CE-25** | 同 CE-24，但**显式** `falsifier.threshold_review_status = "not_reviewed"` | 同上（`/=` 分支） | **放行（红）**：同上 | 拒 `E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED`（detail 记「显式 `not_reviewed`」） | L230「缺一**或** `not_reviewed`」两分支各钉一钉 |

**预期汇总（手算）**：当前校验器 **4/4 放行** ⇒ J1 红成立；补丁版 **4/4 拒绝** + 正例 pass +
**原 21/21 仍拒** ⇒ J1/J3 绿。反例套件总数 **21 → 25**（`DEC-14` 补反例并重新计数，§7）。

---

## 5. 变异清单 `M1…M5`（每条 = 在**补丁版**上删除/改写对应新判据块）

| # | 变异 | 预期被它托住而翻红的条目 |
|---|---|---|
| **M1** | **把默认值改掉**：`DEFAULT_THRESHOLD_REVIEW_STATUS = "reviewed"`（原 `"not_reviewed"`） | `CE-24`（字段缺失）翻回**放行**（有效值变 `reviewed` 且 CE-24 带合规封缄 ⇒ G2/G3 均不响） |
| **M2** | **删掉 `not_reviewed` 的 fail-closed 分支**：整块删除 `B6C-G3` | `CE-24`、`CE-25` 同时翻回**放行** |
| **M3** | **把 `threshold_basis` 检查也删掉**：删除既有 `E_THRESHOLD_BASIS_UNKNOWN` 闭集块（L223-226） | **原第 21 例**（`threshold_basis="made_up_basis"`）翻回**放行** |
| **M4** | 删除 `B6C-G1`（状态闭集块） | `CE-22` 翻回**放行** |
| **M5** | 删除 `B6C-G2`（封缄块） | `CE-23` 翻回**放行** |

**变异判据（J2）**：任一 `M*` 下，**至少**其对应条目由「拒」翻回「放行」（= 期望码从 `observed_codes`
消失），且**正例仍 `pass`**。做不到 ⇒ 我的补丁是假判据，判 `insufficient_evidence`。
**M3 的特殊预期（预登记）**：M3 会让**原 21 例中的第 21 例**翻回放行 —— 这是**预期的变异红**，
**不算 J3 的 21 例回归失败**（J3 只在**未变异的补丁版**上判定）；M3 正是用来证明既有 `threshold_basis`
闭集检查是**承重**的。

---

## 6. ⭐ `L271` 反例监测：语料、规则、**量化触发线（冻结）**

> ruling **L271** 逐字：「校验器新增 `threshold_review_status` 后出现**大批**历史阈值被判不可用、
> 导致 `I-11-C` 完全无法启动 ⇒ A-6.1 的实施方式（追加字段 + 默认 `not_reviewed`）需按实际情况重议，
> 但『未审定不得当已审定』这一实质不因此改变。」
> ⇒ **我把「大批」钉成下面三条触发线；命中任一 ⇒ J4 失败 ⇒ 本卡 `blocked`。**

### 6.1 语料（冻结：只读全盘 JSON 扫描实测）

扫描口径：`.planning/2026-09-19-three-project-history-audit` 下全部 `*.json`（**21,908 个**，
排除 `venv|site-packages|__pycache__`，**0 个读取被拒**），按 `threshold_basis` 命中后**人工判定何者是
阈值记录**（`substitute_caliber.json` / `disclosure_adaptation_v2.json` / 各 `handoff|provenance` 中的
`threshold_basis` **均为散文或开关名，不是阈值记录**，不计入）；**排除字节级副本**
（本卡 `iso/`、`iso_patched/` 与先例卡 `iso/`、`iso_patched/` 内的 `hypotheses.json` 拷贝）。

| # | 语料文件（sha 见 §1） | 记录数 | arithmetic | disclosure | professional | 已携带字段 | 宿主 `state=approved_frozen` |
|---|---|---|---|---|---|---|---|
| 1 | `I-11-A/a20260919-01/.../hypotheses.json`（v1，**本校验器唯一实际校验对象**） | 8 | 4 | 1 | 3 | **0** | 0 |
| 2 | `I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json` | 8 | 4 | 1 | 3 | **0** | **1**（`H-CN-ZIJIN-SEG-01`，arithmetic） |
| 3 | `OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json` | 8 | 4 | 1 | 3 | **0** | 0 |
| 4 | `HYPOTHESES-V4-MERGE/a20260926-01/hypotheses_v4.json` | 8 | 4 | 1 | 3 | **0** | **1**（同上） |
| 5 | `OPEN6-TOLERANCE-TABLE/a20260925-01/tolerance_table.json`（`rows`） | 4 | 4 | 0 | 0 | **0** | 0（`hypothesis_state`=pending/unquantified） |
| 6 | `OPEN6B-TOLERANCE-RULING/a20260926-01/tolerance_signed.json`（`thresholds`） | 4 | 4 | 0 | 0 | **0** | 0（`status=SIGNED` 是**容差**签署，非阈值审定；该文件自声明 `does_not_change_threshold_review_status=true`） |
| | **合计（记录级）** | **40** | 24 | 4 | 12 | **0** | **2** |

**两套口径都测**：
- **记录级** `N_record = 40`（同一底层阈值在 v1–v4 四个版本各计一次；容差表/签署表复述了 4 条 arithmetic）；
- **去重底层级** `N_distinct = 8`（v1–v4 是同 8 条命题的四个版本；容差 4 条 = 其中 4 条 arithmetic 的复述）。

### 6.2 手算预期（冻结；实测不符 ⇒ `erratum-*`，不回改本节）

按 §3.3 保守并集口径：

| 项 | 记录级 | 去重底层级 |
|---|---|---|
| 不可用 `U` | **14 / 40 = 35.0%**（12 条 `professional_judgement_required` + 2 条宿主文档被 `B6C-G3` 拒） | **4 / 8 = 50.0%**（3 条 professional + `H-CN-ZIJIN-SEG-01`） |
| 可用 | 26（24 条 arithmetic 中 22 + 4 条 disclosure − 2 条 G3 命中…精确为 arithmetic 可用 22、disclosure 可用 4） | 4（3 arithmetic + 1 disclosure） |
| A-6.2 判可用的记录数 | **28**（24 ar + 4 dj） | **5** |
| **`U_newly`（A-6.2 判可用却被本卡判不可用）** | **2**（两条宿主 `approved_frozen` 的 arithmetic，由 `B6C-G3` 触发） | **1** |
| U-LITERAL 反事实 `U` | **40 / 40 = 100%** | **8 / 8 = 100%** |

### 6.3 **量化触发线（冻结）** —— 任一命中 ⇒ `L271_trigger_fired = true` ⇒ **J4 失败 ⇒ `blocked`**

- **T1（`I-11-C` 可启动性，主触发线）**：对 4 份 `hypotheses*` 各跑一次启动性探针，**任一份**满足
  「可用阈值总数 = 0」**或**「可用 `arithmetic_identity` = 0」**或**「可用 `disclosure_definition` = 0」
  ⇒ 命中。**测法**：`I-11-C` 复用 falsifier 结构（DEC-6 L170-172）做反方检验，它必须至少能取到
  A-6.2 两类「审定前可用」阈值各一条才能对这两类开检验；一条不剩 ⇒ 「完全无法启动」。
  （`I-11-C` 只要**任一**类归零即判无法启动，不看它是否还有 professional 类。）
  *手算预期*：v1 ar=4/dj=1、v2 ar=3/dj=1、v3 ar=4/dj=1、v4 ar=3/dj=1 ⇒ **不命中**；
  U-LITERAL 下四份全 0 ⇒ **命中**。
- **T2（「大批」的绝对量）**：`U / N ≥ 75%`。**记录级 `U ≥ 30`，去重底层级 `U ≥ 6`** ⇒ 命中。
  *手算预期*：14 / 4、4 / 8 ⇒ **不命中**（U-LITERAL：40、8 ⇒ **命中**）。
- **T3（新增伤害面）**：`U_newly ≥ 50% × A-6.2 判可用的记录数`，即**记录级 `U_newly ≥ 14`、
  去重底层级 `U_newly ≥ 3`** ⇒ 命中。*手算预期*：2、1 ⇒ **不命中**（U-LITERAL：24、5 ⇒ **命中**）。

**触发线数字的取法说明（我为何选这些数）**：L271 只说「大批」。本语料共 40 条记录 / 8 条底层阈值，
且 A-6.2 已**先于本卡**把 12/40 条 professional 判为不可用（这**不是**本卡造成的新增伤害）。
故 T2 取 3/4（「大批」= 多数），T3 专门隔离**本卡新增**的那一面并取 1/2（「过半被判可用者翻不可用」），
T1 直接用 L271 的原话后果（`I-11-C` 启动不了）做**不依赖比例**的硬探针。三条**互补**，避免单一比例被绕过。

**`L271_trigger_fired` 的取值（冻结）**：主字段 = **U-PRIMARY 下 T1/T2/T3 是否任一命中**；
另设 `L271_trigger_fired_literal_A61_reading` = **U-LITERAL 下同三条是否命中**（手算预期 `true`），
两个数字**都**写进 `handoff.json` 与最终报告，**不得只报其一**。

### 6.4 `L271` 语料监测**不做的**事

不改语料任何字节 · 不把任何 `threshold_basis` 改成别的值 · 不把任何 `SIGNED`/`approved_frozen`
翻译成 `reviewed` · 不据此放行任何阈值或参数 · 不解除 `BLOCKED-6b`/`OPEN-6`。
监测只输出「**按冻结规则，哪些记录不可用、为什么、够不够 75%/50%/启动性**」的**计数**。

---

## 7. `DEC-14` 合规（L278 明令：新规则 ⇒ 补反例 + 重跑 21 例计数）

按 `decision.md` DEC-14 L355-358、L367「校验器规则变更必须**重跑全部反例并重新计数**；不允许只跑正例」：

1. 新增 4 条错误码（§3.2），**全部固化为反例**（`CE-22…CE-25`，§4）；
2. **重跑全部反例**：原 21 例 + 新 4 例 = **25 例**，逐条记录 `expected_code / observed_codes / rejected`；
3. **分别计数**：`original_21_rejected`（必须 = 21）与 `new_4_rejected`（必须 = 4）与
   `counterexample_summary`（`cases=25, rejected_as_expected=25, accepted_by_mistake=0`）；
4. 按 DEC-14 L361-362 的反例条款，**显式声明本改动仍不是完备性证明**（写进 `validation_report.json`
   的 `threshold_review_status_schema.limitations`）；
5. 按 DEC-14 L364「新增错误码必须同步进 oracle 的 R2 表」—— 本卡**不回改封盘 `oracle.md`**，
   改由**本卡 `oracle.md` §3.2 表**承载（同先例卡做法），并在 `changes.diff` 头部点名。

---

## 8. 范围边界

- **被改对象只有** `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py`（前像 sha §1），
  改在本 attempt `iso_patched/tools/`；`changes.diff` **逐文件披露**，`touched paths = 1 个 py 文件`。
  **`hypotheses.json` 不在 diff 内**（§3.1 理由）。
- `src/`、`scripts/`、`tools/`（产品仓）**一律不触碰**；本卡全部产出落在
  `execution_runs/BLOCKED6C-THRESHOLD-REVIEW-STATUS/a20260926-01/`。
- 封盘 `I-11-A/a20260919-01`、两半区裁定、`OPEN6-TOLERANCE-*`：**只读**，结束前复核 sha256 逐字不变。
- 本卡**不裁** A-6.1 实施方式的最终效力（那是 ruling owner / 独立复审的权力）；我只**冻结测试判据**
  并把两种读法的量化数字都摆出来（§3.3 / §6.3）。

## 9. 退出判据

1. 本 `oracle.md` 已先冻结（本文件写入早于第一次校验器运行）；
2. J1 红（`CE-22…CE-25` 4/4 放行，记原始 rc）→ J1 绿（4/4 拒）；
3. J3 绿：正例 `pass` + **原 21/21 仍拒** + 新 4 例拒 ⇒ 套件 `25/25`（DEC-14 计数）；
4. J2 绿：`M1…M5` 逐条按 §5 预期翻红；
5. J4：`L271_trigger_fired` 与其字面读法反事实**都**给量化数据；
6. `changes.diff`（逐文件、前/后像 sha、字节数）+ `handoff.json`：
   `status=review_pending`、`implementer_signed=false`、`releases_nothing=true`、
   `does_not_claim_I11A_acceptance=true`、`L271_trigger_fired`(bool) + 量化、`unverified` 如实；
7. `git diff HEAD --name-only` 非 `.planning` = **0**；JSON 写后 `json.load` 重解析；UTF-8 无 BOM、LF。
