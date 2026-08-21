# ZR-607 工作单元卡（preflight）— F2：ownership/consolidation/internal flow 会计桥

- 领取时间：2026-08-22T05:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-607`，ZR-606 accepted + closure→ZR-607；锁 ZR-607。
- 依赖：ZR-603（✅ ownership timeline/apply-once）、ZR-606（✅ commercial terms）。Registry 依赖列=ZR-603,ZR-606。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 ownership/consolidation/internal flow 会计桥——集团内部转冶炼/贸易的收入须可追踪并 elimination（不重复计入集团收入）；gross vs net 口径桥；与 ZR-603 权益折算、ZR-606 商业量价组合成完整会计桥。
2. **production entrypoint 是什么？** 新 `scripts/internal_flow.py`（InternalFlow 数据类 + 校验 + elimination/gross-net 计算）。
3. **RED？** grep elimination|intersegment|internal sale|gross|net|smelt → revenue_constraints 的 elimination 是**通用参数化调整**（segment_adjustment_parameter_ids 指向参数），constants.intersegment_elimination 是调整类别，segments.py:465 处理调整类别——均非**矿业内部流程桥**（内部转冶炼/贸易的可追踪 elimination）。零实现。
4. **允许改哪些文件？** revenue：新 `scripts/internal_flow.py`、新 `tests/test_zr607_internal_flow.py`、revenue receipts/ZR-607/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-608（asset→segment→group reconciliation）。本卡不做：对账/fallback（ZR-608）、单位换算表（ZR-611 按需）。

## Acceptance criteria
- **C1 InternalFlow 可追踪**（杀 G1）：InternalFlow = {flow_id, source, destination, product, volume, transfer_price, period, scenario}——flow_id/source/destination/product/period/scenario 非空 str、volume/transfer_price 有限正数（finite_number）；任一缺失 → gap（不默认为 0）。
- **C2 elimination 不重复计**（杀 G2）：internal_revenue(flow) = volume × transfer_price；eliminate_internal_revenue(external_revenue, flows) → {gross, internal_total, net}：net = external（内部销售从集团收入消除，不重复计）；gross 口径含内部销售、net 口径不含——gross/net 桥。
- **C3 组合语义**（杀 G3）：与 ZR-606 calculate_net_revenue 组合——内部销售按商业条款折算后 elimination；与 ZR-603 口径对齐（equity_share 折算后内部销售仍须消除——权益法下不重复计）。
