# M05 · 专业决策记录（PROPOSED，未签署）

本文件由实现者起草。每一条都是**提议**，`reviewer` 字段一律为 `PENDING_INDEPENDENT_REVIEW`；
实现者不签署专业结论，也不把提议当作已决事项。

## 决定清单

### DEC-M05-1 · 订阅期间分摊（递延确认）如何进入本模型
- 选择（提议）：**不进入**。`timing_factor` 是「年度内确认比例」的契约位，而发行人披露的是「会员充值款在会员有效期内按天确认」的**会计政策**（`disclosure_pages.json` PDF p98）。
  两者不是同一个量：政策描述的是**确认时点分布**，`timing_factor` 是一个乘数。
- 理由：把会计政策直接翻译成一个 0–1 乘数需要跨期充值结构（cohort）数据，发行人不披露。
- 反例：若把「按天确认」当成 `timing_factor<1`，则 2024 年新增会员的一次性充值会被错误地摊到既有客户身上，年收入会被低估；本卡没有可复核的分摊依据，因此不填。
- 兼容影响：不填 `timing_factor` 走默认 1.0，等于「平摊到全年」，这是**已知偏差**而非事实。
- 恢复规则：若日后取到逐月会员数与递延余额，可重算 `timing_factor = 当年确认收入 / 当年现金充值`。
- 被拒绝的替代方案：用披露的 19.3% 增速或「ARPPU 稳步提升」的定性表述反推乘数（无依据）。

### DEC-M05-2 · 期末会员数是否可作 `average_customers`
- 选择（提议）：**不可以**。卡片 L42 明确把「年末客户不等全年平均」列为业务负例。
- 证据：披露只有期末存量 7331 万（PDF p13），没有月度/季度序列，无法计算平均。
- 影响：`subscription.average_customers` 记 `missing`；与之绑定的 `revenue_per_customer` 也随之为 `missing`。
- 待专业审查：行业 reviewer 是否接受某类替代口径（如「付费会员日均数」）作为平均的代理。

## 未决状态

- `disclosure_adaptation`：**unmapped**。以上全部为 PROPOSED，`reviewer` 字段未签署；且仍需「一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅」。
- `accuracy`：**unproven**（无 I-12 冻结设计）。
- 本卡 formula 资格见 `qualification.json`（实现者不自签 accepted）。
