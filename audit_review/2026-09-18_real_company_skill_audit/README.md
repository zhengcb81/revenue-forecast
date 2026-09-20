# 真实公司技能运行与独立审计

信息截止日：2026-09-18。用户授权：选取 A/HK/US 代表公司实际运行 revenue-forecast，检查 filing-fetch 已下载复用与未下载获取、company-wiki 跨目录数据湖保存和索引；记录发现，本轮不修改代码。

拟选样本：紫金矿业（601899，CN，资源周期）、小米集团（1810，HK，多业务与 EV 爬坡）、微软（MSFT，US，软件订阅/云/成熟业务）。基期以已取得并核实的最近完整财年为准，预测未来三年。若公司身份或完整数据无法取得，保留失败证据，不换名制造通过。

分工：公司运行者与独立审计者分离。原始命令、请求、stdout/stderr、退出码、文件哈希、来源摘录、输入迭代和输出统一保存在本目录。除本目录的审计脚本/数据/文档外，不修改产品代码或生产配置；下载与索引通过现有生产 CLI 完成并串行执行。

验收：研究经济实质、预测者/投资者可用性、正式模型校验、来源真实性、reuse/download 分支、跨根定位、immutable raw、manifest/hash、索引与重复调用行为分别下结论。受环境权限、网络或软件缺陷阻断的步骤明确标记 blocked/unproven，不用测试夹具代替真实链路通过证据。

主报告：[AUDIT_REPORT.md](AUDIT_REPORT.md)。

本轮已记录13次真实CLI运行。既有原件复用及部分跨目录完整性检查通过；HK/US新年报落盘后索引失败，紫金既有年报缺review，最新H1获取遇CNINFO HTTP403。三家公司正式来源准备均未成功，因此没有形成正式预测输入/结果；不把研究草案当作引擎输出。

独立数据检查见[independent/data_pipeline_review.md](independent/data_pipeline_review.md)，独立最终意见见[independent/review.md](independent/review.md)。公司研究分别位于ZIJIN、XIAOMI、MSFT目录。

`audit_integrity_check.json`核验13组原始日志哈希，并对恢复期间基线中357份产品代码/配置文件复核，无变化。它不声称覆盖首次执行前未保存的历史状态。产品原有上一轮改动保持原样；本轮不修代码/配置，授权下载产生的真实raw/sidecar保留。
