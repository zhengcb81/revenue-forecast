# 载体落定 review — `I-11-B / a20260926-01`

> **`Test-Path` 断言（本文件新建前实测，逐字记录）**：`Test-Path .\review.md` → **`False`** ｜ `Test-Path .\evidence` → **`False`** ｜ `Test-Path .\evidence\I-11-B` → **`False`** ｜ `Test-Path .\evidence\I-11-B\qualification.json` → **`False`**
> ⇒ 本 attempt 内原先**不存在** `review.md`（无实现者存根需保留）⇒ **新建**；`evidence/I-11-B/` 目录与 `qualification.json` **一并新建**。
>
> **落定性质**：簿记转录（transcription only）。本文件只把独立复审**已经写下**的裁决搬进卡载体，
> **不产生新裁决、不自签、不解除任何 `OPEN-*` / `BLOCKED-*`、不放行任何参数、不升 `threshold_review_status`、
> 不把 `proposed_not_released` 当已发布、不晋升、不写产品仓任何字节、不写五份计划文件、不派 `I-11-C`。**
> 裁决字节非本工位产生：裁决只存在于 `reviewer_report.md`（本 pass 对该文件与侧车写入 **0** 字节）。

---

## 0. 裁决行定位（本落定工位**自行定位**，未采信派单给定的行号/字节区）

对 `reviewer_report.md` 原始字节独立读取 → 严格 UTF-8 解码 → 按 `LF` 切行 → 逐行累加回算 0-based 字节前缀和：

| 项 | 本工位实测 |
|---|---|
| carrier | `reviewer_report.md` |
| 字节 | **28,698** |
| sha256（自算） | `5af4987ee0547a5320fcc35d338d8dbf59ec086e031202638b909c2dfc7e200d` |
| 编码 | UTF-8 **无 BOM**（首字节 0x23）· **仅 LF**（CR=0，LF=208）· 208 行 · 结尾单个 LF |
| 裁决行行号 | **L18**（1-based），全文**唯一**出现的 `VERDICT` |
| 裁决行文本（逐字） | `VERDICT: ACCEPT (with P2x3, P3x3; strict-reading dispute ruled NOT triggered)`
| 裁决行字节区 | **`start=1384` / `end_inclusive=1462` / `end_exclusive=1463` / `length=79`**（0-based，区域不含行尾 LF） |
| 该 79 字节 sha256 | `2d212bed0fc137c234b1001ddebe42c28676d49e0812a89af1f49c062c065eb3` |
| 裁决词本体字节区 | `[1385, 1400)`，15 B，sha256 `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` = `VERDICT: ACCEPT` |
| 判级行 | L12：**判定：ACCEPT（附 P2×3 · P3×3；无 P1 ⇒ 不构成 `changes_required`）**
| §9 判级行 | L173：**ACCEPT**（无 P1；严格读法裁定不触发，故不转 changes_required）
| 三方 sha 一致核对 | 自算 `5af4987ee0547a53…` == 侧车 `reviewer_report.sha256`（84 B）内容 == 派单给定 `5af4987ee0547a53…` ⇒ **一致（true）** |

> 全文 `VERDICT` 出现 **1** 次、`ACCEPT` 出现 **3** 次（L12 判级、L18 裁决行、L173 §9）；**独立成行且唯一承载裁决词的行 = L18**。

---

## 1. 状态面转录

| 字段 | 值 |
|---|---|
| `status` | `review_pending` → **`accepted_scoped`** |
| `status_before` | `review_pending`（原值逐字） |
| `status_transition` | `review_pending -> accepted_scoped` |
| `status_scope` | **范围严格限于本卡交付物（oracle.md · calibration_plan.json · expert_assumptions.json · synthetic_mechanism_check.json · revert_or_stop.json · verify_plan.py · _mut/×5）的证据与判据**；非 clean accept（带 **3×P2 + 3×P3**） |
| `status_history` | **2 条**：① `review_pending`（实现者工位 `implementer_i11b`，交付 17:44:22）② `accepted_scoped`（本簿记落定工位，转录复审 L18 裁决） |
| `implementer_signed` | `false`（**未改**） |
| `verdict_is_transcribed_not_authored` | `true` |
| `pre_image`（handoff，改前自算） | **11,349 B / `8d8c974a102416676e9c48f52cb632c3ba6c7d8fa50af74d3b4db7a3e9c110ca`** |
| `post_image`（handoff，改后自算） | **37,319 B / `4c3c5c908f7c69b23f3ecec52fc81fcbd766e1bfa1174422f8abafbbd7caed31`** |
| 非状态面键 | 程序断言：除 `status` 外**逐键深比对全等（0 不符）**；新增键恰为 10 个落定键 |

---

## 2. `status_authority`（**镜像 1/2**，与 `handoff.json.status_authority`、`qualification.json.status_authority` 逐字段相等）

```json
{
  "carrier": "reviewer_report.md",
  "carrier_path_inside_attempt": "reviewer_report.md",
  "carrier_bytes": 28698,
  "carrier_sha256": "5af4987ee0547a5320fcc35d338d8dbf59ec086e031202638b909c2dfc7e200d",
  "carrier_sha256_prefix16": "5af4987ee0547a53",
  "carrier_total_lines": 208,
  "carrier_encoding": "UTF-8 无 BOM（BOM=False，首字节 0x23 即 # 号）；仅 LF 行尾（CR=0，LF=208）；文件以单个 LF 结尾；严格 UTF-8 解码通过",
  "carrier_encoding_flags": {
    "bom": false,
    "cr_count": 0,
    "lf_count": 208,
    "utf8_valid": true,
    "strict_utf8_decode": true,
    "first_byte": 35
  },
  "three_way_consistency": "落定工位自算 sha256 == reviewer_report.sha256 侧车内容 == 派单给定 5af4987ee0547a53…，三方一致",
  "three_way_match": true,
  "verdict_word_written_by_reviewer": "ACCEPT",
  "verdict_line_text_as_written_by_reviewer": "`VERDICT: ACCEPT (with P2x3, P3x3; strict-reading dispute ruled NOT triggered)`",
  "verdict_line": 18,
  "verdict_line_range_inclusive_1_based": [
    18,
    18
  ],
  "verdict_line_byte_region": {
    "start": 1384,
    "end_inclusive": 1462,
    "end_exclusive": 1463,
    "length": 79,
    "sha256": "2d212bed0fc137c234b1001ddebe42c28676d49e0812a89af1f49c062c065eb3",
    "decoded_utf8": "`VERDICT: ACCEPT (with P2x3, P3x3; strict-reading dispute ruled NOT triggered)`"
  },
  "verdict_token_byte_region": {
    "start": 1385,
    "end_inclusive": 1399,
    "end_exclusive": 1400,
    "length": 15,
    "sha256": "f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7",
    "decoded_utf8": "VERDICT: ACCEPT",
    "note": "裁决词本体 = 裁决行去掉首尾反引号后的前 15 字节"
  },
  "verdict_line_located_by": "本落定工位自行定位（读原始字节 → 严格 UTF-8 解码 → 按 LF 切行 → 逐行累加回算 0-based 字节前缀和）；行号与字节区均为自算，未采信派单文本",
  "verdict_line_unique": true,
  "verdict_line_other_occurrences_note": "全文 VERDICT 出现 1 次（唯一，即 L18）、ACCEPT 出现 3 次（L12 判级、L18 裁决行、L173 §9 判级）；独立成行且唯一承载裁决词的行 = L18",
  "judgement_line": 12,
  "judgement_line_text": "**判定：ACCEPT（附 P2×3 · P3×3；无 P1 ⇒ 不构成 `changes_required`）**",
  "section9_accept_line": 173,
  "section9_accept_line_text": "**ACCEPT**（无 P1；严格读法裁定不触发，故不转 changes_required）",
  "verdict_written_by": "独立复审工位（reviewer_report.md 的作者；与实现者 implementer_i11b 非同一人；实现者未自签）",
  "verdict_is_transcribed_not_authored": true,
  "implementer_signed": false,
  "transcribed_by": "carrier-landing bookkeeping executor（父派委派的簿记落定子代理）—— 只做簿记转录，不产生新裁决、不自签",
  "scope": "accepted_scoped —— 接受范围严格限于本卡交付物（oracle.md · calibration_plan.json · expert_assumptions.json · synthetic_mechanism_check.json · revert_or_stop.json · verify_plan.py · _mut/）的证据与判据；非 clean accept（带 3×P2 + 3×P3）",
  "pin_sidecar": {
    "file": "reviewer_report.sha256",
    "present": true,
    "bytes": 84,
    "sha256": "4f83905ab386ec06c4de3441b66a7805638a6bfb6ee57e7d29db1600b9c07a42",
    "content": "5af4987ee0547a5320fcc35d338d8dbf59ec086e031202638b909c2dfc7e200d  reviewer_report.md",
    "three_way_match": true,
    "verified": "侧车内容（64 位小写 sha + 两个空格 + 文件名 reviewer_report.md = 84 B，无换行）与落定时独立重算的 reviewer_report.md sha256 逐字节相同；三方一致；本 pass 对侧车写入 0 字节"
  },
  "read_only_by_this_pass": "本落定工位对 reviewer_report.md 与 reviewer_report.sha256 的写入字节数 = 0",
  "unverified_source": "reviewer_report.md §10（L185–L187）逐字转录进 handoff.unverified；实现者原残余登记（seven_conditions_status / c3_c5_residuals / dispatch_discrepancies_registered）原位保留，披露不丢失",
  "landing_file": {
    "file": "review.md",
    "pre_image": "落定前 Test-Path 断言全部 = False（.\\review.md → False；.\\evidence → False；.\\evidence\\I-11-B → False；.\\evidence\\I-11-B\\qualification.json → False）⇒ 无实现者存根需保留 ⇒ review.md 新建、evidence/I-11-B/ 目录与 qualification.json 一并新建"
  },
  "section_line_ranges_inclusive_1_based": {
    "verdict_line": [
      18,
      18
    ],
    "judgement_line": [
      12,
      12
    ],
    "strict_reading_ruling_section": [
      34,
      47
    ],
    "four_actions_section": [
      51,
      100
    ],
    "slots_section": [
      104,
      110
    ],
    "ea_section": [
      112,
      127
    ],
    "residuals_section": [
      129,
      144
    ],
    "mutations_section": [
      146,
      162
    ],
    "findings_section": [
      171,
      183
    ],
    "unverified_section": [
      185,
      187
    ]
  }
}
```

---

## 3. `carried_findings`（复审 §9 的 **6 条逐字**，不弱化、不改级、不销项）

```json
[
  {
    "level": "P2",
    "id": "P2-1",
    "dispatch_id": "P2-1",
    "source_section": "reviewer_report.md §9（L176）",
    "finding_verbatim": "- **P2-1** `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 基期可复算性缺陷：store L175 转换公式自相矛盾（`884,943+83,161×24=2,880,807` ≠ `885,141`；真值 38,175.95 vs 沿用值 124,248.63，差 3.25×；自洽基下两点差分应为 ≈−1,071 而非 −10,670.89）。处置：在卡内补登 unverified 项（store 先天缺陷+本卡沿用未标）；**OPEN-2 裁定前任何下游不得消费 124,248.63 及其 ±5% 带**；建议同时提示编排层在 OPEN-2 裁定时先修 store 口径桥。",
    "supporting_section": "reviewer_report.md §3-②（L84）",
    "supporting_verbatim": "**P2-1（本工位重算发现，卡内未登记）**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 的 base=124,248.63（=109,977,556,345÷885,141，实现除式本身自洽），但 **store `hypotheses_v3.json` L175 转换公式自写除式为「884,943 + 83,161×24」= 2,880,807 ≠ 885,141**——按自写除式真值 = **38,175.95**（差 3.25 倍）；两点差分框架（885,141→968,302，−10,670.89）只在 /885,141 基下自洽，若按自洽除式则每 +1 系数仅 ≈−1,071 元。该矛盾**是封盘 store 的先天缺陷**（本卡正确地未回改封盘），但本卡以「contract arithmetic（基期推导）」承接该 base 并逐字沿用矛盾除式，**未把\"base 不可复算\"登记为 unverified 项**（仅登记了系数来源缺口）。落定前必须补登 + 禁止任何下游在 OPEN-2 裁定前消费 124,248.63（详见 §9 P2-1）。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P2",
    "id": "P2-2",
    "dispatch_id": "P2-2",
    "source_section": "reviewer_report.md §9（L177）",
    "finding_verbatim": "- **P2-2** EA 模板 8 字段缺口：7/7 条缺逐条 `carrier_form`（oracle §5 自设失败条款字面即触发\"不成立\"）。处置：7 行常量补齐 + 校验器 I1 扩至 8 字段 + 新增 M6 变异（删 carrier_form 必红）重跑红绿。",
    "supporting_section": "reviewer_report.md §5（L126）",
    "supporting_verbatim": "- **模板缺口（P2-2）**：oracle §5 模板 8 字段中 `carrier_form` **7/7 逐条缺失**（文件顶层有）；按 oracle 自设失败条款的字面，7 条 EA 均不成立——信息零损失（常量串）但违反其自设模板纪律，落定前补齐（7 行常量）并把校验器 I1 从 2 字段扩到 8 字段 + 加 M6 变异（删 carrier_form 必须红）。",
    "also_at": "reviewer_report.md §2（L47）模板性缺口说明",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P2",
    "id": "P2-3",
    "dispatch_id": "P2-3",
    "source_section": "reviewer_report.md §9（L178）",
    "finding_verbatim": "- **P2-3** C3-④ 事实过时：「IND-r2 在跑（目录空）」在 handoff 交付时点（17:44:22）已不成立（IND-r2 17:34-17:38 已 RULED：segment_set_ok=yes content-layer+bridge caveat、S1 会签、E1 仍 BLOCKED-PARTIAL、零放行）。处置：更新登记详情（登记形态 unverified 不变）；确认 IND-r2 不改变本卡任一 blocked_by（本工位已核：不改变）。",
    "supporting_section": "reviewer_report.md §6（L136）",
    "supporting_verbatim": "| C3-④ | IND-r2 | unverified（**详情过时 → P2-3**） | **IND-r2 已在本卡运行窗内落地**（`OPEN-3-IND-R2/a20260926-01`：ruling_ind_r2.md 17:34:28、ind_ruling_r2.json 17:36:20、handoff 17:38:08 `status=RULED`；segment_set_ok=yes_content_layer_with_bridge_caveat、S1 countersigned、E1 维持 BLOCKED-PARTIAL、releases_nothing=true）。本卡 handoff 写于 17:44:22，其\"在跑未归（目录空）\"在交付时点已是旧值。**登记形态（unverified）仍正确**，事实描述须更新；IND-r2 未放行任何东西，I-11-B 的 blocked_by 不因此变化 |",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P3",
    "id": "P3-4",
    "dispatch_id": "P3-1",
    "label_note": "派单以 P3-1 指称；复审报告原文编号为 P3-4（一一对应，逐字取自报告，未弱化）",
    "source_section": "reviewer_report.md §9（L181）",
    "finding_verbatim": "- **P3-4** 金锭线 spot-check 誊算：39,757,982,580 应为 39,758,282,580（差 300,000）；真实线残差 +302,580（0.0007611%），结论不变。",
    "supporting_section": "reviewer_report.md §3-④（L99）",
    "supporting_verbatim": "  - P3-4（誊算差错）：卡内金锭线 spot-check 写作「49,074 千克×810.17 元/克 = 39,757,982,580 元」——**本工位重算真值 = 39,758,282,580（差 +300,000）**；对披露 3,975,798 万元的真实线残差 = +302,580（0.0007611%），**结论（线级容差内）不变**，但等式如印是错的。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P3",
    "id": "P3-5",
    "dispatch_id": "P3-2",
    "label_note": "派单以 P3-2 指称；复审报告原文编号为 P3-5（一一对应，逐字取自报告，未弱化）",
    "source_section": "reviewer_report.md §9（L182）",
    "finding_verbatim": "- **P3-5** EA-4 注解内联合收入带 [320,763, 348,432] 不可复现（应为 [375,283, 414,787]；g 运行值本身全对）。",
    "supporting_section": "reviewer_report.md §5（L127）",
    "supporting_verbatim": "- 数值小注（P3-5）：EA-4 band_rationale 的「三情景三分部收入合计区间 = [320,763, 348,432] USD mn」**不可复现**：按其自身 g 带作用于 FY2026 应为 **[375,283, 414,787]**；声称高点 ≈ FY2026 合计×1.05（348,431），低点无出处。运行值（g_low/g_high）本身全部正确，此为注解内数字错误。EA-2 k=23 点标注\"两点差分方向\"（134,919.5）系线性外推、精确值 137,132.54——已自declared为近似，可接受（备注级）。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P3",
    "id": "P3-6",
    "dispatch_id": "P3-3",
    "label_note": "派单以 P3-3 指称；复审报告原文编号为 P3-6（一一对应，逐字取自报告，未弱化）",
    "source_section": "reviewer_report.md §9（L183）",
    "finding_verbatim": "- **P3-6** M3/M5 变异副本基于旧 handoff 快照（mutation_rc=None 等），非纯单字段差分；建议以定稿字节重生成。",
    "supporting_section": "reviewer_report.md §7（L160）",
    "supporting_verbatim": "- 变异真实性（逐文件 deep-diff）：M1 仅 EA-1 缺字段 ✓；M2 仅 EA-2 eqt 翻转 ✓；M4 恰 12 处 `low: None→0`、余字节全同 ✓；M3/M5 主体变异正确，但**变异副本基于定稿前的 handoff 旧快照**（mutation_rc=None、缺 git_diff_non_planning_measured、written_files 旧版）——不纯单字段差分，P3-6 记录（被测不变量不受影响）。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  }
]
```

计数：**P1 = 0 · P2 = 3 · P3 = 3 · 合计 6**（判级行逐字，L12）：

> **判定：ACCEPT（附 P2×3 · P3×3；无 P1 ⇒ 不构成 `changes_required`）**

> ⚠️ **编号对照**：派单以 `P3-1/P3-2/P3-3` 指称的三条，复审报告原文编号为 **`P3-4`/`P3-5`/`P3-6`**（一一对应）。本落定**以报告原文编号为准**，同时保留 `dispatch_id`，**内容逐字取自报告、未弱化**。

---

## 4. `reviewer_resolved_items`（复审已下的裁定，逐字）

```json
[
  {
    "item": 1,
    "topic": "⭐ 严格读法之争裁定 = 采实现者运行读法（STOP_CALIBRATION 未触发）",
    "source_section": "reviewer_report.md §0（L14）+ §2（L34–L47）",
    "ruling_headline_verbatim": "- **严格读法之争裁定：STOP_CALIBRATION 未触发**（裁定与逐字依据见 §2 —— 这是本复审的职权裁定，不再上抛 owner）",
    "ruling_verbatim": "**裁定**：卡文 L20 严格读法下，本卡 **14 个 proposed 槽位与 7 条 EA 均**不触发 STOP_CALIBRATION；`revert_or_stop.json` 的 `stop_calibration_evaluation.triggered=false` **成立**，4 个 declined 槽位不构成触发。",
    "consequence_verbatim": "**后果核**：4 个 declined 槽位的 fail-closed 处置（不出数、不放行、`blocked_by` 保留 OPEN-2/OPEN-3）与 STOP 想要的实际效果（无来源幅度不得进入任何下游）**完全一致**；采严格读法只会把一份零放行的诚实交付改判 blocked，不增加任何保护。故不触发。",
    "template_gap_note_verbatim": "**⚠️ 复审另发现的模板性缺口（不改判、但落定前必修 → P2-2）**：oracle §5 冻结的 EA 模板含 8 字段，其自设失败条款为「缺任一字段 ⇒ 该条不成立 ⇒ 对应参数触发 STOP_CALIBRATION」。实测 **7 条 EA 逐条均缺 `carrier_form` 字段**（文件顶层有、逐条无，7/7）。该失败条款是**实现者自设的模板纪律**而非卡文 L20 本身：carrier_form 是常量串、信息零损失、卡文 L20 的两个要件（明确假设+区间）逐条满足，故不据此判 STOP；但按其自设条款的字面，该缺口一旦成立即波及全部 EA —— 必须在落定前补齐（见 P2-2）。",
    "basis_count": 4,
    "basis_labels": [
      "L20 是合取命题",
      "卡文 L13（动作①）正向指令",
      "owner §三十四 是更高位的现行授权",
      "merge_ruling §3.2 四类合法基础"
    ],
    "basis_verbatim": [
      "1. **L20 是合取命题**：「幅度**无来源又**未明确分析师假设→STOP_CALIBRATION」——触发主语是**一个幅度**，且须同时满足 (a) 无来源 (b) 未被明确标注为分析师假设。4 个 declined 槽位（ZIJIN_MINERAL_COPPER/GOLD_REALIZED_UNIT_REVENUE_FY2027、MSFT_MICROSOFT_CLOUD、MSFT_LICENSING_VS_CLOUD）**根本未产出任何幅度**（`new_value` 全 null，本工位逐槽验证 §4）：无\"幅度\"存在，条件 (a) 的主语不存在；且 EA-7 本身就是**明示的分析师立场声明**（\"显式拒绝出数、不作任何幅度假设\"），即便把\"假想幅度\"当主语，(b) 也已满足。把合取降格为\"存在无来源槽位即停\"，字面上删去了「又未明确分析师假设」半个条件。",
      "2. **卡文 L13（动作①）正向指令**：「按contract arithmetic、历史经验或外部可比选择校准方法……**缺数据就标expert_assumption**」——卡文自身设计就是\"缺数据→标注假设→继续校准\"。若\"槽位无来源\"本身触发整卡 STOP，动作①的这句指令将永远不可用，属目的性废文。",
      "3. **owner §三十四 是更高位的现行授权**：L751 选项 A 明文「以 5✅+2❌ 现状开 I-11-B，C3/C5 残余列开工后并行欠账」；L758 明文残余「以 expert_assumption 或 unverified 形式登记（不隐藏）」。严格读法会在 owner 作出决定的同一时刻使其落空（C3/C5 残余必然伴随至少 4 个无基期槽位）——`revert_or_stop.json` 自己也登记了这一后果。L775 明文「本节是 owner 的明文改判，优先级高于该自述」。",
      "4. **merge_ruling §3.2（ACCT L226 框架）四类合法基础**：「数值有可核基础（四类之一：来源披露容差 / 同口径历史离散可复算 / 准则监管明文 / **明示 expert_assumption+敏感性区间**）」——权威框架本身把\"明示假设+区间\"认可为与\"有来源\"并列的合法基础，即 **「有来源 **或** 明示假设」的运行读法就是审定框架的读法**。本卡 14 个出数槽位全部满足\"基期有来源（contract arithmetic/历史关系，回源见 §3-②）+ 幅度带明示假设（EA-1/3/4/5，`equivalent_to_disclosure_basis=false` 常量 ✓）\"。"
    ],
    "review_results_count": 6,
    "review_results": [
      {
        "id": "R1",
        "topic": "方法可回源",
        "source_section": "reviewer_report.md §3-①（L53）",
        "result_verbatim": "### ① 方法选择依据是否可回源 — **PASS**"
      },
      {
        "id": "R2",
        "topic": "18 槽位重算一致且 store 全 null",
        "source_section": "reviewer_report.md §3-②（L58）",
        "result_verbatim": "### ② 18 槽位逐一核 — **PASS（14 出数全部复算一致 + 4 显式拒绝全部真 null；1 项基期可复算性缺陷 → P2-1）**"
      },
      {
        "id": "R3",
        "topic": "dependency_control 抽验 E1+E4 真无双通道",
        "source_section": "reviewer_report.md §3-③（L86）",
        "result_verbatim": "### ③ dependency_control 无双通道重复计权 — **PASS（7 共享驱动 + 7 事件逐条在案；抽 2 条自验）**"
      },
      {
        "id": "R4",
        "topic": "手算全重算仅金锭誊算错",
        "source_section": "reviewer_report.md §3-④（L92）",
        "result_verbatim": "### ④ 手算复核 — **PASS（本工位全部独立重算，5+4+3 全对；1 处线级誊算差错 → P3-4）**"
      },
      {
        "id": "R5",
        "topic": "7 条 EA 区间齐",
        "source_section": "reviewer_report.md §5（L124）",
        "result_verbatim": "- **敏感区间 + eqt=false：7/7 齐备**（校验器 I1 绿灯 + M1/M2 红灯双证）✓"
      },
      {
        "id": "R6",
        "topic": "残余 9 项全 open-form",
        "source_section": "reviewer_report.md §6（L143）",
        "result_verbatim": "- **红线核**：9 项无一写成\"已解\"（校验器 I5 绿灯 + M5 红灯[登记→resolved 即 rc=1]双证）；expert_assumption 只承接校准幅度判断、未冲销任何 BLOCKED ✓"
      }
    ],
    "landing_state": "reviewer 已裁定并复核（本落定只转录，不新增裁决、不改判）"
  }
]
```

---

## 5. `unverified`（复审 §10 逐条）

```json
{
  "source": "reviewer_report.md §10（L185–L187）",
  "verbatim": "卡内 9 项残余（C3-①…⑤、C5-①…④，全 open-form，§6）+ 派单差异 2 项（unverified-D1、unverified-C3b）+ 本复审新增 3 项（**unverified-N2**：H-02 转换公式自相矛盾/基期不可复算[P2-1]；**unverified-N3**：EA 模板 carrier_form 缺失[P2-2]；**unverified-N4**：C3-④ IND-r2 已 RULED 的登记更新[P2-3]）+ 数值小注 2 项（P3-4/P3-5）。",
  "count": 16,
  "decomposition": "卡内残余 9（C3-①…⑤、C5-①…④）+ 派单差异 2（unverified-D1、unverified-C3b）+ 复审新增 3（unverified-N2/N3/N4）+ 数值小注 2（P3-4/P3-5）= 16；全部保持 open-form，无一写作已解",
  "items": [
    "C3-①｜origin 字节｜unverified｜62,953B 已落（origin_bytes.bin sha cf84c29048ab314e…）；但 E1 等级=BLOCKED-PARTIAL，字节层 ✅ ≠ E1 解锁",
    "C3-②｜B2 晋升｜verified_by_parent｜父对账：晋升已完成（dayu sec_downloader.py=74,543B/4684933e…、cw dayu_cli_adapter.py=25,328B/32ef1165…，Copy-Item 单步覆盖，committed=false）；B2-PROMOTION handoff 的 MISSING 为事故时点旧值；本工位无产品仓读面，状态为父证",
    "C3-③｜ACCT-R2 定级｜unverified｜RULED 但 e1_level=BLOCKED-PARTIAL、s_level=S1、4 份语料降 E3（8 条引文作废）；'已裁定'≠'通过'，等级即 fail-closed 结果",
    "C3-④｜IND-r2｜unverified｜在跑未归（OPEN-3-IND-R2/a20260926-01 目录空）",
    "C3-⑤｜MSFT 六参数/新两分部参数/HK 参数｜unverified｜维持不放行（OPEN-3/OPEN-5）；MSFT_MICROSOFT_CLOUD、MSFT_LICENSING_VS_CLOUD 本卡显式拒绝出数（EA-7）",
    "C5-①｜6c threshold_review_status 落地｜unverified｜accepted_scoped 带 2×P2+3×P3，非 clean accept",
    "C5-②｜H4 口径桥｜unverified｜残差 269 吨（铜）/534 千克（金）未逐行闭合，金在内/外档翻转 ⇒ 冻结判据 Q2 fail-closed；countersigned=false；会签前不得升 reviewed、不得触发任何动作",
    "C5-③｜6b 恒等式容差｜unverified｜路径(c) 已按 revert_rule 退 unquantified；R2（金 154 千克）NOT_SIGNED；整条 BLOCKED-6b 状态归 ruling_6b L110：须新建 OPEN6B-TOLERANCE-RULING-R2 后由 owner/编排层重判",
    "C5-④｜H2 基准｜unverified｜交付但 still_blocked；3 条 pjr 完成 A-6.3 全套 = 0/3",
    "unverified-D1｜erratum_recorded｜派单称 I-11-A 卡级最新=a20260922-02 —— 不存在；父勘误：I-11-A 唯一 attempt=a20260919-01/accepted_scoped（父误记 I-06-A 的卡级最新）",
    "unverified-C3b｜verified_by_parent｜派单 C3-② ✅ vs B2-PROMOTION handoff blocked —— 父对账后改记：晋升已完成，handoff 为事故时点旧值",
    "unverified-N2｜open｜- **P2-1** `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 基期可复算性缺陷：store L175 转换公式自相矛盾（`884,943+83,161×24=2,880,807` ≠ `885,141`；真值 38,175.95 vs 沿用值 124,248.63，差 3.25×；自洽基下两点差分应为 ≈−1,071 而非 −10,670.89）。处置：在卡内补登 unverified 项（store 先天缺陷+本卡沿用未标）；**OPEN-2 裁定前任何下游不得消费 124,248.63 及其 ±5% 带**；建议同时提示编排层在 OPEN-2 裁定时先修 store 口径桥。",
    "unverified-N3｜open｜- **P2-2** EA 模板 8 字段缺口：7/7 条缺逐条 `carrier_form`（oracle §5 自设失败条款字面即触发\"不成立\"）。处置：7 行常量补齐 + 校验器 I1 扩至 8 字段 + 新增 M6 变异（删 carrier_form 必红）重跑红绿。",
    "unverified-N4｜open｜- **P2-3** C3-④ 事实过时：「IND-r2 在跑（目录空）」在 handoff 交付时点（17:44:22）已不成立（IND-r2 17:34-17:38 已 RULED：segment_set_ok=yes content-layer+bridge caveat、S1 会签、E1 仍 BLOCKED-PARTIAL、零放行）。处置：更新登记详情（登记形态 unverified 不变）；确认 IND-r2 不改变本卡任一 blocked_by（本工位已核：不改变）。",
    "P3-4（复审 §10 数值小注 1）｜open｜- **P3-4** 金锭线 spot-check 誊算：39,757,982,580 应为 39,758,282,580（差 300,000）；真实线残差 +302,580（0.0007611%），结论不变。",
    "P3-5（复审 §10 数值小注 2）｜open｜- **P3-5** EA-4 注解内联合收入带 [320,763, 348,432] 不可复现（应为 [375,283, 414,787]；g 运行值本身全对）。"
  ]
}
```

---

## 6. ⭐ 严格读法之争 —— 复审裁定：**不触发 `STOP_CALIBRATION`**（采实现者运行读法，逐字转录）

**裁定标题（L14 逐字）**

> - **严格读法之争裁定：STOP_CALIBRATION 未触发**（裁定与逐字依据见 §2 —— 这是本复审的职权裁定，不再上抛 owner）

**裁定正文（L36 逐字）**

> **裁定**：卡文 L20 严格读法下，本卡 **14 个 proposed 槽位与 7 条 EA 均**不触发 STOP_CALIBRATION；`revert_or_stop.json` 的 `stop_calibration_evaluation.triggered=false` **成立**，4 个 declined 槽位不构成触发。

**四条逐字依据（L40–L43）**

> 1. **L20 是合取命题**：「幅度**无来源又**未明确分析师假设→STOP_CALIBRATION」——触发主语是**一个幅度**，且须同时满足 (a) 无来源 (b) 未被明确标注为分析师假设。4 个 declined 槽位（ZIJIN_MINERAL_COPPER/GOLD_REALIZED_UNIT_REVENUE_FY2027、MSFT_MICROSOFT_CLOUD、MSFT_LICENSING_VS_CLOUD）**根本未产出任何幅度**（`new_value` 全 null，本工位逐槽验证 §4）：无"幅度"存在，条件 (a) 的主语不存在；且 EA-7 本身就是**明示的分析师立场声明**（"显式拒绝出数、不作任何幅度假设"），即便把"假想幅度"当主语，(b) 也已满足。把合取降格为"存在无来源槽位即停"，字面上删去了「又未明确分析师假设」半个条件。
>
> 2. **卡文 L13（动作①）正向指令**：「按contract arithmetic、历史经验或外部可比选择校准方法……**缺数据就标expert_assumption**」——卡文自身设计就是"缺数据→标注假设→继续校准"。若"槽位无来源"本身触发整卡 STOP，动作①的这句指令将永远不可用，属目的性废文。
>
> 3. **owner §三十四 是更高位的现行授权**：L751 选项 A 明文「以 5✅+2❌ 现状开 I-11-B，C3/C5 残余列开工后并行欠账」；L758 明文残余「以 expert_assumption 或 unverified 形式登记（不隐藏）」。严格读法会在 owner 作出决定的同一时刻使其落空（C3/C5 残余必然伴随至少 4 个无基期槽位）——`revert_or_stop.json` 自己也登记了这一后果。L775 明文「本节是 owner 的明文改判，优先级高于该自述」。
>
> 4. **merge_ruling §3.2（ACCT L226 框架）四类合法基础**：「数值有可核基础（四类之一：来源披露容差 / 同口径历史离散可复算 / 准则监管明文 / **明示 expert_assumption+敏感性区间**）」——权威框架本身把"明示假设+区间"认可为与"有来源"并列的合法基础，即 **「有来源 **或** 明示假设」的运行读法就是审定框架的读法**。本卡 14 个出数槽位全部满足"基期有来源（contract arithmetic/历史关系，回源见 §3-②）+ 幅度带明示假设（EA-1/3/4/5，`equivalent_to_disclosure_basis=false` 常量 ✓）"。

**后果核（L45 逐字）**

> **后果核**：4 个 declined 槽位的 fail-closed 处置（不出数、不放行、`blocked_by` 保留 OPEN-2/OPEN-3）与 STOP 想要的实际效果（无来源幅度不得进入任何下游）**完全一致**；采严格读法只会把一份零放行的诚实交付改判 blocked，不增加任何保护。故不触发。

**模板性缺口说明（L47 逐字，对应 P2-2）**

> **⚠️ 复审另发现的模板性缺口（不改判、但落定前必修 → P2-2）**：oracle §5 冻结的 EA 模板含 8 字段，其自设失败条款为「缺任一字段 ⇒ 该条不成立 ⇒ 对应参数触发 STOP_CALIBRATION」。实测 **7 条 EA 逐条均缺 `carrier_form` 字段**（文件顶层有、逐条无，7/7）。该失败条款是**实现者自设的模板纪律**而非卡文 L20 本身：carrier_form 是常量串、信息零损失、卡文 L20 的两个要件（明确假设+区间）逐条满足，故不据此判 STOP；但按其自设条款的字面，该缺口一旦成立即波及全部 EA —— 必须在落定前补齐（见 P2-2）。

**六项复核结果（逐字）**

> ### ① 方法选择依据是否可回源 — **PASS**
>
> ### ② 18 槽位逐一核 — **PASS（14 出数全部复算一致 + 4 显式拒绝全部真 null；1 项基期可复算性缺陷 → P2-1）**
>
> ### ③ dependency_control 无双通道重复计权 — **PASS（7 共享驱动 + 7 事件逐条在案；抽 2 条自验）**
>
> ### ④ 手算复核 — **PASS（本工位全部独立重算，5+4+3 全对；1 处线级誊算差错 → P3-4）**
>
> - **敏感区间 + eqt=false：7/7 齐备**（校验器 I1 绿灯 + M1/M2 红灯双证）✓
>
> - **红线核**：9 项无一写成"已解"（校验器 I5 绿灯 + M5 红灯[登记→resolved 即 rc=1]双证）；expert_assumption 只承接校准幅度判断、未冲销任何 BLOCKED ✓

---

## 7. `qualification.json` 摘要

| 字段 | 值 |
|---|---|
| 路径 | `evidence/I-11-B/qualification.json`（目录与文件均新建） |
| `formula` | `not_applicable_with_reason`（理由写在 `formula_reason`：纯簿记落定，不产生任何公式/预测结果） |
| `disclosure_adaptation` | `unmapped`（**未触碰**） |
| `accuracy` | `unproven`（**未触碰**） |
| `granted_scope` | **仅**本卡校准计划/映射产出的证据与判据（calibration_plan · expert_assumptions · synthetic_mechanism_check · revert_or_stop · verify_plan + `_mut/` · oracle 判据 · dependency_control · 复审 ACCEPT 本身 · ⭐严格读法裁定） |
| `not_granted` | **`OPEN-2` 前禁消费 `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 的 `base`（124,248.63 及其 ±5% 带，P2-1 矛盾未补登前）** · 参数放行（`low/base/high` 仍 `null`、`_PLACEHOLDER` 维持）· `threshold_review_status` 升级 · 解除任何 `OPEN/BLOCKED` · `proposed_not_released` 视为已发布 · 晋升 · 代签 · 产品仓任何字节 · 五份计划文件 · clean accept · 派 `I-11-C` |
| `status_authority` / `carried_findings` | 与本文件 §2/§3、`handoff.json` **逐字段相等**（镜像） |

---

## 8. 写入面、只读自证与边界

**本 pass 写入面 = 恰三处**：

1. `handoff.json`（状态面转录：`status`/`status_before`/`status_transition`/`status_scope`/`status_history`/`status_authority`/`carried_findings`/`reviewer_resolved_items`/`unverified`/`pre_image`/`verdict_is_transcribed_not_authored`）
2. `review.md`（本文件，新建；落定前 `Test-Path` = `False`）
3. `evidence/I-11-B/qualification.json`（新建目录 + 新建文件）

**本 attempt 既有产物复哈希（全部 `UNCHANGED`）**：

| 对象 | 字节 | sha256（前 16） | 判 |
|---|---|---|---|
| `oracle.md` | 17,723 | `80a2cda0601fcec5` | UNCHANGED |
| `calibration_plan.json` | 32,665 | `e86b41355c1ba7c5` | UNCHANGED |
| `expert_assumptions.json` | 8,580 | `9f8b844e342ec17e` | UNCHANGED |
| `synthetic_mechanism_check.json` | 8,035 | `89f4bafda23d520c` | UNCHANGED |
| `revert_or_stop.json` | 4,367 | `9d5e05f1ac3748aa` | UNCHANGED |
| `verify_plan.py` | 4,495 | `73f632fd976a0cfd` | UNCHANGED |
| `_mut\m1_eas.json` | 7,616 | `efe3f0a5cab90033` | UNCHANGED |
| `_mut\m2_eas.json` | 8,180 | `4692d11b183705c9` | UNCHANGED |
| `_mut\m3_handoff.json` | 10,901 | `6e4f0f06fddb619d` | UNCHANGED |
| `_mut\m4_store.json` | 61,200 | `0a9ca72765ab893e` | UNCHANGED |
| `_mut\m5_handoff.json` | 10,886 | `2b2635e3620e0d17` | UNCHANGED |
| `reviewer_report.md` | 28,698 | `5af4987ee0547a53` | UNCHANGED |
| `reviewer_report.sha256` | 84 | `4f83905ab386ec06` | UNCHANGED |
| 五份计划文件 | — | — | **本工位 0 次写入**（基线与收尾哈希见 `qualification.json.bookkeeping.five_plan_files_reattempt`） |

**git（只读）**：`git -c core.quotepath=false diff HEAD --name-only` → 总数 **3830**、**非 `.planning` = 0**；**未用 `git status`**、**无 git 写**、**未联网**、**未跑任何测试**。

**本落定没有做的事**：

- **没有**写 `reviewer_report.md` / `reviewer_report.sha256`（各 0 字节），**没有**写本 attempt 任何其他既有字节（复哈希 13/13 `UNCHANGED`）；
- **没有**解除任何 `OPEN-2/3/5/6/12` 或任何 `BLOCKED-*`；
- **没有**放行任何参数（`low/base/high` 仍 `null`、两个 `_PLACEHOLDER` 维持）、**没有**把 `proposed_not_released` 当已发布；
- **没有**升 `threshold_review_status`、**没有**改 `threshold_basis` 或任何阈值值；
- **没有**销掉 P2-1/P2-2/P2-3 与 P3-4/P3-5/P3-6 任何一条（6 条全部 `carried`）；
- **没有**产生新裁决、**没有**代签：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`；
- **没有**改五份计划文件、**没有**写 `.planning` 之外任何字节、**没有** git 写、**没有**跑 `git status`、**没有**联网；
- **没有**派 `I-11-C`、**没有**晋升、**没有**触任何 falsifier / 自动动作。

---

*由 carrier-landing bookkeeping executor（父派委派的簿记落定子代理）创建于 2026-09-26；本文件只转录，不新增任何接受。*
