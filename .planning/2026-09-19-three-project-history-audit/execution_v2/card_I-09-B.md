本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-09-B — 实现完整包提交并让读者验证commit资格

父项：I-09。状态：planned；实施结果：未执行。角色：revenue 发布负责人（独立签名/事务 reviewer）。

依赖：I-09-A、I-08-B、I-00-C。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [scripts/revenue_core.py:128](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_core.py:128) — `run_forecast`；SHA-256 `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae`。
- [scripts/revenue_forecast.py:22](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_forecast.py:22) — `_atomic_write_text`；SHA-256 `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc`。
- [scripts/revenue_forecast.py:38](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_forecast.py:38) — `prepare_forecast`；SHA-256 `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc`。
- [scripts/revenue_forecast.py:55](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_forecast.py:55) — `main`；SHA-256 `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc`。
- [scripts/publication_registry.py:53](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:53) — `_read_entries`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:95](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:95) — `_append`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:188](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:188) — `is_registered`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。
- [scripts/publication_registry.py:193](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:193) — `audit`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。

### 允许改动

- 隔离 revenue_core.py、revenue_forecast.py、publication_registry.py 及I-09-A明确列出的现有读者/测试；公共receipt改动仅I-08 owner协作；禁止另造第四发布框架

### 输入与独立预期

- 固定fixture forecast_document()及I-08临时签名提供者；新run私有registry与包目录；初始P0完整已提交，P1与P0不同可见内容/hash。
- 将旧单文件atomic helper正例保留；新的独立oracle是consumer所见成员hash与commit状态，不是调用了os.replace。

### 按序动作

1. 先添加输出写失败registry不应成为可消费正式发布的反例；保存修前rc=2/新增1历史事实，不把旧测试改写成从未失败。
2. 按I-09-A划分prepare与commit：完成强验证/签名、生成全部成员与hash，在唯一commit点之前保持不可消费；不得简单把register移到最后却忽略第二文件/并发/崩溃。
3. 在批准锁内原子更新链尾/提交状态；保持现有hash链验证、generation区分、draft/forecast/snapshot差异，不将所有历史重复行视冲突。
4. 修改批准的reader，让prepare/abort/不完整包不能通过正式资格；旧格式按兼容表处理，不靠input_sha存在即接受任意result。
5. 实现幂等恢复所需最小持久记录；恢复前验证文件/hash/身份，不能补造缺失正式结果或重签改变历史。
6. 执行T-PUB与本卡正反例；I-09-C的kill恢复尚未验收前只标实施就绪，不宣称事务完成。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| P-B1 | 正常发布P1，包括JSON和请求的Markdown | commit完成后两个成员均完整并与manifest/registry绑定；reader只见一致P1 |
| P-B2 | JSON写入失败；或JSON完成而Markdown写失败 | 本次不形成可消费正式P1；existing P0仍按协议可用；rc与错误表一致（现CLI错误通常2） |
| P-B3 | registry写/flush失败 | 不会有可消费无registry资格的新包；残留prepare按协议可恢复，不报成功 |
| P-B4 | 同input不同result/generation、snapshot或draft条目；仅prepare条目 | 正式资格按完整身份/commit验证；保留合法不同generation历史；不能仅is_registered(input)通过 |
| P-B5 | 同一逻辑publication成功后重试 | 逻辑commit仍1；允许审计多行按协议计数；输出未篡改；不要求随时间签名字段必字节相同，按协议比较稳定载荷 |

### 本卡追加证据

- prepare/commit各状态原始记录、成员hash、reader输出、故障前后registry链验证、旧schema兼容、API调用结果、T-PUB日志

命令： T-PUB；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 读者可见半包；只顺序移动register没有恢复协议；绕过强验证/签名；I-09-A遗漏API语义

### 恢复边界

- 保留失败prepare与上个完整P0；隔离恢复按批准协议运行；禁止编辑历史hash链或清空registry回退

### 关闭标准

- P-B1—B5与原单文件安全测试通过；所有批准reader门生效；进入I-09-C但不提前给整体PASS
