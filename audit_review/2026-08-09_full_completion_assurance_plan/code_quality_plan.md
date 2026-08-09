# 三仓代码质量全面提升计划

## 1. 原则

代码质量治理必须在功能场景保护下渐进进行。先建立行为基线和架构门，再收敛重复策略和硬编码；禁止一次性大重写后只靠单测判断等价。

## 2. 硬编码分类与目标

| 类别 | 典型表现 | 目标位置 | 禁止位置 | 验证 |
|---|---|---|---|---|
| Root/path | `company_raw`、`dayu_portfolio`、Dropbox 路径、sibling 相对路径 | RootPolicy/config/test fixture | scanner、resolver、consumer 业务分支 | AST/literal allowlist + EX-08 |
| Provider/market | CN/HK/US 分支、provider URL/规则 | adapter/provider registry | filing/revenue 通用编排 | registry completeness + DL T1/T3 |
| Schema/status | 字段名、reason/status 字符串 | versioned contract/enums | SQL/脚本散落字符串 | contract/type/unknown-value tests |
| Runtime flags | v2/legacy/cohort dict | persisted RuntimePolicySnapshot | WU/CLI/测试中的生产默认值 | CTRL + production caller gate |
| Evidence/receipt | accepted、policy hash、download=0 | validator/journal | 手写 receipt、由结果倒推计数 | AUD-07 + mutation |
| Time/sample | 固定最新年份、绝对路径、真实公司名 | as_of/sample registry/fixtures | product logic/CI workflow | clock injection + privacy gate |

## 3. 渐进重构顺序

1. 冻结 95 场景、command/contract registry 和现有质量基线。
2. 建立 architecture forbidden-pattern gate，仅报告不阻断，确认误报。
3. RootPolicy/adapter/resolver 生产接线完成后，逐个替换 root/provider 分支。
4. 用真实 production caller 取代 test-only helper；每删除一个 helper 先证明替代路径可达。
5. 收敛重复 enums、reason codes、allowlists 和 manifest pins。
6. 拆分复杂函数时保持 API/trace golden；一次只拆一层并跑 T1。
7. legacy hit 连续两个窗口为 0 后关桥，再观察一周期才删除旧代码。
8. 最后把报告型门禁升级为 required check，防止重新引入。

## 4. 质量指标与 ratchet

- Coverage：先记录真实 branch/line baseline；critical control/resolver/download/artifact modules 最终 branch>=95%，整体阈值永不下降。
- Mutation：关键安全/副作用/identity/epoch/latest/artifact mutation kill=100%；新增相关 mutation 不得 survived。
- Complexity：新增/改动函数圈复杂度<=10；存量超标逐 FC 下降，禁止阈值回升。
- Duplication：RootPolicy、reason enum、contract models、test scenario 只能有一个 owner；重复定义数最终为 0。
- Reachability：新增生产构件 production caller>=1；legacy/test-only 构件按计划降至 0。
- Type：跨仓公开契约严格检查；禁止无依据 `Any`、裸 dict 和忽略类型错误。
- Errors：所有跨进程错误结构化、版本化、UTF-8、安全脱敏；禁止捕获后返回假成功。

具体基线数字必须在 FC-104/1204 从稳定 triplet 实测后冻结，本计划不虚构现状阈值。每次降低阈值都必须触发 CI 失败；任何“临时降低”需要新 FC、owner 和到期时间，且不能通过 Phase 15。

## 5. 代码审查清单

- 是否把配置数据误写成业务 `if/elif`？
- 是否引入第二个策略/身份/provenance/allowlist 来源？
- 是否新建只被测试调用的 helper？
- 是否让 filing/revenue 重做 company-wiki 的决策？
- 是否依赖扫描顺序、路径名、mtime、当前年份或本机目录？
- 是否由返回对象推断下载/写入/解析次数，而非 journal？
- 是否吞掉异常、返回空 dict/None 造成假成功？
- 是否把 unknown/unreviewed 当安全或已完成？
- 是否新增无界全表扫描、重试、并发或内存加载？
- 是否触碰用户 dirty file、真实 root 或未授权下载？

任一答案为“是/不确定”时不得 accepted，除非它是明确的 adapter/config owner 位置且有合同和测试证明。

## 6. 完成标准

FC-1201~1205 全 accepted；95 场景无回归；forbidden hardcode/重复策略/关键 dead helper/Windows 编码错误为 0；coverage/mutation/type/complexity required gates 生效；CodeGraph 证明生产调用链收敛且 legacy caller=0。只提交格式化、改名或统计报告不能算完成本目标。

