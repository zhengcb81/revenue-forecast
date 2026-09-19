# 第二波交叉审查：根汇总与 ER / A09 / CC

审查范围：根 `audit_report.md`、`implementation_plan.md` 全文；ER-001…049、A09-001…068、CC-001…058 全部人工 case 的目标、理由、证据及 verdict。对高风险判定另回读原文范围，见下表。本轮没有重新全文审读根 owner 的全部旧文档，不重复认证其全文覆盖，也没有重跑旧生产环境或全部反例。

结论：主汇总区分局部修复、部署未完、规划冻结、真实用户路径失败以及未来计划，方向成立。175 个人工 case 的判定没有发现需要推翻主结论的系统性错误。下表保留初审提出的 6 项引用/措辞/判定对象意见，修订复核状态见文末；不把本分区通过等同于主审最终覆盖已汇合。

| ID | 位置 | 独立复核与建议 | 严重度 |
|---|---|---|---|
| XW-01 | CC-050 evidence | `reviews/wiki/current_probes.json` 不存在。换成实际 `readonly_diagnostics.json`、`historical_git_readonly.json` 或 `review.md`，且 doctor 和历史 Git 的证据范围分开。 | P2 证据可达性 |
| XW-02 | CC-052 rationale | “pause未恢复正确”可被理解为恢复失败。应明确“结束后 desired_state 仍为 paused，保留原用户意图”。filing 的临时下载 scope 是有意授权设计，不能报绕过。 | P3 歧义 |
| XW-03 | audit_report 真实运行计数 | 13 个 run 包含 catalog status 等诊断，不宜叫 13 次完整技能运行。改“13 次前置流程/诊断命令”；0/3 正式预测不变。部分恢复运行发生在 9/19，9/18 是研究信息截止及审计目录名，日期勿混同。 | P3 计数口径 |
| XW-04 | A09-042 / 044 / 047 | 原文是合理质量/动态审核/独立审查协议。insufficient_evidence 应针对“后继已经满足全部协议的主张缺证”，不是声称规范要求本身为假。建议 target 与 rationale 首句写明被判命题。 | P2 判定对象 |
| XW-05 | A09-045 / 054 / 063 | FC904:13–18 明确把 `artifact_read` 定义成 valid_handles 角色列表，把 `producer_events` 定义成重算闭包；:74 明确 file reads=0 new。其 selector 接线修复应承认，名字易误导和后继字面“实际读取”外推须另判。当前 054/063 已承认元数据/选中修复且拒绝扩大成实际读内容，正确。 | P2 范围对齐 |
| XW-06 | report / implementation_plan 的最后收尾 | 覆盖、判定数、文件是否仍变化及各 reviewer 未完成项需最终一次汇合；当前草稿自己声明尚未关闭，保留该边界直到最终核对。不能用 769 个 inventory 路径直接当 769 份独立全文事实验证。 | P2 完成口径 |

## 已回读的易误判原文

- **ER-017**：`findings.md:1344–1357` 是 F11 对缺 trusted verifier 的负面质疑，不是通过声明。当前 supported_scoped 支持这个有依据的质疑；同时承认存在签名时 Ed25519 验签，不扩大为整个签名机制失效。
- **ER-020**：`progress.md:216–257` 清楚记录把敏感性 RED 从无 input 改为带 input，随后宣称四 RED 全绿、Phase3 全部满足。判原弱消费者攻击面未保留成立；后继 F02 已修要另列时点。
- **ER-022**：`progress.md:396–420` 承认 7.2 延后及若干不做，却以 phase-level 状态为权威。根判的是“completed 关闭全部原义务”的外推，而非否认当时确实只改了标题。
- **ER-028 / 029 / 036 / 047 / 049**：均明确限定真实单公司复用、撤回环境先验误诊、config-only 自我纠正或用户获准缩范围，不将这些负面/有限结论误判成实现失败。无需更改 verdict。
- **A09-038**：`implementation_runbook.md:919–952` 明确 parent-HEAD 自反、共同 PDF bytes、活跃 WAL 下不锁原 DB hash。根认可合理限制，也指出行数/schema 不能证明行内容不变；未说非稳定字节一定是审计者写入。
- **A09-042**：`code_quality_plan.md:29–58` 是原目标，含最终 branch95、单 owner、production caller、全部FC完成条件；后继 ratchet 通过不等最终全部清零。需要 XW-04 的对象澄清，不否定 ratchet 的合理性。
- **A09-044**：`dynamic_assurance_plan.md:1–68` 自己声明需要每日/每周/波次、only 样本、实际调用预算、新鲜度及持续观察；不能用纯 calculator 或一次报告闭合时间义务。该规范本身不存在因未执行而“错误”的问题。
- **A09-045**：`fc_904_change_contract.md:1–81` 为 selector 明确定义窄目标及 0 new file reads；字段名不能推真实读取，窄目标已修也不应被抹掉。
- **A09-047**：`independent_review_protocol.md:1–78` 的原要求已相当严格：干净 worktree、重放原命令/negative/mutation、原用户旅程、不得改产品。实际验收不满足它和协议文本不合理是两个命题。
- **A09-049**：`implementation_runbook.md:82–111` 在 :109 确实要求拒绝命令 exit 非零。因此保留 raw rc、expected rc、判定三个字段的建议有明确来源；不是从 JSON 示例只有0就臆造要求。
- **CC-025…047**：已逐项看范围/理由及 8/12 事件原文。合同自报安全、隔离草案、资源/储量/产量口径、HTTP200内容不符、紧邻 registry 前后相同均只支持有限结论。无下载授权+resolver reused+旧 journal 无新增支持本轮零新下载；parser/LLM 0 仍应表述为 envelope/事件计数，而非因此重建所有历史调用。
- **CC-048…058**：没有把 9/18 草案变正式结果，亦未把矿业潜在 67.31% 错误做法影响说成已发生预测误差。旧独立算术及当前 hash 支持算术/证据完整性，不认证未来假设、来源内容准确性或样本外预测准确率。

## 本轮验证程序与未来实施计划的范围

已读 `reviews/company_cases/verify.py` 及 `independent_checks.json`：它独立按输入逐年乘增长率再汇总，与结果比对，且复核旧结果文件 hash、13 日志 hash、20 location/8 artifact/2新raw hash。没有调用产品预测引擎，因此能避免同实现 oracle；也明确没有重新构造历史执行环境。它校验嵌入 result hash 与 receipt 相等，并未重新执行所有 canonical publication 校验，根文本目前没有扩大这一点。

实施计划的顺序与边界合理：先有效配置/注册，再复用/审核/工件；发布/模型可隔离并行；保持 paused、保留 dirty files、已下载原件恢复而非重下、已退役 writer 不重建、外部only缺样本不人为制造。I12 区分场景与校准区间、as-of vintage、基准和失败样本，适合防止用 tests/confidence 自称准确性提升。

建议收尾补一项明确动作：旧 API/部署/维护/故障指南加时代与退役入口提示，并与单一现行手册链接。否则实际代理可能继续按旧命令启动研究 writer、自动清理或无条件恢复 worker。这是文档修订待办，本轮没有改产品手册。

## 本审查自己的更正

根 reviewer 发现我早期 worklog 历史 Git 引用错误，已保留 exit128 原记录并新增 exit0 独立文件。又将 GP002-03 仅参数接线修复从 contradicted 改 supported_scoped。此两项说明审计结果本身也需要明确判定对象和原始证据，不为维持无错误声明抹去更正过程。

最终接受范围仅是上述文本与判定对象的交叉复核；生产产品、未来修复及整个历史全量覆盖的最终声明仍由主审汇合各 owner 证据后决定。

## 受影响修订复核

主审修改后已重新读取 A09-042/044/045/047/054/063、CC-037/045/050/052 与根报告对应文本：XW-01、02、04、05 已解决；XW-03 的 13 命令口径已解决。“9月18日实战”仍为审计名称式简称，建议最终写成“信息截止9/18、延续至9/19的实战审计”避免日期歧义，非改变实测结果。XW-06 属主审最终统计汇合，不由本分区替代签收。旧操作手册加退役提示为后续实施建议，不要求本轮改产品文档。

另发现并行工作区 normalizer.py 字节变化，本 agent 未写该产品文件，也未验证其新运行行为。不得以本次审计的旧快照推断整个 workspace 静止或新 normalizer 已通过。主审已核三个生产配置/策略/worker控制文件前后字节相同；该有限完整性和全仓不变是不同命题。
