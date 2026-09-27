# OPEN-2 C2 第二分支 · 替代口径裁定（行业/会计专业 reviewer，非实现者）

- 工位：`execution_runs/OPEN2-SUBSTITUTE-CALIBER/a20260925-01`（**新建**，四件交付：`oracle.md` / `substitute_caliber.json` / `ruling.md` / `handoff.json`）
- 角色：`industry_or_accounting_reviewer`（行业/会计专业 reviewer，**非实现者、不代签**）
- 被裁对象：`I11A-OPEN-MERGE/a20260924-01/handoff.json` 的 `i11b_unlock_conditions` **第 2 条（C2）第二条分支**
- 只读对象：`I-11-A` 封盘 attempt、两半区裁定、OPEN-11 裁定、`execution_v2/*`、`company-wiki` 紫金原件
- 网络：**0 请求**；git 写：**0**；`git status`：**未执行**；`.planning` 之外写入：**0 字节**
- 判据冻结件：`oracle.md`（sha256 `f5c4529095534013e4dee39b40d42d24ab435030ef81290dfa5ab0e97419f945`，11,035 B），**先冻结后跑**（§④）

---

## ① 身份与授权链

### 1.1 C2 题面（逐字，不转述）

`execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` **L119**（本工位独立读取，文件 sha256 `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878`，21,808 B）：

> `OPEN-2：系数取值解 BLOCKED（S1/A 级证据 + 双签）或落实『分部对外收入 + 分金属销量』替代口径并注册新 parameter_id`

同文件 L117–L125 为 `i11b_unlock_conditions` 全表（7 条）；**第 1 分支（S1/A 级证据 + 双签）两半区已判死**（本工位不重裁）；**本工位只裁第 2 分支**。同文件 L54 另有注册要求：

> `走替代口径则新 parameter_id 须在 model_cards.md 注册并通过 REGISTERED 检查`

### 1.2 两半区裁定（本工位**独立复算** sha256，非引用其自述）

| 半区 | 文件 | sha256（本工位复算） | 字节 | 与合并工位登记值是否一致 |
|---|---|---|---|---|
| 会计 | `execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md` | `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2` | 37,355 | ✅ 与 MERGE handoff L20 一致 |
| 行业 | `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md` | `8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b` | 39,207 | ✅ 与 MERGE handoff L31 一致 |
| OPEN-11 | `execution_runs/I11A-OPEN11-IND/a20260924-01/ruling.md` | `c02e255f67f76be9c0a38569454b64cd93f8469d9fc5244e6da2ce7cfc3bb95d` | 38,930 | 本工位实测值 |
| 合并 | `execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` | `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878` | 21,808 | 该文件自报 `sha256=null`（自指不可自证），由本工位外部复算 |

### 1.3 我据以裁定的两半区原文（逐字）

- **会计面 ACCT `ruling.md` L75（RULING 一句话）**：
  > 「…本地语料当前**无任何 S1/S2**，故 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 必须按 S0 处置 —— 参数保持 `_PLACEHOLDER`、I-11-B 不得放行幅度校准，**替代方案是回退到“分部对外收入 + 分金属销量”的无换算口径**（或整条转 `unquantified`）。」
- **会计面 ACCT `ruling.md` L32（我的会计维度三问之一）**：
  > 「`OPEN-2`：铜当量换算系数在**会计/披露口径**上可接受的来源分级、使用时**必须披露什么**、以及**无公司披露时的替代方案与 fail-closed 默认**。」
- **会计面 ACCT `ruling.md` L100（A-2.3 第 1 条 · 首选替代）**：
  > 「**单位回退（首选）**：只用披露单位计量 —— 收入侧用**分部对外收入（元）**，量侧用**分金属销量**（铜 吨、金 千克），不做混合金属分母；单位经济学若必须给出，按金属分别给（并须符合 M09 `realized_price` 的 driver 注册规则，见兼容影响）。」
- **会计面 ACCT `ruling.md` L103**：「**明确结论：不可得 ⇒ 参数保持 `_PLACEHOLDER` 且不得放行**」。
- **行业面 IND `ruling.md` L77**：「⇒ **A 类来源在 FY2025 年报中不存在**：公司没有披露任何用于把金/银/锌销量折成“铜当量销量”的系数。」
- **行业面 IND `ruling.md` L90（标注要求 1）**：「维持 `pending_professional_decision`，`low/base/high` 保持 `null`；**不得**因本裁定获得放行」。
- **行业面 IND `ruling.md` L96（首选口径替换）**：
  > 「不做当量合并，改为两个已披露量——「矿产品分部对外收入（元）」+「分金属销量（铜 884,943 吨 / 金 83,161 千克 / 锌 / 银，p44 产销量表）」分别落参数；这样 `double_count_exclusion` 中“铜当量折算系数只允许出现一次”的约束自然消失」
- **OPEN-11 `ruling.md` L143（替代口径要用的数据源 + 定位纪律）**：「同一锚文本在 FY2024 = leaf **42**（页脚 42，偏移 0），在 FY2025 = leaf **44**（页脚 45，偏移 +1）⇒ **leaf 与打印页都会跨期漂移**，跨期定位**必须**带 `anchor_text`」；L123–L140 给出两期产销量表的同表/同列/同表注实证与六项同比闭环。
- **卡文 `card_I-11-B.md` L9/L13（前提两行 + 动作 1）**：
  > 「- I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。」
  > 「1. 按contract arithmetic、历史经验或外部可比选择校准方法，保存选择依据与样本；缺数据就标expert_assumption。」

**我 = 上述链路下被指派裁 C2 第二分支的执行者**；只裁本条，越权部分写 `NOT_ESTABLISHED` / `NOT_IN_MY_SCOPE`。

---

## ② 四问逐条结论

### Q1 · 替代口径是否成立？

**结论：成立（有条件）—— 但只在「两槽独立、禁止跨层相除」的读法下成立；「分部对外收入 ÷ 分金属销量」这一读法不成立。** 逐项：

**(a) 好处（少引入一个无来源系数）**

1. `factor_basis=none`：唯一 S0 输入（铜当量换算系数）被彻底移除，ACCT 的 fail-closed 触发条件消失；
2. 两侧都是**同一发行人同一报告期原文披露**，可定位（`anchor_text`+页/表）、`sha256` 绑定，且有**非取文工具**的第二条复核路径（算术闭环 A1–A8 + 跨报告同值 A9）⇒ 满足 ACCT S1 与 IND A 类对“来源”的实质要求；
3. `hypotheses.json` L189/L193 的「铜当量折算系数只允许出现一次」双计约束**自然消失**（IND L96 明示）；
4. 口径暴露二（元/吨铜当量被当铜价）与 IND C 类跨公司不可比**一并消失**；
5. 对系数的**数量级级**敏感性（IND L86 实测 k=20/24/28 摆动）不再存在。

**(b) 代价与风险**

| # | 风险 | 实测证据 |
|---|---|---|
| R1 | 跨层相除会**原样复现**口径暴露二（只是没了系数）：`109,977,556,345 ÷ 884,943 = 124,276.43 元/吨`，分子里装着金/银/锌/锂/铁/钨/钼 收入却贴“元/吨”标签 | `substitute_caliber.json.scope_mismatch.fy2025_measured.naive_ratio_value` |
| R2 | 分母口径暴露：产销量表**不含非控股企业**、且**无 锂/钨/钼/铅** 行，分部收入无法对四金属完全分解 | 表注逐字「本表不含非控股企业的相关数据。」；分部产品定义含铅精矿/锂/钨/钼（EV-09）；`NOT_ESTABLISHED NE-2` |
| R3 | 三重口径错配：产品范围（分部全部产品 vs 四金属）、抵销状态（对外 vs 分产品毛额）、并表范围（合并 vs 不含非控股） | FY2025 实测：分产品矿山行毛额 131,489,500,000 − 对外 109,977,556,345 = **21,511,943,655（19.56%）**；分部总计 − 分产品矿山行 = **6,782,172,956**；内部销售 28,294,116,611 |
| R4 | 双计：`resource`（量×价）与 `direct_revenue`（分部收入）两条路径互斥 | `hypotheses.json` L189/L193；A11 已复算 分产品−抵销=合并数 |
| R5 | 单位对齐：金/银披露单价 `元/克`、披露销量 `千克`，模型相乘须显式 ×1000（**尺度**换算，非金属换算） | 披露单价原文（EV-08） |

**(c) 与原命题 `H-CN-ZIJIN-MIN-02` 的关系**

- **`H-CN-ZIJIN-MIN-02` = `NOT_ESTABLISHED`**：对整个工作区（`.planning` 内外全部 `*.md`/`*.json`）检索 `H-CN-ZIJIN-MIN-02` 与 `ZIJIN-MIN`，**命中 0**（`substitute_caliber.json.not_established NE-1`）。不存在的 id 不得被当作原命题引用。
- 真正被触及的命题是 **`H-CN-ZIJIN-SEG-02`**（`hypotheses.json` L134–L239，sha256 `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`）。

**(d) 改哪条命题？还是新增？**

- **既不改命题的 `claim`，也不新增命题**；只改 **`parameter_mapping` 落点**（新版本追加、旧快照保留）：`unit` 由「人民币元/吨铜当量」改为分金属单位，`original_value`/`conversion_formula`/`falsifier.observable` 换成同表同注口径。
- 不变项：`state=pending_professional_decision`、`decision_sha256=null`、`threshold_basis=professional_judgement_required`、`low/base/high=null`、`three_qualifications` 三栏。
- 若实现者要为「分金属单位收入」另立命题，属 I-11-A 新版本流程，**不在本工位授权内**。

**依据（全部本地可核，编号见 `substitute_caliber.json.evidence`）**：EV-11（ACCT L100）、EV-12（IND L96）、EV-01…EV-10（数据原文）、`oracle.md` P1–P6、A 组 12 项算术复算 `A_RC=0`。

**反例（什么会推翻本裁定）**

1. 会计面或 owner 明文裁定「分部对外收入 ÷ 分金属销量 的比值可用作单位收入」且给出口径桥 ⇒ P3 被推翻，Q1 的“有条件成立”退化为“比值口径成立”（须追加登记）；
2. 检出 `按产品划分的销售详情` 与 `②产销量情况分析表` 的口径**不同表不同注**（例如其一含非控股企业）⇒ P4 被推翻，Q1 整体转不成立；
3. 下一期年报删除产销量表或销售详情表（或改为仅披露合并数）⇒ 量侧数据断供，替代口径转 `NOT_ESTABLISHED`，按 ACCT A-2.3 第 3 条整条转 `unquantified` / `STOP_DISCLOSURE_ADAPTATION`；
4. I-11-B 模型侧证实**只能消费单一“单位收入”字段**、无分产品槽位（IND L104 已预置该反例）⇒ 本替代须回到 **I-10-A 扩展模型**，而不是回到系数；
5. 出现监管明文要求披露铜当量换算系数 ⇒ 第 1 分支复活，本分支降级为备选。

**兼容影响（下游怎么变）**

- **I-11-B**：新增 1 个主 id + 3 个伴随 id（见 Q3）；`resource` 与 `direct_revenue` 二选一进收入路径；`STOP_CALIBRATION`（`card_I-11-B.md` L20）在“幅度无来源又未标 `expert_assumption`”时仍会触发——**本裁定不给幅度**；
- **OPEN-6 / H2**：`H-CN-ZIJIN-SEG-02` 的 `falsifier.observable`（L195「分部报告矿产品对外收入 ÷ 产销量表铜当量销售量」）必须随口径改写；**H2 的 ±5% 仍未审定**（IND L291、ACCT BLOCKED-6a），本裁定**不动任何 `threshold_basis`**；
- **OPEN-2**：被封参数仍封（§⑤），BLOCKED-2a/2b、IND BLOCKED-2/3 原样保留；
- **I-10-A / I-07-E**：披露适配须登记“铜当量系数未披露 + 已改用分金属口径”这一披露缺口；不因此获得任何资格；
- **校验器**：新增 id 必须通过 `REGISTERED`（model_id=`resource`）与 `E_DUPLICATE_PARAMETER` 唯一性检查；本工位**不改**校验器。

**恢复规则（追加式，不回改）**

新证据到达 ⇒ 在本目录追加 `substitute_caliber_r2.json` + `ruling_r2.md`（标 `supersedes: ruling.md#Q1`），不改本文件正文、不改两半区任何字节；`hypotheses.json` 侧只能由有写入面的实现者**新增版本**（`decision.decision_sha256` 指向新裁定），旧快照保留供 I-12 评分。

---

### Q2 · 数据是否够（逐项实测证据）

**结论：四项三年序列全部 `ESTABLISHED`（`A_RC=0`）；另有 4 项 `NOT_ESTABLISHED`（NE-1…NE-4），不猜。**

| 数据项 | FY2023 | FY2024 | FY2025 | 结论 | 实测证据位置（文件 + 行号/页 + 逐字引文要点） |
|---|---|---|---|---|---|
| **矿产品分部对外销售收入（元）** | 59,766,798,161 | 74,089,365,354 | 109,977,556,345 | **ESTABLISHED** | FY2025：`P1_zijin_pages.json` **L161/L163**（`pdf_page=327`），原件 `pdftotext -f 326`（页脚 `-219 -`），引文「对外销售收入109,977,556,345…-349,079,082,852」；FY2024：同文件 **L166/L168**（`pdf_page=328`，`pdftotext -f 327`，页脚 `-220 -`）**＋** AR2024 `pdftotext -f 352`（页脚 238）同值（A9）；FY2023：**AR2024 原件 `pdftotext -f 354`（页脚 240）**，引文「2023年 … 59,766,798,161 150,873,974,024 48,296,807,364 34,465,663,329 - 293,403,242,878」 |
| **矿山产铜 销售量（吨）** | 810,737 | 824,317 | 884,943 | **ESTABLISHED** | FY2025：`P2_zijin_44_48.txt` **L312**「83,161 884,943 352,470 430,254」；FY2024：同文件 **L112**「…620,407 80,919 122,991…」＋ AR2024 `pdftotext -f 42`「67,786 824,317 386,444 424,145」；FY2023：**AR2024 `pdftotext -f 41`（页脚 41）**「…640,890 95,999 73,848…」（铜 = 三行之和）；同比闭合 A2=0.00469pp、A6=0.00498pp |
| **矿山产金 销售量（千克）** | 66,707 | 67,786 | 83,161 | **ESTABLISHED** | FY2025：同 L312（金 83,161）；FY2024：**L112**「38,087 29,699」之和＝67,786 ＋ AR2024 leaf 42「67,786」；FY2023：AR2024 leaf 41「33,673 33,034」之和＝66,707；A1=0.00167pp、A5=0.00248pp |
| **矿山产锌 销售量（吨）** | 414,879 | 386,444 | 352,470 | **ESTABLISHED** | FY2025：L312（锌 352,470）；FY2024：L112（386,444）＋ AR2024 leaf 42（386,444）；FY2023：AR2024 leaf 41（414,879）；A3=0.00144pp、A7=0.00381pp |
| **矿山产银 销售量（千克）** | 411,403 | 424,145 | 430,254 | **ESTABLISHED** | FY2025：L312（银 430,254）；FY2024：L112（424,145）＋ AR2024 leaf 42（424,145）；FY2023：AR2024 leaf 41（411,403）；A4=0.00031pp、A8=0.00279pp |

补充实测（同表同注的第三条路径）：**披露不含税单价三年**（`P2` L57–58 / L107–108；AR2024 leaf 41）——铜精矿 49,406→56,342→63,613、电解铜 59,590→65,894→71,422、金锭 433.09→533.39→810.17 元/克、锌 11,855→14,921→14,999、银 3.50→4.74→6.88 元/克；`A12` 实测 `单价×数量 ≈ 金额` 相对误差 **0.000616%**。

**`NOT_ESTABLISHED`（不猜）**

| id | 项 | 结论 |
|---|---|---|
| NE-1 | 命题 `H-CN-ZIJIN-MIN-02` | **NOT_ESTABLISHED**（工作区 0 命中）；最近真实命题为 `H-CN-ZIJIN-SEG-02` |
| NE-2 | 矿产品分部内 锂/钨/钼/铅精矿 的分金属销量 | **NOT_ESTABLISHED**（产销量表无该等行）⇒ 分部收入无法对四金属完全分解，构成 P3 的实证基础 |
| NE-3 | FY2023 年报**原件** | **NOT_ESTABLISHED**（本地语料只有 FY2024/FY2025 两份 PDF）；FY2023 数据取自 FY2024 年报**比较期同表**，口径连续性由 A5–A8 闭合 |
| NE-4 | 铜当量换算系数取值 | **不在本轮范围**（两半区已判 fail-closed，本工位不重裁、不解锁） |

**反例**：任一年份的表被检出与相邻期不同表/不同注 ⇒ 对应格子改判 `NOT_ESTABLISHED`，Q2 整体转不成立。**兼容影响**：三年基期是 I-11-B 校准的样本（`card_I-11-B.md` L13「保存选择依据与样本」）；样本只到 FY2025，FY2027 幅度仍须自行校准。**恢复规则**：FY2023 年报原件或 FY2026 年报进入本地语料后，追加 `substitute_caliber_r2.json` 补齐第四年，不回改本表。

---

### Q3 · 新 `parameter_id` 怎么定？

**结论：给出 1 个主 id + 3 个伴随 id；命名规则回源归纳（未见任何文档规定构词法，故以既有 14 个 id + 校验器约束为源）；`low/base/high` 一律 `null`。**

**命名规则回源（不是自创）**

- `decision.md` **DEC-5 L125–L135**：「只落到 `model_cards.md` 已注册的 `model_id`/`driver_name`，落不下的判 pending」；
- `validate_hypotheses.py` **L21–L75**（`REGISTERED` 表，`resource` 的 driver 为 `saleable_volume`/`realized_price`/`other_revenue`）、**L187–L190**（`E_UNKNOWN_MODEL`/`E_UNKNOWN_DRIVER`）、**L197–L213**（`E_DUPLICATE_PARAMETER`：一 id 只能一命题×一 driver×一 `effective_period`）；
- 既有 id 构词（`hypotheses.json` L37/L49/L56/L63/L168/L275/L287/L390/L495/L605/L617/L627/L729/L834）：`{发行人}_{范围或分部}_{指标}_{FY20xx}[_PLACEHOLDER]`，全大写下划线分隔；`_PLACEHOLDER` 只用于未获批占位值；
- `model_cards.md` **L644–L650（M09）**：「单位/口径：已售可结算数量×U/同数量单位；不得混矿石吨、精矿吨、金属吨」；
- **明确声明**：`explicit_naming_rule_document = NOT_FOUND`（未见逐条规定构词法的文档），故规则为**从上述三处归纳**，若 owner 另有明文规则，以 owner 规则为准并追加 `ruling_r2.md`。

**主 id（C2 分支的直接落点）**

```
parameter_id          : ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027
model_id / driver     : resource / realized_price   （均在 REGISTERED 内，DEC-5 通过）
unit                  : 人民币元/吨（不含税）
unit_basis            : disclosed_same_table_pairing
                      （分子分母同出「按产品划分的销售详情」同一张表与同一条表注；
                        披露单价为公司原文值，混合单价为 reviewer 由披露值复算并标 derived）
factor_basis          : none ；conversion_factor_value = null
                      ；factor_source_in_filing = not_applicable_no_conversion_used
                      ；cross_company_comparable = not_applicable（不含任何跨公司输入）
low / base / high     : null / null / null     ← 保持 null，不放行
base_period           : FY2023 – FY2025（三年披露基期，观察值已单列、非放行值）
effective_period      : FY2027（待 I-11-B 校准幅度）
state                 : pending_professional_decision（不因本裁定改变）
conversion_formula    : 单位实现收入 = 该金属各产品行金额(元) ÷ 各产品行销售数量；
                        收入 = 单位实现收入 × 销售数量
dependency_control    : shared_driver_ids = [ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027,
                                             ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027,
                                             ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027]
                        double_count_check = 收入路径只允许一条（分部对外收入 或 量×价），
                                             另一侧只作对账；价格变化不得再作为“额外收入”叠加；
                                             同一笔销量不得重复计入；
                                             铜当量换算系数在任何路径出现即判违例
                        correlated_scenarios = 价格与销量在并购/爬坡年同向变动，low/high 不得独立外推
threshold_basis_touched : false      placeholder_suffix_removed : false      released : false
```

**伴随 id（把「分金属销量」按 IND L96 点名的 铜/金/锌/银 补齐；铜、金销量 id 已存在）**

| id | 单位 | driver | 说明 |
|---|---|---|---|
| `ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027` | 人民币元/克（披露单位；与千克销量相乘须登记 ×1000 `unit_scale_only`） | `realized_price` | 与主 id 同构 |
| `ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027` | 吨 | `saleable_volume` | 补齐锌销量槽 |
| `ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027` | 千克 | `saleable_volume` | 补齐银销量槽 |

**为什么主 id 是它（而不是别的）**：C2 第二分支是「系数取值解 BLOCKED」的**替代**，而被封的正是 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027`（`hypotheses.json` L168，单位「人民币元/吨铜当量」）；ACCT L100 明确「单位经济学若必须给出，**按金属分别给**（并须符合 M09 `realized_price` 的 driver 注册规则）」。**备选落法**：若 I-11-B 只走 `direct_revenue`（分部对外收入直接作收入路径），新 id 只需补 锌/银 销量槽——两种落法都在本口径内，**唯一被禁止的落法是跨层相除**。

**反例**：owner 另颁命名规则 ⇒ 主 id 改名并追加 `ruling_r2.md`；`model_cards.md` 若不接受 `resource.realized_price` 的新 id ⇒ 按 DEC-5 退回 `pending_professional_decision`（不是 `unquantified`）。**兼容影响**：注册动作会改动 `model_cards.md` 与 `hypotheses.json`（均**不属本工位写入面**）；校验器需新增 id 通过唯一性检查。**恢复规则**：注册完成或被拒，均以新文件追加登记，不回改本裁定。

---

### Q4 · 与两半区裁定是否冲突？

**结论：不冲突 —— 本替代是两半区各自明文开的那条路（绕开，不是违反）；本工位未违反两半区任何一条。**

| 两半区条文 | 本裁定与之的关系 |
|---|---|
| ACCT L75「替代方案是回退到『分部对外收入 + 分金属销量』的无换算口径」 | **正是本裁定对象**，我把它从“一句话方向”落实为可执行定义 + 数据 + id |
| ACCT L100（A-2.3 首选单位回退：收入侧分部对外收入、量侧分金属销量、不做混合金属分母、单位经济学按金属分别给） | **逐条采纳**；我的 P3/P4/P5 就是它的操作化 |
| ACCT L103「不可得 ⇒ 参数保持 `_PLACEHOLDER` 且不得放行」 | **遵守**（§⑤） |
| ACCT A-2.1 来源分级（S1/S2 才可冻结） | 本口径两侧均为 S1 级（同一期间原文披露 + 页/表/锚 + sha256 + 独立复核路径）；**我未动 S1/S2 定义** |
| ACCT A-2.1 第 5 条「反向推导（收入 ÷ 假设价 × 假设量倒算系数）循环论证不可采」 | **不触碰**：本口径不倒算系数；分金属单价由**同表同表注**的披露值复算（且锌/银直接等于披露单价），无任何“假设价/假设量” |
| ACCT BLOCKED-2a/2b、IND BLOCKED-2/3 | **一条未关**（§⑤） |
| IND L77「A 类来源在 FY2025 年报中不存在」 | **不推翻**：我裁的不是系数，而是不用系数的替代口径；本裁定未对系数给出任何取值 |
| IND L90「维持 pending、low/base/high 保持 null、不得因裁定获得放行」 | **遵守**（§⑤） |
| IND L96（首选口径替换：两个已披露量分别落参数、双计约束自然消失） | **正是本裁定对象** |
| IND C 类「跨公司不可比」 | 本口径**零跨公司输入**（RED_C 被 P1/P2 双拒） |
| OPEN-11 R2-5「跨期定位必须带 anchor_text」 | **遵守并加严**：我实测发现**同文档内跨段索引偏移方向相反**（EV-18），因此把 `anchor_text` 要求扩展到**跨源**引用 |
| ACCT/IND 对 OPEN-6 的处理（H2 未审定） | **不动**任何 `threshold_basis`/`threshold_review_status` |

**唯一需要登记而非裁断的接触面**：`ARITH-INCONSISTENCY-1` —— 封盘件 `original_value` 自述的分母 `885,141` 与其自述公式 `884,943 + 83,161×24 = 2,880,807` **算术不一致**（实测 `109,977,556,345 ÷ 2,880,807 = 38,175.95`，而 `÷ 885,141 = 124,248.63`，隐含 k=0.002381）；IND L86 的三点敏感性中 k=20（43,159.55）、k=28（34,224.13）与自述吻合，**k=24 点换了基准**。**处理：只登记、不回改任何文件**；该发现**不改变**两半区 fail-closed 结论，反而强化“系数分支不可用”；并且它说明被登记的 headline 值在数值上就等于 `收入 ÷ 铜销量`（124,276.43 ≈ 124,248.63）——**正是我 RED_B 要拒的跨层相除**，故 P3 是承重判据（§④ 变异实测证明）。

**本裁定违反了哪一条？—— 没有。** 逐条核对见上表；我未解除任何 BLOCKED、未放行任何参数、未改任何 `threshold_basis`、未写 `approved_frozen`、未代签、未回改两半区或封盘件任何字节（收尾 sha256 复核见 `handoff.json.written_files` 与 §③）。

---

## ③ 我独立复核/复算了什么（列文件 + sha；**不引用实现者自述**）

**1. 只读文件 sha256 复算（`Get-FileHash -Algorithm SHA256`，逐个本机重算）**

| 文件 | sha256（我复算） | 字节 | 与外部登记值比对 |
|---|---|---|---|
| `I11A-OPEN-ACCT/a20260924-01/ruling.md` | `f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2` | 37,355 | ✅ = MERGE handoff L20 |
| `I11A-OPEN-IND/a20260924-01/ruling.md` | `8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b` | 39,207 | ✅ = MERGE handoff L31 |
| `I11A-OPEN11-IND/a20260924-01/ruling.md` | `c02e255f67f76be9c0a38569454b64cd93f8469d9fc5244e6da2ce7cfc3bb95d` | 38,930 | 本工位实测 |
| `I11A-OPEN-MERGE/a20260924-01/handoff.json` | `b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878` | 21,808 | 自报 `null`，外部复算 |
| `I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 51,697 | ✅ = OPEN-11 裁定登记值 |
| `I-11-A/a20260919-01/decision.md` | `e9c96f02118514b8596620b3c0e235a797747fcd3bcf59d1a0fd20aa70166951` | 29,756 | ✅ = IND L398 登记值 |
| `I-11-A/.../extract/P1_zijin_pages.json` | `f1909d136d05bde0230e7fd2761c079026f9a132dd7123109bd7ca7bab85e2cf` | 89,754 | 本工位实测 |
| `I-11-A/.../extract/P2_zijin_44_48.txt` | `073276d2dc73bddef40ec7d415e9f5e7e942769c645f673f422b507a72cbf159` | 17,810 | 本工位实测 |
| `execution_v2/card_I-11-B.md` | `38ff2907acb627f3d5f6a97ca386a17551329ad3909720e84463a185154ae87c` | 1,672 | 本工位实测 |
| `company-wiki` AR2025 PDF | `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d` | 79,925,886 | ✅ = `hypotheses.json` `doc_sha256` |
| `company-wiki` AR2024 PDF | `004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89` | 32,100,114 | ✅ = OPEN-11 裁定登记值 |

**2. 我自己重新取文（`pdftotext -enc UTF-8 [-f N -l N] <pdf> -`，输出只进管道，零落盘）**

- AR2024：leaf 41（2023/2024 销售详情 + 单价）、leaf 42（②产销量情况分析表）、leaf 352（2024 分部表）、leaf 354（**2023 分部表**）、leaf 41–43 全取；
- AR2025：leaf 43/44/45（定位哪一页是产销量表）、leaf 325–329（分部表页序）；
- **索引口径实测（新发现，EV-18）**：同一物理页在两套索引下编号不同——页脚 44 的销售详情页 = `pdftotext` leaf **44** = 封盘 P1 `pdf_page` **43**；页脚 45 的产销量表页 = `pdftotext` leaf **45** = P1 `pdf_page` **44**（`hypotheses page_span` 记 44）；页脚 `-219 -` 的 2025 分部表 = `pdftotext` leaf **326** = P1 `pdf_page` **327** ⇒ **MD&A 段 P1 = leaf−1、附注段 P1 = leaf+1，段间不一致** ⇒ 跨源引用只能靠 `anchor_text`。

**3. 我自己做的算术复算（`python -X utf8`，脚本不读写文件）**

- A1–A8：八个销量同比与两份年报披露值逐一比对，最大偏差 **0.00498pp** < 冻结容差 0.005pp ⇒ `A_RC=0`；
- A9：FY2024 分部对外收入跨报告同值（`74,089,365,354 == 74,089,365,354`）；
- A10：四分部对外之和 = 合并营业收入 `349,079,082,852`（差 0）；
- A11：分产品金额合计 58,404,923 万 − 内部抵消 23,497,015 万 = 合并数 34,907,908 万（差 0）；
- A12：`63,613 × 666,158 = 42,376,308,854` vs 披露 `42,376,570,000` ⇒ 相对误差 **0.000616%**；
- 口径错配量级：分产品矿山行毛额 131,489,500,000 − 分部对外 109,977,556,345 = **21,511,943,655（19.56%）**；分部总计 138,271,672,956 − 分产品矿山行 = **6,782,172,956**；`109,977,556,345 ÷ 884,943 = 124,276.43`；
- `ARITH-INCONSISTENCY-1`：`884,943 + 83,161×24 = 2,880,807`（≠ 自述 885,141）；`num/2,880,807 = 38,175.95`、`num/885,141 = 124,248.63`、`num/(885,141+83,161) = 113,577.74`（差 −10,670.89 在 885,141 基准内自洽）。

**4. 我独立读取的判定依据（逐字，不靠转述）**：C2 原文（MERGE handoff L119）、两半区 ruling 全文、OPEN-11 ruling 全文、`card_I-11-B.md` 全文、`card_I-11-A.md` 全文、`decision.md` DEC-5/开放项表、`validate_hypotheses.py`、`model_cards.md` M09、`hypotheses.json` 全部 8 条命题。

---

## ④ 红绿变异实测 rc

**冻结顺序**：先写 `oracle.md` → 复算其 sha256 = `f5c4529095534013e4dee39b40d42d24ab435030ef81290dfa5ab0e97419f945`（11,035 B，UTF-8 无 BOM、CR=0、纯 LF）→ **再**执行判据脚本。脚本 `python -X utf8 -c <base64 解码>`，不读写任何文件。

**A 组 · 算术复算（数据充分性）**

```
PASS A1 yoy_2025_au  computed=22.68167 disclosed=22.68 diff=0.00167pp
PASS A2 yoy_2025_cu  computed=7.35469  disclosed=7.35  diff=0.00469pp
PASS A3 yoy_2025_zn  computed=-8.79144 disclosed=-8.79 diff=0.00144pp
PASS A4 yoy_2025_ag  computed=1.44031  disclosed=1.44  diff=0.00031pp
PASS A5 yoy_2024_au  computed=1.61752  disclosed=1.62  diff=0.00248pp
PASS A6 yoy_2024_cu  computed=1.67502  disclosed=1.68  diff=0.00498pp
PASS A7 yoy_2024_zn  computed=-6.85381 disclosed=-6.85 diff=0.00381pp
PASS A8 yoy_2024_ag  computed=3.09721  disclosed=3.10  diff=0.00279pp
PASS A9  seg_external_FY2024_cross_report_equal  74089365354 == 74089365354
PASS A10 sum_seg_external_FY2025_equals_consolidated  sum=349079082852
PASS A11 product_rows_minus_elimination_equals_consolidated  58404923+(-23497015)=34907908
PASS A12 unit_price_times_qty_within_0.1pct  rel=0.000616%
A_RC=0
```

**B 组 · 红绿变异（`rc: 0 = ACCEPT，1 = REJECT`）**

| 用例 | 判据 | **实测 rc** | 冻结期望 | 结果 |
|---|---|---|---|---|
| `GREEN_A`（真实替代口径：两槽独立、零系数、同表同注、单收入路径、id 可落） | STRICT | **0** | 0 | ✅ |
| `GREEN_A` | MUTATED | **0** | — | ✅（变异不误伤） |
| `RED_B`（**跨层相除**：`分部对外收入 ÷ 铜销量` 得“元/吨”，其余输入全部真实） | STRICT | **1**（`fail=p3,p4`） | 1 | ✅ |
| `RED_B` | **MUTATED（丢弃 P3/P4）** | **0（ACCEPT）** | 0 | ✅ **变异存活** |
| `RED_C`（同行/行业均值铜当量系数套给紫金） | STRICT | **1**（`fail=p1,p2,p3,p4`） | 1 | ✅ |
| `RED_C` | MUTATED | **1**（`fail=p1,p2`） | 1 | ✅ **变异是定向的** |

```
EXPECT_RC=0     （五条冻结期望逐条 PASS）
OVERALL_RC=1    （各用例 rc 按位或，按 oracle §3 预期为 1）
python exit code = 1
```

**变异证明（GREEN 附变异证明的义务）**：`MUTATED(RED_B) = 0` 而 `STRICT(RED_B) = 1` ⇒ **P3（禁止跨层相除）与 P4（同表同注配对）是承重判据**；把判据改弱后，一个**不该被接受**的口径（把锂/银/锌/铁收入装进“元/吨铜”标签）确实能通过。同时 `MUTATED(RED_C) = 1` ⇒ 变异不是“什么都放行”，它只放开了口径分层这一条。**没有造绿样**：`GREEN_A` 的每个字段都能在 `substitute_caliber.json.evidence[]` 找到 `file + line/leaf + verbatim_quote + sha256`。

**登记（不回改）**：`AMBIG-ORACLE-MUT` —— `oracle.md` §3 公式行写 `MUTATED = P1∧P2∧P6`、括注又写“P5 仍保留”，二义；处置：以公式行为准，并把 `RED_B` 构造成 `single_revenue_path=True`（唯一缺陷就是跨层相除），使两种读法结论一致，rc 不受影响。

---

## ⑤ 不授予什么（明确清单）

1. **不解除 `OPEN-2`**：本裁定只回答 C2 第二分支“口径是否成立”，**不宣布该分支已满足**——`注册`（`model_cards.md` 新增 + `hypotheses.json` 新版本 + `decision.decision_sha256`）属实现者/编排层，本工位无该写入面 ⇒ `c2_branch2_fully_discharged = false`；
2. **不放行任何参数**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 及本裁定新 id 的 `low/base/high` **全部保持 `null`**；新 id 的 `released = false`；
3. **不解除 `_PLACEHOLDER`**：`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`ZIJIN_PLAN_COPPER_VOLUME_FY2026_PLACEHOLDER`、`MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER` 原样保留；
4. **不动阈值**：不改任何 `threshold_basis`、不新增 `threshold_review_status`、不审 ±5% / [0.9,1.1] / 拆分层级判定（BLOCKED-6a/6b/6c 原样）；
5. **不解除任何 `BLOCKED-*`**：ACCT `BLOCKED-2a/2b/3a/3b/6a/6b/6c`；IND `BLOCKED-1…BLOCKED-7` —— 一条未关；
6. **不产生 `I-11-B` 的 ACCEPT**、不写 `approved_frozen`、不声称 I-11-A 验收（`does_not_claim_I11BAcceptance = true`）；
7. **不重裁**两半区已裁的铜当量换算系数（S1/S2、A/B/C 分级与其 fail-closed 结论原样）；
8. **不代签**任何其他角色；**不写**五份计划文件；**不改** `hypotheses.json`/`model_cards.md`/`validate_hypotheses.py`/两半区任何字节。

---

## ⑥ 反例与被拒替代

**被拒的替代方案（逐条）**

1. **跨层相除**：`分部对外收入 ÷ 分金属销量` 当单位收入 —— 三重口径错配（R3 实测 19.56% 缺口 + 无锂/钨/钼/铅量），且数值上等于封盘件那个自相矛盾的 headline（ARITH-INCONSISTENCY-1）；RED_B 实测被 STRICT 拒（rc=1）；
2. **混合分母**：把 吨 与 千克 相加当“总销量” —— 换个名字的未披露换算系数，违反 M09「不得混矿石吨、精矿吨、金属吨」；
3. **同行/行业均值**套系数或“元/吨铜当量”对标 —— IND C 类跨公司不可比；RED_C 在 STRICT 与 MUTATED 下均被拒（rc=1/1）；
4. **用资源储量报告的当量品位折算销量**（IND C′ 口径错配）；
5. **用研报“当量产量”反推**（二手来源，卡文「原文无法核查→STOP_EVIDENCE」）；
6. **用年报摘要替代产销量表**（OPEN-11 已拒：摘要无产销量表、口径相差 230,885 吨）；
7. **先给数、后补来源**（把基期观察值当 FY2027 放行值写进 `base`）—— 本裁定明确 `low/base/high = null`；
8. **因口径改了就把 `H-CN-ZIJIN-SEG-02` 改成 `approved_frozen`** —— 四要件 0/4（沿用 OPEN-11 §3.8 的核对法，本裁定同样 0/4：无新签署、无新版本、无可复算观测量的观察日、无可核幅度）；
9. **把 `H-CN-ZIJIN-MIN-02` 当原命题引用** —— 工作区 0 命中（NE-1）；
10. **回改两半区或封盘件**以“消除”ARITH-INCONSISTENCY-1 —— 只登记、不回改。

**什么会推翻本裁定（反例汇总）**：见 Q1 反例 1–5；Q2 反例（表口径变化）；Q3 反例（owner 另颁命名规则）。

---

## ⑦ 边界（可核）

1. **写入面恰 4 个文件**：`oracle.md`、`substitute_caliber.json`、`ruling.md`、`handoff.json`，全部位于 `execution_runs/OPEN2-SUBSTITUTE-CALIBER/a20260925-01/`；**`.planning` 之外 0 字节**（含 `company-wiki`：只 `Get-FileHash` 与 `pdftotext … -`，输出进管道，未落盘）。
2. **零 git 写**：未执行 `add/commit/checkout/stash/restore/reset` 任何变体；**未执行 `git status`**；收尾仅 `git -c core.quotepath=false diff HEAD --name-only`：`total=3826`、**非 `.planning` = 0**；本工位 4 个新文件经 `git ls-files --others --exclude-standard` 复核为未跟踪路径（不进入 `git diff HEAD`）。total 的历史波动（3821→3826）来自并发写入方，全部落在 `.planning/**` 内。
3. **零网络**：`network_requests_made = 0`；全部证据取自盘上语料。
4. **零封盘/零半区改动**：收尾复算 `hypotheses.json = f2178768…`、ACCT `ruling.md = f3040df0…`、IND `ruling.md = 8bc685a4…`、MERGE `handoff.json = b7314a22…`，与开工前读取值逐一相同。
5. **零 status 变更 / 零代签**：未改 I-11-A/I-11-B 任何 `status`/`state`/`decision`/`threshold_basis`；`handoff.json → releases_nothing = true`、`does_not_claim_I11BAcceptance = true`。
6. **载体格式**：四件均 UTF-8 无 BOM、CR=0（纯 LF）；两个 JSON 写后 `json.load` 重解析 OK。
