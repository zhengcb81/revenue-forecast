"""Manually selected historical assertions, paired with their real acceptance boundary.

No verdict is inferred from a keyword, PASS label or a read counter. Anchors only
locate source occurrences of the reviewer-authored assertions below.
"""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[3]
CASES=[]
def add(i,file,anchor,claim,conclusion,reason,evidence):
    p=ROOT/file; lines=p.read_text(encoding='utf-8-sig').splitlines()
    ns=[n for n,l in enumerate(lines,1) if anchor in l]
    assert ns,(i,file,anchor)
    CASES.append(dict(item_id=i,source_file=file,source_lines=ns,anchor=anchor,source_file_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),original_claim=claim,conclusion=conclusion,reason=reason,current_evidence=evidence,review_method='Source text read in full; this is a manually specified obligation, not automatic PASS extraction.'))

R='task_plan.md'
add('RF-P001',R,'标记为 completed 但未执行全部子项','Completed 可包含未执行的原验收项','contradicted','该句明确承认完成定义变动；拆项不一定无效，但缺口必须保留在独立后继总门，不能在汇总中消失。','task_plan.md:1623-1639; root early_history ledger; item_ledger CA107/CA305')
add('RF-P002',R,'host-signed receipt 为 infra 边界','原 Phase8 宿主验证成为 Phase外基础设施','contradicted','原649/666/687/688要求无verifier只能draft；1612移出scope后仍completed。2649仅host_receipt存在仍不等于可信执行。后继存在真实签名库但当前provider能力门可伪装。','deep_clause_ledger RF-F11-CURRENT; logs/publication_probe.stdout.txt')
add('RF-P003',R,'gap/authorization receipt |','结构化授权判为过度工程','superseded','当时boolean最小授权决定是明确记录；后续filing协议再强化。不可把旧boolean直接报为今日缺陷，也不能称已满足最初request/gap/expiry/issuer绑定。','reviews/filing/item_ledger.jsonl; task_plan.md:946-997')
add('RF-P004',R,'company-wiki atomic 命令','薄客户端两跳替代原单命令','superseded','需求被重新解释为thin boundary。当前原子identify/resolve和上游版本应由filing现行ledger核定；两种架构都需同一request的身份/时间一致性证据。','reviews/filing; item_ledger ZR201-206')
add('RF-P005',R,'_build_forecast_draft(data)','Draft→strong verification→receipt','supported_scoped','当前确先强验证，旧F01修复有效；input绑定亦有当前dispatcher。不能因后续事务失败否认这个顺序修复。','deep_clause_ledger RF-F01-CURRENT/RF-F02-CURRENT; logs/publication_tests.*')
add('RF-P006',R,'所有改动都有失败测试','每个行为修复须目标RED','insufficient_evidence','许多后期RED只是新测试文件glob不存在，不能证明产品反例先失败。历史命令摘要缺完整原始输出时无法补认证当时RED原因。','session progress; 194 card/RED source mappings')
add('RF-P007',R,'production calculator 与 validator','公式共用但独立输入重算','supported_scoped','复算从冻结input取值防输出字段自证有用；同公式保证内部一致，不能独立发现同一经济定义/单位/会计错误。需财务原文或第二种经济恒等式oracle。','model_ledger.jsonl; deep_clause_ledger RF-F02-CURRENT')
add('RF-P008',R,'formal mode 不得由 renderer','Formal 发布硬门','insufficient_evidence','发布mode、业务真实性、原子输出和登记一致性是独立义务；当前签名能力和输出失败孤儿两个反例，不把 renderer 本身无证认定有漏洞。','deep_clause_ledger RF-F11-CURRENT/RF-ZR710-TXN')
add('RF-P009',R,'每次 subprocess 只拿 remaining time','全流程 deadline','contradicted','当前纯隔离模拟clock证明调用9秒后旧remaining允许sleep5，10秒预算到14；不是第二次subprocess或实际墙钟14秒。','reviews/filing/pure_probes.py:16-25; reviews/filing/tests/pure_probes.json')
add('RF-P010',R,'无 trusted verifier 的环境只能输出 missing/gap','无可信授权不能下载','insufficient_evidence','此次不运行下载；需filing当前签名/issuer/request/gap/expiry逐场景结果，不能由字段存在代替外部用户授权真实性。','reviews/filing; item_ledger ZR204/FC804')
add('RF-P011',R,'无第二 owner','单一下载所有权','supported_scoped','早期仅封CLI仍有库owner是历史真缺口，R3后删除原owner是实质修复。有限AST检查只保证已覆盖调用形状，跨技能实际入口还需图/跟踪。','review_audit/findings N03; review_audit/progress R3; current filing client route')
add('RF-P012',R,'剩余子模块因 revenue_core','模块拆分已完成但循环阻止继续','superseded','该借口当时不满足原11模块标准；8/8R9真正468行拆分和5类golden是后继修复，不能再报现有空壳。golden保持旧行为不证明旧行为金融正确。','IMPLEMENTATION_PLAN.md R9; model_ledger.jsonl')
add('RF-P013',R,'新公司输入构建时间','2小时→15分钟与20–25轮→2–4轮','insufficient_evidence','这是影响预估，不是已测改善。需要同复杂度多公司、相同信息预算/助手环境的实际构建日志与失败分类。','task_plan.md:1698-1702; docs buy-side reviews; latest0/3 real audit')
add('RF-P014',R,'默认关闭（不改变现有默认行为','无源数字预检','supported_scoped','启发式有价值但默认off且仅数字+引用存在，不能证明文本语义已从原文核实。符合当时工具提示scope，不满足自动防所有无源结论的更大目标。','scripts/lint_input.py; task_plan.md Phase17')
add('RF-P015',R,'17.9 B 闭环','5条未摘录数字后续补到0','superseded','末尾v3补6条claim的历史修正必须保留，不能把早期5未修当今日现状。0lint只是该启发式未命中；原文真实性及资料完备仍需独立source审查。','task_plan.md:2204/2216; root early_history ledger')
add('RF-P016',R,'以 A11 事实还原构造实证','敏感性旧样本丢失后复原','supported_scoped','诚实说明原初磁盘input缺失，重构场景支持机制演示而非原字节回放；后续必须保留immutable实际输入和trace。','task_plan.md:2198; docs/session-checklist.md')
add('RF-P017',R,'18.3 用户裁定跳过','已授权跳过scanner补全','not_applicable','明确用户范围裁定应尊重，不能指责未实现是擅自造绿。仍应把需要重扫补全的原能力列未覆盖，不能借Phasecompleted认定其存在。','task_plan.md:2182/2284; history_wiki/root successors')
add('RF-P018',R,'17 阿里巴巴会话审查整改','Phase17时期状态','insufficient_evidence','同文件有pending、completed与后记，必须按日期/修订恢复最终结论，不能依单词首次或最后一次出现自动判状态。','task_plan.md:2181/2212/2216; source line occurrence ledger')
add('RF-P019',R,'revenue_forecast.py` 由 0%→81%','分模块90%承诺与81%完成','contradicted','原新增模块≥90%，后继总85和CLI81即completed；coverage口径变化需显式接受和未达标项，不能由总指标掩盖关键边界。','task_plan.md:2603/2655; root early_history')
add('RF-P020',R,'PermissionError 加 3s 重试','50次stress/确定teardown→3秒重试一次全绿','insufficient_evidence','1629pass支持该次套件，不能证明50次stress/三轮全量无残留。后继workerv5计划不等于部署；独立agent审当前worker证据。','task_plan.md:2617-2618/2657; reviews/audit_independent')
add('RF-P021',R,'acquisition_mode`/`authorization_requested','授权receipt→两个说明字段','contradicted','D1原要求可校验download authorization/journal引用，最终两个字段+2test支持说明字段存在，不能独立鉴别授权scope/issuer。','task_plan.md:2629/2659; reviews/filing current ledger')
add('RF-P022',R,'所有消费者使用同一 schema','invest/industry等消费契约','insufficient_evidence','本轮没有全invest各仓current revision运行，保留明确边界；旧36/22/41总数不能证明今日全部DAG接受/拒绝所有新schema。','checklist_ledger root-invest; legacy ledger downstream obligations')

A8='audit_review/2026-08-08_adversarial_plan/task_plan.md'
add('RF-P023',A8,'双层状态','configuration_enabled不等于production_reuse_verified','supported_scoped','这一分层是正确旧约束，真实Dropbox0eligible正例只能证拒绝安全；用户授权negative-only允许完成配置包，但总用户复用目标应保留未证。','item_ledger WU2A/ZR409; session findings #Dropbox')
add('RF-P024',A8,'forecast receipt 记录实际使用','artifact ids/hash/generator及零重复处理','contradicted','当前prepare_source做role选择、计划producerDAG，不打开artifact/执行producer；source raw字节确有SHA检查，不能泛称零字节验证。该技术gap与用户真正消费成功不同。','scripts/source_preparation.py:140-146; scripts/company_wiki_source.py; deep_clause RF-FC904-*')
add('RF-P025',A8,'section query 模块','所有artifact查询fail-closed','contradicted','SectionQuery普通查询仍能返回failed旧版本、错inputSHA、缺文件与不存在span。纯临时SQLite反例，未污染生产。','reviews/wiki_legacy/section_probe.json; company_wiki/source_catalog/section_query.py')
add('RF-P026',A8,'三真实根 + 生产 catalog','L4生产与发布门','insufficient_evidence','真实read-only安全和真实可用率不同；已有负结果应阻“复用成功”声明。GP9/8阻断修复有效，原9/5缺陷不可原样沿用，需当前ledger。','additional GP manual reviews; parent cross_history current delta')
add('RF-P027',A8,'错误码固定','错误契约','insufficient_evidence','错误码稳定传播是独立端到端义务，RF source_preparation仍截stderr转RuntimeError；filing本地typederror存在不等于穿透用户入口。','checklist_ledger root-error-fields; latest real audit')
add('RF-P028',A8,'不能通过排除新文件或降低阈值变绿','95%/90%不降门','contradicted','后session9/1CI25ignore和阈值下调与此原门不同。去除archive有正当范围可能，但需逐路径原因与产品覆盖，不能只报全绿。','session progress finalCI; R4 A06D0 exclusions; parent currentCI audit')
add('RF-P029',A8,'已有 normalized+summary+sections','用户入口实际处理结果复用','insufficient_evidence','角色入receipt可证明选择计划，实际打开同hashbytes、所需事实定位、parser/LLM真实0以及金标准forecast才满足该条。当前sourceprep与SectionQuery不足。','deep_clause RF-FC904-*; item_ledger FC904/WU5.4')
add('RF-P030',A8,'任何 `unresolved/partial/unverified`','未闭合不得全部消除','contradicted','closure ledger保留F015/F034及CI/自然观察partial，却有全部enumeratedtestablefixed语言。负例only授权不消除positive未证。','closure_ledger.md; item_ledger WU10.1/10.2')

S='assurance/runs/session-2026-08-13/progress.md'
def session(i,anchor,claim,verdict,reason,ev):add(i,S,anchor,claim,verdict,reason,ev)
session('RF-P031','or True','已知恒真断言被minor/info接受','contradicted','即使其他断言有价值，该分支不能证明预期业务条件；独立审查已发现而未阻后继，是测量标准问题而不只是遗漏。','CA202/CA302 tests; item_ledger; logs/targeted_tests.txt')
session('RF-P032','CA-306','退役通知部署','contradicted','最终卡/复审称旧目录不动、只模板；8/31又发现通知未部署并回填6份。后来修复不能补成首次accept时已部署。','session findings/progress terminal notes; item_ledger CA306')
session('RF-P033','CAS','终局推进自动闭环','insufficient_evidence','terminaladvance无法找到合法下一卡，手工CAS把state置completed；单writer工具仍有价值，但terminal自动闭环未由卡全测。','session terminal notes; CA001/107 current unit reviews')
session('RF-P034','--no-verify','402提交全部绕过hooks','insufficient_evidence','这是历史叙述，和早期多次precommit输出并存；未逐commit取执行证据，不将它认作已独立证实的402次事实。用户此前明确no-push，未上CI本身不违规。','session findings terminal; current source occurrences')
session('RF-P035','ZR-409','Dropbox canary成功含义','insufficient_evidence','53独立annual候选无capture-ready，2HTTP/51无URL；安全MISSING证明拒绝，不能证明一个真实外部root-only正向复用。future_lake配置fixture不等于第二真实同类root。','item_ledger ZR409; session findings full text')
session('RF-P036','ZR-713','三层backtest全部完成','contradicted','早期层间结果相同被审查发现；后minevolume仍wapeNone，结构层拆开有改进而真实预测误差未产生。','item_ledger ZR713; model_ledger; current rolling_backtest source')
session('RF-P037','ZR-605','finite修复所在函数','contradicted','在商业条款ZR606补finite不能关闭mineoperationZR605接受Inf；单位/basis仍独立未满足。','logs/probe_scopes.stdout.json; deep_clause ADR03/05')
session('RF-P038','ZR-604','至多一条accepted等于已解决冲突','insufficient_evidence','零accepted/空resolution也可能符合字面；保存冲突可支持调查，但formal参数使用必须有确定选择与provenance。','deep_clause RF-ADR-06; contracts/document.py')
session('RF-P039','ZR-608','数字有限等于无伪收入','contradicted','finite/bool/domain只保证数值域，不能验证履约、外销、并表、内部交易与原文证据。','item_ledger ZR608; model_ledger resource/reserve')
session('RF-P040','ZR-709','同公式反推实现价再重算收入','contradicted','reportedrevenue÷volume生成price再volume×price必然勾稽，缺独立商业条款与矿级销量；必须标calibration而非验证。','item_ledger ZR709; current synthetic tests')
session('RF-P041','ZR-806','sidecar字段验证等于消费','insufficient_evidence','元数据与raw绑定有价值但不证明fact/parameter/forecast用到了artifact；现有artifactroles-only路径可保持所有parser/LLM为0。','RF-FC904 clauses; item_ledger ZR806')
session('RF-P042','ZR-703','sync MATCH等于新用例已安装','insufficient_evidence','历史后来手工copy建议/漏新测试显示manifest界限；只核产品manifest可合理，但必须说明完整发布包及当前source安装版本。','item_ledger ZR703/ZR907; reviews/filing installedcopies')
session('RF-P043','CA-301','clean replay','contradicted','gitobjects/hash检验与189hash重算/10receipt重签不是原三干净checkout真实重放，补签保留historyrepair标签。','item_ledger CA301; deep_clause/')
session('RF-P044','ZR-1102','生产可达','contradicted','最终卡允许tests OR lib一引用，测试自引用C4仍接受，不支持生产consumer实际执行。','deep_clause RF-ZR1102-REACH')
session('RF-P045','CA-305','六问题完成','contradicted','accepted+receipt存在+40hex状态被用来验证上游accepted，闭环没有独立业务oracle。','item_ledger CA305/ZR1105')

B='assurance/runs/2026-09-11_r4-phase-b/'
add('RF-P046',B+'b-design.md','S-10','硬字节hash改为偏好','superseded','4旧fixture字节/hash不一致而冻结不能改，owner明确允许metadatafallback，B03单独hardbytes。授权让步合法，但consumerC没接就不等于原读取全链已安全。','R4 B02/B03 doc ledger; currentRF sourceprep')
add('RF-P047',B+'evidence/b03-implementation.md','消费者','独立字节读取API未接消费者','not_deployed','helper18tests/真实Alibaba读取支持该API局部能力；现RF重新按path读取且不使用read_verified_bytes，验证过buffer契约不能保护另一次pathopen。','scripts/company_wiki_source.py; R4 B03 review; parent current source route')
add('RF-P048',B+'evidence/b04-implementation.md','覆盖','旧版本stable reference','insufficient_evidence','移动PDF+sidecar成功不同于同路径覆盖旧bytes仍可得。S12明确不保旧copy，后继metadatahandle只能证身份存在；真正读取需originalversionbytes。','R4 B04 doc ledger; owner decisions9/12')
add('RF-P049',B+'evidence/b06-implementation.md','不可达','preview/qualification新字段','not_deployed','preview规则存在但现有capturecomplete先拒；blocked作为加法字段旧client忽略，wirecompatibility不等于安全语义兼容。','R4 B0607 disposition; currentRF sourceprep ignores qualification/bundle_usable')
add('RF-P050',B+'evidence/b07-plan.md','N-1','N-1合同延期','not_deployed','owner同意当前only不意味着历史N-1义务消失；consumer一次版本adapter必须跨仓补验，B07unknownfailclosed支持其窄目标。','owner-scope-decisions9/12 S8; r4_document_ledger')
add('RF-P051',B+'task_plan.md','在产爆炸半径 = none','相同policyhash证明无行为影响','insufficient_evidence','hash比较只能按同config/同导出语义；B01曾比较错hash实现，候选级过滤仍改变行为；4显式reusable根的特定配置不能外推所有host。','B01 implementation/review disposition; r4_document_ledger')
add('RF-P052',B+'test-acceptance-map.md','L12','L01–L12已验证','insufficient_evidence','各LID需要case实际收集/执行/断言，docstring标识和74机制test未覆盖所有B03/L12；真实OS副作用和consumer仍分层未证。','R4 B08/B.AR reports; r4_document_ledger')
add('RF-P053',B+'owner-authorisation-and-my-adjudication-2026-09-16.md','102','预算25次实际102次','supported_scoped','作者保留超预算事实并由owner批准后续处理是诚实改进。selftest guard有价值，但命令总数/spy数据不是OS强制预算；后续授权不抹去首次偏差。','R4 B.AR raw manifest and adjudication; r4_document_ledger')
add('RF-P054',B+'r4-final-status.md','第五','第五root全兼容','insufficient_evidence','isolated1row59B第五root旁有四standin声明，不是四真实root同时共存。owner明确选择isolated是合法范围，原广义泛化仍未证。','R4 fifth-root report and owner9/18; r4_document_ledger')
add('RF-P055',B+'r4-final-status.md','B10','单一读取链','insufficient_evidence','B10最终单一metadataJSONparser范围，byteprovider/consumer不在包；技术修复有效但不能闭合最初query→open→consumer主链。','B10 implementation/reviews; RF-FC904; wiki SectionQueryprobe')

add('RF-P056',B+'evidence/barfix-product-fixes.md','第二处 `fetchall` 的补修','单文档read故障不中止全批','supported_scoped','并行任务新commit f39bd5a已经新增第二处sqlite3.Error guard和retryable/terminal路径；旧未守卫结论被该版本覆盖。只读diff已核，未由本审查改代码/重跑该套件。record失败及批级读取仍按设计硬停，不应叫遗漏。','company-wiki git show f39bd5a; tests/contract/test_fbar_b10r2_normalize_guards.py; R4 retainedmutation evidence')
add('RF-P057',B+'evidence/barfix-product-fixes.md','此前只有','记录事务以同形源码阅读替代故障驱动','superseded','旧报告借ingest探针证明transaction是错引用；新独立注入播种后武装、首次transaction失败后健康doc仍提交，改进具有实质。保留未重新运行的证据边界。','B progress9/19; current normalizer transaction source; retained seven-case test file')
add('RF-P058',B+'evidence/barfix-product-fixes.md','声明了两次','mutation账目可信度','superseded','重复字典key静默覆盖、replace1错锚点、替换文本已存在造成无变异；旧kill数不能证明每义务。最新selfcheck独立拒绝3种harness缺陷是有用修复，不能代替全数据流变异。','barfix_mutations.py selfcheck; r4_document_ledger')
add('RF-P059',B+'findings.md','F-COV-01','coverage证据raw hash缺原工件','superseded','旧sha无留存文件不可复现，即使哈希格式正确。最新raw+canonical measurementhash+完整95文件artifact留存改进可追踪，但不改变60.5%normalizer门本身coverage范围。','barfix6-coverage.json/coverage_anchor.py; r4_document_ledger')
add('RF-P060',B+'findings.md','F-ZR409-01','零写oracle宿主波动','insufficient_evidence','49只读采样记录云目录size变化且mtime稳支持host敏感性，单独重跑绿不证明所有该类红都是环境；该测试不经过normalizer新路径，所以不能归因新guard。CIignore/coverage||true必须保留分母。','R4 zr409-live-root-watch.json and testsource; latest retainedlogs')
add('RF-P061',B+'findings.md','F-PROD-01','生产scan失败根配置错配','supported_scoped','最新只读scan_runs报告与此前实跑吻合：shadowtrue使无adapter根failclosed，声明adapter修复不改变company_raw。是部署配置未迁移，不是新guard引发；本审查不修生产。最后有效scan日期只是此报告查询scope，不外推全生产写活动。','R4 prod-scan-failclosed.json; parent real source prep capture_ready vs usable=false')

def main():
    (OUT/'prose_clause_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in CASES),encoding='utf8')
    print('manually split source clauses',len(CASES))
if __name__=='__main__':main()
