# I-00-D 预期与干读检查（2026-09-19，新模型视角、只读活动指南）
Q1 唯一入口：company-wiki 现行维护规范入口为 AGENTS.md（职责边界最高优先级）+
README.md（source_catalog 使用）+ docs/source-catalog.md（完整语义）；
revenue-forecast/filing-fetch 各自 SKILL.md 为其技能唯一入口。
Q2 不启动旧writer：AGENTS.md 职责边界（2026-07-16）明确“不得新增研究型 writer”；
CLAUDE.md 顶部增设时代边界横幅（本次修改），旧研究生产职责已退役转 StockWiki。
Q3 不擅自resume：README.md 边界提示（本次修改）记录 worker desired_state=paused、
禁止代理自resume、恢复仅I-16卡；filing-fetch SKILL.md 第4条：用户暂停永不自动恢复。
Q4 不重复下载已有raw：filing-fetch SKILL.md v1.4.0 reuse-first（找不到已索引才在
授权后下载）；sample_manifest 3/3 样本 hash 已核实存在。
干读结论：四问均有指向当前代码/契约的答案；DEPLOYMENT*/OPERATIONS*/使用说明书←不存在，记录为NA。
