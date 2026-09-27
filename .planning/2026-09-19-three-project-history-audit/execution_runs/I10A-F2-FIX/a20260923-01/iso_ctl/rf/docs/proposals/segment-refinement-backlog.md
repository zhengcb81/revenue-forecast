# Backlog：分部细化与 derived_fact 登记

状态：**backlog**（登记，不排期，无实现承诺）
编制：2026-08-01（Phase 17.8）
依据：findings A7/A8/A9、REVIEW.md F7/F8/F9（阿里巴巴会话）

## 1. ACCG 拆 4 流（A7）

- **问题**：`accg_other` 合并两条经济上不同的曲线——直營、物流及其他（105,518，FY2026 +2%）与中国批发（26,312，+8%）为单一 direct_growth（base 3.5%-5.5%）。批发增速被直营拖低，驱动树归因混叠。
- **拆分方向**：CMR / 直營 / 即時零售 / 批發 4 流。
- **代价**：+5 参数 × 3 情景（vs 归因清晰度）。
- **触发条件**：下一次阿里巴巴模型迭代时评估。

## 2. CIG AI/傳統兩流基期拆分（A8，注明反方观点）

- **已披露**：Q4 外部 +40%、AI 产品收入 8,971 百万（占外部 30%）、Model Studio 客户 8 倍。
- **可构造**：基期 AI/非 AI 两流拆分（AI 流 usage 语义、非 AI 流缓慢增长）。
- **反方**：AI 年度绝对值需从 Q4 外推（假设叠加假设）——"更多參數≠更準確"（见 REVIEW.md 第四节分析 3）。当前 direct_growth fallback + 数据缺口声明是披露稀缺公司的诚实选择。
- **触发条件**：AI 年度绝对值有独立披露来源时再评估。

## 3. GMV 注册为 derived_fact（A9）

- **问题**：GMV_base = 343,867 ÷ 4.0% = 8,596,675，基期精确对齐由**构造**保证而非独立证据。
- **方向**：注册为 `derived_fact`（公式 `x0 / x1`：CMR ÷ take_rate），显式化推导关系；或引用独立行业 GMV 估算（易观）。
- **当前状态**：作为 analyst_assumption 注册 + data_gaps 文字声明——诚实但未显式化推导关系。

## 4. 关联登记（Phase 17 工具实证发现）

- **无 claim 摘录数字**（`--check-conclusion-facts` 实证，2026-08-01 修正后仍命中 5 处）：capacity（1,260.63/47/3,800）、customers（6,200）、demand（2.7）、earnings_call（100/300/3,800——含亿 vs billion 单位表述差异）、strategy_communication（3,800/5/6）。均为"来源已注册但数字未摘录为 claim"（A15 同型）；修复方向 = 输入构建时补摘录 claim 或降级表述，不在引擎层处理。
- **FF305 回购来源**（src_buyback_hkex_ff305）同属"无 claim 摘录"（schema 无回购事件类 claim 挂载点，见 TRUST_BOUNDARY §3 偏差记录）。
