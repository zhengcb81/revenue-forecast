# ZR-605 RED 探针证据

- 日期：2026-08-22
- G1：grep MineYear|mine_year|volume.*grade.*recovery|payable scripts → 零命中。MineYearOperation 概念不存在——真实产品缺口。
- drift verdict: `still_missing`——G1 真实产品缺口。修复：新 `scripts/mine_year_operation.py`（MineYearOperation 数据类 + 七字段必填校验 + derive_saleable_volume + 模型驱动映射）。
