本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-04-C — 先冻结跨进程 lease、所有权与恢复协议

父项：I-04。状态：planned；实施结果：未执行。角色：filing-fetch 负责人（wiki 并发 reviewer）。

依赖：I-00-A、I-00-B、I-04-A。

执行门：高级 reviewer 先定案；本卡不实施产品

### 现行源码锚点

- [scripts/fetch_filing.py:465](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:465) — `PausedWorkerScope`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:565](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:565) — `PausedWorkerScope._register`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:579](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:579) — `PausedWorkerScope._unregister`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:592](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:592) — `PausedWorkerScope.__exit__`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。

### 允许改动

- 仅本次状态图、锁协议和调度表；不得弱模型自选文件锁库、数据库锁或重写worker

### 输入与独立预期

- 历史两线程强制read-before-write，各自 first=True，最后仅一个条目；只是逻辑RMW反例，未验证真实跨进程或OS tmp碰撞。
- 签署前统一词义：lease_id 与进程ID不同；owner generation 与 worker incarnation 不同；用户暂停意图优先于本请求自动恢复。

### 按序动作

1. 高级 reviewer 选择适合已支持 OS 的跨进程互斥实现、锁路径/顺序/超时，以及在原目录读写权限不足时的安全失败；不得仅使用 threading.Lock。
2. 定义 acquire/register/pause-confirm/join/release/resume-confirm 全状态和原子边界，特别是最后release与新acquire同时到达。禁止删除所有权证据后无条件resume。
3. 定义唯一 lease ID、同PID嵌套、PID复用检测、stale判断来源；进程探测异常不能等同已死亡；owner文件与entry文件兼容升级如何处理。
4. 定义崩溃窗口：登记后未pause、pause后未确认、最后释放后resume失败、损坏JSON；有歧义的用户意图和未知worker状态应 fail closed，不能自动当空列表。
5. 保留当前显式调用可在用户paused时获授权下载但绝不代用户resume的语义；外部用户在scope中再次pause必须能阻止旧owner恢复，若现有API无法识别则记录依赖并先协调。
6. 写固定调度脚本和每步expected lease集合/owner/action计数。锁内是否可等待CLI、如何避死锁需高级 reviewer 签署，弱模型只实现已选方案。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| F-L1 | A acquire、B acquire、A release、B release；初始running | 有效lease计数1→2→1→0；pause动作1；A退出resume0；B最后退出resume1 |
| F-L2 | 同PID的A/B嵌套；同PID但不同进程创建时间；锁竞争 | 不同lease可独立释放；不得按PID全删；不能复用失效owner资格 |
| F-L3 | 初始由用户paused、无本工具owner；执行获授权下载 | 不自动resume；与允许显式下载相容；不能把该允许路径误报成自动pause绕过 |
| F-L4 | 用户在scope中新增pause；owner JSON损坏；resume失败 | 不自动覆盖用户意图；损坏不能按无owner处理；失败保留可恢复诊断，不伪称已恢复 |

### 本卡追加证据

- 锁选择ADR、状态转移表、线性化点、锁顺序、损坏/过期恢复规则、4个调度精确oracle、支持平台范围

命令： 本卡无产品执行命令；仅设计与独立审查。

### 失败停止条件

- 跨进程锁/用户意图token尚未有方案；试图启用生产worker验证；另造wiki调度系统

### 恢复边界

- 不迁移生产lease文件；决策不成立则保留旧问题未关闭

### 关闭标准

- 高级并发reviewer批准所有故障窗口；需要wiki API变更时由该owner补依赖后才进入I-04-D
