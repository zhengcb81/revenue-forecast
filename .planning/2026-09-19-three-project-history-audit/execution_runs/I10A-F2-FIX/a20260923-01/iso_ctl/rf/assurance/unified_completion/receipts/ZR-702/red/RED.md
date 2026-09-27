# ZR-702 RED 探针证据（2026-08-19）

探针（revenue-forecast, HEAD 5ea9439）：
```
scripts/lint_input.py:28-77 本地硬编码 4 组字段元组：
  TOP_LEVEL_REQUIRED (14 字段) / CAPTURE_REQUIRED (10) / CLAIM_REQUIRED (10) / PARAMETER_REQUIRED (7)
grep schema_fields scripts/ → 0 命中（无字段真源模块）
grep "generate.*lint.*validate.*draft" tests/ → 0 命中（无 generator→engine 端到端测试）
```

结论（G1~G3 坐实）：
- **G1 schema 非单一真源（REV-01）**：linter 硬编码；validator（contracts/document.py 分散 require）与 generator（模板字段）各自维护同语义字段集；无一致性 gate。
- **G2 无 generator 闭环（REV-02）**：generate→fill→lint→validate_document→draft full run 无一次通过测试。
- **G3 生产无 test filler 无断言（REV-04）**：模板未填充语义（FIXME 占位）无钉死。

GREEN 对照（实现后）：schema_fields.py 唯一真源 + linter import + 三方一致测试 + 端到端闭环 + 未填充模板 fail-loud。
