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

以下事项已写入 `handoff.json` 的 `open_questions`，并指向 owner 的接续动作，不在本卡内部决定：

1. **OQ-01（绑定口径）**：卡片要求"运行 cwd 由 I-00-B 绑定"，但 I-00-B 绑定的是隔离方案与两阶段
   命令规则，并未物化 checkout 树。本 attempt 自行物化只读快照 `iso/checkout_scripts`（与生产逐字节
   相同）。若 owner 期望 I-00-B 物化 checkout，provenance 链不同；被测代码字节相同。**需要裁定。**
2. **OQ-02（静默补零）**：`scripts/model_registry.py:335` 对"有 optional 登记但无显式默认"的 driver
   在省略时补 `0.0`。本模型有 1 个此类 optional driver（`other_revenue`），省略即断言"没有该项收入"，
   与"披露里没找到"不可区分。已登记，**未改产品**。
3. **OQ-03（带符号 driver 与负收入终检）**：本模型带符号且无下界的 driver 为 `other_revenue`；
   事后探针（`recovery/probes/signed_driver_probe.json`）实测 `other_revenue = -100.0` → raised=`ModelRegistryError`。
   相关会计口径属 D/E 阶段与会计 reviewer 的决定。
4. **OQ-04（披露适配阶段尚未开始）**：`disclosure_adaptation` 保持 `unmapped`；D 的逐字段映射与
   已结束期间对账由 I-10-A 执行，本卡不产出、也不虚填。

## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据"，
`open_questions` 列出的 OQ-01…OQ-04 即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被阻断项），
`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY`（均按卡片要求停在该资格，
不改成整体 PASS）。
