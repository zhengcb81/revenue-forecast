# 主审第二波复核与更正记录

2026-09-19，root。复核对象是各分区结论、有限通过范围与新计划，不把各代理身份当充分独立性证明。

## 已复核的内容

1. 完整读取 filing、wiki_legacy、aug13_independent、wiki、revenue 报告；复核原始探针脚本、重要日志和逐条账本代表的判定对象。history_filing 再交叉复核 revenue 的全部31模型和24深层条款；audit_independent 再交叉复核 root 的 ER49、A09 68、CC58，共175个人工case。二者均从原文/源码/原始证据核对，没有将生产者总结直接当批准。
2. root 独立重算8/12紫金草案：从参数逐分部、逐年乘法还原15个公司总额，最大差0，原结果文件hash与post receipt相符。保留低置信draft边界；不承认概率已校准或研究充分。
3. root 重算9/18—19实战13份stdout/stderr日志hash，全部匹配；20个原件location、8个派生物和2个新raw共30文件仍与原审计hash相符。仅证明这些文件/记录的当前完整性，没有重新运行下载或正式forecast。
4. root 通过 CodeGraph 定位并完整读取 source_preparation 当前223行：artifact_read来自角色选择，producer_events为重算计划；not_reviewed在需求登记前抛错；队列进程内、now=0。认可已有raw hash验证，未把“没有实际artifact读取”夸大为“完全没有字节校验”。
5. filing deadline 探针首调用模拟耗9秒、剩余时间未刷新再退避5秒；两线程refcount探针强制双方先读再串行写，证明逻辑丢更新，不宣称已观察生产误resume。FC903 raw与LF规范化hash均不符只证明收据绑定失败，不能推断动机。
6. wiki 冻结51文件与315/115结构检查支持规划完整性，未用于认证产品实施。GP002的参数传递本身已经修复；root×adapter×policy生产组合仍失败是另一个命题。SectionQuery、prune和脱敏反例均限定隔离/静态路径，不声称已发生生产数据损失。
7. 8/13原规范26文件+30输入快照hash完整，却仍有原义务→窄卡→accepted的语义断裂。197场景的closure_report反例只针对该函数；不声称所有发布门只看status。

## 本轮纠正的判断与引用

| 项目 | 纠正 | 结论 |
|---|---|---|
| ER 早期F11 | 原文就在质疑可信来源，不能因后继过度宣称而反判原质疑错误 | 原质疑supported_scoped；当前host_signed反例另列 |
| A09-042/044/047 | 原规范合理，证据不足针对后继声称已经满足规范 | 明确assessment target，避免批评错对象 |
| A09-045 | selector合同明确file reads=0 new | 局部selector修复supported；后继真实消费外推另判insufficient |
| CC-050 | current_probes.json不存在 | 改指readonly_diagnostics.json及historical_git_readonly.json |
| CC-052 | “pause未恢复正确”有歧义 | 改为结束仍paused、保留用户暂停意图 |
| 主报告13次 | 包含catalog status与来源准备 | 改为前置流程/诊断命令，不称13次forecast |
| wiki Git证据 | 首次ownership拒绝却被工作稿误写成功 | 保留原exit128；补独立单进程safe.directory成功原文并修引用 |
| 矿业TC示例 | 800不是所有合同唯一正确结果 | 先指定saleable/payable、数量基数、币种及TC/RC单位；payability不得重复扣 |
| 全局完整性 | 不能沿用上轮357文件全未变 | 本轮356/357相同；normalizer并发提交差异单列 |

## 并行修改与证据截止

本审计作者及三位分区审查者只写本新计划目录和隔离scratch，均确认没有产品编辑。357文件旧基线逐项重算中，356相同；normalizer.py的旧hash `0825c9f8…` 与 `f39bd5a^` Git blob相同，新hash `772075ed…` 与 `f39bd5a` 相同。Git提交作者记录为另一agent，具体修改是backfill第二处locations读取异常守卫；本轮未替该并行修复签发新的运行通过。R4三份MD新段落由revenue审查者补读并更新阅读hash。两次尝试用初始空HEAD作diff失败，原失败记录保留；成功证据是明确revision的Git blob核对。

生产source_catalog.yaml、runtime_policy.json、worker_control.json与本轮初始副本字节完全相同。仅对这些列明文件作不变声明；没有用活跃DB字节hash证明全库未变化。新审计完成不会自动替当前其它任务关闭工单。

证据：`../../evidence/final_integrity.json`、`../../evidence/concurrent_normalizer_verified.json`、`../company_cases/independent_checks.json`、`filing_cross_review.md`、`../wiki/cross_review.md`。最终覆盖必须由master_coverage逐路径汇合，不能由本报告文字代替。
