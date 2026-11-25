# RF S3 / S4 发现与取舍

## 根因与实际修正

运行器的日志文件身份原来由调用者写入一个私有成员，再在 run 内取回。改为在选定并持久化编号后通过明确参数传递。原作业断在 compute 后，新的实例只继续 compute-2 和 publication-1。断在执行前的 compute-1 保留历史状态，不被新文件覆盖。历史尝试费用未知仍记未知。

可选 release-readiness 自己打开相邻 CWP SQLite，并用表名判断是否可用。改取 CWP 原生只读 status 的公开文档、来源、活动和缺失位置计数。显式缺配置、owner 非零退出、畸形状态不能被当作成功。零条及额外的非必需诊断允许返回。默认无目录请求时报告 not_supplied。

WU-1304 canary 在 MB-RF 已退出分发，运行路径和被调用的函数未发现现行消费者，然而直接执行仍能访问 CWP 数据库并重新解释其绑定字段。原入口改为只报告退休，不再暗中保留跨层运行通道。原实现可在 1b471df4 的对应路径读取。

## 真实运行印证

2026-11-25 对实际 CWP e3b4a1af 的公开命令进行离线组合。先通过 CWP 本地扫描创建隔离空目录。RF 调用 readiness 得到零文档的有效读面。指定不存在的配置时报红。已存在的三个文件前后内容 SHA 和修改时间一致。按 CWP 已有只读 reader 约定，冷 WAL 数据库第一次只读连接可生成零字节 WAL 及 32768 字节 SHM 协议文件。无业务数据被改写。整个临时目录清理，下载、provider 和模型调用为零。

## 拆分依据

本机实际 Windows 注册状态未知。对 revenue_daily_t2 与 revenue_monthly_broker 的原生 schtasks 查询由系统拒绝。RF 原工作区有真实 20261124T210001Z 日运行记录，21:02:21 结束并标为 stale。另有 20261001T182300Z 月运行的账本和原 7/7 报告。检查 RF、CWP、RFAudit、FF、Dashboard、StockWiki 的当前代码没有发现其他跨仓调用点。

公开 status 不提供旧 canary 的逐件绑定、旧日审计的生产事件与 legacy bridge 台账、月度队列的无遗漏组合匹配、旧 baseline 的最近扫描及根的内部字段。generic query 既没有 artifact_id，又没有稳定的完整分页。暂不把互不等价的数据套成原指标。

## 日审计迁移佐证与顺序

最新实跑 20261124T210001Z 留下报告。旧日审计只因旧 schema 1.0 已完成绑定数量为 0 拒绝，历史 producer events 有 473。该指标只回答旧实现有没有产生特定记录，无法证明当前业务摘要是否可读。调度还读取 CWP 数据目录的 legacy_periods.json，通过 CWP 旧脚本路径调用 legacy_observer.py，同时传入 catalog SQLite 和周期文件物理路径。它可能为凑满旧观察期等待，日审计就绪又使用相同历史台账。

下一次实施先用该份已保存报告复现旧拒绝。核实 run-daily 与 verify 的实际启动者、输出消费人及历史观察期是否仍有人使用。当前常态监控改读 CWP 公布的状态、原文/摘要读面和 F4 观测，新增精确采样要落到 owner 接口及证据。旧计数、根文件总数、观察期和旧 manifest 比对在尚须展示时作诊断，移除作为新材料可读性的代理。若旧周期仍有消费者，继续由 CWP owner 维护原轨迹并给 RF 公开的结果，只在旧用途证实无人需要后归档。先验真实失败路径及无重复写、无重复花费，保留历史日志。

## 目录值级合同

真实 Python 冷启动可证明 report_catalog_lineage 以前只做路径安全投影也会导入目录 facade。这是 owner 装配进基础值流程的反向依赖。CatalogError、准确 SourceRef 字段集合和内部路径检查放到无安装或数据依赖的值层。目录保留原公开的 CatalogError 类，report_catalog_research_attempt 对目录本身的引用成为仅类型引用。report_catalog_research_publication 和相应 sources 模块的深层互相调用、report_catalog_rf_job_import 的私有目录调用仍属独立的后续架构切片。

## 日审计的过时输入与职责

历史日审计把旧 v1 完成工件数量作为当前资料存在的代用指标。20261124T210001Z 报告出现 0 个 v1 完成工件和 473 个 producer events，旧检查仍因少于 3 个工件判失败。现行 CWP 提供公开 status，能分别表明配置和目录是否可读，以及当前来源计数。

部署层仍把 CWP 的公开配置文件交给 CWP。RF 日审计只读取公开状态，在明确给定 SourceRef 时用公开 export-v2 复验原始字节。合法空目录可以健康，实际缺库与指定版本不可验证照常进入 RF 失败收据。历史观察窗口属于旧迁移关账，曾让每次日跑先等和调用 CWP 私有观察器写跨仓历史账。删除这一运行依赖后，过去版本的 RF ledger 和归档报告继续按既有格式读取。

## 周跑、月审计和历史入口

11 月 22 日有周跑失败记录 20261122T083603Z。当前 RF 周跑直接启动 FF 仓内真实下载 pytest，强制真实下载开关并重设宿主 profile。下一步由 FF 拥有测试执行和公开收据，RF 消费原结果。要求真实采集时需沿 FF 公开作业配置真实预算和恢复，单纯离线回放不能代替实际下载验收。

月审计最近可见记录仍为 20261001T182300Z。原入口直接读取 CWP SQLite 的 documents、document_entities、entities 和 artifacts，取标题或归属名称含固定关键词的券商报告，比较报告可能仅靠标题被纳入。检查只要求每项都有旧 normalized 与 sections 两个角色，不验实际原件字节、披露日、供应商或来源版本。CWP 现行提取质量合同允许 metadata_only 和 skipped_no_narrative，旧批量派生已按 owner 计划退役。

CWP 公开 source-query 可经配置按来源商、供应商编号和 as-of 筛选，公开文档浏览可稳定分页单一 canonical issuer，export-v2 可以验证精确原件，公开叙述接口按 NarrativeRef 读取已发布证据。旧标题或归属并集和派生覆盖率没有等价的现行公开业务口径。旧执行入口退役后，已有账本继续按原 35 天读取，过期如实报告。历史 baseline、EX05 和 SLO 工具没有发现当前生产调用，分别保留证据待判定用途。

## 周检旧入口与现行 owner 证据

周调度之前启动 FF 的整个现行下载测试，手工入口还设置真实下载开关运行较早的 FC805。两条入口都把 stdout 猜测成结论，无法保证指定的是同一既有运行。RF 现在仅查原作业收据。已证明失败不会因另一个用例阻断而变成普通环境缺失，FF 公共诊断随原 case 或运行完整保留。已发布的旧归档记录保持可读，现行四项覆盖和较早 FC805 的 gap 流程区别见 [周检接口交接](weekly-owner-boundary.md)。

## EX05 与基线工具的剩余旧边界

FC-505 的旧工具 tools/ex05_chain_replay.py 曾由 assurance/fc/FC-505/11_implementer_receipt.json 手工执行，收据记录两项准确复用和两项旧采集不完整，原文未下载。当前仓内未找到启动该脚本的运行器或 CI。另有历史 scenario_runner 的 EX-03、DBX-01 指向已从当前 Git 树移除的独立测试，EX-05 指向 CWP 旧 resolver 测试，须与名为 EX05 的历史执行脚本区分。旧脚本拼装相邻仓和 Dropbox 的物理根、导入 FF 同级脚本、遍历 Dropbox 比较指纹并输出物理路径。建议保留证据和历史版本，将可执行入口安全退役。独立的 scenario map 本轮不动。

WU-0.1 的 tools/audit_baseline.py 仍能有选择地执行跨仓 SQLite 查询。已知调用为自身工具测试和旧证据 audit_review/2026-08-08_adversarial_plan/progress.md 中的手动命令。它读数据库版本、内部 roots 和 scan_runs 并返回物理根。仓库 Git、工具版本、配置 hash 等独立诊断仍有实际用途。下一步只去掉跨仓数据读取，保留这些独立诊断与旧参数的可解析性，明确区分历史 catalog 口径不再可提供。旧报告原样保存。
