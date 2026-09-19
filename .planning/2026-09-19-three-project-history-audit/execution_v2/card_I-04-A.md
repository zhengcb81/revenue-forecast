本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-04-A — 先定请求 deadline、清理预算和计时 oracle

父项：I-04。状态：planned；实施结果：未执行。角色：filing-fetch 负责人（wiki 并发 reviewer）。

依赖：I-00-A、I-00-B。

执行门：高级 reviewer 先定案；本卡不实施产品

### 现行源码锚点

- [scripts/fetch_filing.py:282](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:282) — `_run_company_wiki_json_retry`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:509](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:509) — `PausedWorkerScope._remaining`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:592](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:592) — `PausedWorkerScope.__exit__`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。

### 允许改动

- 仅本次决策和计时 fixture；不改生产 timeout 默认值/worker 状态

### 输入与独立预期

- reviews/filing/tests/pure_probes.json：deadline 10；模拟子调用消耗9并抛 catalog_busy；旧代码退避5，模型时钟到14。这不是第二次5秒调用或14秒墙钟。
- 独立数学 oracle：t0=0，deadline=10，首次返回t=9，则剩余=1；下一退避<=1；t>=10 不可新发请求。

### 按序动作

1. 高级 reviewer 列请求阶段（resolve/close-gap/status/pause 等）及每阶段是否计入同一 deadline；不用各段独立重置预算。
2. 确定必要恢复动作的单独 cleanup_budget 上限、何时可使用、总 elapsed 怎样分别报告；deadline 已过不等于放弃所有权恢复。
3. 确定 TimeoutExpired/取消/锁等待/退避/worker状态未知的错误语义；截止后不能通过 max(10,...) 新给请求预算。
4. 冻结真实时延测试预算 B、清理上限 C 和平台测量容差 epsilon；epsilon 来自运行环境测量/调度边界并独立批准，不因修后失败临时放宽。
5. 签署模型时钟和真实进程两套 oracle，包含原始 monotonic timestamps；每次子调用传入 timeout<=当时剩余预算，清理使用独立标签。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| F-D1 | clock 0→9，deadline10，jitter=0，catalog_busy | 最多再消耗1的退避；再调用数=0；模型请求结束时间<=10 |
| F-D2 | now100，deadline90，需要发 worker-status | 请求调用数=0；不得返回10秒请求预算 |
| F-D3 | 已由本scope暂停worker，期限耗尽 | 仍按独立清理预算处理所有权；不把清理耗时伪装为请求满足deadline，恢复失败明确记录 |

### 本卡追加证据

- 阶段预算表、C与epsilon选值及理由、超时/取消/恢复状态表、独立 reviewer 签署

命令： 本卡无产品执行命令；仅设计与独立审查。

### 失败停止条件

- cleanup上限/超时分类/实际容差尚未定；通过无限timeout规避失败

### 恢复边界

- 只退回本次决策版本；不暂停/恢复实际worker

### 关闭标准

- 每个阶段有唯一预算来源和记录规则；F-D1—D3 可在无服务环境模拟
