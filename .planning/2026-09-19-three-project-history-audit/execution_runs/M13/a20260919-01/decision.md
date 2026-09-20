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

以下事项已写入 `handoff.json` 的 `open_questions`，并指向 owner 的三步接续动作，不在本卡内部决定：

1. **OQ-01（绑定口径）**：卡片要求"运行 cwd 由 I-00-B 绑定"，但 I-00-B 绑定的是隔离方案与两阶段命令规则，
   并未物化 checkout 树。本 attempt 自行物化只读快照 `iso/checkout_scripts`（与生产逐字节相同）。
   若 owner 期望的是 I-00-B 物化的 checkout，provenance 链不同；被测代码字节相同。**需要 binding 裁定。**
2. **OQ-02（静默补零）**：`scripts/model_registry.py:335` 对"有 optional 登记但无显式默认"的 driver
   在省略时补 `0.0`。本卡两个 optional driver（`performance_fee_revenue`、`other_revenue`）都属此类，
   省略即等于断言"没有该项收入"，与"披露里没找到"不可区分。已登记，**未改产品**。
3. **OQ-03（带符号 driver 与负收入终检）**：`performance_fee_revenue` 是带符号无下界 driver，
   但 `model_registry.py:352-353` 会把整行负收入判为 `ModelRegistryError`。回拨（clawback）期间真实
   可能为负；是否需要专业口径扩展（而不是让计算器直接拒绝）属 D/E 阶段与会计 reviewer 的决定。
4. **OQ-04（披露适配阶段尚未开始）**：`disclosure_adaptation` 保持 `unmapped`；D 的逐字段映射与
   已结束期间对账由 I-10-A 执行，本卡不产出、也不虚填。

## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据"，
`open_questions` 列出的 OQ-01…OQ-04 即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被阻断项），
`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY` 两个停止条件（均按卡片要求
停在该资格，不改成整体 PASS）。
