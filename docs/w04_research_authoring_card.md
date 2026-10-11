# W04 WP06 — 下一轮真实研究执行卡

> 2026-10-11；文档工程交付不等于原三公司经济验收。当前责任 RC09/RC10/RC11/RC12/RC17，87 个原 issue_key 保留原状态。供 ROOT 的新 owned attempt 使用；禁止改写 PW03 sealed input/run/report。

## 0. 读者先知道的事实和边界

- 编写基线：RF `b7fe04aabe1d2a53b67a385c97161af976031040`；当前 engine 4.2.1，canonical forecast schema 3.7，opt-in 3.8/3.9。
- P7 RF 已接受的 4.2.1 修复解决的是 calibration 的 scope/period/native-use 关系；未证明任何真实公司的未来收入量级。
- CWP 保存/校验原件、解析、选择/摘要、版本化只读 export；filing-fetch 请求复用/正确工具获取缺件；RF 负责研究和收入模型；audit 记录/独立诊断。CWP/audit 不做投资判断。
- 用户已有资料采集、配置供应商原语言处理和外发授权。沿实际配置、费用/token/字节/时间母账执行；无逐材料批准、手写授权JSON、canary或人工签收。缺能力/预算如实报原因。Dayu不改；IQS与他人WIP不碰。
- 本文的工作记录不新增 native 字段、数据库、签名者、许可链或“全公司校准”硬门。只在完整执行和四审两个既定大节点验收。

## 1. 接口清单与合法使用

| 公共对象/入口 | 实际字段/用法 | 不可声称的保证 |
|---|---|---|
| SourceRef2.0 | schema_version/document_id/source_id/content_sha256/byte_size/mime_type，无物理路径 | 文件名、目录或hash不能证明研究正确 |
| source_preparation.py | --request-file、--result-envelope、--company-wiki-catalog-config、--timeout-seconds；2.0 filing_intent及actual acquisition_limits | --help、配置存在不代表provider已调用 |
| prepare_registered_source_result | candidate, as_of_date, company_wiki_catalog_config, timeout_seconds=30, source_reader_receipt_version=2.1 | 非期间化deck/industry/IR不伪造FY或走SEC财报发现 |
| narrative public reader | raw /1及显式compact投影/3；以真实read receipt和parent refs核对 | reference(metadata_only)、completed摘要不代表RF已用 |
| consume_narrative_input | request/bindings/source_id/catalog_config；binding四键span_id/claim_id/parameter_id/support_type；read后真到native formula | 仅read不能记consumed；失败不强补成功receipt |
| native schema3.9 | period_flow + period_start/end，当前3/6/12完整月；其他basis不带日期 | partial控制窗口不改名H1来适配 |
| operating_research/1 | inventory/observations/calibrations，exact现有key集合 | optional诊断green不证明economic truth |
| management-communication-scope/1 | category/start_date/end_date/coverage_complete/items；用实际read originals | discovery/index_notice不能作原件 |
| management-target-comparison/1 | annual_revenue_level/quarterly_revenue_level/year_over_year_growth和已有scope ancestry | CC/adjusted/季度/年度/gross/net不能暗换 |
| economic-support-diagnostics/1 | --input/--output，cell supported/conditional/unsupported与具体reason | 不要求future actual、不拦forecast、不当概率 |
| snapshot-schema-diagnostic/1 | 新snapshot真实schema，旧header差异诊断 | 不改旧snapshot fingerprint/registry |

公开范围未知的多issuer投影仍按真实producer资格报告；不能拿更新时间补首次发布时间。新compact运输修复不解开 c620 这类未知 source clock。可以使用其他合格原件完成模型并清楚列出该缺口。

## 2. 有序施工：输入 → 研究 → 参数 → native结果

完整方法见 [installable authoring procedure](../references/research-coverage.md#research-authoring-procedure)。以下为施工时的最小清单，不是新增小节点门。

### 2.1 冻结请求和运行环境

ROOT分配新attempt目录、输入请求、as-of、公司标识、报告币种/scale、fiscal-year end、base年和**连续三年**forecast_years；冻结实际工具/runtime/package版本及母账余额。读取实际provider/model/profile，不猜配置；不复制canonical assurance/output或全湖原件。操作日期真实记UTC，信息截止仍是请求as-of。

本轮原三公司原请求是 CN688012/HK00700：CNY million、FY2025基期、FY2026–28；USMSFT：USD million、FYE06-30、FY2026基期、FY2027–29；as-of2026-10-08。它们是回归控制，不应把公司名写进通用源码。

### 2.2 补真实需求矩阵和资料链

用一份有界矩阵，逐类写实际查询窗口、经营问题、重大性、查询/命令事件、原件source/locator或named gap。年/半年/季报、release/call/deck/strategy/IR活动、IPO/equity/placement/convertible/proceeds、交易历史审计/备考、行业/客户/peer原件均需有逐类决策，不按扩展名或标题判断无价值。

先查CWP原件，存在就prepare/open，不下载。缺件走有意图和实际硬限额的source_preparation/FF，ET适合市场按配置伴随；原语言TXT不翻译。已注册deck/industry/IR使用registered adapter，不强塞fiscal_year。网页事实须有正式原文/SourceRef/capture；搜索输出只有线索。失败保存本次reason/阶段/provider_started/calls/实际账，不继承旧外部状态。

最新财务filing发布时间→as-of窗口完成前不能写checked；较早收购公告只用于控制事实。类型资料无需全选，但selected未读要留下incomplete；未选需specific materiality理由。`not_available`的conclusion写没拿到什么，而非“Read original/no target”。IR活动DOCX与官方问答分列需求；问答speaker/answer/first-publication unknown不装作管理层事实。

### 2.3 真读、政策、目标和经营库存

在原locator真开完整相关语义组：actor、产品、日期、Total/单位/货币、限制/反证和政策触发。summary只是资料导航；已open原文即使摘要失败仍能用于研究。continuous quote保留同一原文顺序；远处脚注/拼段拆成两个claim，不拼成一个verbatim excerpt。OCR/table_row_transcription在工作记录标明，保留各行列/header定位，不给native新增quote_type字段。

按inventory现有topic/disposition记录新产品、目标、capacity/融资/确认/竞争/并购。included_in是父item_id而非随意segment名；相关parameter_ids必须属于父item且已用。所有管理层目标包括qualitative growth/capacity/FX/adjusted variants均进target ledger，正确分strength/period/perimeter后选treatment；不能让unmodeled一把抹去本来可比的目标。

### 2.4 核实历史基期和最小经营cross-check

历史收入、segment外部收入+signed base adjustments与报表总额同币种/scale/period；两年观察只是最小合同。产品收入/销售量推历史blended unit revenue要说明产品mix、服务/验收范围，不把隐含值称ASP。年度与H1/H2/native derived bridge、CC/FX/adjusted、grossnet、收购控制/内部抵销先定清。

同一集团H1与购后短流可并存。众硅真实控制日2026-05-31，至6-30贡献1.29190208 CNYm；不是Jan1 H1，更不是众硅全年销售。64.69%控制股权不乘收入；28,000/43,000/58,000万元年度承诺不能机械7/12或套各年同mismatch。原生3.9当前仅3/6/12月，短流保留原source EvidenceSpan/已核摘录和工作库存；native inventory claim必须绑定合法target，不能留不存在parameter的悬空claim。集团H1保持合法参数。先用groupH1+post-H1 conditional模型；必要时向ROOT报通用typed contribution-window seam。不得因此宣布其它可用收入事实全部不可消费。

### 2.5 先证据后幅度，少参数建三年低基高

每个material curve按observed scope×period×unit/range→explicit conversion→native derived output建立路径。真实range两endpoint有value_range claim和相同observed期/scope/unit；conversion有bound observation、actual scenario applicability；输出必须进入该scope/year native ancestry。先核实际经营、同行/客户同口径和反证，再选future值。

缺range：observed_range=null、unverified，少自由度而非全null。可用一个透明direct_growth/direct_revenue aggregate替多个猜测volume/price/mix/lag，以reported recognition basis解释；非null假设必须有决策理由、条件、counter/limits和未来复查指标。基础条件例是“已观测份额/交付能力持续、不发生新增扩产收入”，不是默认+10%或复制H1。同一future路径不表示已观测，后两年不能隐藏为自动平持；逐年保留条件与饱和/竞争/商业化边界。

三年×三情景每个segment必须有可复算输入与recognized/effective revenue、总额、增量和CAGR；zero base CAGR undefined。没有材料可比范围不会新增发布权限门，但独立经济审查可认定重要量级依据未完成。不能为叫green而捏range，也不能把72future null当完成用户请求。

### 2.6 目标、RPO、paid cohort与确认桥

每个年度独立做perimeter/control/elim；年度/季度/YoY/RPO/run-rate/cumulative分开。CC与reported factor转换和adjusted variants单列，FX<1pp不写+1%乘数。Search exTAC和grossSearch+LinkedInMarketing/Premium不是matched。No consensus不称“超预期”。独立benchmark可不达到管理目标但需真实三情景路径/claims。

总RPO684b与commercial678b是嵌套，不相加；2.3年平均期不等于等比释放；next12months比例只是对应边界，需新增订单/剩余释放/续约桥。paid seats期末存量不等于平均账单人数，registered/nonpaid/users不等于收入。E7 bundling/migration/GitHub reclassification必须在父级核一次；未GA的private preview不造商业化量。可保留清楚条件而非拆出虚构销售线。

政策按实际biz触发：Frontier consulting services provided；Search ads displayed/action和netexTAC相关定义分开；Xbox硬件与内容订阅时点分别说明；FTB/paycohort混合边界不能被统一factor遮蔽；Others定义/recognition不是未来增长。

### 2.7 联合冲击一次入同DAG，再做native sensitivity

先选shared event、真实曝光/影响业务、数量/价格/支付量/变现/acceptance时点、取消/恢复条件；无需捏GPU物理cap。若少事实，用明确conditional金额stress，不称实证Low或probability。广告预算、游戏cohort、支付activity/cloud供给响应有异质性，统一×0.95只有实质共因/转换说明才合理。

native constraints/adjustment每项只记一次。Q4→Q1延期用明确Q4暴露和catch-up/cancel，不能annual/4；customer AR延付不自动取消revenue。构建独立新stress input，重新native完整三年compute；保留Baseline→stressed年度净差、catch-up期限/取消、constraint before/after，不加单shock效应。按driver语义的percent/pp/bp/absolute/range/discrete测base参数各一次，核requested/effective/clamp。native annual paths crossed则如实reject，不能排序抹掉。

### 2.8 单次主要执行与交付

生成骨架时选择实际model/schema；skeleton不是facts/reads。完成所有实际claim/source/params后集中做lint→hashcheck→validate集错→compute/renderer→economicdiagnostics→immutable snapshot；具体命令见下一节。变动模型或具体失败才重跑相关阶段，禁止每个小节点重复完整测试或手写估算替代engine。

一个新authoring输入版本贯穿compute/snapshot和stress；写在新owned路径，实际registry在ownedattempt环境变量，结束恢复原环境。审查包提供原件引用和native参数关系，不复制每版大JSON；记录owned retained/peak/actual收费及unknown母账。forecast目录相邻TRUST_BOUNDARY声明不作许可书。ROOT安排四独立agent分别审来源、fetch、流程数字、经济假设；文档工程完成不宣布研究通过。

## 3. 实际命令和结果矩阵

下面是已存在CLI。尖括号由ROOT新attempt真实值替换，不可直接带placeholder执行。安装skill没有tools/工程tests；本流程不依赖repo-only recipe。

```powershell
# Optional once: field-correct skeleton, no evidence generated
python -X utf8 -B scripts/generate_input_template.py --name <company> --base-year <base> --forecast-years <y1> <y2> <y3> --currency <currency> --unit million --segments <actual-segments> --schema 3.9 --output <new-skeleton.json>

python -X utf8 -B scripts/source_preparation.py --request-file <actual-bounded-request.json> --result-envelope --company-wiki-catalog-config <explicit-config> --timeout-seconds <remaining-budget>

python -X utf8 -B scripts/lint_input.py <new-input.json>
python -X utf8 -B scripts/fix_hashes.py <new-input.json> --check
python -X utf8 -B scripts/revenue_forecast.py <new-input.json> --validate-only --verbose
python -X utf8 -B scripts/revenue_forecast.py <new-input.json> --output <new-forecast.json> --markdown <new-forecast.md>
python -X utf8 -B scripts/research_support_diagnostics.py --input <new-input.json> --output <new-economic-support.json>
python -X utf8 -B scripts/revenue_backtest.py create <new-input.json> --version <same-new-version> --output <new-snapshot.json>
```

`REVENUE_PUBLICATION_REGISTRY`指定新attempt目录内**file**，不能改全局canonical registry。`forecast_version`先在input填same-new-version；schema3.9仅本次有period-flow或role-aware需要时显式选，schema3.7/3.8仍合法。`--validate-only`无registry写；正式compute及snapshot创建会登记。Native snapshot固定新写，不覆盖；JSON文件序列化不同不要求byte相等，强validator和canonical input/result anchor负责语义一致。不得为纯文档检验执行真实source/provider、三家engine或全量manual contracts。

| 大节点 | 本次文档包已做 | 下一真实attempt必须做 |
|---|---|---|
| Doc/interface | 真实文件/字段/CLI适配检查和87key方法映射 | 使用实际已接受并安装的版本 |
| Research+native | NOT_RUN；旧sealed状态保留 | actual originals→claim/param/DAG→三年三情景/target/sensitivity/render/snapshot |
| Four reviewers | NOT_RUN | 实际source/window/locator、reuse/get、numeric/process、独立economic质量 |
| New three companies | NOT_RUN | 不同市场/行业泛化；不加公司特例或继承旧审查 |

## 4. 当前限制与ROOT接口交接

1. `scripts/contracts/period_flow.py:validate_period_flow_fields`/`period_flow_months`只承载3/6/12完整月贡献。合法例：`period=FY2026,time_basis=period_flow,period_start=2026-01-01,period_end=2026-06-30`，须由FYE12-31和claim支持。短control-window金额仍可保留原source EvidenceSpan/已核摘录与context；native claim须有合法target，不可当该typed H1 fact。另开通用贡献窗口契约需ROOT定接口/TDD。
2. `scripts/research/communication_scope.py:analyze_communication_scope`对postfiling取注册source_type regulatory_filing/exchange_filing的max published_date；IPO/发行材料也可能落该集合。下一执行需核是否与latest financial-filing需求一致；如冲突向ROOT提交例，不改source_type来骗窗口。
3. `source_preparation.py:prepare_registered_source_result`及public reader是来源适配责任；research卡不另造来源身份或日期资格。c620多issuer selected row publication仍unknown时继续gap，不用crt/audit/upd timestamps放行。
4. `scripts/research/evidence_roles.py:_calibration`的native scope/period/observed endpoints规则与P7 4.2.1接受一致。`observed_range=null`允许结构运行，不能承诺economicgreen；source-linkedfutureclaim仍遵守已有rationale_support合同，不强补futureactual。
5. 新预算/profile/generation、provider策略、CAS/ledger与新attempt封装由ROOT/WP其他owner实施。此卡不写任何配置，不调整费用/空间cap，不收费追回旧supplier完整响应。

## 5. 证据来源与87项映射

本卡方法依据的是完整解析的PW03三家公司×四role JSON，而非摘要猜测。来源SHA在自身 `.planning/w04-wp06/evidence/implementation/wp06/sealed-report-read-index.json`；对应W04覆盖来源SHA为 `3a189e4e6a6c1768d1c5cf939146acfbfb2be746bf1f5d22d7eef9b322aff116`。P7 RF接受文档记录源主线47f497ad、actual4.2.1工程能力，旧run经济状态未因此改变。

以下每项保持原key、历史状态及PW03复验；表中“研究待新attempt四审”表示文档实现只解决执行责任/方法，不能关旧finding。已PASS的旧症状仍原PASS，不重复造修复。

| 原 issue_key | 方法/章节 | PW03 真实复验 | 新研究状态 |
|---|---|---|---|
| `fresh-20261009T065028-cn-688012/fetch/FETCH-002` | T09 §2.2–2.3 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-cn-688012/process/PROCESS-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-cn-688012/process/PROCESS-002` | T09 §2.2–2.3 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-cn-688012/process/PROCESS-008` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-cn-688012/analyst/ANALYST-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-cn-688012/analyst/ANALYST-002` | T12 §2.7 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-cn-688012/analyst/ANALYST-003` | T09 §2.2–2.3 | BLOCKED | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-cn-688012/analyst/ANALYST-004` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-hk-00700/fetch/FETCH-004` | T09 §2.2–2.3 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-hk-00700/process/PROCESS-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-hk-00700/process/PROCESS-002` | T09 §2.2–2.3 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-hk-00700/analyst/ANALYST-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-hk-00700/analyst/ANALYST-002` | T12 §2.7 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-hk-00700/analyst/ANALYST-003` | T09 §2.2–2.3 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-us-msft/process/PROCESS-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-us-msft/analyst/ANALYST-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `fresh-20261009T065028-us-msft/analyst/ANALYST-002` | T12 §2.7 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/storage/M3-CN-STORAGE-006` | T09 §2.2–2.3 | NOT_RUN | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/fetch/CN688012-FETCH-007` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/process/CN688012-PROCESS-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/process/CN688012-PROCESS-008` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/analyst/ANALYST-CN688012-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/analyst/ANALYST-CN688012-002` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/analyst/ANALYST-CN688012-003` | T12 §2.7 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/analyst/ANALYST-CN688012-004` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-cn-688012/analyst/ANALYST-CN688012-006` | T11 §2.4–2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/fetch/M3-HK-FETCH-004` | T09 §2.2–2.3 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/fetch/M3-HK-FETCH-005` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/fetch/M3-HK-FETCH-006` | T17 §2.3/2.6 | NOT_RUN | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/process/M3-HK-PROCESS-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/process/M3-HK-PROCESS-002` | T11 §2.4–2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/process/M3-HK-PROCESS-003` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/process/M3-HK-PROCESS-006` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-002` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-003` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-004` | T11 §2.4–2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-005` | T10 §2.4–2.5 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-006` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-007` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-hk-00700/analyst/HK-ANALYST-009` | T11 §2.4–2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/process/M3-US-PROCESS-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/process/M3-US-PROCESS-002` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/process/M3-US-PROCESS-006` | T17 §2.3/2.6 | N/A | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/process/M3-US-PROCESS-007` | T17 §2.3/2.6 | PASS | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/analyst/ANALYST-001` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/analyst/ANALYST-002` | T10 §2.4–2.5 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/analyst/ANALYST-003` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/analyst/ANALYST-004` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/analyst/ANALYST-005` | T12 §2.7 | FAIL | NOT_RUN（研究待新attempt四审） |
| `m3-20261009T184946-us-msft/analyst/ANALYST-007` | T11 §2.4–2.6 | FAIL | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/storage/PW03-CN-STORAGE-007` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/fetch/PW03-CN-FETCH-001` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/fetch/PW03-CN-FETCH-002` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/fetch/PW03-CN-FETCH-006` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/process/PROCESS-001` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/process/PROCESS-002` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/process/PROCESS-006` | T11 §2.4–2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/process/PROCESS-007` | T11 §2.4–2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/analyst/ANALYST-PW03-CN-001` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/analyst/ANALYST-PW03-CN-002` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/analyst/ANALYST-PW03-CN-003` | T11 §2.4–2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/analyst/ANALYST-PW03-CN-004` | T12 §2.7 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-cn-688012/analyst/ANALYST-PW03-CN-005` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/storage/PW03-HK-STORAGE-004` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/fetch/PW03-HK-FETCH-002` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/fetch/PW03-HK-FETCH-004` | T17 §2.3/2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/process/PW03-HK-PROCESS-001` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/process/PW03-HK-PROCESS-002` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/process/PW03-HK-PROCESS-005` | T17 §2.3/2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/analyst/ANALYST-001` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/analyst/ANALYST-002` | T12 §2.7 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/analyst/ANALYST-003` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/analyst/ANALYST-004` | T17 §2.3/2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-hk-00700/analyst/ANALYST-005` | T17 §2.3/2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/storage/PW03-MSFT-STORAGE-006` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/fetch/PW03-US-FETCH-003` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/process/PW03-US-PROCESS-001` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/process/PW03-US-PROCESS-003` | T11 §2.4–2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/process/PW03-US-PROCESS-004` | T17 §2.3/2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/process/PW03-US-PROCESS-007` | T09 §2.2–2.3 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/analyst/ANALYST-001` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/analyst/ANALYST-002` | T10 §2.4–2.5 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/analyst/ANALYST-003` | T11 §2.4–2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/analyst/ANALYST-004` | T17 §2.3/2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/analyst/ANALYST-005` | T12 §2.7 | new PW03 finding | NOT_RUN（研究待新attempt四审） |
| `pw03-20261011T010657Z-us-msft/analyst/ANALYST-006` | T11 §2.4–2.6 | new PW03 finding | NOT_RUN（研究待新attempt四审） |

## 6. 停止与交接

文档施工STOP：交三个排他diff/SHA、12 sealed报告读取清单、87key方法映射、轻量actualCLI/schema日志与真实未执行项。ROOT集中接受/正常commit/push/定点安装，随后G4新attempt完成原三公司三年native预测及四审；再新三家公司泛化/G5。此卡不把工程绿当经济完成，不追加每个小节点的审查或审批。
