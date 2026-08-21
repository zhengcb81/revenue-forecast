# ZR-609 工作单元卡（preflight）— F2 合流：紫金 pilot + 第二家矿企泛化

- 领取时间：2026-08-22T07:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-609`，ZR-611 accepted + closure→ZR-609；锁 ZR-609。
- 依赖：ZR-604~608（✅ 冲突/输入/量价/内部流/对账）+ ZR-610（✅ 会计 ADR）+ ZR-611（✅ 合成 E2E）。Registry 依赖列=ZR-604~608,ZR-610,ZR-611。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 合流：紫金 pilot——用 F2 契约链（MineYearOperation→commercial terms→ownership→elimination→reconciliation）对紫金矿业真实主要资产（卡莫阿-卡库拉/巨龙铜业/紫金山等结构）做逐矿可回答演示，逐矿贡献范围清楚；再用第二家**不同结构**矿企（如纯金矿商/无控股链）验证泛化——生产代码零公司/矿名硬编码。
2. **production entrypoint 是什么？** 组合既有 F2 模块（零产品改动——test-only 演示卡，合成紫金结构数据只存在于测试）。
3. **RED？** 无单一产品缺口——RED = 真实结构演示旅程不存在（紫金主要资产结构/逐矿可回答范围/第二家泛化未串起来）。
4. **允许改哪些文件？** revenue：新 `tests/test_zr609_zijin_pilot.py`；revenue receipts/ZR-609/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM、生产代码公司/矿名。
5. **下一单元解锁？** 解锁 ZR-707/711~713（F2 剩余）。本卡不做：真实 PDF 解析（wiki 侧）、ZR-707 schema 3.8 opt-in。

## Acceptance criteria
- **C1 紫金主要资产覆盖**（杀 RED）：合成紫金结构数据覆盖 3+ 主要资产（卡莫阿-卡库拉铜矿（DRC，权益链）、巨龙铜业（西藏）、紫金山金铜矿）——每矿 MineYearOperation→commercial terms→ownership→group 贡献可回答；逐矿可回答范围清楚（gap 诚实标注）。
- **C2 第二家泛化零硬编码**：第二家不同结构矿企（纯金矿商、无控股链、单币种）走同一契约链——生产代码零改动、零公司/矿名硬编码（grep 验证）。
- **C3 全链一致性**：紫金 3 矿贡献 + 内部流 elimination + reconciliation 与手算一致（确定性可重算）。
