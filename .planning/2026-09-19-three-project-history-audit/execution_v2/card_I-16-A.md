本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-16-A — 绑定拟部署完整组合
Parent：I-16。依赖：I-07-E、I-07-D、I-08、I-09、I-13、I-14、I-15。Owner：部署负责人。

允许写：部署提案与隔离安装目录；生产变更尚不执行。

1. 列三仓源commit+dirty内容hash、安装副本hash、解释器/依赖、config/policy/flags/schema版本及真实加载模块；不能只比较仓库HEAD。
2. 在新进程检查加载路径，与安装副本及预期组合一致；用旧加载模块的负例证明能发现版本错配。
3. 记录上个可恢复完整组合、迁移是否可逆、raw/registry/catalog兼容边界。不能证明恢复则blocked，不以关闭严格门回滚。
4. 对部署影响范围列出具体写入、停止/重启进程和恢复步骤；按既有授权执行可逆准备，真正未授权影响再向用户说明具体请求。

退出：提案与恢复演练在隔离环境通过；资格仅“可进入具体部署窗口”，尚非已部署。
