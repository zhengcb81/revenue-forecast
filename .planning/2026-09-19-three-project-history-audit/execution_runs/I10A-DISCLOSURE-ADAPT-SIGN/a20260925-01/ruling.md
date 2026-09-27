# I10A-DISCLOSURE-ADAPT-SIGN · a20260925-01 — `ruling.md`

**Station**：`execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/`
**角色**：行业/会计专业 reviewer（**非实现者**）· `implementer_signed = false`
**判定对象**：C7 = `card_I-11-B.md` 前提第二句「I-10-A 已为实际采用的公司/分部/模型签署披露适配口径」
**日期**：2026-09-25（UTC；写入时刻 `disclosure_adaptation_v2.json → provenance.signed_at_utc`）
**`decision_sha256`**：`86d0a80e3de76325ba4ac12376c7beb40770e063f2b77e8af6ee104e47c6f22b`（求值方式见 §4.3，复算 3 次）
**冻结 oracle**：`oracle.md` = `f28ddd4a33606e8dd8cd9a2e10a615222f900114056cba6c450b01ca75e8cfd3` / 18,078 B（写于**首个判据运行之前**，此后未改）

---

## ① 身份与授权链

### 1.1 我是谁 / 我不是谁

- 我是本卡指派的**行业/会计专业 reviewer**，**非实现者**：`implementer_signed = false`，`implementer_never_signs_acceptance = true`。
- 我**不代签**任何其他角色：不签实现者、不签独立验证者、不签精算 reviewer、不签 owner、不签 I-10-A 的 carrier。
- 我**只**对 `disclosure_adaptation` 一栏作判定；`accuracy`、参数、阈值、放行一概不在我的签署作用域内。

### 1.2 `execution_v2/card_I-11-B.md` 的「前提」两行（逐字）

> L7：`前提：`
>
> L9：`- I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。`

同源原文在 `execution_v2/research_cards.md` **L374**（逐字同句）。

- 第一句 = **C1**，我独立核对（不是照抄）：`execution_runs/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json`
  实测 `hypotheses[0].state = "approved_frozen"`、`decision.decision = "approved_frozen"`、
  `decision.decision_sha256 = 4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f`
  ⇒ **C1 已达成**（非我所授，我不改它一个字节）。
- 第二句 = **C7**，是本卡要做的事。

### 1.3 C7 原文（`I11A-OPEN-MERGE` 逐字）

`execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` **L117–L125** 为 `i11b_unlock_conditions`
数组；**第 7 条在 L124，逐字**：

> `card_I-11-B.md L9：I-10-A 为实际采用的公司/分部/模型签署披露适配口径（现 review.md 记 disclosure_adaptation = NOT granted）`

同文件 **L114** `"i11b_unblocked": false`、**L115** `"i11b_verdict": "BLOCKED"` —— 本卡**不改变**这两个值。

### 1.4 我承接的卡面授权（I-10-A）

`execution_v2/card_I-10-A.md`：
L3 卡名「先行完成实际采用模型的专业披露适配」· L5「Owner：行业/会计reviewer主责；独立验证者核对原文和历史收入」·
L10 前提「先冻结本次实际采用的公司/分部/模型清单」· L19 动作5「逐公司/模型签署 disclosure_adaptation 资格」·
L26 停止条款3「…允许其他已合格分部保留局部结果，但不放行整个公司正式预测」· L29 验收「每个实际采用的公司/分部/模型完成 M 卡 D/E 专业适配与独立签署」。

---

## ② 「实际采用」的逐项清单 + 证据行号

**唯一清单来源（回源，非记忆）**：`execution_runs/I-10-A/a20260923-01/evidence/I-10-A/selected_model_manifest.json`
= `96b0f56e7ab6505f2189efe25d7da77c439740df7c93e531a8a1dceb0f71ef49` / **22,358 B**（本工位实测）。
其 **L6** 逐字：`frozen_scope_rule: 卡文前提2：先冻结本次实际采用的公司/分部/模型清单；只要求这些模型完成企业披露适配，不要求未使用模型全部适配。未使用模型标 not_selected，不宣称企业适配通过。`
（`oracle.md(I-10-A) L13` 亦声明该 manifest 为其 frozen input。）

### 2.1 实际采用 = 6 case / 3 公司 / 6 分部 / 4 model_id

| # | case_id | 公司 | 分部 | model_id | M 卡 | manifest 行号（`segment` / `status:adopted` / `case_id` / `model_id` / `adaptation_scope`） |
|---|---|---|---|---|---|---|
| 0 | **ZJ-MIN-M09** | CN-ZIJIN-2025 紫金矿业 | 矿产品分部 | `resource` | M09 | L40 / **L43** / **L46** / L47 / L49 |
| 1 | **ZJ-SMT-M09** | CN-ZIJIN-2025 紫金矿业 | 冶炼产品分部 | `resource` | M09 | L57 / **L60** / **L63** / L64 / L66 |
| 2 | **XM-PHONE-M03** | HK-XIAOMI-2025 小米集團－Ｗ | 智能手機（手機×AIoT 分部產品線） | `unit_sales` | M03 | L109 / **L112** / **L115** / L116 / L118 |
| 3 | **XM-EV-M03** | HK-XIAOMI-2025 小米集團－Ｗ | 智能電動汽車及AI等創新業務分部 | `unit_sales` | M03 | L149 / **L152** / **L155** / L156 / L158 |
| 4 | **MS-PBP-M05** | US-MSFT-2026 MICROSOFT CORP | Productivity and Business Processes | `subscription` | M05 | L185 / **L188** / **L191** / L192 / L194 |
| 5 | **MS-IC-M06** | US-MSFT-2026 MICROSOFT CORP | Intelligent Cloud | `usage_platform` | M06 | L201 / **L204** / **L207** / L208 / L210 |

期间：第 0–3 项 = **FY2025（已结束）**；第 4–5 项 = **FY2026（US FY ended 2026-06-30，已结束）**（manifest L26 / L94 / L171）。

### 2.2 明确**未**采用（不得宣称适配）

| 公司 | 分部 | manifest 行号 | 不采用理由（manifest 逐字要点） |
|---|---|---|---|
| CN-ZIJIN-2025 | 贸易分部 | L73 / L76 `not_selected` / L78 | 无量价经营数据分解，`M02 direct_revenue` 不构成独立复建 |
| CN-ZIJIN-2025 | 其他分部 | L81 / L84 / L86 | 机制混合不可识别，`special_review` 未决（AD-7） |
| HK-XIAOMI-2025 | IoT與生活消費產品 | L125 / L128 / L130 | 多品类聚合、仅分类收入增速，无单位量价分解 |
| HK-XIAOMI-2025 | 互聯網服務 | L133 / L136 / L138 | 机制混合（M18/M19/M06），披露无 activity×rate 分解（AD-7） |
| HK-XIAOMI-2025 | 其他相關業務 | L141 / L144 / L146 | 占收入 0.9% 且无量价分解 |
| US-MSFT-2026 | More Personal Computing | L217 / L220 / L222 | 三类收入流混合，FY2026 10-K 无任何量价分解（AD-7） |

### 2.3 模型覆盖（本工位解析 manifest 实测）

- `model_registry_coverage.total_models` = **31**（manifest L230）
- `adopted` model_id = **4**：`resource`(M09)、`unit_sales`(M03)、`subscription`(M05)、`usage_platform`(M06)（L231–L236）
- `not_selected` 数组 = **30 条**（其中 3 条是 `reason_note` 的部分采用：M05/M06/M09），**完全未被任何公司采用的 model_id = 31 − 4 = 27**
- `coverage_claim`（L269）：`31/31 model_ids 登记完毕：4 个 adopted（6 个 case），其余 not_selected 并给出理由；not_selected 不宣称企业适配通过`
- `special_review_routing`（L270）：AD-7 + 保险口径 `actuarial_reviewer N/A` 交独立 reviewer 裁定

> **实测差异（记录，不改封盘件）**：`oracle.md(I-10-A) L24` 逐字写 `All other model_ids (26 of 31; M03/M05/M06/M09 are the only adopted models)`，
> 但 31 − 4 = **27**；`not_selected` 数组里 **M03 没有条目**（M05/M06/M09 有 `reason_note`，M03 完全没有）。
> 该行属 R1/R10「label-only」期望行，**不影响任何判据**；我按实测 27 记录，不照抄 26，也不回改封盘 `oracle.md`。

---

## ③ 我**独立复核**了什么（文件 + sha，均为本工位实测；不引实现者自述作为依据）

### 3.1 逐文件实测（只读；sha256 小写 / 字节）

| 文件（相对 `execution_runs/I-10-A/a20260923-01/`） | sha256（我实测） | 字节 | 我做了什么 |
|---|---|---|---|
| `evidence/I-10-A/disclosure_qualification.json` | `6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb` | 8603 | **被取代的机读源**：全文 214 行、CRLF；6 case 的 `status/signed/prepared_state` 逐条读 |
| `evidence/I-10-A/selected_model_manifest.json` | `96b0f56e7ab6505f2189efe25d7da77c439740df7c93e531a8a1dceb0f71ef49` | 22358 | 自行解析 `companies[].segments[].adopted_models[]` 得 6 case（**非读其 coverage_claim 文字**） |
| `evidence/I-10-A/historical_reconciliation.json` | `ce222355e2190dd4e956d85e7dd72e7176d1d149aa6002f8c209571ff16a0abc` | 16485 | 取 4 案 `sum_rebuilt/sum_disclosed/residual/within/tolerance` 与 2 STOP 的 `E_status/level1/residual` |
| `evidence/I-10-A/oracle_expected.json` | `bf212696259d8c289262b50d544278573544be57c68526a58742d6db37fd9d01` | 7017 | 取 4 案 `aggregate_tolerance_rel`（先冻结的容差）与 2 STOP 的 `expected_E_status/expected_probe_status` |
| `evidence/I-10-A/historical_mapping_probe.json` | `b4ef9b96c2578f070cc7945e63ab26b41b4a9f20a1587398c54d8c11ed87b75a` | 8944 | 取 `counts_measured/counts_ok/low_base_high_identical` 与 `not_run`（2 STOP） |
| `evidence/I-10-A/disclosure_mapping.json` | `7e03ea748cb99d74038daeef3b529b824f1300c17ee841aaf8fc19b9f1501e0b` | 65783 | 6 case 的 `missing_fields` / `zero_filled` / `review_signature`（L768/L1095/L1253/L1409/L1479/L1570 全为 `signed:false`） |
| `evidence/I-10-A/qualification.json` | `2a2a14158bb020d042b8f8bebbbc5d6ef0b264214c9ae5d84d92d52ed202f444` | 32841 | **父转述的核对**：L21 `disclosure_adaptation="unmapped"`、L23 `signed_machine_face=false`、L24 `accuracy="unproven"`、L26 `formal_company_forecast_cleared=false`、L74 `signed_count=4`、L75 `stopped_count=2` |
| `oracle.md`（I-10-A） | `5cdd733189686996a264d674ea70d17bbb471b55c611110b969f0b3c449de6dd` | 13121 | 冻结的 6-case 表 L15–L22、手算表 L47–L100、容差 §2 L118–L123、probe 期望 §3、攻击面 §5 |
| `reviewer_report.md` | `6bd90c83634624fafe81ddf0a91498102951932e26776fd1b4172ae1c214decb` | 35164 | **carrier（另一名独立 reviewer，非实现者）**：L15 verdict、L19–L26 授予表、L234 签署效力、L236–L243 逐 case 签署表、L292–L298 签署区 |
| `handoff.json`（I-10-A） | `a3f2208ac8601e1a1711d3f6aa30b3e935148bb93017c8a21d350c10dbea3c58` | 40574 | L5 `status=accepted_scoped`、**L11 `implementer_signed=false`**、L151/L161 机读面 `unmapped/signed=false`；**实测 `reviewer_signed` 键不存在**（父转述属实） |
| `review.md` | `dbe63410b09e1732c73726c6ba44e54a8d2b38d25440515cf17cc447374cd2c3` | 29452 | L139「机读状态在卡内仍为 unmapped、signed=false」、L156「机读面保持 unmapped / signed=false」 |
| `decision.md` | `63afc8dd8707b3353ca205fe8b711ea3149a767d3ed5ae62753ff0c6660a815d` | 18035 | 仅作存在性/哈希核对（实现者自述，**不作依据**） |
| `source_extracts/CN-ZIJIN-2025.txt` | （随 attempt 冻结） | 763644 | 原文行核（见 3.3） |
| `source_extracts/HK-XIAOMI-2025_decoded.txt` | （随 attempt 冻结） | 721603 | 原文行核（见 3.3） |

### 3.2 我自己算的数（不复制任何现成残差）

用披露的**销售数量 × 披露单价**独立重算（本工位 Python，一次性）：

| case | 我算的 Σrebuilt | 我算的 Σdisclosed | 我算的残差 | 冻结容差(相对) | 结论 |
|---|---|---|---|---|---|
| ZJ-MIN-M09 | 131,491,532,271 | 131,489,500,000 | **−2,032,271** | ±0.05% | \|r\|/Σ = 0.0015456% ✅ 内 |
| ZJ-SMT-M09 | 183,988,605,486 | 183,988,510,000 | **−95,486** | ±0.05% | 0.0000519% ✅ 内 |
| XM-PHONE-M03 | 186,461,240,000 | 186,439,777,000 | **−21,463,000** | ±0.05% | 0.0115120% ✅ 内 |
| XM-EV-M03 | 106,051,877,022 | 106,069,513,000 | **+17,635,978** | ±0.10% | 0.0166268% ✅ 内 |

四案逐位等于 `oracle.md(I-10-A) §1` 冻结期望与 `oracle_expected.json`；复算命令与结果在本轮 shell 记录中，
并由 `check_signoff.py` G3 在每次判据运行时重新比对封盘件（不同值即 reject）。

另两笔独立复算：
- 保留案例 **冶炼产锌**：403,324 × 20,327 = **8,198,366,948** vs 披露 **8,198,230,000** → −136,948（−0.0017%，线级 ±0.10% 内）。
- 小米 **附註5 分部收入行** 构成闭环：186,439,777 + 123,200,191 + 37,440,346 + 4,136,860 = **351,217,174**；
  351,217,174 + 106,069,513 = **457,286,687** 千元 —— 与同一行披露的「小計」「總計」逐位相等。

### 3.3 原文行核（我自己 grep 到的，不引他人引文表）

| 抽取件 | 行 | 我读到的原文要点 |
|---|---|---|
| `CN-ZIJIN-2025.txt` | L3951–L3964 | 表头「单价（不含税）/ 销售数量 / 金额（万元）」；「金锭 **810.17** 元/克 · **49,074** 千克 · **3,975,798** 万元」（= 39,757,980,000 元，与我用的 disclosed 一致） |
| `CN-ZIJIN-2025.txt` | L4080–L4085 | 「冶炼产锌 **20,327** 元/吨 · **403,324** 吨 · **819,823**（万元）」 |
| `CN-ZIJIN-2025.txt` | L26011 / L35012–L35013 | 分部附注「**109,977,556,345**」；「**138,271,672,956**」「**189,683,879,295**」 |
| `HK-XIAOMI-2025_decoded.txt` | L1403–L1405 | 「…日止年度的 **165.2 百萬部**…」 |
| `HK-XIAOMI-2025_decoded.txt` | L1435–L1436 | 「…每部人民幣 **1,128.7** 元…」 |
| `HK-XIAOMI-2025_decoded.txt` | L1581–L1583 | 「…日止年度的 **411,082 輛**…」 |
| `HK-XIAOMI-2025_decoded.txt` | L1609–L1610 | 「…每輛人民幣 **251,171** 元…」 |
| `HK-XIAOMI-2025_decoded.txt` | L17788–L17790 | 附註5 分部收入行（含 `186,439,777…351,217,174…106,069,513…457,286,687`） |

L2 桥（我复算）：138,271,672,956 − 131,489,500,000 = **+6,782,172,956**；189,683,879,295 − 183,988,510,000 = **+5,695,369,295** —— 与封盘件一致，且**不进容差门**（`oracle.md(I-10-A)` L125–L126：L2 桥为 scope bridge，informational）。

### 3.4 我核对到的一处封盘件内部数字出入（不改、只记）

`oracle_expected.json` ZJ-MIN `aggregate_tolerance_abs = 65,724,750`，但 0.0005 × 131,489,500,000 = **65,744,750**
（差 −20,000 / −0.03%）。我复算确认；该字段**不被任何 gate 使用**（gate 用 `aggregate_tolerance_rel`），
残差 2,032,271 对任一值都有 30× 余量 ⇒ **对本次判定零影响**。按冻结纪律**不回改**。

### 3.5 我**没有**采用什么作依据

- **不采信实现者自述**：`decision.md` 的结论段、`handoff.completed_steps`/`next_action` 的自评，一律不作为签署依据（仅作存在性与哈希核对）。
- **不读取**错题作答的 `OPEN4-SOURCE-REVIEW-ACQUISITION`（全程未打开）。
- **不联网**（0 次网络调用）、**不做 git 写**、**不写 `.planning` 之外任何路径**（含 `company-wiki` 产品仓）。

---

## ④ 每项 `disclosure_adaptation` 结论、理由、允许/不允许披露

### 4.1 逐项结论

| # | case | `status` | `signed` | 判定 | 计入 `disclosure_adaptation_signed_count` |
|---|---|---|---|---|---|
| 0 | ZJ-MIN-M09 | `unmapped` → **`mapped`** | false → **true** | **granted_scoped** | ✅ |
| 1 | ZJ-SMT-M09 | `unmapped` → **`mapped`** | false → **true** | **granted_scoped** | ✅ |
| 2 | XM-PHONE-M03 | `unmapped` → **`mapped`** | false → **true** | **granted_scoped** | ✅ |
| 3 | XM-EV-M03 | `unmapped` → **`mapped`** | false → **true** | **granted_scoped** | ✅ |
| 4 | MS-PBP-M05 | `unmapped`（**不变**） | false（**不变**） | **not_granted — STOP_DISCLOSURE_ADAPTATION**（判定已签，资格不授予） | ❌ |
| 5 | MS-IC-M06 | `unmapped`（**不变**） | false（**不变**） | **not_granted — STOP_DISCLOSURE_ADAPTATION**（判定已签，资格不授予） | ❌ |

- `disclosure_adaptation_signed_count = **4**`（`signed == true` 的 case 数；与 I-10-A 自身 `qualification.json L74 signed_count=4` 口径一致）
- `disclosure_adaptation_not_granted_count = 2`、`disclosure_adaptation_determination_signed_count = 6`（6 条判定全部由我签署）

### 4.2 理由与披露边界（逐项；完整版在 `disclosure_adaptation_v2.json` 各 `reviewer_determination`）

**0 · ZJ-MIN-M09 → `mapped`（granted_scoped）**
- 理由：D 段 8 线逐字段在案、`missing_fields=[]`；E 段我独立复算残差 **−2,032,271 元（0.0015456%）** 落在先冻结 ±0.05% 内且等于冻结期望；probe 计数 **24**、三键同值；原文 L3958–L3964 量价核对一致。
- **允许披露**：FY2025、8 条主要矿产品线同口径「量×价」复建收入与该残差；该适配作 `historical_mapping_probe` 接线证据；L2 桥 gap **+6,782,172,956 元** 并标 `partially_explained`。
- **不允许披露**：不得称矿产品分部全部收入已适配（表外矿产品不在范围；贸易/其他分部 `not_selected`）；不得把 L2 桥静默吸进容差或称已逐项分解；不得称 accuracy 通过 / 三情景预测 / 企业适配通过；不得据此放行 CN-ZIJIN-2025；不得外推到 `not_selected` 模型（含 M10）。

**1 · ZJ-SMT-M09 → `mapped`（granted_scoped）**
- 理由：残差 **−95,486 元（0.0000519%）** 落在 ±0.05% 内且等于冻结期望；probe **9**；我复算保留案例冶炼产锌 403,324 × 20,327 = 8,198,366,948 vs 8,198,230,000 → −136,948（线级容差内）；原文 L4080–L4085 一致。
- **允许披露**：FY2025、3 条主要冶炼产品线复建收入与该残差；冶炼产锌保留案例复算；L2 桥 gap **+5,695,369,295 元** 标 `partially_explained`。
- **不允许披露**：不得称冶炼分部全部收入已适配（硫酸、电池级碳酸锂等在 E 范围残差内）；不得静默吸收 L2 桥；不得称 accuracy 通过或三情景预测；不得据此放行 CN-ZIJIN-2025。

**2 · XM-PHONE-M03 → `mapped`（granted_scoped）**
- 理由：165,200,000 × 1,128.7 = 186,461,240,000 vs 附註5 186,439,777 千元 → **−21,463,000 元（0.0115120%）**，落在 ±0.05% 内；probe **3**；原文 L1404/L1436/L17790 核对一致；附註5 构成闭环我复算通过。
- **允许披露**：FY2025 智能手機产品线「出货量×ASP」复建收入与该残差；構成桥 `trivial_composition` 验算；解码方法与 0-unmapped 复现。
- **不允许披露**：不得扩到 IoT／互聯網服務／其他相關業務（三者 `not_selected`）；不得称 accuracy 通过或三情景预测；不得据此放行 HK-XIAOMI-2025；不得在 `other_revenue=0` 口径下宣称其他业务已适配。

**3 · XM-EV-M03 → `mapped`（granted_scoped）**
- 理由：411,082 × 251,171 + 2.8e9 = 106,051,877,022 vs 106,069,513,000 → **+17,635,978 元（0.0166268%）**，落在 ±0.10% 内；probe **3**、`mut_omit_optional` **rc2 击杀**（唯一 `other≠0` case）；原文 L1582/L1610 一致。
- **允许披露**：FY2025 分部整段「交付量×每輛 ASP + 其他相關業務 28 億元」复建收入与该残差；`other_revenue` 億元粒度 ±5e7 界为容差依据；構成桥验算。
- **不允许披露**：不得把 AI 等创新业务收入单列（披露含于其他相關業務）；不得改用 backlog/订单存量口径（M29/M21 `not_selected`）；不得称 accuracy 通过或三情景预测；不得据此放行 HK-XIAOMI-2025。

**4 · MS-PBP-M05 → 维持 `unmapped` / `signed=false`（判定：not_granted）**
- 理由：FY2026 10-K 不以所需粒度披露经营量价，4 字段全 `missing`、`zero_filled=false ×4 / =true ×0`；E 未执行（`level1=null`、`residual=null`）、probe `not_run`；缺收入历史桥 ⇒ 触发 `card_I-10-A.md L26` 停止条款3。
- **允许披露**：D 段逐字段映射与会计口径已完成、缺失保留 `missing`；本判定为「不授予」的诚实出口；分部局部结果保留。
- **不允许披露**：不得写 `mapped`、不得把 `signed` 置 `true`；不得补零、不得由收入倒推席位/ARPU、不得用 RPO 摊回 ARPU；不得展示 E 复建值或残差；不得称 US-MSFT-2026 已完成适配或可进入正式预测。

**5 · MS-IC-M06 → 维持 `unmapped` / `signed=false`（判定：not_granted）**
- 理由：3 字段全 `missing`、`zero_filled=false ×3 / =true ×0`（含可选 `fixed_revenue` 也不默认补 0）；E 未执行、probe `not_run`；同判 STOP。
- **允许披露**：D 段完成、`missing` 保留；RPO 仅存量无 rollforward 故项目存量桥不可复建；本判定为「不授予」的诚实出口。
- **不允许披露**：不得写 `mapped`/`signed=true`；不得以增长率反推绝对用量、不得补零、不得由收入倒推费率；不得展示 E 复建值或残差；不得称 US-MSFT-2026 已完成适配。

**精算口径**：6 项均为 `actuarial_reviewer = not_applicable_with_reason`（三家公司均无保险报告分部；
`accounting_decision.md` L102–L106 AD-9；M23 全部 `not_selected`）——**我不代签精算 reviewer**。

### 4.3 `decision_sha256` 求值方式（可独立复算；写入前后各复算一次 + 第三次）

**preimage = UTF-8-no-BOM(`source_sha256` of `evidence/I-10-A/disclosure_qualification.json`) + `0x0A` + UTF-8-no-BOM(下方标记之间的裁定正文)，无尾随换行。**

- `source_sha256` = `6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb`（64 字节，本工位实测）
- preimage 字节数 = **3218** = 64 + 1 + **3153**（裁定正文字节）
- `decision_sha256` = `86d0a80e3de76325ba4ac12376c7beb40770e063f2b77e8af6ee104e47c6f22b`

复算步骤：① 对源文件算 SHA-256；② 从 `oracle.md`（或本文件 §4.3）取出 `--- BEGIN/END C7 RULING TEXT ---`
之间的那一行；③ 拼 `sha + "\n" + ruling_line`；④ SHA-256 → 应等于
`disclosure_adaptation_v2.json` 的 `provenance.decision_sha256`、六个
`reviewer_determination.decision_sha256`、以及 `handoff.json` 的 `decision_sha256`。

**三次求值记录**：**写入前**（`build_v2.py` 内，从 `oracle.md` 提取）= `86d0a80e…6f22b` ·
**写入后第一次**（同脚本重新从 `oracle.md` 提取复算）= `86d0a80e…6f22b`（MATCH）·
**第三次**（本文件写成后，从**本文件**标记块重新提取复算）= 见 `handoff.json` → `decision_sha256_verification`。

--- BEGIN C7 RULING TEXT ---
RULING｜C7/I-10-A disclosure_adaptation → 本 reviewer 裁定（裁定人：非实现者 行业/会计专业 reviewer；授权：execution_v2/card_I-11-B.md L9 前提第二行 逐字「I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。」+ execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json L124 C7 逐字「card_I-11-B.md L9：I-10-A 为实际采用的公司/分部/模型签署披露适配口径（现 review.md 记 disclosure_adaptation = NOT granted）」；作用域仅限 disclosure_adaptation，不含 accuracy、不含任何参数/阈值放行、不产生 I-11-B 的 ACCEPT）。裁定一（实际采用）：以 evidence/I-10-A/selected_model_manifest.json（sha256 96b0f56e7ab6505f2189efe25d7da77c439740df7c93e531a8a1dceb0f71ef49，22358 B，冻结于首个判据运行前）为唯一清单来源，实际采用 = 6 case / 3 公司 / 6 分部 / 4 model_id：ZJ-MIN-M09（CN-ZIJIN-2025 矿产品分部 resource/M09）、ZJ-SMT-M09（CN-ZIJIN-2025 冶炼产品分部 resource/M09）、XM-PHONE-M03（HK-XIAOMI-2025 智能手機 unit_sales/M03）、XM-EV-M03（HK-XIAOMI-2025 智能電動汽車及AI等創新業務分部 unit_sales/M03）、MS-PBP-M05（US-MSFT-2026 Productivity and Business Processes subscription/M05）、MS-IC-M06（US-MSFT-2026 Intelligent Cloud usage_platform/M06）；6 个未采用分部与 27 个 model_id not_selected 带理由，不宣称适配。裁定二（授予 4）：ZJ-MIN-M09 / ZJ-SMT-M09 / XM-PHONE-M03 / XM-EV-M03 判 mapped 并签署——本 reviewer 独立复算 FY2025 同口径「披露量×披露实售价」复建与残差分别为 −2,032,271、−95,486、−21,463,000、+17,635,978 元，逐位等于冻结 oracle 期望，且 |残差|/披露合计 = 0.0015456%、0.0000519%、0.0115120%、0.0166268%，分别落在先冻结的 ±0.05%、±0.05%、±0.05%、±0.10% 内；historical_mapping_probe 计数 24/9/3/3 且 low/base/high 同值；效力仅限该公司/分部/该口径/FY2025，且仅限清单所列 adaptation_scope 的主要产品线 E 口径。裁定三（不授予 2）：MS-PBP-M05 与 MS-IC-M06 维持 status=unmapped、signed=false（本判定签署，资格不授予）——FY2026 10-K 未按所需粒度披露经营量价，7 个字段全 missing、zero_filled=false ×7、zero_filled=true ×0、E 未执行（level1=null、residual=null）、probe 未运行；按 card_I-10-A.md L26 停止条款3 保留 D 段局部结果但不放行 US-MSFT-2026 正式预测。裁定四（fail-closed 收口）：不授予 accuracy（维持 unproven）、不放行任何公司（formal_company_forecast_cleared=false ×3）、不放行任何参数（low/base/high 仍 null）、不改 threshold_basis/threshold_review_status、不解除 OPEN-2/3/5/6 与任何 BLOCKED-*、不产生 I-11-B 的 ACCEPT、不改 I-10-A 封盘任何字节、不代签任何其他角色、implementer_signed=false；AD-7 special_review（仅涉未采用分部）、紫金 L2 范围桥 partially_explained（+6,782,172,956 / +5,695,369,295 元）、F-I10A-2 产品缺陷（fix-card I10A-F2-FIX）与 OPEN-11 矿业库存跨期判定式全部维持开放。
--- END C7 RULING TEXT ---

---

## ⑤ 红绿变异实测 rc

**工具**：`check_signoff.py`（判据 = 冻结 `oracle.md` §2 的 G1–G10；`oracle.md` sha `f28ddd4a…8cfd3` 先冻结）
**产物**：`disclosure_adaptation_v2.json` = `373c162197203da31d68b4273adb27d5c2ba68936bcdf4100e669c23fea9d522` / 66,887 B
**rc 约定**：0=接受 · 1=工具失败 · 2=正确拒绝负例 · 3=应红未红（vacuous，必须为 0 例）

### 5.1 逐臂实测（每个臂**单独进程**跑过一次，rc 为该进程真实退出码）

| 臂 | 内容 | 冻结期望 | **实测 rc** |
|---|---|---|---|
| **GREEN** | 完整判据审真实 `disclosure_adaptation_v2.json` | 0 | **0** ✅ |
| M1 | MS-PBP-M05 被提升为 `mapped/signed=true` | 2 | **2** ✅ |
| M2 | MS-IC-M06 被提升为 `mapped/signed=true` | 2 | **2** ✅ |
| M3 | case 改名为未采用组合 `ZJ-TRADE-M02`（贸易分部） | 2 | **2** ✅ |
| M4 | ZJ-MIN 残差被改成 −70,000,000（超冻结容差 3.4×） | 2 | **2** ✅ |
| M5 | `formal_company_forecast_cleared = true` | 2 | **2** ✅ |
| M6 | `XM-EV-M03.accuracy.status = "proven"` | 2 | **2** ✅ |
| M7 | `provenance.supersedes_sha256` 写错 | 2 | **2** ✅ |
| M8 | 删掉 ZJ-SMT 的 `reviewer_determination` | 2 | **2** ✅ |
| M9 | `implementer_never_signs = false` | 2 | **2** ✅ |
| M10 | 注入 `low/base/high = 100/200/300` | 2 | **2** ✅ |
| M11 | 改动 `company_level`（`disclosure_adaptation` 之外的漂移） | 2 | **2** ✅ |
| M12 | `modified_indices` 谎报为 `[0]` | 2 | **2** ✅ |
| **W1** | 停用 **G4**，喂「MS-PBP 提升」的坏产物 | 0 | **2** ⚠️ |
| **W2** | 停用 **G3**，喂「残差 −70,000,000 仍 signed」的坏产物 | 0 | **0** ✅ |
| **W3** | 停用 **G6**，喂「provenance sha 写错」的坏产物 | 0 | **0** ✅ |
| **W4** | 停用 **G5**，喂「accuracy=proven」的坏产物 | 0 | **2** ⚠️ |
| **W5** | 停用 **G10**，喂「封盘件 pin 被换」的坏产物 | 0 | **0** ✅ |
| **W1b**（补充） | 同时停用 **G3+G4**，喂 M1 | 0（补充臂） | **0** ✅ |
| **W4b**（补充） | 同时停用 **G2+G5**，喂 M6 | 0（补充臂） | **0** ✅ |

`judge_results.json` 实测：`GREEN rc=0` · `mutants_killed = 12/12` · `frozen_weakened_expectation_met = 3/5` ·
`supplementary = 2/2` · `safety_expectations_met = true` · `fail_open_observed = false` · `suite rc = 0`。

### 5.2 两条 ⚠️ 的诚实交代（**期望未达成，但方向是收紧不是放行**）

- **W1（期望 0，实测 2）**：停用 G4 后，同一缺陷**仍被 G3(a) 独立拦下**（「有 signed 却无 E」）。
- **W4（期望 0，实测 2）**：停用 G5 后，同一缺陷**仍被 G2 独立拦下**（`accuracy` 必须与封盘源逐值相同）。
- 二者都是**fail-closed 方向**（实际判据比冻结期望更严），**没有任何一次 fail-open**。
- 为证明这两类缺陷确实是判据在扛而不是本来就无害，我**追加**了 W1b/W4b（同时停用重叠的那一把），
  实测 **rc=0**（坏产物通过）⇒ 判据非空。**补充臂不替换、不改写冻结的 W1–W5 行**，`oracle.md` 一字未动。

### 5.3 红→绿轨迹（全部留档）

1. `check_signoff.py` **写在 `oracle.md` 冻结之后**（判据先冻结再跑）。
2. GREEN 第 1 跑：**rc=2**，5 条命中，全部落在我的 `forbids_disclosure`（禁止清单本身含「三情景预测」等字样）——
   冻结 G5 原文写的是「outside a negated/quoted context」，我的实现漏了「否定语境」这一条；
   **修实现、不修判据**：给 `forbids_disclosure` 加「每个元素必须以『不可披露』开头，否则取消豁免」的收窄约束。
3. GREEN 第 2 跑：**rc=0**。
4. suite 第 1 跑：**rc=1**（`probe["cases"]` 对 2 个 STOP case 取键 `KeyError` —— 纯工具缺陷，非判据失败）；修 `judge` 的 STOP 分支后重跑。
5. suite 第 2 跑：**rc=3**（W1/W4 未达冻结期望，见 5.2）；补 W1b/W4b 后重跑。
6. suite 第 3 跑：**rc=0**（GREEN 0 · M1–M12 全 2 · W2/W3/W5 全 0 · W1b/W4b 全 0 · W1/W4 如实记 2）。
7. 逐臂单进程复跑（上表 20 行）rc 与 suite 完全一致。

---

## ⑥ 本签署**不授予**什么（fail-closed，逐条）

1. **不授予 `accuracy`**：6 case 全部维持 `unproven`；M 卡 F 段 / I-12 冻结设计未做，本卡不授予准确性，也不得由公式或单一公司适配外推。
2. **不放行任何公司正式预测**：`formal_company_forecast_cleared = false` ×3（CN-ZIJIN / HK-XIAOMI / US-MSFT），cleared_count = 0。
3. **不放行任何参数**：`low / base / high` 全部保持 `null`（本产物中根本不引入这些键）；`threshold_basis` / `threshold_review_status` 一律不动、不新增。
4. **不解除任何 OPEN / BLOCKED**：`OPEN-2`、`OPEN-3`、`OPEN-5`、`OPEN-6` 与一切 `BLOCKED-*` 原样保留。
5. **不产生 I-11-B 的 ACCEPT**：`does_not_claim_I11B_acceptance = true`；`I11A-OPEN-MERGE` 的 `i11b_unblocked` 仍应为 `false`（其余 6 条解锁条件我一条都没碰）。
6. **不改变 I-10-A 的任何字节**：`I-10-A/a20260923-01` 12 个封盘件 sha 全部复核不变（G10 每次判据运行都实测）。
7. **不授予来源链资格**：I-07-B 实测 `zero RevenueSourceRecord`，三句逐字声明与 `overall_three_market_pass=false` 继承不变。
8. **不授予三情景/预测性结论**：探针仅 `historical_mapping_probe`；`low/base/high` 同值只证明接线。
9. **不授予未采用分部/模型的适配**：6 个 `not_selected` 分部、27 个未采用 model_id 全部不宣称适配。
10. **不晋升 `model_registry`、不修产品、不执行任何 git 写、不联网、不写 `.planning` 之外路径（含 `company-wiki`）。**
11. **不代签其他角色**：实现者、独立验证者、精算 reviewer、owner、I-10-A carrier 一律不代签。

---

## ⑦ 反例与被拒替代

1. **拒绝「直接改封盘 `disclosure_qualification.json` 把 `signed` 改 `true`」** —— `I-10-A/a20260923-01` 已 `accepted_scoped`，一个字节都不能改；改为**新文件 + `provenance.supersedes_sha256`**（`hypotheses_v2.json` 形态）。
2. **拒绝「把 2 个 MSFT STOP case 也判 `mapped`」** —— 无披露经营量价、E 未执行；判了就是造绿样。G4 专设此门（M1/M2 实测 rc2）。
3. **拒绝「用 `not_applicable_with_reason` 记这 6 项」** —— 语义错误：这两案是「**适用但不可达成**」，不是「不适用」。该 token 在本计划只用于 `actuarial_reviewer`（AD-9）与期初锚点（AD-4）。
4. **拒绝「把 carrier `reviewer_report.md` 的 4 签直接转录成机读签署」** —— 那是 **report-side** 签署，转录**不产生新判定**；C7 要的是**本 reviewer 对「实际采用」集合的独立判定**（含 2 条 STOP 的不授予判定），我必须自己复算而不是誊写。
5. **拒绝照抄「26 of 31 not_selected」** —— 实测 31 − 4 = **27**（见 §2.3）；我按实测写，并把差异记录在案，不回改封盘件。
6. **拒绝用 `aggregate_tolerance_abs = 65,724,750` 当门槛** —— 该字段有 −20,000 转写差且**不被任何 gate 使用**；我一律用相对容差 `aggregate_tolerance_rel`（先冻结）。
7. **拒绝把 L2 范围桥 gap 算进容差** —— `oracle.md(I-10-A)` L125–L126 明定其为 scope bridge、informational；必须**量化 + 标 `partially_explained`**，不得静默吸收。
8. **拒绝「OPEN-11 未裁定 ⇒ 本卡整体 blocked」** —— OPEN-11 是 `i11b_unlock_conditions` 的**另一条**（第 6 条，本轮未派），针对**矿业上一期期末库存跨期可得性**的判定式；我的签署只用**同期已披露销售数量 × 披露单价**，不依赖任何跨期库存恒等式，故不构成 C7 的阻断项（但也不解除它，见 §⑧）。
9. **拒绝「以 `partially_explained` / `unverified 9` 为由整体判 blocked」** —— 这些是 I-10-A 已明示的、**在签署范围之外**的开放项；`oracle.md(I-10-A)` L125–L126 与 L61–L67 已把它们定为「报告义务而非放行条件」，我按其口径签署并把限定写进 `forbids_disclosure`。
10. **拒绝「补零 / 由收入倒推 / 用增长率反推绝对量」** —— AD-11 明示；反例「RPO 摊回 ARPU」被拒（`qualification.json` L97 逐字记录 `zero_filled=true ×0`）。
11. **拒绝读取 `OPEN4-SOURCE-REVIEW-ACQUISITION`（错题作答）作为本卡证据** —— 全程未打开。
12. **拒绝代签独立验证者/精算 reviewer/owner/实现者** —— 只签我这一栏。

---

## ⑧ 边界

1. **C7 判定 = 已达成（`c7_status = met`），但只在 §4.1 那张表的范围内成立**：4 授予（各自限该公司/分部/口径/FY2025/manifest `adaptation_scope` 主要产品线 E 范围）+ 2 已签的不授予判定。
2. **本卡不解锁 I-11-B**：`i11b_unblocked` 仍须其余 6 条条件（≥1 条 `approved_frozen` 命题、OPEN-2、OPEN-3、OPEN-5、OPEN-6、OPEN-11）。我**只**履行第 7 条，**不写** `i11b_unblocked`、**不产生** I-11-B 的 ACCEPT。
3. **开放项照旧开放**：AD-7 special_review（机制混合分部，均未采用）· 紫金 L2 桥逐项分解 · 小米字形共享假设 · MSFT E 外部证据 · 紫金 2024 双期复建 · F-I10A-2 产品缺陷（fix-card `I10A-F2-FIX`）· F-I10A-3 等价变异体（owner 裁）· unverified 1–9 · OPEN-11。
4. **版本纪律**（`card_I-10-A.md` L20 / AD-10）：若后续改变模型、单位、会计、分部范围或收入确认逻辑，须**新建适配版本**，使依赖本口径的下游结果失效并按序重跑；**不得以本文件覆盖新口径**。本文件自身也不可被原地修改——只能再出 `v3` + 新 `provenance`。
5. **写入面**：仅 `execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/**`；`.planning` 之外零写入；`company-wiki` 产品仓零写入；git 只读（`git diff HEAD --name-only` 非 `.planning` 计数 = 0）；网络 0 次。
6. **谁复核我**：我的 `decision_sha256` 是**自算并可独立复算**的（§4.3 三步复算）；它绑定的是**封盘源 sha + 裁定正文**，作用域**只有 `disclosure_adaptation`**，不含任何阈值或 `parameter_id`。
