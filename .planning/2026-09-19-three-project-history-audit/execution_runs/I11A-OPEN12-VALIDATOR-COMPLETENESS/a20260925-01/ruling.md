# I11A-OPEN12-VALIDATOR-COMPLETENESS — 裁定书（ruling）

attempt: `execution_runs/I11A-OPEN12-VALIDATOR-COMPLETENESS/a20260925-01`
role: **统计/工程 reviewer（非实现者）** · `handoff.implementer_signed = false`（**不代签**）
被裁对象: `I-11-A/a20260919-01` 的**校验器完备性**（`OPEN-12` 正解路径）
一句话结论: **`P2-5` 处置「部分」，`P2-6/P2-7/P2-8/P2-9` 处置「已处置」；`P2-5` 的完备性判据不成立
（我构造的 11 个反例全部被现有校验器放行），补法以 `changes.diff` 交付，补后 11/11 被拒、10/10 变异翻红。**

---

## §① 身份与授权链

**我是谁**：owner 指派的**统计/工程 reviewer（非实现者）**，受理新立卡
`execution_v2/card_I11A-OPEN12-VALIDATOR-COMPLETENESS.md`（sha256
`191c0ec5099bb893bf91b50a4acc573ed69c2e072872b0f44becf90f4d811090`，4,308 B）。
卡文第 1 行写明：本卡按 owner 裁定新立（`OWNER_DECISIONS.md` **§二十八**，2026-09-25）。

**§二十八 逐字（`OWNER_DECISIONS.md` L578–L591，sha256 `7e0b7917cb7b0cbe2158e48abc1f073b8157aafe082c115afb5fb593cace80de`）**：

> ## 二十八、【已裁定·第十二批】`OPEN-12` 按**正确所指**重问并获答：**「是，另立校验器专业卡」**（2026-09-25，选项式问答原话）
>
> > **提问原文（父，含自纠声明）**：「**先认错：`OPEN-12` 的所指我上一轮写错了。** 卡文 `I-11-A/decision.md L408` 与合并裁 `merge_ruling L362` 的原始定义是 ——『**是否需要为"校验器完备性"另立一张专业卡（统计/工程 reviewer）**』，**不是**我写的『cutoff 后交易所公告取得方式』…**现在按正确所指问你**」
> > **owner 选择**：**「是，另立校验器专业卡（建议）」**
>
> ### 执行映射
> 1. **`OPEN-12` = 是** ⇒ 卡文 `I-11-A/decision.md` 表中该行的「是否需要…」栏由 **`否` 变为 `是`**（**该行的更正以本节为准；卡文为封盘件，不回改，父按追加式在新卡文中承载**）。
> 2. **新立专业卡**：`execution_v2/card_I11A-OPEN12-VALIDATOR-COMPLETENESS.md`（父写卡文），受理人 = **统计/工程 reviewer**；**`I-11-C 是否复用同一校验器` 随该卡一并裁**（卡文 L408 的「影响面」栏原文）。
> 3. **裁权范围**：只裁 **`P2-5 / P2-6 / P2-7 / P2-8 / P2-9`** 这批独立复核发现的**校验器完备性**问题（源：`decision.md L408` 行首、`oracle §R2`、`mechanism_review §5 第 8/9 条`、`review.md §4`）—— **不重裁 I-11-A 已签收内容、不放行任何参数、不解除任何 BLOCKED、不产生 `I-11-B` 的 ACCEPT**。
> 4. **上一轮错题作答的交付** `OPEN12-CUTOFF-ANNOUNCE-ACQUISITION/a20260925-01` **归档为独立取证成果**（…）**但不计入 `OPEN-12` 的处置**。
>
> ### 执行纪律
> - **本裁定 = 一个许可（开卡），不是一个结论**：**不解除 `OPEN-12`**（其 `RULED_WITH_BLOCKED_VALUE` 状态在新卡交付并裁定前**维持**）、**不改任何 status**、**不产生 ACCEPT**。
> - 上一节 §二十七 的行内勘误**继续有效**：`OPEN-12` 的编号授权（G3）有效，**错的是父配的执行映射**。

**§二十七 行内勘误逐字（L565–L574，与本卡所指直接相关）**：

> **上表第 1 行的执行映射里，`OPEN-12` 的所指写错了。** … **实测（对）**：`OPEN-12` 的**原始定义在卡文**
> `decision.md` **L408** … **合并裁写得是对的**，是**父在起草本节时把 `OPEN-12` 的所指写错了** …
> ⇒ **`OPEN-12` 的正确问法（给 PLAN owner / 统计 reviewer）**：「**是否需要为『校验器完备性』另立一张专业卡？**」
> … **父侧错误第 18 起**（同族：**转述时改变所指**）。

**原始定义（回源，`decision.md` L408 逐字）**：

> `| OPEN-12 | 独立复核指出的 P2-5/P2-6/P2-7/P2-8/P2-9 已在本 attempt 内处置（见 oracle §R2、mechanism_review §5 第 8/9 条、review.md §4）；是否需要为"校验器完备性"另立一张专业卡（统计/工程 reviewer） | PLAN owner / 统计 reviewer | 否 | I-11-C 是否复用同一校验器 |`

**合并裁（回源，`I11A-OPEN-MERGE/a20260924-01/merge_ruling.md` L362 = G3 逐字）**：

> `| **G3** | **OPEN-12** | 「是否需要为"校验器完备性"另立一张专业卡（统计/工程 reviewer）｜**PLAN owner / 统计 reviewer**」（`decision.md` L408） | 本轮未派；`OWNER_DECISIONS.md` 内**未见**针对 I-11-A OPEN-12 的裁定行 | 归 PLAN owner / 统计 reviewer，无本轮授权、无已登记 owner 裁定 | I-11-C 是否复用同一校验器未定 |`

⇒ 授权链闭合：**L408 原始定义 → 合并裁 G3 登记缺口 → §二十七 执行映射写错所指（父自纠，第 18 起）→ §二十八 按正确所指重问并获答「是」→ 本卡成立**。
卡文 L408 该行的「否」以 §二十八 为准（封盘件不回改，由卡文承载更正）。

---

## §② `P2-5 … P2-9` 逐条原文引用（回源，不按转述）

**先说一处位置偏差（如实登记）**：卡文与 §二十八 把「发现原文」指向 `review.md` **§4**；实测 `review.md` §4 是
**实现者自检**「我自己发现的缺陷与限制」（P2-5 仅第 9 条一句带过，`P2-6/7/8/9` 未在 §4 出现）。
`review.md` **§5** 是独立复核报告 **§7 裁决正文**的逐字转录（也不含 P2-5…P2-9 的发现正文）。
**发现正文**在独立复核报告 §2 —— 按 `review.md` L86-88 记录的 sha 定位到
`C:\i11a-rv\review\REPORT.md`（实测 sha256 `e8b7d223e83c91128545e2b25b28b97ecba50cf2a5855e7366fabcaba16cafaf`，
与 `review.md` 记录**一致**），我按原文逐条读了；`review.md` §4/§5/§5.1 也已回源读。

### P2-5（验证器强度）

- **原文（`REPORT.md` L218–L238）**：
  > 「### P2-5（P2｜验证器强度）14/14 被拒是**有限测试**的结果，不是校验器的完备性
  > 正例：`validate()` 对当前 8 条命题返回 `[]`（我独立运行确认）。
  > 反例：我**自造 7 个清单外反例**… 其中 **5 个被接受（即未被拒）**：
  > R1 `page_index_basis` 末尾多一个空格 → **拒**；R5 `doc_id` 换成小米但保留紫金 sha256 → **拒**；
  > R3 `state=approved_frozen` + `reviewer="Independent Reviewer (external)"` → **接受**（自签 approved 只被**名字黑名单**拦…**任何其他名字都能通过**）；
  > R4 `threshold_basis="arithmetic_identity"` 但阈值文本是「±7% 无恒等式」 → **接受**（**无白名单、无内容一致性检查**）；
  > R6 `refuted_by = ["", "   "]` → **接受**；追加：`mechanism_chain = ['a','b','c']` → **接受**；
  > 追加：`observation_date = "TBD"` → **接受**；追加：两条同 `parameter_id` 的**相同**命题 → **接受**
  > （只在「同 id 但 driver/期间不同」时报 `E_DUPLICATE_PARAMETER`；oracle **O-11**…**未实现**）。
  > **判读**：14/14 的结论**没有被推翻**，但它的意义是「校验器能抓它被测过的那 14 类」。
  > `oracle.md` §3.3 / §3.4 / O-11 有 3 条硬规则**没有可执行的检查**，只能由人工 reviewer 兜。」
- **处置记录（回源）**：
  - `oracle.md` **R2-1**：「§7 反例套件由 14 条扩到 21 条…reviewer 自造的 7 个清单外变异中 5 个**当时未被拒绝**…
    本 §7 因此追加以下固定错误码与反例：`E_THRESHOLD_BASIS_UNKNOWN` / `E_THRESHOLD_BASIS_INCONSISTENT` /
    `E_CHAIN_END_SEMANTICS` / `E_OBSERVATION_DATE_UNRESOLVED` / `E_STATE_APPROVED_BY_IMPLEMENTER`（加强）/
    `E_DUPLICATE_PARAMETER`（加强）/ `E_EMPTY_FIELD`（加强）…**这仍不是完备性证明**…禁止下游把"21/21 被拒"读成"校验器完备"。」
  - `oracle.md` **R2-2**：阈值依据新增第三类 `disclosure_definition`（命题 7 自相矛盾的衍生修复）。
  - `mechanism_review.md` **§5 第 8 条**：「**校验器强度是有限的…** 首版…**没有机器检查**；reviewer 自造的 7 个清单外变异中有 5 个
    当时未被拒绝（`approved_frozen` + 编造 reviewer 名、`threshold_basis` 冒充 `arithmetic_identity`、`refuted_by=["","   "]`、
    `mechanism_chain=['a','b','c']`、`observation_date="TBD"`、两条同 parameter_id 的相同命题）。R2 已补齐这四项检查并把反例套件由
    14 例扩到 **21 例**…**但这仍不是完备性证明**：校验器只覆盖已写下来的规则。」
  - `review.md` **§4 第 9 条**：「**校验器强度有限（R2 新增，复核 P2-5）**…reviewer 自造 7 个变异中 5 个当时未被拒绝；
    R2 已补 4 类检查、反例套件扩到 21 例，但**仍不完备**（只覆盖已写下的规则）。」
  - `review.md` **§5.1 P2-5 行**：「已改（并**显式承认仍不完备**）…反例套件 14 → **21**，**reviewer 指出的未拒绝变异全部固化并现已被拒**。」
  - `decision.md` **DEC-14**（L345–L369）：选 (b)「补检查 + 固化反例 + **显式声明仍不完备**」，并写明「**若 reviewer 再找到未被拒绝的变异，
    说明仍有未写下的规则 → 按同一流程：补检查、把该变异固化为反例、把局限写进 §5，而不是辩解"21/21 已足够"**」。
- ⚠️ **计数口径不一致（我实测）**：`REPORT.md` 正文写「7 个…5 个被接受」，但其表格列 **8 行、其中 6 行「接受」**；
  `mechanism_review §5.8` 与 `DEC-14` 写「5 个未拒绝」却各列 **6 项**。三处口径互不吻合 → 该计数**未证实**（见 §⑨）。

### P2-6（表述风险）

> 「### P2-6（P2｜表述风险）OPEN-2 的「10,670.9 元/吨」算术自洽但措辞会被误读
> …**但两处需要正名**：1. …把它压缩成「每 **+1 吨/千克**移动约 10,670.9 元/吨铜当量」，读者极易读成「分母 +1 吨」。
> 实际「分母 +1 吨」的效应是 `…/885141 − …/885142 = 0.1403714089990013` 元/吨…
> **建议改写为**：「金→铜当量系数每 +1 吨/千克 ⇒ 当量分母 +83,161 吨 ⇒ 单位收入 −10,670.89 元/吨」。
> 2. 该式为**两点差分**而非偏导…措辞上不宜写成「偏导」。」

处置记录：`review.md` §5.1 P2-6 行「已改：改写为「系数 +1 吨/千克 ⇒ 当量分母 +83,161 吨 ⇒ 单位收入 −10,670.89 元/吨」，
并注明**两点差分不是偏导**」；落点 `hypotheses.json`（`H-CN-ZIJIN-SEG-02.conversion_formula`）。

### P2-7（内部不一致：观测窗口 vs 总体统计；`352→0`）

> 「### P2-7（P2｜内部不一致）观测窗口只用 3 页却有总体统计；`352→0` 表述错误
> …`probe_source_bytes.py` 对小米文件报告的是**全文件字节统计**（423），而 `P1_xiaomi.stdout.txt` 只**抽样 3 页**；
> `source_map.json` 却写「the standard-library path reports **352→0 classic pages**」…
> **建议**：`source_map.not_readable_in_this_attempt.reason` 改为「415 classic page objects found;
> content streams yield 0 characters on the 3 sampled pages … pdftotext (P2) emits Adobe-CNS1 mojibake」。」

处置记录：`review.md` §5.1 P2-7 行「已改：探针按"文件级字节统计 / 全流统计 / **页面内容流**统计"三档分开报告，
文档统一按内容流口径叙述」；落点 `tools/probe_xiaomi.py`、`source_map.json`、`mechanism_review.md` §5。

### P2-8（口径：VOL-03 用了未披露的「期初库存」）

> 「### P2-8（P2｜口径）VOL-03 用了未披露的「期初库存」
> 命题 3 的 falsifier 阈值写「销售量 ≤ 生产量 + **期初库存**」…年报产销量表只披露**本期库存量（期末）与同比变动**…
> 因此该阈值的「期初库存」在当前披露下**不可观测**，须由行业 reviewer 裁定…**但阈值文本里的分母口径要改，
> 否则下游按字面实现会缺数据**。」

处置记录：`review.md` §5.1 P2-8 行「已改：命题 3 的阈值不再使用未披露的"期初库存"，改为"由上一期披露的期末库存
取得期初库存 + 与库存量同比变动方向一致"的判定式，并新增 `observability_note`；跨期可得性登记为 OPEN-11」；
`mechanism_review.md` **§5 第 9 条** 逐字对应。

### P2-9（证据粒度：`plan_reviews.entries` 只有 12 条 vs 「285 个文件」）

> 「### P2-9（P2｜证据粒度）`plan_reviews.entries` 只有 12 条，与「285 个文件」的声称不对称
> `state_before/after.json` 的 `plan_reviews` 只记录 `entries` **12 条** + 目录 mtime；而 `review.md` §7 与
> `handoff.current_source_hashes.plan_reviews_note` 声称…**285 个**文件…**那 285 条的枚举结果不在交付物里**。
> 我用自己的枚举复核了这个**结论**…结论成立；但「声称的枚举」与「归档的证据」不匹配。」

处置记录：`review.md` §5.1 P2-9 行「已改：`plan_reviews` 改为**全量递归枚举**（path/byte_size/mtime_local）+
`newest_file` 字段，不再只存目录名样本」；落点 `tools/capture_state.py`、`state_before.json`、`state_after.json`。

---

## §③ 我独立复现了什么（**不引用实现者自述作为证据**；下列均为我自己跑/自己读）

**读过的文件（sha256 见 `oracle.md` §1）**：`decision.md`、`oracle.md`、`review.md`、
`evidence/I-11-A/mechanism_review.md`、`tools/validate_hypotheses.py`、`evidence/I-11-A/hypotheses.json`、
`evidence/I-11-A/source_map.json`、`evidence/I-11-A/validation_report.json`、`evidence/I-11-A/state_before.json`、
`state_after.json`、`binding.json`、`tools/probe_xiaomi.py`、`merge_ruling.md`、`OWNER_DECISIONS.md`、
卡文、`card_I-11-C.md`、独立复核 `C:\i11a-rv\review\REPORT.md`。
（`review.md` §5.1 的「已改…」是**被检主张**，我只把它当待验陈述，不当证据。）

**我做的复现（全部在本 attempt 的 iso 副本上运行，源 `I-11-A` 只读）**：

1. **正例与既有反例套件（基线）**：直跑 `main()` → `positive pass (0 errors)`、`21/21 rejected`、
   `accepted_by_mistake=0`、`rc=0`（`red/baseline_run.log`）。重跑产出的 `positive_case`、
   `counterexample_summary`、`counts`、`counterexamples` **四处与归档 `validation_report.json` 逐字段相等**。
2. **独立复现 reviewer 的 8 个原变异（REPRO-1…8）**：按 `REPORT.md` 表格字面构造并跑**当前**校验器
   → **REPRO-1…7 全部被拒**（错误码与表内一致），**REPRO-8（两条同 `parameter_id` 的相同命题）仍被放行**
   （`red/cases_original.json`）。⇒ `review.md` §5.1 P2-5 行「**全部**固化并现已被拒」**在字面第 8 条上不成立**。
3. **我自己的完备性反例（CE-01…CE-11）**：`oracle.md` §3 冻结后跑当前校验器 → **11/11 全部被放行**
   （`red/cases_original.json`、`logs/red_run.log`，`rc=0`）。
4. **补丁与绿**：`changes.diff`（10 个 marker 化判据块）→ **11/11 全部被拒**（含期望错误码），
   正例仍 pass、21/21 不破、8/8 REPRO 全拒（`green/cases_patched.json`、`green/patched_run.log`、`rc=0`）。
5. **变异（M1…M10）**：逐条删除一个新判据块 → **10/10 达到冻结预期**（目标反例翻回「放行」、
   其余保持被拒、正例与 21/21 不变）（`mut/mutation_results.json`，逐条 `rc=0`）。
6. **封盘自证**：`I-11-A/a20260919-01` 全部 103 个非 venv/非 pyc 文件在工作前后 **sha256 逐一相等、0 处差异**
   （`logs/source_manifest_before.sha256` + 复算比对）。
7. **P2-6/7/8/9 的落地回源**（逐条读原文件，见 §④）。

---

## §④ 结论（逐条：已处置 / 部分 / 未处置）

| 条目 | 结论 | 我自己的证据（非实现者自述） |
|---|---|---|
| **P2-5 校验器强度** | **部分（处置不完整）** | ① reviewer 的 8 个原变异：**7 个现已被拒**，**字面第 8 个（相同命题）仍被放行**（REPRO-8 实测）；② **完备性判据不成立**：我构造的 11 个同族反例（`oracle.md` §3）**全部被现有校验器放行**（RED `rc=0`）；③ 另一面**如实**：`oracle R2-1`、`mechanism_review §5.8`、`decision DEC-14` 都**显式声明"仍不完备"**，这一部分的诚实披露**到位** |
| **P2-6 表述风险** | **已处置** | 回源读 `hypotheses.json` → `H-CN-ZIJIN-SEG-02.conversion_formula` 已含「每 +1 吨/千克 ⇒ 当量分母 +83,161 吨（885,141 → 968,302）⇒ … −10,670.89 元/吨铜当量」与「这是**两点差分**，不是偏导数…分母单独 +1 吨的效应仅约 0.14 元/吨（−T/V²）」。**注**：校验器对该族（换算式语义）无检查，但规则面把复算责任交给 `verify_arithmetic.py`（O-12），本卡不要求校验器承担 |
| **P2-7 口径不一致** | **已处置**（就 P2-7 明确要求的两处） | ① `source_map.not_readable_in_this_attempt.reason` 已按建议重写（415 classic page objects / 前 30 页 30 条内容流 / 抽样页 0 字符 / pdftotext mojibake），并带 `measured_facts` 与 `correction_note`；② `tools/probe_xiaomi.py` 实测确有**三档**：`file_level_byte_counts` → 全流 `decode_streams` → 页面 `/Contents` 流，分别落 `facts`。**残留（如实登记，不据此改判）**：`binding.json` L26 仍写「423 /ObjStm occurrences, **0 classic page objects found by this attempt's scanner**」，与同 attempt `probe_xiaomi.py` 实测 415 相矛盾；该残留原文归 **P1-3**（不在本卡裁权内） |
| **P2-8 期初库存口径** | **已处置**（判定式改写到位；跨期可得性另属 OPEN-11，未决） | 回源读 `H-CN-ZIJIN-VOL-03.falsifier.threshold`：已改为「…期初库存须由『上一期披露的期末库存量』取得…方向相反或无法凑平 ⇒ 判口径不一致。上一期数据缺失则本式不可判定（转 `STOP_DISCLOSURE_ADAPTATION`）」；`falsifier.observability_note` 存在并写明 P2-8 与 OPEN-11。**注**：`observable` 的「具体性」在原校验器上**无机器检查**（我的 CE-10 证明其可被空泛风险词放行），但 oracle §3.4.1 当初也没给错误码 ⇒ 记为「内容已处置、机器化缺口由本卡补上」 |
| **P2-9 证据粒度** | **已处置** | 回源读 `state_before.json` / `state_after.json`：`plan_reviews.entries` 各 **285 条**（path/byte_size/mtime_local），带 `file_count`、`listing_note`、`mtime_local`、`newest_file`（`second_wave/final_review_checks.json`, 2026-09-19 10:05:32, 14,385 B）；「声称 285」与「归档 285」现已对称 |

**合并判定**：`decision.md L408` 的断言「P2-5…P2-9 已在本 attempt 内处置」——
**P2-6/7/8/9 成立，P2-5 只部分成立** ⇒ **`OPEN-12` 提出的"是否需要另立专业卡"是必要的，且本卡判定该批问题
处置不完整**。补法见 `changes.diff`（G1…G10），补后证据见 §⑤。

---

## §⑤ 红绿变异实测（rc，两个方向都有红有绿）

| 阶段 | 命令对象 | 判据（冻结在 `oracle.md`） | 实测 | **rc** |
|---|---|---|---|---|
| 基线 | `iso/tools/validate_hypotheses.py` → `main()` | 正例 pass + 21/21 + `accepted_by_mistake=0` | 与归档报告四处逐字段相等 | **0** |
| **红①（完备性漏）** | 同上，跑 `CE-01…CE-11` | 期望 **11/11 被放行** | `positive=pass`、`suite=21/21`、**CE 放行 11/11**、REPRO 拒 7/8（REPRO-8 放行）→ 冻结预期**全部命中** | **0** |
| **绿（补后抓住）** | `iso_patched/tools/validate_hypotheses.py`（= `changes.diff`） | 期望 **11/11 被拒且带期望错误码** + 正例 pass + 21/21 + 8/8 REPRO 拒 | 全部命中（CE-01→`E_THRESHOLD_BASIS_INCONSISTENT`、CE-02/03→`E_DUPLICATE_PARAMETER`、CE-04→`E_CHAIN_END_SEMANTICS`、CE-05→`E_MISSING_FALSIFIER`、CE-06→`E_BAD_PAGE_BASIS`、CE-07→`E_ANCHOR_NOT_FOUND`、CE-08→`E_OBSERVATION_DATE_UNRESOLVED`、CE-09→`E_STATE_APPROVED_BY_IMPLEMENTER`、CE-10→`E_FALSIFIER_OBSERVABLE_VAGUE`、CE-11→`E_EVIDENCE_PATH_NOT_ARCHIVED`） | **0** |
| **变异 M1…M10** | 每次只删一个 `# <OPEN12-Gn>…# </OPEN12-Gn>` 块 | 目标反例**翻回放行**，其余保持被拒，正例与 21/21 不变 | **10/10 达标**（`M1→CE-01`、`M2→CE-02+CE-03+REPRO-8`、`M3→CE-04`、`M4→CE-05`、`M5→CE-06`、`M6→CE-07`、`M7→CE-08`、`M8→CE-09`、`M9→CE-10`、`M10→CE-11`，每次 `others_leaked=[]`） | **0**（逐条） |
| 补丁版 `main()` | `iso_patched` → `main()` | 与基线同 | 正例 pass、21/21、`accepted_by_mistake=0` | **0** |

日志落点：`red/baseline_run.log`、`red/baseline_validation_report.json`、`red/cases_original.json`、
`red/cases_original_run1_with_harness_defect.json`（首跑原始日志，见 `oracle.md` erratum-1）、
`logs/red_run.log`、`green/patched_run.log`、`green/cases_patched.json`、`green/patched_validation_report.json`、
`logs/green_run.log`、`mut/M1..M10/cases_mutation.json`、`mut/mutation_results.json`、`logs/mutations.log`。
（`logs/mutations.log` 是从 `mut/mutation_results.json` 渲染的可读副本；**原始记录是该 JSON**，
每条含 `mutation`、`deleted_guard`、`deleted_bytes`、`rc`、`phase_expectation_met`、`positive`、
`own_suite`、`target_rows`、`other_ce_accepted`。首跑超时被打断的那次运行**没有**留下日志文件，
其产物已被后续两次完整运行覆盖，我只保留 `red/cases_original_run1_with_harness_defect.json` 这一份原始异常记录。）

**两个方向的判别力**：红方向（构造反例 → 放行）与绿方向（补后 → 全拒 + **每条新判据被删即翻红**）都已实测；
不存在「只有反例被拒、没有变异」的假绿。

---

## §⑥ `I-11-C 是否复用同一校验器`（卡文 L408「影响面」栏）

**结论：不建议在当前形态下直接复用；若复用，必须先满足下列条件（复用 ≠ 免检）。**

**理由**：
1. **判据族不同**：`validate_hypotheses.py` 校验的是 `hypotheses.json` 的**命题结构**（来源/机制链/driver/状态机/falsifier 五要素）；
   `I-11-C` 的验收是「每个量化命题都有**可执行触发器、反方判断和保留历史的更新规则**」，其产物是
   `evidence/I-11-C/{challenge_review.md, falsifiers.json, change_policy.json, qualitative_decision.json}`，
   schema 与错误码族都不同（`STOP_REVIEW`、`STOP_LINEAGE`）。
2. **现校验器对 I-11-C 的两条停止条件恰好是盲的**：I-11-C 停止条件一「**反证只有空泛风险词 → STOP_REVIEW**」
   正是我 CE-10 证明的缺口（空泛 `observable` 被放行）；条件二「**触发更新改写旧预测而非新增版本 → STOP_LINEAGE**」
   在本校验器里**完全没有**对应判据（无版本/快照/谱系检查）。
3. **`decision.md` DEC-14 的「兼容影响」只写了 I-11-B 的复用条件**（需接受阈值依据三分类 + 更严参数唯一性），
   **未**覆盖 I-11-C；合并裁 G3 也把该问题登记为「I-11-C 是否复用同一校验器**未定**」。

**若复用，须同时满足（缺一即视为未满足）**：
1. **先落地本卡 `changes.diff` 的 G1…G10**，并以本卡的红/绿/变异三份日志为回归基线（否则 11 个反例在 I-11-C 一样被放行）；
2. **扩展而非替换**：为 I-11-C 新增 `STOP_REVIEW`（空泛风险词 ⇒ 与 G9 同族）与 `STOP_LINEAGE`（旧快照被改写 ⇒ 版本/谱系判据）
   两族检查，且新判据同样**先冻结 oracle、再跑、再做变异**；
3. **schema 适配层独立**：不得直接拿 `validate_hypotheses.py` 去跑 `falsifiers.json`/`change_policy.json`；
   必须写 I-11-C 自己的绑定与错误码闭集，并同步进 I-11-C 的 oracle §7（DEC-14 恢复规则：改判据必须**重跑全部反例并重新计数**，
   不允许只跑正例）；
4. **签署不可复用**：`approved_frozen` 的独立 reviewer 身份 + `decision_sha256` 封缄（G8）必须继续生效，
   实现者/反方 reviewer 不得互签；
5. **状态不解锁**：复用讨论**不产生** `I-11-C` 的 ACCEPT、不解除任何 BLOCKED、不改变 `I-11-B` 的依赖关系。

---

## §⑦ 本卡**不授予**什么

- **不解除 `OPEN-12`**（其 `RULED_WITH_BLOCKED_VALUE` 在本卡交付并裁定前**维持**，`releases_nothing=true`）；
- **不产生 `I-11-A` 的再审/ACCEPT**，**不重裁已 `accepted_scoped` 的内容**，`does_not_claim_I11A_acceptance=true`；
- **不产生 `I-11-B` 或 `I-11-C` 的 ACCEPT**，不解锁任何下游卡；
- **不放行任何参数、不给阈值、不改 `threshold_basis`、不改任何 status、不授权晋升**；
- **不解除任何 BLOCKED**（含 OPEN-2/3/5/6/11 一切未决项）；
- **不代签**：`handoff.implementer_signed=false`，ACCEPT 只能由独立 reviewer 签；
- **不把 `changes.diff` 当作已入库实现**——它只是 diff，真仓零写入；
- **不写五份计划文件**、不联网、禁 git 写、禁 `git status`、不读取/采信
  `OPEN12-CUTOFF-ANNOUNCE-ACQUISITION` 的交付作为本卡证据（它解答的不是本卡问题）。

---

## §⑧ 反例清单（11 条）与被拒替代方案

**A. 反例（`oracle.md` §3 冻结；基命题 `H-CN-ZIJIN-SEG-01`）**

| # | 注入 | 现校验器（红） | 补丁后（绿） | 变异（翻红） |
|---|---|---|---|---|
| CE-01 | `threshold="相对偏离不超过 ±10%（纯幅度阈值）"`（`threshold_basis` 仍 `arithmetic_identity`） | **放行** | 拒 `E_THRESHOLD_BASIS_INCONSISTENT` | M1 |
| CE-02 | 追加除 `hypothesis_id` 外逐字相同的命题（同 `parameter_id`） | **放行** | 拒 `E_DUPLICATE_PARAMETER` | M2 |
| CE-03 | 同 `model_id`+`driver_name`+`effective_period`，但 `parameter_id` 不同（O-11 正向） | **放行** | 拒 `E_DUPLICATE_PARAMETER` | M2 |
| CE-04 | 末环 `"项目档案信息确认流程闭环交付"`（含「确认/交付」、无收入语义） | **放行** | 拒 `E_CHAIN_END_SEMANTICS` | M3 |
| CE-05 | `falsifier.observable="   "`、`source_route="   "` | **放行** | 拒 `E_MISSING_FALSIFIER` | M4 |
| CE-06 | **顶层** `page_index_basis="printed_page_1based"` | **放行** | 拒 `E_BAD_PAGE_BASIS` | M5 |
| CE-07 | **顶层** `anchor_text="这段文字不在原文中"` | **放行** | 拒 `E_ANCHOR_NOT_FOUND` | M6 |
| CE-08 | `observation_date="2026-13"` | **放行** | 拒 `E_OBSERVATION_DATE_UNRESOLVED` | M7 |
| CE-09 | `approved_frozen` + 30 字符编造 reviewer + `decision_sha256="x"` | **放行** | 拒 `E_STATE_APPROVED_BY_IMPLEMENTER` | M8 |
| CE-10 | `observable="市场风险上升（若风险加大则命题失效）"` | **放行** | 拒 `E_FALSIFIER_OBSERVABLE_VAGUE` | M9 |
| CE-11 | `evidence_path="…/NOT_ARCHIVED.json"` | **放行** | 拒 `E_EVIDENCE_PATH_NOT_ARCHIVED` | M10 |

**清单条数 = 11，被拒证据 = `green/cases_patched.json` 逐条 `rejected=true` 且 `expected_code_seen=true`；
放行证据 = `red/cases_original.json` 逐条 `rejected=false`；判别力证据 = `mut/mutation_results.json` 10/10。**

**B. 被我拒绝的替代方案**
1. **「21/21 已足够 ⇒ 校验器完备」**：拒绝——`oracle R2-1` 自己就写了「这仍不是完备性证明」，且我实测 11 条放行。
2. **「只挑能通过的反例凑绿」**：拒绝——CE 集合先冻结、后运行，且每条都要变异证明。
3. **改 `I-11-A` 封盘件来"修好"校验器**：拒绝——封盘只读，改以 `changes.diff` 交付。
4. **由我代签 ACCEPT / 解除 `OPEN-12`**：拒绝——非实现者、无 owner 结论。
5. **用重跑结果反写 `expected`**：拒绝——`expected` 全部手算写在 `oracle.md` §3（首跑与手算不符的两处按 erratum-1 如实登记，不回改表）。
6. **拿上一轮错题交付充数**：拒绝——`OPEN12-CUTOFF-ANNOUNCE-ACQUISITION` 未被读作本卡证据。

---

## §⑨ 边界（本卡不声称的东西）

1. **我的补丁同样不是完备性证明**：G1/G3/G9 是**关键词/字典型有界代理**（例如 G3 要求末环同时含收入词与确认/期间词，
   G9 用有限空泛词表），只能覆盖我冻结的这 11 个反例所代表的族；**不可**被读成"校验器已完备"。
2. **CE 集合不穷尽**：11 条是我能构造出的、有明确规则锚点的反例；未覆盖的族（如 `double_count_exclusion` 的语义质量、
   `refuted_by` 内容是否有意义、`falsifier_candidates` 为空、`hypothesis_id` 唯一性）**未测**，其中若干**也没有**对应错误码。
3. **置信分级**：CE-01…CE-08、CE-10 = 强（规则字面直接要求拒）；**CE-09 = 边界**（`R2-1` 字面只写「`decision_sha256`
   未填」，我按 `§7`「reviewer 非独立 → 拒绝」+ 封缄语义判，64-hex 是最低可证伪门槛）；**CE-11 = 中**（`evidence_path`
   的"必须是已归档输出"来自 O-3 与字段语义，非逐字错误码行）。
4. **oracle 内部张力（登记，不裁）**：`O-8` 要求本 attempt `approved_frozen` 计数为 0，而 `R2-1` 又定义了
   "封缄后可接受 approved" 的路径——两者的适用边界未写明。
5. **计数口径未证实**：`REPORT.md` 正文「7 个…5 个被接受」vs 其表格 8 行 6 放行 vs `mechanism_review §5.8`/`DEC-14`
   「5 个未拒绝」列 6 项；三处不一致，我**不**为任何一方背书。
6. **P2-7 残留**：`binding.json` L26 的「0 classic page objects found by this attempt's scanner」与
   `probe_xiaomi.py` 的 415 实测矛盾（原文归 P1-3，超出本卡裁权，仅登记）。
7. **复现环境**：系统 `C:\Miniconda\python.exe`（3.13.9），**`-B` 运行**（不产 `__pycache__`）、只读源、只写本 attempt 目录；
   未联网、未跑 git 写、未用 `git status`；本卡**不**触碰 `src/`、`scripts/`（`changes.diff` 只含 1 个
   `.planning/.../execution_runs/` 内文件）。
8. **工作树基线**：`git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` = **0**（3,826 行路径全在 `.planning` 内）；
   `git ls-files --others` 在 `.planning` 外的 48 个未跟踪文件全部位于 **`.tmp-r41-mutation/`**（mtime 2026-09-20，早于本卡 2026-09-25，
   **非本卡产生**；登记于此以免被误读为本卡改动）。
9. **本卡不回答**：`OPEN-11` 跨期可得性、`OPEN-6` 阈值审定、`OPEN-4` 索引口径枚举——都归各自裁定人。
