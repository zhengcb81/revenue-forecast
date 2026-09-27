# 复审报告 — I-11-B / a20260926-01（独立复审工位，非实现者）

- 复审对象：`execution_runs/I-11-B/a20260926-01/` 全部 12 文件（oracle.md 先冻结 · calibration_plan.json · expert_assumptions.json · synthetic_mechanism_check.json · revert_or_stop.json · handoff.json · verify_plan.py · `_mut/`×5）
- 复审工位：独立复审（与实现者 `implementer_i11b` 不同人）；本报告只写本文件 + `reviewer_report.sha256`，**不写卡状态、不落定三件套、不改被审件任何字节**
- 收尾复哈希：被审件 12 文件在复审全程前后 SHA256 逐一相同（见 §11），封盘零改动
- 全程：零 git 写、未运行 `git status`、零联网；重算脚本落 `%TEMP%\i11b_review_recompute\`（校验器本体只读、原地执行，见 §7 附注）

---

## 0. 判级

**判定：ACCEPT（附 P2×3 · P3×3；无 P1 ⇒ 不构成 `changes_required`）**

- **严格读法之争裁定：STOP_CALIBRATION 未触发**（裁定与逐字依据见 §2 —— 这是本复审的职权裁定，不再上抛 owner）
- P2 三项均为**落定前必须补登/补验**项（全部可在本 attempt 写入面内修复），不触发回滚
- `proposed_not_released` 形态 = 同 `H4 (iv)`（owner §三十六 已认可），本复审**不把它当放行**；18 槽位全部维持拟定/拒绝态，封盘零字节（§8）

`VERDICT: ACCEPT (with P2x3, P3x3; strict-reading dispute ruled NOT triggered)`

---

## 1. 回源清单（逐字回源 + 自算 sha）

| 件 | 回源 | 本工位自算/核对 |
|---|---|---|
| 授权 | `OWNER_DECISIONS.md §三十四` L745-L780：L754 owner 选择「**A**」；L757「以 MERGE 七条当前 5✅+2❌ 现状开工；i11b_unblocked 语义从『7/7 才开』改为『owner 明文许可开工』」；L758 残余「以 expert_assumption 或 unverified 形式登记」；L763-L766 硬约束；L769-L775 边界 | 逐字读毕 ✓；L750 同时记载「B2 晋升落地」（15:4x 时点）——与 C3-② 父对账措辞自洽 |
| 卡文 | `execution_v2/card_I-11-B.md`：L5 依赖 · L7-L9 前提 · L11-L16 四动作 · **L18-L20 停止**（L20＝「幅度无来源又未明确分析师假设→STOP_CALIBRATION。」）· L23 验收 | 逐字读毕 ✓；卡文仅 25 行，"L73 纪律" 落在配套 `execution_v2/common_research_cards.md` **L73 `"professional_reviewer": null`**（决策块签署纪律）+ 卡文 L23「专业reviewer签署后方可进入forecast」 |
| 上游 I-11-A | `execution_runs/I-11-A/a20260919-01/handoff.json`：L317 `"status": "accepted_scoped"` ✓；`carries` 含 3 个 `_PLACEHOLDER` 保留 id 与「magnitudes are I-11-B's deliverable」 | **卡级唯一 attempt 实测成立**（I-11-A 目录下仅 `a20260919-01`）——父勘误「不存在 a20260922-02」核实无误；派单差异已按 `unverified-D1` 登记形态收录 |
| merge_ruling §3.2 | `I11A-OPEN-MERGE/a20260924-01/merge_ruling.md` L275-L298：H4≠`approved_frozen`；「给数四要件」第②件的四类合法基础**含「明示 expert_assumption+敏感性区间」**（ACCT L226 框架）；§3.4 解锁清单 | 逐字读毕 ✓（该四类基础定义直接支撑 §2 裁定） |
| 上游 shas（自算比对，全部 MATCH） | I11A-HYP-APPROVE handoff `af4130bb`/19,481B · hypotheses_v2 `32c22208`/55,213B · OPEN2-C2 handoff `ae67e2b9`/21,226B · hypotheses_v3 `b2063ac8`/61,231B · I10A handoff `188f49e9`/21,107B · S3 `df5b368c`/24,338B · S4 `88e12c72`/65,590B · S5-ACCT `5609ac46`/11,326B · S5-IND `b7fc61c5`/17,248B · I11A-OPEN11-IND `69fcc785`/8,703B · OPEN-3-ACCT-R2 `291cb507`/17,984B · OPEN6B-R2 `758aa03f`/14,120B · OPEN6H2 `7be2122a`/15,919B · BLOCKED6C `9cca874f` · OPEN6H4 `24292c7d` | 全部 14 个前缀逐一 MATCH ✓ |

---

## 2. ⭐ 严格读法之争 — 本复审裁定：**不触发 STOP_CALIBRATION**（采实现者运行读法）

**裁定**：卡文 L20 严格读法下，本卡 **14 个 proposed 槽位与 7 条 EA 均**不触发 STOP_CALIBRATION；`revert_or_stop.json` 的 `stop_calibration_evaluation.triggered=false` **成立**，4 个 declined 槽位不构成触发。

**逐字依据（四条，独立于实现者的论证另行成立）**：

1. **L20 是合取命题**：「幅度**无来源又**未明确分析师假设→STOP_CALIBRATION」——触发主语是**一个幅度**，且须同时满足 (a) 无来源 (b) 未被明确标注为分析师假设。4 个 declined 槽位（ZIJIN_MINERAL_COPPER/GOLD_REALIZED_UNIT_REVENUE_FY2027、MSFT_MICROSOFT_CLOUD、MSFT_LICENSING_VS_CLOUD）**根本未产出任何幅度**（`new_value` 全 null，本工位逐槽验证 §4）：无"幅度"存在，条件 (a) 的主语不存在；且 EA-7 本身就是**明示的分析师立场声明**（"显式拒绝出数、不作任何幅度假设"），即便把"假想幅度"当主语，(b) 也已满足。把合取降格为"存在无来源槽位即停"，字面上删去了「又未明确分析师假设」半个条件。
2. **卡文 L13（动作①）正向指令**：「按contract arithmetic、历史经验或外部可比选择校准方法……**缺数据就标expert_assumption**」——卡文自身设计就是"缺数据→标注假设→继续校准"。若"槽位无来源"本身触发整卡 STOP，动作①的这句指令将永远不可用，属目的性废文。
3. **owner §三十四 是更高位的现行授权**：L751 选项 A 明文「以 5✅+2❌ 现状开 I-11-B，C3/C5 残余列开工后并行欠账」；L758 明文残余「以 expert_assumption 或 unverified 形式登记（不隐藏）」。严格读法会在 owner 作出决定的同一时刻使其落空（C3/C5 残余必然伴随至少 4 个无基期槽位）——`revert_or_stop.json` 自己也登记了这一后果。L775 明文「本节是 owner 的明文改判，优先级高于该自述」。
4. **merge_ruling §3.2（ACCT L226 框架）四类合法基础**：「数值有可核基础（四类之一：来源披露容差 / 同口径历史离散可复算 / 准则监管明文 / **明示 expert_assumption+敏感性区间**）」——权威框架本身把"明示假设+区间"认可为与"有来源"并列的合法基础，即 **「有来源 **或** 明示假设」的运行读法就是审定框架的读法**。本卡 14 个出数槽位全部满足"基期有来源（contract arithmetic/历史关系，回源见 §3-②）+ 幅度带明示假设（EA-1/3/4/5，`equivalent_to_disclosure_basis=false` 常量 ✓）"。

**后果核**：4 个 declined 槽位的 fail-closed 处置（不出数、不放行、`blocked_by` 保留 OPEN-2/OPEN-3）与 STOP 想要的实际效果（无来源幅度不得进入任何下游）**完全一致**；采严格读法只会把一份零放行的诚实交付改判 blocked，不增加任何保护。故不触发。

**⚠️ 复审另发现的模板性缺口（不改判、但落定前必修 → P2-2）**：oracle §5 冻结的 EA 模板含 8 字段，其自设失败条款为「缺任一字段 ⇒ 该条不成立 ⇒ 对应参数触发 STOP_CALIBRATION」。实测 **7 条 EA 逐条均缺 `carrier_form` 字段**（文件顶层有、逐条无，7/7）。该失败条款是**实现者自设的模板纪律**而非卡文 L20 本身：carrier_form 是常量串、信息零损失、卡文 L20 的两个要件（明确假设+区间）逐条满足，故不据此判 STOP；但按其自设条款的字面，该缺口一旦成立即波及全部 EA —— 必须在落定前补齐（见 P2-2）。

---

## 3. 四动作逐项复核（含本工位全部重算）

### ① 方法选择依据是否可回源 — **PASS**
- `action_1_method_selection`：contract arithmetic 优先；`external_comparable_used=false`、`network_used=false`；本地样本 6 组（分部报告行、产销量表、p56 经营计划、产品线量价行、MSFT FY2026 分部行、I10A 四 signed case）。
- 逐条回源核对：分部四行 **109,977,556,345 / 165,858,644,874 / 29,212,610,830 / 44,030,270,803** 在 store `hypotheses_v3.json` L23 `raw_value` 逐字在案 ✓；产销量 铜销 884,943/产 878,180、金销 83,161/产 82,743、锌销 352,470（L387）、银销 430,254（L406）在案 ✓；MSFT PBP 139,996(+16%)/IC 137,791(+30%)/MPC 54,052(−1%)、合计 331,839 在案（L751/L768）✓；金锭 810.17 元/克×49,074 千克、冶炼锌 20,327 元/吨×403,324 吨在 I10A `disclosure_adaptation_v2.json` L136/L288 以原文行号（CN-ZIJIN-2025.txt L3958-L3964/L4080-L4085）在案 ✓。
- 管理层目标（金 105 吨/铜 120 万吨，p56）：`management_target_is_not_independent=true` 恒真 ✓，仅作 base 对照上界与达成率带，未作准确性证据 ✓。

### ② 18 槽位逐一核 — **PASS（14 出数全部复算一致 + 4 显式拒绝全部真 null；1 项基期可复算性缺陷 → P2-1）**

**本工位重算**（Python 有理数/浮点双轨，脚本存 `%TEMP%\i11b_review_recompute\recompute.py`）：

| 槽位 | base | 带形状 | low/high 本工位重算 | 判 |
|---|---|---|---|---|
| ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027 | 109,977,556,345 | ±5% | 104,478,678,528 / 115,476,434,162 | ✓ 逐位 |
| ZIJIN_SEG_SMELT | 165,858,644,874 | ±5% | 157,565,712,630 / 174,151,577,118 | ✓ |
| ZIJIN_SEG_TRADE | 29,212,610,830 | ±5% | 27,751,980,289 / 30,673,241,372 | ✓ |
| ZIJIN_SEG_OTHER | 44,030,270,803 | ±5% | 41,828,757,263 / 46,231,784,343 | ✓ |
| ZIJIN_MINERAL_REALIZED_UNIT_REVENUE | 124,248.63（=N/885,141） | ±5% | 118,036.20 / 130,461.06 | ✓ 带复算一致；**base 本身不可复算 → P2-1** |
| COPPER/GOLD_REALIZED_UNIT_REVENUE | — | EA-7 | **显式拒绝出数，全 null** | ✓ |
| COPPER_SALEABLE_VOLUME | 884,943 | ±10% | 796,448.7 / 973,437.3 | ✓ |
| GOLD_SALEABLE_VOLUME | 83,161 | ±10% | 74,844.9 / 91,477.1 | ✓ |
| ZINC_SALEABLE_VOLUME | 352,470 | ±10% | 317,223 / 387,717 | ✓ |
| SILVER_SALEABLE_VOLUME | 430,254 | ±10% | 387,228.6 / 473,279.4 | ✓ |
| ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER | 金 105,000 kg / 铜 1,200,000 t | 达成率 [0.9,1.1] | 94,500/115,500 kg；1,080,000/1,320,000 t | ✓（`_PLACEHOLDER` 维持，§三十四 L763 边界遵守）|
| ZIJIN_SEGMENT_RECONCILIATION_FY2027 | 恒等式桥 | 偏差=0，τ=1 元 | 0/0/0（容差形态） | ✓ |
| MSFT_PBP/IC/MPC g | 0.16/0.30/−0.01 | g±=(1+g)×0.95/1.05−1 | 0.102/0.218；0.235/0.365；−0.0595/0.0395 | ✓ 复合公式逐位 |
| MSFT_MICROSOFT_CLOUD_…_PLACEHOLDER | — | EA-7 | **显式拒绝出数，全 null** | ✓ |
| MSFT_LICENSING_VS_CLOUD_COMPOSITION | — | EA-7 | **显式拒绝出数，全 null** | ✓ |

- **合计 18 = 14 proposed + 4 declined**，与 `revert_or_stop.per_slot_summary`（14/4/0）一致 ✓；`silent_unsourced_amplitudes=0` 在上述逐槽核验下成立。
- **`proposed_not_released` 真实性（双侧重证）**：store 侧 `hypotheses_v3.json` 全树 walk `low/base/high` **全部 null**（校验器 I4 绿灯 ×4 个 store 变体，含 v4 与封盘原件）；4 条新 id 在 `model_cards_append.md` L51-L54 逐条 **`null/null/null` + `released=false` + `state=pending_professional_decision`** ✓；plan 侧 14 槽位全部 `proposed_not_released`、4 槽位 `declined_to_calibrate` 且 new_value 全 null（校验器 I2 覆盖 18/18，键名 census `action2_parameter_mapping`×18 无变体）✓。
- **4 个显式拒绝出数的合理性**：逐条核对拒绝理由与上游一致——铜/金分金属实现价：本工位可读面内无铜产品线量价行、金锭行属冶炼口径（不可充当矿产金），且 OPEN-2 明令该值放行=BLOCKED、store original_value=null ✓；MSFT Cloud：store 逐字「无可用换算公式」✓；licensing 拆分：拆分表未披露 ✓。拒绝=非静默（EA-7 承接、带设计预登记），符合"残余不隐藏"红线。

**P2-1（本工位重算发现，卡内未登记）**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的 base=124,248.63（=109,977,556,345÷885,141，实现除式本身自洽），但 **store `hypotheses_v3.json` L175 转换公式自写除式为「884,943 + 83,161×24」= 2,880,807 ≠ 885,141**——按自写除式真值 = **38,175.95**（差 3.25 倍）；两点差分框架（885,141→968,302，−10,670.89）只在 /885,141 基下自洽，若按自洽除式则每 +1 系数仅 ≈−1,071 元。该矛盾**是封盘 store 的先天缺陷**（本卡正确地未回改封盘），但本卡以「contract arithmetic（基期推导）」承接该 base 并逐字沿用矛盾除式，**未把"base 不可复算"登记为 unverified 项**（仅登记了系数来源缺口）。落定前必须补登 + 禁止任何下游在 OPEN-2 裁定前消费 124,248.63（详见 §9 P2-1）。

### ③ dependency_control 无双通道重复计权 — **PASS（7 共享驱动 + 7 事件逐条在案；抽 2 条自验）**
- 抽验 **E1（FY2025 库存释放）**：铜 +6,763 = 884,943−878,180 ✓、金 +418 = 83,161−82,743 ✓（本工位重算）；处置 = 只允许出现在销量通道（ALLOWED_ONCE），base 已剔除常态外推（EA-3），价格侧不得再解释同一增量——与 store L363「均由库存下降/在途释放实现，不得外推为常态」逐字一致 ✓。
- 抽验 **E4（XM-EV other_revenue 2,800,000,000）**：I10A XM-EV-M03 case 中 `other_revenue` 为显式单列字段（L588「含 other_revenue=2,800,000,000 元 显式映射」），本工位重算 411,082×251,171+2.8e9=106,051,877,022 逐位成立、且 I10A 侧记录「mut_omit_optional rc=2 击杀」（去掉该字段即判负）——**结构上不存在经单价二次进入的通道** ✓。
- E2（当量折算只进量侧一次）/E3（计划值只作对照，`management_target_is_not_independent=true`）/E5（抵销 234,970,146,412 只进恒等式桥；store L677/L681 互斥禁令逐字在案）/E6（MSFT Cloud 不与 IC 并用 = PROHIBITED_CO_USE）/E7（三分部增速与集团增速互斥）：逐条与 store/I10A 原文对得上 ✓。
- 联合情景联动（correlated_scenarios 3 组 + `scenario_joint_logic`）：STOP_SCENARIO 判据（量 high×价 high×其他收入 high 独立叠加 ≈+21% 不可能联合）与卡文 L21 一致；`stop_scenario_triggered=false` 成立（EA-6 联动档为结构约束）✓。

### ④ 手算复核 — **PASS（本工位全部独立重算，5+4+3 全对；1 处线级誊算差错 → P3-4）**
- **合成示例 5 步（H-SYNTH-RENEWABLE-01，对照 `research_cards.md` L81-L116 原文）**：①电量 2×8760×0.5=**8,760 MWh** ✓ ②混合价 s=0.5/0.6/0.7 → **30/32/34 元/MWh** ✓ ③收入 8760×{30,32,34}+1200 = **264,000/281,520/299,040** ✓ ④base−原值 = **+17,520** ✓ ⑤单驱动（仅 s 变动，无第四通道）结构成立 ✓；量纲 MW×h×元/MWh=元 ✓。示例数字隔离：15 个示例数与本卡真实字段零交（`1,200,000`（铜计划）与示例 `1200` 来源/量级不同，已登记为非复制）✓。
- **真实映射 4 条（对 I10A `disclosure_adaptation_v2.json` signed 值逐位）**：
  - ZJ-MIN-M09：131,491,532,271 vs 131,489,500,000 → 残差 ±2,032,271 = **0.0015456%** ≤ ±0.05% ✓
  - ZJ-SMT-M09：183,988,605,486 vs 183,988,510,000 → **0.0000519%** ≤ ±0.05% ✓；线级 403,324×20,327 = 8,198,366,948 逐位 ✓
  - XM-PHONE-M03：165,200,000×1,128.7 = **186,461,240,000** 逐位 ✓；残差 −21,463,000 = 0.0115120% ≤ ±0.05% ✓
  - XM-EV-M03：411,082×251,171 = **103,251,877,022** 逐位 ✓；+2.8e9 = 106,051,877,022 ✓；残差 +17,635,978 = 0.0166268% ≤ ±0.10% ✓；other_revenue 仅出现一次 ✓
  - P3-4（誊算差错）：卡内金锭线 spot-check 写作「49,074 千克×810.17 元/克 = 39,757,982,580 元」——**本工位重算真值 = 39,758,282,580（差 +300,000）**；对披露 3,975,798 万元的真实线残差 = +302,580（0.0007611%），**结论（线级容差内）不变**，但等式如印是错的。
- **3 恒等式**：H-05：584,049,229,264−234,970,146,412 = **349,079,082,852** ✓；H-01 四分部对外合计 = **349,079,082,852**（=合并营业收入）✓；MSFT 139,996+137,791+54,052 = **331,839** ✓。另验：四分部总计之和 138,271,672,956+189,683,879,295+170,521,025,777+85,572,651,236 = 584,049,229,264 ✓（store L641 raw_value 全数在案）。

---

## 4. 18 槽位核验汇总

- 总数 18 = 14 proposed + 4 declined（§3-② 表逐槽列明，本工位逐个重算）✓
- `value_state` 键名 18/18 统一、`new_value` 结构统一；declined 4 槽 `low/base/high` 全 null（校验器 I2 覆盖 18/18）✓
- store 侧（hypotheses_v3/v4/封盘原件）`low/base/high` 全 null、`_PLACEHOLDER` 双 id 在位、`released` 键仅 4 处且全 false（校验器 I4 绿灯）✓
- model_cards 侧 4 新 id 全 `null/null/null` + `released=false`（L51-L54）✓
- **proposed_not_released 形态 = H4 (iv) 同形，不构成放行**；卡内 `params_released=false`、`implementer_signed=false`、`releases_nothing=true` 与实测一致 ✓

## 5. 7 条 EA 核验

| EA | 假设内容 | 敏感性区间 | eqt=false | 模板 8 字段 |
|---|---|---|---|---|
| EA-1 | 带形状锚定 H4 [0.9,1.1] / H2 ±5% | 有（量×0.9/1.1、价±5%、增长复合式） | ✓ | 缺 carrier_form |
| EA-2 | 金→铜当量系数 24（示意值） | 有（−10,670.89 两点差分；k=23/25 点） | ✓ | 缺 carrier_form |
| EA-3 | 朴素基线（FY2025 不变；库存释放不外推） | 有 | ✓ | 缺 carrier_form |
| EA-4 | MSFT FY2026 增速持续 | 有（g 复合带，本工位逐位复算 ✓） | ✓ | 缺 carrier_form |
| EA-5 | 矿产分部 base=109,977,556,345（差额+引数双路同值） | 有（±5%；N1 张力=3.17×，实测 3.1741 ✓） | ✓ | 缺 carrier_form |
| EA-6 | 联合情景同档联动（结构约束） | 有（联动带 ≈−14.5%/+15.5%） | ✓ | 缺 carrier_form |
| EA-7 | **显式拒绝出数**（4 槽位） | 有（n/a 形态+带设计预登记） | ✓ | 缺 carrier_form |

- **敏感区间 + eqt=false：7/7 齐备**（校验器 I1 绿灯 + M1/M2 红灯双证）✓
- **漏标检查**：14 个出数槽位全部显式引用 EA（ea_refs 18/18 在键）；无"无标注幅度" ✓
- **模板缺口（P2-2）**：oracle §5 模板 8 字段中 `carrier_form` **7/7 逐条缺失**（文件顶层有）；按 oracle 自设失败条款的字面，7 条 EA 均不成立——信息零损失（常量串）但违反其自设模板纪律，落定前补齐（7 行常量）并把校验器 I1 从 2 字段扩到 8 字段 + 加 M6 变异（删 carrier_form 必须红）。
- 数值小注（P3-5）：EA-4 band_rationale 的「三情景三分部收入合计区间 = [320,763, 348,432] USD mn」**不可复现**：按其自身 g 带作用于 FY2026 应为 **[375,283, 414,787]**；声称高点 ≈ FY2026 合计×1.05（348,431），低点无出处。运行值（g_low/g_high）本身全部正确，此为注解内数字错误。EA-2 k=23 点标注"两点差分方向"（134,919.5）系线性外推、精确值 137,132.54——已自declared为近似，可接受（备注级）。

## 6. C3/C5 残余 9 项核验（含父两条对账措辞）

| # | 项 | 登记态 | 本工位复核 |
|---|---|---|---|
| C3-① | origin 字节 | unverified | 登记成立：62,953B ✅ ≠ E1 解锁（BLOCKED-PARTIAL）✓ 未写"已解" |
| C3-② | B2 晋升 | **verified_by_parent**（父对账措辞在案） | B2-PROMOTION handoff 实读 `status=blocked`（13:01:52 事故时点）✓；§三十四 L750「B2 晋升落地」（15:4x）与之自洽；产品仓不在本工位读面，维持父证形态正确 |
| C3-③ | ACCT-R2 | unverified | OPEN-3-ACCT-R2 handoff sha `291cb507` ✓；RULED≠通过、E1=BLOCKED-PARTIAL/S1/E3 降级= fail-closed 结果 ✓ |
| C3-④ | IND-r2 | unverified（**详情过时 → P2-3**） | **IND-r2 已在本卡运行窗内落地**（`OPEN-3-IND-R2/a20260926-01`：ruling_ind_r2.md 17:34:28、ind_ruling_r2.json 17:36:20、handoff 17:38:08 `status=RULED`；segment_set_ok=yes_content_layer_with_bridge_caveat、S1 countersigned、E1 维持 BLOCKED-PARTIAL、releases_nothing=true）。本卡 handoff 写于 17:44:22，其"在跑未归（目录空）"在交付时点已是旧值。**登记形态（unverified）仍正确**，事实描述须更新；IND-r2 未放行任何东西，I-11-B 的 blocked_by 不因此变化 |
| C3-⑤ | MSFT 六参数/新两分部参数 | unverified | merge_ruling §3.3 逐字在案：E1 五要素缺 4、`MSFT_*` 一律不放行 ✓；本卡两 MSFT 槽位显式拒绝出数与之严格一致 |
| C5-① | 6c | unverified | BLOCKED6C handoff sha `9cca874f` ✓；accepted_scoped 带 2×P2+3×P3，非 clean accept ✓ |
| C5-② | H4 口径桥 | unverified | OPEN6H4 handoff sha `24292c7d` ✓；残差 269t/534kg、countersigned=false、Q2 fail-closed ✓ |
| C5-③ | 6b 容差 | unverified | OPEN6B-R2 handoff sha `758aa03f` ✓；路径(c)退 unquantified、R2 NOT_SIGNED、整条归 ruling_6b L110 另判 ✓ |
| C5-④ | H2 | unverified | OPEN6H2 handoff sha `7be2122a` ✓；交付仍 still_blocked、A-6.3 全套 0/3 ✓ |

- **红线核**：9 项无一写成"已解"（校验器 I5 绿灯 + M5 红灯[登记→resolved 即 rc=1]双证）；expert_assumption 只承接校准幅度判断、未冲销任何 BLOCKED ✓
- 派单差异两条：`unverified-D1`（a20260922-02 不存在——本工位实测 I-11-A 卡级仅 1 个 attempt，勘误成立）与 `unverified-C3b`（父对账措辞）均在 handoff `dispatch_discrepancies_registered` 在案 ✓

## 7. 红绿变异重跑（本工位独立执行）

校验器：`verify_plan.py`（只读，无任何写路径；`utf-8-sig` 载入）。执行方式：因沙箱拒绝 Copy-Item 至 %TEMP%，校验器在原路径**只读**运行（源码审读确认零写入），重算/变异分析脚本落 `%TEMP%\i11b_review_recompute\`。

| 运行 | 结果 |
|---|---|
| GREEN 默认（plan+eas+handoff+store v3） | **rc=0 ALL_INVARIANTS_OK** |
| GREEN 显式 v3 / **v4** / **封盘原件**（三个 store 变体各跑一遍） | **rc=0 ×3** |
| RED M1（删 EA-1 sensitivity_interval） | **rc=1** `I1 violated: EA-1 missing sensitivity_interval` |
| RED M2（EA-2 eqt→true） | **rc=1** `I1 violated: EA-2 equivalent_to_disclosure_basis != false` |
| RED M3（handoff.params_released→true） | **rc=1** `I5 violated: handoff.params_released != false` |
| RED M4（store low: null→0 ×12 叶位） | **rc=1** `I4 violated: store low != null (got 0) — release detected`（逐处具名） |
| RED M5（残余登记→resolved ×8） | **rc=1** `I5 violated: residual … registration='resolved' (must stay open-form)` |

- 变异真实性（逐文件 deep-diff）：M1 仅 EA-1 缺字段 ✓；M2 仅 EA-2 eqt 翻转 ✓；M4 恰 12 处 `low: None→0`、余字节全同 ✓；M3/M5 主体变异正确，但**变异副本基于定稿前的 handoff 旧快照**（mutation_rc=None、缺 git_diff_non_planning_measured、written_files 旧版）——不纯单字段差分，P3-6 记录（被测不变量不受影响）。
- **判别力结论**：5 红全 rc=1 且违例具名、绿 rc=0；变异确能区分好坏实现。覆盖缺口：oracle §5 模板 8 字段中 I1 只测 2 字段（carrier_form 缺失不红）→ P2-2 要求补 M6。
- 与卡内记录比对：`mutation_rc`（绿 0、五红 1、具名）与本工位重跑**完全一致** ✓；首轮 BOM 事故及 `utf-8-sig` 改造已在卡内如实登记 ✓。

## 8. 封盘零字节确认

- **I-11-A 封盘 hypotheses.json 自算 sha256 = `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（51,697 B）**——与派单期望 `f2178768…` 一致 ✓；mtime 2026-09-20 15:48（早于本卡窗口 17:14-17:44）✓
- 全树 `hypotheses*` 12 文件逐一 hash/时间戳核对：封盘原件与 OPEN6B preimage **逐字节相同**（同 sha）；v2/v3/v4/h4/r2 均为**独立新版本载体**（supersedes+modified_indices 结构在案），封盘原件零改动 ✓
- **本卡窗口（09-26 17:14-17:44）内零 hypotheses* 写入**：最新为 hypotheses_r2_v1.json 16:05:13 < 17:14 ✓
- model_cards 侧零值放行（§4）✓；本工位收尾复哈希被审件 12 文件与开工基线逐一相同（§11）✓

## 9. 判级与 P 清单

**ACCEPT**（无 P1；严格读法裁定不触发，故不转 changes_required）

**P2（落定前必须处置，均可在本 attempt 写入面内完成）**
- **P2-1** `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 基期可复算性缺陷：store L175 转换公式自相矛盾（`884,943+83,161×24=2,880,807` ≠ `885,141`；真值 38,175.95 vs 沿用值 124,248.63，差 3.25×；自洽基下两点差分应为 ≈−1,071 而非 −10,670.89）。处置：在卡内补登 unverified 项（store 先天缺陷+本卡沿用未标）；**OPEN-2 裁定前任何下游不得消费 124,248.63 及其 ±5% 带**；建议同时提示编排层在 OPEN-2 裁定时先修 store 口径桥。
- **P2-2** EA 模板 8 字段缺口：7/7 条缺逐条 `carrier_form`（oracle §5 自设失败条款字面即触发"不成立"）。处置：7 行常量补齐 + 校验器 I1 扩至 8 字段 + 新增 M6 变异（删 carrier_form 必红）重跑红绿。
- **P2-3** C3-④ 事实过时：「IND-r2 在跑（目录空）」在 handoff 交付时点（17:44:22）已不成立（IND-r2 17:34-17:38 已 RULED：segment_set_ok=yes content-layer+bridge caveat、S1 会签、E1 仍 BLOCKED-PARTIAL、零放行）。处置：更新登记详情（登记形态 unverified 不变）；确认 IND-r2 不改变本卡任一 blocked_by（本工位已核：不改变）。

**P3（记录在案，不阻断）**
- **P3-4** 金锭线 spot-check 誊算：39,757,982,580 应为 39,758,282,580（差 300,000）；真实线残差 +302,580（0.0007611%），结论不变。
- **P3-5** EA-4 注解内联合收入带 [320,763, 348,432] 不可复现（应为 [375,283, 414,787]；g 运行值本身全对）。
- **P3-6** M3/M5 变异副本基于旧 handoff 快照（mutation_rc=None 等），非纯单字段差分；建议以定稿字节重生成。

## 10. unverified 清单（本卡交付面现存开放项，移交落定/后继）

卡内 9 项残余（C3-①…⑤、C5-①…④，全 open-form，§6）+ 派单差异 2 项（unverified-D1、unverified-C3b）+ 本复审新增 3 项（**unverified-N2**：H-02 转换公式自相矛盾/基期不可复算[P2-1]；**unverified-N3**：EA 模板 carrier_form 缺失[P2-2]；**unverified-N4**：C3-④ IND-r2 已 RULED 的登记更新[P2-3]）+ 数值小注 2 项（P3-4/P3-5）。

## 11. 审计轨迹与收尾复哈希

- 开工基线与收尾复哈希：被审件 12 文件（7 主件 + 5 变异副本）SHA256 前后**逐一相同，零改动**（基线记录于本工位开工第一条命令输出）。
- 本工位写入面：仅 `execution_runs/I-11-B/a20260926-01/reviewer_report.md` + `reviewer_report.sha256`；`%TEMP%\i11b_review_recompute\{recompute.py, mutant_diff.py}`。
- 未跑任何 git 命令（含 `git status`）；零联网；被审件与封盘全程只读。
- 诚实更正：复审途中曾疑 handoff `written_files` 路径与 C1 sha 誊写有误（目测 CJK 宽字符所致），经程序化核对**均为误警**（8/8 路径含正确 attempt id；C1 sha 与 hypotheses_v4 实际 decision_sha256 逐字符 MATCH）；band_conventions 内 3 处 `ea_ref`（无 s）为纯拼写变体、无消费者，并入 P3 级备忘。

## 12. 本复审没有做的事

- **未写任何卡状态**：不改 card、不改 handoff/calibration_plan 等被审件字节；未产出落定三件套（review.md/qualification.json/handoff.json 落定由落定工位做）。
- **未回源原始 PDF 字节**：CN-ZIJIN-AR2025 p327/p328、产销量表、p56 及 MSFT 10-K 原文行未直接重读——对分部四行/产销量/MSFT 值采信封盘 store 的 raw_value 逐字在案 + I10A 的原文行号记录双重转引；如需字节级回源须另行派单。
- **未重审上游 attempt 本体**：I-11-A/I-10-A/OPEN-2/3/5/6/BLOCKED-* 各 handoff 仅核对被引字段与 sha（14/14 MATCH），不重开其验收。
- **未裁 B2 晋升本体**：产品仓不在本工位读面，维持 `verified_by_parent` 形态。
- **未评估拟定值的预测质量/准确性**：本卡验收 L23 明示"不等同准确性通过"；本复审只核可回源性/一致性/红线。
- **未在 %TEMP% 复现校验器副本运行**（沙箱拒绝 Copy-Item；改为原路径只读执行，无任何写入）—— deviation 已在 §7 披露。
- **未派 I-11-C、未触任何 falsifier/自动动作、未解除任何 OPEN/BLOCKED、未放行任何参数。`

---

*复审工位签记：独立复审（非实现者）；本报告不含自签验收效力，落定仍走三件套；owner §三十六：proposed_not_released = H4 (iv) 同形，不是放行。*
