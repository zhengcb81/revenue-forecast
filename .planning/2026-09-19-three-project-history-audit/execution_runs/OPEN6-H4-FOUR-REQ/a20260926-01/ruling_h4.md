# `H4` 阈值「给数四要件」补齐裁定 —— 会计 / 披露 reviewer（非实现者）

- 工位：`accounting_reviewer_h4` · 卡：`I-11-A` · 阈值对象：`H-CN-ZIJIN-PLAN-04` 的 `falsifier.threshold` = `实际产量 ÷ 计划产量 ∈ [0.9, 1.1]`
- 被审 attempt（**全程只读**）：`execution_runs/I-11-A/a20260919-01`
- 本载体（**新建**）：`execution_runs/OPEN6-H4-FOUR-REQ/a20260926-01/`（五件：`oracle.md` · `h4_four_req.json` · `hypotheses_h4_v1.json` · `ruling_h4.md` · `handoff.json`）
- `oracle.md` 先冻结后执行（sha256 `5b66584f5b4b89ef5fc8fc2311b32da2e11b606fcdc076ff0c9399912d534f0d`，19,032 B）
- 取证窗口（UTC）：`2026-09-26T10:25:42Z`；**网络请求 0 次**；**零 git 写**；**未执行 `git status`**；`.planning` 之外**零写入**

---

## ① 授权与身份（逐字，不由转述代替）

### 1.1 我是谁

| 项 | 值 |
|---|---|
| `role` | `accounting_reviewer_h4`（会计 / 披露 reviewer） |
| 是否实现者 | **否**。我未参与 `I-11-A` 任何实现步骤；`handoff.implementer_signed = false`；**不代签**行业面会签与任何其他角色 |
| 写入面 | 仅本目录五件；封盘 `I-11-A` **零字节改动**；五份计划文件**未写**；`OPEN6-TOLERANCE-*`、两半区裁定**未改任一字节** |

### 1.2 授权链（逐字）

1. **`I11A-OPEN-IND/a20260924-01/ruling.md` L299**（本工位确认权的来源，sha `8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b`）：

   > 「**放行条件**：本条仅为**行业面审定**；是否可标 `threshold_basis` 升级、以什么基础允许给数，**由 `I11A-OPEN-ACCT` 依其基础规则确认**，在此之前 I-11-B/I-11-C 不得据此触发。」

2. **`I11A-OPEN-MERGE/a20260924-01/merge_ruling.md` §3.2**（sha `2d214bab861be4ff30ebb7118705d23183fb2eec3e58f987d52287d0bab2e5c1`）：

   > 「### 3.2 易误读点 (a)：行业面给了 **H4 = [0.90, 1.10]** —— 这等于该命题 `approved_frozen` 吗？」
   > 「**结论：四要件 1/4 满足 ⇒ 不齐 ⇒ 按 ACCT L226 一律维持 `not_reviewed`**（该字段本身尚未落地 = BLOCKED-6c，`ACCT ruling.md` L298）⇒ 按 A-6.1（L230）该阈值**不得触发任何自动动作**。」

3. **判据定义**：`I11A-OPEN-ACCT/a20260924-01/ruling.md` **L226**（sha `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2`）逐字：

   > 「审定一个阈值必须同时具备**可复算观测量 + 可核基础 + 非实现者签署（decision_sha256） + 追加式版本化**，否则一律维持 `not_reviewed`」

   细则 = 同文件 **A-6.3 L248–L256**；fail-closed = **A-6.1 L230**；恢复规则 = **L284**。

4. **C5 派单原文**：`I11A-OPEN-MERGE/a20260924-01/handoff.json` **L122**（sha `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878`）：

   > 「OPEN-6：threshold_review_status 落地 + **H4 四要件补齐** + H2 基准 + 恒等式容差对照表」

⇒ **我 = 上述授权链所指的会计面确认方；我只就 `H4` 一个阈值的四要件出具本裁定。**

> **不采信转述**：本文件所有结论均由我回源自测（原文字段、原文抽取件、两份 PDF、校验器源码），不引用 `merge_ruling` 的 1/4 结论作为证据——它是**被复核对象**，不是依据。我自己跑出的基线恰为 `1/4`（§5 `B0`），与之独立吻合。

---

## ② 四步执行记录

| 步 | 动作 | 结果 |
|---|---|---|
| 1 | **逐件复核四要件**（回源自测，不用转述） | ① = ✅ 在（封盘字段原样可读）；②③④ = ❌ 缺（见 §3 各条实测） |
| 2 | **补齐 ②③④** | ② 落 **A-6.3 (iv) `expert_assumption` + 敏感性区间 + 显式「非等同披露依据」**；③ 落**非实现者 `decision_sha256`**（写入前/后各复算一次）；④ 落**追加式新版本 `hypotheses_h4_v1.json`**（`supersedes_sha256 → f2178768…`，封盘零字节改动）⇒ **四要件 4/4** |
| 3 | **跑校验器** | 封盘校验器 `validate()`（sha `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac`）：封盘原件 `errors = 0`、`hypotheses_h4_v1.json` **`errors = 0`**；另用 `BLOCKED6C …/iso_patched/tools/validate_hypotheses.py` 交叉复跑：两份均 `errors = 0`（只调 `validate()`，不跑 `main()`，零 `__pycache__` 落封盘） |
| 4 | **红 / 绿 / 变异** | 见 §5，`OVERALL rc = 0`（7/7 期望全部命中） |

**是否触发 fail-closed：未触发**（四要件判齐，无需判 `blocked`）。fail-closed 的**反向**仍在工作：§5 的 `B0/M1/M2/M3` 四个红分支全部 `rc ≠ 0`，`M4/M5` 证明判据**没有被改弱**。

---

## ③ 四要件逐条结论（我自己回源测的）

### 3.1 要件① 可复算观测量 —— **✅ 满足（原本就在，我没动它）**

封盘 `hypotheses.json` 下标 `3`（我逐字读原文，非转述）：

| 字段 | 逐字 |
|---|---|
| `falsifier.observable` | 「FY2026 实际披露：年报产销量表矿产金/矿产铜的实际产量与销售量，对照计划值 105 吨/120 万吨」 |
| `falsifier.source_route` | 「CN-ZIJIN-AR2025 → 管理层讨论与分析 → 2026年计划及展望 → 经营计划；实现值取自同一发行人 FY2026 年报产销量情况分析表」 |
| `falsifier.observation_date` | 「FY2026 年报披露日（预计2027-03前后）；半年报可用于方向核对但不得替代年度口径」 |
| `falsifier.threshold` / `threshold_basis` | 「实际产量 ÷ 计划产量 落在 [0.9, 1.1] 之外即视为计划显著偏离（阈值依据：professional_judgement_required）」 / `professional_judgement_required` |
| `source.doc_sha256` / `anchor_text` | `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d` /「2026年公司主要矿产品产量计划」 |

⇒ 观测量**指向具体披露表**、`source_route` 可定位、滞后明确、阈值与基础类型齐备；封盘校验器对本条**未报** `E_MISSING_FALSIFIER` / `E_OBSERVATION_DATE_UNRESOLVED`。**（merge_ruling 判 ✅ 我独立复核后同意，但结论是我自己得出的。）**

> **⚠️ 附带实测（不改变①的判定，但必须随本件传播）**：`observable` 指定的「产销量情况分析表」与年报正文 MD&A 的 FY2025 矿产铜口径**不一致**（见 3.2 的 `single_period_probe`）。两个数字都能从原文复算 ⇒ A-6.3 第1条的「可定位/可复算」仍成立；但**判哪个数字会改变结论**，故列为**会签提请事项 #1**。

### 3.2 要件② 可核基础 —— **❌ → ✅ 补齐（落 A-6.3 第2条第 (iv) 类）**

**先按 `oracle §1 R2` 的四类判定树逐类实测（判定树先冻结，后取证）：**

| 类 | 盘上实测 | 结论 |
|---|---|---|
| (i) 来源自身披露容差/定义 | 对 FY2025 年报全文抽取件 `CN-ZIJIN-2025.txt`（sha `196f2c5419fe7d67d50e1b6a13da641e225be515be46aeb53af2b203fe423591`，763,644 B）检索 `达成率\|±\s*10\s*%?\|偏差.{0,6}10` ⇒ **0 命中**；原文只有定性免责句「本计划为指导性指标，存在不确定性，不构成对产量实现的承诺」 | ❌ 不可用 |
| (ii) 同口径历史离散（≥2 可比披露期，计算与原文一并归档） | 可配对期数 = **1 < 2**：FY2025 计划（紫金 FY2024 年报 leaf 55「2025 年公司主要矿产品产量计划：矿产铜 115 万吨、矿产金 85 吨」）+ FY2025 实际（FY2025 年报）⇒ 唯一一对；FY2026 实际**尚未披露**（`observation_date` 2027-03 前后）；FY2024 计划需 FY2023 年报，**盘上不存在**（`company-wiki/…/annual/` 只有 2024、2025 两份年报） | ❌ 不可用（**单点无「离散」可算**） |
| (iii) 准则/监管/交易所明文 | 同一检索 **0 命中**；盘上无任何对「产量计划达成率容差」的明文定义 | ❌ 不可用 |
| (iv) 专家假设 | A-6.3 L253 逐字允许，**但必须标 `expert_assumption` + 给出敏感性区间 + 永远不得记为等同披露依据** | ✅ **采用** |

**补齐动作（三小项全给）：**

1. **`expert_assumption = true`**：写入 `hypotheses_h4_v1.json → [3].threshold_review.basis.expert_assumption`；数值来源逐字登记为 `I11A-OPEN-IND/ruling.md L288/L296` 的矿业面 `professional_judgement` 给数（0.90–1.10）。
2. **敏感性区间**：主档 `[0.9, 1.1]`；**外档 `[0.85, 1.15]`**（更宽：计划明显失真时可能漏检）；**内档 `[0.95, 1.05]`**（更严：爬坡年/并表年/长周期检修年更易被误判为计划失真）。两档均为 reviewer 声明，**不是披露依据**。
3. **`equivalent_to_disclosure_basis = false`**：显式写入，永久禁止把该阈值记为「等同披露依据」。

**同时如实登记一处反面实测（信息性，明确不作为 (ii) 的基础）——`single_period_probe`：**

| 口径 | FY2025 实际（我从原文取） | 矿产铜 比值 | 矿产金 比值 | 是否落带内 |
|---|---|---|---|---|
| 计划（FY2024 年报 leaf 55） | — | 1,150,000 t | 85,000 kg | — |
| A：FY2025 年报 **②产销量情况分析表**（「本表不含非控股企业相关数据」） | 矿山产铜 `878,180` 吨、矿山产金 `82,743` 千克 | **0.763635** | 0.973447 | 铜 **带外** / 金 带内 |
| B：FY2025 年报 **MD&A**（L2880 矿山产铜 `1,085,126` 吨；L3310 矿产金 90 吨、矿产铜 109 万吨） | 同期同指标 | **0.943588** | 1.058824 | 铜 带内 / 金 带内 |

⇒ **同一期、同一指标、两个披露口径给出相反结论**（0.763635 在 `[0.9,1.1]` 之外、0.943588 在之内）；**差异成因我未取证**（未做口径桥），据实登记为**会签提请事项 #1**，**不得**用任一口径宣称「历史离散支持 ±10%」。这正是 (ii) 不可用的第二重理由。

> **被拒的替代方案**：把行业面叙述「通常视为计划基本达成」直接当作基础 —— 那不是四类中的任何一类（这正是 `merge_ruling L284` 对行业面的批评点）；为凑 4/4 而把 (iv) 谎报成 (i)/(ii)/(iii)。

### 3.3 要件③ 非实现者签署 + `decision_sha256` —— **❌ → ✅ 补齐**

| 项 | 值 |
|---|---|
| 签署人 | `accounting_reviewer_h4`（会计 / 披露 reviewer，**非实现者**；`is_implementer = false`；命中 `IMPLEMENTER_MARKERS` = 无） |
| 日期 | `2026-09-26T10:25:42Z` |
| 作用域 | `hypothesis_id = H-CN-ZIJIN-PLAN-04`；`parameter_id = ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER`（**仅登记作用域，不放行**） |
| 落点 | `hypotheses_h4_v1.json → [3].decision.decision_sha256`（裁前 `null` → 裁后非空），同值另见 `[3].threshold_review.signer.decision_sha256` 与 `h4_four_req.json` |

**谁该签（回源）**：A-6.3 第3条逐字「签署身份：**非实现者（本卡为会计/行业 reviewer）**，裁定记录带 `decision_sha256`、日期、作用域」。行业面已按 `IND L288` 给数并按 `IND L299` 把「以什么基础允许给数」**留给我方**确认 ⇒ 本条由**会计面（我）**签，**不是**实现者，**也不代签**行业面会签。

**`decision.decision` 与 `state` 为什么不动**：封盘校验器 L233–L237 逐字 —— `threshold_basis=professional_judgement_required` 的命题**必须**保持 `state = pending_professional_decision`，否则报 `E_THRESHOLD_BASIS_INCONSISTENT`。故 `state` 与 `decision.decision`（命题层面的「情景权重」待裁问题）**保持原样**；本 sha 的作用域**只有阈值四要件**，不是命题批准，**不构成 `approved_frozen`**、**不产生 I-11-B 的 ACCEPT**（与 `OPEN2-C2-REGISTRATION` 在下标 1/2 写 sha 但 `decision= pending` 的既有形态一致）。

### 3.4 要件④ 追加式版本化 —— **❌ → ✅ 补齐**

| 检查 | 实测 |
|---|---|
| 新版本文件 | `hypotheses_h4_v1.json`，顶层与封盘**同形的 8 元素 JSON 数组**，UTF-8 无 BOM、CR=0、LF 尾随（sha `329a719beb9e6ce2bdecdfdde7c6bc6db9e3e1c7e4f36f7fb982cdf81e109717`，54,592 B） |
| `provenance` 落点 | `[3].provenance`（顶层是数组 ⇒ 沿用 `I11A-HYP-APPROVE` / `OPEN2-C2-REGISTRATION` / `HYPOTHESES-V4-MERGE` 三处先例，把版本记录挂在被改条目上） |
| `supersedes_sha256` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（**封盘原件**） |
| `modified_indices` / `unchanged_indices` | `[3]` / `[0,1,2,4,5,6,7]` —— 后 7 条我逐条规范化 JSON 比对，**全部与封盘相等**；下标 3 **确已改变**（不是「旧版本冒充新版本」） |
| 旧版本保留 | 封盘 `hypotheses.json` 收尾复算 sha **仍为 `f2178768…`**（一个字节没动）⇒ 旧阈值与旧版本保留供 I-12 评分，**不回改历史** |
| 分支说明 | 本版本以**封盘原件**为基线（按派单要求 `supersedes_sha256` 指向封盘），**不携带** `hypotheses_v2/v3/v4` 的改动；`v2/v3/v4` 与本分支的裁并归**编排层**，本工位不做裁并 |

---

## ④ `decision_sha256` 全值与求值方式（写入前后各复算一次）

**求值方式（`decision-sha256/v1`，与同角色同轮先例 `OPEN6B-TOLERANCE-RULING` 同形态）：**

```
preimage = utf8( json.dumps(pre, sort_keys=True, ensure_ascii=False, separators=(',',':')) )
decision_sha256 = sha256(preimage) 的小写十六进制
```

`pre` 的键集合在 `oracle §2` **先冻结**：`schema` · `role` · `carrier` · `action` · `authorized_by{ind_l299, merge_ruling_3_2, c5}` · `scope{hypothesis_id, threshold, parameter_ids}` · `four_requirements{r1..r4}` · `basis_class` · `expert_assumption_marked` · `sensitivity_interval` · `equivalent_to_disclosure_basis` · `sealed_original_sha256` · `new_version_file` · `threshold_review_status_effective` · `releases_nothing` · `signed_by` · `signed_at_utc`。

**preimage 全文（canonical，1,472 字节）逐字存于 `h4_four_req.json → decision_preimage_canonical`。**

```
9d2d38450d8fa8f1423a695628b6fbacf91eecc5b4796d3fa7fb621fd147e1c9
```

| 复算 | 值 | 结果 |
|---|---|---|
| **写入前**（生成 `hypotheses_h4_v1.json` 之前） | `9d2d38450d8fa8f1423a695628b6fbacf91eecc5b4796d3fa7fb621fd147e1c9` | — |
| **写入后**（从 `h4_four_req.json → decision_preimage_canonical` 重新提取再算） | `9d2d38450d8fa8f1423a695628b6fbacf91eecc5b4796d3fa7fb621fd147e1c9` | **`two_pass_match = true`** |

三处同值：`hypotheses_h4_v1.json → [3].decision.decision_sha256`、`→ [3].threshold_review.signer.decision_sha256`、`h4_four_req.json → decision_sha256`。

**任何人可重跑**：读 `h4_four_req.json` 取 `decision_preimage_canonical` → 算 SHA-256 → 应等于上值。

---

## ⑤ 红 / 绿 / 变异（`oracle §5` 冻结清单，脚本经 stdin 内联执行、**不落盘**）

`OVERALL rc = 0`（7/7 期望全部命中；`rc ≠ 0` 才是不合格）。

| id | 变异 / 分支 | 实测判定 | 期望 | 命中 | rc |
|---|---|---|---|---|---|
| **G1** | **绿**：本工位 `hypotheses_h4_v1.json` 判四要件 | **4/4** | 4/4 | ✅ | 0 |
| **B0** | **基线红分支**：对**封盘原件**下标 3 判四要件（无审定记录、`decision_sha256 = null`、无新版本） | **1/4**（缺 R2/R3/R4） | 不是 4/4 | ✅ | 0 |
| **M1** | **四要件缺一**：把 `threshold_review.basis.basis_class` 清空 | **3/4**（缺 R2） | 不是 4/4 | ✅ | 0 |
| **M2** | **`decision_sha256` 换值**：末位十六进制改写 | **3/4**（缺 R3，preimage 复算不符） | 不是 4/4 | ✅ | 0 |
| **M3** | **新版本改成旧版本**：下标 3 换回封盘原字节，`provenance` 仍谎报 `modified_indices=[3]` | **1/4**（缺 R2/R3/R4） | 不是 4/4 | ✅ | 0 |
| **M4** | **判据改弱（方向性红）**：R2 改成「有叙述性理由即可，不分类、不要求 `expert_assumption` 标注与敏感性」，喂**只有行业叙述、无四类归类**的记录 | **弱判据 4/4** ∧ **强判据 3/4** | 弱必须放行、强必须拒绝 | ✅ 检出 | 0 |
| **M5** | **判据改弱（方向性红）**：R3 改成「`decision_sha256` 非空即算签署」（不复算 preimage），喂 `0000…`（64 位）假 sha | **弱判据 4/4** ∧ **强判据 3/4** | 弱必须放行、强必须拒绝 | ✅ 检出 | 0 |

补充说明（预先声明，防止事后找补）：

- **`B0 = 1/4` 是我自己跑出来的基线**，与 `merge_ruling §3.2` 独立登记的「1/4」吻合 —— 这是**交叉验证**，不是引用。
- **M4/M5 的意义**：判据**被改弱后，一个不该被审定的阈值确实能通过**（弱判据给出 4/4），而本判据拒绝它 ⇒ 判别力双向成立。
- **判 `blocked` 的分支也要红**：`B0`、`M1`、`M2`、`M3` 即全部「四要件不齐」分支，`rc` 全部 ≠ 0。

**校验器（第 3 步，只调 `validate()`，`-B` + `PYTHONDONTWRITEBYTECODE=1`）：**

| 对象 | 封盘校验器 `cb49360d…` | `BLOCKED6C iso_patched` 校验器 `1085368e…` |
|---|---|---|
| 封盘 `hypotheses.json`（对照） | **`errors = 0`** | **`errors = 0`** |
| `hypotheses_h4_v1.json` | **`errors = 0`** | **`errors = 0`** |

交叉校验器另返回（**机器口径的 fail-closed 证据**）：`threshold_reviewability(H4)` = `{"threshold_review_status_present": true, "raw": "not_reviewed", "effective": "not_reviewed", "state": "pending_professional_decision", "usable": false, "reasons": ["judgement_not_reviewed"]}` ⇒ **该阈值在机器口径下仍不可用于判定**。

---

## ⑥ `threshold_review_status` 与各 `BLOCKED` 的处置（逐条）

| 项 | 结论 | 理由 |
|---|---|---|
| **`threshold_review_status`** | **仍 `not_reviewed`**（两侧一致） | ① **权威封盘文件根本没有这个字段**（我实测 8 条全无）⇒ 有效值 = 默认 `not_reviewed`；② 本工位新版本**显式写 `not_reviewed`**（追加字段、fail-closed），**不升级为 `reviewed`** |
| 为什么四要件 4/4 了还不升 | A-6.3（L246）逐字是「必须**同时**满足，**缺一即维持** `not_reviewed`」——**必要条件**句式：补齐四要件**解除的是「被强制维持」**，不等于状态字段被自动升级 | 升级 = schema 落地 + 行业面会签之后的**独立动作**，不在本工位写入面与授权内 |
| 三条升级障碍（逐条） | (a) 派单明令**不解除 `BLOCKED-6c`**，而该字段的落地实现与校验器改动按 `ACCT L298` 归 **I-11-A 实现者/编排层/schema 侧**；(b) `IND L299` 的另一半——**行业面会签**——按派单「另议」，我**不代签**；(c) 派单禁止本工位**触发任何自动动作**，而把状态升为 `reviewed` 正是打开 A-6.1 下游触发门的开关 | fail-closed：**宁可记为未审定，也不产生一个「看起来已解锁」的状态** |
| 机器后果 | A-6.1（L230）触发门**两侧都关闭**；交叉校验器返回 `usable=false` | 未触发任何 falsifier / 情景切换 / 校准边界 / I-11-C 反方检验 |
| **`BLOCKED-6a`** | **`still_blocked`（未解除）** | 3 条 pjr 阈值中 **H2（IND 拒给数）、H8（两修订未按 A-6.3 签署）仍未签**；我补的只是 **H4 这一份额**，不构成 6a 整体解除 |
| **`BLOCKED-6b`** | **未触碰** | 属 `OPEN6B-TOLERANCE-RULING`，我未改其任一字节 |
| **`BLOCKED-6c`** | **未解除** | 我**没有**改任何校验器、**没有**代落地 schema；只在自己的新版本里显式记 `not_reviewed` |
| **`OPEN-6`** | **未解** | C5 四个子项中我只做「H4 四要件」，另三项（`threshold_review_status` 落地 / H2 基准 / 容差对照表）分别归实现者与他人 |
| **`OPEN-6-TOLERANCE-*` / 两半区裁定** | **一字节未改** | 写入面只有本目录五件 |

---

## ⑦ 本裁定**不授予**什么（逐条，fail-closed）

1. **不放行任何参数**：`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER` 维持 `_PLACEHOLDER`，`low/base/high` 维持 `null`。**阈值审定 ≠ 参数放行**（`IND L330` 逐字）。
2. **不触发任何动作**：falsifier 触发、情景切换、校准边界、I-11-C 反方检验——**一个都没触发**，也不使能（状态仍 `not_reviewed`，A-6.1 门保持关闭）。
3. **不解任何 `BLOCKED`**：`OPEN-6` 与 `BLOCKED-6a/6b/6c` 全部原样；`OPEN-2/3/5/11` 不涉及。
4. **不改 `threshold_basis` 已有值**：仍是 `professional_judgement_required`（四类归类写在**新版本的追加字段**里，不占 `threshold_basis` 的闭集）。
5. **不产生 `I-11-B` 的 ACCEPT**、**不产生命题 `approved_frozen`**（`state`、`decision.decision` 均未动）。
6. **不代签行业面会签**、**不声称 I-11-A 验收**（`does_not_claim_I11A_acceptance = true`）。
7. **不写五份计划文件**；不改 `OPEN6-TOLERANCE-TABLE` / `OPEN6B-TOLERANCE-RULING` / `I11A-OPEN-ACCT` / `I11A-OPEN-IND` / `I11A-OPEN-MERGE` 任一字节；封盘 `I-11-A` 零字节改动。
8. **零 git 写、零 `git status`、零联网、`.planning` 之外零写入**（`company-wiki` 两份 PDF 仅只读打开与哈希）。

---

## ⑧ 给行业面的会签提请（`I11A-OPEN-IND`，**本工位不代签**）

> 会计面已按 `IND L299` 完成「以什么基础允许给数」的确认：**A-6.3 (iv) `expert_assumption` + 敏感性区间**，四要件 **4/4**，非实现者 `decision_sha256` 已出具。**以下事项请行业面复核并会签**（未会签前状态维持 `not_reviewed`，不得据此触发）：

1. **口径必须先统一（最高优先）**：`observable` 指定的「②产销量情况分析表」口径（FY2025 矿山产铜 `878,180` 吨）与 MD&A 口径（`1,085,126` 吨 / 109 万吨）对同一年算出的达成率**一个带外（0.763635）、一个带内（0.943588）**。请明确 H4 用哪一张表、并在 `source_route` 中锁定；差异成因（口径桥）本工位未取证。
2. **敏感性档位确认**：外档 `[0.85,1.15]`、内档 `[0.95,1.05]` 的取法与后果（漏检 / 假阳性）是否接受。
3. **`revert_rule` 的豁免分支**（`IND L298` 行业面自己提的反例）：新项目爬坡年、重大并购并表年、不可抗力/长周期检修年的**豁免分支**尚未写入 `falsifier.revert_rule`（封盘原文无此分支）。本工位**不回改**封盘字段；请在**新版本**中补。
4. **计划值本身的口径**：`IND L323` 反例（计划含「区间指引」或爬坡年特殊口径 ⇒ 双侧对称假设需改单侧/公司自定义区间）待出现该披露时复核。
5. **会签落点**：会签记录请以**新 attempt + 新版本 + `decision_sha256`** 追加，**不得**就地改本文件或封盘；会签通过后，`threshold_review_status` 由**有权方**（实现者/schema owner，`BLOCKED-6c`）落地升级，本工位的 `decision_sha256` 与 `h4_four_req.json` 是其输入。

---

## ⑨ 边界与恢复规则

1. **写入面 = 五件**，全在 `execution_runs/OPEN6-H4-FOUR-REQ/a20260926-01/`；`git -c core.quotepath=false diff HEAD --name-only` 共 **3830** 条、**非 `.planning` 条目 = 0**（**未执行 `git status`**）。
2. **只动一条命题**：`hypotheses_h4_v1.json` 只有下标 `3` 被改（`falsifier.threshold_review_status` 追加、`decision.decision_sha256` 由 `null` → sha、`threshold_review` 追加、`provenance` 追加）；下标 `0/1/2/4/5/6/7` 逐条规范化 JSON 比对与封盘**相等**。
3. **恢复规则（追加式，不回改）**：新证据（口径裁定、爬坡豁免分支、owner 改判 A-6.3、行业面会签）⇒ 在**本目录追加** `ruling_h4_r2.md` + 新 `hypotheses_h4_v2.json`，标 `supersedes` 链；**不修改** `oracle.md`（判据冻结件）、`h4_four_req.json`、`hypotheses_h4_v1.json`、封盘任何字节。
4. **`oracle.md` 冻结后未回改**：本文件交付时其 sha256 与冻结时一致（`5b66584f5b4b89ef5fc8fc2311b32da2e11b606fcdc076ff0c9399912d534f0d`，19,032 B）。
