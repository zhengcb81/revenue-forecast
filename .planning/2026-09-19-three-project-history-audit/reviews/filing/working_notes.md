# filing-fetch 独立历史复审工作记录

2026-09-19，独立代理 history_filing，加入 root 的共享计划。本目录仅审计材料，不修改生产代码/配置/index/worker。

已读取根三件套、PLANNING_STATUS、TERMINAL_NOTICE、CHANGELOG、E2E_DESIGN、FC-903 contract/reviewer report、filing_contracts 当前代码。CodeGraph 已用于文件结构和符号入口。

初步发现：
- 根计划被明确限定 completed_historical_scope；TERMINAL_NOTICE 又标 closed_superseded_incomplete。117/117 accepted 不等于现阶段真实请求闭环。
- Phase3/4存在样本调整、放宽断言和合理缩小承诺：HK目录改 canonical 名、茅台双候选换宁德时代、HK FY2024改FY2025、损坏修复改拒绝、staging无目录改无字节。每项须区分原目标解决与测试范围改变。
- 2026-09 E2E_DESIGN承认 synthetic T1 only；当前 inventory 将此文件列为 unselected，应补入关联实施/验收范围。
- 当前 request 代码支持 schema1.2，SKILL_VERSION仍1.2.0，技能frontmatter1.4.0；版本号不直接说明是否已部署同一行为。
- FC-903 历史审查报告承认diff超预算但仍accepted、单调用点与implementer声称两调用点不符；收据hash需要重算。

下一步：逐条建立历史项台账，审当前代码与测试范围，隔离重跑合同测试并校验安装副本/hash与实际失败日志。

审计操作错误：自建只读runner第一次父目录索引多取一级，cwd不存在导致WinError267，未启动测试。已修runner路径；不是产品故障。
