# ZR-608 工作单元卡（preflight）— F2：asset→segment→group reconciliation 与诚实 fallback

- 领取时间：2026-08-22T06:15Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-608`，ZR-607 accepted + closure→ZR-608；锁 ZR-608。
- 依赖：ZR-607（✅ internal flow 会计桥）。Registry 依赖列=ZR-607。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 asset→segment→group reconciliation——逐矿贡献（模型估计）与外部分部/集团披露对账：容差内才标 modeled；不闭合则回退到分部并列 gap（不伪造）；禁止产量×价格伪收入。
2. **production entrypoint 是什么？** 新 `scripts/reconciliation.py`（层级对账 + 诚实 fallback + 防伪收入门）。
3. **RED？** grep reconcil|fallback|modeled|gap scripts → gap 仅模板/文档词汇（generate_input_template 的 status=data_gap）、无对账机制——真实产品缺口。
4. **允许改哪些文件？** revenue：新 `scripts/reconciliation.py`、新 `tests/test_zr608_reconciliation.py`、revenue receipts/ZR-608/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-611（通用多矿合成 E2E）。本卡不做：E2E 场景（ZR-611）、紫金 pilot（ZR-609）。

## Acceptance criteria
- **C1 容差内 modeled**（杀 G1）：reconcile_layer(asset_total, reference_total, tolerance) → status="reconciled_modeled" 当 |diff| ≤ max(1.0, |ref|)×tol；否则 status="gap"（回退）。
- **C2 诚实 fallback**（杀 G2）：fallback_segment_listing(segment_revenues, group_reported) → 分部并列 + gap 标注——不闭合时不伪造差值；不输出伪收入。
- **C3 防伪收入**（杀 G3）：asset 贡献值必须有限（finite_number）——NaN/inf 拒绝；对账结果不因"产量×价格"式编造而闭合（无来源的 asset 贡献 → gap）。
