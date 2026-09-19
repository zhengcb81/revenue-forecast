本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-07-B — 三市场来源链与二次复用
Parent：I-07。依赖：I-07-A、I-01、I-02、I-03、I-04、I-05、I-06。Owner：独立验收者。

入口：安装态RF/scripts/source_preparation.py；具体argv按I-00-B，不调用helper冒充。案例：scenario_matrix的CN/HK/US各三状态、重复请求、注册失败恢复。

1. 固定每case初始asset/catalog/worker状态及provider/scan/read/producer事件计数；真实调用数不能由artifact INSERT推算。
2. 按已冻结命令运行一次，检查来源链各阶段：raw→注册→资格→review→适用工件→实际消费。正确拒绝要同时返回可执行恢复需求。
3. 同输入第二次运行；已有有效raw两次都不下载，第一次注册恢复后第二次不重复注册有效版本；工件有效不重跑producer。允许的只读query不强制0次。
4. 核对handle身份/hash/期间、真实读取内容、consumer输出，不仅json字段存在。旧失败样本必须回到同用户入口成功或得到明确尚缺信息。
5. live provider测试单独记录网络调用与授权目标；provider不可达不能用mock补签live。

退出：固定案例各有实际结果；三公司仅来源准备通过，仍未授予正式预测资格。缺一市场/真实路径不得总体写三市场通过。恢复：保留已取得raw，只回退当前隔离变更。
