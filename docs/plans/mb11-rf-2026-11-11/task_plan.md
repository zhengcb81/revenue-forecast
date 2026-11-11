# RF B37 差额接收与边界改造

## 目标

在 RF 自己的 codex/mb11-rf 工区，把 B37 compare/scope/publication 的最小 19 路径合同差额接到当前 main，保留现有 durable job、concurrency/recovery、D4 source port 与报告入册行为。严禁把旧 release 整树覆盖到 main。

## 当前状态

- 基线：b005a179280ee19695578bdba9427b4dd44cdd73
- 参考候选：28d646d306e8f0b5f90d402e204676cf97d2b5a1
- 独立工区：C:/Users/郑曾波/Projects/mb11-rf
- 已确认全候选会触及 628 个文件；本次范围严格限制到卡片指定 19 个产品路径与当前合同测试。B37 的 19 个产品路径中 4 个已同 blob、9 个有差异、6 个主线缺失。
- compare/CLI切片已独立审查、提交并推送，commit e060a8607a904547645ee8eaee347bd159004d01 已并入 RF main/origin/main；完整MB-RF/B37未完成。

## 步骤

1. A0（部分完成）：当前main的compare测试真实RED为缺少report_catalog_compare；当前job/recovery/source-port基线51 passed。 compare/CLI合成合同现已初步接入，剩余subject/scope/publication差额待续。
2. B（进行中）：main已接入 report_catalog_compare.py 与 compare_cli.py；剩余9个同名路径需逐hunk适配，另有4个B37主线缺失模块（scope binding、subject resolver、verified compare及其CLI）和publication来源合同待接收。只用RF本仓代码，旧CWP私有存储依赖必须保持隔离。
3. C：运行 B37 对应回归、当前 job/recovery/source/report-catalog 受影响测试。只修复可归于本卡的真实问题。
4. 独立审查实现、合同边界和测试；修完问题再在本分支提交/推送。
5. 本轮compare切片已按commit e060a860快进并推送RF main；其余B37差额按步骤1–4继续独立接收，完成的子功能不代表全卡/跨仓组合完成。

## 不在范围内

候选其余 609 条路径、118 个研究材料、旧 job facade 全树、重新跑公司预测、收费调用、修改 CWP/StockWiki/Dashboard。
