# M15 decision record

Card: M15（`execution_v2/card_M15.md`），model_id `transport`，Attempt `execution_runs/M15/a20260919-01`。
`START_HERE.md` 要求：凡落入专业决策范围的事项（跨进程锁、发布包事务边界、财期/重述/收入总净额与
payability 归属、不可识别模型参数、样本与统计阈值、部署迁移与自然观察资格）都必须**先写 decision.md**。

## 本卡是否需要专业决策

**本卡范围内不需要。** 逐条对照 `START_HERE.md` 的专业决策清单：

- 跨进程锁 / 崩溃恢复：本卡是纯进程内纯函数，无锁、无租约、无持久化（见 `recovery/README.md`）。
- 发布包事务边界：不在本卡范围（属 I-09）。
- 财期/重述/收入总净额/payability 归属：本卡 A–C 阶段**没有任何真实公司披露输入**，
  全部输入是 `card_M15.md` L36 的合成数字，因此不存在"某公司某期的总净额归属"需要拍板。
- 不可识别模型参数：不适用（全部 driver 由合成输入给定）。
- 样本/基准/统计阈值与概率校准：不适用（无统计评估；F 资格未开工）。
- 部署迁移与自然观察资格：不适用（未部署）。

## 本卡实际做出的判断（均为实现级，非专业决策）

- `D-M15-1`：card-specific 负例用 `set_driver_element` 把 `utilization[0]` 置为 1.1，
  使拒绝发生在**值域守卫**上（实测消息 `driver transport.utilization must be between 0.0 and 1.0: FY2027`）。
- `D-M15-2`：用 OBS-YIELD-GT1（`yield = 1.5` → 实测 1135.0）**直接回应卡片 L42**：
  制造良率的 0–1 边界没有被移植到运输 yield；yield 的量纲是 `revenue_per_unit`，实现不设上界。
  该观察非 gating，只把"卡片警告的那件事没有发生"落成可复算证据。
- `D-M15-3`：`ancillary_revenue` 是带符号无下界 driver，因此负辅助收入（退款/冲回）被接受（实测 130.0）；
  探针 `recovery/probes/signed_driver_probe.json` 记录 `ancillary_revenue = -100` 被接受为 50.0。
- `D-M15-4`：本卡不裁定 ASK/RPK 与吨公里的混用、燃油附加是否重复计入、利用率分母口径（卡片 L40/L42），
  这些属 D/E 阶段与行业 reviewer 的范围。

## 升级给 owner 的开放项（本卡不自行裁定）

以下事项与 `handoff.json` 的 `open_questions` **逐条一一对应**（同一编号、同一顺序），并镜像到
`evidence/M15/oq_rulings.json` 的 `open_questions_mirroring_handoff`；三者编号同源，owner 按任一处的
编号核对都不会漏看（F-03 之后不再出现"decision 只写到 OQ-04、handoff 有 5 条"的错位）：

1. OQ-01 (binding): the cards say the run cwd must come from I-00-B, but I-00-B binds the isolation plan and the two-stage command rule, not a materialised checkout tree. This attempt materialised its own read-only snapshot (iso/checkout_scripts, hashes equal to production). Needs a binding ruling; the code under test is byte-identical either way.
2. OQ-02 (silent zero-fill): model_registry.py:335 fills an omitted optional driver that has no explicit default with 0.0. This model has 1 such driver (ancillary_revenue); omitting it asserts 'no ancillary revenue' and is indistinguishable from 'the disclosure was not found'. Registered, NOT fixed.
3. OQ-03 (signed ancillary revenue): ancillary_revenue is signed and unbounded, but a negative total row is refused by model_registry.py:352-353. The probe records ancillary_revenue=-100 being accepted (50.0) on the positive base while a large negative would refuse the row; whether reversals need a different convention is a D/E decision.
4. OQ-04 (yield domain): the implementation applies NO upper bound to yield (OBS-YIELD-GT1 = 1135.0 for yield 1.5). This is correct for a transport unit price, but it means a percent-vs-amount unit error cannot be caught by the contract; the disclosure stage must bind the unit explicitly.
5. OQ-05 (pytest): pytest was not installed in the attempt venv (no offline wheel in the local pip cache, network forbidden) and the historical suite was not re-run. If a reviewer requires the historical suite for this card, that must be stated explicitly because it changes the attempt scope.

## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据 + r3 点验"，
`open_questions` 列出的 OQ-01…OQ-05（共 5 条）即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被
阻断项），`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY`（均按卡片要求停在
该资格，不改成整体 PASS）。
