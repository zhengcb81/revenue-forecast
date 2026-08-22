# ZR-707 RED 探针证据

- 日期：2026-08-23
- G1（mixed recognition）：RECOGNITION_MODES = {"modeled_as_recognized", "lagged_activity"} 已存在；validate_recognition_metadata 已按分部独立校验 mode——混合模式（同公司不同分部不同模式）在当前代码中可通过（per-segment 校验，无跨分部冲突检测）。gap：无显式测试钉死混合模式合法性。
- G2（multi-commodity）：segment 级别每 segment 只有一个 model——无 multi-commodity product matrix 结构。gap：同矿多金属（铜+金副产品）需要独立 commodity lines。
- G3（presentation）：PRESENTATIONS = {"gross", "net"} 已存在；segment_bridge 已存在于 segments.py:500-569。gap：trading/other 活动无显式 presentation 校验测试。
- drift verdict：G1/G3 部分已有机制（需测试钉死）；G2 需产品实现（multi-commodity 验证）。
- 修复：test-only（G1/G3 钉死）+ 新 scripts/mixed_recognition.py（G2 multi-commodity 验证）。
