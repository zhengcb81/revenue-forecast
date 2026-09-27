# ZR-703 RED 探针证据（2026-08-20）

探针（revenue-forecast, HEAD 00a1295）：
```
FORECAST_SCHEMA_VERSION = "3.7"（contracts/constants.py:16）
SUPPORTED_FORECAST_SCHEMA_VERSIONS = {3.4, 3.6, 3.7}

grep "schema 3.6" scripts/（注释/docstring）：
  generate_input_template.py:1 "Emit a schema 3.6 input skeleton..."
  generate_input_template.py:41 "Build a schema 3.6 skeleton..."
  generate_input_template.py:238 "Schema 3.6 skeleton. Replace..."
  fix_hashes.py:1 "Recompute and sync schema 3.6 input-side hashes."
  lint_input.py:1 "Collect-all static pre-flight linter for schema 3.6 inputs."
```

结论（G1~G3 坐实）：
- **G1 文档 3.6 硬编码与常量 3.7 不一致**：5 处注释/docstring 硬编码"3.6"。
- **G2 SUPPORTED_FORECAST_SCHEMA_VERSIONS 与 COMPATIBLE_VERSIONS 迁移路径一致性待验证**。
- **G3 generator 输出 schema_version == FORECAST_SCHEMA_VERSION 无独立钉死**。
