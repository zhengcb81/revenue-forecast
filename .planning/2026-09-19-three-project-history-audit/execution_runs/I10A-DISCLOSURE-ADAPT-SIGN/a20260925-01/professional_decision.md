# `professional_decision.md` — I10A-DISCLOSURE-ADAPT-SIGN · a20260925-01

> 文件名由 `execution_v2/card_I-11-B.md` **L25 证据栏**点名
> （`evidence/I-11-B/…、professional_decision.md`）。本文件放在**本卡自己的产出目录**，
> **不写入** I-11-B 尚未开工的证据面，**不生成** `parameter_changes.json` / `calibration_samples.json` /
> `joint_scenarios.json` / `hand_oracle.json`（那四件仍为「未产生」）。
> 本文件记录的是 **C7：披露适配口径的选择依据与样本**。

**角色**：行业/会计专业 reviewer（**非实现者**）· `implementer_signed = false`
**日期**：2026-09-25（UTC）
**`decision_sha256`**：`86d0a80e3de76325ba4ac12376c7beb40770e063f2b77e8af6ee104e47c6f22b`
（求值方式 = `ruling.md` §4.3；preimage 3,218 字节；写入前 / 写入后 / `ruling.md` 成文后各复算一次，三值相同）
**产物**：`disclosure_adaptation_v2.json` = `373c162197203da31d68b4273adb27d5c2ba68936bcdf4100e669c23fea9d522` / 66,887 B
**被取代源**：`I-10-A/a20260923-01/evidence/I-10-A/disclosure_qualification.json` =
`6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb` / 8,603 B（**0 字节改动**）

---

## 1. 我为什么这样选（选择依据）

### 1.1 判定对象来自回源，不来自转述

「实际采用」**唯一**取自封盘的 `selected_model_manifest.json`（`96b0f56e…71ef49` / 22,358 B），
由我自行解析 `companies[].segments[].status=="adopted" → adopted_models[]` 得到 **6 case**，
与 `disclosure_qualification.json` 的 6 个 case key **逐项相等**（顺序也相等）。
未采用的 6 个分部与 27 个未采用 model_id 明确**不宣称适配**。

### 1.2 每一项的判定门槛（三段式，M 卡 D/E 口径）

按 `card_M09.md L60` / `card_M03.md L63` / `card_M05.md L63` / `card_M06.md L60` 的同一句资格定义
「**逐字段证据** + **一个已结束期间的收入对账** + **生产 forecast 入口映射** 经**独立审阅**；仅限该公司/阶段/口径」：

| 门槛 | 我怎么验 | 不满足则 |
|---|---|---|
| A. 逐字段证据（D） | `disclosure_mapping.json` 每 case `per_instance_fields` 齐全、`missing_fields` 明示（4 个 GREEN case 为空、2 个 STOP case 逐字段列 missing 且 `zero_filled=false`） | 判 `unmapped` |
| B. 已结束期间收入对账（E） | 我用**披露量×披露单价**独立重算，残差绝对值/披露合计 ≤ **先冻结**的 `aggregate_tolerance_rel` | 判 `unmapped`（STOP_DISCLOSURE_ADAPTATION） |
| C. 生产 forecast 入口映射 | `historical_mapping_probe`：`counts_ok=true`、`low_base_high_identical=true`、输出=冻结手算值 | 判 `unmapped` |
| D. 独立审阅 | 本 reviewer 自己复算 + 原文行核；**不是**誊写 carrier 报告 | 不签 |

**结果**：4 项 A/B/C/D 全中 → `mapped` + `signed=true`；2 项 B 失败（FY2026 10-K 无经营量价）
→ **维持 `unmapped` / `signed=false`，同时签署「不授予」判定**。

### 1.3 为什么不用别的取值

- `not_applicable_with_reason` —— 只用于**确实不适用**的项（本计划里是 `actuarial_reviewer`（AD-9）
  与期初锚点（AD-4））。MSFT 两案是「**适用但不可达成**」，用它会掩盖 STOP 事实。
- `not_granted` —— 是 I-11-A hypotheses 自己的三栏用语，不是本计划机读面的 `disclosure_adaptation` 状态值。
- `accepted_scoped` —— 是**卡级 verdict** 词，不是资格状态；我不把卡级裁决词塞进资格状态字段。
- 保持 `unmapped`（MSFT 两案）—— **fail-closed**：没有 E 就没有映射，`signed` 不置 `true`。

---

## 2. 样本（我实际抽出来核对的证据样本）

### 2.1 样本 A · 残差重算样本（4/4，全部由我重算）

| case | 披露量 | 披露单价 | 我算的复建 | 披露收入 | 残差 | 冻结相对容差 | 判定 |
|---|---|---|---|---|---|---|---|
| ZJ-MIN-M09（8 线合计） | 见下 2.2 | 见下 2.2 | 131,491,532,271 | 131,489,500,000 | **−2,032,271** | ±0.05% | 0.0015456% ✅ |
| ZJ-SMT-M09（3 线合计） | 162,950,000 g / 697,678 t / 403,324 t | 772.15 / 71,621 / 20,327 | 183,988,605,486 | 183,988,510,000 | **−95,486** | ±0.05% | 0.0000519% ✅ |
| XM-PHONE-M03 | 165,200,000 部 | 1,128.7 元/部 | 186,461,240,000 | 186,439,777,000 | **−21,463,000** | ±0.05% | 0.0115120% ✅ |
| XM-EV-M03 | 411,082 輛 | 251,171 元/輛 + 2,800,000,000 | 106,051,877,022 | 106,069,513,000 | **+17,635,978** | ±0.10% | 0.0166268% ✅ |

### 2.2 样本 B · 原文行核样本（我 grep 的抽取件行号）

| 抽取件 | 行 | 原文 |
|---|---|---|
| `CN-ZIJIN-2025.txt` | L3958–L3964 | 矿山产金·金锭：`810.17` 元/克 · `49,074` 千克 · `3,975,798` 万元 |
| `CN-ZIJIN-2025.txt` | L3971–L3974 | 金精矿：`730.98` 元/克 · `34,087` 千克 |
| `CN-ZIJIN-2025.txt` | L4080–L4085 | 冶炼产锌：`20,327` 元/吨 · `403,324` 吨 · `819,823`（万元） |
| `CN-ZIJIN-2025.txt` | L26011 / L35012–L35013 | 矿产品分部对外 `109,977,556,345`；分部总计 `138,271,672,956`、`189,683,879,295` |
| `HK-XIAOMI-2025_decoded.txt` | L1404 | `165.2 百萬部` |
| `HK-XIAOMI-2025_decoded.txt` | L1436 | `每部人民幣 1,128.7 元` |
| `HK-XIAOMI-2025_decoded.txt` | L1582 | `411,082 輛` |
| `HK-XIAOMI-2025_decoded.txt` | L1610 | `每輛人民幣 251,171 元` |
| `HK-XIAOMI-2025_decoded.txt` | L17788–L17790 | 附註5 分部收入行 `186,439,777…351,217,174…106,069,513…457,286,687` |

（MSFT 两案为**否定样本**：`disclosure_mapping.json` L1425–L1447 / L1535–L1551 逐字段 `missing`、
`zero_filled=false`；`historical_reconciliation.json` L348–L351 / L358–L361 `level1=null`、`residual=null`。）

### 2.3 样本 C · 探针样本（接线，非三情景）

`historical_mapping_probe.json`：ZJ-MIN `counts=24`（L12/L25）· ZJ-SMT `9`（L121/L134）·
XM-PHONE `3`（L185/L198）· XM-EV `3`（L231/L244，`mut_omit_optional` rc2 击杀）·
MS-PBP/MS-IC `not_run`（`not_run` 段，理由「required parameters missing… running a probe with invented values is forbidden」）。

### 2.4 样本 D · 构成闭环样本（我复算）

小米附註5：186,439,777 + 123,200,191 + 37,440,346 + 4,136,860 = **351,217,174**（小計）；
351,217,174 + 106,069,513 = **457,286,687** 千元（總計）—— 与披露行逐位相等。
紫金 L2 桥：138,271,672,956 − 131,489,500,000 = **+6,782,172,956**；
189,683,879,295 − 183,988,510,000 = **+5,695,369,295**（`partially_explained`，不进容差门）。

---

## 3. 口径清单（机器面，与 `disclosure_adaptation_v2.json` 一一对应）

| case | 公司 / 分部 / 模型 | 期间 | `status` | `signed` | 判定 |
|---|---|---|---|---|---|
| ZJ-MIN-M09 | 紫金 / 矿产品分部 / `resource`(M09) | FY2025 | `mapped` | `true` | granted_scoped |
| ZJ-SMT-M09 | 紫金 / 冶炼产品分部 / `resource`(M09) | FY2025 | `mapped` | `true` | granted_scoped |
| XM-PHONE-M03 | 小米 / 智能手機 / `unit_sales`(M03) | FY2025 | `mapped` | `true` | granted_scoped |
| XM-EV-M03 | 小米 / 智能電動汽車及AI等創新業務分部 / `unit_sales`(M03) | FY2025 | `mapped` | `true` | granted_scoped |
| MS-PBP-M05 | 微软 / PBP / `subscription`(M05) | FY2026 | `unmapped` | `false` | not_granted（STOP，判定已签） |
| MS-IC-M06 | 微软 / IC / `usage_platform`(M06) | FY2026 | `unmapped` | `false` | not_granted（STOP，判定已签） |

`disclosure_adaptation_signed_count = 4` · `not_granted = 2` · `determination_signed = 6` · `cleared = false`。

---

## 4. 判据非空的证明（摘要，完整表在 `ruling.md` §⑤）

- **GREEN**：完整判据审真实产物 **rc=0**。
- **红/变异**：M1–M12 共 12 个不该被接受的口径，**全部 rc=2 被拒**（含「STOP 提升为 mapped」×2、
  「残差超容差」、「accuracy 偷渡」、「provenance 说谎」、「参数放行」、「封盘件被改」）。
- **判据改弱后必须放行**：停用 G3 / G6 / G10 后分别喂坏产物 → **rc=0（放行）**，
  另加 W1b（G3+G4 同时停用）/ W4b（G2+G5 同时停用）→ **rc=0（放行）**。
- 冻结表里 **W1、W4 期望 0 实测 2**：同缺陷被**第二把**独立判据（G3(a)/G2）拦下，
  属**收紧方向**，已如实记录，未改 `oracle.md`，也未据此放宽任何判据。**fail-open 观测 = 0。**

---

## 5. 本文件不授予什么

不授予 `accuracy`（维持 `unproven`）· 不放行任何公司（`formal_company_forecast_cleared=false` ×3）·
不放行任何参数（`low/base/high` 仍 `null`、`threshold_basis`/`threshold_review_status` 不动）·
不解除 `OPEN-2/3/5/6` 与任何 `BLOCKED-*` · 不产生 I-11-B 的 ACCEPT（`i11b_unblocked` 仍须其余条件）·
不改 I-10-A 任何字节 · 不代签实现者/独立验证者/精算 reviewer/owner · 不生成 I-11-B 的四件证据文件。
