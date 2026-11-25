# RF S3 / S4 进度

2026-11-25，从 RF 已发布主线 1b471df4383b41fe319fb292b55b0baa3ee6af4e 创建隔离工作树。原主仓 d62fca9a 的运行日志与 PWF 变动保留。

TDD 红线为 stage runner 缺 attempt_no 参数、release-readiness 走旧的 SQLite 参数且无法处理 owner 状态、退休 canary 对假 CWP 数据库仍触发 SQLite 错误。修正后合并回归的首轮为 85 项通过及 2 项历史 E4 失败。把纯复杂度工具在发布基线和本候选各运行一次，均独立复现 confidence 的 27 > 23 与 narrative contracts 的 53 > 10。两项 E4 都源于旧复杂度检查，不属于本轮产品回归。

已完成 readiness 对真实 CWP 本地临时目录的组合复验。暗含的只读 SQLite 旁文件由 CWP 协议管理，原目录文件不被改写。见 findings.md。真实复验不需要生产配置或 API。

整批聚焦复验使用宿主短路径临时目录，98 项通过，4 项历史 E4 不在本次聚焦范围。旧 E4 的复杂度失败已按同基线复现。沙箱默认深路径导致安装器和场景夹具两个正常旧用例写不进去，改在短路径测试环境复跑后通过，临时目录已清理。

独立 FF reviewer 首轮发现 readiness 在新调度层只保留退出码，无法区别目录与运行环境故障。增加保真回归，3 红 1 绿。返修投影 owner 公共错误类型、retryable 和有明确现存含义的目录不可用信息，保留早期配置异常的类型。假 bearer、路径和未知字段不会外泄，针对性复验 15 项通过，独审复验通过。

已从精确远端父提交正常快进 RF main 到 9042f6e06cdf21144ad5a7d736eb99067cfe8845，提交 hook 的 Ruff、公共 mypy 和宿主路径测试通过，push hook 的 Ruff 与 12 项固定 smoke 通过。独立读取 origin/main 返回同一 SHA。精确源码 [CI](https://github.com/zhengcb81/revenue-forecast/actions/runs/45573177121) 成功。RF 旧主工作区仍保留原 HEAD 和在用变动。

仍开放的日审计、月审计、历史 baseline 和 report catalog 重构见 task_plan.md。日审计真实记录 20261124T210001Z 对应 report 存在，保留原始 stale、exit 1、not-ok 结果。已确认其中仍观察 policy、scan、producer、legacy 和跨根指标。

第二个切片的真实冷启动在旧基线确实加载了目录 facade，隔离测试先红。值级合同抽离后新进程回归绿，路径泄漏仍拒绝且错误对象保持原公开类。八个定向套件 317 passed、2 skipped、1 已有失败。该单例在不含候选改动的 1b471df4 同样返回 identity_not_resolved。用 c211f25c 对比该基线，相关 catalog 源码及身份用例字节没有变更。独立 FF reviewer 又跑冷启动与真实 owner CLI 两项，均通过。短路径隔离测试目录清理完成。

上一个 readiness 发布的失败链路做了真实 F4 补验。建立临时 CWP 配置和空库。正常 status 返回可用，缺配置显示 FileNotFoundError，缺数据库显示 catalog_missing。两次失败通过原 run ID 查回 CWP JSONL，配置和数据库字节与修改时间未变，临时的状态和反馈一并清理，外部调用为零。第二个切片等待快进核验。
