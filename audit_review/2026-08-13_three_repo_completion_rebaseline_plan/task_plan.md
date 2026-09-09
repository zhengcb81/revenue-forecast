# 三仓库既有计划完成度复核与统一收尾计划

> 编制日期：2026-08-13  
> 当前任务范围：只审查、只制定计划；不修改产品代码、配置、数据库、索引、测试或CI。旧日期目录保持只读，仅把根历史入口页改为归档提示并新增唯一控制页。  
> 计划编制状态：完成；产品实施状态：未开始。  
> 唯一下一步入口：`audit_review/README.md`（本次整合后）；本目录文件仅为按需附录，旧FC/R9和冻结ZR目录不得并行领取。

## 并发和所有权协议

- 计划主体只写 `2026-08-13_three_repo_completion_rebaseline_plan/`；本次整合另新增根`audit_review/README.md`，并只改根历史三文件的归档提示。
- 六个日期目录、三仓产品文件、catalog和所有roots只读；旧计划关闭仅写成迁移建议。
- 输入30个文件已在 `input_snapshot.md` 记录path/size/mtime/hash。
- 未来每次写计划/registry/receipt前后做CAS；发现漂移立即释放工作单元、重读并小补丁合并，禁止整文件覆盖。
- 三仓当前有其他程序的提交/dirty变化；本计划不暂存、不回滚、不删除、不提交。

## 本轮计划编制

### Phase A：建立独立审计基线 — `completed`

- [x] 完整读取planning-with-files技能并遵循三文件/2-action/错误日志规则。
- [x] 新建独立计划目录，避免与另一个planning任务冲突。
- [x] 冻结两个输入计划30个文件及hash。
- [x] 记录三仓观察HEAD/branch/upstream/dirty、CodeGraph新鲜度限制和测试环境限制。
- [x] 未重建CodeGraph：并发写入期不争用索引；迁为CA-003独占窗口硬门。

### Phase B：逐项核验旧计划完成度 — `completed`

- [x] 枚举71 FC、R0～R9、FC-1501～1505、receipt、closure、scenario和current manifest。
- [x] 按current evidence分类：I=31、C=26、S=9、P=5、可直接继承current complete=0。
- [x] 确认旧closure为FAIL 66/71，R9强门4/4 RED。
- [x] 识别receipt/scenario/closure的漏仓、漏证据、旧triplet、marker coverage和revision选择假绿。
- [x] 给每个FC和release wave指定新successor。

### Phase C：三仓当前功能和痛点复核 — `completed`

- [x] company-wiki：Catalog真只读、RootPolicy/runtime、location、artifact、安全、producer、broker、worker、实库状态。
- [x] filing-fetch：external handle、freshness/revision、多gap/authorization、错误透明度和真实dayu-only影响。
- [x] revenue-forecast：schema/generator/linter、validate-only、draft/formal、publication、source processing、矿业、backtest/confidence。
- [x] E2E/CI/动态审核：production reachability、Windows/路径、current triplet、scheduler/freshness/alert和R9。
- [x] 将紫金真实运行问题与代码/数据层根因对齐；紫金只作为复杂canary。

### Phase D：统一下一步计划设计 — `completed`

- [x] 解释项目目标、三仓职责、11类痛点和六个最终成功问题。
- [x] 用冻结hash复用92个ZR功能单元与102新+95旧mandatory场景，避免复制出第二套可漂移状态。
- [x] 新增25个CA原子单元，修复基线、receipt/scenario/closure、动态调度、终审和旧计划关闭。
- [x] 建立71 FC和R0～R9逐项迁移矩阵。
- [x] 增加71行逐ID机器式状态投影，消除连续范围展开歧义。
- [x] 建立需求—痛点—工作单元—测试—关闭证据追踪矩阵。
- [x] 建立弱模型20步执行、防跑偏、stop、review和完成声明机械门。
- [x] 设计渐进路线：Reader→policy/lifecycle shadow→roots cohort→artifact/broker→mine/revenue shadow→观察→R9分批删除。

### Phase E：对抗式自审与交付 — `completed`

- [x] 检查CA定义唯一、ZR定义唯一和所有精确引用有定义。
- [x] 检查旧95、新102合计197场景唯一且冻结hash匹配。
- [x] 检查旧71 FC+10 waves全有successor，FC-150x全部迁移。
- [x] 检查所有产品实施单元仍为pending，没有误做代码/配置/数据/测试/CI实现。
- [x] 检查Markdown文件、链接、零字节、临时/锁文件和输入hash。
- [x] 生成计划自审和最终manifest；manifest不记录自身hash，避免自引用。

### Phase F：单一入口与计划整合 — `completed`

- [x] 在 `audit_review/README.md` 建立唯一、可独立执行的主计划。
- [x] 把项目目标、当前结论、下一张卡、A～J顺序、测试层级、停线规则和旧计划处置整合进单文件。
- [x] 将旧目录标为历史证据、最新目录标为按需附录；不移动、不删除、不并发修改旧日期目录。
- [x] 更新本目录入口声明和manifest，消除“PLAN_MANIFEST与authoritative plan谁更权威”的歧义。
- [x] 模拟陌生弱模型接手：只读README即可回答项目目标、当前状态、唯一下一卡、完整顺序、完成门，并找到CA-001及其必读附录。
- [x] 做hash、链接、ID、顺序和产品零改动复核后完成本阶段。

## 未来产品实施主链 — 全部 `pending`

以下只能通过根`audit_review/README.md`的`current_next`领取；`authoritative_execution_plan.md`仅提供阶段边界，本轮没有实施：

- [ ] A：CA-001～004 + ZR-001～004，独占重基线。
- [ ] B：CA-101～109，Evidence/Closure 2.0先行。
- [ ] C：ZR-101～206，真Reader、错误taxonomy和跨仓契约。
- [ ] D：ZR-301～409，来源生命周期、RuntimeContext/RootPolicy、freshness/download。
- [ ] E：ZR-501～510 + artifact migration，broker/web/ProcessingDemand。
- [ ] F：ZR-601～713，revenue合同、矿业会计桥、发布、backtest/confidence。
- [ ] G：ZR-801～806，真实E2E/故障/Windows/Linux/三类公司。
- [ ] H：ZR-901～907 + CA-201～206，真实PR/Daily/Weekly/Monthly和自然时间窗口。
- [ ] I：ZR-1001～1008 + CA-304，渐进cohort、观察、R9分批删除。
- [ ] J：CA-301～306，独立终验、六问题ledger和旧计划terminal closure。

## 完成定义

- 历史accepted、脚本存在、测试ID出现、fixture通过、单仓CI绿都不构成完成。
- 每个单元需要current production RED、正/负/fault/mutation、指定真实层级、独立oracle、side-effect/rollback、implementer+reviewer+closure receipts。
- required场景blocked/skipped、证据过期、triplet/config/skill/sample漂移、reviewer不独立或自然时间不足时保持未完成。
- 最终六个用户问题必须逐项machine pass；不能用总体比例覆盖剩余缺口。

## Errors Encountered

| 编号 | 风险/错误 | 次数 | 处理 |
|---|---|---:|---|
| R-E001 | 旧计划仍有其他程序更新，直接写入有覆盖风险 | 1 | 新建独立目录；输入只读；旧关闭只作CA-306建议 |
| R-E002 | focused pytest在sandbox中文临时目录创建fixture时WinError 5；26 pass、19 setup error | 1 | 不重复同命令；未来用短ASCII可写`--basetemp`控制组后测Unicode变量 |
| R-E003 | 直接读取sibling git因dubious ownership失败 | 1 | 不改global配置；使用每命令`git -c safe.directory=<exact repo>`只读复核 |
| R-E004 | PowerShell下给`rg`传Unix式`*.md`路径通配导致os error 123 | 1 | 改为搜索目录；未重复错误命令 |
| R-E005 | 一次多文件patch因一个context顺序不匹配而整体失败 | 1 | 先用`rg`定位精确context，再以小patch重试；无部分写入 |
| R-E006 | PowerShell不支持bash花括号路径展开，`rg path/{a,b}`触发parser error | 1 | 改为直接搜索目录并在结果中过滤；未重复错误命令 |
| R-E007 | 最终PowerShell校验字符串使用`$name:`导致变量解析错误 | 1 | 改用格式化运算符`-f`，避免冒号紧邻变量 |
| R-E008 | 最终校验将`Sort-Object -Unique`误写成不存在的`sort-Unique` | 1 | 修正cmdlet后重跑；最终14个manifest行hash与ID/FC计数全部通过 |
| R-E009 | 整合根历史三文件时一次组合patch把`# 审查发现`误写为预期`# 研究发现`，context不匹配 | 1 | patch原子失败、无部分写入；重读精确标题后拆成小patch完成 |

## 交付文件导航

- `project_goal_and_pain_points.md`：为什么做、用户最终期待。
- `current_state_audit.md`：三个仓当前真实状态。
- `completion_audit.md`：旧Phase完成度。
- `legacy_transition_matrix.md`：71 FC/R0～R9逐项迁移。
- `legacy_fc_status_registry.md`：71个FC逐ID分类、原因码和successor。
- 根`audit_review/README.md`：唯一控制面、当前游标和领取入口。
- `authoritative_execution_plan.md`：A～J详细顺序和阶段门附录。
- `completion_assurance_registry.md`：25个CA原子单元。
- `traceability_and_acceptance.md`：目标到测试/证据闭环。
- `weak_model_execution_checklist.md`：弱模型防跑偏。
- `input_snapshot.md`：并发输入hash。
- `findings.md` / `progress.md`：审计事实和本轮过程。
- `plan_self_audit.md` / `PLAN_MANIFEST.md`：计划自身验收与冻结清单。
