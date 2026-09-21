# 基线、真实旅程、测量与部署执行卡

全部status=planned。每卡继承[固定九步](START_HERE.md)和[独立验收](review_and_handoff.md)，这里只列专属步骤，不能省略共用步骤。路径前缀RF、CW、FF在I-00-A分别绑定三仓；运行目录均使用未来隔离副本。RF当前为C:/Users/郑曾波/Projects/revenue-forecast。每卡证据输出到execution_runs/<ID>/<attempt>/，不是本历史审计目录。

## I-00-A — 冻结基线与隔离范围
Parent：I-00。依赖：无。Owner：集成负责人。资格：只读基线，不是修复。

必读：../audit_report.md的现场边界；../evidence/final_integrity.json；../evidence/concurrent_normalizer_verified.json。允许写：本次执行记录和新建隔离目录；禁止写三仓产品、raw、生产DB和worker状态。

1. 记录当前三仓绝对路径、HEAD、dirty清单、实际技能入口与解释器；Git ownership失败保留错误，不能以空HEAD继续diff，不改全局safe.directory。
2. 计算拟修改源和配置的hash；区分原有dirty与本次diff。后续卡按需要扩充基线，不要求无关文件全仓重哈希。
3. 从已存在配置读取data roots、catalog位置、worker控制文件和安装路径。记录环境变量名称与非敏感配置指纹，密钥不入日志。
4. 制定隔离映射：三仓源码副本、配置副本、独立DB与输出目录、禁网络默认。若worktree不包含用户未提交改动，明确复制哪些文件与hash，不静默遗漏或提交用户修改。
5. SQLite使用支持的一致性备份/只读snapshot；确认输出在隔离目录。禁止仅复制活跃DB主文件而遗漏WAL；若无安全快照能力，卡标blocked，由存储owner解决。
6. 隔离进程列出实际加载模块和所有有效写目录，确认没有回落到生产默认路径；此检查前不跑scan/fetch/worker。

验收：三仓路径和版本可追溯；故意留一个未绑定写目录时禁止执行；旧用户dirty仍在。恢复：只停本次隔离进程，保留基线，无生产状态可回滚。交付baseline.json、paths.json、snapshot说明及独立检查。

## I-00-B — 绑定当前源码、样本和命令
Parent：I-00。依赖：I-00-A。Owner：集成负责人和各卡owner。资格：每卡开工前提。

锚点：RF/scripts/source_preparation.py；RF/scripts/revenue_forecast.py；各分区卡声明的现行函数；旧真实命令位于RF/audit_review/2026-09-18_real_company_skill_audit/runs/*/run.json。允许写：binding/commands与隔离测试；不修改旧run.json。

1. 用CodeGraph定位卡片函数和调用方，读当前源、参数解析与测试；保存符号位置和sha。旧行号不一致只说明需更新绑定，不能按旧行硬改。
2. 读取[样本清单](sample_manifest.json)和[固定矩阵](scenario_matrix.md)，重算所需原件hash；样本不符先blocked，不按公司名找一个相似年报替换。
3. 从旧命令获取已证实参数，但不直接重放其中--allow-download或生产cwd；把cwd/config/output/db依赖绑定到隔离目录。入口没有隔离能力时先提出最小依赖注入修复卡，不能猜一个不存在的--config参数。
4. 两阶段绑定：实现前冻结基线命令、隔离环境、允许改路径及专业决定；新接口/测试明确planned、不执行，但不阻断获准编辑。实现后读新源码和参数，再编写commands.json每条真实argv、cwd、超时、expected rc、业务结果、写目录和网络目标；所有null/unbound填完并由reviewer核查后才运行该命令。
5. 测试命令使用当前源码中真实存在的test文件/nodeid；先只收集需要的测试，记录确切收集数；若导入副作用不能隔离则停止，不把collect失败当“无测试”。
6. 将入口、依赖、样本和命令一起绑定到具体卡attempt；后续卡可复用未变部分，但变动必重核。

验收：故意配置生产DB或不存在参数，绑定必须不准执行；合格的纯读取命令能够找到精确模块。这里只验命令可定位，不认证产品行为。停止：路径或权限不明确。交付binding.json、commands.json与source anchors。

## I-00-C — 修复现有验收器的证明范围
Parent：I-00。依赖：I-00-B。Owner：验收工具负责人；独立审查者验收。

锚点：RF/assurance/unified_completion/uc/scenarios.py::closure_report、verify；RF/assurance/unified_completion/scenarios/scenario_registry.json；RF/tools/receipt_validator.py::validate_receipt；RF/tools/closure_gate.py::_validate_receipts；../reviews/aug13_independent/checks.py（旧探针只读其逻辑，不覆盖旧输出）；../reviews/aug13_independent/review.md。state的具体更新路径由I-00-B通过现行调用链绑定。允许改：这些现有验收入口及最小测试；禁止新造另一套完成状态产品。

1. 在隔离目录保存当前197场景的原义务、tier、证据路径、输入/oracle绑定；明确未知tier不能等价满足。
2. 冻结六负例：全部passed但无证据；READ10引用不测deadline的测试；同一有效组合旧PASS后新FAIL；空commands；空invariants；删除CA206/301/302原义务仅保留缩小卡。六者都不得解锁相应业务完成。
3. 冻结正例：一个明确适用场景具备真实输入、原始执行结果、独立oracle、正确tier/版本与结论；只允许该范围完成。预期非0错误案例应保留raw rc，经expected rc和业务断言认定负测成功。
4. 专业reviewer先确定旧状态迁移和“最新有效结果”的组合键/时间排序，禁止弱模型只取最后一个JSON或只信accepted标签。
5. 在原验收器内修补证据与义务关联，重跑六负一正并检查旧历史不被改写。任何格式验证不得冒充人工语义oracle。
6. 跨入口调用现有汇总器验证：下层blocked对应上层仍blocked，不能仅在备注保留缺口却summary=true。

退出：六负例都拒绝，正例仅限域接受；原义务与后继分开。恢复：撤回本次隔离修改，不改旧registry/receipt。设计未冻结时blocked，不能为了全绿删除场景。

## I-00-D — 活动指南与退役边界
Parent：I-00。依赖：I-00-B。Owner：三仓文档负责人。

必读：三仓当前SKILL/AGENTS/CLAUDE/README/DEPLOYMENT/OPERATIONS中实际存在文件、审计报告退役项；不存在的文件记录NA，勿为凑齐创建。允许改：活动指南；历史planning和收据只加导航关联，不改原结论。

1. 列出现行入口、唯一writer、raw新写入和外部根复用的不同规则；核查与实际配置/调用一致。
2. 标明退役研究writer、冗余markdown producer、取消迁盘；删除活动操作指引中的过时启动动作，保留历史文档原貌与时代说明。
3. 对capture真实获取日与as-of重建边界、schema版本、review恢复入口写条件和失败分支；未实现的命令标未实现，不能用文档发明能力。
4. 用“新模型只读活动指南”的干读检查：能找到唯一入口、不启动旧writer、不擅自resume、不重复下载已有raw。

验收：四个干读问题都有指向当前代码/契约的答案；若入口尚缺，链接具体未完成卡。恢复：只撤回本次活动文档差异。

## I-07-A — 固定样本与前置状态建档
Parent：I-07。依赖：I-00-B。Owner：独立真实验收者。

输入：[sample_manifest.json](sample_manifest.json)，其中紫金FY2025、小米FY2025、微软FY2026原件引用来自旧只读证据。允许写：隔离case数据/配置与证据；不搬动真实原件。

1. 按manifest路径重哈希目标，匹配company/market/year/provider ID与请求，不凭文件名判断。
2. 复制必要原件/sidecar到隔离root，保留原hash；不同测试状态只在隔离catalog构建，不UPDATE生产review或删除生产副本。
3. 三种状态分别建立独立case目录：已索引合格；文件存在但未注册；确实缺失。原样本当前已有文件，第三种仅是隔离模拟，不能叫真实缺失live样本。
4. 固定as-of 2026-09-18用于旧失败恢复。9/19后获取的capture时间保留真实值；若现契约不允许重建，记历史重建不支持，不倒填时间，另开当前as-of研究case。
5. 外部only合格真实样本暂未绑定，保持blocked；不删其它位置制造only。

验收：状态区分可由文件/hash和catalog查证；缺失模拟与真实live标签分开。交付case输入快照及before计数，不计预测成功。

## I-07-B — 三市场来源链与二次复用
Parent：I-07。依赖：I-07-A、I-01、I-02、I-03、I-04、I-05、I-06。Owner：独立验收者。

入口：安装态RF/scripts/source_preparation.py；具体argv按I-00-B，不调用helper冒充。案例：scenario_matrix的CN/HK/US各三状态、重复请求、注册失败恢复。

1. 固定每case初始asset/catalog/worker状态及provider/scan/read/producer事件计数；真实调用数不能由artifact INSERT推算。
2. 按已冻结命令运行一次，检查来源链各阶段：raw→注册→资格→review→适用工件→实际消费。正确拒绝要同时返回可执行恢复需求。
3. 同输入第二次运行；已有有效raw两次都不下载，第一次注册恢复后第二次不重复注册有效版本；工件有效不重跑producer。允许的只读query不强制0次。
4. 核对handle身份/hash/期间、真实读取内容、consumer输出，不仅json字段存在。旧失败样本必须回到同用户入口成功或得到明确尚缺信息。
5. live provider测试单独记录网络调用与授权目标；provider不可达不能用mock补签live。

退出：固定案例各有实际结果；三公司仅来源准备通过，仍未授予正式预测资格。缺一市场/真实路径不得总体写三市场通过。恢复：保留已取得raw，只回退当前隔离变更。

## I-07-C — 跨根与未知公司泛化
Parent：I-07。依赖：I-07-B。Owner：独立验收者。

输入：矩阵X01—X05。允许写：隔离root/config/catalog；真实外部根只读。必须有高级reviewer冻结适配器支持范围。

1. 对同bytes多根分别核对hash/location，不以root计数当不同来源。
2. 在隔离配置增加此前未命名的同构第五root，使用新root名和非fixture公司；以相同支持的adapter/profile完成scan/resolve。
3. 对未知布局给明确unsupported，不自动猜身份/adapter。
4. 对companies-only/dayu-only/external-only分别跑；仅隔离构造可支持隔离资格，真实external-only缺样本保持blocked。
5. reviewer在测试前固定另一家公司/文件作为保留泛化样本，验证无按公司名硬编码；不得临时换成已成功公司。

退出：每个格单独结论，无外部only实证就不签该资格；它不阻止与其无关的已验证本地读场景。

## I-07-D — 故障矩阵与断点恢复
Parent：I-07。依赖：I-07-B、I-09。Owner：独立故障验收者。

输入：矩阵F01—F06与各专属卡oracle；允许：scratch进程/DB/registry。产品stdout异常与raw rc必须保留。

1. 每个故障单独attempt，恢复初始隔离状态，避免前一个case污染后一个。
2. 分别在provider返回、raw提交后scan前、scan错误、DB事务内锁等待、producer执行、发布提交边界注入；记录实际触发位置和发生次数，没触发的测试无效。
3. 检查失败时没有可消费的伪合格结果；已有raw保留，错误cause/code/retryability不丢失。
4. 清除故障后从原入口重试；比对新增下载/写入/调用数，不能靠重建全部资产掩盖幂等缺陷。
5. 杀进程只针对本case记录PID，确认进程归属隔离树；不操作真实worker。

退出：每个触发点有前后状态、错误与恢复证据；不能以单一“抛了异常”通过。无可靠注入能力先blocked。

## I-07-E — 从合格输入到正式预测产物
Parent：I-07。依赖：I-07-B、I-08、I-09、I-10、I-11。Owner：研究执行者；独立买方验收。

入口：RF/scripts/revenue_forecast.py及受支持验证/发布入口，I-00-B读取当前argparse绑定。输入是前序真实source-preparation产物，禁止拿旧NOT_FORMAL草稿换名。I-10包括31模型公式资格及先行I-10-A：本case实际采用模型的D-E披露适配在I-11-B之前形成独立资格记录，I-07-E只消费和复核；其他未使用模型披露适配不阻塞本公司。准确性F归后继I-12，不能形成I-10→I-12→I-07-E→I-10的循环。

1. 为三公司各冻结基期、分部口径、币种单位、信息日、年度路径与来源claim；缺信息显式保留，不伪造capture。
2. 将管理目标和主要增长驱动按I-11映射，按适用模型卡处理合并/内部抵销、H1锁定、微软重述等已审关键口径。
3. 经真实计算→验证→发布到隔离正式格式registry，记录完整输入/输出与签名资格；没有正式签名能力时可有研究草稿，但正式发布格blocked。
4. 独立复算分部加总、年度增量、敏感性和场景约束；跨根来源失效能追溯到相关输入/产物。
5. 输出三公司独立结果，不因其中一家成功写3/3。交I-13买方验收；本卡仍不授予样本外准确性。

退出：每家公司有完整可审查来源链和产物，或明确blocked；无全文研究包不能通过。

## I-14-A — 性能测量先验证失败分支
Parent：I-14。依赖：I-00-C。Owner：测量负责人。

锚点：RF/tools/slo_probe.py；RF/tools/tests/test_slo_probe.py。允许修改测量器和隔离测量测试，不放宽既有预算。

1. 读当前子进程启动、rc判断、业务输出解析和RSS采样；记录单位与时间锚点。
2. 三个固定进程夹具：exit7且stdout似成功；exit0但业务结果失败；进程存活时分配可测内存后退出。前两者必须判业务测量失败，第三者需有PID匹配的存活期间样本，未采到不能记峰值0。
3. 单独冻结采样间隔、平台可用的peak方式和测量误差规则，由运维reviewer决定；不把合成内存量等同精确RSS oracle。
4. 保持现有exact/latest/bundle p95=5秒与peak_rss_gb=2的预算约束，改预算需独立理由，不随测量失败改阈值。
5. 成功延迟分布与失败率分开报告；不丢失败请求来宣称服务满足SLO。卡通过仅证明测量器，生产SLO需I-16实际测量。
6. 当前源码还有两项必须纳入边界：`--catalog`只检查存在，实际resolve使用config；`bundle=exact[:]`是代理计时。绑定catalog与config不一致必须拒绝或证实实际目标一致；测真实bundle消费路径，不能以复制exact延迟授予bundle资格。沿用原proxy历史记录但明确范围。

退出：三种夹具行为正确；命令总耗时/业务延迟/采样窗口分别记录。恢复：回退测量器隔离差异，不碰生产服务。

## I-14-B — 自然时间与UI观察证据
Parent：I-14。依赖：I-14-A。Owner：独立观测者。

必读：../reviews/wiki_legacy/review.md的WR窗口；../reviews/aug09_plans/manual_cases.json中A09-055/056；旧原义务的实际观察周期。允许写证据，默认不启动后台。

1. 将scheduled_at、started_at、sampled_at、finished_at、quick_check耗时分列。重叠窗口不能相加制造自然时长。
2. 合成时间输入：观察00:00–00:29，结束后quick_check8分钟；oracle观察29分钟而不是37分钟。此例只验证计时算法，不是真实观察资格。
3. 登录30/60/120秒检查使用同一事件锚点和预定时间窗，时间容差在试验前由reviewer冻结；实际支持的UI捕获能力未具备时标blocked，不用事后日志造即时截图。
4. 把自然日/周/月需求原文ID映射到I-17待运行日历；未到时点保留pending，不能用模拟clock达标。

退出：计算和证据分类正确，未执行的自然/UI格仍未完成。恢复：停止本次观察，不改变worker原暂停意图。

## I-14-C — 在真实异常出口验证脱敏
Parent：I-14。依赖：I-00-B。Owner：日志维护者。

锚点：CW/src/company_wiki/source_catalog/worker.py::_write_unhandled_exception_event；旧证据../reviews/wiki_legacy/review.md。允许改异常出口、现有redactor及关联隔离测试。

1. 创建纯合成异常值含Authorization: Bearer SYNTHETIC_AUDIT_TOKEN和token查询参数，不能读取实际密钥。
2. 通过真实异常事件写出路径进入scratch日志，检查整行/嵌套cause/截断边界，不仅检查键名或独立helper。
3. 原始秘密marker在stdout/stderr/事件中不得出现；保留非敏感error code、stage和request ID便于定位。
4. 加一条无敏感数据正常异常，确保错误语义不被整体吞掉；定好脱敏规则后复验未知键的敏感值。

退出：实际出口不泄露合成marker且仍可诊断；不声称覆盖全部未知secret形式。恢复：撤回隔离实现，保留合成日志。

## I-16-A — 绑定拟部署完整组合
Parent：I-16。依赖：I-07-E、I-07-D、I-08、I-09、I-13、I-14、I-15。Owner：部署负责人。

允许写：部署提案与隔离安装目录；生产变更尚不执行。

1. 列三仓源commit+dirty内容hash、安装副本hash、解释器/依赖、config/policy/flags/schema版本及真实加载模块；不能只比较仓库HEAD。
2. 在新进程检查加载路径，与安装副本及预期组合一致；用旧加载模块的负例证明能发现版本错配。
3. 记录上个可恢复完整组合、迁移是否可逆、raw/registry/catalog兼容边界。不能证明恢复则blocked，不以关闭严格门回滚。
4. 对部署影响范围列出具体写入、停止/重启进程和恢复步骤；按既有授权执行可逆准备，真正未授权影响再向用户说明具体请求。

退出：提案与恢复演练在隔离环境通过；资格仅“可进入具体部署窗口”，尚非已部署。

## I-16-B — 部署后的同入口复验
Parent：I-16。依赖：I-16-A。Owner：部署负责人；独立验收者。

前置：具体部署范围已获授权、组合冻结、恢复可用。运行生产步骤时另建新的attempt，不能把隔离绿灯当生产已完成。

1. 记录用户原worker状态；需要时只在明确窗口启动已绑定版本，原paused任务不能因工具退出无条件resume。
2. 安装/配置后从实际用户入口验证：已有复用、新文件摄取、适用工件失效最小重算。记录所加载组合，与I-16-A对照。
3. 用I-14已验证测量器测业务失败率、时延和内存；sample不足不作总体SLO推断。
4. 若失败执行冻结恢复方案，保留已取得raw/journal；核实回到上个可用组合和原worker意图，不重复生产故障注入。

退出：实际部署结果与恢复边界有记录；未运行则blocked。交I-17自然观察，不立即宣布持续服务通过。

## I-17-A — 按原义务积累自然观察
Parent：I-17。依赖：I-16-B、I-14-B。Owner：独立观测者。

1. 从原历史账本列必须保留的7 daily、2 weekly及monthly等原要求、后继是否获准替代、适用服务承诺；由reviewer签定具体要求清单。不能将所有旧周期盲目复活，也不能因耗时长删除仍有效要求。
2. 为每项填写真实开始时间、到期时间、时区、观察频率、允许中断和失败恢复规则；没有这些字段不开始计时。日期按实际运行启动，不沿用本文日期。
3. 每次记录真实采样和异常，覆盖pause/resume、重复请求与版本一致性；如失败，按事先规则重启该资格窗口，不把中断删掉拼接。
4. 时间未到时保留in_progress；只有用户明确要求后才创建持续监测自动化，当前卡不自动安装任务。

退出：每项真实时长与内容足够，或明确仍pending；普通只读功能资格不受未相关自然窗口牵连。

## I-17-B — 从原用户目标逐项终审
Parent：I-17。依赖：I-17-A、I-07-C、I-12、I-13、I-00-C。Owner：未参与该项实施的终审者。

1. 从总纲I-00…17逐条查所有子卡、NA理由、依赖与真实用户旅程；子卡数量全绿不自动推出parent完成。
2. 在当前有效组合重跑I-00-C六负例，缺真实场景/自然观察/证据映射必须继续阻断相应业务完成。
3. 分别报告来源获取、数据湖/工件、正式预测、买方质量、准确性证据和持续服务六种资格；“未证明优于基准”是合法准确性结论，但不能改写为提高。
4. 对审查期间发生的并行代码/config变更重核受影响证据；不向过期版本发通过结论。
5. 输出最终报告包含已完成、限域通过、blocked、合理退役/NA及下一动作。禁止以“全部通过，除……”掩盖阻断项。

退出：结论与证据一致，失败也能如实关闭本次验收工作；产品完成资格仅授予确实满足的范围。

## I-14-D — 脱敏裸值贪婪语义收窄到单 token（C13 立卡）

Parent：I-14。依赖：I-00-B。Owner：日志维护者；独立 reviewer。

来源：I-14-C r5 的 `decision.md` §C13。该缺陷已**冻结不改**（`test_f08_c13_multiline_loss_is_frozen_not_hidden`），
因为它**改则破坏 E4b 的 193 字符基线**；故本卡是它独立的、有自己 oracle 的收窄卡。

锚点：CW/src/company_wiki/source_catalog/redactor（`_BARE_VALUE`，源自 r1，`X+(?:\s+X+)*`）；
I-14-C 的 `iso/product_r2` 证明该行为**继承自 r1、非 r3/r4 引入**。

1. 先量出**当前**基线：裸值停止集为 `,;&"'|` 加空白，且**未加引号的值跨换行**。
   实测（F-I14C-R4-02）：`a=1 token=<marker> b=2` → `a=1 token=<redacted>`；
   而 `'upload failed for token=<marker> doc=17\nstage=summarize code=llm_global_failure request_id=req-1'`
   → `'upload failed for token=<redacted>'`（reviewer 的 24 字符 marker：**112 字符进、34 字符出**，
   `doc=17`、`stage=summarize`、`code=llm_global_failure`、`request_id=req-1` 全部丢失）。
2. 收窄候选：裸值只吃**单个 token**（遇空白即停）。注意这不是"截断"——34 ≪ 200 的截断上限。
3. **新 oracle 必写**：E4b 的 193 字符接受长度**正是由当前行为导出的**；收窄后该基线必然改变，
   信封宽度也会变。新 oracle 必须在改代码**之前**冻结，且不得调用被测函数生成 expected。
4. 负例：多行诊断（`doc=17`/`stage=`/`code=`/`request_id=`）在收窄后**必须存活**；
   纯合成 marker 必须仍被脱敏；既有 rule table `cred-multiline-swallow` 系列需按新语义更新
   （更新的是**语义期望**，不是把失败改绿）。
5. 不得以"冻结测试失败"为据回退；该冻结测试的**唯一正当结局**是本卡写完新 oracle 后由 reviewer 改写它。

退出：裸值不再跨行吞掉后续诊断键，且 E4b 新基线经独立 reviewer 复算。
恢复：回退 redactor 与 rule table 到本卡前像；保留合成日志。

## I-14-E — 重启节点的时序抖动（负载相关，非树差异）

Parent：I-14。依赖：I-00-B。Owner：测试维护者；独立 reviewer。

来源：I-14-C r5 的 `decision.md` §19-②（`OWNER_DECISIONS.md` §13 T1-7 授权立卡）。

1. 观测带（已实测）：每树 12 次 × 2 轮 = 24 次运行中 **6/24 失败**。
   关键事实：**"失败更多的那棵树"在两轮之间翻转** ⇒ 该抖动是**负载相关**，不是树差异。
2. 因此本卡修的是**产品测试的时序假设**，不是产品实现。**不得**为让测试变绿而改产品代码。
3. 先冻结观测：把两轮 24 次的原始记录（树、轮次、通过/失败、负载快照）写成 oracle 的一部分，
   expected 由该原始记录**手算**，不由重跑生成。
4. 两种重启节点分别建立可失败用例：抖动窗口以**独立测量**出的带宽为准，不得事后放宽到"刚好通过"。
5. 若抖动可归因到某个具体资源争用（非"随机"），记录该归因；否则如实写"未定位到单一根因"。
6. `~25%` 是观测值，**不是**冻结阈值；本卡不得把它升格为规范常量。

退出：测试在负载波动下不再随机红/绿，且无需改动产品代码。
恢复：回退测试改动；保留 24 次原始观测记录。

## I-14-F — 深层 cwd 下的 WinError 206（产品侧短 basetemp 约定）

Parent：I-14。依赖：I-00-B。Owner：测试维护者；独立 reviewer。

来源：I-14-C r5 的 `decision.md` §19-③（`OWNER_DECISIONS.md` §13 T1-7 授权立卡）。

1. 观测（已实测）：cwd 路径 166/167 字符时，两种节点**在两棵树上 3/3 全部失败**；
   改短 basetemp（74/75 字符）后 **3/3 全部通过**。⇒ 与 cwd 深度强相关，与树无关。
2. 这是 `WinError 206`（文件名或扩展名太长）在**产品侧**的约定问题：应为测试/子进程建立
   **短路径 basetemp 约定**，而不是要求调用方把 cwd 挪浅。
3. 约定须写成可判据：给定 `cwd` 与 `basetemp` 长度，何时使用短路径回退、回退到哪里、如何清理。
4. 负例：一个故意超深的 cwd 必须**被约定接住并成功**，而不是报 206；一个正常深度的 cwd
   不得被无谓地改道（否则掩盖真实路径问题）。
5. 不得以"把 cwd 缩短"当作修复——那是绕开问题。也不得靠改 `pytest` 全局配置放宽。
6. `START_HERE.md` 已有纪律：`pytest --basetemp` 只能指向**本次新建的空目录**，
   不得指向 attempt 根、证据根或上次测试目录；本卡约定必须与该纪律一致。

退出：深 cwd 下不再出现 206，且正常 cwd 行为不变。
恢复：回退约定实现；保留 166/167 与 74/75 两组原始观测。

## I-14-H — natural_window.py 的两个产品级缺陷

Parent：I-14。依赖：I-00-B。Owner：观测逻辑维护者；独立 reviewer。

来源：`OWNER_DECISIONS.md` §7 第 4 项 + §13 **T1-10**（授权立卡，**产品 + 计划双侧**）。

锚点：I-14-B 的 `iso/natural_window.py`（`SUT_VERSION = "i14b-after-2"`；
`BASIS_REGISTRY` 在 `:60`；`derive_window` 在 `:128`；`_claim.basis` 分发在 `:199-222`）。

1. **缺陷①：`claim.basis` 无枚举校验。** 实测被 accept：`basis=''`、`basis` 缺键、`basis=None`、
   `basis='wall_clock'` **全部被接受** ⇒ J1/J2/J3/J11 可被一个字段名绕过。
   修复：`basis` 必须属于封闭枚举 `{sample_span, command_total, observation_plus_quick_check,
   sum_of_windows, union_of_windows}`；未登记/空串/`null`/缺键一律**拒绝**（`R-BASIS-UNKNOWN`）。
2. **缺陷②：`union_of_windows`/`sum_of_windows` 把 quick_check 计入自然观察时长。**
   实测：**2220 被接受而诚实的 1740 被拒** ⇒ 方向倒置。
   修复：自然观察区间**只由观察阶段构成**；无 `windows[]` 时 `intervals = [(started_at,
   observation_finished_at)]`，quick_check **永不进入**；`union_seconds`/`sum_seconds` 同为观察口径。
   并另加 J15 覆盖"把 quick_check 改名成第二个窗"的变体。
3. **⚠ ②已烧进冻结期望。** `harness/frozen_expectations.json`（r1，sha256
   `3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b`）中
   `expected.W1.computed.union_seconds = 2220`。
   修复**必须同时**以**追加式 provenance** 更正该期望（旧 2220 → 新 1740），
   并新增锚定断言 `sum_seconds=1740`、`observation_interval_count=1`、
   `quick_check_overlap_seconds=0`、`quick_check_in_observation_intervals=false`。
4. **不得回改冻结正文。** 旧值必须保留于 `expected_superseded`（含 old/new/`pre_image_sha256`/时刻/原因），
   并附 r1→r2 期望映射的机械 unified diff。**"从未有过 2220"是禁止的写法**——
   I-14-B 已按此形态落地过 r2，本卡沿用同一形态（`oracle.md` §11.4 为范本）。
5. 注意 I-14-B 的 r2 已**先改实现、后冻结期望**（与其 §4 理想次序相反）。本卡若沿用，
   必须同样如实声明时序，并以 `before/cmd-CASES-r2-r1sut` 型独立复现证明期望不是"照修好的实现写"。
6. 不得改 `SUT_VERSION` 以掩盖差异；不得以"更新期望贴合实现"代替建立新 oracle。

退出：两个缺陷各有可失败用例（RED→GREEN），且期望更正以追加式 provenance 留痕。
恢复：回退实现与期望追加节；保留 `expected_superseded` 与全部原始输出。
## I-14-I — 容器 basis 的逐例拒绝（I-14-H 强制收尾残卡 / RIDER）

Parent：I-14。依赖：I-00-B、I-14-H。Owner：观测逻辑维护者；独立 reviewer。

来源：**I-14-H 独立 reviewer 的强制收尾条件**（`execution_runs/I-14-H/a20260919-01/review.md`，
sha256 `97997d6d26af5a1fd36e486c508a027642f4492af1f5415fe3f25bc929e130b2`，
§5「正确推迟，但附带强制收尾条件」+ §6 + 末节「建议的 status 决定」）。I-14-H 因此只获得
**conditional / accepted_scoped**：验收证据仅为 **12/14 冻结用例 + 12 例 pytest 套件**，
**全 14-case 端到端 `run_cases.py` 门从未通过**。本卡是该条件的唯一兑现路径，**不得消失**。

锚点：I-14-B 的 `iso/natural_window.py`（`SUT_VERSION = "i14b-after-2"`，sha256
`7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796`）；
崩溃行 `:202` `if basis not in BASIS_REGISTRY:  # J16 / P1`。
冻结门：`harness/run_cases.py`（`f2a07d0b…`）+ `harness/cases.i14h.json`（`40260c24…`，14 例）
+ `harness/frozen_expectations.i14h.json`（`bffb11c2…`）。

1. **缺陷（残留，I-14-H 未修）：** `:202` 的成员测试对**不可哈希容器**求 hash ⇒
   `TypeError: unhashable type: 'list'` / `'dict'`。逐例直接调用 `classify` 即复现，
   崩溃点精确在 `:202`；整批次因此 `raw_returncode=4`、`sut_report.json` 未生成、批中止。
   **修复：** 在成员测试前加类型护栏（例如 `isinstance(basis, str)`；非字符串一律
   归入未登记 ⇒ `R-BASIS-UNKNOWN`），**逐例**拒绝，而不是让整批崩溃。
2. **必须逐例满足的冻结期望：** H5 `basis=['union_of_windows']` 与
   H6 `basis={'kind':'union_of_windows'}` 的冻结期望均为
   `{"verdict":"reject_claim","refusals":["R-BASIS-UNKNOWN"]}`，**当前实现无法满足**
   （xfail 只记录，不等于通过）。
3. **不得退化为 r1 的静默 accept：** 缺陷版 r1（`495a4411…`）对 H5/H6 返回
   `accept_claim` / `refusals=[]`，是越权接受。修复方向是 **fail-closed 的逐例拒绝**，
   不是回到 r1。I-14-H 的 `harness/test_i14h_natural_window.py:183-190` 的 xfail 用例
   （`test_container_basis_refused_per_case`）**应在修复后移除 xfail 并转正**。
4. **注意"容器"≠只有 list/dict：** 实测 `{'union_of_windows'}`（set，可哈希）已会
   走 `R-BASIS-UNKNOWN` 分支；真正崩溃的是 **list / dict**。修卡须对
   **list / dict / set / tuple / 嵌套容器**逐一冻结期望（不得把 set 的"碰巧正确"
   当作已覆盖），并补一条负例确保**登记过的字符串 basis 仍按实质裁决**、
   不被类型护栏误拒（阴性对照）。
5. **补跑并落盘（本卡的退出物）：** 移除 xfail 后，用**未修改的** `run_cases.py`
   + **未修改的** i14h 冻结期望补跑**全 14-case 门至 rc 0**，把 `cases_report.json`
   落到 I-14-H attempt 的证据目录（新增 attempt 或 `after/` 子目录），
   并记录 `mismatch_count=0`、`accepted_ineligible=0`、SUT rc 0。
   在补跑完成前，I-14-H 的验收陈述**必须**继续限定为"12/14 冻结用例 + 12 例 pytest 套件"。
6. **同一修卡内一并处理 I-14-H reviewer 记录的两个未披露弱化（UNDISCLOSED WEAKENING）：**
   ①`:241` `quick_check_in_observation_intervals` 与 `:248` `sum_used_for_natural_duration`
   是**硬编码字面量** `False`（并非由区间内容派生），故 `run_cases.py` 的 `REQUIRED_KEYS`
   形状门与 `test_d2_observation_intervals_contain_observation_only` 对这两个键的断言
   **恒真**、不承担判别力——实测两者在 5 个情景（诚实 1740 / 不诚实 2220 / 改名窗变体 /
   合并窗 / sample_span）中取值集合大小均为 **1**。更严重的是：在快检**确实进入**观察区间的
   情景下（union_seconds=2220、quick_check_overlap_seconds=480、observation_interval_count=2）
   该字段仍报 `False`，即**字面量与事实相反**，会给下游读者虚假保证。
   应改为**派生值**，并对这两个键补**可失败**断言（在重叠情景下必须为 True / 参与时长必须为 True）。
   真正的缺陷②判别力目前只来自四个**实算**字段：`union_seconds`、`sum_seconds`、
   `observation_interval_count`、`quick_check_overlap_seconds`（实测取值集合大小均 ≥ 2）。
7. **不得**以放宽冻结期望、跳过 H5/H6、或把门改成 12 例来"通过"；**不得**回改冻结正文
   （沿用 I-14-H 的追加式 provenance 纪律）；**不得**改 `SUT_VERSION` 掩盖差异。
8. 本卡只涉及计时/分类算法在**合成**输入上的健壮性；**不**授予真实自然观察资格、
   真实 UI 即时性、SLO/性能、`disclosure_adaptation`/`accuracy`（沿用 NOT GRANTED）。
   另记：H12（改名窗 + 诚实 1740 声称，双拒绝码 `R-CLAIM-EXCEEDS`+`R-QC-IN-OBS`）
   **无 pytest 对应用例**，仅由冻结门覆盖——补跑全 14-case 门时须确认 H12 实际通过。

退出：全 14-case `run_cases.py` 门 rc 0（mismatch 0 / accepted_ineligible 0）且
`cases_report.json` 已落在 I-14-H attempt 证据目录；xfail 已解除；
`:241`/`:248` 已改为派生值并有可失败断言；以上经独立 reviewer 复算。
恢复：回退 `:202` 类型护栏与派生字段改动；保留本次全 14-case 门落盘报告与
I-14-H 的 xfail 原始记录（作为"修复前确实过不了"的证据）。
