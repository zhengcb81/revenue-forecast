本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-03-D — 验证 close-gap 重检、完整候选范围及实际额度

父项：I-03。状态：planned；实施结果：未执行。角色：company-wiki 来源负责人（filing 为消费者 reviewer）。

依赖：I-03-B、I-03-C、I-02。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [src/company_wiki/source_catalog/close_gap.py:174](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/close_gap.py:174) — `CloseGapTransaction.execute`；SHA-256 `117c8166a6c26f3462574b787e0db79c419e00c8b18287f25738948032f475c3`。
- [src/company_wiki/source_catalog/close_gap.py:326](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/close_gap.py:326) — `CloseGapTransaction._fetch_and_commit`；SHA-256 `117c8166a6c26f3462574b787e0db79c419e00c8b18287f25738948032f475c3`。
- [src/company_wiki/source_catalog/authorization.py:99](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/authorization.py:99) — `validate_download_authorization`；SHA-256 `f858a369ed556d1b110be5ba7be7fa25ae3519fda94296cfe1c4f9e367d55f43`。

### 允许改动

- 隔离 wiki close_gap.py、authorization.py 的计划/额度边界与 contract 测试；canonical 原件保存/注册实现归 I-02 owner，禁止另造 writer

### 输入与独立预期

- 冻结计划、授权、runtime policy 副本；fake provider 按脚本返回 metadata 与内存 bytes；临时 catalog 由 tmp_path 创建。
- 先定义事件类型：provider_fetch_attempt、bytes_received、raw_saved、registration_succeeded，不能拿 fetch_events 一个数字替代全部；字段实现与 I-02 共享。

### 按序动作

1. 构造可运行的隔离 close-gap 调用，读取现有测试中的 fake adapters/staging 布局，不借用生产 config；测试先断言所有解析路径在 new_run_root 内。
2. 在首次 rediscover 后、锁内 rediscover 前插入确定性 barrier；变 URL/date/policy，验证旧 binding 在真实校验出口拒绝且未 fetch。
3. 依据 I-03-A 的单候选/有界批次选择落实 remaining_gap 语义；两个不同缺期必须可区分已完成与待补，不能选择 actionable[0] 后对全计划报完成。
4. 在 fake stream 每个 chunk 处记累计 bytes；未知远端大小按批准政策处理，收到超额度 chunk 必须停止、不得 commit 合格 handle，保留真实已收到字节计数。
5. 在返回 provider_error、空成功、scan/注册失败处观察最终结构；保持本地有效 raw 可恢复，具体重试注册由 I-02 实现。
6. 运行 isolated contract 用例并由 filing 消费者复核 envelope；真实 provider/生产写入留给 I-07，不用本卡 fake 通过覆盖。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| G-D5 | A0 绑定 P0；第一次发现后 URL/date/policy 变成 P1 | 锁内拒绝 stale binding；fetch_attempts=0；无新增 raw/注册 |
| G-D6 | 两个不同期间缺口，授权 max_items=1 | 最多发起1个获准对象下载；另一个仍为显式待补；不得宣称全部无 gap |
| G-D7 | max_bytes=100；fake chunks 60+60；remote_size 未知或谎报80 | 累计收到120须如实记录；到发现超额即停止，合格 handle=0/commit=0；不得声称物理从未收到>100，另记可能单chunk超额 |
| G-D8 | 下载1次并存 raw 成功，注册注入失败；随后重试 | 第一次失败保留 fetch=1/raw_saved=1/registered=0；第二次只恢复缺失注册，新增fetch=0（依赖 I-02） |
| G-D9 | provider异常 vs 空列表成功；本地有可复用旧件 | 前者最新性未知且保留原错误；后者按冻结语义，无虚假已发布/未发布断言；均不触发无授权下载 |

### 本卡追加证据

- 锁前/锁内两个计划及绑定 hash；fake provider 精确事件和收发字节；前后目录/catalog 快照；remaining_gap；I-02 恢复证据链接

命令： T-GAP；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 未授权流量；生产路径；为防重复写另建文件 registry；未批准选择多候选策略；要求修改 I-02 owner 文件而未协调

### 恢复边界

- 仅清理本次临时资源且保留失败证据；真实资产不触碰；隔离 raw 在失败时先保留后由恢复用例验证

### 关闭标准

- 单次与多缺口语义明确；重检/额度/部分失败均可观测；I-02 对应恢复项未完成时本卡不得关闭
