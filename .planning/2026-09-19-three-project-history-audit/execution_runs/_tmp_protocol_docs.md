============================== START_HERE.md ==============================
# 执行包 v2：一次只做一张已具备前提的卡

状态：文档细化；产品实施未开始。本包落实[总纲](../implementation_plan.md)，不取代其原义务，也不继承旧 PASS。适用执行者是不熟悉三仓历史的模型。读完全文不是开工许可：先绑定当前版本、隔离环境和命令，再由调度者释放具体卡。

## 先读这四项

1. 本文；它定义统一执行方法，不要求执行者阅读全部769份历史。
2. [调度表](dispatch.md)：只拿指定的一张卡及其必读文件，依赖未满足时返回blocked，不猜前提。
3. 该卡正文及所指的原证据；执行者自己完整读到关键字段，不能只看上个模型的总结。
4. [独立验收与接续](review_and_handoff.md)：完成后交证据，不由实现者自行宣布最终通过。

本轮只新增计划、样本定位和静态校验材料，不启动provider/worker，不写生产catalog，不替用户作投资结论。未来实施沿用明确授权；本文不会凭空增加一次用户审批，也不会替代必须具备的专业设计和环境前提。

## 当前可以委派什么

当前所有产品卡为planned。I-00-A可从只读基线清点开始；其余先满足依赖。`planned`不是`ready`。每张卡的步骤已经具体化，但尚未绑定未来实施时的checkout、解释器、测试nodeid、安装目录和配置指纹；这些会变化，不能在文档里伪造固定值。

调度者为每次尝试创建单独目录 `execution_runs/<card-id>/<attempt-id>/`，不得覆盖本次审计证据。只用普通文件，不引入新的产品状态机。下述状态只描述工作记录：

| 记录状态 | 进入依据 | 不能替代的条件 |
|---|---|---|
| planned | 有卡片与原义务 | 不表示依赖满足 |
| blocked | 缺样本/专业决定/能力/授权或环境不一致，列出具体原因 | 不能算通过或自动豁免 |
| ready | 指定活动的依赖、设计、绑定和允许范围已满足；记录activity=read/edit/run | 不表示已修改或已测试；允许编辑不等于未绑定命令可运行 |
| implementing | 执行指定步骤，保留日志 | 不允许修改oracle来贴合结果 |
| review_pending | 正反例/恢复/差异证据齐全 | 实现者不能自签accepted |
| accepted | 独立reviewer读证据并复验必要反例 | 仅该卡的明示资格，不外推到产品/预测准确性 |

依赖项标记accepted还不够：它的代码/config/schema/sample指纹必须与本次输入兼容。任一实质变化使受影响的下游卡重新核验，不把所有已做卡一律作废，也不自动继续继承。

## 固定九步执行法

1. **领取**：记录card-id、parent、实现者、独立reviewer及任务目标；复述该卡的一个可观察结果。一次只改该结果涉及的范围。
2. **绑定**：按I-00-B先做编辑前绑定，写`binding.json`中的三仓实际路径、相关文件sha256、解释器、cwd、配置/安装/模块路径、允许写目录和输入hash。已核准的新接口/测试可以尚未存在，标为planned，不因它未实现而禁止获准范围内写代码。实现后再绑定其真实argv/nodeid及副作用，才允许运行。路径存在但不属于隔离目录时停止。
3. **读证据**：读取卡片定位的源文件/函数、现行测试、原反例。使用CodeGraph定位结构；位置漂移时重新定位、记新hash和差异，不能照旧行号改错文件。
4. **冻结预期**：在`oracle.md`写正例、每个负例、预期错误语义/输出/持久化后果。数值预期手算或来自独立披露，不能调用被测函数先生成expected。专业决策未定先blocked。
5. **运行修改前检查**：只在已绑定隔离环境按`commands.json`执行。缺陷若当前已修，保留证据，走“无需代码修改的复验”，不故意造一个RED。若不能复现，解释版本/环境差异，不能偷偷换反例。
6. **最小修改**：只改allowlist与关联最小测试；不改旧收据、历史raw、预期样本、门槛或历史完成表来消除失败。公共契约需跨仓消费者测试，不能只改producer。
7. **修改后检查**：同一输入重跑正反例，再跑卡片要求的实际CLI/跨进程/恢复/幂等检查。原始退出码、expected退出码、业务判定分开；跳过、超时、未采集不是通过。
8. **交审**：提交diff、完整输出、数据/事件前后差异、恢复证据、未满足项。非预期修改立即停止；保留现场，由owner撤回本次差异，不reset/stash用户原改动。
9. **接续**：reviewer接受后，更新该卡范围和下一卡；不按完成卡数解锁上级。写明第一条未完成动作，下一模型从该动作继续。

## 允许弱模型自行决定与必须交专业审查的边界

可自行决定：局部变量命名、遵循仓库现有风格的小重构、已冻结断言的实现、已规定输入的运行与证据收集。不得据此扩大allowlist。

以下先写`decision.md`，由对应专业reviewer给出明确选项及理由，之后再实施：跨进程锁与崩溃恢复机制；发布包事务边界；审核writer与producer契约变更；财期/重述/收入总净额和payability归属；不可识别模型参数；样本/基准/统计阈值及概率校准；部署迁移和自然观察资格。审查意见至少包含选择、理由、反例、兼容影响、恢复规则、拒绝的替代方案。不得用“按最佳实践”代替决定。

这类交接是专业工作分工，不是每一步都向用户索要确认。用户已有授权的可逆工作继续；只有必要信息/授权确实缺失且无法独立解决时才报告用户。

## 命令不能猜

本包中的代码路径是定位锚点，不自动成为允许运行的命令。所有产品命令必须先在I-00-B绑定：

```json
{
  "id": "one-stable-command-id",
  "purpose": "具体测试案例ID与所证命题",
  "cwd": "绑定后的绝对隔离仓库路径",
  "argv": ["绑定后的python绝对路径", "-X", "utf8", "-B", "已核查脚本或-m", "已核查参数"],
  "config_paths": [],
  "allowed_write_roots": [],
  "network": "disabled或具体provider",
  "timeout_seconds": null,
  "expected_returncode": null,
  "expected_business_result": "原文描述",
  "before_after_evidence": [],
  "binding_status": "unbound"
}
```

这是模板，含null/unbound不能运行。绑定分两阶段：实现前冻结现有基线入口、设计和允许编辑文件；新接口先记录预定契约/文件及状态planned。实现后读取真实代码和参数，将新命令改为bound，再运行验证。不能要求新功能存在才允许实施它，也不能反过来猜命令运行。若CLI忽略隔离路径，先修隔离/依赖注入能力，不能在生产上试。以argv数组传参，保留UTF-8，不拼接含公司名的shell字符串。`--help`也需先确认导入没有写库/起worker副作用。收据中的外层runner退出0不能覆盖子命令失败。

每次命令使用独立command-run-id目录，包括修改前/后和重复运行；`pytest --basetemp`可能清理目标，因此只绑定到本次新建空测试目录，不能指向attempt根、证据根或上次测试目录。先保存原始状态/输出，再进行下一次命令。

## 无法完成时的确定动作

- 源码/契约已漂移：停止本卡写入，提交新旧hash及差异；调度者更新受影响绑定，reviewer重审oracle。
- 缺真实样本/外部provider不可达：保留对应case为blocked；隔离测试可以继续，live资格不继承。
- 已下载未注册：保留raw与sidecar，只修/重试注册，不重新下载绕开问题。
- 并发或事务反例失败：保留scratch现场、日志、锁/进程信息；禁止在真实worker/registry上重演。
- 研究假设没有依据：标缺口或用明确fallback；不补假经营数据或把主观情景称统计区间。
- 两次相同失败：先比较失败原因与绑定，停止同命令盲重试；提交接续记录，由owner定位，不能无限消耗预算。

## 本包的完成边界

结构检查、独立干读只能支持“文档覆盖和可读性”。弱模型真正可执行性仍需按[试执行方案](pilot.md)在隔离副本验证；本轮没有进行产品实现试验，也没有证明准确性改善。


## rc 码表（冻结；owner 裁定 T1-19 / §13）

同一批内 rc 语义必须自洽，但**跨批历史 rc 不回改**。今后各批**必须**在自身证据里带一份
自描述 `exit_code_legend`，并在 `commands.json` / `case_results.json` 中按本表归类。

**冻结码表（本包唯一规范值）**

| rc | 含义 | 判据 |
|---|---|---|
| `0` | 通过 | 命令正常结束，且**业务判定为通过**（外层 runner 退出 0 不能覆盖子命令失败） |
| `1` | harness 失败 | 测试/运行器自身出错：导入失败、夹具错误、期望文件缺失、路径未绑定 |
| `2` | 无裁决 / 预期拒绝 | 用例是负例且**业务上被正确拒绝**；或该命令不产生裁决（如只读查询） |
| `3` | 未达预期 | 正例未通过，或负例**未被拒绝**；即"应红未红 / 应绿未绿" |

**已知的历史偏差（只登记、不回改）**

- M05–M08 用 `2 = harness`。
- M09–M16 等用 `1 = harness / 2 = no-verdict / 3 = negative`。
- ⇒ 同一个 `rc=2` 在两类批里语义不同。**跨批聚合前必须先读该批的 `exit_code_legend`**，
  不得假设码表一致。历史 rc 与其证据**一律不动**。

**与 runner 推广的四项前置的关系（T1-8）**

`expected` 只能是**裸类型名**（如 `'ModelRegistryError'`）；复合写法（如
`"ModelRegistryError/continuity"`）会假红。当前 `cases.json` 缺 `expected` 时的归类
（现为 `rc=3`，而登记口径写 `rc=2`）须先按本表**统一到 `rc=2`**，再推广 runner。

============================== common_filing_cards.md ==============================
# I-03 / I-04 / I-08 / I-09 逐卡执行说明

**状态：全部 planned，实施未执行。Markdown 为执行权威正文；JSON 供 dispatch/校验。**

仅 I-03/I-04/I-08/I-09 的未来执行卡。本次未实施、未运行产品/测试、未下载、未写生产DB/worker/registry；仅此JSON与同名Markdown新增。

先CodeGraph定位定义/调用，再读已定位源文件并用Python AST只读核准精确行号/hash。CodeGraph部分行号落后，以下锚点以现行字节为准。

## 共用前置与边界

- 每卡先读取I-00-A/B/C及自己的依赖验收收据；planned不是可执行授权或完成。高级决策卡仅写设计收据，未签署不得实施。跨分区parent依赖由主审dispatch映射到实际卡，不由弱模型猜字母。
- 使用I-00冻结的隔离checkout/解释器/依赖；不覆盖用户dirty文件，不reset/stash主树；所有新增输入、日志、临时catalog、keys、registry、worker模拟文件放在新的new_run_root内。先检查绝对路径前缀，禁止生产公司根/正式registry/旧审计reviews路径。
- 逐个比较本卡源锚点sha256与当前待实施版本；不同即读差异和后继修复，让reviewer确认新基线，不能按旧漏洞重复修已修代码。这里只冻结规划时版本，不要求长期字节不变。
- 卡内“先重现修前失败”“确认修前错标”等动作，仅在当前冻结版本仍存在该缺陷时适用。若后继修复已关闭缺陷，则走无代码变更的原反例复验，记录修复版本与证据；禁止回退有效修复、改坏输入/实现、放宽或篡改断言来人为制造 RED。复验已通过且范围完整时可按无代码变更关闭该实现步骤，未覆盖范围仍保留待验。
- 执行命令模板前由I-00-B把占位解释器、cwd、argv、环境、输入hash与测试节点绑定到新run；复制原probe前先移除其固定旧证据写路径，不执行原脚本覆盖历史。
- 测试分级明确：pure fixture、真实代码本地跨进程、生产配置副本、真实只读数据、真实provider、生产写入。此分区最多前三类且本卡说明更窄；真实provider/安装态用户旅程归I-07/I-16。
- 凡跨项目公共schema、canonical writer、registry或worker API，只有指定owner写；发现scope外必要改动先记录阻断并交owner补卡，不能为绿灯建立平行框架。

### 每卡共同证据

- 新run唯一目录；卡ID、依赖收据hash、原义务及历史反例链接、源码/配置/解释器/实际导入路径hash、dirty清单。
- 输入实际字节/来源、手工独立expected和推导、完整stdout/stderr、raw_returncode、expected_returncode、判定分别记录；测试tier、collected/selected/passed/failed/skipped/deselected分别记录。
- 按本卡要求保存事件/调用/读写/elapsed/状态前后证据；断言不可仅为fileexists、计数或receipt.status=pass。
- 实现者与独立reviewer分别署名；未验和scope外项单列；失败保存原始输入和输出，不能换fixture/公司/口径以保持PASS。

### 禁止事项

- 本轮不执行卡、不改产品代码、不访问真实provider、不改变worker暂停状态、不迁移或清理公司数据湖。
- 未来实现卡不能把测试私钥、fake provider、模拟时钟、模拟PID或fixture-only PASS写成生产/真实市场验收。
- 不修改reviews/下任何历史产物；不运行会固定写入旧scratch/log的pure_probes.py、probe_publication.py或current_recheck.py。只读原脚本和结果。
- 保留已修F01/F02、capture_ready拒绝、有效Ed25519验签、单文件atomic replace等窄正确性；不重开已退役旧研究writer。

## 命令模板（本轮未执行）

占位符必须由 I-00-B 解析为审核过的绝对路径与 argv；不能把模板当现成新 CLI。每个模板的 expected_returncode=0，只对应测试框架成功退出；新增案例仍须逐项验收。不要为了通过而直接运行原历史探针，它们会写回自己的旧 scratch/log。

### T-GAP

已存在wiki contract测试的最小回归入口；不包括未来尚未创建用例的命令

cwd: `<isolated_company_wiki_checkout>`

argv（结构化，不拼接 shell）：

```json
[
  "<I-00-B核定的python>",
  "-X",
  "utf8",
  "-B",
  "-m",
  "pytest",
  "tests/contract/test_source_catalog_gap_plan.py",
  "-q",
  "-p",
  "no:cacheprovider",
  "--basetemp=<new_run_root>/gap-pytest"
]
```

- 已读该版本conftest/测试，确认fake adapter/temp catalog且无生产默认根
- new_run_root是新建绝对路径，不等于旧审计目录
- 新增测试node由I-00-B在创建后绑定；本模板通过不等于新增反例已覆盖

### T-FILING

已存在filing测试文件中排除实际生产wiki依赖的用例

cwd: `<isolated_filing_fetch_checkout>`

argv（结构化，不拼接 shell）：

```json
[
  "<I-00-B核定的python>",
  "-X",
  "utf8",
  "-B",
  "-m",
  "pytest",
  "tests/test_fetch_filing.py",
  "-q",
  "-p",
  "no:cacheprovider",
  "-k",
  "not test_cli_stdin_accepts_utf8_chinese_query",
  "--basetemp=<new_run_root>/filing-pytest"
]
```

- 源tests/test_fetch_filing.py:1438的中文stdin用例直接连接PRODUCTION_WIKI且无显式config，必须排除（历史继承会收集两次）；不能依赖它自动skip
- 逐版检查其余测试与conftest无新增live路径；实际deselected数量记录不硬套旧数
- 未来本地CLI模拟harness需先独立审路径隔离，禁止拿此live用例改公司名运行

### T-PUB

已存在revenue发布/签名/registry/单文件事务测试

cwd: `<isolated_revenue_forecast_checkout>`

argv（结构化，不拼接 shell）：

```json
[
  "<I-00-B核定的python>",
  "-X",
  "utf8",
  "-B",
  "-m",
  "pytest",
  "tests/test_publication_pipeline.py",
  "tests/test_publication_registry.py",
  "tests/test_attestation.py",
  "tests/test_zr710_publication_txn.py",
  "-q",
  "-p",
  "no:cacheprovider",
  "--basetemp=<new_run_root>/publication-pytest"
]
```

环境约束：

```json
{
  "REVENUE_PUBLICATION_REGISTRY": "<new_run_root>/registry",
  "REVENUE_ATTESTATION_PROVIDER": "只在已批准fixture中设置；不得继承真实provider",
  "REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS": "<new_run_root>/测试公钥名单（若该用例需要）"
}
```

- 已读tests/conftest.py，会把registry重定向到tmp_path_factory；必须记录实际最终路径，不能只看外层env
- 原test_attestation.py:71把sys.executable当provider；真正调用协议前必须改为已批准有界fake provider，避免裸解释器挂起
- 旧ZR710仅证明单文件写/registry先失败，不可用其数量宣称整体提交已完成
- 所有测试新增hook/kill限已登记测试进程，不能操作真实worker


本文仅共用前提；领取具体卡见[调度表](dispatch.md)。

============================== review_and_handoff.md ==============================
# 独立验收与上下文接续

每张执行卡使用这里的共用验收步骤；卡片里的专属oracle不可被这里的格式检查替代。

## reviewer固定操作

1. 先读parent I-xx原义务和具体卡；比较本次实际范围。被移出范围的要求必须保留独立待办与依赖，不因拆卡消失。
2. 不先看实现者“通过”摘要；先看输入/源/config/安装指纹、命令、raw退出码和原始输出，再看业务结果。
3. 对比修改前与修改后同一反例。若反例已修，检查是否确实是同一攻击面，接受无需修改的局部复验；不要求人为失败。
4. 复算至少一个卡片专属oracle。expected从被测函数、同一parser或同一helper生成的，一律不能视为独立验证。
5. 从输入维度预先保留一个实现者未用于编写修复的变化案例：例如另一root名、不同修订ID、另一并发时序、不同单位。审查前记录其预期与hash，不看运行结果后选样。不要求秘密传输，也不把未披露要求事后加给实现者。
6. 对状态性卡检查异常后重启/重试和最终持久化，不仅检查异常是否抛出。恢复必须在隔离目录，验证仍可使用上个完整版本。
7. 若卡涉及跨仓入口，至少一次从消费者真实入口到目标后果；mock/helper测试不能替代。明确network/fixture/live层级。
8. 检查allowlist外diff、读取内容与仅选择角色、调用事件与产物事件、elapsed与自然时间、公式正确与准确性分开。
9. 写结论：accepted_scoped / changes_required / blocked / not_applicable_with_reason。列资格与未获资格；只有原义务明确不适用且有依据时可标NA，不能把缺样本标NA。

## 交付最小目录（未来实施时创建）

```text
execution_runs/<card-id>/<attempt-id>/
  binding.json       # 当前代码、配置、输入、隔离目录
  decision.md        # 如需专业设计；无则明确不适用原因
  commands.json      # 每次调用的argv/cwd/timeout/预期
  oracle.md          # 运行前冻结的独立预期
  before/           # 修改前原始日志、状态与hash
  after/            # 修改后原始日志、状态与hash
  recovery/         # 异常后恢复；纯函数可说明NA
  changes.diff      # 仅本次允许修改，与既有dirty分离
  review.md         # 独立结论和保留案例
  handoff.json      # 下一次从哪里继续
```

不能仅交文件名/hash；reviewer需读实际内容。不得执行本轮历史审计脚本后覆盖其旧checks.json来冒充新证据，复制逻辑到新attempt输出目录并绑定当前代码。审计脚本若内嵌旧路径，先做只读检查及路径替换审查，不能直接运行。

## handoff字段与接收动作

`handoff.json`必须有card_id、attempt_id、status、completed_steps、next_step_number、next_action、input_hashes、current_source_hashes、changed_paths、commands_executed、raw_exit_codes、expected_exit_codes、open_questions、blocked_by、evidence_paths、reviewer_status。列表允许空，但未完成原因必须明确；不能写“继续完善”作为next_action。

接手者只读卡片、binding、oracle、decision、review和handoff，再读与下一步有关的源码。先重新验证当前文件hash；一致才从next_step继续，不重复下载、不重做已成功写入。变化则按START_HERE漂移分支暂停受影响步骤。

## 上级完成条件

所有适用子卡被独立接受 + 原义务矩阵无缺口 + 必须的跨卡用户旅程成功，三者缺一不可。31模型的公式卡通过只获得公式资格；实际披露适配与准确性分别验收。真实公司数据管道成功只获得来源链资格；没有正式建模和发布包，仍不能叫预测成功。

普通只读查询不依赖自然观察全部完成；生产持续服务承诺不得跳过其观察资格。替代样本、放宽预算、取消审核门和重新写旧PASS都不能用来关闭blocked。
