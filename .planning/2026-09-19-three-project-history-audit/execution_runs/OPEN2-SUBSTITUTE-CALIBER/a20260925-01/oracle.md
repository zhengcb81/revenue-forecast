# oracle · OPEN-2 C2 第二分支『分部对外收入 + 分金属销量』替代口径裁定判据（先冻结，后跑）

- 工位：`execution_runs/OPEN2-SUBSTITUTE-CALIBER/a20260925-01`
- 角色：`industry_or_accounting_reviewer`（行业/会计专业 reviewer，**非实现者**）
- 被裁对象：`I11A-OPEN-MERGE/a20260924-01/handoff.json` 的 `i11b_unlock_conditions` 第 2 条（C2）**第二条分支**
- 被审/被引文件一律**只读**；本文件是本轮**判据冻结件**，任何后续更正以新文件追加，不回改本正文
- 冻结时点：写入本文件后立即计算 sha256 并记入 `ruling.md` §④，**之后**才允许跑 §6 的实测

---

## 1. 本轮要判哪几个问题（四个，不多判）

| # | 问题 | 判据（引用 §2 的编号） | 可判结论 |
|---|---|---|---|
| Q1 | 替代口径是否成立（好处/代价风险/与原命题关系/改哪条命题还是新增） | P1–P6；风险项 R1–R3 | 成立（附约束） / 不成立 |
| Q2 | 数据是否够：分部对外收入 FY2023/24/25 三年；分金属销量 铜/金/银/锌 三年 | P1 + A 组算术复算 | 逐项 `ESTABLISHED` / `NOT_ESTABLISHED` |
| Q3 | 新 `parameter_id` 怎么定（命名回源、单位、unit_basis、factor_basis、low/base/high、起止年份、dependency_control） | P2、P3、P4、P6 | 给出 id（含单位与标注） / `NOT_ESTABLISHED` |
| Q4 | 与两半区裁定是否冲突（绕开 vs 违反；有无被我违反的条文） | P1–P6 与 ACCT/IND 逐条对照 | 无冲突 / 有冲突（有冲突则按 fail-closed 判不成立） |

**不判**（行不交界，见 §5）：OPEN-2 本身的解除、任何参数/阈值放行、`_PLACEHOLDER` 解除、`BLOCKED-*` 关闭、I-11-B 的 ACCEPT、两半区已裁的铜当量系数取值。

---

## 2. 判据（STRICT，冻结）

记 `SUBSTITUTE_OK = P1 ∧ P2 ∧ P3 ∧ P4 ∧ P5 ∧ P6`。**六条全部满足才判『成立』；任一不满足即 fail-closed 判『不成立』**，不为凑解锁而放宽。

- **P1 单一发行人、同一报告期、原文披露、可定位**：收入侧与量侧的每一个数都必须来自公司自己同一报告期的定期报告原文，可定位到（`anchor_text` + 页/表），文件 `sha256` 已绑定，且至少有一条**非取文工具**的独立复核路径（算术闭环 / 跨报告同值）。第三方、同行均值、券商转述、记忆不满足 P1。
- **P2 单位即披露单位、零换算系数**：每个参数的 `unit` 必须是原文披露单位；`factor_basis` 必须为 `none`（**不得**出现任何铜当量/折算/换算系数）。出现系数 ⇒ 不成立。
- **P3 口径分层、禁止跨层相除**（**本判据的核心，也是变异靶点**）：`分部对外收入`（对外、抵销后、含矿产品分部**全部**产品：铜/金/锌/银/铅/锂/铁/钨/钼…）与 `分金属销量`（仅四金属、且表注"不含非控股企业"）**必须作为两个独立参数槽使用**；**禁止**用前者除以后者（或任何跨层合成）得到"单位收入/元每吨"。理由：分子分母在产品范围、抵销状态、并表范围三个维度都不同源（实测差额见 `substitute_caliber.json` 的 `scope_mismatch`），一旦相除即重新产生原命题"口径暴露二"的缺陷——只是不再有系数而已。
- **P4 单位经济学只能同表同注配对**：若 I-11-B 必须给"单位收入"，其分子分母必须取自**同一张表、同一条表注**（本卡语境：`按产品划分的销售详情`表的 单价/销售数量/金额 三列，两期同表、表注均为"本表不含非控股企业的相关数据"）；跨表跨口径相除不成立。
- **P5 双计排除**：收入路径只允许**一条**进入模型（分部对外收入路径 或 分产品量价路径），另一侧只能作对账/校验（`falsifier`）；两路同时进模型 ⇒ 不成立。
- **P6 落点与命名回源**：新 `parameter_id` 必须落到 `model_cards.md` 已注册的 `model_id`/`driver_name`（`decision.md` DEC-5，L125–L135），且满足 `validate_hypotheses.py` 的唯一性规则（一个 id 只能表示一条命题 × 一个 driver × 一个 `effective_period`，L197–L213）；命名沿用既有 id 的构词法（`ZIJIN` + 范围 + 指标 + 期间，实测样例见 `substitute_caliber.json.naming_rule_evidence`），**不得自创新构词**。缺 P6 ⇒ 只能判"口径可用但 id 未落"。

**风险登记项（不作为否决条件，但必须写进裁定）**

- **R1** 分母/分子口径暴露：跨层相除会把锂/铁/钨/钼/铅与非控股差异混进"元/吨"；
- **R2** 与原命题的关系：替代口径不改命题的 `claim`，只改 `parameter_mapping` 落点（追加新版本，不回改）；
- **R3** 双计：`resource`（量×价）与 `direct_revenue`（分部收入）两条路径互斥（P5）。

---

## 3. 变异判据（MUTATED，同样先冻结）

`MUTATED = P1 ∧ P2 ∧ P6`（**丢弃 P3、P4、P5 中的 P3、P4**，即取消"禁止跨层相除"与"同表同注配对"两条口径约束；P5 仍保留用于双计判定）。

- 用途：证明 STRICT 判据**有判别力** —— 若 MUTATED 下一个**不该被接受**的口径（跨层相除合成的"元/吨混合金属单位收入"）被判 ACCEPT，而 STRICT 下同一口径被判 REJECT，则说明 P3/P4 是真实承重判据，而非装饰。
- 期望（冻结时写下，跑完对照）：
  - `STRICT(GREEN_A)` = 0（真实替代口径通过）
  - `STRICT(RED_B)` = 1（跨层相除口径被拒）
  - `MUTATED(RED_B)` = 0（变异判据放过它 ⇒ 变异存活）
  - `STRICT(RED_C)` = 1（同行/行业均值系数口径被拒）
  - `MUTATED(RED_C)` = 1（变异判据仍拒 ⇒ 变异是**定向**的，不是"什么都放行"）
- rc 约定：**0 = 判据 ACCEPT；非 0（本实现取 1）= 判据 REJECT**。测试程序整体退出码为各用例 rc 的按位或（预期 1）。

---

## 4. `NOT_ESTABLISHED` 定义（缺证据时的唯一合法写法）

某一项数据/结论标 `NOT_ESTABLISHED` 当且仅当满足**全部**：

1. 在**本地可核语料**（本计划 `.planning/**` 只读件 + `company-wiki` 只读原件）中按 `anchor_text` 检索后**未取得**该值的原文行；或取得的原文**无法定位**（无页/表/锚文本）；或
2. 取得的值**无法与第二条独立路径对上**（算术闭环 / 跨报告同值 / 另一版式取文），且无 `sha256` 绑定。

配套纪律：

- 找不到 ⇒ 写 `NOT_ESTABLISHED` + 已执行的检索命令与范围；**不得猜测、不得用反推值冒充披露值**（反推值只能标 `derived_reviewer_computed` 并单列）；
- **本地缺失 ≠ 未披露**；**外部存在 ≠ 本地可核**（沿用两半区判例）；
- 未见全文级检索记录的断言（如"公司全文从未披露 X"）一律不作已核事实。

---

## 5. 范围边界与行不交界声明（冻结）

**写入面**：仅 `execution_runs/OPEN2-SUBSTITUTE-CALIBER/a20260925-01/` 下的四个交付件（`oracle.md`、`substitute_caliber.json`、`ruling.md`、`handoff.json`）。**不写 `.planning` 之外任何路径**（含 `company-wiki` 产品仓）；本轮**不涉** §二十七 #2。

**只读面**：`I-11-A` 封盘 attempt、`I11A-OPEN-ACCT` / `I11A-OPEN-IND` / `I11A-OPEN11-IND` / `I11A-OPEN-MERGE` 四个裁定载体、`execution_v2/*.md`、`company-wiki/companies/紫金矿业/raw/**`（只 `Get-FileHash` 与 `pdftotext … -`，输出只进管道）。

**明令禁止**：git 写操作；**禁用 `git status`**（收尾只允许 `git -c core.quotepath=false diff HEAD --name-only`）；联网（本轮网络请求 = 0，全部证据取自盘上语料）。

**行不交界（我明确不做，逐条）**：

1. **不解除 `OPEN-2`**（第二分支是否已满足与 OPEN-2 是否解 BLOCKED 是两件事，均不由本文件宣布）；
2. **不放行任何参数/阈值**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的 `low/base/high` 保持 `null`、`_PLACEHOLDER` 不解除、`threshold_basis` / `threshold_review_status` 不动；
3. **不解除任何 `BLOCKED-*`**（ACCT：BLOCKED-2a/2b/3a/3b/6a/6b/6c；IND：BLOCKED-1…7）；
4. **不产生 `I-11-B` 的 ACCEPT**，不写 `approved_frozen`；
5. **不重裁**两半区已裁的铜当量换算系数（其 S1/S2、A/B/C 分级与 fail-closed 结论原样保留）；
6. **不代签**其他角色（实现者、owner、会计/行业半区原裁定人）；
7. **不写五份计划文件**（`task_plan.md`/`findings.md`/`progress.md`/`audit_report.md`/`implementation_plan.md` 一律不动）；
8. **不改** `hypotheses.json` / `model_cards.md` / `validate_hypotheses.py` —— 注册动作属实现者/编排层，本工位只给规格。

---

## 6. 实测方案（本节跑之前必须已完成 §7 冻结）

**A 组 · 算术复算（数据充分性的可复算证明；rc = 任一失败即 1）**

- `A1`–`A4`：FY2025 销量 ÷ FY2024 销量 − 1，与 AR2025 产销量表披露的四项销售量同比%（22.68 / 7.35 / −8.79 / 1.44）比对，容差 0.005pp（披露为两位小数）；
- `A5`–`A8`：FY2024 销量 ÷ FY2023 销量 − 1，与 AR2024 产销量表披露的四项销售量同比%（1.62 / 1.68 / −6.85 / 3.10）比对，同容差；
- `A9`：矿产品分部对外收入 FY2024 在 **AR2024（leaf 352）与 AR2025（pdftotext leaf 327 / P1 `pdf_page` 328）两份报告中同值**；
- `A10`：FY2025 四分部对外收入之和 = 合并营业收入 349,079,082,852（|差| ≤ 1 元）；
- `A11`：FY2025 分产品金额（万元）合计 − 内部抵消数 = 合并数 34,907,908 万元；
- `A12`：`单价 × 销售数量 ≈ 金额`（铜精矿 FY2025），相对误差 ≤ 0.1%（单价按整数披露导致的舍入）。

**B 组 · 口径判据实测（rc 见 §3 期望表）**

- `GREEN_A`：真实替代口径对象（收入侧 = 矿产品分部对外收入，量侧 = 分金属销量，两槽独立、零系数、同报告期、已注册 id 可落）→ 期望 `STRICT = 0`；
- `RED_B`：**跨层相除**口径对象（`109,977,556,345 ÷ 884,943 吨` 得"元/吨"并标为单位实现收入，其余输入同样真实）→ 期望 `STRICT = 1`、`MUTATED = 0`；
- `RED_C`：同行/行业均值系数口径对象（把某同行"元/吨铜当量"套给紫金）→ 期望 `STRICT = 1`、`MUTATED = 1`。

**不造绿样**：GREEN 对象的每个字段都必须能在 `substitute_caliber.json` 的 `evidence[]` 里找到 `file + line/leaf + verbatim_quote + sha256`；找不到即把该字段改写为 `NOT_ESTABLISHED` 并重跑（不得为了让 GREEN 通过而补造证据）。

---

## 7. 冻结登记

- 本文件写入后计算 `sha256`，**先**把该 sha 记入 `ruling.md` §④，**再**执行 §6；
- §6 的判定式、期望 rc、用例对象在冻结后**不得修改**；若实现细节需调整，只能追加 `oracle_r2.md` 并作废本轮 rc；
- rc 与实测输出原样抄入 `ruling.md` §④ 与 `handoff.json.red_green_mutation_rcs`。
