本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-14-A — 性能测量先验证失败分支
Parent：I-14。依赖：I-00-C。Owner：测量负责人。

锚点：RF/tools/slo_probe.py；RF/tools/tests/test_slo_probe.py。允许修改测量器和隔离测量测试，不放宽既有预算。

1. 读当前子进程启动、rc判断、业务输出解析和RSS采样；记录单位与时间锚点。
2. 三个固定进程夹具：exit7且stdout似成功；exit0但业务结果失败；进程存活时分配可测内存后退出。前两者必须判业务测量失败，第三者需有PID匹配的存活期间样本，未采到不能记峰值0。
3. 单独冻结采样间隔、平台可用的peak方式和测量误差规则，由运维reviewer决定；不把合成内存量等同精确RSS oracle。
4. 保持现有exact/latest/bundle p95=5秒与peak_rss_gb=2的预算约束，改预算需独立理由，不随测量失败改阈值。
5. 成功延迟分布与失败率分开报告；不丢失败请求来宣称服务满足SLO。卡通过仅证明测量器，生产SLO需I-16实际测量。
6. 当前源码还有两项必须纳入边界：`--catalog`只检查存在，实际resolve使用config；`bundle=exact[:]`是代理计时。绑定catalog与config不一致必须拒绝或证实实际目标一致；测真实bundle消费路径，不能以复制exact延迟授予bundle资格。沿用原proxy历史记录但明确范围。

退出：三种夹具行为正确；命令总耗时/业务延迟/采样窗口分别记录。恢复：回退测量器隔离差异，不碰生产服务。
