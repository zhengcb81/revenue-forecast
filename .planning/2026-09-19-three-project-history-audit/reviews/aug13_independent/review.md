# 8 月 13 日两项计划全文独立复审

日期：2026-09-19。范围为 `audit_review/2026-08-13_three_repo_completion_rebaseline_plan/` 的 15 份 MD 与 `audit_review/2026-08-13_zijin_data_lake_remediation_plan/` 的 13 份 MD。已阅读全文 3,818 行；2,959 个非空原文行中，2,497 个语义 occurrence 进入账本，462 个标题、分隔等上下文单列；97 个人工语义判定，pending/extra 均为 0。数量是追踪覆盖，不是故障数量。

`manual_cases.json` 是人工区间判定；`item_ledger.jsonl/CSV` 保留每条原文、原文件 hash、行号、判定理由和当前证据。CA/ZR 原单元的更细逐 ID 审查由 `../revenue/item_ledger.jsonl` 提供；本分区全文复核原需求、历史观察、治理规范及自审，不直接继承它或历史文档的 PASS。

## 核心结论

原计划不是没有想到这些风险：它在 8 月 13 日已经明确禁止将 fixture 当真实运行、marker 当场景通过、脚本存在当动态运行、自然时间未满当终验完成。**这批计划的 26 个内容文件和 30 个输入快照，本次重算 hash 与 size 全部匹配。** 关键问题发生在后继执行卡与接受条件：原业务义务被缩为局部机制检查，reviewer 按缩后的卡接受，机器 DAG 再用 accepted 标签推导原始总体目标完成。文件锁、hash、自审和测试总数没有保护原始验收语义。

这不意味着测试结果都是伪造，或者所有旧修复都无效。CA105 原 reviewer 如实报告 `unsatisfied=197`；ZR409 的 Dropbox MISSING 是正确的安全拒绝；CA302 reviewer 也公开记录第二矿企与非矿复用紫金文档。这些局部陈述有价值。错误在于随后没有保留相应强业务义务的未完成状态。

## 可独立追溯的缩范围链

| 原承诺 | 后继卡/收据的实际范围 | 独立结论 |
|---|---|---|
| CA registry:150–154：真实连续 7 Daily、2 Weekly、1 Monthly、1 drill；未满只能 pending | `receipts/CA-206/00_wu_card.md:9–26` 引用原强承诺，却明确不做真实累积，仅在测试文件实现纯函数；同日下午 accepted 并解锁 CA301 | 计算器通过不能兑现自然累积；原未完业务义务从 DAG 消失 |
| CA registry:158–162：三个干净 checkout 精确 candidate 全量独立重放 | CA301 card:13/26 明确不做真实 checkout；reviewer finding005 将未断言 candidate checkout 判为卡外部署 | 仅证明 git 对象存在、环境收集、receipt hash 和状态存在性 |
| CA traceability:76–96：紫金、第二异构矿企、非矿三个独立真实来源旅程 | CA302 card:13/27 排除下载/worker；reviewer finding002/003 承认 partial/stale/amended 未直接覆盖、C2/C3 复用紫金 | 合成引擎/模块核算可保留，但不支持跨公司、供应商和 worker 全链终验 |
| CA registry:176–187：真实分批 R9 删除/回滚，六问题机器闭环 | CA304 card:12–26 禁止真实删除，以临时 CatalogStore 激活往返为验收；CA305 `test_c2/c3/c4` 实际查 accepted、文件存在和 hash 长度 | 机制与部署必须分节点；后续 GP 真删除按批另审，不将此历史缺口无限延用 |
| CA authoritative:166–175：ZR1101–1105 由更强 CA301–306 替代，不可再走较弱收口 | 当前 state 的 CA306.next=ZR1101；ZR1104 card:13/26 再次明确不做自然累积 | 后继 ZR 收口没有补回被 CA 卡移走的真实义务 |
| ZR409 card:31/42：三个真实 root 均正向 exact 复用 | reviewer REV001 证实 Dropbox 实际断言 MISSING；REV002 证实 catalog-dir 指纹未执行；REV004 记 53 独有年报均无合格 capture-ready 候选 | 安全拒绝支持负向门；不能顶替 Dropbox 独有正向复用；未跑正向不是产品安全拒绝本身的 bug |
| ZR READ10:52：锁持续至 deadline 后有界失败，保留阶段证据 | current `scenarios/evidence/READ_10.json` 指向 `company-wiki/tests/unit/test_zr304_read_model.py` 的 9 个 artifact/journal 测试；该 297 行文件无 retry deadline 场景 | 原业务义务和证据文件错配；filing 隔离探针首调用模拟耗 9 秒抛 busy，旧 remaining 又允许 5 秒退避，预算 10 的模拟 clock 到 14 才报超时。不是第二调用耗 5 秒或 14 秒墙钟实测 |

上表 `receipts/` 均指 `assurance/unified_completion/receipts/`；源头章节与完整原文行见账本。两份 `TERMINAL_NOTICE.json` 的 `closed_superseded_incomplete` 本身是诚实归档词；其引用的 117/117 accepted 不能另行解释为原业务义务全部满足。

## 71、95、117、197 到底证明什么

1. 71 是旧 FC 唯一 ID 数；5 个 FC150x 已含在 71 内。`completion_assurance_registry.md:47` 的“71 FC + 10 波次 + 5 closure”可作为分组覆盖，但不能无解释当 86 个唯一旧义务；唯一旧 ID 是 71+10。
2. 95 个旧场景与 102 个新场景相加为 197 个唯一场景，是设计覆盖计数。原 `PLAN_MANIFEST.md:58` 明确 required tier 展开后结果更多，不能按 ID 出现计 pass。
3. 本次读取 current scenario registry：197 项均 `passed`，197 项 `fixture_hash=null` 且 `oracle=null`。196 份证据只有 `executed_at, passed, repo, scenario_id, summary, test_file` 六类字段；READ11 为单独的 SLO JSON。不能由这些字段认证所有 required tier、具体输入、triplet 与独立 oracle。
4. 本次精确提取当前 `uc/scenarios.py:143–156` 的纯 `closure_report` 函数，不 import 产品、不访问 DB/网络。去掉全部 evidence、tier、hash，仅给 197 个 `status=passed`，仍返回 `closure_ready=true`。**该反例只针对这个函数，不声称每个发布门都只有此检查。** 原代码 hash、输入与输出保存在 `checks.json`。
5. CA305 的 `tests/test_ca305_six_problems.py:98–211` 将六问展开了，但其 oracle 仍是状态/收据文件/test文件存在、40 字符 commit 与64字符 hash长度；把六个问题分行不等于六个真实业务结果经过验证。

## 计划内部需在下一版消歧的内容

- ZR `task_plan.md:149` 写无授权仅 discovery；`architecture_target.md:219` 写无显式授权不 discover/fetch；后 CA `traceability_and_acceptance.md:32` 要三动作均 0。应明确后版本覆盖和各操作的副作用定义，不把“发现”一词既当本地只读又当外部请求。
- ZR task、runbook 与 CA registry 有三套不同粒度状态词，缺机器映射。应先定义原义务层与实现阶段层，而不是用单个 accepted 混合“代码、部署、自然观察、业务结果”。
- ZR 动态门有 36h/9d/35d，后 CA 要 24h/7d/35d；计划升级可以收紧，但必须将版本与部署接受条件一起冻结。
- ZR runbook 的 mandatory expected-failure 禁行，与后 CA 的结构化 `expected_failure_pass` 需要明确区分“期望的安全拒绝”与“正向用户任务完成”；两者不能互相替代。
- RED 仅为 `glob tests/**/*ca206*` 找不到文件，只能证明缺测试文件。应至少有原用户入口产生期望失败的可重放行为反例。

## 历史边界与后续实施步骤

本次没有重建 8 月 13 日数据库来核对每个历史数值；旧 artifact/summary/LLM 标签数量仅保留为当时观察，不由此推断真实出站或未授权处理。没有把旧 3.6/3.7 模型缺口直接照搬到 4.1；9 月之后的 GP 修复、真实任务接线和分批删除由其他分区按当前证据保留。全文审完意味着每条都完成范围与证据充分性判断，**不等于每条都被证明成立**。

下一轮应先做以下工作，且每一步独立保留未完义务：

1. 给冻结原规范建立 obligation ID，绑定源 hash/行号、行为 oracle、所需 tier 与生产入口；卡片不得删除原义务。减少范围必须附正式 disposition 及仍阻总体关闭的 successor。
2. 将机制代码、部署接线、自然观察、真实用户结果拆成独立节点。CA206 计算器可机制通过，但自然累积必须 pending；所有依赖业务就绪的终验仍阻断。
3. 修场景证据模型为 `scenario × required tier × candidate × environment × sample`，保存真实 command/stdout/stderr、收集/跳过数、业务 outcome、输入与独立 oracle。先消除 READ10 错映射，补预算超时负例。
4. 由独立 agent 从原目标反向审卡，不仅重跑实施者所选套件；禁止以透明披露卡外缺口作为取消原承诺的依据。
5. 再跑三个独立公司文档的 source→filing→索引→worker/ready→模型→发布→二次复用，分别验证 existing 与 authorized-missing；外部 root 必须有唯一物理样本，安全拒绝另计。
6. 现行自然运行证据按实际任务、部署路径、候选版本与日期验收；真实回滚按批执行。只有所有原 obligation 有业务通过或用户认可的取消处置时，才允许总体 terminal。

这轮仅新增审计文档、账本和只读纯函数探针；未修改产品代码、配置、安装技能、历史文档，也未启动 worker、生产 DB 写入或下载。
