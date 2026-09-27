# 复审报告 — I-11-C / a20260926-01（独立复审工位，非实现者）

- 复审对象：`execution_runs/I-11-C/a20260926-01/` **9 主件**（`oracle.md` · `parameter_mapping.json` · `mapping_verification.json` · `verify_mapping.py` · `handoff.json` · `_build_mapping.py` · `_recompute_action1.py` · `_check_hashes.py` · `_run_mutations.py`）+ `_mut/` **5 变异副本** = 14 文件
- 复审工位：**独立复审**（未参与参数设定；与 `I-11-B` 实现者、`I-11-C` 实现者均不同人）
- 写入面：**仅本目录新建 `reviewer_report.md` + `reviewer_report.sha256` 两件**；**不写任何卡状态**、不落定三件套（`review.md`/`qualification.json`/`handoff.json` 落定归落定环节）
- 全程纪律：被审件 / `I-11-B` / 封盘 **只读**（开工与收尾双次哈希比对，§7）；**禁 git 写、未运行 `git status`**（仅 `git -c core.quotepath=false diff HEAD --name-only` 只读计数）；**零联网**；自建重算与变异脚本落 **`%TEMP%\i11c_rev\`**（沙箱实测可写，未使用原路径写入）
- 时间窗：本复审执行于 2026-09-26 约 19:00–19:2x；被审件交付窗 18:00:38–18:22:18

---

## 0. 判级

**判定：ACCEPT（附 P2×3 · P3×3；**无 P1** ⇒ 不构成 `changes_required`）**

- **五项复核全部实跑**：映射可执行性（13 条带数值行 + 5 条零传播行**全部由本工位独立复算**，0 失败）、EA 依从性（17/18 挂 EA，**7/7 条 EA 均有敏感性区间且 `equivalent_to_disclosure_basis=false`**）、参数不放行（store 侧实证全 null）、STOP 核验（绿 rc=0 + 我方 10 红 rc=1 具名）、封盘零字节（`f2178768…` 自算命中）
- **上游 `P2-1`（OPEN-2 前禁消费 `124,248.63`）：未消费**（专项证据见 §4）⇒ 本卡不因该条转 `unverified`/`changes_required`
- **17/18 EA 承接本身不是缺陷**（数据可得性事实）；本复审未发现"挂 EA 却没区间 / 没标 `equivalent=false`"，也未发现"借 EA 之名出无依据数"
- `proposed_not_released` / `mapped_not_released` 形态与 `H4 (iv)` 同形（owner §三十六 认可），**本复审不把它当放行**
- P2 三项均**可在 I-11-C 本 attempt 写入面内修复**（或补登继承项），不改任何数值、不改任何 verdict ⇒ 不升级为 P1

VERDICT: ACCEPT (with P2x3, P3x3; no P1; upstream P2-1 base NOT consumed; strict-reading ruling follows I-11-B review)

---

## 1. 回源清单（逐字回源 + 自算 sha）

| 件 | 回源实测 | 本工位核对 |
|---|---|---|
| 授权 `OWNER_DECISIONS §三十四`（L745-L780） | L754 owner 选「**A**」；L757 开工门槛改判 `5✅+2❌`；L758 残余「以 `expert_assumption` 或 `unverified` 登记」；L761-L766 硬约束（oracle 先冻结／**不放行任何参数**／不触发 falsifier／**实现者不自签·独立复审·落定走三件套**／**每条 EA 必须带敏感性区间 + `equivalent_to_disclosure_basis=false`**）；L769-L775 边界；L779 `I-11-C ← I-11-B` **另派** | 逐字读毕 ✓；文件自算 `17c0db1dbdbb96b5…`（109,029 B）与被审件 `handoff.input_hashes` 一致 ✓ |
| 授权 `§三十六`（L820-L848） | H4 Q2 条件 5 **追加式**修订；「不放行任何参数」边界不变 | 逐字读毕 ✓（`proposed_not_released` 同形先例的依据） |
| 卡文 `card_I-11-C.md`（25 行） | L5 Owner=未参与参数设定的独立研究 reviewer、依赖 I-11-B；L13-L16 reviewer 四动作；L18-L21 `STOP_REVIEW`/`STOP_LINEAGE`；L23 验收；L25 证据四件（`evidence/I-11-C/*`） | 逐字读毕 ✓；sha `b7812e38e425dd00…`/1433 B 与被审件记录一致 ✓；**`evidence/I-11-C` 目录实测不存在**（实现者未越界代建 reviewer 面）✓ |
| 输入 `I-11-B/a20260926-01` | 4 件被引输入自算 sha：`calibration_plan e86b4135…`/32,665 · `expert_assumptions 9f8b844e…`/8,580 · `synthetic_mechanism_check 89f4bafd…`/8,035 · `revert_or_stop 9d5e05f1…`/4,367 | **4/4 与 `handoff.input_hashes` 逐字节一致** ✓（复审收尾再次复核仍一致） |
| 输入 其复审 `I-11-B/reviewer_report.md` | 28,698 B，自算 `5af4987ee0547a53…`；侧车 `reviewer_report.sha256`（84 B）内容与自算**逐字节相同**；其裁决行（L18，全文唯一）判级文本 = `ACCEPT (with P2x3, P3x3; strict-reading dispute ruled NOT triggered)` | 三方一致 ✓；其 **`P2-1`（store base 矛盾、OPEN-2 前禁消费）** 与 **`P2-2`（`carrier_form` 7/7 缺）**、**`P2-3`（C3-④ 事实过时）** 为本次专项核验输入（§4、§5） |
| 形态先例 `H4 (iv)` | `expert_assumptions.json` 顶层 `carrier_form = "A-6.3 (iv) expert_assumption + 敏感性区间"`；7 条逐条 `release_state=not_released` | 与 oracle §3 冻结模板比对 ✓（逐条 `carrier_form` 缺口见 P2-3） |
| 被审件基线（开工首条命令自算） | 见 §7 表；9 主件与 `handoff.written_files_hashes` 记录的 8 条前缀**逐一 MATCH**（`437a7758…`/`d542b34d…`/`cecdcb33…`/`5be2e58a…`/`02fdd5ae…`/`35fc25a2…`/`9c391594…`/`9b37db31…`） | ✓ 且收尾复哈希**前后相同** |

---

## 2. 五项复核

### 2.1 映射可执行性 —— **PASS（18/18 逐条核毕；13 条带数值行全部本工位独立复算，0 失败；记录层 2 处缺陷 → P2-1）**

**方法**：`%TEMP%\i11c_rev\recompute.py`（`fractions.Fraction` + 浮点双轨，只读 4 个输入）先做**全量复算**（不只抽样），再逐行核 `unit` / `period_start` / `period_end` / `original_value` / `new_value` / `conversion_formula` 与上游 `calibration_plan.json` 的逐字段同一性（脚本断言 11 字段 × 18 行）。

**① 转录同一性（18 行 × 11 字段）**：`parameter_id / hypothesis_id / model_id / driver_name / unit / period_start / period_end / original_value / new_value / conversion_formula / ea_refs` —— **18/18 与 CP 完全相同，唯一差异 = 第 5 行 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的 `new_value` 由 CP 的 `{118036.2, 124248.63, 130461.06}` 改为全 `null`**（并把上游三值存档进 `i11b_proposed_values` + `not_executable_no_propagation`）——这是本卡**正确的**不可执行处置，不是誊写差错。

**② 本工位重算 3 条（含 1 条 EA 承接；实际 13 条全算）**：

| 抽样 | 行 | 我的复算 | 判 |
|---|---|---|---|
| **A**（EA-1/EA-3 承接） | `ZIJIN_SEG_SMELT_EXTERNAL_REVENUE_FY2027`（人民币元，FY2025 基期→FY2027） | base=165,858,644,874；×0.95 = **157,565,712,630.30** → 表列 157,565,712,630（Δ0.30）；×1.05 = **174,151,577,117.70** → 表列 174,151,577,118（Δ0.30）；容差 ±0.5 元 ✓ | ✓ |
| **B**（EA-1/EA-3 承接） | `ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027`（吨，FY2025→FY2027） | 884,943×0.9 = **796,448.7** 逐位；×1.1 = **973,437.3** 逐位；`original_value=884,943（FY2025 销售量）` 与 store 产销量表一致 ✓ | ✓ |
| **C**（EA-4/EA-1 承接，增长率复合带） | `MSFT_PBP_REVENUE_FY2027`（小数，FY2026 基线年→FY2027） | g_low=(1.16×0.95)−1 = **0.102** 逐位；g_high=(1.16×1.05)−1 = **0.218** 逐位；与 EA-4 `sensitivity_interval` 的 `0.102 / 0.16 / 0.218` 逐位一致 ✓ | ✓ |

**其余 10 条带数值行同法全算全对**：SEG×4 的 ±5%（MINERAL：×0.95 = 104,478,678,527.75 → 104,478,678,528，Δ0.25；×1.05 = 115,476,434,162.25 → 115,476,434,162，Δ0.25）、VOL×4 的 ±10%（金 83,161→74,844.9/91,477.1；锌 352,470→317,223/387,717；银 430,254→387,228.6/473,279.4，均逐位）、PLAN 达成率带（金 105,000 kg→**94,500/115,500**；铜 1,200,000 t→**1,080,000/1,320,000**，均精确）、MSFT IC/MPC 复合带（0.235/0.365；−0.0595/0.0395，均逐位）、RECON 恒等式（584,049,229,264−234,970,146,412 = **349,079,082,852**；四分部对外合计 = **349,079,082,852**；四分部毛总计和 = **584,049,229,264**，三路差 0）。**差额法 base 复算**：349,079,082,852−165,858,644,874−29,212,610,830−44,030,270,803 = **109,977,556,345**（差=0）。

**③ 不可执行 5 行（零传播）核验**：`new_value` 三档**全 null**（脚本逐行断言）；`missing[]` 逐条列明缺什么；第 5 行的 `i11b_proposed_values` 仅为上游三值**存档**并附「传播值置 null」注记 —— 5/5 成立。

**④ 本工位对两处新发现的独立复算**：
- **N2（分母不自洽）**：`884,943+83,161×24 = 2,880,807`；`885,141−884,943 = 198`；`109,977,556,345 ÷ 885,141 = 124,248.6297…`；`÷ 2,880,807 = 38,175.9543…`；两商比 **3.2546**。⇒ 证实 store L170/L175 等式自身不闭合，被审件判 `not_executable` **正确**（数值小注：卡内写「3.26 倍」，精确应为 **3.25 倍** → P3-6①）。
- **N3（EA-4 注记区间）**：按其自身 g 带作用于 FY2026 三分部 → 低 **375,283.383**（154,275.592+170,171.885+50,835.906）、高 **414,786.897**（170,515.128+188,084.715+56,187.054）；基期合计 331,839 ±5% = **[315,247.05, 348,430.95]**（与注记 `[320763, 348432]` 高位差 1.05）。⇒ **证实注记与自身带换算不符**，被审件登记 `unverified-N3` 正确且只在注记层（运行值全对）。

**⑤ 记录层缺陷（值与 verdict 都对，四查叙述是样板）→ P2-1**：
- `period_check` **18 行同一句**「…FY2027 生效行基期=FY2025（FY2026 无同口径观测，EA-3 朴素基线）」，与 **6 行**自身的 `period_start/end` 冲突（PLAN 行 FY2026→FY2026；`MSFT_PBP/IC/MPC` FY2026 基线年；`MSFT_CLOUD`/`MSFT_LICENSING` FY2026 基线）——这 6 行基期是 **FY2026**、依据是 **EA-4/披露值**，不是 FY2025+EA-3。
- `formula_check` **17 行同写「公式逐项可复算（RECOMP）」**，与 **4 行**冲突：`MSFT_CLOUD`（`conversion_formula="无（store：无可用的换算公式）"`、`amplitude` 明写「无公式」）、`MSFT_LICENSING`（`"无（store：不写换算公式）"`）、`COPPER/GOLD_REALIZED`（`"…（待 OPEN-2 解锁后…）"`，且 `amplitude` 明写「无基期」）。
- `unit_check` **18 行同一句**，其行号清单只列 **16/18** 个单位行（漏 `CP L98/L109`，恰是两条显式拒绝的实现价槽位）→ P3-6②。
- 说明：`verdict`（13/5）、`missing[]`、`amplitude`、`carve_out` **均为逐行真实内容且正确**；缺陷限于上述样板叙述，**不改变任何数值、单位、起止年份字段与可执行性判定**。

**观察（不计 P）**：第 1 行 `blocked_by` 含 `OPEN-2`（承接 CP L46「量价口径系数未解」）同时 `propagation=allowed_not_released` —— 与 CP 原文一致、且 `handoff.blocked_by` 已自宣为「登记性，非本卡新增阻塞」；`OPEN-2` 对分部收入行的实际约束落在量价系数上，本复审不据此判缺陷。

### 2.2 EA 依从性 —— **PASS（17/18 挂 EA；7/7 有区间 + `eqt=false`；无"借 EA 出无依据数"；模板字段缺口 → P2-3）**

**EA 引用统计（本工位脚本实测）**：

| EA | 被 `source.ea_refs` 引用的行数 | `sensitivity_interval`（5 键齐） | `equivalent_to_disclosure_basis` | `release_state` |
|---|---|---|---|---|
| EA-1（带形状） | 13 | ✓ `low/base/high/unit/band_rationale` | **false** ✓ | not_released |
| EA-2（系数 24 示意） | 1（REALIZED_UNIT） | ✓ | **false** ✓ | not_released |
| EA-3（朴素基线） | 9 | ✓ | **false** ✓ | not_released |
| EA-4（MSFT 增速） | 3 | ✓ | **false** ✓ | not_released |
| EA-5（矿产分部 base） | 1 | ✓ | **false** ✓ | not_released |
| EA-6（联合情景结构约束） | **0**（不进 `ea_refs`） | ✓ | **false** ✓ | not_released |
| EA-7（显式拒绝出数） | 4 | ✓（n/a 形态 + 带设计预登记） | **false** ✓ | not_released（无值可放） |

- **17/18 行挂 EA**：唯一例外 `ZIJIN_SEGMENT_RECONCILIATION_FY2027`（`ea_refs=[]`，纯 contract arithmetic 恒等式 + 已签容差 τ=1 元）——与 `action_3_source_counts.contract_arithmetic_only=1` 一致，**例外成立**。
- **挂上的都是本卡 EA-1..EA-7 的真实条目**：全部 `ea_refs` ∈ {EA-1…EA-7}，**无未知引用**（我方构造 `EA-99` → 校验器 rc=1 具名，见 §2.4）；且 `ea_refs` 与 `CP.ea_refs` **18/18 逐字相同**（转录无漂移）。
- **"挂 EA 却没区间 / 没标 equivalent=false"的缺陷：未发现**（7/7 齐备；我方把 EA-1 `eqt→true`、删 EA-4 `sensitivity_interval` 两个红变异均 rc=1 具名）。
- **"借 EA 之名出无依据数"：未发现** —— 13 行的 `base` 全部可回源（分部四行→store raw + 差额法；量四行→store 产销量表；PLAN→p56 计划原值；MSFT×3→FY2026 已披露增速；RECON→恒等式），**EA 只承担带/基线规则**；`124,248.63`（唯一无据可复算的 base）**未传播**（§4）。
- **EA-6 的承载方式**：不进 `ea_refs`，改由 `joint_scenario_constraint` 字段承载 —— **18/18 行在位**（6 行显式点名 `EA-6`），符合其"结构约束而非幅度来源"的性质；`verify_mapping.py` 不校验该字段 → 观察项（并入 P2-2 的覆盖清单）。
- **模板字段缺口 → P2-3**：`expert_assumptions.json` **7/7 条逐条缺 `carrier_form`**（仅文件顶层有），而**被审件自己的** oracle §3 冻结模板含该字段并自设「缺任一字段 ⇒ 该条不成立 ⇒ 对应映射触发 STOP」；`verify_mapping.py` 的 J2 **只测 2 个字段**（我方 T4c 用原样 EA 文件跑 → rc=0）。该缺口与上游 `I-11-B P2-2` 同源、**本卡未登记为继承项** ⇒ 记 P2-3（信息零损失、区间与 `eqt=false` 两项要件齐备，**不据此判 STOP、不构成 P1**）。

### 2.3 参数不放行 —— **PASS（`params_released=false` 实证齐全）**

| 实证点 | 本工位实测 |
|---|---|
| store `low/base/high` | 全树 walk：`low`×12 / `base`×12 / `high`×12，**全部 `null`**（0 个非 null） |
| `_PLACEHOLDER` 维持 | 两个 id（`ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER`）在 store 文本**在位**；`_PLACEHOLDER` 出现 2 次 |
| `released` | store 内 4 处，**全 `false`**；行号实测 `ST L191 / L210 / L386 / L405` 逐行 `false` ✓ |
| store 零改动 | `hypotheses_v3.json` 自算 `b2063ac8533a96ba…`/61,231 B，与 `handoff.input_hashes` 一致；**全部 5 个 store 文件 mtime = 2026-09-26 01:04–01:17**（远早于 I-11-C 窗口 18:00–18:22） |
| **映射值落点** | 抽 8 个 distinct `low/high` 值检索：`hypotheses_v3.json` **仅命中 base 原值 `109977556345`（披露 raw，非放行值）**，`low/high` **零出现**；`I-11-B/calibration_plan.json` 命中（上游 `proposed_not_released` 载体，本就是这些值的出处）；`I-11-B handoff/oracle/expert_assumptions` **零命中** ⇒ 映射值只在**卡内载体**（I-11-B plan + I-11-C mapping），不进 store/封盘/model_cards |
| `value_state` 普查 | `mapped_not_released`×13 · `unmapped_declined_no_number`×4 · `not_executable_no_propagation`×1；**无任何 `released*`** |
| handoff 锁字段 | `params_released=false`、`implementer_signed=false`、`releases_nothing=true`、`status=review_pending`、`falsifiers_triggered=0`、`auto_actions_triggered=0`、`git_status_run=false`、`git_writes_performed=false`、`network_requests_made=0` —— 与被审件正文一致 |
| 越界写检查 | `evidence/I-11-C` **不存在**；五份计划文件 mtime 17:27:02/17:33:28/17:33:52（**均早于 I-11-C 窗口**）；本目录内**无任何 `hypotheses*`/`model_cards*` 新版本** |
| 红证 | 我方 `R3`（`handoff.params_released→true`）rc=1 J1；`R4`（`handoff.status→accepted`）rc=1 J1；`R1`（`value_state→released`）rc=1 J1 |

### 2.4 STOP 核验 —— **绿 rc=0 + 我方 10 红 rc=1 具名；STOP 分支真伪成立；另有 2 处覆盖盲区 → P2-2**

**执行方式**：`verify_mapping.py` **原路径只读执行**（源码审读确认零写入），变异副本与输入副本全部落 **`%TEMP%\i11c_rev\`**（沙箱允许 %TEMP% 写，未改原路径）。**未重跑被审件 `_run_mutations.py`**（它会重写被审件 `_mut/`），改以自建变异等价覆盖。

**绿（真伪基线）**：默认参数与显式四路径各跑一次 → **`ALL_INVARIANTS_OK` rc=0 ×4**（原件 2 次 + 我方重新序列化副本 2 次）。

**红（我方自建变异，全部具名 rc=1）**：

| # | 构造（数据不足/放行/红线） | rc | 首条违例 |
|---|---|---|---|
| **T1** | **"数据不足"槽位带数字**：`COPPER_REALIZED`（`value_state=unmapped_declined_no_number`）注入 `{61000, 64210.5, 67421}` | **1** | `J1 violated: … unmapped/blocked but new_value not all-null (propagation of numbers forbidden)` |
| R1 | `mapping_rows[0].value_state → "released"` | 1 | `J1 violated: … value_state='released'` |
| R2 | `rows[0].new_value.base → 281520`（合成示例数） | 1 | `J2 violated: … base=281520 is a quarantined synthetic number` |
| R3 | `handoff.params_released → true` | 1 | `J1 violated: handoff.params_released != false` |
| R4 | `handoff.status → "accepted"`（自签探针） | 1 | `J1 violated: handoff.status='accepted' != review_pending` |
| T3 | `ea_refs` 加 `EA-99`（未知 EA） | 1 | `J2 violated: … references unknown EA 'EA-99'` |
| T4 | 副本删 EA-4 `sensitivity_interval`（3 条 MSFT 行仍引用） | 1 | `J2 violated: MSFT_PBP/IC/MPC … relies on EA-4 which has no sensitivity_interval`（3 行具名） |
| T4b | 副本把 EA-1 `eqt → true` | 1 | `J2 violated: … relies on EA-1 with equivalent_to_disclosure_basis != false` |
| T5 | store 副本 `low:null → 0`（放行模拟） | 1 | `J3 violated: store low != null (got 0) — release detected` |
| T6 | `unverified_findings[0].registration → "resolved"` | 1 | `J4 violated: finding unverified-N1 registration='resolved'` |

**⇒ 派单要求的"构造数据不足输入验证会停"成立：T1 直接命中槽位级 STOP 分支并具名拦截。**

**盲区（P2-2，构造证据）**：
- **T2**：同一"数据不足"槽位带数字，但把 `value_state` 改成 `mapped_not_released`（`executability.verdict` 仍是 `not_executable`）→ **rc=0 `ALL_INVARIANTS_OK`**。校验器的 J1 **只认 `value_state`，不读 `executability.verdict`**，而 oracle §4.4 的槽位级 STOP 判据写的是「任一槽位映射不可执行/数据不足 ⇒ 不出数」——两字段解耦时 STOP 不触发。
- **R2b**：把合成数 `281520` 注入**字典型** `new_value`（PLAN 行 `base.gold_kg`）→ **rc=0**；J2 的合成数扫描只看 `low/base/high` 的标量，**不递归字典**。
- **T4c**：用**原样** `I-11-B/expert_assumptions.json` 跑 → rc=0；J2 只测 2 个字段（`sensitivity_interval`/`eqt`），不测 oracle §3 模板其余字段（与 P2-3 同源）。
- 覆盖清单：被审件 M1-M5 与我方 R1/R2/R3/T3/T4/T4b/T5/T6 均已覆盖；**T2/R2b/T4c 三个方向无任何变异覆盖**。

**实效核**：槽位级 STOP 实际生效（5 行 `new_value` 全 null，§2.1③）；卡级 —— 我核对"从严触发式"读法：13 行传播的 base **全部可回源**（contract arithmetic / 已签容差 / historical relationship + store 行号），带 **全部由 EA-1/EA-4 承接且带区间 + `eqt=false`**，5 个不可执行槽位**零数字** ⇒ **无"无来源又未明确声明"的幅度进入下游，`STOP_CALIBRATION` 不触发**；严格读法之争我**采纳上游 I-11-B 复审的裁定与四条逐字理由**（L20 是合取命题 / L13 正向指令 / owner §三十四 更高位授权 / ACCT L226 四类合法基础含"明示 expert_assumption+敏感性区间"），维持**不触发**；该争点在被审件中保持 open-form 登记（`stop_evaluation.card_level_strict_reading_registered`），**本复审不据此放行任何参数**。
**STOP_SCENARIO**：18/18 行携带 `joint_scenario_constraint`，未发现量 high×价 high×其他收入 high 独立叠加；E1-E7 复用禁令逐条转录在 `action_2_dependency_control_transcribed` ⇒ `stop_scenario_triggered=false` 成立。

### 2.5 封盘零字节 —— **PASS（`f2178768…` 自算命中；I-11-B 六件收尾复哈希一致；并发落定事件如实登记）**

- **`I-11-A/hypotheses.json` 我方自算 sha256 = `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（51,697 B，mtime 2026-09-20 15:48:19）** —— 与派单期望前缀 **`f2178768…` 一致** ✓；mtime 早于 I-11-C 窗口 5 天。
- **`I-11-B` 六件（其 `written_files`）收尾复哈希**：

| 文件 | sha256（前 16） | 字节 | mtime |
|---|---|---|---|
| `oracle.md` | `80a2cda0601fcec5` | 17,723 | 17:27:15 |
| `calibration_plan.json` | `e86b41355c1ba7c5` | 32,665 | 17:35:56 |
| `expert_assumptions.json` | `9f8b844e342ec17e` | 8,580 | 17:37:49 |
| `revert_or_stop.json` | `9d5e05f1ac3748aa` | 4,367 | 17:39:01 |
| `verify_plan.py` | `73f632fd976a0cfd` | 4,495 | 17:42:13 |
| `synthetic_mechanism_check.json` | `89f4bafda23d520c` | 8,035 | 17:43:28 |

  六件 mtime **全部 17:27–17:43 < I-11-C 窗口 18:00** ⇒ I-11-C **未改动**其上游；其中 4 件与 `I-11-C handoff.input_hashes` 逐字节一致（另 2 件无上游记录 sha，以本表为收尾基线）。
- **被审件 14 件：开工基线与收尾复哈希逐一相同（0 改动）**（§7）。
- **并发事件（如实登记，非我方改动）**：`I-11-B` 落定工位在本复审窗口内运行 —— `handoff.json` 于 **19:05:21** 被重写为 `status=accepted_scoped`（`review_pending → accepted_scoped`），`review.md` 于 **19:13:34** 新建（36,801 B），`qualification.json` 在我两次观测之间出现又消失（19:1x）。该落定 `review.md` 逐字载有 `not_granted`：**「`OPEN-2` 前禁消费 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 的 `base`（124,248.63 及其 ±5% 带…）」**，且声明 P2-1/P2-2/P2-3/P3-4/5/6 **六条全部 `carried`、无一销掉**。⇒ **`I-11-C` 所依赖的 4 件输入 sha 前后一致，本复审结论不因该并发事件改变**；`I-11-B` 落定件本体不在本次复审范围（只读引用其禁令原文）。
- store 侧 `hypotheses_v3.json` `b2063ac8…`/61,231 B 前后一致 ✓。

---

## 3. 18 条逐条判定表

> 图例：✓=该项复核通过；✗=该项记录有缺陷（值/字段本身正确，见 P 号）；`=null` 表示零传播（正确）

| # | parameter_id | 单位 | 起止年份 | 原值 → 新值（我方复算） | 转换公式自洽 | EA refs | value_state / verdict | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027 | 人民币元 ✓ | FY2025→FY2027 ✓ | 109,977,556,345 → 104,478,678,528 / 109,977,556,345 / 115,476,434,162（±5%，Δ0.25）✓ | ✓（差额法差=0） | EA-1, EA-3, EA-5 | mapped_not_released / executable | **PASS**（carve：N1 张力已登记） |
| 2 | ZIJIN_SEG_SMELT_EXTERNAL_REVENUE_FY2027 | 人民币元 ✓ | FY2025→FY2027 ✓ | 165,858,644,874 → 157,565,712,630 / … / 174,151,577,118（Δ0.30）✓ | ✓ | EA-1, EA-3 | mapped / executable | **PASS**（抽样 A） |
| 3 | ZIJIN_SEG_TRADE_EXTERNAL_REVENUE_FY2027 | 人民币元 ✓ | FY2025→FY2027 ✓ | 29,212,610,830 → 27,751,980,289（=27,751,980,288.5 进位）/ … / 30,673,241,372 ✓ | ✓ | EA-1, EA-3 | mapped / executable | **PASS** |
| 4 | ZIJIN_SEG_OTHER_EXTERNAL_REVENUE_FY2027 | 人民币元 ✓ | FY2025→FY2027 ✓ | 44,030,270,803 → 41,828,757,263 / … / 46,231,784,343 ✓ | ✓ | EA-1, EA-3 | mapped / executable | **PASS** |
| 5 | ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027 | 元/吨铜当量 ✓ | FY2025→FY2027 ✓ | 109,977,556,345/885,141 → **=null**（存档 118036.2/124248.63/130461.06 未传播）✓ | **✗ 不自洽（N2，我方复算证实：合成 2,880,807 vs 885,141；商比 3.2546）** | EA-1, EA-2 | not_executable_no_propagation / not_executable | **PASS**（零传播处置正确；N2 已登记；未消费上游 P2-1 base） |
| 6 | ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027 | 元/吨（不含税）✓ | FY2025（未取得）→FY2027 ✓ | null → **=null** ✓ | **✗ `formula_check` 样板**（"可复算" vs "待 OPEN-2 解锁"）→ P2-1 | EA-7 | unmapped_declined / not_executable | **PASS**（值层；记录层 P2-1） |
| 7 | ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027 | 元/克（不含税）✓ | FY2025（未取得）→FY2027 ✓ | null → **=null** ✓ | **✗ 同上** → P2-1 | EA-7 | unmapped_declined / not_executable | **PASS**（值层；记录层 P2-1） |
| 8 | ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027 | 吨 ✓ | FY2025→FY2027 ✓ | 884,943 → 796,448.7 / 884,943 / 973,437.3（±10% 逐位）✓ | ✓ | EA-1, EA-3 | mapped / executable | **PASS**（抽样 B；carve：BLOCKED-6b 未签已登记） |
| 9 | ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027 | 千克 ✓ | FY2025→FY2027 ✓ | 83,161 → 74,844.9 / … / 91,477.1 ✓ | ✓ | EA-1, EA-3 | mapped / executable | **PASS** |
| 10 | ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027 | 吨 ✓ | FY2025→FY2027 ✓ | 352,470 → 317,223 / … / 387,717 ✓ | ✓ | EA-1, EA-3 | mapped / executable | **PASS** |
| 11 | ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027 | 千克 ✓ | FY2025→FY2027 ✓ | 430,254 → 387,228.6 / … / 473,279.4 ✓ | ✓ | EA-1, EA-3 | mapped / executable | **PASS** |
| 12 | ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER | 吨/万吨→千克/吨 ✓（105 t=105,000 kg；120 万 t=1,200,000 t） | FY2026→FY2026 ✓ | 105,000 kg / 1,200,000 t → 94,500/115,500 kg、1,080,000/1,320,000 t（达成率 [0.9,1.1] 精确）✓ | ✓（带=EA-1 形状） | EA-1, EA-3 | mapped / executable | **PASS**（`_PLACEHOLDER` 维持；**`period_check` ✗ 说成 FY2025→P2-1**；EA-3 对计划年基期仅为承接注记） |
| 13 | ZIJIN_SEGMENT_RECONCILIATION_FY2027 | 人民币元 ✓ | FY2025→FY2027 ✓ | 恒等式 → 0/0/0（τ=1 元）✓（我方三路复算差=0） | ✓ | **[]**（唯一无 EA 行，纯 contract arithmetic） | mapped / executable | **PASS** |
| 14 | MSFT_PBP_REVENUE_FY2027 | 小数（增长率）✓ | FY2026 基线年→FY2027 ✓ | 0.16 → 0.102 / 0.16 / 0.218（复合带逐位）✓ | ✓ | EA-1, EA-4 | mapped / executable | **PASS**（抽样 C；**`period_check` ✗ 说成 FY2025+EA-3 → P2-1**） |
| 15 | MSFT_IC_REVENUE_FY2027 | 小数 ✓ | FY2026→FY2027 ✓ | 0.30 → 0.235 / 0.30 / 0.365 ✓ | ✓ | EA-1, EA-4 | mapped / executable | **PASS**（同上 P2-1） |
| 16 | MSFT_MPC_REVENUE_FY2027 | 小数 ✓ | FY2026→FY2027 ✓ | −0.01 → −0.0595 / −0.01 / 0.0395 ✓ | ✓ | EA-1, EA-4 | mapped / executable | **PASS**（同上 P2-1） |
| 17 | MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER | USD million ✓ | FY2026→FY2027(unquantified) ✓ | 214,400（叙述值）→ **=null** ✓ | **✗ `formula_check`"可复算" vs `conversion_formula`"无"、`amplitude`"无公式"** → P2-1 | EA-7 | unmapped_declined / not_executable | **PASS**（值层；记录层 P2-1；`_PLACEHOLDER` 维持） |
| 18 | MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027 | USD million ✓ | FY2026→FY2027(pending) ✓ | 101,997 → **=null** ✓ | **✗ 同上** → P2-1 | EA-7 | unmapped_declined / not_executable | **PASS**（值层；记录层 P2-1） |

**计数核**：18 = 13 `mapped_not_released`（有数值）+ 4 `unmapped_declined_no_number` + 1 `not_executable_no_propagation`；`action_1_summary` 13 executable / 5 not_executable 与我方逐行判定**完全一致**；`from_expert_assumption=17`、`contract_arithmetic_only=1` 与 `ea_refs` 实测**一致**。

---

## 4. 专项：是否消费上游 `P2-1` 的矛盾 `base`

**上游禁令（逐字，`I-11-B/…/review.md` L406 `not_granted`）**：「`OPEN-2` 前**禁消费** `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 的 `base`（**124,248.63 及其 ±5% 带**，P2-1 矛盾未补登前）」。

**本工位实证（脚本检索 + 逐行断言）**：

| 检查 | 结果 |
|---|---|
| `124248.63 / 118036.2 / 130461.06` 出现在哪些行 | **仅** `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 一行 |
| 该行 `new_value` | **`{low: null, base: null, high: null}`** |
| 该行 `value_state` / `propagation` | `not_executable_no_propagation` / **`blocked_no_propagation（槽位级 STOP：…数字不得进入任何下游）`** |
| 任何 `new_value` 内含 `124248.63`？ | **False**（全表断言） |
| 该三值在本卡出现的**唯一实体位置** | `i11b_proposed_values`（上游拟值**存档**字段）+ `action_1_summary`/`unverified_findings` 的差异描述文本 + `_recompute_action1.py` 的探针断言 + `_mut/` 变异副本 |
| 是否被用作任何其他行的输入 | **否**（SEG×4、VOL×4、RECON、MSFT×3 的 base 全部来自 CP 原值/恒等式，逐字段与 CP 同一） |
| 是否登记 | **是**：`unverified-N2`（`parameter_mapping.unverified_findings` + `handoff.unverified_findings_registered`，均 `registration=unverified`），并明写「proposed 值在更正前不得传播」 |

**结论**：**未消费**。上游 `P2-1` 的两条处置要求在本卡载体上均已满足（① 补登 `unverified` —— 本卡 `unverified-N2`；② 禁止下游消费 —— 零传播 + 我方断言为证）⇒ **本卡不因 `P2-1` 转 `unverified`/`changes_required`**。同一上游项的 `P2-2`（`carrier_form`）、`P2-3`（C3-④ 事实过时）**在本卡未被登记为继承项** ⇒ 分别记 **P2-3** / **P3-4**（见 §5）。

---

## 5. 判级与 P 清单

**ACCEPT**（无 P1；不构成 `changes_required`）

**P2（落定前必须处置；均可在 I-11-C 本 attempt 写入面内完成）**

- **P2-1 四查记录样板化与自相矛盾**：`period_check` 18 行同一句、与 **6 行**（PLAN、MSFT×3、CLOUD、LICENSING）自身 `period_start/end` 冲突（基期实为 FY2026、依据 EA-4/披露值，非 FY2025+EA-3）；`formula_check` 17 行写「公式逐项可复算」、与 **4 行**（COPPER/GOLD_REALIZED、CLOUD、LICENSING）的 `conversion_formula`=`无/待解锁` 及 `verdict=not_executable` 冲突；`unit_check` 行号清单 16/18。**处置**：按行重写这三组叙述字段（`verdict`/`missing`/`amplitude`/`new_value` 无需改动），并在 `mapping_verification.json` 增列四查逐行差异表。
- **P2-2 `verify_mapping.py` 三处覆盖盲区**（STOP/隔离校验不完整）：① `executability.verdict=not_executable` 与 `value_state` 解耦时不失效（T2 rc=0）；② 字典型 `new_value`（PLAN 行）内数值不进 J2 合成数扫描（R2b rc=0）；③ J2 只测 EA 模板 8 字段中的 2 个（T4c rc=0）、且不校验 18 行必备的 `joint_scenario_constraint`。**处置**：J1 增「`verdict=not_executable` ⇒ 三档全 null」、J2 改递归扫描 + 扩到模板 8 字段 + 校验 `joint_scenario_constraint` 存在性；新增对应红变异（M6/M7/M8）重跑红绿。
- **P2-3 EA 模板 `carrier_form` 逐条缺失（7/7，继承上游 `I-11-B P2-2`）且本卡未登记**：按被审件自身 oracle §3 的失败条款字面「缺任一字段 ⇒ 该条不成立 ⇒ 对应映射触发 STOP」，7 条 EA 均处该状态；信息零损失（顶层已有常量串）、区间与 `eqt=false` 两项要件 7/7 齐备 ⇒ **不据此判 STOP、不构成 P1**。**处置**：二选一 ——（a）上游补齐 7 行常量后本卡复验；（b）本卡以继承项形式登记 `unverified` 并把 J2 扩到 8 字段（与 P2-2③ 合并做）。

**P3（记录在案，不阻断）**

- **P3-4 `C3-④` 事实过时（继承上游 `I-11-B P2-3`）**：被审件写「`IND-r2` 在跑未归（`execution_runs/OPEN-3-IND-R2/a20260926-01/` **空/零文件**）」；我方实测该目录 **9 件**，`ruling_ind_r2.md` 17:34:28、`ind_ruling_r2.json` 17:36:20、`handoff` 17:38:08 —— 均**早于**被审件写入（oracle 18:02:41 / handoff 18:22:18）。登记形态 `unverified` 正确、方向保守（少报已知信息），不构成红线；落定前须刷新事实描述（与上游 P2-3 同源、根项已在上游在案）。
- **P3-5 `m3`/`m5` 变异副本基于定稿前的 handoff 旧快照**：deep-diff 实测各 **15 个叶键差异**（目标变异 1 处 + `written_files`/`written_files_hashes` 属旧版），非纯单字段差分（同上游 P3-6）；被测不变量本身经我方在**当前** handoff 上重跑（R3 rc=1、T6 rc=1）已复证。`m1`/`m2`/`m4` 为**纯单字段**差分（1/1/5 叶，均即预期变异）✓。
- **P3-6 数值与引文小注**：① N2 描述「商差 **3.26** 倍」精确值 **3.2546 ⇒ 应为 3.25 倍**；② `unit_check` 行号清单漏 `CP L98/L109`（16/18）；③ `parameter_mapping.json` 及 `_mut/` 5 副本为 **CRLF**、其余 7 主件为 **LF**（**14 件全部无 BOM**、JSON 均可解析，`parameter_mapping.json` 的 1,332 行全 CRLF）——行尾不一致仅记录，不影响任何校验。

---

## 6. unverified 清单（本复审后仍开放，移交落定/后继）

**承继被审件（全 open-form，我方复核形态无一写作"已解"）**
1. C3-① origin 字节 · C3-② B2 晋升 · C3-③ ACCT-R2 定级 · C3-④ IND-r2（**事实描述待刷新 → P3-4**）· C3-⑤ MSFT/新分部/HK 参数不放行 —— 5 项 `unverified`
2. C5-① 6c 阈值复审态 · C5-② H4 口径桥残差 · C5-③ 6b 恒等式容差 · C5-④ H2 基准 —— 4 项 `unverified`
3. `unverified-N1`（store `349,079,082,852` 分部语义张力；EA-5 实测张力比 **3.1741**）—— **仍 open**（未回源 AR p327/p328）
4. `unverified-N2`（分母 885,141 权威推导/算术更正）—— **算术层我方已独立复算证实不自洽**；**权威推导仍 open**（会计面 + AR 产销量表回源）
5. `unverified-N3`（EA-4 注记区间来源）—— **算术层我方已独立复算证实**（[375,283.383, 414,786.897] vs 注记 [320763, 348432]；基期 ±5% = [315,247.05, 348,430.95]）；**注记数字的来源仍 open**
6. `unverified-D1`（I-11-C 两站拆分确权归编排层）—— 非本工位职权

**本复审新增（open）**
7. `unverified-R1`：EA 模板 `carrier_form` 缺口的继承处置（= P2-3）
8. `unverified-R2`：`C3-④` 事实刷新（= P3-4）
9. `unverified-R3`：校验器 T2/R2b/T4c 三盲区的补检与补变异（= P2-2）
10. **严格读法之争**：我**采操作读法 + 上游裁定**，判 `STOP_CALIBRATION` **不触发**；登记保持 open-form，若落定/owner 采严格读法 ⇒ 本卡转 `blocked`（回滚 = 作废本表 13 行 `mapped_not_released`，零封盘改动、零 store 改动）——**本复审不因该争点放行任何参数**

---

## 7. 审计轨迹与收尾复哈希

**被审件 14 件 开工基线 = 收尾复哈希（逐一相同，0 改动）**

| 文件 | sha256（前 16） | 字节 |
|---|---|---|
| `handoff.json` | `77f3bbab3f66deda` | 16,815 |
| `mapping_verification.json` | `cecdcb33281727f7` | 9,193 |
| `oracle.md` | `437a7758da4c0387` | 16,336 |
| `parameter_mapping.json` | `d542b34d3429f240` | 54,875 |
| `verify_mapping.py` | `5be2e58a942e7d93` | 6,685 |
| `_build_mapping.py` | `35fc25a2bacf7669` | 23,999 |
| `_check_hashes.py` | `9c3915948a448557` | 1,925 |
| `_recompute_action1.py` | `02fdd5ae5b8f275e` | 4,497 |
| `_run_mutations.py` | `9b37db31e02e9f6a` | 3,387 |
| `_mut/m1_released.json` | `bda6501a74a3da1b` | 54,862 |
| `_mut/m2_synthetic.json` | `c19edc9daca67418` | 54,867 |
| `_mut/m3_params_released.json` | `dbf6bb8646b6bc5c` | 16,707 |
| `_mut/m4_ea_missing_interval.json` | `d27fe0eb102af627` | 8,507 |
| `_mut/m5_residual_resolved.json` | `652eb3293352dbfd` | 16,706 |

- 编码检查：**14/14 无 BOM**；`parameter_mapping.json`+`_mut` 5 件为 CRLF，其余 8 件 LF（→ P3-6③）；全部 JSON 经 `json.load` 解析通过。
- 输入指纹复验：`_check_hashes.py`（原路径只读执行）→ **`RESULT ALL_OK`（8/8）**；我方独立自算同一 8 项**逐一 MATCH**。
- git：只读 `git -c core.quotepath=false diff HEAD --name-only` → **total=3830、`non_planning=0`**（与被审件所记一致）；**未运行 `git status`、零 git 写**；⚠️ 该证据有界：`git diff HEAD` 不含 untracked 文件，故"无 .planning 外写入"只能作**有界证据**（另以 `evidence/I-11-C` 不存在、五份计划文件 mtime 早于窗口、本目录无 hypotheses/model_cards 新版本三路旁证）。
- 自建产物（**唯一在 %TEMP% 的写入**）：`%TEMP%\i11c_rev\{recompute.py, stop_tests.py, red_runs.py, audit2.py, t*/r*_*.json}` —— 被审件与输入**零写入**。
- 本报告写入面：`execution_runs/I-11-C/a20260926-01/reviewer_report.md` + `reviewer_report.sha256`（**2 件**）。

---

## 8. 本复审没有做的事

- **未写任何卡状态**：不改 `card_*`、不改被审件任一字节、不改 `I-11-B` 任何文件；**未产出落定三件套**（`review.md`/`qualification.json`/`handoff.json` 归落定环节）。
- **未回源原始披露字节**：`CN-ZIJIN-AR2025` p327/p328、产销量表、p56 经营计划、`US-MSFT-2026` 10-K 分部行**未直接重读**；对 base 与原值采信 **store `raw_value` 逐字 + `calibration_plan` 转录 + I-11-B 复审已核**三重转引；`unverified-N1/N2` 的字节级回源仍开。
- **未重开上游验收**：`I-11-A`/`I-10-A`/`OPEN-2/3/5/6`/`BLOCKED-*` 各 handoff 只核被引字段与 sha，不重开其裁决；**并发落定中的 `I-11-B review.md`/`qualification.json` 本体未复审**（只读引用其 `not_granted` 禁令原文与 `carried` 清单）。
- **未重跑被审件 `_run_mutations.py`**（会重写被审件 `_mut/`，与只读纪律冲突）——改以 `%TEMP%` 自建 13 个变异等价覆盖（§2.4），并以 deep-diff 复核其 5 个副本的纯度（→ P3-5）。
- **未跑 `git status`**（派单禁止）、**未联网**、**未提权**、未做任何 git 写。
- **未评估拟定值的预测质量/准确性**：本卡验收与本复审均只核可回源性/算术自洽/一致性/红线，不产生准确性结论。
- **未执行卡文 L13-L16 的 reviewer 四动作**（可证伪替代解释表 / falsifier 阈值 / 四失败标注 / 版本触发规则）与 `evidence/I-11-C/*` 四件的建立——`unverified-D1` 已登记该两站拆分，最终确权归编排层。
- **未裁 `unverified-D1`、未代 owner 作严格读法的最终裁定**（本报告只给出复审立场与后果核）；**未触发任何 falsifier/自动动作、未解除任何 `OPEN-*`/`BLOCKED-*`、未放行任何参数、未派 `I-07-E`**。

---

*复审工位签记：独立复审（非 I-11-B 实现者、非 I-11-C 实现者、未参与参数设定）；本报告不含自签验收效力，落定仍走三件套；`proposed_not_released`/`mapped_not_released` 同 `H4 (iv)`，不是放行。*
