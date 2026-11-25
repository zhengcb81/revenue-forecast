# RF F4 S3 / S4 边界整改

当前切片状态 MERGED。工作从 RF 已发布主线 1b471df4383b41fe319fb292b55b0baa3ee6af4e 起步。主仓既有变动留给原任务。总控计划位于 company-wiki 的 module-boundaries-2026-11-11 审计。

## 当前交付

- [x] 让运行器以参数接收已保存的 attempt_no，由同一编号关联运行记录、反馈与标准输出。重启重新构造运行器后，原来源阶段不再执行。
- [x] release-readiness 的可选目录状态经 CWP 公开的 source-catalog status 获取。把 --catalog SQLite 路径改为 --catalog-config CWP 配置。由运行 RF 的 Python 环境提供已安装的 company-wiki 命令模块。不带选项时不调用 CWP。
- [x] 移除曾退出分发的 WU-1304 canary 的可执行私有目录探针。保留原路径的退休提示。原版本、报告和推导留在 Git。
- [x] 先复现上述三处，再做成功、失败、恢复和真实公开接口组合测试。
- [x] 独立审查及返修通过。保留 CWP 发布的机器错误代码和安全失败类型，不转写 stderr 正文。
- [x] 正常 hooks、非强制快进及远端哈希复核通过。产品提交 9042f6e06cdf21144ad5a7d736eb99067cfe8845 的 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45573177121) 成功。

## 目录数据投影后续切片（已独审）

- [x] 正常报告溯源投影从同一个纯契约层获取 CatalogError、SourceRef 键和公开输出路径校验。已有目录 facade 继续公开相同 CatalogError，读取投影的冷启动不需要加载目录存储。
- [x] 真实新进程验证正常投影通过，物理 locator 仍按原错误拒绝。本次没有增加新的发布门禁。
- [x] 既有八个回归套件验证读取、来源、失败登记和发布行为。单个跨仓身份旧夹具在未改的发布基线同样失败，单独保留待办。
- [x] 正常快进并复核远端源码 c3396e96ba9e22a6fd6601b783c504aecdb8f622，[CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45574901776) 成功。

## 仍有工作

- 日审计已改用 CWP 公开状态与按需原版验真，保留 RF 本仓收据和历史回读。已完成源、实际公开端口验证及独立审查。Windows 任务实际注册查询由系统拒绝，部署状态独立跟踪。周跑已按下项移植。月度队列和其余历史 baseline 分开处置。
- 周跑已对接 FF 发布的四项组合收据，RF 独立审查、定向 83 项和精确主线 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45596205549) 已通过，源码 43961a73 已发布。实际 Windows 任务部署和真实实跑继续由所属模块协调，见 [周跑公开接口交接](weekly-owner-boundary.md)。
- 月度 broker 旧执行入口退役已发布 4b9a4783，定向回归、真实旧归档回读、独审和精确 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45598302331) 通过。原 20261001T182300Z 仍为历史 7/7。原查询、历史验证和手工移除命令保留。系统拒绝实际 Windows 注册查询，本次无系统任务变更。未来若有现行月度需求，从公开来源和证据目标定义新口径，使用对应 owner 供数。
- EX05 旧执行与 baseline 跨仓 SQLite 查询已移除，84 项定向与独审 5 项通过，源码 deb59f70 已发布，精确 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45599725734) 成功。保留 FC-505 原始收据和 baseline 的本地 Git、配置摘要、运行环境观测。旧参数可解析，未请求等于未观察，显式旧库观测记录为 unavailable。独立历史 scenario runner 和 SLO 保留原样。
- 合并其他 runtime/report catalog 耦合项仍需按总控审计逐项收口。本轮三个修复不能作为 RF S3 完整结案。

## 收口标准

独审以最终代码和针对性行为回归为准。真实验证限隔离配置和原生公开入口。对基线已经失败的历史门禁保留复现证据并另行处理，不改阈值换绿。代码发布的实况在本计划 progress.md 记录。

## S5 复审接续

从远端主线 `b9e59db4` 的独立稀疏工作树复核 RF 项。先验证既有 CI 实际选择与运输器诊断，再修 SLO 公开边界和多根恢复错误语义。依次补定向回归、核对本地快测与正式 CI 的职责、交给总控独审。原主工区存在其他任务的改动；由总控按正式版本另行对齐宿主。

- [x] 复现并修复 RF 本轮 CI 漏项和 FF 子进程诊断。
- [x] 复现并修复 SLO 私有目录预检、单有效根失证原因和 CWP status 原因投影。
- [x] 核对原工作树、F4 两套运行路径和四份安装清单。隔离验证新旧回告读取。
- [ ] 由总控独审及发布。现场语义只改运行版本指向，合格后验证既有作业冷读与安装重复零写。

## S5-08 报告来源冷读切片

基线为通过正式 CI 的 RF `1577be3c5f76c58949610c9325918caea03f1b9e`。ROOT 已核对范围，作者在独立短路径工作树调整报告目录读取与写入的边界。

- [x] 用已封存来源和真实新 Python 进程复现冷读加载报告写入与准入模块。冻结原内容、路径绑定、来源 SHA 以及异常类。
- [x] 把读写双方共用的保留响应校验放入独立值模块。读面消费狭窄的 `read` / `document` 端口。原来源准入路径继续调用相同校验，历史写入、报告和原文件引用仍由原 owner 维护。
- [ ] ROOT 核对候选的入册、历史报告、冷读、权限与字节完整性回归并发布。新增冷读用例加入现有 CI 调用，本地固定快测不变。
- [ ] 后续独立切片：将 publication 与 publication_sources 共用的原生录制阶段校验提炼为只读证明端口。重点复现捕获时序、原 argv、实际消耗 argv 及原冻结文件一致性。
- [ ] 后续独立切片：将 `ReportCatalog` 的 `rf_job_record` 读取校验与 job importer 的注册职责分开。优先冻结原作业归属、完成态、历史版本和明确恢复语义，再设计窄的目录写入端口。

更早 `research_attempt` 与 `research_identity` 之间的共享 observation/来源身份工具形成另一组已有回边，另行处理。以上余项不扩大本切片的写入范围。
