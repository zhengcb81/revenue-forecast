# 紫金矿业五年收入预测技能调用与对抗式过程审计

> 日期：2026-08-12  
> 范围：独立调用 `revenue-forecast` 技能完成紫金矿业未来五年收入增速预测，并完整记录技能实际行为。  
> 约束：不给技能追加关于矿山、Dropbox、下载或预处理的引导提示；本审计不创作产品代码/配置改动，也不主动调用 catalog ingest/index/metadata/worker-priority 写接口；允许生成本次研究/审计 Markdown 产物。由于复用主链的所谓只读初始化实际具备隐含写能力，且后台 worker/其他 agent 并发运行，数据库和工作树的字节级不变不能作为先验承诺，只能按目标级证据审计。  
> 状态真相：本文件只记录本次运行阶段；任何旧计划或产品完成声明均不作为本次证据。

## Phase 0（建立隔离记录与读取技能契约）— 状态：completed

- [x] 建立本次 planning-with-files 三文件。
- [x] 完整读取 `planning-with-files/SKILL.md`。
- [x] 完整读取 `revenue-forecast/SKILL.md`。
- [x] revenue 技能明确要求调用 filing-fetch；已完整读取 `filing-fetch/SKILL.md`。
- [x] 完整读取矿业预测所需的 revenue references；另记录技能包缺失 session/trust 文档。
- [x] 冻结三仓 Git 运行前状态及用户既有 dirty allowlist。
- [x] 冻结 catalog 文件元数据与 worker 运行前状态；确认 worker 会并发改变 catalog。
- [x] 冻结紫金矿业相关文件在 companies/dayu/Dropbox 的目标级清单与 catalog/artifact/span 状态。

## Phase 1（不加提示的 revenue-forecast 原生运行）— 状态：completed

- [x] 只以“紫金矿业，预测未来五年收入增速”为任务输入执行技能。
- [x] 按技能自身的澄清、数据发现、证据、模型、验证与保存流程运行；标准 source preparation 失败后按同版 checklist 使用隔离 local_document draft。
- [x] 逐步记录命令、文件、搜索、选择、跳过、失败、下载和写入副作用。
- [x] 将预测输出与运行证据保存为独立研究产物。

## Phase 2（filing-fetch 复用与下载审计）— 状态：completed

- [x] 证明是否调用 filing-fetch，以及调用参数、返回状态和生产调用链。
- [x] 从 envelope 代码、journal mtime/内容与内部 handle 证明第三轮为 existing resolution、零下载；并核验 exact candidate/hash/path。
- [x] 证明没有下载新财报或其他文档，并记录无下载授权、失败点和零下载副作用。
- [x] 区分技能请求、filing-fetch/前置策略拒绝、local fallback 与下载未授权四种情况。

## Phase 3（矿种、矿山、区域、储量与逐年营收覆盖审计）— 状态：completed

- [x] 盘点技能是否主动研究矿种、矿山/项目、国家地区和储量/资源量。
- [x] 检查口径：权益/100%口径、资源量/储量、品位、基准日期、单位与来源。
- [x] 检查五年逐年预测的安全颗粒度；采用可对账四业务分部，证明逐矿拆分缺必要收入桥并明确不伪造。
- [x] 核对低/基准/高情景、价格/产量/汇率/投产节奏与增速计算；未冻结曲线的部分登记为 gap。

## Phase 4（文档预处理、MD、切片、标签与可检索性审计）— 状态：completed

- [x] 建立运行前目标清单：两份财报、七份 Dropbox 券商研报及 sidecar 污染文档的 artifact/span 基线。
- [x] 对财报、Dropbox 券商研报、dayu/companies 来源分别检查原文件和派生 MD 内容质量。
- [x] 检查 MD 是否绑定 source hash/schema、是否切片、是否带公司/矿种/矿山/区域/期间标签。
- [x] 实测矿产分布、历史、储量信息能否通过现有索引/查询稳定找到。
- [x] 若未预处理，只记录是否存在当场处理/worker 提升接口及其安全边界，不实际触发。

## Phase 5（网络补缺、新闻下载/索引/处理/保存审计）— 状态：completed

- [x] 记录技能在本地证据不足时是否主动使用网络搜索。
- [x] 核查网络来源的权威性、信息日期和可追溯链接。
- [x] 核查相关新闻是否下载、是否写入受管目录、是否建立索引、是否预处理及保存。
- [x] 未发生的行为明确标记“未发生”，不得用能力推断冒充运行事实。

## Phase 6（对抗式复核、问题与系统性改进建议）— 状态：completed

- [x] 对技能输出做来源完整性、计算一致性、遗漏、旁路、陈旧数据和伪 E2E 检查。
- [x] 将每个用户问题逐项给出“满足/部分满足/不满足/未触发”及证据。
- [x] 记录额外发现，按根因提出全局化改进建议，不实施修复。
- [x] 完成写入边界核验：本审计未创作产品代码/配置改动，未调用显式 ingest/index/metadata/worker-priority 写接口；目标级证据显示零本轮 filing acquisition、零 artifact 生成。复用命令经过隐含写能力初始化且后台 worker/其他 agent 并发变更环境，因此不作 catalog DB/工作树字节级零变化的虚假保证。

## 退出标准

- 预测必须覆盖连续五个未来财年，并给出各年收入、同比增速和五年 CAGR。
- 每个关键数字必须能回溯到来源或显式假设；不能把未找到的数据默认为零。
- filing reuse/download、预处理/index/news 行为必须以实际 trace 和前后状态为证，不能凭代码能力推断。
- 六类审计问题均有结论、证据、不足、风险和系统性建议。

## Errors Encountered

| 序号 | 阶段 | 错误 | 尝试 | 处置 |
|---|---|---|---:|---|
| E-001 | Phase 0 | 当前沙箱拒绝读取 `C:\Users\郑曾波\.agents\skills\revenue-forecast\SKILL.md` | 1 | 已通过权限系统获得该文件只读访问并完整读取；未扩大写权限 |
| E-002 | Phase 0 | `compliance-contract.md` 指向的 `docs/session-checklist.md` 在已选技能目录中不存在 | 1 | 不重复读取同一路径；下一步枚举技能目录定位是否迁移/遗漏，并把文档漂移列入审计 |
| E-003 | Phase 0 | 首次 `rg --files` 只列出 SKILL.md，参考文档被忽略规则隐藏 | 1 | 改用只读 `Get-ChildItem -Recurse -Force` 枚举；确认 references 存在，但 docs/template 确实缺失 |
| E-004 | Phase 0 | 三仓当前 `fcap` 分支均未配置 upstream，`git rev-parse @{u}` 失败 | 1 | 不把 upstream 一致性当本次基线；只冻结本地 40 位 HEAD、branch 和 dirty allowlist |
| E-005 | Phase 0 | restricted sandbox 无法读取用户级全局 git ignore，并对 company-wiki `.pytest_cache` 报访问警告 | 1 | 不申请无关权限；使用显式 `git status --short` 输出作为已知不完整但足够的 tracked/untracked 基线 |
| E-006 | Phase 0 | 标称只读的 `company-wiki source_catalog status` 返回 `attempt to write a readonly database` | 1 | 不重试、不授予写权限；改用成功的 `worker-status`、目标级只读查询和文件元数据，列为产品缺陷 |
| E-007 | Phase 0 | 标称只读的 `company-wiki source_catalog query` 同样尝试写只读数据库 | 1 | 不重试、不授予写权限；改用 SQLite `mode=ro&immutable=1` 的显式只读查询或文件清单 |
| E-008 | Phase 0 | 首次通过 JS 包装调用 sqlite3 时命令字符串引号导致 JavaScript SyntaxError，命令未执行 | 1 | 不重复同一引号写法；改用模板字符串并把 SQL 作为 PowerShell 单一双引号参数传入 |
| E-009 | Phase 1 | 第一次真实 `source_preparation` reuse-only 调用失败：company-wiki resolve 尝试写只读数据库 | 1 | 保留完整错误链；按权限协议申请仅运行同一无下载命令的升级权限，并披露它可能触碰 catalog 运行元数据 |
| E-010 | Phase 1 | 获得写权限后第二次 FY2025 reuse-only 调用等待约 60 秒后失败为 `database is locked`，且上游标为 fatal/non-retryable | 1 | 不立即重复；重新读取计划，检查 worker/锁状态并调查只读 resolve 为何需要竞争写锁；保持无下载 |
| E-011 | Phase 1 | 官网 2025 Annual Results Presentation PDF 的浏览器点击返回 internal error | 1 | 不反复点击同一入口；同一官方 2025 Results HTML 已包含核心产量指引、资源与矿山表，后续只在确有独有信息时再尝试 PDF |
| E-012 | Phase 1 | 沙箱内 `Get-CimInstance Win32_Process` 被拒绝访问 | 1 | 不申请仅为审计进程清单的额外权限；使用产品正式 `worker-status` 的 process inventory/lock 状态 |
| E-013 | Phase 1 | 年报文件枚举条件同时匹配通用“2024/2025年年度报告”，产生大量无关输出 | 1 | 不重复该广条件；后续使用已经从 catalog 冻结的两个 exact path 计算 hash |
| E-014 | Phase 1 | 第三轮前 help 命令误用不存在的 `revenue_core/source_preparation.py` 相对路径 | 1 | 命令未进入程序、无副作用；用 `rg --files` 定位已知脚本名后只执行实际入口 |
| E-015 | Phase 1 | 第 3/3 轮 filing-fetch 返回 handle 后，revenue 因 envelope `prompt_injection_status=not_reviewed` 拒绝构建 source record | 1 | 按技能三轮规则停止；不补造审查状态、不继续调用；从既有 journal 核对 outcome/download，必要时使用已核验 canonical local_document fallback |
| E-016 | Phase 6 | 首次独立 post-run 反算使用不存在的 `segment.scenarios.*.annual_revenue`，只读脚本报 KeyError | 1 | 读取实际结果结构后改用 `effective_revenue`；重跑全部通过，模型结果未改变 |
| E-017 | Phase 1/6 | native `render_markdown` 对合法 draft 报 `publication_receipt gate_ids mismatch` | 2 | 验证带 input 的 formal-only 分支与去 input 的 legacy 分支均不支持该 current-schema draft；不改 renderer、不伪造 formal receipt，生成明确标注的隔离摘要并保留原始 JSON |
| E-018 | Phase 6 | 运行期间其他 agent 持续提交/编辑三个仓库，产品 HEAD/工作树不是静态目标 | 多次观测 | 不追逐或覆盖并发实现；在 contract 变更后完成一次封存重跑，用 RUN_MANIFEST 固化当时关键文件与产物 hash，并把封存后 renderer 修改排除在本次结论外 |
