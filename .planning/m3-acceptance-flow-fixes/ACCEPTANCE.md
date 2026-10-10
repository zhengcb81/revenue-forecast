# M3-FLOW 收件验收及根修

收件结论：原交付不能直接认定全链路完成。12 个源测文件与 17 条原日志 SHA 一致，但交付遗漏了机制 claim 来源独立性、mixed peer、精确整月及新 schema 共享消费者负例。

## 本线已修（限定四文件）

- 机制 triangulation 按有效机制 claim 的 source_id 计数，历史来源不能凑成第二个机制来源。混合节点全部 claims/source_ids 继续披露；有效机制支持不会因同行类比被整节点删除。3.7/3.8 行为保留。
- 用日历边界验证 3/6/12 整月，取消平均天数及 ±0.2 月；完整财政年度窗口保留闰日 FYE 规则。金额未年化，stock 未改变。
- 专用 regression 包覆盖两个真实产品 RED、三个非整月反例、两个 mixed roles public compute→strong 场景、闰年/非月末 FYE/ISO 上限日期控制。

最终定点包：58 passed，9 subtests passed；ruff/mypy exit 0。工程测试全部离线、零供应商/模型调用，owned TEMP 已删除。详见 acceptance.json 及原日志。第一次 sandbox TMP 错误与 MAIN 同时编辑 report 的中间态失败均保留，不能冒认产品 RED。

## MAIN 责任

- report 的新 schema feature 消费者与 period 日期渲染由 MAIN 修复；本线 strong mixed-role 回归已与其修复组合通过。
- 更新 still-stale references/CHANGELOG/SKILL 的精确整月和 claim 来源措辞；正常 commit/push、精确 HEAD CI，定点安装。
- 原分支 --no-verify push 与旧红 CI 不构成发布验收。不改 assurance/output 及生产原件。
- 真实公司未来幅度/校准/联合压力仍后续研究任务，离线绿不证明预测准确。
