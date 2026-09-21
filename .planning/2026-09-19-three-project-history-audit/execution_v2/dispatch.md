# 调度表：原义务→执行卡

本表从卡片索引生成，不执行任务，不自动授予ready。所有卡planned；先读[执行协议](START_HERE.md)。上级完成还需原义务和用户旅程，不只看子卡计数。

原始依赖写I-xx表示其全部适用子卡；精确展开见[dispatch.json](dispatch.json)。若只需要某个子结果，必须显式改为子卡ID并说明依据，不能执行时自行跳过。

| 卡 | 原义务 | 标题/正文 | 前置卡 | 状态 |
|---|---|---|---|---|
| I-00-A | I-00 | [冻结基线与隔离范围](card_I-00-A.md) | 无（仍需本卡环境/设计前提） | planned |
| I-00-B | I-00 | [绑定当前源码、样本和命令](card_I-00-B.md) | I-00-A | planned |
| I-00-C | I-00 | [修复现有验收器的证明范围](card_I-00-C.md) | I-00-B | planned |
| I-00-D | I-00 | [活动指南与退役边界](card_I-00-D.md) | I-00-B | planned |
| I-07-A | I-07 | [固定样本与前置状态建档](card_I-07-A.md) | I-00-B | planned |
| I-07-B | I-07 | [三市场来源链与二次复用](card_I-07-B.md) | I-07-A, I-01, I-02, I-03, I-04, I-05, I-06 | planned |
| I-07-C | I-07 | [跨根与未知公司泛化](card_I-07-C.md) | I-07-B | planned |
| I-07-D | I-07 | [故障矩阵与断点恢复](card_I-07-D.md) | I-07-B, I-09 | planned |
| I-07-E | I-07 | [从合格输入到正式预测产物](card_I-07-E.md) | I-07-B, I-08, I-09, I-10, I-11 | planned |
| I-14-A | I-14 | [性能测量先验证失败分支](card_I-14-A.md) | I-00-C | planned |
| I-14-B | I-14 | [自然时间与UI观察证据](card_I-14-B.md) | I-14-A | planned |
| I-14-C | I-14 | [在真实异常出口验证脱敏](card_I-14-C.md) | I-00-B | planned |
| I-16-A | I-16 | [绑定拟部署完整组合](card_I-16-A.md) | I-07-E, I-07-D, I-08, I-09, I-13, I-14, I-15 | planned |
| I-16-B | I-16 | [部署后的同入口复验](card_I-16-B.md) | I-16-A | planned |
| I-17-A | I-17 | [按原义务积累自然观察](card_I-17-A.md) | I-16-B, I-14-B | planned |
| I-17-B | I-17 | [从原用户目标逐项终审](card_I-17-B.md) | I-17-A, I-07-C, I-12, I-13, I-00-C | planned |
| I-14-D | I-14 | [脱敏裸值贪婪语义收窄到单 token（C13 立卡）](card_I-14-D.md) | I-00-B | planned |
| I-14-E | I-14 | [重启节点的时序抖动（负载相关，非树差异）](card_I-14-E.md) | I-00-B | planned |
| I-14-F | I-14 | [深层 cwd 下的 WinError 206（产品侧短 basetemp 约定）](card_I-14-F.md) | I-00-B | planned |
| I-14-H | I-14 | [natural_window.py 的两个产品级缺陷](card_I-14-H.md) | I-00-B | planned |
| I-14-I | I-14 | [容器 basis 的逐例拒绝（I-14-H 强制收尾残卡 / RIDER）](card_I-14-I.md) | I-00-B, I-14-H | planned |
| I-01-A | I-01 | [doctor 与实际扫描共用配置能力判断](card_I-01-A.md) | I-00-A, I-00-B, I-00-D | planned |
| I-02-A | I-02 | [扫描返回必须说明完成状态与目标注册结果](card_I-02-A.md) | I-01-A | planned |
| I-02-B | I-02 | [跨 CLI 保留阶段错误及已发生副作用](card_I-02-B.md) | I-02-A, I-00-B | planned |
| I-02-C | I-02 | [注册已落盘的小米/微软原件且不再下载](card_I-02-C.md) | I-02-A, I-02-B | planned |
| I-02-D | I-02 | [注册重入与同 bytes 去重不伪报成功](card_I-02-D.md) | I-02-C | planned |
| I-02-E | I-02 | [在每个持久化边界中断后只恢复缺失阶段](card_I-02-E.md) | I-02-D | planned |
| I-05-A | I-05 | [默认产物与验证器共用契约，sections 不能绕过资格](card_I-05-A.md) | I-02-E | planned |
| I-06-A | I-06 | [安全阻断前登记可持久恢复的需求](card_I-06-A.md) | I-02-E | planned |
| I-06-B | I-06 | [执行真实审核并从原请求恢复](card_I-06-B.md) | I-06-A, I-05-A | planned |
| I-05-B | I-05 | [把工件选择与实际读取分开，消费者读取已验证字节](card_I-05-B.md) | I-05-A, I-06-B | planned |
| I-05-C | I-05 | [按需求执行最小补产并如实计调用次数](card_I-05-C.md) | I-05-B, I-06-B | planned |
| I-15-A | I-15 | [prune 只删除已验证归档集合并证明可恢复](card_I-15-A.md) | I-00-A, I-00-B, I-00-C | planned |
| I-03-A | I-03 | [冻结期间、修订、最新性与授权绑定契约](card_I-03-A.md) | I-00-A, I-00-B | planned |
| I-03-B | I-03 | [按冻结期间和修订规则修复纯 GapPlan 选择](card_I-03-B.md) | I-03-A, I-00-C | planned |
| I-03-C | I-03 | [把下载对象、资格与策略完整绑定到计划及授权](card_I-03-C.md) | I-03-A, I-00-C | planned |
| I-03-D | I-03 | [验证 close-gap 重检、完整候选范围及实际额度](card_I-03-D.md) | I-03-B, I-03-C, I-02 | planned |
| I-04-A | I-04 | [先定请求 deadline、清理预算和计时 oracle](card_I-04-A.md) | I-00-A, I-00-B | planned |
| I-04-B | I-04 | [修复退避旧预算和 worker 最小10秒越界](card_I-04-B.md) | I-04-A, I-00-C | planned |
| I-04-C | I-04 | [先冻结跨进程 lease、所有权与恢复协议](card_I-04-C.md) | I-00-A, I-00-B, I-04-A | planned |
| I-04-D | I-04 | [实施原子lease更新并验证进程交错](card_I-04-D.md) | I-04-C, I-04-B | planned |
| I-04-E | I-04 | [保留嵌套错误与失败前真实副作用计数](card_I-04-E.md) | I-04-B, I-04-D, I-02, I-03-D | planned |
| I-08-A | I-08 | [先定签名信任域、提供者协议及旧版本边界](card_I-08-A.md) | I-00-A, I-00-B | planned |
| I-08-B | I-08 | [实际调用受信提供者并验证签名后才声明host_signed](card_I-08-B.md) | I-08-A, I-00-C | planned |
| I-08-C | I-08 | [验证消费者拒绝伪造、跨载荷重放和未签结果](card_I-08-C.md) | I-08-B | planned |
| I-09-A | I-09 | [先定结果包提交、读可见性与幂等协议](card_I-09-A.md) | I-00-A, I-00-B, I-08-A | planned |
| I-09-B | I-09 | [实现完整包提交并让读者验证commit资格](card_I-09-B.md) | I-09-A, I-08-B, I-00-C | planned |
| I-09-C | I-09 | [逐边界故障注入、并发与重启恢复独立验收](card_I-09-C.md) | I-09-B, I-08-C | planned |
| M01 | I-10 | [直接增长率](card_M01.md) | I-00-B, I-00-C | planned |
| M02 | I-10 | [直接收入路径](card_M02.md) | I-00-B, I-00-C | planned |
| M03 | I-10 | [销量乘单价](card_M03.md) | I-00-B, I-00-C | planned |
| M04 | I-10 | [产能利用与良率](card_M04.md) | I-00-B, I-00-C | planned |
| M05 | I-10 | [平均客户订阅](card_M05.md) | I-00-B, I-00-C | planned |
| M06 | I-10 | [用量平台变现](card_M06.md) | I-00-B, I-00-C | planned |
| M07 | I-10 | [服务容量与利用](card_M07.md) | I-00-B, I-00-C | planned |
| M08 | I-10 | [金额订单存量桥](card_M08.md) | I-00-B, I-00-C | planned |
| M09 | I-10 | [资源销售量与实售价](card_M09.md) | I-00-B, I-00-C | planned |
| M10 | I-10 | [储量消耗桥](card_M10.md) | I-00-B, I-00-C | planned |
| M11 | I-10 | [计费量与费率](card_M11.md) | I-00-B, I-00-C | planned |
| M12 | I-10 | [银行净利息与手续费](card_M12.md) | I-00-B, I-00-C | planned |
| M13 | I-10 | [平均资管规模收费](card_M13.md) | I-00-B, I-00-C | planned |
| M14 | I-10 | [直营加盟与供应收入](card_M14.md) | I-00-B, I-00-C | planned |
| M15 | I-10 | [运力利用与收益率](card_M15.md) | I-00-B, I-00-C | planned |
| M16 | I-10 | [已出租面积租金](card_M16.md) | I-00-B, I-00-C | planned |
| M17 | I-10 | [商业销售与许可收入](card_M17.md) | I-00-B, I-00-C | planned |
| M18 | I-10 | [曝光填充与CPM](card_M18.md) | I-00-B, I-00-C | planned |
| M19 | I-10 | [活跃用户付费变现](card_M19.md) | I-00-B, I-00-C | planned |
| M20 | I-10 | [客户流量与时间暴露](card_M20.md) | I-00-B, I-00-C | planned |
| M21 | I-10 | [实物订单交付桥](card_M21.md) | I-00-B, I-00-C | planned |
| M22 | I-10 | [里程碑与销售分成](card_M22.md) | I-00-B, I-00-C | planned |
| M23 | I-10 | [保险服务披露映射](card_M23.md) | I-00-B, I-00-C | planned |
| M24 | I-10 | [ARR存量与收入时点](card_M24.md) | I-00-B, I-00-C | planned |
| M25 | I-10 | [装机存量售后](card_M25.md) | I-00-B, I-00-C | planned |
| M26 | I-10 | [开闭店与新店成熟度](card_M26.md) | I-00-B, I-00-C | planned |
| M27 | I-10 | [发电量与电价](card_M27.md) | I-00-B, I-00-C | planned |
| M28 | I-10 | [AUM流量与收费桥](card_M28.md) | I-00-B, I-00-C | planned |
| M29 | I-10 | [有供给约束的商业化](card_M29.md) | I-00-B, I-00-C | planned |
| M30 | I-10 | [有限市场采用](card_M30.md) | I-00-B, I-00-C | planned |
| M31 | I-10 | [库存与销售桥](card_M31.md) | I-00-B, I-00-C | planned |
| I-10-B | I-10 | [model_registry 的静默补 0 与按名字定符号](card_I-10-B.md) | I-00-B | planned |
| I-10-A | I-10 | [先行完成实际采用模型的专业披露适配](card_I-10-A.md) | I-07-B, M01, M02, M03, M04, M05, M06, M07, M08, M09, M10, M11, M12, M13, M14, M15, M16, M17, M18, M19, M20, M21, M22, M23, M24, M25, M26, M27, M28, M29, M30, M31 | planned |
| I-11-A | I-11 | [冻结定性到参数的可证伪命题](card_I-11-A.md) | I-00-B, I-00-C | planned |
| I-11-B | I-11 | [校准参数幅度和联合情景](card_I-11-B.md) | I-11-A, I-10-A | planned |
| I-11-C | I-11 | [独立反方审查与触发更新](card_I-11-C.md) | I-11-B | planned |
| I-12-A | I-12 | [专业冻结评估设计](card_I-12-A.md) | I-07-E | planned |
| I-12-B | I-12 | [建立无未来信息的样本与实际值](card_I-12-B.md) | I-12-A | planned |
| I-12-C | I-12 | [冻结预测与基线后解封实际值](card_I-12-C.md) | I-12-B | planned |
| I-12-D | I-12 | [按冻结公式计算指标与不确定性](card_I-12-D.md) | I-12-C | planned |
| I-12-E | I-12 | [分范围判定准确性并保留失败](card_I-12-E.md) | I-12-D | planned |
| I-13-A | I-13 | [买方交付逐项评分](card_I-13-A.md) | I-07-E, I-11-C | planned |
| I-13-B | I-13 | [情景与投资者问题走查](card_I-13-B.md) | I-13-A | planned |
| I-13-C | I-13 | [冻结交付资格与接续清单](card_I-13-C.md) | I-13-B | planned |

## 委派顺序

1. I-00-A只读基线；I-00-B绑定具体卡的环境与命令；I-00-C确保完成门不再失真，I-00-D修活动文档。
2. 来源配置/注册→GapPlan/预算与工件审核→真实来源旅程。发布和模型公式可在独立副本并行，但共享schema/registry/config写入只有一个owner。
3. 正式预测与买方质量；准确性按独立评估设计执行，不用公式通过代替。
4. 部署与真实观察，最后按原义务终审；当前任何卡都没有已实施或已部署资格。

总计92张执行卡；31模型逐项卡属于I-10，单独授予公式/披露/准确性资格。
owner 于 2026-09-20 总授权新立的 5 张卡（I-14-D / I-14-E / I-14-F / I-14-H / I-10-B）
来自 OWNER_DECISIONS.md §13 T1-7 / T1-10 / T1-22；它们只登记**产品缺陷进入受控修卡流程**，
不构成任何实施资格，也不改任何既有冻结件。
第 92 张卡 **I-14-I**（容器 basis 的逐例拒绝）**不是**新增授权项：它是 I-14-H 独立
reviewer 强制收尾条件的兑现路径（`review.md` §5 + 末节），依赖 I-14-H。
I-14-H 因此只获得 conditional / accepted_scoped（验收证据 = 12/14 冻结用例 + 12 例
pytest 套件；全 14-case `run_cases.py` 门从未通过）。I-14-I 只登记该强制收尾，
同样不构成任何实施资格，也不改任何既有冻结件。
