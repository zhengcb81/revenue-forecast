# ZR-608 RED 探针证据

- 日期：2026-08-22
- G1：grep reconcil|fallback|modeled|gap scripts → gap 仅是模板/文档词汇（generate_input_template 的 status=data_gap、lint_input 文档、mine_year_operation gap-on-missing 文档）；无层级对账（asset→segment→group）机制、无 fallback 语义、无防伪收入门——真实产品缺口。
- drift verdict: `still_missing`。修复：新 `scripts/reconciliation.py`（reconcile_layer 容差门 + fallback_segment_listing + finite 防伪门）。
