# ZR-701 RED 探针证据（2026-08-19）

探针（revenue-forecast, HEAD 为 ZR-510 closure 提交后）：
```
revenue_forecast.py：main 内联 run_forecast（无 prepare_forecast 显式命名/契约测试）
--validate-only 已存在（零写行为无测试钉死）
publication_registry.py：仅 formal 发布（无 draft 未验证 artifact 类型）
source_preparation.py：prepare_source 无 ProcessingDemand 提交
```

结论（G1~G4 坐实）：
- **G1** 无显式 prepare_forecast 纯函数契约。
- **G2** validate-only 零写无钉死测试。
- **G3** 无 Draft artifact（formal-only）。
- **G4** source_preparation 不提交 ProcessingDemand（执行计划 F1 要求）。

GREEN 对照（实现后）：prepare_forecast 纯函数 + 确定性测试；validate-only 零写断言（无文件/无 registry 写入）；draft/formal 两类 receipt；processing_demand.py（同 wiki ZR-507 契约）+ prepare_source enqueue；原子发布绑定测试。
