本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-00-A — 冻结基线与隔离范围
Parent：I-00。依赖：无。Owner：集成负责人。资格：只读基线，不是修复。

必读：../audit_report.md的现场边界；../evidence/final_integrity.json；../evidence/concurrent_normalizer_verified.json。允许写：本次执行记录和新建隔离目录；禁止写三仓产品、raw、生产DB和worker状态。

1. 记录当前三仓绝对路径、HEAD、dirty清单、实际技能入口与解释器；Git ownership失败保留错误，不能以空HEAD继续diff，不改全局safe.directory。
2. 计算拟修改源和配置的hash；区分原有dirty与本次diff。后续卡按需要扩充基线，不要求无关文件全仓重哈希。
3. 从已存在配置读取data roots、catalog位置、worker控制文件和安装路径。记录环境变量名称与非敏感配置指纹，密钥不入日志。
4. 制定隔离映射：三仓源码副本、配置副本、独立DB与输出目录、禁网络默认。若worktree不包含用户未提交改动，明确复制哪些文件与hash，不静默遗漏或提交用户修改。
5. SQLite使用支持的一致性备份/只读snapshot；确认输出在隔离目录。禁止仅复制活跃DB主文件而遗漏WAL；若无安全快照能力，卡标blocked，由存储owner解决。
6. 隔离进程列出实际加载模块和所有有效写目录，确认没有回落到生产默认路径；此检查前不跑scan/fetch/worker。

验收：三仓路径和版本可追溯；故意留一个未绑定写目录时禁止执行；旧用户dirty仍在。恢复：只停本次隔离进程，保留基线，无生产状态可回滚。交付baseline.json、paths.json、snapshot说明及独立检查。
