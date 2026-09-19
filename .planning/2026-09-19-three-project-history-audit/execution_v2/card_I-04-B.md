本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-04-B — 修复退避旧预算和 worker 最小10秒越界

父项：I-04。状态：planned；实施结果：未执行。角色：filing-fetch 负责人（wiki 并发 reviewer）。

依赖：I-04-A、I-00-C。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [scripts/fetch_filing.py:282](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:282) — `_run_company_wiki_json_retry`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:509](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:509) — `PausedWorkerScope._remaining`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:515](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:515) — `PausedWorkerScope.__enter__`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:592](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:592) — `PausedWorkerScope.__exit__`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。

### 允许改动

- 隔离 filing scripts/fetch_filing.py 中时间预算与对应 tests/test_fetch_filing.py；新计时测试仅新 run 临时服务脚本

### 输入与独立预期

- I-04-A 签署的 B/C/epsilon；旧 pure_probes.py 仅阅读并提取等价 fixture，绝不原地运行覆盖 reviews/filing/tests。
- 受控本地子进程只延迟与输出指定 JSON，没有任何 wiki/provider 连接；真实计时参数依 I-04-A 固定。

### 按序动作

1. 先在新用例重建 F-D1/F-D2 并保存当前失败；明确 mock time 是数学验证。
2. 在子调用返回/抛错后重新计算 remaining，再选择退避；请求预算耗尽立即返回已批准错误，不发后续调用。
3. 替换 _remaining 的请求最小10秒逻辑，按决策区分 request 与 cleanup；status/pause/resume 的日志均带阶段/预算类型。
4. 覆盖 success、catalog contention、nonretryable、取消与 timeout 路径；每次真实 subprocess timeout 与调用前 monotonic 剩余一致。
5. 运行本地延迟子进程用例，保存 start/end/call/sleep/cleanup timestamp；按签署 epsilon 核对请求和总 elapsed。
6. 运行 T-FILING，检查 deselected 的 live 中文用例确实未执行；测试命令若指向生产目录立刻中止，不靠 skip 的环境猜测。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| F-B1 | F-D1原反例 | 首次调用1次、退避<=1、无第二调用，模拟elapsed<=10；异常可含已耗尽的最后 catalog_busy 原因 |
| F-B2 | now100 deadline90；或只余0.2秒 | 前者请求调用0；后者传入timeout<=0.2，不强行10秒 |
| F-B3 | fatal/worker_paused，仍有充足预算 | 不自动重试；calls=1；保留原分类 |
| F-B4 | 受控真实进程耗时接近B，再busy；清理分支耗时<=C | request_elapsed<=B+epsilon；cleanup_elapsed<=C+epsilon；total分别报告，不能混作10→14模拟复现 |
| F-B5 | 首次立即成功，worker未运行/用户已暂停两种 | 无多余重试；按现有意图不启动或恢复用户worker |

### 本卡追加证据

- 修前/修后模型时钟轨迹；真实受控延迟轨迹；原始stdout/stderr/exit；每次timeout参数；请求/清理分项elapsed；deselection记录

命令： T-FILING；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 引入新最小timeout/偷偷加总B；真实时延容差未提前签署；发现依赖真实生产wiki

### 恢复边界

- 只回退隔离预算代码；所有模拟worker资源局限临时路径；不得以实际worker-resume收尾

### 关闭标准

- F-B1—B5和既有非live单测通过；模型测试与真实受控进程测试分别签收，不外推真实provider
