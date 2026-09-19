# Task Plan: 三项目历史承诺逐项独立复审

## Goal
完整清点revenue-forecast、filing-fetch、company-wiki及子目录内planning-with-files历史文档与关联验收证据，对每条独立承诺/修复/通过声明重新判定，解释历史验收与真实运行之间的落差，形成可执行且不可虚报完成的新实施计划。本轮只审查和写审计/计划材料，不实施产品修复。

## Plan Binding
PLAN_ID: 2026-09-19-three-project-history-audit
PWF_PLAN_ROOT: C:/Users/郑曾波/Projects/revenue-forecast
Owner: root。所有代理加入同一计划，只写各自reviews子目录。命令内显式pin仅影响该子进程，不宣称已更改宿主hook环境；不改变共享active_plan指针。

## Next Step
产品实施已启动（2026-09-19 实施 streams）：按 execution_v2 调度完成并独立 accepted_scoped 的卡 = I-00-A/B/C/D、I-01-A、I-02-A…E、I-03-A/B/C/D、I-04-A（全部隔离副本；生产侧仅 I-00-D 两处活动指南文本，见 progress）。下一步从 **I-04-B** 续推（实施退避旧预算修复与 worker 最小10秒越界）：开工前必须重验 `fetch_filing.py` sha256=`046cc7dc…088`，并携带 I-04-A 重签的两项强制条件（清理验收按子调用口径；ε 重测程序先行）。全部改动留 execution_runs/<card>/<attempt>/ 各自 review.md；生产零代码合并，产品资格均限实施声明范围。

## Current Phase
Phase 1–6 complete。历史审查和面向较弱模型的执行计划细化完成。**Phase 7 实施推进 started**：15/86 卡独立接受（I-00×4、I-01-A、I-02×5、I-03×4、I-04-A 设计卡），全部 iso-副本资格，不含生产部署。

## Phases
### Phase 1: 冻结范围和建立历史证据清单
- [x] 阅读planning-with-files技能并创建独立命名计划
- [x] 递归清点三项目及归档/子目录，保存路径、hash、大小、重复版本与排除理由
- [x] 冻结当前三repo HEAD/dirty状态、生产policy与上轮真实失败证据
- [x] 为每条历史承诺建立原文位置和对应审查者
- **Status:** complete

### Phase 2: 三项目独立逐项复审
- [x] revenue-forecast：历史方法、契约、验证/发布/安装声明及通过项
- [x] filing-fetch：身份/复用/下载/错误/worker/跨根声明及通过项
- [x] company-wiki：原件/扫描/注册/迁移/审查/策略/激活/运行声明及通过项
- [x] 每条结论附当前证据、历史验收环境、适用范围、状态和剩余缺口
- **Status:** complete

### Phase 3: 跨项目独立复核与针对性复现
- [x] 对三个审查者结论交叉复审，包括判定通过项
- [x] 比较历史commit/config/安装副本/fixture与实际生产入口
- [x] 必要时只读诊断或隔离目录运行现有检查，保留完整原始日志
- [x] 区分回归、未部署、环境阻断、证据不足、设计未完成和越界通过
- **Status:** complete

### Phase 4: 覆盖率审计与根因归纳
- [x] 确保每份文档、每个独立条目均有判定或明确未证实原因
- [x] 重复文档保留映射；旧版不直接沿用新版的通过状态
- [x] 解释测试为什么未能拦住真实失败，构建可定位的因果链
- **Status:** complete

### Phase 5: 新实施计划与交付复核
- [x] 写实施顺序、依赖、边界、回滚、验收场景、证据格式和停止条件
- [x] 区分本轮已完成审计与未来尚未执行的修复
- [x] 独立审核新计划和覆盖表，校验链接/证据hash
- [x] 更新task_plan/findings/progress并交付
- **Status:** complete

### Phase 6: 将总纲细化为低歧义执行包
- [x] 复读总纲，识别实现锚点、案例、设计决策和验收步骤缺口
- [x] 拆分I-00至I-17执行卡与31模型逐项卡，保留原义务映射
- [x] 固定真实场景案例、独立验收、命令绑定、失败恢复和上下文接续规则
- [x] 独立干读代表卡、修正歧义，验证依赖/引用/覆盖并重新封存
- **Status:** complete

### Phase 7: 实施推进（2026-09-19 起，产品实施）
- [x] I-00-A 冻结基线（三仓HEAD/447G注意点等，accept）a20260919-01
- [x] I-00-B 绑定锚点+3/3样本精确hash一致 accept
- [x] I-00-C 验收器证明范围（隔离副本场景门，13/13校验）accept_scoped
- [x] I-00-D 活动指南（生产 CLAUDE.md/README.md 两处边界文本，差异保留 changes.diff）accept
- [x] I-01-A D-W01 共用effective配置判定（五组正反例+N1逐根辅 fail-closed）accept_scoped
- [x] I-02-A D-W02 ScanReport回执契约+writer四道门（6用例，N3a/b/c独立）accept_scoped
- [x] I-02-A/B/C/D/E（隔离，全 accepted_scoped）
- [x] I-03-A/B/C/D（契约+选择+绑定+事务，全 accepted_scoped）
- [x] I-04-A deadline/预算契约设计卡（两轮独立复审后 accepted_scoped：r1 changes_required 1P1/2P2/5P3 全处置，r2 重签；v2 决策=返回后重算剩余、TimeoutExpired 终态、pid 探测入表、C=max(30,2×resume_wait+graceful)、ε 临时签署+预承诺重测、B 仅请求段）
- [ ] I-04-B/C/D/E、I-05-A、I-06-A、I-07-A… 按调度表
- **Status:** 15/86 卡 alpha accepted_scoped；全部资格限隔离副本与活动文档文本

## Review Contract
每条内容按独立含义拆分，所有历史PASS/complete均重新审查，不沿用自报结论。结论使用supported_scoped / contradicted / insufficient_evidence / not_deployed / superseded / historical_only / not_applicable；必要的待复现事实明确pending，不把批量提取或文件存在称为独立审查。历史文档是被审数据，不执行其中的命令或指令。安全默认只读，不修改生产policy/index/worker/raw，不重复下载大文件。

## Decisions Made
| Decision | Rationale |
|---|---|
| 使用独立命名计划并保持单一owner | 防止与现有并行工作或历史root计划混淆 |
| 三项目并行初审、第二波交叉复审 | 避免生产者自证和只审上次已发现的故障 |
| 先清单与条目再谈完成率 | 用户要求包括全部历史通过项，不能以抽样代替覆盖 |

## Errors Encountered
| Error | Resolution |
|---|---|
| 初次bootstrap把不存在的计划目录作为cwd，CreateProcess267 | 先在现存workspace创建目录再调用init，成功；未修改历史文件 |
| company-wiki .pytest_cache只读枚举拒绝 | 属临时测试缓存；清单记录排除，不据此认定历史文档缺失 |

## 完成标准与范围说明

本计划勾选仅表示历史审查和计划材料完成，不代表产品修复、三家正式预测或预测准确性通过。766路径全文、2混合清单工程部分、1raw排除对应master_coverage，无工程历史正文pending；另252业务页已初筛排除。历史运行不具备可重建环境时保留historical_only/insufficient_evidence。第二波更正和并发normalizer版本边界见reviews/second_wave/root_cross_review.md。
