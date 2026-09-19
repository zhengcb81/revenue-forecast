本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-00-D — 活动指南与退役边界
Parent：I-00。依赖：I-00-B。Owner：三仓文档负责人。

必读：三仓当前SKILL/AGENTS/CLAUDE/README/DEPLOYMENT/OPERATIONS中实际存在文件、审计报告退役项；不存在的文件记录NA，勿为凑齐创建。允许改：活动指南；历史planning和收据只加导航关联，不改原结论。

1. 列出现行入口、唯一writer、raw新写入和外部根复用的不同规则；核查与实际配置/调用一致。
2. 标明退役研究writer、冗余markdown producer、取消迁盘；删除活动操作指引中的过时启动动作，保留历史文档原貌与时代说明。
3. 对capture真实获取日与as-of重建边界、schema版本、review恢复入口写条件和失败分支；未实现的命令标未实现，不能用文档发明能力。
4. 用“新模型只读活动指南”的干读检查：能找到唯一入口、不启动旧writer、不擅自resume、不重复下载已有raw。

验收：四个干读问题都有指向当前代码/契约的答案；若入口尚缺，链接具体未完成卡。恢复：只撤回本次活动文档差异。
