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

- 日审计已改用 CWP 公开状态与按需原版验真，保留 RF 本仓收据和历史回读。已完成源、实际公开端口验证及独立审查。Windows 任务实际注册查询由系统拒绝，部署状态独立跟踪。周跑 FF 测试入口、月度队列及其余历史 baseline 各自确认当前用途。
- 周跑已对接 FF 发布的四项组合收据，RF 独立审查已通过，正在发布。实际 Windows 任务部署和真实实跑继续由所属模块协调，见 [周跑公开接口交接](weekly-owner-boundary.md)。
- 月度 broker 队列在本机没有注册证据，也没有当前主目录 ledger。确认其他启动者及历史验收用途。若仍需该能力，请 owner 给出准确的文档类型、标题或关联实体匹配和完整分页，再迁移。不能以不全的列表判断全队列 OK。
- 历史 baseline 不直接迁移 SQLite schema、扫描记录和根信息。先核实归档复查用途并确定由 owner 提供的公开收据字段。单独修复可验证的近代入口。
- 合并其他 runtime/report catalog 耦合项仍需按总控审计逐项收口。本轮三个修复不能作为 RF S3 完整结案。

## 收口标准

独审以最终代码和针对性行为回归为准。真实验证限隔离配置和原生公开入口。对基线已经失败的历史门禁保留复现证据并另行处理，不改阈值换绿。代码发布的实况在本计划 progress.md 记录。
