# ZR-605 工作单元卡（preflight）— F2：MineYearOperation 输入合同

- 领取时间：2026-08-22T03:45Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-605`，ZR-610 accepted + closure→ZR-605；锁 ZR-605。
- 依赖：ZR-604（✅ 冲突解决）、ZR-610（✅ 会计 ADR 冻结）。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 MineYearOperation 输入合同——将逐矿年度运营数据（volume/grade/recovery/payable/product/period/scenario）封装为结构化输入，必填七字段缺一有 gap（不默认 0），遵守已批准矿业 ADR。
2. **production entrypoint 是什么？** 新 `scripts/mine_year_operation.py`（MineYearOperation 数据类 + 校验 + 派生驱动）。
3. **RED？** grep MineYear|mine_year|volume.*grade.*recovery|payable → 零命中——真实产品缺口。
4. **允许改哪些文件？** revenue：新 `scripts/mine_year_operation.py`、新 `tests/test_zr605_mine_year_operation.py`、revenue receipts/ZR-605/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-606（商业量价层）。本卡不做：price/payability/TC-RC（ZR-606）、ownership/内部交易（ZR-607）。

## Acceptance criteria
- **C1 七字段必填**（杀 G1）：MineYearOperation = {volume, grade, recovery, payable, product, period, scenario}——任一缺失 → gap（ForecastInputError），不默认为 0。volume > 0，grade > 0，recovery ∈ (0,1]，payable ∈ (0,1]，product 非空 str，period 非空 str，scenario ∈ {low,base,high}。
- **C2 ADR 合规**（杀 G2）：derive_saleable_volume(op) = volume × grade × recovery × payable；derive 所用公式与 ZR-610 ADR §2 一致（resource 模型的 saleable_volume 由上游分解得到）。
- **C3 可消费性**（杀 G3）：MineYearOperation → model_registry resource 模型驱动映射（saleable_volume + realized_price → 可直接喂 calculate_model_path）。
