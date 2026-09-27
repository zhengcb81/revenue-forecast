# ZR-711 RED 探针证据

- 日期：2026-08-23
- G1（3.8 opt-in 零实现）：document.py:78-81 严格 `schema_version == FORECAST_SCHEMA_VERSION ("3.7")`——3.8 文档被拒；constants.SUPPORTED_FORECAST_SCHEMA_VERSIONS = {3.0..3.7} 无 3.8；schema_compatibility.SCHEMA_EMIT_ENGINES 无 3.8 键。
- G2（operating_units 词汇零命中）：grep operating_unit scripts → 零命中——3.8 矿业层（operating units/consolidation）无 schema 表达。
- G3（converter 零实现）：grep convert.*3_8|3_7_to_3_8 scripts → 零命中——无 3.7↔3.8 converter。
- drift verdict: `still_missing`。修复：constants/schema_compatibility 加 3.8 词汇；document.py 版本门 {3.7,3.8} + operating_units 加性校验（复用 validate_mine_year_operation）；新 scripts/schema_optin.py 双向 converter（只加空 gap 不猜值，round-trip 语义相等）。
