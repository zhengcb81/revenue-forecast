本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-07-D — 故障矩阵与断点恢复
Parent：I-07。依赖：I-07-B、I-09。Owner：独立故障验收者。

输入：矩阵F01—F06与各专属卡oracle；允许：scratch进程/DB/registry。产品stdout异常与raw rc必须保留。

1. 每个故障单独attempt，恢复初始隔离状态，避免前一个case污染后一个。
2. 分别在provider返回、raw提交后scan前、scan错误、DB事务内锁等待、producer执行、发布提交边界注入；记录实际触发位置和发生次数，没触发的测试无效。
3. 检查失败时没有可消费的伪合格结果；已有raw保留，错误cause/code/retryability不丢失。
4. 清除故障后从原入口重试；比对新增下载/写入/调用数，不能靠重建全部资产掩盖幂等缺陷。
5. 杀进程只针对本case记录PID，确认进程归属隔离树；不操作真实worker。

退出：每个触发点有前后状态、错误与恢复证据；不能以单一“抛了异常”通过。无可靠注入能力先blocked。
