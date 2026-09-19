# wiki legacy / CW / 早期专项独立审查

## 最新覆盖状态（2026-09-19；取代下方早期进展）

本分区46文件已闭合：15473原文块=14966语义位置+507结构标签，pending/extra/duplicate均0，详coverage.json。docs/archive17交root完成，详../wiki_archive/coverage.json。根task/findings/progress、三恢复版本、全部root context与四专项完整阅读；两业务日志1066事件逐工程遥测审查，非逐投资事实复核。额外污染26组3886条工程计数/当前完整条目缺席校验与42个receipt/机制补充项已落盘。最终结论和后续实施步骤见review.md。原CW全门与后继WR窄修复分别裁决，未继承或抹去任何历史PASS。

新增收据复算：三raw pilot真实增量相符，但连续样本窗口约29分钟与summary37.1/42.7/44.5总耗时不同。Step6 linked capture只有tag0/null；后继脚本截断已修，当前采样标签累计29/88/207秒由exact AST纯探针重现。原始数据与hash在wr_receipt_checks.json。所有纯测试仅审计临时/内存，无生产动作。

2026-09-19 history_filing 第二波。仅审查写本目录，不执行历史命令。范围含root旧CW、docs/archive、四专项(portfolio-reuse-fix/automatic、core-section-extraction、catalog-space-remediation)及污染清理工程计数；worker重叠原文向worker审查者请求证据映射。当前此文件不是完成声明。

已读取：AGENTS职责边界、task_plan根开头130行、CW恢复开头100行、v2开头130行、两log首尾和结构；portfolio-reuse-fix四文档全文。

初步语义：
- 2026-07-16 BOUNDARY-0正式退役投资研究Wiki/估值/投研accepted；旧4月目标缺失不能简单认作当前bug。
- portfolio Strategy A历史曾复制文件到companies以复用，后来rollback/superseded Strategy B。旧全链路PASS验证的是“提升后的companies副本”，不是原始portfolio唯一副本可直接消费。
- Strategy A计划正文Phase2–6全completed但子任务大量未勾；后置关闭解释为空框不再活动。原目标包含revenue source/capture(T12)、第二公司与广泛去重，叙述的金山云几个年报不能证明所有目标。
- 同一progress尾部重复插入早先“仅方案/未动代码”，单看最后段落会倒退状态；必须有事件时间及supersedes，不宜通过首尾字符串决定完成。
- 新真实失败的“canonical file written but exact identity did not resolve”曾在Strategy A历史出现过，但旧根因是顶层market字段，本次是v2 scanner adapter配置；相同外层错误不证明同一bug反复回归。

待审范围仍很大；不得把分节/清单生成称为逐项审查。

## 第二批进展（2026-09-19）

- 四专项17文件全文读取、当前对应模块CodeGraph与代码对照完成，791条独立block语义记录，99结构标签；special_pending=0。多数历史数量只判historical_only，不伪称重跑。存为special_item_ledger.jsonl/CSV。
- 根task_plan.md:1595–4417（CW恢复/2.24–31）全文逐段读取，1871条语义记录、100结构标签，cw_pending=0。大量严格原合同缺完整收据被判insufficient_evidence；这不等于当前所有功能都坏。
- SectionQueryService纯临时SQLite探针完成：failed旧版本/缺文件/错sourcehash/不存在spans仍普通返回；多版本返回旧项，SQL无排序/版本状态过滤。section_probe.json含源码hash，未访问生产。
- CW2.28全部11attempt索引hash复算一致，但当前既有validator检查实际目录报5个错误：phase9 PASS但failed/skip/xfail；phase10 candidate不在schema，invariant passed=null。cw228_receipt_check.json。
- 相同helper另有临时fixture反例：旧phase0 PASS、新index指向phase0 FAIL、phase1 PASS，validate_chain返回空错误。用any历史PASS而非index选定最新有效PASS；空commands/invariants仍可通过schema。
- 原phase4R只有978/23789fingerprints、4retryable、worker下次登录才启动仍PASS；7R未交付dirty仍PASS；10R自己明确Independent reviewer not available。总汇2796–2799升级为completed缺证。候选本身是正确限制，错误在汇总越级。
- 尚未完成：根task1–1594/大部分findings+progress、CW恢复版本逐条映射、root其它文件和docs/archive、两log工程遥测entry、污染移出工程计数；这些未被本批ledger计入已审。
- 工具错误：一次apply_patch只给函数行前缀未匹配而拒绝，未落盘；改为添加完整独立范围修正。几次宽读输出截断已通过具体文件/范围补读，未把截断部分当已读。
