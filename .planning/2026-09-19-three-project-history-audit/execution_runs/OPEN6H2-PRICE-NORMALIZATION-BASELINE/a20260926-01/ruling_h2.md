# OPEN6-H2 · `H2` 阈值的「`OPEN-2` 口径 + 价格归一化基准」—— 矿业行业 reviewer 裁定

- 工位（新建）：`execution_runs/OPEN6H2-PRICE-NORMALIZATION-BASELINE/a20260926-01/`
- 角色：`mining_industry_reviewer_h2`（矿业行业 reviewer，**非实现者**；会计面为**会签**对象，本文件**不代签**）
- 被裁对象：`H2` = `H-CN-ZIJIN-SEG-02` 的 `falsifier.threshold`「相对偏离 ±5%」（`threshold_basis = professional_judgement_required`）
- 判据冻结件：`oracle.md`（**先冻结后裁定**）—— 15,820 B，sha256 **`19317143039ce1905cae742e4de321127d309deb73a474845c3e953a75ea7aff`**，冻结时点 `2026-09-26T10:50:54Z`，UTF-8 无 BOM / CR=0
- 纪律：网络请求 **0**；git 写 **0**；**未执行 `git status`**；`.planning` 之外写入 **0 字节**；`OPEN2-*` / `HYPOTHESES-V4-MERGE` / 两半区裁定 / `OPEN6-TOLERANCE-*` / `BLOCKED6C-*` **全程只读**

> **一句话结论**：**口径锚点 = 须重定义（重定义后只能锚新 id）**；**价格归一化基准四要素 1/4（仅"来源与取回时点"齐）** ⇒ **不给数，`h2_value = null`，`h2_status = still_blocked`，未签署 `decision_sha256`，`threshold_review_status` 维持 `not_reviewed`。**

---

## ① 身份与授权（逐字，本工位自算 sha256）

| 授权点 | 逐字原文 | 出处 |
|---|---|---|
| **任务定义** | `\| **H2 ±5%** \| OPEN-2 口径裁定 + 价格归一化基准（价格序列/期间/净价口径） \| 矿业 reviewer + 会计面（IND L373 BLOCKED-6；ACCT BLOCKED-6a） \|` | `I11A-OPEN-MERGE/a20260924-01/merge_ruling.md` **L234**（sha256 `2d214bab…2e5c1`，49,062 B） |
| **H2 现状** | `❌ **不采用占位值；替代数值 \`BLOCKED\`**` | 同文件 **L217**（转引 IND **L291**） |
| **待办点名** | `…；H2 补 OPEN-2 口径 + 价格归一化基准；4 条恒等式容差对照表（BLOCKED-6b）。` | 同文件 **L330 第 5 条** |
| **行业半区** | `\| **BLOCKED-6** \| OPEN-6：H2 单位收入阈值的**替代数值**（±5% 不采用） \| OPEN-2 口径裁定 + 价格归一化基准（价格序列/期间/净价口径） \| 矿业 reviewer + 会计面；**保持 \`professional_judgement_required\` 未审定** \|` | `I11A-OPEN-IND/a20260924-01/ruling.md` **L373**（sha256 `8bc685a4…f4b`） |
| **会计半区** | `- **BLOCKED-6a**：3 条 \`professional_judgement_required\` 阈值的**数值**是否恰当（±5%、[0.9,1.1]、拆分层级判定）—— 需行业/专业 reviewer 按 A-6.3 给出证据与签署；我**不给数**。` | `I11A-OPEN-ACCT/a20260924-01/ruling.md` **L296**（sha256 `f3040df0…9c2`） |
| **给数前置** | `必须**同时**满足，缺一即维持 not_reviewed：1. 观测量可复算…2. 数值有可核基础…(i)…(ii) 同口径历史离散…(iii)…(iv) 专家假设…；3. 签署身份：非实现者…decision_sha256、日期、作用域…；4. 追加式版本化…` | 同文件 **A-6.3 L244–L256** |
| **排序约束** | `- **OPEN-2 交互**：命题 2 的 ±5% 观测量依赖铜当量分母 ⇒ 该条审定必须排在 OPEN-2 之后。` | 同文件 **L280** |
| **⭐ 前提已成立** | `两槽独立、禁止跨层相除`（ruling L59）；`铜当量换算系数在任何路径中出现即判违例（factor_basis 必须为 none）`（`substitute_caliber.json` L160） | `OPEN2-SUBSTITUTE-CALIBER/a20260925-01`（`ruling.md` `f927c44c…99e53`；`substitute_caliber.json` `649a9ff8…22e72`） |
| **⭐ 注册与合并** | `falsifier_full_unchanged = true`（registration.md **L79**）；`…state_reason / falsifier **逐路径无差异**`（merge_report.md **L51**）；`c1_preserved: true` / `c2_registration_preserved: true`（V4 handoff **L98/L101**） | `hypotheses_v4.json` sha256 `ebf6fa4e…9c4654`（68,565 B） |

**本工位只做 `L234` 点名的矿业 reviewer 半方；同句「+ 会计面」的会签是另一步（§⑦ 提请，不代签）。**

---

## ② 第一步 · 口径锚点判定（三选一）

# 结论：**`requires_redefinition` —— H2 的 observable 必须重定义，重定义后只能锚到新 id；旧 id 不得再作锚。**

### 2.1 逐条依据

| # | 依据 | 逐字引文 | 文件 + 行号 |
|---|---|---|---|
| 1 | **v4 现状**：observable 仍是旧口径（跨层相除） | `下一年度年报：分部报告矿产品对外收入 ÷ 产销量表铜当量销售量，与本期校准的单位实现收入之比` | `HYPOTHESES-V4-MERGE/a20260926-01/hypotheses_v4.json` **L352** |
| 2 | **旧 id 口径含换算系数 + 跨层相除** | `"unit": "人民币元/吨铜当量"`、`"original_value": "109977556345/885141（… = 分部对外收入 109,977,556,345 元 ÷ (铜销量 884,943 吨 + 金销量 83,161 千克 × 24 吨/千克)）"` | 同文件 **L286–L288** |
| 3 | **新 id 口径合规** | `"unit": "人民币元/吨（不含税）", "unit_basis": "disclosed_same_table_pairing", "factor_basis": "none"` | 同文件 **L298–L301** |
| 4 | **注册时 falsifier 整块未动** | `8 条 falsifier（含 threshold / threshold_basis / observation_date）｜整块逐字节相同（falsifier_full_unchanged = true）` | `OPEN2-C2-REGISTRATION/a20260926-01/registration.md` **L79** |
| 5 | **v4 合并也未动 falsifier** | `…state_reason / falsifier **逐路径无差异**（v3 未升级任何批准状态）` | `HYPOTHESES-V4-MERGE/a20260926-01/merge_report.md` **L51** |
| 6 | **判据原文：口径变 ⇒ 观测量变** | `- OPEN-6 的 H2 阈值 observable 定义（口径变 ⇒ 观测量变）；` | `I11A-OPEN-IND/a20260924-01/ruling.md` **L111** |
| 7 | **替代口径禁止跨层相除** | `**结论：成立（有条件）—— 但只在「两槽独立、禁止跨层相除」的读法下成立；「分部对外收入 ÷ 分金属销量」这一读法不成立。**` | `OPEN2-SUBSTITUTE-CALIBER/a20260925-01/ruling.md` **L59** |
| 8 | **factor_basis 必须为 none** | `铜当量换算系数在任何路径中出现即判违例（factor_basis 必须为 none）` | 同目录 `substitute_caliber.json` **L160** |
| 9 | **旧口径依赖未清（反向事实）** | `铜当量折算系数只允许出现一次（在量的口径转换中），不得在价格里再折算一次。` | `hypotheses_v4.json` **L346 / L350** |
| 10 | **旧 id 的 falsifier 本就不可执行** | `- I-11-B：H2 阈值未定 ⇒ ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027 的 falsifier 不可执行（与 OPEN-2 联动）；` | IND ruling **L331** |

**推理链（三段）**：
1. OPEN-2 替代口径已裁：跨层相除不成立、`factor_basis` 必须为 `none` ⇒ **旧 id 的口径（元/吨铜当量 = 分部收入 ÷ 含系数的分母）不再允许作锚**（依据 2/7/8）。
2. IND **L111**：口径变 ⇒ 观测量变；而注册与 v4 合并**都**没动 `falsifier`（依据 4/5）⇒ **口径已变、观测量未变**，现状即"待重定义"（依据 1）。
3. 新 id 的口径满足 A-1/A-2（依据 3）⇒ **重定义后的唯一合法落点是新 id**（铜主 id + 金伴随 id）。

⇒ 三选一里：**不是 `anchor_old_id`（被替代口径否定）、也不是"已可 `anchor_new_id`"（observable 尚未改写）⇒ `requires_redefinition`。**

### 2.2 反例（什么会推翻本判定）

1. 会计面/owner 明文豁免旧铜当量口径（含系数来源）⇒ `old_id_allowed` 翻真，判定退化为 `anchor_old_id`（须追加 `ruling_h2_r2.md`）；
2. 实现者在**命题新版本**把 observable 改写为同表同注的分金属实现单价（经价格归一化）比值并留 `decision_sha256` ⇒ 判定升为 `anchor_new_id`，剩余阻塞只看四要素；
3. 出现公司自披露的铜当量系数（IND L102 反例）⇒ OPEN-2 第一分支复活，新旧 id 的合规关系重排，须重裁锚点；
4. 若 owner 裁定"命题不得新增版本"⇒ 重定义无处落，H2 只能整条转 `unquantified`（ACCT A-2.3 第 3 条阶梯）。

### 2.3 兼容影响（下游怎么变）

- **H2 语义改变**：由「混合金属隐含单位收入的比值」变为「分金属实现单价（同表同注）经价格归一化后的相对实现率」⇒ **原 ±5% 无继承性**，阈值须在重定义后重取；
- **作用域必须扩到 parameter_id**：A-6.3 第 3 条要求 `hypothesis_id + parameter_id`；重定义后 H2 应绑定 `ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027`（及金的伴随 id），旧 id 的 falsifier 保持不可执行（IND L331）；
- **写入面不在本工位**：改 `hypotheses` 属实现者/编排层（新版本追加，旧快照保留供 I-12）；
- **不放行**：新 id `released=false`、`low/base/high=null`，锚点判定不构成参数放行；
- **I-11-C**：复用 `falsifier.threshold/threshold_basis/revert_rule`，重定义须同步，否则反方检验会拿旧口径判新披露。

### 2.4 恢复规则（追加式）

新证据/新版本 ⇒ 本目录追加 `h2_baseline_r2.json` + `ruling_h2_r2.md`（标 `supersedes: ruling_h2.md#step1`）；**不回改本文件、不改两半区与 `OPEN2-*`/`HYPOTHESES-V4-MERGE` 任何字节**；`hypotheses.json` 侧只能由有写入面者**新增版本**。

---

## ③ 第二步 · 价格归一化基准**四要素**（逐项回源）

**总判定：`NOT_ESTABLISHED`（1/4 齐：仅 B4 成立）。**

| 要素 | 判定 | 证据位置（文件 + 行号/leaf + 逐字引文要点） | 缺口（实测） |
|---|---|---|---|
| **B-1 价格序列** | ❌ `NOT_ESTABLISHED`<br>子事实 `price_rows_available=true` | ✅ **数据在盘上**：① `I-10-A/…/source_extracts/CN-ZIJIN-2025.txt`（sha `196f2c54…3591`，763,644 B）**L3383–L3453**（= AR2025 leaf 36）逐字：`品种 / 单位 / 2025 年终价 / 较年初增减(%) / 2025 年均价 / 同比(%) … 黄金 伦敦金现货 美元/ 盎司 4,308 62.8 3,439 44.0 … 铜 伦铜现货 美元/ 吨 12,504 44.0 9,945 8.7 … 国内现货 元/ 吨 99,480 35.4 81,141 8.2`；② AR2024 原件（sha `004f733e…7a89`）**leaf 35** 逐字：`2024 年均价 2,388 558 28 7,221 9,147 75,019 2,779 23,416 2,073 17,383` + `同比 (%) 23.0 24.1 21.1 29.8 7.9 9.7 5.0 8.2 -3.1 10.3`；③ 会计面同类披露最小集 `I11A-OPEN-ACCT/ruling.md` **L90**「价格假设：所用价格序列、币种、基准日（`as_of`），及其原文出处」 | **无指派**：对 `execution_runs/**/*.md` 检索 `价格序列\|价格基准\|TC/RC 净价` 共 15 命中，**0 条指派**（全部是"要求/缺什么"登记句：MERGE L234、IND L305/L373、`OPEN3-E1-ACCT-RULING` L278「H2 价格基准 ❌ 未动」）。10 条候选（5 金属 × 伦敦/国内现货）× 2 货币 × 2 形态（年均价/年终价），**用哪一条未定**；无汇率规则；**年均价构造方法（算术/加权/采样）未披露** ⇒ 序列不可执行 |
| **B-2 期间** | ❌ `NOT_ESTABLISHED`<br>子事实 `price_periods={FY2024,FY2025}` | ✅ 声明的期间：`hypotheses_v4.json` **L305–L307/L355** `"base_period_start": "FY2023", "base_period_end": "FY2025"`、`"effective_period": "FY2027"`、`"observation_date": "2027年年度报告披露日（预计2027-03前后）…"`；✅ 可得两期：AR2024 leaf 35、AR2025 leaf 36（同上） | **(a) 缺 1 期**：AR2024 全文检索 `2023 年均价\|2023年均价` 命中 **0**；`年均价\|年终价` 全文仅 3 处（2024 年终价行 / 2024 年均价行 / 叙述行）；`company-wiki/companies/紫金矿业/raw/financial_reports/annual/` **只有 FY2024、FY2025 两份 PDF**（与 OPEN2 `NE-3` 一致）⇒ 声明基期 3 期中缺 FY2023；**(b) 对齐规则 0 处文本**：年均价 vs 年终价、基期窗口如何与 FY2027 观察期配对、季报是否入样，盘上未定义；**(c) 跨期不可复算**：见 §③.1 `XC-01` |
| **B-3 净价口径** | ❌ `NOT_ESTABLISHED` | ✅ 被观察侧口径：`P2_zijin_44_48.txt`（sha `073276d2…f159`）**L53/L101** 逐字 `单价（不含税）`；**L57** `810.17 730.98 63,613 69,665 71,422 14,999`、**L107** `533.39 504.30 56,342 63,180 65,894 14,921`；✅ TC/RC 概念出现但无折减口径：`CN-ZIJIN-2025.txt` **L5437** `…铜精矿加工费已跌至历史低位；中国铜原料采购小组（CSPT）计划减产以应对原料不足…`；✅ 命题自认缺口：`hypotheses_v4.json` **L279/L372** `…相对市场价还受结算净价/应付比例/库存时点影响` / `若结算净价/应付比例（TC/RC、payability）被单独列出，隐含价格需再拆一层，否则价格与加工费会双计`；✅ 范围差：`P2` **L97/L193 注1** `本表不含非控股企业的相关数据。` | **桥不存在**：现货序列 ↔ 实现单价之间的 **VAT / TC-RC / payability / 权益金 / 产品形态**折减状态与换算式，原文与已签裁定**均 0 处**。且同金属不同形态价差显著（FY2025 铜精矿 63,613 vs 电解铜 71,422 元/吨，−10.93%；FY2024 56,342 vs 65,894，−14.50%）⇒ 现货精铜价与实现单价**不同层**，无桥即比值不可定义 |
| **B-4 来源与取回时点** | ✅ `ESTABLISHED` | AR2025 `…2025年年度报告.pdf.source.json`：`content_sha256=01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d`、`byte_size=79,925,886`、**`retrieved_at=2026-07-31T21:23:16Z`**、`provider=cninfo`、`provider_document_id=1225023658`、`filing_date=2026-03-20`、`source_url=…/new/disclosure/detail?stockCode=601899&announcementId=1225023658…`、`transport_url=https://static.cninfo.com.cn/finalpage/2026-03-21/1225023658.PDF`、`http_status=200`；AR2024 同结构：`content_sha256=004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89`、`byte_size=32,100,114`、**`retrieved_at=2026-08-01T07:10:51Z`**、`provider_document_id=1222870413`、`filing_date=2025-03-21`；抽取件 `CN-ZIJIN-2025.txt` 763,644 B / `196f2c54…3591`、`P2_zijin_44_48.txt` 17,810 B / `073276d2…f159`；**第二条独立复核路径**：`pdftotext -enc UTF-8 -f 36 -l 36 <AR2025.pdf> -` 与抽取件同值、`-f 35 -l 35 <AR2024.pdf> -` 复现 2024 年均价行 | — |

### 3.1 `XC-01` 跨期可复算性探针（**不是阈值、不是归一化比值**）

用 AR2024 leaf 35 与 AR2025 leaf 36 的年均价重算同比，与各自披露的 `同比(%)` 比对（自算，未读写文件）：

| 序列 | FY2024 | FY2025 | 重算 | 披露 | 差(pp) |
|---|---|---|---|---|---|
| 金-伦敦(美元/盎司) | 2,388 | 3,439 | +44.0117 | 44.0 | 0.0117 |
| 金-国内(元/克) | 558 | 794 | +42.2939 | 42.9 | **0.6061** |
| 银-伦敦(美元/盎司) | 28 | 40 | +42.8571 | 41.6 | **1.2571** |
| 银-国内(元/千克) | 7,221 | 9,678 | +34.0258 | 34.7 | **0.6742** |
| 铜-伦敦(美元/吨) | 9,147 | 9,945 | +8.7242 | 8.7 | 0.0242 |
| 铜-国内(元/吨) | 75,019 | 81,141 | +8.1606 | 8.2 | 0.0394 |
| 锌-伦敦(美元/吨) | 2,779 | 2,870 | +3.2746 | 3.3 | 0.0254 |
| 锌-国内(元/吨) | 23,416 | 22,889 | −2.2506 | −2.3 | 0.0494 |
| 铅-伦敦(美元/吨) | 2,073 | 1,963 | −5.3063 | −5.3 | 0.0063 |
| 铅-国内(元/吨) | 17,383 | 16,874 | −2.9281 | −1.6 | **1.3281** |

`worst = 1.3281pp`；**6/10 落在 0.05pp 内，4/10 超 0.5pp**。白银-伦敦可用整数位舍入解释，**铅-国内（五位精度）与金-国内、银-国内无法用显示值舍入解释** ⇒ 两份年报的年均价**构造方法不透明、跨期不可复算延伸**。
**用途**：只作 B-1/B-2 的实测支撑；**不产出阈值、不产出归一化比值、不作参数取值**（把重算比值当基准即 `oracle §④ C.3` 明令禁止的"跳过净价桥直接除"）。

---

## ④ 第三步 · 给数，还是维持 `BLOCKED`

# 结论：**维持 `BLOCKED` —— `h2_value = null`，`h2_status = still_blocked`，未签署 `decision_sha256`。**

### 4.1 给数门（`oracle §④ C.1`）逐条核对

| # | 条件 | 现状 | 判定 |
|---|---|---|---|
| 1 | 口径锚点 ∈ {新 id, 旧 id} | `requires_redefinition`（口径已变、observable 未重定义） | ❌ **T-1 触发** |
| 2 | 四要素全 `ESTABLISHED` | B1 ❌ / B2 ❌ / B3 ❌ / B4 ✅（1/4） | ❌ **T-2 触发** |
| 3 | A-6.3 ① 可复算观测量 | `falsifier.observable` 仍指旧口径、`source_route` 指向产销量表铜当量分母，重定义未发生 | ❌ |
| 4 | A-6.3 ② 数值有可核基础（四类之一） | (i) 无来源披露容差；(ii) 同口径历史离散需"同口径 + ≥2 可比期 + 过程归档"，而价格序列既未指派、也无净价桥、且跨期不可复算（§3.1）⇒ **同口径不成立**；(iii) 无准则/交易所明文；(iv) `expert_assumption` **不适用于"观测量与基准未定义"**（口径未定 ⇒ 专家假设无处安放） | ❌ |
| 5 | A-6.3 ③ 非实现者签署 + `decision_sha256` + 作用域 | 本次判 `blocked`，**未签署**（`h2_decision_sha256 = null`） | ❌ |
| 6 | A-6.3 ④ 追加式版本化 | 未发生（本工位无 `hypotheses` 写入面，也未获授权改写） | ❌ |

⇒ 任一即维持 `not_reviewed`；此处 **6 条全不满足**（`T-1/T-2/T-3` 全部触发）。

### 4.2 实测缺口清单（`blocked` 的具体理由，可逐条复核）

1. **口径缺口**：`falsifier_full_unchanged = true`（registration.md L79）+ v4 L352 仍为跨层相除句 ⇒ `requires_redefinition`；
2. **序列缺口**：候选 10 条 / 2 货币 / 2 形态，**指派 0 条**；年均价构造方法未披露；无汇率规则；
3. **期间缺口**：声明基期 FY2023–FY2025（3 期）vs 本地年均价 2 期；`2023 年均价` 命中 0；`annual/` 仅 2 份 PDF；期间对齐规则 0 处文本；跨期同比 4/10 差 >0.5pp；
4. **净价缺口**：spot ↔ 实现单价的 VAT/TC-RC/payability/权益金/产品形态桥 0 处；同金属形态价差 −10.93%（FY2025 铜精矿 63,613 vs 电解铜 71,422）实证不同层；
5. **签署缺口**：按 `IND L345`，**不得为凑齐三条 `pjr` 而强行给 H2 一个数字**；按 `ACCT L296`，数值是否恰当属 BLOCKED-6a，本工位只提供"证据 + 缺口"，不提供数字。

### 4.3 红绿变异实测（`rc: 0 = 接受 / 1 = 拒绝`）

**冻结顺序**：写 `oracle.md` → 复算 sha256 = `19317143039ce1905cae742e4de321127d309deb73a474845c3e953a75ea7aff`（15,820 B，无 BOM、CR=0）→ **再**跑 `python -X utf8 -c <inline judge>`（不读写文件）。

| # | 用例 | action | mode | 实测 rc | 冻结期望 | 结果 |
|---|---|---|---|---|---|---|
| 1 | `ACTUAL`（本次真实证据） | `give` | STRICT | **1** | 1 | ✅ 判 blocked 的分支红 |
| 2 | `ACTUAL` | `keep_blocked` | STRICT | **0** | 0 | ✅ 绿 |
| 3 | `CF-ANCHOR-FIXED`（反事实：observable 已重定义+签署版本化，四要素=实测） | `give` | STRICT | **1** | 1 | ✅ 隔离四要素门 |
| 4 | `CF-ANCHOR-FIXED` | `give` | `MUT-4`（弃 B1∧B2∧B3） | **0** | 0 | ✅ **变异存活** |
| 5 | `SYNTH-FULL`（四要素+锚点+A-6.3 全齐，合成夹具） | `give` | STRICT | **0** | 0 | ✅ 绿：判据不为难 |
| 6 | `SYNTH-FULL` | `keep_blocked` | STRICT | **1** | 1 | ✅ 红：不许赖 `blocked` |
| 7 | `SYNTH-MISS-B1` | `give` | STRICT / `MUT-1` | **1 / 0** | 1 / 0 | ✅ B-1 承重 |
| 8 | `SYNTH-MISS-B2` | `give` | STRICT / `MUT-2` | **1 / 0** | 1 / 0 | ✅ B-2 承重 |
| 9 | `SYNTH-MISS-B3` | `give` | STRICT / `MUT-3` | **1 / 0** | 1 / 0 | ✅ B-3 承重 |
| 10 | `SYNTH-OLD-ANCHOR`（锚旧铜当量 id，四要素齐） | `give` | STRICT / `MUT-5` | **1 / 0** | 1 / 0 | ✅ 判据 A 承重 |
| 11 | `SYNTH-NO-SIGN`（四要素齐但无签署/无新版本） | `give` | STRICT / `MUT-6` | **1 / 0** | 1 / 0 | ✅ A-6.3 ③④ 承重 |

```
failures   = 0
EXPECT_RC  = 0     （16 行期望逐条比对全中）
OVERALL_RC = 1     （各用例 rc 按位或；含 1/3/6/7–11 的红例，按 oracle §⑤ 预期为 1）
python exit code = 0（以 EXPECT_RC 退出）
```

**双向证明**：`SYNTH-FULL + give = 0`（不是"一律 blocked"）；`SYNTH-FULL + keep_blocked = 1`（不是"一律放行"）；`CF-ANCHOR-FIXED` 与 `SYNTH-MISS-B*` 在对应变异下 **1 → 0** ⇒ **判据改弱后，一个不该给数的阈值确实能通过** ⇒ B-1/B-2/B-3 与判据 A、A-6.3 ③④ 是**承重判据**。
**合成夹具声明**：`SYNTH-*` 字段带 `SYNTHETIC` 语义、sha 用 `0…0`，**不构成任何现实主张**，不进入 `h2_baseline.json` 证据表。

---

## ⑤ 不授予什么（明确清单）

1. **不给 H2 数值**：`h2_value = null`、`h2_value_status = NOT_ESTABLISHED`；**±5% 仍未采用**，替代数值仍 `BLOCKED`；
2. **不签署**：`h2_decision_sha256 = null`（四要件不齐，按 fail-closed 不签）；
3. **不动阈值字段**：`threshold_basis` 仍 `professional_judgement_required`；`threshold_review_status` 仍 **`not_reviewed`**；命题 `state` 仍 `pending_professional_decision`；
4. **不放行任何参数**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027`、`ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027`、`ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027` 及锌/银销量槽的 `low/base/high` **全 null**、`released=false`；`_PLACEHOLDER` 维持；
5. **不解除任何 BLOCKED**：`ACCT BLOCKED-6a/6b/6c`、`IND BLOCKED-1…BLOCKED-7`、`OPEN-6`、`OPEN-2` —— 一条未关；
6. **不产生 `I-11-B` 的 ACCEPT**、不写 `approved_frozen`、不声称 I-11-A/I-11-B 验收；
7. **不触发任何 falsifier / 校准边界 / 情景切换**（A-6.1 L230）；
8. **不代签会计面**、不代写 `hypotheses.json` / `model_cards.md` / `validate_hypotheses.py`；
9. **不改** `OPEN2-*`、`HYPOTHESES-V4-MERGE`、两半区裁定、`OPEN6-TOLERANCE-*`、`BLOCKED6C-*`、封盘 `I-11-A/a20260919-01` 任何字节。

---

## ⑥ 会签提请（给会计面 / 行业面）

> 本节是**提请**，不是批准；两条都须各自出具新载体（追加式），本工位不代签。

### 6.1 给**会计面**（`I11A-OPEN-ACCT` 继任 / `OPEN-6-ACCT-R2`）

| # | 请会计面裁定的事项 | 我方提供的材料 | 我方明确不让渡的 |
|---|---|---|---|
| A | **B-3 净价口径**：认定 现货价格序列 ↔ `单价（不含税）` 之间的 VAT / TC-RC / payability / 权益金 / 产品形态桥，或明文裁定"不做价格归一化，改走 A-6.3(ii) 同口径历史离散" | `h2_baseline.json → step_2.elements[B3].found/gap`（4 条证据 + 缺口实测） | 我**不代**会计面定净价口径，**不给**换算系数 |
| A' | **B-1 系列指派的"币种 + 基准日"面**：会计面 A-2.2 L90 要求「价格序列、币种、基准日（`as_of`）、原文出处」——请确认该最小集是否适用于 H2（我按同类规则类比适用，**请确认或纠正**） | `h2_baseline.json → B1.found[B1-D4]`（ACCT L90/L91 逐字） | 我不改写 A-2.2 的适用范围 |
| B | **B-2 期间基期**：是否允许把新 id 的 `base_period` 由 FY2023–FY2025 收窄为 FY2024–FY2025（本地仅两期年均价），或要求补 FY2023 年报原件 | `h2_baseline.json → step_2.elements[B2].gap`（命中 0 与目录枚举） | 我不改 `base_period` 字段 |
| C | **A-6.3 ② 可核基础归类**：重定义后的 H2 数值应归 (ii) 同口径历史离散 还是 (iv) `expert_assumption` + 敏感性区间 | 本文件 §4.1 第 4 行 | 我不在四要素齐之前给任何数值基础 |
| D | **`BLOCKED-6a` 状态**：本工位**未**解除它（四要件 0/6）；请在收到四要素齐的载体后再裁 | §4.1、`h2_baseline.json → step_3` | 我不要求提前解除 |

### 6.2 给**矿业行业面**（本席位的后续复裁，或另一位矿业 reviewer）

| # | 事项 | 说明 |
|---|---|---|
| I | **B-1 系列的行业选择**（金属 × 市场 × 形态）：铜/金/锌/银 各用 伦敦现货 还是 国内现货？年均价 还是 年终价？ | 需与 A 面（币种/基准日）同批裁定，否则仍缺指派 |
| I' | **重定义后的 observable 文本**（我给出建议口径，**不落文件**）：`下一年度年报「按产品划分的销售详情」中该金属各产品行 单价（不含税）与销售数量同表同注配对得到的实现单价，经指派价格序列归一化后与基期（FY202x–FY202y）之比`；**禁止**任何形式的分部收入 ÷ 分金属销量 | 需落命题新版本（实现者写入面）+ `hypothesis_id`/`parameter_id` 作用域 |
| I'' | **阈值取数路径**：`IND L307` 反例要求"用本地可核历史序列证明价格中性年份波动 ≤5%"；当前跨期不可复算（§3.1）⇒ 该反例**尚未满足**，±5% 不恢复 | 需 B-1/B-2/B-3 齐后再取数 |
| I''' | **`revert_rule` 待补**：重定义后须加入"价格正常化口径变化 ⇒ 不直接改价、先查口径"分支（现有 L357 只覆盖价格/结构/系数/库存时点） | 属命题新版本内容 |

---

## ⑦ 边界（可核）

1. **写入面恰 4 个文件**：`oracle.md`、`h2_baseline.json`、`ruling_h2.md`、`handoff.json`，全部位于 `execution_runs/OPEN6H2-PRICE-NORMALIZATION-BASELINE/a20260926-01/`；**`.planning` 之外 0 字节**（`company-wiki` 只 `Get-FileHash` / JSON 解析 / `pdftotext … -` 进管道，未落盘）。
2. **零 git 写**：未执行 `add/commit/checkout/stash/restore/reset` 任何变体；**未执行 `git status`**；收尾仅 `git -c core.quotepath=false diff HEAD --name-only`。
3. **零网络**：`network_requests = 0`，全部证据取自盘上语料。
4. **零只读面改动**：收尾复算 `hypotheses_v4.json = ebf6fa4e…`、`OPEN2 ruling.md = f927c44c…`、`substitute_caliber.json = 649a9ff8…`、两半区 `8bc685a4…` / `f3040df0…`、`merge_ruling.md = 2d214bab…`，与开工前读取值逐一相同。
5. **零 status 变更 / 零代签**：未改任何 `status`/`state`/`decision`/`threshold_basis`/`threshold_review_status`；`handoff.json → releases_nothing = true`。
6. **载体格式**：四件均 UTF-8 无 BOM、CR=0（纯 LF）；两个 JSON 写后 `json.load` 重解析通过。
