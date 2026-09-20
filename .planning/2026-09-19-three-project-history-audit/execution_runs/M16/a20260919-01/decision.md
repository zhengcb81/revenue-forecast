# M16 decision record

Card: M16（`execution_v2/card_M16.md`），model_id `real_estate_rental`，Attempt `execution_runs/M16/a20260919-01`。
`START_HERE.md` 要求：凡落入专业决策范围的事项（跨进程锁、发布包事务边界、财期/重述/收入总净额与
payability 归属、不可识别模型参数、样本与统计阈值、部署迁移与自然观察资格）都必须**先写 decision.md**。

## 本卡是否需要专业决策

**本卡范围内不需要。** 逐条对照 `START_HERE.md` 的专业决策清单：

- 跨进程锁 / 崩溃恢复：本卡是纯进程内纯函数，无锁、无租约、无持久化（见 `recovery/README.md`）。
- 发布包事务边界：不在本卡范围（属 I-09）。
- 财期/重述/收入总净额/payability 归属：本卡 A–C 阶段**没有任何真实公司披露输入**，
  全部输入是 `card_M16.md` L33 的合成数字，因此不存在"某公司某期的总净额归属"需要拍板。
- 不可识别模型参数：不适用（全部 driver 由合成输入给定）。
- 样本/基准/统计阈值与概率校准：不适用（无统计评估；F 资格未开工）。
- 部署迁移与自然观察资格：不适用（未部署）。

## 本卡实际做出的判断（均为实现级，非专业决策）

- `D-M16-1`：card-specific 负例用 `set_driver_element` 把 `average_occupied_area[0]` 置为 -1，
  使拒绝发生在**下界守卫**上（实测消息 `driver real_estate_rental.average_occupied_area must be between 0.0 and inf: FY2027`）。
- `D-M16-2`：把"面积域下端含端点"作为非 gating 观察（OBS-BOUND-INCLUSIVE，取 0 → 实测 2.0），
  与 NEG-CARD（取 -1 → 拒绝）配对。
- `D-M16-3`：注册的 driver 集合中**没有**出租率/占用率 driver，这从契约层面确认了卡片 L8
  "已租面积不能再乘出租率"；尝试传入 `unknown_driver` 会被 N04 机制拒绝（`unsupported drivers`）。
- `D-M16-4`：`other_revenue` 是带符号无下界 driver（实测 29.0 于 -1），而 `rent_per_area` 与
  `average_occupied_area` 非负；"现金租金 vs 直线法会计租金""月租转年租"（卡片 L37/L39）不在本卡裁定范围。

## 升级给 owner 的开放项（本卡不自行裁定）

以下事项与 `handoff.json` 的 `open_questions` **逐条一一对应**（同一编号、同一顺序），并镜像到
`evidence/M16/oq_rulings.json` 的 `open_questions_mirroring_handoff`；三者编号同源，owner 按任一处的
编号核对都不会漏看（F-03 之后不再出现"decision 只写到 OQ-04、handoff 有 5 条"的错位）：

1. OQ-01 (binding): the cards say the run cwd must come from I-00-B, but I-00-B binds the isolation plan and the two-stage command rule, not a materialised checkout tree. This attempt materialised its own read-only snapshot (iso/checkout_scripts, hashes equal to production). Needs a binding ruling; the code under test is byte-identical either way.
2. OQ-02 (silent zero-fill): model_registry.py:335 fills an omitted optional driver that has no explicit default with 0.0. This model has 1 such driver (other_revenue); omitting it asserts 'no other revenue' and is indistinguishable from 'the disclosure was not found'. Registered, NOT fixed.
3. OQ-03 (signed other revenue): other_revenue is signed and unbounded (the probe records -1 being accepted as 29.0), so 'other revenue' can silently absorb a negative amount while the row stays non-negative. Whether such items belong in this driver at all is a D/E decision.
4. OQ-04 (monthly vs annual rent): rent_per_area carries no unit metadata beyond 'revenue_per_area', so a monthly rent used as an annual one cannot be detected by the contract; card_M16.md L39 requires an explicit conversion. The disclosure stage must bind this.
5. OQ-05 (pytest): pytest was not installed in the attempt venv (no offline wheel in the local pip cache, network forbidden) and the historical suite was not re-run. If a reviewer requires the historical suite for this card, that must be stated explicitly because it changes the attempt scope.

## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据 + r3 点验"，
`open_questions` 列出的 OQ-01…OQ-05（共 5 条）即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被
阻断项），`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY`（均按卡片要求停在
该资格，不改成整体 PASS）。
