本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-09-C — 逐边界故障注入、并发与重启恢复独立验收

父项：I-09。状态：planned；实施结果：未执行。角色：revenue 发布负责人（独立签名/事务 reviewer）。

依赖：I-09-B、I-08-C。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [scripts/revenue_forecast.py:55](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_forecast.py:55) — `main`；SHA-256 `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc`。
- [scripts/publication_registry.py:95](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:95) — `_append`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:53](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:53) — `_read_entries`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:127](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:127) — `register_publication`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:188](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:188) — `is_registered`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:193](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:193) — `audit`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。

### 允许改动

- 仅隔离的publication transaction测试/本次故障harness；发现产品问题退回I-09-B修，不能测试者绕过产品入口

### 输入与独立预期

- 每个故障点独立新目录与同一P0/P1输入；I-09-A冻结故障点与返回码oracle；两真实本地进程与只读consumer进程。
- 测试必须包括真正进程中止，Python finally不会运行；patch OSError仅证明异常路径，不代替崩溃持久性。

### 按序动作

1. 为签署故障表逐点建立barrier/故障注入hook，只在测试构建启用；在代码中定位hook后由独立reviewer检查不改变正常提交顺序。
2. 分别注入OSError（写/flush/fsync/replace/registry）、到点终止发布子进程、恢复中再终止；只能终止new_run manifest记录的测试PID。
3. 每个点由全新reader进程读取并记录可见包成员/hash/commit资格；不得仅看写者返回值，不能只确认无tmp文件。
4. 由新的恢复进程重复两次恢复，检查幂等、hash链、未误删P0、未凭空生成P1；保留孤儿prepare的明确不可消费状态。
5. 并发两个相同publication与两个不同publication；消费者持续观测，核对锁、链尾、逻辑commit数量和允许的审计历史行。
6. 运行真实CLI的JSON+Markdown、stdout-only、直接库API及snapshot兼容测试，全部在隔离registry；冻结语义不支持的组合明确拒绝。
7. 独立reviewer按原用户完整包要求签收；只在本卡scratch验证的结果不能签成生产部署资格。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| P-C1 | prepare前后、JSON完成、Markdown完成、registry持久化前后、commit前后、返回前逐点kill | 按冻结表仅P0或完整P1可消费；无混包；未commit的P1资格为false |
| P-C2 | P1已commit后响应丢失，再重试同幂等请求 | 逻辑P1=1；返回/恢复可定位同发布；允许历史行数不误报重复bug |
| P-C3 | 两进程同时从同链尾提交；另一个reader连续读 | 链无分叉/断裂；无丢失提交；reader不会接受半行/未commit为正式包；允许短暂忙/重试按契约 |
| P-C4 | 恢复中再次kill；损坏prepare或成员hash；完整P0存在 | 再次恢复幂等；损坏项fail closed且保留诊断；P0不被删除或改写 |
| P-C5 | stdout pipe失败、直接API、validate-only、snapshot历史 | 各按冻结兼容矩阵；validate-only无发布写；stdout失败不伪称跨终端事务回滚 |

### 本卡追加证据

- 每故障点独立run_id/输入/代码hash、hook位置与触发轨迹、PID证据、原始returncode及expected分离、reader观测、两次恢复结果、registry链全检与提交计数

命令： T-PUB；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 测试kill涉及未登记PID；底层持久性不满足已宣称平台保证；需要删历史行；只测异常不测真正退出

### 恢复边界

- 只停止测试进程并保留scratch证据；恢复上一个完整测试包；真实registry/用户包绝不触碰；失败退回I-09-B并保留反例

### 关闭标准

- 故障表逐行签收无缺格；两进程并发与全新reader/recovery成立；旧功能兼容与签名链通过；生产I-16/I-17仍单列待验

## 只读历史证据入口

- [reviews/cross_history/current_recheck.json](C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/cross_history/current_recheck.json)
- [filing/tests/pure_probes.json](C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/filing/tests/pure_probes.json)
- [revenue/logs/publication_probe.stdout.txt](C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/revenue/logs/publication_probe.stdout.txt)
- [reviews/revenue/probe_publication.py](C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/revenue/probe_publication.py)

每卡完成需其completion_criteria、共用证据包及独立reviewer收据同时具备。本文全部status=planned/execution_result=null；测试命令是经绑定后才可用的参数数组模板，不是本轮已执行结果。
