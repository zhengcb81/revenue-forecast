# ZR-604 RED 探针证据

- 日期：2026-08-22
- G1：document.py:471-479 semantic_groups 检测冲突 → `ForecastInputError("unresolved conflicting parameters for {key}: {ids}")`——硬失败，无 assertion_status/resolution_status 字段、无双 assertion 机制。grep `assertion_status|resolution_status|conflict|review` scripts/*.py scripts/contracts/*.py → 零命中。
- drift verdict: `still_missing`——G1 真实产品缺口。修复：constants.py +2 行词汇 + document.py helper 提取（_validate_conflict_resolution + _validate_parameter_status_fields）+ semantic_groups 循环改造——validate_parameters 零 McCabe 增量。
