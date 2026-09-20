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

## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据 + r3 点验"，
`open_questions` 列出的 OQ-01…OQ-05（共 5 条）即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被
阻断项），`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY`（均按卡片要求停在
该资格，不改成整体 PASS）。
