# 执行记录

2026-10-31：main09be0974隔离到ROOT短路径稀疏工区；主工区3个定时assurance WIP未改。首RED7个业务断言失败+1缺稀疏夹具错误；补精确夹具，138P。再经独审单段正式发布2F、null/参数反链2F、投影自洽改写4F分别复现并修。早期投影前缀误写产生4假绿和shell转义错误已保留，不计RED；compact subject实现中间5F亦保留，最终29P/2.86s。

集中阶段171P/39.96s（含28安装测试）；增加4投影例后的中间175例为170P/5F，后仅复验受影响29例全绿。类型检查14文件绿，Ruff绿。实际v5同一付费artifact 0POST/0下载，必要CWP定位回放实执行；1%参数扰动6断言通过，独审32断言/源码SHA冻结，0剩余阻断。发布和技能安装收据随后补，不提前宣称远端CI绿。

发布前CI材料核对：新日常发布测试间接依赖docs归档夹具，但CI只检出tests等目录。ROOT稀疏去掉docs正确复现1F，6份夹具按原字节共12018B置于tests/fixtures/shared_reading_wire，唯一helper改归属路径；旧归档保留、无新下载/扩大CI。无docs工区81P/4.21s。0559d75c首轮主线正常pre-push679P/96.57s，3份assurance WIP哈希不变；最终CI和部署以总控收据为准。

2026-11-01：同一新版华利artifact v6经实际native链及45独立断言通过，0新POST/下载；正式产物和收据见review/v6，replay.py --case v6可隔离离线重跑。生产代码无delta；v5原签名保留，公司研究/P3仍OPEN。
