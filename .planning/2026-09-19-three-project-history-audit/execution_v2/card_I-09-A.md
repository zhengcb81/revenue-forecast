本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-09-A — 先定结果包提交、读可见性与幂等协议

父项：I-09。状态：planned；实施结果：未执行。角色：revenue 发布负责人（独立签名/事务 reviewer）。

依赖：I-00-A、I-00-B、I-08-A。

执行门：高级 reviewer 先定案；本卡不实施产品

### 现行源码锚点

- [scripts/revenue_core.py:128](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_core.py:128) — `run_forecast`；SHA-256 `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae`。
- [scripts/revenue_forecast.py:38](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_forecast.py:38) — `prepare_forecast`；SHA-256 `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc`。
- [scripts/revenue_forecast.py:55](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_forecast.py:55) — `main`；SHA-256 `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc`。
- [scripts/publication_registry.py:95](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:95) — `_append`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:127](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:127) — `register_publication`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:162](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:162) — `register_snapshot`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:188](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:188) — `is_registered`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。

### 允许改动

- 仅本次事务协议/迁移/故障矩阵；不改正式registry，不删除历史记录

### 输入与独立预期

- 历史反例：run_forecast先登记，随后_atomic_write_text失败，CLI rc=2但registry已增加1行且无输出：reviews/revenue/logs/publication_probe.stdout.txt。
- 现有每文件temp+fsync+replace仍是有效窄修复；现有同输入两运行=两条审计历史不是必然重复发布bug。

### 按序动作

1. 高级 reviewer 决定一个publication的身份：input/result/engine/schema/artifact_type与包目标怎样参与；逻辑幂等重试与允许重复审计行分别定义。
2. 定义必需结果成员：JSON、可选Markdown、receipt/manifest；输出参数缺省(stdout)与直接run_forecast库调用没有文件路径时的提交语义。不可偷偷把library行为改成未登记还称正式。
3. 在现有实现上选择最小prepare/commit/recovery或等效协议；明确唯一commit点、崩溃一致性假设、文件与registry跨卷限制、Windows rename/fsync可保证范围。弱模型不得自选SQLite/manifest/新数据库架构。
4. 明确读者只消费committed且各成员hash一致的版本；哪些现有lookup/is_registered/audit/backtest入口需更新、旧append行如何解读但不伪造commit资格。
5. 选择跨进程提交串行化/锁与链尾更新方式，列同一/不同publication并发；_append读链尾再append的原子性必须包含在协议。
6. 签署故障点表：prepare前后、JSON持久化、Markdown持久化、registry append/flush、commit可见前后、回执返回前、恢复再崩溃；每点给可见版本/返回码/恢复动作。
7. 定义旧包保留和撤销策略；no-output/stdout输送失败的可达保证单列，不能承诺对终端stdout和磁盘做不可能的共同回滚。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| P-D1 | 新包输出失败，初始无已提交包 | 消费者可见新正式包数=0；registry即便有prepare事件也不被is_registered等当committed |
| P-D2 | 已有P0；写P1第一或第二文件失败 | 消费者继续见完整P0或明确不可用，绝不见P0/P1混包；恢复可验证，不覆盖历史 |
| P-D3 | P1 commit后返回前崩溃，再以同幂等身份重试 | 逻辑committed P1=1；审计行数可>1但含义由签署协议限定 |
| P-D4 | 库API无输出路径、stdout-only、snapshot与forecast共registry | 分别有明确语义/兼容规则；不得误把snapshot或draft当已提交formal包 |

### 本卡追加证据

- 状态图/唯一commit点/reader契约/幂等键、平台持久性假设、API兼容矩阵、逐故障点固定oracle、独立事务reviewer签署

命令： 本卡无产品执行命令；仅设计与独立审查。

### 失败停止条件

- stdout/API语义未定；试图一次rename跨卷实现假原子；欲删旧registry造绿；锁/恢复尚未定

### 恢复边界

- 仅修改本次设计文档；旧包/registry只读；不预先迁移生产历史

### 关闭标准

- P-D1—D4和全部故障点无未决；I-08信任状态与提交状态独立且一致；后继卡绑定决策hash
