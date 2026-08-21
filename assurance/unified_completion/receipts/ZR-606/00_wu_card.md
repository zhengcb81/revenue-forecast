# ZR-606 工作单元卡（preflight）— F2：商业量价层

- 领取时间：2026-08-22T04:45Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-606`，ZR-605 accepted + closure→ZR-606；锁 ZR-606。
- 依赖：ZR-605（✅ MineYearOperation）。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 商业量价层——price/payability/TC-RC/premium/byproduct/FX/royalty 的商业条款封装；每个变量有来源/假设/期限（provenance）；多商品与副产品不重复计价；净收入可重算（敏感性）。
2. **production entrypoint 是什么？** 新 `scripts/commercial_terms.py`（CommercialTerm/CommercialTerms 数据类 + 校验 + 净收入计算）。
3. **RED？** grep TC-RC|payab|premium|byproduct|royalty|FX → payable 已在 ZR-605、licensing_commercial/milestone_royalty 与矿业无关、foreign_exchange 仅是调整类别——商业量价层零实现。真实产品缺口。
4. **允许改哪些文件？** revenue：新 `scripts/commercial_terms.py`、新 `tests/test_zr606_commercial_terms.py`、revenue receipts/ZR-606/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-607（ownership/consolidation/internal flow 会计桥）。本卡不做：内部交易/elimination（ZR-607）、对账（ZR-608）。

## Acceptance criteria
- **C1 provenance 必填**（杀 G1）：每个商业条款变量 = {value, source, assumption, period}——value 有限数值（finite_number——ZR-605 REV-001 inf 教训）、source/assumption/period 非空 str。price 必填；TC/RC/premium/byproduct_credit/FX_rate/royalty_rate 可选（None 合法）。
- **C2 不重复计价**（杀 G2）：净收入 = gross（saleable_volume × price）− TC − RC + premium + byproduct_credit − royalty，再 × FX；byproduct_credit 是独立加项（副产品收入不得计入主商品 volume 再乘 price——多商品不重复计价）。
- **C3 敏感性可重算**（杀 G3）：纯函数 calculate_net_revenue(saleable_volume, terms) 可对任意 price/FX 重算——同一输入幂等、不同价格确定性可复现。
