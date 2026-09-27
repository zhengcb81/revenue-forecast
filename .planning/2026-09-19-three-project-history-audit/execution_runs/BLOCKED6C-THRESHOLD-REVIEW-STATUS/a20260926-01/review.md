# 载体落定 review — `BLOCKED6C-THRESHOLD-REVIEW-STATUS / a20260926-01`

> **Test-Path 断言（本文件新建前实测，逐字记录）**：`Test-Path .\review.md` → **`False`** ｜ `Test-Path .\evidence` → **`False`**
> ⇒ 本 attempt 内原先**不存在** `review.md`（无实现者存根需保留）⇒ **新建**；`evidence/` 目录一并新建
> （`Test-Path .\evidence\BLOCKED6C-THRESHOLD-REVIEW-STATUS\qualification.json` → **`False`**，已同时断言）。
>
> **落定性质**：簿记转录（transcription only）。本文件只把独立复审**已经写下**的裁决搬进卡载体，
> **不产生新裁决、不自签、不解除任何 `BLOCKED-*` / `OPEN-6`、不放行任何参数、不改 `threshold_basis` 或任何阈值值、
> 不产生 `I-11-B` / `I-11-C` 的 ACCEPT、不晋升、不写产品仓任何字节、不写五份计划文件。**
> 裁决字节非本工位产生：裁决只存在于 `reviewer_report.md`（本 pass 对该文件与侧车写入 **0** 字节）。

---

## 0. 裁决行定位（本落定工位**自行定位**，未采信派单给定的行号/字节区）

对 `reviewer_report.md` 原始字节独立读取 → UTF-8 解码 → 按 `LF` 切行 → 子串索引 → 回算 0-based 字节前缀和：

| 项 | 本工位实测 |
|---|---|
| carrier | `reviewer_report.md` |
| 字节 | **33,083** |
| sha256（自算） | `442577484e7b32bd1af18df872568afa1f645a46f335159e843523a4db9a3ff9` |
| 编码 | UTF-8 **无 BOM**（BOM=False）· **仅 LF**（CR=0，LF=375）· 375 行 |
| 裁决行行号 | **L3**（1-based），全文唯一独立成行的 `VERDICT: ACCEPT` |
| 裁决行文本（逐字） | `VERDICT: ACCEPT` |
| 裁决行字节区 | **`start=77` / `end_inclusive=91` / `end_exclusive=92` / `length=15`**（0-based，区域不含行尾 LF） |
| 该 15 字节 sha256 | `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |
| 计数行 | L286，字节区 `[25114, 25167)`，sha256 `ad6a0d132e20e1ae77679464f169ab48eb8dcaaca2d3b9a63e61034054956d7c` |
| 三方 sha 一致核对 | 自算 `442577484e7b32bd…` == 侧车 `reviewer_report.sha256` 内容 == 派单给定 `442577484e7b32bd…` ⇒ **一致（true）** |

> `VERDICT` 全文出现 3 次、`ACCEPT` 出现 6 次，其余均在正文内被引用；**独立成行且唯一承载裁决词的行 = L3**。

---

## 1. 状态面转录

| 字段 | 值 |
|---|---|
| `status` | `review_pending` → **`accepted_scoped`** |
| `status_before` | `review_pending`（原值逐字） |
| `status_transition` | `review_pending -> accepted_scoped` |
| `status_scope` | **范围严格限于 iso 改动 + `changes.diff` 的证据与判据**（非 clean accept：带 2×P2 + 3×P3） |
| `status_history` | 2 条：① `review_pending`（实现者工位，2026-09-26T08:50:44Z）② `accepted_scoped`（本簿记落定工位，转录复审 L3 裁决） |
| `implementer_signed` | `false`（**未改**） |
| `verdict_is_transcribed_not_authored` | `true` |
| `pre_image`（handoff，改前自算） | 30,842 B / `88c39b95e0afa99f68f50ca7108cfe5774b8160e11cf5c7860299f38c67785a0` |
| `post_image`（handoff，改后自算） | 48,744 B / `9cca874fb8ab743a8f810524a4a941bd65c9128ca086c9983100511af661e5e0` |

---

## 2. `status_authority`（**镜像 1/2**，与 `handoff.json.status_authority`、`qualification.json.status_authority` 逐字段相等）

```json
{
  "carrier": "reviewer_report.md",
  "carrier_path_inside_attempt": "reviewer_report.md",
  "carrier_bytes": 33083,
  "carrier_sha256": "442577484e7b32bd1af18df872568afa1f645a46f335159e843523a4db9a3ff9",
  "carrier_sha256_prefix16": "442577484e7b32bd",
  "carrier_total_lines": 375,
  "carrier_encoding": "UTF-8 无 BOM（BOM=False）；仅 LF 行尾（CR=0，LF=375）",
  "carrier_encoding_flags": {
    "bom": false,
    "cr_count": 0,
    "lf_count": 375,
    "utf8_valid": true
  },
  "three_way_consistency": "落定工位自算 sha256 == reviewer_report.sha256 侧车内容 == 派单给定 442577484e7b32bd…，三方一致",
  "three_way_match": true,
  "verdict_word_written_by_reviewer": "ACCEPT",
  "verdict_line_text_as_written_by_reviewer": "VERDICT: ACCEPT",
  "verdict_line": 3,
  "verdict_line_range_inclusive_1_based": [
    3,
    3
  ],
  "verdict_line_byte_region": {
    "start": 77,
    "end_inclusive": 91,
    "end_exclusive": 92,
    "length": 15,
    "sha256": "f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7",
    "decoded_utf8": "VERDICT: ACCEPT"
  },
  "verdict_line_located_by": "本落定工位自行定位（读原始字节 → UTF-8 解码 → 按 LF 切行 → 子串索引 → 回算 0-based 字节前缀和）；行号与字节区均为自算，未采信派单文本",
  "verdict_line_unique": true,
  "verdict_line_other_occurrences_note": "全文 `VERDICT` 出现 3 次、`ACCEPT` 出现 6 次，均在正文内被引用；独立成行且唯一承载裁决词的行 = L3",
  "count_line": 286,
  "count_line_text": "**P1 = 0 ⇒ `VERDICT: ACCEPT`（可带 P2/P3）。**",
  "count_line_byte_region": {
    "start": 25114,
    "end_inclusive": 25166,
    "length": 53,
    "sha256": "ad6a0d132e20e1ae77679464f169ab48eb8dcaaca2d3b9a63e61034054956d7c"
  },
  "verdict_written_by": "独立复审工位（reviewer_report.md 的作者；与实现者非同一人；实现者未自签）",
  "verdict_is_transcribed_not_authored": true,
  "implementer_signed": false,
  "transcribed_by": "carrier-landing bookkeeping executor（父派委派的簿记落定子代理）—— 只做簿记转录，不产生新裁决、不自签",
  "scope": "accepted_scoped —— 接受范围**严格限于 iso 改动 + changes.diff** 的证据与判据；非 clean accept（带 2×P2 + 3×P3）",
  "pin_sidecar": {
    "file": "reviewer_report.sha256",
    "present": true,
    "bytes": 85,
    "sha256": "c3349767b342b580d9585e91802083f5992bb80d6eaf20c14f1a08071fa8e042",
    "content": "442577484e7b32bd1af18df872568afa1f645a46f335159e843523a4db9a3ff9  reviewer_report.md",
    "three_way_match": true,
    "verified": "侧车内容与落定时独立重算的 reviewer_report.md sha256 逐字节相同；本 pass 对侧车写入 0 字节"
  },
  "read_only_by_this_pass": "本落定工位对 reviewer_report.md 与 reviewer_report.sha256 的写入字节数 = 0",
  "unverified_source": "reviewer_report.md §7（L323–L340）9 条逐字转录进 handoff.unverified；实现者原 9 条逐字保存在 evidence/BLOCKED6C-THRESHOLD-REVIEW-STATUS/qualification.json 的 unverified_implementer_pre_review，披露不丢失",
  "landing_file": {
    "file": "review.md",
    "pre_image": "落定前 Test-Path 断言 = False（本 attempt 内原先不存在 review.md，无实现者存根需保留）⇒ 新建"
  },
  "section_line_ranges_inclusive_1_based": {
    "verdict_line": [
      3,
      3
    ],
    "count_line": [
      286,
      286
    ],
    "dual_reading_ruling_and_L271_section": [
      198,
      250
    ],
    "L17_section": [
      254,
      266
    ],
    "not_recommended_section": [
      270,
      280
    ],
    "findings_P1_P2_P3": [
      284,
      319
    ],
    "unverified_section": [
      323,
      340
    ]
  }
}
```

---

## 3. `carried_findings`（**镜像 1/2**；复审 §6 的 5 条**逐字**，不弱化、不改级、不销项）

```json
[
  {
    "level": "P2",
    "id": "P2-1",
    "source_section": "reviewer_report.md §6（L290–L298）",
    "finding_verbatim": "- **P2-1｜冻结手算 `24` vs 实测 `28` 未记 `erratum`，且 `handoff` 声称「全部匹配」。**\n  `oracle §6.3` 的 T3 括注逐字「*手算预期*：2、1 ⇒ 不命中（**U-LITERAL：24、5** ⇒ 命中）」，\n  而 `U_newly_literal` 实测 = **28**（记录级）/ 5（去重级）。`24` 恰等于 §6.2 自己的「24 条 arithmetic」，\n  漏算了 4 条 `disclosure_definition` ⇒ **属 oracle 内部算术笔误**（§6.2 的 `A-6.2 判可用 = 28` 本身是对的、我实测也是 28）。\n  `oracle §6.2/§9` 规定「实测与本表不符 ⇒ 按 `erratum-*` 记录，不回改本表」，\n  而 `handoff.L271.matches_oracle_frozen_hand_calculation = true`、step 2 detail 更写\n  「**no erratum needed because every measured number matched the frozen hand calculation**」—— **该句对 24/28 这一点不成立**。\n  **影响**：`28 ≥ 14` 与 `24 ≥ 14` 同为命中，**T3-literal 结论、U-PRIMARY 全部数字、最终 verdict 均不受影响**；\n  纯属**披露/计数纪律**问题 ⇒ **P2，不升 P1**。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P2",
    "id": "P2-2",
    "source_section": "reviewer_report.md §6（L299–L305）",
    "finding_verbatim": "- **P2-2｜同一份机器报告里并存两条互相矛盾的读法，且未标注哪条对 `usable` 生效。**\n  `green/validation_report.json` 的 `threshold_reviewability.rule` 写 U-PRIMARY（`not_reviewed` 的 arithmetic/disclosure **usable=true**），\n  而紧邻的 `threshold_review_status_schema.fail_closed` 逐字写\n  「`threshold_review_status` absent **or not_reviewed** ⇒ **the threshold does not participate in any judgement**」（= 字面 A-6.1）。\n  对同 26 条记录，一个说「可用」、一个说「不参与任何判定」，**下游 I-11-B「阈值门」/ I-11-C 无法从报告本身判断以谁为准**。\n  **方向是 fail-safe 的**（字面串只会导致更保守），且本复审已在 §3 裁定 U-PRIMARY 生效 ⇒ **P2 不升 P1**；\n  建议补一行 `reading: \"U-PRIMARY governs usable; the fail_closed string is the verbatim A-6.1 item-1 source text (literal reading, counterfactual)\"`。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P3",
    "id": "P3-1",
    "source_section": "reviewer_report.md §6（L309–L310）",
    "finding_verbatim": "- **P3-1｜补丁内引用路径笔误**：`changes.diff` L24（= `iso_patched` 内 `B6C-SCHEMA` 注释）写\n  `ruling execution_runs/I11A-OPEN-ACCT/a20260924-01.md L226`，正确应为 `.../a20260924-01/ruling.md`。仅注释，不影响判定。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P3",
    "id": "P3-2",
    "source_section": "reviewer_report.md §6（L311–L312）",
    "finding_verbatim": "- **P3-2｜报告键名与冻结措辞有出入**：`oracle §3.1` 冻结「报告写 `defaulted=true` + **`carried=false`**」；\n  实现落的是 `defaulted` + **`threshold_review_status_present`**（语义等价，但无字面 `carried` 键）。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  },
  {
    "level": "P3",
    "id": "P3-3",
    "source_section": "reviewer_report.md §6（L313–L315）",
    "finding_verbatim": "- **P3-3｜M4/M5 是「判定级」而非「整标记块级」变异**（保留共享 `_trs_*` 赋值以免 `NameError`）——\n  实现者已在 `handoff.unverified` 第 3 条与 `make_mutants.py` 内如实披露；我复核其源码后认为**该保留在方法上正当**\n  （删整块会崩溃、不构成判别力证据），**不扣分**，仅登记。",
    "landing_state": "carried（未销项；本落定只转录，不改级、不处置、不销项）"
  }
]
```

计数：**P1 = 0 · P2 = 2 · P3 = 3 · 合计 5**；计数行逐字（reviewer_report.md L286）：

> **P1 = 0 ⇒ `VERDICT: ACCEPT`（可带 P2/P3）。**

---

## 4. `reviewer_resolved_items`（复审已下的四条裁定，逐字）

```json
[
  {
    "item": 1,
    "topic": "⭐ 双读法裁定 = 采 `U-PRIMARY`（主读法）",
    "source_section": "reviewer_report.md §3.1–§3.2（L198–L228）",
    "ruling_verbatim": "> **我裁定采用 `U-PRIMARY`（oracle §3.3 冻结的主读法）作为判定本卡 J4 / `L271` 触发线的唯一读法。**\n> 依据 U-PRIMARY：`T1/T2/T3` **全部不命中** ⇒ `trigger_fired = false` ⇒ **fail-closed 第 1 条未触发 ⇒ 不判 `blocked`**。\n> `U-LITERAL` 的量化（40/40、8/8、三线全中）**照实保留**为反事实披露，**不作判据**。\n> **若采字面读法 ⇒ 三线全中 ⇒ 按本卡冻结的 `J4` 应判 `blocked`。** 故本裁定是决定性的，我明确落笔、不回避。",
    "basis_count": 4,
    "basis_labels": [
      "L226 禁令自带范围",
      "A-6.1 小节标题是「占位阈值」使用禁令",
      "字面读法会让 A-6.2 成死条文",
      "L271 自己把「实施方式」与「实质」切开"
    ],
    "basis_verbatim": [
      "**正证 1 —— 裁定主体的禁令子句自带范围。** ruling **L226** 是 OPEN-6 的「裁定（一句话）」，其禁令原文是\n「`threshold_basis=professional_judgement_required` **且** `threshold_review_status≠reviewed` 的阈值**不得触发任何自动动作**」。\n字面读法把范围词 `professional_judgement_required` 删掉，等于**改写了裁定主体的量词**。",
      "**正证 2 —— A-6.1 的小节标题即范围。** L228 逐字「裁定 A-6.1：**占位阈值**在审定前的使用禁令」；\n`decision.md DEC-6` L156–157 把**占位阈值**定义为 `threshold_basis = \"professional_judgement_required\"` 的那一类。\nA-6.1 第 1 条是**该小节下的第 1 条**，其「二者缺一或 `not_reviewed` ⇒ fail-closed」按标题与 DEC-6 只辖占位阈值。",
      "**正证 3 —— 字面读法会让同一条裁定的 A-6.2 成为死条文。** L236–L242 的 A-6.2 表有一列**列名就叫「审定前可否使用」**，\n逐字给 `arithmetic_identity = 可用（等式判定）`、`disclosure_definition = 可用（是/否型判定）`、\n`professional_judgement_required = 不可用`。\n而**盘上 40 条记录 0 条携带该字段**（我已实测）⇒ 全部落默认 `not_reviewed` ⇒ 字面读法下 **40/40 全不可用**，\nA-6.2 那两行「可用」**永远不可能成立**、`DEC-6` 的「两类阈值」之分也随之塌缩。\n**一条裁定不会在同一节里既说「审定前可用」又说「只要没审定就一律不可用」** ⇒ 字面读法与 A-6.2 冲突，须让位于明确列举的表格。",
      "**正证 4 —— L271 自己把「实质」与「实施方式」切开了。** L271 逐字：「⇒ A-6.1 的**实施方式**（追加字段 + 默认 `not_reviewed`）\n**需按实际情况重议**，但**『未审定不得当已审定』这一实质不因此改变**。」\n即：**大批判不可用 ⇒ 触发的是「重议实施方式」这个 owner 动作，不是「实现者的实现错了」**。\n字面读法**恰恰会让该反例在字段落地的第一天就必然成立**（40/40 ⇒ 三线全中），\n这说明字面读法不是裁定者想要的操作化方式 —— 否则他不会把它写成「什么会推翻本裁定」里的一条。"
    ]
  },
  {
    "item": 2,
    "topic": "⭐ `L271` 段落位置的影响",
    "source_section": "reviewer_report.md §3.2 段落位置证 1/2（L230–L239）",
    "basis_verbatim": [
      "**段落位置证 1 —— L271 在 `#### 反例（什么会推翻本裁定）` 之下（该段首行 = L268，L271 是其第 2 条）。**\n反例段的语义是「**若出现该现象，则本裁定的实施方式需重议**」——它是一个**带后果的触发器**，\n**不是**「落地前必须先满足的前置条件」。登记册 §一四三 B.2 已明确记载父曾把它误读成前置条件并自纠\n（逐字「**把反例当成了前置条件，属误读**」，L3557 再记一次）。**本次复审确认该自纠正确。**",
      "**段落位置证 2 —— 位置差异改变了 `trigger_fired=true` 的读法。**\n若 L271 是前置条件 ⇒ 触发 ⇒ 「实现者不该动手」⇒ 卡本身有问题。\n若 L271 是反例（实际位置）⇒ 触发 ⇒ 「**ruling owner 要重议 A-6.1 的实施方式**」，**实质（未审定不得当已审定）继续有效**，\n实现者**把该触发如实量化并上交裁定**（而不是自行判死或自行放行）**恰恰是正确处置**。\n实现者在 `oracle §3.3` 明写「**此分歧由复审裁定，不由我静默选边**」，并在 `handoff.unverified` 第 2 条再次披露 —— **不静默选边成立**。"
    ],
    "conclusion": "L271 在 `#### 反例（什么会推翻本裁定）`（段首 L268）之下 ⇒ **带后果的触发器，不是前置条件**；复审确认登记册 §143-B.2 的自纠正确；实现者「不静默选边」成立"
  },
  {
    "item": 3,
    "topic": "⭐ 显式反面登记",
    "source_section": "reviewer_report.md §3.1 L205 / §3.3-4 L249–L250 / §5 L270–L280",
    "verbatim_reverse_verdict": "> **若采字面读法 ⇒ 三线全中 ⇒ 按本卡冻结的 `J4` 应判 `blocked`。** 故本裁定是决定性的，我明确落笔、不回避。",
    "verbatim_no_reversal": "**不建议。** 两道 fail-closed 的实测状态：\n\n| fail-closed | 条件（oracle 冻结） | 我的实测 | 后果 |\n|---|---|---|---|\n| 第 1 条 | 任一 `L271` 触发线在 **U-PRIMARY** 下命中 | **T1 不命中 / T2 记录 14<30、去重 4<6 不命中 / T3 记录 2<14、去重 1<2.5 不命中** ⇒ `trigger_fired=false` | **未触发** |\n| 第 2 条 | 原 21 例在**未变异补丁版**上任一回归 | **21/21 仍拒、`accepted_ids=[]`** | **未触发** |\n\n⇒ 按我裁定的 U-PRIMARY，**两道均未触发 ⇒ 不判 `blocked`**，本卡 `status=review_pending` + `implementer_signed=false`\n的交付形态**成立**。（**若采字面读法则必须 `blocked`** —— 见 §3.1/§3.3-4，我已显式登记，不留给下一位猜。）",
    "verbatim_owner_trigger": "4. **若日后 owner 明文采字面读法** ⇒ 按本卡冻结 `J4` 三线全中 ⇒ 本卡应改判 `blocked` 并按 L271 重议实施方式；\n   该情形**由我显式登记在此**，不由实现者承担。"
  },
  {
    "item": 4,
    "topic": "`L17 scope` 裁定 = 不适用（oracle §0.1 明令由复审行使）",
    "source_section": "reviewer_report.md §4（L254–L266）",
    "verbatim_l17_text": "**L17 逐字（我独立回源读到）**：「凡跨项目公共schema、canonical writer、registry或worker API，只有指定owner写；\n发现scope外必要改动先记录阻断并交owner补卡，不能为绿灯建立平行框架。」",
    "verbatim_ruling_and_basis": "**我的裁定：L17 不适用（同意实现者 §0.1 的判断，理由为我自读原文后独立得出）**：\n1. L17 的四类辖域是**跨项目公共**件；被改对象是 `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py`，\n   落在 `.planning` 内、**非产品仓**（`src/`/`scripts/`/产品 `tools/` 计 0 文件，我复核 diff 头与 `git diff` 均一致）；\n2. 该文件目前是 `I-11-A` **自己**的校验器；`I-11-C 是否复用同一校验器` 属 `OPEN-12`（owner 已裁「另立校验器专业卡」），\n   **跨项目复用尚未发生**，故尚不存在「公共 API 由非 owner 改写」的事实；\n3. 本补丁**不建平行框架**：新错误码、新报告块全部进**同一支**校验器与**同一份** `validation_report.json`；\n4. 附**前置提醒（P3 级）**：一旦 `OPEN-12` 卡裁 `I-11-C` 复用本校验器，`B6C-G1..G4` 与三新错误码须按\n   `A-6.3 第 5 条 / DEC-14 L364` 跨卡同步，**那时 L17 才可能被触发**；届时由 schema owner 收口。",
    "carry_forward": "前置提醒（P3 级）：一旦 `OPEN-12` 裁 `I-11-C` 复用本校验器，须按 A-6.3 第 5 条 / DEC-14 L364 跨卡同步，**那时 L17 才可能被触发**；届时由 schema owner 收口"
  }
]
```

---

## 5. `unverified`（复审 §7 的 **9 条逐字**）

```json
[
  "1. **21,908 文件的全盘 JSON 扫描未复跑**（oracle §6.1 冻结时做过）。我只复核了**冻结的 6 份语料**\n   （sha 全等 + 记录数 8/8/8/8/4/4 + 分 basis 24/4/12 + 0 字段携带）。\n   ⇒ 「盘上没有第 7 份阈值记录文件」这一断言**未独立复验**。",
  "2. **`T1` 是「可用阈值探针」，不是真的 I-11-C 启动**：真实 I-11-C 代码是否能开机**未测**（超出本卡范围，实现者已披露）。",
  "3. **`A-6.3` 的四要素是否满足**（观测量可复算 / 可核基础 / 非实现者签署 / 追加式版本化）**与本卡无关、我未审**：\n   `BLOCKED-6a`（3 条判断类阈值数值）、`BLOCKED-6b`（4 条容差）**仍 `still_blocked`**，本报告**不解锁、不代签**。",
  "4. **实现者未跑任何产品仓测试套件 / CI / lint**（超范围，已披露）；我同样未跑 —— 因为本卡**零产品写**。",
  "5. **`red/` 下的日志与报告带 CRLF**（Windows 控制台 / 校验器写出），实现者已披露并将 `green/` 归一为 LF；\n   我核的是**内容全等**而非行尾。",
  "6. **`handoff.continuation.previous_patch_sha_not_recoverable`**（36,030 B 的中间态补丁无 sha 可回填）——\n   属系统事件遗留，**我无法验证也未试图恢复**；本 attempt 的**后像**已由 `1085368e3d05cf9b…` 锁定。",
  "7. **`I-11-C` 是否复用同一校验器** 未裁（`OPEN-12` 另立专业卡，owner 已答「是」）。",
  "8. **3 签名阈值审定路径**：本复审**不授予任何审定签署**，`reviewed` 语义的后续使用仍须按 A-6.3 逐条取证。",
  "9. **`red/` 由「上一位 worker」与「续跑 worker」两段完成**：前者的 rc 从未落盘、\n   `rc=0` 来自续跑重跑（`red/baseline_recheck_report.json` 与前件 sha 相同 `adcade2f…`）——\n   我的独立重跑给出**同样的 0**，但**无法回溯上一位当时的真实 rc**。"
]
```

> 实现者原 `handoff.unverified` 的 9 条已由复审 §7 的 9 条**逐字取代**（内容全部被覆盖，见 `qualification.json.unverified_implementer_pre_review` 原样留存），**披露不丢失**。

---

## 6. 双读法裁定与 `L271` 段落位置（本落定的核心结论，逐字转录）

**① 双读法裁定 = 采 `U-PRIMARY`（主读法）**，裁定正文逐字：

> **我裁定采用 `U-PRIMARY`（oracle §3.3 冻结的主读法）作为判定本卡 J4 / `L271` 触发线的唯一读法。**
> 依据 U-PRIMARY：`T1/T2/T3` **全部不命中** ⇒ `trigger_fired = false` ⇒ **fail-closed 第 1 条未触发 ⇒ 不判 `blocked`**。
> `U-LITERAL` 的量化（40/40、8/8、三线全中）**照实保留**为反事实披露，**不作判据**。
> **若采字面读法 ⇒ 三线全中 ⇒ 按本卡冻结的 `J4` 应判 `blocked`。** 故本裁定是决定性的，我明确落笔、不回避。

四条依据（逐字，见 §4 `basis_verbatim`）：
1. **正证 1 —— 裁定主体的禁令子句自带范围。** ruling **L226** 是 OPEN-6 的「裁定（一句话）」，其禁令原文是
   「`threshold_basis=professional_judgement_required` **且** `threshold_review_status≠reviewed` 的阈值**不得触发任何自动动作**」。
   字面读法把范围词 `professional_judgement_required` 删掉，等于**改写了裁定主体的量词**。
2. **正证 2 —— A-6.1 的小节标题即范围。** L228 逐字「裁定 A-6.1：**占位阈值**在审定前的使用禁令」；
   `decision.md DEC-6` L156–157 把**占位阈值**定义为 `threshold_basis = "professional_judgement_required"` 的那一类。
   A-6.1 第 1 条是**该小节下的第 1 条**，其「二者缺一或 `not_reviewed` ⇒ fail-closed」按标题与 DEC-6 只辖占位阈值。
3. **正证 3 —— 字面读法会让同一条裁定的 A-6.2 成为死条文。** L236–L242 的 A-6.2 表有一列**列名就叫「审定前可否使用」**，
   逐字给 `arithmetic_identity = 可用（等式判定）`、`disclosure_definition = 可用（是/否型判定）`、
   `professional_judgement_required = 不可用`。
   而**盘上 40 条记录 0 条携带该字段**（我已实测）⇒ 全部落默认 `not_reviewed` ⇒ 字面读法下 **40/40 全不可用**，
   A-6.2 那两行「可用」**永远不可能成立**、`DEC-6` 的「两类阈值」之分也随之塌缩。
   **一条裁定不会在同一节里既说「审定前可用」又说「只要没审定就一律不可用」** ⇒ 字面读法与 A-6.2 冲突，须让位于明确列举的表格。
4. **正证 4 —— L271 自己把「实质」与「实施方式」切开了。** L271 逐字：「⇒ A-6.1 的**实施方式**（追加字段 + 默认 `not_reviewed`）
   **需按实际情况重议**，但**『未审定不得当已审定』这一实质不因此改变**。」
   即：**大批判不可用 ⇒ 触发的是「重议实施方式」这个 owner 动作，不是「实现者的实现错了」**。
   字面读法**恰恰会让该反例在字段落地的第一天就必然成立**（40/40 ⇒ 三线全中），
   这说明字面读法不是裁定者想要的操作化方式 —— 否则他不会把它写成「什么会推翻本裁定」里的一条。

**② `L271` 段落位置的影响**（逐字）：

> **段落位置证 1 —— L271 在 `#### 反例（什么会推翻本裁定）` 之下（该段首行 = L268，L271 是其第 2 条）。**
> 反例段的语义是「**若出现该现象，则本裁定的实施方式需重议**」——它是一个**带后果的触发器**，
> **不是**「落地前必须先满足的前置条件」。登记册 §一四三 B.2 已明确记载父曾把它误读成前置条件并自纠
> （逐字「**把反例当成了前置条件，属误读**」，L3557 再记一次）。**本次复审确认该自纠正确。**

> **段落位置证 2 —— 位置差异改变了 `trigger_fired=true` 的读法。**
> 若 L271 是前置条件 ⇒ 触发 ⇒ 「实现者不该动手」⇒ 卡本身有问题。
> 若 L271 是反例（实际位置）⇒ 触发 ⇒ 「**ruling owner 要重议 A-6.1 的实施方式**」，**实质（未审定不得当已审定）继续有效**，
> 实现者**把该触发如实量化并上交裁定**（而不是自行判死或自行放行）**恰恰是正确处置**。
> 实现者在 `oracle §3.3` 明写「**此分歧由复审裁定，不由我静默选边**」，并在 `handoff.unverified` 第 2 条再次披露 —— **不静默选边成立**。

**③ 显式反面登记（逐字，不许省）**：
- 反面裁决（逐字）：
  > **若采字面读法 ⇒ 三线全中 ⇒ 按本卡冻结的 `J4` 应判 `blocked`。** 故本裁定是决定性的，我明确落笔、不回避。
- 是否建议改判 `blocked`（逐字）：
  > **不建议。** 两道 fail-closed 的实测状态：
  
  | fail-closed | 条件（oracle 冻结） | 我的实测 | 后果 |
  |---|---|---|---|
  | 第 1 条 | 任一 `L271` 触发线在 **U-PRIMARY** 下命中 | **T1 不命中 / T2 记录 14<30、去重 4<6 不命中 / T3 记录 2<14、去重 1<2.5 不命中** ⇒ `trigger_fired=false` | **未触发** |
  | 第 2 条 | 原 21 例在**未变异补丁版**上任一回归 | **21/21 仍拒、`accepted_ids=[]`** | **未触发** |
  
  ⇒ 按我裁定的 U-PRIMARY，**两道均未触发 ⇒ 不判 `blocked`**，本卡 `status=review_pending` + `implementer_signed=false`
  的交付形态**成立**。（**若采字面读法则必须 `blocked`** —— 见 §3.1/§3.3-4，我已显式登记，不留给下一位猜。）
- owner 触发器：> 4. **若日后 owner 明文采字面读法** ⇒ 按本卡冻结 `J4` 三线全中 ⇒ 本卡应改判 `blocked` 并按 L271 重议实施方式；
     该情形**由我显式登记在此**，不由实现者承担。

**④ `L17 scope` 裁定 = 不适用**（逐字，含前置提醒）：

> **L17 逐字（我独立回源读到）**：「凡跨项目公共schema、canonical writer、registry或worker API，只有指定owner写；
> 发现scope外必要改动先记录阻断并交owner补卡，不能为绿灯建立平行框架。」

> **我的裁定：L17 不适用（同意实现者 §0.1 的判断，理由为我自读原文后独立得出）**：
> 1. L17 的四类辖域是**跨项目公共**件；被改对象是 `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py`，
>    落在 `.planning` 内、**非产品仓**（`src/`/`scripts/`/产品 `tools/` 计 0 文件，我复核 diff 头与 `git diff` 均一致）；
> 2. 该文件目前是 `I-11-A` **自己**的校验器；`I-11-C 是否复用同一校验器` 属 `OPEN-12`（owner 已裁「另立校验器专业卡」），
>    **跨项目复用尚未发生**，故尚不存在「公共 API 由非 owner 改写」的事实；
> 3. 本补丁**不建平行框架**：新错误码、新报告块全部进**同一支**校验器与**同一份** `validation_report.json`；
> 4. 附**前置提醒（P3 级）**：一旦 `OPEN-12` 卡裁 `I-11-C` 复用本校验器，`B6C-G1..G4` 与三新错误码须按
>    `A-6.3 第 5 条 / DEC-14 L364` 跨卡同步，**那时 L17 才可能被触发**；届时由 schema owner 收口。

---

## 7. `qualification.json` 摘要

| 字段 | 值 |
|---|---|
| 路径 | `evidence/BLOCKED6C-THRESHOLD-REVIEW-STATUS/qualification.json`（目录与文件均新建） |
| `formula` | `not_applicable_with_reason`（理由写在 `formula_reason`：本卡是纯簿记落定，不产生任何公式/预测结果） |
| `disclosure_adaptation` | `unmapped`（**未触碰**） |
| `accuracy` | `unproven`（**未触碰**） |
| `granted_scope` | **仅** iso 改动 + `changes.diff` 的证据与判据（复审已独立复跑的六项复核） |
| `not_granted` | 阈值审定签署 / 3 签名路径 · `BLOCKED-6a`/`6b` 解除（**仍 `still_blocked`**）· `OPEN-6` 解除 · 放行参数（`low/base/high` 仍 `null`）· 改 `threshold_basis`/阈值值 · 封盘 `I-11-A` 字节 · `I-11-B`/`I-11-C` 的 ACCEPT · 晋升 · 产品仓任何字节 · 字面读法下的 `blocked` 改判（**须 owner 明文采该读法**） |
| `status_authority` / `carried_findings` | 与本文件 §2/§3、`handoff.json` **逐字段相等**（镜像） |

---

## 8. 写入面、只读自证与边界

**本 pass 写入面 = 恰三处**：
1. `handoff.json`（状态面转录：`status`/`status_before`/`status_transition`/`status_scope`/`status_history`/`status_authority`/`carried_findings`/`reviewer_resolved_items`/`unverified`/`pre_image`/`verdict_is_transcribed_not_authored`）
2. `review.md`（本文件，新建）
3. `evidence/BLOCKED6C-THRESHOLD-REVIEW-STATUS/qualification.json`（新建目录 + 新建文件）

**本 attempt 既有产物复哈希（收尾实测，全部 `UNCHANGED`）**：

| 对象 | 字节 | sha256（前 16） | 判 |
|---|---|---|---|
| `oracle.md` | 27,126 | `6d86f27111f9a121` | UNCHANGED |
| `changes.diff` | 15,892 | `b2ec16ffe1e8f32b` | UNCHANGED |
| `final_verification.json` | 12,498 | `5390f9155cf3026a` | UNCHANGED |
| `reviewer_report.md`（只读） | 33,083 | `442577484e7b32bd` | UNCHANGED（本 pass 写 0 字节） |
| `reviewer_report.sha256`（只读） | 85 | `c3349767b342b580` | UNCHANGED（本 pass 写 0 字节） |
| `handoff.json`（**除状态面**） | — | — | 深比对：非状态面键**逐键全等**（写入时程序断言，0 不符） |
| `iso/` | 67 文件 / 1,159,080 | `9aeb06b5607caff4` | UNCHANGED |
| `iso_patched/` | 67 文件 / 1,169,966 | `5fd4dcbfdb582d79` | UNCHANGED |
| `tools/` | 6 文件 / 74,905 | `139ea62b1cb42f0f` | UNCHANGED |
| `red/` | 7 文件 / 45,697 | `2e4201a4684bbbe9` | UNCHANGED |
| `green/` | 4 文件 / 34,383 | `511dfd31dccd006b` | UNCHANGED |
| `mut/` | 15 文件 / 291,696 | `d346d3ea11293993` | UNCHANGED |
| `l271/` | 2 文件 / 15,785 | `ff9d3a0d92637b44` | UNCHANGED |
| 五份计划文件 | — | — | **本工位 0 次写入**；收尾复测 4 份 `UNCHANGED`，`findings.md` 于 `2026-09-26 10:59:14` 被**外部写入者**（非本工位）改动，已如实登记 |

**git（只读）**：`git -c core.quotepath=false diff HEAD --name-only` → 总数 **3830**、**非 `.planning` = 0**；**未用 `git status`**、**无 git 写**、**未联网**、**未跑任何测试**。

**本落定没有做的事**：
- **没有**写 `reviewer_report.md` / `reviewer_report.sha256`（各 0 字节），**没有**写本 attempt 任何其他既有字节；
- **没有**解除 `BLOCKED-6a` / `BLOCKED-6b`（仍 `still_blocked`）/ `BLOCKED-6c` / `OPEN-6` / `OPEN-12`；
- **没有**放行任何参数（`low/base/high` 仍 `null`）、**没有**改 `threshold_basis` 或任何阈值值；
- **没有**产生 `I-11-B` / `I-11-C` 的 ACCEPT、**没有**晋升、**没有**写产品仓任何字节；
- **没有**代签：`implementer_signed = false`，`verdict_is_transcribed_not_authored = true`；
- **没有**改五份计划文件、**没有**做字面读法下的 `blocked` 改判（该改判须 **owner 明文采字面读法**）；
- **没有**改封盘 `I-11-A/a20260919-01` 与两半区裁定、容差裁定的任何字节。

---

*由 carrier-landing bookkeeping executor（父派委派的簿记落定子代理）创建于 2026-09-26；本文件只转录，不新增任何接受。*
