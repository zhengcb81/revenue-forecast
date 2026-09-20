# M14 decision record

Card: M14（`execution_v2/card_M14.md`），model_id `retail_franchise`，Attempt `execution_runs/M14/a20260919-01`。
`START_HERE.md` 要求：凡落入专业决策范围的事项（跨进程锁、发布包事务边界、财期/重述/收入总净额与
payability 归属、不可识别模型参数、样本与统计阈值、部署迁移与自然观察资格）都必须**先写 decision.md**。

## 本卡是否需要专业决策

**本卡范围内不需要。** 逐条对照 `START_HERE.md` 的专业决策清单：

- 跨进程锁 / 崩溃恢复：本卡是纯进程内纯函数，无锁、无租约、无持久化（见 `recovery/README.md`）。
- 发布包事务边界：不在本卡范围（属 I-09）。
- 财期/重述/收入总净额/payability 归属：本卡 A–C 阶段**没有任何真实公司披露输入**，
  全部输入是 `card_M14.md` L39 的合成数字，因此不存在"某公司某期的总净额归属"需要拍板。
- 不可识别模型参数：不适用（全部 driver 由合成输入给定）。
- 样本/基准/统计阈值与概率校准：不适用（无统计评估；F 资格未开工）。
- 部署迁移与自然观察资格：不适用（未部署）。

## 本卡实际做出的判断（均为实现级，非专业决策）

- `D-M14-1`：card-specific 负例用 `set_driver_element` 把 `recognized_fee_rate[0]` 置为 1.1，
  使拒绝发生在**值域守卫**上（实测消息 `driver retail_franchise.recognized_fee_rate must be between 0.0 and 1.0: FY2027`），
  而不是数组长度守卫上——同批历史卡曾出现负例其实被长度守卫拒掉的失真。
- `D-M14-2`：把"比例域上端含端点"作为**非 gating 观察**（OBS-BOUND-INCLUSIVE，取 1.0 → 实测 257.0），
  与 NEG-CARD（取 1.1 → 拒绝）配对。
- `D-M14-3`：`supply_revenue` 在本注册表中**不是**带符号 driver，因此负供应收入由 driver 下界（0.0）直接拒绝，
  而不是被"收入不得为负"终检拒绝；用 OBS-SUPPLY-BOUND 记录该契约事实，并在 `recovery/probes/signed_driver_probe.json`
  留下可复算的探针。
- `D-M14-4`：本卡不裁定"加盟系统销售能否并表""一次加盟费递延与供应重复确认"等会计口径（卡片 L45），
  这些属 D/E 阶段与会计 reviewer 的范围。

## 升级给 owner 的开放项（本卡不自行裁定）

以下事项与 `handoff.json` 的 `open_questions` **逐条一一对应**（同一编号、同一顺序），并镜像到
`evidence/M14/oq_rulings.json` 的 `open_questions_mirroring_handoff`；三者编号同源，owner 按任一处的
编号核对都不会漏看（F-03 之后不再出现"decision 只写到 OQ-04、handoff 有 5 条"的错位）：

1. OQ-01 (binding): the cards say the run cwd must come from I-00-B, but I-00-B binds the isolation plan and the two-stage command rule, not a materialised checkout tree. This attempt materialised its own read-only snapshot (iso/checkout_scripts, hashes equal to production). Needs a binding ruling; the code under test is byte-identical either way.
2. OQ-02 (silent zero-fill): model_registry.py:335 fills an omitted optional driver that has no explicit default with 0.0. This model has 3 such drivers (franchise_system_sales, recognized_fee_rate, supply_revenue); omitting franchise_system_sales asserts 'no franchise system sales' and omitting supply_revenue asserts 'no supply revenue', both indistinguishable from 'the disclosure was not found'. Registered, NOT fixed.
3. OQ-03 (signed vs bounded optional drivers): this model has NO signed/unbounded driver, so a negative supply revenue or franchise system sale is refused by the driver bound (0.0) rather than by an accounting judgement. Recorded by OBS-SUPPLY-BOUND and recovery/probes/signed_driver_probe.json; whether internal eliminations need a signed convention is a D/E decision.
4. OQ-04 (gross vs net for franchise system sales): the implementation multiplies franchise_system_sales by recognized_fee_rate, i.e. only the recognised fee share enters revenue. card_M14.md L45 refuses full consolidation; the disclosure-adaptation stage must decide how the system-sales figure is sourced and whether one-off franchise fees are deferred.
5. OQ-05 (pytest): pytest was not installed in the attempt venv (no offline wheel in the local pip cache, network forbidden) and the historical suite was not re-run. If a reviewer requires the historical suite for this card, that must be stated explicitly because it changes the attempt scope.

## 独立复核者对上述开放项的意见（**不是本实现者的决定**）

以下为 2026-09-20 独立复核转达的**复核者立场**，原样承接，**未由实现者采纳为决定**；
owner 需要据此自行裁定（复核者对 OQ-02 / OQ-03 明确表示「同意登记、反对在本批修」）：

- OQ-01 (binding): the independent reviewer accepted this attempt's handling - the code under test is byte-identical to production and the isolation semantics were measured to hold - and characterises the residual question as provenance DOCUMENTATION: the owner should state in writing either (a) that a self-built read-only snapshot byte-identical to production is accepted as equivalent to the I-00-B binding, or (b) that I-00-B must add a materialisation step and later cards must reference its output. The implementer does NOT adopt this as a decision; it is the reviewer's opinion, carried for the owner.
- OQ-02 (silent zero-fill): the reviewer AGREES to register it and OPPOSES fixing it in this batch; the reviewer's own independent enumeration found the same surface (31 optional driver slots without an explicit default across 24 models) and suggests the owner require an explicit value or an explicit null at the D (disclosure-adaptation) stage instead of changing the formula-layer semantics.
- OQ-03 (signed driver vs the non-negative revenue check): the reviewer AGREES to register and OPPOSES fixing it in this batch. The reviewer adds that the check is PER ROW, so a single negative year during a clawback refuses the whole row, while the correct accounting treatment depends on the presentation convention (net presentation vs separate lines) - an accounting reviewer's remit. Both sides were measured (see recovery/probes/signed_driver_probe.json and the signed-driver observation).
- OQ-04 (this card's own fourth question, card-specific): the reviewer separately closed the domain-edge part of it - both endpoints are inclusive with zero gap (1.0 accepted, 1.0000001 refused) - and, for the M13 invalid-observation variant, judged the 'do not repack the frozen fixture, open a labelled probe instead' handling ACCEPTABLE. This card's own text is in handoff.json; the implementer does not adopt the reviewer's opinion as its own decision.
- OQ-05 (pytest / historical suite): the reviewer AGREES that this card does not need it: the batch's evidence chain is a single standard-library-only runner plus frozen JSON, and the historical 97 tests / 216 subtests are not part of it. If the owner requires a re-run it should be registered as a SEPARATE regression gate, not folded into the formula sign-off conditions.


## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据 + r3 点验"，
`open_questions` 列出的 OQ-01…OQ-05（共 5 条）即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被
阻断项），`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY`（均按卡片要求停在
该资格，不改成整体 PASS）。

## r3 bookkeeping addendum (appended, not rewritten)

> 本节由 r3 记账/转录执行者于 2026-09-20 **追加**（append-only）：上文既有字节未被改写；`decision.md` 的
> 前像字节经 `sha256(new[:len(old)]) == sha256(old)` 逐字节校验。本节**不是自签**，验收文字由独立复核者写出。

1. **r3 独立复核判定**：本卡 `formula` 资格 = `accepted_scoped`，**范围仅限 `formula`**；`disclosure_adaptation`
   与 `accuracy` 不在本次裁定内。
2. **载体**：`review.md` 中的复核者裁决原文（**`review.md` 第 197–315 行**）；其**逐字节**转录证明见
   `evidence/M14/verdict_transcription_r3.json`（旧字节是新字节的前缀、追加区 sha256 = reviewer 源文件
   sha256 = `3ae06f89c6204fdffbb0811a6d70ba18efe5682ba78ce28fc91e9df60075b761`、源文件 9103 B、`byte_identical: true`）。同一裁定已记入
   `handoff.json.status` 与 `evidence/M14/qualification.json` 的 `formula.state`，两处旧值
   `review_pending` 均保留在 `*_before_bookkeeping_fix` 键下。（本节自身位于本文件第 63–85 行。）
3. **历史值声明**：本文件此前若出现任何"待复核 / 未签收 / pending"口径的表述，一律视为**历史值**，以本节为准。
   事实核对（记账执行者）：本卡 `decision.md` 原文并未出现 `review_pending` 字样（该字样出现在 M17–M20 的
   decision 记录中），故此声明用于**消除口径歧义**，而非订正某一行原文。
4. **范围未扩大**：`disclosure_adaptation` 仍为 `unmapped`，`accuracy` 仍为 `unproven`；D（披露映射）、
   E（历史映射探针）、F（准确性）三阶段**未执行**，不在本裁定覆盖范围内。
5. **非自签声明**：`implementer_signed: false`；`implementer_never_signs_acceptance: true`；
   authority = "acceptance was written by an independent reviewer, not by the implementer"。

相关记录：`recovery/production_drift_note.json`（F-r3-02 时间窗内的生产漂移声明）、
`evidence/M14/cases_annotation_repack.json`（F-r3-01 口径更正）、`recovery/bookkeeping_r3/summary.json`
（本次记账的改前→改后 sha256 台账）。
