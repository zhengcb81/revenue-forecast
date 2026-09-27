# ZR-712 RED 探针证据

- 日期：2026-08-23
- G1（policy 版本化缺失）：scripts/analysis/confidence.py 权重（20/25/10/15/15/15）与 rating 阈值（80/55）硬编码在 calculate_confidence——无 policy 对象、无版本、无校验。rating 由 `score >= 80 / >= 55` 字面量决定。
- G2（反博弈缺失）：grep mutation/duplicate/split/plug/zero-impact/one-observation/wrong-record scripts/analysis/confidence.py → 零命中；test_scenarios_confidence.py 仅覆盖 duplicate sensitivity、source rank 不提升、segment crossing 三例——六类 accuracy-record 博弈 mutation 无显式拒绝/披露。
- G3（接线）：validate_historical_accuracy_records（evidence.py）处理 wape/observations，但无博弈检测钩子。
- drift verdict: `still_missing`。修复：新 `scripts/confidence_policy.py`（policy 版本化 + validate_confidence_policy + detect_gaming_mutations 六类 + recompute_rating）+ 测试钉死。
