# W09-RF-RESEARCH 发现

## ROOT已冻结的起点（2026-10-23）

- 与ROOT的W08源码写集无重叠，工区已实际检出；不复用母仓未提交源码。
- 历史输入由母卡同目录INPUTS.json绑定真实路径/SHA。只读历史，不覆盖旧封存。
- W09准备49项摘录和经营桥是作者准备，不能代替独立研究质量验收；旧摘要不是新W08生产摘要。
- 0新联网/外部模型/下载；统一预算与unknown保留，生产原件不动、不翻译。

## 后续发现

### F1 页首切片是这次所有错引的共同根因

旧输入的摘录绝大多数是"某页前 650 字符"。这个切片的**归属**由页面排版决定，不由 claim 的目标业务决定。H1 p12 页首恰好是 TIDES 客户/分子数 + Testing 业务段，于是 9 条 Biology activity claim 与 `claim_driver_biology` 拿到了整页最不相关的一段；年报 p14 页首是小分子 D&M 段，于是 3 条 Biology H2 rebase 引用了一段完全无关的内容。

这解释了为什么"字节校验通过"却仍然错：校验只能证明切片真实存在，不能证明它描述的是目标业务。

### F2 三路审查集合里本来就有正确条目

18 条化学/TIDES 价格 claim 在旧输入里已经是 `conversion_assumption`。PROCESS-001 对它们的角色指控部分不成立（root_causes.json 自己也记录了 `process_role_allegation_partially_refuted_ids`）。如果按"被审查到就是错的"去改，反而会造出新缺陷。本次保留全部 18 条并补写跨业务范围说明。

### F3 预期被写成了实绩

`rpo_expected_2026_opening_cohort` 的原文是"4,220,706.46 万元**预计**将于 2026 年度确认收入"，是发行人预期，不是实际、不是区间、不是全年下限。旧输入写成 `reported_fact` 是因为作者脚本 `param()` 对"来自原文"的值一律默认 `reported_fact`。该参数没有收入 DAG 消费，所以纠正本身不改任何数字——这一点必须明说。

### F4 一个混合指数掩盖了两个节奏

旧 Base 对 non-TIDES 用单一活动量指数（1.30）覆盖小分子 D&M 与残余化学服务。但披露的 H1 节奏是 D&M +72.7%、残余约 +5.62%，差一个数量级。指数的存在形式合法，解释力是空的：它说不出最大增量由谁贡献。

独立桥给出了可检验的条件推论：残余 H2 重复可比期时，同一 non-TIDES 总额要求 D&M H2 增长约 +35.3%；残余保持 FY25 时，FY2028 D&M 需约 FY25 的 2.05 倍。这两个数在残余 ±10% 时分别移动到 +33.0%/+37.6% 与 2.02x/2.08x。

### F5 两个分母不能混用

non-TIDES 占集团**净**增量 65.82%；旧 native 输出的正向 driver 增量份额是 61.57%。分母不同（集团净增量 vs 正向 driver 增量之和），数字不同，不能互相替换来制造更高集中度。

### F6 修复过程中自己引入并修掉的四个缺陷

- `author_main_input.py` 的 `return` 写在 observations 赋值之前 → 66 条 typed observation 丢失（adequacy 显示 0 条）。已修复。
- RPO 纠正没进 `claim-changes.json`（不在 49 union 内）。已补 `out_of_union_requirement_repairs`。
- Testing activity claim 有同样的页首切片缺陷（不在 49 union 内）。已修复并单列，不计入 49。
- `forecast_version` 与 snapshot `--version` 字符串不一致，导致快照 input SHA 与 forecast input SHA 不同。已统一版本串并重跑全链。

### F7 六个 FY2026 桥仍带 `conversion_assumption_not_disclosed`

这不是输入缺陷：这些桥把 FY2026 活动量指数当作 conversion 输入，而活动量指数被声明为 `mechanism_direction`（它本身就是经营机制，不是转换）。投影因此找不到覆盖它的 conversion claim。**为消掉这个诊断而把机制改标成 conversion 会造成真正的错标**，所以保留诊断并在 `remaining-unknowns.json` 披露。

### F8 没有任何经验校准

`observed_range` 全为 null，12 项校准全 `unverified`。置信分与旧版完全相同（24.01705900038857）——因为本次是引用/角色修复，不改变证据数量与模型结构。分数不变本身就是"没有偷改数字"的证据之一。
