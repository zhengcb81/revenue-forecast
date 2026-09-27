# OPEN6-H2 · 「`OPEN-2` 口径 + 价格归一化基准」 —— 矿业行业 reviewer **oracle（先冻结，后裁定）**

- 工位角色：`mining_industry_reviewer_h2`（矿业行业 reviewer + 会计面会签提请对象，**非实现者**）
- 唯一写入面（新建）：`.planning/2026-09-19-three-project-history-audit/execution_runs/OPEN6H2-PRICE-NORMALIZATION-BASELINE/a20260926-01/`
- 裁定对象：`H2`（= `H-CN-ZIJIN-SEG-02` 的 `falsifier.threshold`「相对偏离 ±5%」）
- 冻结时点（UTC）：`2026-09-26T10:50:54Z` —— **本文件先写、先算 sha256，之后才跑判据脚本与裁定**
- 纪律：**禁网**（全部证据取自盘上语料）· **禁 git 写** · **禁 `git status`** · `OPEN2-*` / `HYPOTHESES-V4-MERGE` / 两半区裁定 / `OPEN6-TOLERANCE-*` / `BLOCKED6C-*` **一律只读**（一个字节不改）· 不写 `.planning` 之外任何文件（含 `company-wiki`：只读 + `pdftotext … -` 进管道）

---

## ① 授权（逐字，逐条自算字节区；不采信他人登记的 sha）

| 授权点 | 逐字原文 | 出处（本工位自算 sha256 / 字节区） |
|---|---|---|
| **任务定义 L234** | `\| **H2 ±5%** \| OPEN-2 口径裁定 + 价格归一化基准（价格序列/期间/净价口径） \| 矿业 reviewer + 会计面（IND L373 BLOCKED-6；ACCT BLOCKED-6a） \|` | `I11A-OPEN-MERGE/a20260924-01/merge_ruling.md` **L234**，sha256 `2d214bab861be4ff30ebb7118705d23183fb2eec3e58f987d52287d0bab2e5c1`（49,062 B） |
| **H2 现状 L217** | `- **L291**（H2 行）：「\| **H2** \| 单位收入 ±5% \| ❌ **不采用占位值；替代数值 `BLOCKED`** \| — \| `BLOCKED` \|」` | 同文件 **L217** |
| **待办点名 L330 第 5 条** | `5. **OPEN-6**：…；H4 补齐四要件后由会计面确认；H2 补 OPEN-2 口径 + 价格归一化基准；4 条恒等式容差对照表（BLOCKED-6b）。` | 同文件 **L330** |
| **IND H2 行 L291** | `\| **H2** \| 单位收入 ±5% \| ❌ **不采用占位值；替代数值 `BLOCKED`** \| — \| `BLOCKED` \|` | `I11A-OPEN-IND/a20260924-01/ruling.md` **L291**，sha256 `8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b`（39,207 B） |
| **IND 不给数理由 L301-L306** | `1. **观测量口径未定**：observable = "分部收入 ÷ **铜当量销售量**"（\`hypotheses.json:195\`），而分母依赖 OPEN-2 中尚未裁定来源的系数 ⇒ 阈值在口径未定前**没有定义**；… 3. 价格归一化所需的**基准（用哪条价格序列、哪个期间、是否 TC/RC 净价）**本工位没有可核依据 ⇒ 给数即"看起来完成"。 ⇒ **替代数值 \`BLOCKED\`**（缺：OPEN-2 口径裁定 + 价格归一化基准）。` | 同文件 **L301–L306** |
| **IND 反例 L307** | `- **反例**（会让我改判接受 ±5%）：若用本地可核的历史序列证明该 observable 在**价格中性年份**的历史波动确实 ≤5%，则 ±5% 可恢复为可审定值。` | 同文件 **L307** |
| **IND 口径联动 L111** | `- OPEN-6 的 H2 阈值 observable 定义（口径变 ⇒ 观测量变）；` | 同文件 **L111** |
| **IND L331** | `- I-11-B：H2 阈值未定 ⇒ \`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027\` 的 falsifier 不可执行（与 OPEN-2 联动）；` | 同文件 **L331** |
| **IND 被拒替代 L345** | `- 为"凑齐三条 pjr"而强行给 H2 一个数字（无口径、无基准 ⇒ 违反 fail-closed）；` | 同文件 **L345** |
| **IND BLOCKED-6 L373** | `\| **BLOCKED-6** \| OPEN-6：H2 单位收入阈值的**替代数值**（±5% 不采用） \| OPEN-2 口径裁定 + 价格归一化基准（价格序列/期间/净价口径） \| 矿业 reviewer + 会计面；**保持 \`professional_judgement_required\` 未审定** \|` | 同文件 **L373** |
| **ACCT BLOCKED-6a L296** | `- **BLOCKED-6a**：3 条 \`professional_judgement_required\` 阈值的**数值**是否恰当（±5%、[0.9,1.1]、拆分层级判定）—— 需行业/专业 reviewer 按 A-6.3 给出证据与签署；我**不给数**。` | `I11A-OPEN-ACCT/a20260924-01/ruling.md` **L296**，sha256 `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2`（37,355 B） |
| **ACCT A-6.3（给数前置）L244–L256** | `必须**同时**满足，缺一即维持 not_reviewed：1. **观测量可复算**…；2. **数值有可核基础**，且属于以下之一并写明：(i) 来源自身的披露容差/定义…(ii) **同口径历史离散**…(iii) 准则/监管/交易所明文定义…(iv) **专家假设**：允许，但必须标 \`expert_assumption\` 并给出敏感性区间…；3. **签署身份**：非实现者…带 \`decision_sha256\`、日期、作用域（\`hypothesis_id\` + \`parameter_id\`）；4. **追加式版本化**…不回改**历史；5. **跨卡同步**…` | 同文件 **L244–L256** |
| **ACCT A-6.1（未审定禁令）L230** | `…\`threshold_basis=professional_judgement_required\` 且 \`threshold_review_status≠reviewed\` 的阈值**不得触发任何自动动作**（falsifier 触发、情景切换、校准边界、I-11-C 反方检验），只能作为"已登记的待审观察条件"…` | 同文件 **L230** |
| **ACCT OPEN-6 排序 L280** | `- **OPEN-2 交互**：命题 2 的 ±5% 观测量依赖铜当量分母 ⇒ 该条审定必须排在 OPEN-2 之后。` | 同文件 **L280** |
| **⭐ 前置已成立：OPEN-2 替代口径** | `两槽独立、禁止跨层相除`；`铜当量换算系数在任何路径中出现即判违例（factor_basis 必须为 none）` | `OPEN2-SUBSTITUTE-CALIBER/a20260925-01/ruling.md` **L59 / L160**（`substitute_caliber.json` sha256 `649a9ff8d1a4490aedbe863ee52a338ba7b30c50408d7ca5f0a9361daa622e72`；`ruling.md` sha256 `f927c44cacacb6d0db8e9d1cc09aa559d74427837fd885c4cd0081dbca899e53`） |
| **⭐ C2 注册已完成** | `registered_parameter_ids = [ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027, ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027]`；`8 条 falsifier … 整块逐字节相同（falsifier_full_unchanged = true）` | `OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（经 v4 继承）与 `registration.md` **L79** |
| **⭐ v4 合并** | `c1_preserved: true`、`c2_registration_preserved: true`、`falsifier 逐路径无差异` | `HYPOTHESES-V4-MERGE/a20260926-01/handoff.json` **L98/L101**、`merge_report.md` **L51**（`hypotheses_v4.json` sha256 `ebf6fa4e2f708c397165127926475d5426afbdef0d93864a795a8640029c4654`，68,565 B） |

> **本工位身份**：`L234` 逐字点名的**矿业 reviewer 半方**；同句「+ 会计面」与 `ACCT BLOCKED-6a` 是**另一步会签**，本工位**只提请、不代签**。

---

## ② 判据 A —— 口径锚点（`anchor ∈ {anchor_new_id, anchor_old_id, requires_redefinition}`）

**判定规则（先冻结）**：

| # | 条件（全部本地可核） | 满足 ⇒ |
|---|---|---|
| **A-1 因子中性** | 锚点参数 `factor_basis = none`，任何路径不得出现铜当量换算系数（`OPEN2-SUBSTITUTE-CALIBER` ruling **L160**「铜当量换算系数在任何路径中出现即判违例」） | 允许作锚 |
| **A-2 同表同注、禁跨层相除** | 锚点 `unit_basis = disclosed_same_table_pairing`；observable **不得**是「分部对外收入 ÷ 分金属销量 / 铜当量销量」这类跨层相除（ruling **L59/L73**、`RED_B`） | 允许作锚 |
| **A-3 口径变 ⇒ 观测量变**（IND **L111**） | 若当前已注册 `falsifier.observable` 指向的口径已被替代口径取代（原铜当量口径），则该 observable **必须先被重定义**，且重定义须落在**命题新版本**（A-6.3 第 4 条追加式版本化）上 | 判 `requires_redefinition` |
| **A-4 现状核对** | 逐字读 `hypotheses_v4.json` 的 `falsifier.observable`：若仍为铜当量跨层相除句 ⇒ A-2 不满足 | 判 `requires_redefinition` |

**结论式（先冻结）**：

```
anchor = anchor_new_id   ⇔ A-1 ∧ A-2 成立 且 该 observable 已在已注册的新版本中重定义
anchor = anchor_old_id   ⇔ 旧铜当量口径仍被 OPEN-2 允许（factor_basis 可非 none）
anchor = requires_redefinition ⇔ 其余情况（含：新 id 合规但 observable 仍是旧句）
```

> **`requires_redefinition` 不是"判不了"**：它是三选一里的**确定答案**（可给证据、可给恢复规则）；但它同时意味着**当前 observable 不可执行** ⇒ 直接触发判据 C 的 `blocked`。

---

## ③ 判据 B —— 价格归一化基准四要素（**任一 `NOT_ESTABLISHED` 即 `blocked`**）

每个要素必须同时满足「**盘上定位**（文件 + 行号/leaf + 逐字引文 + 文件 sha256）」与该要素的**语义完备条件**；只找到"数字"不等于找到"基准"。

| 要素 | 语义完备条件（先冻结） | 判 `ESTABLISHED` 需要 |
|---|---|---|
| **B-1 价格序列** | 指定**一条**用于 H2 归一化的价格序列：金属 × 市场（伦敦/国内现货等）× 货币（美元/人民币）× 形态（年均价/年终价）；若含多币种须另有**汇率换算规则**；"盘上有 10 行可选"≠"已指派 1 条" | 有明确指派 + 该序列逐期数值可定位；无指派 / 币种规则缺 ⇒ `NOT_ESTABLISHED`（可另记 `price_rows_available=true` 子事实） |
| **B-2 期间** | (a) 基期窗口内**每一期**都有该序列的披露值（基期 = 新 id `base_period` = **FY2023–FY2025**）；(b) 观察期（`observation_date` = FY2027 年报）与基期的**期间对齐规则**（年均价 vs 年终价 vs 观察窗口）已写明 | (a)∧(b) 均可定位；任一缺 ⇒ `NOT_ESTABLISHED` |
| **B-3 净价口径** | 明确写出：该序列与被观察的实现单价（`单价（不含税）`）各自的 **VAT / TC-RC 加工费 / payability 应付比例 / 权益金 / 产品形态（精矿 vs 电解）** 折减状态，以及二者之间的**桥**；无桥 ⇒ 比值不可定义 | 原文或已签裁定给出桥；否则 ⇒ `NOT_ESTABLISHED`（**禁止**用常识或"spot 就是净价"代填） |
| **B-4 来源与取回时点** | 文件路径 + `content_sha256` + **取回 UTC**（`retrieved_at`）+ 来源 URL/提供方 | 三件齐（引文另附）⇒ `ESTABLISHED` |

**子事实登记规则**：找到"数据可得性"但缺"指派/对齐/桥"时，**记 `NOT_ESTABLISHED` + 子事实 `*_available=true`**；子事实**不得**用来升级要素结论（否则判据等于自破）。

---

## ④ 判据 C —— `blocked` 触发条件与给数门

### C.1 给数门（**全部**成立才允许 `h2_value ≠ null`）

```
GIVE ⇔  anchor ∈ {anchor_new_id, anchor_old_id}                  （判据 A）
     ∧  B-1 ∧ B-2 ∧ B-3 ∧ B-4 全部 ESTABLISHED                    （判据 B）
     ∧  A-6.3 四要件齐：
          (1) 可复算观测量（observable 已按 A-3 重定义并可定位 source_route/observation_date）
          (2) 数值有可核基础，属 (i)来源披露容差 (ii)同口径历史离散(≥2 期、过程归档)
              (iii)准则/监管明文 (iv)expert_assumption+敏感性区间 四类之一并写明
          (3) 非实现者签署 + decision_sha256 + 日期 + 作用域(hypothesis_id + parameter_id)
          (4) 追加式版本化（写入命题新版本，旧版本保留，不回改）
```

### C.2 `blocked` 触发（**任一**成立即触发，fail-closed）

- `T-1`：`anchor = requires_redefinition`（口径已变、observable 未重定义）；
- `T-2`：四要素中任一 `NOT_ESTABLISHED`；
- `T-3`：A-6.3 四要件缺任一件。

**触发后果（冻结，逐条）**：

1. `h2_value = null`、`h2_status = still_blocked`、`h2_decision_sha256 = null`（**不签署**）；
2. `threshold_basis = professional_judgement_required` **维持原值不动**；`threshold_review_status` 维持 **`not_reviewed`**；`professional_judgement_required` **保持未审定**；
3. **不放行任何参数**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027`、`ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027` 及 4 个新 id 的 `low/base/high` 全部保持 `null`；`_PLACEHOLDER` 维持；
4. **不解除** `ACCT BLOCKED-6a`、`IND BLOCKED-6`、`OPEN-6`、`OPEN-2` 任何一条；**不产生** `I-11-B` 的 ACCEPT；**不触发**任何 falsifier/校准边界（A-6.1 L230）；
5. **不代签会计面**（A-6.3 会签是另一步）。

### C.3 明文被拒的"给数"路径（IND **L345** / ACCT **L288**）

- ❌ 为凑齐三条 `pjr` 而强行给 H2 一个数字；
- ❌ 把 ±5% 直接当已审定值放行；
- ❌ 用"盘上有价格表"直接除一除得出阈值（跳过 B-3 净价桥 = 跨口径相除，等价于被拒的 `RED_B`）；
- ❌ 用 `expert_assumption` 兜底绕开 B-1/B-2/B-3 —— `A-6.3(iv)` 只对**"数值基础"**开放，**不对"观测量与基准未定义"开放**（口径/基准未定 ⇒ 观测量本身没有定义，专家假设无处安放）。

---

## ⑤ 变异清单（**先冻结，后跑**）

判据脚本 `judge(case, action, mode)`，`mode ∈ {STRICT, MUT_x}`；**rc = 0 接受 / 1 拒绝**。

| id | 变异（对 STRICT 的改弱） |
|---|---|
| `MUT-1` | 丢弃 **B-1（价格序列指派）** |
| `MUT-2` | 丢弃 **B-2（期间）** |
| `MUT-3` | 丢弃 **B-3（净价口径）** |
| `MUT-4` | 丢弃 **B-1 ∧ B-2 ∧ B-3**（只留 B-4 来源与取回时点） |
| `MUT-5` | 丢弃**判据 A（口径锚点）** |
| `MUT-6` | 丢弃 **A-6.3 第 (3)(4) 件（非实现者签署 + 追加式版本化）** |

**冻结的用例与期望 rc**：

| # | 用例 | action | mode | **期望 rc** | 意图 |
|---|---|---|---|---|---|
| 1 | `ACTUAL`（本次真实证据：A=`requires_redefinition`，B1/B2/B3 缺，B4 有） | `give` | STRICT | **1** | 判 blocked 的分支要红 |
| 2 | `ACTUAL` | `keep_blocked` | STRICT | **0** | 绿：正确结论被接受 |
| 3 | `CF-ANCHOR-FIXED`（反事实：observable 已按 A-3 重定义并签署版本化，四要素 = 本次实测） | `give` | STRICT | **1** | 隔离四要素门 |
| 4 | `CF-ANCHOR-FIXED` | `give` | `MUT-4` | **0** | **变异存活**：判据改弱后一个不该给数的阈值能通过 |
| 5 | `SYNTH-FULL`（合成对照样：A/B1–B4/A-6.3 全齐，字段标 `SYNTHETIC-*`） | `give` | STRICT | **0** | 绿：判据不为难，四要素齐即可给数 |
| 6 | `SYNTH-FULL` | `keep_blocked` | STRICT | **1** | 红：该给数时不许赖着 `blocked`（双向） |
| 7 | `SYNTH-MISS-B1`（仅 B-1 缺） | `give` | STRICT / `MUT-1` | **1 / 0** | B-1 承重 |
| 8 | `SYNTH-MISS-B2`（仅 B-2 缺） | `give` | STRICT / `MUT-2` | **1 / 0** | B-2 承重 |
| 9 | `SYNTH-MISS-B3`（仅 B-3 缺） | `give` | STRICT / `MUT-3` | **1 / 0** | B-3 承重 |
| 10 | `SYNTH-OLD-ANCHOR`（锚到旧铜当量 id，四要素齐） | `give` | STRICT / `MUT-5` | **1 / 0** | 判据 A 承重 |
| 11 | `SYNTH-NO-SIGN`（四要素齐但无非实现者签署/无新版本） | `give` | STRICT / `MUT-6` | **1 / 0** | A-6.3 第 3/4 件承重 |

```
EXPECT_RC = 0     （11 组期望逐条比对，全中 ⇒ 0）
OVERALL_RC = 1    （各用例 rc 按位或；含 1/3/6/7/8/9/10/11 的红例，预期 1）
```

> **合成样（`SYNTH-*`）只作判据夹具**，全部字段带 `SYNTHETIC-` 前缀、sha 用 `0…0`，**不构成任何现实主张**，不进入 `h2_baseline.json` 的证据表。

---

## ⑥ 冻结声明

1. 本文件写入后**不回改**；sha256 由本工位在**裁定前**算一次、**收尾**再算一次，两次同值才继续。
2. 判据 A/B/C 与变异清单**在读取"裁定结论"之前**已成文；裁定只做**套用**，不得新增/放宽/收紧判据。
3. 本 oracle **不授予任何东西**：不含阈值取值、不含参数放行、不改任何 `status`/`threshold_basis`。
4. 红绿双向义务：既要有"该 blocked 的确实红"（用例 1/3/6/…），也要有"改弱后不该给数的能通过"（用例 4/7–11 的 `MUT` 列）。
