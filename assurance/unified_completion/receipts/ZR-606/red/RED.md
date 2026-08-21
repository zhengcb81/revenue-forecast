# ZR-606 RED 探针证据

- 日期：2026-08-22
- G1：grep TC-RC|payab|premium|byproduct|royalty|FX scripts → payable 已在 ZR-605（MineYearOperation 的 smelter terms 比例）；licensing_commercial/milestone_royalty 模型与矿业商业量价无关；constants.foreign_exchange 仅是 ADJUSTMENT_CATEGORIES（调整类别，非量价计算）。商业量价层（price/payability/TC-RC/premium/byproduct/FX/royalty 组合计算）零实现——真实产品缺口。
- drift verdict: `still_missing`。修复：新 `scripts/commercial_terms.py`（CommercialTerm provenance 结构 + validate + calculate_net_revenue）。
