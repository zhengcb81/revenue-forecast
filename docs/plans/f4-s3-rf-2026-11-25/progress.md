# RF S3 / S4 进度

2026-11-25，从 RF 已发布主线 1b471df4383b41fe319fb292b55b0baa3ee6af4e 创建隔离工作树。原主仓 d62fca9a 的运行日志与 PWF 变动保留。

TDD 红线为 stage runner 缺 attempt_no 参数、release-readiness 走旧的 SQLite 参数且无法处理 owner 状态、退休 canary 对假 CWP 数据库仍触发 SQLite 错误。修正后合并回归的首轮为 85 项通过及 2 项历史 E4 失败。把纯复杂度工具在发布基线和本候选各运行一次，均独立复现 confidence 的 27 > 23 与 narrative contracts 的 53 > 10。两项 E4 都源于旧复杂度检查，不属于本轮产品回归。

已完成 readiness 对真实 CWP 本地临时目录的组合复验。暗含的只读 SQLite 旁文件由 CWP 协议管理，原目录文件不被改写。见 findings.md。真实复验不需要生产配置或 API。

整批聚焦复验使用宿主短路径临时目录，98 项通过，4 项历史 E4 不在本次聚焦范围。旧 E4 的复杂度失败已按同基线复现。沙箱默认深路径导致安装器和场景夹具两个正常旧用例写不进去，改在短路径测试环境复跑后通过，临时目录已清理。

独立 FF reviewer 首轮发现 readiness 在新调度层只保留退出码，无法区别目录与运行环境故障。增加保真回归，3 红 1 绿。返修投影 owner 公共错误类型、retryable 和有明确现存含义的目录不可用信息，保留早期配置异常的类型。假 bearer、路径和未知字段不会外泄，针对性复验 15 项通过，独审复验通过。

已从精确远端父提交正常快进 RF main 到 9042f6e06cdf21144ad5a7d736eb99067cfe8845，提交 hook 的 Ruff、公共 mypy 和宿主路径测试通过，push hook 的 Ruff 与 12 项固定 smoke 通过。独立读取 origin/main 返回同一 SHA。精确源码 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45573177121) 成功。RF 旧主工作区仍保留原 HEAD 和在用变动。

仍开放的日审计、月审计、历史 baseline 和 report catalog 重构见 task_plan.md。日审计真实记录 20261124T210001Z 对应 report 存在，保留原始 stale、exit 1、not-ok 结果。已确认其中仍观察 policy、scan、producer、legacy 和跨根指标。

第二个切片的真实冷启动在旧基线确实加载了目录 facade，隔离测试先红。值级合同抽离后新进程回归绿，路径泄漏仍拒绝且错误对象保持原公开类。八个定向套件 317 passed、2 skipped、1 已有失败。该单例在不含候选改动的 1b471df4 同样返回 identity_not_resolved。用 c211f25c 对比该基线，相关 catalog 源码及身份用例字节没有变更。独立 FF reviewer 又跑冷启动与真实 owner CLI 两项，均通过。短路径隔离测试目录清理完成。

上一个 readiness 发布的失败链路做了真实 F4 补验。建立临时 CWP 配置和空库。正常 status 返回可用，缺配置显示 FileNotFoundError，缺数据库显示 catalog_missing。两次失败通过原 run ID 查回 CWP JSONL，配置和数据库字节与修改时间未变，临时的状态和反馈一并清理，外部调用为零。第二个切片从 c211f25c 正常快进至 c3396e96ba9e22a6fd6601b783c504aecdb8f622。提交 hooks 的 Ruff、公共 mypy 和宿主路径测试通过。推送 hooks 的 Ruff 和 12 项固定测试通过。Git 远端哈希复核等于该源码，[CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45574901776) 成功。

## 2026-11-25 日审计真实入口复验

候选从正式 `ad2379d55e9a9e4f1e832a3781f7b57656dc3663` 的短隔离工区开始。先加现行资料、指定来源不可用和调度仅执行本仓入口三个测试，旧入口全红。日审计和 release readiness 现在共享同一 RF 状态探针，后者保留既有错误文本和安全归因。已移除直接读外部 SQLite、遍历资料根、旧工件与事件条数门槛、等待 FC-705 的 24 小时窗口和调用跨仓观察器。原台账读取及周/月通用 freshness 函数继续服务原有调用者。

Ruff 和 113 项定向测试通过。覆盖每天入口、历史收据回读、原 readiness 错误投影以及周/月共用登记函数。合成临时目录下实际调用 RF 调度 CLI 和 CWP 公开 CLI（本机 CWP `7edbcac8caa6d836ea708d3a058117f8d7ba2bd8`），通过状态、准确来源的原版验真、错误版本引用和实际缺库三组。两种失败分别保存 owner 的 `expected_version_mismatch` 和 `catalog_missing`。核对原文和 catalog SHA 没有变化，缺库未创建，测试目录已清理。没有真实下载、模型请求或费用。

仓内 Windows 注册动作仍生成裸 `run-daily` 可以继续解析。手动隔离验证请给 RF 自己的 `--ledger`、`--alerts`、`--report-root`，并给 `run-daily --config` 指定 CWP 配置。可重复传 `--source-ref` 指定要验真的公开引用 JSON。实际本机任务的查询由系统拒绝访问，注册状态与当前部署代码由宿主另核。独审要求补齐等数目但错身份、SHA、字节数或 MIME 的返回反例，并验证不同排序的正确回复。RF 只对齐公开身份字段，实际原件仍由 CWP 验真。源和测试复验指纹为 `eb4f222609f502c8bb7a4c55acdd467c8bed0cc35aed7e09c150f0f4659dcca5`。

独立非作者审查 ACCEPT，实际短路径复验 38 项通过，并以现有已安装 CWP 用裸 run-daily 分别验证缺库 blocked 和空库 ok。CWP 使用 SQLite 只读连接时可由 SQLite 自行生成 WAL/SHM 辅助文件，目录主文件的 SHA 一致。测试隔离根恢复清理。源码发布以包含本记录的 RF 主线提交为准。

周跑接口盘点完成。FF 单作业和当前离线矩阵可为迁移提供证据。实际三市场采集加坏件反例的组合回告仍缺可消费的公开 owner 收据，进入明确 BLOCKED。Windows 实际注册查询返回拒绝访问。当前没有改动每日或每周生产任务。见 [周跑公开接口交接](weekly-owner-boundary.md)。

## 2026-11-25 周检收据对接

RF 以 `c34bf37126717e9d1108e8dd2b8b915d20a68f14` 为基线，先在实际入口复现九条 RED。移除周调度和手工入口的跨仓测试启动，统一读取 FF 公开收据。本仓保留原报告与台账的读法，并用 owner 实际完成时间评估七天期限。离线、实际失败、阻断、缺失、过期、错号分别记录，运行和失败原因完整保留。

依赖 FF `c11094338bb50a62c1b58c43a1aedaa5f2f9aab4` 已发布。隔离真实组合用 FF 原生命令精确读回离线四项通过、最近混合失败和阻断、精确缺失及不存在收据目录。四种均符合预期，FF 收据文件哈希不变。真实生产下载、本机定时任务和安装副本没有执行。定向 82 项通过，涵盖周检两入口、历史台账、写失败、原完成时间边界、日月调度与发布门。全部受影响 Python 路径 Ruff 和 Git diff 检查通过。

广一点的历史审计试验发现 `test_aud2_05_missing_sample_blocks` 缺 `test_zr806_real_t2_samples` 模块。该历史测试从官方基线直接提取运行同样失败，原文件在基线 Git 树中已经不存在。保持该历史用例和缺口记录。本次只用公开收据反例替换同文件已失效的旧周检输出判定。最终候选独立复审 28 项通过，另复跑实际 FF 离线组合。

独审还复现两条缺口。FF 在 Git 元数据不可用时发布的完整 live 收据，旧候选因 `owner_revision=unknown` 误拒。版本现为溯源诊断，真实执行和四项结果仍用于判断。同名手工 RF 报告过去会覆盖归档，现由独占目录创建生成新的观察编号，原文件字节不变。这两条先红再复验，最终定向组合 83 项通过。

周检源码 `43961a735f533e46562d7e799657a7bb34b94c16` 已正常快进 RF main。标准提交检查与推送 Ruff、12 项固定试验通过，远端 Git 引用匹配，精确 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45596205549) 的 verify 成功。隔离测试证明收据可回查和结果不被错误转绿。真实下载矩阵与 Windows 调度部署单独记录，未在本轮执行。

## 2026-11-25 旧月检退役

从周检文档发布 ba134f9221a6616ee09697ed62a5092d6e9d90b4 起步。两个真实旧 CLI 对带旧两类派生行的仿真库返回 0 并推进历史账本，两次进程审计直接观测到 SQLite 私有读。注册命令模拟拦截发现旧实现会立即尝试改 Windows 任务。五个回归先红，七个兼容对照保绿。新入口统一返回 monthly_broker_audit_retired 和退出码 2，旧参数继续可解析。保留既有 task query 和 unregister，以及只读 verify 的 35 天账本语义。

从原 RF 工作区只读复制真实归档 ledger 和详细报告到隔离根，用原生 CLI 验证 verify 返回 stale 和退出码 1，裸 run-monthly 和同一编号手工入口返回退役。20261001T182300Z 原报告覆盖 7/7。两份原件和隔离副本的字节均未变，无新增文件，隔离副本已清理。原 ledger SHA-256 c8ee858f0f9f6e131c75c0cae064541be791356c8bf02989305eafd78673d887，原 report SHA-256 b704d1b3a20648f3f3c31686dd0942f3800912f9c7b27e409e48920ff7e6b09f。未改实际 Windows 任务、全局技能、副本或 CWP 数据。

月检和日/周调度等七个定向测试文件合计 79 项通过，Ruff 与 diff 检查通过。额外历史 CA204 文件收集时报缺 test_zr709_zijin_journey，精确基线已无该模块，CA204 文件本轮未改。ROOT 独立复验 12 项通过，确认仅按原方式读取历史和移除既有 task，现行代码未发现其他消费者。冻结指纹 34a1842413e0eb4a1b0037517e12884abe91e18d73e3e35800d3380416b3ea4c。正常 hooks 通过，精确 RF main 4b9a4783f0aa835245ae363e6279a4a4414b9fba 的 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45598302331) 成功。

## 2026-11-25 EX05 和 baseline 的旧边界

基于已发布的 3ac1f6cda76328fd240f41b862622ad2162798f6。旧 EX05 在假 CWP 和 FF 导入下，真实 Python 冷启动确实开始遍历假 Dropbox。旧 baseline 对合成历史库触发 sqlite3.connect，并把旧表输出为当前数据；不带 --read-only 则拒绝本地 Git 与配置摘要。四条反例先红，原只读本地目录对照保绿。新版 84 项定向绿，Ruff 和 diff 检查通过。

从本仓导出仍跟踪的 FC-505 原始收据，隔离验证两条真实手工命令。旧 EX05 不扫描数据，退出码 2 并指向已保存收据。baseline 正常返回隔离 Git 的暂存状态与配置字节 SHA，旧 catalog 标为 unavailable，且 Git 索引原字节和时间不变。不存在的 catalog 未创建，隔离根清理，归档原字节未变。FC-505 SHA-256 bae3b9271b2e8e9d533766ce73a6f2e64349db0c0ab554440568d0ca22729827。ROOT 独立运行 5 项通过，验证后清理隔离根。冻结 LF 指纹 41f9e5675adbd5da8ac1831569876774fd2addbe9016c12a55830506f05345fd。待主线精确验收。
