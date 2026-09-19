本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-04-D — 实施原子lease更新并验证进程交错

父项：I-04。状态：planned；实施结果：未执行。角色：filing-fetch 负责人（wiki 并发 reviewer）。

依赖：I-04-C、I-04-B。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [scripts/fetch_filing.py:565](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:565) — `PausedWorkerScope._register`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:579](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:579) — `PausedWorkerScope._unregister`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:515](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:515) — `PausedWorkerScope.__enter__`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:592](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:592) — `PausedWorkerScope.__exit__`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。

### 允许改动

- 隔离 filing fetch_filing.py 的 lease/owner 边界及必要现有依赖声明（锁实现仅限已签方案）；相应测试；不修改生产workercontrol

### 输入与独立预期

- I-04-C 签署状态表；新 run 内的临时 catalog/lease目录；仅记录pause/resume而不控制真实worker的 fake command process。
- 两进程 A/B 通过显式barrier控制顺序；不是在同一Python解释器里patch os.getpid 就声称跨进程通过。

### 按序动作

1. 先写顺序和同PID嵌套测试，再按协议实现锁内读-改-写与唯一lease释放，固定临时文件名称冲突也要在协议内处理。
2. 实现owner generation与pause/resume确认间的可恢复状态；进程退出不得吞掉写失败后仍报告拥有首租约。
3. 实现计划中的stale/损坏处理并保护用户原暂停意图；最后释放不跨越新acquire，也不无条件删除所有权证据。
4. 运行两真实本地子进程在临时目录内的barrier调度：同时acquire、先后release、last-release与new-acquire竞态、同PID嵌套（单进程两scope）。
5. 在每个签署崩溃窗口只杀本测试已记录PID的子进程；保存剩余磁盘状态，再以独立新进程执行批准恢复。
6. 运行T-FILING；对照各事件恰好一次/禁止事件要求。不能仅用循环100次无碰撞作为并发正确性证明。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| F-L5 | A/B在read前barrier同时acquire | 首个owner只有1；两个lease都保留；pause确认后参与者进入；无提前resume |
| F-L6 | A最后release前B开始acquire | 符合冻结线性化顺序；B持有有效lease期间不得被A恢复worker |
| F-L7 | 同PID两个scope，内层退出 | 仅移除内层lease，外层仍有效；resume=0直到最后退出 |
| F-L8 | 在登记/暂停确认/释放/恢复窗口中止；JSON损坏；锁超时 | 每点恢复结果与签署状态表一致；不得自动丢弃未知owner；明确失败和资源状态 |
| F-L9 | 初始user_paused或中途user_pause | 工具不会解除该暂停意图；显式下载允许与否按既有授权契约 |

### 本卡追加证据

- 每个调度的进程ID/leaseID/generation/monotonic事件；每步目录文件内容/hash；pause/resume spy日志；崩溃前后与恢复新进程证据

命令： T-FILING；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 锁协议变更或死锁；需kill未知PID；任何路径指向生产catalog；无法证明用户意图时停止自动恢复

### 恢复边界

- 只终止本卡登记的测试进程；保留临时owner状态供分析；回退代码不能删除生产所有权文件或主动resume

### 关闭标准

- 顺序、同PID、真实两进程、崩溃恢复与用户暂停五类均满足；高级并发reviewer独立读轨迹签收
