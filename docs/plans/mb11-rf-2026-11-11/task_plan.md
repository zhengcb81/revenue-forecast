# RF B37 差额接收与边界改造

## 目标

在 RF 自己的 codex/mb11-rf 工区，把 B37 compare/scope/publication 的最小 19 路径合同差额接到当前 main，保留现有 durable job、concurrency/recovery、D4 source port 与报告入册行为。严禁把旧 release 整树覆盖到 main。

## 当前状态

- 基线：b005a179280ee19695578bdba9427b4dd44cdd73
- 参考候选：28d646d306e8f0b5f90d402e204676cf97d2b5a1
- 独立工区：C:/Users/郑曾波/Projects/mb11-rf
- 已确认全候选会触及 628 个文件；本次范围严格限制到卡片指定 19 个产品路径与当前合同测试。B37 的 19 个产品路径中 4 个已同 blob、9 个有差异、6 个主线缺失。
- 当前compare/CLI两文件与B37纯合成测试已接入临时分支，范围回归通过；独立审查增量复核中，尚未提交、推送或并入RF main。

## 步骤

1. A0（部分完成）：当前main的compare测试真实RED为缺少report_catalog_compare；当前job/recovery/source-port基线51 passed。 compare/CLI合成合同现已初步接入，剩余subject/scope/publication差额待续。
2. B（进行中）：已接入 report_catalog_compare.py 与 compare_cli.py；其余9个同名路径、scope/subject/verified compare及publication合同仍需逐项差额适配。只用RF本仓代码，旧CWP私有存储依赖必须保持隔离。
3. C：运行 B37 对应回归、当前 job/recovery/source/report-catalog 受影响测试。只修复可归于本卡的真实问题。
4. 独立审查实现、合同边界和测试；修完问题再在本分支提交/推送。
5. ROOT验收后按通过的 commit 并入 RF main，更新本卡和总控 PWF；没有真实组合条件时保留明确的组合待办，不假报跨仓全通。

## 不在范围内

候选其余 609 条路径、118 个研究材料、旧 job facade 全树、重新跑公司预测、收费调用、修改 CWP/StockWiki/Dashboard。
