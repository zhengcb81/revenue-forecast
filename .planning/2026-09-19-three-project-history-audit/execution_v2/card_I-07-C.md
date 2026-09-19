本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-07-C — 跨根与未知公司泛化
Parent：I-07。依赖：I-07-B。Owner：独立验收者。

输入：矩阵X01—X05。允许写：隔离root/config/catalog；真实外部根只读。必须有高级reviewer冻结适配器支持范围。

1. 对同bytes多根分别核对hash/location，不以root计数当不同来源。
2. 在隔离配置增加此前未命名的同构第五root，使用新root名和非fixture公司；以相同支持的adapter/profile完成scan/resolve。
3. 对未知布局给明确unsupported，不自动猜身份/adapter。
4. 对companies-only/dayu-only/external-only分别跑；仅隔离构造可支持隔离资格，真实external-only缺样本保持blocked。
5. reviewer在测试前固定另一家公司/文件作为保留泛化样本，验证无按公司名硬编码；不得临时换成已成功公司。

退出：每个格单独结论，无外部only实证就不签该资格；它不阻止与其无关的已验证本地读场景。
