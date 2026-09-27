# RED.md — ZR-906 最终六类 ratchet（阶段 H 第五卡）

## 探针（全部在当前机器实跑）

- **G1 无 hardcode/legacy/encoding 自动化扫描器**：grep final_ratchet → 零命中；scripts/ 中 Kamoa/Porgera 仅出现在 docstring/注释防线语义标签（asset_ownership.py:18/174——ZR-603 模式，需代码级过滤区分）。
- **G2 coverage gate 不可用（超时）**：`tools/run_coverage_gates.py` 实测超时（>300s）——其全量 pytest 未排除 fc1103（T3 runner 既有挂起基线）→ required check 无法落地。
- **G3 无聚合器/零增长门**：六类 gate 分散无聚合；mypy 无冻结基线门（既有 2 条错误）。

## 既有能力（不重复建设）

- `tools/tests/test_complexity_ratchet.py`（复杂度 ratchet，FROZEN_MAX/NEW_FILE_MAX）；`tools/run_coverage_gates.py`（per-module coverage 门，需修 fc1103 排除）；quality_baseline.json（ZR-104）。

## 结论

G1~G3 全部为真实缺口（`still_missing`）；实施 = `tools/final_ratchet.py`（六类聚合 + scanners-only）+ 修 run_coverage_gates + 测试钉死非空洞与零增长，产品零改动。
