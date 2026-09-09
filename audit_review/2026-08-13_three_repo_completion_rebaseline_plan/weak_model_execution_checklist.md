# 弱模型防跑偏执行清单

> 本清单不是建议，而是每个 ZR/CA 工作单元的强制入口/出口。冻结 annex 中的20步手册仍适用；本文把最容易犯错的地方写成机械检查。

## 1. 每次领取前的五问

实施者必须先在 preflight receipt 中逐字回答：

1. 这个单元推进哪个用户目标和哪个痛点？
2. 当前 production entrypoint 是什么；哪些 helper/seam 不是生产路径？
3. 哪个 current-triplet 行为是 RED；独立 oracle 如何证明它不是 fixture/环境错误？
4. 允许改哪些文件；哪些仓、roots、数据、配置、旧计划绝对禁止写？
5. 下一单元的解锁条件是什么；本单元哪些问题明确不解决？

任何答案引用“旧receipt已通过”“看起来已有”“测试很多”都不合格。

## 2. 领取前机械门

- [ ] CA-001锁持有者/TTL/base hashes仍有效。
- [ ] 三仓40位HEAD、dirty allowlist、upstream状态与candidate manifest一致。
- [ ] CodeGraph indexed commit一致；若不一致先停在CA-003。
- [ ] plan、registry、command、scenario、config、schema、skill和sample hashes匹配。
- [ ] 前置单元状态为accepted/already_satisfied，且receipt未过期。
- [ ] 工作文件allowlist互不重叠；shared schema/registry只有一个writer。
- [ ] 使用短ASCII可写basetemp做控制组；中文/长路径是独立变量组。

## 3. RED 的有效性

- [ ] RED从公开/production入口触发；直接调用私有helper只能算T0。
- [ ] 先证明当前代码确实失败，并保存exit、business outcome、trace、oracle和side effects。
- [ ] 环境错误单独分类；不得为让RED出现而故意破坏fixture。
- [ ] 正例、负例至少各一；安全/事务/复用/迁移再加fault和mutation。
- [ ] “结构化错误返回”只证明错误合同，不证明成功旅程。
- [ ] 真实样本缺失记blocked，不得换一个更容易且非排他的样本。

## 4. 常见错误与强制拦截

| 错误实现 | 必须杀死它的门 |
|---|---|
| 在resolver加 `if Dropbox/dayu/companies` | AST硬编码门 + fourth-root core diff=0 |
| 给CatalogStore加`read_only=True`但仍初始化 | 不存在DB/OS只读/live WAL/写syscall测试 |
| runtime policy可选，缺失退v1 | RuntimeContext必填 + resolve/ensure/close-gap snapshot一致性 |
| v1结果后贴v2 policy hash | policy canonical hash重算 + stage trace reader版本 |
| Dropbox canary在companies另有副本 | root unique sample registry + selected root/location断言 |
| JSON sidecar变成annual report | primary-role=0 + persist→resolve负例 |
| `newer_revision`只展示不下载 | amendment provider spy + actionable集合断言 |
| artifact缺source hash仍复用 | source_sha required + source-change invalidation |
| INSERT artifact当成LLM调用 | invocation start/result/cache journal与spy对账 |
| 返回`producer_events`就称scheduled | 真demand row、worker PID/claim、artifact持久化、second-run-zero |
| private Dropbox直接外部LLM | privacy/rights/receipt gate + egress spy=0 |
| filename确认券商报告实体/日期 | 首页/section/table identity冲突golden |
| PDF cell平铺bullet称表格保真 | row/column/merged/footnote/page oracle |
| resource写成reserve | predicate+basis mutation |
| 已披露权益产量再乘持股 | Kamoa/Porgera口径测试 |
| 80%受控子公司收入只并80% | consolidation test |
| equity-method项目并入集团收入 | consolidation inclusion=0 test |
| 产量×价格直接称逐矿收入 | external segment reconciliation gate |
| 2028目标支撑2030参数 | covers-until temporal mutation |
| generator只过自家linter | real validate_document + draft full run |
| validate-only先formal后删文件 | syscall/registry before-after不可逆门 |
| draft走formal gate | Draft/Formal union contract tests |
| registry先append再写文件 | fault-injection publication transaction |
| 复制claim/拆参数提高confidence | metamorphic anti-gaming suite |
| 测试ID出现就算coverage | CA-105 current execution artifact |
| workflow有脚本就算动态审核 | scheduler/run freshness/alert self-test |
| 为让R9绿删除/skip测试 | mutation + new journey + caller/hit/rollback联合门 |

## 5. 每个单元的固定实施步幅

1. 只添加RED和独立oracle；运行并保存首败。
2. reviewer确认RED能杀死目标缺陷，才允许产品改动。
3. 做最小实现，禁止顺手迁移/删除/改schema版本。
4. focused GREEN；重跑旧相邻测试，确认没有改坏正确行为。
5. owner repo format/lint/type/unit/contract/integration/coverage/complexity。
6. affected sibling + exact current triplet T1。
7. fault/mutation/race/idempotent second invocation。
8. 需要数据/路由时只做副本dry-run→shadow→rollback；生产apply必须等rollout phase。
9. 生成implementer receipt；不得改accepted状态。
10. 独立reviewer在clean checkout重跑；closure validator单独推进状态。

若一项失败，回到对应步骤；不得把多个失败揉成“大致通过”。

## 6. 数据和迁移安全

- 外部 roots（Dropbox/dayu）任何文件/mtime/权限/sidecar零写。
- 下载只到受管 staging，再由canonical writer提交companies；无授权 discover/fetch/commit全为0。
- migration先副本、dry-run、计数守恒、batch journal、resume、idempotence、rollback visibility。
- 不可证明的legacy artifact保留但隔离，不能猜source hash、producer或实体。
- prompt/private历史审计不能把“缺证据”解释成“安全”；先封堵未来路径，再决定历史处置。
- 用户dirty文件不入diff、不stash、不reset、不覆盖。

## 7. 测试层不可互相替代

| 层 | 必须行为 | 不能声称 |
|---|---|---|
| T0 | pure/schema/property/contract | 跨仓生产接线完成 |
| T1 | 临时roots/catalog、三个真实subprocess、边界spy | 真实49GB catalog/个人PDF/provider完成 |
| T2 | 真实catalog和roots只读、unique samples | 网络下载/生产切换完成 |
| T3 | 真实provider+临时wiki，首次下载/二次零下载 | production cohort完成 |
| T4 | 明确授权的小cohort与rollback | 长期动态健康完成 |

receipt必须分别记录每层结果。T2缺失时不能用100个T0代替。

## 8. 独立 reviewer 检查

- [ ] reviewer身份不同，clean checkout，未使用实施者cache/临时文件。
- [ ] 精确triplet和所有输入hash重算。
- [ ] CodeGraph caller/impact与production trace一致。
- [ ] RED首败是真缺陷；没有弱化断言、减少collection、skip/xfail。
- [ ] diff只在allowlist，未加入公司/root/path特例或第二状态源。
- [ ] 正/负/fault/mutation/race全部重跑。
- [ ] side-effect ledger与OS/catalog/registry before-after一致。
- [ ] migration/cohort执行before→after→rollback→restored。
- [ ] unresolved finding有优先级、owner、successor；P1/P2阻断，承诺phase前关闭的P3也阻断。

Reviewer只能给 `accepted / changes_required / blocked / rejected`，不能边修边批。

## 9. 立即停线条件

- plan/registry/config/schema/sample被并发修改；
- 未授权provider或LLM外发、生产catalog写入、外部root写入；
- 错实体/期间/修订版复用；
- source/provenance/security冲突被静默吞并；
- mandatory collected下降或出现skip/xfail；
- shadow diff不可解释、迁移无journal或rollback；
- current triplet或policy snapshot在同请求中漂移；
- 真实SLO超过冻结预算；
- 需要扩大权限/数据模型/用户语义却没有ADR和review。

停线不是失败；隐藏、跳过或降低门槛才是失败。

## 10. 完成声明模板

每个单元/phase只能用以下结构交付：

```text
用户目标：
current RED：
实现范围与明确非目标：
base/result/current triplet：
正/负/fault/mutation/race：
T0/T1/T2/T3/T4实际结果：
side effects与rollback：
implementer/reviewer/closure receipt hashes：
剩余finding与successor：
```

任何“代码已重构”“测试都过”“reviewer accepted”而缺上述字段的声明，机器closure必须拒绝。
