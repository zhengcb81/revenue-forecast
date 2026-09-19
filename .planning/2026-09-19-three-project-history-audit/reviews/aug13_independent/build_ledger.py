"""Manual semantic decisions after full reading; enumeration only expands source occurrences."""
from pathlib import Path
import collections,csv,hashlib,json,re

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
CA='audit_review/2026-08-13_three_repo_completion_rebaseline_plan'
ZR='audit_review/2026-08-13_zijin_data_lake_remediation_plan'
# Every interval below was assigned manually, not from PASS/keyword counts.
# H = dated observation, S = supported only within stated scope,
# U = original business obligation lacks sufficient present evidence,
# X = concrete counterevidence to completion/semantic agreement,
# D = older route explicitly superseded, not a current product defect.
V={'H':'historical_only','S':'supported_scoped','U':'insufficient_evidence','X':'contradicted','D':'superseded'}
CASES=[]
def add(prefix,name,rows):
    p=ROOT/prefix/name;end=len(p.read_text(encoding='utf-8').splitlines())
    for i,(start,status,reason,evidence) in enumerate(rows):
        CASES.append(dict(case_id=f'A13-{len(CASES)+1:03}',source_file=f'{prefix}/{name}',start=start,end=rows[i+1][0]-1 if i+1<len(rows) else end,conclusion=V[status],reason=reason,evidence=evidence))
REV='reviews/revenue/item_ledger.jsonl (逐 CA/ZR 当前独立复核，仅作交叉证据，不继承历史 accepted)'
FF='reviews/filing/review.md; reviews/filing/tests (当前隔离 retry、pause、路由及结果契约反例)'
CHECK='reviews/aug13_independent/checks.json (本次独立 hash/size、197 evidence 字段、纯函数反例)'
CARD='assurance/unified_completion/receipts/'

add(CA,'authoritative_execution_plan.md',[
(1,'S','原计划约束清楚区分原承诺与状态入口，明确既有资产先复验；冻结 hash 当次重算匹配，仅支持文档版本与编排设计。',CHECK),
(38,'U','A/B 的锁、证据状态机和 closure 组件存在，但原 current triplet、生产可达性、原始命令证明和逐 tier 语义未由组件存在证明；当前标签可独立推成 ready。',CHECK+'; '+REV),
(64,'U','C/D 原验收包括真只读、活跃 writer/49GB SLO、跨 roots 请求级 policy、amended 最小下载；实际 ZR409 Dropbox 正向改为正确 MISSING，仍缺此入口正向完成证据；ZR205 deadline 有当前纯反例。',CARD+'ZR-409/00_wu_card.md:31; '+CARD+'ZR-409/12_reviewer_receipt.json findings REV001/002; '+FF),
(95,'U','E 原要求 worker 持久 ProcessingDemand、七真实 PDF 两位独立标注及表格阈值；F 原要求逐矿事实/单位/会计与事务发布，不能由同公式 fixture、DAG selector 或 artifact 计数代理。当前 unit 审查保留局部有效实现。',REV),
(123,'X','G 三公司/多状态/真实 provider-worker 目标与 CA302 只合成引擎并排除 worker/下载不等价；H 不可豁免自然累积与 CA206 纯函数卡在同日解锁终验相冲突。',CARD+'CA-302/00_wu_card.md:9-27; '+CARD+'CA-206/00_wu_card.md:9-26'),
(149,'U','I 的删除/回滚原须两个自然零 hit 周期；CA304 接受纯机制不等于原执行完成。后 GP 分批删除需按批保留真实修复，不宣称所有 legacy 今天仍在。',CARD+'CA-304/00_wu_card.md:9-26; '+REV),
(166,'X','J 明文 ZR1101–1105 由更强 CA301–306 替代，实际 CA306.next=ZR1101，ZR1104 又接受同一纯 soak，未补回实际部署/自然累积；最小证据包不能由 summary/existence 代替。',CHECK+'; '+CARD+'ZR-1104/00_wu_card.md:9-26; tests/test_ca305_six_problems.py:98-211')])
add(CA,'completion_assurance_registry.md',[
(1,'S','25 CA 定义及 pending 的编制状态是结构资产；此处规范不是已实现声明。后继卡必须保持强义务，不能只锁卡 hash。',CHECK),
(13,'U','CA001–003 原锁/current环境/CodeGraph生产可达性并不被 control 文件存在和 git 对象存在自动证明；原始完整证据仍需独立验证。',REV),
(42,'S','71 FC+10 waves+5 closure 分组均有映射，支持覆盖登记；5 FC150x 已包含在71中，不能当86个唯一旧义务。建议唯一键去重同时保留分组标签。','legacy_fc_status_registry.md:25-99; legacy_transition_matrix.md:20-96; '+CHECK),
(49,'X','Evidence/Closure 2.0 原要求真实逐 tier、独立命令/副作用、missing证据红；当前 197 passed 全缺 fixture/oracle，label-only AST仍ready，CA305 tests 存在性仍可证明六问。',CHECK+'; tests/test_ca305_six_problems.py:108-163'),
(113,'X','CA201–206 要求真实 scheduler/fanout/自然7/2/1；CA202 明文禁止scheduler注册，CA206排除自然累积但 accepted。此为历史总状态升级错误；不抹去9月后GP实际任务接线。',CARD+'CA-202/00_wu_card.md:12-26; '+CARD+'CA-206/00_wu_card.md:13; '+REV),
(156,'X','CA301–306 原 clean checkout/三真实公司/实际R9/六问均强于实施卡。CA302 reviewer 已知第二矿企与非矿复用紫金仍以minor接受；CA301 reviewer将未做clean checkout判卡外。',CARD+'CA-301/12_reviewer_receipt.json finding005; '+CARD+'CA-302/12_reviewer_receipt.json findings002/003'),
(195,'U','DAG 顺序规范可维护依赖，却不能阻止语义缩水；终局117accepted不是117原始义务完成。ZR1009/110x吸收需显式状态映射，不重复弱终验。',CHECK)])
add(CA,'completion_audit.md',[
(1,'S','I/C/S/P 四类明确旧 accepted 不继承为当前完工，保存已实现资产。71行31/26/9/5为当时证据分类，不是今日故障数或零代码。','legacy_fc_status_registry.md; '+REV),
(23,'H','逐 Phase 已有实现、缺口与禁止动作是8/13截面；相应后继CA/ZR当前逐项复核覆盖，不将旧 Phase RED直接沿用现状。',REV),
(44,'S','准确区别66/71登记和真正当前完工，Phase14不计入71也不能遗漏。旧执行行装饰status、receipt摘要、proxySLO不支持整体完成；该诊断获后续缩门实证。','reviews/aug09_plans/; '+CHECK),
(54,'S','应保留Reader/identity/artifact等可用资产、禁止无条件R9删除。新版仍采用保留局部修复、拆机制与部署、旧史料只读的处理。',REV)])
add(CA,'current_state_audit.md',[
(1,'H','8/13三仓截面有绑定HEAD；原作者未将本轮计划编制称产品修复。当前代码/部署应重新冻结，不能仅由后续真实失败倒推全部旧观察仍成立。',CHECK+'; '+REV),
(17,'H','wiki既有资产、writer读路径、artifact绑定、RootPolicy与隐私元数据是当时观察；649摘要/529+120模型标签只证记录分布，不能推出实际外发或未授权。当前GP002扫描配置及ready契约是另有新证据的断点。','reviews/wiki/item_ledger.jsonl; '+REV),
(48,'U','filing 当时提及exact/latest/auth/retry；当前已独立核安装hash同步及280tests78subtests，仍有call-deadline和并发refcount/部分结果契约反例。保留已修精确授权范围，不把旧bool漏洞直接沿用。',FF),
(65,'H','RF旧3.6/3.7、validator/generator/publication、mine不足是当时证据；4.1新31模型与旧模型升级需分版本。当前原子整组发布问题由新隔离探针支持，其余按当前引擎判断。',REV+'; reviews/revenue/logs/probe_publication.*'),
(86,'S','明确测试环境和真实行为须分开、旧日常skip不能替代R9、代码质量ratchet不等于偿债；这些推理仍成立。具体旧测试数量/CC只保持历史口径。',REV+'; '+CARD+'CA-301/12_reviewer_receipt.json')])
add(CA,'findings.md',[
(1,'H','001–015：作者已识别历史假绿（66/71、非法装饰状态、proxySLO、缺失receipt、self-dep、closure只剩5项、fixture冒充real）；这是已知机制而非9/19才首次发现。当前hash不变，后继卡/终验仍重现同类语义缩水。逐旧FC由revenue分区另有71ID账本。',CHECK+'; '+REV),
(109,'H','016–020：读路径写库、v1/v2漂移、dayu/Dropbox身份、amendment、artifact覆盖等是8/13状态；数据数量本轮不重建当时DB。具体现在缺陷只能由当前入口/原始实跑独立证实。',REV+'; reviews/wiki/review.md; '+FF),
(140,'S','021–022：producer row不是实际LLM/parser调用，prompt安全需实际治理；数量并不能证明外发。当前source_preparation事件仍是DAG计划，不能计本次零调用。',REV),
(151,'H','023–026：旧生成器/validate/draft/发布/矿业与R9/环境错误逐项保留版本，后继部分已修；当前出版半事务有单独反证。不能因环境失败把整批作pass，也不把环境失败当全部产品缺陷。',REV+'; reviews/revenue/logs/probe_publication.*'),
(174,'S','027–029：唯一入口、immutable annex和不复制117卡是合理治理。当前26+30hash匹配证明原规格未静默改写，缩水发生在后继卡/接受门，锁文件不能防语义缩水。',CHECK)])
add(CA,'input_snapshot.md',[(1,'S','本次重算30输入文件hash与size全部匹配；mtime仅是历史观察未当作语义或内容证明。输入漂移处理规则保留，内容冻结不证明实施遵守。',CHECK)])
add(CA,'legacy_fc_status_registry.md',[(1,'S','71唯一FC逐项有旧状态、原因与successor；仅投影分类已核，不继承旧PASS或将26旧C认作26今日bug。5FC150x属于这71而非额外唯一5项。',REV+'; legacy_transition_matrix.md; '+CHECK)])
add(CA,'legacy_transition_matrix.md',[(1,'S','71FC、10waves、痛点逐行映射保留来源和successor，可追溯；FC150x重复为闭环分组。只证登记完整，successor执行充分性由CA/ZR独立条目复核。',REV),
(120,'X','旧计划只有全部强业务门通过才可关闭；8/31terminal虽诚实叫closed_superseded_incomplete，其引用117accepted仍建立在CA206/301/302缩门之上，不能释为所有承诺兑现。',CARD+'CA-206/00_wu_card.md; '+CARD+'CA-301/00_wu_card.md; '+CARD+'CA-302/00_wu_card.md; TERMINAL_NOTICE.json')])
add(CA,'PLAN_MANIFEST.md',[(1,'S','编制完产品pending、历史截面、14文件hash和5annex、25+92/95+102是正确限定的文档资产；本次26+30hash复算通过，ID与pass明确区分。',CHECK),
(60,'S','机器自审能证明唯一性、链接、非空和结构登记；不能证明三仓产品成功。原文自身明确required real缺失blocked、不许豁免自然时间；后续执行未保留这些强门。',CHECK+'; '+CARD+'CA-206/00_wu_card.md:13')])
add(CA,'plan_self_audit.md',[(1,'S','结构、旧项映射、用户痛点和防弱模型步骤经全文读属计划质量，hash与映射数量可重算；这不是产品PASS。相对链接0的旧文字不能替代当前有效链接验收。',CHECK),
(65,'U','渐进安全与动态保证设计明确，但未定义卡片缩范围必须派生不可豁免业务子节点，允许后继accepted掩盖部署待办；自然周期24/7/35与ZR36/9/35需版本化裁决。',CARD+'CA-202/00_wu_card.md; '+CARD+'CA-206/00_wu_card.md'),
(88,'S','显式声明计划未改产品/生产未授权/未知决策必须实施期审，合理。最终自审通过仅计划级，不能沿用为终局功能级。',CHECK)])
add(CA,'progress.md',[(1,'H','逐条进度记录编制/复核/整合，不是运行产品证据；结尾明确本轮文档完成、未来全部pending。hash冻结支持保留该历史截面，不要求重演8/13操作。',CHECK)])
add(CA,'project_goal_and_pain_points.md',[(1,'U','根目标是所有公司来源→ready→模型→发布闭环，需用户可用而非文件存在；三仓单责与外部root只读正确，现有入口依旧未满足原全部需求。',REV+'; '+FF),
(34,'H','P01–P11定义当时痛点与资产，不是全新当前bug；原始测试/代码债务数字仅该版本。当前证据链显示P01机制再次发生，但其余须按后继修复判断。',REV),
(116,'S','原文要求保留已有资产且六问逐项答，已采纳。CA305虽然把问题逐项列出，实质只验证accepted/文件存在/hash长度，未兑现六问的行为oracle。','tests/test_ca305_six_problems.py:98-211')])
add(CA,'task_plan.md',[(1,'S','PhaseA–F编制全部completed与未来A–J全部pending区分清楚；锁/owner职责无需推断为产品通过。历史环境错误逐项登记合理。',CHECK),
(71,'X','未来链强门后来被同ID卡缩为纯计算器或结构验证，终局117accepted/terminal未保留部署pending子节点。CA306后又执行已被取代ZR110x，仍纯函数未补回原门。',CHECK+'; '+CARD+'ZR-1104/00_wu_card.md')])
add(CA,'traceability_and_acceptance.md',[(1,'U','六问题、复用/下载/处理/broker矿业合同的每行测试与关闭证据是原始业务承诺，不能被单元ID同名代替。无授权discover/fetch/commit=0明确强于ZR旧段。',REV+'; '+FF),
(76,'X','原JourneyA紫金、B异构矿企、C非矿独立端到端；CA302实际C2/C3都复用紫金文档且不worker/download，reviewer明知仍accepted。',CARD+'CA-302/12_reviewer_receipt.json findings002/003'),
(98,'X','原24h/7d/35d自然审核及真实证据freshness，不由CA206注入时钟函数13tests或197passed摘要代替；当前按标签的scenario closure有纯反例。',CHECK)])
add(CA,'weak_model_execution_checklist.md',[(1,'U','五问/RED/禁行/固定步幅/独立review规则严谨，但原始需求与card语义等价没有可执行检查。RED取glob新test=0可证明没有测试文件，不能证明用户行为失败。',CARD+'CA-206/00_wu_card.md:11; '+CARD+'CA-302/00_wu_card.md:11'),
(83,'X','原不可用fixture替真tier、未满自然窗不能接终验、不得把部署留空；后卡明文排除真实动作但同IDaccepted。正确做法是mechanism_pass与business_pending分子节点。',CARD+'CA-206/00_wu_card.md:13; '+CARD+'CA-301/00_wu_card.md:13; '+CARD+'CA-304/00_wu_card.md:13'),
(132,'U','模板要求范围/样本/残余问题如实列；receipt确实披露部分卡外缺口，问题是聚合门没保留未完义务，而非所有实施者凭空捏造测试通过。',CARD+'CA-302/12_reviewer_receipt.json')])

add(ZR,'architecture_target.md',[(1,'U','所有公司/三仓单责/source-only、CatalogReader物理只读和request-root选择是有效目标；当前仍需实际用户入口调用链与环境配置联合验收，不能由类型或helper存在证明。',REV+'; '+FF),
(86,'U','RootPolicy配置泛化、source状态和request-specific ready需要共用运行快照；当前raw-ready≠review-ready，以及GP002生产adapter配置错配均揭示边界未闭合。','reviews/wiki/item_ledger.jsonl; '+REV),
(143,'U','ProcessingDemand必须持久队列交worker且公平/预算/恢复；DAG selector和本进程队列不等于执行producer。Broker doc/table/chunk/tag各层须独立原文oracle，非文件计数。',REV),
(176,'U','AssetFact/MineYearOperation/AccountingBridge要求事实与估计、资源/储量、所有权/控制、币种单位、payable与内部销售分别建模；当前矿业helper有限性/单位和会计证据缺口按117unit审查保留。',REV),
(207,'X','revenue原要求formal prepare/commit/recovery幂等。当前输出失败后registry已追加仍有反例；全局无授权不discover与ZRtask149仅discovery冲突，必须按后来CA强门明确覆盖而非隐含解释。','reviews/revenue/logs/probe_publication.*; task_plan.md:149; CA traceability_and_acceptance.md:32'),
(230,'S','渐进/N-1/rollback设计正确，旧路径不得只因新函数存在删除；此处不声明已执行。',REV)])
add(ZR,'dynamic_assurance_plan.md',[(1,'U','自始明确脚本存在≠机制运行，绝对零/趋势SLI均需实际入口计数；8/31后卡又将部署排除。后GP自然触发证据应单独保留，不抹掉真实后修。',CARD+'CA-202/00_wu_card.md; '+REV),
(56,'U','轮换样本/原子报告/告警release链要hash和独立oracle，current196scenario evidence只有文件+summary等6字段，无per-tier/source/triplet充分绑定。',CHECK),
(93,'X','36h/9d/35d旧release门和后CA24h/7d/35d应版本化；自然7/2/1+drill强门被CA206/ZR1104计算器范围替代，test-only接受不等于自然运行。',CARD+'CA-206/00_wu_card.md; '+CARD+'ZR-1104/00_wu_card.md')])
add(ZR,'findings.md',[(1,'H','001–013：并发/旧计划复用不继承PASS/紫金封存RED/三仓HEAD漂移/95场景不足/动态运行缺口是当时观察；当前hash固定支持追溯，不能认为后续未曾修复。',CHECK+'; '+REV),
(89,'H','014–021：writer读路径、retry上游分类、renderer须回放、旧契约/模型/调度/硬编码/索引新鲜度均明确应实测，不足凭词计数。当前对应实现判定由新独立unit账本和FFprobe，旧观察不直接变当前bug。',REV+'; '+FF),
(139,'S','022–028：隐私元数据不是出站证明，shadow无人读不等可复用，来源与事实/预测分层、canonical与request位置、producerattempt与artifact、exact与freshness正交均是合理边界；当前要以真实消费证据兑现。',REV),
(182,'S','029–030：记录HEAD再漂移并修正ADR先后/自依赖/自然窗表达属于计划改善，不能证明后来实现或两份计划阈值一致；8/13版本hash本次匹配。',CHECK)])
add(ZR,'implementation_runbook.md',[(1,'U','状态机比task_plan和CAregistry词汇更细（preflight/drift/red/owner/triplet等），缺显式映射；20步强门本来禁止缩范围，但card后来改了被锁内容后仍能accepted。',CARD+'CA-206/00_wu_card.md; CA completion_assurance_registry.md:11; task_plan.md:56'),
(87,'X','T0–T4互不替代与独立副作用ledger规范强；current READ10 映射artifact/journal unit test并不能证明deadline；197passed不能证明required tiers。',CHECK+'; ../company-wiki/tests/unit/test_zr304_read_model.py:1-297'),
(132,'U','停止/漂移/独立审查/声明模板说明应保留缺口；expected-failure一律禁行与后CA结构化expected_failure_pass存在规则版本差，需要明确哪层失败可成功，不能把MISSING正向旅程当复用。',CARD+'ZR-409/12_reviewer_receipt.json; CA authoritative_execution_plan.md:135')])
add(ZR,'legacy_plan_disposition.md',[(1,'S','旧资产可以保留而旧完成状态不得继承，pending/superseded/deferred范围清楚；旧投资wiki退休不再列当前恢复目标。旧Phase/FC/RF映射是登记资产，不是代码通过。',REV+'; reviews/wiki_legacy/review.md'),
(60,'S','取消/降级候选由授权及owner办理；本次不据candidate即视删除已完成，也不把旧目录terminal等于原业务通过。',CARD+'CA-306/00_wu_card.md')])
add(ZR,'migration_rollout_plan.md',[(1,'U','备份、容量、restore、golden/shadow、cohort/rollback等需真实执行且授权；卡级activation tmp往返不证明生产恢复和存量覆盖。',CARD+'CA-304/00_wu_card.md; '+REV),
(56,'U','legacyartifact分桶/不强绑正确，七broker语义和mine shadow必须每角色/每公司证明；9月GP真实补处理可支持局部role，不能自动升7/7全部语义。',REV+'; reviews/wiki/item_ledger.jsonl'),
(94,'U','逐波receipt包含副作用/SLO/rollback/hits，是所需证据；实际原始结果与生产candidate要校验，不能仅通过字段存在/summary。',CHECK)])
add(ZR,'PLAN_MANIFEST.md',[(1,'S','12文件/4继承来源hash、92ZR/102新场景及计划pending明确；本次26内容与30输入hashsize全对，支持冻结。编制完成不称产品完成。',CHECK),
(54,'D','这里首卡ZR001后来被CA统一入口CA001及冻结annex覆盖，属有意取代，不是现在两个合法入口。历史原文件保留可追溯。','CA PLAN_MANIFEST.md:70-79; CA task_plan.md:62-69')])
add(ZR,'plan_self_audit.md',[(1,'S','审的是计划无遗漏/顺序/防假绿，PA001ADR先后、PA002自依赖、PA003soak强门等修正真实留文；仅支持计划改进，不是产品验收。',CHECK),
(50,'U','列出防弱模型/虚假完成攻击/E2E真实性，但实施并无冻结原义务→卡语义差分门。后收据明知‘非真实公司文档’仍放行，说明设计检查没有在接受总状态时生效。',CARD+'CA-302/12_reviewer_receipt.json'),
(108,'S','仍需实施时冻结的迁移/阈值/矿企/时间决策明确未完成，最终完整性是计划完整。不得将这些开放决策自动降为已完成产品。',CHECK)])
add(ZR,'progress.md',[(1,'H','每条为计划编制/自审/文件统计，最终明确实施Phase0–11全部pending；保留当时哈希与HEAD，不能把文档进度当真实旅程。',CHECK)])
add(ZR,'scenario_matrix.md',[(1,'U','95旧+102新197唯一ID成立且计划明言tier不能替代。当前一个status/tier字符串并未实现scenario×tier结果，closure纯函数只看label。',CHECK),
(39,'X','READ01–12需真只读/lock/deadline/预算/SLO；READ10当前证据错指artifact read model测试，当前FF预算10→14秒反例说明该义务仍未受有效门保护。',CHECK+'; '+FF),
(56,'U','BR每项是publisher/身份/多实体/版面/表格单位脚注/隐私/7真实PDF两个标注者等独立义务；10个metadata合同测试不能当全部T1/T2语义过关。',CHECK+'; '+REV),
(87,'U','MINE01–24覆盖资源/储量/LCE/控制权/归属/单位/商业条款/内部交易/披露桥，须各经济oracle。纯helper及same-formula fixture不能证明原文事实和公司会计。',REV),
(116,'U','REV与ZJ涵盖validate/draft/formal/replay/mine/backtest以及existing/partial/missing/stale/amended，当前197摘要把ZJ01T2指向合成Zijin9tests，非所承诺真实闭环。',CHECK+'; '+CARD+'CA-302/12_reviewer_receipt.json'),
(158,'U','AUD2自证缺任务/跳过/陈旧/错误candidate、真实golden版权边界和单场景run/hash/oracle要求均不可由marker或test_file替代。缺fixture/oracle的197passed证据不足。',CHECK)])
add(ZR,'task_plan.md',[(1,'S','编制P0–P2 completed与产品Phase0–11 pending清楚；三仓边界/最终成功定义是规范。计划未改代码声明不等产品未曾改。',CHECK),
(54,'U','状态pending→in_progress→implemented→independently_verified→accepted比runbook细状态不一致；Phase0–3强制真实RED、只读、语义状态/绑定，当前需按CA/ZR逐项证据，不能用链条标签。',REV),
(136,'U','Phase4有‘无授权仅discovery’，architecture全局不discover、后CA三类动作0冲突需显式裁决；根复用/download/index链实测失败须保留独立原因不全归provider网络。',FF+'; architecture_target.md:217-229; CA traceability_and_acceptance.md:32'),
(154,'U','Phase5–7将broker/web/worker、矿山事实单位会计、输入/发布/回测分别要求；实现局部有效但不能用同紫金引擎替第二公司/真实来源。',REV),
(208,'X','Phase8–11真实E2E/自然审核/迁移/终验不能由8/31一下午test-only卡全部accepted来满足；后继ZR1104同样排除自然累积，未补强CA门。',CARD+'CA-206/00_wu_card.md; '+CARD+'ZR-1104/00_wu_card.md'),
(273,'D','旧独立ZR001入口已被统一CA计划覆盖；交付导航与错误记录是版本历史，不应删改为看似一直一致。','CA authoritative_execution_plan.md:7-19')])
add(ZR,'traceability_matrix.md',[(1,'U','每个目标/缺陷/单元/测试/证据映射保留，映射完整不等行为通过；71/95/117/197均不能替代消费者真实结果。所有原行进入occurrence账本，不按标签继承。',REV+'; '+CHECK),
(58,'U','known-defect closure条目含renderer、publisher、side effects、mines等；相应当前受控反例与后修分别保留，不能笼统宣称全部解决或全部仍坏。',REV+'; '+FF),
(79,'X','原closure任何未满足必须阻断；CA305六问test实际只查accepted/路径/长度，未匹配实际公司结果。','tests/test_ca305_six_problems.py:98-211')])
add(ZR,'work_unit_registry.md',[(1,'U','92ZR逐ID注册和依赖关系完整；本分区全文重读规格，117unit更细当前判断在revenue独立ledger，不复制其PASS。原义务分别保留，不跨版本合并结论。',REV),
(24,'X','ZR201–206读模型/统一错误/deadline/SLO承诺中，ZR205当前首调用模拟耗9秒抛busy后仍用旧remaining允许5秒退避，预算10模拟clock到14再报超时；READ10现映射不验此行为。',FF+'; '+CHECK),
(35,'U','ZR301–510原source状态→consumer ready、artifact/queue、root/download、broker/html/worker非单metadata合同；当前按入口证据仍有scan/ready/reuse闭环缺口。',REV+'; reviews/wiki/item_ledger.jsonl'),
(76,'U','ZR601–713矿山事实/经济/会计/未来actual/发布原义务不因helper通过消失；本次独立读ZR713卡明确三层WAPE，peer当前观察mine-volume只求actual总量无预测误差。',CARD+'ZR-713/00_wu_card.md:16-18; '+REV),
(110,'X','ZR801–1105真实E2E、自然审核、迁移与终验被CA强卡吸收后实际再走弱ZR110x；状态全accepted缺部署子义务，不支持总体完成。',CHECK+'; '+CARD+'ZR-1104/00_wu_card.md'),
(157,'S','依赖主链为编排规范，能防任务顺序乱跑但不能证明消费者行为；保留该设计、补原义务与卡范围强一致门。',REV)])

def main():
    rows=[];struct=[];coverage=[]
    for prefix in (CA,ZR):
        for p in sorted((ROOT/prefix).glob('*.md')):
            rel=p.relative_to(ROOT).as_posix();lines=p.read_text(encoding='utf-8').splitlines();cases=[c for c in CASES if c['source_file']==rel]
            seen=[];digest=hashlib.sha256(p.read_bytes()).hexdigest()
            for n,s in enumerate(lines,1):
                if not s.strip():continue
                matched=[c for c in cases if c['start']<=n<=c['end']];assert len(matched)==1,(rel,n)
                c=matched[0];seen.append(n)
                if s.lstrip().startswith('#') or re.fullmatch(r'\s*\|[\s|:\-]+\|\s*',s) or s.strip() in ('```','```text','```json','---'):
                    struct.append(dict(source_file=rel,source_line=n,source_text=s,reason='heading/table divider/code fence; context read, no standalone claim',case_id=c['case_id']));continue
                ids=sorted(set(re.findall(r'\b(?:CA|ZR|FC)-\d{3,4}\b',s)))
                rows.append(dict(item_id=f"{c['case_id']}:L{n:04}",case_id=c['case_id'],source_file=rel,source_line=n,source_sha256=digest,source_text=s,historical_status='original dated plan/audit; source text retained verbatim',conclusion=c['conclusion'],review_mode='full_text_manual_semantic_interval_original_occurrence',reason=c['reason'],current_evidence=c['evidence'],unit_ids=ids,recommendation='原规格与后继卡拆为可追溯行为义务；机制/部署/自然观察/业务验收各自保留状态，不继承PASS。'))
            expected=[i for i,s in enumerate(lines,1) if s.strip()]
            coverage.append(dict(source_file=rel,sha256=digest,lines=len(lines),nonblank=len(expected),semantic_occurrences=sum(r['source_file']==rel for r in rows),structural_context=sum(r['source_file']==rel for r in struct),manual_cases=len(cases),pending=sorted(set(expected)-set(seen)),extra=sorted(set(seen)-set(expected))))
    assert len(coverage)==28
    assert not any(c['pending'] or c['extra'] for c in coverage)
    (OUT/'manual_cases.json').write_text(json.dumps(CASES,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'item_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    (OUT/'structural_exclusions.json').write_text(json.dumps(struct,ensure_ascii=False,indent=2),encoding='utf-8')
    result=dict(files=coverage,totals=dict(files=len(coverage),lines=sum(c['lines'] for c in coverage),nonblank=sum(c['nonblank'] for c in coverage),semantic_occurrences=len(rows),structural_context=len(struct),manual_cases=len(CASES),pending=0,extra=0),conclusions=dict(collections.Counter(r['conclusion'] for r in rows)),limitations='原文occurrence不等bug数；H是已复核的历史范围，不认证旧遥测数字。原CA/ZR逐ID与本报告互补，不继承它们历史PASS；未重跑真实生产/下载/worker。')
    (OUT/'coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['item_id','case_id','source_file','source_line','conclusion','reason','current_evidence','source_text'],extrasaction='ignore');w.writeheader();w.writerows(rows)
    print(json.dumps(result['totals'],ensure_ascii=False));print(result['conclusions'])
if __name__=='__main__':main()
