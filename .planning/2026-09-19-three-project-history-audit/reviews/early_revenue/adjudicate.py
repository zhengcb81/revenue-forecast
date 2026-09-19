"""Lead review of six completely read early planning bodies.

Manual section judgments, not completion inferred from keywords. Every nonblank
source line is retained so receipt fields and repeated statements remain visible.
These are occurrence records, not counts of independent bugs or passed tests.
"""
from pathlib import Path
import hashlib, json, re, collections
HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1]
ROOT = PLAN.parents[1]
FILES = ['findings.md','progress.md','audit_review/findings.md','audit_review/progress.md',
         'audit_review/2026-08-08_adversarial_plan/findings.md',
         'audit_review/2026-08-08_adversarial_plan/progress.md']
CASES=[]
def case(file, start, end, verdict, target, reason, evidence, action):
    CASES.append(dict(case_id=f'ER-{len(CASES)+1:03}', file=file, start=start,end=end,
        verdict=verdict,target=target,reason=reason,evidence=evidence,action=action))
RF='reviews/revenue/item_ledger.jsonl; reviews/revenue/checklist_ledger.jsonl; reviews/revenue/model_ledger.jsonl'
FF='reviews/filing/review.md; reviews/filing/item_ledger.jsonl'
WK='reviews/wiki/item_ledger.jsonl; reviews/wiki_legacy'
REAL='audit_review/2026-09-18_real_company_skill_audit/AUDIT_REPORT.md'
for f in FILES:
    case(f,1,100000,'historical_only','历史过程、命令、数量、局部修复及后继引用',
        '已完整阅读。记录的时间点、套件、角色和写入边界均保留；历史测试数/accepted本身不能证明当前生产或收入预测准确性。原问题的当前适用性逐项转入独立项目账本；未重跑旧版本环境不伪称原数字得到本轮复算。',
        RF+'; '+FF+'; '+WK,'以原要求与现验收差集处理，不执行旧日志命令，不复活退休路线，不把执行过程字段计为独立缺陷。')
case('findings.md',27,143,'superseded','早期filing所有权与复用初判',
     '本节自己撤回ensure必定下载的初判：上游会先resolve。旧实现/安装状态后来变化，当前已有280项隔离回归及34文件三安装副本匹配，不能重复报告已删除owner仍双活。',FF,'保留reuse-first和上游边界；用真实入口验证而非只看client是否直接调用ensure。')
case('findings.md',144,424,'historical_only','旧23模型、schema、workflow、输入输出与跨技能基线',
     '逐条读过模型/来源/管理目标/置信度/敏感性/回测/安装观察。当前31模型已有97测试+216subtests的隔离复验，不能继承旧23模型状态；结构与单位正确不构成经济真实性。',RF,'逐模型适用边界、参数来源、确认时点、生命周期和真实origin误差分开验收。')
case('findings.md',425,445,'supported_scoped','基线按日期漂移被如实发现',
     '正文从158全绿纠正为2错误并解释as_of与capture日期；这是旧固定日期fixture问题，不能和9/18同名canonical错误（缺adapter）混同。',REAL,'每个错误保留底层原因、日期、配置和阶段，不只按错误名字聚合。')
case('findings.md',447,475,'insufficient_evidence','将未实现项归为过度工程/可选',
     '9.5/9.6/10被缩减后仍汇总全部13Phase完成；是否必要可以重新决策，但不能单靠实现者评价抹去原验收义务。后继长期缺授权/接线说明领域要求仍需单独闭合。','progress.md:309–347,396–420; '+RF,'原义务与被批准的范围变化分别记录；取消或替代不等于实现通过。')
case('findings.md',478,544,'insufficient_evidence','恒运昌25次输入构建与21验证函数覆盖完整',
     '从一次公司实战推断全部validator逻辑正确没有充分证据；其后F02反例直接否定无条件外推。direct_growth置信度60.6不是准确率，23次schema错误反映构建摩擦。','findings.md:1126–1139; '+RF,'生成输入前校验单位/枚举/来源并保留适配成本；准确性用冻结预测与实际值评估。')
case('findings.md',545,678,'historical_only','紫金占位、双市场身份、锁、磁盘、URL、编码',
     '多个不同原因先后阻塞同请求，不应合并成下载器失效。7/31成功获取FY2025是实际局部成果；后来已存在文档复用仍成功，但当前新下载注册链另有配置缺口。',REAL+'; '+FF+'; '+WK,'保留每段完整错误信封和资产状态；不足元数据、确证冲突、上游403分别处理。')
case('findings.md',679,742,'historical_only','MongoDB实战和旧worker覆盖治理',
     '旧worker仍加载旧代码使已退役文档复活的历史链证据充分作为根因解释；不能说当前paused worker正在复活。本节财务数字为历史研究记录，本轮没有重新作公司预测。','progress.md:790–924; '+WK,'部署验收绑定实际加载模块/配置指纹；资料不够不通过拼接公司名补URL。')
case('findings.md',743,854,'historical_only','阿里巴巴A1–A17事实、经济逻辑与修复',
     '未读来源、自报工具、GMV由CMR/take-rate构造循环、敏感性早年冲击不传播等均独立识别；后继17.9补claims/v3不可变有实际修复记录。缺抽取/约束的原缺陷不应机械算作当前仍在。','progress.md:970–1223; '+RF,'经济假设需独立driver证据及反证；数字claim存在和hash匹配不足以证明经济因果。')
case('findings.md',855,964,'historical_only','Alphabet双类股、断言取代及工作流反思',
     'GOOG/GOOGL归一后来有真实同hash零下载验证；local_document应急交付只支持预测步骤，不自动证明filing修好。基于搜索摘要数字的不可靠性和每公司手写builder成本仍是验收设计问题。','progress.md:1229–1690; '+REAL,'保留发行人/证券/市场三层身份与可观测复用；适配信息不足时明确拒绝，不能靠重复尝试冲过。')
case('findings.md',1108,1139,'superseded','早期F01/F02发布顺序与无输入弱验证',
     '当前先validate_published_forecast再receipt、嵌入input并强dispatcher，独立代理37回归及源读确认；承认后继修复，旧反例不能直接判定现状。','reviews/revenue/logs/publication_*; progress.md:1851–1870','保留历史因果，另验整组输出/registry事务和签名声明，不用修复F01代表所有发布义务通过。')
case('findings.md',1344,1357,'supported_scoped','原F11对trusted host能力的质疑及后继边界',
     '原F11质疑仍有新当前反例：普通文件路径被attestation_capability当provider能力，结果host_signed却无signature且validator接受。真实Ed25519验签在存在签名时有效，不能泛称完全无签名保护。','reviews/revenue/logs/publication_*; reviews/revenue/probe_publication.py','host_signed必须绑定真实可信签名与被签载荷；未取得证明保留draft/不可信状态。')
case('findings.md',1432,1434,'superseded','CodeGraph未初始化的末尾残留',
     '前文1423–1430已经说明初始化，末尾旧待确认不是当前工具不可用证据。','findings.md:1423–1434; 当前工具发现CodeGraph可用','历史残留显式按日期化解，不改旧文件伪造一致。')
case('progress.md',164,215,'insufficient_evidence','Phase2全部满足与真实两阶段签发',
     '当时测试receipt形状/结果字段并不证明真实调用顺序；8/3F01已证伪该外推，8/4后继再修复。本轮应区分三个时点。','findings.md:1108–1139; progress.md:1851–1870; '+RF,'固定真实consumer API作为验收口，不只测内部helper。')
case('progress.md',216,257,'contradicted','修改RED的入参后声明弱验证全部修好',
     '233行把validate_forecast_output(forged)改为(forged,data)，而输出独立消费者仍调用无input路径；8/3复现证明原攻击面未被同一测试保留。后继已修不能抹掉这是漏检原因。','findings.md:1126–1139; progress.md:233; reviews/revenue/logs/publication_*','原失败调用/业务义务保持不变；修复后增测新接口同时保留旧consumer反例。')
case('progress.md',309,347,'insufficient_evidence','13阶段全完成与残余、coverage总数',
     '同节承认目标未实现或为可选、coverage82低于84，却用全完成汇总，缺原范围变更与实现证明的分栏。','findings.md:447–475; '+RF,'汇总状态不得覆盖子条款与目标阈值；局部通过标明范围。')
case('progress.md',396,420,'contradicted','标题状态权威替代逐条义务',
     '417明确阶段级状态权威，未更新全部checkbox且7.2未做；选择少数函数存在/绿测便标题completed，不足以关闭剩余原要求。',RF,'可记录历史状态漂移，但新的完成判断逐原义务证据落地，不以标题相互证明。')
case('progress.md',488,537,'historical_only','磁盘备份治理与收敛尚未完成',
     '正文明确有证据待回填、worker_state未收敛；不能把若干勾选代表整个备份恢复已验。此处不重新删除/备份生产库。',WK,'未来运行恢复另验容量、精确备份覆盖及真实恢复；持续观察未跑记未跑。')
case('progress.md',701,770,'insufficient_evidence','三市场/任意公司外推',
     '3家公司2成功1HK失败是部分真实证据；末尾any-company语义不由这个样本成立，metadata旧缺口与9/18扫描不兼容也不是同一问题。',REAL+'; '+WK,'每市场×已有/缺失×二次复用按实际结果单列。')
case('progress.md',790,924,'historical_only','URL、restore和worker版本管理修复',
     '多项真实修复存在，但dropbox被排除在company_raw复用范围，且跨公司名URL后继F052/054指出错误绑定。局部测试绿不是三root可用。','audit_review/2026-08-08_adversarial_plan/findings.md:496–527; '+WK,'文档身份和hash绑定每个provenance；配置和运行加载版本一同验收。')
case('progress.md',970,1223,'supported_scoped','17.3/17.9事实与敏感性lint及后继更正',
     '记录承认启发式识别6条非3条、单位假阳性、遗漏日期等边界；后继6claims/v3反映实际纠正，不应继续当全部未修。支持范围是所列输入和lint，不是所有结论真实性。',RF+'; findings.md:743–854','工具警告与事实来源人工复核并行；敏感性全路径按参数传导验收，不只改到终年非零。')
case('progress.md',1502,1651,'historical_only','免打扰子集、部署与回归限制',
     '6/7明确延期本身诚实；后续Phase18主体修复与WR10.15故障独立。不能把临时环境解释当最终根因。',WK+'; progress.md:1668–1690','归因需要最小复现，保留原始错误与实际加载版本。')
case('progress.md',1652,1667,'supported_scoped','GOOG与GOOGL真实复用验收',
     '这是有证券/期间/同hash的真实只读局部证据，应承认，不等于所有未来US新文档注册成功。',REAL+'; progress.md:1652–1667','固定该回归，新增当前原件首次注册和二次复用链。')
case('progress.md',1668,1691,'supported_scoped','撤回spawn环境误判并修真实回归',
     '正文明确pickle local closure、UTF8和错误Pool探针分别处理，反驳此前harness先验解释；1621通过仅支持修后套件。',WK,'失败归因先证伪测试/产品两侧，再判环境，不用standalone绿排除并发真缺陷。')
case('progress.md',1851,1870,'supported_scoped','8/4后继修复的有限承认',
     '当前代理确认F01验证顺序/F02输入绑定已修；F11host_signed和ZR710多输出事务有新反例，所以本段不能外推整个发布可信链完成。','reviews/revenue/logs/publication_*; '+RF,'保留修复成果，新的签名/输出失败反例单列，不重复整套重写。')
case('audit_review/findings.md',474,595,'historical_only','ZR204–806 closure逐条补记',
     '所有补记均完整读；每个ZR原义务与实际card/测试独立复查在262unit账本。三root旅程包含Dropbox MISSING正确负例，不能作外部root-only正例；ZR409生产loader延期、ZR710事务范围、ZR709fixture必须保留限制。',RF+'; '+REAL,'从每张原卡对到真实入口；test-only、fixture、doc-only、production分开，延期后继未做不算当前闭合。')
case('audit_review/progress.md',75,270,'historical_only','ZR204–806执行回执与阶段汇总',
     '完整读每项命令/数量/结果/复核/流程偏差；json hash修复、联合closure、单跑竞态不是原始全目标证据。对应当前单元结论独立落账，不由accepted83/117推得生产能力。',RF+'; '+REAL,'保留receipt原字节与实际rc，引用者校验含义和后继，不手写伪commit。')
AF=FILES[4]; AP=FILES[5]
case(AF,10,19,'superseded','config-only初判',
     '本文件F034后文动态探针自己否定“配置即充分”；config支持kind只证明表达候选权限，不证明metadata进入resolver。',AF+':269–277,398–404','按最终更正引用；目前另有v2flag×adapter配置反例。')
case(AF,72,229,'historical_only','F008–028 roots、衍生物、生产catalog和组合E2E',
     '早期空白后已有SQL下推/SourceBundle/状态过滤等成果，仍需当前调用链验收。49GB及各计数仅属8/8抽样；第4周持续门没有足够时间不能靠完成标题通过。',WK+'; '+RF+'; '+REAL,'逐原痛点映射当前消费者与生产配置，保留后继修复；不重复报告旧全表查询必然仍用。')
case(AF,231,267,'superseded','F029–033 CI/11重复测试/静态质量',
     '后继WU1.1/1.2实际清理并补唯一性门，有原始记录；旧185ruff和11重复数量不得直接当当前现状。新的当前CI/receipt漏洞另按独立证据判定。',AP+':770–840; '+RF,'部署/CI真实运行独立于本地修复；测试数与收集/跳过/失败分栏。')
case(AF,269,292,'supported_scoped','F034自我纠正与语义摄取边界',
     'config-only被真实resolver反例证伪，区分物理内容寻址与语义可消费是有效分析；但当前版本已新增adapter能力，不能照旧断言代码中没有adapter。',WK+'; '+REAL,'将问题具体化为当前生产哪些roots无adapter、何种flag激活路径，而非泛化全系统硬编码。')
case(AF,305,370,'historical_only','旧问题/场景/风险矩阵逐行',
     '矩阵中P-Dropbox仍写配置方案已证明，与同文F034更正冲突；其余行按原日期和后继WU/ZR重审，不能把30/37场景行数当真实旅程完成。',RF+'; '+FF+'; '+WK,'引用文件+行而非重复F-ID；矩阵对每当前路径和限制有独立结论。')
case(AF,371,486,'historical_only','F037–050目录语义与权限分层',
     '全段读过。root物理索引≠active身份provenance合格，旧retired/docling/mixed分类统计属于当时。当前缺adapter导致新file_seen0是后继配置集成问题，历史关键词分类失败不是其直接原因。',WK+'; '+REAL,'修复规范化和配置能力一致性；外部目录只读与唯一canonical writer边界保留。')
case(AF,487,518,'historical_only','F051接线孤岛/F052–054公司名URL错误绑定',
     'WU5.x纯函数绿后仍无生产调用的后继证据解释当时失效；目前source_preparation等接线已存在却在not_reviewed之前停/入队为0，应重新按当前阶段判断。',RF+'; '+REAL,'新增调用者验收以及缺资料后的实际可执行修复路径，不只查函数存在。')
case(AF,520,597,'supported_scoped','F055–060边界和架构裁决适用范围',
     '保留退役不自动复活、唯一writer和身份来源门；物理湖有价值的判断合理。8/9config-only不可能只属于旧profile，不能否认后来adapter实现；gap根无关不代表当前修订排序/期间/hash算法正确。','reviews/cross_history/current_recheck.json; '+WK,'按当前四个gap反例补语义验收；来源合规与可检索/可证实分层。')
case(AP,15,74,'insufficient_evidence','WU10.1/10.2独立全链与closure90/88条',
     '回执内部90cleared/5partial又88cleared/7partial冲突；独立验收真实canary只ls/SELECT，selector spy不证明产品全链。明确保留F034和下载未运行应尊重，不能把accepted外推全部目标。',AP+':35,42,53–69; '+RF,'有限accepted保留，另验真实入口/外部唯一root/首次下载/二次复用。')
case(AP,75,127,'historical_only','WU9迁移armed状态',
     '生产完整scan未满，armed而非complete的写法正确；当前不能从当时代码门/祖先commit给生产授权。',WK,'版本、配置、切换策略、实际扫描结果分别取证。')
case(AP,129,217,'insufficient_evidence','WU7.1/8.3声明校验与WU6.2场景统计',
     'verifier按正则只证明受覆盖格式；filing代理当前probe仍漏Phase4/全局证据。37覆盖分母中known-gap/Windowsskip/机制替代同时记绿，34/37与列出的条件也不够清楚。',FF+'; '+RF,'验收结果按scope报告，不能把全部文档完成依赖正则绿。')
case(AP,219,504,'historical_only','WU5.x–6.2 helper与递延接线',
     '每个receipt字段均读：5.4消费接线推WU6；6.2直接selector的spy抛异常证明被测helper边界，未证明真实用户链会用它。4个新增门和已修hash/supersession应承认；下游消费者证据另找。',AF+':487–494; '+RF+'; '+REAL,'组件通过与组合旅程通过分别记账，后继任务必须回到原用户结果。')
case(AP,508,600,'historical_only','WU4授权/GapPlan/LatestPolicy',
     'authority缺省fetch/caps和expiry委托边界当时多项defer，latest防早退已有实际修复。当前不能沿用8例证明所有修订/期间，独立root4反例仍在。','reviews/cross_history/current_recheck.json; '+FF,'新旧版本/期间选择以provider语义日期，授权hash绑定所有影响动作的字段。')
case(AP,603,698,'supported_scoped','WU3状态过滤/SQL/确定性反例修复',
     '记录实质独立发现：insert_order没用、cap吞旧年度、SLO从2秒回500ms、.rejections负例被前门遮蔽，后继给出改正。范围是所列受测机制，不可据此声称当前生产所有roots已通。',WK+'; '+RF,'保持独立oracle和扰动真实进入调用路径；避免测试数据循环自证。')
case(AP,700,769,'supported_scoped','用户决定配置加负例验收',
     '原文706/724明确用户当时只做配置记录缺口，不声称production reuse。应承认这一限定通过，不能描述为未授权缩水；768旧不得转绿与后继授权需按时间理解。',AF+':269–277; '+RF,'把configuration_enabled与production_reuse_verified两字段继续区分。')
case(AP,770,915,'historical_only','WU0/1基线工具、重复测试清理与实际套件',
     '各回执有真实改错与限制：恢复mutation误用checkout丢未提交变更后重建；连续suite出现不同竞态，standalone绿不能永久豁免。baseline hash/行数仅当时观测。',WK+'; '+RF,'本轮仅scratch反例不改产品；运行零写包括DB/WAL/SHM且不伪称所有历史数字复算。')
case(AP,916,992,'supported_scoped','8/8–9调查自纠正和限定结论',
     '完整读取可见从config-only推论到动态否定、再查retirement与调用者的纠正；非产品实施。旧时点硬编码/根规模不自动沿用现状。',AF+'; '+WK,'保留自纠正链作教训；未来必须对实际配置执行完整成功与失败两类旅程。')

rows=[]; coverage=[]
for f in FILES:
    p=ROOT/f; raw=p.read_bytes(); lines=raw.decode('utf-8-sig').splitlines()
    digest=hashlib.sha256(raw).hexdigest(); heading=''; nrows=0
    for n,line in enumerate(lines,1):
        if not line.strip(): continue
        if re.match(r'^#{1,6}\s',line): heading=line
        matching=[c for c in CASES if c['file']==f and c['start']<=n<=c['end']]
        c=matching[-1]; ids=re.findall(r'\b(?:CA|ZR|FC|WU)-\d+(?:\.\d+)?(?:-\w+)?',line)
        rows.append(dict(occurrence_id=f'ERL-{len(rows)+1:05}',source_file=str(p),relative=f,
            line_start=n,line_end=n,file_sha256=digest,original_text=line,heading=heading,
            historical_markers=re.findall(r'accepted|completed|PASS|GREEN|pending|blocked|\[x\]|\[ \]',line,re.I),
            referenced_original_ids=ids,manual_case_id=c['case_id'],verdict=c['verdict'],
            assessment_target=c['target'],rationale=c['reason'],evidence=c['evidence'],remedy=c['action'],
            read_status='fully_read',reviewer='root',review_scope='historical statement and evidence sufficiency, not automatic current product certification'))
        nrows+=1
    coverage.append(dict(file=f,sha256=digest,lines=len(lines),nonblank_occurrences=nrows,read_status='fully_read',
        method='Complete source read; audit_review common text also mapped to already-read root documents by exact splitlines after heading-depth normalization; novel ranges read separately',semantic_cases=[c['case_id'] for c in CASES if c['file']==f]))
(HERE/'manual_cases.json').write_text(json.dumps(CASES,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'item_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
(HERE/'coverage.json').write_text(json.dumps(dict(files=coverage,summary=dict(files=len(FILES),original_lines=sum(x['lines'] for x in coverage),occurrences=len(rows),manual_cases=len(CASES),pending=0,verdict_occurrences=dict(collections.Counter(r['verdict'] for r in rows)),warning='Occurrence/section review counts are not independent bugs, passed tests, or a certification of every historical command.')),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(files=len(FILES),lines=sum(x['lines'] for x in coverage),occurrences=len(rows),manual_cases=len(CASES)),ensure_ascii=False))
