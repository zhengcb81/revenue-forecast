# ZR-507 RED 探针证据（2026-08-19）

探针（company-wiki, wiki HEAD cbc6d8c）：
```
grep ProcessingDemand src/company_wiki → 0 命中
```
+ codegraph_freeze.py（revenue）wiki 目标列表：
```
"ProcessingDemand",  # required but expected missing (registered)
```

结论（G1~G3 坐实）：
- **G1 ProcessingDemand 不存在**：wiki 无 ProcessingDemand 类/队列（grep 0 命中；codegraph_freeze 期望缺失注册）。
- **G2 无去重/租约语义**：无 enqueue 按 key 去重、claim 租约 + heartbeat 续租、超时回收、retry 退避。
- **G3 无 consumer-priority 隔离**：无 priority 不可变契约（防插队）。

GREEN 对照（实现后）：ProcessingDemand dataclass + DemandQueue 全 API；生命周期闭环（enqueue→claim→heartbeat→complete / expire 回收 / fail 退避 / terminal）；consumer priority 不可变；codegraph_freeze 将 ProcessingDemand 移至 present 后 codegraph-verify 通过。
