========================= card_I-08-A.md =========================
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

========================= card_I-08-B.md =========================
本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-08-B — 实际调用受信提供者并验证签名后才声明host_signed

父项：I-08。状态：planned；实施结果：未执行。角色：revenue 发布负责人（独立签名/事务 reviewer）。

依赖：I-08-A、I-00-C。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [scripts/revenue_core.py:113](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_core.py:113) — `attestation_capability`；SHA-256 `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae`。
- [scripts/revenue_core.py:128](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_core.py:128) — `run_forecast`；SHA-256 `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae`。
- [scripts/revenue_publication.py:120](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_publication.py:120) — `build_publication_receipt`；SHA-256 `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba`。
- [scripts/revenue_publication.py:185](C:/Users/郑曾波/Projects/revenue-forecast/scripts/revenue_publication.py:185) — `validate_publication_receipt`；SHA-256 `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba`。
- [scripts/contracts/evidence.py:270](C:/Users/郑曾波/Projects/revenue-forecast/scripts/contracts/evidence.py:270) — `_validate_host_signature`；SHA-256 `bc5e4c5305fad22f9c028fd989536d6529ef868698fb0adfcd9363b3e096208e`。
- [scripts/contracts/evidence.py:311](C:/Users/郑曾波/Projects/revenue-forecast/scripts/contracts/evidence.py:311) — `validate_host_receipt`；SHA-256 `bc5e4c5305fad22f9c028fd989536d6529ef868698fb0adfcd9363b3e096208e`。

### 允许改动

- 隔离 revenue_core.py、revenue_publication.py、contracts/evidence.py 及对应签名测试；仅按已定协议增加最小provider适配；禁止通用新签名框架

### 输入与独立预期

- I-08-A 固定协议；只用于新run临时目录的Ed25519测试密钥、受信名单、受控provider子进程；不读取实际私钥。
- fixture forecast_document()明确是合成fixture，不能因测试签名称真实capture；真实provider资格留后续I-16/I-17。

### 按序动作

1. 先加入任意存在文件的回归反例，确认修前错标host_signed；不用原probe_publication.py原地运行。
2. 将能力/签发拆清：文件可执行只可作为预检查，正式host_signed必须来自一次成功的协议调用及对所需证据链的有效验证。
3. 强验证成功后构造签署payload，按协议调用受控provider，验证响应schema/key/issuer/hash/domain/版本和签名；失败保持不受信或拒绝，依决策错误表。
4. 避免签名自引用：canonical payload排除哪些签名字段、result_sha如何绑定须严格依I-08-A；不能为了签名通过放弃现有receipt/hash门。
5. 更新旧test_configured_provider_means_host_signed_publication，改为明确协议fixture；不得在新实际调用逻辑下裸执行sys.executable等待输入。
6. 测试provider超时、非0、截断JSON、超长响应及合法签名；输出完整验证轨迹而不记录私钥。使用新scratch registry运行T-PUB。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| A-B1 | 普通.py存在，无可用协议；裸解释器路径 | 不会host_signed；受控超时/拒绝，无挂起，不以isfile通过 |
| A-B2 | 合法临时受信provider返回正确签名 | host_signed且验签成功；真实provider_invocations=1；payload、key、issuer、版本均对应 |
| A-B3 | 签名改1位；不受信key；错误issuer；payload改1字段 | 每个变异拒绝可信声明；正式可信登记=0 |
| A-B4 | provider timeout/nonzero/invalidJSON/oversize | 按冻结错误表失败关闭；不悄悄改成host_signed；时间/大小受限 |
| A-B5 | invalid input_document或强验证失败 | 签发调用0；registry新增0；F01/F02不回归 |

### 本卡追加证据

- 公钥fixture/指纹（不含私钥）、精确被签payload/响应/验签日志、进程调用计数、修前反例、T-PUB原始结果、全量数据/代码hash

命令： T-PUB；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- 信任名单来自同一响应且无外部锚；签名证明被扩大到历史capture；为通过而删F01/F02；普通解释器成为无界provider

### 恢复边界

- 仅回退隔离代码和测试配置；保留旧结果不改签名；失败输出不得被可信consumer接收；临时私钥按测试范围管理

### 关闭标准

- A-B1—B5通过；crypto正例和publication链共同验收；实现者不能自签真实provider已可用
