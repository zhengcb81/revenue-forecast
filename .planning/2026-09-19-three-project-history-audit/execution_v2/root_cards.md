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
