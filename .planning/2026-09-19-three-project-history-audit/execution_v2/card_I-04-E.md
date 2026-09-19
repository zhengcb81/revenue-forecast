本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-04-E — 保留嵌套错误与失败前真实副作用计数

父项：I-04。状态：planned；实施结果：未执行。角色：filing-fetch 负责人（wiki 并发 reviewer）。

依赖：I-04-B、I-04-D、I-02、I-03-D。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [scripts/fetch_filing.py:199](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:199) — `_run_company_wiki_json`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:251](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:251) — `_classify_wiki_error`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:622](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:622) — `_record_download_events`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/fetch_filing.py:938](C:/Users/郑曾波/Projects/filing-fetch/scripts/fetch_filing.py:938) — `_close_gap_and_return_handle`；SHA-256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。
- [scripts/filing_contracts.py:44](C:/Users/郑曾波/Projects/filing-fetch/scripts/filing_contracts.py:44) — `FilingFetchError`；SHA-256 `2d1b2e3374f1d0c255f94303d208f8657f54c9c32b3428e424f43e6a81ddc457`。

### 允许改动

- 隔离 filing fetch_filing.py、filing_contracts.py 的信封/计数及测试；wiki canonical error/event实现由I-02/I-03-D单owner提交

### 输入与独立预期

- 从I-02取得已签署错误taxonomy与真实阶段事件，输入样例至少含 code/retryable/request_id/stage/attempts/cause 及准确字段映射。
- fixture一：DB lock可重试；二：HTTP403，上游 retryable=true 必须原样结构化保留，是否自动重试另由冻结策略与 deadline 决定；三：本地请求schema错误；四：fetch=1/raw=1/register=0的部分失败。原始日志与结构体分别保存。

### 按序动作

1. 先固定stderr/stdout的机器信封契约；完整结构先解析再限长人类消息，日志前缀/大于2000字符不能将已知错误压成另一种fatal。
2. 改 close-gap 非completed 出口保留原cause/status/retryability/阶段而非只包装gap_not_closed；未知/损坏payload继续明确不可信，不伪造可重试。
3. 在每次子调用尝试和每个可信上游事件落账；失败返回也更新统计，不能只在合格handle返回后_record_download_events。
4. 定义累计与本次增量的去重键，避免重试读取同一envelope重复加数；不得把未知下载次数写0，应按I-02契约标未知并保留证据。
5. 用fake upstream的实际本地CLI协议测试 existing/missing/provider失败/注册失败/retry；配置显式指向新临时目录。不要直接运行当前 live 中文用例。
6. 运行T-FILING并与I-02事件对账；跨项目共享字段改变须由双方reviewer签收，再移交I-07真实CN403复核。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| F-E1 | 嵌套 db_timeout,retryable=true,request_id=R1；cause消息>2000字符 | machine code/retryability/R1/stage不丢；是否重试与预算一致；只展示文本可截断 |
| F-E2 | provider HTTP403（上游 retryable=true，本例冻结策略禁止本次自动重试，预算尚充足）与本地 invalid schema 两种 | 403 的原代码、stage、request_id、retryable=true 原样结构化保留；本例自动重试=0、上游调用=1，不能改写 retryable=false。schema 错误保持其独立代码与阶段；两者均不冒充 catalog 锁。另行获准的重试仍受冻结策略和 deadline 约束 |
| F-E3 | fetch1、raw_saved1、registration0后失败；同事件envelope再读一次 | 失败结果报告已发生副作用；累计不翻倍；不返回capture_ready |
| F-E4 | 上述失败后重试，仅注册成功；已有合格文件重复请求 | 两者本次新增fetch=0；部分失败恢复保留同raw hash；调用数与进程spy逐条对账 |
| F-E5 | 非JSON/未知错误或事件计数缺失 | 明确协议失败/计数未知，不伪造结构或0，不自动宽松重试 |

### 本卡追加证据

- 完整原始信封与人类日志；每attempt spy；上游事件ID与增量/累计对照；两次请求raw hash；隔离CLI stdout/stderr/exit

命令： T-FILING；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 上游尚无可靠事件字段；不能对账；需要把全部错误设retryable才能通过；发生生产provider调用

### 恢复边界

- 保留现有raw和原失败日志；回退信封变更但不以清零统计掩盖副作用；不重复下载替代注册恢复

### 关闭标准

- 5类正反例及I-02对账一致；真实provider未测必须继续未测，不能用本地CLI测试量代替
