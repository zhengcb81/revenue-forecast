# F4 RF 已有作业的多根冷读

## 问题与改动

总控登记的 RF 默认数据根里查不到 W12 的作业。原 W12 资料根仍持有可读取的作业、阶段和费用终态。旧 `reconcile` 只接受一个有效 `--owner-root`，传入多个值时 argparse 实际采用最后一个，结果依赖参数顺序。

本仓只改 `scripts/rf_job_feedback.py` 的确定性读取和定向测试。可重复提供本机已配置的 `--owner-root`。读取只经 `JobFacade.get_status`，路径经既有原生路径处理和解析后去重。仅真正缺该作业的根能视为空。多个命中的副本需有一致的作业身份、原范围及开始时点、阶段尝试、结果证明和结算。不同定义返回 `native_owner_conflict`，已有但无法确认的记录返回 `native_owner_unverified`。单根格式和原阶段错配规则照旧。旧 CLI 失败的原诊断仍走原历史端口。

    python -B scripts/rf_job_feedback.py reconcile --owner-root <默认数据根> --owner-root <已登记的另一个RF数据根>

标准输入保持 `feedback-action/1` 原发生及证据。读取使用明确参数中的目录。任意观察中的路径字段不决定查找范围。

## 验收

- 独立候选起点 `fec37c6a3bfb66c23e5a4816f9c046e96407586d`。四项 RED 分别复现最后一个根漏作业、同编号不同发行人范围误报完成、损坏副本被另一个覆盖、重复根接口缺失。修复后用真实持久化作业和外进程读取核对双顺序、匹配副本、冲突与路径去重，温读和冷读均不写资料根。
- 身份、F4、成本、状态四文件合计 42 项通过。`ruff check scripts/rf_job_feedback.py tests/test_rf_job_feedback_roots.py` 通过。
- 用 W12 原 owner-feedback.jsonl 中实际 publication-1 结束观察查 `rfjob-20261120-594c00a589d1`。旧入口在正式默认根返回 unknown。按两种顺序传入默认根与原 `revenue-forecast-audit/runs/w12-20261120-cn-603259/execution/rfo`，分别返回同一 succeeded/known；原发生 `d7c32ad822e7b453b83dfa82449f7212101652c851f8c187a00757eba6bdacea`。原 sidecar 及 18 个 RF 文件的内容哈希一致，无新增请求、费用或状态文件，临时根清理。试验收据 SHA-256 `9c0eddfc87489cf46070e9999a441c60d2ac963c48c2d9796aabde4d2324b9a2`。
- 两个功能和测试文件的 LF 汇总 SHA-256 `838c293e473679fecaf563129a6baa2bf4081eb1f82989e70b21c1eac76f104d`。按排序路径、NUL、LF 内容、NUL 计算。ROOT 独审通过，独立复跑四个真实 JobFacade 路径用例通过，并读核 W12、范围一致性和关闭行为。此处仅验证 RF 所属端口，宿主配置和实际订阅由总控另外接续。
