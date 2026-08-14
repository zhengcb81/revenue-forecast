# CA-108 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED：验证器无 mutation 保证

CA-101~107 的每个验证器只有正例/负例测试，没有 systematic mutation 保证。
任何单点缺陷（漏仓、漏 receipt、错 revision、自签、命令缩减、skip/blocked、
旧 triplet、dirty、无 schedule、半报告、代理 SLO、伪零、缺样本、R9 未过、
finding 未关）都可能静默通过——这正是本卡 30 个 critical mutation 的基线。

## 新工具对照（本卡实现）

`uc.mutations`：30 个 critical mutation（receipt.validate×8、revision pairing×7、
strict_state×7、ledger×3、scenario registry×3、closure×2），三段式
（make_valid→mutate 就地→check），runner 报告 total/killed/alive；
实测 kill=30/30=100%。新增 closure 分支须同时新增 mutation（验收规则）。
