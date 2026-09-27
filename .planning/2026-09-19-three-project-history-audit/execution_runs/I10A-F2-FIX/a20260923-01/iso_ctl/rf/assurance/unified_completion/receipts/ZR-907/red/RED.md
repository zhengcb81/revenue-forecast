# RED.md — ZR-907 contract/doc/sample/skill-package drift patrol（阶段 H 收官）

## 探针（全部在当前机器实跑）

- **G1 无 schema 版本字面一致性门**：既有 `tools/drift_patrol.py`（R6.4）patrol() 仅五类（version/installation/config/docs/dependencies）——无 schema 版本字面扫描（"3.6" 等旧字面量可回归，ZR-703 清理无持续门）；FORECAST_SCHEMA_VERSION=3.7/OPT_IN=3.8 真源在 contracts/constants.py，无跨文件一致性检查。
- **G2 无 manifest 引用 hash 聚合**：uc manifest-verify（引用文件 hash）独立于 drift_patrol，无统一出口（引用文件被改 → manifest 红，但 patrol 不查）。
- **G3 无字段/引用存在性门**：关键契约常量无"被引用处存在"持续检查。

## 既有能力（不重复建设）

- `tools/drift_patrol.py`（R6.4：version/installation/config/docs/dependencies——installation 已含 skill-sync MATCH）；uc manifest-verify（ZR-905 已验证判别力）。

## 结论

G1~G3 为真实缺口（`still_missing`）；实施 = 扩展 `tools/drift_patrol.py`（patrol() 加 schema 字面扫描 + manifest-verify 聚合）+ 测试钉死注入漂移检出，产品零改动。
