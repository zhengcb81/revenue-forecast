# OPEN6-H4-FOUR-REQ · `H4` 阈值「给数四要件」补齐 —— 会计/披露 reviewer **oracle（先冻结，后裁定）**

- 工位：`accounting_reviewer_h4`（会计 / 披露 reviewer，**非实现者**）
- 卡：`I-11-A` · 被审 attempt（**全程只读**）：`execution_runs/I-11-A/a20260919-01`
- 本载体（**新建**）：`.planning/2026-09-19-three-project-history-audit/execution_runs/OPEN6-H4-FOUR-REQ/a20260926-01/`
- 唯一写入面（五件）：`oracle.md` · `h4_four_req.json` · `hypotheses_h4_v1.json` · `ruling_h4.md` · `handoff.json`
- 本文件是**判据冻结件**：先写本文件 → 才允许生成 `hypotheses_h4_v1.json` / `h4_four_req.json`。**冻结后不回改**（若必须改，整轮作废重跑）
- 纪律：**禁网** · **禁 git 写** · **禁用 `git status`** · `.planning` 之外**零写入**（含 `company-wiki`，其 PDF 只读）· 五份计划文件**不写** · 封盘 `I-11-A` **零字节改动**

---

## 0. 授权与定义（回源逐字；sha256 为本工位自算，不采信他人登记）

| # | 授权点 / 定义 | 逐字原文 | 出处（本工位实测） |
|---|---|---|---|
| A1 | **四要件定义** | 「审定一个阈值必须同时具备**可复算观测量 + 可核基础 + 非实现者签署（decision_sha256） + 追加式版本化**，否则一律维持 `not_reviewed`」 | `I11A-OPEN-ACCT/a20260924-01/ruling.md` **L226**，sha `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2`（37,355 B） |
| A2 | **四要件细则 A-6.3（前四条 = 四要件）** | L248 观测量可复算；L249–L253 数值有可核基础且属 (i)–(iv) 之一；L254 签署身份 = 非实现者 + `decision_sha256` + 日期 + 作用域（`hypothesis_id` + `parameter_id`）；L255 追加式版本化 = 审定后写入命题**新版本**、旧版本保留、**不回改历史** | 同上 **L248–L256** |
| A3 | **A-6.1 fail-closed（L230）** | 「二者缺一或状态为 `not_reviewed` ⇒ **fail-closed**：阈值不参与判定……**不得**据此宣布『被推翻/未被推翻』」；「`threshold_basis=professional_judgement_required` 且 `threshold_review_status≠reviewed` 的阈值**不得触发任何自动动作**（falsifier 触发、情景切换、校准边界、I-11-C 反方检验）」 | 同上 **L230** / **L226** |
| A4 | **A-6.3 第4条落地方式（恢复规则）** | 「阈值审定后：新建 `OPEN-6-ACCT-R2`（附审定记录 sha256、证据链、作用域），命题新增版本并保留旧版本；本条正文与 `threshold_basis=professional_judgement_required` 的历史标注**一律不改**，只追加状态」 | 同上 **L284** |
| A5 | **BLOCKED-6a / 6c 分派** | 「BLOCKED-6a：3 条 `professional_judgement_required` 阈值的**数值**是否恰当（±5%、[0.9,1.1]、拆分层级判定）—— 需行业/专业 reviewer 按 A-6.3 给出证据与签署；我**不给数**」／「BLOCKED-6c：`threshold_review_status` 字段的**落地实现与校验器改动** —— 属 I-11-A 实现者/编排层与 schema 侧，我只给要求」 | 同上 **L296** / **L298** |
| I1 | **H4 行业面给数** | 「**H4** ｜ 计划达成率 `[0.9, 1.1]` ｜ ✅ **采用**（矿业面给数）｜ **0.90 – 1.10**（±10%）｜ `professional_judgement`（本 reviewer，矿业面）」 | `I11A-OPEN-IND/a20260924-01/ruling.md` **L288**，sha `8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b`（39,207 B） |
| I2 | **放行条件（本工位确认权来源）** | 「**放行条件**：本条仅为**行业面审定**；是否可标 `threshold_basis` 升级、以什么基础允许给数，**由 `I11A-OPEN-ACCT` 依其基础规则确认**，在此之前 I-11-B/I-11-C 不得据此触发。」 | 同文件 **L299**（逐字） |
| I3 | **阈值 ≠ 参数放行** | 「I-11-B：H4 阈值影响 `ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER` / `ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 的达成判定（**注意这两个参数仍是 `_PLACEHOLDER`，阈值审定不等于参数放行**）」 | 同文件 **L330**（逐字） |
| M1 | **本任务的判例文本** | 「### 3.2 易误读点 (a)：行业面给了 **H4 = [0.90, 1.10]** —— 这等于该命题 `approved_frozen` 吗？」「**结论：四要件 1/4 满足 ⇒ 不齐 ⇒ 按 ACCT L226 一律维持 `not_reviewed`**（该字段本身尚未落地 = BLOCKED-6c，`ACCT ruling.md` L298）⇒ 按 A-6.1（L230）该阈值**不得触发任何自动动作**。」 | `I11A-OPEN-MERGE/a20260924-01/merge_ruling.md` **L275** / **L288**，sha `2d214bab861be4ff30ebb7118705d23183fb2eec3e58f987d52287d0bab2e5c1`（49,062 B） |
| M2 | **C5 派单原文** | 「OPEN-6：threshold_review_status 落地 + H4 四要件补齐 + H2 基准 + 恒等式容差对照表」 | `I11A-OPEN-MERGE/a20260924-01/handoff.json` **L122**，sha `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878`（21,808 B） |
| S1 | **同形态先例（格式参照）** | 「preimage = UTF-8（无 BOM）字节串……`decision_sha256 = SHA-256(preimage)` 的小写十六进制」 | `I11A-HYP-APPROVE/a20260925-01/ruling.md` §4.3，sha `5b71efa4a27f9860bc02d03f10c37bd919ecbf57199369318829d342b1932050`（37,879 B） |
| S2 | **同角色同轮先例（签署式）** | `decision-sha256/v1` = `sha256( utf8( json.dumps(pre, sort_keys=True, ensure_ascii=False, separators=(',',':')) ) )`，写入前后各复算一次 | `OPEN6B-TOLERANCE-RULING/a20260926-01/handoff.json` L72–L78，sha `b4497616b8e82edd7bd4f707b0e9b739589403feedb97c5803d80c00b63403b7`（20,098 B） |

> **我 = 会计/披露 reviewer（非实现者）**：我未参与 `I-11-A` 的任何实现步骤；`handoff.implementer_signed = false`；不代签行业面会签、不代签任何其他角色。
> **本工位只做一件事**：逐件复核并（若判齐）补齐 `H-CN-ZIJIN-PLAN-04`（`H4`）阈值的四要件 ②③④。**不放行任何参数、不解任何 `BLOCKED`、不触发任何动作。**

---

## 1. 冻结判据：四要件 R1–R4（逐条可机检）

对「一个阈值审定记录」判定，**四条同时成立 ⇒ `4/4`；任一不成立 ⇒ `blocked`（并列出缺哪件）**。

### R1（要件①）可复算观测量

同时成立：

1. `falsifier.observable` 非空且指向**具体披露行/表**（含可识别的产品/指标与对照基准）；
2. `falsifier.source_route` 非空且可定位到发行人披露章节；
3. `falsifier.observation_date` 含可解析日期锚（正则 `\d{4}\s*[-/年]\s*\d{1,2}`），滞后明确；
4. `falsifier.threshold` 非空、`threshold_basis` ∈ 闭集 `{arithmetic_identity, professional_judgement_required, disclosure_definition}`。

- **不采信**实现者自述，须由本工位读封盘 `hypotheses.json` 原文字段本身确认。

### R2（要件②）可核基础 —— A-6.3 第2条四类之一，**必须写明是哪一类**

判定树（**先冻结，四类互斥取其一**）：

| 类 | 判据（本工位必须在盘上取证） | 取证标准（先冻结） |
|---|---|---|
| (i) 来源自身披露容差/定义 | 被引原文**自己**写明了该比率的容差/口径定义 | 关键词检索（`达成率`/`±10`/`偏差`等）**零命中** ⇒ 不得用 (i) |
| (ii) 同口径历史离散 | 同一披露指标在 **≥2 个可比披露期**上的实际「计划/实际」配对，**计算过程与所用原文一并归档**（可复算） | 盘上可配对期数 **< 2** ⇒ **不得**用 (ii)（单点无「离散」可言） |
| (iii) 准则/监管/交易所明文 | 引到**原文**明文定义该容差 | 盘上语料零命中 ⇒ 不得用 (iii) |
| (iv) 专家假设 | **允许**，但必须 ①标 `expert_assumption = true` ②给出**敏感性区间**（至少一个比主阈值更宽与更严的档位，并写明各档后果）③`equivalent_to_disclosure_basis = false`（**永远不得**被记为等同披露依据） | 三小项缺一 ⇒ R2 不成立 |

- **R2 成立** ⇔ 存在 `threshold_review.basis_class` ∈ 上表之一，且该类的全部要求在记录中逐项写明。
- **明令禁止**：以「行业判断理由」「通常视为」这类**叙述**代替四类归类（这正是 `merge_ruling` L284 对行业面的批评点）；**禁止**为凑 4/4 而把 (iv) 谎报为 (i)/(ii)/(iii)。

### R3（要件③）非实现者签署 + `decision_sha256`

1. `decision.decision_sha256` 匹配 `^[0-9a-f]{64}$` 且**非** `null`；
2. 该值 = 本 oracle §2 冻结的 preimage 求值结果（本工位**写入前后各复算一次**，两次须逐字符相同）；
3. 签署人身份为**非实现者**：`signer.role = accounting_reviewer_h4`，`signer.is_implementer = false`，且不在 `IMPLEMENTER_MARKERS = {本卡实现者, implementer, I-11-A implementer, 弱模型}`；
4. 记录带**日期**与**作用域** = `hypothesis_id`（`H-CN-ZIJIN-PLAN-04`）+ `parameter_id`（`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER`）。

### R4（要件④）追加式版本化

1. 新版本文件 `hypotheses_h4_v1.json` 存在，顶层 = 与封盘同形的 **8 元素 JSON 数组**；
2. `provenance.supersedes_sha256` == `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（封盘原件）；
3. `provenance.modified_indices == [3]`，其余 7 个下标与封盘**逐字节（规范化 JSON）相等**；
4. **新版本必须真的「新」**：下标 3 与封盘下标 3 **不相等**（若「新版本」实为旧版本原字节 ⇒ R4 不成立）；
5. **旧版本保留**：封盘文件 `f2178768…` 收尾复算仍逐字节未改（= 旧阈值/旧版本保留供 I-12 评分）。

### 统一：`blocked` 触发条件（fail-closed，先冻结）

出现下列任一 ⇒ 判 **`blocked`**，输出 `h4_four_req_status = "still_1_4"`（或实际计数）+ 缺件清单 + 实测证据，**该结果即为合格交付**，不得放宽判据凑 4/4：

- R1–R4 任一不成立；
- R2 四类**都无法**在盘上取证（尤其 (ii) 期数不足、(i)/(iii) 零命中却仍想给数）；
- §2 的 preimage 两次复算不一致；
- 封盘 `hypotheses.json` 收尾 sha ≠ `f2178768…`（只读纪律被破坏）；
- 写入面越界（`.planning` 之外出现新字节、或五份计划文件被改）。

---

## 2. 冻结：`decision_sha256` 求值方式（`decision-sha256/v1`）

```
preimage = utf8( json.dumps(pre, sort_keys=True, ensure_ascii=False, separators=(',',':')) )
decision_sha256 = sha256(preimage) 的小写十六进制
```

`pre` 的键集合（**先冻结；写入前不得增删改键名**）：

| 键 | 内容 |
|---|---|
| `schema` | `"decision-sha256/v1"` |
| `role` | `"accounting_reviewer_h4"` |
| `carrier` | `"execution_runs/OPEN6-H4-FOUR-REQ/a20260926-01"` |
| `action` | `"h4_threshold_four_requirements_confirmation"` |
| `authorized_by` | `{ind_l299: <IND ruling L299 逐字>, merge_ruling_3_2: <merge_ruling §3.2 标题逐字>, c5: <handoff L122 逐字>}` |
| `scope` | `{hypothesis_id: "H-CN-ZIJIN-PLAN-04", threshold: "实际产量 ÷ 计划产量 ∈ [0.9, 1.1]", parameter_ids: [两个 `_PLACEHOLDER`]}` |
| `four_requirements` | `{r1: "satisfied", r2: "satisfied", r3: "satisfied", r4: "satisfied"}`（各值按实测；若判不齐则写 `"not_satisfied"` ⇒ 该 sha **不写入**） |
| `basis_class` | `"expert_assumption"` |
| `expert_assumption_marked` | `true` |
| `sensitivity_interval` | `[0.85, 1.15]`（外档）/ `[0.95, 1.05]`（内档），主阈值 `[0.9, 1.1]` |
| `equivalent_to_disclosure_basis` | `false` |
| `sealed_original_sha256` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| `new_version_file` | `"hypotheses_h4_v1.json"` |
| `threshold_review_status_effective` | `"not_reviewed"` |
| `releases_nothing` | `true` |
| `signed_by` / `signed_at_utc` | `"accounting_reviewer_h4（会计/披露 reviewer，非实现者）"` / ISO-8601 Z |

- preimage 全文（canonical 字符串）逐字存入 `h4_four_req.json → decision_preimage_canonical`，任何人可重算。
- **复算两次**：写入 `hypotheses_h4_v1.json` **前**一次、写入**后**重新从 `h4_four_req.json` 提取 preimage 再算一次；两次与写入 JSON 的值必须逐字符相同（记 `decision_sha256_before_write` / `decision_sha256_after_write` / `two_pass_match`）。

---

## 3. 冻结：`threshold_review_status` 的处置（先裁定，后执行）

| # | 判据（先冻结） | 结论 |
|---|---|---|
| 3.1 | 封盘 `hypotheses.json` 是否含 `falsifier.threshold_review_status` | **本工位实测：不含**（8 条全无）⇒ 权威口径有效值 = 默认 `not_reviewed` |
| 3.2 | 该字段的**落地实现与校验器改动**归谁 | `ACCT L298` 逐字归 **I-11-A 实现者/编排层与 schema 侧**；派单明令**不解除 `BLOCKED-6c`** ⇒ **本工位不代落地 schema、不改任何校验器** |
| 3.3 | 本工位在自己的新版本里写什么 | **显式写 `threshold_review_status = "not_reviewed"`**（追加字段、fail-closed；**不升级为 `reviewed`**） |
| 3.4 | 为什么四要件补齐后仍写 `not_reviewed` | (a) 把状态升为 `reviewed` 会打开 A-6.1 的下游触发门，而派单明令本工位**不触发任何自动动作**、**不解除 `BLOCKED-6c`**；(b) `IND L299` 的另一半（**行业面会签**）按派单「另议」，本工位**不代签**；(c) fail-closed：**宁可记为未审定，也不产生一个「看起来已解锁」的状态** |
| 3.5 | 四要件 `4/4` 与 `threshold_review_status=not_reviewed` 是否矛盾 | **不矛盾**：A-6.3（L246）逐字是「必须**同时**满足，**缺一即维持** `not_reviewed`」——这是**必要条件**句式；补齐四要件**解除的是「被强制维持」**，不等于状态字段被自动升级。状态升级 = schema 落地 + 会签后的独立动作，**不在本工位写入面与授权内** |
| 3.6 | 机器可读后果 | 权威封盘文件：字段缺失 ⇒ 有效 `not_reviewed`；本工位新版本：显式 `not_reviewed` ⇒ A-6.1 触发门**两侧都保持关闭**；`releases_nothing = true` |

---

## 4. 冻结：取证与复算方法

1. **一手语料**（sha256 由本工位现算，见 §0）：封盘 `hypotheses.json`、封盘校验器、ACCT/IND/MERGE 三份 ruling、`I-10-A` 的 `CN-ZIJIN-2025.txt` 抽取件、`company-wiki` 两份紫金年报 PDF（**只读**）。
2. **不采信实现者/行业面自述的数值**：涉及「计划值 / 实际值 / 配对期数」的数字，一律由本工位从原文抽取件或 PDF **自己重算**并登记命令与结果。
3. **②的取证标准**见 §1 R2 表（关键词零命中 / 期数 < 2 即判不可用），**不以常识、行业惯例、"数据恰好凑平"代填**。
4. **校验器纪律**：只调用 `validate(hypotheses, source_map, attempt, doc_texts)`；**绝不执行 `main()`**（不写 `validation_report.json`、不写 ascii log）；运行方式 `PYTHONDONTWRITEBYTECODE=1 python -X utf8 -B -`（脚本经 stdin 传入）⇒ 零脚本文件、零 `__pycache__`、封盘 `tools/__pycache__` 不变。
5. **变异测试脚本**以 stdin 内联执行（**不落盘**），结果逐条记入 `ruling_h4.md §⑤`。
6. **JSON 写后 `json.load` 重解析**；UTF-8 **无 BOM**；**LF**（CR 计数 = 0）。
7. 收尾只跑 `git -c core.quotepath=false diff HEAD --name-only`（**禁用 `git status`**），非 `.planning` 条目须为 0。

---

## 5. 冻结：红 / 绿 / 变异清单

**绿（`rc = 0`）**：`hypotheses_h4_v1.json`（含 R1–R4 记录）判 `4/4`；且封盘校验器 `validate()` 对它 `errors = 0`（对封盘原件亦 `errors = 0` 作对照）。

**红（`rc ≠ 0` = 被检出）**：

| id | 变异（对判据或记录的改写） | 必须红的检查 | 期望 |
|---|---|---|---|
| **B0** | **基线红分支**：直接对**封盘原件**下标 3 判四要件（无 `threshold_review` 块、`decision_sha256 = null`、无新版本） | 四要件检查器 | `still_1_4`，`rc ≠ 0`（应复现 merge_ruling 的 1/4） |
| **M1** | **四要件缺一**：把 `threshold_review.basis_class` 置空（② 缺） | 四要件检查器 | `3/4`，`rc ≠ 0` |
| **M2** | **`decision_sha256` 换值**：把 `decision.decision_sha256` 末位改一个十六进制字符 | preimage 复算 | `rc ≠ 0` |
| **M3** | **新版本改成旧版本**：把下标 3 换回封盘原字节（`provenance.modified_indices` 仍谎报 `[3]`） | R4「真新性」检查 | `rc ≠ 0` |
| **M4** | **判据改弱（方向性红）**：把 R2 改成「存在任一叙述性理由即可，不分类、不要求 `expert_assumption` 标注与敏感性区间」，喂入**行业面原始叙述**（无四类归类）的记录 | 弱判据必须放行、强判据必须拒绝 | 弱判据 `4/4`（= 不该被审定的阈值**通过了**）∧ 强判据 `rc ≠ 0` ⇒ **检出**，`rc = 0` |
| **M5** | **判据改弱（方向性红）**：把 R3 改成「`decision_sha256` 非空即算签署」（不复算 preimage） | 弱判据放行假 sha、强判据拒绝 | 同上 ⇒ **检出**，`rc = 0` |

- **`rc ≠ 0` 的含义**：该变异**未**被检出 = 判别力不足 = 不合格。
- **blocked 分支也要红**：B0 与「四要件任一不成立」的全部分支必须 `rc ≠ 0`。

---

## 6. 范围边界（交付时逐条核对）

1. **不放行任何参数**：`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER` / `ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 维持 `_PLACEHOLDER`，`low/base/high` 维持 `null`；**阈值审定 ≠ 参数放行**（IND L330）。
2. **不解 `OPEN-6`**，**不解除 `BLOCKED-6a` / `6b` / `6c` 任何一条**（本工位只补 H4 这一份额；`6a` 另有 H2/H8、`6b`/`6c` 归属他人）。
3. **不触发任何 falsifier / 情景切换 / 校准边界 / I-11-C 反方检验**（ACCT L230 + IND L299）。
4. **不改 `threshold_basis` 已有值**（`professional_judgement_required` 原样保留）；**不升级 `threshold_review_status`**（见 §3）。
5. **不产生 `I-11-B` 的 ACCEPT**；**不代签行业面会签**；不写五份计划文件；不改 `OPEN6-TOLERANCE-*` 与两半区裁定任一字节。
6. **写入面 = 本目录五件**；封盘 `I-11-A` 零字节改动；`.planning` 之外零写入；零 git 写；**禁用 `git status`**；禁网。

---

## 7. 交付物之间的关系

```
oracle.md（本文件：冻结 R1–R4 + blocked 条件 + decision-sha256/v1 + status 处置 + 变异清单 + 边界）
   └── h4_four_req.json（逐要件结论 + 证据 + preimage 全文 + 写入前后两次求值）
         └── hypotheses_h4_v1.json（追加式新版本：仅下标 3 改，supersedes_sha256 → f2178768…）
               └── ruling_h4.md（§①授权 · §②四步 · §③逐件复核实测 · §④②③④怎么补 · §⑤红绿变异 rc · §⑥不授予 · §⑦给行业面的会签提请）
                     └── handoff.json（role / authorized_by / h4_four_req_status / threshold_review_status 说明 / releases_nothing / written_files / git_diff_non_planning）
```
