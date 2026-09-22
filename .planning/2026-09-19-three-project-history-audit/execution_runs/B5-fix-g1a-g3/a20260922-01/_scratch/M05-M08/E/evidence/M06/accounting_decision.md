# M06 · 专业决策记录（PROPOSED，未签署）

本文件由实现者起草。每一条都是**提议**，`reviewer` 字段一律为 `PENDING_INDEPENDENT_REVIEW`；
实现者不签署专业结论，也不把提议当作已决事项。

## 决定清单

### DEC-M06-1 · 支付佣金的总额/净额（principal vs agent）如何决定活动量口径
- 选择（提议）：**以发行人的政策披露为准，且本卡不自行判定**。腾讯披露「视乎其于交易中担任主要责任人或代理人，按总额或净额基准呈报收入」（`disclosure_pages.json` PDF p167, 2.22(e)）。
- 理由：`eligible_activity × monetization_rate` 只有在两者**同口径**时才有意义；若活动量是 GMV（总额）而收入是净佣金，则 rate 必须是净 take rate。
- 反例：用 GMV × 毛利率或 GMV × 收入/GMV 都会把平台自身的成本结构塞进 rate，得到「看起来可复算」但无会计含义的乘积。
- 恢复规则：需先取得按总额/净额分列的收入与对应活动量；在此之前两者都记 `missing`。
- 被拒绝的替代方案：用「按百分比厘定」直接假定一个百分比（披露中没有该数字）。

### DEC-M06-2 · `monetization_rate` 的名称是否意味着 [0,1] 概率
- 选择（提议）：**不是**。卡片 L8 与审计台账都写明它是**货币/活动单位**。
- 运行时事实：本卡的探针 `OBS-RATE-GT1`（`rate=1.5`）返回 `753.0`，说明实现**没有**把该 driver 限制在 [0,1]（`evidence/M06/negative_results.json` 的 observations）。
- 待专业审查：这是否与 `ratio_drivers` 的其它成员的处理方式存在**契约不一致**（`subscription.timing_factor` 与 `services.utilization` 都被限制在 [0,1]）。不自行改实现。

## 未决状态

- `disclosure_adaptation`：**unmapped**。以上全部为 PROPOSED，`reviewer` 字段未签署；且仍需「一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅」。
- `accuracy`：**unproven**（无 I-12 冻结设计）。
- 本卡 formula 资格见 `qualification.json`（实现者不自签 accepted）。
