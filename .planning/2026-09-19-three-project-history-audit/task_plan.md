# Task Plan: 三项目历史承诺逐项独立复审

## Goal
完整清点revenue-forecast、filing-fetch、company-wiki及子目录内planning-with-files历史文档与关联验收证据，对每条独立承诺/修复/通过声明重新判定，解释历史验收与真实运行之间的落差，形成可执行且不可虚报完成的新实施计划。本轮只审查和写审计/计划材料，不实施产品修复。

## Plan Binding
PLAN_ID: 2026-09-19-three-project-history-audit
PWF_PLAN_ROOT: C:/Users/郑曾波/Projects/revenue-forecast
Owner: root。所有代理加入同一计划，只写各自reviews子目录。命令内显式pin仅影响该子进程，不宣称已更改宿主hook环境；不改变共享active_plan指针。

## Next Step
产品实施已启动（2026-09-19/20 实施 streams）：已独立 accepted_scoped 的卡 = I-00-A/B/C/D、I-01-A、I-02-A…E、I-03-A/B/C/D、I-04-A（设计）、I-04-B（实施）、**I-04-C（设计；C1 已关闭、C2=OPEN-3 owner 裁定项）**、I-08-A（设计）、**I-07-A**、**I-14-A（隔离测量修复；D1 未签 ⇒ 不得提升进 RF/tools/）**、I-15-A（**仅证据/诊断**；产品实施 blocked, D-W15 未签）、M01–M04 与 **M05–M07**（**仅 formula 资格**）。**未接受**：M08（blocked，owner 三步；F-M08-06/-07/-08/-09 修复在办）、I-14-C（r3 changes_required：新 P1 F-I14C-08 重复 key；r4 已交独立复核）、I-05-A（r2 修复待复评）、I-06-A（blocked，D-W06 未签；OPEN-2 幂等键缺请求身份）。**在跑**：I-08-B（实现完成，独立复核中，含 CONFLICT-1/2 待裁）、I-09-A、I-11-A、M09–M28。全部改动留 execution_runs/<card>/<attempt>/ 各自 review.md；**生产零代码合并**（历史事故：I-14-C 曾直接改生产工作树，已由父代理回退为 HEAD；2026-09-20 巡检另发现两处越界写已处置，见 findings.md 隔离巡检节）；产品资格均限实施声明范围。

## Current Phase
Phase 1–6 complete。历史审查和面向较弱模型的执行计划细化完成。**Phase 7 实施推进 started**（计数经 2026-09-20 验收记账审计修正）：**19 张盘上可核的独立 `accepted_scoped`**（I-00-B/C/D、I-01-A、I-02-A…E、I-03-A…D、I-04-A、I-04-B、I-14-A）+ **8 张条件性接受**（I-04-C、M01–M07：r1/r2 确有独立 `accepted_scoped`，但最新修订轮的点复审尚未返回）+ **T BD 待补裁决**（I-00-A：盘上最新结论为 `changes_required`，errata 修复**未见 reviewer 确认**；I-08-A：盘上最新为 `changes_required（收窄）`，review.md 的 R1–R14 全部未勾选；I-15-A：仅"证据/诊断"范围、产品实施 `blocked_by D-W15`）。M08 = `blocked`（owner 三步）。**不再使用单一"28/86"口径**（那是按会话内回传统计的，与盘上载体不符）。审计另确认本计划存在两种 reviewer 工作模式：模式一（reviewer 亲自撰写 `review.md`：I-00…I-03 共 17 张，结论为盘上事实）与模式二（reviewer 零写入、产物只在 `%TEMP%`，由实现者转录：I-04-A/B/C、I-07-A、I-08-A、I-14-A、I-15-A、M01–M08，其结论此前**只存在于会话**）—— 收尾动作是把模式二的结论落盘（见 `progress.md` 同段）。全部 iso-副本资格，不含生产部署。

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
- [x] I-04-B 实施卡（隔离副本：退避改"返回后重算剩余"、请求预算去 `max(10,…)` 下限、清理独立 C、探测 `min(20,相位预算)`、信封分账字段；修前 RED 5 failed→修后 10 passed，T-FILING 126 passed；两轮复审：r1 changes_required 1P1/4P2/5low 全处置 → r2 **accepted_scoped**，条件 C1/C2 均已处置）
- [x] I-04-C 设计卡（跨进程 lease/所有权/恢复协议；三轮复审：r1 changes_required（ADR-10"最后退出者非 owner 且无义务"分支会留永久 paused、认领周期缺 owner 证据校验、计数/报告不符 9/16）→ r2 修 → r3 **accepted_scoped**；随签 **C1**（§13.5 与 review §1 P3-4 的 F-LK2 过时值 `[12,19,7,26,43]`）**已关闭**（真值 `[16,35,10,56,18] ⇒ lost [184,165,190,144,182]`，`verify_flk2.py` 13/13，父代理复核 hash 与只追加证明），**C2**=OPEN-3（60 s 上限命名/边界 + `worker-pause` 是否留在锁内）登记为 **owner 裁定项**，明写不阻塞签收）
- [x] I-07-A（accepted_scoped；更正：`config.legal_fifth_root` planned 计数、census 真值 3440 组、`future_lake` 实为 1 行 `README.md`）
- [x] I-14-A（accepted_scoped，仅隔离测量修复；D1 未签 ⇒ 不提升进 `RF/tools/`；bundle 未测量恒 exit 2 属契约变更）
- [x] M05–M07（**仅 formula 资格**，accepted_scoped）；M08 **blocked**（owner 三步：裁定读法 C 权威 → owner 更正 `card_M08.md` L42 与 `model_cards.md`/`dispatch.md` → 同 `code_root` 复跑留档）。**更正目标须按实测**：四文件印的是 `手算：100+40−5−10−15−60=50；−15重估必须剔除。`（各 1 处），并非早先流传的 `100+40−5−10+−15−60`；读法 C 的带符号呈现应为 `100+40−5+−10+−15−60`，期望 `[50]` 不变
- [ ] I-14-C r4 独立复核中（r3 新 P1 F-I14C-08 重复 key 已修：`iso/product_fixed/observability.py 049f5d5b…`；保真判据已进 runner，rc=2；C12 硬前置、C13 冻结）
- [ ] I-08-B 独立复核中（CONFLICT-1 subprocess 豁免集、CONFLICT-2 golden 刷新待裁）
- [ ] I-05-A r2 复评中；I-06-A blocked（D-W06 五问未签，OPEN-2 幂等键缺请求身份为决定性）
- [ ] I-09-A、I-11-A、M09–M28 实施中；其余（I-04-D/E、I-05-B/C、I-06-B、I-07-B/C/D/E、I-08-C、I-09-B/C、I-10-A、I-12-A…E、I-13-A…C、I-14-B、I-15-A 产品、I-16-A/B、I-17-A/B、M29–M31）按调度表与 owner 门推进
- **Status:** 28/86 卡 alpha accepted_scoped（含 M01–M07 仅公式资格、I-14-A 仅隔离测量、I-15-A 仅证据资格）；M08 blocked、I-14-C/I-05-A 复评中、I-06-A blocked；全部 iso-副本资格，不含生产部署

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
