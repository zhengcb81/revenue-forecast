# ZR-607 RED 探针证据

- 日期：2026-08-22
- G1：grep elimination|intersegment|internal sale|gross|net|smelt scripts → 现有命中均为**通用机制**：
  - revenue_constraints.py:11 CONSTRAINT_TYPES 含 elimination——通用参数化调整（segment_adjustment_parameter_ids 指向参数，值 ≤0），非内部流程
  - constants.py:146 intersegment_elimination——调整类别枚举
  - segments.py:465——调整类别处理
  - mine_year_operation.py payable——smelter terms 比例（ZR-605），非内部交易
- 结论：**矿业内部流程桥**（内部转冶炼/贸易的可追踪 elimination、gross/net 口径桥、与 ZR-603 权益/consolidation 组合）零实现——真实产品缺口。
- drift verdict: `still_missing`。修复：新 `scripts/internal_flow.py`（InternalFlow 可追踪 + eliminate_internal_revenue + gross/net 桥）。
