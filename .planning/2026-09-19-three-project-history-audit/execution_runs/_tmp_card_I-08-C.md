本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-08-C — 验证消费者拒绝伪造、跨载荷重放和未签结果

父项：I-08。状态：planned；实施结果：未执行。角色：revenue 发布负责人（独立签名/事务 reviewer）。

依赖：I-08-B。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [scripts/revenue_publication.py:185](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_publication.py:185) — `validate_publication_receipt`；SHA-256 `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba`。
- [scripts/revenue_report.py:1196](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_report.py:1196) — `validate_published_forecast`；SHA-256 `a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f`。
- [scripts/revenue_report.py:1239](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_report.py:1239) — `validate_forecast_output`；SHA-256 `a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f`。
- [scripts/publication_registry.py:188](C:/Users/郑曾波/Projects/revenue-forecast/scripts/publication_registry.py:188) — `is_registered`；SHA-256 `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`。

### 允许改动

- 隔离 revenue 对应publication/attestation/pipeline测试；发现消费者门缺失时仅修改I-08-A已批准入口，scope外invest-*由其owner接卡

### 输入与独立预期

- 同一合成forecast的合法签名包S、明确unattested U、draft D；从S克隆变异，不能重新签名或调用生产helper重算expected。
- 通过CodeGraph在I-00-B记录实际消费路径，具体argv由调用点核定；本卡不凭空列invest命令。

### 按序动作

1. 冻结消费者集合及各入口的信任需求；分别记录能否展示、能否正式投资模块使用，不把普通只读查看和可信消费混在一起。
2. 经真实验证dispatcher调用 S/U/D；重放矩阵逐个变更input/result/schema/issuer/key/source事件或请求域，保持原签名。
3. 将伪造host_signed字符串与registry中存在同input anchor的组合送入消费者；检查不能仅凭label或is_registered(input)通过。
4. 保留合法历史S重复读取正例；只拒绝跨被签域滥用，不把历史签名验证改成一次性开销。
5. 检查F01/F02：输入不一致须在签发/发布前拒绝；输出校验使用embedded input强验证。运行T-PUB，附consumer调用轨迹。
6. 逐消费者签收；scope外消费者未测列出明确未完成依赖，不写全生态通过。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| A-C1 | S合法且所有哈希/受信域一致 | 要求签名的消费者通过；重复读取S仍通过 |
| A-C2 | U或D；或U仅改attestation_status=host_signed | 要求可信formal的消费者拒绝；普通查看按既定兼容规则，不伪造签名 |
| A-C3 | S跨input/result/schema/issuer/source-event重放 | 每个被签域变异拒绝；只重算非秘密hash不修复签名 |
| A-C4 | registry有同input的旧不同result；当前包缺合法绑定 | 不能因is_registered(input)=true接收当前伪包 |
| A-C5 | 合法S配不同input_document；或修改后保留旧verification context | 强验证拒绝；不触发新签发或登记 |

### 本卡追加证据

- 消费者清单/调用图、每入口的期望与实际、变异前后差异、S/U/D资格表、独立reviewer结论与scope外未验证项

命令： T-PUB；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 找不到某消费者真实入口；只测试验签helper却宣称消费者已接通；需改scope外仓库而无owner协调

### 恢复边界

- 保留旧可读文档；可信消费在不确定时拒绝并注明缺口，不通过关闭门恢复

### 关闭标准

- 所有已批准消费者入口实跑矩阵；无未验入口被标完成；F01/F02仍正确
