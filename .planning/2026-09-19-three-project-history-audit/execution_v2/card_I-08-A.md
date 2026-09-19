本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-08-A — 先定签名信任域、提供者协议及旧版本边界

父项：I-08。状态：planned；实施结果：未执行。角色：revenue 发布负责人（独立签名/事务 reviewer）。

依赖：I-00-A、I-00-B。

执行门：高级 reviewer 先定案；本卡不实施产品

### 现行源码锚点

- [scripts/revenue_core.py:113](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_core.py:113) — `attestation_capability`；SHA-256 `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae`。
- [scripts/revenue_core.py:128](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_core.py:128) — `run_forecast`；SHA-256 `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae`。
- [scripts/revenue_publication.py:120](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_publication.py:120) — `build_publication_receipt`；SHA-256 `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba`。
- [scripts/revenue_publication.py:185](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_publication.py:185) — `validate_publication_receipt`；SHA-256 `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba`。
- [scripts/contracts/evidence.py:270](C:/Users/郑曾波/Projects/revenue-forecast/scripts/contracts/evidence.py:270) — `_validate_host_signature`；SHA-256 `bc5e4c5305fad22f9c028fd989536d6529ef868698fb0adfcd9363b3e096208e`。

### 允许改动

- 仅本次协议/信任域决策；不生成生产密钥、不改受信名单、不开放新网络服务

### 输入与独立预期

- 历史普通存在.py文件被判capability=true且unsigned被标host_signed：reviews/revenue/logs/publication_probe.stdout.txt；脚本只读。
- 现有 _validate_host_signature 已对提供的Ed25519签名做whitelist验证，缺口是publication标签/调用链，不得声称现有密码验证全不存在。

### 按序动作

1. 高级 reviewer 区分原始capture事件签名、host receipt签名、forecast publication签名；列每层证明的事实。后加出版签名不能凭空证明旧raw曾由可信工具取得。
2. 在现有证据schema上选择最小协议：请求/响应传输、canonical payload字段、issuer/key ID/版本、input/result/receipt绑定、domain separator、nonce/request ID/重放边界。
3. 明确可重复验证历史签名与跨payload重放的区别；同一immutable artifact重复读取不应因签名曾使用过而失效；新请求能否复用签名按已签字段判。
4. 选择受信key/issuer来源、只读权限、轮换与撤销规则、provider身份约束、超时和输出大小限制；弱模型不得自行实现自签自信任或引入网络钥匙服务。
5. 决定无provider、普通文件、provider失败、缺私钥、旧unsigned formal/draft的行为；既有unattested可以保留研究结果，但不得升级host_signed或穿过要求签名的消费者门。
6. 固定F01/F02回归：验证先于签发/登记，当前input_document绑定走强验证；列消费者签名验收入口与最小修改范围，scope外入口由owner补卡。
7. 签署协议文档、测试key fixture使用范围、旧版本可读/可信分类与错误表，之后I-08-B/C才能实现。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| A-D1 | provider环境变量指向任意存在.py或sys.executable，无协议响应 | 不得host_signed；失败或明确unattested按签署决策，不靠存在性判断 |
| A-D2 | 合法受信key签名正确payload；同签名复制到不同input/result/schema/issuer | 原件verify通过，变异全部拒绝；历史同artifact重复验证允许 |
| A-D3 | unsigned旧source receipt + 新publication签名 | 不得声称原capture具备先前不存在的可信签名；信任范围明确受限 |
| A-D4 | invalid输入或篡改input_document | provider调用0、registry新增0；保留F01/F02已修顺序 |

### 本卡追加证据

- 签名payload的精确字节规范、key/issuer信任域表、协议与限额、兼容及重放表、F01/F02定位、独立安全reviewer签署

命令： 本卡无产品执行命令；仅设计与独立审查。

### 失败停止条件

- 签名范围/旧包兼容/密钥来源未定；只有文件存在探测；测试私钥被当生产信任

### 恢复边界

- 不修改生产密钥/名单/结果；旧unsigned档案保留原标签，不重签伪造历史事件

### 关闭标准

- A-D1—D4都有固定消费者预期；provider协议和信任域无未决；新schema不绕过强验证
