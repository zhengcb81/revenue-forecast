# M13 decision record

Card: M13（`execution_v2/card_M13.md`），model_id `asset_management`，Attempt `execution_runs/M13/a20260919-01`。
`START_HERE.md` 要求：凡落入专业决策范围的事项（跨进程锁、发布包事务边界、财期/重述/收入总净额与
payability 归属、不可识别模型参数、样本与统计阈值、部署迁移与自然观察资格）都必须**先写 decision.md**。

## 本卡是否需要专业决策

**本卡范围内不需要。** 理由（逐条对照 `START_HERE.md` 的专业决策清单）：

- 跨进程锁 / 崩溃恢复：M13 是纯进程内纯函数，无锁、无租约、无持久化（见 `recovery/README.md`）。
- 发布包事务边界：不在本卡范围（属 I-09）。
- 财期/重述/收入总净额/payability 归属：本卡 A–C 阶段**没有任何真实公司披露输入**，
  全部输入是 `card_M13.md` L12–34 的合成数字，因此不存在"某公司某期的总净额归属"需要拍板。
- 不可识别模型参数：不适用（全部 driver 由合成输入给定）。
- 样本/基准/统计阈值与概率校准：不适用（无统计评估；F 资格未开工）。
- 部署迁移与自然观察资格：不适用（未部署）。

## 本卡实际做出的判断（均为实现级，非专业决策）

- `D-M13-1`：card-specific 负例用 `set_driver_element`（把 `management_fee_rate[0]` 置为 1.1），
  使拒绝发生在**值域守卫**上，而不是数组长度守卫上。理由：同批历史卡曾出现"负例其实被长度守卫拒掉"
  的失真；本 attempt 的 `run_result.json` 记录拒绝消息
  `driver asset_management.management_fee_rate must be between 0.0 and 1.0: FY2027` 作为证据。
- `D-M13-2`：把"比例域上端含端点"作为**非 gating 观察**（OBS-BOUND-INCLUSIVE，取 1.0 → 期望 2005），
  与 NEG-CARD（取 1.1 → 拒绝）配对，避免"越界即拒绝"掩盖端点语义。
- `D-M13-3`：冻结的观察项 OBS-SIGNED-PERF-FEE 以 `base=defaults` 规格构造失败（该 base 无
  `performance_fee_revenue` 键 → KeyError）。**没有**重打包冻结件去掩盖；改以事后探针
  `recovery/probes/signed_driver_probe.json` 回答同一事实问题，并记入 `evidence/M13/revision_r2.json` 的 R2-05。

## 升级给 owner 的开放项（本卡不自行裁定）

以下事项与 `handoff.json` 的 `open_questions` **逐条一一对应**（同一编号、同一顺序），并镜像到
`evidence/M13/oq_rulings.json` 的 `open_questions_mirroring_handoff`；三者编号同源，owner 按任一处的
编号核对都不会漏看（F-03 之后不再出现"decision 只写到 OQ-04、handoff 有 5 条"的错位）：

1. OQ-01 (binding)：卡片要求"运行 cwd 由 I-00-B 绑定"，但 I-00-B 绑定的是隔离方案与两阶段命令规则，
   并未物化 checkout 树。本 attempt 自行物化只读快照 `iso/checkout_scripts`（与生产逐字节相同）。
   独立复核（2026-09-20）接受该处置，建议 owner 二选一书面写明：(a) 认可"与生产逐字节相同的自建只读
   快照"等价于 I-00-B 绑定；或 (b) 要求 I-00-B 追加物化步骤、后续卡改引其产物。
2. OQ-02 (silent zero-fill)：`scripts/model_registry.py:335` 对"有 optional 登记但无显式默认"的 driver
   在省略时补 `0.0`。本模型有 **2 槽**（`performance_fee_revenue`、`other_revenue`）；registry 级为
   **31 槽 / 24 模型**（标单位，见 `oq_rulings.json.enumerated_counts_with_units`）。独立复核
   **同意登记、反对在本批修**，建议 owner 在 **D 阶段**要求显式传值或显式 `null`。
3. OQ-03 (signed driver vs 负收入终检)：本模型带符号且无下界的 driver 为 `performance_fee_revenue`；
   探针（`recovery/probes/signed_driver_probe.json`）实测 `performance_fee_revenue = -100` →
   raised=`ModelRegistryError`。独立复核同意登记、反对在本批修，并补充：终检是**逐行**判定，
   会计上正确做法取决于口径（净额列报 vs 分列），属会计 reviewer 职权。
4. OQ-04 (invalid frozen observation)：冻结观察项 `OBS-SIGNED-PERF-FEE` 以 `base=defaults` 规格构造失败
   （该 base 无该 driver 键 → KeyError），**没有**重打包掩盖；r2 立了可执行的事后探针，r3 又按复核建议
   在该观察项上加了**只增不改**的标注字段（`evidence/M13/cases_annotation_repack.json` 证明差异仅为该
   标注）。独立复核判定该处置**可接受**；owner 若要改为"重打包 cases.json 并重跑"，需显式声明。
5. OQ-05 (pytest)：本 attempt 的 venv **未安装 pytest**（本地 pip 缓存无离线 wheel、联网被禁），
   历史 97 tests/216 subtests **未重跑**。独立复核**同意"本卡不需要"**，并指出若 owner 要求重跑，
   应作为**独立的回归门**单独登记，不并入 formula 签收条件。

## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据 + r3 点验"，
`open_questions` 列出的 OQ-01…OQ-05（共 5 条）即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被阻断
项），`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY`（均按卡片要求停在该资格，
不改成整体 PASS）。

## 独立复核者对上述开放项的意见（**不是本实现者的决定**）

以下为 2026-09-20 独立复核转达的**复核者立场**，原样承接，**未由实现者采纳为决定**；owner 需据此自行
裁定（复核者对 OQ-02 / OQ-03 明确表示「同意登记、反对在本批修」）：

- OQ-01 (binding): the independent reviewer accepted this attempt's handling - the code under test is byte-identical to production and the isolation semantics were measured to hold - and characterises the residual question as provenance DOCUMENTATION: the owner should state in writing either (a) that a self-built read-only snapshot byte-identical to production is accepted as equivalent to the I-00-B binding, or (b) that I-00-B must add a materialisation step and later cards must reference its output. The implementer does NOT adopt this as a decision; it is the reviewer's opinion, carried for the owner.
- OQ-02 (silent zero-fill): the reviewer AGREES to register it and OPPOSES fixing it in this batch; the reviewer's own independent enumeration found the same surface (31 optional driver slots without an explicit default across 24 models) and suggests the owner require an explicit value or an explicit null at the D (disclosure-adaptation) stage instead of changing the formula-layer semantics.
- OQ-03 (signed driver vs the non-negative revenue check): the reviewer AGREES to register and OPPOSES fixing it in this batch. The reviewer adds that the check is PER ROW, so a single negative year during a clawback refuses the whole row, while the correct accounting treatment depends on the presentation convention (net presentation vs separate lines) - an accounting reviewer's remit. Both sides were measured (recovery/probes/signed_driver_probe.json: performance_fee_revenue = -100 -> refused by the non-negative-revenue check).
- OQ-04 (invalid frozen observation OBS-SIGNED-PERF-FEE): the reviewer judged the handling ACCEPTABLE - do not repack the frozen fixture, keep the invalid observation and answer the factual question with a labelled post-hoc probe - and asked for the invalid observation to be marked inside cases.json, which revision r3 did with an append-only annotation whose only difference is proven by evidence/M13/cases_annotation_repack.json.
- OQ-05 (pytest / historical suite): the reviewer AGREES that this card does not need it: the batch's evidence chain is a single standard-library-only runner plus frozen JSON, and the historical 97 tests / 216 subtests are not part of it. If the owner requires a re-run it should be registered as a SEPARATE regression gate, not folded into the formula sign-off conditions.

## r3 bookkeeping addendum (appended, not rewritten)

> 本节由 r3 记账/转录执行者于 2026-09-20 **追加**（append-only）：上文既有字节未被改写；`decision.md` 的
> 前像字节经 `sha256(new[:len(old)]) == sha256(old)` 逐字节校验。本节**不是自签**，验收文字由独立复核者写出。

1. **r3 独立复核判定**：本卡 `formula` 资格 = `accepted_scoped`，**范围仅限 `formula`**；`disclosure_adaptation`
   与 `accuracy` 不在本次裁定内。
2. **载体**：`review.md` 中的复核者裁决原文（**`review.md` 第 208–326 行**）；其**逐字节**转录证明见
   `evidence/M13/verdict_transcription_r3.json`（旧字节是新字节的前缀、追加区 sha256 = reviewer 源文件
   sha256 = `46d52996d4df1039c14c69da8eb5b434f3f088aea049aa3a744f98704c5050d3`、源文件 9108 B、`byte_identical: true`）。同一裁定已记入
   `handoff.json.status` 与 `evidence/M13/qualification.json` 的 `formula.state`，两处旧值
   `review_pending` 均保留在 `*_before_bookkeeping_fix` 键下。（本节自身位于本文件第 75–97 行。）
3. **历史值声明**：本文件此前若出现任何"待复核 / 未签收 / pending"口径的表述，一律视为**历史值**，以本节为准。
   事实核对（记账执行者）：本卡 `decision.md` 原文并未出现 `review_pending` 字样（该字样出现在 M17–M20 的
   decision 记录中），故此声明用于**消除口径歧义**，而非订正某一行原文。
4. **范围未扩大**：`disclosure_adaptation` 仍为 `unmapped`，`accuracy` 仍为 `unproven`；D（披露映射）、
   E（历史映射探针）、F（准确性）三阶段**未执行**，不在本裁定覆盖范围内。
5. **非自签声明**：`implementer_signed: false`；`implementer_never_signs_acceptance: true`；
   authority = "acceptance was written by an independent reviewer, not by the implementer"。

相关记录：`recovery/production_drift_note.json`（F-r3-02 时间窗内的生产漂移声明）、
`evidence/M13/cases_annotation_repack.json`（F-r3-01 口径更正）、`recovery/bookkeeping_r3/summary.json`
（本次记账的改前→改后 sha256 台账）。
