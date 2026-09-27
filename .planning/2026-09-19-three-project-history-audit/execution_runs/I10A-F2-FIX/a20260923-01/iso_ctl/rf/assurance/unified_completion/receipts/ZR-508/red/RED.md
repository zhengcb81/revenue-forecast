# ZR-508 RED 探针证据（2026-08-19）

探针（company-wiki, wiki HEAD bd337c4）：裸 DemandQueue（ZR-507）在持续高优先级流下的行为。

```
queue.enqueue(key="low", priority=0, now=0.0)
for t in 1..10: enqueue(high{t}, priority=5); claim; complete
claimed sequence: ['high1'...'high10']
low ever claimed: False
scheduler exists: False
```

结论（G1~G3 坐实）：
- **G1 无调度器/饿死**：裸 claim 严格 priority 序——低优先级 demand 在持续高优先级流下永不 claim（饿死）；无 aging 机制。
- **G2 无 deadline 语义**：无 deadline 逼近紧急调度。
- **G3 无 cost budget**：无 kind 级预算限流。

GREEN 对照（实现后）：DemandScheduler.schedule_once 用 effective_priority（aging bonus）→ 等待 ≥ aging_window 的低优先级必然被调度；deadline 逼近紧急加成 + 过期标记；kind budget 限流 + 重置恢复；同序列确定性；ZR-507 契约零改动。
